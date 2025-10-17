import streamlit as st
from utils.auth_utils import check_login
from modules.ticket_transaction_etl import load_and_clean_data
from modules.customer_extraction import extract_unique_customers
import pandas as pd

st.set_page_config(
    page_title="Customer Data Extraction",
    layout="wide",
)

# --- Auth ---
authenticator = check_login()

st.title("👥 Customer Data Extraction")

uploaded_file = st.file_uploader("Upload CSV Anda", type=["csv"], key="file_customer_data")

if uploaded_file is not None:
    st.session_state.df_customer_data = load_and_clean_data(uploaded_file)
    df = st.session_state.get("df_customer_data")

    # --- Filter rentang Tgl Kunjungan sebelum ekstraksi ---
    visit_col = "Tgl Kunjungan"

    # Validasi kolom & nilai tanggal
    if visit_col not in df.columns:
        st.error(f"Kolom '{visit_col}' tidak ditemukan di data.")
    else:
        has_visit = df[visit_col].notna().any()
        if not has_visit:
            st.warning(f"Tidak ada nilai pada kolom '{visit_col}'. Ekstraksi akan memakai semua data.")
            df_filtered = df.copy()
        else:
            # Pastikan tipe datetime
            if not pd.api.types.is_datetime64_any_dtype(df[visit_col]):
                df[visit_col] = pd.to_datetime(df[visit_col], errors="coerce")

            # Dapatkan min & max date (sebagai date saja untuk widget)
            min_date = df[visit_col].min().date()
            max_date = df[visit_col].max().date()

            st.markdown("### Pilih Rentang *Tgl Kunjungan*")
            with st.form("visit_date_filter"):
                start_date, end_date = st.date_input(
                    "Rentang Tgl Kunjungan",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    format="DD/MM/YYYY",
                )
                submitted = st.form_submit_button("Filter & Ekstrak Pelanggan")

            # Default: belum submit → jangan proses ekstraksi
            if not has_visit:
                df_filtered = df.copy()
            elif submitted:
                # Validasi rentang
                if start_date > end_date:
                    st.error("Rentang tanggal tidak valid: tanggal awal lebih besar daripada tanggal akhir.")
                    df_filtered = df.iloc[0:0].copy()  # kosong
                else:
                    mask = df[visit_col].dt.date.between(start_date, end_date)
                    df_filtered = df.loc[mask].copy()

                    if df_filtered.empty:
                        st.warning("Tidak ada data dalam rentang tanggal yang dipilih.")
            else:
                st.info("Silakan pilih rentang tanggal dan klik **Filter & Ekstrak Pelanggan**.")
                st.stop()  # hentikan eksekusi sampai user submit

    # Jika sudah ada df_filtered (dari blok di atas), pakai itu untuk ekstraksi
    if "df_filtered" in locals():
        df_to_extract = df_filtered
    else:
        df_to_extract = df

    customers_dict = extract_unique_customers(df_to_extract)

    if not customers_dict:
        st.warning("Tidak ada data customer yang valid / tidak ada unit yang sesuai.")
    else:
        st.success("✅ Data customer berhasil diekstrak!")

        st.markdown("### Hasil Per Unit")
        for unit, df_unit in customers_dict.items():
            st.write(f"**{unit}** – {len(df_unit)} customer unik")
            st.dataframe(df_unit.head(), use_container_width=True)

            csv_bytes = df_unit.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=f"⬇️ Download data {unit}",
                data=csv_bytes,
                file_name=f"{unit.replace(' ', '_')}_customers.csv",
                mime="text/csv",
                key=f"dl_{unit}"
            )

        # Opsional: download semua unit sekaligus
        all_customers = pd.concat(customers_dict.values(), ignore_index=True)
        all_csv = all_customers.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download semua unit (gabungan)",
            data=all_csv,
            file_name="all_units_customers.csv",
            mime="text/csv",
        )
