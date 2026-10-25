# ReviewLens: Mining 567 thousand Amazon Food Reviews with Hadoop MapReduce and MongoDB

*Draft for the Big Data Tools and Techniques report. All numbers come from the files in `results/` and `evidence/`. Add your name/register number, and write the Introduction and Conclusion in your own words before submitting.*

## 1. Introduction and objective
Online shops collect millions of customer reviews. This project processes a real review dataset with **Hadoop MapReduce** and stores the data and results in **MongoDB** to answer: *What do customers praise or complain about? Which products are rated best/worst? How did review volume and ratings change over time? Do many people review, or a few?*

## 2. Dataset
* **Amazon Fine Food Reviews**, Kaggle (`snap/amazon-fine-food-reviews`), licence CC0 — https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews
* 568,454 reviews, 74,258 products, 256,059 reviewers, October 1999 – October 2012. Fields: Id, ProductId, UserId, ProfileName, HelpfulnessNumerator/Denominator, Score (1–5), Time, Summary, Text.
* Semi-structured: free text (average 436 characters) plus numeric/ID fields.
* Citation: McAuley, J. & Leskovec, J. (2013), *From amateurs to connoisseurs: modeling the evolution of user expertise through online reviews*, WWW 2013.

## 3. Tools
| Tool | Version | Role |
|---|---|---|
| Apache Hadoop (HDFS, YARN, MapReduce) | 3.4.3, single-node cluster, Hadoop Streaming | distributed storage & processing |
| MongoDB (native server) | 7.0.14, port 27019 | storage: insert, query, update, delete |
| Python, pandas, PyMongo, matplotlib | 3.12 | mappers/reducers, loading, validation, charts |
| Ubuntu Linux, 12 cores, 14 GB RAM | | environment |

## 4. Architecture / data flow
`Reviews.csv → cleaning → MongoDB (reviews) → export (TSV) → HDFS → MapReduce jobs on YARN → result files → MongoDB (mr_* collections) → analysis, charts, validation`  (diagram in README).

## 5. Pre-processing (cleaning log)
| Issue | Rows | Action |
|---|---|---|
| Missing profile name / summary | 26 / 27 | filled with empty string |
| Helpful votes > total votes | 2 | removed |
| Exact duplicate reviews (user, product, time, text) | 1,205 | removed |
| Reviews containing HTML tags | 146,636 | tags stripped, whitespace normalised |
| Result | 568,454 → **567,247** | derived fields: sentiment (score ≤2 negative, 3 neutral, ≥4 positive), month |

## 6. MongoDB integration
567,247 documents inserted with `insert_many` (batches of 10,000) in 11.2 s (≈ 50,600 documents/s); storage 161 MB; seven indexes (`productId`, `userId`, `date`, `score`, `sentiment`, unique `reviewId`). Operations demonstrated: `insert_one/insert_many`, `find`, aggregation pipeline (`$group`, `$match`, `$sort`), `update_one/update_many` (`$set`, `$inc`), `delete_one/delete_many`. Index effect (`explain`): a product lookup examines 913 documents in about 1–3 ms with the index, but 567,247 documents in about 260 ms without it. Result collections: `mr_words` 34,541, `mr_products` 74,258, `mr_months` 143, `mr_users` 256,059, `mr_activity_hist` 7, `mr_jobs` 5.

## 7. MapReduce method
The 567,247 reviews are exported from MongoDB to a tab-separated file (283 MB) and stored in HDFS, which splits it into **3 blocks** (128 MB, 128 MB, 13.9 MB), so three map tasks run in parallel. Jobs use Hadoop Streaming (Python).

| Job | Map output (key → value) | Reduce | Combiner |
|---|---|---|---|
| J1 word count by sentiment | `sentiment\|word → 1` | sum (keep ≥ 20) | sum |
| J2 product statistics | `productId → 1, score, star histogram` | sum, mean | sum |
| J3 monthly trend | `YYYY-MM → 1, score, helpful votes` | sum | sum |
| J4 reviewer activity | `userId → 1` | sum | sum |
| J4b (chained, reads J4 output) | `activity bucket → 1` | sum | sum |

*Pseudocode (J1):* `map(line): fields = split(line, TAB); s = sentiment(score); for word in tokens(lower(text)): if word not in stopwords: emit(s + "|" + word, 1)`  ·  `reduce(key, values): emit(key, sum(values))`.
*Efficiency:* in J1 the mappers emitted 22,811,691 pairs; the combiner reduced them to 950,254 before the shuffle (−96 %). Run times (idle laptop): J1 64 s, J2 24 s, J3 22 s, J4 24 s, J4b 20 s. Hadoop counters recorded 567,247 lines read and 0 malformed lines. J1 shows 2 killed map attempts (speculative execution).

## 8. Results
*(Insert charts from `results/charts/`.)*
1. **Ratings are strongly positive:** 5★ 63.9 %, 4★ 14.2 %, 3★ 7.5 %, 2★ 5.2 %, 1★ 9.2 % (Figure 3).
2. **Words:** most frequent in positive reviews — great, good, like, coffee, love, taste, tea, flavor. In negative reviews the frequent words are similar (like, taste, product, good) — frequency alone does not separate sentiment. Words that are far more typical of negative reviews (relative frequency): *deceptive* 39.8×, *yuck* 28.3×, *worst* 24.8×, *refund* 23.2×, *false*, *disappointing*, *moldy* (Figure 2).
3. **Growth and drift:** volume rises steadily to a peak of 21,903 reviews in September 2012; the average monthly score falls from 4.38 (first year) to 4.12 (last 12 months) (Figure 4).
4. **Reviewer behaviour:** 68.5 % of the 256,059 reviewers wrote exactly one review; the most active wrote 442 (Figure 5, log scale).
5. **Products:** 857 products have ≥ 100 reviews; the best average is 4.97 (113 reviews) and the worst 1.34 (131 reviews).

## 9. Validation
Each job was recomputed independently with pandas/Python `Counter` on the cleaned file and compared key by key: **5 of 5 checks passed with zero mismatches** (34,541 + 74,258 + 143 + 256,059 + 7 keys). Five unit tests check each mapper/reducer on small inputs. The Hadoop counters and logs for every run are in `evidence/hadoop/`.

## 10. Limitations
Hadoop ran on a single machine (real HDFS/YARN, no multi-node speed-up). Hadoop Streaming uses Python, not Java. MongoDB and Hadoop exchange data through files. Word frequency is not sentiment. About 173,000 reviews are the same review copied across product variants; only exact duplicates were removed. Findings describe Amazon food reviews from 1999–2012.

## 11. Conclusion
*(Write 4–5 lines: what you built, what you learned about HDFS/MapReduce/MongoDB, the main findings, and future work, e.g. a multi-node cluster, sentiment classification, a MongoDB-Spark pipeline.)*

## 12. References
1. Dean, J., Ghemawat, S. (2004). MapReduce: Simplified Data Processing on Large Clusters. OSDI.
2. Apache Hadoop documentation, https://hadoop.apache.org/docs/r3.4.3/ (HDFS Architecture; MapReduce Tutorial; Hadoop Streaming).
3. MongoDB Manual 7.0, https://www.mongodb.com/docs/v7.0/ (CRUD operations; Indexes; Aggregation).
4. McAuley & Leskovec (2013), WWW. Kaggle dataset page above.
5. PyMongo documentation, https://pymongo.readthedocs.io/.
