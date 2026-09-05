# C-027 Spec-Wave Adjudication (C-028 session, 2026-07-09)

Status: ADJUDICATED by the lead after a two-round advisory discussion
with gpt-5.6-sol (thread 019f4cfb-f1bb-76c3-813e-433c340860a7; the
advisor reviewed the lead's resume plan, then drafted per-question
rulings which the lead adjudicated row-by-row). WHERE A RULING BELOW
CONFLICTS WITH A SPEC'S BODY TEXT, THE RULING WINS; specs are not
re-edited item-by-item (their headers point here).

Rulings marked **[ED]** are compiled for Ed and are NOT yet decided —
implementation must not assume them.

## Headline rulings (H1–H7 from the lead's resume plan)

- **H1 (P2-039 guard factor):** ACCEPT g(n)=max(1, sqrt((10-1)/(n-1)))
  as a FROZEN, versioned OPERATIONAL SAFETY FACTOR — explicitly not a
  tolerance/confidence/power bound and never justification for reducing
  required n. The floor artifact records BOTH guarded and unguarded
  values. A preregistered n=10 diagnostic comparison may inform
  prospective reconsideration only; the factor cannot reopen after
  calibration data exists.
- **H2 (reducer version 0.3.0, no 0.2.0 projection):** ACCEPT only
  with: (a) a documented inventory establishing no retained/published
  0.2.0 artifact exists; (b) a D-030 amendment; (c) explicit version
  dispatch — legacy allowlist as-is, 0.3 exact, 0.2/unknown fail with a
  named "unsupported reducer version / re-reduction required" error.
  NAMED REVIEW CHECK for the P2-040 PR: the branch keys
  additive-absence tolerance on the PRESENCE of `summary_provenance`,
  not its recorded reducer version — a purported 0.3 summary omitting
  new governed fields could receive pre-0.3 tolerance. Fix or refute
  during review.
- **H3 (campaign-level cooldown gap):** ACCEPT fail-closed; P2-041 must
  SHIP the campaign-level recovery gate + raw provenance or remain
  fail-closed; P2-037 independently repeats the check.
- **H4 (D-050 revisit → D-064):** the compliance surface is a TRACKED
  per-session JSONL invocation snapshot, one row per invocation
  (MET-001 spec option 2). Run reports carry counts + a link; the
  codex-run observer index and workflow journals are raw substrate; the
  gitignored bridge manifest becomes optional local convenience. (The
  lead's run-report-summary-as-surface proposal was REJECTED in
  discussion: summarization is how ~100 invocations became zero
  auditable rows.)
- **H5 (P2-040 scope):** D-057/D-030 doc amendments, the
  run_bundle_layout update, the six-corpus regression unit test, and
  the P2-016(i) supersession note RIDE THE P2-040 CODE PR. Only
  ARC-6/FIX-7/FIX-8 defer to the remainder row. P2-040 is PARTIAL until
  the remainder lands.
- **H6 (DOC-008):** conversion deferred to a dedicated session; the
  kernel branch merges LAST, with the kernel refreshed at the final
  integrated head and an explicit NOT-AUTHORITATIVE-UNTIL-CONVERSION
  header.
- **H7 (review depth):** P2-040 gets two independent lenses
  (evidence-semantics/backward-compat + adversarial-tests/
  version-dispatch), a test-amplification pass, a core+IO interaction
  review, lead corpus-strict + mock-e2e gates, and a final-head.
  P2-039, RPT-001, DOC-008 get separate targeted reviews and separate
  PRs. RETRO-001 runs BEFORE the final integration gate.

## Per-spec rulings (advisor-proposed, lead-adjudicated: all ACCEPTED)

| Spec | Question | Ruling |
|---|---|---|
| Analysis trio | AP-2 multiplicity family | Four six-contrast families per model (estimand-local per D-053), not one m=24 family |
| Analysis trio | AP-2 confirmatory metrics | Freeze gross request, idle-sub request, gross prefill, gross decode; mean power/TTFT/token ratios stay exploratory |
| Analysis trio | LOO/randomization consequence | Verdict-changing LOO or randomization disagreement blocks L2/L3; magnitude-only influence → visible caveat |
| Analysis trio | B14 reason vocabulary | Exact closed v1 set appended to D-057; additions need a versioned amendment |
| Trio + P2-039 | Floor-schema alignment | The IMPLEMENTED `joulewise.detection_floor_artifact.v1` schema + typed resolver are authoritative; trio B3 amended to it, no aliases; comparative blocks own floor-contrast treatment; deterministic floor bounds default to no-cancellation |
| P2-038 | D-030 raw-to-trace amendment | Accept midpoint/bracket reconstruction for current era; legacy identity algorithm retained |
| P2-038 | Post-run idle sentinel (~5 s) | Accept, outside the measured window; update campaign runtime estimates |
| P2-038/039 | idle_drift_guard block | Required as a separate schema block before calibration data |
| P2-038 | Live closure | Software may land first; P2-038 incomplete until quiet-machine shakedown + backup to approved destination **[ED: P0-003 destination]** |
| P2-039 | Stack/condition identities | Hashes from exact artifacts; hashed condition-family definitions; no display-name wildcards |
| P2-039 | Two-model floor economics | Preserve two-model L2: floor coverage for BOTH stacks, revised de-duplicated bundle count before collection; if the quiet-window cost is rejected, the uncovered stack is capped at L1 explicitly **[ED: collection scope/time]** |
| SPLIT-AP | Primary estimand | CONFIRM the applied choice: composite gross, two already-powered warm nodes; others stay named sensitivities |
| SPLIT-AP | Dual-reference inference | Intersection–union rule ratified (beat both references, Holm-adjusted, above floor) |
| SPLIT-AP | D-062 clause propagation | One full normative clause at the shared field definition; pointers elsewhere |
| SPLIT-AP | Amortized provisioning variant | Omit from v1 (50/50 call recorded); later only with frozen horizon/denominator, descriptive L1 |
| SPLIT-AP | Pack-lint timing | Implementation queued now; required before registry freeze or split execution; does not block this integration |
| NV-GATE-2 | NV-3 unregistered backend | Hard-fail strict for unregistered production backends; explicit mock-only exemption |
| NV-GATE-2 | NV-4 process demotion | Demote on ANY surviving worker-started process incl. the sampler; file/dir cleanup failure stays quality-only |
| NV-GATE-2 | NV-2 cooldown ID | Linked ID when protocol-valid, else fresh valid ID + manifest linkage |
| NV-GATE-2 | NV-1 include_usage | Send first; on rejection retry without, label `stream_chunk_fallback`, per-token claims ineligible |
| DOC-008 | Mixed-lane REPRO rows | Split agent prep from external tail; no multi-lane rows |
| DOC-008 | P2-004/P2-005 lanes | `[AGENT]` now; hardware/access as explicit dependencies |
| DOC-008 | P2-016 granularity | One conservative parent row until a child is independently executable |
| DOC-008 | P2-006 interpretation gate | BOTH P2-037 and P2-041 required before L2 interpretation |
| P2-040 | New D-057 codes | `nonpositive_window_duration`, `idle_baseline_unrecorded` accepted exactly |
| P2-040 | `request` alias | Retained through schema v0.1 as idle-subtracted alias; removal only in v0.2 |
| P2-040 | warmup_seconds | IMPLEMENT (post-active-warmup settling; zero = current behavior) rather than delete — config-hash stability |
| P2-040 | Zero-window strict semantics | Reject only bundles CLAIMING successful measurement; honest failure records stay structurally strict-valid |
| P2-040 | FIX-5 scope | Zero-MAD stays forensic-only; LOO and floor/effect decisions live in P2-037/P2-039 |
| RPT-001 | Report source home | `docs/report_src/` permanent (root `report/` already means the bundle browser) |
| RPT-001 | n=3 representation | Raw points + mean + observed range; SD in T1; t-interval only in the audit artifact |
| RPT-001 | Claims-index authority | JSONL canonical; Markdown generated projection |
| RPT-001 | Stack IDs | RENAME `LEGACY-M3MAX-QWEN25-15B-MLX` → `LEGACY-M3MAX-QWEN25-1P5B-MLX` before the ID becomes durable |
| RPT-001 | Legacy L1 void disposition | Per peer-audit finding `01-F3` (`docs/process_traces/2026-09-04-peer-audit/01-full-base.md`) and ruling 17 Q7 (`docs/process_traces/2026-09-04-peer-audit/17-magistrate-final-ruling.md:49-51`), amend §7, §6.2 steps 3–5, §6.3, and §6.4 of `rpt-001_report_vertical_slice.md` to the void disposition: the profile is a voided historical demonstration; `voided-placeholder` is a legal build mode and `voided` is a legal claims-index status. The Markdown projection intentionally sanitizes even the exact-legacy grandfather row; the mechanical `PROJECTION_DRIFT` invariant is unchanged. |
| RPT/REPRO | Full-corpus CI | Scheduled/manually-triggered job after pack publication, never per-PR **[ED: publication/CI commitment]** |
| RPT-001 | Renderer/template | Defer until P1-008 supplies the submission target **[ED: evaluator input]** |
| REPRO-001 | Environment identity | Two-lock case ratified (Mac `.venv` + minimal system-Python analysis lock) |
| REPRO-001 | Release provenance | Tag the exact clean commit; refuse publication from a dirty tree **[ED: actual publication]** |
| REPRO-001 | Pack size | Three-bundle pack (incl. second 1.5B rep) **[ED: actual publication]** |
| MET-001 | MET-7 | Already satisfied by the applied D-054 amendment; do not duplicate |
| MET-001 | MET-3 disposition | "User-directed override, recorded retroactively, + recording failure" stands if the contemporaneous record is unambiguous; else escalate to Ed **[conditional]** |
| MET-001 | Audit/marking order | MET-5 audit → mechanical REV-3 markings; RETRO-001 closes in the same bookkeeping arc as the breach addendum |

## Ed-decision list (compiled; nothing below is assumed)

1. P0-003 external backup destination (E0; hard pre-Window-A gate).
2. Two-model floor-coverage economics: accept the added quiet-window
   cost for 122B floor cells, or explicitly cap 122B at L1.
3. Full-real-corpus CI job commitment (post pack publication).
4. Report renderer/template (rides P1-008 rubric/format capture).
5. REPRO pack publication acts: release tag + publishing the
   three-bundle pack externally.
6. D-060 stop-line ratification (still PROPOSED from C-027).
7. MET-3 override wording only if the record reads ambiguous (lead
   review found it unambiguous; flagged for transparency).

## Integration order (revised per advisory round 1)

Rebase every impl/* onto the merged spec head first. Then: docs tranche
(doc009+met001+ap-edit+repro001, one combined review) → P2-040 PR
(core+io, full H7 stack) → P2-039 PR → RPT-001 PR → RETRO-001 →
cross-stream integration review → DOC-008 kernel LAST (refreshed,
non-authoritative) → bookkeeping (D-064 entry, C-028 records, queue
PARTIAL labels, sweep, site).
