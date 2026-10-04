# Desk-day design seat (`_v5`), 2026-10-04 14:56 PDT (headless orchestrator seat, Opus 5.5)

Brief: `docs/process_traces/2026-10-04-activation-df31cb27/40-desk-day-seat-brief.md`. State:
`~/night-archive/desk-day-v5/` (`progress.json`). Main at start `8fa002f7`. No unread owner mail
(`from:claude2.glaring610@passmail.net is:unread`: none). Nothing armed.

## Lanes launched (Sol 6.1 through `codex-run-v3`, detached)

| Lane | Worktree / branch | Effort | Brief | Report |
|---|---|---|---|---|
| Issuer obligation (seal record 52 (a), (b); Fable 4 on #463) | `JouleWise-wt-dd5-issuer`, `feat/2026-10-04-g2a-issuer-harvest-bound` | xhigh | [10](10-sol-issuer-brief.md) | `~/night-archive/desk-day-v5/sol-issuer.md` |
| `G2A-ATTACH-GUARD-TESTS-01` + #467 Fable N3, N5 | `JouleWise-wt-adae-tests`, `tests/2026-10-03-g2a-attach-guard-tests` (main merged in, `eb0c3926`) | high | [11](11-sol-guard-tests-brief.md) | `sol-guardtests.md` |
| `RUN-CONFIG-NORMALIZED-PIN-01` | `JouleWise-wt-dd5-runcfg`, `fix/2026-10-04-run-config-normalized-pin` | high | [12](12-sol-runcfg-brief.md) | `sol-runcfg.md` |
| Scout: pin home, pack generation, re-proof, next block | `JouleWise-wt-dd5-scout` (detached, read-only) | xhigh | [13](13-sol-scout-brief.md) | `sol-scout.md` |

The step3 interactive-session heuristic already excludes `codex` lines (block-3 arm recipe
`docs/process_traces/2026-10-03-design-block3/40-g2a-b3-arm-recipe.md:318`); nothing to do.

## Results so far (15:00-15:50)

- Guard-tests seat: N3 and N5 added (`93b84dae`); 211 passed, 1 skipped; mutation kill for N5 shown. PR #469.
  Executing review (Sol 6.1 high): brief [14](14-sol-guardtests-review-brief.md).
- Run-config seat: verdict "wrongly refused" (the pack pin is over the source config; the runner writes
  `BenchmarkConfig.to_dict()` bytes, `joulewise/bundle.py:~950`). Fix `ee749c39`: authenticate the source
  config against the pin, then the run config against the runner-normalized hash, then the metadata binding.
  Report [12r](12-sol-runcfg-report.md). Executing review: brief [15](15-sol-runcfg-review-brief.md).
- Scout: report [13r](13-sol-scout-report.md). Findings that change the plan:
  1. The pin's home is `configs/campaigns/d117_contrast_v5/prefill_pin/` (runsheet Phase D); `--ruling-trace` is
     the 08-30 ratification path.
  2. Both `_v5` floor generators hardcode `PREFILL_LENGTH = 512` and refuse a pin of another length. Checked
     privately against `selection.json`: the selected length is not 512, so both floors need a producer change
     (D-117: the prefill floor cells ride the floor windows, so they measure the selected length).
  3. The contrast generator cannot pass generic generator authentication (scout §2).
  4. All three generators bind acceptance `n17_r6` (previous OS epoch), not `n24_25g83_r2` (in force).
  5. Next measurement: the D-176 pack-bound rehearsal (`r1`) then G2-b (`s1`), not a claim window; the first
     claim-bearing `_v5` window is ALPHA, after L10-A, the launch-realization recheck, the claim registration
     and #416.
- Producer seats launched (Sol 6.1 xhigh): floors [16](16-sol-floors-brief.md)
  (`feat/2026-10-04-v5-floor-prefill-from-pin`), contrast [17](17-sol-contrast-brief.md)
  (`feat/2026-10-04-v5-contrast-replay-acceptance`). Orchestrator ruling: packs bind the acceptance in force
  (`n24_25g83_r2`), the floors take their prefill length from the issued pin only.

## 15:50-16:10

- PR #469 (guard tests): review [14r](14-sol-guardtests-review.md) FAIL, R1 MAJOR: the F6 cleanup in
  `scripts/recover_calibration_ledger.py` could unlink a writer-lease lock inode another writer holds
  (contract `docs/contracts/calibration_ledger_append.md`: the inode is never deleted). **Fixed** by dropping
  the unlink (`7f7cbec6`); the lock stays in the archive (an empty file). 19/19 mutants killed. G2 (N3 mocks
  acceptance authentication and strict member validation): **accepted** as a conditional bracket-decision
  regression, which is what Fable N3 asked for. The controller change is a docstring (reviewer: AST
  unchanged), so the PR has no executable measurement change left: Fable pass N/A.
- PR #470 (run config): review [15r](15-sol-runcfg-review.md) FAIL, F1 MAJOR (second plan-tree read not bound
  to `tree_sha`) **fixed** by the lead (`2a682b2e`), test added; 49 passed. Cold Fable final pass launched
  (brief [21](21-fable-runcfg-brief.md)).
- PR #471 (issuer): round 1 [10r1](10-sol-issuer-report-r1.md) asked two rulings. **F1 ruled:** the end-state pin
  keeps D-166's static `exhausted_ladder_branch` declaration (a pre-registration constant in every pin, not an
  assertion); authority is the closed end-state record. **F2 ruled:** scope added for the desk-chain
  integration test. Round 2 [18r](18-sol-issuer-report-r2.md): implemented; dry issue from the real archive exit
  0 with `g2a_record_sha256` = `c694c488…8222`; end state on the real RECOVER record refuses
  `end_state_trigger_not_met`. Executing review (Sol xhigh) brief [19](19-sol-issuer-review-brief.md).
- Floors round 1 [16r1](16-sol-floors-report-r1.md): pin-derived length and acceptance `n24_25g83_r2` done;
  blocked on `joulewise/paper_reported_energy.py` (reported cells hardcode `prefill-p512`). **Ruled:**
  prospectively register ladder-specific `prefill-p<L>` identities, historical p512 bytes unchanged; one length
  per family. The round-1 span projection (whole window × L/512) is rejected as a plan; round 2 builds a
  component estimate. Round 2 brief [20](20-sol-floors-r2-brief.md).

## Next-block consult (blind, one round): Sol 6.1 xhigh [31](31-sol-next-block-consult.md), Opus 5.5 [32](32-opus-next-block-consult.md)

Both seats: register option (a), one qualification block with a pack-bound rehearsal occurrence `r1`, an
arm-and-expire control and the real-pack G2-b `s1`; neither G2-b alone (D-176 §4: G2-a discharges no gate;
the T-0 liveness row needs the rehearsal's receipt bundle) nor straight to ALPHA (the first real `_v5` bytes at
the new prefill length must meet validate/reduce/finalizer before claim custody; `CAMPAIGN_TRANSACTION` needs
G2-b's verdict). Both: land the launch-realization recheck and the unattended one-block stop BEFORE `s1`, so
G2-b runs the claim head; both name G10 (Ed-owned privileged-anchor positive control) as an open owner link.
They differ on recovery: Sol allows no capture-bearing recovery (Q3 fence), Opus allows one `s2` after a named,
removed cause. Not a science disagreement on the measurement; the orchestrator rules it at registration.
Opus adds: seal the claim analysis plan before the `s1` harvest is opened (blindness). Sol adds: pre-register an
outcome-independent environmental diagnostic before claims.
Issuer review [19r](19-sol-issuer-review.md) FAIL: F1 (block-3 provenance from editable declarations) and F2 (a
permitted validity-filtered SELECT refused). **F1 disposition:** fix by anchoring to the records committed on main
(`windows/<plan_id>/harvest.json`, `selection.json`), the archive's own `SHA256SUMS`, and the frozen plan's policy;
coordinated multi-file forgery is outside the threat model (D-161). **F2:** fix. Round 3 brief [22](22-sol-issuer-r3-brief.md).
