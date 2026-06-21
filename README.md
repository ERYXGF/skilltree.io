# skilltree.io

Paste a GitHub repo link → an AI agent reverse-engineers your code into professional resume bullets and an interactive proficiency chart.

Built for the **Youth Code x AI 2026** hackathon (Track 04: What Do I Even Do With My Life?).

## Stack

Python 3.11+ · FastAPI · React + Tailwind · Plotly · Anthropic Claude · SQLite · GitHub REST API

## Quick start (foundation)

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env        # then add your ANTHROPIC_API_KEY
python scripts/run_all.py     # run foundation test board (Phases 1–10)
uvicorn backend.main:app --reload
```

`GET /health` should return `{"status":"ok"}`.
