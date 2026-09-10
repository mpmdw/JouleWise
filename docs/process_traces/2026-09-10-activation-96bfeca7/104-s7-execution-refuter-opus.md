# 104 — Seat S7 execution-lens refuter (Opus)

Worktree `/Users/edr/code/JouleWise-wt-s7-night-wrapper`, branch
`feat/2026-09-10-epoch-s7-derivation-night-wrapper`, HEAD `94e4fc89`, base `aea38b1a`.
Read-only except temporary mutation cuts, all restored byte-for-byte (§Cut table).
`git status --porcelain` empty at start and at end. No captures, no `[QUIET-MAC]`
work, no sudo, no git state changes, no touch of canonical / `~/night-custody` /
other worktrees. Every subprocess ran with `PYTHONDONTWRITEBYTECODE=1`.

## VERDICT — MERGEABLE AFTER FIXES

The mechanism works: I launched an emitted wrapper exactly as the driver does and
it reached the reservation with all 24 bindings, and every precondition I broke
refused **before** `exec` with a named reason. The tests are defect-shaped: 8 of 8
independent cuts were killed.

One design claim in the diff is **false as written**, and it is the claim the whole
attestation story rests on: the wrapper does **not** pin the capturing chain's
bytes. It pins a *path to a sidecar file that nothing pins*. `F1` below is the
required fix (≈2 lines, and the generator already contains the exact pattern it
needs, 12 lines above). `F3`/`F4` should ride the same fix round.

---

## Findings

### F1 — BLOCKER (correctness of the attestation claim). The plan-pinned wrapper does not cover the capturing chain's bytes.

`scripts/gen_derivation_night.py:235-240` renders

```
# The plan pins THIS wrapper's digest; the wrapper pins the capturing
# chain's, so the plan-pinned digest transitively covers the bytes that
# actually capture.  The sidecar names the path relative to the clone.
( cd "$REPO" && /usr/bin/shasum -a 256 --status -c '<night_root>/chain.zsh.chain-source.sha256' ) || route_refuse ...
```

The digest itself is **not in the wrapper's bytes**. `WrapperSpec.chain_sha256`
(`:131`, computed `:383`) is used at exactly one place — the region's prose at
`:452` — and never by `render_wrapper`. What the wrapper carries is the *path* of a
third file, `<night_root>/chain.zsh.chain-source.sha256`, written by `emit()` at
`:269-274`. That file is not the plan's `chain_path` nor its `chain_sha256_path`,
so `scripts/run_night.py:1576-1607` never sees it and nothing attests it.

Three consequences, the first executed:

**(a) Swapping the sidecar swaps the pin, with the wrapper byte-identical.**

```
append b"\n# injected\n" to <clone>/scripts/night_chains/calibration_derivation_only.zsh
rewrite <night_root>/chain.zsh.chain-source.sha256 with the new digest
/bin/zsh <night_root>/chain.zsh   (driver env, stdin DEVNULL)
```

Observed: `rc=3` (my fake interpreter's post-reservation stop), 2 calls made —
readiness and the full reservation — i.e. **the night ran a modified capturing
chain**; `wrapper bytes unchanged: True`. Expected: refusal.

**(b) The documented arm-time attestation cannot detect a chain change.** The arm
procedure the region and record 04 `:672-694` prescribe is *re-emit and assert byte
equality of the wrapper*. Editing the tracked chain and re-emitting produces an
**identical wrapper** (only the third file changes), so that assertion passes over
a changed capturing chain. The step that is supposed to be the tripwire is blind to
the thing it is claimed to cover.

**(c) It invites the 03:00 repair that destroys the pin.** An operator who sees
`FAIL tracked derivation chain bytes do not match the arm-time digest` has an
obvious, wrong repair available: regenerate the sidecar. Nothing downstream
notices.

**Fix (~2 lines).** Bake the literal and compare inline, exactly as the wrapper
already does for the frozen plan at `:227-233`:

```
observed_chain_sha256="$(/usr/bin/shasum -a 256 "$REPO/scripts/night_chains/calibration_derivation_only.zsh" | /usr/bin/awk '{print $1}')"
[ "$observed_chain_sha256" = '<spec.chain_sha256>' ] || route_refuse 'tracked derivation chain bytes do not match the arm-time digest'
```

Then `chain_source_sidecar` and the third file disappear, the chain digest enters
the plan-pinned bytes, the comment at `:235-237` becomes true, and F2 is subsumed.
This is verbatim the scout's own recommendation (101 §8 Q1: "have the wrapper
`shasum -c` the tracked chain against an arm-pinned digest **baked into the
wrapper's own bytes** — cheap, and it closes the gap without a schema change. I
would take this; it is four lines"). The seat implemented the sidecar variant
instead and asserted the property the baked variant would have had.

Regression to add with the fix: emit, change the tracked chain, re-emit, assert the
wrapper's bytes changed.

### F2 — SHOULD-FIX. The third file is undocumented, and its absence refuses without a reason.

`render_region` (`:440-449`) documents the emit command and `zsh -n` only. Nothing
tells the arm that `chain.zsh.chain-source.sha256` must exist at the night root and
must survive whatever copies the night root. Executed with the file removed:
`rc=1`, stderr `shasum: …/chain.zsh.chain-source.sha256: No such file or directory`
— no `FAIL` prefix, no statement of what the night needed. Subsumed by F1's fix.

### F3 — SHOULD-FIX. The generator digests the chain from its *own* repo, never from the measurement clone.

`build_spec:355` — `chain_bytes = TRACKED_CHAIN_PATH.read_bytes()` where
`TRACKED_CHAIN_PATH = REPO_ROOT / TRACKED_CHAIN_RELPATH` (`:32,:45`), i.e. the
checkout the generator is *executed from*. The wrapper verifies the chain under
`$REPO = $MEASUREMENT_ROOT` (`:210,:238`). At arm time those are different
checkouts (the magistrate's worktree vs the measurement clone). My fixture happened
to make them identical, which is exactly how this hides.

Failure mode: the magistrate's worktree is dirty or at another HEAD → the emitted
digest is of bytes the night will never run → the night refuses at launch and is
burned, with the mismatch discoverable only after t0. It fails *safe*, not silent,
which is why this is should-fix and not blocker. The wrapper's HEAD equality check
(`:205-208`) does not close it: it binds the clone to `measurement_head` but not
against uncommitted edits (scout 101 §6, "Clean-checkout: Open").

Fix: read the chain from `Path(plan.measurement_root) / TRACKED_CHAIN_RELPATH`,
or refuse at emit time when the two differ.

### F4 — SHOULD-FIX (diagnosability). Three refusals are silent.

`:222-224` — `test -f "$PLAN"`, `test -f "$IDENTITY_EPOCH_JSON"`,
`test -f "$T1_BINDINGS_JSON"` exit 1 under `set -e` with **empty stderr**
(executed, all three: `rc=1 err=''`). Every other refusal in the wrapper prints
`FAIL <reason>` through `route_refuse` (`:184`). The driver redirects the chain's
stderr to a file; an unattended night's only forensic record of why it refused
would be an empty stream. Fix: `|| route_refuse '…is missing'` on each.

### F5 — NIT. The `TRANSACTION_PACK` guard is effectively unreachable and untested.

`:296-299`. Executed: a plan with `receipt_class: "TRANSACTION_PACK"` and no
`pack_night` key is refused *earlier*, by `NightPlan.from_mapping` — observed
`FAIL night plan is not an exact v2 plan: plan keys are not exact
(missing=["'pack_night'"], extra=[])` (`joulewise/night_gate.py:215-216`). The
guard fires only for a **well-formed** pack plan; no test in
`tests/test_gen_derivation_night.py` constructs one (test list has no pack test). I
confirmed the guard does fire by stubbing `from_mapping` in-process: `refused: a
derivation night is DIAGNOSTIC_NO_PACK; this plan is a pack night`. Either build a
valid `pack_night` fixture or stop counting it as covered.

### F6 — NIT. `--allow-slot-count` moves off the pre-registration with no louder record.

Executed: `--slot-count 6 --allow-slot-count` → `rc=0`, wrapper carries
`SLOT_COUNT='6'` and 6/6 binding flags. Cold-gate ruling 46 §R-c pre-registers 12.
The escape hatch is fine; consider requiring a reason string echoed into the
wrapper's header comment so the emitted bytes state that the night departs from the
pre-registration.

### Non-finding, recorded because it cost me two runs

I twice observed a reservation argv with **zero** bindings before tracing it to my
own concurrency: my cut-table job was mutating the worktree's tracked chain at the
time, and cut C2 deletes the `"$@"` line the fixture then copied. 31 subsequent
launches (25 alternating plain/spaces + 6 spaces) were `(rc 3, 76 argv elements, 12
attempt-id flags)` — 31/31. As a side effect this is an independent *live* proof of
what C2 costs: with `"$@"` gone, the real reservation receives no bindings at all
and would refuse `declared_slot_flag_count_mismatch`
(`scripts/reserve_calibration_window_bracket.py:172-186`) mid-night, after the
settle, having already opened nothing.

---

## What I verified (executed, brief items 1–8)

**1. THE LAUNCH.** Emitted from a synthetic v2 plan via the seat's `WrapperFixture`
(a real one-commit git clone with a fake `.venv/bin/python`), then launched exactly
as `scripts/run_night.py:430-444` does: `["/bin/zsh", wrapper]`, `stdin=DEVNULL`,
`cwd=/`, env = `PATH=/usr/bin:/bin` plus only `NIGHT_PLAN_ID`, `MEASUREMENT_ROOT`,
`MEASUREMENT_HEAD`, `PY`. Observed, in order:

1. `recover_calibration_ledger.py --ledger … --head-pin … readiness --phase
   pre-reserve --session-id derivation-20260912-epoch --plan …` (12 argv elements);
2. `reserve_calibration_window_bracket.py … --session-kind derivation
   --slot-count 12 … --slot-attempt-id derivation-20260912-epoch-d01
   --slot-custody-locator <runs_root>/instrument_validation/…-d01 … (×12) …
   --execute` — 76 argv elements, 12 `--slot-attempt-id`, 12
   `--slot-custody-locator`, `--execute` last, nothing after it.

Precondition breaks, each launched the same way (`calls=0` means nothing ran, i.e.
refusal was before `exec`):

| Break | rc | stderr | calls |
|---|---|---|---|
| `MEASUREMENT_HEAD` = `b`×40 | 1 | `FAIL measurement_head does not match the wrapper` | 0 |
| `NIGHT_PLAN_ID` = `other-night` | 1 | `FAIL night plan id does not match the wrapper` | 0 |
| `MEASUREMENT_ROOT` = `/tmp` | 1 | `FAIL measurement_root does not match the wrapper` | 0 |
| tracked chain, last byte changed | 1 | `FAIL tracked derivation chain bytes do not match the arm-time digest` | 0 |
| frozen plan bytes changed (extra `\n`) | 1 | `FAIL frozen plan bytes do not equal the arm-time digest` | 0 |
| frozen plan `plan_id` changed | 1 | `FAIL frozen plan id does not equal the arm-time literal` | 0 |
| `identity_epoch.json` deleted | 1 | *(empty — F4)* | 0 |
| `t1_bindings.json` deleted | 1 | *(empty — F4)* | 0 |
| `calibration_plan.json` deleted | 1 | *(empty — F4)* | 0 |
| `chain.zsh.chain-source.sha256` deleted | 1 | `shasum: …: No such file or directory` (F2) | 0 |
| no driver vars at all (`PATH` only) | 1 | `FAIL measurement_root is required` | 0 |
| driver env without `PY` | 3 | — (wrapper sets `PY` itself, `:211`) | 2 |

**2. DETERMINISM AND DIGESTS.** Two emissions of one plan: wrapper bytes identical,
`chain.zsh.sha256` identical. Sidecar form
`68dcd149…651a  chain.zsh` — `shasum -a 256 -c` from the night root → `chain.zsh:
OK`; `run_night._sidecar_digest(text, "chain.zsh")` accepts and equals the wrapper's
digest. The chain-source sidecar
`d6d23bff…0a65  scripts/night_chains/calibration_derivation_only.zsh` verifies with
`shasum -a 256 -c` run from the clone root. Changing `t0_epoch_s`, `window_max_s`
or `plan_id` each changes the wrapper's digest. (Changing the *tracked chain* does
not — F1(b).)

**3. THE ENV LEAK.** Launched with the driver's four vars plus a hostile
pre-set environment: `SLOT_COUNT=3 SETTLE_S=0 SLOT_CADENCE_S=1
SLOT_CAPTURE_BUDGET_S=1 WINDOW_END_EPOCH_S=1 SESSION_ID=evil-session
RUNS_ROOT=/tmp/evil PLAN_ID=evil EVIDENCE_ROOT_ID=evil SLEEP=/bin/false
DATE=/bin/false PY=/bin/false`. Observed reservation: `--slot-count 12`,
`--session-id derivation-20260912-epoch`, `--evidence-root-id
EVR-derivation-20260912`, 12 attempt-id flags — **every leak defeated**. The
wrapper exports unconditionally (`:217`), never `${VAR:-…}`; the tracked chain's
own `${VAR:-default}` forms (`:63-71`) are therefore unreachable. Cut C1 confirms
a test guards this.

**4. REFUSALS** (generation time, `rc=2` each):

| Attack | Observed |
|---|---|
| dead-man, `completion == deadman` exactly | `FAIL plan overruns the dead-man: … = 1789221600 is not before the next local 07:00 = 1789221600` |
| dead-man, one second inside | `rc=0`, emitted (boundary is strict `<`, `:313`) |
| dead-man, +60 s over | `FAIL plan overruns the dead-man: … 1789221660 … 1789221600` |
| census `t3` in session id | `FAIL session id contains the census substring 't3'` |
| census `t3` in an emitted literal (plan id) | `FAIL night plan id contains the census substring 't3'` |
| census `claude` in custody root | `FAIL night custody root contains the census substring 'claude'` |
| census `codex` in `--runs-root` | `FAIL runs root contains the census substring 'codex'` |
| census `claude` in window id | `FAIL window id contains the census substring 'claude'` |
| `--slot-count 6` | `FAIL slot count 6 is not the pre-registered 12; pass --allow-slot-count` |
| `--slot-count 0 --allow-slot-count` | `FAIL slot count must be positive` |
| `--out` ≠ `chain_path` | `FAIL --out /tmp/elsewhere/chain.zsh is not the plan's chain_path '…'` |
| `TRANSACTION_PACK` | refused, but by the schema, not the guard — see F5 |

Census coverage is genuinely broad (session id, plan id, window id, custody root,
runs root, evidence root id, every path literal via `_require_absolute` →
`_census_clean`), and `_census_clean` lowercases before matching, which is stricter
than the case-sensitive `pgrep -lf "codex|claude|t3"` at `joulewise/night_gate.py:42`.

**5. `"$@"` FORWARDING PIN.** Cut C2 (delete `    "$@" \` from
`scripts/night_chains/calibration_derivation_only.zsh:155`) →
`ERROR: test_chain_forwards_its_argv_verbatim_into_the_reservation` (the new test at
`tests/test_issue_calibration_acceptance_generation.py:606`), `FAILED (errors=1)`
over 91 tests. The two renamed source-shape tests now assert the **landed** surface:
`:556-576` asserts `# SKELETON:` is *absent* and the "does not pin this file in its
plan: it pins the wrapper emitted by scripts/gen_derivation_night.py" statement is
present; `:578-604` asserts the `--derivation-only (:1771) / requires --session-id,
--slot and --attempt-id … (:1946)` header block **and cross-checks it against
`scripts/validate_powermetrics_fiducial.py`'s actual CLI text** — the header cannot
go stale without the test failing. That cross-check is the strongest thing in the
test diff.

**6. GENERATED REGION.** `python3 scripts/gen_g2_phase_d.py --check` → `PASS
generated Phase D matches pinned runbook bytes` (rc 0);
`python3 scripts/gen_derivation_night.py --check` → `PASS generated derivation-night
wrapper region matches` (rc 0). The runsheet grew 1611 → 1740 lines and the diff is
`@@ -1609,3 +1609,132 @@` — a pure append. Every `gen_g2_phase_d.PINNED_ANCHORS`
line (1407, 1412, 1428, 1516, 1541, 1556, 1636, 1653, 1663, 1693, 1727) is in
`docs/phase_2/window_runbook.md`, untouched by this diff; the runsheet's own pinned
fence inventory `[(1534,1598),(328,351),(374,385),(389,564),(575,587)]` all sits
below 1609. **No anchor moved.**

**7. OTHER.**
- `set -euo pipefail` with an unset optional var: launched with `PY` absent from the
  driver env → `rc=3`, both calls made; the wrapper sets `PY` itself (`:211`) and
  every reference is `${VAR:-}`-guarded or exported first. No unbound-variable exit.
- `custody_root` containing spaces (`…/night root with spaces/…`): emit `rc=0`,
  `/bin/zsh -n` rc 0, launch reached the reservation with all 12 locators intact,
  e.g. `--slot-custody-locator '…/night root with spaces/…/instrument_validation/derivation-20260912-epoch-d01'`.
  `_quote` (`:72-79`) single-quotes and refuses embedded `'` and control characters.
- **`WINDOW_END_EPOCH_S` vs the chain's own abort arithmetic.** The chain
  (`:170-198`) sets `next_start` after the single settle, so with the wrapper's
  pinned `SETTLE_S=600`, `SLOT_CADENCE_S=600`, `SLOT_CAPTURE_BUDGET_S=480`,
  `SLOT_COUNT=12`: d01 starts at chain_start+600; d12 starts at
  600 + 11×600 = **chain_start+7200**; d12's admission test is
  `slot_start + 480 > WINDOW_END_EPOCH_S` → refuse, so d12 needs
  chain_start+7680 ≤ t0+9000. With `window_max_s = 9000` and chain_start ≈ t0 the
  margin is **1320 s**, matching runbook 99's programmed span of 7680 s. The night
  tolerates up to 1320 s of launch delay between the plan's t0 and the chain's
  actual start before d12 is dropped as `window_exhausted`; the wrapper's own
  preflight (git rev-parse, one 6 KB shasum, one jq) is sub-second, so the real
  consumer of that margin is the gate/driver interval, not this diff.

**8. TESTS.** `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
tests.test_gen_derivation_night tests.test_issue_calibration_acceptance_generation
tests.test_run_night` → **`Ran 191 tests in 81.034s` / `OK`** (rc 0).

---

## Cut table

Each cut was applied to the worktree file, the named module was run, and the file
was restored and re-hashed. `scripts/gen_derivation_night.py`
`ca9be928…a832` before **and** after; `scripts/night_chains/calibration_derivation_only.zsh`
`d6d23bff…0a65` before **and** after.

| # | Cut | Killed by | Result |
|---|---|---|---|
| C1 | `export NAME='lit'` → `export NAME=${NAME:-'lit'}` (`:217`) | `test_every_required_chain_variable_is_exported_with_its_plan_value`, `test_window_end_is_the_integer_sum_of_t0_and_window_max`, both region tests | rc 1 |
| C2 | delete `"$@" \` from the chain (`:155`) | `test_chain_forwards_its_argv_verbatim_into_the_reservation` | rc 1 |
| C3 | neuter the tracked-chain `shasum -c` (`:238-240`) | `test_the_wrapper_refuses_when_the_tracked_chain_bytes_change` + region tests | rc 1 |
| C4 | dead-man `not completion < deadman` → `<=` (`:313`) | `test_a_plan_that_overruns_the_dead_man_refuses` | rc 1 |
| C5 | drop the `NIGHT_PLAN_ID` equality guard (`:198-199`) | `test_the_wrapper_refuses_a_different_plans_coordinates` | rc 1 |
| C6 | drop `_census_clean("session id", …)` (`:334`) | `test_a_census_substring_anywhere_in_the_night_refuses` (subtests `session id` **and** `night custody root`) | rc 1 |
| C7 | `exec /bin/zsh` → `source` (`:245`) | `test_twenty_four_binding_flags_satisfy_the_real_reservation_parser`, `test_a_slot_count_other_than_the_pre_registered_twelve_refuses` | rc 1 |
| C8 | emit attempt ids without locators (`:169`) | `test_the_wrapper_reaches_the_reservation_with_all_bindings`, `test_twenty_four_binding_flags_satisfy_the_real_reservation_parser` | rc 1 |

8/8 killed. Note the region tests (`test_the_runsheet_region_matches_the_generator`,
`test_the_region_carries_the_live_chain_digest`) fire on any change to rendered
bytes, so C1/C3/C5/C7 are each *also* killed by a specific behavioural test, which
is what matters; I checked the specific killer in each row above.

## Hashes

```
HEAD                                              94e4fc89e1bffc390162bc699eef6676b88eb813
scripts/gen_derivation_night.py                   ca9be9288f05e1908b8685a492af9a427d4c44db59e5e982190642b369a5a832
scripts/night_chains/calibration_derivation_only.zsh
                                                  d6d23bff48d410144e74c19307dde79aebdd3a4fbf6e8eea97f34217ef470a65
tests/test_gen_derivation_night.py                544bdf0be71545aea0356e3f3e2caee30d7b317bbe24e57507114483ebd2602d
tests/test_issue_calibration_acceptance_generation.py
                                                  764215058cd7a19c1d98ce236aac7177e96d48e82e9a69e67dd249faec6f1154
docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md
                                                  19e3d32f3d4ba3f0b34ba46221746607fe1e3935794ba3406a37cdc834b15c96
```

Harness used for the launch attacks (my own, outside the repo):
`/tmp/s7refute/h.py`, `/tmp/s7refute/cut.py`.

## On the seat's UNVERIFIED report

Corroborated by execution: the 13 literal exports via `NightPlan.from_mapping`, the
plan equality checks, the `exec` with 24 binding flags, and the refusals for pack
plan / dead-man overrun / census substrings / slot count / `--out` ≠ `chain_path`.
Its "12 cuts killed" I did not attempt to reproduce cut-for-cut; my 8 independent
cuts were all killed, which is the same signal. Its claim of a `shasum -c` "of the
tracked chain" is literally true but does **not** deliver the property the code
comment claims for it — F1.
