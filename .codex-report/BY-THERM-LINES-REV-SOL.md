GPT-6 (exact runtime model identifier is not exposed in this session)
VERDICT: REJECT

Review target: `ee4ce93fc..5d80e12cd`, repository `mpmdw/JouleWise`. Authority: registration §21 item 3 and §7. Synthetic Linux execution, Python 3.13.5, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`. No real BYTES data or hardware was used. Neither harvest nor analysis was edited.

1. **BLOCKER — Native grouped exports are not preserved: heldout changes refuse, and successful transforms silently lose unchanged heldout rows.** `scripts/bytes_thermal_lines.py:231`, `:259`. The script requires every changed member in the public runs CSV, but the real exporter puts heldout science rows in the private, already-offset CSV and publishes its locator/census in the session sidecar (`joulewise/b6/export_runs.py:724-769`). The transform copies neither that sidecar nor that store. This is not an exotic malformed export. The native campaign generator/exporter reproduces both failures.

   Repro, from repository root:

   ```sh
   JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -u .codex-report/by-therm-lines-rev-sol/campaign.py
   ```

   Relevant output tail:

   ```text
   CSV_TRANSFORM bytes-s5-p1 REFUSED changed member absent from CSV
   CSV_TRANSFORM bytes-s5-p2 REFUSED changed member absent from CSV
   CSV_TRANSFORM bytes-s2-p2 success
   BLINDED_SOURCE_CENSUS bytes-s2-p2 100 model_rows 50
   BLINDED_OUTPUT_CENSUS bytes-s2-p2 50
   BLINDED_OUTPUT_MODELS bytes-s2-p2 [('Qwen3-8B-4bit', 'computed', 9, None), ...]
   ```

   The other 50 science rows are the unchanged heldout Qwen3-30B model. `_stage_export_rows(include_withheld=True)` follows the source sidecar, but treats an output without a sidecar as a legacy complete CSV. Thus this is also silent census loss, not merely an explicit refusal. With `include_withheld=False`, neither source nor output intentionally opens heldout rows; that stage restriction does not justify losing them after the stage-1 commit. The s5 request-end and hull alternatives cannot be produced through this blinded path when they change heldout members. Fit-only lines can compute; it is incorrect to say neither command can ever work on real data. Until supported, an affected line must explicitly print `not defined (withheld thermal-line rows unavailable)` rather than disappear or silently omit a model. The hidden rows are already offset, so editing their code field need not unblind measurements.

2. **MAJOR — The linked output can change meaning while all recorded input SHA-256 values still match.** `scripts/bytes_thermal_lines.py:125`, `:239`, `:251-257`. Only files read for the transform are hashed. Linked reductions, bundles, flags, and other analysis inputs are outside that record. The unchanged analysis does not validate `thermal_line.json` before reading them. The campaign probe publishes an output, changes one source reduction, then re-runs unchanged `load_records` on the output. Its kept synthetic rails record and the reduced result change without any recorded hash mismatch.

   Repro: the campaign command above, or the smaller independent probe:

   ```sh
   JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 .codex-report/by-therm-lines-rev-sol/probes.py
   ```

   Output:

   ```text
   PUBLISHED_REDUCTIONS_CHANGED True
   ANALYSIS_LINK_MUTATION True ALL_RECORDED_HASHES_MATCH True
   LINK_MUTATION True all_recorded_hashes_match True
   ```

   A later replacement/re-harvest at the same source paths can therefore alter a published view without the promised digest detection. Moving the source also breaks the absolute links. This fails the requested persistence property. For plain archives I verified that analysis itself preserves every source file's hash; `readable_run` uses external scratch for compressed readers. No source-writing analysis defect was demonstrated. Writable links alone are not evidence that the current analysis writes through them.

3. **MAJOR — Missing thermal evidence causes a nonphysics CLI refusal instead of a printable line/status.** `scripts/bytes_thermal_lines.py:167-169`, `:283-284`. A real harvest can have no thermal journal: monitor joins emit disclose-only `thermal.unmeasured` and continue. The sensitivity tool instead exits before producing any record, even when there are no OS exclusions to remove and its exclusion set must equal the primary's.

   Repro: `probes.py` above; it removes the journal and clears the source exclusion list before invoking the transform. Output:

   ```text
   REFUSAL missing-journal archived thermal journal unavailable; no evaluation written
   ```

   This is a real archive state, not a physical stop. With no affected OS codes the line can carry `thermal.unmeasured` and retain the primary exclusion set. If an affected member's window cannot be evaluated, print `not defined (archived thermal journal unavailable)` with its identity/evidence flag. Do not invent a restoration.

   The other requested refusals have different reach. CSV/archive code disagreement is not produced by a coherent native export of the same acceptance: export constructs `exclusion_codes` from acceptance member exclusions. It can occur with a stale export after re-acceptance, changed records, or mixed input directories; that supplied state should print `not defined (CSV/archive exclusion disagreement)` and identify the member. A changed member absent from the public CSV occurs routinely through the native withheld store (finding 1), as well as through genuinely incomplete exports; the latter should print `not defined (changed member absent from export)`. The probes execute both refusal branches. Neither disagreement authorizes choosing a union or intersection of codes. Output-overlap refusal protects source bytes and is appropriate; the explicitly required request-end-would-add finding is also appropriate.

4. **MAJOR — The required uninterrupted counting-session test is absent, and the shared harvest fixture does not supply it.** `tests/test_bytes_thermal_lines.py:53`, `:239`. One test family replaces acceptance with a hand-built projection of B5 exclusions. Another starts from a generated archive and injects thermal records. Both pass, but neither executes the specified real harvest → real B6 acceptance → transform → valid analysis chain.

   Repro:

   ```sh
   JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -u .codex-report/by-therm-lines-rev-sol/chain.py
   ```

   I removed the acceptance adapter in this independent script and called real `accept_archive`, native `export`, both transforms, and unchanged `load_records`. These loaders block before `reduce_models` is reached. The real acceptance rejects the shared fixture with missing captures/bracket, undefined NEG-8, and structural failures. Output includes:

   ```text
   REAL_ACCEPTANCE 2 EXCLUDE False [...]
   REAL_ANALYSIS 2 tail all archive not defined session is not a counting accepted attempt
   REAL_ANALYSIS 2 tail all small-line2tail not defined session is not a counting accepted attempt
   REAL_ANALYSIS 2 tail blinded ... not defined model predictors differ from registered manifest: mock-model
   ```

   The clean pass-1 fixture has the same ingress limitations. I did not override counting, fake acceptance rows, or alter the bound analysis to conceal this. Consequently this review does **not** establish the requested single valid counting chain for cases (a)-(f). The committed scripts distinguish the uninterrupted but unavailable chain from the valid campaign replay. This gap remains a delivered-test defect, not evidence that real BYTES harvests are non-counting.

Executed

- `python3.13 -m unittest tests.test_bytes_thermal_lines -q`: 8 passed, 275.067 s. This includes the supplied full-module archive/blinded reducer replay, battery-code preservation, inside-request retention, no-request fallback, sentinel JSON/CSV opacity and byte preservation, null/unavailable/reference records, idempotence, and overlap/monotonicity refusal.
- `python3.13 -m unittest tests.b6.test_bytes_p2_thermal_window tests.test_harvest_b5_window -q`: 198 passed, 11 skipped, 727.391 s. The pass-1, block-5 and other-group byte-identity replays passed.
- `chain.py`: real block-6-path harvest and real acceptance/export, without the B5→B6 exclusion adapter, on pass-1 tail, pass-2 tail, and clean pass-1 sessions. Both commands run; archive and CSV change lists agree; second transforms have no changes; overlapping output is refused. Sealed thermal threshold values exactly equal resolved harvest inputs; sealed spans exactly equal production assessments. Analysis was invoked at both stages; its unavailable outcomes are disclosed above.
- `campaign.py`: native grouped claim-shaped exports for s2 and s5, both passes, and unchanged analysis. Only existing keys from those synthetic sessions are copied to the release directory. Archive analysis' historical `export/bytes` locator is supplied alongside native per-pack exports, with the withheld locator preserved. This is a campaign replay, not a harvest-chain substitute. All source archive hashes remain unchanged across the original/output analysis runs before the deliberate mutation test.
- `probes.py`: duplicate OS rows are both removed; a second thermal code survives; references and absent-span members retain codes; equal request/hull windows retain the hull outcome; an exact-end nonzero read retains OS exclusion; nonnumeric boundary reads advance to the next numeric read; malformed lines produce a notice. No tolerance is used. Its guarded JSON decoder rejects measurement sentinel decoding, while stdout excludes the sentinel.
- Bound analysis SHA-256: `18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`, unchanged. `git diff --check` passed.

Per-case accounting against §21 (distinguishing actual reduction from code-only checks):

| Case | Source → output; hand check |
|---|---|
| (a) pass-2 tail-only | Native campaign archive replay: Qwen3-8B and Llama each keep repeats 0–9 and quads 0–9 on source; output keeps repeats 0–9 and quads 1–9. The selected member is ordinal 10 in quad 0, so all four quad members drop. Matches §21. Qwen fit CSV agrees; Llama CSV refuses. |
| (b) null/unavailable/reference | Executed probes preserve their exclusions exactly and report notices; existing hull codes are not duplicated. The production thermal-window tests separately exercise real missing-span/journal and reference joins. A complete valid counting-chain unit result for these variants was not obtained. |
| (c) pass-1 restoration | Native campaign replay: source keeps repeats 0–9, quads 1–9; output additionally keeps quad 0, for 10 repeats/10 quads. Only ordinal 10 loses the OS code. Matches §21. The supplied small harvest tests separately confirm inside-request members stay excluded and a restored OS member with a battery code stays dropped; these are not full-module reducer results. |
| (d) clean pass 1 | Real harvest/acceptance transform has an identical exclusion list and `equals_registered_line=true`; analysis remains unavailable for the independent fixture reasons above. Matches the exclusion-set rule; does not establish a computed printed value. |
| (e) stages | Archive/CSV member change lists agree when changed members are public. The native mixed export then loses 50 heldout science rows; heldout-member transforms refuse. Fails the stage-equivalence requirement. |
| (f) repeat/source safety | Second transforms have no changes and overlapping writes refuse. Plain archive analysis preserves source bytes. Later linked-input mutation is undetected by all recorded hashes. Fails persistence. |

The independent edge fixture removes OS from `dup`, `other`, and `nonnumeric`; retains OS on `ref`, `absent`, `equal`, and `edge`; retains `thermal.powermetrics_pressure_elevated` on `other`. These are exactly the production-function/request-end decisions. Pass 2 adds only OS for science records with an available journal and true hull exclusion; null/unavailable records add nothing. I found no exclusion-set arithmetic defect on these inputs.

Threshold/span provenance is correct for a coherent, unchanged archive. Harvest writes resolved threshold provenance in `record_thresholds`, seals the same assessed `self.spans` before monitor joins, and uses those spans and `inputs.thresholds` in the production thermal join. The transform reuses that sealed gap value and the integer hull-start/request-end stamps. No new floating comparison or agreement bar is introduced. The pre-existing production gap conversion uses `int(float(gap_s)*1e9)`; it is not a new tolerance. Measurement JSON is lexically skipped; opaque CSV values are copied byte-for-byte. The executed supplied sentinel tests and independent guarded decoder support that property for the tested production-shaped fields.

Decisions I made

- Reject for real grouped-export failure and undetected linked-input drift; passing exclusion-set probes do not cure those failures.
- Keep primary policy, acceptance physics, five-unit minimum, whole-unit rule, NEG-8, and analysis unchanged. Synthetic seam evidence is not hardware validation.
- Treat missing records as a flag or explicit `not defined` reason under the supplied doctrine. Preserve safety overlap refusal and the brief's explicit would-add finding.
- Do not claim the requested complete counting chain passed. Commit the honest failing/unavailable chain reproduction beside the native export and adversarial probes so the lane can turn them into regression tests.
- Restrict repository writes to this report and `.codex-report/by-therm-lines-rev-sol/`; no registry or project-state edits.
