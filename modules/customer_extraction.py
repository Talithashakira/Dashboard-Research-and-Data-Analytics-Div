import re
import pandas as pd

# --- Validasi nomor ponsel Indonesia ---
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

# --- Validasi & normalisasi email ---
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

# --- Daftar unit yang diproses & mapping nama unit dari data produksi ---
UNITS = [
    "Ancol",
    "Dufan Ancol",
    "Atlantis Ancol",
    "Sea World Ancol",
    "Samudra Ancol",
    "Jakarta Bird Land Ancol",
]

# Jika di data produksi namanya beda, mapping-kan ke salah satu UNITS di atas
UNIT_MAP = {
    # contoh:
    "Dunia Fantasi": "Dufan Ancol",
    "SeaWorld Ancol": "Sea World Ancol",
    "Birdland": "Jakarta Bird Land Ancol",
    # tambahkan sesuai kebutuhan
}

# --- Ticket promosi yang tidak ingin diikutkan ---
promo_tickets = [
    "Tiket Free Kendaraan Listrik - Mobil",
    "Tiket Free Kendaraan Listrik - Motor",
]

def extract_unique_customers(
    df: pd.DataFrame,
    unit_col: str = "Ticket Group",
    ticket_col: str = "Ticket Detail",
    visit_col: str = "Tgl Kunjungan",
    visit_fmt: str = "%d/%m/%Y",
):
    """
    Menghasilkan dict {unit: DataFrame[Attendee Name, Attendee Email, Attendee Phone, Tgl Kunjungan (Semua)]}
    - Membersihkan email & phone
    - Mengabaikan ticket promosi
    - Menggabungkan tanggal kunjungan (unik & urut) per (email, phone)
    """

    df = df.copy()

    # Normalisasi nama unit jika perlu
    if unit_col in df.columns:
        df[unit_col] = df[unit_col].replace(UNIT_MAP)

    # Bersihkan kontak
    if "Attendee Email" in df.columns:
        df["Attendee Email"] = df["Attendee Email"].apply(clean_email)
    if "Attendee Phone" in df.columns:
        df["Attendee Phone"] = df["Attendee Phone"].apply(clean_phone)

    # Pastikan kolom tanggal
    if visit_col in df.columns and not pd.api.types.is_datetime64_any_dtype(df[visit_col]):
        df[visit_col] = pd.to_datetime(df[visit_col], errors="coerce")

    def _join_dates(s: pd.Series, fmt: str) -> str:
        dates = pd.to_datetime(s, errors="coerce").dropna().dt.date
        if len(dates) == 0:
            return ""
        dates = sorted(set(dates))
        return ";".join(d.strftime(fmt) for d in dates)

    results = {}
    if unit_col not in df.columns:
        return results  # tidak ada kolom unit

    unique_units = set(df[unit_col].dropna().unique().tolist())
    for unit in UNITS:
        if unit not in unique_units:
            continue

        # Filter baris untuk unit ini & bukan tiket promosi
        sub = df[
            (df[unit_col] == unit) &
            (~df[ticket_col].isin(promo_tickets))
        ][["Attendee Name", "Attendee Email", "Attendee Phone", visit_col]].copy()

        # Buang baris tanpa kedua kontak (lebih longgar: minimal salah satu ada → gunakan how="all")
        sub = sub.dropna(subset=["Attendee Email", "Attendee Phone"], how="all")

        if sub.empty:
            results[unit] = sub
            continue

        # Group: gabungkan tanggal kunjungan, ambil nama terakhir
        grouped = (
            sub.sort_values(visit_col)
               .groupby(["Attendee Email", "Attendee Phone"], as_index=False, dropna=False)
               .agg({
                   "Attendee Name": "last",
                   visit_col: lambda s: _join_dates(s, visit_fmt),
               })
        )

        grouped = grouped.rename(columns={visit_col: "Tgl Kunjungan (Semua)"})
        grouped = grouped[["Attendee Name", "Attendee Email", "Attendee Phone", "Tgl Kunjungan (Semua)"]]

        results[unit] = grouped.reset_index(drop=True)

    return results
