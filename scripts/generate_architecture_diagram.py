"""Generate a crisp, professional, high-resolution Pipeline Architecture diagram for ReviewLens."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

# Figure setup
fig, ax = plt.subplots(figsize=(15, 8.5), dpi=300)
fig.patch.set_facecolor("#0f172a")
ax.set_facecolor("#0f172a")

# Coordinate bounds
ax.set_xlim(0, 15)
ax.set_ylim(0, 8.5)
ax.axis("off")

# Helper for drawing rounded boxes
def draw_box(x, y, w, h, title, subtitle, details, border_color, fill_color="#1e293b", badge=None):
    # Shadow/Border box
    box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12,rounding_size=0.15",
                                 facecolor=fill_color, edgecolor=border_color, linewidth=1.8)
    ax.add_patch(box)
    
    # Title
    ax.text(x + w*0.05, y + h - 0.35, title, fontsize=11, fontweight="bold", color="#f8fafc", ha="left")
    
    # Badge (if any)
    if badge:
        bbox_props = dict(boxstyle="round,pad=0.2", facecolor=border_color, alpha=0.25, edgecolor=border_color, lw=1)
        ax.text(x + w - 0.15, y + h - 0.35, badge, fontsize=8, fontweight="bold", color=border_color, ha="right", bbox=bbox_props)

    # Subtitle
    if subtitle:
        ax.text(x + w*0.05, y + h - 0.7, subtitle, fontsize=9, fontweight="semibold", color="#94a3b8", ha="left")
    
    # Details
    if details:
        y_text = y + h - 1.05
        for line in details:
            ax.text(x + w*0.05, y_text, line, fontsize=8.2, color="#cbd5e1", ha="left")
            y_text -= 0.32

# Helper for drawing connected arrows
def draw_arrow(x1, y1, x2, y2, label="", color="#64748b", rad=0.0):
    connectionstyle = f"arc3,rad={rad}" if rad != 0 else "arc3,rad=0"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.45",
                                color=color, lw=1.8, connectionstyle=connectionstyle))
    if label:
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2 + 0.15
        bbox_props = dict(boxstyle="round,pad=0.2", facecolor="#0f172a", edgecolor="#334155", lw=0.8)
        ax.text(mx, my, label, fontsize=7.8, color="#94a3b8", ha="center", va="center", bbox=bbox_props)

# --- Row 1: INGESTION & PRIMARY STORAGE (Top) ---
# 1. Raw Dataset
draw_box(0.5, 5.7, 3.8, 2.2,
         "1. Raw Ingestion", "Kaggle Dataset (CC0)",
         ["• Amazon Fine Food Reviews", "• 568,454 text reviews", "• 74,258 products, 256,059 users", "• Period: Oct 1999 – Oct 2012"],
         "#f59e0b", badge="RAW DATA")

# 2. Cleaning & Preprocessing
draw_box(5.5, 5.7, 4.0, 2.2,
         "2. Cleaning & Normalization", "scripts/02_clean.py",
         ["• Removed 1,205 duplicate reviews", "• Dropped 2 invalid vote rows", "• Stripped HTML in 146,636 texts", "• Result: 567,247 clean JSONL"],
         "#10b981", badge="HYGIENE AUDIT")

# 3. Native MongoDB Primary Store
draw_box(10.6, 5.7, 3.9, 2.2,
         "3. Native MongoDB Store", "reviewlens.reviews (:27019)",
         ["• Standalone host process (No Docker)", "• Bulk loaded in 9.4s (60k docs/s)", "• 7 Compound & Unique Indexes", "• 152 MB database footprint"],
         "#3b82f6", badge="NOSQL PRIMARY")

# --- Row 2: DISTRIBUTED STORAGE & PROCESSING (Middle) ---
# 4. HDFS Storage
draw_box(10.6, 2.7, 3.9, 2.2,
         "4. Distributed File System", "HDFS Cluster (3.4.3)",
         ["• Exported file: reviews.tsv (283 MB)", "• Partitioned into 3 blocks of 128 MB", "• Block 0: ~189k rows | Block 1: ~189k", "• Block 2: ~189k rows (Data locality)"],
         "#8b5cf6", badge="HDFS BLOCKS")

# 5. Hadoop MapReduce on YARN
draw_box(4.8, 2.7, 4.7, 2.2,
         "5. Hadoop MapReduce Engine", "YARN Distributed Compute",
         ["• J1: Sentiment Word Frequency (MIN_COUNT=20)", "   ↳ Combiner cut 22.8M → 950k pairs (-96%)", "• J2: Per-Product Rating Stats (74k products)", "• J3: Monthly Longitudinal Trend (143 months)", "• J4 & J4b: Reviewer Activity & Histogram (Chained)"],
         "#ec4899", badge="MAPREDUCE ON YARN")

# --- Row 3: RESULTS & CONSUMPTION (Bottom) ---
# 6. MongoDB Result Collections
draw_box(0.5, 2.7, 3.5, 2.2,
         "6. Analytical Serving", "MongoDB Collections (mr_*)",
         ["• mr_words (34,541 rows)", "• mr_products (74,258 rows)", "• mr_months (143 rows)", "• mr_users (256,059 rows)", "• mr_activity_hist (7 buckets)"],
         "#06b6d4", badge="NOSQL MARTS")

# 7. Verification & UI Dashboard (Full width bottom bar)
draw_box(0.5, 0.4, 14.0, 1.6,
         "7. Independent Validation & Interactive Dashboard", "End-to-End Verification & Serving",
         ["• Ground-Truth Verification (08_validate.py): Independent Pandas recomputation vs Hadoop results → 5/5 Checks PASS (0 mismatches across 365,008 keys)",
          "• Real-Time CRUD & Index Benchmark (10_mongo_crud_demo.py): explain() query benchmark verified 2 ms indexed vs 188 ms unindexed collection scan",
          "• Interactive Streamlit Dashboard: Multi-page analytics, live query workbench, and operational cluster telemetry"],
         "#10b981", badge="ALL PASS (5/5)")

# --- Arrows connecting pipeline stages ---
# 1 -> 2
draw_arrow(4.3, 6.8, 5.5, 6.8, "02_clean.py", "#10b981")
# 2 -> 3
draw_arrow(9.5, 6.8, 10.6, 6.8, "04_load_mongo.py", "#3b82f6")
# 3 -> 4
draw_arrow(12.5, 5.7, 12.5, 4.9, "05_export_to_hdfs.py", "#8b5cf6")
# 4 -> 5
draw_arrow(10.6, 3.8, 9.5, 3.8, "3 parallel map splits", "#ec4899")
# 5 -> 6
draw_arrow(4.8, 3.8, 4.0, 3.8, "07_load_results.py", "#06b6d4")
# 6 -> 7
draw_arrow(2.2, 2.7, 2.2, 2.0, "08_validate.py", "#10b981")
# 5 -> 7
draw_arrow(7.1, 2.7, 7.1, 2.0, "09_analysis_and_charts.py", "#10b981")

# Diagram Title & Subtitle Header
ax.text(0.5, 8.2, "ReviewLens: End-to-End Big Data Architecture", fontsize=15, fontweight="bold", color="#f8fafc")
ax.text(0.5, 7.95, "Separation of Concerns: Native MongoDB (Storage & Serving) | Apache Hadoop HDFS & YARN (Distributed MapReduce)", fontsize=9.5, color="#64748b")

plt.tight_layout()
out_path = Path(__file__).resolve().parents[1] / "dashboard/pipeline_architecture.png"
out_path.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out_path, facecolor="#0f172a", edgecolor="none", dpi=300)
print(f"Generated architecture diagram at {out_path}")

