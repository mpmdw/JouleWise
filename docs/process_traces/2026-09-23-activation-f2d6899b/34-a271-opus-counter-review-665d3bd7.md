# A271 at 665d3bd7: Opus 5.5 counter-review, gate-ledger row 6 (condensed hand-back, filed at the bookkeeping gate)

**Verdict: MERGEABLE AFTER FIXES.**

**Tests:** 123 passed with 163 subtests (tests/test_corecaptured_loop.py, tests/test_night_gate.py, tests/test_arm_retry.py), plus one test_evidence_night test. The two-dot and three-dot diffs against ea4995d5 have the same sha, `cbed1ce0…`, so the merge lost no A234 hunk.

**Earlier findings:**
- **B1 closed.** Actuation requires item 0 and every earlier row to pass (evidence_night.py:1096).
- **S1 closed**, except for one new stale text (S-2 below). Both policy blocks equal render_policy().
- **S2** was decided by ruling 16 Q2.
- **S3** is closed as a recorded deviation (record 28:161).
- **S4 closed.**
- **S5 closed.**

**Should-fix:**
- **S-1.** A rehearsal check moves the real machine. Under a fixture launchctl, item 0 is decided by the fake while the Wi-Fi toggle and the sudo restart go to the production actuator. Executed: LifecycleTests.kw uses `launchctl_bin="/fixture/launchctl"`, and `test_corecaptured_arm_toggles_once_and_counts_only_post_toggle_spawns` asserts one off and one on. Cure: stay read-only under a fake launchctl with the production actuator. **Cured in 7e29eb0d.**
- **S-2.** A234's zero-capture definition (NIGHT_HANDBACK.md:57, runbook:1856) lists the not-quiet causes without the corecaptured loop. **Cured in 7e29eb0d.** Also stale, and pre-existing: night_quiet_admission.md:261.
- **S-3.** Record 31's premise that the threshold is a "named code constant" was not implemented: bare literals remain. **Cured in 7e29eb0d** (corecaptured_loop constants).

**Nits:**
- **N-1.** The handback paragraph says "The check reads…" before naming which check. **Cured.**
- **N-2.** Two header-only fixtures are byte-identical. Kept as provenance.
- **N-3.** A post-toggle threshold of >= 1 assumes that turning Wi-Fi on never spawns corecaptured ("because xpc event") itself. The only evidence is the owner's single bench cure (0 spawns in 4 min). If turning Wi-Fi on does trigger a spawn, every toggle ends in a restart and a refusal. Log the first live toggle. NOT EXECUTED.
- **N-4.** The arm-to-t0 latent risk (record 13 N3) is unchanged.

**Consumers:**
- The nested `C3.measured["corecaptured"]` dict cannot veto or license A234's release, because the veto scans top-level keys only. It does not hit `_QUIET_RECEIPT_KEYS`.
- A t0 corecaptured refusal is `night_refused_not_quiet`, which is eligible for early release and the successor route, as Q2 intended.

**Overbuild:** minimal. The only candidate is N-2.
