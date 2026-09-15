# lt-05 — CONSULT REQUEST: the lieutenant stops the fix loop on INSTALL-WINDOWS-MULTI-01

Written 08:27 PDT 2026-09-15 (clock read). **No fix round 2 was launched.**

## The trigger fired, and it is mandatory

The standing escalation trigger: *two consecutive rounds failing with the SAME
SIGNATURE — same defect class, another missed call site, another failed
formulation — is evidence of a structural problem, and the next spend is a
CONSULT, not round three.* The lieutenant is forbidden to continue past an
escalation trigger and forbidden to self-exempt from a mandatory one.

The independent delta auditor answered the same-signature question **YES**,
unprompted by any finding of the lieutenant's, and named two classes:

1. **Missed boundary-check call site.** Round A (seat A's implementation) omitted the listed-span check from every `close`-mode recheck. Round B (fix round 1) added the selected span's close to the `close`-mode checks — and the delta shows the FINAL bootstrap, `install_night_agent.sh:348`, still crosses it: four executed fake-launchctl cases end **exit 0 with both agents loaded**, including one that crosses TWO span boundaries. Same class, one call site further along.
2. **Incomplete failure cleanup.** Round A left rendered plists behind after a failed bootstrap. Round B added an EXIT trap to make cleanup complete — and the delta shows `set -e` from inside `render()` SKIPS that trap on zsh 5.9 (minimal proof: `/bin/zsh -c 'set -e; trap "print trap-fired" EXIT; f() { false; }; f'` exits 1 silently), leaving a plist overwritten and a backup directory leaked; and that TERM/INT/HUP after the first bootstrap now delete BOTH plists while leaving the job LOADED — strictly worse than round A, because the installed-plist fence depends on those files to see an armed plan.

Two rounds, two classes, both repeats. This is the shape the rule exists to
catch, and it is exactly the disposition the rule distrusts — "it is only one
more line at `:348`" — that would make a third round feel cheap.

## What the lieutenant is NOT doing

Not writing fix round 2. Not adjudicating the blocker's severity (it stays a
blocker; it is unclosed). Not opening a PR. Not merging. Not touching runbook
§3. The integration head stays at `df86cee6`, pushed, with the blocker OPEN and
documented.

## The lieutenant's structural hypothesis — offered to the consult, not decided

Both classes have one shape: **the installer performs a multi-step, non-atomic
mutation of machine state (render two plists → bootout → bootstrap → bootstrap →
verify) whose preconditions are TIME-VARYING, and correctness is being pursued
by adding point checks at individual call sites.** The set of call sites is not
closed, so each round closes the ones it can see and the next audit finds
another. The cleanup path has the mirror defect: it is attached to exit paths
(traps, per-branch rollback) rather than being one idempotent routine with a
single entry.

A structural answer would replace "check at every call site" with "make crossing
impossible", e.g. refuse BEFORE the sequence begins unless the whole bootstrap
budget fits inside both bounds — `now + MAX_INSTALL_DURATION_S < min(selected
span close, install_close_epoch)` — and, if the sequence nevertheless overruns,
fail through ONE idempotent teardown that bootouts by label and then removes
files, in that order, so a partial install can never end with a loaded job and no
plist. The lieutenant has NOT implemented this and does not have the authority to
adopt it: it introduces a new constant and changes the installer's refusal
contract, which is design-bearing and belongs to the adjudication that produced
record `1acf2aee/06`.

## Questions for the consult

1. Is the point-check approach salvageable for the remaining call site, or is the restructure above (or another) required before any further round?
2. `MAX_INSTALL_DURATION_S` would be a new constant. The adjudication explicitly ruled out inventing new ceiling constants in this lane (it rejected `MAX_PLAN_SPAN_S` for exactly that reason). Does that ruling extend here, and if so what mechanism carries the bound instead?
3. F3's teardown ordering — bootout before file removal — changes what a signalled install leaves behind. Is that a mechanism choice or does it need adjudication, given the installed-plist fence reads those files?
4. Does the blocker need to be closed at all before this lane lands, given it is LATENT under the shipped whole-day default `(("00:00","24:00"),)` and becomes live only when a narrowed span list is configured? A defensible alternative is to land the lane with a documented, test-pinned refusal to accept any span list OTHER than the shipped default until the installer is restructured. **The lieutenant has no authority to choose this and is not recommending it** — it trades a capability this lane exists to ship against an unclosed blocker, and that trade is the magistrate's or Ed's.

## Two further items the consult should carry

- **Acceptance clause (c) narrowing (FIX-5).** "t0 may be any clock time" now reads "any whole minute that occurs exactly once in local time". Ruled by the lieutenant, fail-closed, reversible in one predicate. Reasoning and dissent route are in `lt-03`.
- **The pre-registration question (seat D F2 / contract refuter §8).** Runbook §3's FAIL-route distinct-calendar-days constraint is judged DESIGN-BEARING by both the docs seat and the contract lens, which cites `configs/calibration/preregistration_d079_epoch_25g83_rev1.md:143` and `docs/decision_log.md:11869-11876`. §3 is byte-identical (SHA-256 `71337a836df21f1f3668bcb46e7ffe6e487a247f7ce51368b459b9516612072b`). It is for the cold gate or Ed, and it is INDEPENDENT of the blocker — it can be ruled in parallel.
