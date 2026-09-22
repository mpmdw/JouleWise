# Record 02 — RETAINED-ROOT-REFUSAL-CLASS-01: the ruled cure on branch `fix/2026-09-21-retained-root-terminal-markers`, gauntlet

Activation 29ea94df, 2026-09-21 22:14–. Authority: cold-gate ruling packet 05 (`05-coldgate-packet-a230-retained-root-discovery/10-coldgate-fable-ruling.md`, sha256 `da4d2760c818926bd4b2731687e0f5e574cee5ba5c951d8021932ed7007cea60`) paired with the Opus contract refuter (`11-opus-contract-refuter.md`, sha256 `0347c6a9f182fd6185441a6bf65683952d3a2aa790efbde88d1e52f329acdc53`); both sealed verbatim at `85ddb9ec` on the bookkeeping branch.

## §1 Synthesis of the gate (charter §5: each reviewer's result, each disagreement, the disposition)

| Q | Cold Fable judge | Opus contract refuter | Disposition |
|---|---|---|---|
| Q1 marker set | AFFIRM (a) with precedence: ACTIVE (chain.started without chain.exited) tested first; retained on courier.sent / result.json / chain.exited / any `run_night._refusal_paths` name; UNKNOWN otherwise; exact contract sentence ruled; pairs refuters | REJECT, BLOCKER: R1 the 09-16 root was already retired (22:03:27) before the packet froze; R2 precedence unstated in the option text; R3 `chain.exited` can be a dead-man `launch_failed` record, so retained ≠ harvested; R4 no span arithmetic (watchdog keeps a plan active by time after chain.exited) | Ruling stands. R1: disclosed in §2 (actor = interactive session a87c3444, Ed at the machine, under D-183, digests written before and verified after the move; not this session). R2: the ruled rule and the code test ACTIVE first. R3: accepted as the contract already says (item 4 last sentence: classification certifies neither liveness nor delivery); a dead-man-reaped root is terminal for arm safety, which is item 4's purpose. R4: residual registered as lane A263 (the watchdog independently fences launches during an active span). |
| Q2 lane A230 | AFFIRM (ii): runbook §0.7 restated in the executable form (exact text ruled); handback retention sentence unchanged | REJECT, BLOCKER: (ii)'s "span half" is not implemented by the check; options came from a narrative source (TASK_QUEUE line) | Ruling stands: the judge held authority from the lane's own text and rule 11; the ruled replacement text names the executable check and forbids moving roots to satisfy §0.7. The span-half gap is the same residual as R4 → A263. |
| Q3 own MCP helpers | AFFIRM (a): procedure; exact handbook step ruled; preferred durable form (c) launch without MCP needs its own packet | REJECT, MATERIAL: prefers (b) code alignment; (a) had no executed evidence; exhibits D1/D2/D8/D9 outside the reviewers' read set | Ruling stands. Executed evidence now exists (§2.3: SIGTERM to the two helpers, no respawn in 60 s, session healthy). (c) registered as lane A264. Exhibit read-set defect noted for the next packet (copy the JSON records into the packet directory). |
| Q4 regressions | eight ruled cases + acceptance command | adds: refusal + open chain → ACTIVE (= ruled case 5); `launch_failed` chain.exited; span-inside case | Ruled cases implemented (§2.2). The `launch_failed` and span cases belong to A263. |
| Hygiene | BLOCKER: the root's move during assembly undisclosed; MATERIAL: C2 used beyond its object for Q1 (judge disregarded it); MATERIAL: module runtime misstated (≈180 s, not 60 s) | BLOCKER same move; BLOCKER narrative-source framing of Q2; MATERIAL asymmetric option notes, selective `plan_span_active` prose, unverifiable exhibits, unflagged authority clash | All accepted as packet defects for this magistrate's next packet; none changes the rulings, which both reviewers reached on the code exhibits. |

No override is issued.

## §2 The change (head `fc28d782`, base main `9e0a4995`) and bench evidence

### §2.1 Files
- `joulewise/evidence_night.py`: `TERMINAL_NIGHT_RECORDS`, `REFUSAL_RECORD_GLOBS` (mirroring `run_night._refusal_paths`), `retained_roots` rewritten: ACTIVE first, then retained on any marker (every marker listed as evidence, also for ACTIVE roots so the lead sees what is there), else UNKNOWN; verdict passes only when every root is retained.
- `docs/contracts/evidence_night_entry.md` item 4: the ruled sentence verbatim; the two unchanged sentences kept.
- `docs/phase_2/derivation_night_runbook.md` §0.7: the ruled replacement text verbatim (lane A230).
- `docs/process/NIGHT_HANDBACK.md` §Arm procedure via the tracked commands: the ruled pre-check step verbatim.
- `TASK_QUEUE.md`: A230 DONE (both tables); A263 RETAINED-ROOT-SPAN-ARITHMETIC-01 and A264 MAGISTRATE-LAUNCH-WITHOUT-MCP-01 registered (both tables).
- `tests/test_evidence_night.py`: marker table extended to eight shapes; `test_discovery_refuses_an_open_chain_and_ignores_non_marker_records` walks the 09-16 shape (refusal + open chain → ACTIVE; + chain.exited → retained; open chain with courier.sent → ACTIVE; receipt-only → UNKNOWN); `test_retained_root_classification_ruled_cases` = the ruling's eight cases (refusal.json only; chain.exited only; refusal-3.json; calibration-refusal.json.2.json; chain.started alone → ACTIVE and `check` refuses naming retained_roots; chain.started + calibration-refusal.json → ACTIVE (precedence); chain.started + chain.exited → retained; plan only → UNKNOWN) plus refusal.json as a directory → UNKNOWN.

### §2.2 Bench runs (this session)
- `-k retained -k discovery` at the bench: 4 tests OK (2.8 s) at `fc28d782`.
- Full module before the ruled cases (draft head): 93 tests OK, 167.6 s. With the ruled cases, first run: 1 failure (my assertion demanded an empty evidence list for an ACTIVE root; the code lists the markers it found — kept, test corrected). Replay at `fc28d782`: see §2.4.
- Patched classifier run read-only against the live custody directory at 22:09: three roots retained (`courier.sent`, `result.json`, `chain.exited` each; the pilot root also `refusal.json`, `refusal-01.json`); the 09-16 root already absent (§1 R1).

### §2.3 Executed probe for Q3 (a)
22:12:41 `kill 75861 75865` (this session's `codex mcp-server` node wrapper and binary, children of session root 75838). At +10 … +60 s: neither PID alive, no new `codex` child under 75838, the session (75838) alive and working. The Codex MCP tool is unavailable to this session from then on; seats run through `codex-run-v3` instead.

### §2.4 Replay at `fc28d782`
`env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_evidence_night` → `Ran 94 tests in 169.226s` / `OK` / rc 0 (22:22 PDT).

## §3 Refuters on `fc28d782` (two distinct lenses, both read-only in their own worktrees; two seats cannot share one worktree — the first Sol launch refused with rc 75 "another scoped runner holds the worktree lock")

| Lens / seat | Result | Findings |
|---|---|---|
| Contract — Astra (gpt-6-astra, high), `/tmp/magistrate-29ea94df/seats/refuter-contract-astra.md` | no blocker | F1 should-fix: runbook §0.7 heading and opening sentence still forbid any discoverable root; F2 should-fix: the runbook's "whose span is active" is not implemented by the check (inherited from the ruling; = Opus R4, lane A263); F3 should-fix: the ruled zsh loop's `(N)` matches directories (contradicts the ruling's own regular-file rule); F4 should-fix: ruled case 1 (refusal-only) not asserted in isolation through `check()`, evidence compared by basename — two in-memory mutants survived; F5 nit: attribution appended inside the ruled passages (contract text itself verbatim); F6 nit: "exactly one family" comment wrong. Verified: classification matches the ruled rule; no scope creep. |
| Execution — Sol (gpt-5.6-sol, xhigh), `/tmp/magistrate-29ea94df/seats/refuter-execution-sol.md` | no blocker | F1 should-fix: the manual loop prints `retained` for a directory marker, a symlinked marker and a directory plan (executed); fourteen fixtures classified as ruled; six mutations (precedence swap, drop chain.exited, literal refusal.json, `exists()` for `is_file()`, ACTIVE on chain.started alone, two-entry set) all KILLED by `test_retained_root_classification_ruled_cases`; module 94 OK (272.5 s); residual = A263 reproduced at t0 + 600. |

Dispositions (lead): every should-fix applied in fix round 1; A263 implemented rather than deferred, because both refuters reproduced it and the ruled runbook text asserts the span half — a stricter fence added on top of the ruled rule, never a relaxation, recorded here as a labeled addition (not an override: the ruling's classification stands and is tested first). The `(N.)` qualifier and the plan-file guard are the one correction to the ruled loop text; the runbook names it as such.

## §4 Fix round 1 → `518a65a8` (bench, this session)

- `retained_roots(state, now_epoch_s=None)`: after the record classification, a `retained` root's own `night_plan.json` is parsed with `NightPlan.from_mapping`; `custody_root` must be the root's own directory (realpath) else UNKNOWN; `scripts/magistrate_watchdog.plan_span_active(plan, now, Storage(root))` true → ACTIVE ("plan span active"); `PlanError`/`ValueError`/`TypeError`/`OverflowError`/`OSError` → UNKNOWN ("plan unreadable: …"). Every row carries `reason`; the record carries `now_epoch_s`.
- Runbook §0.7: heading "Nothing else is armed, and every discoverable root is retained"; opening sentence names ACTIVE/UNKNOWN; loop gains `[[ ! -f $p || -L $p ]] → REFUSED` and `(N.)` on every marker glob; attribution and the correction note moved below the ruled passage.
- Handbook: ruled step verbatim in its own paragraph, preceded by a one-paragraph source note.
- Contract item 4: span sentence appended after the ruled sentences (ruled text untouched).
- TASK_QUEUE: A263 DONE (both tables); A264 stays READY.
- Tests: `sibling_plan`/`sibling_root` helpers give every fixture root a parseable v2 plan ten days old; evidence asserted by full path everywhere; ruled case 1 in isolation through `check()` with the complete row; `test_discovery_span_fence_reuses_the_watchdog_rule` (inside t0 + window + courier deadline → ACTIVE with and without courier.sent; after it, courier.sent closes the span; without it the span runs to dead-man + lock freshness; foreign custody_root → UNKNOWN; `{}` plan → UNKNOWN "plan unreadable: PlanError").
- Fast run at `518a65a8`: `-k retained -k discovery -k span` → 6 tests OK (14.4 s). Full module and full sharded suite: §5.
