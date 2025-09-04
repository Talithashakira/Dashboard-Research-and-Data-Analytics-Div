def convert_numeric(df: pd.DataFrame, numeric_cols: list) -> pd.DataFrame:
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df