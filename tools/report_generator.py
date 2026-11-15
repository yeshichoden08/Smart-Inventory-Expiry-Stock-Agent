import pandas as pd
from tools.expiry_checker import check_expiry
from tools.stock_monitor import check_stock

def make_inventory_report(inventory):
    if inventory.empty:
        return pd.DataFrame(columns=["product_id", "product_name", "quantity", "min_stock", "expiry_date", "status"])
    df = inventory.copy()
    df["expiry_date_parsed"] = pd.to_datetime(df["expiry_date"], errors="coerce").dt.date
    from datetime import date
    today = date.today()
    def expiry_label(d):
        if pd.isna(d): return "Invalid date"
        if d < today: return "Expired"
        if (d - today).days <= 7: return "Expiring soon"
        return "Normal"
    df["expiry_status"] = df["expiry_date_parsed"].apply(expiry_label)
    df["stock_status"] = df.apply(
        lambda r: "Out of stock" if r["quantity"] <= 0 else
        ("Low stock" if r["quantity"] <= r["min_stock"] else "Normal"), axis=1
    )
    return df.drop(columns=["expiry_date_parsed"])
