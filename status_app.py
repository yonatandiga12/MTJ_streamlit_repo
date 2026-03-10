import json
from datetime import datetime, timedelta, timezone
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


def parse_timestamp(ts: str | None) -> datetime | None:
    if not ts:
        return None
    ts = str(ts).strip()
    try:
        # Expected format: "YYYY-MM-DD HH:MM:SS UTC"
        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S UTC")
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


data = load_runs(Path("runs.json"))
if not data:
    st.info("No runs.json found yet. Wait for a job to update it.")
    st.stop()

raw_runs = list(data["runs"].values())
if not raw_runs:
    st.info("No runs recorded yet.")
    st.stop()

now = datetime.now(timezone.utc)
active_rows: list[dict] = []
stuck_ids: list[str] = []
done_ids: list[str] = []

for r in raw_runs:
    total = int(r.get("total_questions_configured") or 0)
    completed = int(r.get("questions_completed") or 0)
    run_id = str(r.get("run_id") or "")

    last_dt = parse_timestamp(r.get("last_updated"))
    is_done = total > 0 and completed >= total

    # Skip fully done runs if they are older than 2 hours
    if is_done and last_dt is not None and (now - last_dt) > timedelta(hours=2):
        continue

    is_stuck = False
    if (not is_done) and last_dt is not None and (now - last_dt) > timedelta(hours=4):
        is_stuck = True
        stuck_ids.append(run_id)

    # Add status label
    if is_done:
        r["status"] = "Done"
        done_ids.append(run_id)
    elif is_stuck:
        r["status"] = "Stuck"
    else:
        r["status"] = "Running"

    active_rows.append(r)

if not active_rows:
    st.info("No active runs to display (all finished more than 2 hours ago).")
    st.stop()

df = pd.DataFrame(active_rows)

# Sort by last_updated if present
if "last_updated" in df.columns:
    df = df.sort_values("last_updated", ascending=False)

st.caption(f"Generated at: {data.get('generated_at', 'unknown')}")

if done_ids:
    st.markdown(":green[Done runs: {}]".format(", ".join(done_ids)))

if stuck_ids:
    st.markdown(":red[Stuck runs: {}]".format(", ".join(stuck_ids)))

cols_to_show = [
    "run_id",
    "status",
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

