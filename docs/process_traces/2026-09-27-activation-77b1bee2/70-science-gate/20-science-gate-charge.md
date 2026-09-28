# Cold science gate SCI-25G83-CANDIDATE-01: may the epoch-25G83 calibration candidate proceed to the issuing transaction?

You are a COLD judge: a fresh session with no loop context. **No one who sat on the capture may sit on the exclusions**, which is why you are here. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first.**

**The packet** was assembled mechanically from primary artifacts. It is at `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/packet/`; start at `00-index.md`. It covers runbook `docs/phase_2/derivation_night_runbook.md` §4.3 items 1–8, adapted to Revision 5's two windows.

**Further evidence** (verify; do not trust):
- `../12-astra-rederivation-report.md`: an independent cross-family re-derivation from raw custody. **REDERIVATION: MATCH**, 0 findings.
- `../../60-prepare-record/`: the refusal-branch statement `00-refusal-branch-final-statement.md` (sha256 `8717e33c…`), the amendment `11-predecessor-path-ruling.md`, the pre-checks `20-prechecks/`, and the verbatim run `30-run1/`.
- The custody-repair rulings in `../../50-custody-outside-repo/`.

**Primary artifacts you may read directly:**
- the candidate `…/30-run1/candidate_acceptance_25g83.json` (sha256 `dbad7cc7…b5b2`);
- custody `/Users/edr/night-custody/d079-epoch-25g83-derivation-w{1,2}-20260927/`;
- the run checkout `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2` @ `e7c8bcc6` (issuer, ledger);
- the registration `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` (sha256 `81b65f08…ddf1`), especially Revision 5 and A-R5b;
- `docs/decision_log.md`: the D-125 addendum (2026-09-25) and D-138.

**Rule on:**
1. **Membership and exclusions.** Are the 12 members exactly the registration's retained set? Each of the 12 non-valid captures is `clock_anchor_unresolved` or `detection_nonconvergent`. Is each exclusion a registered mechanism correctly applied (packet item 4)? Could any exclusion have selected on outcome?
2. **Arithmetic and proofs.** Are S, C, the level screen, the quantile proofs (item 5) and headroom correct and within their declared bounds? Weigh the independent re-derivation.
3. **The screen challenge.** Two members, w1-d04 at 0.03611 s and w2-d10 at 0.03808 s, exceed r6's 0.032898493715362 s. The issuer skips the historical veto under Revision 5 (packet 06, issuer :1923–1935). **Does the sealed Revision 5 text remove that veto?** Quote it. If it does not, what follows under the registration?
4. **Physics and science sanity.**
   - The new epoch's level screen (0.0381 s) and ceiling C (0.0190 s) are well above r7's (0.0329 s / 0.0102 s).
   - W2 values run higher than W1's.
   - The valid yield was 50 %, against ≈79 % assumed.
   - The display state at t0 is unconstrained (a known condition).
   - W2 had a +12 mAh battery-gauge step between slots, with no charge event in `pmset`.
   Is there any sign of an instrument, custody or process artifact rather than the epoch's true behaviour? Is anything germane to whether the numbers are true left unchecked? Under the owner's directive, anything germane to verity is mandatory.
5. **The verdict.** Choose **PROCEED TO ISSUANCE** (the D-138 transaction, which has its own gate), **HOLD** (name exactly what must happen first), or **REFUSE** (under which statement item). State the marks the calibration carries and any disclosure the issued artifact or paper must carry.

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every command in the foreground. Use `/opt/homebrew/bin/python3`. macOS has no `timeout`; use `perl -e 'alarm N; exec @ARGV' …`.
- Modify NO file in any repository or custody root. Scratch goes under `/tmp/cg-sci-77b1bee2/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/21-science-gate-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 45 minutes. Mark anything not run as NOT EXECUTED.
- The first line is `VERDICT: PROCEED TO ISSUANCE`, `VERDICT: HOLD` or `VERDICT: REFUSE`. End with a 3-line plain summary for the owner.
