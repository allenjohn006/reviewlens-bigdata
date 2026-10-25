# How to run ReviewLens

Three situations. Open a terminal and start with: `cd ~/reviewlens && source scripts/env.sh`

## 1. Every time you sit down (after a reboot Hadoop and MongoDB are OFF)
```bash
bash scripts/start_hadoop.sh        # starts NameNode, DataNode, ResourceManager, NodeManager (skips ones already running)
bash scripts/03_start_mongo.sh      # starts native MongoDB on port 27019
jps                                 # should list the 4 Hadoop daemons
```
Everything is already loaded, so you can go straight to the demo (section 2). Check: `mongosh --port 27019 --eval 'db.getSiblingDB("reviewlens").reviews.countDocuments({})'` → `567247`.

## 2. Show it (live demo, ~10 minutes)
```bash
mongosh --port 27019                                   # show dbs · use reviewlens · show collections · db.reviews.findOne()
hdfs dfs -ls -h /reviewlens/raw                        # the data in HDFS  (browser: http://localhost:9870 -> Utilities -> Browse the file system)
bash scripts/run_job.sh J3_monthly_volume /reviewlens/raw/reviews.tsv j3_month_mapper.py sum_reducer.py sum_reducer.py
                                                       # a MapReduce job running; watch http://localhost:8088 at the same time (~25 s)
head results/mr/J3_monthly_volume.tsv                  # its output
python scripts/08_validate.py                          # proof: ALL PASS (1-2 minutes)
python scripts/10_mongo_crud_demo.py                   # insert / find / update / delete / index explain
python -m pytest tests -q                              # 5 passed
```
Full demo script and answers to likely questions: `docs/PRESENTATION.md`.

## 3. Rebuild everything from scratch
Only if you want to repeat the whole pipeline (takes about 5 minutes):
```bash
bash scripts/run_all.sh
```
It starts MongoDB and Hadoop, cleans the data, loads MongoDB, exports to HDFS, runs the 5 jobs, loads results, validates, draws charts and runs the MongoDB demo. Output of the last full run: `evidence/run_all.log`.
Single steps (what they do and what output to expect): `docs/STEP_BY_STEP.md`, Part B.

## 4. On a new / another laptop
1. Do the one-time installs in `docs/STEP_BY_STEP.md` **Part A** (Java, Hadoop, MongoDB, Python, Kaggle token).
2. `git clone https://github.com/allenjohn006/reviewlens-bigdata.git ~/reviewlens` (log in to GitHub first; the repo is private).
3. `cd ~/reviewlens && uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python pandas pymongo matplotlib pytest kaggle`
4. `bash scripts/run_all.sh` (it downloads the data from Kaggle by itself if `data/raw/Reviews.csv` is missing).
Paths assume Hadoop in `~/tools/hadoop` and MongoDB in `~/tools/mongodb`; change them in `scripts/env.sh` if yours differ, and replace `allen` in the Hadoop XML paths with your username.

## 5. Stop everything
```bash
yarn --daemon stop nodemanager; yarn --daemon stop resourcemanager; hdfs --daemon stop datanode; hdfs --daemon stop namenode
mongod --dbpath ~/reviewlens/mongo-data --shutdown
```

## Quick fixes
| Problem | Fix |
|---|---|
| `Connection refused` | Hadoop or MongoDB not started → section 1 |
| `jps` shows fewer than 4 daemons | `bash scripts/start_hadoop.sh` |
| A job says output directory exists | `hdfs dfs -rm -r /reviewlens/out/<JobName>` (the runner does this itself) |
| MongoDB won't start / kernel message | must be MongoDB **7.0**, not 8 |
| More problems | `docs/STEP_BY_STEP.md` Part C |
