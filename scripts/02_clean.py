#!/usr/bin/env python3
"""STEP 2 - Clean the raw Kaggle file and write one JSON document per line (semi-structured, ready for MongoDB).
Every row that is changed or dropped is COUNTED and the counts are saved in results/cleaning_log.json (the 'cleaning log' the rubric asks for)."""
import json, re, pathlib, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
raw = pd.read_csv(ROOT / "data/raw/Reviews.csv", dtype={"ProductId": "string", "UserId": "string"})
log = {"rows_in": int(len(raw))}
# 1. missing values: profile name / summary are optional -> fill with empty text; ids and text are mandatory
log["null_profile_name_filled"] = int(raw.ProfileName.isna().sum()); log["null_summary_filled"] = int(raw.Summary.isna().sum())
raw["ProfileName"] = raw.ProfileName.fillna(""); raw["Summary"] = raw.Summary.fillna("")
mandatory = raw[["ProductId", "UserId", "Score", "Time", "Text"]].isna().any(axis=1); log["dropped_missing_mandatory"] = int(mandatory.sum()); raw = raw[~mandatory]
# 2. impossible values: helpful votes cannot exceed total votes; score must be 1..5
bad_help = raw.HelpfulnessNumerator > raw.HelpfulnessDenominator; log["dropped_helpful_gt_total"] = int(bad_help.sum()); raw = raw[~bad_help]
bad_score = ~raw.Score.between(1, 5); log["dropped_score_out_of_range"] = int(bad_score.sum()); raw = raw[~bad_score]
# 3. exact duplicates: same user + product + time + text
dup = raw.duplicated(["UserId", "ProductId", "Time", "Text"]); log["dropped_exact_duplicates"] = int(dup.sum()); raw = raw[~dup]
# 4. text hygiene: strip HTML tags (<br />), collapse whitespace/newlines/tabs so one review = one line
tag = re.compile(r"<[^>]+>"); ws = re.compile(r"\s+")
log["reviews_with_html_tags_cleaned"] = int(raw.Text.str.contains(tag).sum())
clean = lambda s: ws.sub(" ", tag.sub(" ", s)).strip()
raw["Text"] = raw.Text.map(clean); raw["Summary"] = raw.Summary.map(clean)
empty = raw.Text == ""; log["dropped_empty_text_after_cleaning"] = int(empty.sum()); raw = raw[~empty]
# 5. derived fields used later (sentiment bucket, calendar date)
date = pd.to_datetime(raw.Time, unit="s"); raw["date"] = date.dt.strftime("%Y-%m-%d"); raw["month"] = date.dt.strftime("%Y-%m")
raw["sentiment"] = pd.cut(raw.Score, [0, 2, 3, 5], labels=["negative", "neutral", "positive"]).astype(str)
log["rows_out"] = int(len(raw)); log["rows_removed_total"] = log["rows_in"] - log["rows_out"]; log["products"] = int(raw.ProductId.nunique()); log["users"] = int(raw.UserId.nunique())
log["date_min"], log["date_max"] = raw.date.min(), raw.date.max(); log["sentiment_counts"] = raw.sentiment.value_counts().to_dict()
out = ROOT / "data/clean/reviews_clean.jsonl"
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    for r in raw.itertuples(index=False):
        f.write(json.dumps({"reviewId": int(r.Id), "productId": r.ProductId, "userId": r.UserId, "profileName": r.ProfileName, "helpYes": int(r.HelpfulnessNumerator), "helpTotal": int(r.HelpfulnessDenominator),
                            "score": int(r.Score), "sentiment": r.sentiment, "date": r.date, "month": r.month, "summary": r.Summary, "text": r.Text}, ensure_ascii=False) + "\n")
(ROOT / "results").mkdir(exist_ok=True); (ROOT / "results/cleaning_log.json").write_text(json.dumps(log, indent=2))
print(json.dumps(log, indent=2)); print("wrote", out, f"({out.stat().st_size / 1e6:.0f} MB)")
