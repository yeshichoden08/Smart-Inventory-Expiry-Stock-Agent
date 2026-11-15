from pathlib import Path
import sys
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from agent import run_agent
from data_manager import load_inventory, save_inventory, seed_inventory, REQUIRED_COLUMNS
from memory_manager import load_memory, save_feedback, clear_memory

st.set_page_config(
    page_title="StockWise | Smart Inventory Agent",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Readable navy-blue / teal theme
st.markdown("""
<style>
    .stApp { background: #F4F7FB; color: #172B4D; }
    [data-testid="stSidebar"] { background: #10243A; }
    [data-testid="stSidebar"] * { color: #F4F7FB !important; }
    .main-title { color: #10243A; font-size: 2rem; font-weight: 800; margin-bottom: 0; }
    .sub-title { color: #60758B; margin-top: 0.2rem; }
    .metric-card {
        background: white; padding: 18px 20px; border-radius: 14px;
        border: 1px solid #E2EAF2; box-shadow: 0 2px 8px rgba(16,36,58,.04);
    }
    .metric-label { color: #60758B; font-size: .88rem; }
    .metric-value { color: #10243A; font-size: 1.8rem; font-weight: 800; }
    .result-card {
        background: white; border: 1px solid #DCE7F0; border-left: 5px solid #159A91;
        border-radius: 12px; padding: 18px; margin: 8px 0 16px 0;
    }
    .small-muted { color: #60758B; font-size: .85rem; }
    div.stButton > button[kind="primary"] { background: #087F8C; border-color: #087F8C; }
    div.stButton > button[kind="primary"]:hover { background: #066873; border-color: #066873; }
</style>
""", unsafe_allow_html=True)

if not (ROOT / "data" / "inventory.csv").exists():
    seed_inventory()

if "agent_result" not in st.session_state:
    st.session_state.agent_result = None
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

def metric_card(label, value, note=""):
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="small-muted">{note}</div></div>',
        unsafe_allow_html=True
    )

inventory = load_inventory()

with st.sidebar:
    st.markdown("## 📦 StockWise")
    st.caption("Smart Inventory Expiry & Stock Monitoring Agent")
    page = st.radio("NAVIGATION", ["Dashboard & Agent", "Inventory Management", "Agent Memory", "Evaluation"])
    st.divider()
    st.markdown("### Agent settings")
    use_ollama = st.checkbox("Use local Ollama explanation", value=False,
                             help="Optional. Requires Ollama running locally with qwen3:8b pulled.")
    ollama_model = st.text_input("Ollama model", value="qwen3:8b", disabled=not use_ollama)
    st.caption("Rule-based inventory tools always perform the calculations. Ollama only explains their verified results.")
    st.divider()
    st.caption("DAT404 | Custom AI Agent Project")

if page == "Dashboard & Agent":
    st.markdown('<p class="main-title">Smart Inventory Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Monitor stock levels, expiry dates and agent decisions in one place.</p>', unsafe_allow_html=True)

    if inventory.empty:
        st.warning("Your inventory is empty. Add products in Inventory Management.")
    else:
        exp_df = inventory.copy()
        exp_df["expiry_date"] = pd.to_datetime(exp_df["expiry_date"], errors="coerce").dt.date
        today = date.today()
        expired_n = int((exp_df["expiry_date"] < today).sum())
        expiring_n = int(((exp_df["expiry_date"] >= today) & (exp_df["expiry_date"] <= today + timedelta(days=7))).sum())
        low_n = int((inventory["quantity"] <= inventory["min_stock"]).sum())
        out_n = int((inventory["quantity"] <= 0).sum())
        total_units = int(inventory["quantity"].sum())

        cols = st.columns(5)
        with cols[0]: metric_card("Total products", len(inventory), "Unique inventory items")
        with cols[1]: metric_card("Total units", total_units, "Current quantity")
        with cols[2]: metric_card("Expired", expired_n, "Past expiry date")
        with cols[3]: metric_card("Expiring in 7 days", expiring_n, "Urgent attention")
        with cols[4]: metric_card("Low / out of stock", low_n, f"{out_n} out of stock")

    st.divider()
    st.markdown("### 🤖 Ask the inventory agent")
    st.write("Enter a request in everyday language. The agent will plan the task, choose tools, analyse your inventory and show the result.")
    examples = [
        "Check all products that are expiring soon",
        "Show me all expired products",
        "Which products have low stock?",
        "Recommend which products I should restock",
        "Generate an inventory summary report",
    ]
    selected_example = st.selectbox("Example prompts", ["Choose an example..."] + examples)
    with st.form("agent_prompt_form"):
        prompt = st.text_input("Your prompt", value="" if selected_example == "Choose an example..." else selected_example,
                               placeholder="e.g. Check which products are expiring in the next 7 days")
        submitted = st.form_submit_button("Run agent", type="primary", use_container_width=True)

    if submitted:
        if not prompt.strip():
            st.warning("Please enter a prompt.")
        else:
            with st.spinner("Agent is planning and checking your inventory..."):
                result = run_agent(prompt, inventory, use_ollama=use_ollama, ollama_model=ollama_model)
                st.session_state.agent_result = result
                st.session_state.last_prompt = prompt

    result = st.session_state.agent_result
    if result:
        st.markdown("### Agent result")
        st.markdown(f'<div class="result-card"><b>Agent response</b><br>{result["response"]}</div>', unsafe_allow_html=True)
        left, right = st.columns([1, 1])
        with left:
            st.markdown("**Plan followed**")
            for step in result["plan"]:
                st.write(f"✓ {step}")
        with right:
            st.markdown("**Tools executed**")
            for tool in result["tools_used"]:
                st.write(f"🛠️ {tool}")
        if result.get("data") is not None:
            st.markdown("**Data found**")
            if result["data"].empty:
                st.info("No matching products were found.")
            else:
                st.dataframe(result["data"], use_container_width=True, hide_index=True)
        st.caption(f"Task type: {result['intent']}  |  Status: {result['status']}")
        st.markdown("**Was this result helpful?**")
        f1, f2, f3 = st.columns([1, 1, 4])
        with f1:
            if st.button("👍 Yes", key="feedback_yes"):
                save_feedback(st.session_state.last_prompt, "helpful")
                st.success("Feedback saved to agent memory.")
        with f2:
            if st.button("👎 No", key="feedback_no"):
                save_feedback(st.session_state.last_prompt, "not helpful")
                st.success("Feedback saved to agent memory.")

    st.divider()
    st.markdown("### Inventory overview")
    if not inventory.empty:
        a, b = st.columns(2)
        with a:
            category_counts = inventory.groupby("category", dropna=False)["product_id"].count().reset_index(name="products")
            fig = px.bar(category_counts, x="category", y="products", title="Products by category",
                         color_discrete_sequence=["#159A91"])
            fig.update_layout(paper_bgcolor="white", plot_bgcolor="white", font_color="#172B4D")
            st.plotly_chart(fig, use_container_width=True)
        with b:
            status_df = pd.DataFrame({
                "Status": ["Expired", "Expiring within 7 days", "Other"],
                "Products": [expired_n, expiring_n, max(0, len(inventory)-expired_n-expiring_n)]
            })
            fig = px.pie(status_df, names="Status", values="Products", title="Expiry status distribution",
                         color_discrete_sequence=["#D95D5D", "#E9A23B", "#159A91"])
            fig.update_layout(paper_bgcolor="white", font_color="#172B4D")
            st.plotly_chart(fig, use_container_width=True)

elif page == "Inventory Management":
    st.markdown('<p class="main-title">Inventory Management</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Add products, review records or upload your own CSV dataset.</p>', unsafe_allow_html=True)

    with st.expander("➕ Add a new product", expanded=True):
        with st.form("add_product_form"):
            c1, c2, c3 = st.columns(3)
            product_name = c1.text_input("Product name")
            category = c2.text_input("Category", value="General")
            supplier = c3.text_input("Supplier", value="Not specified")
            c4, c5, c6 = st.columns(3)
            quantity = c4.number_input("Quantity", min_value=0, value=10, step=1)
            min_stock = c5.number_input("Minimum stock", min_value=0, value=5, step=1)
            unit_price = c6.number_input("Unit price", min_value=0.0, value=1.0, step=0.5)
            expiry = st.date_input("Expiry date", value=date.today() + timedelta(days=60))
            add = st.form_submit_button("Add product", type="primary")
            if add:
                if not product_name.strip():
                    st.error("Product name is required.")
                elif (inventory["product_name"].str.lower() == product_name.strip().lower()).any():
                    st.error("A product with this name already exists. Use a different name.")
                else:
                    new_row = pd.DataFrame([{
                        "product_id": f"P{int(pd.Timestamp.now().timestamp())}",
                        "product_name": product_name.strip(),
                        "category": category.strip() or "General",
                        "quantity": int(quantity),
                        "min_stock": int(min_stock),
                        "expiry_date": expiry.isoformat(),
                        "supplier": supplier.strip() or "Not specified",
                        "unit_price": float(unit_price),
                    }])
                    save_inventory(pd.concat([inventory, new_row], ignore_index=True))
                    st.success("Product added successfully.")
                    st.rerun()

    st.markdown("### Current inventory")
    st.dataframe(inventory, use_container_width=True, hide_index=True)
    uploaded = st.file_uploader("Upload inventory CSV", type=["csv"])
    if uploaded is not None:
        try:
            incoming = pd.read_csv(uploaded)
            missing = [c for c in REQUIRED_COLUMNS if c not in incoming.columns]
            if missing:
                st.error("Missing required columns: " + ", ".join(missing))
            else:
                st.dataframe(incoming.head(), use_container_width=True)
                if st.button("Replace inventory with uploaded CSV", type="primary"):
                    save_inventory(incoming[REQUIRED_COLUMNS])
                    st.success("Inventory replaced successfully.")
                    st.rerun()
        except Exception as exc:
            st.error(f"Could not read CSV: {exc}")

elif page == "Agent Memory":
    st.markdown('<p class="main-title">Agent Memory & Feedback</p>', unsafe_allow_html=True)
    st.write("The agent stores previous prompts and user feedback as a simple episodic memory.")
    memory = load_memory()
    if memory:
        st.dataframe(pd.DataFrame(memory).iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.info("No memory records yet. Run a prompt and submit feedback.")
    if st.button("Clear agent memory"):
        clear_memory()
        st.success("Agent memory cleared.")
        st.rerun()

elif page == "Evaluation":
    st.markdown('<p class="main-title">Agent Evaluation</p>', unsafe_allow_html=True)
    st.write("Run the included test suite from the VS Code terminal to verify the agent tools.")
    st.code("py -m pytest evaluation/test_agent.py -v", language="powershell")
    test_cases = pd.DataFrame([
        ["TC01", "Product expires tomorrow", "Urgent expiry alert"],
        ["TC02", "Product expired yesterday", "Expired-product alert"],
        ["TC03", "Product expires in 20 days", "Upcoming expiry alert"],
        ["TC04", "Quantity below minimum stock", "Restock recommendation"],
        ["TC05", "Quantity above minimum stock", "Normal stock status"],
        ["TC06", "Quantity is zero", "Out-of-stock alert"],
        ["TC07", "Empty inventory", "Safe empty result"],
        ["TC08", "Invalid expiry date", "Validation / invalid-date handling"],
    ], columns=["Test ID", "Test condition", "Expected result"])
    st.dataframe(test_cases, use_container_width=True, hide_index=True)
    st.info("Record actual test results after running the tests. Do not report expected results as measured results.")
