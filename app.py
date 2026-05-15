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


# Load external CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css("assets/style.css")

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
