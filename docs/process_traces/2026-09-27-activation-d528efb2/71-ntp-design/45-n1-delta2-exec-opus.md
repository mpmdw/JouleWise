DELTA: PASS

# N1 delta re-audit after fix rounds 2 and 2b: execution of addendum A1 §7.3

Auditor: Opus 5.5, an executing re-audit seat that wrote no part of the fix. 2026-09-28, about 08:50 to 09:40 PDT.
Candidate: detached worktree `/Users/edr/code/JouleWise-wt-ntp-n1delta2-d528efb2`, head `36e8ba6e`. Its git status was clean before and after every run, and its head did not move.
Comparison heads: `3ad82b43` (before round 2) and `c8995f4b` (round 2 without 2b).

**Result in one paragraph.** All seven rows of A1 §7.3 pass, with one qualification in row 1 (below). No run showed D1's signature, which A1 §3.4 defines as the network-time log query or the ON command running while a process with a capture signature is alive. That covers the judge's probes, the 35 new regressions, the seven deletions and 43 cases of my own hunt. An independent checker counted such processes at the instant of every query and every ON (the oracle, defined in §1). The same checker reports D1 on `3ad82b43` in all five hunt cases I ran there. The contract lens's N1 (the witness pattern) also does not survive: I added seven new attack lines and all seven are refused. I found three new NITs and no BLOCKER or SHOULD-FIX. One matter for the lead: **a separate session ran real `sudo -n /usr/bin/powermetrics` processes during this audit** (§6). I did not start them. They spoiled my first timing run, which I repeated with those processes excluded.

## 0. Contamination disclosure

1. **Put into my context by the harness before the charge, not opened by me:** the owner's global instruction file, the project instruction files (`CLAUDE.md`, `CLAUDE.local.md`) and the one-line index of the owner's memory store. I took the writing standard from them as form. Every fact below rests on a file I read or a command I ran.
2. **Not opened:** `RUN_STATE.md`, `TASK_QUEUE.md`, any `CLAUDE*.md`, `AGENTS.md`, any memory file, any skill file.
3. **Read:** addendum A1 (record 38) in full; the prior delta (36); the round-2 and round-2b reports (42, 44); the judge's probes (38-probes); the listing of 39-probes (I did not run them). In the candidate I read the diff `3ad82b43..36e8ba6e` and the production code the diff calls.
4. **Executed:** read-only git; `ps` and `pgrep`; my probes; and the per-ID runner, which runs a test module and records each test's outcome. **Not executed:** `sudo`, `systemsetup`, `sntp`, `/usr/bin/log`, `pmset`, `ioreg`, any capture, any process named after the real sampler. Every probe installs an audit hook, a Python check that raises before any of those programs can start. Every network-time command and every log query went to an injected stand-in, a test function that answers in place of the real command. Each probe process was a harmless Python sleeper, and each was killed at the end of its case. A search after every run found none left.
5. **Files:** no candidate file was changed. The only repository file I wrote is this report. Scratch is under `/tmp/ntp-n1delta2-exec/` (`probes/`, `standins/`, `logs/`, `mod/`). I made four scratch worktrees, `JouleWise-wt-ntp-n1d2x-{old,pristine,del,c899}`, and removed them at the end.

## 1. Words used

| Term | Meaning |
|---|---|
| **Query**, **ON**, **OFF** | The driver's one reading of the clock daemon's log, and the two commands that turn "set time automatically" on and off (ruling in force). |
| **Marker file** | The file that says ON is still owed. |
| **Proof** | `_prove_capture_absent` in `scripts/run_night.py`. It asks whether any capture process is still running, using three checks. **P1:** is the chain's own process group empty? **P2:** is every group in the night's registry file empty? **P3:** does one listing of every process on the machine (a **sweep**) contain no command line with a capture signature? |
| **Pass** | One run of P1, then P2, then P3. |
| **Retry horizon** | The latest moment, measured from the start of the proof, at which the proof will still start another pass. |
| **Capture signature** | A command-line word whose last path part is a sampler's name, or text containing one of the night's paths (A1 §1). |
| **Stated limit** | A1 §4.4: a surviving process whose command line has no capture signature passes the proof by design. A1 §7.4 says such a process is not D1. |
| **Stand-in sampler** | `/tmp/ntp-n1delta2-exec/standins/hdx-sampler`, a Python sleeper. For each probe I add its name to the list of sampler names (`CAPTURE_SAMPLER_NAMES`), as the judge did with `cgprobe-sampler`. |
| **Path stand-in** | A sleeper script under the night's measurement root. Its path is a capture signature, the same way a real collector's script path is. |
| **Plain sleeper** | `python -B …/standins/hdx_plain.py` or `python -c 'sleep'`. Its command line has no capture signature. |
| **Oracle** | My own check, independent of the code under test. It replaces the stand-in runner for the query and ON calls. At the start of each query, at its end and at the start of ON, it lists every process and records any that has a capture signature. D1 is present exactly when the oracle finds one. |
| **By assertion** | The test fails on an `AssertionError` from the thing it tests, not on some other exception. |

## 2. Table of §7.3 rows

| # | What | Result | Evidence (commands under `/tmp/ntp-n1delta2-exec/probes/`, logs under `/tmp/ntp-n1delta2-exec/logs/`) |
|---|---|---|---|
| 1 | Judge's probes against the candidate | **PASS, with one qualification.** Every row that has a capture signature ran only OFF and kept the marker file. **D2** gave `restored` with ON retried, in both branches. **D3** gave `network_time_unattested` three times. The clean control ran off, query, on. **Qualification:** the two separate-group rows of `probe_d1.py` (`DRIVER_SEPARATE_GROUP`, `RECOVERY`) still run query and ON on the candidate. Their survivor is `python -c "import time; time.sleep(45)"`, which has no capture signature, so this is A1's stated limit and not D1 (A1 §7.4). The judge's own prototype row `I_PLAIN_SLEEPER_NO_SIGNATURE` behaves the same way. The same shapes with a capture signature are refused (row 4: H1b, H4a–c, H5, RECOVERY). `KILL_PATH` still prints `termination_proven: true`. That is correct, because A1 C7 keeps that function unchanged, and the query and ON after a stop are gated by the proof (T4, H5). | Probes adapted only in their paths. The adaptation also restores the real proof, because `NightDriverTests.setUp` now installs a stand-in that always says "proved". `python3 -B probe_{d1,cure,d2}.py <root> cand\|old`, `probe_d3.py <root> cand`. Logs: `probe_d1-{cand,old}.log`, `probe_cure-{cand,old}.log`, `probe_d2-{cand,old}.log`, `probe_d3-cand.log`. `probe_cure` on the candidate: B, C, D and F give exit 3 with only OFF and the marker kept; the F recovery gives `chain_unproved` while the child lives, then `restored` with one `h5-on.json`; G gives off, query, on. On `3ad82b43`, B, C, D and F all run off, query, on. D3 on the real logs: 2,040 of 2,040 and 90 of 90. |
| 2 | §4.7 and §5 regressions, plus E1 and E2 | **PASS.** All 35 added tests pass on the candidate. On `3ad82b43` with the candidate's test files, every §4.7 and §5 row fails **by assertion**. T1–T3, the P2 case and T4 (census and deadline) give `['off','query','on'] != ['off']`. T5 gives `['restored'] != ['chain_unproved']`. T6: `restored` appears in the outcome set. T7 ×3 give `0 != 3`. T8 and T10 fail on `False is not true`, the presence check. D2 (i) and (ii) give `'marker_invalid' != 'restored'`; (iii) and (iv) give `'marker_invalid' != 'chain_unproved'`. D3 fails in all three subtests: `'clean' != 'network_time_unattested'`. The E1 tests fail on "no capture proof on this head". The P1 recovery test fails on its `capture_proof` parameter check. **T9 passes on both heads.** The two same-group live tests pass on both, as expected, since fix round 1 cured that case. On `c8995f4b`, the E1 and E2 regressions also fail by assertion: `'P1' != 'P3'`, the 0.2 s timeout test, and `'night_window_exceeded' != 'night_chain_alive'`. Five added unit tests *error* on the old head instead of failing: they call a function or keyword that does not exist there. None of them is a §4.7 or §5 row. | `run_ids.py regress_ids.txt` from each root. Logs: `regress-cand.{txt,json}`, `regress-old.{txt,json}`, `regress-c899.{txt,json}` |
| 3 | Deletions | **PASS.** Each deletion turned its named test red by assertion. **P3:** T2 and T3 go red. **P2:** the journaled child without a signature goes red, and T1 changes to `'P3' != 'P2'`. **P1 inside the proof:** the P1 unit test and the recovery test for a same-group child without a signature go red, but the driver-side same-group tests **stay green**. This reproduces round 2b's caveat: the census taken after the chain exits (`run_night.py:1033`) catches the child first. **P1 plus that census:** the same-group test without a signature goes red on its events, and the one with a signature goes red on its exit status (`3 != 6`). **C5:** T5 and T6 go red. **Never-launched claim:** D2 (i) and (ii) give `'chain_unproved' != 'restored'`. **E2 `os.replace`:** T4 deadline gives `'night_window_exceeded' != 'night_chain_alive'`. T4 census stays green, as it should, because that stop has no earlier refusal document to replace. After every case the file was restored and `git status` was clean. | `deletions.py` in scratch worktree `n1d2x-del`. Log: `deletions.log`, `del-*.json` |
| 4 | Own hunt, real processes, through the production driver (`run_night` → the real chain `Popen`, real `pgrep` census, real `ps` sweep) | **PASS.** In 43 cases, plus seven cases timed against the query, the oracle found **no** capture-signature process at any query or ON call. Every case whose survivor has a signature is refused. Every case that runs query and ON has a survivor with no signature and is listed as such. Details in §3. | `hunt.py <root> cand [cases]`. Logs: `hunt-cand.log`, `hunt-cand-h3-midquery.log`; the old head for contrast: `hunt-old-subset.log`, where the oracle reports D1 in 5 of 5 cases |
| 5 | The 42 tests marked fixed in record 36 | **PASS.** 40 of 42 pass. The other two IDs no longer exist, and both were replaced as A1 rules. The saved F1 test gave way to T1 (A1 §6, D4). `…returns_marker_invalid_without_on` was renamed `…returns_chain_unproved_without_on` for the label change of A1 §5, with the same body except the expected label. Both replacements pass (row 2). | `run_ids.py r1_42_ids.txt`, manifest `/tmp/ntp-n1delta-d528efb2/selected.json`. Log: `r1-42-cand.{txt,json}` |
| 6 | Modules run whole with the per-ID runner, from the candidate root, one at a time, outside any sandbox | **PASS.** No failure that is absent on `3ad82b43`. `test_network_time_window`: 48 of 48 ok (baseline 41 of 41). `test_night_gate`: 104 of 104 (104). `test_arm_retry`: 37 of 37 (37). `test_run_night`: 281 of 281 ok in 187 s (255 of 255). `test_launch_window`: LAUNCH_WINDOW_RESULT. The only baseline IDs that disappeared are the two replacements of row 5. | `run_mods.sh`, which runs `TMPDIR=/tmp/ntp-n1delta2-exec/tmp/ python3 -B …/30-s1-repair/run_module_ids.py <module> mod/<module>.json`. Comparison: `compare_mods.py`. Outputs: `/tmp/ntp-n1delta2-exec/mod/*.json`, `*.log`, `run_mods.out` |
| 7 | Does the signature survive? | **D1: NO. N1: NO.** See §5. | — |

## 3. The hunt (row 4)

Each case ran through the production driver with a chain script that starts the named process tree. Each tree was run three times: with a stand-in sampler, with a path stand-in, and with a plain sleeper as the process that survives. "Only OFF" means the driver ran OFF and neither the query nor ON, and the marker file stayed. Exit 3 is the refusal status and 6 means the chain's end could not be proved.

| Case | Signature survivor (stand-in sampler / path stand-in) | Plain sleeper |
|---|---|---|
| **H1a** Double fork; the middle process ends; no `setsid`. The grandchild is an orphan (its parent is process 1) and stays in the chain's group. | Exit 6, only OFF (the census after the chain's exit sees the group) | Exit 6, only OFF |
| **H1b** Double fork with `setsid` in the middle (the usual way to turn a program into a daemon). The grandchild is an orphan in a group whose leader has ended. | Exit 3, only OFF, P3 names the survivor (9 and 8 passes) | Query and ON ran. The survivor has no signature: stated limit |
| **H2a** Child calls `setsid` 1.0 s after it starts, **before** the chain ends (the chain lingers 2 s) | Exit 3, only OFF, P3 | Query and ON ran; no signature: stated limit |
| **H2b** Child calls `setsid` 1.0 s after it starts, **after** a chain that ends at once | Exit 6, only OFF | Query and ON ran; no signature: stated limit |
| **H3** A separately grouped starter with no signature waits until the chain has ended, then after 0, 0.3 or 1.0 s starts a separately grouped sampler | Exit 3, only OFF, P3 names the sampler | — |
| H3 with a delay of 6 s (the sampler would start after ON) | Query and ON ran while only the starter lived, and the starter has no signature: stated limit. The driver had returned before the sampler would have started. | — |
| H3 with the starter in the chain's group | Exit 6, only OFF | — |
| **H3, timed against the query** (the query stand-in takes 2 s, as a real query does): the sampler starts 1.4, 1.8, 2.2, 2.6, 3.0 or 3.3 s after the chain ends | **The query had started with no signature process alive.** In five cases the sampler appeared *during* the query. The second proof, taken before ON, found it, and **ON was withheld** (exit 3, P3, marker kept). At a delay of 3.6 s the sampler started after ON. The survivor at the moment of the query had no signature, so by A1 §7.4 this is the stated limit, not D1. By A1 §3.5 (record 38 E8), a capture that overlaps the query is also `network_time_unattested`. | — |
| **H4a** Separately grouped child starts a separately grouped child; the parent lives | Exit 3, only OFF, P3 | Query and ON ran; no signature: stated limit |
| **H4b** The same; the parent ends | Exit 3, only OFF, P3 | the same |
| **H4c** The same; the parent is journaled by the chain and then ends | Exit 3, only OFF, P3 (5 and 6 passes) | the same |
| **H5** H4a under a **deadline stop** (the driver stops the chain at its deadline) | Exit 3, only OFF, P3. The earlier cause is kept as `prior_abort = night_window_exceeded` | — |
| **RECOVERY** H4b, then recovery while the sampler lives | Driver exit 3, only OFF; recovery `chain_unproved`, no command | — |

Contrast on `3ad82b43` (`hunt-old-subset.log`): H1b, H2a (path stand-in), H4b, H3 at 0 s and H5 all ran off, query, on, and the oracle found a signature process at the query and ON. The oracle can therefore tell the two heads apart.

## 4. E1 timing: how long the proof waits for a sampler that is ending

**Forcing question.** Round 2b's rule starts a further pass only when its worst case still fits inside `GROUP_CENSUS_WINDOW_S` = 5 s. The worst case charges 1 s (`CAPTURE_CHECK_TIMEOUT_S`) for each listing. So a pass is charged 2 s with no registry, 3 s with one registered group and 4 s with two or more, although a real pass takes 0.04 to 0.06 s.

**Measurement, direct.** `e1_timing.py` calls the production `_prove_capture_absent` with a real census and a real sweep. The stand-in sampler exits a set time after the proof begins, and the registries hold groups that have already ended. The name list held **only** the stand-in's name, to shut out the foreign sampler of §6. Log: `e1-timing-cand-isolated.log`.

| Registry | Last pass started at (retry horizon) | Waited for, and proved, when the stand-in had this much life left | Refused (P3) from | Time the proof took when refusing | Formula 5 − 0.2 − budget |
|---|---|---|---|---|---|
| none | 2.68–2.78 s | up to 2.55 s | 2.85 s | about 3.1 s | 2.8 s |
| 1 group | 1.73–1.81 s | up to 1.65 s | 1.95 s | 1.8–2.1 s | 1.8 s |
| 3 groups | 0.71–0.97 s | up to 0.75 s | 1.05 s | 0.8–1.1 s | 0.8 s |

**Measurement, through the driver** (`hunt-cand.log`, the `E1_*` cases). The stand-in sampler is the chain's separately grouped child and lives 0.5 to 3.5 s. The driver notices that the chain has ended about 1.1 to 1.3 s later, because it polls, so the proof starts late. In every case **without** a registry, the query started *after* the stand-in had ended (for example, life 3.5 s: planned end 3.55 s, query start 3.93 s), so the stand-in was waited for. **With** one registered group, lives up to 3.0 s were waited for. At 3.5 s the night was refused on P2 after 7 passes, with the stand-in alive at that moment. That is the safe direction.

**Answer.** No run started the query or ON beside a stand-in that was still ending. A stand-in with 1 to 3 s left **is waited for** when the remaining life is below the retry horizon: 2.8 s with no registry, 1.8 s with one group, 0.8 s with two or more. Above the horizon it is **refused**. It was alive at the moment of refusal, so the refusal is not false, but it comes sooner than the 5 s window A1 §4.2 allows. An idle night always has a registry of two or more groups (a recorder, collectors and samplers), so its real horizon is 0.8 s. The cost is liveness only: the night ends REFUSED, the marker file stays, and recovery restores ON later. This is NIT-1 below. Round 2b's report disclosed the trade-off (about 0.8 s and 2.8 s); my numbers agree with it.

## 5. Row 7: does the signature survive?

- **D1: NO.** Across the adapted `probe_cure` and `probe_d1`, 35 regressions, 43 hunt cases and 7 query-timed cases on the candidate, the oracle found no process with a capture signature alive at any query start, query end or ON start, except in one situation. In the query-timed H3 cases, a sampler started *during* the query by a starter with no signature was alive at the query's end. The query had begun with none alive, and ON was withheld (H3 at 1.4–3.0 s). By A1 §7.4 this is the stated limit (a survivor with no capture signature) and not D1. The deciding cases, where D1 would have shown if present, are H1b, H2a, H4b, H5 and RECOVERY on the candidate: in each, only OFF ran. The same cases on `3ad82b43` show D1.
- **Contract lens N1 (witness category read by position): NO.** The judge's three attack lines each give `network_time_unattested` (`probe_d3-cand.log`). My seven further lines in the real syslog shape (`probe_n1_extra.py`, log `probe_n1_extra-cand.log`) were also all refused on the candidate. They were: a line with a library token whose message holds a `timed[…]: [com.apple.timed:data]`; a `text` line that repeats the host and process; a line with no host; a category glued to the text after it; two host words; a process named `xtimed`; a timestamp with no offset. Four of them give `clean` on `3ad82b43`. Both control lines, the real shape and the fixture shape, still give `clean`. The real-log counts stay 2,040 and 90.

## 6. Environment note for the lead (not a finding against N1)

From about 08:57 PDT, another session's S1 bench (`zsh /tmp/s1bench-d528efb2/rule9/run.sh`, parent process 93468) ran the full test suite. While it ran, `sudo -n /usr/bin/powermetrics -n 2 … -o /tmp/s1bench-d528efb2/rule9/tmp/joulewise-powermetrics-*.plist` and `/usr/bin/powermetrics …` appeared repeatedly. **I did not start them.** My probes block that name. The brief said nothing heavy was running. Consequences:

1. My first `e1_timing.py` run is spoiled in its 1-group and 3-group rows: P3 correctly matched the foreign samplers (`e1-debug.log`). I repeated it with the neutral name only. The tables of §4 come from the repeat.
2. This is also real executed evidence of one thing that A1 §9 left untested: **as an unprivileged reader, P3 does see and match the production shape `sudo -n /usr/bin/powermetrics …` and the root-owned `/usr/bin/powermetrics …` rows.** On this machine, root processes show their full arguments to `ps`.
3. The hunt, the regressions and the module runs matched only my own stand-ins. I checked every refusal's `matches`, and every case that ran query and ON had no foreign sampler present at the time. A foreign sampler is a risk for these live tests: it makes T9 and the other clean-path tests refuse. Run them on a machine where no other capture is running.

## 7. New findings

No BLOCKER. No SHOULD-FIX.

**NIT-1: the retry horizon is well under the 5 s A1 allows.** `scripts/run_night.py:3963–3964` together with `:3902` (`_capture_pass_calls`). Each listing is charged its full 1 s timeout, while real passes take 0.04 to 0.06 s. The proof therefore stops retrying after 0.8 s for any registry of two or more groups (every idle night), 1.8 s for one group and 2.8 s with none, and gives up within about 1 to 3 s (§4). This fails in the safe direction and costs only liveness. A possible repair, for the lead to weigh: let the last pass overrun the window by its own worst case, so the proof is bounded by 5 s plus one pass, and the horizon becomes about 5 s.

**NIT-2: path signatures match on a bare text prefix.** `scripts/run_night.py:3825` (`any(path in command …)`). With measurement root `/Users/edr/code/JouleWise`, the command `/bin/zsh /Users/edr/code/JouleWise-wt-other/run.sh` matches (executed: `signature-matcher.log`). So does `log stream --predicate powermetrics`, through the word rule. Both fail in the safe direction, and A1 §9 foresaw over-matching, but a plain prefix widens it to every sibling worktree. Requiring a path boundary (`/`, a space, a quote or the end of the text after the path) would keep the intent.

**NIT-3: on this machine the idle-night recorder carries no capture signature.** `joulewise/quiet_predicate_campaign.py:1633`, where the recorder is started as `[sys.executable, "-B", "-m", "joulewise.quiet_predicate_campaign", "record", …]`. Homebrew's framework Python replaces the program path (argv[0]) shown by `ps` with `…/Python.app/Contents/MacOS/Python`, even when started through the measurement root's `.venv/bin/python`. I executed this with the repository's own `.venv`: `sys.executable` is `/Users/edr/code/JouleWise/.venv/bin/python`, but its child is listed as `/opt/homebrew/Cellar/python@3.13/…/Python.app/Contents/MacOS/Python -B -c …` (`venv-argv0.log`). So the recorder's listed command line names neither a sampler nor a night path, and only P2 sees it: it is journaled two lines after it is created (`:1610` → `:1612`). The recorder writes covariate rows only (`role: covariate_only, admits_nothing: true`, `:885`), not power samples, so by A1 §7.4 an orphaned recorder is the stated limit and not D1. It is noted because A1 §1 counts the recorder as a capture process. A collector is still matched: its script path under the measurement root is an argument, not the program path (T2 relies on this). This belongs in seat N3's scope, not N1's.

## 8. Left unchecked, stated plainly

- No real sampler, `sudo` or capture was started by me. The only real samplers seen belong to the foreign bench of §6.
- The query-timed H3 cases use a 2 s query stand-in. A real query's length varies.
- I did not run the Opus refuter's probes (39-probes). The deadline and census stops are covered by T4 and H5.
- The retry-horizon measurement comes from one machine on one morning, under the load of the foreign bench.

## Summary

1. All seven rows of A1 §7.3 pass. D1 does not survive: in no executed case did the query or ON run while a process with a capture signature was alive, and the same cases show D1 on `3ad82b43`.
2. The contract lens's N1 does not survive: ten attack lines are all refused, and the real-log counts stay 2,040 and 90.
3. Every deletion goes red by assertion. The P1 caveat is reproduced: the driver-side same-group case is held by the census taken after the chain exits.
4. The hunt found only the stated limit: survivors with no signature pass. A sampler started during the query is caught before ON.
5. E1: the retry horizon is 0.8, 1.8 or 2.8 s rather than 5 s. A sampler that is still ending is waited for below that horizon and refused above it (NIT-1). There are also two NITs on over-matching and the recorder's command line.
6. A foreign real `powermetrics` from another session ran during this audit. It spoiled one timing run, which I repeated. It also confirmed that P3 sees root-owned sampler rows.
