```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"clean","completion":"complete","summary":"Opus B2 closed under the source-backed 1.5B ruling; both model arms qualified and all prescribed checks pass.","workspace":{"base_requested":"c1fa5f15","base_mode":"exact","head_start":"c1fa5f15a9e106f3de222c9c2d5c8781e75d892e","head_end":"c1fa5f15a9e106f3de222c9c2d5c8781e75d892e","upstream_end":"c1fa5f15a9e106f3de222c9c2d5c8781e75d892e","branch":"feat/2026-09-05-paper-m"},"pathspec":["docs/paper/draft-v2-skeleton.md","docs/paper/results-fill-registry.md","tests/test_paper_terms_lint.py","docs/process_traces/2026-09-05-paper-m/07-fix-round-2b-report.md"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"ready"},"verification":[{"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 11 tests in 2.378s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_terms_lint","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 16 tests in 2.830s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_select_outcome_branches","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 5 tests in 0.816s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_replay_fence","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 10 tests in 26.775s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V5","kind":"other","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 scripts/check_paper_replay_fence.py --corpus-root /Users/edr/code/JouleWise","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["MEMBER 20260722T145535-e941c821","COMPARED 43","MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"COMPARED 43\\nMISMATCHES 0$"}},{"id":"V6","kind":"lint","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 docs/paper/fill-rehearsal/select_outcome_branches.py --check-rendered docs/paper/draft-v2-skeleton.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["METHODS_DIAGNOSTIC validated; abstract_words=246, limit=250"]},"expected":{"exit_code":0,"tail_regex":"METHODS_DIAGNOSTIC validated; abstract_words=246, limit=250$"}},{"id":"V7","kind":"inspection","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}],"flags":[]}
```

## Change

Opus B2 is CLOSED. This resumes the partial cure in `06-fix-round-2-report.md` under the lead's explicit ruling that the primary artifact governs: the failing arm is **Qwen2.5-1.5B-Instruct-4bit (1.5B)**, and the passing arm is **Qwen2.5-7B-Instruct-4bit (7B)**.

Mission M0 found no active stop card or global work-selection gate. The targeted restart, workspace, queue, Do-Not-Do-Yet and orchestration instructions were inspected. This direct PAPER-M resumed ruling supplied the bounded work selection; lead-owned queue/state files were not writable. Intake was clean on the requested branch and exact base. HEAD and upstream remain unchanged. No commit, discovery suite, Claude/Codex launcher, child agent, quiet-machine measurement, or out-of-scope repository write occurred.

Before any article edit, the primary artifact was read at
`/Users/edr/code/JouleWise/docs/process_traces/2026-08-09-prefill-phase-proof/results.json`.
Its bytes equal the tracked artifact at
`docs/process_traces/2026-08-09-prefill-phase-proof/results.json`.
SHA-256: `e93c1d9c9ccff764cb6c64379cc3551c710e63b38b5314569d89662d2b88d8b1`.

Independent per-bundle counts, distinct membership, model names, and minimum-sample verdicts were recomputed and checked against both stack summaries before writing:

| Artifact stack / model in every member | Distinct bundles | Overlapping sampler records | Re-derived verdict | Membership |
|---|---:|---|---|---|
| 1.5B / Qwen2.5-1.5B-Instruct-4bit | 50 | 37 with two; 13 with three | 37 not_resolvable_sample_count; 13 identifiable | 10 runs_window_a10_20260725; 40 runs_window_c_20260726 |
| 7B / Qwen2.5-7B-Instruct-4bit | 50 | 33 with three; 17 with four | 50 identifiable | 50 runs_window_7bfloor_20260729 |

Each member has `minimum_samples=3`; its re-derived outcome agrees with its overlap count. The strengthened existing test repeats these checks against the explicitly configured primary corpus and the matching tracked artifact. These are checks of retained historical evidence, not a new live hardware experiment.

The Abstract, record-support section, Discussion, availability statement and Conclusion now identify both model arms. The record-support population paragraphs precede the detailed r03 example, which now explicitly names the 1.5B model. The diagnostic conclusion states model/stack dependence: two records per bundle failed for the 1.5B stack; its three-record members passed, and three or four passed for 7B. This does not isolate a causal size effect, establish an energy comparison, or promote voided energy values.

Numerical bindings remain DG-067–069 for 37/50/13 and DG-072/073/076/077 for overlap counts and the minimum. Existing EXTRACT rows DG-135–139 bind the 7B size, passing count, three/four-record histogram and identity; the newly repeated 33 and 17 in the Abstract and Conclusion use those rows. New EXTRACT rows DG-140–142 explicitly bind the 1.5B model identity and its 10/40 membership to the artifact path and fingerprint. All retain DIAGNOSTIC_ERA / NON_CLAIM_BEARING labels.

Cure map uses final line numbers; old text is from the clean requested base:

| Finding | Line | Old | New |
|---|---|---|---|
| Opus B2 — Abstract model identity and positive arm | draft-v2-skeleton.md:28 | “Earlier short requests” with 37/50 failures; passing arm only “historical 7B stack.” | Both full Qwen2.5 model names; 1.5B has 37 two-record failures and 13 three-record passes; 7B has 50 passes, split 33 three-record / 17 four-record. |
| Opus B2 — population identity, membership and verdicts | draft-v2-skeleton.md:675 | “1.5-billion-parameter diagnostic configuration” with no full model name or local membership disclosure. | Full 1.5B identity, 50 bundles, 10 a10 + 40 window C, explicit not_resolvable_sample_count / identifiable outcomes; both population paragraphs now precede the example. |
| Opus B2 — positive-arm diagnostic interpretation | draft-v2-skeleton.md:683 | 7B count disclosure followed by “Record support thus differs by model/stack.” | Full 7B identity and 33/17 count disclosure retained; explicit count discipline: two fail for 1.5B, three pass for its remaining members, three/four pass for 7B. |
| Opus B2 — detailed failure example | draft-v2-skeleton.md:739 | “this smaller-stack population.” | “the Qwen2.5-1.5B-Instruct-4bit population”; both population arms introduced before r03. |
| Opus B2 — Discussion | draft-v2-skeleton.md:788 | “smaller-stack population” and “7B population.” | Qwen2.5-1.5B-Instruct-4bit and Qwen2.5-7B-Instruct-4bit named together. |
| Opus B2 — availability | draft-v2-skeleton.md:896 | “smaller-stack” and “7B stack” custody descriptions. | Both full model names and explicit DG-140–142 / DG-135/139 bindings. |
| Opus B2 — Conclusion | draft-v2-skeleton.md:918 | Unqualified “historical record-support population” and “historical 7B stack.” | Both model names and complete histograms; explicit model/stack-dependent record identifiability rather than blanket failure. |
| Opus B2 — new source bindings | results-fill-registry.md:1016 | No explicit full 1.5B model-identity row or dedicated 10/40 membership rows in the round-2 disclosure. | DG-140–142, each EXTRACT with primary path, SHA-256, exact member/identity locator and non-claim-bearing status. |
| Opus B2 — regression | tests/test_paper_terms_lint.py:349 | Checked both primary populations and DG-135–139, but did not require both model names in every result section. | Also checks per-member count/verdict agreement, DG-140–142, model qualifiers in four sections, headline histograms, explicit diagnostic conclusion and absence of 1.7B. |

Wrong `1.7B` article sites: **none at intake; none after edits**. No model-label replacement sites are omitted. The registry's separate prospective Qwen3-1.7B identity is legitimate prospective context and was preserved. Figure 3's caption and SVG illustrate the generic two/three-overlap rule, explicitly not population frequencies; neither asserts a historical model failure. No historical-failure figure caption required relabelling, and no figure bytes changed.

Acceptance retained: no active article fills; only METHODS_DIAGNOSTIC selection; retired empirical selectors rejected; historical headline and transfer limitation preserved; first-use footer remains `Terms inventoried: 261; FAILS: 0.` at `docs/paper/protocol/first-use-audit-ledger.md:285`. The selector reports 246 Abstract words against 250. Other round-2 cures were preserved, not claimed as newly authored.

Exact final verification tails (commands and replay expectations are in the envelope):

V1:
```text
Ran 11 tests in 2.378s

OK
```

V2:
```text
Ran 16 tests in 2.830s

OK
```

V3:
```text
Ran 5 tests in 0.816s

OK
```

V4:
```text
Ran 10 tests in 26.775s

OK
```

V5:
```text
MEMBER 20260722T145535-e941c821
COMPARED 43
MISMATCHES 0
```

Next exact step: lead reviews this uncommitted diff and report for final acceptance. No implementation blocker remains.

## Verification notes

All five prescribed baseline commands passed before edits, one at a time with `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise`. Final runs used that same sequential order and environment; the discovery suite was expressly prohibited and was never run.

Two intermediate checks found prose-edit regressions and were cured before the final green runs. First-use ledger: `Ran 11 tests in 2.328s`, `FAILED (failures=2)`; shortening the Abstract moved “measurement window,” and wording in the body moved “The model.” Restoring the measurement-window sentence and rephrasing the body preserved their existing ledger homes without changing the ledger. Terms lint: `Ran 16 tests in 2.835s`, `FAILED (failures=1)`; a line wrap split the existing exact “ten named members” assertion. Restoring the contiguous custody phrases cured it without weakening that assertion. No unresolved failure remains.

