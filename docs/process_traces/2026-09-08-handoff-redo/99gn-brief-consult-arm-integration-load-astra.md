WRITE_SCOPE: []

# CONSULT — ARM-INTEGRATION-LOAD-01: readiness gates refuse under test-suite load (gpt-6-astra, HIGH, genre scout, read-only)

You are consulted as a design peer with explicit license to disagree with the lead. Read-only tree at 9e1c7280 (D-176 final head). Do NOT run the test suite; static reading plus small `python3 -c` probes only.

Observed today (four occurrences, same signature): when the full suite runs under `scripts/shard_tests.py --workers 4` while ANY other substantial process is active (a second replay, a codex seat's acceptance run, or even a reviewer agent + seat launching during shard start-up), one of these refuses and the test fails:
- `tests/test_arm_readiness_integration.py::ArmReadinessIntegrationTests::test_alpha_beta_gamma_end_to_end_pass_and_no_hash_cycle (profile='BETA')` — result `{'status': 'REFUSE', 'arm_disposition': 'NO_GO', 'reason_codes': ['readiness_clock_preflight_refused']}`; earlier occurrences refused on the machine census (`'REFUSE' != 'PASS'` with census reasons).
- `tests/test_launch_window.py` relocation tests and `test_real_minted_v4_launch…` (once).
All pass when the suite runs alone. The production gates (clock preflight, machine census) are load-sensitive BY DESIGN — a real ARM must refuse on a busy machine — so weakening them is not an option (soundness above all).

Questions:
1. Locate the exact preflight/census code paths these tests exercise (cite file:line): what does the clock preflight measure, with what threshold, and what does the census count? Which of those inputs does a 4-worker unittest burst plausibly perturb?
2. Options, each with a concrete sketch and the soundness argument:
   (a) Deterministic doubles at the integration seam: inject the preflight/census RESULTS (not skip them) via the existing dependency-injection points, while separate unit tests keep pinning the real probes' refusal behaviour under synthetic bad inputs. Name the injection points that already exist (e.g. `patch_pack_night_dependencies`, evidence-author hooks) and whether the integration test would still prove the end-to-end wiring.
   (b) Serialize: mark ARM-gated modules exclusive in `scripts/shard_tests.py` (there is precedent — `calibration-exits-exclusive` CI jobs) so they run alone after the shards; cite how the runner currently orders modules.
   (c) Accept + document: keep the current behaviour, require replays to run alone (the documented condition today).
3. Recommend ONE, or a combination, with the argument; state what a reviewer should refuse to accept (e.g. any change that makes the production preflight less strict).
4. Draft the TASK_QUEUE row text for the chosen fix (ID ARM-INTEGRATION-LOAD-01, lane, one-line what, acceptance).
Report under 900 words; header < 8192 bytes; end your turn after the report.
