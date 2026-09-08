WRITE_SCOPE: ["scripts/window_status.sh","scripts/run_night.py","scripts/run_campaign.py","joulewise/measurement_liveness.py","tests/test_window_status_guard.py","tests/test_measurement_liveness.py","tests/test_run_night.py","tests/test_run_campaign.py"]

# Seat brief — WINDOW-STATUS-GUARD-CENSUS-01 redesign per the rule-11 consult (gpt-6-astra, high)

Ruling of record: docs/process_traces/2026-09-08-handoff-redo/94-consult-window-guard-astra-report.md (it is NOT in this checkout; read it in full with `cat /private/tmp/claude-501/-Users-edr-code-JouleWise/1d65b6ea-5518-4207-8f65-31f8bf376204/scratchpad/runs/consult-window-guard.md`). The argv classifier is RETIRED; liveness markers with (pid, start token) identity govern; campaign markers auto-discovered via a registry entry. Implement the consult's SEAT BRIEF below exactly; start from main (the earlier classifier branch is abandoned). RULING on the acceptance conflict: the explicit prohibition governs — run ONLY the named module groups (tests.test_window_status_guard tests.test_measurement_liveness tests.test_run_night tests.test_run_campaign) plus `bash -n`; never `unittest discover`; no git commit; header < 8192 bytes; genre implementation verdict keys.

## SEAT BRIEF

**Objective:** Replace `window_status.sh` argv classification with the census specified above. Preserve publication and freeze behavior. No live captures, pushes, commits, watchdog installation, or changes to immutable custody.

**WRITE_SCOPE — exact paths:**

- `scripts/window_status.sh`
- `scripts/run_night.py`
- `scripts/run_campaign.py`
- `joulewise/measurement_liveness.py`
- `tests/test_window_status_guard.py`
- `tests/test_measurement_liveness.py`
- `tests/test_run_night.py`
- `tests/test_run_campaign.py`

**Deliverables:**

1. Shared identity, marker parsing, registry publication/cleanup, and census implementation in `joulewise/measurement_liveness.py`, with an injectable identity observer.
2. Chain-child `start_time` recording; preserve existing once-only and exit semantics.
3. Additive campaign start identity and production-only registry publication at ordinary and AXI execution acquisitions. Preserve existing campaign-lock ownership and stale-repair semantics.
4. Status shell invokes the marker census before any write; remove argv classification and its test hook.
5. Temporary-root fixtures for every changed test. No reads of host custody, no host process census, and no registry writes under the real home directory.
6. Return a clause map linking each behavior to its production site, biting assertion, and executed counterfactual. Lead owns bookkeeping and deployment.

**Deterministic regressions and counterfactuals:**

| Assertion | Counterfactual it must catch |
|---|---|
| Open chain with matching PID/start refuses before any status write or Git action | Ignore chain markers |
| Closed chain permits publication when no campaign is live | Ignore `chain.exited` |
| Same PID with different start token warns and permits | Compare PID alone |
| Dead PID with stale markers permits | Refuse on file existence alone |
| Legacy live-PID or malformed open marker refuses as indeterminate | Treat parse/identity uncertainty as empty census |
| `courier.sent` cannot suppress a live chain/campaign | Short-circuit on sent |
| Production campaign in an unrelated, spaced runs directory refuses | Inspect only `$REPO/runs` |
| Ordinary and AXI execution publish before mocked child launch | Remove either registration call |
| Exceptions release owned registry entries; replacement entries survive cleanup | Unconditionally unlink by pathname |
| Dead owner leaves harmless stale registry entry | Treat stale entry as live |
| Dry-run and maintenance-only acquisition publish no measurement entry | Register every lock acquisition |
| Mentions in editors, prompts, test names and paths do not affect output | Restore argv classifier |
| Live marker under a path containing `unittest` still refuses | Restore global word exemption |
| Freeze sentinel still permits local status write but prevents publication after a clear census | Move or remove freeze branch |
| Root/probe error refuses before status/Git mutation | Convert observation error to clear |

Test the shell with fake identity-probe executables and temporary custody. Mock measurement subprocesses in writer tests. Replace the old command-shape tests with marker-state assertions; install a failing `ps` stub to prove regression tests never consult host processes.

**Acceptance modules:**

```text
python3 -m unittest tests.test_measurement_liveness tests.test_window_status_guard
python3 -m unittest tests.test_run_night tests.test_run_campaign
python3 -m unittest tests.test_launch_window tests.test_magistrate_watchdog
python3 -m unittest discover -s tests
bash -n scripts/window_status.sh
git diff --check
```

Final handoff must report actual results, exact changed paths, clause-map counterfactual results, and the documented hand-launch/orphan/snapshot limitations. No fixture result may be described as live quiet-Mac validation.
