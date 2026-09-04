# Blind Fable design seat — AUTHENTICATOR-ALLOWLIST-GUARD-01 (2026-09-04)

Disclosure: auto-loaded were `~/.claude/CLAUDE.md`, project `CLAUDE.md`, and the
memory index `MEMORY.md`. Not read: `CLAUDE.local.md`, `RUN_STATE.md`,
`TASK_QUEUE.md`, or any other seat's proposal. `$OUT` was unset at launch;
this path is the seat's choice. Read at the bench (HEAD `eff3304e`): all eight
mission traces, D-151/D-153/D-161 rows and `MAGISTRATE-RULING-O1.md` §7–9,
`joulewise/arm_readiness.py` (`_r1_derived_irrelevant_path_manifest` :1672,
`validate_r1_lifecycle_registry` :1718–1965, `validate_registry` :2093–2125,
the changed-set gate :4786–4855, `RECEIPT_HISTSEM_PINSET_RELATIVE_PATH` :2947,
the marker id pin :10927, freeze constants :10998/:11346), the tracked
registry, and the fixture builders in `tests/test_arm_readiness_evidence.py:28`
and `tests/test_arm_readiness_lifecycle.py:125–164`.

## 0. Root cause the traces did not name

The third occurrence is not a design regression; it is a fixture
accommodation. The re-scope derives the manifest correctly, but it pins ONE
SHA-256 over the derived output (`_R1_ALLOWLIST_PROVENANCE_SHA256`). A single
pin cannot hold across lifecycle records: every test fixture rotates
`successor_pack_ids` (qwen25 `_v2` families) and the PASS freeze ordinal
(`freeze-0001/0002/0004`), and `validate_r1_lifecycle_registry` runs on those
records at every consumer (:4786, :4942), not only at load. To keep fixtures
green the seat fenced the check behind `registry_id == "d117-r1-lifecycle-v1"`.
The pin forced the gate; the gate opened the class. Remove the pin and the
gate has no reason to exist.

## 1. The closed set and where it lives

Governed artifact families that may ever appear in an irrelevant-path
allowlist, for each of the exactly three successor profiles ALPHA/BETA/GAMMA:

| Family | Path template under `configs/campaigns/<pack_id>/` | Count |
|---|---|---|
| F1 generic source record | `arm_readiness.sources/<stem>.json` | 11 |
| F2 generic evidence receipt + sidecar | `arm_readiness.evidence/evidence-<stem>.json{,.sha256}` | 22 |
| F3 PASS freeze receipt + sidecar | `arm_readiness.freeze.receipts/<freeze_id>.json{,.sha256}` | 2 |
| F4 plan-tree binding + sidecar | `plan_tree.json`, `plan_tree.sha256` | 2 |
| F5 digest-conditional successor pinset (one, repo-wide) | tail of `RECEIPT_HISTSEM_PINSET_RELATIVE_PATH` | 1 |

3 × 37 + 1 = 112. Nothing else. Authenticators have no repository path by
construction: `hC` lives in transaction custody out of band (D-153 A5), the
family marker must be outside the repository (:11667), and F5 is the single
authenticator-adjacent path, admitted only under the C→S digest condition.

Home of the enumeration: code, one constant block in `arm_readiness.py`
(`_R1_GOVERNED_PRE_REGISTRATION_EVIDENCE_STEMS`, the four F1–F4 templates,
and the pinset chain tail), which is outside the subtraction set and changes
only by reviewed PR. The table above is mirrored verbatim into the D-151
addendum (§5) as the human-readable spec; code is the ONE home, the doc is a
pointer. No runtime registry, no JSON manifest file, no digest pin.

## 2. Derivation across registry ids, with no opt-in

```python
def r1_governed_artifact_manifest(successor_policy: Mapping) -> tuple[str, ...]:
    # inputs: successor_policy["successor_pack_ids"]  (3 validated ids, no '/' or '\\')
    #         successor_policy["pass_freeze_receipt_id"]  (r"^freeze-\d{4}$")
    # constants: STEMS, F1-F4 templates, RECEIPT_HISTSEM_PINSET_RELATIVE_PATH[-1]
```

Inputs are only fields of the lifecycle record itself plus code constants.
`registry_id` is NOT an input. In `validate_r1_lifecycle_registry`, replace
the gated block at :1955 with two exhaustive branches:

- `successor_pack_ids` is `ED_RESERVED:*` → `irrelevant_path_allowlist`
  must be exactly `[]` (the placeholder state).
- `successor_pack_ids` is a Mapping → `allowlist == derived` as sorted lists;
  refuse naming the extra and missing paths.

There is no third branch, so no record state admits an unexplained path.
Why a future id with `configs/arm_readiness/future-confirmation-token.json`
cannot pass: the derivation has no free variable that can emit it. Its only
degrees of freedom are three pack ids (which select a directory under
`configs/campaigns/`, path separators refused) and one freeze ordinal (which
selects a filename inside F3). Every emitted path is under
`configs/campaigns/<pack>/` or equals the code-enumerated pinset tail. The
literal allowlist is never read to decide membership; it is compared to the
derivation and discarded.

The freeze ordinal is the one input the current code hard-codes (:1700
`freeze-0004`, also :10998/:11346). Add `pass_freeze_receipt_id` to
`successor_policy` (tracked registry, placeholder, fixtures), and make the
marker's freeze-binding check at :11346 read it, so the registry and marker
cannot disagree. Fallback if the tracked registry cannot be edited before the
next window (a published marker pins its bytes at :10920): keep the ordinal as
a single named code constant used at both sites, and rewrite the
`_v2` fixtures to it. The record field is the better paper: it is the
lifecycle record naming its own evidence, which is what §1 claims.

Consumption is unchanged: `_r1_changed_paths` minus (allowlist − conditional),
conditional paths only under `_require_confirmed_conditional_path`.

## 3. Refusal codes and the ONE test

No new reason code. `READINESS_REASON_CODES` is closed and covered by the
`reason-code-coverage` evidence inside the governed packs; adding a code would
force a new family generation (D-153 registered limitation) to fix a guard.
Use `readiness_row_registry_mismatch` with fixed message tokens, both
branches:

- `R1 allowlist not derivable from governed artifacts: extra=[…] missing=[…]`
- `R1 allowlist must be empty while successor pack ids are ED_RESERVED`

The one test, `test_allowlist_extra_path_refuses_for_every_lifecycle_record`
(`tests/test_arm_readiness_schemas.py`), one method, `subTest` over four
records built from the tracked registry:

1. id unchanged; 2. id `d117-r1-lifecycle-v2`; 3. id `test-r1-lifecycle-v1`;
4. id `d117-r1-lifecycle-v2` AND pack ids rotated to `…_v6` names with the
   allowlist re-derived by the production function (must PASS before the
   append, proving the derivation follows the record, not the id).

Each: append `configs/arm_readiness/future-confirmation-token.json`, sort,
`validate_registry` (or `validate_r1_lifecycle_registry` for record 3, the
consumer path), assert `reason_code == "readiness_row_registry_mismatch"` and
the extra path is named in the message. No authenticator is named, registered,
or decorated anywhere in the test.

Mutation kills, both pasted as executed evidence in the fix report:
(a) `if False and allowlist != derived` → all four subtests fail;
(b) restore `and registry_id == "d117-r1-lifecycle-v1"` → subtests 2–4 fail.
Kill (b) is the counterfactual that names this mission's actual defect;
kill (a) alone was already green at the third occurrence and proved nothing
about ids.

## 4. Salvage, not rebuild

The re-scope landing (trace 07) is the right mechanism and stays: registry
and decorator removed, positive derivation, exact-set comparison. Bounded fix
round on the same branch:

- DELETE `_R1_ALLOWLIST_PROVENANCE_SHA256` and its raise (:1707–1715). It
  authenticates code with code, defends only against the trusted operator
  (D-161 over-engineering), and is what forced the id gate.
- DELETE the `registry_id ==` conjunct (:1955); add the reserved branch.
- Parametrize the freeze ordinal (§2) and take the pinset from the chain
  tail rather than index `[1]` so a `_v6` pinset rotates by code enumeration
  (D-151 cond. 6) without touching the derivation.
- Fixtures: `lifecycle_registry(allowlist=…)` in
  `test_arm_readiness_evidence.py` (25 call sites, 6 with explicit
  allowlists) becomes derived-by-default; explicit allowlists only where a
  test asserts a refusal. The lifecycle fixture's manual path rewriting
  (`test_arm_readiness_lifecycle.py:143–163`) collapses to re-deriving from
  the rotated record. This is the real cost, and it is the right cost: those
  fixtures model an open allowlist the contract forbids.
- Replace the current acceptance test with §3's; keep
  `test_registry_load_closes_conditional_code_paths_against_allowlist`.
- Land only outside a changed-set window; the registry is in the relevant
  set (D-151 cond. 8: window property, not repo invariant).

## 5. Decision log

Dated addendum to D-151, not a new decision: "V-1(vii) INSTALLED 2026-09-0x:
`irrelevant_path_allowlist` is checked equal to the manifest derived from the
lifecycle record's own successor ids and PASS freeze id for EVERY lifecycle
record; the derived-manifest dissent is now the mechanism; clause 7 is
enforced by construction (no derivation input can name a path outside
§1's families); the in-code manifest digest is retired under D-161." Record
it under the ruled-not-installed pattern as decided→done.

## Disagreements with the earlier rulings

1. The original row acceptance ("derive the forbidden set from registered
   authenticator roles") was wrong at altitude: a deny-list over an open
   semantic class cannot close. Trace 06 got this right; I concur with it.
2. The park ruling's question, "the closed set … across registry ids", is
   malformed. The registry id is a label, not an input; asking how membership
   varies across ids invites another id-keyed table, which is a fourth
   opt-in. Membership is a function of the record's declared successors.
3. PARKED was too strong. The third occurrence is one conjunct and one pin,
   both traceable to fixture pressure. A consult round costs more than the
   fix. The same-signature rule still earned its keep by catching it.
4. Trace 07's SHA pin was a mistake, not a feature; it caused the defect.
5. Trace 08's cure ("apply the check independently of identifier") is
   necessary but not sufficient: with the pin and hard-coded ordinal kept,
   an unconditional check refuses every fixture and every future generation,
   and the next seat will reintroduce a gate. The ordinal and pinset must be
   inputs first.
6. The marker's own id literal at :10927 is a second `d117-r1-lifecycle-v1`
   spelling. It fails closed, so it is not a bypass, but it should share one
   constant with the registry loader rather than be a third spelling.
