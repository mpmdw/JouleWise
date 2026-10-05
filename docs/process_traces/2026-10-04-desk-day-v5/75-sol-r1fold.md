```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend B with a prospective erratum, honest evaluator adaptation, isolated failure custody and explicit Q110 disposition.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "b37301867edfe4a6a966fe1514dd25952d123c9c",
    "head_end": "b37301867edfe4a6a966fe1514dd25952d123c9c",
    "upstream_end": "b37301867edfe4a6a966fe1514dd25952d123c9c",
    "branch": "design/2026-10-04-v5-qualification-block"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "Fold ruling", "action": "needs_ruling"},
      {"row": "Common evidence preparation", "action": "start_now"},
      {"row": "Additional r1 admission machinery", "action": "do_not_start"},
      {"row": "s1 execution", "action": "wait_for"},
      {"row": "First claim window", "action": "wait_for"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --exit-code",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --porcelain=v1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "B is advice, not authorization; current D-176 requires the separate rehearsal.",
      "needs": "Prospectively amend decision 4, dependent kernel edges, evaluator/control interfaces and Q110 coverage before execution."
    }
  ]
}
```

## Scheduling matrix

Row | action | wait_for | collision surface
---|---|---|---
Fold erratum | needs_ruling | Cold ruling; Ed retains veto | D-176, A161/A160/Q3, Q110
Common evidence preparation | start_now | Existing scoped authority | Execution/lineage/lifecycle producers
Additional r1 profile/genesis machinery | do_not_start | Disposition of this consult | Production admission registry
a1 → s1 | wait_for | Erratum, sealed implementation, G10, desk controls; a1 expires before s1 | Quiet Mac; fresh per-occurrence authority
First claim window | wait_for | Successful qualification, Q110 disposition, remaining claim prerequisites | Claim head and immutable evidence

## Critical path

**1. Exclusive defect coverage: none identified that protects a claim number.** Recommend **B**, subject to the corrections below. D-176 currently requires the separate night; this recommendation does not discharge it (`docs/decision_log.md:11529`, `:11539`).

The draft makes r1 non-inference: no model member or energy estimate (`configs/campaigns/v5_qualification_25g83/registration_block4_draft.md:25`). Its exclusive coverage is therefore the rehearsal-specific profile, isolated ledger recipe and T0_REHEARSAL acceptance branch. Those components protect rehearsal operation, not a number produced by the GAMMA claim path. Removing that occurrence removes their qualification purpose.

The shared defects remain observable on s1:

- Prompt/EOF/hang or missing descendants: incomplete execution and potentially biased workload energy.
- Wrong/stale pack, ARM, namespace or duplicate consumption: incorrect workload attribution, unauthorized repetitions and compromised prospective inference.
- Human/agent activity: added measured joules.
- Clock defects: incorrect integration boundaries and uncertainty.
- Failed backup/close-out: loss or misassociation of evidence supporting the eventual number.

These correspond to the actual execution, GO, lineage and lifecycle predicates (`joulewise/t0_rehearsal.py:459`, `:753`, `:936`, `:989`). s1 exercises the real workload and bracket predicates as well (`configs/campaigns/v5_qualification_25g83/registration_block4_draft.md:89`). Desk fault tests remain necessary for crash/race cases; neither successful night proves every failure branch.

**2. What B loses.** It loses an earlier opportunity to discover unattended integration failures without spending the science shakedown. That is operational insurance. It also loses one independent empirical liveness bundle: the current Q110 acceptance requires at least three, with r1/a1/s1 supplying them (`TASK_QUEUE.md:712`). Do not count a1 and s1 twice. Prospectively settle whether existing authenticated evidence supplies the third bundle, an additional non-consuming control supplies it, or the acceptance is reruled before ALPHA.

The operational loss is acceptable because s1 is expressly non-claim, and the draft permits one s2 after a named R3 tooling cure while stopping physics failures (`configs/campaigns/v5_qualification_25g83/registration_block4_draft.md:107`, `:109`). That allowance is not general retry permission.

For a cheap, uncontaminating failure, preserve:

- One-use consumption, bounded shutdown and no automatic re-arm.
- Separate attempts, immutable failed bytes, no member pooling or stage top-ups.
- Enforced non-claim purpose through consumption/downstream replay, isolated science roots and structural-only disclosure.
- Fresh authorization/T-0 for s2, with qualification coverage reviewed at any changed execution head.

The existing doctrine supplies these fences (`docs/decision_log.md:11515`, `:11571`; `configs/campaigns/v5_qualification_25g83/registration_block4_draft.md:107`, `:142`, `:164`). Non-claim status does not itself prevent ledger contamination or influence on an unsealed analysis plan.

**3. Minimum live qualification before claims.** Require **G1, G2, G3, G4, G5, G8 and G9** from successful s1 evidence. Require **G10’s authentic physical control separately**, outside armed/T-0 spans; its software boundary checks may be replayed using s1 inputs. G10 cannot be manufactured from an ordinary successful s1 (`joulewise/t0_rehearsal.py:1165`, `:1200`). Perform the physical control before s1 and return time OFF, following the prospective recipe (`configs/campaigns/v5_qualification_25g83/registration_block4_draft.md:71`, `:77`).

G6’s concrete path separation and G7’s real-launcher refusal can be desk controls. However, **B is not executable unchanged**:

- G6 requires a rehearsal-class receipt/prefix; G7 authenticates presentations against that rehearsal’s retained bytes; the overall evaluator invokes all ten gates (`joulewise/t0_rehearsal.py:804`, `:905`, `:1232`).
- `g7-control` requires fresh rehearsal-linked custody and **CAMPAIGN_TRANSACTION** authorization, so the s1 G2B_SHAKEDOWN plan is presently rejected (`scripts/run_night.py:2162`, `:2181`). Amend the control interface to accept the non-claim production-plan template; never issue premature campaign authority to satisfy it.
- G1 requires every exit code to equal zero, conflicting with legitimate empty-pgrep outcomes; missing dialogue/exec observations remain unresolved in lane B (`joulewise/t0_rehearsal.py:461`; `/Users/edr/night-archive/desk-day-v5/sol-b4b.md:150`).

Reuse predicates, but prospectively define honest composition of live and desk evidence. Do not label omitted gates PASS. Complete actual G9 backups/close-out/restore: s1’s physical-ahead STOP explicitly does not emit launch completion (`configs/campaigns/v5_qualification_25g83/registration_block4_draft.md:49`).

**4. D-161 disposition.** **None of G5/G6/G7 is wholly deliberate-forgery-only.** G5 catches stale/wrong authority and accidental duplicate execution; G6 catches outputs landing in claim/input roots; G7 catches accidental presentation of rehearsal authority. Those are plausible mistakes under D-161’s explicit test (`docs/process_traces/2026-08-27-t26/threat-model-prune/04-MAGISTRATE-RULING.md:11`).

Retire any additional machinery justified solely by a trusted operator deliberately forging and resealing authority. Removing r1-specific profile/genesis/live-proof requirements is justified by eliminating their consumer and redundant qualification cost, not by calling all receipt authentication or root separation anti-forgery.

Static inspection only; no repository writes, tests or live qualification were performed.