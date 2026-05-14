from pathlib import Path

import pandas as pd

from core.duck_csv import read_csv_with_sql

DATA_FILE = Path("vaccine_records_cleaned.csv")
NAMES_FILE = Path("vaccine_names.csv")
COLUMNS = ["id", "name", "raw_name", "dose", "date", "manufacturer", "batch", "arm", "provider"]
ARM_OPTIONS = ["", "L", "R"]


def load_vaccine_names() -> pd.DataFrame:
    if not NAMES_FILE.exists():
        return pd.DataFrame(columns=["canonical_zh", "abbr_zh", "canonical_en", "abbr_en", "aliases"])
    try:
        raw_df = read_csv_with_sql(NAMES_FILE, "load_vaccine_names.sql").fillna("")
    except Exception:
        raw_df = pd.read_csv(NAMES_FILE, dtype=str).fillna("")
    return _normalize_vaccine_names_columns(raw_df)


def _first_non_empty(row: pd.Series, keys: list[str]) -> str:
    for key in keys:
        if key in row.index:
            value = str(row.get(key, "")).strip()
            if value:
                return value
    return ""


def _normalize_vaccine_names_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Accept simplified/traditional variants in vaccine_names.csv while standardizing
    to canonical_zh (traditional display target) and related fields.
    """
    normalized_rows = []
    for _, row in df.iterrows():
        canonical_zh_tw = _first_non_empty(row, ["canonical_zh_tw", "canonical_zh_hant", "canonical_zh"])
        canonical_zh_cn = _first_non_empty(row, ["canonical_zh_cn", "canonical_zh_hans"])
        canonical_zh = canonical_zh_tw or canonical_zh_cn

        abbr_zh_tw = _first_non_empty(row, ["abbr_zh_tw", "abbr_zh_hant", "abbr_zh"])
        abbr_zh_cn = _first_non_empty(row, ["abbr_zh_cn", "abbr_zh_hans"])
        abbr_zh = abbr_zh_tw or abbr_zh_cn
        canonical_en = _first_non_empty(row, ["canonical_en"])
        abbr_en = _first_non_empty(row, ["abbr_en"])

        alias_parts = []
        for key in ["aliases", "aliases_tw", "aliases_hant", "aliases_cn", "aliases_hans"]:
            if key in row.index and str(row[key]).strip():
                alias_parts.extend([a.strip() for a in str(row[key]).split("|") if a.strip()])
        # Ensure simplified/traditional standards are both matchable as aliases.
        for value in [canonical_zh_tw, canonical_zh_cn, abbr_zh_tw, abbr_zh_cn]:
            if value:
                alias_parts.append(value)
        aliases = "|".join(alias_parts)

        normalized_rows.append(
            {
                "canonical_zh": canonical_zh,
                "abbr_zh": abbr_zh,
                "canonical_en": canonical_en,
                "abbr_en": abbr_en,
                "aliases": aliases,
            }
        )
    return pd.DataFrame(normalized_rows).fillna("")


def build_alias_map(names_df: pd.DataFrame) -> dict:
    mapping = {}
    for _, row in names_df.iterrows():
        zh = row["canonical_zh"].strip()
        azh = row.get("abbr_zh", zh).strip() or zh
        en = row["canonical_en"].strip()
        aen = row.get("abbr_en", en).strip() or en
        for alias in [zh, azh, en, aen] + [a.strip() for a in row["aliases"].split("|")]:
            if alias:
                mapping[alias.lower()] = (zh, azh, en, aen)
    return mapping


def resolve_name(raw: str, alias_map: dict) -> tuple:
    key = str(raw).strip().lower()
    if key in alias_map:
        return alias_map[key]
    return (raw, raw, raw, raw)


def load_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(DATA_FILE, index=False)
        return df
    try:
        df = read_csv_with_sql(DATA_FILE, "load_records.sql")
    except Exception:
        df = pd.read_csv(DATA_FILE, dtype=str)
    df = df.rename(columns={"vaccine_name": "name", "vaccination_date": "date", "batch_no": "batch"})
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[COLUMNS]
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df["dose"] = pd.to_numeric(df["dose"], errors="coerce")
    df["arm"] = df["arm"].fillna("").str.strip().str.upper()
    df["arm"] = df["arm"].where(df["arm"].isin(["L", "R"]), "")

    names_df = load_vaccine_names()
    alias_map = build_alias_map(names_df)

    def _resolve(row):
        raw = row["raw_name"] if str(row["raw_name"]).strip() else row["name"]
        zh, azh, en, aen = resolve_name(raw, alias_map)
        return pd.Series(
            {"name": zh, "abbr_zh": azh, "name_en": en, "abbr_en": aen, "raw_name": raw if raw != zh else row["raw_name"]}
        )

    resolved = df.apply(_resolve, axis=1)
    df["name"] = resolved["name"]
    df["abbr_zh"] = resolved["abbr_zh"]
    df["name_en"] = resolved["name_en"]
    df["abbr_en"] = resolved["abbr_en"]
    df["raw_name"] = resolved["raw_name"]
    return df


def save_data(df: pd.DataFrame):
    cols_to_save = [c for c in COLUMNS if c in df.columns]
    df[cols_to_save].to_csv(DATA_FILE, index=False)


def next_id(df: pd.DataFrame) -> int:
    if df.empty or df["id"].isna().all():
        return 1
    return int(df["id"].dropna().max()) + 1
