# 38 — Apex Fable code-reading diff gate + overbuild prune, transactional installer (rows 7 and 8) — 19:31 PDT (clock-read)

Magistrate `d6888966` (Fable 5.1), full session context. Head: `0ba6ce54` on `feat/2026-09-15-install-windows-transactional`
(= `073a9763` + docs T2 `8f334b8f` + fake launchctl `e867dee9` + import guard `6dc86461` + engine `490be1a3` + fix rounds
`96dee838` / `3b339ac9` / `53d95227` / `d626bf64` / `0ba6ce54`). Read in full by the magistrate at `d626bf64`:
`joulewise/night_agent_install.py` (676 lines) and `scripts/install_night_agent.sh` (91 lines); then the `d626bf64..0ba6ce54`
diff (four shell argv guards; test-only otherwise). Inputs: adjudication 34, seat reports 33a/b/c, contract refuter,
Opus execution lens (lt-28), deltas (lt-30), the lieutenant's packet (row 9 replay 6135/0/0 at `0ba6ce54`; acceptance
`class_1: NO`, `class_2: NO`).

## Design-level questions and answers (D1–D10 against the code I read)

1. **Is exit 0 reachable only through the commit predicate?** Yes. `Transaction.run` sets `result` to 0 only in
   `_teardown`'s COMMITTED branch; COMMITTED is entered only by `_commit()`, which reads the clock once after the
   verification reads (which follow the last launchd mutation) and refuses with `>=` on
   `min(selected_span_close, install_close_epoch_s)`. `uninstall()` returns 0 only after `verified_bootout` yields an
   `Absent` proof for every label. No other `return 0` / `result = 0` exists. I1 by construction.
2. **Can a plist be deleted or overwritten without an absence proof?** No. `Target._authorize` requires an `Absent`
   minted by `require_absent` with the SAME target, label and generation; `bootstrap`/`bootout` bump the generation,
   so a proof taken before a mutation is void after it. `write_plist` (publication) is deliberately outside the proof
   regime (lieutenant ruling R2: publication is not deletion) and is atomic (`os.replace`). I2 by construction.
3. **Is UNKNOWN ever treated as absent?** No. `LaunchctlAdapter.print` yields ABSENT only on rc 113 with the exact
   `Could not find service "<label>" in domain for user gui: <uid>` line; timeouts (5 s), OSError and decode errors are
   UNKNOWN; `require_absent` raises on anything but ABSENT; verification demands LOADED. The wire signature is an OS fact
   pinned by a test (accepted, enumerable residue per 34 §Still enumerable).
4. **One teardown, dispatched on state?** Yes: `_unwind` masks INT/TERM/HUP, calls `_teardown` once, discards queued
   repetitions (SIG_IGN before unmask), restores handlers. `_teardown` branches on `state` only; a `BrokenPipeError`
   from the success print lands in the COMMITTED branch (result forced to 0; stdout dup'd to /dev/null so the
   interpreter's shutdown flush cannot turn it into 120). The RETAINED branch never restores or removes and prints the
   documented lines plus `liveness_unknown: …` per UNKNOWN label; restore failure is RETAINED with exit 1.
5. **Signals before any mutation?** Handlers are installed at ADMITTED→STAGED, before `stage()` and before any write;
   earlier, default disposition terminates a process that has mutated nothing (all refusals precede `mkdir`).
6. **Priors and the sidecar journal.** `.prior` sidecars are written at STAGED from existing plists (`copy2`, mtime
   kept), restored atomically or unlinked on ROLLED_BACK, discarded on SUCCESS, retained on RETAINED; `validate()` refuses
   (exit 3, "re-run --uninstall") when a sidecar exists, so a retained state must be resolved before any new install.
   `uninstall()` removes the plists under proof and DISCARDS the sidecars rather than restoring them — consistent with
   "uninstall removes the agents" (the prior plan's agent is uninstalled too). Design note for the docs/ledger: this
   must be stated where the runbook describes exit 4 recovery; if the counter-review finds it undocumented, that is a
   docs amendment, not an engine change.
7. **Occupancy and I3.** `require_absent` on BOTH labels before admission (UNKNOWN refuses with `state=unknown` and the
   raw diagnostics); no bootout on the success path; therefore no prior managed job is ever loaded when we mutate, and
   restoring files restores the prior state exactly. The concurrent-installer race (a foreign load between admission
   and bootstrap) resolves to a refusal at bootstrap and a teardown that boots out both labels — the single-operator
   assumption adjudication 34 D7 accepted when it rejected the lock file. Recorded, not changed.
8. **Uninstall on the system interpreter.** The shell pins `python="/usr/bin/python3"` for `--uninstall`, the module is
   stdlib-only and 3.9-compatible (no f-strings, `unlink(missing_ok=True)`, `capture_output`), and `validate_install`
   imports the driver lazily; the lieutenant's guard test pins the import isolation. D7 met.
9. **Constants (I5).** None invented; `install_close_epoch_s` and spans come from `scripts/run_night.py` via
   `Prepared`; the shipped default span list is untouched.
10. **Render-only (I4).** `NullAdapter` raises on any launchctl verb; `Transaction` refuses a RenderTarget without it;
    no occupancy check in render mode; render + uninstall mutually exclusive before any launchctl call.

Deviations from adjudication 34 noted by the lieutenant (R1–R10) and read here: NullAdapter nulls only the launchctl
verbs (needed for rendering); proof obligation attached to the target type; `-m` entrypoint with PYTHONPATH pinned and
cwd set to the repo (R8 cure); the audit script's clock read moved after the last launchd mutation. Each is an
improvement or a faithful reading; none changes an invariant.

Residuals accepted as limitations, not defects (to appear in the PR body): no `fsync` (atomicity, not durability —
power loss untested; SIGKILL at 14 seams tested); the D2 wire signature pinned by a test rather than re-probed per run;
concurrent installers can lose each other's sidecars (lock rejected); `<custody_root>/night` at 0o755 pre-existing.

## Prune (row 8)

Nothing overbuilt: the engine is the adjudicated shape and nothing more (no lock, no journal directory, no duration
constant, no retry). The test matrix is large (1157 lines) because the product cells are the guarantee; the mapping
table ties every old FIX-1..10 assertion to a cell. Merge-able once row 6 (fresh Opus counter-review) and the delta on
fix round 4 close.

Verdict for row 7: PASS at `0ba6ce54`.
