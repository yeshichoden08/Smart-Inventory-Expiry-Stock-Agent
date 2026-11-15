from datetime import date, timedelta
import pandas as pd

def check_expiry(inventory, today=None, days_ahead=30):
    """Return expired and upcoming-expiry products, with a clear status."""
    if inventory.empty:
        return pd.DataFrame(columns=list(inventory.columns) + ["days_remaining", "expiry_status"])
    today = today or date.today()
    df = inventory.copy()
    df["expiry_date_parsed"] = pd.to_datetime(df["expiry_date"], errors="coerce").dt.date
    df["days_remaining"] = df["expiry_date_parsed"].apply(
        lambda d: (d - today).days if pd.notna(d) else None
    )
    df = df[df["expiry_date_parsed"].notna()].copy()
    df = df[(df["days_remaining"] < 0) | (df["days_remaining"] <= days_ahead)].copy()
    def status(days):
        if days < 0: return "Expired"
        if days <= 7: return "Urgent"
        return "Upcoming"
    df["expiry_status"] = df["days_remaining"].apply(status)
    return df.drop(columns=["expiry_date_parsed"]).sort_values("days_remaining")
