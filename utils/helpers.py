def format_rupiah(x: float) -> str:
    if x >= 1_000_000_000:
        return f"Rp {x/1_000_000_000:.1f}M"
    elif x >= 1_000_000:
        return f"Rp {x/1_000_000:.1f}jt"
    else:
        return f"Rp {x:,.0f}"
