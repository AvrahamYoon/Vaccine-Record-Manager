"""
Expand vaccine_names.csv aliases: add s2t/t2s variants per token plus
traditional standard name and abbreviation with their simplified forms.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


def _has_cjk(s: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", s))


def _dedup_key(s: str) -> str:
    return s.lower() if not _has_cjk(s) else s


def expand_row(canonical_zh: str, abbr_zh: str, aliases: str, s2t, t2s) -> str:
    base: list[str] = []
    for x in (
        canonical_zh.strip(),
        abbr_zh.strip(),
        *(a.strip() for a in aliases.split("|") if a.strip()),
    ):
        if x:
            base.append(x)

    seen: set[str] = set()
    out: list[str] = []

    def push(tok: str) -> None:
        tok = tok.strip()
        if not tok:
            return
        key = _dedup_key(tok)
        if key in seen:
            return
        seen.add(key)
        out.append(tok)

    # Standard trad + simplified counterparts first (helps matching mainland names)
    tw_name = canonical_zh.strip()
    tw_abbr = abbr_zh.strip()
    if tw_name:
        push(tw_name)
        cn_name = t2s.convert(tw_name)
        if cn_name != tw_name:
            push(cn_name)
    if tw_abbr:
        push(tw_abbr)
        cn_abbr = t2s.convert(tw_abbr)
        if cn_abbr != tw_abbr:
            push(cn_abbr)

    for tok in base:
        push(tok)
        if not _has_cjk(tok):
            continue
        st = s2t.convert(tok)
        ts = t2s.convert(tok)
        if st != tok:
            push(st)
        if ts != tok:
            push(ts)

    return "|".join(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("vaccine_names.csv"))
    parser.add_argument("--output", type=Path, default=Path("vaccine_names.csv"))
    args = parser.parse_args()

    try:
        from opencc import OpenCC  # opencc-python-reimplemented
    except ImportError:
        raise SystemExit("Missing dependency: pip install opencc-python-reimplemented")

    s2t = OpenCC("s2t")
    t2s = OpenCC("t2s")

    df = pd.read_csv(args.input, dtype=str).fillna("")
    if "canonical_zh" not in df.columns or "aliases" not in df.columns:
        raise SystemExit("Expected columns canonical_zh and aliases.")

    expanded = []
    for _, row in df.iterrows():
        exp = expand_row(row["canonical_zh"], row["abbr_zh"], row["aliases"], s2t, t2s)
        expanded.append(exp)

    df["aliases"] = expanded

    df.to_csv(args.output, index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
