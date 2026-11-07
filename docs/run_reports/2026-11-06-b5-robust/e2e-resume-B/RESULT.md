# Block-5 synthetic-chain resume equality — Case B

## Verdict

**EQUAL.** After the required exclusions, the reference run and the
interrupted-then-resumed run have the same record digest, joined-driver exit,
and 1,336-entry file manifest. There are no remaining path-level differences.

This is the expected normal `--stop-after` closure: each harness invocation
exited 1 and each joined driver exited 2 when the step after 3b refused with
`synthetic_stop_after`. No Python traceback occurred, both `summary.json`
files were produced, and the requested interrupt occurred.

## Environment

| Item | Value |
|---|---|
| Git HEAD | `9eb90c6c5b5c4683f5f4be61fbe599e945d6f1c1` |
| Python | `Python 3.12.13` |
| `nproc` | `3` |
| Workers | `2` |
| Reference A wall time | `660.950529836 s` |
| Interrupted + resumed B wall time | `1370.888351925 s` |
| Reference A harness exit | `1` (expected) |
| Interrupted + resumed B harness exit | `1` (expected) |

Wall times are elapsed wall-clock measurements around each complete harness
invocation, including setup/restore work performed by that invocation.

## Commands

The requested run commands were executed from the repository root. Standard
output and standard error were redirected to separate `/tmp/jwr` capture files
so the latter could be copied into this report bundle.

```bash
mkdir -p /tmp/jwr/tmp && TMPDIR=/tmp/jwr/tmp python3 -B scripts/b5_e2e_synthetic.py --scratch /tmp/jwr/run --out /tmp/jwr/out/A --workers 2 --stop-after 3b
rm -rf /tmp/jwr/run
TMPDIR=/tmp/jwr/tmp python3 -B scripts/b5_e2e_synthetic.py --scratch /tmp/jwr/run --out /tmp/jwr/out/B --workers 2 --stop-after 3b --interrupt-after-step 3b
git rev-parse HEAD
python3 --version
nproc
```

The comparison read only the two harness `summary.json` files. It compared
`record_sha256`, `exit_code`, and the `manifest` mapping after dropping:

1. every path containing `/restricted/resume/`;
2. every `restricted/logs/runtime-phases.jsonl` path;
3. every `restricted/logs/runtime-vdl-counters.json` path; and
4. every `restricted/logs/runtime-stack-*.txt` path.

No file beneath a `restricted/` directory was opened.

## Comparison

| Field | Reference A | Interrupted + resumed B | Result |
|---|---|---|---|
| `record_sha256` | `e34e60a244cf6fee7a40c52fa863fce112d6988abf02a6a6a38764280e3ecd19` | `e34e60a244cf6fee7a40c52fa863fce112d6988abf02a6a6a38764280e3ecd19` | EQUAL |
| Joined-driver `exit_code` | `2` | `2` | EQUAL |
| Filtered manifest path count | `1336` | `1336` | EQUAL |
| Remaining path-level differences | `0` | `0` | EQUAL |

### Remaining path-level differences

None. Consequently, there are no path/A-digest/B-digest rows to list.

## B interruption/resume evidence

### Requested B stderr lines

There were no B stderr lines beginning with `resume` or `interrupted` (B's
captured stderr is empty). For clarity, the harness emitted
`interrupted; resuming` on **stdout**, not stderr.

### B manifest paths under `restricted/resume/`

Count: **3**. Names only (all entries, below the 20-name limit):

1. `dry-run/restricted/resume/abandoned/1/logs/runtime-phases.jsonl`
2. `dry-run/restricted/resume/abandoned/1/logs/runtime-stack-6235.txt`
3. `dry-run/restricted/resume/recovery.jsonl`

These names came exclusively from B's `summary.json` manifest; the named files
were not opened.

## Preserved artifacts

- `A-summary.json` — exact copy of reference A's harness summary.
- `B-summary.json` — exact copy of interrupted + resumed B's harness summary.
- `A.stderr` — exact capture of reference A's stderr (empty).
- `B.stderr` — exact capture of interrupted + resumed B's stderr (empty).
