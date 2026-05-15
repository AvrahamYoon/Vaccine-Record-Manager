import streamlit as st
import streamlit.components.v1 as components
import os

def init_custom_ui():
    """
    Initializes custom CSS and JS.
    Uses components.html for JS to ensure reliable execution in Streamlit.
    """
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    
    style_path = os.path.join(assets_dir, "style.css")
    script_path = os.path.join(assets_dir, "script.js")

    if os.path.exists(style_path):
        with open(style_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    if os.path.exists(script_path):
        with open(script_path, encoding="utf-8") as f:
            js_code = f.read()
            # Wrap JS in a component to ensure execution
            components.html(f"<script>{js_code}</script>", height=0, width=0)
