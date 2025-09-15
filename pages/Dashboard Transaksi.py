import streamlit as st
import pandas as pd

# Import dari modules
from modules.ticket_transaction_etl import load_and_clean_data
from views import unit_ancol as ancol, unit_dufan as dufan, unit_atlantis as atlantis, unit_samudra as samudra, unit_seaworld as seaworld, unit_birdland as birdland
from modules.transaction_visualization import (
    show_summary_cards,
    show_trend_payment,
    show_trend_purchased,
    show_top5_payment,
    show_top5_purchased,
    show_heatmap_calendar,
    show_total_payment_per_unit,
    show_customer_segmentation,
)
from utils.ui_utils import render_aggrid, download_csv_button
from utils.auth_utils import check_login

st.set_page_config(
    page_title="Dashboard Transaksi",
     layout="wide",
)

# --- Auth ---
authenticator = check_login()

# --- Main ---
st.title("📊 Dashboard Monthly Transaction Report")

# Upload CSV
uploaded_file = st.file_uploader("Upload CSV Anda", type=["csv"], key="file_transaksi")

if uploaded_file is not None:
    st.session_state.df_transaksi = load_and_clean_data(uploaded_file)

    df = st.session_state.get("df_transaksi")   

    menu = st.sidebar.selectbox(
        "Pilih Unit",
        ["Semua Transaksi", "Ancol", "Dufan", "Atlantis", "Samudra", "Sea World", "Birdland"],
        index=0
    )

    if menu == "Semua Transaksi":
        st.subheader("📌 Semua Transaksi")

        # Filter tanggal
        min_date, max_date = df["Tgl Transaksi"].min(), df["Tgl Transaksi"].max()
        start_date, end_date = st.date_input(
            "Pilih rentang tanggal:", [min_date, max_date],
            min_value=min_date, max_value=max_date
        )
        mask = (df["Tgl Transaksi"] >= pd.to_datetime(start_date)) & (df["Tgl Transaksi"] <= pd.to_datetime(end_date))
        df_filtered = df.loc[mask]

        # Summary cards
        show_summary_cards(df_filtered)

        show_total_payment_per_unit(df_filtered)

        # 🔹 Trend vs Top 5 Payment
        col1, col2 = st.columns([2, 1])
        with col1:
            st.altair_chart(show_trend_payment(df_filtered), use_container_width=True)
        with col2:
            st.altair_chart(show_top5_payment(df_filtered), use_container_width=True)

        # 🔹 Trend vs Top 5 Purchased
        col1, col2 = st.columns([2, 1])
        with col1:
            st.altair_chart(show_trend_purchased(df_filtered), use_container_width=True)
        with col2:
            st.altair_chart(show_top5_purchased(df_filtered), use_container_width=True)

        # 🔹 Customer Segmentation
        show_customer_segmentation(df_filtered)

        # 🔹 Heatmap Kunjungan per Hari
        st.altair_chart(show_heatmap_calendar(df_filtered), use_container_width=True)

        # AgGrid
        render_aggrid(df_filtered)

        # Download button
        download_csv_button(df_filtered, filename="transaksi_semua.csv")

    elif menu == "Ancol":
        ancol.show()
    elif menu == "Dufan":
        dufan.show()
    elif menu == "Atlantis":
        atlantis.show()
    elif menu == "Samudra":
        samudra.show()
    elif menu == "Sea World":
        seaworld.show()
    elif menu == "Birdland":
        birdland.show()
else:
    st.info("📂 Silakan upload file CSV terlebih dahulu untuk melihat dashboard.")