from pathlib import Path
import json
from datetime import datetime

MEMORY_FILE = Path(__file__).parent / "memory" / "agent_memory.json"

def load_memory():
    if not MEMORY_FILE.exists():
        return []
    try:
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

def _write(records):
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(records, indent=2), encoding="utf-8")

def save_interaction(prompt, intent, tools, response):
    records = load_memory()
    records.append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "prompt": prompt,
        "intent": intent,
        "tools_used": ", ".join(tools),
        "response": response,
        "feedback": "Not provided"
    })
    _write(records[-200:])

def save_feedback(prompt, feedback):
    records = load_memory()
    for record in reversed(records):
        if record.get("prompt") == prompt and record.get("feedback") == "Not provided":
            record["feedback"] = feedback
            break
    _write(records)

def clear_memory():
    _write([])
