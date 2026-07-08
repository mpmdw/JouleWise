# 2K Live Verification Checklist

Status: checklist only. This file makes no live-hardware claims.

Use for the first live NVIDIA/vLLM + nvidia-smi + SSH contact. Record command
stdout/stderr excerpts, bundle paths, and any `[N/A]` rows as evidence in the
Phase 1 exit checklist or linked run report.

## 1. SSH/SCP Transport

1. Confirm OpenSSH alias/auth outside JouleWise:
   ```sh
   ssh -o BatchMode=yes -o ConnectTimeout=10 -- <alias> true
   ```
   Expected evidence: exit 0, no password prompt.

2. Confirm SCP with the same alias:
   ```sh
   tmp="$(mktemp)"
   printf 'joulewise\n' > "$tmp"
   scp -o BatchMode=yes -o ConnectTimeout=10 -- "$tmp" <alias>:/tmp/joulewise-scp-check.txt
   ssh -o BatchMode=yes -o ConnectTimeout=10 -- <alias> cat /tmp/joulewise-scp-check.txt
   ```
   Expected evidence: copied text is `joulewise`; argv has `--` before the
   destination for SSH and before operands for SCP.

Protocol pins checked: B-4, B-7, B-14 superseded by B-33.

## 2. Worker Ship And Generated Run Isolation

3. Run one generated-id smoke config with no `run_id` field:
   ```sh
   python3 -m joulewise.cli run configs/examples/nvidia_vllm_ssh.json --runs-dir runs/live-2k
   ```
   If the example still pins `run_id`, copy it to a scratch config and remove
   only that field before running.

4. On the node, list the work root:
   ```sh
   ssh -o BatchMode=yes -o ConnectTimeout=10 -- <alias> 'find /tmp/joulewise -maxdepth 3 -type d | sort'
   ```
   Expected evidence: one top-level `/tmp/joulewise/node_worker.py`, and
   per-run `<generated_run_id>/tasks`, `<generated_run_id>/artifacts`, and
   `<generated_run_id>/state`.

5. Start two generated-id runs concurrently from two terminals, then repeat
   the node listing.
   Expected evidence: two different generated run ids; no
   `/tmp/joulewise/pending-run-id`; pidfiles and artifacts stay under their
   own run ids.

Protocol pins checked: B-2, B-3, B-6, B-8, B-15 superseded by B-34.

## 3. vLLM Runtime

6. Verify `vllm serve` readiness through JouleWise prepare:
   ```sh
   python3 -m joulewise.cli run <scratch-nvidia-config.json> --runs-dir runs/live-2k-vllm
   ```
   Expected evidence: runtime prepare metadata includes vLLM command, port,
   readiness status, and a task timeout consistent with the config path.

7. Verify warmup and streaming artifacts:
   ```sh
   latest="$(ls -td runs/live-2k-vllm/* | head -1)"
   ls "$latest/raw" "$latest/outputs" "$latest/logs"
   sed -n '1,5p' "$latest/raw/vllm_events.jsonl"
   sed -n '1,5p' "$latest/raw/vllm_tokens.jsonl"
   sed -n '1,5p' "$latest/outputs/tokens.jsonl"
   ```
   Expected evidence: raw events/tokens are node-domain timestamps; output
   tokens are controller-domain timestamps; response text exists.

8. Run an OOM probe appropriate for the RTX 3050 8GB target by increasing
   model size/context or memory utilization only in a scratch config.
   Expected evidence: OOM maps to `unsupported` / `did_not_fit`, with stderr
   or HTTP body evidence. If TinyLlama-class vLLM does not fit or vLLM setup is
   not viable on this node, record the decision point for llama.cpp-CUDA
   fallback instead of claiming vLLM applicability.

Protocol pins checked: B-24, B-25 amended by B-39, B-26, B-27, B-28.

## 4. nvidia-smi Telemetry

9. Verify power query support:
   ```sh
   ssh -o BatchMode=yes -o ConnectTimeout=10 -- <alias> \
     'nvidia-smi --query-gpu=timestamp,power.draw,temperature.gpu --format=csv,noheader,nounits -lms 100 -f /tmp/jw-nvidia-smi-check.csv & pid=$!; sleep 1; kill $pid; cat /tmp/jw-nvidia-smi-check.csv'
   ```
   Expected evidence: timestamp, numeric power, and temperature rows. If
   power is `[N/A]` or `[Not Supported]`, preserve those rows as evidence.

10. Verify timezone/offset evidence:
    ```sh
    latest="$(ls -td runs/live-2k-vllm/* | head -1)"
    python3 - "$latest" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
m = json.loads((p / "metadata.json").read_text())
print(json.dumps(m["adapters"]["telemetry"], indent=2)[:4000])
PY
    ```
    Expected evidence: worker metadata or pidfile payload contains
    `node_utc_offset_s` and optionally `node_tzname`; parser diagnostics do
    not rely on parser-local fallback for new artifacts.

11. Verify raw-to-derived artifact mapping:
    ```sh
    latest="$(ls -td runs/live-2k-vllm/* | head -1)"
    sed -n '1,5p' "$latest/raw/nvidia_smi.csv"
    sed -n '1,5p' "$latest/power_trace.csv"
    ```
    Expected evidence: raw CSV is verbatim node output; power trace timestamps
    are controller-domain derived samples.

Protocol pins checked: B-18 superseded by B-37, B-19, B-20, B-21 amended by
B-36, B-23.

## 5. Pidfile Kill Safety

12. Create a stale vLLM pidfile pointing at the current shell PID but a
    mismatched command, then run cleanup:
    ```sh
    ssh -o BatchMode=yes -o ConnectTimeout=10 -- <alias> 'mkdir -p /tmp/joulewise/stale-test/state; printf "{\"pid\":%s,\"command\":[\"not-this-process\"],\"node_started_at_s\":1}\n" "$$" > /tmp/joulewise/stale-test/state/vllm.pid'
    ```
    Dispatch a runtime cleanup task against `run_id=stale-test` or run the
    equivalent worker command with a cleanup task JSON.
    Expected evidence: cleanup succeeds with stale-pidfile metadata, removes
    `vllm.pid`, and does not signal the shell.

13. Repeat for `nvidia_smi.pid` and telemetry `stop_sampling`.
    Expected evidence: structured failure, no CSV artifact, pidfile removed,
    and no signal to the mismatched process.

Protocol pins checked: B-6, B-21 amended by B-36.

## 6. Clock Alignment Re-Derivation

14. Re-derive one nvidia-smi timestamp:
    ```sh
    latest="$(ls -td runs/live-2k-vllm/* | head -1)"
    python3 - "$latest" <<'PY'
import csv, json, pathlib, sys
from joulewise.adapters.nvidia_smi import parse_nvidia_smi_csv
p = pathlib.Path(sys.argv[1])
m = json.loads((p / "metadata.json").read_text())
alignment = next(a for a in m["adapters"]["telemetry"]["clock_alignments"] if a["stage"] == "telemetry.stop_sampling")
raw = (p / "raw" / "nvidia_smi.csv").read_text()
rows = parse_nvidia_smi_csv(raw, node_utc_offset_s=m["adapters"]["telemetry"].get("worker_metadata", {}).get("node_utc_offset_s"))
with (p / "power_trace.csv").open(newline="") as h:
    first = next(csv.DictReader(h))
print(rows[0].node_timestamp_s - alignment["offset_estimate_s"])
print(first["timestamp_s"])
PY
    ```
    Expected evidence: the two printed timestamps match within floating-point
    formatting tolerance. If timezone metadata is nested only in worker
    pidfile metadata, pass that recorded offset to the parser and record the
    source path.

15. Re-derive one vLLM token/event timestamp similarly from
    `raw/vllm_tokens.jsonl` and the `runtime.run_workload` alignment.
    Expected evidence: raw node-domain timestamp minus persisted offset equals
    the converted output token timestamp.

Protocol pins checked: B-5, D-002, B-35.

## 7. De-Provisionalization Notes

Mark these pins as de-provisionalized only after evidence above is recorded:
B-2, B-3, B-4, B-5, B-6, B-7, B-14 superseded by B-33, B-15 superseded by
B-34, B-18 superseded by B-37, B-19, B-20, B-21 amended by B-36, B-23,
B-24, B-25 amended by B-39, B-26, B-27, B-28, B-29 amended by B-34.
