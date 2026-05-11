import streamlit as st

from core.data_store import COLUMNS
from core.pdf_export import build_pdf


def render_export_page(df, T: dict):
    st.title(T["export_title"])
    st.info(f"{T['export_info']} **{len(df)}** {T['export_cols']}`{', '.join(COLUMNS)}`")

    col_csv, col_pdf = st.columns(2)

    export_df = df[[c for c in COLUMNS if c in df.columns]].copy()
    csv_bytes = export_df.to_csv(index=False).encode("utf-8-sig")
    col_csv.download_button(
        label=T["download"],
        data=csv_bytes,
        file_name="vaccine_records_export.csv",
        mime="text/csv",
        type="primary",
    )

    with col_pdf:
        with st.spinner(""):
            try:
                pdf_df = df.copy()
                pdf_df["name"] = pdf_df["_display_name"]
                pdf_col_headers = [
                    T["col_id"],
                    T["col_name"],
                    T["col_dose"],
                    T["col_date"],
                    T["col_mfr"],
                    T["col_batch"],
                    T["col_arm"],
                    T["col_prov"],
                ]
                pdf_bytes = build_pdf(
                    pdf_df,
                    title=T["pdf_title"],
                    generated_label=T["pdf_generated"],
                    total_label=T["pdf_total"],
                    col_headers=pdf_col_headers,
                )
                st.download_button(
                    label=T["download_pdf"],
                    data=pdf_bytes,
                    file_name="vaccine_records_export.pdf",
                    mime="application/pdf",
                    type="primary",
                )
            except Exception as e:
                st.error(f"PDF generation failed: {e}")

    st.dataframe(
        df[["id", "_display_name", "raw_name", "dose", "date", "manufacturer", "batch", "arm", "provider"]],
        width="stretch",
        hide_index=True,
    )
