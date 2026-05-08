from pathlib import Path

import pandas as pd

DATA_FILE = Path("vaccine_records_cleaned.csv")
NAMES_FILE = Path("vaccine_names.csv")
COLUMNS = ["id", "name", "raw_name", "dose", "date", "manufacturer", "batch", "arm", "provider"]
ARM_OPTIONS = ["", "L", "R"]


def load_vaccine_names() -> pd.DataFrame:
    if not NAMES_FILE.exists():
        return pd.DataFrame(columns=["canonical_zh", "abbr_zh", "canonical_en", "abbr_en", "aliases"])
    return pd.read_csv(NAMES_FILE, dtype=str).fillna("")


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
