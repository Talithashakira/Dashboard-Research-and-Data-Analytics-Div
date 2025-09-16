import pandas as pd
import re
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


_VALID_PREFIXES = (
    "811","812","813","821","822","823","851","852","853","814","815","816",
    "855","856","857","858","895","896","897","898","899","817","818","819",
    "859","877","878","879","831","832","833","838","881","882","883",
    "884","885","886","887","888","889"
)
_MOBILE_RE = re.compile(r"^628[1-9]\d{6,11}$")

def clean_phone(phone):
    if pd.isna(phone):
        return None
    s = str(phone).strip()
    s = re.sub(r"[^\d+]", "", s)
    if s.startswith("+62"): s = "62" + s[3:]
    elif s.startswith("620"): s = "62" + s[3:]
    elif s.startswith("62+"): s = "62" + s[3:]
    elif s.startswith("0062"): s = "62" + s[4:]
    elif s.startswith("0"): s = "62" + s[1:]
    elif s.startswith("68"): s = "62" + s[1:]
    elif s.startswith("608"): s = "62" + s[2:]
    elif s.startswith("6262"): s = "62" + s[4:]
    elif s.startswith("6228"): s = "62" + s[3:]
    elif s.startswith("8"): s = "62" + s
    if not s.startswith("62"):
        return None
    if _MOBILE_RE.fullmatch(s):
        prefix = s[2:5]
        if prefix in _VALID_PREFIXES:
            return s
    return None

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
_COMMON_DOMAINS = {
    "gamil.com": "gmail.com",
    "gmil.com": "gmail.com",
    "gnail.com": "gmail.com",
    "yaho.com": "yahoo.com",
    "yhoo.com": "yahoo.com",
    "hotnail.com": "hotmail.com",
    "outlok.com": "outlook.com",
}

def clean_email(email):
    if pd.isna(email):
        return None
    s = str(email).strip().lower()
    s = re.sub(r"\s+", "", s)
    if "@" not in s:
        return None
    try:
        username, domain = s.split("@", 1)
    except ValueError:
        return None
    if domain in _COMMON_DOMAINS:
        domain = _COMMON_DOMAINS[domain]
    s = f"{username}@{domain}"
    if _EMAIL_RE.fullmatch(s):
        return s
    return None

UNITS = [
    "Ancol",
    "Dufan Ancol",
    "Atlantis Ancol",
    "Sea World Ancol",
    "Samudra Ancol",
    "Jakarta Bird Land Ancol",
]

promo_tickets = [
    "Tiket Free Kendaraan Listrik - Mobil",
    "Tiket Free Kendaraan Listrik - Motor",
]

def get_unique_customers(df, unit_col="Ticket Group", ticket_col="Ticket Detail"):
    df = df.copy()

    # Bersihkan email & phone
    df["Attendee Email"] = df["Attendee Email"].apply(clean_email)
    df["Attendee Phone"] = df["Attendee Phone"].apply(clean_phone)

    results = {}
    for unit in UNITS:
        if unit in df[unit_col].unique():
            temp = (
                df[
                    (df[unit_col] == unit)
                    & (~df[ticket_col].isin(promo_tickets))
                ]
                [["Attendee Name", "Attendee Email", "Attendee Phone"]]
                .dropna(subset=["Attendee Email", "Attendee Phone"])
                .drop_duplicates(subset=["Attendee Email", "Attendee Phone"])
                .reset_index(drop=True)
            )
            results[unit] = temp
    return results



