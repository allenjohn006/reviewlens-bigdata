#!/usr/bin/env python3
"""JOB 2 - REDUCER.  Sum per product, then finish the maths: average score.  out: productId reviews avgScore star1..star5"""
import sys
cur, acc = None, None
def emit():
    if cur is not None: print(f"{cur}\t{int(acc[0])}\t{acc[1] / acc[0]:.4f}\t" + "\t".join(str(int(x)) for x in acc[2:]))
for line in sys.stdin:
    k, _, v = line.rstrip("\n").partition("\t"); n = [float(x) for x in v.split(",")]
    if k != cur: emit(); cur, acc = k, n
    else: acc = [a + b for a, b in zip(acc, n)]
emit()
