import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from utils.auth_utils import get_authenticator, _hide_sidebar, _show_sidebar

# ===============================
# Config halaman
# ===============================
st.set_page_config(
    page_title="Home", 
    page_icon="🏠", 
    layout="wide")
    

authenticator = get_authenticator()
st.session_state["authenticator"] = authenticator
authenticator.login(location="main")

# ===============================
# Cek status login & atur sidebar
# ===============================
if st.session_state.get("authentication_status"):
    # === Jika login sukses ===
    _show_sidebar()
    st.title("Selamat Datang")
    st.markdown("#### **Dashboard Research & Data Analytics Division**")
    st.divider()
    st.write("Konten dashboard di sini ...")

elif st.session_state.get("authentication_status") is False:
    # === Jika login gagal ===
    _hide_sidebar()
    st.error("❌ Username atau password salah")

else:
    # === Jika belum login ===
    _hide_sidebar()
    st.warning("Silakan login terlebih dahulu")
