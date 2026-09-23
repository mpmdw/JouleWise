```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Use shared disk evidence and enforce successor eligibility at the production install boundary; the current successor policy has no production caller.",
  "workspace": {
    "base_requested": "313efcca",
    "base_mode": "exact",
    "head_start": "313efcca236a8c914e4956fc7d686a810060e5ea",
    "head_end": "313efcca236a8c914e4956fc7d686a810060e5ea",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "F1", "severity": "blocker", "text": "successor_arm_allowed has no production caller; ordinary installation can bypass D-182 eligibility."},
      {"id": "F2", "severity": "should_fix", "text": "The receipt is written once by the driver; a shared disk scan is preferable, but must reject missing custody and symlinked scan roots."},
      {"id": "F3", "severity": "should_fix", "text": "A270 needs a separate captured-abort eligibility door, with shared one-successor controls."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "rg -n 'successor_arm_allowed\\(' joulewise scripts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["joulewise/arm_retry.py:287:def successor_arm_allowed(now_epoch_s, plan, notice, result, receipt, delivery) -> Decision:"]
      },
      "expected": {"exit_code": 0, "tail_regex": "joulewise/arm_retry.py:287:def successor_arm_allowed"}
    }
  ],
  "flags": [
    {"id": "G1", "kind": "verification_gap", "level": "nonblocking", "text": "Read-only consult; no tests or live arm were run.", "needs": ""}
  ]
}
```

## Findings

**F1 — Q2, production call site.** Confirmed: `successor_arm_allowed` is defined but never called by production Python code ([arm_retry.py](/Users/edr/code/wt-1d3796d5-consult/joulewise/arm_retry.py:287)). Today the tracked evidence-night route is `prepare → check → notice → veto → publish-install → verify` ([NIGHT_HANDBACK.md](/Users/edr/code/wt-1d3796d5-consult/docs/process/NIGHT_HANDBACK.md:711)). `prepare` creates the candidate, while the generic [night_plan_writer.py](/Users/edr/code/wt-1d3796d5-consult/joulewise/night_plan_writer.py:50) only writes plan bytes. `check` consults `classify_abort`, explicitly leaving full retry clearance to the lead ([evidence_night.py](/Users/edr/code/wt-1d3796d5-consult/joulewise/evidence_night.py:1019)). `publish_install` then publishes and invokes the installer without successor clearance ([evidence_night.py](/Users/edr/code/wt-1d3796d5-consult/joulewise/evidence_night.py:1410)). There is no `evidence_night arm` command ([evidence_night.py](/Users/edr/code/wt-1d3796d5-consult/joulewise/evidence_night.py:1587)).

Call `successor_arm_allowed` inside `publish_install`, immediately before publication, using durable predecessor lineage bound to the candidate. Make the check authoritative in the common [night_agent_install.validate_install](/Users/edr/code/wt-1d3796d5-consult/joulewise/night_agent_install.py:1083) path as well: the runbook permits direct `install_night_agent.sh` installation ([NIGHT_HANDBACK.md](/Users/edr/code/wt-1d3796d5-consult/docs/process/NIGHT_HANDBACK.md:1126)). A caller-supplied `successors_used: 0` alone is inadequate; it must come from preserved lineage and prior-install records ([arm_retry.py](/Users/edr/code/wt-1d3796d5-consult/joulewise/arm_retry.py:277)). The installer must reject an attempted successor whose required lineage is omitted, so removing a flag cannot turn it into an ordinary first arm.

**F2 — Q1, Q3, Q4.** Choose **B**, with a separate, immutable harvest attestation if a durable snapshot is needed. The driver creates `night/receipt.json` exclusively at the gate ([run_night.py](/Users/edr/code/wt-1d3796d5-consult/scripts/run_night.py:183), [run_night.py](/Users/edr/code/wt-1d3796d5-consult/scripts/run_night.py:3060)); harvest copies custody byte-exact ([NIGHT_HANDBACK.md](/Users/edr/code/wt-1d3796d5-consult/docs/process/NIGHT_HANDBACK.md:1058)). Rewriting C5 after the fact would change the gate’s receipt. The eligible live shape indeed lacks the demanded field: [arm_retry.py](/Users/edr/code/wt-1d3796d5-consult/joulewise/arm_retry.py:247) requires it, while production searches found references but no writer.

Move the watchdog’s disk scan into one `joulewise` implementation used by release and successor eligibility ([magistrate_watchdog.py](/Users/edr/code/wt-1d3796d5-consult/scripts/magistrate_watchdog.py:851)). Require a readable, regular custody directory and verified completed harvest; inspect the retained source at arm time. A missing or torn archive must deny. Treat symlinked custody or scan roots as present/unknown. The current scanner treats a wholly missing root as empty, and its reservation walk skips a symlinked nested directory unless its *name* ends in `.consumed.json` ([magistrate_watchdog.py](/Users/edr/code/wt-1d3796d5-consult/scripts/magistrate_watchdog.py:801), [magistrate_watchdog.py](/Users/edr/code/wt-1d3796d5-consult/scripts/magistrate_watchdog.py:831)). Its direct capture locations already reject symlinks ([magistrate_watchdog.py](/Users/edr/code/wt-1d3796d5-consult/scripts/magistrate_watchdog.py:836)). A partial harvest or missing custody therefore needs an explicit fail-closed gate, not an absence inference.

Production-boundary regressions should show: delivered live-shaped refusal permits one fresh successor; a bare C5 row without disk proof denies; `chain.started`, any reservation marker, either capture location, or a nonempty envelope index denies; a second successor denies. Add missing/torn custody and symlink cases. The existing tests mostly exercise fabricated C5 evidence directly ([test_arm_retry.py](/Users/edr/code/wt-1d3796d5-consult/tests/test_arm_retry.py:453)).

**Q4 proposed implementation `WRITE_SCOPE`:** `joulewise/zero_capture_evidence.py`, `joulewise/arm_retry.py`, `joulewise/evidence_night.py`, `joulewise/night_agent_install.py`, `joulewise/night_gate.py`, `joulewise/night_plan_writer.py`, `scripts/magistrate_watchdog.py`, `tests/test_arm_retry.py`, `tests/test_evidence_night.py`, `tests/test_night_agent_install.py`, `tests/test_magistrate_watchdog.py`, `docs/process/NIGHT_HANDBACK.md`. The plan files are included for sealed predecessor lineage; the implementation seat should narrow this list if it can bind lineage without changing the plan schema.

**F3 — A270 and Q5.** Shape eligibility as two typed predicates feeding common delivery, lineage, spacing, notice, veto, install-close, and one-use checks. Keep `zero_capture_successor_allowed` strictly zero-capture: *any* start, reservation, or capture fact denies. A270 adds `captured_abort_successor_allowed` for the exact `non_observer_process_busy` abort, authenticated captured count below registration `minimum_retained`, and archived byte-exact envelopes ([D-182 addendum](/Users/edr/code/wt-1d3796d5-consult/docs/decision_log.md:12032)). Do not make the zero-capture predicate accept 1–7 captures. The brief’s “symlinks count as present” claim is too broad for the current reservation walk. Its “every live receipt returns `missing_zero_capture_evidence`” applies to otherwise eligible gate refusals, not all receipts: the terminal predicate first rejects other reasons and positive capture claims ([arm_retry.py](/Users/edr/code/wt-1d3796d5-consult/joulewise/arm_retry.py:202)).

## Residual risk

The common installer and tracked entry point both need lineage-bound tests. Testing only `arm_retry.py` would leave the present production bypass intact.