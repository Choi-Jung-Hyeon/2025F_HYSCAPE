#!/bin/bash
# ============================================================
# Hyscape Unified Daily Automation System
# WSL/Linux Execution Script
# ============================================================

echo "============================================================"
echo "⚡ Hyscape Unified Daily Automation System"
echo "============================================================"
echo ""
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting automation..."
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Run with virtual environment Python
/home/fourmi103/2025F_HYSCAPE/venv/bin/python main_unified.py

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "============================================================"
    echo "❌ ERROR: Automation failed!"
    echo "============================================================"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Error occurred" >> logs/error.log
    exit 1
else
    echo ""
    echo "============================================================"
    echo "✅ SUCCESS: All tasks completed!"
    echo "============================================================"
    exit 0
fi
