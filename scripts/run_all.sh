#!/usr/bin/env bash
# Runs the WHOLE pipeline end to end (each step is also a separate script - see docs/STEP_BY_STEP.md).
set -e; cd "$(dirname "$0")/.."; source scripts/env.sh
bash scripts/03_start_mongo.sh                       # native MongoDB 7.0 on port 27019
bash scripts/start_hadoop.sh                         # HDFS + YARN (skips daemons that are already running)
[ -f data/raw/Reviews.csv ] || bash scripts/01_download.sh
$PY scripts/02_clean.py                              # clean -> data/clean/reviews_clean.jsonl + results/cleaning_log.json
$PY scripts/04_load_mongo.py                         # insert into MongoDB
$PY scripts/05_export_to_hdfs.py && hdfs dfs -mkdir -p /reviewlens/raw && hdfs dfs -put -f data/clean/reviews.tsv /reviewlens/raw/
bash scripts/06_run_jobs.sh                          # the MapReduce jobs
$PY scripts/07_load_results.py                       # results -> MongoDB
$PY scripts/08_validate.py                           # independent check
$PY scripts/09_analysis_and_charts.py                # charts
$PY scripts/10_mongo_crud_demo.py                    # insert / find / update / delete / explain
