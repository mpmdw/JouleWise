# Record 61 — Opus counter-review (gate-ledger row 6): Stage A evidence executor

Branch `feat/2026-09-19-stage-a-evidence-executor` @ `087bf3af` (base `0c529f99`), read-only in
`/Users/edr/code/JouleWise-wt-saopus-d0b83820`. 2026-09-19, ~25 min.

## Verdict: MERGE-WITH-FIXES — 2 blockers, 4 should_fix, 7 nits

The ruled shape is implemented faithfully: the registration table, the honest C1 metadata, the
chain-source measurement, the typed evidence receipt at both dispatch points, the disjoint-pair
sizing and its chi-square factors are all correct and independently verified below. Both blockers
are about the night that will actually run, not about the contract: one loses the whole pilot on the
first hiccup, the other silences the courier on the most likely t0 refusal.

## Blockers

**B1 — one failed `collect` (or one unproven per-envelope cleanup) destroys the pilot.**
`joulewise/quiet_predicate_campaign.py:431-436`: after each envelope the chain raises on
`cleanup_proven is False` and on `code != 0`, which exits the loop through `except` → `outcome =
"refused"`. If envelope 3 of 12 errors (all rounds errored → `collect` exits 1), envelopes 4–12
never run, `retained` ≤ 2 < `minimum_retained` 8 → `status: INCONCLUSIVE`, `s_upper: null`, no
top-up, ~2 h 10 m of window spent, `evidence_outcome.json` shows `outcome: refused`. The protocol
already has the named mechanism for this exact case — a bad envelope is excluded by
`incomplete_interior_support` — so continuing the frozen schedule is protocol-compliant and
aborting is not required by any ruling. Counterfactual/fix: record the failed envelope, continue the
frozen cadence, and abort only when the remaining envelopes can no longer reach `minimum_retained`.
Call site: `quiet_predicate_campaign.execute`, the two `raise ValueError` lines inside the loop.
Tested? `test_twelve_protocol_envelopes_one_recorder_no_load_and_cleanup` proves the happy path; no
test asserts what the night does with a mid-chain collector failure.

**B2 — a pre-`execute` chain refusal suppresses the courier entirely (no email at all).**
`scripts/run_night.py:_evidence_cleanup_error` runs whenever `chain.started` exists and the payload
is evidence. It calls `cleanup_groups(journal, …)`; when `night/evidence_processes.jsonl` does not
exist, `process_groups` raises `ValueError("evidence process journal missing")` — caught once inside
the loop, then raised again, uncaught, at `quiet_predicate_campaign.py:180` (`residue = … |
process_groups(path)`), escaping a function whose docstring says "fail closed". `run_courier` then
returns `last_error: "evidence outcome/cleanup unproven; courier suppressed: …"` and sends nothing.
That journal is created only inside `execute()`, i.e. *after* `verify_environment()` — so every
manifest/digest/protocol refusal at t0 (`EVIDENCE_REFUSED`, chain rc 2), which is the single most
likely night-one outcome, yields a night with no courier notification and no email. Counterfactual/
fix: `chain.started` present, journal absent ⇒ no group was ever launched ⇒ clean; let the courier
report the chain's refusal. Also make `cleanup_groups` return an error rather than raise at :180.

## Should fix

**S1 — pre-registration answer to Q3: yes, frozen parameters can move without the pinned digest.**
The protocol file is byte-pinned (`manifest_for` compares `files[PROTOCOL_PATH]` to
`night_gate.QPE01_PILOT_REGISTRATION_SHA256`), so N, settle, interior, the pairing rule, the
exclusion names and the stop-branch *names* are genuinely frozen. But the executed sizing constants
are **not read from it**: `size_block_two(s_upper, delta_j=1)` (:263) and `stop_branch(…,
smallest_share=.05, …)` with literal `24` and `1` (:269-283) hardcode δ, the multiplier 8, the
floor 3, the 24-pair stop and the 0.05-core share, and `validate_protocol` (:40-51) does not include
`sizing`, `stop_branches`, `start_drift_max_s`, `exclusions` or `power_interval_ms` in its frozen
set. The 0.05 share appears in the README and in code but **nowhere in the registration file**.
Editing δ to 0.5 in code at a new `measurement_head` changes block-two sizing with no registration
change, no digest change and no cold-gate ruling. Fix: read all five from the protocol and add
`sizing`/`stop_branches` to `validate_protocol`'s `fixed`.

**S2 — `killpg` on the `sudo -n powermetrics` group cannot succeed from a non-root collector.**
`scripts/sample_quiet_predicate_evidence.py:159` sets `_privilege_prefix = ("sudo","-n")`; the diff
changes `os.kill(self.process.pid, …)` to `os.killpg(…)` at :617 and :631 with only
`except ProcessLookupError`. Signalling a root-owned group as the user returns EPERM →
`PermissionError` escapes `PowerRecorder.stop`. In `cleanup_groups` the same EPERM *is* caught
(:173) but lands in `errors` → `cleanup_proven: False` → B1's hard abort. Net effect: the one
scenario teardown exists for (powermetrics outlives its collector) is exactly the scenario the
campaign cannot clear, and it ends the night. Fix: catch `PermissionError` in the recorder, and let
an un-signallable root group be an envelope exclusion, not a campaign abort.

**S3 — the ruled covariate recorder's journal is written and never reduced.** `record_covariates`
writes `night/evidence_busy_cores.jsonl`, but `pilot_summary` takes `busy_cores` from the
collector's in-round `observation.metrics.busy_cores` (`:341`) and never opens the recorder journal.
The recorder's `observer_cpu_s` rows are likewise unread. The file is inventoried and couriered, so
nothing is lost — but the artifact a reader will assume feeds the summary does not. Either join it or
say in the README that the summary's covariate comes from the round sampler.

**S4 — "amended only by cold-gate ruling" is enforced only by prose.** `RULED_REGISTRATIONS`
(`night_gate.py:46-52`) is an ordinary module constant; the binding clause lives in
`NIGHT_HANDBACK.md:135`. Nothing in the tests pins the table's membership, so a future seat can add
an entry in a routine diff. Cheap fix: a test asserting exactly the two ruled digests and their
`binds_chain` flags, naming the amendment rule.

## Nits

1. `stop_branch` re-imports `math` (:271) and `hard_exclusions` re-imports `re` (:209); both are
   module-level already.
2. `validate_protocol`'s `fixed` dict re-states 15 values that the byte digest already freezes — two
   sources of truth that can drift in opposite directions at the next reissue.
3. `pairs_above_3_pair_sd` (:340) scans `overlapping`, so it can name pair (2,3), which the protocol
   summary calls "every **original** adjacent pair". Diagnostic only, but the label overstates.
4. `scripts/night_chains/quiet_predicate_evidence.zsh:2` — "The sealed protocol owns every timing
   parameter" is true of timing and false of sizing (S1). Say "timing"; don't imply sizing.
5. A crashed evidence probe leaves the supervisor's default calibration-schema receipt, and the
   installer refuses with "probe receipt kind does not match payload kind", hiding the real
   `refusal_code: probe_worker_failed` (`night_agent_install.py:validate_evidence_probe_receipt`).
6. `night_gate.py:1193` catches bare `Exception` and maps every cause — including an unavailable or
   slow `git show` — to `night_chain_digest_mismatch`, a refusal code that names the wrong thing.
7. TOCTOU: the protocol is digest-checked in `manifest_for` and re-read unchecked in `main()` (:469).

## Verified correct (counter-checked, not assumed)

- **Receipt honesty (Q2).** C1's existing value is preserved exactly: `detail` stays the literal
  "D-166 registration hash passed" when the digest is D-166's and becomes
  "registration hash passed: QPE-01 …" otherwise (`night_gate.py:1434`); `registration_label`,
  `registration_ruling`, `registration_bound_chain_source_sha256` are additive. Grep confirms
  `:1434` is the only D-166 string reachable in a receipt, so **no receipt string says "D-166" under
  the evidence plan**. An unruled digest, or a non-binding registration under an evidence payload,
  refuses `night_refused_registration`.
- **Chain-source measurement is a real measurement.** `_check_chain_identity` runs
  `git -C <root> show <measurement_head>:scripts/night_chains/quiet_predicate_evidence.zsh`, hashes
  that, *and* hashes the working-tree file, and requires both to equal the wrapper's embedded
  `EVIDENCE_CHAIN_SOURCE_SHA256`. If the wrapper's literal disagrees, C5 refuses
  `night_chain_digest_mismatch` before C1 is reached — so a stale wrapper never reaches the
  registration comparison. Calibration wrappers take the untouched path.
- **Chi-square inversion (Q3).** Independently re-derived with a stdlib series inversion plus a
  200 000-interval Simpson integration of the χ² pdf: χ²₀.₁₀,₃ = 0.584374 (Simpson CDF 0.100000) →
  √(3/0.584374) = 2.2658; χ²₀.₁₀,₅ = 1.610308 (CDF 0.100000) → √(5/1.610308) = 1.7621. The
  implementation returns the same values to 6 dp across df 3–11. Minimum 4 pairs ⇒ df ≥ 3, inside
  the guard.
- **`busy_cores` never influence retention.** `hard_exclusions` reads only census, AC and
  `CPU_Speed_Limit`; `overlapping[…]["retained"]` reads only exclusions, `boot_id`, `os_build`;
  `pairs_above_3_pair_sd` names without excluding. No path from a busy-core value to `retained`.
- **Census self-trip (the record 45 caution).** `gen_evidence_night` runs `_census_clean` over the
  plan id, measurement root, custody root, chain path, plan path and template path; `NIGHT_DIR` is
  `custody_root/night`, so the collector's `--out` argv is covered transitively. No in-chain argv
  contains `codex|claude|t3` for the intended roots.
- **N < 8 courier summary.** `status: INCONCLUSIVE`, `s_upper: null`, `block_two_pairs: null`,
  `block_two_stop.outcome: "no decision"`, and summary.md states the retained counts; the courier
  prompt requires reporting an unset bound as a limitation. No sizing is emitted. Correct.

## Commands run

```
git log --oneline 0c529f99..087bf3af; git diff --stat/-- <paths> 0c529f99 087bf3af
.venv/bin/python -B -m unittest tests.test_night_gate tests.test_gen_evidence_night \
  tests.test_quiet_predicate_campaign tests.test_sample_quiet_predicate_evidence   # 142 tests OK
.venv/bin/python -B -m unittest tests.test_run_night                                # OK
.venv/bin/python -  (independent chi-square inversion + Simpson cross-check, above)
```
No writes outside `/tmp/magistrate-d0b83820/opus-counter-stagea/` and this file; no sudo,
powermetrics, collect or LaunchAgent action.
