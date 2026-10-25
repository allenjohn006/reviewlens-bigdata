#!/usr/bin/env bash
# usage: run_job.sh NAME INPUT_HDFS_PATH MAPPER REDUCER [COMBINER|-] [extra -D options...]
# Runs ONE Hadoop Streaming job, saves the console log (with Hadoop counters) to evidence/hadoop/NAME.log and the output to results/mr/NAME.tsv
source "$(dirname "$0")/env.sh"
NAME=$1; IN=$2; MAP=$3; RED=$4; COMB=${5:--}; shift 5 2>/dev/null
LOG=$RL/evidence/hadoop/$NAME.log; mkdir -p $RL/evidence/hadoop $RL/results/mr
OUT=/reviewlens/out/$NAME; hdfs dfs -rm -r -f -skipTrash $OUT >/dev/null 2>&1
FILES="$RL/hadoop/streaming/common.py,$RL/hadoop/streaming/$MAP,$RL/hadoop/streaming/$RED"
CARG=""; if [ "$COMB" != "-" ]; then CARG="-combiner $COMB"; FILES="$FILES,$RL/hadoop/streaming/$COMB"; fi
START=$(date +%s)
echo "# JOB $NAME $(date -Is) input=$IN mapper=$MAP reducer=$RED combiner=$COMB" > $LOG
hadoop jar $STREAMING_JAR -D mapreduce.job.name=reviewlens-$NAME "${@}" -files "$FILES" -cmdenv PYTHONPATH=. \
  -input $IN -output $OUT -mapper "python3 $MAP" -reducer "python3 $RED" $CARG >> $LOG 2>&1
RC=$?; END=$(date +%s); echo "# exit=$RC elapsed_s=$((END-START))" >> $LOG
hdfs dfs -cat "$OUT/part-*" > $RL/results/mr/$NAME.tsv 2>/dev/null
echo "$NAME  exit=$RC  elapsed=$((END-START))s  output_rows=$(wc -l < $RL/results/mr/$NAME.tsv)"
grep -E "Map input records|Map output records|Combine input records|Combine output records|Reduce input records|Reduce output records|Launched map tasks|Launched reduce tasks" $LOG | sed 's/^\s*//' | tr '\n' ';' | cut -c1-700; echo
