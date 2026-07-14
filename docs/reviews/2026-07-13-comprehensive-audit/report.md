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

(Filled by the inventory + scans; every tracked current-source file → one
domain; one walk or an explicit exclusion; zero-finding cells recorded
here with their receipt ids.)

## 8. Findings synthesis

(Filled at adjudication: per-domain verdict table, accepted/rejected
findings, work-order list in dependency order, rejected-findings table,
deep-dive outcomes. MANDATORY subsection: every rejected or downgraded D7
finding in its own table with rationale — the audit's authors built D7's
subject matter, so those adjudications are surfaced to Ed rather than
silently self-decided.)

## 9. Method notes and deviations

Charter-review dissent record: the Sol co-planner's round-2 design included
3 standalone upfront keep-defender scans (D1/D4/D7); the fresh-eyes Fable
review argued they duplicate §4's per-candidate keep-defender refuters and
produce keep-rows for undisputed code (audit-theater by this charter's own
standard); the lead sided with the fresh-eyes review and folded keep-prior
paragraphs into those domains' scan prompts instead.

(Filled at close: what deviated from this charter and why; spend summary;
per-layer catch attribution.)
