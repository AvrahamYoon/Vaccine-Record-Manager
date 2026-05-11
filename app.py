import os
import subprocess
import sys

import streamlit as st

from core.auth import is_auth_gate_enabled, is_authenticated, set_authenticated
from core.data_store import load_data
from core.i18n import LANG
from views.export import render_export_page
from views.overview import render_overview_page
from views.records import render_records_page
from views.login import render_login_page
from views.settings import render_settings_page

st.set_page_config(page_title="Vaccine Records", page_icon="💉", layout="wide")

st.markdown(
    """
<style>
    .stApp { background: #f5f6fa; }
    .block-container { padding: 2rem 2.5rem; max-width: 1180px; }
    [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e8eaed; }
    [data-testid="stSidebar"] .stRadio > label { display: none; }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap: 2px; }
    [data-testid="stSidebar"] .stRadio label {
        padding: 0.55rem 0.9rem !important; border-radius: 8px !important; font-size: 0.9rem !important;
        color: #4b5563 !important; font-weight: 500 !important; cursor: pointer; transition: background 0.15s;
    }
    [data-testid="stSidebar"] .stRadio label:hover { background: #f0f2f5 !important; }
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] span:first-child { display: none; }
    .stat-card {
        background: #ffffff; border-radius: 12px; padding: 1.1rem 1rem 1rem 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 8px rgba(0,0,0,0.04); text-align: center;
    }
    .stat-label {
        font-size: 0.72rem; color: #9ca3af; font-weight: 600; letter-spacing: 0.06em;
        text-transform: uppercase; margin-bottom: 0.4rem;
    }
    .stat-value { font-size: 1.75rem; font-weight: 700; color: #111827; line-height: 1.1; }
    h1 {
        font-size: 1.5rem !important; font-weight: 700 !important; color: #111827 !important;
        margin-bottom: 1.2rem !important; padding-bottom: 0.6rem !important; border-bottom: 1px solid #e8eaed !important;
    }
    h4 { color: #374151 !important; font-size: 0.95rem !important; font-weight: 600 !important; margin-bottom: 0.5rem !important; }
    .stButton > button[kind="primary"] {
        background: #4f7df3 !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; color: white !important;
    }
    .stButton > button[kind="primary"]:hover { background: #3b6de0 !important; }
    .stButton > button[kind="secondary"] { border-radius: 8px !important; border-color: #d1d5db !important; color: #374151 !important; }
    [data-testid="stExpander"] {
        background: #ffffff; border-radius: 10px !important; border: 1px solid #e8eaed !important; box-shadow: none !important;
    }
    [data-testid="stForm"] {
        background: #ffffff; border-radius: 12px; padding: 1.5rem !important;
        border: 1px solid #e8eaed !important; box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }
    hr { border-color: #e8eaed; margin: 1.2rem 0; }
    [data-testid="stSidebar"] .stSelectbox label { color: #6b7280 !important; font-size: 0.8rem !important; }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: #f9fafb !important; border-color: #e5e7eb !important; border-radius: 8px !important; color: #374151 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

_auth_on = is_auth_gate_enabled()
if _auth_on and not is_authenticated():
    render_login_page()
    st.stop()

with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    lang_key = st.session_state.get("lang_select", "English")
    T = LANG[lang_key]
    st.markdown(
        f"<p style='font-size:1.05rem;font-weight:700;color:#111827;margin:0 0 0.8rem 0.2rem'>💉 {T['app_title']}</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='margin:0 0 0.8rem 0;border-color:#e8eaed'>", unsafe_allow_html=True)
    page = st.radio("nav", T["pages"], label_visibility="collapsed")
    if _auth_on:
        st.markdown("<hr style='margin:0.8rem 0;border-color:#e8eaed'>", unsafe_allow_html=True)
        if st.button(T["login_logout"], key="logout_btn"):
            set_authenticated(False)
            st.rerun()

T = LANG[st.session_state.get("lang_select", "English")]
lang_key = st.session_state.get("lang_select", "English")
use_abbr = st.session_state.get("name_fmt", "abbr") == "abbr"
df = load_data()


def _pick_name(row):
    if lang_key == "English":
        return row["abbr_en"] if use_abbr else row["name_en"]
    return row["abbr_zh"] if use_abbr else row["name"]


df["_display_name"] = df.apply(_pick_name, axis=1)

if page == T["pages"][0]:
    render_overview_page(df, T)
elif page == T["pages"][1]:
    render_records_page(df, T, lang_key, use_abbr)
elif page == T["pages"][2]:
    render_export_page(df, T)
elif page == T["pages"][3]:
    render_settings_page(df, T, lang_key, use_abbr)

if __name__ == "__main__" and not os.environ.get("IS_STREAMLIT_CHILD"):
    os.environ["IS_STREAMLIT_CHILD"] = "1"
    script = os.path.abspath(__file__)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            script,
            "--server.headless",
            "true",
            "--server.port",
            "8501",
        ]
    )
