# Cold Fable final pass PRR-FINALPASS-01 — ruling on PR-R candidate 8cd9e831

Judge: Claude Fable 5.1, fresh session, worktree `JouleWise-wt-coldgate-152c9255-prr` (HEAD 14ddbcc3, docs branch; the candidate was inspected by `git show`/`git diff` and by `git archive` extracts under `/tmp/coldgate-prr-{a,b,main}`; no tracked file other than this one was written). Machine clock at start 09:48:38 PDT 2026-09-25; at writing 09:58 PDT. Foreground only; no subagents, no background tasks, no sudo/launchctl/powermetrics; the canonical root, night-custody and LaunchAgents were not touched.

**Disclosure of auto-loaded context.** The harness injected `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, and the auto-memory index `MEMORY.md` (truncated) before I acted. None was requested; none is used as evidence here. I read no RUN_STATE, TASK_QUEUE, council log, run report or process trace outside the packet directory except the one file the charge lists (§5 of the acc2 addendum ruling, read from `origin/main`).

## 0. Trust anchors (recorded before the merits)

| Item | Expected | Observed | Method |
|---|---|---|---|
| Charter, deliberate-typo run | `…5d82` | `…5d81` | `scripts/validate_gate_packet.py` → `result: REFUSE`, `reason: charter_trusted_observed_mismatch`, rc=2 |
| Charter, correct run | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | same | validator `result: PASS`, rc=0; independently `shasum -a 256 docs/process/coldgate_charter.md` = same |
| Packet `00-charge.md` | `e45e9df3b62bfec124d96ff6f2faf4083a6d4f0e8cea37ced13618777baa4308` | same | validator + `shasum -a 256` |
| Exhibits ex-01 / ex-02 / ex-05 | manifest values | all three `observed == expected` | validator receipt, `exhibit_manifest_sha256 b74a564b…` |

Merge base of the candidate is `origin/main` = `95521871` (charge's "merge of main 95521871" confirmed). Candidate = `3c52518d` (WIP) + `62db28b7` (fix round 1) + merge commit `8cd9e831`.

## 1. Probes I executed (all on the candidate extract unless stated)

| # | Probe | Result |
|---|---|---|
| P1 | `git diff --quiet origin/main 8cd9e831 -- joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/adapters/powermetrics.py joulewise/reduce.py scripts/night_chains/calibration_derivation_only.zsh` | rc=0 (byte-identical); also rc=0 vs `c034a56f` |
| P2 | r7 validation, own script on `origin/main` extract vs candidate extract: `load_calibration_acceptance_bound()` → `_valid_acceptance_bound` | True on both; canonical-JSON sha256 prefix `efe3145bd32b512e` on both; os_build swapped to 25G83 → False on both; all 7 registered rows complete on both |
| P3 | Quick modules `test_calibration_bracketing test_acc_25g83_rev5 test_preregistration_chain_digest test_calibration_cadence_report test_reissue_calibration_acceptance` | Ran 120 tests in 14.5 s, OK (skipped=1: `test_production_path_authenticates_real_76_receipt_import_prefix`, "lead-reviewed D-079 import inputs are unavailable" — environmental, pre-existing) |
| P4 | `tests.test_issue_calibration_acceptance_generation` | Ran 114 tests in 62.3 s, OK, 0 skipped (the charge's 10-minute estimate was pessimistic) |
| P5 | Seal probe: second extract, the four placeholders replaced by 40/64-hex literals in the live file (line 608; placeholder line count 1 → 0), then `test_acc_25g83_rev5 test_preregistration_chain_digest` | Ran 17 tests, OK — the seal-robust fixtures survive a real seal (ex-01 S2 closed) |
| P6 | `python3 scripts/sim_acc_25g83_rev5.py --trials 200` (seed 25098312, 5 s) | Reproduces `docs/calibration/acc_25g83_rev5_simulation.md` exactly: W1 futility 1/1/0/1; W3 0; excursion-limited 0/118/0/0; zero headroom 196/72/195/0; later level refusal 10/9/6/22; bracket pass 189/190/194/177; floor/interval/false-admission 0 in every cell; upper bound 1.4867 % |
| P7 | Forbidden salvage symbols `PROTOCOL_V3_ID`, `R8_ACCEPTANCE_ID`, `_registered_protocol_pin_matches`, `protocol_v4` in the candidate tree | none |
| P8 | `## D-126-disposition-25G83-v3-2026-09-25 …` heading count in candidate `docs/decision_log.md` | exactly 1 (line 12176) |
| P9 | Cited ruling file exists on `origin/main` | yes (`git cat-file -e`) |
| P10 | PR #412 (PR-L) state; `git merge-tree --write-tree 8cd9e831 99495ba9` | OPEN, unmerged; trial merge clean, no conflicting paths |
| P11 | R16-a text location: `git grep -l "R16-a"` on `origin/main` and the candidate | absent from both; present at worktree HEAD only inside `docs/process_traces/…/24-finalpass-packet-prl/*` and the activation record (not read) |
| P12 | What the rendered launchd plists embed (`origin/main` `night_agent_install.py:608-630`, templates) | `@@PLAN@@`, `@@CUSTODY_ROOT@@`, `@@MONTH@@ @@DAY@@ @@HOUR@@ @@MINUTE@@`, `@@PROBE_DIR@@`, `@@RECEIPT@@` — all per-window values |

## 2. Rulings

### R1 — AFFIRM (implements R4, R5, R9, R10, R17; pinned files and r7 unchanged)

- **R4** (a) entry heading `## D-126-disposition-25G83-v3-2026-09-25 — D-126 disposition, epoch 25G83 v3, 2026-09-25`, eleven rows, mechanism verbatim (`decision_log.md:12176-12197`). (b) registry with `{content_id, disposing_decision_id, mechanism}` rows, 11 entries. (c) A-7 exclusion `and observation.content_id not in dispositions` (issuer diff hunk at `:1352-1381`); registry read only when `revision_five`. (d) `disposing_decision_ids` in the prior set, plus refusal `registered dispositions absent from the successor prior set` (`:1519-1531`). (e) `test_issuer_refuses_unsealed_launch_context_and_disposes_exact_ids` covers empty registry → refuse, present → issue, prior set ⊇ 11 ids, bracketing → `fresh`. I did not recompute the eleven content ids from `/Users/edr/night-archive` (ex-01 and ex-02 each did, independently, with matching results; that is two independent primary-evidence checks and I accept them).
- **R5** see R2.
- **R9** predicate is `target_epoch == REVISION_FIVE_EPOCH` (dict equality on six fields incl. `PROTOCOL_ID`, `calibration_bracketing.py:280-287`); text test `"# Revision 5 ("` (`:1281`); W1 futility `< 6` (`:1326`); W3 refusal when W1+W2 ≥ 12 (`:1355-1362`); no forbidden symbols (P7); pinned files unchanged (P1); addenda carry "for epoch 25G83/v3 under registration Revision 5" and cite the ruling (`decision_log.md:12199-12205`). Salvaged set limited to stale-number audit, dry-run `valid=`, `_derivation_frame_cadence`, zero-headroom arithmetic. Bracketing validator accepts `screen <= drift` and `drift == max(pred, Q99, screen)` only under `registration_revision: 5` on the exact epoch.
- **R10** four models, W1→futility→W2→count-only W3, all members retained, no equivalence branch; finite bound stated; replay reproduced (P6).
- **R17** `scripts/calibration_cadence_report.py` imports only `argparse json pathlib plistlib statistics typing`; per-capture median, window median/max, strict `> 150 ms` on the median of capture medians; first record dropped; chain `.zsh` unchanged (P1).
- **r7 unchanged**: P2.

### R2 — AFFIRM with one text correction carried into the fix round

All elements present at `preregistration_d079_epoch_25g83_rev1.md:600-647`: header (a)–(o) each located; (l) reads "strict S < C" where the ruling's list says "strict S ≥ C" — the ruling's wording is a typo (the relation being dropped is D-125's strict screen-below-ceiling, which is S < C; the D-126 addendum says the same), the PR's text is correct and stays. The Authority line cites the ruling file, which exists on main (P9). One defect: line 618 still names the bare `D-126` (ex-05 NIT-3, open in the candidate) — exact text in F2.

### R3 — REFUSE (packet defect), with the decision rule the cure must be judged by

The exact words of R16-a are not in the packet, not on `origin/main`, and not in the candidate (P11); they exist only in a PR-L process-trace ruling the charge does not list. The charter forbids me to go looking and forbids ruling on the charge's paraphrase ("the T0-rehearsal exemption"). Minimum cure: add an exhibit `ex-06-r16a-text.md` containing the verbatim R16-a text with source path, commit or sha256, exact line range, and ≥ 5 lines of contiguous context on each side; then re-present R3 alone. The rule the re-rule will apply, stated now so the magistrate can pre-check it: R16-a must appear in Revision 5 **if and only if** its text (i) permits any W1/W2/W3 capture to be armed or retained outside the Revision 5 operating condition, or (ii) changes the custody root or evidence path of any member capture, or (iii) alters any element (a)–(o). If none of (i)–(iii) holds it belongs only to the acceptance-rulings record, because Revision 5 already omits R6, R16 and every other installer/gate mechanism by design (R5 fixes science, R15 fixes machinery order). On the charge's own description a T0-rehearsal exemption to the R16 custody-root refusal touches none of (i)–(iii), so the expected outcome is "not in Revision 5" — but that is expectation, not a ruling, until the text is before a judge.

### R4 — REJECT the seal step as written; AFFIRM the issuer refusal

Issuer refusal: AFFIRMED. `_prepare_candidate` refuses `unsealed placeholders` on `<PR-L-MERGE-SHA>|<RENDERED-PLIST-SHA256:[^>]+>` and `pins are malformed` unless `template at commit [0-9a-f]{40}` and `rendered-plist digests hex, hex, and hex` both match (`issuer:1283-1289`); the check sits inside the `revision_five` branch only, so historical epochs are unaffected (P4 passes with the historical pre-Revision-5 text). P5 proves the tests survive a real seal.

Seal step: NOT EXECUTABLE as a one-time seal. The text pins "rendered-plist digests" for night, dead-man and probe. On main the rendered plists embed the plan path, the custody root, the probe receipt path and the launch calendar (`@@PLAN@@ @@CUSTODY_ROOT@@ @@MONTH@@ @@DAY@@ @@HOUR@@ @@MINUTE@@ @@PROBE_DIR@@ @@RECEIPT@@`, P12), and PR-L computes `rendered_plist_sha256` from exactly those rendered bytes at install (`Prepared.launch_context`). Every window renders different bytes, so three digests sealed before W1 cannot describe W2 or W3, and re-sealing per window violates "rules fixed here before capture" and the arm-digest pin. The ruling is internally inconsistent on this point: R5(a) says "rendered-plist digests <values>", R15 says "seal Revision 5, `protocol_v3.json` and **template** digests into the arm notice". Template digests are campaign-constant once PR-L merges and satisfy the reason given for the pin ("launch context sets the sampler cadence" — the template carries `ProcessType`). No consumer cross-checks the sealed digests (the issuer checks form only; PR-L checks rendered digests against its own receipt), so this is a provenance-text defect, not a science bypass; the physical condition is enforced per arm by PR-L's `ProcessType == Interactive` refusal. Rule requested and exact texts in F1.

### R5 — EXECUTED, all six modules pass

P3 + P4: 234 tests, OK, 1 environmental skip. Seal-probe run P5 additionally OK.

### R6 — FIX-FIRST

MERGE after: (1) PR #412 merged first (charge order; trial merge is clean, P10); (2) the F1–F3 texts below landed in one fix commit on the branch and re-audited by one lens against these exact texts (a further cold gate is not required for this delta if the texts are applied verbatim; the R5(a) amendment itself is a ruled-text change and is a charter §3(4) trigger — record it as a dated addendum to the acceptance-rulings record and convene the amendment ratification on that addendum, which may be bundled with the R3 re-rule); (3) R3 re-presented with ex-06 before the seal, not before the merge.

## 3. Findings

**BLOCKER:** none.

**F1 — MATERIAL — new rule requested: amendment A-R5a-1 (R5(a) operating-condition pin = template digests).**
Addendum text for the acceptance-rulings record (magistrate writes, dated): "A-R5a-1 (2026-09-25, PR-R cold final pass): R5(a)'s pinned operating condition names the PR-L merge commit and the sha256 of the two launchd templates at that commit. Rendered-plist digests embed per-window paths and the launch calendar and are recorded per window in the arm evidence and probe receipt under R2; they are not part of the registration text. R15's 'template digests' wording governs."
Revision 5 line 608, replace the sentence beginning "The pinned operating condition is" through "…<RENDERED-PLIST-SHA256:probe>." with: `The pinned operating condition is captures launched by a launchd agent with ` `` `ProcessType=Interactive` ``, `template at commit <PR-L-MERGE-SHA>, template digests <TEMPLATE-SHA256:night> and <TEMPLATE-SHA256:probe>. The first digest is the sha256 of configs/launchd/com.joulewise.night.plist.template (shared by the night and dead-man labels) and the second of configs/launchd/com.joulewise.night-probe.plist.template, both read at that commit. Each window's rendered-plist digests are plan-specific and are recorded in that window's arm evidence and probe receipt by the installer; they are not part of this text.`
Replace the following sentence "Sealing replaces these literals … without backticks." with: `Sealing replaces these three literals after PR #412 merges and before W1's arm notice: the commit is the merge commit of PR #412 on main; each digest is ` `` `git show <that commit>:<template path> | shasum -a 256` ``. `The placeholder count (` `` `grep -c -E '<PR-L-MERGE-SHA>|<TEMPLATE-SHA256:' `` `on this file) must be 0 before the arm-notice digest is taken; seal the literal tokens without backticks; at the seal, replace the header parenthetical "sealing pending PR-L pins" with "sealed <YYYY-MM-DD> at PR-L merge <first 8 hex of the commit>".`
Issuer `scripts/issue_calibration_acceptance_generation.py:1283-1289`: placeholder regex → `r"<PR-L-MERGE-SHA>|<TEMPLATE-SHA256:[^>]+>"`; malformed check → `re.search(r"template at commit [0-9a-f]{40}\b", text)` and `re.search(r"template digests [0-9a-f]{64} and [0-9a-f]{64}\b", text)`; messages unchanged.
`tests/test_acc_25g83_rev5.py`: `LAUNCH_CONDITION = re.compile(r"template at commit \S+, template digests \S+ and \S+\.")`; `registration_with_launch_pins(commit, night, probe)` builds `f"template at commit {commit}, template digests {night} and {probe}."`; `sealed_registration()` → `("a"*40, "b"*64, "c"*64)`; the unsealed fixture uses `("<PR-L-MERGE-SHA>", "<TEMPLATE-SHA256:night>", "<TEMPLATE-SHA256:probe>")`; the malformed fixture `("not-a-commit", "b"*64, "c"*64)`. Add one assertion in `test_issuer_refuses_unsealed_launch_context_and_disposes_exact_ids`: a fixture whose digest sentence reads `rendered-plist digests …` (the superseded form) is refused with `pins are malformed`.
Decision-log disposition entry and `docs/calibration/acc_25g83_rev5_simulation.md`: no change.

**F2 — NIT (fix in the same commit; the text is digest-pinned at arm).** `preregistration_d079_epoch_25g83_rev1.md:618`: replace `disposed as diagnostics under D-126,` with `` disposed as diagnostics under `D-126-disposition-25G83-v3-2026-09-25`, ``. (ex-05 NIT-3, open in the candidate.)

**F3 — NIT.** `tests/test_issue_calibration_acceptance_generation.py:344-347`: delete the dead `probe = subprocess.run([...kern.osversion...])` statement so the hunk equals `c034a56f` (ex-05 NIT-1, open in the candidate). Optionally (ex-05 NIT-2) add to `test_registry_rejects_unruled_or_duplicate_dispositions` a case `row["disposing_decision_id"] = "D-126"` asserting `invalid or duplicate`.

**F4 — NIT, packet hygiene.** (i) The charge's ex-05 summary "all closed" omits ex-05's three new NITs; two of them are open in the candidate (F2, F3). (ii) The charge states assembly at 09:52 PDT while the packet digest already validated on this machine at 09:48:38; the time pin is wrong by ≥ 4 min or the clocks differ. Neither affects the merits.

**F5 — NIT, observation (no action).** No consumer cross-checks the sealed launch-context pins against arm evidence; the issuer's epoch predicate is the ruled six-field tuple and the physical condition is enforced by PR-L at every install. If a future rule wants the registration's operating condition to be machine-checked at issuance, it would compare each member's arm-evidence `launch_context` digests with that window's probe receipt, not with the registration text.

## 4. Disposition

FIX-FIRST. Apply F1 (with the A-R5a-1 addendum recorded and ratified), F2, F3 verbatim; merge PR #412 first; one-lens delta re-audit against these texts; then MERGE PR-R. R3 is REFUSED pending exhibit ex-06 and must be re-ruled before the seal. Everything the charge asked for in R1, R2, R5 is affirmed on primary evidence; the four pinned files and r7's validation are unchanged; the disposition and the simulation are exactly as ruled and reproduced.
