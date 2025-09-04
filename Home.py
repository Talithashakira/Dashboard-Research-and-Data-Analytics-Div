import streamlit as st


st.set_page_config(
    page_title="Introduksi",
     page_icon="📘",
     layout="wide"
)

st.title("Selamat Datang di Dashboard Research and Data Analytics 👋")

st.markdown("""
## 📖 Introduksi
Aplikasi ini dibuat untuk mempermudah analisis data transaksi unit rekreasi.

### 🔎 Alur Penggunaan
1. Pergi ke halaman **Dashboard** (lihat di sidebar kiri).
2. Upload file CSV transaksi.
3. Pilih unit yang ingin dianalisis (Ancol, Dufan, Atlantis, dll).

👉 Silakan mulai dengan memilih **Dashboard** pada sidebar.
""")
