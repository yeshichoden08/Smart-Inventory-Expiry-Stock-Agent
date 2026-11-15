from tools.expiry_checker import check_expiry
from tools.stock_monitor import check_stock
from tools.recommendation import make_recommendations
from tools.report_generator import make_inventory_report
from memory_manager import save_interaction
from ollama_explainer import explain_with_ollama

def detect_intent(prompt: str) -> str:
    p = prompt.lower()
    if any(word in p for word in ["restock", "reorder", "recommend", "recommendation", "what should i buy"]):
        return "recommendations"
    if any(word in p for word in ["low stock", "out of stock", "stock level", "stock shortage", "stock monitoring"]):
        return "stock"
    if any(word in p for word in ["expir", "expired", "expiry", "near expiry"]):
        return "expiry"
    if any(word in p for word in ["report", "summary", "overview", "all products", "show inventory", "total stock"]):
        return "report"
    return "general"

def run_agent(prompt, inventory, use_ollama=False, ollama_model="qwen3:8b"):
    """Plan a task, select tools, execute them and store an episodic record."""
    intent = detect_intent(prompt)
    plan = ["Understand the user's inventory request", "Select the relevant inventory tool(s)",
            "Analyse the inventory records", "Prepare a result and save the interaction"]
    tools_used = []
    result_df = None

    if intent == "expiry":
        result_df = check_expiry(inventory)
        tools_used = ["Expiry Checking Tool"]
        if result_df.empty:
            response = "I checked the expiry dates. There are no expired or upcoming-expiry products in the selected checking window."
        else:
            urgent = int((result_df["expiry_status"] == "Urgent").sum())
            expired = int((result_df["expiry_status"] == "Expired").sum())
            response = f"I checked {len(inventory)} products and found {len(result_df)} products needing expiry attention: {expired} expired and {urgent} urgent (within 7 days). Review the table below and take action."
    elif intent == "stock":
        result_df = check_stock(inventory)
        tools_used = ["Stock Monitoring Tool"]
        if result_df.empty:
            response = "I checked the stock quantities. No products are currently below their minimum stock level."
        else:
            out = int((result_df["stock_status"] == "Out of stock").sum())
            response = f"I checked {len(inventory)} products and found {len(result_df)} stock issues, including {out} out-of-stock products. Review the suggested action for each item."
    elif intent == "recommendations":
        result_df = make_recommendations(inventory)
        tools_used = ["Expiry Checking Tool", "Stock Monitoring Tool", "Recommendation Tool"]
        response = "I checked expiry dates and stock levels, then prepared recommendations. Expired items should be separated from sale, near-expiry items should be prioritised, and low-stock items should be reviewed for restocking."
        if result_df.empty:
            response = "No urgent inventory actions are required based on the current records."
    elif intent == "report":
        result_df = make_inventory_report(inventory)
        tools_used = ["Inventory Retrieval Tool", "Report Generation Tool"]
        response = f"Inventory summary: {len(inventory)} products and {int(inventory['quantity'].sum()) if not inventory.empty else 0} total units. The table shows each product's current stock and expiry status."
    else:
        result_df = make_inventory_report(inventory)
        tools_used = ["Inventory Retrieval Tool", "Report Generation Tool"]
        response = ("I can help check expiry dates, find low-stock products, recommend restocking or generate an inventory report. "
                    "I interpreted your request as a general inventory overview. Try: 'Which products have low stock?'")

    if use_ollama:
        explanation = explain_with_ollama(prompt, response, result_df, ollama_model)
        if explanation:
            response = explanation

    save_interaction(prompt, intent, tools_used, response)
    return {
        "intent": intent,
        "plan": plan,
        "tools_used": tools_used,
        "data": result_df,
        "response": response,
        "status": "Completed"
    }
