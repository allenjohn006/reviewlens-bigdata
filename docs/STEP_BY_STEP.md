# ReviewLens — Step by step, from scratch

Every command below was run on this laptop (Ubuntu 26.04, 14 GB RAM, 12 cores) and the output shown is real. Read the **"why"** lines — they are the answers to your faculty's questions.

Conventions: `$` = type this in a terminal. Replace `allen` with your Linux username where it appears in a path. Lines starting with `#` are comments. Project folder: `~/reviewlens`.

> **The big picture (draw this in the viva)**
> ```
>  Kaggle CSV ──clean──▶ MongoDB (native, port 27019)  ── export ──▶ HDFS ──▶ MapReduce jobs (YARN) ──▶ result files
>   568,454 rows        STORAGE: insert/find/update/delete     3 blocks        mapper → shuffle → reducer     │
>                              ▲                                                                             │
>                              └──────────────── results loaded back (mr_* collections) ◀───────────────────┘
>                                   │
>                                   └── queries / charts / validation
> ```
> **MongoDB = storage. Hadoop = processing.** They never talk directly (the MongoDB–Hadoop connector is discontinued), so data travels as a text file.

---
## PART A — Install the tools (do once)

### A1. Java (Hadoop is written in Java)
```bash
$ sudo apt update
$ sudo apt install -y openjdk-17-jdk-headless
$ java -version
openjdk version "17.0.20.1" ...
```
*Why:* Hadoop runs on the JVM. Java 17 is supported by Hadoop 3.4.

### A2. Hadoop 3.4.3
```bash
$ mkdir -p ~/tools && cd ~/tools
$ curl -O https://dlcdn.apache.org/hadoop/common/hadoop-3.4.3/hadoop-3.4.3.tar.gz     # ~700 MB, official Apache mirror
$ tar xzf hadoop-3.4.3.tar.gz                  # unpack
$ ln -sfn hadoop-3.4.3 hadoop                  # short name: ~/tools/hadoop
```
Tell your shell where things are — add to the end of `~/.bashrc`, then run `source ~/.bashrc`:
```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export HADOOP_HOME=$HOME/tools/hadoop
export PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH
```
Check: `$ hadoop version` → `Hadoop 3.4.3`.

Also set Java for Hadoop itself: open `~/tools/hadoop/etc/hadoop/hadoop-env.sh` and add the line `export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64`.

### A3. Configure Hadoop as a single-machine cluster ("pseudo-distributed")
Four small XML files in `~/tools/hadoop/etc/hadoop/` (copies are in this repo's `config/` folder). Each one answers one question:

**`core-site.xml` — where is the file system?**
```xml
<configuration>
  <property><name>fs.defaultFS</name><value>hdfs://localhost:9000</value></property>
</configuration>
```
**`hdfs-site.xml` — where does HDFS keep its data, and how many copies?** (one machine → 1 copy)
```xml
<configuration>
  <property><name>dfs.replication</name><value>1</value></property>
  <property><name>dfs.namenode.name.dir</name><value>file:///home/allen/hdfs/nn</value></property>
  <property><name>dfs.datanode.data.dir</name><value>file:///home/allen/hdfs/dn</value></property>
</configuration>
```
**`mapred-site.xml` — run MapReduce on YARN**
```xml
<configuration>
  <property><name>mapreduce.framework.name</name><value>yarn</value></property>
  <property><name>mapreduce.application.classpath</name><value>$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/*:$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/lib/*</value></property>
  <property><name>yarn.app.mapreduce.am.env</name><value>HADOOP_MAPRED_HOME=/home/allen/tools/hadoop</value></property>
  <property><name>mapreduce.map.env</name><value>HADOOP_MAPRED_HOME=/home/allen/tools/hadoop</value></property>
  <property><name>mapreduce.reduce.env</name><value>HADOOP_MAPRED_HOME=/home/allen/tools/hadoop</value></property>
</configuration>
```
**`yarn-site.xml` — the "resource manager" settings (how much memory/CPU jobs may use)**
```xml
<configuration>
  <property><name>yarn.nodemanager.aux-services</name><value>mapreduce_shuffle</value></property>
  <property><name>yarn.nodemanager.env-whitelist</name><value>JAVA_HOME,HADOOP_COMMON_HOME,HADOOP_HDFS_HOME,HADOOP_CONF_DIR,HADOOP_YARN_HOME,HADOOP_MAPRED_HOME</value></property>
  <property><name>yarn.nodemanager.resource.memory-mb</name><value>9216</value></property>   <!-- use 4096 on an 8 GB laptop -->
  <property><name>yarn.nodemanager.resource.cpu-vcores</name><value>12</value></property>   <!-- number of CPU cores -->
  <property><name>yarn.scheduler.minimum-allocation-mb</name><value>512</value></property>
  <property><name>yarn.scheduler.maximum-allocation-mb</name><value>4096</value></property>
  <property><name>yarn.nodemanager.vmem-check-enabled</name><value>false</value></property>
</configuration>
```
*Why `mapreduce_shuffle`:* the **shuffle** (moving mapper output to the right reducer) is a service run inside the NodeManager.

### A4. Create the HDFS storage — **ONLY THE FIRST TIME**
```bash
$ mkdir -p ~/hdfs/nn ~/hdfs/dn
$ hdfs namenode -format -force -nonInteractive
...  Storage directory /home/allen/hdfs/nn has been successfully formatted.
```
> ⚠️ Never run `format` again on a cluster that has data — it **erases HDFS**.

### A5. Start Hadoop (four daemons)
```bash
$ hdfs --daemon start namenode          # the HDFS "index": knows which blocks make up which file
$ hdfs --daemon start datanode          # stores the actual data blocks
$ yarn --daemon start resourcemanager   # the "manager": decides which jobs get CPU/memory
$ yarn --daemon start nodemanager       # the "worker": runs the map and reduce tasks in containers
$ jps                                   # lists running Java programs
5875 NameNode
6396 DataNode
7329 ResourceManager
7738 NodeManager
```
Shortcut in this repo: `bash scripts/start_hadoop.sh` (skips daemons already running). **After every reboot you must start them again.**

Web pages (open in a browser — your faculty will want to see them):
* **http://localhost:9870** – NameNode: HDFS health, *Utilities → Browse the file system* (files, blocks).
* **http://localhost:8088** – YARN ResourceManager: every job ("application"), its status and tasks.

### A6. Smoke test with the official word-count example
```bash
$ printf 'the coffee is great\nthe tea is great too\ncoffee and tea\n' > sample.txt
$ hdfs dfs -mkdir -p /smoke                         # a folder INSIDE HDFS (not on your normal disk)
$ hdfs dfs -put sample.txt /smoke/                  # copy a local file into HDFS
$ hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.4.3.jar wordcount /smoke/sample.txt /smoke/out
...  Job job_..._0006 completed successfully     Map input records=3     Reduce output records=7
$ hdfs dfs -cat /smoke/out/part-r-00000
and 1 / coffee 2 / great 2 / is 2 / tea 2 / the 2 / too 1
```
If you got those counts, **Hadoop works**. Everything else in this project is "the same, with our own mapper/reducer and our own data".

### A7. MongoDB 7.0 — native, **no Docker**
```bash
$ cd ~/tools && mkdir -p dl mongodb mongosh
$ curl -L -o dl/mongodb-7.0.tgz https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu2204-7.0.14.tgz
$ curl -L -o dl/mongosh.tgz   https://downloads.mongodb.com/compass/mongosh-2.3.8-linux-x64.tgz
$ tar xzf dl/mongodb-7.0.tgz -C mongodb --strip-components=1       # mongod = the server
$ tar xzf dl/mongosh.tgz     -C mongosh --strip-components=1       # mongosh = the command-line client
$ mkdir -p ~/reviewlens/mongo-data ~/reviewlens/logs                # where the database FILES will live (on your disk)
$ ~/tools/mongodb/bin/mongod --dbpath ~/reviewlens/mongo-data --port 27019 --bind_ip 127.0.0.1 --fork --logpath ~/reviewlens/logs/mongod.log
child process started successfully, parent exiting
$ ~/tools/mongosh/bin/mongosh --port 27019 --eval 'db.version()'
7.0.14
```
*Why 7.0, not 8.x:* MongoDB 8 refuses to start on Linux kernel 6.19–7.0.13 (this laptop has 7.0.0). *Why port 27019:* an older Docker MongoDB from the RetailPulse project may still use 27017.
*How to prove it is native:* `ps aux | grep mongod` shows a normal process owned by you, `ls ~/reviewlens/mongo-data` shows its files, and `docker ps` need not show anything.
Stop it: `~/tools/mongodb/bin/mongod --dbpath ~/reviewlens/mongo-data --shutdown`. Start it again: `bash scripts/03_start_mongo.sh`.

### A8. Python environment
```bash
$ curl -LsSf https://astral.sh/uv/install.sh | sh          # uv = fast Python installer; open a new terminal afterwards
$ cd ~/reviewlens
$ uv venv --python 3.12 .venv                               # private Python for this project
$ uv pip install --python .venv/bin/python pandas pymongo matplotlib pytest kaggle
```
Use it as `.venv/bin/python script.py` (or after `source scripts/env.sh`, simply `$PY script.py`).

### A9. Kaggle access (to download the dataset)
1. kaggle.com → your profile → **Settings → API → Create New Token** (downloads a token).
2. Save its content in `~/.kaggle/access_token` and run `chmod 600 ~/.kaggle/access_token`.
*(Or skip this: open the dataset page in a browser, press Download, and unzip `Reviews.csv` into `~/reviewlens/data/raw/`.)*

---
## PART B — Build the project (each step = one script; run them in order)

Always start with: `$ cd ~/reviewlens && source scripts/env.sh`

### Step 1 — Get the data
```bash
$ bash scripts/01_download.sh
568455 data/raw/Reviews.csv           # 568,454 reviews + header
```
Dataset: **Amazon Fine Food Reviews** (Kaggle `snap/amazon-fine-food-reviews`, CC0). Columns: Id, ProductId, UserId, ProfileName, HelpfulnessNumerator, HelpfulnessDenominator, Score (1–5), Time, Summary, Text. 74,258 products, 256,059 reviewers, Oct 1999 – Oct 2012. *Why this dataset:* text reviews are **semi-structured** data, well above the 50,000-record minimum.

### Step 2 — Clean the data
```bash
$ python scripts/02_clean.py        # same as: .venv/bin/python scripts/02_clean.py
```
What it does and the real result (`results/cleaning_log.json`):

| Problem found | Rows | Action |
|---|---|---|
| Missing profile name / summary | 26 / 27 | filled with empty text (they are optional) |
| Helpful votes **greater than** total votes (impossible) | 2 | dropped |
| **Exact duplicates** (same user, product, time, text) | 1,205 | dropped |
| Reviews containing HTML (`<br />`) | 146,636 | tags removed, whitespace collapsed (one review = one line) |
| **Result** | 568,454 → **567,247** | `data/clean/reviews_clean.jsonl` (JSON documents, 393 MB) |

Also derives `sentiment` (score ≤2 negative, 3 neutral, ≥4 positive) and `month`. *Why a cleaning log:* the rubric asks for preprocessing evidence; counts prove nothing was removed silently.

### Step 3 — Start MongoDB
```bash
$ bash scripts/03_start_mongo.sh
MongoDB 7.0.14 is up on port 127.0.0.1:27019
```

### Step 4 — Insert the data into MongoDB
```bash
$ python scripts/04_load_mongo.py
connected to MongoDB 7.0.14 at ('127.0.0.1', 27019)
{ "inserted": 567247, "count_in_db": 567247, "insert_seconds": 11.2, "indexes": [...7 indexes...], "storage_mb": 161 }
```
`insert_many` in batches of 10,000, then 7 indexes (productId, userId, date, score, sentiment, unique reviewId). **Look at it yourself:**
```bash
$ mongosh --port 27019
> use reviewlens
> db.reviews.countDocuments({})
567247
> db.reviews.findOne()                                    # one review document
> db.reviews.find({productId: "B007JFMH8M"}).limit(3)
```

### Step 5 — Export from MongoDB and put the file into HDFS
```bash
$ python scripts/05_export_to_hdfs.py                     # MongoDB -> data/clean/reviews.tsv (283 MB, 567,247 lines)
$ hdfs dfs -mkdir -p /reviewlens/raw
$ hdfs dfs -put -f data/clean/reviews.tsv /reviewlens/raw/
$ hdfs fsck /reviewlens/raw/reviews.tsv -files -blocks    # how HDFS stored it
 0. blk_...  len=134217728     1. blk_...  len=134217728     2. blk_...  len=14528297     Total blocks: 3
```
**Concept:** HDFS cuts the file into **128 MB blocks**. 3 blocks → Hadoop starts **3 mappers**, one per block, in parallel. Each line = `reviewId productId userId score month helpYes helpTotal body`, separated by tabs.

### Step 6 — Run the MapReduce jobs
```bash
$ bash scripts/06_run_jobs.sh
```
Watch http://localhost:8088 while it runs. Real results:

| Job | Question it answers | Mapper emits | Reducer does | Time | Output |
|---|---|---|---|---|---|
| **J1** | Which words appear in positive / neutral / negative reviews? | `sentiment\|word → 1` per word | adds the 1s | 64 s | 34,541 (word ≥20×) |
| **J2** | How many reviews and what average score per product? | `productId → 1,score,star-histogram` | sums, divides | 24 s | 74,258 products |
| **J3** | How does review volume / score change by month? | `month → 1,score,helpful…` | sums | 22 s | 143 months |
| **J4** | How many reviews does each reviewer write? | `userId → 1` | counts | 24 s | 256,059 reviewers |
| **J4b** | (chained: reads J4's output) distribution of reviewer activity | `bucket → 1` | counts | 20 s | 7 buckets |

The scripts are in `hadoop/streaming/` — each is ~10 lines. This is **Hadoop Streaming**: Hadoop runs any program that reads lines from stdin and prints `key<TAB>value` to stdout; ours are Python. **Same MapReduce**, just not Java.

**How one job runs (use this on the whiteboard) — the word count of `"the coffee is great"`:**
```
HDFS block ─▶ MAP  (one per block)                SHUFFLE & SORT                         REDUCE
 "great coffee"  ▶ great|1  coffee|1               all pairs with the SAME key         great  → 1+1+1 = 3
 "great tea"     ▶ great|1  tea|1     ──combiner──▶ are sent to ONE reducer, sorted ─▶  coffee → 1+1   = 2
 "coffee tea"    ▶ coffee|1 tea|1     (adds up      by key                              tea    → 1+1   = 2
                                       per mapper)
```
**Combiner** = a mini-reducer run on each mapper's output *before* the shuffle. Real number from J1: mappers produced **22,811,691** word pairs; after the combiner only **950,254** crossed the network (−96 %).
**Counters** (`Quality` group in our mappers) = Hadoop's way to count events across all tasks, e.g. malformed lines skipped. Logs with all counters: `evidence/hadoop/J*.log`.
**Job chaining:** J4b's input is J4's output folder in HDFS.

### Step 7 — Load the results into MongoDB
```bash
$ python scripts/07_load_results.py
{'mr_words': 34541, 'mr_products': 74258, 'mr_months': 143, 'mr_users': 256059, 'mr_activity_hist': 7, 'mr_jobs': 5}
```
Collections `mr_*` hold the results; `mr_jobs` holds job statistics (time, records in/out, mappers, reducers).

### Step 8 — Validate (prove the MapReduce results are right)
```bash
$ python scripts/08_validate.py
PASS J1 word counts by sentiment (>=20) (34541 keys, 0 mismatches)   ... PASS J2 ... J3 ... J4 ... J4b ...   ALL PASS
```
pandas/Counter recomputes every job on the cleaned file with a **different code path**; any difference would print `FAIL`. *This is your "Result — accuracy and validation" evidence.*

### Step 9 — Analyse and draw charts
```bash
$ python scripts/09_analysis_and_charts.py       # reads MongoDB, writes results/charts/*.png and results/insights.json
```
### Step 10 — MongoDB operations demo (insert / find / update / delete)
```bash
$ python scripts/10_mongo_crud_demo.py           # prints a readable transcript; also saved to evidence/mongo/crud_demo.txt
```
The same in the shell (type these live):
```javascript
> use reviewlens
> db.reviews.insertOne({reviewId: 9000001, productId: "B000DEMO01", score: 5, summary: "Demo", text: "Added live"})   // CREATE
> db.reviews.find({productId: "B000DEMO01"})                                                                         // READ
> db.reviews.updateOne({reviewId: 9000001}, {$set: {score: 4}, $inc: {helpYes: 2}})                                  // UPDATE
> db.reviews.deleteOne({reviewId: 9000001})                                                                          // DELETE
> db.reviews.aggregate([{$group: {_id: "$productId", n: {$sum: 1}, avg: {$avg: "$score"}}}, {$match: {n: {$gte: 200}}}, {$sort: {avg: -1}}, {$limit: 5}])
> db.reviews.find({productId: "B007JFMH8M"}).explain("executionStats")      // look at totalDocsExamined
```
Index effect measured: with the `productId` index **913 documents examined, about 1–3 ms**; without it **567,247 examined, about 260 ms**.

### Step 11 — Tests
```bash
$ python -m pytest tests -q          # 5 passed: each job's mapper|sort|reducer logic
```

### Step 12 — Generate Architecture Visual
```bash
$ python scripts/generate_architecture_diagram.py
```
Outputs a high-resolution (300 DPI) schematic to `dashboard/pipeline_architecture.png` illustrating the exact dataflow from Kaggle CSV through Cleaning, Native MongoDB, HDFS blocks, MapReduce jobs on YARN, Validation, and Dashboard visualizers.

### Step 13 — Launch the Multi-Page Streamlit Dashboard
```bash
$ bash dashboard/start_dashboard.sh
```
Access at `http://localhost:8501`. Features 6 pages:
1. **Dataset**: Raw vs cleaned counts, anomaly breakdown, and live document preview.
2. **MapReduce**: 5-job monitor with real YARN runtimes, block splits, and the 96% combiner reduction.
3. **MongoDB**: Native instance stats, collection sizes, 7 indexes, and index lookup benchmark.
4. **Insights**: 5 interactive Plotly charts (Rating Distribution, Polarizing Words, Growth Drift, Long Tail, Product Averages).
5. **Validation**: Zero-mismatch proof table validating all MapReduce outputs against pandas.
6. **Live Demo**: Live interactive query execution in MongoDB (insert, update, delete, aggregation pipeline, and `explain()`).

### Run everything at once
`bash scripts/run_all.sh` (about 5 minutes).

---
## PART C — Troubleshooting (real problems met while building)
| Symptom | Cause | Fix |
|---|---|---|
| `jps` does not list NameNode etc. | Hadoop does not auto-start after reboot | `bash scripts/start_hadoop.sh` |
| `Connection refused` to port 9000/27019 | daemon/mongod not running | start it (Step 3 / A5) |
| `syntax error: unexpected end of file` in bash | Windows CRLF line endings (`\r\n`) introduced by editing in Windows | `find . -type f -not -path '*/.*' -exec sed -i 's/\r$//' {} +` |
| Hadoop daemons die immediately when subshell exits | Terminal session or subshell sending SIGHUP to background JVMs in WSL | Daemons run with `hdfs --daemon start` or `nohup` in decoupled process groups |
| Web UI inaccessible from Windows browser | Wrong port or binding | Access `http://localhost:8501` (Streamlit), `http://localhost:9870` (NameNode), `http://localhost:8088` (YARN); WSL2 forwards localhost automatically |
| Job fails: `ModuleNotFoundError: No module named 'common'` | Python can't find the shared file shipped with `-files` | already fixed: runner passes `-cmdenv PYTHONPATH=.` |
| Real error hidden behind `subprocess failed with code 1` | error is in the *task's* stderr | `~/tools/hadoop/logs/userlogs/<application>/<container>/stderr` |
| `mongod` exits at once / `kernel … incompatibility` | MongoDB 8.x on kernel ≥ 6.19 | use 7.0.x |
| `Port is already allocated` | another MongoDB (Docker) on 27017 | we use 27019 |
| `Name node is in safe mode` | NameNode just started | wait, or `hdfs dfsadmin -safemode wait` |
| `Output directory already exists` | Hadoop never overwrites output | `hdfs dfs -rm -r /reviewlens/out/<job>` (runner does it) |
| `BulkWriteError … duplicate key _id` | PyMongo adds `_id` to a dict after `insert_one` | copy the dict before reusing it |

## PART D — Stop everything
```bash
$ pkill -f "streamlit run" || true
$ yarn --daemon stop nodemanager; yarn --daemon stop resourcemanager; hdfs --daemon stop datanode; hdfs --daemon stop namenode
$ ~/tools/mongodb/bin/mongod --dbpath ~/reviewlens/mongo-data --shutdown
```
