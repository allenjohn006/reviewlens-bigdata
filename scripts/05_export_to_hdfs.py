#!/usr/bin/env python3
"""STEP 5 - MongoDB -> text file -> HDFS.  MongoDB is the storage; Hadoop reads plain text files from HDFS (the MongoDB-Hadoop connector is discontinued).
One review per line, tab separated: reviewId productId userId score month helpYes helpTotal body(summary + text)."""
import os, pathlib, subprocess
from pymongo import MongoClient
ROOT = pathlib.Path(__file__).resolve().parents[1]; out = ROOT / "data/clean/reviews.tsv"
db = MongoClient(os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27019"))["reviewlens"]; n = 0
proj = {"_id": 0, "reviewId": 1, "productId": 1, "userId": 1, "score": 1, "month": 1, "helpYes": 1, "helpTotal": 1, "summary": 1, "text": 1}
with open(out, "w", encoding="utf-8") as f:
    for d in db.reviews.find({}, proj).sort("reviewId", 1):
        body = (d["summary"] + " . " + d["text"]).replace("\t", " ").replace("\n", " ")
        f.write(f'{d["reviewId"]}\t{d["productId"]}\t{d["userId"]}\t{d["score"]}\t{d["month"]}\t{d["helpYes"]}\t{d["helpTotal"]}\t{body}\n'); n += 1
print(f"exported {n} reviews from MongoDB to {out} ({out.stat().st_size / 1e6:.0f} MB)")
