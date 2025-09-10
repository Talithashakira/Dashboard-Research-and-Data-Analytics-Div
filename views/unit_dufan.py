import streamlit as st
import pandas as pd
from modules.visualization import (
    show_summary_cards,
    show_trend_payment,
    show_trend_purchased,
    show_top5_payment,
    show_top5_purchased,
    show_heatmap_calendar,
    show_customer_segmentation,
)
from utils.ui_utils import render_aggrid, download_csv_button

def show():
    df = st.session_state.df

    # 🔹 Filter berdasarkan Ticket Group
    df_unit = df[df["Ticket Group"] == "Dufan Ancol"]

    st.header("Unit Dufan", divider="gray")

    # Filter tanggal
    min_date, max_date = df_unit["Tgl Transaksi"].min(), df_unit["Tgl Transaksi"].max()
    start_date, end_date = st.date_input(
        "Pilih rentang tanggal (Dufan):", [min_date, max_date],
        min_value=min_date, max_value=max_date
    )
    mask = (df_unit["Tgl Transaksi"] >= pd.to_datetime(start_date)) & (df_unit["Tgl Transaksi"] <= pd.to_datetime(end_date))
    df_filtered = df_unit.loc[mask]

    # Summary cards
    show_summary_cards(df_filtered)

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

    # 🔹 Heatmap
    st.altair_chart(show_heatmap_calendar(df_filtered), use_container_width=True)

    # AgGrid
    render_aggrid(df_filtered)

    # Download button
    download_csv_button(df_filtered, filename="transaksi_dufan.csv")
