# Exhibit A — joulewise/night_gate.py at 27957b60 (t0 agent census)

```python
# a night plan's registration_path points at it (repo-relative or absolute).
D166_REGISTRATION_PATH = (
    "configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json"
)
AGENT_CENSUS_ARGV = ("/usr/bin/pgrep", "-lf", "codex|claude|t3")

PMSET_BATT_ARGV = ("/usr/bin/pmset", "-g", "batt")
PMSET_GENERAL_ARGV = ("/usr/bin/pmset", "-g")
HID_IDLE_ARGV = (
# …
def agent_census(probes: CensusProbes) -> tuple[ProbeResult, Refusal | None]:
    try:
        result = _run(probes, AGENT_CENSUS_ARGV)
    except ProbeError as exc:
        try:
            observed_monotonic_ns = _safe_monotonic_ns(probes)
        except ProbeError as clock_exc:
            observed_monotonic_ns = 0
            exc = ProbeError(f"{exc}; {clock_exc}")
        result = ProbeResult(
            argv=AGENT_CENSUS_ARGV,
            exit_code=-1,
            stdout="",
            stderr=str(exc),
            monotonic_ns=observed_monotonic_ns,
        )
        return result, Refusal("night_probe_error", str(exc), (result,))
    if result.exit_code == 1 and result.stdout.strip() == "":
        return result, None
    lines = result.stdout.strip().splitlines()
    detail = f"pgrep exit {result.exit_code}"
    if lines:
        shown = lines[:20]
        bounded = "\n".join(shown)
        if len(lines) > len(shown):
            bounded += f"\n… (+{len(lines) - len(shown)} more)"
        detail += f"; forbidden process output: {bounded}"
    return result, Refusal("night_refused_agent_present", detail, (result,))

```
