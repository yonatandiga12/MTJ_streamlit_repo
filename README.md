# Multi-Turn Jailbreak Dashboard

This repository hosts the public Streamlit app that displays live status for multi-turn jailbreak runs.

**Dashboard URL:**  
https://mtjapprepo-nkvag6gkyecugh8jnu8riw.streamlit.app/

The app reads `runs.json` from this repository (periodically updated by the cluster jobs) and renders a table of:

- Run ID
- Target model
- Dataset name
- Questions completed / total
- Successful / failed questions
- Attack success rate (ASR)
- Predictor model repo
- Last update time

