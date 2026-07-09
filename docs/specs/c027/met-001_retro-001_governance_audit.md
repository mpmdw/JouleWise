Status: DRAFT pending lead adjudication (C-027 spec wave)

# Spec: MET-001 (governance audit addenda batch) + RETRO-001 (retroactive review of four direct-to-main commits)

Queue rows: TASK_QUEUE.md rows 0s (MET-001) and 0t (RETRO-001).
Evidence base: docs/reviews/2026-07-09-c027-whole-project-review.md §3 B5/B6, §5
governance remedies, §7 rows REV-1..REV-12/MET-7/TOP-7;
docs/reviews/c027/lens-reverse.md findings 1–5, 12; docs/orchestration.md:169–182
(manifest minimum fields); docs/decision_log.md D-031 (~1554), D-050 (~2477).

Scope discipline for the whole batch: **dated records get append-only addenda;
current-state files (RUN_STATE, TASK_QUEUE, checklists) are corrected normally**
(lens-reverse preamble). Both rows are [AGENT]-executable, no hardware.

---

## MET-1 — Dated D-031 breach addendum

**Decision (adjudicate): target is the decision log, not a reviews note.**
The binding addendum goes to `docs/decision_log.md`, appended at the END of the
D-031 entry (precedent: D-031 already carries the dated "Execution topology
addendum (2026-07-07)"). Rationale: D-031 is the breached rule; future readers of
D-031 must see the breach without chasing a reviews file. The long-form evidence
table lives in the MET-5 audit note (below) and is cross-linked, not duplicated.

Text skeleton (append verbatim shape, fill nothing else in):

```
Breach addendum (2026-07-09, C-027 whole-project review, MET-001):

Four commits landed directly on main in violation of this decision's PR
convention (only single-commit bookkeeping may bypass a PR):

- a05e54d — campaign scripts + tests (code+tests; 108 insertions).
- 8856c04 — controller/environment implementation + tests (code+tests;
  158 test lines).
- a835c73 — claims linter + 38 test lines inside a 26-file
  "bookkeeping + integration fixes" commit (code+tests mixed into
  bookkeeping).
- 36d5641 — 33-line scripts/build_site.py behavior change, NO tests,
  mixed with deployment output; postdates the then-recorded
  verification head c095c83, so main carried unverified code.

Content classes: three code+tests commits, one untested site-script
change (counterreview corrected the lead's earlier "all four contain
code+tests" overstatement — see review §6 item 2).

Remediation: retroactive independent review under RETRO-001 (result:
docs/reviews/c027/retro_b6_review.md). Rule going forward: integration
fixes and site-script behavior changes require their own PR; this
addendum does not amend D-031's text, it records its breach. History is
not rewritten; the commits stand.
```

## MET-2 — C-017 addendum: PR #18 wrong-base merge reclassified as merge-gate breach

**Target:** `docs/council_log.md`, dated addendum block appended immediately after
the C-017 full entry (~line 1087 region). Append-only; the original C-017 text
(which calls it a "base-retarget slip recovered via #20") is not edited.

Text skeleton:

```
Addendum (2026-07-09, C-027 review, MET-001 / REV-4): the PR #18 merge
fdcf800 landed into suite-substrate, not main, and required promotion
PR #20 (84a70ca) to recover. Reclassified from operational "slip" to a
MERGE-GATE BREACH: D-031 requires PRs to land to main, and the merge
gate requires sibling merge-order simulation, which would have caught
the wrong base. Code outcome was fully recovered; the gate failure
stands as recorded. No history rewrite.
```

## MET-3 — Stop-card override record (advisor-site episode)

**Target:** `docs/decision_log.md`, dated addendum appended at the END of the
D-050 entry (D-050 owns the stop-card rule; the CP-5 card itself is cleared from
RUN_STATE, so the historical record belongs with the rule, not the current-state
file). Cross-link from the MET-5 audit note.

Text skeleton:

```
Stop-card override addendum (2026-07-09, C-027, MET-001 / REV-5):
during the ACTIVE CP-5 stop card (RUN_STATE at 2c8b267: "Do not start
other queue work"), advisor-site commits bf9ffc5, a1ac0a7, fda79c1,
e6cf431 were produced before CP-5 resumed (later landed via PR #28).
User direction for that work existed and is recorded at
docs/run_reports/2026-07-09-advisor-status-site.md:13, but no override
was recorded on the stop card at the time. Disposition: recorded
retroactively as a USER-DIRECTED OVERRIDE (scope: advisor status site
only; CP-5 state untouched), plus a recording failure — the override
should have been appended to the stop card when work began. Rule
restated: undocumented supersession of an active stop card is
indistinguishable from bypass; overrides are recorded on the card
before the first commit of overriding work.
```

Open point for the lead: if the lead disputes that the user direction covered
starting BEFORE CP-5 resume, the disposition flips to "breach, user-direction
mitigating" — same addendum location, one-line change. Default per the run
report evidence: override.

## MET-4 — D-050 revisit adjudication (manifest requirement)

The D-050 revisit clause ("Revisit when: one full stopped-and-resumed session
completes under the new stop-card rule…") fired at CP-5/C-022 and was never
adjudicated (review §7 MET-7). This unit adjudicates it. Because it CHANGES a
requirement, it is a new decision-log entry (append-only amendment to D-050),
not a mere addendum. Use the next free D-number at write time (D-064 expected;
D-060..D-063 are allocated by C-027 — verify before writing).

Constraints the adjudication must respect: (a) `.codex-bridge/` is GITIGNORED,
so the live manifest is local-only and cannot serve as repo-auditable evidence
as-is; (b) the codex-run observer index at `~/.codex/claude-spawned/index.jsonl`
holds FINISHED rows WITH session ids for 37+ historical invocations (recovery
substrate exists but is also off-repo); (c) C-027 mirrored its own 10 rows into
tracked docs (run report + archived lens files), which worked.

**Options:**

1. **Track the manifest** — un-gitignore `.codex-bridge/invocation_manifest.jsonl`.
   Pro: zero-copy, always current. Con: multi-worktree sessions contend on one
   tracked JSONL (merge noise, exactly the writer-separation failure mode
   REV-11 records); every delegated run dirties the tree mid-session; raw-log
   adjacency risks accidentally tracking snapshots.
2. **Per-session snapshot into docs/** — `.codex-bridge/` stays gitignored as
   the local working buffer; at end-of-session bookkeeping, the session's rows
   are copied verbatim to `docs/process_traces/<session-id>_manifest.jsonl`
   (append-only, one file per session) and the run report links it.
3. **Run-report mirror** — require the run report to carry the manifest table
   inline. Pro: one file. Con: prose file becomes the machine-readable
   authority; tables get "summarized" (that is how ~100 invocations became
   zero rows); hardest to audit mechanically.

**Recommendation: option 2 (per-session snapshot into docs/).** It makes the
manifest repo-auditable (fixes B5/REV-1 structurally), avoids tracked-file
write contention across worktrees, keeps raw logs out of git per
orchestration.md:178–182 (pointer rows with hashes, not payloads), and is the
pattern C-027 already validated. The snapshot step is added to the RUN_STATE
end-of-work checklist and to orchestration.md's manifest paragraph. Run reports
keep only counts + a link. Lead may overrule; record dissent in the entry.

## MET-5 — Manifest recoverability audit procedure

**Output:** `docs/reviews/c027/manifest_recoverability_audit.md` — the audit
note. It also hosts the cross-links for MET-1/MET-3 evidence detail.

Procedure (exact steps):

1. **Enumerate claims.** Extract every claimed invocation from the four run
   reports: C-022 ~35 (docs/run_reports/2026-07-09-cp5-resume.md:132), C-024
   ~20 (2026-07-09-spec-fleshing-wave1.md:88), C-025 ~60 = ~46 workflow + ~14
   direct (2026-07-09-spec-fleshing-wave2.md:49), C-026 ~6
   (2026-07-09-p2034-broad-packs.md:44). Where reports name roles/lenses
   (e.g., "4 counterreview lenses, 3 fix rounds, 4 final-head"), enumerate at
   that granularity; where they give only a count, enumerate as
   `<session>-unnamed-NN` rows.
2. **Enumerate substrate.** (a) Observer index: read
   `~/.codex/claude-spawned/index.jsonl`, filter FINISHED rows, collect
   run_key, session_id, start/end timestamps, command line. (b) Workflow
   journals and surviving out-files under the scratchpad/worktree paths the
   run reports cite. (c) Any `.codex-bridge/` per-run prompt/response/log
   snapshots still on disk.
3. **Match.** Join claims to substrate by timestamp window (session working
   hours from git commit times), role/lens naming in prompts or out-file
   names, and session ids. A match requires at least one concrete artifact;
   narrative co-occurrence is not a match.
4. **Label** each claimed invocation exactly one of:
   - **recovered** — session id AND a surviving prompt or output artifact;
   - **partially-recovered** — session id XOR artifact (one, not both);
   - **unrecoverable** — neither. Never asserted; never backfilled with
     invented hashes or reconstructed "probable" session ids.
5. **Emit the table** in the audit note: one row per claimed invocation with
   columns `session | claimed role/lens | claim source (report:line) |
   matched run_key/session_id | evidence path(s) | label`. Summary counts per
   session at the top.
6. **Apply the marking rule:** every final-head / self-merge / "fresh review"
   gate (REV-3 set: e.g., the reviews claimed before merges 10f40b6 and
   c095c83) whose supporting invocation is labeled unrecoverable gets the
   marking **"reported, independently unverifiable"** — appended as dated
   addenda to the corresponding council-log entries (C-022/C-024/C-025/C-026)
   and flagged in the audit table. Claims are never deleted or softened in
   place; the marking is additive. Recovered gates get their session ids
   appended instead.

## MET-6 — C-024 fix-round count clarification

**Target:** `docs/council_log.md`, dated addendum after the C-024 entry
(pointer row ~line 61 and full entry ~line 1358). Append-only — the council log
is the count authority (REV-12), so neither number is silently edited.

Text skeleton:

```
Addendum (2026-07-09, C-027, MET-001 / REV-12): C-024 records "3 fix
rounds" while its run report records fix units F1–F6 ("6 fix rounds",
counted as 6 in the session total). Clarification: [after checking the
wave-1 report's F1–F6 rows, state the actual relationship — e.g. "3
chronological fix ROUNDS comprising 6 fix UNITS" — or, if the records
genuinely conflict, say so]. Convention going forward: council log
counts ROUNDS; run reports may additionally count UNITS and must label
which they are counting.
```

The implementer must read the F1–F6 rows in
docs/run_reports/2026-07-09-spec-fleshing-wave1.md before filling the bracket —
do not guess the reconciliation.

## MET-7 — D-054 170-vs-180 bundle-count amendment (queue-row item)

Queue row 0s also mandates "D-054 170-vs-180 amendment" (review §7 TOP-7),
which the C-027 spec brief did not enumerate — included here so the row's
acceptance is satisfiable. **Target:** dated addendum at the end of the D-054
entry in `docs/decision_log.md`, stating which count (170 or 180) is correct,
the basis of the discrepancy, and which downstream docs cite the wrong number
(correct current-state citers normally; dated citers get nothing — the addendum
is the record). Implementer derives the correct count from the D-054 entry and
the guard-floor artifacts it cites; if underivable, the addendum records the
discrepancy as unresolved with both sources named.

---

## RETRO-1 — Retroactive independent review of the four B6 commits

**Review packet.** The four commits are non-contiguous on main, so the packet
is the concatenation of per-commit patches, NOT a range diff (a range would
drag in reviewed intervening merges):

```
cd /Users/edr/code/JouleWise
for c in a05e54d 8856c04 a835c73 36d5641; do
  git show --stat --patch "$c"
done > docs/reviews/c027/retro_b6_packet.txt
```

Commit the packet alongside the result (it is small, and it freezes exactly
what was reviewed).

**Reviewer composition.**
- Two fresh read-only Codex lenses via `scripts/codex-run` (read-only sandbox),
  neither with prior session context: L1 correctness/evidence-integrity lens
  (does any diff affect measurement, reduction, claims, or site output
  incorrectly?), L2 tests/regression lens (are the shipped tests adequate;
  what does untested 36d5641 change in build_site.py behavior?).
- Lead gate (never delegated, per hard rule 1): lead runs the full suite at
  current head AND live-verifies the 36d5641 build_site.py change by
  regenerating the site and diffing output against expectations — 36d5641 is
  the untested commit, so it gets the live check.
- All three invocations get manifest rows under the MET-4 regime (snapshot
  into docs/process_traces/ at session end).

**Severity rubric.** blocker = defect currently on main affecting measurement/
evidence/claims correctness or deployed site output; should-fix = real defect
without evidence impact; nit = style/clarity. Verification per
adversarial-review tiers (blockers 2 refuters, should-fix 1, nits 0).

**Recording.** Result file `docs/reviews/c027/retro_b6_review.md`: packet
pointer, lens findings, lead-gate results, disposition per finding. Plus a
dated council-log addendum row (pointer entry) crediting layer yield.

**Closure conditions (what closes RETRO-001):**
1. Every finding dispositioned in the result file (fixed / queued / declined
   with reason). Any blocker fix lands via its OWN PR — never direct-to-main
   (that would re-enact the breach under audit).
2. Lead gate complete: suite green at head + build_site.py live check done by
   the lead.
3. RUN_STATE "Current Verification" advanced past 36d5641 to the post-review
   head, citing retro_b6_review.md as the evidence (this clears the REV-7
   "verification stops at c095c83" drift for this axis).
4. Queue row 0t marked done with the result-file pointer.

---

## Fences (bind both rows)

- ALL addenda are APPEND-ONLY. No editing of dated entries (decision log
  entries, council log entries, run reports); only current-state files
  (RUN_STATE, TASK_QUEUE, checklists) may be corrected in place.
- NO history rewrites: no rebase, no force-push, no amending the four commits;
  they stand as-is with the addendum record.
- NO invented evidence: unrecoverable stays labeled unrecoverable; no
  reconstructed hashes, session ids, or timestamps; "believed" never becomes
  "verified" without an artifact.
- The audit table asserts labels, never recovery; the marking rule adds
  "reported, independently unverifiable" rather than deleting claims.
- MET-4's decision entry is the only unit that changes a forward-going rule;
  everything else records the past.

## DEVIATIONS / OPEN QUESTIONS for the lead

1. **MET-7 added beyond the spec brief:** queue row 0s requires the D-054
   170-vs-180 amendment; the brief's unit list omitted it. Included as MET-7.
   Confirm or split to its own row.
2. **MET-3 disposition default:** spec defaults to "user-directed override,
   recorded retroactively + recording failure" based on advisor report line
   13. Lead confirms the user direction covered pre-resume start, else flip to
   "breach, mitigated".
3. **MET-4 D-number:** D-064 assumed next free — verify against decision log
   head at write time.
4. **MET-4 recommendation** (per-session snapshot into docs/process_traces/)
   needs lead ratification since it amends D-050's manifest requirement;
   dissent recorded in the entry if overruled.
5. **Ordering:** MET-5's audit should run BEFORE the REV-3 markings are
   written (the audit determines which gates get marked); MET-1/2/3/6/7 are
   order-independent. RETRO-001 may run in parallel with MET-001 but its
   closure (RUN_STATE verification advance) should land in the same session's
   bookkeeping as the MET-1 addendum so the breach record and its remediation
   point at each other.
6. **Marking-rule blast radius:** if the audit recovers most C-022/C-025
   final-head sessions via the observer index (37+ FINISHED rows exist), few
   or no gates get marked — the spec does not presume the markings will be
   needed, only that the rule fires mechanically on unrecoverable labels.
