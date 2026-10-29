#!/usr/bin/env bash
# Host-level passive sampler: load, memory, every python process (incl. spawned workers).
out=$1; every=${2:-10}
while true; do
  {
    echo "== $(date -u +%FT%TZ) load=$(cut -d' ' -f1-4 /proc/loadavg)"
    grep -E '^(MemAvailable|SwapTotal|SwapFree):' /proc/meminfo | tr -s ' ' | paste -sd' '
    ps -eo pid,ppid,nlwp,rss,pcpu,etimes,args --sort=-pcpu | grep -E 'python|PID' | grep -v grep | head -20 | cut -c1-200
  } >> "$out"
  sleep "$every"
done
