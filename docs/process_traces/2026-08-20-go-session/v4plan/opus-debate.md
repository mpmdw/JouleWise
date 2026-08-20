# `_v4` transaction — Opus debate response (bounded, one round)

My design (`opus-design.md`) stands as written except where marked CONCEDED or
CORRECTED below. Citations are to `/Users/edr/code/JouleWise/`, verified in the
read-only worktree at `1d7db83` (tree == main == `5bd7acf` content).

---

## 1. Sol's "R1 lifecycle circularity" vs my allowlist/changed-set blocker

**Verdict: SAME MECHANISM, DISTINCT AND EARLIER TRIGGER POINT. Sol's is
correct and mine was located one step too late. CONCEDED, and Sol's trigger is
adopted as the primary.**

Both findings are `_r1_changed_paths` (whole-repo `git diff --name-only
derivation_commit..current_head`, `arm_readiness.py:3105-3113`) minus an empty
`irrelevant_path_allowlist` (`:3210-3218`). We differ on where it first fires:

- **Mine:** at ARM, because the plan-tree/U11/freeze commits sit between
  authoring and arm-time HEAD.
- **Sol's:** at FREEZE, because committing the evidence bytes themselves
  already makes the changed set non-empty.

**Sol is right, and I verified the wiring Sol's scratch probe did not
establish.** Sol's probe called `validate_r1_evidence_lifecycle` directly; it
did not show that `generate_freeze_receipt` reaches that gate. It does:

- `generate_freeze_receipt` (`:5408`) calls `_discover_evidence(...,
  lifecycle_registry=registry["freeze_evidence_lifecycle"], ...)` at
  **`arm_readiness.py:5516-5524`**.
- `_discover_evidence` calls `_authenticate_generic_evidence_item` for every
  PACK-namespace item under a live registry at **`:4601-4609`**, which routes
  to `validate_r1_evidence_lifecycle` at `:4356` → the changed-set gate.

So the family refuses at **step 4/5 (mint)**, not step 8 (arm). That is
materially better news operationally — it fires *before* Ed's step-6
irreversible point — and it makes the pre-mint proof cheaper to run.

**Two corrections I add on top of Sol's finding:**

**(1a) At freeze the error is CAUGHT; at arm it is NOT.** `_discover_evidence`
catches `EvidenceLifecycleError` and converts it to a refusal record
(`:4612-4613` — this is precisely the pattern r1 R-4.1 tells us to mirror).
`_freeze_evidence_for_arm` does not, at **both** `:6139-6141` and
`:6334-6336`. So the same defect is a diagnosable refusal at mint and a bare
traceback at arm. **This is why C7 (the B2 catch, at both call sites — R-4.1
names only the first) is non-negotiable rather than hygiene.**

**(1b) NEW, and it raises the stakes on the pre-proof — a refused mint may
POISON `_v4` permanently.** A caught refusal means `generate_freeze_receipt`
does not abort; it proceeds to assemble the receipt with `evidence_refusals`
folded in (`:5516` → the refusals list threaded to the receipt writer). If a
`freeze-0004` receipt is written and its plan-tree slot pinned, then A-4's
substituted mechanism applies forever after: `generate_freeze_receipt` returns
the **idempotent replay** whenever a plan-pinned freeze receipt exists
(`:5437-5484`), and the ordinal derives from the pack DIRECTORY NAME
(`:5427-5432`, `:5489-5500`). **A refused `freeze-0004` would therefore be
unfixable inside `_v4` — the recovery is `_v5`.**
I could not settle within budget whether the writer refuses to emit a receipt
carrying refusals. **This is a MUST-ANSWER question for the pre-mint proof**,
and it is added to the joint blocker list as its own item, because it converts
"the experiment failed, retry" into "the family is dead."

**Joint blocker list (consolidated, both seats):**

| B | Blocker | First fires | Recoverable? |
|---|---|---|---|
| **B-α** | Empty allowlist refuses the transaction's own committed evidence | `generate_freeze_receipt` → `:5516` → `:4601` → `:3212` | Only if 1b resolves benign |
| **B-β** | Same gate refuses at every subsequent arm (shakedown + 3 windows) from the mint/kernel/custody commits | `:6139`, `:6334` | No — post-publication |
| **B-γ** | The same error escapes uncaught on the arm path | `:6139-6141`, `:6334-6336` | n/a — cured by C7 |
| **B-δ** | *(new, mine, §4 below)* unattended T-0 is impossible: `CLOCK_ATTESTATION` is `OPERATOR_ATTESTATION` by construction | every window incl. shakedown | Build item |

---

## 2. Envelope: converge the number, and kill the deadline-on-Ed

### 2a. Where the arithmetics differ

Sol's fixed total 22.6767 h vs my 18.84 h. The gap is almost entirely one
modelling choice: **Sol counts to GAMMA's finish; I count to GAMMA's arm.** I
hold that the fuse binds at arm — `validate_r1_class_lifecycle` runs in the arm
path, and consumption is a single instant checked against
`arm["valid_until_monotonic_ns"]` at `:7910-7914`, with that value already
capped by `min(now + capability_horizon, *evidence_expirations)` at
`:6240-6242`. But Sol's conservatism costs ~5 h on a horizon proposal measured
in days, and being wrong in my direction is unrecoverable. **CONCEDED: adopt
Sol's finish-of-GAMMA convention for the proposal arithmetic.**

**The real divergence is not arithmetic, it is which schedule we price.** Sol
prices ONE shape: all three windows back-to-back in a single continuous span.
That is my Case A — 18.8–22.7 locked hours on Ed's daily-driver M3 Max with
zero weather, under D-078's no-retry rule where one refused capture ends that
lane (`docs/decision_log.md:172` C5). It is not the ratified operating shape
(`docs/strategy/2026-08-14-70h-plan.md:71-92`; hard block chain
`TASK_QUEUE.md:534-536`), and Sol's 72 h has **no headroom for a single
refused night**. My Case B (one window per quiet night) puts GAMMA's finish at
≈ T0+79 h clean and ≈ T0+151 h with one weather night per lane.

### 2b. Is a bound on Ed's response enforceable or sane? **No. DISPUTED — refuted.**

Three independent grounds:

1. **It is unenforceable by anything in the repo.** There is no revocation
   mechanism; "abort at T0+24h" is prose. r3 B-3 already ruled on this exact
   class: *"prose halt triggers are how stop signals get eaten."* A design seat
   cannot fix its arithmetic with a sentence addressed to a human.
2. **Its abort clause is factually wrong.** Sol writes that at the deadline the
   transaction "abort[s] while reversible … and re-author/re-mint later." At
   Sol's own step 6, `freeze-0004` has already been minted at step 4. Under
   A-4's mechanism (`:5437-5484`, `:5427-5432`) **`_v4` cannot be re-minted**;
   re-mint means `_v5`. The clause promises a recovery the code does not
   provide.
3. **It inverts rule 11.** Ed's step-6 exact-byte confirmation is the seat
   accountable for when to stop (D-149 retains it explicitly,
   `docs/decision_log.md:172`; r2 A-5.1). Attaching a destruction deadline to
   it manufactures precisely the sunk-cost continuation pressure rule 11 exists
   to prevent — "answer in 24 h or the family dies" is a stop-signal
   reinterpretation device, and it is not the lieutenant's or a design seat's
   to install.

**And it does not even work, because Ed is needed FIVE times, not once** — see
§4/B-δ: `CLOCK_ATTESTATION` requires an interactive operator paste at every
T-0. You cannot bound a human you must wake for the shakedown and all three
windows.

### 2c. CONVERGED PROPOSAL TO ED

> **Horizon: 168 h (`604_800_000_000_000` ns) on the ten generic freeze-time
> kinds, policy `r1.execution_bound.freeze_generic_168h.v1`.**
> **No deadline on Ed.** Sol's safety intent is preserved by machinery instead:

1. **The step-6 packet prints the live remaining-fuse figure** (r2 A-3 already
   requires the mints to record the wall-clock consume-by deadline; surface it
   on the confirmation table so Ed sees what his turnaround costs).
2. **A mechanical minimum-fuse gate in the scheduler**, alongside r3 B-3's
   gap gate: refuse to authorize any window whose pack has less than a declared
   threshold of fuse remaining. This is Sol's deadline, relocated from a human
   to `scripts/run_campaign.py` (which exists — I checked; S3 is a modification,
   not a greenfield build).
3. **The per-window re-pin check** (my a.5 countermeasure), now load-bearing
   for the reason Sol gives — see the corrected cost statement below.

Sol's 72 h is recorded as dissent. It is the floor for the marathon schedule
only and absorbs zero weather; under Case B it fails during BETA. If Ed rejects
168 h on freshness grounds, **96 h is the least I would sign** (clean Case B,
no weather); I will not sign 72 h.

### 2d. Freshness-cost statement — CORRECTED, Sol's refutation accepted

**CONCEDED, and it is a real catch.** My design listed B-1's
`EXECUTION_ENVIRONMENT_FINGERPRINT_EXACT_AT_REUSE` among the detectors that
"do not relax." Sol is right that it does not belong there: *"the B-1
fingerprint comparator only protects authoring reuse; it does not establish
that the environment remained unchanged until arm."* R-3's own registered
limitation says the same — no ARM-time environment refusal exists
(`R1_REFUSAL_ROLES` is closed at eight with no environment role,
`arm_readiness.py:488-497`).

**Corrected statement for Ed's packet — exactly three detectors do not relax at
168 h:**

1. **Changed-set gate** (`:3207-3218`) — any relevant in-tree path that moved
   since derivation refuses. Strictly stronger than any clock for in-repo facts.
2. **One-boot binding** (`:4263-4270`, `:3380-3381`) — a reboot voids the
   family at any remaining wall-clock. Preserved verbatim from Sol's proposal.
3. **Per-window T-0 re-derivation** — 9 volatile kinds @ 20 min, 4 nonvolatile
   @ 6 h, code-pinned (`arm_readiness_evidence_t0.py:45-46, 102-122, 1758-1768`).

**The exposed residual, stated plainly:** out-of-tree, non-boot, non-T-0 facts
— principally the acceptance artifact and estimator-pinned files where they
resolve outside the pack tree — may be up to seven days old at consumption
instead of one, with **no ARM-time environment check anywhere in the system**.
Because B-1 does not cover this, **the per-window re-pin check is not a
nicety; it is the substitute for the missing ARM-time detector**, and the
168 h proposal is conditional on it shipping. Concretely: every GO receipt
re-derives and compares the live sha of the acceptance artifact against the
frozen pin (r6 `0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d`,
`docs/process/ed-s5-mint-decision-2026-08-19.md` confirmation table) and of
`ESTIMATOR_IDENTITY`'s pinned files. With it, 168 h is strictly safer than
today's unaugmented 24 h. Without it, I would not go past 96 h.

---

## 3. Step order — adjudicated against the changed-set mechanism

**Sol's step 7 VIOLATES the mechanism Sol itself discovered. DISPUTED; my
inversion holds and is now doubly required.**

Sol's step 7 ("Atomic publication, kernel, canonical, custody") places kernel
rows, generated state, and custody commits **after** step-2 authoring — the r1
R-4.5 ordering my design deliberately inverted. Those commits land between
`derivation_commit` and the arm-time HEAD of the shakedown and all three claim
windows, and they are refused by the same gate.

The inconsistency is internal to Sol's own design: Sol's F2 remedy is *"an
exact, transaction-scoped output manifest … governed sources, receipts,
sidecars, normalized plan-tree freeze slots, identity projections, and freeze
receipts. It must not accept globs or unrelated post-derivation files."*
`docs/process/state_kernel.json`, generated state, `CLAIMS_STATUS.md`, and
custody records are none of those things — Sol's manifest deliberately refuses
to cover them, and Sol's step 7 then commits them.

**Ruling I put forward:** all kernel / state / custody / doc commits land
**before** evidence authoring. The one legitimate post-publication term is
**B-5's published-head canonical suite RUN**, which is fine because a green run
commits nothing. Amendment I add: **if the published-head canonical produces
any commit at all (a state regen, a custody hash), that is itself an ABORT
trigger**, because it invalidates the four remaining arms.

**Where Sol's order is better than mine — CONCEDED, adopt:**

- Sol emits the three `_v4` pack roots in **step 1, pre-authoring**. I folded
  emission into my step 5. Sol's is correct: the pack directories should exist
  and be committed before the fuse starts, leaving the plan-tree *regen* (which
  must consume the final evidence manifest) as the only in-fuse pack-tree write.
- Sol splits plan-tree regen (step 3) from U11+mints (step 4). Cleaner, and it
  gives the changed-set manifest a smaller, more precisely enumerable surface.

**Converged order:** P-block → 1 registry+code+`_v4` roots (Sol) → 1b literal
sweep → **1c kernel/state/custody/doc commits + pre-authoring canonical (mine,
non-negotiable)** → 2 Ed terminal review → 3 author evidence (**FUSE STARTS**)
→ 4 plan-tree regen → 5 U11 + freeze-0004 → 6 ceremony/probe/marker candidate
→ 7 Ed step-6 (publication-refusal anchored here per B-6) → 8 publication +
published-head canonical **producing zero commits** → 9 shakedown → 10-12
ALPHA/BETA/GAMMA.

---

## 4. V6 marker and mint license

**V6 — AGREED on substance, with one adopted improvement and one caution.**
Both seats and the magistrate converge on option (a) build-at-boundary. Sol's
binding set (three pack ids+paths, three plan-tree digests, three freeze-0004
paths+shas, exact installed registry `{registry_id, path, sha256}`,
complete-family predicate) matches terra's adopted spec and is more concrete
than mine; **adopt Sol's spec verbatim**, including its schema id
`joulewise.d117_family_publication_marker.v1` and external path
`configs/campaigns/d117_family_publication_v4.json` (outside the three pack
roots, so R-3/runsheet-step-5 compliant). Caution to record: B-7's ledger
requires the packet to also carry option (b)'s *reduced* `_v5` price if the
envelope already makes a further family likely — Sol asserts this but does not
number it; the magistrate should not send Ed an unnumbered cross-term.

**Mint license — my finding stands, Sol's treatment is under-specified.
DISPUTED (severity), AGREED (remedy shape).** Sol writes "install or confirm
D-148.1 mint permissions … or commit to running the six mint commands
personally," treating the state as unknown. **I verified it.** The installed
`.claude/settings.local.json` allow-list contains `_v3`/1p5b **literals** plus
`generate_arm_readiness.py freeze --help` — **zero** of the six `_v4` mint
commands are licensed, none is scoped to
`/Users/edr/JouleWise-measurement-20260818`, and the wildcard snippet D-148.1
ruled (`docs/process/ed-s5-mint-decision-2026-08-19.md:25-33`) was never
installed; S5 ran on per-prompt manual approvals. Sol's fallback (Ed runs the
six commands) is legitimate and was the historical route, but it puts Ed's
hands inside a live fuse at mint time in addition to step 6; the 30-second
settings edit is strictly better. Recommend the rule, keep the fallback.

**Sudoers — REFUTED, and it produces a new blocker (B-δ).** Sol's step 0 says
to install `scripts/joulewise-network-time.sudoers` and "perform the privileged
prior-state read." I read the file:

```
Cmnd_Alias JOULEWISE_NETWORK_TIME = /usr/sbin/systemsetup -setusingnetworktime off, \
                                    /usr/sbin/systemsetup -setusingnetworktime on
```

It covers the two **set** commands only. **I also correct my own P4**, which
claimed the T-0 author runs `sudo -n … -getusingnetworktime`: it does not.
`grep` over `joulewise/arm_readiness_evidence_t0.py` shows exactly two `sudo -n`
invocations — `-setusingnetworktime off` (`:899-904`, covered by this file) and
`powermetrics -i 200 -n 1` (`:1469`, covered by D-004). The citation I relied
on (`2026-08-15-readiness-council/refuter-outputs/sol-refuter-B-execution.md:203`)
describes code that has since changed.

**The blocker is real but has a different and worse shape than either seat
stated.** The prior-state read is not a `sudo -n` probe at all — it is an
`OPERATOR_ATTESTATION` (`arm_readiness_evidence_t0.py:884-889`, derived from
`attestation_identity, prior_identity, disable_identity`), i.e. **Ed
interactively pasting a trusted-clock UTC literal and the exact
`Network Time: On/Off` line** (`docs/process/rehearsal-operator-card.md` §E-4).
RUN_STATE records the same collision: *"the T-0 author currently demands an
interactive paste."* Therefore:

> **B-δ: D-149 unattended auto-GO is impossible today. Every window — the
> shakedown and all three claim windows — requires Ed awake at T-0.** Closing
> it needs BOTH (i) a `-getusingnetworktime` entry added to the sudoers slice,
> which is a **scope change to a D-127-ratified privileged install** (D-127
> charters "exactly the two fixed systemsetup network-time commands") and
> therefore an Ed/magistrate item, and (ii) a **code change** giving
> `_derive_clock_attestation` a self-derived path to replace the operator
> attestation. Installing the existing `.sudoers` file, as Sol's step 0
> prescribes, does not achieve unattended operation, because no code path
> consumes a `-getusingnetworktime` read.

B-δ is also the final nail in §2b: Ed's latency cannot be bounded once when the
schedule needs his hands five times.

---

## 5. Other refutations / concessions on Sol

| Item | Verdict |
|---|---|
| Sol's V1 verification (two existing `R1EvidenceLifecycleTests` pass) | **Non-probative, not refuted.** Those tests use the fixture registry, which passes `allowlist=("pack/plan_tree.json",)` (`tests/test_arm_readiness_evidence.py:404,419`). They prove nothing about `[]`. Sol does not claim otherwise; recording it so the magistrate does not read V1 as coverage. |
| Sol: "13 T-0-authored kinds" in the horizon-consistency pin | **CONCEDED — Sol is right and my draft was wrong.** Census verified: `_VOLATILE_EVIDENCE_KINDS` = 9 (`arm_readiness_evidence_t0.py:102-114`), `_NONVOLATILE_EVIDENCE_KINDS` = 4 (`:115-122`), total 13, with a module-level assertion that the union equals every governed kind (`:123-128`). **My C6 is amended to assert the exact 9/4 partition** — sharper than R-3's class-framing and than Sol's bare "13". |
| Sol: `scripts/run_campaign.py`, `scripts/d149_go_evaluator.py` in S3 scope | **AGREED, and I withdraw a concern I nearly raised.** `scripts/run_campaign.py` exists; B-3's mechanical gate is a modification, not a greenfield scheduler build. |
| Sol: "For the first sample, the conservative p99 is the sole/max observation" | **CONCEDED, adopt.** n=1 p99 is a real gap my design left implicit. |
| Sol's F2 remedy shape — keep `allowlist: []`, teach the gate to subtract an **authenticated** transaction-output manifest — vs my remedy (enumerate paths into `irrelevant_path_allowlist`) | **CONCEDED to Sol on soundness; I withdraw mine.** A static allowlist entry for e.g. `…/freeze-0004.json` forgives that path *forever, for every future arm* — a permanent hole through which a post-mint pack mutation would pass unnoticed. Sol's derived, digest-authenticated manifest has no such hole and costs no registry value. **Two conditions I attach:** (i) the subtraction must be **digest-conditional and testable** — a path is subtracted only if its current bytes hash to a value already bound by the freeze receipt / evidence manifest, never merely because it is under a governed directory; (ii) this is a **contract change to the R1 authentication path** — the very thing my design's §3 rejected code-level grandfathering for — so it is a magistrate/council item under rule 11, not a lieutenant call, and it enlarges the BIG gauntlet by one implementation+review stage (Sol's S0). |
| Sol's step-6 abort clause "everything remains unpublished and reversible" | **REFUTED** — `freeze-0004` exists by then; `:5437-5484` + `:5427-5432` make `_v4` non-re-mintable. Reversibility at step 6 holds only if nothing has been pushed AND the measurement checkout is hard-reset to the pre-mint commit — which must be stated as an explicit, tested recovery procedure, not assumed. |
| Sol's horizon pin "assert 300s budget equals capability horizon and remains below 20 minutes" | **Unsourced.** The equality is V5's no-silent-truncation invariant (agreed); the "below 20 minutes" bound has no cited basis. Drop it or cite it. |

---

## FINAL AMENDED POSITION

| # | Item | Position |
|---|---|---|
| 1 | Circularity is a distinct, earlier trigger of my mechanism; fires at **freeze** (`:5516`→`:4601`→`:3212`), caught (`:4612`), then again **uncaught** at arm (`:6139`, `:6334`) | **CONCEDED** to Sol's trigger; **added** 1a (two failure modes) and 1b (possible permanent `_v4` poisoning — must-answer) |
| 2a | Arithmetic convention: count to GAMMA's finish | **CONCEDED** |
| 2b | Bound on Ed's step-6 response | **DISPUTED** — unenforceable, its abort clause is factually wrong (`:5437-5484`), it inverts rule 11, and B-δ needs Ed five times not once |
| 2c | Horizon number | **CONVERGED: 168 h**, no Ed deadline, safety via the step-6 fuse readout + a mechanical minimum-fuse scheduler gate + the per-window re-pin. Sol's 72 h recorded as dissent; 96 h is my floor |
| 2d | Freshness cost — B-1 does not protect until arm | **CONCEDED**; corrected to three non-relaxing detectors, and the re-pin check is reclassified from optional to **required** |
| 3 | Kernel/state/custody commits post-authoring (Sol step 7) | **DISPUTED** — violates Sol's own F2 manifest scope; my pre-authoring inversion holds, plus a new abort trigger if the published-head canonical emits any commit |
| 3b | Pack emission at step 1; regen split from mints | **CONCEDED**, adopted |
| 4a | V6 option (a) + Sol's binding set | **AGREED**, adopt verbatim; number B-7's cross-term |
| 4b | Mint license | **AGREED** on remedy; **verified ABSENT for `_v4`** — not "confirm", *install* |
| 4c | Sudoers sufficiency | **REFUTED**; new blocker **B-δ** (unattended T-0 impossible; needs a D-127 scope change **and** a code change) |
| 5a | 13 T-0 kinds | **CONCEDED**; C6 sharpened to the 9/4 partition |
| 5b | F2 remedy shape (authenticated manifest, not allowlist bytes) | **CONCEDED** to Sol, with digest-conditionality and a rule-11 authority note attached |
| 5c | Sol's V1 tests as coverage; "below 20 minutes" pin | **Recorded as non-probative / unsourced** |

---

## CONSOLIDATED RULING LIST FOR THE MAGISTRATE

### A. r4-amendment items (magistrate rules; amends r1/r2/r3)

1. **A1 — §1c `irrelevant_path_allowlist: []` is VACATED as a sufficient
   specification.** It is a third install blocker (B-α/B-β). Replacement per
   Sol's F2 shape: allowlist stays `[]`; the gate learns to subtract a
   **digest-authenticated, transaction-scoped output manifest**. Contract
   change to the R1 authentication path → magistrate authority, not
   lieutenant's.
2. **A2 — mandatory pre-mint executed proof.** Three synthetic `_v4` roots:
   author → commit → regen → U11 → `freeze-0004` → dry-run, all green under the
   installed v2 registry; plus negative controls (ordinary dependency mutation
   still refuses; an unexpected file under a governed directory still refuses;
   plan-tree normalization still forgives only the freeze slot). **No live
   authoring before this is green.** Both seats independently refuse to proceed
   without it.
3. **A3 — MUST-ANSWER inside A2:** does `generate_freeze_receipt` emit a
   `freeze-0004` receipt carrying refusals, and does the plan-tree pin then lock
   the idempotent replay (`:5437-5484`)? If yes, a failed mint is unrecoverable
   inside `_v4` and A2 becomes the single highest-stakes gate in the plan.
4. **A4 — R-4.5 step order AMENDED:** kernel / state / custody / doc commits
   move **before** evidence authoring; only the published-head canonical *run*
   is post-publication, and any commit it produces is an abort trigger.
5. **A5 — C7 (B2 catch) applies at BOTH `:6139-6141` and `:6334-6336`.** R-4.1
   names only the first; the second has the identical unguarded shape.
6. **A6 — V3 horizon-consistency assertion sharpened** to the exact 9/4
   partition of the 13 T-0-authored kinds
   (`arm_readiness_evidence_t0.py:102-122`), superseding R-3's class-framed
   census and both seats' drafts.
7. **A7 — B-3's mechanical gate extended** with a minimum-remaining-fuse check
   before any window authorization, and n=1 p99 defined as the sole/max
   observation. Lands in `scripts/run_campaign.py` (exists).
8. **A8 — new blocker B-δ registered:** D-149 unattended auto-GO is
   unavailable today; `CLOCK_ATTESTATION` is `OPERATOR_ATTESTATION` by
   construction (`arm_readiness_evidence_t0.py:884-889`). Closing it is a
   D-127 privileged-scope change **plus** a code change. Until closed, every
   window is an Ed-hands event and the campaign schedule must say so.
9. **A9 — B-7 cross-term must be NUMBERED** on Ed's V6 packet, not asserted.

### B. Ed items

1. **V6 marker option** — recommendation (a), Sol's binding set as spec.
   *Transaction-blocking.*
2. **Horizon** — **168 h** on the ten generic kinds, conditional on the
   per-window re-pin check shipping; four `NO_R1_AUTHORING_LANE` kinds stay
   24 h; two T-0 procedural kinds stay 6 h. Sol's 72 h + T0+24h deadline
   presented as the recorded dissent, with its abort clause's defect noted.
   **No deadline is placed on Ed.** *Blocks registry byte assembly.*
3. **Mint license** — install the four wildcard entries
   (`ed-s5-mint-decision-2026-08-19.md:25-33`); verified absent for `_v4`
   today. ~30 s. Fallback: Ed runs the six commands personally.
4. **Sudoers scope change** (B-δ(i)) — add `-getusingnetworktime` to
   `scripts/joulewise-network-time.sudoers`; a D-127 scope amendment, Ed's own
   hands per D-115.
5. **No-reboot commitment** for the campaign span; boot UUID pinned.
6. *(Batch 1–5 into one Ed session per the minimize-Ed-sessions rule; step-6
   confirmation and the per-T-0 clock attestations are necessarily separate.)*

### C. Plan-internal (lead/lieutenant, no ruling needed)

1. Converged step order of §3.
2. Stage decomposition: Sol's S0–S5, with S0 (F2 correction) gating everything
   and S-5/execution lead-only. My §(d) lead-only list stands.
3. Code-delta manifest = my C1–C10 with C6 amended per A6, C7 per A5, C10
   re-shaped per A1; plus Sol's per-seam test pins, which are stronger than
   mine on the closure/mutation dimensions — adopt Sol's column.
4. Re-cut the shakedown run card from `_v3` to `_v4` before step 9.
5. **P0b carried:** verify whether the standing READY-candidate verdict
   transfers from a `_v3`-identity sitting to `_v4`. If not, D-149 C1 fails at
   the shakedown GO receipt with the fuse running.
6. Literal sweep: 11 live files / 16 occurrences + kernel + runsheet +
   decision-log pointer + site regen ≈ 15; 18 frozen pack files and all
   `docs/process_traces/**` are immutable. Archival v1 sha pin
   `d248fdc5…39a2e5` (both seats independently confirmed).
