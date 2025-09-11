import pandas as pd
from utils.data_loading import load_csv
from utils.data_cleaning import convert_to_datetime
from utils.preprocessing import convert_numeric

def load_and_clean_data(file: str) -> pd.DataFrame:

    # 1. Load
    df = load_csv(file)

    # 2. Pilih kolom yang perlu digunakan
    cols_to_use = [
        "Group_Secara keseluruhan, seberapa puaskah Anda terhadap pengalaman berekreasi di Dunia Fantasi Ancol?",
        "Numeric_Secara keseluruhan, seberapa puaskah Anda terhadap pengalaman berekreasi di Dunia Fantasi Ancol?",
        "What is the primary reason for your score?",
        "Tags_What is the primary reason for your score?",
        "Sentiment_What is the primary reason for your score?",
        "Numeric_Dari Pengalaman Anda, apakah anda akan mempertimbangkan untuk datang kembali ke Dunia Fantasi Ancol?",
        "Sync On-DateTime",
        "Name",
        "Email",
        "Phone Number",
        "Campaign Id",
        "Camp Sent On Date Time",
    ]
    df = df[cols_to_use]

    # 3. Rename kolom
    df = df.rename(columns={
        "Group_Secara keseluruhan, seberapa puaskah Anda terhadap pengalaman berekreasi di Dunia Fantasi Ancol?": "CSI",
        "Numeric_Secara keseluruhan, seberapa puaskah Anda terhadap pengalaman berekreasi di Dunia Fantasi Ancol?": "Numeric_CSI",
        "What is the primary reason for your score?": "Primary Reason",
        "Tags_What is the primary reason for your score?": "Tags_Primary Reason",
        "Sentiment_What is the primary reason for your score?": "Sentiment_Primary Reason",
        "Numeric_Dari Pengalaman Anda, apakah anda akan mempertimbangkan untuk datang kembali ke Dunia Fantasi Ancol?": "Numeric_Will Return",
    })

    # 4. Convert to datetime
    df = convert_to_datetime(df, ["Sync On-DateTime"], dayfirst=True)
    df = convert_to_datetime(df, ["Camp Sent On Date Time"], utc=True)

    df = convert_numeric(df, ["Numeric_Will Return"])
    
    return df


