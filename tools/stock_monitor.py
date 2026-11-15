import pandas as pd

def check_stock(inventory):
    """Find products at or below their configured minimum stock level."""
    if inventory.empty:
        return pd.DataFrame(columns=list(inventory.columns) + ["stock_status", "suggested_reorder"])
    df = inventory.copy()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
    df["min_stock"] = pd.to_numeric(df["min_stock"], errors="coerce").fillna(0)
    df = df[df["quantity"] <= df["min_stock"]].copy()
    df["stock_status"] = df["quantity"].apply(lambda q: "Out of stock" if q <= 0 else "Low stock")
    df["suggested_reorder"] = (df["min_stock"] * 2 - df["quantity"]).clip(lower=0).astype(int)
    return df.sort_values(["quantity", "product_name"])
