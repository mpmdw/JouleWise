#!/usr/bin/env bash
set -u

usage() {
  echo "Usage: $0 [RUNS_DIR] [DEST]" >&2
}

RUNS_DIR="${1:-runs}"
DEST="${2:-$HOME/JouleWise-backup}"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

if [ "$#" -gt 2 ]; then
  usage
  exit 64
fi

timestamp_utc() {
  TZ=UTC date "+%Y-%m-%dT%H:%M:%SZ"
}

count_bundles() {
  if [ ! -d "$RUNS_DIR" ]; then
    echo 0
    return
  fi

  bundle_count=0
  while IFS= read -r _bundle_path; do
    bundle_count=$((bundle_count + 1))
  done < <(find "$RUNS_DIR" -mindepth 1 -maxdepth 1 -type d ! -name experiments -print)
  echo "$bundle_count"
}

append_log() {
  status="$1"
  count="$2"
  printf "%s source=%s rsync_status=%s bundle_count=%s\n" \
    "$(timestamp_utc)" "$RUNS_DIR" "$status" "$count" >> "$DEST/backup.log"
}

if [ ! -d "$RUNS_DIR" ]; then
  echo "backup_runs.sh: source runs directory not found: $RUNS_DIR" >&2
  if mkdir -p "$DEST" 2>/dev/null; then
    append_log "source_missing" 0
  fi
  exit 66
fi

if ! mkdir -p "$DEST/runs"; then
  echo "backup_runs.sh: failed to create backup destination: $DEST/runs" >&2
  exit 73
fi

bundle_count="$(count_bundles)"
rsync -a "$RUNS_DIR"/ "$DEST/runs"/
rsync_status="$?"
if ! append_log "$rsync_status" "$bundle_count"; then
  echo "backup_runs.sh: failed to append backup log: $DEST/backup.log" >&2
  if [ "$rsync_status" -ne 0 ]; then
    exit "$rsync_status"
  fi
  exit 74
fi

if [ "$rsync_status" -ne 0 ]; then
  echo "backup_runs.sh: rsync failed with exit status $rsync_status" >&2
  exit "$rsync_status"
fi

echo "backup_runs.sh: backed up $bundle_count bundle(s) from $RUNS_DIR to $DEST/runs"
