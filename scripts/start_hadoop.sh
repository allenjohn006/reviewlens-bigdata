#!/usr/bin/env bash
# Start the four Hadoop daemons (single-node cluster). Safe to run repeatedly.
source "$(dirname "$0")/env.sh"
for d in "hdfs namenode:NameNode" "hdfs datanode:DataNode" "yarn resourcemanager:ResourceManager" "yarn nodemanager:NodeManager"; do
  cmd=${d%%:*}; name=${d##*:}; if jps | grep -q " $name$"; then echo "$name already running"; else $cmd --daemon start ${cmd#* }; echo "started $name"; fi; done
sleep 3; jps | grep -E "NameNode|DataNode|ResourceManager|NodeManager"; hdfs dfsadmin -safemode wait >/dev/null 2>&1
