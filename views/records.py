from datetime import date

import pandas as pd
import streamlit as st

from core.data_store import ARM_OPTIONS, COLUMNS, build_alias_map, load_vaccine_names, next_id, resolve_name, save_data


def render_records_page(df: pd.DataFrame, T: dict, lang_key: str, use_abbr: bool):
    st.title(T["records_title"])

    with st.expander(T["filter"], expanded=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        keyword = col1.text_input(T["keyword"])
        name_opts = [T["all"]] + sorted(df["_display_name"].dropna().unique().tolist())
        sel_name = col2.selectbox(T["vac_name"], name_opts)
        years = sorted(
            pd.to_datetime(df["date"], errors="coerce").dt.year.dropna().astype(int).unique().tolist(), reverse=True
        )
        sel_year = col3.selectbox(T["sel_year"], [T["all"]] + [str(y) for y in years])
        prov_opts = [T["all"]] + sorted(df["provider"].dropna().unique().tolist())
        sel_prov = col4.selectbox(T["provider_label"], prov_opts)
        sel_arm = col5.selectbox(T["arm_label"], [T["all"], "L", "R", T["unfilled"]])

    filtered = df.copy()
    if keyword:
        mask = filtered.apply(lambda r: keyword.lower() in " ".join(r.astype(str)).lower(), axis=1)
        filtered = filtered[mask]
    if sel_name != T["all"]:
        filtered = filtered[filtered["_display_name"] == sel_name]
    if sel_year != T["all"]:
        filtered = filtered[pd.to_datetime(filtered["date"], errors="coerce").dt.year == int(sel_year)]
    if sel_prov != T["all"]:
        filtered = filtered[filtered["provider"] == sel_prov]
    if sel_arm == "L":
        filtered = filtered[filtered["arm"] == "L"]
    elif sel_arm == "R":
        filtered = filtered[filtered["arm"] == "R"]
    elif sel_arm == T["unfilled"]:
        filtered = filtered[filtered["arm"] == ""]

    filtered = filtered.sort_values("date", ascending=False).reset_index(drop=True)
    st.caption(f"{T['showing']} {len(filtered)} {T['of']} {len(df)} {T['records']}")

    filtered_editor = filtered.copy()
    filtered_editor["__delete__"] = False
    display_cols = ["__delete__", "id", "_display_name", "raw_name", "dose", "date", "manufacturer", "batch", "arm", "provider"]
    edited = st.data_editor(
        filtered_editor[display_cols],
        width="stretch",
        num_rows="fixed",
        column_config={
            "__delete__": st.column_config.CheckboxColumn(T["col_delete"], default=False),
            "id": st.column_config.NumberColumn(T["col_id"], disabled=True),
            "_display_name": st.column_config.TextColumn(T["col_name"], disabled=True),
            "raw_name": st.column_config.TextColumn(T["col_raw"], disabled=True),
            "dose": st.column_config.NumberColumn(T["col_dose"], min_value=1),
            "date": st.column_config.TextColumn(T["col_date"]),
            "manufacturer": st.column_config.TextColumn(T["col_mfr"]),
            "batch": st.column_config.TextColumn(T["col_batch"]),
            "arm": st.column_config.SelectboxColumn(T["col_arm"], options=ARM_OPTIONS),
            "provider": st.column_config.TextColumn(T["col_prov"]),
        },
        key="records_editor",
    )

    if st.button(T["save"], type="primary"):
        delete_ids = edited.loc[edited["__delete__"] == True, "id"].dropna().astype(int).tolist()
        if delete_ids:
            df = df[~df["id"].isin(delete_ids)].reset_index(drop=True)
        edited_kept = edited[edited["__delete__"] != True].copy()
        kept_ids = edited_kept["id"].dropna().astype(int).tolist()
        for col in ["dose", "date", "manufacturer", "batch", "arm", "provider"]:
            df.loc[df["id"].isin(kept_ids), col] = edited_kept.set_index("id")[col].reindex(kept_ids).values
        save_data(df)
        if delete_ids:
            st.success(f"{T['saved_with_delete']} {len(delete_ids)}")
        else:
            st.success(T["saved"])
        st.rerun()

    st.markdown("---")
    with st.expander(T["add_title"], expanded=False):
        names_df = load_vaccine_names()
        if lang_key == "English":
            canonical_list = sorted(names_df["canonical_en"].dropna().unique().tolist())
        else:
            canonical_list = sorted(names_df["canonical_zh"].dropna().unique().tolist())
        select_opts = [f"— {T['add_vac_custom']} —"] + canonical_list

        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            vac_select = c1.selectbox(T["add_vac_select"], select_opts)
            custom_name = c1.text_input(T["add_vac_custom"], placeholder="e.g. MyVaccine")
            dose = c2.number_input(T["dose_label"], min_value=1, step=1, value=1)
            vac_date = c2.date_input(T["date_label"], value=date.today())
            manufacturer = c1.text_input(T["mfr"])
            batch = c2.text_input(T["batch"])
            arm = c1.selectbox(T["arm_label"], ARM_OPTIONS)
            provider = st.text_input(T["provider_label"])
            submitted = st.form_submit_button(T["add_btn"], type="primary")

        if submitted:
            raw_input = custom_name.strip() if vac_select.startswith("—") else vac_select
            if not raw_input:
                st.error(T["name_empty"])
            else:
                alias_map = build_alias_map(names_df)
                zh, azh, en, aen = resolve_name(raw_input, alias_map)
                new_row = {
                    "id": next_id(df),
                    "name": zh,
                    "raw_name": raw_input,
                    "dose": int(dose),
                    "date": vac_date.strftime("%Y-%m-%d"),
                    "manufacturer": manufacturer.strip(),
                    "batch": batch.strip(),
                    "arm": arm,
                    "provider": provider.strip(),
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                label = aen if (lang_key == "English" and use_abbr) else en if lang_key == "English" else azh if use_abbr else zh
                st.success(f"{T['added']}{label} · {T['dose_label'][:-2]} {dose}{T['dose_suffix']}{new_row['id']})")
                st.rerun()

    st.markdown("---")
    with st.expander(T["import_title"], expanded=False):
        st.caption(T["import_help"])
        uploaded = st.file_uploader(T["import_upload"], type=["csv", "xlsx", "xls"], key="records_import_uploader")
        if uploaded is not None:
            if uploaded.name.lower().endswith(".csv"):
                src_df = pd.read_csv(uploaded, dtype=str).fillna("")
            else:
                src_df = pd.read_excel(uploaded, dtype=str).fillna("")

            src_cols = src_df.columns.tolist()
            options = [T["import_empty"]] + src_cols
            field_map = {
                "raw_name": T["col_raw"],
                "dose": T["col_dose"],
                "date": T["col_date"],
                "manufacturer": T["col_mfr"],
                "batch": T["col_batch"],
                "arm": T["col_arm"],
                "provider": T["col_prov"],
            }
            mapped = {}
            map_cols = st.columns(2)
            for i, (target, label) in enumerate(field_map.items()):
                mapped[target] = map_cols[i % 2].selectbox(
                    f"{label} ← {T['import_source_col']}",
                    options,
                    key=f"records_map_{target}",
                )

            preview_df = pd.DataFrame()
            for target in field_map:
                source = mapped[target]
                preview_df[target] = "" if source == T["import_empty"] else src_df[source].astype(str).str.strip()

            preview_df["raw_name"] = preview_df["raw_name"].fillna("").astype(str).str.strip()
            preview_df["dose"] = pd.to_numeric(preview_df["dose"], errors="coerce")
            preview_df["date"] = pd.to_datetime(preview_df["date"], errors="coerce")
            preview_df["date"] = preview_df["date"].dt.strftime("%Y-%m-%d")
            preview_df["arm"] = preview_df["arm"].fillna("").astype(str).str.strip().str.upper()
            preview_df["arm"] = preview_df["arm"].where(preview_df["arm"].isin(["L", "R"]), "")

            valid = (preview_df["raw_name"].str.strip() != "") & preview_df["dose"].notna() & preview_df["date"].notna()
            st.markdown(f"#### {T['import_preview']}")
            st.dataframe(preview_df.head(10), width="stretch", hide_index=True)
            st.caption(f"{T['import_required']}  ({int(valid.sum())}/{len(preview_df)})")

            if st.button(T["import_btn"], type="primary", key="records_import_btn"):
                to_import = preview_df[valid].copy()
                if to_import.empty:
                    st.error(T["import_fail"])
                else:
                    names_df = load_vaccine_names()
                    alias_map = build_alias_map(names_df)
                    resolved = to_import["raw_name"].apply(lambda x: resolve_name(x, alias_map))
                    to_import["name"] = resolved.apply(lambda x: x[0])
                    start_id = next_id(df)
                    to_import["id"] = range(start_id, start_id + len(to_import))
                    to_import = to_import[["id", "name", "raw_name", "dose", "date", "manufacturer", "batch", "arm", "provider"]]
                    new_df = pd.concat([df[COLUMNS], to_import], ignore_index=True)
                    save_data(new_df)
                    st.success(f"{T['import_success']} {len(to_import)}")
                    st.rerun()
