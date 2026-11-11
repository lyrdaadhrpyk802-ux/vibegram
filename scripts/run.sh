#!/data/data/com.termux/files/usr/bin/bash
# ============================================
#  scripts/run.sh - Run Python without .pyc generation
#  All code and comments are English. No emojis.
# ============================================
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD:${PYTHONPATH:-}"
export PYTHONDONTWRITEBYTECODE=1
exec python -B "$@"
