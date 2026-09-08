```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Installed D-176 decision and kernel graph; all requested checks pass; seat-1 contract draft needs lead wire rulings.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "952dc74123aa1c221cee7dca7bd41ddbd617bb53",
    "head_end": "952dc74123aa1c221cee7dca7bd41ddbd617bb53",
    "upstream_end": null,
    "branch": "feat/2026-09-08-d176-stage3-ruling"
  },
  "pathspec": [
    "docs/decision_log.md",
    "docs/process/state_kernel.json",
    "TASK_QUEUE.md",
    "RUN_STATE.md",
    "tests/test_gen_state.py",
    "docs/contracts/pack_night_go_receipt.md",
    "docs/process_traces/2026-09-08-handoff-redo/85-d176-install-astra-report.md"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-08-handoff-redo/86-brief-d176-install-astra.md"
  ],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "other",
      "cmd": "python3 scripts/gen_state.py > /private/tmp/d176-acceptance-rwx2j4__/generate.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "python3 scripts/gen_state.py --check > /private/tmp/d176-acceptance-rwx2j4__/final-gen-state-check.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_gen_state > /private/tmp/d176-acceptance-rwx2j4__/test-gen-state-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_docs_freshness > /private/tmp/d176-acceptance-rwx2j4__/final-test-docs-freshness.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONPATH=. python3 /private/tmp/d176-acceptance-rwx2j4__/audit_installation.py > /private/tmp/d176-acceptance-rwx2j4__/audit-installation.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS: 10 dependency deletions rejected; exact 23 GO keys and both verbatim replay lists verified"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PASS: 10 dependency deletions rejected;"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check > /private/tmp/d176-acceptance-rwx2j4__/diff-check.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: judge §1 requires replay by a recorded GO path, but its exact v3 go_receipt list has no path and its GO schema has no receipt_id. The draft preserves the ruled lists and cannot define reproducible identity/replay without a ruling.",
      "needs": "Rule the recorded GO path and receipt_id derivation; recommended: adopt Opus go_receipt.path and explicitly pin identity derivation."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: judge §2 requires claim_eligible in consumption and synthesis §2 requires exact-attempt authorization, but their wire placements are not pinned. Authorization authority, confirmation confirmed_at and condition evidence entry encodings are also unspecified.",
      "needs": "Pin these fields/references and JSON encodings in contract §8, then have the Opus refuter review the seat-1 draft before landing or code scope."
    }
  ]
}
```

## Change

Installed the six adopted D-176 decisions in full, the index row and failure-mode
replays; installed the synthesis §5 graph; regenerated the queue and restart
views; updated the live-ID/count pins (149 → 150) and the G2-b dependency
expectation; drafted the seat-1 contract from the governing judge text and only
the expressly adopted Opus amendments. The new row copies NIGHT-REHEARSAL-01's
fences exactly. The old G7-stays-UNRULED fence is retained until its ruled
post-consumer-merge addendum. No task is retired or declared live-complete.

The exact GO key table, required callee keywords, field equalities, two refusal
codes/R-8 registration route, consumption v3/legacy replay, authorization,
confirmation custody/argv/child route, rehearsal purpose/G7, legacy retirement,
and future runtime clause map are in the draft. Its §8 is an explicit
NEEDS_RULING return: the omitted wire details cannot be invented by this seat.
All independent authorized work is finished; contract completion is partial.

**Clause map — installed decision and documentation clauses**

| Ruling clause | Production site of this installation | Biting assertion / inspection | Counterfactual |
|---|---|---|---|
| Synthesis decisions 1–6 and adopted status | `docs/decision_log.md:11161`; index `docs/decision_log.md:222` | `tests/test_docs_freshness.py:679::test_decision_index_matches_decision_bodies` (V4) | Omit the D-176 index while retaining its body; index/body check fails |
| D-176 contract §1 | `docs/contracts/pack_night_go_receipt.md:17` | NOT PINNED: runtime assertion belongs to the subsequent implementation/refutation seat; this is a documentation draft | Produce GO before ARM verify |
| D-176 contract §2 | `docs/contracts/pack_night_go_receipt.md:54` | V5 exact 23-key and verbatim replay inspection | Remove or add a GO key |
| D-176 contract §3 | `docs/contracts/pack_night_go_receipt.md:107` | NOT PINNED: runtime assertion belongs to the subsequent implementation/refutation seat; this is a documentation draft | Allow callee bypass or live v2 replay |
| D-176 contract §4 | `docs/contracts/pack_night_go_receipt.md:173` | NOT PINNED: runtime assertion belongs to the subsequent implementation/refutation seat; this is a documentation draft | Authorize G2-b as a campaign or omit attempt/claim binding |
| D-176 contract §5 | `docs/contracts/pack_night_go_receipt.md:199` | NOT PINNED: runtime assertion belongs to the subsequent implementation/refutation seat; this is a documentation draft | Omit confirmation flags or pass hC through environment |
| D-176 contract §6 | `docs/contracts/pack_night_go_receipt.md:234` | NOT PINNED: runtime assertion belongs to the subsequent implementation/refutation seat; this is a documentation draft | Count G2-a as closure or fake G7 with no production entry |
| D-176 contract §7 | `docs/contracts/pack_night_go_receipt.md:272` | V5 exact 23-key and verbatim replay inspection | Change/drop a verbatim replay case |
| D-176 contract §8 | `docs/contracts/pack_night_go_receipt.md:310` | NOT PINNED: runtime assertion belongs to the subsequent implementation/refutation seat; this is a documentation draft | Silently invent unresolved wire fields |
| D-176 contract §9 | `docs/contracts/pack_night_go_receipt.md:327` | NOT PINNED: runtime assertion belongs to the subsequent implementation/refutation seat; this is a documentation draft | Omit a ruling clause or claim an unbuilt test exists |

Runtime production-site/test cells remain explicitly NOT PINNED in contract §9,
with target seams and one-site counterfactuals, as D-170 requires for a
before-code seat. The contract must receive the lead's wire ruling and Opus
refutation; it is not a claim that those production regressions exist.

**Clause map — synthesis §5, exact kernel JSON pointers**

`J` below is `docs/process_traces/2026-09-08-handoff-redo/78-coldgate-packet-d169-stage3/10-coldgate-fable-ruling.md`, with its exact line number. `K` below is `docs/process/state_kernel.json`. All field pointers resolve in the
written JSON; dependency indices are after generator canonical sorting. The
common biting method is `tests/test_gen_state.py:720` (`test_d176_ruling_installs_build_start_and_live_close_graph
`), which pins build readiness separately from pending live closure. V5 deletes
each of ten dependencies in memory and verifies that this method rejects every
mutation. It never mutates repository files or runs hardware.

| Clause | File:JSON pointer(s) installed | Biting assertion | Counterfactual |
|---|---|---|---|
| J:29; hard-start decision D-176, T0 close, consumer/S9 ownership | `K:/tasks/UNATTENDED-LAUNCH-01/acceptance`; `K:/tasks/UNATTENDED-LAUNCH-01/authority`; `K:/tasks/UNATTENDED-LAUNCH-01/dependencies/0` (close, T0-UNATTENDED-01); `K:/tasks/UNATTENDED-LAUNCH-01/dependencies/1` (start, D-176); `K:/tasks/UNATTENDED-LAUNCH-01/status`; `K:/tasks/UNATTENDED-LAUNCH-01/status_note` | `tests/test_gen_state.py:720` plus V2 pointer/canonical validation | Remove the ruled dependency/value or restore its superseded value |
| J:30; close by consumer PR, no separate implementation | `K:/tasks/S9-06-WINDOW-T0-GO-RECEIPT-GATE-01/acceptance`; `K:/tasks/S9-06-WINDOW-T0-GO-RECEIPT-GATE-01/dependencies/0` (close, UNATTENDED-LAUNCH-01); `K:/tasks/S9-06-WINDOW-T0-GO-RECEIPT-GATE-01/dependencies/1` (start, D-170); `K:/tasks/S9-06-WINDOW-T0-GO-RECEIPT-GATE-01/goal`; `K:/tasks/S9-06-WINDOW-T0-GO-RECEIPT-GATE-01/status_note` | `tests/test_gen_state.py:720` plus V2 pointer/canonical validation | Remove the ruled dependency/value or restore its superseded value |
| J:31; ruling start, decisions 1–4 merged and rehearsal harvested close | `K:/tasks/D169-STAGE3-01/acceptance`; `K:/tasks/D169-STAGE3-01/authority`; `K:/tasks/D169-STAGE3-01/dependencies/0` (close, D176-DECISIONS-1-4-MERGED); `K:/tasks/D169-STAGE3-01/dependencies/1` (close, NIGHT-PACK-REHEARSAL-01); `K:/tasks/D169-STAGE3-01/dependencies/2` (start, D-176); `K:/tasks/D169-STAGE3-01/goal`; `K:/tasks/D169-STAGE3-01/status`; `K:/tasks/D169-STAGE3-01/status_note` | `tests/test_gen_state.py:720` plus V2 pointer/canonical validation | Remove the ruled dependency/value or restore its superseded value |
| J:32; new agent/p1 row, both hard starts, copied fences | `K:/tasks/NIGHT-PACK-REHEARSAL-01/acceptance`; `K:/tasks/NIGHT-PACK-REHEARSAL-01/authority`; `K:/tasks/NIGHT-PACK-REHEARSAL-01/dependencies/0` (start, NIGHT-REHEARSAL-01); `K:/tasks/NIGHT-PACK-REHEARSAL-01/dependencies/1` (start, UNATTENDED-LAUNCH-01); `K:/tasks/NIGHT-PACK-REHEARSAL-01/fallback`; `K:/tasks/NIGHT-PACK-REHEARSAL-01/fences`; `K:/tasks/NIGHT-PACK-REHEARSAL-01/flags`; `K:/tasks/NIGHT-PACK-REHEARSAL-01/goal`; `K:/tasks/NIGHT-PACK-REHEARSAL-01/id`; `K:/tasks/NIGHT-PACK-REHEARSAL-01/lane`; `K:/tasks/NIGHT-PACK-REHEARSAL-01/priority`; `K:/tasks/NIGHT-PACK-REHEARSAL-01/rank`; `K:/tasks/NIGHT-PACK-REHEARSAL-01/status`; `K:/tasks/NIGHT-PACK-REHEARSAL-01/status_note`; `K:/tasks/NIGHT-PACK-REHEARSAL-01/stop_card` | `tests/test_gen_state.py:720` plus V2 pointer/canonical validation | Remove the ruled dependency/value or restore its superseded value |
| J:32; hard-start on pack rehearsal | `K:/tasks/V5-G2B-SHAKEDOWN-01/dependencies/0` (start, NIGHT-PACK-REHEARSAL-01); `K:/tasks/V5-G2B-SHAKEDOWN-01/dependencies/1` (start, V5-DESK-DAY-01) | `tests/test_gen_state.py:720` plus V2 pointer/canonical validation | Remove the ruled dependency/value or restore its superseded value |
| J:33; replace old rehearsal hard start by D-176 | `K:/tasks/T0-UNATTENDED-01/dependencies/0` (start, D-176); `K:/tasks/T0-UNATTENDED-01/status`; `K:/tasks/T0-UNATTENDED-01/status_note` | `tests/test_gen_state.py:720` plus V2 pointer/canonical validation | Remove the ruled dependency/value or restore its superseded value |
| J:33; direct exhibit A §R4/lines pointer and retained G7 fence | `K:/tasks/T0-REHEARSAL-PRODUCERS-01/acceptance`; `K:/tasks/T0-REHEARSAL-PRODUCERS-01/authority`; `K:/tasks/T0-REHEARSAL-PRODUCERS-01/dependencies/0` (close, T0-UNATTENDED-01); `K:/tasks/T0-REHEARSAL-PRODUCERS-01/status_note` | `tests/test_gen_state.py:720` plus V2 pointer/canonical validation | Remove the ruled dependency/value or restore its superseded value |
| J:34; registered limitation through G2-b, close/rerule before ALPHA | `K:/tasks/T0-LIVENESS-BOUND-EMPIRICAL-01/status_note` | `tests/test_gen_state.py:720` plus V2 pointer/canonical validation | Remove the ruled dependency/value or restore its superseded value |
| J:35; magistrate CAMPAIGN_TRANSACTION authorization after G2-b | `K:/tasks/V5-TRANSACTION-GO-01/acceptance`; `K:/tasks/V5-TRANSACTION-GO-01/goal`; `K:/tasks/V5-TRANSACTION-GO-01/status_note` | `tests/test_gen_state.py:720` plus V2 pointer/canonical validation | Remove the ruled dependency/value or restore its superseded value |

The authority on the UNATTENDED launch, stage-3 installer and new rehearsal row
is the synthesis path. Satisfied D-176 decision dependencies point to the named
state-graph regression because the installed clause is **build authority**;
this is not a substitute for the still-pending runtime GO-check-deletion
regression. D169-STAGE3-01 retains its explicit implementation and live-close
dependencies. The installation also reconciles V5-TRANSACTION-GO-01's acceptance
and status prose with its ruled goal; its existing lane and G2-b hard start are
preserved.

`K:/latest_report` points here and `K:/updated` remains 2026-09-08. The generated
regions in `RUN_STATE.md` and `TASK_QUEUE.md` are solely generator outputs; the
manual restart addition identifies the draft's unresolved wire details and the
next exact step. `tests/test_gen_state.py:EXPECTED_IDS`, the 150-count pin in
`test_exact_live_id_set`, and the G2-b hard-start expectation in
`test_quiet_mac_all_lead_only_and_v5_g2a_is_queued_lane_head` are updated with
2026-09-08 comments. The graph method is the new producer regression for this
bookkeeping installation.

**Authority and untouched scope.** No active stop card or global selection gate
was present. This explicit installation brief selects bounded documentation and
graph work over the ordinary queue head. No code, hardware measurement, quiet
window, integration installation, commit, push, merge or message to another
person was performed. The packet is immutable: exhibit A is linked at §R4 lines
161–181 (table at 167–177, G4 preservation at 179), and no
`14-g1-g10-table.md` is created. The pre-existing untracked brief is preserved.
There is no configured branch upstream. No scope expansion is requested.

## Verification notes

The process return codes, not a pipeline's return code, are recorded in the
header. Each requested acceptance command writes a separate log. Baseline:
`gen_state --check` rc 0, `tests.test_gen_state` rc 0 (43 tests), and
`tests.test_docs_freshness` rc 0 (31 tests).

The first post-install state test run returned rc 1 because the existing
G2-b hard-start expectation still listed only V5-DESK-DAY-01. Updated that
expectation in the authorized test file to include NIGHT-PACK-REHEARSAL-01;
the final run returned rc 0 (44 tests). The generator check and docs freshness
acceptance returned rc 0. The repository-wide suite was not run, as the brief
explicitly forbids it; these are documentation, kernel and focused-test changes.

The supplemental inspection script is temporary and read-only with respect to
the repository. Its exact replay command is V5. The first in-memory audit also
rejected four non-edge mutations (copied fences, stale producer pointer, ALPHA
limitation and transaction goal), in addition to those ten edge deletions; its
original log is retained below. Those checks are graph/contract evidence only,
not evidence that the future GO producer or live qualification works.

Temporary logs and audit-script custody (not promoted outside the exhaustive
repository scope; the hashes below preserve the session's artifact identities):

| Temporary artifact | SHA-256 |
|---|---|
| `/private/tmp/d176-acceptance-rwx2j4__/audit-installation.log` | `b79fb6b2789b14df6702aff199de6f14bff3b6b5e5b49ef13403264cebe959fa` |
| `/private/tmp/d176-acceptance-rwx2j4__/audit_installation.py` | `e03848400491a3026296b73b24cf2e47c5148380340af2f5bad47750f2df5122` |
| `/private/tmp/d176-acceptance-rwx2j4__/baseline-gen-state.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `/private/tmp/d176-acceptance-rwx2j4__/baseline-test-docs-freshness.log` | `e9d6822ebdc862562387819454e2551618749447b95706308363c231431e7a5c` |
| `/private/tmp/d176-acceptance-rwx2j4__/baseline-test-gen-state.log` | `f54e0df126f04d4405901004241c0b70ca5e6e2a1a70066806d3d8b40d583e39` |
| `/private/tmp/d176-acceptance-rwx2j4__/contract-inspection.log` | `58456e7bd586b7d7d2c5ec40eb10df882ecdb175ba76b4e0fcbc6689ce84b886` |
| `/private/tmp/d176-acceptance-rwx2j4__/diff-check.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `/private/tmp/d176-acceptance-rwx2j4__/final-gen-state-check.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `/private/tmp/d176-acceptance-rwx2j4__/final-test-docs-freshness.log` | `51d903a5a78a686967d7a49b03f4746f4c031e2f5e13980b722c9f02f2ab091b` |
| `/private/tmp/d176-acceptance-rwx2j4__/gen-state-check.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `/private/tmp/d176-acceptance-rwx2j4__/generate.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `/private/tmp/d176-acceptance-rwx2j4__/mutation-graph.log` | `fe851064a9c5a9250c6e2ddf62eaf0574120271f9c0f671e66d0aa2154f868fc` |
| `/private/tmp/d176-acceptance-rwx2j4__/test-docs-freshness.log` | `148ad372ebf9917fea2832b5ba08f682ac69774b9d3353c8242bb534c42e5316` |
| `/private/tmp/d176-acceptance-rwx2j4__/test-gen-state-final.log` | `e5f8fcf96c5ba4bde8a1f0634e2941003df0f55eec7668f9b9f182316fbd6666` |
| `/private/tmp/d176-acceptance-rwx2j4__/test-gen-state.log` | `b6488e01d51ed70d40dc373bb2573fbdb77cdafd4b8597213deb0062e80a7707` |

## Residual risk

**NEEDS_RULING F1:** the GO receipt has no receipt_id and the judge's v3
reference has no path, although replay requires the recorded path. Options:
explicit Opus-style `go_receipt.path` plus a ruled identity derivation, or a
ruled deterministic locator/identity over existing fields. Recommended: the
explicit path with lead-pinned identity derivation. Blocked: a reproducible exact
v3 identity/replay contract.

**NEEDS_RULING F2:** pin the exact-attempt authorization binding, consumption
claim_eligible placement, and authority/confirmed_at/condition-evidence JSON
encodings. Options: explicit fields and types, or exact references to existing
schemas with named mappings. Recommended: reuse existing formats where applicable
but specify their mappings explicitly. Blocked: a byte/schema-compatible seat-1
contract usable independently by producer and consumer implementers.

Completed authorized work: decision entry/index, graph, generated views, fidelity
pins/regression, the ruled portion of the contract, and this report. Next exact
step: the lead answers contract §8, resumes this seat to install the exact wire
ruling, then sends the completed contract to the Opus refuter before contract
landing and code scope. No further repository paths are needed for that answer.
