# Seat: Mythos 5.2, #774 re-attack 2

`date`: Sat Nov 14 18:28:50 PST 2026

**Verdict: REFUSE at `3b58b23e4`.** The guard module itself now holds: N1, N2, N3, N8 and N10 are closed. But the sealed desk command still leaves per-member energy in the clear through the harvest it launches (M1), and the committed finalized manifest publishes per-member file sizes (M2). M1 is the audit's original finding by a third route.

**Method and limit.** This is a static trace again: I read via git only, as instructed, and ran no test, probe or mutant. RL-152 §3.5 row 2's executing replay of N1 to N4 is still owed. M1 in particular deserves a ten-minute executing check before anyone acts on it.

**Blinding.** I opened code, tests, tracked docs, the PR body, the prior report, the three rulings, the roster tags of the tracked `collection_plan.json` and the pilot pack's `registration.json`. My read of RL-149 §3 ran about 30 lines into §4 (a design table, no data). No measurement, slot, transcript, energy, power or meter file; no SSH; nothing edited.

## 1. N1 to N11

| Item | Status | Note |
|---|---|---|
| N1 | Closed | Prints rows and thermal records both take `ep.episode_id` (`rl145_prints.py:356`, `thermal_desk.py:249`). A missing-artifact row has no condition, so it is sealed. |
| N2 | Closed | Lists, residual rows and transfer scores are benign-only with one digest; `distinct_trajectories` is withheld. Cell keys carry the condition, so a printed cell cannot hold a non-benign member. |
| N3 | Closed | A fresh 16-byte nonce per digest (`v4_desk_seal.py:213-221`); no reuse path. Nit: the DC stdout line omits `sealed_nonce` (`align_v4_session.py:1006-1007`). |
| N4 | Interim form | See section 3. |
| N5 | Fail-closed, two residuals | M5. |
| N6 | Not closed | M2 and M6. |
| N7 | Partly, and worse than stated | M3. |
| N8 | Closed | |
| N9 | `_desk` closed; the rest open | M4. |
| N10 | Closed | Every membership test goes through `NotBenign`; `None` is excluded from the benign set (`:452`). |
| N11 | Unchanged | Lead's call. |

## 2. New findings (M1 to M8)

### M1 — HIGH: the desk's own harvest writes an unsealed per-member table
- **Path.** `_desk` launches the harvest with `--export-dir <session>/export --non-claim` and saves its stdout (`scripts/align_pilot_session.py:352-355, 363-365`). The export applies blinding offsets only `if not non_claim or grouped_blind` (`joulewise/b6/export_runs.py:717`). It writes `export/<pack>/<session>.runs.csv` (`:730-731, 754`).
- **What leaks.** Per run id, sabotage included, in W1, C and T: gross, idle-subtracted, request and per-phase energy (`:698-704`), token counts and phase durations (`:395-414`), status and flag codes.
- **Why it fires.** `grouped_blind` needs `blinding_group` in the pack registration. The only align registration in the tree says "no grouped claim blinding" (`configs/campaigns/align_pilot_v3/registration/registration.json`); no v4 one is tracked and the v4 kit writes none.
- **It cannot be skipped.** Finality needs harvest exit 0 or 6 (`light_triage.py:127, 140`), and both come after the export returns (`scripts/harvest_b6_session.py:72-77`). If no registration resolves, the harvest faults at export and no window can be final.
- **Second part, MEDIUM.** `archive/derived/flags.jsonl` holds each member's harvest flags with observed values, which is the content `seal_line` replaces with a digest. `staging/harvest.stdout`, `derived/b6-acceptance.json` and the export sidecar carry `flag_counts` over all members. Beside W1's printed benign harvest lines, that is RL-152 §3.2's subtraction again.
- **Why tests miss it.** The guard tests run `--no-harvest` (`tests/align/test_v4_desk_release_guard.py:383`), so the sentinel detector never sees harvest output.
- **Fix.** Before release on a v4 session, send the export and harvest streams under `archive/withheld/`. The lead rules which `derived/` files are restricted for v4. Add a test that runs the real harvest on the synthetic bundles and scans every file outside `archive/withheld/`.

### M2 — HIGH: the committed finalized manifest lists every bundle file with its size
- **Path.** `_tree_rows` records `{sha256, size}` for every regular file in the session root (`joulewise/align/apple/harvest_offload.py:121-137, 423-447`). Bundles live inside it (`scripts/bytes_h_session.py:360`). The record carries the file at `records/$K/evidence/finalized_manifest.json`, and the packet builder reads it from the pushed ref (runbook `:134`; `scripts/align_v4_next_arm_packet.py:221-235`).
- **What leaks, per member.**
  - The raw plist size, which N6's own fix calls elapsed time.
  - The sizes of the transcript, turn, event and gate-journal files.
  - The names `outputs/align_failure.json` and `align_runtime_events.jsonl`, which exist only after a deadman or fault (`workload.py:799-841`). That is the carved bit by file name.
- **Fix.** A design call, needed before W1's first record (R1 is exempt, `:224`). Either commit only the digest and keep the manifest restricted, or hash per-member sub-manifests into one entry.

### M3 — MEDIUM: the unlisted-codes line can never read `none` on real bundles
- **Path.** The runner stamps every episode with `single_request_summary_fields_not_episode_metrics:…` and `episode_interval_excludes_scoring_and_serialization_tail` (`workload.py:710-712, 749`). The reader strips only a third code (`:926-928`), and both reach the thermal records' `flags` (`thermal_desk.py:251`).
- **Consequence.** Neither code is allowlisted or a known prefix (`v4_desk_seal.py:1078-1094`). So W1 always prints `withheld members: present, to the research lead`, and C/T counts start at twice the readable members. A real new fault is masked.
- **Why tests miss it.** The fixture patches `read_bundle_record` (`test_v4_desk_release_guard.py:255`).
- **Fix.** List the bookkeeping codes as known, and test `unlisted_codes` on a runner-produced episode.

### M4 — MEDIUM: N9's cover for `u3_export` and `reduce` ends at the merge
- **Path.** `measure_pair` writes `energies_j` and suffixed exclusion reasons for any two named bundles (`scripts/align_v4_u3_export.py:83-116`). `reduce` writes per-turn energy tables to an operator-chosen directory (`pm_reduce.py:181-188`).
- **Why the cover fails.** RL-149 §3 line 4 names only the desk and the triage, and holds "until it merges".
- **Fix.** Refuse a bundle whose stored pack tag is a v4 window before release; the tag is in each bundle's config (`align_v4_kit.py:1676`, `align_v4_series.py:350`). Make `reduce` write only under `archive/withheld/`.

### M5 — LOW-MEDIUM: the standalone thermal desk takes its scope from the manifest
- A C or T manifest tagged `W1` on every member prints its benign rows whole (`v4_desk_seal.py:1233-1235`). The fix is the same stored pack tag.
- The repo's own W1 manifest tags its reference members `pilot7-reference` (`scripts/align_v4_w1_synthetic.py:339`). It now seals as C, so W1's contrast and RL-145 prints never appear. That invites a hand re-tag.

### M6 — LOW: N6 residue in harvest-off
- `workers`, `free_memory_bytes` and `reserve_bytes` are printed together (`scripts/align_v4_harvest_off.py:337-343, 519`). When memory binds, they bracket the largest plist to a factor of (w+1)/w.
- A failed sweep row prints its peak on stderr (`:355-360`).
- Fix: print the worker count and basis only.

### M7 — LOW: N4 soundness
Covered in section 3.

### M8 — LOW: `tokens: null` on a sealed member
It shows that the member's token record is incomplete, which may track a cut. Please confirm.

## 3. The interim N4 line

The code matches the runner. A refused XML call is flagged once, on the last turn (`workload.py:566-571, 652-655`), and form (b) fires when that turn is the first or second. The line stays one bit. Three gaps for the lead's ruling:

- **Late single breakage.** A refusal first appearing at turn index 2 or later on one D member reads `within`.
- **Form (c) is fragile.** It needs both sabotage D members readable. In the standalone desk it also needs the manifest's `role` tags (`v4_desk_seal.py:1130-1131, 1263`).
- **Untested on runner output.** The tests hand-build records, the same weakness as M3.

## 4. Next steps

1. An executing seat confirms M1 by running the real harvest on the synthetic bundles and listing `export/`.
2. The builder fixes M1 and M3 before merge.
3. The lead rules on M2 before W1's first record, and on M4, M5 and N4.