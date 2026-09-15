# 13 — Magistrate synthesis: cold gate 25 ruling 10 ADOPTED with the Opus pairing amendments — 09:05 PDT (clock-read)

Magistrate `d6888966` (Fable 5.1). Inputs: ruling 10 (cold Fable judge, convened 08:55:36 from
`wt-coldgate-iw` at `df86cee6`; the ruling's own "08:44–09:05" span is the judge's estimate — the convene script
started 08:55:36 and the file landed 09:01, both clock-read), pairing refuter 12 (Opus, independent answers written
before it read the ruling; refutation 09:04). Verdicts converge on all six questions. No overrule; no dissent.

## Adopted, question by question

- **Q1 — (c) single commit gate.** One line before the success `print` at `scripts/install_night_agent.sh:360`:
  `check_schedule close "$selected_span_close" || exit $?`. Mechanism, not a contract change. Regression: exhibit B's
  four F1 cases with the advance injected at the dead-man bootstrap + the exactly-at-close case; deleting the gate
  line turns all five RED.
- **Q2 — no new constant.** `MAX_INSTALL_DURATION_S` is rejected (same kind as `MAX_PLAN_SPAN_S`); the bound is
  observed by the gate, not predicted. Opus nit adopted: a recorded install start/end pair is diagnostic and allowed;
  no duration may FEED A REFUSAL.
- **Q3 — one EXIT-trap teardown, bootout before remove, AMENDED (Opus, blocker-grade, executed probe).** Ruling 10's
  steps 1–4 stand with this insertion between the bootouts and the restore: after both `bootout`s, re-read
  `launchctl print gui/$uid/<label>` for each label; if either still reports loaded, restore NOTHING and remove
  NOTHING (including `$plist_backup`), print both labels still loaded and the retained plist paths, and return a
  distinct non-zero status; only when both report not-loaded may the restore / `rm -f` / `rm -rf "$plist_backup"`
  run. Step 4's matrix gains a `bootout` rc=1 injection whose expectation is the inverse of the other cells: exit
  non-zero AND both plists still present AND `installed_agent_fence()` still sees the plan. Everything else in Q3
  as written (explicit `exit N` on every failure path; `render … || exit 1`; inline bootout rollbacks at
  `:344,:349,:355-356` deleted; no `always` blocks; teardown never bootstraps; idempotent).
- **Q4 — (i) close first.** Class 2 (P-F3) is live under the shipped default span, and Opus's CASE 2 shows class 1
  crosses under the default too via `install_close_epoch`; option (ii) lands a different lane. Fix round 2 is
  authorised UNDER this ruling (structure changed, not the call site; charter §9 justification present) as ONE seat
  implementing Q1(c) + Q3-as-amended + the Q6 `:1297` sentence, then the delta auditor's isolated-reversion protocol
  on the new regressions, then the twelve-row gate.
- **Q5 — AFFIRM.** Kernel acceptance text for `INSTALL-WINDOWS-MULTI-01` to be recorded exactly as ruling 10 gives
  it (bookkeeping, this activation; the goal sentence keeps Ed's "at any clock time").
- **Q6 — (i) no conflict, AMENDED (Opus, material).** The `:1297` sentence goes into this lane's docs diff. The §3
  item-3 rewrite (`:2085-2086`) is NOT folded into this lane: §3 is byte-identical by every brief of the lane and
  carries the registration constraint; the cross-reference preserves it but lands as a SEPARATE Ed-visible docs
  item (lane to register: RUNBOOK-S3-FAIL-ROUTE-CROSSREF-01, Ed-visible, docs-only, with ruling 10 Q6's text as
  the proposed sentence).

## Process observations (recorded, not decided here)

- Coldness: the judge disclosed the harness auto-loaded `~/.claude/CLAUDE.md` and the worktree's tracked
  `CLAUDE.md` (doctrine). Rule 11's "doctrine-free" premise is weakened by the user-level file, which no worktree
  choice removes. For the council's fresh-eyes sweep / Ed: convene judges with a HOME override or an explicit
  `--no-user-memory`-style flag if one exists. Changes no verdict here.
- The delta auditor's same-signature YES (lt-04) was the correct trigger; the lieutenant's stop was correct.

## Next (magistrate direction)

Lieutenant resumes: fix round 2 (one Astra xhigh seat, WRITE_SCOPE `scripts/install_night_agent.sh`,
`tests/test_install_night_agent.py`, `docs/phase_2/derivation_night_runbook.md` (line 1297 sentence only)) → delta
re-audit (fresh Astra xhigh, isolated reversion of the gate line and of the bootout-verification block) → fresh Opus
counter-review (row 6) → replay (row 9) → fresh-eyes (row 10) → ledger + PR body draft → hand back. Magistrate: rows
7/12, kernel Q5 text, RUNBOOK-S3 lane, PR, merge, post-merge review.
