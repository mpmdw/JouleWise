#!/usr/bin/env bash
set -u

exec /Users/edr/code/JouleWise/scripts/backup_runs.sh \
  "${1:-runs/p2_015_floors_window_a}" \
  "/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup"
