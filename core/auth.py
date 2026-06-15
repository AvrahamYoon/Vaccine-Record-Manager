"""Login gate: enabled by default; override credentials via env or secrets.toml."""

from __future__ import annotations

import hashlib
import hmac
import os

import streamlit as st
from streamlit.runtime.secrets import StreamlitSecretNotFoundError

from core.data_store import is_demo_mode

# Defaults (override with VACCINE_APP_USERNAME / VACCINE_APP_PASSWORD or .streamlit/secrets.toml)
DEFAULT_LOGIN_USERNAME = "admin"
DEFAULT_LOGIN_PASSWORD = "RO_760715"


def is_auth_gate_enabled() -> bool:
    """If False, the app runs without any login (for local dev / CI / demo)."""
    if is_demo_mode():
        return False
    v = os.environ.get("VACCINE_APP_NO_AUTH", "").strip().lower()
    return v not in ("1", "true", "yes", "on")


def _secrets_dict():
    try:
        return st.secrets
    except (FileNotFoundError, RuntimeError, OSError, AttributeError, StreamlitSecretNotFoundError):
        return None


def _safe_secret_lookup(secret_obj, key: str, parent_key: str | None = None) -> str:
    if secret_obj is None:
        return ""
    try:
        if parent_key is None:
            if key in secret_obj and str(secret_obj[key]).strip():
                return str(secret_obj[key]).strip()
        else:
            auth = secret_obj.get(parent_key)
            if isinstance(auth, dict) and str(auth.get(key, "")).strip():
                return str(auth[key]).strip()
    except StreamlitSecretNotFoundError:
        return ""
    return ""


def get_expected_username() -> str:
    env_u = os.environ.get("VACCINE_APP_USERNAME", "").strip()
    if env_u:
        return env_u
    sec = _secrets_dict()
    username = _safe_secret_lookup(sec, "login_username")
    if username:
        return username
    auth_username = _safe_secret_lookup(sec, "login_username", parent_key="auth")
    if auth_username:
        return auth_username
    return DEFAULT_LOGIN_USERNAME


def get_expected_password() -> str:
    env_p = os.environ.get("VACCINE_APP_PASSWORD", "").strip()
    if env_p:
        return env_p
    sec = _secrets_dict()
    password = _safe_secret_lookup(sec, "login_password")
    if password:
        return password
    auth_password = _safe_secret_lookup(sec, "login_password", parent_key="auth")
    if auth_password:
        return auth_password
    return DEFAULT_LOGIN_PASSWORD


def is_authenticated() -> bool:
    return bool(st.session_state.get("_auth_ok"))


def set_authenticated(value: bool) -> None:
    st.session_state["_auth_ok"] = bool(value)


def _digest_eq(a: str, b: str) -> bool:
    ha = hashlib.sha256(a.encode("utf-8")).digest()
    hb = hashlib.sha256(b.encode("utf-8")).digest()
    return hmac.compare_digest(ha, hb)


def verify_login(username: str, password: str) -> bool:
    return _digest_eq(username, get_expected_username()) and _digest_eq(password, get_expected_password())
