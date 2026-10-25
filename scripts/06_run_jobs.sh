#!/usr/bin/env bash
# STEP 6 - run the MapReduce jobs on the data in HDFS.   Arguments of run_job.sh: NAME  INPUT  MAPPER  REDUCER  COMBINER  [extra Hadoop options]
cd "$(dirname "$0")/.."; R=scripts/run_job.sh; IN=/reviewlens/raw/reviews.tsv
bash $R J1_sentiment_words      $IN j1_words_mapper.py   sum_reducer.py        sum_reducer.py -D mapreduce.reduce.env=MIN_COUNT=20 -D mapreduce.job.reduces=2
bash $R J2_product_stats        $IN j2_product_mapper.py j2_product_reducer.py sum_reducer.py -D mapreduce.job.reduces=2
bash $R J3_monthly_volume       $IN j3_month_mapper.py   sum_reducer.py        sum_reducer.py
bash $R J4_reviewer_activity    $IN j4_user_mapper.py    sum_reducer.py        sum_reducer.py -D mapreduce.job.reduces=2
bash $R J4b_activity_histogram  /reviewlens/out/J4_reviewer_activity j4b_hist_mapper.py sum_reducer.py sum_reducer.py     # CHAINED: input = output of job 4
