# Smart Inventory Expiry and Stock Monitoring Agent

A DAT404 custom AI agent project built with Python and Streamlit.

## Features
- Natural-language prompt box for inventory requests.
- Agent intent detection, planning and tool selection.
- Expiry checking: expired, urgent (within 7 days), upcoming (within 30 days).
- Stock monitoring: low-stock and out-of-stock detection.
- Recommendations based on verified inventory records.
- Inventory summary dashboard and charts.
- Add products and upload a CSV dataset.
- Episodic memory and user feedback.
- Optional local Ollama explanation (Qwen model).
- Automated tests.

## Windows / VS Code setup

Open the project folder in VS Code. Open Terminal > New Terminal and run these commands one at a time:

```powershell
py --version
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

If PowerShell blocks activation, run this once in the same terminal:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
Then activate the environment again:
```powershell
.\.venv\Scripts\Activate.ps1
```

Open the local address shown in the terminal, normally:
http://localhost:8501

## Example prompts
- Check all products that are expiring soon.
- Show me all expired products.
- Which products have low stock?
- Recommend which products I should restock.
- Generate an inventory summary report.

## Optional Ollama
The agent's inventory calculations and tool selection work without Ollama.
To enable local LLM explanations:
1. Install and start Ollama.
2. Pull a model, for example: `ollama pull qwen3:8b`
3. In the dashboard sidebar, enable "Use local Ollama explanation".
4. Keep the rule-based tools as the source of inventory facts.

If Ollama is unavailable, the application automatically uses its rule-based explanation.

## Run tests
In the VS Code terminal:
```powershell
py -m pytest evaluation/test_agent.py -v
```

## CSV format
Required columns:
`product_id, product_name, category, quantity, min_stock, expiry_date, supplier, unit_price`

Use dates in `YYYY-MM-DD` format.

## Important project notes
- The sample dataset is generated with expiry dates relative to the day the application first creates the CSV.
- The sample data is for demonstration only. Replace it with your own verified dataset before presenting real business claims.
- Recommendations are suggestions. The agent does not automatically order products or dispose of stock.
- Record actual evaluation results; do not claim test success until the tests have been run.
