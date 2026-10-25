#!/usr/bin/env python3
"""STEP 8 - VALIDATION: recompute every MapReduce result with a DIFFERENT method (pandas / Counter on the cleaned file, not Hadoop) and compare key by key."""
import collections, json, pathlib, re, sys
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "hadoop/streaming")); from common import STOP, TOKEN
df = pd.read_json(ROOT / "data/clean/reviews_clean.jsonl", lines=True, dtype={"productId": str, "userId": str})
def mr(name): return [l.rstrip("\n").split("\t") for l in open(ROOT / f"results/mr/{name}.tsv", encoding="utf-8")]
checks = []
def compare(name, hadoop, mine, tol=1e-6):
    only_h = [k for k in hadoop if k not in mine]; only_m = [k for k in mine if k not in hadoop]; bad = []
    for k in hadoop.keys() & mine.keys():
        a, b = hadoop[k], mine[k]
        if max(abs(x - y) for x, y in zip(a, b)) > tol * max(1, max(abs(x) for x in a)): bad.append((k, a, b))
    ok = not (only_h or only_m or bad); checks.append({"check": name, "keys": len(hadoop), "missing_in_hadoop": len(only_m), "extra_in_hadoop": len(only_h), "mismatches": len(bad), "status": "PASS" if ok else "FAIL", "examples": bad[:3]})
    print(("PASS" if ok else "FAIL"), name, f"({len(hadoop)} keys, {len(bad)} mismatches)")
# J1 words by sentiment (threshold 20 is part of the job definition)
cnt = collections.Counter()
for s, t, x in zip(df.sentiment, df.summary + " . " + df.text, df.score):
    for w in TOKEN.findall(t.lower()):
        if w not in STOP: cnt[(s, w)] += 1
compare("J1 word counts by sentiment (>=20)", {f"{a}|{b}": [float(c)] for a, b, c in [(k.split('|')[0], k.split('|')[1], v) for k, v in [(r[0], r[1]) for r in mr("J1_sentiment_words")]]}, {f"{s}|{w}": [float(c)] for (s, w), c in cnt.items() if c >= 20})
g = df.groupby("productId").agg(n=("score", "size"), avg=("score", "mean")); st = df.groupby(["productId", "score"]).size().unstack(fill_value=0).reindex(columns=[1, 2, 3, 4, 5], fill_value=0)
compare("J2 per-product reviews, average, star histogram", {r[0]: [float(r[1]), float(r[2])] + [float(x) for x in r[3:8]] for r in mr("J2_product_stats")}, {p: [float(g.n[p]), round(float(g.avg[p]), 4)] + [float(x) for x in st.loc[p]] for p in g.index}, tol=1e-4)
m = df.groupby("month").agg(n=("score", "size"), s=("score", "sum"), hy=("helpYes", "sum"), ht=("helpTotal", "sum"))
compare("J3 monthly reviews, score sum, helpful votes", {r[0]: [float(x) for x in r[1].split(",")] for r in mr("J3_monthly_volume")}, {k: [float(r.n), float(r.s), float(r.hy), float(r.ht)] for k, r in m.iterrows()})
u = df.groupby("userId").size(); compare("J4 reviews per reviewer", {r[0]: [float(r[1])] for r in mr("J4_reviewer_activity")}, {k: [float(v)] for k, v in u.items()})
bk = lambda n: "01" if n == 1 else "02" if n == 2 else "03-05" if n <= 5 else "06-10" if n <= 10 else "11-20" if n <= 20 else "21-50" if n <= 50 else "51+"
h = u.map(bk).value_counts(); hs = u.groupby(u.map(bk)).sum()
compare("J4b reviewer-activity histogram", {r[0]: [float(x) for x in r[1].split(",")] for r in mr("J4b_activity_histogram")}, {k: [float(h[k]), float(hs[k])] for k in h.index})
rep = {"all_pass": all(c["status"] == "PASS" for c in checks), "rows_validated": int(len(df)), "checks": checks}
(ROOT / "results/validation_report.json").write_text(json.dumps(rep, indent=2)); print("ALL PASS" if rep["all_pass"] else "SOME FAILED")
