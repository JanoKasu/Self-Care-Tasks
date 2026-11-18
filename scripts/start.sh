#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
python="$project_dir/.venv/bin/python"

if [ ! -x "$python" ]; then
    echo "Virtual environment not found at $project_dir/.venv" >&2
    echo "Create it and install requirements.txt before enabling autostart." >&2
    exit 1
fi

cd "$project_dir"
export SELF_CARE_FULLSCREEN=1
exec "$python" "$project_dir/main.py"
