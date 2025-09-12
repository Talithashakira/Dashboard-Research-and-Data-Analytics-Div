import streamlit as st
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
# Cek status login
# ===============================
if st.session_state.get("authentication_status"):
    # === Jika login sukses ===
    _show_sidebar()
    st.title("Selamat Datang 👋")
    st.markdown("#### **Dashboard Research & Data Analytics Division**")

    st.write(
        """
        Selamat datang di portal **Research & Data Analytics Division**.  
        Di sini kamu bisa memantau dan menganalisis berbagai data yang kami kelola.

        🔹 **Dashboard Customer Experience (CE)**  
        Menyajikan visualisasi hasil survei *Customer Satisfaction Index (CSI)*  
        yang dikumpulkan melalui survei Sensum.  
        Dashboard ini membantu memahami tingkat kepuasan, loyalitas, serta sentimen pelanggan
        terhadap layanan dan unit rekreasi di Ancol.

        🔹 **Dashboard Transaksi**  
        Menampilkan analisis dan visualisasi data transaksi yang diambil
        dari sistem penjualan pada **Dashboard Ancol**.
        Kamu dapat melihat tren pembayaran, unit dengan transaksi tertinggi,
        serta metrik keuangan lainnya untuk mendukung pengambilan keputusan.

        Gunakan menu di sidebar untuk menjelajahi setiap fitur. 🚀
        """
    )

    st.divider()
    st.write("📌 Silakan pilih menu di sebelah kiri untuk mulai melihat data.")

elif st.session_state.get("authentication_status") is False:
    # === Jika login gagal ===
    _hide_sidebar()
    st.error("❌ Username atau password salah")

else:
    # === Jika belum login ===
    _hide_sidebar()
    st.warning("Silakan login terlebih dahulu")
