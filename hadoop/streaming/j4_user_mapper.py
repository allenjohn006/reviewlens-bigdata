#!/usr/bin/env python3
"""JOB 4 - MAPPER.  key = userId, value = 1  -> how many reviews each reviewer wrote."""
import sys
for line in sys.stdin:
    p = line.rstrip("\n").split("\t")
    if len(p) == 8: print(f"{p[2]}\t1")
