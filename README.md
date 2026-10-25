# ReviewLens — Hadoop MapReduce + native MongoDB on 567 k food reviews

A small Big Data project for the *Big Data Tools and Techniques* course. It shows, end to end:
**where Hadoop is used, how MapReduce runs, and how MongoDB (native, not Docker) stores and serves the data.**

```
Kaggle CSV ─clean─▶ MongoDB 7.0 (native, :27019) ─export─▶ HDFS (3 blocks) ─▶ Hadoop MapReduce on YARN ─▶ results ─▶ MongoDB (mr_* collections) ─▶ queries, charts, validation
 568,454 rows        567,247 documents + 7 indexes         reviews.tsv         5 job runs, combiners, counters                                           5/5 checks PASS
```

* **Dataset:** Amazon Fine Food Reviews (Kaggle, CC0) — 568,454 text reviews, 74 k products, 256 k reviewers, 1999–2012.
* **MapReduce jobs** (Hadoop Streaming, Python): word frequency by sentiment · product statistics · monthly trend · reviewer activity · a chained histogram.
* **MongoDB:** bulk insert, indexes, find/aggregate/update/delete, `explain()`.
* **Proof:** independent pandas validation (0 mismatches), unit tests, Hadoop logs and counters, screenshots.

## Start here
| I want to… | Open |
|---|---|
| **Run it / do the demo** | [`docs/HOW_TO_RUN.md`](docs/HOW_TO_RUN.md) |
| **See what was done, in plain words** | [`docs/WHAT_WAS_DONE.md`](docs/WHAT_WAS_DONE.md) |
| **Build it from zero and understand every command** | [`docs/STEP_BY_STEP.md`](docs/STEP_BY_STEP.md) |
| Check it against the faculty rubric | [`docs/RUBRIC_CHECK.md`](docs/RUBRIC_CHECK.md) |
| Write the report | [`docs/REPORT_DRAFT.md`](docs/REPORT_DRAFT.md) |
| Prepare slides, live demo, viva answers | [`docs/PRESENTATION.md`](docs/PRESENTATION.md) |
| Continue in a new chat / hand over | [`CONTEXT.md`](CONTEXT.md) |

## Run everything (about 5 minutes, after the one-time installs in STEP_BY_STEP Part A)
```bash
cd ~/reviewlens && bash scripts/run_all.sh
```
Results: `results/` (cleaning log, validation report, insights, charts, job outputs) · `evidence/` (Hadoop logs, MongoDB demo transcript, UI screenshots).

## Layout
`scripts/` numbered steps 01–10 + helpers · `hadoop/streaming/` the mappers & reducers · `config/` Hadoop XML files used · `tests/` unit tests · `docs/` guides · `results/`, `evidence/` generated proof · `data/` (not in git: raw/clean data) · `mongo-data/` (not in git: the database files).

## Honest notes
Single-machine Hadoop cluster (real HDFS/YARN, one node) · Python via Hadoop Streaming (not Java) · MongoDB ⇄ Hadoop exchange files because the official connector is discontinued · word frequency ≠ sentiment.
