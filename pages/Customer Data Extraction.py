import streamlit as st
from utils.auth_utils import check_login
from modules.ticket_transaction_etl import get_unique_customers, load_and_clean_data
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

    customers_dict = get_unique_customers(df)

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
