import streamlit as st
import pandas as pd
import plotly.express as px

from modules.csi_etl import load_and_clean_data
from ui.components import sentiment_metric, custom_metric
from utils.helpers import get_tags_counts

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


        st.markdown("#### **Positive Sentiment Tags**")
        col1, col2, = st.columns([1, 3])

        with col1:
            tag_counts_positive = get_tags_counts(df_filtered, "Positive")
            st.write("**Positive Tags Counts**")
            st.dataframe(tag_counts_positive, use_container_width=True)
        
        with col2:
            fig = px.treemap(
                tag_counts_positive,
                path=["Tag"],
                values="Count",
                color="Count",
                color_continuous_scale="Greens",
            )
            st.plotly_chart(fig)
        
        df_positive = df_filtered[df_filtered["Sentiment_Primary Reason"] == "Positive"]

        # Ambil semua tag unik
        all_tags_pos = (
            df_positive["Tags_Primary Reason"]
            .dropna()
            .str.split("|")
            .explode()
            .str.strip()
            .unique()
        )

        selected_tags_pos = st.multiselect(
            "Pilih Tags (Positive)",
            options=sorted(all_tags_pos),
            default=all_tags_pos  # default semua tampil
        )

        if selected_tags_pos:
            df_positive_filtered = df_positive[
                df_positive["Tags_Primary Reason"].str.contains("|".join(selected_tags_pos), na=False)
            ][["Primary Reason", "Tags_Primary Reason"]]

            st.dataframe(df_positive_filtered, use_container_width=True)


        st.markdown("#### **Negative Sentiment Tags**")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            tag_counts_negative = get_tags_counts(df_filtered, "Negative")
            st.write("**Negative Tags Counts**")
            st.dataframe(tag_counts_negative, use_container_width=True)
        
        with col2:
            fig = px.treemap(
                tag_counts_negative,
                path=["Tag"],
                values="Count",
                color="Count",
                color_continuous_scale="Reds",
            )
            st.plotly_chart(fig)

        df_negative = df_filtered[df_filtered["Sentiment_Primary Reason"] == "Negative"]

        # Ambil semua tag unik
        all_tags_neg = (
            df_negative["Tags_Primary Reason"]
            .dropna()
            .str.split("|")
            .explode()
            .str.strip()
            .unique()
        )

        selected_tags_neg = st.multiselect(
            "Pilih Tags (Negative)",
            options=sorted(all_tags_neg),
            default=all_tags_neg
        )

        if selected_tags_neg:
            df_negative_filtered = df_negative[
                df_negative["Tags_Primary Reason"].str.contains("|".join(selected_tags_neg), na=False)
            ][["Primary Reason", "Tags_Primary Reason"]]

            st.dataframe(df_negative_filtered, use_container_width=True)

    else:
        st.info("📌 Silakan pilih unit rekreasi untuk menampilkan laporan.")

else:
    st.info("📂 Silakan upload file CSV terlebih dahulu untuk melihat dashboard.")
