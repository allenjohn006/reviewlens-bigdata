# Plan (executed) — ReviewLens

| # | Step | Script | Done |
|---|---|---|---|
| 0 | Install Java, Hadoop 3.4.3, native MongoDB 7.0, Python env, Kaggle token | STEP_BY_STEP Part A | ✔ |
| 1 | Download Kaggle dataset | `01_download.sh` | ✔ |
| 2 | Clean + cleaning log | `02_clean.py` | ✔ |
| 3 | Start native MongoDB | `03_start_mongo.sh` | ✔ |
| 4 | Insert into MongoDB, indexes | `04_load_mongo.py` | ✔ |
| 5 | Export → HDFS | `05_export_to_hdfs.py` | ✔ |
| 6 | MapReduce jobs J1–J4b | `06_run_jobs.sh`, `hadoop/streaming/` | ✔ |
| 7 | Results → MongoDB | `07_load_results.py` | ✔ |
| 8 | Independent validation | `08_validate.py` | ✔ |
| 9 | Analysis + charts | `09_analysis_and_charts.py` | ✔ |
| 10 | CRUD / aggregation / explain demo | `10_mongo_crud_demo.py` | ✔ |
| 11 | Tests, docs, report, presentation | `tests/`, `docs/` | ✔ |
| 12 | Streamlit interactive UI dashboard (6 pages) | `dashboard/`, `start_dashboard.sh` | ✔ |
| 13 | High-res architecture diagram generator | `scripts/generate_architecture_diagram.py` | ✔ |
| 14 | GitHub repository sync & release | `git push origin main, alnx` | ✔ |

Design choices: one dataset (text → semi-structured) · few jobs, each teaching one idea (word count, aggregation by key, time series, long-tail + job chaining) · Mongo = storage only · everything scripted and repeatable · every number produced by a script.
Effort for the student: ~½ day to read STEP_BY_STEP and rehearse, ~½ day for report + slides.
