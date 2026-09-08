# G2A-CHAIN-ROUTING-01 — implemented / scoped acceptance ready

Base and final HEAD: `e4ce8b3bece33db40de68b6c407a514fbaed9a26`.
Branch: `feat/2026-09-08-g2a-chain-routing`; no upstream configured.
Intake: no active stop card; explicit 2026-09-08 routing ruling selects this
AGENT task ahead of the ordinary queue. Workspace started clean. No commit,
measurement-checkout creation, protected-clone change, dependency installation, hardware
measurement, or repository-wide test suite was performed.

## Change

The G2-a emitter inventories the new plan-derived source section, retaining
exact fence-range checking, source comments, independent byte reconstruction,
date-only substitution, generated bracket verification, and the GNU sidecar.
The historical fixed block remains byte-identical, marked SUPERSEDED.
`--check` now also validates the executable source-fence inventory.

`preflight.sh` is actually at
`docs/process_traces/2026-08-28-live-smoke/preflight.sh`; there was no
`scripts/preflight.sh` at this head. The existing, explicitly allowed script
now consumes an absolute v2 plan filename. It reads `schema`, `schema_version`,
`measurement_root`, and `measurement_head` with system jq, ignores inherited
coordinate overrides, compares Git HEAD, and derives PY and PYTHONPATH.
This is a routing check; the night driver retains full NightPlan authentication.

The exact v2 key set (`joulewise/night_gate.py:105`) has no interpreter field.
Driver, chain, and preflight derive `$MEASUREMENT_ROOT/.venv/bin/python`; no
schema field was added. In `scripts/run_night.py::_run_chain_once`, :419 exports
`plan.measurement_root`, :420 exports `plan.measurement_head`, and :422 derives
PY from that root. These overwrite inherited child values alongside the existing
`plan_id` handoff at :418. Parent environment stays unchanged. The chain verifies
the coordinates before output creation or interpreter execution. The resumed
production-code delta is limited to this four-line handoff addition.
Preflight's previous checked-out-single-branch gate becomes a detached-head
gate, matching the clone ruling. Locked dependency, import, physical ledger,
process, and privilege gates remain.

### Every removed/rerouted measurement literal

Paths below are repository-relative. Before locations refer to the base above;
after locations refer to the current worktree. R =
`docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`;
P = `docs/process_traces/2026-08-28-live-smoke/preflight.sh`.

| Before | Literal | After |
|---|---|---|
| P:8 | `/Users/edr/JouleWise-measurement-20260813` in usage | P:8 accepts an absolute night-plan filename |
| P:41 | fixed required checkout, same root | P:43 reads `.measurement_root`; P:52 assigns the checkout |
| P:42 | `/Users/edr/code/JouleWise/.venv/bin/python` | P:53 derives the measurement-root venv |
| P:58 | fixed checkout refusal, same root | P:44 validates absolute root; P:55 compares the plan head |
| R:169 | only-accepted historical root | R:167 points to the plan-derived routing contract |
| R:253 | emitted fixed measurement checkout | Preserved as history at R:255; new emitted assignment at R:1530 derives from MEASUREMENT_ROOT |
| R:255 | emitted development interpreter | Preserved as history at R:257; new emitted assignment at R:1532 derives the measurement venv |
| R:728 | literal preflight checkout argument | R:731 passes "$NIGHT_PLAN" |

`scripts/gen_g2_phase_d.py:96` switches the inventory from the historical
section to the new source; :122 re-pins the five fence ranges. Its :130 fixed
block selection and :147 source-block comments still operate over the reviewed
inventory. Unrelated historical struck text at R:63 and the separately generated
G2-b runbook chain at R:934 retain their original literals; neither is emitted by
`--emit-chain`. The retired root/interpreter grep is empty for the G2-a output
and the entire preflight.

Future roots and exact Python 3.13 venv reconstruction are documented at
R:1483, including `git clone --no-hardlinks`, detached reviewed HEAD, constrained
editable mac install, the three otherwise-unrequired locked packages, and the
mandatory empty normalized freeze diff. This follows the existing 2026-08-27
venv-relock record; the recipe was documented, not executed.

### Routing refusal texts

All exit 1 before measurement work:

- Chain: `FAIL measurement_root is required`.
- Chain: `FAIL measurement_root must be an absolute path`.
- Chain: `FAIL measurement_root contains control characters`.
- Preflight: `FAIL night plan path must be absolute`.
- Preflight: `FAIL night plan must use joulewise.night_plan.v2 with schema_version 2`.
- Preflight: `FAIL measurement_root must be a non-empty absolute path`.
- Both: `FAIL measurement_head must be a full 40-character lowercase SHA-1`.
- Both: `FAIL checkout HEAD cannot be read`.
- Chain: `FAIL checkout HEAD does not equal measurement_head`.
- Preflight: `FAIL checkout HEAD does not equal measurement_head (observed <SHA>)`.
- Both: `FAIL measurement venv Python is missing or not executable`.
- Preflight: `FAIL measurement checkout must be detached at measurement_head`.

## Verification notes

Acceptance is limited to `tests/test_gen_g2_phase_d.py` (8),
`tests/test_preflight.py` (8), and `tests/test_run_night.py` (58): 74 tests total. Neither
`scripts/prewindow_check.sh` nor its test module needed changes. The new routing tests
execute prefixes with fake Git/venv fixtures; driver regressions use the real
plan writer/parser and gate with fixture probes and a recorded Popen. They do
not run the measurement chain or preflight hardware legs. Shell-dependent tests skip when
zsh/system jq is unavailable; no skips occurred here.

Before implementation, the existing generator baseline passed four tests and
`--check`. Adding the named literal-survival and missing-root counterfactuals
then failed both on the original implementation; the missing-root shell prefix
returned 0 instead of 1. Adding the initial seven preflight tests failed fifteen
assertions/subtests, including the named mismatched-head and missing-root
counterfactuals. Preflight's old prefix still printed the fixed-source-venv and
fixed-checkout failures rather than consuming the plan. Captured baseline tails:

```text
python3 -B -m unittest discover -s tests -p test_gen_g2_phase_d.py
AssertionError: 0 != 1 :
Ran 6 tests in 0.021s
FAILED (failures=2)

python3 -B -m unittest discover -s tests -p test_preflight.py
Ran 7 tests in 0.076s
FAILED (failures=15)
```

After implementation, the requested check/emission/syntax commands and scoped
acceptance were captured as follows (empty tail means successful silence):

```text
$ python3 -B -m unittest discover -s tests -p test_gen_g2_phase_d.py
exit 0
........
----------------------------------------------------------------------
Ran 8 tests in 0.292s

OK
```

```text
$ python3 -B -m unittest discover -s tests -p test_preflight.py
exit 0
........
----------------------------------------------------------------------
Ran 8 tests in 1.008s

OK
```

```text
$ python3 -B scripts/gen_g2_phase_d.py --check
exit 0
PASS generated Phase D matches pinned runbook bytes
```

```text
$ python3 -B scripts/gen_g2_phase_d.py --emit-chain /private/tmp/g2a-routing-chain.zsh --night-date 20260908
exit 0
emitted /private/tmp/g2a-routing-chain.zsh
```

```text
$ /bin/zsh -n /private/tmp/g2a-routing-chain.zsh
exit 0

```

```text
$ /bin/bash -n docs/process_traces/2026-08-28-live-smoke/preflight.sh
exit 0

```

```text
$ git diff --check
exit 0

```

Additional inspection: the historical fixed fence including its body matches
`git show HEAD:<runsheet>` byte-for-byte; the emitted GNU sidecar is exactly
SHA-256(chain bytes) plus the chain basename. The retired-coordinate grep over
the emitted chain and preflight returned no matches. The chain was never run.

## Approved scope expansion and driver regression evidence

The first return requested `scripts/run_night.py` and `tests/test_run_night.py`.
The lead prospectively approved both on resume, limiting production work to
`_run_chain_once`'s plan-to-child handoff. This was the only outstanding scope
blocker; it is now resolved. No NEEDS_SCOPE or NEEDS_RULING remains, and no
out-of-scope repository write was made. The earlier changes in this same
worktree were this worker's own preserved work; no unowned dirty paths exist.

Two driver regressions were added before changing the handoff:

- `test_counterfactual_inherited_coordinates_override_parsed_night_plan`:
  starts with stale parent root/head/PY and plan ID, a plan root containing
  spaces, and a measurement head distinct from repo_head. It checks the actual
  Popen environment against the parsed plan and verifies the parent is unchanged.
- `test_plan_supplies_coordinates_when_parent_exports_are_absent`:
  removes all three routing exports from the parent and checks that the plan
  supplies them to the child. Before the fix, the observed values were
  `[None, None, None]`.

Exact focused replay command (run before and after the four-line handoff):

```text
python3 -B -m unittest tests.test_run_night.NightDriverTests.test_counterfactual_inherited_coordinates_override_parsed_night_plan tests.test_run_night.NightDriverTests.test_plan_supplies_coordinates_when_parent_exports_are_absent
```

Fail-before tail (exit 1):

```text
Ran 2 tests in 0.035s

FAILED (failures=2)
```

Pass-after tail (exit 0):

```text
Ran 2 tests in 0.031s

OK
```

Full scoped driver-module acceptance (exit 0):

```text
$ python3 -B -m unittest discover -s tests -p test_run_night.py
..........................................................
----------------------------------------------------------------------
Ran 58 tests in 7.593s

OK
```

The resumed verification reran both other touched modules, `--check`, scratch
`--emit-chain`, zsh syntax, preflight Bash syntax, the historical-block byte
comparison, the GNU sidecar comparison, and the retired-coordinate absence
check. All passed. The operator notes now describe the installed handoff.

Next exact step: lead reviews the final scoped diff and owns any subsequent
real-night preparation/arming. Test fixtures establish routing behavior, not
live hardware readiness. No commit or production checkout was created.
