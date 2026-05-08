import pandas as pd
import streamlit as st

from core.data_store import build_alias_map, load_vaccine_names
from core.i18n import LANG


def render_settings_page(df, T: dict, lang_key: str, use_abbr: bool):
    st.title(T["settings_title"])

    c1, c2 = st.columns(2)
    new_lang = c1.selectbox(
        T["lang_label"],
        list(LANG.keys()),
        index=list(LANG.keys()).index(lang_key),
        key="lang_select",
    )
    fmt_options = [T["name_fmt_abbr"], T["name_fmt_full"]]
    current_fmt = "abbr" if use_abbr else "full"
    fmt_choice = c2.radio(
        T["name_fmt_label"],
        fmt_options,
        index=0 if current_fmt == "abbr" else 1,
        horizontal=True,
    )
    st.session_state["name_fmt"] = "abbr" if fmt_choice == fmt_options[0] else "full"
    if new_lang != lang_key:
        st.rerun()

    st.markdown("---")

    st.markdown(f"#### {T['dq_section']}")
    issues = []
    dup_ids = df[df["id"].duplicated(keep=False)]
    if not dup_ids.empty:
        issues.append((T["dup_id"], dup_ids))
    bad_date = df[pd.to_datetime(df["date"], errors="coerce").isna()]
    if not bad_date.empty:
        issues.append((T["bad_date"], bad_date))
    bad_dose = df[pd.to_numeric(df["dose"], errors="coerce").isna()]
    if not bad_dose.empty:
        issues.append((T["bad_dose"], bad_dose))
    bad_arm = df[~df["arm"].isin(["", "L", "R"])]
    if not bad_arm.empty:
        issues.append((T["bad_arm"], bad_arm))

    names_df_dq = load_vaccine_names()
    alias_map_dq = build_alias_map(names_df_dq)
    known_keys = set(alias_map_dq.keys())
    unstd = df[
        (df["raw_name"].str.strip() != "") & (~df["raw_name"].str.strip().str.lower().isin(known_keys))
    ][["id", "_display_name", "raw_name", "date"]].drop_duplicates(subset=["raw_name"])
    if not unstd.empty:
        issues.append((T["dq_unstd"], unstd))

    if not issues:
        st.success(T["dq_ok"])
    else:
        for title, rows in issues:
            st.error(f"⚠️ {title}  ({len(rows)})")
            st.dataframe(rows, use_container_width=True)

    st.markdown("---")
    st.markdown(f"#### {T['vac_names_title']}")
    st.caption(T["vac_names_caption"])
    names_df = load_vaccine_names()
    if not names_df.empty:
        st.dataframe(names_df, use_container_width=True, hide_index=True)
