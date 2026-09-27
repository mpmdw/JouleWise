# Cold gate SWEEPCLASS-SAMESIG-01, erratum: the paired refuter's F1 to F6

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, the decision log, or memory or skill files. **Write the contamination disclosure first.**

**Your working tree** is `/Users/edr/code/JouleWise-wt-samesig-cg-3ba66eeb`, detached at `315364b2` (the S1 head). It is the same tree the ruling was written against.

**Why you are convened.** A cold Fable judge ruled SWEEPCLASS-SAMESIG-01 (`21-coldgate-fable-ruling.md`, sha256 prefix 71b1c570, in this directory: `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-3ba66eeb/30-sweepclass-samesig/`). Its paired Opus contract refuter (`22-opus-paired-refuter.md`, same directory; probes in `probes-refuter/`) agrees with most of the ruling. It reports:

- **F1, BLOCKER (a tree finding, from reading; its end-to-end probe was NOT run).** `scripts/run_campaign.py` `_first_eligible_cooldown_anchor` freezes `summary["idle_baseline"]`, an idle power value taken from `evaluate_member`'s pre-gate record, into campaign provenance before the gate at `:9032`. A later campaign reuses it through `prior_campaign_cooldown_anchor`; that campaign's gate covers only its own members, so the source bundle is never battery-checked. The value reaches the verdict rows and decides admission reasons such as `cooldown_cap_hit`. The refuter proposes: return it under step 11, and open a lane that authenticates the anchor's source bundle when the anchor is frozen or reused.
- **F2, SHOULD-FIX.** The consumers form lacks the "every call and every reference" clause that 62 (b) gave the callers form, so a new caller of `evaluate_member` would be silent. It passes on today's tree.
- **F3, SHOULD-FIX.** The promise's file scope omits `docs/paper/**`, where the paper's figure scripts live. Widening it adds 2 rows in a hash-checked script, which need a `historical` grant.
- **F4, SHOULD-FIX.** There is no test row for "a read inside a lambda is never gated". A detector that lets a lambda inherit its enclosing gate passes every new row. The refuter proposes row R51-23b.
- **F5 and F6, NITs.**
  - 61 (b) clause 1 counts plain reads of private names, which are routine (89 private-name imports in 32 files). It should cover writes, plus reads of `_cache`, `_path` and mangled names.
  - Rule 6 should say "nested scopes included".
  - R60-7 needs a `skipTest` when its pinned commit is absent.
  - 61 (c) needs a named route for a tree finding whose fix is production code the ruling did not cover.

**State of play:** the S1 fix-round-3 seat is ALREADY implementing your ruling's §8.2 steps 1–12 as written. It was told to return F1's path under step 11 with executed evidence and not to fix it, and not to add F2/F4's rows. Rule so that your changes can be applied as a small follow-on to that seat's work.

**Rule.**
1. **F1.** First decide whether it is true: execute a probe that traces an unauthenticated bundle's `idle_baseline` through `_first_eligible_cooldown_anchor` → provenance → `prior_campaign_cooldown_anchor` → an admission reason. If true, is it a pre-existing path (present on main `97082508`, before S1), or one that S1 introduced? Does it block S1's merge, or is it its own lane, and in what order relative to the next scored campaign? Give the exact route under 61 (c) for a tree finding whose fix is production code, and name the lane.
2. **F2, F3, F4:** UPHOLD or REJECT each, with exact text and rows (each row with its counterfactual and production call site).
3. **F5, F6:** exact text, or no change.
4. List the complete delta to §8.2 (the added steps or rows) that the seat applies after its current work.

**Keep intact:**
- custody is never a status;
- authentication precedes every exclusion decision;
- `joulewise/battery_float.py` and FT §E's excluded list stay byte-identical;
- the eight consumers do not import `battery_float`.

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every probe in the foreground (split any long probe into short foreground commands).
- Edit no repository file. Scratch goes under `/tmp/cg_samesig_err/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-3ba66eeb/30-sweepclass-samesig/31-coldgate-fable-erratum-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 35 minutes. Mark anything not run as NOT EXECUTED.
- End with a 5-line plain summary for Ed (technical, no project grounding; gloss every internal id).
