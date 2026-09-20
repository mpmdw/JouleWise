```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"findings","completion":"complete","summary":"E1-E4 implemented; required suites pass.","workspace":{"base_requested":"67a147c4","base_mode":"exact","head_start":"67a147c4","head_end":"67a147c4","upstream_end":null,"branch":"feat/2026-09-20-evidence-night-b2-r2"},"pathspec":["joulewise/evidence_night.py","tests/test_evidence_night.py","docs/contracts/evidence_night_entry.md","docs/process/NIGHT_HANDBACK.md"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"pending_verification"},"verification":[],"flags":[{"id":"F1","kind":"environment","level":"nonblocking","text":"Broader touched-suite failures; see notes.","needs":"Lead verification."}]}
```

## Change

- Added a boundary-specific production-provenance regression.
- Moved boundary veto observation into durable `observing-veto`, before `publishing`.
- Added the 60-second directive timeout and recorded fail-closed timeout refusal.
- Corrected both documentation clauses, added the phase table and live-validation limitation, separated provenance from “Ed,”, and captured notice stdout.

Required verification passed:

| Command | Tests |
|---|---:|
| `/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_night` | 92 |
| `/opt/homebrew/bin/python3.11 -B -m unittest tests.test_evidence_night` | 92 |
| `/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_arm_sequence tests.test_arm_retry tests.test_night_gate` | 108 |

Protected regions remain byte-identical:

- Executed→EOF: `4c71305c61b0a8e3fea6b8fb9ec8b871`
- ARM-RETRY-POLICY lines 68–144: `fc6e3a97a4a5c7a650264f9facb7eed8`

`git diff --check` passed. Diff: **4 files, 157 insertions, 28 deletions**. HEAD unchanged; no commits.

## Verification notes

Counterfactual replay loads baseline code/docs in memory without changing the checkout:

```sh
/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/b2r2-proof.py baseline
```

All six selected tests fail against `67a147c4`; mode `current` passes. E1’s baseline failure is its phase assertion—the production gate already existed. Mode `no-boundary-gate` independently proves that deleting that gate reaches the forbidden installer seam and fails. Modes `no-timeout-request` and `no-timeout-forward` also fail.

The timeout test runs a real sleeping subprocess with a shortened test deadline while asserting that production supplies `timeout=60`.

The repository-required broader run:

```sh
/Users/edr/code/JouleWise/.venv/bin/python -B scripts/quick_suite.py --tier touched --since 67a147c4
```

finished with **169 modules, 76 excluded, 4 failing modules**:

- `test_axi_controller_events`: two failures reporting unavailable campaign process identity.
- `test_night_agent_install`: one diagnostic mismatch caused by unavailable `pgrep` process census.
- `test_sample_quiet_predicate_evidence`: CPU-budget assertion; isolated replay passed.
- `test_run_night`: six instances of the known 8-second watchdog artifact, ignored as directed.

Full output: [touched-suite log](/tmp/b2r2-touched.log).

## Residual risk

Lead verification remains: review the diff and rerun the process-observation failures outside this sandbox. Successful real-`launchctl` installation remains PROVISIONAL until the bench’s first live use.