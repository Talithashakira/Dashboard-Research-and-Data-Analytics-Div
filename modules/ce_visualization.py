# ce_visualization.py
import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt

from ui.components import sentiment_metric, custom_metric
from utils.helpers import get_tags_counts, get_tags_sentiment_counts


# ===============================
# Selektor Unit & Periode
# ===============================

def show_unit_selector(unit_options: list[str]) -> str | None:
    """Menampilkan selectbox unit. Return string nama unit atau None jika belum dipilih."""
    selected_unit = st.selectbox("Pilih Unit:", [""] + unit_options, key="ce_unit_select")
    return selected_unit or None


def show_period_filter(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Menampilkan multiselect periode (berdasar kolom 'Camp Sent On Date Time')."""
    st.subheader("📅 Filter Periode Survey")

    if "Camp Sent On Date Time" not in df.columns:
        st.warning("Kolom 'Camp Sent On Date Time' tidak ditemukan.")
        return df.copy(), []

    available_periods = (
        df["Camp Sent On Date Time"]
        .dropna()
        .dt.strftime("%d-%m-%Y")
        .unique()
        .tolist()
    )
    available_periods = sorted(available_periods)

    if not available_periods:
        st.info("Tidak ada periode yang tersedia pada dataset.")
        return df.copy(), []

    selected_periods = st.multiselect(
        "Pilih Periode Survey",
        options=available_periods,
        default=available_periods,
        key="ce_period_select"
    )

    if not selected_periods:
        st.info("Tidak ada periode dipilih. Menampilkan seluruh data.")
        return df.copy(), []

    mask = df["Camp Sent On Date Time"].dt.strftime("%d-%m-%Y").isin(selected_periods)
    df_filtered = df[mask].copy()
    return df_filtered, selected_periods


# ===============================
# 1) CSAT (Customer Satisfaction)
# ===============================

def show_csat(df_filtered: pd.DataFrame) -> None:
    """Menampilkan metric CSAT dan bar chart distribusi penilaian (kolom 'Numeric_CSI')."""
    st.subheader("⭐ Customer Satisfaction Score (CSAT)")
    if "Numeric_CSI" not in df_filtered.columns:
        st.warning("Kolom 'Numeric_CSI' tidak ditemukan.")
        return

    total_responses = df_filtered["Numeric_CSI"].notna().sum()
    satisfied_responses = df_filtered.loc[df_filtered["Numeric_CSI"] >= 4].shape[0]
    csat_score = (satisfied_responses / total_responses) * 100 if total_responses > 0 else 0.0

    custom_metric("📌 Customer Satisfaction Score", f"{csat_score:.2f}%")

    csi_counts = (
        df_filtered["Numeric_CSI"]
        .value_counts(dropna=True)
        .sort_index()
    )

    if csi_counts.empty:
        st.info("Belum ada data untuk ditampilkan pada CSAT.")
    else:
        st.bar_chart(csi_counts)


# ===============================
# 2) Intent to Return (CLI)
# ===============================

def show_intent_to_return(df_filtered: pd.DataFrame) -> None:
    """Menampilkan rata-rata 'Numeric_Will Return' dan bar chart distribusi."""
    st.subheader("🔁 Intent to Return")

    if "Numeric_Will Return" not in df_filtered.columns:
        st.warning("Kolom 'Numeric_Will Return' tidak ditemukan.")
        return

    avg_cli = df_filtered["Numeric_Will Return"].mean(skipna=True)
    avg_cli = 0.0 if pd.isna(avg_cli) else avg_cli
    custom_metric("📌 Rata-rata Intent to Return", f"{avg_cli:.2f}")

    cli_counts = (
        df_filtered["Numeric_Will Return"]
        .value_counts(dropna=True)
        .sort_index()
    )

    if cli_counts.empty:
        st.info("Belum ada data untuk ditampilkan pada Intent to Return.")
    else:
        st.bar_chart(cli_counts)


# ===============================
# 3) Sentiment Scorecards
# ===============================

def show_sentiment_scorecards(df_filtered: pd.DataFrame) -> None:
    """Menampilkan tiga kartu metrik sentimen (Positive, Neutral, Negative)."""
    st.subheader("💬 Sentiment Analysis")

    col_name = "Sentiment_Primary Reason"
    if col_name not in df_filtered.columns:
        st.warning(f"Kolom '{col_name}' tidak ditemukan.")
        return

    counts = df_filtered[col_name].value_counts(dropna=False)

    c1, c2, c3 = st.columns(3)
    with c1:
        sentiment_metric("😊 Positive Sentiment", int(counts.get("Positive", 0)), "Positive")
    with c2:
        sentiment_metric("😐 Neutral Sentiment", int(counts.get("Neutral", 0)), "Neutral")
    with c3:
        sentiment_metric("😡 Negative Sentiment", int(counts.get("Negative", 0)), "Negative")


# ===============================
# 4) Sentiment Tags (Positive & Negative)
# ===============================

def _show_single_sentiment_tags(
    df_filtered: pd.DataFrame,
    sentiment_label: str,
    treemap_color_scale: str,
    table_key: str
) -> None:
    """Utilitas untuk merender satu blok 'Positive' atau 'Negative' tags."""
    header = f"#### **{sentiment_label} Sentiment Tags**"
    st.markdown(header)

    c1, c2 = st.columns([1, 3])

    with c1:
        tag_counts = get_tags_counts(df_filtered, sentiment_label)
        st.write(f"**{sentiment_label} Tags Counts**")
        st.dataframe(tag_counts, use_container_width=True)

    with c2:
        if tag_counts.empty:
            st.info(f"Tidak ada tag untuk sentimen {sentiment_label}.")
        else:
            fig = px.treemap(
                tag_counts,
                path=["Tag"],
                values="Count",
                color="Count",
                color_continuous_scale=treemap_color_scale,
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"**Daftar {sentiment_label} Sentiment**")

    col_sent = "Sentiment_Primary Reason"
    col_tags = "Tags_Primary Reason"
    col_reason = "Primary Reason"

    if not all(c in df_filtered.columns for c in [col_sent, col_tags, col_reason]):
        st.warning("Kolom yang diperlukan untuk daftar detail tidak lengkap.")
        return

    df_sub = df_filtered[df_filtered[col_sent] == sentiment_label].copy()
    all_tags = (
        df_sub[col_tags]
        .dropna()
        .str.split("|")
        .explode()
        .str.strip()
        .dropna()
        .unique()
        .tolist()
    )

    selected_tags = st.multiselect(
        "Pilih Tags",
        options=sorted(all_tags),
        default=all_tags,
        key=table_key
    )

    if selected_tags:
        pattern = "|".join([t.replace("|", r"\|") for t in selected_tags])
        df_detail = df_sub[df_sub[col_tags].str.contains(pattern, na=False)][[col_reason, col_tags]]
        st.dataframe(df_detail, use_container_width=True)
    else:
        st.info("Tidak ada tag yang dipilih.")


def show_sentiment_tags_sections(df_filtered: pd.DataFrame) -> None:
    """Menampilkan dua blok: Positive Tags dan Negative Tags."""
    _show_single_sentiment_tags(
        df_filtered,
        sentiment_label="Positive",
        treemap_color_scale="Greens",
        table_key="pos_tag_picker"
    )
    _show_single_sentiment_tags(
        df_filtered,
        sentiment_label="Negative",
        treemap_color_scale="Reds",
        table_key="neg_tag_picker"
    )


# ===============================
# 5) Distribusi Sentiment by Tags
# ===============================

def show_tag_sentiment_distribution(df_filtered: pd.DataFrame) -> None:
    """Menampilkan bar chart horizontal distribusi sentiment per tag."""
    st.markdown("#### **Distribusi Sentiment Berdasarkan Tags**")

    tag_sentiment_counts = get_tags_sentiment_counts(df_filtered)
    if tag_sentiment_counts.empty:
        st.info("Tidak ada data tag-sentiment untuk ditampilkan.")
        return

    chart = (
        alt.Chart(tag_sentiment_counts)
        .mark_bar()
        .encode(
            x=alt.X("Count:Q", title="Jumlah"),
            y=alt.Y("Tags:N", sort="-x", title="Tags"),
            color=alt.Color(
                "Sentiment_Primary Reason:N",
                scale=alt.Scale(
                    domain=["Positive", "Neutral", "Negative"],
                    range=["#2ecc71", "#f1c40f", "#e74c3c"]
                ),
                title="Sentiment"
            ),
            tooltip=["Tags", "Sentiment_Primary Reason", "Count"]
        )
        .properties(width=600, height=400)
    )

    st.altair_chart(chart, use_container_width=True)
