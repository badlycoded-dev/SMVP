#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
else
    echo "Virtual environment already exists."
fi

source "$SCRIPT_DIR/venv/bin/activate"

candidates=("dep.txt" "deps.txt" "req.txt" "reqs.txt" "requirements.txt" "requirements-dev.txt")
found=""
for f in "${candidates[@]}"; do
    if [ -f "$f" ]; then
        found="$f"
        break
    fi
done

if [ -n "$found" ]; then
    echo "Found $found - installing dependencies..."
    pip install -r "$found"
    echo "Dependencies installed."
else
    echo "No dependencies file found."
fi

if [ ! -f "manage.py" ]; then
    echo "Starting Django project..."
    django-admin startproject config .
else
    echo "Django project already initialized (manage.py exists)."
fi

echo "Setup complete."