```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "S1 CURED: round 3 correctly describes the registered ratio. S3 remains: scientific terms are unglossed. All 98 tests, generator check, and diff check pass.",
  "workspace": {
    "base_requested": "dc93749c",
    "base_mode": "descendant",
    "head_start": "7fc058b9941b32a3f2fc2a821d3eab2104e393a3",
    "head_end": "7fc058b9941b32a3f2fc2a821d3eab2104e393a3",
    "upstream_end": "7fc058b9941b32a3f2fc2a821d3eab2104e393a3",
    "branch": "fix/2026-09-11-c1-registration-seam"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "MERGEABLE AFTER FIXES",
    "findings": [
      {
        "id": "S3",
        "severity": "should_fix",
        "path": "docs/phase_2/derivation_night_runbook.md",
        "line": 505,
        "summary": "The paragraph introduces energy component, floor, and dominance sentence without earlier or inline definitions; literal field names specify division but do not explain the quantities."
      }
    ],
    "cured": ["S1"],
    "same_signature": "Round 3 cures the same factual-misdescription class as round 2 S1. The first-use explanation class S3 survives."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_gen_derivation_night tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 98 tests in 22.234s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 98 tests[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 scripts/gen_derivation_night.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS generated derivation-night wrapper region matches"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS generated derivation-night wrapper region matches"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check dc93749c..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --stat dc93749c..HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " docs/phase_2/derivation_night_runbook.md | 17 ++++++++++-------",
          " 1 file changed, 10 insertions(+), 7 deletions(-)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1 file changed, 10 insertions\\(\\+\\), 7 deletions\\(-\\)"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git status --porcelain",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Findings

**S3 — SHOULD_FIX — `docs/phase_2/derivation_night_runbook.md:505–508`: first-use explanations remain missing.**

The arithmetic is now accurate, but naming two fields does not explain “floor,” identify an “energy component,” or tell the reader what the “dominance sentence” claims.

**S1 — fully CURED. Same-signature statement:** round 3 cures the **same factual-misdescription class** as round 2’s S1. The surviving finding is S3, the first-use explanation defect.

**Claim-by-claim evidence**

In the table, `registration.json` means `configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json`; `generator` means its sibling `generate_configs.py`.

| Paragraph claim | Primary evidence and judgment |
|---|---|
| “the D-117 contrast campaign’s (`configs/campaigns/d117_contrast_v5`)” | Generator `:2`: “Generate a model-panel-parameterized D-117 CONTRAST v5 pack”; `:19–20` identifies that directory. **Supported.** |
| “registration of its dominance criterion, decision D-165” | Generator `:525–526`: `dominance_criterion_registration()` returns “the frozen D-165 ratio and common-mode replay contract.” Decision log `:211` identifies the registered `dominance_criterion`. **Supported.** |
| “fixed before that campaign’s data” | Decision log `:10733–10734`: the ratio “is pre-registered into the `_v5` pack”; `:211` explicitly says “fixed before collection.” **Supported as the prospective registration rule.** |
| “for every energy component” | JSON `:1`: `"per_component":true,"all_must_pass":true`; generator `:536–537` agrees. Decision log `:211` specifies “per component per cell, all must pass.” **Supported**, although the paragraph does not identify those components. |
| “`corner_widened_unguarded_floor_j` divided by `point_unguarded_floor_j`” | JSON `:1`: those exact `numerator` and `denominator` values; generator `:531–532` agrees. Decision log `:211` explicitly defines that division. **Supported.** |
| “must be at least the file’s `threshold` of 2.0” | JSON `:1`: `"threshold":2.0,"comparison":"greater_than_or_equal"`; generator `:533–534` supplies those fields. Decision log `:10733` says `R ≥ 2`. **Supported.** |
| “`R == 2.0 passes`” | JSON `:1` and generator `:535`: exact `exact_equality_policy` string. **Supported.** |
| “for the campaign’s dominance sentence to stand” | Decision log `:211` makes the dominance subtitle gate-contingent. JSON `:1` requires all components to pass. **Supported as a necessary condition.** It does not say this ratio alone is sufficient. The additional mandatory diagnostic can still withdraw the sentence: decision log `:10735–10736`, retained by the addendum at `:11276–11279`. |
| “the file is named for D-166 although it carries the D-165 rule” | Filename; generator `:526`; decision log `:10728` identifies D-165, while `:10751` identifies D-166 as “the workload.” Its `:11290–11304` addendum changes the decode prompt. **Supported.** |
| “It has nothing to do with this calibration night’s physics” | `joulewise/night_gate.py:1300–1328` reads and hashes the registration, compares its digest, and marks C1; it does not evaluate the scientific ratio. **Supported in context:** the registered criterion is not this calibration night’s scientific acceptance rule. |
| “the one document the night gate is coded to authenticate for this receipt class, through C1” | `night_gate.py:34–40` pins its digest and names its path; `:1300–1328` applies this digest check to `DIAGNOSTIC_NO_PACK` and `REHEARSAL_STUB`, recording C1. **Supported as document-content identity:** matching content may be supplied through another permitted path. |
| “A receipt class is the plan’s category, and it selects which gate checks apply” | `night_gate.py:536–543` initializes conditions from `class_table()[receipt_class]`, including `NOT_APPLICABLE`. **Supported.** |
| “this night’s class is `DIAGNOSTIC_NO_PACK`, a night that runs no measurement pack” | Runbook `:764–767` defines the selected class; `:778` sets the plan field. **Supported.** |
| “The scientific pre-registration is bound … by H … and by the digest recorded below and in §1.5” | Runbook `:243–247` binds the plan and checkout to H; `:496–497` requires the pre-registration inside H; `:538–550` specifies its digest record. `night_gate.py:1006–1026` checks the measurement head; `scripts/issue_calibration_acceptance_generation.py:1174–1181` hashes the pre-registration and refuses a digest mismatch. **Supported.** |

No unsupported factual claim remains that warrants an S1 corrected sentence.

Primary inspection commands included:

```sh
nl -ba configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json
nl -ba configs/campaigns/d117_contrast_v5/generate_configs.py | sed -n '525,575p'
nl -ba joulewise/night_gate.py | sed -n '34,40p;1300,1328p'
nl -ba docs/decision_log.md | sed -n '10718,10773p;11270,11308p'
```

The independent builder/file inspection returned:

```text
builder equals JSON: True
sha256: dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265
matches C1 constant: True
numerator: corner_widened_unguarded_floor_j
denominator: point_unguarded_floor_j
threshold: 2.0
comparison: greater_than_or_equal
exact_equality_policy: R == 2.0 passes
per_component: True
all_must_pass: True
```

**First-use census**

The census covers the changed explanation and its attached continuation through line 517.

| Term of art | Earlier construction, inline gloss, or flag |
|---|---|
| D-117 contrast campaign / `_v5` directory | **FLAG:** `:503` supplies an exact directory, but does not explain what experiment “contrast campaign” denotes. |
| Registration / pre-registration | Inline `:504–505` explains the before-data rule. Earlier `:124–125` builds that principle. The glossary’s “Registration” at `:150–155` instead means a set of ledger sessions; it does not define this campaign’s criterion registration. |
| Dominance criterion | Inline `:505–508` supplies the arithmetic, but its scientific meaning depends on the unglossed “dominance sentence.” **Partial gloss.** |
| Decision D-165 | Inline `:504–508` identifies it with the described rule. |
| D-166 | Earlier `:11–12` and `:500–502` identify the required registration file; inline `:509` explains the filename/rule mismatch. |
| Energy component | **FLAG:** first occurrence `:505`; neither earlier nor inline text identifies the components. |
| Floor | **FLAG:** first occurrence `:505`; no earlier definition. |
| `corner_widened_unguarded_floor_j` | Inline `:506` identifies its numerator role. **FLAG for meaning:** “corner-widened,” “unguarded,” and `_j` are not explained. |
| `point_unguarded_floor_j` | Inline `:507` identifies its denominator role. **FLAG for meaning:** “point,” “unguarded,” and `_j` are not explained. |
| Ratio / R | Inline `:505–508` gives the division and equality example; R is readily inferable as that ratio. |
| Threshold | Inline `:507` gives its operational meaning: minimum passing ratio, 2.0. |
| Dominance sentence | **FLAG:** first occurrence `:508`; no explanation of the claim the sentence makes. |
| Calibration night | Built at `:107–130`: calibration captures, their acceptance, and the purpose of this night. |
| Night gate / authenticate | Earlier `:12` names the gate; inline `:511–512` identifies its registration-check role. The actual authentication operation is not explained here. |
| C1 | Inline `:511–512`: “the night gate’s registration check.” |
| Receipt class | Inline `:512–513`: the plan’s category selecting applicable checks. |
| Plan | Earlier `:53–56`, `:194`, `:245–247`, and `:373` build its staging, chain-path, and head-binding roles. |
| `DIAGNOSTIC_NO_PACK` | Inline `:513–514`: a night with no measurement pack; forward reference to §1.1. |
| Measurement pack | **FLAG under the strict first-use test:** not explicitly defined before `:514`. “Frozen campaign pack” at `:374` is an earlier use, not a definition. |
| H / measurement commit / pin | Built at `:243–247`; restated inline at `:515–516`. |
| Commit tree | Inline `:516` says it contains the pre-registration; earlier `:189` establishes committed files as identical across clones at H. |
| Digest | Earlier `:14`: “a fingerprint of the file’s bytes.” |

The requested floor scan contradicts the premise that this runbook has an *earlier* floor definition:

```text
$ grep -n -i 'floor' docs/phase_2/derivation_night_runbook.md | head
505:campaign's data: for every energy component, the ratio of two floors that the
506:file names — `corner_widened_unguarded_floor_j` divided by
507:`point_unguarded_floor_j` — must be at least the file's `threshold` of 2.0
1090:**The generator's floor under this allocation.** `gen_derivation_night.py`
1102:                = 7980 s          ← the generator's hard floor for 12 slots
1107:floor, not a recommendation: 9000 s remains the value to author**, because 7980
1111:this floor from the new slot count rather than bypassing it.
1172:pre-settle allowance is a floor for; item 1 is the driver's own work. Every
1414:reconstruction is the successor's floor, not a licence to record less.
1685:  operative screen differs from the raw range (the never-zero floor), the
```

The first later explanation concerns a **minimum time allocation**, not an energy floor. It cannot supply the missing meaning at line 505.

**Writing judgment and dictated replacement**

The paragraph lets a reader reproduce the division given already-identified inputs, but not understand those inputs or the resulting claim. It also leaves C1’s actual operation implicit. For this runbook’s registration check, a shorter explanation can remove the scientific detour and state the reproducible check directly.

Replace lines 503–517 verbatim with:

> The file named above records decision D-165’s comparison rule for a separate experiment, the D-117 contrast campaign (`configs/campaigns/d117_contrast_v5`). The rule was fixed before that campaign’s data; the filename names D-166, the workload decision. This calibration night uses the file for C1, the night gate’s registration check: the gate computes the SHA-256 digest of its UTF-8 text and requires it to match `night_gate.D166_REGISTRATION_SHA256`. C1 checks that identity without evaluating the comparison rule. The plan selects `DIAGNOSTIC_NO_PACK`, the category for a night without a measurement pack (a scheduled set of measurement runs); the category determines which gate checks apply (§1.1). The calibration night’s scientific pre-registration is bound separately by H, the measurement commit whose tree contains it and which the plan pins, and by the digest recorded below and in §1.5.

This is a proposed documentation correction only; no files were edited.

## Residual risk

Verification was limited to the requested documentation delta, 98 focused tests, generator consistency, and whitespace. No live or quiet-machine measurement ran. HEAD and upstream remained `7fc058b9941b32a3f2fc2a821d3eab2104e393a3`; the worktree remained clean.

Next exact step: the lead adjudicates S3 and the proposed replacement, then performs final contextual review.

VERDICT: MERGEABLE AFTER FIXES