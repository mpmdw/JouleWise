# JouleWise Comprehensive Audit — Charter and Report

Status: CHARTER FROZEN (2026-07-13, post fresh-eyes Fable review — 3 blocking
amendments applied; the standalone keep-defender scans were cut on its
argument over the peer's round-2 design, dissent recorded in §9); findings
sections are filled as the audit executes. Pinned object: repository HEAD
`e3fc14a01ca047e779fa7924fdf128b25762d063` (steady state, suite 1387 OK).
Lane: [AGENT] throughout; no quiet-machine contact; the audit changes NOTHING
in the repository except this directory's contents and, at adjudication,
lead-promoted TASK_QUEUE rows.

Provenance: method co-designed by the Fable lead and Sol xhigh over the
bridge-protocol/v1.1 discussion lane (peer channel thread
`019f5ded-5f4d-77a0-8e63-d4fb26d93a4c`, 2 rounds, 2026-07-13; Sol's
responsibility-domain + seam-walk counter-proposal adopted over the lead's
21-cell matrix). Ed's directive: thorough audit before further building;
three seeking missions (overengineering, too much code, architecture
oversights) plus evidence-motivated passes; generous Fable overseer
coverage; ultracode authorized for execution; budget deprioritized —
duplication trims stand, coverage trims do not.

## 1. Purpose and outputs

Adjudicated keep / simplify / delete / fix verdicts over the whole
repository and a prioritized, queue-ready work-order list, BEFORE further
feature work. Durable outputs are EXACTLY two artifacts: this report and
`register.jsonl`. Scan receipts under `receipts/` are orchestration
evidence, not a new artifact class.

## 2. Decomposition

### M1/M2 responsibility domains (merged execution, two ordered lenses)

| D | Domain |
|---|---|
| D1 | Run lifecycle and evidence kernel: config, schemas, CLI, controller, clocks, bundles, provenance, validation |
| D2 | Platform boundaries: runtime, telemetry, transport, node client/worker, adapters |
| D3 | Campaign and workload orchestration: suites, generators, manifests, campaign runner |
| D4 | Reduction, analysis, uncertainty, and claim gates |
| D5 | Reporting, figures, packaging, privacy, site publication |
| D6 | Test portfolio: duplication, vacuity, fixture inflation, obsolete compatibility tests |
| D7 | Governance and process stack: plans, authorities, state kernel, bridge, generated status/site documents |

Each domain session runs lens order: M2 deletion-oriented inventory first
(definitions/uses, registrations, flags, duplication, redundant tests,
stdlib reimplementations), then M1 value challenge (abstraction payoff,
roadmap necessity, configuration cost, indirection, machinery-to-risk).
Findings may carry both mission tags. The D1, D4, and D7 scan prompts carry
an explicit KEEP-PRIOR paragraph (these domains carry the highest
mistaken-simplification cost); standalone opposing-prior scan sessions were
cut at charter review as duplicating §4's per-candidate keep-defender
refuters. D7 rows carry `author_conflict: true` (the audit's authors built
that stack); D7's M1 value lens measures value to the undergrad-capstone
deliverable, with process cost (session time, doc-maintenance burden, token
spend) admissible as evidence.

### M3 seam walks (cross-cutting, end-to-end)

| W | Walk |
|---|---|
| W1 | One-run lifecycle: config → controller/adapters → raw bundle → strict validation → reduction, including every failure and cleanup path |
| W2 | Campaign-to-claim: design/order → corpus → floors/uncertainty → aggregation/statistics → claims → figures/report |
| W3 | Local-to-remote and future-split evolution: local/SSH/node worker → schema evolution → offline replay/multi-node; concurrency, locking, cleanup, PROVISIONAL boundaries |
| W4 | Clean-clone-to-publication: installation/preflight → reproducible run → artifact regeneration → package/privacy/site (includes an EXECUTED clean-clone reproduction at the pinned HEAD; network/credential boundaries recorded, never substituted) |
| W5 | Authority-to-enforcement-to-test: decisions/contracts → code gates → tests/live gates → queue/status/public claims |

### Mandatory specialist pass — scientific and numerical validity

Two bounded examinations spanning W1/W2 (sound architecture can still
implement the wrong estimand): (a) measurement/reduction validity — units,
time bases, integration, idle subtraction, denominators, token provenance,
boundary alignment, missingness/exclusion handling; (b) statistical/claim
validity — estimands, dependence, ratios, multiplicity, floor logic,
uncertainty propagation, sensitivity, claim downgrades, independent-oracle
quality of tests. The measurement-validity examination MUST sample at least
one retained real corpus bundle under `runs/` (untracked; §6 sampling
clause) — a wrong estimand baked into recorded evidence is invisible to
code-only review.

### Coverage rule

Batch 0's inventory emits the AUTHORITATIVE tracked-file → domain (+walk or
exclusion) assignment table into §7 BEFORE any scan launches, and every scan
prompt carries its explicit file manifest — scanners never choose their own
scopes. Stray assignments pinned at charter review: `site_capsule/` (live
server+client+lakebed.json) → D5; `.github/workflows/ci.yml` and
`pyproject.toml` and `env/*` → D1 with W4; `scripts/backup_runs.sh` → D1;
`.mcp.json`, `.codex/config.toml`, `.claude/{agents,commands,skills}`,
`.agents/skills` → D7; `LICENSE` → excluded (legal boilerplate). Generated mirrors are checked against their
sources/generators and sampled, not line-reviewed; historical records
(ledgers, dated reports, decision/council entries) are evidence, not
current operating surfaces.

## 3. Register contract (`register.jsonl`, one JSON object per row)

- `row_type`: `finding` | `work_order`.
- Finding rows: `id`, `state` (open/verified/refuted/accepted/rejected/
  deferred), `mission_tags` [M1|M2|M3|SCI], `domain`, `seams` [],
  `dedupe_of`, `finding`, `consequence`, `counterevidence`, `severity`
  (blocker|should-fix|nit), `proposed_disposition` (keep|simplify|delete|
  fix|investigate), `evidence_refs` [] (file:line, command+result, behavior
  trace, contract ref, or bounded absence-search description),
  `verification` {method, outcome, reviewer_family, residual_uncertainty},
  `adjudication` {decision, rationale}, `work_order_id`.
- Work-order rows: `id`, `finding_ids` [], `action`, `bounded_scope`,
  `non_goals`, `authority`, `dependencies`, `lane`, `acceptance_evidence`,
  `verification_command`, `effort`, `state`.
- Drop rule: no auditable evidence → dropped at consolidation. A multi-file
  trace, executed behavior, or bounded absence search IS evidence; a
  missing single file:line is not a drop reason.
- Several findings SHOULD collapse into one root-cause work order.
- Scan receipts (`receipts/<scan-id>.json`): scope examined, exclusions,
  checks performed, uncertainties, `rows: []` — a clean scan is
  distinguishable from an incomplete one; zero-finding outcomes land in the
  coverage table, never as fake findings.
- Writer discipline: register ids are scan-prefixed at birth (`D3-007`,
  `W2-011`, `SCI1-003`) so `dedupe_of` never dangles; exactly ONE writer
  touches `register.jsonl` (the lead, with the register-integrity Fable
  agent acting on its behalf) — every other agent returns rows inside its
  receipt or reply; state transitions are lead-applied edits; receipts are
  immutable once written.

## 4. Verification and adjudication

Scanners assign only the `severity` enum; verification TIERS are assigned
at consolidation by the lead using consequence, confidence, and
reversibility (a should-fix deleting a measurement safeguard tiers UP):

- Tier 3 — claim/evidence/data-loss blockers and DESTRUCTIVE core
  simplifications: two evidence methods, executable repro where feasible,
  cross-family (Fable) overseer verification, lead ruling.
- Tier 2 — should-fix: one strong confirmation; add a refuter when
  confidence or reversibility is poor. Per Ed's generosity directive, EVERY
  unique should-fix root cause gets cross-family Fable verification (the
  calibration sample is subsumed at 100%).
- Tier 1 — low-risk dead code/duplication: definition/use/registration
  trace + relevant focused checks.
- Tier 0 — nits: no standalone verification; a nit survives only by riding
  an accepted work order without expanding its scope.

Keep-defender refuters ("defend keeping this") run for EVERY consequential
simplification/deletion candidate. Blocker definition (reserved): evidence
corruption/loss, claim invalidation, failure of the canonical reproducible
flow, or an architecture defect making the next roadmap gate unsafe.
"Large" and "complicated" are not blockers. Cross-mission dedupe precedes
verification. The lead adjudicates every disposition; dissent is recorded
in the row.

Deep dives (0–3): commissioned by the lead only with a named unresolved
decision and expected output — triggers are an unresolved consequential
decision, conflicting evidence, required dynamic behavior, or one root
cause crossing multiple flows. Finding COUNT is not a trigger.

## 5. Execution topology (dynamic Workflow; ultracode authorized)

- Batch 0: repo-wide mechanical inventory (one-liners only; LOC/imports/
  CLI-config surface; routing context, never evidence) emitting the §7
  file→domain/walk assignment table and the per-scan file manifests. Runs
  BEFORE any scan; the lead ratifies the manifests.
- Batch 1 (parallel): 7 domain scans (Sol high; D1/D4/D7 prompts carry the
  keep-prior paragraph) + 5 seam walks (Sol xhigh) + 2 scientific-validity
  examinations (Sol xhigh) + W4's executed clean-clone reproduction.
  ≈ 14-15 Sol sessions.
- Batch 2: 2 Sol xhigh consolidations (excess/root-cause dedupe;
  architecture/science synthesis) emitting deduped register rows.
- Batch 3 (generous Fable overseer layer): 3 bounded Fable sweeps over
  consolidated packets (packet files are EMITTED BY the Batch 2
  consolidators; the lead assigns packets to sweeps) (scientific validity + evidence integrity;
  architecture/reproducibility/roadmap fitness; deletion/right-sizing) —
  verifying every prospective blocker, every claim-affecting or
  evidence-loss finding, every core-control deletion, and 100% of unique
  should-fix root causes; plus a Fable register-integrity agent (schema,
  dedupe correctness, evidence_refs resolvable); plus Sol xhigh refuters
  batched by risk (evidence/claim integrity; destructive simplification/
  roadmap fitness) and keep-defenders per §4. Any substantive NEW issue surfaced by a Batch 3
  sweep or refuter routes through the normal finding/verification path —
  same rule as the Batch 5 critic; that bounds recursion everywhere.
- Batch 4: 0–3 lead-commissioned deep dives.
- Batch 5: lead adjudication, dependency ordering, queue promotion; ONE
  Fable completeness critic (negative-space enforcement: modality not run,
  claim unverified, cell without recorded outcome, work order without
  acceptance evidence — emits gaps, not findings); a critic-reported gap
  pauses report freeze for one bounded closure-and-recheck loop, and any
  newly surfaced substantive issue routes through the normal
  finding/verification path.

Effort pins: domain/keep-defender scans high; walks, science, refuters,
consolidations xhigh; NO ultra (no Sol-side subagent spawning). Scan
prompts carry the context-capsule discipline (authority anchors, pinned
HEAD, settled-vs-challengeable) and the register row schema inline;
scanners return rows + receipt, not prose.

## 6. Negative space (admitted up front; finalized at close)

- Pinned to `e3fc14a…`; says nothing about later changes.
- No agent audit validates sensor truth, quiet-machine behavior, or live
  NVIDIA/Orin/remote operation; PROVISIONAL stays PROVISIONAL.
- Future empirical validity cannot be certified before the relevant corpus
  exists; methods and enforcement only.
- Grep/import/coverage cannot alone prove code dead where CLI dispatch,
  plugins, or external consumers may exist.
- Clean-clone verification is bounded by network, credentials, hardware,
  optional dependencies; unresolved boundaries are reported, not papered
  over.
- Sol scanners, Sol refuters, Fable overseers, and the lead are correlated
  reviewers; family diversity mitigates, does not eliminate.
- The audit makes no fixes; work-order acceptance must be revalidated as
  earlier fixes alter later assumptions.
- Ignored caches, external evidence stores, immutable raw corpora are
  outside tracked-source completeness unless explicitly sampled.
- The UNTRACKED half of the process stack (`~/.claude` skills,
  `~/.local/bin/codex-run-v3`, personal wrappers) is out of scope: D7's
  verdicts cover the TRACKED governance surface only and cannot certify
  the orchestration stack as a whole.

## 7. Coverage map

Batch 0's ratified census is 443 tracked files = 276 domain-assigned + 167
excluded.  The later ratification moved
`docs/reviews/2026-07-10-hardening-adjudication.md` into D7/W5 and sampled the
generated RPT-001 evidence in SCI2; those ratified figures supersede the
pre-ratification 275/168 draft still visible in `manifests/inventory.md`.
Ground truth: `manifests/RATIFICATION.md`, the explicit manifests under
`manifests/`, and the immutable receipts under `receipts/`.

The table accounts for all 15 Batch-1 receipts.  “Manifest files” is the
authoritative manifest size, not the larger number of authority or bounded
call-follow files a scanner sometimes recorded in `scope_examined`.  SCI2 was
the chartered prompt-assembled exception (49 files); W4-exec was an executed
companion over the pinned clone, not a second line-review manifest.  “Blockers”
counts rows whose scan-time `severity` was `blocker`, not environmental
limitations in each receipt's `uncertainties` array.

| Scan | Domain / walk | Manifest files | Rows emitted | Blockers | Receipt |
|---|---|---:|---:|---|---|
| D1 | Run lifecycle and evidence kernel | 30 | 7 | 0 | `receipts/D1.json` |
| D2 | Platform boundaries | 16 | 8 | 0 | `receipts/D2.json` |
| D3 | Campaign/workload orchestration | 32 | 5 | 0 | `receipts/D3.json` |
| D4 | Reduction, analysis, uncertainty, claims | 33 | 4 | 0 | `receipts/D4.json` |
| D5 | Reporting, packaging, privacy, site | 36 | 6 | 0 | `receipts/D5.json` |
| D6 | Test portfolio | 72 | 3 | 0 | `receipts/D6.json` |
| D7 | Governance/process stack (ratified) | 57 | 7 | 0 | `receipts/D7.json` |
| W1 | One-run lifecycle | 30 | 6 | 4: W1-001..W1-004 | `receipts/W1.json` |
| W2 | Campaign-to-claim | 40 | 5 | 2: W2-001, W2-002 | `receipts/W2.json` |
| W3 | Local-to-remote/future-split | 14 | 7 | 1: W3-001 | `receipts/W3.json` |
| W4 | Clean-clone-to-publication | 34 | 7 | 1: W4-001 | `receipts/W4.json` |
| W4-exec | Executed clean-clone companion | n/a (pinned clone; W4 companion) | 4 | 0 | `receipts/W4-exec.json` |
| W5 | Authority-to-enforcement-to-test | 19 | 7 | 0 | `receipts/W5.json` |
| SCI1 | Measurement/reduction validity; ratified W1 ∪ D4 | 62 | 4 | 1: SCI1-001 | `receipts/SCI1.json` |
| SCI2 | Statistical/claim validity; prompt-assembled | 49 | 5 | 1: SCI2-001 | `receipts/SCI2.json` |
| **Total** | **15 receipts** | **13 manifest cells + 2 chartered companions** | **85** | **10** | `receipts/` |

No cell was a zero-row scan.  The exclusions and negative space in §6 still
bind: these receipts do not promote fixture evidence to live hardware evidence,
do not certify sensor truth or quiet-machine behavior, and do not extend the
pinned-tree audit to later code.  Each receipt's `uncertainties` field is the
cell-specific blocker/boundary record.

## 8. Findings synthesis

### 8.1 Register accounting and operative findings

`register.jsonl` contains 101 rows: 61 accepted finding rows and 40 work-order
rows.  Dedupe leaves 43 operative findings and 18 accepted-merged finding rows.
Among the operative set there are 20 tier-2 findings, 22 tier-3 findings, and
one record-only nit with no standalone tier.  There is no operative tier-1
finding: the register's one tier-1 verified row, C1-018, merged into C2-034.
Operative proposed dispositions are 30 fix, 11 simplify, one delete, and one
keep.  All counts and text below derive from `register.jsonl`; packet paths are
called out where a ruling amended the register.

#### Tier 2 — 20 operative findings

| Finding | Domain / seam | Operative issue | Disposition |
|---|---|---|---|
| C1-011 | D3 | `run_campaign.py` concentrates policy and lifecycle code, but no current defect was shown. | Defer-roadmap → WO-033 |
| C1-012 | D3 | Planned split/KV commands lack queue owners, while the packs already label them PLANNED. | Defer-roadmap → WO-034 |
| C1-013 | D4 | The P2-038 closed reason vocabulary omits an emitted fail-closed reason. | Fix → WO-025 (landed) |
| C1-020 | D6 | Security/clock regressions pinned private helpers rather than public behavior. | Fix → WO-026 (landed) |
| C1-025 | D7 | `codex-watch` was unreferenced in the tracked operating surface and depended on private formats. | Delete after operator confirmation/replacement → WO-027 (landed) |
| C2-004 | W1 | Aggregate computation preceded incremental-manifest persistence, leaving a narrow interrupt window. | Fix → WO-028 (landed) |
| C2-007 | W2 | Missing prompt-token evidence failed open as a modality exemption. | Fix → WO-011 (landed) |
| C2-008 | W2 | The diagnostic HTML report omitted strict/evidence state and could imply readiness. | Fix → WO-029 (landed) |
| C2-009 | SCI2+W2 | RPT-001 labeled configured output budgets as runtime observations. | Fix → WO-014 (landed) |
| C2-011 | W3 | The v1 node payload union cannot carry a future split-transfer payload. | Defer-roadmap → WO-035 |
| C2-012 | W3 | Remote node/GPU launches lack ownership and retry/idempotency discipline. | Defer-roadmap → WO-036 |
| C2-017 | W4 | The release chain lacked one executable non-secret clean-clone gate. | Fix → WO-019 (landed) |
| C2-020 | W4+W4X | Analysis installation/locking was incorrect and under-bounded. | Fix → WO-030 (landed) |
| C2-023 | D7+W4X+W5 | Reader-facing current-state and decision-index surfaces lacked an enforced freshness owner. | Fix → WO-031 (landed) |
| C2-026 | SCI1 | A JouleWise-derived MHz value was advertised as Hz; rich telemetry itself must stay verbatim. | Fix → WO-007 (landed) |
| C2-027 | SCI2 | Threshold sensitivity used a D-047-invalid premise and AP-5 lacked a traceability pointer. | Fix → WO-032 (landed) |
| C2-028 | D1 | `default=str` silently destroyed metadata type/value provenance. | Fix → WO-023 (landed) |
| C2-032 | D5 | Report and publication pipelines used different bundle-tree identity folds. | Fix → WO-015 (landed) |
| C2-034 | D5 | The site emitted unused live payload fields; page trimming needs a retained-route/value review. | Defer-roadmap → WO-039 |
| C2-036 | D7 | Review/process work lacked numeric spend bands and a named-failure bar. | R2 ruling → WO-022 (landed; `packets/ed-rulings.json#R2`) |

#### Tier 3 — 22 operative findings

| Finding | Domain / seam | Operative issue | Disposition |
|---|---|---|---|
| C1-005 | D2 | Mock and MLX duplicated suite-control policy while the mock oracle had to remain independent. | Simplify → WO-008 (landed) |
| C1-010 | D3 | Manifest policy fields mixed enforced, descriptive, reserved, and removable semantics. | R4 per-field ruling → WO-009 (landed; `packets/ed-rulings.json#R4`) |
| C1-014 | D4 | `claims_lint` duplicated a fail-closed engine validator, creating maintenance/false-rejection risk. | Simplify with C2-022 → WO-013 (landed) |
| C2-001 | W1+W3 | Destructive cleanup could precede durable evidence custody. | Fix → WO-001 (landed) |
| C2-002 | D1+W1 | Independently maintained validity rules allowed contradictory success/admission states. | R3 admission-state ruling → WO-002 (landed; `packets/ed-rulings.json#R3`) |
| C2-003 | D2+SCI2+W1 | Configured output intent substituted for designated, enforced realized-output evidence. | Fix → WO-003 (landed) |
| C2-005 | SCI2+W2 | Floor resolution was neither independently consumable nor bound to bundle bytes/metrics. | Fix → WO-004 (landed) |
| C2-006 | D3+D4+SCI2+W2 | Frozen sample-size authority was fragmented and permitted incompatible authored paths. | Simplify/fix → WO-012 (landed) |
| C2-010 | W3 | Remote results lacked version and per-dispatch correlation validation. | Fix with C2-014/C2-015 → WO-010 (landed) |
| C2-013 | W3 | NVIDIA PROVISIONAL status was not machine-enforced at claim admission. | Defer-roadmap → WO-037 |
| C2-014 | D2+W3 | Arbitrary remote identifiers could reach recursive cleanup paths. | Fix with C2-010/C2-015 → WO-010 (landed) |
| C2-015 | W3 | SSH stderr heuristics could suppress authoritative status recovery. | Fix with C2-010/C2-014 → WO-010 (landed) |
| C2-016 | D5+W4 | Full capstone regeneration depended on undeclared machine-local evidence and paths. | Controlled/internal default → WO-017 plus mechanical WO-040 (landed; court T06) |
| C2-018 | D5+W4+W4X | Ambient Marked/Lakebed tooling made suite/publication behavior environment-dependent. | Simplify/pin → WO-018 (landed) |
| C2-021 | D7+W5 | State-kernel migration claimed completion without authority parity. | R1 choice A → WO-021 (landed; `packets/ed-rulings.json#R1`) |
| C2-022 | W5 | Claims validators and governed-surface selection disagreed. | Fix with C1-014 → WO-013 (landed) |
| C2-024 | SCI1 | Powermetrics interval support was discarded in active and idle estimands. | Fix → WO-005 (landed) |
| C2-025 | SCI1 | Phase-marker missingness/overlap failed open across stream identities. | Fix → WO-006 (landed) |
| C2-029 | D1 | Bundle provenance could not distinguish clean, dirty, unknown, or changed-during-run source. | Capture in WO-016 + T11 claim exclusion in WO-004 (landed) |
| C2-030 | D2 | Remote ownership was split between unused public surface and duplicated lifecycle helpers. | Defer-roadmap → WO-038 |
| C2-033 | D5 | Publication preflight computed an unused full private-tree inventory. | Simplify → WO-024 (landed) |
| C2-035 | D7 | Normative bridge wire/ceremony policy was duplicated beyond permitted enforcement-boundary repetition. | Simplify → WO-020 (landed) |

#### Record-only, no standalone tier — 1 operative finding

| Finding | Domain / seam | Operative issue | Disposition |
|---|---|---|---|
| C2-019 | W4 | Fresh-publisher ownership/bootstrap is already diagnosed; platform account ownership cannot be transferred by a secret-free repo document. | Accepted-no-fix, keep; no work order |

The 18 accepted-merged rows remain in the register for provenance and are not
silently dropped.  This mapping accounts for every non-operative finding row:

| Merged row | Operative row | Merged row | Operative row | Merged row | Operative row |
|---|---|---|---|---|---|
| C1-001 | C2-002 | C1-002 | C2-028 | C1-003 | C2-029 |
| C1-004 | C2-030 | C1-006 | C2-030 | C1-007 | C2-014 |
| C1-008 | C2-003 | C1-009 | C2-006 | C1-015 | C2-032 |
| C1-016 | C2-033 | C1-017 | C2-016 | C1-018 | C2-034 |
| C1-019 | C2-018 | C1-021 | C2-021 | C1-022 | C2-035 |
| C1-023 | C2-036 | C1-024 | C2-023 | C2-031 | C1-005 |

### 8.2 Work-order landing and deferred-roadmap ledger

All 40 work-order rows are accounted here.  The register's row-local lifecycle
values are the adjudication/dispatch snapshot; landing status below is reconciled
to this integration tree, the wave topology in `packets/fix-streams.json`, the
court amendments in `packets/fable-court-holdings.json`, and the ruled specs in
`packets/ed-rulings.json`.  Every stream, bench, and ruled/Fable order is LANDED:
33 landed and 7 deferred-roadmap.

| Landing group | Work orders (complete list) | Current-tree evidence |
|---|---|---|
| S1 | WO-023, WO-001, WO-002, WO-003, WO-004, WO-005, WO-006, WO-007, WO-008, WO-009, WO-010, WO-011 (12) | terminal stream commit `f664d69`; per-order commits `6abdf6c` through `f664d69` |
| S2 | WO-032, WO-012, WO-013, WO-014, WO-015, WO-016, WO-017, WO-029, WO-040 (9) | terminal stream commit `b23b262`; WO-040 `2cc7c57` |
| S3 | WO-018 (1) | `2b4b3a6` |
| S4 | WO-019, WO-031 (2) | `7b1299c`, `0de4cea` |
| S5 | WO-020 (1) | `b1f3aac` |
| Bench | WO-024, WO-025, WO-026, WO-027, WO-028, WO-030 (6) | bench batch `dd2c9f1`; WO-027 `e24f26a` + `3e0e928`; final-wave tree `0de4cea` |
| Ruled / Fable route | WO-021, WO-022 (2) | R1 `c7ee7ca`; R2 `3e9f76b`; `packets/ed-rulings.json` |
| **Landed total** | **33** | **all non-roadmap work-order ids** |

The seven deferred orders are queue-promotion material, not incomplete wave
work (`packets/fix-streams.json`, final global note).  Their row actions provide
the promotion triggers; the pointers below say where each must enter the live
queue without pretending it is ready now.

| Deferred order | Finding | Queue-promotion pointer / trigger |
|---|---|---|
| WO-033 | C1-011 | Promote immediately before campaign-scale or split/multi-node work first forces edits to `scripts/run_campaign.py`; preserve the full campaign parity portfolio (`register.jsonl#WO-033`). |
| WO-034 | C1-012 | Promote when Phase-3 split work is scheduled, alongside the current `SPLIT-AP`/`P3-001b` sequence, before any PLANNED pack command is treated as executable (`register.jsonl#WO-034`). |
| WO-035 | C2-011 | Promote before the first split-transfer task or wire-version extension is implemented (`register.jsonl#WO-035`). |
| WO-036 | C2-012 | Promote before retries or concurrent campaigns introduce shared node/GPU ownership (`register.jsonl#WO-036`). |
| WO-037 | C2-013 | Promote into the P2-005/NV-GATE-2 code-now path before, never after, live promotion; the promotion receipt must be non-self-asserted (`register.jsonl#WO-037`; `packets/pa2-out.md`). |
| WO-038 | C2-030 | Promote at the multi-node roadmap decision, before consolidating or deleting any public transport/lifecycle surface (`register.jsonl#WO-038`). |
| WO-039 | C2-034 | Promote at the next explicit site-capacity/right-sizing decision; first record the retained route/page inventory and value-versus-bytes review (`register.jsonl#WO-039`). |

### 8.3 Mandatory Ed-facing rejected, narrowed, amended, and ruled ledger

**Zero findings were rejected at any layer.**  The Fable layer returned 46
confirmed, 15 narrowed, and 0 refuted verdicts; Sol final returned 7 proceed,
30 amend, and 0 reject verdicts; the court returned 11 conclusion-amended, one
conclusion-stands, and 0 overturned holdings.  The lead register therefore
retains all 61 findings as accepted or accepted-merged.  Because D7 was authored
by this audit's operators, this ledger exposes every narrowing/amendment/ruling
to Ed, including changes outside D7; nothing was silently self-dismissed.

#### Fable verifier narrowings — 15

Source: `packets/fable-verdicts.json`.

| Finding | What changed at the Fable layer | Source |
|---|---|---|
| C1-008 | Limited the defect to future spike reruns/3.0.2 reuse; the retained 64/64 live verdict was not undermined, and the row merged into C2-003. | `packets/fable-verdicts.json#C1-008` |
| C1-009 | Recast a breached lint requirement as an explicitly deferred but unowned enforcement implication; merged into C2-006. | `packets/fable-verdicts.json#C1-009` |
| C1-011 | Recast file concentration from a present defect to a roadmap-conditioned, behavior-preserving refactor. | `packets/fable-verdicts.json#C1-011` |
| C1-012 | Recast absent planned commands as roadmap sequencing debt, not current operator deception; preserved the packs. | `packets/fable-verdicts.json#C1-012` |
| C1-014 | Removed current claim-integrity exposure because validators union fail closed; retained maintenance and future false-rejection risk. | `packets/fable-verdicts.json#C1-014` |
| C1-022 | Removed already-fixed effort-policy duplication and retained only excess wire/ceremony restatement beyond D-065 exceptions. | `packets/fable-verdicts.json#C1-022` |
| C1-023 | Acknowledged D-060 and risk-scaled review already exist; narrowed the gap to numeric budgets and spend/deliverable enforcement. | `packets/fable-verdicts.json#C1-023` |
| C2-004 | Reduced evidence-loss framing to a narrow interrupt-window/recoverable discovery defect because aggregation is non-raising. | `packets/fable-verdicts.json#C2-004` |
| C2-017 | Limited the release gap to missing package construction and executable non-secret seams; Phase-5 quickstart work was already tracked. | `packets/fable-verdicts.json#C2-017` |
| C2-019 | Downgraded to a record-only nit/no-fix because diagnosis already exists and account-bound ownership cannot be solved in Git. | `packets/fable-verdicts.json#C2-019` |
| C2-022 | Removed warning-only prose as a defect and reframed the schema conflict as a loud future deadlock, not a silent CI bypass. | `packets/fable-verdicts.json#C2-022` |
| C2-026 | Confined the false-Hz issue to JouleWise's derived field; preserved rich telemetry verbatim and removed present numerical-claim harm. | `packets/fable-verdicts.json#C2-026` |
| C2-027 | Found existing threshold rationale and narrowed the gap to sensitivity/robustness plus AP-5 traceability (later corrected further by Sol). | `packets/fable-verdicts.json#C2-027` |
| C2-035 | Limited bridge duplication to nonuniform wire/ceremony restatement and preserved the D-065 enforcement-boundary exemption. | `packets/fable-verdicts.json#C2-035` |
| C2-036 | Acknowledged D-060's freeze and narrowed the gap to numeric bands, spend ceilings, and a named-failure bar. | `packets/fable-verdicts.json#C2-036` |

#### Sol-final amendments — 30

Source: `packets/sol-final-verdicts.json`.  The seven proceed rows were C1-011,
C1-013, C1-014, C1-020, C2-006, C2-014, and C2-033; they needed no amendment.

| Finding | What changed at Sol final | Source |
|---|---|---|
| C1-005 | Mechanically protected mock-oracle independence with literal contract fixtures instead of shared-helper parity alone. | `packets/sol-final-verdicts.json#C1-005` |
| C1-010 | Required a lead per-field semantics ruling, versioned compatibility, and retained-manifest/hash tests before implementation. | `packets/sol-final-verdicts.json#C1-010` |
| C1-012 | Removed the out-of-scope D3-005 pruning rider; any future pruning needs its own migration/retention proof. | `packets/sol-final-verdicts.json#C1-012` |
| C1-025 | Replaced “orphaned” with tracked-surface evidence, and required Ed confirmation plus a live-visibility replacement before deletion. | `packets/sol-final-verdicts.json#C1-025` |
| C2-001 | Added explicit durable-custody acknowledgement, adapter/test scope, and interrupt-preservation requirements. | `packets/sol-final-verdicts.json#C2-001` |
| C2-002 | Replaced an overbroad cross-product with three separate parity matrices plus positive status fixtures. | `packets/sol-final-verdicts.json#C2-002` |
| C2-003 | Corrected the finding to repair existing realized fields, retain per-item suite outcomes, and verify emitted token evidence. | `packets/sol-final-verdicts.json#C2-003` |
| C2-005 | Required distinct calibration/consumer bundles, complete-byte/metric binding, campaign-order binding, and CLI tests. | `packets/sol-final-verdicts.json#C2-005` |
| C2-007 | Made prompt-evidence exemptions authoritative validated policy; neighboring annotations cannot self-exempt. | `packets/sol-final-verdicts.json#C2-007` |
| C2-008 | Chose the diagnostic-browser design: show invalid bundles, never imply readiness, and co-display provenance/unknowns. | `packets/sol-final-verdicts.json#C2-008` |
| C2-009 | Sealed rpt001-v1, required a complete v2, and forbade inferring stop reason from configured-cap equality. | `packets/sol-final-verdicts.json#C2-009` |
| C2-010 | Added a unique echoed dispatch token, complete identity validation, wire-version decision, and matching-stale-response test. | `packets/sol-final-verdicts.json#C2-010` |
| C2-013 | Replaced self-asserted promotion with a commit/protocol-bound receipt plus transport-derived execution classification. | `packets/sol-final-verdicts.json#C2-013` |
| C2-016 | Split clean-clone assembly/checking from full evidence re-derivation and required controlled/internal labeling absent a supplied pack. | `packets/sol-final-verdicts.json#C2-016` |
| C2-017 | Made WO-017/WO-018 hard dependencies and defined dry-run as real temporary execution with named external boundaries. | `packets/sol-final-verdicts.json#C2-017` |
| C2-018 | Required a pinned artifact-identity policy, deterministic canonical size gate, and separate ambient integration gate. | `packets/sol-final-verdicts.json#C2-018` |
| C2-021 | Exposed complete-vs-narrow to Ed, requiring either authoritative generic gates/oracles or an honest manual-authority declaration. | `packets/sol-final-verdicts.json#C2-021` |
| C2-022 | Added version-aware authority cases, fail-closed hybrid handling, differential union tests, and correct governed-surface selection. | `packets/sol-final-verdicts.json#C2-022` |
| C2-023 | Bound freshness to the landing head and separated structural completeness from volatile facts. | `packets/sol-final-verdicts.json#C2-023` |
| C2-024 | Expanded reducer-version/dispatch scope and froze interval-edge plus weighted variance/ESS semantics before implementation. | `packets/sol-final-verdicts.json#C2-024` |
| C2-025 | Defined pairing by phase-stream/node identity, rejecting illegal same-stream pairs while allowing distinct-node concurrency. | `packets/sol-final-verdicts.json#C2-025` |
| C2-026 | Chose additive `gpu_freq_mhz_mean`, retained the legacy mislabeled alias, and preserved rich records verbatim. | `packets/sol-final-verdicts.json#C2-026` |
| C2-027 | Corrected the record: sensitivity existed but used a D-047-invalid pseudo-replication premise; empirical work stays deferred to data. | `packets/sol-final-verdicts.json#C2-027` |
| C2-028 | Pinned one deterministic recursive quarantine contract covering cycles, keys, non-finite values, and diagnostics. | `packets/sol-final-verdicts.json#C2-028` |
| C2-029 | Moved source capture to writer creation, added end-state comparison, exhaustive source states, and hard claim exclusion. | `packets/sol-final-verdicts.json#C2-029` |
| C2-030 | Kept `node_worker` self-contained, required within-file dedupe, and forbade deleting public methods on repo absence alone. | `packets/sol-final-verdicts.json#C2-030` |
| C2-032 | Preserved the legacy tab identity, emitted NUL identity only in a new version, and required cross-pipeline equality. | `packets/sol-final-verdicts.json#C2-032` |
| C2-034 | Limited deletion to proven-unused live fields and required per-page retention, route, deep-link, and provenance checks. | `packets/sol-final-verdicts.json#C2-034` |
| C2-035 | Corrected the exact duplicate surfaces and required a clause inventory, canonical snippets, and direct drift-check execution. | `packets/sol-final-verdicts.json#C2-035` |
| C2-036 | Kept caps as an Ed-ratification proposal and required explicit accounting, denominators, boundaries, exceptions, ownership, and consequences. | `packets/sol-final-verdicts.json#C2-036` |

#### Fable court holdings — 11 amended, 1 stands

Source: `packets/fable-court-holdings.json`.  R3 below is the lead ruling that
closed T02 and is stored at `packets/ed-rulings.json#R3`.

| Holding | Result | What changed | Source |
|---|---|---|---|
| T01 / C2-001 | Amended | Added an on-disk remote-retention/reclamation mechanism, leak-side test, and WO-001↔WO-010 token-compatible seam note. | `packets/fable-court-holdings.json#T01` |
| T02 / C2-002 | Amended + R3 | Required an explicit nullable-energy ruling and retained-corpus sweep; R3 chose SUCCEEDED plus distinct energy-evidence-absent admission, with energy claims fail-closed. | `packets/fable-court-holdings.json#T02`; `packets/ed-rulings.json#R3` |
| T03 / C2-003 | Amended | Added sealed-suite compatibility: no rewrite/synthetic collapse, recorded eligibility revocations, and a version/compatibility note. | `packets/fable-court-holdings.json#T03` |
| T04 / C2-005 | Amended | Added the WO-016 cross-stream seam and preserved LOO subsets only after complete binding/re-extraction. | `packets/fable-court-holdings.json#T04` |
| T05 / C2-006 | Amended | Bound n inside the frozen hash-covered registry and added post-freeze-mutation and mixed-authority negative tests. | `packets/fable-court-holdings.json#T05` |
| T06 / C2-016 | Amended | Split immediate mechanical work into WO-040; made controlled/internal the default and evidence handoff Ed-opt-in. | `packets/fable-court-holdings.json#T06` |
| T07 / C2-024 | Amended | Fixed WO-005 test scope and required reconciliation of the two recorded interval-effect reconstructions to one authoritative oracle. | `packets/fable-court-holdings.json#T07` |
| T08 / R1/WO-021 | Amended | Added an independent pre-demotion gate/allowlist freeze cross-check and corrected fail-open gate-content risk. | `packets/fable-court-holdings.json#T08` |
| T09 / R2/WO-022 | Amended | Required a receipted or `accounting_unknown` audit anchor and pinned manifest-known session inclusion/resume dedupe. | `packets/fable-court-holdings.json#T09` |
| T10 / stream ordering | Stands | Kept S4 after its hard dependencies; only optional prose drafting remained discretionary. | `packets/fable-court-holdings.json#T10` |
| T11 / C2-029 | Amended | Bound analysis-side provenance exclusion to WO-004, serialized it after WO-016 semantics, and removed impossible scope promises from WO-016. | `packets/fable-court-holdings.json#T11` |
| T12 / bench batch | Amended | Confirmed WO-024/025/026/028, required WO-030's missing clean-venv evidence, and recorded two non-reopening nit riders. | `packets/fable-court-holdings.json#T12` |

#### Lead/Ed-deferred rulings — R1, R2, R4

| Ruling | What changed | Source |
|---|---|---|
| R1 | Chose state-kernel choice A, narrowly authoritative for work selection: schema-v3 global gates, then-current gate freeze, independent-oracle tests, parity-before-prose-demotion, and residual DOC-008 work left open. | `packets/ed-rulings.json#R1` |
| R2 | Ratified provisional procedural spend guardrails with per-tier/WO/arc bands, SOFT/HARD consequences, a deliverable-progress tripwire, named-failure bar, accounting honesty, and sunset/recalibration rules; T09 supplied the final accounting amendments. | `packets/ed-rulings.json#R2`; `packets/fable-court-holdings.json#T09` |
| R4 | Classified every WO-009 manifest field as enforced, reserved-compatible, descriptive provenance, or remove; notably removed `items[].status_policy` and required a declared-not-verified marker for cache policy. | `packets/ed-rulings.json#R4`; `packets/wo009-field-scout.md` |

### 8.4 Counted reconciliation commands

The following read-only script was run against this tree from the repository
root.  It is included so every count above can be reproduced rather than
inferred from prose:

```sh
python3 - <<'PY'
import collections, json, re
from pathlib import Path

base = Path("docs/reviews/2026-07-13-comprehensive-audit")
receipt_ids = ["D1","D2","D3","D4","D5","D6","D7",
               "W1","W2","W3","W4","W4-exec","W5","SCI1","SCI2"]
receipts = [json.loads((base / "receipts" / f"{scan}.json").read_text())
            for scan in receipt_ids]
print("receipts", len(receipts), "rows", sum(len(r["rows"]) for r in receipts),
      "blockers", sum(x.get("severity") == "blocker"
                      for r in receipts for x in r["rows"]))

rows = [json.loads(line) for line in (base / "register.jsonl").read_text().splitlines()]
findings = [r for r in rows if r["row_type"] == "finding"]
operative = [r for r in findings if r.get("dedupe_of") is None]
merged = [r for r in findings if r.get("dedupe_of") is not None]
orders = [r for r in rows if r["row_type"] == "work_order"]
tiers = collections.Counter()
for row in operative:
    match = re.search(r"tier_final=([0-9])", row["verification"]["outcome"])
    tiers[match.group(1) if match else "record-only"] += 1
print("register", len(rows), "findings", len(findings), "operative", len(operative),
      "merged", len(merged), "work_orders", len(orders))
print("operative_tiers", dict(sorted(tiers.items())),
      "deferred", sum(r["state"] == "deferred-roadmap" for r in orders),
      "nondeferred", sum(r["state"] != "deferred-roadmap" for r in orders))

fable = json.loads((base / "packets/fable-verdicts.json").read_text())["verdicts"]
sol = json.loads((base / "packets/sol-final-verdicts.json").read_text()).values()
court = json.loads((base / "packets/fable-court-holdings.json").read_text())
print("fable", dict(collections.Counter(v["verdict"] for v in fable)))
print("sol", dict(collections.Counter(v["final"] for v in sol)))
print("court", dict(collections.Counter(v["holding"] for v in court)))
print("rulings", sorted(k for k in
      json.loads((base / "packets/ed-rulings.json").read_text()) if k.startswith("R")))
PY
```

Output:

```text
receipts 15 rows 85 blockers 10
register 101 findings 61 operative 43 merged 18 work_orders 40
operative_tiers {'2': 20, '3': 22, 'record-only': 1} deferred 7 nondeferred 33
fable {'confirmed': 46, 'narrowed': 15}
sol {'amend': 30, 'proceed': 7}
court {'conclusion-amended': 11, 'conclusion-stands': 1}
rulings ['R1', 'R2', 'R3', 'R4']
```

## 8.5 ULTRA comparison audit (post-wave verification modality)

Ran 2026-07-15 (Sol ULTRA, read-only, pinned worktree at `978e4c6`;
WO-022 pre-run statement in the 2026-07-14 run report; full response
preserved at `receipts/ULTRA-comparison-response.md`). Per-order
verdicts: 12 LANDED-FAITHFUL, 22 LANDED-WITH-DEVIATION, 6
DEFERRED-CONFIRMED (WO-034..039 sampled set), 0 NOT-FOUND. Two blockers
and twenty findings, triaged under Ed's same-day substance-over-ceremony
ruling:

| Disposition | Findings |
|---|---|
| FIXED, commit `913a2a6` (fresh xhigh checker FAIL on F2/F4 residue → fix round → delta PASS) | F1 custody window (blocker), F2 sealed-bundle gate (blocker), F3 schema parity, F4 frozen-v1-arm dispatch regression, F5 node_role identity, F16 explicit unknown rendering, F17 clean-venv boundary receipts |
| FIXED, lead bench `7853fc4` | F13 D-063 authority amendment, F10 WO-015 supersession line, F15 R-018 ratified-D-060 wording, F21 D-051 page-trim amendment (partial AUD-WO-039 pre-implementation recorded) |
| QUEUED, kernel task `AUD-FOLLOWUPS` (this file is its accepted-residue list) | F7 owned D-062 lint queue row, F9 WO-014 discriminating realized-token test, F11 WO-017 no-handoff regression assertion, F12 WO-020 standalone bridge-checker decision, F22 WO-040 absolute path + genuine pristine-clone test |
| ACCEPTED with disposition (Ed ruling: features/project over meta-process; work verified green) | F6 WO-009 persistence-migration scope expansion (migration sound, v1/v2 tests green); F20 misc bounded-scope overruns; F8/F14 ceremony-class receipt/test formality where adequate substitutes exist |
| RECORDED process deviations (historical; cannot unbreach) | F15→WO-023 DO-FIRST precursor ordering breach (landed after S2 opened; caught only at ULTRA) |
| RECORDED (Ed, 2026-07-15 close-out session) | F18 WO-027 codex-watch non-use: Ed confirmed verbatim "No flow uses it, only you use it. if no functionality is lost, go ahead." Functionality preserved: recovery recipe in the codex skill + the .codex-bridge observability replacement (demonstrated live). Acceptance clause CLOSED. |

## 9. Method notes and deviations

Charter-review dissent record: the Sol co-planner's round-2 design included
3 standalone upfront keep-defender scans (D1/D4/D7); the fresh-eyes Fable
review argued they duplicate §4's per-candidate keep-defender refuters and
produce keep-rows for undisputed code (audit-theater by this charter's own
standard); the lead sided with the fresh-eyes review and folded keep-prior
paragraphs into those domains' scan prompts instead.

### Close-out record (2026-07-15)

Deviations from this charter, and why:

- The wave PAUSED mid-flight at the bench batch (2026-07-13 checkpoint)
  for Ed's resume; the 2026-07-14/15 session completed it. The
  checkpoint, not this charter, governed resume ordering.
- WO-023's DO-FIRST precursor ordering was breached (landed after S2
  opened); undetected by the per-order layers, caught by the ULTRA
  comparison audit; recorded, not repairable.
- The close-out's "site regen" step was superseded mid-wave by D-068
  (Ed-directed): sessions end with a `docs/site/DRIFT.md` refresh; Ed
  deploys manually.
- The ULTRA comparison audit ran after the integration tree and
  supersession closure rather than after a main-merge adoption commit:
  Ed's merge is the adoption act (D-031 convention), so verification
  preceded adoption rather than following it.
- Two lead cross-tree/sequencing errors during resume (commit-before-
  close on WO-010; bench edits under an active lease) plus two
  hand-extended-sha prompt defects and one `resume --last` cross-thread
  mis-attach — all caught by the harness/wrapper layers, all
  adjudicated with Ed approvals recorded in the lease event chain and
  decision log (D-065 operational note).

Spend summary: `receipts/WO-022-audit-close-spend.json` (refreshed at
close; estimated basis, rollout-derived, cached-dominated; the arc's
band crossings are recorded there with the pre-policy flag on WO-010's
21.8M-token implementation session).

Per-layer catch attribution (resume arc; unique catches only):

| Layer | Unique catches |
|---|---|
| Fresh per-order Sol checkers | WO-011 item_type-label evidence bypass (major); WO-021 four-record silent queue loss (blocker); WO-031 three freshness-coverage majors (with mutation probes); WO-027 live-discovery gap; ULTRA-fix F2 fail-open residue + F4 inauthentic regression (blocker+major) |
| C-033 coherence council | six D-entry corrections incl. the D-058 Primary Metric supersession |
| Integration review (xhigh) | capsule budget breach from stream-union growth; D-068 vacuous-green on capsule/generated deploy surfaces |
| ULTRA comparison audit | the WO-001/010 custody interrupt window (blocker), the sealed-bundle vacuous gate (blocker), the frozen-arm dispatch regression, node_role identity collapse, + 18 further deviations/dispositions (§8.5) |
| Fable completeness critic | unfilled §9 close record; ULTRA modality absent from the durable record with a dangling AUD-FOLLOWUPS pointer; three undispositioned majors |
| Harness permission classifier | three refusals of lead self-approved lease abandonments (all subsequently Ed-adjudicated) |
| Lead-live | checker-thread `resume --last` mis-attach caught and killed after one read-only call |
