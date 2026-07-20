# 2026-07-20 — Phase 0 instrument repair: anchor estimator v2, energy envelopes, convergence sign-off, first live pulse-fiducial calibration

DRAFT — sections marked [PENDING] are filled at checkpoint close this session.

Ed-directed ("spend serious time making sure the measurement instruments are
rigorous"; ultracode authorized). Executes roadmap Phase 0
(`docs/phase_2/splitwise_replication_roadmap.md`) against the D-078 soundness
gate. Branch: `impl/p0-instrument-repair` (from main `ccfa5c2`).

## Build arc

1. **Design:** Sol xhigh pre-decision consult (thread 019f7df3-8120) rejected
   the lead's naive native-timestamp anchor (stamps are 1-second-quantized
   censored observations, lead-verified) and specified the
   censored-constraint interval estimator (N ∩ C), continuous common-shift
   energy envelopes (interior extrema required — endpoint-only evaluation is
   unsound), the 40-pulse fiducial protocol, and the stream split. Its
   288-bundle sweep: anchor intervals non-empty 288/288, median width 70 ms,
   max 116 ms.
2. **Implementation (ultracode workflow, 76 agents):** three worktree
   streams — A anchor+envelope+fiducial harness (reducer 0.5.1 + AXI 0.6.1,
   additive; 0.5.0/0.6.0 byte-frozen), B engine wire compat +
   cooldown/cap-hit joins + extraction hygiene, C idle-admission core.
   Per-stream review panels (contract/execution/physics + Sol cross-model
   lens), severity-tiered refuters, fix-until-dry with delta re-audits
   (A: 1 round, B: 3, C: 1; zero unresolved). Integration head `3480f1b`,
   full suite `Ran 1910 tests, OK` (21 named environment skips in the bare
   worktree).
3. **C2 hookup (Sol high):** live CPU-aware admission enforcement in the
   controller (production fail-closed, exploratory flagged), typed
   `idle_admission_extension` sidecar schema, adapter-power call site,
   `--whole-window-verdict` NEG-8 bracket pass, attempts ledger. Lead-verified
   fail-closed on missing telemetry under both policies; committed `d1c1538`;
   suite lead-run `Ran 1918 tests, OK (skipped=21)`.
4. **Lead physics verification (independent arithmetic, not the branch's
   code):** r01 anchor interval `[1784491122.657586, 1784491122.770690]`,
   midpoint matching the branch to the microsecond; corrected gross 7.6639 J
   (branch: 7.664159 J) vs the defective 0.274 J; envelope scan
   [6.765, 7.681] J with the maximum at an interior breakpoint.
5. **Convergence sign-off (ultracode workflow):** rounds of one fresh-thread
   Sol xhigh whole-instrument adversarial audit + two Fable clean-room
   physics recomputers + two Sol high sweeps (contract, execution);
   P0/P1 findings refuted by two distinct lenses; Sol high fix rounds with
   delta re-audits. CHECKPOINT STATE (Ed stop, 2026-07-20): round 1 ran
   fully (findings confirmed -> Sol high fix round -> delta re-audit);
   round-1 fix work lead-committed as `ca6861b` after adjudication (the
   worker-drafted D-078 closed-vocabulary amendment ADOPTED; two stray
   scratch files excluded; fix agents had drafted doc changes outside a
   declared scope — lead reviewed each; convergence fix prompts must carry
   exhaustive WRITE_SCOPE next run, lead error recorded). Round 2 was
   mid-flight (final read-only sweep) when Ed called the checkpoint; the
   workflow was stopped cleanly. **Convergence sign-off NOT yet reached** —
   resume workflow wf_c5a2e6c8-147 (script in the session workflows dir)
   or relaunch round 2 fresh next session.

## Live instrument validation (lead-owned [QUIET-MAC], Ed pre-authorized window)

- **Pulse-fiducial calibration:** NOT RUN — Ed's checkpoint stop arrived
  before the quiet window opened. The chain is staged and ready:
  scratchpad `pulse_run.sh` (idle-wait -> displaysleepnow -> 
  `scripts/validate_powermetrics_fiducial.py --allow-live --power-policy
  ac_high_power` from the it-p0 worktree with the main venv). FIRST ACTION
  next quiet window.
- **Stability probe (probe-only runs root, non-claim-bearing):** NOT RUN
  (same stop). Config dir staged in the session scratchpad (`stability/`:
  NEG-8 + short ×2 + mid ×1 with a probe-labeled order manifest). Runs
  right after the pulse calibration; the acid test is the short cell
  reading ~8 J with an honest envelope (defective corpus: 0.274 J) while
  correctly REMAINING cadence-ineligible.

## Checkpoint state

Branch `impl/p0-instrument-repair` pushed at `ca6861b` (streams + C2 +
round-1 fixes; last lead-run full suite at `d1c1538`: `Ran 1918 tests,
OK (skipped=21)`; the round-1 fix commit's suite gate is owed at round-2
resume). No PR yet — opens after convergence sign-off. Remaining before
any re-collection, in order: (1) convergence round 2 to sign-off (both
model families clean at P0/P1); (2) lead final pass + PR per the
operation-loop gate shape; (3) live pulse-fiducial calibration (staged);
(4) stability probe (staged); (5) window licenses from measured
B_effective; then Window-A re-collection per the roadmap. Salvage of the
288-bundle corpus remains a separate Ed ruling under D-078; DF-TELEM
unchanged.
