import requests

def explain_with_ollama(user_prompt, verified_summary, result_df, model="qwen3:8b"):
    """Optional LLM explanation. The inventory calculations remain rule-based."""
    try:
        facts = result_df.head(20).to_string(index=False) if result_df is not None else "No rows"
        prompt = f"""
You are explaining verified results from an inventory monitoring tool.
User request: {user_prompt}
Verified tool summary: {verified_summary}
Verified rows:
{facts}

Explain the result in clear, short language. Do not invent quantities, dates, products,
or actions. If information is missing, say it is not available. Do not override the
verified tool summary.
"""
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=35
        )
        response.raise_for_status()
        return response.json().get("response", "").strip() or None
    except Exception:
        return None
