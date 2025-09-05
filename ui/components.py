import streamlit as st
from ui.styles import BRAND_COLORS

def branded_metric(label: str, value: str, unit: str):
    color = BRAND_COLORS[unit][500]
    html = f"""
    <div style="
        background-color: {BRAND_COLORS[unit][50]};
        border: 1px solid {color};
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        margin-bottom: 16px;
    ">

    <div style="color: {color}; font-size: 14px; font-weight: regular;">{label}</div>
    <div style="color: {color}; font-size: 24px; font-weight: medium;">{value}</div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)