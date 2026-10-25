#!/usr/bin/env python3
"""STEP 7 - Load the MapReduce outputs (results/mr/*.tsv) and the Hadoop job statistics (evidence/hadoop/*.log) into MongoDB collections."""
import glob, os, pathlib, re
from pymongo import MongoClient
ROOT = pathlib.Path(__file__).resolve().parents[1]; MR = ROOT / "results/mr"
db = MongoClient(os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27019"))["reviewlens"]
def rows(name): return (l.rstrip("\n").split("\t") for l in open(MR / f"{name}.tsv", encoding="utf-8"))
def put(coll, docs):
    db[coll].drop(); docs = list(docs); db[coll].insert_many(docs); return len(docs)
out = {}
out["mr_words"] = put("mr_words", ({"sentiment": k.split("|")[0], "word": k.split("|")[1], "count": int(float(v))} for k, v in rows("J1_sentiment_words")))
out["mr_products"] = put("mr_products", ({"productId": p[0], "reviews": int(p[1]), "avgScore": float(p[2]), "stars": [int(x) for x in p[3:8]]} for p in rows("J2_product_stats")))
def month(p): v = [float(x) for x in p[1].split(",")]; return {"month": p[0], "reviews": int(v[0]), "avgScore": round(v[1] / v[0], 4), "helpYes": int(v[2]), "helpTotal": int(v[3])}
out["mr_months"] = put("mr_months", (month(p) for p in rows("J3_monthly_volume")))
out["mr_users"] = put("mr_users", ({"userId": p[0], "reviews": int(float(p[1]))} for p in rows("J4_reviewer_activity")))
out["mr_activity_hist"] = put("mr_activity_hist", ({"bucket": p[0], "reviewers": int(float(p[1].split(",")[0])), "reviews": int(float(p[1].split(",")[1]))} for p in rows("J4b_activity_histogram")))
for coll, key in (("mr_words", "word"), ("mr_products", "productId"), ("mr_months", "month"), ("mr_users", "userId")): db[coll].create_index(key)
db.mr_words.create_index([("sentiment", 1), ("count", -1)]); db.mr_products.create_index([("reviews", -1)])
jobs = []
for f in sorted(glob.glob(str(ROOT / "evidence/hadoop/J*.log"))):
    t = open(f).read(); g = lambda pat: (int(re.search(pat, t).group(1)) if re.search(pat, t) else None); ex = re.search(r"# exit=(\d+) elapsed_s=(\d+)", t)
    jobs.append({"job": pathlib.Path(f).stem, "exit": int(ex.group(1)), "elapsedSeconds": int(ex.group(2)), "mapInput": g(r"Map input records=(\d+)"), "mapOutput": g(r"Map output records=(\d+)"), "combineInput": g(r"Combine input records=(\d+)"),
                 "combineOutput": g(r"Combine output records=(\d+)"), "reduceInput": g(r"Reduce input records=(\d+)"), "reduceOutput": g(r"Reduce output records=(\d+)"), "maps": g(r"Launched map tasks=(\d+)"), "reduces": g(r"Launched reduce tasks=(\d+)"),
                 "hdfsBytesRead": g(r"HDFS: Number of bytes read=(\d+)")})
out["mr_jobs"] = put("mr_jobs", jobs); import json; (ROOT / "results/mongo_results_load.json").write_text(json.dumps(out, indent=2)); print(out)
