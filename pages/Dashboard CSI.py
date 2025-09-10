import streamlit as st
import pandas as pd

from modules.csi_etl import load_and_clean_data
from ui.components import sentiment_metric, custom_metric
from utils.helpers import get_top_tags

st.set_page_config(
    page_title="Dashboard CSI",
    layout="wide",
)

st.title("👥 Dashboard CSI Report")

uploaded_file = st.file_uploader("Upload CSV Anda", type=["csv"])

if uploaded_file is not None:
    if "df" not in st.session_state:
        st.session_state.df = load_and_clean_data(uploaded_file)

    df = st.session_state.df

    unit_options = [
        "Taman Pantai Ancol",
        "Dunia Fantasi",
        "Atlantis",
        "Samudra",
        "Sea World",
        "Jakarta Birdland",
        "Putri Duyung",
    ]

    selected_unit = st.selectbox("Pilih Unit:", [""] + unit_options)

    if selected_unit:
        st.header(f"Report {selected_unit}", divider="gray")


        # ===============================
        # 🔎 Filter Periode Survey
        # ===============================
        st.subheader("📅 Filter Periode Survey")

        available_periods = (
            df["Camp Sent On Date Time"]
            .dt.strftime("%d-%m-%Y")
            .dropna()
            .unique()
        )

        available_periods = sorted(available_periods)

        selected_period = st.multiselect(
            "Pilih Periode Survey",
            options=available_periods,
            default=available_periods
        )
        
        df_filtered = df[df["Camp Sent On Date Time"].dt.strftime("%d-%m-%Y").isin(selected_period)]

        col1, col2 = st.columns([2, 2])

        # ===============================
        # 1. CSI (Customer Satisfaction Index)
        # ===============================

        with col1:
            st.subheader("⭐ Customer Satisfaction Index (CSI)")

            avg_csi = df_filtered["Numeric_CSI"].mean()
            custom_metric("📌 Rata-rata Customer Satisfaction Index", f"{avg_csi:.2f}")

            csi_counts = df_filtered["Numeric_CSI"].value_counts().sort_index()
            st.bar_chart(csi_counts)

        # ===============================
        # 2. CLI (Customer Loyalty Index)
        # ===============================

        with col2:
            st.subheader("🔁 Customer Loyalty Index (CLI)")

            avg_cli = df_filtered["Numeric_Will Return"].mean()
            custom_metric("📌 Rata-rata Customer Loyalty Index", f"{avg_cli:.2f}")

            cli_counts = df_filtered["Numeric_Will Return"].value_counts(dropna=True).sort_index()
            st.bar_chart(cli_counts)

        # ===============================
        # 3. Sentiment Scorecards
        # ===============================
        st.subheader("💬 Sentiment Analysis")

        sentiment_counts = df_filtered["Sentiment_Primary Reason"].value_counts()

        col1, col2, col3 = st.columns(3)

        with col1:
            sentiment_metric("😊 Positive Sentiment", sentiment_counts.get("Positive", 0), "Positive")
        with col2:
            sentiment_metric("😐 Neutral Sentiment", sentiment_counts.get("Neutral", 0), "Neutral")
        with col3:
            sentiment_metric("😡 Negative Sentiment", sentiment_counts.get("Negative", 0), "Negative")

        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏷️ Top Positive Tags")
            st.bar_chart(get_top_tags(df_filtered, "Positive"))
        
        with col2:
            st.subheader("🏷️ Top Negative Tags")
            st.bar_chart(get_top_tags(df_filtered, "Negative"))
    
    else:
        st.info("📌 Silakan pilih unit rekreasi untuk menampilkan laporan.")

else:
    st.info("📂 Silakan upload file CSV terlebih dahulu untuk melihat dashboard.")
