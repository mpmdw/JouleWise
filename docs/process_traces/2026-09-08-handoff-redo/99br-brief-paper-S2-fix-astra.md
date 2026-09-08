WRITE_SCOPE: ["docs/contracts/paper_reported_energy.md","docs/contracts/paper_supply_custody.md","docs/contracts/paper_comparison_rendering.md","docs/contracts/paper_comparison_placements.md","docs/paper/results-fill-registry.md","joulewise/paper_reported_energy.py","joulewise/paper_custody.py","joulewise/paper_rendering.py","tests/test_paper_reported_energy.py","tests/test_paper_custody.py","tests/test_paper_comparison_placements.py","tests/test_paper_rendering.py","configs/paper_supply/supply_map.json","docs/decision_log.md","TASK_QUEUE.md"]

# Paper S2 — fix round on the Opus contract refutation (gpt-6-astra, HIGH, genre implementation)
Head 720b166c on feat/2026-09-08-paper-S2. Read the refutation at the absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99bq-ref-paper-S2-opus-contract-review.md (F1–F12) and the Astra delta at /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99bp-delta-paper-S2-astra-report.md
(clean; arithmetic verified). Cure every finding with these rulings; verify each line by reading the code:
F1 RULED: register TWO follow-ups in TASK_QUEUE.md in the file's existing row format: BRIDGE-BASELINE-ANCHORS-01
  (codex-run-v3 emits the bridge-protocol v1.1 header fragment BASE_HEAD/BASELINE_MANIFEST/BASELINE_DIGEST; until then
  runner-owned lanes treat the wrapper's baseline snapshot as the launch baseline — ruling 8 of the S2 synthesis) and
  WINDOW-LIVENESS-DOCS-01 (active-campaigns registry path, stale semantics, repair owner, no SIGTERM handler; from the
  WINDOW-STATUS-GUARD-CENSUS-01 terminal review 99ap).
F2: the contract names `statistics.fmean` over the ordered 50 members as the CANONICAL computation and states the
  algebraic equivalence to 0.2·mean(r)+0.8·mean(b) as a note (not the definition); the digest is over the canonical form.
F3: map "the four surfaces" to the exact bundle fields (bundle_read.py ~:1037–1041) and specify the collapse rule:
  tuple surfaces must be identical across their elements and equal to the other surfaces; a single int results; any
  disagreement refuses with a named code.
F4: a closed refusal vocabulary `paper_reported_energy_<reason>` raised through a typed error class (mirror the D-173
  `paper_custody_*` pattern); the contract enumerates every code; tests assert codes, not prose.
F5: update paper_supply_custody.md ~:206–208 and paper_comparison_rendering.md ~:65–67 to name BOTH pending production
  roles (1p7b.v5 and 8b.v5); state in the contract why the 8b pending role was added (both models are cells of the
  registration) — it is now a ruled clause, not an unruled addition.
F6: reconcile the X5 census in paper_comparison_placements.md ~:71–74 with paper_supply_custody.md ~:455–458 (five
  fields defined in paper_reported_energy.md; RETIRED_FALLBACK; no placement restored); keep the S1 three-table
  agreement tests green (tests/test_paper_comparison_placements.py) — if the agreement test pins the old text, update
  the pin to the reconciled text and say so.
F7 RULED: the renderer reads the projection from a typed field that BOTH the fixture branch and the future production
  branch carry (`reported_energy_projection: ... | None` on VerifiedReportedEnergyParents); None → closed refusal
  `paper_reported_energy_projection_absent`; never StopIteration. Add a POSITIVE fixture rendering test through the
  projection and the absent-refusal test.
F8: assert the 8b pending entry in tests/test_paper_custody.py's production git-blob coverage test.
F9 RULED: the ordering fence becomes mechanical: a function in paper_reported_energy.py that, given the repo and a
  model, checks (a) the commit introducing the registration constants (found via `git log --diff-filter=A` or a pinned
  sha recorded in the contract) is an ancestor of the commit adding the spec blob, and (b) the spec's digest equals
  registration_sha256(model); a synthetic-repo test (temp git repo) proves both directions (violates when the spec
  predates the registration). The contract states this check as the fence.
F10: decode cells require only the OUTPUT denominator surfaces; prompt-surface agreement is required only for prefill
  cells; regression each way.
F11: n_bundles renders `expected_n` from the registration, not a literal.
F12: enrich the D-179 index row to the substance level of its neighbours; leave the numbering (D-176 is on PR #303;
  D-177/D-178 are pending entries for the characterization and S3 rulings — do NOT create them here).
Acceptance (rc-gated to a log): tests.test_paper_reported_energy tests.test_paper_custody tests.test_paper_rendering
tests.test_paper_comparison_placements tests.test_paper_comparison_contract tests.test_d117_floor_qwen25_1p5b_plan
tests.test_gen_state tests.test_docs_freshness; git diff --check; no commit; header < 8192 bytes; report per finding
with file:line and, for F7/F9/F10, the counterfactual.
