# `_v4` FAMILY TRANSACTION PLAN — independent design seat (Opus)

Base: read-only worktree at `5bd7acf`-descendant `1d7db83`, tree == main.
Citations are repo-relative to `/Users/edr/code/JouleWise/` (content-identical
to the worktree I read); line numbers verified in this tree.

Authority folded: r1 `MAGISTRATE-RULING.md` R-1..R-6 as amended by r2 A-1..A-6
and r3 B-1..B-8, plus the four cold conditions in `cold-delta-verdicts.md`.

---

## 0. HEADLINE (read this before the arithmetic)

Two findings, both executed against code, both dispositive:

**(i) The envelope does not fit, and not by a little.** The fuse is 24 h from
EVIDENCE AUTHORING (not from mint) — verified from the live `_v3` artifacts,
below. Three claim windows are 17.93 h of pure in-window occupancy. Under the
ratified one-window-per-quiet-night shape the last arm lands at T+74 h. The
24 h horizon fails before ALPHA is even armed. r3 B-5's expectation ("expected
to recommend a pre-mint horizon raise") is confirmed and is not optional.

**(ii) A THIRD install blocker that the council did not find, and it is fatal
as ruled.** `irrelevant_path_allowlist: []` (§1c, r1, ratified through r3)
makes the `_v4` family **structurally unarmable**. `_r1_changed_paths` is a
whole-repository `git diff --name-only derivation_commit..current_head`
(`joulewise/arm_readiness.py:3105-3113`), and `relevant = set(changed_paths) -
allowlist` refuses on ANY residue (`:3210-3218`). The transaction's OWN mint
commits — plan-tree regen ×3, identity-pin projection ×3, freeze-0004 ×3, all
committed at the measurement checkout per
`docs/process/ed-s5-mint-decision-2026-08-19.md:36-46` — sit between the
evidence's `derivation_commit` and the arm-time HEAD. With an empty allowlist
the first evidence item refuses `DEPENDENCY_CHANGED_SET`, and per r1 R-4.1's
own finding that error escapes `_freeze_evidence_for_arm` uncaught
(`:6139-6141`) rather than becoming a refusal record. The repo's own test
fixtures prove the shape: they must pass `allowlist=("pack/plan_tree.json",)`
to get an evidence item past this gate
(`tests/test_arm_readiness_evidence.py:404,419`).

The §1c reasoning for `[]` — *"the strictest value and the behaviour-neutral
one: there is no allowlist in force today, so an empty list changes nothing"*
(`docs/process_traces/2026-08-20-go-session/opus-reg-report.md` §1c) — is true
only because the gate has never run: no v2 registry has ever been installed,
so `lifecycle_registry is not None` has never been true in production. `[]` is
behaviour-neutral exactly until the moment it is not.

This is §(e). It is what I refuse to proceed without.

---

## (a) ENVELOPE ARITHMETIC

### a.1 The fuse mechanism, established from artifacts (not from prose)

| Fact | Evidence |
|---|---|
| For the 16 `EXECUTION_BOUND` kinds the deadline is `now + policy["horizon_ns"]` **read from the registry**, stamped at authoring | `joulewise/arm_readiness_evidence.py:1961-1962`, `:2436` |
| So the horizon is a pure registry value pre-mint — no code delta to change it | same; `arm_readiness_evidence.py:42` `_EVIDENCE_VALIDITY_NS` is the **v1 / non-EXECUTION_BOUND** path only (`:2421`) |
| Refusal at arm when past deadline | `arm_readiness.py:3376-3386` (`validate_r1_class_lifecycle`) |
| The pack inherits the **minimum** deadline over all evidence | `arm_readiness.py:6230-6242` |
| Reboot kills it independently of any horizon | `arm_readiness.py:4263-4270`, `:3380-3381`; boot id at `:1075-1102` |
| **The clock starts at AUTHORING, not at mint** | `_v3` PACK evidence `issued_at_utc = 2026-08-19T16:51:33.551326Z` (all 11 items, `configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.evidence/*.json`); freeze-0003 minted `2026-08-20T00:28:59Z` — **7.6 h later**; the recorded death time is `~2026-08-20T16:51:33Z` (`docs/process/ed-s5-mint-decision-2026-08-19.md:46`) = authoring **+ exactly 24 h**. The magistrate's independently measured "+5.41 h at ~11:27Z" lands on the same instant. |

Corroborated on the previous family: `_v2` evidence `2026-08-18T13:26:14Z`,
freeze-0002 `2026-08-18T13:29:16Z` (**3 min 02 s** authoring→mint — the
achievable latency), and the ruling's "`_v2` is 21.7 h dead at 11:07Z" resolves
to `2026-08-19T13:22Z` ≈ authoring + 24 h.

**Consequence the ruling does not state:** every hour between authoring and the
LAST arm is fuse burn, including Ed's step-6 turnaround, the canonical suite,
and all preceding windows. `_v3` burned 7.6 h of its 24 h before it was even
minted.

**The binding instant is the LAST ARM, not the last consume.** After arm, the
receipt's own `valid_until = min(now + capability_horizon_ns, *evidence
deadlines)` (`:6240-6242`) governs, and consume is a single instant checked at
`:7910-7914`. GAMMA's 5.17 h of running is therefore outside the fuse. But note
the trap: if the fuse has < 300 s left at arm, `valid_until` collapses to the
fuse deadline and the arm→consume budget silently shrinks — the V5 misreading
hazard the ruling recorded, in its live form.

### a.2 The terms

| # | Segment | Duration | Source |
|---|---|---|---|
| T1 | Evidence authoring ×3 packs | 0.25 h (planning-grade; unmeasured) | 50 s spread across the three `_v3` calls; `docs/strategy/2026-08-14-70h-plan.md:22-23` cites "~15 min author+re-freeze" |
| T2 | Plan-tree regen ×3 + commits | 0.10 h | mechanical |
| T3 | Identity pins ×3 + freeze-0004 ×3 + commits | 0.10 h **executable**, but see P3 | "~5 minutes", `ed-s5-mint-decision:26`; `_v2` did 3 min |
| T4 | Receipt verification, landing pull, push | 0.30 h | |
| T5 | Canonical FULL GREEN at published head | **0.78 h** (46.7 min) | `docs/process_traces/2026-08-19-prep-sprint/canonical-4597ad4.log:550` (2802.7 s / 3759 tests) |
| **T6** | **Ed step-6 exact-byte confirmation** | **UNBOUNDED** | r3 B-5(a); see a.3 |
| T7 | Marker instance build + validate + publish | 0.30 h | A-1 option (a) fuse-bound remainder per B-7 |
| T8 | Shakedown window (D-139 shakedown-first) | 1.25 h | 31 min executed wall clock (`docs/run_reports/2026-08-18-t10-session.md:828-859`) + up to 45 min `prewindow_check.sh --wait` dwell (`docs/process/rehearsal-operator-card.md:71`) |
| T9 | Inter-window turnaround ×3 (custody close, re-quiesce, T-0 re-author incl. ED-FIRST terminal review, arm) | 1.0 h each = 3.0 h | unmeasured; `05-arm-to-consume-budget.md:164-170` records that the arm→consume gap **has never been measured** |
| T10 | ALPHA | **6.28 h** (376.8 min) | `configs/campaigns/d117_floor_qwen25_1p5b_v3/plan_tree.json:982-991`; ratified `docs/decision_log.md:8917-8920` |
| T11 | BETA | **6.48 h** (388.8 min) | `configs/campaigns/d117_floor_qwen25_7b_v3/plan_tree.json:983-992` |
| T12 | GAMMA | **5.17 h** (310.0 min) | `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/plan_tree.json:941-967` |

Three-window occupancy = **17.93 h**. (The cold refuter's F6 "~12.8 h+" omits
GAMMA; the correct figure is 17.93 h, and the 70 h plan's "~19.5 h" is the
closer prior — `docs/strategy/2026-08-14-70h-plan.md:112`.)

### a.3 Modelling T6 explicitly (r3 B-5 requires this)

Ed's step-6 turnaround cannot be budgeted from any recorded number, so model it
from the only precedent that exists: the `_v3` confirmation table was completed
2026-08-19 evening and the exact-byte confirmation is **still owed** — it sits
in the "Other accumulated Ed-owed" list at
`docs/process/ed-s5-mint-decision-2026-08-19.md` tail, >12 h later and
undischarged at the time of this design. Combined with D-149's explicit
retention of "claim publication, exact-byte confirmation" as Ed's
(`docs/decision_log.md:172`) and rule-11's batching posture, the honest model is:

- **best case** 0.5 h (Ed is at the loop when the packet lands)
- **modal case** 8–12 h (overnight-shaped, the r3 B-5 wording)
- **observed case** > 12 h and open

T6 is not a tail risk. It is the largest single term.

### a.4 Does it fit? NO. Two cases.

**Case A — the theoretical minimum (one continuous no-reboot span, all three
windows back to back, zero weather):**

```
T1..T5 = 0.25+0.10+0.10+0.30+0.78            =  1.53 h
T7+T8                                         =  1.55 h
T9 ×3                                         =  3.00 h
T10 + T11 (before GAMMA's arm)                = 12.76 h
                                     subtotal = 18.84 h + T6
```

24 h − 18.84 h = **5.16 h of total allowance for T6**, and only if the machine
runs 18.8 h locked-quiet with no reboot, no interactive use, no refusal (D-078:
a refused capture ENDS that lane — `docs/decision_log.md:172` C5), and Ed
answers step-6 inside five hours. Under the modal T6 this overruns by 3–7 h;
under the observed T6 it is already dead. And "18.8 continuous locked hours on
Ed's daily-driver M3 Max" is not a schedule anyone should sign.

**Case B — the ratified shape (one window per quiet night;
`docs/strategy/2026-08-14-70h-plan.md:71-92`; hard block chain
`TASK_QUEUE.md:534-536`, ALPHA→BETA→GAMMA):**

```
D0 night   transaction + T6 + publication + shakedown
D1 night   ALPHA   arm at ≈ T_a + 26 h   ← ALREADY PAST 24 h
D2 night   BETA    arm at ≈ T_a + 50 h
D3 night   GAMMA   arm at ≈ T_a + 74 h
```

**24 h fails at ALPHA's arm — before a single claim datum is collected.**

Add D-078 weather (one refused night per lane, re-run "inside the span",
`70h-plan.md:112-116`): last arm at ≈ T_a + 146 h.

### a.5 PRE-MINT HORIZON-RAISE PROPOSAL TO ED

Per r3 B-5 the stagger is struck (partial family publication) and the only
lawful lever is a pre-mint raise. Mechanically it is a **pure registry value**
— `horizon_ns` is read from the registry at authoring
(`arm_readiness_evidence.py:1961`), so no code delta and no `_v5` if taken
before mint. Council-gift now, `_v5`-priced after.

> **PROPOSAL: raise the TEN generic freeze-time `EXECUTION_BOUND` kinds from
> 86_400_000_000_000 ns (24 h) to 604_800_000_000_000 ns (168 h / 7 days).**
> Policy id `r1.execution_bound.generic_168h.v1`.

Scope is exactly the ten: `ACCEPTANCE_OWNER, ACCEPTANCE_SUCCESSOR,
ESTIMATOR_IDENTITY, MINT_TRUST, MULTICELL_MINT, PACK_AUTHENTICATION,
REASON_CODE_COVERAGE, RECEIPT_ORACLE, RECOVERY_LEDGER_TEST,
THREE_WINDOW_REGRESSION` (`arm_readiness.py:676-706` minus the four B-2
no-lane kinds minus the two T-0 kinds). **The four B-2 kinds stay at 24 h**
(`r1.execution_bound.no_r1_lane_24h.v1` — nothing consumes them in a lane).
**The two T-0 kinds (`OFFLINE_INPUT_INVENTORY`, `TERMINAL_REVIEW`) stay at
6 h** — their deadlines are stamped by `_NONVOLATILE_EVIDENCE_VALIDITY_NS`
(`joulewise/arm_readiness_evidence_t0.py:50`, dispatch `:1758-1768`), which the
registry cannot override; raising them would manufacture exactly the drift the
V3 consistency assertion exists to catch.

**Why 168 h and not more or less.**
- Clean Case-B last arm = T+74 h → 94 h spare.
- Full-weather last arm = T+146 h → 22 h spare.
- 96 h (4 days) covers clean only, zero weather. I do not recommend it: under
  D-078 one refused window costs a full night and a blown fuse costs a `_v5`
  family.
- Above 168 h buys nothing: Ed's daily-driver MBP will not go 7 days without a
  reboot, and the **boot binding** (`arm_readiness.py:4263-4270`) then becomes
  the operative fuse — which is the correct place for it, because a reboot is a
  true invalidation event and a clock is only a proxy for one.

**FRESHNESS COST, stated exactly.**

What the 24 h number buys is a blanket staleness bound on facts that have no
other detector. Four detectors do **not** relax at 168 h:

1. **Changed-set gate** — `_r1_changed_paths` refuses on any relevant path that
   moved between `derivation_commit` and arm-time HEAD (`:3207-3218`). For
   everything in-tree this is strictly stronger than any time bound.
2. **Boot binding** — any reboot invalidates (`:4263-4270`, `:3380-3381`).
3. **Per-window T-0 re-derivation** — 20 min volatile / 6 h nonvolatile,
   code-pinned (`arm_readiness_evidence_t0.py:49-50`). Machine state, clock,
   census, power, ledger are all re-derived at every single window regardless.
4. **B-1's `EXECUTION_ENVIRONMENT_FINGERPRINT_EXACT_AT_REUSE`** at authoring
   re-use (`arm_readiness_evidence.py:469-472`, `:2216`).

The residual the raise actually exposes is narrow: a fact the evidence asserts
that is (i) outside the git tree, (ii) not the boot session, (iii) not in the
environment fingerprint, and (iv) not re-derived at T-0. Concretely that is the
acceptance artifact and the estimator-pinned files where they resolve outside
the pack tree, plus OS-level settings absent from the fingerprint. 24 h → 168 h
widens the undetected window for that class from one day to seven.

**Countermeasure that makes the trade approximately free** (ship it with the
raise, in the GO-receipt template so it is mechanical, not prose): every
window's GO receipt re-derives and compares the live sha of the acceptance
artifact against the frozen pin (r6 =
`0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d`,
`ed-s5-mint-decision-2026-08-19.md` confirmation table) and of
`ESTIMATOR_IDENTITY`'s pinned files. Seconds per arm; it re-pins the only class
the time bound was covering. **With it, 168 h is strictly safer than today's
24 h-without-it.**

**Fallback if Ed refuses the raise:** the only remaining lawful shape is Case A
— shakedown plus all three claim windows compressed into a single sub-24 h
no-reboot marathon with a ≤5 h step-6 turnaround. I would refuse to operate
that, and say so on the packet.

---

## (b) ORDERED STEP LIST

Notation: **[ED]** = Ed's hands, **[LEAD]** = lieutenant/lead only, no
delegation, **[DEL]** = delegable to Sol under WRITE_SCOPE.

### PRECONDITION BLOCK (all before step 1; none blocks the merge wave)

| P | Item | Role | Verification | Abort |
|---|---|---|---|---|
| **P0** | Merge wave landed; READY-candidate sitting verdict standing (D-149 C1: no NOT-READY, no UNVERIFIED, ED-QUAL rows closed) | [LEAD] | verdict file custodied + sha | any NOT-READY → transaction does not start |
| **P0b** | **The READY verdict must be re-checked for `_v4` applicability.** If the sitting verdicted on `_v3` pack identities, D-149 C1 does not transfer to a family that did not exist at the sitting | [LEAD] → cold gate if ambiguous | explicit written finding | ambiguous → cold-instance ruling before step 1 |
| **P1** | **ED ITEM 1 — V6 marker option (a) build-at-boundary or (b) UNBUILT.v0.** TRANSACTION-BLOCKING (r2 A-1 + cold delta); the registry cannot install with an unresolved marker string | **[ED]** | ruling recorded | unresolved → step 1 does not run |
| **P2** | **ED ITEM (NEW, this design) — the §(a) horizon raise.** Lands in the registry bytes at step 1; `_v5`-priced after mint | **[ED]** | number recorded in the ruling | unresolved → step 1 does not run |
| **P3** | **ED ITEM (NEW, this design) — the D-148.1 mint license does NOT cover `_v4`.** VERIFIED DEFECT: the installed `.claude/settings.local.json` allow-list contains only `_v3`/1p5b **literals** plus `generate_arm_readiness.py freeze --help`; **zero** of the six `_v4` mint commands are licensed and none is scoped to `/Users/edr/JouleWise-measurement-20260818`. The wildcard snippet D-148.1 ruled (`ed-s5-mint-decision-2026-08-19.md:25-33`) was never installed — S5 ran on per-prompt manual approvals | **[ED]** (~30 s; the classifier bars the agent from writing its own rule) | `grep` the four wildcard entries present | absent → step 5 blocks mid-fuse; batch with P1/P2 |
| **P4** | **ED ITEM (NEW, this design) — sudoers slice** for `/usr/sbin/systemsetup -getusingnetworktime` (D-127 QUIET-GUARD shape, exact binary + exact argv, no wildcards; D-115 install conditions; Ed personally executes the one privileged command) | **[ED]** | `sudo -n` verified | absent → **every** unattended T-0 author refuses (`arm_readiness_evidence_t0.py:884-903` runs `sudo -n` unconditionally and refuses nonzero; D-004 grants NOPASSWD to `powermetrics` only, `docs/decision_log.md:328`) → no D-149 auto-GO for shakedown or any window |
| **P5** | **THE ALLOWLIST DESIGN** — see §(e). A determinate, enumerated `irrelevant_path_allowlist`, ruled before the bytes are assembled | [LEAD] + council; Ed-reserved class | executed proof: the full mint sequence replayed on a scratch clone, then an arm dry-run that reaches past `:3212` | not proven executably → **STOP; do not mint** |
| **P6** | No-reboot commitment for the campaign span; boot session recorded | **[ED]** | `sysctl -n kern.bootsessionuuid` pinned | reboot → full re-author, new family |

### TRANSACTION STEPS

**Step 1 — Registry bytes.** [DEL, lead-verified byte-by-byte]
- Preconditions: P1, P2, P5.
- Content: outer id `d117-row-registry-v2` at
  `configs/arm_readiness/d117_row_registry_v2.json`;
  `schema_version = joulewise.arm_readiness_row_registry.v2`; V1 = the three
  `_v4` ids; V2/B-1 token `EXECUTION_ENVIRONMENT_FINGERPRINT_EXACT_AT_REUSE`
  on the ten generic + two T-0 kinds; B-2 token `NO_R1_AUTHORING_LANE` with
  policy id `r1.execution_bound.no_r1_lane_24h.v1` on the four; V3 horizons per
  §(a.5); V4 eight `readiness_r1_*` codes; V5 `capability_horizon_ns =
  arm_to_consume_budget_ns = 300_000_000_000`; V6 per P1; §1c inner id
  `d117-r1-lifecycle-v1`, `cross_chain_numbering` with no embedded generation
  number, `freeze_receipt_v2_predecessor_bindings =
  sorted(FREEZE_PREDECESSOR_KEYS)` (the nine at `arm_readiness.py:382-392`),
  `irrelevant_path_allowlist` per P5, `row_policies` mechanically generated in
  the outer registry's own row order.
- Verification: `validate_r1_lifecycle_registry(require_resolved=True)` AND
  `validate_registry` green over the assembled bytes; canonical rendering
  (`load_registry` enforces `require_canonical=True`, `:2508-2510`);
  `_r1_contains_reserved` walk clean (`:1501-1508`, `:1796-1800`).
- Abort: any validator refusal, any `ED_RESERVED:` residue anywhere in the walk.

**Step 2 — The code deltas, SAME COMMIT as step 1.** [DEL, lead-verified]
- All of §(c). The install is inert or explosive without them.
- Verification: full canonical green; the per-delta test pins of §(c) all
  present and each proven to fail against the pre-delta code.
- Abort: any delta missing → do not proceed; the registry bytes do not land
  alone.

**Step 2b — `ROW_REGISTRY_RELATIVE_PATH` + the literal sweep + archival
companion.** [DEL, mechanical] Same commit.
- `joulewise/arm_readiness.py:80` → the v2 path (one literal; four consumers at
  `:2509, :2768, :2778, :2900`).
- Live-editable sweep set, enumerated (61 files contain the literal; 18 are
  frozen pack bytes that must NOT be touched under D-140, and the
  `docs/process_traces/**` + `docs/run_reports/**` hits are immutable custody):
  `joulewise/arm_readiness.py` (1) · `tests/test_arm_readiness_lifecycle.py`
  (7) · `tests/test_arm_readiness_evidence_t0.py`,
  `tests/test_arm_readiness_integration.py`,
  `tests/test_arm_readiness_registry.py`,
  `tests/test_arm_readiness_schemas.py`, `tests/test_d117_decode_contrast_plan.py`
  (1 each) · `docs/phase_2/alpha_arm_readiness.md`,
  `beta_arm_readiness.md`, `gamma_arm_readiness.md`, `window_runbook.md`
  (1 each) · **= 11 files, 16 occurrences**; plus a new `docs/decision_log.md`
  pointer row, the kernel row, the runsheet, and `docs/site/*` regeneration →
  **~15 files**, matching the ruled figure.
- Archival companion: `configs/arm_readiness/d117_row_registry_v1.json` STAYS
  in-tree, unreferenced, with a **test pin on its sha — verified in this tree
  as `d248fdc521cb904b7ad8f1c4ecb834f7810a1d8f39697b462591f2feac39a2e5`**
  (matches the ruled `d248fdc5…39a2e5`).
- Verification: `grep -rl d117_row_registry_v1` returns ONLY the 18 frozen pack
  files + immutable custody + the archival companion itself.

**Step 2c — MERGE + PUBLISHED-HEAD CANONICAL + kernel/custody, ALL BEFORE
AUTHORING.** [LEAD]
- **This inverts r1 R-4.5's ordering, deliberately.** r1 puts "kernel rows +
  canonical + custody" LAST (step 7). Under the changed-set gate every one of
  those commits would land between `derivation_commit` and the arm-time HEAD
  and refuse the family. Kernel row A63 amendment, `gen_state.py --check`,
  runsheet edits, decision-log pointer, custody records, the full canonical
  suite (0.78 h) — **all of it lands and is pushed before the fuse starts.**
- Verification: canonical FULL GREEN at the head that will become
  `derivation_commit`; `git status --porcelain` empty at the measurement
  checkout; `head == local main == origin/main` (`reviewed_main` `exact_match`,
  `arm_readiness.py:3666`).
- Abort: any red test, any dirty tree.

**Step 3 — Ed's terminal-review attestation at the measurement checkout.**
**[ED]**
- The `--allow-empty` attested commit (`docs/process/rehearsal-operator-card.md`
  §2), which touches zero paths — the one commit that is changed-set-free by
  construction.

**Step 4 — `_v4` evidence authored, at the measurement checkout, at that head.**
[LEAD]
- **FUSE STARTS HERE. Record the wall-clock consume-by deadline into the
  run-card artifacts (r2 A-3, mandatory) at this instant, not at mint.**
- Verification: 33 receipts PASS ×3 packs; every receipt's `derivation_commit`
  == the step-3 head; deadline == authoring + the P2 horizon.
- Abort: any refusal → diagnose read-only, do not re-author blind.

**Step 5 — Plan trees regenerated ×3, then identity pins ×3, then freeze-0004
×3.** [LEAD; needs P3]
- `plan_arm_readiness_attachment` rebuilds `row_registry` from the live bytes
  (`:2900`) so the new trees pin the new id/path/sha.
- Ordinal = predecessor + 1, `--predecessor-pack-root` naming each pack's `_v3`
  sibling; the same-family re-authoring escape is closed by code (idempotent
  replay `:5437-5484`; ordinal from the pack DIRECTORY NAME `:5427-5432`,
  `:5489-5500`) so there is no second attempt.
- **Post-freeze custody `--check` must pass explicit preserve mode** (runsheet
  step-5 operator trap).
- Verification: freeze-0004 ×3, PASS, predecessor triple vs the `_v3`
  freeze-0003 shas (`0abfddb1…`, `f232d076…`, `f32bd3a8…` from the
  ed-s5 confirmation table); absolute `pack_root` pin recorded (`_pack_record`
  `:3692`).
- Abort: any non-PASS → STOP, cold review. Do not re-mint.

**Step 5b — Ceremony, per B-4 (redefined; NO real arm).** [LEAD]
- ONE `generate_arm_readiness.py dry-run` producing `DRY_RUN_REHEARSAL`
  evidence, PLUS the file-09 probe requiring **P1, P2, P3 all OK**.
- **B-4's recorded trade:** the empty-refusals arm receipt is no longer the V4
  reason-code-delta proof vehicle. Until the shakedown arm, that proof rests on
  dry-run + load-closure + gauntlet regressions, and **the shakedown GO receipt
  is the named V4-delta proof point.**
- Abort: any probe not OK → STOP before Ed sees anything.
- **Additionally required by §(e): the P5 allowlist must have been proven on a
  scratch clone BEFORE step 4. If it was not, this is the last honest place to
  stop, and the correct action is to stop.**

**Step 6 — ED CONFIRMATION at the irreversible point (r2 A-5.1).** **[ED]**
- Present the exact-byte table (three pack tree digests, three freeze-0004
  shas, the marker bytes, the installed registry reference) in the
  `ed-s5-mint-decision` confirmation-table pattern.
- **The publication-refusal clause anchors HERE (r3 B-6), before Ed's yes**:
  under P1 option (a) publication refuses until the marker instance validates;
  under option (b) the UNBUILT canary refuses.
- **T6 burns fuse from step 4's clock.** The packet must carry the live
  remaining-fuse figure so Ed sees what his turnaround costs.
- Abort: no yes → nothing publishes; everything to here is revertible.

**Step 7 — Publication on Ed's explicit yes.** [LEAD]
- Marker instance built after pack bytes are final, external to pack roots,
  binding all three `_v4` plan-tree digests, all three freeze-0004 references,
  and the exact installed registry reference (terra's binding set, adopted
  verbatim).
- Verification: published-head canonical green (B-5 term (b)); staleness fan-out
  gone.

**Step 8 — Shakedown window = THE MEASUREMENT (r3 B-3).** [LEAD, D-149 auto-GO;
needs P4]
- Re-cut `docs/process/window-run-cards/shakedown-v3-first-light.md` for `_v4`
  first — the card currently names the `_v3` family throughout.
- The first REAL arm of the `_v4` family happens here, under its D-149 GO
  receipt. The receipt records the observed **T-0→arm gap** and **arm→consume
  gap** (neither has ever been measured —
  `registry-packet/05-arm-to-consume-budget.md:164-170`).
- **MANDATORY HALT GATE, MECHANICAL, NOT PROSE (r3 B-3 + cold final check):**
  bounds are T-0→arm ≤ 15 min and p99 arm→consume ≤ 4 min. The check is a
  **gate in the window scheduler, evaluated before the NEXT window is
  authorized** (wired via the A-5.4(d) D-149 automation analysis). Violation →
  campaign halts before any claim window; the horizon question goes to Ed with
  the observed numbers and the `_v5` price on the packet.
- In-band check per the run card; OUT-OF-BAND or refused → STOP the lane,
  council consult (D-078 no-retry).

**Steps 9/10/11 — ALPHA → BETA → GAMMA.** [LEAD, D-149 auto-GO]
- Hard block chain (`TASK_QUEUE.md:534-536`), one pack per window, no cadence
  requirement but a strict quiet lock per window.
- Each arm carries the a.5 countermeasure re-pin check in its GO receipt.
- Each arm re-checks remaining fuse; **abort the campaign rather than arm with
  < 1 h of fuse** (below 300 s the arm receipt's `valid_until` silently
  collapses to the fuse deadline, `:6240-6242`).

---

## (c) CODE-DELTA MANIFEST

All in the step-1/2 commit. Every delta gets a **defect-shaped** regression:
the test must fail against pre-delta code.

| # | Delta | Site | Test pin |
|---|---|---|---|
| C1 | Four typed `readiness_r1_*` frozensets, unioned into `READINESS_REASON_CODES` + entries in `REASON_TYPE_BY_CODE` | `joulewise/arm_readiness.py:180-211` | (a) each of the 8 codes round-trips `_validate_refusal` (`:1434-1443`); (b) parametrized issuance test proving a bare code raises `readiness_schema_invalid` pre-delta |
| C2 | **Registry-load closure check**: refuse at load any `refusal_vocabulary` code not in `READINESS_REASON_CODES`, or whose type ≠ `REASON_TYPE_BY_CODE[code]` | refusal loop `arm_readiness.py:1746-1785` | a registry with a well-formed-but-unclosed code must refuse AT LOAD (today it loads and explodes only at issuance — both seats executed this double failure) |
| C3 | **Type-enum constraint (mechanical, not a choice):** `SUCCESSOR_CHAIN` is a valid `REASON_TYPE_BY_CODE` value (`:210`) but is **absent** from the registry-side type allowlist (`:1768-1776`). No V4 code may be typed `SUCCESSOR_CHAIN`. Proposed assignment: POLICY = {class_mismatch, unknown_policy}; LIFECYCLE = {dependency_changed_set, dependency_manifest_invalid, temporal_budget_exceeded, v1_grandfathered}; CUSTODY = {family_publication_unmet}; GIT = {successor_chain_invalid} | `:1768-1776`, `:488-498` (8 roles) | a registry entry typed `SUCCESSOR_CHAIN` must refuse at load — pins the latent gap so it cannot be silently "fixed" into a `_v5` |
| C4 | `_SUPPORTED_ENVIRONMENT_COMPARISONS` gains **both** tokens: `EXECUTION_ENVIRONMENT_FINGERPRINT_EXACT_AT_REUSE` (B-1) and `NO_R1_AUTHORING_LANE` (B-2) | `joulewise/arm_readiness_evidence.py:117-119`; consumed `:1786-1796` | every one of the 16 EXECUTION_BOUND kinds authors without the `UNKNOWN_POLICY` refusal; an unlisted token still refuses |
| C5 | **B-1 comparator** in `_authenticate_existing_r1`: the stored fingerprint's digest must equal the digest of a freshly-derived fingerprint; mismatch REFUSES RE-USE with author code `evidence_author_environment_changed`. Comparison term = `sha256(render_json(fingerprint))` (`arm_readiness_evidence.py:469-472`), one determinate term over all nine fields — immune to term-set drift | `arm_readiness_evidence.py:2216`, dispatch `:2361-2371` | (a) perturb the fingerprint → re-use refuses; (b) identical fingerprint → re-use succeeds; (c) **`PACK_AUTHENTICATION` regression**: its fingerprint digests the full sorted `os.environ` (`:442-453`), so its re-use effectively always refuses across shell sessions — pin that as EXPECTED fail-closed so operators never read routine environment-noise refusals as pack corruption |
| C6 | **Horizon consistency assertion** (registry ↔ code, two sources of truth) | new assertion in `validate_r1_lifecycle_registry` | asserts: the 7 TIME_BOUND volatile + 2 SESSION_STATE_BOUND rows == `_VOLATILE_EVIDENCE_VALIDITY_NS` (20 min); `CLOCK_ATTESTATION` + `LEDGER_RESERVATION` + the two T-0 EXECUTION_BOUND rows == `_NONVOLATILE_EVIDENCE_VALIDITY_NS` (6 h) — `arm_readiness_evidence_t0.py:49-50`, which the registry **cannot** override; `RE_DERIVABLE` == null. Test: bumping either t0 constant must red this assertion |
| C7 | **B2 fail-ugly catch**: wrap `_freeze_evidence_for_arm` and convert `EvidenceLifecycleError` to a refusal record, mirroring `arm_readiness.py:4613-4614` | **both** call sites — `:6139-6141` AND the re-validation path at `:6334-6336` (r1 R-4.1 named only the first; the second has the identical unguarded shape) | defect-shaped: a `V1_GRANDFATHERING` / `DEPENDENCY_CHANGED_SET` raise must produce a NO_GO receipt with the registry-derived code+type, not an escaping exception. **Two tests, one per call site.** |
| C8 | `set(bindings) == FREEZE_PREDECESSOR_KEYS` assertion so the declaration cannot drift from `_derive_freeze_predecessor` | `arm_readiness.py:382-392` derivation `:5113-5148`; assertion in the lifecycle validator | a registry with the fixture's fictional five-key list must refuse at load |
| C9 | `ROW_REGISTRY_RELATIVE_PATH` → v2 path + the archival sha pin | `arm_readiness.py:80` | (a) `load_registry` resolves the v2 file; (b) sha pin on the v1 archival companion |
| C10 | **P5 allowlist** (see §(e)) — bytes, not code, but its proof obligation is a code-level test | `:3210-3218` | executed test: replay the full mint commit sequence in a temp repo, then assert `validate_r1_evidence_lifecycle` passes. **This is the only test that proves the family can arm at all.** |

---

## (d) WRITE_SCOPE + STAGE DECOMPOSITION

**Several sessions, not one.** D-144 classification is BIG (r2 A-5.5): full
implementation gauntlet, C-028 delta re-audits on every fix round, Fable final
review, and one more two-seat pass over the implemented artifact pre-merge.

| Stage | Owner | WRITE_SCOPE (exhaustive) | Gate out |
|---|---|---|---|
| **S-0 ALLOWLIST DESIGN** | **[LEAD] + two-seat + cold gate.** NOT delegable as a value — it is a sixth Ed-reserved-class value the council never ruled | scratch only | Executed proof on a throwaway clone: full mint sequence → `validate_r1_evidence_lifecycle` passes. **No other stage starts until this is green.** |
| **S-1 CODE DELTAS** | [DEL] Sol **xhigh**, one session (C1–C9 are one contract surface; splitting them invites the "install is inert" failure) | `joulewise/arm_readiness.py`, `joulewise/arm_readiness_evidence.py`, `tests/test_arm_readiness_lifecycle.py`, `tests/test_arm_readiness_evidence.py`, `tests/test_arm_readiness_registry.py`, `tests/test_arm_readiness_schemas.py`, `tests/test_arm_readiness_integration.py`, `tests/test_arm_readiness_evidence_t0.py` | independent audit (never self-grade) → 2 refuters with DISTINCT lenses (contract vs execution) → delta re-audit of every fix round |
| **S-2 REGISTRY BYTES** | [DEL] Sol xhigh builds; **[LEAD] verifies byte-by-byte against the ruling** — post-mint every byte is `_v5`-priced | `configs/arm_readiness/d117_row_registry_v2.json`, `scripts/build_candidate*.py` (new, or scratch) | both validators green; a lead-authored diff of the assembled bytes against the r1§1b/r3 value table, value by value |
| **S-3 LITERAL SWEEP** | [DEL] Sol **high** (mechanical) or Workflow fan-out — matches the memory's "mechanical multi-site / no shared invariant" fit | the 11 live files of step 2b + `docs/process/phase2-transaction-runsheet.md` + `docs/process/state_kernel.json` + `docs/decision_log.md` (append a pointer row only — never rewrite history) | `grep` residue check; `gen_state.py --check` clean; **explicit refusal to touch any `configs/campaigns/**` or `docs/process_traces/**` path** |
| **S-4 RUN-CARD + GO-RECEIPT + SCHEDULER GATE** | [DEL] Sol high, [LEAD] reviewed | `docs/process/window-run-cards/*`, `docs/process/d149-go-receipt-template.md`, the scheduler gate module | B-3's halt trigger exists as executable code with its own test, not as a sentence |
| **S-5 EXECUTION** | **[LEAD] ONLY. Zero delegation.** Steps 3–8 at `/Users/edr/JouleWise-measurement-20260818` | the measurement checkout | rule 1: the lead never delegates final verification |
| **S-6 PRE-MERGE SEAT PASS** | two seats + cold pair (D-144 BIG) | — | merge wave under D-148.2 gate authority |

Ed touches, **batched into ONE session** per the standing minimize-Ed-sessions
rule: P1 (V6 option) + P2 (horizon) + P3 (mint license, ~30 s) + P4 (sudoers,
one privileged command) + P6 (no-reboot commitment). Step 3 (terminal review)
and step 6 (confirmation) are necessarily separate and later.

**Lead-only, never delegated:** the P5 allowlist ruling; the step-6 packet
assembly; all of S-5; the decision to abort. Per rule 11 the lieutenant is
forbidden to decide alone on P1/P2 (process/irreversible), on adjudicating any
of these blockers downward, or on continuing past the B-3 halt gate.

---

## (e) THE SINGLE LARGEST RISK, AND MY REFUSAL

**RISK: `irrelevant_path_allowlist: []` makes the `_v4` family structurally
unarmable, and the failure surfaces only AFTER the mints — i.e. after the point
of no return, with a live fuse and a dead family.**

The chain, all executed against code in this tree:

1. `_r1_changed_paths` is a **whole-repository** `git diff --name-only
   derivation_commit..current_head` — not a dependency-filtered diff
   (`joulewise/arm_readiness.py:3105-3113`).
2. `relevant = sorted(set(changed_paths) - allowlist)`; **any** residue raises
   `DEPENDENCY_CHANGED_SET` (`:3210-3218`).
3. `current_head` is the measurement checkout's live HEAD
   (`reviewed_main` → `git rev-parse HEAD`, `:3652-3668`; wired at `:5378-5382`
   → `:5390` → `:4348`).
4. The transaction commits **six to nine times** at that checkout between
   authoring and arm — plan-tree regen ×3, identity pins ×3, freeze-0004 ×3,
   "one commit per step" (`docs/process/ed-s5-mint-decision-2026-08-19.md:36-46`).
5. Those commits cannot be avoided: `committed_pack_tree_sha256` means
   `pack_sha256` is the **committed** tree (`:3694`), and freeze-0004 binds
   `evidence_set_sha256` (`:5147`, `FREEZE_PREDECESSOR_KEYS` `:382-392`) so
   evidence must precede the mint. There is no ordering in which
   `derivation_commit == current_head` at arm.
6. Therefore `relevant` is non-empty at every arm, and with `allowlist = []`
   every arm refuses.
7. And per r1 R-4.1's own finding the resulting `EvidenceLifecycleError`
   escapes `_freeze_evidence_for_arm` **uncaught** (`:6139-6141`) — so the
   first operator symptom is a traceback, not a diagnosable refusal record.
8. The repository's own tests confirm the shape: they pass
   `allowlist=("pack/plan_tree.json",)` to get an evidence item through this
   gate (`tests/test_arm_readiness_evidence.py:404,419`). The only regime in
   which `[]` has ever been "behaviour-neutral" is the regime where the gate
   never runs, because no v2 registry has ever been installed.

This is a third blocker of exactly the same class as the byte-pin and
`V1_GRANDFATHERING`, and it is worse than both, because those two refuse
BEFORE the mints while this one refuses AFTER them — and post-`_v4` a registry
edit costs a `_v5` family (R-4 item 3, the ruling's own standing price).

**Second-order, and the reason the allowlist cannot simply be widened
thoughtlessly:** under Case B the campaign spans days, and every commit landing
at the measurement checkout between ALPHA's window and BETA's arm — reductions,
custody, run reports, bookkeeping — refuses BETA. Either the measurement
checkout's main is frozen for the entire multi-day span (viable: reductions
happen at the custody clone per the shakedown run card), or the allowlist grows
to cover the repo's whole working set and the gate becomes decorative. That is
a design decision with a science-facing consequence, not a config value.

### WHAT I REFUSE TO PROCEED WITHOUT

**Three items. Any one missing → I do not start step 1.**

1. **An executed proof that the family can arm.** On a throwaway clone: author
   R1 evidence at head H, run the full mint sequence exactly as step 5 will run
   it, then call `validate_r1_evidence_lifecycle` / an arm dry-run against the
   candidate registry, and show it reaches past `arm_readiness.py:3212`. The
   allowlist is whatever that experiment says it must be, enumerated
   path-by-path, and it lands in the step-1 bytes. **This is the file-09
   experiment's mirror image and it has not been run.** Until it is, the ruled
   `[]` is an unexecuted assumption sitting at the irreversible point.
2. **Ed's horizon-raise ruling (P2) before any byte is assembled.** The
   envelope arithmetic in §(a) says 24 h fails at ALPHA's arm; a mint under the
   ruled 24 h buys a `_v5` family the moment the second window is scheduled.
3. **The two Ed-hands preconditions verified present, not assumed** (P3 mint
   license — verified ABSENT for `_v4` today; P4 sudoers slice — verified
   ungranted, D-004 covers `powermetrics` only). Both block mid-fuse. Both cost
   Ed under a minute. Neither has an agent-side workaround, by design.

Secondary — I would also not proceed without P0b (whether the standing
READY verdict transfers from a `_v3`-identity sitting to a family that did not
exist when the sitting was held). If it does not transfer, D-149 C1 fails at
the shakedown's GO receipt and the entire post-publication schedule stalls with
the fuse running.
