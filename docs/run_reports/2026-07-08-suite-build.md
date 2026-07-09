# Run report — suite build: adjudication + P2-010a/b + P2-012/P2-020 engines (2026-07-08)

**Deliverable check (§0 sentence):** WORKING SUITE CODE ON MAIN — P2-010a
substrate + P2-010b smoke ladder + P2-012 phase-1 generators + P2-020
sentinel generator. **SHIPPED**: all four are merged to main (HEAD
`c752c30`), 732 tests green, live-verified on real MLX and via the CLI
mock flows, post-merge integration review clean.

## Product outcomes (all merged)

- **Adjudication (main `fadbd41` + `c2cfd99`):** all 37
  suite_implementation_research.md cross-check amendments dispositioned
  (Codex disposition draft → fresh Codex adversarial round → lead calls);
  binding pins D-044 (suite config identity: omission serialization +
  canonical effective-manifest hash), D-045 (substrate execution
  semantics, 9 pins), D-046 (AP-6 ids-native BOS-less sentinels), D-047
  (affine ladder pins); AP-5/AP-6 row amendments; bank sketch amendments;
  D-029/C-015 back-annotations (D-043 discipline). Amendments during the
  merge gate: D-047.2 k=25 accounting (`336b515`), D-045.1 order_seed
  signature (`024cec9`).
- **P2-010a substrate (PR #17, 4 commits):** `joulewise/suite.py`
  (manifest dataclasses, canonical effective manifest + sha256, marker
  vocabulary, ItemStatus + assignable subsets, pinned policy
  vocabularies, sentinel-gated duplicates, per-block level contiguity);
  `WorkloadProfile.suite_manifest_ref/sha256` with all pre-existing
  config hashes byte-identical; `SuiteRuntimeAdapter.run_suite(...,
  order_seed)` (controller-derived, never runtime-chosen); mock + MLX
  suite execution with per-item statuses incl. `fixed_budget_underrun`;
  `outputs/suite_items.jsonl` with response text, token-id hashes,
  `prompt_source`/`bos_present`; BundleReader suite accessors +
  validation (hash chain on the effective manifest, keyed marker
  pairing/nesting, group-marker requirements, ids-native expected-hash
  closure, status vocabulary policing incl. all status_counts, suite_end
  arithmetic, status-aware gating so failure bundles stay D-011-valid);
  reducer `suite_metrics` (gross-only, identifiability, both-floor seam
  `none_pending_P2-015`); strict rollup provenance
  (`joulewise.suite_prompt_token_ids.v1`, recomputed from the JSONL at
  strict validation); D-047.5 sampler pinning (both mlx_lm API homes);
  contracts docs (run_bundle_layout, adapter_contracts suite sections);
  stream ledger SUB-1..SUB-7.
- **P2-010b affine core (PR #18 → promoted via #20):**
  `joulewise/workloads.py` (derive_item byte-exact to report C §1.1,
  raw-completion render_prompt, ASCII-only scorer, audit-hash chain);
  smoke manifest `affine_smoke_v1` (levels {1,8,64}×8 + dedicated
  sentinel item at positions 0/25; k=25 distinct/26 executions; clean
  8-item level denominators); annotations sidecar (ground truth
  quarantined, C-004); mock example config. Envelope-gate analysis
  script is the named follow-on (queue row).
- **P2-012 phase-1 + P2-020 engine (PR #19):** `joulewise/gensuite` —
  sha256-ctr DRBG (golden-vector pinned), exact-shape grow/greedy-fill
  (full re-encode, fail-closed, no pad/truncate), six category
  generators (reasoning DAG integer-safe with independent
  parse-and-evaluate tests), five AP-6 sentinel conditions ids-native
  BOS-less (D-046), B7 tokenizer file-manifest identity (mandatory
  sidecar; no silent fallback), truthful provenance (GEN-3). Real-
  tokenizer manifest generation is a lead-side `.venv` follow-on.

## Verification evidence

- Merged main (`c752c30`): 732 tests OK (skipped=10), lead-run (617 at
  session start; +115). CI green both legs on every PR head and every
  post-review commit.
- Lead live gates (never delegated; 5 rounds): mock suite CLI
  run → `validate-bundle --strict` → `reduce` green; real MLX
  (Qwen2.5-1.5B + mock telemetry) suite runs at three code states incl.
  merged main — strict-valid, per-item energies with honest
  `not_resolvable` flags, `order_seed` byte-stable across the plumbing
  change, sampler `pinned: true` via `mlx_lm.sample_utils.make_sampler`;
  affine smoke end-to-end on the merged validator (26/26, statuses
  `capped` ×26 as expected for mock-at-budget under natural_eos).
- Three live-only catches, all fixed + regression-tested: cwd-relative
  manifest refs (SUB-5), missing strict rollup provenance (SUB-6),
  sampler API namespace (SUB-7). None was visible to 680+ unit tests.
- Post-merge integration review (fresh Codex, full-flow commands): NO
  CROSS-STREAM DEFECTS; AP-6 vocabulary join verified
  (`prompt_source: "token_ids"`, `bos_present: false` consistent between
  gensuite sidecars and adapter JSONL); repeated-seed drift test green.

## Process record

- Review stack: 2 Explore fact checks; Codex adjudication draft + fresh
  adversarial round (2 material amendments: effective-manifest hash;
  ids-native path as substrate requirement); 9 Codex lenses across 3
  units + 2 per stacked stream; 1 Opus fresh-eyes pass (Codex quota
  outage) that caught a real tokenize-window regression; 7-reviewer
  pre-merge oversight batch (10+ unique catches incl. two validation
  holes); 3 final-head passes; post-merge integration review. ~30 codex
  sessions + 3 Claude subagents.
- Codex quota outage (~13:10–14:0x, resolved by Ed's account upgrade):
  degraded mode ran lead line-reads + one Opus lens; recorded, no layer
  skipped — the oversight batch ran post-reset before any merge.
- Merge-gate process slip (lead): PR #18 merged into its stacked base
  `suite-substrate` instead of main (base never retargeted after #17).
  Recovered via promotion PR #20; #19 retargeted before touching.
  Lesson folded: stacked PRs get their base retargeted immediately after
  the parent merges, before any merge command.

## Restart instructions (next agent)

1. Suite work follow-ons, all [AGENT]: (a) envelope-gate analysis script
   (AFF-CHECKPOINT: E1–E4 + E5 advisory per D-047.3/4, sentinel-tag
   exclusion, distinct-item denominators); (b) lead-side real-tokenizer
   (`.venv`, Qwen2.5-1.5B) jw_mixed + sentinel manifest generation and
   commit (GEN-CHECKPOINT); (c) campaign-runner expected-vs-realized
   hash check for text-path items (B8's deferred half).
2. Quiet Window A ([QUIET-MAC]) unchanged: P2-015 expanded floors, then
   P2-006 2M. The affine smoke campaign (B=5, ~10–25 min) can ride a
   quiet-window tail after P2-015.
3. Window B: P2-019 q4 grid + P2-020 sentinel campaign, n sized from A.
4. Background chip pending: alignment-capture-outside-window fix
   (pre-existing D-013 concern, spun off). DONE same day — PR #21
   (council log C-018).

## Process trace appendix

- **Shape:** ADJ (adjudication) → Stream A (substrate, 3 units +
  oversight fixes) → Streams B/G parallel in worktrees off unit-1. Full
  tier all streams (measurement semantics). Report D not built against —
  deferred-binding dispositions. Machine state agent-heavy → quiet-lane
  tasks untouched.
- **Catches (unique, by layer):** Explore fact checks 2 (B10 moot, B1
  confirmed); adj attack round 4 (effective-hash identity gap the
  standout); unit lenses ~20 accepted across A1/A2/B1/G1 rounds (real
  validation/design defects, incl. D-011 completeness break, sentinel
  index mispairing, sentinel-tag denominator corruption, B7-not-recorded,
  ascii-tail enforcement); Opus fresh-eyes 1 major (tokenize-window
  bracketing regression — FakeClock-blind); LEAD LIVE GATES 3 (refs,
  strict rollup, sampler namespace) — historically consistent: the
  blocker-class catches live only at this layer; oversight batch 10+
  (status_counts holes, tamperable rollup digest, order_seed plumbing,
  group-marker vanishing, AP-6 evidence fields); final-head 2 (doc
  signature staleness; public sidecar-less builders); integration 0
  (clean). Lead triage amendments: sentinel-tag-gated duplicates (blanket
  uniqueness would break D-040), fh19 negative-test overreach rejected.
- **Deliberations:** A1 omission (consensus); A3 lead-stronger → attack
  amended to effective-hash (position refinement, accepted); B5 lead
  DEVIATED from draft (ids-native all-five; attack sustained with
  non-generalization caveat); C3 consensus. Affine sentinel redesign
  (lens catch → lead option (d): dedicated item, k=25) → D-047.2
  amendment.
- **Interventions:** Ed × 2 (max-Codex directive — adjudication drafting
  moved lead→Codex; quota upgrade mid-outage). Zero wake stalls across
  ~30 codex-runs. One lead process slip (PR #18 base retarget) —
  recovered same session, lesson folded.
- **Delegation calibration (schema v2):**

| id | to | unit | altitude | outcome | catches | lead-rework |
|---|---|---|---|---|---|---|
| explore ×2 | claude | fact sweeps | pinned-spec | good | 2 | none |
| adj-draft | codex | 37 dispositions + 8 argued calls | design-freedom | excellent | 1 | none |
| adj-attack | codex | adversarial review of lead batch | judgment-invited | excellent | 4 amendments | none |
| docs-batch | codex | adjudication record + AP/bank edits | pinned-spec | good | — | 1 gate fix (false provenance claim) |
| streamA u1-u3 | codex | substrate implementation | pinned+design | good ×3 | — | 1 (Opus finding fixes lead-implemented during outage) |
| streamB/G u1 | codex | affine + gensuite | design-freedom | good ×2 | 1 (prompt-defect flag) | none |
| lenses ×11 | codex | counterreview | design-freedom | good-excellent | ~20 accepted | triage only |
| opus lens ×1 | claude(opus) | outage substitute | judgment-invited | excellent | 1 major + 3 | none |
| fix rounds ×7 | codex | pinned fixes | pinned-spec | clean one-shot ×7 | — | none |
| oversight ×7 | codex | pre-merge gate | design-freedom | excellent | 10+ | triage only |
| final-head ×3+1 | codex | tail-commit passes | pinned-spec | good | 2 | none |
| integration ×1 | codex | cross-stream | pinned-spec | clean | 0 | none |

- **Prompt-defect log:** streamB test-spec error (cross-level value
  identity) — model correctly preferred the pinned report and flagged;
  fh19 criterion overreach (negative tests correctly pass None). Lesson:
  re-derive prompt-pinned test expectations from the spec, and scope
  "no caller passes X" criteria to positive paths.
- **Yield/spend:** ~30 codex sessions + 3 Claude subagents + ~5 lead
  live-gate rounds. The expensive-miss prevention cases: the
  effective-hash identity hole (would have let code-default changes
  alter semantics without changing run identity), the sentinel-tag
  denominator corruption (would have silently broken every AP-5 level
  claim), and the three live-only integration defects.

## §10 note (post-large-workload trigger)

The standing reassessment trigger fires (multi-PR merge session). Ran at
SCALED depth rather than the full 4-analyst workflow: C-016's full run
happened earlier the same day over the same logs, so a second full pass
would re-mine near-identical evidence. Scaled compliance: (a)
skill-usage entry finalized with folds applied same-session; (b)
supersession closure verified by the sweep (4 findings, all fixed
pre-commit); (c) calibration longitudinal: design-freedom delegation ran
excellent for the second consecutive session (adjudication draft, attack
round, oversight) — the runs-hot signal is now a trend, not an anecdote;
prompt-defect rows 2 (both lead-side spec-transcription errors); (d)
oversight dispositions all traced to commits or queue rows (P2-025, the
alignment chip); (e) layer overlap: the Opus outage substitute produced
1 major unique catch — evidence that a non-Codex fresh-eyes lens has
standalone value at the adapter-refactor tier, worth one deliberate
A/B in a future session before any standing role change; (f)
derivability: the stacked-PR lesson and outage pattern are folded where
a fresh agent will find them (multi-stream skill; skill-usage log).
