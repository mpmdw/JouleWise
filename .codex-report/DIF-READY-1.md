# DIF-READY-1: what stands between today and the first DIFFICULTY session

Seat DIF-READY-1, cloud, 2026-10-27. Branch `lane/2026-10-27-difficulty-ready`, cut from origin/main `64ceaa4f`.
No real measurement data was opened, searched or printed. All tests used synthetic fixtures. Nothing was run on the
measurement Mac.

## SUMMARY

**Not ready.** The registered analysis code is ready. On current main it is byte-identical to registration §10, and
its tests pass. What is missing is the collection side, which DIFFICULTY's registration assumes but nobody has built:

1. **The block-6 loop cannot carry a DIFFICULTY session.**
   - A block-6 module must be a 50-run floor or a 40-run contrast (`joulewise/b6/pack_registration.py:94-113` on the
     collection line). DIFFICULTY needs 570 thinking-off and 100 thinking-on per-problem energy attempts, interleaved
     by level.
   - The member runner's fixed-request path forces the full token count: `run_workload` passes `suppress_eos=True`
     (`joulewise/adapters/mlx_runtime.py:445-454`). A DIFFICULTY answer has to stop at EOS or at its cap.
2. **The energy adapter does not exist.** Registration §2 line 55 says it is "built and reviewed separately, before the
   first energy session". It turns a captured run into `energy.csv` rows at rails and wall, with the four physical
   flags.
3. **The bench runner does not exist.** It would make about 5,700 to 6,000 generations without power capture, writing
   the records that `scripts/difficulty_score.py` reads.
4. **Revision 2.4 of the registration is queued but not written.** It covers the wall battery term and the idle-power
   leak (DIFF-1).
5. **The #416 freeze audit of the collection code has not run.** `docs/process/gate_policy.md` amendment item 4 requires
   it once per freeze.

**Earliest feasible dates**, if the build starts 2026-10-28 with parallel seats and each review closes in one fix round:

- **First DIFFICULTY bench session (no power): 2026-11-06.** Bench needs only a small generation runner plus the
  registered scorer. It can fill the Mac right after BYTES closes on 2026-11-05.
- **First DIFFICULTY energy session: about 2026-11-13.** A realistic window is 2026-11-13 to 2026-11-17.
  - 6 to 10 Nov is not feasible for energy. Items 1, 2, 4 and 5 are claim-path work, each needing two cross-family
    executing reviews (gate policy rule 3).
  - Paper 1's writing window (15-22 Nov) wins any conflict for the lead's attention (contingency §7). A slip past
    17 Nov is therefore likely if any review needs a second round.
  - The registered end date, 2027-01-31, leaves ample room. About 14.5 h of thinking-off energy session time, plus
    4B thinking-on, is a small fraction of that window.

## Inventory

Status: DONE, PARTIAL, MISSING, or MAC (only checkable at the desk). "Collection line" means
`work/2026-10-23-by-slots-draft` at `991358f73`, the line the measurement checkout is built from. The block-6 loop is
not on main.

| # | Requirement (source) | Status | Evidence |
|---|---|---|---|
| 1 | Registration committed before any DIFFICULTY energy (§11 item 1) | DONE | v2 `8c47aa656` 2026-10-14 20:10 PDT; 2.1 `5f59fb6d5`; 2.2 `36984a8c8`; 2.3 `fe6d61b4f` 2026-10-15 20:00 PDT (`git log -- docs/registrations/difficulty_pack_v2.md`). No DIFFICULTY energy exists (RUN_STATE item 53: "DIFFICULTY stays December-January"). |
| 2 | Refuter dispositions for v2, 2.1, 2.2 (header, lines 5-7; §4.1) | DONE (record off-repo) | Cited as `refuter-v2/DISPOSITIONS.md`, `refuter-v2.1/DISPOSITIONS.md` and `refuter-v2.2/sol.md` under `/Users/edr/night-archive/difficulty-pack/`, not in git. Commit `36984a8c8` message summarises the 2.1 dispositions. |
| 3 | Gate on revision 2.3 (twin bar 1e-9 → 1e-6) | PARTIAL | `fe6d61b4f` names no refuter. Under gate policy amendment item 2, a change to the twin's agreement bar arguably does not change what is computed, so CI plus a lead line suffices. That lead line is not on record. |
| 4 | Revision 2.4: wall battery term and idle-power leak (DIFF-1; RUN_STATE items 54, 65) | MISSING | Queued text in `docs/process_traces/2026-10-22-forward/DIFF-1-QUEUE.md` on `lane/2026-10-22-difficulty-queue` (`25c5763e5`), not on main. Needs one Sol 6.1 xhigh refuter (gate policy rule 5). See NEEDS_RULING R1, R2. |
| 5 | Registered code bytes (§10, 12 files) | DONE | All 12 SHA-256 match on this branch: `sha256sum -c`, and `tests/test_difficulty_registered_hashes.py`. `joulewise/benchmark_import_math.py` has the registered hash `bdb165fd…` on main and on the collection line. |
| 6 | Appendix A configuration (`274994de…`) | DONE (text); MAC (file copy) | The json block of the registration hashes to `274994de…` (same test). The copy at `/Users/edr/night-archive/difficulty-pack/v2.2-registration/pack_config_difficulty_v2.2.json` can only be checked at the Mac. |
| 7 | Pilot exclusion file `pilot_item_ids.txt` (SHA-256 `5ba18f9a…`, §3.1) | MAC | Appendix A names `/Users/edr/night-archive/pilots/difficulty/pilot_item_ids.txt`. `scripts/difficulty_manifest.py` stops if it is unreadable (contract `docs/contracts/difficulty_tables.md` "Configuration"). |
| 8 | Selections `08d66d9c…` and manifest `22079f59…` (§3.2) | MAC | `/Users/edr/night-archive/difficulty-pack/v2.2-registration/`. A rebuild needs the PRM800K files at `~/jw_data/math-prm800k-7ecc7947/` (`tests/test_difficulty_manifest.py:176-177`). In the cloud `test_S_real_math_manifest_cli` skipped because those files are absent. |
| 9 | Models at the registered revisions (§2) | DONE on record, MAC to confirm | The collection line's `configs/bytes/identity_pins.json` `units` pins `Qwen3-1.7B-4bit@3b1b1768…`, `Qwen3-4B-4bit@4dcb3d10…` and `Qwen3-8B-4bit@545dc425…` under `/Users/edr/.cache/huggingface/hub/…/snapshots/<rev>`. These are exactly DIFFICULTY's revisions. Weights are 968,080,210, 2,263,022,529 and 4,607,835,174 bytes (`model_artifact_inventory`). BYTES uses them, so no download is needed while they are kept. Registration §2 names the location `/Users/edr/jw_models/mlx-community/`; BYTES's location is the HF cache. Either is fine if the revision matches. |
| 10 | Pack code merged with current main | DONE | Merge `7e530bf15`: no conflicts, because every pack file is new. |
| 11 | Pack tests pass | DONE | 4 modules, 56 tests, 1 skip, under CPython 3.13.17 and 3.11.17 (below). One cross-platform test failure was fixed in `817572d50`. |
| 12 | Twin (§10) | DONE (code); real-table agreement is post-collection | `scripts/difficulty_twin.py` hash matches. `tests/test_difficulty_twin_agreement.py` passes on synthetic data. Agreement on real tables comes before unblinding. |
| 13 | Pack registration in the loop (`configs/b6/packs/<id>/registration.json`) | MISSING | None exists on any branch (`grep -ri difficulty` over `joulewise scripts configs` of the collection line finds only the MATH importer and suite schema). |
| 14 | Module shape for per-problem attempts | MISSING (design) | `pack_registration.py:94-113` allows only floor (50) or contrast (40). A new module kind such as `attempts` changes `pack_registration`, `compose`, `queue` sizing and `plan_inputs`. NEEDS_RULING R3. |
| 15 | Member that generates a MATH prompt greedily and stops at EOS or cap | MISSING | Fixed-request path: `mlx_runtime.py:445-454` (`suppress_eos=True`). Usable pieces: `WorkloadProfile.prompt_text` (`joulewise/schemas.py:936,961`); raw encoding (`mlx_runtime.py` `_prompt_for_workload`), so the chat template must be pre-rendered; the suite path records `response_text`/`stop_reason` and suppresses EOS only under `fixed_budget_exact` (`mlx_runtime.py:632-704`). Note that `mlx_runtime.py`, `controller.py`, `suite.py` and `run_campaign.py` are in `configs/b6/registration/acceptance.json` `number_bearing_paths`. Changing them after `registered_commit` raises `code.number_bearing_unreviewed` (EXCLUDE_WINDOW) unless reviewed. |
| 16 | Energy adapter → `energy.csv` (§2, §5.1) | MISSING | Must write the registered ten columns. The twin rejects any other header (DIFF-1 decision 1, `scripts/difficulty_twin.py` `read_table`). It must also write `wall_battery.csv` (R1) and map block-6 hazard codes to `agent_overlap`, `sleep`, `contention_above_level` and `idle_wait_cap` (R4). The block-6 exporter writes no generated text (`joulewise/b6/export_runs.py:24-43`), so energy rows need their tokens from the run bundle (`response.txt`, `tokens.jsonl`). |
| 17 | Bench runner (no power) → generation records for `scripts/difficulty_score.py` | MISSING | Required fields are read by `joulewise/packs/difficulty/score.py:46-88`: `model, mode, item_id, attempt, response_text, finish_reason` (stop/length/error), `prompt_tokens, generated_tokens, generated_token_ids, flags`. Machine time is about 13.0 h thinking-off plus 3.8 h for 4B thinking-on (§4.3), and 5.6 h more if 8B thinking-on runs. |
| 18 | Blinding (§9: pack factor U(0.8,1.25), configuration factor U(0.97,1.03)) | PARTIAL | The ranges match `joulewise/b6/blinding.py:16-17`. However `FIT_MODELS` (`blinding.py:139-144`) is exactly DIFFICULTY's three models, and BYTES's group logic releases "fit" rows. A DIFFICULTY `blinding_group` needs its own stage rule, plus R2's idle withholding (`export_runs.py` still writes `idle_power_w`). |
| 19 | Precheck/desk integration | PARTIAL | Generic: model-file hash check against `identity_pins.json` `units` (`precheck.py:213-244`), battery, thermal, agents, clock, disk, and desk harvest/acceptance (`desk_lane.py:185-262`). Pack-specific and missing: a `sizing_b5.json` row (`plan_inputs.py:85-88` raises without one); the disk and smoke terms are hard-coded to the `bytes-s` prefix (`precheck.py:79-95`, `plan_inputs.py:119`); a `smoke_keep.json` entry; a `loop_difficulty.json` with its own `loop_root` and `pack_ids`. |
| 20 | Contention level in force (§5.1, §12 item 7) | MAC/record | The adapter must write the level it used into each session record. Find the value from block-6 §13 decision 2 at the desk. |
| 21 | Harvest → tables | PARTIAL | `scripts/difficulty_score.py` and `scripts/difficulty_estimate.py` are registered and tested. The step from block-6 harvest to `bench.csv`/`energy.csv` is the adapter (item 16). |
| 22 | Collection-code freeze audit (#416, once per freeze; contingency §7 item 2) | MISSING | Runs after items 13-19 are frozen. |
| 23 | Governed estimator files byte-identical | DONE | `powermetrics_fiducial.py` `bcdfeec0…`, `reduce.py` `7b9c0d28…`, `uncertainty_evidence.py` `b583f35a…`, `adapters/powermetrics.py` `70f47086…`: equal on main, on the collection line, on this branch and on the trial merge below. |

## CHANGES

On `lane/2026-10-27-difficulty-ready`, pushed:

| Commit | What |
|---|---|
| `7e530bf15` | Merge of `lane/2026-10-14-difficulty-pack` (`281a06043`) into main `64ceaa4f`. No conflicts; all 12 registered hashes intact. |
| `817572d50` | Tests only: the two test modules from `fix/2026-10-22-audit-difficulty` (`ae8c8509c`), which use revision 2.3's 1e-6 bar. On Linux x86-64, `NormalDist().inv_cdf(0.975)` is `0x1.f5c0331eeff82p+0`, one ulp from the value that makes `wilson(0, 20)[1]` exactly 0. The old exact `== 0` check therefore failed with 1.39e-17. That branch's comment-only edits to `estimators.py` and `difficulty_twin.py` were **not** taken, because they change two registered hashes (`425a7123…` and `a9537adc…`, against registered `14c657f2…` and `4ec1b833…`). See R5. |
| `5daf182a3` | `tests/test_difficulty_registered_hashes.py` parses §10's twelve rows and appendix A and checks the tree. Counterfactuals: one appended byte in `score.py` fails it, and so does the audit branch's `estimators.py`. |

**Loop integration was not committed.** Nothing minimal makes the pack arm in the current loop. The module schema,
the runner's EOS rule and the adapter are all number-bearing or claim-path changes that need a ruling first (R3) and
two executing reviews. A placeholder draft pack would also fail `validate()` on its module counts, which apply to drafts
too, and would break `tests/test_b6_loop.py:148-175` and `tests/test_bytes_plan_trees.py:24-28`.

**Trial merge.** The collection line merges cleanly into this branch: local scratch merge of
`work/2026-10-23-by-slots-draft` (`991358f73`), not pushed. The integration lane for items 13-19 should start from that
line, or from the measurement checkout's head, and take this branch's three commits. They touch only new files and
tests.

## Tests run (synthetic only)

| Tree | Modules | Result |
|---|---|---|
| this branch, CPython 3.13.17 | `test_difficulty_manifest`, `test_difficulty_score`, `test_difficulty_estimators`, `test_difficulty_twin_agreement` | 56 tests, OK, 1 skipped (`test_S_real_math_manifest_cli`: real MATH files absent) |
| this branch, CPython 3.11.17 | same four | 56 tests, OK, 1 skipped |
| this branch, before `817572d50` | same four | 56 tests, 1 failure (`test_A_wilson`, platform ulp, above) |
| this branch | `test_difficulty_registered_hashes` | 2 tests, OK |
| trial merge with the collection line | `test_b6_loop`, `test_b6_queue`, `test_b6_registration`, `test_pack_stopping`, `b6.test_precheck`, `b6.test_model_files`, `b6.test_plan_inputs`, `test_b6_compose` | 158 tests, 2 errors |
| collection line alone (baseline) | same eight | 158 tests, the same 2 errors |

The 2 errors are `test_done_guard_skips_tick_and_resume_invalidates` and
`test_guard_skip_pass_terminal_and_overrun_plist_and_cli_override`. Both fail with
`FileNotFoundError: '/bin/zsh'`, because this container has no zsh. The DIFFICULTY merge adds no failure.

## NEEDS_RULING

The registration was not edited. Proposed text follows for each item.

**R1. Wall adds the battery term (revision 2.4).** Ruled for DIFFICULTY by BAT-RULING §6 (two blind seats and a cold
Fable judge, all agreeing), but not yet in the registration. Proposed text, from DIFF-1-QUEUE.md `25c5763e5`,
unchanged:

- Replace §2's `wall` bullet with:
  > - `wall`: the whole machine: the energy on the laptop's USB-C charging cable from a USB-C power meter, plus the energy the battery supplied over the same request, read from the battery current and voltage that the laptop reports with each meter reading (charging counts negative). It is printed beside rails as a labelled line, with the battery's share as its own column. Runs where the battery helped carry the flag `battery_assist` (recorded, not excluding).
- Append to the adapter paragraph: the text of DIFF-1-QUEUE.md lines 63-78. It defines P_b = −B0AC × B0AV / 10⁶ W, the term (T / n) × Σ P_b, and the side table `wall_battery.csv` with columns `model, mode, level, item_id, attempt, meter_j, battery_j, battery_v_end_j, battery_end_window_complete`, blinded like `energy_j`. It also defines the flag `battery_unmeasured` (recorded, not excluding).
- Add §12 item 11:
  > `wall` adds the battery term over the request, gross and signed. The meter and battery parts, and the battery energy reported in the τ after the request, go to a side table. A missing battery reading is a recorded flag (BAT-2 ruling §6; DIFF-1).

**R2. No idle quantity is visible before release (revision 2.4).** Proposed text, DIFF-1-QUEUE.md lines 225-233,
appended to §9 after "unblinding divides the factors out once.":

> Before release, no table outside the withheld store carries a per-run idle quantity on either boundary: not the idle baseline's mean power or its variance, not an idle-subtracted energy, and not the meter's idle power. The machine's idle power does not depend on which configuration is loaded, so its blinded value in two configurations would give the ratio of their factors. Gross minus idle-subtracted energy is the idle power times the request's duration, and durations are not blinded. These columns are written, already multiplied by the factors, to the withheld store and released with the factors. The energies visible before release are `energy_j` in `energy.csv` and `meter_j`, `battery_j` and `battery_v_end_j` in the `wall` side table (section 2).

Also add §12 item 12:

> No per-run idle quantity is visible before release. The idle columns go to the withheld store, because the machine's idle power reads the configuration factors (4b350f47 record; DIFF-1).

**R3. How energy attempts sit in block-6 sessions.** This is a science-design fork for the lead (gate policy rule 6:
one seat per family if a council is wanted). §9 says "Energy attempts run inside the collection design's sessions,
each with its own idle baseline", but block-6 sessions are built from 50- or 40-run modules. Proposed text, appended
to §9 "Collection":

> A DIFFICULTY session is a block-6 session (calibration captures, reference corpus of 12 verified clean members, and references at the registered cadence) whose science stages are **attempt modules**: ordered lists of energy attempts, each one problem of a registered energy subset generated once by one configuration, greedy, stopping at the end-of-sequence token or the output cap, with its own idle baseline before it. Within a module the three thinking-off configurations' attempts on one level alternate in a fixed rotation (1.7B, 4B, 8B), and the order of problems within a level is the energy-subset order of section 3.2; thinking-on attempts form their own modules. Module length is set so that a session's science fits the collection design's science-minute limit; the collection plan records the exact order. A re-measured attempt (section 5.2) is appended to a later module of the same configuration.

The lead must also decide the gate level for the runner's EOS change in `mlx_runtime.py` or a new runner. Because the
file is on `number_bearing_paths`, this rides rule 3.

**R4. Mapping block-6 hazard codes to DIFFICULTY's four physical flags.** This is an exclusion rule, so §5.1 and lead
judgement apply. §5.1 names `agent_overlap`, `sleep`, `contention_above_level` and `idle_wait_cap`. The block-6
catalog uses codes such as `agent.presence_overlap`, `agent.unit_overlap`, `contention.request_overlap` and the sleep
guard's codes. Proposed text, appended to §5.1 after "The estimator only maps flag names.":

> The energy adapter writes `agent_overlap` for any block-6 member code whose catalog effect is `EXCLUDE_MEMBER` in the `agent.` family; `sleep` for any sleep-guard code that marks the run's span as slept; `contention_above_level` for `contention.request_overlap` at or above the level; `idle_wait_cap` when the idle wait reached its 1,500 s limit. Every other block-6 code is copied as a recorded adapter flag. The mapping table is committed with the adapter before the first energy session.

**R5. The audit branch's comments.** `fix/2026-10-22-audit-difficulty` adds comments only (AST-identical), but moves two
registered SHA-256s. Recommended: do not merge those two file edits. The test-bar change is already taken. If the
comments are wanted, revision 2.4 would re-register both hashes.

**R6. Small text corrections, no change to what is computed.**

- (a) The line-5 header says draft `8c47aa656` was "never on main", but it is in main's history (`git log` above).
  Proposed: "(commit `8c47aa656`, superseded the same day)".
- (b) The "registered design" table in `docs/contracts/difficulty_tables.md` still shows the v2 draft sizes (200 bench,
  20/20/40/40/40 energy). That file is a registered hash, so leave it, and add to §10:
  > The table contract's size table is the draft's; appendix A's configuration is the registered design.
- (c) If bench attempts run on the Air (pipeline audit `segments.json:478`), §2's "One Apple M3 Max laptop" needs:
  > Bench attempts may be generated on another Apple-silicon machine with the same MLX and mlx-lm versions; energy attempts only on the M3 Max.

  Recommended: keep the bench on the Mac, which needs no ruling.

**R7. mlx-lm version.** The registration fixes revisions and greedy decoding but no mlx-lm version. BYTES runs mlx-lm
0.31.3 (RUN_STATE item 66). Proposed §2 addition:

> The runtime is the measurement checkout's pinned MLX and mlx-lm (mlx-lm 0.31.3 at registration of revision 2.4), recorded in every session's identity pins; a change of runtime version is a new configuration.

## Proposed order of work (cloud)

1. **Revision 2.4 text (R1, R2, R3, R4, R6, R7).** One Sol 6.1 xhigh refuter and a lead line. About 1 day.
2. **In parallel:**
   - (a) **Bench runner**, collection tooling with no power. It writes generation records with token ids, using the
     registered chat template `math_levels_v1/qwen3_chat_boxed_v1`. Its regression test should score synthetic
     records through `scripts/difficulty_score.py`. Gate: rule 2, with one reviewer recommended.
   - (b) **Attempt module and generator.** Covers the pack registration, `loop_difficulty.json`, the sizing row,
     `smoke_keep`, the identity pins (reusing BYTES's three `units`), EOS-stopping members and the plan-tree sidecars.
   - (c) **Energy adapter.** Covers `energy.csv`, `wall_battery.csv`, the flag mapping, the DIFFICULTY blinding stage
     rule and idle withholding.
   - (b) and (c) take rule 3: two executing reviews launched together.
3. **#416 freeze audit, smoke, first energy session.**

## Mac-side checklist (Ed or the measurement-Mac orchestrator, at a SESSION_DESK, never while `collection.active` exists)

1. **Models.** Confirm the three snapshots are present and complete:
   `ls ~/.cache/huggingface/hub/models--mlx-community--Qwen3-{1.7B,4B,8B}-4bit/snapshots/` should show `3b1b1768…`,
   `4dcb3d10…` and `545dc425…`.
   - The precheck's model-file hash compares against `configs/b6/registration/identity_pins.json`.
   - Weights total 7.84 GB (0.97 + 2.26 + 4.61). These are BYTES models, so no download is expected.
   - Do not delete them when BYTES closes (RUN_STATE: never delete a model an open study names).
   - If any is missing, run `hf download mlx-community/Qwen3-<size>-4bit --revision <rev>`, about 7.9 GB in all.
2. **Disk.** Run `df -g /Users/edr`.
   - The models are already counted.
   - Per energy session, expect BYTES-like capture volume. The sizing row from item 2(b) will state the bytes; until
     then keep at least the free space BYTES sessions needed (about 130 GB was free on 10-25, item 70).
   - Bench output is text only, under 1 GB.
3. **Registration objects.** Check `shasum -a 256` on:
   - `/Users/edr/night-archive/pilots/difficulty/pilot_item_ids.txt` = `5ba18f9a…99bf88`;
   - `…/difficulty-pack/v2.2-registration/pack_config_difficulty_v2.2.json` = `274994de…d7dd`;
   - `selections-difficulty-v2.2.json` = `08d66d9c…56e3`;
   - `manifest-difficulty-v2.2.json` = `22079f59…82f9`.
4. **MATH sources.** Confirm `~/jw_data/math-prm800k-7ecc7947/` holds `prm_test.jsonl`, `prm_train.jsonl`,
   `ptr_test.txt`, `ptr_train.txt` and `prm_LICENSE`. Then run
   `python3.13 -m unittest tests.test_difficulty_manifest` on this branch. `test_S` should run instead of skipping.
   Optionally rebuild the manifest with `scripts/difficulty_manifest.py` to a path outside the repository, and compare
   its hash with item 3's.
5. **Python.** `/opt/homebrew/bin/python3.13 --version`: the registration names CPython 3.13.1. Run the four pack
   modules plus `tests.test_difficulty_registered_hashes` there.
6. **Contention level.** Record the value in force from block-6 §13 decision 2, for the adapter's session record
   (§5.1).
7. **Agent rule.** No agent process during any DIFFICULTY session (RUN_STATE item 80 (1)), and close the Codex app
   daemon.
