import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date
import subprocess
import sys
import os
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Config ────────────────────────────────────────────────────────────────────
DATA_FILE = Path("vaccine_records_cleaned.csv")
COLUMNS = ["id", "name", "dose", "date", "manufacturer", "batch", "arm", "provider"]
ARM_OPTIONS = ["", "L", "R"]

st.set_page_config(page_title="Vaccine Records", page_icon="💉", layout="wide")

# ── i18n ──────────────────────────────────────────────────────────────────────
LANG = {
    "English": {
        "app_title": "Vaccine Records",
        "pages": ["Dashboard", "Records", "Add Record", "Reports", "Data Quality", "Export"],
        "total": "Total Doses", "kinds": "Vaccine Types", "last_date": "Last Vaccination",
        "left_arm": "Left Arm (L)", "right_arm": "Right Arm (R)",
        "yearly_chart": "Doses per Year", "arm_chart": "Arm Distribution",
        "year": "Year", "count": "Count",
        "records_title": "Vaccination Records", "filter": "Filter / Search",
        "keyword": "Search", "vac_name": "Vaccine", "all": "All",
        "sel_year": "Year", "provider_label": "Provider", "arm_label": "Arm",
        "unfilled": "Not set", "showing": "Showing", "of": "/", "records": "records",
        "save": "💾 Save Changes", "saved": "Saved!",
        "delete_title": "Delete Record", "delete_id": "Enter ID to delete",
        "delete_btn": "🗑️ Delete", "not_found": "ID not found:",
        "confirm_del": "Confirm delete", "yes_del": "✅ Confirm", "cancel": "❌ Cancel",
        "deleted": "deleted",
        "add_title": "Add Vaccination Record",
        "vac_name_input": "Vaccine Name *", "dose_label": "Dose *",
        "date_label": "Date *", "mfr": "Manufacturer", "batch": "Batch No.",
        "add_btn": "➕ Add Record", "name_empty": "Vaccine name is required",
        "added": "Added: ", "dose_suffix": " (ID=",
        "reports_title": "Reports", "timeline": "Vaccination Timeline",
        "vac_count": "Doses by Vaccine", "provider_stat": "Doses by Provider",
        "yearly_stat": "Doses per Year", "arm_ratio": "Arm Distribution",
        "dq_title": "Data Quality", "dq_ok": "✅ No issues found.",
        "dup_id": "Duplicate IDs", "bad_date": "Invalid or missing date",
        "bad_dose": "Non-numeric dose", "bad_arm": "Invalid arm value (not L/R/empty)",
        "export_title": "Export Data", "export_info": "Total",
        "export_cols": "records  ·  Columns: ", "download": "⬇️ Download CSV",
        "col_id": "ID", "col_name": "Vaccine", "col_dose": "Dose",
        "col_date": "Date (YYYY-MM-DD)", "col_mfr": "Manufacturer",
        "col_batch": "Batch", "col_arm": "Arm", "col_prov": "Provider",
        "lang_label": "Language",
        "download_pdf": "⬇️ Download PDF", "pdf_title": "Vaccination Record",
        "pdf_generated": "Generated:", "pdf_total": "Total records:",
    },
    "正體中文": {
        "app_title": "疫苗接種記錄",
        "pages": ["總覽", "記錄管理", "新增記錄", "報表", "資料品質", "匯出"],
        "total": "總接種次數", "kinds": "疫苗種類", "last_date": "最近接種日期",
        "left_arm": "左臂 (L)", "right_arm": "右臂 (R)",
        "yearly_chart": "每年接種次數", "arm_chart": "左右臂比例",
        "year": "年份", "count": "次數",
        "records_title": "接種記錄", "filter": "篩選 / 搜尋",
        "keyword": "關鍵字搜尋", "vac_name": "疫苗名稱", "all": "全部",
        "sel_year": "年份", "provider_label": "接種單位", "arm_label": "接種部位",
        "unfilled": "未填", "showing": "顯示", "of": "/", "records": "筆記錄",
        "save": "💾 儲存變更", "saved": "已儲存！",
        "delete_title": "刪除記錄", "delete_id": "輸入要刪除的 ID",
        "delete_btn": "🗑️ 刪除", "not_found": "找不到 ID：",
        "confirm_del": "確認刪除", "yes_del": "✅ 確認", "cancel": "❌ 取消",
        "deleted": "已刪除",
        "add_title": "新增接種記錄",
        "vac_name_input": "疫苗名稱 *", "dose_label": "劑次 *",
        "date_label": "接種日期 *", "mfr": "生產企業", "batch": "批號",
        "add_btn": "➕ 新增記錄", "name_empty": "疫苗名稱不能為空",
        "added": "已新增：", "dose_suffix": "（ID=",
        "reports_title": "報表", "timeline": "接種時間線",
        "vac_count": "每種疫苗接種次數", "provider_stat": "接種單位統計",
        "yearly_stat": "每年接種次數", "arm_ratio": "左右臂接種比例",
        "dq_title": "資料品質檢查", "dq_ok": "✅ 資料品質良好，未發現問題！",
        "dup_id": "重複 ID", "bad_date": "日期缺失或格式錯誤",
        "bad_dose": "劑次非數字", "bad_arm": "接種部位非 L/R/空",
        "export_title": "匯出資料", "export_info": "共",
        "export_cols": "筆記錄　欄位：", "download": "⬇️ 下載 CSV",
        "col_id": "ID", "col_name": "疫苗名稱", "col_dose": "劑次",
        "col_date": "日期 (YYYY-MM-DD)", "col_mfr": "生產企業",
        "col_batch": "批號", "col_arm": "接種部位", "col_prov": "接種單位",
        "lang_label": "語言",
        "download_pdf": "⬇️ 下載 PDF", "pdf_title": "疫苗接種記錄",
        "pdf_generated": "產生時間：", "pdf_total": "共記錄：",
    },
}

# ── PDF generation ────────────────────────────────────────────────────────────
def _register_cjk_font():
    """Try to register a CJK-capable font for PDF output. Falls back to Helvetica."""
    # Common CJK font paths on Windows / macOS / Linux
    candidates = [
        ("NotoSansCJK", r"C:\Windows\Fonts\NotoSansCJK-Regular.ttc"),
        ("MicrosoftYaHei", r"C:\Windows\Fonts\msyh.ttc"),
        ("MicrosoftYaHei", r"C:\Windows\Fonts\msyh.ttf"),
        ("SimSun", r"C:\Windows\Fonts\simsun.ttc"),
        ("PingFang", "/System/Library/Fonts/PingFang.ttc"),
        ("NotoSansCJK", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    ]
    for name, path in candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                return name
            except Exception:
                continue
    return "Helvetica"  # ASCII fallback


def build_pdf(df: pd.DataFrame, title: str, generated_label: str, total_label: str) -> bytes:
    """Render the vaccine records dataframe as a styled A4 PDF and return bytes."""
    font_name = _register_cjk_font()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=18 * mm, bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "title", fontName=font_name, fontSize=16, leading=22,
        textColor=colors.HexColor("#111827"), spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        "sub", fontName=font_name, fontSize=9, leading=13,
        textColor=colors.HexColor("#6b7280"), spaceAfter=12,
    )
    cell_style = ParagraphStyle(
        "cell", fontName=font_name, fontSize=8, leading=11,
        textColor=colors.HexColor("#1f2937"),
    )
    header_style = ParagraphStyle(
        "header", fontName=font_name, fontSize=8, leading=11,
        textColor=colors.white, fontWeight="bold",
    )

    col_labels = ["ID", "Vaccine / 疫苗", "Dose", "Date", "Manufacturer", "Batch", "Arm", "Provider / 接種單位"]
    col_widths = [10*mm, 28*mm, 12*mm, 22*mm, 28*mm, 22*mm, 10*mm, 42*mm]

    # Build table rows
    header_row = [Paragraph(h, header_style) for h in col_labels]
    data_rows = []
    for _, row in df.iterrows():
        data_rows.append([
            Paragraph(str(int(row["id"])) if pd.notna(row["id"]) else "", cell_style),
            Paragraph(str(row["name"]) if pd.notna(row["name"]) else "", cell_style),
            Paragraph(str(int(row["dose"])) if pd.notna(row["dose"]) else "", cell_style),
            Paragraph(str(row["date"]) if pd.notna(row["date"]) else "", cell_style),
            Paragraph(str(row["manufacturer"]) if pd.notna(row["manufacturer"]) else "", cell_style),
            Paragraph(str(row["batch"]) if pd.notna(row["batch"]) else "", cell_style),
            Paragraph(str(row["arm"]) if pd.notna(row["arm"]) else "", cell_style),
            Paragraph(str(row["provider"]) if pd.notna(row["provider"]) else "", cell_style),
        ])

    table = Table([header_row] + data_rows, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f7df3")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fb")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
        ("LINEBELOW", (0, 0), (-1, 0), 0, colors.transparent),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))

    from datetime import datetime
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    story = [
        Paragraph(title, title_style),
        Paragraph(f"{generated_label} {now_str}　　{total_label} {len(df)}", sub_style),
        table,
    ]
    doc.build(story)
    return buf.getvalue()


# ── CSS: light, clean, minimal ────────────────────────────────────────────────
st.markdown("""
<style>
    /* Global background */
    .stApp { background: #f5f6fa; }
    .block-container { padding: 2rem 2.5rem; max-width: 1180px; }

    /* Sidebar — light grey */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e8eaed;
    }
    [data-testid="stSidebar"] .stRadio > label { display: none; }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap: 2px; }
    [data-testid="stSidebar"] .stRadio label {
        padding: 0.55rem 0.9rem !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
        color: #4b5563 !important;
        font-weight: 500 !important;
        cursor: pointer;
        transition: background 0.15s;
    }
    [data-testid="stSidebar"] .stRadio label:hover { background: #f0f2f5 !important; }
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] span:first-child { display: none; }

    /* Stat cards */
    .stat-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.1rem 1rem 1rem 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 8px rgba(0,0,0,0.04);
        text-align: center;
    }
    .stat-label {
        font-size: 0.72rem;
        color: #9ca3af;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }
    .stat-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #111827;
        line-height: 1.1;
    }

    /* Page title */
    h1 {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #111827 !important;
        margin-bottom: 1.2rem !important;
        padding-bottom: 0.6rem !important;
        border-bottom: 1px solid #e8eaed !important;
    }

    /* Section headings */
    h4 { color: #374151 !important; font-size: 0.95rem !important; font-weight: 600 !important; margin-bottom: 0.5rem !important; }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: #4f7df3 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        color: white !important;
    }
    .stButton > button[kind="primary"]:hover { background: #3b6de0 !important; }
    .stButton > button[kind="secondary"] {
        border-radius: 8px !important;
        border-color: #d1d5db !important;
        color: #374151 !important;
    }

    /* Expander */
    [data-testid="stExpander"] {
        background: #ffffff;
        border-radius: 10px !important;
        border: 1px solid #e8eaed !important;
        box-shadow: none !important;
    }

    /* Form */
    [data-testid="stForm"] {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem !important;
        border: 1px solid #e8eaed !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }

    /* Divider */
    hr { border-color: #e8eaed; margin: 1.2rem 0; }

    /* Selectbox in sidebar */
    [data-testid="stSidebar"] .stSelectbox label { color: #6b7280 !important; font-size: 0.8rem !important; }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: #f9fafb !important;
        border-color: #e5e7eb !important;
        border-radius: 8px !important;
        color: #374151 !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Data helpers ──────────────────────────────────────────────────────────────
def load_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(DATA_FILE, index=False)
        return df
    df = pd.read_csv(DATA_FILE, dtype=str)
    # Normalize legacy column names
    df = df.rename(columns={"vaccine_name": "name", "vaccination_date": "date", "batch_no": "batch"})
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[COLUMNS]
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df["dose"] = pd.to_numeric(df["dose"], errors="coerce")
    df["arm"] = df["arm"].fillna("").str.strip().str.upper()
    df["arm"] = df["arm"].where(df["arm"].isin(["L", "R"]), "")
    return df

def save_data(df: pd.DataFrame):
    df.to_csv(DATA_FILE, index=False)

def next_id(df: pd.DataFrame) -> int:
    if df.empty or df["id"].isna().all():
        return 1
    return int(df["id"].dropna().max()) + 1

# Shared chart style
COLORS = ["#6ea8fe", "#f4a261", "#6bcb77", "#ffd166", "#a78bfa", "#f472b6"]

def apply_chart_style(fig, **kwargs):
    fig.update_layout(
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        margin=dict(t=8, b=8, l=8, r=8),
        font=dict(family="system-ui, -apple-system, sans-serif", size=12, color="#4b5563"),
        **kwargs
    )
    fig.update_xaxes(showgrid=True, gridcolor="#f3f4f6", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#f3f4f6", zeroline=False)
    return fig

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    lang = st.selectbox("", list(LANG.keys()), key="lang_select")
    T = LANG[lang]
    st.markdown(f"<p style='font-size:1.05rem;font-weight:700;color:#111827;margin:1rem 0 0.5rem 0.2rem'>💉 {T['app_title']}</p>", unsafe_allow_html=True)
    st.markdown("<hr style='margin:0.5rem 0 0.8rem 0;border-color:#e8eaed'>", unsafe_allow_html=True)
    page = st.radio("nav", T["pages"], label_visibility="collapsed")

T = LANG[st.session_state.get("lang_select", "正體中文")]
df = load_data()

# ════════════════════════════════════════════════════════════════════════════
# Dashboard
# ════════════════════════════════════════════════════════════════════════════
if page == T["pages"][0]:
    st.title(T["pages"][0])

    total = len(df)
    kinds = df["name"].nunique()
    last_dt = pd.to_datetime(df["date"], errors="coerce").max()
    last_date_str = last_dt.strftime("%Y-%m-%d") if pd.notna(last_dt) else "—"
    left = int((df["arm"] == "L").sum())
    right = int((df["arm"] == "R").sum())

    cols = st.columns(5)
    for col, label, value in zip(cols, [
        T["total"], T["kinds"], T["last_date"], T["left_arm"], T["right_arm"]
    ], [total, kinds, last_date_str, left, right]):
        col.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-label">{label}</div>'
            f'<div class="stat-value">{value}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    df_dated = df.copy()
    df_dated["year"] = pd.to_datetime(df_dated["date"], errors="coerce").dt.year

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"#### {T['yearly_chart']}")
        yearly = df_dated.groupby("year").size().reset_index(name=T["count"])
        yearly = yearly.dropna(subset=["year"])
        yearly["year"] = yearly["year"].astype(int).astype(str)
        fig = px.bar(yearly, x="year", y=T["count"], text=T["count"],
                     color_discrete_sequence=[COLORS[0]])
        apply_chart_style(fig, xaxis_title=T["year"], yaxis_title=T["count"])
        fig.update_traces(marker_line_width=0, textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown(f"#### {T['arm_chart']}")
        arm_df = df[df["arm"].isin(["L", "R"])]["arm"].value_counts().reset_index()
        arm_df.columns = ["arm", T["count"]]
        arm_df["arm"] = arm_df["arm"].map({"L": T["left_arm"], "R": T["right_arm"]})
        fig2 = px.pie(arm_df, names="arm", values=T["count"], hole=0.45,
                      color_discrete_sequence=[COLORS[0], COLORS[1]])
        apply_chart_style(fig2)
        fig2.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(fig2, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# Records
# ════════════════════════════════════════════════════════════════════════════
elif page == T["pages"][1]:
    st.title(T["records_title"])

    with st.expander(T["filter"], expanded=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        keyword = col1.text_input(T["keyword"])
        name_opts = [T["all"]] + sorted(df["name"].dropna().unique().tolist())
        sel_name = col2.selectbox(T["vac_name"], name_opts)
        years = sorted(pd.to_datetime(df["date"], errors="coerce").dt.year.dropna().astype(int).unique().tolist(), reverse=True)
        sel_year = col3.selectbox(T["sel_year"], [T["all"]] + [str(y) for y in years])
        prov_opts = [T["all"]] + sorted(df["provider"].dropna().unique().tolist())
        sel_prov = col4.selectbox(T["provider_label"], prov_opts)
        sel_arm = col5.selectbox(T["arm_label"], [T["all"], "L", "R", T["unfilled"]])

    filtered = df.copy()
    if keyword:
        mask = filtered.apply(lambda r: keyword.lower() in " ".join(r.astype(str)).lower(), axis=1)
        filtered = filtered[mask]
    if sel_name != T["all"]:
        filtered = filtered[filtered["name"] == sel_name]
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

    edited = st.data_editor(
        filtered, use_container_width=True, num_rows="dynamic",
        column_config={
            "id": st.column_config.NumberColumn(T["col_id"], disabled=True),
            "name": st.column_config.TextColumn(T["col_name"]),
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
        unchanged = df[~df["id"].isin(filtered["id"])]
        merged = pd.concat([unchanged, edited], ignore_index=True).sort_values("id")
        save_data(merged)
        st.success(T["saved"])
        st.rerun()

    st.markdown("---")
    st.markdown(f"**{T['delete_title']}**")
    del_id = st.number_input(T["delete_id"], min_value=1, step=1, value=1)
    if st.button(T["delete_btn"]):
        if del_id in df["id"].values:
            st.session_state["pending_delete"] = int(del_id)
        else:
            st.warning(f"{T['not_found']} {del_id}")

    if "pending_delete" in st.session_state:
        pid = st.session_state["pending_delete"]
        row = df[df["id"] == pid]
        st.warning(f"{T['confirm_del']} — ID {pid}: {row['name'].values[0]}, {row['date'].values[0]}")
        c_yes, c_no, _ = st.columns([1, 1, 5])
        if c_yes.button(T["yes_del"]):
            df = df[df["id"] != pid].reset_index(drop=True)
            save_data(df)
            del st.session_state["pending_delete"]
            st.success(f"ID {pid} {T['deleted']}")
            st.rerun()
        if c_no.button(T["cancel"]):
            del st.session_state["pending_delete"]
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# Add Record
# ════════════════════════════════════════════════════════════════════════════
elif page == T["pages"][2]:
    st.title(T["add_title"])

    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        vac_name = c1.text_input(T["vac_name_input"])
        dose = c2.number_input(T["dose_label"], min_value=1, step=1, value=1)
        vac_date = c1.date_input(T["date_label"], value=date.today())
        manufacturer = c2.text_input(T["mfr"])
        batch = c1.text_input(T["batch"])
        arm = c2.selectbox(T["arm_label"], ARM_OPTIONS)
        provider = st.text_input(T["provider_label"])
        submitted = st.form_submit_button(T["add_btn"], type="primary")

    if submitted:
        if not vac_name.strip():
            st.error(T["name_empty"])
        else:
            new_row = {
                "id": next_id(df), "name": vac_name.strip(), "dose": int(dose),
                "date": vac_date.strftime("%Y-%m-%d"), "manufacturer": manufacturer.strip(),
                "batch": batch.strip(), "arm": arm, "provider": provider.strip(),
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success(f"{T['added']}{vac_name} · dose {dose}{T['dose_suffix']}{new_row['id']})")
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# Reports
# ════════════════════════════════════════════════════════════════════════════
elif page == T["pages"][3]:
    st.title(T["reports_title"])

    df_r = df.copy()
    df_r["date_parsed"] = pd.to_datetime(df_r["date"], errors="coerce")
    df_r["year"] = df_r["date_parsed"].dt.year

    # Timeline scatter
    st.markdown(f"#### {T['timeline']}")
    timeline = df_r.dropna(subset=["date_parsed"]).sort_values("date_parsed")
    fig_tl = px.scatter(
        timeline, x="date_parsed", y="name", color="name",
        hover_data=["dose", "provider", "arm"],
        labels={"date_parsed": T["col_date"][:4], "name": T["col_name"]},
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_tl.update_traces(marker=dict(size=11, opacity=0.8, line=dict(width=1, color="#ffffff")))
    apply_chart_style(fig_tl, showlegend=False, height=360)
    st.plotly_chart(fig_tl, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"#### {T['vac_count']}")
        vc = df_r["name"].value_counts().reset_index()
        vc.columns = [T["col_name"], T["count"]]
        fig_vc = px.bar(vc, x=T["count"], y=T["col_name"], orientation="h",
                        color_discrete_sequence=[COLORS[0]])
        apply_chart_style(fig_vc)
        fig_vc.update_layout(yaxis={"categoryorder": "total ascending"})
        fig_vc.update_traces(marker_line_width=0)
        st.plotly_chart(fig_vc, use_container_width=True)

    with col2:
        st.markdown(f"#### {T['provider_stat']}")
        pc = df_r["provider"].value_counts().reset_index()
        pc.columns = [T["col_prov"], T["count"]]
        fig_pc = px.bar(pc, x=T["count"], y=T["col_prov"], orientation="h",
                        color_discrete_sequence=[COLORS[2]])
        apply_chart_style(fig_pc)
        fig_pc.update_layout(yaxis={"categoryorder": "total ascending"})
        fig_pc.update_traces(marker_line_width=0)
        st.plotly_chart(fig_pc, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"#### {T['yearly_stat']}")
        yc = df_r.dropna(subset=["year"]).groupby("year").size().reset_index(name=T["count"])
        yc["year"] = yc["year"].astype(int).astype(str)
        fig_yc = px.bar(yc, x="year", y=T["count"], text=T["count"],
                        color_discrete_sequence=[COLORS[1]])
        apply_chart_style(fig_yc, xaxis_title=T["year"])
        fig_yc.update_traces(marker_line_width=0, textposition="outside")
        st.plotly_chart(fig_yc, use_container_width=True)

    with col4:
        st.markdown(f"#### {T['arm_ratio']}")
        arm_df = df_r[df_r["arm"].isin(["L", "R"])]["arm"].value_counts().reset_index()
        arm_df.columns = ["arm", T["count"]]
        arm_df["arm"] = arm_df["arm"].map({"L": T["left_arm"], "R": T["right_arm"]})
        fig_arm = px.pie(arm_df, names="arm", values=T["count"], hole=0.45,
                         color_discrete_sequence=[COLORS[0], COLORS[1]])
        apply_chart_style(fig_arm)
        fig_arm.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(fig_arm, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# Data Quality
# ════════════════════════════════════════════════════════════════════════════
elif page == T["pages"][4]:
    st.title(T["dq_title"])
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

    if not issues:
        st.success(T["dq_ok"])
    else:
        for title, rows in issues:
            st.error(f"⚠️ {title}  ({len(rows)})")
            st.dataframe(rows, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# Export
# ════════════════════════════════════════════════════════════════════════════
elif page == T["pages"][5]:
    st.title(T["export_title"])
    st.info(f"{T['export_info']} **{len(df)}** {T['export_cols']}`{', '.join(COLUMNS)}`")

    col_csv, col_pdf = st.columns(2)

    # CSV download
    csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
    col_csv.download_button(
        label=T["download"], data=csv_bytes,
        file_name="vaccine_records_export.csv", mime="text/csv", type="primary",
    )

    # PDF download — generate on the fly so one click downloads directly
    with col_pdf:
        with st.spinner(""):
            try:
                pdf_bytes = build_pdf(
                    df,
                    title=T["pdf_title"],
                    generated_label=T["pdf_generated"],
                    total_label=T["pdf_total"],
                )
                st.download_button(
                    label=T["download_pdf"], data=pdf_bytes,
                    file_name="vaccine_records_export.pdf",
                    mime="application/pdf", type="primary",
                )
            except Exception as e:
                st.error(f"PDF generation failed: {e}")

    st.dataframe(df, use_container_width=True)

# ── Entry point: run via VSCode play button ───────────────────────────────────
if __name__ == "__main__" and not os.environ.get("IS_STREAMLIT_CHILD"):
    os.environ["IS_STREAMLIT_CHILD"] = "1"
    script = os.path.abspath(__file__)
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", script,
        "--server.headless", "true",
        "--server.port", "8501",
    ])
