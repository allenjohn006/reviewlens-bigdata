# What was done — in plain language

## The goal
Your faculty want to **see Hadoop and MapReduce working** and **MongoDB running directly on your machine (not in Docker)**. Front end, back end and cloud do not matter. So this project is small and focused on exactly that.

## The story of the project (say this in the viva)
1. **Data.** I took 568,454 real customer reviews of food products from Kaggle (text + star rating + product + reviewer + date).
2. **Cleaning.** Removed duplicates and impossible rows, stripped HTML, filled blanks → 567,247 clean reviews. Every change is counted in `results/cleaning_log.json`.
3. **MongoDB (storage).** The clean reviews were inserted into a MongoDB server running natively on your laptop (port 27019). We created indexes and tried insert / find / update / delete.
4. **Hadoop (processing).** The reviews were exported from MongoDB into HDFS (Hadoop's file system), where the 283 MB file is cut into 3 blocks. Five MapReduce jobs then processed them on YARN:
   * J1 counted every word, separately for positive / neutral / negative reviews;
   * J2 computed review count and average score for each of 74,258 products;
   * J3 computed reviews and average score per month (trend 1999–2012);
   * J4 counted how many reviews each of 256,059 reviewers wrote;
   * J4b (chained to J4) turned that into a histogram.
5. **Back to MongoDB.** The job results were loaded into MongoDB collections (`mr_words`, `mr_products`, `mr_months`, `mr_users`, `mr_activity_hist`, `mr_jobs`) and analysed with queries, producing 5 charts and the insights.
6. **Proof it is correct.** Every job was recomputed a different way with pandas — 5 of 5 checks matched exactly. Five unit tests check each mapper/reducer. The whole pipeline was re-run from scratch in one command (4 min 39 s) and gave the same results.
7. **Interactive Dashboard & Architecture Visual.** A clean, professional multi-page Streamlit dashboard (`http://localhost:8501`) showcases dataset exploration, MapReduce executions, MongoDB schema/indexes, interactive Plotly visualizations, validation proof, and live MongoDB query execution. A high-resolution pipeline architecture diagram is embedded on the landing page.

## Main findings
64 % of reviews are 5-star · 68.5 % of reviewers wrote just one review (most active: 442) · average score drifted from 4.38 to 4.12 over the years · review volume peaked in Sept 2012 (21,903) · words like *deceptive, yuck, worst, refund* mark negative reviews · "good" and "like" are common even in negative reviews, so word frequency is not sentiment.

## Where everything is
| Place | What |
|---|---|
| `~/reviewlens` (this folder) | The whole project — **separate from `~/IA-3`** (RetailPulse) |
| GitHub `allenjohn006/reviewlens-bigdata` (private) | The same project, pushed |
| `dashboard/` | Multi-page Streamlit UI (`app.py`, 6 subpages in `pages/`, `pipeline_architecture.png`, `start_dashboard.sh`) |
| `scripts/` | Numbered steps 01–10 (download, clean, start Mongo, load, export, run jobs, load results, validate, charts, CRUD demo), `generate_architecture_diagram.py`, plus `run_all.sh` for everything |
| `hadoop/streaming/` | **The MapReduce code** (mappers and reducers) — show this when asked "where is MapReduce?" |
| `config/` | The four Hadoop XML configuration files |
| `tests/` | Unit tests of the mappers/reducers |
| `results/` | Outputs: cleaning log, job outputs (`mr/`), validation report, insights, charts |
| `evidence/` | Hadoop job logs with counters, MongoDB demo transcript, screenshots of NameNode / HDFS / YARN, full run log |
| `docs/` | `STEP_BY_STEP.md` (build from zero), `HOW_TO_RUN.md`, `RUBRIC_CHECK.md`, `REPORT_DRAFT.md`, `PRESENTATION.md`, `PLAN.md` |
| `data/`, `mongo-data/` | Raw/clean data and the MongoDB database files (on your disk, **not** in git because they are large) |
| Outside the repo: `~/tools/hadoop`, `~/tools/mongodb`, `~/tools/mongosh` | The installed software |

## What is yours to finish
* Add your name/register number; write the report's Introduction and Conclusion in your own words (`docs/REPORT_DRAFT.md`).
* Make the 9-slide PPT from `docs/PRESENTATION.md` and paste in the charts.
* Practise the live demo once.
* The MongoDB certificate (10 marks) is yours.

## Honest limits
One-machine Hadoop cluster · Python via Hadoop Streaming instead of Java · MongoDB and Hadoop exchange a file because the official connector is discontinued · word frequency ≠ sentiment.
