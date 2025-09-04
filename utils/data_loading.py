import pandas as pd

def load_csv(file: str) -> pd.DataFrame:
    """Load data dari file CSV"""
    return pd.read_csv(file)
