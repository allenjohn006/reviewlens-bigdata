#!/usr/bin/env python3
"""JOB 1 - MAPPER.  Input line (tab separated): reviewId productId userId score month helpYes helpTotal body
For every meaningful word in the review emit  'sentiment|word <TAB> 1'.   (The classic word count, split by sentiment.)"""
import sys
from common import STOP, TOKEN, Counters, sentiment
C = Counters("Quality")
for line in sys.stdin:
    p = line.rstrip("\n").split("\t")
    C.inc("lines_read")
    if len(p) != 8: C.inc("malformed_lines_skipped"); continue
    try: s = sentiment(int(p[3]))
    except ValueError: C.inc("bad_score_skipped"); continue
    for w in TOKEN.findall(p[7].lower()):
        if w not in STOP: print(f"{s}|{w}\t1"); C.inc("words_emitted")
C.flush()
