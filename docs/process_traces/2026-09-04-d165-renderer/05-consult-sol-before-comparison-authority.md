```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The repository has positive authority for a non-admitted whole-window verdict but no governed artifact or validator receipt that authenticates claim-verdict nonissuance; R4-F1 must split those cases.",
  "workspace": {"base_requested":"47f81ca9","base_mode":"exact","head_start":"47f81ca9328d66fb37e73408d805501068fc2e6f","head_end":"47f81ca9328d66fb37e73408d805501068fc2e6f","upstream_end":"47f81ca9328d66fb37e73408d805501068fc2e6f","branch":"feat/2026-09-04-d165-outcome-renderer"},
  "pathspec": ["docs/process_traces/2026-09-04-d165-renderer/05-consult-sol-before-comparison-authority.md"],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {"id":"F1-AUTHORITY-SUBSTITUTE","severity":"blocker","file":"joulewise/results_fill_outcome.py:32-63,138-180","text":"The renderer substitutes an unregistered four-field projection and a caller-constructible result tuple for the actual whole-window artifact, custody paths, and execution of its validator."},
      {"id":"F2-ABSENCE-NOT-EVIDENCE","severity":"blocker","file":"joulewise/analysis_engine/claims.py:22-30; joulewise/analysis_engine/artifact.py:945-973,1655-1681","text":"No current claim-verdict schema issues outcome 'absent', and validate_claim_verdicts validates an artifact that exists; filesystem absence cannot authenticate the registered 'required verdict absent' reason."},
      {"id":"F3-IMPOSSIBLE-FINALIZED-ANCHOR","severity":"blocker","file":"joulewise/analysis_manifest_v3.py:3498-3515","text":"A non-admitted whole-window verdict prevents finalized-manifest issuance, so finalized_manifest_bytes cannot be the mandatory identity anchor for the very before-comparison window stop it is meant to render."},
      {"id":"F4-R4-F1-ABSTRACT","severity":"should_fix","file":"docs/process_traces/2026-09-04-paper-i/06-magistrate-contract-rulings.md:25","text":"R4-F1 names source bytes and a validator result without naming the real schemas, path/digest custody, validator invocation, receipt replay, or the fundamentally different proof needed for nonissuance."}
    ]
  },
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"rg -n 'WHOLE_WINDOW_SCHEMA =|def whole_window_refusal_reasons|SCHEMA_VERSION = \"joulewise.claim_verdicts.v1\"|def validate_claim_verdicts|CLAIM_OUTCOMES =|def render_outcome_fills' joulewise/whole_window.py joulewise/analysis_engine/artifact.py joulewise/analysis_engine/claims.py joulewise/results_fill_outcome.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["joulewise/whole_window.py:5525:def whole_window_refusal_reasons("]},"expected":{"exit_code":0,"tail_regex":"[\\s\\S]*joulewise/whole_window.py:5525:def whole_window_refusal_reasons\\("}},
    {"id":"V2","kind":"inspection","cmd":"sed -n '1p' docs/process_traces/2026-09-04-d165-renderer/05-consult-sol-before-comparison-authority.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["```json"]},"expected":{"exit_code":0,"tail_regex":"^```json$"}},
    {"id":"V3","kind":"inspection","cmd":"git status --short","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["?? docs/process_traces/2026-09-04-d165-renderer/05-consult-sol-before-comparison-authority.md"]},"expected":{"exit_code":0,"tail_regex":"^\\?\\? docs/process_traces/2026-09-04-d165-renderer/05-consult-sol-before-comparison-authority\\.md$"}}
  ],
  "flags": [
    {"id":"L1","kind":"lead_ruling","level":"blocking","text":"The magistrate must choose positive nonissuance evidence or an unrenderable absence; current doctrine cannot authenticate an absent claim-verdict artifact as an issued reason.","needs":"Adopt the replacement R4-F1 clause and either register a content-addressed claim-verdict nonissuance/completion artifact plus validator, or amend OR-01 and paper-G so absence remains STOP_FILL and is not called an issued reason."},
    {"id":"V-GAP","kind":"verification_gap","level":"nonblocking","text":"Per the preflight rule, this structural consult used source inspection only; no behavioral claim required a test.","needs":""}
  ]
}
```

## Findings

### F1-AUTHORITY-SUBSTITUTE — blocker

#### Q1 — the governed source that exists today

For a whole-window stop, the positive source is an
`idle_admission_whole_window_verdict` row whose schema is
`joulewise.idle_admission_whole_window_verdict.v1`
(`joulewise/whole_window.py:74`). `run_campaign` derives the issued status from
the evaluated core as exactly `invalid`, `passed`, `flagged`, or `failed`
(`scripts/run_campaign.py:6324-6338`), constructs the schema-bearing row with
its evaluation basis, bundle census, member failures, and idle-admission core
(`scripts/run_campaign.py:6353-6385`), appends that exact row to
`campaign_log.jsonl` (`scripts/run_campaign.py:6400-6407`), and can publish the
same bytes as a no-clobber standalone output (`scripts/run_campaign.py:6408-6414`,
`scripts/run_campaign.py:3363-3383`). There is no governed artifact schema
named `whole_window_admission`, and the real artifact does not issue
`kind: whole_window_admission`, `outcome: excluded`, a public model label, or
the synthetic four-field projection accepted by the renderer.

The owning validator is `whole_window_refusal_reasons`. Its actual contract is
not `(bytes) -> reason`: it consumes a runs root, the exact referenced bundle
IDs, and optionally the evaluation-basis digest, authenticated consumption
session, and consumption-semantics ID (`joulewise/whole_window.py:5525-5533`).
It reopens the authoritative campaign log (`:5575-5607`), selects the matching
basis (`:5621-5644`), and revalidates every candidate row (`:5666-5713`). The
row validator checks the real schema, exact membership, policy/provenance,
source manifests, and rederived evidence (`joulewise/whole_window.py:5031-5055,
5098-5149,5169-5179,5360-5475`). Thus “measurement window excluded” is paper
policy derived from a validated, non-admitted row; it is not an issued
`outcome: excluded` field. The exact public reason must be a registered
rendering of the authenticated row's status, `idle_admission_core.conditions`,
and `member_failures`, not caller prose.

The current `BeforeComparisonValidationResult` is not this validator's return
type and is not produced anywhere by it. It is a public dataclass containing a
validator-name string, two caller-supplied digests, and a tuple
(`joulewise/results_fill_outcome.py:50-63`); `_validated_before_payloads` merely
checks internal equality among those caller-controlled values (`:138-180`).
The round-1 wrapper therefore has the same authority as the round-0 dict.

### F2-ABSENCE-NOT-EVIDENCE — blocker

The claim side has a positive artifact only when analysis succeeds:
`joulewise.claim_verdicts.v1` (`joulewise/analysis_engine/artifact.py:42`). The
producer evaluates every contrast in the authenticated analysis manifest and
places its `claim_evaluation` in the emitted contrast row
(`joulewise/analysis_engine/__init__.py:1761-1807`), then finalizes and writes
the content-identified artifact (`:1827-1889`). Its closed outcome vocabulary
is `not_estimable`, `not_resolvable`, `unresolved`, `direction_supported`, or
`equivalent`; `absent` is not a verdict (`joulewise/analysis_engine/claims.py:22-30,
326-375`). `validate_claim_verdicts` checks the full artifact and its canonical
ID (`joulewise/analysis_engine/artifact.py:945-973`), requires every contrast to
carry `claim_evaluation` (`:1655-1681`), and checks family enumeration against
the contrasts (`:3014-3030`).

R2 prospectively orders `joulewise.claim_verdicts.v2` with an added
`claim_side_bound`, but no v2 producer or validator exists under `joulewise/`
at this head (`docs/process_traces/2026-09-04-paper-i/06-magistrate-contract-rulings.md:13-17`).
That unimplemented additive schema would still carry a claim evaluation; it
does not convert nonissuance into an `absent` outcome.

Therefore no current artifact or validator **issues** “required
token-generation verdict absent” or “required prompt-processing verdict
absent.” If `claim_verdicts.json` does not exist, there are no bytes, content
digest, artifact ID, or `validate_claim_verdicts` result to authenticate. If a
valid artifact exists, the required contrast has a real five-outcome verdict,
not an absent one. The tiny `claim_evaluation/outcome: absent` object in the
renderer is an unregistered assertion that `validate_claim_verdicts` has never
validated.

Paper-G currently says OR-01 prints “the reason issued by the governing
evidence” (`docs/paper/fill-rehearsal/branch-selection.md:8-13`) and later calls
verdict absence an issued stop reason (`:64-73`). That is supportable for a
positive whole-window row, but not for raw nonexistence. Today the paper must
treat a missing claim-verdict artifact as **unissued/unavailable**: it may not
publish caller-authored absence prose as an authenticated issued reason, and
OR-01 remains `STOP_FILL`. To publish the registered absence sentence, the
workflow first needs a positive, content-addressed nonissuance/completion
artifact whose validator binds the expected verdict role and output namespace
to the authenticated prospective campaign and records why issuance did not
occur.

### F3-IMPOSSIBLE-FINALIZED-ANCHOR — blocker

The round-1 signature requires `finalized_manifest_bytes` for every
before-comparison case (`joulewise/results_fill_outcome.py:306-346`). That is
impossible for the whole-window exclusion branch: finalization opens the real
whole-window artifact and refuses unless its status is `passed` and
`claim_licensing` is true (`joulewise/analysis_manifest_v3.py:3498-3515`). The
fixture's minimal “finalized manifest” is consequently not evidence that the
production stop can cross this boundary.

#### Q2 — exact renderer input contract

Use a path-only orchestration boundary. Each `PATH` below must have a separate
expected SHA-256, and every receipt is itself supplied by path plus SHA-256;
the renderer reopens all paths without following an unbound replacement and
replays the named validator. A receipt is corroborating, content-addressed
output, not a capability token: accepting a caller-constructed receipt object
would repeat this defect.

1. **Pre-stop identity:** `prospective_manifest_path` + digest
   (`joulewise.analysis_manifest.v3.prospective`), `plan_tree_path` + digest,
   and a prospective-validation receipt binding both. Replay
   `validate_prospective_analysis_manifest_v3` with those exact paths
   (`joulewise/analysis_manifest_v3.py:2932-2975`). This is the fixed `_v5`
   identity source available before finalization; do not require a finalized
   manifest on this lane.
2. **Whole-window stop:** `runs_root_path`, `campaign_log_path` + digest, and,
   for each model/window, `whole_window_verdict_path` + digest and a
   whole-window-validation receipt + digest. The receipt must bind the real
   schema, exact campaign-log row digest, prospective-manifest digest, model and
   phase derived from the frozen pack, referenced bundle IDs,
   evaluation-basis digest, consumption-semantics ID, validator implementation
   identity, and the validator's structured distinction between
   `source_valid` and `admission=excluded`. The same command must replay
   `whole_window_refusal_reasons`; a bare reasons tuple is not a receipt and the
   present validator API needs a structured receipt producer before this can be
   wired safely.
3. **Claim verdict present:** `claim_verdicts_path` + digest,
   `finalized_manifest_path` + digest, and claim-verdict-validation receipt +
   digest. Replay `validate_claim_verdicts(artifact,
   frozen_manifest=manifest)`, require exact registered decode/prefill contrast
   enumeration, and render the actual claim outcome through DS-32/PG-08. A
   negative or unresolved five-outcome verdict is still **present** and never
   becomes OR-01 “verdict absent.”
4. **Claim verdict not issued:** until a new governed artifact exists, there is
   no input for this lane and it returns `STOP_FILL`. A sufficient future
   `joulewise.claim_verdict_nonissuance.v1` would need its own path, digest, and
   validator receipt, binding the prospective-manifest/plan-tree digests,
   exact expected contrast IDs and roles, closed expected output path,
   terminal workflow state, nonissuance reason code, and predecessor
   whole-window receipt(s). Testing `Path.exists()` is never the predicate.
5. **At close-out:** likewise accept paths + digests for the D-165 close-out,
   finalized manifest, floor artifact, and replay sidecar, plus a receipt bound
   to `validate_d165_closeout`; do not make the close-out mapping a different
   caller-object exception to the same rule.

`STOP_FILL` means “the renderer lacks authenticated authority to print”: any
missing path, digest mismatch, unsafe/replaced path, invalid or non-replayable
receipt, wrong `_v5` identity, ambiguous row/basis, validator error, or bare
artifact absence. A rendered `before comparison: ...` sentence requires a
positive validated source: either a valid non-admitted whole-window row with
its reason rendered only from issued fields, or a future valid nonissuance
artifact that positively records the absent verdict and reason. Branch
selection and sentence filling must remain distinct: process state may force
the conservative REFUSAL branch, but it does not authorize OR-01 bytes until
the relevant positive evidence chain exists.

### F4-R4-F1-ABSTRACT — should_fix

#### Q3 — diagnosis and replacement clause

Yes. R4-F1's “governed source bytes ... and its validator result”
(`docs/process_traces/2026-09-04-paper-i/06-magistrate-contract-rulings.md:25`)
is too abstract. It does not name the real schema, validator call inputs,
custody paths, or receipt replay; it also uses one formulation for a positive
whole-window record and a negative filesystem fact. Round 1 complied with its
surface grammar by wrapping invented bytes in invented validation metadata.

Replacement clause, verbatim:

> **F1 (replacement):** A before-comparison sentence is renderable only from a repository-defined positive evidence chain, never from a caller-authored projection, Boolean, validator-name string, result tuple, mapping, or rehashed bytes. For an excluded measurement window, the renderer or its non-bypassable path adapter must open a content-addressed `joulewise.idle_admission_whole_window_verdict.v1` row, prove that the same bytes occur exactly once in the bound `campaign_log.jsonl`, bind the row through a validated `joulewise.analysis_manifest.v3.prospective` and plan tree to the exact fixed `_v5` model, phase, bundle census, evaluation basis, and consumption semantics, and replay `whole_window_refusal_reasons`; the pre-stop lane must not require a finalized manifest. `joulewise.claim_verdicts.v1` has no `absent` outcome, so missing claim-verdict bytes are not authenticated evidence and must return `STOP_FILL` until a separately governed, content-addressed nonissuance/completion artifact and validator bind the expected verdict role, output path, campaign identity, terminal state, and issued reason. Every source and receipt crosses the boundary by path plus expected digest, every receipt is reopened and replayed rather than trusted as a caller object, and any missing, mismatched, ambiguous, unsafe, or validator-refused input returns `STOP_FILL` without professor-facing prose.

#### Q4 — ruling row (four sentences)

The only current positive before-comparison authority is a validated, non-admitted `joulewise.idle_admission_whole_window_verdict.v1` row bound through campaign custody and the prospective `_v5` pack; no normalized stop object or caller-created validator result has authority. `joulewise.claim_verdicts.v1` issues only its five registered outcomes, so a missing claim-verdict file is nonissuance, not an authenticated “verdict absent” artifact, and OR-01 must remain `STOP_FILL` unless a governed nonissuance/completion artifact is added. The renderer accepts only source paths with expected digests and replayable validator-receipt paths with their digests, using the prospective manifest for pre-finalization identity and a finalized manifest only on lanes where one can exist. Adopt the replacement F1 clause above and keep REFUSAL branch selection separate from authorization to print a before-comparison sentence.

## Residual risk

No current public receipt schema distinguishes “authentic row whose admission
failed” from “row whose provenance or structure failed” for this renderer
boundary. The proposed path contract therefore still needs a separately ruled
receipt schema/producer (or an in-command structured validator API) before the
implementation can safely render a whole-window stop; this consult does not
invent that wire as if it had already landed.
