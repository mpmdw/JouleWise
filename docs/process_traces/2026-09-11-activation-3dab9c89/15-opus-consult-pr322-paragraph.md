# Opus consult — PR #322 §0.5 C1-registration paragraph

Read-only bounded consult. Worktree `/Users/edr/code/JouleWise-wt-c1-seam`
at HEAD `7fc058b9`. Nothing was edited.

## Q1 — Delete the science detour? YES

Agreed, and more strongly than the brief puts it. The runbook reader's task
in §0.5 is to author and verify a plan field and to predict whether gate
condition C1 will pass; C1 is a pure content-identity check that never
parses, let alone evaluates, the registered rule
(`joulewise/night_gate.py:1300-1328`). Explaining the D-165 ratio therefore
buys the reader nothing operational while importing at least four unbuilt
terms ("energy component", "floor", "unguarded", "dominance sentence") that
this file never needs and never defines — the file has no energy-floor
definition anywhere; its only later "floor" is a minimum time allocation
(`:1090-1111`). It also imports maintenance risk the runbook cannot carry:
D-165 already has a 2026-09-04 dated addendum demoting R_cm to a sensitivity
diagnostic (`docs/decision_log.md:11270`), and the pinned digest constant
itself was rolled on 2026-09-05 for a "v2 relabel"
(`night_gate.py:30-36`). A prose copy of another campaign's rule inside a
calibration runbook is a second, unauthenticated home for that rule; it can
drift while C1 keeps passing. Option (c) — delete — is right.

## Q2 — Fact-check of the refuter's proposed replacement

| Claim in the proposal | Verdict | Evidence |
|---|---|---|
| Records D-165's comparison rule, for the D-117 contrast campaign at `configs/campaigns/d117_contrast_v5` | OK | `docs/decision_log.md:211` (ratio pre-registered into the `_v5` pack); JSON `numerator`/`denominator`/`threshold` fields; the directory itself |
| Rule fixed before that campaign's data | OK | `decision_log.md:211` "fixed before collection"; `:10733-10734` |
| Filename names D-166, "the workload decision" | OK | `decision_log.md:212` and `:10751` — D-166 is "THE WORKLOAD" (`_v5` prompt/prefill-length decision). Recommend "the decision that set that campaign's workload" so the noun phrase is self-glossing |
| Gate "computes the SHA-256 digest of its UTF-8 text" | OK, and the precision matters | `night_gate.py:1302-1307`: `probes.read_text(...)` then `.encode("utf-8")`; production probe is `Path(path).read_text(encoding="utf-8")` (`scripts/run_night.py:295`) — text mode, so universal-newline translation applies. It is NOT a raw-bytes hash; a CRLF copy would hash differently. Keep "as UTF-8 text" |
| Must match `night_gate.D166_REGISTRATION_SHA256` | OK | `night_gate.py:30-36`, compared at `:1315-1326` |
| Applies to `DIAGNOSTIC_NO_PACK` | OK | `night_gate.py:1300`: `if plan.receipt_class in {"DIAGNOSTIC_NO_PACK", "REHEARSAL_STUB"}`. Worth keeping "for this receipt class": for `TRANSACTION_PACK`, C1 is derived from pack custody records instead (`:905-911`), not from this digest |
| "C1 checks that identity without evaluating the comparison rule" | OK | `:1300-1328` hashes only |
| Receipt class = plan's category selecting which checks apply | OK | `class_table()` `:428-457`; `_initial_conditions` `:540-552`; only C2 is `NOT_APPLICABLE` for this class |
| `DIAGNOSTIC_NO_PACK` = night without a measurement pack | OK | runbook `:761-765`; `night_gate.py:436-442` |
| **"measurement pack (a scheduled set of measurement runs)"** | **WRONG gloss — fix** | A pack in this repo is a committed/frozen bundle pinned by identity, not a schedule: the plan's `pack_night` block carries `pack_id`, `pack_root`, `pack_sha256`, `attempt_ordinal` (`night_gate.py:128-131`), the runbook calls it a "frozen campaign pack" (`:374`), and a `TRANSACTION_PACK` night "launches a pack launcher" (`:2048`). Nothing about it is scheduled. Replace with a committed-bundle gloss |
| Pre-registration bound by H and by the digest below/§1.5 | OK | runbook `:243-247`, `:496-497`, `:538-550` |

One further defect the proposal does not fix, and it is a first-use defect
of the worst kind — a **collision with a term this very file already
builds**: §Terms `:150-155` defines **Registration** as "the set of ledger
sessions that the pre-registration declares a derivation corpus is drawn
from". The retained sentence at `:499-502` and the proposal's "the night
gate's registration check" reuse the same word for a JSON file. A reader who
learned the §Terms sense at line 150 will mis-read line 511. The final text
below names the collision in one parenthesis and otherwise avoids the word.

## Q3 — First-use census on the proposed replacement, in context

Built earlier in the file, or glossed inline, and therefore clean: night
gate (`:11-12`), digest ("a fingerprint of the file's bytes", `:14`),
pre-registration / calibration night (`:107-130`), plan (`:53-56`,
`:243-247`), H / measurement commit / pin (`:243-247`), commit tree
(`:189`), `night_gate.<LITERAL>` naming shape (established one sentence
earlier at `:500-501`), §1.5 (forward reference to an existing section),
D-117 contrast campaign (inline gloss "a different experiment"), D-165 /
D-166 (inline), C1 (inline), receipt class (inline), `DIAGNOSTIC_NO_PACK`
(inline + §1.1).

FLAGS against the proposal as written:

1. **"registration" collision** with §Terms `:150-155` — neither built for
   this sense nor disambiguated. Fixed below.
2. **"measurement pack"** — the proposal's gloss is inaccurate (Q2). Fixed
   below with a committed-bundle gloss plus the concrete alternative ("this
   night takes only the twelve calibration captures"), which is what the
   reader actually needs.
3. **"SHA-256 digest of its UTF-8 text"** sits next to the changelog's
   digest gloss "fingerprint of the file's bytes" (`:14`); say "reads the
   file as UTF-8 text" so text-mode reading is explicit rather than a
   silent contradiction of the bytes gloss.
4. Minor: "the workload decision" reads as a defined term; "the decision
   that set that campaign's workload" glosses itself.

No other term in the replacement fails the test. Deleting the science
removes every previously-flagged term ("energy component", "floor",
"corner_widened"/"point"/"unguarded"/`_j`, "dominance sentence") outright.

## Q4 — Final paragraph, verbatim (replaces lines 503-517)

```
The file belongs to a different experiment. It records the comparison rule
that decision D-165 fixed for the D-117 contrast campaign
(`configs/campaigns/d117_contrast_v5`) before that campaign collected data;
the filename instead names D-166, the decision that set that campaign's
workload. What the rule says does not matter to this night, which never
evaluates it. The night gate requires this file for this night's receipt
class and checks exactly one thing, recorded as gate condition C1: it reads
the file as UTF-8 text and requires the SHA-256 of that text to equal the
literal `night_gate.D166_REGISTRATION_SHA256` in the same module. Nothing
else about the file is read. (Beware one word collision: `registration_path`
and C1's "registration" are the gate's own names for THIS file, not §Terms'
**Registration**, the set of ledger sessions a derivation corpus is drawn
from.) A receipt class is the plan's category, and it selects which gate
checks apply; this night's is `DIAGNOSTIC_NO_PACK`, the class for a night
that launches no measurement pack — no campaign's committed bundle of runs,
pinned in a plan by id, root and digest — because this night takes only the
twelve calibration captures (§1.1 defines the class in full). The night's
own scientific pre-registration, the file named at the top of this section,
is bound to the night separately: by H, the measurement commit whose tree
contains it and which the plan pins, and by the digest recorded below and in
§1.5.
```

Lines wrap at 79 columns, matching the file. Re-run
`python3 scripts/gen_derivation_night.py --check` and the two test modules
after pasting; the edit touches prose only, so both should stay green.
