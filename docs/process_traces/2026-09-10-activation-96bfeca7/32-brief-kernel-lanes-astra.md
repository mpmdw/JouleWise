SESSION_MODE: delegated
WRITE_SCOPE: ["docs/process/state_kernel.json", "TASK_QUEUE.md", "docs/process/EXPECTED_IDS.md", "tests/test_gen_state.py"]
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# Kernel bookkeeping for activation 96bfeca7 (gpt-6-astra, high, genre implementation): three new lanes, two status notes, regenerate

Worktree: this one, branch `bookkeeping/2026-09-10-kernel-lanes` from origin/main (`57da1d30`, checkpoint T38h). Edit ONLY the
kernel `docs/process/state_kernel.json`, then regenerate every generated region with `python3 scripts/gen_state.py`
(TASK_QUEUE.md and whatever else the generator owns), and keep `python3 scripts/gen_state.py --check`, `python3 -m unittest
tests.test_gen_state tests.test_docs_freshness` green. If the generator pins an ID count or list in a file outside
WRITE_SCOPE (grep EXPECTED_IDS / expected_ids), STOP with NEEDS_SCOPE naming it; do not hand-edit generated regions. Read the
kernel's existing rows (e.g. `GATE-SENSIBILITY-SWEEP-01`, `ARM-RETRY-CLASS-01`, `NIGHT-REHEARSAL-01`) to copy the exact
row shape (acceptance{evidence,pointer,summary}, authority{label,path}, dependencies, fallback, fences, flags, goal, id,
lane, priority, rank, status, status_note, stop_card). Ranks: append after the current maximum. Evidence paths below are
on branch `bookkeeping/2026-09-10-activation-96bfeca7` (pushed); reference them by repo-relative path.

## New lanes (all `lane: agent`, `status: queued`)

1. `NIGHT-STREAM-PATHS-01` (priority p2_next_slice). Goal: render the night agents' launchd `StandardOutPath`/`StandardErrorPath`
   outside `night/` so a pre-night dead-man firing leaves `night/` literally empty. Authority: cold gate 31 ruling 10 + addendum 11
   (`docs/process_traces/2026-09-10-activation-96bfeca7/31-coldgate-packet-deadman-stream-files/10-coldgate-fable-ruling.md`,
   `11-ruling-addendum-opus-amendments.md`). Acceptance summary: `configs/launchd/com.joulewise.night.plist.template` renders
   `@@CUSTODY_ROOT@@/launchd/@@LOG_STEM@@.out|.err` (or another path outside `night/`); `scripts/install_night_agent.sh:125`
   creates that directory as well as `night/`; `tests/test_run_night.py:816–817` amended and a new assertion that neither
   rendered path starts with `<custody_root>/night/`; harvest rows updated to preserve the courier transcript from the new
   location; historical traces untouched; lands under the twelve-row gate; NOT a gate on the 09-11 harvest or the 09-12 arm.
   status_note: "2026-09-10: ruled by cold gate 31 as a registered follow-up (item 5 MET on the 09-10 07:00 firing under the
   driver-records reading); until it lands, the item-5 predicate P1–P4 of ruling 10 / checklist 13 §3a is the criterion."
2. `FIXTURE-SENTINEL-CONTROLLER-01` (priority p2_next_slice). Goal: cure the controller test fixture that still sleeps through
   its post-idle capture against a real deadline, so `tests.test_controller::test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce`
   stops failing on a loaded local host (CI green at 078a13a4; local failure reproduced at main). Authority: root-cause report
   19 + lead note (`docs/process_traces/2026-09-10-activation-96bfeca7/19-rootcause-controller-idle-drift-local-astra-report.md`,
   `19-lead-note-local-controller-failure.md`). Acceptance: the fixture uses the bounded `--no-sleep` policy shared with the
   campaign-test helper (PR #310, consult 87); defect-shaped regression per report 19 §Remediation (byte-exact promotion, bounded
   post drift, strict validation clean, timeout reproduces without the cure); third instance of the host-timing fixture class
   (87, 99, 19) recorded. status_note: "2026-09-10: registered by activation 96bfeca7; not on the G2-a path; CI is the gate of
   record for PR #314, whose local replay names this one known local-only failure."
3. `GATE-R2-COVERAGE-ULP-01` (priority p3 or the kernel's lowest active tier; `fences`: D-138 — rides the Phase-2 transaction
   branch, lands only inside the atomic re-freeze with the D-079 acceptance reissue). Goal: land seat-A repair R2
   (`joulewise/reduce.py::_anchor_coverage_ok` endpoint coverage using the same one-ULP endpoint arithmetic at both edges as the
   preceding tail gate; run_bundle_layout.md sentence) staged as
   `docs/process_traces/2026-09-10-activation-96bfeca7/15-r2-coverage-ulp-staged-for-d138.patch` with its four regressions in
   `15-r2-tests-staged-for-d138.py.txt`. Authority: lead note 15 + seat-A inventory 02a §B R2. Acceptance: patch applied inside
   the re-freeze, the D-138 pin test updated by the reissue, the four tests green, a delta refuter. status_note: "2026-09-10:
   STAGED, not landed (reduce.py is a D-138 governed input); a rare near-boundary false refusal until then, not a G2-a blocker."

## Status notes on existing rows (append a dated sentence to `status_note`; change `status` only where stated)

- `GATE-SENSIBILITY-SWEEP-01`: "2026-09-10 (activation 96bfeca7): inventory complete (02a 156 rows / 02b 143 rows; the 1e-15 is a
  decimal presentation quantum in an identity check and stays); repairs R1/R3/R4 + G2-a idle_seconds 75 on PR #314
  (`feat/2026-09-10-gate-sensibility-sweep`, final head beb808bc) through the full gauntlet incl. cold gate 24 on the contract
  prose; R2 staged (GATE-R2-COVERAGE-ULP-01); B1 (D-165 provenance band, seat B) needs a decision-log correction → cold gate,
  not G2-a-blocking at G2-a energies; the lane closes when PR #314 merges and the B1 disposition is recorded." Keep status as is
  unless the kernel has an `in_progress`-like value the other rows use; then use that.
- `NIGHT-REHEARSAL-01`: "2026-09-10 07:00 PDT: pre-night dead-man observed standing down (record 30); item 5 ruled MET by cold
  gate 31 subject to the harvest predicate P1–P4 (checklist 13 §3a); items 4 and 6 await the 09-11 harvest."
- `G2A-FIRST-WINDOW-01`: "2026-09-10: no supported short chain (packet 04); proposed inputs PLAN_ID d117-g2a-prefill-probe-20260912,
  NIGHT_ROOT /Users/edr/night-custody/d117-g2a-prefill-probe-20260912, t0 2026-09-12T02:56:00-07:00, WINDOW_MAX_S 13500,
  measurement root /Users/edr/JouleWise-measurement-v5-20260911-g2a at H = the handback commit (inventory row inside H); arm
  materials 11/12/13 on `feat/2026-09-10-g2a-handback-20260912`; Ed emailed 04:50 (1a08b223b02862e9), silence = full chain;
  ruling due after rehearsal acceptance."
- `CLONE-READINESS-01`: "2026-09-10: production clone provisionally cut at 078a13a4 (record 05: clean tree, lock diff empty,
  ledger authenticated with custody replay at sequence 76, tokenizer pins match); fresh cut at H on 09-11 per checklist 13 §6."

Verification: `python3 scripts/gen_state.py` then `python3 scripts/gen_state.py --check` (rc 0), `python3 -m unittest
tests.test_gen_state tests.test_docs_freshness` (gate on rc). No git commit. Report claude-codex-report/v1, genre implementation,
header < 8192 bytes: changed paths, the new ranks, and any NEEDS_SCOPE.
