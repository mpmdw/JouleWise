# Execution-lens refuter on 12ec41d2 (terra xhigh + wrapper replay), verbatim

**Refuter report — NIGHT-PLAN-PIN-01, head `12ec41d2` (verified; worktree clean, real repo/custody/measurement checkout untouched; no `night-results/*` ref created)**

Instruments: gpt-5.6-terra xhigh (default tier, `codex-run-v3 --genre review`, run_key `20260904T025550Z-22784-refuter-terra`, 856 s, envelope valid, 3/3 verifications pass) in a `$TMPDIR` clone, plus my own replay in a second clone. Terra report: `<tmp>/planpin/refuter-terra.md`.

**Table A — findings (terra severity / lead-replay severity)**

| ID | Sev (terra / lead) | Site | Evidence (executed) | Test catches? |
|---|---|---|---|---|
| B1 | blocker / **should-fix (contested)** | `joulewise/night_gate.py:605-608` vs `:624-631` | Measurement+driver probes run BEFORE the two age checks. Aged plan (`authored_epoch_s=-200000`) + probe error → `night_probe_error`, not `night_plan_stale`; future-authored + probe error → `night_probe_error`, not `night_plan_malformed`. Pre-existing shape (origin/main probed `checkout_head` before the age checks too) but the probed path is now an external checkout whose absence is plausible. Fail-closed either way. Brief's stipulation (00-brief:93-94: window guard precedes every probe; census follows stale checks) HOLDS — terra over-reads it. 6-line fix. | N |
| S1 | should-fix / should-fix | clause (c); `scripts/run_night.py:277`; `tests/test_run_night.py:1125` | Counterfactual `root`→`str(REPO_ROOT)` leaves the cited test GREEN (`Ran 1 test OK`): the test pins a MOVED scratch repo, so any wrong HEAD also reads "stale". Row (c) is effectively NOT PINNED for "probe uses the plan's root". | N |
| S2 | should-fix / should-fix | `scripts/run_night.py:282` | Drop `.strip()` → a MATCHING real plan refuses `night_plan_stale` (detail carries `\n`); `test_run_night`+`test_night_gate` still 100 OK. No positive production-path test exists; one such test kills S1 and S2. | N |
| L1 | — / should-fix | `scripts/install_night_agent.sh:53-62` | Plan with `measurement_root: "."`, `measurement_head`=driver HEAD → installer rc=0, both plists rendered (git -C resolves relative to cwd). Gate later refuses `night_plan_malformed`: an arm that is guaranteed to refuse. Installer has no isabs/hex/schema check. | N |
| L2 | — / nit | `install_night_agent.sh:53-54` | v1 plan on install path → rc=1 with a Python `KeyError: 'measurement_root'` traceback instead of exit 3 + pin/retirement text. Fail-closed. Uninstall of a v1 plan rc=0 (correct, clause h). | N |
| N1 | nit / should-fix (magistrate) | `docs/process/NIGHT_HANDBACK.md:21-22,63,67-70` | Courier-read text still states dev-HEAD gate + "installer checks repo_head before uninstall". Out of Sol WRITE_SCOPE; listed as follow-up in landing report. | text |
| N2 | — / nit | landing report §Compatibility | Says `rehearsal-20260903` is "still armed": night already fired 02:56 09-03 (`night.log`), agents uninstalled. | — |

**Table B — mutation / production probes (lead replay; terra concurs on all)**

| Probe | Path | Observed | Caught by |
|---|---|---|---|
| (a) `:633` → `checkout_head != plan.repo_head` | unittest | 46 ran, 1 FAIL + 1 ERROR (`:446`, `:460`) | Y |
| (b) `:43` guard → `if (( 1 ))` | unittest | `0 != 3: plan repo_head does not match driver checkout HEAD` | Y `test_install:131` |
| 39-hex / UPPERCASE head | real `_load_plan` | `night_plan_malformed` + retirement text | Y (upper `:327-328`); 39-hex N |
| ancestor sha / non-ancestor sha | `_load_plan`+`make_probes()` | `night_plan_stale` (detail names plan head, checkout head, root) | Y `test_run_night:1125` |
| root = non-repo / nonexistent dir | same | `night_probe_error: RuntimeError: measurement head probe failed for …` | Y (fake) `:472` |
| root relative / empty | `_load_plan` | `night_plan_malformed` (isabs / non-empty) | Y `:323-325` / N |
| v1 plan; v1 schema + v2 keys | `_load_plan` | `night_plan_malformed` "…v1 is retired…re-authored under…v2" (keys msg / schema msg) | Y `:294` |
| trailing-newline head from adapter | fake probe | `night_plan_stale` (gate compares raw; adapter strips) | — |
| terra extra: delete isabs `:239-245` | unittest | relative-root subtest fails | Y |
| terra: v1 via real `run_night()` + stub courier | production | rc 3, retirement text persisted to `refusal.json` (`_malformed_plan_exit:1008-1028`) | parser Y |

**Table C — clause map a–j (all 19 file:line citations verified exact)**

| Row | Lines exact | Clause holds | Counterfactual |
|---|---|---|---|
| a,b | Y | Y | executed, kills |
| c | Y | production Y; **assertion does NOT bite** (S1) | executed, test stays green |
| d,e,f,g,h,j | Y | Y | executed (terra), kill |
| i | Y | Y as stipulated (order proof below); terra marks N over B1 | census-first mutation kills |

**Table D — remaining `repo_head` / dev-HEAD sites**

| Site | Behaviour |
|---|---|
| `night_gate.py:232-236, 612-613` | format check; records `plan_repo_head`, `driver_checkout_head`; no equality refusal |
| `run_night.py:270-274` | driver HEAD probe; movement informational; probe FAILURE → `night_probe_error` (pre-existing) |
| `install_night_agent.sh:43-52` | install-only rc 3 on mismatch; uninstall skips |
| plist template | `WorkingDirectory @@REPO@@`; no HEAD compare |
| `NIGHT_HANDBACK.md:21-22,63,67-70` | stale text only (N1) |
| `joulewise/arm_readiness_evidence_t0.py:~2262-2268` | pre-arm authoring refusal on HEAD change; not a fire-time gate |

**Gate order proof (executed, fake probes):** expired+wrong-head+census-fail → `night_window_expired`, zero run/measurement/checkout calls; age+head+census → `night_plan_stale` "older than 36 hours", zero run calls; head+census → `night_plan_stale`, zero run calls; driver-head moved+census-fail → `night_refused_agent_present`, C5 `driver_checkout_head` recorded. Pinned by `test_night_gate.py:437` and `:512` (ORDER walk, successful probes only — B1's error path is unpinned).

**(5) Custody roots:** both `rehearsal-2026090{2,3}/night_plan.json` are v1; `NightPlan.from_mapping` on them → `night_plan_malformed` "plan keys are not exact (missing measurement_head, measurement_root)…v1 is retired…". Nothing reads them: `launchctl list | grep -i joulewise` rc=1, `~/Library/LaunchAgents` no joulewise rows; 0903 night already fired 02:56 (REFUSED `night_refused_agent_present`; courier sent 02:57; dead-man skipped 07:00); a re-run would hit `_existing_record`. Nothing can fire.

**Integration:** merge-base `2f59e791`; real origin/main (`46eaf18c`) touched none of the six files → trivially integrable. Full suite: `Ran 104 tests … OK` (mine and terra).

**Landing verdict: NOT LANDABLE as-is (terra and lead agree on the verdict, disagree on B1 severity).** Soundness is intact — every probe fails closed and no path starts measurement — but a cold gate cannot pass a clause map whose row (c) assertion does not bite (S1) with an untested positive production path (S2), and an installer that arms a night the gate will certainly refuse (L1). Fix round (one Sol high seat): (1) move the `:604-608` probe block below the two age checks + an error-shaped order regression (B1); (2) one positive production-path test: scratch root HEAD == plan, REPO_ROOT HEAD differs, real `make_probes()` → passes stale (kills S1 and S2); (3) installer isabs + 40-hex checks with tests (L1/L2); (4) magistrate rewrites `NIGHT_HANDBACK.md` lines and files the R-6/R-7 reinterpretation addendum (N1). Then delta re-audit. B1's blocker-vs-should-fix is left to the magistrate: I record terra's blocker and my dissent (stipulated order holds; refusal-code masking on an already-fail-closed path).
