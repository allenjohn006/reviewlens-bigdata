#!/usr/bin/env python3
"""STEP 4 - Insert the cleaned reviews into the NATIVE MongoDB (port 27019) and build indexes.
Uses insert_many in batches of 10 000. Re-running drops the collection first, so it is repeatable."""
import json, os, pathlib, time
from pymongo import MongoClient, ASCENDING
ROOT = pathlib.Path(__file__).resolve().parents[1]
client = MongoClient(os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27019"), serverSelectionTimeoutMS=4000)
print("connected to MongoDB", client.server_info()["version"], "at", client.address)       # fails loudly if mongod is not running
db = client["reviewlens"]; db.reviews.drop(); t0 = time.time(); batch, n = [], 0
with open(ROOT / "data/clean/reviews_clean.jsonl", encoding="utf-8") as f:
    for line in f:
        batch.append(json.loads(line))
        if len(batch) == 10_000: db.reviews.insert_many(batch, ordered=False); n += len(batch); batch = []
if batch: db.reviews.insert_many(batch, ordered=False); n += len(batch)
t_insert = time.time() - t0
for field in ("productId", "userId", "date", "score", "sentiment"): db.reviews.create_index([(field, ASCENDING)])
db.reviews.create_index([("reviewId", ASCENDING)], unique=True)
stats = db.command("collstats", "reviews")
out = {"inserted": n, "count_in_db": db.reviews.count_documents({}), "insert_seconds": round(t_insert, 1), "docs_per_second": round(n / t_insert), "indexes": [i["name"] for i in db.reviews.list_indexes()],
       "storage_mb": round(stats["storageSize"] / 1e6), "avg_doc_bytes": round(stats["avgObjSize"])}
(ROOT / "results/mongo_load.json").write_text(json.dumps(out, indent=2)); print(json.dumps(out, indent=2))
