# 07 — Harvest record, 06:55 PDT (clock-read), activation `d6888966`

All four detached seats reported between 06:47 and 06:50 PDT (wall time; the
Astra xhigh implementation seat took about 13 minutes).

| Seat | Report | Outcome | Landed as |
|---|---|---|---|
| A — INSTALL-WINDOWS-MULTI-01 implementation (Astra xhigh, brief 1acf2aee/07) | record 02 | `blocked/partial`: FIX-1..5 implemented; V1/V3–V8 pass; V2 had two failures = generated runsheet region drift (NEEDS_SCOPE F1, out of its scope) | `391a194b` on `feat/2026-09-15-install-windows-multi-01` (nine files by pathspec) |
| D — docs (Astra high, brief 1acf2aee/08) | record 03 | `findings/complete`: D-1..D-4 written from the adjudicated design (record 1acf2aee/06); D-5 no change; F1: docs written against the design, not seat A's code; F2: runbook §3 distinct-calendar-days constraint (scientific registration) left as is | `d49c0b9b` on `feat/2026-09-15-install-windows-multi-01-docs` (four files by pathspec) |
| PACK-ROOT scout (Astra xhigh, brief 1acf2aee/04) | record 04 | `findings/partial`: BUILD is the ruled route and waits for the issued G2-a pin (V5-DESK-DAY-01 owns it); roster replacement needs Ed; GAMMA generator emits `claim_leaf`/`bound_leaf` where T-0 reads `claim_root_leaf`/`bound_root_leaf` (start_now); Q2/Q5 blocked by the read-only sandbox | no edits (read-only); lead bench-verified the GAMMA defect at `664b3f6c` (`generate_configs.py:2697` vs `:1882` and `arm_readiness_evidence_t0.py:1017–1018`) |
| Lanes registration (Astra high, brief 01) | record 05 | `findings/complete`: A197 WATCHDOG-STALE-EXIT-CLASS-01, A198 FIXTURE-FAKE-VLLM-LEAK-01; 172 rows; `gen_state --check` rc 0; 44 tests OK — re-run by the lead at the bench | `664b3f6c` on main (rebased onto `1d39729c`, ff-pushed) |

## Lead bench work

- Seat A's NEEDS_SCOPE F1 approved at the bench: the three-line generated-region
  replacement it prepared (`/tmp/install-windows-runsheet.patch`) applied to
  `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`; then
  `tests.test_gen_derivation_night`, `test_run_night`, `test_magistrate_watchdog`,
  `test_install_night_agent`, `test_night_gate` all OK in `wt-install-windows`
  (lead-run). Committed `33bdc457` on the seat A branch.
- Integration tree `int/2026-09-15-install-windows` at `1cc8db30`
  (`wt-integ-install-windows`): seat A head `33bdc457` + `origin/main 664b3f6c` +
  seat D head `d49c0b9b`, both merges clean; the five modules plus
  `test_docs_freshness` and `test_gen_state` OK (lead-run). Pushed.
- GAMMA root-key repair seat launched 06:54:36 (Astra high, detached, brief 06,
  worktree `wt-gamma-keys`, branch `fix/2026-09-15-gamma-root-keys` at
  `664b3f6c`), output `/tmp/magistrate-d6888966/12-gamma-keys-astra.md`.

## Open for the gauntlet (handed to the Opus lieutenant, records `lt-*` in this directory)

1. Reconcile seat D's docs against seat A's actual code: seat A's report lists
   exact replacements (`MAGISTRATE_WATCHDOG.md:31,42,48,52,54`; runbook
   `:1250–1263`, `:1411–1416`, `:1389`, `:1423`, `:1150–1166`, `:2113`), and seat D
   wrote its text from the design before seat A existed (its F1).
2. Two refuters with distinct lenses (contract vs execution) on the integrated
   diff `origin/main..int/2026-09-15-install-windows`; fix rounds with
   defect-shaped regressions; delta re-audit of every fix round; replay at the
   final head; twelve-row ledger; PR body. Merge stays with the magistrate.
3. Seat D's F2 (runbook §3 calendar-days constraint vs D-181) is a question for
   the packet, not a fix: record it for the cold gate if the refuters agree it is
   design-bearing.
