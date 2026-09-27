# Arm gate — cold Fable verdict — W2 `d079-epoch-25g83-derivation-w2-20260927`

Read-only; probes ran 04:30–04:34 PDT 09-27. Every probe was EXECUTED unless marked.

## Q1 Bindings — PASS
- `shasum` over all 14 staged files equals `09-staging-sha256.txt`; `night_plan.json` = `arm-attempts/000001/plan.json` = `0395a605…c0ce` (`cmp` equal).
- Plan fields read: `repo_head` = `measurement_head` = `a71a5e79…7b27`; plan id, t0 1790524800, `window_max_s` 9000, custody and measurement roots as charged.
- Clone: `git rev-parse HEAD` = H; `--is-shallow-repository` = false, no `.git/shallow`, 5598 commits; `git status --porcelain --ignored` lists only ignored `.venv/`, `joulewise.egg-info/`, `runs/`.
- Recomputed from the clone (working file and `git show H:`), all equal to the notice: pre-registration `81b65f08…ddf1`; frozen plan `9ab4776f…a072` (custody copy equal); protocol_v3 `9eaf92f8…31b1`; D-166 registration `dfe55f8d…c265`; night template `e62a461b…e5c8`; probe template `1570b745…1fd`; chain source `b5beea46…d6fb`. PR #412 merge `9b750bf3` and verdict commit `c5088b87` are ancestors of H.

## Q2 Ledger — PASS
- `cmp` W2 clone vs W1 clone ledger: byte-equal, 226 rows, sha256 `b03be938…c63f`.
- Pin file at H = working file: sequence 226, `bd7aee7a…6693`. In-memory: row 226 `receipt_digest` = pin; sequences 1..226 contiguous; 225/225 predecessor links intact; the 176-row n2 ledger is a byte prefix. `step1.out:25`: `authenticated head-equals-pin 226 bd7aee7a…`.
- `check --session-ids …w1-20260927` with both registration flags, run in the W2 clone: rc 0; `battery=pass recorded=pass`; `state=finalized terminal=yes declared=12 filled=12 valid=6 excluded=none`; pending 0; admissible yes. Ledger digest, `runs/` listing and `git status` unchanged after the run.
- Other ledgers (both charged globs, canonical): eleven at 76 rows, one 78-row fork, n1 126, n2 176, W1 = W2 = 226. No later head exists.

## Q3 Script changes — PASS; exactly the intended set
`diff -ru` of the two sets: README and step5 identical. `arm-env.zsh`: H, T0, `WINDOW_ID`, `LEDGER_SOURCE` and its digest pin. step0, step1, step4: the string `W1`→`W2` in a printed label, and in step1's basename test. step2: one comment. step3: notice text only.
- Ledger source: same mechanism as W1 (digest pin, byte copy, authenticated head-equals-pin); not weaker.
- **NIT-1:** the README is W1's bytes: 15 "W1" mentions and the HARVEST CHECK command the harvest record (item 8) found stale. No step executes it. Harvest W2 by runbook §2.2a.

## Q4 Wrapper and schedule — PASS
- `chain.zsh` sha256 `e27978bd…7c01` = sidecar = notice. Against W1's wrapper with ids normalised it differs in two lines only: H and `WINDOW_END_EPOCH_S` 1790533800 = t0 + 9000. It refuses unless plan id, root, H and clone HEAD match; pins frozen plan, identity epoch `b8a1094c…`, T1 `8dcdfb00…`, chain source `b5beea46…`, all recomputed equal. Slots d01–d12; 600/600/480.
- Plists (`plutil -lint` OK): night Month 9 / Day 27 / Hour 9 / Minute 0; dead-man Hour 12 / Minute 35; all three `ProcessType=Interactive`; interpreter = the clone's `.venv/bin/python` (3.13.1, MLX 0.31.2, runs); courier `…/claude/versions/2.1.283` executable; night and dead-man point at the custody `night_plan.json` (published by step 4).
- Boundaries: install close 08:50 = t0 − 600; REQUEST 08:52; TERM 08:54; KILL 08:55; window end 11:30; courier 11:35; dead-man 12:35 = t0 + 9000 + 300 + 3600. Same offsets as W1.

## Q5 Notice — no false or stale line
Every digest, path and epoch recomputes. The W1 harvest line equals `10-w1-harvest/harvest-line.txt`. The d11 sentence matches the final pass (7575→7584 on both capacity figures, 0 mA, 12891 mV) and today's gate reads 7584/7584. Both early touches match record items 4 and 8. Imprecise, not false:
- **NIT-2:** "a third window W3 follows on count": the registration says W3 is *permitted* only if the count after W2 is below 12.
- **NIT-3 (carried):** line 12 "replaced at most once"; line 11 now states one per epoch.
- **NIT-4 (carried):** "install span 1 close" is midnight 09-28; the binding cutoff is 08:50.
- **NIT-5 (carried):** the probe digest is the staged render; record the install-time digest.

## Q6 Science — sound
- **Battery:** step 0 at 04:27:22 PDT: connected, not charging, `InstantAmperage` 0 mA, gauge age 37 s. Live `pmset`: AC, 100 %, charged. Step 4 requires a second pass (`grep -c` = 2); the gate checks again at t0.
- **Spacing:** W1 window end 1790503200 → W2 t0 = 21600 s = 6.000 h, zero margin but met; chain end 02:33:42 → t0 = 6.44 h. t0 must not move earlier.
- **Identity, T1:** both files byte-equal to W1's. Live: 25G83, Mac15,9, sampler `b762e5bf…`, `powermode 0`.
- **Registration:** W1 6 valid is not "fewer than 6", cadence 128.80 ms < 150 ms, battery pass: W2 is the registered next window. Replacement unused. W3 only if W1+W2 < 12, so W2 needs ≥ 6 valid.
- **NIT-6 daytime:** Revision 5 and A-R5b contain no time-of-day rule (grep: none). Revision 1 lines 113–123 describe a generator refusal at "the next local 07:00" and an install span 03:00–06:30; code at H uses the derived dead-man and `INSTALL_SPANS` 00:00–24:00, the same code W1 armed under. Ed's any-time ruling covers it. Two duties: (a) the 150 ms cadence stop is written for W1's harvest only, so produce W2's cadence report as a disclosed diagnostic beside W1's; (b) name W2 as the epoch's first daytime window in the harvest record. The notice prints the times but never says "daytime"; Ed must leave the machine untouched 08:52–11:35. NOT EXECUTED: whether anything detects keyboard or mouse input after t0.
- **NIT-7 census:** `arm-census-2.json` shows `codex_exec` PIDs 38918 and 38964 under session root 81063, non-exempt. They and this review session must be gone before step 4's final census; a census hit at t0 costs the window.

## Findings
BLOCKER: none. MATERIAL: none. NIT: 1–7.

**VERDICT: ARM**
