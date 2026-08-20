# Window-scheduler mechanical gates — design (Opus seat, D-144 round)

Authority: r3 B-3 (`MAGISTRATE-RULING-r3.md:61-69`) — under D-149 unattended
auto-GO the halt trigger is "a MECHANICAL GATE IN THE WINDOW SCHEDULER (bounds
checked before the next window is authorized), not prose". r5 S-2
(`rulings-r5-consolidation.md:21-31`) adds the claim-window admission gate;
r5 V-3(b) (`:129-131`) adds the fail-early `reviewed_main` check; r5 V-6
(`:159-164`) makes THIS design its own bounded co-design round, no waiver.
Verdict packet V-5 (`readiness-sitting/VERDICT-PACKET.md:116`) records the
executed finding: **absent from `scripts/` and `joulewise/`**.

---

## 0. Executed verification of the two contested code claims

**(a) The cold refuter's asserted minimum-fuse check in `scripts/run_campaign.py`
does not exist at `5bd7acf`.** The file is 8148 lines; its ONLY `arm_readiness`
coupling is the import at `scripts/run_campaign.py:48-53`
(`LaunchLineageError`, `authenticate_campaign_launch_lineage`,
`launch_lineage_required`, `render_json`), consumed solely for launch-lineage
authentication at `:1466-1479`, `:1490-1497`, `:1497-1555`. Greps over the whole
file for `valid_until|monotonic_ns|reviewed_main|boot_session|\bfuse\b|horizon|
expiry|\b300\b` return **zero** hits. `scripts/launch_window.py` (304 lines) is a
consumption-side lifecycle tool (`:38-52` argparse: `--pack-root`,
`--arm-receipt`, `--launch-manifest`; `:226 launch`, `:253 lifecycle`) with no
gate of any kind. The claim is refuted; the gate layer is greenfield.

**(b) The arm path's own expiry check is bypassed on the freeze-replay legs.**
`_authenticate_generic_evidence_item` enforces `valid_until_monotonic_ns <
now_monotonic_ns` only when `now_monotonic_ns` is passed
(`joulewise/arm_readiness.py:4272-4278`). Both freeze-replay call sites —
`:5253-5262` and `:5385-5392` — pass `expected_boot_session_id` and
`expected_head_commit` but **not** `now_monotonic_ns`. This is B-12 (re-graded
nit→blocker, `VERDICT-PACKET.md` b.2 B-12): a `FREEZE_AND_ARM` row can report
PASS from expired evidence. **Consequence for this design: G1 must recompute
deadlines from the evidence receipt bytes itself and must never accept the arm
receipt's `status: PASS` as proof of freshness.** Until B-12 lands, G1 is the
only live expiry check in the auto-GO path.

---

## 1. Placement

**`joulewise/scheduler_gates.py`** (new pure module) + **`scripts/evaluate_window_gates.py`** (thin CLI).

Why `joulewise/` and not `scripts/`:

- The gates must reuse the governed refusal machinery. `_receipt_refusal`
  (`arm_readiness.py:3623-3635`) hard-refuses any code outside
  `READINESS_REASON_CODES` (`:192-201`) with `readiness_internal_error` — a
  `scripts/` evaluator cannot mint refusals legitimately without importing it.
- The gates need `reviewed_main` (`:3652-3675`), `_pack_record` (`:3676-3700`),
  `_current_boot_session_id` (`:1075-1095`), `validate_r1_temporal_budget`
  (`:3299-3341`), `R1_EVIDENCE_FRESHNESS_CLASSES` (`:676-700`) — all module-private
  or module-level in `joulewise/`.
- Testability: the existing suite convention is `tests/test_arm_readiness*.py`
  (10 files) against `joulewise/` modules; `scripts/` shell gates
  (`prewindow_check.sh`) carry no regression pins.

Why NOT extending `scripts/prewindow_check.sh`: that script explicitly disclaims
gate authority — "This is a READINESS check, not a measurement gate. It never
waives, relaxes, or substitutes for the campaign's own environment and CPU
admission gates" (`scripts/prewindow_check.sh:16-19`). It stays advisory and
feeds C3 as an input, never as an authority.

**Vocabulary boundary — deliberate.** The gates get their OWN frozenset,
`SCHEDULER_GATE_REASON_CODES`, defined in `scheduler_gates.py`, and their own
emitter `_gate_refusal`. They are NOT unioned into `READINESS_REASON_CODES`.
Reason: an arm receipt (`ARM_RECEIPT_KEYS`, `arm_readiness.py:394-414`) must not
be able to carry a scheduler code — a scheduler-layer refusal masquerading as an
arm-ceremony row refusal would corrupt the replay comparison at
`arm_readiness.py:5343-5348`. Where a gate's predicate is *exactly* an existing
arm-ceremony predicate (G4), the gate mirrors the arm code verbatim and marks it
`mirrored_from: "arm_readiness"` in the receipt.

**Receipt.** Schema `joulewise.window_scheduler_gate_receipt.v1`, written into
the window custody root **before** the first capture (D-149 template
`docs/process/d149-go-receipt-template.md:3-4`). Shape:

```
schema_version, receipt_kind: "window_scheduler_gate",
receipt_id, issued_at_utc, now_monotonic_ns, boot_session_id,
window_class: SHAKEDOWN | CLAIM,
pack:            <_pack_record(root), arm_readiness.py:3676-3700>
reviewed_main:   <reviewed_main(root), arm_readiness.py:3652-3675 — full dict>
gates: [ {gate_id, verdict: PASS|REFUSE|RECORD_ONLY, observations{...},
          refusals: [{type, code, gate_id, detail, mirrored_from?}]} ]
verdict: GO | NO-GO
claim_admissible: bool
assurance: <ASSURANCE, arm_readiness.py:110-113>
```

**All six gates always evaluate; no short-circuit.** The D-149 template requires
NO-GO to list the failing condition(**s**) (`d149-go-receipt-template.md:39`).
Only an environment error (`scheduler_environment_error`) aborts early.

**Custody binding.** The D-149 GO receipt gains one line —
`gate_receipt_sha256: <...>` — and a GO receipt whose gate receipt is absent,
unreadable, digest-mismatched, or `verdict: NO-GO` is not a GO (template `:5`,
"A GO without a receipt is not a GO"). Append-only: a corrected gate receipt is a
NEW receipt superseding by timestamp, old one retained (template `:60-62`). When
a gate receipt enters a sitting packet it is listed in the Exhibit manifest and
validated by `scripts/validate_gate_packet.py` (grammar at `:64-75`).

---

## 2. Gate inventory

### G1 — MINIMUM FUSE

Refuse arming when the remaining evidence fuse cannot cover the projected window
span plus the governed arm-to-consume budget.

**INPUTS**
| input | exact source |
|---|---|
| per-receipt deadlines | evidence receipt `valid_until_monotonic_ns` (`arm_readiness.py:403`, key set `:431+`), read from the frozen pack's `arm_readiness.evidence/` namespace (`_evidence_directories`, `:4155-4163`) |
| which receipts are fuse-bearing | `R1_EVIDENCE_FRESHNESS_CLASSES` `== "TIME_BOUND"` (`:676-700`; today: `BACKUP_PREFLIGHT`, `CLOCK_ATTESTATION`, `CLOCK_PROBE`, `MACHINE_PREFLIGHT`, `MAINTENANCE_CENSUS`, `POWERMETRICS_PROBE`, `POWER_PREFLIGHT`, `PROCESS_CENSUS`) |
| budget (the margin) | `registry["arm_policy"]["arm_to_consume_budget_ns"]`, read via `validate_r1_temporal_budget` (`:3299-3341`, budget read at `:3305`) |
| projected window span | **operator-supplied `--projected-span-ns`, sourced from the window's run card**; no machine-readable span exists today (`docs/process/window-run-cards/shakedown-v3-first-light.md:20-36` is a six-step prose block) |
| now | `time.monotonic_ns()` in the gate process, valid only under G5's boot pin |
| class horizons (recorded, not re-derived) | `_VOLATILE_EVIDENCE_VALIDITY_NS = 20*60*1e9`, `_NONVOLATILE_EVIDENCE_VALIDITY_NS = 6*3600*1e9` (`joulewise/arm_readiness_evidence_t0.py:49-50`, applied `:1760-1762`) |

**PREDICATE** `min(deadlines) - now_monotonic_ns >= projected_span_ns + arm_to_consume_budget_ns`.
Zero invented numbers: the margin IS the registry budget; the span IS the run
card's.

**REFUSAL CODES** (type `TEMPORAL`)
- `scheduler_fuse_insufficient` — predicate false. Observations:
  `earliest_deadline_ns`, `now_monotonic_ns`, `projected_span_ns`,
  `arm_to_consume_budget_ns`, `deficit_ns`, `governing_evidence_id`,
  `governing_kind`.
- `scheduler_fuse_underivable` — any TIME_BOUND receipt missing/non-int/≤0
  deadline (mirrors `arm_readiness.py:3319-3330`), or unreadable evidence bytes.
- `scheduler_span_undeclared` — `--projected-span-ns` absent. **No default.**
- `scheduler_budget_unresolved` — registry budget still
  `"ED_RESERVED:arm-to-consume-budget-ns"` (`arm_readiness.py:534-535`); mirrors
  `readiness_row_registry_mismatch` raised at `:3308-3312`.

**FAIL-CLOSED DEFAULT** REFUSE. Every underivable input refuses; there is no
"assume enough fuse" branch and no `--force`.

**TEST PINS**
1. Deadline at `now + span + budget - 1` → `scheduler_fuse_insufficient`; at
   `+0` → PASS (boundary pinned on the inclusive side).
2. One TIME_BOUND receipt with `valid_until_monotonic_ns: null` amid valid ones
   → `scheduler_fuse_underivable` (proves min() does not silently skip).
3. Registry with the ED_RESERVED placeholder → `scheduler_budget_unresolved`.
4. Span omitted → `scheduler_span_undeclared` (proves absence ≠ zero).
5. **B-12 independence pin**: an arm receipt with `status: PASS` whose evidence
   deadline is `now - 1` → G1 REFUSES. Fails today if G1 ever short-circuits on
   arm status; this is the regression that keeps `:5253-5262`/`:5385-5392`
   from re-entering the auto-GO path.

---

### G2 — HALT BOUNDS (T-0→arm ≤ 15 min; p99 arm→consume ≤ 4 min)

r3 B-3 (`MAGISTRATE-RULING-r3.md:57-69`): V5 values install as status-quo
defaults; **the first D-139 shakedown IS the measurement**, its GO receipt
recording the observed gaps; violation halts the campaign BEFORE any claim
window and the horizon question goes to Ed with the observed numbers.

**TWO-PHASE, mechanically distinguished** by `timing_ledger.measurement_state`:

- `UNMEASURED` (ledger empty): gate MEASURES and RECORDS both gaps, verdict
  `RECORD_ONLY`, no refusal on bound violation — the shakedown is what produces
  the numbers. But `window_class == CLAIM` under `UNMEASURED` → REFUSE
  `scheduler_bounds_unmeasured`. (Shakedown-first is thereby mechanical.)
- `MEASURED` (≥1 closed window in the ledger): bounds ENFORCED.

**INPUTS**
| gap | exact source |
|---|---|
| T-0 anchor | T-0 sequence `finished_monotonic_ns` (`arm_readiness_evidence_t0.py:499`, staleness cousin `:537`; `_MAX_T0_SEQUENCE_AGE_NS = 60*60*1e9` at `:52`) |
| arm instant | arm receipt `issued_at_utc` + `valid_until_monotonic_ns` (`arm_readiness.py:401,403`) |
| consume instant | consumption receipt, `CONSUMPTION_RECEIPT_SCHEMA = "joulewise.arm_readiness_launch_consumption.v2"` (`:71`), located per `scripts/launch_window.py:157 _consumption_path` |
| ledger | new `window_timing_ledger.v1`, append-only, in the campaign custody root |

**p99 with n=1 — stated honestly.** p99 is undefined at small n. The gate
evaluates `max(observed arm→consume over the ledger) <= 240e9 ns` while
`n < 100`, and records `statistic: "max(n=<k>) as conservative p99 upper bound"`
in the receipt. A max is ≥ p99 for any sample, so this is strictly tighter than
the ruled bound — it cannot pass a window the ruled bound would fail. At
`n >= 100` the gate switches to the empirical p99 and records `statistic:
"p99(n=<k>)"`. This is a measurement substitution, not a threshold change; the
numbers 15 min and 4 min come only from `MAGISTRATE-RULING-r3.md:61-62`.

**REFUSAL CODES** (type `HALT`)
- `scheduler_halt_bound_violated` — either bound exceeded. Observations:
  `t0_to_arm_ns`, `arm_to_consume_statistic_ns`, `statistic`, `bound_ns`,
  `bound_source: "MAGISTRATE-RULING-r3.md:61-62"`, `ledger_n`.
- `scheduler_campaign_halted` — a HALT record exists. **Sticky**: once written,
  every subsequent evaluation on the family refuses. Cleared only by an
  Ed-signed clearance artifact naming the observed numbers (r3 B-3:63-65 — the
  horizon question goes to Ed; a post-mint change is `_v5`-priced). The gate
  never clears its own halt (rule-11 lieutenant-forbidden: "reinterpreting a
  stop signal").
- `scheduler_bounds_unmeasured` — CLAIM window before any measurement.
- `scheduler_timing_underivable` — missing T-0 or arm or consume stamp.
- `scheduler_timing_cross_boot` — any two stamps under different
  `boot_session_id` (monotonic clocks are not comparable across boots; this is
  the interlock that makes G5 a precondition of G2, not a peer).

**FAIL-CLOSED DEFAULT** REFUSE on every underivable input; `RECORD_ONLY` is
reachable ONLY for `window_class == SHAKEDOWN` with an empty ledger.

**TEST PINS**
1. T-0→arm at `900e9 + 1` under MEASURED → violated; at `900e9` → PASS.
2. Ledger of 3 with max `241e9` → violated, `statistic: "max(n=3)…"`.
3. CLAIM + empty ledger → `scheduler_bounds_unmeasured`.
4. HALT record present + a perfectly clean window → `scheduler_campaign_halted`
   (proves stickiness survives a good window).
5. Arm and consume stamps under different boot UUIDs →
   `scheduler_timing_cross_boot`, not a computed gap.
6. SHAKEDOWN + empty ledger + a 20-minute T-0→arm gap → `RECORD_ONLY`, gap
   written to the ledger, `verdict: GO` unaffected (proves the measurement
   window is not blocked by the thing it exists to measure).

---

### G3 — B-22 PRESENCE (claim-window admission)

r5 S-2, verbatim (`rulings-r5-consolidation.md:21-31`): "ONE gate, stated
precisely: B-22 blocks CLAIM-WINDOW CLOSE-OUT. The D-139 shakedown (non-claim,
diagnostic) may run and close without it… the scheduler's claim-window admission
gate (S-2's mechanical gates) checks its presence. Shakedown close-out records
produced under the un-cured validator are BARRED from any later claim use — no
retrospective promotion."

**EXECUTED STATE AT `5bd7acf`.** `window_duration_margins_receipt.v1` is
declared at `joulewise/window_duration_margins.py:43`
(`RECEIPT_SCHEMA_VERSION`), namespace `:44`, written by
`scripts/record_window_duration_margins.py:25-31`. Repo-wide references to
`window_duration_margins` outside the module, its script, and its own test:
`TASK_QUEUE.md`, `docs/**` only. **No machine consumer and no frozen-pack
binding exist** — L6's "writer only" reproduces.

**INPUTS**
| input | source |
|---|---|
| window class | run card / CLI `--window-class` |
| consumer presence | importable symbol `joulewise.window_duration_margins.authenticate_window_duration_margins` (the S-2 work item's deliverable) |
| binding presence | the receipt's `pack` binding resolving against `_pack_record` (`arm_readiness.py:3676-3700`) — pack-and-ordinal exact per r5 V-1(v) (`:100-101`) |
| cure proof | a defect-shaped tamper fixture: the L4 falsifier — a truncated two-cell receipt that validates after only its internal SHA is repaired (`VERDICT-PACKET.md` B-22, `seat-L4.md:2 V5,:17`) |
| provenance of every input record | each record's originating gate receipt's `claim_admissible` flag |

**PREDICATE (two limbs)**
1. *Admission*: `window_class == CLAIM` ⟹ consumer importable **and** binding
   resolves **and** the tamper fixture is REFUSED by the consumer when invoked.
   Presence is proved by executing the falsifier, never by a version string — a
   consumer that exists but accepts the truncated receipt is not a cure.
2. *Barring*: every gate receipt stamps `claim_admissible = (limb 1 holds)`.
   Any window whose declared inputs reference a record whose gate receipt has
   `claim_admissible: false` → REFUSE. No retrospective promotion.

**REFUSAL CODES** (type `ADMISSION`)
- `scheduler_b22_cure_absent` (consumer missing / not importable)
- `scheduler_b22_binding_absent` (no frozen-pack binding)
- `scheduler_b22_cure_ineffective` (tamper fixture accepted — the cure is a stub)
- `scheduler_shakedown_record_claim_use` (limb 2)

**FAIL-CLOSED DEFAULT** REFUSE for CLAIM; PASS for SHAKEDOWN with
`claim_admissible: false` stamped. If the tamper probe cannot be executed at all
(import error, fixture missing) → REFUSE, never "assume cured".

**TEST PINS**
1. CLAIM at today's tree → `scheduler_b22_cure_absent` (the gate is red on
   arrival — pinning that is the point).
2. SHAKEDOWN at today's tree → PASS, `claim_admissible: false`.
3. Stub consumer that returns True unconditionally →
   `scheduler_b22_cure_ineffective`.
4. CLAIM window declaring an input produced under a `claim_admissible: false`
   receipt → `scheduler_shakedown_record_claim_use`, even with the cure landed.

---

### G4 — `reviewed_main` EXACT-MATCH, FAIL-EARLY

r5 V-3(b) (`rulings-r5-consolidation.md:129-131`): "a scheduler-gate check that
`reviewed_main` `exact_match` is TRUE before every arm — the latter exists as the
refusal itself; the guard makes it fail-early."

**INPUTS** `reviewed_main(pack_root)` — `arm_readiness.py:3652-3675`. Returns
`head_commit`, `head_tree_oid`, `local_main_commit`, `origin_main_commit`,
`clean`, `exact_match`. `clean = (git status --porcelain=v1
--untracked-files=all == "")` (`:3659-3665`); `exact = clean and head ==
local_main == origin_main and head != "unavailable"` (`:3666`).

**PREDICATE** `exact_match is True`.

**REFUSAL CODES** — mirrored verbatim from the governed GIT set
(`arm_readiness.py:140-146`), because the predicate is identical:
- `readiness_git_tree_dirty` (`mirrored_from: "arm_readiness"`) when `not clean`
- `readiness_reviewed_main_mismatch` (`mirrored_from`) otherwise

Mirrors the arm-time behaviour at `:6422-6435` (dirty first, then not-exact) and
`:6293-6298` (stale reviewed-main proof).

**What the gate ADDS beyond the arm refusal**: the arm-time refusal does not say
*which* conjunct failed. The gate records
`failed_conjunct: dirty | head_ne_local_main | head_ne_origin_main | unavailable`
plus the four raw values. This matters because `origin_main == "unavailable"`
(no remote ref, offline bench) makes `exact` false — the fail-closed direction is
correct, but it must not be read as tampering at 03:00. Recorded, and it is the
availability fragility r5 S-6 names (`:56-58`): "GIT_CHECKOUT has no R1 artifact
and no lifecycle governance at all — its sole guarantee is the arm-time
exact-match check, which is availability-fragile."

**Interlock with the V-3 freeze.** The freeze binds local_main AND origin/main
for the span (r5 V-3(c), `:131-135`) — no pushes from any machine or session.
G4 is the mechanical detector of a freeze breach: any push to origin/main during
the span moves `origin_main_commit` off `head_commit` and every subsequent arm
refuses. That is the intended coupling; state it in the receipt.

**FAIL-CLOSED DEFAULT** REFUSE. `_git_text` returning None → "unavailable" →
`exact` false → refuse (`:3655-3658`).

**TEST PINS**
1. One untracked file → `readiness_git_tree_dirty`, `failed_conjunct: dirty`.
2. `origin/main` one commit ahead → `readiness_reviewed_main_mismatch`,
   `failed_conjunct: head_ne_origin_main` (the freeze-breach pin).
3. No `refs/remotes/origin/main` at all → refuse,
   `failed_conjunct: unavailable` (proves offline ≠ pass).
4. Clean, all three equal → PASS.

---

### G5 — BOOT-UUID PIN

r5 V-7 item 5 (`rulings-r5-consolidation.md:177-179`): "NO-REBOOT COMMITMENT for
the campaign span + pinned boot UUID (a reboot voids the family at any remaining
wall-clock, `:4263-4270`)."

**INPUTS**
| input | source |
|---|---|
| live UUID | `_current_boot_session_id()` — `arm_readiness.py:1075-1095`, `sysctl -n kern.bootsessionuuid`, 10 s timeout, raises `readiness_io_error` on any failure; docstring `:1076`: "callers must fail closed if unavailable" |
| per-receipt UUID | evidence receipt `boot_session_id`, checked at `:4263-4270` (`readiness_record_expired`, "evidence item belongs to a prior boot session") |
| campaign-span pin | **new** `campaign_boot_pin.v1` in the campaign custody root — does not exist today; per-receipt binding is per-artifact, not per-campaign |

**PREDICATE** live UUID == pinned UUID == every evidence receipt's
`boot_session_id`. First gate evaluation of a family WRITES the pin
(create-only, `O_EXCL`); thereafter compares.

**REFUSAL CODES** (type `IDENTITY`)
- `scheduler_boot_pin_mismatch` — reboot occurred; the family is void at any
  remaining wall-clock.
- `scheduler_boot_pin_underivable` — sysctl failed/timed out.
- `scheduler_boot_pin_conflict` — pin file exists with a different family id, or
  `O_EXCL` create loses a race (two schedulers → single-writer violation).

**FAIL-CLOSED DEFAULT** REFUSE. G5 is evaluated FIRST among the six because G1's
and G2's monotonic arithmetic is meaningless across a boot; a G5 failure marks
G1/G2 `NOT_EVALUATED` (never PASS) in the receipt.

**TEST PINS**
1. Pin ≠ live → `scheduler_boot_pin_mismatch`, and G1/G2 recorded
   `NOT_EVALUATED` (the ordering pin).
2. sysctl absent/nonzero → `scheduler_boot_pin_underivable`.
3. Second concurrent create → `scheduler_boot_pin_conflict`.
4. Evidence receipt from a prior boot with matching live/pin → refuse
   (proves the third conjunct is real, not decorative).

---

### G6 — D-149 FIVE-CONDITION AUTO-GO CHECKLIST AS CODE

Authority: `docs/decision_log.md:172` (index row, five conditions verbatim) and
`:8865+` (body). Template: `docs/process/d149-go-receipt-template.md:9-40`, which
at `:63-66` licenses exactly this ("a mechanical evaluator MAY be built to fill
C2–C4… it goes through the ordinary gauntlet first… The template is
authoritative either way"). Queue row: `TASK_QUEUE.md:373-378`
`WO-D149-GO-EVALUATOR`. The template's five conditions are "the D-149 index
row's, verbatim in order" (`:6-7`) — the code carries them in that order and
names the same C1..C5 labels.

**C1 — READY-candidate council verdict stands.**
Inputs: a custodied `council-verdict.md` path + sha256 (template `:16-18`);
three form checks — no NOT-READY, no UNVERIFIED, ED-QUALIFICATION rows closed
(`decision_log.md:172`). Template `:44-46`: "Never infer from a draft or a
packet — only a custodied verdict counts." Mechanically: the gate requires the
file to live under a `docs/process_traces/<date>-*/` custody root, digest-pins
it, and parses its verdict-form block; a packet file or an uncommitted path
refuses. ED-QUAL closure is evaluated against the **reclassified** set per r5 S-1
(`:12-19`): `ED-QUAL-L6-1` has left the ED-QUALIFICATION class (T0/perishable)
and closes at the shakedown window's own arm row evaluation — so for
`window_class == SHAKEDOWN` it is not a member of the conjunct, and for CLAIM the
full post-reclassification set applies. Without this, amendment 10 + amendment 11
conjunct 3 make READY structurally unreachable (r5 S-1, the deadlock both cold
seats proved).
Codes: `scheduler_c1_verdict_uncustodied`, `_unparseable`, `_form_failed`
(observations: which of the three checks failed, plus the offending row ids).

**C2 — arm ceremony green, freshness honored.** Delegated: arm receipt
`status == "PASS"` (`ARM_RECEIPT_KEYS`, `arm_readiness.py:394-414`) **AND** G1
PASS. Template `:22-23` asks for volatile (20 min) and procedural (6 h) horizons
remaining at T-0; those constants are
`arm_readiness_evidence_t0.py:49-50`, selected at `:1760-1762`, and the receipt
records `mm:ss` / `h:mm` remaining for each. Per r5 V-5 (`:155-157`) the r4-6
anchor is named as `arm_readiness_evidence_t0.py:884-889`. The arm status alone
is NOT sufficient — see §0(b).
Codes: `scheduler_c2_arm_not_pass`, `_horizon_exhausted` (the latter is G1's
refusal surfaced under the C2 label).

**C3 — machine quiet.** Inputs: census artifact + sha (template `:26`), fleet
quiesced via pgrep evidence (`:27`), no interactive use / display asleep (`:28`),
single-writer attestation (`:29`). `scripts/prewindow_check.sh` supplies an
ADVISORY reading only (`:16-19` disclaimer; daemon list `:65-68`; check-8 at
`:150`). r5 S-7(a) (`:69-74`) adopts seat L8's tightened check-8 pattern
(`codex|claude|t3|mcp-server`) and records that "B-16's tightened check refuses
while any lead session runs, so it lands BEFORE ED-Q-L9-3's agent-free fixture
capture". **Consequence the gate must encode:** under the tightened pattern, C3
is unsatisfiable from inside a lead session. The gate therefore self-checks its
own process ancestry and refuses
`scheduler_c3_evaluator_context_invalid` if it finds itself under an agent
session — it must run from the no-agent driver context (the
`shakedown-driver.sh` pattern named in template `:49-52`).
Codes: `scheduler_c3_census_missing`, `_census_dirty`, `_writers_present`,
`_evaluator_context_invalid`.

**C4 — boot session + clock discipline.** Boot half = G5. Clock half: network
time OFF with attached evidence (template `:33`, `:53-54`). The admissibility
hook per r5 V-5 (`:157-158`) is `arm_readiness.py:643`:
`"CLOCK_ATTESTATION": frozenset({"OPERATOR_ATTESTATION", "PROBE"})` — PROBE is
admissible, which is what makes an unattended C4 possible at all; without it C4
would require Ed's hands and D-149 would be self-defeating.
**Executed precondition, unmet:** `sudo -n systemsetup -getusingnetworktime`
returns "sudo: a password is required" at head (VERDICT-PACKET §2(d) E-1) — a
hard precondition of any auto-GO window, not a convenience. r5 V-7 item 4
(`:174-177`) adds the discriminating probe for the *setter* verb
(`sudo -n systemsetup -setusingnetworktime off`, the verb T-0 executes,
`scripts/capture_t0_step.py:612`) because E-1's prior evidence tested GET only.
The gate probes BOTH and refuses if either is unavailable.
Codes: `scheduler_c4_clock_underivable`, `_network_time_on`,
`_privilege_absent` (with `probe: get | set` recorded — the distinction r5 V-7.4
demands).

**C5 — no-retry binding (D-078).** Template `:55-56`: "no evidence — it is the
issuer's binding acknowledgment". The gate records the acknowledgment AND
enforces its one mechanical half: if a refusal record exists for this lane and no
diagnosis record accompanies it, REFUSE re-arm. That converts "a refused capture
ends that lane with diagnosis, never re-arm-and-hope" (`decision_log.md:172`)
from prose into a gate — which is the whole point of V-5 ("prose halt triggers
are how stop signals get eaten", `MAGISTRATE-RULING-r3.md:68-69`).
Codes: `scheduler_c5_undiagnosed_retry`, `_refusal_log_unreadable`.

**VERDICT** one word, GO or NO-GO, NO-GO listing every failing condition
(template `:39`).

**FAIL-CLOSED DEFAULT** Every C-condition defaults NO-GO. A condition whose
evidence line is missing is a NO-GO by the template's own rule (`:5-6`: "a
condition without its evidence line is a NO-GO").

**TEST PINS**
1. Verdict file passed as a *packet* path → `scheduler_c1_verdict_uncustodied`.
2. Verdict with one UNVERIFIED row → `_form_failed`, naming the row.
3. SHAKEDOWN with `ED-QUAL-L6-1` open → C1 PASSES (the S-1 reclassification pin
   — without it READY is unreachable and the deadlock returns).
4. CLAIM with `ED-QUAL-L6-1` open → C1 refuses (the reclassification is
   shakedown-scoped, not a general amnesty).
5. Arm receipt PASS + expired evidence → NO-GO via C2/`_horizon_exhausted`.
6. Evaluator launched under a lead session → `_evaluator_context_invalid`.
7. `sudo -n systemsetup -getusingnetworktime` failing → `_privilege_absent`,
   `probe: get`; setter failing → same code, `probe: set`.
8. Lane with a refusal record and no diagnosis → `_undiagnosed_retry`.
9. Two conditions failing → receipt lists BOTH (the no-short-circuit pin).

---

## 3. What the gate layer does NOT do

Every threshold cites a ruling clause; the layer invents none.

| number | sole source | gate |
|---|---|---|
| T-0→arm ≤ 15 min | `MAGISTRATE-RULING-r3.md:61-62` | G2 |
| p99 arm→consume ≤ 4 min | `MAGISTRATE-RULING-r3.md:61-62` | G2 |
| 20 min volatile / 6 h procedural | `arm_readiness_evidence_t0.py:49-50` | G1, G6-C2 |
| arm-to-consume budget (G1's margin) | registry `arm_policy`, `arm_readiness.py:518,534-535` — **ED_RESERVED today** | G1 |
| projected window span | the window's run card, operator-declared | G1 |
| 168 h family horizon | r5 V-4 (`:141-151`) — an **Ed disclosure item**, deliberately NOT a code constant | none |

Explicitly out of scope:
- **No waiver, relaxation, or substitution** for the arm ceremony's own gates —
  the `prewindow_check.sh:16-19` doctrine, inherited verbatim.
- **No re-implementation** of evidence authentication, digest checking, or
  freeze replay. G1 recomputes deadlines only; everything else calls
  `arm_readiness`.
- **No severity adjudication and no promotion.** G3 stamps
  `claim_admissible: false`; it never upgrades a record (r5 S-2: "no
  retrospective promotion").
- **No self-clearing of a HALT** (G2). Rule-11 lieutenant-forbidden:
  reinterpreting a stop signal. Ed clears, with the observed numbers in hand.
- **No writes to the pack.** Gate artifacts land in the window/campaign custody
  root only — a pack write would move `committed_pack_tree_sha256` and refuse
  its own arm at `arm_readiness.py:5186-5190`.
- **No `--force`, no `--skip-gate`, no env override.** The absence of a bypass
  flag is a design commitment, testable by grep.
- **No new numbers for p99 at small n** — the max-substitution is documented as
  strictly tighter than the ruled bound, and recorded per-receipt.

---

## 4. WRITE_SCOPE + stage decomposition

**Stage 0 — this D-144 round.** r5 V-6 (`:159-164`): the scheduler mechanical
gates are a schema/contract design and get their OWN bounded co-design round
(independent seats, one debate, magistrate ruling) BEFORE implementation; no
waiver. Also: S-1..S-5 land as ONE composed merge with ONE pre-merge two-seat
pass, and the Fable ruling on its findings is the MAGISTRATE'S. No code until
this rules.

**Sequencing constraint — the freeze.** r5 V-3(c) (`:131-135`) freezes
local_main AND origin/main for the measurement span and suspends rule-7
push-promptly. Stages 1–7 therefore land **before** the freeze opens, or ride the
transaction's enumerated step list (V-3(d): "ordinary commits" = any commit not
in that list). Landing gate code mid-span would trip G4 by construction.

| stage | content | WRITE_SCOPE | gate to pass |
|---|---|---|---|
| 1 | Vocabulary + receipt schema + pure evaluator core (no I/O policy, no gate logic) | `joulewise/scheduler_gates.py`, `tests/test_scheduler_gates.py` | schema round-trip; `_gate_refusal` rejects unregistered codes (mirror of `arm_readiness.py:3626-3629`) |
| 2 | **G4 + G5** — the two whose inputs fully exist at `5bd7acf` | `joulewise/scheduler_gates.py`, `tests/test_scheduler_gates.py` | 8 pins above; G5-before-G1/G2 ordering pin |
| 3 | **G1** min-fuse, incl. independent deadline recomputation | `joulewise/scheduler_gates.py`, `tests/test_scheduler_gates.py`, `tests/test_arm_readiness_lifecycle.py` | 5 pins; **sequence with or after B-12** (`arm_readiness.py:5253-5262`, `:5385-5392`) — pin 5 is the delta-re-audit hook |
| 4 | **G2** halt bounds + `window_timing_ledger.v1` + sticky HALT record | `joulewise/scheduler_gates.py`, `joulewise/window_timing_ledger.py`, `tests/test_scheduler_gates.py`, `tests/test_window_timing_ledger.py` | 6 pins; sticky-halt pin is the anti-eaten-signal regression |
| 5 | **G3** B-22 presence + tamper probe | `joulewise/scheduler_gates.py`, `tests/test_scheduler_gates.py` | **BLOCKED** on the S-2 cure work item (r5 `:24-28`: frozen-pack binding + machine consumer, gauntleted, landing BEFORE the first claim window's close-out). Stage 5 lands red-on-arrival pins first (G3 pins 1–2 pass today), cure-effective pins after |
| 6 | **G6** D-149 checklist + CLI + doc wiring | `scripts/evaluate_window_gates.py`, `joulewise/scheduler_gates.py`, `docs/process/d149-go-receipt-template.md`, `docs/process/window-run-cards/shakedown-v3-first-light.md`, `tests/test_evaluate_window_gates.py` | 9 pins; template gains the `gate_receipt_sha256` line and the run card's precondition block (`:9-18`) names the CLI |
| 7 | Kernel/queue transaction closing `WO-D149-GO-EVALUATOR` | `docs/process/state_kernel.json`, `TASK_QUEUE.md`, `RUN_STATE.md`, `tests/test_gen_state.py` | lead-authored at the bench under kernel discipline + ONE terra-high refuter over the transaction diff (r5 S-4, `:40-47`) |

Stages 2, 3, 4, 6 are gauntlet-shaped per hard rule 9: implement under enforced
WRITE_SCOPE → independent audit → severity-tiered refuters with distinct lenses
→ fix rounds with defect-shaped regressions → **delta re-audit of every fix
round**. Stage 3 additionally requires a delta re-audit against B-12's landing,
since the two touch the same expiry predicate from opposite sides.

**Two open items this design surfaces for the magistrate, not for the
implementer:**
1. G1 cannot pass until `arm_policy.arm_to_consume_budget_ns` stops being
   `"ED_RESERVED:arm-to-consume-budget-ns"` (`arm_readiness.py:534-535`). That is
   an Ed/registry item and belongs on the V-7 packet; the gate refuses until it
   resolves, which is correct but means the gate is inert-by-refusal, not
   inert-by-silence.
2. G6-C3 under the B-16-tightened pattern makes an agent-run evaluator
   self-refusing. The gate encodes that honestly
   (`scheduler_c3_evaluator_context_invalid`), but it means the D-149 no-hands
   path requires an agent-free driver process — a topology commitment that
   should be ruled, not assumed.
