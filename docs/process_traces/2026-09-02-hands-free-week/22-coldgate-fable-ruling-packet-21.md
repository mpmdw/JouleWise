# Cold-gate ruling, packet 21 (third convening) — Fable seat

Convened 2026-09-04 06:10 PDT as detached `claude -p` in worktree `feat/2026-09-04-packet-21`. Single foreground session; no subagents, installs, email, or claude/codex started. One harness-forced background move is disclosed under Executed.

## 1. Contamination disclosure

Auto-loaded at launch: `~/.claude/CLAUDE.md` (global rules), `./CLAUDE.md` (project notes), and the memory index `~/.claude/projects/-Users-edr-code-JouleWise/memory/MEMORY.md` (one-line pointers). I used none of them as authority. I did not read CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md, memory files, or any narrative state document. A git log line naming commit d1133538 was visible at launch; I did not open it.

## 2. Digests and validator

| Item | Expected | Observed (shasum -a 256) |
|---|---|---|
| charter `docs/process/coldgate_charter.md` | 099de884…c95d81 | 099de884…c95d81 MATCH; registry line 16 at a6e9edde carries the same value |
| packet `21-coldgate-packet-watchdog-v3.md` | 177d4359…0be6e2 | 177d4359…0be6e2 MATCH |

Validator: `scripts/validate_gate_packet.py …` with both expected digests → `"result":"PASS"`, rc 0, all 43 exhibit digests observed == expected, manifest sha256 7c6f54bb…8442, schema coldgate-validator-receipt/v2. All 43 exhibits are byte-identical to blobs at pinned head fdbb840c (`git hash-object` lookup: code under `scripts/`, `tests/`, `joulewise/night_plan_writer.py`, docs under `docs/process/`).

## 3. Executed (scratch worktree `/private/tmp/coldgate21-85215` at fdbb840c; temp custody roots only)

| # | Probe | Result |
|---|---|---|
| T1 | six named modules, `python3 -m unittest` | 184 tests OK in 28 s (packet §5: 182; +2 drift, NIT) |
| S1 | real `tick` CLI: valid v2 + golden retired-v1 + torn (40 %) + missing `measurement_head` | rc 0, `HOLD_UNSAFE`, reason names torn and missing paths, not v1; one `plan_retired_v1` event; no `attempts/` |
| S2–S4d | v1-label+v2 keys; future-authored; golden minus a key; v2-label+v1 keys; golden plus a key; chmod-0 file | all `HOLD_UNSAFE` malformed/unreadable, no attempts |
| S5/S6 | positive control valid-only; golden v1 only (dry-run) | `HOLD_CENSUS` (my own session in census) / `LAUNCHING` |
| C1–C3 | one root two heads; two roots overlapping; two roots non-overlapping | `HOLD_UNSAFE plan_conflict` / `plan_conflict` / `LAUNCHING` |
| D1 | replacement tick, torn sibling + valid plan at t0−14 min, real ps, recorded live stub | one tick: `resident_adopted`, `resident_drain_started`, SIGTERM at once, stub gone, phase COMPLETE, `HOLD_CENSUS` (my session in census) |
| D5 | as D1, stub ignores SIGTERM | SIGKILL sent in the same tick, stub gone |
| D2 | valid plan at t0−15.5 min (TERM phase), stub ignores TERM | SIGTERM only, stage TERM, stub alive, request persisted |
| D3 | far plan (2 h): tick 1 → REQUEST only, no signal; request aged 9 m05 s → SIGTERM; aged 10 m05 s → `already_gone` | ladder continues from the original request across ticks |
| D4 | recorded start token ≠ live process | `already_gone`, no signal, lock removed |
| H1 | `handoff-inventory` from my (headless `claude -p`) ancestry | refused: "must be run by the Terminal-hosted interactive magistrate" |
| H2 | `/usr/bin/python3` (3.9.6) import of the runbook reaper's symbols from the pinned checkout | IMPORT_OK; lstart token format identical in `RealProcessTable`, installer, reaper |
| I1/I2 | pinned installer `--install` from temp copy and from the scratch worktree | rc 3 `noncanonical_checkout`, nothing written, launchctl never called |
| I3 | pinned installer, canonical constant rewritten to a temp git repo, stub ps/launchctl, temp HOME | rc 0; `bootout, bootstrap, print`; lock seeded `first_install_adoption`; plist pins absolute python3.14 and the rendered repo |
| I3b | same with REAL ps ancestry | rc 1 "--install must be run by the current magistrate session" (my ancestor is `claude -p`) |
| I4/I6/I7 | bootstrap failure with plist present / absent; lock-seed failure with plist absent | pre-existing plist bytes restored / plist removed / plist removed, stale lock untouched, 0 launchctl calls |
| I5 | `--uninstall` against stub | bootout + rm |
| K1 | canonical `/Users/edr/code/JouleWise` vs pin | HEAD a6e9edde (main); installer, watchdog, template, both docs DIFFER OR MISSING from the pinned bytes |
| NOT EXECUTED | canonical-path install (K1; headless ancestry); launchd-spawned tick; real twin kill; reaper survival across parent TERM; Gmail send | hard rules / K1 / budget |

Mutations (applied alone, tests run, file restored; tree clean at end):

| Mutation | Outcome |
|---|---|
| M4 `tick` never adopts on `HOLD_UNSAFE` | KILLED (2 F, 1 E) |
| M5 drop `plan_phase == "KILL"` from `kill_due` | KILLED (4 F) |
| M6 `plan_conflicts` returns `[]` | KILLED (2 F) |
| M7 installer canonical check removed | KILLED (1 F) |
| M2 torn JSON skipped silently; M3 `decide` ignores `snapshot.errors` | suite HUNG (mutated tick forks looping supervisors; run overran the 600 s foreground limit, harness backgrounded it, I killed my own processes) — detected, not a clean red |
| M1 `is_retired_v1_plan` drops the schema-label check | SURVIVED (63 OK) |
| M9 drops the complete-required-keys check (any v1-labelled subset ignored) | SURVIVED (63 OK) |
| M8 installer cleanup no longer removes the plist it wrote when none pre-existed | SURVIVED (8 OK); behaviour itself correct (I6/I7) |

## 4. Verdicts

**Q-B1 — AFFIRM.** Severity MATERIAL (test oracle). `magistrate_watchdog.py:133-141` ignores only schema v1 with key set == golden (fixture-derived `:110-127`); `:649-699` holds unreadable, malformed, future-authored. Executed S1–S6, C1–C3: every doubtful shape holds; only the golden shape is ignored. Prior B-1 cured; round-4 fail-open not recreated (S1, M4/M5 killed). Disagreement with the labeled "CURED" only in degree: M1 and M9 show the two limbs of "positively identified by the complete golden shape" are unpinned by any committed test. Cure: add a v2-labelled/v1-key-set and a v1-labelled/subset sibling to the CLI four-plan set.

**Q-CLI — AFFIRM, MATERIAL.** `test_magistrate_watchdog_cli.py:141-208` runs `sys.executable scripts/magistrate_watchdog.py tick` with only `git`/session-bin stubs on PATH: real parse, service lock, `real_dependencies`, classifier, real `ps`. Class closed for the constructor/control-flow signature (M4–M6 killed). Minimum missing seam: the retired-identification limbs above (M1, M9) — a hold-vs-ignore decision reachable in production and untested.

**Q-SIG-a — REJECT** (a consult was not mandatory). Charter §9 makes explicit justification the alternative to consult/redesign ("licensing another same-shape round requires explicit justification"). Delta 5 (`15:248`) and delta 6 (`18:133`) are two consecutive YES after the round-4 consult; `16:5-7` supplies the justification for round 6. Round 7's licence (`16:21-23`) rests on a narrower S-2→S-2b, which is thinner because S-2 was a specified cure that re-failed; the Opus counter-review (`21:35-52`) then served as the different-family consult before round 8. Quotes verified complete against the exhibit lines.
**Q-SIG-b — AFFIRM**; the written dissent stands. Concur with the magistrate's label.

**Q-HANDOFF — AFFIRM the mechanism, MATERIAL M-B.** Inventory `:901-996` separates ancestry-closed `owned` from ppid-1 `unclassified_candidates`; promotion demands pid+start (`:938-948`); headless ancestor refused (H1). Signal path: TERM then KILL root-last by tree walk, immediate pair revalidation (`:1560-1595`, D1/D2/D5), absence and reuse non-signal (D3c, D4). S-2b executed across ticks (D3). Gaps I could not execute: launchd-spawned recovery at THIS pin (17n is on main, not at fdbb840c) and the runbook reaper (`MAGISTRATE_WATCHDOG.md:141-220`) runs as a `nohup … &` child of the interactive session's tool shell without `os.setsid()`; if the session tears down its tool process group on TERM, the reaper dies before its KILL step and the handoff silently stalls with the twin alive and the watchdog `ACTIVE` forever. Cure (doc only): first statement `os.setsid()`, or launch via `python3 -c 'import os;os.setsid();…'`.

**Q-INSTALL — REJECT "executable tonight"; AMEND. BLOCKER B-A.** Opus B-2, S-2, S-3 are cured (I1–I7; `install_magistrate_watchdog.sh:64-74,157-176,215-239`; doc GUI-login/15-min liveness paragraph). But step 4 requires the installer at `/Users/edr/code/JouleWise`, and K1 shows that checkout is main a6e9edde without any of the five pinned files. Counterfactual: a magistrate running the checklist tonight fails step 3 (`scripts/magistrate_watchdog.py` absent or old) before any install. Cure: insert step 0 — merge fdbb840c to main under the normal gate, `git -C /Users/edr/code/JouleWise pull --ff-only`, and verify the five files' sha256 equal the packet exhibits — that merge is an irreversible action the packet did not present, so I do not authorize it here. Two further conditions: the acting magistrate must be Terminal-hosted interactive (I3b: a headless magistrate cannot install); C-4's "failed lock seed removes the plist it wrote" is not in the committed tests (M8) — MATERIAL, add the plist-absent cases.

**Q-C9 — REJECT running the first night with the risk; AMEND.** MATERIAL. Prompt lines 2-6 make the launch email and `notice.ack` the only proof the Gmail MCP loads under launchd `-p`; line 21 makes failure silent. Minimum pre-night evidence, obtainable without new machinery: do not arm any real plan until (a) one launchd-spawned activation exists (`attempts/<activation>/` with a lock lacking `first_install_adoption`) AND (b) `notice.ack` for that activation exists, AND (c) one `REHEARSAL_STUB` night has produced `courier.sent` through the night driver's own `-p` courier. Concur with the magistrate that it is the night driver's contract; disagree that it may stay open past arming.

**Q-FENCE — AFFIRM.** `:761-807` canonicalises roots, holds one-root-two-heads and overlapping-different-roots, composes non-overlapping; `:1201-1208` and `:1703-1743` hold/drain; rows `:797-807` include the canonical repo. Executed C1–C3, M6 killed.

**Q-PROC — AMEND.** Replacement text: "Any change to `scripts/magistrate_watchdog.py`, `scripts/install_magistrate_watchdog.sh`, `configs/launchd/*.template`, or `SESSION_ARGV_AFTER_PROMPT` must ship with a green test that runs the real entry point as a subprocess (real argv parsing, service lock, dependency construction; at most the process-table and network seams injected) and with at least one named mutation of the changed lines shown RED under that test." Scope: prospective, those files only; not a charter amendment. M1/M9/M8 surviving is the evidence for the mutation clause.

**P-4 — AFFIRM** (`:70-71`; resident `step()` `:1751-1753` reads the cache only; probe in `decide` `:1224`; refresh thread `:1404-1440`). **P-5 — AFFIRM** (`:63-65`, STOP file `:1230`). **R-6 — AFFIRM with one sentence added**: "The watchdog ignores only the golden retired shape and holds every other v1-labelled object" (S4/S4c vs S6); other limbs verified at `night_gate.py:52,636-639,267-271`, `install_night_agent.sh:56-73,88`. **R-7 — AFFIRM** (prompt line 10; doc line 86; `night_gate.py:639`). **R-9 — AFFIRM** (`:67-74`; D1–D5; glob `:64`; resident loop network-free).

## 5. Hygiene

(1) Q-INSTALL omits that the canonical checkout does not carry the object — affects Q-INSTALL only (B-A). (2) §5 test count 182 vs executed 184 — NIT. (3) Q-HANDOFF is a six-limb compound question; answered per limb. (4) Q-SIG excerpts complete. (5) 17n launchd proof is cited "on main", not at the pin — affects Q-HANDOFF's live-evidence limb.

## 6. Overall

**INSTALL: AFFIRM conditionally** — the watchdog may be installed once B-A is cured (object on main and in the canonical checkout, sha256-verified), by a Terminal-hosted magistrate, with the reaper `setsid` amendment applied. **FIRST UNATTENDED NIGHT: REJECT for now** — arm nothing until the Q-C9 evidence (a)(b)(c) exists; the mechanism itself carries no BLOCKER. Severity roll-up: BLOCKER B-A (sequencing); MATERIAL M-A (M1/M9 oracle), M-B (reaper setsid), M-C (M8 oracle), M-D (Gmail unproven).
