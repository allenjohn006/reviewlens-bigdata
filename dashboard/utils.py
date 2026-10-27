"""Shared utilities for the ReviewLens dashboard."""
import os
from pymongo import MongoClient
import streamlit as st

# ── Brand colours ──────────────────────────────────────────────────────────────
GREEN   = "#16a34a"
RED     = "#dc2626"
TEAL    = "#0f766e"
AMBER   = "#f59e0b"
BLUE    = "#1d4ed8"
PURPLE  = "#7c3aed"
BG_DARK = "#0f172a"
BG_MID  = "#1e293b"
CARD    = "#0f172a"

PALETTE_SENTIMENT = {"positive": GREEN, "negative": RED, "neutral": AMBER}

MONGO_URI  = os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27019")
MONGO_PORT = int(os.environ.get("MONGO_PORT", 27019))
DB_NAME    = "reviewlens"

RESULTS_DIR  = os.path.join(os.path.dirname(__file__), "..", "results")
EVIDENCE_DIR = os.path.join(os.path.dirname(__file__), "..", "evidence")


@st.cache_resource
def get_db():
    """Return a cached MongoClient database handle."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    return client[DB_NAME]


def mongo_alive() -> bool:
    try:
        get_db().command("ping")
        return True
    except Exception:
        return False


def kpi(col, label: str, value, delta: str = "", color: str = GREEN):
    """Render a metric KPI card in a Streamlit column."""
    col.markdown(
        f"""
        <div style="
            background:{BG_MID};border-radius:12px;padding:18px 20px;
            border-left:4px solid {color};margin-bottom:4px;">
          <div style="color:#94a3b8;font-size:0.78rem;font-weight:600;
                      text-transform:uppercase;letter-spacing:.08em;">{label}</div>
          <div style="color:#f1f5f9;font-size:1.9rem;font-weight:800;
                      line-height:1.1;margin-top:4px;">{value}</div>
          {f'<div style="color:{GREEN};font-size:.8rem;margin-top:4px;">{delta}</div>' if delta else ''}
        </div>""",
        unsafe_allow_html=True,
    )


def badge(text: str, color: str = GREEN) -> str:
    return (
        f'<span style="background:{color}22;color:{color};border:1px solid {color}55;'
        f'border-radius:6px;padding:2px 10px;font-size:.75rem;font-weight:700;">{text}</span>'
    )


def section_header(title: str, subtitle: str = ""):
    st.markdown(
        f'<h2 style="color:#f1f5f9;margin-bottom:2px;">{title}</h2>'
        + (f'<p style="color:#64748b;margin-top:0;">{subtitle}</p>' if subtitle else ""),
        unsafe_allow_html=True,
    )
    st.markdown('<hr style="border-color:#1e293b;margin:8px 0 20px 0;">', unsafe_allow_html=True)


def load_json(filename: str) -> dict:
    import json, pathlib
    p = pathlib.Path(RESULTS_DIR) / filename
    return json.loads(p.read_text()) if p.exists() else {}

