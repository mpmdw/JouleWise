# Arm gate — Opus 5.5 contract lens — qpe01-pilot-n1-20260923-0700 (probes 05:13–05:20 PDT)

**Verdict: ARM.** No blocker. Nothing material to the run itself. Two defects in the notice's prose sit in hardcoded text in `render_notice` at H. Fixing them means a code change, a new H and a new prepare, so they go to a lane rather than an arm cure (see N1, N2).

## Q1 Bindings: PASS
- `night_plan.json` sha256 is 6193c6b6…b566 and `prepare.json` is 39b9382f…f067; both match the charge.
- The plan binds H (26fb4280…9f15) as both `repo_head` and `measurement_head`. It also binds `registration_path` configs/…/pilot_protocol_v3.json, plan_id qpe01-pilot-n1-20260923-0700, t0 1790172000.0, window_max_s 9000, the custody root and the measurement root, all as named. The schema is night_plan.v2 and the receipt class is DIAGNOSTIC_NO_PACK.
- I recomputed the v3 registration sha256 in the clone: 69321c69…3616. It equals the ruled digest, `prepare.bindings.registration_sha256`, `night_gate.QPE01_PILOT_REGISTRATION_SHA256` (line 67) and the evidence-manifest entry.
- In the clone, `rev-parse HEAD` returns H. `status --porcelain` is empty. `diff --stat 3a411784 H -- joulewise scripts configs` prints nothing; the whole diff is 5 docs files.

## Q2 Wrapper/chain: PASS
- The custody `chain.zsh` has sha256 464697de…fb87, which matches `chain.zsh.sha256` and prepare's digests.
- It exports `NIGHT_PAYLOAD_KIND=quiet_predicate_evidence`. It refuses on a mismatch of plan id, measurement root or measurement head. It re-hashes the clone's chain source against `EVIDENCE_CHAIN_SOURCE_SHA256=568a2771…b7ea`, then runs `exec /bin/zsh <clone>/scripts/night_chains/quiet_predicate_evidence.zsh`.
- The chain source hashes to 568a2771…b7ea both on disk and via `git show H:…`. That equals v3's `chain_source_sha256` (v1 and v2 pin the same bytes).
- All 8 evidence-manifest file digests match the clone's bytes.

## Q3 Schedule: PASS
- The night plist runs Month 9, Day 23, Hour 7, Minute 0. The dead-man plist runs Hour 10, Minute 35 with no Day or Month, i.e. daily by design.
- All three plists (night, dead-man, probe) call the absolute interpreter `<clone>/.venv/bin/python`. Its sha256 is d483cfdc…6132, which matches `prepare.interpreter`, and it reports Python 3.13.1. WorkingDirectory is the clone.
- The courier binary `~/.local/share/claude/versions/2.1.280` exists.
- The boundaries follow from t0 and window_max_s: install close excluded at t0−600, REQUEST t0−480, TERM t0−360, KILL t0−300, window end t0+9000 = 1790181000, courier +300 = 1790181300, dead-man 1790184900 = 10:35 PDT. They are computed by tracked code (`evidence_night.py` lines 499–503).

## Q4 Notice: two defects in the prose (all identity, digest and time lines are correct)
- **N1 (false line):** "Busy cores remain a descriptive covariate. The 7,800-second program fits inside 9,000 seconds; no top-up or automatic repeat."
  - Since v2 the pitch is 620 s, so the program is 600 + 11×620 + 600 = **8,020 s**. That formula is from `quiet_predicate_campaign.py` lines 1471–1478.
  - The 7,800 string is hardcoded at `evidence_night.py:283` and was stale in the v2 notices too.
  - It does no harm here: 8,020 still fits in 9,000, and every absolute time Ed acts on (REQUEST through the dead-man) is printed correctly.
- **N2 (stale, incomplete):** the notice never mentions v3, the 620 s pitch, or the 0.5-busy-core non-observer predicate. That predicate refuses at the arm check or at t0, excludes an envelope at 30 core-seconds, and aborts after 2 consecutive exclusions, about 31 minutes after t0.
  - So "Busy cores remain a descriptive covariate" is literally consistent with `busy_cores_role: covariate_only`, but it leaves out that a busy process can now end the night early.
  - v3 is still identified, by path and sha256, in the digest lines. "No model, load generator, calibration-ledger session or measurement pack runs" is true.
  - No other v2 wording turned up.
- **Tier: NIT for this arm; fix before the next arm.** No action of Ed's depends on either line. The handback at H (which Fable approved) carries the full v3 description.
  - Proposed lane: make `render_notice` derive the span from the registration and name v3, the 620 s pitch and the predicate.
  - If the magistrate decides notice exactness is part of the consent, this becomes MATERIAL, and the only cure (code, PR, new H, re-prepare) costs the 07:00 slot.

## Q5 Other checks
- `RULED_REGISTRATIONS` at H: v3 (69321c69) is the live entry, with `binds_chain` True and no `superseded_by`. v1 and v2 each carry `superseded_by`, so a v2 plan would fail the ruled lookup (lines 129–131).
- `T0_NON_OBSERVER_SHARE_MAX` = 0.5 matches v3's `t0_non_observer_share_max` 0.5. The arm check imports the gate's own predicate (`machine_quiet_check`).
- `EVIDENCE_PLAN_PATH` points to `<custody>/night_plan.json`, which does not exist yet. That is expected: publish-install puts it there, and the probe plist reads the staged copy. The `verify` step should confirm the published copy hashes to 6193c6b6.
- Other roots exist under ~/night-custody: 20260920, 20260921-2238 and 20260922-2100. `active-campaigns` is empty. Retained-root and census checks are left to the tracked `check`. **NOT EXECUTED** by me: forbidden by the charge.
- LaunchAgents state: **NOT EXECUTED** (forbidden). The `verify` step covers it.

## Findings
- BLOCKER: none.
- MATERIAL: none.
- NIT: N1 (the 7,800 s figure is false; the true figure is 8,020 s). N2 (the notice omits the v3 predicate and pitch). File both as one render_notice lane before the next arm.
- Note: `check` must pass the 0.5-core machine-quiet predicate at arm time; a daemon busy then refuses the arm, as designed.
