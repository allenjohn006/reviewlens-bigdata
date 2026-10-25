#!/usr/bin/env bash
# STEP 3 - start MongoDB natively (a normal process on this machine, NOT Docker). Data lives in ./mongo-data, port 27019.
source "$(dirname "$0")/env.sh"; mkdir -p $RL/mongo-data $RL/logs
if pgrep -f "mongod --dbpath $RL/mongo-data" >/dev/null; then echo "mongod already running"; else
  mongod --dbpath $RL/mongo-data --port $MONGO_PORT --bind_ip 127.0.0.1 --fork --logpath $RL/logs/mongod.log; fi
mongosh --quiet --port $MONGO_PORT --eval 'print("MongoDB " + db.version() + " is up on port " + db.getMongo().host)'
