# Cold science gate packet: D-079 epoch 25G83, Revision 6, block 1 (assembled 2026-10-02)

What this is: the primary records a cold gate needs to decide whether
`2-candidate/candidate_acceptance_25g83_rev6.json` is a correct application of the
pre-registered rules (`1-registration-and-arms/preregistration_d079_epoch_25g83_rev1.md`,
sha256 `d0034003a7e61683696b88662825d909dc4bb8ad23678edad6bbc8dfd4877b78`, Revision 6 at its end)
to the corpus captured in two windows. The layout follows runbook
`docs/phase_2/derivation_night_runbook.md` §4.3 items 1-8. That runbook was written for a
three-night campaign; Revision 6 (registration §6-§7) replaces it with windows C1, C2 (and a C3 only
if the count rule asks for one). Its count rule returned `CLOSE_AND_DERIVE` after C2, so this block
has two sessions. Assembled mechanically by a derivation seat (Claude Opus 5.5) that read no values
and picked nothing by outcome. Every file was copied whole by
`../packet-assembly-script.py.txt`; `SOURCES.tsv` maps each packet file to its origin, and
`MANIFEST.sha256` hashes every packet file (`shasum -a 256 -c MANIFEST.sha256` from this directory).

| Session id | Window | Night plan id (custody directory name) |
|---|---|---|
| `d079-epoch-25g83-r6-20261001T0617Z` | C1 | `d079-epoch-25g83-r6-derivation-c1-20261001T0617Z` |
| `d079-epoch-25g83-r6-20261001T2252Z` | C2 | `d079-epoch-25g83-r6-derivation-c2-20261001T2252Z` |

## Items

1. **`1-registration-and-arms/`**: the registration file, and per window: `arm-steps/` (stdout of
   arm steps 0-5 as run; step 2 carries the desk-input lines of runbook §0.8), `arm-staging/` (the
   frozen arm environment, battery gate, schedule, render context, arm-attempt records including the
   notice actually sent), `custody-arm/` (what the arm wrote into the window's custody root: night
   plan, calibration plan, chain script and its digests, identity epoch, T1 bindings, start-condition
   manifest, night-probe receipt).
2. **`2-candidate/`**: the candidate whole; `invocation.md` (exact argv of every
   `prepare-candidate` run, exit codes, output digests); the run-3 stdout; `verify-members` stdout
   (24 PASS); the blind campaign R9 record the issuer wrote and checked (`r9_campaign.json`).
3. **`3-chain-logs-and-harvest/`**: per window, the custody `night.log`, the chain's
   `operator_logs/derivation-chain.log` (every `slot_start`/`slot_end`/abort line), the whole
   `night/` directory (chain stdout/stderr, censuses, clean dwell, receipt, result, start
   conditions, `chain.exited`), the harvest's `r9_window.json`, the C1 harvest stdout, and the
   committed battery-float verdict. Also the ledger the issuer read (376 rows) and the committed head
   pin. `unregistered-attempts/` holds the only other C1 arm attempts: `c1-20261001T0137Z` (refused at
   t0 before the chain started; no session, no ledger rows) and `c1-20261001T0555Z` (battery gate
   refused before publication). Neither is a registration session. Revision 6 has no separate
   count-only dry-run file for these windows: the count rule ran inside each harvest
   (`harvest.json`, below) and is replayed in the candidate's `derivation_notes.revision6_count_replay`.
4. **`4-excluded-members.json`**: the candidate's excluded-member list (empty) and the R9 record's
   clock-movement or empty-fit refusals (empty), with the 24 members (`member_id`,
   `manifest_sha256`, `instrument_evidence_sha256`). The gate is asked to check the assertion that
   `affine_clock_fit_empty` is the only registered exclusion mechanism.
5. **`5-quantile-proof.json`**: the candidate's `quantile_proof` blocks verbatim (both the
   two-draw and the within-window derivation). The two bounds are the issuer's declared bounds.
6. **`6-screen-diagnostics-and-S-vs-C.json`**: the candidate's rule outcomes (screen challenge
   count and threshold, the prior-maximum-plus-range diagnostic), per-member comparison with the
   prior level screen, the predecessor's ceiling, rounding, ratified operatives (S and C), source
   statistics and the registered generation row, verbatim.
7. **`7-per-window-distribution-order-clock-anchor.json`**: per-window distribution and timing
   (verbatim from the candidate), the R9 slot order, and per member the clock-anchor fields copied
   verbatim from that member's `instrument_evidence.json`. Diagnostics only; they authorize no
   trimming.
8. **`8-known-conditions.md`**: the registration's "Known conditions (recorded, not rules)"
   section, verbatim (display state at t0 is not constrained).

## Primary artifacts referenced in place, not copied

- Harvest records, committed in this repository (byte-identical to the archived copies the issuer
  read, sha256 in `REFERENCES.sha256`):
  `docs/process_traces/rev6-windows/d079-epoch-25g83-r6-20261001T0617Z/harvest.json` and
  `docs/process_traces/rev6-windows/d079-epoch-25g83-r6-20261001T2252Z/harvest.json`.
- Member evidence (about 1 GB per window): `/Users/edr/night-custody/<night plan id>/runs/instrument_validation/<member_id>/`
  (`manifest.json`, `instrument_evidence.json`, `power_trace.csv`, `events.jsonl`, `raw/`). The
  candidate stores each path relative to `/Users/edr/night-custody`. Re-check them with
  `scripts/issue_calibration_acceptance_generation.py verify-members --artifact 2-candidate/candidate_acceptance_25g83_rev6.json --corpus-root /Users/edr/night-custody`.
- Code: `scripts/issue_calibration_acceptance_generation.py` (the issuer), and the files the
  registration and the R9 record pin (chain `scripts/night_chains/calibration_derivation_only.zsh`,
  cap-rule text, roster, predecessor `configs/calibration/calibration_acceptance_d079_v2_n17_r8.json`).
  `REFERENCES.sha256` lists their digests at this commit (paths relative to the repository root: `shasum -a 256 -c docs/process_traces/rev6-derivation-block1/packet/REFERENCES.sha256` from there).
