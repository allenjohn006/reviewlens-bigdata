#!/usr/bin/env bash
# Start all ReviewLens services, daemons, and dashboard in one command.
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"
source scripts/env.sh

echo "=========================================================="
echo "  ReviewLens — Starting Entire Big Data System"
echo "=========================================================="

# 1. Native MongoDB
echo "[1/4] Starting Native MongoDB 7.0 on port 27019..."
bash scripts/03_start_mongo.sh

# 2. Hadoop Daemons
echo "[2/4] Starting Hadoop daemons (HDFS & YARN)..."
bash scripts/start_hadoop.sh

# 3. Quick test verification
echo "[3/4] Running unit tests..."
pytest tests -q || true

# 4. Streamlit Dashboard
echo "[4/4] Starting Streamlit Interactive Dashboard on port 8501..."
echo "=========================================================="
echo "  All services are LIVE:"
echo "  * Streamlit Dashboard:    http://localhost:8501"
echo "  * Hadoop NameNode Web UI: http://localhost:9870"
echo "  * YARN ResourceManager:   http://localhost:8088"
echo "  * Native MongoDB:         localhost:27019"
echo "=========================================================="

exec python -m streamlit run dashboard/app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --theme.base dark \
  --theme.primaryColor "#16a34a" \
  --theme.backgroundColor "#0f172a" \
  --theme.secondaryBackgroundColor "#1e293b" \
  --theme.textColor "#f1f5f9"

