# Opus counter-review (gate ledger row 6) — 518a65a8 on fix/2026-09-21-retained-root-terminal-markers

Reviewer: Claude Opus 5, read-only, worktree `/Users/edr/code/JouleWise-wt-retention-29ea94df`, base main `9e0a4995`.

## Verdict: MERGE

No blocker. Four should-fixes are documentation/pinning, none of them changes an arm decision today, and all four are cheap follow-ups that do not need to gate this merge. The classifier is fail-closed in every state I could construct, the three real roots are unchanged, and the new tests kill the mutations the refuters named.

## Q1 — is the classification sound?

I tried to construct a custody root classified `retained` while a night process could still be alive or a courier could still write into it. Every construction is caught:

- **Refusal written before the chain, driver still running.** `scripts/run_night.py:625` writes `calibration-refusal.json` on the pre-chain path, so `chain.started` may be absent while the driver lives. Markers → `retained` by records alone; the span fence then reads `now <= plan_completion_epoch` (`magistrate_watchdog.py:774-776`) → `ACTIVE`. Caught, and only because of the fix round's span fence.
- **Courier still to write after `chain.exited`.** `plan_span_active` returns True through `t0 + window_max_s + COURIER_DEADLINE_S`, and after that until `deadman_epoch + COURIER_LOCK_FRESH_S` unless `courier.sent` exists. Caught.
- **Spurious second fire on a live root.** `_write_rerun_refusal` (`run_night.py:1740-1759`) writes `rerun.refusal*.json`, which matches none of `REFUSAL_RECORD_GLOBS` (`refusal-[0-9]*.json` does not match `rerun.refusal-01.json`). A rerun-only root stays UNKNOWN, which is the right answer, and the rerun itself does no work. Caught.
- **Unparseable or foreign-`custody_root` plan.** → UNKNOWN, refuses. Fail-closed.
- **Armed-but-not-started root (future t0).** No markers → UNKNOWN, refuses.

The one residual: **`plan_span_active` is evaluated with the ENTRY checkout's constants** (`PLAN_LEAD_S`, `COURIER_DEADLINE_S`, `COURIER_LOCK_FRESH_S`) against a sibling plan that may have been authored under a different repo head. If any of those constants shrinks, an old root could read `retained` while the watchdog that actually owns it still calls the span active. Not reachable today (the three live roots are long past every bound) and doubly fenced by check items 0 (`night_agents`) and 5 (census foreign-PID refusal), so it is a documentation debt, not a defect. Listed as should-fix S4.

Verdict on Q1: **sound for the purpose.** `retained_roots` is one of three independent fences in `check` (`evidence_night.py:909` night_agents, `:916` retained_roots, `:917` census); no single-fence evasion I could build survives all three.

## Q2 — is the `scripts.magistrate_watchdog` reuse legitimate?

**Yes, and it is established precedent in this very file.** `evidence_night.py:487` and `:569` already import `PLAN_LEAD_S, TERM_LEAD_S, KILL_LEAD_S` from the same module inside functions. The contract preamble scopes clone execution narrowly — "It checks plan identity, age and exclusive install close with the clone's code" (`evidence_night_entry.md:178-180`) — and item 5 names argv derivation and ancestry classification as the clone-executed pieces. Item 4 is not about H's artifacts at all: it judges *the machine's* sibling roots, which the clone has no privileged view of. Entry-checkout evaluation is the correct seat. `Storage(plan.parent)` is safe: `Storage.exists` (`magistrate_watchdog.py:272-273`) does not consult `self.root`, and `_write_path` is never reached because nothing writes. The function-local import keeps the 0.43 s watchdog import off the module path.

## Q3 — the three real roots (verbatim output)

`env PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'from joulewise import evidence_night as e; import json; print(json.dumps(e.retained_roots({"roots_under": "/Users/edr"}), indent=1))'`

```
{
 "inventory": [
  {
   "plan": "/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night_plan.json",
   "classification": "retained",
   "reason": null,
   "evidence": [
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night/courier.sent",
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night/result.json",
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night/chain.exited"
   ]
  },
  {
   "plan": "/Users/edr/night-custody/d079-epoch-25g83-derivation-n2-20260919/night_plan.json",
   "classification": "retained",
   "reason": null,
   "evidence": [
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n2-20260919/night/courier.sent",
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n2-20260919/night/result.json",
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n2-20260919/night/chain.exited"
   ]
  },
  {
   "plan": "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night_plan.json",
   "classification": "retained",
   "reason": null,
   "evidence": [
    "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night/courier.sent",
    "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night/result.json",
    "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night/chain.exited",
    "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night/refusal.json",
    "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night/refusal-01.json"
   ]
  }
 ],
 "now_epoch_s": 1790055130.28486,
 "verdict": "pass"
}
```

Three roots, all `retained`, verdict `pass`, no regression. `reason: null` proves the plans parsed and `plan_span_active` returned False for each (an unparsed plan would carry a `plan unreadable:` reason). The pilot root also exercises the new refusal-glob path with a real two-digit `refusal-01.json`.

## Q4 — tests

Fixtures are honest: `sibling_plan` (`tests/test_evidence_night.py:638-648`) is a full `joulewise.night_plan.v2` mapping, and the span test at `:826-833` proves it actually parses — `("ACTIVE", "plan span active (…)")` is only reachable through a successful `NightPlan.from_mapping`. No assertion is vacuous that I could find:

- `test_discovery_span_fence_reuses_the_watchdog_rule` walks all four branches of `plan_span_active` with explicit `now_epoch_s`, including both sides of `t0 + 9000 + COURIER_DEADLINE_S`, and imports the real constant rather than hard-coding it.
- `test_retained_root_classification_ruled_cases` covers all eight ruled Q4 cases plus the `refusal.json`-as-a-directory case, asserts exact full-path evidence lists (Astra F4's basename gap is cured), and separately pins the refusal-only **pass** verdict (`:781-798` rewrite) so the aggregate-fail assertion can no longer mask a wrong row.
- The precedence mutation (retained tested before active) is killed twice: `("chain.started", "calibration-refusal.json") → ACTIVE` and the courier-marker re-check at `:762`.

## Findings

**should-fix**

- **S1 — `joulewise/evidence_night.py:707` — `REFUSAL_RECORD_GLOBS` duplicates `run_night._refusal_paths` and nothing pins them together, while the contract (`docs/contracts/evidence_night_entry.md:224`) says classification is "any regular file matched by `run_night._refusal_paths`".** The stated rationale in the comment at `:703-705` ("mirrored here so the entry checkout classifies without importing the clone") is not correct: `scripts/run_night.py` is in the entry checkout exactly as `scripts/magistrate_watchdog.py` is — which the same function imports at `:713` — and it imports in ~0.00 s with no side effects (probed). Today the two glob tuples are character-identical, so this is drift risk, not a live defect. *Cure:* call `run_night._refusal_paths(night)` directly, or add one assertion test that `REFUSAL_RECORD_GLOBS` equals the globs `_refusal_paths` uses.
- **S2 — `docs/contracts/evidence_night_entry.md:234-235` — the retained trailing sentence now reads as a contradiction.** "Retention classification does not certify process liveness or completed delivery" sits nine lines below two new rules that are *exactly* liveness rules. A reader without project grounding will ask which one is true. *Cure:* rewrite as "Classifying a root `retained` certifies only that a terminal record exists and that the plan's span is over; it does not certify that the courier's delivery succeeded."
- **S3 — `docs/phase_2/derivation_night_runbook.md:743` — "Every line must read `retained`; an `ACTIVE` or `UNKNOWN` line … stops the arm."** Read alone this says the zsh loop is the gate. The correction — that the loop omits the span rule, so it can print `retained` where `check` says ACTIVE — arrives three paragraphs later at `:751-753`. *Cure:* put one clause at `:743` ("this loop reads records only and cannot see the span rule; `check` binds") instead of leaving it to the Source paragraph.
- **S4 — `docs/contracts/evidence_night_entry.md:230-232` — the span rule does not say whose constants apply.** `plan_span_active` runs from the entry checkout against plans authored under other repo heads, so `COURIER_DEADLINE_S` / `PLAN_LEAD_S` / `COURIER_LOCK_FRESH_S` may differ from those the plan was written under. *Cure:* add "evaluated with the entry checkout's timing constants, which may differ from the head that authored an older sibling plan."

**nit**

- **N1 — `docs/contracts/evidence_night_entry.md:226` — "`refusal-N.json`" is ungrounded.** The allocator writes two-digit names (`run_night.py:273`, `{index:02d}`) and the glob is `refusal-[0-9]*.json`. *Cure:* write "`refusal-01.json` and later numbers".
- **N2 — `joulewise/evidence_night.py:731` — `reason` is `null` for every retained row.** The record cannot distinguish "span evaluated and over" from "span never evaluated" without re-deriving it. *Cure:* set `reason = "terminal record present; plan span over"`.
- **N3 — `joulewise/evidence_night.py:736-737` — an unparseable plan on an otherwise plainly-harvested root is UNKNOWN with no cure but moving the root**, which is the property the ruling used to reject Q1 option (b) and which §0.7 now forbids ("Do not move or edit a root to change its line"). Not reachable today — all three live plans parse. *Cure:* none needed now; note it in A263's row so a future schema bump does not strand a harvested root.

## Q6 — merge-ability

Nothing to prune: I looked for overbuild and found none. The `now_epoch_s` parameter is load-bearing (it is the only way the span test pins both sides of a boundary), the `custody_root` realpath guard is what makes the borrowed span rule apply to the right root, and the `reason` field is the evidence the contract now promises. The two new tests plus the rewritten old one are proportionate to a contract change. Docs and code agree on every rule; TASK_QUEUE closes A230/A263 and opens A264 for the ruled Q3 follow-up, with both table copies (compatibility and lane) updated in step.

Missing for a safe merge: only the stated gate — local full replay green plus quick tier (the module alone was 92 tests / 180 s on `9e0a4995`, so the replay is the long pole), then hosted CI post-merge. I did not run the suite per my charge.

## Executed probes (all read-only, none inside the worktree)

- `git diff 9e0a4995..518a65a8` over all six files; `git log --oneline -3`.
- `git show origin/bookkeeping/…:…/10-coldgate-fable-ruling.md` (the ruling).
- The Q3 command above, verbatim output quoted.
- `sed -n 760,800p scripts/magistrate_watchdog.py` (`plan_span_active`, `plan_completion_epoch`), `grep -n "class Storage" -A 40` (`exists`, `_write_path`).
- `sed -n 270,300p scripts/run_night.py` (`_refusal_paths`, the `{index:02d}` allocator), `sed -n 1740,1775p` (`_write_rerun_refusal`), `grep -n 'rerun\.'`.
- `python3 -B -c "import scripts.magistrate_watchdog; import scripts.run_night"` with timing → 0.431 s / 0.000 s, no side effects.
- `sed -n 168,232p docs/contracts/evidence_night_entry.md`; `sed -n "$(grep -n 'def check(' …)",+45p joulewise/evidence_night.py`.
- `grep -nE "^[+-]\|" TASK_QUEUE.md` over the diff; scan of both refuter reports for their verdict blocks (Sol's A263 span gap, Astra's F4 evidence-path gap) to confirm the fix round answered them.
- NOT EXECUTED: the test suite (charge: a replay may be running in the worktree); no writes anywhere; no read of canonical, custody, staging, measurement or LaunchAgents paths beyond the Q3 probe's own discovery.
