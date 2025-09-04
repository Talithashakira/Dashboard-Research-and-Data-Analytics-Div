import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
import altair as alt


def show_summary_cards(df):
    col1, col2, col3 = st.columns(3)

    # 🎟️ Total Ticket Purchased
    with col1:
        total_tickets = df["Ticket Purchased"].sum()
        st.metric("🎟️ Total Ticket Purchased", f"{total_tickets:,}")

    # 💰 Total Payment
    with col2:
        total_payment = df["Total Payment"].sum()
        st.metric("💰 Total Payment", f"Rp {total_payment:,.0f}")

    # 📈 Daily Growth (%)
    with col3:
        # Pastikan kolom tanggal dalam datetime
        df["Tgl Transaksi"] = pd.to_datetime(df["Tgl Transaksi"])

        # Agregasi per hari
        daily_sales = df.groupby("Tgl Transaksi")["Ticket Purchased"].sum().sort_index()

        # Hitung pertumbuhan harian (%)
        daily_growth = daily_sales.pct_change() * 100

        # Ambil rata-rata growth (drop NaN hari pertama)
        avg_growth = daily_growth.dropna().mean()

        # Kalau tidak ada data growth
        if pd.isna(avg_growth):
            avg_growth = 0

        st.metric("📈 Rata-rata Daily Growth", f"{avg_growth:.2f} %")


# =====================
# Trend Charts
# =====================
def show_trend_payment(df_filtered):
    """Trend berdasarkan Total Payment per Unit"""

    # Mapping warna unit
    unit_colors = {
        "Ancol": "#0033A0",
        "Dufan Ancol": "#E0004D",
        "Atlantis Ancol": "#5C068C",
        "Sea World Ancol": "#006EB3",
        "Samudra Ancol": "#00A497",
        "Jakarta Bird Land Ancol": "#F68D2E"
    }

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

    # Mapping warna unit
    unit_colors = {
        "Ancol": "#0033A0",
        "Dufan Ancol": "#E0004D",
        "Atlantis Ancol": "#5C068C",
        "Sea World Ancol": "#006EB3",
        "Samudra Ancol": "#00A497",
        "Jakarta Bird Land Ancol": "#F68D2E"
    }

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

    # Fungsi format Rupiah ke jt/M
    def format_rupiah(x):
        if x >= 1_000_000_000:
            return f"Rp {x/1_000_000_000:.1f}M"
        elif x >= 1_000_000:
            return f"Rp {x/1_000_000:.1f}jt"
        else:
            return f"Rp {x:,.0f}"

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
        dx=3  # jarak sedikit dari ujung bar
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

def show_total_payment_per_unit(df_filtered: pd.DataFrame):
    """
    Menampilkan custom scorecard Total Payment per Unit (Ticket Group)
    dengan warna background (50), border (500), dan rounded.
    """
    if "Ticket Group" not in df_filtered.columns or "Total Payment" not in df_filtered.columns:
        st.warning("Kolom 'Ticket Group' atau 'Total Payment' tidak ditemukan di dataframe.")
        return

    # Mapping warna per unit
    unit_colors = {
        "Ancol": {"fill": "#C9DAFF", "border": "#0033A0"},
        "Dufan": {"fill": "#FCE5ED", "border": "#E0004D"},
        "Sea World": {"fill": "#C6E4F7", "border": "#006EB3"},
        "Atlantis": {"fill": "#D8ACF1", "border": "#5C068C"},
        "Samudra Ancol": {"fill": "#B8F6F1", "border": "#00A497"},
        "Jakarta Birdland": {"fill": "#FEF4EA", "border": "#F68D2E"},
    }

    # Hitung total payment per unit
    total_payment_unit = (
        df_filtered.groupby("Ticket Group")["Total Payment"]
        .sum()
        .reset_index()
    )

    # Format Rupiah singkat
    def format_rupiah(x):
        if x >= 1_000_000_000:
            return f"Rp {x/1_000_000_000:.1f}M"
        elif x >= 1_000_000:
            return f"Rp {x/1_000_000:.1f}jt"
        else:
            return f"Rp {x:,.0f}"

    total_payment_unit["Total Payment Formatted"] = total_payment_unit["Total Payment"].apply(format_rupiah)

    # Bikin kolom horizontal
    n_cols = len(total_payment_unit)
    cols = st.columns(n_cols)

    # Render custom card pakai HTML
    for i, row in total_payment_unit.iterrows():
        unit = row["Ticket Group"]
        value = row["Total Payment Formatted"]
        colors = unit_colors.get(unit, {"fill": "#f0f0f0", "border": "#333"})

        card_html = f"""
        <style>
            .custom-card-container {{
                background-color: var(--fill-color);
                border: 2px solid var(--border-color);
                border-radius: 16px;
                padding: 16px;
                text-align: center;
                font-family: Arial, sans-serif;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: transform 0.2s;
            }}
            .custom-card-container:hover {{
                transform: translateY(-5px);
            }}
            .custom-card-container h4 {{
                margin: 0;
                color: var(--border-color);
            }}
            .custom-card-container p {{
                margin: 8px 0 0;
                font-size: 20px;
                font-weight: bold;
                color: var(--border-color);
            }}
        </style>
        <div class="custom-card-container" style="
            --fill-color: {colors['fill']};
            --border-color: {colors['border']};
            ">
            <h4>{unit}</h4>
            <p>{value}</p>
        </div>
        """
        cols[i].markdown(card_html, unsafe_allow_html=True)