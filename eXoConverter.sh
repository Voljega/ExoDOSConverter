#!/bin/sh
dir="$(dirname "$0")"
# use the virtual environment created by the installation steps if there is one
if [ -x "$dir/.venv/bin/python3" ]; then
    python="$dir/.venv/bin/python3"
else
    python=python3
fi
exec "$python" "$dir/main.py" "$@"
