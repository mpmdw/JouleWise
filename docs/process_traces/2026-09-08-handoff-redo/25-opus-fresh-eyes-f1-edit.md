# 25 — Opus fresh-eyes review of the F1 edit (gate ledger row 10)

Scope: `git diff 298da021 2da5c62a -- docs/process/MAGISTRATE_WATCHDOG.md` (the only
non-trace change). Read-only. Bench-verified this session in a scratch worktree at
`2da5c62a` (since removed): probe script + `python3 -m unittest
tests.test_magistrate_watchdog` → **82 tests OK**.

## Verified correct

- **Predicate matches code.** `scripts/magistrate_watchdog.py:518-533`: both bad
  branches build from `initial_state()` (`:494-517`, which has no `state_error` key and
  `resident_session: None`), then set `state_error` + `state="HOLD_UNSAFE"`. `grep
  state_error` finds only those two sites (`:526`, `:531`). `tick` persists the whole
  dict (`:2276 storage.atomic_json`). Bench probe on a `{torn` file: rewritten
  `state.json` has `state_error` non-null, `resident_session` null, `state` HOLD_UNSAFE.
  No path writes `state_error` while a resident is recorded, so the second conjunct is
  load-bearing and correct.
- **No contradiction with `corrupt_lock_no_record`.** `corrupt_lock_refusal:` returns
  `corrupt_lock_no_record` for both subcases; the doc deliberately splits them
  (state_error → Ed may remove; state_error null + bad `resident_session` → preserve).
- **No headless-authorization surface.** The sentence sits inside **ED-HANDS ONLY**; its
  only imperative is a read-only `json.tool`. Removal still reads "Ed must … observer
  Terminal". Nit: it is the block's one actor-less imperative — prefer "Ed determines".

## Findings

**S2 should-fix — `docs/process/MAGISTRATE_WATCHDOG.md:196`.** The verbatim command is
not sufficient: it tests JSON well-formedness, not the watchdog's schema check. Bench-run:
`python3 -m json.tool` on `{}` and on `[]` — the exact shapes step 4 names as malformed —
exits **rc 0** and shows no `state_error`, so the operator lands in the "preserve the
lock" branch although `load_state` classifies them malformed. Self-heals in one tick only
if the daemon is ticking; in this block's own scenario (install aborted at lock seed) it
may not be, leaving no path forward. Fix: also qualify when the parsed value is not an
object or its `"schema"` != `joulewise.magistrate_watchdog_state.v1`.

**S3 nit — same line.** `state_error` is never cleared (no clear site; probe confirms it
survives a later populated `resident_session`). Since `resident_session` resets to null at
session end (`:1639`, `:1723`, `:2172`), the predicate re-qualifies indefinitely after any
past corruption. Not unsafe — with a null resident there is no durable owner to reconcile,
and the ps/inventory absence checks still gate removal — but the "what survives" clause
should say it survives recovery too.

## Verdict

**FIX** — (1) S2: schema-invalid-but-parseable `state.json` misclassified as "preserve".
