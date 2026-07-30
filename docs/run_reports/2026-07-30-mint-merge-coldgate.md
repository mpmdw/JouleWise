# 2026-07-30 — Audit harvest, FIX-10, the cold-gate escalation, PR #88 merge, advisor hardening

Magistrate session (Fable, rule-11 topology), resuming the RUN_STATE
resume script from the 10ca912 handoff. Main advanced
`10ca912 → e1e0aec → d8b5d54 → da83337` (PR #88 merge).

## Arc 1 — FIX-9 audit harvest and FIX-10

The FIX-9+FIX-8 delta re-audit (Sol xhigh, launched by the predecessor
session) was recovered complete from the prior session's scratchpad:
**FAIL** — blocker QA-1 (a repeated declared `bundle_ids` entry whose
surplus `physical_members` rows are malformed undercounts to one
candidate; the one-row fast path accepts its cooldown evidence without
the supersession matcher), should-fix QA-2 (the positive join regression
stubbed the reader with a validator-invalid entry). QA-1 was
bench-confirmed by the magistrate against the code before acceptance.
Mint #1's artifact-internal consistency passed (audit Q6).

FIX-10 (Sol high, WRITE_SCOPE = `inputs.py` + integration tests;
first launch came back blocked on a read-only sandbox — magistrate
launch-flag error, relaunched with `-s workspace-write`): declared-
occurrence tallying, fast path licensed only at declared count exactly 1,
both malformed-duplicate regressions verified defect-shaped (failed
pre-fix), and a real validator → `campaign_log.jsonl` reader → join
custody fixture. Lead-verified 48/48 focused; committed `16c7af0`;
lead-side canonical suite at that head **2280 OK (skipped=21)**.

## Arc 2 — the escalation fired, and was honoured

The FIX-10 delta re-audit (Sol xhigh) returned **FAIL with two successor
blockers**: QA-10A (zero-candidate duplicate declarations are omitted
from the result map entirely; the omission escapes `floor_extraction`'s
map-iteration completeness) and QA-10B (the writer's
failed-existing → quarantine → invoked-retry shape stays at declared
count 1 under invoked-only tallying, and the supersession writer cannot
even author the repair record for it). Two consecutive same-signature
fix-round failures → the standing escalation trigger FIRED. **No FIX-11
was ordered.** A mandatory cold gate convened: fresh Fable instance on a
mechanically-assembled packet, paired with an Opus contract-lens refuter
(exercise #4 of the pairing).

Outcome (D-088, magistrate synthesis of both verdicts): the structural
cause is a missing clean/failed outcome bit on `execution="existing"`
manifest rows — no counting rule over current data can separate benign
cumulative re-listings from the laundering shape. Join hardening moved to
COOLDOWN-JOIN-GAUNTLET-01 under the ratified C1/C3/C4/C5 contract, with
the counting domain (writer outcome bit vs the refuter's verified
declaration-order discriminator) a design decision for that gauntlet.
Merge licensed at the audited head with conditions. On the record against
the magistrate: FIX-10 was conformant with ruling R2 — for QA-10B the
*ruling* was the defect (refuter's catch).

**Evidence-soundness verification (three independent scans — magistrate
bench, cold instance, refuter):** both blocker shapes are ABSENT from all
claim-bearing corpora. a10 and window C (mint #1 inputs): zero duplicate
declarations. The 7B window's only true duplicates are the two
daemon-intrusion replacements, both resolved through the licensed
validated-supersession path (exactly 2 records in the log; quarantine in
custody; one pre-FIX-9 REFUSED extraction artifact preserved).

## Arc 3 — merge train

Registration preceded the merge per the cold-gate condition: bookkeeping
batch `e1e0aec` (D-083..D-088, C-039 addendum + close-out, QA-1 closure +
QA-10A/B/C/D + gauntlet rows staged, sweep memos, hardened advisor brief,
`test_gen_state` EXPECTED_IDS sync). CI then caught a real magistrate
error: the batch appended six decision bodies without index rows —
`test_docs_freshness` red, fixed in `d8b5d54`. Lesson recorded: the
pre-commit test surface for doc-touching commits must include
`tests.test_docs_freshness`.

GitHub then served a stale PR test-merge ref (three runs checked out a
merge into pre-fix `e1e0aec` despite base updates and two close/reopen
cycles; the exact merge reproduced green locally). Resolution: wait for
the ref recompute (verified via `refs/pull/88/merge` fetch), third
reopen, checkout SHA verified `ff0dda5` (merge into `d8b5d54`) BEFORE
spending the watch. All five checks green; merged at the intact audited
head. **Main `da83337` carries mint #1** (validator clean, lead-run
`validate_floor_artifact == []`).

## Arc 4 — advisor claim set (Ed's ~14:30 meeting)

Every quantitative claim in the brief was verified against primary
evidence (delegated Opus verification, 30 claims, all exact at full
precision), and six overclaims were tightened by the magistrate: the
142 J cross-window effect relabelled as a strong preliminary observation
(floors bound within-session error; the pre-registered head-to-head is
what upgrades it); "backup daemon" corrected to the operator log's
unidentified-excursion hypothesis (also fixed in the council log);
4.7× → ≈4.9× parameters (actual weight counts); literature universals
rephrased to "we found no published…"; purchasing-spec claim scoped to
requirements; the null test now carries its ±2.6 J spread (consistent
with zero — and the origin of the 14 J floor). `validate_floor_artifact`
run lead-side: `[]`. Deliverable:
`docs/advisor_briefs/2026-07-30-advisor-brief.md`.

The dictated-fills pattern caught two magistrate errors this session:
the TokenPowerBench arXiv id conflation (2512.03024, not 2605.11999) and
the decision-index omission (caught by CI, same class).

## Verification ledger

- Branch head `16c7af0`: lead-run canonical `Ran 2280 tests`, `OK
  (skipped=21)`; Sol-side `2280 OK (skipped=24)` (three extra
  environment-gated skips in the delegated sandbox).
- Local reproduction of the exact PR merge (d8b5d54 + 16c7af0):
  `tests.test_docs_freshness` 6/6 OK.
- CI green on merge ref `ff0dda5`: build, installed-wheel, release-chain,
  test (3.11), test (3.14).
- Post-merge suite on `da83337`: recorded in RUN_STATE §Current
  Verification when complete (in flight at report write).
- Mint #1 validator: `validate_floor_artifact == []`, lead-run 2026-07-30.
- Corpus scans (fail-open shapes): magistrate script + cold-instance and
  refuter independent re-derivations, all three corpora clean.

## Open at close

- COOLDOWN-JOIN-GAUNTLET-01 (own gauntlet; C1 first commit; counting
  domain design consult owed).
- Kernel refresh (fold staged intake rows; close STACK-ID-BIND-01 on the
  real-bundle re-verify at 7f2c108+; retire FLOOR-LABEL-01 READY row;
  point latest_report here).
- Contrast/floor window tonight per D-085 Q1 — Ed-gated (AC power,
  settled machine, network-time confirmation still unverified).
- Advisor answers (acceptance bar, write-up scope, wall meter, claim
  priorities) reorder the queue on Ed's return.
