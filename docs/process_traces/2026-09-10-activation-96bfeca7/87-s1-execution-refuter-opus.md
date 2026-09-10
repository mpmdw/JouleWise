# 87 — Seat S1 EXECUTION-LENS refuter (Opus)

Worktree `/Users/edr/code/JouleWise-wt-s1-writer-derivation`, branch
`feat/2026-09-10-epoch-s1-writer-derivation-only`, HEAD `12f1d1cf`, base
`1e43d1cc`. Read-only: no git state changed, no commit, no branch, no other
worktree touched. Two temporary mutation cuts, both restored byte-for-byte and
sha256-reverified; `PYTHONDONTWRITEBYTECODE=1` on every subprocess. No live
`powermetrics`, no `[QUIET-MAC]` work — fixture sampler only. Full
`tests.test_calibration_exits` was NOT run (per brief); single tests only.

## VERDICT: **MERGEABLE** (three nits, no blockers, no should-fix)

Every clause the brief asked me to attack held under execution. The seat's
report is now **corroborated, not assumed**: I reproduced all six refusal gates
through the real CLI on my own fixtures, produced a real derivation capture and
inspected its sealed bytes, and independently killed the V2 disposition clause.
The two exceptions the seat self-declared (§F3 refusal class, the
`@unittest.skip`) are both **correct on the evidence** — I tried to break each
and could not.

## Baseline hashes (start of session, `/tmp/ref87-baseline-sha.txt`)

```
9affd15e6b23d24de2ec895e4fa651998d40391d1a14690b597aac392b5592d4  scripts/validate_powermetrics_fiducial.py
212a1ffa2f4b1e19cf972907f6ec3f8fd82c645b1532e6932d89e05f3cfaa87f  tests/test_validate_powermetrics_fiducial_derivation_only.py
0ead3dbf141e893181f9bbb47e556e51d987058df70d7e2d715a60daa9cc81dd  tests/test_calibration_exits.py
c66ffbfcc483f71df4f9c617e450044644dc3ed5de89fa015183e8b8c086d944  joulewise/calibration_exits.py
```

All four re-verified identical at end of session; `git status --short` empty.

---

## 1. The refusal gates, through the real CLI (independent invocations, not the seat's tests)

All run from the worktree root against the **live repo acceptance**
`configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`
(`acceptance_id d079_calibration_acceptance_v2_n17_r6`, epoch `os_build 25F84 /
Mac15,9 / ac_high_power / 100 / joint_loss_sublevel_interval_branch_v2 /
powermetrics_pulse_fiducial_v3`, `preflight_level_screen_s 0.032898493715362`).
Identity fixtures: `/tmp/ref87-match.json` (the artifact's own epoch) and
`/tmp/ref87-diff.json` (same, `os_build=25G83`).

| # | Invocation (all `python3 scripts/validate_powermetrics_fiducial.py …`) | rc | printed `code` | expected |
|---|---|---|---|---|
| P1 | `--power-policy ac_high_power --derivation-only --output-root … --identity-epoch-json-for-test /tmp/ref87-diff.json` (no `--allow-live`) | 2 | `calibration_quiet_mac_auth_required` | ✔ clause (a) by ordering |
| P2 | `--allow-live --power-policy ac_high_power --derivation-only … --identity-epoch-json-for-test /tmp/ref87-match.json` | 2 | `calibration_derivation_only_epoch_unchanged`, `context.acceptance_id = d079_calibration_acceptance_v2_n17_r6` | ✔ clause (c) |
| P3 | same as P2 but `…-diff.json`, no session | 2 | `calibration_derivation_only_session_kind_required`, `context.detail` names `--session-id/--slot/--attempt-id` | ✔ clause (b) standalone |
| P4 | `--allow-live --power-policy … --derivation-only --rederive-from /tmp/ref87-src.json --output …` | 2 | `calibration_writer_bracket_rederive_conflict`, `context.detail = "--derivation-only applies only to live capture"` | ✔ clause (e), fires **before** the `--rederive-from` branch that returns 0 |
| P5 | `--allow-live --power-policy … --derivation-only --output …` (no `--rederive-from`) | 2 | `calibration_writer_bracket_rederive_conflict` (same detail) | ✔ (see NIT-1) |
| P6 | ORDINARY standalone, matching epoch, no `--allow-live` (control) | 2 | `calibration_quiet_mac_auth_required` | ✔ ordinary path untouched |
| P7 | ORDINARY `--allow-live`, **differing** epoch | 2 | `calibration_frozen_protocol_invalid`, `context = {reason: acceptance_artifact_epoch_mismatch, stale_fields: ["os_build"]}` | ✔ — load-bearing for §4 |

**Bracket-kind session refusal and the fix-round ordinary-mode guard** were
exercised through the seat's ledger harness (real `append_bracket_session_receipt`
reservation API, derivation-kind 12-slot-shape session via
`derivation_session_slots`, and a kindless bracket-kind session):
`tests.test_validate_powermetrics_fiducial_derivation_only`, **`Ran 9 tests in
44.376s / OK (skipped=1)` rc 0** (`/tmp/ref87-A-newmod.log`, verbose). The two
that matter:

- `test_bracket_kind_session_refuses_a_derivation_only_capture` — ok; asserts
  `calibration_derivation_only_session_kind_required`, `context.session_kind ==
  "bracket"`, and `custody["pre"]` never created.
- `test_ordinary_mode_refuses_a_derivation_kind_slot_and_appends_nothing` — ok;
  asserts `calibration_derivation_session_requires_derivation_only`,
  `context.session_kind == "derivation"`, `context.slot == "d01"`,
  **`ledger.read_bytes() == before`** and `custody.exists() is False`. That is
  exactly the brief's "appending nothing, no custody dir" requirement, and it
  is asserted on bytes, not on a count.

### Independent cut (mine, not the seat's)

| Clause | Cut | Test | Result |
|---|---|---|---|
| V2 — a `None` screen must never reach the systematic comparison (`scripts/validate_powermetrics_fiducial.py:2412-2413`) | deleted the `preflight_systematic_screen_s is not None and` conjunct | `…DerivationOnlyLiveCaptureTests::test_derivation_slot_of_a_differing_epoch_appends_valid_with_provenance` | **`Ran 1 test in 21.635s / FAILED (failures=1)` rc 1** — `TypeError: '>' not supported between instances of 'decimal.Decimal' and 'NoneType'` at `main` `:2414`. Bytes restored, sha256 `9affd15e…` re-verified, `git status` clean. |

I did not re-run the seat's other six cuts; my CLI reproduction of every gate on
fixtures I built myself is the independent evidence, and the one clause where a
silent wrong answer (rather than a refusal) was possible is the one I cut.

---

## 2. The admit path and the seal — EXECUTED, and this is the seat's own §2(iv) gap partly closed

Driver `/tmp/ref87_item2.py` (mine): re-key the acceptance into a synthetic
repo, open a **derivation-kind** session via `append_bracket_session_receipt`,
capture slot `d01` at epoch `25G83` with the fixture sampler.

```
WRITER rc = 0
EV derivation_only= True  screen_basis keys= ['acceptance_id','artifact_sha256','epoch','preflight_level_screen_s']  exceeds= False  status= valid
MF derivation_only= True  screen_basis keys= ['acceptance_id','artifact_sha256','epoch','preflight_level_screen_s']  exceeds= False
LEDGER disposition= valid  slot= d01
receipt artifact_sha256 keys= ['events.jsonl','instrument_evidence.json','manifest.json','power_trace.csv','raw/powermetrics.plist']
receipt content_id present= True
STALE FIELDS vs r6 = ['os_build']
```

- Disposition is **`valid`** — never `systematic-invalid`, never
  `systematic-valid`. ✔ (ruling 46 V2.)
- Exactly the four `screen_basis` keys A1 names, in both files. ✔
- `exceeds_prior_level_screen` present as a real `bool`. ✔

**Seal (tamper probe).** Both `screen_basis` blocks are inside sealed content —
the finalization receipt's `artifact_sha256` covers **both**
`instrument_evidence.json` and `manifest.json`, and `content_id`
(`CONTENT_ID_ARTIFACTS = (instrument_evidence.json, manifest.json)`,
`joulewise/calibration_ledger.py:126-129`) is derived from those two:

```
TAMPER1 (evidence screen_basis.acceptance_id -> "TAMPERED")
  manifest-hash-match: False   receipt-hash-match: False
TAMPER2 (manifest screen_basis.acceptance_id -> "TAMPERED")
  receipt-manifest-hash-match: False  (920b0820… vs c230a512…)
```

Both files restored byte-for-byte in the temp repo before teardown. The
read-back path that consumes those hashes is
`joulewise/calibration_ledger.py:5514-5528`, which raises
`RefusalCode.CUSTODY_UNREADABLE` on exactly this mismatch. **The manifest side
matters and I checked it specifically**: `manifest.json` is excluded from
`MANIFEST_BOUND_ARTIFACTS` (it cannot hash itself) and is written *after* the
evidence, so the only thing binding a tampered `manifest["screen_basis"]` is
the ledger receipt — and it does. No hole.

**D-102 cl.2 the other way.** I did not call `evaluate_calibration_bracket`
end-to-end (it needs S3's candidate-sequence + policy + snapshot fixture; same
reason the seat gave, and I agree it is S3's gate). What I DID execute is the
production staleness computation on the real finalized row using the production
constant: `ACCEPTANCE_IDENTITY_FIELDS` filtered against the row's
`identity_epoch` yields **`['os_build']`**, and
`joulewise/calibration_bracketing.py:1534-1539` is literally
`freshness_status = "stale" if stale_fields else "fresh"`. So the row reads
`stale` against r6 and cannot be consumed for measurement. I additionally
checked the **field-set symmetry** that would have been a blocker if it were
broken: the writer's `stale_fields` at `:1840-1844` iterates the artifact's
`identity_epoch` keys, while `calibration_bracketing` iterates
`ACCEPTANCE_IDENTITY_FIELDS`; executed, the two sets are **identical**
(`diff = []`). An asymmetry there would have let a capture unlock
derivation-only on a field r6 still calls fresh — i.e. a screen bypass. It does
not exist. Recommend the S3 gate still require the end-to-end assertion.

---

## 3. Ordinary path unchanged

`tests.test_powermetrics_fiducial.WriterLedgerIntegrationTests` +
`tests.test_calibration_ledger.CalibrationLedgerTests` at HEAD:
**`Ran 77 tests in 2.854s / OK (skipped=1)` rc 0** (`/tmp/ref87-C-ordinary.log`).
That set includes the ordinary bracket-slot writer integration tests and the
`systematic-invalid` disposition cases at
`tests/test_calibration_ledger.py:330, 412, 447, 738-758`. Plus P6/P7 above are
direct ordinary-path CLI controls, and the seat's own
`test_ordinary_mode_still_fills_a_bracket_kind_slot_unchanged` (ok, `valid`,
and asserts `derivation_only`/`screen_basis` are **absent** from ordinary
evidence) is the kind-scoping regression.

**Not executed, out of time:** the base-vs-HEAD byte diff of one bracket
capture's writer output at the same absolute temp path. Given the disposition
expression is the only ordinary-path edit and its added conjunct is vacuously
true when `preflight_systematic_screen_s` is a Decimal, plus the 77 green tests
and the absent-keys assertion, I judge the residual risk low — but the gate
should treat that specific check as **unperformed by me**.

---

## 4. The refusal class (`abort-session`) — the seat's F3 argument VERIFIED by execution

The seat's claim was that `correct-preflight`/`ready_to_arm` is structurally
unreachable for `DERIVATION_SESSION_REQUIRES_DERIVATION_ONLY`. Both legs check
out:

1. **Is the guard even reachable on a mismatched epoch? No.** P7: the ordinary
   writer at a differing epoch refuses `calibration_frozen_protocol_invalid`
   (`reason acceptance_artifact_epoch_mismatch`, `stale_fields ["os_build"]`)
   at `main:1863-1871`, which runs *before* `_CaptureLedgerLifecycle` is
   constructed at `:1927`. So the guard at
   `scripts/validate_powermetrics_fiducial.py:1378` fires **only** when the
   machine epoch MATCHES the active acceptance. That is exactly the state the
   seat's witness `_state_derivation_kind_writer` builds, and its docstring
   says so.
2. **Is there a same-state argument correction? No.** P2 proves the obvious
   candidate is not one: on a matching epoch, adding `--derivation-only`
   refuses `calibration_derivation_only_epoch_unchanged`. The only other
   correction is an ordinary bracket slot, which needs a second open session —
   and `is_governed_open_bracket_extension` tolerates one.

**The class is right.** `abort-session` / `session_aborted` / `night_loss=true`
mirrors the three sibling capture-time writer refusals (`display_arm_failed`,
`sampler_never_ready`, `rollover_gate_timeout`) exactly, and the registry row
carries empty correction-surface/corrected-success like they do. The registry
projection test passes (the seat's `Ran 1 / OK`; the row is in the diff at
`docs/contracts/calibration_ledger_append.md:341`).

**NIT-2 (below) is the one thing I would put in the record about it:** the
guard does not fire in the *real* 25G83 scenario — there the ordinary writer at
a derivation slot is stopped by `FROZEN_PROTOCOL_INVALID` instead. Fail-closed
either way, so D-161 is satisfied and this is not a defect; it is a
diagnosability nit.

---

## 5. The `@unittest.skip` — I tried the fixture route and it FAILS; the skip is honest

The harness already carries the exact candidate cure — `_rekey_acceptance(maximum_s=…)`
at `tests/test_validate_powermetrics_fiducial_derivation_only.py:289-300`,
which rewrites `source_statistics.maximum_s`,
`rounding.preflight_level_screen.value_s` and
`ratified_operatives.preflight_level_screen_s` together and re-keys the
`derivation_sha256` and the bracketing pin. I removed the skip decorator
(1287 bytes) and ran the test alone:

```
FAIL: test_a_bound_above_the_prior_level_screen_is_recorded_but_still_valid
AssertionError: 2 != 0 : {"arm_blocked": true,
  "code": "calibration_frozen_protocol_invalid",
  "context": {"reason": "acceptance_artifact_unauthenticated"}, …}
Ran 1 test in 0.531s / FAILED (failures=1)
```

Restored: sha256 `212a1ffa2f4b1e19cf972907f6ec3f8fd82c645b1532e6932d89e05f3cfaa87f`
matches baseline; `git status --short` empty.

So `_valid_acceptance_bound`'s self-consistency fence (max of the 17 member
values must quantize to `preflight_level_screen_s`, range to `bracket_screen_s`)
rejects the rewritten artifact exactly as the skip reason predicts. **Within the
10-minute budget I found no fixture-level route to the TRUE branch** that does
not either (a) rewrite the whole 17-member corpus + both t-quantile predictions
(that is S4's issuer), or (b) run a ~17-minute capture (time scale ~0.35 against
a bound of `9.298…e-05` vs a screen of `0.032898493715362`, a factor of ~354).
I also endorse the seat's rejection of a test-only `--acceptance-path` seam: it
would let a caller aim the mode at a different-epoch artifact and walk straight
through `DERIVATION_ONLY_EPOCH_UNCHANGED`. The clause is diagnostic-only and
cannot change a disposition (the cut in §1 proves the disposition ignores it),
so the residual risk of the gap is a wrong `bool` in a recorded diagnostic, not
a wrong verdict.

---

## 6. Observer dispatch — the narrowing is correct and the rest of the table is clean

Parsed all 40 `WitnessCase` observer literals from
`tests/test_calibration_exits.py` (AST, not grep) and cross-checked every
prefix relation against the dispatch at `:5125-5423`.

Strict-prefix pairs that exist in the table:

| prefix | shadowed sibling | matched at | exact? |
|---|---|---|---|
| `audit` | `audit-baseline`, `audit-observations` | `:5125` `in {"audit","inspect","repair"}` | ✔ exact set |
| `abandon` | `abandon-credentials` | `:5145` `== "abandon"` | ✔ |
| `repair` | `repair-credentials` | `:5125` exact set / `:5143` `==` | ✔ |
| `reserve-execute` | `reserve-execute-new` | `:5190` `==`, `:5194` `in {…,…}` | ✔ exact |

The only remaining `startswith` matches are the three **namespace** dispatchers
(`reserve-`, `advance-`, `writer-` at `:5185/:5299/:5330`); no observer outside
each namespace begins with its prefix, and every branch *inside* the three
namespaces is an exact `==` or an exact set — including the new
`{"writer-derivation-epoch","writer-derivation-standalone"}` at `:5358` and the
`_writer_env` dispatch at `:5415`
(`{"writer-display-failure","writer-derivation-session"}`). Note `:5320`
`writer-binding-conflict` is correctly ordered *before* the `writer-` namespace
`startswith`. **No further shadowing risk found.** The seat's narrowing was the
right call and it caught a real self-inflicted defect (its own F4 §"second
defect caught").

---

## Findings

**BLOCKERS: none. SHOULD-FIX: none.**

**NIT-1 — `--derivation-only --output` (no `--rederive-from`) reports a
"rederive conflict".** `scripts/validate_powermetrics_fiducial.py:1721-1733`
routes both `--rederive-from` and bare `--output` to
`WRITER_BRACKET_REDERIVE_CONFLICT`. Reproduce: P5 above. Observed
`calibration_writer_bracket_rederive_conflict`; the sibling ordinary path for
bare `--output` is `OUTPUT_REQUIRES_REDERIVE` (`:1754`). Same registry class,
same fail-closed outcome, and `context.detail` disambiguates — but a reader of
the refusal alone will look for a `--rederive-from` that was never passed.
Cosmetic; no gate depends on it.

**NIT-2 — the fix-round guard is unreachable in the scenario that motivates
it.** `scripts/validate_powermetrics_fiducial.py:1378`. On the real 25G83
epoch, an operator running the ordinary writer at a derivation slot gets
`FROZEN_PROTOCOL_INVALID / acceptance_artifact_epoch_mismatch` (P7), not
`calibration_derivation_session_requires_derivation_only`. The guard only fires
in the narrower matching-epoch case. Fail-closed both ways (D-161 satisfied), so
this is a diagnosability note, not a defect — but the report and the guard's
comment read as though the guard is what protects the 25G83 case, and it is
not. One sentence in the comment would fix the impression.

**NIT-3 — `_rekey_acceptance(maximum_s=…)` is a non-functional parameter.**
`tests/test_validate_powermetrics_fiducial_derivation_only.py:289-300`. Its
only caller is the skipped test, and executed (§5) it yields
`acceptance_artifact_unauthenticated`. Keeping a parameter whose documented
purpose ("how a test drives a real capture ABOVE the prior epoch's screen")
demonstrably does not work invites the next reader to build on it. Either delete
it or add the executed refusal to the skip reason, which currently reasons about
`_valid_acceptance_bound` analytically rather than reporting the observed code.

## Coverage I did not reach (35-minute budget)

- Base-vs-HEAD byte diff of the ordinary bracket capture output (§3).
- `evaluate_calibration_bracket` end-to-end on r6 (§2) — substituted the
  production `stale_fields` computation on the real row plus the field-set
  symmetry check; recommend S3 still owns the end-to-end assertion.
- Re-execution of the seat's six other mutation cuts (substituted independent
  CLI reproduction of every gate + one own cut on the clause where a silent
  wrong answer was possible).
