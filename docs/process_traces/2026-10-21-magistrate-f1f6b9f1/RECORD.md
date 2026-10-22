# Magistrate activation f1f6b9f1 (Opus 5.5, headless, 2026-10-21 from 10:56 PDT)

Launch: no pending notices; no unread mail from Ed; directive issues open are the standing ones (#405-#422), nothing new; no `standdown.request`.

## BYTES item H re-arm stopped at the pre-calibration capture (10:51 PDT)
- Session `bytes-h-20261021T173857133683Z` (root `/Users/edr/night-bytes/h-20261021T173856Z`), t0 10:46:00 PDT. Arm physics all PASS (battery, clock, contention, disk, instrument, thermal; census clean). Watchdog terminal release `chain_stopped` at 10:56.
- Chain: `bytes-mac-check-bracket-reservation` rc 0 (status `reserved`), settle, `bytes-mac-check-pre-calibration` rc 2 after 1 s: `calibration_session_not_found: bracket session is not present in the ledger`; `chain.stop pre_calibration_capture_failed` rc 11. Zero runs.
- Cause: the measurement view (`scripts/bytes_h_session.py measurement_view`) linked code but kept a private copy of `runs/calibration_observation_ledger.jsonl`. The reservation got `--ledger <view>/runs/...` and wrote its two rows there (view ledger 402 to 404 rows). The capture takes no `--ledger`; its default is `REPO_ROOT/runs/...` with `REPO_ROOT = Path(__file__).resolve().parents[1]`, and `<view>/joulewise` is a link, so it read the checkout's ledger (402 rows, no reservation). The b6 sessions ran from the checkout itself (and the b6 smoke from a real clone), so the two paths were one file there. The a69c5394 rehearsal drove lineage publication and member checks but not the reservation and capture.
- Acts: `desk` run from the h2 checkout (harvest_exit 0, `gates_exit 1` with `decimal.ConversionSyntax` on a zero-run session; disk disclosure 497,164,288 B between arm and desk). Both night agents uninstalled (`install_night_agent.sh --plan <custody>/night_plan.json --uninstall`; no `com.joulewise.night*` in launchd or LaunchAgents). Canonical root fast-forwarded to a06bd6f9f. Ed emailed (Gmail 1a15f9ef64507841, on the arm-notice thread).

## Fix
- `lane/2026-10-21-bytes-h-session` 08ca7dfa4, then c10b6895f: the view links `runs/` to the checkout as a whole directory, so the chain's `--ledger` and every default ledger path are one file. The head pin stays a regular-file copy: 08ca7dfa4 also linked `configs/calibration/`, and a real dry prepare then printed INPUTS_ONLY `calibration_ledger_head_uncommitted`, because the plan writer asks git whether the pin is committed and git does not look through a linked directory. No chain stage writes the pin (only the desk pin advance, `_advance_head_pin` via `recover_calibration_ledger.py advance-head-pin`), so a copy is safe.
- Regression test `MeasurementViewLedgerTests` (passes on c10b6895f, fails on 6ef1ffc86); `tests.test_bytes_h_session` 32 tests OK.
- CI: draft PR #518 (`ci/2026-10-21-bytes-h3`, lane merged with main).

## Rehearsal (lead, real programs)
- Scratch clone at c10b6895f (`/Users/edr/night-archive/f1f6-h3/scratch-checkout`, h2's venv linked, the 402-row ledger copied). Real `prepare` into `/Users/edr/night-bytes/dry-f1f6-h3`: STAGED (never installed).
- `rehearse_real.py` (a69c5394's): lineage published, 123/123 member checks PASS, roles corpus 18 / start 3 / midpoint 1 / end 3 / science 98.
- The chain's own reservation command, under the published hazard context: rc 0, `reserved`; the rows landed in the checkout's ledger (402 to 404). (Without the hazard context the reservation requires a committed pin and refuses the view's copy; the night always has the context, so that refusal is a rehearsal artifact, not a night path.)
- The chain's own pre-calibration capture command, live: passed the ledger lookup (`calibration_writer_arm_authorized`), the step that refused at 10:51.
- The window calibration verdict stage on that capture: rc 0, `verified`, no flags.
- One real member through `run_campaign` (the bound-collection stage, stopped after the first bundle): `validate` and `prepare` passed and the member bound the pre-calibration; two members (r01, r02) then failed `idle_baseline` with `powermetrics admission stream did not complete the idle slice before timeout`. Cause: powermetrics delivers about 250 ms frames at `-i 100` under this activation (direct probe: 30 frames, median 254.7 ms; each of the four samplers alone 229-243 ms), so 576 idle frames (57.6 s at 10 Hz) cannot arrive within the 96.5 s timeout (577 x 0.1 x 1.5 + 10). Not a night path: the night's own arm cadence check at 10:46 (night agent context) measured 300 frames in 39.76 s (about 133 ms), the same as a b6 member's idle stream (576 frames in 75 s, median 130 ms), which completes the slice in about 77 s. The slowdown is this magistrate job's launchd context (as on 10-17, when the b6 loop needed `ProcessType Interactive`). Rehearsals that need member-cadence powermetrics should run under a night-agent-like context.

## Executing review (Opus, non-author): ACCEPT WITH CHANGES
Report `/Users/edr/night-archive/f1f6-h3/REVIEW.md`. Ran the module (32 OK), the regression test both ways, and a census on the dry view: one physical ledger for every reader and writer (reservation by argv; captures and `run_campaign` members by default, so the members would also have missed the session before the fix; desk and harvest by the plan's path). No chain stage writes the head pin.
- L1 (low, operational): the view's `runs/` now writes into the checkout, so a reserved attempt leaves an open session there and a re-prepare from that checkout stops at INPUTS_ONLY. Disposition: accepted as procedure; before each prepare, confirm the checkout's ledger head equals its committed pin, or use a fresh checkout. Done for this arm (h2: 402 rows, pin 402 committed).
- L2 (low, record only, predates the fix): the chain's `session-status` record checks the view's pin copy against the checkout and will print a misleading `calibration_ledger_head_uncommitted` in `post-bracket-terminal-boundary.json`; harvest derives its own boundary, so no number. Disposition: flag, not refuse; no change now.
- Support for the launchd-context reading: `joulewise/night_agent_install.py` refuses any night agent whose `ProcessType` is not exactly `Interactive`; `com.joulewise.magistrate.plist` sets none.

## H re-arm
- CI on #518 (lane c10b6895f merged with main): all 20 checks pass except gate-ledger (CI-only PR, no ledger).
- Pre-arm: no unread mail from Ed; directives unchanged; no `standdown.request`; AC, IsCharging No, InstantAmperage 0, 100%; no thermal warning; 100 GB free; caffeinate pid 885 alive.
- h2 checkout fast-forwarded to c10b6895f; ledger 402 rows, pin 402 committed (review L1).
- `prepare` into `/Users/edr/night-bytes/h-20261021T185555Z`: STAGED, session `bytes-h-20261021T185555335572Z`, t0 12:03:00 PDT 2026-10-21 (19:03:00 UTC); view `runs` links to the h2 checkout's `runs`.
- Arm notice emailed to Ed before install (Gmail 1a15fd22d9427559). `install` is this session's last act.

## Pruning list (this session)
- Chain stop on capture refusal: caught a real plumbing defect (ledger split), cost about 1 h 10 min of Mac time, no number.
- Lead rehearsal through the chain's own commands: caught the git-through-symlink defect in the first fix (INPUTS_ONLY) before arm.
- Opus executing review: found the members shared the defect (no number), two record-level lows.
