from pathlib import Path
from datetime import date, timedelta
import pandas as pd

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "inventory.csv"
REQUIRED_COLUMNS = ["product_id", "product_name", "category", "quantity", "min_stock",
                    "expiry_date", "supplier", "unit_price"]

def seed_inventory():
    today = date.today()
    rows = [
        ["P001", "Fresh Milk", "Dairy", 18, 10, (today + timedelta(days=1)).isoformat(), "Mountain Dairy", 2.50],
        ["P002", "Brown Bread", "Bakery", 4, 8, (today + timedelta(days=3)).isoformat(), "Daily Bakery", 1.80],
        ["P003", "Apple Juice", "Beverages", 25, 10, (today + timedelta(days=20)).isoformat(), "Druk Drinks", 3.00],
        ["P004", "Cooking Oil", "Grocery", 3, 10, (today + timedelta(days=120)).isoformat(), "Bhutan Foods", 8.50],
        ["P005", "Rice 5kg", "Grocery", 30, 10, (today + timedelta(days=240)).isoformat(), "Farm Supply", 12.00],
        ["P006", "Yoghurt", "Dairy", 0, 6, (today - timedelta(days=2)).isoformat(), "Mountain Dairy", 1.50],
        ["P007", "Biscuits", "Snacks", 40, 12, (today + timedelta(days=90)).isoformat(), "Happy Snacks", 2.00],
        ["P008", "Orange Juice", "Beverages", 6, 8, (today + timedelta(days=5)).isoformat(), "Druk Drinks", 3.50],
    ]
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=REQUIRED_COLUMNS).to_csv(DATA_FILE, index=False)

def load_inventory():
    if not DATA_FILE.exists():
        seed_inventory()
    try:
        df = pd.read_csv(DATA_FILE)
        for col in REQUIRED_COLUMNS:
            if col not in df.columns:
                df[col] = None
        df = df[REQUIRED_COLUMNS].copy()
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
        df["min_stock"] = pd.to_numeric(df["min_stock"], errors="coerce").fillna(0).astype(int)
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)
        df["expiry_date"] = pd.to_datetime(df["expiry_date"], errors="coerce").dt.strftime("%Y-%m-%d")
        return df
    except Exception:
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

def save_inventory(df):
    clean = df.copy()
    for col in REQUIRED_COLUMNS:
        if col not in clean.columns:
            clean[col] = None
    clean[REQUIRED_COLUMNS].to_csv(DATA_FILE, index=False)
