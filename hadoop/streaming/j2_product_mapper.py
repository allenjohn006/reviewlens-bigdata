#!/usr/bin/env python3
"""JOB 2 - MAPPER.  key = productId, value = 1,score,star1..star5  (count, score sum and a star histogram)."""
import sys
from common import Counters
C = Counters("Quality")
for line in sys.stdin:
    p = line.rstrip("\n").split("\t"); C.inc("lines_read")
    if len(p) != 8: C.inc("malformed_lines_skipped"); continue
    s = int(p[3]); h = ["0"] * 5; h[s - 1] = "1"
    print(f"{p[1]}\t1,{s},{','.join(h)}")
C.flush()
