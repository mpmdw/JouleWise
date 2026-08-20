# ROW L8-OPERATOR-RECOVERY-HUMAN-FACTORS — Operator + recovery human factors (GATING)
Original verdict: NOT-READY (7 blockers / 5 should-fix / 3 nits / coverage 21/24)
Seat's own work orders at the sitting: WO-L8-1 … WO-L8-8 (`seat-reports/L8-OPERATOR-RECOVERY-HUMAN-FACTORS-report.md:141`).
Sitting-packet row: `sitting-packet-FINAL.md:33` — `| L8-OPERATOR-RECOVERY-HUMAN-FACTORS | GATING | NOT_READY | 21/24 | 7 | 5 | 3 | 8 | 6 | 4 |`; seat hash `80cd36a6d19f95f4` (`:18`).

**ASSEMBLER NOTE ON THE READING TREE (material to every citation below).**
The brief states the worktree is at `d10881b`. Verified: the worktree
`.../scratchpad/wtS0` is on `impl/r2-s0-mint-resolver` at **`79a4cd0`**
("D-149 GO-receipt template + evidence runbook"); `d10881b` is `HEAD~1`.
`main == origin/main == 0099382`. `git rev-list --left-right --count main...HEAD`
= **10 / 51** — i.e. HEAD is 51 ahead of merge-base `311d8016` and is
**missing 10 commits that are on main** (all doc/guide syncs; `git log --oneline main ^HEAD`).
For the L8 surface specifically I diffed `main` against `HEAD` over
`docs/phase_2/window_runbook.md`, `scripts/capture_t0_step.py`,
`scripts/prewindow_check.sh`, `joulewise/arm_readiness_evidence_t0.py`,
`scripts/launch_window.py`, `scripts/generate_arm_readiness.py`,
`docs/process/rehearsal-operator-card.md`, `joulewise/arm_readiness.py`:
only the runbook (18 lines) and `arm_readiness.py` (14 lines) differ, and the
runbook delta is **entirely** the D-079 fiducial constants
(`0.033558756679900` → `0.032898493715362`, `0.010818 s` → `0.009724 s`,
acceptance artifact `…v2_n19` → `…v2_n17_r3`) — branch-only, and untouched by
any L8 finding. **Every runbook §4/§5C/§6 and tool citation in this row reads
identically on `main`.**

---

## L8-B1 — No shipped producer for the T-0 input files the evidence author requires

### (a) Original finding (VERBATIM)
> ### L8-OPERATOR-RECOVERY-HUMAN-FACTORS B1: No shipped producer for the T-0 input files the evidence author requires
> at: joulewise/arm_readiness_evidence_t0.py:448-499,595-724 vs docs/phase_2/window_runbook.md:802-838
> scenario: Ed completes E-4…E-9 exactly as the runbook/packet write them, runs the T-0 author, and gets REFUSE evidence_author_t0_clock_attestation_missing (executed): the author consumes nine byte-canonical JSON inputs (six command captures with monotonic timestamps + clock-attestation + arm-context + launch-manifest) that no tool, no runbook step, and no packet step produces; the only 2am path forward is hand-fabricating canonical JSON with invented monotonic_ns values, which the receipts cannot distinguish from honest capture
> REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

Citation: `sitting-packet-FINAL.md:84-87` §3 heading "L8-OPERATOR-RECOVERY-HUMAN-FACTORS B1"; seat report `seat-reports/L8-OPERATOR-RECOVERY-HUMAN-FACTORS-report.md:100`; refuter verdicts — B-contract "All six CONFIRMED; none refuted", with the correction "F1+F2 MERGE into ONE work order: shipped T-0 acquisition/capture tool … Nine filenames are implementation preconditions, not D-134 names" (`sitting-packet-FINAL.md:425-429`); B-execution `refuter-outputs/sol-refuter-B-execution.md`.
Post-verdict adjudication: none — CONFIRMED; folded into WO-T0-PRODUCER (`council-verdict.md:81-83`; cold ruling `cold-fable-ruling.md:88`).

### (b) What changed since 2026-08-15
- **`a61ac92`** "WO-T0-PRODUCER: T-0 acquisition capture tool + R2 resolver + D-127 clock route + dwell/env hardening (#152)" — **merged to main** (`git merge-base --is-ancestor a61ac92 main` → yes; also on HEAD). PR-branch head `9e8936a` ("Merge main into wo-t0-producer") is **NOT** on main and **NOT** on HEAD — it is the pre-squash branch tip only. TASK_QUEUE cites `9e8936a` as the "D-121-verified head" (`TASK_QUEUE.md:106`).
- Ships **`scripts/capture_t0_step.py`** (1060 lines at HEAD; created by `a61ac92`, later touched by `65cc0f3`, `d8d2022`, `32cf987` — all on main).
- It produces the nine inputs into `<custody>/<pack>/arm_readiness.t0.inputs/` (`scripts/capture_t0_step.py:41`):
  - **six command captures** — `STEP_FILENAMES` at `:59-66`: `clock-prior-state.json`, `clock-disable.json`, `quiet-mac-prep.json`, `prewindow-check.json`, `ledger-readiness.json`, `ledger-reservation.json`; argv derived, not typed, by `_command_for_step` (`:602-677`);
  - **`clock-attestation.json`** — `_clock_attestation` (`:536-599`);
  - **`arm-context.json`** and **`launch-manifest.json`** — `_prepare_derived_inputs` (`:516-533`).
- Runbook §5C now names the tool at every E-step (E-4 … E-9a) and states the post-condition: *"After E-9a, the private input namespace contains exactly the six captures plus `clock-attestation.json`, `arm-context.json`, and `launch-manifest.json`"* (`docs/phase_2/window_runbook.md:969-971`) — **on main**.
- Publication is fail-closed and no-clobber: `_write_no_clobber` (`:180-224`) never replaces an existing path; twelve registered refusal codes (`CAPTURE_REASON_CODES`, `:85-100`); `_require_sequence` (`:680-739`) re-validates every predecessor capture byte-canonically and refuses out-of-order, recapture, and future-capture-exists.
- **The forgery half of the finding was NOT closed — it was superseded by an honest-contract rewrite.** `65cc0f3` "T-0 F4 honest contract: D-134 cl.6 overclaim superseded (production-interface/ceremony rule, no operator-fabrication-resistance claim), TRUSTED-OPERATOR limitation v1 registered, public execute/monotonic_ns/utc_now injection seam removed from capture_t0_step (module-private test hook)" — **merged to main via PR #154 (`a59c795`)**. Module docstring now reads: *"The production CLI is a trusted-operator ceremony interface, not independent producer attestation. … v1 does not defend against deliberate operator fabrication."* (`scripts/capture_t0_step.py:2-11`). Runbook §5C's handback attestation says the same: *"This is the human record of the trusted-operator ceremony, not mechanically independent producer attestation."* (`window_runbook.md:984-986`).
- **What "the F4 honest-contract deltas ride the follow-up t0-producer lane per the 2026-08-15 provenance ruling" (`TASK_QUEUE.md:106`) deferred, and what became of it:** the deferral was recorded at `RUN_STATE.md:524-526` ("T-0 F4 honest-contract deltas … into a follow-up on the t0-producer lane after #152 merges") and the ruling is custodied at `7b31213` "F4 T-0 capture provenance: honest-contract fix mandated (correct overclaim + remove injection seam); **trusted-operator scope + option-(a) attested architecture DEFERRED to Ed/advisor (paper-scope)**" (on main). The *deltas* landed (#154). What remains deferred is the **architecture**: option-(a) independent attested production, deferred to Ed/advisor as paper scope. `TASK_QUEUE.md:106` is therefore **stale prose** — it still reads as though the deltas are pending.

### (c) Candidate disposition for the seat
**READY-EVIDENCE-ATTACHED (mechanism) + SUPERSEDED-BY-RULING (fabrication half).** The seat is adjudicating whether a shipped, sequence-enforcing, no-clobber nine-input producer merged to main discharges B1's *"no tool produces them"* limb, and separately whether the trusted-operator honest contract (D-134 cl.6 superseded; TRUSTED-OPERATOR limitation v1 registered) is an acceptable disposition of B1's *"receipts cannot distinguish forgery from honest capture"* limb — given that the alternative architecture is deferred to Ed/advisor and that **no end-to-end execution of this tool has ever occurred** (see L8-ED-Q-L8-2 below).

### (d) Skeptical probes
1. Run the nine-input production once end-to-end against scratch roots and count the files: `ls <custody>/<pack>/arm_readiness.t0.inputs/` must contain exactly nine. **No one has ever done this** — the dress rehearsal was never executed. What is the evidence the tool works on a real pack, as opposed to in `tests/test_capture_t0_step.py`?
2. `tests/test_capture_t0_step.py:72` is the only site calling `readiness.resolve_frozen_plan` in that suite. The cold ruling made a **real-pack** regression test *mandatory* (`cold-fable-ruling.md:88`). Ask: which test exercises a *committed* `configs/campaigns/d117_*` pack rather than a synthetic fixture? If none, the C-028 condition on this WO is unmet.
3. `_write_no_clobber(arm_path, …, accept_identical=True)` (`:527-529`) vs `_write_no_clobber(clock_path, …, accept_identical=False)` (`:598`). Probe the asymmetry: can a stale `arm-context.json` from an abandoned earlier attempt be silently reused because it is byte-identical, while the machine state it describes has changed?
4. TRUSTED-OPERATOR limitation v1 — find its registration text and ask whether it is limited to the *tool* or also disclaims the **handback attestation** at `window_runbook.md:975-983`, which is the only remaining anti-forgery instrument.
5. `TASK_QUEUE.md:106` says the F4 deltas "ride the follow-up lane"; #154 merged them on 2026-08-16. Is any other queue/kernel row still carrying the closed deferral as open?

---

## L8-B2 — The frozen E-7b command cannot prove the ≥10-minute idle the author enforces

### (a) Original finding (VERBATIM)
> ### L8-OPERATOR-RECOVERY-HUMAN-FACTORS B2: The frozen E-7b command cannot prove the ≥10-minute idle the author enforces
> at: scripts/prewindow_check.sh:36-37,177-198 vs joulewise/arm_readiness_evidence_t0.py:49,954-957 vs runbook:366-373,780-789
> scenario: On a well-prepared (clean) machine, `prewindow_check.sh --wait` exits READY after 3 checks × 30 s ≈ 61 s (per-check cost measured at 0.156 s); the T-0 author refuses any prewindow capture shorter than 600 s, so the better Ed prepares the machine the more certainly authoring refuses — and if the author did not enforce it, the window would launch into the XProtect idle-daemon band that cost window a9's first member, now unrecoverable because the one-launch capability makes relaunch a newly frozen session
> REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

Citation: `sitting-packet-FINAL.md:89-92`; seat report `:101`; refuter B-contract/B-execution — "F3 prewindow gap arithmetic verified: clean exit ~60s vs author 600s (gap 540s). Remedy: min-dwell in --wait; do NOT lower author threshold" (`sitting-packet-FINAL.md:430-431`).
Post-verdict adjudication: none — CONFIRMED, remedy pinned by the cold ruling to "the ≥10-min continuous dwell in `prewindow_check --wait` (do NOT lower the author's 600 s threshold)" (`cold-fable-ruling.md:88`).

### (b) What changed since 2026-08-15
- **`a61ac92` (merged to main)** added the min-dwell to the script exactly as ordered: `scripts/prewindow_check.sh:37` — `MIN_CLEAN_DWELL_S=600                # continuous clean time required by D-134`.
- The `--wait` loop now requires *continuous* clean time and **resets on any failed sample**: `:172-199`. Comment at `:172-174`: *"require at least ten continuous clean minutes. Any failed sample resets Bash's elapsed-seconds interval; three quick samples are not a substitute for the idle dwell that D-134's T-0 author independently checks."* First-sample time is explicitly not counted (`:182-184`: *"The clean interval starts only after a complete successful sample; time spent proving that first sample is not retroactively counted as clean"*). Exit READY only at `clean_elapsed >= MIN_CLEAN_DWELL_S` (`:190-192`).
- The author's threshold was **not** lowered: `joulewise/arm_readiness_evidence_t0.py:50` — `_MIN_IDLE_NS = 600 * 1_000_000_000`.
- A **third**, independent enforcement was added at the capture layer: `scripts/capture_t0_step.py:712-717` refuses any `prewindow-check` capture whose `finished_monotonic_ns - started_monotonic_ns < 600 * 1_000_000_000`, as part of `_require_sequence`'s predecessor validation.
- The producer derives the E-7b argv itself — the operator cannot substitute a shorter one: `prewindow_command = ("/bin/bash", …"scripts/prewindow_check.sh", "--wait", "--timeout-min", "45", "--window", profile)` (`scripts/capture_t0_step.py:478-485`), and `_require_sequence` compares the stored `argv` against the re-derived one (`:698`).
- All of the above is **on main** (verified: `git diff main HEAD -- scripts/prewindow_check.sh scripts/capture_t0_step.py joulewise/arm_readiness_evidence_t0.py` is empty).

### (c) Candidate disposition for the seat
**READY-EVIDENCE-ATTACHED.** The seat is adjudicating whether a 600 s continuous-clean dwell in `--wait`, plus the unchanged 600 s author floor, plus a third 600 s span check in the capture validator, closes the 540 s contradiction — noting that the 45-minute `--timeout-min` cap now sits only 35 minutes above the required dwell, and that this path has never been executed live.

### (d) Skeptical probes
1. Timeout headroom: with `MIN_CLEAN_DWELL_S=600` and a hardcoded `--timeout-min 45`, a machine that goes dirty even twice at minute ~20 and ~32 has no room left. Run `--wait` on a real 2am machine and ask how often the reset fires. Is 45 minutes an evidenced number or an inherited default?
2. `$SECONDS` is wall-clock, not monotonic. The dwell loop uses Bash `$SECONDS` (`:175-197`) while the capture's independent check uses `monotonic_ns`. Probe a clock slew (D-127 turns network time **off** at E-5, but an NTP step before that): can the two disagree, and which refuses?
3. The reset is `clean_since=-1` only on `check_once` failure. Check 8's agent census is the pattern L8-N1/L9 says is *broken* (see N1 below) — so a live `claude`/`t3` session never trips the reset. Does the dwell then certify a machine that is not quiet?
4. Confirm the E-7b **frozen** command in whatever operator document Ed actually holds. The stale `arm-packet-alpha-FINAL-20260813.md` (see B5) was never recut and its §3 tap script predates all of this.
5. `_require_sequence` validates the dwell only when `prewindow-check` is a *predecessor* (`:712-717`). Does the check also run when `prewindow-check` is the step being captured, or only retrospectively at `ledger-readiness`/`ledger-reservation`?

---

## L8-B3 — CLOCK_PROBE needs sudo -n systemsetup, which D-004's powermetrics-only sudoers cannot satisfy

### (a) Original finding (VERBATIM)
> ### L8-OPERATOR-RECOVERY-HUMAN-FACTORS B3: CLOCK_PROBE needs sudo -n systemsetup, which D-004's powermetrics-only sudoers cannot satisfy
> at: joulewise/arm_readiness_evidence_t0.py:884-905; docs/decision_log.md:316; runbook:509-514
> scenario: At authoring time (>10 min after E-4/E-5 because E-7b's wait sits between), the interactive sudo timestamp is cold and the sudoers NOPASSWD entry covers only /usr/bin/powermetrics, so the fresh `sudo -n systemsetup -getusingnetworktime` probe exits nonzero → clock.network_time_off underivable → author REFUSE → no GO receipt, with no documented recovery at night
> REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

Citation: `sitting-packet-FINAL.md:94-97`; seat report `:102`; binds ED-Q-L8-1 (`sitting-packet-FINAL.md:195`).
Post-verdict adjudication: partial — Disposition 4 struck **F4's timing premise** only, "privilege gap survives inside WO-T0-PRODUCER" (`council-verdict.md:44-46`).

### (b) What changed since 2026-08-15 — the largest repair in the row
- **The privileged `get` was eliminated, not granted.** D-127 authorizes only the two exact *write* vectors. Runbook `docs/phase_2/window_runbook.md:542-547`: *"macOS gates both the read and the write of this setting … **D-127 authorizes only the exact `off` and `on` writes**; the capture wrapper and the T-0 author use the `off` vector, and restore uses the `on` vector. **No wildcard or privileged `get` is authorized.**"* (on main).
- The prior-state read became an **operator-interactive** record with no subprocess at all: `scripts/capture_t0_step.py:49-52` `INTERACTIVE_PRIOR_STATE_ARGV = ("operator-interactive", "network-time-prior-state")`, returned by `_command_for_step` for `clock-prior-state` (`:605-606`); `arm_context["clock_route"] = "MANUAL"` (`:438`).
- The clock attestation is now an operator-supplied independent-clock literal cross-checked against the derived system clock with a 2.0 s tolerance — no privilege: `_clock_attestation` (`:536-599`), `reference_source: "independent_trusted_clock"` (`:591`), refusal `evidence_author_t0_capture_clock_observation_invalid`.
- The remaining privileged call is the D-127 **write**: `("/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-setusingnetworktime", "off")` — `scripts/capture_t0_step.py:607-613` and `joulewise/arm_readiness_evidence_t0.py:891-915` (`_derive_clock_probe`), argv hard-validated by `_systemsetup_argv`.
- **Regression pins the absence of the `get`:** `tests/test_capture_t0_step.py:410-419` `test_capture_paths_contain_no_privileged_network_time_get` asserts `"-getusingnetworktime"` appears in none of `scripts/capture_t0_step.py`, `scripts/prewindow_check.sh`, `joulewise/arm_readiness_evidence_t0.py`.
- **Sudoers fragment shipped:** `scripts/joulewise-network-time.sudoers` (296 bytes, sha256 `7dfe980be89a7912d69c6e72b5582649fc4c50db88bf709bcfbb4a1c34e4406d`), a `Cmnd_Alias` over exactly the two fixed argv, `edr ALL=(root) NOPASSWD:`. Introduced by `a61ac92` — **on main**. It is a *second* fragment beside D-004's, not an amendment of it.
- **INSTALLED, with operator receipts (off-repo).** `/etc/sudoers.d/joulewise-network-time`, `root:wheel`, mode `0440`, **296 bytes**, dated **Aug 17 17:55** — beside `joulewise-powermetrics` (Jul 6 20:52, unamended). Custody receipts in `~/JouleWise-window-custody/ed-qual-20260817/`: `sudoers-digest.txt` (matches `7dfe980b…`), `sudoers-vector-off.txt` (17:56:53.212 → `setUsingNetworkTime: Off`) and `sudoers-vector-on.txt` (17:56:53.240 → `On`) — 28 ms apart, i.e. genuinely passwordless — plus `vector-{off,on}-confirmed.txt` ground-truth flips.
- In-repo corroboration: `docs/run_reports/2026-08-18-t10-session.md:104` (commit `786183a`, **on main**): *"| **D-127 sudoers** | Installed root:wheel 0440; digest `7dfe980b…` verified; **both** vectors passwordless with ground-truth state flips (Network Time Off→On) |"*; and `docs/process/ed-morning-packet-2026-08-18.md:111-113` marks it **CLOSED**.
- **Exercised live in an unattended driver:** `docs/process_traces/2026-08-18-shakedown-first-light/05-driver-as-run.sh:31-33` runs `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off` with an EXIT-trap restore at `:19-22,66-67`. Commit `4db15bd` — **on main**. A non-interactive `sudo -n` in an unattended trap only works with the rule already live.
- Ed's owed step was `docs/process/ed-evening-checklist.md:8-13` item 1 (commit `aa90dc3`).

### (c) Candidate disposition for the seat
**READY-EVIDENCE-ATTACHED (ED-Q-L8-1 closed).** The seat is adjudicating whether removing the privileged `get` entirely (regression-pinned), replacing it with a MANUAL/interactive prior-state record plus an independent-clock attestation, and installing + twice-exercising the two-vector D-127 fragment, closes B3 — noting the residual that the *installed bytes* were never digest-verified as root (only size 296 and mode 0440 are observable to a non-root reader) and that three repo docs still describe the install as pending.

### (d) Skeptical probes
1. Root-verify the install: `sudo shasum -a 256 /etc/sudoers.d/joulewise-network-time` against `7dfe980b…`, and `sudo visudo -cf /etc/sudoers.d/joulewise-network-time`. This is the only unclosed leg and it is an Ed-hands step.
2. **Three stale docs contradict the closure.** `docs/phase_2/alpha_arm_readiness.md:126-129` still reads *"`privilege.installed_bytes` | **STAGED BY #152; INSTALL EVIDENCE PENDING.**"* and *"`privilege.activation_fence` | **IMPLEMENTATION LANDED; OPERATOR EVIDENCE PENDING** … remain in the batched qualification session"* — last touched `f130827` (2026-08-16), one day **before** the install. Also `docs/process/ed-batch-packet.md:53`, `RUN_STATE.md:541-542,621`. Ask which surface a 2am operator would read.
3. The prior-state literal is now typed by the operator from an interactive read. Nothing binds it to reality. What refuses if Ed pastes `Network Time: Off` when it is On?
4. The 2.0 s clock tolerance (`capture_t0_step.py:578`) is compared against `utc_now()` — the *system* clock, which E-5 is about to freeze by disabling NTP. Probe: is the attestation taken before or after the `off` write, and can a pre-existing multi-second offset pass?
5. `_derive_clock_probe` raises *"fresh D-127 enforcement did not set network time Off"* on nonzero exit. On a machine where the fragment is missing (a fresh clone, a new operator, a re-imaged Mac), what is the documented night recovery? B3's original "no documented recovery at night" limb.
6. `RUN_STATE.md` current blocks (T12 `:291`, T11 `:335`, T10 `:394`) carry **zero** hits for `sudoers`/`D-127`/`systemsetup`. The item has fallen off the live tracker even though its evidence lives off-repo.

---

## L8-B4 — Committed freeze receipt is stale — the ALPHA pack cannot arm at the audit baseline

### (a) Original finding (VERBATIM)
> ### L8-OPERATOR-RECOVERY-HUMAN-FACTORS B4: Committed freeze receipt is stale — the ALPHA pack cannot arm at the audit baseline
> at: configs/campaigns/d117_floor_qwen25_1p5b_v1/arm_readiness.freeze.receipts/freeze-0001.json (pack_identity.pack_root=/Users/edr/JouleWise-measurement-20260813/…) vs joulewise/arm_readiness.py:3604-3610
> scenario: Executed: every `generate_arm_readiness.py arm` invocation at the baseline head refuses readiness_freeze_receipt_mismatch before row evaluation, because freeze-0001.json binds the pre-#149 measurement-tree pack identity while the committed digest is now f4c02c8a…; the pack also still self-describes 'unfrozen draft / not armable' (M-2), which §5C's entry gate treats as NO-GO — a re-freeze plus magistrate ruling must precede any night
> REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

Citation: `sitting-packet-FINAL.md:99-102`; seat report `:103`.
**Post-verdict adjudication: STRUCK.** `council-verdict.md:44-45` Disposition 4: *"**Struck findings:** L8-B4 (both lenses: wrong-path artifact; correct fail-closed refusal), WO-L2-4 (phantom), F4's timing premise (privilege gap survives inside WO-T0-PRODUCER)."* Underlying refuter text, A-contract lens: *"L8-B4 freeze-receipt mismatch: REFUTED. Mismatch was wrong-path artifact (receipt binds canonical measurement-checkout absolute path; identity_matches=True all three packs at canonical path; committed digest not a comparison input; M-2 already governs placeholder text). CAVEAT: canonical-path arm probe degraded to readiness_io_error at boot lookup (read-only sandbox); execution lens to replay. Severity: dies as independent blocker; wrong-checkout refusal = correct fail-closed."* (`sitting-packet-FINAL.md:371-376`). Also `:487` — "DEAD: L8-B4 freeze-receipt mismatch (both lenses, artifact)".

### (b) What changed since 2026-08-15 — what the successor re-freeze does to the underlying question
B4 is struck as a *blocker*, but it named two underlying questions the seat still has to see resolved: **(i)** which pack/checkout an arm night actually binds, and **(ii)** the M-2 "unfrozen draft / not armable" placeholder.

**(i) The `_v3` re-freeze reproduces B4's exact *shape* at a new canonical root.**
- Freeze-0003 minted for all three packs: `5e38f1e` (1p5b_v3), `eb7f6c6` (7b_v3), `94dc3b3` (contrast_v3), plus `8b2b021` (S5 confirmation table). **ALL FOUR ARE BRANCH-ONLY** — `impl/r2-s0-mint-resolver`, not on `main` (verified with `git merge-base --is-ancestor … main`).
- `configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.freeze.receipts/freeze-0003.json` binds `pack_identity.pack_root = "/Users/edr/JouleWise-measurement-20260818/configs/campaigns/d117_floor_qwen25_1p5b_v3"`, `plan_path: "calibration_plan.json"`, `plan_id: …-v3`, `plan_sha256 9ab4776f…`.
- **The runbook's own §4 example still binds `/Users/edr/JouleWise-measurement-20260813` and the `_v2` family** (`window_runbook.md:192-217`, and `:233-238`: *"The `_v2` successor family (amended 2026-08-18) emits the ruled `plan.path: "calibration_plan.json"` shape in all three profiles, so this example binds the `_v2` packs"*). The freeze-0003 receipts bind the **20260818** checkout and the **`_v3`** packs. An operator copying §4 verbatim would arm against a pack generation that is now one behind, at a checkout path that is two generations behind.
- `docs/process/rehearsal-operator-card.md` likewise pins `_v2` and `freeze-0002` at `/Users/edr/JouleWise-measurement-20260818` (`:3`).

**(ii) M-2 was resolved by ruling, not by byte repair — and the placeholder text is now doctrine.**
- Disposition 2 remanded M-2 to its own cold gate (`council-verdict.md:31-38`). That gate was held: `docs/process_traces/2026-08-15-m2-coldgate/composed-verdict.md`. Its Disposition 2a **strikes the premise B4 relied on**: *"The 'overrode a NO-GO reading' premise is STRICKEN. No machine gate and no §5C clause reads draft_status (verified); the premise traced to L8-B4, itself struck at the council."* Disposition 2b strikes the "every arm packet must cite this ruling" duty, replacing it with *"one informational operator note that pack descriptive text is legacy and receipts govern."*
- A second cold gate then settled the successor semantics: `docs/process_traces/2026-08-18-freeze-semantics-coldgate/` (14 files incl. `12-cold-adjudicator-ruling.md`, `13-opus-contract-refuter.md`, `14-composed-verdict.md`). Ruling at `12-…:17`: *"**No gate reads the descriptive bytes** — `grep draft_status joulewise/ --include=*.py` returns nothing. M-2(a)'s premise holds in code. VERIFIED."*; and `:59`: freeze-awareness is satisfied by dynamic `target_status` from the authenticated attachment, a fail-closed regeneration guard, and byte-identical preserve-mode replay — *"§B3's 'final frozen snapshot' is re-read as the snapshot as committed under the receipt — the draft-worded bytes."*
- Consequently the `_v3` packs **still carry draft wording by design**: `configs/campaigns/d117_floor_qwen25_1p5b_v3/{plan_tree.json:793, calibration_plan.json:3, order_manifest.json:3, producer_contract.json:13}` all read `"draft_status": "as_generated_pre_d134_freeze"`, and `README.md:5` now states *"This description does not carry freeze status. The committed D-134 freeze receipt and its plan-tree attachment are authoritative … An external unexpired PASS/GO arm receipt is required before launch."* The wording changed from the v1 "The pack is not armable" to a receipt-deferring sentence.

### (c) Candidate disposition for the seat
**STRUCK-AT-2026-08-15** (per Disposition 4), with a live successor question attached. The seat is adjudicating not B4 itself but whether the `_v3`/freeze-0003 re-freeze — **which lives only on `impl/r2-s0-mint-resolver` and not on `main`** — plus two cold-gate rulings that legitimise the draft wording, leave the operator's documents pointing at the *right* pack and checkout; on the evidence, they do not (runbook §4 = `_v2` @ `20260813`; rehearsal card = `_v2` @ `20260818`; freeze-0003 = `_v3` @ `20260818`).

### (d) Skeptical probes
1. Which pack does the READY-candidate window actually arm — `_v2` or `_v3`? Then check `window_runbook.md:192-217` and `docs/process/rehearsal-operator-card.md:3` and ask which of them is correct.
2. `MEASUREMENT_REPO=/Users/edr/JouleWise-measurement-20260813` (runbook `:191`) vs `pack_root=/Users/edr/JouleWise-measurement-20260818` (freeze-0003). `capture_t0_step.py:344-348` refuses when `_repo_for_pack(pack) != REPO_ROOT`. Predict the refusal an operator copying §4 gets, and where in the night it fires.
3. The re-freeze is **branch-only**. `git merge-base --is-ancestor 5e38f1e main` → no. Ask what happens to the READY claim if the branch is not merged before the sitting.
4. Disposition 2b requires the successor arm packet to carry the informational M-2 note. **No successor arm packet exists** (see B5). Where does that note live?
5. Replay the A-contract lens's unresolved CAVEAT: *"canonical-path arm probe degraded to readiness_io_error at boot lookup (read-only sandbox); execution lens to replay."* Was that replay ever done at the canonical path on the real machine?
6. Freeze-0003's `predecessor` field references `_v2`. Verify the chain `freeze-0001 → 0002 → 0003` reauthenticates (`b6553fd` "WO-FREEZE-NUMBERING delta-8: replay reauthenticates the successor; v2 freeze sequences carry the predecessor").

---

## L8-B5 — The FINAL arm packet's tap script is stale against the baseline runbook and would run the wrong night sequence

### (a) Original finding (VERBATIM)
> ### L8-OPERATOR-RECOVERY-HUMAN-FACTORS B5: The FINAL arm packet's tap script is stale against the baseline runbook and would run the wrong night sequence
> at: ~/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md §3 (frozen tree 49dcc49a, digest 6246b618) vs runbook:802-838 and manifest head ac3fe1d2/digest f4c02c8a
> scenario: The packet is expressly 'written to be executed without reading the runbook', yet it contains no T-0 authoring E-step, no 20-minute volatile horizon, no re-author rule, and expects §0.6's 'no shipped authoring route' refusal that no longer matches the shipped tooling; a tired Ed following it verbatim goes E-9 → E-9a and dead-ends (or worse, improvises) at the exact point the current runbook inserts the author step
> REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

Citation: `sitting-packet-FINAL.md:104-107`; seat report `:104`; independently raised by L6 as its should-fix S4 (`sitting-packet-FINAL.md:150`); B-contract refuter minimal WO set item (4) *"issue a successor FINAL packet only after those mechanics pass end-to-end"* (`refuter-outputs/sol-refuter-B-contract.md:250`).
Post-verdict adjudication: none — CONFIRMED; sequenced into **Phase 2**: *"then the successor arm packet ONLY after the T-0 repair passes end-to-end at the exact reviewed head (Opus W8)"* (`council-verdict.md:99-100`); Opus W8 at `opus-contract-refuter-findings.md:71`; plus the M-2 rider *"the successor arm packet must cite it until the re-freeze retires it"* (`council-verdict.md:39`), later narrowed to an informational note (`m2-coldgate/composed-verdict.md:20`).

### (b) What changed since 2026-08-15
- **NO SUCCESSOR ARM PACKET WAS WRITTEN.** Searched: `grep -rn` across the repo for `arm-packet`, `arm_packet`, `FINAL-2026`, `successor arm packet`, `recut`, `packet-alpha` — every hit is either (a) a *reference* to the stale packet (`TASK_QUEUE.md:768`, `RUN_STATE.md:723`, `docs/process/audit-baseline-manifest.json:3`, `docs/run_reports/2026-08-13-t6-session.md:33,625,851,910`, `docs/strategy/2026-08-14-70h-plan.md:27`), (b) the 2026-08-10/11 SKELETON-era records, or (c) the **order** to recut (`triage.json:592` WO-L8-5; `council-verdict.md:39,99`; `cold-fable-ruling.md:101`; `council_log.md:3746`). `grep -rn "FINAL-2026"` matches only `arm-packet-alpha-FINAL-20260813.md`.
- Off-repo custody confirms it: `~/JouleWise-window-custody/t4-session-20260810/` contains exactly `arm-packet-alpha-FINAL-20260813.md` (67081 bytes, **mtime Aug 13 20:21**), `arm-packet-alpha-SKELETON.md`, `arm-packet-discrepancy-resolutions.md`. **Nothing written after 2026-08-13.** The document the council found stale is byte-for-byte the document that still exists.
- `L8-B5` appears **nowhere** in `RUN_STATE.md` (zero hits); no `recut` line; no open-item row tracks it.
- **What was written instead:** `docs/process/rehearsal-operator-card.md` (123 lines) + `scripts/ed_session/build_rehearsal_env.sh` (183 lines), both added by **`ad14ac4`** "Dress-rehearsal builder + operator card (terra rounds 1-5)" — **merged to main**; neither file touched since. It is explicitly a narrower artifact: `:1` *"# D-117 ALPHA scratch **dress-rehearsal** operator card"*, `:3` *"This is **qualification choreography evidence, never claim evidence**."*
- Against B5's four named gaps, the card scores **2 of 4**: T-0 authoring step **present** (`:98`, E-9b invoking `scripts/author_arm_evidence_t0.py`); 20-minute volatile horizon **present** (`:95`, bolded); **5-minute arm-receipt fuse ABSENT** (`grep -iE "fuse|5-minute|five-minute|300"` over the card → nothing); **re-author rule ABSENT** (`grep -iE "re-author|reauthor"` → nothing; §11 has a reset-for-retry `rm -r`, which is not the same rule).
- The builder is **not** a packet generator — it builds a disposable rehearsal *environment* (scratch custody/ledger/runs/backup roots, extracted `window-chain.zsh`, a 25-key `window.env`) and ends by printing `NEXT=docs/process/rehearsal-operator-card.md` (`:183`). Its pin is a *starting* commit, not the reviewed head: `START_COMMIT="28a0daa22ca17d5c27df94879763e57c34665646"` (`:6-10`, on main) with only `git merge-base --is-ancestor "$START_COMMIT" HEAD` (`:32`) — it accepts **any** descendant, so it structurally cannot satisfy Opus W8's "exact reviewed head".

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND.** The seat is adjudicating a blocker with no repair: the operator's night document is the same 2026-08-13 file the council condemned; the only new operator artifact is a scratch rehearsal card that is explicitly non-claim, covers 2 of the 4 missing elements, and is pinned to a starting commit rather than a reviewed head — and B5 is not tracked anywhere in `RUN_STATE.md`.

### (d) Skeptical probes
1. `ls -la ~/JouleWise-window-custody/t4-session-20260810/` and read the mtime. Is there any arm packet newer than 2026-08-13?
2. Opus W8 makes the successor packet cuttable only *after* the T-0 repair passes **end-to-end at the exact reviewed head**. The T-0 repair has never been executed end-to-end at all (see ED-Q-L8-2). Is W8's precondition even reachable before the rehearsal runs?
3. `docs/process/audit-baseline-manifest.json:3` still binds the stale packet as the operator document of the audit baseline. If the manifest is superseded (Phase 3), what replaces that binding?
4. Disposition 2b of the M-2 cold gate assigns an informational note to "the successor arm packet". With no such packet, is that ruling in effect discharged, orphaned, or breached?
5. `build_rehearsal_env.sh:32` asserts only ancestry. Ask what stops the rehearsal from running at a head that differs from the terminal-review-attested commit the T-0 author demands (see the trailer sub-row).
6. `rehearsal-operator-card.md:3` says "Ed's terminal-review commit advances its HEAD" — so by construction the card runs at a head *after* the pinned one. Which head is "reviewed"?

---

## L8-B6 — Runbook §4 window.env example and §6 chain template fail the T-0 author's own machine contract

### (a) Original finding (VERBATIM)
> ### L8-OPERATOR-RECOVERY-HUMAN-FACTORS B6: Runbook §4 window.env example and §6 chain template fail the T-0 author's own machine contract
> at: runbook:181-206 ($-values, WINDOW_CUSTODY_ROOT/BACKUP_DEST naming, FROZEN_PLAN=custody reservation JSON) and runbook:971 (REPO=${MEASUREMENT_REPO:-…}) vs joulewise/arm_readiness_evidence_t0.py:571-593,652-676,1138-1156
> scenario: A freeze-step that copies the runbook's own example produces window.env with $-containing values (parser refuses as ambiguous), missing CUSTODY_ROOT/CLAIM_BACKUP_DEST/BOUND_BACKUP_DEST keys, a FROZEN_PLAN that is not the pack's calibration_plan.json (E-8 capture argv then fails the reviewed-literal check), and a chain whose REPO line fails the exact-binding regex — four independent guaranteed authoring refusals discovered only at night
> REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

Citation: `sitting-packet-FINAL.md:109-112`; seat report `:105`. Both B-lens refuters confirmed all four *and* added the fifth: *"The plan mismatch is worse than reported. Production `plan_tree.json` stores a repository-relative path … but the author joins that to `pack_root` … producing a doubled, nonexistent path. The synthetic test fixture instead uses `pack / "calibration_plan.json"` … masking the production-pack shape."* (`refuter-outputs/sol-refuter-B-execution.md:228`; same at `sol-refuter-B-contract.md:246`).
Post-verdict adjudication: none — CONFIRMED; both the four mismatches and the doubled path folded into WO-T0-PRODUCER with a **mandatory real-pack regression** (`council-verdict.md:82-83`; `cold-fable-ruling.md:88`), gated behind the R2 `FROZEN_PLAN` ruling (Opus W4, `opus-contract-refuter-findings.md:63`).

### (b) What changed since 2026-08-15 — four of five cured; a new sixth mismatch is live
All citations below are on **`main`** (runbook diff main↔HEAD is D-079 constants only).

**Cured — refusal 1 (`$`-values):** §4 now states the contract in prose (`window_runbook.md:181-185`): *"This file is a frozen literal input to the T-0 producer: it has exactly the keys below, every path is absolute, and no value contains `$` or a shell expansion."* The example (`:191-217`) carries no `$`. Parser: `scripts/capture_t0_step.py:253-257` refuses on `"$" in parts[0]` or multi-token values.

**Cured — refusal 2 (key naming):** the example now carries **exactly the 25 keys** of `_ENV_KEYS` (`capture_t0_step.py:102-130`), including `CUSTODY_ROOT` (`:213`), `WINDOW_CUSTODY_ROOT` (`:214`), `CLAIM_BACKUP_DEST` (`:216`), `BOUND_BACKUP_DEST` (`:217`). `_parse_window_environment` refuses on any missing **or unknown** key (`:259-266`), and `_load_context:409-412` additionally requires `CUSTODY_ROOT == WINDOW_CUSTODY_ROOT` — which the runbook explains at `:224-228`.

**Cured — refusal 3 (`FROZEN_PLAN`):** §4 `:183-186`: *"`FROZEN_PLAN` is R2's execution-boundary literal for the committed pack-relative `calibration_plan.json`; it is not a custody reservation plan."* Example value is the pack's own plan (`:194`). Enforced by `_load_context:373-380` against `readiness.resolve_frozen_plan`. §6 `:1140-1144` adds *"Never create or select a second custody reservation JSON."*

**Cured — refusal 4 (chain `REPO`):** §6 template is now a literal (`:1150` `REPO=/Users/edr/JouleWise-measurement-20260813`), matched by `capture_t0_step.py:464-475` (`^REPO=…$` regex requiring exactly one value equal to the resolved repository, plus no `^QUARANTINE_ROOT=` override) and independently by `arm_readiness_evidence_t0.py:676-682`.

**Cured — the refuter's doubled plan-path:** the shared strict resolver `readiness.resolve_frozen_plan` (`joulewise/arm_readiness.py:3720-3765`) — docstring: *"The stored path is never repaired with a basename or repository-root fallback. The absolute path returned here is the sole execution-boundary literal for `FROZEN_PLAN` and every governed `--plan` argument."* It joins `plan.path` to `pack_root` component-by-component with symlink and regular-file checks. Runbook `:233-237`: *"The v1 ALPHA and BETA `plan_tree.json` bytes carry the superseded repository-relative spelling; the shared R2 resolver refuses those packs, and they are never basename-repaired in an operator file."* Verified: `configs/campaigns/d117_floor_qwen25_1p5b_v3/plan_tree.json` `plan.path == "calibration_plan.json"`. So the doubled path is cured by **fail-closed refusal of the v1 packs**, not by repair.

**NOT cured — a sixth, live mismatch of the same shape, self-documented rather than fixed.**
- `window_runbook.md:1189-1192`: *"Save the following as `WINDOW_PLAN_ROOT/window-chain.zsh` … **`window.env` must additionally bind the absolute `ARM_RECEIPT`, `ARM_READINESS_CUSTODY_ROOT`, and `LAUNCH_MANIFEST` paths used by E-10**"*, and the chain body then dereferences `"$ARM_RECEIPT"` (`:1209`) and `"$LAUNCH_MANIFEST"` (`:1211`) under `set -euo pipefail` (`:1197`).
- But `_ENV_KEYS` is an **exhaustive 25-key set that contains neither `ARM_RECEIPT` nor `LAUNCH_MANIFEST`**, and `_parse_window_environment` refuses `unknown` keys (`capture_t0_step.py:259-266`). §4's example carries the 25 and no more.
- The repair round **knew and recorded it instead of fixing it** — `docs/process/rehearsal-operator-card.md:5`: *"`window.env` deliberately has the producer's enforced exact 25-key set, which excludes `ARM_RECEIPT` and `LAUNCH_MANIFEST`; **this differs from the runbook chain wording.** The paths are derived after ARM in this card; do not edit `window.env`."*
- Note the T-0 **author** (`arm_readiness_evidence_t0.py:657-671`) checks only a *subset* of expected keys and would tolerate extras — so the exact-key refusal is the **capture tool's**, i.e. it fires at E-4…E-9a, before ARM exists. The two documents therefore cannot both be satisfied at the same time by one `window.env`.

### (c) Candidate disposition for the seat
**STILL-OPEN (four of five refusals cured; one new refusal of the identical class is live and documented-not-fixed).** The seat is adjudicating whether §4/§6 now compose into a copyable operator contract, given (a) the 25-key vs `ARM_RECEIPT`/`LAUNCH_MANIFEST` contradiction between `window_runbook.md:1189-1192` and `capture_t0_step.py:102-130`, and (b) the §4 example's `_v2`/`20260813` bindings against the `_v3`/`20260818` freeze-0003 receipts (see B4).

### (d) Skeptical probes
1. Author a `window.env` from §4 verbatim, then append the two keys §6 demands, then run `capture_t0_step.py clock-prior-state`. Expected: `evidence_author_t0_capture_environment_invalid … unknown=['ARM_RECEIPT','LAUNCH_MANIFEST']`. Then omit them and run `window-chain.zsh`: expected unbound-variable abort under `set -u`. Which is the intended night?
2. If the answer is "append the two keys after E-9a", nothing pins `window.env` bytes across the capture→author boundary — `arm_readiness_evidence_t0.py:645-650` re-reads `window.env` at author time via `_input_identity`. Probe whether mutating `window.env` between the last capture and E-9b is detected at all.
3. §4's example is `_v2` @ `/Users/edr/JouleWise-measurement-20260813`; freeze-0003 binds `_v3` @ `…20260818`. Copy §4 verbatim and predict the first refusal (`capture_t0_step.py:344-348`).
4. `SETTLE_S` must be exactly `"180"` (`capture_t0_step.py:413-417`) and `POWER_POLICY` must match `_frozen_power_policy` (`arm_readiness_evidence_t0.py:670`). Are both frozen literals present and correct in §4 and in whatever the rehearsal builder emits?
5. The mandatory **real-pack** regression: `grep -n resolve_frozen_plan tests/test_capture_t0_step.py` returns one hit (`:72`) inside a fixture builder. Name the test that loads a committed `configs/campaigns/d117_*` pack. If none exists, the cold ruling's mandatory condition on this WO is unmet and the doubled-path cure is suite-masked in the same way the original defect was.
6. `CLAIM_BACKUP_DEST`/`BOUND_BACKUP_DEST` in §4 are double-quoted because the iCloud path contains a space. `shlex.split(posix=True)` handles that — but confirm the frozen bytes match what the operator's editor writes (smart quotes, trailing whitespace).

---

## L8-B7 — Launch without arm/consume ceremony is not machine-caught at launch or by any downstream consumer

### (a) Original finding (VERBATIM)
> ### L8-OPERATOR-RECOVERY-HUMAN-FACTORS B7: Launch without arm/consume ceremony is not machine-caught at launch or by any downstream consumer
> at: runbook:964-1148 (window-chain.zsh performs no receipt check); grep: arm_readiness.consumptions referenced only in joulewise/arm_readiness.py and arm_readiness_evidence_t0.py
> scenario: Ed (or a rushed magistrate) skips E-9a/b/c after the E-9 reservation and runs the launch recipe: the chain settles, calibrates and collects a normal-looking window with no refusal anywhere; the only gate on the missing arm/consumption lineage is human close-out item 5 — the required launch-license output neither traces through a machine consumer nor fails closed (cross-confirm consumer side with L5/L6/L7/L10)
> REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

Citation: `sitting-packet-FINAL.md:114-117`; seat report `:106`. **Both DG lenses CONFIRMED**: DG-contract — *"L8-B7 launch ceremony: CONFIRMED blocker (consume_launch_capability exists but never execs; chain has no receipt check; zero downstream consumers authenticate launch lineage). Remedy: reviewed launcher consume->exec + downstream provenance refusal; Ed still performs physical launch."* (`sitting-packet-FINAL.md:404-406`); DG-execution — *"L8-B7: CONFIRMED blocker. Minimal WOs per both lenses: (1) kernel reconciliation, (2) atomic arm-consume-to-launch binding."* (`:417-418`).
Post-verdict adjudication: escalated — Opus W7 ruled it **contract-bearing**, requiring a Phase-0 rule-2 design consult before code (`council-verdict.md:78`).

### (b) What changed since 2026-08-15 — the deepest repair in the row, and still not closed
- **Phase-0 consults held and custodied:** `docs/process_traces/2026-08-15-launcher-binding-consult/{consult-prompt.md,consult.md}` and `docs/process_traces/2026-08-15-launch-lineage-consult/{consult-prompt.md,consult.md}`. Mechanism adopted at `5fe977d` "WO-LAUNCH-BINDING F2 lineage-locator mechanism adopted (fixed root-local locator, 8-point writer auth, no argv/env); WO staged 1-4 (stage 4 = Phase 2). Consult custodied" — **on main**.
- **`scripts/launch_window.py` exists** (304 lines), created by `345bfbb` "WO-LAUNCH-BINDING checkpoint (WIP — NOT merge-ready): launcher core + verify_consumed_launch + scoped downstream gates" and rewritten by `66884c6` — **both on main**.
- **`impl/wo-launch-binding` MERGED** — contrary to the TASK_QUEUE hand-authored checkpoint's framing. `git merge-base --is-ancestor impl/wo-launch-binding main` → **yes**, via **PR #156 (`f392ff6`, 2026-08-16)**; stage 3 followed via **PR #157 (`bd333de`)**; `impl/wo-consumption-edge` via **#155 (`d54db78`)**.
- **A third-failure cold gate was held on this WO:** `docs/process_traces/2026-08-16-launch-f3-coldgate/` — 18 artifacts including `01/02` dual-lens reports, `04`/`10` delta reports, `05/06` escalation consult, `11-branch-full-diff.patch`, `12-cold-adjudicator-ruling.md`, `13-opus-contract-refuter-report.md`, `14-composed-verdict.md`. Verdict `14-…:1-9`: *"DESIGN AFFIRMED. ADOPT_PRIVATE_REQUIRED_CONTEXT_API stands"*, refuter CONCUR-WITH-AMENDMENTS A0–A11 adopted in full.
- The `66884c6` fix round **deleted the forgeable surfaces**: *"public consumption wrapper and BOTH caller-frame guards DELETED (forgeable checks must not exist even as decoration); module-private required-context consumer with callee-side reauthentication; atomic no-clobber primary = the only real enforcement; honest registered limitation (in-process forgery = same-UID family, Ed-owed)"*.
- **Runbook §5C/E-10 rewritten** (`window_runbook.md:1052-1075`, on main): the sole reviewed launcher *"generates the anonymous-FD handoff, atomically creates and fsyncs the no-clobber consumption primary (the single-use linearization point), publishes its sidecar, replays `verify_consumed_launch`, and calls `execve` on the exact frozen foreground argv. It neither spawns and returns nor retries."* The chain's first executable action is that launcher (`:1200-1211`), and *"Direct shell invocation has no FD 198 and refuses `launch_handoff_invalid` before settle or collection"* (`:1204-1206`). *"The retained `generate_arm_readiness.py consume` CLI now refuses with registered `readiness_usage_invalid` and points to `scripts/launch_window.py`; it is not a compatibility launch path."* (`:1073-1075`).
- **BUT the runbook itself says the ceremony is not yet complete and launch is NO-GO.** `window_runbook.md:1076-1088` (on main): *"**Current implementation boundary (2026-08-15 fix round):** the launcher enforces consume → revalidate → exact `execve`, and marker-bearing campaign collection enforces exact pack-config membership plus outer/inner lineage agreement. **Calibration-slot writer enforcement is not implemented yet**; neither the three frozen D-117 packs nor their current configs may be changed in place to add the marker. Calibration-side stage 2, downstream reduce/extract/mint stages 3–4, and the Phase-2 successor-family marker freeze remain required. Therefore this E-10 command is a documented target procedure, **not current authority to launch**: every D-117 physical launch remains NO-GO until those gates and the full review gauntlet close."*
- **A1 is still an open queue row.** `TASK_QUEUE.md:536` (and the mirror at `:630`): `| A1 | WO-LAUNCH-BINDING | P1 Phase Gate | READY [AGENT] | … Note: Stages 1-3 MERGED (#156 f392ff6, #157 bd333de); calibration-side stage 2 DONE on the staged estimator branch @ e22e658 (delta-ACCEPTED, rides the re-freeze per the Phase-2 plan); remaining: stage 4 successor flag inside the transaction. **Launch stays NO-GO** |`
- The hand-authored checkpoint at `TASK_QUEUE.md:491-499` is now **stale relative to that row** — it still reads *"Stage 1 plus the campaign half of stage 2 are implemented on `impl/wo-launch-binding` … This does not close A1 or clear `WINDOW-COUNCIL-GATE`: the sibling calibration writer, stages 3-4, successor-family freeze transaction, and full C-028 gauntlet remain outstanding."* Both agree on the conclusion (A1 open, gate uncleared); they disagree on how much has landed.
- **D-149** — `0e96dbb` "D-149: standing conditional T-0 GO — full no-hands window automation (Ed); kernel fences u…" — is **BRANCH-ONLY** (`git merge-base --is-ancestor 0e96dbb main` → **no**; on HEAD → yes). Body at `docs/decision_log.md:172`, `:8865-8870`. It auto-issues T-0 GO for no-hands windows only when *"(1) a READY-candidate council verdict stands (charter form: no NOT-READY, no UNVERIFIED, **ED-QUALIFICATION rows closed**); (2) the frozen pack's arm ceremony passes every gate with freshness horizons honored…"*, and reserves to Ed *"anything needing hands (cables, backlight, reboots, new sudo), claim publication, exact-byte confirmation"*. **It removes Ed's per-window GO tap; it does not machine-enforce the arm ceremony, and it re-imports this row's ED-QUALIFICATION closure as its own precondition.** Head `79a4cd0` adds the D-149 GO-receipt template (branch-only).

### (c) Candidate disposition for the seat
**STILL-OPEN.** The seat is adjudicating a blocker with a large, cold-gated, merged repair (sole launcher, atomic no-clobber consumption primary, FD-198 handoff, `verify_consumed_launch` replay, `consume` CLI refusing) against three facts that keep it open: the runbook's own text says calibration-slot writer enforcement is unimplemented and *"every D-117 physical launch remains NO-GO"*; A1 is still `READY [AGENT]` with stage 4 outstanding and stage-2 calibration work parked on a branch (`e22e658`); and D-149 — the ruling that would let a window launch with no Ed tap — is branch-only and conditions itself on this row's closure.

### (d) Skeptical probes
1. Run the negative case that defines B7: invoke `window-chain.zsh` directly with no arm ceremony. Expected `launch_handoff_invalid` before settle. Has anyone executed it, or is it only in tests? (`docs/process_traces/2026-08-16-launch-f3-coldgate/10-delta2-report.md` — check whether A9's "honest end-to-end launcher pass post-fix" was actually run.)
2. `window_runbook.md:1076-1088` says NO-GO. `TASK_QUEUE.md:536` says NO-GO. Ask the magistrate which document *retires* that sentence, and whether stage 4 lands before or after the sitting.
3. Calibration-side stage 2 is `@ e22e658` "on the staged estimator branch … rides the re-freeze". Verify that sha exists and is unmerged; a claim of coverage resting on an unmerged branch is a material fact.
4. The 66884c6 registered limitation is *"in-process forgery = same-UID family, Ed-owed"*. Find the registration and ask what "Ed-owed" resolves to — is there an owed action nobody is tracking?
5. Downstream: the finding's second limb was *"zero downstream consumers authenticate launch lineage"*. Grep for the provenance refusal at reduce/extract/mint. Stages 3-4 per A1 are "downstream reduce/extract/mint stages 3–4 … remain required" — so is the downstream limb closed at all?
6. D-149 is branch-only. If the sitting clears this row while `0e96dbb` is unmerged, which ruling governs the first no-hands window?
7. §5C stops at *"No verdict, author, verifier, or other automated command may cross this boundary"* (`:1050-1051`) for Ed's inspection — reconcile with D-149's no-hands automation. Is the human inspection boundary still in force?

---

## L8-S1 — Arm CLI demands the ARM_CONTEXT JSON inline while the authenticated arm-context.json already sits in custody

### (a) Original finding (VERBATIM)
> - [should_fix] [L8] Arm CLI demands the ARM_CONTEXT JSON inline while the authenticated arm-context.json already sits in custody

Full seat text (`seat-reports/L8-…-report.md:109`): *"**S1 — ARM_CONTEXT must be retyped inline** though the authenticated `arm-context.json` already sits in custody (`generate_arm_readiness.py:58-70`); accept a custody path or freeze the `--arm-context "$(cat …)"` literal."*
Citation: `sitting-packet-FINAL.md:161`.

### (b) What changed since 2026-08-15
- **NO REPAIR.** `scripts/generate_arm_readiness.py:47` still `arm.add_argument("--arm-context", required=True)`, and `:65` still refuses with *"--arm-context must be the JSON object itself, not a path"*.
- The runbook restates the requirement unchanged: `window_runbook.md:1031-1039` — *"`ARM_CONTEXT_JSON` is the exact JSON object itself, not a path. Its keys are exactly `bracket_session_id`, `pre_attempt_id`, `post_attempt_id`, `clock_route`, `claim_runs_root`, `bound_runs_root`, `custody_root`, `quarantine_root`, `claim_backup_destination`, `bound_backup_destination`, and `waiver_path`…"*
- The finding got *worse* in one sense and better in another: `capture_t0_step.py:433-445` now **derives** the same eleven-key object and writes `arm-context.json` into custody (`_prepare_derived_inputs:518,527-529`) — so the authenticated file the seat pointed at is now definitely there, and the CLI still refuses to read it. Mitigation only: `rehearsal-operator-card.md:101` tells the operator *"The argument is the exact JSON object, derived by E-4"* — i.e. paste it.

### (c) Candidate disposition for the seat
**STILL-OPEN / NO-REPAIR-FOUND.** The seat is adjudicating an unfixed 2am retyping hazard that the T-0 producer has made strictly more absurd: the tool now writes the authenticated JSON to custody, and the arm CLI refuses to read it from there.

### (d) Skeptical probes
1. Diff the eleven keys `capture_t0_step.py:433-445` writes against the eleven the runbook lists at `:1032-1036`. Any drift is a paste that refuses at 2am.
2. Ask what the operator is expected to paste from — a terminal `cat` of `arm-context.json`? Then the "not a path" rule buys nothing but a copy-error surface.
3. Time the paste inside the 20-minute volatile horizon and the 5-minute fuse. The seat's §7 says the arm-receipt path is *"the sole live-substituted token"*; with an inline eleven-key JSON that is no longer true.

---

## L8-S2 — The 5-minute arm-receipt validity fuse is documented nowhere the operator can see

### (a) Original finding (VERBATIM)
> - [should_fix] [L8] The 5-minute arm-receipt validity fuse is documented nowhere the operator can see

Full seat text (`:110`): *"**S2 — 5-minute arm-receipt fuse undocumented** (`arm_readiness.py:3596`); a benign pause between E-9a and E-9c refuses and nothing tells Ed the licensed recovery (re-arm within the surviving horizon)."*
Citation: `sitting-packet-FINAL.md:162`. Also a seat deliverable at `:137` (§7): *"the **separate 5-minute arm-receipt fuse** (B/S2) nested inside"*, and named in the ED-Q-L8-2 charter (`sitting-packet-FINAL.md:196`).

### (b) What changed since 2026-08-15
- **NO REPAIR.** The fuse is still in code: `joulewise/arm_readiness.py:6101` — `def generate_arm_receipt(…, *, validity_ns: int = 300_000_000_000)` (line moved from `:3596` by intervening edits; the constant is unchanged and dates to `696576c` "§5C arm-readiness records (D-134) … (#141)").
- Searched for the documentation: `grep -rn "5-minute|five-minute|five minutes|5 minutes|300 seconds|300-second|fuse"` over `docs/phase_2/window_runbook.md`, `docs/process/rehearsal-operator-card.md`, `docs/phase_2/alpha_arm_readiness.md` → **zero hits**. The runbook documents the *20-minute* volatile horizon (`:996-1002`) and the six-hour non-volatile horizon, and requires *"the exact unexpired, unsuperseded `PASS`/`GO` result"* (`:1045`) — but never names the 300 s window or the licensed recovery.
- The rehearsal operator card, the one new operator document, also omits it (see B5(b)) — and it is the document ED-Q-L8-2 was supposed to time *against* the fuse.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND.** The seat is adjudicating an undocumented 300-second failure mode that sits inside the ceremony the row's own qualification (ED-Q-L8-2) was chartered to time — and that qualification was never run.

### (d) Skeptical probes
1. `grep -rn "300_000_000_000" joulewise/` and then grep every operator-facing doc for its plain-language equivalent. If the only home is a Python keyword default, the operator cannot see it.
2. Is 300 s ever overridden at the call site? `generate_arm_receipt` takes `validity_ns` as a keyword — check whether `scripts/generate_arm_readiness.py` passes a different value, which would make the fuse invisible *and* wrong.
3. The seat says re-arm within the surviving 20-minute horizon is licensed. Find the code path that permits a second ARM after a fuse expiry, and reconcile with `arm_readiness_evidence_t0.py:1511-1517` (a REFUSE arm receipt occupies the namespace, making re-authoring "intentionally impossible after any refused ARM"). Is the licensed recovery real or folklore?
4. Ask what the operator sees on expiry — a registered refusal code, or a bare traceback.

---

## L8-S3 — Re-author cleanup is a raw rm -r on custody paths with no shape verification

### (a) Original finding (VERBATIM)
> - [should_fix] [L8] Re-author cleanup is a raw rm -r on custody paths with no shape verification

Full seat text (`:111`): *"**S3 — Re-author `rm -r` has no shape guard** (runbook :823-827); a mistyped `$PACK_ID` hitting a sibling pack's custody deletes it irreversibly, receipt-free."*
Citation: `sitting-packet-FINAL.md:163`. Seat's proposed WO-L8-8: *"governed `reauthor-clean` replacing raw `rm -r`"* (`:141`).

### (b) What changed since 2026-08-15
- **Partial, prose only.** The runbook re-author rule survived the re-cut and now carries a verify-first sentence and an explicit three-namespace enumeration — `window_runbook.md:1010-1020`: *"A reboot or any HEAD change voids the authored receipts. **Before re-authoring, first verify these are the exact three pack-specific T-0 namespaces and remove all three** so no no-clobber collision can masquerade as a retry:"* followed by `/bin/rm -r -- "$ARM_READINESS_CUSTODY_ROOT/$PACK_ID/arm_readiness.t0.sources" … arm_readiness.evidence … arm_readiness.t0.inputs`.
- Hardening delta vs the baseline: absolute `/bin/rm`, `--` end-of-options, and the "verify first" instruction. **No machine shape guard, no governed `reauthor-clean` subcommand, no receipt.** `grep -rn "reauthor|re-author" scripts/*.py scripts/*.sh` returns only `scripts/author_arm_readiness_evidence.py:78` (*"git rm -r -- … before re-authoring"*, a different tool).
- Off in the other direction: `rehearsal-operator-card.md` §11 has its own reset `rm -r` of the same three namespaces, also unguarded.

### (c) Candidate disposition for the seat
**STILL-OPEN.** The seat is adjudicating whether `/bin/rm -r --` plus a prose "verify first" is an acceptable disposition of an irreversible, receipt-free, `$PACK_ID`-interpolated deletion at 2am, when the registered remedy (WO-L8-8, a governed `reauthor-clean`) was never built.

### (d) Skeptical probes
1. `$PACK_ID` is sourced from `window.env`. Simulate a typo: does anything between the shell and the filesystem notice that the target is a *sibling* pack's populated custody?
2. Compare against the row's own no-clobber doctrine: `capture_t0_step.py:180-190` refuses to *replace* a file, then the runbook tells the operator to `rm -r` three trees by hand. Is that consistent?
3. A refused ARM leaves a REFUSE receipt occupying the namespace (seat §7, `arm_readiness_evidence_t0.py:1511-1517`), making re-authoring intentionally impossible. Does the `rm -r` delete that fence too, and thereby re-open a night the mechanism intended to end?
4. Is there any custody receipt or log of the deletion? If not, a post-hoc audit cannot distinguish a legitimate re-author from a cover-up.

---

## L8-S4 — Morning restore (E-16) before the magistrate finishes has no machine catch

### (a) Original finding (VERBATIM)
> - [should_fix] [L8] Morning restore (E-16) before the magistrate finishes has no machine catch

Full seat text (`:112`): *"**S4 — Morning restore-before-handback has no machine catch** (runbook :557-568; packet §3.5); two-tap ordering is purely procedural."*
Citation: `sitting-packet-FINAL.md:164`. Universe item 23 (`:36`): *"Behavior: morning two-tap restore ordering (E-15/E-18/E-16) | examined (procedural only)"*.

### (b) What changed since 2026-08-15
- **NO MACHINE CATCH ADDED.** The ordering is still prose: `window_runbook.md:623-637` — the restore checkbox *"After the window closes, meaning after `measurement_complete`, the whole-window verdict, and the backup, re-enable it: `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on`"* with the rationale *"The restore comes last because re-enabling automatic network time permits the system to slew the wall clock, and the verdict, backup, and close-out steps are still reading clock-anchored evidence and custody metadata. Wake the display, confirm `measurement_complete`, then hand back — **the restore is a separate tap after the magistrate's §9 and §11 steps**."*
- Close-out remains a written record, not a gate: `:637-638` *"Record in the close-out that automatic time was disabled, when it was disabled, and when it was restored"*; mirrored at `:1828`.
- The one thing that *did* change is that the restore vector is now covered by the installed D-127 fragment and was exercised as an EXIT trap in the shakedown driver (`2026-08-18-shakedown-first-light/05-driver-as-run.sh:19-22,66-67`) — which, note, restores **automatically on exit**, the opposite of the ordered "separate tap after §9/§11". That is a live divergence between the shakedown driver's behaviour and the runbook's rule.
- Renumbering caveat: the seat's "E-16" is old numbering. Current §5C uses E-4…E-9a/E-9b/E-9c/E-10; `grep -n "E-14"` over the runbook returns nothing.

### (c) Candidate disposition for the seat
**STILL-OPEN.** The seat is adjudicating an unrepaired procedural-only ordering gate, now with an added wrinkle: the only automation that touches the restore vector (the shakedown driver's EXIT trap) restores *immediately on exit*, which is precisely the premature restore S4 warns about.

### (d) Skeptical probes
1. Read `05-driver-as-run.sh:19-22,66-67`. Confirm the trap fires before any verdict/backup step. If a claim window ever reuses that driver shape, S4's hazard is realised by the tooling itself.
2. What reads clock-anchored evidence during §9/§11 and would actually be corrupted by an NTP slew? Name the artifact — if none, S4 may be over-stated; if some, it deserves a machine gate.
3. Is the close-out's disabled/restored timestamp pair machine-checked anywhere, or only prose (`:637-638`, `:1828`)?
4. The E-numbering in the seat report (E-15/E-16/E-18) no longer matches the runbook. Ask which document the operator holds and whether the ordering survived the renumbering intact.

---

## L8-S5 — In-horizon TOCTOU: post-authoring process starts are not re-probed at arm/verify/consume

### (a) Original finding (VERBATIM)
> - [should_fix] [L8] In-horizon TOCTOU: post-authoring process starts are not re-probed at arm/verify/consume

Full seat text (`:113`): *"**S5 — In-horizon TOCTOU** (design-bounded, `t0.py:45-47`): post-authoring process starts are never re-probed; the prohibition needs an explicit ABORT row in the recut packet."*
Citation: `sitting-packet-FINAL.md:165`.

### (b) What changed since 2026-08-15
- **Unchanged in code, by design.** `joulewise/arm_readiness_evidence_t0.py:47-50`: *"Live machine state can change between authoring and ARM consumption. Keep that unavoidable TOCTOU window bounded to the expected arm-sequence length."* → `_VOLATILE_EVIDENCE_VALIDITY_NS = 20 * 60 * 1_000_000_000`, `_NONVOLATILE_EVIDENCE_VALIDITY_NS = 6 * 60 * 60 * 1_000_000_000`. No re-probe was added.
- The prohibition is now stated more prominently in the runbook: `window_runbook.md:996-1002` — *"Eleven volatile evidence kinds carry a **20-minute monotonic horizon** beginning at E-9b. That is the operator's visible clock: do not start any new agent, browser, `caffeinate`, monitor, maintenance, or other polling process after authoring. Run ARM immediately, verify it, stop for Ed's inspection, and then invoke E-10."*
- And in the rehearsal card: `rehearsal-operator-card.md:95` (bolded) — *"After E-9b, eleven volatile evidence kinds have a 20-MINUTE monotonic horizon: start no new process and proceed immediately to ARM, verify, Ed inspection, then the one launcher invocation."*
- **The remedy the seat actually asked for — "an explicit ABORT row in the recut packet" — cannot exist: there is no recut packet** (B5).

### (c) Candidate disposition for the seat
**STILL-OPEN.** The seat is adjudicating whether prominent prose in two documents (one of them a scratch rehearsal card, neither of them the operator's night packet) discharges a design-bounded TOCTOU whose registered remedy was an ABORT row in a document that was never written.

### (d) Skeptical probes
1. Start a `caffeinate` between E-9b and ARM and run ARM. Does anything refuse, or does the receipt mint clean? That is the whole finding.
2. `_VOLATILE_EVIDENCE_VALIDITY_NS` is 20 min; the arm-receipt fuse is 5 min; Ed's inspection sits between verify and E-10 with no stated bound. Ask what bounds the inspection, and whether a careful Ed can blow the horizon by being careful.
3. The census probes that would catch a new process are the ones L8-N1/L9 say over- and under-match (`arm_readiness_evidence_t0.py:963-980`, `:1344-1360`). Even a re-probe would use a broken pattern — is WO-CENSUS-SEMANTICS (A4, BLOCKED on ED-Q-L9-3) a hard dependency of S5?

---

## L8-N1 — prewindow check 8's agent pattern omits claude/t3 and check 4 WARN-only without admin

### (a) Original finding (VERBATIM)
> - [nit] [L8] prewindow check 8's agent pattern omits claude/t3 and check 4 WARN-only without admin

Full seat text (`:116`): *"**N1** prewindow check 8 omits claude/t3 (observed passing with a live Claude session); check 4 WARN-only without admin."*
Citation: `sitting-packet-FINAL.md:166`. Twin at L9 should-fix (`:186`): *"prewindow_check.sh agent census misses claude / codex mcp-server / t3 — printed OK while three agent processes were live"*.

### (b) What changed since 2026-08-15
- **Check 4: repaired** — it no longer attempts a privileged clock read at all. `scripts/prewindow_check.sh:102-105`: *"# 4. Clock state is deliberately not read here. D-127 grants repository automation only the exact off/on writes; Ed records the prior state in interactive E-4 and E-5 performs the governed exact off enforcement."* → prints a NOTE. The "WARN-only without admin" condition is gone (fallout of the B3 route change).
- **Check 8: NOT repaired.** `scripts/prewindow_check.sh:148-156` at HEAD (identical on main):
  `procs="$(ps aux | grep -E "codex exec|codex-run|run_campaign|window-chain" | grep -vc grep)"`
  — still no `claude`, no `t3`, no `codex mcp-server`. The seat's observed failure (printing OK with a live Claude session) reproduces at the current head.
- The correct pattern exists elsewhere and was never back-ported: the T-0 author's agent probe uses `codex|claude|t3` (seat report `:98` calls it "correct and verified effective live"). The census work order that would fix it — **A4 `WO-CENSUS-SEMANTICS` — is BLOCKED on ED-Q-L9-3** per the brief's queue state.
- This matters beyond a nit: check 8's OK is what lets the B2 dwell loop keep counting clean seconds (`:179-197`).

### (c) Candidate disposition for the seat
**STILL-OPEN (half repaired).** The seat is adjudicating a surviving false-OK in the gate that now certifies the 600-second quiet dwell — the nit's blast radius grew when B2's repair made check 8 the dwell's admission test.

### (d) Skeptical probes
1. With a live `claude` session, run `scripts/prewindow_check.sh` and read check 8's line. Expect `ok  no agent or measurement process running`.
2. Then run `--wait` and watch whether the dwell counter accumulates 600 clean seconds on a machine with agents live. If it does, B2's repair certifies a contaminated machine.
3. Is the fix gated behind A4 (BLOCKED on ED-Q-L9-3), or is it a one-line regex change that no work order owns? A four-token regex edit sitting behind a blocked WO is a scheduling artifact, not a technical constraint.

---

## L8-N2 — E-14 do-not-return-before time is hand arithmetic at T-0

### (a) Original finding (VERBATIM)
> - [nit] [L8] E-14 do-not-return-before time is hand arithmetic at T-0

Full seat text (`:117`): *"**N2** E-14 do-not-return-before time is 2am hand arithmetic (6.28 h = 6 h 16.8 m); freeze a `date -v+377M` literal."*
Citation: `sitting-packet-FINAL.md:167`.

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND, and the anchor has dissolved.** `grep -n "E-14|date -v|377|6.28|do not return|do-not-return"` over `docs/phase_2/window_runbook.md` → **zero hits**. The E-numbering was re-cut to E-4…E-9a/E-9b/E-9c/E-10; there is no E-14 in the current runbook.
- The finding was anchored in the **FINAL arm packet** (`arm-packet-alpha-FINAL-20260813.md`), which was never recut (B5) and still contains the original hand arithmetic. So the nit is neither fixed nor findable in the repo — it lives only in the off-repo document nobody rewrote.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND.** The seat is adjudicating a nit whose home document (the stale packet) still exists unchanged and whose repository anchor no longer exists, i.e. it will silently ride into the night unless the successor packet is written.

### (d) Skeptical probes
1. Open `~/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md` and find the do-not-return-before arithmetic. Is it still 6.28 h?
2. Confirm the E-renumbering did not orphan other packet-anchored findings the same way (N3, S4, S5 all cite old numbering).

---

## L8-N3 — ED-session census pattern is substring-based and false-positive-prone (fails closed)

### (a) Original finding (VERBATIM)
> - [nit] [L8] ED-session census pattern is substring-based and false-positive-prone (fails closed)

Full seat text (`:118`): *"**N3** ED-script census is substring-based → spurious refusals beside any dev activity (fails closed; observed live)."*
Citation: `sitting-packet-FINAL.md:168`.

### (b) What changed since 2026-08-15
- **Indirect evidence of a related repair, no direct fix found.** The T10 operator run's defect harvest records a *different but adjacent* census defect and its discovery: `docs/run_reports/2026-08-18-t10-session.md:125` (commit `e5dc38a`) — *"`ed_session`: blanket `sudo -n /usr/bin/true` probe is **incompatible with the command-scoped NOPASSWD host config**"*. That is a real ed_session census finding from live execution, but it is not N3.
- I found no commit changing the ED-session census matching from substring to exact. Searched: `scripts/ed_session/` history, `grep -rn "pgrep"` patterns, and the L8/L9 census work order (A4 `WO-CENSUS-SEMANTICS`, **BLOCKED on ED-Q-L9-3**).
- N3's sibling defects at L9 (`arm_readiness_evidence_t0.py:963-980` MAINTENANCE_CENSUS unpassable; `:1344-1360` PROCESS_CENSUS browser/monitor over-match) are the explicit payload of A4 and remain blocked.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND** (fail-closed, so no false-launch risk; it costs nights, not correctness). The seat is adjudicating a nit whose owning work order (A4) is blocked on an Ed-qualification row, alongside two L9 blockers of the same class.

### (d) Skeptical probes
1. Run the ED-session census beside an ordinary dev shell and count spurious refusals.
2. Is ED-Q-L9-3 (quiet-state fixture) closed? The brief's queue state says A4 is BLOCKED on it; agent evidence says the quiet census was *"Captured 23:51 by the lead… over-match findings confirmed as fixture ground truth"* (`docs/run_reports/2026-08-18-t10-session.md`). If the fixture exists, why is A4 still blocked?
3. Ask whether N3 and L9's two census blockers are one defect class that should be adjudicated together rather than split across two seats' severity tiers.

---

## L8-TRAILER — Terminal-review-trailer producer gap (refuter discovery; SINGLE-LENS then CLEARED)

### (a) Original finding (VERBATIM)
Not in §3 — discovered by the B-execution refuter. `refuter-outputs/sol-refuter-B-execution.md:232`:
> One further end-to-end obstacle surfaced: baseline commit `ac3fe1d` lacks the three `JouleWise-Terminal-Review*` commit trailers demanded at [918–930](…/joulewise/arm_readiness_evidence_t0.py:918). The integrated repair must establish an operational producer for that terminal-review evidence too.

Also `refuter-outputs/refuter-verdicts.md:115`: *"NEW DISCOVERY: baseline ac3fe1d lacks the three JouleWise-Terminal-Review* commit trailers the T-0…"*
Post-verdict adjudication: **labelled SINGLE-LENS at the sitting, then CLEARED.** `council-verdict.md:46-49` Disposition 5 recorded it single-lens and ORDERED a second distinct-lens refuter. The ADDENDUM (`:121-131`) discharges it: *"The ordered second-lens refuter (refuter-outputs/sol-refuter-singlelens.md, Sol xhigh, execution lens) confirmed all four single-lens claims: … and the terminal-review-trailer gap (no producer; remedy = a lead-owned terminal-review attestation step whose commit the superseding manifest pins, with the measurement checkout and T-0 author operating at the attested commit — folds into WO-T0-PRODUCER + the Phase-3 supersession). Their work orders now implement without further verification debt. Disposition 5's condition is discharged."* Second-lens detail at `refuter-outputs/sol-refuter-singlelens.md:46,149,166,247`.

### (b) What changed since 2026-08-15
- **The consumer was moved and hardened; the producer is still a human act with no tooling.** `scripts/capture_t0_step.py:288-316` `_verify_terminal_review` now runs at **context load**, i.e. at E-4, the very first capture — before any of the nine inputs exist. It requires `readiness.reviewed_main(pack_root)` to be `clean` **and** `exact_match`, then parses `git show -s --format=%B HEAD` for exactly three trailers matched by `r"(JouleWise-Terminal-Review(?:-Tree-Oid|-Pack-Sha256)?):\s*(\S+)"` and compares them to `{"JouleWise-Terminal-Review": "PASS", "-Tree-Oid": <HEAD^{tree}>, "-Pack-Sha256": <pack_sha256>}` — any deviation raises `evidence_author_t0_capture_terminal_review_missing` (`:312-316`). Registered code at `:91`. Called from `_load_context:490`. **On main** (`a61ac92`).
- **No producer script.** I found no tool that creates the attestation commit. The remedy the addendum names — *"a lead-owned terminal-review attestation step whose commit the superseding manifest pins"* — is a lead procedure; the only trace of it in an operator document is `docs/process/rehearsal-operator-card.md:3`: *"Ed's terminal-review commit advances its HEAD"*, and `:the Part A dry-run row` is marked *"BOUNDARY-PROVEN (requires Ed's terminal-review commit first)"*.
- The second half of the remedy — *"the superseding manifest pins [that commit]"* — is **Phase 3** work (`council-verdict.md:104-107`), not started. `docs/process/audit-baseline-manifest.json` is still the 2026-08-15 baseline.

### (c) Candidate disposition for the seat
**STILL-OPEN.** The seat is adjudicating a gap whose *consumer* is now strict and early-firing (E-4 refuses without the three exact trailers) while its *producer* remains an unwritten lead procedure and its manifest-pinning half is unstarted Phase-3 work — i.e. the hardening moved the failure from the T-0 author to the first capture, without creating the thing that makes the check passable.

### (d) Skeptical probes
1. `git log -1 --format=%B` on the head you intend to arm from. Does it carry all three trailers? On `main` (`0099382`) and on `79a4cd0` it does not — check.
2. Who writes the attestation commit, with what checklist, and what does "PASS" attest to? A trailer whose production has no procedure is a rubber stamp with a regex.
3. `_verify_terminal_review` also requires `reviewed_main` `clean` and `exact_match` — so the measurement checkout must equal local **and** origin main. Reconcile with freeze-0003 living on `impl/r2-s0-mint-resolver`, unmerged. Can E-4 pass at all while the re-freeze is branch-only?
4. The trailer binds `HEAD^{tree}` and `pack_sha256`. Any commit after the attestation (including a RUN_STATE bookkeeping commit) invalidates it. What stops routine commits from voiding the night?
5. Phase 3's supersession is the other half of the remedy. Is it scheduled before the READY-candidate sitting or after?

---

## L8-COVERAGE — 21/24 evidence universe

### (a) Original finding (VERBATIM)
`sitting-packet-FINAL.md:33` row: `| L8-OPERATOR-RECOVERY-HUMAN-FACTORS | GATING | NOT_READY | 21/24 | 7 | 5 | 3 | 8 | 6 | 4 |`
Seat's own statement (`seat-reports/L8-…-report.md:38`): *"**Coverage: 21 / 24** examined; items 7 and 12 partial, item 24 unexecuted (rows below). Unexecuted obligations listed in §5."*
The three gaps: **item 7** Runbook §10/§11/§12 morning + failure-playbook operator surface — *"partial (ordering read; §10 rows are L2/L10 primary)"*; **item 12** `scripts/quiet_mac_prep.sh` — *"static only (live run needs sudo/display)"*; **item 24** ED-session live sudo paths (ABBA arms, supervised sampler) — *"NOT executed (no sudo) → ED-QUALIFICATION"*.
Post-verdict adjudication: the verdict makes coverage a **standing packet element**: *"every seat's evidence universe was self-nominated, and the one denominator adversarially tested fell. Closing all listed work orders does not entitle READY; the READY-candidate re-audit must re-enumerate every universe independently and run the adversarial coverage attack as a standing packet element."* (`council-verdict.md:23-27`). L2's denominator fell from 15/16 to a real universe of 251 (`sitting-packet-FINAL.md:387-390`) — L8's 24 has never been adversarially tested.

### (b) What changed since 2026-08-15
- **Item 24 → CLOSED as ED-Q-L8-3.** `docs/run_reports/2026-08-18-t10-session.md:105-106`: sampler checklist *"PASS — cadence mean 1.0128 s, zero orphans"*; rail probe *"ABBA executed; ANE delta exactly 0.000000000 J … Documentation-grade"*. Custody `~/JouleWise-window-custody/ed-qual-20260817/`. **On main** (`786183a`).
- **Item 12 → still static.** ED-Q-L8-4 (*"live `quiet_mac_prep.sh` run to confirm its three OK literals … match what the T-0 author's `_quiet_capture` requires verbatim"*, `sitting-packet-FINAL.md:198`) has **no row anywhere**: not in the T10 qualification ledger (`2026-08-18-t10-session.md:100-110`), not in `ed-morning-packet-2026-08-18.md:105-126`, not in `TASK_QUEUE.md`, not in `docs/process/state_kernel.json`. It is the one ED-QUAL row in this seat that was never even tracked.
- **Item 7 → no re-audit.** No L8 re-audit exists: `grep -rn "WO-L8-|L8 re-audit|L8-REAUDIT"` over `TASK_QUEUE.md`, `docs/process/state_kernel.json`, `RUN_STATE.md` → **zero hits**. Only `WO-L2-REAUDIT` was chartered and delivered (`docs/process_traces/2026-08-15-l2-reaudit/`, `0f886d3`).
- **The seat's own eight work orders were never registered.** WO-L8-1 … WO-L8-8 (`seat-reports/L8-…-report.md:141`) appear in no queue or kernel row; their content was folded into the council's WO names (WO-T0-PRODUCER, WO-LAUNCH-BINDING, …), which means WO-L8-5 (recut packet) and WO-L8-8 (governed `reauthor-clean`) have no owner at all.
- **The denominator itself is unchanged and untested.** The universe still enumerates the artifacts as they stood at `ac3fe1d`: e.g. item 11 *"scripts/prewindow_check.sh (199 ln)"* and item 14 *"joulewise/arm_readiness_evidence_t0.py (2043 ln)"*. At HEAD those files are 199+ and **2090** lines respectively, and an entire new artifact — `scripts/capture_t0_step.py` (1060 lines) — plus `scripts/launch_window.py` (304), `docs/process/rehearsal-operator-card.md` (123), `scripts/ed_session/build_rehearsal_env.sh` (183), and `scripts/joulewise-network-time.sudoers` did not exist when the universe was drawn. **A 24-item universe cannot cover a surface that has grown by ~1,700 lines of new operator-path code.**

### (c) Candidate disposition for the seat
**STILL-OPEN / ED-ROW.** The seat is adjudicating a denominator that (i) was self-nominated and never adversarially attacked as the verdict requires of a READY-candidate sitting, (ii) predates roughly 1,700 lines of new operator-path artifacts that must now be *in* the universe, and (iii) still carries one partial (item 7), one static-only (item 12, whose ED-QUAL row ED-Q-L8-4 exists in no tracker), against one genuine closure (item 24 / ED-Q-L8-3).

### (d) Skeptical probes
1. Re-enumerate independently. Ask for the L8 universe **at the current head** and check whether `scripts/capture_t0_step.py`, `scripts/launch_window.py`, `scripts/joulewise-network-time.sudoers`, `docs/process/rehearsal-operator-card.md`, and `scripts/ed_session/build_rehearsal_env.sh` are in it. If the seat re-presents 24 items, the denominator is stale by construction.
2. Run the L2-style attack on the L8 denominator: what is the *real* universe of operator-path artifacts and behaviours? L2's fell from 16 to 251.
3. ED-Q-L8-4 exists in no tracker. Who owns it, and does the charter's "all ED-QUALIFICATION rows closed with evidence" (`RUN_STATE.md:4054`) bind a row nobody records?
4. WO-L8-5 and WO-L8-8 have no queue row. Ask which registered WO owns the recut packet and the governed `reauthor-clean`, and if none, whether the row can clear with two of its own eight remedies unowned.
5. Item 7 (§10/§11/§12 morning + failure playbook) was deferred to L2/L10 as "primary". Confirm those seats actually audited the operator-facing §10 refusal rows; the seat's unexecuted-obligation 4 flags *"packet O-9's missing one-page extract"*.

---

## ROW-LEVEL OPEN ITEMS

1. **L8-B5 — successor/recut arm packet: NO REPAIR AT ALL.** `~/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md` is unchanged since 2026-08-13 (mtime Aug 13 20:21) and remains the only arm packet in existence. `L8-B5` appears **zero** times in `RUN_STATE.md`. The rehearsal operator card is scratch-only, non-claim, missing the 5-minute fuse and the re-author rule, and is pinned to a *starting* commit (`build_rehearsal_env.sh:32` asserts only ancestry), so it structurally cannot satisfy Opus W8's "exact reviewed head". Searched: full-repo greps for `arm-packet`/`FINAL-2026`/`recut`/`successor arm packet`, `docs/process/`, `RUN_STATE.md`, and the off-repo custody directory.

2. **ED-Q-L8-2 dress rehearsal — NEVER EXECUTED, not even partially, and it has fallen off the plan of record.** `~/JouleWise-window-custody/ed-qual-20260817/rehearsal` does not exist (the builder refuses to reuse a root, so its absence is a one-to-one proxy). `docs/process_traces/2026-08-18-shakedown-first-light/05-driver-as-run.sh` is the D-139 **nonclaim** shakedown — no `capture_t0_step.py`, no `author_arm_evidence_t0.py`, no `generate_arm_readiness.py arm/verify`, no `launch_window.py`; its `sleep 660` belongs to a quiet-state baseline, not E-7b. Status of record: `docs/run_reports/2026-08-18-t10-session.md:110` *"| **Dress rehearsal** | **OPEN** …"*; `ed-morning-packet-2026-08-18.md:126` *"**OPEN: the dress rehearsal (item 4) only.**"*; T10 says it was **unblocked** 2026-08-18 morning and then never run. **The current RUN_STATE blocks (T15-PREP `:14-58`, T14-GO `:59-120`) do not mention it at all**, while `RUN_STATE.md:4054` and D-149 condition (1) both require ED-QUALIFICATION rows closed. **Consequence: no part of the B1/B2/B6/B7 repair chain has ever been executed end-to-end by anyone.**

3. **ED-Q-L8-4 is untracked.** The live `quiet_mac_prep.sh` three-OK-literals row appears in no ledger, packet, queue, or kernel. Universe item 12 remains static-only.

4. **L8-S2 (5-minute arm-receipt fuse) — NO-REPAIR-FOUND.** Still `validity_ns: int = 300_000_000_000` at `joulewise/arm_readiness.py:6101`; zero hits for any plain-language equivalent in `window_runbook.md`, `rehearsal-operator-card.md`, or `alpha_arm_readiness.md`.

5. **L8-S1 (inline ARM_CONTEXT) — NO-REPAIR-FOUND.** `scripts/generate_arm_readiness.py:65` still refuses a path; the runbook (`:1031`) still mandates the inline object — now while the producer writes the authenticated `arm-context.json` to custody.

6. **New B6-class defect, documented rather than fixed:** `window_runbook.md:1189-1192` requires `window.env` to bind `ARM_RECEIPT` and `LAUNCH_MANIFEST`; `scripts/capture_t0_step.py:102-130,259-266` refuses them as `unknown` against an exhaustive 25-key set. Self-recorded at `docs/process/rehearsal-operator-card.md:5` (*"this differs from the runbook chain wording"*). Both sides are on `main`.

7. **B4-class staleness reintroduced by the successor re-freeze:** freeze-0003 binds `_v3` @ `/Users/edr/JouleWise-measurement-20260818`; runbook §4's example binds `_v2` @ `/Users/edr/JouleWise-measurement-20260813`; the rehearsal card binds `_v2` @ `…20260818`. Three documents, three bindings.

8. **The re-freeze and D-149 are BRANCH-ONLY.** `5e38f1e`, `eb7f6c6`, `94dc3b3`, `8b2b021` (freeze-0003 family + S5 table), `0e96dbb` (D-149), `d59d36f` (D-148) are on `impl/r2-s0-mint-resolver` and **not on `main`**. Any L8 disposition resting on the `_v3` packs or on D-149 rests on unmerged state.

9. **The terminal-review trailer has a strict consumer and no producer.** `capture_t0_step.py:288-316` refuses at E-4 without three exact trailers; no script creates them; the manifest-pinning half is unstarted Phase-3 work. Neither `main` (`0099382`) nor HEAD (`79a4cd0`) carries the trailers.

10. **B7's own documents say launch is NO-GO.** `window_runbook.md:1076-1088` (*"not current authority to launch … every D-117 physical launch remains NO-GO"*) and `TASK_QUEUE.md:536` (A1 `READY [AGENT]`, *"remaining: stage 4 successor flag inside the transaction. Launch stays NO-GO"*). Calibration-side stage 2 is parked at `e22e658` on an unmerged branch. `TASK_QUEUE.md:491-499`'s hand-authored checkpoint is stale against the A1 row it sits above.

11. **L8-N1's surviving half now guards the B2 repair.** `scripts/prewindow_check.sh:150`'s pattern still omits `claude`/`t3`/`codex mcp-server`, and that same check gates the 600-second continuous-clean dwell. The fix appears to be a regex edit sitting behind A4 `WO-CENSUS-SEMANTICS`, which is BLOCKED on ED-Q-L9-3.

12. **Three merged docs still describe D-127 as not installed:** `docs/phase_2/alpha_arm_readiness.md:126-129` (*"STAGED BY #152; INSTALL EVIDENCE PENDING"*, *"OPERATOR EVIDENCE PENDING"*), `docs/process/ed-batch-packet.md:53`, `RUN_STATE.md:541-542,621`. The install happened 2026-08-17 17:55. Also unverified: the **installed bytes' digest** (root-only read).

13. **The seat's eight work orders (WO-L8-1…8) were never registered anywhere**; WO-L8-5 (recut packet) and WO-L8-8 (governed `reauthor-clean`) consequently have no owner. No L8 re-audit was chartered (only WO-L2-REAUDIT).

14. **The 21/24 denominator was never adversarially re-enumerated**, despite the verdict making that a standing READY-candidate packet element — and it predates ~1,700 lines of new operator-path artifacts (`capture_t0_step.py` 1060, `launch_window.py` 304, `rehearsal-operator-card.md` 123, `build_rehearsal_env.sh` 183, `joulewise-network-time.sudoers`).

15. **Assembler-side caveat on the reading tree:** the worktree is at `79a4cd0`, not the `d10881b` named in the brief, and it is **missing 10 commits present on `main`**. I verified that the eight L8-relevant files are byte-identical between `main` and HEAD except for D-079 constants in the runbook, but a seat re-checking any *other* path should re-derive its own main/HEAD position.
