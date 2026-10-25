"""Unit tests for the MapReduce logic: each job is run as  mapper | sort | reducer  - exactly what Hadoop does, minus the cluster."""
import os, subprocess, sys, pathlib
S = pathlib.Path(__file__).resolve().parents[1] / "hadoop/streaming"; PY = sys.executable
def run(mapper, reducer, text, env=None):
    e = {**os.environ, "PYTHONPATH": str(S), **(env or {})}
    m = subprocess.run([PY, str(S / mapper)], input=text, capture_output=True, text=True, env=e, check=True)
    r = subprocess.run([PY, str(S / reducer)], input="\n".join(sorted(m.stdout.splitlines())) + "\n", capture_output=True, text=True, env=e, check=True)
    return m, [l.split("\t") for l in r.stdout.splitlines()]
def row(i, product, user, score, month, body, hy=0, ht=0): return f"{i}\t{product}\t{user}\t{score}\t{month}\t{hy}\t{ht}\t{body}\n"
DATA = row(1, "P1", "U1", 5, "2010-01", "Great coffee, great taste", 3, 4) + row(2, "P1", "U2", 1, "2010-01", "Terrible stale coffee", 0, 2) + row(3, "P2", "U1", 3, "2010-02", "average tea") + "broken line without tabs\n"

def test_job1_counts_words_per_sentiment_and_drops_stopwords():
    m, out = run("j1_words_mapper.py", "sum_reducer.py", DATA); d = {r[0]: int(float(r[1])) for r in out}
    assert d["positive|great"] == 2 and d["positive|coffee"] == 1 and d["negative|coffee"] == 1 and d["negative|stale"] == 1 and d["neutral|average"] == 1
    assert not any(k.endswith("|the") or k.endswith("|and") for k in d)
    assert "Quality,malformed_lines_skipped,1" in m.stderr                       # the broken line is counted, not crashed on

def test_job1_minimum_count_applies_only_to_the_reducer():
    _, out = run("j1_words_mapper.py", "sum_reducer.py", DATA, env={"MIN_COUNT": "2"})
    assert [r[0] for r in out] == ["positive|great"]

def test_job2_product_average_and_star_histogram():
    _, out = run("j2_product_mapper.py", "j2_product_reducer.py", DATA); d = {r[0]: r for r in out}
    assert d["P1"][1:3] == ["2", "3.0000"] and d["P1"][3:] == ["1", "0", "0", "0", "1"] and d["P2"][1] == "1"

def test_job3_monthly_totals():
    _, out = run("j3_month_mapper.py", "sum_reducer.py", DATA); d = {r[0]: [float(x) for x in r[1].split(",")] for r in out}
    assert d["2010-01"] == [2, 6, 3, 6] and d["2010-02"] == [1, 3, 0, 0]

def test_job4_reviews_per_user_then_histogram_chain():
    _, per_user = run("j4_user_mapper.py", "sum_reducer.py", DATA); assert {r[0]: int(float(r[1])) for r in per_user} == {"U1": 2, "U2": 1}
    text = "".join(f"{u}\t{n}\n" for u, n in per_user)
    _, hist = run("j4b_hist_mapper.py", "sum_reducer.py", text); assert {r[0]: r[1] for r in hist} == {"01": "1,1", "02": "1,2"}
