# ROW L7-SEAM-READER-B-EXECUTION — Seam Reader B / execution-derived producer→consumer graph (GATING)
Original verdict: NOT-READY (0 blockers / 2 should-fix / 1 nit / coverage 21/25)
**UNVERIFIED on coverage** — the denominator (25 universe items) was self-nominated by the seat;
`council-verdict.md:18-22` rules every seat's universe self-nominated and orders independent
re-enumeration + the adversarial coverage attack as a standing packet element. L7 is additionally
one of the three seats named in Phase 3's minimum re-audit set (`council-verdict.md:102-104`).

Assembly base: read-only worktree `…/scratchpad/wtS0`, branch `impl/r2-s0-mint-resolver` @ `79a4cd0`
(the brief names `d10881b`; that is HEAD~1's parent — the branch tip is two commits later).
`main` == `origin/main` == `0099382`; merge-base = `311d8016`. Every sha below checked with
`git merge-base --is-ancestor <sha> main`.

**Standing branch fact for the seat:** `git diff --stat 311d8016..main` = 4 prose files only. **No
code has landed on main since the merge-base.** Every code repair cited is either pre-fork (on main)
or branch-only.

---

## L7-SF1 — Frozen PACK-namespace evidence consumed without its monotonic horizon being checked

### (a) Original finding (VERBATIM)
> - [should_fix] [L7] Frozen PACK-namespace evidence is consumed at arm/verify/consume without its declared monotonic horizon being checked — and all 33 frozen receipts' horizons have ALREADY lapsed

Citation: `docs/process_traces/2026-08-15-readiness-council/sitting-packet-FINAL.md:145`; seat report
`…/seat-reports/L7-SEAM-READER-B-EXECUTION-report.md`. Sibling filings of the same seam:
**L6-N3** (`sitting-packet-FINAL.md:125`, filed as a nit) and **L1-B1**
(`sitting-packet-FINAL.md:48-51`, filed as a blocker) — three seats, three severities.
Refuter verdicts: `…/refuter-outputs/refuter-verdicts.md` §"A-contract" ("L1-B1 expiry: CONFIRMED.
Remedy corrected: in-place re-author NOT contract-valid (D-131 requires successor pack+custody root).
… 24h horizon is implementation policy, not D-134/D-137 contract text") and §"A-execution" F1
("CONFIRMED executed: 33/33 generic receipts refuse readiness_record_expired via
`_authenticate_generic_evidence_item` at live monotonic").
Post-verdict adjudication: routed to Phase 0 **R1** and Phase 2 re-freeze
(`council-verdict.md:74-75`, `:97-99`). Work-order text
`…/triage.json:347` (WO-L7-1) framed it as a two-option choice and marks it **"needs magistrate
ruling"**.

### (b) What changed since 2026-08-15

**The mechanism: NO-REPAIR-FOUND.** At HEAD in `joulewise/arm_readiness.py`:
- The horizon check sits in `_authenticate_generic_evidence_item` (def `:4163`) behind an **optional**
  `now_monotonic_ns: int | None = None` (`:4171`); refusal at `:4271-4278`.
- `_load_freeze_reference` (def `:5151`) calls it at `:5253-5262` with only
  `expected_boot_session_id` / `expected_head_commit` / `lifecycle_registry` — **no `now_monotonic_ns`**;
  the function does not accept a clock parameter.
- `_freeze_evidence_for_arm` (def `:5360`) calls it at `:5385-5392` — same, no clock parameter.
- The R1 lifecycle branch inside `_authenticate_generic_evidence_item` (`:4319-4373`) is gated on
  `receipt["schema_version"] != EVIDENCE_RECEIPT_SCHEMA` (`:58`). The frozen receipts **are**
  `joulewise.arm_readiness_evidence_receipt.v1` == `EVIDENCE_RECEIPT_SCHEMA`, so that branch — and
  `validate_r1_class_lifecycle`'s horizon test at `:3378-3387` — is skipped for exactly them.
- Per stage: **arm** `generate_arm_receipt` (`:6096`) → `_load_freeze_reference` (`:6109`),
  `_discover_evidence(..., include_pack=False)` (`:6130-6141`), `_freeze_evidence_for_arm` (`:6139`) →
  **NO**. **verify** `verify_arm_receipt` (`:6587`) → `_verify_arm_receipt` (`:6481`) →
  `_derive_arm_semantics_for_verification` (`:6280`, called `:6559`) → same two helpers → **NO**.
  **consume** `_consume_launch_capability` (`:7297`) → `_verify_arm_receipt` (`:7372`); and
  `_replay_consumed_arm` (`:7060`) → `_derive_arm_semantics_for_verification` (`:7158`) → **NO**.
- The only defense remains the downstream min-fold: `generate_arm_receipt` folds evidence expirations
  into the arm receipt at `:6230-6242` (written `:6252`), and `_verify_arm_receipt` refuses on it at
  `:6495-6501`. Frozen rows can still evaluate PASS from horizon-lapsed bytes; the arm capability
  dies of the min-fold, not of the row check.
- Commit history: `git log --oneline 8937dec..HEAD -- joulewise/arm_readiness.py` = 18 commits; only
  `8fd29f7` "R1 freeze-evidence lifecycle (Phase-2 prep)" (**main**) and `9e71279` "Fix round 1"
  (**main**) touched horizon logic, adding `validate_r1_class_lifecycle` / `validate_r1_temporal_budget`
  and the `now_monotonic_ns` plumbing into `_discover_evidence`. Occurrence count of `now_monotonic_ns`
  went 9 (`8937dec`) → 16 (`8fd29f7`) → 19 (`9e71279`) and has been **19 ever since**, through all
  four branch-only commits (`f4d5ea7`, `bb81323`, `b7e5730`, `3038eeb`).
  `git diff 311d8016..HEAD -- joulewise/arm_readiness.py` is a single 16-line hunk inside
  `_issued_d079` (~`:4134`) adding D-079 r3/r4/r5/r6 ids; grep of that diff for `monotonic` → nothing.

**D-137 — what it actually mandates (read at source).** Index row `docs/decision_log.md:162`; body
`:8766-8790`, operative clause `:8768-8776`: every v1 receipt carrying `valid_until_monotonic_ns`
also carries a derived `boot_session_id`, and "verification and atomic consumption compare the
receipt's boot session with the current boot session; a mismatch refuses closed as
`readiness_record_expired`. The monotonic expiry is therefore never interpreted across a reboot."
**D-137 mandates boot-session comparison — never a compare of `valid_until_monotonic_ns` against
*now* on the frozen-evidence path.** That asymmetry is the seam, and it survives at HEAD.
Amendments: `:9453-9480` (D-134/D-137 launcher-binding amendment, 2026-08-15) and `:9290-9295`
("**D-137 is AMENDED, with zero reach over content receipts**") — both boot-session only.

**The freeze-lifecycle ruling.** `docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/coldgate-adjudicator-ruling.md`
is the closest disposition. `:12` names the gate question as replacing "the 24h-monotonic-horizon
implementation policy that expired all 33 frozen generic receipts"; `:28` "The 24h `valid_until` is
stamped uniformly at authoring (`now + _EVIDENCE_VALIDITY_NS`, ~line 1646) with no per-kind reasoning
— blanket implementation policy"; `:36` confirms the seam in code verbatim ("At the freeze-verify
call site … `_authenticate_generic_evidence_item` is invoked with only `expected_boot_session_id`");
amendment 7 (`:71`) "**Validator-before-consumption ordering.** The horizon may not be removed in any
commit that does not also land the fresh dependency-comparison validator and its cl.10 test
obligations." Magistrate synthesis at `docs/decision_log.md:9196-9243` adopts it with the composed
amendment set. **Its cure is the new content schema, not a threaded clock** — and that schema is not
in production (below). WO-L7-1's "needs magistrate ruling" between the two options is **still
unruled**: no selection found in `docs/decision_log.md`, the freeze-lifecycle consult, or the 16
files under `docs/process_traces/2026-08-19-r1-r2-codesign/`.
**Not the same R1:** D-146 (`docs/decision_log.md:8844-8848`, ONE home
`…/2026-08-19-r1-r2-codesign/13-r1-ruling.md`) is the *capture-pipeline v3* ruling; grep of that file
for `horizon|valid_until|TIME_BOUND|monotonic` → **zero hits**.

**The empirical half: CURED, by data, branch-only, and with a clock on it.**
- Re-freeze commits, all **BRANCH-ONLY**, all authored by Ed R 2026-08-19:
  `3a75a77` "D-147 S4: author D-134 freeze evidence for the three `_v3` packs at the measurement
  checkout (all PASS)" (09:57 −0700); `5e38f1e` / `eb7f6c6` / `94dc3b3` "D-147 S5: freeze-0003 minted
  for d117_floor_qwen25_1p5b_v3 / _7b_v3 / contrast…_v3 (PASS; predecessor `_v2`/freeze-0002 …)"
  (17:28-17:29 −0700); `8b2b021` "S5 COMPLETE: confirmation table filled".
  Custody: `docs/process/ed-s5-mint-decision-2026-08-19.md` (confirmation table, `:78-89`) and
  `docs/process_traces/2026-08-19-refreeze-execution/` (r5-issuance, r6-issuance, reports, s2-goldens,
  s4, suite-logs).
- Read-only probe in this worktree at `time.monotonic_ns() ≈ 2,415,087,816,993,791`:
  `configs/campaigns/d117_*_v3/arm_readiness.evidence/*.json` = **33 files**, all
  `joulewise.arm_readiness_evidence_receipt.v1`, all carrying both `valid_until_monotonic_ns` and
  `boot_session_id`; `valid_until` = 2,468,742,407,178,458 (1p5b_v3) / 2,468,774,933,440,083 (7b_v3) /
  2,468,792,444,508,708 (contrast_v3) — **all 33 LIVE, ~15 hours remaining, lapsing ≈2026-08-20
  17:28 PST**. The 66 `_v1`/`_v2` receipts remain lapsed.
- Boot binding: every receipt carries `boot_session_id = da90818c-9c31-45d0-8813-deae65fba143`, which
  is still the machine's current boot session — no reboot has occurred since 2026-08-13.
  `docs/process/ed-s5-mint-decision-2026-08-19.md:41-46` states the coupling in operator prose: "the
  S4 evidence EXPIRES ~2026-08-20T16:51:33Z and dies on ANY REBOOT … **DO NOT REBOOT the Mac before
  ruling.**"
- **The 24 h stamp is untouched:** `joulewise/arm_readiness_evidence.py:42`
  `_EVIDENCE_VALIDITY_NS = 86_400 * 1_000_000_000`, applied `:2421`.
- **The ruled content-bound schemas are NOT in production.** `docs/decision_log.md:9264-9270`
  specifies `joulewise.arm_readiness_content_evidence_receipt.v1` (carrying neither
  `boot_session_id` nor `valid_until_monotonic_ns`) and
  `joulewise.arm_readiness_execution_evidence_receipt.v1`. `grep -rn "content_receipt|
  arm_readiness_evidence_content|dependency_divergent" joulewise/*.py` → nothing. Blocker on the
  install: `docs/process/phase2-transaction-runsheet.md:11-15` "step 4 (R1 registry install)
  NEEDS_RULING on Ed-reserved values (five items)";
  `docs/process/ed-s5-mint-decision-2026-08-19.md:90-92` "R1 row-registry reserved values — three of
  five are now supplied".

### (c) Candidate disposition for the seat
**STILL-OPEN on the mechanism / CURED-BY-DATA-WITH-EXPIRY on the empirics.** The seat is adjudicating
a two-part should-fix where the empirical half was cured by a branch-only re-freeze whose receipts
lapse ≈2026-08-20 17:28 PST and die on any reboot, while the mechanical half is byte-for-byte
unchanged and the ruling that would decide *how* to fix it (WO-L7-1's two options) has never been
made. The seat must also reconcile a three-way severity split on one seam (L1 blocker / L7 should-fix
/ L6 nit).

### (d) Skeptical probes
1. **Re-probe the horizons at sitting time.** If the sitting is after ≈2026-08-20 17:28 PST, the
   finding's second clause is true again verbatim and the "repair" evaporated on a timer.
2. `sysctl kern.bootsessionuuid` vs `da90818c-9c31-45d0-8813-deae65fba143`. A reboot voids all 33
   regardless of clock.
3. Execute the seam: call `_load_freeze_reference` against a `_v1` pack (lapsed receipts) and confirm
   it does **not** raise `readiness_record_expired` — proving the check is absent, not merely
   unpassed. Then confirm the min-fold at `:6230-6242` is the only thing that kills the arm receipt.
4. `grep -c now_monotonic_ns joulewise/arm_readiness.py` (expect 19) and read `:5253-5262`,
   `:5385-5392` — the kwarg must still be absent.
5. Demand the WO-L7-1 ruling. Cold amendment 7 forbids removing the horizon without the fresh
   dependency-comparison validator; that validator does not exist
   (`grep -rn "dependency_divergent|dependency manifest" joulewise/`). So neither option is
   currently executable — ask what the actual plan is.
6. Ancestry check: `git merge-base --is-ancestor 5e38f1e main` (expect false ×4). If the `_v3` family
   is branch-only, an arm performed from `main` sees only lapsed `_v1`/`_v2` packs.

---

## L7-SF2 — Mandatory pre-arm sequence is undocumented

### (a) Original finding (VERBATIM)
> - [should_fix] [L7] Mandatory pre-arm sequence is undocumented: the runbook's E-step tool does not exist at the frozen measurement-checkout head, and advancing the checkout stales the recorded §5C dry-run receipt

Citation: `sitting-packet-FINAL.md:146`. Independently filed by L5 as
"Pre-arm sequence unregistered: measurement checkout must advance and the §5C dry-run must be
re-executed at the final head (dry-run-0001 is stale by binding)" (`sitting-packet-FINAL.md:133`), and
carried as ED-QUAL row **ED-L7-2** (`sitting-packet-FINAL.md:188`): "fresh §5C lead dry-run PASS at
the final reviewed head on the measurement checkout … a new PASS receipt binding the final
head/digest is required desk evidence before arm".
Ordered remedy, `…/2026-08-15-readiness-council/triage.json:347` (WO-L7-2, pre-arm, doc + checklist),
verbatim: "add the explicit sequence to RUN_STATE/ed-qualification-session/runbook §5C entry gate:
(1) advance the measurement checkout to the final reviewed merged main (clean, exact match),
(2) verify boot session unchanged (DA90818C...), (3) lead personally re-runs the §5C dry-run at that
head and requires a fresh PASS receipt binding the new head + new pack digest, (4) only then the
E-steps; correct RUN_STATE's 'NO REBOOT preserves the frozen evidence' to name the dry-run staleness
and the #149 pack-byte drift". **None of the four steps was found written into any of those three
documents** (see (ii) below).

### (b) What changed since 2026-08-15

**(i) The E-step tool exists — but not where the runbook points.**
- `scripts/capture_t0_step.py` exists at HEAD and at `/Users/edr/JouleWise-measurement-20260818`.
  It landed with `a61ac92` "WO-T0-PRODUCER … (#152)" — **merged to main** (merge recorded at
  `docs/run_reports/2026-08-15-t8-session.md:153`, 2026-08-16T01:10:33Z).
- **The runbook still pins the OLD checkout.** `docs/phase_2/window_runbook.md:28-31` declares
  `MEASUREMENT_REPO` default `/Users/edr/JouleWise-measurement-20260813`; the literal env block at
  `:189` and `:192-193, 201-202, 204, 815, 1150, 1201` hardcode it with `_v2`-era campaign roots.
  That checkout's HEAD is `49dcc49a…` ("FREEZE 6/6: D-134 freeze receipt — GAMMA PASS…") and
  `ls /Users/edr/JouleWise-measurement-20260813/scripts/capture_t0_step.py` → **No such file**.
  So at the head the operative runbook pins, the tool the same runbook commands at `:913-963` still
  does not exist — the finding's literal condition, unrepaired in the operative document.
- `grep -n "20260818\|_v3\|freeze-0003" docs/phase_2/window_runbook.md` → **zero hits**. The actual
  working checkout `/Users/edr/JouleWise-measurement-20260818` (HEAD `94dc3b34`, i.e. behind this
  worktree by three commits) is named only in `docs/process/rehearsal-operator-card.md:3`,
  `docs/process/ed-morning-packet-2026-08-18.md`, and
  `docs/process/ed-s5-mint-decision-2026-08-19.md` — none of which is the §5C authority.

**(ii) The E-step sequence itself IS now documented; the ordering rule is not.**
- Documented: `docs/phase_2/window_runbook.md:869` ("Ed executes the frozen E-step sequence with no
  reordering"); `:913, 922, 931, 942, 952, 963` the six literal `capture_t0_step.py` invocations;
  `:994-1005` E-9b + the 20-minute volatile horizon; `:1010-1027` "A reboot **or any HEAD change**
  voids the authored receipts … then repeat E-4 through E-9b … **E-9c** is ARM followed by verify".
  `docs/phase_2/window_runbook.md:846-858` (§5C dry-run) already requires the receipt to have
  `status: PASS`, `arm_disposition: NOT_APPLICABLE`, "and the same reviewed HEAD and final
  committed-pack digest that the arm evaluation will bind … **a stale dry-run receipt** … is NO-GO".
  WHERE: these came in with `a61ac92` and the launch-binding series — **main**.
  `docs/process/rehearsal-operator-card.md` (added by `ad14ac4`, **branch-only**) walks the same
  sequence as sections 1-11 with ED-FIRST/BOUNDARY-PROVEN markings; `:95` restates the 20-minute
  horizon.
- **NOT documented — the specific ordering interaction the finding names** (advance the checkout so
  the tool exists → the recorded §5C dry-run receipt is thereby staled → re-run the dry run before
  arm). `grep -n "stale|advanc" docs/phase_2/window_runbook.md` → `:71, 91, 337, 362, 517, 779, 856,
  1238, 1316, 1568, 1573, 1598, 1604, 1619`, none of which states the rule.
  `docs/process/phase2-transaction-runsheet.md` grep for `pre-arm|prearm|dry-run|E-step|checkout` →
  one hit (`:12`, a passing "receipts at the measurement checkout").
  `docs/process/ed-batch-packet.md` and `docs/process/ed-evening-checklist.md` → **zero** hits for
  `pre-arm|prearm|E-step|dry.run|advanc|stale|5C` (the checklist mentions `capture_t0_step.py` once,
  `:18`, as a pointer).

**(iii) No fresh §5C dry-run receipt at the current head.**
- `find` over the repo → zero `dry-run-*.json`. Over `/Users/edr` → exactly one:
  `/Users/edr/JouleWise-window-custody/d117_floor_qwen25_1p5b_v1/arm_readiness.dry_run.receipts/dry-run-0001.json`
  (mtime 2026-08-13 20:04; `issued_at_utc 2026-08-14T03:04:35.752191Z`).
- Its bindings: `receipt_id dry-run-0001`, `status PASS`, `arm_disposition NOT_APPLICABLE`,
  schema `joulewise.arm_readiness_dry_run_receipt.v1`, `pack.pack_id d117_floor_qwen25_1p5b_v1`
  (**the retired v1 family**), `pack_root /Users/edr/JouleWise-measurement-20260813/configs/campaigns/
  d117_floor_qwen25_1p5b_v1`, `pack_sha256 6246b618…`, checks
  `[real_reservation_cli_execute, real_writer_entry_pre, real_writer_entry_post,
  same_head_pack_binding]`.
- The v1 dry-run schema has **no `head_commit` key**; the HEAD binding rides the `command_sha256` of
  `same_head_pack_binding`, which `_latest_dry_run_binding`
  (`joulewise/arm_readiness.py:5881-5931`) recomputes as
  `sha256("reviewed-head\0<head_commit>\0pack\0<pack_sha256>")` and refuses as
  `readiness_dry_run_stale` on mismatch (`:5929`).
- **It matches nothing current**: not head `79a4cd0`, not the `_v3` family, not the `_v3` pack digests.
  It would refuse `readiness_dry_run_stale` at arm. No dry-run receipt exists under
  `/Users/edr/JouleWise-measurement-20260818`.

### (c) Candidate disposition for the seat
**STILL-OPEN, partially documented.** The seat is adjudicating a should-fix where the E-step sequence
gained full runbook prose (main) and a rehearsal card (branch-only), but the three components of the
finding are all still live: the runbook pins a checkout where the tool does not exist, the ordering
rule that the checkout advance stales the dry-run receipt is written nowhere, and the only dry-run
receipt on the machine is a 2026-08-14 `_v1` artifact that fails the staleness binding at the current
head — with ED-L7-2 undischarged.

### (d) Skeptical probes
1. `ls /Users/edr/JouleWise-measurement-20260813/scripts/capture_t0_step.py` — if still absent, the
   finding's first clause reproduces verbatim against the runbook's own `MEASUREMENT_REPO` default.
2. `grep -n "MEASUREMENT_REPO\|20260813\|20260818" docs/phase_2/window_runbook.md` — the night
   document must name the checkout that actually holds the `_v3` packs and the tool. Does it?
3. Recompute the staleness binding by hand:
   `sha256("reviewed-head\0" + head + "\0pack\0" + pack_sha256)` for `dry-run-0001.json` against
   the current head and `_v3` digest, and confirm `_latest_dry_run_binding`
   (`joulewise/arm_readiness.py:5881-5931`) would refuse.
4. Ask who owns ED-L7-2 and when it runs. It requires the real reservation CLI `--execute` and the
   production writer through both slots under lease — an Ed/quiet-machine desk row, and it must bind
   the **final** reviewed head, which does not exist until the branch merges.
5. Note the circularity and put it to the seat: every branch commit re-stales any dry-run receipt, so
   the receipt can only be minted after the tree is frozen for the window. Is that sequencing written
   down anywhere? If not, this is a process gap, not a documentation nit.
6. Cross-check L5's twin finding (`sitting-packet-FINAL.md:133`) — same defect, and L5 is in Phase 3's
   named re-audit minimum. One remedy or two?

---

## L7-N1 — `joulewise reduce` writes its re-reduction artifact into the invoker's CWD

### (a) Original finding (VERBATIM)
> - [nit] [L7] `joulewise reduce` writes its re-reduction artifact into the invoker's CWD by default

Citation: `sitting-packet-FINAL.md:147`. No post-verdict adjudication found.

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** Entry point `joulewise/cli.py`, `_cmd_reduce` def `:1835` (verb documented at
  `:9`; header comment `:1830-1832`). Default output path, `:1885-1903`:
  `if args.output: output_path = Path(args.output)` else … `output_path = cwd / (
  f"{bundle_path.name}.summary_metrics.rereduced.{reducer_version}.json")` at `:1901-1903`.
  **Line 1901 is the finding, unchanged.**
- The guards present protect only against writing *into* the bundle — `:1895-1898` (CWD inside the
  bundle → error 2, "choose an external `--output` for immutable evidence"), `:1911-1917` (output
  inside bundle), `:1918-1924` (stored-summary overwrite), `open("x")` at `:1926`. None relocates the
  default away from the invoker's CWD.
- Commits touching `joulewise/cli.py` since `8937dec`: `3038eeb` (**branch-only**), `b7e5730`
  (**branch-only**), `f16037c` (**main**), `b9c7d0a` (**main**). The reduce-region changes in that
  range are the launch-lineage additions (`authenticate_bundle_launch_lineage` `:1849`,
  `payload["launch_lineage"]` `:1878-1882`); none touched `:1901`.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND.** The seat is adjudicating an unchanged CWD-default nit on a re-reduction path
that has since gained launch-lineage authentication — i.e. the artifact got more provenance-bearing
while its default destination stayed the operator's working directory.

### (d) Skeptical probes
1. `sed -n '1885,1905p' joulewise/cli.py` — confirm `:1901` at the sitting.
2. Does §11 or §12 of the runbook invoke `joulewise reduce` without `--output`? If yes, an operator
   following the runbook literally drops a provenance-bearing artifact wherever they happen to stand.
   `grep -n "joulewise reduce\|_cmd_reduce\|rereduced" docs/phase_2/window_runbook.md`.
3. Now that `payload["launch_lineage"]` rides in the artifact (`:1878-1882`), is a stray CWD copy a
   custody problem rather than an ergonomics nit? Put the re-severitisation question to the seat.

---

## L7-COVERAGE — 21/25, self-nominated denominator

### (a) Original finding (VERBATIM)
Seat table row: `sitting-packet-FINAL.md:29` — `| L7-SEAM-READER-B-EXECUTION | GATING | NOT_READY | 21/25 | 0 | 2 | 1 | 7 | 7 | 3 |`
Seat's own denominator, `…/seat-reports/L7-SEAM-READER-B-EXECUTION-report.md:7`:
> ## 1. Evidence universe (enumerated before findings; 25 items, 21 examined)

with the seat's method statement at `:3`: "obligation graph derived from *actual runs*: tests,
dry-runs, the freeze log, live CLI probes. L6's output not read." Its four unexamined items are the
§6 unexecuted obligations at `sitting-packet-FINAL.md:216-222` (live capture path incl.
`validate_powermetrics_fiducial --allow-live`; the CI-exclusive `test_calibration_exits` /
`test_calibration_writer_crash_matrix` modules; the decisive full-fixture mint proof needing network;
whole-window verdict and `extract_detection_floors` against a real corpus;
`reserve_calibration_window_bracket.py --execute` against the production ledger; `quiet_mac_prep.sh`;
a9/a10 basis excluded to seat 11).

Council ruling on all coverage numbers — `council-verdict.md:18-22`:
> **The work-order program is NOT CERTIFIED COMPLETE** (Opus B4 cure, cold §E concurring): every seat's evidence universe was self-nominated, and the one denominator adversarially tested fell. Closing all listed work orders does not entitle READY; the READY-candidate re-audit must re-enumerate every universe independently and run the adversarial coverage attack as a standing packet element.

Phase 3, `council-verdict.md:102-104`: "baseline-manifest SUPERSESSION (with the ruled fields) +
focused re-audit of pack/custody-bearing seats (**L1, L5, L7 minimum**) + adversarial coverage
re-enumeration of all universes". Reinforced at `docs/council_log.md:3760`.

### (b) What changed since 2026-08-15
- **Yes, L7's universe was self-nominated** — the seat enumerated its own 25 items before findings.
- **Neither the Phase-3 re-audit nor the coverage re-enumeration has run for L7.** The only executed
  re-audit is **WO-L2-REAUDIT** (`docs/process_traces/2026-08-15-l2-reaudit/`, custody `0f886d3`,
  **main**), scoped to L2 (`reaudit-prompt.md:10` carries the adversarial coverage attack for
  calibration acquisition only). Phase 3 is gated behind the baseline-manifest supersession, which has
  not happened: `docs/process/audit-baseline-manifest.json` has exactly one commit ever, `694442c`
  (**main**), untouched in `311d8016..HEAD`, and still carries `runbook_sha256 25a4e809…` against a
  runbook that now hashes `8e1b76e2…` (1,588 → 1,875 lines). `docs/process/phase2-transaction-runsheet.md:106-108`
  still defers the supersession as "its own follow-up"; `RUN_STATE.md:603` still lists it as future.
- **L7's own audit basis has been invalidated by the re-freeze.** The seat's validity argument
  (`…/L7-SEAM-READER-B-EXECUTION-report.md:4`) rests on recomputing all three pack digests
  (`f4c02c8a / 6a8a3bf6 / 1cc0c784`) byte-identical to the manifest "therefore … valid under
  amendment 12". Those are the `_v1` digests; the funded family is now `_v3` with new digests
  (`1e3f1fa3… / 6d0b9b75… / 0d071941…`, `docs/process/ed-s5-mint-decision-2026-08-19.md:86-88`).
- **New universe items exist that L7 never saw:** `scripts/capture_t0_step.py` and its three schemas
  (`:38-40`), `scripts/joulewise-network-time.sudoers`, `scripts/launch_window.py` /
  `verify_consumed_launch` (launch-binding series), the `freeze-000N` chain and
  `--predecessor-pack-root` route, the D-149 GO receipt
  (`docs/process/d149-go-receipt-template.md`, **branch-only**), and the `_v3` pack family.

### (c) Candidate disposition for the seat
**STILL-OPEN.** The seat is adjudicating whether L7 may carry 21/25 into a READY-candidate sitting
when the council named L7 explicitly in Phase 3's minimum re-audit set, that re-audit has not run,
its gate (baseline-manifest supersession) has not been reached, and the seat's own amendment-12
validity argument now rests on pack digests that the freeze-0003 re-freeze rotated.

### (d) Skeptical probes
1. Demand the Phase-3 artifact for L7. If none exists, the coverage line is UNVERIFIED by the
   council's own standing rule, independent of the three findings.
2. Re-enumerate independently at HEAD and diff against the seat's 25 items — the launch-binding
   surface, the T-0 capture tool, `freeze-000N`, and the D-149 GO receipt are all new execution-derived
   nodes.
3. Re-run the seat's own validity check: recompute the three pack digests via
   `joulewise.arm_readiness.committed_pack_tree_sha256` and compare to
   `docs/process/audit-baseline-manifest.json`. A mismatch means L7's results are void under
   amendment 12, not merely thin — the same disposition L2 received.
4. Four of the five unexamined items still require live sudo / a real corpus / network. Ask which of
   the seat's three ED rows (ED-L7-1 prewindow `--wait` to READY, ED-L7-2 fresh §5C dry-run,
   ED-L7-3 live fiducial calibration) have been discharged. None was found discharged in this sweep.
5. Charter amendment 11 treats NOT-READY and UNVERIFIED as distinct verdicts (L2 precedent). Should
   L7 carry an explicit UNVERIFIED-on-coverage label into the sitting the way L2 did?

---

## ROW-LEVEL OPEN ITEMS
- **L7-SF1 mechanism:** NO-REPAIR-FOUND. `_load_freeze_reference` (`joulewise/arm_readiness.py:5253-5262`)
  and `_freeze_evidence_for_arm` (`:5385-5392`) still omit `now_monotonic_ns`; the only defense is the
  downstream min-fold (`:6230-6242` / `:6495-6501`). WO-L7-1's two-option choice
  (`…/2026-08-15-readiness-council/triage.json:347`) is still marked "needs magistrate ruling" and no
  ruling exists.
- **L7-SF1 empirics:** cured only as DATA and only on the branch. The 33 `_v3` receipts lapse
  ≈2026-08-20 17:28 PST and die on any reboot; boot session
  `da90818c-9c31-45d0-8813-deae65fba143`. `5e38f1e`, `eb7f6c6`, `94dc3b3`, `8b2b021`, `3a75a77` are all
  branch-only — an arm from `main` sees only lapsed `_v1`/`_v2` packs.
- **R1 content-bound schemas ruled but not installed.** `joulewise.arm_readiness_content_evidence_receipt.v1`
  / `…_execution_evidence_receipt.v1` (`docs/decision_log.md:9264-9270`) appear nowhere in
  `joulewise/`; the registry install is runsheet step 4, NEEDS_RULING, 3 of 5 Ed-reserved values
  supplied. The fresh dependency-comparison validator that cold amendment 7 makes a precondition for
  removing the horizon does not exist.
- **L7-SF2 runbook pin:** `docs/phase_2/window_runbook.md:28-31,189` still pins
  `/Users/edr/JouleWise-measurement-20260813` (HEAD `49dcc49a`), where `scripts/capture_t0_step.py`
  does not exist; the runbook has zero hits for `20260818`, `_v3`, or `freeze-0003`.
- **L7-SF2 ordering rule:** undocumented in every operator surface checked (runbook, runsheet,
  rehearsal card, ed-batch-packet, ed-evening-checklist). The circular dependency (any commit
  re-stales the dry-run receipt) is written down nowhere.
- **L7-SF2 dry-run receipt:** only `dry-run-0001.json` exists machine-wide (2026-08-14, `_v1` pack,
  `20260813` checkout); it fails `_latest_dry_run_binding` at the current head. **ED-L7-2
  undischarged**, and it cannot be discharged until the tree is frozen for the window.
- **L7-N1:** NO-REPAIR-FOUND; `joulewise/cli.py:1901` still defaults to `Path.cwd()`, now for an
  artifact that carries `launch_lineage`.
- **All three of L7's ED-QUAL rows (ED-L7-1, ED-L7-2, ED-L7-3)** were found undischarged; no
  discharge evidence located in `docs/process/`, `docs/process_traces/2026-08-18-shakedown-first-light/`,
  or `RUN_STATE.md`.
- **Coverage:** self-nominated 25-item universe; no independent re-enumeration or adversarial coverage
  attack for L7 despite L7 being explicitly named in Phase 3's minimum set; the Phase-3 gate
  (baseline-manifest supersession) is unexecuted; and the seat's amendment-12 validity argument rests
  on `_v1` pack digests that the re-freeze rotated.
- **Severity split unresolved across the packet:** the same monotonic-horizon seam is L1-B1 (blocker),
  L7-SF1 (should-fix), and L6-N3 (nit). The sitting should rule one severity.
