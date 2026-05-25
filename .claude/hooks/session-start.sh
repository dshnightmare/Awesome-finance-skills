#!/bin/bash
set -euo pipefail

# Only run in remote Claude Code on the web environment
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

echo "🚀 Setting up Awesome-finance-skills sandbox environment..."

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

# ── Step 1: Install lightweight packages (fast) ─────────────────────────────
echo "📦 Installing core packages..."
python3 -m pip install \
  loguru requests python-dotenv pydantic PyYAML tqdm pytest \
  pandas numpy matplotlib markdown \
  akshare yfinance \
  pyecharts \
  rank-bm25 jieba scikit-learn \
  ddgs baidusearch pycountry \
  "agno" \
  --quiet --no-warn-script-location 2>&1 | tail -3

# ── Step 2: Install heavy ML packages ───────────────────────────────────────
echo "🤖 Installing ML/AI packages (torch CPU, transformers)..."
python3 -m pip install \
  torch --index-url https://download.pytorch.org/whl/cpu \
  --quiet --no-warn-script-location 2>&1 | tail -3

python3 -m pip install \
  transformers sentence-transformers huggingface_hub einops \
  --quiet --no-warn-script-location 2>&1 | tail -3

echo "✅ All dependencies installed."
