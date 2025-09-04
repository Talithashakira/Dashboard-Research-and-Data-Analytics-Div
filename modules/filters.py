def filter_by_unit(df, unit_name):
    """Filter dataframe berdasarkan unit (Ticket Group)"""
    return df[df["Ticket Group"].str.contains(unit_name, case=False, na=False)]
