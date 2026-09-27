# W1 arm gate: Opus contract lens (independent of 06)

Probes were run read-only at 2026-09-26 23:12 PDT (epoch 1790489520).

## Q1 Bindings: PASS
- The staged plan sha256 is `388420b5…02f5`, and it is byte-equal (`cmp`) to `arm-attempts/000001/plan.json`.
- `repo_head` = `measurement_head` = H. The plan id, t0 1790494200, window_max_s 9000, the custody root and the measurement root all match the charge.
- The clone's `HEAD` is H. `git status --porcelain` is empty; the only ignored paths are `.venv/`, `egg-info/` and `runs/`.
- I recomputed these digests in the clone:
  - pre-registration `81b65f08…ddf1`;
  - frozen plan `9ab4776f…a072` (the custody copy is equal);
  - protocol_v3 `9eaf92f8…a9b1`;
  - D-166 registration `dfe55f8d…c265`.
  All four equal the notice. I did not recompute the template digests (NOT EXECUTED); step 2 already asserts them against Revision 5.

## Q2 Ledger: PASS
- The clone ledger is byte-equal (`cmp`) to the n2 ledger. Both hash to sha256 `95d152f0…5302`, which equals `ledger-176-sha256.txt` at H (`git show HEAD:`).
- The n2 ledger has 176 rows. The last row is seq 176, and its `receipt_digest` is `0f7609ae…2512`, which equals `calibration_ledger_head.json` at H.
- I swept every `~/JouleWise-measurement-*/runs` ledger and the canonical checkout:
  - Most are 76 rows, including the canonical one. They are an exact prefix of n2.
  - `20260919-derivation` has 126 rows (n1) and is an exact prefix of n2.
  - `20260916-derivation` has 78 rows and is NOT a prefix. Its extra rows 77–78 are an abandoned n1-20260916 `append-intent` and a `bracket-session-open` forked off seq 76. That fork is dead and not on the pinned chain.
  - No ledger anywhere is longer than 176 rows. The qpe01 pilot clones have no calibration ledger.
- n2 is therefore the only chain that reaches the committed pin, so it is the right and complete source.
- Pre-registration line 618 states that the n1/n2 B values "are never members of the new registration". The 176 rows supply continuity of the chain's hashes only, never members.

## Q3 Script changes: PASS
I ran `diff` against `c79816c9`. Only `arm-env`, `step1`, `step2` and `step3` differ; `step0`, `step4`, `step5` and the README are identical.
- (a) The script adds an explicit digest pin before the copy. The existing byte-equality check and the authenticated-head check both remain, so this is strictly stronger.
- (b) The refused partial clone was moved to `~/night-archive/w1-step1-refused-clone-22784e38`. `night-custody/measurement/` now holds only the fresh clone.
- (c) The expected mismatch set changes from `{os_build, powermetrics_sha256}` to exactly `{os_build}`. The script also adds an explicit sampler row pinning `b762e5bf…` expected = observed `match`, and `/usr/bin/powermetrics` hashes to `b762e5bf…` live. This is no weaker: it pins more, and the mlx row is covered by the exact-set line.
- (d) The render set is now an exact set that also contains the per-plan probe label. This is no weaker.
- No other change is present.

## Q4 Wrapper and schedule: PASS
- `chain.zsh.sha256 -c` reports OK (`ccaeac64…`). The chain-source sidecar is `b5beea46…`, which equals the clone's `calibration_derivation_only.zsh`.
- `chain.zsh` hard-refuses unless the measurement root is this clone and the measurement head is H. It binds the frozen plan sha256 and the clone's ledger and pin.
- The rendered calendars are right: night fires Month 9, Day 27, 00:30; dead-man fires at 04:05. The interpreter is the clone's `.venv/bin/python`, and the working directory is the clone.
- The courier binary `…/claude/versions/2.1.283` exists.
- The boundaries follow t0:
  - install close is t0 − 600 (lead 480 + margin 120);
  - REQUEST is t0 − 480;
  - the window ends at t0 + 9000;
  - the dead-man fires at t0 + 12900.

## Q5 Notice: no false line found
I checked every digest, epoch and path in the notice against the files. See the NITs below.

## Q6 Science: PASS
- **Battery gate (step 0, raw values):**
  - ExternalConnected Yes, IsCharging No;
  - signed InstantAmperage 0 mA;
  - UpdateTime age 59 s, within the 180 s limit;
  - FullyCharged Yes at 100 %.

  The gate code implements the A-R5b predicate as written (pre-registration line 652), including the two's-complement reading and quoted top-level keys.
- **Identity epoch and T1 bindings:** `identity-epoch.json` and `t1-bindings.json` are field-for-field equal to the n2 seq-176 row. They also match the live machine: build `25G83`, `Mac15,9`, powermetrics `b762e5bf…`, mlx `0.31.2` from the clone venv.
- The plan is a DIAGNOSTIC_NO_PACK derivation under the pinned Revision 5 + A-R5b file, with n1/n2 excluded from membership.

## Publication-time assertions in step 4 / step 5
I found none that will fail on the current staged state, provided the manual act in README step 6 is done:
- `notice-evidence.txt` is currently absent, and `test -s` requires it;
- `notice.json` needs its three placeholders filled, and `accepted`, `prerequisites_clear` and `veto_clear` set to true;
- `attempts.json` must stay `[]`.

The install span is (00:00–24:00), re-resolved on the day of admission, so an install after midnight passes. Only `install_close` at 00:20 binds.

## Findings
- BLOCKER: none.
- MATERIAL: none.
- NIT 1: step 4 requires exactly 2 lines reading `BATTERY GATE PASS`, and it appends a line before `retry_allowed` and before the probe. If anything later in step 4 fails, a rerun sees 3 and fails closed. Any retry needs a manual attempt-2 procedure.
- NIT 2: in step 2, the CHECK text still reads "old os_build and sampler mismatches", which is stale after (c).
- NIT 3: the probe plist in `render-context` points to the staged plan path. The probe that step 4 installs renders against the published path, so its digest will differ from `562e4341…`. Step 5 compares digests only for the night and dead-man plists, so nothing fails, but the probe digest in the notice is not the one that will be installed.
- NIT 4: the notice line "install span 1 close EXCLUDED 2026-09-27T00:00" is true but misleading. The binding limit is install close at 00:20.
- NIT 5: `arm-census-2` shows the magistrate's own codex mcp-server children as `foreign_pids`, under the session root the magistrate owns. Before t0 − 45 min, those children, this lens and the Fable judge must all be gone.

VERDICT: ARM
