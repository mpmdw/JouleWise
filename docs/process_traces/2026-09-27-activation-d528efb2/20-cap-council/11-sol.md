```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend route R with a measured cadence range, a fresh registered reissue corpus, and clock-source investigation before claim windows.",
  "workspace": {
    "base_requested": "e7c8bcc6",
    "base_mode": "descendant",
    "head_start": "00c399da62702f6f79ef70d58618524c1e27b2d8",
    "head_end": "00c399da62702f6f79ef70d58618524c1e27b2d8",
    "upstream_end": "e7c8bcc68d9a1c4f20e11c1904e49552c81ffcd1",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "F1", "severity": "should_fix", "text": "A reissue using only the original 12 would retain the old cap's cadence selection; re-evaluating excluded ledger rows would change immutable dispositions after their diagnostic B values became known."},
      {"id": "F2", "severity": "should_fix", "text": "The August max-plus-percentage rule has no demonstrated coverage at the launch context's longer frame lengths."},
      {"id": "F3", "severity": "should_fix", "text": "A nonsignificant association between cells and B does not establish absence of selection bias in future measurement energy."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse main origin/main e7c8bcc6 HEAD && git merge-base --is-ancestor e7c8bcc6 HEAD && git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["00c399da62702f6f79ef70d58618524c1e27b2d8", "## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "## HEAD \\(no branch\\)"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "## HEAD \\(no branch\\)"}
    }
  ],
  "flags": [
    {"id": "R1", "kind": "residual_risk", "level": "nonblocking", "text": "The existing 25G83 captures do not measure cell need at the launch context's upper frame lengths; the proposed sizing rule can remain unfulfilled until that range is observed.", "needs": "Lead to obtain prospective cell-only coverage or keep the claim-window hold."}
  ]
}
```

SEAT: Sol 6.0 — CAP-COUNCIL-25G83-01

## Findings

**F1 — Use a fresh corpus for the later reissue.** The cap is a reproducible limit on branch-and-bound work across all pulses, with a separate 120-second host safety deadline. It guards against pathological loss surfaces; it is not a memory limit or a physical threshold. Exhaustion discards every partial fit. A frame or pulse count alone cannot safely replace it: a flat lower bound can expand toward \(2^{28}\) leaves for *one* pulse. A cadence-dependent formula might be useful after validation, but changing either the constant or its mechanism rotates a D-138-pinned estimator input and requires the atomic reissue and dependent pin updates. `joulewise/powermetrics_fiducial.py:77–92,524–550,636–696,992–1010`; `tests/test_powermetrics_fiducial.py:641–644`; `docs/decision_log.md:10361–10380`.

**Recommend route R.** Keep the `dbad7cc7` issuance and its 12 members exactly as recorded. Do not turn the eight capped rows into members: their ledger dispositions are immutable, and their diagnostic B values are disclosed. Reissuing with only the original 12 would preserve selection by the old cap even after that filter is removed. Register fixed fresh slots under the final estimator bytes; retain every valid, resolved result without a B-based choice. The same fresh, non-claim captures can serve as the reissue corpus *and* H2’s cap-stop check if both purposes and failure rules are fixed before capture. These are recommendations and inferences from the membership rule and A1, not changes to the current issuance. `configs/calibration/preregistration_d079_epoch_25g83_rev1.md:156–177,610–614`; `docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/21-science-gate-ruling.md:29–45,180–193`; `docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/31-addendum-ruling.md:125–139,158–170`.

**F2 — Write this sizing rule before computing a value.** Proposed covered range: **127.5–136.0 ms per-capture median native frame length**, spanning the observed 127.6–130.2 ms and the registration’s 134.8 ms launch-context p95 with room above it. Freeze the complete estimator code first. Let \(D\) contain exact full-fit cell counts and frame medians from every clock-resolved W1/W2 capture, plus consecutive, prospectively declared **cell-only** pilot captures under the registered launch context and those frozen code bytes. Require at least three pilot medians in 130.5–<133 ms and three in 133–136 ms; otherwise **do not compute a cap or clear route R**. Set the fixed per-capture cap to \(1000\lceil1.25\max_{i\in D}(\text{cells}_i)/1000\rceil\). Read no B in sizing. Treat August counts as a historical check, not sizing observations; use the launch-context table to set the range, not to invent cell counts. A later code change restarts sizing. This rule deliberately waits for measured upper-range counts instead of extending the 7,500-cells/ms fitted line beyond its data. Outside 127.5–136.0 ms, flag the cadence as out of scope and withhold the **whole claim window** pending a new rule; do not silently drop its bracket. Then require at least 24 distinct, fixed-plan non-claim captures under the new cap, zero cap stops, and observed upper-range coverage before clearing H2. The bin counts, 25% allowance and whole-window response are my proposed design choices, not established guarantees. `docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/31-addendum-ruling.md:81,158–170`; `docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/21-science-gate-ruling.md:55–85`.

**Sequence and cost.** (1) Issue `dbad7cc7` with the four unchanged digests. (2) Investigate clock steps and decide which staged estimator branches belong in the *later* D-138 transaction; freeze that combined estimator before counting cells. (3) Run the cell-only sizing pilot, write the resulting cap into that later atomic transaction, and reissue from a newly registered corpus. (4) Complete the ≥24 non-claim captures and the clock ruling. (5) Once the final calibration is issued and the headline pipeline frozen, run Ed’s three-family full-system audit on the final system; only then arm a claim window. If that audit runs on the earlier issuance first, the successor still needs review. Inference: the cheapest successful schedule is roughly one 12-slot sizing window plus two 12-slot validation/reissue windows, at least two days including the intervening code transaction; upper-cadence scarcity or a failed zero-stop check adds windows, so there is no honest fixed completion date. A1 expressly separates the current issuance from the cap change; the recorded #416 trigger is issuance plus pipeline freeze. `docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/31-addendum-ruling.md:125–139,158–166`; `docs/process_traces/2026-09-27-activation-77b1bee2/00-activation-record.md:25–32`; `configs/calibration/preregistration_d079_epoch_25g83_rev1.md:99–110,610–614`.

**Clock steps (H4).** Five milliseconds is the current anchor-v3 *admission policy*, not evidence that physical clock drift becomes invalid at precisely 5 ms. The code also has a distinct v3.1 model allowing 25 ppm sustained drift with a 15 ms backstop while pricing the drift into uncertainty; adopting it for this calibration would require its own identity and reissue ruling. First compare the retained paired wall/monotonic stamps around W1 d08, W1 d11 and W2 d07 with existing `timed` unified logs and `pmset -g log`: locate when offset changed and check for time synchronization or sleep/wake events. This is read-only forensic work, with no agent-session quiet capture. Five readings may narrow an interval without proving whether it was a step or slew; if logs are missing, seek a separately planned, agent-free diagnostic clock log. `joulewise/uncertainty_evidence.py:39–80,1090–1125`; `docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/21-science-gate-ruling.md:39–47`.

**F3 — Qualify two conclusions.** A1 correctly identifies a plausible energy-filter mechanism, but its assertion that the old calibration describes future surviving measurements is conditional on future machine states resembling these 24 captures. Likewise, \(r=-0.05\) and permutation \(p=0.44\) in 20 computable captures do not prove no B selection, and say nothing directly about workload energy. D-143’s 20.3% margin exceeded the *August* spread, but was not a cadence-range guarantee; the eight healthy 25G83 cap stops demonstrate that limit. These are inferences from the small observed set, the stated conditional mechanism and the later result. `docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/21-science-gate-ruling.md:55–85`; `docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/31-addendum-ruling.md:143–156`; `joulewise/powermetrics_fiducial.py:77–88`.

## Residual risk

Even zero stops in 24 validation captures cannot guarantee zero future stops. Route R should claim coverage only over the measured frame range and retain per-cause records for every attempted bracket. `docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/31-addendum-ruling.md:160–166`.