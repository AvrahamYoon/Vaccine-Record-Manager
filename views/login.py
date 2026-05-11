import streamlit as st

from core.auth import set_authenticated, verify_login
from core.i18n import LANG


def render_login_page() -> None:
    """Full-page login when the auth gate is on and the session is not authenticated."""
    st.session_state.setdefault("lang_select", "English")
    lang = st.selectbox(
        "Language / 語言",
        list(LANG.keys()),
        index=list(LANG.keys()).index(st.session_state.get("lang_select", "English")),
        key="lang_select",
    )
    T = LANG[lang]

    st.title(T["login_title"])
    st.caption(T["login_caption"])

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(T["login_username_label"], autocomplete="username")
        password = st.text_input(T["login_password_label"], type="password", autocomplete="current-password")
        submitted = st.form_submit_button(T["login_submit"], type="primary")

    if submitted:
        if verify_login(username.strip(), password):
            set_authenticated(True)
            st.rerun()
        else:
            st.error(T["login_error"])
