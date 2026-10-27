# ReviewLens — Hadoop MapReduce + Native MongoDB on 567k Food Reviews

A complete Big Data engineering project for the **Big Data Tools and Techniques** course (**23DC2044**, Karunya Institute, B.Tech AI&DS). It demonstrates, end to end:
**how Hadoop MapReduce executes on YARN, how native MongoDB (NoSQL) stores and indexes semi-structured data, and how results are validated and served through an interactive dashboard.**

```
Kaggle CSV ─clean─▶ MongoDB 7.0 (native, :27019) ─export─▶ HDFS (3 blocks) ─▶ Hadoop MapReduce on YARN ─▶ results ─▶ MongoDB (mr_* collections) ─▶ Dashboard & Validation
 568,454 rows        567,247 documents + 7 indexes         reviews.tsv         5 job runs, combiners, counters        6 result marts                 5/5 checks PASS
```

* **Dataset:** Amazon Fine Food Reviews (Kaggle CC0) — 568,454 text reviews, 74,258 products, 256,059 reviewers (Oct 1999 – Oct 2012).
* **Hadoop MapReduce (Hadoop 3.4.3 Streaming, Python):** 5 jobs on YARN (Sentiment Word Frequency with 96% Combiner Reduction, Per-Product Statistics, Longitudinal Monthly Trends, Reviewer Activity, and Chained Activity Histogram).
* **Native MongoDB (7.0.14, Port 27019):** Bulk insert (60k docs/s), 7 indexes, full CRUD operations, and `explain()` index query benchmark (2 ms indexed vs 188 ms table scan).
* **Validation & Proof:** Independent Pandas ground-truth validation (5/5 PASS, 0 mismatches across 365,008 keys), isolated unit tests, execution logs with Hadoop counters.
* **Interactive UI Dashboard:** Multi-page Streamlit application running on `http://localhost:8501` showcasing metrics, charts, live query workbench, and architecture diagrams.

---

## Quick Navigation

| I want to... | Open |
| :--- | :--- |
| **Launch the Interactive UI Dashboard** | [`dashboard/README.md`](dashboard/) · `bash dashboard/start_dashboard.sh` → `http://localhost:8501` |
| **Run the pipeline or conduct the live demo** | [`docs/HOW_TO_RUN.md`](docs/HOW_TO_RUN.md) |
| **Understand the project story and findings** | [`docs/WHAT_WAS_DONE.md`](docs/WHAT_WAS_DONE.md) |
| **Step-by-step setup in WSL from scratch** | [`docs/STEP_BY_STEP.md`](docs/STEP_BY_STEP.md) |
| **Check alignment with faculty evaluation rubric** | [`docs/RUBRIC_CHECK.md`](docs/RUBRIC_CHECK.md) |
| **Prepare slides, viva questions, and demo script**| [`docs/PRESENTATION.md`](docs/PRESENTATION.md) |
| **Read the academic report draft** | [`docs/REPORT_DRAFT.md`](docs/REPORT_DRAFT.md) |
| **Handoff notes & technical context** | [`CONTEXT.md`](CONTEXT.md) |

---

## Quick Start (WSL / Ubuntu)

### 1. Launch the Live Services & Dashboard
```bash
cd ~/reviewlens && source scripts/env.sh
bash scripts/start_hadoop.sh          # Starts NameNode, DataNode, ResourceManager, NodeManager
bash dashboard/start_dashboard.sh      # Starts MongoDB (:27019) + launches Dashboard (:8501)
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser to view the interactive dashboard.

### 2. Run the Full Data Pipeline from Scratch (~4–5 minutes)
```bash
cd ~/reviewlens && bash scripts/run_all.sh
```
Executes ingestion, cleaning, MongoDB loading, HDFS export, 5 MapReduce jobs on YARN, results loading, ground-truth validation, and chart generation.

---

## Repository Layout

* [`dashboard/`](dashboard/) — Multi-page Streamlit dashboard (`app.py`, 6 sub-pages, architecture diagram, startup script).
* [`scripts/`](scripts/) — Numbered pipeline scripts `01`–`10`, environment loader (`env.sh`), and daemon management.
* [`hadoop/streaming/`](hadoop/streaming/) — MapReduce Python mappers, reducers, and combiners.
* [`config/`](config/) — Pseudo-distributed Hadoop XML configurations (`core-site.xml`, `hdfs-site.xml`, `mapred-site.xml`, `yarn-site.xml`).
* [`tests/`](tests/) — Pytest unit test suite verifying MapReduce logic in isolation.
* [`results/`](results/) — Cleaning audit log, job output TSVs (`mr/`), analytical figures (`charts/`), and validation reports.
* [`evidence/`](evidence/) — Hadoop YARN execution logs with job counters, NameNode/YARN UI screenshots, and MongoDB benchmark transcript.
* [`docs/`](docs/) — Complete presentation kits, runbooks, report draft, and rubric compliance audits.
* `data/`, `mongo-data/` — Ignored by Git: raw/cleaned data files and native MongoDB WiredTiger storage files.

---

## Technical Notes & Architecture Decisions
* **Single-Node Pseudo-Distributed Hadoop:** Production Apache Hadoop 3.4.3 binaries running real HDFS and YARN daemons on one physical node.
* **Hadoop Streaming:** MapReduce written in Python consuming `stdin` and emitting `stdout` key-value pairs via `hadoop-streaming-3.4.3.jar`.
* **Decoupled Data Exchange:** MongoDB and Hadoop communicate via clean TSV files in HDFS (because the official MongoDB-Hadoop connector was discontinued by MongoDB).
* **Native Host Database:** MongoDB 7.0 runs as a standalone native OS process on port **27019**, completely separate from Docker container instances.
* **Word Frequency vs Sentiment:** Lexical frequencies alone do not equate to sentiment; relative odds ratios are computed to isolate true negative signal words.
