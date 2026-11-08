# W1 smoke kit: Sol/Opus agreement report

Authority: RUN_STATE 220. Sol and Opus each build the kit independently, the builds are compared and
agreed, and then the lead rules. The two builds:

- **Opus (Claude Opus 5.5):** `align/2026-11-08-w1-smoke-opus` @ `7146444ed`, documented in
  `docs/align/v4/W1-SMOKE-opus.md`. I wrote it before looking at the Sol branch.
- **Sol (Sol 6.1):** `align/2026-11-08-w1-smoke` @ `035a8c7fe` (implementation `8fd55af2a`), documented in
  `docs/align/v4/W1-SMOKE.md` and `docs/run_reports/2026-11-08-w1-smoke.md`. Sol declares its own status
  as **PARTIAL / NOT CLEARED FOR MBP LAUNCH**: it has no native reduced-window builder and no automatic
  fault orchestration.

Both builds start from `align/2026-11-08-v4-r11` @ `05b6d04cb`. Opus ran both builds on the Air:
- Opus: `--next w1` and `--next r1`, and the two test modules (26 + 17 tests, all OK);
- Sol: `scripts/align_v4_prequal.py --offline --w1-smoke-only --stage w1`, and its three test modules
  (all OK).

No hardware was used and no restricted path was read.

## 1. Coverage, check by check (Part A: Air PREQUAL)

| Required item | Opus | Sol | Assessment |
|---|---|---|---|
| Production arm CLI with all required args | `arm-cli`: help and argparse enforcement, then the full production `install()` through `_arm_and_install` and `h.install` with a fake installer. 11 cases: control, missing/edited/pre-R12 triage, missing/stale/future top-up, OBC, disk image, charging, powermode. | `w1-arm-cli`: argv forwarding and an omission check per flag, then `_arm_and_install` for 5 cases (ok, missing top-up, OBC, edited status, volume). Stops at the `pilot.install` boundary. | **Both pass.** Opus goes deeper: it covers `install()` (session-start restore, host lock, terminal-session refusal, W1 disk check) and the real `h.install` census and t0 guard. Sol's per-flag omission loop is neat. |
| Triage packet integrity | `triage-staleness` FAIL. A well-formed stale packet admits (G1). | `w1-triage-integrity` FAIL. A stale packet admits, and **edited basis text with valid statuses also admits** (no byte digest). | **Agree on G1.** Sol has the extra edited-bytes observation; adopt it. |
| Receipt against the candidate | `receipt`: validator self-test on a clean clone (an exact receipt is admitted; a digest mismatch and a working-bytes drift are refused), then the committed receipt (pending). It names the 4 bound artifacts not yet committed. | `w1-executed-receipt`: **recomputes the static import closure** from `endpoint.py`, `run_night.py` and `align_v4_session.py`, and requires it to sit inside `ARTIFACTS` (it does today). Then validates the receipt, requires `receipt.commit == candidate`, and requires a clean checkout. FAIL (pending). | **Complementary.** Sol's closure-coverage check and explicit candidate equality are real additions. Opus's self-test proves the validator rejects drift. Adopt both. |
| Fixed-8 `calibration_stop` on the planned manifest | `calibration-stop` PASS. Uses the protocol's planned C1-C8 (7/7 per pair): continue ×8 then complete, zero-capture, escalation, provisional, insufficient, a 9th window, loss of two whole windows (completes), loss of three (insufficient), and 5 triage-integrated arms. `cal-escalation-exit` FAIL (MED-2(a) deadlock). | `w1-calibration-series`: a lead-supplied, source-hash-bound **series projection** file (W1 → C1-C8 → test, 7/7). The same predicate cases. FAIL today because the projection is absent. | **Agree on the predicate.** Sol binds the check to a frozen manifest file, which is better once one exists. Opus can run now and also catches MED-2(a). Merge: Opus cases, plus Sol's projection binding when the lead freezes the manifest. |
| R1 → W1 chain on a lane-shaped record | `r1-w1-chain`: the CLIs as `R1-TO-W1-CHAIN.md` writes them, in a clean clone of the candidate, record installed, then the real `kit --check`. FAIL with **G2**: the runbook omits kit regeneration, so `--check` reports drift. | `w1-r1-chain`: in process, with `kit.generate` run **before** `--check` and readiness patched to synthetic. PASS, plus a negative (a tampered member is caught by `--check`) and a bad count export refused by the CLI. | Sol's check verifies the code. Opus's check verifies the operator runbook as written, and that is what found G2. Keep both. |
| KM003C through the HAZARD_PACK launcher, fake meter, per-member DC-missing flag | `km003c-launch` PASS: the real driver with a **live sample-writing** stand-in meter, clean and SIGKILLed mid-chain. Restart into stream-002, custody hashes, the straddling member reads `missing`/`meter.*`, the post-restart member reads `available`, rails unchanged, production argv, `require_enabled`. `km003c-crash-radius` FAIL (**G3**). | `w1-meter-launch` PASS: the real driver with `FAKE_METER` (header and trailer only, no samples) and the production argv. Then `capture_member` on a synthetic stream truncated *with* a trailer. | **Both pass the stated item.** Only Opus's live killed stream finds G3: a crashed reader voids DC for every earlier member of its stream (no trailer, so no offset). Sol's truncated fixture keeps its trailer and cannot see this. |
| W1 plan `window_max_s` sizing | `w1-window-max`: the W1 template filled at the planning worst case. Validator = `plan_inputs.window_max_s` = b5 formula (44,640 s). Caps, L1 fit, and **no `wait_outside_os_batch` in the W1 executed closure**. PENDING until `w1_plan.json` is committed. | `w1-window-deadline`: a general validator over an operator-supplied `smoke_deadline_projection` (segments × attempts, plus 11,164 s per possible batch encounter, plus bracket/close/harvest). Applies the 67,371 / 96,427 s floors **only** to R1. FAIL today because the projection is absent. | **Complementary.** Opus proves W1's own sizing code paths agree and that W1 has no hidden wait. Sol's validator is the right tool for R1 and D windows whose plans have segments and retries. Adopt both. |
| WP22 synthetic W1 dry run in full | `wp22-dry-run` FAIL: `JW_WP22_FULL=1` module (`FAILED (errors=2)`) plus the cold-review witness. | **Not covered.** | **Sol misses** the fault that motivated this kit (HIGH-1). |
| "An arm route exists end to end" for the next measurement | `arm-route`: `configs/align/v4/arm_routes.json`. R1 FAILs and names item 218; W1 PASSes, with 7 steps' entry points answering. | **Not covered.** | **Sol misses** the other motivating fault (item 218). |
| Smoke kit pre-qualified on the Air | `smoke-kit` PASS: production `measurement_view` plus reduction plus `chain.stage_plan`, and 6 of 7 fault expectations against the production arm. | Parser and recorder unit-tested; no pre-qualification of a native recipe, because none exists. | Opus only. |
| One command, PASS/FAIL table, non-zero exit | `scripts/align_v4_w1_prequal.py --next {r1,w1}`. Probes run in parallel processes. Each check has a `gates` stage; a FAIL of a later-gate check is shown but does not block; `--waive` records a waiver. | `scripts/align_v4_prequal.py --offline --w1-smoke-only --stage w1`, integrated with the existing prequal (implementation hashes, scope field). Exit 1. | Both meet the brief. Sol's integration into the existing runner is tidier for the magistrate rule; Opus's gating model is needed so an R1 arm is not blocked by W1-only debt. |

## 2. Faults each build catches or misses (state at `05b6d04cb`)

| Fault | Opus | Sol |
|---|---|---|
| WP22 dry run red (cold HIGH-1) | **catches** | misses |
| No R1 arm route (item 218) | **catches** (`--next r1` FAIL) | misses |
| Stale but well-formed triage packet (G1) | catches | catches |
| Packet bytes edited with valid statuses (no digest) | misses | **catches** |
| Escalation deadlock, no lead-ruling row (cold MED-2(a)) | **catches** | misses |
| R1→W1 runbook omits kit regeneration before `--check` (G2) | **catches** | misses (regenerates itself) |
| KM003C crash voids DC for earlier members of the stream (G3) | **catches** | misses |
| Executed module missing from the receipt artifact set | misses | **catches** (passes today) |
| Receipt bound to a different commit than the candidate | partial (self-test binds HEAD; committed receipt pending) | **catches** explicitly |
| R1/D deadline sized from a stale figure (items 215/216 class) | W1 only (code-path agreement; no batch wait in the W1 closure) | **catches** for any plan given a segment projection |
| Pending registration inputs, R0/R1 placeholders, U3 stop | catches (kit-ready, receipt) | catches (receipt) |
| A required arm flag dropped, or a refusal path broken | catches (11 cases through `h.install`) | catches (5 cases to the installer boundary) |

## 3. Part B: native smoke

| Aspect | Opus | Sol |
|---|---|---|
| Executable today | **Yes**, one detached command (`align_v4_w1_smoke.py run --detach`), then `parse`. Needs a W1-ready kit, which means it runs after registration and before the W1 arm. | **No**, by its own statement. It provides a checklist, a create-once transcript recorder with bounded process-group timeouts, a teardown recorder and a 9-case parser. The builder and adapters are blocked on two NEEDS_RULING items. |
| Reduced window | Production `align_v4_session.prepare` with a seam that reduces the session-local view pack via `b6.smoke.reduce_tree`. Keeps a 1.5B NEG-8 reference and W1 ordinal 1. | Recommends the `b6.smoke` isolated-copy reduction too; not built. |
| **Ledger isolation** | **Defect, found from Sol's doc.** `measurement_view` links the checkout's `runs/` directory, so the smoke's bracket reservation and calibration captures would append to `runs/calibration_observation_ledger.jsonl`. Its physical head would then move past the committed pin, and the next production prepare (W1 itself) would refuse with `calibration_ledger_head_mismatch` until the pin is advanced (`joulewise/b5/plan.py`). | **Correct:** do not use `measurement_view`; copy the ledger and head pin with distinct inodes (`b6.smoke.copy_ledger`). |
| Arm fault attempts | 7 automatic production-CLI attempts on disposable sessions whose plan copy has a past t0. The installer cannot be reached even if an arm admits. Teardown is automatic (clone removed; the dmg detached and verified gone). 6 of 7 are pre-qualified on the Air. | Manual: the operator runs each attempt through the recorder. No guard keeps an admitting arm away from the installer. |
| CPU contender | In window: `yes` for 45 s, out of tree, inside the anchor's request. Expected flag: `contention.request_overlap`, checked with the production `monitor.member_findings`. | A separate `run_night --dry-arm` expected to **refuse for contention**. **Likely wrong.** The arm dwell refuses only if 180 s of clean intervals never appear within 2,700 s, so a 30 s contender delays READY and the dry arm then returns GO. The dry arm also refuses at the agent census while an agent is alive (`driver.dry_arm`). |
| Meter kill | In the same window, during the first member, so the W1 member runs in the restarted, trailer-closed stream. The parser requires the killed member to read DC `missing`/`meter.*` and the W1 member `available`. | A separate 15 min window, killing the reader identified from the journal. |
| Terminal and finalize | `night/result.json`, then the launchd job gone (B1 latch), then a sha256 custody inventory. | Adapter receipts proposed, not implemented. |
| Wall time | Estimate 36-41 min for one detached run. Parser FAILs above 2,700 s. Not yet measured natively. | 45 min of targets, including two separate windows (15 + 15 min). Not runnable. |

## 4. Wall time

- **Part A on the Air:**
  - Opus: 21-36 s for 13 checks with 6 jobs today. WP22 fails fast now; when green, the full WP22
    module adds about 3-6 min.
  - Sol: 13 s for 7 checks.
- **Part B on the MBP:** Opus is about 36-41 min estimated, for one run. Sol is 45 min of targets and
  not runnable.

## 5. Recommendation: one merged kit

**Base it on the Opus build.** It is the only one that runs end to end, and its Part A covers both
faults that motivated the kit. Port these pieces from Sol:

1. **Executed-closure coverage** (`w1_prequal.closure`) and the explicit `receipt.commit == candidate`
   and clean-checkout assertions, both into Opus's `receipt` check.
2. **Packet byte-binding witness** (edited basis text with valid statuses), folded into
   `triage-staleness`. Both builds agree that the fix belongs to the lead, as a production schema change:
   bind `previous_record_sha256` (or the commit) and the packet digest into the arm record, and check
   them at arm.
3. **Segment-projection deadline validator** (`validate_deadline`), added as a `deadline` check. It
   requires an installed-plan projection for `--next r1` and for D windows. The R1-only floors stay R1-only.
4. **Series-projection binding** for `calibration-stop`, as soon as the lead freezes a series manifest.
   Until then, keep Opus's protocol-planned C1-C8.
5. **Integration into `scripts/align_v4_prequal.py`**, Sol's style: one magistrate rule, implementation
   hashes and a scope field. Keep Opus's per-check gate/blocking semantics and waivers, so W1 debt does
   not block an R1 arm.
6. **Native ledger isolation (required before any native run).** Replace Opus's view seam with a
   `b6.smoke.prepare`-style isolated clone:
   - a `copy_ledger` copy with distinct inodes, and a reduced tree committed in the clone;
   - the kit directory unchanged, so `kit.generate(check=True)` still passes;
   - the production `align_v4_session` arm and install still run against that clone.

   Re-run `smoke-kit` against the new builder.
7. **Native discipline:** Sol's create-once transcripts and bounded process-group timeout, for every
   command the runner spawns.
8. **Contender observable:** keep Opus's in-window `contention.request_overlap`. Drop the dry-arm
   contention refusal.
9. **File ownership:** both builds use `joulewise/align/w1_prequal.py`, `w1_smoke.py` and
   `tests/align/test_w1_{prequal,smoke}.py`. Merge as one owner (Opus files), port Sol's functions, and
   keep `tests/align/test_w1_smoke_paths.py` as Sol's in-process probes.

**Lead rulings needed:**

| Item | Both builds' view |
|---|---|
| Native W1 smoke may use a labelled, reduced, isolated scaffold | Both recommend yes |
| Triage freshness and digest binding (G1 plus edited bytes) | Production change; keep the check red until installed |
| MED-2(a) lead-ruling row | Open since the cold review |
| G2 runbook fix | Add `python3 scripts/align_v4_kit.py` between steps 5 and 6 of `R1-TO-W1-CHAIN.md` |
| G3 | Implement the documented monitor-journal offset fallback in `km003c.capture_member`, or record that a reader crash voids DC for its whole stream (a SECONDARY channel, but Ed's rule analyses it for every member) |

**Use now:**
- Before arming R1, run Opus Part A with `--next r1`. It blocks only on `arm-route` until the ruled R1
  route is declared in `arm_routes.json`.
- Do not run Part B natively until item 6 is merged.

## 6. Lead rulings and the merged kit (2026-11-08)

The lead adopted the recommendation. The single merged kit is on `align/2026-11-08-w1-smoke-merged`
(documented in `W1-SMOKE.md`). It is merged onto `align/2026-11-08-v4-r11` @ `2cce80ede`, which already
carries the MED-2(a) `lead_rulings` rows, the packet `record_commit` check, the WP22 fix and the
strict-tier receipt work.

| Item | Done |
|---|---|
| Sol ports | Executed-closure coverage plus receipt commit (as an ancestor, with a clean checkout); edited-packet bytes (`triage-edited-bytes`); segment deadline (`deadline`); series binding (`series-manifest`); bounded process-group commands and create-once transcripts in the native runner. |
| One command | `scripts/align_v4_prequal.py --w1-next {r1,w1}`. `scripts/align_v4_w1_prequal.py` is removed. |
| Reduced labelled `smoke` window | Approved and kept. |
| Isolation (HARD) | `w1_smoke.isolate` (clone, `copy_ledger`, own `runs/` and custody, base-interpreter venv) plus `isolation_violations` before every arm, and `IsolationTests`. The do-not-run note is removed. |
| Contender | Sol's dry-arm refusal is dropped. The in-window `contention.request_overlap` is required. |
| G1/G1b/G2/G3 | Handed to the v4 fixer. The checks are written as behavioural properties, so they go green on the fix: G1 (C2 packet refused after C3), G1b (an edited copy of the committed packet refused), G2 (the runbook's shell block regenerates before `--check`), G3 (a pre-kill member keeps DC). |
| Opt-in audit | The base launcher check is semantic (green against `origin/main`). The `optin-required` WARN row lists 134 opt-in-only required tests; 14 are run here (WP22). |
