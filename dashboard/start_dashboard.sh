#!/usr/bin/env bash
# Start the ReviewLens dashboard.
# Usage:  bash dashboard/start_dashboard.sh
set -e
cd "$(dirname "$0")/.."
source scripts/env.sh

echo "========================================"
echo "  ReviewLens Dashboard"
echo "========================================"
echo "  Making sure MongoDB is running..."
bash scripts/03_start_mongo.sh

echo ""
echo "  Starting Streamlit dashboard..."
echo "  Open your browser at:  http://localhost:8501"
echo ""
python -m streamlit run dashboard/app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --theme.base dark \
  --theme.primaryColor "#16a34a" \
  --theme.backgroundColor "#0f172a" \
  --theme.secondaryBackgroundColor "#1e293b" \
  --theme.textColor "#f1f5f9"

