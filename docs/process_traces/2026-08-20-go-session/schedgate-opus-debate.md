# Opus seat — debate response (one round, bounded)

All terra citations re-verified by me at the ruled head `5bd7acf` in
`wtRC-OPUS`. Terra read via `git show 5bd7acf:` from an ancestor checkout
(its FL1); **every line range it cites lands and its contents match** — I press
no custody point against terra's cites. Only its *test execution* failed (V3,
no writable tmpdir), which it flags honestly at FL2.

---

## 0. HEADLINE CONCESSION — terra is right about the fuse, and my G1 predicate was wrong

Terra: "r3 expressly says `arm_to_consume_budget_ns` is the minimum remaining
T-0 evidence life at arm, not the measured arm→consume gap… It does not treat a
capture's projected multi-hour span as the fuse projection."

Executed at `custody-staging/MAGISTRATE-RULING.md:95-105`, verbatim:

> **V5** arm_policy: `capability_horizon_ns` = `arm_to_consume_budget_ns` =
> `300_000_000_000` (behaviour-neutral vs the `:6101` default; equality is the
> no-silent-truncation invariant). BOTH rehearsal conditions bind, one per
> parameter (Opus's trace, ratified): T-0→arm ≤ 15 min gates
> `arm_to_consume_budget_ns` (via `validate_r1_temporal_budget:3299-3341`);
> p99 arm→consume ≤ 4 min (1 min margin) gates `capability_horizon_ns` (via
> `:7910-7914`). **RECORDED WARNING: the name `arm_to_consume_budget_ns` does
> NOT measure the arm→consume gap — it is the minimum remaining T-0 evidence
> life required at arm. Both seats independently misread it; in production that
> misreading is a lost window.**

The `:6101` default verifies: `generate_arm_receipt(..., validity_ns: int =
300_000_000_000)` at `joulewise/arm_readiness.py:6095-6100`.

**My G1 predicate — `min(deadlines) − now ≥ projected_span_ns +
arm_to_consume_budget_ns` — is struck.** It committed exactly the misreading the
ruling names, treating a ratified *absolute floor* as a *margin* to be added to a
multi-hour capture span. Two consequences, both disqualifying:

1. It invents a threshold. The ruled quantity is 300 s of remaining T-0 evidence
   life at arm; `span + 300 s` is a different, unruled number.
2. It is structurally unsatisfiable. A multi-hour span against a 20-minute
   volatile evidence horizon (`arm_readiness_evidence_t0.py:49`) refuses every
   window. "In production that misreading is a lost window" — the ruling
   predicted this failure and I walked into it.

**`--projected-span-ns` and `scheduler_span_undeclared` are withdrawn entirely.**
Corrected G1: `min(TIME_BOUND deadlines) − now ≥ arm_to_consume_budget_ns`.

I note for the record that the coordinator's brief carried the same misreading
("remaining evidence fuse < projected window span + margin"). Terra's seat caught
it; mine did not. That is the round's decisive exchange and it belongs at the top
of the ruling list.

---

## 1. Point-by-point adjudication

### 1.1 Fuse semantics — **CONCEDED** (above)

### 1.2 "A minimum-fuse check already exists" — **CONCEDED with a material addition**

Terra F1 locates it: `validate_r1_temporal_budget()` "is called during arm
issuance, not campaign scheduling (`arm_readiness.py:3299-3340`, `:6151-6159`)."
Verified at `:6151-6159`:

```python
    if lifecycle_registry is not None:
        try:
            validate_r1_temporal_budget(
                evidence_receipts.values(), lifecycle_registry,
                now_monotonic_ns=evaluated_at_monotonic_ns,
            )
        except EvidenceLifecycleError as exc:
            evidence_refusals.append(exc.refusal())
```

My §0(a) refuted the cold refuter's *specific* claim (a check in
`scripts/run_campaign.py`) and stopped there; terra went on to find where the
check actually lives. Concede the location.

**Addition terra missed:** the call is guarded by `if lifecycle_registry is not
None:` (`:6151`), and `lifecycle_registry` is the R1 registry, **dormant at
`_v3`** — VERDICT-PACKET §2(c) V-1: "Registry install at the `_v4` boundary (v2
registry + `freeze_evidence_lifecycle`) — dormant R1 today". So the check exists
and is **inert on today's family**. Both statements are needed: the scheduler
must not re-implement it (terra's point), and must not assume it fires
(mine). G1's scheduler role therefore narrows to: *prove the registry is
installed and the parameter resolved, invoke the existing check, and refuse if
it is dormant* — the exact shape terra's test pin already asks for ("prove the
scheduler invokes the existing arm check too").

### 1.3 Refusal vocabulary — **CONCEDED to terra's anchors, positions converge**

We independently reached the same rule (own closed frozenset, ruled in the D-144
round, never emitted ad hoc). Terra's anchors are strictly better than mine:

| | mine | terra | adjudication |
|---|---|---|---|
| refusal record shape | — | `REFUSAL_KEYS = {"type","code","row_id","evidence_id"}` `:338` | terra, verified |
| write-side closure | `_receipt_refusal:3623-3635` | `ArmReadinessError.__init__` `:941-951` + `.refusal()` `:953-960` | both; terra's is the general path |
| **read-side closure** | *missed* | `_validate_refusal:1434-1448` — refuses unclosed `code` **and** `type`/`code` disagreement | **terra**; this is what makes the vocabulary closed on *read*, which is the property that matters for a receipt someone else authored |
| min-fuse code | invented `scheduler_fuse_insufficient` | **registry's `TEMPORAL_BUDGET` role code/type** | **terra** |

Terra's last row is a real improvement: `R1_REFUSAL_ROLES` at `:488-499` contains
`TEMPORAL_BUDGET`, and the registry supplies its `code`/`type` via
`refusal_vocabulary` (`_R1_REFUSAL_ENTRY_KEYS = {"role","code","type"}`, `:504`;
placeholder rows `:546-553`). The min-fuse refusal code should be **read from the
installed registry, not invented by either of us**. My `scheduler_fuse_*` codes
are withdrawn in favour of the governed role. This sharpens the ED_RESERVED
blocker: at `5bd7acf` not only is the *value* reserved
(`"ED_RESERVED:arm-to-consume-budget-ns"`, `:534-535`) — the *refusal code* is
too (`"ED_RESERVED:refusal-code:temporal_budget"`, `:546-553`).

I retain one point terra did not address: scheduler-only codes must live in a
frozenset **not unioned into `READINESS_REASON_CODES`**, because `_validate_refusal`
(`:1436-1442`) — terra's own anchor — would then *accept* a scheduler code inside
an arm receipt's `refusals`, and the freeze-replay comparison at `:5343-5348`
compares `_canonical_refusals(receipt["refusals"])` against the recomputed set.
A scheduler code admissible there is a replay-corruption surface. Terra's phrase
"closed in the new scheduler receipt contract" is compatible with this; I read us
as agreeing and make the mechanism explicit.

### 1.4 Placement — **AGREED, converged independently**

New pure module + thin CLI, not `run_campaign.py`. Naming differs only
cosmetically (`joulewise/window_scheduler_gates.py` +
`scripts/evaluate_window_scheduler_gates.py` vs my
`joulewise/scheduler_gates.py` + `scripts/evaluate_window_gates.py`). **I adopt
terra's names** — `window_scheduler_gates` matches the r3 B-3 phrase "gate in the
window scheduler" and disambiguates from `validate_gate_packet.py`.

### 1.5 Ordering — **CONCEDED to terra; my design had an ordering incoherence**

Terra's sequence: pre-arm admission → issue arm receipt → pre-consume D-149
evaluation → GO receipt + authorization → `launch_window` consumes → shakedown
timing receipt closes → claim admission checks halt bounds.

My design ran all six gates "before authorizing any arm" while G6-C2 depends on
the arm receipt's `status`. That is circular: C2 ("arm ceremony green, freshness
honored") is unevaluable before the arm exists. The D-149 template sides with
terra — C2 cites "arm receipt path + sha256"
(`docs/process/d149-go-receipt-template.md:21`) and the receipt is written
"before the first **capture**" (`:3-4`), not before the arm.

Terra's split also puts the halt-bounds check at *claim admission* — i.e. the
pre-arm phase of the **next** window — which is precisely r3 B-3's "bounds
checked before the next window is authorized" (`MAGISTRATE-RULING-r3.md:66-67`).
Full concede; two-phase ordering adopted.

### 1.6 Enforced launch seam — **CONCEDED; terra caught a bypass I left open**

Terra: "require a matching final authorization receipt in
`scripts/launch_window.py` before consumption. Otherwise a direct CLI call
bypasses the scheduler."

Correct and important. `scripts/launch_window.py` takes `--pack-root`,
`--arm-receipt`, `--launch-manifest` (`:40-46`) and consumes via `launch`
(`:226`) with no gate reference whatsoever. My design bound the gate receipt into
the *GO receipt* — a document. A documentary binding that any direct CLI
invocation walks around is the literal failure mode V-5 exists to prevent
("prose halt triggers are how stop signals get eaten",
`MAGISTRATE-RULING-r3.md:68-69`). Terra's seam makes it mechanical. Adopted, and
it adds `scripts/launch_window.py` + `tests/test_launch_window.py` to the
implementation WRITE_SCOPE, which my staging omitted.

### 1.7 Arm monotonic stamp — **CONCEDED; my G2 input was defective**

Terra F2: the arm receipt "has UTC issuance and expiry but no arm monotonic
timestamp (`:6243-6262`); that needs a schema amendment."

Verified, and my G2 input table said "arm instant ← arm receipt `issued_at_utc` +
`valid_until_monotonic_ns` (`:401,403`)". That is wrong, provably:

```python
valid_until = min([evaluated_at_monotonic_ns + arm_horizon_ns, *evidence_expirations])   # :6235-6241
```

When the `min` is taken from an evidence expiry, `valid_until_monotonic_ns`
carries **no recoverable arm instant**. My derivation silently assumes the other
branch. Terra's field list (`t0_monotonic_ns`, `armed_at_monotonic_ns`,
`consumption_receipt{path,sha256,consumed_at_monotonic_ns}`, `t0_to_arm_ns`,
`arm_to_consume_samples_ns`, `arm_to_consume_p99_ns`, shared pack/reviewed-main/
boot bindings) is adopted wholesale.

Two things I add that terra did not price:

- **The value already exists**; it is simply not persisted.
  `evaluated_at_monotonic_ns` is live at `:6155` and `:6235`. The amendment is
  "persist a local", not "measure something new".
- **The amendment is not free.** `ARM_RECEIPT_KEYS` (`:394-414`) is exact-key
  enforced, so adding `armed_at_monotonic_ns` makes every existing `_v3` receipt
  refuse `readiness_unknown_key` under new code and every new receipt refuse
  under old. It must be a **schema version bump inside the `_v4` transaction**,
  not an in-place key addition. Terra's stage-2 WRITE_SCOPE puts
  `joulewise/arm_readiness.py` in an implementation stage without noting this;
  that under-prices it and collides with the V-3 freeze.
- Terra's consume-side cite verifies and is good news: `:7910-7913` already
  records `consumed_at_monotonic_ns` and refuses `consumption occurred after the
  arm validity horizon`. So **exactly one field is missing** to make r3 B-3's
  measurement custodiable.

### 1.8 p99 at n=1 — **CONCEDED to terra's formulation (numerically identical, cleaner)**

Mine: `max(ledger)` while n<100, switch to empirical p99 at n≥100.
Terra: nearest-rank p99 over every shakedown arm→consume event; at n=1 under
D-078 no-retry, p99 = that one value; no interpolation, no historic borrowing.

These **coincide numerically for all n ≤ 100** (nearest-rank p99 =
⌈0.99n⌉-th order statistic = the max for every n ≤ 100), so neither moves the
ruled 240 s bound. Terra's is one rule at all n; mine introduced a discontinuity
at n=100 that no ruling supports — an invented boundary, which is precisely what
§3 of my own design forbids. Terra's adopted; my n=100 switch withdrawn.

### 1.9 B-22 — **CONCEDED refinement; terra's characterization is more precise than mine**

I wrote "no machine consumer". Terra is sharper: a validator *exists* —
`validate_window_duration_margins_receipt()` at
`joulewise/window_duration_margins.py:1032` — but it "validates only
self-consistency of a supplied receipt". Verified: the signature takes
`receipt: Mapping` and **nothing else** (`:1032`), so it cannot compare against
pack bytes; it checks that `pack_tree_sha256`, `registry_source_sha256`,
`evaluation_basis_sha256`, `cell_inventory_sha256` are well-formed hex strings
(`:1042-1049`), never that they *match a selected frozen pack*. That is exactly
the hole the L4 falsifier walks through.

So the cure is not "build a consumer" but **"build a pack-aware close-out
validator taking a pack root, comparing cell inventory, member pins, pack-tree
hash, registry source hash, and evaluation-basis binding against the selected
frozen pack."** Terra's wording adopted.

Terra also draws a boundary I did not: "The scheduler's B-22 pre-admission check
is only a prevention of an uncloseable claim window. It does not substitute for
the post-window consumer, and it must not evaluate or block a shakedown
close-out." **AGREED and adopted** — it keeps the scheduler from quietly becoming
the close-out authority, which would re-home a ruling S-2 placed elsewhere.

### 1.10 Boot UUID — **PARTIAL: terra's three-point check adopted; my campaign pin retained (DISPUTED removal)**

Terra: T-0 GO boot UUID, arm receipt boot UUID, and a fresh `sysctl` probe
identical **before arm and before consume**; existing `readiness_record_expired`
/ `readiness_io_error`.

- **Concede the before-consume re-check** — I checked once. A reboot in the
  arm→consume gap is live (that gap is the very thing G2 bounds at 240 s) and my
  single check misses it.
- **Concede the code choice** for the artifact-mismatch conjunct:
  `readiness_record_expired` is exactly what the arm path emits at `:4263-4270`
  ("evidence item belongs to a prior boot session"); mirror it rather than invent
  `scheduler_boot_pin_mismatch`.
- **DISPUTE dropping the campaign-span pin.** r5 V-7 item 5
  (`rulings-r5-consolidation.md:177-179`) is a NO-REBOOT COMMITMENT **for the
  campaign span** — "a reboot voids the family at any remaining wall-clock". Terra's
  three-point check is *internally consistent by construction*: after a reboot,
  window N+1 authors a fresh T-0, a fresh arm, and a fresh probe, all three
  agreeing on the **new** boot UUID → terra's gate PASSES while the family is
  void. Only a create-only, span-scoped pin (`campaign_boot_pin.v1`, `O_EXCL`)
  makes "voids the family" mechanical. Keep both: terra's three-point identity
  **and** the campaign pin. The pin conjunct has no governed predicate in
  `arm_readiness`, so it is the one place a new closed scheduler code is
  warranted (consistent with terra's own rule at its line 142).

### 1.11 Staging — **PARTIAL**

- **AGREE the B-22 cure is ours and goes early.** r5 S-2 (`:24-28`) places it in
  the `_v4` program, gauntleted, landing before the first claim close-out. My
  "blocked on an external item" framing was wrong; terra's "first" is right on
  priority.
- **DISPUTE folding it into the scheduler-gate stage list.** It is a separate
  work item with its own gauntlet and its own WRITE_SCOPE
  (`joulewise/window_duration_margins.py`, `scripts/record_window_duration_margins.py`,
  `tests/test_window_duration_margins.py`). Run it as a **parallel track**
  starting first; the scheduler's G3 stage is gated on that track landing. Same
  ordering, honest scope boundaries.
- **AGREE with terra's stage-4 exclusion** (`decision_log.md`, `RUN_STATE.md`,
  `TASK_QUEUE.md`, process-trace rulings stay lead-owned, outside any
  implementation worker's scope) — this is r5 S-4's kernel-transaction discipline
  (`:40-47`) and is better stated than my stage 7.
- **RETAIN my freeze constraint, which terra omits.** r5 V-3(c) (`:131-135`)
  freezes local_main **and** origin/main for the span. Every stage lands before
  the freeze opens or rides the transaction's enumerated step list (V-3(d)).
  Landing gate code mid-span trips the reviewed-main gate by construction — and
  terra's stage 2 touches `arm_readiness.py`, the highest-collision file in the
  tree.

---

## 2. What terra caught that I missed

1. **The fuse misreading** (§0) — decisive, and the ruling had pre-registered it.
2. **The `launch_window.py` bypass** (§1.6) — a mechanical hole in my custody
   binding.
3. **The existing `validate_r1_temporal_budget` call site** `:6151-6159` (§1.2).
4. **The missing `armed_at_monotonic_ns`** and the arithmetic proving my derivation
   invalid (§1.7).
5. **Read-side vocabulary closure** `_validate_refusal:1434-1448`, and
   registry-sourced `TEMPORAL_BUDGET` code/type instead of invented codes (§1.3).
6. **Before-consume boot re-check** (§1.10).
7. **The scheduler-vs-close-out authority boundary** for B-22 (§1.9).
8. **That the D-149 template cannot presently custody the r3 B-3 measurements at
   all** — I noticed it needed one line (`gate_receipt_sha256`); terra saw the
   template has no monotonic fields and no consumption reference whatsoever
   (`:10-39`). Terra's F2 is the larger, correct finding.

## 3. My three magistrate-facing findings vs terra

Terra contradicts **none** of the three. In each case terra's design is silent,
and the silence is a gap:

| finding | terra's text | status |
|---|---|---|
| **C1 shakedown-scoping** (S-1 reclassification, `rulings-r5-consolidation.md:12-19`) | C1 = "custodied council verdict plus three form conclusions" — the ED-QUAL conjunct is carried unqualified | **survives, and terra's design deadlocks without it.** Terra's C1 as written refuses the shakedown, because ED-QUALIFICATION rows are not closed — the exact structural unreachability "both cold seats independently proved" (r5 S-1). The reclassification must be shakedown-scoped and CLAIM-unscoped. |
| **C3 evaluator self-refusal** (B-16 tightened pattern `codex\|claude\|t3\|mcp-server`, r5 S-7(a) `:69-74`) | C3 = "attached census/quiescence outputs" — no evaluator-context check | **survives.** Terra proposes no alternative C3 handling, so there is nothing to weigh against it. Under the tightened pattern an agent-run evaluator refuses itself; the no-hands path needs an agent-free driver process, and that is a topology commitment to be ruled, not assumed. |
| **C4 two-verb probe** (`sudo -n systemsetup -getusingnetworktime` **and** `-setusingnetworktime off`, `scripts/capture_t0_step.py:612`, per r5 V-7.4 `:174-177`) | C4 = "boot and clock-off evidence" — no verb distinction, no E-1 blocker | **survives.** E-1's prior evidence tested GET only; the ruling explicitly adds the setter probe because that is the verb T-0 executes. Terra's C4 would pass a bench where GET works and SET does not. |

I also retain the `arm_readiness.py:643` anchor
(`"CLOCK_ATTESTATION": frozenset({"OPERATOR_ATTESTATION", "PROBE"})`, per r5 V-5
`:157-158`): PROBE admissibility is what makes an unattended C4 possible at all.
Terra does not cite it.

## 4. Executed refutations against terra

Only two, both narrow — terra's substantive claims held up:

1. **"Shakedown itself is exempt because it creates the measurement"** (terra's
   halt-bounds row) is right for the *bounds* but incomplete as a gate: without
   an explicit `measurement_state` conjunct, a **claim** window may also run
   before any measurement exists, since terra's claim-side rule ("claims refuse
   without a valid, exact-family shakedown record") is stated in the test-pin
   column, not the rule column. I keep it as a first-class refusal
   (`scheduler_bounds_unmeasured`) so shakedown-first is mechanical rather than
   incidental. Minor, probably a drafting artifact.
2. **Terra's V3 verification did not execute** (`exit_code: 1`, "No usable
   temporary directory found"); terra flags this at FL2. So no claim in either
   design is backed by a passing focused test yet. Both designs' test pins are
   *specified*, none *run*. That belongs in the ruling as a shared residual, not
   as a mark against terra.

Terra's `git show`-based inspection I re-verified independently at `5bd7acf`:
`:338`, `:488-499`, `:941-960`, `:1434-1448`, `:3299-3341`, `:6095-6100`,
`:6151-6159`, `:6235-6241`, `:6243-6262`, `:7910-7913`,
`window_duration_margins.py:1032-1049`, `MAGISTRATE-RULING.md:95-105` — **all
land, all contents match.** No terra cite is refuted.

---

## 5. Final amended position, per item

| # | Item | Position |
|---|---|---|
| 1 | Fuse = minimum remaining T-0 evidence life ≥ `arm_to_consume_budget_ns` (300 s); **no projected span** | **CONCEDED** to terra |
| 2 | `--projected-span-ns` / `scheduler_span_undeclared` withdrawn | **CONCEDED** |
| 3 | Existing check at `:6151-6159`; scheduler invokes, does not re-implement | **CONCEDED**, + my dormancy addition (`if lifecycle_registry is not None`) |
| 4 | Placement: new pure module + thin CLI, not `run_campaign` | **AGREED** (independent convergence); terra's names adopted |
| 5 | Refusal shape `:338`; read-side closure `:1434-1448`; registry-sourced `TEMPORAL_BUDGET` code | **CONCEDED** to terra |
| 6 | Scheduler codes in a frozenset **not** unioned into `READINESS_REASON_CODES` | **AGREED** (mechanism made explicit; replay-corruption surface at `:5343-5348`) |
| 7 | Two-phase ordering: pre-arm admission → arm → pre-consume D-149 → GO+authorization | **CONCEDED** to terra |
| 8 | Enforced authorization seam in `scripts/launch_window.py` | **CONCEDED** to terra; added to WRITE_SCOPE |
| 9 | `armed_at_monotonic_ns` + terra's full timing-field list | **CONCEDED** to terra |
| 10 | That amendment is a **schema version bump inside `_v4`**, not an in-place key add (`ARM_RECEIPT_KEYS:394-414` is exact-key enforced) | **DISPUTED** (terra under-prices; I add the constraint) |
| 11 | p99 = nearest-rank over shakedown events; n=1 ⇒ that value; no interpolation/borrowing | **CONCEDED** to terra; my n=100 switch withdrawn |
| 12 | B-22 cure = pack-aware close-out validator taking a pack root (not merely a consumer) | **CONCEDED** to terra's sharper reading of `:1032-1049` |
| 13 | Scheduler B-22 check prevents an uncloseable claim window; does **not** substitute for the post-window consumer, must not touch shakedown close-out | **AGREED** |
| 14 | Boot: three-point identity, checked before arm **and** before consume; mirror `readiness_record_expired` | **CONCEDED** to terra |
| 15 | Boot: campaign-span `campaign_boot_pin.v1` **retained** alongside | **DISPUTED** (terra's three-point check is internally consistent after a reboot and passes a void family; V-7.5 binds the span, not the window) |
| 16 | C1 must be shakedown-scoped per S-1 | **DISPUTED** as against terra's silence — my finding stands; terra's C1 deadlocks |
| 17 | C3 evaluator-context self-check + agent-free driver topology | **DISPUTED** as against terra's silence — stands, unopposed |
| 18 | C4 probes both GET and SET verbs; `:643` PROBE admissibility | **DISPUTED** as against terra's silence — stands, unopposed |
| 19 | `scheduler_bounds_unmeasured` as a first-class refusal (CLAIM before any measurement) | **DISPUTED** (terra states it only in a test-pin column) |
| 20 | B-22 cure runs as a **parallel track starting first**, not as stage 1 of the scheduler build | **DISPUTED** on scope boundary; **AGREED** on priority |
| 21 | Lead-owned files (`decision_log.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, rulings) outside implementation WRITE_SCOPE | **AGREED**; terra's statement adopted over my stage 7 |
| 22 | V-3(c) freeze constraint binds all stages | **DISPUTED** as against terra's silence — retained |
| 23 | No `--force`/bypass flag anywhere, testable by grep | **AGREED** (terra: "does not waive C1–C5, auto-retry a refusal") |
| 24 | Family-publication-marker schema stays a separate D-144 round | **AGREED** (terra, r5 V-6 `:159-164`) |

**Net:** conceded 9, agreed 7, disputed 8 — of which 4 (16–18, 22) are disputes
against silence rather than against a stated terra position, and 3 (10, 15, 19)
are additions terra's design would accept without contradiction. The one genuine
methodological disagreement is item 20 (scope boundary of the B-22 track).

---

## 6. Consolidated magistrate ruling list

**Decisive:**

**R1.** Ratify the corrected fuse semantics and **strike the "projected window
span + margin" framing from the brief**: the gate is `min(TIME_BOUND evidence
deadlines) − now ≥ arm_to_consume_budget_ns` (300 s per V5). The ruling already
warned that "both seats independently misread it; in production that misreading
is a lost window" (`MAGISTRATE-RULING.md:100-105`) — a third seat (this
coordinator's brief) then misread it identically. **Recommend the corrected
sentence be written into the gate module's docstring and the D-149 template**, so
the next reader cannot repeat it. This is a first-use-test failure in the
governing prose, not just a seat error.

**R2.** Rule the **arm-receipt schema amendment** adding `armed_at_monotonic_ns`
(+ terra's timing fields): version bump inside the `_v4` transaction, priced for
receipt invalidation (`ARM_RECEIPT_KEYS:394-414` is exact-key enforced). Without
it, r3 B-3's measurement cannot be custodied at all (terra F2) — and exactly one
field is missing, since consumption already stamps monotonically (`:7910-7913`).

**R3.** Rule the **enforced authorization seam**: `scripts/launch_window.py` must
require a matching authorization receipt before consumption. A documentary
binding alone reproduces the eaten-stop-signal failure V-5 exists to prevent.

**R4.** Rule the **p99 estimator**: nearest-rank over shakedown arm→consume
events; at n=1 under D-078 no-retry, p99 is that observed value; no interpolation,
no historic borrowing.

**Contested, needing a call:**

**R5.** Boot pinning — three-point identity only (terra), or three-point **plus**
a campaign-span `campaign_boot_pin.v1` (mine). My argument: terra's check passes a
post-reboot window whose artifacts are all internally consistent, while
V-7.5 (`:177-179`) voids the family "at any remaining wall-clock".

**R6.** C1's ED-QUALIFICATION conjunct — confirm the S-1 reclassification is
**shakedown-scoped and CLAIM-unscoped**. Unruled, terra's C1 refuses the very
shakedown that D-139 makes first, restoring the deadlock both cold seats proved.

**R7.** C3 topology — does the D-149 no-hands path run from an **agent-free
driver process**? Under B-16's tightened pattern an agent-run evaluator refuses
itself. Rule the topology; do not let it be discovered at 03:00.

**R8.** B-22 track boundary — parallel track with its own gauntlet and
WRITE_SCOPE (mine), or stage 1 of the scheduler build (terra). Both agree it goes
first.

**Recorded, uncontested:**

**R9.** C4 probes both `-getusingnetworktime` and `-setusingnetworktime off`
(`capture_t0_step.py:612`, r5 V-7.4); E-1's sudoers install is a hard
precondition of any auto-GO window.

**R10.** All stages land before the V-3(c) freeze opens or ride the transaction's
enumerated step list; terra's stage 2 touches `arm_readiness.py`, the
highest-collision file.

**R11.** Both parameters are `ED_RESERVED` at `5bd7acf` — the value
(`:534-535`) **and** the `TEMPORAL_BUDGET` refusal code (`:546-553`). G1 is
inert-by-refusal until Ed's registry install; that is correct behaviour but must
be visible on the V-7 packet.

**R12.** Shared residual: **neither seat executed a single focused test** (terra's
V3 failed on a read-only sandbox, FL2; my seat is read-only by construction).
Every test pin in both designs is specified, none run. First implementation pass
runs them in a writable worktree before any review credit is taken.
