# Block 5 RELEASE + UNSEAL runbook

Prepared 2026-11-05. **Procedure only: block 5 remains blind.** This document records
no comparator verdict, release, or permission to open study data in this writing
session. Its real-data commands are for a later operator explicitly authorized
to use the custody roots, including restricted directories. The writing lane
stays inside this clone, uses no network, and runs no analysis or measurements.

## Authority and fixed handoff

The release path is [analysis_plan_block5.md:184–199][plan-release] (§3.2) and
[registration_block5.md:4842–4848][reg-event] (§8.3). Apply the later binding
readings [D-188, decision_log.md:12239–12248][d188],
[D-189, decision_log.md:12251–12261][d189], and
[D-190, decision_log.md:12263–12272][d190]; do not edit the sealed documents to
install those readings.

| Role | Fixed referent / current state |
|---|---|
| Release analysis | Annotated tag `b5/analysis-r2`, commit `929fc65c9ce3ff82f0311d28acf76a682edd466f`; tree `9e89d7ff48999416467129c03ea171fc3a1f3f83` |
| Equivalence oracle | Annotated tag `b5/analysis-r1-9bfix-ref`, commit `e7eb872d232ab58efe3ff861ae2c33dbfd8c0a33`; tree `de2e980edecf9047efd5c86dd4f31488a6d5a739`; never merge this reference branch |
| Reference run | dry-i, custody root `$REF_CUSTODY`; running at the task handoff |
| Candidate run | dry-j, custody root `$CAND_CUSTODY`; task handoff says finished, exit 3, step 9b `outcome_class`, steps 10 and 11 `ok` |
| Release checkout | `$R2_WORKTREE`, clean and detached at the exact r2 commit above |

Tag commits and trees were checked from this clone's Git objects; no custody was
accessed. [RUN_STATE.md:1004–1024][state-r2] records the tags, PR #643, and the next
comparison, but still calls dry-j running. The finished-dry-j statement above is
the newer **user-provided handoff**, not a locally observed run result. Resolve
all three variables from the lead's real handoff; this runbook supplies no paths.

There are two different comparisons:

- **Reference vs rewrite:** D-188 result equivalence, with audit differences
  allowed. Use the independent comparator below.
- **dry-j vs its release:** identical inputs and registered output commitments
  at the **same r2 commit**. Use the driver's release check. D-188 does not
  authorize release-time arithmetic or input changes. See
  [analysis_plan_block5.md:189–199][plan-release] and
  [dry_run.py:2006–2028, 2076–2100][driver-release].

## Preconditions checklist — remain blind

- [ ] The designated lead owns the event and final verification. Check current
  stop cards and machine-state restrictions; this task is desk work, not a
  quiet-machine capture. Do not disturb the existing seven-worker job. Arrange
  an uninterrupted analysis window with the host owner; never suspend a refit
  to make room. See [AGENTS.md:38–68][agent-intake] and the deadline branch below.
- [ ] The block is closed: each pack has its first claim-usable attempt, or the
  registered END STATE applies. No undecided UNCLASSIFIED code remains. Confirm
  from released structure and pinned automation, without opening exclusions or
  outcome logs. [analysis_plan_block5.md:51–64][plan-inputs];
  [registration_block5.md:4692–4707][reg-unclassified].
- [ ] Preserve raw bundles, archives, prior attempts, and both dry runs. Custody
  is write-once. No re-collection, mutation, deletion, in-place retry, or new
  attempt selection is part of this procedure.
  [registration_block5.md:568–576][reg-custody].
- [ ] Confirm the applicable **second seal**, harvest addenda and final harvest
  record digests. Bind registration, plan, catalog, applicable errata, inventory,
  and each analysed window to the correct seal era. Use the second-seal table at
  [SEAL_RECORD.md:394–417][seal-second], not the older §4 table alone.
- [ ] The **analysis-code addendum** exists before the event: analysis commit,
  files and their SHA-256s, date and authoring seat, whose record states that it
  read no claim-window energy. Include the D-189/D-190 rebind and the r2 tag;
  the reference is only the oracle. This is required by
  [registration_block5.md:5519–5544][reg-pins]. See gaps below: an r2 tag by itself
  does not supply this addendum.
- [ ] Record exact commit and tree identities and environment provenance. Preserve
  the Python minor version, dependency lock and relevant OS/toolchain notes;
  use the established r2 environment, without installing or upgrading anything.
  [freeze_by_commit.md:48–69, 83–86][freeze-identity].
- [ ] Confirm required L9 review evidence from the owning handoff. The 2026-10-27
  amendment makes this one stage of two executing reviews; do not reintroduce
  superseded full-size synthetic gates.
  [ED-RULING.md:93–97][l9-review].
- [ ] Both dry runs have terminal, authenticated structural records at their
  fixed tags. Require completion without tooling refusal **and** the expected
  full step sequence through 11; an EQUIVALENT pair of incomplete/stopped runs
  would not establish this. For dry-j's expected D-189 pattern, require exactly
  one non-stopping 9b row, no 9b outputs/flags, and 10/11 `ok`.
  [dry_run.py:1517–1531][nonstopping]; [D-189 item 2][d189].
- [ ] The comparator checkout is independent of `$R2_WORKTREE` and contains the
  reviewed PR #643 comparator and its own `equivalence_*.json` configs. Record
  its commit and printed code/config hashes. Tiers remain leaf-local, exemptions
  remain reviewed, and timing policy remains `strict`.
  [compare_b5_results.py:13–54][comparator-contract];
  [equivalence_tiers.json:258][tiers-strict];
  [equivalence_exemptions.json:1–5][exemptions].
- [ ] Resolve the independent-recompute evidence/order question in **Gaps** before
  the event. Result equivalence is not independent recomputation of the science.
- [ ] `$CAND_CUSTODY/release/` does not already exist; custody is outside the
  analysis repository, absolute, whitespace-free and symlink-free. Keep the
  original index, inputs, ledger bytes, VDL selection and analysis environment.
  Do not use `$REF_CUSTODY` as the release destination.
  [run_b5_analysis.py:24–55][driver-flags]; [dry_run.py:347–370][custody-preflight].

## 1. Compare dry-i and dry-j while blind

**Later authorized operator only.** In the independent comparator checkout,
with the two existing custody variables set:

```sh
: "${REF_CUSTODY:?set from the lead handoff}" "${CAND_CUSTODY:?set from the lead handoff}"
python3 -I -B tools/b5_equivalence/compare_b5_results.py \
  --mode blinded --run blind-dry-run "$REF_CUSTODY" "$CAND_CUSTODY"
comparator_rc=$?
printf 'comparator_exit=%s\n' "$comparator_rc"
```

Capture the exit code immediately; do not pipe away the comparator's status.
The entry point and switches are
[compare_b5_results.py:2041–2083][comparator-cli]. Read only its fixed-grammar
stdout and `$CAND_CUSTODY/equivalence/BLINDED-VERDICT.txt`, never the valued
reports in `equivalence/restricted/`. Those reports can contain outcomes even
when the invocation is blinded. No `--mode open` on study data: the tracked
open-index list permits only synthetic/engineering inputs.
[compare_b5_results.py:48–54, 89–91][comparator-contract];
[equivalence_open_indices.json:1–16][open-indices].

| Exit / exported verdict | Action |
|---|---|
| `0` / `VERDICT: EQUIVALENT` | Require inputs, decisions, registered and intermediate `MATCH`, full completed-run coverage and the reviewed strict policy. Audit `DIFFER (not printed)` is allowed. Save the header, verdict and record digests as structural evidence; proceed only with the preconditions met. |
| `1` / `VERDICT: NOT_EQUIVALENT` | Stop before the release event. Preserve both runs; investigate only the emitted role/section names while blind. No tolerance, tier relaxation, audit promotion or candidate selection to obtain a pass. |
| `2` / `COMPARATOR_ERROR stage=… side=…` | No equivalence established. Fix the comparator/custody issue within its reviewed authority and repeat the blinded comparison. Do not inspect the restricted traceback in a blind seat. |
| Pending, absent, truncated output, signal, or exit/verdict disagreement | No usable verdict. A previous exported success cannot stand in for this invocation. |

Semantics: [compare_b5_results.py:7–11, 19–46][comparator-contract],
[1898–1916][comparator-output], [1992–2027][comparator-freshness],
[2083–2104][comparator-cli]. Commit-derived digests are checked by **verified
referent** on each side, not accepted as arbitrary differing hashes; the
underlying artifacts still compare at their own leaf tiers. Step-9b non-issuance
and absent claim-side-bound custody are decisions, not audit exemptions
([D-189 item 5][d189]). Do not infer which non-issuable state occurred.

## 2. Record the release event — this is the unseal boundary

After step 1 and the preconditions, the **lead** appends the actual event to
`docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md`, in its existing
**“Release event”** section. It currently says “Nothing is recorded here yet”
([SEAL_RECORD.md:624–628][seal-event]). Do not write a release into the sealed
registration or replace its hashes. The event must tie the sealed registration,
plan and catalog SHA-256s to the final harvest records
([registration_block5.md:4842–4848][reg-event]).

Use a dated, attributed event record with these reviewable fields. The first
binding is the registered requirement; the additional links make this runbook's
execution auditable rather than create a new signed-attestation protocol:

- Effective UTC time and lead/seat identity; the three sealed-document digests,
  applicable seal/errata, final harvest paths and digests for each analysed pack.
- Analysis-code addendum pointer; r2 commit/tree and annotated tag; reference
  commit/tree and tag; index digest; environment/lock pointer.
- dry-i/dry-j record paths and hashes, terminal status evidence, comparator
  checkout/code/config hashes, blinded verdict and exit code; required review
  and independent-recompute evidence or the lead's recorded ordering disposition.
- The pre-event authors'/reviewers' actual blinding statements and the designated
  post-event readers. Never attest on someone else's behalf or backdate a record.

The seal record's append convention requires date and writing seat
([SEAL_RECORD.md:309–317][seal-append]); the program addendum's blind-author
requirement is [registration_block5.md:5519–5522][reg-pins]. No separate
cryptographic release attestation or `b5/release` tag is defined in those sources.
Keep existing annotated tags; a ruled future fix gets a new analysis revision
and old/new trees under [freeze_by_commit.md:48–69][freeze-identity].

**What becomes readable, and by whom.** The event lifts the study's withholding
rule for the lead and the results cold gate. This includes bundle energies,
powers and phase durations, floor/mean/ratio values, numeric calibration
diagnostics, restricted flag codes and counts; the claim/bound runs roots,
restricted custody logs, copied archive sources, `withheld/`, the three restricted
`derived/` files, and backups/offloads are enumerated in
[registration_block5.md:4826–4841, 4874–4904][reg-readers]. The dry-run output tree
and comparator valued reports contain the same protected class of information.
This is an access-rule transition: custody already has ordinary filesystem
permissions ([registration_block5.md:4850–4856][reg-map]); no chmod, move,
decryption, or deletion is specified. It does not publish the data or authorize
unregistered analyses. A seat reserved for writing/reviewing a repair must
still read **no released number**, even after the event
([registration_block5.md:4901–4904][reg-readers]; [PLAN §3.2 item 3][plan-release]).
This writing session's stricter access prohibition remains in force.

## 3. Run RELEASE at r2 into dry-j's custody root

**Later authorized operator only, after the event.** Verify the clean checkout
and tag locally; stop if any identity differs. Do not fetch, move tags or change
inputs. From the established Python 3.13 environment:

```sh
: "${R2_WORKTREE:?set from the lead handoff}" "${CAND_CUSTODY:?set from the lead handoff}"
cd "$R2_WORKTREE" || exit 2
test "$(git rev-parse HEAD)" = 929fc65c9ce3ff82f0311d28acf76a682edd466f || exit 2
test "$(git rev-parse 'b5/analysis-r2^{commit}')" = 929fc65c9ce3ff82f0311d28acf76a682edd466f || exit 2
test -z "$(git status --porcelain)" || exit 2
python3.13 -B scripts/run_b5_analysis.py \
  --mode release --index configs/analysis/b5/analysed_windows.json \
  --custody "$CAND_CUSTODY" --workers 2
release_rc=$?
printf 'release_exit=%s\n' "$release_rc"
```

Two workers bound host load here; the CLI promises the same record/output
semantics for every worker count ([run_b5_analysis.py:29–32][driver-flags]).
Preserve dry-j's recorded VDL selection; do not guess it from defaults or change
it to cure a failure. The only modes are `blind-dry-run` and `release`; the index
and custody arguments are required. An optional `--phase-log` is structure-only
and needs a new absolute path outside both repository and custody, without
symlinks; it is omitted here to avoid inventing a path. See
[run_b5_analysis.py:9–66, 85–117][driver-flags].

The driver writes `$CAND_CUSTODY/release/B5-RELEASE-RECORD.json`; it still puts
step outputs under `release/restricted/`. Exit 0 means all steps completed;
exit 3 means an outcome class without tooling/unclassified refusal; exit 2
blocks completion. For the handoff's dry-j pattern, expect **3**, with the same
single 9b non-stopping row and steps 10/11 `ok`, not a fabricated success code.
[D-189 items 1–4][d189]; [dry_run.py:2090–2100][driver-release].

## 4. Verify RELEASE before opening results for use

The lead records the new record's path/hash, exit status and completion. Require
the exact r2/index/seal bindings, identical attempt selection, kept counts and
input census, and the same step decisions as dry-j. Require no
`release_difference`; all scientific outputs, **both** disclosure views and the
validated fill input have identical commitments. The driver checks inputs before
step 0 and outputs at completion; a difference becomes
`release_digest_differs_from_dry_run`, including a first differing input path or
step/output name. [dry_run.py:176–210][release-primitive],
[2006–2028, 2076–2100][driver-release].

**Do not compare whole JSON files with `cmp`.** Their `mode` differs, and real
step-code audit sidecars have fresh random whitespace salt. The shipped equality
primitive excludes only names accepted by `is_sidecar_name` (step codes and the
VDL-mode token); it does not exempt scientific artifacts. These are distinct
from D-189's absent claim-side-bound sidecar.
[dry_run.py:176–210, 283–289][release-primitive];
[1887–1917][driver-audit]. The earlier synthetic checks asserting identical step
rows are [test_release_equality.py:9–35, 97–110][equality-tests]; changed-output
and changed-input refusals are pinned by [test_release_equality.py:45–81,
112–139][equality-tests]. They are not evidence that real run records are
byte-identical.

For this run's D-189 outcome specifically, verify **no claim-side-bound sidecar
and no claim-evidence custody** in either run. The validated 9b row has no
outputs or flags, and code returns before writing the sidecar, replay request,
floor acceptance, claim-evidence receipt/inventory or role census
([dry_run.py:1534–1560][claim-open]; [D-189 item 1][d189]). Ordinary reported-energy
custody and the mint's dominance sidecar still exist. Files are content-addressed
as hashes, so a filename search for `claim-side-bound.json` cannot prove absence
([dry_run.py:612–630][addressed-write]).

The following **later authorized post-event check** reads the two public
records and classifies only the custody JSON schemas/family markers and claim
role census; it prints one fixed token. It does not authenticate raw evidence
or rerun analysis; the driver's validated release is the prerequisite. Run from
`$R2_WORKTREE` after the command above. The physical absence check necessarily
accesses `restricted/`, so it is forbidden in this documentation session.

```sh
python3.13 -B - "$CAND_CUSTODY" <<'PY'
from copy import deepcopy
import json
from pathlib import Path
import sys
from joulewise.b5_analysis import dry_run as d

try:
    if sys.flags.optimize:
        raise RuntimeError('assertions must be enabled')
    root = Path(sys.argv[1])
    records = []
    for directory, filename, mode in (
        ('dry-run', 'B5-BLIND-DRY-RUN-RECORD.json', 'blind-dry-run'),
        ('release', 'B5-RELEASE-RECORD.json', 'release'),
    ):
        record = json.loads((root / directory / filename).read_bytes())
        assert record['mode'] == mode
        assert record['analysis_commit'] == '929fc65c9ce3ff82f0311d28acf76a682edd466f'
        assert record['completed_without_tooling_refusal'] is True
        assert 'release_difference' not in record
        rows = record['steps']
        assert len([r for r in rows if r['step'] == '9b']) == 1
        assert all(r['status'] == 'ok' or d.is_nonstopping_outcome(r) for r in rows)
        assert all(any(r['step'] == step and r['status'] == 'ok' for r in rows)
                   for step in ('10', '11'))
        assert any(d.is_nonstopping_outcome(r) for r in rows)
        restricted = root / directory / 'restricted'
        assert not (restricted / 'supply-census/claim-evidence-gamma.json').exists()
        for path in (restricted / 'custody').glob('*.json'):
            value = json.loads(path.read_bytes())
            assert value.get('schema_version') != 'joulewise.claim_side_bound.v2'
            assert value.get('schema_version') != 'joulewise.claim_replay_request.v1'
            assert value.get('family') != 'claim_evidence'
            assert value.get('schema_version') != 'joulewise.paper_floor_acceptance.v1'
        normalized = deepcopy(record)
        normalized.pop('mode')
        for row in normalized['steps']:
            row['outputs'] = [o for o in row['outputs'] if not d.is_sidecar_name(o['name'])]
        records.append((record, normalized))
    d.require_release_equality(records[0][0], records[1][0])
    assert records[0][1] == records[1][1]
except Exception:
    print('RELEASE_POSTCHECK_FAILED')
    raise SystemExit(2) from None
print('RELEASE_POSTCHECK_OK')
PY
```

Schema/family classification follows [claim_side_bound.py:17][bound-schema],
[paper_custody.py:36, 519][custody-schemas] and
[dry_run.py:1328–1353][claim-custody]. A failed check stops result use; preserve
the records rather than print the compared objects. See gaps for the limits of
this supplemental check and the literal record-equality wording.

## 5. Open, cross-check, fill, and hand off — in this order

1. With the event recorded and release verified, the designated **post-release
   reader** may open the results under the §8 reader rule. Log who first reads
   numbers and when, so repair authors/reviewers can remain blind. Do not
   broaden access to every agent session or publish raw custody.
2. Complete the **independent recompute / results cold gate** before using any
   printed number. The independent arithmetic entry is
   [independent_recompute_b5.py:1–16, 2840–2852][recompute]; its comparator is
   [compare_b5_recompute.py:4027–4072][recompute-compare], with block-5 bars in
   `configs/analysis/b5/recompute_bars.json`. It is separate from D-188's exact
   equivalence comparator. Resolve the event-order gap below; do not copy
   block-6 S-13 tolerances into block 5. The lead's block-5 bars and the duty to
   hand-check any printed uncovered leaf are [RUN_STATE.md:339–342][recompute-state].
   The required results gate re-derives every printed number
   ([analysis_plan_block5.md:171–172][paper-plan]). No recompute command is
   fabricated here: its existing output path and archive arguments must come
   from the owning handoff.
3. Use step 11's **validated fill input**, addressed by the release record:
   `release/restricted/outputs/results-fill-input.json`, plus its disclosure
   record and released/unreleased views. Trace each item by the record's digest,
   not an ad hoc evidence path. The implemented chain is sensitivity →
   `scripts/produce_b5_disclosures.py` → `scripts/build_results_fill_input.py`;
   [dry_run.py:1716–1739][step11] and
   [build_results_fill_input.py:84–111][fill-input] show validation and arguments.
4. **Do not run the retired renderer to fill block 5.** Although
   [v5-artifact-flow.md:24, 32][artifact-flow] describes `render_results_fills.py`
   and calls the adapter missing, the later
   [SEAL_RECORD.md:631–638][renderer-deviation] explicitly ends the dry run at
   the validated input, with `results_rendering_not_run_no_block5_template`.
   A block-5 Results renderer must print every contrast-census row with its
   issued state, unsupported/refused included, validate row-for-row, and pass
   the Results cold gate before its numbers enter the paper.
5. Preserve nulls and non-issuance. D-190 leaves registered not-resolvable and
   not-estimable values null; do not substitute zero or a default claim. A fill
   requiring `VerifiedClaimEvidence` cannot issue without the claim-side-bound
   sidecar; it must refuse downstream ([D-189 item 4][d189]; [D-190][d190]).
6. Record actual release verification, results-gate/recompute status, readable
   scope, remaining STOP_FILLs and next work in `RUN_STATE.md` and a dated run
   report. Update `TASK_QUEUE.md` via its generated-state rules when live
   selection changes, and `PROJECT_STATUS.md` only if advisor-visible state
   changes ([AGENTS.md:120–128][handoff]; [AGENT_PLAN.md:10–20][state-rules]).
   Cite D-188/D-189/D-190; put any **new** scientific deviation/ruling in
   `docs/decision_log.md` with its authority and disposition. The existing
   decisions do not require inventing another decision number just to log
   execution ([AGENT_PLAN.md:19–20][state-rules]).
7. Only after the actual release, hand off `FREEZE-BY-COMMIT-01` as the next
   implementation task ([TASK_QUEUE.md, row A346][next-task];
   [freeze_by_commit.md:102–118][freeze-rollout]). The pre-event runbook does not
   discharge that task, revise frozen estimators, or authorize pruning.

## Ed-only actions and manual lead work

- **Ed:** new science/scope/estimator rulings, exceptions to his blinding/access
  rules, hardware/access decisions, and owner actions requiring his hands or
  credentials. Keep a laptop run plugged in and stationary under the owner's
  availability; if that cannot be maintained, arrange a fresh run rather than
  pause/resume it ([RUN_STATE.md:303][no-pause]). The runbook grants no sudo,
  process-signalling, physical-machine or integration authority.
- **Lead, manually:** identify the roots and readers; verify pins, reviews and
  verdicts; author the program addendum and Release event; keep repair seats
  blind; perform final verification and bookkeeping. The registration assigns
  the event to the lead, **not an Ed-only unseal command**
  ([registration_block5.md:4842–4848][reg-event]). Ordinary process calls need
  no invented new owner stop ([RETROSPECTIVE.md:68][process-calls]).
- No source located here defines an Ed password/key ceremony, an Ed signature,
  an OS permission change, or a required new release tag for block 5. If an
  external custody arrangement needs one, obtain its actual instructions from
  Ed; do not guess or treat this document as supplying them. Ownership of
  scientific direction and final lead responsibilities is
  [orchestration.md:14–27][roles].

## Failure branches

| Condition | Required disposition |
|---|---|
| `NOT_EQUIVALENT` | Stay blind; retain both roots and the blinded differing-field names. Diagnose in source/synthetic fixtures. Apply a reviewed blind repair under D-188/R3; use new immutable run roots and, when governed code changes, a new analysis revision/addendum. Repeat the comparison against the fixed reference. Never widen equality or silently reuse dry-j after changing code. |
| Comparator error or timing-truncated coverage | No proof. Correct the comparator/custody problem or obtain a fresh complete reference. Do not use a matching prefix as an end-to-end release gate. Current `timing_class_policy` is `strict`. |
| 9b `outcome_class` with D-189's exact row; 10/11 `ok` | Expected non-stopping outcome, exit 3. Continue to equality and the registered release path; no probing for the underlying state and no sidecar fabrication. |
| Any other non-`ok` row, or 10/11 not `ok` | Stop and inspect only public classification. Tooling → R3, same data, blind fix if needed and fresh run. Unclassified → classify blind under authority; do not expose raw logs. Other registered scientific outcomes remain results; the driver stops later rows, so they cannot be represented as this completed through-11 handoff without a lead disposition. Registered p42 exits are already recorded as completed, not a new exception. |
| Step-deadline failure caused by approximately 19 h of SIGSTOP-frozen elapsed time; `calibration_wall_deadline_fired` is the implemented active-refit example | This is elapsed-time host failure, not evidence of a science/code defect. Preserve the failed attempt and stop/freeze timing record; do not change the deadline, deterministic cell budget, arithmetic, exclusions or decision rules. Run **fresh from the beginning**, same pinned code and immutable inputs, into a new custody root on an uninterrupted host. Do not resume the frozen process as a valid continuation. The 19 h scenario comes from the task; neither its actual refusal code nor its timing was independently observed here. |
| Release input/output digest mismatch | Stop result use. Preserve `release_difference` and both runs; route as a determinism/custody defect under PLAN §3.2. Never edit a record or copy dry-run outputs over release outputs. A release directory cannot be reused; the complete dry-run/release pair needs fresh custody for retry unless a later ruling defines a different route. |
| Archived ledger digest/prefix failure | Custody incident: cold gate, not automatic R3. No rewriting the ledger or archive. The live-ledger prefix rule and its distinct refusal routes are [L9 RULING.md:163–177][ledger-rule]. |
| Repair after numbers have been read | Use authors **and reviewers** that have read no released number, reproduce with a synthetic fixture, keep other registered fixture outputs byte-identical. Otherwise obtain a cold ruling before running and label outputs produced after unblinding. [PLAN §3.2 item 3][plan-release]. |
| Missing claim-side-bound custody blocks a paper fill | Preserve the refusal/STOP_FILL. D-189 permits the release outcome; it does not issue `VerifiedClaimEvidence`. A future presentation/contract remedy needs its own authority. |

Deadline authority: [ED-RULING.md:53–78][deadline-ruling]. The 120 s budget is
[powermetrics_fiducial.py:90–94, 526–550][wall-clock]: it checks elapsed
`time.monotonic()`, not CPU time. A SIGSTOP interval can therefore exhaust an
active budget on resumption. The observer and driver convert a firing into a
tooling refusal at its step ([deadline_observer.py:1–19][deadline-observer];
[dry_run.py:2057–2071][driver-release]). This case needs a fresh run, not a
speculative code change. Do not alter the running job from this writing lane.

## Gaps / blockers and contradictions to carry forward

1. **Operational evidence is unverified here.** No custody path, dry-i terminal
   record, final dry-i/dry-j verdict, r2 environment record, release record or
   physical no-sidecar check was opened. dry-j's completion comes from the task;
   `RUN_STATE` item 165 is stale on that point. This is a procedure, not a GO.
2. **Analysis addendum / event still need evidence.** This clone's seal record
   has harvest addenda and a later meter addendum, but no identified r2
   analysis-program file/hash addendum; its Release event is still a placeholder.
   The lead must locate the authoritative addendum or supply the missing
   record before the event, without claiming a retrospective record existed
   earlier. No executable validates the addenda/seal record
   ([registration_block5.md:5689–5700][reg-manual-pins]).
3. **No fully specified unseal attestation protocol.** §8 defines actor, ordering,
   document digests, harvest binding and readable scope; it does not fix a
   release-record schema, signature method, UTC format, reader log, Ed-only
   ceremony or new tag. The event fields above are a practical checklist, not
   evidence that the repo already mandates those extra formats.
4. **Literal “record equals” needs the audit qualification.** D-189 item 4 says
   the records equal; `mode` differs, and D-188 real audit sidecars are salted
   and written after equality. The operative comparison is the shipped
   `release_difference` plus matching bindings/decisions, excluding its two
   recognized audit sidecar classes. Do not promise whole-file equality or
   “no sidecars of any kind.” The inline postcheck is supplemental, assumes
   driver-validated records, and checks the current JSON schema/family layout;
   it is not an independent custody authenticator.
5. **Independent-recompute ordering needs a lead disposition.**
   [RUN_STATE.md:67][recompute-old-order] says release by dry run plus independent
   recompute agreement; [RUN_STATE.md:1023][state-r2] gives the next step as final
   equivalence then release. The equivalence tool is not the recompute tool.
   Find the actual recompute agreement and its governing ordering before the
   event; if the records do not settle the discrepancy, the lead records a
   ruling rather than silently waiving either check. The results cold gate
   before paper use remains explicit in PLAN §3.1 step 12.
6. **Paper rendering is not delivered by a successful release.** The seal's
   declared deviation supersedes the plan/flow's renderer instructions. No
   block-5 Results template is supplied by this runbook. Missing sidecars can
   separately block claim-evidence fills even when the fill input is valid.
7. **Live ledger identity is stricter than an unchanged archived prefix.** The
   current driver records the *whole live ledger* hash in its input census
   ([dry_run.py:726–729][live-ledger]) and compares that hash again before
   release ([dry_run.py:1770–1793][live-ledger-diff]). Appending valid later
   observations can thus block release equality even while the archived copy
   remains a valid prefix. Do not roll a ledger back or substitute a different
   file. Coordinate custody/ledger stability with the owning lead; if it has
   changed, resolve under authority with fresh blinded evidence as needed.
8. **Post-release implementation stays deferred.** Freeze-by-commit phase 1,
   pruning, deferred parallel cleanup and a D-178 non-issuable successor are
   separate work ([RUN_STATE.md:1024][state-r2]; [freeze rollout][freeze-rollout]).
   This documentation changes no frozen program, pin, scientific rule or data.

[plan-release]: ../../configs/campaigns/v5_claim_25g83/analysis_plan_block5.md#L184
[plan-inputs]: ../../configs/campaigns/v5_claim_25g83/analysis_plan_block5.md#L51
[paper-plan]: ../../configs/campaigns/v5_claim_25g83/analysis_plan_block5.md#L171
[reg-event]: ../../configs/campaigns/v5_claim_25g83/registration_block5.md#L4842
[reg-custody]: ../../configs/campaigns/v5_claim_25g83/registration_block5.md#L568
[reg-unclassified]: ../../configs/campaigns/v5_claim_25g83/registration_block5.md#L4692
[reg-pins]: ../../configs/campaigns/v5_claim_25g83/registration_block5.md#L5519
[reg-manual-pins]: ../../configs/campaigns/v5_claim_25g83/registration_block5.md#L5689
[reg-map]: ../../configs/campaigns/v5_claim_25g83/registration_block5.md#L4850
[reg-readers]: ../../configs/campaigns/v5_claim_25g83/registration_block5.md#L4826
[seal-second]: ../process_traces/2026-10-07-block5-seal/SEAL_RECORD.md#L394
[seal-event]: ../process_traces/2026-10-07-block5-seal/SEAL_RECORD.md#L624
[seal-append]: ../process_traces/2026-10-07-block5-seal/SEAL_RECORD.md#L309
[renderer-deviation]: ../process_traces/2026-10-07-block5-seal/SEAL_RECORD.md#L631
[d188]: ../decision_log.md#L12239
[d189]: ../decision_log.md#L12251
[d190]: ../decision_log.md#L12263
[state-r2]: ../../RUN_STATE.md#L1004
[recompute-state]: ../../RUN_STATE.md#L339
[recompute-old-order]: ../../RUN_STATE.md#L67
[no-pause]: ../../RUN_STATE.md#L303
[agent-intake]: ../../AGENTS.md#L38
[handoff]: ../../AGENTS.md#L120
[state-rules]: ../../AGENT_PLAN.md#L10
[roles]: ../orchestration.md#L14
[next-task]: ../../TASK_QUEUE.md
[freeze-identity]: freeze_by_commit.md#L48
[freeze-rollout]: freeze_by_commit.md#L102
[comparator-contract]: ../../tools/b5_equivalence/compare_b5_results.py#L7
[comparator-cli]: ../../tools/b5_equivalence/compare_b5_results.py#L2041
[comparator-output]: ../../tools/b5_equivalence/compare_b5_results.py#L1898
[comparator-freshness]: ../../tools/b5_equivalence/compare_b5_results.py#L1992
[tiers-strict]: ../../configs/analysis/b5/equivalence_tiers.json#L258
[exemptions]: ../../configs/analysis/b5/equivalence_exemptions.json#L1
[open-indices]: ../../configs/analysis/b5/equivalence_open_indices.json#L1
[driver-flags]: ../../scripts/run_b5_analysis.py#L9
[custody-preflight]: ../../joulewise/b5_analysis/dry_run.py#L347
[driver-release]: ../../joulewise/b5_analysis/dry_run.py#L2006
[nonstopping]: ../../joulewise/b5_analysis/dry_run.py#L1517
[release-primitive]: ../../joulewise/b5_analysis/dry_run.py#L176
[driver-audit]: ../../joulewise/b5_analysis/dry_run.py#L1887
[equality-tests]: ../../tests/b5_analysis/test_release_equality.py#L9
[claim-open]: ../../joulewise/b5_analysis/dry_run.py#L1534
[claim-custody]: ../../joulewise/b5_analysis/dry_run.py#L1328
[addressed-write]: ../../joulewise/b5_analysis/dry_run.py#L612
[bound-schema]: ../../joulewise/analysis_engine/claim_side_bound.py#L17
[custody-schemas]: ../../joulewise/paper_custody.py#L36
[step11]: ../../joulewise/b5_analysis/dry_run.py#L1716
[fill-input]: ../../scripts/build_results_fill_input.py#L84
[artifact-flow]: v5-artifact-flow.md#L24
[recompute]: ../../scripts/independent_recompute_b5.py#L1
[recompute-compare]: ../../scripts/compare_b5_recompute.py#L4027
[l9-review]: ../process_traces/2026-10-27-l9-restart/ED-RULING.md#L93
[deadline-ruling]: ../process_traces/2026-10-27-l9-restart/ED-RULING.md#L53
[deadline-observer]: ../../joulewise/b5_analysis/deadline_observer.py#L1
[wall-clock]: ../../joulewise/powermetrics_fiducial.py#L90
[ledger-rule]: ../process_traces/2026-10-block5/l9-rulings/RULING.md#L163
[live-ledger]: ../../joulewise/b5_analysis/dry_run.py#L726
[live-ledger-diff]: ../../joulewise/b5_analysis/dry_run.py#L1770
[process-calls]: ../process_traces/2026-11-04-d188-retrospective/RETROSPECTIVE.md#L68
