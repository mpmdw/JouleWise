# Seat: Mythos 5.2, #774 re-attack

`date`: Sat Nov 14 15:26:34 PST 2026 (session start 15:10:03 PST).

**Verdict: REFUSE at `18fb3746f` (content `ea9b54a03`).** One HIGH leak path remains in an entry point the PR lists as sealed (N1), §3.4's tool-path tripwire cannot fire on the failure it names (N4), and three MEDIUM recovery paths are open in W1 (N2, N3, N5). Each fix is small, but N4 needs a re-ruling.

**How this was done, and its limit.** This is a static trace only. Python and writes outside the worktree were both denied in my session, so I ran no probe, no test and no mutant. Every finding below is from reading code via `git show`/`git diff`/`git grep`, with line numbers at `18fb3746f` (guard files are identical at `ea9b54a03`). RL-152 §3.5 row 2 asks for recovery attempts on real-shaped inputs; this seat meets that only as traces, so an executing seat should replay N1 to N4 after the fixes.

**Blinding.** I opened no measurement, slot, transcript, energy, power, meter or powermetrics file, nothing under `~/night-*` or campaign-out, and used no SSH. I read rulings, code, tests, tracked docs, and the `run_id` lines of the tracked `collection_plan.json`. I edited nothing; the worktree is unchanged.

## Findings

### N1 — HIGH: the standalone thermal desk's `RL145_PRINTS.json` prints every W1 member's rows, non-benign included
- **Path.** `guard_thermal_desk` keeps a prints row when `r.get('id') not in nonbenign` (`joulewise/align/apple/v4_desk_seal.py:1160-1167`). The production builder sets `id` from the manifest item, `{'id': item.get('id'), **row}` (`scripts/align_v4_thermal_desk.py:104`), and `bundle_prints` returns `episode`, never `id` (`joulewise/align/apple/rl145_prints.py:356`).
- **Why it fires.** The repo's own manifest builder writes members without `id` (`scripts/align_v4_w1_synthetic.py:343-344`; also `tests/align/test_thermal_desk.py:376`). So every row has `id: None`, which is not in the non-benign set, and all rows are kept. The file is labelled `population: benign` and `withheld_members` is the digest of an empty list.
- **What leaks, per non-benign member and turn.** `decode_tokens`, `prefill_tokens`, `prefill_s`, `decode_s`, `load_s`, OS-level and PM-state shares (`rl145_prints.py:103-131, 347-350`); `desk_verdict.flags` and `exclusion_reasons` verbatim with suffix text (`:357-359`); G1 release outcomes; `tv1h_trigger.unequal_rows.rows_compared`, which is about one per second of member span (`:296-298`). This re-opens F1, F2 and F3 through this file.
- **Why the tests miss it.** The guard test replaces `rl145_prints_report` with hand-built rows that carry `id = run_id`, and gives the manifest ids (`tests/align/test_v4_desk_release_guard.py:1031-1035, 1049`). No test checks the sealed prints file with the production builder.
- **Fix.** Join on `episode`, and keep a row only when its id is in the benign set (unknown id means withheld). Add a test that runs the real `rl145_prints_report` on a manifest without `id`.

### N2 — MEDIUM: W1 eligibility lists give carved and heat-ended bits per non-benign member
- **Path.** `_seal_residual_rows` skips every scope entry that is not a dict with `residuals` (`v4_desk_seal.py:862-864`). So `scopes[*].eligible_members` and `representatives` (`pilot_analysis.py:270-271`) pass through with non-benign run ids. `_seal_pilot_w1` also passes `episode_scope_alternative_eligible_members` unchanged (`:806`) and keeps the non-benign keys of `..._ineligible_reasons` (`:847-850`). Both are printed (`scripts/align_pilot_session.py:495-498`).
- **Recovery.** The `registered` scope drops a member that is excluded or has `episode.deadman` (`pilot_analysis.py:199-200`). The alternative scope drops deadman, malformed call, G1 and hold timeouts, and an OS level above zero in the episode (`:173-186`). `excluded` is visible, so for ordinals 11 and 14, absence from a list is the carved bit itself.
- **Counting and ordering.** `distinct_trajectories − benign_distinct_trajectories` (`:265`) is the non-benign eligible count per scope, and differences across scopes are a carved count over non-benign members alone. The per-row digests left in `residuals` and `cross_pair_transfer.scores` (`v4_desk_seal.py:870-873`) sit in roster order, so their positions name the members even without the lists.
- **Table.** `w1_pooled_figures.md` files these as "eligibility, not pooled". The alternative scope is not the eligibility in force, so RL-151 C1's rule does not cover it. Today the same deadman bit also shows in `calibration_exclusions` (the known C1(b) gap), but this path survives the truncation rule and the W1 receipt checklist does not name it.
- **Fix.** In W1 filter those lists to benign ids, replace the non-benign rows with one digest (as F4 did), and print the trajectory counts benign-only.

### N3 — MEDIUM: keyed digests are deterministic within a desk, so equality against a known plaintext recovers low-entropy values
`keyed_digest` is HMAC(key, canonical JSON) with no field path or nonce (`v4_desk_seal.py:202-208`).
- **F4 at one bit.** `tool_call_flags.withheld_non_benign` is the digest of `[]` when no non-benign member has a tabulated tool flag (`:634`). The same PILOT always holds a known digest of `[]`: `counts_withheld.tamper_detection_curve`, which is empty by construction (`pilot_analysis.py:248-249`, sealed at `v4_desk_seal.py:874`). Equal digests mean no refused or malformed call among the eight non-benign members.
- **`repeat_token_identity`.** Non-benign cells are digests of one of three values (`:846`). A single-member cell is known `not_evaluated`, and U3 prints token identity in clear, so the mapping is recoverable.
- **Harvest lines, C/T and W1 non-benign.** `seal_line` digests `{'flags': [], 'battery_discharge': None}` identically for every clean member (`:445`). `battery-assist.json` has entries only for assisted members (`joulewise/b5/harvest.py:6356`). A member whose digest differs from the common one, with no visible exclusion or disclosure code, carries assist or another non-excluding harvest flag. This is an F5 residual, and it contradicts the PR body's §4.4 statement that nothing of such a flag is visible.
- **Fix.** Bind the field path and member id into the MAC input, or add a per-digest nonce kept in the withheld archive. Keep the token commitment as the one deliberate equality-preserving digest.

### N4 — MEDIUM: tripwire 1 cannot fire on D's tool path
- **Path.** `tool_path_fires` needs the flag on at least two turns (`v4_desk_seal.py:1037-1042`). On the XML path a refused call returns no calls (`joulewise/align/apple/xml_tool_calls.py:182-186`), and the episode loop breaks on a turn with no tool calls (`joulewise/align/apple/workload.py:652-655`). So `episode.unsupported_tool_call_format` appears at most once per episode, on its last turn. `malformed_tool_call.json` exists only on the 30B path (`workload.py:564-565`).
- **Consequence.** A sabotage-instructed D member whose tool path is broken ends on one refused call and the line reads `within`. Chair ruling 2(d) is not restored for ordinals 11 and 14.
- **Test.** The fixture plants the flag on several turns of one member (`test_v4_desk_release_guard.py:180`), a shape the runner cannot produce on that path.
- **Fix.** The builder followed the ruling's words, so this needs the lead. Suggested form: fire when a non-benign member's episode ends on a refused or malformed call with fewer than three admitted turns, or when both sabotage D members carry the flag.

### N5 — MEDIUM: the standalone thermal desk's scope fails open to W1
- **Path.** Scope comes from the optional manifest `window` tag. With no tag, or one that matches neither pattern, it is `W1` (`v4_desk_seal.py:1140-1142`). `window_scope` for sessions fails closed to C (`:410-418`).
- **Consequence.** A C or T bundle set run with an untagged manifest gets the W1 seal: benign rows whole (turn-owned energy, per-turn observations), U2 to U6 detail, the contrast, and through N1 every prints row.
- **Fix.** Default to C; require an explicit `W1` tag on every member for W1 scope.

### N6 — MEDIUM (outside the diff; same class as F2): harvest-off commands emit member time through file sizes
- `desk --workers auto`, the runbook's production form, prints `sizing.peak_bytes_per_worker` as 8× the largest raw plist, and `largest_plist_bytes` with a sweep (`scripts/align_v4_harvest_off.py:290, 332, 342-343, 403-404`). That is a maximum over a set holding non-benign members (RL-149 §3(c) condition 1).
- `reduce` writes `MANIFEST.json` with each member's `raw_size` and `reduced_size` (`joulewise/align/apple/pm_reduce.py:176-178`). `reduced_size` is a header plus a fixed-size row per sample (`:130-135`), so it gives the sample count. Its stdout prints the window totals (`align_v4_harvest_off.py:493-496`). The runbook calls both "structure-only" (`HARVEST-OFF-MAGISTRATE-RUNBOOK.md:209, 260`).
- **Fix.** Print the worker count only; treat the MANIFEST sizes and `SWEEP.json` as withheld.

### N7 — LOW-MEDIUM: tripwire 2 covers part of what F3 hides, and behaviour codes drive it
- It reads thermal records' `flags` only (`v4_desk_seal.py:1054-1061`). Harvest-catalog flags on a non-excluded member, `energy_flags` and non-meter DC flags are hidden by the same default and not counted.
- The runner emits codes on neither list: `tool_error`, `tool_result_coerced`, `task_scoring_error`, `episode_error`, `episode.g0_unreleased`, `episode.interrupted` (`workload.py:599, 605, 661, 669, 690`). `tool_error` is behaviour. So `withheld members: present` will fire on routine tool errors, is one bit of behaviour by condition, and masks a real new fault.
- **Fix.** Classify those codes; add harvest flag codes and `energy_flags` to the count.

### N8 — LOW: W1 passes `cross_pilot_token_identity` through
With `--compare-session`, non-benign rows print `status`, `first_divergent_turn` and `fields`, including `turn_count` (`align_pilot_session.py:263-265, 493-494`). `_seal_pilot_w1` has no branch for the key; C/T withholds it (`v4_desk_seal.py:782-787`). Fix: withhold non-benign rows.

### N9 — LOW: unguarded import and bundle-path routes
- `align_pilot_session._desk` is the old desk with identity as default (`:303`); only `desk()` checks. Move the stored-identity check inside it.
- `align_v4_u3_export.py r1|pilot` prints `energies_j` for any named bundle (`:94, 114`), and `reduce` writes per-member energy tables. Neither checks the bundle's identity. RL-149 §3 line 4 is the only cover.

### N10 — LOW: W1 seals "if id is in the non-benign set, else print"
An id that fails to join prints whole (`v4_desk_seal.py:604, 629, 737, 747, 1050`). Run ids equal episode ids today, so only N1 is live. Invert to a benign allowlist.

### N11 — LOW: withheld-archive sizes
`size(PILOT.full.json) − size(PILOT.json)` tracks the token-id arrays of the eight non-benign W1 summaries, a pooled figure from a directory listing. It is weaker than the readable file RL-151 §4.3 accepted, but the blind rule says "open", not "list". Timestamps carry only the desk time.

## Answers to the five questions

1. **F1 to F6.**
   - **F1:** closed for the common CLI, explicit `None`, custom policy, and the thermal desk's `PILOT.json` and `THERMAL.md`. Not closed for `RL145_PRINTS.json` in W1 (N1) or the scope default (N5); `_desk` remains (N9).
   - **F2:** closed. Coverage is one span per episode plus one per G0 interval (`thermal_desk.py:156-157`), so the list length is not a turn count. Duration still leaves by N1 and N6.
   - **F3:** closed in the seal. Carved facts still leave by N1 and N2.
   - **F4:** subtraction closed; one bit back through N3.
   - **F5:** list and counts closed; weaker residual through N3.
   - **F6:** dictionary attack closed; equality attack open (N3).
2. **Combination.** Yes: N2 (counting, ordering), N3 (comparison), N6 and N11 (sizes). I found no cross-window intersection.
3. **§3.2.** `s_r_j`, `s_r_df` and `cell_residual_counts` are taken over benign residuals by run id before the digests (`v4_desk_seal.py:868-883`); I found no route for a non-benign residual into them. The rule does not hold everywhere: N2's trajectory counts and N3's digests. The table's `distinct_trajectories` and `episode_scope_alternative_*` rows are wrong as argued in N2, and `cross_pilot_token_identity` is missing.
4. **§3.4.**
   - Tripwire 1: not real for D (N4). Tripwire 2: partial (N7).
   - Confirmation 3: the content holds by grep. `w1_d_g0_cap` reads R1's `deadman_budget` only (`scripts/align_v4_kit.py:614-639, 815-826`), and nothing reads `PILOT.full.json`. The pin checks two signatures and one printed line, so it would not catch a body that starts reading W1 through `root`. That matters only as a regression guard.
   - Confirmation 2: U3 is in memory, as stated. For U4 and E_ref it is confirmed by absence: `v4_desk_evidence` has no in-repo producer and `u4_reference` has no caller, so before release U4 cannot be evaluated from any released table. Since U4-inconclusive carries the R20 extra-sentinel consequence, the lead should say whether that is intended.
5. **Base merge.** No new path in the guard code. It widens N1: prints rows gain `token_events_source` (a deadman marker) and `rows_compared`. `stamp_fresh` adds an unguarded stderr line with no member id. `align_w1_3a_desk.py` has no identity check but reads G0 intervals only.

**Still open as already ruled:** carved codes in per-member `calibration_exclusions`, `exclusion_codes` and `members_excluded` until the truncation rule (C1(b)). I did not check CI.