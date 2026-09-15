# 70 — Rule-11 consult (Opus 5, contract lens, one round) on PR #338's same-signature residue: rule-persistence wording in the kernel status_note after fix round 3 (2026-09-14 17:55 PDT; worktree at 7a004b37)

Convened because the round-3 delta (record 69) found the class cured in D-181 but present at another site (another missed call site = rule 11's trigger). Verbatim final report.

---

Read-only work complete in `/Users/edr/code/JouleWise-wt-338-e` (HEAD `7a004b37`); nothing written anywhere.

## 1. Exhaustive enumeration

**In-diff sites that keep a prior timing/install rule alive (DEFECT, 1 source + 2 generated):**

- `/Users/edr/code/JouleWise-wt-338-e/docs/process/state_kernel.json:2919` — `INSTALL-WINDOWS-MULTI-01.status_note`, final sentence: `Until landed the ruled single install span stands.` This is the only authored defect. It asserts a *rule* survives, which Ed's ruling 1 voided ("Nothing else about timing is a rule"; the span is "a mechanism limit, not a scientific one").
- `/Users/edr/code/JouleWise-wt-338-e/TASK_QUEUE.md:681` and `/Users/edr/code/JouleWise-wt-338-e/TASK_QUEUE.md:854` — the same sentence rendered into the two generated `A0 | INSTALL-WINDOWS-MULTI-01` rows. Not independent sites: `scripts/gen_state.py` renders both marker-fenced regions from `docs/process/state_kernel.json` (`KERNEL_REL`, line 30), so they are fixed by regeneration only.

**In-diff sites that mention conditioning but are CORRECT as written (no action):**

- `docs/decision_log.md:11853–11856` — "…each clause names its implementation lane, and **until that lane lands the existing mechanism's limits remain facts, not rules** (decided ≠ done: the ruling is in force from the moment it names; what the machinery cannot yet do is a mechanism limit, as Ed's clause 1 says)." This is the round-3 cure and is the correct formulation. Leave.
- `docs/process/state_kernel.json:2913` (`goal`) — "instead of the single 03:00–06:30 block" is a description of the lane's target, not an assertion that the block is ruled. Leave.
- `docs/process/state_kernel.json` `ARM-CENSUS-IDLE-INTERACTIVE-01.status_note` — "A session left open through t0 still refuses the night (plan-span census unchanged)" states a fence Ed **explicitly preserved** ("the census at arm and at t0"). Leave.
- Nit, not a defect: the D-181 Status clause "each clause names its implementation lane" is literally false for cl.2 ("No lane: this clause changes no text"). Cosmetic; does not condition the ruling.

**Pre-dating sentences in the four touched rows (checked at `792b7bc9`):**

- `INSTALL-WINDOWS-MULTI-01.status_note` pre-PR read "…until landed the ruled 03:00–06:30 window stands." → **this PR must fix it**: the PR did not inherit it, it *rewrote* it into "Until landed the ruled single install span stands." The PR is the author of record for the surviving sentence.
- `ARM-RETRY-CLASS-01`, `ARM-CENSUS-IDLE-INTERACTIVE-01`: pre-PR notes carried only "Sequenced after G2-a instrument validation", which this PR correctly replaced/superseded. No residue.
- `ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01`: append-only edit; no "stands"/"until landed" text before or after. Clean.
- **Out of scope, leave:** `docs/decision_log.md:11745` ("…until that lane lands **the prior rule stands** (decided ≠ done)") and `docs/decision_log.md:11754` ("…the ruled 2026-09-10 03:00–06:30 window **stands for** rehearsal-20260911") — both inside the dated **D-180** entry, untouched by this PR. Decision-log convention is correction by dated addendum, not retro-edit; D-181 already supersedes D-180's sequencing, and the rehearsal-20260911 sentence is spent (that night never ran).

## 2. Exact replacement text

Single site, `docs/process/state_kernel.json:2919` — replace the final sentence
`Until landed the ruled single install span stands.`
with (33 words; no `|` or newline, so `_check_cell_text` at `scripts/gen_state.py:101` passes):

> `Until this lands, the machinery still supports only one install span and one fixed launchd minute — a mechanism limit, not a rule; D-181 cl.1 is in force and no timing rule survives it.`

Then regenerate: `python3 scripts/gen_state.py` (verify with `--check`, exit 0), which propagates to `TASK_QUEUE.md:681` and `:854`. No other edits.

## 3. Structural cause and cure

Yes — the cause is the **"decided ≠ done / prior rule stands" boilerplate**, copied forward from D-180's Status paragraph into the kernel row it governed. Round 3 fixed the *instance it was looking at* (the decision-log Status paragraph) rather than the *class*, so the copy living in the kernel row — and its two generated renderings — survived. Same signature, different call site: exactly the rule-11 trigger.

A pure `stands` / `until landed` grep is **necessary but not sufficient**, because the class is semantic (a paraphrase like "remains the rule" or "still governs" would evade it). The cure is exhaustive only if the grep is widened to the paraphrase set and run over the whole diff. That widened grep, run now:

```
git diff 792b7bc9..HEAD | grep -E '^\+' | grep -niE \
 'stands|until landed|until (that|it|this) lane|still the rule|remains (the )?(rule|in force|in effect)|governs|holds until|applies until|unchanged until'
```

Output — 4 hits, no more:

```
18:  TASK_QUEUE.md   A0 INSTALL-WINDOWS-MULTI-01 row (agent lane table)   -> "...Until landed the ruled single install span stands."
47:  TASK_QUEUE.md   A0 INSTALL-WINDOWS-MULTI-01 row (combined table)     -> "...Until landed the ruled single install span stands."
82:  docs/decision_log.md  "until that lane lands the existing mechanism's limits remain facts, not rules"  [CORRECT]
267: docs/process/state_kernel.json  INSTALL-WINDOWS-MULTI-01.status_note -> "...Until landed the ruled single install span stands."  [SOURCE DEFECT]
```

Three of four are the one source sentence and its two renderings; the fourth is the cured wording. Kernel-wide, the only other `03:00–06:30` / `02:56` mentions (lines 2578, 3672, 3696, 3782) are historical records of nights that actually ran or were armed — facts, not rules. The class is closed by the single edit above plus regeneration.

## 4. Proportionality

A fourth **bench** round is proportionate; no cold gate is required. The change is one status_note sentence plus a deterministic regeneration — well under the bench-vs-session threshold (rule 9), reversible, touching no process rule, no stop signal, no severity adjudication, and nothing irreversible, so none of rule 11's mandatory cold-gate triggers fire. What the consult changes is the *shape* of round 4: it must be a grep-gated **class sweep** (the widened grep above, run before and after, pasted into the delta re-audit) rather than a fourth site-at-a-time patch — the site-at-a-time habit is what produced this consult. If the post-edit grep returns anything other than the single line 82 hit, stop and escalate rather than run round five.

**Recommendation:** proceed at the bench with the one-sentence kernel edit + `gen_state.py` regeneration, gate the round on the widened grep returning only the D-181 Status line, and leave D-180's own entry untouched.
