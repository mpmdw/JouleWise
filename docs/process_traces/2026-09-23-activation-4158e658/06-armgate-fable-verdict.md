# ARM GATE — cold Fable 5.1 final pass — activation 4158e658 — qpe01-pilot-n1-20260923-0700

Judge: fresh Fable 5.1 instance, read-only, foreground only. Probes run 2026-09-23 05:13–05:17 PDT.
Nothing outside this file was written; no launchctl/sudo/evidence_night subcommand was executed.

## Q1 Bindings — PASS
- night_plan.json (sha256 6193c6b6…b566 recomputed, matches): repo_head = measurement_head =
  26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15 = H; plan_id qpe01-pilot-n1-20260923-0700; t0_epoch_s
  1790172000; window_max_s 9000; registration_path …/pilot_protocol_v3.json; custody_root and
  measurement_root exactly the two paths named in the brief; receipt_class DIAGNOSTIC_NO_PACK.
- `git -C <clone> rev-parse HEAD` = H. `git status --porcelain` empty. `git diff --stat 3a411784 H
  -- joulewise scripts configs` prints nothing.
- `shasum -a 256 <clone>/configs/…/pilot_protocol_v3.json` = 69321c69…3616 (ruled digest).
- prepare.json (sha256 39b9382f…f067 matches) frozen_triple = (plan_id, clone, H); bindings block
  carries the same registration digest and chain_source_sha256 568a2771…b7ea. Every one of the nine
  sealed digests in prepare.json re-verified byte-for-byte (all OK).

## Q2 Wrapper / chain — PASS
- Custody chain.zsh exists (sha256 464697de… = chain.zsh.sha256 = prepare digest), exports
  NIGHT_PAYLOAD_KIND=quiet_predicate_evidence, refuses on NIGHT_PLAN_ID / MEASUREMENT_ROOT /
  MEASUREMENT_HEAD mismatch (all three literals = plan values), re-hashes the clone's
  scripts/night_chains/quiet_predicate_evidence.zsh against 568a2771…b7ea before `exec /bin/zsh` on it.
- Chain bytes at H: `shasum` on the working file and `git show H:scripts/night_chains/…zsh | shasum`
  both = 568a2771…b7ea = v3 registration `chain_source_sha256` = wrapper pin = manifest entry.
- evidence_manifest.json: all 8 file digests re-verified against the clone at H (all OK);
  measurement_head H; plan_id matches.
- Chain itself: exports the payload kind, requires PY/EVIDENCE_PLAN_PATH/EVIDENCE_MANIFEST_SHA256,
  execs `joulewise.quiet_predicate_campaign run`.

## Q3 Schedule — PASS
- com.joulewise.night.plist: Month 9 Day 23 Hour 7 Minute 0; deadman plist Hour 10 Minute 35;
  both ProgramArguments[0] = <clone>/.venv/bin/python (absolute, inside the clone; sha256
  d483cfdc… = prepare interpreter sha; Python 3.13.1); run_night.py at H; --plan points at the
  custody night_plan.json; courier-bin /Users/edr/.local/share/claude/versions/2.1.280 exists, executable.
- Boundaries vs t0=1790172000 (07:00:00 PDT confirmed by `date -r`): install close 1790171400
  (t0−600, 06:50), REQUEST 1790171520 (t0−480), TERM 1790171640 (t0−360), KILL 1790171700 (t0−300),
  window end 1790181000 (t0+9000 = 09:30), courier 1790181300 (+300 = 09:35), dead-man 1790184900
  (+3600 = 10:35 = deadman calendar). All consistent.
- Program fit: settle 600 + 11×620 + 600 = 8020 s ≤ 9000 (quiet_predicate_campaign fit rule).

## Q4 Notice — one stale figure (NIT)
- Truthful: registration v3 path + ruled digest listed; twelve 600 s envelopes, 480 s interiors,
  60 s offsets, 600 s settle; 100 ms power sampling; busy-cores journal; no model / load generator /
  calibration session / pack; no top-up; provisional; every boundary line correct.
- FALSE/STALE LINE (evidence_night.py:283 at H, hard-coded literal):
  "Busy cores remain a descriptive covariate. The 7,800-second program fits inside 9,000 seconds; no top-up or automatic repeat."
  The program is 8,020 s (600 + 11×620 + 600), not 7,800 (600 + 12×600, pre-pitch arithmetic). The
  620 s pitch is not stated. It still fits and no boundary Ed acts on is affected. Also omitted
  (not false): the 0.5-core t0 non-observer predicate and the v3 per-process busy exclusion with
  abort-after-2; "descriptive covariate" is true only of the aggregate busy_cores statistic.
  Cure needs a code change (new H), so it is NOT worth this window: lane it.

## Q5 Other — nothing blocking
- night_gate.py at H: v3 entry keyed 69321c69…, binds_chain True, v2 (2c539240…) and v1 carry
  superseded_by → any v2 arm refused. No pilot_protocol_v2 pin in joulewise/scripts/configs
  (only historical prose in NIGHT_HANDBACK.md). T0_NON_OBSERVER_SHARE_MAX = 0.5 present.
- Retained roots: 20260922-0217 and 20260922-2100 both have chain.exited + courier.sent +
  result.json (terminal); 20260921-2238 has no night_plan.json so is not inventoried;
  active-campaigns empty. Nothing ACTIVE/UNKNOWN visible to `retained_roots` from here.
- v2 and v3 pin the same chain bytes (568a2771…) — expected, chain unchanged; v3 differences
  live in the campaign module, which the manifest pins (8c0afbb8…).
- Runway: now 05:16 PDT, install close 06:50 — 94 min, above the 40-min default.

## Findings
- NIT-1: notice line "The 7,800-second program…" understates the program by 220 s and omits the
  620 s pitch; derive the figure from the registration (settle_s + (envelopes−1)·slot_pitch_s +
  envelope_s) in a follow-up PR; not a cure for this arm.
- NIT-2: notice does not name the 0.5-core t0 predicate or the v3 per-process busy abort; same lane.

## Verdict: ARM
