#!/usr/bin/env python3
"""JOB 4b (CHAINED: reads the OUTPUT of job 4) - MAPPER.  Turns 'userId <TAB> n_reviews' into a histogram bucket."""
import sys
def bucket(n): return "01" if n == 1 else "02" if n == 2 else "03-05" if n <= 5 else "06-10" if n <= 10 else "11-20" if n <= 20 else "21-50" if n <= 50 else "51+"
for line in sys.stdin:
    u, n = line.rstrip("\n").split("\t"); print(f"{bucket(int(float(n)))}\t1,{n}")
