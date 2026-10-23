# BY-PREP-P — what BYTES pass 1 needs before prepare

Report-only Sol 6.1 Cloud seat, 2026-10-23. Source lane: lane/2026-10-22-bytes-pass1 at **1c458d71d8a048e24b6c3a6b402fe3c34d9f57c3**. Delivery branch: **report/2026-10-22-by-prep-p**. No code, registration, source evidence, Mac state, PR, or other branch was changed.

**Finding:** add six pack-specific sizing rows to **configs/b6/registration/sizing_b5.json**, with positive programmed_span_s and T_stream_max_s and a valid nested disk_derivation whose P is reconstructed exactly. Today this file contains only ALPHA, BETA and GAMMA; there are zero bytes-s rows. The existing H desk evidence supports all six draft P values without another Mac run. Its time candidates remain qualified: the soak-derived margin is incomplete, and the measured fixed time omits verdict/backup. These are draft registration inputs, not permission to arm.

The executable generation recipe is [by-prep-p/commands.md](by-prep-p/commands.md). Each row's full draft, exact fractions, native encoding and limitations are in [by-prep-p/sizing_b5.draft.json](by-prep-p/sizing_b5.draft.json). Neither artifact changes the real registration.

## Governing texts and the exact prepare contract

| Authority or consumer | What it determines |
|---|---|
| docs/process_traces/2026-10-21-magistrate-283e9802/H-DISK-RULING.md, items 1–7 and addendum 1 | P = c(B+WAIT)+fixed; maximum of two summed bases; stream-rate WAIT; committed fixed; c=2; no reserve; native budget exactly P. The original ruling governs H, with item 7 sending the same form to J/C5 for each BYTES pass shape. |
| .codex-report/BY-C5.md, P PER SUB-PACK, PACK ENCODING, R6 and WHICH TEXT WINS; .codex-report/BY-C5-fix1.md, A1/A2/A4 and R2-3 dispositions | C5 adopts that form for BYTES. Raw allocated bytes alone supply rates. Committed H fixed bytes supersede the stopped session's partial measured fixed. Per-model allowance form stays as implemented; a changed registered form requires a new P. Missing/malformed registered P deliberately holds prepare. |
| .codex-report/bytes-pass1-merge.md, cross-lane conflict and real-run implication | Missing P in the rehearsal produced HOLD_LOOP lane_missing:driver:disk.budget_missing. Fixture-only P repaired the rehearsal; it did not register production rows. The director's LEDGER line 111 is referenced there; that separate ledger is not tracked in this base. The adopted R2-3 disposition is preserved in the two C5 reports and the production driver comment. |
| joulewise/b6/registration.py: load_sizing; joulewise/b6/plan_inputs.py: build, sizing_label, valid_disk_terms, encode_disk_budget | The actual sizing file and row fields, identity lookup, exact integer validation and native encoding. |
| joulewise/b6/driver_lane.py: prepare_session | Uses measurement/configs/b6/registration, collects real desk identities, builds inputs, and returns LaneMissing before prepared.json/plan metadata when required_free_bytes is null. |
| docs/design/bytes_pack_design.md, R6/R8 and addenda 5–6; docs/registrations/bytes_pack_v1.md, §§5, 18–19 | Six sub-packs per pass; all six pass-1 t0 values must precede 2026-11-02T00:00:00-08:00 (= 2026-11-02T08:00:00Z). Fixed packs bypass the modular 265-minute science cap. Registration slots, cold gate and first-session smoke remain. |

A sizing row is selected by **row.pack_id == exact campaign id**. The dictionary key can be a label; using the same pack id as the key avoids an unnecessary second naming scheme. For pass 1 the six recommended pointers are:

- /packs/bytes-s1-p1
- /packs/bytes-s2-p1
- /packs/bytes-s3-p1
- /packs/bytes-s4-p1
- /packs/bytes-s5-p1
- /packs/bytes-s6-p1

All are in configs/b6/registration/sizing_b5.json, schema_version joulewise.b5_sizing.v1. Keep the three replication rows. The six p2 rows are needed before their own sessions; they have reversed order and the same counts under today's trees, so their current numerical candidates equal p1. They are not a prerequisite to a minimum one-pass result.

**Minimum row contract:**

~~~json
{
  "pack_id": "bytes-s1-p1",
  "programmed_span_s": "<finite positive number from the sizing derivation>",
  "T_stream_max_s": "<finite positive measured stream bound>",
  "disk_derivation": {
    "B_bytes": "<nonnegative JSON integer>",
    "extra_wait_raw_bytes": "<nonnegative JSON integer>",
    "fixed_retained_bytes": "<nonnegative JSON integer>",
    "peak_copies": 2,
    "session_wait_budget_s": 7200,
    "required_free_bytes": "<integer exactly 2*(B_bytes+extra_wait_raw_bytes)+fixed_retained_bytes>"
  }
}
~~~

The quoted placeholders above describe types; the draft JSON has actual numbers. A standalone top-level P, H's bytes-mac-check row, module planning minutes in pack registration, or a C5 output file beside the checkout does not satisfy this consumer. P is the required free space in **bytes**, not just B. No reserve is added.

There are two distinct missing-input states. With zero sizing rows, build() raises "pack has no registered sizing: <pack>". With a time row present but absent/inconsistent disk_derivation, encode_disk_budget records disk.budget_missing and DriverLane returns the deliberate R2-3 LaneMissing. Supplying a valid registered row remedies both. The current registry test loops over existing bytes-s rows, so its "0 checked" is vacuous success, not registration completeness.

**Prepared is not launched.** DriverLane.prepare_session writes inputs/metadata; launch later invokes the native writer. These rows solve the sizing/P input seam. Pack status, bindings, authenticated ledger and science registration still govern an actual launch.

## P, its inputs and each row's derivation

For timed H members i, let a_i be **one raw bundle's inode-deduplicated allocated bytes**, POSIX st_blocks×512; s_i its paired pre_spawn/post_parse sampler span; w_i its member-wall span. Then:

- r_s = max(a_i/s_i), r_w = max(a_i/w_i), over all available timed raw members, including references/scaffold.
- m = max(max request / min request − 1) over succeeded check/soak groups. Current C5 uses the groups it has and labels incompleteness; it does not silently discard a completed planning observation because it is flagged.
- Per model j: u_j = (mean request_j + max(stream_j − request_j))×(1+m), v_j = mean member_wall_j×(1+m). The reference uses its own timed members. The reference spread does not independently enlarge m.
- B_s = ceil(r_s×Σ n_j u_j); B_w = ceil(r_w×Σ n_j v_j); B=max(B_s,B_w). Sum first, then ceiling once per whole basis, then maximum. Do not sum per-model maxima.
- WAIT=ceil(r_s×7200); **P=2(B+WAIT)+fixed**. Use exact rational arithmetic from the stored decimal lexemes.

The sources already exist:

- mpmdw/JouleWise-data, branch analysis/bytes-h-desk-20261022, pinned **8db1b40d64d8c543e7a9bee4fd9ced0da63d4b0b**, directory bytes-h-desk-20261022.
- MEASUREMENTS.json and export/bytes-h-20261021T185555335572Z-calibration.{runs.csv,session.json}.
- tables/indep_runs.json contains raw_bytes per run. scripts/indep_measure.py defines and measures that field over the raw tree. Join by run id and verify the already-recorded timings. Never halve retained_bytes.
- tables/disk_h.json contains the independent rate/copy disclosure. Its rounded per-model maximum rates alone cannot reproduce the exact integer P; use the per-run receipts.
- Current pass plan_tree.json science/stage_graph entries supply model counts, reference counts and collection counts. Counts come from these trees, not from model parameter counts or resident bytes in the manifest.

I independently recomputed using the original decimal lexemes and integer rational arithmetic. The common current inputs are:

| Input | Value and derivation |
|---|---|
| Margin m | 135722362995148 / 4081589090824127 = approximately 0.03325233382759357, the current incomplete 70B soak request max/min−1. |
| r_s | 1608417280000000000000 / 890824130839901 B/s, approximately 1,805,538.5168827055. Maximum one-copy raw_bytes/stream_s from the joined receipts. |
| r_w | 16084172800000000000000 / 12509476685523987 B/s, approximately 1,285,759.0452694688. Maximum one-copy raw_bytes/member_wall_s. Decimal displays are not arithmetic inputs. |
| WAIT | 12,999,877,322 B = ceil(r_s×7200 s), the sealed session WAIT budget. |
| fixed | 4,046,531,103 B from configs/campaigns/bytes_mac_check/registration/sizing_b5.json#/packs/bytes-mac-check/disk_derivation/fixed_retained_bytes. The committed H derivation scales the observed 1,438,707,712 fixed bytes by max(1,45120/16042.009888648987), ceiling upward. C5's later ruling uses this committed integer unchanged for every pass. The partial H measured 1,266,544,640 B is disclosure only. |
| c | 2, raw plus partitioned rsync backups; the APFS clone archive adds no physical copy under the ruling. H's observed implied c=0.8020750916018277 remains disclosure, with no substitution into P. |
| Native encoding | n is the real tree's member count, no spares. q=floor(2B/(3n)); headroom=(2B−3nq)+2WAIT+fixed. Then 3nq+headroom=P exactly. q is an encoding in the existing native three-target interface; the writer requires q>0, which every draft satisfies. |

Each two-model pack has 50 members per model plus 25 references (18 corpus+3 start+1 midpoint+3 end), n=125. Each single-model pack has 50+25=75. Collection count is 10 and 7 respectively. The 18 corpus slots are budgeted even though collection can stop after 12 valid references.

Per-model disk allowances (seconds; exact fractions in the draft JSON):

| Pack | Model | Count | Stream allowance s | Member-wall allowance s |
|---|---|---:|---:|---:|
| bytes-s1-p1 | qwen3-1p7b | 50 | 95.936319909 | 133.421011685 |
| bytes-s1-p1 | qwen3-4b | 50 | 99.592648098 | 138.716749210 |
| bytes-s1-p1 | reference | 25 | 93.759871868 | 130.734032387 |
| bytes-s2-p1 | qwen3-8b | 50 | 105.675267598 | 146.138676197 |
| bytes-s2-p1 | qwen3-30b-a3b | 50 | 100.460336724 | 145.758197295 |
| bytes-s2-p1 | reference | 25 | 93.759871868 | 130.734032387 |
| bytes-s3-p1 | qwen3-14b | 50 | 115.960714413 | 158.620031792 |
| bytes-s3-p1 | qwen3-next-80b | 50 | 103.600245103 | 160.362644347 |
| bytes-s3-p1 | reference | 25 | 93.759871868 | 130.734032387 |
| bytes-s4-p1 | qwen3-32b | 50 | 147.706179398 | 199.223982318 |
| bytes-s4-p1 | qwen3-8b-8bit | 50 | 110.556092239 | 153.147274265 |
| bytes-s4-p1 | reference | 25 | 93.759871868 | 130.734032387 |
| bytes-s5-p1 | llama-70b | 50 | 206.799102208 | 272.192316153 |
| bytes-s5-p1 | reference | 25 | 93.759871868 | 130.734032387 |
| bytes-s6-p1 | qwen35-122b | 50 | 114.679302444 | 189.463644769 |
| bytes-s6-p1 | reference | 25 | 93.759871868 | 130.734032387 |

The displayed seconds are rounded to nine decimal places; the draft JSON retains exact numerator/denominator pairs. Per-row sums of these counts and unrounded allowances give:

| Pack | B_s bytes | B_w bytes | B bytes | P bytes | q bytes/member | Native headroom bytes | Smoke share bytes |
|---|---:|---:|---:|---:|---:|---:|---:|
| bytes-s1-p1 | 21,883,930,645 | 21,697,490,999 | 21,883,930,645 | 73,814,147,037 | 116,714,296 | 30,046,286,037 | 1,400,571,562 |
| bytes-s2-p1 | 22,841,465,166 | 22,967,763,886 | 22,967,763,886 | 75,981,813,519 | 122,494,740 | 30,046,286,019 | 1,469,936,889 |
| bytes-s3-p1 | 24,053,464,961 | 24,709,054,674 | 24,709,054,674 | 79,464,395,095 | 131,781,624 | 30,046,286,095 | 1,581,379,500 |
| bytes-s4-p1 | 27,547,300,445 | 26,855,538,139 | 27,547,300,445 | 85,140,886,637 | 146,918,935 | 30,046,286,012 | 1,763,027,229 |
| bytes-s5-p1 | 22,901,363,715 | 21,700,998,244 | 22,901,363,715 | 75,849,013,177 | 203,567,677 | 30,046,285,852 | 1,832,109,098 |
| bytes-s6-p1 | 14,585,071,383 | 16,382,541,368 | 16,382,541,368 | 62,811,368,483 | 145,622,589 | 30,046,285,958 | 1,310,603,310 |

The last column is the retained smoke-member share ceil(2B×m_smoke/n), with m_smoke=4 for s1–s4 and 3 for s5–s6, from configs/b6/smoke_keep.json. PRECHECK uses P alone when no smoke is due, and P+that share when smoke is due. Native arm subsequently measures free space against P. Smoke fixed files are excluded from this share; BY-C5 discloses that this can waste a smoke before a later full-session disk refusal. Do not add WAIT/fixed a second time or weaken the arm bar.

All six P integers and q/headroom identities exactly match .codex-report/BY-C5.md and BY-C5-fix1.md. I did not reconstruct fractions from the rounded allowance table in those reports.

## Time rows and what remains unmeasured

C5's time formula, with c_col the collection count, is:

S = [Σ_models 50×mean(member_wall_j) + 25×mean(reference wall)]×(1+m)
    + (c_col+1)×SETTLE_S + c_col×collection_stage_overhead_s + fixed_desk_s.

Here SETTLE_S=60 comes from joulewise/b5/chain.py. BY-0's tables/fixed_inputs.json supplies collection_stage_overhead_s=44.44705606997013, the mean of 16 completed collection-stage spans minus their member-wall unions. Its fixed_desk_s=1185 comes from H's reservation/pre-calibration/bound derivation and the prior block-6 median post-calibration; **it is explicitly a lower bound because verdict/backup were not timed**.

With that lower bound inserted into a separate copy of the measurements, the current source arithmetic gives:

| Pack | Pass-1 module order | Planned members | Collections | Draft S seconds, lower bound | T_stream_max_s |
|---|---|---:|---:|---:|---:|
| bytes-s1-p1 | qwen3-1p7b + qwen3-4b | 125 | 10 | 19164.709415 | 96.390694042 |
| bytes-s2-p1 | qwen3-8b + qwen3-30b-a3b | 125 | 10 | 20152.665045 | 102.247239625 |
| bytes-s3-p1 | qwen3-14b + qwen3-next-80b | 125 | 10 | 21506.955177 | 112.229906125 |
| bytes-s4-p1 | qwen3-32b + qwen3-8b-8bit | 125 | 10 | 23176.384200 | 142.944862875 |
| bytes-s5-p1 | llama-70b | 75 | 7 | 18854.096010 | 201.498298959 |
| bytes-s6-p1 | qwen35-122b | 75 | 7 | 14717.662441 | 111.030780958 |

T_stream_max_s is the maximum measured per-run paired sampler span for the pack's models (test-7 workloads included) and the references. It is separate from the mean-plus-overhead disk allowance. C5's clock bar is 5000/T_stream_max_s−0.25 ppm: the existing 5 ms budget, h=0, and registered 0.25 ppm margin. The tightest current row is s5, approximately 24.56410526 ppm, derived from 201.49829895899165 s. The live measured rate/word is checked on the actual Mac later.

The native window duration is separately ceil-to-minute(ceil(S)+3300+7200+7200), using the writer's T0, pause and WAIT constants. This is a maximum planning duration, not the measured elapsed time. The full-precision draft values and resulting maxima are in the JSON.

**Important qualification:** the frozen original MEASUREMENTS.json has both sizing receipts null, so current C5 on it produces null programmed_span_s. It still derives disk terms after raw-byte augmentation. The numeric S values above are the BY-0 lower-bound scenario, not a newly complete measurement and not final allowances. The recipe creates distinct raw-only and sizing-draft outputs to keep that distinction reviewable.

## Inputs: agent work now versus measurement

| Item | Existing input or required observation | Work possible while windows are paused |
|---|---|---|
| Six P derivations, counts, q/headroom, clock candidates | H timings plus independent raw-byte receipts, committed H fixed bytes, six trees | **Agent-doable now**, on Cloud from frozen desk exports. No model load, inference, capture or new measurement is required. |
| Six draft spans and module est_minutes | Same H timings and measured spread; BY-0 fixed-time table | **Agent-doable now as qualified drafts.** Update modules[].est_minutes in pack drafts for accurate planning; those values are not the sizing-row S. |
| Full soak margin / stable long-regime evidence | 70B soak 11/12 succeeded, 7 kept after exclusions; 122B soak 0/12 | **Needs a quiet-Mac remainder** if complete soak evidence is required. This cannot be supplied by the manifest, a second desk run or fabricated timing. Current C5 marks incompleteness; it is not itself a new physical refusal. |
| Complete fixed_desk_s | Verdict and backup timings absent from H and the archived chain journals BY-0 inspected | **Needs an authentic existing timing receipt or a newly timed run.** Searching archived records is agent work; if none exists, collecting it is measurement. The lower bound must remain labelled. |
| Registered allowance policy | Existing C5 form includes flagged completed planning runs and the incomplete margin | Preserve that form in drafts. Replacing it with a clean-only/checks-only margin or a different per-model overhead changes P and needs the lead's registration decision; do not quietly make that change to meet a date. |
| Manifest and C4 file pins | configs/bytes/bytes_manifest.json, configs/bytes/identity_pins.json; BY-G re-derivation | **Agent-doable now**: bind existing pins to final tree bytes, populate prose slots and verify config/model identity links. The manifest contains W/KV/R, revisions and identities; it contains no measured wall time, sampler duration, raw-byte rate, fixed time or session free space. |
| Actual file/runtime identity on this Mac | Local model files and chosen measurement interpreter | Read-only hash/version checks are **agent-doable on the Mac while paused**. Cloud cannot attest that the Mac's current files/stack still match. Existing BY-G file hashes do not assert an executed runtime stack. |
| Current disk availability | statvfs on actual planned session volume, excluding purgeable | **Agent-doable read-only on the Mac**, then measured again by arm. Historical 53 GiB in BY-C5-fix1 is not today's receipt. Do not use Cloud disk free or delete evidence from this report seat. |
| F_min, contention coefficient/resolution, T_phase/T10 | Measured floor/CPU receipts and a complete bracket, if not already archived | Desk derivation is agent work once authentic raw inputs exist; missing physical inputs need their owning measurement. These are separate C5/registration slots, not terms of P. Absent T10/T_phase follows the existing flag-only policy; never borrow ALPHA/GAMMA's line. |
| Test 7 and known-bytes probe | H test-7 ends absent; probe receipt required by registration | An existing receipt can be read now. A missing experiment needs its own lead-controlled Mac run. Absent passed test 7 retains the already-ruled scaled drift allowance; do not invent a new disk hold. |

H's data comes from this Mac, already recorded. It need not be remeasured merely to execute the desk derivation. New observations are needed to fill actual evidentiary gaps, or if the eventual registered inputs/collection shape change. BY-0's source report is docs/process_traces/2026-10-22-forward/BY-0-H-DESK.md on **lane/2026-10-22-bytes-h-desk**; it is not present in this pass1 base. I read that branch explicitly and pinned its associated data commit above.

## Step list for BY-SLOTS / BY-PIN

1. **Replay the frozen desk inputs now.** Use commands.md §§1–3. Preserve the original H outputs. Join independent raw-byte receipts by run id, keep nulls for never-ran members, run the integrated current C5 and retain its source hashes. Expect stopped-session fail/unavailable lines, not a zero-exit requirement. This yields six current P candidates and stream bounds without a quiet window.

2. **Resolve the final time inputs without guessing.** Use commands.md §4 to make six isolated draft rows. Preserve measured_margin_complete=false and the fixed-time lower-bound disclosure. Search for actual verdict/backup timing receipts; if absent, put their collection in the next quiet-Mac brief. The lead decides whether the eventual registration explicitly qualifies existing partial observations or first completes the remainder. This report does not convert incomplete H evidence into full C5 success.

3. **Install approved sizing in the owner lane.** Future edits belong in configs/b6/registration/sizing_b5.json at the six pointers above. Supply pack_id, S, stream max, full disk_derivation and source receipts. Preserve ALPHA/BETA/GAMMA. Validate every selected pack explicitly, not merely every existing bytes-s row. If allowance inputs/form change, regenerate all affected P values. Keep exact integer P reconstruction and real tree-derived n. This seat has made none of these out-of-scope edits.

4. **Bind the final collection and identity inputs.** Future owner edits: configs/b6/packs/bytes-sN-p1/registration.json, configs/campaigns/bytes-sN-p1/plan_tree.json, configs/bytes/identity_pins.json and the shared registration inputs actually consumed under configs/b6/registration. The twelve current pass trees have arm_attachments={}; BY-SLOTS must supply the approved fourteen-binding launch declaration before the native writer can launch. Do not copy a test's synthetic declaration into production. Regenerate tree-dependent pin receipts after final tree changes. BY-G already supplies eleven model/reference file identities; use them instead of re-downloading or rerunning KV generation merely for P.

5. **Finish registration, integration and gate work.** The six pack registrations are currently status=draft, with null estimator versions and draft_notes. open_packs rejects them. Fill the §18 slots in docs/registrations/bytes_pack_v1.md, resolve the existing analysis/twin integration items, put the agreeing file SHA-256 into estimators[].version, remove draft_notes and commit registered packs only under the required cold gate. BY-MERGE reports the BY-TWIN-BAT agreement gap; I have not rerun or adjudicated it. The whole laptop suite before the BYTES release-line merge and the smoke by fingerprint remain §19 requirements. The final registered inputs, rather than report-only drafts, must be in the measurement checkout.

6. **Prepare in a fresh authentic measurement checkout.** Check the actual ledger against its committed head pin; preserve H's evidence instead of repairing its old open bracket implicitly. BY-0 reports H's old h2 checkout at 408 ledger rows with pin 402; those are historical observations, not a command to truncate or reset a current ledger. Use the real measurement interpreter and desk identity producer. A valid row lets the sizing/P seam pass; other genuine failures must be diagnosed at their actual consumer. Reusing stale prepared.json can bypass a fresh preparation read, so use a fresh staging/session id for the finalized registration.

7. **Obtain a current physical disk snapshot and the last arm checks.** The largest current P is s4 at 85,140,886,637 B. With its four-member smoke due, PRECHECK's bar is P+1,763,027,229 = **86,903,913,866 B**. Do not add the old 150 GiB reserve. The actual arm repeats the physical free-space check. The registered in-window disk.low stop stays unchanged. Quiet handoff, notice, smoke, installation and every pass-1 t0 before the stated cutoff remain the lead/operator's actions; none was performed here.

## Decisions I made

- Treat the user-selected report task as the live AGENT task. Mission M0 intake found ACTIVE_STOP_CARD NONE. The base's generated lane pointers are older; the explicit bounded user instruction selects this work. TASK_QUEUE's contents response was empty, so I did not infer a new queue instruction from it.
- Apply H-DISK through the later adopted BY-C5 dispositions to BYTES. Preserve the deliberate R2-3 registration-completeness exception; receipt/provenance gaps continue as flags under their existing rules.
- Count the actual stage graph including all 25 planned references and no spares, rather than only science members.
- Use independently recorded one-copy raw allocations. Preserve the current C5 observed-group/overhead arithmetic, committed fixed bytes, two whole-basis ceilings, c=2 and 7200 s WAIT.
- Produce six explicit report-only rows and the full derivation for every one. Keep pass 2 as a later registration requirement.
- Label all time drafts and soak incompleteness. No clean-only margin, guessed padding, model interpolation, borrowed threshold, or new acceptance bar was introduced.
- Separate the Prepared input contract from final registration and launch gates. Preserve absent T10/T_phase's flag-only handling and the fixed-pack cap ruling.
- Use the connected GitHub tools for bounded report delivery because the cloud executor remained starting/offline. This changes only the authorized branch's report paths. I used expected-SHA, non-force ref advances.
- No test module was touched or run. This is report-only work; the production-shaped synthetic diagnostic is supplied for the next shell-enabled seat, with its limitation stated. I do not count it as executed validation.

## Work, executed checks and exact tails

The requested local fetch/checkout, seat shell setup, Python replay and git diff --check could not run because no usable execution environment was provided. tools/cloud/seat_setup.sh is absent from the base tree (no tools directory; exact path fetch returned 404), so there was no base setup script to execute. I read AGENTS.md, Mission M0, the targeted RUN_STATE sections, orchestration and the owning texts through the repository connector. I applied the cloud-environment-runtime skill for startup/network readiness; no Docker, model, capture or quiet-Mac command ran.

| Actual action | Exact result/tail |
|---|---|
| exec_command with pwd; later the repository/network-policy read attempt | "No usable execution environment is available. Wait for an environment to become available before using this tool." No shell process started. |
| wait_for_environment on the selected environment; runtime status rechecks | Wait remained pending. Last observed status: {"phase":"starting","connectivity":"offline","failure":null,"observations_current":true}. |
| GitHub source ref/tree reads | lane head 1c458d71d8a048e24b6c3a6b402fe3c34d9f57c3; tree 76e364fd71cf9b09b913949f16376f9ad7d1ab1b. Frozen data head 8db1b40d64d8c543e7a9bee4fd9ced0da63d4b0b. |
| Independent exact-rational derivation in the tool JavaScript runtime | Six P integers equal the C5 report table exactly; six identities P=2(B+WAIT)+fixed and 3nq+headroom=P. Final row: bytes-s6-p1 B=16382541368, WAIT=12999877322, fixed=4046531103, P=62811368483, q=145622589, headroom=30046285958. JSON parse succeeded. |
| Artifact validation tail | "6/6 exact P and native budget identities; JSON parses; all six P match BY-C5; source rows remain untouched" |
| First small commit and branch advance | 970c26693853ead5ef038a7de112c0c776e13af4, "BY-PREP-P: draft pass-1 sizing derivations and replay commands"; remote compare status ahead, ahead_by 1, exactly the two by-prep-p artifact paths; github_update_ref force=false returned {"success":true}. |

No measured agreement tolerance was selected. Integer byte/roster/budget properties were checked exactly. Source timing values were parsed from their original decimal lexemes for the independent rational derivation. Rate comparisons between independently executed programs, when the recipe is run, retain BY-C5's ruled 1e-6 relative bar; their units have no printed half-width. Rounded displays above are presentation only. No Python production replay, synthetic end-to-end execution, live prepare, full suite, Mac free-space observation, or CI result is claimed by this seat.

The final step is this report's own commit on the same branch, after reviewing its tree diff for the exhaustive write scope, followed by a non-force remote advance. No PR is opened.

## Open questions / NEEDS_RULING

**NEEDS_RULING: none for this report or the prescribed derivation.** The governing texts already choose the disk form, raw-byte domain, committed fixed term, native encoding and missing-P hold.

The registration owner still owes a concrete disposition of incomplete soak data and fixed-time receipts. Choosing a different retained planning dataset or allowance form would change registered S/P, so that choice belongs in the registration decision before its gate; I have preserved the current C5 form in the draft rather than silently choosing another. A missing measurement remains an explicit gap. The paused-window instruction remains in force.

**Next exact action:** on a shell-enabled desk seat, execute commands.md §§1–4 against the pinned H desk data, review the fresh C5 candidates and receipt gaps, then give BY-SLOTS the six approved sizing rows and BY-PIN the final-tree/registration pin work. Only the registration/quiet-window owner can finish the remaining physical and launch gates.
