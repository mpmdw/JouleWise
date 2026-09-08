```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Installed the D-176 second-pass B1–B5, S1–S6 and N1–N2 wire ruling across the contract and successor scopes.",
  "workspace": {
    "base_requested": "bfedd6fa",
    "base_mode": "exact",
    "head_start": "bfedd6fa196f06591d70c48e4c9443c120d5aaab",
    "head_end": "bfedd6fa196f06591d70c48e4c9443c120d5aaab",
    "upstream_end": null,
    "branch": "feat/2026-09-08-d176-stage3-ruling"
  },
  "pathspec": [
    "docs/contracts/pack_night_go_receipt.md",
    "docs/decision_log.md",
    "docs/process_traces/2026-09-08-handoff-redo/85-d176-install-astra-report.md"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-08-handoff-redo/86-brief-d176-install-astra.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness",
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
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --check",
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
  "flags": []
}
```

## Change

Part 3, 2026-09-08: installed the interactive magistrate's approximately 11:00
PDT ruling verbatim as contract §10, resolving the Opus refutation's B1–B5,
S1–S6 and N1–N2 documentation findings. Propagated the ruling into §§1–8 and
the §9 clause map; appended the dated D-176 decision-log line. GO has 26 exact
top-level keys; its authorization locator has five keys, confirmation locator
two, conditions five, and consumption GO reference seven. The consumption
schemas retain distinct 8/20/22-key sets. G7 has an exact eight-key artifact.

The contract now defines the pinned v3 plan and its authentication route,
plan-persisted attempt ordinal, custody-root resolution, capture marker and
evidence namespace at first use. It specifies both record reads, plan-byte
hash equality, ordered consumer checks, exact author evidence membership and
set digest, shared condition shape/order/status vocabulary, conditional pack
fence lift, ARM-derived window id, shared frozen production roots, all four
rehearsal purpose/root cases, and live-v2 versus historical replay behavior.
§7.1 names each successor's exhaustive WRITE_SCOPE, baseline file:line seams,
focused regression files, shared-file symbol ownership and read-only inputs.
These are successor scope specifications; this turn edited no runtime files.

The §9 B1–B5/S1–S6/N1–N2 rows map every finding to installed clauses, runtime
seams and counterfactual regressions. Runtime tests and final implementation
lines remain NOT PINNED for the implementing seats; documentation installation
does not establish runtime behavior or close a live gate.

Intake: Mission M0 found no active stop card or global selection gate. The
explicit seat brief selects this bounded [AGENT] documentation work over the
ordinary queue. HEAD exactly matches the requested parts-1–2 baseline. The
pre-existing untracked brief is preserved; no upstream is configured. The
exhaustive delegated scope leaves kernel/restart/queue bookkeeping lead-owned.

Next exact step: the lead sends this amended contract to the Opus refuter and
performs the contract landing gate before issuing successor code scopes. No
commit, repository-wide suite, hardware measurement or external consult ran.

**Part-3 verification:** the requested docs-freshness suite passed at baseline
(31 tests, rc 0) and after installation (31 tests, rc 0). `git diff --check`
passed. A read-only contract inspection confirmed 26 unique exact GO keys, all
13 addendum clauses and corresponding clause-map rows, the unchanged verbatim
replay list, replacement of the three gesture clauses, and exactly the three
authorized modified paths. No runtime behavior was tested in this docs-only turn.

Captured post-install acceptance (bytecode writing disabled):

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness
...............................
----------------------------------------------------------------------
Ran 31 tests in 0.950s

OK
rc=0
```

### Historical parts 1–2 evidence

The following preserves prior installation evidence and its then-current wire
counts/status. Part 3 and contract §10 supersede those earlier wire summaries;
prior tests are not represented as checks performed in this turn.


Part 2, 2026-09-08: installed the interactive magistrate's approximately 10:20
PDT wire ruling within the three authorized documentation paths. Contract §8
now gives normative answers: producer-issued UUID4 plus file digest identity;
absolute custody replay locator and independent digest/id refusal; the exact
four-key authorization object with record-copied purpose, attempt and claim
eligibility; the seven-key authorization record including attempt_id; the
six-key consumption GO reference; and exact authority, timestamp, evidence,
digest, monotonic and boolean encodings. GO now has 24 required top-level keys.
The old authorization_record_sha256 scalar is retired in favor of authorization.

Propagated the ruling into §§1–5 and the D-170 clause map. Appended one dated
D-176 decision-log line identifying these as normative amendments to the earlier
key lists and pointing to §8. No adopted outcome was reopened.

**First-use inspection:** read the complete contract, including its replay list
and clause map, for unexplained terms and producer/consumer/replay continuity.
Added definitions for the measurement stages versus rehearsal gates, attempt and
custody root, authorization/confirmation records, UUID4 identity, monotonic/boot
and UTC timing, launch artifacts, claim rechecks, courier/dead-man, HID and
positive controls, registration references, and implementation/qualification
labels. The retained consumption-v2 key list now has an explicit baseline and
owning validator reference. The producer's issue order, callee's own reads,
record-to-GO-to-consumption equality chain, replay path and both mismatch
refusals are explicit. This is documentation inspection, not runtime proof.

**Clause map — part-2 installation**

| Clause | Installation site | Verification / counterfactual |
|---|---|---|
| Q1 | Contract §§1, 2, 3, 8.1, 9 | Inspected producer-issued id, six-key GO reference, absolute custody path, and separate digest/id refusal; omission would break replay identity. |
| Q2 | Contract §§1–4, 8.2, 9 | Inspected seven-key authorization record and four-key GO copy, exact plan/ordinal binding and consumption eligibility; an altered copy must refuse. |
| Q3 | Contract §§2, 4, 5, 8.3, 9 | Inspected exact nested keys, authority string, dual timestamp, relative evidence path and primitive encodings; extra keys or wrong types must refuse. |
| Dated ruling | D-176 final dated line | V1 checks documentation freshness and decision references; contract §8 owns the amended wire details. |

Next exact step: lead sends the completed wire contract to the Opus refuter,
then performs the contract landing gate before issuing code scope. Runtime
production/test cells remain NOT PINNED for their implementing seats. No code,
live qualification, commit, repository-wide suite or out-of-scope bookkeeping
was performed. The pre-existing untracked brief is preserved. There is no
configured upstream.

### Part-1 evidence retained (historical; superseded wire status)

The following records the committed part-1 installation, not work or tests
performed in part 2. Its pending-wire statements, 23-key inspection and old line
numbers describe that historical draft. The ruling above resolves both former
NEEDS_RULING flags; §8 is now ready for the assigned contract refutation.


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

### Part-1 verification notes (historical)

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

### Historical part-2 verification notes

Part-2 acceptance uses only the requested focused documentation suite. Its
combined stdout/stderr and process return code are logged below in this
allowlisted report, avoiding any additional repository log path. Bytecode
writing is disabled through PYTHONDONTWRITEBYTECODE for the captured run.
The prior interactive invocation produced progress output but its return code
was not retained; the captured run below is the authoritative acceptance.

```text
$ python3 -m unittest tests.test_docs_freshness
...............................
----------------------------------------------------------------------
Ran 31 tests in 0.900s

OK
rc=0
```
