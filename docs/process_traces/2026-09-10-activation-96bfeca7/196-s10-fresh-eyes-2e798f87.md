# Fresh-eyes review (gate row 10) — S10 round 8, commit 2e798f87

Read-only, from an export at `/tmp/s10-r8-export` (`git archive 2e798f87`), `PYTHONDONTWRITEBYTECODE=1`.
No repo was modified; no git write command was run.

Verdict: **one BLOCKER-class integration defect** (a genuine desk-tool record is
refused by the branch's `--equivalence-record` cross-check), one should-fix doc
contradiction, two nits. Everything else asked about is CLEAN and true against the code.

---

## (1) The three edits — exactly as described, and true against the code

`git show 2e798f87 --stat` (non-merge commit; its parent `ed4936c7` is the merge of `origin/main`):

```
 docs/contracts/epoch_continuation.md    |  3 ++-
 docs/contracts/powermetrics_fiducial.md |  8 +++++---
 scripts/issue_epoch_continuation.py     | 18 ++++++++++++------
 3 files changed, 19 insertions(+), 10 deletions(-)
```

`git diff cfeba22f 2e798f87 -- docs/contracts scripts/issue_epoch_continuation.py` shows
exactly those three hunks and nothing else. No conflict markers anywhere in the tree.

**(a) `powermetrics_fiducial.md` — the "CLI supplies no snapshot" sentence is replaced, and the
replacement is TRUE.** Old text: "Until the CLI supplies its ledger snapshot here, a
file-authenticated continuation can pass capture preflight but fail the session cross-check at
claim time." Replaced by the claim that the writer supplies its custody-verified snapshot.
Verified in the merged tree:

- `/tmp/s10-r8-export/scripts/validate_powermetrics_fiducial.py:1951-1954` — the writer loads
  `load_calibration_ledger_snapshot(args.ledger, args.head_pin, require_committed_pin=True,
  verify_custody=True, mode="issuing")` into `preflight_snapshot`, before any capture state exists
  (comment at 1949-1950).
- It is passed to **both** preflight helpers: `:1958` (derivation-only screen basis) and
  `:2008-2010` (ordinary `_derive_preflight_systematic_screen_s`), and to the lifecycle at `:2055`
  (`preflight_snapshot=preflight_snapshot`), consumed at `:1503`/`:1522-1534`.
- `:409-416` — `acceptance_judged_epochs(artifact, ledger_snapshot=ledger_snapshot, …)` and
  `"judged_epochs_basis": "ledger_snapshot" if ledger_snapshot is not None else
  "registry_pins_only"`. So the recorded basis on the CLI path is `ledger_snapshot`, as the new
  sentence says.
- "exactly as it is at claim time" is accurate: claim time calls the same function with a ledger
  snapshot at `joulewise/calibration_bracketing.py:2058-2060`. The writer's snapshot is loaded
  under `verify_custody=True, mode="issuing"`, i.e. at least as strong as the claim-time load.
- The paragraph stays internally coherent: the `registry_pins_only` carve-out for the three
  identity-only helper callers survives at `docs/contracts/powermetrics_fiducial.md:178-183`.

**(b) `issue_epoch_continuation.py` docstring — builds both terms at first use.** The rewritten
docstring (`scripts/issue_epoch_continuation.py:3-17`) defines EQUIVALENCE NIGHT ("the one
derivation-kind ledger session of twelve capture slots run on the new epoch and judged, after it
closes, against the envelope the acceptance already carries (directive issue 316)") and
RANGE-EXPANSION TRIGGER ("the acceptance's own re-derivation trigger that fires when a new valid
capture on a judged epoch falls outside the corpus's observed range") **before** the sentence that
uses them ("acknowledged rows bypass only that trigger"). First-use test passes for both terms,
and the text reaches the operator through `--help` (pasted in §4).

**(c) `epoch_continuation.md` — the resolved row / null detail statement is TRUE.**
Added at `docs/contracts/epoch_continuation.md:63-64`: "A resolved row carries a null detail (a
detail on a resolved row refuses `slots.anchor_v3_detail`)." Enforced at
`/tmp/s10-r8-export/joulewise/calibration_epoch_continuation.py:243`:

```python
_require(not slot["anchor_v3_resolved"] or slot["anchor_v3_detail"] is None, "slots.anchor_v3_detail")
```

with the companion "unresolved must name a detail" rule at `:244-245`
(`slots.anchor_v3_detail_required`) and the type rule at `:242`. Both directions now documented.
CLEAN.

---

## (2) The merge — both halves present; §2.3 permits the post-night read; no duplication

`git merge-base --is-ancestor origin/main 2e798f87` → **MAIN_FULLY_MERGED** (origin/main =
a3261cf2). `git diff --stat origin/main 2e798f87 -- scripts/epoch_equivalence_check.py
tests/test_epoch_equivalence_check.py` is empty: the desk tool and its tests arrived from main
byte-identical.

**Revision 6 §2.5 is present** (`docs/phase_2/derivation_night_runbook.md:11` changelog line
"revision 6 (2026-09-10)"; §2.5 at `:1596`, its three inputs `:1613`, envelope constants `:1634`,
rule `:1670`, three outcomes `:1690`, the desk-tool invocation block `:1714-1723`).

**The branch's judged-epoch wording survives the merge.** `git diff origin/main 2e798f87 --
docs/phase_2/derivation_night_runbook.md` is exactly three hunks, all branch-side:
- `:143-147` glossary "Stale field" — now "differs from **every identity epoch the active
  acceptance judges** (its own, and any epoch an authenticated continuation has carried it onto)".
- `:716` desk-inputs refusal row — "this machine's identity epoch is one the acceptance at `<path>`
  **already judges** … this is an ORDINARY night".
- `:2033` capture-writer refusal row — `calibration_derivation_only_epoch_unchanged` now reads
  "one the active acceptance **already judges** (its own, or a continued epoch)".

**§2.3 as merged permits the post-night read the ruling allows.** Quoting rule 2 verbatim
(`docs/phase_2/derivation_night_runbook.md:1497-1502`):

> "**Once this night's ledger session is terminal, the retained values ARE read**, and §2.5 is what
> they are read for. Terminal means the session's last declared slot is final or the session was
> aborted. This is the change revision 6 carries, and it is licensed by the ruling rather than by
> the desk: the equivalence rule is fixed at §2.5, in writing, before the night runs, so reading
> afterwards selects nothing — nothing is left to choose."

Rule 1 (`:1491-1496`) still forbids reading while the night runs; rule 3 (`:1503-1510`) restores the
code-enforced blindness fence on the FAIL route only. No contradiction with §8's `blind /
blindness` and `blindness fence` rows (`:2208`, `:2210`), which say the same.

**No duplicated paragraph from the merge.** Duplicate-line scan over the runbook returns only
repeated shell `export`/flag lines inside separate code blocks (expected). One contradiction, below.

### FINDING A (should-fix) — §8 first-use table still carries the pre-merge "stale field" meaning

`docs/phase_2/derivation_night_runbook.md:2203`:

> "| stale field | §Terms, used §0.8 | An identity field whose value on this machine differs from
> **the active acceptance's epoch**; at least one must be stale for a derivation night to be the
> right night. |"

This is main's narrow definition, which the branch deliberately widened at `:143-147`. After a PASS
plus a landed D-102 addendum, the machine's fields DO differ from the acceptance's original epoch,
so §8 says "stale" exactly where §Terms and both refusal rows (`:716`, `:2033`) say "not stale —
already judged". The §8 table's stated job is to give every term's one-line meaning, so this is the
row most likely to be read in isolation at the desk. One-line fix. (Introduced in round 7, not
round 8, but it is what the merged tree now ships.)

---

## (3) Cross-check field names — DISAGREE. A real desk-tool record is refused.

Direction of the handoff: `scripts/epoch_equivalence_check.py` **emits** the
`joulewise.epoch_equivalence_check.v1` record; `issue_epoch_continuation.py prepare-candidate
--equivalence-record` **consumes** it and cross-checks it against its own reconstruction
(`_s9_projection`, `scripts/issue_epoch_continuation.py:280-330`; `_crosscheck` at `:233-250`).

Top level agrees exactly (`schema_version`, `reference_envelope`, `session`, `slot_outcomes`,
`retained`, `m`, `maximum_s`/`maximum_slot`/`minimum_s`/`minimum_slot`/`range_s`,
`level_screen_comparison`, `bracket_screen_comparison`, `verdict`, `verdict_reason`), verdict
lexemes agree (`PASS`/`FAIL`/`INCONCLUSIVE`, emitter `epoch_equivalence_check.py:598-602` vs
`record["verdict"].upper()`), `slot_outcomes` entry keys agree
(`slot, attempt_id, b_fiducial_s, retained, outcome, detail`), `retained` entry keys agree
(`slot, attempt_id, b_fiducial_s`), `session` keys agree, and the two screen values are
numerically identical (`level_screen_s = 0.032898493715362`, `bracket_screen_s = 0.009724`).

### FINDING B (BLOCKER-class) — `reference_envelope` has two fields the issuer refuses

`scripts/epoch_equivalence_check.py:288-300` (`reference_envelope()`) emits **ten** keys:

```
acceptance_file_sha256, acceptance_id, acceptance_path, bracket_screen_s, corpus_n,
level_screen_s, maximum_budgetable_drift_s, raw_corpus_maximum_s, raw_corpus_range_s, screen_rule
```

`_s9_projection` (`scripts/issue_epoch_continuation.py:307-313`) expects **seven**
(`acceptance_id, corpus_n, raw_corpus_maximum_s, raw_corpus_range_s, level_screen_s,
bracket_screen_s, maximum_budgetable_drift_s`), and the provenance allowlist at
`scripts/issue_epoch_continuation.py:237-238` forgives only one extra:

```python
"equivalence_record.reference_envelope": {"acceptance_path"},
```

`_crosscheck` then refuses any remaining unknown key (`:241-242`). The two names the tool emits and
the desk check's consumer does **not** accept:

- **`acceptance_file_sha256`** (the artifact's byte digest — pure provenance, the companion of the
  already-forgiven `acceptance_path`)
- **`screen_rule`** (the screen rule registered for the generation — a reconstructable registry fact)

Executed this session, in the export:

```
$ python3 -c "... I._crosscheck(fixture_reference_envelope, E.reference_envelope(acceptance), 'equivalence_record.reference_envelope')"
REFUSED: ContinuationRefusal equivalence_record.reference_envelope.acceptance_file_sha256
```

So a genuine record written by the merged tree's own desk tool, handed to the merged tree's own
issuer, exits 3 naming a provenance field — never reaching any science comparison. Nothing in the
witness path can succeed today.

Why no test catches it: the witnesses in `tests/fixtures/epoch_continuation/s9-*.json` are shaped as
`_s9_projection` output plus `acceptance_path` (verified: their `reference_envelope` has exactly the
eight keys, missing both `acceptance_file_sha256` and `screen_rule`). They are self-consistent with
the consumer and were never produced by `scripts/epoch_equivalence_check.py` — `tests/fixtures/
epoch_continuation/build.py:36-41` builds them through the issuer, not the desk tool. No test in
either module runs the real emitter into the real consumer.

Contract impact, not just code: `docs/contracts/epoch_continuation.md:307-317` promises that the
flag "accepts an S9 `joulewise.epoch_equivalence_check.v1` witness", that "recognized additional
science fields … are also cross-checked", and that "Unknown fields refuse; only the explicitly
identified path and tool/publication provenance may be ignored." A v1 witness's
`acceptance_file_sha256` is precisely artifact provenance and `screen_rule` is precisely a
recognized science fact — the contract as written is not what the code does.

Severity call for the magistrate: the flag is **optional**, and runbook §2.5 explicitly says "the
record is a witness for the continuation transaction, never its input"
(`docs/phase_2/derivation_night_runbook.md:1738-1740`), and no documented step passes it — so the
PASS route is not blocked tonight and the night is not at risk. But the feature as merged is
dead on its only real input, and the fix is small and local: add both names to the provenance
allowlist at `:238` (or reconstruct `screen_rule` in `_s9_projection` and allow
`acceptance_file_sha256`), plus one test that feeds a tool-produced record through
`prepare-candidate`. A fixture rebuilt from the real emitter would have caught this and should be
the regression's shape.

---

## (4) Commands, pasted verbatim

```
$ cd /tmp/s10-r8-export && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
    tests.test_epoch_continuation tests.test_epoch_equivalence_check \
    tests.test_validate_powermetrics_fiducial tests.test_docs_freshness \
    tests.test_custody_mode_inventory tests.test_mint_policy_resolver_guard 2>&1 | tail -3

Ran 138 tests in 153.001s

OK
```

(run twice; second run `Ran 138 tests in 162.576s` / `OK`)

```
$ cd /tmp/s10-r8-export && PYTHONDONTWRITEBYTECODE=1 python3 scripts/issue_epoch_continuation.py --help | head -30
usage: issue_epoch_continuation.py [-h] {prepare-candidate,check} ...

Prepare an unissued continuation, or authenticate one through its byte pin. A
continuation lets an unchanged acceptance judge another identity epoch (the
machine's six-field identity). A judged epoch is an identity that acceptance
may evaluate. The EQUIVALENCE NIGHT is the one derivation-kind ledger session
of twelve capture slots run on the new epoch and judged, after it closes,
against the envelope the acceptance already carries (directive issue 316).
Acknowledged rows are exactly that night's finalized attempts. The RANGE-
EXPANSION TRIGGER is the acceptance's own re-derivation trigger that fires
when a new valid capture on a judged epoch falls outside the corpus's observed
range; acknowledged rows bypass only that trigger, because the equivalence
rule already compared them against the envelope. Systematic failures remain
triggers and prevent candidate preparation. The level screen caps every valid
capture's bound, resolved or not. The bracket screen caps their range, maximum
minus minimum. Both come from the prior acceptance's ratified operatives: no
threshold is fitted to this night.

positional arguments:
  {prepare-candidate,check}
    prepare-candidate   re-derive a PASS night and write an unissued
                        continuation
    check               require issued, registry-pinned bytes and print judged
                        epochs

options:
  -h, --help            show this help message and exit
```

---

## Nits (no action required)

- `docs/contracts/epoch_continuation.md:64` — the inserted sentence leaves a ~101-column line
  ("detail on a resolved row refuses `slots.anchor_v3_detail`). The reader enforces this audit trail
  but") in a file otherwise wrapped near 78. Cosmetic; `tests.test_docs_freshness` does not enforce
  width.
- `docs/contracts/powermetrics_fiducial.md:191-195` — the new closing sentence restates the snapshot
  fact already given at `:174-176` ("The writer CLI loads its custody-verified snapshot before
  identity preflight…"). It earns its place by attaching the fact to the derivation-only
  `screen_basis` path and adding the claim-time equivalence, but a reader meets the same assertion
  twice in one paragraph.
