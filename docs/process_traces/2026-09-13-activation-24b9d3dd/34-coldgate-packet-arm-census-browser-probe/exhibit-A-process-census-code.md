# Exhibit A — joulewise/arm_readiness_evidence_t0.py at main 4b9a34111d33a04727a09127a1c1fbd8aab87052: the fresh probe, the absent-check and the process census

```python
476:def _fresh_probe(
477-    context: _Context,
478-    kind: str,
479-    label: str,
480-    argv: _Sequence[str],
481-) -> _ProbeResult:
482-    if kind in {"MAINTENANCE_CENSUS", "PROCESS_CENSUS"}:
483-        r1_finished = context.values.get("r1_batch_finished_monotonic_ns")
484-        if (
485-            not _real_int(r1_finished)
486-            or r1_finished > context.clock.monotonic_ns()
487-        ):
488-            raise _underivable(
489-                kind,
490-                "fresh census cannot run before the R1 clock-reference batch completes",
491-            )
492-    try:
493-        return _execute_probe(argv, cwd=context.repository)
494-    except Exception as exc:
495-        raise _underivable(kind, f"fresh {label} probe could not execute: {exc}") from exc
496-
497-
498-def _boot_probe(repository: _Path) -> tuple[str, _ProbeResult]:
# …
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
# …
def _derive_process_census(context: _Context) -> _DerivedRow:
    kind = "PROCESS_CENSUS"
    probes = (
        _fresh_probe(context, kind, "keep-awake", ("/usr/bin/pgrep", "-x", "caffeinate")),
        _fresh_probe(context, kind, "agent", ("/usr/bin/pgrep", "-lf", "codex|claude|t3")),
        _fresh_probe(context, kind, "browser", ("/usr/bin/pgrep", "-lf", "Safari|Google Chrome|Chromium|Firefox|browser automation")),
        _fresh_probe(context, kind, "monitor", ("/usr/bin/pgrep", "-lf", "powermetrics|window-chain|run_campaign|tail -f|watch")),
    )
    for label, probe in zip(("keep-awake", "agent", "browser", "monitor"), probes, strict=True):
        _expect_absent(probe, kind=kind, label=label)
    return _DerivedRow(
        "t0.no_stray_keepawake",
        kind,
        {"absent_process_classes": ["agent", "browser", "keep_awake", "monitor"], "fresh_process_census": True},
        "PROBE",
        probes=probes,
    )


```
