```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"findings","completion":"complete","summary":"C1-C3 implemented; required suites pass.","workspace":{"base_requested":"0481bb0b","base_mode":"exact","head_start":"0481bb0b17824542da33e15147caaf083ee0c575","head_end":"0481bb0b17824542da33e15147caaf083ee0c575","upstream_end":null,"branch":"feat/2026-09-20-evidence-night-lifecycle-r2"},"pathspec":["joulewise/evidence_night.py","tests/test_evidence_night.py","docs/contracts/evidence_night_entry.md"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"pending_verification"},"verification":[],"flags":[{"id":"F1","kind":"verification_gap","level":"nonblocking","text":"Broader touched suite fails; see notes.","needs":"Lead gate."}]}
```

## Change

- **C1:** Retry classification executes through the clone’s `.venv/bin/python -B -c`, with JSON input/output and clone cwd. Counterfactual fixtures prove both retry and cold-gate verdicts follow clone policy.
- **C2:** Retry inventory and prior-notice discovery read attempt records exclusively under `lifecycle/`. Tests cover both inventory locations, ignored root records, and `prepare`’s existing root-output refusal.
- **C3:** Documented all requested refusal names and moved “rehearsal, never armable” beside the `armable` definition.

Required verification passed:

| Interpreter | Tests | Result |
|---|---|---|
| Python 3.13.1 | `tests.test_evidence_night` | 69 passed |
| Python 3.11.15 | `tests.test_evidence_night` | 69 passed |
| Python 3.13.1 | `tests.test_evidence_arm_sequence tests.test_arm_retry tests.test_arm_census` | 53 passed |

Exact replay commands, cwd `.`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_night
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.11 -B -m unittest tests.test_evidence_night
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_arm_sequence tests.test_arm_retry tests.test_arm_census
```

`git diff --check` passed. `git diff --stat`: **3 files changed, 151 insertions, 34 deletions**. HEAD unchanged; no commits.

## Verification notes

Detailed evidence is outside the JSON to respect the 800-byte header limit.

The original evidence-night baseline passed **62 tests**. With new tests applied while implementation and contract remained at `0481bb0b`, all six targeted regressions failed; the same six passed after the fixes:

- `ArgumentsTests.test_lifecycle_contract_refusals_and_rehearsal_boundary`
- `LifecycleTests.test_retry_uses_clone_retry_route`
- `LifecycleTests.test_retry_uses_clone_cold_gate_route`
- `LifecycleTests.test_retry_reads_lifecycle_attempt_inventories`
- `LifecycleTests.test_retry_ignores_root_attempt_records`
- `LifecycleTests.test_notice_reuse_reads_only_lifecycle_records`

[Counterfactual failure log](/tmp/evidence-night-r2-before.log).

The repository-required broader check completed with **169 modules, 76 excluded, 4 failing modules**:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/quick_suite.py --tier touched --since 0481bb0b
```

Failures were in unchanged modules:

- `test_axi_controller_events`: two failures reporting unavailable campaign process identity; reproduced independently.
- `test_sample_quiet_predicate_evidence`: CPU-budget assertion; reproduced in a focused replay.
- `test_run_night`: nine failures and one error involving subprocess deadlines, acknowledgements, and receipt assertions.
- `test_night_agent_install`: one diagnostic assertion encountered unavailable sysmon/process census.

The touched run also passed `tests.test_evidence_night`. [Full touched-suite log](/tmp/evidence-night-r2-touched.log).

## Residual risk

Broader verification remains non-green. Next step: lead diff review and adjudication of those four module failures. Fixture results remain PROVISIONAL; no live hardware validation was performed.