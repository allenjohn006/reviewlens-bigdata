#!/usr/bin/env python3
"""STEP 10 - MongoDB CRUD demo on the NATIVE server: Create, Read, Update, Delete + aggregation + index/explain. Prints a readable transcript (also saved to evidence/mongo/crud_demo.txt)."""
import os, pprint, pathlib, sys, io, time
from pymongo import MongoClient
ROOT = pathlib.Path(__file__).resolve().parents[1]; buf = io.StringIO()
def say(*a):
    s = " ".join(str(x) for x in a); print(s); buf.write(s + "\n")
c = MongoClient(os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27019")); db = c.reviewlens; R = db.reviews
say(f"== Connected to MongoDB {c.server_info()['version']} at {c.address} (native process, not Docker). Database: reviewlens, collections: {sorted(db.list_collection_names())}")
say(f"   reviews in collection: {R.count_documents({})}")
say("\n== CREATE  (insert_one / insert_many)")
R.delete_many({"productId": "B000DEMO01"})          # make the demo repeatable
base = {"reviewId": 9000001, "productId": "B000DEMO01", "userId": "ADEMOUSER", "profileName": "viva demo", "helpYes": 0, "helpTotal": 0, "score": 5, "sentiment": "positive", "date": "2026-10-25", "month": "2026-10", "summary": "Demo review", "text": "Inserted live during the viva."}
say("insert_one ->", R.insert_one(dict(base)).inserted_id)       # dict(base): PyMongo adds an _id to the dict it inserts
many = [{**base, "reviewId": 9000002 + i, "score": s, "sentiment": "negative" if s <= 2 else "neutral" if s == 3 else "positive", "summary": f"Demo {i}"} for i, s in enumerate((1, 3, 4))]
say("insert_many ->", len(R.insert_many(many).inserted_ids), "documents")
say("\n== READ  (find / count / aggregate)")
say("find_one reviewId=9000001 ->"); pprint.pprint(R.find_one({"reviewId": 9000001}, {"_id": 0}), stream=buf); pprint.pprint(R.find_one({"reviewId": 9000001}, {"_id": 0}))
say("demo reviews by sentiment:", {d["_id"]: d["n"] for d in R.aggregate([{"$match": {"productId": "B000DEMO01"}}, {"$group": {"_id": "$sentiment", "n": {"$sum": 1}}}])})
say("5-star reviews in the whole collection:", R.count_documents({"score": 5}))
say("Top 5 products with >= 200 reviews by average score (aggregation pipeline straight on the 567k reviews):")
for d in R.aggregate([{"$group": {"_id": "$productId", "n": {"$sum": 1}, "avg": {"$avg": "$score"}}}, {"$match": {"n": {"$gte": 200}}}, {"$sort": {"avg": -1}}, {"$limit": 5}]): say(f"   {d['_id']}  reviews={d['n']}  avg={d['avg']:.3f}")
say("\n== UPDATE  (update_one / update_many)")
say("update_one helpYes += 2 ->", R.update_one({"reviewId": 9000001}, {"$inc": {"helpYes": 2, "helpTotal": 2}}).modified_count, "modified")
say("update_many set flag on demo docs ->", R.update_many({"productId": "B000DEMO01"}, {"$set": {"demo": True}}).modified_count, "modified")
say("after update:", R.find_one({"reviewId": 9000001}, {"_id": 0, "helpYes": 1, "helpTotal": 1, "demo": 1}))
say("\n== DELETE  (delete_one / delete_many)")
say("delete_one ->", R.delete_one({"reviewId": 9000001}).deleted_count); say("delete_many demo product ->", R.delete_many({"productId": "B000DEMO01"}).deleted_count); say("reviews now:", R.count_documents({}))
say("\n== INDEX  (why indexes matter: explain with and without the productId index)")
q = {"productId": "B007JFMH8M"}
for label, hint in (("WITH index   ", {"productId": 1}), ("WITHOUT index ", {"$natural": 1})):
    t = time.time(); e = R.find(q).hint(list(hint.items())).explain()["executionStats"]; say(f"   {label} -> docs examined={e['totalDocsExamined']:>7}  returned={e['nReturned']:>4}  server time={e['executionTimeMillis']} ms")
say("   index list:", [i["name"] for i in R.list_indexes()])
(ROOT / "evidence/mongo").mkdir(parents=True, exist_ok=True); (ROOT / "evidence/mongo/crud_demo.txt").write_text(buf.getvalue())
