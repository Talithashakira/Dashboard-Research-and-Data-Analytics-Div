import streamlit as st
import pandas as pd
import altair as alt

from ui.styles import BRAND_COLORS
from ui.components import branded_metric, custom_metric
from utils.helpers import format_rupiah

def show_summary_cards(df):
    col1, col2, col3 = st.columns(3)

    # 🎟️ Total Ticket Purchased
    with col1:
        total_tickets = df["Ticket Purchased"].sum()
        custom_metric("🎟️ Total Ticket Purchased", f"{total_tickets:,}")

    # 💰 Total Payment
    with col2:
        total_payment = df["Total Payment"].sum()
        custom_metric("💰 Total Payment", f"Rp {total_payment:,.0f}")

    # 📈 Daily Growth (%)
    with col3:
        df["Tgl Transaksi"] = pd.to_datetime(df["Tgl Transaksi"])
        daily_sales = df.groupby("Tgl Transaksi")["Ticket Purchased"].sum().sort_index()

        daily_growth = daily_sales.pct_change() * 100

        avg_growth = daily_growth.dropna().mean()

        if pd.isna(avg_growth):
            avg_growth = 0

        custom_metric("📈 Rata-rata Daily Growth", f"{avg_growth:.2f} %")


# =====================
# Trend Charts
# =====================
def show_trend_payment(df_filtered):
    """Trend berdasarkan Total Payment per Unit"""

   # Ambil warna brand utama (500)
    unit_colors = {unit: color[500] for unit, color in BRAND_COLORS.items()}

    df_filtered["Tgl Transaksi"] = pd.to_datetime(df_filtered["Tgl Transaksi"])
    df_filtered["weekday"] = df_filtered["Tgl Transaksi"].dt.dayofweek

    weekend_df = df_filtered[df_filtered["weekday"].isin([4, 5, 6])].copy()
    weekend_df["day_start"] = weekend_df["Tgl Transaksi"].dt.floor("D")
    weekend_df["day_end"] = weekend_df["Tgl Transaksi"].dt.floor("D") + pd.Timedelta(days=1)

    trend = df_filtered.groupby(["Tgl Transaksi", "Ticket Group"]).agg({
        "Total Payment": "sum"
    }).reset_index()

    weekend_bg = (
        alt.Chart(weekend_df.drop_duplicates("Tgl Transaksi"))
        .mark_rect(color="lightblue", opacity=0.3)
        .encode(x="day_start:T", x2="day_end:T")
    )

    lines = (
        alt.Chart(trend)
        .mark_line(point=True)
        .encode(
            x="Tgl Transaksi:T",
            y="Total Payment:Q",
            color=alt.Color("Ticket Group:N",
                            scale=alt.Scale(domain=list(unit_colors.keys()),
                                            range=list(unit_colors.values()))),
            tooltip=["Tgl Transaksi", "Ticket Group", "Total Payment"]
        )
    )

    return alt.layer(weekend_bg, lines).properties(
        width=500, height=400, title="📈 Trend Total Payment"
    ).interactive()


def show_trend_purchased(df_filtered):
    """Trend berdasarkan Ticket Purchased per Unit"""

    # Ambil warna brand utama (500)
    unit_colors = {unit: color[500] for unit, color in BRAND_COLORS.items()}

    df_filtered["Tgl Transaksi"] = pd.to_datetime(df_filtered["Tgl Transaksi"])
    df_filtered["weekday"] = df_filtered["Tgl Transaksi"].dt.dayofweek

    weekend_df = df_filtered[df_filtered["weekday"].isin([4, 5, 6])].copy()
    weekend_df["day_start"] = weekend_df["Tgl Transaksi"].dt.floor("D")
    weekend_df["day_end"] = weekend_df["Tgl Transaksi"].dt.floor("D") + pd.Timedelta(days=1)

    trend = df_filtered.groupby(["Tgl Transaksi", "Ticket Group"]).agg({
        "Ticket Purchased": "sum"
    }).reset_index()

    weekend_bg = (
        alt.Chart(weekend_df.drop_duplicates("Tgl Transaksi"))
        .mark_rect(color="lightblue", opacity=0.3)
        .encode(x="day_start:T", x2="day_end:T")
    )

    lines = (
        alt.Chart(trend)
        .mark_line(point=True)
        .encode(
            x="Tgl Transaksi:T",
            y="Ticket Purchased:Q",
            color=alt.Color("Ticket Group:N",
                            scale=alt.Scale(domain=list(unit_colors.keys()),
                                            range=list(unit_colors.values()))),
            tooltip=["Tgl Transaksi", "Ticket Group", "Ticket Purchased"]
        )
    )

    return alt.layer(weekend_bg, lines).properties(
        width=500, height=400, title="📈 Trend Ticket Purchased"
    ).interactive()


# =====================
# Top 5 Charts
# =====================
def show_top5_payment(df_filtered):
    """Top 5 Ticket berdasarkan Payment"""
    top5_payment = (
        df_filtered.groupby("Ticket Detail")["Total Payment"]
        .sum()
        .nlargest(5)
        .reset_index()
    )

    top5_payment["label"] = top5_payment["Total Payment"].apply(format_rupiah)

    base = (
        alt.Chart(top5_payment)
        .mark_bar(color="#00205B")
        .encode(
            x="Total Payment:Q",
            y=alt.Y("Ticket Detail:N", sort="-x"),
            tooltip=["Ticket Detail", alt.Tooltip("Total Payment:Q", format=",")]
        )
    )

    # Tambahkan label di ujung bar
    text = base.mark_text(
        align='left',
        baseline='middle',
        dx=3  
    ).encode(
        text="label:N"
    )

    chart = base + text

    return chart.properties(width=400, height=400, title="🏆 Top 5 Ticket by Payment")


def show_top5_purchased(df_filtered):
    """Top 5 Ticket berdasarkan Purchased"""
    top5_purchased = (
        df_filtered.groupby("Ticket Detail")["Ticket Purchased"]
        .sum()
        .nlargest(5)
        .reset_index()
    )

    return (
        alt.Chart(top5_purchased)
        .mark_bar(color="#00205B") 
        .encode(
            x="Ticket Purchased:Q",
            y=alt.Y("Ticket Detail:N", sort="-x"),
            tooltip=["Ticket Detail", "Ticket Purchased"]
        )
        .properties(width=300, height=400, title="🏆 Top 5 Ticket by Purchased")
    )



def show_heatmap_calendar(df_filtered: pd.DataFrame):
    import altair as alt

    df_filtered = df_filtered.copy()  # biar aman dari SettingWithCopy

    # Pastikan kolom tanggal valid
    if "Tgl Kunjungan" not in df_filtered.columns:
        raise KeyError("Kolom 'Tgl Kunjungan' tidak ditemukan di dataframe")

    # Tambahkan kolom tahun, bulan, hari
    df_filtered["year"] = df_filtered["Tgl Kunjungan"].dt.year
    df_filtered["month_num"] = df_filtered["Tgl Kunjungan"].dt.month
    df_filtered["month_name"] = df_filtered["Tgl Kunjungan"].dt.month_name()
    df_filtered["day"] = df_filtered["Tgl Kunjungan"].dt.day

    # 🔹 Hitung total pengunjung per tanggal
    visits = (
        df_filtered.groupby(["year", "month_num", "month_name", "day"])["Total Ticket Purchase"]
        .sum()
        .reset_index(name="count")
    )

    # 🔹 Buat heatmap
    heatmap = (
        alt.Chart(visits)
        .mark_rect()
        .encode(
            x=alt.X("day:O", title="Day of Month"),
            y=alt.Y(
                "month_name:N",
                title="Month",
                sort=alt.SortField("month_num", order="ascending"),
            ),
            color=alt.Color("count:Q", scale=alt.Scale(scheme="blues"), title="Jumlah Orang"),
            tooltip=["year", "month_name", "day", "count"],
        )
        .properties(width=500, height=300, title="📊 Heatmap Kunjungan")
    )

    return heatmap

def show_total_payment_per_unit(df_filtered):
    total_payment_per_unit = (
        df_filtered.groupby("Ticket Group")["Total Payment"]
        .sum()
        .reset_index()
    )

    cols = st.columns(len(total_payment_per_unit))

    for  i, row in total_payment_per_unit.iterrows():
        unit = row["Ticket Group"]
        value = format_rupiah(row["Total Payment"])
        label = f"{row['Ticket Group']}"

        with cols[i]:
            branded_metric(label, value, unit)

def show_customer_segmentation(df_filtered):
    promo_tickets = [
        "Tiket Free Kendaraan Listrik - Mobil",
        "Tiket Free Kendaraan Listrik - Motor"
    ]

    # 1️⃣ Cari transaksi yang hanya berisi tiket promo
    df_txn_tickets = df_filtered.groupby("No Transaksi")["Ticket Detail"].unique().reset_index()
    df_txn_tickets["is_promo_only"] = df_txn_tickets["Ticket Detail"].apply(
        lambda tickets: set(tickets).issubset(set(promo_tickets))
    )

    # 2️⃣ Ambil transaksi valid (bukan promo-only)
    valid_txn = df_txn_tickets[df_txn_tickets["is_promo_only"] == False]["No Transaksi"]
    df_filtered = df_filtered[df_filtered["No Transaksi"].isin(valid_txn)]

    # 3️⃣ Balikin ke level transaksi (1 row per transaksi)
    df_txn = df_filtered.groupby(["No Transaksi", "Attendee Email", "Attendee Phone"]) \
               .agg({"Total Payment Transaction": "sum"}) \
               .reset_index()

    # 4️⃣ Hitung transaksi per customer
    buyer_counts = df_txn.groupby("Attendee Email")["No Transaksi"].nunique().reset_index()
    buyer_counts.columns = ["Attendee Email", "Transaction Count"]

    # 5️⃣ Segmentasi
    repeat_buyers = buyer_counts[buyer_counts["Transaction Count"] > 1].shape[0]
    one_time_buyers = buyer_counts[buyer_counts["Transaction Count"] == 1].shape[0]
    unique_buyers = buyer_counts.shape[0]

    st.subheader("👥 Customer Segmentation")

    col1, col2, col3 = st.columns(3)
    with col1: custom_metric("👤 Unique Buyers", f"{unique_buyers:,}")
    with col2: custom_metric("🆕 One-Time Buyers", f"{one_time_buyers:,}")
    with col3: custom_metric("🔁 Repeat Buyers", f"{repeat_buyers:,}")

    # 6️⃣ Layout pie chart + tabel dalam satu row
    col_left, col_right = st.columns([1, 2])  

    with col_left:
        buyer_segments = pd.DataFrame({
            "Segment": ["One-Time Buyers", "Repeat Buyers"],
            "Count": [one_time_buyers, repeat_buyers]
        })
        pie = (
            alt.Chart(buyer_segments)
            .mark_arc()
            .encode(
                theta="Count:Q", color="Segment:N", tooltip=["Segment", "Count"]
            )  
        )
        st.markdown("###### **Distribusi Repeat Buyers**")
        st.altair_chart(pie, use_container_width=True)

    with col_right:
        repeat_table = (
            buyer_counts[buyer_counts["Transaction Count"] > 1] \
            .sort_values("Transaction Count", ascending=False) \
            .reset_index(drop=True)
        )
        st.markdown("###### **Daftar Repeat Buyers**")
        st.dataframe(repeat_table, use_container_width=True)
