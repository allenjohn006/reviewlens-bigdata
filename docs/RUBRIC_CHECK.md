# Rubric check — Big Data Tools and Techniques (23DC2044)

*Source: the course rubric as summarised in `RetailPulse_Three_Subject_Rubric_Alignment_Report.docx` (the scanned rubric itself is not in the repo). Your faculty's two stated asks: **see Hadoop/MapReduce actually run**, and **MongoDB connected natively (not in Docker)**. Per your instruction MapReduce is done by **Hadoop**; MongoDB is used for storage only (insert/delete/update/query).*

| Criterion (marks) | What is needed | ReviewLens evidence | Where |
|---|---|---|---|
| **Dataset & MapReduce (10)** | Relevant Kaggle dataset ≥ 50 k records, semi-structured preferred; cleaned; MapReduce implemented correctly with meaningful results | Kaggle *Amazon Fine Food Reviews*: **568,454 text reviews** → 567,247 after cleaning (cleaning log with counts). **5 MapReduce runs** on Hadoop (word count by sentiment, product statistics, monthly trend, reviewer activity, chained histogram) with combiners and counters | `results/cleaning_log.json`, `hadoop/streaming/`, `evidence/hadoop/*.log` |
| **NoSQL integration (5)** | Successful integration with a NoSQL DB, operations verified | **Native MongoDB 7.0.14** (own process, own data folder, port 27019, no Docker). 567,247 documents inserted (11 s), 7 indexes, `mr_*` result collections, live **insert / find / update / delete**, aggregation pipeline, `explain()` (about 1–3 ms vs about 260 ms) | `evidence/mongo/crud_demo.txt`, `results/mongo_load.json` |
| **Result (10)** | Accurate output, explained, validated, insights | **5/5 validation checks PASS, 0 mismatches** against an independent pandas recomputation; 5 charts; written insights and limits; **Streamlit multi-page dashboard** (`http://localhost:8501`) with Plotly charts and live query execution; high-resolution **pipeline architecture diagram** (`dashboard/pipeline_architecture.png`) | `results/validation_report.json`, `results/charts/`, `dashboard/`, `evidence/` |
| **Report (5)** | Clear, structured: provenance, preprocessing, method, pseudocode, outputs, DB integration, validation, figures, citations | Full draft ready to paste into Word | `docs/REPORT_DRAFT.md` |
| PPT 7–10 slides | Title/problem, objectives, dataset, cleaning, tools, MapReduce method, architecture, results/validation, conclusion, references | 9-slide outline + live-demo script | `docs/PRESENTATION.md` |
| Certificate (10) | MongoDB skills course | **You** | — |

## What the faculty can see live
1. `jps` → NameNode, DataNode, ResourceManager, NodeManager (Hadoop running on your machine).
2. http://localhost:9870 file browser → `/reviewlens/raw/reviews.tsv` in **3 blocks**.
3. A job running (`bash scripts/run_job.sh …`) while http://localhost:8088 shows it → mappers, reducers, counters, final output.
4. `mongosh --port 27019` → `show collections`, `countDocuments`, insert/update/delete.
5. `ps aux | grep mongod` → plain host process (not Docker); `ls mongo-data`.
6. Streamlit Interactive Dashboard (`http://localhost:8501`) → Professional 6-page interface presenting the entire pipeline, architecture diagram, interactive Plotly visualizations, live MongoDB CRUD/aggregation demo, and validation proof.

## Honest limitations (say them before they ask)
* Hadoop Streaming uses Python, not Java — same MapReduce model (map → shuffle/sort → reduce).
* Single-node "pseudo-distributed" cluster on one laptop: real HDFS/YARN software, but no multi-machine speed-up.
* MongoDB and Hadoop exchange data through a text file (the official connector is discontinued).
* Word frequency is not sentiment ("good" is common in negative reviews because of "not good").
* 173 k reviews are copies of the same review posted under several product *variants*; only exact duplicates were removed.
* Reviews are from Amazon (US, 1999–2012); findings describe this dataset only.
