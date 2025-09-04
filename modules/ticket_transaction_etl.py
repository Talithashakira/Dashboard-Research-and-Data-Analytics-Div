import pandas as pd
from utils.data_loading import load_csv
from utils.preprocessing import convert_numeric
from utils.data_cleaning import (
    clean_empty_rows, 
    drop_unused_columns, 
    convert_to_datetime, 
    split_multi_items, 
    strip_and_explode
)

def load_and_clean_data(file: str) -> pd.DataFrame:
    # 1. Load
    df = load_csv(file)

    # 2. Drop kolom tidak perlu
    cols_to_drop = [
        "Settlement Paid Timestamp",
        "Payment Type",
        "Ticket Type",
        "Kode Voucher",
        "Voucher Amount",
        "Biaya",
        "Total Paid",
    ]
    df = drop_unused_columns(df, cols_to_drop)

    # 3. Convert ke datetime
    df = convert_to_datetime(df, ["Tgl Transaksi", "Tgl Kunjungan"])

    # 4. Hitung total per transaksi (sebelum explode)
    if "Ticket Purchased" in df.columns and "Ticket Price" in df.columns:
        df["Total Payment Transaction"] = df.apply(
            lambda x: sum(
                pd.to_numeric(i, errors="coerce") * pd.to_numeric(p, errors="coerce")
                for i, p in zip(str(x["Ticket Purchased"]).split(";"),
                                str(x["Ticket Price"]).split(";"))
            ),
            axis=1,
        )
        df["Total Ticket Purchased Transaction"] = df["Ticket Purchased"].apply(
            lambda x: sum(pd.to_numeric(i, errors="coerce") for i in str(x).split(";"))
        )

    # 5. Split multi-item kolom
    multi_item_cols = ["Ticket Group", "Ticket Purchased", "Ticket Detail", "Ticket Price"]
    df = split_multi_items(df, multi_item_cols)

    # 6. Bersihkan dan explode
    df = clean_empty_rows(df)
    df = strip_and_explode(df, multi_item_cols)

    # 7. Konversi numerik
    df = convert_numeric(df, ["Ticket Purchased", "Ticket Price"])

    # 8. Hitung ulang total per item (setelah explode)
    if "Ticket Purchased" in df.columns and "Ticket Price" in df.columns:
        df["Total Payment"] = df["Ticket Purchased"] * df["Ticket Price"]
        df["Total Ticket Purchase"] = df["Ticket Purchased"]

    return df
