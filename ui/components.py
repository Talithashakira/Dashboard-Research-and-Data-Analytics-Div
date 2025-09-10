import streamlit as st
from ui.styles import BRAND_COLORS, GRAY_COLORS, STATUS_COLORS

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


def custom_metric(label, value):
    html = f"""
    <div style="
        background-color:{GRAY_COLORS[50]};
        border: 1px solid {GRAY_COLORS[500]};
        border-radius: 12px;
        padding: 12px;
        text-align: left;
        margin-bottom: 16px;
        ">
        <div style="font-size:14px; color:#31333F; margin-bottom:4px;">{label}</div>
        <div style="font-size:28px; font-weight:600; color:#090A11;">{value}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def sentiment_metric(label, value, status):
    color = STATUS_COLORS[status][500]
    html = f"""
    <div style="
        background-color: {STATUS_COLORS[status][50]};
        border: 1px solid {color};
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        margin-bottom: 16px;
        ">
        <div style="font-size:16px; color:#31333F; margin-bottom:4px;">{label}</div>
        <div style="font-size:32px; font-weight:600; color:{color};">{value}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)