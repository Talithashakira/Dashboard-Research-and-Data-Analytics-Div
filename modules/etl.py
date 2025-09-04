import pandas as pd
from modules.data_cleaning import clean_empty_rows

def load_and_clean_data(file: str) -> pd.DataFrame:
    df = pd.read_csv(file)

    cols_to_drop = [
        "Settlement Paid Timestamp",
        "Payment Type",
        "Ticket Type",
        "Kode Voucher",
        "Voucher Amount",
        "Biaya",
        "Total Paid",
    ]

    df = df.drop(columns=cols_to_drop, errors="ignore")

    # Konversi tanggal
    for col in ["Tgl Transaksi", "Tgl Kunjungan"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")


    # Hitung total per transaksi
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

    # Multi-item split
    multi_item_cols = ["Ticket Group", "Ticket Purchased", "Ticket Detail", "Ticket Price"]
    for col in multi_item_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.split(";")
    
    # Cleaning tambahan
    df = clean_empty_rows(df)
    df = df.explode(multi_item_cols)

    for col in multi_item_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Konversi numerik
    numeric_cols = ["Ticket Purchased", "Ticket Price"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Hitung ulang total per item
    if "Ticket Purchased" in df.columns and "Ticket Price" in df.columns:
        df["Total Payment"] = df["Ticket Purchased"] * df["Ticket Price"]
        df["Total Ticket Purchase"] = df["Ticket Purchased"]
    
    return df