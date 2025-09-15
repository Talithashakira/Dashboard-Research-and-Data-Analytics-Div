import streamlit as st
import pandas as pd
import re

def format_rupiah(x: float) -> str:
    if x >= 1_000_000_000:
        return f"Rp {x/1_000_000_000:.1f}M"
    elif x >= 1_000_000:
        return f"Rp {x/1_000_000:.1f}jt"
    else:
        return f"Rp {x:,.0f}"

def _hide_sidebar():
    """
    Menyembunyikan sidebar Streamlit
    """
    hide_style = """
        <style>
        [data-testid="stSidebar"] {display: none;}
        button[data-testid="stBaseButton-headerNoPadding"] {display: none;}
        </style>
    """
    st.markdown(hide_style, unsafe_allow_html=True)

def _show_sidebar():
    """
    Menampilkan sidebar Streamlit
    """
    show_style = """
        <style>
        [data-testid="stSidebar"] {display: block !important;}
        button[data-testid="stBaseButton-headerNoPadding"] {display: block !important;}
        </style>
    """
    st.markdown(show_style, unsafe_allow_html=True)

def map_columns(df: pd.DataFrame, question_map: dict) -> pd.DataFrame:
    col_mapping = {}
    for pattern, std_name in question_map.items():
        for col in df.columns:
            if re.search(pattern, col, flags=re.IGNORECASE):
                col_mapping[col] = std_name
                break
    return df.rename(columns=col_mapping)

def get_tags_counts(df, sentiment):
    df_sentiment = df[df["Sentiment_Primary Reason"] == sentiment]

    all_tags = (
        df_sentiment["Tags_Primary Reason"]
        .dropna()
        .str.split("|")
        .explode()
        .str.strip()
    )

    tag_counts = all_tags.value_counts().reset_index()
    tag_counts.columns = ["Tag", "Count"]

    return tag_counts

def get_tags_sentiment_counts(df):
    # Ambil kolom Sentiment dan Tags
    df_tags = df[["Tags_Primary Reason", "Sentiment_Primary Reason"]].dropna()

    # Pecah tags yang dipisahkan "|"
    df_tags = (
        df_tags.assign(Tags=df_tags["Tags_Primary Reason"].str.split("|"))
        .explode("Tags")
    )
    df_tags["Tags"] = df_tags["Tags"].str.strip()

    # Hitung jumlah kombinasi Tags x Sentiment
    tag_counts = (
        df_tags.groupby(["Tags", "Sentiment_Primary Reason"])
        .size()
        .reset_index(name="Count")
    )

    return tag_counts
