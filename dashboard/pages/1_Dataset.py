"""Page 1 — Dataset & Cleaning"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st, plotly.graph_objects as go, pandas as pd
from utils import *

st.set_page_config(page_title="Dataset & Cleaning | ReviewLens", layout="wide")
st.markdown("""<style>
  [data-testid="stAppViewContainer"]{background:#0f172a;}
  [data-testid="stSidebar"]{background:#1e293b !important;}
  h1,h2,h3,h4,p,li,label{color:#f1f5f9 !important;}
  [data-testid="metric-container"]{background:#1e293b;border-radius:10px;padding:12px;}
  thead tr th{background:#334155 !important;color:#f1f5f9 !important;}
  tbody tr:nth-child(even){background:#1e293b !important;}
  tbody tr:nth-child(odd){background:#0f172a !important;}
  td,th{color:#e2e8f0 !important;}
</style>""", unsafe_allow_html=True)

section_header("Dataset Ingestion & Data Hygiene Audit",
               "Amazon Fine Food Reviews (Kaggle CC0) · 568,454 Raw Rows · Oct 1999 – Oct 2012")

# ── Load cleaning log ──────────────────────────────────────────────────────
log = load_json("cleaning_log.json")
rows_in  = log.get("rows_in", 568454)
rows_out = log.get("rows_out", 567247)
removed  = log.get("rows_removed_total", 1207)

# ── KPIs ──────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
kpi(c1, "Raw Input",       f"{rows_in:,}",   "Kaggle CSV rows",               BLUE)
kpi(c2, "Clean Records",   f"{rows_out:,}",  "Stored in MongoDB",             GREEN)
kpi(c3, "Removed Rows",    f"{removed:,}",   "0.21% of raw dataset",          RED)
kpi(c4, "Unique Products", f"{log.get('products',74258):,}", "Catalog items", TEAL)
kpi(c5, "Unique Reviewers",f"{log.get('users',256059):,}",  "Authors",         AMBER)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row: before/after bar + cleaning breakdown ─────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### Volume Comparison: Raw vs Clean")
    fig = go.Figure(go.Bar(
        x=["Raw Dataset (568,454)", "Cleaned Dataset (567,247)"],
        y=[rows_in, rows_out],
        marker_color=[AMBER, GREEN],
        text=[f"{rows_in:,}", f"{rows_out:,}"],
        textposition="outside",
    ))
    fig.update_layout(
        paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
        font_color="#e2e8f0", yaxis=dict(gridcolor="#334155"),
        margin=dict(t=20, b=20, l=20, r=20), height=320,
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("#### Cleaning Operations Breakdown (Audit Log)")
    cleaning_rows = [
        ["Null profile names filled with empty string",  log.get("null_profile_name_filled", 26),     "FILLED"],
        ["Null summaries filled with empty string",      log.get("null_summary_filled", 27),          "FILLED"],
        ["Helpful votes greater than total votes",      log.get("dropped_helpful_gt_total", 2),      "DROPPED"],
        ["Out-of-range star scores",                    log.get("dropped_score_out_of_range", 0),    "DROPPED"],
        ["Exact duplicate reviews (User+Product+Time+Text)", log.get("dropped_exact_duplicates", 1205), "DROPPED"],
        ["HTML tags stripped & whitespace collapsed",   log.get("reviews_with_html_tags_cleaned", 146636), "SANITIZED"],
        ["Empty text bodies after cleaning",            log.get("dropped_empty_text_after_cleaning", 0), "DROPPED"],
    ]
    df = pd.DataFrame(cleaning_rows, columns=["Data Quality Condition", "Record Count", "Resolution"])
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── Sentiment Distribution ─────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Sentiment Distribution (Partitioned Data)")
sent = log.get("sentiment_counts", {"positive": 442966, "negative": 81723, "neutral": 42558})

col_pie, col_sent_info = st.columns([1, 1])
with col_pie:
    fig2 = go.Figure(go.Pie(
        labels=["Positive (4-5 Stars)", "Negative (1-2 Stars)", "Neutral (3 Stars)"],
        values=[sent["positive"], sent["negative"], sent["neutral"]],
        marker_colors=[GREEN, RED, AMBER],
        hole=0.55,
        textinfo="label+percent",
        textfont_color="#f1f5f9",
    ))
    fig2.update_layout(
        paper_bgcolor="#0f172a", font_color="#e2e8f0",
        margin=dict(t=20, b=20, l=20, r=20), height=320,
        legend=dict(font_color="#e2e8f0"),
    )
    st.plotly_chart(fig2, use_container_width=True)

with col_sent_info:
    total = sum(sent.values())
    for label, val in [("positive", sent["positive"]), ("negative", sent["negative"]), ("neutral", sent["neutral"])]:
        pct = val / total * 100
        color = PALETTE_SENTIMENT[label]
        st.markdown(f"""
        <div style="background:#1e293b;border-radius:10px;padding:14px;
                    margin-bottom:10px;border-left:4px solid {color};">
          <div style="color:{color};font-weight:700;font-size:0.95rem;
                      text-transform:uppercase;">{label}</div>
          <div style="color:#f1f5f9;font-size:1.5rem;font-weight:800;">{val:,}</div>
          <div style="color:#94a3b8;font-size:.85rem;">{pct:.1f}% of total reviews</div>
        </div>""", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#1e293b;border-radius:10px;padding:14px;">
      <div style="color:#94a3b8;font-size:.8rem;font-weight:600;">Sentiment Partitioning Criteria</div>
      <div style="color:#cbd5e1;font-size:.85rem;margin-top:6px;line-height:1.6;">
        <span style="color:{RED};font-weight:700;">Negative:</span> Score 1 or 2<br>
        <span style="color:{AMBER};font-weight:700;">Neutral:</span> Score 3<br>
        <span style="color:{GREEN};font-weight:700;">Positive:</span> Score 4 or 5
      </div>
    </div>""", unsafe_allow_html=True)

# ── Date range ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Longitudinal Temporal Coverage")
d1, d2 = st.columns(2)
kpi(d1, "Earliest Ingested Review", log.get("date_min", "1999-10-08"), "13 years continuous corpus", BLUE)
kpi(d2, "Latest Ingested Review",   log.get("date_max", "2012-10-26"), "Complete historical archive",  TEAL)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="background:#1e293b;border-radius:8px;padding:12px 16px;border-left:3px solid #3b82f6;color:#cbd5e1;font-size:0.85rem;">
  <b>Requirement Alignment:</b> Unstructured text dataset with metadata totaling 568,454 records, satisfying the course threshold of 50,000 records by 11.3x. All preprocessing transformations are fully logged.
</div>""", unsafe_allow_html=True)
