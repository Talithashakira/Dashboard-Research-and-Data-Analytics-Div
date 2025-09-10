import pandas as pd

def clean_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Clean empty rows from dataframe"""
    df = df.dropna(how="any")
    df = df[~df.apply(lambda row: row.astype(str).str.strip().eq("").any(), axis=1)]
    return df

def drop_unused_columns(df: pd.DataFrame, cols_to_drop: list) -> pd.DataFrame:
    return df.drop(columns=cols_to_drop, errors="ignore")

def convert_to_datetime(
    df: pd.DataFrame, 
    date_cols: list,
    dayfirst: bool = False,
    utc: bool = False
) -> pd.DataFrame:
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=dayfirst, utc=utc)
    return df

def split_multi_items(df: pd.DataFrame, multi_item_cols: list) -> pd.DataFrame:
    for col in multi_item_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.split(";")
    return df

def strip_and_explode(df: pd.DataFrame, multi_item_cols: list) -> pd.DataFrame:
    df = df.explode(multi_item_cols)
    for col in multi_item_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    return df
