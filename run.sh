#!/usr/bin/env bash
set -e

echo "====================================================================="
echo "Explainable Multi-Source News Bias and Framing Analyzer"
echo "====================================================================="

# Activate virtual environment
source ./venv/bin/activate

echo "[1/2] Starting FastAPI Backend on http://localhost:8001 ..."
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!

echo "[2/2] Starting Frontend Vite Dev Server on http://localhost:5173 ..."
npm --prefix frontend run dev -- --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!

echo ""
echo "System online!"
echo "API Docs: http://localhost:8001/docs"
echo "Analytics Dashboard: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all servers."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true" EXIT INT TERM
wait
