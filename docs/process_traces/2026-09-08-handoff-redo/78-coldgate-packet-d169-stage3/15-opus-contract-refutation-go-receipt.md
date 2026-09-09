# Opus contract-lens refutation — seat-1 GO-receipt contract (D-176)

Read-only, worktree `/Users/edr/code/JouleWise-wt-d176` at `bfedd6fa` (install part 2). Target:
`docs/contracts/pack_night_go_receipt.md`. Authorities: `13-magistrate-synthesis.md` (ruling of record),
`10-coldgate-fable-ruling.md`, `11-coldgate-opus-refutation.md`, `docs/decision_log.md:11161`. Ordered test
run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness tests.test_gen_state` →
**75 tests, OK**.

## Findings

| id | sev | file:line | defect | demonstrating command |
|---|---|---|---|---|
| B1 | blocker | `joulewise/night_gate.py:106-121`, `:203` | The contract anchors C1/C5 on "sha256-bound into the pack-night plan" (§4:250, §5:290, §2:131,145) and on "the plan's attempt identifier" (§8.2:427). The live plan schema is exact-key and holds **none** of `pack_id`, `pack_sha256`, `authorization_record_sha256`, `confirmation_record_sha256`, `attempt_ordinal`. The contract never names `_PLAN_KEYS`, never says the plan schema is extended, and assigns that work to no seat. Every "bound into the plan" clause is unimplementable and unowned. | `sed -n '106,121p;200,206p' joulewise/night_gate.py` |
| B2 | blocker | `joulewise/arm_readiness.py:8975-8992` | §3:230-232 "Put v2 into the legacy branch [of `validate_consumption_receipt`]: it may replay historically only with `require_current_boot=False`." Wrong site and wrong effect. `_read_v2_consumption` refuses any `schema_version != CONSUMPTION_RECEIPT_SCHEMA` **unconditionally** (`:8989-8992`), before `require_current_boot` is consulted — so after the v3 flip, v2 historical replay is refused, contra the ruling. And the legacy branch validates against `LEGACY_CONSUMPTION_RECEIPT_KEYS` (8 keys, `:670-679`), not v2's 20 (`:681-702`); routing v2 there fails exact-keys. A third key-set constant and a boot-conditional schema gate are required and unspecified. | `sed -n '8975,8995p;670,702p' joulewise/arm_readiness.py` |
| B3 | blocker | `joulewise/arm_readiness.py:1048-1062`, `:223-231`, `:1103-1112` | The consumer raises `ArmReadinessError` throughout, and that class refuses any code outside the frozen `READINESS_REASON_CODES`. §3:186-203 registers `launch_go_receipt_missing/_invalid` in `LAUNCH_LINEAGE_REASON_CODES` — i.e. `LaunchLineageError` codes — but never says which exception type `_consume_launch_capability` raises for GO failures, nor that `scripts/launch_window.py` must catch both. | `python3 -c "import sys;sys.path.insert(0,'.');from joulewise.arm_readiness import ArmReadinessError; ArmReadinessError('launch_go_receipt_invalid','x')"` → `ValueError: unregistered readiness reason code` |
| B4 | blocker | contract §6:329-335 vs `joulewise/t0_rehearsal.py:38,50,88-95` | G7 requires presenting a `T0_UNATTENDED_SUPERVISED_REHEARSAL`-class receipt "in the existing rehearsal schema" and preserving a refusal "with the class in `detail`". That object is `joulewise.t0_unattended_rehearsal_receipt.v1` with six keys; under §2's exact-key GO schema it dies on `schema_version` before any class check, so the demanded `detail: <class>` is unreachable. No check ordering is ruled, the "existing rehearsal schema" is never named, no artifact (path/schema/producer) is defined for "records the class refusal", and "the absence of any `.consumed.json` and capture" leaves *capture* dangling. | `sed -n '36,52p;86,96p' joulewise/t0_rehearsal.py` |
| B5 | blocker | contract §3:161-181; `joulewise/arm_readiness.py:9575-9587` | §3 orders the callee to "re-read and re-digest the confirmation and authorization records", but adds only three keywords (`go_receipt`, `authenticated_go_receipt`, `go_receipt_sha256`) and stores no locator for either record: GO carries `confirmation_record_sha256` and `authorization.sha256` (digests only); v3 `step6_confirmation` carries the *table* path, not the record's. The callee has no path to read. | `grep -n "confirmation_record_sha256\|authorization" docs/contracts/pack_night_go_receipt.md` |
| S1 | should-fix | `joulewise/arm_readiness.py:9748`, `:9486` | §6's rehearsal predicate needs an authenticated window id; §2:108-110 says only "authenticated through the pack and existing launch context". The actual authenticated source is `receipt["pack"]["window_id"]` (consumer `:9748`, replay `:9486`). Name it. | `sed -n '9744,9750p' joulewise/arm_readiness.py` |
| S2 | should-fix | `joulewise/night_gate.py:738-746` | `TRANSACTION_PACK` is refused unconditionally ("stage 3 not implemented"). No contract clause and no seat's write scope names this line as the fence to lift; seat 2's scope as written (`run_night.py` producer + orchestration) cannot make a pack night run. | `sed -n '736,748p' joulewise/night_gate.py` |
| S3 | should-fix | `joulewise/night_gate.py:122-136` | Two condition shapes now exist: night_gate's `_RECEIPT_KEYS`/`_CONDITION_KEYS` (`{condition_id,status,basis,evidence,measured}`, `_STATUSES`, `_VERDICTS`) and GO's three-key condition (§2:149). The contract never states whether GO supersedes, wraps, or coexists with the night-gate receipt, nor reuses `_CONDITION_IDS`/`_STATUSES`. | `sed -n '122,136p' joulewise/night_gate.py` |
| S4 | should-fix | contract §6:322-325 | "disjoint from an independently established census of production roots" — the census artifact, its producer and its schema are unnamed. G6 consumes `bundle.production_roots` (`t0_rehearsal.py:779-787`); the consumer has no bundle. Consumer-side "disjoint roots" is unimplementable as stated. | `sed -n '775,788p' joulewise/t0_rehearsal.py` |
| S5 | should-fix | `joulewise/arm_readiness.py:9796-9800` | The child route (§5:298-302) reads `step6_confirmation` from the v3 record, but `_lifecycle_receipt_path` resolves through `_read_v2_consumption`, which B2 shows refuses non-v2. Not named in the contract or in any seat's scope. Also: no refusal code is named for a v2 record on live replay. | `sed -n '9796,9802p' joulewise/arm_readiness.py` |
| S6 | should-fix | contract §2:123,147 | `t0_evidence` membership is "Fifteen `ARM_ONLY` receipts plus capture-step records… authenticate its pack/attempt membership" — the capture-step count is open, no set digest is carried, and the membership predicate is a gesture. A seat cannot decide when the array is complete. | `grep -n "t0_evidence" docs/contracts/pack_night_go_receipt.md` |
| N1 | nit | contract §2:133 vs §5:288 | `issued_epoch_s` typed `number` while `confirmed_at.epoch_s` is `float`; `status` vocabulary not enumerated (`_STATUSES` exists); condition ordering/duplicate rules unstated under an otherwise exact-key regime. | — |
| N2 | nit | `joulewise/arm_readiness.py:2542-2554`, `:377` | The absolute `go_receipt.path` is consistent with `_validate_launch_artifact_reference` (absolute) and deliberately unlike `arm_receipt.path` (relative, `FREEZE_REFERENCE_KEYS`); §8.3:456 flags the difference. No constant name is proposed for the six-key `go_receipt` set. | — |

## Per-question evidence

**1. Fidelity — clean.** All six synthesis decisions are installed. The judge's 23 top-level keys appear verbatim
in §2's table; the only departures are the two the magistrate ruled in §8 — `receipt_id` added (§8.1) and the
scalar `authorization_record_sha256` replaced by `authorization {sha256, purpose, attempt_id, claim_eligible}`
(§8.2). The eight consumer conditions of judge §1:11 (ARM id+sha, pack digest, boot session, three launch
digests, `verdict == GO`, five PASS, `receipt_class`, `now ∈ [issued, valid_until)`) are all present at §3:172-177.
Authorization's seven keys = judge §2:17 six plus ruled `attempt_id`. Confirmation's four keys and the purpose
table match judge §3/§2. v1 retirement, "no second lock", G2-a discharging nothing, `DIAGNOSTIC_NO_PACK`
rejection, R-8's three steps, the verbatim replay list plus additions (a)–(c) and F6's omission regression are all
carried. **No drift, no omission, no invented key.**

**2. Exact-key discipline — GO/authorization/confirmation yes; consumption no.** §8.3:459-462 states the closed-set
rule and every table is typed, matching `_require_exact_keys` style. The consumption schema fails: §3:208-216 lists
one key set and says "set `schema_version` to v3, and add exactly these two fields", i.e. it *mutates* the single
`CONSUMPTION_RECEIPT_KEYS`. A v2 record then fails exact-keys in the non-legacy branch and fails again in the legacy
branch (8-key v1 set). Answering the question directly: **live v2 → refused (correct, but by `_read_v2_consumption`
`:8989`, not by the ruled mechanism); historical v2 with `require_current_boot=False` → also refused** (B2). The
ruling is not satisfied by the text.

**3. Strongest attack — authorization swap after plan freeze.** Write a second 0600 authorization in custody with
`purpose=CAMPAIGN_TRANSACTION`, `claim_eligible=true`, the same `pack_sha256` and `permitted_chain_sha256`, and a
plan naming its digest; the producer copies those fields honestly, GO self-consists, and the consumer's re-digest
of "the authorization record against `sha256` and the plan" (§2:145) passes. The only refuser is the plan's
immutable binding — which B1 shows does not exist in the plan schema and is not covered by any named digest. If
the intent is that the plan is inside the frozen pack and therefore covered by `pack_sha256`, the contract must
say so; it never does. **Gap, not refusal.** The other three attacks are refused: forged GO must name an ARM that
itself replays PASS/GO (`arm_readiness.py:9650-9682`); replayed GO loses the `O_EXCL` write and a fresh ARM has a
fresh `receipt_id` (`:9773-9781`); CLI-then-callee mutation is caught by the callee's own read/compare
(`:9662-9677`) plus §8.1's `receipt_id`+digest pair at replay.

**4. Consumer placement — correct.** §3:161-167 places the three keywords on `_consume_launch_capability` with the
existing `_MISSING_LAUNCH_CONTEXT` sentinel (mirrors `:9575-9587`, `:9593-9600`), §3:169-183 puts re-read, re-digest
and drift refusal inside the callee (mirrors the ARM pattern at `:9662-9677`), replay goes through
`verify_consumed_launch` (`:9451-9495`), the ARM `O_EXCL` write stays the sole one-use point (§3:240-245 ≙
`:9770-9781`), and §3:183 plus clause-map row `:511` explicitly forbid a CLI-only check. The one placement omission
is B5's missing locators.

**5. Rehearsal/G7 — incomplete.** §6:324-326 gives two of four cells: prefixed + non-`T0_REHEARSAL` → refuse;
`T0_REHEARSAL` accepted only on prefix with disjoint roots. Unprefixed + `T0_REHEARSAL` → refuse is only *implied*
by "ONLY", never written as a row with a code; prefixed + `T0_REHEARSAL` + non-disjoint roots has no code and no
mechanism (S4). G7's artifact is not unambiguous: B4 makes the demanded `detail` unreachable and no evidence file,
schema or location is named for "records the class refusal".

**6. Replicability — no.** Undefined or unbuilt at first use: **the plan** (an authority from §2:118 onward; never
given a file, schema, digest or authentication route — B1); **`attempt_ordinal`** ("the driver's integer counter",
§1:36 — no persistence, so replay cannot recompute it); **transaction custody root** vs the code's
`window_custody_root`/`custody_pack_root` (`:9683-9689`) — the resolution rule for §8.3's relative evidence paths
is unstated; **disjoint roots** (S4); **capture** (§6:334); **namespace** (used §7:388, defined §7:376). Gesture
clauses a seat cannot implement: "authenticate its pack/attempt membership and underlying evidence" (§2:147),
"authenticate the referenced evidence… and condition semantics" (§2:146), "the independently held launch context"
(§3:171). No literal "as appropriate" appears.

## Verdict

**LAND-WITH-FIXES** (docs-only PR). Required before landing: B1, B2, B3, B4, B5 as a ruled §10 addendum (or §8.4),
plus S1–S6. The contract is faithful to the ruling and its enforcement placement is right; what is missing is the
half of a wire contract that names *where in this code base* each binding lives.

CODE SCOPE MAY BE ISSUED: **no** (B1 leaves the C1/C5 root of trust — the plan — undefined and unowned; B2/B3/B5
each name work no seat can perform from the text; B4 makes seat 4's G7 acceptance unreachable as written).
