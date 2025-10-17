# Dashboard CE.py
import streamlit as st
import pandas as pd

from modules.customer_survey_etl import load_and_clean_data
from utils.auth_utils import check_login

# >>> IMPORT modul visualisasi baru
from modules.ce_visualization import (
    show_unit_selector,
    show_period_filter,
    show_csat,
    show_intent_to_return,
    show_sentiment_scorecards,
    show_sentiment_tags_sections,
    show_tag_sentiment_distribution,
)

st.set_page_config(
    page_title="Dashboard Customer Experience",
    layout="wide",
)

# --- Auth ---
authenticator = check_login()

# --- Main ---
st.title("👥 Dashboard Customer Experience Report")

uploaded_file = st.file_uploader("Upload CSV Anda", type=["csv"], key="file_ce")

if uploaded_file is not None:
    # Load + simpan ke session (opsional)
    st.session_state.df_ce = load_and_clean_data(uploaded_file)
    df: pd.DataFrame = st.session_state.get("df_ce")

    # Opsi unit (bisa dipindah ke config)
    unit_options = [
        "Taman Pantai Ancol",
        "Dunia Fantasi",
        "Atlantis",
        "Samudra",
        "Sea World",
        "Jakarta Birdland",
        "Putri Duyung",
    ]

    # Pilih unit
    selected_unit = show_unit_selector(unit_options)

    if selected_unit:
        st.header(f"Report {selected_unit}", divider="gray")

        # Filter periode
        df_filtered, selected_periods = show_period_filter(df)

        # Layout 2 kolom: CSAT & Intent to Return
        col1, col2 = st.columns([2, 2])
        with col1:
            show_csat(df_filtered)
        with col2:
            show_intent_to_return(df_filtered)

        st.divider()

        # Sentiment scorecards
        show_sentiment_scorecards(df_filtered)

        # Sentiment tags (Positive & Negative)
        show_sentiment_tags_sections(df_filtered)

        # Distribusi Sentiment by Tags
        show_tag_sentiment_distribution(df_filtered)

    else:
        st.info("📌 Silakan pilih unit rekreasi untuk menampilkan laporan.")
else:
    st.info("📂 Silakan upload file CSV terlebih dahulu untuk melihat dashboard.")
