# Presentation kit (9 slides + live demo + viva answers)

## Slides (7–10 required)
1. **Title & problem** — ReviewLens; "What do customers of online food shops say, and how can we find out from 567 thousand reviews?"
2. **Objectives** — process semi-structured reviews with Hadoop MapReduce; store/query with MongoDB; validate; draw insights.
3. **Dataset** — Kaggle Amazon Fine Food Reviews: 568,454 reviews, 74 k products, 256 k reviewers, 1999–2012, CC0.
4. **Cleaning** — table from report §5 (−1,207 rows; 146,636 HTML cleaned).
5. **Tools & architecture** — the data-flow diagram: MongoDB (storage) ⇄ HDFS/MapReduce (processing); native, no Docker (insert `dashboard/pipeline_architecture.png`).
6. **MapReduce method** — job table + the word-count shuffle picture + combiner (−96 %) + counters.
7. **MongoDB integration** — 567,247 inserts, 7 indexes, CRUD, `explain` about 1–3 ms vs about 260 ms.
8. **Results** — charts 01–05 (2–3 per slide as space allows) + key numbers + live Streamlit Dashboard demo (`http://localhost:8501`).
9. **Validation, limitations, conclusion** — 5/5 PASS; honest limits; future work. (+ References.)

## Live demo (10 minutes) — Two presentation options

### Option 1: Visual Interactive Presentation (Streamlit Dashboard)
Start the dashboard: `bash dashboard/start_dashboard.sh` and open `http://localhost:8501`.
1. **Main Landing:** Show the programmatically generated Pipeline Architecture diagram and system summary metrics (567k docs, 283 MB HDFS, 5 jobs).
2. **Page 1 (Dataset):** Show raw vs clean review statistics, cleaning logs, and sample review JSONs.
3. **Page 2 (MapReduce):** Walk through the 5 jobs, mapper/reducer logic, YARN runtimes, and the 96% combiner reduction.
4. **Page 3 (MongoDB):** Show native MongoDB status, 7 collections, index configurations, and index benchmark.
5. **Page 4 (Insights):** Present the 5 interactive Plotly charts (Rating Distribution, Polarizing Words, Monthly Volume/Rating Trend, Long-tail Reviewer Activity, Top Products).
6. **Page 5 (Validation):** Demonstrate the 5/5 PASS zero-mismatch independent pandas validation table.
7. **Page 6 (Live Demo):** Run live MongoDB queries in front of faculty: CRUD actions, aggregation pipeline, and the live `explain()` demonstrating index performance (1–3 ms vs 260 ms).

### Option 2: Command-Line and Terminal Verification
If faculty request seeing the terminal, cluster daemons, and low-level commands:
```bash
cd ~/reviewlens && source scripts/env.sh
bash scripts/start_hadoop.sh              # 1. Hadoop daemons;   jps  -> 4 daemons (NameNode, DataNode, RM, NM)
bash scripts/03_start_mongo.sh            # 2. native MongoDB;   ps aux | grep mongod ; ls mongo-data
mongosh --port 27019                      # 3. show dbs; use reviewlens; show collections; db.reviews.countDocuments({}); db.reviews.findOne()
hdfs dfs -ls -h /reviewlens/raw           # 4. the data in HDFS;  browser: localhost:9870 -> Browse the file system (3 blocks)
bash scripts/run_job.sh J3_monthly_volume /reviewlens/raw/reviews.tsv j3_month_mapper.py sum_reducer.py sum_reducer.py     # 5. run a job LIVE (~25 s); open localhost:8088 meanwhile
head results/mr/J3_monthly_volume.tsv     # 6. the output
python scripts/08_validate.py             # 7. validation ALL PASS (about 1-2 min; or show results/validation_report.json)
python scripts/10_mongo_crud_demo.py      # 8. insert / find / update / delete / explain
```
Safety net if something fails: every output already exists in `results/` and `evidence/` (logs, screenshots, charts).

## Likely viva questions and short answers
| Question | Answer |
|---|---|
| What is Hadoop? | A framework that stores huge files across machines (HDFS) and processes them in parallel (MapReduce) with YARN managing resources. |
| What is HDFS? Why blocks? | Distributed file system; files are cut into 128 MB blocks, spread over DataNodes and tracked by the NameNode. Blocks allow parallel processing (one mapper per block) and replication. Ours: 3 blocks, replication 1 (one machine). |
| Explain MapReduce | Map turns each input line into key-value pairs; shuffle & sort groups all values of a key to one reducer; reduce combines them. Example: word count. |
| What is a combiner? | A mini-reducer on each mapper's output before the shuffle: 22.8 M pairs → 950 k in job 1. |
| What does YARN do? | Resource manager: allocates CPU/memory containers to jobs; NodeManager runs the tasks. |
| Why Python / Streaming? | Hadoop Streaming runs any program that reads stdin and writes `key<TAB>value`; same model as Java MapReduce, faster to write. |
| Where exactly is MapReduce in your project? | `hadoop/streaming/*.py` (mappers/reducers) executed by `scripts/run_job.sh` through `hadoop-streaming-3.4.3.jar` on YARN; logs in `evidence/hadoop/`. |
| Why MongoDB? What does it do here? | NoSQL document store: holds the cleaned reviews (JSON documents) and the MapReduce results; supports insert/find/update/delete, indexes, aggregation. |
| Why not Docker? | Faculty asked for a direct connection: `mongod` runs as a normal process with data in `~/reviewlens/mongo-data`; PyMongo/`mongosh` connect to `127.0.0.1:27019`. |
| How are MongoDB and Hadoop connected? | Through a file: export from MongoDB → HDFS → jobs → results → loaded back. The official MongoDB-Hadoop connector is discontinued. |
| Why is this "big data"? | 567 k reviews, 283 MB text, 22.8 M words processed; the same code scales to the 14 M-review set (6 GB) used in RetailPulse. Honest: it is a mini-cluster on one machine. |
| How do you know the results are right? | Independent pandas recomputation, 5/5 checks, zero mismatches; unit tests. |
| What is an index? | A sorted lookup structure; the product query examined 913 docs (about 1–3 ms) instead of 567,247 (about 260 ms). |
| What did cleaning change? | −1,205 duplicates, −2 impossible rows, 146,636 HTML-stripped, 53 nulls filled. |
| What are the limits? | Single node; frequency ≠ sentiment; variant-copied reviews remain; data from 1999–2012. |
| What are speculative tasks? | Hadoop starts a duplicate attempt of a slow task and keeps whichever finishes first; J1 had 2 killed attempts. |
| What is a counter? | A cluster-wide tally (e.g. lines read, malformed lines) reported in the job summary. |
