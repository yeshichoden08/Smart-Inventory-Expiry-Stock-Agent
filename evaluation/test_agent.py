from datetime import date, timedelta
import pandas as pd

from tools.expiry_checker import check_expiry
from tools.stock_monitor import check_stock
from tools.recommendation import make_recommendations
from agent import detect_intent, run_agent

def sample():
    today = date.today()
    return pd.DataFrame([
        ["A", "Milk", "Dairy", 3, 5, (today + timedelta(days=1)).isoformat(), "Supplier", 2.0],
        ["B", "Rice", "Grocery", 20, 5, (today + timedelta(days=100)).isoformat(), "Supplier", 5.0],
        ["C", "Yoghurt", "Dairy", 0, 4, (today - timedelta(days=1)).isoformat(), "Supplier", 1.0],
    ], columns=["product_id", "product_name", "category", "quantity", "min_stock",
                "expiry_date", "supplier", "unit_price"])

def test_expiry_tool_finds_expired_and_urgent():
    result = check_expiry(sample())
    assert set(result["expiry_status"]) == {"Expired", "Urgent"}

def test_stock_tool_finds_low_and_out_of_stock():
    result = check_stock(sample())
    assert set(result["stock_status"]) == {"Low stock", "Out of stock"}

def test_intent_detection():
    assert detect_intent("show expired products") == "expiry"
    assert detect_intent("which products have low stock") == "stock"
    assert detect_intent("recommend what to restock") == "recommendations"

def test_recommendations_are_generated():
    result = make_recommendations(sample())
    assert not result.empty
    assert "recommendation" in result.columns

def test_agent_runs_and_selects_tool():
    result = run_agent("show me low stock products", sample())
    assert result["status"] == "Completed"
    assert "Stock Monitoring Tool" in result["tools_used"]
