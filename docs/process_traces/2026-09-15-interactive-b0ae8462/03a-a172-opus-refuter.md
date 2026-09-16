# 03a — Opus contract-lens refuter on the A172 design brief

Read-only seat, 2026-09-15, `JouleWise-wt-lanes-design` @ `84e577ac`. No tests,
installers or processes run.

## Findings

**B1 (blocker) — arm-time `exec` of Python extracted from Markdown.** §3.3
(brief:159) puts two helper definitions inside `ARM-RETRY-HELPERS` markers in the
runbook plus a foreground loader that reads that source out of the doc at
reviewed H and executes it. Its stated reason — "rather than shipping a hidden
retry module in `tests/`" — is the tell: the shape fits a WRITE_SCOPE, not the
system. Those bytes become a production call site on the arm path with no
import-time review, no ordinary mutation surface and no chain-digest coverage,
in a lane #337 and `TASK_QUEUE.md:794` scope as **docs + test**. Use prose steps
with no executable helper, or a real module (`joulewise/arm_retry.py`).

**B2 (blocker) — the budget does not bind, and no notice-age bound exists.** The
budget is "the abort's span plus the next listed span" (brief:154). Live,
`scripts/run_night.py:69` is `INSTALL_SPANS = (("00:00","24:00"),)` — one span
per day, so "same or next span" means **up to ~48 h**. The only real bounds are
`install_close_epoch` (`run_night.py:965` = `t0 − PLAN_LEAD_S − 3600`) and
`PLAN_MAX_AGE_S = 36 h` (`night_gate.py:58`). The notice guard checks only
`sent_epoch_s <= now` plus a NO re-read (brief:156) — no maximum notice age. A
retry could publish ~30 h after the email that is Ed's veto window, and
`test_retry_budget_includes_same_and_next_span_only` still passes: it supplies
synthetic spans and never reads the real constant. Fix: state the operative
bound (plan cutoff + plan age), add a named maximum notice age, and assert
against `run_night.INSTALL_SPANS`. This is also the one gap in an otherwise
replicable "refreshed notice" definition (brief:123,155,156): hashed bytes,
timing and the mismatch set are mechanical, but "stale" is defined only as
digest mismatch or newer abort/NO, never against the clock.

**S1 (should-fix) — `arm_retry_policy.json` is a third copy, neither oracle nor
document.** §3.5 rightly makes the test's cause IDs independent literals and
imports `night_gate` for the code set — so the JSON is bypassed by the tests
that would give it meaning, while buying a renderer, a `--render` mode, two
marker pairs and a "production never imports a test module" rule. The acceptance
asks only that *the two documents* carry the enumeration and *a test* pin it:
enumeration in two marked doc blocks; test asserts four IDs == literal list,
cold set == the union of the two registries, blocks byte-identical. Verdict:
**overbuild under D-161**.

**S2 (should-fix) — partition correct, aimed at the wrong registry.** Verified
independently: 14 gate + 8 driver = 22, reproduced with no misassignment,
omission or invented code, and the two confusable rows (`night_plan_stale`,
`night_refused_boot_clock`) called right. But no gate/driver code *can* be an
arm abort — they are emitted at t0 — so "none of the 22 is retryable" is trivially true. The refusals that
do abort an arm are the installer's 13-row §1.3 table, of which the brief
enumerates three and leaves the rest to prose — while demanding "every code, not
'all others'" for the 22. Unassigned too: `HOLD_CENSUS`
(`magistrate_watchdog.py:1434`, the state that *is* `arm_idle_interactive`) and
`slot_refused` (`NIGHT_HANDBACK.md:392`).

**Test cells.** Mostly real oracles. Two are not:
`test_both_live_documents_render_the_policy_exactly` is tautological against a
renderer mutation (mitigated by cells 1–2), and
`test_final_publication_guard_rereads_after_notice` is an oracle *only because*
of B1 — remove the exec and it degrades to a text assertion, which argues for a
small real module. The must-die set is meaningful only where code exists; for a
pure docs lane it collapses to "delete a table row". Genuine catch worth
keeping: brief:165 — a second abort overwriting the first's
`$STAGE/failed-night_plan.json` evidence.

**Live-state claims — every one I checked is TRUE, no mismatch.**
`night_gate.py:60–94` byte-identical across `84e577ac` and `0ba6ce54`;
`production_census` (`:370`), `handoff_census` (`:959`, docstring warns against
substitution) and `_is_interactive_claude` (`:872`) are as described; two sane
clock samples (`:1191`); network recovery needs control rc=0 and stop ref absent
(`:405–421`); prompt clause (a)/(b) verbatim at line 19; all four handback
anchors and runbook §1.3 match.

## Rulings

**R1 — adopt (b) as amended.** Keep raw-plan SHA-256 and no count cap: a hard
"three attempts" re-inserts the human decision point D-180 cl.2 removes. Do not
adopt the two-span budget as the stated bound — under the live constant it is a
~48 h non-bound dressed as a tight one (B2). Adopt instead: retry until
`install_close_epoch(plan)`, subject to `PLAN_MAX_AGE_S`, a named maximum notice
age and ≥60 s spacing; keep "same or next span" as D-180's ceiling, pinned to
the live constant in test. Drop persistent `arm-retry.json` (it serves only R2).
Keep `$STAGE/arm-attempts/NNNNNN/` — cheap, and it cures brief:165.

**R2 — reject (b); adopt (a) plus one sentence.** The brief says line 19
conflicts with resuming a predecessor candidate. It does — but the same line
ends: "Authoring a new plan with `write_night_plan` and installing its two night
agents under the NIGHT_HANDBACK procedure is arming, not an alteration under
this line." D-180 cl.2 grants relief from the **cold gate**, attached to the
*cause* and requiring only the same plan *class* — not custody of specific
bytes. A successor therefore already has what Ed's goal needs: on finding a
recorded retry-class abort it authors a fresh same-class plan, sends a fresh
notice, and arms — no clause (c), no cross-activation state, no
prior-owner-ended proof, no widening of the prohibition that protects an armed
night. Reusing the predecessor's exact bytes is cosmetic, bought with the most
dangerous edit in the brief. Add to NIGHT_HANDBACK instead: *a retry-class abort
recorded by a prior activation authorises a successor's ordinary fresh-plan arm
of the same class without a new cold gate; the predecessor's published plan
directory, if any, stays untouched under the existing human-resolution path.*

**R3 — adopt (a), scope amended.** Shape right, (b)/(c) correctly rejected.
Amend the list: drop `arm_retry_policy.json` (S1) and
`MAGISTRATE_RELAUNCH_PROMPT.md` (R2), leaving NIGHT_HANDBACK, the runbook and
`tests/test_arm_retry_policy.py`. Agreed cl.2 is class-generic while cl.3 is
stub-only, and pack receipt rules stay hard. If the publication-guard oracle is
wanted back, the correct widening is `joulewise/arm_retry.py` with two pure
functions — not executable Markdown.
