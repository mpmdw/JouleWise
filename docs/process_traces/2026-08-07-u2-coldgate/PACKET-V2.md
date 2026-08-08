# PACKET-V2 — U2 cold gate, reconvened (D-102 successor engine, reworked exhibit)

## 1. Header

- **Exhibit under review:** branch `impl/d117-u2-successor` @ `ad5f3f7`
  (full sha `ad5f3f732cfaf9a336461ea5ff33788f4fc80b8a`). This is the
  REWORKED exhibit; it supersedes the first-round exhibit state
  `399ffeb`. The exhibit is the gate's evidence, not a landing
  candidate.
- **Main baseline at assembly:** `origin/main` @ `195cafd` — "RUN_STATE
  overnight: trust authority class ruled DEAD (fix round 3 on two new
  items); recovery audit FAIL with all three historical classes as
  implementation misses (dictated fix round 1, tripwire armed); D-124
  banked".
- **Convening rules:** the charter in this directory's `README.md`
  (cold Fable instance with no loop context, paired Opus contract-lens
  refuter; both rule on this packet only; magistrate overrule requires
  written dissent Ed sees). Charter erratum #2, carried from the prior
  round: worktree convening does NOT suppress doctrine injection for
  subagent judges; the contamination-disclosure line is the working
  control. Conveners and judges should apply the charter with that
  erratum.
- **v1 remand note.** The first packet (PACKET.md, ruled on by
  COLD-FABLE-RULING.md and OPUS-REFUTATION.md, both in this directory)
  was REMANDED: it quoted D-102 and D-116 as the governing authorities,
  while the exhibit's own `SUCCESSOR_DECISION_IDS` declares D-102,
  D-109, D-117 (plus the placeholder `COLD-GATE-U2-PENDING`) as
  binding — D-109, operative for seven of the twelve questions, was
  not before the gate. The remand synthesis is `SYNTHESIS.md` in this
  directory. This packet places the declared authorities in full
  (byte-verified), re-presents all twelve questions against the
  reworked exhibit, and adds Q13 (a choice the first packet covered
  with no question).

## 2. The question for the gate

Whether to ratify, ratify as amended, reject, or defer each of the
thirteen contested semantics implemented and tagged in the reworked U2
successor-engine exhibit at `ad5f3f7` — corpus universe (Q1), preflight
screen source (Q2), numerical method (Q3), count-boundary progression
(Q4), systematic-refusal policy and closure (Q5), no-content handling
(Q6), lineage/loader surface (Q7), registry authority and migration
shim (Q8), publication ordering (Q9), probe-over-open-extension (Q10),
trigger absorption and conjunct scope (Q11), exhibit scope (Q12), and
allowance generalization with minimum corpus (Q13). Each section below
presents the implemented choice, what changed since `399ffeb`, the
strongest arguments FOR and AGAINST, the prior-round evidence, the
consequences of ruling either way, and the decision required. The
packet takes no position; the per-question decision menu is in §6.

**Standing neutrality note on survival/mootness mappings.** Statements
below that a prior-round finding is "MOOTED" by or "survives" the
rework are the ASSEMBLER'S contestable characterizations, offered to
orient the gate. Which prior findings survive the rework is itself part
of what the gate rules; these mappings are labelled where they appear
and bind nothing.

## 3. Binding context — authority quotations (byte-verified)

### Quotation verification

Verifier's overall verdict line, quoted: "OVERALL: FAIL — all 12 quoted
blocks are byte-identical to their sources and all structural/
completeness checks pass, but the declared-authority preamble cites a
nonexistent commit id (ad4f3f7… for ad5f3f7…); the packet must not ship
a wrong 40-char sha in the authority chain of a remanded
byte-verification exhibit. Correct the two commit ids (short + full) in
the tuple preamble and the extract is fully PASS as-is; no quoted block
needs any change."

The correction the verifier required has been applied in this packet:
the tuple preamble below cites the exhibit commit as `ad5f3f7` =
`ad5f3f732cfaf9a336461ea5ff33788f4fc80b8a`. All twelve quoted blocks
are reproduced unmodified. The verifier additionally confirmed: the
tuple's sole definition on the exhibit is `calibration_bracketing.py`
:144-149; the successor script imports the name at its line 36 and
embeds it at line 373; D-102 (index + sole body entry), D-109 (index +
body + addendum II, the only headed D-109 addendum in the log), and
D-117 (index + body) are complete extracts; `COLD-GATE-U2-PENDING` has
no decision-log entry or index row anywhere in the repo.

### DECLARED-AUTHORITY-TUPLE

Source: `joulewise/calibration_bracketing.py` at exhibit commit
`ad5f3f7` (`ad5f3f732cfaf9a336461ea5ff33788f4fc80b8a`), lines 144-149.
The successor script `scripts/build_calibration_acceptance_successor.py`
imports the name at its line 36 and embeds it at line 373 as
`"decision_ids": list(SUCCESSOR_DECISION_IDS)`.

```
SUCCESSOR_DECISION_IDS = (
    "D-102",
    "D-109",
    "D-117",
    "COLD-GATE-U2-PENDING",
)
```

Tuple members, exactly: `D-102`, `D-109`, `D-117`,
`COLD-GATE-U2-PENDING`.

**Disposition of the fourth member.** `COLD-GATE-U2-PENDING` has no
decision-log entry or index row anywhere in the repository (verifier-
confirmed); its only occurrences are the exhibit source line and the
prior packet's quotation. It is the placeholder naming THIS pending
gate itself. The gate is asked (§6, cross-cutting item) to dispose of
it: what identifier replaces it on ratification, and what its presence
means if the gate rejects or defers.

### D-102 — INDEX ROW

Source: `/Users/edr/code/JouleWise/docs/decision_log.md`, line 127.

```
| D-102 | CAL-BRACKET-D079-01 pins: budget cap 0.001275166090593858 s (99% two-draw prediction ceiling 0.012093166090593858 s, blind n=19 derivation), exact-identity-epoch freshness with prospective re-derivation triggers, never-zero allowance max(drift, screen) embedded once, decimal-source numeric semantics with labelled presentation values | accepted (magistrate ratification, lead-replayed arithmetic, 2026-08-01) |
```

### D-102 — BODY

Source: `/Users/edr/code/JouleWise/docs/decision_log.md`, lines
6345-6407.

```
## D-102: CAL-BRACKET-D079-01 pins ratified — corpus-derived budget cap, identity-epoch freshness, never-zero allowance, decimal numeric semantics

- Date: 2026-08-01
- Status: accepted (magistrate ratification after the two-round Sol xhigh
  design consult + the independent n=19 corpus reconstruction; ALL
  arithmetic lead-replayed at the bench: ceiling, cap, t(0.995,18)
  quantile by numerical CDF, window B pre-cal value against primary
  evidence bytes)
- Applies to: CAL-BRACKET-D079-01, the future
  `configs/calibration/calibration_acceptance_d079_v2.json` artifact

The four pins D-079 left unexecutable, now pinned:

1. **Budget cap (Candidate A, 99% two-draw prediction family, derived
   blind from the pre-window-B n=19 corpus):**
   `max_budgetable_excess_s = 0.001275166090593858`;
   `maximum_budgetable_drift_s = 0.012093166090593858`
   (= t(0.995,18)=2.878440472713585 × sd 0.002970761365307205 × √2;
   cap = ceiling − operative screen 0.010818). Consequences verified: a
   ~11.58 ms drift branch is budgetable; a 15 ms bracket refuses.
   **Window B itself remains refused regardless** — its pre-calibration
   0.035435840879704805 s (verified in primary evidence) exceeds the
   pre-flight level screen, and D-079 cl.2's systematic failure is
   never budgetable. The CAL-BRACKET regression at ~11 ms models the
   DRIFT BRANCH only, never a whole-window B pass.
2. **Freshness = exact identity epoch, no calendar hard expiry:** the
   artifact binds {os_build, hardware_model, power_policy,
   sampling_interval_ms, estimator_revision, pulse_protocol_id}; any
   change → `calibration_acceptance_bound_stale`. Mandatory prospective
   re-derivation triggers: any identity-field change; protocol/estimator
   byte change; a new valid same-identity calibration expanding the
   observed range; corpus doubling (19→38); a new systematic failure
   challenging the pre-flight screen. A trigger observation is judged
   under the PRIOR artifact — never incorporated into a threshold that
   judges itself. Calendar-age fields are provenance/advisory only (the
   corpus spans four days; a calendar constant would be invented).
3. **Never-zero allowance confirmed:**
   `A_s = max(observed_drift_s, 0.010818)`;
   `B_operative = max(B_pre, B_post) + A_s`, embedded ONCE in the
   authenticated operative fiducial bound (anchor-envelope
   re-reduction); no second calibration-drift energy term anywhere
   downstream (D-078 cl.11 single-count).
4. **Decimal numeric semantics:** the artifact stores source decimal
   lexemes and exact-decimal derivations (range
   0.010817749309353528 s; 95% prediction 0.008826584887500717 s;
   pre-flight exact max 0.03355875667989999 s) SEPARATELY from the
   ratified operative comparators (0.010818; 0.033558756679900;
   ROUND_HALF_EVEN at the declared quantum), hashing the decimal
   strings + rounding rule into the derivation sha256. D-079's
   12-place `0.010817749309` is a LABELLED presentation value, never a
   comparator. Acceptance comparisons run in decimal semantics;
   binary64 conversion happens only at the reducer boundary and is
   recorded.

Corpus provenance: the n=19 member list with per-member manifest and
evidence sha256s is reconstructed and lead-spot-verified (2026-08-01
session records; summary in the session custody dir) — the artifact
copies those tables verbatim with re-verification at authoring, never
retyped. Implementation remains sequenced behind gauntlet commit 3 and
the D-100 repair (shared write surfaces).

Revisit when: CAL-BRACKET-D079-01's delta audit reports, or any
re-derivation trigger fires.
```

### D-109 — INDEX ROW

Source: `/Users/edr/code/JouleWise/docs/decision_log.md`, line 134.

```
| D-109 | CAL-BRACKET-D079-01 F3: A-min-with-reservation — writer-enforced receipt ledger (reservation-first pending entry before capture, mandatory finalization, unresolved-pending refusal), ledger-only consumption, repo-committed head pin, single immutable snapshot threading; R1 authority/retention/anti-rollback (7 clauses) + R2 prior-observation set with the 38-total counting rule (8 clauses); Option B recorded as rejected fallback; lands with F1+F2 as the single combined fix round | accepted (Ed 2026-08-03, same deferral; Sol soundness breaks lead-verified and adopted) |
```

### D-109 — BODY

Source: `/Users/edr/code/JouleWise/docs/decision_log.md`, lines
7075-7172. This is the FULL body — all seven R1 clauses and all eight
R2 clauses; no clause-selection has been applied.

```
## D-109: CAL-BRACKET-D079-01 F3 — A-min-with-reservation adopted (writer-enforced receipt ledger, reservation-first, repo-committed head pin); R1 ledger-authority and R2 prior-observation-set rulings

**2026-08-07 supersession note:** The issuance clause later superseded by
D-116 is retained unchanged as historical context. Current rule ownership:
D-116.

- Date: 2026-08-03
- Status: accepted (Ed ruling 2026-08-03: same explicit deferral to the
  joint magistrate + Sol position, same debate record. Arc: the fix
  investigation recommended A-min; Sol round 1 BROKE that formulation
  as stated (writer crash-window; prefix-subset is not anti-rollback)
  and recommended Option B for the timeline; magistrate round 2
  supplied the low-schedule-pressure record, the metrology-centric
  pivot, and the shared-R2 marginal-cost analysis; Sol WITHDREW B and
  converged on A-min-with-reservation, marginal cost Medium. Both
  soundness holes were lead-verified at the bench before adoption.)
- Applies to: `scripts/validate_powermetrics_fiducial.py` (sole
  production calibration writer), `joulewise/calibration_bracketing.py`,
  `joulewise/whole_window.py`, `scripts/run_campaign.py`,
  `configs/calibration/calibration_acceptance_d079_v2.json`, and every
  consumer construction of `AuthenticatedConsumptionSession`. This is
  a faithful IMPLEMENTATION of D-102 (no threshold/freshness
  amendment); it supplies the authority/universe rulings D-102 left
  silent. Lands with F1 + F2 as the single combined CAL-BRACKET fix
  round. Option B (signed narrowing amendment) is recorded as REJECTED
  fallback — coherent and honest, but it weakens the thesis instrument
  where the project has slack to build the sounder boundary.

**R1 — ledger authority, retention, anti-rollback (7 clauses):**
1. A canonical observation-receipt ledger and its append API are the
   SOLE authority for governed calibration observations. An off-ledger
   calibration artifact is invalid everywhere: as bracket endpoint,
   trigger evidence, derivation member, or claim evidence. Consumers
   enumerate ledger entries only, never caller-supplied directories.
2. RESERVATION-FIRST: every capture appends an authenticated `pending`
   attempt entry BEFORE hardware capture begins, and must finalize it
   as valid / systematic-invalid / ordinary-invalid / abandoned. Any
   unresolved pending, unfinalized, malformed, or conflicting entry
   causes claim evaluation to REFUSE. (Grounds, bench-verified: the
   writer creates capture state pre-receipt and has pre-manifest
   failure exits — a publish-on-return receipt misses exactly the
   crash/interrupt cases a completeness mechanism exists to catch.)
3. Receipts are immutable and hash-chained: sequence, predecessor,
   attempt id, content id, artifact hashes, six-field epoch, full T1,
   capture time, exact bound lexeme, disposition, custody locator.
4. The acceptance artifact pins its baseline ledger head. Evaluation
   ALSO requires the independent current-head pin (clause below),
   verifies one complete non-forked chain extension from baseline to
   current, and threads ONE immutable ledger snapshot through every
   consumer path (session, direct runner path, secondary verifier) —
   repeated independent loads are a refusal-grade defect.
   Anti-rollback authority: a REPO-COMMITTED head-pin file
   `{sequence, head_digest, ledger_schema}` (existing checked-in
   byte-pin trust model; no second trusted latest-sequence store).
   Rotation is epoch-bounded — at most one lead-controlled
   quiet-machine collection session — and NO claim evaluation may
   occur between ledger advancement and pin commit; a physical head
   differing from the committed pin refuses.
5. Ledger history is retained permanently. Referenced evidence remains
   in authenticated custody; missing or unverifiable required bytes
   cause refusal, never silent omission.
6. Version 1 is single-authority, single-machine. Remote/other-machine
   captures are invalid until imported through an authenticated ledger
   transaction; direct multi-machine append requires a new ruling.
7. Threat model, stated honestly and to be stated wherever A-min is
   described: the mechanism closes workflow omission, unregistered
   evidence, and rollback/stale-head consumption. It does NOT defend
   against a malicious trusted writer or an authority that rewrites
   both Git and ledger history. No stronger claim may be made.

**R2 — prior-observation set and prospective triggers (8 clauses):**
1. The issuance cutoff is an exact ledger sequence + head digest.
2. `derivation_corpus` remains exactly the n=19 threshold-producing
   observations.
3. `prior_observation_set` = every content-distinct governed
   observation known at the cutoff — valid, systematic-invalid,
   ordinary-invalid, blind holdout, and unresolved — with epoch and
   disposition recorded separately. (The current artifact's two
   ID-only `blind_exclusions` are insufficient and are superseded.)
4. Content identity is path-independent, derived from canonical
   primary-byte hashes; attempt identity is separate; copies do not
   create new observations.
5. "New" (trigger population) = current authentic content IDs −
   `prior_observation_set`, regardless of capture timestamp or source
   root; a previously unknown historical artifact IS new when
   discovered. Every new observation is judged under the PRIOR
   artifact (D-102's prospective rule).
6. New unresolved or unclassifiable attempts cause refusal; only after
   trigger disposition may a successor artifact absorb them.
7. The 32-valid/6-invalid same-epoch inventory is a backfill
   CANDIDATE, not a ratified classification: identities may seed the
   backfill, but dispositions require raw-physics + hash verification
   before issuance, and any unresolved member blocks issuance.
8. Counting rule for the D-102 corpus-doubling trigger (19→38): 38
   TOTAL authenticated, content-distinct, VALID same-epoch
   observations — including previously blind observations once
   unblinded — not 38 post-cutoff observations. Under the candidate
   inventory, six further valid observations trigger re-derivation.
```

### D-109 ADDENDUM II — BODY

Source: `/Users/edr/code/JouleWise/docs/decision_log.md`, lines
7306-7343. (The only headed addendum for D-109 in the log; no
"addendum I" heading exists.)

```
## D-109 addendum II: reviewed mint-core interface amendment (integration-collision resolution); D-110 oracle clarification

- Date: 2026-08-04 (successor magistrate ruling after bounded
  pre-decision Sol high consult, one round; Ed's HIGH effort cap
  observed)
- Status: executed (PR #100 gate-complete, CI green at `4280ebd`;
  merge is Ed's tap — the harness denies agent self-merge)
- Record: `docs/process_traces/2026-08-04-calbracket-integration-collision/`
  (FINDING.md, RESOLUTION.md, impl + delta re-audit reports) and
  `docs/process_traces/2026-08-04-calbracket-collision-consult/`

1. D-109 R1.4's `calibration_ledger_snapshot` threading is a DELIBERATE
   REVIEWED INTERFACE REVISION of the mint core. The generalized mint's
   `_CORE_SIGNATURES` pin is amended to the new signature; no adapter
   shim, no multi-version pin, no core-file digest pin (consult Q1,
   adopted). Future `_CORE_SIGNATURES` changes require explicit
   signature-pin review plus parity evidence (noted in-code).
2. The guard's framing is corrected to REVIEW-PINNED MINT-CORE
   INTERFACE — it pins selected signatures of a review-controlled core
   file and is not a byte freeze; "byte-identical" is reserved for
   observed output comparisons.
3. D-110 CLARIFICATION (conditions unchanged): tooling byte-identity
   evidence means INTEGRATION-TREE CORE-VS-WRAPPER PARITY on identical
   inputs. It does not require any future artifact to match the tainted
   historical mint-1 digests — D-110's corrected re-mint may
   legitimately produce different bytes. MINT-GENERALIZE-01's
   acceptance evidence is reworded accordingly in the kernel.
4. Guard hardening (delta re-audit F2, proven live): rendered-signature
   comparison is spoofable by a default whose `repr()` is `None`; the
   guard now identity-checks the None sentinel defaults structurally,
   with a regression. Residual honestly held: `__signature__` spoofing
   remains a property of the approach; the guard is a reviewed-drift
   tripwire, not a security boundary against an adversarial core file.
5. PROCESS FINDING (candidate rule, NOT ratified here — rule-11
   cold-gate packet item): the lead's rule-1 verification replay runs
   on the INTEGRATION tree whenever the branch is behind main. Recorded
   with the collision as its motivating catch (CI on the merge ref was
   the only layer that could see it).
```

### D-116 — INDEX ROW and BODY

**Label: CONTEXT BEYOND DECLARED AUTHORITY.** D-116 is NOT named in
`SUCCESSOR_DECISION_IDS`. It is placed here because (a) it is reachable
context via D-109's and D-116's supersession notes, (b) the prior-round
rulings cited it, and (c) the remand synthesis mandated its Window-B
completeness note be before the gate for Q1. The gate weighs it as
context, not as declared exhibit authority.

Index row — source: `/Users/edr/code/JouleWise/docs/decision_log.md`,
line 141.

```
| D-116 | D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (seq 76 / head 08456d50…; issued sha 316113960c…; 30/2/6 dispositions); D-110 condition (b) SATISFIED → MINT-GENERALIZE-01 unblocked for re-mint; two-cold-gate history (plan HELD → consumer impl + gauntlet → bytes PROCEED, sequencing HOLD resolved by consumer-first merge); window_metrologyB calibration fiducials in completeness record are NOT a D-113 violation | executed (Fable magistrate, 2026-08-06; Ed pre-authorized) |
```

Body — source: `/Users/edr/code/JouleWise/docs/decision_log.md`, lines
7591-7612.

```
## D-116: D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (D-110 condition (b) SATISFIED)

**2026-08-07 supersession note:** The historical re-mint consequence later
superseded by D-117 is retained unchanged as historical context. Current
rule ownership: D-117.

**Date:** 2026-08-06 (Fable magistrate, overnight; issuance pre-authorized by Ed 2026-08-05 conditional on the gate passing).
**Status:** EXECUTED. This retires the schema fixture and issues the authoritative calibration acceptance artifact — the anchor all future floor-mint claims authenticate against. D-110 re-mint condition (b) ("R2 backfill verified, ledger bootstrapped, head pinned") is now SATISFIED; (a) was satisfied by PR #100, (c) by PR #105. **MINT-GENERALIZE-01 is UNBLOCKED for the re-mint.**

**What was written.**
- `runs/calibration_observation_ledger.jsonl` — the 76-receipt genesis historical-import chain (git-ignored local custody artifact, sha256 `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`; deterministic from the custodied inputs below + the raw evidence; MUST be backed up per the runbook before the re-mint consumes it).
- `configs/calibration/calibration_ledger_head.json` — the repo-committed head pin (sequence 76, head_digest `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`), the D-109 R1.4 anti-rollback trust anchor.
- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
- Reproducibility inputs custodied at `docs/process_traces/2026-08-06-d079-issuance-coldgate/` (disposition table sha `5da820aa…`, custody manifest sha `99cbf3df…`, execute summary, ledger sha).

**Disposition inventory (B1 lead-ruled).** 30 valid / 2 systematic-invalid / 6 ordinary-invalid. The two systematic-invalid members (`20260726T000039-491995f3`, `20260801T064830-c76f5d1c`) have bounds `0.035435840879704805` / `0.0350400833260715`, both exceeding the ratified pre-flight screen `0.033558756679900`; D-102 (§~6298) explicitly names the first a systematic failure "never budgetable." R2.8 counting: 30 valid < 38 threshold, so issuance does NOT itself trigger corpus-doubling re-derivation (eight further valid same-epoch observations would; R2.8's literal "six further" was conditioned on the superseded 32-valid candidate). derivation_corpus preserved byte-identical at n=19 (its fixture whole-core digest was `3cece3b2…`; that value is NOT carried into the issued artifact — embedding it would fail the loader). All 38 custody locators are iCloud-backup copies (raw evidence is git-ignored by repo convention; integrity rests on the committed hash chain, not the custody pointer).

**Window-B completeness note (soundness-critical, for any reviewer asking "why Window-B in the anchor?").** The `prior_observation_set` correctly includes 6 `window_metrologyB` **calibration fiducial** observations (2 valid: `e0ce33f5`, `8c3bfe9e`), as mandated by D-109 R2.3/R2.8 completeness (every content-distinct governed CALIBRATION observation). This is NOT a D-113 violation: D-113 retired Window B's WINDOW CLAIM consumption (its null-ladder/additivity science members), not the calibration fiducials collected in that period; the general calibration machinery survives per D-113. These fiducials are EXCLUDED from the frozen n=19 threshold basis (which is Window-A-only) and do not influence the bound.

**Gate history (the process earned its keep on the anchor).** Two rule-11 cold gates. Cold gate #1 (on the plan) HELD correctly — the naive JSON-edit plan had no issued-artifact consumer (F1) and would have invalidated the whole-core digest (F2). That forced a real consumer implementation, which then ran the full C-028 gauntlet: adversarial audit (consumer proven false-ACCEPT-resistant; 3 emission/execute blockers incl. ledger-commit-BEFORE-artifact-validation) → fix → delta (exit-3 masking) → fix → final delta ACCEPT. Cold gate #2 (on the exact bytes): both lenses PROCEED on CONTENT (head/dispositions/B1/R2 all independently reproduced); HOLD on sequencing only — the consumer had to land on main before writing the issued artifact, else the anchor bricks. Resolved by merging PR #108 first, then executing against consumer-present main, with the co-landing verification (`_valid_acceptance_bound(issued)=True`) confirmed post-write. Full records: `docs/process_traces/2026-08-06-d079-issuance-coldgate/`.

**Consequences.** MINT-GENERALIZE-01 (b) satisfied; the re-mint (a10 extraction + mint #1 re-derivation under the corrected selector, embedding the D-102 pin-3 never-zero drift allowance) is the next step — the path to a non-empty claims table. The runs/ ledger must be custody-backed before the re-mint consumes it.
```

### D-117 — INDEX ROW

Source: `/Users/edr/code/JouleWise/docs/decision_log.md`, line 142.

```
| D-117 | D-110's historical re-mint order SUPERSEDED (structurally unsatisfiable at main: issued ledger holds only import-marked receipts, candidate discovery excludes imports); replacement = THREE prospective claim windows (fresh 1.5B decode floor, fresh 7B decode floor, fresh decode contrast) live-bracketed under the issued regime; prefill floor cells ride the floor windows; contrast decode-only by default (≥256-token prefill arm stays Ed's open option); D-113 readiness rewired (three-window P1 closure precedes MET-WINDOW-C-01); Option 1 preserved as cold-gated contingency only | adopted (Ed directive, in-thread 2026-08-07; transcribed by the Fable magistrate) |
```

### D-117 — BODY

Source: `/Users/edr/code/JouleWise/docs/decision_log.md`, lines
7614-7673.

```
## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired

**Date:** 2026-08-07 (Ed directive, in-thread; transcribed by the Fable
magistrate. Ed, verbatim: "if i recall for a paper ready at the quality
needed we need 3 more machine quiet nights and a lot of desk work",
with an explicit go to "execute all the deskwork" — read together with
his 2026-08-06 in-thread MVP-scope directive "a little more than just
decode, at least decode/prefill". His ruling moots a cold gate: apex
authority per rule 11.)
**Status:** ADOPTED. Full technical record:
`docs/process_traces/2026-08-06-d110-remint-fork/` (DIAGNOSIS: the
structural closure live-reproduced at `c537386`; Sol xhigh consult run
`20260806T165843Z-10884`; SYNTHESIS: magistrate concurrence).

1. **The D-110 clause-3 re-mint order (historical a10 consumption under
   the corrected selector) is SUPERSEDED.** The issued ledger holds only
   import-marked receipts; candidate discovery excludes imports by
   design; future live receipts cannot causally bracket past windows.
   The order is structurally unsatisfiable at main, not merely
   inconvenient. D-110's OTHER holdings STAND untouched: mint #1 and
   derivatives remain non-claim-bearing, and the never-zero
   `A_s = max(observed_drift_s, 0.010818)` allowance (D-102 pin 3)
   BINDS every mint under this entry.
2. **Replacement: three compact prospective claim windows** — fresh
   1.5B decode floor, fresh 7B decode floor, fresh 1.5B-vs-7B contrast
   — each with fresh §5A, live pre/post calibration receipts appended
   to the issued ledger, own verdict + head-pin + custody. Claims
   chain: historical corpus → issued D-079 acceptance rule → live
   brackets → prospective floors → prospective contrast. Honest
   framing preserved from the consult: historical data establish the
   RULE; live receipts bracket all claim-bearing science.
3. **Scope (Ed's decode/prefill directive):** prefill FLOOR cells ride
   both floor windows (cheap, same members' prefill phase). The model
   contrast is DECODE-ONLY by default: the 2026-08-07 desk feasibility
   check (`docs/process_traces/2026-08-07-prefill-feasibility/`) found
   the 128-token prefill contrast MARGINAL against the effective bar
   (interval overlaps it). A prospectively frozen ≥256-token prefill
   contrast arm remains an OPEN ED OPTION (estimand change +
   ~110 core minutes, likely its own window) — not adopted here.
4. **D-113 rewire:** its readiness dependency on the historical re-mint
   completing is REMOVED. The three-window P1 closure PRECEDES the
   broader MET-WINDOW-C-01 C2/C4/C5 replacement campaign (grounds:
   Ed's paper-first priority stack, 2026-08-06).
5. **Naming:** "Window D" is unavailable (collides with
   `runs_window_d_20260726` and D-113's reserved terminology); the
   three windows receive new immutable plan/root identifiers at plan
   freeze.
6. **Option 1 (finite-allowlist historical candidacy) is PRESERVED as
   a versioned contingency ONLY**, requiring a rule-11 cold gate before
   any implementation (semantics sketch: consult response §3). The
   historical corpora remain untouched on disk, non-claim-bearing per
   D-110 cl.1, logs sha-verified.
7. **Unblocked desk queue** (consult §4): freeze three window plans +
   budgets; 1.5B decode floor plan from the proven 10-absolute/40-null
   design; generalized mint pinsets with per-plan six-decimal literals
   (the D-084 hard literal `7.377086` refuses any corrected mint under
   every option — closure is per-plan supply via the generalized path);
   extraction specs / order manifests / evidence-root ids / contrast
   manifest; synthetic three-window live-ledger integration regression;
   D-102 successor-artifact packet; results/methods prose placeholders.
```

### FINDINGS-REGISTER — LENS 2 (contains L5, L4, and the loader note)

Source:
`/Users/edr/code/JouleWise/docs/process_traces/2026-08-07-night-hardening/FINDINGS-REGISTER.md`,
lines 24-37.

```
## Lens 2 — calibration/ledger (AUDIT-LEDGER.md)

- L5 HIGH: bracket selection can BORROW another window's receipts
  (global candidate scan; no runs_root/intended-pair binding) — exactly
  the defect class U1's session capability + exact binding closes.
  U1 review MUST include this scenario as a regression vector.
- L4 HIGH: pre-flight screens only a COPIED SCALAR (0.033558…), not
  the issued artifact/identity epoch/range triggers — science can run
  all night then be rejected at the morning verdict (identity epoch
  change; sub-corpus-minimum lag). Closure = memo §5A step 6 pre-science
  acceptance + D-102 trigger probe (U2) + de-duplicating the hardcoded
  literal. U2 review must include both scenarios.
- Loader itself verified correct at HEAD (issued role, file sha
  316113960c…, estimator hashes match).
```

### FINDINGS-REGISTER — LENS-2 DISPOSITION PARAGRAPH

Source:
`/Users/edr/code/JouleWise/docs/process_traces/2026-08-07-night-hardening/FINDINGS-REGISTER.md`,
lines 39-44.

```
## Disposition

U1/U3 in flight cover L5 and part of the mint surface. U2 covers L4's
trigger probe. R6 (absolute-paths) + R5 (monotonic time) + lock
staleness need either a small hardening unit (U1.5) or explicit
operator-procedure mitigations — decide when lens 3 lands.
```

## 4. The thirteen questions

Authority citations in the sections below reference the byte-verified
quotations in §3 by entry name (DECLARED-AUTHORITY-TUPLE; D-102 —
INDEX ROW / BODY; D-109 — INDEX ROW / BODY / ADDENDUM II; D-116 —
INDEX ROW / BODY, context beyond declared authority; D-117 — INDEX
ROW / BODY; FINDINGS-REGISTER — LENS 2; FINDINGS-REGISTER — LENS-2
DISPOSITION PARAGRAPH). D-109 is quoted WHOLE (all R1 and R2 clauses).
Prior-round material is labelled "(prior round, pre-rework)" and is
evidence about the superseded exhibit state `399ffeb`, not about the
code under review.

---

### Q1 — Successor corpus universe

**(1) Question.** When a successor acceptance artifact is derived, which observations constitute its derivation corpus: the exhibit selects every content-distinct, `valid`-dispositioned, same-epoch observation known through the issuance cutoff. The contested alternatives in the record are (a) that universe as implemented, (b) a Window-A-only universe that excludes the Window-B calibration fiducials per the exclusion language in D-116 — BODY (Window-B completeness note; context beyond declared authority), and (c) a frozen-parent-basis universe extended only by trigger-disposed observations under D-109 — BODY R2.2/R2.6. The gate must rule which universe the corpus-selection rule is licensed to enumerate.

**(2) Code at ad5f3f7.** `SUCCESSOR_CORPUS_SELECTION = "all_content_distinct_valid_same_epoch_observations_through_cutoff"` (`joulewise/calibration_bracketing.py:88`, tag at :86). The build path (`scripts/build_calibration_acceptance_successor.py:292-336`) walks every grouped content-distinct observation through the cutoff, keeps rows classified `valid` in the active epoch as corpus members, and records all others in the prior set. The artifact validator (`_valid_successor_acceptance_bound`, `calibration_bracketing.py:1124-1133`) requires `corpus.selection` to equal the constant and `members` length to equal `n`.

**(3) Changed since 399ffeb.** The selection constant and rule are unchanged. The only touch inside Q1's enforcement is the corpus-size floor raised from 2 to `SUCCESSOR_MINIMUM_CORPUS_SIZE = 19` (see Q13). Separately, the Q11 rework (build script :309-314) now refuses the ENTIRE build (`successor_trigger_lacks_parent_disposition`) whenever any trigger-content id in the parent probe's `new_content_ids` is present while the parent probe's single GLOBAL outcome is not `successor_required` — a build-level predicate against the parent probe's overall outcome, not a per-observation disposition record. This changes when trigger observations can reach the Q1 selector via the trigger path, without changing the selector itself.

**(4) Strongest argument FOR.** D-109 — BODY R2.8 defines the corpus-doubling trigger over exactly this universe: 38 **total** authenticated, content-distinct, valid same-epoch observations, including previously blind observations once unblinded — not 38 post-cutoff observations. A successor re-derivation is the event R2.8's counting rule exists to trigger; deriving from any narrower universe than the one counted would make the trigger and the derivation disagree about what the corpus is. On this reading, D-109 — BODY R2.2 ("derivation_corpus remains exactly the n=19 threshold-producing observations") is an issuance-time statement about the parent v2 artifact's recorded field, not a standing constraint on successors — the frozen-n=19 reading misapplies it. D-109 — BODY R2.3's completeness mandate (every content-distinct governed calibration observation in the prior set) supplies the same-universe consistency ground.

**(5) Strongest argument AGAINST.** The refuter's Q1 finding survives the rework essentially intact (assembler characterization, contestable), because the selection rule is byte-identical to 399ffeb. Two limbs: (a) D-116 — BODY (Window-B completeness note) states the two valid Window-B calibration fiducials "are EXCLUDED from the frozen n=19 threshold basis (which is Window-A-only) and do not influence the bound" — the implemented selector, which filters only on content-distinct/valid/same-epoch, absorbs them into a threshold-producing basis, converting observations recorded as bound-inert into bound-driving members. (b) Under D-109 — BODY R2.2 read as standing text, prior-set valid members that were never trigger-disposed (the refuter counted ~11 of 30 at the original cutoff) enter the threshold basis without any disposition event licensing absorption. Assembler characterization (contestable): the R2.6 limb of the prior objection — trigger observations absorbed without disposition — is now addressed for the trigger path by the Q11 build-refusal predicate (which refuses the whole build unless the parent probe's global outcome was `successor_required`); it does not reach prior-set members, for whom R2.6's gate arguably never applies and the R2.2/D-116 question remains live.

**(6) Prior-round evidence (prior round, pre-rework).** Cold Fable: **RATIFY** — complete valid same-epoch prefix; per COLD-FABLE-RULING.md:16-17 the ruling's own words ground it in "D-102 pin 2's 19→38 trigger and D-116 R2.8 counting"; frozen-n=19 misapplies the issuance-time statement. NOTE for the gate: the prior judge attributed the R2.8 counting rule to D-116; this packet's byte-verified extracts carry R2.8 as a clause of D-109 — BODY (D-116 — BODY applies "R2.8 counting" in its disposition inventory). Whether the prior judge mis-cited, or read D-116's application of R2.8 as its source, is unresolved and bears on how much of the prior RATIFY survives; see UNSWEPT EVIDENCE item 3. Opus refuter: **CONTRACT-BREAK** — selector absorbs the two valid Window-B fiducials D-116 marks bound-inert; R2.2/R2.6 (omitted from that packet) contradict absorption of never-disposed prior-set members. The synthesis REMANDED Q1 as genuinely contested, to be ruled only with the D-109 R2.2/R2.5/R2.6 and D-116 Window-B texts in front of the gate — this packet places them (see D-109 — BODY, D-116 — BODY).

**(7) If the gate rules the other way.** The rule is a single named constant enforced at three sites (constant :88, builder walk :292-336, validator equality :1124-1133); a Window-A-only or disposed-members-only ruling changes the builder's filter and the constant's string, and recomputes every downstream statistic — `n`, sample sd, quantile df, the Q2 screen value, the Q4 boundary count, and whether the corpus clears the Q13 minimum of 19 (a narrower universe falling below 19 refuses issuance outright under the current guard). No other code shape changes; artifacts already issued are unaffected because none exist beyond the parent.

**(8) Decision the gate must return.** Which universe the successor corpus-selection rule enumerates — as implemented (all content-distinct valid same-epoch through cutoff), Window-A-only, or parent-basis-plus-disposed-triggers — and specifically whether (i) the two valid Window-B calibration fiducials and (ii) prior-set valid members never trigger-disposed are licensed members of a successor threshold basis.

---

### Q2 — Preflight level-screen source

**(1) Question.** From which quantity is the successor artifact's preflight level screen — the comparator against which every new valid observation's bound is judged, with excess classified as systematic failure — derived: the observed corpus maximum alone, or a rule that also incorporates a statistical prediction term. Historical context: the original exhibit (399ffeb) derived the screen as `max(observed_maximum, prediction_95)`; both prior judges rejected that rule, and the synthesis adopted observed-max-only as the design direction "subject only to the reassembled packet surfacing any ratified text that mandates otherwise (none was found by either judge)." The choice under review is the reworked implementation.

**(2) Code at ad5f3f7.** `SUCCESSOR_PREFLIGHT_SCREEN_RULE = "observed_corpus_maximum"` (`calibration_bracketing.py:94`, tag at :91). In `derive_successor_decimal_derivation`, `preflight_screen = maximum.quantize(1e-15, ROUND_HALF_EVEN)` (:510-512) — the corpus maximum alone. The 95% two-draw prediction is still computed and recorded in `source_statistics` (:490-494, :542) as derivation evidence, and the rule string is emitted in the artifact's `rounding.preflight_level_screen.source_rule` (:565). The probe compares each new valid observation's bound against this screen and refuses `systematic_refusal` when exceeded (:2095-2132). A third class is also classified systematic (verified ~:2109-2119): a `valid` observation whose bound lexeme fails to parse (`_decimal(...)` is None) — a malformed-lexeme observation reaches the Q5 persistent-refusal path through this branch, not through the screen comparison.

**(3) Changed since 399ffeb.** The screen was previously `max(observed_maximum, prediction_95)`; the prediction term was removed from the comparator and demoted to recorded evidence. This implements the cold judge's Q2 amendment verbatim, including the ROUND_HALF_EVEN 1e-15 quantization.

**(4) Strongest argument FOR.** Both sealed judges converged against the max() rule from opposite lenses: the prediction term (a two-draw dispersion statistic, ~3.80x the level maximum on the real corpus) is incommensurable with a level ceiling; the max() is a no-op at n=19 and binds only when the corpus is tightest — exactly the degenerate regime the screen polices — where it can only RAISE the refusal ceiling, loosening systematic classification in the anti-conservative direction of the project's worst prior defect class (RT-1). The observed maximum alone can never loosen: any bound exceeding everything ever validly observed is treated as a challenge requiring ruling (Q5), not absorbed. No evidence is lost, since the prediction remains a recorded derivation value; and neither judge found ratified text mandating the prediction term (the cold judge's own caveat: if such text exists, that is a packet-completeness problem — this packet's authority set, per DECLARED-AUTHORITY-TUPLE, now contains D-102, D-109, and D-117 in full, plus the placeholder COLD-GATE-U2-PENDING, for the gate to check).

**(5) Strongest argument AGAINST.** Assembler characterization (contestable): the prior Opus UNSOUND verdict attacked the discarded max() rule and does not carry against observed-max-only. What survives as the strongest case against the implemented choice: the observed maximum of a finite corpus is a sample path, not a distribution property. With the screen set at exactly the historical maximum, any new valid observation even infinitesimally above every prior one is classified systematic and — via Q5's persistent-refusal policy — permanently blocks automatic issuance pending an authority ruling. The screen is therefore guaranteed to be crossed eventually under any continuous bound distribution, converting an ordinary upper-tail draw into a chain-stopping event; a prediction-based ceiling was the mechanism that priced expected tail growth. The counter-reading of the same fact — that crossing the observed envelope SHOULD demand a ruling — is the FOR argument; the gate must decide which reading the screen's purpose ratifies. Additionally, if the gate finds any ratified text mandating a prediction-bearing screen in the now-complete authority set, the implemented rule would contradict it (none was found in the prior round).

**(6) Prior-round evidence (prior round, pre-rework).** Cold Fable: **RATIFY-AS-AMENDED** — amendment: screen from the observed corpus maximum alone, prediction stays a recorded derivation value (the amendment the rework implements). Opus refuter: **UNSOUND** — max() mixes incommensurable quantities and raises the systematic screen exactly when the corpus is tightest, anti-conservative in RT-1's direction (an objection against the now-removed rule). Synthesis: convergent rejection of max(); observed-max-only adopted as design direction, binding finding 1.

**(7) If the gate rules the other way.** The derivation source is one expression (:510-512) plus the emitted `source_rule` string (:565); the prediction values are already computed and recorded, so reinstating a prediction-bearing comparator is a localized change to the derivation function and the rule constant, plus regenerated tests. It would also shift the Q5 systematic-classification boundary upward whenever the prediction exceeds the maximum (the loosening both prior judges identified), and any successor derived meanwhile under observed-max-only would carry a screen no looser than the reinstated rule would have minted; whether that discrepancy is acceptable, and in which direction it cuts, is for the gate. No issued artifact is affected; none exists beyond the parent, whose screen is the D-102-ratified literal either way.

**(8) Decision the gate must return.** Which source rule mints the successor preflight level-screen comparator: the observed corpus maximum alone (as implemented), the historical `max(observed_maximum, prediction_95)`, or another rule the gate finds mandated by the quoted authorities.

---

### Q3 — Numerical method: compatibility pins vs verified kernel

**(1) Question.** By what numerical method are Student-t quantiles produced for successor derivations, given that the parent artifact's authenticated bytes embed df=18 quantile literals ratified by D-102 — BODY (bench numerical-CDF inversion, 2026-08-01) that two independent computations now place in disagreement with the ratified value at the 11th decimal for p=0.995. The choice under review is the split the exhibit presents: the ratified pins reproduce the PARENT derivation exactly; the independently checked kernel derives all SUCCESSORS.

**(2) Code at ad5f3f7.** `decimal_student_t_quantile(probability, df, *, use_compatibility_pin=True)` (`calibration_bracketing.py:415`, tag at :95) bisects the Student-t survival function at 80-digit precision to bracket width 1e-72 (midpoint error at most 5e-73 conditional on exact survival-function evaluation); when `use_compatibility_pin=False` the df=18 D-102 ratified literals (:169-176) are skipped and the numerical path runs unconditionally, supporting independent verification. The continued fraction (:334-382) iterates to `SUCCESSOR_CONTINUED_FRACTION_MAX_ITERATIONS = 10_000` (:100) and returns only when both the per-step multiplicative change and the full-value delta across the iteration are within epsilon (:371-376); nonconvergence raises `CalibrationAcceptanceNumericalRefusal("successor_quantile_continued_fraction_nonconvergence")` (:379-381).

**(3) Changed since 399ffeb.** The `use_compatibility_pin` bypass is new (there was no way to run the algorithm at df=18); the iteration cap became a named constant; the convergence test gained the second full-value-delta conjunct; the failure path changed from bare `ArithmeticError` to the governed refusal class (:179-184). New evidence files: `docs/process_traces/2026-08-07-u2-coldgate/Q3-KERNEL-EVIDENCE.md` and the raw oracle grid `Q3-MPMATH-ORACLE-GRID.json`.

**Status of the kernel evidence file — two coexisting states the gate must weigh.** Q3-KERNEL-EVIDENCE.md at ad5f3f7 OPENS with: "Status: PARTIAL — the required mpmath oracle could not be installed in this sandbox. … The re-convened gate must not treat this document as closing that named requirement." A LATER APPENDED section ("MPMATH ORACLE RUN (lead bench, 2026-08-08 — closes the environment-blocked mandate)") claims closure of exactly that requirement; the header was never updated. The two states coexist in the committed file, and resolving them in favor of closure is the gate's call, not this packet's. Provenance facts a judge needs before crediting the oracle run: (a) the oracle-run section is dated 2026-08-08 — the future, relative to this 2026-08-07 convening; (b) the generating script is custodied only as a scratchpad `mpmath_oracle.py` — it is not in the repository, so the oracle run is not reproducible from repository bytes (the raw grid JSON is committed beside the evidence file).

**Kernel evidence (as presented by Q3-KERNEL-EVIDENCE.md at ad5f3f7; raw grid custodied beside it):**

| verification | scope | result |
|---|---|---|
| Independent 120-digit Decimal hypergeometric/Newton fallback (Sol sandbox; mpmath uninstallable, no network) | df=1..79, p ∈ {0.975, 0.995}, pin bypassed incl. df=18; full per-df table in the evidence file | max production-vs-fallback deviation 2.469e-69 at (df=59, p=.975) |
| mpmath 1.4.1 oracle run claimed at the lead bench (dps=120, tol 1e-110; dated 2026-08-08; script off-repo — see status note above) | df=1..80, 160 points, pin bypassed | max absolute kernel-vs-oracle deviation **3.106e-69**; confirms the fallback grid |
| Checked-in non-pinned df=37 regression reference | production vs independent-series value | compared within 1e-60 |

| pin vs independently computed value (df=18) | value |
|---|---|
| pin(18, 0.975) − independent value | 3.194616191395558598446630825e-15 |
| pin(18, 0.995) − independent value | 2.502272361194206686381792572e-11 |
| D-102 ratified bench value 2.878440472713585 − independent value | 2.502311780587872656463160790e-11 |

The evidence file's stated reading (the file's own position, not the packet's): the retained pins are faithful ~79-digit extensions of the ratified-but-imperfect bench values — on its reading the July bench inversion erred at the 11th decimal for p=0.995 — while the kernel agrees with both independent computations to ~69 digits at every grid point; the pin discrepancy's effect on the derived budget is ~1e-14 s against a 1.08e-2 s screen. The evidence file argues its own conclusion ("the only coherent resolution"); the gate should weigh the numerical agreement of the two independent checks as evidence, while noting that "which value is authoritative" is exactly the kernel-vs-ratified-bytes question presented in (8). The exhibit retains the governed pins because changing them would alter authenticated derivation bytes, which exceeds the remand's authority.

**(4) Strongest argument FOR.** The split preserves both invariants the record treats as non-negotiable. Backward: the pins reproduce the parent's authenticated derivation byte-exactly — the D-102 literals are ratified operatives, and the refuter's own banked replay (all five D-102 ratified operatives reproduce exactly through the pinned constants; see UNSWEPT EVIDENCE item 2 — the replay itself is not inspectable from this packet) depends on them; silently "correcting" ratified bytes outside a ratification act is the self-attestation direction this project escalates on. Forward: every successor value is minted by a kernel checked against two independent computations at every df it will ever compute — the claimed mpmath oracle at dps=120 over all 160 grid points, deviation ≤ 3.106e-69, which the evidence file presents as addressing the synthesis's named lift conditions (≥100-digit oracle, grid including df=18 pin-bypassed, stated convergence/error bound, governed nonconvergence refusal). Whether those conditions are in fact satisfied is for the gate; the file's own PARTIAL header and the provenance facts above bear directly on that. The physical consequence of the retained pin discrepancy is ~1e-14 s against a 1.08e-2 s screen — nine orders below the instrument's attribution limit.

**(5) Strongest argument AGAINST.** Assembler characterization (contestable): the rework addresses the core of both prior objections — "algorithm short-circuited at the only verified df / only test asserts the pin against itself" via the bypass plus the 160-point grid; "ArithmeticError at 10k iterations with no governed refusal" via the refusal class; "bisection tolerance asserted, never bounded" via the stated stopping rules and the empirical end-to-end bound (the evidence file itself notes the Lentz threshold is an operational rule, not a tail theorem). What survives: (a) the refuter's 63-unratified-digits finding — the kernel emits ~80-digit values of which D-102 ratified 16; those digits enter `derivation_sha256` and become authenticated chain bytes without any ratification act covering them, and the synthesis explicitly requires "a ruling on the 63 unratified digits" as part of closing Q3 — independent verification establishes their numerical agreement, not their ratification status; (b) the split institutionalizes, inside a lineage that elsewhere refuses on any byte disagreement, a pinned value that differs from the independently computed value by 2.5e-11: a future successor whose corpus returns to n=19 would compute the kernel's df=18 quantile, so parent and successor would carry values differing by 2.5e-11 at identical (df, p) — a permanent, documented intra-chain inconsistency, where the alternative (re-ratifying corrected literals) trades that for a supervised amendment of ratified bytes; (c) the closure evidence itself carries the PARTIAL/closure contradiction and off-repo provenance stated in (3).

**(6) Prior-round evidence (prior round, pre-rework).** Cold Fable: **DEFER** — structure sound, but the pin short-circuited the algorithm, no reference comparison at any df, ~64 unratified digits; lift conditions: ≥100-digit oracle over a (df, p) grid including df=18 pin-bypassed, plus a stated convergence/error bound. Opus refuter: **UNSOUND** — algorithm short-circuited at the only verified df, dictionary-lookup test, 63 unratified digits hashed into derivation_sha256, bare ArithmeticError, tolerance asserted not bounded. Synthesis: convergent — kernel unverified at every df it will compute; the named lift conditions are those the rework's evidence files address.

**(7) If the gate rules the other way.** (a) *Kernel-everywhere (drop the pins):* the flip is the `use_compatibility_pin` default and deletion of the :169-176 literals, but the parent's derivation would no longer reproduce from the code path — reproducing or amending the parent then requires a ratification act on the corrected literals (beyond this exhibit's authority) and touches the banked D-102 operative replay. (b) *Pins-as-ratified (pin df=18 forever):* successors reaching df=18 would embed the value that differs from the two independent computations by 2.5e-11; all other dfs use the kernel regardless, since pins exist only at (18, 0.975/0.995). (c) *Re-ratification of corrected pins:* requires an authority ruling amending D-102 literals, outside the remand; the mechanical sites are the same either way. In all cases the ~1e-14 s budget effect is unchanged in magnitude; what differs is which bytes are authenticated and what act licenses them.

**(8) Decision the gate must return.** Whether the pins-reproduce-the-parent / kernel-derives-all-successors split is the governed numerical method for Student-t quantiles in this lineage — including (i) the disposition of the df=18 compatibility pins given the comparison table above, (ii) the ratification status of the unratified digits (~63 beyond D-102's 16) that kernel-minted values contribute to `derivation_sha256` in successor artifacts, and (iii) whether the Q3 evidence file, given its coexisting PARTIAL header and closure-claiming appendix and its off-repo oracle script, discharges the synthesis's named lift conditions.

---

### Q4 — Count-boundary progression and the versioned-per-entry boundary rule

**(1) Question.** After the ratified 19→38 corpus-doubling trigger (D-102 — BODY, pin 2), what rule governs subsequent count boundaries — the exhibit implements retain-until-crossed-then-double-the-newly-issued-corpus-count, now recorded as a versioned rule name on every registry entry — and is the irreversibility that remains after versioning correctly characterized and acceptable as disclosed?

**(2) Code at ad5f3f7.** Two named rules exist: `GENESIS_COUNT_BOUNDARY_RULE = "d102_initial_total_valid_same_epoch_count_38"` and `_COUNT_BOUNDARY_RULE_RETAIN_THEN_DOUBLE`, with `_SUPPORTED_COUNT_BOUNDARY_RULES` as a closed set (`joulewise/calibration_bracketing.py:101-113`). Every registry entry must carry a `count_boundary_rule` field in the supported set (`_valid_registry`, lines 667, 691-692); a root entry must carry the genesis rule (line 724); a successor entry's rule must match the rule recorded inside its own artifact, and the boundary value is recomputed under that entry's recorded rule, with three distinct refusal codes for rule mismatch, unsupported rule, and wrong boundary value (lines 879-899). The checked-in registry JSON at ad5f3f7 carries the one-line genesis-rule field (already migrated). The Q8 migration shim injects the genesis rule into a legacy single-entry root only from authenticated committed HEAD bytes.

**(3) Changed since 399ffeb.** Previously a single module-level rule string was applied to all entries with no per-entry field, and the loader recomputed the expected boundary for every chain entry and returned `None` for the whole registry on any ancestor disagreement — the undisclosed one-way door of SYNTHESIS binding finding 6. New at ad5f3f7: per-entry rule versioning, the genesis rule, root/successor schema checks, the three refusal codes, and (via Q7) typed refusal reasons in place of bare `None`. What remains irreversible, now disclosed: an issued entry is permanently bound to its recorded rule and recorded boundary value (artifact immutability); a rule name can never be removed from the closed supported set without bricking issued ancestors that carry it; a future ruling changing the schedule can act only prospectively, by adding a new rule name carried by later entries. At ad5f3f7 no successor artifact has issued, so this residual irreversibility is potential, not yet actual.

**(4) Strongest argument FOR.** Retention-until-crossed is the more conservative reading of D-102 — BODY pin 2, whose only ratified number is 38 (the pre-rework Fable judge's ground); the versioning converts the previously undisclosed one-way door into a per-entry recorded fact with diagnosable disagreement, preserving fail-closed verification of every ancestor while leaving prospective rule change structurally possible; and permanently binding an issued entry to the rule that produced it is the same immutability trust shape as the hash-chained ledger itself (D-109 — BODY, R1 clauses) — a chain whose issued judgments could be retroactively re-ruled would be the greater defect.

**(5) Strongest argument AGAINST.** The pre-rework refuter's objection had two limbs. Limb 1 survives the rework untouched (assembler characterization, contestable): the implemented schedule is batch-dependent — a corpus crossing the 38 boundary at n=40 yields a next boundary of 80, whereas a fixed-doubling reading of D-102's "corpus doubling (19→38)" continues 38→76; the boundary sequence thus depends on batch arrival timing, and versioning discloses this choice but does not supply ratified authority for it — `_COUNT_BOUNDARY_RULE_RETAIN_THEN_DOUBLE` is an unratified generalization now stamped into every future entry. Limb 2 (the undisclosed one-way door: whole-registry `None` on any ancestor boundary disagreement, making the rule retroactively irreversible) is, on the assembler's characterization, addressed in its undisclosed form by the per-entry versioning and typed refusals; what survives of it is the narrower, now-disclosed residue in (3): issued entries can never be re-ruled, and the supported set can only grow.

**(6) Prior-round evidence (prior round, pre-rework).** Cold Fable: RATIFY — retention pending boundary then 2× the newly issued count; 38 the only ratified number; retention the more conservative reading. Opus refuter: UNSOUND — batch-dependent schedule (40→80, not 76) plus the undisclosed one-way door in the loader's whole-registry `None`. Synthesis: binding finding 6 — the undisclosed one-way door was found and recorded as a defect requiring disclosure/rework; the schedule question was to be re-presented with the irreversibility explicit, which (3) above now states.

**(7) If the gate rules the other way.** A different schedule (e.g., fixed doubling of the ratified sequence) becomes a new rule string added to `_SUPPORTED_COUNT_BOUNDARY_RULES` and carried by future entries; the root's genesis-rule field (recording the ratified 38) is unaffected; because no successor has issued at ad5f3f7, no chain surgery is required — the change is a constant/predicate change at the validated sites plus the ruling's record. Verified fact bearing on this element (critic pass): the loader recomputes boundary values only for the `retain_then_double` rule; a successor entry carrying the genesis rule refuses `acceptance_registry_boundary_rule_unsupported` — the "closed supported set" is effectively single-member for successor entries, so adding a new schedule additionally requires a recompute branch for the new rule, not only a new string. Conversely, if the implemented rule is ratified, the first issued successor permanently records it, and any later schedule change applies only from the next entry forward.

**(8) Decision the gate must return.** (a) Whether retain-until-crossed-then-double-the-issued-corpus-count is the correct reading of D-102 — BODY pin 2's doubling trigger, or whether a different progression is required; (b) whether the per-entry versioned rule with a closed supported set and recompute-under-recorded-rule verification is accepted as the disclosure mechanism for the residual irreversibility stated in (3), which the gate is asked to ratify or reject as an explicitly labelled irreversible property.

---

### Q5 — Persistent systematic refusal and the closure question

**(1) Question.** When the probe encounters a new same-epoch observation that is systematic-invalid, valid with a bound exceeding the preflight screen, or valid with an unparseable bound lexeme (see (2)), it refuses automatic successor issuance persistently, pending a new ruling, and no automatic path can consume or age out that observation. Is this the correct implementation of D-102 — BODY pin 2's mandatory re-derivation trigger ("a new systematic failure challenging the pre-flight screen"), and what event constitutes CLOSURE — the point at which such an observation stops being "new" so the trigger can be discharged?

**(2) Code at ad5f3f7.** `SUCCESSOR_SYSTEMATIC_POLICY = "persistent_refusal_pending_new_ruling"` (`joulewise/calibration_bracketing.py:116`). The probe classifies as systematic any new same-epoch observation that is systematic-invalid, or valid with a bound exceeding the preflight screen, or valid with a bound lexeme that fails to parse (`_decimal(...)` is None) — all three classes verified at ~:2109-2119/2095-2132 — and returns `outcome="systematic_refusal"` with trigger `new_systematic_failure_challenges_preflight_screen` and the policy string as refusal reason. A malformed-lexeme night therefore reaches this persistent block through a path independent of the screen comparison. Nothing in the automatic path consumes or ages out such an observation; no field, disposition, or code path exists by which a subsequent ruling retires it from "new". Under Q11's build predicate, trigger absorption requires the parent probe's single global outcome to be `successor_required`; a `systematic_refusal` outcome therefore refuses any absorbing build.

**(3) Changed since 399ffeb.** The refusal mechanism itself is unchanged (constant, comparator shape, outcome identical). What changed around it: (a) per Q2, the screen it compares against is now the observed corpus maximum alone (the 95% two-draw prediction demoted to recorded evidence), which can only lower or hold the refusal ceiling — the refusal now fires at least as readily as before; (b) per Q6, no-content closures no longer categorically block, so this refusal is the remaining persistent-block class; (c) the closure gap named by the SYNTHESIS ("rework must define CLOSURE") is not addressed in code at ad5f3f7; (d) the engine-vs-writer classification conflict also stands in code — the live writer's hardcoded screen literal remains out of this exhibit's scope (Q12, `WRITER_INTEGRATION_SCOPE_STATUS`), covered operationally by the pre-rework Q12 amendment making writer copied-scalar removal a named blocking unit for live nights. Parity fact (verified, cuts both ways): the writer's hardcoded `PREFLIGHT_SYSTEMATIC_SCREEN_S = 0.033558756679900` (`scripts/validate_powermetrics_fiducial.py:103`) equals the parent artifact's `preflight_level_screen_s` literal (`calibration_bracketing.py:81`) byte-for-byte today — the two authorities agree until the first successor issuance changes the engine's screen.

**(4) Strongest argument FOR.** D-102 — BODY pin 2 makes a systematic challenge a mandatory trigger, and its second conjunct plus D-109 — BODY R2.5/R2.6 forbid a threshold absorbing its own challenge; a persistent refusal pending an authority ruling is the only shape that cannot self-serve — any automatic aging-out or absorption rule would let the mechanism adjudicate the very evidence that impeaches it. The cost is availability, never soundness (the pre-rework Fable judge's ground), which matches the project's ratified fail-closed posture; and closure-by-ruling rather than closure-by-code is arguably the point: what discharges a challenge to a ratified screen is a ruling, which is precisely what the policy string names.

**(5) Strongest argument AGAINST.** The pre-rework refuter's core objection SURVIVES the rework in full (assembler characterization, contestable): D-102's trigger is a mandatory RE-DERIVATION trigger — the ratified response to a systematic challenge is re-derivation under governed process, not indefinite paralysis — and the exhibit converts it into a closure-less deadlock: "pending_new_ruling" names no mechanism (no ruling-reference field, no governed disposition, no re-derivation route) by which any ruling, however authoritative, discharges the observation; meanwhile the active artifact remains operative for claim evaluation, so science continues under a challenged screen while every subsequent trigger is unreachable behind the refusal. The engine-second-guesses-writer limb also survives in code (writer integration explicitly out of scope). Assembler characterization (contestable): the Q2 rework removes the anti-conservative `max()` comparator that made refusal fire in the wrong regime, and the Q6 rework removes the no-content categorical block that compounded the deadlock — but the closure gap itself is byte-identical to the state both judges saw.

**(6) Prior-round evidence (prior round, pre-rework).** Cold Fable: RATIFY — forecloses the threshold absorbing its own challenge; cost is availability, not unsoundness. Opus refuter: UNSOUND — mandatory re-derivation trigger converted to a closure-less deadlock; engine second-guesses the production writer's valid classifications; Q5×Q12 night-killer composition. Synthesis: the rework must define CLOSURE; the question was to be re-presented with the closure gap explicit — it is presented here unchanged in code, per (3)(c).

**(7) If the gate rules the other way.** If the gate requires a defined closure mechanism, the comparator and refusal shape (lines 2109-2132) stand and a governed discharge path is added — the isolated policy constant and refusal-reason string localize the change; the gate's ruling would specify the discharge event and its recorded form. If the gate ratifies persistent refusal as implemented, closure remains an out-of-band authority action with no consuming code path at ad5f3f7, and the first systematic-classified observation on any night ends automatic issuance until such a path is separately built and ratified; the chain's availability then depends entirely on ruling latency.

**(8) Decision the gate must return.** (a) Ratify or reject persistent-refusal-pending-ruling as the implementation of D-102 — BODY pin 2's systematic trigger; (b) define closure: the specific event, and its required recorded form (e.g., a ruling ID referenced in a successor artifact, a governed ledger disposition, a re-derivation under a newly ratified screen — the gate chooses the form; the packet takes no position), after which a systematic-classified observation is no longer "new"; (c) whether the engine-vs-writer classification conflict must be resolved in code before any live night relies on this path, or remains adequately covered by the Q12 blocking-unit amendment.

---

### Q6 — No-content / abandoned observation handling

**(1) Question.** D-109 — BODY R1.2 designs `abandoned` as one of four terminal finalization states, and its reservation-first protocol (append `pending` before capture begins) guarantees abandoned rows whenever a capture dies before producing bytes — the ordinary overnight-abort path. The rework replaces the original categorical block on any no-content observation with an admission path that authenticates each no-content row as a terminal abandoned closure against its ledger receipt and excludes it from the corpus. Is this admission path sound under R1.2's text, now in the packet?

**(2) Code at ad5f3f7.** `SUCCESSOR_NONCONTENT_POLICY = "exclude_authenticated_terminal_no_content"` (`joulewise/calibration_bracketing.py:120`). `_terminal_no_content_rows` (lines 1802-1850) authenticates each no-content observation as a terminal `abandoned` closure — no content_id, no artifact hashes, no bound lexeme, non-empty attempt_id and custody_locator — against its ledger receipt (matching event type, receipt_digest, attempt_id, disposition, and emptiness fields), raising `successor_terminal_no_content_closure_invalid` / `successor_terminal_no_content_receipt_malformed` otherwise. `_governed_noncontent_rows` (lines 2682-2699) merges these with shape-hardened governed-unused-slot rows (lines 2648-2671) and refuses on key collisions (`successor_noncontent_closure_conflict`); the builder (`build_calibration_acceptance_successor.py:294-296`) and prefix matcher (lines 2756-2763) consume the merged set; the artifact validator accepts disposition `"abandoned"` alongside `"governed-unused-slot"` with attempt/sequence/receipt uniqueness enforced across all noncontent rows (lines 1208-1242); the probe authenticates new no-content closures inline and refuses diagnosably on malformed shapes (lines 2054-2067).

**(3) Changed since 399ffeb.** Previously `_noncontent_rows` raised unconditionally — any no-content observation categorically blocked automatic issuance — and the validator accepted only `governed-unused-slot`. New: the authenticated-abandoned admission path, receipt authentication, the merge function, the uniqueness hoist, and diagnosable refusals on malformed receipt shapes (the site of the pre-rework unguarded-KeyError rider).

**(4) Strongest argument FOR.** The rework admits exactly the terminal state R1.2 designs, on exactly the failure path R1.2 exists to catch: SYNTHESIS binding finding 4 established (code-verified, undisputed) that the old unconditional raise permanently bricked automatic issuance on the designed overnight-abort path — the first abandoned row ended automatic succession for the life of the immutable ledger. The admission is narrow: a row qualifies only by matching its immutable hash-chained receipt on disposition, attempt identity, and strict emptiness, with cross-row uniqueness and collision refusal; every malformed, conflicting, or ambiguous shape still refuses diagnosably. Under R1.2, `abandoned` is a finalized — resolved — state, so excluding it from the corpus is consistent with D-109 R2.6's refusal rule for unresolved attempts rather than in tension with it.

**(5) Strongest argument AGAINST.** Assembler characterization (contestable): the pre-rework refuter's CONTRACT-BREAK argued against the unconditional raise on R1.2's designed terminal state, which no longer exists, and the KeyError rider is addressed by the diagnosable refusal path (lines 2054-2067). The surviving adverse case is new and runs against the implemented choice itself: (a) authenticated exclusion is unbounded — no count, rate, or trigger treats a stream of abandoned closures as itself a signal, so a systematically failing rig (the D-079 cl.2 lens: repeated pre-bytes deaths may BE a systematic failure mode) produces rows that never enter the threshold basis, never challenge the preflight screen, and never surface in any refusal — the one terminal state whose accumulation is invisible to the Q5 trigger; (b) the reading that an abandoned closure is "resolved" under D-109 R2.6 is an interpretive choice the exhibit makes, not ratified text — R2.6 could be read as requiring that attempts which produced no judgeable content cause refusal until affirmatively dispositioned by something beyond shape authentication; (c) admission turns exclusion into a permanent, authenticated fact of every future successor's derivation, whereas the old block, however costly, forced each such row in front of an authority.

**(6) Prior-round evidence (prior round, pre-rework).** Cold Fable: RATIFY of the then-categorical refusal — "the only non-concealing default given the evidence machinery that exists" — issued without R1.2 in front of him; the SYNTHESIS holds that RATIFY does not survive R1.2 and vacated it. Opus refuter: CONTRACT-BREAK — R1.2's terminal `abandoned` plus reservation-first means the first ordinary overnight abort permanently bricks automatic issuance; plus the unguarded KeyError on receipt-shape variation. Synthesis: binding finding 4 — the brick on the designed overnight-abort path is established; the rework was to present an admission path under R1.2's full text, which this section does.

**(7) If the gate rules the other way.** If the gate rejects the admission path — ruling abandoned rows must block, or must require a disposition beyond receipt authentication — the isolated sites are `_terminal_no_content_rows`, `_governed_noncontent_rows`, and the validator's accepted-disposition set; a rejection ruling would also need to state what discharges an abandoned row, since an unconditional block re-creates the behavior SYNTHESIS binding finding 4 recorded on the designed overnight failure path. If the gate ratifies, the first overnight abort exercises the path live and authenticated exclusion becomes part of every future successor's derivation bytes, with any later bound on accumulation requiring a fresh ruling.

**(8) Decision the gate must return.** (a) Whether an authenticated terminal `abandoned` closure is "resolved" within the meaning of D-109 — BODY R2.6 (terminal per R1.2, hence excludable) or a refusal-causing state pending further disposition; (b) whether the authentication predicate — receipt match, strict emptiness fields, attempt/sequence/receipt uniqueness, collision refusal — is sufficient for admission; (c) whether unbounded abandoned-row exclusion is acceptable, or whether accumulation of abandoned closures must itself feed a systematic-signal trigger — and if so, in which unit (this exhibit or the out-of-scope writer/arm path per Q12).

---

### Q7 — v3 lineage, naming, parent availability, and the loader failure surface

**(1) Question.** Must successor artifacts use the v3 schema with cutoff-derived immutable filenames (`calibration_acceptance_v3_s<seq>_<digest16>.json`), form a single-parent ancestry rooted at the issued v2 anchor with every registered ancestor's exact bytes present and authenticated in the current checkout, and must every registry-loading failure surface as a typed refusal carrying a stable reason code rather than an undifferentiated failure value? The prior packet left "parents always present" versus "recoverable from Git history" open for the gate; the rework additionally puts the loader's diagnosability design in front of the gate as part of this question. Authority context: `SUCCESSOR_DECISION_IDS` (see DECLARED-AUTHORITY-TUPLE) names D-102, D-109, D-117, and the placeholder `COLD-GATE-U2-PENDING` (disposed of in §3 and §6); D-109 R1.3 and R1.5 (see D-109 — BODY) govern immutability, permanent retention, and refusal-not-omission for missing required bytes.

**(2) Code at ad5f3f7.** `SUCCESSOR_LINEAGE_POLICY = "immutable_present_single_parent_cutoff_named_v3"` (`joulewise/calibration_bracketing.py:123`; tag at :121-123). v3 names must match the cutoff-derived pattern against the entry's own cutoff (:166-168, :848-863). The secondary Q7 site anchors `load_calibration_acceptance_registry` (docstring :784): every fail-closed branch raises `CalibrationAcceptanceRegistryRefusal` with a stable reason code — path substitution, unreadable/outside-repo, missing commit, schema/ancestry invalid, artifact-path substitution, artifact unreadable, artifact missing commit, artifact authentication failure, successor-name invalid, parent missing, the three boundary codes (Q4), and lineage invalid (:786-911) — and the return type is `dict`, never `None`. Registered artifact bytes are themselves checked against Git HEAD when committed mode is required (:822-828). Missing parents refuse (`acceptance_registry_parent_missing`, :877-879 region). The probe converts loader refusals into `authentication_or_epoch_refusal` results carrying the reason (loader-refusal conversion at ~:1939-1947, `except CalibrationAcceptanceRegistryRefusal … refusal_reasons=(exc.reason,)`; the separate branch at :2002-2016 is the identity-epoch mismatch check with the fixed reason `observed_identity_epoch_mismatch`).

**(3) Changed since 399ffeb.** The lineage policy, naming rule, and present-in-checkout requirement are unchanged. New: the loader previously returned `None` for every failure mode; the refusal-code taxonomy, the non-optional return type, and the per-artifact HEAD-byte check are all new.

**(4) Strongest argument FOR.** Exact on-disk ancestry keeps the trust chain reviewable and available to ordinary consumers without reconstructing Git history, and immutable cutoff-derived paths prevent overwriting authority bytes while preserving the issued v2 anchor as lineage root — the shape D-109 R1.3/R1.5's immutability-and-permanent-retention design points toward. The new taxonomy closes the diagnosability strain directly: fourteen formerly indistinguishable failure modes now each carry a stable reason that the probe records, so a refusing night is attributable from its evidence alone (the synthesis logged this as the should-fix the rework was to close). The HEAD-byte check on each artifact removes a gap where a worktree-substituted ancestor could pass hash authentication against a tampered registry row in non-committed contexts.

**(5) Strongest argument AGAINST.** D-102 prescribes neither v3 naming nor permanent working-tree retention of every ancestor; Git-authenticated recovery could retain exact bytes without making every inactive artifact a runtime dependency, and under the implemented rule a deleted ancestor or sparse checkout invalidates the *active* artifact — a whole-registry refusal on a row that no evaluation consumes. The refuter's Q4-amplifier strand (any ancestor disagreement bricks the whole registry) survives in this presence/authentication form (assembler characterization, contestable), though on the same characterization the rework addresses its sharpest instance: the boundary-rule one-way door is now versioned per entry (Q4), so a future rule change no longer retroactively invalidates issued ancestors. The diagnosability strand of the prior STRAIN ("14 failure modes collapse to bare None") is addressed by the taxonomy; what remains arguable is that a taxonomy is not a degraded mode — every reason still terminates in full refusal, and no partial-chain operation exists.

**(6) Prior-round evidence (prior round, pre-rework).** Cold Fable: RATIFY — "present-in-checkout; one authentication path; fail-closed on missing ancestors." Opus refuter: STRAIN — 14 failure modes collapse to bare None, no partial-chain degraded mode, carried as a Q4 amplifier. Synthesis: survives intact (no contract break found; Fable grounds adopted provisionally; diagnosability recorded as a rework should-fix; re-present with D-109 text).

**(7) If the gate rules the other way.** If Git-history recovery of ancestors is permitted, the loader must authenticate missing inactive parents from a defined commit/object identity and the present-in-checkout refusals become recovery paths; any different schema, name shape, prefix length, branching, or retention rule requires corresponding builder, registry-validator, and fixture changes. If the gate rejects the refusal-taxonomy design (e.g., requires a smaller closed reason set, or a partial-chain degraded mode), the reason codes are load-bearing in the probe's evidence records and in tests, so renaming or collapsing them is a coordinated change across :786-911, the loader-refusal conversion at ~:1939-1947, and the test file.

**(8) Decision the gate must return.** RATIFY / RATIFY-AS-AMENDED / REJECT on `SUCCESSOR_LINEAGE_POLICY = "immutable_present_single_parent_cutoff_named_v3"`, ruling explicitly (a) present-in-checkout vs Git-recoverable ancestors, and (b) whether the loader's typed refusal-reason taxonomy is the ratified failure surface for registry authentication.

---

### Q8 — Registry authority versus D-109 R1.4's second-store language

**(1) Question.** Is the committed acceptance registry — exactly one active row, exact SHA-256 authentication of every registered artifact's bytes — the sole rotating trust anchor for acceptance authority, and is such a registry compatible with D-109 R1.4 (see D-109 — BODY), whose anti-rollback design names a repo-committed *ledger head-pin* file as the authority and states "no second trusted latest-sequence store"? The gate must also rule on the rework's narrowly-scoped legacy-root migration shim, which is new trust-path code inside this authority.

**(2) Code at ad5f3f7.** `ACCEPTANCE_REGISTRY_AUTHORITY = "committed_registry_one_active_exact_sha256"` (`joulewise/calibration_bracketing.py:126`; tag at :124-126). `_active_registry_entry` requires exactly one active row (:914-921). New `_load_registry_for_current_active_selection` (:923-984) loads the committed registry and, on exactly the `acceptance_registry_missing_commit` reason, performs a one-shot legacy-root migration: it authenticates the OLD single-entry HEAD registry bytes, requires the entry to *lack* `count_boundary_rule`, injects the genesis rule, revalidates, and authenticates the HEAD artifact bytes/sha/derivation before returning — it never consumes worktree bytes and never permits an active-entry switch. `load_calibration_acceptance_bound` and `_acceptance_artifact_sha256` route through it (:1630-1632, :1701-1702). **Committed-registry topology fact (verified in the critic pass; the gate needs it to judge the shim):** `main` carries NO acceptance-registry file at all (absent from `git ls-tree -r main`), and the registry JSON at the exhibit head ad5f3f7 is already migrated (it carries the genesis-rule field). The "legacy single-entry root lacking the field" that the shim's precondition describes therefore corresponds to a committed state locatable on neither main nor the exhibit head as presented; on which checkout/commit the shim's precondition is actually reachable is NOT established by this packet — see UNSWEPT EVIDENCE item 5.

**(3) Changed since 399ffeb.** The authority constant and single-active-row rule are unchanged. The previous code downgraded to `require_committed=False` whenever the registry path was absent from HEAD; that downgrade is removed and replaced by the committed-bytes migration shim, which fires only on the one legacy-root schema condition.

**(4) Strongest argument FOR.** Authority rotates without minting a new executable constant per successor, while the active bytes, derivation, cutoff, and ancestry stay exact and Git-reviewed — a generalization of the committed-hash-pin trust shape the project already ratified for the v2 bootstrap (the prior Fable ground: every bootstrap pin matches D-116's ratified bytes exactly). On R1.4: the registry is not a second *latest-sequence* store for the ledger — it stores no ledger sequence claim of its own; each entry pins its artifact, and the artifact pins its ledger cutoff, so ledger-head authority remains solely the R1.4 head-pin design. The prior refuter *tested* the strongest adverse R1.4 second-store reading and REJECTED it. The rework strengthens the FOR: the old silent downgrade to uncommitted mode — a genuine hole in "committed registry is the authority" — is deleted, and the shim that replaces it consumes only HEAD bytes under full authentication.

**(5) Strongest argument AGAINST.** D-102 authenticates the artifact but never independently ratifies a registry as sole trust root, and the authority string is self-asserted by the code it governs — the refuter's surviving residual: nothing cross-checks the registry against the D-109 head-pin file, so acceptance authority and ledger authority are parallel committed anchors whose mutual consistency is only as strong as the artifact's internal cutoff pin. Assembler characterization (contestable): the rework addresses the downgrade objection (committed mode can no longer be silently escaped) but opens a new surface in its place: the migration shim *constructs* an authority object whose bytes were never committed as such — it injects `count_boundary_rule` into a HEAD entry that lacks it — so for the shim's lifetime, the operative registry object is HEAD-derived but not HEAD-identical, on an unratified code path that has never been through a gate, and whose triggering committed state this packet could not locate (see (2)). And during a first-ever publication window (see Q9), the shim is exactly what makes evaluation under the parent authority *possible* where a strict committed-mode reading would refuse.

**(6) Prior-round evidence (prior round, pre-rework).** Cold Fable: RATIFY — bootstrap pins match D-116's ratified bytes exactly; generalizes the committed-hash-pin trust shape. Opus refuter: STRAIN — strongest adverse reading (R1.4 second-store) tested and REJECTED; residual: self-asserted authority string, no cross-check against the head-pin file. Synthesis: survives intact (no contract break; Fable grounds adopted provisionally; re-present with D-109 text).

**(7) If the gate rules the other way.** If the registry is not accepted as sole rotating anchor, the replacement must be specified — a code pin per successor, a binding to the R1.4 head-pin file, a signed root, or another committed manifest — together with its rotation, rollback, and active-selection rules, and every consumer path (:1630-1632, :1701-1702) rewired to it. If the gate accepts the registry but rejects the migration shim, the legacy root must instead be re-committed with the genesis field before any successor work (a one-commit operation), and :923-984 collapses to a plain committed load. If the gate requires a head-pin cross-check, that is additive validation inside :786-911 with a new refusal reason.

**(8) Decision the gate must return.** RATIFY / RATIFY-AS-AMENDED / REJECT on `ACCEPTANCE_REGISTRY_AUTHORITY = "committed_registry_one_active_exact_sha256"` as compatible with D-109 R1.4's no-second-trusted-store language, ruling explicitly on (a) whether a registry↔head-pin cross-check is required, and (b) whether the one-shot legacy-root migration shim (:923-984) is ratified, amended, or replaced by a pre-committed schema migration — noting that the committed state its precondition requires has not been located (UNSWEPT EVIDENCE item 5).

---

### Q9 — Publication ordering: the mechanical co-landing barrier versus R1.4's no-evaluation window

**(1) Question.** Must successor artifact and registry co-land as one governed transition with no governed acceptance evaluation possible between authority movement and its Git commitment — the analog, for acceptance-authority rotation, of D-109 R1.4's rule that "NO claim evaluation may occur between ledger advancement and pin commit" (see D-109 — BODY, quoted in full there) — and does the rework's single-commit atomic-HEAD-advance mechanism satisfy that requirement as a mechanical property rather than an operational promise? The synthesis bound this question's direction (finding 5): the unbarriered replace→commit window of the original exhibit is not acceptable; the rework was to implement the barrier mechanically or present R1.4 with an explicit question on what mechanism satisfies it. Both are before the gate here.

**(2) Code at ad5f3f7.** `SUCCESSOR_PUBLICATION_POLICY = "single_commit_two_path_atomic_head_update_verified"` (`joulewise/calibration_bracketing.py:129`; tag at :127-129). `publish_successor` (`scripts/build_calibration_acceptance_successor.py:515`) takes an exclusive publish lock — precisely: a lock file resolved via `git rev-parse --git-path joulewise-successor-publish.lock` (git-directory-resident), opened `O_CREAT|O_RDWR|O_NOFOLLOW`, verified a single-hardlink regular file, then held under an advisory `fcntl.flock(LOCK_EX)` (:555-588). The lock is advisory and serializes only cooperating publisher processes on the same filesystem; it imposes nothing on independent consumer processes. The function then requires the registry's HEAD bytes to equal the expected parent bytes and the artifact path to be uncommitted (:590-593), requires a clean index, a worktree dirty only at the registry path, and untracked files only at the artifact path (:636-640), writes both files, builds a commit through an isolated `GIT_INDEX_FILE` (read-tree of old HEAD, add of exactly the two paths, write-tree, commit-tree with old HEAD as sole parent, :655-712), verifies via `diff-tree` that the commit touches exactly the two paths (:715-734), atomically advances HEAD with `git update-ref HEAD <commit> <old_head>` (:740), then re-loads the registry in committed mode requiring the new acceptance_id active and the artifact's HEAD bytes exact, raising `SuccessorDurabilityUncertain("successor_post_commit_selection_verification_failed")` otherwise (:750-768). Any failure before the ref advances rolls back both files (:776-780); the returned verification record (`commit`, `committed_paths`, `committed_mode_verified`) is merged into the build output (:837-846).

**(3) Changed since 399ffeb.** The original exhibit's policy was `artifact_first_registry_last_head_input_only`: two `os.replace` calls with the registry replace as the commit point and Git HEAD used only as input; it wrote no barrier of any kind. The co-landing commit, path-set verification, atomic ref advance, committed-mode post-verification, cleanliness preflight, and rollback are all new.

**(4) Strongest argument FOR.** The barrier is now a property of the machinery, not a promise: because every ordinary consumer loads in committed mode only (the Q8 downgrade removal is load-bearing here), the interval between the filesystem replaces and the ref advance is a state in which committed-mode loading cannot select the successor — evaluation against the new authority is impossible by construction, and authority transfer occurs at a single atomic compare-and-swap (`update-ref` with the expected old head). This implements both halves of the prior Fable amendment (one commit; recorded post-commit committed-mode verification) and answers the prior Opus CONTRACT-BREAK on its own terms: there is no longer a window in which moved authority awaits a separate commit, and the post-verify plus `SuccessorDurabilityUncertain` make a torn outcome loud rather than silent. The path-set verification and cleanliness preflight bound the commit to exactly the two governed paths, so the mechanism cannot smuggle unrelated worktree state into an authority commit.

**(5) Strongest argument AGAINST.** Assembler characterization (contestable): the prior refuter's core objection — no head pin written, a second unbarriered window, consumers refusing indistinguishably from "no registry exists" — is substantially addressed: the window between replace and commit is closed to successor-selection, refusals now carry reasons (Q7), and the transition is one atomic ref advance. What survives is narrower and interacts with Q8: during the window, a strict reading of R1.4's barrier ("NO ... evaluation may occur", not "no evaluation may succeed under the new authority") is not met, because for the first-ever legacy-root publication the Q8 migration shim would satisfy a concurrent consumer from the OLD committed authority rather than refusing — evaluation *occurs* mid-transition, under the parent artifact. (For all subsequent publications the shim's single-entry/no-field precondition fails and the window is a hard refusal. NOTE: the committed state on which this first-publication scenario is reachable has not been located — main carries no acceptance registry at all and the exhibit head's registry is already migrated; see Q8(2) and UNSWEPT EVIDENCE item 5.) A defender would answer that judging under the prior artifact is exactly D-102's prospective rule (D-109 R2.5); an objector would answer that R1.4 draws the line at *any* evaluation inside a rotation window, and that the advisory flock barrier is process-local — nothing serializes an independent consumer process except the committed-mode property itself. Additionally, the exhibit still writes no R1.4 head-pin file; the rework's position is that the head pin is U1 ledger machinery outside this exhibit's four files (Q12 scope), which the gate must either accept or reject as a scope ruling.

**(6) Prior-round evidence (prior round, pre-rework).** Cold Fable: RATIFY-AS-AMENDED — mechanism ratified, with a then-operational amendment: artifact + registry as ONE commit, no governed evaluation between publish return and HEAD, recorded post-commit committed-mode verification. Opus refuter: CONTRACT-BREAK — R1.4's no-evaluation barrier absent; no head pin written; a second, longer, unbarriered replace→commit window; concrete one-night strand scenario; mirror image of the sequencing class D-116's cold gate HELD on. Synthesis: convergent direction (finding 5) — the unbarriered window is not acceptable; barrier/co-landing must be mechanical, or R1.4 presented with an explicit mechanism question.

**(7) If the gate rules the other way.** If the gate holds that R1.4's barrier requires *hard refusal* during any rotation window, the change is confined to the Q8 shim's interaction (disable the shim during a held publication lock, or pre-commit the legacy-root migration so the shim never coexists with a publication) — the commit mechanism itself is unaffected. If the gate holds that the acceptance rotation must additionally bind the R1.4 ledger head-pin file into the same commit, `publish_successor`'s two-path set (:715-734) becomes a three-path set and the cleanliness preflight widens accordingly. If the gate rejects single-commit co-landing altogether in favor of a journaled or sealed-bundle transaction, :515-785 is replaced wholesale and the post-verification contract re-derives. If the gate ratifies as implemented, the recorded verification (`commit`, `committed_paths`, `committed_mode_verified`) becomes the required issuance evidence shape.

**(8) Decision the gate must return.** RATIFY / RATIFY-AS-AMENDED / REJECT on `SUCCESSOR_PUBLICATION_POLICY = "single_commit_two_path_atomic_head_update_verified"` as satisfying D-109 R1.4's barrier requirement applied to acceptance-authority rotation, ruling explicitly on (a) whether refusal-by-construction — including first-publication evaluation under the OLD committed authority via the Q8 shim — meets or breaches the no-evaluation window, and (b) whether the R1.4 head-pin file must co-land in the publication commit or remains U1/writer scope.

---

### Q10 — Probe over U1's governed open extension

**(1) Question.** May the pre-science trigger probe run while U1's governed two-slot bracket extension is open — a narrow exception to the terminal-committed-snapshot requirement that otherwise gates all successor machinery — or must the probe, like issuance, wait for a terminal committed ledger head? The question now carries a substrate change: the predicate the exception trusts is owned by U1, and U1's recovery shape has been redesigned since the first packet.

**(2) Code at ad5f3f7.** `PRE_PROBE_OPEN_SESSION_POLICY = "permit_governed_open_u1_extension_probe_only"` (`joulewise/calibration_bracketing.py:133`, tag at :130). The probe may inspect exactly U1's governed open two-slot extension; any triggered *build* is refused by `_assert_terminal_committed_snapshot` (`scripts/build_calibration_acceptance_successor.py:170-181`) unless every bracket session is aborted/finalized, the ledger head is committed, and the last receipt is not a reservation/session-open/slot-claim event. Issuance and the morning verdict therefore sit behind the terminal-committed assertion in both directions; only the read-only probe crosses it. NOTE: the trusted predicate itself (U1's `is_governed_open_bracket_extension`) has no file:line citation in this packet, in either its operative or its redesigned form — see UNSWEPT EVIDENCE item 8.

**(3) Changed since 399ffeb.** The constant and its enforcement are unchanged. The adjacent `_governed_unused_slot_rows` consumed by the probe was shape-hardened (described under Q6). The material change is *external to the exhibit*: the U1 recovery redesign landed on `impl/d117-ledger-recovery` (`c392d79` + fix round `c0e0257`, per `docs/process_traces/2026-08-07-d117-u-units/RECOVERY-SHAPE-CONSULT.md`) — the sidecar journal is deleted in favor of a ledger-resident intent protocol (append-intent/finalize/abandon control receipts in the main chain). That branch is ungated and unmerged (its own log records a D-118/D-121 gauntlet owed before PR). The governed-open-extension predicate the Q10 exception trusts will be expressed against that new receipt substrate once it lands; it has not been re-verified against it.

**(4) Strongest argument FOR.** The exception is as narrow as such an exception can be drawn: read-only, advisory, authenticated, scoped to exactly the governed two-slot extension shape, with issuance and the morning verdict both behind `_assert_terminal_committed_snapshot`. Both prior judges found the shape plausible; the alternative (probe also waits for terminal close) delays trigger *detection*, not any state change, so the exception buys operational awareness at zero write risk. The exhibit's own enforcement is complete on its side of the boundary.

**(5) Strongest argument AGAINST.** The Opus STRAIN survives in transformed form (assembler characterization, contestable): the exception's narrowness is outsourced to a predicate in a different unit (U1's `is_governed_open_bracket_extension`), unexamined by this exhibit, and a false positive admits WITHHELD observations (finalized slots) into the trigger population that feeds the Q1 corpus. The specific aggravator in round one — the predicate sat on a branch under a fired escalation (foreign-replay class, zero-payload auto-replay) — no longer applies as stated, because the escalation was answered by the recovery redesign; but the redesign *replaces the predicate's substrate entirely*, so the objection re-arises in stronger form: the exhibit ratifies trust in a predicate whose implementation is about to change and whose new form has passed no gauntlet. Ratifying now ratifies a trust relationship against bytes that will not be the operative bytes.

**(6) Prior-round evidence (prior round, pre-rework).** Cold Fable: RATIFY — narrow authenticated read-only exception, issuance behind terminal committed snapshot. Opus refuter: STRAIN — narrowness outsourced to an unexamined U1 predicate then under a fired escalation. Synthesis: DEFERRED until the U1 recovery-shape rework lands and the trusted predicate is re-verified on the new shape.

**(7) If the gate rules the other way.** (a) If the exception is refused: the probe joins issuance behind `_assert_terminal_committed_snapshot`; the policy constant and probe path tighten; trigger detection waits for session close/abort — the prior Fable ruling characterized this cost as availability-only; that characterization is argument, not established fact, and the substrate question becomes moot either way. (b) If the gate defers to post-landing re-verification: the constant stands provisionally, Q10 ratification rides the `impl/d117-ledger-recovery` gauntlet, and the exception may not be exercised on a live night until the predicate is re-verified against the ledger-resident shape. (c) If ratified as-is: the trust relationship extends automatically to the successor predicate implementation when the recovery branch lands, without a further gate.

**(8) Decision the gate must return.** One of: ratify the probe-only exception as implemented; refuse it (probe requires terminal committed snapshot); or defer ratification until the ledger-resident recovery shape lands and the governed-open-extension predicate is re-verified against it — and, if deferring, state whether the exception may be exercised in the interim.

---

### Q11 — Trigger-observation absorption, parent-judgment lineage, computed successor_probe

**(1) Question.** Under what scope does D-102 pin 2's second conjunct ("never incorporated into a threshold that judges itself" — see D-102 — BODY, pin 2) permit a trigger observation to enter the successor corpus: does judgment under the *prior* artifact discharge the conjunct (narrow scope, as implemented), or does the conjunct bar trigger observations from the successor threshold entirely because that threshold will judge future evaluations of the same content (broad scope)? Secondarily: does the replacement of the fabricated `successor_probe` attestation with a computed probe close the self-attestation blocker?

**(2) Code at ad5f3f7.** `POST_SUCCESSOR_POLICY = "require_explicit_parent_judgment_lineage"` (`calibration_bracketing.py:136`, tag at :134). The builder: (a) requires the grouped-minus-parent-prior content set to equal exactly the parent probe's `new_content_ids`, refusing `successor_parent_judgment_content_set_mismatch` (`build_calibration_acceptance_successor.py:284-290`); (b) at the tagged site (:309-314) refuses the ENTIRE build with `successor_trigger_lacks_parent_disposition` when a trigger observation's content id appears in `parent_new_ids` while the parent probe's single GLOBAL outcome is not `successor_required` (`if content_id in parent_new_ids and parent_probe["outcome"] != "successor_required": raise …`) — an all-or-nothing predicate against the parent probe's overall outcome, not a per-observation disposition record, and its failure refuses the whole build rather than excluding the row; the comment marks this isolated predicate as the flippable site for this ruling (D-109 R2.6 conservative default); (c) `_probe_proposed_successor` (:184-228) copies the proposed registry and artifacts into a temporary root and runs the production `probe_calibration_acceptance_trigger` against the proposed bytes, refusing `successor_real_probe_refused:<outcome>:<reasons>` unless the result is `accepted_under_active_artifact`; the real result is stored in the build (:467-475).

**(3) Changed since 399ffeb.** The hardcoded literal attestation (`{"outcome": "accepted_under_active_artifact", ...}`, never computed) is removed in favor of the computed probe. The content-set equality check and the build-level parent-outcome predicate are new; the old code checked only that parent-new IDs were a *subset* of the successor prior set, with no gate on the parent probe's outcome.

**(4) Strongest argument FOR.** The rework implements the conservative reading of D-109 R2.6 (absorption only after trigger disposition) as an enforced predicate rather than a comment: no trigger observation reaches the corpus unless the real parent probe judged the trigger population under the prior artifact and returned `successor_required` — the first-conjunct discipline ("judged under the prior artifact") made mechanical, at build granularity. The max()-shape of self-attestation is gone: the artifact now records what production code actually computed, refusing loudly when the probe refuses. The D-102 index row's own language ("never-zero allowance … exact-identity-epoch …") and D-109 R2.6 are both satisfiable under this reading, and the flippable isolated predicate means a broad-scope ruling costs a one-site flip, not a redesign — the code does not entrench either answer.

**(5) Strongest argument AGAINST.** The Opus CONTRACT-BREAK survives in its core (assembler characterization, contestable): the check remains a *mandatory-inclusion* posture — trigger observations DO enter the successor threshold basis, and that threshold will judge all future same-epoch evaluations, including further evaluations of the same content. If pin 2's second conjunct is read broadly, parent-probe judgment does not cure incorporation; the exhibit still implements the conjunct's negation, only now with lineage paperwork. Moreover the predicate operates at build granularity against one global outcome: it cannot distinguish among trigger observations — either the parent probe's overall outcome licenses absorbing all of them, or the build refuses entirely. What the rework addresses (same characterization): the fabricated-attestation aggravator (the probe is computed), and the "attests a property the code does not enforce" claim as applied to parent judgment (now enforced at :309-314, at build granularity). What survives untouched: the conjunct-scope question itself — which is exactly what this packet presents for explicit ruling. Residual adverse reading of the new machinery: `_probe_proposed_successor` runs the probe with `require_committed_registry=False` against temp-root bytes — a validation mode structurally different from the committed-mode path every production consumer uses (inherent to pre-commit validation, but the gate should see it). The cold judge's second DEFER ground — no non-test consumer of `POST_SUCCESSOR_POLICY` exists at evaluation time — is only partially addressed: build-time enforcement now exists ((a)/(b) above); a post-successor evaluation-time consumer still does not.

**(6) Prior-round evidence (prior round, pre-rework).** Cold Fable: DEFER — pin 2's scope genuinely underdetermined; ratifying a permission whose enforcing consumer does not exist licenses future code sight-unseen. Opus refuter: CONTRACT-BREAK — mandatory inclusion implements the pin-2 conjunct's negation; aggravated by the hardcoded `successor_probe` literal (fabricated attestation, third occurrence of the class). Synthesis: the fabricated attestation is a blocker independent of any packet question; the conjunct-scope question must be re-presented explicitly under D-102 pin 2's full text.

**(7) If the gate rules the other way.** Broad conjunct scope: the tagged predicate at build :309-314 changes from refuse-the-build-unless-parent-outcome-`successor_required` to categorical exclusion of trigger observations from corpus membership — a filtering behavior that does not exist in the current code (today's behavior on predicate failure is refusal of the entire build, not row exclusion); trigger observations would be recorded in the prior set with their parent judgment but never become corpus members. Consequences: the successor corpus shrinks by the trigger count (interacts with the Q13 minimum-corpus floor — exclusion could leave n below any ratified floor), and the count-boundary schedule (Q4) advances on a smaller n. Narrow scope: the code stands as written. Either ruling leaves the computed-probe mechanism (c) intact; rejecting mechanism (c) itself would require a different attestation design, since the pre-rework literal is a closed blocker under the synthesis.

**(8) Decision the gate must return.** (i) The scope of D-102 pin 2's second conjunct: parent-artifact judgment discharges it (absorption as implemented, at build granularity against the parent probe's global outcome) or it bars trigger observations from the successor threshold entirely (flip the :309-314 predicate to exclusion); (ii) whether the computed `_probe_proposed_successor` attestation, including its `require_committed_registry=False` temp-root mode, satisfies the self-attestation blocker the synthesis recorded.

---

### Q12 — Exhibit scope and L4

**(1) Question.** Is the four-file exhibit's scope — closing the authenticated probe API while leaving writer copied-scalar removal and the U8 arm-path integration explicitly out of scope — an acceptable unit boundary for U2, now judged with the FULL findings-register text before the gate: the LENS 2 block (containing both L4 and the adjacent L5) and the Disposition paragraph the first packet truncated (see FINDINGS-REGISTER — LENS 2 and FINDINGS-REGISTER — LENS-2 DISPOSITION PARAGRAPH in §3)?

**(2) Code at ad5f3f7.** `WRITER_INTEGRATION_SCOPE_STATUS = "probe_closed_writer_and_arm_path_residual"` (`calibration_bracketing.py:139`, tag at :137): the exhibit closes the authenticated probe API; writer scalar removal and the U8 arm-path call remain out of this exhibit's scope. The live writer still consumes the hardcoded `PREFLIGHT_SYSTEMATIC_SCREEN_S` literal with no authentication (`scripts/validate_powermetrics_fiducial.py:103`, used :915-918). Parity fact (verified, cuts both ways): that writer literal `0.033558756679900` equals the parent artifact's `preflight_level_screen_s` literal (`calibration_bracketing.py:81`) byte-for-byte today — the two authorities agree until the first successor issuance changes the engine's screen; divergence begins only then.

**(3) Changed since 399ffeb.** The constant and the scope boundary are unchanged. What changed is the *packet*, not the code: the first packet quoted the L4 register bullet truncated exactly at the Disposition paragraph ("U2 covers L4's trigger probe") — the single most Q12-relevant sentence — and dropped adjacent L5; this packet places the un-truncated register text in §3 (both blocks byte-verified).

**(4) Strongest argument FOR.** The register's own Disposition — now quoted in full — assigns U2 exactly this scope; the refuter, reading the full entry from source, returned NO-CASE and called the exhibit's residual labelling honest. A bounded four-file exhibit is reviewable at the depth this gate demands; folding writer surgery and the U8 arm path into the same exhibit would have made the first gauntlet's per-question verification intractable. The Fable amendments (L4 stays OPEN at HIGH until writer de-dup AND arm-path integration land; writer copied-scalar removal is a NAMED BLOCKING UNIT for any live night relying on the writer's systematic classification; L4's two mandated review scenarios ride the writer-integration review) fence every operational risk the scope leaves open, and the synthesis made the blocking-unit amendment doubly binding.

**(5) Strongest argument AGAINST.** The Q5×Q12 composition hazard survives the rework untouched (assembler characterization, contestable), because the writer is out of scope by design: a successor can issue with a screen differing from the writer's stale unauthenticated literal; an overnight post-calibration landing between the two is finalized valid by the writer, appended immutably, then re-judged systematic by the morning probe — persistent refusal (Q5), the night spent, and no automatic successor can ever issue again. The Q2 rework changes the arithmetic of that divergence (the screen is now the observed corpus maximum alone, no longer `max(maximum, prediction_95)`) but does not close the two-authority split — the only closure is the out-of-scope writer integration itself; today the two literals agree byte-for-byte (see (2)), so the hazard is latent until first successor issuance. Nothing in the rework addresses this; the first packet's truncation defect is cured, but curing the quotation does not cure the hazard. An adverse reading holds that a scope which structurally defers the only fix for a named night-killer should not be ratified separately from a binding schedule for that fix.

**(6) Prior-round evidence (prior round, pre-rework).** Cold Fable: RATIFY-AS-AMENDED — scope acceptable with the three amendments above. Opus refuter: NO-CASE — the register's own (packet-truncated) Disposition assigns U2 exactly this scope; residuals honestly labelled. Synthesis: convergent — scope stands, Fable amendments binding.

**(7) If the gate rules the other way.** If the scope is refused: U2 cannot be ratified as a standalone unit; writer scalar removal and/or the U8 arm-path call must join the exhibit (or a successor exhibit) before any part merges — the arm-blocker timeline for nights 1–2 extends by that integration and its own review. If the scope stands: the amendments are the operational fence — L4 remains open at HIGH, no live night may rely on the writer's systematic classification until the named blocking unit lands, and the two mandated review scenarios attach to the writer-integration review, not to U2.

**(8) Decision the gate must return.** Whether the `probe_closed_writer_and_arm_path_residual` scope stands as U2's unit boundary — judged on the full, un-truncated L4/L5/Disposition text — and, if it stands, confirmation that the three prior amendments (L4 open at HIGH; writer de-dup as named blocking unit; review scenarios riding writer integration) bind as conditions of ratification.

---

### Q13 — Allowance-rule generalization and minimum-corpus bound (NEW)

**(1) Question.** The exhibit generalizes the calibration-drift allowance from D-117 cl.1's binding literal — `max(observed_drift_s, 0.010818)` — to the corpus-dependent `max(observed_drift_s, bracket_screen_s)`, where `bracket_screen_s` is re-derived per successor corpus; no prior question covered this rule. The gate must decide which operand D-117 cl.1 binds for successor artifacts, and — inseparably — what minimum corpus size licenses issuance at all, given that the smallest corpus the pre-rework code accepted (n=2) yields df=1 and t(0.995,1)=63.66, a statistically degenerate screen.

**(2) Code at ad5f3f7.** `SUCCESSOR_MINIMUM_CORPUS_SIZE = 19` (`calibration_bracketing.py:143`, tag at :140). Three guard sites enforce the floor: `derive_successor_decimal_derivation` refuses fewer members with `successor_corpus_below_pending_q13_minimum_19` (:463-466); the artifact validator requires `corpus.n >= 19` (:1130); the builder applies the same floor (`build_calibration_acceptance_successor.py:340-341`). The allowance rule itself is deliberately unchanged at both of its sites: the artifact field `"allowance_rule": "max(observed_drift_s,bracket_screen_s)"` (:577-583, tagged "deliberately unchanged pending the re-convened ruling") and the runtime computation `allowance = max(drift_decimal, screen)` in `evaluate_calibration_bracket` (:3370-3373, tagged as the isolated site the re-convened packet can flip without touching downstream shape). The identity between D-117 cl.1's literal and the parent artifact's screen is a byte fact of the exhibit: the parent `bracket_screen_s` literal at `calibration_bracketing.py:80` carries `0.010818`, the same value D-117 cl.1 binds. The guard's stated purpose is preventing the df=1 / t≈63.66 path from becoming an issued comparator while Q13 is pending.

**(3) Changed since 399ffeb.** The Q13 tag, the constant, and all three guard sites are new (the floor was 2). The `max(observed_drift, bracket_screen)` computation itself is byte-identical to the original exhibit — the rework fenced the question rather than answering it.

**(4) Strongest argument FOR.** The `max(drift, screen)` *shape* is D-102-ratified text ("never-zero allowance max(drift, screen) embedded once" — see D-102 — INDEX ROW and D-102 — BODY); the generalization reads D-117 cl.1's `0.010818` as the value that rule takes under the genesis corpus, not as a constant that survives the corpus it was derived from. A successor regime that re-derives its level screen, prediction, and budget cap from its own corpus (Q1/Q2) but freezes a predecessor corpus's screen inside the allowance would mix two authorities inside one comparator; the generalization keeps the artifact self-consistent, preserves the never-zero property for any positive screen, and the n≥19 floor — the genesis corpus size, the only ratified n in the record — prevents the degenerate small-df regime from ever reaching an issued comparator while the ruling is pending.

**(5) Strongest argument AGAINST.** D-117 cl.1 binds the literal `0.010818` (see D-117 — BODY, cl.1); the exhibit substitutes a corpus-dependent quantity for ratified text with no ratifying decision — precisely the unauthorized-generalization pattern the refuter flagged, and it entered the code covered by NO question, surfacing only as a composition hazard. A corpus-derived screen makes the allowance floor drift with the corpus: a tighter successor corpus *lowers* the allowance floor below the ratified 0.010818, loosening nothing today but narrowing the never-zero guarantee to whatever the corpus happens to produce. The n≥19 guard is code, not authority: 19 is the genesis count, not a derived statistical bound — nothing in the record establishes it as the correct floor rather than a convenient one, and the refusal reason (`…pending_q13_minimum_19`) itself concedes the number is unratified. No part of the rework addresses the refuter's coupling finding (assembler characterization, contestable) — it was fenced (floor raised from 2), not resolved; the fence's own number is among the things needing ratification. Note also the Q11 interaction: a broad conjunct-scope ruling there shrinks corpora and makes the floor bind more often.

**(6) Prior-round evidence (prior round, pre-rework).** No per-question verdicts exist: Q13 was not a question in the first packet. Its provenance (prior round, pre-rework): the Opus refuter's composition-hazard finding — the allowance generalization of D-117 cl.1's binding literal was covered by no question, and n=2 corpora were accepted where t(0.995,1)≈63.66; synthesis binding finding 7(b) created Q13 and mandated the minimum-n bound be ruled ("n=2 corpora must refuse or be justified").

**(7) If the gate rules the other way.** If cl.1's literal binds: flip the runtime site (:3370-3373) to `max(drift_decimal, 0.010818)` and the artifact `allowance_rule` field (:577-583) accordingly — both tagged as isolated, no downstream shape change; successor-derived screens remain recorded evidence and preflight comparators (Q2) but never allowance inputs; the minimum-corpus question then decouples from the allowance and is decided on the screen/prediction derivations alone. If the generalization is ratified: the gate must simultaneously fix the licensing floor — 19, another n, or a df-based criterion — since the current 19 is expressly a placeholder pending this ruling; the refusal reason code renames from `pending_q13` to the ratified rule, and the validator/builder/derivation floors move together (three sites listed in (2)).

**(8) Decision the gate must return.** Two rulings, both required: (i) the allowance's screen operand for successor artifacts — D-117 cl.1's literal `0.010818` or the successor's own `bracket_screen_s`; (ii) the minimum corpus size (or statistical criterion) that licenses successor issuance, replacing the placeholder n≥19 guard with ratified authority — including whether n=2..18 corpora refuse permanently or under what justification any of them could issue.

## 5. Unswept evidence

What a fresh judge cannot see, or cannot verify, from this packet.
Items marked "surfaced" now appear in a section but remain only
partially inspectable; items marked "unswept" are not examinable from
this packet at all.

1. **Q3 evidence file's internal contradiction** (surfaced in Q3(3);
   resolution unswept): Q3-KERNEL-EVIDENCE.md's PARTIAL status header
   ("must not treat this document as closing that named requirement")
   coexists with a closure-claiming appendix dated 2026-08-08 — the
   future relative to this convening — whose generating script exists
   only as an off-repo scratchpad `mpmath_oracle.py`. Which state
   governs is for the gate; neither the oracle run nor its script has
   been independently re-executed for this packet.
2. **The banked D-102 five-operative replay** (unswept): the synthesis
   BANKED it and ordered the reassembly to cite it; it is referenced in
   Q3(4) but has no entry name, location, or stated scope anywhere
   available to this assembly — the judge cannot inspect the evidence
   on which the pins-reproduce-the-parent claim rests.
3. **The prior Fable ruling's "D-116 R2.8" citation** (surfaced in
   Q1(6); resolution unswept): the prior judge cited R2.8 as D-116
   text; this packet's byte-verified extracts carry R2.8 as D-109
   text, with D-116 applying it. Whether this is a mis-citation or a
   cross-decision clause-numbering collision is unresolved.
4. **`COLD-GATE-U2-PENDING`** (surfaced in §3): the declared tuple's
   fourth member; no decision-log entry exists (verifier-confirmed);
   its replacement/disposition is a decision item in §6.
5. **The committed-registry topology for the Q8 shim / Q9
   first-publication scenario** (surfaced in Q8(2)/Q9(5); resolution
   unswept): main carries no acceptance-registry file; the exhibit
   head's registry is already migrated. The checkout/commit on which
   the shim's precondition (`acceptance_registry_missing_commit` +
   committed entry lacking `count_boundary_rule`) is actually
   reachable could not be located from the available material.
6. **The Q5/Q12 parity fact** (now surfaced in Q5(3) and Q12(2)): the
   writer's hardcoded screen literal equals the parent artifact's
   literal byte-for-byte today; divergence begins at first successor
   issuance. Cuts both ways.
7. **The third systematic class** (now surfaced in Q2(2)/Q5(1)-(2)):
   a valid observation with an unparseable bound lexeme is classified
   systematic (~:2109-2119). Its interaction with the writer's own
   validation was not examined.
8. **U1's `is_governed_open_bracket_extension`** (unswept): the
   predicate Q10's exception trusts has no file:line pointer in this
   packet, in either its operative form or its redesigned
   (`c392d79`/`c0e0257`) form; the judge is asked to rule on a trust
   relationship with no pointer to the trusted code.
9. **Test evidence** (unswept): the exhibit's +317-line test change is
   not referenced in any section; which questions carry defect-shaped
   regressions, and which paths (e.g., Q9's torn-publication paths,
   Q6's receipt-authentication refusals) are exercised, is invisible
   from this packet.
10. **Charter erratum #2** (surfaced in §1): worktree convening does
    NOT suppress doctrine injection for subagent judges; the
    contamination-disclosure line is the working control. The
    convening procedure in this directory's README.md predates the
    erratum.
11. **Provenance of `0.010818` in the parent bytes** (now surfaced in
    Q13(2)): the parent `bracket_screen_s` literal at
    `calibration_bracketing.py:80` carries the same value D-117 cl.1
    binds; the deeper derivation lineage of that literal was not
    re-traced for this packet.
12. **Genesis-rule recompute asymmetry** (now surfaced in Q4(7)): the
    loader recomputes boundaries only for `retain_then_double`; a
    successor entry carrying the genesis rule refuses
    `acceptance_registry_boundary_rule_unsupported` — the supported
    set is effectively single-member for successors. The full
    supported-set/recompute matrix was not exhaustively traced.
13. **Prior-ruling documents consulted only at single lines** (unswept
    beyond those lines): COLD-FABLE-RULING.md and OPUS-REFUTATION.md
    were consulted for specific citations (e.g., :16-17); their full
    texts sit beside this packet and were not re-summarized here —
    the per-question verdict lines in each section are carried from
    the remand synthesis.
14. **Q3-MPMATH-ORACLE-GRID.json** (unswept): the committed raw grid's
    contents were not independently recomputed or compared for this
    packet; the deviation figures in Q3 are the evidence file's own.

## 6. The decision required

For each question the gate returns one of: **RATIFY** /
**RATIFY-AS-AMENDED** (stating the amendment) / **REJECT** (stating
the required replacement semantics) / **DEFER** (stating the lift
conditions). The specific sub-rulings each question requires are
enumerated in its element (8); they are restated here only by pointer.
No recommendation accompanies any item.

- **Q1** — corpus universe: menu above; sub-rulings Q1(8)(i)-(ii).
- **Q2** — preflight screen source: menu above; Q2(8).
- **Q3** — numerical method split: menu above; sub-rulings
  Q3(8)(i)-(iii), including the ratification status of the unratified
  digits and the disposition of the evidence file's coexisting
  PARTIAL/closure states.
- **Q4** — count-boundary progression: menu above; sub-rulings
  Q4(8)(a)-(b), including the labelled residual irreversibility.
- **Q5** — persistent systematic refusal: menu above; sub-rulings
  Q5(8)(a)-(c), including the definition of closure.
- **Q6** — no-content/abandoned handling: menu above; sub-rulings
  Q6(8)(a)-(c).
- **Q7** — lineage/naming/loader surface: menu above; sub-rulings
  Q7(8)(a)-(b).
- **Q8** — registry authority + migration shim: menu above;
  sub-rulings Q8(8)(a)-(b), noting UNSWEPT item 5.
- **Q9** — publication ordering/barrier: menu above; sub-rulings
  Q9(8)(a)-(b).
- **Q10** — probe over open extension: menu above; the three-way
  disposition in Q10(8), including interim-exercise status if
  deferred.
- **Q11** — trigger absorption/conjunct scope: menu above; sub-rulings
  Q11(8)(i)-(ii).
- **Q12** — exhibit scope: menu above; Q12(8), including whether the
  three prior amendments bind as conditions.
- **Q13** — allowance generalization + minimum corpus: menu above;
  both required rulings Q13(8)(i)-(ii).
- **Cross-cutting** — disposition of the declared tuple's fourth
  member `COLD-GATE-U2-PENDING` (§3): what identifier replaces it on
  ratification of any question set, and what its presence means under
  rejection or deferral.
