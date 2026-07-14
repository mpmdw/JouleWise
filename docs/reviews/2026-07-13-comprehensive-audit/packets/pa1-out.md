```json
[
  {
    "id": "PA1-001",
    "severity": "blocker",
    "issue": "WO-002 binds implementation to packets/ed-rulings.json R3 and forbids re-ruling, but that file contains only R1 and R2. The succeeded-summary/no-idle-baseline admission decision is therefore undefined.",
    "suggested_resolution": "Add an explicit R3 ruling with the exact admission semantics and update the authority reference, or restore NEEDS_RULING behavior until that ruling exists."
  },
  {
    "id": "PA1-002",
    "severity": "blocker",
    "issue": "The T11 fold assigns tests/test_corpus_strict_validation.py to S1 WO-004, but S1's union_write_scope omits it while S2's union_write_scope still claims it. The declared parallel scopes are not disjoint from the actual work-order scopes.",
    "suggested_resolution": "Move the test path from the S2 union to S1, then rerun the mechanical scope-disjointness check."
  },
  {
    "id": "PA1-003",
    "severity": "blocker",
    "issue": "WO-004's C2-029 admission enforcement consumes provenance-field semantics defined by WO-016, yet WO-004 depends only on WO-003 and is ordered early in parallel S1 while WO-016 lands late in S2. A conflict note saying \"serialize or freeze\" is not an enforceable dependency.",
    "suggested_resolution": "Make WO-016 a hard predecessor of the C2-029 portion, split that portion into a post-WO-016 order, or freeze the complete field names and semantics in the register before dispatch."
  },
  {
    "id": "PA1-004",
    "severity": "blocker",
    "issue": "WO-005 requires a retained-corpus re-reduction comparison artifact reconciling -0.498% and -0.93%, but its verification_command runs only unit tests and its bounded_scope names no durable comparison-artifact path. The blocker repair can pass without producing its principal acceptance evidence.",
    "suggested_resolution": "Name a durable artifact path, add it to bounded_scope, and add an executable retained-corpus comparison command that writes and validates the authoritative reconciliation."
  },
  {
    "id": "PA1-005",
    "severity": "blocker",
    "issue": "Court-created WO-040 is stream S2 and a hard prerequisite of WO-019, but fix-streams.json omits it from S2 work_order_ids and suggested_order. The published stream plan can close S2 without executing WO-040.",
    "suggested_resolution": "Add WO-040 to S2 and place it before WO-017 and before S4 is released; refresh all stream-close and resume-plan summaries."
  },
  {
    "id": "PA1-006",
    "severity": "blocker",
    "issue": "Four dependencies are not work-order IDs: WO-019 uses \"WO-017 (labeling decision only)\", WO-022 and WO-031 use annotated soft dependencies, and WO-027 embeds an Ed precondition. A dependency resolver cannot distinguish edges from prose.",
    "suggested_resolution": "Restrict dependencies to exact IDs and introduce explicit soft_after, required_rulings, and external_preconditions fields. Split partial-order milestones into distinct work orders where necessary."
  },
  {
    "id": "PA1-007",
    "severity": "blocker",
    "issue": "The ordering constraints for WO-021 and WO-031 are mutually incompatible: WO-021 says it is scheduled last after S4, while WO-031 says WO-021's generated projections land first and WO-031 is S4's final order.",
    "suggested_resolution": "Use one serial order, preferably WO-019, then WO-021/WO-022, then WO-031 as the final freshness pass."
  },
  {
    "id": "PA1-008",
    "severity": "should-fix",
    "issue": "R1 and R2 are accepted in ed-rulings.json and the register actions say RULED, but fix-streams.json and the WO-021/WO-022 conflict notes still say awaiting-ed-ruling and prohibit planning.",
    "suggested_resolution": "Replace all awaiting-ruling states and notes with the accepted R1/R2 dispositions and regenerate the scheduling summary."
  },
  {
    "id": "PA1-009",
    "severity": "blocker",
    "issue": "WO-022 is internally stale: its action says to implement the ratified R2 policy, while acceptance_evidence still describes submitting a proposal and enacting no values before ratification, and verification_command is \"proposal review by Ed\" rather than an implementation check.",
    "suggested_resolution": "Rewrite acceptance and verification for the post-ruling state: exact policy text landed, R-018 corrected, audit-close accounting receipt attached or marked unknown, and session-inclusion semantics checked."
  },
  {
    "id": "PA1-010",
    "severity": "blocker",
    "issue": "WO-019's verification_command is not a runnable command: it contains the literal annotation \"(new script); full suite:\". It also does not unambiguously establish the required clean-clone execution boundary.",
    "suggested_resolution": "Replace it with exact executable commands, including a clean temporary-clone invocation of release_check.py --dry-run followed by the canonical suite."
  },
  {
    "id": "PA1-011",
    "severity": "blocker",
    "issue": "WO-003's court-added compatibility acceptance requires exercising existing sealed bundles and explicitly recording eligibility revocations, but its verification command contains no retained-corpus compatibility sweep and no durable revocation-report target is scoped.",
    "suggested_resolution": "Add a retained-corpus exact/replay/ratio compatibility check and a scoped report artifact that records every changed eligibility outcome."
  },
  {
    "id": "PA1-012",
    "severity": "should-fix",
    "issue": "The court fold creates one-to-many finding ownership that report.md §3 cannot represent: C2-029 is listed by WO-004 and WO-016 but points only to WO-016; C2-016 is listed by WO-017 and WO-040 but points only to WO-017.",
    "suggested_resolution": "Either define one canonical parent work order with explicit suborders, or amend the register contract to support work_order_ids and migrate both split findings consistently."
  },
  {
    "id": "PA1-013",
    "severity": "should-fix",
    "issue": "The verification tiers diverge from report.md §4: C2-004 remains severity should-fix but is tier_final=1, while C2-019 is a tier-1 accepted nit with no work order. The charter assigns should-fix to Tier 2 and permits a nit to survive only as a Tier-0 rider on an accepted work order.",
    "suggested_resolution": "Set C2-004 to Tier 2. Reject/drop C2-019 or attach it as a Tier-0 rider to an accepted order."
  },
  {
    "id": "PA1-014",
    "severity": "blocker",
    "issue": "Court T08 requires an independent pre-demotion freeze cross-check for WO-021, but that evidence is absent from acceptance_evidence and cannot be produced by its local pytest/gen_state verification command. The order can close without the compensating control for its fail-open gate-content seam.",
    "suggested_resolution": "Add the independent cross-check receipt to acceptance_evidence and require its recorded result before prose demotion."
  },
  {
    "id": "PA1-015",
    "severity": "should-fix",
    "issue": "Additional acceptance/command mismatches remain: WO-025's command tests emitter behavior but never checks the amended closed vocabulary in the spec; WO-034's gen_state --check cannot prove that every PLANNED pack command has an owner row.",
    "suggested_resolution": "Add a spec-vocabulary consistency check for WO-025 and a pack-command-to-queue ownership lint with fixtures for WO-034."
  },
  {
    "id": "PA1-016",
    "severity": "should-fix",
    "issue": "WO-020 and fix-streams.json still include .agents/skills/claude-consult/SKILL.md under an unresolved scope decision, while CHECKPOINT.md records the lead ruling that this path was removed from scope.",
    "suggested_resolution": "Apply the recorded lead ruling by removing the path and open-decision text from WO-020 and S5's union scope, or supersede the checkpoint with a new explicit ruling."
  },
  {
    "id": "PA1-017",
    "severity": "should-fix",
    "issue": "WO-030 is landed-with-residual and now has a usable clean-venv verification command, but fix-streams/checkpoint scheduling treats the bench batch as complete and gives the residual no execution slot.",
    "suggested_resolution": "Add a post-court bench-close step that runs both clean-venv forms, stores the receipt, and transitions WO-030 to landed only after success."
  }
]
```
BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Read all 101 register rows and found 17 adoption-blocking or corrective coherence issues across rulings, scopes, ordering, verification, and charter conformance.","pathspec":[],"verification":["Parsed all 101 JSONL rows successfully","Compared every court-marked work order with fable-court-holdings.json","Compared register stream membership, dependencies, and bounded scopes with fix-streams.json","Checked ed-rulings.json and report.md sections 3-4","Confirmed no ordinary exact-ID dependency cycle; identified non-resolvable and contradictory ordering constraints"],"flags":["no_edits"]}