import pandas as pd
from tools.expiry_checker import check_expiry
from tools.stock_monitor import check_stock

def make_recommendations(inventory):
    if inventory.empty:
        return pd.DataFrame(columns=["product_name", "issue", "recommendation", "priority"])
    rows = []
    expiry = check_expiry(inventory)
    stock = check_stock(inventory)
    for _, r in expiry.iterrows():
        if r["expiry_status"] == "Expired":
            action, priority = "Separate from sale and follow the business disposal policy.", "High"
        elif r["expiry_status"] == "Urgent":
            action, priority = "Prioritise sale or use; check product condition and applicable policy.", "High"
        else:
            action, priority = "Monitor the date and plan stock rotation (first-expiring, first-out).", "Medium"
        rows.append({"product_name": r["product_name"], "issue": f"{r['expiry_status']} ({r['days_remaining']} days)",
                     "recommendation": action, "priority": priority})
    for _, r in stock.iterrows():
        action = ("Check supplier availability and prepare a replenishment request."
                  if r["quantity"] > 0 else "Check supplier availability; confirm demand before replenishing.")
        rows.append({"product_name": r["product_name"], "issue": r["stock_status"],
                     "recommendation": action, "priority": "High"})
    return pd.DataFrame(rows, columns=["product_name", "issue", "recommendation", "priority"])
