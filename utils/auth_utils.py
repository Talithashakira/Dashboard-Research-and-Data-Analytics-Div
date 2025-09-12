# utils/auth_utils.py
import streamlit as st
import streamlit_authenticator as stauth

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


def _hide_sidebar():
    """
    Menyembunyikan sidebar Streamlit
    """
    hide_style = """
        <style>
        [data-testid="stSidebar"] {display: none;}
        button[data-testid="stBaseButton-headerNoPadding"] {display: none;}
        </style>
    """
    st.markdown(hide_style, unsafe_allow_html=True)


def _show_sidebar():
    """
    Menampilkan sidebar Streamlit
    """
    show_style = """
        <style>
        [data-testid="stSidebar"] {display: block !important;}
        button[data-testid="stBaseButton-headerNoPadding"] {display: block !important;}
        </style>
    """
    st.markdown(show_style, unsafe_allow_html=True)


def check_login(location: str = "unrendered"):
    """
    Mengecek status login user.
    Jika belum login atau salah, otomatis berhenti dan sembunyikan sidebar.
    """
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
