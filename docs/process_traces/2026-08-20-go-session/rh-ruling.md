# RECEIPT-HISTSEM-01 — D-144 co-design ruling (2026-08-20 evening)

Seats: terra (xhigh) + Opus 5, independent designs + one debate
response each (custody: rh-terra-design.md, rh-opus-design.md,
rh-terra-debate.md, rh-opus-debate.md). Both seats independently
derived the same pure-git primitive; Opus executed it (9/9 historical
digests match; all-nine HEAD differential equivalence;
terra-confirmed). Every material divergence was resolved by a seat
withdrawing on executed evidence; this ruling records the union.
Pending one cold delta pass (contract change on the freeze/arm path).

## Ruled design

1. PRIMITIVE: `historical_pack_tree_sha256` = pure-git `ls-tree` at
   the recorded `head_commit` + `cat-file blob` per OID under the
   existing PACK_DIGEST_DOMAIN framing (no checkout, no network). A
   DIFFERENTIAL SELF-TEST (`historical(HEAD) ==
   committed_pack_tree_sha256` across all packs) pins the framing
   mechanically — never in prose.
2. CHECKS: K5 (historical recompute vs the receipt's recorded
   `pack_sha256`) + K12 (the pinned CURRENT-tree digest) are
   LOAD-BEARING; K7 (the delta-shape envelope: custody-dir adds only,
   zero deletes, modifications only in the freeze-retarget set) is
   LAYERED HARDENING and the `_v4` pinset-row BOOTSTRAP validator
   (the only check that can validate a new pinset rather than
   consume one). Opus's K7-as-sole-closure headline withdrawn; terra's
   same-path-rewrite attack recorded as the reason.
3. COORDINATES: two, explicit — HISTORICAL (`head_commit`) for
   K5/K6; HEAD for receipt→sidecar→freeze→plan binding and the K12
   pin (measured: plan_tree.json differs 9/9 — a historical plan
   check would refuse the corpus).
4. PLACEMENT: IN-LIBRARY gate — adopted on a DOUBLE CROSSOVER (the
   session's third, recorded honestly per the cold pass): terra's
   final conceded to the CLI seam while Opus's final conceded to
   in-library on its own dissolved cost objection; the ruled position
   adopts IN-LIBRARY on Opus's concession evidence ("a gate a future
   caller can route around is not a gate"; C1 exists because a check
   was not wired), overruling terra's cross-concession. Gates inside
   `generate_arm_receipt` (~:6108) AND `generate_freeze_receipt`
   (~:5411 — the function whose None/None omission IS C1, and the
   path the compelled `_v4` re-freeze runs through). The primitive
   CO-LOCATES beside `committed_pack_tree_sha256` (~:2553) — the
   seats' CONVERGED location (Opus conceded its own new-module
   proposal; the differential self-test lives ten lines from what it
   pins) — with a disjoint `histsem_*` error vocabulary on the
   LaunchLineageError second-vocabulary template (:991-998 — zero
   reason-code price; the 47-code pin untouched), caught in the
   :4616 idiom so no bare exception escapes (the fail-ugly class
   ruled against this session). The
   `scripts/generate_arm_readiness.py` seam carries the CLI test;
   `arm_readiness.py` gains ONLY the two gate calls + catch — none
   of the four r6-pinned files touched.
5. REFUSAL GRANULARITY: distinct codes for
   history-unavailable (shallow/gc'd), historical-digest-mismatch,
   binding-mismatch, pinset-absent — terra's own residual-risk
   two-situations note resolved.
6. ARCHIVAL RULE carried: `_v3` replays only at its ruled coordinate;
   a LOCATION refusal is not pack corruption — the verifier does not
   add a pack_root equality check (terra's catch; an implementer trap
   otherwise).
7. REGRESSION SHAPE: defect-shaped means BOTH halves — the control
   (the pre-existing frozen-PACK chain, called without
   expected_pack_sha256, ACCEPTS the coherent tamper) and the new
   histsem refusal. CI wiring in the full-fetch job only.
8. SCHEDULING CONSTRAINT (binding on the `_v4` transaction): this
   verifier LANDS BEFORE the `_v4` re-freeze; the `_v4` pinset row
   mints AFTER freeze-0004 ×3 AND BEFORE Ed's exact-byte step-6
   (the r4-3 step reference — the ambiguous "S5" label is retired) —
   retrofitting reproduces C1's shape (an expected value nobody
   supplied). COLD-PASS AMENDMENT TO r5 V-1 (ruled by that pass):
   the allowlist value goes 111 → 112, adding the pinset's exact
   path (pack-and-ordinal-exact per V-1(v); `_v5` gets its own entry,
   never a glob) — without it, the post-mint pinset commit trips the
   whole-repo changed-set gate and refuses every subsequent `_v4`
   arm. S-0's clone proof extends to exercise the histsem gates and
   the pinset (present → arms cross; absent → the pinset-absent
   refusal; the 112-entry candidate contract still fails on
   missing/extra/unused).
9. TRUTH BOUNDARY (paper wording mandated; the detectability
   sentence is Opus's, terra concurring): this is DETECTABILITY, not
   integrity — the verifier does not stop a history-rewriting
   in-process actor (that residual is a REGISTERED LIMITATION under
   D-139 A1, which is why it is recorded rather than a gap); it
   raises forgery
   cost from a 6-file commit to a history rewrite that breaks
   merge-base ancestry against origin/main and contradicts the
   hand-published S5 digest table. The paper says so in those words.

## Normative annexes

The two debates' consolidated ruling lists (rh-terra-debate.md,
rh-opus-debate.md — incl. the held items: mandatory facts[]
source_sha256, the CI-hard/pre-arm-advisory origin-main split, the
predecessor binding and freeze-gate predecessor mode, pinset
byte-pin-in-test with no --update lane, the contract doc as ONE
home, no fetch/repair in any lane) are NORMATIVE ANNEXES to this
ruling; where they diverge from these clauses, the clauses control.

## Process note

Every concession in both directions was evidence-driven (executed
prototype; the two in-library vocabulary precedents; the 9/9 plan
measurements; the ruled fail-ugly and archival clauses). The union is
materially better than either seat's design — the co-design protocol's
value demonstrated again.
