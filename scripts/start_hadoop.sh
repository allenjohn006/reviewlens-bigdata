#!/usr/bin/env bash
# Start the four Hadoop daemons (single-node cluster). Safe to run repeatedly.
source "$(dirname "$0")/env.sh"

start_daemon() {
    local tool=$1
    local daemon=$2
    local jps_name=$3
    if jps | grep -q " ${jps_name}$"; then
        echo "${jps_name} already running"
    else
        $tool --daemon start $daemon
        echo "started ${jps_name}"
    fi
}

start_daemon hdfs namenode NameNode
start_daemon hdfs datanode DataNode
start_daemon yarn resourcemanager ResourceManager
start_daemon yarn nodemanager NodeManager

sleep 2
jps | grep -E "NameNode|DataNode|ResourceManager|NodeManager"
hdfs dfsadmin -safemode leave >/dev/null 2>&1 || true
