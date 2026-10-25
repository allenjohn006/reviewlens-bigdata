#!/usr/bin/env python3
"""REDUCER / COMBINER.  Input arrives SORTED BY KEY (Hadoop's shuffle & sort).  Adds up comma-separated numbers per key.
Used as a combiner too: a combiner is a 'mini reducer' that runs on each mapper's output first so far less data crosses the network."""
import sys, os
minimum = float(os.environ.get("MIN_COUNT", 0))        # set only for the reducer (-D mapreduce.reduce.env=MIN_COUNT=20), never for the combiner
cur, acc = None, None
def emit():
    if cur is not None and acc[0] >= minimum: print(cur + "\t" + ",".join(("%d" % x if x == int(x) else "%.4f" % x) for x in acc))
for line in sys.stdin:
    key, _, val = line.rstrip("\n").partition("\t"); nums = [float(x) for x in val.split(",")]
    if key != cur: emit(); cur, acc = key, nums
    else: acc = [a + b for a, b in zip(acc, nums)]
emit()
