```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "A292 can begin a harness for the sealed v4 roster, but row/window schema and the v5 cap policy need magistrate rulings before implementation.",
  "workspace": {
    "base_requested": "75d04e9e",
    "base_mode": "descendant",
    "head_start": "b2f6c563b9f87d75fed34dd02243c5f63bdcd127",
    "head_end": "b2f6c563b9f87d75fed34dd02243c5f63bdcd127",
    "upstream_end": "75d04e9ee7b6ee23df25fed0a30478a45f97090b",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "A292 harness, ruled v4 behavior",
        "action": "start_now",
        "wait_for": "",
        "collision_surface": "new reducer tests only"
      },
      {
        "row": "A292 reducer implementation",
        "action": "wait_for",
        "wait_for": "committed RED harness and magistrate rulings on OPEN schemas",
        "collision_surface": "joulewise/scored_reduce.py"
      },
      {
        "row": "AP-5M v5 claim adaptation",
        "action": "needs_ruling",
        "wait_for": "E2 adoption and A291 contract v5",
        "collision_surface": "cap semantics, cell key, retry and recapture rules"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD; git rev-parse origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "b2f6c563b9f87d75fed34dd02243c5f63bdcd127",
          "75d04e9ee7b6ee23df25fed0a30478a45f97090b"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "75d04e9ee7b6ee23df25fed0a30478a45f97090b"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_scored_packer tests.test_scored_roster_checker",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 65 tests in 13.601s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 65 tests.*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The rulings bind row/window identity and behavior but do not settle a complete A292 row/window JSON schema or all reducer refusal codes.",
      "needs": "Magistrate rules schemas and codes before the implementation brief."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The AP-5M v5 draft explicitly supersedes v4 capped-is-incorrect semantics and leaves the A291 v5 contract open.",
      "needs": "Keep v5 claim behavior out of this v4 implementation until adoption and contract amendment."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A291's reduce-column witnesses are explicitly PROVISIONAL; the 65 passing packer/checker tests do not close them at the real reducer entry.",
      "needs": "Re-run every R-column witness through A292 reduce."
    }
  ]
}
```

## Binding clauses

The following quotations are the operative reducer-facing text. Later amendments replace the earlier wording where indicated.

- **Kernel acceptance and status.** “Reduce only a sealed, replayable roster. Each score row carries scorer_id and both the registration and roster digests; each capture window carries both digests; any mismatch refuses; mismatch refuses. Key windows by (block_id, attempt) so voided and retried captures cannot collide. Derive a cap hit from generated_tokens at or above the registered token cap, require stop_reason, and refuse disagreement with cap flags. Every registered item is exactly one counted row or typed terminal refusal. Accept a terminal ceiling_violation window, record its gross_j on the refusal, and exclude it from cell sums by rule, not caller filtering. Pass terminal refusals through typed; consume every field listed as CARRIED to this reducer by gate 45.” `docs/process/state_kernel.json:3832`. “At the real reducer entry, re-run A291’s PROVISIONAL reduce-column witnesses and consume cap_bound_fraction as mandatory rows … The stopped c0998fdb draft is not accepted.” `docs/process/state_kernel.json:3861`.

- **Identity, constants, rows, windows.** “Identity fields (`schema`, `registration_id`, `plan_id`) are CONSUMED: their witness is that a roster sealed under the old digest is refused by every consumer under the new registration.” `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md:46`. “Constants: levels, merge_order, min_correct 3, holm_m 5, both spread minima 5, cap_bound_fraction 0.20, retry_stages” and “Module constants pinned by `schema`; one test asserts equality to the AP-5M text.” Same file `:52`. “Rows carry `scorer_id` and both digests; reducer refuses mismatch” and “Windows carry both digests too.” Same file `:59`.

- **Cap evidence.** “capped := generated_tokens ≥ Registration.cap_tokens[arm]; stop_reason required on every row; disagreement refuses.” The same refuter requires windows keyed by `(block_id, attempt)`, the executed roster as reducer input, exactly one row or terminal refusal per roster item, and exclusion of voided windows by rule. `docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/11-opus-contract-refuter.md:15`; the kernel installs these in its A292 acceptance. The later A291 ruling adds: “`cap_bound_fraction` → A292 (reducer, the M3 cap-bound label). Each is a module constant pinned by `schema` and asserted equal to the AP-5M value by one A291 test; each is a mandatory CONSUMED row in its consumer lane's gate.” `docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md:17`.

- **Terminal capture.** “A window for a terminal ceiling_violation attempt is accepted, recorded on the terminal refusal as `gross_j`, and never enters a cell sum.” `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md:79`. A completed single over its derived worst case also advances: “its completed attempt is listed in the roster's voided attempts and its window `(block_id, attempt)` is excluded by `reduce` by rule”; a terminal attempt follows the gross-J rule. `docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md:27`. The addendum makes the count predicate exact: “`reduce` counts a window only when its `(block_id, attempt)` is a live placement.” `docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/20-addendum/21-coldgate-fable-addendum-ruling.md:78`.

- **Replay and entry ordering.** “`_seal(registration, roster)` runs on the input at the entry of `requeue_overrun` and `reduce` and at every public exit of `pack` and `requeue_overrun`.” `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md:52`. “The roster carries an append-only `events` list, one entry per `requeue_overrun` call (block id, observations, resulting `sha256`). `reduce` asserts `registered_sha256 == pack(registration, predicted_decode_s)["sha256"]`, replays every event from the root, and refuses unless the final digest matches its input roster.” Same file `:54`. The later detailed replay amendment requires each event’s re-derived decisions, placements and digest to match, then field-for-field final equality. `docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/20-addendum/21-coldgate-fable-addendum-ruling.md:72`.

- **Real-entry gate.** “A291 ships `verify_executed_roster(registration, roster, predicted_decode_s)` = `_seal` on the input, the `registered_sha256` re-pack assertion, and event replay with per-event digest equality (Q20). A291's `reduce`-column witnesses run against it and are recorded PROVISIONAL. A292's `reduce` calls it as its first statement (AST-asserted); A292's gate re-runs every A291 `reduce`-column witness at the real entry as mandatory rows. A291 may not describe the `reduce` column as closed.” `docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md:47`.

- **Capture completeness.** “Every `loaded` envelope that has run is reported by one `requeue_overrun` call, in index order, including envelopes in which every block completed; `idle_slot` envelopes are never reported.” “`reduce` refuses (`unreported_envelope`) a roster with any `loaded` envelope whose `observations is None`.” `docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/20-addendum/21-coldgate-fable-addendum-ruling.md:82`.

- **Executed spread and drift.** “A cell is spread-exceeded when its executed roster holds fewer than five parent blocks whose every item has a counted window, or fewer than five distinct envelopes holding them”; the cell records `spread_exceeded: true`, reports its numbers, and its level remains unresolved until registered recapture. `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md:71`. The cause is amended to “for any reason after capture (terminal `ceiling_violation`, `unattributed_overrun`, or a rescheduled parent the seal cannot place).” `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md:58`. A parent’s executed position is the item-weighted mean of the envelope indices of its counted windows; voided attempts and idle slots contribute nothing. `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md:73`. “At `reduce` entry the executed lever is computed from counted windows …; if it exceeds `max_gap` the level carries `drift_exceeded: true`, its numbers are reported, and A293 reports it NR(`drift_exceeded`) until a registered recapture.” `docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md:39`. “`spread_exceeded` is decided once, at `reduce` entry, from the finished roster and the set of captured window keys.” Same file `:41`. With zero counted parents for a model at a level, the executed lever is `null`, drift is not set, and that cell is spread-exceeded. `docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/20-addendum/21-coldgate-fable-addendum-ruling.md:76`.

- **Typed status and precedence.** When both NE(`ceiling_violation`) and `spread_exceeded` apply, NE takes precedence and the spread flag is still recorded; without NE, spread gives NR(`spread_exceeded`). `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md:60`. A291 extends this to drift: “NE(`ceiling_violation`) > NR; a level with both `spread_exceeded` and `drift_exceeded` is NR with both reasons recorded.” `docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md:39`. `unattributed_overrun` is a terminal-refusal **type**, never a refusal code. `docs/process_traces/2026-09-24-activation-278ebc9e/89-a291-contract-v4-1-inv11-closed.md:417`.

- **Witness standard.** The gate requires every registration field and ruled constant either to be consumed by an executed boundary witness on every closed path or to appear in the closed CARRIED list; validation-only witnesses do not count. Every magistrate invariant row needs an executed violating witness on every path, and “Every CARRIED row is a mandatory CONSUMED row in its consumer lane's gate.” `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md:56`. “No invariant row/path cell may be `n/a`”; entry or exit injection supplies otherwise unavailable witnesses. `docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md:45`. The v4.1 contract lists the R-column witness form, including recorded values and root-only minima, at `docs/process_traces/2026-09-24-activation-278ebc9e/89-a291-contract-v4-1-inv11-closed.md:404-410`.

- **AP-5M v5 boundary.** The v5 file labels itself “PROPOSAL ONLY” and says it is not an adopted plan or permission to arm a night. `docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:3`. Its retry sentence retains monotone within-night retries, bounded single retries, terminal `ceiling_violation`, `unattributed_overrun` and `night_exhausted`, no dropped tail, spread, balance and bounded recapture, but states: “A291 contract v5 is OPEN” and “No v4 roster or `claims.py` verdict is grandfathered into v5.” Same file `:53`. Its scoring text separately supersedes v4 capped-is-incorrect: a forced thinking-cap hit can still be correct when a parseable answer appears within the answer allowance. Same file `:41`. These are draft obligations for the later v5 contract, not authority to change A292’s sealed v4 semantics.

## Merged packer interface consumed by A292

- `Registration` is an immutable canonical object; `.digest` is the registration SHA, `.cap` is `interior_s − guard_s`, `.max_gap` is derived, and `CAP_BOUND_FRACTION = 0.20`. `joulewise/scored_registration.py:25-28,59-95`.
- `pack(registration, predicted_decode_s) -> roster`; `requeue_overrun(registration, roster, envelope_index, observations) -> roster`; `verify_executed_roster(registration, roster, predicted_decode_s) -> None` or `PackingRefusal(code)`; `executed_status(registration, roster, predicted_decode_s, captured_window_keys) -> dict`. `joulewise/scored_packer.py:16-19,347,412,491-503`.
- Exact roster keys are `schema`, `registration_sha256`, `claim_ready`, `item_set_sha256`, `n_per_level`, `blocks`, `envelopes`, `placements`, `terminal_refusals`, `events`, `drift_lever_slots`, `planned_spread_shortfall`, `registered_sha256`, `sha256`. `joulewise/scored_packer.py:273-280`; contract types at `docs/process_traces/2026-09-24-activation-278ebc9e/89-a291-contract-v4-1-inv11-closed.md:178-197`.
- Block keys: `block_id model level items predicted_item_s predicted_s attempt retry_stage parent_block_id superseded late`. Envelope keys: `index model kind blocks voided_block_ids observations`. Placement keys: `block_id attempt stage reserved_s envelope_index`. Recorded observation keys: `block_id status elapsed_s decision`. Event keys: `envelope_index block_ids observations placements sha256`. Terminal-refusal keys: `type block_id attempt parent_block_id item_id model level`; types are `ceiling_violation` and `unattributed_overrun`. `joulewise/scored_packer.py:176-188`; contract detail at `docs/process_traces/2026-09-24-activation-278ebc9e/89-a291-contract-v4-1-inv11-closed.md:199-260`.
- The roster digest is SHA-256 of canonical JSON after removing top-level `sha256`, top-level `registered_sha256`, and each event’s `sha256`. The root has `registered_sha256 == sha256`; descendants preserve the root digest and carry event-result digests. `joulewise/scored_packer.py:30-40,273-309`; contract at `docs/process_traces/2026-09-24-activation-278ebc9e/89-a291-contract-v4-1-inv11-closed.md:262-267`.
- `verify_executed_roster` seals, repacks, replays all events, and rejects any unreported loaded envelope. `executed_status` accepts the reducer-supplied set of `(block_id, attempt)` captured-window keys and returns `spread_exceeded`, `executed_drift_lever_slots`, and `drift_exceeded`. `joulewise/scored_packer.py:471-503`.
- The independent checker is `tests/scored_roster_checker.py`; it has its own canonicalization and `check_roster`, `check_transition`, `check_executed`, and `check_registration` interfaces. Its `check_executed` returns the three executed-status fields on valid input or `{"violations": [...]}` on invalid input. `tests/scored_roster_checker.py:83-104,794-865`. It checks the roster, not A292 item rows or capture-window records.

## Proposed committed RED acceptance harness

Use one named test per clause below. “OPEN code” means assert a typed refusal now, then pin its code only after the magistrate rules it. The harness should run RED against the absent/new reducer before the implementation seat receives its scope.

| Test | Input and expected result |
|---|---|
| `test_reduce_calls_replay_verifier_first_ast` | Inspect reducer AST; first statement of `reduce` calls `verify_executed_roster` with unchanged registration, roster and predictions. |
| `test_reduce_replays_root_and_each_event` | Mutate root digest, intermediate event digest, event decision or placement while preserving superficial final shape; refusal `inv_39` or `inv_38` from the verifier. |
| `test_reduce_rejects_unreported_loaded_envelope` | Finished roster with one loaded `observations: null`; `unreported_envelope`. |
| `test_reduce_rejects_registration_roster_binding_mismatch` | Correct roster under a different registration, or mismatched `registration_sha256`; verifier refusal `inv_01`. |
| `test_reduce_rejects_row_identity_mismatch` | Change only `scorer_id`, registration digest or roster digest in a score row; typed refusal, code OPEN. |
| `test_reduce_rejects_window_identity_mismatch` | Change either digest in a capture window; typed refusal, code OPEN. |
| `test_reduce_keys_windows_by_block_and_attempt` | Valid voided attempt and later live retry sharing `block_id`; both windows accepted as distinct keys, only live attempt counted. Duplicate same key refused, code OPEN. |
| `test_reduce_derives_cap_from_generated_tokens` | Values immediately below and at `cap_tokens[arm]`; cap hit changes exactly at equality. Missing `stop_reason`, or cap flag/stop reason disagreement, refuses with OPEN code. |
| `test_reduce_consumes_cap_bound_fraction_boundary` | Fractions exactly `0.20` and just above; cap-bound label changes only above threshold for the ruled v4 M3 label. Changing the module constant must change the witness. |
| `test_reduce_requires_exact_item_partition` | Omit or duplicate a registered item, or supply both row and terminal refusal; typed refusal, code OPEN. Valid roster yields exactly one counted row or typed terminal per `(model,item)`. |
| `test_reduce_preserves_typed_terminals` | `ceiling_violation` and `unattributed_overrun` entries emerge typed and associated with their item and attempt; neither is silently dropped. |
| `test_reduce_records_terminal_window_without_summing` | Supply a terminal `ceiling_violation` window with `gross_j`; output refusal record contains that J, cell sum excludes it. |
| `test_reduce_excludes_completed_culprit_single_window` | Supply the voided completed single window and its later live window; only live key enters sums and counted-parent position. |
| `test_reduce_computes_executed_spread_once` | Four fully counted parents or four distinct holding envelopes after capture; numbers reported and `spread_exceeded: true`. Five of each clears it. |
| `test_reduce_computes_executed_parent_drift` | Alter counted window envelope positions across `max_gap`; `drift_exceeded` follows executed positions, excluding voided attempts and idle slots. Zero counted parents yields null lever and spread flag. |
| `test_reduce_reruns_every_provisional_R_witness` | Parameterize every R-column invariant row in contract v4.1, including entry injections and recorded-value witnesses; run through real `reduce`, not only `verify_executed_roster`. Compare executed values with independent `check_executed`. |
| `test_reduce_refusal_precedence_and_flags` | Terminal ceiling violation plus spread/drift shortfall records all applicable flags; A292 passes typed evidence for A293’s NE-over-NR decision. Exact A292 output shape remains OPEN. |

## OPEN items for the magistrate

1. **A292 input/output schema and refusal vocabulary.** The stopped reducer used `ROW_KEYS` and `WINDOW_KEYS`, but those omit the now-required `scorer_id` and both digests; its output shape and plain-string refusals were never accepted. `c0998fdb:joulewise/scored_reduce.py:11-19,33-40`. Rule exact row/window keys, types, output fields, and codes before freezing the RED harness.
2. **Window completeness and terminal variants.** The rulings say every registered item is one counted row or typed terminal, and require terminal ceiling-violation gross J when its window exists. They do not fully settle whether every voided or `unattributed_overrun` attempt must have a window, nor which missing-window cases refuse. Do not inherit the draft’s “all active windows required” rule without a ruling.
3. **Cap policy across v4 and proposed v5.** The sealed v4 rule derives capped from `generated_tokens ≥ cap_tokens[arm]`; the v5 draft distinguishes thinking-cap hits from answer-allowance hits and supersedes “capped is incorrect.” `docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:41`. The v5 contract, cell key `(model, level, budget)`, and `night_exhausted` transitions remain OPEN at `:53`. A292 should not silently choose a hybrid.
4. **Executed-status shape is implemented but flagged as proposed by contract v4.1.** The contract says its exact return shape is proposed, not ruled, and notes tension between per-level and per-cell spread wording. `docs/process_traces/2026-09-24-activation-278ebc9e/89-a291-contract-v4-1-inv11-closed.md:393-398,788`. The magistrate should affirm how A292 presents it.
5. **Checker INV-12 mismatch.** R4b records a checker clause stricter than contract INV-12 on a single’s `predicted_item_s`; it expressly requests later reconciliation and forbids resting a claim on checker INV-12 agreement until ruled. `docs/process_traces/2026-09-24-activation-278ebc9e/82-coldgate-packet-a291-r3method/30-addendum/21-coldgate-fable-r4-addendum-ruling.md:63`.
6. **Stopped draft reuse.** `c0998fdb` performed gross block reduction, cap counting, attempt-keyed windows, typed ceiling terminals and cell summaries (`c0998fdb:joulewise/scored_reduce.py:33-171`). It was stopped after four class-IV defects: ignored item-set binding, caller-supplied prediction guard, skipped retry-envelope M8 guard, and configurable minima of one. `docs/process_traces/2026-09-23-activation-d8cc9c0a/37-a281a-stop-and-consult-brief.md:5-11`. Its code also calls the obsolete `_verify_roster` and assumes obsolete block fields (`arm`, `origin_attempt`, `ceiling_violation`, stored `drift_exceeded`). It is usable as an **untrusted test-case source**, not as an implementation base.

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Rule exact A292 schemas/codes | needs_ruling | magistrate | Harness assertions |
| Commit ruled-behavior RED harness | start_now | schema-dependent cases may remain pending | `tests/test_scored_reduce.py` |
| Implement A292 to GREEN | wait_for | committed RED harness and schema ruling | `joulewise/scored_reduce.py` |
| AP-5M v5 adaptation | needs_ruling | E2 adoption and A291 v5 contract | Cap and retry semantics |

## Critical path

Magistrate settles A292 schemas and codes → harness seat commits executable RED acceptance tests → implementation seat receives that exact test commit and makes it GREEN → real-entry R-column re-run and claim-bearing review gate. AP-5M v5 adoption and contract amendment are a separate prerequisite for any v5 claim path.

## Delegation contracts

- **Harness seat proposed `WRITE_SCOPE`:** `["tests/test_scored_reduce.py"]`. It owns fixtures and executable A292 acceptance tests there, commits the RED state, and records every provisional R-column witness against the real reducer entry. If an independent reducer oracle is ruled necessary, the magistrate should add its exact path prospectively.
- **Implementation seat proposed `WRITE_SCOPE`:** `["joulewise/scored_reduce.py"]`. It starts from the committed harness head and may not edit the harness, packer, checker, registration, kernel or AP-5M text. Any required change to those files returns as `NEEDS_SCOPE` or `NEEDS_RULING`.

No files were modified.