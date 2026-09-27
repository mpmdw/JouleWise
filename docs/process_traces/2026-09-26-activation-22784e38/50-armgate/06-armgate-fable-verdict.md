# Arm gate — cold Fable verdict — W1 `d079-epoch-25g83-derivation-w1-20260927`

Read-only; probes ran 23:09–23:13 PDT 09-26. Nothing written but this file. Every probe below was EXECUTED unless marked.

## Q1 Bindings — PASS
- `shasum` over staging: `night_plan.json` = `arm-attempts/000001/plan.json` = `388420b5…02f5`; `schedule.json`, `render-context.json`, `notice-body.txt` equal `09-staging-sha256.txt`.
- Plan fields read: `repo_head` = `measurement_head` = `97082508…0142`; plan id, t0 1790494200, `window_max_s` 9000, custody root and measurement root as charged.
- Clone: `git rev-parse HEAD` = H; `git status --porcelain --untracked-files=all` prints 0 lines.
- Recomputed from the clone, all equal to the notice: pre-registration `81b65f08…ddf1`; frozen plan `9ab4776f…a072` (custody copy identical); protocol_v3 `9eaf92f8…31b1`; D-166 registration `dfe55f8d…c265`; night template `e62a461b…e5c8`; probe template `1570b745…1fd`; chain source `b5beea46…d6fb`.

## Q2 Ledger — PASS
- `cmp` clone vs n2 ledger: byte-equal, 176 rows, sha256 `95d152f0…5302` = `git show H:…/ledger-176-sha256.txt`.
- Pin at H: sequence 176, `0f7609ae…2512`. In-memory probe: row 176 `receipt_digest` = pin; sequences 1..176 contiguous; 175/175 `predecessor_digest` links intact. Receipt digests were not recomputed from content by me; `step1.out:25` shows the repo authenticator's `head-equals-pin 176 0f7609ae…`.
- Other ledgers (13 clones, canonical, 2 archives): eleven are the 76-row base `aa806848…`, an exact prefix of n2; the n1 clone's 126 rows are an exact prefix of n2; none is newer than n2's (09-19 07:03); the four qpe01-pilot clones (09-20 → 09-23) have no ledger. n2 is the right source.
- **NIT-1:** `JouleWise-measurement-20260916-derivation` holds 78 rows, a fork off the 76-row base: rows 77–78 are `append-intent` + `bracket-session-open` for session `…-n1-20260916`, with no slot claim and no capture. Nothing is lost; disclose at harvest.

## Q3 Script changes — PASS; no other change
`diff` of all eight files against `c79816c9`: README, step0, step4, step5 identical; `arm-env.zsh` differs only by the H/T0/PREREG fills and (a).
- **(a)** Stronger: the old source had no digest pin. The byte-copy and authenticated head-equals-pin checks are unchanged.
- **(b)** Not a script change. Archive exists at `~/night-archive/w1-step1-refused-clone-22784e38` (HEAD = H, 76-row ledger).
- **(c)** Not weaker. The exact line `mismatched fields: os_build` on both reports excludes any sampler or MLX mismatch; the added row pins the sampler to `b762e5bf…`, equal to the pre-registration's registered digest (line 135) and to `shasum /usr/bin/powermetrics` now. The `rc=3` and no-`ledger:` checks are untouched. **NIT-2:** the literal row is asserted on the plain report only.
- **(d)** Equal strictness (exact three-name set, each `Interactive`, digest recorded); it matches the unmodified step 4, which already requires three labels in the probe receipt.

## Q4 Wrapper and schedule — PASS
- `chain.zsh` sha256 `ccaeac64…b956` = sidecar. It refuses unless plan id, measurement root and H equal its literals and clone HEAD = H; it pins the frozen plan, identity-epoch (`b8a1094c…`) and T1 (`8dcdfb00…`) digests, all recomputed equal. Slots d01–d12; settle 600, cadence 600, budget 480; `WINDOW_END_EPOCH_S` 1790503200 = t0 + 9000 (needed span 7680 s).
- Plists read: night Month 9 / Day 27 / Hour 0 / Minute 30; dead-man Hour 4 / Minute 5; all three `ProcessType=Interactive`; interpreter = the clone's `.venv/bin/python` (3.13.1, runs); night and dead-man point at the custody `night_plan.json`; courier binary `…/claude/versions/2.1.283` is executable.
- Boundaries (`date -r`): install close 00:20 = t0 − 480 − 120; REQUEST 00:22; TERM 00:24; KILL 00:25; t0 00:30; window end 03:00; dead-man 04:05 = t0 + 9000 + 300 + 3600.

## Q5 Notice — no false line
Every digest, path and epoch recomputes. Imprecise lines:
- **NIT-3:** "replaced at most once": A-R5b allows one replacement window per epoch, not per window.
- **NIT-4:** "install span 1 close EXCLUDED 2026-09-27T00:00:00-07:00" is the 09-26 span only. `INSTALL_SPANS` is `00:00–24:00`; the binding cutoff is 00:20.
- **NIT-5:** probe digest `562e4341…` is the staged render. `night_agent_install.py:1032–1036` derives the probe's paths from the plan's directory, so the install-time probe plist will have a different digest; step 4 checks only that three 64-hex digests exist. Record the install-time digest. NOT EXECUTED: the install-time render.

## Q6 Science — sound
- Battery, step 0: connected, not charging, `InstantAmperage` 0 mA, gauge age 59 s, raw capacity 7575/7575. Live `pmset -g batt`: AC, 100 %, charged. Step 4 requires a second fresh pass. Per-slot pre/post readings exist at H (`validate_powermetrics_fiducial.py:2269, 2497`).
- Identity epoch and T1 vs the live machine: 25G83, Mac15,9, sampler `b762e5bf…`, MLX 0.31.2, protocol digest: all equal. `ac_high_power` is the project's label for AC power with low-power mode off; live `powermode 0` satisfies it (`controller.py:510–534`).
- Revision 5: 12 slots, 600 s settle and cadence, Interactive launch at the pinned templates; registered chain digest (line 544) `b5beea46…` = the clone's chain. W1 has no neighbour yet for the 6 h rule.
- **NIT-6 (harvest):** the ledger holds 24 finalized 25G83 slot rows from n1/n2 (11 valid) with the same six identity fields. Revision 5 makes them diagnostics, never members; the issuer must exclude them by session.
- **NIT-7:** census foreign PIDs 70194/70213/70214 are the magistrate's own Codex MCP server children (`raw-pgrep.txt`). They and this review session must be gone before REQUEST.

## Findings
BLOCKER: none. MATERIAL: none. NIT: 1–7.

**VERDICT: ARM**
