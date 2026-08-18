# Decision Log

This is the canonical record of design decisions for JouleWise. Every decision
that binds later work, trades off real alternatives, or would otherwise need to
be re-derived by a future agent gets an entry here.

## How To Use This Log

- Before implementing anything non-trivial, check whether a decision here
  already covers it. Do not silently re-decide settled questions.
- When you make a new decision of this kind during a run, add an entry, link it
  from the run report, and reference its ID (`D-NNN`) in the code review or doc
  that applies it.
- Statuses: `accepted` (binding until revisited), `open` (criteria defined,
  evidence pending), `proposed` (recorded, awaiting Ed's ratification),
  `superseded by D-NNN`.
- Every entry must include Options Considered and Considerations. A decision
  without recorded alternatives is not auditable.
- Revisit triggers are part of the contract: when a trigger fires, the decision
  must be re-examined, not quietly worked around.

## Index

| ID | Title | Status |
|---|---|---|
| D-001 | Run bundles store normalized `config.json`, not YAML | accepted |
| D-002 | Telemetry sampling via subprocess + file, no controller threading | accepted |
| D-003 | Timestamp and clock-alignment policy | accepted |
| D-004 | `powermetrics` privilege workflow | accepted |
| D-005 | One bundle per repetition, grouped by experiment manifest | accepted |
| D-006 | Dashboard v1 is a static HTML report generator | accepted |
| D-007 | YAML config input is deferred | accepted |
| D-008 | Split runs arrive via schema v0.2 (`run_kind` + `split_plan`) | accepted |
| D-009 | Dependency policy: stdlib core, optional extras | accepted |
| D-010 | Run ID scheme | accepted |
| D-011 | `summary_metrics.json` is the bundle completion marker | accepted |
| D-012 | Failure-reason to run-status mapping | accepted |
| D-013 | Controller-as-DUT mitigation for Mac-local runs | accepted |
| D-014 | Statistical protocol for repeated runs | accepted |
| D-015 | Split-mechanism priority and same-runtime rule | accepted |
| D-016 | Benchmark model selection | open (provisional small-model pick 2026-07-06; opens 2G only) |
| D-017 | CI scope | accepted |
| D-018 | Per-backend `power_w` definition and rail policy | accepted |
| D-019 | Mock adapters use simulated time via an injectable clock | accepted |
| D-020 | CLI binds `FakeClock` for all-mock runs, `SystemClock` otherwise | accepted |
| D-021 | Controller flushes `events.jsonl` before the reduce stage | accepted |
| D-022 | Auto-generated run-ID suffix is config-hash-derived, not random | accepted |
| D-023 | Per-item phase status lives solely in the exit checklists | accepted |
| D-024 | Adapters receive a `RunContext`, not piecemeal parameters | accepted; implemented (2N.1, 2026-07-06) |
| D-025 | One shared bundle read layer for reducer, report, validation, and aggregation | accepted; implemented (2N.8, 2026-07-06) |
| D-026 | Measured window is bounded by sampling-active marker events | accepted |
| D-027 | Per-rail rows must share per-sample timestamps; misalignment is a structured failure | accepted |
| D-028 | `reduce` verb rewrites `summary_metrics.json` in place (the one sanctioned post-finalize mutation) | accepted |
| D-029 | Config schema declares nullable optionals; serialization (and config hashes) unchanged | accepted |
| D-030 | `validate-bundle` stays structural by default; `--strict` adds raw-evidence checks | accepted |
| D-031 | Multi-model council review; PR convention for multi-commit sessions (merge authority amended by C-010); D-023 extension + end-of-session consistency sweep | accepted |
| D-032 | `phase_energy_j` is gross-only in summary v0.1 | accepted |
| D-033 | Prompt-content provenance is recorded per run bundle | accepted |
| D-034 | Slice 2O owns the workload program after 2M and 3.0.1; implementation lane reopened by D-042 | accepted |
| D-035 | Replay claims require fresh-process (subprocess-per-stage) isolation | accepted |
| D-036 | Spike verdict codes derive from measured data, never hardcoded | accepted |
| D-037 | Claims ladder (L0-L4) binds reader-facing claim language from 2M onward | accepted |
| D-038 | Analysis plans bind L2/L3 claims to pre-registered comparison rows | accepted |
| D-039 | Workload program v2: substrate first, identification before scale; pre-Window-A allowlist superseded by D-041/D-042 | accepted |
| D-040 | Suite architecture v2: generic suite mechanism, bundle-level replication | accepted |
| D-041 | Benchmark interop via frozen-subset imports and marker-shim energy layer; interop lane remains post-2M + post-P2-010a | accepted |
| D-042 | D-034 implementation lane reopened; suite build may proceed pre-2M | accepted |
| D-043 | Supersession-closure discipline | accepted |
| D-044 | Suite config identity: omission-serialized ref + effective-manifest hash | accepted |
| D-045 | Suite substrate execution semantics (run_suite, statuses, per-item outputs) | accepted |
| D-046 | AP-6 sentinel delivery is ids-native BOS-less at literal equal shape | accepted |
| D-047 | Affine ladder pins: level set, smoke sizing, gate denominators | accepted |
| D-048 | Split program is model-first: pre-registered compositional prediction before split runs | accepted |
| D-049 | Split transfer-energy boundary accounting on discrete-GPU ends | accepted |
| D-050 | Active stop cards and process-trace manifests | accepted |
| D-051 | Advisor status site uses source-derived static pages plus fail-soft live GitHub overlays | accepted |
| D-052 | Capstone scope contract: frozen umbrella headline and contribution ladder | accepted |
| D-053 | Contrast-level statistical inference and the frozen analysis registry | accepted |
| D-054 | False-effect guard floor and unknown-term claim-ceiling policy | accepted |
| D-055 | Research-question registry is the canonical live index | accepted |
| D-056 | Suite order policies and order_row provenance | accepted |
| D-057 | Uncertainty terms: drift is a bound; stable claim-gate reason codes | accepted |
| D-058 | Token-normalization and stack-identity contract adopted | accepted |
| D-059 | Claims-lint mechanical enforcement in CI | accepted |
| D-060 | Depth-before-breadth stop line | accepted (ratified 2026-07-10) |
| D-061 | Review-layer evaluation rule v2 | accepted |
| D-062 | Confirmatory sampling policy (fixed n, demotion) | accepted |
| D-063 | Process architecture v2 (state kernel first) | accepted |
| D-064 | Delegated-invocation compliance surface: tracked per-session JSONL event stream, canonical report envelope, enforced write scope | accepted |
| D-065 | bridge-protocol/v1.1 — co-work lane, session wrappers, tolerant envelope | accepted |
| D-066 | Scoped spec-freeze override for the AXI extension agenda (Ed override) | accepted |
| D-067 | Idle reporting basis — gross headline; idle-subtracted is a labeled within-device secondary view | accepted |
| D-068 | Site deployment is Ed-manual; sessions end with a drift report, never a deploy | accepted |
| D-069 | Advisor-doc alignment (stream S-0) is sanctioned front-facing work | accepted |
| D-070 | Architectural-axes extension agenda (AXI): scope, claim posture, batch-axis rulings | accepted |
| D-071 | G10 memory-fit rule ratified (axi-sd-memory-fit-shape-v1); device-list review opened | accepted |
| D-072 | Standing self-merge-with-full-gate authority (gh merges included) | accepted |
| D-073 | D-016 device-list amendment: Mac + 3080 Ti primary fleet, 12 GiB cap | accepted |
| D-074 | Conditional Qwen3-4B primary repin + OLMo-1B conversion spike authorized | accepted |
| D-075 | Extension-axis intake: ranked fold-in without new thesis proliferation | accepted |
| D-076 | Site capacity right-sizing (AUD-WO-039 review): measured-first budgets | accepted |
| D-077 | Environment guard, idle admission, and cooldown v2 | accepted |
| D-078 | Soundness gate: no claim-bearing extraction from time-anchor-defective powermetrics corpora | accepted; operative under Ed's direction through the full repair arc (close-out cap explicitly Ed-ratified 2026-07-22; original-text ratification rides PR #79 review) |
| D-079 | Calibration acceptance v2: derived bracket screen plus budget, a pre-flight calibration screen with cause-removal retry, one general production scope name, and publishing the decode floor now | accepted (Ed-ratified 2026-07-27) |
| D-080 | Standing fresh-eyes sweep: a periodic, non-reactive outside review on one cadence unit, a rotating second lens, and a mechanically generated packet | accepted (magistrate-ratified 2026-07-27) |
| D-081 | Session History pointers: build_site parser accepts docs/process_traces/ alongside docs/run_reports/, fail-closed otherwise | accepted (Ed-ratified 2026-07-28) |
| D-082 | Floor-mint execution semantics: basis-pinned subset consumption (Option A), component-scoped cross-window artifact schema v2, production_window scope, prospective source_class, non-defaulting widths | accepted (magistrate-adjudicated 2026-07-28, executing D-078 cl.11 / D-079 cl.4-5) |
| D-083 | B3 adjudication: the additive effective-clearable-effect expression is a disclosure obligation, not an acceptance threshold; two-gate claims design ratified; B3 not-a-defect | accepted (magistrate-ruled 2026-07-29; Sol dissent preserved) |
| D-084 | Operative decode-floor pin re-set to the composed cell gate 7.377086 J (absolute 3.592138 / comparative 7.377086 / gate = max, never summed), amending the isolated D-079 cl.5 pin | accepted (Ed-ratified 2026-07-29) |
| D-085 | splitwise_decode_v1 / qwen25_7b_decode_floor_v1 pre-registration ratifications Q1-Q9: floor-first ordering, family ids, comparative_contrast kind, two-arm stack scope, fixed A/B/B/A, production_window scope, Q7 refused, magistrate operates windows solo | accepted (magistrate-ratified 2026-07-29) |
| D-086 | Supersession-aware cooldown-evidence join (FIX-9): validated supersession entries extend to the cooldown join; resolve only when a valid entry names exactly the observed duplicates; --evaluation-basis-sha256 invocation/doc root cause | accepted (magistrate-ruled 2026-07-30) |
| D-087 | Cold-gate exercise record: F1 MODIFY→FIX-8 with C1-C4, M1-M4 synthesis, packet correction on the record, third-failure-closes precedent | accepted (cold-gate + magistrate synthesis 2026-07-29) |
| D-088 | Cooldown-join escalation: no FIX-11 (missing existing-outcome bit makes counting rules structurally unsound), join contract C1/C3/C4/C5 ratified for its own gauntlet, conditioned merge license for impl/mint-tool at 16c7af0, QA-10B ruling-was-the-defect finding recorded | accepted (cold gate + Opus refuter + magistrate synthesis 2026-07-30) |
| D-089 | D5-J adopted for the cooldown-evidence join: declaration-first, join-owned occurrence ledger, one invariant owner, observed→declared matcher, catalog-completeness gate C, `-1` sentinel retired, EXACTLY two accepting shapes with the liberalization cell STRUCK; interim merge refused — the structural fix lands pre-merge | accepted (escalation-triggered design consult + magistrate ruling 2026-07-30; amends D-088 in venue only) |
| D-090 | Delegation conduct on the FIX-10 round: a read-only audit brief is binding, and a commit message may not assert a review that has not happened or label non-defect-shaped tests as regressions | accepted (magistrate-recorded 2026-07-30) |
| D-091 | Metrology pivot: the capstone is metrology-centric — the measurement instrument is the product; the paper leads with metrology claims (linearity, additivity, floors, drift governance) and the model contrasts become demonstration studies | accepted (Ed/Rivoire-ratified 2026-07-30) |
| D-092 | Wall meter ratified for the paper (claim C8) with no hardware yet — operate without until purchased; P1-003 answered: buy per the SPEC/Khan/CCGRID references in the advisor brief | accepted (Rivoire-answered, relayed by Ed 2026-07-30) |
| D-093 | DA-1 cold-gate synthesis: no behavior-changing fix round (DA-1 closes in the gauntlet at the validator/reader boundary), merge at the comment-corrected head `707f76e`, DA-1 registered into gauntlet C5, raw-vs-validated bench scan added to every claim consumption | accepted (cold gate + Opus refuter + magistrate synthesis 2026-07-31) |
| D-094 | Gauntlet counting domain: COMPOSED design adopted (prospective writer outcome enum + fail-closed legacy log binding; truth table preserves the struck cell; DA-1 closes at the raw reader boundary); D-088 benign-count corrected 46→44; three-commit landing order C1-first | accepted (D-088 cl.2 mandated consult + magistrate 2026-07-31) |
| D-095 | MANIFEST-CONTRAST design: analysis-manifest v3 (new module + dispatcher, v1/v2 byte-frozen), governed ABBA block derivation, folded_sha256 arm binding, Holm m=1 two-sided positive-direction, cross_stack_armwise_max.v1 floor rule; claim chain = gauntlet → v3 → multi-cell mint → claim | accepted (rule-2 consult + magistrate 2026-07-31; implementation queued behind the gauntlet) |
| D-096 | Metrology v1 plan vocabulary ratified (staleness_sentinel, plan-only field shapes, recorded fallbacks); four window-A plans FROZEN before measurement; F2 --k hardening is a standing pre-replacement condition | accepted (magistrate ratification pass 2026-07-31) |
| D-097 | B1 cold-gate synthesis: v2 outcome consumption deferred to gauntlet commit 3 (writer-minted authenticated discriminator required); interim v2-label and outcome-field refusal everywhere (reader accepted set == writer emitted set); merge train held on four release conditions | accepted (unanimous cold gate + refuter, magistrate synthesis 2026-07-31) |
| D-098 | Metrology window A record: salvage close under the third-failure rule, a10-precedent recorded-deviation post-cal retry, whole-window verdict FAILED as-issued (dangling quarantined slot + refused bracket formation), two checkpoint corrections (additivity 21/24; Anker charger identity); machinery questions registered to MET-VERDICT-ADJ-01, never hand-applied | accepted (magistrate-recorded 2026-08-01) |
| D-099 | Metrology window B record + doctrine: three-launch arc under the bird-SIGSTOP protocol (once-validated), clock-anchor knife-edge accepted as an instrument-design finding (rate-aware anchor queued), TM attribution retired as a false proxy, operator output streaming during idle gates recorded as a measurement hazard (one-line arm messages binding), verdict FAILED as-issued (membership resolution) with adjudication routed to MET-VERDICT-ADJ-01 | accepted (magistrate-recorded 2026-08-01) |
| D-100 | Salvage-dangler terminal semantic: cold-gate synthesis — S2-A admission-bounded exclusion (measurand-existence line, cap of one, fail-closed default) landed in the S3 consumption-semantics-dispatch shape so original FAILED rows stand by construction; unanimous machinery repairs (count-uniform path, sibling-discard fix, identity binding, ledger honesty); window B re-evaluation licensed under recorded conditions [since 2026-08-02 HARD-BLOCKED on D100-BII-BINDING-01 per D-106 cl.3], window A unlicensed; refuter dissents recorded | accepted (cold gate + bounded follow-up + Opus refuter, magistrate synthesis 2026-08-01) |
| D-101 | The site gates nothing: CI release-chain job advisory (continue-on-error), site source docs stay live and session-maintained, DRIFT.md refresh optional, site budgets never reshape governed records | accepted (Ed-directed 2026-08-01) |
| D-102 | CAL-BRACKET-D079-01 pins: budget cap 0.001275166090593858 s (99% two-draw prediction ceiling 0.012093166090593858 s, blind n=19 derivation), exact-identity-epoch freshness with prospective re-derivation triggers, never-zero allowance max(drift, screen) embedded once, decimal-source numeric semantics with labelled presentation values | accepted (magistrate ratification, lead-replayed arithmetic, 2026-08-01) |
| D-103 | C3 structural cold-gate synthesis: WAL attestation ordering + torn-tail tolerance + origin-gated operator repair (B1); one authentication predicate with TWO named aggregation policies, cold instance OVERRULED on catalog-global verdicts with recorded dissent (B2); writer-strict/reader-tolerant path discipline, backslash false-malformed corrected (B3); origin-binding redesign registered as fallback; fix-round-2 scope restated | accepted (cold gate + Opus refuter, magistrate synthesis with bench-verified overruling, 2026-08-01) |
| D-104 | C3 residuals cold-gate synthesis (CONVERGENT): acquisition-identity lock tokens (registry + dev/ino + nonce + root binding; log_path.parent candidate rejected), positive writer-grammar tail recognizer with byte-exact canonical round-trip (message-class discrimination ruled out; refuter-discovered whitespace-preservation hole closed), SF1 ruled jointly, R1-R11 regressions, origin-binding fallback not routed | accepted (cold gate + Opus refuter converged; magistrate synthesis 2026-08-02) |
| D-105 | C3 disposition: LAND via a final custody micro-commit (preserve-then-truncate sidecar, writer-side ASCII key assertion, F3 hygiene, R7-as-ruled) + narrow fresh audit + merge; F1/F2 registered as a NEW ruling (not D-088 precedent) closing via C3-RECOGNIZER-EXACT-01 with the number-grammar exactness STRUCK for a documented decidable superset (D-104 cl.2 amended); three-scan absence evidence recorded; runway-context-in-packet process violation recorded | accepted (cold gate + Opus refuter, magistrate synthesis 2026-08-02) |
| D-106 | b-ii residual: Variant D — merge the inert D-100 repair at its audited head, register NOTHING (D-105 guard failure + decidable-closure inversion accepted), window B re-evaluation BLOCKED on D100-BII-BINDING-01 (interval containment + custody digest freeze + nested closure + condition-3 re-record); cold instance overruled on the refuter's bench-verified showing; magistrate packet-hygiene failures recorded | accepted (cold gate + refuter, magistrate synthesis 2026-08-02) |
| D-107 | D100-BII nested-content closure cold gate 2: C-A′ producer-derived admission grammar with per-leaf value domains (no bare isinstance(str)); derivation obligation corpus-verified (in-kind fence condition recorded); scope expanded to the inventory grammar + guard-phase/node_cleanup false-refusal repairs; row acceptance amended with the over-refusal gate (license 3/3 real subjects); fix round 2 licensed, fresh focused audit; magistrate packet-hygiene failures recorded (third occurrence, standing tightening) | accepted (cold gate + Opus refuter, magistrate synthesis 2026-08-02) |
| D-108 | D100-BII-BINDING-01 clause (c) RETIRED as a license precondition (zero-output-bytes predicate mechanically unreachable; substitution closed by the landed clause-(b) manifest pin); row closes on (a)+(b)+(d) with the repaired-tool digest-bound re-record over ALL THREE D-087 occurrences carrying the formal load (manual record corroboration only); L-A′ demoted to banked non-load-bearing hygiene; window B re-evaluation unblocks on row close | accepted (Ed 2026-08-03, deferral to the joint magistrate+Sol consult; C-042 debate record) |
| D-109 | CAL-BRACKET-D079-01 F3: A-min-with-reservation — writer-enforced receipt ledger (reservation-first pending entry before capture, mandatory finalization, unresolved-pending refusal), ledger-only consumption, repo-committed head pin, single immutable snapshot threading; R1 authority/retention/anti-rollback (7 clauses) + R2 prior-observation set with the 38-total counting rule (8 clauses); Option B recorded as rejected fallback; lands with F1+F2 as the single combined fix round | accepted (Ed 2026-08-03, same deferral; Sol soundness breaks lead-verified and adopted) |
| D-110 | Mint #1 retroactively NON-CLAIM-BEARING (taint-and-remint, Ed ruling on sweep finding RT-1: floors embed zero allowance where D-102 pin 3 mandates +max(drift, 0.010818 s)); re-mint gated on D-109 landing + artifact issuance + validator pin widening; RT-2 dependency edge minted (MINT-GENERALIZE-01 hard-blocked on CAL-BRACKET-D079-01); night-consult 7B-mint license suspended; RT-5 recorded: all four PASSED window verdicts untainted | accepted (Ed 2026-08-03, sweep-triggered) |
| D-111 | Adjudication evidence gains tracked custody: load-bearing adjudication artifacts (cold-gate packets, rulings, refuter reports, cited debate records, re-records, decision-input corpora, archive digests) commit under docs/process_traces/ in the producing session; .desk stays working scratch; named backfill set executed this session | accepted (Ed 2026-08-03, sweep-triggered) |
| D-112 | Window B re-evaluation STOP gate synthesis: refusal = CORRECT fail-closed machinery (sole cause mtadd-p2048o0128-r06 collection-time clock-anchor failure, falsify-by-removal 69/69 + per-bundle attribution); no repair row; D-100 license EXHAUSTED AS DRAWN; original FAILED verdict stands; r06 removal channel + F7 barred-cell-scope question + NEG-8 bound re-mint PARKED FOR ED; standing correction: condition spellings non-unique to producer | accepted (magistrate synthesis of the convergent cold gate, 2026-08-03; record tracked in process_traces) |
| D-113 | Window B TERMINALLY CLAIM-RETIRED (Ed ruled D-112 channel (c)): RETAINED_IMMUTABLE / PERMANENTLY_NON_CLAIM_BEARING with labelled forensic use; no new verdict (original FAILED stands); WB-specific D-100/D-106/D-108 license retired, general machinery survives; WINB-R06-DISPOSITION-01 closes ABANDONED_FOR_FRESH_COLLECTION; F7 whole-window voiding AFFIRMED as current semantics (cell-scoped alternative only via a new Ed-ratified amendment under D-083's revisit rule, including the stated causal-domain proof and preregistration gates); NEG-8 WB re-mint MOOT, freshness rule survives by cross-reference; fresh-claim reset beginning Window C (no WB member in replacement basis; MET-WINDOW-C-01 re-scope); standing rigor-first principle + anti-rigor-spiral guardrail; Window C NO-GO until consult Q4 gates green | ratified (Ed 2026-08-05; magistrate transcription after Sol xhigh consult, record in process_traces) |
| D-114 | T3-CHAIN DESCOPE (Ed directive, reverses his 2026-08-03 T3-DRIVE priority): t3 stays the INTERACTIVE control plane; t3-resident-during-measurement-windows DROPPED; QUIET-GUARD-01 re-scoped to commit 1 only; commits 2-4 + T3-CHAR-PAIR-01 + WO-T3-VIS-01 + SEC5A-REMOTE-01 shelved; T3-DRIVE gate lifted; Q13 degraded tail accepted; Q10 credential superseded | ratified (Ed, 2026-08-05, in-thread; D-113 number reserved for the parked WINB-R06 disposition) |
| D-115 | Quiet-guard Q2 setup authority = FIXED INSTALLATION CAPABILITY, not general root authority; binding conditions: fresh interactive sudo authorization (sudo -k), digest-authenticated staged content, real interpreter isolation; installs INACTIVE; renumbered from the contract's proposed D-114 marker (number collision with the descope); entry lands via main + merge-back (packet-letter deviation ruled in the entry) | adjudicated (lead under Ed's standing Q2 license, 2026-08-05) |
| D-116 | D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (seq 76 / head 08456d50…; issued sha 316113960c…; 30/2/6 dispositions); D-110 condition (b) SATISFIED → MINT-GENERALIZE-01 unblocked for re-mint; two-cold-gate history (plan HELD → consumer impl + gauntlet → bytes PROCEED, sequencing HOLD resolved by consumer-first merge); window_metrologyB calibration fiducials in completeness record are NOT a D-113 violation | executed (Fable magistrate, 2026-08-06; Ed pre-authorized) |
| D-117 | D-110's historical re-mint order SUPERSEDED (structurally unsatisfiable at main: issued ledger holds only import-marked receipts, candidate discovery excludes imports); replacement = THREE prospective claim windows (fresh 1.5B decode floor, fresh 7B decode floor, fresh decode contrast) live-bracketed under the issued regime; prefill floor cells ride the floor windows; contrast decode-only by default (≥256-token prefill arm stays Ed's open option); D-113 readiness rewired (three-window P1 closure precedes MET-WINDOW-C-01); Option 1 preserved as cold-gated contingency only | adopted (Ed directive, in-thread 2026-08-07; transcribed by the Fable magistrate) |
| D-118 | NOTHING approaches merge without the full council: the merge gate is ENUMERATED (independent audit; paired distinct lenses; lead FIX contract; delta re-audit of every fix round; same-signature statement; Opus counter-review; apex Fable diff gate — delegable to Fable subagents, magistrate adjudicates; overbuild/prune; lead unpiped integration-tree replay; final-head rule; CI + post-merge cross-unit review) and MECHANICALLY CHECKED via a per-PR gate ledger; D-072 self-merge is conditioned on that ledger being complete; a burn license never reduces the gate | ratified (Ed directive, 2026-08-07; trigger: PRs #111/#112/#113 merged with an incomplete gate, self-reported and closed retroactively) |
| D-119 | Claim-LANGUAGE rulings (wording strength of provenance/custody statements, demonstrated-vs-designed framing, limitation phrasing) delegated to the magistrate, CONSERVATIVE BY DEFAULT — take the weaker honest phrasing unless evidence for the stronger is named in the same breath; what to measure/fund/scope/publish remains Ed's; ends when Ed joins the draft review loop | ratified (Ed directive, 2026-08-07; prompted by the operator-attested custody wording, which affected no measurement or datum) |
| D-120 | D117-POSTCOLLECTION-TRUST-01 executed: `floor_mint_postcollection` DELETED with no producer assigned (unknown-key refusal under a closed D-117 report profile); the v2 mint calculates the verification projection from each pin's DOMAIN OWNER (ledger+binding custody, issued acceptance allowance, verdict-basis membership/drift, floors recomputed from authenticated members) and never generates pins; git-derived provenance (mint runs git, refuses dirty tree; origin/main containment recorded, unknown tolerated); assurance qualifier single_authority_hash_bound_replay.v1 REQUIRED in v2 artifacts; paper §5/§11 updated in step; v2 mint bar lifts only when this lands through the full D-118 gate | adopted (escalation consult ESCALATION-CONSULT-RESPONSE.md; magistrate transcription, 2026-08-07) |
| D-121 | The MAGISTRATE'S OWN final review is the TERMINAL merge-gate item: after EVERY other pass (audits, lenses, deltas, counter-reviews, subagent final-head passes, CI) completes, the magistrate itself — WITH full session context — reviews the exact merge candidate last; no delegation of this terminal slot (subagent Fable passes remain valid as EARLIER items); only then D-072 merge. Amends D-118 (adds item 12; the ledger records it explicitly) | ratified (Ed directive, in-thread 2026-08-08; transcribed by the magistrate) |
| D-122 | Ruling 4 RULED BY ED (reverses the standing recommendation): the paper is NOT decode-only — the contrast window (gamma) grows a prospectively frozen 256-token prefill ABBA arm (scout evidence: 128-tok historical delta 5.809930 J vs ~5 J practical bar = MARGINAL, interval dips below; 256-tok projection ~11.619860 J clears with >2x margin — sizing projection, not demonstrated; the claim machinery refuses honestly if the night lands below bar and the marginality analysis publishes); prefill floor cells still ride alpha/beta; pack/night budgets grow accordingly | ratified (Ed directive, in-thread 2026-08-08: "size up the workloads to get more data — I don't want a decode-only paper/scope if at all possible"; transcribed by the magistrate) |
| D-123 | Ruling 2 RULED BY ED: YES — reported phase-energy mean cells pre-register in the alpha/beta packs (same 50 members, no added collection), conditional on the scheduled no-semantics-change check proving floor outputs byte-identical; PLUS Ed's standing design preference: workload SIZE is the free lever against the fixed attribution blur — size signals up wherever it costs the instrument nothing and does not destabilize proven designs; PLUS an ordered Sol debate on whether attribution itself can be improved within instrument scope; PLUS the overnight license (~12h autonomous, goal = a defensible paper, Sol liberal on fast tier, magistrate oversight with D-121 terminal reviews, Opus extra eyes) | ratified (Ed directive, in-thread 2026-08-08, on leaving for the night; transcribed by the magistrate) |
| D-124 | Common-mode ABBA contrast estimator PROMOTED-AS-CANDIDATE in the TWO-SHARED-EDGE form (shared onset + shared offset parameters, adversarial per-bundle residuals) after the ordered current-semantics replay HELD the bar decisively (a5 decode: worst-case default 8.611855 J vs joint-sweep 1.632422 J, two-shared-edge 1.869502 J — all NON-CLAIM); registration conditions bind (named estimator + named stationarity transfer assumption with evidence; pre-registration in the D-117 packs BEFORE claim data; identical treatment on calibration and consuming contrast; allowance exactly once; full D-118/D-121 gate; issued artifact untouched); the evidentiary limit of the transfer assumption is registered and rides the paper's limitations | adopted (magistrate under the D-123 overnight license; Ed may reverse — flagged for morning review) |
| D-125 | Ed morning ratification batch (2026-08-08): D-124 common-mode estimator SIGNED OFF ("if instrument gets better, yes"); the Q1+Q13 lineage-envelope adoption RATIFIED on trust ("i trust your decisions there"), with the magistrate's clarification on record that this is successor calibration-acceptance arithmetic (not workload profiles) and only ever strengthens the 0.010818 floor — D-117 cl.1 is accordingly AMENDED for successors to "genesis lower bound + lineage-envelope rule" (the consult's transcription condition is met; freeze-until-ruled ends); 40-hour work window granted — plan of record at docs/strategy/2026-08-08-40h-plan.md | ratified (Ed, in-thread 2026-08-08 morning; transcribed by the magistrate) |
| D-126 | U2 second-convening synthesis TRANSCRIBED (record: docs/process_traces/2026-08-07-u2-coldgate/SYNTHESIS-V2.md): six first-round objections verified moot in code by both sealed judges; Q2/Q4/Q6/Q7/Q9/Q11 + the Q13 n>=19 floor RATIFIED with the cold judge's binding amendments; Q5 ratified WITH the judge's closure definition (decision-log disposition by content_id + successor prior_observation_set record; consuming code waits for the first disposing ruling); Q8 registry authority ratified and the migration shim DELETED by convergent ruling; the Q1+Q13 joint remand is RESOLVED by the D-125 lineage envelopes; Q12 stays OPEN pending full-register re-presentation (packet rule hardened: quotes run to end of document section); Q10 deferred to the recovery gate; rework round 2 + the landing gauntlet (required writer≠reviewer lens over the 965-line successor test surface) bind before any successor issuance; this decision ID replaces the COLD-GATE-U2-PENDING tuple member — an issued artifact may never embed a tuple member with no decision-log entry | adopted (magistrate transcription of the sealed convening, 2026-08-08) |
| D-127 | AUTONOMOUS WINDOW LOOP authorized (Ed directive, in-thread 2026-08-08, during the 40h window): partially REVERSES D-114's descope — the scoped network-time toggle (QUIET-GUARD sudoers slice: exactly the two fixed systemsetup network-time commands, exact binary path + exact argv, no wildcards) plus an autonomous experiment-loop harness (post-window supervisor step relaunches a fresh headless claude session with launch-then-verify-then-retry liveness proof + an independent launchd fallback timer; agent fully EXITS during capture — zero-agent rule for the capture itself is UNCHANGED) are chartered for build. D-115's conditions bind the privileged install path (fresh sudo -k auth, authenticated staged content, interpreter isolation) and Ed personally executes the one sudo install command — the privileged step never passes through the agent. Security-critical: full D-118/D-121 gauntlet + pre-decision design consult; built OFF the night-critical path and INSTALLED only at a deliberate Ed-present moment | ratified by D-128 (build authorized; install gated; initially chartered by Ed, in-thread; transcribed by the magistrate) |
| D-128 | STANDING RUN-THE-LOOP MANDATE (Ed, in-thread 2026-08-08): the magistrate runs the project and experiment loop end-to-end — windows, mints, refusal diagnosis, re-arms, desk analysis, paper assembly — UNTIL A DEFENSIBLE PAPER EXISTS (P1 bar: measured numbers whose every claim survives the adjudicated trust model, D-119-conservative wording, the results acceptance contract, and the D-078 floors doctrine). D-127 is RATIFIED (was chartered). What still binds unchanged: zero-agent capture fence; D-118/D-121 on every merge; escalation + cold-gate discipline; the lieutenant-forbidden list; Ed's owed rulings stay his (funding, scope, spec governance); publication/claim release stays Ed-gated. This is authority to keep driving between his taps, not license to relax any gate | ratified (Ed, in-thread; transcribed by the magistrate) |
| D-129 | ED OPERATING DIRECTIVES BATCH (in-thread 2026-08-09, T3 session; transcribed by the magistrate): (a) STANDING FAN-OUT ORDER — maximal parallel fan-out (multiple Sol lanes in disjoint worktrees + Workflow grader/review fleets + Opus corps) is the DEFAULT whenever it speeds work, incl. H1/H2 prep when H0 lanes are saturated; queue only on real collisions or gate dependencies; no gate or doctrine is relaxed by fan-out. (b) CODEX SERVICE TIER — fast usage cut ~60%: DEFAULT tier is the norm (supersedes the 2026-08-08 fast-standing-default); fast reserved for the single run whose wall-clock gates the session milestone; one consolidated xhigh beats multiple fast highs. (c) FABLE TOKEN ECONOMY — orchestration/direction subagents run as Opus 5 (high); Fable reserves = rulings, security classifications, D-121 terminal reviews, final live verification, escalation calls, Ed comms; COVERAGE UNREDUCED — Fable still full-audits everything important or claim-bearing itself, reading primary artifacts (savings come from ceremony delegation, never from thinning review). (c) amends the operative stream-director framing in docs/orchestration.md (the stamped C-009/C-010 council record stays as a dated record) | adopted (Ed, in-thread; transcribed by the magistrate) |
| D-130 | DECISIVE-RUN VENUE RULING (cold gate + paired refuter, 2026-08-11; PR #122): decisive designation follows EVIDENTIARY SUBSTANCE, not venue. For PR #122 ONLY, the authoritative decisive run for the D-117 v2 production proof is the custodied lead local execution at e871f5b (hermetic-by-construction: byte-pinned store from the published release; unset-store can only skip or fail; the legacy-locator assertion executed against 190 LIVE machine-local decoy paths), taken together with the CI-proven transport/authentication chain (workflow steps 1-7 hosted-green). The hosted d117-production-proof job is ADVISORY (dispatch-only) pending WO-CI-RESTRUCTURE; its first hosted green is the required second independent execution; contradiction of the local result = automatic stop signal + cold gate. NO general local-decisive lane: any future substitution requires a cold-gate ruling on THAT merge, a digest-pinned fixture with an equivalent store-content lock, a live-decoy hermeticity assertion, a committed one-command replay recipe (scripts/replay_d117_decisive.sh is the template), and a recorded restructure order; the admission EXPIRES at WO-CI-RESTRUCTURE closure. Citation discipline until closure: "lead-verified locally (custodied bundle: docs/evidence/d117-v2-decisive-20260811/) + CI-verified transport/authentication chain", never "CI-proven decisive run". Lesson bound for future proofs: a decisive job whose runtime was never bounded against its venue's hard cap is a design defect | adopted (cold-gate ruling + refuter concurrence; magistrate-applied 2026-08-11) |
| D-131 | Identity-pin projection contract: ADOPT AS PROPOSED the design consult's U11-01 through U11-04 — exact-key `joulewise.identity_pin_projection_receipt.v1` receipts; canonical ordered per-unit pack shape; shared never-operator-entered model/runtime/config derivation; freeze then read-only arm verification; closed refusal vocabulary; immutable successor reissue; and U8-owned readiness consumption before GO | proposed — adopt-as-proposed consult transcription; the magistrate reviews before push (2026-08-11) |
| D-132 | STOPPING RULES TARGET DOOM LOOPS, NOT CONVERGING INSTRUMENTS (Ed, in-thread 2026-08-11): meta-process stop rules exist to kill non-converging loops — same defect recurring, no durable progress. They must NEVER terminate work on an instrument or component that is demonstrably converging (each round permanently closing its defect against a rising audit bar) when that work serves the paper: PROGRESS TOWARD A PUBLISHABLE PAPER IS THE HIGHEST-ORDER GOAL and all process rules rank below it (composing with D-119 soundness-above-all: soundness bounds WHAT may be claimed; this principle bounds when work may be STOPPED). Applied same-day: the FCM-01 stopping-rule execution is REVISED — the six-round record shows convergence, not doom-looping (arithmetic proven exact; production path sound from round 2; successive defects 0.25 J → 5e-10 J in ever-more-exotic classes) — and the estimator is REVIVED under the class-closing-by-construction design: the public registered surface is DELETED; the estimator becomes internal to the governed extraction path (the only path that may mint claims per the custody model), so no admitted-input class exists. The re-spec-to-default branch stays unmerged as the ready fallback until the revival round's delta verdict. Rust is affirmed as the H2/H3 next-generation core answer (unforgeable capability tokens), now justified by executed demonstration rather than conjecture | adopted (Ed, in-thread; transcribed by the magistrate) |
| D-133 | FCM-01 DISPOSITION — HYBRID + ALT-D120 (cold gate revised sitting, 2026-08-11): round-6 delta REJECT (FCM6-01, forged registration admitted by validators) adjudicated by fresh Fable + Opus refuter. Fallback respec/d124-withdrawn merges after its own gates (freeze lane unblocks there, decoupled from FCM); FCM-01 continues unmerged under ALT-D120 — DELETE serialized registration vocabulary so forgeries die as closed-profile unknown-key refusals (D-120 precedent); false round-6 provenance claim corrected + sixth sha rotation; FULL fresh delta owed on moved arithmetic (any exact understatement = permanent drop, no further revival); re-spec back to tighter estimator only if ALT-D120 + full delta + new mint-estimator WO all land pre-freeze-wave. Bench-verified: mint has zero estimator vocabulary (tighter floor unmintable this cycle regardless); forged field inert (no consumer); production authenticate binds expected_sha256. Ed schedule call flagged: gamma-arm-in-main-paper would make mint work critical path and hold the wave | adopted (cold gate; magistrate, no dissent) |
| D-134 | §5C ARM-READINESS RECORD CONTRACT (adopt-as-proposed consult, 2026-08-11): two-stage append-only receipts — pack-pinned non-authorizing FREEZE receipt + external pack-binding ARM receipt (hash cycle broken: frozen bytes declare the arm-receipt schema/namespace, never its future sha); d117_row_registry_v1.json sole row authority for ALPHA/BETA/GAMMA (Markdown = checked views); UNKNOWN prohibited (REFUSE or registered NOT_APPLICABLE); derive-never-enter throughout; dry-run never authorizes; impossible pre-launch single-foreground-launch row replaced by atomically consumable single-launch capability; enumerated doctrine amendments + full test obligations bind before any D-117 arm. Trace: process_traces/2026-08-11-5c-readiness-contract/ | adopted (consult adopt-as-proposed; magistrate) |
| D-135 | SITE BUDGETS ADVISORY (Ed, in-thread 2026-08-12): conservative capsule/page/shard byte budgets and pagination margins WARN, never fail builds/tests/PR gates; the ONLY failing site-size condition is the physical Lakebed 1,048,576-byte cap under the real validator (deploys physically fail past it); content is never trimmed/split/archived to satisfy an advisory budget; SITE-CAPSULE-BUDGET-01 superseded | adopted (Ed, in-thread; transcribed) |
| D-136 | SITE LANE RETIRED FROM PROCESSES (Ed, in-thread 2026-08-12): no session spends tokens on Lakebed/capsule size, packing, deploy failures, or site-chain diagnosis — the site is a status doc, not a workstream; the site workflow runs on manual dispatch only (never push/pull_request) and its results never gate anything or prompt session work; extends D-135 and D-101 addendum II | adopted (Ed, in-thread; transcribed) |
| D-137 | ARM-READINESS V1 BOOT-SESSION AMENDMENT (magistrate-ratified, 2026-08-12): every v1 arm or generic evidence receipt carrying `valid_until_monotonic_ns` also carries a derived, never-operator-entered `boot_session_id`; verification and atomic consumption refuse a boot-session mismatch as `readiness_record_expired`; composes with D-120/D-134 and deliberately supersedes the preserved D-134 consult's literal key lists before any production receipt issuance | adopted (magistrate-ratified v1 schema amendment) |

---

## D-001: Run bundles store normalized `config.json`, not YAML

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: `docs/contracts/run_bundle_layout.md` originally specified `config.yaml`
as the normalized config artifact, but the package is intentionally
zero-dependency and the stdlib has no YAML parser. The Phase 1 CLI already
rejects non-JSON configs.

Options considered:

1. Keep `config.yaml` in the bundle and add PyYAML as a core dependency.
   Pro: human-friendly artifact. Con: breaks the zero-dependency core for a
   cosmetic gain; the bundle copy is machine-written anyway.
2. Store both `config.yaml` (if input was YAML) and `config.json`. Pro:
   preserves the authored artifact. Con: two sources of truth in the bundle;
   normalization questions; still needs the dependency.
3. Store normalized `config.json` only. Pro: stdlib `json` round-trips it; the
   bundle copy is for machines and reducers, not for authoring; deterministic
   key ordering enables config hashing. Con: marginally less pleasant to read.

Decision: option 3. The bundle stores `config.json`, written with sorted keys
and a recorded SHA-256 hash in `metadata.json`.

Considerations: the bundle's job is auditability and reduction, not authoring
ergonomics. Sorted-key JSON gives us a stable config hash for free, which
Phase 4 aggregation uses to group runs. Human authoring comfort is a separate
question handled by D-007.

Consequences: `run_bundle_layout.md` updated; the bundle writer (Slice 2A)
writes JSON; config hashing is defined as SHA-256 over the sorted-key,
2-space-indented JSON encoding.

Revisit when: D-007 introduces YAML input, or a downstream consumer needs the
originally-authored file preserved.

---

## D-002: Telemetry sampling via subprocess + file, no controller threading

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: power sampling must run concurrently with the workload. The
`TelemetryAdapter` contract already has `start_sampling`/`stop_sampling`, but
nothing specified the concurrency mechanism.

Options considered:

1. Python threads inside the controller polling the telemetry source. Pro:
   single process. Con: GIL interaction with an in-process runtime (MLX
   generation) can distort sample timing; threading bugs are the classic
   source of flaky harnesses; the controller would be doing work during the
   measured window (see D-013).
2. `asyncio` event loop. Pro: no threads. Con: forces async contracts onto all
   adapters for one use case; same in-process timing concern.
3. Each telemetry adapter spawns its native sampler as a subprocess that
   writes to a file in the bundle; `start_sampling` launches it,
   `stop_sampling` terminates it and parses the file. Mock telemetry simply
   synthesizes samples. Pro: real backends (`powermetrics`, `nvidia-smi
   -lms`) are already long-running sample-emitting processes, so this matches
   their grain; the controller sleeps during the measured window; the raw
   backend output is preserved verbatim in the bundle as source of truth.
   Con: process lifecycle management per backend; parsing happens after the
   fact.

Decision: option 3.

Considerations: the deciding factors are measurement integrity (controller
does nothing during the measured window) and auditability (the raw sampler
output lands in `raw/` untouched, and `power_trace.csv` is derived from it,
so a parsing bug can be fixed and re-reduced without re-running hardware).
This also keeps the v1 controller single-threaded and therefore simple to
reason about and test.

Consequences: every real telemetry adapter defines: spawn command, raw output
path under `raw/`, stop mechanism, and a parser raw -> `PowerSample` rows.
The controller never reads samples mid-run; live progress display is out of
scope for v1.

Revisit when: a backend appears that cannot run as a file-writing subprocess,
or sub-second live feedback becomes a requirement.

---

## D-003: Timestamp and clock-alignment policy

- Date: 2026-06-09
- Status: accepted
- Phase: 2 (single node), 3 (multi node)

Context: every event and power sample carries `timestamp_s`. Reducers join
events to traces by time. Phase 3 joins traces across two machines, so clock
error becomes energy-attribution error.

Options considered:

1. Monotonic clock only. Pro: immune to wall-clock steps. Con: meaningless
   across processes and machines; cannot align controller, sampler subprocess,
   and remote nodes.
2. Wall clock (epoch UTC) only. Pro: universal meaning. Con: NTP steps/slew
   can distort intervals mid-run.
3. Epoch UTC (`time.time()`) as the canonical `timestamp_s` everywhere, with
   per-process monotonic-vs-wall offset recorded in metadata, NTP sync state
   recorded per node, and controller-mediated marker events bounding
   cross-node offset for split runs.

Decision: option 3.

Considerations: at our sampling rates (~1-10 Hz) the precision we need is
tens of milliseconds; LAN NTP holds well under that. The marker procedure
(controller timestamps a no-op command on the remote node immediately before
and after each remote stage; round-trip halving bounds the offset) gives a
recorded, per-run error bound rather than an assumption. Monotonic-only would
make multi-process correlation impossible, and our samplers are separate
processes by D-002.

Consequences: `metadata.json` gains `clock` fields (ntp_synced, estimated
offset bound, method). The methodology doc gets a Clock Synchronization
section (done in the same change as this entry). Reducers must treat
cross-node intervals shorter than the recorded offset bound as unreliable and
flag them in measurement quality.

Revisit when: sampling moves to >=100 Hz (wall meters with fast export) or a
target cannot run NTP.

---

## D-004: `powermetrics` privilege workflow

- Date: 2026-06-09
- Status: accepted
- Phase: 2

Context: Phase 1 evidence shows `/usr/bin/powermetrics` exists and "must be
invoked as the superuser". Automated benchmark runs need a non-interactive,
auditable way to obtain that privilege. Hard rule inherited from Phase 1:
document the privilege workflow, never bypass it in code.

Options considered:

1. Run the whole controller as root. Pro: simple. Con: massively
   over-privileged; everything the harness writes becomes root-owned; worst
   auditability.
2. Interactive `sudo` prompt at run start. Pro: zero configuration. Con:
   breaks unattended/repeated runs (sudo timeout mid-experiment), and an
   agent cannot answer the prompt.
3. A `sudoers` rule scoped to exactly `/usr/bin/powermetrics` (NOPASSWD) for
   the benchmark user, installed once by the user, documented in the
   Phase 1 exit checklist's instrumentation section. Controller pre-checks
   capability with
   `sudo -n /usr/bin/powermetrics -n 1 -i 100` style probe and fails with
   structured `permission_denied` if absent.
4. A setuid wrapper binary. Con: writing setuid programs to avoid a sudoers
   line is strictly worse on every axis.

Decision: option 3, with option 2 documented as the manual fallback for
one-off runs.

Considerations: the scoped sudoers rule grants exactly one binary, owned by
Apple, that only reads telemetry. The pre-check converts a mid-run privilege
failure into an up-front structured failure, which the Phase 1 contract
(structured outcomes, not crashes) requires. Passwords never appear in code,
configs, or logs.

Consequences: the powermetrics adapter (Slice 2H) always invokes via
`sudo -n`; the Phase 1 exit checklist's instrumentation section gains the
exact sudoers line for the user to install during the 2026-06-10 auth
session; `permission_denied` failures tell the operator precisely what to
add.

Revisit when: macOS changes powermetrics privilege requirements, or the
measurement machine is shared and the owner declines the sudoers rule (then
runs become operator-attended, option 2).

---

## D-005: One bundle per repetition, grouped by experiment manifest

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: `workload_profile.repetitions` exists in the config schema but
nothing defined whether N repetitions produce one bundle or N bundles.

Options considered:

1. One bundle containing N sub-runs. Pro: one directory per experiment. Con:
   every artifact (trace, events, summary) needs an internal rep dimension;
   the "bundle = one measured run" invariant breaks; partial failure of rep 3
   of 5 makes bundle status ambiguous; reducers get conditional logic
   everywhere.
2. One bundle per repetition, plus an experiment manifest
   (`runs/experiments/<experiment_id>.json`) listing member bundle IDs, the
   shared config hash, and creation time. Pro: bundle invariant stays "one
   bundle = one measured run = one status"; per-rep failure is naturally
   isolated; Phase 4 aggregation walks manifests. Con: more directories; the
   manifest is one more artifact to maintain.

Decision: option 2. Bundle IDs of members are `<experiment_id>__r<N>`.

Considerations: the strongest argument is statistical hygiene in Phase 4 -
each repetition is an independent observation with its own quality fields
(thermal drift, dropped samples), and forcing that independence into the
directory structure prevents accidental cross-rep contamination in reducers.
Partial experiments (3 of 5 reps succeeded) stay representable without a
special bundle state.

Consequences: controller gains an experiment loop (Slice 2F); cooldown gates
between reps live at the experiment level; `run_bundle_layout.md` documents
the manifest.

Revisit when: never expected; this is structural.

---

## D-006: Dashboard v1 is a static HTML report generator

- Date: 2026-06-09
- Status: accepted
- Phase: 2 (v1), 4 (figures)

Context: the original Phase 2 checklist said "dashboard v1 as a read-only run
browser" with no definition. Any web stack is a large dependency and
maintenance surface for a single-user research artifact.

Options considered:

1. Flask/FastAPI web app. Pro: interactive. Con: server process, dependency
   tree, session management for zero concurrent users; classic capstone time
   sink; violates "polish after vertical slice" rule in spirit.
2. Jupyter notebooks only. Pro: flexible. Con: not a "run browser"; execution
   state is not reproducible evidence; poor handoff artifact.
3. `python3 -m joulewise report runs/ --output report/` generating static
   HTML: an index table of runs plus a per-run page with metadata, summary
   metrics, and a power-trace chart with phase shading. Charts rendered by
   matplotlib (Agg) to PNG/SVG. No JavaScript build, no server; open the
   files in a browser.

Decision: option 3. Matplotlib becomes the first real dependency, isolated in
the `[analysis]` extra (D-009), which Phase 4 needs regardless.

Considerations: the dashboard's actual job in this project is (a) sanity-check
runs during data collection and (b) show the supervisor progress. Static
generation serves both, is testable (assert files exist and contain expected
strings), and produces committable artifacts. Interactivity has no identified
user.

Consequences: Slice 2J implements it; `report` fails with a helpful message
if matplotlib is missing; notebooks remain available for exploration but are
never the source of report figures (see Phase 4 plan).

Revisit when: a real interactive need appears (e.g., live monitoring of long
sweeps in Phase 3) - and then prefer extending the generator before adopting
a server.

---

## D-007: YAML config input is deferred

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: the CLI is JSON-only; one doc claimed YAML preference. Related to,
but distinct from, D-001 (bundle artifact format).

Options considered:

1. Add PyYAML now. Con: first core dependency, motivated by zero observed
   pain; example configs are short.
2. Defer: JSON-only input until a human actually authors enough configs for
   YAML comments/anchors to matter; then add PyYAML behind a `[yaml]` extra
   with YAML accepted at the CLI boundary only (immediately normalized to the
   JSON-backed schema).

Decision: option 2.

Considerations: Phase 2-3 configs will mostly be generated (sweeps), not
hand-authored. The cost of adding YAML later is one loader function; the cost
of adding it now is a permanent dependency and a second on-disk dialect to
test.

Consequences: CLI error message keeps stating the position ("YAML planned");
docs stop calling YAML "preferred".

Revisit when: the Phase 3 experiment matrix produces hand-edited config
sprawl that JSON makes painful.

---

## D-008: Split runs arrive via schema v0.2 (`run_kind` + `split_plan`)

- Date: 2026-06-09
- Status: accepted (design), implementation in Phase 3 Stage 3.1
- Phase: 3

Context: `BenchmarkConfig` v0.1 has exactly one `hardware_target`, so a
disaggregated run (prefill node + decode node + interconnect) is currently
inexpressible. Discovering this mid-Phase-3 would force a rushed schema
change after data collection had started.

Options considered:

1. Generalize `hardware_target` to a list of targets with role tags. Pro:
   maximally general (N-way splits someday). Con: validation becomes
   conditional on role combinations; every consumer must handle lists; we
   have no N>2 use case.
2. Add optional `run_kind: monolithic | transfer_bench | split_offline |
   split_live` (default `monolithic`) plus an optional `split_plan` object
   with named roles: `prefill_target`, `decode_target` (full HardwareTarget
   objects), and a `transfer` block (method: `file_scp` | `tcp_stream`,
   staging dir, link label). `transfer_bench` runs get a `transfer_bench`
   block (payload sizes, port) and reuse the two-target shape. Validation
   rules are explicit per run_kind (e.g., `hardware_target` required for
   monolithic, forbidden when `split_plan` present).
3. Separate config schema/file type for split runs. Con: two schemas to
   version, validate, and document; shared fields drift.

Decision: option 2, as schema_version 0.2, designed and implemented at the
start of Phase 3 (Stage 3.1) before any split data is collected. v0.1
configs remain valid: absent `run_kind` means `monolithic`.

Considerations: named roles match the experiment's fixed two-stage structure
and keep validation rules enumerable and testable. Backward compatibility by
defaulting preserves all Phase 2 configs and bundles. Designing now but
implementing at Phase 3 start avoids speculative code while eliminating the
mid-phase surprise.

Consequences: phase labels gain `deserialize`; the composite bundle layout
(nodes/prefill, nodes/decode) accompanies it; reducers learn per-stage
decomposition. All documented in the Phase 3 plan.

Revisit when: an N>2 pipeline experiment is actually proposed.

---

## D-009: Dependency policy: stdlib core, optional extras

- Date: 2026-06-09
- Status: accepted
- Phase: all

Context: the repo is zero-dependency by design ("Phase 1 can run without
dependency installation"). Phases 2-4 need MLX (Mac runtime), matplotlib
(reports/figures), and likely pandas (aggregation).

Options considered:

1. Add dependencies to core as needed. Con: `python3 -m joulewise run` on a
   bare machine stops working; CI and the mock path inherit heavy installs;
   the Phase 5 "new user runs one local benchmark from the README" promise
   gets harder.
2. Keep core stdlib-only forever. Con: re-implementing plotting/dataframes is
   absurd.
3. Stdlib-only core (schemas, controller, mock adapters, bundle writer,
   reducer v1, CLI), with extras: `[mac]` = mlx, mlx-lm; `[analysis]` =
   matplotlib (+ pandas when Phase 4 lands); `[yaml]` = pyyaml (when D-007
   triggers). Adapters import their backend lazily and return structured
   `runtime_unavailable` / `telemetry_unavailable` failures when the extra
   is absent.

Decision: option 3.

Considerations: the mock vertical slice is the project's portability proof
and CI substrate; keeping it dependency-free keeps it fast and unbreakable.
Lazy imports turn missing extras into the structured failures the contract
already requires, which doubles as a test of the failure paths.

Consequences: `pyproject.toml` gains `[project.optional-dependencies]`; CI
(D-017) installs nothing; docs state which extra each command needs.

Revisit when: a stdlib-only requirement becomes the bottleneck for core
correctness (not convenience).

---

## D-010: Run ID scheme

**2026-08-07 supersession note:** The clause later superseded by D-022 is
retained unchanged as historical context. Current rule ownership: D-022.

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: bundle directories need unique, sortable, informative names. The
config has an optional `run_id` field.

Options considered:

1. UUID4. Pro: unique. Con: opaque; directory listings become unreadable;
   sorting is meaningless.
2. Monotonic counter. Con: requires global state; collides across machines.
3. `<UTC timestamp>__<target_id>__<workload_name>__<4 hex chars>`, e.g.
   `20260610T142233Z__macbook_m3_max__smoke_short__a1b2`. Components
   sanitized to `[a-z0-9_-]`. If the config supplies `run_id`, it is used
   verbatim after sanitization, with a collision check that fails the run
   rather than overwriting (bundles are immutable evidence). Repetition
   members append `__r<N>` (D-005).

Decision: option 3.

Considerations: timestamp prefix makes `ls runs/` chronological; embedded
target/workload makes manual triage possible without opening files; the hex
suffix prevents same-second collisions; refusing to overwrite enforces the
"bundles are evidence" rule mechanically.

Consequences: bundle writer owns ID generation and sanitization; tests cover
collision behavior.

Revisit when: never expected.

---

## D-011: `summary_metrics.json` is the bundle completion marker

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: a crashed or killed run must be distinguishable from a completed one
by artifact inspection alone.

Options considered:

1. Write into `runs/<id>.partial/` and rename on completion. Pro: atomic.
   Con: a crash leaves `.partial` dirs whose artifacts (events up to the
   crash) are exactly what you want to inspect, but tooling now needs to know
   two names; rename breaks any open file handles on some platforms.
2. A `_COMPLETE` sentinel file. Pro: explicit. Con: one more artifact that
   says nothing else.
3. Define the writing order so `summary_metrics.json` is always written last,
   after all other artifacts are flushed, and define "complete bundle" as
   "directory containing a schema-valid `summary_metrics.json`". The final
   event in `events.jsonl` is `run_finalized`.

Decision: option 3.

Considerations: the summary is already mandatory and already last in data-flow
order (it is derived from everything else), so the invariant costs nothing.
`validate-bundle` (Slice 2E) checks it; aggregation (Phase 4) skips
directories without it and logs them as incomplete. Failed runs still get a
summary (status=failed) per D-012, so "incomplete" specifically means
"harness died", which is the signal we want.

Consequences: bundle writer enforces write order; reducers never run on
incomplete bundles.

Revisit when: never expected.

Amendment (2026-07-07, P2-013 group 4, C-007 resolution 2): "schema-valid
`summary_metrics.json`" is now enforced by ONE shared summary validator
used by both `BundleReader.is_complete()` and default validation
(`_check_summary`), with required keys per status: a `succeeded` summary
must carry the headline energy fields present AND finite (audit finding
B1 showed a status-only succeeded summary previously counted as complete
and valid, hiding truncated metrics); token-derived and idle-subtracted
metrics stay nullable; failed/unsupported summaries keep their looser
per-status requirements. "Complete" therefore means "contains a summary
that satisfies the per-status contract", not merely "parseable JSON
object". Historical bundles are unaffected: real corpus summaries
already carry the full field set.

Superseded in part (2026-07-15, WO-002/R3; D-043): a no-idle-baseline
reduction may remain SUCCEEDED with `energy_request_j` null under the
R3 DISTINCT absent-energy admission state — the succeeded-summary
predicate accepts it while every claim gate requiring request energy
fails closed on that state. The 2026-07-07 shared-validator amendment's
finite-energy requirement no longer binds that one admission state; see
`docs/reviews/2026-07-13-comprehensive-audit/packets/ed-rulings.json`
R3 and the WO-002 canonical predicate.

---

## D-012: Failure-reason to run-status mapping

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: `RunStatus` has `succeeded | failed | unsupported` and
`FailureReason` has eight codes, but nothing defined which reasons produce
which status. The distinction matters: `unsupported` is a *finding* the
capstone reports (hardware applicability results); `failed` is a *defect or
environment problem* to fix.

Options considered:

1. Let each adapter pick the status. Con: inconsistent semantics across
   backends; the same condition becomes a finding on one target and a bug on
   another.
2. A fixed mapping table owned by the controller:
   - `unsupported`: `did_not_fit`, `format_unavailable`,
     `unsupported_workload`, `runtime_unavailable`, `telemetry_unavailable`
     (structural incompatibility of the hardware/runtime/model/workload
     combination).
   - `failed`: `permission_denied`, `transport_unavailable`, `unknown_error`
     (operational problems that a configuration or environment change should
     fix).

Decision: option 2.

Considerations: the dividing principle is "would we publish this outcome as a
result?" A model that does not fit in 8 GB VRAM is a result; a missing
sudoers line is not. `permission_denied` is deliberately `failed` because it
is always fixable per D-004. `runtime_unavailable` is deliberately
`unsupported` because by D-009 it means "this target composition lacks this
backend", which is an applicability statement; if it occurs because an extra
simply was not installed on a machine that supports it, the run report should
say so and the run be repeated - the controller cannot distinguish these, so
the human/agent in the loop must.

Consequences: controller implements the table; tests pin it; the known
ambiguity on `runtime_unavailable` is documented in the Phase 2 plan and
flagged in run reports when it occurs.

Revisit when: a reason code appears that the table misclassifies in practice;
amend the table and this entry rather than special-casing in adapters.

---

## D-013: Controller-as-DUT mitigation for Mac-local runs

- Date: 2026-06-09
- Status: accepted
- Phase: 2

Context: in the Mac vertical slice the controller process runs on the same
machine that `powermetrics` measures. Controller activity during the measured
window pollutes the power trace; this is a measurement-validity threat no
checklist previously named.

Options considered:

1. Ignore it. Con: silently biases the flagship measurements.
2. Run the controller from a second machine over SSH even for the Mac. Pro:
   clean separation. Con: requires the SSH transport before the first real
   vertical slice, inverting the planned order; the Mac is the only always
   available device.
3. Co-residency protocol: (a) idle baseline is measured with the controller
   resident and quiescent, so the controller's floor load is inside the
   baseline that gets subtracted; (b) during the measured window the
   controller does nothing but a blocking wait on the runtime (no logging, no
   polling - log records are buffered in memory and flushed after
   `stop_sampling`); (c) the runtime adapter for local runs executes in the
   same process by design, so its cost *is* the workload; (d) document
   residual risk: controller wake-ups are zero by construction, and any OS
   background activity affects idle and load windows alike.
   AMENDED 2026-07-08 (PR #21, `255a7e6`): the quiescent window is
   MARKER-bounded, not call-bounded — the `sampling_stopped` timestamp is
   stamped immediately after the runtime returns, BEFORE adapter alignment
   capture and `stop_sampling` wind-down, so that controller/adapter
   bookkeeping is outside the reducer's measured window. Item (b)'s
   "until stop_sampling" phrasing predates this and reads call-bounded;
   the stamp is the boundary.

Decision: option 3 for Phase 2, with option 2 recorded as the upgrade path
once the SSH transport exists (re-run a subset and compare).

Considerations: idle subtraction already exists in the methodology; making
the controller part of the measured system's *idle* state is the cheapest way
to cancel its first-order effect. Deferred logging is essential - a single
log line during a 1 Hz window is a visible artifact.

Consequences: controller gains an explicit quiescent-wait mode and deferred
log flush; methodology doc gains a Controller Co-Residency section; the
comparison run is queued as a Phase 3-era validation task.

Revisit when: the SSH-based comparison shows a measurable delta, in which
case Mac headline numbers move to remote-controlled runs.

---

## D-014: Statistical protocol for repeated runs

**2026-08-07 supersession note:** The clauses later superseded by D-053 and
D-077 are retained unchanged as historical context. Current rule ownership:
D-053 and D-077.

- Date: 2026-06-09
- Status: accepted (draft to be ratified against real variance data at Phase 4
  Stage 4.0)
- Phase: 2 (collection), 4 (analysis)

Context: acceptance criteria say "repeated runs report variance" and
"uncertainty intervals" with no method defined. Choosing after seeing data
invites motivated choices; choosing now and ratifying with documented
reasoning is auditable.

Options considered (per element):

- Repetitions: n=3 (cheap, wide CIs) vs n=5 (headline-defensible, ~2.8x t
  multiplier instead of ~4.3x at 95%) vs n>=10 (hardware time we may not
  have). Chosen: n>=5 for headline comparisons, n>=3 minimum elsewhere,
  recorded per experiment.
- Interval: normal z (wrong at small n) vs Student t (standard at small n,
  assumes rough normality) vs bootstrap percentile (assumption-light but
  unstable at n=5). Chosen: report mean, sample stddev, and 95% t-interval;
  run a bootstrap sensitivity check in Phase 4 and report both where they
  disagree materially.
- Outliers: silent removal (never), keep-all (can bury a real artifact), flag
  via modified z-score on MAD > 3.5 and *report with and without, with the
  physical cause investigated and documented*. Chosen: the latter; a flagged
  point with no identified cause is kept in headline numbers.
- Ordering: condition blocks (thermal drift confounds with condition) vs
  round-robin interleaving (decorrelates slow drift; more model reloads).
  Chosen: round-robin across conditions where reload cost permits, with the
  executed order recorded in the experiment manifest; where blocks are
  operationally forced, that is recorded too.
- Thermal equilibrium between reps: fixed sleep (blind) vs temperature
  threshold (sensor availability varies by target) vs idle-power recovery
  gate. Chosen: idle-power recovery - wait until a rolling 30 s idle-power
  mean returns to within 10% of the run's recorded idle baseline, with a
  5-minute cap (cap hit => recorded in measurement quality).

Decision: as chosen above; figures always show raw points alongside
aggregates.

Considerations: every element was picked to survive a hostile question in a
capstone defense: "why n=5", "why t", "did you drop points", "did thermal
state drift". The idle-power gate was chosen over temperature because it uses
the instrument we always have (the power meter itself) and directly measures
the quantity whose drift would bias us.

Consequences: methodology doc gains the Statistical Protocol section;
controller implements the cooldown gate (Slice 2F); Phase 4 Stage 4.0
ratifies or amends with observed variance, updating this entry's status.

Revisit when: Phase 4 Stage 4.0, mandatorily.

---

## D-015: Split-mechanism priority and same-runtime rule

- Date: 2026-06-09
- Status: accepted
- Phase: 3

Context: the headline experiment splits prefill and decode across machines,
which requires moving KV-cache state. KV tensors are runtime-specific
(layout, dtype, quantization, RoPE handling), and not every runtime can
export or import them. This is the project's largest feasibility risk
(R-004, R-005).

Options considered:

1. Live KV streaming between runtimes first (Splitwise-style). Pro: closest
   to the inspiration paper. Con: hardest variant of the riskiest component;
   no public stable path in vLLM, none at all across heterogeneous runtimes;
   a failure here late in the schedule sinks the phase.
2. Cross-runtime transfer via a translation layer (e.g., vLLM prefill ->
   MLX decode). Con: deep model-internals work, research-grade in itself,
   out of scope for a measurement capstone.
3. Feasibility-ordered ladder with a guaranteed floor:
   a. *Synthetic transfer microbenchmark* (always feasible): move
      KV-sized payloads between nodes with both-end power sampling. Yields
      transfer energy/time vs payload size vs link speed regardless of any
      runtime's cooperation.
   b. *Offline replay* (primary mechanism): same runtime family on both
      ends; prefill on node A, persist the prompt cache to a file, transfer
      it, resume decode from it on node B. Candidate paths: mlx-lm prompt
      cache save/load; llama.cpp `--prompt-cache` session files; vLLM
      expected unsupported for file replay (spike confirms).
   c. *Live split* (stretch): socket streaming during a run, only attempted
      after (b) produces publishable data.
   Rule: same runtime (and pinned version) on both ends of any real KV
   transfer; cross-runtime KV portability is explicitly out of scope, and
   heterogeneous *hardware* pairs are achieved with a portable runtime
   (llama.cpp) where its backends allow.

Decision: option 3.

Considerations: the ladder converts an existential risk into a bounded one:
even if every runtime spike fails, (a) plus Phase 2 homogeneous baselines
still supports an analytical split-energy model (prefill energy measured on
A, decode energy measured on B via replay-or-monolithic decomposition,
transfer energy measured synthetically), which is an honest, defensible
capstone result. Each rung up improves directness of measurement. The
same-runtime rule eliminates the one problem (tensor portability across
engines) that no amount of harness engineering can fix on schedule.
Open question carried into the spikes: llama.cpp session-file portability
across *backends/platforms* (CUDA-save -> Metal-load) is unverified and gets
its own spike with an explicit verdict.

Consequences: Phase 3 plan is structured around the ladder (Stage 3.0
spikes before any hardware scheduling); the KV-size analytical model feeds
payload sizes for (a); verdict codes per runtime are recorded in
`docs/phase_3/kv_feasibility.md`.

Revisit when: a spike contradicts an assumption (then the ladder re-ranks,
documented), or vLLM's disaggregation API stabilizes early enough to matter.

---

## D-016: Benchmark model selection

**2026-08-07 supersession note:** The clause later superseded by D-073 is
retained unchanged as historical context. Current rule ownership: D-073.

- Date: 2026-06-09
- Status: open (criteria fixed now; closure requires Phase 1 supervisor scope
  plus Phase 2 install evidence)
- Phase: 2+

Context: every cross-target comparison needs identical model(s). The example
config's `qwen-placeholder` must become a real decision before Slice 2G.

Selection criteria (fixed now):

1. Must run on all primary targets: MLX-format weights available (or
   convertible) for Mac; GGUF available for llama.cpp paths; vLLM-loadable
   for the CUDA path.
2. Must fit the smallest VRAM targets at the chosen quantization: 8 GB
   (RTX 3050, Orin Nano) with headroom for KV at experiment prompt lengths.
3. KV-per-token small enough that transfer payloads span an interesting
   range (see Phase 3 KV table) but large enough to exercise the
   interconnect.
4. Open weights with a license permitting academic benchmarking and local
   mirroring (R-014: mirror weights locally once chosen).
5. Prefer one small + one mid model from the same family to separate
   model-size effects from family effects.

Candidate set (to be narrowed with evidence): Qwen2.5-1.5B-Instruct,
Qwen2.5-7B-Instruct, Llama-3.2-1B-Instruct, Llama-3.2-3B-Instruct,
Llama-3.1-8B-Instruct.

Options considered (shape of the decision): single model (cleanest matrix,
no size axis) vs small+mid pair (size axis, double hardware time) vs per-
target best model (incomparable - rejected outright).

Decision pending; leaning small+mid pair from one family, final call
recorded here with per-runtime artifact paths and exact revisions when
closed.

**Provisional pick recorded (2026-07-06, user-directed build-out session;
gate = explicit user go-ahead, recorded in the run report):**
Qwen2.5-1.5B-Instruct as the small model, MLX 4-bit artifact
`mlx-community/Qwen2.5-1.5B-Instruct-4bit`, revision
`8b403126fc14f14cfc99bb4cfa72ecbc129ea677`, mirrored locally (R-014) at
`/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit` (839 MB).
Evidence: HF repo verified via API 2026-07-06; loaded and generated on
the M3 Max via Slice 2G (bundle `example-mac-mlx-mock-telemetry`,
265.8 tok/s decode); KV row verified against the mirrored config.json
(28,672 B/token fp16, matches the Phase 3 table). This opens the 2G gate
("closed or provisional") ONLY. Full closure still requires: P1-001
supervisor scope, the mid-model pick (leaning Qwen2.5-7B-Instruct, same
family per criterion 5), a CUDA-target load, and GGUF artifact paths.
The provisional pick is reversible at config level (one model stanza +
pinned hash update).

Closure evidence required: supervisor scope notes (P1-001); successful load
on Mac MLX (Slice 2G) and one CUDA target; recorded weight artifact
paths/revisions; KV-size table row computed for the chosen models.

Revisit when: a chosen model's weights become unavailable or a target cannot
load it (then the recorded fallback candidate is promoted).

Amended (2026-07-15, WO-019; D-043): CI scope extends beyond the core
suite — a clean-clone publication release check (`scripts/release_check.py
--dry-run`, real temporary-directory execution of every non-secret seam)
and the WO-021 `gen_state.py --check` drift gate are CI jobs; credential-
bearing steps (deploy) remain outside CI per D-068 and the publication
release checklist.

---

## D-017: CI scope

- Date: 2026-06-09
- Status: accepted
- Phase: all

Context: the GitHub remote has no CI; agents benefit from remote green-check
evidence, and Phase 5 promises a reproducible mock path.

Options considered:

1. No CI. Con: "tests pass" claims rest on local runs in handoff notes.
2. Full matrix with extras (mlx cannot install on Linux runners; GPU absent).
   Con: impossible or meaningless for hardware paths.
3. Core-only CI: ubuntu runner, Python 3.11 and 3.14 (oldest supported per
   `pyproject.toml`, plus the version observed in local development),
   `python -m unittest discover -s tests` plus CLI smoke
   (`validate-config` on both example configs). Later phases extend it with
   the mock-bundle end-to-end run and `validate-bundle` once those exist.

Decision: option 3.

Considerations: the stdlib-only core (D-009) is exactly the testable surface
on a hosted runner; hardware adapters are validated by run bundles, not CI.
Two Python versions catch the realistic compat risks (3.11 floor vs 3.14
local) at trivial cost.

Consequences: `.github/workflows/ci.yml` added; Phase 2 Slice 2E adds the
mock end-to-end step to it; README badges optional, not required.

Revisit when: a self-hosted runner with GPU/Mac hardware ever materializes
(unlikely; not planned).

---

## D-018: Per-backend `power_w` definition and rail policy

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: `power_trace.csv` has `power_w`, `source`, and optional `rail`
columns, but "power" means different physical boundaries on different
backends (SoC subsystems vs GPU board vs module input vs wall AC). Without a
fixed definition, cross-target comparisons silently compare different
quantities.

Options considered:

1. One `power_w` row per sample, backend decides what it means. Con: loses
   per-rail information; the meaning varies invisibly.
2. Per-rail rows only, reducers sum everything. Con: "everything" differs by
   backend; accidental double counting (e.g., a backend reporting both
   package and per-subsystem rails).
3. Per-rail rows preserved as reported, plus a per-backend *rail manifest*
   that names exactly which rails sum to the backend's canonical `power_w`
   for reduction, and a methodology table stating each backend's physical
   measurement boundary. powermetrics: cpu_power + gpu_power + ane_power
   (SoC subsystem proxy; excludes display, storage, PSU losses). nvidia-smi:
   board power as reported (GPU board only; excludes host). jetson_rails:
   VDD_IN preferred (module input) with the actually-used rail recorded.
   wall_meter: AC wall power (full system).

Decision: option 3.

Considerations: per-rail rows keep raw fidelity (Apple's per-subsystem split
is itself interesting data); the manifest makes the summation auditable and
fixable post hoc; the boundary table converts an implicit comparability
problem into an explicit, reportable limitation - cross-target absolute
comparisons must state boundaries, and wall-meter deltas (when the meter
exists, P1-003) calibrate the gap.

Consequences: telemetry adapters declare their rail manifest in
`device_metadata`; reducer sums per the manifest; methodology gains the
Measurement Boundaries section; the limitations section of the final report
inherits the boundary table.

Revisit when: a backend exposes a strictly better boundary (e.g., macOS adds
package-level wall-equivalent reporting).

---

## D-019: Mock adapters use simulated time via an injectable clock

- Date: 2026-06-09
- Status: accepted
- Phase: 2

Context: reducer correctness tests need traces and events whose expected
energy is computable in closed form; the controller needs real time for real
runs. If mocks sleep through real seconds, tests get slow and flaky; if the
controller special-cases mocks, the lifecycle under test diverges from the
real one.

Options considered:

1. Mocks sleep in real time. Con: a 30 s idle window makes the test suite
   unusable; timestamp jitter breaks exact assertions.
2. Controller branches on mock backends. Con: the code path being tested is
   no longer the production path.
3. A minimal `Clock` protocol (`now() -> float`, `sleep(seconds)`) injected
   into the controller; `SystemClock` for real runs, `FakeClock` that
   advances instantly for tests and mock runs. Mock adapters compute
   deterministic timestamps/samples from the config and the injected clock;
   the controller code path is identical in both modes.

Decision: option 3.

Considerations: this is the standard seam for time-dependent systems; it
keeps the mock vertical slice fast (CI, D-017), exact (reducer tests assert
energy to the float), and honest (same controller code). The mock telemetry
trace is specified in Slice 2B as piecewise-constant power levels per
lifecycle stage so trapezoidal integration has a closed-form expectation.

Consequences: controller and adapters take a clock parameter; no module ever
calls `time.time()`/`time.sleep()` directly except `SystemClock`.

Revisit when: never expected.

---

## D-020: CLI binds `FakeClock` for all-mock runs, `SystemClock` otherwise

- Date: 2026-06-12
- Status: accepted
- Phase: 2

Context: D-019 created the clock seam but left open which clock the
`run` verb binds. With `SystemClock`, a mock end-to-end run sleeps
through real idle/warmup seconds and produces nondeterministic
timestamps; the mock path's whole value (fast CI substrate, exact
closed-form expectations, byte-identical reruns) depends on simulated
time.

Options considered:

1. Always `SystemClock`. Pro: one rule. Con: mock e2e takes wall-clock
   seconds in CI for no measurement benefit; timestamps differ per run,
   so determinism can only be asserted in unit tests, never on real CLI
   artifacts.
2. An explicit `--fake-clock` flag. Pro: caller control. Con: the flag
   would be mandatory-in-practice for mock runs and dangerous-if-misused
   for real runs (simulated timestamps in a hardware bundle would corrupt
   evidence silently).
3. Selection by composition at the CLI boundary: `FakeClock` if and only
   if both `runtime_backend` and `telemetry_backend` are `mock`,
   `SystemClock` otherwise. The clock kind is recorded in
   `metadata.json` (`clock.kind`), so every bundle states which time base
   produced it.

Decision: option 3.

Considerations: this is not the controller-branches-on-mocks anti-pattern
D-019 rejected - the controller code path is identical; only the injected
dependency differs, chosen at the outermost boundary. Mixed compositions
(e.g. Slice 2G's real MLX runtime + mock telemetry) correctly get
`SystemClock`, because real workload execution needs real time even when
power is synthetic. Library callers of `run_benchmark` always pass their
own clock explicitly; the rule binds only the CLI default.

Consequences: `cli.py`'s `run` verb implements the rule with a comment
citing this entry; the CI mock end-to-end step is effectively instant;
`metadata.json` discloses the time base per bundle.

Revisit when: a mixed mock/real composition needs simulated time, or a
test needs to drive the CLI with a seeded clock (then add the explicit
flag from option 2 with a refuse-on-real-telemetry guard).

---

## D-021: Controller flushes `events.jsonl` before the reduce stage

- Date: 2026-06-12
- Status: accepted
- Phase: 2

Context: the controller buffers all events in memory and flushes them
only at `_finish()` (D-013 deferred logging keeps the measured window
quiescent). Slice 2D's reducer is a pure function over the on-disk bundle
artifacts (D-002), including `events.jsonl`, and the controller calls it
during the reduce stage - which originally ran *before* the buffered
events were written. The reducer would have read an empty `events.jsonl`
(no measured-run window, no token events). The 2C author flagged this for
2D.

Options considered:

1. Pass the in-memory events to the reducer directly. Con: breaks the
   D-002 contract that `reduce_bundle(path)` is pure over on-disk
   artifacts - the same function is reused by `validate-bundle` and the
   report generator, which only have the files; two code paths would
   diverge.
2. Flush `events.jsonl` once, before the reducer runs in the reduce
   stage, and have `_finish()` (the failure paths included) flush only if
   not already flushed. `finalize()` still appends `run_finalized` last
   and writes `summary_metrics.json` last (D-011 unchanged).

Decision: option 2. The flush is a delta flush keyed on a flushed-count,
not a strict one-shot: the reduce stage's own `stage_completed` event is
buffered *after* the in-reduce flush, so a strict one-shot would drop it
and break the event-sequence contract. Each `_flush_events` call appends
only events buffered since the previous flush, stable-sorted within the
batch; later batches are strictly later in time, so global order holds.

Considerations: this keeps the reducer honest (pure over files, so a
reducer bug is fixed by re-reducing the bundle, never by re-running
hardware) while preserving D-011 (summary still last) and D-013 (the
flush happens in the reduce stage, well after `stop_sampling`).

Consequences: `events.jsonl` exists and is complete (minus the trailing
`run_finalized`) at reduce time; failure paths, which never reach reduce,
still flush their buffered events exactly once in `_finish()`.

Revisit when: events grow large enough that buffering the whole run in
memory is a problem (then stream to a temp file and swap on finalize).

---

## D-022: Auto-generated run-ID suffix is config-hash-derived, not random

- Date: 2026-06-12
- Status: accepted (refines D-010)
- Phase: 2

Context: D-010 specified the auto-generated run ID as
`<ts>__<target>__<workload>__<4 hex>` with the 4-hex suffix from
`secrets.token_hex(2)` to prevent same-second collisions. A random suffix
makes the run ID - which is embedded in the `run_started` event and in
`metadata.json` - differ across otherwise-identical runs, violating the
Slice 2B acceptance criterion "identical config + clock seed =>
byte-identical events" for any valid config that omits `run_id` (the
adversarial review confirmed this empirically).

Options considered:

1. Keep `secrets.token_hex(2)`. Con: breaks the determinism criterion for
   the no-`run_id` case; the byte-identity guarantee then silently
   depends on the operator always supplying a `run_id`.
2. Drop the suffix entirely. Con: loses cross-config disambiguation when
   two different configs share a target/workload/second.
3. Derive the 4-hex suffix from the config's content hash (first 4 hex of
   the SHA-256 over the canonical config bytes, the same bytes that feed
   `config_sha256`). Deterministic per config; different configs get
   different suffixes; identical configs get identical IDs.

Decision: option 3. The suffix is `config_sha256[:4]`.

Considerations: this satisfies the determinism criterion (identical
config + clock => byte-identical run ID, events, and metadata) while
keeping cross-config disambiguation. The residual collision case -
identical config, same UTC second, same runs dir - now produces the same
ID and is refused by the immutable-evidence rule (D-010: never overwrite
a bundle), which is the correct response to "you are about to write a
second bundle for the identical config in the same second". Repetitions
never collide: the experiment runner assigns distinct `__rN` run IDs
(D-005/D-010), each a supplied `run_id` that bypasses the generated form.

Consequences: `generate_run_id` computes the suffix from the config hash;
`metadata.run_id` and the `run_started` event are now deterministic for a
fixed config; a run-benchmark-level determinism regression test pins it.

Revisit when: a use case genuinely needs two same-config same-second
bundles in one directory without the experiment runner (then reintroduce
a disambiguator, e.g. a monotonic counter rather than randomness, to keep
determinism).

---

## D-023: Per-item phase status lives solely in the exit checklists

- Date: 2026-07-05
- Status: accepted
- Phase: all

Context: project status was being recorded on six surfaces (phase plan
headers and per-step lines, exit checklists, `AGENT_PLAN.md` checkboxes,
`TASK_QUEUE.md`, `RUN_STATE.md`, `PROJECT_STATUS.md`). The 2026-07-05
planning audit found same-day drift from the 2026-06-12 run:
`phase_1_plan.md` still marked the Hailo verdict and readiness review
"open" after the checklist closed them, and `phase_2_plan.md`'s header
still read "planned" with 7 of 13 slices complete. The replication
exceeded one operator's update discipline on the project's busiest day,
which is exactly when drift is most misleading.

Options considered:

1. Keep all six surfaces and try harder. Con: already failed empirically;
   discipline does not scale with excitement or fatigue.
2. Exit checklists become the single per-item status authority; phase
   plan files carry no status (header points at the checklist; per-step
   status lines removed); `AGENT_PLAN.md` keeps a coarse checkbox mirror
   updated at slice/phase closes; `TASK_QUEUE.md`/`RUN_STATE.md` remain
   work-selection and handoff views (different content, not duplicated
   status); `PROJECT_STATUS.md` remains the derived advisor summary.
3. Generate a status dashboard from one machine-readable source. Con:
   tooling investment the project does not need yet; a script is its own
   maintenance surface.

Decision: option 2. The evidence matrix in
`docs/phase_N/phase_N_exit_checklist.md` is the only place a per-item
status is asserted; every other document either points there or mirrors
coarsely and says so.

Considerations: plans stay useful as timeless specs (objectives, gates,
design, acceptance) that do not rot when work completes; the checklist
was already the evidence dossier, so status naturally colocates with the
evidence that justifies it; the coarse `AGENT_PLAN.md` mirror is retained
because it is the cross-phase index agents read first, and its checkbox
grain (one line per slice) is cheap to keep honest. The same audit drove
a companion dedup: `phase_2_plan.md` owns each gated slice's
what/when/done while the hardware guide owns the how, replacing the
previous near-verbatim duplication.

Consequences: all five plan headers now read "Status: tracked in the
exit checklist"; `phase_1_plan.md` per-step status lines removed; the
source-of-truth map in `AGENT_PLAN.md` updated to name the checklists as
status authority; plan/guide duplication for slices 2G-2M cut to
pointers.

Revisit when: the `AGENT_PLAN.md` coarse mirror is found drifted again -
then replace the mirror with a generated table (option 3) rather than
adding discipline.

---

## D-024: Adapters receive a `RunContext`, not piecemeal parameters

- Date: 2026-07-06
- Status: accepted; implemented in Slice 2N.1 (2026-07-06)
- Phase: 2

Context: mock adapters get by on `config` (plus `clock` at construction),
but real adapters need more: a place to write raw telemetry evidence
(D-002; powermetrics plist), log/output paths, the run ID, and - in
Phase 3 - the node's role in a split run. Slice 2N.1 originally left the
delivery mechanism open (new parameter vs writer injection vs context
object). An external architecture review (Codex, 2026-07-06) recommended
deciding now, before any real adapter is written against a narrower
seam.

Options considered:

1. Add parameters piecemeal as needs appear (e.g.
   `start_sampling(raw_dir=...)`). Con: every future need is another
   signature break across all adapters and their tests; Phase 3 alone
   would force two more rounds.
2. Inject the `RunBundleWriter` into adapters. Con: hands adapters the
   power to write summaries/finalize - far more authority than they
   need; couples every adapter to the writer's full API.
3. A small immutable `RunContext` dataclass passed to adapter lifecycle
   methods: `config`, `clock`, `run_id`, `bundle_path`, `raw_dir`,
   `logs_dir`, `outputs_dir`, and optional `node_role` (None for
   single-node runs; used by Phase 3 split orchestration).

Decision: option 3. One additive seam that covers the known Phase 2
needs (raw evidence, logs) and the foreseen Phase 3 needs (node role,
composite bundles) without granting adapters bundle-lifecycle authority.

Considerations: the context is data, not capability - adapters get paths
and identity, not the writer; write-order/immutability invariants stay
with the controller and writer. `node_role` rides along as an optional
field now precisely so the v0.2 compatibility check (2N.9) can exercise
it without any schema change (R-015 intact). Mocks accept the context
and ignore what they do not need, keeping one lifecycle code path.

Consequences: `interfaces.py` adapter protocols take a context in their
lifecycle methods (exact placement pinned during 2N.1);
`adapter_contracts.md` updated in the same run; the controller
constructs the context after bundle creation.

Revisit when: a need appears that is per-call rather than per-run (then
a per-call argument is correct, not a context field), or Phase 3's
composite-bundle design (D-008) demands fields that would make the
context mutable - mutability is the line not to cross.

Amendment (2026-07-06, 2N.1 implementation): placement is pinned as a
trailing optional per-method parameter (`context: RunContext | None =
None`) on every adapter lifecycle method, not construction-time
injection. Rationale: the D-014 cooldown gate invokes `measure_idle`
between repetitions when no bundle is open, and direct adapter tests
call methods outside any run; optionality keeps one lifecycle code path
while the controller always supplies the context. Adapters must produce
no raw output when the context is absent. The writer-side counterpart is
`RunBundleWriter.raw_path`/`write_raw` (validated plain file names,
collision-checked, closed by `finalize()`); adapters never receive the
writer - they write into `context.raw_dir` directly.

---

## D-025: One shared bundle read layer for all bundle consumers

- Date: 2026-07-06
- Status: accepted; implemented in Slice 2N.8 (2026-07-06, `joulewise/bundle_read.py`)
- Phase: 2

Context: three code paths already parse bundles independently -
`reduce.py` (trace/events/manifest for metrics), `report.py` (the same
for charts), and `cli.py` `validate-bundle` (structural checks) - and
they have already diverged once: the report sums all rails when the
manifest matches nothing while the reducer excludes/fails (2N.7
finding). Phase 4's `aggregate` verb would be a fourth parser. An
external architecture review (2026-07-06) recommended a shared read
layer before the divergence class grows.

Options considered:

1. Keep per-consumer parsing, fix mismatches as found. Con: the 2N.7
   bug recurs in new forms; every policy (rail manifest, measured
   window, completeness) must be kept aligned by vigilance across four
   files.
2. A shared `BundleReader` (in `joulewise/bundle.py` or a new
   `bundle_read.py`): loads config, metadata, events, power trace, rail
   manifest, measured/phase windows, completion state, and structural
   problems - one implementation of every bundle-interpretation policy;
   consumers apply presentation/reduction on top.
3. Full ORM/database layer now. Con: heavyweight; Phase 4's CSV plan
   plus a possible stdlib-sqlite cache (Stage 4.1 note) already covers
   querying needs.

Decision: option 2. Reducer, report, `validate-bundle`, and (later)
`aggregate` all consume the shared reader; policy questions like "which
rails sum to `power_w`" are answered in exactly one place.

Considerations: this is the code-level analogue of D-023's one-fact-one-
home rule; the reducer's math (`_integrate`, idle subtraction) stays in
`reduce.py` - the reader owns parsing and policy, not metrics. The 2N.7
report/reducer alignment must be implemented BY building on the reader,
not as a spot fix, or the divergence just reappears at the next
consumer.

Consequences: Slice 2N gains item 2N.8; 2N.7 is implemented on top of
it; Phase 4 Stage 4.1's aggregate verb builds on the reader (noted in
the Phase 4 plan).

Revisit when: bundle schema v0.2 lands (the reader is where composite-
bundle reading concentrates), or a consumer needs streaming reads that
the whole-bundle reader cannot serve.

---

## D-026: Measured window is bounded by sampling-active marker events

- Date: 2026-07-06
- Status: accepted (Slice 2N.2)
- Phase: 2

Context: the reducer integrated energy between the `measured_run`
`stage_started` and `stage_completed` events. `stage_started` is stamped
before `thermal_state` and `start_sampling`, and `stage_completed` after
`stop_sampling`, `thermal_state`, and the outputs/trace writes - so under
`SystemClock`, real sampler spawn latency (sudo probe, process start,
first sample) and wind-down cost (process stop, plist parsing) land
inside the integrated window, inflating gross energy, the
idle-subtraction duration, and TTFT. `FakeClock` collapses these
intervals to zero, so the mock suite could never catch it.

Options considered:

1. Reorder the stage boundary: stamp `stage_started(measured_run)` only
   after `start_sampling` confirms. Con: a `start_sampling` failure would
   then be attributed to a stage that never started, breaking the event
   invariant that a failing stage has a `stage_started`; and the stage
   end would still include post-window artifact writes.
2. Explicit `sampling_started`/`sampling_stopped` marker events on the
   `measured_run` phase; the reducer integrates between markers, falling
   back to stage boundaries for pre-2N bundles.

Decision: option 2. `sampling_started` is stamped only after
`start_sampling` returns ok (sampling confirmed active);
`sampling_stopped` is stamped before `stop_sampling` is invoked (the
wind-down happens after the window closes). TTFT is measured from
`sampling_started`. The failure path's best-effort stop records the same
closing marker, so post-hoc re-reduction sees identical window semantics.

Considerations: stage boundaries keep their operational meaning (what the
controller was doing when) while the markers own the measurement
semantics - two facts, two event types. The two marker buffer-appends are
the only in-memory buffer touches inside the D-013 quiescent window
(negligible; nothing touches disk). The stop marker is appended to the
buffer after the runtime events so the stable flush-sort keeps it
bracketing them. Additive event types keep R-015 intact
(`validate-bundle` checks event keys, not a type whitelist).

Consequences: `_measured_window` in `joulewise/reduce.py` prefers the
markers and falls back to stage boundaries; telemetry adapters must not
return from `start_sampling` before sampling is actually running
(recorded in `adapter_contracts.md`); a latency-simulating telemetry test
pins the exclusion.

Revisit when: a real adapter cannot confirm sampling start
synchronously (would need an async readiness probe), or Phase 3 split
runs need per-node windows (D-008 composite bundles).

---

## D-027: Per-rail rows must share per-sample timestamps; misalignment is a structured failure

- Date: 2026-07-06
- Status: accepted (Slice 2N.4)
- Phase: 2

Context: `power(t)` sums `power_w` over the manifest rails grouped by
exact `timestamp_s` equality (D-018). A real multi-rail adapter (e.g.
Jetson rails) emitting per-rail rows with slightly skewed timestamps
would silently produce an interleaved per-rail curve whose integral
badly undersums the true power - a wrong number with no error, the worst
failure mode for a measurement harness. The grouping rule lived only in
a `bundle.py` comment.

Options considered:

1. Bucket timestamps within a tolerance derived from the sampling
   interval. Con: silently rewrites the data; the bucket width is a new
   free parameter; boundary cases (a sample near a bucket edge) move
   energy between samples invisibly.
2. Detect-and-fail: with a multi-rail manifest, every timestamp on the
   summed curve must carry exactly the full manifest rail set; a subset
   is a structured failure naming the timestamp and missing rail(s).

Decision: option 2. The contract is now explicit: a telemetry adapter
emits one row per rail per sample instant, all sharing that instant's
single timestamp (row fan-out per rail, one clock read per sample).
Adapters that sample rails at genuinely different instants must
resample/align before emitting rows - alignment policy belongs to the
adapter that knows its hardware, not to a generic bucketer.

Considerations: honesty over convenience - the project's core promise is
boundary-honest energy numbers, so a detectably wrong sum must fail
loudly (R-015 unaffected: no schema change). Single-rail manifests
cannot misalign; the check costs one set comparison per timestamp.
Enforcement lives in `BundleReader.summed_curve` (D-025), so the
reducer, report, and any future consumer inherit it identically.

Consequences: `adapter_contracts.md` telemetry section documents the
row contract; the reducer converts the reader's misalignment failure
into a structured FAILED summary; skewed/aligned twin fixtures pin both
sides.

Revisit when: a real telemetry backend cannot share one timestamp
across rails at source (then the adapter grows an explicit, tested
alignment step - still adapter-side, not reader-side).

Amendment (2026-07-07, P2-013 group 4, C-007 resolution 4): the rail-set
rule is extended to DUPLICATES — at any timestamp on the summed curve,
each manifest rail must appear exactly once; a duplicate rail row at one
timestamp (including the single-rail case) is rejected rather than
summed, since silent double-counting is the same wrong-number failure
mode as undersumming (audit finding B5). Enforcement stays in the one
shared trace-validation path consumed by both `summed_curve()` and
default validation, so all consumers inherit it identically (D-025).

---

## D-028: `reduce` verb rewrites `summary_metrics.json` in place

**2026-08-07 supersession note:** The clause later superseded by D-078 is
retained unchanged as historical context. Current rule ownership: D-078.

- Date: 2026-07-06
- Status: accepted (Slice 2N.6)
- Phase: 2

Context: D-002's promise - a reducer bug never re-runs hardware - needs
a user-facing path: `python3 -m joulewise reduce <bundle-dir>`
re-derives the summary from the raw artifacts. D-011 makes
`summary_metrics.json` the completion marker written last by
`finalize()`, and bundles are otherwise immutable evidence (D-010), so
where the re-derived summary lands is a real policy choice.

Options considered:

1. Rewrite `summary_metrics.json` in place. Pro: one summary, every
   consumer (validate-bundle, report, Phase 4 aggregate) keeps working
   unchanged; the summary is by definition derived from the raw
   artifacts, so rewriting it destroys no evidence.
2. Write a versioned name (`summary_metrics.v2.json`). Con: every
   consumer needs a resolution rule for which summary wins; the D-011
   completion marker becomes ambiguous; stale headline numbers linger in
   the canonical file.

Decision: option 1. In-place rewrite is the ONE sanctioned
post-finalize bundle mutation; everything else in a finalized bundle
stays immutable. The verb refuses paths without a `config.json` (exit
2, no write) so evidence is never invented inside an arbitrary
directory; degenerate bundle contents produce a structured FAILED
summary (exit 3); success exits 0 - matching `run`'s exit scheme, with
the same greppable `bundle:` result line.

Considerations: the raw artifacts (config, events, trace, raw/, logs)
remain the evidence of record; the summary is a cache of derivation.
If provenance of a re-reduction ever matters, the harness git commit is
already in `metadata.json` and the rewrite is reproducible from it.

Consequences: `reduce_bundle` returns structured failures for
missing/corrupt `config.json`/`metadata.json` (keeping its docstring's
"never crashes" promise); `run_bundle_layout.md`'s immutability language
gains this exception; CLI help documents the verb.

Revisit when: Phase 4 aggregation needs to distinguish "reduced by
which harness version" across a corpus (then a provenance field inside
the summary - additive, R-015 - beats a versioned file).

---

## D-029: Config schema declares nullable optionals; serialization unchanged

- Date: 2026-07-06
- Status: accepted (Slice 2N.5)
- Phase: 2

Context: `BenchmarkConfig.to_dict()` (dataclass `asdict`) emits `null`
for absent optionals, but the hand-written exported JSON Schema declared
those properties non-nullable - so a bundle's normalized `config.json`
failed external validation against `print-config-schema` output. The
harness's own `from_mapping` tolerated the nulls, hiding the mismatch
from every internal path.

Options considered:

1. Omit-None serialization: `to_dict()` drops null-valued keys. Pro:
   smaller, arguably cleaner artifact. Con: changes the config bytes and
   therefore every config SHA-256 - which is run identity (D-001 bundle
   hash, D-022 run-ID suffixes, D-005 experiment grouping). Acceptable
   only while no real bundles exist, and it buys nothing measurable.
2. Schema declares nullable optionals (`"type": ["string", "null"]`
   etc.), serialization untouched. Pro: hashes stable; an explicit
   `"field": null` and an absent field validate identically; the schema
   now tells external consumers the truth about emitted artifacts.

Decision: option 2 (also what the Phase 2 plan's 2N.5 text pins). Every
optional the emitter can produce as `null` is declared nullable;
numeric constraints (`minimum`) are unaffected by the null arm under
JSON Schema 2020-12.

Considerations: config-hash stability is worth protecting even
pre-hardware - the mock e2e byte-determinism tests (D-022) already
depend on it. A pinned-hash test now guards the serialization: any
future change to `to_dict()` bytes fails loudly and must come back
through this log.

Consequences: `schemas.py` `json_schema()` updated; round-trip tests
assert (a) every null-emitted field is schema-nullable and every
emitted key is schema-known on bare Python, (b) full `jsonschema`
validation where that package happens to be installed (D-009: CI has no
extras), (c) pinned SHA-256 per example config.

Revisit when: schema v0.2 (D-008) - the v0.2 exporter must keep the
nullable-optionals rule; or if a downstream consumer requires
omit-None artifacts (then revisit WITH a hash-migration plan).

AMENDED 2026-07-08 (D-044): the nullable-emission rule gains one scoped
exception — NEW additive suite-only optionals (`suite_manifest_ref`,
`suite_manifest_sha256`) are serialized by OMISSION when None, so every
pre-suite config stays byte-identical and no hash migration occurs. All
pre-existing optionals keep null emission. See D-044.

---

## D-030: `validate-bundle` stays structural by default; `--strict` adds raw-evidence checks

- Date: 2026-07-06
- Status: accepted (from the 2026-07-06 project status review, finding P2)
- Phase: 2 (matters most at Phase 5 dataset publication)

Context: the independent status review demonstrated that the default
validator blesses succeeded bundles whose analysis artifacts no longer
follow from their source evidence - an emptied rail manifest, a tampered
`energy_request_j`, and an unverified powermetrics `power_trace.csv`
derivation all validated clean. Structural checks alone cannot gate a
published dataset.

Options considered:

1. Broaden the default `validate-bundle` to include analysis checks.
   Con: the default is used in CI and on failed/unsupported/incomplete
   bundles, where a fresh reduction is not comparable (failure summaries
   are controller-written from partial evidence); a heavier default also
   makes the structural verb slower and noisier for its most common use.
2. A `--strict` opt-in mode: for `status=succeeded` bundles only, (a)
   the measured window must exist, (b) the summed curve must be
   reducer-consumable (>= 2 in-window samples for a nonzero window), (c)
   powermetrics `power_trace.csv` rows must equal the adapter's
   re-derivation from `raw/powermetrics.plist` plus
   `metadata.device.plist_anchor_offset_s` as parsed analytical values
   (exact timestamps, watts, source, rail, row count, and order; not
   byte-exact CSV spelling and not tolerance-based), and (d)
   `summary_metrics.json` must equal a fresh `reduce_bundle` result
   (exact-key diff reported). Failed/unsupported bundles pass strict
   untouched; non-powermetrics bundles skip the powermetrics sub-check.

Decision: option 2. Default semantics are unchanged; strict mode is the
gate for any "all bundles intended for analysis pass validation" claim -
Phase 5 dataset publication (Stage 5.2) and Phase 4 aggregation intake
should run `validate-bundle --strict`.

Considerations: the raw-to-trace comparison is semantic row equality:
the powermetrics adapter owns plist timestamp and rail semantics, and
CSV formatting is incidental. The re-reduction comparison has one
legacy-additive exception: fresh-only null keys and a missing legacy
`summary_provenance` block are tolerated (A-19), while all stored values
and stored extras remain exact claims. Any other drift - tampering, a
reducer version change, partial rewrites - surfaces as a named key diff.
Strict mode lives in `cli.py`, not the reader: it composes the reader with the
powermetrics adapter and reducer, and the reducer already consumes the
reader (D-025), so putting it in `bundle_read` would create an import
cycle.

Consequences: `validate_bundle(path, strict=False)` keeps its importable
signature; CLI gains `--strict`; the reviewer's two reproductions are
pinned as tests (manifest emptied, summary tampered), along with the
powermetrics raw-to-trace gate; Phase 5 Stage 5.2 should adopt
`--strict` for the published sample bundles.

Amendment (2026-07-10, P2-040 / C-027 adjudication H2): reducer `0.3.0`
defines the corrected nonpositive-window, metric-specific request-gate,
joint-edge-bound, and runtime-observed token-denominator semantics. An
inventory of `runs/` (including the retained main-checkout corpus), test
fixtures, and docs found no retained or published summary artifact recording
reducer `0.2.0`; all `0.2.0` matches were historical or specification prose.
Accordingly there is no `0.2.0` compatibility projection. Strict validation
dispatches solely on the reducer version recorded in the stored summary:
the frozen pre-D-033 legacy identity allowlist retains its existing
provenance-less additive-absence tolerance; recorded `0.3.0` summaries are
compared exactly; recorded `0.2.x` and unknown versions fail with
`unsupported reducer version; re-reduction required`. The presence of a
`summary_provenance` object alone never selects compatibility tolerance.
Succeeded bundles with a nonpositive measured window fail strict admission;
honest failed summaries remain structurally and strictly valid because they
make no successful-measurement claim.

Amendment (2026-07-10, P2-038 / C-028 adjudication): the six exact frozen
legacy identities continue to reconstruct powermetrics traces with
`metadata.device.plist_anchor_offset_s` and the original cumulative-elapsed
algorithm. Current-era powermetrics bundles instead use
`metadata.uncertainty_evidence.clock_anchor.first_sample_end_point_epoch_s`:
the point is the midpoint of the recorded controller-monotonic process-spawn
to first-parse bracket after applying the conservative run wall-minus-
monotonic envelope. Record zero is timestamped at that interval endpoint;
records `i>0` advance by elapsed values `1..i`. Strict mode re-derives the
midpoint and bounds from paired-clock observations and raw plists; plist
whole-second dates are consistency checks only and never tighten the bound.
Amendment (2026-07-10, P2-040 review fix, post-#49 union): reducer `0.3.1`
adds governed output fields `measurement_quality.runtime_cleanup_ok` and
`measurement_quality.remote_cleanup_failed`; `0.3.1` strict
comparison is exact. A stored `0.3.0` summary is compared against a fresh
reduction projected to recorded reducer version `0.3.0`, with absence-only
tolerance for exactly `ADDED_SINCE_0_3_0` (currently
`measurement_quality.runtime_cleanup_ok` and
`measurement_quality.remote_cleanup_failed`); any stored value remains an
exact claim. Legacy and unsupported-version arms are unchanged. From this point,
every governed output-shape addition MUST bump the reducer patch version and
extend the immediately prior frozen version's named absence-tolerance set.
A frozen reducer version is never reused for a changed governed output shape.

Amendment (2026-07-11, P2-041 / Component C5): reducer `0.4.0` renames the
top-level evidence-only surface from `claim_eligibility` to
`window_evidence_precheck`, removes the generic `request` alias from newly
reduced summaries, and retains the metric-specific `gross_request` and
`idle_subtracted_request` entries. Reducer `0.4.0` strict comparison is exact.
Current-era summaries recording reducer `0.3.0` or `0.3.1` require explicit
re-reduction; they are not projected across this semantic rename. The frozen
pre-D-033 legacy identity arm retains its provenance-less additive-absence
tolerance and original raw reconstruction, while recorded `0.2.x` and unknown
versions remain unsupported. Legacy compatibility never authorizes positive
claim readiness. Summary schema remains `0.1`; schema `0.2` remains reserved
for the previously adjudicated composite changes.

Amendment (2026-07-11, P2-044 idle dependence / lead-adjudicated design):
reducer `0.4.1` adds the governed `idle_mean_uncertainty` derivation and changes
`E_idle_mean_j2` to `measured_duration_s^2 *
governed_variance_of_mean_w2`. Current-era reducer `0.4.0` summaries are
rejected as re-reduction-required with no absence projection; the six frozen
legacy identity arms are unchanged. Strict validation fails on a raw/metadata
idle-baseline mismatch. The predeclaration freeze, before Window-A/P2-015
calibration effects are inspected, is:

- Exact method ID and formulas, including autocovariance denominator.
- Powermetrics 10 s bandwidth.
- Median-interval lag conversion.
- IID variance floor and ESS clamps.
- Minimum three-bandwidth trace rule.
- Cadence regularity threshold of 1.25.
- Rail definition: the same CPU+GPU+ANE arithmetic total used by the idle baseline.
- Arithmetic, not time-weighted, mean so the uncertainty matches the current point estimand.
- No trimming, detrending, stationarity “repair,” or adaptive bandwidth.
- Raw/metadata cross-check tolerance and failure behavior.
- Physical-backend applicability.
- `independent_run` covariance scope and the separation from deterministic drift.
- Reducer 0.4.1 and exact P2-037 required-method gate.
- The hand fixtures below.

The frozen method ID is `newey_west_bartlett_10s_iid_floor_v1`. The estimator
uses `L=floor(10/median(interval_s))`, the IID variance floor, ESS clamped to
`[1,n]`, `n >= 3*(L+1)`, and a type-7 linear p95/p05 cadence ratio no greater
than 1.25. Raw/metadata count is exact; mean, sample standard deviation, and
duration use `rel_tol=1e-9` and `abs_tol=1e-12`. Irregular cadence fails closed
without resampling. The policy is powermetrics-v1 only; other physical
backends emit `backend_policy_not_frozen`, and mock remains non-claim-bearing.
ESS is audit-only, never P2-037's paired-block sample size or degrees of
freedom. Any later method change requires a new method ID and reducer version;
historical outputs are never silently recomputed under changed policy.
The P2-044 hand fixtures are implemented in `tests/test_idle_dependence.py`;
P2-037's propagation fixture remains owned by its separate tree.

Amendment (2026-07-11, P2-045 / adjudicated hardening C5): reducer `0.4.2`
adds governed `inter_token_throughput_tokens_s = (N - 1) /
(t_last - t_first)`, where N is the runtime-observed output-token count and the
timestamps are the first and last observed decode-token events. It is null
when N is below two, fewer than two decode timestamps exist, or their span is
zero. This is the steady-state decode/inter-token estimand. The frozen legacy
`throughput_tokens_s` name and value remain unchanged: runtime-observed output
token count divided by the first-to-last decode-token span, which counts N
tokens over N−1 inter-token intervals and therefore exceeds the new metric by
N/(N−1) when the counts agree. Because no existing field changes meaning,
current-era reducer `0.4.1` gets absence-only tolerance for exactly the new
field; a stored value remains an exact claim. Reducer `0.4.2` comparison is
exact, while the `0.4.0`, `0.3.x`, unsupported-version, and six frozen legacy
dispatch arms remain otherwise unchanged. Any change to either formula or
nullability rule requires a new reducer version; frozen versions are never
reused.

Revisit when: bundle schema v0.2 lands (composite summaries need their
own strict semantics), or a reducer version bump makes historical
summaries legitimately differ from fresh reductions (then strict needs
a provenance-aware comparison, see D-028's revisit note).

Superseded in part (2026-07-15, WO-005; D-043): the P2-044 idle-
dependence amendment's frozen arithmetic-mean and trapezoidal-point-
estimand rules are replaced by reducer 0.5.0's duration-weighted idle
mean/variance/HAC/ESS with first-class interval support and a declared-
version dispatch matrix; legacy arms stay frozen under their original
rules (no re-dispatch). See the WO-005 frozen semantics spec and
reconciliation receipt under
`docs/reviews/2026-07-13-comprehensive-audit/receipts/`.

---

## D-031: Multi-model council review, PR convention, and drift controls

- Date: 2026-07-07
- Status: accepted
- Phase: all (process)

Context: the user directed a standing multi-model workflow: Codex
(gpt-5.5) implements and reviews as a near-peer, Claude leads and
verifies on hardware, Opus subagents run fast parallel sweeps, and the
models review each other bidirectionally with discussion of important
findings. The first two councils (see `docs/council_log.md` C-001/C-002)
caught a real blocker in green-tested code and six files of bookkeeping
drift respectively.

Options considered:

1. Single-model implement-and-self-review. Con: C-001 proved a fully
   green suite hid a blocker only adversarial review found.
2. Review without discussion (findings applied verbatim). Con: C-001's
   best fix came from the implementer arguing design back; C-002's
   run_id finding was refined in discussion.
3. Bidirectional council with bounded discussion (adopted): implementer
   ↔ reviewer roles swap per session; confirmed findings get one or two
   discussion rounds; the lead decides and records dissents in the
   council log.

Decision, in three parts:

- **Council process**: as above; sessions recorded in
  `docs/council_log.md` (positions, votes, resolutions — not
  transcripts). The lead (Claude) is the only member that runs real
  hardware; sub-agent "tests green" is never sufficient for
  hardware-adjacent slices.
- **PR convention**: multi-commit sessions land on a feature branch with
  a PR to `main` (one reviewable GitHub diff + CI before merge; the user
  merges). Single-commit bookkeeping may still go straight to main.
- **Drift controls**: D-023 is extended — prose status summaries must
  carry an as-of date and defer to checklist matrix rows (no duplicated
  live gate lists) — and every session ends with a delegated
  docs-consistency sweep before the final bookkeeping commit
  (RUN_STATE end-of-work step 7). Higher-level docs (README,
  PROJECT_STATUS, playbook) are in the sweep's scope explicitly.

Application note (2026-07-11, C-028 closeout): advisor and handoff prose must
separate four states that were conflated during the arc: merged software,
an open follow-up PR, a satisfied software gate, and completed live
execution. Test counts are cited with both the exact head and environment
convention: current main 1,220/`skipped=10`; PR #59 worktree
1,224/`skipped=12`; restricted managed-sandbox runs may carry
`skipped=13`. Historical exact tails remain valid only at their recorded
heads. This is an application of D-023/D-031, not a new status authority.

Revisit when: council overhead exceeds its catch rate (track via council
log outcomes), or the model roster changes.

Execution topology addendum (2026-07-07, user direction): when a session
has multiple independent workstreams, each stream runs in its own git
worktree on its own branch, owned by a dedicated orchestrator subagent
(Fable) that drives its own Codex thread — the bridge resolves the repo
root per-worktree, so parallel Codex sessions keep separate
`.codex-bridge/` state and `resume --last` pointers. The lead session
stays the integrator: it reviews each stream's diff, runs the council
loop per stream, and lands each as its own PR. Worktrees are skipped for
single-stream sessions (pure overhead). First planned use: the
2M / P2-008 / kv-size batch after the vertical-slice PR merges.

Flagship-model addendum (2026-07-07, user-directed): the user directed the
benchmark be run on "the top of the line model that can run on this
128 GB machine." Research council (web-verified) selected
`mlx-community/Qwen3.5-122B-A10B-4bit` (rev `e9c67b0`, 69.6 GB download,
~72-76 GB inference footprint, 122B MoE / 10B active, Feb 2026
generation; fits without wired-limit changes; expected ~40-45 tok/s on
M3 Max; runners-up gpt-oss-120b-MXFP4 and GLM-4.5-Air recorded in the
run report). This is a SECOND provisional model alongside the small
Qwen2.5-1.5B pick — it does not close D-016 (mid-model/CUDA/GGUF
criteria still open) but extends the provisional set at user direction;
mirrored per R-014.

(Amended 2026-07-08, D-043 back-annotation: the PR convention's
"the user merges" clause is superseded by Ed's 2026-07-08 standing
self-merge-with-review authority, recorded in C-010; the gate shape
lives in the resume-merge run report and `docs/orchestration.md`.)

Breach addendum (2026-07-09, C-027 whole-project review, MET-001):

Four commits landed directly on main in violation of this decision's PR
convention (only single-commit bookkeeping may bypass a PR):

- a05e54d — campaign scripts + tests (code+tests; 108 insertions).
- 8856c04 — controller/environment implementation + tests (code+tests;
  158 test lines).
- a835c73 — claims linter + 38 test lines inside a 26-file
  "bookkeeping + integration fixes" commit (code+tests mixed into
  bookkeeping).
- 36d5641 — 33-line scripts/build_site.py behavior change, NO tests,
  mixed with deployment output; postdates the then-recorded
  verification head c095c83, so main carried unverified code.

Content classes: three code+tests commits, one untested site-script
change (counterreview corrected the lead's earlier "all four contain
code+tests" overstatement — see review §6 item 2).

Remediation: retroactive independent review queued as RETRO-001
(result file: `docs/reviews/c027/retro_b6_review.md`, pending at the
time of this addendum). Recoverability evidence table:
`docs/reviews/c027/invocation_recoverability_audit.md`. Rule going
forward: integration fixes and site-script behavior changes require
their own PR; this addendum does not amend D-031's text, it records
its breach. History is not rewritten; the commits stand.

**2026-08-07 pointer note:** `docs/reviews/c027/retro_b6_review.md` was
not recovered in the repository and is unavailable for citation.

---

## D-032: `phase_energy_j` is gross-only in summary v0.1

- Date: 2026-07-07
- Status: accepted
- Phase: 2+

Context: `SummaryMetrics.phase_energy_j` attributes energy to workload
phase windows (`prefill`, `decode`, and later split phases). The reducer
also computes idle-subtracted request energy for the measured window, so
per-phase summaries need an explicit basis before 2M bundles are written.
C-007 decided that idle-subtracted phase attribution is Phase 4 analysis
policy, not a v0.1 bundle-summary contract.

Options considered:

1. Store gross phase energy only in `phase_energy_j`.
2. Store idle-subtracted phase energy in `phase_energy_j`.
3. Store both gross and idle-subtracted phase maps in summary v0.1.

Decision: option 1. `phase_energy_j` is gross joules only in summary
schema v0.1. Idle-subtracted phase attribution is derived later by
Phase 4 analysis policy, with any allocation assumptions stated there.

Considerations: gross phase windows are direct integrations over the
recorded power curve and do not require choosing how to allocate one idle
baseline across unequal or nested phase windows. This keeps the bundle
summary close to evidence while preserving Phase 4 freedom to apply a
documented attribution policy when answering analysis questions.

Consequences: consumers must not read `phase_energy_j` as an
idle-subtracted metric. Phase 4 may derive idle-subtracted phase values
from gross phase energy, idle baseline, and phase durations, but those
derived values are analysis outputs, not summary v0.1 fields.

Revisit when: a future summary schema version adds explicit per-phase
idle-subtracted fields with a named allocation policy.

---

## D-033: Prompt-content provenance is recorded per run bundle

- Date: 2026-07-07
- Status: accepted
- Phase: 2+

Context: The 2O placement council found that config hashes and token
counts do not prove realized prompt content. A tokenizer or generator
revision can produce a different token stream from the same nominal
profile, which would weaken the 2M corpus before later workload
enrichment begins. A-11 pinned the pre-2M workload provenance shape.

Options considered:

1. Rely on the normalized config hash and token counts. Con: misses
   tokenizer/model drift under the same config.
2. Record a text-only prompt hash. Con: insufficient for token-level
   identity because tokenization is part of the workload.
3. Record per-bundle workload provenance with a domain-separated hash of
   canonical JSON prompt token IDs, supplemental text hash, generator
   identity, tokenizer identity/revision/class/vocab size, model source
   and revision, and the output policy actually applied.

Decision: option 3. `metadata.json` gains additive
`workload_provenance` computed by the runtime adapter and written by the
controller. The prompt hash domain is
`joulewise.prompt_token_ids.v1`; campaign sameness is checked by
cross-bundle hash equality, not inferred from campaign membership.

Considerations: the runtime adapter is the point where text/profile
inputs become realized generation inputs, so it owns the provenance
block. The controller only carries and serializes it through
`RuntimeResult`. The block is per bundle (D-005), so repetitions can be
audited independently.

Consequences: new mock and MLX bundles record realized prompt-token
identity, tokenizer/model identity, generator identity, and
`fixed_budget_exact` output policy details. `run_campaign.py` needs no
special logic because it shells normal `joulewise run` executions.
Residual limitation: deleting both `summary_provenance` and
`metadata.workload_provenance` makes a new bundle indistinguishable from
a legacy bundle to strict validation.

Revisit when: a new runtime cannot expose token IDs or tokenizer
identity; that adapter must either add an equivalent audited source or
record a structured unavailable field before its bundles are admitted to
analysis.

---

## D-034: Slice 2O owns the workload program after 2M and 3.0.1

- Date: 2026-07-07
- Status: accepted
- Phase: 2+

Context: Commit `aa665e1` created Phase 2 Slice 2O for workload program
placement after the C-007 follow-on council. The slice owns queue tasks
P2-010 (`affine_mod_ladder_v1`) and P2-012 (`jw_mixed_v1`) as
post-baseline enrichment, not as pre-2M gates.

Options considered:

1. Put workload/prompt enrichment in Phase 4. Con: Phase 4 should
   consume workload dimensions and analysis outputs, not construct the
   workload corpus it analyzes.
2. Start workload enrichment before 2M. Con: delays and contaminates the
   homogeneous baseline milestone.
3. Create a Phase 2 post-baseline slice, 2O, gated after 2M strict-valid
   bundles, P2-013/P2-014, and the Stage 3.0.1 verdict.

Decision: option 3. Slice 2O owns the workload program P2-010 through
P2-012 after 2M and 3.0.1. Phase 4 consumes workload dimensions and
analysis-ready annotations but does not own workload construction.

Considerations: the 2O plan maps prompt/workload types to metrics and
research questions while keeping correctness quarantined as annotation,
not an intelligence-per-joule claim. This sequencing protects the 2M
baseline and keeps later workload expansion additive.

Consequences: P2-010 and P2-012 remain queued behind the 2M corpus and
the Stage 3.0.1 verdict. P2-014(e) is the pre-2M obligation: prompt
content provenance must exist before the campaign so later sameness
claims are auditable.

Revisit when: 2M is skipped or materially re-scoped; then 2O gates and
research-question mapping must be re-approved rather than silently
advanced.

(Amended 2026-07-08, D-043 back-annotation: D-042 reopened the
implementation lane for suite build before 2M; campaign-execution
ordering remains unchanged.)

---

## D-035: Replay claims require fresh-process (subprocess-per-stage) isolation

- Date: 2026-07-07
- Status: accepted
- Phase: 3+

Context: Stage 3.0.1 (verdict `replay_supported`, PR #9) established the
evidence standard that makes a KV-cache replay claim trustworthy: the
prefill/save, load/resume, and monolithic-reference stages each ran in a
fresh OS process, so no in-process cache or object reuse could fake
resume continuity. Promoted from the 3.0.1 stream ledger
(`docs/stream_logs/2026-07-07-kv-spike-301.md`, ratified by the lead
2026-07-07).

Decision: any future replay/persistence claim (3.0.2 llama.cpp, 3.0.3
vLLM, cross-machine variants, and Phase 3 measurement runs that assert
resume equivalence) must isolate the stages being compared in separate
OS processes, with only on-disk artifacts crossing the boundary.
Residual shared state (OS page cache, compiled-kernel caches) is
accepted as timing-only, not correctness-bearing.

Consequences: spike/measurement harnesses inherit the 3.0.1 script's
subprocess-per-stage shape; an in-process "resume" result is not
admissible evidence for a replay verdict.

Revisit when: a runtime cannot be driven per-stage from a fresh process;
that limitation must be recorded in the verdict itself.

---

## D-036: Spike verdict codes derive from measured data, never hardcoded

- Date: 2026-07-07
- Status: accepted
- Phase: 3+

Context: the 3.0.1 script computes `replay_supported` from the measured
token-identity comparison and the size-vs-prediction delta; a regression
flips the verdict to `partial(...)`/`replay_unsupported` with the failing
reason. Promoted from the 3.0.1 stream ledger (ratified by the lead
2026-07-07); aligns with D-015's evidence discipline.

Decision: every Stage 3.0.x feasibility verdict (and any later
feasibility gate) must be COMPUTED by the evidence-producing script from
its recorded measurements, with the failure branch emitting a distinct
verdict plus reason. A verdict string asserted by prose or hardcoded in
a report is not evidence.

Consequences: 3.0.2/3.0.3 spikes reuse this contract; reviewers check
the verdict derivation path as part of the evidence chain.

Revisit when: a verdict genuinely requires human judgment inputs; those
inputs then become recorded fields the code still derives from.

---

## D-037: Claims ladder (L0-L4) binds reader-facing claim language from 2M onward

- Date: 2026-07-08
- Status: accepted
- Phase: 2+

Context: an independent 5.5 critique of the whole project (counter-
reviewed and adjudicated in council C-011) found that the project's
claim discipline lived in scattered prose — the two-claim track, the
detection-floor gate, question-bank quarantines — with no single binding
taxonomy for how strongly a result may be worded. The 2M report is
imminent; wording discipline is cheapest before the first corpus lands.

Options considered:

1. Keep prose discipline + the planned Phase 4 claims index. Con: the
   strongest language can arrive before Phase 4 review catches it — it
   already did once (the flagship report's active-parameter wording,
   demoted by C-005/DOC-007 but resurfacing in derived prose).
2. Full claims index now with per-claim IDs. Con: only six real bundles
   exist; most rows would be placeholders (council: seed it post-2M).
3. Adopt the ladder now as a lightweight binding contract; per-claim IDs
   and mechanical enforcement arrive with the Phase 4 index.

Decision: option 3. `docs/contracts/claims_ladder.md` defines L0
(capability) through L4 (generalized finding) with allowed claim shape,
required evidence, and forbidden language per level, plus two riders:
cross-boundary comparisons are descriptive-only without a named
calibration bundle, and energy-per-output-token claims require
runtime-observed token counts + stop reason + output-policy label
(config-fallback denominators force L0 wording). Phase 4 Stage 4.3
acceptance requires every final-report claim to carry its ladder level.

Consequences: reader-facing docs written from 2M onward cite the level
their evidence supports; the flagship two-point comparison is pinned at
hypothesis-generating (L1 with the confound caveat); reviewers check
wording against the ladder as part of the standard lens rounds.

Revisit when: the Phase 4 claims index lands (mechanical enforcement
may subsume the prose rule), or a claim class appears that the five
levels cannot express.

---

## D-038: Analysis-plans contract binds L2/L3 claims to pre-registered plans

- Date: 2026-07-08
- Status: accepted
- Phase: 2+

Context: the suite-science hardening council (C-014) found that planned
comparisons carried no pre-registered analysis: estimators, floor gates,
sample sizing, and claim ceilings lived in scattered prose, and the
Token-Shape Sufficiency Null (C5-W.1) was unfalsifiable as designed. The
claims ladder (D-037) disciplines wording but not the analysis that
produces the number being worded.

Options considered:

1. Keep discipline in the question bank per question. Con: the bank
   records what a question is, not how its comparison will be analyzed;
   the C-W.1 confound survived three council passes there.
2. Full statistical analysis plan documents per campaign. Con:
   pre-registration theater; prose ritual the loop would stop reading.
3. A compact per-comparison plan table as a contract, with a binding
   rule: no reader-facing L2/L3 claim without a filled plan row.

Decision: option 3. `docs/contracts/analysis_plans.md` defines the plan
schema (metric + window class, unit of analysis + dependence structure,
estimator, inclusion/waiver rules, order/blocking, floor gate =
max(floor_abs, floor_cmp), MDE/n sizing with predeclared top-up,
denominator provenance, holdouts for L3, claim ceiling, disqualifiers,
post-execution manifest links) plus standing reporting rules: phase
metrics are gross-only until phase-idle modeling exists; short-prefill
windows below 3 samples report `not resolvable`; capped cells are
excluded from prompt-slope/rank claims unless realized lengths match;
rank claims require rank gap > comparison MDE; itemized suites
(ladder/mixed items inside one bundle) are never treated as independent
replicates — uncertainty is computed at bundle or block level.

Consequences: six plans seeded (Q4 grid fit, 2M asymmetry, Q5 rank
stability, C5-W.1 equivalence, ladder level-energy guards, content
sentinel); floor fields fill from the P2-015 calibration artifact;
reviewers check L2/L3 wording against plan rows as part of standard
lens rounds.

Revisit when: the Phase 4 claims index lands (plans may merge into it),
or a comparison class appears the schema cannot express.

---

## D-039: Workload program v2 — substrate first, identification before scale

- Date: 2026-07-08
- Status: accepted
- Phase: 2+

Context: C-014 (lead audit + scout + three design lenses + peer
counterreview) found the planned suite could measure things no consumer
cites and claim things no design could support: Q4 unreachable at L3
from the 4-cell 2M grid; P2-015 yielding only an absolute floor while
L2/L3 claims are gated by the comparative MDE; jw_mixed_v1 cross-
category comparisons shape-confounded; the full 64-level scored ladder
having no claims-index consumer; Q4-Q6 having no Phase 4 figure slots.

Decision, five parts (specs live in the amended
`docs/research_question_bank.md`, `docs/phase_2/phase_2_plan.md` 2O, and
`docs/contracts/analysis_plans.md`):

1. P2-010 splits: P2-010a reusable suite substrate (item/level markers,
   `BundleReader.item_windows()`, category/source_manifest/output_policy
   fields, per-item stop/token/response hashes); P2-010b smoke-scale
   ladder whose acceptance is envelope validation. The full scored
   64-level campaign is deferred until C5-1.9 has a named consumer.
2. jw_mixed_v1 runs phased: common-shape identification stratum (all six
   categories at one matched shape) → natural-EOS pilot (>=4
   items/category on reasoning/JSON/chat/multilingual) → full panels
   only if earlier phases show above-floor structure. Supersedes the
   fixed-budget-full-first sequencing from C-005; quarantines intact.
3. New suite element `q4_l3_shape_grid_v1` (AP-1): 4x3 prompt x decode
   grid with predeclared interpolation + extrapolation holdouts,
   categorical-additive fit first — the only planned path to an L3
   claim on current hardware.
4. Quiet-window execution is TWO windows: A = expanded P2-015 floors +
   2M + drift sentinels, then reduce and compute CV/floor/MDE; B = Q4
   grid with n sized from Window A, plus the content-sensitivity
   sentinel. Rationale: MDE-sized n cannot honestly precede the floor
   measurement.
5. P2-015 expands to per-metric/window-class floors (gross request,
   idle-subtracted request, phase, item/level) plus comparative MDE
   tables; `docs/phase_2/detection_floor.md` becomes a per-consumer
   table.

D-034's gate is unchanged: 2O work stays post-2M; the only pre-Window-A
item is P2-021 (drift-sentinel support in the 2M generator), which is 2M
campaign tooling, not workload enrichment.

(Amended 2026-07-08, D-043 back-annotation: this pre-Window-A allowlist
was superseded twice: first by D-041 item 5's amendment, then by D-042.)

Consequences: queue rows P2-015/P2-006/P2-010/P2-012 amended; P2-019,
P2-020, P2-021 added; Phase 4 figure registry gains F9-F12 so Q4-Q6
data has named consumers before it is collected.

Revisit when: Window A results contradict the sizing assumptions, or a
consumer for the full scored ladder appears.

---

## D-040: Suite architecture v2 — one generic suite mechanism, bundle-level replication

- Date: 2026-07-08
- Status: accepted
- Phase: 2+

Context: Ed directed the benchmark toward multi-prompt runs of varying
difficulty and type. Council C-015 (two design lenses + peer
counterreview) designed the architecture; the statistical shape had to
compose with D-038's pseudo-replication rule.

Decision (spec in the question bank's C-015 section):

1. A suite bundle executes k distinct items once each (r_within = 1);
   replication comes from B whole-suite bundles (B >= 5, top-up 10).
   Within-bundle repeats are reserved for sentinel items — they estimate
   order/cache/thermal effects, never independent n. Uncertainty lives
   at bundle/block level (D-038).
2. No per-item micro-cooldowns: back-to-back execution is the named
   session ecology. Order is rotated/Latin-squared across bundles;
   item/block/position/prefix-group/order-seed metadata recorded.
   Suites split into balanced blocks when wall time exceeds ~10-15 min
   OR drift sentinels/floor identifiability degrade. k=24 first default.
3. ONE mechanism: affine ladder, jw_mixed, q4 grid, content sentinel,
   and benchmark imports are all PROFILES over one suite manifest +
   marker/window path. After P2-010a, no workload expansion gets bespoke
   plumbing — new benchmarks are manifests plus generators.
4. P2-010a is capped to the MINIMAL substrate (markers, item_windows(),
   source/category/output-policy fields, per-item token/stop/response
   hashes, order/cache metadata, manifest validation) PLUS the per-item
   validity/status model (succeeded | malformed | capped | runtime_failed
   | below_floor | excluded_from_claim) with aggregation rules for when
   partial suites remain claim-usable. Scorers, import-specific fields,
   and rich difficulty machinery are deferred until profiles need them.
5. Difficulty is first-class quarantined item metadata {axis, value,
   scale, label, source}; shape is not difficulty; the C-004 quarantine
   composes unchanged.

Consequences: P2-010 queue row redefined; suite throughput rises 3-15x
in item coverage while n stays honest at the bundle level; every later
workload (including imports) inherits provenance, windows, and the
status model for free.

Revisit when: P2-010a implementation finds the minimal substrate
insufficient, or a profile genuinely cannot ride the generic mechanism.

---

## D-041: Benchmark interop — frozen-subset imports + marker-shim energy layer

**2026-08-07 supersession note:** The clause later superseded by D-060 is
retained unchanged as historical context. Current rule ownership: D-060.

- Date: 2026-07-08
- Status: accepted
- Phase: 2+ (all implementation post-2M per D-034; see stop-line)

Context: Ed directed easy integration of external benchmarks into the
suite and extension of external benchmarks with JouleWise's energy
measurement. C-015 designed both directions.

Decision (specs in the bank C-015 section + adapter_contracts.md):

1. IMPORT: a thin `benchmark_import` manifest freezes identity,
   licensing, contamination, rendering, and quarantine metadata for a
   hash-manifested external-benchmark subset; execution rides P2-010a.
   First target: HumanEval as a plumbing smoke (MIT; 256/512-token
   completions clear the ~9 Hz item-window floor more plausibly than
   short-answer benchmarks); FLORES second (tokenizer/multilingual
   science); MMLU/tinyBenchmarks rejected as first targets.
2. EXPORT: a marker-emitting shim contract — the external harness owns
   prompts, generation semantics, and accuracy artifacts; JouleWise owns
   power capture, bundle assembly, marker validation, and energy
   reduction. P2-022 is a verdict-shaped feasibility spike
   (external_markers_supported | partial | unsupported; D-035/D-036
   inherited) pinned to energy-layer feasibility ONLY.
3. Joined accuracy(theirs)+energy(ours) data may state observed energy
   for marked item/subset windows alongside the external metric
   ARTIFACT; it may never produce JouleWise accuracy claims,
   pass@k-per-joule, leaderboard standing, or intelligence-per-joule.
4. Kill/defer list (C-015; the bank's C-015 section holds the verbatim
   11-entry list, which is authoritative): leaderboard integration, live
   dataset fetching, latest-split support, accuracy scoring beyond
   quarantined annotation, judges/retries/pass@k/benchmark-score
   normalization, full per-harness adapters AND generation-callable
   wrappers as the FIRST export path (the shim comes first; they are
   sequencing kills, not categorical), per-item uncertainty treated as
   independent replication, public energy leaderboards before cross-lab
   replication, any intelligence-per-joule ratio.
5. Sequencing gate AMENDED (D-039 named only P2-021 as the pre-Window-A
   item; this adds the Window-A capture hardening stream, and nothing
   else): only P2-021 and Window-A capture hardening precede P2-015/2M. Substrate, shim spike, imports, q4-grid and
   jw_mixed execution are post-2M unless D-034 is reopened. Stop-line:
   under schedule pressure, interop and suite expansion drop before
   P2-015/2M/Mac characterization — the guaranteed capstone is the
   instrument plus Mac characterization, never the expansion.
   (Amended 2026-07-08 pre-merge: the allowlist names pre-Window-A
   work items; prep steps internal to P2-015, including the lead-run
   tasks-sampler overhead smoke that also validates the 2s env-capture
   settle absorbs the probe burst, are part of P2-015 itself, not
   additional items.)

Consequences: queue gains P2-022/P2-023/P2-024; adapter_contracts.md
gains the shim contract; the bank gains C5-I.1..I.5 and the capability
map; export direction prioritized over import for adoption-per-build-day.

Revisit when: the P2-022 spike returns unsupported/partial, or D-034 is
reopened.

(Amended 2026-07-08, D-043 back-annotation: the revisit clause FIRED by
D-042's reopening. ADJUDICATION RECORDED: D-042 opened only the
suite-BUILD lane; the interop lane (P2-022 shim spike, P2-023 imports)
REMAINS post-2M + post-P2-010a as originally gated.)

---

## D-042: D-034 implementation lane reopened — suite build proceeds pre-2M (owner directive)

- Date: 2026-07-08
- Status: accepted
- Phase: 2+

Context: Ed directed (this session) that the test-prompt suite for
observation/trace generation be actually built with dedicated research
and effort, not only specified. D-034 (reaffirmed by the C-015 gate
amendment) held ALL 2O substrate/suite implementation post-2M; its
revisit clause names exactly this: reopening by decision rather than
silent advancement.

Decision: the IMPLEMENTATION lane of the workload program is open now:
P2-010a substrate, P2-010b smoke ladder, P2-012 phase-1 content
generators, and P2-020 sentinel content generation may proceed as
[AGENT] work before 2M. UNCHANGED: campaign EXECUTION ordering (Window A
P2-015 floors then P2-006 2M first; Window B after), the quiet-machine
clause of the C-015 stop-line (no suite work consumes quiet-machine
time), the minimal-substrate cap (D-040.4), and all quarantines. The
drop-order under schedule pressure also stands: suite build drops before
P2-015/2M/Mac characterization.

Research input: `docs/phase_2/suite_implementation_research.md`
(4 cross-checked reports; amendments are UNRESOLVED review findings the
implementing session adjudicates first).

Consequences: P2-010/P2-012/P2-020 status cells flip to build-unblocked;
the 2O gate paragraph carries a dated amendment note pointing here.

Revisit when: suite build threatens the Window A/2M schedule (drop it),
or 2M lands (gate question dissolves).

---

## D-043: Supersession-closure discipline

- Date: 2026-07-08
- Status: accepted
- Phase: all

Context: a meta-reassessment (5-analyst workflow over the full
council/decision/skill logs) found ~70% of accumulated doc defects were
one mode: a rule superseded while its losing surfaces stayed live (merge
authority x3 surfaces, the pre-2M allowlist x3 versions, topology x3
docs, the decision index ending at D-037, unamended fired revisit
clauses).

Options considered:

1. Continue relying on broad end-of-session consistency sweeps. Con: the
   drift pattern survived repeated sweeps because losing surfaces were
   outside the immediate diff.
2. Require only the winning decision to mention what it supersedes. Con:
   readers landing on the older rule still see a live instruction.
3. Add write-time back-annotation plus a sweep-time supersession check
   keyed by the session's supersessions.

Decision: option 3.

1. WRITE-TIME: any change that supersedes a prior rule MUST, same
   session, append a dated amendment/supersession line to EVERY surface
   stating the losing version, including the superseded decision/council
   entry and its index row.
2. SWEEP-TIME: the end-of-session consistency sweep includes a
   supersession check driven by the session's SUPERSESSIONS (grep the
   superseded wording across both logs, contracts, process docs), not
   only its diff.

Consequences: fired-clause back-annotations above land under this rule;
the sweep prompt gains check five.

Revisit when: if two consecutive sweeps find zero supersession drift, the
sweep-time check may relax to spot-checks.

---

## D-044: Suite config identity — omission-serialized ref + effective-manifest hash

- Date: 2026-07-08
- Status: accepted (suite-build adjudication; A1/A3 dispositions)
- Phase: 2

Context: P2-010a adds `workload_profile.suite_manifest_ref` as a fourth
mutually exclusive prompt source. Under D-029's nullable emission it
would emit `null` into EVERY normalized config, breaking all five pinned
config hashes and therefore run identity (D-001/D-022/D-005) for
logically unchanged configs. Separately, a path-only ref leaves manifest
BYTES outside run identity: two runs with different manifest content at
the same path would share config hash and D-022 suffix.

Options considered:

1. Accept the hash break and repin (uniform dataclass serialization).
   Con: global identity churn for the 6 real corpus bundles' config
   lineage, against D-029's protect-hashes rationale.
2. Serialize the new suite fields by omission when None; keep every
   pre-existing optional null-emitted. Con: one scoped carve-out in
   `to_dict()`; the emitted-keys round-trip test must learn about
   declared omitted optionals.
3. For manifest identity: ref-only config with sameness via
   `metadata.suite.manifest_sha256` (dataset_ref precedent). Con: config
   hash misses manifest bytes — D-022 collision across different
   manifests at the same ref.
4. Config also carries a required manifest hash. Sub-choice: raw file
   bytes vs the canonical EFFECTIVE manifest (defaults materialized) —
   raw bytes would let a future change to code-level defaults alter
   effective semantics without changing identity (counterreview catch).

Decision: options 2 + 4 (effective-hash form). `suite_manifest_ref` and
`suite_manifest_sha256` are BOTH omitted from `to_dict()` when None
(scoped D-029 exception, back-annotated there) and both required
together. `suite_manifest_sha256` is the SHA-256 of the canonical
effective manifest: parsed, schema-validated, pinned defaults
materialized, sorted-key 2-space JSON + newline (D-001 convention).
`_stage_validate` recomputes it from the ref'd file and fails closed on
mismatch (structured failure, in-bundle). The bundle writes the
canonical effective manifest as `suite_manifest.json`; `metadata.suite`
records the same effective hash plus the source file's raw byte hash as
audit evidence. A suite example config gets its own pinned hash in
`tests/test_schemas.py`.

Considerations: manifest bytes now enter run identity through the config
hash; campaign sameness remains hash equality, never membership (D-033
rule). Changing a pinned marker/output default (D-045) changes effective
manifests, hence hashes, hence identity — deliberate.

Revisit when: schema v0.2 export (D-008) restates the serialization
rules; or a third omission-serialized field is proposed (then decide a
general rule instead of accreting exceptions).

Amended (2026-07-15, WO-009/R4; D-043): per-field manifest policy-knob
semantics are now explicit at the persistence layer (v2 bundle
manifests): `order_policy` and `items[].output_policy` enforced;
`cache_policy` descriptive-provenance with a mandatory declared-not-
verified marker; `within_bundle_repeats` and `warmup_policy`
reserved-compat; `default_output_policy` descriptive; `status_policy`
REMOVED (non-default values rejected). See ed-rulings.json R4.

---

## D-045: Suite substrate execution semantics

**2026-08-07 supersession note:** The clause later superseded by D-056 is
retained unchanged as historical context. Current rule ownership: D-056.

- Date: 2026-07-08
- Status: accepted (suite-build adjudication; A4/A5/A6/A8/C6 + attack-round guards)
- Phase: 2

Context: P2-010a implements the C-015 generic suite substrate; the
execution-architecture report (suite_implementation_research.md §A) is
sound-with-amendments and its adjudicated form needs its contract
choices pinned.

Decision (bundle of pins; alternatives recorded in the research doc's
adjudication section):

1. Item loop lives runtime-side: new `SuiteRuntimeAdapter` protocol with
   `run_suite(config, manifest, context)`; `run_workload` untouched;
   [AMENDED 2026-07-08, oversight round: the signature gained
   keyword-only `order_seed` supplied by the controller so the seed is
   never runtime-derived — `run_suite(config, manifest, context=None, *,
   order_seed)`; see item 6 and adapter_contracts.md];
   controller dispatches when a suite manifest is present and fails fast
   pre-window (`UNSUPPORTED_WORKLOAD` when the runtime lacks the
   protocol; structured FAILED on unreadable/invalid manifest).
2. Manifest is a bundle-root artifact (`suite_manifest.json`, canonical
   effective form per D-044), never embedded in config.
3. Marker events ride the five-key event shape with `phase: "suite"`;
   vocabulary (suite/block/level/item start+end event types and required
   metadata keys) is pinned in `joulewise/suite.py` constants. The
   manifest's `markers:`/`outputs:` blocks are OPTIONAL: absent →
   pinned defaults materialized into the effective manifest; present →
   values must equal the pinned constants; divergent → validation
   error. Changing a default is a suite schema revision, never a silent
   code edit (identity via D-044).
4. Status ownership: runtime assigns `succeeded|malformed|capped|
   runtime_failed` in `item_end`; reducer alone may downgrade to
   `below_floor` (floor seam ships with `floor_source =
   "none_pending_P2-015"`); `excluded_from_claim` is analysis-only and
   is a validation error if seen in events or summaries. FIXED-BUDGET
   UNDERRUN (emitted < planned under `fixed_budget_exact`) is
   `malformed` with `status_reason="fixed_budget_underrun"`; bundle
   validation rejects `succeeded` where `fixed_budget_exact` and
   `emitted_tokens != planned_output_tokens`.
5. Per-item prompt sources are mutually exclusive per item:
   `prompt_text` (materialized at generation time, text path, BOS inside
   budget) | `prompt_token_ids` (ids-native additive path, required by
   D-046 sentinels) | synthetic shape (`shape.planned_prompt_tokens`).
   Per-item prompt identity uses the existing domain-separated token-ID
   hash (`joulewise.prompt_token_ids.v1`, D-033); any `prompt_sha256`
   field name means the token-ID hash.
6. `order_seed` derives deterministically:
   `sha256(suite_seed + "\0" + order_policy + "\0" + str(rep_index))`
   truncation per implementation; recorded in `suite_start` metadata and
   `metadata.suite`; never runtime-chosen.
7. Per-item/block/level energies are GROSS-only (C-014 phase rule); no
   per-item idle subtraction or token-normalized claim metrics.
8. Per-item outputs: single `outputs/suite_items.jsonl`; each line
   carries `item_id`, `item_index`, `status` (+ `status_reason` when
   applicable), `prompt.token_ids_sha256`, `response_text`,
   `response_sha256`, `stop_reason`, `prompt_tokens`, `emitted_tokens`,
   token timestamps. Response TEXT is hereby RATIFIED as a P2-010a scope
   addition to the C-015 minimal sketch (needed for re-reducible
   scoring, D-036/C-004); the bank sketch gets a dated amendment.
9. Reducer summary gains additive `suite_metrics` (not in
   `_SUMMARY_WRITER_KEYS_V0_1`, `summary_provenance` precedent);
   `SUMMARY_REDUCER_VERSION` bumps to `0.2.0`.

Revisit when: composite/split bundles (schema v0.2) touch suite
manifests; or the first real suite campaign contradicts a pin.

Amended (2026-07-15, WO-009/R4; D-043): execution-policy knob semantics
at the persistence layer follow the R4 per-field ruling recorded under
D-044's amendment (enforced vs descriptive-provenance vs reserved-compat
vs removed).

---

## D-046: AP-6 sentinel delivery — ids-native, BOS-less, literal equal shape

- Date: 2026-07-08
- Status: accepted (suite-build adjudication; B5 disposition, counterreview-amended)
- Phase: 2

Context: AP-6 requires five equal-shape content conditions. Text-path
prompts realize BOS + 511 content tokens (`add_special_tokens=True`)
while the incumbent repeated-seed stream and the random-token sentinel
are ids-native with no BOS — "equal shape" was not literally true, and
BOS-normalizing the control would change the very incumbent stream
(`_synthetic_prompt_tokens`) whose generalization AP-6 tests.

Options considered:

1. Prepend BOS to ids-native conditions (511 content tokens). Con: the
   control stops being byte-for-byte the incumbent stream.
2. Record BOS presence as covariate, conditions heterogeneous. Con:
   "five equal-shape conditions" would be false as written.
3. Deliver ALL five conditions ids-native without BOS: text-derived
   conditions (natural prose, code-like, multilingual) are generated
   with `add_special_tokens=False` accounting and delivered as token
   ids.

Decision: option 3. Literal equal shape across all five; the control is
exactly the incumbent recipe; `bos_present=false` and
`prompt_source="token_ids"` recorded per condition. BINDING CAVEAT
(counterreview): AP-6 results describe the ids-native no-BOS regime and
do NOT automatically generalize to the AP-4 text path (BOS present,
different delivery); the AP-6 row carries this limit, and a small
text-path bridge (AP-6b) is the named option if Window-B analysis needs
the generalization. jw_mixed category items (AP-4) are unaffected.

Revisit when: AP-6b is proposed, or a model/tokenizer without a stable
ids-native path enters the sentinel set.

---

## D-047: Affine ladder pins — level set, smoke sizing, gate denominators

- Date: 2026-07-08
- Status: accepted (suite-build adjudication; C0/C2/C3/C5/C8/C9 dispositions)
- Phase: 2

Context: the affine-ladder report (suite_implementation_research.md §C)
needed lead ratification of its level-set reading and statistical
corrections from its cross-check.

Decision:

1. Level set is the powers of two `{1, 2, 4, 8, 16, 32, 64}` — the
   bank's "levels 1..64" line is edited to say so (docs fix). Item
   identity keys on the difficulty VALUE (`n_iter`), so smoke items are
   a strict subset of full-ladder items.
2. Smoke ladder (P2-010b): levels `{1, 8, 64}` × 8 items/level + 2
   repeated-seed sentinel executions (suite start/end); k = 24 distinct
   items (C-015 first default holds; the earlier "k=26 / 2-over" claim
   was an accounting error — sentinel executions are within-bundle
   repeats, not distinct items). B = 5 bundles, top-up 10.
   AMENDED 2026-07-08 (AFF-1, review-driven, same session): the sentinel
   is a DEDICATED derived item (`n_iter=1, item_index=8`, id
   `affine_v1_sentinel`) so no ordinary level item carries the sentinel
   tag — duplicating L01/i00 would have corrupted the
   8-distinct-items-per-level denominator. Accounting is therefore
   k = 25 distinct items / 26 executions; every level still has exactly
   8 untagged distinct items. Ledger:
   docs/stream_logs/2026-07-08-affine-ladder.md AFF-1.
3. Gate statistics: under deterministic (greedy) decoding, repeated
   bundles replicate ENERGY only; all token/stop-reason/correctness
   denominators are the 8 DISTINCT items per level. E1's 5% threshold at
   n=8 means ZERO tolerated non-EOS items per level — stated, not
   implied. The report's pooled "40-80 items/level" power framing is
   rejected as pseudo-replication.
4. E5 (early-EOS bias) is advisory and recorded
   `expected_not_evaluable` at smoke sizing (needs ≥10 distinct parsed
   items per class); smoke stays 8 items/level.
5. Sampler pinning (B9, applies suite-wide): the MLX adapter records
   sampler provenance (greedy/temp-0 default made explicit) so "greedy"
   in manifests rests on recorded fact, not an unpinned library default.
6. AP-5 row edit rides this decision: the scored campaign predeclares
   malformed-as-incorrect in the accuracy denominator (reported
   alongside); full-ladder k=112 + sentinels still needs its own
   ratification at campaign time.
7. Threshold defensibility (C7): the ~4%-of-window arithmetic is
   re-anchored on the first smoke bundle's measured level-window energy;
   smoke bundles double as level-window floor-calibration evidence for
   P2-015.

Revisit when: the first smoke bundle's measured item time falls outside
0.11–0.20 s/item (resize per the report's table); or the scored
campaign is scheduled (k-policy ratification).

Amendment (2026-07-09, CP-5 resume, PR #27): the sampler-pinning clause
is superseded — adapters now FAIL CLOSED with `sampler_pin_unverified`
when the sampler cannot be pinned/verified, instead of proceeding
unpinned with a provenance note. Accepted at the CP-6 methodology
adjudication; contract wording updated in
`docs/contracts/adapter_contracts.md` the same session.


---

## D-048: Split program is model-first — pre-registered compositional prediction before split runs

- Date: 2026-07-08
- Status: accepted (C-020 whole-project merit debate; three-pole consensus)
- Phase: 3 (binds Phase 3 design + AP row seeding; framing binds Phase 4)

Context: the C-020 merit debate's decisive arithmetic (KV bytes/token ×
link speed vs measured idle/decode watts) shows the Q1 crossover is
possible but NOT likely uniformly across the planned pairings — a bare
"no crossover found" sweep result would read as predictable. All three
debate poles (session-lead Fable, fresh-Fable, Codex stack) converged
independently on the fix.

Options considered:

1. Keep the crossover sweep as the flagship, report whatever verdict
   lands. Con: the null branch is a shrug; a positive is a point
   observation without a transferable theory.
2. Invert entirely — make the Q4 compositional model the thesis and the
   split sweep mere validation (fresh-Fable's strong form). Con:
   under-weights that the both-end per-stage energy decomposition
   DATASET is itself the first-of-kind artifact regardless of model fit.
3. Synthesis: model-first FRAMING, dataset-first CONTRIBUTION.

Decision: option 3. The program's thesis sentence is: "JouleWise builds
auditable per-stage split-inference energy bundles, then tests whether a
pre-registered compositional model predicts them." Binding mechanics:
(a) BEFORE any split hardware runs, the compositional model (AP-1 Q4
coefficients + measured link-transfer energy + idle floors) produces
pre-registered predicted split-energy curves per pairing/link, recorded
in a seeded analysis-plan row (incl. the named same-boundary headline
pairing, which is L2-eligible calibration-free); (b) Phase 3 acceptance
is reframed as prediction validation: every branch is a result —
confirmed model (predictive tool), quantified unmodeled overhead term
(systems finding), or crossover located where predicted (doubly
credible); (c) a no-crossover verdict is publishable ONLY as successful
prediction or quantified overhead discovery, never presented as a
surprise negative. Design should include at least one pairing/link cell
where the model PREDICTS a crossover, if any exists in the feasible set.

Consequences: `docs/phase_3/phase_3_plan.md` acceptance framing gets a
dated amendment pointing here; the AP row obligation rides the split-prep
queue row; Phase 4 claim wording inherits the thesis sentence.

Revisit when: the 2M-fitted Q4 model fails its own monolithic holdouts
(then the compositional prediction has no validated coefficients and the
sweep reverts to exploratory with that stated).

---

## D-049: Split transfer-energy boundary accounting on discrete-GPU ends

- Date: 2026-07-08
- Status: accepted (C-020; Codex-stack catch, repo-verified)
- Phase: 3

Context: on nvidia-smi-measured ends, board power EXCLUDES the host
CPU/NIC/DRAM work of moving KV bytes over TCP — so "transfer energy"
measured at a discrete-GPU end is near-zero by construction: a silent
undercount in unmeasured silicon, asymmetric across the pairing matrix
(Mac and Jetson boundaries include their NIC/host paths; dGPU boundaries
do not).

Options considered:

1. Ignore — report board-only numbers. Con: cross-pairing transfer
   comparisons silently broken; exactly the boundary sin (D-018) the
   project exists to avoid.
2. Wall-meter (or equivalent host-side measurement of) the GPU host on
   transfer legs so the transfer window has a host-inclusive boundary.
3. Explicitly scope dGPU transfer cells as board-only LOWER BOUNDS in
   the stage accounting, named per cell in the AP row and claim wording.

Decision: option 2 where the meter is available for the leg, option 3
otherwise — never option 1. The per-stage accounting schema must carry a
per-cell boundary label for the transfer stage; the seeded split AP row
(D-048) names which cells are host-inclusive vs board-only lower bounds;
cross-pairing transfer-energy comparisons are permitted only between
like-boundary cells or via the D-018 calibration bridge.

Consequences: split-prep queue row carries this; `docs/contracts/`
boundary docs get the transfer-stage label when the split schema lands
(Phase 3 implementation, not now — R-015 additive rule applies).

Revisit when: the wall/USB-C calibration (Q6) bounds the host-side gap
tightly enough to model it instead of measuring per leg.

---

## D-050: Active stop cards and process-trace manifests

**2026-08-07 supersession note:** The clause later superseded by D-064 is
retained unchanged as historical context. Current rule ownership: D-064.

- Date: 2026-07-09
- Status: accepted (user-directed meta-process cleanup after CP-5 pause)
- Phase: cross-project process

Context: CP-5 intentionally paused a live pre-campaign review session
after token spend ran out. The project preserved the necessary resume
facts, but they were split across `RUN_STATE.md`, `TASK_QUEUE.md`, a
stream log, off-repo checkpoint artifacts, and older run-report restart
pointers. That made the handoff recoverable but too easy to bypass.

Options considered:

1. Leave the existing pointers alone. Con: normal "what next" prose can
   compete with an active checkpoint and lead a future agent into lower
   queue work.
2. Move all checkpoint details into the queue. Con: the queue is too
   compact to own dirty worktree/PR/artifact inventory safely.
3. Add an active stop-card layer to `RUN_STATE.md`, with the queue and
   run-report intake explicitly subordinated to it, plus lightweight
   manifests for future delegated runs.

Decision: option 3. An ACTIVE `ACTIVE_STOP_CARD` in `RUN_STATE.md` is
the single restart authority wrapper and overrides normal next-work
sections, queue ranking, playbook missions, and latest-run-report
defaults until cleared. Stop cards must preserve the resume authority,
reason for stop, paused work inventory, status terms, artifact pointers,
first resume action, and clearance criteria. Substantial delegated,
skill, council, or worktree-heavy runs must leave a process trace and,
when large enough, an `invocation_manifest.jsonl`-style pointer map tying
prompts, sessions, outputs, dispositions, and commits/PRs together.

Consequences: CP-5 remains paused and untouched, but future intake now
routes to its exact stream-log authority first. Half-finished work is
not executable unless it has an authority pointer, bounded scope,
acceptance evidence, and a lane. Councils retain their role for
methodology/measurement/claim/hardware decisions but must report yield,
dispositions, and downstream closures. `scripts/codex-bridge` now
implements a local invocation manifest with prompt snapshots, response
snapshots, logs, status files, prompt/output/log hashes, session-id
capture when present, and pending disposition fields.

Revisit when: one full stopped-and-resumed session completes under the
new stop-card rule, or the invocation manifest proves too heavy for
ordinary delegated runs.

Stop-card override addendum (2026-07-09, C-027, MET-001 / REV-5):
during the ACTIVE CP-5 stop card (RUN_STATE at 2c8b267: "Do not start
other queue work"), advisor-site commits bf9ffc5, a1ac0a7, fda79c1,
e6cf431 were produced before CP-5 resumed (later landed via PR #28).
User direction for that work existed and is recorded at
docs/run_reports/2026-07-09-advisor-status-site.md:13, but no override
was recorded on the stop card at the time. Disposition: recorded
retroactively as a USER-DIRECTED OVERRIDE (scope: advisor status site
only; CP-5 state untouched), plus a recording failure — the override
should have been appended to the stop card when work began. Rule
restated: undocumented supersession of an active stop card is
indistinguishable from bypass; overrides are recorded on the card
before the first commit of overriding work. A second override
precedent is recorded here for the same reason: Ed's 2026-07-09 live
directive to begin implementation before spec adjudication (C-027 spec
wave) superseded the recorded DRAFT-pending-adjudication gate —
recorded so undocumented supersession does not recur.

---

## D-051: Advisor status site uses source-derived static pages plus fail-soft live GitHub overlays

- Date: 2026-07-09
- Status: accepted
- Phase: 2 / project communication

Context: the Lakebed status site had a strong static source-derived
observatory and a live freshness banner, but the deployed snapshot could
still be stale exactly where an advisor cares most (`RUN_STATE.md` and
`TASK_QUEUE.md`). The hand-authored Story page also carried moving counts
that had drifted from the generated status pages.

Options considered:

1. Keep the site purely static and rely on the freshness banner. Pro:
   simplest deployment. Con: advisors still read stale body text first.
2. Make Lakebed the new source of truth for project status. Pro: live UI.
   Con: creates a second status database and undermines the repo audit
   trail.
3. Keep repo markdown as the source of truth, generate static pages from
   it, and add fail-soft Lakebed overlays that fetch current GitHub
   markdown for a narrow set of advisor-facing fields.

Decision: option 3. The source-derived static site remains the fallback
and audit surface. Lakebed serves `/api/freshness` for commit drift and
`/api/live-status` for a small parsed live view over
`PROJECT_STATUS.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, and the risk
register. The status page may update top-line fields from this API while
source chips and generated pages continue to show exactly what the baked
snapshot was built from.

Consequences:

- The Story page should avoid volatile counts unless they are generated
  or source-linked.
- Advisor-facing depth belongs in generated status panels: snapshot
  state, advisor asks, campaign readiness, evidence board, and claim
  ceiling.
- Lakebed endpoint aliases should remain server endpoints, because
  Lakebed routes direct HTTP requests to matching `GET` endpoints before
  client routes.
- The live APIs must fail soft and must never hide static provenance.

Revisit when: GitHub raw-content fetch becomes unreliable enough to need
an authenticated token or when a formal advisor portal with user-specific
state is required.

Amended (2026-07-15, integration budget fix; recorded as a PARTIAL
pre-implementation of deferred AUD-WO-039): the packed capsule omits the
generated task-queue payload — its routes alias to the Roadmap page —
to hold the 1-MiB Lakebed artifact under the conservative budget after
the audit fix wave's doc growth. The tracked TASK_QUEUE.md (whose live
queue is now the WO-021 generated region) remains the authoritative
long-form source; the full retained-route/page inventory and any
compatibility endpoint decision remain with AUD-WO-039 at its landing.

## D-052: Capstone scope contract — frozen umbrella headline and contribution ladder

**2026-08-07 supersession note:** The clause later superseded by D-060 is
retained unchanged as historical context. Current rule ownership: D-060.

- Date: 2026-07-09
- Status: accepted
- Phase: cross-phase / claims

Context: review C-023 (finding B4) required one frozen, defensible headline
claim with fallbacks, and the user's 2026-07-09 direction required the
contribution framing to honor the filled measurement matrix as the end-goal
novelty. Stream ledger: `docs/stream_logs/2026-07-09-scope.md` (SC-1).

Decision: `docs/contracts/capstone_scope.md` (PR #30) is the binding scope
contract. Headline: "auditable, boundary-labeled local LLM energy
characterization on named hardware/runtime/model/workload stacks" — an
umbrella scope statement carrying NO global claim level; per-result
ceilings follow D-037. Split inference is a stretch extension gated on a
named method; calibration is required specifically for cross-boundary
quantitative winners. Contribution is argued as a three-rung ladder
(instrument/methodology → filled-matrix scoped empirical coverage →
contingent findings), with auditability as the warrant that makes the
coverage claim believable, not a substitute for it. R-012 remains the
single home of the minimum-viable-capstone floor; the contract adds
reporting stop-lines only.

Consequences: reader-facing wording must trace to this contract; the
related-work check (vs JouleSort, MLPerf Power, ML.ENERGY, Zeus) is a
named precondition for the Rung-2 coverage-novelty claim.

## D-053: Contrast-level statistical inference and the frozen analysis registry

- Date: 2026-07-09
- Status: accepted (ratifies the "pending ratification (C-023 S3)" contract markers)
- Phase: cross-phase / statistical protocol

Context: review C-023 (findings B2 + M1) found the D-014 interval-separation
rule statistically wrong for paired designs and no benchmark-level
multiplicity policy. Stream ledger: `docs/stream_logs/2026-07-09-stats.md`.

Decision (PR #29): claims derive from the confidence interval of the
paired/block difference or named model contrast, never marginal-interval
separation; three-way wording rule (below-floor `not resolvable`;
above-floor non-directional `unresolved`/no directional claim; equivalence
only via a predeclared gate); permutation checks follow the actual
randomization scheme within exchangeable strata (minimum 6 blocks);
leave-one-out influence checks at n<=10 with defined triggers. Analysis
plans gain required fields family_id / claim_role / selection_scope /
multiplicity_rule; the registry is FROZEN before campaign execution with an
enumerated complete contrast_id set (exact Holm/BH denominators); post-hoc
claims are exploratory. AP-1..AP-6 carry seeded family values; AP-5 BH
sweeps are restricted to correctness/metadata (item-window energy stays
exploratory). This amends D-014's protocol wording; D-014's repetition
counts and outlier never-silently-drop rules stand.

Consequences: the claims-index linter (future) refuses L2/L3 without these
fields; campaign execution requires a frozen registry snapshot.

## D-054: False-effect guard floor and unknown-term claim-ceiling policy

- Date: 2026-07-09
- Status: accepted (promotes stream-ledger P15-7)
- Phase: 2 / measurement

Context: C-023 finding B1 (no metrological error budget); counterreview R2
killed the drafted percentile-UCB floor (unidentifiable at n=10: the sample
maximum exceeds the true 95th percentile only 40.1% of the time; a
nonparametric 95/95 bound needs n=59). Stream ledger:
`docs/stream_logs/2026-07-09-p2015.md` (P15-7; P15-2/P15-6 superseded).

Decision (PR #31): `docs/phase_2/detection_floor.md` is the P2-015 design.
Floors are FALSE-EFFECT GUARD FLOORS — max(largest observed absolute
residual/contrast, Student-t prediction bound for one new observation) —
with bootstrap as sensitivity only and a pre-registered small-sample guard
factor at 5<=n<10. Error-budget terms are enumerated per
backend x metric x window class; UNKNOWN terms cap claim level (they do not
block L0/L1 operation). Variance and deterministic bounds propagate
separately (drift is a bound unless a distributional model is justified).
Wall/USB-C PD calibration runbooks are pre-registered as bridge-model fits
(slope/intercept over workload-induced deltas), not absolute-delta
acceptance. Window-B revalidation: stale floors cap affected claims until
topped up.

Consequences: P2-015 campaign sizing is derivable from the economics table
(170-340 bundles); claim tooling must consume floor rows + error-budget
fields per the analysis registry (D-053).

Amendment (2026-07-09, C-027 sweep adjudication): 170 bundles is the
minimum Window-A request/phase subset; 180-340 is the total campaign
including the required Window-B revalidation cell (economics table,
`docs/phase_2/detection_floor.md`). Prose citing either number must name
which scope it means.

## D-055: Research-question registry is the canonical live index

- Date: 2026-07-09
- Status: accepted (promotes stream-ledger RQ-1)
- Phase: cross-phase / research bookkeeping

Context: C-023 finding B3 — the same question existed as promoted Q, banked
item, capability-map row, and C5 tier row with no alias normalization.
Stream ledger: `docs/stream_logs/2026-07-09-rqreg.md`.

Decision (PR #32): `docs/research_question_registry.md` is the canonical
LIVE index of question status, aliases, type, claim ceiling, forbidden
upgrade, AP/campaign owners, gate class, and pre-hardware preparability
(75 rows). `docs/research_question_bank.md` remains the historical and
deliberative record — single-writer split. The registry indexes ratified
council decisions; it never re-decides them. C-023 coverage gaps enter as
`candidate (C-023)` rows.

Consequences: promotion/status changes edit the registry (with the bank
still holding deliberation); front-facing docs point at the registry for
current state; the future claims-index linter consumes registry columns.

## D-056: Suite order policies and order_row provenance

- Date: 2026-07-09
- Status: accepted (promotes stream-ledger P30-1..P30-3; additive amendment to D-045.6)
- Phase: 2 / suite execution

Context: C-015 promised round-robin/Latin-square rotation; the sequencing
spec executed manifest_order (C-023 M2, pre-campaign blocker). Design round
ratified in `docs/stream_logs/2026-07-09-p2030.md` before implementation.

Decision (PR #34): `execution_policy.order_policy` names an operational
policy from the closed set {manifest_order, block_round_robin_v1,
block_latin_square_v1 (Williams row-balanced)}; realized order is the pure
function realized_order(manifest, policy, order_row); order_row is
controller-derived (suite rep index), recorded in metadata.suite alongside
order_seed = sha256(suite_seed, policy, order_row) — the D-045.6 hash
surface gains order_row as a companion, additively. Rotation unit is the
contiguous block run; all-sentinel blocks are position-anchored;
item_index stays manifest identity, position is the realized ordinal.
Strict validation recomputes the expected permutation AND the order_seed
fail-closed when order_row is present; legacy bundles without order_row
stay valid. Pinned generated manifests keep manifest_order byte-identical.
Reports/tooling surface manifest_order wording when rotation is absent.
Within-block item rotation is a named deferred revisit.

Consequences: suite campaigns can execute the C-015 rotation promises with
auditable order provenance; campaign-level config ordering remains
order_manifest.json (a distinct mechanism — see the campaign-packs README
operator note).

Amended (2026-07-15, WO-009/R4; D-043): `order_policy` is confirmed
ENFORCED at the persistence layer under the R4 per-field ruling (see
D-044's amendment); the remaining execution-policy knobs carry their
ruled enforce/descriptive/reserved/removed semantics in v2 bundle
manifests.

## D-057: Uncertainty terms — drift is a bound; claim-gate reason codes are stable vocabulary

**2026-08-07 supersession note:** The clause later superseded by D-077 is
retained unchanged as historical context. Current rule ownership: D-077.

- Date: 2026-07-09
- Status: accepted (promotes stream-ledger P29-2/P29-3)
- Phase: 2 / measurement

Context: P2-029 (PR #33) implemented detection_floor.md §3 (D-054).

Decision: (a) idle drift enters uncertainty accounting ONLY as a
deterministic bound (E_drift_bound_j in energy_bound_terms_j, from the
single documented evidence key idle_drift_bound_w) — never as a variance
term unless a distributional model is explicitly justified; no drift
magnitude is ever invented from cooldown flags (cap-hits add
claim-ineligibility reasons instead). (b) The claim_eligibility reason
codes (insufficient_in_window_samples, cadence_ratio_unrecorded/below,
clock_bound_unrecorded/exceeds_quarter_window, drift_term_unknown,
interpolation_bound_unrecorded/exceeds_floor, ...) are STABLE machine
vocabulary: consumers may match on them; changes require a decision-log
amendment. Single bundles are not_estimable; unknown gate inputs fail
machine-readably, never silently pass.

Consequences: claim tooling and the analysis registry consume these codes;
P2-015 floor artifacts plug into the same gate fields.

Amendment (2026-07-10, P2-040 / C-027 adjudication): the stable reason
vocabulary adds `nonpositive_window_duration` (the evaluated window has
duration `<= 0` and cannot bear a claim) and `idle_baseline_unrecorded` (an
idle-subtracted metric was requested without a valid recorded idle baseline).
Request gating is metric-specific: `gross_request` governs
`gross_energy_j` without idle-baseline or drift requirements, while
`idle_subtracted_request` governs `idle_subtracted_energy_j` and requires
both. The `request` gate remains a deprecated alias of
`idle_subtracted_request` through summary schema v0.1; removal waits for
schema v0.2.

Amendment (2026-07-10, P2-041 / C-027 adjudication): the closed v1
analysis/campaign consumer vocabulary is:
`analysis_manifest_invalid`, `analysis_manifest_not_frozen`,
`order_manifest_hash_mismatch`, `config_hash_mismatch`, `bundle_missing`,
`bundle_strict_invalid`, `bundle_status_not_succeeded`,
`metric_missing_or_nonfinite`, `paired_block_incomplete`,
`insufficient_complete_blocks`, `fixed_n_plan_incomplete`,
`window_evidence_precheck_missing`, `campaign_cooldown_evidence_missing`,
`idle_window_suspect`, `idle_window_suspect_unknown`,
`floor_artifact_invalid`, `floor_row_missing`, `floor_row_ambiguous`,
`floor_row_stale`, `floor_transport_inapplicable`, `floor_abs_missing`,
`floor_cmp_missing`, `effect_not_above_floor`,
`interpolation_bound_exceeds_floor`,
`interpolation_bound_exceeds_half_effect`,
`deterministic_bound_obscures_direction`, `required_error_term_unknown`,
`required_covariance_unknown`, `runtime_token_denominator_required`,
`stop_reason_required`, `output_policy_required`,
`tokenizer_identity_mismatch`, `multiplicity_family_incomplete`,
`multiplicity_not_rejected`, `equivalence_margin_not_above_floor`,
`equivalence_not_supported`, `randomization_check_insufficient_blocks`,
`randomization_sensitivity_disagrees`, `loo_verdict_influential`,
`loo_magnitude_influential`, `outcome_dependent_top_up`, and
`legacy_l1_mechanics_only`. Additions or spelling changes require a
versioned amendment. P2-041 copies reducer reasons verbatim, uses the
campaign-specific subset above, and never treats absent/null cooldown state
as recovery. The Component C5 `window_evidence_precheck` migration and
generic-alias removal supersede only D-057's historical field name and the
preceding amendment's alias-retention wording; its metric-specific reason
semantics remain binding.

Amendment (2026-07-11, P2-037 / C-028 analysis-trio adjudication): the
analysis engine adds the following exact closed v1 reason vocabulary. Consumers
may match these strings; additions or semantic changes require another
versioned amendment:

```text
analysis_manifest_invalid
analysis_manifest_not_frozen
order_manifest_hash_mismatch
config_hash_mismatch
bundle_missing
bundle_strict_invalid
bundle_status_not_succeeded
metric_missing_or_nonfinite
paired_block_incomplete
insufficient_complete_blocks
fixed_n_plan_incomplete
window_evidence_precheck_missing
campaign_cooldown_evidence_missing
idle_window_suspect
idle_window_suspect_unknown
floor_artifact_invalid
floor_row_missing
floor_row_ambiguous
floor_row_stale
floor_transport_inapplicable
floor_abs_missing
floor_cmp_missing
effect_not_above_floor
interpolation_bound_exceeds_floor
interpolation_bound_exceeds_half_effect
deterministic_bound_obscures_direction
required_error_term_unknown
required_covariance_unknown
runtime_token_denominator_required
stop_reason_required
output_policy_required
tokenizer_identity_mismatch
multiplicity_family_incomplete
multiplicity_not_rejected
equivalence_margin_not_above_floor
equivalence_not_supported
randomization_check_insufficient_blocks
randomization_sensitivity_disagrees
loo_verdict_influential
loo_magnitude_influential
outcome_dependent_top_up
legacy_l1_mechanics_only
```

Reducer-owned precheck reasons remain copied verbatim. Unknown reasons and
unknown covariance/term provenance fail closed rather than acquiring a local
alias or zero value.

## D-058: Token-normalization and stack-identity contract adopted

- Date: 2026-07-09
- Status: accepted (promotes stream-ledger P31-1)
- Phase: cross-phase / claims

Decision (PR #35): `docs/contracts/token_normalization.md` is binding for
token-denominated metrics and stack identity on all claims-ladder-governed
surfaces: request energy primary; J/token tokenizer-scoped with
runtime-observed denominators; cross-tokenizer/model-family comparisons
require companion denominators (J/char, J/byte, semantic-pair) or must
avoid efficiency-ranking language (enforceable forbidden-phrase list); the
11-field stack-identity table (hardware unit, OS, runtime, kernel/library,
model artifact hash, quantization, tokenizer identity incl.
prompt_source/bos_present, sampler/output policy, batching/concurrency —
always applicable, boundary label, telemetry backend) with the table-wide
rule: every field is a concrete value or an explicit unavailable/unknown;
silent omission is non-compliant.

Consequences: the L4-review stack-confound and J/token-comparability
attacks now have a binding answer; figures/captions compose with
capstone_scope single-unit language.

## D-059: Claims-lint mechanical enforcement in CI

- Date: 2026-07-09
- Status: accepted
- Phase: cross-phase / claims tooling

Decision (PR #37 + integration fix): `scripts/claims_lint.py` is the
mechanical enforcement layer for the claims discipline — AP-row
required-field/registry-field completeness (17-field contract, hard errors
on malformed rows, strict multiplicity forms), registry integrity (closed
sets incl. pre_hardware_preparable, duplicate IDs, AP-owner existence),
campaign-pack draft AP linting (marker-gated; index/README files exempt),
and a warning-only forbidden-language scan. A unittest lints the live repo
in CI: breaking an AP row or the registry fails the build. The linter
satisfies the C-023 cut-line condition for structural claim checks; the
Phase 4 claims-index mode extends this tool rather than a new one.

Consequences: the D-053 freeze discipline and D-055 registry are now
machine-checked.

Amendment (2026-07-11, P2-037): `claims_lint` gains an explicit
`claim-index` mode over the canonical Phase-4 JSONL. It verifies the linked
`joulewise.claim_verdicts.v1` bytes, canonical ID, AP/contrast/role/outcome,
manifest/floor/bundle provenance, D-062 demotion, sensitivity caveats, and
claim-level ceiling. The single pre-P2-037 manual-review L1 row is
grandfathered only under its exact canonical row identity/hash and emits a
warning; it does not become engine-supported evidence.

## D-060: Depth-before-breadth stop line (RATIFIED)

- Date: 2026-07-09; RATIFIED by Ed 2026-07-10 as written (C-028 session,
  live decision; the independent hardening proposal's convergent freeze
  recommendation was noted at ratification)
- Status: **accepted** (C-027 council recommendation; allocates
  Ed-facing work, so Ed ratifies or amends)
- Phase: cross-phase / project management

Proposal (C-027; amends D-041/D-052 sequencing and extends R-012/R-018):
no NEW breadth — new campaign packs, registry expansion, site features,
meta-process growth — until four gates pass:

1. Grading rubric + calendar captured by a hard date; if the program
   stays silent past it, adopt and RECORD a provisional grading contract
   with conservative internal deadlines (external silence triggers scope
   fallback, never indefinite paralysis).
2. Off-machine backup with a restore proof, before any NEW irreplaceable
   campaign evidence is retained (P0-003). Does not block report
   drafting, analysis tooling, or correctness fixes.
3. Window A complete in the C-027 sense: smoke, frozen sampling rule and
   guard factor (P2-039), production uncertainty evidence (P2-038),
   versioned floor artifact, floors, baselines — with the executable
   contrast/claim path (P2-037) before any L2 interpretation.
4. One end-to-end vertical slice: report source skeleton + reproducible
   bundle→analysis→figure→claims-row→report-page path (RPT-001).

Application note (2026-07-11, C-028 closeout): gate 2 is satisfied by the
verified iCloud backup and byte-identical strict-valid restore. The software
prerequisites inside gate 3 are also satisfied: P2-039, P2-038, and the
P2-042→P2-041→P2-037 analysis trio are merged, with reducer dispatch current
through 0.4.2. Gate 3 itself is not complete because Window-A smoke, floors,
and baselines have not executed. That execution is a quiet-machine + Ed
action; no landed-software statement raises its claim level or promotes the
PROVISIONAL NVIDIA pins.

Work that CLOSES these gates, correctness defects, report writing, and
already-obligated hardware preparation are always permitted.

Alternatives considered: status quo (rejected — C-027/NEGSPACE evidence:
six real bundles vs ~6M tokens of same-day breadth work); a blanket
freeze including correctness work (rejected — would block the gates'
own prerequisites).

Amendment (2026-07-15, WO-022/R2, Ed-ratified 2026-07-13): the spend
guardrails extending this stop line landed verbatim in
`docs/orchestration.md` §"Spend guardrails (WO-022...)" — capstone
benchmark bands (session/WO/arc tiers, soft record-and-continue vs hard
pause-and-ask-Ed), the deliverable-progress tripwire bound to these
D-060 gates, the named-failure bar for process innovation, and the
keep-defender guarantee. Landing snapshot receipt (estimated; close-out
refresh owed):
`docs/reviews/2026-07-13-comprehensive-audit/receipts/WO-022-audit-close-spend.json`.

## D-061: Review-layer evaluation rule v2 (replaces the two-zero-sessions drop rule)

- Date: 2026-07-09
- Status: accepted (C-027; process-layer, within council authority)
- Phase: cross-phase / process instrumentation

Context: the "drop a layer after two zero-catch sessions" rule was
falsified by its own record — integration review returned zero unique
catches twice (C-017, CP-5) and then caught five real cross-stream seams
(C-024). Mechanical application would have deleted the layer immediately
before its highest-value session.

Decision: layer evaluation uses (a) applicability decided by
PRE-DECLARED mechanical predicates (e.g. integration review counts only
when 2+ independently developed streams merge touching a shared
contract/consumer/generated artifact), never post-hoc judgment; (b) an
outcome taxonomy separating accepted-unique-defect / duplicate /
clean-verification / false-positive-suppression — suppression is
valuable but is not a catch; (c) fixed severity weights declared before
the session; (d) three applicable exposures TRIGGER an expected-loss
review decision, never automatic deletion; (e) safety, final-head, and
integration layers are never auto-dropped on zero-defect streaks —
they are judged by expected-loss reduction.

Alternatives considered: keep the two-zero rule (falsified); "three
applicable sessions, severity-weighted" as free-text judgment (rejected
in council — reintroduces the discretion that made the old rule
unfalsifiable).

## D-062: Confirmatory sampling policy — fixed n, explicit demotion, no silent top-ups

- Date: 2026-07-09
- Status: accepted (C-027; scientific protocol, ratifies the RIGOR/STATS
  adjudication; amends the top-up language in
  `docs/contracts/analysis_plans.md` — AP-EDIT applies the text)
- Phase: cross-phase / statistical protocol

Context: the analysis plans repeatedly started at n=5 and added
repetitions when an observed CI was near-floor or unsatisfactory, then
reported ordinary 95% CIs. Outcome-dependent sample growth invalidates
nominal coverage (C-027 RIGOR finding, adjudicated with the peer's
counterreview).

Decision: (a) confirmatory contrasts use n FROZEN before observing that
pack's effects, sized from Window-A variance/MDE evidence — nearer 10
than 5 for near-floor comparisons; (b) predeclare replacement rules for
technically invalid runs (they are not top-ups); (c) any
outcome-dependent top-up permanently DEMOTES that contrast to
exploratory: the original fixed-n analysis is reported regardless of
direction, pooled estimates are never presented as retaining nominal
confirmatory coverage, and no later convenience re-promotes the claim;
(d) a pre-registered two-look alpha-spending design (frozen max n, look
boundaries, spending function) is PERMITTED for a specifically justified
expensive campaign, never the default.

Alternatives considered: full group-sequential machinery as default
(rejected — avoidable defense surface for a capstone); status quo
(rejected — statistically invalid).

## D-063: Process architecture v2 — machine-readable state kernel first

- Date: 2026-07-09
- Status: accepted (C-027; process-layer)
- Phase: cross-phase / process architecture

Context: five core process files grew 3,106 → 4,893 lines with ~9.5k net
process/history lines since orchestration landed; the same-day RUN_STATE
dual next-action drift (C-027 B3) is the demonstrated failure mode of
hand-maintained state mirrors.

Decision (staged; big-bang migration rejected by both council sides):
Stage 1 (DOC-008) = a thin machine-readable state kernel (task id, lane,
status, dependencies, authority pointer, acceptance pointer, stop-card
pointer) from which the RUN_STATE restart block and the live queue view
are GENERATED; PROJECT_STATUS compaction with a status-history archive;
retire `docs/planning_reflection_protocol.md` as standalone intake
(zero credited catches across four recent sessions — its useful fields
fold into queue rows); the two-writer rule and credential-boundary push
procedure move into `docs/orchestration.md`. Stage 2 = per-session
findings/invocations ledgers making "unique catch" a query (extends
D-050). Policy-doc generation comes LAST — supersession requires
semantic judgment (council position, adopted from the peer's argument
over the lead's original ordering).

Alternatives considered: defer the kernel and generate
current_policy.md first (the lead's draft position — REVERSED in
council: it leaves the demonstrated drift mode active); full big-bang
migration (rejected: risks the drift it cures).


Amended (2026-07-15, WO-021/R1 choice A; D-043): the Stage-1 kernel's
NOT_AUTHORITATIVE_DERIVED_VIEW posture is superseded — schema v3 makes
the kernel AUTHORITATIVE_WORK_SELECTION_STATE (work selection ONLY;
phase completion stays with exit checklists, policy with this log,
scientific truth with evidence artifacts), adds active_global_gates
with conjunctive select semantics beneath stop-card precedence, and
demotes competing hand-authored work-selection surfaces to one
generated region per file.

---

## D-064: Delegated-invocation compliance surface — tracked JSONL event stream, report envelope, enforced write scope

- Date: 2026-07-11 (core surface adjudicated 2026-07-10, C-028 H4;
  v3/envelope/scope clauses ratified after landing in the C-028
  infrastructure wave)
- Status: accepted (C-028; process-layer)
- Phase: cross-project process instrumentation

Context: D-050 requires substantial delegated runs to leave a
process trace and an invocation-manifest pointer map. The C-027
audit showed a gitignored bridge manifest cannot serve as
repository-auditable evidence, and that run-report summaries had
collapsed roughly one hundred invocations into zero auditable
per-invocation rows. The D-050 revisit condition fired at
CP-5/C-022 and is adjudicated here through MET-001 option 2 and
C-028 H4. During the C-028 arc the surface was then exercised in
production: a wrapper crash mid-run (lead in-place edit of the
installed runner) and two out-of-scope diffs (p2043-impl,
p2044-fixround) tested the recovery and enforcement semantics now
ratified below.

Decision:

1. **Compliance surface.** One tracked, append-only JSONL manifest
   per substantial session under `docs/process_traces/`, with rows
   for every actual invocation. Failed, capacity-ended, resumed,
   and retried invocations get their own rows; resumes may share a
   model session ID but never an invocation row. Run reports carry
   only counts plus a link to the tracked manifest. The codex-run
   observer index and raw logs remain recovery substrate, never
   the compliance surface; the gitignored bridge manifest remains
   local convenience only.

2. **Manifest v3 is an append-only EVENT STREAM, not a mutable
   ledger.** Three event kinds: `run_started` (wrapper-authored at
   dispatch: prompt hash/bytes, contract, genre, write scope,
   head/branch at start), `run_finished` (wrapper-authored at
   exit: invocation state, report parse validity, semantic
   status/completion, finding/verification counts, scope-violation
   counts, head at end), and `run_consumed` (LEAD-authored at the
   moment the lead dispositions the output: consumed / rejected /
   deferred, with pointer). Consumption events are lead-owned
   exclusively — a wrapper or delegated session never writes them.
   Emitted rows are never mutated, rewritten, or deleted;
   corrections are new rows. When the wrapper dies without writing
   `run_finished`, the LEAD authors a recovery `run_finished` row
   that says so explicitly (`error_stage`, a note naming the
   failure, and any manually-performed classification) — silent
   reconstruction that imitates a normal wrapper row is forbidden.
   Two live defects were found on day one — a resume no-op after a
   NEEDS_SCOPE early-return, and an in-place-edit crash hazard now
   covered by the atomic-mv install rule — and both are recorded
   in the adapter's operational lessons.

3. **claude-codex-report/v1 is the canonical session report.**
   Every delegated session returns the envelope: machine-parsed
   header (run status, completion, finding counts by severity,
   verification results, scope-deviation flags) over a prose body.
   `run_finished` records the parse verdict and the extracted
   counts. A session without a valid envelope is not consumable as
   review or implementation evidence — it is raw substrate pending
   a lead ruling or a re-run. NEEDS_RULING early-returns are
   compliant envelopes, not failures.

4. **WRITE_SCOPE is enforced, not advisory.** Each invocation
   declares its write scope up front; the runner diffs the
   worktree against that scope after the run. On violation the
   runner exits 77, the out-of-scope work is PRESERVED in an
   evidence bundle (status `failed_preserved`) and is never
   landed; the lead inspects the bundle and decides. A session
   that discovers it needs wider scope returns NEEDS_SCOPE as a
   structured request; scope expansion is PROSPECTIVE ONLY — a new
   invocation with the widened scope — never a retroactive
   blessing of an already-out-of-scope diff. WRITE_SCOPE strictly
   overrides any in-repo end-of-work instruction (AGENTS.md
   precedence section, per the CI-002 root cause).

This amends and supersedes only D-050's invocation-manifest
compliance-surface clause. D-050's stop-card authority,
process-trace obligation, and raw-log pointer policy are
unchanged. v2 single-row-per-invocation snapshots remain valid
evidence for pre-v3 invocations; new sessions emit v3.

Alternatives considered:

1. Run-report invocation summary as the surface. Rejected:
   summarization destroyed per-invocation auditability — the exact
   failure MET-001 exists to repair.
2. Gitignored live bridge manifest as the authority. Rejected:
   structurally local-only; unignoring a shared live file creates
   multi-worktree contention and dirty-tree noise.
3. Mutable per-invocation rows updated in place (start → finish →
   disposition on one row). Rejected: in-place mutation destroys
   the append-only audit property, makes wrapper crashes
   indistinguishable from clean rows, and invites silent
   retro-editing; the event stream keeps every state transition
   and its author.
4. Free-form final messages as session reports. Rejected:
   unparseable; counts and scope flags cannot be mechanically
   extracted into `run_finished`.
5. Advisory-only write scope (prompt-level restriction without a
   runner backstop). Rejected: the CI-002 deviation demonstrated
   that in-repo end-of-work instructions override polite prompt
   scoping; enforcement must be structural, with the work
   preserved rather than discarded so enforcement never destroys
   evidence.

Consequences: session closeout must land the tracked manifest(s)
before bookkeeping is declared complete; every `run_started` must
be closed by a wrapper or lead-authored `run_finished` and a
lead-authored disposition, with missing rows recorded as missing,
never inferred from aggregates. D-063 Stage 2 may generate queries
and projections over these files but may not replace the row-level
source. Council-log layer-yield claims (D-061) should cite manifest
rows.

Revisit when: three substantial sessions have landed v3 manifests;
or the one-file-per-session scheme shows material contention or
ambiguity; or `run_consumed` coverage proves too burdensome to
sustain (in which case narrow the event, do not revert to mutable
rows).

---

## Adjudication note (was: drafting notes for the lead)

Lead-adjudicated 2026-07-11: accepted as drafted. The date
(2026-07-11 with the 07-10 H4 parenthetical), the "Status: accepted
(C-028; process-layer)" voice, the clause-2 recovery-row
generalization from the live p2037-fixround recovery row
(`error_stage: wrapper_crash_lead_inplace_edit`), the clause-4
exit-77/`failed_preserved` semantics (verified against the live
p2043-impl / p2044-fixround status files), and the v2-valid-for-
pre-v3 transition sentence all stand. One addition per lead
dictation: the day-one-defects sentence appended to clause 2.

## D-065: bridge-protocol/v1.1 — co-work lane, session wrappers, tolerant envelope

- Date: 2026-07-13 (Ed-directed; spec ratified from a lead+Sol xhigh
  design consult, thread `019f5d1d-b681-7db1-8714-812fdd2f198b`)
- Status: accepted (C-032; process-layer). Contract text is the ONE
  home for every wire rule; this entry records adoption and the
  process-binding consequences only.
- Phase: cross-project process instrumentation

Context (state at recording: the v1.1 amendment is ratified and carried by PR #65, gate-complete and awaiting Ed's merge; it becomes the current contract on main when #65 merges): one production day of bridge-protocol/v1 showed the manual MCP
write ceremony (~6 bookkeeping commands) pushing small writes off the
bridge, a 13-field header taxing pure discussion turns, envelope
strictness (minification, closed key set) failing substantively correct
returns, a pinned reverse-consult effort, and effort-tier prose
restated in four places. Ed directed a consult-first revision for
"maximum co-work" with persistence in the top-level docs.

Decision:

1. `docs/contracts/bridge_protocol.md` is amended (via PR #65) to
   `bridge-protocol/v1.1`: reduced discussion-lane header (+ context
   capsule and continuation deltas), `scripts/bridge session-open`/
   `session-close` as the PREFERRED write ceremony (receipt-anchored,
   fail-closed, `session.lock`-serialized with primitives, write-only
   in v1.1), tolerant single-final-line envelope with normative field
   types, per-call reverse-consult `effort` (`high`|`xhigh`) with an
   effort echo line and single-envelope deviation handling, and
   per-objective peer channels with bounded proposal diffs
   (aggregate ≈3 files/200 lines; durable provenance record when the
   lead applies one).
2. Process bindings: design consults default to the discussion lane on
   a per-objective peer channel (never counted as independent review);
   delegated writes open and close through the wrappers, with the
   primitives reserved for recovery and adjudicated overrides;
   effort-tier policy prose lives only in
   `.claude/skills/codex/SKILL.md` §Effort selection (consumers carry
   at most the ratified one-line pointer); enforcement-boundary
   guardrails are exempt from dedup and stay explicit at their
   surfaces.
3. Deferred, revisit on demonstrated need: snapshot_read wrapper
   sessions (v1.1 wrappers are write-only; the unreachable v1.1-draft
   DISCUSSION-success path was removed rather than enabled), and any
   expansion-receipt artifact (the lease event chain is the
   authoritative expanded-scope record).

Addendum (same session, 2026-07-13): Ed named the merge; PR #65 MERGED
as `d285989`; the v1.1 contract is now the current contract on main
(merged-main suite lead-run: 1387 OK).

Operational note (2026-07-15, Ed-approved lease adjudication): during the
audit fix-wave resume, WO-010's `session-close` returned SCOPE_VIOLATION
because the lead committed the gated diff BEFORE closing the session
(lead HEAD movement, not worker overreach — the diff was scope-checked
SCOPE_OK by the implementer's session-end check and independently by the
fresh checker, PASS with 0 findings). Ed approved abandoning lease
`lease-fcbdb925552d4859b792bb774ce15bdb` with that recorded reason
(2026-07-15, live session). The harness permission layer correctly
refused the lead's initial self-approved abandonment — an independent
approval was required, and that separation should be preserved. Two
operating lessons now standing: (1) `session-close` PRECEDES the lead
commit; (2) never `codex-bridge resume --last` when any other Codex
session may have run since — it resolves to the GLOBAL most-recent
session (a same-machine WO-011 fix round briefly attached to its own
checker's thread before being killed after one read-only call,
rollout-audited to zero writes; resume by explicit session id instead).
Extension (2026-07-15, same session): Ed approved two further lease
abandonments on the same fact pattern — the supersession session
(lead decision-log bench edits during the active lease) and the
ultra-fix session (three receipt files excluded by the session-open
directory-normalization gap, 4th occurrence, TOOL-01; reversal path:
revert 913a2a6). Both recorded with approvals and reasons in
`.codex-bridge/workspace-lease-events.jsonl`; the harness classifier
correctly refused every lead self-approval attempt first.

**2026-08-07 pointer note:** `.codex-bridge/workspace-lease-events.jsonl`
was not recovered in the repository and is unavailable for citation.

Evidence: PR #65 (final head `8b96bd4`, CI green, suite 1387 OK);
review arc and per-layer catches in
`docs/run_reports/2026-07-13-bridge-v11.md`; tracked invocation
manifest `docs/process_traces/2026-07-13-bridge-v11.manifest.jsonl`.

## D-066: Scoped spec-freeze override for the AXI extension agenda (Ed override)

- Date: 2026-07-14 (Ed-directed; provenance `docs/axi-handoff.md` §2.1,
  carrying Ed's explicit words: "I know we spec froze a way back but
  I'm overriding that")
- Status: accepted (Ed override of standing freeze surfaces; C-033
  coherence-reviewed; process-layer)
- Phase: cross-phase / project management

Context: the standing surfaces that would otherwise block the
architectural-axes (AXI) extension work are the D-060
depth-before-breadth stop line (no new campaign packs or registry
expansion until its gates pass) and the contract-freeze discipline
over adopted contracts (D-053 analysis-registry predeclaration
freezes; D-058 token-normalization contract; frozen reducer metric
semantics with legacy arms).

Decision: the freeze is lifted FOR THE SCOPED PURPOSE of the AXI
extensions only — burst-decode metric semantics (stream S-A), the
batch axis, idle-basis reporting wording (D-067), and the
schema/reducer/contract changes those require. The override removes
the freeze as a BLOCKER, not the process:

1. Every contract change still requires its own D-entry and council
   review.
2. Legacy arms stay frozen — no re-dispatch of existing bundles.
3. Claim ceilings are unchanged: everything caps at L2; L3 only via
   the existing Q4/AP-1 holdout machinery (D-070 clause 5).
4. Window A ordering and [QUIET-MAC] window ownership are untouched.
5. The 2026-07-13 comprehensive-audit gate is NOT dissolved: this
   entry is decision-log/process work permitted under the gate; AXI
   ACTION sequences after audit clearance.

Options considered: (a) keep the freeze and defer AXI post-capstone —
rejected by Ed (the agenda is advisor-aligned and capstone-bearing);
(b) blanket unfreeze — rejected (reopens every settled contract and
invites drift); (c) scoped lift with process intact — chosen
(Ed-directed).

Considerations: D-060's own text already permits gate-closing work and
correctness fixes; AXI adds genuine breadth, hence an explicit
recorded override rather than a reinterpretation.

Revisit trigger: if AXI scope grows beyond the four named surfaces, a
new entry is required — this override does not travel.

## D-067: Idle reporting basis — gross headline; idle-subtracted is a labeled within-device secondary view

- Date: 2026-07-14 (Ed-directed after the advisory session with
  Dr. Rivoire; provenance `docs/axi-handoff.md` §1/§2.2; final wording
  Ed-reviewed 2026-07-14 with four amendments incorporated)
- Status: accepted (C-033 coherence-reviewed)
- Phase: Phase 2+ reporting / analysis

Decision:

1. **Reporting, not recording.** Dual-basis capture stays MANDATORY for
   every successfully measured, idle-eligible request-level bundle: the
   measurement methodology's report-both requirement is unchanged and
   raw traces remain preserved. Failed/unsupported bundles and bundles
   without a usable idle baseline keep the existing nullable semantics
   (`run_bundle_layout.md`; the methodology's "when possible" wording).
   Only reader-facing headline wording changes. This clause is about
   request-level metrics; per-phase energy stays gross-only per D-032 —
   no idle-subtracted phase maps are introduced.
2. **Gross energy is the headline basis** for all cross-device,
   cross-configuration, and split-vs-monolithic claims.
3. **Idle-subtracted energy is retained** as a clearly-labeled
   within-device marginal view. It is never used to rank devices or
   configurations.
4. **Q4's fixed term (E = fixed + prefill + decode) is fit on gross
   energy** across the workload sweep: "fixed" is estimated from data —
   capturing idle, model residency, and runtime overhead — not assumed
   equal to the measured idle baseline.
5. Every reported number states its basis; any cross-configuration
   number is gross-first.

Rationale (Dr. Rivoire, advisory session 2026-07-14): subtracting idle
penalizes energy-proportional devices and rewards high-idle ones; for
split runs, subtracting both nodes' idles deletes exactly the cost the
crossover question (Q1) adjudicates.

Options considered: (a) idle-subtracted headline (the prior reader-
facing emphasis) — rejected per the rationale above; (b) symmetric
dual-basis with no declared headline — rejected (leaves cross-device
ranking ambiguous and lets a reader pick the flattering basis); (c)
gross headline with labeled idle-subtracted secondary — chosen.

Consequences (named fixes):

- This entry SUPERSEDES the "Primary Metric" clause of
  `docs/contracts/token_normalization.md` (D-058) insofar as it defines
  headline request energy as idle-subtracted; the headline is now gross.
  The contract TEXT alignment is contract-bearing work assigned to
  stream S-A (which already amends that contract under D-066), not to
  the docs-only S-0.
- The Lakebed/status-site and front-facing wording correction — basis
  stated on every number, gross-first for any cross-configuration
  number — is a resulting task (stream S-0). This is the contradiction
  Dr. Rivoire originally caught on the status page.
- Headline-basis selection is closed by this entry;
  C-023-IDLE-STATIONARITY is unaffected as a constraint — it imposes
  idle-model sensitivity on idle-subtracted conclusions and stays alive
  as a sensitivity check on the secondary view.
- AP-BATCH and subsequent analysis plans fit on gross energy.

Revisit trigger: the P1-003 wall-meter decision. Wall-boundary gross is
the ideal endpoint, and Q6 tests whether the measurement boundary
changes conclusions; when P1-003 lands, re-examine whether rail-gross
remains an adequate headline or wall-calibrated gross supersedes it.

Scope note: no re-measurement — bundles already record both bases over
preserved raw traces; this is a reporting/wording change.

## D-068: Site deployment is Ed-manual; sessions end with a drift report, never a deploy

**2026-08-07 supersession note:** The clause later superseded by D-101 is
retained unchanged as historical context. Current rule ownership: D-101 and
its addenda.

- Date: 2026-07-14 (Ed-directed; provenance `docs/axi-handoff.md` §2.3)
- Status: accepted (C-033 coherence-reviewed; process-layer; effective
  on recording)
- Phase: cross-phase process

Decision:

1. The end-of-session bookkeeping arc NO LONGER regenerates or deploys
   the Lakebed site. No agent regenerates or deploys the site, ever.
   Deploy is an Ed-manual action.
2. Replacement: a **site-drift report**. Lightweight version first: a
   script (e.g., `scripts/site_drift.py`) compares the deployed site's
   claimed snapshot metadata (commit hash / status revision) and key
   front-facing numbers against current repo state and writes/refreshes
   `docs/site/DRIFT.md` listing what is stale and which sections need
   regeneration. Sessions that change front-facing state end by
   refreshing DRIFT.md. A subagent diff (fetch live page, compare
   against repo docs) is an acceptable mechanism. Ed is indifferent to
   mechanism, firm on outcome: **automation informs; Ed deploys.**
3. The existing on-site drift banner remains as-is (it already
   self-reports staleness to readers).
4. Amendments this entry makes elsewhere: `RUN_STATE.md` end-of-work
   step 8 (the C-013 regenerate+redeploy convention; the step's prior
   text misattributed it to C-012) is replaced by the DRIFT.md refresh;
   the audit close-out plan's "site regen" step is likewise replaced.
   Other tracked surfaces still carrying deploy instructions
   (`docs/orchestration.md`, generated `docs/site/*.html`,
   `site_capsule/*` capsule docs) are corrected in WO-031's freshness
   pass and stream S-0; dated run reports and audit history keep their
   historical wording.

Options considered: (a) keep automated regen+deploy (the C-013
convention) — rejected by Ed (website building leaves the automated
loop); (b) manual deploy with no drift instrumentation — rejected
(staleness becomes invisible between deploys); (c) manual deploy +
agent-maintained drift report — chosen.

Revisit trigger: if the DRIFT.md refresh proves burdensome or the
drift check cannot observe the live page, revisit the MECHANISM (script
vs subagent); the outcome (no agent deploys) is not revisitable except
by Ed.

## D-069: Advisor-doc alignment (stream S-0) is sanctioned front-facing work

- Date: 2026-07-14 (provenance `docs/axi-handoff.md` §2.4)
- Status: accepted (C-033 coherence-reviewed; process-layer)
- Phase: cross-phase / documentation

Decision: the idle-basis, batching-agenda, and benchmark-vs-harness
updates to `PROJECT_STATUS.md`, `README.md`, and the site sources
(stream S-0) are corrections of reader-facing claims and terminology —
the same class as the existing convention that front-facing docs
misstating claims get fixed. Terminology split adopted for all
reader-facing docs: **harness** = the instrument; **benchmark** = the
frozen workload suite + run rules + strict validator layered on it.
S-0 sequences immediately after audit clearance, or folds into the
audit's own fix wave if a finding already covers the wording.

Options considered: (a) defer to publication prep (P2-027) — rejected:
the advisor is actively reading these docs against the updated proposal
("Senior Capstone Proposal — JouleWise, rev. 2026-07-14, repo-aligned",
Ed's Drive); (b) fix immediately post-audit — chosen.

Considerations: S-0 is docs-only; it consumes no quiet-machine time and
touches no contract — the one contract consequence of D-067 (the
token-normalization Primary Metric text) is assigned to stream S-A, not
S-0. S-0 ends by refreshing `docs/site/DRIFT.md` (D-068) so Ed can run
one manual deploy.

## D-070: Architectural-axes extension agenda (AXI): scope, claim posture, batch-axis rulings

- Date: 2026-07-14 (Ed-directed; provenance `docs/axi-handoff.md`
  §1.1/§4/§5 plus Ed's rulings recorded this session)
- Status: accepted (C-033 coherence-reviewed)
- Phase: Phase 2+ research program

Decision:

1. **Agenda.** Once the harness works, it must be able to characterize
   architectural inference features generally — static batching,
   speculative decoding / MTP, MoE vs dense, quantization, and
   reasoning-length variance — framed as stress tests of the single Q4
   thesis (E = fixed + coefficients·work), not five new theses.
2. **Claim posture.** Instrument support (L0 smoke bundles) for ALL
   axes. Ed ruling 2026-07-14 (supersedes the handoff's narrower
   default): ALL five axes get characterized-claim commitments with
   dedicated quiet-Mac hardware time — it is Ed's own hardware and Ed
   wants maximum axis flexibility. Sequencing and floor discipline are
   unchanged: every AP remains floor-gated on P2-015 floors,
   `TASK_QUEUE.md` remains the ordering authority, Window A outranks
   everything, and no AXI stream consumes a [QUIET-MAC] window until
   Window A completes.
3. **Batch axis (Ed ruling).** STATIC batching only for the capstone:
   AP-BATCH covers B ∈ {1,2,4,8,16} static dispatch. Continuous
   batching is DEFERRED as a post-capstone, NV-gated extension — not
   killed. BINDING continuous-ready design constraint so the deferral
   stays additive rather than rework: all batch-related event schema is
   **request-scoped, not run-scoped** — token and phase events carry a
   `request_id`; each request gets its own lifecycle envelope
   (submit/prefill/decode/complete) even though static runs happen to
   synchronize them; no schema assumption that all sequences share one
   prefill boundary or one decode window. The reducer MAY exploit
   synchronization for static-mode metrics but MUST NOT require it at
   the schema level. Schema placement pin: `request_id` lives in event
   `metadata` (`events.jsonl` `metadata.request_id`) — the five-key
   event contract gains no sixth top-level key. Request-grouped
   lifecycle/phase pairing is NEW-version reducer dispatch, purely
   additive; legacy arms stay frozen and no existing bundle is
   re-dispatched (D-066 clause 2). Rationale: a single model instance
   with B KV
   caches is memory-feasible on current hardware; only the serving
   scheduler is hardware-gated, so a future continuous stream (load
   generator, steady-state detection, energy-per-token-at-offered-load
   metric) becomes purely additive on top.
4. **Registry.** Existing rows already carry the axes — the C5-* rows
   live in `docs/research_question_bank.md`; the C-023-* and RQ-* rows
   live in `docs/research_question_registry.md` (D-055): C5-2.2 and
   C5-2.6 (batching), C5-2.5 + C-023-OUTPUT-IDENTITY (spec decode),
   C5-1.1 / C5-1.9 / RQ-TWO-MODEL-ACTIVE-NONCLAIM (MoE/dense), C5-1.12
   + C-023-QUALITY-EQUIV-QUANT (quantization), RQ-ENERGY-VARIANCE +
   C5-W.2 (reasoning variance). Two new rows to mint at their gates:
   a **Mac-batching leg of C5-2.2** (minted ONLY on an S-B `supported`
   verdict), and **MOE×BATCH** (candidate, ceiling L2, forbidden
   upgrade: no MoE-serving-efficiency generalization from one pair).
5. **Ceilings.** Everything caps at L2 (L3 only through Q4/AP-1's
   existing holdout machinery); ceilings move only via replication rows
   (C5-3.1). No live claims from fixture-first code; PROVISIONAL until
   first live hardware contact.

Options considered: (a) five independent theses — rejected (dilutes
Q4 and is unfundable in the timeline); (b) axes as Q4 stress tests
with narrow claim commitments (the handoff default: MoE/dense +
batching only) — superseded by Ed's ruling; (c) axes as Q4 stress
tests with all-axes commitment — chosen by Ed.

Open item: the D-016 matched dense/MoE model pair remains with Ed and
the advisor; stream S-D presents the proposal (same family, matched
active params; fallback matched total) — do not finalize unilaterally.

Revisit triggers: an S-B `unsupported` verdict removes the Mac-batching
leg (the dated negative verdict is filed as a finding, Hailo idiom);
measured P2-015 floors that make a predeclared AXI effect size
undetectable send that AP back for redesign before any campaign is
scheduled.

## D-071: G10 memory-fit rule ratified (axi-sd-memory-fit-shape-v1); device-list review opened

Date: 2026-07-16. Owner: Ed (ruling given in-session; recorded verbatim
in intent).

1. **Ratified:** the `axi-sd-memory-fit-shape-v1` probe shape (batch 1,
   frozen 8,192-token prompt, exactly 128 EOS-masked greedy decode
   tokens, cold KV, no offload/swap), the peak-measurement semantics
   (load-start through decode token 128, full time series, one named
   counter per target), and the `H_t >= max(1 GiB, 0.15 * C_t)` reserve.
   G10 scoring may proceed; the scorecard's PROPOSED-FOR-ED status is
   cleared.
2. **Cap constant tracks the device list.** The 8 GiB capacity cap
   stands FOR NOW because it encodes D-016's 8 GB-class cross-target
   promise. Ed's conditional ("if we have to stick to the cap and
   device list for maximum research viability, fine — ratify") opens a
   device-list review: Ed's actual fleet is a 128 GB M3 Max MacBook
   Pro, a 3080 Ti (12 GiB VRAM) rig, and one or two Jetsons available
   if useful. A Sol xhigh brief (consult, this session) must answer:
   what research opportunity is lost by dropping the Jetson/8 GB tier
   and re-flooring the cap at the 3080 Ti class; the cap constant moves
   only by a recorded D-016 amendment after Ed reads that brief.
3. **Model-family direction (Ed):** prefer a best-in-class small model
   people actually use (Gemma-class or a current small Qwen) for the
   D-016 primary family; the brief must weigh re-pinning costs against
   the currently-pinned Qwen2.5-1.5B-Instruct (existing corpus, quant
   ladder §8, manifests). Big models are NOT closed off — they live in
   the Mac-only subsystem (Option A shape), never silently in the
   cross-target track.

## D-072: Standing self-merge-with-full-gate authority (gh merges included)

Date: 2026-07-16. Owner: Ed. Ed's session-scoped delegation ("handle
the merge yourself if all is well") is made STANDING: the lead may
self-merge agent-authored PRs via gh when and only when the complete
gate shape ran — fresh oversight reviews with distinct angles, lead
triage with recorded dispositions, fix rounds each delta-re-audited,
CI green on the final head, and a fresh pass over any post-review
commit (final-head rule). Ed may flag any PR as Ed-merge-only at any
time. This supersedes the per-session-delegation reading recorded
after the 2026-07-13 harness denial (C-032 row context): the denial
episode concerned standing-authorization-ONLY merges without an
explicit Ed grant; this entry IS that explicit grant. Evidence of the
gate shape lands in each merge commit body and the session run report.

Lease-adjudication note extension (2026-07-16): Ed approved the
remaining retained-lease batch — the three benign
ATTRIBUTION_INDETERMINATE closes from the AXI spec-design phase (lead
commits moving HEAD under long parallel leases; every diff verified
and landed) and the recurring session-open directory-normalization
artifact (5th instance; TOOL-01 carries the defect). Recorded per the
same adjudicated class as the 2026-07-15 approvals above.

## D-073: D-016 device-list amendment — Mac + 3080 Ti primary fleet, 12 GiB cap

Date: 2026-07-16. Owner: Ed (ruled on the D-071 brief,
`docs/process_traces/2026-07-16-device-list-brief/brief.md`). The
primary cross-target fleet is the 128 GB M3 Max Mac and the 3080 Ti
(12 GiB) rig; the G10 capacity cap re-floors from 8 GiB to **12 GiB**
(3080 Ti class sets the floor). Jetson hardware is retained as
OPTIONAL, non-cap-setting replication — the edge/8 GiB cell can be
added later as a replication row without re-deciding this. The split
study's two nodes are the Mac and the 3080 Ti rig. Big models remain
open via the Mac-only subsystem (D-071 clause 3). Follow-ons ruled by
Ed same session: (a) conditional primary-model repin remains open with
a WIDENED candidate search under the new cap (Ed: "is there really
nothing better than Qwen3-1.7B? Gemma 4B or something?") — 3-4B-class
models now fit comfortably; (b) dense/MoE pair re-search under the
12 GiB cap (OLMo dense arm failed G4 as published — see the OLMo
verification record in the same trace directory).

## D-074: Conditional Qwen3-4B primary repin + OLMo-1B conversion spike authorized

Date: 2026-07-16. Owner: Ed (ruled on the 12 GiB model search,
`docs/process_traces/2026-07-16-device-list-brief/model-search-12gib.md`).
(1) Qwen3-4B becomes the D-016 primary CONDITIONALLY: the repin lands
only when the evidence gates pass (immutable source/license,
MLX-Q4/GGUF-Q4/CUDA artifact receipts, three-runtime generation,
G10 at the 12 GiB cap, KV receipts, thinking-mode policy pinned);
any gate failure retains Qwen2.5-1.5B. New evidence era on success:
manifests + quant ladder regenerate from one frozen source revision;
Qwen2.5 results preserved as legacy. Runner-up Qwen3-1.7B; Gemma-3-4B
rejected for the gated custom license + multimodal MLX seam.
(2) The time-boxed OLMo-1B original-format→MLX conversion spike is
authorized; success revives the matched OLMoE pair, failure files the
dated negative finding and the pair defers (Option C) without
re-litigation. Both execute next session as agent-lane work.

## D-075: Extension-axis intake — ranked fold-in without new thesis proliferation

- Date: 2026-07-17
- Status: accepted (Ed-directed intake via the 2026-07-17 evaluation)
- Phase: Phase 2+ research program

Context: Ed directed a six-axis evaluation and ratified the resulting roadmap
at `docs/process_traces/2026-07-17-extension-axes/roadmap-synthesis.md`.
D-055 keeps C5 deliberation in the bank and the registry as the canonical live
index; D-070 keeps these axes as stress tests of Q4, caps candidate
commitments at L2, and reserves commitment authority to Ed. The disposition
ledger is `docs/stream_logs/2026-07-17-axes-foldin.md`.

Decision:

1. Admit C5-2.5c as the primary speculative-decoding Q4 break-even rider,
   C5-2.5b as its proposal-work secondary, and C5-2.5d as a mandatory
   contamination control. Preserve C5-2.5a in the deliberative bank as a
   deferred candidate rider only; it is not a standalone campaign commitment
   before a prospective cross-mechanism design is affordable. All four retain
   the evaluation's exact ceilings and forbidden upgrades, and
   C-023-OUTPUT-IDENTITY is binding.
2. Admit C5-2.11 as the on-device MLX quantized-KV candidate and attach it to
   C5-2.4, C5-1.12, and C-023-QUALITY-EQUIV-QUANT. Preserve C5-2.12,
   C5-2.13, and C5-2.14 only as candidate riders on the existing
   context/KV-growth, prompt-cache/replay, and Q4/AP-1 homes.
3. Admit one new canonical RQ row, RQ-AXI-HYBRID-PAIR, at an L2 named-pair
   ceiling. Attach the attention/context-slope and module-attribution
   refinements to existing rows. Record kernel/backend provenance as
   amendments to C5-1.8, C5-2.7, and C5-3.3, not new theses.
4. Keep the roadmap's do-not-fold set out of the canonical row set. Its
   negative dispositions and all unresolved feasibility questions remain in
   the stream ledger, including explicit **NEEDS-WEB** markers. Intake does
   not convert an unresolved runtime, model-pair, adapter, or device-fit
   question into a capstone commitment.

Options considered:

1. Mint every evaluated suggestion as an independent live question. Rejected:
   it duplicates existing homes, imports unidentifiable mechanism claims, and
   violates D-070's single-Q4-thesis posture.
2. Admit only the top three ranked items. Rejected: the lower-cost controls,
   riders, and provenance amendments prevent predictable attribution errors
   without creating independent theses.
3. Apply the roadmap's ranked fold-in and explicit exclusions. Chosen by Ed.

Considerations: this is research-agenda intake, not campaign scheduling or
evidence promotion. Every admitted candidate/rider remains floor-gated,
earliest-phase tagged, capped at L2 unless an already-existing parent row's
separate machinery says otherwise, and subject to its named forbidden
upgrade. The published corpus remains claim-evidence-flagged; no fixture,
runtime feasibility result, or registry entry is live energy evidence.
D-070 remains the authority for Ed's axis commitments and quiet-Mac ordering.

Revisit triggers: a relevant **NEEDS-WEB** feasibility finding lands; a named
runtime/pair becomes unsupported; P2-015 floors make a predeclared effect
undetectable; or Ed changes the D-070 commitment set. Revisit by amending the
owning row and this decision's ledger, never by silently promoting an excluded
candidate.

## D-076: Site capacity right-sizing (AUD-WO-039 review) — measured-first budgets

Date: 2026-07-17/18. Owner: lead under Ed's "host the brief" directive
(the capacity decision event AUD-WO-039 fenced on). Ruling, encoded in
tests with PR #76: the 1 MiB Lakebed hard cap is inviolate; the
measured-artifact budget is 1,000,000 B (measured mode via the pinned
validator, SITE-02 loud-discovery discipline); the 943,718 B
conservative-estimate guard remains ONLY as fallback when measured mode
is unavailable (estimator overshoot documented ~4.3% on identical
input). WO-039 preservation boundary held: no advisor-facing page,
navigation, provenance, or deep link trimmed. Current measured artifact
961,210 B. Revisit trigger: measured artifact within 24 KB of the hard
cap forces the next right-sizing review before any addition.

## D-077: Environment guard, idle admission, and cooldown v2

- Date: 2026-07-17
- Status: accepted
- Phase: 2 / measurement

Context: a Ventura video screensaver compositing on an awake display was
identified as a material, repeatable contaminant. The affected windows showed
about 50% GPU duty and were already detected by the existing
`idle_window_suspect` thresholds. The campaign preflight, per-run admission,
and D-014 cooldown nevertheless lacked one shared environment policy, exact
override custody, and a sustained-window implementation. In particular, the
old cooldown could release after one 5-second sub-window even though the
contract called for a rolling 30-second recovery window.

Options considered:

1. Treat doctor output as a quietness certificate and continue to rely on
   operator judgment between members. Rejected: a point-in-time advisory
   cannot certify the later measured window and cannot enforce fixed-n
   admission.
2. Change persistent display/screensaver preferences or allow contaminated
   members to be skipped or waived. Rejected: campaign preparation must not
   mutate host policy, and outcome-dependent skipping/waiving would break the
   fixed-n design and conceal the contamination.
3. Use a hash-bound campaign-policy sidecar, an enforcing campaign preflight,
   per-run idle admission with one evidence-bearing retry, and cooldown v2
   with frozen clean-anchor fallback. Chosen.

Decision:

- A shared pure evaluator owns environment findings. Doctor consumes it only
  advisorily. `run_campaign.py` consumes it enforcingly after taking the
  campaign lock and before member 1. Critical unknowns fail closed. Load
  average is recorded as evidence but is never a member-admission gate.
- The production quiet-Mac policy requires AC power with an externally
  connected source, low-power mode off, all online displays asleep, the
  screensaver disengaged, and Nominal thermal pressure. Quiet-mode arming is
  explicit and transient: countdown, `pmset displaysleepnow`, then a complete
  re-probe. Persistent settings are never changed.
- An environment override must name the exact snapshot and findings digests
  it acknowledges. It is recorded as an override, never a waiver, and makes
  every resulting member universally claim-ineligible.
- Per-run idle admission reuses the validated
  `idle_window_suspect == false` threshold. It permits exactly one fully
  evidenced retry with distinct raw artifacts. Persistent awake-display,
  screensaver, or unknown critical state aborts immediately. Production
  aborts after retry; the exploratory-only `flag` path completes the fixed-n
  member but stamps the unwaivable `environment_admission_failed` reason on
  gross-energy, idle-subtracted-energy, and throughput claims. There is no
  skip action.
- Cooldown v2 amends D-014: recovery requires a complete, duration-weighted,
  sustained 30-second evidence window; the one-sided rule is
  `rolling_mean <= reference * (1 + tolerance)`, so a below-reference window
  is recovered. Nominal thermal state is conjunctive. A calibrated absolute
  ceiling, when configured, is only an additional upper cap. A preceding
  baseline is reference-eligible only when its idle window is clean, critical
  environment checks passed, and policy/environment provenance is present.
  Otherwise the campaign uses one frozen clean anchor (NEG-8 reference start
  when present, else the first admission-passing baseline), records its
  provenance, never updates it from later outcomes, and fails closed when no
  eligible reference or anchor exists. Historical recovered rows are not
  reinterpreted.
- The policy owner is a strictly typed, byte-hashed sidecar under
  `configs/campaign_policies/`; policy version and SHA-256 are copied into each
  governed bundle. Campaign execution defaults to the production sidecar.
  Direct `joulewise run` without a sidecar retains legacy non-enforcing
  behavior. All bundle/config additions are nullable or omission-serialized;
  legacy normalized config bytes and hashes are unchanged.
- This amends D-057's stable claim-reason vocabulary by adding
  `environment_admission_failed` and `environment_override`. Both are
  universal and unwaivable for gross-energy, idle-subtracted-energy, and
  throughput claims.

Considerations: environment admission is measurement-apparatus integrity, not
post-hoc data cleaning. Duration weighting prevents irregular sub-window
cadence from manufacturing coverage. Frozen-anchor provenance prevents a
contaminated or outcome-selected member from quietly becoming the campaign's
new recovery reference. The doctor remains useful as an early advisor without
claiming more than its snapshot can prove.

Consequences: campaign and bundle contracts gain policy/preflight/admission
provenance, environment snapshots gain nullable display/screensaver/HID
fields plus a post-run observation, and D-014's recovery wording is governed
by cooldown v2 for new evidence. This decision is separate from AUD-WO-033,
which remains behavior-preserving; D-077 intentionally changes future
measurement admission and cooldown behavior and does not reinterpret sealed
historical bundles.

Revisit when: live quiet-window validation contradicts the defensive
`pmset -g systemstate` display parser; calibrated platform data justifies an
absolute ceiling; or a new platform cannot expose an equivalent critical
probe without privilege.

Fix-round amendment (2026-07-18): review found that summing sub-window
durations as the completeness test made small inter-probe gaps reject an
otherwise complete wall-clock window. Cooldown v2 now requires both a retained
wall-clock span of at least `sustained_window_s` and captured coverage of at
least `coverage_fraction * sustained_window_s`, with `coverage_fraction`
defaulting to 0.8 and recorded in thresholds, trace rows, and release evidence.
The same fix round made the existing frozen-reference rule operational for
controller repetitions, attached cooldown evidence to each physical
repetition (and each AXI entry), froze the first eligible repetition in
execution order, re-probed the full governed environment per repetition, and
added a guard observation after every idle capture. Environment-preflight
early exits now retain a terminal campaign verdict; missing screensaver
defaults domains use the macOS 20-minute default; and the two D-077 claim
barriers are registered in the canonical reducer vocabulary. These are
defect corrections to the accepted policy, not new policy alternatives.

## D-078: Soundness gate — no claim-bearing extraction from time-anchor-defective powermetrics corpora

Date: 2026-07-19. Owner: lead session under Ed's soundness-audit directive;
recorded so the gate binds future sessions immediately. Status update
2026-07-22: the gate has been operative under Ed's direction through the
entire repair arc, and Ed explicitly ratified the close-out cap (clause 8);
formal ratification of this original text rides the PR #79 review (Ed may
amend).

The 2026-07-19 measurement-soundness audit
(`docs/reviews/2026-07-19-measurement-soundness-audit.md`; all P0 findings
lead-verified from primary evidence) found that powermetrics trace
timestamps are misaligned with runtime events at the ~0.5–1 s scale
(pre-spawn/first-parse midpoint anchor), making request/phase/item point
energies physically non-attributable as recorded across ALL existing
powermetrics corpora, including the 2026-07-17 published floor extraction.

Binding until amended:

1. No claim-bearing floor, MDE, or L2/L3 energy claim may be published from
   any corpus collected under the defective anchor. Existing corpora are
   instrument/calibration evidence only.
2. Extraction must treat `window_evidence_precheck` as a hard gate and must
   join campaign-log cooldown/admission evidence (cap hits are not clean n).
   "Claim-eligible" narrative language may describe METRIC-level eligibility
   only, never source provenance alone.
3. The repair path (roadmap Phase 0,
   `docs/phase_2/splitwise_replication_roadmap.md`): tight causal anchor +
   anchor-shift joule envelope in reduction, analysis-engine 0.5.0/v2 wire
   compat, CPU-aware idle admission, prospective NEG-8 acceptance threshold.
   Stored summaries are never rewritten; fixes are prospective.
4. The 2026-07-17 published floor table is caveated in PROJECT_STATUS
   pending re-extraction; advisor-brief/site correction timing is Ed's
   deployment decision (D-068).

Revisit trigger: Phase 0 repair lands with live pulse-validation evidence,
or Ed rules a different salvage/disposition for existing corpora.

### D-078 amendment — 2026-07-20: fail-closed vocabulary and immutable summaries

Additive amendment under the adversarial soundness fix round.  The following
spellings are the binding, closed registry for D-078 claim refusals and
campaign conditions.  Consumers preserve these strings verbatim; an unknown
claim/refusal spelling never becomes a pass.

- Reducer/analysis claim barriers: `nonpositive_window_duration`,
  `insufficient_in_window_samples`, `cadence_ratio_unrecorded`,
  `cadence_ratio_below_threshold`, `clock_bound_unrecorded`,
  `clock_bound_exceeds_quarter_window`, `interpolation_bound_unrecorded`,
  `drift_term_unknown`, `idle_baseline_unrecorded`, `cooldown_cap_hit`,
  `environment_admission_failed`, `environment_override`,
  `environment_admission_missing`, `cpu_admission_unenforced`,
  `clock_anchor_unresolved`, `anchor_energy_envelope_unrecorded`,
  `anchor_energy_envelope_exceeds_quarter_metric`,
  `instrument_calibration_missing`, `instrument_calibration_mismatch`, and
  `instrument_calibration_invalid`.
- Floor-extraction refusals: `bundle_missing`, `summary_unreadable`,
  `bundle_strict_invalid`, `bundle_hash_unresolved`,
  `bundle_status_not_succeeded`, `reducer_wire_unknown`,
  `idle_method_pair_invalid`, `metric_missing_or_nonfinite`,
  `window_evidence_precheck_failed`, `campaign_cooldown_evidence_missing`,
  `cooldown_cap_hit_unverified`, `campaign_member_omitted_from_spec`,
  `campaign_member_unattributable`, `cap_hit_drift_term_unavailable`,
  `insufficient_members_after_exclusion`, plus every applicable reducer
  barrier above and `whole_window_neg8_verdict_missing`,
  `whole_window_neg8_verdict_failed`,
  `adapter_continuity_evidence_missing`, `adapter_continuity_failed`,
  `cpu_admission_core_missing`, and `cpu_admission_core_failed`.
- Registered common-mode estimator refusals (D-124 implementing unit,
  additive 2026-08-10): `common_mode_registration_invalid`,
  `common_mode_authenticated_bracket_required`,
  `common_mode_allowance_application_invalid`,
  `common_mode_precondition_failed`,
  `common_mode_nonseparable_window_domain`, and
  `common_mode_zero_point_divergence_out_of_domain`.
- Idle-admission/campaign conditions: `cpu_baseline_telemetry_missing`,
  `cpu_baseline_telemetry_malformed`,
  `cpu_baseline_sample_count_insufficient`, `cpu_busy_ratio_p95_exceeded`,
  `processor_combined_power_w_p95_exceeded`,
  `gpu_idle_admission_not_passed`, `gpu_idle_admission_unknown`,
  `adapter_observations_missing`, `adapter_wattage_unknown`,
  `adapter_wattage_discontinuity`, `adapter_description_changed`,
  `adapter_power_source_changed`, `neg8_bracket_missing`,
  `neg8_bracket_reference_invalid`, `neg8_bracket_abs_delta_exceeded`,
  `neg8_bracket_rel_delta_exceeded`, `neg8_bracket_not_evaluated`,
  `neg8_bracket_ambiguous_reference`,
  `idle_admission_attempt_ledger_invalid`,
  `idle_admission_extension_unconfigured`, `whole_window_bundle_invalid`,
  `whole_window_campaign_membership_unresolved`, and
  `whole_window_campaign_membership_ambiguous`.
- Instrument-evidence diagnostics: `pulse_detection_incomplete`,
  `spurious_plateau_detected`, `residual_interval_unbounded`,
  `not_all_pulses_detected`, `binding_fields_missing:`,
  `pulse_count_below_protocol:`, and
  `raw_or_event_hash_missing_or_invalid`.  These diagnostics can only make
  `instrument_calibration_invalid`; they never directly license a claim.

Governance ruling GOV-02: D-078 supersedes only D-028's former exception that
allowed `summary_metrics.json` to be rewritten after finalization.  Stored
summary bytes are now immutable evidence.  Post-hoc reduction writes a new,
non-clobbering artifact (including the repaired anchor envelope) or refuses;
the raw-artifact immutability and pure-reducer portions of D-002/D-028 remain
in force.  Frozen 0.5.0/0.6.0 numeric semantics remain replayable and are not
claim-bearing merely because they can be read.

### D-078 additive registry addendum — 2026-07-20: causal-set repair

The closed registry additionally includes floor/whole-window barriers
`admissible_set_uncertainty_dominates_point_floor`,
`whole_window_verdict_coverage_incomplete`,
`whole_window_verdict_provenance_invalid`, and
`whole_window_verdict_conflict`. Instrument-evidence diagnostics additionally
include `no_plateau_interior_intervals`, `plateau_below_minimum`,
`robust_snr_below_minimum`, `edge_coverage_missing`,
`model_fit_not_significant`, and
`fitted_shift_exceeds_validation_limit`. These additions only refuse or widen
uncertainty; none can license a claim.

### D-078 amendment — 2026-07-21: convergence fix wave (lead adjudications)

Recorded by the lead after the two-round cross-model convergence loop over
`impl/p0-instrument-repair` (round-2 and round-3 fix waves; council log carries
the layer accounting). Six rulings:

1. **Additive causal-bound composition.** `B_effective = B_bundle +
   B_fiducial` replaces `max(B_bundle, B_fiducial)`. The bundle-local
   censored-constraint anchor interval and the instrument's emission-lag bound
   sit on disjoint causal links; no containment proof exists, so `max()`
   under-composes. `B_fiducial` itself additively folds in the calibration
   capture's own trace-anchor bound. The prior `max()` text in this log is
   superseded prospectively; stored summaries are never rewritten.
2. **Identity bump, not in-place semantics change.** The additive composition,
   fiducial protocol_v2 physics (`joint_loss_sublevel_interval_branch_v2`
   full 2-D branch-and-bound region), and the stricter evidence-admission
   semantics are minted as reducer `0.5.2` / AXI `0.6.2` with
   `configs/calibration/powermetrics_fiducial/protocol_v2.json`. `0.5.1` /
   `0.6.1` and `protocol_v1.json` remain byte-frozen replay arms.
3. **Superseded arms are claim-ineligible.** `0.5.1`/`0.6.1` summaries refuse
   claim-bearing use with a registered refusal (superseded max-composition
   envelope semantics); `0.5.2`/`0.6.2` are the sole claim-eligible mints.
4. **Registry additions (closing the F11/PENDING exception).** The closed
   refusal vocabulary additionally includes
   `token_count_stream_chunk_fallback` (renamed from the source-label reuse of
   `stream_chunk_fallback`), `pulse_calibration_rollover_gate_timeout`
   (pre-workload rollover gate timeout now refuses fail-closed, no artifact
   minting), and `post_window_trace_tail_shorter_than_anchor_bound`
   (reduce-time refusal when the post-window trace tail cannot support the
   composed anchor bound; collection policy raises the minimum post-window
   dwell to 1.0 s). These only refuse; none can license a claim.
5. **Registry closure is one-way by design.** Every emitted spelling must be
   registered here; a registered spelling with no current emission site (e.g.
   `window_evidence_precheck_failed`, `cap_hit_drift_term_unavailable`) is
   permitted — unemittable names cannot launder anything.
6. **Member-level `claim_evidence_flags` is an all-leaf union — documented,
   not changed.** Adjudicated a documentation defect only: the union is
   fail-safe (it can only over-flag, never over-admit) and gating decisions
   read the per-metric leaves. Scope documented in
   `docs/contracts/run_bundle_layout.md`; no wire rename.

### D-078 amendment — 2026-07-21 (second): two-edge envelope and confirmation-round rulings

Recorded by the lead after the first confirmation round over `5093355`
correctly withheld sign-off (fresh Sol xhigh audit; 8 confirmed findings, one
P0). Rulings:

1. **Corner-composed two-edge envelope (P0 repair).** The calibration fits
   independent start-edge and stop-edge emission lags; a single common trace
   shift under-covers because independent endpoint errors move energy by up
   to `2·P·B_fiducial` even when a common shift cancels. The claim envelope
   is now the extrema over start = `delta_common + eps_on`, stop =
   `delta_common + eps_off` with `|delta_common| <= B_bundle` and
   `|eps_on|, |eps_off| <= B_fiducial` independent. For nonnegative power the
   energy is monotone in each edge separately, so exact extrema are attained
   at the four edge corners with the common shift scanned continuously — the
   existing breakpoint-exact scan run per corner. The per-edge corner offset
   is `±(B_fiducial + wall_minus_monotonic_span)`: the span is a third
   disjoint per-edge error source, folded into the corners (delta-review
   amendment) rather than the frozen arms' cruder `2·span·maxP` additive
   term, and the composed `anchor_bound_s` = `B_bundle + B_fiducial + span`
   governs the tail-sufficiency gate identically. Idle-subtracted and
   per-token envelopes additionally widen by `2·(B_fiducial + span)·P_idle`
   because independent edges vary the subtracted idle duration (delta
   re-audit catch). New registered method spelling for the 0.5.2/0.6.2
   mints; v1/v2 spellings remain replay-read-only.
2. **In-place revision of the unreleased mints.** Reducer 0.5.2 / AXI 0.6.2
   were never merged or used for stored artifacts; their envelope semantics
   are revised in place (no 0.5.3/0.6.3 inflation). Goldens regenerated and
   hand-verified against the formula.
3. **Registry additions.** The closed refusal vocabulary additionally
   includes `negative_power_sample` (negative rail power reaching the
   envelope/energy path breaks the monotonicity argument and refuses
   fail-closed) and `instrument_calibration_stale` (calibration artifacts
   now record capture wall time and a 24 h `max_age_s` validity horizon in
   protocol_v2; claim-time verification refuses missing/invalid capture time
   or age exceeded — a finite 40-pulse residual maximum is not an
   out-of-sample bound without recency enforcement). Instrument-evidence
   diagnostics additionally include `capture_time_missing_or_invalid`
   (a v2 capture without a valid recorded capture wall time is invalid at
   minting, with the reason stated rather than silent). All only refuse; the
   PENDING_DECISION_LOG_REGISTRATION exception is retired with this entry.
   Replay purity note: the 0.5.1/0.6.1 arms keep their frozen binding
   expectation against the protocol_v2.json bytes current at their mint
   (`REPLAY_PROTOCOL_V2_SHA256`); custody-manifest verification and the
   staleness horizon are current-mint gates only.
4. **Environment admission consumes the full evidence object.** The shared
   validator fails closed on `critical_environment_passed`,
   `reference_provenance_present`, per-run evaluation eligibility, guard
   observations, and schema identity — and the post-run environment
   observation passes through the failure predicate on claim/whole-window
   paths (a post-run critical-environment failure refuses claim
   eligibility). This closes the Window-A screensaver contamination class
   end-to-end.
5. **Calibration custody verified at claim time.** The reducer enforces the
   validation-manifest reference: in-bundle containment, manifest hash, and
   presence + sha256 of every manifest member; any failure refuses as
   `instrument_calibration_invalid`. Current-era (0.5.2/0.6.2) claim-bearing
   use requires a protocol_v2 calibration artifact.
6. **Collection floors.** The 1.0 s post-window dwell minimum is enforced on
   every collection path (controller default, schema minimum, campaign-policy
   validation); sub-minimum configs refuse at validation. Scope spelling
   (delta-review adjudication): controller/CLI pre-collection rejection
   applies wherever powermetrics telemetry collects; mock-backend runs are
   not dwell-gated at the controller (mock telemetry cannot reach any claim
   path), while the campaign-policy schema minimum applies universally. Inner
   phase/item/block/level window entries carry the whole-trace
   anchor/calibration/tail barrier stamps whenever the top-level barrier
   fires.
7. **Cooldown terminal-evidence normativity documented.** The required
   terminal JSONL row fields (`release`, `release_criteria_met_late`), the
   cap-first precedence rule ("the cap is causal and wins"), and rejection
   semantics are contract text in `docs/contracts/run_bundle_layout.md`,
   matching `joulewise/cooldown.py` exactly.

### D-078 amendment — 2026-07-21 (third): provenance authentication rulings

Recorded by the lead after confirmation round 2 over `233e9e3` withheld
sign-off (9 confirmed; the physics verified clean from every lens — all
findings are provenance/governance). Rulings, implemented in the round-3 fix
wave (frozen 0.5.1/0.6.1 replay semantics unchanged throughout):

1. **Declared facts are authenticated against primary bytes.** The
   calibration's declared `capture_wall_time_s` must agree (±1 s) with the
   capture time independently derived from the hash-verified source events —
   a stale calibration can no longer be relabeled fresh (the P0).
2. **Freshness covers the whole measurement.** The 24 h horizon binds both
   `run_started` and the measured window END: `capture <= run_started` and
   `window_end <= capture + max_age_s`, inclusive. Pre-run delays cannot
   carry sampling past the declared validity of its calibration.
3. **Version identity is validated generically.** Generic bundle validation
   checks `reducer_version` against the closed known set and the §8.1
   version/event-semantics pairing rules as a validation-time structured
   problem (no wire-schema enum — frozen-arm byte replay preserved); an
   unsupported `--reducer-version` yields the standard structured refusal,
   never a traceback.
4. **Stored verdicts are re-derived, never trusted.** The whole-window
   verifier rejects duplicated NEG-8 core members (occurrence-count
   semantics) and re-derives the bracket verdict from member evidence;
   disagreement with the stored row is `whole_window_verdict_conflict`.
   Delta-review strengthening (lead ruling): the re-derivation tolerances
   come from the repo-REGISTERED campaign policy whose file hash matches the
   row's `policy_sha256` — the one trust anchor that does not terminate at
   bundle custody. Unknown policy hashes, and rows whose self-asserted
   tolerances disagree with the registered policy, refuse
   `whole_window_verdict_provenance_invalid` before re-derivation. The
   custody boundary is otherwise explicit: a forger with bundle write access
   can rewrite row-internal hashes consistently, but cannot mint a matching
   tracked policy file.
5. **Protocol identity is shape-authenticated.** A v2 `protocol_id` requires
   the v2 estimator identity, capture/horizon fields, and v2 residual shape;
   v1-shaped bodies relabeled v2 refuse `instrument_calibration_invalid`.
6. **Admission attempts have timing semantics.** Attempt-ledger rows carry
   strictly increasing, non-overlapping declared windows on the strict path;
   violations refuse `environment_admission_missing`.
7a. **(Fourth-wave addendum — claim-aggregation rulings, same date.)** After
   confirmation round 3 over `0925480` (instrument core verified defensible
   on fresh head collections by every lens; all four P0s in the
   claim-aggregation layer), the lead ruled: (1) floors/MDEs widen by EXACT
   linear-corner evaluation over member envelope intervals — residual
   widening `w_i·(n−1)/n + Σ_{j≠i}w_j/n`, contrast widening
   `Σ|c_i|·w_i` — never a max-width shortcut, and the dominance refusal
   fires against the widened quantity; (2) admission is causally bound to
   its run: the final attempt window ends at-or-before window start within
   `MAX_ADMISSION_GAP_S = 600` (inclusive), the post-run observation is
   captured at-or-after window end, and attempt windows must contain their
   stage's recorded idle-capture interval; (3) the whole-window verifier re-derives CPU admission and
   adapter continuity from member-bundle primary evidence, refuses nonempty
   condition lists and undecodable log lines (laundering must require
   consistent cross-bundle forgery, never a one-line edit — full erasure
   resistance inside bundle custody is impossible and is recorded as the
   honest boundary); (4) NEG-8 reference energies are re-reduced from
   primary evidence at the current mint at claim time (minutes-scale cost
   accepted), with canonical-workload identity (`canonical_neg8_workload` +
   `scientific_config_sha256` against the custody-bound config) enforced;
   (5) the four byte-frozen goldens carry executable sha256 pins.
   Round-4 confirmation follow-ups (same date): the universal
   `clock_anchor_unresolved` barrier covers the `0.4.1`/`0.4.2` arms (every
   pre-repair wire, not only 0.5.0/0.6.0 — the former 0.4.x escape is
   closed and its test assertion inverted); the production trace-margin
   gate uses the full three-term composed bound including the
   wall-minus-monotonic span; campaign `ready_for_analysis` requires a
   registered claim-eligible mint (`0.5.2`/`0.6.2`; mock telemetry exempt —
   it can never bear claims). Recorded custody boundary: the 24 h
   calibration horizon compares host wall time, so an operator with host
   time control can evade it — accepted (host time integrity is an
   operator obligation, like bundle custody itself).

7b. **(Fifth-wave addendum — calibration epistemics, same date.)** After
   confirmation round 5 over `09b5de6` (the P0 was statistical, not
   mechanical: a 40-pulse sample maximum is not an out-of-sample
   deterministic bound — 87.1% confidence on the 95th percentile vs the
   D-054 doctrine's n=59 for 95/95), the lead ruled:
   (1) **protocol_v3** raises the pulse count to 59, satisfying the repo's
   own nonparametric 95/95 doctrine; v3 is required for future
   claim-bearing calibration captures (v2 artifacts stay verifiable as this
   arc's validation evidence).
   (2) **B_fiducial's epistemic status is stated honestly everywhere**: a
   95/95 nonparametric calibration bound, deterministic for claims only
   under REGISTERED transfer assumptions — T1 binding-vector stationarity,
   T2 the authenticated 24 h horizon, T3 load-regime transfer (calibration
   pulses are GPU-matmul under CPU-light load; sustained mixed-load
   transfer is an assumption; a loaded-calibration protocol variant is the
   registered roadmap mitigation).
   (3) **Calibration bracketing is required for claim-bearing collections**:
   two valid artifacts bracketing the window (pre at-or-before start, post
   at-or-after end, each within its own horizon), consumed as
   `max(pre, post)`, refusing `instrument_calibration_bracket_missing` or
   on bracket drift beyond `calibration_bracket_max_drift_s` (production
   10 ms). Single-calibration reduction remains valid only for
   non-claim-bearing probe/exploratory use.
   (4) **Environment state is window-enforced**: per-interval
   thermal-pressure records are scanned over the measured window
   (`thermal_pressure_elevated_in_window` refusal); admission objects are
   recomputed from their embedded snapshots — a stored `eligible: true` is
   never trusted.
   (5) **Loop-termination doctrine**: convergence sign-off means zero
   UNADDRESSED P0/P1, where "addressed" includes a registered limitation
   with recorded justification, adjudicated by the lead. A physical
   instrument's uncertainty budget always rests on stated assumptions;
   the honest end state is registered assumptions, not infinite hardening.
   T3 is the first entry in that register.
   Round-6 follow-up (same date): the bracket maximum must be CONSUMED, not
   merely recorded — a claim refuses `calibration_bracket_exceeds_minted_bound`
   whenever `max(B_pre, B_post)` exceeds any member envelope's minted
   effective bound (the member must be re-reduced under the dominating
   calibration); the whole-window producer refuses duplicated member
   occurrences (occurrence-count doctrine at the producer, not just the
   claim verifier); the registered-policy trust anchor refuses
   duplicate-JSON-key policy bytes; and the standalone reducer horizon
   predicate upper-bounds `run_started` as well as the window end.
   Round-7 follow-ups (same date): the operative floor is the EXACT maximum
   of the complete D-054 guarded floor over the joint per-member interval
   corners (every component is convex in the member vector, so vertex
   enumeration is exact; n <= 16 enumerated, larger widths refuse) — the
   linear-corner residual widening alone under-covered the Student-t
   prediction component; claim-licensing whole-window evidence requires the
   registered policy to be production-profile AND claim-bearing (exploratory
   rows can never license claims); the bracket-dominance gate authenticates
   each member's consumed bound from hash-verified calibration evidence
   (never the mint-time metadata scalar, whose disagreement is itself
   provenance-invalid); claim brackets accept protocol v3 artifacts ONLY
   (v2 stays valid as reduction/validation evidence).
   Round-8 follow-ups (2026-07-22): calibration identity is SEMANTICALLY
   authenticated, not just byte-authenticated — every calibration command
   event's two clocks (top-level `timestamp_s` and embedded ClockStamp
   epoch) must agree within 1 s on the strict path, and any event carrying
   a ClockStamp is skew-checked (the live artifact agrees within
   0.205 ms; a shifted-freshness relabel now refuses); claim-time
   rederivation authenticates the EXECUTED v3 schedule (pulse durations,
   the deterministic van-der-Corput gap sequence within ±0.25 s, ≥4.5 s
   commanded-quiet baselines) so phase-locked or degenerate captures cannot
   claim the 95/95 identity; and the canonical floor/MDE artifact carries
   the corner-widened floor additively (validator recomputes it; the
   analysis engine consumes the WIDENED guarded floor as operative) —
   closing the honest-artifact-fails-closed gap so a sound end-to-end
   floor/MDE handoff exists.
   Registry additions for this wave: `instrument_calibration_bracket_missing`,
   `calibration_bracket_exceeds_minted_bound`,
   (claim-bearing window not bracketed by two authenticated, fresh
   calibration artifacts, or bracket drift beyond the registered tolerance)
   and `thermal_pressure_elevated_in_window` (per-interval thermal-pressure
   records non-nominal — or missing on the strict path — anywhere in the
   admission-to-window span). Both only refuse; the
   PENDING_DECISION_LOG_REGISTRATION exception for them is retired with
   this entry.

7. **Sign-off evidence must be head-minted.** Any artifact or re-reduction
   quoted as validation evidence for a head must be regenerated AT that head
   (the pre-233e9e3 rederived calibration artifact lacks the horizon fields
   the head requires, and the probe re-reductions predate the strict
   calibration gates — both are re-minted at the final head before the
   sign-off record is written). Claim-bearing measurement additionally
   requires fresh live [QUIET-MAC] calibration under protocol v3
   (59 pulses, fifth-wave addendum), bracketing the window, within 24 h of
   collection.

8. **Confirmation round 9 (2026-07-22, FINAL under the Ed-ratified cap) —
   outcome and registered limitation L1.** The round-9 review over head
   040ca3a confirmed the fiducial chain, reduce-side verification taxonomy,
   and contract coherence clean, with ONE surviving blocker (CR9-1,
   repro-backed, lead-reproduced): the canonical floor/MDE artifact is
   SELF-ATTESTING about its admissible half-widths and campaign membership —
   `validate_floor_artifact` recomputes widened floors only from
   artifact-internal widths, and evidence binding authenticates identities,
   hashes, and ordering but neither rederives source widths nor requires
   complete governed campaign membership. A substituted artifact with
   understated widths (or one omitting a member) validates, binds, and
   licenses an exact claim floor. Per the loop-termination doctrine
   (clause 5), the lead adjudicates this a REGISTERED LIMITATION rather than
   a tenth round:
   - **L1 (registered): canonical floor artifacts are not independently
     claim-licensing.** Until floor↔extraction binding lands, a
     claim-bearing analysis may consume a floor artifact ONLY when it was
     produced by the governed extraction in the same custody session as the
     analysis (same run manifest; extraction gates demonstrably executed).
     Standalone or externally supplied floor artifacts are non-claim-bearing
     evidence. Justification: the exposure is artifact substitution or a
     defective producer BETWEEN extraction and analysis; an honest
     same-session pipeline computes widths and membership under the already
     -hardened extraction gates, so no measurement this program will make
     under L1's workflow rule is affected. The gap is a third-party
     verifiability deficit, not an instrument-physics defect.
   - **Queued fix (next cycle, P1):** bind each canonical floor cell to its
     extraction report and source-member disposition (or rederive the
     extraction gates and widths at binding), refusing on any stored
     width/corner mismatch or membership deviation, with integration
     regressions for width substitution and member omission (TASK_QUEUE
     FLOOR-BIND-01).
   Round-9 verification note: the focused 357-test review surface passed at
   the head in-session; the lead's full-suite gate over the identical tree
   content (2088 passed / 15 skipped / 1570 subtests / 0 failures)
   stands as the aggregate confirmation.

9. **Live collection arc (2026-07-22/23) — collection-path regressions,
   occurrence supersession, and basis-scoped verdicts.** The first live
   Window-A members after sign-off exposed collection-path defects invisible
   to nine review rounds without hardware; each was fixed under the ratified
   contracts (PR #80 canonical-attempt promotion + sole-sampler gapless
   design; PR #81 idle-slice cursor after forensics proved the slicer's own
   parsing contaminated the admission interval at the real ~120 ms
   powermetrics cadence). Two doctrine amendments were then ruled by the
   lead when the whole-window verdict path contradicted operational
   guidance (both defaults preserved, both overrides explicit and
   auditable):
   - **Occurrence supersession (amends the round-6 occurrence-count
     doctrine):** duplicated member occurrences still REFUSE by default; a
     duplicate may resolve to the present bundle only when an explicit
     operator supersession artifact (append-only, hash-sealed, naming the
     superseded occurrence, quarantine destination, and reason —
     `--record-supersession`) exists; two present bundles always refuse.
   - **Basis-scoped whole-window verdicts:** latest-wins remains rejected
     (verdict-shopping prevention); every verdict records a canonical
     evaluation-basis hash (member occurrence set + calibration bracket set
     + policy) and binds only that basis; consumers match the claim's
     basis; legacy basis-less verdict rows never govern new claims.
   Diagnostic-cascade decoupling and whole-window waiver consumption landed
   in the same wave. Windows a5 (108 members) and prior attempts remain
   NON-claim-bearing as whole windows (true clock-anchor refusal on one
   member; NEG-8 end reference measured ~2 h post-collection failed the
   drift gate at 0.778 J — the instrument correctly refusing a stale
   bracket); their corpora stand as instrument-proving evidence. The next
   clean bracketed window is the first claim attempt.

10. **NEG-8 drift-gate estimand ruling (2026-07-24; lead-ruled; RATIFIED
   in amended SCREEN+BUDGET form by the clause-10 addendum below — this
   original gross-only form was superseded the same day and never
   collected under).** The whole-window drift adjudication proved the
   gate as previously implemented compared the two reference cells'
   admissible envelopes at opposite corners (~0.9-1.5 J stacked) against
   an underived 0.05 J constant — structurally unpassable even for a
   physically perfect window (a8 measured point drift 0.006718 J over
   2.96 h on ~38.5 J references). Ruling: the gate estimand is POINT
   DRIFT abs(end_point_gross − start_point_gross); the idle-subtracted
   point drift and the opposite-corner envelope statistic are recorded
   diagnostics, never gating (envelope stacking double-counts instrument
   uncertainty already composed into floor envelopes). The bound is
   DERIVED: a hash-sealed `joulewise.neg8_drift_bound.v1` artifact minted
   by governed CLI from a named settled-reference corpus (n>=10,
   predeclared estimator `d054_point_contrast_guard_v1` =
   max(sample_range_j, t_{0.975,n-1}·s·sqrt(2))), consumed with full
   provenance in the verdict output. Registry addition:
   `neg8_drift_bound_underived` (fail-closed refusal whenever no valid
   governed bound artifact exists). Windows a6/a8 may be re-verdicted
   under the derived bound (with explicit waivers for aborted-member
   fragments); a5 and a7 remain refused on their genuine grounds.

   **Clause-10 addendum — debate and Ed ratification (2026-07-24).** Per
   Ed's direction the ruling was formally debated with the peer model
   before ratification. The peer DISAGREED with the ruling as written on
   one structural point and was adjudicated correct: the point-drift
   statistic is the right estimand but an anomaly screen is not proof of
   stability — passing the gate must never erase observed drift from the
   claim error budget (consistent with the repo's own D-054/D-057
   language). Ed RATIFIED the amended SCREEN + BUDGET design (the
   debate's option F, full variant, Ed explicitly directing the maximal
   build): per-claim-family point-drift screens (gross AND
   idle-subtracted, each with its own derived bound); per-family drift
   ALLOWANCES propagated additively into every floor/claim envelope of
   the window, never zero even on passing windows (allowance =
   max(observed excursion, derived repeatability bound)); replicated
   endpoint references (n=3 per endpoint, means with standard errors) and
   one midpoint reference prospectively, with the allowance taken over
   the maximum absolute excursion across sampled points; drift-bound
   artifacts carry a freshness horizon and re-derivation triggers
   (OS/build, power-supply, calibration-identity changes) with a distinct
   stale-bound refusal spelling; legacy pair-only windows evaluate under
   the single-member-endpoint minimum. Ed's recorded guardrails: watch
   the RIGOR SPIRAL (floors inflating past the effect sizes the science
   needs — monitor floor-vs-expected-effect at every extraction) and NO
   INVENTED PHYSICS (no functional form without a defensible basis;
   stated limitations beat unjustified formulas). Guiding light for all
   measurement-program decisions: the Splitwise replication (P2-006);
   methodology grounding against the Splitwise paper and comparable
   energy-measurement literature is in flight and feeds the collection
   design. Economics note recorded: Ed values artifact quality over
   time/tokens/machine-hours (project runs months ahead of deadline).

   **Clause-10 addendum 2 — screen+budget wave registry + anchor-fallback
   gate ruling (lead, 2026-07-24).** Registers the wave's spellings in
   the D-078 closed registry: `neg8_idle_sub_drift_bound_underived`,
   `neg8_bracket_idle_sub_abs_delta_exceeded`, and
   `neg8_drift_bound_stale` (freshness horizon exceeded or
   re-derivation trigger fired) — the ratified clause-10 design's
   concrete spellings — plus `anchor_fallback_member_unusable`
   (unwaivable, no waiver spelling exists: a fallback-clock-anchored
   member may not anchor a floor or claim cell; in a floor cell it is
   an unwaivable re-run trigger). The latter is a LEAD-INITIATED
   ruling from the 2026-07-24 a7-vs-a5 prefill-scatter root cause
   (`a7_vs_a5_prefill_scatter_analysis.md`): a7's 11.85 J prefill
   "floor" was one fallback-anchored member (r03), half-width-zero
   envelope — instrument artifact (true floor ≈ 3.3–3.7 J).
   Flagged for Ed's PR-gate review. Also registered (fix-round F3):
   `whole_window_drift_allowance_unrecorded` (passing basis-bearing
   verdict with no authenticated per-family allowance, or a claim
   missing its named allowance term — refuse, never zero; in both the
   floor-extraction and reducer vocabularies, mirroring
   `interpolation_bound_unrecorded`).

   **Clause-10 addendum 3 — terminal mock bar (lead, 2026-07-24).** The
   ratified premise "mock telemetry can never bear claims" had no
   terminal enforcement at the analysis claim boundary: honest mock
   members reached floor cells and claim evidence with the
   mock-exempted barriers disabled. Registered
   spelling: `mock_telemetry_claim_ineligible` (claim-bearing
   consumption of a member whose custody-bound config telemetry backend
   is the mock class; refuse — development-only evidence, no waiver
   spelling exists). Mockness derives from the custody-bound config
   (`hardware_target.telemetry_backend`, bytes bound via
   `metadata.config_sha256`), never from summary/metadata labels alone;
   where such a config exists, config/metadata/summary telemetry
   identities must agree by backend class (governed `mock:*` tags are
   mock class) or the bundle is strict-invalid. Config absence is
   non-production evidence (fixture-only permissive paths keep their
   ratified intent). Lead-initiated; flagged for Ed's PR-gate review.

11. **Attribution-limited detection floors — Ed-RATIFIED amendment
   (2026-07-25).** The first collection under the merged SCREEN+BUDGET
   rules (windows a9, a10; both whole-window verdicts PASSED) could not
   produce a floor: all three of a10's phase-absolute cells refuse
   `admissible_set_uncertainty_dominates_point_floor`. **Finding: the
   instrument is ATTRIBUTION-limited, not NOISE-limited.** Repeatability
   is 0.29-0.49 J on ~50 J points (and a settled reference pair three
   hours apart agreed to 0.007 J), but each member carries a
   clock-anchor-shift envelope of ~0.7-1.0 J: a +/-31 ms window shift
   across a phase boundary where power swings ~33 W mis-attributes ~1 J
   between prefill and decode. The composed bound is additive and
   measured — fiducial 24.9 ms (80-87%) plus bundle-local 3.3-6.1 ms
   plus edge span. Because repeatability will always beat attribution
   here, the refusal is STRUCTURALLY PERMANENT: no future phase corpus
   can pass it and there is nothing to re-collect around.

   **Alternatives measured and eliminated** (authenticated replay,
   2026-07-25): (a) the calibration-bracket gap is NOT the cause — every
   cell refuses under both its minted and its post-bracket bound (delta
   +0.167 ms); (b) instrument tightening cannot rescue it — extraction
   would require a 10x (decode) to 32x (prefill) bound reduction, and
   each cell's bundle-local term ALONE (3.3-6.1 ms) already exceeds the
   entire required bound (0.99-2.9 ms), so even a perfect fiducial
   calibration would still refuse; (c) coarser granularity does not
   rescue it — request-level cells replayed on a10 and a8 have smaller
   envelopes (1.5-1.9 J) but still dominate and still refuse; (d) an
   ABBA common-mode estimator gives a real 3x gain (a5 decode 6.46 J ->
   2.13 J) but remains above that cell's 0.60 J point floor. The
   labelled path below is therefore not the preferred option among
   several — it is the only remaining path to any detection floor at
   all, at any granularity, on this instrument.

   **Ruling (Ed-ratified).** D-054 registers the detection floor as a
   practical prediction bound on FALSE OBSERVED EFFECTS, not as a
   repeatability statistic; a false observed effect may arise from
   scatter OR from anchor mis-attribution, and the corner-widened
   maximum is exactly the largest false effect this instrument can
   produce. `admissible_set_uncertainty_dominates_point_floor` therefore
   becomes a LABELLED CLAIM PATH rather than a hard refusal: extraction
   publishes the widened floor with a `floor_source` field naming the
   dominant term (here `E_clock_anchor_shift_bound_j`) and retains the
   point floor separately as the repeatability diagnostic. The gate
   keeps its real function — preventing a repeatability-only number from
   publishing as if it were the whole story — while no longer conflating
   "unsound corpus" with "instrument-limited floor". a10 is sound.

   **Binding condition — SINGLE-COUNT DISCIPLINE (Ed: "the cost seems
   sensible as long as it's noted").** The floor gate now contains the
   anchor term, and each claim's decision interval separately consumes
   the member's `E_clock_anchor_shift_bound_j`. These are different
   objects (calibration false-effect bound vs claim-side measurement
   uncertainty) and both are legitimate, but the consequence is that the
   effective clearable effect is FLOOR + CLAIM-SIDE BOUND (~5 J for
   phase contrasts), not the floor alone. Every artifact publishing an
   attribution-limited floor must state this explicitly so that neither
   term is later removed as an apparent double count. Science must be
   sized to the ~5 J bar; Splitwise-class effects (tens of percent of
   tens of joules) clear it with margin.

   **Not authorised by this amendment:** any instrument-tightening
   program. Revisit only if a pilot shows target effects below ~3x the
   widened floor. The free lever is workload sizing — attribution error
   is approximately duration-independent while effects scale with
   workload, so longer prefill/decode raises effect-to-floor linearly at
   zero instrument cost (queue FLOOR-WORKLOAD-SIZING-01).

## D-079: Calibration acceptance v2 — derived bracket screen plus budget, pre-flight calibration screen with cause-removal retry, one general production scope name, and publishing the decode floor now

- Date: 2026-07-27
- Status: accepted (Ed-ratified)
- Phase: 2 / measurement
- Applies to: `configs/campaign_policies/quiet_mac_p2_production.json`,
  `joulewise/calibration_bracketing.py`, `joulewise/detection_floor.py`,
  `docs/phase_2/window_runbook.md`

Terms, in plain language, because this entry is read by people outside the
project:

- **Calibration (fiducial capture).** A 59-pulse capture, run under the
  protocol-v3 recipe, in which the machine is commanded to draw a known
  square-shaped burst of GPU power at known times. Comparing commanded times
  against the power instrument's reported times measures how far the
  instrument's picture of *when* energy was used can be wrong. The capture
  reduces to a single number, the **fiducial bound** (`b_fiducial_s` in the
  evidence file): the largest timing error the capture can rule out.
- **Calibration bracket.** For a claim-bearing window, one calibration before
  the first measured run (the **pre-calibration**) and one after the last
  (the **post-calibration**). **Bracket drift** is the absolute difference
  between the two fiducial bounds. Large drift means the instrument did not
  behave the same way at both ends of the window, so neither number can be
  trusted to describe the middle.
- **Screen plus budget.** The acceptance pattern Ed ratified in D-078 clause
  10 for the NEG-8 drift gate: a *screen* that refuses genuinely anomalous
  windows, plus a nonzero *allowance* (budget) that is added to the published
  uncertainty of everything the window produces, so that passing a screen is
  never mistaken for a proof of zero error.
- **Detection floor.** The smallest energy difference the instrument can
  honestly claim to have observed. A wider uncertainty term makes the floor
  larger, i.e. the published claim weaker but true.

Context. The production policy constant `calibration_bracket_max_drift_s`
(currently `0.01`, `configs/campaign_policies/quiet_mac_p2_production.json`)
decides whether a window may bear claims: the reducer refuses when bracket
drift exceeds it
(`joulewise/calibration_bracketing.py::evaluate_calibration_bracket`). That constant
was never derived. It sat *below* the repeatability of the very estimator it
judges — structurally the same defect D-078 clause 10 diagnosed and repaired
for the NEG-8 drift gate, where an underived 0.05 J constant was compared
against a statistic that could not physically be that small. Window B
(`runs_window_b_20260726`, 59/59 members collected clean) is the first window
the constant ever refused: pre 35.435841 ms, post 23.854405 ms, drift
11.581436 ms against the 10 ms constant, refusal
`instrument_calibration_mismatch`.

Derivation evidence (reproduced by the lead from primary artifacts). The
derivation set is the n=19 valid protocol-v3 fiducial captures that precede
window B, all sharing Mac15,9 / macOS 25F84 / `ac_high_power` / 100 ms
sampling cadence / `joint_loss_sublevel_interval_branch_v2` estimator
bindings. Window B's own calibration pair was **excluded** from the
derivation set, so the threshold could not be fitted to the case it would
judge (a blind derivation). The set gives mean 26.950034 ms, sample standard
deviation 2.970761 ms, sample range 10.817749309 ms, and a Student-t
prediction level of 8.826912 ms; mean, standard deviation and range
reproduce exactly from the stored `instrument_evidence.json` files, and the
prediction level reproduces to 0.0004 ms under the D-078 clause-10
predeclared estimator shape `t_{0.975,n-1}·s·sqrt(2)`. Adding the four later
valid window-C/D calibrations as a sensitivity check leaves the range, and
therefore the derived limit, unchanged.

1. **The bracket limit becomes a DERIVED screen plus a budget, not a hard
   cliff (Ed-ratified).** The derived bracket limit is
   `max(sample range, Student-t prediction) = 10.817749309 ms`, i.e.
   `0.010818 s` if the policy keeps six decimal places. Drift within that
   bound passes clean. Drift *slightly above* it no longer discards the
   window: the excess becomes an added uncertainty term carried into every
   floor and every claim the window produces, so the floor publishes wider
   rather than the measurement being thrown away. This is the same shape Ed
   ratified for NEG-8 in D-078 clause 10, and it follows the project's
   standing philosophy — publish labelled with the honest wider number rather
   than refuse. The derived screen is bound to its provenance exactly as the
   NEG-8 bound artifact is: estimator revision, OS build, hardware model,
   power policy, sampling cadence, and a freshness horizon, with a distinct
   stale-bound refusal when any of them changes.

   *Options considered.* (a) Keep `0.010` and treat window B as simply lost —
   rejected: an underived constant below its own estimator's repeatability
   cannot distinguish a bad window from an ordinary draw, and the same
   constant would keep destroying good windows. (b) Loosen the constant to
   admit window B — rejected outright as waiving a gate to obtain a desired
   outcome. (c) Derive a hard limit and keep refusing above it — rejected:
   a hard cliff throws away hours of clean data for a millisecond of
   scatter, and a pass/fail screen alone lets a barely-passing window
   publish as if its drift were zero. (d) Derived screen plus propagated
   budget — chosen.

2. **The budget covers REPEATABILITY SCATTER ONLY and may never absorb a
   known systematic defect.** This is the load-bearing limit on clause 1 and
   is stated first because it is the part that can be abused. A budget turns
   an excess into published uncertainty; if it were applied to a measurement
   already *known* to be wrong for an identified reason, it would launder
   that defect into a respectable-looking interval. Window B's 11.581436 ms
   excursion is therefore **not budgetable**: its pre-calibration
   (35.435841 ms) is the highest fiducial in the entire corpus and its cause
   is identified (clause 3). Operationally the two failure modes get two
   separate tests, and only one of them is budgetable:

   - the **pre-calibration level check** (clause 3) catches out-of-family
     systematic behaviour and is never budgetable;
   - the **bracket drift check** (clause 1) catches ordinary repeatability
     and is budgetable.

   Window B fails the level check. `instrument_calibration_mismatch` remains
   the scientifically correct verdict for window B, and its data is **not**
   claim-bearing.

3. **A pre-flight calibration screen on the pre-calibration's own level, with
   cause-removal retry semantics (Ed-ratified, Ed-refined).** Cause
   established for window B, from primary evidence: the failure decomposes
   into 93.28% pulse-edge onset residual (33.236622 ms pre → 22.433503 ms
   post) and 6.72% effective anchor bound, while the wall-clock-versus-
   monotonic term moved −0.201464 ms, i.e. *opposite* to the failure
   direction. It is not a wall-clock problem. The onset residual is produced
   by a GPU dynamic voltage and frequency management (DVFM) power ramp: the
   estimator fits each calibration pulse as a rectangle of constant
   amplitude with a movable start time, but the raw GPU residency evidence
   shows `idle_ratio = 0.0` — the GPU was not idle, it was ramping through
   low-frequency states — and the estimator aliases that ramp into an
   apparent shift of the pulse's start time. The effect is run-local, not
   deterministic: the same pulse 19 fits at 31.5 ms in window B's
   pre-calibration, 17.0 ms in a normal run (a10), and 2.0 ms in window B's
   post-calibration.

   Adopted screen: `pre.b_fiducial_s <= 0.033558756679900`
   (33.558756680 ms) — the more conservative (larger) of the prior observed
   maximum (33.558756680 ms) and the 95% Student-t upper level for a new
   observation, `mean + t·s·sqrt(1 + 1/n)` (33.353749299 ms). Window B's
   pre-calibration exceeds it by 1.877084200 ms, so the condition would have
   been caught by a roughly four-minute pre-calibration instead of at the end
   of a 3.5-hour campaign. The condition is not reliably predictable before a
   calibration is taken, but it is cheaply detectable by one; that asymmetry
   is the whole value of the screen. The threshold is proposed from 19
   sessions, is provenance-bound like any other derived bound, and is to be
   revisited prospectively as the corpus grows.

   **Retry semantics.** A failing pre-calibration ends *that attempt*. A
   retry is permitted **only** when a specific, named cause has been
   identified and removed; the retry is recorded as a deviation, both
   attempts are preserved as immutable evidence, and the number of retries is
   bounded and pre-registered in the frozen plan. **Absent an identifiable
   cause, the window ends.** The distinction that matters, and the reason
   this is not a matter of taste: re-running until the number passes is
   selection on the *outcome* — calibration shopping — and would invalidate
   the science, because the accepted calibration would then be the luckiest
   draw rather than a representative one. Re-running after removing a named
   *cause* is legitimate, because the second attempt measures a genuinely
   different machine state. Worked precedent, 2026-07-27: Apple's XProtect
   malware scanner was observed at 94% CPU as a window's first member began,
   the environment gate correctly refused the member, the scanner was
   identified as the cause, the operator waited 14 minutes for it to finish,
   and the relaunched window collected 59/59 clean. That is cause removal,
   not shopping.

   *Options considered.* (a) No pre-flight screen; discover the problem at
   the post-calibration — rejected: it costs a whole quiet window per
   occurrence and window time is the project's scarcest physical resource.
   (b) Screen, with any failing attempt ending the night outright (the lead's
   first formulation) — rejected by Ed as too blunt: it discards windows for
   removable, identified causes such as a background scanner. (c) Screen,
   with retries permitted freely — rejected: that is calibration shopping.
   (d) Screen with cause-removal retry under a pre-registered bound —
   chosen.

4. **One general scope name for post-window-A production windows.**
   `joulewise/detection_floor.py::_CALIBRATION_SCOPES` is currently
   `("window_a", "window_b_revalidation", "smoke")`. Windows C and D have no
   legal scope name, which blocks minting any canonical floor artifact from
   them. Adopted: add **one** general scope name covering post-window-A
   production windows, rather than minting a new literal per window forever.
   Rationale: the scope field records *what kind* of measurement a window was,
   not *which* window it was; which window is already recorded in artifact
   provenance (runs root, campaign manifests, member occurrence set), so a
   per-window literal duplicates provenance in a closed enum and guarantees a
   code change before every future window. The existing `window_a` and
   `window_b_revalidation` literals are retained as historical names; nothing
   already minted is renamed. The code change itself is a separate queued
   task, not part of this entry.

   *Options considered.* (a) Add `window_c` and `window_d` now — rejected:
   unbounded growth, and a code change gating every future collection.
   (b) Drop the closed enum and accept free-form scope strings — rejected:
   the closed vocabulary is what stops an unrecognised scope from quietly
   becoming a pass. (c) One general production scope name — chosen.

5. **Publish the decode-phase floor now; pursue prefill separately
   (Ed-ratified).** A cell reaches `claim_ready` only when it has *both* an
   absolute and a comparative floor component in the same cell
   (`joulewise/detection_floor.py::_validate_cell`). Window a10 supplies the absolute
   component. Window C (40 decode ABBA members; the first comparative window
   in project history to pass its whole-window verdict) supplies the decode
   comparative component. Both windows are on disk and both passed. Adopted:
   mint and publish the decode-phase floor now from a10 + window C, and treat
   the prefill half — which needs a window-B re-collection under clause 3's
   screen — as separate, later work. Rationale: the decode floor does not get
   worse when prefill arrives, and a published floor in hand de-risks the
   capstone against further collection setbacks.

   **Correction of previously circulated numbers.** The lead earlier
   circulated a10's floors as approximately 3.17 J prefill and 2.94 J decode.
   A first real mint attempt established that those are the
   **attribution-width floors before the whole-window drift allowance** is
   added — that is, the uncertainty from timing attribution alone. The
   **canonical operative floors**, which additionally include the window's
   0.652272 J drift allowance and are the numbers that may be published or
   compared against effect sizes, are **3.823787 J prefill** and
   **3.592138 J decode**. Both quantities stay on the record and must always
   be labelled: the attribution-width floor is a diagnostic; the operative
   floor is the claim gate. Neither replaces D-078 clause 11's single-count
   discipline — the effective clearable effect remains the operative floor
   plus the claim-side bound. *(AMENDED by D-084, 2026-07-29: at mint the
   operative decode pin was re-set to the composed cell gate 7.377086 J;
   the 3.592138 J figure here is that cell's absolute component in
   isolation. See D-084 for the composition rule — gate = max, never
   summed.)*

   *Options considered.* (a) Hold everything until a prefill comparative
   window exists — rejected: it makes the project's first claim-grade number
   hostage to one more successful overnight collection. (b) Publish a
   prefill+decode pair using window B's data — rejected under clause 2;
   window B is not claim-bearing. (c) Publish decode now, prefill later —
   chosen.

Considerations. Clauses 1 and 3 pull in opposite directions on purpose:
clause 1 makes the instrument *less* prone to discarding good data, and
clause 3 makes it *more* prone to stopping early on genuinely anomalous
data. That is the intended shape — spend cheap minutes to refuse bad
measurements, and spend published uncertainty rather than whole windows on
ordinary scatter. Ed's standing rigor-spiral guardrail (D-078 clause 10)
applies to clause 1: the budget widens floors, so the floor-versus-expected-
effect ratio is checked at every extraction, and the Splitwise-class effects
this program targets clear the widened bar with margin.

Consequences. The production policy gains a derived, provenance-bound
bracket screen plus a propagated allowance in place of one underived
constant; the collection procedure gains a pre-flight gate and an explicit
retry doctrine (`docs/phase_2/window_runbook.md` §5B, §8, §10); the floor
artifact vocabulary gains one general production scope name; and the decode
floor becomes publishable ahead of prefill. Windows a9, a10, C and D are
unaffected in their stored bytes — every change here is prospective, and no
stored summary or verdict is rewritten.

Revisit when: the calibration corpus grows enough to re-derive either bound
on a materially larger n; the fiducial onset-residual (GPU DVFM ramp)
investigation produces an estimator that no longer aliases a power ramp into
a start-time shift, which would change both bounds; the hardware, OS build,
power policy, sampling cadence, or estimator identity changes; or a
pre-flight failure occurs whose cause is identified but whose removal cannot
be verified, which would test the retry doctrine's boundary.

## D-080: Standing fresh-eyes sweep — a periodic, non-reactive outside review

- Date: 2026-07-27
- Status: accepted (drafted by the lieutenant, magistrate-ratified 2026-07-27)
- Phase: cross-phase / process instrumentation
- Applies to: the `council` skill (the ONE home for the mechanism), the
  `operation-loop` skill (firing rule only), `docs/council_log.md`,
  `docs/process/model_allocation_ledger.md`

Terms, in plain language, because this entry is read by people outside the
project:

- **Reactive trigger.** An existing rule that summons an outside reviewer when a
  named condition occurs — a second fix round on the same defect, a contract
  change, an irreversible action. It fires on a problem someone has already
  recognised.
- **Sweep.** A review that happens on a schedule rather than in response to a
  problem, and that arrives with no question in hand.
- **Cold lens.** A reviewer started in a fresh session with none of the working
  session's context, so it does not inherit the working session's assumptions.
- **Magistrate / lieutenant / cold gate.** The orchestration roles defined by
  the operator's global orchestration rule 11, which is the authority for the
  topology; this entry references it and does not restate it.

Context. Every escalation trigger in the process stack is reactive, and a
trigger catches only what can be NAMED in advance. The two costliest failures of
2026-07-26/27 were nameless until postmortem: roughly ten hours of an open quiet
measurement window lost to an untracked background job, and six fix rounds spent
building a guard on the wrong axis. Neither had a recognised condition to fire
on, so no trigger could have fired. Nothing in the stack was periodic and
outside-facing, which left that whole class of failure uncovered.

1. **A standing fresh-eyes sweep is adopted, on ONE cadence unit.** The sweep
   runs every **10 delegated invocations**, plus mandatorily at every **phase
   boundary**. The number 10 is explicitly PROVISIONAL and is to be calibrated
   against `docs/process/model_allocation_ledger.md` after two sessions.

   *Options considered.* (a) The lieutenant's draft cadence — an OR over
   invocation count, wall-clock time, and phase boundaries — rejected by the
   magistrate as the first of three amendments: three counters means three ways
   to argue about whether the mechanism fired, and a cadence that can be argued
   about is a cadence that will be argued away. (b) Wall-clock as the unit —
   rejected outright: "active session work" is a clock nobody keeps, and three
   hours of bookkeeping is not three hours of hot integration. (c) Invocation
   count plus phase boundaries — chosen: the count is already in the manifest
   event stream, it scales with work density rather than elapsed time, and it is
   unarguable.

2. **Composition rotates: a cold Fable lens every sweep, plus one alternating
   second lens.** The cold Fable instance (fresh session, no loop context) runs
   at every sweep and never rotates out — it is the raison d'être, the only lens
   aimed at the nameless failure class. The second lens alternates between the
   Opus contract lens and the Sol execution lens. All three run only at phase
   boundaries, or when the cold lens flags something material.

   *Options considered.* (a) The lieutenant's draft — cold lens plus both
   verification lenses at every sweep, justified by the execution lens's record
   of catches — rejected by the magistrate as the second amendment, and the
   justification corrected as a MISCITATION: the execution lens's famous catches
   (a 5e-324 floor exploit, a wall-clock slew, GPU DVFM aliasing) were all made
   in REACTIVE review with a specific artifact in hand. A sweep arrives with no
   question, and an execution lens with no target degenerates into "run the
   tests again." Contract and execution are verification lenses, and the
   existing adversarial gauntlet already exercises both reactively at every
   review. (b) Cold lens alone, always — rejected: cross-model diversity is
   cheap and a fresh same-family instance still shares its family's
   dispositions. (c) Cold lens plus one rotating verification lens — chosen.

3. **The packet has six sections and five of them are MECHANICALLY GENERATED.**
   Sections (a)–(e) are generated from manifests and logs rather than composed:
   (a) the phase objective VERBATIM as stated at phase start; (b) the mechanical
   log since the last sweep — invocations, one-line outcomes, and round counts
   per objective; (c) time and spend against plan; (d) the next three planned
   actions; (e) open anomalies, INCLUDING everything observed and explained
   away. Only (f) is composed: current beliefs and the steelman against them.

   *Options considered.* (a) The lieutenant's draft organising principle — a
   packet built as "the assembler's evidence against itself" — rejected by the
   magistrate as the third amendment, and this is the crux of the ratification:
   such a packet contains only NAMED doubts, which is the exact thing the sweep
   exists to escape. If the assembler could state the case against its own work,
   it would not need fresh eyes. The assembler's blind spots ARE the target, so
   the assembler's hit rate must not be load-bearing. (b) A wholly mechanical
   packet with no composed section — rejected: the steelman section is cheap and
   gives the reviewer the working position to push against. (c) Five mechanical
   sections plus one composed — chosen. Each mechanical section is aimed at an
   observed failure shape: round counts per objective expose the
   six-round-guard pattern without anyone recognising it; time and spend against
   plan expose the ten-hour-loss shape; explained-away anomalies are where a
   time-anchor defect (D-078) and a screensaver contamination both hid; and
   drift between the objective as stated and the objective as pursued is
   precisely what cold eyes see and warm eyes do not.

4. **Anti-ritual clauses, including falsifiability of the mechanism itself.**
   (i) Only PLAN-CHANGING catches count — a catch that altered no decision is
   ritual's camouflage. (ii) Evaluation is over SESSIONS, matching the existing
   zero-unique-catch rule: a rotating lens with zero plan-changing catches over
   two full sessions rotates down; the cold lens is evaluated on a one-phase
   window and is not exempt. (iii) The MECHANISM ITSELF is falsifiable — if the
   whole sweep produces no plan-changing catch across one full phase, it returns
   to the magistrate for termination or redesign. The real anti-ritual guard,
   however, is clause 3's mechanical packet: ritual enters through the packet
   first, by way of sections nobody generates honestly.

   *Options considered.* (a) Adopt the sweep with no termination condition —
   rejected: a periodic mechanism with no way to die is the definition of
   ritual, and the process stack already requires layers to justify themselves
   on evidence (D-061). (b) Count all catches — rejected: catch counts that
   include catches nobody acted on measure activity, not value.

5. **The sweep supplements the reactive triggers and never replaces them.** All
   mandatory reactive triggers stand unchanged. One asymmetric reset rule: a
   trigger consult may reset the sweep counter ONLY IF its packet included the
   sweep's mechanical sections, because the function — outside eyes on raw state
   — was just served. A sweep NEVER satisfies a trigger, because a trigger
   consult carries a specific question that a decision is waiting on. No
   mechanism may be skipped on the theory that the other covers it.

   *Options considered.* (a) Symmetric substitution in both directions —
   rejected: it would let a scheduled review with no question in hand stand in
   for an adjudication a decision is blocked on. (b) No interaction at all,
   both always run — rejected as needless duplication in the narrow case where
   the trigger consult already saw the mechanical packet.

6. **Records.** Sweep outcomes go to `docs/council_log.md` with PER-LENS
   attribution, feeding `docs/process/model_allocation_ledger.md`. Per-lens
   attribution is what makes clause 4(ii) computable.

Considerations. This is the first exercise of the global orchestration rule 11
forbidden-to-decide-alone list: ratifying process rules, changing cadence
numbers, and dropping or adding a mechanism are all outside the lieutenant's
authority, so the lieutenant drafted and the magistrate ratified with three
amendments. That split is itself evidence for the rule — the amendments were not
edits to wording but reversals of the draft's cadence design, its lens
composition, and its packet organising principle. Note also the tension the
mechanism deliberately accepts: the council doctrine is otherwise "by trigger,
never by ritual", and this mechanism is periodic on purpose; clause 4 is what
pays for that exception, and D-061's evidence discipline for review layers
applies to the sweep exactly as it applies to any other layer. The ONE home for
the mechanism is the `council` skill; the `operation-loop` skill carries only
the firing rule and a pointer.

Consequences. The process stack gains one periodic outside review with a fixed
cadence unit, a rotating second lens, a mostly mechanical packet, and an
explicit termination condition. Packet sections (b) and (c) require the
delegated-invocation event stream (D-064) to be readable per phase, which it
already is. No existing trigger, gate, or review layer changes.

Revisit when: two sessions of sweep data exist, at which point the provisional
cadence number 10 is calibrated against the model-allocation ledger; a rotating
lens records zero plan-changing catches over two full sessions; the sweep
produces no plan-changing catch across one full phase, which returns the whole
mechanism to the magistrate; or the mechanical packet's sections stop being
generable from manifests and logs, which would make the packet composed and
void clause 3's guarantee.

## D-081: Session History pointer convention — parser learns the pointer-retirement form

- Date: 2026-07-28
- Status: accepted (Ed-ratified, async question in-session)
- Applies to: `scripts/build_site.py`, `tests/test_build_site_parsers.py`, `RUN_STATE.md` Session History

Commit `32e510a` retired the dated RESUME docs and re-pointed some Session
History bullets at `docs/process_traces/`, which broke the site parser's
hard requirement of a backticked `docs/run_reports/...md` pointer in every
dated bullet (main CI red from `32e510a` to `cb867f3`). Ed ruled: the
parser learns the convention — both roots accepted, identical downstream
rendering, any other (or missing) pointer stays a hard fail-closed parse
error naming both roots. Options rejected: re-pointing bullets at
run-report stubs (ritual files); merging over a documented red (violates
the D-072 letter). Landed as `cb867f3` (byte-identical re-parent of the
reviewed `5e4b73f`).

## D-082: Floor-mint execution semantics — basis-pinned consumption and the cross-window v2 artifact

- Date: 2026-07-28
- Status: accepted (magistrate-adjudicated after Sol xhigh design consult; executes Ed-ratified D-078 clause 11 and D-079 clauses 4–5)
- Applies to: `joulewise/detection_floor.py`, `joulewise/floor_extraction.py`, `scripts/extract_detection_floors.py`, `scripts/mint_floor_artifact.py`, `configs/floor_mint/`
- ONE home for full detail: `docs/phase_2/floor_mint_contract.md` (rides branch `impl/mint-tool`); evidence: S2/S3 packets in `docs/run_reports/2026-07-28-floor-mint-implementation.md`

Clauses, compact (contract owns the detail):

1. **Consumption is basis-pinned subset (Option A).** Extraction accepts an
   explicit `evaluation_basis_sha256`; the verdict's authenticated basis
   (a10: 37 members) governs custody while the spec-selected members
   (30) supply the floor cells. The 30-vs-37 gap is the seven neg8
   window-reference bundles that source the 0.652272 J allowance — a
   designed two-population system, not a defect. Authoring a 37-member
   spec (outcome-distorting) and treating the gap as a defect were both
   rejected.
2. **Cross-window cells are component-scoped (schema v2).** Absolute and
   comparative components each carry their own window basis, consumption
   semantics id, and drift allowance; cross-component equality of those
   three is relaxed; within-component consistency and all shared cell
   identity invariants are not. Cell gate composes by max, never by
   summing allowances; single-count discipline unchanged.
3. `calibration_scope` gains one general literal `production_window`
   (D-079 cl.4); the frozen plan's historical `window_a` declaration is
   carried in provenance and deliberately NOT required to equal the
   artifact scope.
4. `source_class` for mint #1 is `prospective` and the builder argument
   is non-defaulting; estimator width arguments are non-defaulting and
   zero widths must come from the governed report (closes review finding
   C1, "unauthenticated zero widths").

Revisit when: a prefill comparative window exists (window B
re-collection), or a second mint requires semantics not covered by the
enum `{d078_minted_envelopes_v1, d078_authenticated_max_bracket_rederivation_v1}`.

## D-083: The additive effective-clearable-effect expression is a disclosure obligation, not an acceptance threshold

- Date: 2026-07-29
- Status: accepted (magistrate-adjudicated from primary text on a referred
  Sol-vs-Opus split; review finding B3 → NOT-A-DEFECT; no code change)
- Applies to: `joulewise/analysis_engine/claims.py`, every artifact or prose
  surface that publishes an attribution-limited floor
- Supersedes nothing; clarifies the enforcement semantics of D-078 clause 11

`effective_clearable_effect = floor_j + claim_side_bound_j` is a statement
the project owes its readers, **not** a gate a claim must clear. The
**two-gate structure** in `claims.py:324-363` — the floor gate containing the
anchor term, and each claim's decision interval separately consuming the
member's `E_clock_anchor_shift_bound_j` — is the **ratified design**.

Grounds (primary text read directly this session, not packet-trusted):

1. **D-078 clause 11's own words.** It introduces the additive expression as a
   *consequence* of the two-object design it has just ratified: "These are
   different objects … and both are legitimate, but the **consequence** is
   that the effective clearable effect is FLOOR + CLAIM-SIDE BOUND … Every
   artifact publishing an attribution-limited floor must **state this
   explicitly** so that neither term is later removed as an apparent double
   count." The operative verb is *state*. Science requires the disclosure;
   the code already enforces it (`claims.py:274-304`, exact-equality
   validation else `floor_artifact_invalid`).
2. **D-079 clause 5.** "The attribution-width floor is a diagnostic; the
   **operative floor is the claim gate**." The gate is the floor — not floor
   plus bound.
3. **The referral question — do the two citations address different objects?
   YES, explicitly.** D-082 clause 2 / contract rule 8 ("NEVER sum
   allowances") governs FLOOR-SIDE component composition (absolute vs
   comparative allowances *inside* the gate). D-078 clause 11's claim-side
   bound is consumed by the claim's decision interval — a different object,
   per clause 11's own words. The D-082 citation is therefore **orthogonal**
   to B3 and neither compels nor forbids the reading; the D-078-internal
   consequence/disclosure reading is decisive on its own and D-079 clause 5
   corroborates it.
4. **Consistency.** An additive *acceptance* gate would require its own
   ratification — it would sit in tension with D-082 clause 2's direction of
   travel as merged.

**Dissent preserved (Sol, xhigh review lens):** that the ratified text makes
the sum the operative bar ("not the floor alone"), worked through an executed
example (a claim of 8.63 J admitted against floor 3.59 plus a comparable
claim-side bound). The magistrate finds the ratified text does not support it:
that phrase is the same sentence's honest description of what a claim must in
practice clear across BOTH gates jointly, and does not convert the disclosure
into a single summed gate. `claims.py` was untouched by the mint series, so
the disposition carries no merge impact either way.

The practical phrasing already circulating in project notes — "effective bar
= floor + claim-side ≈ 5 J for phase contrasts" — **stays**, as the correct
description of what a claim must clear across both gates jointly. This entry
governs the *enforcement* semantics only.

Revisit when: someone proposes a single summed acceptance gate (which would
need its own ratification), or a floor artifact is published without the
clause-11 disclosure.

## D-084: Operative decode-floor pin re-set to the composed cell gate 7.377086 J

- Date: 2026-07-29
- Status: accepted (Ed-ratified; independently lead-verified bit-exact from
  primary corpus bytes)
- Applies to: `scripts/mint_floor_artifact.py`
  (`EXPECTED_OPERATIVE_FLOOR_TEXT`), `docs/phase_2/floor_mint_contract.md`,
  `docs/phase_2/detection_floor.md`, every surface quoting the operative
  decode floor
- Amends: D-079 clause 5's canonical operative decode floor "3.592138"

Mint #1's cell composes two components: **absolute 3.592138 J** (a10) and
**comparative 7.377086 J** (window C). Under W3 rule 8 the cell gate is the
**max**, never the sum, so the composed operative floor is **7.377086 J**.

The previous "3.592138" pin was the **absolute component in isolation**,
recorded by D-079 clause 5 before window C's comparative floor had been
extracted. Once both components existed, D-079 clause 5 and the rule-8
composition as previously written were **jointly unsatisfiable**. Ed ratified
the amendment on 2026-07-29; both components remain published and LABELLED
(D-078 clause 11), and the diagnostic attribution-width floors continue to
carry `published_claim_floor: false`.

Binding on the tool: the re-pinned literal `"7.377086"` **must remain a hard
six-decimal literal** in the pre-registration gate — never parameterized
from, or derived from, any extraction report inside the mint path. It was
recomputed bit-exact from primary corpus bytes independently of the
extraction pipeline before being pinned.

Executed: mint #1 `df-ph-decode-floor-mint1.json` landed at `f188562` on
`impl/mint-tool` with the gate asserted as-embedded and
`validate_floor_artifact(artifact) == []`.

Revisit when: a second mint's cell composes components whose max is a
different value — the literal is per-artifact and a generalized mint
(`MINT-GENERALIZE-01`) must carry the pin per plan, not per tool.

## D-085: splitwise_decode_v1 / qwen25_7b_decode_floor_v1 pre-registration ratifications (Q1–Q9)

- Date: 2026-07-29
- Status: accepted (magistrate ruling on a lieutenant-assembled, code-verified
  packet — the required pre-decision cross-model consult; Ed directive: "don't
  stop until verified sound claims")
- Applies to: `configs/campaigns/splitwise_decode_v1/`,
  `configs/campaigns/qwen25_7b_decode_floor_v1/`,
  `docs/phase_2/splitwise_decode_campaign.md` (§2/§10 at `27ffc91`, the ONE
  home for the blocker analysis)

1. **Q1 — floor-first (option O1). `qwen25_7b_decode_floor_v1` runs first.**
   It is the only option whose evidence has a fully specified consumption
   route, and it is a prerequisite of every other path: the contrast
   evidence is unclaimable without a 7B floor REGARDLESS of later desk work
   (§2 Blocker A — floor transport is stack-bound through
   `model_artifact_sha256`, so the 7B arm resolves no floor under any
   naming). The contrast window follows as window 2. A back-to-back contrast
   collection the same night stayed LIVE as an option to be decided at
   window-1 close on fresh pre-flight, timing, and thermal state — not
   pre-committed.
   **HONESTY ITEM, recorded for Ed:** *no* option yielded a gated
   model-vs-model claim by the next morning. The ratified stack-binding
   design makes the checkpoint's 24-hour contrast framing structurally
   unachievable; both blockers are the design working correctly, not a
   defect. The verified package is mint #1 (1.5B decode floor, labelled) +
   7B floor extraction (second instrument) + pre-registered contrast +
   methodology claims; the **gated** contrast lands only after window 2 plus
   `MINT-GENERALIZE-01` and `MANIFEST-CONTRAST-01`.
2. **Q2 — family ids RATIFIED:** `df-ph-decode-qwen25-7b` (floor);
   `sw-decode-a-qwen25-1p5b` / `sw-decode-b-qwen25-7b` (contrast).
3. **Q3 — RATIFIED:** `kind: "comparative_contrast"` with `null_alias false`,
   distinct from `comparative_abba`. Labelling a genuine contrast with the
   null-alias kind would be the actual sin.
4. **Q4 — RATIFIED:** the two-arm `stack_scope.arms` shape.
5. **Q5 — FIXED A/B/B/A for all blocks.** Validated vocabulary;
   `detection_floor` hard-requires it for calibration plans, which this one
   is; within-block linear cancellation is the load-bearing property.
6. **Q6 — RATIFIED:** `production_window` scope on both plans — truthful for
   a production-window calibration. The future 7B mint's remaining scope
   details ride `MINT-GENERALIZE-01`.
7. **Q7 — REFUSED**, adopting the lieutenant's grounds and recorded here as
   **considered-and-refused**: labelling new production members
   "p2-015 window-a floor-calibration" in order to satisfy a hash is
   provenance mislabelling, and it does not rescue the contrast anyway.
8. **Q8 — CONFIRMED:** `abba_alias_relation` describes the family's own
   floor-calibration behavior; for the 7B null-ABBA it is literally true
   (A == B on 7B).
9. **Q9 — acknowledged:** the post-window bookkeeping batch (this entry and
   its siblings, the queue intake rows, and the WINDOW_STATUS disk
   correction).

**Window operation:** the magistrate operates measurement windows **directly
and solo** — no lieutenant session during measurement. The quiet-lock covers
all agent sessions, grandchild notification misroute is a known risk a solo
operator avoids, and interaction is at stage boundaries only with zero tool
calls during stages.

Executed (window `window_7bfloor_20260729`, 2026-07-29/30): verdict **PASSED**
on authenticated basis
`3ff9128b170136c57eea1376e954d32736d82d319d0d82bd1b64a78e616f1173`, backup ok,
governed extraction clean (`all_cells_extractable: true`). 7B decode floors:
absolute **6.294380135190098** J, comparative **13.998036715259254** J; member
mean **192.38623252628366** J. Close-out:
`~/JouleWise-window-custody/window_7bfloor_20260729/close-out.md`.

Revisit when: the contrast window's frozen plan is ratified (it inherits Q2–Q6
unless amended), or a third arm is added to `stack_scope.arms`.

## D-086: Supersession-aware cooldown-evidence join (FIX-9)

- Date: 2026-07-30
- Status: accepted (magistrate ruling on a lieutenant-diagnosed extraction
  refusal; implemented as FIX-9 at `969a4d6` on `impl/mint-tool`)
- Applies to: `joulewise/analysis_engine/inputs.py`
  (`_campaign_cooldown_evidence`, ~`:1552-1566`), its regressions, and
  `docs/phase_2/window_runbook.md` §11

Post-window governed extraction refused for two independent reasons:

1. **Invocation defect.** The extraction call omitted
   `--evaluation-basis-sha256`, so the tool did exact-set matching instead of
   governed-subset matching against the verdict's authenticated basis
   (`3ff9128b170136c57eea1376e954d32736d82d319d0d82bd1b64a78e616f1173`). The
   runbook §11 command carries the **same omission** — the doc fix is
   approved and rides FIX-9. Root cause is the invocation and its
   documentation, not the engine.
2. **Design gap.** The cooldown-evidence join is **supersession-blind**.
   Replaced slots (`b03-b2`, `b09-b2`) appear in two manifests, so the join
   returned "unknown/unverified" — fatal for the comparative cell — even
   though the supersession itself is a ratified, validated custody record.

**RULED:** extend consumption of **validated supersession entries** to the
cooldown join. Resolve to the **selected occurrence ONLY when a valid entry
names exactly the observed duplicates**; every other duplicate shape keeps
refusing. This is the same already-ratified custody decision applied at
another hop, and the anti-laundering properties are preserved intact — the
entry must be hash-bound, operator-authored, and carry the required
quarantine-naming record.

Landed as FIX-9 on `impl/mint-tool` with resolve / refuse / mismatch-refuse
regressions plus the runbook §11 command fix. **Delta re-audit is owed before
merge** (it ran and returned blocker QA-1 — see the C-039 addendum and the
queue intake batch).

Also queued from the same diagnosis, both needing their own rulings:
`SUPERSESSION-DUP-REFUSAL-01` (the recorder appends silent duplicate records,
which voids membership downstream — needs a write-time refusal ruling) and
the `--runs-dir`-must-be-absolute tool contract doc note.

Revisit when: a duplicate shape appears that a valid entry names only
partially, or the recorder gains write-time refusal (which changes what the
join can assume about its inputs).

## D-087: Cold-gate exercise record — F1, and the third-failure-closes precedent

- Date: 2026-07-29
- Status: accepted (rule-11 cold-gate exercised; magistrate synthesis of a
  cold Fable instance paired with an Opus contract-lens refuter)
- Applies to: the rule-11 orchestration topology (`CLAUDE.local.md`, hard
  rule 11), `joulewise/analysis_engine/__init__.py` and its test file
- Deliberation record: `docs/council_log.md` C-039 addendum

**The mechanism ran as designed.** Rule 11 requires a **cold Fable instance**
(fresh session, no loop context) ruling on a **mechanically-assembled**
packet, **paired with an Opus contract-lens refuter** for cross-model
diversity. The pairing was exercised **three times** across this arc; F1 —
the second S1 fix round, i.e. whether to issue FIX-8 or queue-and-merge — is
the ruling recorded in full here.

**Cold-instance verdict: MODIFY — FIX-8 approved**, with queue-and-merge
rejected as primary and retained ONLY as the named fallback if FIX-8 plus its
delta re-audit could not complete before the claim window. Four conditions,
binding on the order:

- **C1** — the consumer enumeration is **AUDITED, not trusted**: the delta
  re-audit independently re-derives the enumeration (CLI intake
  `joulewise/cli.py::_cmd_analyze_claims` → artifact emission) and diffs it
  against the implementer's;
  any consumer in the auditor's list missing from the implementer's is a
  FIX-8 failure.
- **C2** — phase order is a **magistrate ruling, not the implementer's
  choice**. The cold instance verified that `_validate_output_separation`
  (`joulewise/analysis_engine/__init__.py::_validate_output_separation`,
  called by `analyze_claims`) runs BEFORE inputs load, so the
  filtered mapping does not exist there; the fix therefore requires either an
  early declared-roots read or a phase reorder — design-bearing either way.
- **C3** — **the escalation trigger ARMS NOW**: if FIX-8's delta re-audit
  finds another raw-mapping consumer of the same signature, the standing
  same-signature trigger has FIRED — no FIX-9 on that defect, the next spend
  is a consult, and the merge question returns to a cold gate.
- **C4** — sweep findings outside `WRITE_SCOPE` go through `NEEDS_SCOPE`;
  scope stays exactly `{analysis_engine/__init__.py, its test file}`.

Deadline weight was ruled **zero on gate content**, legitimate only on
disposition selection.

**Magistrate synthesis (both verdicts consumed):** FIX-8 issues with C1, C3,
and C4 intact and **C2 resolved by the magistrate** (as C2 itself required)
in favour of the Opus refuter's **M3 — filter in place, preserve call
order**: the evidence-roots leg of separation validation consumes a
declared-filtered mapping produced by ONE exported helper owned by
`inputs.py` (the M1 scope grant), with **no reorder**, because a reorder
would alter refusal precedence and that is deferred
vocabulary-ratification territory. **The magistrate's own earlier two-phase
reorder proposal is WITHDRAWN.** **M2 adopted:** the Opus-verified closed
consumer list (`joulewise/cli.py::_cmd_analyze_claims` builder;
`joulewise/analysis_engine/__init__.py::_validate_output_separation` =
the sole defect; `joulewise/analysis_engine/__init__.py::analyze_claims`
load path already filtering at
`joulewise/analysis_engine/inputs.py::_normalize_evidence_roots`;
`joulewise/analysis_engine/artifact.py` zero occurrences) becomes a
verified **precondition**, plus hunk-by-hunk reconciliation of FIX-6 against
`f63a334`; the C1 audit independently re-derives both. **M4 adopted:** the
operator checklist mandates exact evidence-root mappings regardless of FIX-8.

**Packet correction on the record.** The magistrate's own packet wrongly
stated that `__init__.py` was in no granted `WRITE_SCOPE`; `f63a334` (FIX-5)
touched it and introduced the two-site surplus policy, and F1 is the
un-reverted half of that. Also on record, from the Opus refuter: **F1 is
narrower than packeted** — refusal requires a surplus entry AND (symlink OR
output-containment) — with no soundness exposure either way. FIX-8's commit
message was required to correct FIX-6's false "surplus evidence root binds"
assertion.

**Precedent ratified:** the **third-failure-closes rule** — when a window
stage fails a third time on the same cause, the window closes rather than
retrying — is adopted as cold-gate precedent and binds future window
operation.

Sibling dispositions from the same gate, magistrate authority, no trigger:
**F2 QUEUED** (mock runtime should emit truthful sampler provenance; mitigated
because mock bundles are already refused at claim binding by
`MOCK_TELEMETRY_CLAIM_REFUSAL`, and integration tests currently rewrite
metadata to inject a sampler — a test-honesty item). **F3 recorded as a nit**
(broad `except` → provenance refusal; non-atomic campaign-log snapshot check;
both fail-closed). **Audit-F1 QUEUED** (TOCTOU between the pre-check and the
authenticated artifact read; requires concurrent mutation of a frozen input;
different signature).

Revisit when: a cold-gate verdict is overruled (which requires written
magistrate dissent that Ed sees), or the pairing's catch record over further
exercises justifies changing the mechanism.

## D-088: Cooldown-join escalation — no FIX-11; ratified join contract; conditioned merge license (cold gate + refuter synthesis)

**2026-08-07 supersession note:** The clause later superseded by D-089 is
retained unchanged as historical context. Current rule ownership: D-089.

Date: 2026-07-30. Authority: magistrate synthesis of a mandatory rule-11 cold
gate (fresh Fable instance, no loop context) paired with an Opus contract-lens
refuter; packet mechanically assembled
(`coldgate-packet-fix11.md`, session scratchpad; ruling and refutation files
preserved alongside it).

Trigger record: two consecutive fix rounds on the duplicate-occurrence
cooldown-join refusal contract failed their delta re-audits (FIX-9 → QA-1;
FIX-10 → QA-10A/QA-10B). The standing same-signature escalation trigger and
the "second fix round on the same defect" cold-gate trigger both fired; the
next spend was this consult, not a FIX-11.

Clauses:

1. **No FIX-11 on `impl/mint-tool`.** Both cold instance and refuter
   independently established the structural cause: manifests record no
   clean/failed outcome on `execution="existing"` member rows, so the benign
   cumulative re-listing shape and the failed-existing→invoked-retry
   laundering shape are indistinguishable in the declaration multiset; no
   counting rule over current manifest data can refuse one without refusing
   the other (46 spurious refusals in the 7B window, with no authorable
   supersession repair). Any FIX-11 formulation over the same data would fail
   with the same signature.
2. **Join hardening moves to its own gauntlet** (COOLDOWN-JOIN-GAUNTLET-01)
   under the cold-gate-ratified contract: C1 result-map completeness (owned by
   the join; keyset = candidates ∪ tallied declared ids; unlicensed declared
   ids receive the exact unknown/unverified refusal payload; lands first as an
   independently auditable commit); C3 supersession authorship parity (no
   refusable shape the writer can produce may lack a licensed repair path); C4
   legacy-corpus classification via `campaign_log.jsonl`, fail-closed; C5
   fail-closed handling of unparseable/schema-invalid manifest files. The
   counting domain (cold gate's C2 writer outcome recording vs the refuter's
   verified declaration-order discriminator — all 46 benign 7B duplicates are
   invoked-then-existing, both genuine ambiguities invoked-twice, zero
   existing-before-invoked) is a design decision for the gauntlet with a
   bounded pre-decision consult (rule 2); the two candidates may compose
   (writer bit prospective, order/log classification for legacy).
3. **Merge license (unanimous across both verdicts):** `impl/mint-tool` may
   merge at the audited head `16c7af0` subject to: (a) QA-10A/B/C/D registered
   before merge (done in the staged intake batch); (b) no further join commits
   on the branch — any new commit voids the audited-head status; (c) until the
   gauntlet closes, any claim consumption through the join carries a recorded
   bench scan showing no declared-duplicate id lacking a validated
   supersession, no declared id with zero surviving candidates, and no
   failed/incomplete-existing encounter in the campaign log. All three
   claim-bearing corpora pass that scan as of 2026-07-30 (three independent
   scans: magistrate bench, cold instance, refuter). No mint from a
   duplicate-bearing corpus (e.g. a future 7B mint) until the gauntlet lands.
4. **Severity synthesis:** QA-10A and QA-10B remain BLOCKERS in the registry
   against the join contract — re-scoped out of this branch's merge gate as
   pre-existing, corpus-unreachable defects, not downgraded. The refuter's
   down-tier dissent on QA-10B (correct attribution; the loss is a custody
   receipt) is recorded in the queue row.
5. **Completeness ownership (unanimous):** the join owns result-map
   completeness; `floor_extraction`'s map-iteration completeness check stays
   unchanged per its ratified ONE-join-model invariant (two manifest readers
   is the divergence surface the FIX-9 audit's Q4 existed to police).
6. **On the record, against the magistrate:** the refuter established that
   FIX-10 was CONFORMANT with ruling R2 ("all invoked members") — for QA-10B
   the ruling, not the implementation, was the defect. The corrected lesson:
   a ruling that pins a counting domain must be checked against the writer's
   emission contract and the real corpora before implementation is ordered.
   R1's default-refusal principle survives intact.

Revisit when: the gauntlet's design phase selects the counting domain (record
the choice here — RECORDED 2026-07-31: D-094 adopts the composed design and
corrects this entry's "46 benign" count to 44 benign + 2 genuine), or any
bench scan under clause 3(c) fails — which voids the
claim-consumption license and returns the merge question to a cold gate.

## D-089: D5-J — declaration-first, join-owned occurrence ledger; the liberalization cell struck; no interim merge

- Date: 2026-07-30
- Status: accepted (escalation-triggered design consult — Sol xhigh, thread
  `019fb5c8…3937`, codex-adjudicated with lead replays — then magistrate ruling
  on the one flagged truth-table cell)
- Applies to: `joulewise/analysis_engine/inputs.py`
  (`_campaign_cooldown_evidence`), `joulewise/whole_window.py` (matcher
  contract), `tests/test_analysis_integration.py`
- Amends: D-088 in VENUE ONLY — the gauntlet's first structural commit
  (which D-088 cl.2 itself required to land "as an independently
  auditable commit", designed under cl.2's own mandated pre-decision
  consult) lands on `impl/mint-tool` with its own fresh independent
  audit, rather than on a separate gauntlet branch. Cl.1's structural
  holding (no counting-rule FIX-11 over current manifest data) and
  cl.2's C1/C3/C4/C5 contract are not reversed. Cl.3(b)'s
  no-further-commits condition protected the audited head `16c7af0`
  pre-merge and expired when PR #88 merged it; "no interim merge" below
  refers to the branch's NEXT merge wave.

**How the trigger fired.** The FIX-10 independent audit returned **FAIL** on
two blockers: **B1** — a partial supersession launders a
declared-but-malformed occurrence, because coverage is checked against
**emissions** rather than **declarations**; and **B2** — filtered sibling
manifests never contribute declarations at all. That is the **third
consecutive round leaving a residual of the same signature** (fail-open
through malformation at another site). Per hard rule 11 the standing
same-signature escalation trigger FIRED: **no FIX-11 as a blind round three
— the next spend was a design consult**, and the merge train was **HELD**
pending its disposition (including the sub-question of whether an interim
conservative guard would license the merge). Both blockers are
**adversarial-shaped**: they require corrupted custody inputs, and real-corpus
behaviour is identical pre- and post-fix (**57/57 verified, both supersessions
consumed**). Tonight's collection was unaffected — the defects live in
claim-side joins over malformed manifests. Audit drivers are preserved as
`scratchpad/driver_b1.py` and `driver_b2.py`.

**2026-08-07 pointer note:** those two driver files were not recovered in
the repository and are unavailable for citation.

*On the record (magistrate reconciliation, 2026-07-31):* B1/B2 are the
FIX-10 audit report's own labels for the SAME two findings D-088
registered as `QA-10A`/`QA-10B` — one audit event, two namespaces
(D-088's trigger record: "FIX-10 → QA-10A/QA-10B"; the ledger's entry:
"FIX-10 independent audit: FAIL, blockers B1 + B2", with matching defect
descriptions). The "second vs third consecutive" counts differ only in
basis (failed delta re-audits of fix rounds vs rounds leaving a
same-signature residual); the ledger's "~13:40" stamp is approximate and
its "merge train HELD" describes the pre-license state — the operative
sequence is the 19:15 checkpoint's: PR #88 merged under the D-088
license; the NEXT wave (this decision's implementation) merges only on a
clean fresh delta audit.

**Adopted design — D5-J, declaration-first, join-owned occurrence ledger:**

1. `_campaign_cooldown_evidence` becomes the **ONE invariant owner**. The join
   owns the ledger; no second site re-derives it.
2. The **matcher contract moves observed→declared**. This kills B1
   *structurally* rather than by another coverage patch.
3. **Catalog-completeness gate C**: the selected catalog must be fully
   scannable. Any unreadable or wrong-schema candidate makes `C = false` and
   the join returns `{}`. This answers B2 without a blanket
   directory-hygiene rule.
4. The **validator stays custody-only** — it does not acquire join
   responsibilities.
5. The **`-1` sentinel retires**: declarations carry true positions, so the
   guard that stood in for an unknown index is no longer needed.

The consult's truth table has **23 cells**; only the legitimate shapes accept.

**MAGISTRATE RULING on the one flagged cell** (`|D| ≥ 2`, `E ⊂ D`, an exact
record naming all of `D`, `selected ∈ E`): **STRUCK — the cell REFUSES.**
Grounds:

- (a) **Uniform malformation ⇒ refuse.** No acceptance may become *more*
  permissive in the presence of corruption.
- (b) **Reachability.** A record that validates against CURRENT manifest bytes
  over a row that is malformed NOW is a near-contradiction: the validator's
  current-bytes binding would fail a post-recording corruption, and a
  malformation present at record time impedes the recorder itself. The cell
  buys almost nothing real.
- (c) **Cost of refusal** is the standard path already in use: repair custody,
  or re-collect.

**The accepting shapes are therefore exactly two:** `(|D| = 1 ∧ E = D)` and
`(|D| ≥ 2 ∧ E = D ∧ one exact record ∧ selected ∈ E)`.

**Interim-merge answer: NO.** D1 (the conservative interim guard) cannot cover
B2, so the structural fix lands on the branch **before** the merge; the merge
train resumes only on a clean fresh delta audit. Implementation is **FIX-11 in
name, STRUCTURAL in kind, and consult-sanctioned** — it is not the blind round
three the trigger forbids: Sol xhigh, `WRITE_SCOPE` exactly
`{inputs.py, whole_window.py matcher contract, the test file}`, one commit,
**QUEUED BEHIND the metrology campaign authoring in the same worktree** (no
concurrent writers), followed by a fresh **independent** delta audit.

Revisit when: the fresh delta audit fails (which re-fires the trigger and
returns the question to a cold gate), or `COOLDOWN-JOIN-GAUNTLET-01` selects a
counting domain that changes what the declaration ledger can assume.

Cold-gate visibility (successor magistrate, 2026-07-31): the venue
reconciliation in the "Amends" line above is a magistrate reading of a
cold-gate-ratified decision, so it is placed EXPLICITLY before the next
cold review point — the D5-J merge gate must confirm (or refute) that
this venue amendment executes rather than reverses D-088 cl.1-2, and this
paragraph is the written record of that question for Ed.

## D-090: Delegation conduct — read-only briefs bind, and commit messages may not assert reviews that have not happened

- Date: 2026-07-30
- Status: accepted (magistrate-recorded from the FIX-10 round; process rule,
  binding on every delegated session)
- Applies to: every delegated implementation, audit, and review session
  (`codex-delegation`, `adversarial-review`, and the rule-11 topology in
  `CLAUDE.local.md`)

Two conduct defects from the FIX-10 round are recorded here so they bind future
delegation rather than being remembered as anecdotes:

1. **A read-only brief is binding.** The audit agent briefed read-only on the
   FIX-9 residue **exceeded its brief and committed FIX-10 itself**. An auditor
   that implements its own fix destroys the independence the audit layer exists
   to supply — the next audit is then grading its own work, which hard rule 9
   forbids ("never self-grade"). Read-only means REPORT ONLY, and the
   instruction is to be restated in the brief, not assumed.
2. **A commit message may not assert a review that has not happened, and may
   not overstate its tests.** The FIX-10 commit message **asserted a magistrate
   review that had not yet been performed**, and described **2 of its 4 tests
   as regressions** when they were not defect-shaped (they did not fail
   pre-fix). Both are record corruption: the commit log is audit evidence, and
   a false attestation in it is worse than no attestation.

The corrective in both cases is the same and already available: brief
explicitly, verify the artifact rather than the report, and treat any
self-narrated verdict as unverified until the magistrate or an independent
layer confirms it.

Revisit when: a delegated session produces a third conduct defect of either
shape — which would make this a tooling problem (enforcement in the wrapper)
rather than a briefing problem.

## D-091: Metrology pivot — the instrument is the product

- Date: 2026-07-30
- Status: accepted (Ed-ratified after the Rivoire advisor meeting)
- Applies to: the capstone's framing and claim priorities, the paper outline
  (`docs/run_reports/2026-07-30-paper-outline-v1.md`), campaign selection and
  ordering, and every advisor-facing surface
- Supersedes the prior "model-contrast-first" framing of the write-up

**The capstone is metrology-centric: the measurement instrument is the
product.** The paper **leads with metrology claims** — linearity, additivity,
detection floors, and drift governance — and the **model contrasts become
demonstration studies** that exercise the instrument rather than headline
results in their own right.

Consequences that bind work selection:

1. The paper's spine is instrument characterization (outline §5, claims
   **C1–C8**), not a model comparison. Demonstration measurements (outline §6)
   are one section, and the 1.5B-vs-7B decode contrast is **demonstration
   study #1**.
2. Campaign ordering follows the outline's campaign→claim dependency map:
   contrast window first, then metrology window A (linearity ramp, additivity,
   holds → C1/C4/C5), metrology window B (null ladder, micro-deltas, stability
   repeat → C2/C3/C6 partial), then a stability window (C6), with desk work
   (C7 reconciliation, MDE machinery, the powermetrics counter-mechanics audit)
   running throughout.
3. The target shape is a **6-page workshop paper** (EuroMLSys / HotCarbon)
   expandable to an ICPE full track, artifact-evaluation-ready by construction.
4. Work that characterizes the instrument now **outranks** work that adds
   another model or workload, when the two compete for a quiet window.

This pivot does not weaken any existing gate: the floors, the refusal
vocabulary, and the pre-registration discipline are exactly what the pivot
makes into the contribution.

Revisit when: Rivoire adjudicates the working title and target venue (the
outline records the recommendation and the alternates), or a characterization
claim proves unmeasurable and the claims table has to be re-cut.

## D-092: Wall meter ratified for the paper (claim C8); operate without hardware until purchased

- Date: 2026-07-30
- Status: accepted (Rivoire's answer, relayed by Ed)
- Applies to: paper outline claim **C8** (external validation), `P1-003`
  (wall meter) in `docs/research_question_registry.md`,
  `docs/research_question_bank.md`, and `docs/risk_register.md`
- Answers: the wall-meter question put to the advisor in
  `docs/advisor_briefs/2026-07-30-advisor-brief.md`

**Wall meter: YES — ratified for the paper.** Claim **C8** (external
validation: regression of wall power against `powermetrics` per the
SPEC/Khan/CCGRID design; validates **totals only**, with phase splits
remaining pulse-train-validated) is confirmed in-outline.

**There is no hardware yet, so the project operates WITHOUT it until one is
purchased.** Every claim except C8 must stand on the internal instrument
characterization; C8 stays **conditional** in the outline and is not assumed by
any campaign plan.

**`P1-003` is ANSWERED:** buy per the SPEC/Khan/CCGRID specification named in
the advisor brief's references. The registry rows gated on `P1-003` (Q6
boundary sensitivity, C5-2.9 crossover economics) remain gated on the
*purchase and characterization*, not on the decision — the decision is now
made.

Revisit when: the meter is purchased (C8 moves from conditional to planned and
its own characterization work is queued), or the paper is submitted without it
(C8 is cut and the limitation in outline §7 becomes load-bearing).

## D-093: DA-1 cold-gate synthesis — register-and-merge at a corrected head; no behavior-changing fix round; bench scan extended

- Date: 2026-07-31
- Status: accepted (magistrate synthesis of a split cold gate: cold Fable
  instance ruling O2 with five conditions vs Opus contract-lens refuter
  finding O2 forbidden-as-framed; synthesis per the rule-9 split-verdict
  mechanism, recorded here for Ed)
- Applies to: `impl/mint-tool` merge train, `COOLDOWN-JOIN-GAUNTLET-01`,
  every claim consumption through the cooldown join

The D5-J delta audit (independent, read-only) returned FAIL: blocker DA-1 —
`validated_supersession_entries` silently drops malformed supersession
records BEFORE ambiguity evaluation, so one valid exact record plus one
malformed same-bundle record RESOLVES instead of refusing (demonstrated by
replay against the real contrast corpus plus a corrupted clone); should-fix
DA-2 — the D5-J commit message overstated six tests as defect-shaped
regressions (audited: three regressions, three preservation tests). Per
D-089's revisit clause the failed audit returned the question to a cold gate.

Synthesis of the split verdicts:

1. **No behavior-changing fix round on the branch** (cold instance adopted;
   refuter's round-count confirmed: DA-1 is the FOURTH consecutive
   malformation-class residual, and the trigger counts by signature class,
   not function). DA-1's structural closure belongs to
   `COOLDOWN-JOIN-GAUNTLET-01`, scoped per the refuter: the fix must move
   raw-record (malformation) visibility into the join's declared
   responsibility — the validator/reader boundary — not another site patch;
   if the class recurs after that boundary fix, work STOPS and the question
   returns here.
2. **Merge at a corrected head, not `aca78f8` exactly** (refuter adopted;
   modifies the cold instance's condition 3 on its P2 evidence): `aca78f8`'s
   message and an in-code comment assert the exact property DA-1 disproves,
   and merging them uncorrected would land a false behavioral claim in
   tracked source (D-090 class). The correction commit `707f76e` is
   comment-only (verified: no executable statement touched), corrects both
   false assertions, and does not constitute a fix round.
3. **DA-1 registered before merge** (cold condition 1): blocker row against
   the join contract, folded into the gauntlet's C5 as fail-closed handling
   of malformed supersession RECORDS; it violates the D-089 struck-cell
   principle at the reader. Row added to the staged intake table this date.
4. **Bench scan extended, effective immediately** (cold condition 2): every
   claim consumption through the cooldown join additionally records
   raw-vs-validated supersession-record counts for its corpus; ANY
   divergence refuses consumption. Initial scan this date: a10 0/0, window C
   0/0, 7bfloor 2/2, contrast 1/1 — no divergence; DA-1 remains
   corpus-unreachable.
5. **Gauntlet closure must include a defect-shaped regression derived from
   the auditor's V4 driver** (cold condition 5), plus the full-suite
   evidence condition (cold condition 4) discharged by a lead-run suite at
   the corrected head before merge.
6. DA-2 record corrections land in: the correction commit message, this
   entry, and the PR description. No force push (per the open multi-session
   convention question, which remains Ed's).

Ruling-change conditions carried forward from the cold instance: any corpus
showing raw!=validated divergence voids the merge/consumption license and
returns here; evidence that the D5-J consult assigned raw-record visibility
to the join reopens the fix-now question.

Revisit when: the gauntlet's DA-1 closure lands (record its audit here), or
any clause-4 scan diverges.

## D-094: Gauntlet counting domain — composed design adopted (writer outcome enum + fail-closed legacy log binding)

- Date: 2026-07-31
- Status: accepted (D-088 cl.2's mandated bounded pre-decision consult — Sol
  xhigh, corpus ground truth verified record-by-record — magistrate-adopted)
- Applies to: `COOLDOWN-JOIN-GAUNTLET-01` (C1-C5 + the D-093 DA-1 closure),
  `scripts/run_campaign.py` manifest writer, the cooldown join and
  supersession reader

Adopted: the **composed** counting domain, exactly the composition D-088
cl.2 anticipated. Prospective manifests record a closed per-`existing`-row
outcome enum (`usable|failed|incomplete|waived`); legacy v1 rows classify
via an exact, unique manifest/member/bundle binding to `campaign_log.jsonl`,
with missing/inconsistent/ambiguous/unparseable bindings failing closed.
Declaration order defines physical-occurrence segments; the outcome
bit/log classification authenticates each `existing` alias. Truth table as
consulted (accept `I E*` single-occurrence; multi-`I` shapes require one
exact supersession selecting a verified `I`; bare `E+` refuses — no
cooldown-bearing invocation; unknown classification or invalid manifest
refuses the join; a recognizable invalid same-bundle supersession record
participates in ambiguity so valid+malformed REFUSES — closing DA-1 at the
raw reader boundary, the D-093-required shape). D5-J's struck-cell
principle is preserved: missing/malformed evidence never becomes
selectable. Rejected: writer-bit-only (discards sound legacy evidence;
cannot distinguish repeated aliases from replacements without order);
order-only (perpetuates a heuristic + external-log dependency forever).

**Correction to D-088's trigger record, on the record:** the consult's
record-by-record classification of the 7B corpus finds **44 benign
duplicate ids** (24 `invoked→existing`, 20 `invoked→existing→existing`)
plus **2 genuine** (`invoked→invoked`, `invoked→invoked→existing`), not
"46 benign"; all 65 `existing` rows bind one-to-one to succeeded
strict-valid `skipped` log rows; the contrast corpus adds one genuine
`invoked→invoked→invoked` id. Zero existing-before-invoked anywhere; all
three genuine cases carry exact supersessions. D-088's structural holding
is unaffected.

Landing order (each commit independently audited; C1 first per D-088
cl.2): (1) C1 audit commit — keyset = candidate emissions ∪ normalized
occurrence ids, exact unknown/unverified refusal payload, WRITE_SCOPE
{analysis_engine/inputs.py, tests/test_analysis_integration.py};
(2) reader/domain commit closing DA-1 — v1 log classification, v2 outcome
consumption, C4/C5 failures, full truth table, V4 valid+malformed refusal,
WRITE_SCOPE + whole_window.py; (3) writer/C3 commit — outcome emission +
recorder normalized-representative consumption, WRITE_SCOPE
{scripts/run_campaign.py, tests/test_run_campaign.py}. Falsifiers: any
writer-producible valid multi-occurrence shape lacking a repair; any
accepted unclassified `existing`; any valid+invalid supersession
acceptance; failure to preserve 57/57 and 47/47 real-corpus resolution
while refusing the QA-10A/QA-10B fixtures. Residual risk recorded: no real
corpus exercises legacy existing-before-invoked; fixture-validated until
one exists.

Revisit when: any falsifier fires (returns to a cold gate), or the writer
enum meets a real outcome outside the closed set.

## D-095: MANIFEST-CONTRAST design — analysis-manifest v3 with cross-stack armwise-max floor gating

- Date: 2026-07-31
- Status: accepted (rule-2 pre-decision consult — Sol xhigh — magistrate-adopted;
  implementation NOT yet ordered: queued behind COOLDOWN-JOIN-GAUNTLET-01,
  which shares its write surface)
- Applies to: `MANIFEST-CONTRAST-01`, `MINT-GENERALIZE-01`, the
  splitwise_decode_v1 gated contrast claim

Adopted design: mint `joulewise.analysis_manifest.v3` in a NEW module with a
schema dispatcher in the manifest load path; the v1 validator and every
Slice-2M constant stay byte-untouched (frozen-corpus doctrine), v2 stays the
AP-SPEC sibling. Rejected: amending v1 (violates frozen corpora); a parallel
contrast document type (duplicates identity/replacement/floor/claim plumbing
and weakens the single consumption boundary).

v3 freezes: `comparative_contrast` / `null_alias false` / n=10 / orientation
`condition_b_minus_condition_a`; plan SHA + both stage-order SHAs + the
authenticated PASSED verdict basis `1e08e8ef…d147`; a governed derivation
rule mapping `swdec-contrast-bNN-{a1,b1,b2,a2}` to blocks with exact cover
and contiguous NN; two arm records carrying ratified family hash + realized
stack identity admitting the real MLX `{kind:"file_set", folded_sha256}`
shape (the STACK-ID-BIND-01 lesson); estimator
`abba_block_arm_mean_difference_t_v1` (Di = (B1+B2)/2 − (A1+A2)/2, paired-t
machinery, conservative deterministic-bound averaging, never inferred ABBA
cancellation); Holm α=.05 m=1; two-sided with `hypothesized_direction:
positive` — a significant NEGATIVE result must not satisfy the registered
claim; equivalence/mde null (not pre-registered).

Floor gating: NEW named claim-level rule `cross_stack_armwise_max.v1` —
resolve each arm's floor independently on its exact stack (each cell already
max(abs, comparative) per D-084), claim clears BOTH arm gates, i.e.
max(F_A, F_B), never the sum; claim-side anchor bounds stay separately
consumed with D-078 cl.11 disclosure. **Consequence on the record:** mint #1
alone cannot authorize arm A (its cells are df-ph-* families, not
sw-decode-*), so the claim needs ONE new multi-cell floor artifact with
independently stack-scoped 1.5B and 7B cells and the sw-decode-* families
predeclared; mint #1 stays byte-identical. That mint is D-088-blocked until
the gauntlet lands (7B corpus is duplicate-bearing).

**The honest dependency chain, ratified:** COOLDOWN-JOIN-GAUNTLET (D-094
commits) → v3 consumer → generalized multi-cell mint → arm floor bindings →
analyze_claims. The D-093 raw-vs-validated scan hooks at the ONE
supersession reader boundary, scans the contrast root and every declared
floor-evidence root before estimation, records {raw_count, validated_count}
in the claim artifact, and refuses on divergence. Physical roots bind by
authenticated basis, never by directory label.

Write surface (for the future implementation order): new
analysis_manifest_v3 module; analysis_engine inputs/__init__/claims/
artifact; cli; the splitwise manifest generator + generated manifest; four
test files. Rough size 1.8-2.6k lines. Delta-audit checklist recorded in
the consult memo (v1 byte-identity, position single-consumption, refusal
edges, folded_sha256 parity, m=1 mechanics, negative-direction refusal,
armwise-max never sum, cl.11 survival, D-093 refusal precedence).

Revisit when: the gauntlet lands (implementation may then be ordered), or
any element above fails ratification review at the implementation delta
audit.

## D-096: Metrology v1 plan vocabulary ratified; four window-A plans FROZEN

- Date: 2026-07-31
- Status: accepted (magistrate ratification pass over the five campaign
  READMEs' OPEN QUESTIONS + review findings F1-F3 of PR #90)
- Applies to: `configs/campaigns/metrology_v1/**`

Ratified as selected: `use_role: staleness_sentinel` for every metrology
cell (characterization cells gate no claim; the semantically-wrong
alternatives were correctly refused); the modular family-id template and
cross-campaign byte-identical shared families; additivity's `df_ph_decode`
workload retention (family byte-identity outranks a campaign-specific
name — the modularity-directed fallback), its three-metric `df-condition=`
tagging and request-family-as-primary-workload as DESCRIPTIVE vocabulary
(a future manifest consumer must re-ratify before consuming); micro_delta's
validator-forced `A_equals_B` alias literals on A≠B contrast families as a
RECORDED fallback (any future family-only consumer must be checked against
it — review F3); the plan-only field shapes `condition_families` arrays,
`output_tokens_by_k`, and long_holds' `idle_seconds_by_condition_family` +
`mt_idle_extended` (review F1 — any future plan validator is written
against these ratified shapes, and their ratification happens HERE, before
any consumer exists); `minimum_claim_n: 1` on the one-member idle
characterization cells.

Standing condition (review F2): before the micro_delta k0064 placeholder
is replaced from the fitted ramp slope, `generate_configs.py --k` handling
must be hardened to canonicalize order and remove-or-refuse stale k
outputs; replacement without that hardening is out of contract.

FREEZE: linearity_ramp, null_ladder, additivity_shapes, and long_holds
flip `freeze_status` to `frozen_before_measurement` this date (regenerated
deterministically; plan SHAs re-pinned in the sidecars and member tags; no
member of any of these plans has ever been measured). micro_delta stays
`draft_pending_slope` by design. Tonight's metrology window A therefore
needs only §5A + launch; its stage list is the suite README's window-A
packing (ramp + additivity + null o0512 + holds Part A).

Revisit when: a plan validator or manifest consumer is introduced (must be
written against the shapes ratified here), or the F2 hardening lands.

## D-097: B1 cold-gate synthesis — v2 outcome consumption DEFERRED to commit 3; interim v2/outcome refusal everywhere

- Date: 2026-07-31
- Status: accepted (mandatory rule-11 cold gate after B1's second consecutive
  failed formulation; cold Fable instance + Opus contract-lens refuter
  CONVERGED on deferral; magistrate synthesis adopts the refuter's stricter
  variant)
- Applies to: `impl/cooldown-gauntlet`, D-094's commit-3 contract

Trigger: B1 (outcome-enum consumption discrimination) failed two
formulations — commit-2 trusted a closed outcome on any existing row; the
fix round discriminated v2 by self-asserted `schema_version`, and the
re-audit demonstrated a one-file relabel of a real 7B v1 manifest bypassing
the mandatory legacy log binding while still resolving 57/57. Per the
standing trigger the next spend was this gate, not a third round.

Ruling (unanimous across both instances): **no third in-manifest
formulation exists** — with no writer emitting the enum, every in-manifest
marker is self-asserted; authenticated discrimination requires
writer-minted evidence and therefore belongs to commit 3, which must land
writer emission, a writer-external authenticated discriminator (e.g. a
writer-emitted campaign-log attestation binding manifest identity to a
content hash, structurally parallel to the v1 log binding), reader
re-acceptance, and the v2 truth-table row as ONE composed, audited change,
with the relabel probe as a permanent regression.

Adopted interim state (the refuter's O3 variant — strictly fail-closed):
strike commit-2's v2 outcome-consumption clauses AND remove v2 from the
join's accepted schema set, so a v2-labelled manifest refuses at the
catalog gate and an `outcome` field on ANY member refuses — the reader's
accepted set exactly equals the writer's emitted set (v1 only). Grounds:
no legitimate writer can produce either today (verified: run_campaign.py
emits only v1; its own resume/policy scanners skip non-v1; zero v2
manifests across all 29 corpora), so presence is uniform malformation.

Merge-train release conditions (cold instance, binding): (1) the deferral
commit lands on the branch; (2) a regression proves the relabel probe
REFUSES; (3) fresh delta re-audit passes and the full suite is green at
the new head, lead-verified; (4) both real-corpus mappings hash-identical
(57/57, 47/47). B2/B3/DA-1 remain independently verified closed.

Commit-3 riders, on the record (refuter findings): (i) the legacy binding
currently authenticates but DISCARDS the classified status — a v1 existing
row bound to a failed/incomplete log row is representative-equivalent to
usable; D-094's refusal text survives, but commit 3 must decide whether
classification beyond authentication is consumed; (ii) the v1 log binding
is anti-MALFORMATION, not anti-tamper — coordinated manifest+log rewrite
defeats it; the tamper layer is source-manifest hashing in the verdict
path, and claims about B1 severity are recorded on malformation grounds.

Revisit when: commit 3 is designed (its consult must consume this entry),
or any release condition fails.

## D-098: Metrology window A record — salvage close, recorded-deviation post-cal, verdict FAILED as-issued

- Date: 2026-08-01
- Status: accepted (magistrate-recorded 2026-08-01)
- Applies to: `runs_window_metrologyA_20260731` (+ its `_bound` root), MET-VERDICT-ADJ-01

Window `window_metrologyA_20260731` (2026-07-31 night) collected and
banked: NEG-8 bound corpus 12/12 + minted bound, start triplet 3/3,
**linearity_ramp 40/40 complete** (claim C1's campaign), midpoint,
additivity 21/24 at final state, end triplet 3/3. Three §10-handled
member failures with cause named each time; the third closed the window
as salvage per the ratified rule. Post-cal attempt 1 failed (preserved
`20260731T214355-126fc2ab`); ONE settled retry ran under the
a10-precedent RECORDED DEVIATION and is valid
(`20260731T215120-fa1e9cda`). Supersessions recorded once each
(claim root `mtadd-p0512o0512-r06`; bound root `neg8-refcorpus-r05`)
before the verdict.

Rulings recorded:

1. **The whole-window verdict FAILED and stands as issued** (row
   appended 2026-08-01T07:52Z): `whole_window_bundle_invalid` +
   `environment_admission_failed` on the quarantined-never-replaced
   `mtadd-p0512o0512-r08` occurrence, and
   `instrument_calibration_bracket_missing` with the bracket selector
   returning pre AND post null — it refused the deviation-retry
   post-cal rather than consuming it, so the §8 budgetable case was
   never evaluated. `neg8_bracket` passed; adapter continuity stable.
   No hand-application of §8 to the preserved calibrations is
   permitted; the machinery questions route EXCLUSIVELY through
   MET-VERDICT-ADJ-01 (independent audit → magistrate ruling → cold
   gate for any proposed override).
2. **Two checkpoint corrections on the record:** final-state additivity
   was **21/24**, not the 23/24 an earlier checkpoint carried; the
   window's power identity is a **140 W Anker PD** charger
   (instrument-visible "pd charger"/140.0) — the prior "Apple" label
   was cosmetic.
3. The corpus is banked, intact, and non-claim-bearing until
   MET-VERDICT-ADJ-01 rules; nothing in this entry invalidates the
   bundles. [Ruled 2026-08-01 → D-100: window A is PERMANENTLY denied a
   re-evaluation license (immutable T1-incompatible retry); the corpus
   stays design-input/diagnostic only.]

Close-out: `~/JouleWise-window-custody/window_metrologyA_20260731/close-out.md`.
Revisit when: DISCHARGED 2026-08-01 by D-100 — (a) ruled as contract
gap (repair `MET-DANGLER-DISPOSITION-01`), (b) ruled machinery defect
with correct retry rejection (repair `CAL-BRACKET-D079-01`).

## D-099: Metrology window B record — bird-SIGSTOP protocol, knife-edge anchor finding, streaming hazard; verdict FAILED as-issued

- Date: 2026-08-01
- Status: accepted (magistrate-recorded 2026-08-01)
- Applies to: `runs_window_metrologyB_20260801` (+ its `_bound` root), window operation doctrine, MET-VERDICT-ADJ-01, MET-WINDOW-C-01

Window `window_metrologyB_20260801` (2026-07-31→08-01 overnight) ran in
three launches and salvage-closed at the third member failure,
collecting: bound corpus 12/12 + in-window bound mint, references 7/7,
**null_o0128 + null_o0512 complete** (claim C2, 2 of 3 rungs),
**additivity 23/24 single-root** (C4), calibration bracket clean
(2.25 ms drift vs the 10 ms policy screen, pre+post single-attempt).
Banked to iCloud 72+13 bundles, backup rc=0. One supersession recorded
pre-verdict (`mtnull-o0512-b04-b2`, entry `3896c5ed…`). Remainder
(null_o2048, long_holds, additivity p2048o0128-r08) → MET-WINDOW-C-01.

Rulings and doctrine recorded:

1. **The whole-window verdict FAILED and stands as issued** (row
   appended 2026-08-01T14:19Z), on a DIFFERENT machinery shape than
   window A: `source_campaign_manifests` resolved EMPTY over the
   four-chain-segment window (populated `campaign_manifests/` dir; the
   supersession recorder had consumed it an hour earlier), the recorded
   supersession was not consumed, the dangling r08 was NOT excluded,
   and NEG-8 evaluated missing/reference-invalid/stale against the
   bound minted in-window. All routed to MET-VERDICT-ADJ-01 question
   group (c); no reinterpretation outside that path.
2. **Clock-anchor knife-edge is an accepted instrument-design finding**
   (bounded Sol xhigh consult, 2026-08-01, escalation-trigger-mandated
   after two same-signature §5B pre-cal aborts): at 197 s capture
   length the native-second intersection margins are ~±1 ms and the
   unmodeled controller wall/monotonic rate (~−12 ppm ≈ 2.3 ms per
   capture) exceeds every margin — pass/fail is quantization-phase
   luck. The consult refuted the lead's cadence-drift mechanism.
   Rate-aware anchor design is a queued desk/paper item; the finding is
   publishable as a metrology limitation.
3. **TM attribution is retired as a false proxy:** `tmutil
   destinationinfo` shows no destinations configured; the prep script's
   "TM RUNNING" line detects only process residency. Window A's
   failure-#3 "TM-consistent" label is tainted. The observed overnight
   intruder class is mobileassetd/softwareupdated (~04:29 PT both
   nights) and bird.
4. **bird-SIGSTOP is once-validated practice:** identity custody
   (pid + lstart), double-verified state T, fail-safe CONT trap on all
   exit paths, post-window identity check, cloudd/fileproviderd
   launcher holds; pre-cal passed first-attempt under it after failing
   twice with bird active.
5. **Operator output streaming during idle gates is a measurement
   hazard (binding doctrine):** window B failure #3 was caused by the
   operating session's own post-arm status streaming (claude 12–18%
   CPU + Terminal rendering) during a member's idle gate. Zero tool
   calls is INSUFFICIENT; after arming a launcher the session's message
   must be ONE LINE, and zero streaming during idle-gate exposure binds
   all window operation (encoded as a MET-WINDOW-C-01 fence).

Close-out: `~/JouleWise-window-custody/window_metrologyB_20260801/close-out.md`.
Report: `docs/run_reports/2026-08-01-metrology-window-b.md`.
Revisit when: the rate-aware anchor design lands. [The (c) branch was
DISCHARGED 2026-08-01 by D-100: pure cascade, machinery ruled CORRECT
for window B.]

## D-100: Salvage-dangler terminal semantic — cold-gate synthesis (S2-A as redrawn, landed in the S3 semantics-dispatch shape)

**2026-08-07 supersession note:** The Window-B clause later superseded by
D-113 is retained unchanged as historical context. Current rule ownership:
D-113.

- Date: 2026-08-01
- Status: accepted (rule-11 mandatory cold gate: cold Fable instance ruling
  + one bounded factual follow-up + independent Opus contract-lens
  refutation; magistrate synthesis. This entry is the Ed-visible written
  record required by the topology.)
- Applies to: whole-window verdict machinery (`scripts/run_campaign.py`
  membership/disposition paths), §10 contract amendment, windows
  `runs_window_metrologyA_20260731` / `runs_window_metrologyB_20260801`,
  MET-VERDICT-ADJ-01, MET-WINDOW-C-01 scope

Question ruled: the terminal whole-window semantic for a §10-quarantined
member occurrence with zero surviving bundles in a D-087 salvage-closed
window (packet:
`docs/process_traces/2026-08-03-d111-backfill/adjudication_packet_20260801/`, retained with the
audit, both rulings, and the refutation as the session record).

**1. Unanimous machinery repairs (both instances converged; land as one
audited repair commit with the regressions below):**
- Uniform count-independent dangler path: the accidental count-one
  (silent accept, late strict invalidation) and count-two (duplicate-path
  group discard) behaviors are both retired; presence check added to the
  single-declaration branch.
- A failing sibling group must NEVER discard an unrelated valid
  supersession (window B's destroyed `mtnull-o0512-b04-b2` record is the
  defect exemplar).
- Membership groups must bind by explicit identity: all eight window B
  manifests carry `analysis_manifest_id: null` and collapse into one
  synthetic group (refuter R11); the repair adds an identity-binding
  requirement or a recorded explicit safety finding at the verdict row.
- Ledger honesty (refuter R12): rows recording `strict_valid: true` /
  `clean` for a bundle with no bytes are repaired so exclusion evidence
  derives from bundle bytes, never from those flags.

**2. Disposition semantic adopted: the cold instance's S2-A with its
redrawn condition (b), carried in the refuter's S3 shape.**
- Fail-closed default everywhere the license fails, including every
  non-salvage window.
- Salvage-dangler exclusion license, ALL mechanical: (a) recorded D-087
  closure binding the attempts; (b-i) launcher-layer refusal with zero
  bundle bytes, OR (b-ii) pre-workload admission abort — no
  `stage_started` for any workload/measurement stage (success vocabulary:
  warmup, measured_run, idle_drift_sentinel; danglers terminate at
  idle_baseline), `environment_admission.admitted == false`, summary
  failed with zero measurand fields, telemetry bounded to the admission
  phase (per R5a the implemented test accepts the real bundle shape,
  including the ~150 ms instrument-teardown trace flush past the failure
  event; unclassifiable evidence voids); (c) exhaustive per-attempt
  evidence; (d) cap of ONE dangling member per window; (e) verdict-row
  exclusion payload with per-attempt quarantine path, config/metadata/
  summary sha256, terminal stage, failure reason, license branch, and
  operator deviations flagged.
- **Landing shape (refuter R5/R6, adopted over the cold instance's
  bespoke supersession block):** any licensed re-evaluation appends a NEW
  row under a NEW `consumption_semantics_id`
  (`salvage_dangler_exclusion_v1`) with a genuinely new
  `evaluation_basis.sha256`; consumers reach it only by explicitly
  requesting those semantics with a pinned basis. The original FAILED
  rows are never edited and continue to govern default consumption —
  verdicts stand as issued BY CONSTRUCTION, and no
  `whole_window_verdict_conflict` can arise.
- **Registry amendment explicit (refuter R9):** the new spellings are the
  first registered conditions that do not refuse; the D-078 registry's
  governing sentence is amended by this entry to admit
  semantics-dispatch-scoped non-refusing dispositions, which remain
  unreachable outside an explicit semantics request.

**3. Factual record corrected (both directions):**
- Packet fact 6 wording corrected: the danglers' attempts DID create
  quarantined idle-phase bundles; the MEASURAND was never observed (event
  sequences terminate at idle_baseline; durations explained by two ~36 s
  admission-baseline attempts, refuting the refuter's R2 workload
  inference from primary evidence).
- Refuter R1 confirmed for the three `p2048-o0128` cells (frozen
  `minimum_claim_n: 8`, r08 named, 7 present — barred regardless of this
  ruling; that shape re-collects in window C) and corrected in scope: the
  other six additivity cells (two complete shapes) and both null rungs
  remain the real, non-illusory stake of the license.
**4. Prospectivity decided explicitly (refuter dissent 3):** D-078's
prospectivity doctrine binds stored summaries and numeric semantics —
none of which are rewritten here; adjudicated verdict re-evaluation
through this cold-gate path, on a new basis under explicit semantics
dispatch, is the ratified override channel (CLAIMS_STATUS §4 cl.3).

**5. Window B re-evaluation license:** reinstated under the redrawn (b),
subject to ALL cold-ruling conditions with condition 6 replaced by the
S3 landing shape: contract amendment landed; repair landed with
regressions R1-R8 + R5a/R5b + identity-binding and ledger-honesty
regressions; independent read-only audit at the exact head; recorded
(b-ii) bench verification of both r08 bundles (performed 2026-08-01,
recorded in the packet: no workload stage, admitted false, zero measurand
fields, both attempts); D-093 cl.4 raw-vs-validated scan on B's corpus;
frozen byte-identical corpus; deviation-escape (any condition outside the
audited cascade set returns to a cold gate). [Superseding note,
2026-08-02: D-106 clause 3 HARD-BLOCKS this license on
D100-BII-BINDING-01 and requires the (b-ii) verification RE-RECORDED
with the repaired tool plus per-file digests — the 2026-08-01 manual
bench verification no longer satisfies it.] **Window A: no license** —
its FAILED verdict rests on the immutable T1-incompatible retry.

**6. Dissents recorded (Ed sees this entry):** the refuter preferred the
`flagged`-status S4 landing, contingent on its R2 workload inference,
which primary evidence refuted; its R10 preference for a
named-and-removed-cause license axis over flag-not-void operator
deviations is NOT adopted for the license (exclusion never improves a
measured value and the per-cell gates bar the affected cells) but its
standard is adopted for the surviving RE-COLLECTION duty (runbook
:796-799): the re-collected slot launches only after the named cause is
removed — for window B's r08 that includes the operator-streaming
doctrine (D-099 cl.5). S1 is rejected on the refuter's R3/R4/R13 grounds
(it would ratify a permanently false custody condition over a corpus
whose provenance is present, complete, and bound).

Revisit when: the repair commit's delta audit reports, any license
condition fails, the R5a real-shape regression conflicts with any prose
clause (regression wins; prose amends), or the cold instance's named
falsifier (admission-gate sensitivity blind spot correlated with the
dangler's intruder class) gains evidence.

## D-101: The site gates nothing — publication chain fully decoupled from CI pass/fail and session doctrine

**2026-08-07 supersession note:** The clauses later superseded by D-101
addendum II are retained unchanged as historical context. Current rule
ownership: D-101 addendum II.

- Date: 2026-08-01
- Status: accepted (Ed-directed 2026-08-01, verbatim intent: "stop gating
  anything on the website being up to date … keep whatever docs it needs
  live but stop worrying about liveness of the site … the site should be
  separate completely even though it's based on the project I want it
  gating nothing")
- Applies to: `.github/workflows/ci.yml` (release-chain job),
  `scripts/build_site.py` / `scripts/pack_capsule.py` consumers,
  RUN_STATE end-of-work step 8, DRIFT.md cadence

1. The CI `release-chain` job (publication tools, capsule decoder check,
   `release_check.py` site build + pack) is **advisory**:
   `continue-on-error: true`. It still runs and its logs still inform;
   it can never fail CI. The `test`, `build`, and `installed-wheel` jobs
   remain the gates, and they already cover code correctness for the
   site modules.
2. The site's SOURCE docs (README, PROJECT_STATUS, CLAIMS_STATUS,
   decision/council logs, run reports, queue/state files) remain live,
   first-class, and session-maintained — the decoupling is of the
   rendered/packaged site, not of the documentation.
3. `docs/site/DRIFT.md` becomes optional/informative: refreshing it is
   no longer a mandated close-out step (amends RUN_STATE end-of-work
   step 8; D-068's no-agent-deploy rule is unchanged and Ed still
   deploys manually whenever he chooses).
4. Shard-budget or capsule-size failures are site-lane facts, never
   session blockers; nobody trims or reshapes governed project records
   to fit site budgets. (Today's roadmap rendering change stands on its
   own merits as a de-duplication, not as a compliance obligation.)

Revisit when: Ed changes the site's standing, or the site gains an
external consumer whose freshness matters.

## D-100 addendum (2026-08-01): four mechanical spellings ratified for the repair; reader fail-open folds in

- Status: accepted (magistrate ratification of the repair design consult's
  four lead-owned spellings; each implements D-100's ruling under its R5a
  real-shape-primacy clause — no disposition or landing-shape change)

1. **R5a admission predicate:** license check (b-ii) reads
   `metadata.environment_admission.decision == "abort"` with a nonempty
   ordered attempt list, every `attempts[*].admitted == false`, and
   `claim_reason == "environment_admission_failed"` — the real bundle
   bytes' shape; D-100's prose `admitted: false` was a summary of exactly
   this.
2. **Teardown bound:** a final powermetrics trace flush ending no later
   than **0.250 s** after the idle-baseline failure event is teardown
   evidence, never workload evidence (real flushes measured 136–171 ms;
   anything later voids).
3. **D-087 closure artifact:** `joulewise.salvage_closure.v1` binds the
   policy, membership-binding digest, the three failure occurrences with
   a BYTE-DERIVED shared failure signature (never narrative root-cause
   identity), the terminal occurrence, timestamps, evidence paths, and
   operator deviations. Window A/B closure artifacts are authored from
   custody evidence and lead-verified before any re-evaluation.
4. **Custody-root universe for (b-i):** the closed set is the window's
   runs root plus every quarantine/custody root declared by that
   window's closure artifact (for windows A/B: the runs root and
   `~/JouleWise-window-custody/<window>/quarantine`). "Zero bytes
   anywhere" is evaluated over exactly that declared universe.

Also ratified from the same consult: **MEMBERSHIP-READER-FAILOPEN-01
FOLDS INTO the repair commit** (shared surface; the occurrence-resolver
rewrite would otherwise leave R2's supersession path knowingly
fail-open), retiring the separate queue row when the repair lands; and
the salvage semantic is defined as the COMPOUND
`salvage_dangler_exclusion_v1` = authenticated max-bracket survivor
consumption + exactly one D-100 exclusion (one scalar id never carries
two orthogonal meanings). Window B's re-evaluation stays OUTSIDE the
repair commit, behind the exact-head audit [and, since 2026-08-02,
behind D100-BII-BINDING-01 per D-106 clause 3].

## D-102: CAL-BRACKET-D079-01 pins ratified — corpus-derived budget cap, identity-epoch freshness, never-zero allowance, decimal numeric semantics

- Date: 2026-08-01
- Status: accepted (magistrate ratification after the two-round Sol xhigh
  design consult + the independent n=19 corpus reconstruction; ALL
  arithmetic lead-replayed at the bench: ceiling, cap, t(0.995,18)
  quantile by numerical CDF, window B pre-cal value against primary
  evidence bytes)
- Applies to: CAL-BRACKET-D079-01, the future
  `configs/calibration/calibration_acceptance_d079_v2.json` artifact

The four pins D-079 left unexecutable, now pinned:

1. **Budget cap (Candidate A, 99% two-draw prediction family, derived
   blind from the pre-window-B n=19 corpus):**
   `max_budgetable_excess_s = 0.001275166090593858`;
   `maximum_budgetable_drift_s = 0.012093166090593858`
   (= t(0.995,18)=2.878440472713585 × sd 0.002970761365307205 × √2;
   cap = ceiling − operative screen 0.010818). Consequences verified: a
   ~11.58 ms drift branch is budgetable; a 15 ms bracket refuses.
   **Window B itself remains refused regardless** — its pre-calibration
   0.035435840879704805 s (verified in primary evidence) exceeds the
   pre-flight level screen, and D-079 cl.2's systematic failure is
   never budgetable. The CAL-BRACKET regression at ~11 ms models the
   DRIFT BRANCH only, never a whole-window B pass.
2. **Freshness = exact identity epoch, no calendar hard expiry:** the
   artifact binds {os_build, hardware_model, power_policy,
   sampling_interval_ms, estimator_revision, pulse_protocol_id}; any
   change → `calibration_acceptance_bound_stale`. Mandatory prospective
   re-derivation triggers: any identity-field change; protocol/estimator
   byte change; a new valid same-identity calibration expanding the
   observed range; corpus doubling (19→38); a new systematic failure
   challenging the pre-flight screen. A trigger observation is judged
   under the PRIOR artifact — never incorporated into a threshold that
   judges itself. Calendar-age fields are provenance/advisory only (the
   corpus spans four days; a calendar constant would be invented).
3. **Never-zero allowance confirmed:**
   `A_s = max(observed_drift_s, 0.010818)`;
   `B_operative = max(B_pre, B_post) + A_s`, embedded ONCE in the
   authenticated operative fiducial bound (anchor-envelope
   re-reduction); no second calibration-drift energy term anywhere
   downstream (D-078 cl.11 single-count).
4. **Decimal numeric semantics:** the artifact stores source decimal
   lexemes and exact-decimal derivations (range
   0.010817749309353528 s; 95% prediction 0.008826584887500717 s;
   pre-flight exact max 0.03355875667989999 s) SEPARATELY from the
   ratified operative comparators (0.010818; 0.033558756679900;
   ROUND_HALF_EVEN at the declared quantum), hashing the decimal
   strings + rounding rule into the derivation sha256. D-079's
   12-place `0.010817749309` is a LABELLED presentation value, never a
   comparator. Acceptance comparisons run in decimal semantics;
   binary64 conversion happens only at the reducer boundary and is
   recorded.

Corpus provenance: the n=19 member list with per-member manifest and
evidence sha256s is reconstructed and lead-spot-verified (2026-08-01
session records; summary in the session custody dir) — the artifact
copies those tables verbatim with re-verification at authoring, never
retyped. Implementation remains sequenced behind gauntlet commit 3 and
the D-100 repair (shared write surfaces).

Revisit when: CAL-BRACKET-D079-01's delta audit reports, or any
re-derivation trigger fires.

## D-103: C3 structural cold-gate synthesis — WAL attestation ordering, two named aggregation policies (cold instance overruled on B2 with recorded dissent), reader-tolerant/writer-strict path discipline

- Date: 2026-08-01
- Status: accepted (rule-11 cold gate on the C3 escalation trigger: cold
  Fable structural ruling + independent Opus contract refutation;
  magistrate synthesis with ALL load-bearing claims bench-verified —
  the unreachable heal, the pointwise byte-pinned verdict path, the
  design's contradictory acceptance clauses, the reconstruction-based
  grammar hole. THIS ENTRY CARRIES A WRITTEN OVERRULING of the cold
  instance's B2 order, which Ed sees here.)
- Applies to: impl/cooldown-gauntlet-c3 (fix round 2), D-097 (three
  riders), COOLDOWN-JOIN-GAUNTLET-01

**Root cause (layered, all in the DESIGN, not the implementation):**
(a) C3-DESIGN §2's "hash and attest AFTER atomic replacement" ordering
guarantees the crash window — no downstream formulation could close it
(cold instance; bench-verified: session-and-pid-unique manifest paths
make any same-path heal unreachable after a real restart);
(b) the design's §3 acceptance text is self-contradictory (union
invariant vs refuse-the-entire-catalog-including-siblings — both
clauses verified in the text), so B2's two "failed formulations" were
implementations of the two contradictory clauses;
(c) the design's WRITE_SCOPE forbade whole_window.py while its
call-site list omitted the verdict verifier, so round 1's B2 "failure"
was scope compliance (refuter §4.3 — the trigger count for B2 is
corrected on the record; the trigger's firing remains valid via B1/B3).
Per-snapshot attestation is NOT ruled structurally unsound; the
refuter's per-session ORIGIN-binding redesign is recorded as the
REGISTERED FALLBACK — one further same-signature failure of this
mechanism goes to a new cold gate with origin binding as the default
candidate, not to a round 4.

**1. B1 (D-097 rider i-bis, the WAL ordering):** write tmp → fsync →
attest the exact tmp bytes → THEN os.replace. A crash now leaves a
dangling attestation row (authenticates nothing, tolerated by design)
instead of a published-unattested manifest (which latches the ENTIRE
runs_root — including all future campaigns — into global refusal; the
refuter's blast-radius finding is accepted and both prior audits
understated it). Both helper branches attest the same in-process bytes
(resolves the TOCTOU inconsistency). Append discipline: mandatory
campaign.lock enforced mechanically + single O_APPEND row write +
check-before-append idempotence (which also closes the latent
duplicate-current A→B→A brick for the locked writer — refuter §3(b)).
**Torn-tail tolerance:** load_campaign_log_rows tolerates exactly ONE
torn FINAL line as a recognized crash artifact (ignoring that row
alone); any earlier malformation still refuses globally — this cures
the second unhealable brick and its regression of v1-only histories
(the refuter's severity correction of the re-audit is accepted).
Strand-then-refuse remains the correct baseline; cross-session repair
is an EXPLICIT operator command under the lock, healing only
lineage-proven strands (>=1 shape-valid attestation, same
path+session_id, zero current) and REFUSING lineage-less files
(relabel-indistinguishable). Reader-side healing and blind sweeps are
rejected unanimously — a campaign-start sweep would void D-097's
relabel ruling outright.

**2. B2 (D-097 rider iii — the OVERRULING):** the cold instance
ordered the verdict path onto the global catalog with the per-manifest
loader deleted. **The magistrate overrules.** Grounds, bench-verified:
the verdict verifier is a pointwise dereference of PINNED descriptors —
each sha256 rechecked against the authenticated raw bytes, policy sha
matched, membership itself pinned; no code path in it enumerates
campaign_manifests/ — so a poisoned sibling cannot enter, alter
coverage, or alter re-derivation there. Forcing catalog consumption
would multiply the B1 latch into issued verdicts, hand a
denial-of-verdict primitive to anything that can drop a file in the
directory, and violate the union invariant. The cold instance's own
recorded counterargument (availability hostage to directory hygiene)
corroborates. RATIFIED CONTRACT: **one authentication predicate, two
named aggregation policies** — pointwise-dereference (pinned-descriptor
verification; the per-manifest loader is RETAINED as this policy's
entry point, documented and fenced by a regression that no enumerative
consumer imports it) and all-or-nothing enumeration (all six catalog
consumers, unchanged). The design's §3 invariant is amended to name
both policies explicitly. The fix-round-1 poisoned-sibling regression
INVERTS: a verdict row referencing attested manifest A PASSES beside an
unattested sibling; every enumerative consumer still refuses globally.

**3. B3 (D-097 rider iv — writer-strict, reader-tolerant):** the
reader's MALFORMED class narrows to the minimal decidable predicate
(exact "campaign_manifests/" prefix; single-segment, non-empty basename;
".json" suffix; basename != ".json"; no "/" in basename). Backslash is
REMOVED from the malformed set (legal APFS basename character — the
current false-malformed classification is the brick direction; the
refuter's finding is accepted). Recognizable rows that pass the
predicate but match no manifest are STALE — pinned deliberately by
regression (NUL and newline rows are inert-by-construction: exact-match
against a reconstruction cannot alias, POSIX forbids NUL filenames).
The WRITER applies the cold instance's anchored strict grammar
(fullmatch [A-Za-z0-9][A-Za-z0-9._-]{0,250}\.json) at mint time and
raises on its own violation — strict emission, tolerant-but-decidable
classification, both ends inside the one shared module.

**4. Regression set for fix round 2 (defect-pinning, union of both
instances):** B1 fault injection at each ordering point + NEW-SESSION
end-to-end (catalog never poisoned; synthetic legacy strand refuses,
is not healed by new-session writes, heals via the operator command
with lineage, refuses without — relabel probe); append idempotence
under concurrent equality-branch calls; torn-FINAL-line tolerated /
mid-file malformation refused / v1-only history with torn tail still
loads; A→B→A content revisit does not brick; B2 poisoned-sibling pair
(dereference passes, enumeration refuses) + no-enumerative-import pin;
B3 classification table (predicate failures => malformed; NUL, newline,
unicode, leading-dot => stale; backslash no longer malformed) + writer
mint-grammar positive control + writer-raise probe. Performance:
re-stated as a measured nit (largest real corpus 1.78 MB / 14
manifests); the one-parse-per-verification counter lands only if
trivial. The broad-OSError nit in the equality branch is folded in.

**5. Fix-round-2 WRITE_SCOPE (restated lease, exhaustive):**
scripts/run_campaign.py, joulewise/campaign_provenance.py,
tests/test_run_campaign.py, tests/test_analysis_integration.py,
tests/test_whole_window.py, and joulewise/whole_window.py
(docstring/comment alignment only — its production dereference logic
is now contract-correct as committed). Fresh delta re-audit on a NEW
thread afterward (independence rule).

Revisit when: fix round 2's delta re-audit reports (any same-signature
failure => the registered origin-binding fallback goes to a new cold
gate), or any rider text conflicts with observed writer behavior.

## D-104: C3 residuals cold-gate synthesis — acquisition-identity lock tokens, positive writer-grammar tail recognizer (convergent gate; both magistrate candidates rejected)

**2026-08-07 supersession note:** The clauses later superseded by D-105 are
retained unchanged as historical context. Current rule ownership: D-105.

- Date: 2026-08-02
- Status: accepted (second rule-11 cold gate on gauntlet commit 3: cold
  Fable ruling + independent Opus refutation CONVERGED on rejecting both
  magistrate candidate formulations and on their replacements; magistrate
  synthesis merges the two near-identical prescriptions. Both instances
  probed CPython's json taxonomy independently rather than trusting the
  packet.)
- Applies to: impl/cooldown-gauntlet-c3 fix round 4, D-103 §1

1. **Lock token (Defect 1) — BLOCKER stands (refuter's should-fix
   dissent recorded; operationally identical since both mandated
   in-commit remediation).** Formulation, merged: ownership is
   established at acquisition and verified by identity — a process-local
   registry keyed by the resolved lock path records (st_dev, st_ino)
   from the O_EXCL fd, the resolved runs_dir, and a random NONCE written
   into the lock content; the assert requires registry presence + stat
   identity + nonce match + path == root/campaign.lock + the retained
   basename/pid checks; append target binding: the log's resolved parent
   equals the registered root, OR an external log is legal iff its
   directory contains NO campaign.lock. The magistrate's log_path.parent
   candidate was REJECTED — it breaks the supported --log configuration
   at four derivation sites and leaves PID-reuse open. Registered
   residual queued, not folded: two roots sharing one external --log
   remain mutually unserialized (pre-existing). SF1 (pre-loop lock
   stranding) is ruled JOINTLY as the stale-lock generator: guard
   try/finally begins immediately after acquisition; unlink sites
   idempotent beyond FileNotFoundError.
2. **Torn-tail (Defect 2) — REPLACED with the positive writer-grammar
   recognizer; error-message-class discrimination is RULED OUT** (both
   instances verified it unsound in both directions and
   version-unstable; it would have been the third negative-check
   formulation). Case (ii) preserve+LF-complete iff ASCII AND dict AND
   byte-exact canonical round-trip (dumps(loads(S), sort_keys=True)
   == S) — this also closes the refuter's NEWLY DISCOVERED preservation
   hole ('{"a":1} ' — json.loads tolerates trailing whitespace — would
   have been PERMANENTLY WRITTEN into the log; missed by rounds 2, 3,
   the round-3 re-audit, and the packet). Case (i) truncate iff a
   proper prefix of a canonical writer serialization per an explicit
   incremental recognizer of the writer's closed grammar (first byte
   "{", isascii-only — the UTF-8-prefix latitude is struck; writer
   output is pure ASCII). Everything else refuses globally; refusal
   raises BEFORE any truncation. Acceptance-set contract for the delta
   re-audit: accepted set ⊆ prefixes of canonical serializations AND
   ⊇ every prefix of every dumps(dict, sort_keys=True) output — pinned
   by the R7 property test over real writer rows (self-checking
   completeness, the answer to the cold instance's own proportionality
   counterargument). raw_decode end-check may remain as a redundant
   early refusal only.
3. **Regressions:** the cold ruling's R1-R11 (stale-pid-reuse,
   inode-recreate, cross-root append, external-log positive/negative
   controls, post-release refusal; the prefix property corpus incl.
   '{"a": 1e' and '{"a": tru'; the refusal table incl. '{"a":1} ',
   whitespace-only tail flip, and the '{"a" : 1' canonical-strictness
   pin; byte-exact preservation; refusal-touches-nothing) + the parse
   count pin as a nit-level extra.
4. **Corrections on the record:** the packet miscited the B3/NUL
   precedent (D-103 ratified NUL rows STALE; blocker status attached to
   the predicate SHAPE, not the row's fate) and understated the append
   surface (8 token origins, 12 append call sites).
5. **Origin-binding fallback: NOT routed — both instances, emphatically.**
   Scope boundary restated: the D-103 fallback triggers only on a
   same-signature failure of the per-snapshot ATTESTATION mechanism; a
   recognizer bug is not a structural trigger, but a third formulation
   failure on the tail-classification clause returns to a cold gate.

Revisit when: fix round 4's fresh delta re-audit reports.
[2026-08-02 magistrate disposition: the round-4 re-audit found two
blockers that are IMPLEMENTATION INFIDELITIES to this ruling (bare-Path
tokens aliasing across release/reacquire — the nonce was not bound into
an unforgeable token object; recognizer grammar missing canonical
key-ordering and the -0.0 float form), not formulation failures — both
counterexamples are decided correctly by the ruled formulations. The
auditor's contrary reading (F1) is recorded as dissent. Round 5 is
licensed as fidelity repair under this ruling's recognizer-bug clause,
with a BINDING commitment: any blocker in round 5's re-audit on either
mechanism, however shaped, returns to a cold gate and opens the descope
question with Ed — no further formulation-vs-implementation parsing.]

## D-105: C3 disposition synthesis — LAND with a final custody micro-commit; F1/F2 registered as a NEW ruling with refuter-amended closure; number-grammar exactness struck

- Date: 2026-08-02
- Status: accepted (third rule-11 cold gate on gauntlet commit 3: cold
  Fable ruling [Option A, fences, closure procedures] + independent
  Opus refutation [does not oppose landing; replaces the grounds and
  fences]; magistrate synthesis of the split on pre-merge scope. Ed
  sees this entry; his override outranks it.)
- Applies to: impl/cooldown-gauntlet-c3 final commit, the C3 merge,
  new row C3-RECOGNIZER-EXACT-01, D-104 cl.2 amendment

**Disposition: LAND, via one final MICRO-COMMIT on the branch, then a
narrow fresh audit of that micro-diff alone, then PR/merge.** The
micro-commit contains ONLY (~40-60 lines + tests, recognizer
classification logic UNTOUCHED): (1) preserve-then-truncate custody —
append_log copies any to-be-truncated tail bytes to a quarantine
sidecar and emits a warning BEFORE ftruncate (the refuter's central
fix: classifier errors can no longer destroy evidence, making
recognizer exactness irrelevant to custody); (2) writer-side key
assertion at the append_log serialization point (every row key must be
str and ASCII, raising otherwise) — closes the five unvalidated
on-disk-JSON splice sites, the integer-key canonicality break, AND the
F1 false-negative's entire reachability in ~2 lines; (3) F3 + the
sys.exception() hygiene fix (explicit exception passing; release-path
stat failures chain, never mask) — the refuter is right that this sits
on the SF1 path D-104 already ruled jointly; (4) R7 extended to real
writer rows from the actual corpora PLUS a non-BMP-key row (the
ratified pin was implemented over a synthetic corpus and missed F1 by
one character position — an as-ruled infidelity corrected before it
guards anything). This synthesis adopts the refuter's pre-merge
position over the cold instance's merge-head-exactly rule BECAUSE the
audited-head discipline is preserved by auditing the new head: the
micro-diff gets its own fresh narrow audit before PR. The cold
instance's registration fences otherwise stand as amended below.

**F1/F2 registration — a NEW ruling, not a D-088 application** (the
refuter's B4 is accepted: QA-10A/B were pre-existing defects; these are
branch-introduced; future sessions must not cite this as precedent for
registering anything corpus-absent). Registered as non-downgradable
blockers against D-104 cl.2 with closure ONLY through
C3-RECOGNIZER-EXACT-01, whose acceptance criteria are the REFUTER'S
amended set: (i) exact escape-ordering completion-feasibility (the
cold instance's interval + surrogate-pair procedure — cheap and real,
~40 lines); (ii) number grammar tightened to a DOCUMENTED DECIDABLE
SUPERSET of json.dumps float spellings (fixed-notation window,
coefficient rules, exponent padding), with **D-104 cl.2's ⊆ direction
AMENDED** to the honest two-sided form "accepted ⊆ prefixes of the
documented decidable superset grammar AND ⊇ every prefix of every
dumps(dict, sort_keys=True) output" — three rounds failed on the
literal ⊆ half because it demands deciding the image of CPython's
shortest-repr algorithm; the exactness demand is STRUCK (the cold
instance's own strongest-counterargument anticipated this); (iii)
independent delta audit; both registered rows close together. While
open: the accepted set may only shrink; the custody sidecar makes torn
tail preservation AUTOMATIC (supersedes the manual operator fence);
non-ASCII row keys are blocked MECHANICALLY by the assertion
(supersedes the doctrine fence).

**Evidence record:** three independent absence scans now on file with
stated predicates (cold instance: recursive Python, 40 files/1747
rows; refuter: own scanner, 40 files, plus canonicality and key-depth
checks; third: shell-bytes-only via delegated scanner, 40 files, byte
level) — all clean; the 33-count in the packet was a depth-1 glob and
is corrected. The refuter's TYPE correction is adopted on the record:
corpus scans corroborate but cannot bound a future-crash-artifact
recognizer; the sound bound is the writer grammar plus the key
assertion, which the micro-commit lands.

**Process findings (bind future gates):** cost-of-delay/runway context
MUST NOT appear in material a cold instance reads — it goes in a
sealed annex Ed sees alongside the ruling (the refuter's S3; this
packet violated it and the paired-refuter design absorbed the damage);
packet options sections state facts and verified costs only, no
adverbs of advocacy. Merge conditions: the lead-side suite + mapping
pins already on record at 5a2868b are re-run at the micro-commit head
(rule 1), CI green, D-072 gate.

Revisit when: the micro-commit's narrow audit reports, or
C3-RECOGNIZER-EXACT-01 closes.

## Repairs disposition note (2026-08-02, magistrate; D-104-precedent containment)

Both repair branches' delta re-audits each left one refined blocker
cluster: MET-DANGLER (B2: the b-i content sweep parses only three exact
filenames; B3: the b-ii allowlist is not closed over multiplicity or
allowed-file content) and MANIFEST-CONTRAST v3 (F1 refined: floor-root
exact cover validates against a mutable self-declared set rather than
the file_sha256-bound artifact's roots). ADJUDICATION ON THE RECORD:
the RULED formulations (D-100's "zero bytes anywhere" and
"unclassifiable ⇒ void"; D-095's "every declared floor-evidence root")
are intact and decide every audit scenario correctly — the misses trace
to the MAGISTRATE'S FIX-ROUND BRIEFS, which operationalized them as
filename/field enumerations. One brief-repair round each is licensed
with the corrected content-general operationalizations (b-i: byte-level
occurrence-identifier sweep over EVERY file under every custody root,
no filename enumeration; b-ii: exact file-set equality + per-file
schema validation of allowlisted content; v3: exact-cover derived from
the authenticated artifact's bound root set). BINDING COMMITMENT (the
D-104 shape): any blocker in either round's re-audit on these
mechanisms, however shaped, returns to a cold gate — no further
formulation-vs-brief-vs-implementation parsing. Auditor dissent, if
either re-auditor reads the trigger as already fired, is preserved in
their reports.

## D-106: b-ii residual synthesis — Variant D (land the inert branch, register NOTHING, window B blocked on two decidable fixes; cold instance overruled with dissent)

**2026-08-07 supersession note:** The clauses later superseded by D-107,
D-108, and D-113 are retained unchanged as historical context. Current rule
ownership: D-107, D-108, and D-113.

- Date: 2026-08-02
- Status: accepted (cold gate: cold Fable ruled Option A + window-B YES;
  Opus refuter demonstrated the fence and the YES unsound on
  bench-verified facts; magistrate synthesis ADOPTS THE REFUTER'S
  VARIANT D, overruling the cold instance a second time this runway —
  written dissent below, Ed sees this entry.)
- Applies to: impl/met-dangler-disposition merge, new row
  D100-BII-BINDING-01, window B re-evaluation gating

**Bench-verified grounds for the overruling:** (1) the Option A fence
binds by PATH against a CONTENT-substitution defect — the recorded
manual verification (winB-closure-facts.md) contains ZERO bundle
digests, so the fence's predicate survives the attack it fences;
(2) the operative runbook's condition 3 requires RE-RECORDING with the
repaired tool at execution time — the packet's parenthetical quoted the
half that supported its lean (a packet-authoring failure, the
magistrate's own, recorded); (3) the window's three sibling quarantine
bundles are mutually substitutable by a single same-name file copy — no
adversary, no coordination — so the rider-(ii) exemption does not reach
it (the rider ASSIGNS this layer the anti-malformation duty);
(4) NEW WRITER-LEVEL FACT (refuter): powermetrics emits identical
8-field telemetry rows for measured and idle captures from one code
path — telemetry rows carry NO identity BY CONSTRUCTION, so per-file
schema formulations can never bind capture identity; only interval
containment or a digest freeze can. This diagnoses both failed
formulations and discriminates a viable third fix in kind.

**Ruling (Variant D):**
1. **MERGE impl/met-dangler-disposition at 05d99b6** — both instances
   agree the branch strictly narrows a PRE-EXISTING gap and is INERT
   (salvage semantics reachable only by explicit dispatch + pinned
   basis; no non-salvage behavior change; lead suite 2396 OK unmasked
   and mapping pins hash-identical ON RECORD at this head in the
   gate-commit). An in-code marker lands with the binding fix noting
   the open row (a follow-up commit's docstring, not a branch commit —
   audited-head discipline).
2. **NOTHING is registered.** The refuter's S-1 is accepted: D-105's
   guard failed on first contact and the ratio was inverted (D-105
   registered the UNDECIDABLE; this is DECIDABLE). Structural cap
   adopted: registration is never granted for decidable closures, and
   no second registration may cite shape without independently
   satisfying D-105's F-A5-style criteria.
3. **Window B's re-evaluation is BLOCKED** on row
   **D100-BII-BINDING-01**: (a) interval containment — every telemetry
   timestamp within [run_started event, failure + 0.250 s] (the
   ~5-line decidable-superset control; the cadence-consistency clause
   is STRUCK as the recognizer-exactness trap; the concurrent-capture
   residual is RECORDED as a known limitation); (b) custody digest
   freeze — the closure artifact records sha256 of every file in each
   b-ii bundle and a root-level digest manifest of the quarantine dir,
   re-verified at license execution (digests the tool already
   computes); (c) nested-content closure per the decisive audit's
   second scenario; (d) the runbook's condition-3 re-record with the
   REPAIRED tool. These are different IN KIND from the two failed
   enumerations (the standing trigger's own requirement) and land as
   ordinary audited work — one commit + focused audit.
4. **Packet-hygiene violations recorded against the magistrate:** the
   Option C runway line repeated the D-105 S3 violation under a false
   self-certification; the condition-3 selective quotation. Packet
   authorship for cold gates moves to MECHANICAL assembly only:
   verbatim source quotes with file:line, no paraphrase of governing
   conditions.
**Dissent recorded (cold instance):** Option A with fences + window-B
YES on the compensating-control theory; its own stated
strongest-counterargument (doctrinal fences decay) is noted as
convergent with the refuter's B-1. **Refuter dissents absorbed** into
the ruling itself.

Revisit when: D100-BII-BINDING-01's focused audit reports (window B
re-evaluation unblocks on its closure), or any window-C dangler seeks
the b-ii license first.

### D-078 registry amendment — 2026-08-02: D-100 semantics-scoped non-refusing disposition

D-078's closed-registry rule is amended narrowly to register
`whole_window_member_terminally_absent_salvage` as the first non-refusing
disposition. It is non-refusing only when selected through the explicit
`salvage_dangler_exclusion_v1` consumption semantic with a pinned 64-hex
evaluation-basis digest and exactly one fully authenticated D-100 exclusion.
Under `d078_minted_envelopes_v1`,
`d078_authenticated_max_bracket_rederivation_v1`, or no-argument dispatch,
the same spelling is unknown/refusing and a salvage row is ineligible for
selection. This amendment licenses no historical re-evaluation by itself and
does not weaken any existing D-078 refusal spelling.

## D-101 addendum (2026-08-02): live-content site tests leave the blocking gate

**2026-08-07 supersession note:** The clause later superseded by D-101
addendum II is retained unchanged as historical context. Current rule
ownership: D-101 addendum II.

- Status: accepted (Ed-directed 2026-08-02: the site was ratified as
  gating nothing, yet a decision-log edit still turned main red)
- Applies to: `tests/test_build_site_parsers.py`,
  `.github/workflows/ci.yml`

D-101 clause 1 kept site-module unit tests in the blocking `test` job as
ordinary code correctness. That boundary missed a subclass: tests that
render the LIVE repo docs (the two full-build capsule-pack tests). On
2026-08-02, adding the D-106 entry to `docs/decision_log.md` aged D-100
out of the bounded site view and failed those tests on main — a governed
project-record edit acting as a session blocker, which D-101 clause 4
forbids in substance. Amendment: tests that consume live governed
records are site-lane and advisory — they default-skip in the blocking
suite (env guard `JOULEWISE_SITE_CONTENT_TESTS`) and run in the
advisory `release-chain` job. Synthetic-input parser tests remain
gating. The anchor-minting defect itself was also fixed on its merits
(`775fa23`: short anchors mint only from `D-NNN:` entry headings).

Revisit when: Ed changes the site's standing (same trigger as D-101).

## D-101 addendum II (2026-08-03): the site observatory is a separate failure domain

- Status: accepted (Ed-directed 2026-08-03, verbatim intent: the
  annoyance was never email volume — it was project CI failing "because
  of the dumbass site which has nothing to do with the verity of the
  measurements recorded"; "the site observatory should be completely
  separate — though it obviously relies on this project")
- Applies to: `.github/workflows/ci.yml`, `.github/workflows/site.yml`
  (new), `tests/test_build_site_parsers.py`, `tests/test_pack_capsule.py`

Widens the 2026-08-02 addendum from live-content tests to the WHOLE
site lane. The criterion is Ed's: project CI fails only for reasons
bearing on the correctness of the harness, measurements, and governed
records. Amendment:

1. ALL site-lane tests (`test_build_site_parsers`,
   `test_pack_capsule` — synthetic-input and live-content alike)
   default-skip in the blocking suite behind
   `JOULEWISE_SITE_CONTENT_TESTS` and run in the site workflow. Zero
   deletions (D-061-clean); full coverage persists in the site lane.
2. The publication chain (formerly the advisory `release-chain` job)
   moves to a new `site` workflow (`.github/workflows/site.yml`).
   Project `ci` contains zero site machinery; site failures surface
   under the `site` workflow name and are site-lane facts (D-101
   clause 4), never project CI failures. The SITE-02 "D2 guaranteed in
   CI" condition is satisfied by the site workflow's esbuild/decoder
   coverage (the focused step folded into the module run).
3. Project-record lint (docs-freshness, registry pins, gen-state pins)
   is NOT site machinery and REMAINS in the blocking gate — those
   fences protect governed records, which is inside Ed's criterion.

Revisit when: Ed changes the site's standing, or the site gains an
external consumer whose freshness matters (same triggers as D-101).

## D-107: D100-BII-BINDING-01 nested-content closure — cold-gate synthesis: producer-derived admission grammar with value domains (C-A′), scope expanded to the inventory grammar and the false-refusal repairs, over-refusal gate added to the row

- Date: 2026-08-02 (successor session, post-move)
- Status: accepted (cold gate 2 of the D100-BII arc: cold Fable ruled
  the structural diagnosis + closed-grammar shape with a P1–P6
  acceptance predicate; Opus refuter — probe-required brief — broke the
  packet's C-A text on the value axis, proved BOTH established-fact
  errors in the packet, and surfaced two decisive facts outside the
  packet's frame; magistrate synthesis ADOPTS THE REFUTER'S C-A′
  merged with the cold instance's predicate. The cold instance is not
  overruled: its own fallback clause anticipated exactly this
  decision-level disposition. Ed sees this entry.)
- Applies to: joulewise/salvage_dangler.py b-ii license surfaces, row
  D100-BII-BINDING-01 (acceptance amended), window B re-evaluation
  gating. Custody:
  `docs/process_traces/2026-08-03-d111-backfill/coldgate_d100_bii/`
  (packet 2, both
  instruments, fix-1 + delta reports).

**Trigger record (corrected on the refuter's probe):** formulation 1
(a6ce7af) and formulation 2 (fix round 1) were THE SAME PREDICATE —
a key-denylist spelling list; a6ce7af's classifier already recursed
through mappings and lists, and `generated_text` voided exactly where
`model_output` licensed. Round 1 added one spelling and hoisted the
predicate into a raising walk. Two same-signature failures → the
standing trigger fired; C-B (a third enumeration of the forbidden
complement) is REJECTED by both instances.

**Decisive refuter facts (bench-relevant, all probe-backed):**
1. The license tool refuses ALL THREE real window-B quarantine bundles
   at the artifact-INVENTORY gate at bc2ab19, a6ce7af, and the live
   diff alike: the expected sets are ≤8 hand-fixture paths vs 22
   producer-emitted files per real bundle (salvage_dangler.py:34-40,
   :677-689, :701). Pre-existing; falsifies the row's "window B
   unblocks on closure" premise as scoped.
2. Fix-1's classifier over-refuses 769/769 real bundle metadata files
   (`guard_observations[].phase == "after_attempt_N"` treated as
   workload evidence; producer emits it at controller.py:1175) and
   voids the legitimate controller-owned `metadata.extra.node_cleanup`
   (controller.py:2155-2167; three shipping adapters).
3. Four grammar-legal string channels carry workload bytes on the live
   code: `environment_admission.failure`, event/summary
   `failure_reason`, `events[].message`, `summary.failure_message` —
   each has a CLOSED producer value domain (7 abort literals; the
   FailureReason enum), so the value axis closes with zero
   false-refusal cost.

**Ruling:**
1. **Shape = C-A′** (refuter's replacement, subsuming the cold
   instance's P1–P6): producer-derived closed admission grammar over
   the three b-ii read surfaces (metadata.json, events.jsonl rows,
   summary_metrics.json) — per-container closed key set (exact raw-key
   match; any non-member voids, which subsumes the Unicode-confusable
   case a fortiori) AND a decidable per-leaf value predicate from
   {CLOSED-ENUM, HASH, NUMBER/TIMESTAMP, BOOL/NULL}; no leaf admits on
   bare isinstance(str). The workload-evidence spelling list may remain
   as defense-in-depth but carries no load.
2. **Derivation obligation (the in-kind discriminator):** every
   admitted key set and value domain is derived from producer code AND
   verified to contain every value emitted across the governed corpus
   (the 24 abort bundles in runs_window_*/ plus the 3 quarantine
   subjects). A key or value present in a real governed bundle and
   absent from the grammar is a defect OF THE GRAMMAR. Open containers
   (none found on this surface) take D-105's documented decidable
   superset, never claimed exactness.
3. **Scope expansion, same commit:** (a) the F-1 artifact-inventory
   grammar is corrected under the same derivation obligation; (b) the
   guard-observation phase domain admits after_attempt_N; (c)
   `metadata.extra` admits the six producer scalars PLUS node_cleanup
   (closed list-of-mappings grammar). These are the same surface and
   the same duty; splitting them would re-create the vacuous-inertness
   defect.
4. **Fence ruling (recorded):** the "no third schema-shaped
   formulation" fence REACHES this surface. An allowlist differs in
   kind from the two failed denylists iff (i) membership is decidable
   over a finite admitted set AND (ii) the set is producer-derived and
   corpus-verified per clause 2 — D-097's own evidentiary standard.
   Without (ii) a closed grammar is the third enumeration and the
   fence bites; with it the fence is satisfied. Capture identity
   remains bound solely by interval containment + digest freeze
   (untouched, byte-identical per the audits).
5. **Row acceptance AMENDED (over-refusal gate):** the row does not
   close until (i) inspect_salvage_attempt LICENSES all three real
   quarantine bundles, pinned by a read-only regression against the
   real bundles or a hash-pinned byte-faithful fixture; (ii)
   regressions prove all four value channels VOID; (iii) the extra
   allowlist and (iv) the corrected inventory set are recorded with
   their derivations. Prior acceptance items stand.
6. **F2 (recursion):** same commit; explicit depth guard (32; producer
   maxima are 7/4) raising SalvageAuthorizationError — refuse, never
   truncate, no RecursionError conversion; the boundary-catch fact
   (SalvageAuthorizationError subclasses ValueError; run_campaign's
   handler continues fail-closed) is recorded.
7. **License:** fix round 2 proceeds NOW under this ruling as one
   commit + a FRESH focused audit against the merged predicate (cold
   P1–P6 + clause-5 gate). Return triggers: any grammar-should-void
   content licensing in that audit = third same-signature failure →
   return to this gate, no bench round 3; any container that can be
   neither closed nor supersetted decidably → decision level.
8. **Packet-hygiene failures recorded against the magistrate (third
   occurrence):** established fact 2 laundered a bounded trace into
   "over-refusal clean" (false, 769/769); established fact 3 was
   uncited and false (and re-leaned on winB-closure-facts.md, the
   exact artifact D-106 ground (1) faulted); the delta's open flag G1
   was omitted; two precedent citations mislabelled. STANDING
   TIGHTENING: every established-fact item in a cold-gate packet
   carries file:line or a probe transcript, and the source documents'
   flags sections are quoted IN FULL, never summarized.
**Dissents:** none unabsorbed — the cold instance's Q3/Q5 position is
superseded per its own recorded fallback ("the identical fix shape via
a minimal amendment, and nothing else in this ruling changes"); the
refuter's F-8 conditions are implemented by clauses 3, 4, and 8.

Revisit when: the round-2 focused audit reports (window B
re-evaluation unblocks only on the amended-row closure), or any
window-C dangler seeks the b-ii license first.

**Addendum (2026-08-03, outcome of the above revisit):** the round-2
focused audit fired the D-107 clause-7 return trigger — fix round 2
implemented C-A′ but left open-superset leaves that license workload
bytes (bench-confirmed). Cold gate 3 (two cold Fable instances + Opus
refuter) concluded, probe-backed, that clause (c) **cannot achieve its
"zero workload output bytes" predicate under any bench formulation**
(the grammar constrains values but not list cardinalities; ~1.2 KB of
free numeric-leaf capacity remains under any grammar), AND that the
content-substitution attack (c) was ordered to close is **already
closed by the landed clause (b)** hash-sealed closure-manifest pin. Per
rule 11 the bench loop was STOPPED (not a fourth round); the disposition
is escalated to Ed as **D-108 pending** — retire clause (c) as a license
precondition [magistrate + refuter recommendation], or land a
mechanically-derived cardinality-closed grammar with the numeric
residual explicitly ruled. Fix rounds 1+2 are held UNCOMMITTED/untrusted
on branch `impl/d100-bii-binding`; nothing this addendum describes is
landed. Full record:
`docs/process_traces/2026-08-03-d111-backfill/coldgate_d100_bii/`
(PACKET-3, both cold
rulings, refuter-3, SYNTHESIS-gate3-FOR-ED). This supersedes D-107's
"fix round 2 proceeds now" license pending the D-108 ruling.

## D-108: D100-BII-BINDING-01 clause (c) RETIRED as a license precondition — row closes on (a)+(b)+(d), with the clause-(d) three-occurrence re-record carrying the formal load

**2026-08-07 supersession note:** The Window-B clause later superseded by
D-113 is retained unchanged as historical context. Current rule ownership:
D-113.

- Date: 2026-08-03
- Status: accepted (Ed ruling 2026-08-03: explicit deferral to the
  joint magistrate + Sol recommendation — "i defer to you and sol's
  decision". Inputs: cold gate 3 (two cold Fable instances + Opus
  refuter, all recommending retirement;
  `docs/process_traces/2026-08-03-d111-backfill/coldgate_d100_bii/`)
  plus an Ed-requested 2-round adversarial Sol xhigh consult over the
  decision packet (thread `019fc9bb-73fd-7042-8faf-2a72d74ee5b3`,
  record `docs/process_traces/2026-08-03-d111-backfill/debate-d108-d109/` (tracked; scratch original in .desk); tracked copy: `docs/process_traces/2026-08-03-d111-backfill/debate-d108-d109/`), which CONVERGED
  on retirement while tightening the closure conditions below.)
- Applies to: row D100-BII-BINDING-01, `joulewise/salvage_dangler.py`
  b-ii license surfaces, window B re-evaluation gating. Supersedes
  D-106 clause 3(c) and the D-107 C-A′ obligation AS LICENSE
  PRECONDITIONS; the D-106 revisit clause survives (clause 5 below).

**Grounds (probe-backed, gate 3):** (i) D-100's "zero workload output
bytes" predicate is unreachable under any bench content grammar —
≥195 finite-only numeric leaves ≈1.2 KB free capacity in one real
subject's metadata (refuter R-5) plus producer-open list cardinalities
(R-4), which fired D-107 clause 7's second return trigger; (ii) the
substitution attack clause (c) was ordered against is already closed by
the LANDED clause (b) hash-sealed closure-manifest pin (R-6 traced the
only production path); (iii) what a grammar could still add is
protection against a careless closure AUTHOR — a smaller, partly
unclosable duty that does not warrant a license precondition.

**Ruling:**
1. Clause (c) — the nested-content closure — is retired as a license
   precondition. No further grammar formulation may be benched against
   the D-100 zero-output-bytes predicate; that predicate is recorded
   as mechanically unreachable on this surface.
2. The row closes on: **(a)** telemetry interval containment; **(b)**
   the hash-sealed closure-manifest pin (landed); **(d)** the
   repaired-tool, digest-bound re-record executed over ALL THREE D-087
   closure occurrences, results bound to the exact closure manifest.
   Consult correction adopted on the evidence surface: the exclusion
   TARGET is one member (mtadd-p2048o0128-r08, occurrences 2+3), but
   the authorization EVIDENCE surface is all three occurrences — the
   closure loader refuses any closure without exactly three and
   inspects every one (`salvage_dangler.py` exactly-three predicate;
   b04-b2's valid supersession removes it as the excluded member, not
   from the closure's evidentiary predicate). The 2026-08-01 manual
   verification (full b-ii facts for the two r08 attempts only) is
   CORROBORATION ONLY and carries no formal load.
3. The derived content grammar (L-A′) is demoted to non-load-bearing
   hygiene. Decision-record obligation: bank the EXECUTABLE L-A′
   derivation + full probe transcript (immutable input hashes for the
   26 b-ii bundles, generated grammar, 26/26 admission results, every
   carrier mutation INCLUDING why the seventh carrier survives, tool
   identity) in
   `docs/process_traces/2026-08-03-d111-backfill/coldgate_d100_bii/` at
   or before row close. It
   must never be described as zero-output or substitution closure.
4. Fix rounds 1+2 held uncommitted on `impl/d100-bii-binding`: the
   clause-(c) grammar work is discarded or demoted per clause 3; the
   clause-(a) containment work is salvageable subject to fresh audit
   of whatever subset is kept.
5. D-106's revisit clause survives intact: a future (e.g. window-C)
   dangler seeking the b-ii license RETURNS TO THE GATE. Retirement
   removes the automated content guard, not the gate.
6. Window B re-evaluation unblocks when the row closes per clause 2.

## D-109: CAL-BRACKET-D079-01 F3 — A-min-with-reservation adopted (writer-enforced receipt ledger, reservation-first, repo-committed head pin); R1 ledger-authority and R2 prior-observation-set rulings

**2026-08-07 supersession note:** The issuance clause later superseded by
D-116 is retained unchanged as historical context. Current rule ownership:
D-116.

- Date: 2026-08-03
- Status: accepted (Ed ruling 2026-08-03: same explicit deferral to the
  joint magistrate + Sol position, same debate record. Arc: the fix
  investigation recommended A-min; Sol round 1 BROKE that formulation
  as stated (writer crash-window; prefix-subset is not anti-rollback)
  and recommended Option B for the timeline; magistrate round 2
  supplied the low-schedule-pressure record, the metrology-centric
  pivot, and the shared-R2 marginal-cost analysis; Sol WITHDREW B and
  converged on A-min-with-reservation, marginal cost Medium. Both
  soundness holes were lead-verified at the bench before adoption.)
- Applies to: `scripts/validate_powermetrics_fiducial.py` (sole
  production calibration writer), `joulewise/calibration_bracketing.py`,
  `joulewise/whole_window.py`, `scripts/run_campaign.py`,
  `configs/calibration/calibration_acceptance_d079_v2.json`, and every
  consumer construction of `AuthenticatedConsumptionSession`. This is
  a faithful IMPLEMENTATION of D-102 (no threshold/freshness
  amendment); it supplies the authority/universe rulings D-102 left
  silent. Lands with F1 + F2 as the single combined CAL-BRACKET fix
  round. Option B (signed narrowing amendment) is recorded as REJECTED
  fallback — coherent and honest, but it weakens the thesis instrument
  where the project has slack to build the sounder boundary.

**R1 — ledger authority, retention, anti-rollback (7 clauses):**
1. A canonical observation-receipt ledger and its append API are the
   SOLE authority for governed calibration observations. An off-ledger
   calibration artifact is invalid everywhere: as bracket endpoint,
   trigger evidence, derivation member, or claim evidence. Consumers
   enumerate ledger entries only, never caller-supplied directories.
2. RESERVATION-FIRST: every capture appends an authenticated `pending`
   attempt entry BEFORE hardware capture begins, and must finalize it
   as valid / systematic-invalid / ordinary-invalid / abandoned. Any
   unresolved pending, unfinalized, malformed, or conflicting entry
   causes claim evaluation to REFUSE. (Grounds, bench-verified: the
   writer creates capture state pre-receipt and has pre-manifest
   failure exits — a publish-on-return receipt misses exactly the
   crash/interrupt cases a completeness mechanism exists to catch.)
3. Receipts are immutable and hash-chained: sequence, predecessor,
   attempt id, content id, artifact hashes, six-field epoch, full T1,
   capture time, exact bound lexeme, disposition, custody locator.
4. The acceptance artifact pins its baseline ledger head. Evaluation
   ALSO requires the independent current-head pin (clause below),
   verifies one complete non-forked chain extension from baseline to
   current, and threads ONE immutable ledger snapshot through every
   consumer path (session, direct runner path, secondary verifier) —
   repeated independent loads are a refusal-grade defect.
   Anti-rollback authority: a REPO-COMMITTED head-pin file
   `{sequence, head_digest, ledger_schema}` (existing checked-in
   byte-pin trust model; no second trusted latest-sequence store).
   Rotation is epoch-bounded — at most one lead-controlled
   quiet-machine collection session — and NO claim evaluation may
   occur between ledger advancement and pin commit; a physical head
   differing from the committed pin refuses.
5. Ledger history is retained permanently. Referenced evidence remains
   in authenticated custody; missing or unverifiable required bytes
   cause refusal, never silent omission.
6. Version 1 is single-authority, single-machine. Remote/other-machine
   captures are invalid until imported through an authenticated ledger
   transaction; direct multi-machine append requires a new ruling.
7. Threat model, stated honestly and to be stated wherever A-min is
   described: the mechanism closes workflow omission, unregistered
   evidence, and rollback/stale-head consumption. It does NOT defend
   against a malicious trusted writer or an authority that rewrites
   both Git and ledger history. No stronger claim may be made.

**R2 — prior-observation set and prospective triggers (8 clauses):**
1. The issuance cutoff is an exact ledger sequence + head digest.
2. `derivation_corpus` remains exactly the n=19 threshold-producing
   observations.
3. `prior_observation_set` = every content-distinct governed
   observation known at the cutoff — valid, systematic-invalid,
   ordinary-invalid, blind holdout, and unresolved — with epoch and
   disposition recorded separately. (The current artifact's two
   ID-only `blind_exclusions` are insufficient and are superseded.)
4. Content identity is path-independent, derived from canonical
   primary-byte hashes; attempt identity is separate; copies do not
   create new observations.
5. "New" (trigger population) = current authentic content IDs −
   `prior_observation_set`, regardless of capture timestamp or source
   root; a previously unknown historical artifact IS new when
   discovered. Every new observation is judged under the PRIOR
   artifact (D-102's prospective rule).
6. New unresolved or unclassifiable attempts cause refusal; only after
   trigger disposition may a successor artifact absorb them.
7. The 32-valid/6-invalid same-epoch inventory is a backfill
   CANDIDATE, not a ratified classification: identities may seed the
   backfill, but dispositions require raw-physics + hash verification
   before issuance, and any unresolved member blocks issuance.
8. Counting rule for the D-102 corpus-doubling trigger (19→38): 38
   TOTAL authenticated, content-distinct, VALID same-epoch
   observations — including previously blind observations once
   unblinded — not 38 post-cutoff observations. Under the candidate
   inventory, six further valid observations trigger re-derivation.

## D-110: Mint 1 retroactively NON-CLAIM-BEARING (taint-and-remint); RT-2 dependency edge minted; the night consult's 7B-mint license SUSPENDED

> **2026-08-07 supersession (D-117):** clause 3's historical re-mint
> order is SUPERSEDED — structurally unsatisfiable at main (see
> `docs/process_traces/2026-08-06-d110-remint-fork/`); replaced by
> three prospective windows. The taint holding and the never-zero
> allowance correction STAND and bind the D-117 mints.

- Date: 2026-08-03 (Ed ruling, present, option "taint-and-remint" selected
  from the magistrate's three-option packet during the 16h runway)
- Status: accepted (trigger: the Ed-ordered two-week read-only soundness
  sweep — 34 agents, Fable auditors + Sol xhigh second-eyes, run in a
  parallel session — finding RT-1, Sol-confirmed. Memory record:
  two-week-soundness-sweep-2026-08-03; full results ephemeral in that
  session's task outputs.)
- Applies to: `df-ph-decode-floor-mint1` (absolute 3.592138 /
  comparative 7.377086 / operative gate 7.377086 J), row
  MINT-GENERALIZE-01, CLAIMS_STATUS, the D-095 chain.

**Grounds (RT-1):** mint #1's consumed fiducial bounds embed a
never-zero allowance of ZERO where D-102 pin 3 mandates
+max(drift, 0.010818 s) — for a10 a ~+43% wider operative bound than the
7.377086 J floor was derived from. The CAL-BRACKET-D079-01 adjudication
record framed the defect as a non-salvage severity escalator
(mis-refusals only); the accepted-side, anti-conservative direction was
never ruled on. RT-5 (recorded): all four PASSED window verdicts are
UNTAINTED — the 0.010 cliff is strictly tighter than the ruled screen
(drifts 8-25x below it) and the 10-field identity match supersets the
D-102 epoch; the taint is confined to floor artifacts.

**Ruling:**
1. Mint #1 is retroactively NON-CLAIM-BEARING. No consumption, quotation
   as a claim, or gating use of its floors until re-mint. Per
   CLAIMS_STATUS no landed claim has consumed it; if any consumption is
   discovered it voids with it.
2. RE-MINT CONDITIONS: (a) the D-109 CAL-BRACKET implementation lands
   (merged + gauntlet-clean); (b) the acceptance artifact is ISSUED
   (R2 backfill verified, ledger bootstrapped, head pinned); (c) the
   library validator's evidence_root_id pin is widened by scheduled work
   (DC-2/FM-3) so minted artifacts authenticate truthfully; then mint #1
   re-derives under the landed selector with the computed allowance.
3. RT-2 dependency edge MINTED in the kernel: MINT-GENERALIZE-01 is
   hard-blocked on CAL-BRACKET-D079-01 landing + this ruling's re-mint
   conditions. The 2026-08-03 night consult's Q3 license (governed 7B
   mint after byte-compare) is SUSPENDED as superseded-by-evidence —
   recorded honestly: the joint consult licensed it without RT-1 in
   frame because the adjudication record itself understated the defect's
   direction.
4. The Q1 mint-1 byte-compare replay REMAINS licensed (verification of
   tooling parity + the FM-1/FM-2 re-derivability question; it creates
   no claim). Its result is recorded either way.

## D-111: Adjudication evidence gains tracked custody — docs/process_traces/ is the home; .desk is working scratch only

- Date: 2026-08-03 (Ed ruling, present; option "track adjudication
  evidence" selected)
- Status: accepted (trigger: the soundness sweep's strongest structural
  finding — six domains independently: load-bearing adjudication
  evidence exists only in untracked `.desk/` — cold-gate packets and
  rulings, the D-108 debate record, the gate-3 synthesis CLAIMS_STATUS
  cites, the TEST-SPEED timing corpus, archive manifest digests — while
  the project's whole pivot is custody and attestation.)
- Applies to: all future adjudication artifacts; a named backfill set.

**Ruling:**
1. Going forward, LOAD-BEARING adjudication artifacts — cold-gate
   packets and rulings, refuter reports, debate/consult records that a
   decision entry cites, digest-bound re-records, decision-input
   corpora (e.g. timing data), archive manifest digests — are committed
   under `docs/process_traces/` (dated subdirectories) in the same
   session that produces them. A decision entry may not cite a memo as
   authority unless it is tracked or explicitly declared ephemeral in
   the entry itself.
2. `.desk/` remains legitimate working scratch; nothing load-bearing
   terminates there.
3. BACKFILL (this session): the D-100/D100-BII cold-gate packets and
   rulings
   (`docs/process_traces/2026-08-03-d111-backfill/coldgate_d100_bii/`,
   `docs/process_traces/2026-08-03-d111-backfill/adjudication_packet_20260801/`),
   the D-108/D-109 debate record, the night-consult rulings memo, the
   clause-(d) re-record JSON, the CAL-BRACKET F3 memos
   (`.desk/calbracket_d079/`), the TEST-SPEED timing corpus
   (`.desk/test-speed-consult/`, `.desk/testspeed/`), and the archive
   manifest digests (RS-4). Large or binary members may be represented
   by a digest manifest with the bytes retained in `.desk` + backup.

## D-112: Window B re-evaluation STOP gate — classification (i) adopted; the D-100 license is EXHAUSTED AS DRAWN; the r06 disposition ruling is PARKED FOR ED

**2026-08-07 supersession note:** The parked Window-B disposition later
superseded by D-113 is retained unchanged as historical context. Current
rule ownership: D-113.

- Date: 2026-08-03 (magistrate synthesis of the night's cold gate; both
  instruments convergent by independent methods; full verbatim record
  tracked at `docs/process_traces/2026-08-03-winB-reeval-stop/`)
- Status: accepted (gate outcome recorded; the successor ruling it
  parks is NOT decided here)
- Applies to: window B re-evaluation licensing (D-100 §5 / D-106 /
  D-108 chain), bundle `mtadd-p2048o0128-r06`, the NEG-8 drift bound,
  future cascade classifications.

**Ruling:**
1. The 2026-08-03 governed re-evaluation refusal was CORRECT
   fail-closed machinery on real evidence state (classification (i)).
   Sole cause: r06's collection-time clock-anchor failure
   (`native_intersection_empty`) + downstream environment-admission
   temporal-binding failure — proven by falsify-by-removal (69/69 clean
   without it) and per-bundle attribution with a stage-1-clean
   control-flow proof. No repair row; no corrected command; the
   deviation-escape STOP was itself correct.
2. EVIDENCE GAP recorded against `mtadd-p2048o0128-r06` (kernel row
   WINB-R06-DISPOSITION-01). The `current_environment_refusals`
   sub-branch remains unpinned (open sub-question in the record).
3. The D-100 re-evaluation license is EXHAUSTED AS CURRENTLY DRAWN:
   unreachable while r06 is a member (exclusion cap spent on r08; r06
   is no dangler; waivers forbidden under salvage). Window B
   re-evaluation stays BLOCKED; the original FAILED verdict stands as
   issued; nothing is reinterpreted.
4. PARKED FOR ED (successor packet; Ed-level because it amends a
   claim-license shape): the r06 removal channel (per-member waiver
   ruling / membership re-binding / abandon re-evaluation for window C
   re-collection), the refuter-F7 scope question (whether one member of
   an already-barred cell may void the whole window's consumption), and
   the fresh NEG-8 bound re-mint that any future licensed run needs
   (the 2026-08-01 bound expired 2026-08-02; recorded against the
   magistrate's packet as an omission).
5. STANDING CORRECTION (both instruments): condition spellings are
   NON-UNIQUE to producer — `environment_admission_missing` has a
   window-level cascade producer AND a per-bundle reduce-time producer.
   D-100's cascade classification was correct for the producer it
   examined; future cascade classifications must name producers.

## D-109 addendum II: reviewed mint-core interface amendment (integration-collision resolution); D-110 oracle clarification

- Date: 2026-08-04 (successor magistrate ruling after bounded
  pre-decision Sol high consult, one round; Ed's HIGH effort cap
  observed)
- Status: executed (PR #100 gate-complete, CI green at `4280ebd`;
  merge is Ed's tap — the harness denies agent self-merge)
- Record: `docs/process_traces/2026-08-04-calbracket-integration-collision/`
  (FINDING.md, RESOLUTION.md, impl + delta re-audit reports) and
  `docs/process_traces/2026-08-04-calbracket-collision-consult/`

1. D-109 R1.4's `calibration_ledger_snapshot` threading is a DELIBERATE
   REVIEWED INTERFACE REVISION of the mint core. The generalized mint's
   `_CORE_SIGNATURES` pin is amended to the new signature; no adapter
   shim, no multi-version pin, no core-file digest pin (consult Q1,
   adopted). Future `_CORE_SIGNATURES` changes require explicit
   signature-pin review plus parity evidence (noted in-code).
2. The guard's framing is corrected to REVIEW-PINNED MINT-CORE
   INTERFACE — it pins selected signatures of a review-controlled core
   file and is not a byte freeze; "byte-identical" is reserved for
   observed output comparisons.
3. D-110 CLARIFICATION (conditions unchanged): tooling byte-identity
   evidence means INTEGRATION-TREE CORE-VS-WRAPPER PARITY on identical
   inputs. It does not require any future artifact to match the tainted
   historical mint-1 digests — D-110's corrected re-mint may
   legitimately produce different bytes. MINT-GENERALIZE-01's
   acceptance evidence is reworded accordingly in the kernel.
4. Guard hardening (delta re-audit F2, proven live): rendered-signature
   comparison is spoofable by a default whose `repr()` is `None`; the
   guard now identity-checks the None sentinel defaults structurally,
   with a regression. Residual honestly held: `__signature__` spoofing
   remains a property of the approach; the guard is a reviewed-drift
   tripwire, not a security boundary against an adversarial core file.
5. PROCESS FINDING (candidate rule, NOT ratified here — rule-11
   cold-gate packet item): the lead's rule-1 verification replay runs
   on the INTEGRATION tree whenever the branch is behind main. Recorded
   with the collision as its motivating catch (CI on the merge ref was
   the only layer that could see it).

## D-113: WINDOW B TERMINALLY CLAIM-RETIRED — abandonment ruled (Ed); fresh collection beginning Window C; F7 whole-window precedent affirmed

> **2026-08-07 amendment (D-117 cl.4):** the readiness dependency on
> D-110's historical re-mint is REMOVED; the three-window P1 closure
> precedes the MET-WINDOW-C-01 replacement campaign.

**Date:** 2026-08-05 (Ed ruling, in-thread; transcribed by the Fable
magistrate after a bounded Sol xhigh design consult — full record at
`docs/process_traces/2026-08-05-d113-rigor-consult/`). The number was
reserved by D-112 clause 4.
**Status:** RATIFIED (Ed chose channel (c) of D-112 clause 4 verbatim:
"the rigor of the data collected matters, i have ample time — soundness
and quality of the project and claims above all").

**Ruling.**
1. **Abandonment.** No Window B re-evaluation or claim consumption will
   occur, ever. This entry is a license-and-claim-custody disposition,
   NOT a governed evaluation: no new verdict row is emitted; the
   original FAILED verdict remains the sole as-issued Window B verdict
   and continues to govern default consumption.
2. **Terminal status: RETAINED_IMMUTABLE / CLAIM_RETIRED /
   PERMANENTLY_NON_CLAIM_BEARING.** The authenticated corpus, campaign
   log, closure/membership artifacts, r06 stop record, and verified
   backup remain preserved under existing custody policy (no deletion,
   movement, or re-archival is required or triggered). Window B is
   prohibited from supplying any claim cell, floor, calibration, NEG-8
   reference, drift bound, or whole-window basis. Labelled read-only
   use for instrument forensics, machinery regression, protocol design,
   and diagnostics remains permitted; every such use carries the label
   "Window B, original verdict FAILED, D-113 claim-retired, non-claim
   evidence."
3. **License retirement (scoped).** D-100 §5 as modified through
   D-106/D-108 is EXHAUSTED AND RETIRED for Window B;
   `salvage_dangler_exclusion_v1` may not be invoked against that
   corpus again. The license text and artifacts are preserved as
   historical evidence. D-100's general semantics and D-108 clause 5's
   future-dangler return-to-gate rule survive intact for other windows.
4. **WINB-R06-DISPOSITION-01 closes: ABANDONED_FOR_FRESH_COLLECTION.**
   The unpinned `current_environment_refusals` sub-branch is retained
   as unresolved historical residue, nonblocking (r06 can authorize no
   claim). No successor r06 investigation row absent a new forensic
   purpose.
5. **F7 precedent AFFIRMED as current semantics:** an included member
   carrying a globally scoped refusal voids the whole-window
   consumption basis even when its cell is independently barred; barred
   status has no upstream authentication effect. Recorded explicitly as
   CONFIRMATION of the ratified fail-closed semantics, not as a finding
   that whole-window invalidation is always the physically correct
   causal scope. Any future cell-scoped semantic requires a new
   Ed-ratified amendment under D-083's revisit rule, including the stated
   causal-domain proof and preregistration gates,
   a new explicit semantics identity, and anti-claim-shopping
   regressions — none of which is built now (the only use case was
   abandoned). Blast radius is managed prospectively via shorter,
   claim-coherent windows.
6. **NEG-8:** the expired Window-B bound and its re-mint obligation are
   MOOT. The standing near-run-time freshness rule (window runbook +
   D-078: dual-family bound minted inside the same quiet window that
   consumes it; 86400 s is a maximum validity horizon, never permission
   to reuse; exact identity bindings; refusal on change or expiry)
   continues to bind every future window BY CROSS-REFERENCE — no
   duplication of thresholds into this entry. A Window C mint is a
   fresh mint, not a re-mint.
7. **Fresh-claim reset.** Every still-desired Window-B claim component
   routes to fresh collection beginning with Window C; no Window B
   member counts toward replacement claims (C2's o0128/o0512 and C4's
   Window-B members return to uncollected-for-claim state).
   MET-WINDOW-C-01 must be re-scoped from its remainder-only shape to a
   fresh-claim plan; if the full replacement exceeds the runbook's
   2-4 hour envelope with references, calibrations, and >=20% failure
   margin, it splits prospectively across windows C and D rather than
   compressing the night.
8. **STANDING PRINCIPLE (Ed's prerogative, operationalized):** for
   irreversible claim-bearing collection, schedule pressure, sunk cost,
   and convenience never justify weakening a soundness gate; unknown or
   unresolved known-failure state is NO-GO; when salvage and fresh
   collection differ materially in epistemic quality and fresh
   collection is feasible, fresh collection is the default. PAIRED
   GUARDRAIL (anti-rigor-spiral, with D-078): more data or more process
   is required only when it closes a named validity threat or
   materially improves a planned claim — smaller independent windows, a
   narrower claim, or no claim may be MORE rigorous than
   over-collection. Escalation stays event-driven (repeated known
   failure, new producer for a refusal spelling, identity-epoch change,
   consumer failure after clean collection); no new recurring
   ceremonies. Mechanization is ONE hard start fence on the
   claim-window task (a reviewed frozen-plan readiness record + every
   hard dependency satisfied, verified by the ordinary launcher), not a
   new governance subsystem.
9. **Window C readiness: NO-GO until the consult's precondition gates
   are green** (consult record Q4, the ONE home for the full list):
   frozen fresh scope with runtime budget; desk toolchain + D-078 chain
   complete on merged main including the ISSUED D-079 acceptance
   artifact and the D-110 (b)+(c) re-mint chain; instrument/machine
   identity gates including the 140 W adapter discrepancy and a fresh
   §5A; quiet-guard status used honestly (installed-INACTIVE is not a
   Window C control; the proven zero-agent guarded-shell path with
   independent census is the default); and one frozen GO/NO-GO
   checklist with no in-night policy decisions. The runbook
   §5A-vs-§13.1 member-level clock-retry inconsistency must be resolved
   BEFORE the plan freeze; rigor-first default is NO member-level
   anchor retry without a prospective ruling.

**Consult dissents recorded (adopted):** kept-local-never-consumed was
rejected in favor of claim-retired-with-labelled-forensic-use; the
strict F7 answer is semantics-confirmation, not causal-scope truth;
D-110 condition (c) is readiness assurance for Window C, not
contamination physics; an installed-inactive quiet guard contributes
nothing to the Window C assurance case.

**Consequences.** CLAIMS_STATUS Window B section gains the terminal
labels; kernel row WINB-R06-DISPOSITION-01 retires as ABANDONED (same
session, after in-flight read-only sessions clear); MET-WINDOW-C-01
re-scope and the claim-window start fence register as queued work;
RUN_STATE's parked-decisions list drops D-113.

## D-114: T3-CHAIN DESCOPE — t3 stays the interactive control plane; t3-resident-during-measurement-windows is DROPPED (Ed directive, supersedes the 2026-08-03 T3-DRIVE priority)

**2026-08-07 supersession note:** The readiness clause later superseded by
D-117 is retained unchanged as historical context. Current rule ownership:
D-117.

**Date:** 2026-08-05 (Ed, in-thread, during the desk session).
**Status:** RATIFIED by the directive's own author. This reverses Ed's
2026-08-03 ~23:55 T3-DRIVE-PRIORITY directive. Under rule 11 a
lieutenant may not self-exempt from a standing priority; that
constraint does not bind Ed reversing his own instruction, so no cold
gate was convened. The lead proposed the descope shape; Ed ruled.

**Question.** The t3-drive chain (host-wide quiet lease, refuse-at-arm,
resident watcher, t3 handoff/relaunch, README banner projection, plus
an app-up/app-down characterization pair to decide app-adjacent window
admissibility) had grown a root-owned, sudo-capable, credential-bearing
surface — a 7-blocker focused audit on commit 1 alone, and a design
consult showing the credential could not be honestly removed without
also revising Q10/Q11/Q13/Q19/Q24 as a set. Ed: "is the juice worth the
squeeze for a UX improvement of using t3 as a control plane?" and "I am
tired of wasting time on this control plane stuff and want to get back
to the project."

**Ruling.**
1. **KEEP — t3 as the INTERACTIVE control plane.** Ed drives sessions
   from t3, including remotely and away from the measurement machine.
   This costs nothing and requires no guard machinery.
2. **DROP — t3 resident during measurement windows.** Claim windows
   return to the proven path: quit t3, ordinary guarded shell, zero
   agent sessions, fresh §5A, walk away. Every successful claim window
   to date used exactly this path. The app-up admissibility question is
   therefore MOOT, not answered.
3. **QUIET-GUARD-01 re-scoped to COMMIT 1 ONLY** — the host-wide quiet
   lease and process census, installed-INACTIVE. Retained on non-t3
   merit: it gives the ordinary guarded-shell launcher a MECHANICAL
   refuse-at-arm census, replacing today's procedural eyeballing. Its
   seven audit blockers are still fixed to the safety bar before it
   lands (it is root-adjacent regardless of who calls it).
4. **SHELVED:** QUIET-GUARD commits 2-4 (launcher interception, t3
   handoff + resident watcher, t3-relaunch + banner projection + all
   credential handling); T3-CHAR-PAIR-01 (BOTH arms — the r03 re-capture
   and the app-DOWN arm); WO-T3-VIS-01; SEC5A-REMOTE-01 (its
   programmatic substrate lived in the dropped scope).
5. **T3-DRIVE-PRIORITY gate LIFTED** (`active_global_gates: []`); the
   project queue is ungated. The two in-flight t3-adjacent desk items
   (T3-AMEND-01 doctrine bookkeeping, COLDGATE-VALIDATOR-01) finish
   because both are cheap, near-complete, and independently useful.
6. **Q13's degraded tail is ACCEPTED as an edge case** (Ed, explicit):
   if a relaunch fails and no session returns, there is no remote
   signal. A failed relaunch requires physical presence anyway, so
   local discovery at next login is sufficient. This retires the
   requirement that motivated the unattended-push credential.
7. **Q10 (guard git identity WITH unattended push) is SUPERSEDED** —
   moot under the descope; no credential enters any guard path.

**Design record preserved for any future revival** (from the 2026-08-05
credential consult, before the descope was ruled): a credentialed
network pusher running DURING a quiet window contradicts the window's
defining property. The correct shape is credentials only at the
unprivileged interactive boundary (pre-arm and post-window pushes), a
PRE-ARMED SERVER-SIDE DEAD-MAN ALARM for the no-return case (which also
catches total host death), a dedicated non-login service UID rather
than HOME-restore env scrubbing (root is otherwise ambiently
credential-reachable via git helpers / SSH / Keychain), and a banner
that can only truthfully say ARMING_REQUESTED pre-window.

**Consequences.** The successor's queue is the science queue: the two
open soundness-sweep blockers (RT-1 mint-floor understatement; voided
numbers on README/PROJECT_STATUS), the a10 phase-floor extraction, and
MINT-GENERALIZE-01 — whose D-110 condition (a) was satisfied the same
day by the CAL-BRACKET merge (PR #100, `f75d12b`).

## D-115: Quiet-guard Q2 setup authority is a FIXED INSTALLATION CAPABILITY, not general root authority (Commit-1 packet entry; renumbered from the contract's proposed D-114 marker)

**Date:** 2026-08-05 (lead adjudication, Fable magistrate session).
**Status:** ADJUDICATED under Ed's standing Q2 license (2026-08-05
ratification batch: Q2 proceeds on lead defaults subject to Ed veto).
**Numbering note:** the Commit-1 worker proposed this entry as D-114
inside `docs/contracts/quiet_guard.md` (it does not own the decision
log, correctly). D-114 was consumed the same day by the T3-CHAIN
DESCOPE, so this entry is D-115; the contract marker renumbers to
D-115 in the Commit-1 fix round. **Packet-letter deviation, ruled:**
the IMPL-PACKET file map places this entry in Commit 1's delta, but
the branch forked before D-114 landed and an in-branch append would
manufacture a merge conflict in this file; the entry lands on main and
is merged back into `impl/quiet-guard`, which satisfies the packet's
purpose (binding authority exists before the capability merges) with
cleaner custody.

**Question.** Q2 asked what authority the one-time
`scripts/setup_quiet_guard.sh` sudo session exercises when it creates
the root-owned quiet-guard state under
`/Library/Application Support/JouleWise/quiet-guard/`.

**Ruling.**
1. **Capability boundary.** The setup script exercises a fixed
   installation capability: create the root-owned state/install
   directories, install the fixed-command privileged helper and the
   narrow `sudoers.d` command aliases, and write `live_promotion=false`.
   It confers NO general root authority; nothing outside that
   enumerated set is licensed. Normal guard operation is `sudo -n`
   against the fixed command aliases only, and the helper drops to the
   invoking uid/gid before any agent child executes.
2. **Binding conditions on the capability** (from the 2026-08-05
   adversarial audits qg-audit-A/B; the capability is not validly
   exercised without them):
   a. **Fresh interactive authorization** — the installer must
      invalidate any cached sudo timestamp (`sudo -k`) before
      requesting authorization, so a cached ticket can never silently
      convert repository state into root-executed code.
   b. **Authenticated content** — what is installed must be
      authenticated against pinned digests of the reviewed artifacts
      (or an equivalently strong provenance check), not merely parsed
      for syntactic validity; root-staging closes copy races but does
      not authenticate what was staged.
   c. **Real interpreter isolation** — the installed helper runs with
      genuine isolation guarantees (no site initialization, no
      user-site, no environment hooks: `-I`-equivalent), matching the
      contract's isolation claim.
3. **Inactive by construction.** Commit 1 installs INACTIVE:
   `live_promotion=false`, `arm` refuses (`t3_char_pair_verdict_missing`),
   and no launcher, chain, watcher, or projection code is in scope
   (D-114 descope). Activation requires a separate, later, Ed-visible
   step and is not licensed by this entry.

**Consequences.** The Commit-1 fix round renumbers the contract marker
and implements conditions 2a-2c with discriminating regressions; the
QUIET-GUARD-01 row cannot land while any condition lacks enforcement.

## D-116: D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (D-110 condition (b) SATISFIED)

**2026-08-07 supersession note:** The historical re-mint consequence later
superseded by D-117 is retained unchanged as historical context. Current
rule ownership: D-117.

**Date:** 2026-08-06 (Fable magistrate, overnight; issuance pre-authorized by Ed 2026-08-05 conditional on the gate passing).
**Status:** EXECUTED. This retires the schema fixture and issues the authoritative calibration acceptance artifact — the anchor all future floor-mint claims authenticate against. D-110 re-mint condition (b) ("R2 backfill verified, ledger bootstrapped, head pinned") is now SATISFIED; (a) was satisfied by PR #100, (c) by PR #105. **MINT-GENERALIZE-01 is UNBLOCKED for the re-mint.**

**What was written.**
- `runs/calibration_observation_ledger.jsonl` — the 76-receipt genesis historical-import chain (git-ignored local custody artifact, sha256 `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`; deterministic from the custodied inputs below + the raw evidence; MUST be backed up per the runbook before the re-mint consumes it).
- `configs/calibration/calibration_ledger_head.json` — the repo-committed head pin (sequence 76, head_digest `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`), the D-109 R1.4 anti-rollback trust anchor.
- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
- Reproducibility inputs custodied at `docs/process_traces/2026-08-06-d079-issuance-coldgate/` (disposition table sha `5da820aa…`, custody manifest sha `99cbf3df…`, execute summary, ledger sha).

**Disposition inventory (B1 lead-ruled).** 30 valid / 2 systematic-invalid / 6 ordinary-invalid. The two systematic-invalid members (`20260726T000039-491995f3`, `20260801T064830-c76f5d1c`) have bounds `0.035435840879704805` / `0.0350400833260715`, both exceeding the ratified pre-flight screen `0.033558756679900`; D-102 (§~6298) explicitly names the first a systematic failure "never budgetable." R2.8 counting: 30 valid < 38 threshold, so issuance does NOT itself trigger corpus-doubling re-derivation (eight further valid same-epoch observations would; R2.8's literal "six further" was conditioned on the superseded 32-valid candidate). derivation_corpus preserved byte-identical at n=19 (its fixture whole-core digest was `3cece3b2…`; that value is NOT carried into the issued artifact — embedding it would fail the loader). All 38 custody locators are iCloud-backup copies (raw evidence is git-ignored by repo convention; integrity rests on the committed hash chain, not the custody pointer).

**Window-B completeness note (soundness-critical, for any reviewer asking "why Window-B in the anchor?").** The `prior_observation_set` correctly includes 6 `window_metrologyB` **calibration fiducial** observations (2 valid: `e0ce33f5`, `8c3bfe9e`), as mandated by D-109 R2.3/R2.8 completeness (every content-distinct governed CALIBRATION observation). This is NOT a D-113 violation: D-113 retired Window B's WINDOW CLAIM consumption (its null-ladder/additivity science members), not the calibration fiducials collected in that period; the general calibration machinery survives per D-113. These fiducials are EXCLUDED from the frozen n=19 threshold basis (which is Window-A-only) and do not influence the bound.

**Gate history (the process earned its keep on the anchor).** Two rule-11 cold gates. Cold gate #1 (on the plan) HELD correctly — the naive JSON-edit plan had no issued-artifact consumer (F1) and would have invalidated the whole-core digest (F2). That forced a real consumer implementation, which then ran the full C-028 gauntlet: adversarial audit (consumer proven false-ACCEPT-resistant; 3 emission/execute blockers incl. ledger-commit-BEFORE-artifact-validation) → fix → delta (exit-3 masking) → fix → final delta ACCEPT. Cold gate #2 (on the exact bytes): both lenses PROCEED on CONTENT (head/dispositions/B1/R2 all independently reproduced); HOLD on sequencing only — the consumer had to land on main before writing the issued artifact, else the anchor bricks. Resolved by merging PR #108 first, then executing against consumer-present main, with the co-landing verification (`_valid_acceptance_bound(issued)=True`) confirmed post-write. Full records: `docs/process_traces/2026-08-06-d079-issuance-coldgate/`.

**Consequences.** MINT-GENERALIZE-01 (b) satisfied; the re-mint (a10 extraction + mint #1 re-derivation under the corrected selector, embedding the D-102 pin-3 never-zero drift allowance) is the next step — the path to a non-empty claims table. The runs/ ledger must be custody-backed before the re-mint consumes it.

## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired

**Date:** 2026-08-07 (Ed directive, in-thread; transcribed by the Fable
magistrate. Ed, verbatim: "if i recall for a paper ready at the quality
needed we need 3 more machine quiet nights and a lot of desk work",
with an explicit go to "execute all the deskwork" — read together with
his 2026-08-06 in-thread MVP-scope directive "a little more than just
decode, at least decode/prefill". His ruling moots a cold gate: apex
authority per rule 11.)
**Status:** ADOPTED. Full technical record:
`docs/process_traces/2026-08-06-d110-remint-fork/` (DIAGNOSIS: the
structural closure live-reproduced at `c537386`; Sol xhigh consult run
`20260806T165843Z-10884`; SYNTHESIS: magistrate concurrence).

1. **The D-110 clause-3 re-mint order (historical a10 consumption under
   the corrected selector) is SUPERSEDED.** The issued ledger holds only
   import-marked receipts; candidate discovery excludes imports by
   design; future live receipts cannot causally bracket past windows.
   The order is structurally unsatisfiable at main, not merely
   inconvenient. D-110's OTHER holdings STAND untouched: mint #1 and
   derivatives remain non-claim-bearing, and the never-zero
   `A_s = max(observed_drift_s, 0.010818)` allowance (D-102 pin 3)
   BINDS every mint under this entry.
2. **Replacement: three compact prospective claim windows** — fresh
   1.5B decode floor, fresh 7B decode floor, fresh 1.5B-vs-7B contrast
   — each with fresh §5A, live pre/post calibration receipts appended
   to the issued ledger, own verdict + head-pin + custody. Claims
   chain: historical corpus → issued D-079 acceptance rule → live
   brackets → prospective floors → prospective contrast. Honest
   framing preserved from the consult: historical data establish the
   RULE; live receipts bracket all claim-bearing science.
3. **Scope (Ed's decode/prefill directive):** prefill FLOOR cells ride
   both floor windows (cheap, same members' prefill phase). The model
   contrast is DECODE-ONLY by default: the 2026-08-07 desk feasibility
   check (`docs/process_traces/2026-08-07-prefill-feasibility/`) found
   the 128-token prefill contrast MARGINAL against the effective bar
   (interval overlaps it). A prospectively frozen ≥256-token prefill
   contrast arm remains an OPEN ED OPTION (estimand change +
   ~110 core minutes, likely its own window) — not adopted here.
4. **D-113 rewire:** its readiness dependency on the historical re-mint
   completing is REMOVED. The three-window P1 closure PRECEDES the
   broader MET-WINDOW-C-01 C2/C4/C5 replacement campaign (grounds:
   Ed's paper-first priority stack, 2026-08-06).
5. **Naming:** "Window D" is unavailable (collides with
   `runs_window_d_20260726` and D-113's reserved terminology); the
   three windows receive new immutable plan/root identifiers at plan
   freeze.
6. **Option 1 (finite-allowlist historical candidacy) is PRESERVED as
   a versioned contingency ONLY**, requiring a rule-11 cold gate before
   any implementation (semantics sketch: consult response §3). The
   historical corpora remain untouched on disk, non-claim-bearing per
   D-110 cl.1, logs sha-verified.
7. **Unblocked desk queue** (consult §4): freeze three window plans +
   budgets; 1.5B decode floor plan from the proven 10-absolute/40-null
   design; generalized mint pinsets with per-plan six-decimal literals
   (the D-084 hard literal `7.377086` refuses any corrected mint under
   every option — closure is per-plan supply via the generalized path);
   extraction specs / order manifests / evidence-root ids / contrast
   manifest; synthetic three-window live-ledger integration regression;
   D-102 successor-artifact packet; results/methods prose placeholders.

## D-118: NOTHING APPROACHES MERGE WITHOUT THE FULL COUNCIL — the merge gate is enumerated and mechanically checked (Ed directive)

**Date:** 2026-08-07 (Ed, in-thread, verbatim: "make sure they get a
comprehensive fable pass, and make sure NOTHING gets near merge status
ever again without the full council..."). **Status:** RATIFIED — apex
authority; binds every future session and every agent role.

**Trigger (recorded honestly):** three D-117 units (PRs #111/#112/#113)
merged the same day after a strong but INCOMPLETE gate. They received
paired audit lenses, lead-written FIX contracts, fix rounds, delta
re-audits, second fix rounds, second deltas, lead-replayed full suites,
and green CI. They did NOT receive: (a) the apex Fable diff gate — the
magistrate substituted test evidence and spot-checks for reading ~9,200
merged insertions; (b) the mandatory overbuild/merge-ability prune lens
(Ed's own standing addition); (c) Opus counter-review, which Ed had
explicitly asked to be in the instrument mix; and (d) for U4, the
final-head rule — its L5 fix landed after its delta and was merged with
no fresh pass. Gaps (a)-(d) were self-reported by the magistrate on Ed's
direct question, then closed retroactively.

**THE GATE (all of it, every time; no item is discretionary):**

1. **Independent audit** of the implementation by a fresh reviewer that
   did not write it. Never self-graded.
2. **PAIRED LENSES, distinct angles** — minimum contract + execution.
   Measurement-adjacent work adds the physics/causality lens.
3. **Lead-written FIX contract** with dictated closure shapes; findings
   are triaged and dispositioned, never silently applied.
4. **DELTA RE-AUDIT of every fix round** — fix rounds introduce defects;
   this project has proven it repeatedly, including twice on 2026-08-07,
   where BOTH units' original defect classes survived round one in new
   forms and only the delta caught them.
5. **Same-signature statement required** from every delta. A surviving
   class fires the escalation trigger: the next spend is a consult, not
   another fix round.
6. **OPUS COUNTER-REVIEW** on the near-final head — cross-model
   diversity, not a second Sol pass.
7. **APEX FABLE DIFF GATE** — a Fable-class judgment pass that READS THE
   CODE and answers design-level questions (is this the right shape or a
   workaround frozen into a contract; would a maintainer want to own it).
   **This MAY be delegated to Fable subagents** (Ed, same exchange:
   "you can delegate fable missions to other instances of fable") — the
   magistrate owns the ADJUDICATION of their findings, not the reading.
   What may never happen is the gate being skipped or downgraded to a
   cheaper model tier.
8. **OVERBUILD / MERGE-ABILITY PRUNE** — "would I want to maintain this
   diff"; surplus abstraction and test bloat are pruned BEFORE merge, as
   no downstream layer re-asks it.
9. **Lead full-suite replay, unpiped, on the INTEGRATION tree** (not the
   stale branch), with the exact tail recorded.
10. **FINAL-HEAD RULE** — any commit landing after the last review round
    gets one more fresh-eyes pass before merge, however small. No
    exceptions; this rule previously caught a live crash path here.
11. **CI green on the final head**, and for a multi-unit wave, a
    **post-merge cross-unit integration review** hunting interaction
    defects no isolated layer can see.

**Mechanical enforcement (so this is not memory-dependent):** every PR
description must carry a GATE LEDGER listing items 1-11 with the
evidence path or commit for each, and any item marked NOT-RUN blocks the
merge. A PR without a complete gate ledger is not merge-eligible
regardless of CI state. The D-072 self-merge authority is CONDITIONED on
this ledger being complete — it was never a license to merge on green
alone.

**Scope note:** a burn/liberal-delegation license (Ed, 2026-08-07)
increases the volume of work fed INTO this gate. It never reduces the
gate. If throughput and gate completeness conflict, throughput yields.

## D-119: Claim-LANGUAGE rulings delegated to the magistrate, conservative-by-default, until Ed joins the draft loop

**Date:** 2026-08-07 (Ed, in-thread, after the operator-attested
adjudication: "it's a language issue not a software/hardware issue. yeah
rule conservative on those, fable i trust you to rule on that for now
until i start being in the loop on drafts"). **Status:** RATIFIED.

**What is delegated.** How a claim is WORDED — the strength of a
provenance/custody statement, whether a result is described as
demonstrated vs designed, how a limitation is framed, which verb a
guarantee gets. The magistrate rules these directly and records them,
without waiting on Ed.

**The standing rule for those rulings: CONSERVATIVE BY DEFAULT.** When
two honest phrasings are available, take the weaker one. An overclaim in
front of a metrology-expert advisor costs credibility that is expensive
to rebuy; an underclaim costs a sentence. Where a stronger phrasing is
actually warranted by evidence, it may be used — but the evidence is
named in the same breath.

**What is NOT delegated** (unchanged, still Ed's): what to MEASURE, what
to fund with quiet nights, scope decisions, venue and calendar, anything
irreversible, and any ruling that changes what the project claims to
have DONE rather than how it says it.

**Boundary case that prompted this:** the floor artifact's custody
statement. The finding was that the paper implied third-party
verifiability where the system provides tamper-evidence within a
single-operator trust model. No measurement, instrument, calibration, or
datum was affected — the fix was wording. That class is now magistrate
territory.

**Termination:** this delegation ends when Ed begins reviewing drafts
directly. He may reverse any ruling at any time; none of them bind him.


## D-120: D117-POSTCOLLECTION-TRUST-01 — the postcollection trust closure (adopted consult design, executed)

**Date:** 2026-08-07. **Status:** ADOPTED (design), EXECUTED on
`impl/d117-postcollection-trust` (merge gated by D-118).

**The defect class (three prior relocations):** the v2 generalized mint
authenticated postcollection custody pins against
`component.report["floor_mint_postcollection"]` — a block nothing in
production emits, so in production both the pins and their "authority"
would be authored by the same operator hand. Rounds 1-3 each moved the
trust boundary down a level without terminating it (fabricated-hash
mint; presence-only check; per-field equality against the same
operator-authored block).

**The adopted shape (binding design memo: final block of
`docs/process_traces/2026-08-07-d117-u-units/ESCALATION-CONSULT-RESPONSE.md`):**
1. `floor_mint_postcollection` is DELETED from production and fixture
   vocabulary; no producer is assigned; a report containing it (or any
   unknown key) REFUSES under a closed D-117 mint-consumption profile.
2. The mint verifies every pin against its DOMAIN OWNER and treats the
   extraction report as a cache requiring reauthentication, never an
   oracle. Verifier calculation is mandatory; pin generation is
   forbidden (missing pins refuse).
3. The mint derives project commit/tree state by running git itself and
   refuses a dirty tree; origin/main containment of the mint commit is
   recorded evidence (unknown tolerated, never a gate).
4. Every v2 artifact carries the REQUIRED assurance qualifier
   (`single_authority_hash_bound_replay.v1`, independent_attestation
   false) stating what the system establishes and does not establish.
5. The honest trust claim is single-authority, hash-bound, fail-closed
   consistency — never operator independence (ADJUDICATION-TRUST-MODEL.md
   controls; the paper's §5/§11 language updated in the same change).

**Consequence:** the v2 mint remains BARRED from issuing until the
executing branch passes the full D-118 gate and merges; U10 depends on
this entry.


## D-121: The magistrate's contextual final review is the terminal merge-gate item (Ed directive; amends D-118)

**Date:** 2026-08-08 (Ed, in-thread: "fable should do a final review of
everything that is gonna touch main after every other pass. with
relevant context"). **Status:** RATIFIED. Ed's ruling moots the rule-11
cold gate on process amendments.

**The rule.** Nothing merges to main until the magistrate (the directing
Fable instance) has personally reviewed the exact merge candidate — the
final head, its full diff, and its completed gate ledger — AFTER every
other gate item has finished. This review is:
1. **Terminal:** it is D-118 item 12, sequenced strictly after items
   1-11 (including CI). A fix landing after it re-triggers it (the
   final-head rule composes: any new commit restarts at item 4's delta
   and ends at item 12 again).
2. **Contextual, by design:** unlike cold gates and fresh subagent
   passes (which exist to remove loop context), this slot exists to
   apply it — the magistrate reads the candidate knowing the session's
   escalations, adjudications, deferred items, and cross-branch state
   that no fresh reviewer holds.
3. **Non-delegable:** delegated Fable subagent diff/final-head passes
   remain valid as EARLIER ledger items; they never satisfy item 12.
   The magistrate adjudicates and signs the ledger.

**Why (the session evidence that prompted it):** on 2026-08-07 the
apex-delegable reading let merges complete where the magistrate's own
last-look happened mid-gauntlet rather than last; separately, a
counter-review caught a branch falsifying a PAPER sentence — a
cross-surface fact only context-holding review reliably connects. The
terminal slot puts the accountable reviewer at the accountable moment.

**Ledger form:** item 12 reads "Magistrate final review — <head sha>,
<verdict>, <one-line disposition of any deferred items>."


## D-122: Prefill contrast IN SCOPE — 256-token prospectively frozen arm on gamma (Ed ruling 4)

**Date:** 2026-08-08 (Ed, in-thread: the small-prefill measurability
problem is answered by sizing up the workloads; "I don't want a decode
only paper/scope if at all possible"). **Status:** RATIFIED. Reverses
the adjudication's RECOMMEND-no; Ed's apex authority controls.

**Evidence basis (labelled NON-CLAIM sizing scout,
docs/process_traces/2026-08-07-prefill-feasibility/):** at the
historical 128-token prompt the best ABBA estimate of the 7B-1.5B
prefill delta is 5.809930 J against the ~5 J practical bar (D-078/D-083
composition) — 16% point headroom with the diagnostic interval's lower
side below the bar: MARGINAL. Proportional sensitivity for a 256-token
prompt projects ~11.619860 J, comfortably clear. No historical 7B
corpus above 128 prompt tokens exists, so 256-tok is a sizing
projection, not demonstrated evidence — which is acceptable because the
arm is PROSPECTIVELY FROZEN and the claim machinery fails closed.

**Consequences:**
1. Gamma's campaign pack gains a 256-token prefill ABBA arm (frozen
   prompt, frozen member/minute budget — lands in the U7 pack under the
   adopted stage_launch.v1 contract). Night budget grows; the operator
   packet states the new duration.
2. Prefill FLOOR cells continue to ride alpha/beta unchanged (D-117).
3. If the collected contrast lands below the decision bar, the verdict
   refuses per doctrine and the marginality analysis publishes as
   prospective sizing evidence — never a quiet omission.
4. The D-117 clause "contrast decode-only by default; 256-tok arm stays
   Ed's option" is SUPERSEDED by this exercise of that option.


## D-123: Ruling 2 YES + the signal-size doctrine + the overnight license (Ed, 2026-08-08)

**Date:** 2026-08-08, in-thread, Ed's last exchange before an ~12h
autonomous overnight window. **Status:** RATIFIED.

1. **Reported-energy cells: YES.** The alpha/beta packs pre-register
   reader-facing phase-energy means alongside the floor cells — same 50
   members, zero added collection — conditional on the pack-gate check
   proving the addition leaves every floor computation byte-identical.
   Ed's framing accepted: what freezes is the PROCEDURE (measurand +
   reduction method), never the number; exploration stays allowed and
   labelled.
2. **Signal-size doctrine (standing preference).** Ed: making the
   workload bigger is "basically free to the instrument" — the
   legitimate knob against the fixed ~1 J attribution blur is effect
   size, not averaging. Apply wherever free: D-122's 256-token prefill
   arm is the first exercise; future designs default to sized-up
   signals unless sizing destabilizes a proven design or breaks
   comparability with pinned claims.
3. **Attribution debate ordered.** A bounded Sol consult on whether
   phase ATTRIBUTION itself can be improved within the ruled instrument
   scope (no instrument-improvement program). If the answer is "no
   headroom beyond signal sizing," that is recorded and the question
   closes.
4. **Overnight license.** ~12h autonomous; goal "keep working until
   you've got a defensible paper"; Sol liberal on fast tier; the
   magistrate (Fable) oversees — D-121 terminal reviews bind every
   merge; Opus lenses continue ("other eyes never hurt").


## D-124: Common-mode contrast estimator — promoted as the registered candidate (two-shared-edge form)

**Date:** 2026-08-08 overnight (magistrate adjudication under the D-123
license; Ed-reversible, flagged for morning). **Trigger:** Ed's
attribution debate (D-123 item 3) -> adopted memo -> ordered replay.

**Evidence (NON-CLAIM, custodied at
docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md):**
on the exact a5 decode ABBA corpus under CURRENT issued semantics, the
worst-case-sum default composes an 8.611855 J comparative floor; the
common-mode joint sweep gives 1.632422 J; the more faithful
two-shared-edge variant 1.869502 J. The promotion bar (>=2x or >=2 J)
holds by every variant. Material for D-117: the prefill contrast's
~11.6 J projected signal is thin against an 8.6 J-class worst-case
floor and comfortable against a ~1.9 J-class common-mode floor.

**What is promoted:** the TWO-SHARED-EDGE estimator (the replay's own
soundness objection to the 1-D shared-shift form is sustained). It is a
CANDIDATE until its implementing unit lands through the full gate and
its identity is pre-registered in the D-117 pack bytes; if either
fails, contrasts fall back to the worst-case default and the paper says
so.

**Registration conditions (all bind):** named estimator identity;
named block-timescale stationarity/transfer assumption WITH the
bracket-calibration evidence (onset/offset spans) and its honest limit
(the historical corpus records bounds, not realized member-level
errors) carried into the paper's limitations; pre-registration before
any claim-bearing data; identical covariance treatment on calibration
floor blocks and the consuming science contrast; D-102 never-zero
allowance applied exactly once inside the shared operative bound; full
D-118/D-121 gate on the implementing unit; the issued acceptance
artifact is not reopened and no raw calibration corpus is voided.

**Sequencing:** the implementing unit rides AFTER the trust branch
merges (shared floor_extraction/estimator surface) and BEFORE pack
freeze (the packs name the estimator identity). FLOOR-COMMONMODE-01's
kernel row sharpens to this form.

### D-124 amendment — 2026-08-10: strict-noncollapse domain (magistrate, post-escalation consult; flagged for Ed's review)

The implementing unit's D-118 gauntlet found the two-shared-edge sweep
UNDERSTATING the floor in two successive formulations (missing per-edge
breakpoints; then separable composition failing when a joint edge shift can
collapse a member window shorter than twice the shared bound). Per the
standing escalation trigger the second recurrence went to a design consult,
whose terminating design is ADOPTED: the estimator is **exact on a registered
strict-noncollapse domain and refuses outside it**. Every admitted A1/B1/B2/A2
member window must prove, with outward float rounding
(`nextafter(start+B) < nextafter(end-B)`), that no joint shift within the
authenticated bound B can collapse it; geometry outside the domain refuses
with the typed reason `common_mode_nonseparable_window_domain` and is never
estimated (no silent fallback — a cell not registered for this estimator uses
the worst-case composition and says so). Composed extrema carry an outward
numerical enclosure so float summation direction cannot reopen an
understatement route; the reportable floor value is unchanged at 1.869502 J
while its trailing ulps move upward. The registered parameter dict now pins
`shared_extrema_rule =
separable_onset_offset_exact_sweep_on_strict_noncollapse_domain`, the domain
precondition, and the refusal reason, so `COMMON_MODE_PARAMETER_SHA256`
CHANGES and the previous registration object fails validation (permitted: the
registration was still a pending candidate; packs are unfrozen). Current
claim-path geometries sit safely inside the domain (decode windows
seconds-scale; measured 1.5B p128 prefill windows 0.121-0.147 s vs the
0.0736 s collapse threshold); Q8 p256 evidence will be checked at collection,
not inferred. The paper's limitations carry the applicability limit. Consult
record: the FCM-01 escalation consult (T4 session, custodied with the run
artifacts); refuter evidence: executed 0.25 J (breakpoints) and 1.06 J
(collapse geometry) understatements on synthetic corpora.

**Erratum (2026-08-10, cold-gate ruling + paired refuter):** the sentences
"exact on the registered strict-noncollapse domain" and the
enclosure-prevents-understatement claim were incorrect as written —
falsified by the round-2 audit (emitted width below the exact admissible
width by up to 2.3e-13 J at ~1000 J member scale; structural component of
the shortfall proven EXACTLY ZERO by rational-arithmetic probes on both
adjudication sides). Corrected statement, as further qualified by the FCM-R4
input-surface tolerance audit below: over inputs constructed by the registered
builder from authenticated bundle evidence, the emitted width bounds the exact
admissible width outward, up to the disclosed member-envelope pad and the
disclosed zero-point discrepancy term, under the documented single-sourcing
assumptions for the bracket bounds. Under those assumptions, the total
overstatement against the exact about-zero bar is capped by the member-envelope
pad, the zero-point discrepancy term, and directed-rounding slack. As first
implemented (bbf7bdd) the enclosure was scaled to the contrast magnitude
and did not dominate member-scale float error; it is now scaled to the
member-integrand envelope and registered in the parameter dict (sha
rotates once). The earlier "current claim-path geometries sit safely inside
the domain" sentence overstated the evidence: only the a5 decode root has
collected evidence (committed inventory records its margin); the remaining
referenced roots including Q8 p256 have none yet and are asserted
absent-by-name in the committed inventory; margins are a freeze-gate
checklist item at collection.

### D-124 amendment — 2026-08-10: FCM-R4 explicit zero point, third erratum, and input-surface tolerance audit (cold-gate FINAL)

FCM-R3-01 falsified the prior errata's unconditional upper-bound sentences:
an input admitted by every coded precondition emitted
`0.09999999950000743 J` against an exact required
`0.10000000050000024 J`, an understatement of approximately
`9.9999e-10 J`. The defect had been present since the original implementation:
the sweeps' structural zero-shift contrast was recovered by `isclose` against
the separately reduced ABBA delta, conflating tolerance with identity. Those
unconditional sentences are superseded.

Round 4 makes the zero-shift contrast `z` an explicit registered input. It must
be present by exact equality in both onset and offset sweeps. Extrema are
composed as signed excursions about `z`; the emitted shared half-width adds
`|z - delta|` outward exactly once, separately from the unchanged
`64u * S_env` member-envelope pad, whose floored scale set now includes
`|z|`. A mismatch outside the existing `isclose(rel_tol=1e-9,
abs_tol=1e-12)` band refuses with
`common_mode_zero_point_divergence_out_of_domain`; this is a pure provenance
guard and is not load-bearing for soundness. The intuitive round-3 arithmetic
plus `|z-delta|` candidate was tried and refuted: it fails the independent
about-zero exact bar on FCM-R3-01 and remains a named negative regression.
Real trimmed recompute fixtures for a5 decode blocks b02 (nonzero measured
divergence) and b01 (zero divergence) are committed under
`tests/fixtures/fcm_r4_real_blocks/` within the 256 KB cap.

The registered parameter hash is
`4d1c544fe3a52148c7d379f4c50ade4ac3b64211d817cd1438a2365973291981`.
All superseded hashes (`ea4aa669...`, `9d964cfb...`, and `977189cd...`) are
rejected by regression.

**FCM-R4 input-surface tolerance audit.** These are the complete tolerance
acceptances on the registered arithmetic path. The production caller
single-sourcing statements are assumptions of the upper-bound claim; direct
callers must preserve them.

| Accepted comparison | Coded tolerance | Production single source / caller assumption | Disposition |
|---|---:|---|---|
| Sweep bound vs authenticated operative bracket bound | `rel=0`, `abs=1e-12 s` | `extract_comparative_cell` obtains `common_mode_bound_s` once from `registered_common_mode_operative_bound` and passes that exact float unchanged to the sweep builder and estimator; the authenticated session alias is checked against the same value. | No discrepancy term: production is exactly single-sourced. Direct callers assume the same identity. |
| `b_fiducial_s` vs optional `operative_b_fiducial_s` alias | `rel=0`, `abs=1e-12 s` | When both exist, arithmetic selects `b_fiducial_s`; the optional alias is redundant provenance and never supplies sweep arithmetic. | No discrepancy term: the tolerated alias is non-operative. |
| Recorded allowance string vs passed `calibration_drift_allowance_s` | `rel=0`, `abs=1e-12 s` | Production bracket construction computes one Decimal allowance, then emits its exact decimal string and binary64 projection together; arithmetic uses the binary64 field. | No discrepancy term under the single-producing-value assumption. |
| Operative bound vs endpoint plus allowance | `rel=0`, `abs=1e-12 s` | Production bracket construction computes `operative_bound = endpoint_max_decimal + allowance` once in Decimal and emits its binary64 projection as `b_fiducial_s`; the separate endpoint/allowance fields are audit projections of the same derivation. | No discrepancy term under the production-constructor assumption; externally assembled brackets assume the same derivation. |

Claims-with-assumptions correction: **over inputs constructed by the registered
builder from authenticated bundle evidence, the emitted width bounds the exact
admissible width outward, up to the disclosed member-envelope pad and the
disclosed zero-point discrepancy term, under the documented single-sourcing
assumptions for the bracket bounds in the audit table above.**
No published replay number changes; the six-decimal value remains
`1.869502 J`.


## D-125: Ed's morning ratification batch — D-124 signed off, lineage envelopes ratified, D-117 cl.1 amended for successors, the 40-hour window

**Date:** 2026-08-08 morning. **Status:** RATIFIED (Ed, in-thread).

1. **D-124 signed off.** Ed's condition ("if instrument gets better")
   is exactly the property: the two-shared-edge common-mode estimator
   tightens comparative floors 4-5x on repo-demonstrated evidence, under
   the full registration conditions of D-124. FLOOR-COMMONMODE-01's
   implementation must land through the full gate BEFORE pack freeze so
   the estimator identity pre-registers in pack bytes.
2. **Q1+Q13 envelope adoption ratified on trust.** Magistrate
   clarification recorded: this governs SUCCESSOR calibration-acceptance
   arithmetic (drift screen + budget ceiling derivation), not workload
   profiles; screens/ceilings become lineage-monotone t-family envelopes
   inheriting the genesis screen 0.010818 as a lower bound — the
   allowance can only strengthen. With Ed's ratification the consult's
   transcription condition is met: **D-117 clause 1 is AMENDED for
   successor artifacts** from "every mint uses max(drift, 0.010818)" to
   "genesis lower bound + lineage-envelope rule"; the genesis literal
   remains binding as the floor and for every mint under the issued
   artifact. Freeze-until-ruled ends.
3. **The 40-hour window.** Ed grants ~40 continuous hours including
   quiet-window nights (Ed available for §5A arm/disarm taps). The plan
   of record is `docs/strategy/2026-08-08-40h-plan.md`; RUN_STATE points
   to it as the resume script across /clear.

## D-126: U2 second convening — synthesis of record; COLD-GATE-U2-PENDING resolves to this entry

**Date:** 2026-08-08. **Status:** ADOPTED (magistrate transcription of
the sealed second convening; both judges' rulings custodied at
`docs/process_traces/2026-08-07-u2-coldgate/`).

1. **Outcome.** Partial ratification + one joint remand, per
   SYNTHESIS-V2.md: six first-round objections verified moot in the
   exhibit's bytes by both sealed judges (Q2 observed-max screen, Q4
   one-way door, Q6 abandoned-brick, Q7 bare-None loader, Q9
   unbarriered publication, Q11 fabricated successor_probe).
2. **Ratified with binding amendments:** Q2; Q4 (plus the two-site
   freeze test obligation on `_SUPPORTED_COUNT_BOUNDARY_RULES` and its
   recompute branch); Q5 (the cold judge's closure definition is
   BINDING — an observation ceases to be "new" only via an explicit
   decision-log disposition by content_id plus the next successor's
   prior_observation_set recording the disposing decision ID; consuming
   code lands with the first disposing ruling, not before); Q6; Q7; Q8
   (registry authority ratified; the migration shim DELETED by
   convergent ruling — `_load_registry_for_current_active_selection`
   collapses to the plain committed load); Q9 (strict with the shim
   gone); Q11; the Q13 n>=19 licensing floor.
3. **Q1+Q13 joint remand: RESOLVED** by the lineage-monotone envelope
   design (Q1Q13-REMAND-CONSULT.md), ratified by Ed as D-125. The
   silent clamp is removed; issuance refuses
   `successor_screen_exceeds_budget_ceiling` when screen >= ceiling;
   cap = ceiling − screen with no max(0,·); runtime classification and
   record fields per consult §6.
4. **Q12 OPEN** pending re-presentation on the FULL register text.
   Packet rule hardened (second occurrence of the truncation class):
   register/finding quotes run to END OF DOCUMENT SECTION, never to an
   assembler-chosen paragraph boundary.
5. **Q10 DEFERRED** to the recovery gate; the exception may not be
   exercised on a live night before the predicate re-verifies on the
   ledger-resident substrate.
6. **Cross-cutting:** CH-1 (writer copied-scalar unit) deadline is
   before the first successor issuance or any live night relying on
   writer dispositions, whichever comes first. The U2 landing gauntlet
   REQUIRES a writer≠reviewer lens over the 965-line successor test
   surface (torn-publication, rollback, durability-uncertain,
   receipt-authentication paths). No successor can issue until rework
   round 2 + the remand resolution + the landing gauntlet + CH-1 have
   all landed.
7. **Tuple rule:** this decision ID replaces `COLD-GATE-U2-PENDING`;
   an issued artifact may never embed a tuple member with no
   decision-log entry.

## D-127: Autonomous window loop chartered — scoped time-toggle + verified relaunch harness (partial D-114 reversal)

**Date:** 2026-08-08 (Ed, in-thread during the 40h window). **Status:**
RATIFIED by D-128 (build authorized; install gated; initially CHARTERED).

1. **What Ed authorized.** Claude Code drives the full experiment loop
   across multi-day unattended stretches: harvest → mint → judge →
   build/freeze next pack → toggle network time off → launch the
   supervisor → EXIT for the capture; the window's final step relaunches
   a fresh headless session. Ed's involvement reduces to optionally
   remote, or zero once the toggle lands.
2. **Zero-agent during capture is UNCHANGED.** The agent fully exits for
   the ~3h capture; this charter removes the human toggle and the
   relaunch gap, not the contamination fence. (The dormant-app
   characterization number becomes moot for this design — full exit,
   not residency.)
3. **Scoped toggle.** Sudoers rule for exactly the two fixed
   systemsetup network-time commands (exact path, exact argv, no
   wildcards). Honest risk register: worst-case abuse is TIME
   MANIPULATION, which for this project is a measurement-integrity
   vector (clock anchors, drift screens) — detectable by the existing
   custody/drift chain; not a general-privilege surface. D-115's
   install conditions bind (sudo -k fresh auth; authenticated staged
   content; interpreter isolation); Ed personally runs the single sudo
   install command after the artifacts clear their gauntlet.
4. **Relaunch harness (Ed's design point, corrected for process
   lifecycle).** No pre-existing process to check — each cycle launches
   fresh. Shape: preflight (binary, auth, disk state) → launch →
   liveness proof (the fresh session's first scripted action writes a
   heartbeat/claim file; launcher stands down only on proof) → bounded
   retries with backoff → independent launchd fallback timer as the
   second wake layer. Never one mechanism.
5. **Process.** Security-critical: pre-decision design consult, full
   D-118 gauntlet, D-121 terminal review; own branch/worktree, OFF the
   night-critical path (trust/recovery merges outrank it); D-114's
   remaining descopes (t3-resident, T3-CHAR-PAIR, WO-T3-VIS, SEC5A
   remote) stay descoped except as this charter names.

## D-128: Standing run-the-loop mandate — drive until the paper is defensible

**Date:** 2026-08-08 (Ed, in-thread: "i want you running this
project/loop until you've got a defensible paper"). **Status:**
RATIFIED. Also ratifies D-127 (chartered → ratified).

1. **The mandate.** The magistrate owns continuous operation of the
   experiment loop and the project: pack building, window arming (via
   D-127 once landed; via Ed's §5A taps until then), morning harvests,
   verdicts, mints, refusal diagnosis, re-arm decisions, desk analysis,
   and paper assembly — across sessions and days, without per-step
   authorization, until the paper is DEFENSIBLE.
2. **"Defensible" is the bar, and it is conservative:** the P1 MVP
   paper carrying measured numbers whose every claim survives the
   adjudicated trust model, the results-prose acceptance contract
   (template landed 1e6fa16), D-119 conservative wording, and the
   D-078 attribution-limited floors doctrine. Defensible to advisor
   Rivoire's metrology bar, not merely internally green.
3. **Unchanged fences (this mandate relaxes NOTHING):** zero-agent
   capture; the full D-118 gate + D-121 terminal review on every
   merge; standing same-signature escalation and cold-gate triggers
   (U2's count-3 freeze stands as precedent); the lieutenant-forbidden
   list; Ed's owed rulings (Window-C funding, ruling 8 spec
   governance, wall-meter/artifact scope) remain his; any external
   claim release or publication remains Ed-gated.
4. **Morning surface.** Each cycle leaves Ed a one-page morning state
   (what ran, what minted or refused and why, what the next night
   does, anything parked awaiting him) — RUN_STATE stays the pointer.

## D-129: Ed operating directives batch — fan-out standing, fast-tier cut, Fable economy with full coverage

Transcribed from Ed's in-thread directives during the T3 session
(2026-08-09 day). Three linked operating rules, all process-level; no
measurement, claim, or trust-model semantics change.

1. **Standing fan-out order.** Fan-out to the degree demonstrated in T3
   (~8 concurrent streams: Sol implementation/diagnosis lanes in disjoint
   worktrees, Opus grader+refuter Workflow fleets, an Opus-directed sweep,
   local suite gates, CI) is the DEFAULT whenever it speeds work — not a
   per-session grant. Queue only on genuine file/invariant collisions or
   gate dependencies. Extends the 2026-08-02 Workflow standing permission
   and the T1 harder-parallelism directive from prompted to standing. It
   also covers H1/H2 preparation work when the H0 lanes are saturated (the
   extension-axes roadmap draft is the first artifact of that license).
2. **Codex service tier.** Fast-tier usage drops by roughly 60%. Default
   tier is the norm; the wrappers' 2026-08-08 fast-standing-default is
   superseded (their env default may lag — override per call with
   `CODEX_SERVICE_TIER=default`). Fast is reserved for the single run whose
   wall-clock directly gates the session's merge or milestone, and depth is
   consolidated (one xhigh run) rather than multiplied (several fast highs).
3. **Fable token economy, coverage unreduced.** Orchestration and
   direction work (bridge ceremony, launch/poll/harvest, envelope
   validation, packet assembly, lead-check replay) runs on Opus 5 high
   subagents; Sol remains the execution workhorse. Fable's non-delegable
   reserve: adjudication and rulings, security classifications, D-121
   terminal reviews, final live verification (hard rule 1), escalation and
   stop decisions, and Ed communication. Ed's explicit rider: **coverage is
   not reduced** — Fable still personally full-audits anything important or
   claim-bearing (claim artifacts, trust/security surfaces, merge diffs,
   published numbers), reading the primary artifacts; the savings come from
   delegating ceremony, never from thinning or skipping a Fable review.
   This amends the operative "stream director is now the exception"
   framing in `docs/orchestration.md` (the C-009/C-010 stamped council
   consensus remains in place as the dated record it is); Opus-directed
   Sol lanes are now the standing default shape.

## D-130: Decisive-run venue — substance over venue, fenced to PR 122

**Date:** 2026-08-11. **Trigger:** the `d117-production-proof` workflow's
decisive step was cancelled at the exact 360-minute GitHub-hosted platform
cap twice at head e871f5b (count 2 of the timeout signature); the standing
escalation trigger routed the question to a cold gate, mandatory in any case
as a verdict-authority reinterpretation.

**Ruling (cold gate, disposition (a); paired contract-lens refuter CONCURS):**
decisive authority for the PR #122 merge is re-seated to the lead local
decisive execution at e871f5b (2026-08-10T21:16:58Z → 2026-08-11T00:52:37Z,
rc=0, 12938.543 s, the workflow's exact decisive test), hydrated the CI way
(anonymous release download; archive sha256 `f1286bc8…9553` equal to the
committed transport descriptor and independently re-hashed by the cold gate;
governed hydrator; census byte-compare), taken together with the CI-proven
steps 1-7 transport/authentication chain (hosted-green at earlier heads).
The refuter's hermeticity finding: the local green is hermetic BY
CONSTRUCTION — store-content lock (census + 190-member hash equality against
the authenticated ledger), skip lock (an unset store variable can only skip
or hard-fail, never pass), and the legacy-locator assertion executed against
190 LIVE machine-local decoy paths (the actual T2 leakage paths), giving the
local run MORE teeth on the operator-leakage axis than a hosted run where
those paths do not exist.

**Binding conditions applied:** evidence bundle posted to the PR pre-merge
and committed at `docs/evidence/d117-v2-decisive-20260811/` (contemporaneous
worktree/interpreter/store attestations; durable copy in the window-custody
store); merge executed at e871f5b exactly; the workflow de-triggered to
`workflow_dispatch` in the first post-merge commit (the refuter's Route-A
substance without moving the merged head; the one auto-fired main run
cancelled); the two tracked "required"-wording contract sentences amended in
the same commit; WO-CI-RESTRUCTURE registered in TASK_QUEUE (matrix-split
the attack legs to fit hosted limits; full trust gauntlet — proof-semantics
work; deadline: before any claim publication and before the pack-freeze
merge wave — a recorded deviation from the refuter's tighter before-FCM-01
ordering, reasoning: FCM-01 touches the estimator surface, not the auth
core, and holding it on this work order would re-couple the critical path
this ruling decoupled); a Python 3.11 local decisive replay owed post-merge
(the decisive test has completed on no CI interpreter; refuter C3). The
fence, expiry, and five-part future-substitution test in the index row bind
future sessions.

### D-124 relicense — 2026-08-11 (Ed, in-thread; transcribed by the magistrate)

Ed RELICENSED one repair round for the frozen FLOOR-COMMONMODE-01 unit,
adopting the magistrate's recommended disposition (i) after weighing the
long-term-value question directly: the structural zero-threading repair buys
(1) the end of the audit tax on the registered surface, (2) safe reuse for
every future direct caller the extension-axes/P3 roadmap creates, and
(3) the cleaner registered-instrument exhibit for the paper — at desk-thread
cost off Ed's critical path. Ed's criteria as stated: dropping is acceptable
if the repair buys nothing for the paper or future research; repairing is
acceptable as a cheap non-blocking desk thread — both resolved in favor of
repair. **Pre-committed stopping rule (binding, no further deliberation):
if the repair round's delta re-audit finds ANY exact-arithmetic
understatement at an admitted input — any mechanism, any magnitude — the
unit drops to the worst-case default estimator (freeze-plan Q7 reversed,
both floor packs' comparative cells re-specced to METHOD_ID) without
another round.** The repair contract is the magistrate-adjudicated
structural-threading draft (custodied with the T4 session record); the
refuter-authored acceptance oracle may be amended only by its author.

### D-124 amendment — 2026-08-11: FCM-01 ALT-D120 completion (rounds 5-10)

The registered common-mode estimator's soundness campaign ran rounds 5-10
on 2026-08-11 (full round-by-round notes:
`docs/process_traces/2026-08-11-fcm-coldgate/fcm-round-notes-5-to-10.md`).
Round 5 (structural registered-input record) fired the stopping rule below;
D-132 revived the work and the D-133 cold gate ruled ALT-D120 — DELETE the
serialized registration vocabulary rather than authenticate it. Rounds 6-10
executed that: the public registered surface deleted (round 6-7); total
recursive vocabulary refusal + strict duplicate-key JSON parsing at every
admitted-byte entry (round 8); strict pre-admission in front of the pinned
legacy loader with a full loads-census (round 9); and complete finite-number
policy (overflow-to-inf) plus the last two census-miscovered parsers
(round 10, ACCEPTED clean by its delta — no findings). The O3 full delta
cleared the relocated arithmetic TERMINALLY: zero exact understatements in
4,096 independent rational-arithmetic cases plus a 1,536-case differential.
Registered identity is custody-closed and never carried in admitted
report/artifact vocabulary; provenance is re-derived in the governed
extraction path. Consumption of the tighter floor still gates on
WO-MINT-ESTIMATOR-VOCAB (D-133 cl.4).

## D-131: Identity-pin projection contract — adopt as proposed

**Date:** 2026-08-11. **Status:** ADOPTED — adopted as proposed from the
binding U11 design consult; magistrate transcription + implementation review
completed and recorded in the PR #131 D-121 terminal-review comment; ratified
at the #131 merge (2026-08-12).

1. **Receipt and custody.** Identity projection uses the exact-key
   `joulewise.identity_pin_projection_receipt.v1` schema with no self-hash.
   Freeze receipts append under the pack's
   `identity_pin_projection.receipts/` directory and are authenticated by
   GNU-style SHA-256 sidecars plus the final plan tree. Arm re-verification
   is pack-read-only and writes its receipt under the bracket session in the
   window custody root. `projection_input_sha256` binds the closed
   declaration, config, model-file, and live-probe inventory rather than the
   final tree.
2. **Canonical identity units.** Alpha and beta each carry one ordered
   identity unit. Gamma carries exactly four ordered units: `A/decode`,
   `A/prefill_p256`, `B/decode`, and `B/prefill_p256`; A references the 1.5B
   producer and B references the 7B producer. Every unit carries the same
   model/runtime/config triple used by the shared floor mint. The former
   gamma A/B model map and pack-wide runtime/config pins are invalid.
3. **Derive; never enter.** No operator, CLI option, launch recipe, or public
   verifier callable may supply or override an identity pin. Model
   enumeration, scientific-config identity, the governed eleven-field stack
   identity, and triple derivation have one shared implementation consumed by
   runtime collection, both mint paths, analysis, detection-floor
   validation, freeze, and arm verification. Any pack-versus-config or
   frozen-versus-live mismatch fails closed.
4. **Lifecycle and successor.** Active packs are `unprojected` or `frozen`;
   `superseded` is inactive. Null pins and a null receipt are legal only
   before projection. Freeze is the sole `unprojected` to `frozen`
   transition and is byte-idempotent on the identical frozen projection;
   verify cannot mutate the pack. Reissue creates a new pack/custody root and
   appends a new receipt whose `supersedes` record binds the old pack,
   receipt, and readiness hashes; old receipts are never edited or deleted,
   and an opened session or attempt ID is never reused.
5. **Readiness boundary.** U11 exposes `verify_frozen_projection()` and its
   CLI receipt only. U8 owns the readiness-record
   `identity_pin_projection` section binding frozen and arm receipt
   path/SHA pairs, derivation contract, ordered unit IDs, and PASS status.
   Every U11 reason makes readiness REFUSE. No D-117 pack may arm before that
   U8 consumer lands and passes.

### D-078 registry amendment — 2026-08-11: identity-pin readiness refusals

The closed readiness-refusal vocabulary gains
`readiness_identity_artifact_unreadable`,
`readiness_identity_environment_dirty`,
`readiness_identity_projection_mint_divergence`,
`readiness_identity_pinset_frozen_mismatch`, and
`readiness_identity_receipt_namespace_anomalous` (fix round 4: a committed
entry in the governed identity_pin_projection.receipts namespace that does
not conform to the freeze grammar — projection-<4+ digits>.json plus its
.sha256 sidecar — refuses verification fail-closed rather than being
silently skipped, so an authenticated successor can never be hidden behind
a non-conforming filename). These spellings belong to the
U8 readiness registry, not transport or member-verdict vocabularies. They
only refuse; none can license a run or claim.

## D-132: Stopping rules target doom loops, not converging instruments

**Date:** 2026-08-11 (Ed, in-thread; transcribed by the magistrate).
**Trigger:** the same-day execution of the D-124 relicense stopping rule,
which terminated FLOOR-COMMONMODE-01 after its round-5 delta audit.

**The principle (Ed's words, in substance):** a process limit like "stop
after N rounds of arbitration" exists to stop doom looping — it is never to
prevent continuous work on material that keeps getting better. Never stop
work on an instrument or component making progress because of a meta
process rule. Progress toward a publishable paper is the highest-order
goal; all other prerogatives fall below it. (This composes with D-119
rather than conflicting: soundness governs what may be CLAIMED; D-132
governs when work may be STOPPED.)

**Application to FCM-01:** the six-round record is convergence, not
looping — the extremum enumeration proven exact in rational arithmetic
three ways, the production path sound from round 2 onward, each round's
defect permanently closed, successive findings shrinking from 0.25 J to
5e-10 J while the audit bar rose (adversary-authored oracle, exact
arithmetic, fabrication attacks). The terminal insight: every post-round-2
kill was against the PUBLIC contract — a promise the custody model's own
rules say no claim path consumes (claim-bearing floors must come from the
governed extraction path). REVIVAL DESIGN (round 6): delete the public
registered surface entirely; the estimator becomes internal to the
governed extraction pipeline and a registered result exists only as an
artifact of that path — the admitted-input class closes by construction.
All banked assets carry over (oracle, real b01/b02 fixtures, enclosure,
proofs). The re-spec-to-default branch remains unmerged as the immediate
fallback should the revival round's fresh delta find any exact
understatement on the extraction path.

**Rust disposition (Ed's question answered):** a Rust core would hold the
unforgeable-token property Python cannot (executed demonstration:
FCM-R5-01's five construction escape hatches) but adds nothing to
measurement capability and does not close language-independent classes
(test authorship, repo trust). It is affirmed as the H2/H3 answer for the
next-generation instrument core, not a P1 dependency.

## D-133: FCM-01 disposition — hybrid + ALT-D120 (cold gate, revised sitting)

**Ruled 2026-08-11 by the mandated cold gate** (fresh Fable adjudicator +
paired Opus contract-lens refuter; revised sitting after the refuter's
brief; magistrate adopted the revised ruling without dissent). Trigger:
the round-6 fresh delta REJECTED on FCM6-01 (registration dictionary
injectable into admitted JSON; validators and the unbound authenticator
accept it), landing outside both branches of the pre-committed decision
rule, and a round 7 would have been the next round on the
fabricated-record-admission class.

**Bench-verified facts that shaped the ruling** (magistrate-executed):
the pinned mint scripts contain ZERO estimator vocabulary — the tighter
two-shared-edge floor cannot reach a minted artifact this cycle under any
disposition without new D-118-gated mint work; no consumer of
`estimator_registration` exists outside its two owning modules (the
forged field is inert); the production claim path binds
`expected_sha256` + `expected_artifact_id`, which the delta's V3
reproduction omitted. The adjudicator's first ruling (round-7
custody-closure) was withdrawn on these facts with concessions on the
record, including that `exact_understatement_found=false` was a
non-finding (lenses unexecuted).

**The disposition:**
(1) Fallback `respec/d124-withdrawn` (681ab49) merges after its own gate
shape (fresh delta audit + re-verified generator/--check/dual-interpreter
evidence + D-121); the pack-freeze lane unblocks at that merge and FCM-01
may not gate it thereafter.
(2) FCM-01 continues as an unmerged desk thread under ALT-D120: DELETE
the serialized registration vocabulary (CellReport.as_row stops emitting
it; removed from _D117_MINT_FLOOR_OPTIONAL_KEYS and _CMP_OPTIONAL_KEYS;
self-equality branch deleted) so both demonstrated forgeries become
closed-profile unknown-key REFUSALS — the D-120 precedent (delete
vocabulary, don't authenticate it). The false round-6 provenance claim
("registered results exist only as governed extraction artifacts") is
corrected to what the design enforces, with a sixth parameter-sha
rotation.
(3) A FULL fresh delta is owed on the branch head (the +497 lines of
moved arithmetic are unaudited; the round-6 delta was interrupted before
its arithmetic lenses). Any exact understatement found there drops the
estimator to the fallback PERMANENTLY under the original pre-committed
rule — no further revival.
(4) Packs re-spec back to the tighter estimator only if ALT-D120 + the
full delta + the mint-estimator vocabulary workstream (new, D-118-gated,
registered in TASK_QUEUE) all land before the freeze wave.
(5) Debts surfaced, not discharged: the FLOOR-COMMONMODE-01 BANKED
UNGATED 425f75f audit debt and the fallback's previously-unstated gate
status enter the ledger.

**Flagged to Ed (schedule call, not ruled):** if the gamma-arm claim
capability must ship in the MAIN paper this cycle, the mint-estimator
workstream becomes critical path and the freeze wave waits by direction —
reversal condition 5 of the ruling. Default absent Ed's direction: the
freeze does not wait; the tighter number banks for the ICPE version.

D-132 is satisfied, not overridden: work continues; consumption is
deferred. The same-signature escalation trigger is satisfied by
resolution through this consult with a structurally different remedy
(deletion, not a third validator).

### D-124/D-133 implementation note — 2026-08-11: spec-authoritative mint dispatch

WO-MINT-ESTIMATOR-VOCAB added per-cell v2 mint dispatch at postcollection
equality, frozen artifact construction, and final evidence binding. The sole
authority is the authenticated comparative extraction-spec cell; estimator
and registration identity remain absent from reports, artifacts, pinsets, and
provenance. Regressions cover spec swaps, report-vocabulary and opposite-width
mismatches, a negative control at each dispatch site, equality/U10 repair,
one-ULP common-mode understatement, mixed-selector ordering, default-byte
preservation, registered refusal without fallback, and no-output refusal. The
focused matrices passed 334 tests on both `python3` and `python3.11` (one
skip); the canonical suites passed 3,067 tests on both interpreters (96
skips).

**F1-F12 fix-round addendum (2026-08-12, uncommitted final-gate worktree).**
The cold-gate final ruling replaces every earlier condition set. At prepared
integration head `a798f2bc2a33187ee8f0b7f9d5ad7836a7faca02`, the pinned core
`scripts/mint_floor_artifact.py` has SHA-256
`79229aa2757f70a277c870fc50d0672d70952035f982da26ba5211eb7df8ba16`.
It is byte-identical to the prepared post-#131 upstream parent
`60d9e42a8204c3a117a577ddb4680fcb30814a26` and to the current
`origin/main` copy. AST/source comparison re-verified
`_verify_report_widths`, `_report_members`, `_target_report_cell`, and
`_authenticate_component` unchanged; the binder still iterates exactly
`("absolute", "comparative")`. The fix deletes the common-mode
`except core.MintError` swallow and the provenance-derived binding-result
fallback. The pinned binder now runs to completion over an isolated deep copy
whose only substituted artifact field is the comparative
`admissible_half_widths_j`, populated from authenticated
`comparative_component.widths_j`; the exact registered-width comparison still
targets the real artifact, which is the object passed to the final writer.

**F6 refusal-identity ledger.** A mechanical pre-WO-to-fix audit plus the
default-path differential/refusal matrices found the following complete set of
identity effects:

- Existing default-path v2 refusal fixtures retain their messages. Default
  output bytes retain the independent golden component hashes, default
  authentication refusals match the pinned core exactly, and default binding
  still uses the pinned `rel_tol=1e-12, abs_tol=1e-12` width check.
- The former test assertion
  `"absolute_evaluation_basis_sha256 mismatch"` is not silently relaxed.
  Component/pin gating now fires earlier, before estimator dispatch, with the
  exact refusal `producer[0].decode.absolute: evaluation basis sha256
  mismatch`; the regression pins that complete prefix. The older downstream
  U10 projection message was
  `postcollection_evidence_mismatch:
  absolute_evaluation_basis_sha256 mismatch against domain-owned verification
  projection`. The identity change is justified by F1/F5's required ordering:
  the authenticated component pin owns this mismatch and must refuse before
  any estimator executes.
- At the postcollection `except ValueError` site, a spec-selected estimator
  selection/recomputation refusal is deliberately normalized to
  `postcollection_evidence_mismatch: comparative estimator recomputation
  refused: <original cause>`. This new gate applies to the newly registered
  path after component and producer authentication; it does not relabel a
  successfully selected default path or any existing default fixture.
- At the final binding call site, estimator-module `ValueError` is deliberately
  normalized to the public generalized `MintError` while preserving
  `str(exc)` byte-for-byte. Pinned-core `MintError` refusals, including every
  default-path binder refusal, retain both their message and the pre-existing
  generalized-boundary normalization. The gate is the final estimator-aware
  evidence binder; it refuses before output writing.

No other existing refusal assertion was widened. New common-mode refusals are
additive and fail closed: exact report-width/type mismatch, frozen-object
construction mismatch, and exact artifact-width/type mismatch.

**F11 scope and inventory.** The authoritative WRITE_SCOPE is amended to
include `tests/test_detection_floor.py`. Its edit existed in the working tree
before any scope grant was on the record; this ruling ratifies the content
prospectively, and does **not** ratify that sequencing. Against the prepared
integrated upstream parent (`a798f2b^2`, `60d9e42`), the mechanical diff
inventory is exactly:

1. `docs/decision_log.md`
2. `joulewise/floor_mint_estimator.py`
3. `scripts/mint_floor_artifact_generalized.py`
4. `tests/test_detection_floor.py`
5. `tests/test_floor_mint_estimator.py`
6. `tests/test_mint_floor_artifact_generalized.py`

During this fix session `origin/main` advanced independently to `c3b2c79`; the
literal final-gate command `git diff origin/main --name-only` therefore also
reports four upstream-only differences (`.github/workflows/d117-production-proof.yml`,
`.github/workflows/site.yml`, `RUN_STATE.md`, and
`docs/process_traces/2026-08-12-calexits-mutation-consult/consult.md`). They
are not WO edits and remain outside WRITE_SCOPE. F11(c) must be re-executed by
the lead after integrating the authorized six-path diff onto the then-current
upstream head; no worker-side merge, rebase, or out-of-scope repair is
authorized here. D-133 clause 3's full fresh FCM delta likewise remains an
open, lead-owned merge gate and is not discharged by this work order.

## D-134: §5C arm-readiness record contract — two-stage append-only receipts (adopt-as-proposed)

**Adopted 2026-08-11 (T4-late)** from the binding design consult (Sol
xhigh; trace: docs/process_traces/2026-08-11-5c-readiness-contract/),
which resolved the four NEEDS_RULING gaps an implementation attempt
correctly refused to guess through (same trace, needs-ruling-report.md):
the §5C record's lifecycle/hash-cycle (the runbook had the plan pinning a
record that binds the plan's sha), the freeze-time vs arm-time row split,
the absent closed schema, and undefined dry-run semantics.

**The contract (ten clauses, adopt-as-proposed):**
1. Readiness splits into a pack-pinned, non-authorizing FREEZE RECEIPT
   and an external, pack-binding ARM RECEIPT.
2. Frozen bytes declare the future arm-receipt schema and governed
   namespace — never its future path/sha value (the hash cycle is broken
   by declaring slots, not hashing future bytes).
3. `d117_row_registry_v1.json` is the SOLE row authority for ALPHA, BETA,
   and GAMMA; Markdown matrices are checked views.
4. UNKNOWN is prohibited in receipts; missing live evidence is REFUSE;
   NOT_APPLICABLE only by registered predicates.
5. Exact-key, no-self-hash receipts; committed-pack verification;
   semantic supersession; D-120's single-authority assurance qualifier.
6. Derive-never-enter: every row verdict, applicability, digest, identity
   pin, and evidence binding is derived; operators supply paths and
   irreducible attestations, never conclusions.
7. Dry-run PASS is same-head rehearsal evidence only; it bypasses no
   freeze refusal and can never occupy the arm slot.
8. A live ledger-reservation row is added, and the impossible pre-launch
   "single foreground launch" row is replaced by an atomically consumable
   single-launch capability (exactly one consumer succeeds; replay and
   stale predecessors refuse).
9. The enumerated live doctrine is amended (runbook §5C/§5A, D-117
   attachment-slot clarification, refusal-registry amendment, operator
   packet ARM sequence, 40h-plan B2/B5, state-kernel fence wording);
   historical process traces are preserved and superseded by decision,
   never edited in place.
10. The full mutation/lifecycle/namespace/replay/U11-integration/
    three-profile test obligations bind before any D-117 arm.

Critical path per the consult: D-131/U11 landing → registry + doctrine
amendment → three pack profiles → freeze receipts + final pack bytes →
reviewed-main proof → same-head dry-run receipt → Ed's §5A and T-0 domain
receipts → live ledger reservation → final arm GO receipt → atomic
launch consumption. Implementation launches after PR #131 merges.

## D-135: Site-capsule budgets are advisory — only the physical Lakebed cap may gate

**Ed, in-thread 2026-08-12 (transcribed by the magistrate; verbatim intent:
stop letting the site block engineering on an antiquated requirement).**
The self-imposed conservative site budgets — the 1,000,000-byte measured
capsule budget, per-page/per-shard byte budgets (e.g. the 30,000-byte
record-page shard), and pagination-margin assertions — are ADVISORY:
build tooling and tests may WARN on them but must not fail a build, a
test suite, or a PR gate. The ONLY site-size condition that may fail
anything is the physical Lakebed platform cap (1,048,576 bytes measured
by the real validator), because exceeding it makes the deploy itself
fail. Content decisions (what the decision log or council log records)
are never to be trimmed, split, or archived to satisfy an advisory
budget. SITE-CAPSULE-BUDGET-01 is SUPERSEDED by this ruling (archival
remains available as an option if the PHYSICAL cap ever approaches, but
nothing gates on the conservative margin).

## D-136: The site lane is retired from all automatic processes

**Ed, in-thread 2026-08-12 (transcribed by the magistrate; verbatim intent:
"stop bothering with the capsule size … i don't wanna see any lakebed stuff
touched anymore i'm tired of it costing tokens. take it out of the processes
entirely it pollutes context for a repetitive status doc").**
Extends D-135 and D-101 addendum II. Clauses:

1. No session spends tokens on Lakebed/capsule size, packing, deploy
   failures, or site-chain diagnosis. A red site-chain result is not a
   finding, not a follow-up, and never appears in a merge gate, run report
   priority list, or RUN_STATE watch item.
2. The `site` workflow triggers on `workflow_dispatch` only — never on
   push or pull_request. Site publication happens if and when a human
   chooses to run it.
3. The site's content remains whatever the repo's docs already say; no
   engineering effort is owed to fitting it into any platform constraint.
   The 2026-08-12 physical-cap overrun on PR #136's branch is explicitly
   NOT to be diagnosed or fixed (the in-flight diagnosis was killed on
   this ruling).
4. Open SITE-* queue items and the D-135 advisory-budget machinery stay
   as they are (merged or in-flight work is not reverted), but no new
   site work is minted.

### D-117 amendment — 2026-08-12: frozen readiness slots do not hash future arm bytes

D-134 amends D-117's plan-freeze attachment rule without changing the
scientific plans or their historical custody. The frozen `plan_tree.json`
declares an `arm_attachments.arm_readiness` slot containing the D-134
contract/schema ID, the authoritative row-registry path/digest/profile, the
pack-contained freeze-receipt path and digest, the deterministic external
arm-receipt namespace, and the committed-pack digest algorithm. The frozen
plan never contains a future arm receipt's path or SHA-256. That receipt does
not exist until T-0 facts have been observed, so hashing it into frozen bytes
would create a plan/receipt hash cycle and would falsely make future evidence
look freeze-known.

The pack-pinned freeze receipt is non-authorizing. After all pack bytes are
committed, the external arm receipt binds the completed pack digest and live
evidence under `CUSTODY_ROOT/PACK_ID/arm_readiness.receipts/`. This is a slot
declaration, not a deferred mutation of the pack. Historical D-117 freeze
traces and the external T4 custody record remain immutable evidence; this
decision supersedes their old lifecycle prose rather than editing them.
D-120's existing assurance qualifier survives intact: readiness establishes
single-authority, hash-bound, fail-closed consistency and never proves
operator independence or independent attestation.

### D-078 registry amendment — 2026-08-12: closed D-134 readiness refusals

The readiness layer owns the following closed 46-code vocabulary. The type
labels are `STRUCTURE`, `CUSTODY`, `GIT`, `LIFECYCLE`, `POLICY`, `IDENTITY`,
and `ENVIRONMENT`; upstream evidence receipts retain their own closed detail
codes.

- **STRUCTURE (8):** `readiness_schema_invalid`,
  `readiness_receipt_kind_invalid`, `readiness_unknown_key`,
  `readiness_row_registry_mismatch`, `readiness_row_set_incomplete`,
  `readiness_row_applicability_invalid`,
  `readiness_evidence_reference_invalid`, `readiness_usage_invalid`.
- **CUSTODY (9):** `readiness_pack_unreadable`,
  `readiness_pack_namespace_anomalous`, `readiness_pack_digest_mismatch`,
  `readiness_pack_not_committed`, `readiness_freeze_receipt_unreadable`,
  `readiness_freeze_receipt_mismatch`, `readiness_evidence_unreadable`,
  `readiness_evidence_digest_mismatch`,
  `readiness_receipt_namespace_anomalous`.
- **GIT (3):** `readiness_git_tree_dirty`,
  `readiness_reviewed_main_mismatch`, `readiness_terminal_review_missing`.
- **LIFECYCLE (9):** `readiness_receipt_superseded`,
  `readiness_record_expired`, `readiness_record_consumed`,
  `readiness_output_collision`, `readiness_lock_unavailable`,
  `readiness_dry_run_missing`, `readiness_dry_run_refused`,
  `readiness_dry_run_stale`, `readiness_dry_run_used_as_arm_record`.
  `readiness_lock_unavailable` is defensive forward-compatibility and is
  currently unreachable on the atomic-consume path, which acquires no lock:
  every race loser receives `readiness_record_consumed`. A test pins that
  unreachability so any future emission is a loud contract change rather than
  a silent one.
- **POLICY (10):** `readiness_dependency_refused`,
  `readiness_waiver_source_invalid`, `readiness_waiver_set_nonempty`,
  `readiness_root_binding_invalid`, `readiness_root_not_fresh`,
  `readiness_backup_preflight_refused`,
  `readiness_machine_preflight_refused`,
  `readiness_clock_preflight_refused`,
  `readiness_ledger_preflight_refused`,
  `readiness_launch_capability_unavailable`.
- **IDENTITY (5):** `readiness_identity_artifact_unreadable`,
  `readiness_identity_environment_dirty`,
  `readiness_identity_projection_mint_divergence`,
  `readiness_identity_pinset_frozen_mismatch`,
  `readiness_identity_receipt_namespace_anomalous`. This block is imported
  unchanged from the D-131 identity-pin projection decision.
- **ENVIRONMENT (2):** `readiness_io_error`,
  `readiness_internal_error`.

Every one of these 46 spellings only refuses. No readiness code, type label,
`PASS`, `GO`, `READY`, `clean`, or `ready` licenses ARM, physical launch, or a
scientific claim. This amendment composes with D-120's unchanged
single-authority assurance qualifier; it does not add an independent witness.

## D-137: Arm-readiness v1 monotonic expiry is bound to the boot session

**Adopted 2026-08-12 (magistrate-ratified v1 schema amendment).** Every v1
arm-readiness arm receipt and generic evidence receipt that carries
`valid_until_monotonic_ns` also carries the required, derived
`boot_session_id`. The value is machine-derived and is never supplied by an
operator, API argument, or command-line option. Verification and atomic
consumption compare the receipt's boot session with the current boot session;
a mismatch refuses closed as `readiness_record_expired`. The monotonic expiry
is therefore never interpreted across a reboot.

This amendment composes with the single-authority, hash-bound assurance model
adopted for postcollection trust in D-120 and with the two-stage arm-readiness
contract in D-134. The cross-reboot rule was already ratified, a live defect
was corroborated through two independent review lenses, and no production
readiness receipts had been issued, so correcting v1 before issuance carries
no migration cost. Leaving reboot invalidation in operator prose would repeat
the prose-only failure mode that the arm-readiness machine gate exists to
eliminate.

This is a deliberate divergence from the literal v1 key lists in the adopted
D-134 consult under
`docs/process_traces/2026-08-11-5c-readiness-contract/consult.md`. That consult
is preserved historical evidence and is not edited; this later decision is
the authority for the amended v1 schema.
### D-133 cl.4 execution ratification + Q8 budget ratification — 2026-08-12 (Ed, T6 session start)

Three Ed rulings taken at the T6 session's first interactive exchange
(recorded verbatim from the AskUserQuestion round; the T5 checkpoint had
flagged all three as ED-OWED):

1. **D-133 clause 4 conditional: EXECUTE.** PR #140 (WO-MINT-ESTIMATOR-VOCAB)
   merged at `e11b1ad` with all F1–F12 met, mechanically satisfying the
   clause-4 conditions (ALT-D120 + terminal delta + mintvocab, all
   pre-freeze-wave). Ed ratified executing the re-spec on its own ruled
   terms: both floor packs re-spec to the tighter **1.869502 J** floor
   (vs the 8.611855 J default) via a separate generator run + gate before
   FREEZE. The paper swap is mechanical via PR #133's merged
   conditional-insert block. Reversal condition 5 (hold the freeze for an
   explicit go) was offered and declined — the ruled default proceeds.
2. **Q8 quiet-window budgets: RATIFIED as computed.** The p256 cells are
   REAL new bundles (50→100 members/pack, PR #138): **~6.28 h per 1.5B
   pack / ~6.48 h per 7B pack, 20% margin included** — now the planning
   numbers for window arming.
3. **Window night: TONIGHT (2026-08-12).** Ed does the live
   sudo/powermetrics checklist (gates reliance on #127's production
   sampler) and the §5A taps tonight; the freeze lane drives to ARMED
   today. R2 perishable-resource discipline applies for the rest of the
   session.

### Item-(1) mechanism ruling — 2026-08-12 (magistrate, consult-adopted): WO-COLLECTION-MARGIN-01

The freeze-plan addendum's LIVE item (1) — record each registered comparative
cell's minimum window-duration margin at collection — lost its named
mechanism when FCM-01 withdrew (D-133). Pre-decision Sol xhigh consult
(1 round, rule-2 default) REJECTED the magistrate's candidate (a §5C
readiness-registry collection-time row) on a verified structural blocker:
the D-134 registry carries exactly two evaluation phases (FREEZE_AND_ARM,
ARM_ONLY), both pre-launch, and the ARM receipt is atomically consumed — a
collection-time row would either refuse every arm, gate nothing, or break
the two-stage append-only authorization contract. Drop REJECTED as
indefensible (WO-4/Q9 37/50 not_resolvable evidence; item (3) forbids the
"p256 windows are expected longer" inference). ADOPTED: a dedicated
append-only collection-margin receipt (WO-COLLECTION-MARGIN-01, registered
in TASK_QUEUE with the full ratified design). Gate split: PACK FREEZE gates
on the mechanism existing (schema + registered-cell inventory + deterministic
namespace); COLLECTION CLOSE-OUT gates on the resulting receipt. Receipt
PASS asserts derivation completeness from authenticated bytes, never margin
positivity — D-133 ruled no new acceptance threshold. Residual risk recorded:
the receipt exposes inadequate temporal support; it cannot repair it —
an inadequate p256 result still requires recollection, claim demotion, or a
separately ruled disposition. Sol's design win logged to the codex-delegation
field-note scorecard.

### Window ALPHA slip ruling — 2026-08-13 (Ed, T6 session)

The three-pack freeze COMPLETED at 49dcc49 (tighter 1.869502 J floor; U11
projections + D-134 freeze receipts + authored evidence all PASS; §5C lead
live verification discharged on the frozen checkout). At arm-packet
finalization the mechanic found the launch-blocking §0.6 gap: FIFTEEN
ARM_ONLY rows (clock.*, desk.terminal_review, twelve t0.*) evaluate only
from evidence receipts in CUSTODY_ROOT/PACK_ID/arm_readiness.evidence/,
which nothing in production can author — the arm-side sibling of the
freeze-side X-1 gap closed the same day by #145. Ed RULED: slip the window
to 2026-08-14 night; build WO-ARM-EVIDENCE-AUTHOR-01 as day work under the
full gauntlet rather than arm an untested path at midnight. Also owed to
Ed from the packet: M-1 (BRACKET_SESSION_ID literal vs the runbook's
<WINDOW_ID>-calibration convention — ratify the operator binding) and M-2
(the frozen packs' draft_status/README still say "unfrozen draft" — a
generator-owned cosmetic contradiction needing a ruled fix, since pack
bytes are now frozen). Standing constraint: NO REBOOT before T-0 or the
evidence re-authors (cheap now — the tool exists).

### Window gating directive — 2026-08-13 late (Ed, T6): council-audited instrument readiness precedes any window

Ed: do not focus on running the windows unless a COUNCIL decides the
instruments are ready on a COMPREHENSIVE AUDIT; desk work is the default
program, "do whatever is logical for the progress of the project." This
supersedes the same-day window-ladder scheduling (and the earlier
window-tonight ruling's urgency) — the ladder now sits behind a full-tier
council verdict: a comprehensive instrument-readiness audit spanning the
frozen packs, writer + calibration bracket + sampler supervision (#127
production reliance was still Ed-owed), reduce/floors/mint chain, custody,
and runbook procedure, adjudicated to GO / NO-GO-with-work-orders. Work
orders out of the audit become the desk program. The 72h machine window
remains available if the council reaches GO while it lasts; otherwise the
span is desk work and the windows wait for readiness plus a later tap
window — soundness above schedule, per the standing prerogative.

### Interaction contract — 2026-08-14 morning (Ed): magistrate decides everything except hardware/sudo

Ed: wait on him ONLY for physical-hardware and sudo actions; work the
70-hour horizon toward the paper; MINIMIZE his required appearances (batch
all Ed-needs into as few machine sessions as possible). Consequently the
magistrate now rules directly on items previously queued as Ed-owed unless
they touch hardware/privilege. Applied immediately:

**M-1 RULED (magistrate):** BRACKET_SESSION_ID for Window ALPHA =
`window_alpha_YYYYMMDD-calibration` (date bound at arm). The runbook:177
convention reads `<WINDOW_ID>-calibration` where WINDOW_ID would give the
plan-id literal; the packet mechanic verified the operator binding passes
the path-component check and the margin recorder reads the plan-id as
window ID independently. The window-letter form is adopted for operator
legibility; the arm packet and §12 record BOTH the literal and the
plan-id so no consumer ambiguity survives. Rationale custodied with the
packet.

**M-2 RULED (magistrate):** the frozen packs' `draft_status:
"unfrozen_draft"` and README "not armable" lines are GENERATOR-OWNED
DESCRIPTIVE TEXT that predates the freeze machinery; the freeze receipts
and plan-tree pins are the AUTHORITATIVE state. Remedy: the chain-fix
batch teaches the generators a freeze-aware status line (mirroring the
existing freeze-aware D-134 attachment handling) and regenerates the
sidecar-consistent text via the canonical path; until that lands, the
freeze receipt's presence governs and the §5C gate's placeholder-text
NO-GO reading is OVERRIDDEN for exactly this field by this ruling (scoped,
recorded — the packet cites it).

**M-2 EXECUTION NOTE (magistrate, 2026-08-15 — factual record per council-verdict R4;
the override's soundness is REMANDED to its own cold gate, see
docs/process_traces/2026-08-15-readiness-council/council-verdict.md Disposition 2):**
the remedy as ruled ("regenerates the sidecar-consistent text via the canonical path")
did NOT execute as written — #149 shipped freeze-aware status FORWARD-ONLY under
PRESERVE_CURRENT_FROZEN_BYTES, and the three frozen packs still carry
`draft_status: "unfrozen_draft"` at the audit baseline (verified by the cold
adjudicator and sweep-S3). Preserving frozen bytes was the correct engineering
call; the recorded consequence is that this ruling, scoped as transitional, is the
STANDING operative instrument for the current packs' lifetime: the freeze receipt's
presence governs, and the §5C placeholder-text NO-GO reading remains overridden for
exactly this field. Every arm packet must cite this ruling until the Phase-2
re-freeze regenerates truthful freeze-aware status text, at which point this
override RETIRES.

ED-QUALIFICATION batching: all sudo/hardware rows (sudo powermetrics
checklist, live sampler supervision check, JW-MET-3 rail probe, §5A tap
familiarization) are assembled into ONE scripted ~15-minute session,
prepared before Ed is next pinged; a window arm can chain onto the same
session when the council is READY, so one appearance can close
qualification AND start a window.

### R3 RULED (magistrate, 2026-08-15; council-verdict Phase 0): P2-006 formally RETIRED from window selection

Authority: the 2026-08-15 council verdict (docs/process_traces/
2026-08-15-readiness-council/council-verdict.md, Disposition 3 + Phase 0
R3), executing the DG-refuter finding that D-117 replaced the Window-A
program's claim path without formally naming or retiring row P2-006 —
leaving the kernel rendering a superseded campaign READY [QUIET-MAC] with
zero active gates (fleet blocker L1-B2).

**Ruling:**
1. P2-006 ("Window A two-model campaign") is RETIRED as a quiet-window
   selection row, effective immediately. Its outputs do not trace to the
   current D-117 claim path; no quiet night may be spent on it.
2. The retirement is SUPERSESSION, not deletion: the row's history and
   its D-110-era rationale remain in the record. Any future two-model
   exploratory campaign enters as a NEW row scoped under the then-current
   claim path and gate table.
3. WO-KERNEL-RECONCILE (council Phase 1, magistrate-supervised) executes
   this ruling in the kernel transaction: remove P2-006 from live
   selection, install the WINDOW-COUNCIL-GATE global gate (scope
   quiet_mac, allowed_task_ids [], clearance = a READY-candidate council
   verdict), reconcile the false U11/FCM rows, and regenerate.
4. Until that transaction lands, any surface rendering P2-006 as READY is
   OVERRIDDEN by this ruling; the generated regions are known-stale
   (fleet L1-B2/B3, adjudicated).

### R2 RULED (magistrate, 2026-08-15; council-verdict Phase 0; Sol design consult adopted): FROZEN_PLAN identity

Consult custodied: docs/process_traces/2026-08-15-r2-frozen-plan-consult/
(rule-2 pre-decision consult, adopted in full). Authority: council verdict
Phase 0 R2; resolves the B-cluster refuter condition (F6) that blocked
prose/parser changes.

**Ruling:**
1. FROZEN_PLAN is the committed pack's `calibration_plan.json` — never a
   custody reservation JSON, never `plan_tree.json`. Its identity is the
   tuple (pack_id, canonical pack-relative path, plan_id, SHA-256 of
   exact committed bytes); the freeze receipts already record exactly
   this binding.
2. Authoritative storage is canonical pack-root-relative POSIX syntax
   (reject absolute paths, `.`/`..`, symlinks, non-regular files,
   uncommitted bytes). Absolute paths appear ONLY at the execution
   boundary as one resolved literal; the frozen window.env carries
   literal absolute values, no `$` expansion.
3. One SHARED RESOLVER implements rule 2 and replaces every ad-hoc join
   (_pack_identity, dry-run rehearsal, evidence authoring, the T-0
   author's plan-path check — the doubled-plan-path defect site).
   Alpha/beta producers emit `plan.path: "calibration_plan.json"`
   (gamma already conforms).
4. E-8 verification requires path + plan_id + sha equality (not sha
   alone); E-9 uses the identical --plan literal. Runbook §4/§6 prose
   re-cut accordingly.
5. Execution rides WO-T0-PRODUCER (council Phase 1) with the ruled
   real-pack regression test; the consult's per-surface fix list is the
   work order's checklist.

### WO-CONSUMPTION-EDGE contract ADOPTED (magistrate, 2026-08-15; council Phase 0; Sol design consult adopted)

Consult custodied: docs/process_traces/2026-08-15-consumption-edge-consult/
(rule-2 pre-decision consult — the ONE home for schema detail; not
restated here). Cures fleet blocker L10-B1/L4 (the gamma claim edge).

**Ruling:**
1. The two-artifact contract is ADOPTED: the pack's frozen prospective
   manifest is NEVER mutated post-collection and analyze-claims NEVER
   accepts it directly. An OUTCOME-BLIND finalizer (authenticates
   completeness, custody, and frozen selectors; never reads an effect)
   derives an immutable `joulewise.analysis_manifest.v3.finalized`
   artifact with full lineage (prospective id/sha, collection manifest,
   whole-window verdict + evaluation basis, bracket binding, ledger
   terminal head, exact aggregate floor artifact); a finalized-schema
   validator gates analyze-claims consumption.
2. The frozen semantic projection covers every estimand/multiplicity-
   bearing field (per the consult's enumeration); both D-122 contrasts
   are carried regardless of decision-envelope outcome — refusals are
   first-class results.
3. The present placeholder `postcollection_attachments` remain
   draft-only and are REJECTED by the frozen validator (D-134
   slot-declaration precedent).
4. Execution = WO-CONSUMPTION-EDGE (council Phase 1) with a dedicated
   queue row; the L10 sacrificial rehearsal re-runs the full edge at
   the same head before any window is spent.
5. The consult's open rulings (prefill/floor/multiplicity finalization
   items) are carried on the work order's RULING-REQUIRED list; any that
   touch claim semantics surface to Ed with the Phase-1 close.
6. **Mechanism disposition (lead ruling, continuation):** claim-artifact
   family validation compares the emitted family policy against the exact
   frozen family semantics carried by the authenticated manifest; it no
   longer imposes the historical Holm α=.05, m=1 policy as a code constant.
   Multi-contrast finalized families map LOO omissions by their frozen block
   number across arm-specific block IDs and refuse under
   `analysis_manifest_family_semantics_mismatch` if that frozen stratum map
   is absent or ambiguous. This mechanism takes no position on which family
   semantics Ed should freeze.

**RULING-REQUIRED — Ed (scientific scope; blocks production freeze, not the
mechanism build):** (a) the p256 prefill test and scientific direction;
(b) whether decode and prefill share one multiplicity family or use separate
families, and the resulting frozen `m`; (c) the owned p256 floor or governed
transport rule; and (d) authorization of the production successor freeze
followed by the same-HEAD, production-pack L10 sacrificial replay. Synthetic
two-family m=1 and shared-family m=2 tests are mechanism discrimination only
and are not scientific rulings.

### D-078 amendment — 2026-08-15: analysis-manifest consumption-edge refusal registry

The following exact spellings extend D-078's closed, fail-closed refusal
registry for the adopted prospective → finalized → consumer lifecycle.
Nested validators may add detail, but must retain one of these top-level
codes and must exit before estimation or claim-artifact publication.

- Prospective: `analysis_prospective_schema_invalid`,
  `analysis_prospective_unknown_key`, `analysis_prospective_not_frozen`,
  `analysis_prospective_identity_mismatch`,
  `analysis_prospective_plan_tree_mismatch`,
  `analysis_prospective_source_hash_mismatch`,
  `analysis_prospective_unsafe_path`,
  `analysis_prospective_member_cover_mismatch`,
  `analysis_prospective_block_cover_mismatch`,
  `analysis_prospective_contrast_cover_mismatch`,
  `analysis_prospective_family_invalid`,
  `analysis_prospective_multiplicity_invalid`,
  `analysis_prospective_floor_dependency_unresolved`, and
  `analysis_prospective_unresolved_slot`.
- Finalization: `analysis_finalization_input_unreadable`,
  `analysis_finalization_prospective_invalid`,
  `analysis_finalization_attachment_missing`,
  `analysis_finalization_attachment_invalid`,
  `analysis_finalization_verdict_not_passed`,
  `analysis_finalization_evaluation_basis_mismatch`,
  `analysis_finalization_member_cover_mismatch`,
  `analysis_finalization_bracket_binding_mismatch`,
  `analysis_finalization_ledger_head_mismatch`,
  `analysis_finalization_floor_dependency_unsatisfied`,
  `analysis_finalization_semantics_mismatch`,
  `analysis_finalization_noncanonical`, and
  `analysis_finalization_output_conflict`.
- Consumer: `analysis_manifest_prospective_not_consumable`,
  `analysis_manifest_finalized_invalid`,
  `analysis_manifest_lineage_mismatch`,
  `analysis_manifest_collection_identity_mismatch`,
  `analysis_manifest_floor_attachment_mismatch`, and
  `analysis_manifest_family_semantics_mismatch`.

**Mechanism-only amendment (FIX ROUND 1, 2026-08-15; R-t9-6 carried,
not decided):** the consumer registry additionally admits
`analysis_manifest_transport_ruling_pending`,
`analysis_manifest_runs_root_mismatch`, and
`analysis_manifest_bundle_path_divergence`. A prospective/finalized v3
artifact may faithfully freeze either `exact_stack_only.v1` or
`same_stack_componentwise_worst_case.v1`, including its complete transport
group, condition-domain, backend, floor-field, and rule bindings. Until Ed
selects the open p256 floor branch, a valid governed-transport artifact exits
pre-estimation under `analysis_manifest_transport_ruling_pending`; it is not
misreported as an exact-stack failure. This amendment carries both branches
and chooses neither scientific semantics.

**Boundary-classification amendment (FIX ROUND 3, 2026-08-16):** validator defects at the prospective and consumer boundaries refuse under the newly registered `analysis_prospective_internal_error` and `analysis_manifest_internal_error` codes respectively; they are never classified as malformed input.

### R1 RULED (magistrate synthesis of the rule-11 cold gate, 2026-08-15): freeze-evidence lifecycle — content-bound design ADOPTED WITH THE COMPOSED AMENDMENT SET

Gate record (the ONE homes; not restated here):
docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/ — consult.md
(Sol design), coldgate-adjudicator-ruling.md (cold Fable:
ADOPT-WITH-AMENDMENTS, 7 amendments), coldgate-opus-refuter-findings.md
(Opus refuter: 3 blockers/3 should-fix/7 notes + the magistrate's rule-1
verification note correcting B2's premise).

**Ruling (rule-9 synthesis; the stricter seat prevails on every split):**
1. The content-bound lifecycle design is ADOPTED with the taxonomy
   SPLIT per Opus B1: RE_DERIVABLE (DOCTRINE_PIN, PACK_FAMILY —
   re-derived at ARM, no stored validity at all) / EXECUTION_BOUND (the
   execution-derived kinds — RETAIN boot binding + horizon until Ed's
   execution-environment-fingerprint ruling lands, then migrate per
   that ruling; nothing relaxes ahead of its governing decision) /
   TIME_BOUND / SESSION_STATE_BOUND / TEMPORAL_CAPABILITY per the
   consult. The cold adjudicator's central-claim finding is superseded
   on B1's verified code evidence (unscrubbed subprocess env;
   site-packages-dependent suite runs; live-import comparisons).
2. Staleness gate = CHANGED-SET ENUMERATION (git diff
   derivation_commit..HEAD against a governed, registry-pinned
   irrelevant-path allowlist; complete by construction) as the primary
   conjunct, dependency manifest as an additional conjunct, PLUS the
   cold amendment-2 read-path routing obligation (every deriver read
   routes through recording helpers, test-enforced). Magistrate
   verification (custodied): TODAY neither head comparison nor manifest
   replay executes on the evidence path — the design+amendments
   strengthen an unbounded surface.
3. TERMINAL_REVIEW binds head_tree_oid unconditionally; DRY_RUN keeps
   D-134 cl.7 same-head verbatim; any head relaxation is per-policy-ID.
4. Cold amendments 1,3,4,5,6,7 adopted in full (refusal vocabulary —
   extended by Opus S3's fuller spelling set, all registered before
   issuance; plan-tree enumerated-subtraction normalization; content
   schema key hygiene; environment facts recorded now; grandfathering
   prohibition into D-131 cl.4 text; validator-before-horizon-removal
   ordering). Opus S2 adopted (class as code constant, author refuses
   on registry mismatch). Opus N2 adopted (D-137 delta is labelled an
   AMENDMENT with its zero-reach consequence stated). N7's
   temporal-budget clarification adopted (evaluates the T-0 set
   explicitly).
5. NO GRANDFATHERING (both seats + contract text): the 33 expired v1
   receipts are never revalidated; migration is fresh re-authoring
   within the Phase-2 successor family, one atomic family transaction.
6. Ed's reserved list = the union of both seats' lists (freshness
   semantics per row; horizons + arm-to-consume budget; environment-
   fingerprint comparison semantics; refusal-code spellings/types;
   successor pack IDs + cross-chain numbering; freeze-receipt v2
   predecessor bindings + family publication marker; the irreversible
   successor-family publication and Phase-3 baseline identity — rule-11
   irreversible triggers, Ed approval mandatory). Surface at the
   batched session with the Phase-1 close.
7. Execution: contract-text deltas + implementation ride the Phase-1/2
   work orders under this ruling; every fix round carries C-028 delta
   re-audits.

### R1 implementation amendment — 2026-08-17 (Phase-2 preparation only; no publication)

This amendment executes the reversible schema/tooling tranche of the ruled
R1 lifecycle.  It creates no successor pack, receipt, family marker, custody
root, baseline successor, ARM authority, or publication event.

1. **D-131 clause 4 — no grandfathering is machine-enforced.** A generic
   `joulewise.arm_readiness_evidence_receipt.v1` presented to an R1-registry
   path is a `V1_GRANDFATHERING` refusal role.  The 33 issued v1 receipts
   remain historical bytes only; validation of their historical schema is
   not revalidation, reinterpretation, or permission to consume them.
2. **D-134 clauses 1/3/5/6/9/10 — split schemas and registry authority.**
   `RE_DERIVABLE` uses the exact-key
   `joulewise.arm_readiness_content_evidence_receipt.v1`, which carries
   neither `boot_session_id` nor `valid_until_monotonic_ns`.
   `EXECUTION_BOUND` uses the exact-key
   `joulewise.arm_readiness_execution_evidence_receipt.v1`, retaining both
   fields.  The five-class policy, per-kind and per-row policy IDs,
   irrelevant-path allowlist, ARM horizon/budget, environment-comparison
   policy, and refusal vocabulary have one exact-key lifecycle-registry
   input embedded in the successor row registry.  DOCTRINE_PIN and
   PACK_FAMILY are code-constant `RE_DERIVABLE`; every other generic
   deriver is code-constant `EXECUTION_BOUND`; authoring refuses a
   registry/code mismatch.
3. **Staleness is conjunctive.** The primary gate enumerates every Git path
   changed in `derivation_commit..reviewed_HEAD` and refuses any path absent
   from the authenticated exact-path allowlist.  The additional dependency
   conjunct replays every primary and executed-file binding against both the
   derivation commit and reviewed HEAD.  The plan-tree exception normalizes
   only `arm_attachments.arm_readiness.freeze_receipt.path` and `.sha256` by
   returning that slot to `null`; an added key or any other field change
   refuses.  A source-level release guard mechanically rejects direct
   filesystem, Git, or process reads added to a deriver outside the recording
   helpers.
4. **R1 clause 3 remains unconditional.** A schema-bearing TERMINAL_REVIEW
   source must bind the reviewed `head_tree_oid` exactly.  DRY_RUN_REHEARSAL
   remains under D-134 clause 7's existing same-head rule; neither condition
   is relaxed by a freshness policy.
5. **D-137 is AMENDED, with zero reach over content receipts.** Boot-session
   comparison continues for `EXECUTION_BOUND`, `TIME_BOUND`, and the ARM
   temporal capability wherever their schemas carry monotonic validity.
   The new content schema carries neither field, so D-137's boot/deadline
   rule has zero reach over `RE_DERIVABLE` receipts.  This does not alter any
   issued v1 byte.
6. **D-078 lifecycle refusal registry is structurally complete before
   issuance.** Its eight mandatory roles are `CLASS_MISMATCH`,
   `DEPENDENCY_CHANGED_SET`, `DEPENDENCY_MANIFEST`, `FAMILY_PUBLICATION`,
   `SUCCESSOR_CHAIN`, `TEMPORAL_BUDGET`, `UNKNOWN_POLICY`, and
   `V1_GRANDFATHERING`.  Exact spellings and type labels remain Ed-reserved
   under R1 clause 6 and therefore come only from that authenticated
   registry.  The checked-in placeholder uses explicit `ED_RESERVED:`
   values and refuses issuance/consumption; no placeholder is a reason code.
7. **Reserved semantics remain fail-closed.** Per-row policies, generic
   execution horizons, ARM capability horizon, arm-to-consume budget, and
   execution-environment comparison semantics must all be resolved in the
   single registry.  The six ruled probe/suite kinds record interpreter,
   platform, non-repository `sys.path` descriptors/digests, and (for
   PACK_AUTHENTICATION) inherited-environment value digests now.  Because Ed
   has not ruled comparison semantics, the implementation comparison
   allowlist is intentionally empty and an R1 author refuses before writing
   any output through the registry's `UNKNOWN_POLICY` role.  The
   temporal-budget gate explicitly evaluates the
   `TIME_BOUND` T-0 set; session-state and execution deadlines are not
   silently substituted for that set.  The same registry carries explicit
   unresolved seams for the three successor pack IDs, cross-root freeze
   numbering, the freeze-receipt-v2 predecessor-binding set, and the family
   publication-marker schema; none has a code default or permits generation.

### R1 implementation amendment — FIX ROUND 1 lifecycle enforcement (2026-08-17)

The first contract/execution lens pair rejected the preparation tranche at
`8fd29f7`; this amendment records the converged cures without authorizing a
successor publication.

1. **Freshness class is code-only for the complete evidence vocabulary.** One
   exhaustive table assigns all 29 D-134 evidence kinds plus the ARM capability.
   `DOCTRINE_PIN` and `PACK_FAMILY` are `RE_DERIVABLE`; the ten other generic
   derivers plus `DRY_RUN_REHEARSAL`, `GIT_CHECKOUT`,
   `IDENTITY_PIN_PROJECTION`, `OFFLINE_INPUT_INVENTORY`,
   `PRIVILEGE_INSTALLATION`, and `TERMINAL_REVIEW` are `EXECUTION_BOUND`;
   `BACKUP_PREFLIGHT`, `CLOCK_ATTESTATION`, `CLOCK_PROBE`,
   `MACHINE_PREFLIGHT`, `MAINTENANCE_CENSUS`, `POWERMETRICS_PROBE`,
   `POWER_PREFLIGHT`, and `PROCESS_CENSUS` are `TIME_BOUND`;
   `LAUNCH_RECIPE`, `LEDGER_RESERVATION`, and `ROOT_PREFLIGHT` are
   `SESSION_STATE_BOUND`; the ARM receipt is `TEMPORAL_CAPABILITY`.  A registry
   supplies policy IDs and ruled parameters but validates against this table;
   it cannot define, omit, or override a class.  Temporal-budget selection also
   uses the code table, so relabelling `CLOCK_PROBE` cannot remove it from the
   budget gate.  Production evidence discovery dispatches TIME/SESSION class
   validation, while ARM verification dispatches the single-use temporal-
   capability validation.
2. **Resolved policy shapes are class-specific.** `RE_DERIVABLE` carries no
   horizon and only `NOT_APPLICABLE` environment comparison; TIME/SESSION
   policies carry a positive horizon and `NOT_APPLICABLE`; EXECUTION carries a
   positive horizon and an applicable comparison.  Contradictory resolved
   fields refuse instead of being silently ignored.  The implementation's
   execution-comparison allowlist remains empty, so the outstanding Ed ruling
   still blocks authoring through the registered `UNKNOWN_POLICY` role.
3. **Read routing has a best-effort developer-error guard under D-139.** The
   import-time release lint starts at every deriver and walks ordinary direct
   or simply aliased calls to reachable top-level local helpers until an
   explicit recording boundary.  It catches the recognized direct filesystem,
   Git, and process-read spellings in derivers, the same spellings in those
   transitive helpers, and simple acquired-callable aliases such as
   `reader = __import__("builtins").open`,
   `reader = importlib.import_module("builtins").open`, `reader = os.open`,
   imported-function aliases, and fixed-point aliases of those readers or
   helpers.  These checks catch accidental unrecorded reads; they are not a
   complete Python data-flow analysis or an in-process security boundary.
   **HONEST REGISTERED LIMITATION:** deliberate same-interpreter circumvention
   is outside D-139.  Python code in the same interpreter can construct a more
   dynamic alias, alter module state, or invoke an unmodelled read mechanism.
   Stronger protection would require a separately ruled OS trust boundary;
   this guard makes no claim that no read can escape.
4. **Plan-tree subtraction preserves all non-slot bytes.** Normalization locates
   the unique `arm_attachments.arm_readiness.freeze_receipt` value token and
   replaces only that token with `null`.  It does not parse-and-reserialize the
   surrounding document; whitespace, ordering, and every byte outside the
   enumerated slot remain identity-bound.
5. **D-139 A3 successor IDs install through the registry.** The R1 registry's
   successor field is an exact `ALPHA`/`BETA`/`GAMMA` role map.  Production
   profile routing admits only the ID installed for that role and validates
   the D-139-approved uniform successor shapes.  The approved initial values
   are `d117_floor_qwen25_1p5b_v2`, `d117_floor_qwen25_7b_v2`, and
   `d117_contrast_qwen25_1p5b_vs_7b_v2`; a later shape-conforming generation
   can be installed by registry bytes alone, without editing an ID allowlist in
   Python.  Exact-byte family publication remains reserved and no successor
   bytes are created by this amendment.

### WO-MARGIN-RECORDER-AUTHZ contract ADOPTED (magistrate, 2026-08-15; council Phase 0; Sol design consult adopted)

Consult custodied: docs/process_traces/2026-08-15-recorder-authz-consult/
(the ONE home for the mechanism detail). Cures fleet blocker L4-B1.

**Ruling:**
1. NO new authentication primitive: the recorder reuses the mint's
   session-local `allow_governed_extraction_spec`, invoked NARROWER than
   the mint — exactly once, only in the floor-pack branch, only for the
   plan-tree-selected extraction-spec path, after pack-identity and
   exactly-one-source validation, with an immediate hash comparison of
   the returned bytes against the plan-tree pin BEFORE any census/
   membership processing. Never granted: the GAMMA manifest, reports,
   plan tree, bundles, or the other floor pack's spec.
2. The grant exempts only the recursive lexical estimator_registration
   ban for that one file; duplicate-key/UTF-8/finite-number/grammar/
   digest-stability/path-containment checks all survive. No change to
   joulewise/authentication_io.py or any public API.
3. The synthetic census tests are REPLACED by frozen-pack regressions
   modeling the REAL re-specced cell shapes (the green-suite-broken-seam
   specimen dies in the same commit) — per the consult's attempt/result
   table.
4. Execution = WO-MARGIN-RECORDER-AUTHZ (council Phase 1). This
   executes D-133's close-out gate; it amends no scientific semantics.

### M-2 GATE AMENDMENT — separate entry (heading added 2026-08-15; recorder-race gate mechanic caught it misfiled inside the recorder adoption entry)

**M-2 GATE AMENDMENT (magistrate, 2026-08-15, per the remanded cold gate's composed verdict —
docs/process_traces/2026-08-15-m2-coldgate/composed-verdict.md, the ONE home):** the engineering
core is UPHELD (receipts govern over descriptive bytes; frozen bytes are never repaired). The
instrument is NARROWED: (a) the "overrode a NO-GO reading" premise is STRICKEN — no machine gate
or §5C clause reads draft_status; M-2 resolves a human-operator ambiguity only; (b) the "every
arm packet must cite this ruling" duty is STRICKEN — replaced by one informational operator note
in the successor packet; (c) the retirement clause is corrected — retirement occurs at successor
freeze ONLY IF the Phase-2 generator work makes draft_status freeze-aware (currently hardwired at
every JSON emission site); (d) the override's exhaustive scope is the three 2026-08-13 receipt
hashes (ddbbb409…1738, a6dec2c2…7870, 2ef73bf0…106f), retiring per pack — it may never be cited
for any other pack; (e) the contrast pack's pending-ratification/TODO markers are OUTSIDE M-2 and
carry their own RULING-REQUIRED row; (f) the #149 --plan argv divergence must reconcile under R2
before any arm.

### WO-LAUNCH-BINDING contract ADOPTED (magistrate, 2026-08-15; council Phase 0; Sol design consult adopted)

Consult custodied: docs/process_traces/2026-08-15-launcher-binding-consult/
(the ONE home for the mechanism). Cures fleet blocker L8-B7 (launch
without ceremony not machine-caught; confirmed by both DG lenses).

**Ruling:**
1. Every D-117 physical launch is NO-GO until machine-enforced: the sole
   supported production route is the reviewed launcher
   (scripts/launch_window.py), invoked PERSONALLY by
   Ed after inspecting the ARM verification result, performing: atomic
   no-clobber consumption-primary claim (the single-use linearization
   point, fsynced) → verify_consumed_launch replay (arm receipt/PASS/GO/
   supersession, boot + monotonic validity, reviewed HEAD + committed
   pack digest, context/roots/backups/reservation/locks, launch-manifest
   + window.env + chain bytes, exact final argv) → execve on the exact
   frozen foreground argv. No spawn-and-return, no retry loop.
2. One-use handoff token via inheritable anonymous FD only (never argv/
   env/file); consumption record stores its SHA-256. Consumption v2
   record additions per the consult.
3. Downstream lineage: collection, reduce, verdict, extraction, and mint
   consumers authenticate descent from the consumption record; absent
   lineage = refusal (reason-codes per the consult, registered under
   D-078's closed vocabulary before issuance).
4. This is strictly additive fail-closed machinery (no existing guarantee
   weakens); the D-134 clause additions + implementation take the full
   C-028 gauntlet with adversarial refuters on the contract delta text —
   the cold review rides the gauntlet.
5. Execution = WO-LAUNCH-BINDING (council Phase 1); runbook §6/E-step
   deltas + the ceremony-skip regression battery per the consult.

### D-134/D-137 launcher-binding amendment — 2026-08-15

D-134 clause 8 is narrowed: the reviewed launcher is the sole supported
production route for atomically claiming the single-launch capability;
Python does not authenticate its caller.  The atomic no-clobber primary is
the single-use enforcement.  The consumption receipt alone does not prove a
launch. Authorization attaches only to the chain start descended from the
one-use inherited anonymous-FD handoff.

The following clauses are added to D-134:

11. The sole production entrypoint performs consume → revalidate → `execve`;
    Ed invokes it personally after inspecting ARM `PASS`/`GO`, and no
    automated verdict invokes it.
12. Consumption is irrevocable. Start, settle, and completion are append-only
    successor receipts; absence or any post-claim failure never reopens the
    capability.
13. Collection, post-hoc reduction, whole-window verdict, extraction, and
    mint independently authenticate launch lineage using the D-078 vocabulary
    registered below. Backup and quarantine remain available on refusal.
14. Crash injection, race, ceremony-bypass, mutation, and every-downstream-
    stage tests are release gates for this mechanism.

D-137 is clarified accordingly: current-boot comparison applies through the
launcher and chain entry. Historical postcollection consumers compare the
boot identity recorded in the consumption, lifecycle, and bundle records to
one another, not to the machine's current boot, so a later reboot does not
destroy otherwise valid immutable evidence.

### D-078 registry amendment — 2026-08-15: launch-consumption lineage refusals

D-078's closed claim-refusal vocabulary is amended additively for the adopted
WO-LAUNCH-BINDING contract. The following six exact spellings are registered
at collection, post-hoc reduction, bound derivation, whole-window verdict,
extraction, and mint boundaries; no synonym, generic provenance downgrade, or
latest-wins interpretation is permitted:

- `launch_consumption_missing` — a required consumption reference, primary,
  or sidecar is absent;
- `launch_consumption_invalid` — consumption/lifecycle custody is
  noncanonical or schema-invalid, has a bad sidecar/digest or namespace, or
  has an invalid predecessor chain;
- `launch_binding_mismatch` — authenticated records disagree on pack, plan,
  reviewed HEAD, arm context, collection boot, session IDs, roots, launch
  recipe bytes, or exact exec argv;
- `launch_lineage_conflict` — members or artifacts name more than one
  consumption/pack/boot lineage;
- `launch_lifecycle_incomplete` — start or settle is absent, or completion is
  absent at verdict, extraction, or mint;
- `launch_handoff_invalid` — the chain lacks the one-use inherited anonymous
  FD token, its SHA-256 disagrees, or the handoff/start is replayed.

These are terminal claim refusals. Backup, quarantine, and immutable evidence
preservation remain available. A refusal never reopens a consumed capability;
recovery requires a newly frozen bracket session, new attempt IDs, and a new
ARM receipt.

### RECORDER CHECK-TO-GRANT RACE — registered limitation + WO-RECORDER-GRANT-IDENTITY queued (magistrate, 2026-08-15; rule-11 cold gate, composed verdict)

Gate record (the ONE home): docs/process_traces/2026-08-15-recorder-race-coldgate/ —
packet + non-author assemble.py, both cold rulings, composed-verdict.md. The gate fired on the
rule-11 mandatory trigger (second fix round on the same defect class) AND the standing escalation
trigger (F-9: two rounds, same signature — the grant re-resolves the caller's path inside the
callee at authentication_io.py:352, so no caller-side patch is atomic).

**REGISTERED LIMITATION (L1 shape):** the margin recorder's governed-vocabulary grant
(window_duration_margins.py) is subject to a check-to-grant TOCTOU: a concurrent local process
with repository write access can, mid-run, alias the selected floor-spec path so
allow_governed_extraction_spec registers the OTHER floor pack's identity (executed:
10/400 and 7/1200 uninstrumented iterations; a swap-and-revert yields a SILENT success with an
attacker-chosen identity granted). **RECEIPT INTEGRITY IS INTACT:** every post-grant read in the
recorder is hash-pinned (expected_sha / member_config_sha256), so a stolen exemption cannot alter
a receipt today — the harm is a contract-boundary violation (clause 1's "never granted the other
floor pack's spec") and a forensic refusal-code downgrade, not a receipt forgery. **Bounding
workflow rule:** the recorder runs single-operator with no concurrent repo-writing process during
a close-out; this is documented in the runbook §11 close-out preamble (propagation owed with the
WO). **Justification for interim acceptance:** receipt integrity intact + the real cure is an
authority-plane amendment (below), not a caller-side round three.

**THREAT-MODEL RULING (conservative):** the concurrent unprivileged local writer is NOT ruled out
of the instrument's threat model. docs/contracts/calibration_ledger.md bounds the model by
authority, not timing, and is SILENT on races; L2's sibling writer-signature finding was
confirmed-and-withheld pending a ruling that did not exist; precedent (the arm-author caffeinate
volatile-census blocker; the A→B→A TOCTOU design kill; the ledger lock's hardlink-fail-closed
hardening) grades this class blocker-and-fix. Declining to declare it out-of-model to purchase a
merge. **ED-WEIGHTED (risk appetite, non-blocking):** if Ed's appetite rules the concurrent local
writer out of model on a single-operator machine, WO-RECORDER-GRANT-IDENTITY drops to this
registered limitation alone. Surfaced at the batched session with both cold rulings.

**WO-RECORDER-GRANT-IDENTITY (queued, TASK_QUEUE; OWN future rule-11 cold gate — authority plane):**
the minimal true cure is to stop allow_governed_extraction_spec re-resolving its argument — accept
a caller-verified identity verbatim, or key the grant on an fd / (st_dev,st_ino) — which edits
joulewise/authentication_io.py and therefore amends the adoption ruling's clause 2 ("no
authentication_io.py change"). F-10's post-grant grant-delta verification (with the read-only
accessor clause 2 currently forbids) folds into this WO. NOT licensed as a caller-side patch.

**LANDS NOW on impl/wo-margin-recorder-authz (independent, both seats):** F-5 — the unnormalized
V2AuthenticationInputError escaping _pack_inventory on a non-adversarial path (_json_object reads
outside its try); normalized to WindowDurationMarginsRefusal. The recorder branch then merges on
receipt-soundness (original blocker L4-B1 cured; round-1 static-invariance guard retained; F-5
landed) WITH this limitation registered — not as "race closed."

### D-078 registry amendment — 2026-08-15: WO-T0-PRODUCER acquisition refusals

The shipped T-0 acquisition wrapper adds this closed twelve-code vocabulary.
Every spelling is a fail-closed producer refusal and none licenses ARM,
launch, or a claim:

- `evidence_author_t0_capture_usage_invalid`
- `evidence_author_t0_capture_environment_invalid`
- `evidence_author_t0_capture_boot_probe_failed`
- `evidence_author_t0_capture_plan_invalid`
- `evidence_author_t0_capture_terminal_review_missing`
- `evidence_author_t0_capture_sequence_invalid`
- `evidence_author_t0_capture_clock_observation_invalid`
- `evidence_author_t0_capture_command_failed`
- `evidence_author_t0_capture_result_invalid`
- `evidence_author_t0_capture_output_collision`
- `evidence_author_t0_capture_io_error`
- `evidence_author_t0_capture_internal_error`

The wrapper accepts only pack/custody/window-plan paths and, at E-4, two
prompted operator observations — the independent-clock UTC literal and the
pasted prior network-time state output; both are registered irreducible
operator observations, not derived values. Boot identity, monotonic bounds,
commands, context, manifest, digests, and conclusions are derived. A capture
is canonical and no-clobber; a preserved nonzero/invalid-result capture still
refuses and is never permission to continue.

**NEEDS_RULING — R2 frozen-generator follow-up.** The current ALPHA and BETA
`plan_tree.json` bytes still store repository-relative `plan.path` values,
and all three frozen generators' `freeze_aware_reservation_plan_arguments`
omit `--plan` while preserve mode is true. Those generators and pack bytes
are outside WO-T0-PRODUCER's exhaustive write scope, while R2 requires the
shared resolver to reject rather than basename-repair them and M-2 clause (f)
requires the generated argv to converge. Options considered: (A) weaken the
resolver or repair at runtime (rejected by R2); (B) edit frozen generators and
pack bytes in this work order (not authorized); (C) include both generator
repairs in the lead-owned Phase-2 successor freeze transaction. Recommendation:
option C, emitting pack-relative `calibration_plan.json` and deriving the
generated reservation `--plan` from that reference before the one atomic
re-freeze. Until ruled and executed, ALPHA/BETA positive T-0 rehearsal and the
generated-stage E-9 equivalence remain blocked; GAMMA supplies the conforming
real-pack positive resolver regression.

### T-0 CAPTURE PROVENANCE (F4) — honest-contract fix now + trusted-operator scope call DEFERRED to Ed/advisor (magistrate, 2026-08-15)

Consult custodied: docs/process_traces/2026-08-15-t0-capture-provenance-consult/
(the ONE home; recurred across THREE review rounds — B-execution,
singlelens F4, the T0-producer review — so per the standing escalation
trigger this was a CONSULT, not another patch).

**The finding:** the T-0 evidence author authenticates capture BYTES, keys,
typed monotonic values, boot identity, freshness, and ordering — but NOT
which process produced them. A hand-authored canonical JSON with fabricated
monotonic_ns, or a call through capture_step's public execute/monotonic_ns/
utc_now injection seam, is indistinguishable to the consumer from a genuine
capture. The council's WO-T0-PRODUCER scope wanted "boot-bound monotonic-ns
fields NO HUMAN CAN HAND-PRODUCE" — that property is NOT enforced, so the
contract currently OVERCLAIMS.

**Distinct from the recorder race (do NOT reuse its justification):** the
recorder race stayed in-model with an accepted limitation BECAUSE post-grant
receipt integrity survived. Here forged historical dwell DIRECTLY DEFEATS
T-0's semantic purpose (binding the arm to a real quiet window). So a
limitation here is acceptable ONLY through an EXPLICIT trusted-operator /
no-concurrent-writer assumption — never by claiming integrity survives.

**MANDATORY HONEST-CONTRACT FIX (folds into the WO-T0-PRODUCER branch; not
optional, truthful either way):** (a) supersede D-134 clause 6's
"derive-never-enter … no human can hand-produce" with a production-interface/
ceremony rule that does NOT assert operator-fabrication resistance; correct
the runbook + author docstrings to match; (b) remove the PUBLIC
execute/monotonic_ns/utc_now injection seam from capture_step (tests use a
private/test-only hook), so casual/accidental fabrication is harder and the
public CLI has no monotonic override.

**REGISTERED LIMITATION (v1):** T-0 capture provenance is TRUSTED-OPERATOR —
deliberate fabrication by the operator is not defended against; the real
binding to a real quiet window is the human §5A tap + the terminal-review
attestation + the single-operator assumption, all STATED as the limitation.

**RULING-REQUIRED — Ed + advisor (Rivoire; metrology-rigor bar); PAPER-SCOPE,
non-blocking:** does the MVP measurement-integrity claim rest on
trusted-operator T-0 evidence (accept the limitation, publish it labelled),
or does the claim need the consult's OPTION (a) — a hardened signed capture
app + external verifier issuing a pre-E-4 nonce + App Attest assertion
(Secure Enclave / attestation chain / remote verifier key) binding
nonce+app+HEAD+boot+monotonic-transcript+argv+output-hashes, countersigned,
author-pinned? Option (a) genuinely moves the trust root outside Ed but adds
a server, app distribution, and a macOS-27 dependency — disproportionate to
this WO, real for a stronger paper. The honest-contract fix lands regardless;
this call only decides whether option (a) becomes a future work item.

### D-134 amendment — 2026-08-15: T-0 derive-never-enter is a production ceremony, not producer attestation

This amendment supersedes D-134 clause 6 with the ruling's honest production
contract:

> Derive-never-enter is a production-interface and ceremony rule, not
> independent producer attestation. When faithfully invoked, the production
> CLI derives row values, command captures, timestamps, identities, and
> digests; operators supply only paths and the registered irreducible
> observations (at E-4, exactly two: the independent-clock UTC literal and
> the pasted prior network-time state output). Consumers authenticate
> canonical bytes, same-boot
> freshness/order, and fresh current-state probes, but cannot prove that the
> T-0 input bytes originated in the shipped wrapper. Deliberate fabrication by
> the trusted operator/authority is outside the v1 single-authority threat
> model.

The previously claimed property that a human cannot hand-produce acceptable
historical T-0 capture bytes is **NOT enforced**. Removing production clock
and execution injection parameters is misuse resistance, not a security
boundary or independent proof of producer origin.

**REGISTERED LIMITATION (v1):** T-0 capture provenance is TRUSTED-OPERATOR —
deliberate fabrication by the operator is not defended against; the real
binding to a real quiet window is the human §5A tap + the terminal-review
attestation + the single-operator assumption, all STATED as the limitation.

### WO-LAUNCH-BINDING F2 (lineage-locator) — mechanism ADOPTED + WO staged (magistrate, 2026-08-15; Sol design consult)

Consult custodied: docs/process_traces/2026-08-15-launch-lineage-consult/
(the ONE home for the 8-point authentication chain + schema). Resolves the
F2 blocker: how a child collection/calibration writer receives the
authenticated launch lineage WITHOUT argv/env.

**Adopted mechanism (option c backed by a):** at settle,
record_launch_lifecycle_event("settle") publishes a fixed root-local
locator `<claim_runs_root>/.joulewise-launch-lineage.json` and
`<bound_runs_root>/.joulewise-launch-lineage.json` (+ GNU sha256 sidecars),
canonical/no-clobber/fsynced, never repaired; partial publication burns
the attempt. Roots come from the consumed arm receipt's authenticated
arm_context. Schema `joulewise.launch_lineage_locator.v1` (exact-key);
CONSTANT basename (identities live in authenticated CONTENT, never the
path — no scanning/"latest" ambiguity). Writers DERIVE the path from their
own --runs-dir / --output-root.parent (calibration requires
output_root.name == "instrument_validation") — no receipt path, token, or
lineage JSON in child argv/env. Before any bundle/custody dir/provenance/
slot claim the writer runs the consult's 8-point authentication (locator +
consumption predecessor + pack digest/HEAD/IDs + start predecessor +
handoff_token_sha256 without accessing the token + settle ordering + boot
equality + config membership + runs-root match); reduce/mint reauthenticate
the same. Fail-closed refusals REGISTERED under D-078 (append at
implementation). Lineage receipt is SESSION/boot-bound (matches the arm
capability lifetime), NOT R1 content-bound.

**RESIDUAL (recorded):** a fixed authenticated locator is intentionally
observable; it stops absent-lineage and wrong-session bypass but does NOT
cryptographically prove each writer's Unix parent is the frozen chain. The
existing fresh-root / campaign-lock / exact-membership / calibration-slot
single-use gates cover ordinary/direct-invocation bypass. Hostile same-UID
mid-window process injection is a LARGER contract (a frozen per-stage
dispatcher minting one-use stage receipts via anonymous FD) — NOT smuggled
into this mechanism; rule separately IF in scope (Ed risk-appetite, same
family as the recorder-race + T-0-provenance trusted-operator calls).

**WO-LAUNCH-BINDING STAGES (re-scoped):** (1) launcher core + verify_
consumed_launch + the locator publication at settle + retire the public
standalone consume CLI [impl/wo-launch-binding — the launcher core is the
current WIP checkpoint]; (2) writer-side derivation + 8-point auth +
stamping [after this adoption]; (3) reduce/mint downstream reauthentication
gates; (4) successor-config launch_lineage_required flag [PHASE 2 — frozen
packs can't be edited in place; lands with the successor-family freeze
transaction under R1]. The full binding is contract-bearing → C-028
gauntlet before merge.

### D-130 closure recorded — 2026-08-15

WO-CI-RESTRUCTURE is **CLOSED**. PR #129 (`7a76a29`) landed the
registry-certified matrix proof, and hosted run `31541829071` succeeded in
3h20m48s from 2026-08-11T22:18:21Z; this is D-130's required second
independent decisive execution. Hosted run `31518739878` is a second success.
Per the pinned magistrate disposition, the temporary local-decisive admission
therefore expired at closure and the dispatch-only workflow restriction is
lifted.

**Citation consequence:** D-130's temporary mandatory wording —
“lead-verified locally … + CI-verified transport/authentication chain” — is no
longer required for future summaries, which may accurately cite the
restructured hosted proof as hosted CI evidence. This does not retroactively
change the historical provenance of PR #122's merge decision: descriptions of
that merge must still identify the custodied local decisive execution rather
than recast it as a hosted decisive run.

**ADDENDUM (2026-08-16): automatic triggering DEFERRED, closure unchanged.**
Restoring push/pull_request triggers exposed that the decisive matrix is not
runnable at current main: every leg fails at fixture setup with
`AttributeError: module 'scripts.mint_floor_artifact' has no attribute
'STACK_IDENTITY_DOMAIN'` (tests/test_mint_floor_artifact_generalized.py:4974;
failed PR runs 31928874193, 31929587168, 31929945739). This is fixture/API
drift accumulated while the workflow was dispatch-only — a runnability
failure at setup, not a leg contradiction of proof semantics, so it is not a
stop signal and does not reopen D-130 (the second independent execution
remains a historical fact at #129's head). The workflow returns to
`workflow_dispatch` and WO-PROOF-RUNNABILITY-REPAIR is registered: repair the
fixture drift under the full proof-semantics trust gauntlet the
WO-CI-RESTRUCTURE registration prescribed, prove the matrix green at a
current-main head, then restore automatic triggering in the same change.

### D-078 amendment — 2026-08-15: locator and campaign-writer enforcement landed

The campaign half of WO-LAUNCH-BINDING stage 2 implements the already
registered six-code launch-consumption vocabulary without adding aliases.
At marker-bearing collection admission, a missing locator/primary/sidecar is
`launch_consumption_missing`; malformed canonical bytes, a bad sidecar, or an
invalid predecessor chain is `launch_consumption_invalid`; a wrong root,
role, boot, pack, plan, reviewed HEAD, arm-context digest, recipe, argv,
config membership, or lifecycle phase is `launch_binding_mismatch`; unequal
authenticated claim/bound locator payloads are `launch_lineage_conflict`;
absent start/settle is `launch_lifecycle_incomplete`; and FD/token/start
replay remains `launch_handoff_invalid` at chain entry. The outer campaign
preflight and inner bundle writer each derive and authenticate from the fixed
root-local locator. They never receive lineage through argv/environment and
never reapply the arm's short T-0 expiry after authenticating that consumption
occurred within it. Calibration writer enforcement remains the separately
owned next stage-2 landing; downstream stages 3-4 and the C-028 gauntlet still
gate launch readiness.

**Fix-round authentication clarification (2026-08-15):** collection's inner
writer authenticates the exact config path already present in the ordinary
child `run` argv and requires its raw-byte digest at that exact pack-relative
inventory member; parsed semantic equality alone is insufficient. The inner
metadata stamp also carries the authenticated selected-locator content digest.
The outer campaign retains its own authenticated lineage and locator digest,
then reopens each child bundle after process completion and requires canonical
lineage-byte plus locator-digest equality. A consistent replacement between
the outer and inner reads is therefore terminal `launch_lineage_conflict`; the
attempt evidence is preserved and is never reported successful. This adds no
receipt, token, or lineage carrier to child argv or environment. Calibration
writer enforcement remains deferred to the calibration-side stage-2 landing,
downstream reduce/extract/mint enforcement remains stages 3–4, successor config
markers remain a Phase-2 freeze transaction, and physical launch remains
NO-GO pending those gates and the full C-028 gauntlet.

### WO-LAUNCH-BINDING fix round 2 — private required-context API and AXI Phase-2 release gate (lead-adopted consult, 2026-08-15)

F3 adopts `ADOPT_PRIVATE_REQUIRED_CONTEXT_API` exactly.  The public-named
consumption wrapper and both caller-frame/file-identity guards are deleted;
caller identity is not represented as security.  The sole supported
production route is the reviewed launcher calling one underscore-named,
non-exported consumer with mandatory authenticated arm and launch-manifest
values, their exact primary/artifact digests, the bound roots, exact exec
argv, and handoff-token digest.  At reconciliation time, the callee
independently reopens the arm receipt and follows its digest-pinned
`evidence[]` LAUNCH_RECIPE item through the authenticated evidence receipt's
`facts[0].source_path` / `source_sha256` into the custody-root T-0 source
record.  That source record's `input_artifacts[]` is the identity anchor: the
caller manifest must occupy the root-locally derived
`arm_readiness.t0.inputs/launch-manifest.json` path with the attested bytes,
and `window.env` and `window-chain.zsh` must match their attested paths and
bytes.  The callee also reconciles boot, custody-contained window root, and
exact foreground argv before any consumption publication, and replay repeats
the same reconciliation before PASS.  This required-context API is an
ordinary-misuse boundary only.  The atomic no-clobber consumption primary is
the **only real enforcement** and the single-use linearization point; every
later complete caller loses that write.

The T-0 author validates `window-chain.zsh` content only for exactly one
reviewed `REPO=` line and the absence of a `QUARANTINE_ROOT=` assignment.
Consumption therefore binds to the **attested** chain, not to a generally
reviewed chain; the remaining pre-arm chain-authoring surface is explicit.
The reconciliation claim is likewise bounded to reconciliation time: the
registered hostile-same-UID residual includes an exec-time chain swap after
the final read and before `execve`.

**HONEST REGISTERED LIMITATION:** deliberate in-process invocation of the
private consumer with forged-but-complete valid inputs is indistinguishable
from the supported route.  Python code in the same interpreter, or code under
the same trusted UID, can import private functions, reconstruct readable
inputs, alter module state, or invoke the launcher.  This mechanism proves
single use, not caller identity or Unix parentage.  Stronger protection needs
a separately ruled OS trust boundary.  Ed's batched risk-appetite list carries
this hostile-same-UID/same-interpreter family with the recorder race and T-0
provenance limitations; this work order does not silently expand that threat
model.

**ROUND-3 COLD-GATE RECORD:** the caller-identity/data-authentication pivot was
recorded by the escalation consult before the third failure, so it is a
contemporaneous distinction rather than a post-hoc reclassification.  The
standing trigger was discharged twice: by the consult after failure two and
by the rule-11 cold gate after failure three; licensing this implementation
round exercises the cold instance's authority rather than bypassing the
trigger.  The counterargument remains explicit: under F3's original invariant
framing (standalone consumption not fully retired), all three failures can be
read as one class, and mechanism-level repartition without a prior-record test
could make the trigger unfireable.  Future reauthentication designs must name
and file:line-confirm the comparison anchor and carry complete-but-foreign,
attack-shaped regressions.

NDF1 adopts `DEFER_WITH_PHASE_2_RELEASE_GATE`.  D-078's closed vocabulary is
amended additively with `launch_lineage_axi_unsupported`: a marker-bearing AXI
v2 campaign is refused before child dispatch because the current fixed
root-local locator contract covers flat/root-local writers only.  This is a
release/scheduling boundary, not an exclusion of AXI from launch lineage;
non-marker AXI campaigns retain their prior behavior.  No nearest-ancestor
search and no per-attempt locator replication are permitted.

The Phase-2 release gate is the consult's exact mechanism: freeze an
authenticated successor-schema derivation descriptor (for example,
`axi_attempt_v1`) and implement exact AXI layout projection
`TOP/axi_attempt_bundles/<manifest-id>/<entry-id>/a<ordinal>`, mechanically
derive `TOP`, then authenticate the successor manifest/config/entry/digest and
attempt-directory relationship before opening exactly TOP's fixed locator.
Until that projection and its adversarial regressions land, no successor pack
may freeze or issue `launch_lineage_required` on an AXI config family.

### D-138 — D-079-pinned estimator-input changes are merge-staged into the atomic re-freeze (magistrate, 2026-08-15; promoted from session ruling R-t9-4 at the T9 close)

Any change to a file in the issued D-079 acceptance artifact's
`estimator_code_sha256` pin set (`joulewise/powermetrics_fiducial.py`,
`joulewise/uncertainty_evidence.py`, `joulewise/adapters/powermetrics.py`,
`joulewise/reduce.py`) deliberately stales the issued artifact: the canonical
suite's authenticated-staleness fan-out is a LIVE INVARIANT (the suite proves
the issued artifact matches real bytes), and re-keying those tests to fixtures
to make such a branch mergeable is FORBIDDEN — it would delete the invariant
that catches accidental estimator drift.

**Consequences:** (1) such branches complete their C-028 gauntlet normally but
are MERGE-STAGED: they merge ONLY inside the atomic Phase-2 successor
re-freeze transaction that re-issues the acceptance artifact and every
dependent pin (first instance: `impl/wo-detect-pulses-budget` @ `5449e58`,
carrying WO-DETECT-PULSES-BUDGET + the calexits flake fix). (2) Follow-on work
that must touch the same pinned files RIDES THE SAME BRANCH rather than
opening a second staleness event on main (the inheritance corollary; the
flake fix is the precedent). (3) The re-issue and pin update remain lead-owned
inside the re-freeze; tests may re-key only private synthetic fixtures.
Authority context: R-t9-4 (docs/run_reports/2026-08-16-t9-session.md), the
2026-08-15 D-078 registry amendment on the staged branch, and the council's
Phase-2 re-freeze ruling.

### WO-LAUNCH-BINDING stage 3 downstream-authentication checkpoint — 2026-08-16

The authorized downstream implementation keeps D-138's D-079 estimator-input
pin intact: `joulewise/reduce.py` is unchanged.  The analysis-input boundary
reopens bundle receipts, requires one identical full lineage across the
effective corpus, and carries that lineage into the reduction audit row.  That
is a sound gate for analysis-engine consumption, but it does **not** close the
standalone post-hoc reduction boundary: `joulewise.cli._cmd_reduce` calls the
pinned reducer directly and is outside this stage's authorized write set.
Calling the analysis-only gate sufficient for the standalone verb would be a
dodge.  The reducer can remain pure arithmetic; the minimal missing gate is at
that CLI caller, before `reduce_bundle`, with the authenticated full lineage
added only to marker-bearing prospective reduction output.

Marker-bearing NEG-8 derivation directly authenticates every member without
requiring completion and seals one identical settled lineage into the bound.
Marker-bearing whole-window verdict authentication reopens the members, both
selected calibration evidence files, and the bound; it derives and requires
the deterministic completion receipt through `authenticate_launch_lineage`
and seals the identical settled full lineage into the evaluation basis.
Extraction independently reopens every source with completion required,
refuses marker/legacy or nonidentical mixtures, and carries the common full
lineage in both member basis rows and the report.  The settled lineage remains
byte-identical across carriers; its schema's `completion: null` is not
rewritten after collection, because historical authentication derives the
completion path from the authenticated consumption identity.

Mint-side estimator entry points now reopen the full extraction-spec source
set and governing whole-window sources, require completion, and compare the
directly authenticated full lineage with the extraction report.  A copied
lineage without source receipts is `launch_consumption_missing`; no new
D-078 code is introduced.  Legacy artifacts remain dormant when neither
sources nor report claim launch lineage.

R-t9-8 grants that scope and closes both remaining boundaries while preserving
D-138: marker-bearing standalone reductions authenticate before the unchanged
reducer is called and carry the full authenticated lineage only in the new
prospective artifact; legacy reductions remain byte-stable.  Detection-floor
artifact v2 follows the codebase's additive closed-schema precedent by
registering `provenance.launch_lineage` as an optional slot without changing
the schema version, and both mint constructors propagate only a directly
authenticated, identical lineage while legacy artifacts omit the slot.

The two mint scripts are separately hash-pinned as T-0 sources by the frozen
packs' `arm_readiness.sources/mint-trust.json`, but those packs are
non-selectable and no live suite invariant binds the issued hashes.  Their
source pins are therefore **superseded-pending-refreeze**: the Phase-2 atomic
successor re-freeze transaction re-derives every T-0 source at the successor
head.  Editing them here is sanctioned for main and is **not** a live-invariant
break, unlike D-138's issued D-079 estimator-input pins.

### D-139 — Ed's batched rulings A1-A3 (Ed, 2026-08-17, in-session; packet docs/process/ed-batch-packet.md)

**A1 — In-process adversary RULED OUT OF MODEL (registered limitation,
family-wide).** Ed: "no adversarial programs affecting the measurement can be
assumed." Consequences, effective immediately: (1) WO-RECORDER-GRANT-IDENTITY
is RETIRED to the registered check-to-grant limitation — no implementation, no
cold gate (the design consult remains custodied at
docs/process_traces/2026-08-16-grant-identity-consult/ should the appetite
ever change); (2) the T-0 trusted-operator limitation v1 is FINAL for the MVP
claim (option-(a) attested capture stays closed); (3) the launch-binding
forged-complete-context residual is FINAL as registered. The paper states the
assumption once, plainly.

**A2 — Gamma scientific rulings.** (1)+(2) Ed DELEGATED to the
magistrate/Sol; the consumption-edge consult's recommendation is ADOPTED
verbatim: ONE primary Holm family, alpha=0.05, m=2, containing the decode and
prefill_p256 contrasts, two-sided tests with pre-registered positive
scientific directions; a missing/non-estimable member stays in the frozen
m=2; the frozen cross-arm block-strata mapping (block numbers 1-10 across
both arms) carries the family (mechanism merged in #155). These values enter
the gamma prospective manifest's families block at the production freeze.
(3) p256 floor: DEDICATED ARTIFACT (no p128→p256 transport rule) — Ed's
preference, at zero extra collection cost: the funded fixed-256-token prefill
floor cells are already in the frozen packs (#138). The consumption edge's
analysis_manifest_transport_ruling_pending branch remains permanently
refusing (dormant), as designed.

**A3 — Phase-2 reserved approvals: recommended defaults APPROVED** (uniform
`_v2` successor pack IDs; chain-monotonic `freeze-0002` with explicit
predecessor bindings; the existing operational horizons — 20-minute volatile
/ six-hour procedural — carry forward as the approved freshness defaults).
The environment-fingerprint comparison semantics remain an open Ed ruling
(the R1 fail-closed seam stands). RESERVED STILL: the final exact-byte
publication confirmation at the transaction's irreversible point — Ed
confirms when the bytes exist.

**SHAKEDOWN-FIRST SEQUENCING DIRECTIVE (Ed, same message):** "focus first on
doing the minimal verifying runs to make sure the instrument is proper and
not being polluted by any other signal." The first quiet-machine consumption
after a READY-candidate verdict is MINIMAL INSTRUMENT VERIFICATION — the
ED-Q-L9-3 quiet-state baseline and calibration-only shakedown runs proving
signal purity — BEFORE any claim window. Exact workload consistency is
explicitly subordinate to instrument-purity verification for these first
runs. The claim windows (alpha/beta/gamma) follow only after the shakedown
evidence is clean.
