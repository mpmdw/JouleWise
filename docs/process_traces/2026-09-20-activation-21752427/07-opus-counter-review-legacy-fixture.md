# Record 07 — Opus contract-lens counter-review of `d5f35ca1` (CI-LEGACY-FIXTURE-LINUX-01), 2026-09-20 ≈04:05 PDT

Reviewer: Opus 5 subagent (read-only, contract lens; brief in the magistrate's launch prompt: R1 same production branch, R2 guard placement, R3 the fixed `/tmp` sha256 path, R4 shared fixture convention, R5 commit-message accuracy). Verbatim report:

VERDICT: MERGE

FINDINGS

1. (nit — separate lane) `tests/test_install_night_agent.py:110` — `chain_sha256_path="/tmp/install-night-agent-test.sha256"` is the same class of defect the commit cures: a fixed absolute path outside the test root whose existence/content the test does not control. Currently inert: `tests/test_run_night.py:184` (`write_matching_probe_receipt`) rewrites both `chain_path` and `chain_sha256_path` to per-test files before any code reads the sidecar, and the missing-chain legacy branch takes `payload_kind == "calibration"`, which never reads it (`joulewise/night_agent_install.py:1172` is inside the evidence branch; :755/:893 are `probe_bindings`/`evidence_probe_bindings`, reached only after the rewrite). A leftover or foreign `/tmp/install-night-agent-test.sha256` on a shared runner would flip an OSError refusal into a mismatch refusal if any future test reaches those readers pre-rewrite. Not present on this machine (`ls` → No such file).

2. (nit — separate lane) `tests/test_magistrate_watchdog_cli.py:198` — `chain_path="/bin/true"`, the identical pattern. Verified `/bin/true` does not exist on macOS at all, so that fixture is platform-divergent by construction even though its module is currently green.

3. (nit — report only) No shared `NightPlan` fixture builder exists (R4).

R1. Yes, same branch. Production catches `except OSError:` around `chain_bytes = chain.read_bytes()` (`joulewise/night_agent_install.py:1150-1153`, comment "Legacy render fixtures may name an unavailable chain"), then `b"".decode("utf-8")` → `""` → `night_gate.probe_payload_kind("")` returns `"calibration"` (night_gate.py:78-79). A never-created path under `tempfile.TemporaryDirectory(dir="/tmp")` raises `FileNotFoundError` (an `OSError`, ENOENT) on macOS and Linux alike — identical to the old macOS-absent `/bin/true`.

R2. Placement is sound. The guard runs at the top of `_write_plan` (all 51 call sites), `self.root` is a fresh TemporaryDirectory per `setUp` (line 68), so no ordering effects. No false-failure vector found: nothing in the suite writes `legacy-missing-chain.zsh` (grep: the only occurrence is line 92), and the tests that do write to `parsed["chain_path"]` (lines 364-366, 390-392, 430) all run after `_prepare_receipt`, by which point the plan names `custody/probe-chain.zsh`, not the guarded path. Empirically 65/65 pass with the guard live.

R3. Yes — see finding 1; not fixed, as instructed.

R4. No convention was bypassed: `test_night_gate.py:147` and `test_magistrate_watchdog.py:124` each define their own local `make_plan`; there is no shared builder to have used. This module already imports its heavyweight fixtures from `tests/test_run_night.py`.

R5. Accurate, no overclaim. I reproduced the stimulus by pointing the fixture at `/usr/bin/true` (ELF on macOS): exactly 12 failures of 65, and all 12 carry the "night wrapper is not valid UTF-8" signature. Clean run on 3.13: `Ran 65 tests ... OK`. The message's 3.11 claim I did not re-verify.

## Magistrate disposition (04:08 PDT)
- Nit 1: registered for a separate lane (fixed `/tmp` sidecar path); inert today per the reviewer's executed trace.
- Nit 2: same-signature instance in `tests/test_magistrate_watchdog_cli.py:198` — see the bench decision in record 08 §3 (whether the module reaches the UTF-8 refusal on Linux decides if it joins this PR).
- Nit 3: no action.
