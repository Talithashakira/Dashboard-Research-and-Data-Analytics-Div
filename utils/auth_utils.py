import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

def get_authenticator():
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        credentials=config["credentials"],
        cookie_name=config["cookie"]["name"],
        key=config["cookie"]["key"],
        cookie_expiry_days=config["cookie"]["expiry_days"]
    )
    return authenticator


def _hide_sidebar():
    hide_style = """
        <style>
        [data-testid="stSidebar"] {display: none;}
        button[data-testid="stBaseButton-headerNoPadding"] {display: none;}
        </style>
    """
    st.markdown(hide_style, unsafe_allow_html=True)

def _show_sidebar():
    show_style = """
        <style>
        [data-testid="stSidebar"] {display: block !important;}
        button[data-testid="stBaseButton-headerNoPadding"] {display: block !important;}
        </style>
    """
    st.markdown(show_style, unsafe_allow_html=True)

def check_login(location: str = "unrendered"):
    authenticator = get_authenticator()
    authenticator.login(location=location)

    auth_status = st.session_state.get("authentication_status")

    if auth_status is None:
        _hide_sidebar()
        st.warning("🔐 Silakan login terlebih dahulu untuk mengakses dashboard.")
        st.stop()

    if auth_status is False:
        _hide_sidebar()
        st.error("❌ Username atau password salah.")
        st.stop()

    _show_sidebar()
    return authenticator