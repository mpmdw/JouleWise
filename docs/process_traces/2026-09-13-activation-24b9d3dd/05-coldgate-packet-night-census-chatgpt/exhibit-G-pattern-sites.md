# Exhibit G — every site at 27957b60 that carries the census pattern (rg over tracked files, process traces and docs/legacy excluded)

```
./joulewise/t0_rehearsal.py:52:_AGENT_TOKEN_RE = re.compile(r"(?:^|[/\s])(codex|claude|t3)(?:[/\s]|$)", re.I)
./RUN_STATE.md:15:**T38p (2026-09-13 ~06:00 PDT) — EQUIVALENCE NIGHT REFUSED AT t0 (AGENT PRESENT); HARVESTED AND UNINSTALLED; RE-PLAN FOR 09-15.** Headless activation `c5048879` (launched 05:34:22 af
./joulewise/arm_readiness_evidence_t0.py:1724:        _fresh_probe(context, kind, "agent", ("/usr/bin/pgrep", "-lf", "codex|claude|t3")),
./tests/test_arm_readiness_evidence_t0.py:2509:                ("/usr/bin/pgrep", "-lf", "codex|claude|t3"),
./tests/test_arm_readiness_integration.py:418:            ("codex|claude|t3", "PROCESS_CENSUS"),
./joulewise/night_gate.py:42:AGENT_CENSUS_ARGV = ("/usr/bin/pgrep", "-lf", "codex|claude|t3")
./tests/test_night_gate.py:298:            ("/usr/bin/pgrep", "-lf", "codex|claude|t3"),
./scripts/gen_derivation_night.py:58:# joulewise/night_gate.py:42 censuses `pgrep -lf "codex|claude|t3"` every 30 s
./tests/test_gen_derivation_night.py:409:        """`pgrep -lf "codex|claude|t3"` aborts the night on its own argv.
./scripts/prewindow_check.sh:149:  procs="$(ps aux | grep -E "codex|claude|t3|mcp-server|run_campaign|window-chain" | grep -vc grep)"
./docs/process/NIGHT_HANDBACK.md:196:`night_refused_agent_present` (census `pgrep -lf codex|claude|t3` exit 0:
./docs/phase_2/derivation_night_runbook.md:357:     "$MEASUREMENT_ROOT" "$CALIBRATION_PLAN" | grep -iE 'codex|claude|t3'; then
./tests/test_arm_readiness_schemas.py:1810:        "census": {"argv": ["/usr/bin/pgrep", "-lf", "codex|claude|t3"],
```

## joulewise/t0_rehearsal.py lines 45–70 (the token regex used by the rehearsal census)
```python
PROCESS_LINEAGE_SCHEMA = "joulewise.t0_unattended_process_lineage.v1"
LIFECYCLE_SCHEMA = "joulewise.t0_unattended_lifecycle.v1"
FALSIFIER_SCHEMA = "joulewise.t0_unattended_falsifier_controls.v1"
POSITIVE_CONTROL_SCHEMA = "joulewise.t0_unattended_anchor_positive_control.v1"

_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_HID_IDLE_RE = re.compile(r'^\s*"HIDIdleTime"\s*=\s*([0-9]+)\s*$')
_AGENT_TOKEN_RE = re.compile(r"(?:^|[/\s])(codex|claude|t3)(?:[/\s]|$)", re.I)
_CLOCK_ROW_DEFINITION = {
    "applicability_rule": "ALWAYS",
    "evaluation_phase": "ARM_ONLY",
    "predicate_id": "clock.correct_and_prior_state.v1",
    "required_evidence_kinds": ["CLOCK_ATTESTATION"],
    "row_id": "clock.correct_and_prior_state",
}
_LIFECYCLE_STAGES = (
    "launch",
    "capability_consumption",
    "capture",
    "claim_backup",
    "bound_backup",
    "close_out",
    "restore",
)
_EXECUTION_KEYS = {"schema_version", "sequence_completed", "processes"}
_EXECUTION_PROCESS_KEYS = {
```

## joulewise/arm_readiness_evidence_t0.py lines 1300–1345 (own-vs-foreign classification at the arm census, if present)
```python
    _capture_ok(capture, kind=kind, label="prewindow readiness wait")
    if capture["argv"] != manifest["prewindow_command"]:
        raise _underivable(kind, "prewindow capture differs from the frozen command")
    if capture["finished_monotonic_ns"] - capture["started_monotonic_ns"] < _MIN_IDLE_NS:
        raise _underivable(kind, "prewindow capture does not prove the required ten-minute idle")
    if "TIMED OUT" in capture["stdout"] or "BLOCK" in capture["stdout"] or _re.search(
        r"READY after [0-9]+ min\.", capture["stdout"]
    ) is None:
        raise _underivable(kind, "prewindow capture does not end in READY")
    return capture, identity, artifacts


def _expect_absent(result: _ProbeResult, *, kind: str, label: str) -> None:
    if result.exit_code != 1 or result.stdout.strip():
        raise _underivable(kind, f"fresh {label} census found a forbidden process")


def _maintenance_probe(context: _Context, *, kind: str) -> _ProbeResult:
    probe = _fresh_probe(
        context,
        kind,
        "maintenance",
        (
            "/usr/bin/pgrep",
            "-lf",
            "XProtect|mds_stores|mdworker|mdbulkimport|backupd|photoanalysisd|softwareupdated|Spotlight|mediaanalysisd",
        ),
    )
    _expect_absent(probe, kind=kind, label="maintenance")
    return probe


def _derive_background_quiet(context: _Context) -> _DerivedRow:
    kind = "MAINTENANCE_CENSUS"
    _prewindow, prewindow_identity, manifest_artifacts = _prewindow_capture(context, kind=kind)
    probe = _maintenance_probe(context, kind=kind)
    return _DerivedRow(
        "t0.background_quiet",
        kind,
        {"observation_status": "PASS", "fresh_maintenance_census": True},
        "PROBE",
        input_artifacts=(prewindow_identity, *manifest_artifacts),
        probes=(probe,),
    )


```
