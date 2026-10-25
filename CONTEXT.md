# CONTEXT — read this first if you are a new chat / new person

## Who and why
Student (Karunya Institute, B.Tech AI&DS, team project; works on Ubuntu 26.04, 14 GB RAM, 12 cores) needs a **small, simple Big Data project** for course **23DC2044 Big Data Tools and Techniques**. The faculty do **not** care about front end/back end/cloud. They want to **see Hadoop and MapReduce running and understand the database side**, and they want **MongoDB connected natively (not a Docker instance)**. The student has exams and wants to finish early and be able to explain everything themself.

## Rubric (marks 30 + 10 certificate by the student)
Dataset & MapReduce 10 (Kaggle dataset ≥ 50 k records, semi-structured/unstructured preferred, cleaned, correct MapReduce, meaningful results) · NoSQL integration 5 (MongoDB operations verified) · Result 10 (accurate, explained, validated) · Report 5 · PPT 7–10 slides. Decision: **Hadoop does MapReduce; MongoDB only for storage/insert/delete/query** (the handout's "MapReduce in MongoDB" was an error).

## Decisions made (do not re-litigate)
* Project **ReviewLens**, option A: Amazon Fine Food Reviews. Separate small repo (this one), independent of the large **RetailPulse** repo (`~/IA-3`, GitHub `allenjohn006/retailpulse`), which stays as it is.
* Native MongoDB **7.0.14** (tarball in `~/tools/mongodb`, port **27019**, data `~/reviewlens/mongo-data`); **not 8.x** (crashes on kernel 7.0.0-31). Old Docker Mongo (`retailpulse-mongo`) uses 27017 — ignore.
* Hadoop 3.4.3 single node at `~/tools/hadoop` (HDFS :9000, NameNode UI :9870, YARN UI :8088), Java 17, Hadoop Streaming with Python. Daemons stop on reboot: `bash scripts/start_hadoop.sh`.
* MongoDB ⇄ Hadoop through a TSV file (connector discontinued). Python env: `.venv` (3.12, uv).
* Working style: plan first, honest numbers (never invent metrics), log everything, no secrets in files. The student asked for step-by-step explanations they can repeat themselves.

## State (2026-10-25): **built and verified**
Clean 568,454→567,247 · MongoDB loaded (11 s, 7 indexes) · 5 Hadoop runs OK (J1 64 s, J2 24 s, J3 22 s, J4 24 s, J4b 20 s) · results loaded to `mr_*` · validation 5/5 PASS · 5 charts · CRUD demo · 5 unit tests · docs written · screenshots in `evidence/screenshots/`.

## Possible next work
Student rehearses the demo (`docs/PRESENTATION.md`), writes report conclusion in own words, makes the PPT, adds name/ID. Optional: a second small structured job (e.g. Store Sales) if the faculty want structured data too; Java version of one mapper/reducer if they insist on Java; GitHub repo polish.

## How to verify quickly
`source scripts/env.sh && jps && mongosh --port 27019 --eval 'db.getSiblingDB("reviewlens").reviews.countDocuments({})'` → 567247; `python -m pytest tests -q` → 5 passed; `python scripts/08_validate.py` → ALL PASS.
