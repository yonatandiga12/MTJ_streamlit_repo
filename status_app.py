import json
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Jailbreak Runs Dashboard", layout="wide")

st.title("Jailbreak Runs Dashboard")


def load_runs(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8") or "{}")
        runs = data.get("runs") or {}
        if not isinstance(runs, dict):
            return {}
        return {"generated_at": data.get("generated_at"), "runs": runs}
    except Exception as exc:
        st.error(f"Failed to read runs.json: {exc}")
        return {}


data = load_runs(Path("runs.json"))
if not data:
    st.info("No runs.json found yet. Wait for a job to update it.")
    st.stop()

runs = list(data["runs"].values())
if not runs:
    st.info("No runs recorded yet.")
    st.stop()

df = pd.DataFrame(runs)

# Sort by last_updated if present
if "last_updated" in df.columns:
    df = df.sort_values("last_updated", ascending=False)

st.caption(f"Generated at: {data.get('generated_at', 'unknown')}")

cols_to_show = [
    "run_id",
    "target_model",
    "dataset_name",
    "questions_completed",
    "total_questions_configured",
    "successful_questions",
    "failed_questions",
    "attack_success_rate",
    "predictor_repo",
    "last_updated",
]

existing_cols = [c for c in cols_to_show if c in df.columns]

st.dataframe(df[existing_cols], use_container_width=True)

