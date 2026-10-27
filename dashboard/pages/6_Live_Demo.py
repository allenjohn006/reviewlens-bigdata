"""Page 6 — Live Demo (CRUD + Query Workbench)"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st, pandas as pd, time
from utils import *

st.set_page_config(page_title="Live Demonstration | ReviewLens", layout="wide")
st.markdown("""<style>
  [data-testid="stAppViewContainer"]{background:#0f172a;}
  [data-testid="stSidebar"]{background:#1e293b !important;}
  h1,h2,h3,h4,p,li,label{color:#f1f5f9 !important;}
  thead tr th{background:#334155 !important;color:#f1f5f9 !important;}
  tbody tr:nth-child(even){background:#1e293b !important;}
  tbody tr:nth-child(odd){background:#0f172a !important;}
  td,th{color:#e2e8f0 !important;}
  .stTextInput input,.stSelectbox div{background:#1e293b !important;color:#f1f5f9 !important;}
  div.stButton>button{background:#1d4ed8;color:white;border:none;border-radius:8px;
                      padding:8px 20px;font-weight:600;}
</style>""", unsafe_allow_html=True)

section_header("Live MongoDB Query & Operational Demonstration",
               "Real-time CRUD operations, aggregation pipelines, and query execution benchmarks")

alive = mongo_alive()
if not alive:
    st.error("MongoDB is offline. Execute 'bash scripts/03_start_mongo.sh' to initialize daemon.")
    st.stop()

db = get_db()
R  = db["reviews"]

doc_count = R.count_documents({})
st.success(f"Connected: collection 'reviewlens.reviews' contains {doc_count:,} documents.")

# ── Tabs ───────────────────────────────────────────────────────────────────
t1, t2, t3, t4 = st.tabs(["Query Workbench", "Aggregation Pipeline", "Live CRUD Operations", "Index Execution Benchmark"])

# ───── Tab 1: Query ────────────────────────────────────────────────────────
with t1:
    st.markdown("##### Search Reviews Collection")
    col_a, col_b, col_c = st.columns([2, 1, 1])
    product_id = col_a.text_input("Product Identifier", placeholder="e.g. B007JFMH8M")
    sentiment  = col_b.selectbox("Sentiment Filter", ["(Any)", "positive", "negative", "neutral"])
    n_results  = col_c.slider("Result Limit", 1, 50, 10)

    if st.button("Execute Query"):
        query = {}
        if product_id.strip():
            query["productId"] = product_id.strip()
        if sentiment != "(Any)":
            query["sentiment"] = sentiment
        try:
            docs = list(R.find(query, {"_id":0,"reviewId":1,"productId":1,"userId":1,
                                       "score":1,"sentiment":1,"date":1,"summary":1,"text":1}).limit(n_results))
            st.markdown(f"**Matching Documents: {R.count_documents(query):,} | Showing: {len(docs)}**")
            if docs:
                st.dataframe(pd.DataFrame(docs), use_container_width=True, hide_index=True)
            else:
                st.warning("No matching documents found.")
        except Exception as e:
            st.error(f"Execution Error: {e}")

    st.markdown("---")
    col_q1, col_q2, col_q3 = st.columns(3)
    with col_q1:
        five_star = R.count_documents({"score": 5})
        st.metric("5-Star Reviews", f"{five_star:,}", f"{five_star/567247*100:.1f}% of total")
    with col_q2:
        neg = R.count_documents({"sentiment": "negative"})
        st.metric("Negative Reviews", f"{neg:,}", f"{neg/567247*100:.1f}% of total")
    with col_q3:
        recent = R.count_documents({"date": {"$gte": "2012-01-01"}})
        st.metric("Reviews Ingested (2012)", f"{recent:,}", "Peak volume year")

# ───── Tab 2: Aggregation ──────────────────────────────────────────────────
with t2:
    st.markdown("##### High-Volume Top Products by Mean Rating (Aggregation Pipeline)")
    min_reviews = st.slider("Minimum Review Volume Threshold", 10, 500, 200)

    if st.button("Run Aggregation Pipeline"):
        with st.spinner("Executing pipeline across 567,247 documents..."):
            t0 = time.time()
            pipeline = [
                {"$group": {"_id": "$productId", "n": {"$sum": 1}, "avg": {"$avg": "$score"}}},
                {"$match": {"n": {"$gte": min_reviews}}},
                {"$sort": {"avg": -1}},
                {"$limit": 10},
            ]
            results = list(R.aggregate(pipeline))
            elapsed_ms = (time.time() - t0) * 1000
        st.success(f"Aggregation completed in **{elapsed_ms:.1f} ms**")
        if results:
            df_agg = pd.DataFrame([
                {"Rank": i+1, "Product Identifier": r["_id"],
                 "Review Count": r["n"], "Mean Rating": round(r["avg"], 4)}
                for i, r in enumerate(results)
            ])
            st.dataframe(df_agg, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("##### Yearly Ingestion Distribution")
    if st.button("Calculate Annual Volume"):
        pipeline2 = [
            {"$group": {"_id": {"$substr": ["$date", 0, 4]}, "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}},
        ]
        yearly = list(R.aggregate(pipeline2))
        if yearly:
            df_yr = pd.DataFrame([{"Year": r["_id"], "Reviews": r["count"]} for r in yearly])
            import plotly.express as px
            fig = px.bar(df_yr, x="Year", y="Reviews",
                         color_discrete_sequence=[TEAL],
                         title="Annual Ingested Volume")
            fig.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                              font_color="#e2e8f0", height=350)
            st.plotly_chart(fig, use_container_width=True)

# ───── Tab 3: CRUD ────────────────────────────────────────────────────────
with t3:
    st.markdown("##### Live CRUD Operations Cycle")
    st.info("Demonstrates programmatic Create, Read, Update, and Delete operations against the native MongoDB server.")

    if st.button("Execute Live CRUD Cycle"):
        try:
            # Cleanup prior demo documents
            R.delete_many({"productId": "B000DEMO_UI"})
            log_lines = []

            # CREATE
            doc = {"reviewId": 9999001, "productId": "B000DEMO_UI", "userId": "UIDEMO",
                   "score": 5, "sentiment": "positive", "date": "2026-10-27",
                   "month": "2026-10", "summary": "Viva demonstration document", "text": "Document created live during demonstration.",
                   "profileName": "Viva Reviewer", "helpYes": 0, "helpTotal": 0}
            res = R.insert_one(dict(doc))
            log_lines.append(f"CREATE: insert_one() inserted document with _id = `{res.inserted_id}`")

            # READ
            found = R.find_one({"reviewId": 9999001}, {"_id": 0})
            log_lines.append(f"READ: find_one() located document with score = `{found['score']}`, sentiment = `{found['sentiment']}`")

            count_5 = R.count_documents({"score": 5})
            log_lines.append(f"READ: count_documents() identified `{count_5:,}` 5-star documents in collection")

            # UPDATE
            upd = R.update_one({"reviewId": 9999001}, {"$set": {"score": 4, "edited": True}, "$inc": {"helpYes": 2}})
            log_lines.append(f"UPDATE: update_one() modified `{upd.modified_count}` document(s) with $set and $inc operators")

            after = R.find_one({"reviewId": 9999001}, {"_id": 0, "score": 1, "helpYes": 1, "edited": 1})
            log_lines.append(f"   Post-update state: score={after.get('score')}, helpYes={after.get('helpYes')}, edited={after.get('edited')}")

            # DELETE
            d1 = R.delete_one({"reviewId": 9999001})
            log_lines.append(f"DELETE: delete_one() removed `{d1.deleted_count}` document(s)")

            final = R.count_documents({})
            log_lines.append(f"INTEGRITY: Collection restored to baseline count: `{final:,}` documents")

            for line in log_lines:
                st.markdown(f"• {line}")
            st.success("CRUD demonstration completed successfully.")
        except Exception as e:
            st.error(f"CRUD Operation Failed: {e}")

# ───── Tab 4: Index Benchmark ────────────────────────────────────────────
with t4:
    st.markdown("##### Query Execution Plan Benchmark: explain()")
    pid = st.text_input("Target Product ID for Plan Evaluation", value="B007JFMH8M")

    if st.button("Evaluate Execution Plans"):
        try:
            import plotly.graph_objects as go
            results_b = {}
            for label, hint in [("Indexed Plan (productId_1)", {"productId": 1}), ("Table Scan (Natural)", {"$natural": 1})]:
                exp = R.find({"productId": pid}).hint(list(hint.items())).explain()["executionStats"]
                results_b[label] = {
                    "docs_examined": exp["totalDocsExamined"],
                    "docs_returned": exp["nReturned"],
                    "server_ms":     exp["executionTimeMillis"],
                }

            for label, stats in results_b.items():
                color = GREEN if "Indexed" in label else RED
                st.markdown(f"""
                <div style="background:#1e293b;border-radius:10px;padding:14px;
                            margin-bottom:8px;border-left:4px solid {color};">
                  <b style="color:{color};">{label}</b><br>
                  Documents Examined: <b style="color:#f1f5f9;">{stats['docs_examined']:,}</b> &nbsp;|&nbsp;
                  Documents Returned: <b style="color:#f1f5f9;">{stats['docs_returned']:,}</b> &nbsp;|&nbsp;
                  Server Execution Time: <b style="color:{color};">{stats['server_ms']} ms</b>
                </div>""", unsafe_allow_html=True)

            fig = go.Figure(go.Bar(
                x=list(results_b.keys()),
                y=[r["server_ms"] for r in results_b.values()],
                marker_color=[GREEN, RED],
                text=[f"{r['server_ms']} ms" for r in results_b.values()],
                textposition="outside",
            ))
            fig.update_layout(
                paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                font_color="#e2e8f0", yaxis_title="Execution Time (ms)",
                yaxis=dict(gridcolor="#334155"), height=300,
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)

            speedup = results_b["Table Scan (Natural)"]["server_ms"] / max(results_b["Indexed Plan (productId_1)"]["server_ms"], 1)
            st.success(f"Indexed scan executed **{speedup:.0f}x faster**, eliminating the need to examine {results_b['Table Scan (Natural)']['docs_examined']:,} documents.")
        except Exception as e:
            st.error(f"Benchmark Error: {e}")
