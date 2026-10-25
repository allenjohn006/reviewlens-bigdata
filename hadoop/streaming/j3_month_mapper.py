#!/usr/bin/env python3
"""JOB 3 - MAPPER.  key = month (YYYY-MM), value = 1,score,helpYes,helpTotal  -> reviews per month, average score, helpfulness."""
import sys
from common import Counters
C = Counters("Quality")
for line in sys.stdin:
    p = line.rstrip("\n").split("\t")
    if len(p) != 8: C.inc("malformed_lines_skipped"); continue
    print(f"{p[4]}\t1,{p[3]},{p[5]},{p[6]}")
C.flush()
