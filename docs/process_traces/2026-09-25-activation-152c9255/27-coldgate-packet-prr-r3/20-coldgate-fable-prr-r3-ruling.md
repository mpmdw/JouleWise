# Cold Fable gate PRR-R3-01 — ruling on R3 (R16-a placement) and amendment A-R5a-1

Judge: Claude Fable 5.1, fresh session, worktree `JouleWise-wt-coldgate-152c9255-prrr3` (HEAD 5ebef5e2, docs branch). Machine clock at validator run 10:01:12 PDT 2026-09-25; at writing ≈10:06 PDT. Foreground only; no subagents, no background tasks, no sudo/launchctl/powermetrics/systemsetup/pmset; the canonical root, night-custody, measurement directories and LaunchAgents were not touched; the only file written is this one. PR-L code was inspected by `git show 99495ba9:<path>` and a `git archive` extract under `/tmp/cg-prr-r3-prl`; PR-R by `git show 8cd9e831:<path>`.

**Disclosure of auto-loaded context.** The harness injected `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, and the auto-memory index `MEMORY.md` (truncated) before I acted. None was requested; none is used as evidence. I read no RUN_STATE, TASK_QUEUE, council log, run report, CLAUDE.local.md, or process-trace file outside the packet directory, with one bounded exception: to check ex-06 for selective quotation I hashed its source file and extracted exactly lines 34–48 of it (nothing else of that file was read).

## 0. Trust anchors (recorded before the merits)

| Item | Expected | Observed | Method |
|---|---|---|---|
| Charter, deliberate-typo run | `…5d82` | `…5d81` | `scripts/validate_gate_packet.py` → `result: REFUSE`, `reason: charter_trusted_observed_mismatch`, rc=2 |
| Charter, correct run | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | same | validator `result: PASS`, rc=0; independently `shasum -a 256` = same |
| Packet `00-charge.md` | `2551af8ed9bfe592628132afc9bfa03784490aeb0fee4571df1df80c33a112df` | same | validator + `shasum -a 256` |
| ex-06 / ex-20 | manifest values `4f8bda1e…` / `d596801d…` | both `observed == expected` | validator receipt, `exhibit_manifest_sha256 0d1179f5…` |
| ex-06 source | `98621b06…6382c3`, lines 34–48 | `shasum -a 256` = same; `diff` of source lines 34–48 against ex-06 lines 6–20 = IDENTICAL | the quoted range is complete and verbatim; rule text is line 42 as stated |

## 1. Probes executed

| # | Probe | Result |
|---|---|---|
| P1 | R16 mechanism, PR-L head 99495ba9 `joulewise/night_gate.py` | cutoff `MEASUREMENT_ROOT_CUSTODY_CUTOFF_EPOCH_S = 1790340000`, root `/Users/edr/night-custody/measurement` (`:200-201`); exemption branch `:1251-1263` grants `rehearsal = True` only for `TRANSACTION_PACK` + `pack_night` + `_pack_object(path, "authorization_record", sha256)` with `purpose == "T0_REHEARSAL"`, any `PackNightRefusal/OSError/ValueError` → no exemption; R16 refusal body `:1264-1285` unchanged for every other plan |
| P2 | Rehearsal invariants, same file | `_authenticate_pack_records` refuses `claim_eligible` true for any non-`CAMPAIGN_TRANSACTION` purpose (`:988-989`); `_pack_rehearsal_roots` requires the `rehearsal-t0-unattended-` window-id prefix iff purpose is `T0_REHEARSAL` (`:1107-1110`, `t0_rehearsal.py:39`) and refuses containment against every production custody root, detail `rehearsal_roots_not_disjoint: measurement_root` (`:1116-1147`); `scripts/run_night.py:2134` requires `T0_REHEARSAL` and `claim_eligible is False` on the rehearsal path |
| P3 | Named tests on the PR-L extract | `test_night_gate -k rehearsal_exempts_only_authenticated -k exemption_requires_real_authorization_digest`: Ran 2, OK; `test_run_night -k post_cutoff_t0_inside_measurement_custody_refuses_disjointness_end_to_end`: Ran 1, OK |
| P4 | Revision 5 text at candidate 8cd9e831 `configs/calibration/preregistration_d079_epoch_25g83_rev1.md:600-647` | read in full; contains no mention of R16, custody root, rehearsal, exemption or `measurement_root`; launch-context sentence at `:608` with four placeholders `<PR-L-MERGE-SHA>`, `<RENDERED-PLIST-SHA256:night|deadman|probe>`; no fix commit has landed (branch tip = 8cd9e831; last commits touching the file are 62db28b7, 3c52518d) |
| P5 | R16-a on `origin/main` / candidate | absent from both (`git grep`); R16-a exists only in the PR-L ruling ex-06 quotes |
| P6 | Templates at 99495ba9 | `com.joulewise.night.plist.template` sha256 `e62a461b9f739be6aa57588219674cbb27f574dc40930ee1ee706f230442e5c8`, `ProcessType=Interactive` at line 7, 15 `@@…@@` placeholders incl. `@@PLAN@@ @@CUSTODY_ROOT@@ @@MONTH@@ @@DAY@@ @@HOUR@@ @@MINUTE@@`; `com.joulewise.night-probe.plist.template` sha256 `1570b74587075445ee64fff9b14b718a4b753ec3432db9363455636a2d2fc1fd`, `ProcessType=Interactive` at line 6, `@@PLAN@@ @@RECEIPT@@ @@PROBE_DIR@@`. PR-L adds exactly one line to each vs main (`git diff --stat`) |
| P7 | Installer at 99495ba9 `joulewise/night_agent_install.py` | one night template feeds both `com.joulewise.night` and `com.joulewise.night.deadman` (`LABELS :39`, `validate_install :1170`, `render` `:634-650` substitutes `@@MODE@@`/calendar/`@@LOG_STEM@@` per label from `self.template`); probe from `night-probe` template (`:1031`); `rendered_plist_sha256 = _digest_bytes(payload)` per label on the rendered bytes (`:578-593`), `ProcessType != "Interactive"` refused per label (`:588-589`) |
| P8 | Consumers of the pin sentence at 8cd9e831 (`git grep`) | exactly: registration `:608`; issuer `scripts/issue_calibration_acceptance_generation.py:1283-1289`; `tests/test_acc_25g83_rev5.py:26-38,147-148`. No other file parses `rendered-plist digests` or `template at commit` |
| P9 | PR #412 | OPEN, `mergeCommit: null`, base `main` (gh, 10:05 PDT) |

## 2. Rulings

### Q1 — AFFIRM the final pass's expected outcome: R16-a is NOT in Revision 5; acceptance-rulings record only

Applying ex-20 §2 R3's rule to the verbatim text (ex-06 line 14):

- **(i) Permits a W1/W2/W3 capture armed or retained outside the operating condition? No.** R16-a "removes only R16" (the `measurement_root_outside_custody` refusal) and only for a plan whose authenticated authorization record has `purpose` exactly `T0_REHEARSAL`. The operating condition (launchd agent, `ProcessType=Interactive`, pinned template) is enforced by the installer on every label of every plan regardless of purpose (P7 `:588-589`); R16-a does not touch it. An exempted plan must carry `claim_eligible = false` (P2 `:988-989`, restated in R16-a's own text) and a rehearsal window id, so it cannot be a W1/W2/W3 window and cannot yield a retained member. Both directions execute (P3).
- **(ii) Changes the custody root or evidence path of any member capture? No.** R16-a sets no path. It lifts one refusal for rehearsal plans, whose roots must remain disjoint from every production custody root including `/Users/edr/night-custody/measurement` (P2 `:1116-1147`; end-to-end refusal in P3). Member captures (any non-rehearsal plan) stay under R16 exactly as before (P1 `:1264-1285`).
- **(iii) Alters any element (a)–(o)? No.** The Revision 5 text (P4) contains no sentence about R16, custody roots or rehearsals; ex-20 R2 located every element (a)–(o) inside lines 600–647, and R16-a changes none of those lines. Basis stated plainly: I rule (iii) on the primary Revision 5 text plus ex-20's location of (a)–(o) within it; the (a)–(o) list itself is not in the packet (NIT N1 below).

**Ruled text.** R16-a is recorded in the acceptance-rulings record only, not in Revision 5. Placement: the magistrate appends to the acceptance-rulings record, under a dated heading `R16-a (2026-09-25, PR-L final pass, ratified placement PRR-R3-01)`, the R16-a paragraph exactly as ex-06 line 14 reads (from "R16-a. The `measurement_root_outside_custody` refusal…" to "…no quiet-admission plan receives the exemption."), citing source `docs/process_traces/2026-09-25-activation-152c9255/24-finalpass-packet-prl/20-fable-final-pass-prl.md` line 42, sha256 `98621b0621e3f24bd04f5b190fbfadda595ff74d3b8c846b39574df0e26382c3`. Revision 5's text is not edited for R16-a; the `# Revision 5 (` header, lines 600–647, and the seal digest are unaffected by this ruling. The code comment "pending final pass" at `night_gate.py:1249-1250` may be updated to cite the PR-L ruling in a later PR; that is not a condition of anything here.

### Q2 — AFFIRM amendment A-R5a-1 in substance, with the exact ratified text amended as below (three corrections, none changing the mechanism)

The amendment is correct on primary evidence, independent of any ruling text I could not read: the rendered plists embed per-window values (P6, P7) so three rendered-plist digests sealed before W1 cannot describe W2/W3; the templates are campaign-constant once PR #412 lands and carry `ProcessType=Interactive` (P6), which is the physical operating condition the pin exists to fix; the installer refuses any non-Interactive rendered plist per window (P7). The consumer set is exactly the three sites F1 rewrites (P8), so the amendment is complete. Corrections to F1's exact text: (1) ex-20 lines 74–75 carry stray backtick fragments from quoting; the clean text is given here. (2) "the merge commit of PR #412 on main" is ambiguous under squash/rebase merges and under the `integ/2026-09-25-prl-prr` branch; the pin is the commit GitHub reports as PR #412's `mergeCommit`. (3) The addendum sentence "recorded per window in the arm evidence and probe receipt under R2" and "R15's 'template digests' wording governs" cite ruling clauses not exhibited; the ratified addendum states the mechanism directly and cites the ruling file by path so it is checkable.

**Ratified text A-R5a-1 (record verbatim):**

> A-R5a-1 (2026-09-25, PR-R cold final pass PRR-FINALPASS-01 F1, ratified by cold gate PRR-R3-01): Under ACCEPTANCE-25G83-02 R5(a) as ruled in `docs/process_traces/2026-09-25-activation-152c9255/05-coldgate-packet-acc2/30-addendum/21-coldgate-fable-acc2-addendum-ruling.md`, Revision 5's pinned operating condition names the commit at which PR #412 (PR-L) landed on main and the sha256 of the two launchd templates `configs/launchd/com.joulewise.night.plist.template` (rendered for both the night and dead-man labels) and `configs/launchd/com.joulewise.night-probe.plist.template` at that commit. Rendered-plist digests embed per-window values (plan path, custody root, probe receipt path, launch calendar); the installer records them per window in that window's arm evidence and probe receipt as `rendered_plist_sha256`, and they are not part of the registration text. Where R5(a) says "rendered-plist digests", read "template digests".

**Where it is recorded (the seal step cites this):** `docs/decision_log.md`, a new entry with the exact heading `## ACCEPTANCE-25G83-02 addendum A-R5a-1 (2026-09-25): Revision 5 operating-condition pin = template digests`, placed immediately after the existing `## D-126 addendum (2026-09-25): Revision 5 corpus and equivalence for epoch 25G83/v3` entry (candidate `decision_log.md:12203`), body = the ratified paragraph above plus one line `Ratification: docs/process_traces/2026-09-25-activation-152c9255/27-coldgate-packet-prr-r3/20-coldgate-fable-prr-r3-ruling.md §2 Q2.` If the magistrate also keeps a separate acceptance-rulings record, copy the same paragraph there; the decision-log heading is the citable home.

**Revision 5 line 608, exact replacement.** Replace from "The pinned operating condition is" through "…seal the literal tokens without backticks." with:

> The pinned operating condition is captures launched by a launchd agent with `ProcessType=Interactive`, template at commit <PR-L-MERGE-SHA>, template digests <TEMPLATE-SHA256:night> and <TEMPLATE-SHA256:probe>. The first digest is the sha256 of configs/launchd/com.joulewise.night.plist.template (shared by the night and dead-man labels) and the second of configs/launchd/com.joulewise.night-probe.plist.template, both read at that commit. Each window's rendered-plist digests are plan-specific and are recorded in that window's arm evidence and probe receipt by the installer; they are not part of this text. Sealing replaces these three literals after PR #412 lands on main and before W1's arm notice: the commit is the one GitHub reports as PR #412's merge commit (`gh pr view 412 --json mergeCommit`); each digest is `git show <that commit>:<template path> | shasum -a 256`. The placeholder count (`grep -c -E '<PR-L-MERGE-SHA>|<TEMPLATE-SHA256:'` on this file) must be 0 before the arm-notice digest is taken; seal the literal tokens without backticks; at the seal, replace the header parenthetical "sealing pending PR-L pins" with "sealed <YYYY-MM-DD> at PR-L merge <first 8 hex of the commit>" (amendment A-R5a-1, `docs/decision_log.md`).

The sentence "Launch context sets the sampler cadence; this condition is part of the registered experiment." that follows stays unchanged.

**Issuer** `scripts/issue_calibration_acceptance_generation.py:1283-1289`: placeholder regex → `r"<PR-L-MERGE-SHA>|<TEMPLATE-SHA256:[^>]+>"`; malformed check → `re.search(r"template at commit [0-9a-f]{40}\b", text)` and `re.search(r"template digests [0-9a-f]{64} and [0-9a-f]{64}\b", text)`; both refusal messages unchanged.

**Tests** `tests/test_acc_25g83_rev5.py`: `LAUNCH_CONDITION = re.compile(r"template at commit \S+, template digests \S+ and \S+\.")`; `registration_with_launch_pins(commit, night, probe)` builds `f"template at commit {commit}, template digests {night} and {probe}."`; `sealed_registration()` → `("a"*40, "b"*64, "c"*64)`; unsealed fixture `("<PR-L-MERGE-SHA>", "<TEMPLATE-SHA256:night>", "<TEMPLATE-SHA256:probe>")`; malformed fixture `("not-a-commit", "b"*64, "c"*64)`; add to `test_issuer_refuses_unsealed_launch_context_and_disposes_exact_ids` one case whose digest sentence reads `template at commit <40 hex>, rendered-plist digests <64 hex>, <64 hex>, and <64 hex>.` and assert refusal `pins are malformed`. The decision-log disposition entry and `docs/calibration/acc_25g83_rev5_simulation.md`: no change (as F1).

Everything else in ex-20 F1 (F2, F3 unchanged) stands as written. This is an AFFIRM of the amendment with exact text; no new rule beyond A-R5a-1 is requested.

## 3. Findings

**BLOCKER:** none.

**MATERIAL:** none. (The F1 text defects corrected above are executable ambiguities, cured by the ratified text; had they been applied literally, the seal step would have had to choose the commit under a non-fast-forward merge, which is why the text is corrected here rather than left.)

**N1 — NIT, packet hygiene.** The elements (a)–(o) list (acc2 addendum ruling §5 R5) and the R5(a)/R15 clauses that A-R5a-1 amends are not exhibited; Q1(iii) and Q2 were decidable on the Revision 5 text and the code, so no REFUSE, but a packet amending a ruling clause should quote that clause with path, digest and line range as ex-06 does.

**N2 — NIT, packet hygiene.** The charge states assembly at 10:05 PDT; the packet files carry mtime 10:00 and validated on this machine at 10:01:12. Same defect as ex-20 F4(ii); does not affect the merits.

**N3 — NIT, observation.** `night_gate.py:1249-1250` still labels the exemption "magistrate provisional reading … pending final pass"; after the PR-L ruling it should cite the ruling. Cosmetic; not a merge condition here.

**N4 — NIT, observation.** No fix commit has landed on `feat/2026-09-25-acc-registration-rev5` (tip 8cd9e831). The ex-20 FIX-FIRST order (merge PR #412; land F1–F3 verbatim in one commit; one-lens delta re-audit; then merge PR-R; seal after) is unchanged by this ruling, with F1 applied in the text ratified here.

## 4. Plain summary for Ed

The rehearsal-only exemption to the custody-root refusal (R16-a) stays out of the Revision 5 registration: it cannot arm, retain or relocate any real window capture, so it is recorded with the acceptance rulings only. The registration's launch pin is changed, as the final pass asked, from per-window rendered-plist digests to the two launchd template digests at PR-L's merge commit; the exact wording is ratified above and goes into the decision log.

## 5. Disposition

Q1: AFFIRM — R16-a not in Revision 5; acceptance-rulings record only (text and placement in §2 Q1). Q2: AFFIRM amendment A-R5a-1 with the ratified text in §2 Q2, recorded in `docs/decision_log.md` under the heading given there. No BLOCKER, no MATERIAL. All probes executed; nothing marked NOT EXECUTED.
