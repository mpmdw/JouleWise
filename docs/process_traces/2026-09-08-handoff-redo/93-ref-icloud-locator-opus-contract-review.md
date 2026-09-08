# ICLOUD-CUSTODY-LOCATOR-01 part 3 — Opus contract-lens refuter

Worktree `/Users/edr/code/JouleWise-wt-ref-icloud-locator-opus`, HEAD `42b0d235`.
Packet `git diff HEAD~3 HEAD` is **five** files, not four: the merge `1c83f2af`
carries `docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md`
(+2 lines, the magistrate's own stand-down note — not seat scope, benign).

Permitted suite: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
tests.test_calibration_ledger_custody tests.test_calibration_bracketing
tests.test_calibration_ledger tests.test_authentication_io` →
**Ran 155 tests, OK (skipped=2)**, plus the ledger mutation probe reporting
`KILLED 3 renderer AST mutations`.

## Findings

| id | sev | file:line | defect | demonstrating command |
|---|---|---|---|---|
| SF-1 | should-fix | `joulewise/calibration_ledger.py:4766`, `:5218`, `:1781` | Timeout is indistinguishable from genuine absence in every receipt and log. The sibling, already-landed `ICLOUD-BACKUP-PROBE-01` — same env var, same 2 s budget — emits a `backup_root_unavailable` stderr line for exactly this case. This diff emits nothing; the outcome silently becomes `RefusalCode.CUSTODY_PARTIAL` or `calibration_ledger_custody_invalid`, whose registry row is `corruption_backstop` / `hard-stop-preserved` / `night_stopped_preserved=true`. An unreachable mount is thus recorded as *ledger corruption*. | `sed -n '783,793p' docs/paper/results-fill-registry.md; sed -n '287p' docs/contracts/calibration_ledger_append.md; sed -n '5218,5224p' joulewise/calibration_ledger.py` |
| SF-2 | should-fix | `joulewise/calibration_ledger.py:4720-4736` | The `probe_custody` docstring documents the *post*-probe mount race but is silent on the only case that changes a decision: a responsive-but-slow mount (>2 s on `exists`/`is_dir`) is reported ABSENT while the tree is in fact complete. The sibling design's addendum names that case explicitly ("unresponsive **or responsive-but-slow**"); this docstring does not. | `sed -n '4720,4736p' joulewise/calibration_ledger.py` |
| SF-3 | should-fix | (absent) | No doc/contract update lands with the code. `JOULEWISE_BACKUP_ROOTS` is documented in four docs, all describing the *scripts* semantics only; the ledger's new lexical-replacement meaning and `CUSTODY_PROBE_TIMEOUT_S` are undocumented. | `grep -rn "JOULEWISE_BACKUP_ROOTS" --include='*.md' . \| grep -v process_traces` |
| SF-4 | should-fix | `joulewise/calibration_ledger.py:4677-4680`; `scripts/validate_powermetrics_fiducial.py:1425,1455` | New provenance seam on the **mint** side: `artifact_hashes()` now honours the override, so with a non-empty `JOULEWISE_BACKUP_ROOTS` it hashes bytes at the mapped root while the caller records the *original* `custody_locator` in the observation. The receipt then claims locator L with digests of bytes at M. Pre-change `artifact_hashes` had no override at all, so this is new. Not adversarial (D-161), but an honest-operator footgun that manufactures a false evidence record — D-161 keeps evidence fail-closed. Fix: refuse (or record the effective path) when the override is active on a minting path. | `sed -n '4658,4680p' joulewise/calibration_ledger.py; sed -n '1450,1458p' scripts/validate_powermetrics_fiducial.py` |
| N-1 | nit | `joulewise/calibration_ledger.py:4677`, `:4704` | The stated justification for relocating `artifact_hashes` (was ~270) and the `_assert_absolute_nonsymlink_directory` wrapper (was 2318) to the file tail is a "line-pinned sentinel test". **No such test exists in the repo.** The relocation is pure churn that separates each wrapper from its `_unbounded` body by 2.4–4.4 kloc. Recommend moving both wrappers back adjacent to their bodies. | `grep -rn "co_firstlineno\|getsourcelines\|calibration_ledger\.py:[0-9]" tests/ docs/contracts joulewise/ scripts/` → no matches |
| N-2 | nit | `joulewise/calibration_ledger.py:4711`, `:5668` | `probe_custody` is imported cross-module by `calibration_bracketing.py:27` but is not in `__all__`. | `grep -n '"probe_custody"' joulewise/calibration_ledger.py` → rc 1 |
| N-3 | nit | `joulewise/calibration_ledger.py:2387,2388,2412,2422` | Up to four sequential probes per historical directory (worst case ~8 s), and `_custody_state`→`_governed_raw_nofollow` at `:5218`/`:5226` probes twice. Correct, but the budget is per-call, not per-locator. | `sed -n '2385,2425p' joulewise/calibration_ledger.py` |
| N-4 | nit | `tests/test_calibration_ledger_custody.py:18` | `test_production_budget_matches_paper_probe` asserts the constant equals its own literal — a self-declared fixture; it kills only a value mutation, not a behaviour. | read |

**No blockers.**

## Per-question evidence

**Q1 — does "absent" ever change a verdict on a responsive machine?** No.
Enumerated callers of the probed helpers and the consequence of `absent`:

| entry point | absent → | consequence |
|---|---|---|
| `_custody_state` (`:4766`) → `:5218` slot validation | `"absent"` | **refusal** `RefusalCode.CUSTODY_PARTIAL` (`:5220-5223`) |
| `_custody_state` → `:4842` `calibration_session_status`, `:4978` readiness | `"absent"` | reported field; drives a readiness *report*, no silent grant |
| `_custody_reasons` (`:1781`) | `{"calibration_ledger_custody_invalid"}` | **refusal**; byte-identical to the pre-change OSError branch (`git show HEAD~3:joulewise/calibration_ledger.py` lines 1784-1799) |
| `artifact_hashes` (`:4680`) | `{}` | equivalent — the old loop already skipped missing artifacts, yielding `{}`; downstream `content_id_from_artifact_hashes` returns `None` and the caller refuses |
| `_assert_absolute_nonsymlink_directory` (`:4704`) → `:2412` | raises `CalibrationLedgerError` | **refusal**; caught at `:2418` → `"custody is outside checkout root"` (message text differs, exception type and branch identical) |
| `_read_contained_nofollow` (`:2342`) → `:2387-2388` | raises | **refusal** `"primary evidence is unreadable"` |
| `_governed_raw_nofollow` (`:2364`) → `:2422`, `:3411`, `:5226` | raises | **refusal** / `CUSTODY_UNREADABLE` / historical-reauth failure |
| `load_calibration_candidate` (`bracketing:1081`) → `_candidate_from_observation:1244` → `discover_calibration_candidates:1338` | `None` → `return ()` | **whole candidate set emptied**, not a partial drop — `bracketing:1339-1340`. No silent skip anywhere. |

Every path is a refusal or an all-or-nothing empty set; there is no fallback and
no silent partial. On a responsive mount the probe never fires, so no ledger
verdict, readiness decision or claim-bearing number moves. `docs/contracts/paper_supply_custody.md` (D-173) governs the *paper* supply seam and never mentions
`calibration_ledger` or `custody_state` (`grep -n "calibration_ledger\|custody_state" docs/contracts/paper_supply_custody.md` → no matches), so it is untouched.
D-151's standing fixed-point rule — "no authenticator path ever enters any
allowlist" — is what the magistrate's scope refusal enforces; this diff complies.

**Q2 — is "absent" honest for "unreachable"?** For the *decision*, yes (fail-closed,
correct under D-161: custody is evidence). For the *record*, no — see SF-1. The
diff provides **no** distinguishable reason: `grep -rn "unreachable" joulewise/calibration_ledger.py` finds only the pre-existing `"custody locator is unreadable"`
message at `:2338`, which the timeout path never reaches. Because the repo already
ships the exact signal (`backup_root_unavailable`) for the identical situation in
the sibling landing, silence here is a **consistency should-fix**, not acceptable
D-161 pruning.

**Q3 — authentication invariants: clean.**
`git diff HEAD~3 HEAD -- joulewise/authentication_io.py` → **empty**.
The only worker target in either file is the nested `probe` closure
(`calibration_ledger.py:4740-4748`); `grep -n "Thread(" joulewise/calibration_ledger.py joulewise/calibration_bracketing.py` returns exactly one construction site
(`:4749`). `probe` calls only `Path.exists` and `Path.is_dir`. Nothing in the
call graph reaches `authentication_io`. There is **no copied context**: no
`contextvars.copy_context()` appears in the diff, and `threading.Thread` does not
inherit context, so the worker sees `active_v2_authentication_session() is None`
— asserted at `tests/test_calibration_ledger_custody.py:294`
(`self.assertEqual(worker_sessions, [None])`). The probe result is a *path
selection only*; it carries no bytes and no digest, and `inspect` runs on the
caller thread (`tests/…custody.py:92-104`) through the unchanged
`read_authentication_input*` functions. Lock retention is directly refuted at
`tests/…custody.py:301-305`: with the worker still alive, `session._lock.acquire(blocking=False)` succeeds and a subsequent authenticated read of another locator
completes inside the same and a later session.

**Q4 — spec-vs-test.**
(a) Absent-equivalence per entry point: `tests/test_calibration_ledger_custody.py:124` computes the genuine-missing outcome first and asserts the timed-out outcome is
*equal* to it, across six entry points × `exists`/`is_dir`, with
`read_authentication_input`/`_nofollow` `assert_not_called` both before and after
the worker is released. Strong. Gap: `load_calibration_candidate` is **not** in
that equivalence loop — `tests/test_calibration_bracketing.py:2636` only asserts
`assertIsNone` on timeout.
(b) Lock safety after timeout: `tests/…custody.py:266-320` (above), plus
`tests/…custody.py:245-262` proving reads run on the caller inside a live session.
(c) Override semantics: empty override never starts a thread
(`tests/…custody.py:58`, `:189`, `test_calibration_bracketing.py:2673`);
non-empty override is suffix-preserving and first-existing-wins with **no
fallback past a corrupt first root** (`tests/…custody.py:239-242`);
runs-root reconstruction asserted exactly (`test_calibration_bracketing.py:2694`).
Self-declared fixture: only N-4.

**Q5 — overbuild / residue.** Nothing from the refused design survives:
`authentication_io.py` is untouched, and the parts 1–2 pattern of executing
inspection/absence callbacks in the worker is gone — the worker body is three
lines of `exists`/`is_dir`. The relocation is *not* justified by any artefact in
the repo (N-1) and should be reverted for reviewability, but is harmless.
Duplication note: `_custody_probe_paths` is a fourth private copy of the
`JOULEWISE_BACKUP_ROOTS` parse (alongside `scripts/paper_excursion_decomposition.py:137`, `scripts/check_paper_replay_fence.py:333`,
`scripts/paper_anchor_correction_quantified.py:224`); semantics are compatible
today but will drift.

## Verdict

**LAND-WITH-FIXES** — SF-1 (emit a distinguishable unreachable signal, matching
`backup_root_unavailable`), SF-2 (docstring the responsive-but-slow case), SF-3
(document the ledger-side override and budget), SF-4 (close the mint-side
locator/digest provenance seam under an active override); N-1…N-4 optional.
