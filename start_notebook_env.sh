#!/usr/bin/env zsh
set -euo pipefail

TARGET_DIR="/Users/jonasvogt/Job/Vorlesungen/Python/AI_Products_Dash"
PROJECT_DIR="/Users/jonasvogt/Job/AIGovernance/AI_Multiples"

source "$TARGET_DIR/.venv/bin/activate"
export PYTHONPATH="$PROJECT_DIR:${PYTHONPATH:-}"

echo "Python: $(which python)"
echo "PYTHONPATH includes: $PROJECT_DIR"
echo "Notebook: $TARGET_DIR/teaching_dash_minimal.ipynb"
