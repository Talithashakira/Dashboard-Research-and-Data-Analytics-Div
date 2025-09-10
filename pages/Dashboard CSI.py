import streamlit as st
import pandas as pd

from modules.csi_etl import load_and_clean_data

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

    # ===============================
    # 1. CSI (Customer Satisfaction Index)
    # ===============================
    st.subheader("⭐ Customer Satisfaction Index (CSI)")

    col1, col2 = st.columns([2, 1])

    with col1:
        csi_counts = df["CSI"].value_counts().sort_index()
        st.bar_chart(csi_counts)

    with col2:
        avg_csi = df["Numeric_CSI"].mean()
        st.metric("📌 Rata-rata CSI", f"{avg_csi:.2f}")

    # ===============================
    # 2. CLI (Customer Loyalty Index)
    # ===============================
    st.subheader("🔁 Customer Loyalty Index (CLI)")

    col3, col4 = st.columns([2, 1])

    with col3:
        cli_counts = df["Numeric_Will Return"].value_counts(dropna=True).sort_index()
        st.bar_chart(cli_counts)

    with col4:
        avg_cli = df["Numeric_Will Return"].mean()
        st.metric("📌 Rata-rata CLI", f"{avg_cli:.2f}")

    # ===============================
    # 3. Sentiment Scorecards
    # ===============================
    st.subheader("💬 Sentiment Analysis")

    sentiment_counts = df["Sentiment_Primary Reason"].value_counts()

    col5, col6, col7 = st.columns(3)

    col5.metric("😊 Positive", sentiment_counts.get("Positive", 0))
    col6.metric("😐 Neutral", sentiment_counts.get("Neutral", 0))
    col7.metric("😡 Negative", sentiment_counts.get("Negative", 0))

else:
    st.info("📂 Silakan upload file CSV terlebih dahulu untuk melihat dashboard.")
