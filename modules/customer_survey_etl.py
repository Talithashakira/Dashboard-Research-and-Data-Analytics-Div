import re
import pandas as pd
from utils.data_loading import load_csv
from utils.data_cleaning import convert_to_datetime
from utils.preprocessing import convert_numeric
from utils.helpers import map_columns

QUESTION_MAP = {
    r"Group_Secara keseluruhan.*puaskah Anda terhadap pengalaman.*": "CSI",
    r"Numeric_Secara keseluruhan.*puaskah Anda terhadap pengalaman.*": "Numeric_CSI",
    r"Numeric_Dari Pengalaman Anda.*datang kembali.*": "Numeric_Will Return",
}

def load_and_clean_data(file: str) -> pd.DataFrame:

    df = load_csv(file)

    df = map_columns(df, QUESTION_MAP)

    cols_to_use = [
        "CSI",
        "Numeric_CSI",
        "What is the primary reason for your score?",
        "Tags_What is the primary reason for your score?",
        "Sentiment_What is the primary reason for your score?",
        "Numeric_Will Return",
        "Sync On-DateTime",
        "Camp Sent On Date Time",
        "Name",
        "Email",
        "Phone Number",
        "Campaign Id",

    ]

    df = df.rename(columns={
        "What is the primary reason for your score?": "Primary Reason",
        "Tags_What is the primary reason for your score?": "Tags_Primary Reason",
        "Sentiment_What is the primary reason for your score?": "Sentiment_Primary Reason",
    })

    df = convert_to_datetime(df, ["Sync On-DateTime"], dayfirst=True)
    df = convert_to_datetime(df, ["Camp Sent On Date Time"], utc=True)

    df = convert_numeric(df, ["Numeric_Will Return"])

    return df