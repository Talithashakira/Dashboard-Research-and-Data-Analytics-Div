import pandas as pd

def convert_numeric(df: pd.DataFrame, numeric_cols: list) -> pd.DataFrame:
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def convert_to_nullable_int(df: pd.DataFrame, int_cols: list) -> pd.DataFrame:
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    return df