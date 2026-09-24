# 29 — A280 PR A contract lens, round 1 (Opus 5.5 subagent), head 702afd8d

Transcribed by the magistrate from the subagent's final report (brief 24). Scratch lives under `/tmp/a280lens/`.

**Verdict:** no blockers; 3 should-fix; 5 nits. The idle artifacts are behaviour-preserving. The claim that the table is "fit for PR B" is overstated.

## Executed evidence
- **E1 names and signatures** (base vs head archives). `evidence_night.KIND`, `night_gate.EVIDENCE_CHAIN_PATH`, `QPE01_PILOT_REGISTRATION_PATH`, and `quiet_predicate_campaign.PROTOCOL_PATH`, `CHAIN_PATH`, `HARNESS_PATHS` and `MANIFEST_SCHEMA` are identical, and so are all signatures. Diffs: `MANIFEST_PATHS` gains `joulewise/night_kinds.py` only; `NIGHT_KINDS` and `kind_row` are added; `scripts.gen_evidence_night.manifest_for` is gone.
- **E2 refusal text.** An AST comparison of every raise, `Refused`, `Refusal` and `GenerationRefusal` expression (evidence_night 270/270, night_gate 143/143, quiet_predicate_campaign 46/46, gen_evidence_night 15/15) shows an empty diff in all four.
- **E3 goldens reproduced independently.** All 8 artifacts equal the stored goldens; a fresh `git archive cdc05e9b` reproduces H `0aed0da3…`.
- **E4 committed head.** `tests.test_night_kinds` 3 OK. The composition tests (`LifecycleCompositionTests` plus three `PrepareTests`) 4 OK; record 16's composition error is gone at the committed H. The base control is also OK.
- **E5 cross-head manifest matrix.** Head code accepts the head manifest and refuses the base manifest (`CalledProcessError` from `git show …:joulewise/night_kinds.py`). Base code refuses the head manifest (`ValueError manifest per-file digests differ from measurement_head`) and accepts the base manifest. The head file list = the base list + `night_kinds.py`.
- **E6** a patched third row (`scored_campaign`): `kind_row` works, but `night_gate.probe_payload_kind("export NIGHT_PAYLOAD_KIND=scored_campaign\n")` raises `ValueError probe payload kind ambiguous`.

## Clause table
K1 immutable/typed: MET (night_kinds.py:16-17, :25-45, :47, :91-95). K1 "every per-kind fact": PARTIAL (the notice subject label `EVIDENCE` at evidence_night.py:295 and the idle-only notice sentences at :330, :334-337, :338, :341 are not in the row). K2 sites read the table: PARTIAL (`probe_payload_kind` night_gate.py:150-162 and `KIND` evidence_night.py:28 look up a constant key; E6). K2 same refusal text: MET. K2 imported names: MET. K2 deferred sites listed: MET. K3: MET (test_night_kinds.py:203-236, :238-244). K4: MET, one nit (N4). K5: MET for what was run. R1: MET (quiet_predicate_campaign.py:86; E5). R2: MET (night_gate.py:29; the fixture change is only tests/test_evidence_night.py:877). The `except ModuleNotFoundError` left in evidence_night's H-side snippets at :248, :517 and :1032 is reachable only when H predates the table, and it uses the caller's row: acceptable.

## Findings
- **S1** Payload recognition is not driven by the table (night_gate.py:150-162; E6). Fix: accept any `NIGHT_KINDS` payload key (identical with two rows), or relabel it deferred.
- **S2** The arm check keys BOTH the corecaptured and the machine-quiet check on `corecaptured_at_arm_and_t0` (evidence_night.py:1359-1374), while t0 keys the 30 s predicate on `non_observer_at_arm_and_t0` (night_gate.py:1549-1550). This breaks `machine_quiet_check`'s "same predicate as t0" contract (:1066-1075) for any row whose flags differ. Identical today; one-line split.
- **S3** Not fit for PR B without further refactoring. Sites bound to `KIND` or to the literal: `locations` (:158-166), `prior_records` (:219, :231), `sealed_candidate` (:240, :246), `notice_subject` (:295), `render_notice` (:299), the census snippet (:1031), `notice_unused` (:1655). `render_notice` emits idle-only sentences unconditionally (:330, :334-337, :341), and the corecaptured t0 sentence (:338) is not keyed on its flag. Fix in PR A or list them in PR B's brief.
- **N1** quiet_predicate_campaign.py:161 adds a Python window pin (`or plan.window_max_s != row.window_max_s`), contradicting §1.2; it cannot fire today.
- **N2** The calibration row's `plan_id_prefix=""`/`measurement_root_suffix=""` (night_kinds.py:71-72) match everything; use `None`.
- **N3** Test hygiene: the fixed `/tmp/jwkindfixture` is removed on every run, so concurrent runs race; `TZ`/`tzset()` are never restored; the `JW_KIND_BASE_SOURCE` override cannot work because the goldens embed `/tmp/jwkindbase`.
- **N4** `scripts.gen_evidence_night` no longer re-exports `manifest_for` (no importer found).
- **N5** Head code checking a base manifest refuses through an uncaught `CalledProcessError`; night_agent_install.py:1177-1179 catches only `(OSError, ValueError)`. Pre-existing, fails closed, not a production path.

## R3 (the 82-file survey)
Real but narrow: **should-fix in its own lane, not a PR A blocker.** `measurement_head` fingerprints every tracked file, and `checkout_ok` (evidence_night.py:148-155) checks the tree clean, untracked files included, at prepare and at the arm check (:626). The t0 gate compares only `rev-parse HEAD` (night_gate.py:1241-1261), and the per-file comparison (`tracked_bytes`, quiet_predicate_campaign.py:96-102) covers only the 9 manifested files. So a working-tree change to an executing, unmanifested file between the arm check and t0 goes undetected; the most material case is `corecaptured_loop.count_spawns`. The likelihood is low (a dedicated clone; D-161 operator-only adversary). Cure: one clean-tree check (`git status --porcelain=v1 --untracked-files=all`) in the H clone at t0 or in `verify_environment`. That closes the class, including shadowing untracked modules. Extending `MANIFEST_PATHS` by a static over-approximation is the wrong tool.

## Double-check
Decide S1 and S2 in PR A (one line each, behaviour-preserving). Carry S3 into PR B's brief. The live watchdog (PID 43172) imports only `night_gate` names that still exist (magistrate_watchdog.py:40-46), so a canonical fast-forward does not force a restart.
