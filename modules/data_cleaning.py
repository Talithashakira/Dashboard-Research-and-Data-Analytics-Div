import pandas as pd

def clean_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Clean empty rows from dataframe"""
    df = df.dropna(how="any")
    df = df[~df.apply(lambda row: row.astype(str).str.strip().eq("").any(), axis=1)]
    return df