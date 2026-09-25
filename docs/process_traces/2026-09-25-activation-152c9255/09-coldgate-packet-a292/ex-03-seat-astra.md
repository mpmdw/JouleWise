```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend a versioned v4 reducer with explicit completeness rules, preserved executed-status evidence, and an independent reducer oracle committed before implementation.",
  "workspace": {
    "base_requested": "23289fc5",
    "base_mode": "exact",
    "head_start": "23289fc5ef71664d6a59161d79be4720d6e53b6f",
    "head_end": "23289fc5ef71664d6a59161d79be4720d6e53b6f",
    "upstream_end": "75d04e9ee7b6ee23df25fed0a30478a45f97090b",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "D1",
        "severity": "blocker",
        "text": "Freeze the reducer schemas, completeness policy and v4 semantics before freezing the RED harness; proposed exact rules are in R1-R3."
      },
      {
        "id": "D2",
        "severity": "should_fix",
        "text": "Executed presentation must distinguish cell spread from level drift, retain partial-parent positions, and record unattributed_overrun even when spread passes."
      },
      {
        "id": "D3",
        "severity": "should_fix",
        "text": "Require an independent reducer oracle and real-entry witnesses without treating the unresolved checker INV-12 clause as authority."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_scored_packer tests.test_scored_roster_checker",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 65 tests in 13.863s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 65 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)\\s*$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git merge-base --is-ancestor 75d04e9e HEAD",
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
      "text": "R1-R7 are proposed design dispositions, not installed authority.",
      "needs": "Magistrate synthesis and the requested cold ruling must install the contract before harness freeze."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Verification covers the existing packer/checker only; no reducer implementation or reducer acceptance harness was written or executed.",
      "needs": ""
    }
  ]
}
```

## Findings

**D1 — BLOCKER:** settle the wire contract and missing-evidence behavior before the schema-dependent RED tests are committed.

**D2 — MATERIAL:** preserve the distinctions between complete parents, positioned parents, cell spread, level drift, and terminal causes.

**D3 — MATERIAL:** independent arithmetic and ownership checks are needed beyond the existing roster checker.

All prescriptions below are **proposed ruling text**. Existing authority is cited separately. No files were modified.

### R1 — Schemas and refusal vocabulary

**BLOCKER; D1.** The binding requirements establish scorer/digest identity and an exact item partition, but do not specify a complete reducer wire schema. The merged roster already provides ownership, attempts and terminal types; the reducer should derive these relationships rather than accept additional caller authority. Sources: `docs/process/state_kernel.json:3832`; `joulewise/scored_packer.py:176`; `joulewise/scored_packer.py:90`.

Use `ReductionRefusal(PackingRefusal)` with the inherited `.code` interface. Propagate verifier exceptions unchanged. Give new reducer conditions descriptive `reduce_*` codes; assigning additional `inv_*` numbers would imply an invariant inventory that has not been ruled. The existing idiom is at `joulewise/scored_packer.py:16`; contract code conventions and the distinction between terminal types and raised codes are at `docs/process_traces/2026-09-24-activation-278ebc9e/89-a291-contract-v4-1-inv11-closed.md:412`.

Keep energy at block-window granularity. A block containing several items contributes its gross J **once**. Counted item records identify their block; they do not contain invented per-item joules.

**Exact executable contract text:**

```text
API:
reduce(registration, roster, predicted_decode_s, item_rows, block_windows)

Its first Python statement MUST be:
verify_executed_roster(registration, roster, predicted_decode_s)
No decorator, coercion, lookup, defaulting or validation may precede that call.
The function is pure and does not mutate any argument.

Wire conventions:
Objects have exactly the listed keys. Arrays are Python lists.
S = nonempty string.
H = lowercase 64-character hexadecimal string.
I = nonnegative integer, with type(value) is int; bool is excluded.
L = integer in {1,2,3,4,5}; bool and float are excluded.
N = finite nonnegative JSON number; bool is excluded.
B = bool.
? means nullable, never an omitted key.
No aliases, unknown keys, silent coercions or defaults.

ScoreRow:
schema: literal "joulewise.scored_row.v1"
scorer_id: S
registration_sha256: H
roster_sha256: H
item_id: S
model_id: S
arm: S
level: L
block_id: S
attempt: I
retry_stage: "initial" | "whole_block" | "single_problem" | "single_retry"
parent_block_id: S?
prompt_tokens: I
generated_tokens: I
outcome: "correct" | "incorrect" | "malformed" | "truncated"
stop_reason: "stop" | "length"
truncated: B

Score rows describe only final counted attempts.
Match model, item, level, block, placement attempt, placement stage and parent
against the verified roster; match arm and scorer_id against registration.
Historical score records are outside this input interface.
Reject a score row for a terminal item or non-live attempt.

CaptureWindow:
schema: literal "joulewise.scored_window.v1"
registration_sha256: H
roster_sha256: H
block_id: S
attempt: I
gross_j: N

Both row/window digests must equal registration.digest and FINAL roster.sha256.
registered_sha256 is not an alternative accepted roster digest.
Windows are a list so duplicate (block_id, attempt) records remain detectable.

Reduction:
schema: literal "joulewise.scored_reduction.v1"
cap_policy: literal "ap5m.v4"
registration_sha256: H
roster_sha256: H
registered_sha256: H
mode: "pilot" | "registered"
roster_claim_ready: B
counted_rows: list[CountedRow]
terminal_refusals: list[Terminal]
attempts: list[Attempt]
cells: list[Cell]
levels: list[Level]

CountedRow = exact ScoreRow fields plus:
capped: B
correct: B

Terminal = exact verified roster terminal fields:
type: "ceiling_violation" | "unattributed_overrun"
block_id: S
attempt: I
parent_block_id: S?
item_id: S
model: S
level: L
plus:
gross_j: N?
For ceiling_violation, gross_j is its required window's energy.
For unattributed_overrun, gross_j is null; any supplied block energy is retained
once in Attempt, since a terminal parent can contain several refused items.

Attempt, exactly one per roster placement:
block_id: S
attempt: I
envelope_index: I
model_id: S
level: L
parent_block_id: S?
item_ids: list[S]
observation_status: "completed" | "cut_off" | "not_started"
disposition: "counted" | "voided" | "ceiling_violation" | "unattributed_overrun"
window_present: B
gross_j: N?
Derive disposition from live ownership and terminal records, not caller flags.
window_present iff the matching window exists; absent energy is null, never 0.

Cell, exactly ten records:
model_id: S
arm: S
level: L
n_registered: I
n_counted: I
n_terminal: I
correct: I
prompt_tokens: I
generated_tokens: I
gross_j: N
accuracy: N?
cap_hits: I
cap_hit_fraction: N?
cap_bound: B
cap_bound_label: null | "cap-bound"
counted_parent_count: I
counted_envelope_count: I
spread_exceeded: B

Level, exactly five records:
level: L
executed_drift_lever_slots: N?
max_gap: N?
drift_exceeded: B
spread_exceeded: B
evidence_status: "clear" | "NR" | "NE"
reasons: list["ceiling_violation" | "unattributed_overrun" |
              "spread_exceeded" | "drift_exceeded"]

Per cell:
n_counted + n_terminal == n_registered.
correct, token totals and cap_hits use counted_rows only.
gross_j = math.fsum(gross_j of counted attempts in placement order).
accuracy = correct / n_counted, or null when n_counted == 0.
R3 defines cap fields; R4 defines spread, drift and status.
Emit empty/all-terminal cells too. No estimator verdict is implied by "clear"
or roster_claim_ready. All output numbers must remain finite.

Ordering:
counted_rows and terminals: level, role order (8B then 1.7B), registered item order.
attempts: roster placement order.
cells: level then role order.
levels: ascending.
Reasons: the declaration order above.
Do not parse model identity by splitting block IDs or cell-key strings.

New refusal codes:
reduce_schema                 wrong containers, exact keys or schema literals
reduce_domain                 invalid scalar type/domain
reduce_binding                validly formed but mismatched scorer/digests
reduce_score_ownership        row identity disagrees with its live placement
reduce_item_partition         missing/duplicate item, or row-terminal overlap
reduce_duplicate_window       repeated (block_id, attempt)
reduce_window_ownership       unknown placement or window for not_started
reduce_missing_live_window    missing required counted window
reduce_missing_terminal_window missing required ceiling_violation window
reduce_cap_evidence           cap flag/stop reason/outcome disagreement
reduce_numeric                nonfinite arithmetic result or numeric overflow

Validation order after the verifier:
shape/domain; bindings; duplicate keys; ownership; cap consistency;
exact item partition; window completeness; aggregation.
Within a phase use input list order.
PackingRefusal codes from verification remain unchanged.
Terminal types are records, never exception codes.
```

### R2 — Window completeness

**BLOCKER; D1.** Require live windows because a successful result must assign every nonterminal registered item to a counted row backed by a counted window. A missing capture does not authorize the reducer to invent a new roster terminal. That follows the kernel partition requirement and the live-placement counting rule: `docs/process/state_kernel.json:3832`; `docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/20-addendum/21-coldgate-fable-addendum-ruling.md:78`.

Require ceiling-terminal windows as a **new completeness ruling**, stronger than the existing conditional “a window … is accepted” language. The reason is to ensure every such refusal carries the measured energy of the falsified bound. Existing authority establishes acceptance, recording and exclusion, but not mandatory presence: `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md:79`.

Other voided windows cannot affect counted arithmetic. Make them optional but expose their absence. In particular, `unattributed_overrun` includes `not_started`, so blanket requirements would demand fabricated evidence; the actual transitions are at `joulewise/scored_packer.py:430`.

This is not full-night energy accounting: optional discarded captures mean the audit ledger can be incomplete. It is complete accounting of the accepted claim windows.

**Exact executable contract text:**

```text
Construct placement keys from roster.placements, not a numeric attempt range.
Join each placement to its envelope observation by block_id.

Classify with precedence:
live placement -> counted;
terminal-key ceiling_violation -> ceiling_violation;
terminal-key unattributed_overrun -> unattributed_overrun;
otherwise -> voided.

Required windows:
- Every live placement: required; absence raises reduce_missing_live_window.
- Every terminal ceiling_violation placement: required; absence raises
  reduce_missing_terminal_window.
- Other voided placements: optional.
- Terminal unattributed_overrun with cut_off: optional.
- Any not_started placement, terminal or otherwise: window forbidden;
  presence raises reduce_window_ownership.

A window for any unknown placement is refused.
A supplied optional window receives the same schema, binding, numeric and
uniqueness checks as a required window.
Count only live placement keys. Every other supplied window remains in the
attempt ledger and contributes zero to every cell sum.
Missing optional windows remain window_present=false, gross_j=null.
A missing required window raises; it never silently reduces the denominator,
becomes zero energy, or creates an invented terminal refusal.

Acceptance examples:
live missing                         -> reduce_missing_live_window
ceiling terminal missing             -> reduce_missing_terminal_window
completed voided missing             -> success, audit absence
cut_off unattributed missing          -> success, typed terminal and audit absence
not_started unattributed missing      -> success, typed terminal
not_started unattributed with window  -> reduce_window_ownership
voided attempt 0 + live attempt 1     -> accept both; sum attempt 1 only
```

### R3 — Cap policy

**BLOCKER; D1.** Implement v4 now, without runtime policy switches. The kernel explicitly binds token-derived caps. The v5 proposal changes correctness, measurement sampling and the cell design, so a configurable cap predicate would conceal a much larger contract change. Sources: `docs/process/state_kernel.json:3832`; `docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:41`; the same file `:53` and `:57`.

The current mandatory reducer constant is `CAP_BOUND_FRACTION`, not the estimator’s merge or multiplicity constants: `docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md:17`. Its value is `0.20` at `joulewise/scored_registration.py:25`. I propose retaining the strict `>` label boundary visible in the stopped draft, explicitly adopting it rather than treating that draft as authority (`c0998fdb:joulewise/scored_reduce.py:168`).

**Exact executable contract text:**

```text
Reduction schema v1 implements only cap_policy="ap5m.v4".
It accepts the current registration/roster schemas through the existing verifier.
It has no caller-supplied cap-policy or cap-bound-threshold parameter.

For every accepted score row:
capped = generated_tokens >= registration.cap_tokens[registration.arm]
require truncated == capped
require (stop_reason == "length") == capped
require outcome != "truncated" or capped
require not (capped and outcome == "correct")
Any failure raises reduce_cap_evidence.
correct = outcome == "correct"
A capped incorrect or malformed row is permitted and remains incorrect.
Here truncated means the token-cap flag, not a wall-clock capture cutoff.

For each cell:
cap_hit_fraction = cap_hits / n_counted if n_counted else null
cap_bound = cap_hit_fraction > CAP_BOUND_FRACTION if n_counted else false
cap_bound_label = "cap-bound" if cap_bound else null

Boundary witnesses:
generated_tokens=cap-1, stop, truncated=false -> uncapped
generated_tokens=cap, length, truncated=true  -> capped
generated_tokens>cap, length, truncated=true -> capped
one cap hit among five counted rows          -> fraction .20, not cap-bound
two cap hits among five counted rows         -> fraction .40, cap-bound
patch CAP_BOUND_FRACTION across .40          -> label changes

V5 requires a separately adopted registration/roster/reducer contract and new
wire versions. Do not add budget, answer_allowance or night_exhausted to v1.
```

### R4 — Executed-status presentation

**MATERIAL; D2.** Affirm cell-level spread and level-level drift. The proposed existing helper shape is useful internally, but A292 should also report the counts that explain a spread flag. The ambiguity is expressly recorded at `docs/process_traces/2026-09-24-activation-278ebc9e/89-a291-contract-v4-1-inv11-closed.md:393` and `:788`.

Distinguish **fully counted parents** from **parents with a position**. The implementation includes partially counted parents in position means while requiring at least one fully counted parent in each model before producing a lever. That matches the contract’s literal combination and should be affirmed explicitly, including its null discontinuity. Sources: `joulewise/scored_packer.py:137`; `tests/scored_roster_checker.py:273`; `tests/test_scored_packer.py:318`.

The scout’s summary must include the independent `unattributed_overrun` NR reason: spread can pass while that terminal still makes the level unresolved. This is already ruled, not a proposed addition: `docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/20-addendum/21-coldgate-fable-addendum-ruling.md:66`.

Preserve envelope indices for downstream use, but do not implement a difficulty-axis covariate model here. The later gate expressly leaves the proposed R6-1 process rule unratified: `docs/process_traces/2026-09-24-activation-278ebc9e/117-coldgate-packet-a291-finalpass/20-coldgate-fable-finalpass-ruling.md:63`.

**Exact executable contract text:**

```text
After verification and row/window admission, construct the accepted live-window
key set once and evaluate executed status once. Never use stored planned values
as executed values.

For each parent:
counted items = items backed by accepted live windows.
fully counted = every registered item of that parent is counted.
position = arithmetic mean of counted items' envelope indices, if any;
           otherwise absent.
A block window contributes its envelope index once per item it contains.

For each cell:
counted_parent_count = number of fully counted parents.
counted_envelope_count = distinct envelopes holding those fully counted parents'
                        counted windows.
spread_exceeded = counted_parent_count < 5 or counted_envelope_count < 5.

For each model/level:
position_mean = arithmetic mean of all available parent positions, including
                partially counted parents; each parent has equal outer weight.
For each level:
lever = null if either model has zero fully counted parents;
        otherwise abs(position_mean_8B - position_mean_1.7B).
drift_exceeded = lever is not null and max_gap is not null and lever > max_gap.
Equality to max_gap does not exceed it.
Pilot max_gap=null produces drift_exceeded=false.

Level spread_exceeded = OR of its two cell spread flags.
Reasons accumulate:
ceiling_violation if any cell has that terminal;
unattributed_overrun if any cell has that terminal;
spread_exceeded if either cell has spread_exceeded;
drift_exceeded if the executed lever exceeds max_gap.
evidence_status = NE if ceiling_violation is present;
                  NR if any other reason is present;
                  clear otherwise.
NE does not erase NR reasons or numerical records.
"clear" is only the reducer evidence screen, not an A293 claim verdict.

Mandatory witnesses:
four versus five fully counted parents;
four versus five distinct holding envelopes;
partial-parent contribution to the position mean;
zero complete parents despite nonempty partial positions -> null lever;
lever equal to versus above max_gap;
unattributed_overrun with at least five complete parents -> NR;
ceiling plus spread plus drift -> NE with all three reasons retained.
```

### R5 — INV-12

**MATERIAL; D3.** A292 need not wait for reconciliation, provided it does not claim to settle it. The cold ruling forbids resting a claim on checker-INV-12 agreement and offers two possible future resolutions: `docs/process_traces/2026-09-24-activation-278ebc9e/82-coldgate-packet-a291-r3method/30-addendum/21-coldgate-fable-r4-addendum-ruling.md:63`.

Reduction uses live ownership, observations and captures; it does not need a single’s `predicted_item_s` to allocate energy. Keep mandatory replay unchanged. Replay reconstructs singles with the producer’s current value and checks final equality, so neutrality does **not** mean accepting arbitrary tampering of that field. Sources: `joulewise/scored_packer.py:453`; `joulewise/scored_packer.py:471`.

The harness should use ordinary producer-generated singles, which satisfy either possible reconciliation. A separate reducer oracle should independently compute reducer quantities rather than make the unresolved roster predicate its acceptance authority.

**Exact executable contract text:**

```text
A292 does not depend on A291-INV12-RECONCILE-01 for implementation start.

Do not modify the packer, registration, roster checker or INV-12 contract.
Do not introduce a reducer predicate requiring prediction equality for singles.
Do not weaken or bypass verify_executed_roster.

Positive reducer fixtures use actual replayable producer transitions.
Test settled INV-12 parent identity and partition clauses separately.
Do not assert that changing a single's predicted_item_s must produce inv_12.
If mandatory replay rejects such a candidate, record its actual replay code;
do not describe that result as settlement of the disputed INV-12 clause.

Do not filter INV-12 out of arbitrary checker failures to declare validity.
Unexpected checker disagreement is adjudicated, not masked.
The reducer oracle owns its arithmetic and status calculations independently;
roster-checker agreement is supplemental evidence with the INV-12 exclusion
explicitly recorded.
```

### R6 — The stopped draft `c0998fdb`

**MATERIAL; D1.** Use it as an untrusted test-case source only. Its entry calls obsolete `_verify_roster`; row/window schemas lack the required bindings; window matching depends on removed fields; and it copies obsolete drift fields. These are architectural mismatches, not a small compatibility patch: `c0998fdb:joulewise/scored_reduce.py:8`, `:16`, `:71`, `:124`.

Its use of attempt-keyed windows and once-per-block energy remains a useful source of examples, but each example needs fresh expectations. The kernel explicitly says the draft is not accepted: `docs/process/state_kernel.json:3861`.

**Exact executable contract text:**

```text
Do not copy the stopped reducer as the implementation base.
Write the new entry, validation, ownership join and output construction from
the installed A292 contract.

Extract candidate regressions for:
duplicate attempt keys; missing rows; cap equality; capped correct;
terminal energy; all-terminal cells; zero generated tokens; zero correct;
whole-block retries and split parents.
For every adopted case, attach its current ruling clause and independently
computed expected result. A stopped-draft output is never the oracle.

Discard draft expectations requiring obsolete roster fields, plain-string
refusals, terminal-window filtering, or stored executed drift.
```

### R7 — Delegation

**MATERIAL; D3.** Require an independent reducer oracle. The existing checker checks roster validity and executed status, not score bindings, row completeness, cap evidence or energy sums; its public scope is visible at `tests/scored_roster_checker.py:841`. A test harness that merely compares output against production `executed_status` would leave those new responsibilities largely self-checked.

Give the harness seat both the tests and oracle, committed before implementation. The implementation seat must not read the oracle or harness source; it can run the named tests and receive failures. This is a proposed A292 independence rule, consistent with the earlier different-seat checker requirement at `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md:56`.

Mandatory real-entry R witnesses remain a separate gate obligation. Helper agreement does not close that column: `docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md:47`.

There is one necessary reconciliation with R2: existing helper tests can intentionally omit a live capture and still compute spread (`tests/test_scored_packer.py:335`). At the proposed strict reducer entry, that input must fail completeness. Its failure must not be misreported as an executed-spread witness; add a valid partly terminal roster to exercise the recorded spread/position behavior.

**Exact executable contract text:**

```text
Harness seat WRITE_SCOPE:
["tests/test_scored_reduce.py", "tests/scored_reducer_checker.py"]

Implementation seat WRITE_SCOPE:
["joulewise/scored_reduce.py"]

The magistrate supplies the installed R1-R7 contract and an immutable harness
commit. The implementation seat cannot edit or read the two harness files;
it may run tests.test_scored_reduce and inspect its failure output.
The lead performs final verification and owns reports, kernel and contract edits.

Oracle API:
check_reduction(registration_mapping, roster, predicted_decode_s,
                item_rows, block_windows, candidate_output)
    -> list[Violation]

Violation has exactly inv_id, code, detail, all strings.
The oracle imports no production module and does not call production reduce,
executed_status, ownership helpers or aggregation helpers.
It independently reconstructs per-item ownership, attempt classification,
counted energy, cap aggregates, spread counts, parent positions and level reasons.
Harness tests pin input-refusal codes and test the oracle against deliberately
wrong outputs. No production output supplies an expected value.

Before implementation starts:
- Commit a RED harness with individual missing-feature failures, not only a
  module-import failure.
- Commit the oracle and hand-calculated positive/negative oracle checks.
- Enumerate every provisional A291 R witness and its real-entry A292 test.
- Include AST-first-verifier, stale root, altered intermediate event, altered
  decision/placement, unreported envelope, and malformed-input witnesses.
- For helper cases lacking required live windows, assert the new completeness
  refusal AND add a valid terminal-degradation fixture for recorded-value
  coverage. A refusal does not close that recorded-value row.
- Include scorer_id and CAP_BOUND_FRACTION consumption witnesses.
- Exercise drop-key, unknown-key, bool-as-int, NaN/infinity, duplicate-key,
  missing-window and summed-once boundaries.
- Kill representative mutants: bypass verifier; ignore digest/scorer; count a
  voided/terminal window; sum block J per item; change >= to > at token cap;
  change > to >= at cap-bound/drift; discard partial-parent positions;
  omit unattributed_overrun from reasons.

Implementation gate:
python3 -B -m unittest tests.test_scored_reduce tests.test_scored_packer tests.test_scored_roster_checker

Any required edit outside the assigned allowlist returns NEEDS_SCOPE.
No expectation changes by the implementation seat.
No claim that A291's R column is closed until the lead checks its complete
real-entry witness ledger and adjudicates any changed witness form.
```

## What would show this design wrong

- A ruled or required runner interface already binds rows/windows to capture-time roster digests rather than the final digest. R1 would then need an explicit immutable binding-manifest design; rewriting raw capture evidence would be unacceptable.
- A demonstrated requirement to produce partial reducer results when a live capture is missing. R2 deliberately refuses that input; supporting it would require ruled reducer-created terminal types and denominator/status semantics.
- A legitimate ceiling-terminal attempt for which no block window can exist. That would refute mandatory terminal-window presence and require an explicit missing-energy state.
- A cold ruling that excludes partly counted parents from drift means, or defines zero-parent nullability differently. R4 intentionally adopts the current literal combination.
- An independently calculated example where the oracle and reducer agree but duplicate block energy, resolve an unattributed terminal, or hide missing evidence. That would invalidate the proposed gate’s sufficiency.

## Expected disagreement

Other seats may require every started attempt’s window for full energy custody; I keep discarded captures optional and visibly absent.  
Some may allow partial successful reductions; I require complete live evidence and preserve only roster-authorized terminals.  
I expect disagreement over retaining partial-parent positions and the zero-complete-parent null rule.  
I favor explicit v4 delivery over waiting for v5 or adding policy switches.

## Residual risk

Only the existing 65 packer/checker tests were executed. No proposed reducer behavior, oracle, runner binding workflow or live capture was validated. The next exact step is to install the cold ruling, then commission the scoped RED harness and independent oracle.