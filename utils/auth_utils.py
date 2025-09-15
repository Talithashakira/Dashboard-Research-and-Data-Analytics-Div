# utils/auth_utils.py
import streamlit as st
import streamlit_authenticator as stauth

from utils.helpers import _hide_sidebar, _show_sidebar

def get_authenticator():
    config = {
        "credentials": {
            "usernames": {
                st.secrets['ADMIN_USER']: {
                    "password": st.secrets['ADMIN_PASSWORD']
                }
            }
        },
        "cookie": {
            "name": st.secrets['COOKIE_NAME'],
            "key": st.secrets['COOKIE_KEY'],
            "expiry_days": st.secrets['COOKIE_EXPIRY_DAYS']
        }
    }

    authenticator = stauth.Authenticate(
        credentials=config["credentials"],
        cookie_name=config["cookie"]["name"],
        key=config["cookie"]["key"],
        cookie_expiry_days=config["cookie"]["expiry_days"]
    )
    return authenticator


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
