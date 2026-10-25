#!/usr/bin/env bash
# Source this file:  source scripts/env.sh   -> sets paths for Java, Hadoop, MongoDB, the project and Python
export RL=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)               # project root
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export HADOOP_HOME=$HOME/tools/hadoop
export MONGO_HOME=$HOME/tools/mongodb
export MONGOSH_HOME=$HOME/tools/mongosh
export PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$MONGO_HOME/bin:$MONGOSH_HOME/bin:$HOME/.local/bin:$PATH
export STREAMING_JAR=$HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-3.4.3.jar
export MONGO_PORT=27019                                                  # native MongoDB (NOT the Docker one on 27017)
export MONGO_URI="mongodb://127.0.0.1:$MONGO_PORT"
export PATH=$RL/.venv/bin:$PATH                                          # so plain "python" is the project Python
export PY=$RL/.venv/bin/python
