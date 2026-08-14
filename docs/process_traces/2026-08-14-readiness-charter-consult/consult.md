```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Do not ratify the draft: its component inventory omits the authority plane, producer-consumer seams, operator/environment failure surfaces, and full post-collection claim path, while CONDITIONAL GO and magistrate-only GO adjudication are fail-open.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "a13b01cba7963357d60ea6c43d4f0b29ac261e12",
    "head_end": "a13b01cba7963357d60ea6c43d4f0b29ac261e12",
    "upstream_end": "a13b01cba7963357d60ea6c43d4f0b29ac261e12",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "DO_NOT_RATIFY_AS_WRITTEN",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The authority and state-kernel control plane is outside the audit"
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "Component lenses do not audit producer-consumer seams or obligation completeness"
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "READY-WITH-CONDITIONS and arm-time ED-SESSION closure form a fail-open path"
      },
      {
        "id": "F4",
        "severity": "blocker",
        "title": "A magistrate-alone READY verdict is not a trustworthy council decision"
      },
      {
        "id": "F5",
        "severity": "blocker",
        "title": "The post-collection path stops before claim consumption is proven"
      },
      {
        "id": "F6",
        "severity": "blocker",
        "title": "Operator-error and environmental-control completeness lack dedicated discriminating lenses"
      },
      {
        "id": "F7",
        "severity": "should_fix",
        "title": "Several component lenses overlap at the wrong boundaries and dilute ownership"
      },
      {
        "id": "F8",
        "severity": "should_fix",
        "title": "The mechanics verify raised findings but do not discriminate a falsely clean audit"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse '@{upstream}'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## main...origin/main",
          "a13b01cba7963357d60ea6c43d4f0b29ac261e12",
          "a13b01cba7963357d60ea6c43d4f0b29ac261e12"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## main\\.\\.\\.origin/main.*a13b01cba7963357d60ea6c43d4f0b29ac261e12"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c 'import collections,json; d=json.load(open(\"configs/arm_readiness/d117_row_registry_v1.json\")); print(\"rows\",len(d[\"rows\"])); print(\"phases\",dict(collections.Counter(r[\"evaluation_phase\"] for r in d[\"rows\"]))); s=json.load(open(\"docs/process/state_kernel.json\")); print(\"kernel\",s[\"authority\"],s[\"updated\"],len(s[\"active_global_gates\"]))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "rows 35",
          "phases {'ARM_ONLY': 21, 'FREEZE_AND_ARM': 14}",
          "kernel AUTHORITATIVE_WORK_SELECTION_STATE 2026-08-08 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "rows 35.*ARM_ONLY.*21.*kernel AUTHORITATIVE_WORK_SELECTION_STATE 2026-08-08 0"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "sed -n '15,67p' docs/process/instrument-readiness-audit-charter-DRAFT.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Per component: READY / READY-WITH-CONDITIONS / NOT-READY(+work orders).",
          "Overall: GO only if no component is NOT-READY and all conditions are",
          "schedulable at arm. Custody: docs/process_traces/<date>-readiness-council/."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "schedulable at arm"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This was a read-only charter review; no live sudo, powermetrics, sampler, quiet-Mac, or operator rehearsal was executed.",
      "needs": "Close stable hardware capabilities in a pre-council ED-QUALIFICATION block; leave only genuinely perishable observations for T-0."
    }
  ]
}
```

## Findings

### F1 — BLOCKER: the authority plane is missing

Coverage verdict: incomplete.

The charter audits measurement components but not the machinery that decides whether they may run. That includes the state kernel, dependency edges, global gates, stop cards, generated queue projections, decision-log propagation, and the transition from council verdict to arm authority.

This is not hypothetical. The kernel declares itself `AUTHORITATIVE_WORK_SELECTION_STATE`, is dated 2026-08-08, and reports zero active global gates, while Ed’s 2026-08-13 directive requires the council audit before any window. See [state_kernel.json](/Users/edr/code/JouleWise/docs/process/state_kernel.json:1) and the [directive](/Users/edr/code/JouleWise/docs/decision_log.md:8847). A comprehensive readiness audit that omits this contradiction can certify an instrument whose authoritative scheduler does not know its new fence exists.

Add a launch-gating control-plane lens covering decision → kernel → queue/run-state projection → pack/readiness registry → arm/consume authority, including stale-base and supersession behavior.

### F2 — BLOCKER: seams are nobody’s primary responsibility

The nine lenses are noun-based. The recent failures were relationship failures:

- a predicate existed but its producer did not;
- a receipt existed but did not bind the consumer’s plan;
- frozen evidence was allowed to assert a live T-0 fact;
- code and fixtures shared the same weakness;
- individually correct branches minted a conflicting global decision ID.

C-057 records all of these classes, including two weaker mixed frozen/live predicates and the integration-only D-136 collision. See [C-057](/Users/edr/code/JouleWise/docs/council_log.md:3481) and its [integration finding](/Users/edr/code/JouleWise/docs/council_log.md:3499).

A “walk” through §5–§12 is not a seam audit. Require a complete obligation graph:

`authoritative fact → producer → namespace/path → schema → binding fields → verifier predicate → consumer → refusal code → operator disposition`.

Every readiness row, evidence kind, close-out artifact, and claim consumer must appear exactly once as an obligation, with zero missing producers, orphan outputs, unbound comparisons, or phase mismatches. The graph needs two independent readers from the outset—contract and execution—not merely refuters after somebody happens to notice a finding.

### F3 — BLOCKER: conditional GO is the trapdoor

Verdict-form verdict: reject.

“Conditions are schedulable at arm” is almost maximally weak. The current registry contains 21 `ARM_ONLY` rows; the §0.6 incident established that fifteen required receipts had no production author. Scheduling those rows did not make them executable.

Delete `READY-WITH-CONDITIONS` and `CONDITIONAL GO`. Use:

- Component: `READY` or `NOT_READY`.
- Council: `READY` only after every nonperishable obligation is closed; otherwise `NO_GO`.
- Launch: `GO` only when council `READY` is combined with an exact, authenticated T-0 closure receipt.

Only genuinely perishable observations may remain for T-0: current boot, power, thermal/display state, process census, root freshness, receipt freshness, and current ledger reservation. Missing code, missing producers, unexecuted sampler behavior, unresolved contract semantics, and privilege-installation capability are nonperishable and therefore `NOT_READY`.

Each T-0 predicate must bind:

- condition ID and exact predicate;
- producer command and schema;
- evidence path/namespace and digest;
- pack, HEAD, boot, plan, and session identities;
- freshness horizon and invalidation events;
- verifier/consumer;
- owner and latest execution phase;
- refusal code and required stop action;
- append-only closure receipt.

No prose waiver, hand-edited JSON, or operator-entered conclusion may close one.

### F4 — BLOCKER: every READY verdict needs the cold pairing

Sitting verdict: the draft’s “cold pair only if reversing a prior gate” is too narrow.

The first READY verdict lifts Ed’s global measurement fence. That is itself a high-impact authority change, irrespective of whether an older gate is formally reversed. C-057 is dispositive: the first adjudicator found a real defect but prescribed an inert cure; the paired reader proved it inert. Both earlier condition sets would have certified closure. See [C-057’s paired ruling](/Users/edr/code/JouleWise/docs/council_log.md:3465).

Required composition:

- Every final `READY`: fresh rule-11 adjudicator plus independent contract-lens refuter over the same mechanically assembled, sealed primary-byte packet.
- Mandatory pairing also for any condition, finding downgrade, dissent, contract reinterpretation, prior-gate reversal, or moved-head substitution.
- Magistrate alone may issue an interim conservative HOLD/NO-GO that preserves the fence and accepts all verified findings without downgrade. It may not clear the fence.
- The packet must be custodied before either reader starts and must bind the final HEAD. Any relevant head or pack movement invalidates affected lenses and the sitting.

### F5 — BLOCKER: “claim-capable” is not tested through claim consumption

The draft reaches reduction, floors, minting, and custody, but not the entire consumer chain. The runbook itself requires extraction and analysis to occur in one lead-controlled custody session under L1 [window_runbook.md](/Users/edr/code/JouleWise/docs/phase_2/window_runbook.md:53), and close-out does not call a window claim-bearing until verdict, allowances, backup, and extraction all succeed [window_runbook.md](/Users/edr/code/JouleWise/docs/phase_2/window_runbook.md:1430).

Add a lead-owned, nonclaiming sacrificial lifecycle rehearsal using disposable roots:

frozen pack → readiness rehearsal → launch-consumption simulation → strict bundle validation → reduction → whole-window verdict → duration-margin receipt → backup/restore check → extraction → floor mint → registered analysis → claim artifact/rendering.

It must use production CLIs and schemas wherever machine safety permits and record explicit substitutions. A failure discovered here costs desk time; the same failure discovered after collection costs the window.

The retained a9/a10 characterization audit does not substitute for this. Move it to a parallel publication/claim-basis audit; it should gate use of that historical exhibit, not launch of a new fleet.

### F6 — BLOCKER: tired-operator and environmental failure surfaces need their own lenses

Operator verdict: the procedure lens is insufficient. A text walk asks whether commands look coherent; it does not ask what a tired Ed can accidentally do.

Require a fresh-shell operator rehearsal and error-injection matrix covering at least:

- wrong checkout or pack;
- wrong/missing environment variable;
- quoted JSON versus JSON-path confusion;
- stale or superseded receipt;
- duplicate reservation or consumption;
- consumed capability followed by failed launch;
- partial calibration custody and restart;
- occupied root or stale lock;
- wrong command order;
- terminal closure or copy/paste truncation;
- reboot/sleep between evidence and arm;
- wrong recovery route;
- accidental output/log monitoring during the quiet period.

Every common error must refuse before collection or produce an unambiguous recovery route. Instructions that rely on memory or recognition of prose are findings.

Environmental verdict: incomplete census. The audit needs a hazard register, not a keyboard/display addendum. At minimum cover power-supply identity and charge state, performance/low-power mode, all displays and lid state, keyboard backlight, screensaver, thermal and memory pressure, concurrent users/remote sessions, agent and keep-awake processes, Time Machine/iCloud/indexing/update activity, network/Bluetooth/external peripherals, notifications/media devices, storage headroom, OS/runtime identity, and clock services.

Each hazard must be classified as mechanically controlled, continuously observed, held constant and receipted, or an admitted residual with a claim limitation. Unknown cannot mean PASS. Current divergences needing explicit adjudication include the prewindow clock probe degrading inability to observe into `WARN` and its narrow process-name census [prewindow_check.sh](/Users/edr/code/JouleWise/scripts/prewindow_check.sh:88).

### F7 — SHOULD_FIX: merge overlapping ownership, then add deliberate seam overlap

Redundancy verdict: refactor.

Merge:

1. Current 1 + 2 into **Calibration acquisition**: fiducial writer, authenticated acceptance, bracket reservation, ledger, recovery, and writer lifecycle.
2. Current 3 + 4 into **Capture and telemetry**: sampler lifecycle, child supervision, cadence, parser, channel census, and CPU+GPU+ANE boundary.
3. Current 5 + the estimator/mint portion of 6 into **Quantitative claim pipeline**: reducer, verdict, floors, common-mode estimator, mint, analysis consumption, and both-gates logic.
4. The custody/readiness portion of 6 + current 7 into **Pack, readiness, and custody**: generators, frozen bytes, evidence production, U11, freeze/arm/consume receipts, and external custody.

Do not merge the human procedure lens with the mechanical integration lens. Their overlap is deliberate and their questions differ. Move current 9 outside the launch-GO aggregation.

### F8 — SHOULD_FIX: the draft can reward ritual

Ritual verdict: insufficiently discriminating.

The failure modes are explicit:

- “one lens each” prevents independent seam ownership;
- “read-only, artifact-bound” predetermines deferral of the evidence most relevant to hardware readiness;
- C-028 verifies findings but not a lens’s claim that it found none;
- no coverage denominator defines “comprehensive”;
- no minimum executed falsifiers are required;
- no final-head invalidation rule exists;
- a custody directory is named, but its mandatory contents are not;
- “schedulable” rewards plans rather than evidence.

Every lens must deliver an enumerated evidence universe, coverage numerator/denominator, executed positive and negative probes, unexecuted obligations, concrete failure scenarios, and a READY falsification attempt. A zero-finding report without that packet is `UNVERIFIED`, not READY. The sitting must adjudicate primary evidence and coverage gaps, not merely “verified findings.”

### Per-question verdicts

| Question | Verdict |
|---|---|
| Coverage | Reject: five launch-critical domains are missing or subordinated. |
| Redundancy | Merge 1+2, 3+4, 5+mint, and custody+7; preserve deliberate cross-cut overlap. |
| Verdict form | Delete READY-WITH-CONDITIONS and CONDITIONAL GO. |
| Sitting | Every READY requires the cold adjudicator/refuter pair. |
| ED-SESSION rows | Split into pre-council qualification and genuinely perishable T-0 observations. |
| Ritual risk | High unless clean claims, coverage, final-head freshness, and executed falsifiers are binding. |

### Exact charter amendments

1. Replace “every byte” with an enumerated required-artifact universe: every required output must either trace through a claim consumer or fail closed against consumption.
2. Add an immutable audit-baseline manifest binding HEAD, upstream, pack digests, row registry, acceptance artifact, runbook, chain, state kernel, and governing decision IDs.
3. Add a state/authority/control-plane lens.
4. Replace the nine-component list with the refactored fleet below.
5. Require the complete producer-consumer obligation graph and zero-gap census.
6. Require two independent seam readers from audit start.
7. Add the tired-operator rehearsal and error-injection matrix.
8. Add the environmental hazard register and completeness disposition.
9. Add the disposable full-lifecycle post-collection rehearsal.
10. Split ED work into pre-council `ED-QUALIFICATION` and perishable `T0` rows; stable capabilities cannot be deferred.
11. Delete `READY-WITH-CONDITIONS`; define council READY plus a separately bound T-0 GO closure.
12. Require cold pairing for every READY, with sealed-packet custody and final-head invalidation.
13. Move retained a9/a10 characterization to a non-launch-gating publication-basis audit.

### Fleet size and effort

| Lens | Seats / tier |
|---|---:|
| Authority, kernel, gates, projections | 1 × xhigh |
| Calibration acquisition | 1 × xhigh |
| Capture, sampler, telemetry boundary | 1 × xhigh |
| Quantitative claim pipeline | 1 × xhigh |
| Pack, readiness, custody | 1 × xhigh |
| Producer-consumer seams | 2 × high, distinct contract/execution readers |
| Operator and recovery human factors | 1 × xhigh |
| Environmental controls census | 1 × high |
| Sacrificial full lifecycle | 1 × xhigh |
| Retained characterization/publication basis | 1 × high, outside launch GO |
| Final sitting | cold Fable adjudicator + Opus contract refuter |

That is ten launch-gating primary seats, one parallel historical-basis seat, and the two-seat cold sitting. Finding refuters remain on demand under C-028. No ultra session is justified initially; the record favors decomposed xhigh work and distinct high-tier pairings over one larger reader.

## Residual risk

The off-repository final arm packet and uncommitted arm-author implementation were not available within this repository-scoped read-only review. No live hardware, privilege, sampler, or quiet-machine qualification was performed, so those outcomes remain unknown pending the amended audit.