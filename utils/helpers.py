def format_rupiah(x: float) -> str:
    if x >= 1_000_000_000:
        return f"Rp {x/1_000_000_000:.1f}M"
    elif x >= 1_000_000:
        return f"Rp {x/1_000_000:.1f}jt"
    else:
        return f"Rp {x:,.0f}"

def get_tags_counts(df, sentiment):
    df_sentiment = df[df["Sentiment_Primary Reason"] == sentiment]

    all_tags = (
        df_sentiment["Tags_Primary Reason"]
        .dropna()
        .str.split("|")
        .explode()
        .str.strip()
    )

    tag_counts = all_tags.value_counts().reset_index()
    tag_counts.columns = ["Tag", "Count"]

    return tag_counts
