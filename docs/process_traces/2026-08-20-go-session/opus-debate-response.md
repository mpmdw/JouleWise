# D-148.5 — OPUS SEAT, DEBATE ROUND (bounded, one response)

Read `terra-reg-report.md` in full. Convergences stipulated: enumeration A; the three `_v4` ids for
V1; defer-to-`_v4`; V5 = 300 s / 300 s conditional on a measured rehearsal. Below, only the five
named divergences plus one blocker against terra's bytes that the divergence list does not cover.

All checks re-run read-only from `wtREG-O` @ `afb7d57`.

---

## 1. V2 — **CONCEDED on the token; AMENDED on where the mechanism lives**

Terra is right and I was inconsistent. My own V6 ruling refuses to install a string naming an
unbuilt mechanism; `INTERPRETER_PLATFORM_EXACT_AT_AUTHORING` is a string naming a mechanism that
exists only if my delta (d) lands. If the `_v4` transaction sheds one delta under fuse pressure —
and it is carrying four — the registry ships a lie. Applying my own principle symmetrically, the
installed token must describe what the code does at the moment the bytes land.

**Concede:** `"environment_comparison": "RECORD_ONLY"` for all sixteen EXECUTION_BOUND kinds, and
`_SUPPORTED_ENVIRONMENT_COMPARISONS = frozenset({"RECORD_ONLY"})`
(`joulewise/arm_readiness_evidence.py:117-119`), exactly as terra's diff.

I note for the record that terra's "no comparator build" framing is not the operative distinction —
terra's V2 is also a code change, at the same line. The operative distinction is **truthfulness at
install time**, and on that terra wins.

**Amend — the staleness hole must still close, outside the registry's vocabulary.** I withdraw the
claim that the comparator is registry semantics; I do not withdraw the finding that there is a real
hole. Corrected site (my §1b cited `:2090-2126`, which is the *non*-R1 path `_authenticate_existing`
at `:2047`): the R1 re-use path is **`_authenticate_existing_r1` (`arm_readiness_evidence.py:2216`)**,
dispatched at `:2362-2371` whenever the evidence namespace already exists and a lifecycle registry is
installed — i.e. on any re-run of the author during a mint ceremony. It re-checks head
(`:2248`), evidence id and kind (`:2299-2300`), class and policy — and **not** the recorded
environment fingerprint. Fresh authoring cannot be stale (`_execution_environment_fingerprint` is
derived live at `:2427-2430`), so this is the *only* way a receipt bearing a stale environment
reaches a freeze.

Fix it with a `_refuse(kind, "evidence_author_environment_changed", …)` in the author's own
**unconstrained** vocabulary (`_refuse` → `EvidenceAuthoringError`, `:240-241`), comparing the six
scalar terms already present (`interpreter`, `implementation`, `python_version`, `platform_system`,
`platform_release`, `platform_machine`, `:454-466`). The registry does not name it; the registry
still says `RECORD_ONLY`, which remains true — *the registry compares nothing*.

**Why this placement is not a quibble, and is the one thing terra's V2 costs that terra does not
price.** Per my §2 finding (uncontested by terra, and implied by terra's own B1): once `_v4`'s plan
trees and `freeze-0004` receipts pin the registry bytes, **any** later registry edit changes the
sha and forces a `_v5` family. So under terra's design as written, upgrading `RECORD_ONLY` to a real
comparison token later costs an entire pack family. Putting the mechanism in the author's vocabulary
means it can be strengthened, weakened, or extended to `sys.path` and inherited-environment terms at
any time **without touching the registry and without a `_v5`**. Terra's token choice is right;
terra's implicit assumption that the token is where the mechanism belongs would freeze the project's
only environment protection behind a family boundary.

---

## 2. V3 — **DISPUTED. Terra's 20-minute tier on freeze-time evidence recreates L1-B1 with a
20-minute fuse. I reject the compromise for the same reason.**

Answering the question directly — *is 24 h on MULTICELL_MINT defensible for claim integrity?* Yes,
and 20 minutes is not merely stricter, it is **unarmable**. Three grounds, in order of force.

**(a) The arm receipt min-inherits FREEZE evidence expirations, so a freeze-time horizon is a fuse
on the whole pack, not a freshness property of one receipt.** Verified at `afb7d57`:
`evidence_receipts.update(freeze_evidence_receipts)` (`arm_readiness.py:6145`) executes **before**
`evidence_expirations = [... for item in evidence_receipts.values() ...]` (`:6230-6234`), which feeds
`valid_until = min([evaluated_at_monotonic_ns + arm_horizon_ns, *evidence_expirations])`
(`:6240-6242`). `MINT_TRUST`, `MULTICELL_MINT`, `RECOVERY_LEDGER_TEST` and `THREE_WINDOW_REGRESSION`
are all `FREEZE_AND_ARM` rows (`desk.mint_trust`, `desk.multicell_mint`,
`desk.recovery_ledger_path`, `desk.three_window_regression`) authored at freeze time and carried
inside the freeze receipt. Under terra's tier, the pack becomes unarmable **20 minutes after the
freeze** — the freeze happens at `/Users/edr/JouleWise-measurement-20260818`, then the merge wave
lands, then the window runs. There is no version of that sequence that fits in 20 minutes.

This is not hypothetical: it is exactly the L1-B1 defect class this project has now suffered three
times, and I measured its current state myself — `_v1` −128.1 h, `_v2` −21.7 h, `_v3` +5.73 h at
2026-08-20T11:07:50Z. Terra's ruling shortens that fuse from 24 h to 20 min. Under D-078 no-retry,
that is a lost-window generator, and it would make the `_v4` family the shortest-lived of the four.

**(b) Terra's split has no anchor in the code's only source-of-truth table, and mis-sorts by its own
criterion.** `_EVIDENCE_SOURCE_KINDS` (`arm_readiness.py:639-668`) is the sole authority on what each
kind draws from. Verified: `ACCEPTANCE_OWNER`, `MINT_TRUST`, `MULTICELL_MINT`, `REASON_CODE_COVERAGE`,
`RECEIPT_ORACLE`, `RECOVERY_LEDGER_TEST`, `THREE_WINDOW_REGRESSION` are **all** `frozenset({"PROBE"})`
— byte-identical entries. Terra sends three of those seven to the 6 h "reviewed_bytes" tier and four
to the 20 m "machine_probe" tier. The distinction is an intuition, not a derivation; nothing in the
repository lets a future reader reproduce which side a kind falls on, which is precisely the property
a contract-bearing registry must have.

**(c) The physical question decides it against terra.** The right test for a horizon is *what can
change within it that would falsify the attestation.* For the T-0 volatile set the answer is
concrete — someone unplugs the mains (`POWER_PREFLIGHT`), a daemon wakes (`PROCESS_CENSUS`), the lid
opens (`MACHINE_PREFLIGHT`) — which is why 20 min is right **there**. For `MULTICELL_MINT` the
answer is: nothing on a 20-minute scale. The committed bytes are pinned by `head_commit` and
`pack_sha256` (re-checked at `arm_readiness.py:4248-4261`), the interpreter identity is pinned by
`boot_session_id` (`:4263-4270`), and dependency drift is caught by the `DEPENDENCY_CHANGED_SET` /
`DEPENDENCY_MANIFEST` gates (`:3118`, `:3130`, `:3215`, `:3234-3292`). These kinds are
**reviewed-byte proof that happens to execute on a machine**, not live machine state. Terra's tier
treats the substrate as the subject.

**Compromise explicitly rejected, and why.** The coordinator's proposal — my live/declarative split
with terra's subject tiers on the live kinds — puts `MINT_TRUST`, `MULTICELL_MINT`,
`RECOVERY_LEDGER_TEST`, `THREE_WINDOW_REGRESSION` at 20 min. All four are freeze-time generic-deriver
kinds, i.e. exactly the fatal set in (a). The compromise is the failure mode with extra steps.

**What I concede to terra.** Terra is right that "behaviour-neutral" is a process argument, not a
claim-integrity argument, and my §1b leaned on it too hard. I amend the justification: **24 h is not
a staleness allowance, it is the named length of the freeze→consume fuse**, and the ruling must say
so in those words plus the derived operational contract — *the `_v4` freeze→window consumption must
complete within 24 hours, and the fuse is the L1-B1 mechanism, now named rather than implicit.*
Shortening it does not make the evidence truer; it makes windows fail. I also adopt terra's
`OFFLINE_INPUT_INVENTORY` / `TERMINAL_REVIEW` at 6 h — we already agree there, and for the same
reason (it mirrors `_NONVOLATILE_EVIDENCE_VALIDITY_NS`, `arm_readiness_evidence_t0.py:50`).

I retain the live/declarative split. Verified again this round: `GIT_CHECKOUT` and
`PRIVILEGE_INSTALLATION` appear in the codebase **only** in the predicate→kind map
(`arm_readiness.py:912`, `:916-919`) — in no authoring lane, in neither `_GENERIC_DERIVER_KINDS`
(`arm_readiness_evidence.py:89-101`) nor `_ROW_KIND` (`_evidence_t0.py:88-103`) — so terra's 6 h and
20 m for those two, and for `DRY_RUN_REHEARSAL` / `IDENTITY_PIN_PROJECTION`, gate nothing. Terra's
bytes are not wrong there; they are silently inert, and a registry that does not mark its inert rows
will be misread by the next reader as a gate.

---

## 3. V6 — **DISPUTED. I hold `UNBUILT.v0`; I adopt terra's binding set as the specification.**

Terra's principle is mine and I accept it: *a string alone is inert; this is not permission for a
forward declaration.* That is why I ruled a token that **names its own absence** rather than
`joulewise.d117_family_publication_marker.v1`. Terra's remedy — install the real name together with
a real schema, a canonical marker file, and a consumer — does not survive three checks.

**(a) Terra's consumer has no home.** Re-verified: `grep -rn "family_publication_marker_schema"
joulewise/ scripts/` returns only the placeholder (`arm_readiness.py:543`), the key-set constant
(`:523`), and the `_require_string` loop (`:1736`). And `FAMILY_PUBLICATION` remains the **only** one
of the eight roles with no raise site anywhere (the other seven: `:2954`, `:3102`, `:3118`, `:3130`,
`:3186`, `:3201`, `:3215`, `:3234-3292`, `:3323`, `:3338`, `:4226`, `:4328-4371`, `:4574`, `:4581`,
and `arm_readiness_evidence.py:1772`, `:1780`, `:1791`, `:2295`). Publication in this project is
runsheet step 7 — a ceremony, not a code path. Terra's "consumer that refuses
`r1_family_publication`" therefore requires **inventing the publication path** inside the `_v4`
transaction. That is not a marker retrofit; it is building publication machinery on a fuse.

**(b) Terra's own ordering makes the trio unsatisfiable at install time.** Terra and I agree the
registry must land *before* `_v4` plan attachments and evidence are authored (terra B1:
*"The install must land before `_v4` plan attachments and evidence are authored"*). But terra's
marker must bind *"all three `freeze-0004` receipt references"* — and by the self-hash-cycle argument
(`06-…:82-88`, which terra does not contest) the marker can only be created **after** all pack bytes
are final. So at the moment the registry bytes are committed, the canonical marker file terra
requires cannot exist. The position is repairable — schema + consumer before, instance after — but
in its repaired form it is a forward declaration with extra machinery, which is what terra set out to
forbid.

**(c) It overturns a ratified D-147 disposition without arguing against it.** *"(1) Family-marker
particulars: `_v3` lands FIRST, machine-readable supersession marker retrofits via its own co-design
pass (both seats recommend; magistrate concurs)"* — `14-r2-ruling.md:117-120`. A registry-values
council does not get to reverse a two-seat-plus-magistrate concurrence in passing, and under
CLAUDE.local.md rule 11 reinterpreting a prior verdict is a mandatory cold-instance trigger, not a
seat's call.

**What I adopt from terra.** Terra's binding set is better specified than my ruling's and I take it
verbatim as the **specification the marker co-design pass must satisfy**: the marker binds all three
`_v4` plan-tree digests, all three `freeze-0004` receipt references, and the exact installed registry
reference — and lives outside the pack roots. I add: the ruling records that spec next to the
`UNBUILT.v0` token, so the retrofit pass inherits a written contract rather than re-deriving one.
My canary (a test asserting that while the installed string matches `*.UNBUILT.v*` no module in
`joulewise/` references the field) is what makes the token mechanically self-refuting rather than
merely honestly named — which is terra's actual demand, met at a cost the fuse can pay.

---

## 4. Outer `registry_id` and path — **CONCEDED in principle; AMENDED on the names; one addition**

Terra is right and my §2 reasoning was stale by one step. My grounds for keeping both were file 09
§5d: whole-dict equality over `{registry_id, path, sha256, plan_profile}` (`arm_readiness.py:319`,
`:1349-1358`) means `path` and `registry_id` each break the frozen family independently. But that
argument preserves `_v3`'s ability to arm at the live head — and `_v3` is dead at the live head by
two independent mechanisms I documented myself (the byte-pin, and `V1_GRANDFATHERING` at `:4219-4229`
against 11 of the 12 PACK-namespace items in each `freeze-0003.json`). Once F3 fixes `_v3`'s replay
coordinate at the pre-install commit, **nothing at the `_v4` boundary is pinned to the old id or
path**: `_v4`'s plan trees are built from live bytes at mint time (`:2900`) and its receipts pin
whatever the new values are. **Concede the rename.**

**Amend the names.** I dispute terra's specific `d117-row-registry-r1`: `r1` names the *ruling*, not
the *schema generation*, and reintroduces the legibility trap in a new form the moment an R2-era
registry exists. Since we are paying the rename cost anyway, pay it for legibility:

```
outer registry_id : "d117-row-registry-v2"     (matches joulewise.arm_readiness_row_registry.v2)
file path         : configs/arm_readiness/d117_row_registry_v2.json
inner registry_id : "d117-r1-lifecycle-v1"     (mine; terra's d117-r1-lifecycle-registry-v1 is
                                                equally fine — I do not contest it)
```

**Two conditions the rename carries.** (i) `ROW_REGISTRY_RELATIVE_PATH` (`:80`) is a code constant;
the path change is a **code delta in the same commit**, and its four uses (`:2509`, `:2768`, `:2778`,
`:2900`) move with it. (ii) The literal string is referenced across the repo — verified: six test
modules (`tests/test_arm_readiness_registry.py`, `…_schemas.py`, `…_lifecycle.py`, `…_integration.py`,
`…_evidence_t0.py`, `test_d117_decode_contrast_plan.py`), `docs/decision_log.md`, three
`docs/phase_2/*_arm_readiness.md`, `docs/phase_2/window_runbook.md`, and several run reports and
council traces. That is a consistency-sweep item with a real footprint and it belongs in the
transaction's step list, not discovered at merge.

**Addition to terra's F3 that the rename makes possible and necessary.** Terra's F3 preserves a
*commit* as `_v3`'s replay coordinate. Because we are moving the v2 registry to a new filename, the
old file can simply **stay in the tree at the new head, unreferenced by code**, as `_v3`'s archival
companion — with a test pin asserting its sha is still
`d248fdc521cb904b7ad8f1c4ecb834f7810a1d8f39697b462591f2feac39a2e5` (re-verified this round). A
preserved file with a pinned digest is a stronger custody object than a commit sha in prose: it
cannot be lost to a rewrite, and the pin fails loudly if anyone touches it. This is strictly better
than either seat's original position and it is only available *because* we rename rather than
overwrite.

---

## 5. F3 and the V5 condition — **F3 ADOPTED with one amendment; the V5 conditions are not rivals,
they measure different parameters and BOTH bind**

**F3 — adopt.** It is correct, it is the named consequence my §2 hazard list only gestured at, and it
is the rule that makes the rename in §4 safe. **One amendment, without which the rule is unusable:**
terra says "the prior registry commit/check-out". The checkout must be *named*, because file 09 §3
established that `_pack_identity` pins `"pack_root": str(pack_root.resolve())` — an **absolute** path
— so the `_v3` packs authenticate **only** at `/Users/edr/JouleWise-measurement-20260818`. F3 must
therefore read: *`_v3` replays only at commit ⟨pre-install sha⟩ checked out at
`/Users/edr/JouleWise-measurement-20260818`; any other location yields
`readiness_freeze_receipt_mismatch` and must not be misread as pack corruption.* Both coordinates or
the rule fails in practice.

**V5 — synthesis, and a naming trap the ruling must call out.** Terra has attached a correct
measurement to the wrong parameter, and I omitted terra's. Trace both gates:

- `validate_r1_temporal_budget` (`:3299-3341`) compares `earliest TIME_BOUND deadline − now_at_arm`
  against `arm_to_consume_budget_ns`. TIME_BOUND deadlines are stamped at T-0 authoring as
  `t0_author_time + 20 min`, so the quantity gated is `20 min − (T-0→arm gap)`. Requiring ≥ 5 min
  **is** my condition: **T-0→arm ≤ 15 min.** The gate never looks at the arm→consume gap at all.
- The arm→consume gap is gated elsewhere: `consumption["consumed_at_monotonic_ns"] >
  arm["valid_until_monotonic_ns"]` → `launch_binding_mismatch`, *"consumption occurred after the arm
  validity horizon"* (`:7910-7914`), where `valid_until` is capped by `capability_horizon_ns`
  (`:6235-6242`). Terra's **p99 arm→consume ≤ 4 min with 1 min margin** is exactly the right
  condition — for `capability_horizon_ns`.

So both conditions are adopted, one per parameter, and neither substitutes for the other. The ruling
must additionally record that **`arm_to_consume_budget_ns` does not measure the arm→consume gap** —
its name is actively misleading, it is the *minimum remaining T-0 evidence life required at arm*, and
two seats independently reached for the wrong measurement because of the name. That misreading in
production is a lost window.

---

## 6. Not on the divergence list, but terra's V4 bytes are executably non-installable

Flagged once, not relitigated: terra's `r1_*` codes fail `_validate_refusal` (`:1434-1443`). Executed
this round and last: `r1_class_mismatch` → `readiness_schema_invalid: .code is not closed`. Registry
codes reach receipts via `EvidenceLifecycleError.refusal()` (`:982-988`) → the receipt's `refusals`
list, which closes both `code ∈ READINESS_REASON_CODES` and `type == REASON_TYPE_BY_CODE[code]`.
Terra's V4 is installable **only** with my finding-(C) delta (four new typed frozensets unioned into
`READINESS_REASON_CODES` + `REASON_TYPE_BY_CODE`, plus the registry-side closure check at
`:1768-1780`). Given that delta must land, prefer `readiness_r1_*` spellings so the R1 codes stay
inside the one `readiness_*` vocabulary the census already partitions; terra's `LIFECYCLE` typing of
`DEPENDENCY_CHANGED_SET` / `DEPENDENCY_MANIFEST` over my `POLICY` is a coin-flip and I yield it.

---

## FINAL AMENDED POSITION

1. **§1a counting** — AGREED (enumeration A; `successor_pack_ids` a reopened sixth). I retain the
   mechanical 15-site enumeration as the ruling's operative form; terra does not contest it.
2. **V1** — AGREED: the three `_v4` ids.
3. **V2 token** — CONCEDED to terra: `RECORD_ONLY` + `_SUPPORTED_ENVIRONMENT_COMPARISONS =
   frozenset({"RECORD_ONLY"})`. My token was inconsistent with my own V6 principle.
4. **V2 mechanism** — AMENDED (new): the re-use environment check ships in the same transaction at
   `_authenticate_existing_r1` (`arm_readiness_evidence.py:2216`) as an *unregistered* `_refuse`, so
   it is strengthenable later without a registry edit — which post-`_v4` costs a `_v5` family.
5. **V3 ten live freeze-time kinds** — DISPUTED (24 h stands). Terra's 20 m tier makes the pack
   unarmable 20 min after freeze (`:6145` → `:6230-6242`), recreating L1-B1 on a shorter fuse; and
   the split has no anchor in `_EVIDENCE_SOURCE_KINDS` (`:639-668`), which types all seven of those
   PROBE kinds identically. Coordinator's compromise rejected: it contains the fatal four.
6. **V3 justification** — CONCEDED: "behaviour-neutral" is insufficient; the ruling states 24 h as
   the *named freeze→consume fuse length* with its operational contract.
7. **V3 T-0 tiers + the two 6 h EXECUTION_BOUND kinds** — AGREED with terra.
8. **V3 live/declarative marking** — DISPUTED (retained): four kinds have no authoring lane
   (`:912`, `:916-919` only); an unmarked inert row will be read as a gate.
9. **V4** — DISPUTED against terra's bytes: `r1_*` fails `_validate_refusal` (`:1434-1443`),
   executed. Use `readiness_r1_*` + the four-part code delta. Terra's `LIFECYCLE` typings: yielded.
10. **V5 values** — AGREED: 300 s / 300 s, nested by the derived identity budget == capability horizon.
11. **V5 conditions** — SYNTHESIS: both bind — T-0→arm ≤ 15 min gates `arm_to_consume_budget_ns`;
    terra's p99 arm→consume ≤ 4 min gates `capability_horizon_ns` (`:7910-7914`).
12. **V6** — DISPUTED (hold `…marker.UNBUILT.v0` + canary): terra's consumer has no publication path,
    its marker cannot exist at install time by terra's own ordering, and it reverses D-147's ratified
    retrofit (`14-r2-ruling.md:117-120`) — a rule-11 cold-instance trigger. Terra's binding set
    ADOPTED as the retrofit pass's written spec.
13. **Outer registry id + path** — CONCEDED to terra in principle (F3 dissolves the constraint);
    AMENDED to `d117-row-registry-v2` / `d117_row_registry_v2.json`; carries a `:80` code delta and a
    ~15-file consistency sweep.
14. **F3** — ADOPTED, amended: the replay coordinate must name **both** the pre-install commit and
    `/Users/edr/JouleWise-measurement-20260818` (absolute `pack_root` pin, file 09 §3); plus keep the
    old registry file in-tree with its sha `d248fdc5…39a2e5` pinned as `_v3`'s archival companion.
15. **Install timing** — AGREED: defer to the `_v4` boundary; and the fuse I measured (+5.73 h at
    2026-08-20T11:07:50Z) has since shortened, so the choice is closing on its own.
