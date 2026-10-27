# CONTEXT — ReviewLens Project Handoff & Technical Overview

## Who and Why
Student (Karunya Institute, B.Tech AI&DS, team project; running inside **WSL2 / Ubuntu on Windows**, 14 GB RAM, 12 cores) needs an end-to-end Big Data project for course **23DC2044 Big Data Tools and Techniques**.
The faculty requirement: **demonstrate Hadoop MapReduce running on YARN, connect native MongoDB directly (not in Docker), validate accuracy, and present business insights.**

## Rubric Alignment (Marks: 30 + 10 Certificate)
* **Dataset & MapReduce (10 marks):** Kaggle *Amazon Fine Food Reviews* (568,454 rows, 11.3x required 50k minimum). Cleaned to 567,247 records with a complete audit log. 5 MapReduce jobs with combiners and counters on Hadoop YARN.
* **NoSQL Integration (5 marks):** Native MongoDB 7.0.14 running on port **27019** (isolated from Docker on 27017). 567,247 documents loaded in 9.4s, 7 indexes, full CRUD operations, and `explain()` benchmark (2 ms indexed vs 188 ms table scan).
* **Result & Accuracy (10 marks):** 5/5 validation checks PASS with **0 mismatches across 365,008 keys** against independent Pandas recomputations. 5 analytical figures and insights report.
* **Report (5 marks):** Comprehensive draft prepared in `docs/REPORT_DRAFT.md`.
* **Presentation (7–10 slides):** Structured outline and live demo script in `docs/PRESENTATION.md`.
* **Certificate (10 marks):** MongoDB Skills course certificate provided by student.

## Architecture Decisions Made
* **Decoupled Architecture:** Hadoop does MapReduce; MongoDB handles storage, indexing, and transactional/analytical queries.
* **Native MongoDB 7.0.14:** Standalone process running on port **27019** with physical files in `mongo-data/` (not Docker). MongoDB 7.0 is selected because MongoDB 8.x crashes on Linux kernel 7.0.
* **Hadoop 3.4.3 on YARN:** Single-node pseudo-distributed cluster (`HADOOP_HOME=~/tools/hadoop`, HDFS on `:9000`, NameNode UI on `:9870`, YARN UI on `:8088`). Java 17, Hadoop Streaming via Python.
* **File Exchange:** MongoDB and Hadoop exchange data via tab-separated values (`reviews.tsv`) in HDFS because the legacy MongoDB-Hadoop connector was deprecated by MongoDB.
* **Streamlit UI Dashboard:** Multi-page interactive application on `http://localhost:8501` featuring telemetry, live query workbench, index benchmarks, and publication-grade architecture diagram.
* **Git Repository:** Synchronized to `https://github.com/allenjohn006/reviewlens-bigdata.git` on branches `main` and `alnx`.

## Current System State (Verified Active)
1. **WSL Environment:** Cleaned Unix LF line endings across all scripts and configurations.
2. **Native MongoDB 7.0:** Active on port 27019 with 567,247 documents loaded in `reviewlens.reviews` and 6 `mr_*` result marts.
3. **Hadoop Daemons:** All 4 services active (`NameNode`, `DataNode`, `ResourceManager`, `NodeManager`).
4. **Streamlit UI:** Active on `http://localhost:8501`.
5. **Testing & Validation:** 5/5 unit tests pass in 0.19s; 5/5 ground-truth validation checks PASS with 0 mismatches.

## Quick Health Check
```bash
source scripts/env.sh
jps                                    # Should list NameNode, DataNode, ResourceManager, NodeManager
mongosh --port 27019 --eval 'db.getSiblingDB("reviewlens").reviews.countDocuments({})'  # Returns 567247
python -m pytest tests -q              # Returns: 5 passed in 0.19s
python scripts/08_validate.py          # Returns: ALL PASS
curl -sI http://localhost:8501         # Returns: HTTP/1.1 200 OK
```
