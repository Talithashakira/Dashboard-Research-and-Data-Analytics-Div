import pandas as pd

def drop_unused_columns(df: pd.DataFrame, cols_to_drop: list) -> pd.DataFrame:
    return df.drop(columns=cols_to_drop, errors="ignore")

def convert_to_datetime(df: pd.DataFrame, date_cols: list) -> pd.DataFrame:
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
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
