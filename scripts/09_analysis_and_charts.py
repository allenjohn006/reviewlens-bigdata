#!/usr/bin/env python3
"""STEP 9 - Analyse the MapReduce results stored in MongoDB (queries/aggregations) and draw the charts used in the report/presentation."""
import json, os, pathlib
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pymongo import MongoClient
ROOT = pathlib.Path(__file__).resolve().parents[1]; CH = ROOT / "results/charts"; CH.mkdir(parents=True, exist_ok=True)
db = MongoClient(os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27019")).reviewlens; ins = {}
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False, "font.size": 10})
G, R, T, A = "#16a34a", "#dc2626", "#0f766e", "#f59e0b"
# 1. top words per sentiment
top = {s: list(db.mr_words.find({"sentiment": s}, {"_id": 0}).sort("count", -1).limit(15)) for s in ("positive", "negative")}
fig, ax = plt.subplots(1, 2, figsize=(11, 4.6))
for a, s, col in zip(ax, ("positive", "negative"), (G, R)):
    w = top[s][::-1]; a.barh([x["word"] for x in w], [x["count"] for x in w], color=col); a.set_title(f"Most frequent words in {s} reviews"); a.set_xlabel("occurrences (MapReduce job 1)")
fig.tight_layout(); fig.savefig(CH / "01_top_words.png"); plt.close(fig)
# distinctive words: much more common in negative than positive reviews (relative frequency ratio)
tot = {s: sum(d["count"] for d in db.mr_words.find({"sentiment": s})) for s in ("positive", "negative")}
pos = {d["word"]: d["count"] for d in db.mr_words.find({"sentiment": "positive"})}; neg = {d["word"]: d["count"] for d in db.mr_words.find({"sentiment": "negative"})}
dist = sorted(({"word": w, "negative": c, "positive": pos.get(w, 0), "ratio": round((c / tot["negative"]) / ((pos.get(w, 0) + 1) / tot["positive"]), 1)} for w, c in neg.items() if c >= 300 and c + pos.get(w, 0) >= 500), key=lambda x: -x["ratio"])[:12]
fig, ax = plt.subplots(figsize=(7, 4.4)); d = dist[::-1]; ax.barh([x["word"] for x in d], [x["ratio"] for x in d], color=R); ax.set_title("Words most typical of negative reviews"); ax.set_xlabel("times more frequent in negative than in positive reviews (relative)")
fig.tight_layout(); fig.savefig(CH / "02_negative_signal_words.png"); plt.close(fig)
# 2. score distribution (sum of the per-product star histograms)
stars = [0] * 5
for d in db.mr_products.find({}, {"stars": 1, "_id": 0}):
    stars = [a + b for a, b in zip(stars, d["stars"])]
fig, ax = plt.subplots(figsize=(6, 4)); ax.bar(["1★", "2★", "3★", "4★", "5★"], stars, color=[R, R, A, G, G]); ax.set_title("Reviews by star rating"); [ax.text(i, v, f"{v/sum(stars)*100:.0f}%", ha="center", va="bottom") for i, v in enumerate(stars)]
fig.tight_layout(); fig.savefig(CH / "03_star_distribution.png"); plt.close(fig)
# 3. monthly volume + average score
mo = list(db.mr_months.find({}, {"_id": 0}).sort("month", 1))
fig, ax = plt.subplots(figsize=(10, 4)); ax.plot([m["month"] for m in mo], [m["reviews"] for m in mo], color=T); ax.set_ylabel("reviews per month", color=T); ax2 = ax.twinx(); ax2.plot([m["month"] for m in mo], [m["avgScore"] for m in mo], color=A, lw=1); ax2.set_ylabel("average score", color=A); ax2.set_ylim(3, 5)
ax.set_xticks([m["month"] for m in mo][::12]); ax.set_xticklabels([m["month"][:4] for m in mo][::12]); ax.set_title("Review volume and average score by month (MapReduce job 3)"); fig.tight_layout(); fig.savefig(CH / "04_monthly.png"); plt.close(fig)
# 4. reviewer activity (long tail)
order = ["01", "02", "03-05", "06-10", "11-20", "21-50", "51+"]; h = {d["bucket"]: d for d in db.mr_activity_hist.find({}, {"_id": 0})}
fig, ax = plt.subplots(figsize=(7, 4)); ax.bar(order, [h[b]["reviewers"] for b in order], color=T); ax.set_yscale("log"); ax.set_xlabel("reviews written by one reviewer"); ax.set_ylabel("number of reviewers (log scale)"); ax.set_title("Most reviewers write only one review (job 4 + chained job 4b)")
fig.tight_layout(); fig.savefig(CH / "05_reviewer_activity.png"); plt.close(fig)
# 5. products: best / worst among well-reviewed (>=100 reviews)
best = list(db.mr_products.find({"reviews": {"$gte": 100}}, {"_id": 0, "stars": 0}).sort("avgScore", -1).limit(5)); worst = list(db.mr_products.find({"reviews": {"$gte": 100}}, {"_id": 0, "stars": 0}).sort("avgScore", 1).limit(5))
n_users = db.mr_users.count_documents({}); one = h["01"]["reviewers"]; top_user = db.mr_users.find_one(sort=[("reviews", -1)], projection={"_id": 0})
ins.update({"reviews_total": sum(stars), "star_share_pct": [round(v / sum(stars) * 100, 1) for v in stars], "top_positive_words": [x["word"] for x in top["positive"][:8]], "top_negative_words": [x["word"] for x in top["negative"][:8]], "negative_signal_words": dist[:8],
            "peak_month": max(mo, key=lambda m: m["reviews"]), "avg_score_first_year": round(sum(m["avgScore"] for m in mo[:12]) / 12, 2), "avg_score_last_year": round(sum(m["avgScore"] for m in mo[-12:]) / 12, 2), "reviewers": n_users,
            "one_review_reviewers_pct": round(one / n_users * 100, 1), "most_active_reviewer": top_user, "best_products_ge100_reviews": best, "worst_products_ge100_reviews": worst,
            "products_with_ge100_reviews": db.mr_products.count_documents({"reviews": {"$gte": 100}})})
(ROOT / "results/insights.json").write_text(json.dumps(ins, indent=2, default=str)); print(json.dumps(ins, indent=2, default=str)[:2600]); print("charts:", sorted(p.name for p in CH.glob("*.png")))
