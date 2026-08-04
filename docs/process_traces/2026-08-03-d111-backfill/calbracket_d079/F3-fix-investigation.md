```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "The best fix is a writer-enforced canonical receipt ledger (A-min): C's root-list attestation alone cannot prove completeness, but the sole production calibration writer allows a much smaller mechanically complete registry than Option A assumed.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "a14d1fe189734a9a58035736becb75612a85a157",
    "head_end": "a14d1fe189734a9a58035736becb75612a85a157",
    "upstream_end": null,
    "branch": "impl/cal-bracket-d079"
  },
  "pathspec": [],
  "unowned_dirty": [
    "joulewise/analysis_engine/claims.py",
    "joulewise/calibration_bracketing.py",
    "joulewise/whole_window.py",
    "tests/test_calibration_bracketing.py",
    "tests/test_reduce.py",
    "tests/test_whole_window_selection.py",
    "configs/calibration/calibration_acceptance_d079_v2.json",
    "tests/verify_calibration_acceptance_corpus.py"
  ],
  "verdict": {
    "overall": "No pure no-authority C exists: completeness requires either enforced registration, an authoritative parent scan, or a trusted non-rollback attestation.",
    "best_pick": "A-MIN",
    "rows": [
      {
        "id": "A-MIN",
        "action": "needs_ruling",
        "wait_for": "Ed ratifies the canonical ledger, trust anchor, and registration-as-governed-validity boundary.",
        "collision_surface": "Capture writer, calibration evaluator, acceptance artifact, whole-window session/verifier, verdict basis.",
        "cost": "M",
        "soundness": "Fail-closed for every governed capture because the sole production writer must atomically publish a receipt before returning."
      },
      {
        "id": "A",
        "action": "wait_for",
        "wait_for": "Use only if multi-writer or multi-machine calibration capture is expected soon.",
        "collision_surface": "Full registry schema, writer locking, migration, every caller, custody and backup.",
        "cost": "L",
        "soundness": "Sound with authenticated non-rollback head and mandatory write-through registration."
      },
      {
        "id": "B",
        "action": "do_not_start",
        "wait_for": "Only reconsider if Ed explicitly accepts the cross-root residual.",
        "collision_surface": "D-102 amendment, artifact scope declaration, verdict provenance.",
        "cost": "S",
        "soundness": "Does not fail closed on an expander outside the declared roots; it legalizes that residual."
      },
      {
        "id": "C-BARE",
        "action": "do_not_start",
        "wait_for": "",
        "collision_surface": "Caller-supplied root list and verdict record.",
        "cost": "S",
        "soundness": "Hashes authenticate named roots but cannot prove that another root was not omitted."
      },
      {
        "id": "C-SEALED",
        "action": "needs_ruling",
        "wait_for": "Ed accepts a signed or repo-pinned non-rollback scope checkpoint as the completeness authority.",
        "collision_surface": "Snapshot schema/generator, trust pin, snapshot threading, evaluation basis.",
        "cost": "M",
        "soundness": "Contractually sound relative to the attestor; it cannot mechanically detect a false completeness assertion."
      },
      {
        "id": "PARENT-SCAN",
        "action": "wait_for",
        "wait_for": "Ed defines authoritative custody-parent anchors and portability rules.",
        "collision_surface": "Host-specific root discovery, archive custody, raw-evidence availability.",
        "cost": "M",
        "soundness": "Fail-closed inside the ruled anchors, but artifacts outside them remain invisible."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "nl -ba /Users/edr/code/JouleWise/docs/decision_log.md | sed -n '6265,6335p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "6298 any change -> calibration_acceptance_bound_stale. Mandatory prospective",
          "6300 byte change; a new valid same-identity calibration expanding the",
          "6302 challenging the pre-flight screen. A trigger observation is judged",
          "6303 under the PRIOR artifact"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Mandatory prospective.*PRIOR artifact"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "AST call-site count over joulewise/**/*.py and scripts/**/*.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "calibration_bracket_for_bundles: 3 non-test calls",
          "AuthenticatedConsumptionSession: 6 non-test constructions"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "3 non-test calls.*6 non-test constructions"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "find /Users/edr/code/JouleWise -maxdepth 1 -type d -name 'runs*' -print | wc -l; find /Users/edr/code/JouleWise -maxdepth 4 -type f -path '*/instrument_validation/*/manifest.json' -print | wc -l; find /Users/edr/code/JouleWise -maxdepth 2 -type f -name MANIFEST.sha256 -print | wc -l; find '/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup' -maxdepth 2 -type f -name MANIFEST.sha256 -print 2>/dev/null | wc -l",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "35",
          "54",
          "22",
          "23"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "35.*54.*22.*23"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## impl/cal-bracket-d079",
          "six modified tracked files",
          "two untracked files"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "impl/cal-bracket-d079"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "D-102 does not define the authoritative observation universe, completeness authority, or anti-rollback head.",
      "needs": "Ed chooses A-min, A, C-sealed, parent-scan, or explicitly amends D-102 for B."
    },
    {
      "id": "R2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Prospective comparison needs an authenticated prior-observation set distinct from the n=19 derivation corpus; the artifact currently records only member rows plus ID-only blind exclusions.",
      "needs": "Ratify the issuance cutoff and content-identity inventory for observations already known when D-102 was accepted."
    },
    {
      "id": "R3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A root list plus root hashes proves integrity of named roots, not exhaustive coverage or freshness; recording it in the same verdict adds accountability but no independent authority.",
      "needs": ""
    },
    {
      "id": "V-GAP",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The 32-valid/6-invalid unique same-epoch inventory was derived from stored manifests/evidence and content hashes, not a fresh physical re-fit of all raw traces.",
      "needs": "Raw-physics verification belongs in implementation/backfill acceptance, not this read-only design investigation."
    }
  ]
}
```

## Findings

The single best pick is **A-min: a canonical, writer-enforced observation-receipt ledger**.

This is not the heavy “registry service threaded through everything” version of A. Repository tracing found exactly one production author of calibration artifacts: [validate_powermetrics_fiducial.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/eaafcc6f-e4c3-4661-b903-3333270ce728/scratchpad/calbracket/scripts/validate_powermetrics_fiducial.py:252). That writer can atomically publish a compact receipt for every valid or failed capture. This makes completeness enforceable at the production boundary and avoids scanning arbitrary runs roots or trusting a caller’s claim that its list is complete.

C uncovered an important requirement, but its bare form does not close the hole: a list of roots and hashes authenticates what was listed, not that an omitted root does not exist.

A second important finding is that the artifact needs two different sets:

- `derivation_corpus`: the n=19 observations used to derive the numeric thresholds.
- `prior_observation_set`: every content-distinct observation already known when the artifact was issued, including blind holdouts and authenticated systematic/invalid attempts.

D-102 says the triggers are prospective and judged under the prior artifact. Therefore “new” must mean `current_observations − prior_observation_set`, not `current_observations − derivation_corpus`. Otherwise known window-B holdouts and later observations would be incorrectly treated as newly discovered after D-102.

The current artifact’s `blind_exclusions` contains only two directory IDs; that is insufficient as the authenticated prior-observation boundary.

### A — full authenticated registry

1. **Soundness:** Yes, provided every governed capture is write-through registered and the registry has an authenticated, non-rollback head. Missing, truncated, wrong-scope, or non-prefix snapshots must refuse. An off-registry artifact remains a hole unless registry membership becomes part of governed calibration validity.

2. **Implementation:** Add a registry reader/writer and schema; update the sole capture writer; add baseline registry head/content set to `calibration_acceptance_d079_v2.json`; split trigger observations from local T1 endpoint selection in [calibration_bracketing.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/eaafcc6f-e4c3-4661-b903-3333270ce728/scratchpad/calbracket/joulewise/calibration_bracketing.py:508); thread one immutable snapshot through the runner, session, verifier, floor extraction, minting, and analysis consumers. This is genuinely new infrastructure.

3. **D-102:** Faithful implementation; no weakening amendment. Ed must still rule the registry’s authority, retention, and validity boundary because D-102 is silent there.

4. **Cost:** L.

### B — bounded n=19 plus evaluated root

1. **Soundness:** No against the stated cross-root hole. A valid expander in an unscanned root continues licensing. It only becomes “sound” after redefining that root as out of scope.

2. **Implementation:** Declare the bounded universe in D-102 and the acceptance artifact; retain local discovery; record the root and candidate identities in the verdict. Touch mainly `decision_log.md`, the artifact, `calibration_bracketing.py`, and tests.

3. **D-102:** Requires an Ed-signed amendment because it weakens “mandatory” trigger coverage.

4. **Cost:** S.

### C-bare — caller root list plus hashes and verdict recording

This form is not viable.

A root hash proves the contents of root R. It does not prove that R, S, and T are all the roots. Nor does recording the list in the verdict provide an independent trust root: the same caller controls both the evidence and the completeness claim.

It also lacks:

- an authenticated issuer;
- an authoritative namespace or enumeration rule;
- an issuance cutoff;
- anti-rollback/latest-head protection;
- exact coverage of invalid/systematic attempts;
- a distinction between the derivation corpus and previously observed holdouts.

It therefore does **not** fail closed when an expander is omitted from the list.

### C-sealed — authenticated observation-scope checkpoint

C becomes viable when the supplied set is a signed or independently byte-pinned checkpoint containing:

- `scope_policy_id` and the authoritative custody anchors;
- issuer identity and trust pin;
- issuance sequence/cutoff;
- predecessor or non-rollback current-head binding;
- exact root-listing digests, not just hashes of selected roots;
- content identities for every valid and failed observation;
- the prior-observation-set digest;
- a declaration that the snapshot exactly covers the ruled namespace.

Evaluation then requires the artifact’s prior set to be a subset, judges only the delta under the prior artifact, and records the checkpoint digest in the whole-window basis.

1. **Soundness:** It fails closed on missing, unsigned, stale, rolled-back, or internally incomplete checkpoints. It cannot mechanically detect a signer’s false assertion that an omitted root does not exist. If Ed accepts that signer as the completeness authority, it is contractually sound relative to that trust boundary.

2. **Implementation:** New snapshot schema, generator, verifier, and trust pin; new snapshot parameter through the evaluator/session/verifier; verdict-basis persistence. No live append registry or evaluation-time global scan.

3. **D-102:** Faithful complete-or-refuse implementation; no weakening amendment. The authority and anti-rollback mechanism require Ed’s ruling.

4. **Cost:** M.

### A-min — canonical writer-enforced receipt ledger, recommended

Use the existing calibration artifact as the evidence body and append only a compact receipt:

`sequence, predecessor, content_id, manifest/evidence/raw hashes, six-field epoch, full T1, capture time, exact bound lexeme, valid/systematic disposition, source locator`.

The production capture command must publish the receipt atomically before returning success or failure. The evaluator loads one immutable ledger snapshot from a canonical location, requires the artifact’s prior set to be present, evaluates the delta, and uses the evaluated window root only for full-T1 pre/post selection.

The ledger needs an authenticated non-rollback head. A repo-pinned checkpoint follows the project’s existing trust model; a detached Ed-authority signature would avoid rotating source pins after each capture.

1. **Soundness:** Yes for every governed production capture. A capture that cannot publish its receipt is incomplete and cannot support claims. This closes the cross-root expander, doubling, and systematic-failure holes without discovering arbitrary roots.

2. **Implementation:** New compact ledger/head module and backfill tool; modify `validate_powermetrics_fiducial.py`; update `calibration_bracketing.py`, the acceptance artifact, `whole_window.py`, `run_campaign.py`, and verifier/basis tests. The outer claim consumers can receive a snapshot through `AuthenticatedConsumptionSession`; they do not need individual root lists.

3. **D-102:** Faithful implementation. Ed must rule that receipt publication is part of governed validity and select the head authority, but no D-102 threshold/freshness amendment is needed.

4. **Cost:** M.

### Authoritative parent scan

Ed could instead define one or more custody-parent anchors, require the evaluator to enumerate every matching `instrument_validation/<id>/manifest.json`, and record a digest of the complete directory listings.

This fails closed within the anchors but is host-specific and needs a decision about local roots, iCloud archives, quarantine, and future machines. Re-authenticating old raw evidence is also awkward because many large traces were pruned locally.

Cost is M; it is faithful only after Ed rules the anchor set.

## Existing inventories

No existing artifact closes completeness:

- There are currently 35 local `runs*` roots and 54 validation manifests.
- Only 22 local roots and 23 iCloud backup roots have `MANIFEST.sha256`.
- Campaign manifests enumerate campaign members inside one root; they do not enumerate calibration attempts or other roots.
- `campaign_log.jsonl` is per-root, and the calibration author does not append calibration observations to it.
- Each validation `manifest.json` authenticates one capture’s files, not the parent directory or global population.
- `runs/instrument_validation` is only a partial aggregation.
- The D-102 artifact authenticates 19 corpus members, not the complete prior-observation population.

A metadata/content-hash inventory found 32 unique valid and 6 unique invalid same-epoch observations across the local roots. That does not prove fresh raw physics, but it demonstrates why a separate `prior_observation_set` is necessary.

## Production caller trace

There are exactly three direct non-test calls to `calibration_bracket_for_bundles`:

- `AuthenticatedConsumptionSession._prepare` in `whole_window.py:461`;
- secondary current-row verification in `whole_window.py:3424`;
- `idle_admission_core_verdict` in `scripts/run_campaign.py:4277`.

There are six production constructions of `AuthenticatedConsumptionSession`:

- `scripts/run_campaign.py:5184`;
- `joulewise/floor_extraction.py:1614`;
- `joulewise/analysis_engine/inputs.py:1343,2768`;
- `scripts/mint_floor_artifact.py:512,1122`.

The runner’s whole-window verdict and AXI paths reach the evaluator through `idle_admission_core_verdict`. The ordinary call near `run_campaign.py:7600` does not evaluate calibration because `whole_window` remains false.

Under A or C-sealed, all these paths must share the same immutable observation snapshot; repeated independent loads create a time-of-check/time-of-use split. Under A-min, the session can own the canonical snapshot, but the direct runner path and secondary verifier must reuse that exact object or recorded head.

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| A-MIN | needs_ruling | Canonical authority, head authentication, registration validity | Capture writer, evaluator, artifact, session/verifier |
| C-SEALED | needs_ruling | Completeness signer and anti-rollback rule | Snapshot generator, caller APIs, verdict basis |
| A | wait_for | Evidence that multi-writer scale justifies it | Registry and every producer/consumer |
| PARENT-SCAN | wait_for | Authoritative parent-anchor ruling | Local/cloud custody and portability |
| B | do_not_start | Explicit D-102 weakening amendment | Decision log and residual-risk record |
| C-BARE | do_not_start | — | Fails completeness proof |

## Critical path

Ed first chooses the observation authority and anti-rollback mechanism. Then the implementation must reconstruct and authenticate the prior-observation set, including known holdouts and systematic attempts. F1, F2, and F3 should land together after that schema is fixed, followed by one acceptance-artifact regeneration and byte-pin rotation.

Direct D-102 fidelity work after the ruling is mechanical: refuse without completeness proof, use content identities, require prior-set inclusion, judge only the delta under the prior artifact, share one snapshot across every caller, and persist its head in the verdict/evaluation basis.