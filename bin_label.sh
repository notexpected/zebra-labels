#!/usr/bin/env bash
# Generate a storage bin label for the Zebra GX420d
exec "$(dirname "$0")/.venv/bin/python3" "$(dirname "$0")/bin_label.py" "$@"
