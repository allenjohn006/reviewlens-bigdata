#!/usr/bin/env bash
# STEP 1b - download the dataset from Kaggle (needs your Kaggle API token in ~/.kaggle/access_token, see docs/STEP_BY_STEP.md)
source "$(dirname "$0")/env.sh"; mkdir -p $RL/data/raw
export KAGGLE_API_TOKEN=$(cat ~/.kaggle/access_token)
$RL/.venv/bin/kaggle datasets download -d snap/amazon-fine-food-reviews -p $RL/data/raw --unzip
rm -f $RL/data/raw/database.sqlite                  # duplicate of Reviews.csv in another format
wc -l $RL/data/raw/Reviews.csv
