# BFG-D round 8: test hermeticity on hosts with no battery (lead contract)

**Defect, found by hosted CI on #424.** Hosted CI runs on Linux, where `/usr/sbin/ioreg` does not exist. Run 36242000950 had 24 errors or failures:
- `tests.test_evidence_night` PrepareTests: 15;
- `tests.test_night_kinds` NightKindTests: 4;
- `tests.test_run_night` NightDriverTests: 5 (`test_installer_refuses_*`).

Each one reaches the real installer's battery check (`night_agent_install.validate_install`) or another production battery probe, which then refuses with `battery not at float: FileNotFoundError … /usr/sbin/ioreg`. The refusal fires before the refusal the test is asserting on.

These tests pass on the Mac only because the Mac is at float at the moment they run. **The local suite therefore depends on the host battery's state.** That is a hermeticity defect. It is not a gate defect: the gate is right to refuse.

**Closure shape (tests only):**
1. Every test that drives a production path containing a battery probe must supply the fixture runner. This covers both in-process calls and subprocesses such as the zsh-wrapped installer.
   - Extend the existing mechanism in `tests/battery_float_fixture.py` (injection for in-process calls; the fake-HOME user-site runner for child Pythons) to every such test, including these three modules' subprocess launches.
   - If a child interpreter disables the user site, or the installer's child environment cannot be reached from tests, **stop and report NEEDS_RULING** with the exact production seam you would need. Do not add a production environment-variable bypass of the battery gate on your own.
2. Tests that assert a *battery* refusal keep asserting it, with the charging or missing fixture injected explicitly.
3. **Proof of hermeticity, required:**
   - Run `tests.test_evidence_night`, `tests.test_night_kinds`, `tests.test_run_night`, `tests.test_install_night_agent`, `tests.test_night_agent_install` and `tests.test_arm_readiness_evidence_t0` **twice**.
     - (a) Once normally.
     - (b) Once with the host probe made to fail. In a /tmp copy of the repo, set `battery_float.IOREG_BATTERY_ARGV`'s binary to a nonexistent path, then run the six modules from that copy. This simulates Linux.
   - Both runs must be green. Paste both tails.
   - Then grep `tests/` for any other test that reaches a production battery probe without a fixture. Run each module you find under (b) as well.
4. Never weaken an assertion. List every expected-value edit.

**Rules.**
- WRITE_SCOPE: `tests/**` only.
- Pin proof unchanged: `git diff --stat cab01506 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs scripts/paper_anchor_correction_quantified.py` must be empty.
- No full discovery.
- One foreground session.
