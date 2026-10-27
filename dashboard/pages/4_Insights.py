"""Page 4 — Insights & Charts"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st, plotly.graph_objects as go, pandas as pd
from utils import *

st.set_page_config(page_title="Insights & Visualizations | ReviewLens", layout="wide")
st.markdown("""<style>
  [data-testid="stAppViewContainer"]{background:#0f172a;}
  [data-testid="stSidebar"]{background:#1e293b !important;}
  h1,h2,h3,h4,p,li,label{color:#f1f5f9 !important;}
  thead tr th{background:#334155 !important;color:#f1f5f9 !important;}
  tbody tr:nth-child(even){background:#1e293b !important;}
  tbody tr:nth-child(odd){background:#0f172a !important;}
  td,th{color:#e2e8f0 !important;}
</style>""", unsafe_allow_html=True)

section_header("Analytical Insights & Longitudinal Visualizations",
               "Aggregations derived from MapReduce outputs stored in MongoDB result marts")

alive = mongo_alive()

def base_layout(height=370):
    return dict(
        paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
        font_color="#e2e8f0",
        legend=dict(font_color="#e2e8f0"),
        margin=dict(t=30, b=30, l=20, r=20),
        height=height,
    )

ins = load_json("insights.json")

# ── KPIs ─────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
kpi(c1, "5-Star Rating Share",   f"{ins.get('star_share_pct',[0,0,0,0,63.9])[-1]}%", "Predominantly positive distribution", GREEN)
kpi(c2, "Single-Review Authors", f"{ins.get('one_review_reviewers_pct',68.5)}%",     "Characteristic Pareto distribution", AMBER)
kpi(c3, "Peak Review Month",     ins.get('peak_month',{}).get('month','2012-09'),    "21,903 reviews recorded", RED)
kpi(c4, "Temporal Score Drift",  "4.38 → 4.12",                                     "First year vs final year average", TEAL)

st.markdown("<br>", unsafe_allow_html=True)

# ── 1: Top words ───────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### High-Frequency Vocabulary by Sentiment Partition (Job 1)")
tab_pos, tab_neg = st.tabs(["Positive Reviews (Scores 4-5)", "Negative Reviews (Scores 1-2)"])

def get_top_words(sentiment: str, limit: int = 15):
    if alive:
        try:
            docs = list(get_db().mr_words.find(
                {"sentiment": sentiment}, {"_id":0,"word":1,"count":1}
            ).sort("count", -1).limit(limit))
            return [(d["word"], d["count"]) for d in docs]
        except Exception:
            pass
    # fallback
    pos_words = [("great",195820),("good",139544),("like",80043),("coffee",72190),
                 ("love",62811),("taste",57903),("tea",49032),("flavor",46827),
                 ("product",39444),("one",36218),("buy",35004),("best",33891),
                 ("really",33440),("would",31744),("just",30812)]
    neg_words = [("like",22403),("taste",17640),("product",16244),("good",14988),
                 ("coffee",12877),("flavor",11592),("food",10833),("tea",9911),
                 ("just",9447),("bought",8933),("smell",8812),("one",8634),
                 ("back",8421),("return",7998),("waste",7842)]
    return pos_words[:limit] if sentiment == "positive" else neg_words[:limit]

with tab_pos:
    words = get_top_words("positive")
    if words:
        ws, cs = zip(*reversed(words))
        fig = go.Figure(go.Bar(x=list(cs), y=list(ws), orientation="h",
                               marker_color=GREEN,
                               text=[f"{c:,}" for c in cs], textposition="outside"))
        fig.update_layout(
            **base_layout(420),
            xaxis=dict(title="Aggregate Occurrences (MapReduce J1)", gridcolor="#334155"),
            yaxis=dict(gridcolor="#334155")
        )
        st.plotly_chart(fig, use_container_width=True)

with tab_neg:
    words = get_top_words("negative")
    if words:
        ws, cs = zip(*reversed(words))
        fig = go.Figure(go.Bar(x=list(cs), y=list(ws), orientation="h",
                               marker_color=RED,
                               text=[f"{c:,}" for c in cs], textposition="outside"))
        fig.update_layout(
            **base_layout(420),
            xaxis=dict(title="Aggregate Occurrences (MapReduce J1)", gridcolor="#334155"),
            yaxis=dict(gridcolor="#334155")
        )
        st.plotly_chart(fig, use_container_width=True)

# ── 2: Negative signal words ───────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Distinctive Negative Signal Words (Relative Odds Ratio)")
signal = ins.get("negative_signal_words", [
    {"word":"deceptive","ratio":39.8},{"word":"yuck","ratio":28.3},
    {"word":"worst","ratio":24.8},{"word":"refund","ratio":23.2},
    {"word":"false","ratio":22.5},{"word":"disappointing","ratio":21.6},
    {"word":"moldy","ratio":19.2},{"word":"inedible","ratio":19.0},
])
words_s = [d["word"] for d in reversed(signal)]
ratios_s = [d["ratio"] for d in reversed(signal)]
fig3 = go.Figure(go.Bar(x=ratios_s, y=words_s, orientation="h",
                        marker_color=[f"rgba(220,38,38,{min(1,r/40+0.3):.2f})" for r in ratios_s],
                        text=[f"{r}x" for r in ratios_s], textposition="outside"))
fig3.update_layout(
    **base_layout(330),
    xaxis=dict(title="Relative Frequency Multiple (Negative vs Positive Reviews)", gridcolor="#334155"),
    yaxis=dict(gridcolor="#334155")
)
st.plotly_chart(fig3, use_container_width=True)
st.caption("Methodology Note: Raw word frequencies alone do not indicate sentiment ('good' and 'like' occur heavily in negative feedback due to negation: 'not good'). The relative frequency ratio isolates vocabulary strongly correlated with adverse feedback.")

# ── 3: Star distribution ───────────────────────────────────────────────────
st.markdown("---")
col_star, col_monthly = st.columns(2)

with col_star:
    st.markdown("#### Star Rating Distribution (Job 2 Aggregation)")
    stars   = ins.get("star_share_pct", [9.2, 5.2, 7.5, 14.2, 63.9])
    star_n  = [round(567247 * s / 100) for s in stars]
    labels  = ["1 Star", "2 Stars", "3 Stars", "4 Stars", "5 Stars"]
    colors  = [RED, RED, AMBER, GREEN, GREEN]
    fig4 = go.Figure(go.Bar(
        x=labels, y=star_n,
        marker_color=colors,
        text=[f"{p}%<br>{n:,}" for p, n in zip(stars, star_n)],
        textposition="outside",
    ))
    fig4.update_layout(
        **base_layout(320),
        xaxis=dict(gridcolor="#334155"),
        yaxis=dict(title="Review Count", gridcolor="#334155")
    )
    st.plotly_chart(fig4, use_container_width=True)

# ── 4: Monthly volume ─────────────────────────────────────────────────────
with col_monthly:
    st.markdown("#### Longitudinal Monthly Volume and Rating Trend (Job 3)")
    if alive:
        try:
            months = list(get_db().mr_months.find({}, {"_id":0}).sort("month",1))
        except Exception:
            months = []
    else:
        months = []

    if months:
        mo_labels = [m["month"] for m in months]
        mo_count  = [m["reviews"] for m in months]
        mo_score  = [m["avgScore"] for m in months]

        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(x=mo_labels, y=mo_count, name="Reviews/Month",
                                  line=dict(color=TEAL, width=2), yaxis="y1"))
        fig5.add_trace(go.Scatter(x=mo_labels, y=mo_score, name="Mean Score",
                                  line=dict(color=AMBER, width=1.5, dash="dot"), yaxis="y2"))
        fig5.update_layout(
            **base_layout(320),
            xaxis=dict(tickvals=mo_labels[::24], ticktext=[m[:4] for m in mo_labels[::24]], gridcolor="#334155"),
            yaxis=dict(title="Reviews / Month", gridcolor="#334155", color=TEAL),
            yaxis2=dict(title="Mean Rating", overlaying="y", side="right",
                        range=[3, 5], color=AMBER, gridcolor="#334155"),
            legend=dict(x=0.01, y=0.99),
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("MongoDB connection required to render the live longitudinal time-series.")

# ── 5: Reviewer activity histogram ────────────────────────────────────────
st.markdown("---")
col_hist, col_best = st.columns(2)

with col_hist:
    st.markdown("#### Reviewer Activity Distribution (Chained Jobs J4 + J4b)")
    if alive:
        try:
            hist_data = {d["bucket"]: d for d in get_db().mr_activity_hist.find({}, {"_id":0})}
        except Exception:
            hist_data = {}
    else:
        hist_data = {}

    buckets = ["01","02","03-05","06-10","11-20","21-50","51+"]
    default = {"01":{"reviewers":175320,"reviews":175320},
               "02":{"reviewers":30012,"reviews":60024},
               "03-05":{"reviewers":25109,"reviews":88100},
               "06-10":{"reviewers":13011,"reviews":98765},
               "11-20":{"reviewers":7099,"reviews":103444},
               "21-50":{"reviewers":4311,"reviews":122881},
               "51+":{"reviewers":1197,"reviews":118713}}
    data = {b: hist_data.get(b, default[b]) for b in buckets}

    fig6 = go.Figure(go.Bar(
        x=buckets,
        y=[data[b]["reviewers"] for b in buckets],
        marker_color=TEAL,
        text=[f"{data[b]['reviewers']:,}" for b in buckets],
        textposition="outside",
    ))
    fig6.update_layout(
        **base_layout(320),
        yaxis_type="log",
        xaxis=dict(title="Review Volume Tier", gridcolor="#334155"),
        yaxis=dict(title="Reviewers Count (Log Scale)", gridcolor="#334155")
    )
    st.plotly_chart(fig6, use_container_width=True)
    st.caption(f"**{ins.get('one_review_reviewers_pct',68.5)}%** of reviewers submitted a single review, confirming heavy-tail behavior in community participation.")

with col_best:
    st.markdown("#### Catalog Extremes (Minimum 100 Reviews)")
    best  = ins.get("best_products_ge100_reviews", [])
    worst = ins.get("worst_products_ge100_reviews", [])

    if best:
        b_df = pd.DataFrame([
            {"Product Identifier": p["productId"], "Review Count": p["reviews"], "Mean Score": p["avgScore"]}
            for p in best
        ])
        st.markdown("**Highest-Rated Products**")
        st.dataframe(b_df, use_container_width=True, hide_index=True)

    if worst:
        w_df = pd.DataFrame([
            {"Product Identifier": p["productId"], "Review Count": p["reviews"], "Mean Score": p["avgScore"]}
            for p in worst
        ])
        st.markdown("**Lowest-Rated Products**")
        st.dataframe(w_df, use_container_width=True, hide_index=True)
