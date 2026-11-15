"""The High Power path of block hp-01 (RL-149 sections 2.3 and 2.5; RL-155 section 5.2).

The kit's optional ``power_mode`` field, rule 6 at admission, the RESTORE_UNPROVEN stop, the runner's
PowerModeGuard around the legs on every exit path, the close's proof of powermode 0 and no marker, and
the committed ``cl-hp-01`` kit.

Every power command goes to the mock host's fake ``pmset``/``sudo``. A tripwire makes any test (and any
mutant) that would start a process naming pmset, sudo or kill fail, and ``os.kill``/``os.killpg`` raise:
nothing here reaches /usr/bin/pmset or signals a process. The host-state directory is overridden to a
temporary directory, so the fixed /Users/Shared/JouleWise/host-power path is never touched.
"""
from __future__ import annotations

import io
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import powermode
from joulewise.cadence import desk, kit as kitmod, legs as legsmod, stops as stopsmod
from scripts import align_r1_rehearsal as r1, cadence_legs_runner as runner
from tests.cadence.test_legs_runner import NEW_WINDOW, campaign_kit, local

TMP = os.environ.get("TMPDIR")
AUTO, HIGH, QUERY, LIST = (list(r1.PowerModeGuard.AUTO), list(r1.PowerModeGuard.HIGH), list(r1.PowerModeGuard.QUERY),
                           list(r1.PowerModeGuard.LIST))
KITS = runner.ROOT / "docs/process/cadence/kits"
HOST_ARGS = ("pmset", "sudo", "kill")


def hp_kit(validate=True, **template):
    kit = campaign_kit(validate=False, **template)
    kit["frozen"]["paths"].update({p: "3" * 64 for p in kitmod.POWER_MODE_PATHS})
    kit["inclusion_rules"].append({"id": "block_power_mode", "text": "The power mode is the block's: High Power."})
    kit["power_mode"] = 2
    return kitmod.validate_kit(kit) if validate else kit


class Tripwire:
    """No process naming pmset, sudo or kill starts, and no signal is sent, while a test runs."""

    def __init__(self, case):
        real_run, real_popen = subprocess.run, subprocess.Popen

        def check(argv):
            text = " ".join(map(str, argv)) if isinstance(argv, (list, tuple)) else str(argv)
            if any(word in text for word in HOST_ARGS):
                raise AssertionError(f"a test reached a host power or signal command: {text}")

        def run(argv, *a, **kw):
            check(argv)
            return real_run(argv, *a, **kw)

        class Popen(real_popen):
            def __init__(self, argv, *a, **kw):
                check(argv)
                super().__init__(argv, *a, **kw)

        def no_signal(*a, **kw):
            raise AssertionError(f"a test tried to signal a process: {a}")

        for target, value in (("subprocess.run", run), ("subprocess.Popen", Popen), ("os.kill", no_signal),
                              ("os.killpg", no_signal)):
            patcher = patch(target, value)
            patcher.start()
            case.addCleanup(patcher.stop)


class HostStateSandbox(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=TMP)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        env = patch.dict(os.environ, {powermode.HOST_STATE_ENV: str(self.root / "host-state-seam")})
        env.start()
        self.addCleanup(env.stop)
        Tripwire(self)


# --------------------------------------------------------------------------
# The kit field and the validator
# --------------------------------------------------------------------------
class KitFieldTests(HostStateSandbox):
    def test_v1_kits_validate_unchanged_and_are_automatic(self):
        for name in ("cl-dev-01", "cl-dev-02"):
            self.assertNotIn("power_mode", json.loads((KITS / f"{name}.json").read_bytes()))
            kit, sha = kitmod.load_kit(KITS / f"{name}.json")
            self.assertEqual(kitmod.power_mode(kit), kitmod.AUTOMATIC)
        self.assertEqual(kitmod.power_mode(campaign_kit()), 0)

    def test_power_mode_two_validates_and_explicit_zero_is_automatic(self):
        self.assertEqual(kitmod.power_mode(hp_kit()), kitmod.HIGH_POWER)
        zero = campaign_kit(validate=False)
        zero["power_mode"] = 0
        self.assertEqual(kitmod.power_mode(kitmod.validate_kit(zero)), 0)

    def test_power_mode_values_are_closed(self):
        for bad in (1, 3, -1, True, False, "2", 2.0, None, {"ac": 2}):
            kit = hp_kit(validate=False)
            kit["power_mode"] = bad
            with self.assertRaisesRegex(kitmod.KitError, r"power_mode: 0 \(Automatic\) or 2"):
                kitmod.validate_kit(kit)

    def test_high_power_kit_freezes_the_power_path_and_registers_rule_6(self):
        for path in kitmod.POWER_MODE_PATHS:
            kit = hp_kit(validate=False)
            del kit["frozen"]["paths"][path]
            with self.assertRaisesRegex(kitmod.KitError, "must freeze the power-mode path " + path):
                kitmod.validate_kit(kit)
        kit = hp_kit(validate=False)
        kit["inclusion_rules"] = [r for r in kit["inclusion_rules"] if r["id"] != "block_power_mode"]
        with self.assertRaisesRegex(kitmod.KitError, "block_power_mode"):
            kitmod.validate_kit(kit)

    def test_other_unknown_top_keys_still_refuse(self):
        kit = hp_kit(validate=False)
        kit["powermode"] = 2
        with self.assertRaisesRegex(kitmod.KitError, "unknown key 'powermode'"):
            kitmod.validate_kit(kit)
        kit = campaign_kit(validate=False)
        del kit["desk"]
        with self.assertRaisesRegex(kitmod.KitError, "missing key 'desk'"):
            kitmod.validate_kit(kit)


class AdmissionAndStopTests(HostStateSandbox):
    RESULT = {"leg_status": "complete", "g0_released": True, "decode_cap_reached": True}

    def test_rule_6_is_the_blocks_mode(self):
        two, zero = {**self.RESULT, "ac_powermode": {"value": 2}}, {**self.RESULT, "ac_powermode": {"value": 0}}
        self.assertTrue(legsmod.leg_admitted(two, contaminated=False, block_mode=2))
        self.assertFalse(legsmod.leg_admitted(zero, contaminated=False, block_mode=2))
        self.assertTrue(legsmod.leg_admitted(zero, contaminated=False))
        self.assertFalse(legsmod.leg_admitted(two, contaminated=False))
        for unobserved in (None, {"value": None}, {"value": True}, {"value": "2"}):
            self.assertFalse(legsmod.leg_admitted({**self.RESULT, "ac_powermode": unobserved}, contaminated=False,
                                                  block_mode=2), unobserved)

    def test_result_carries_restore_proven_only_when_given(self):
        self.assertNotIn("restore_proven", legsmod.span_result(rc=0, planned=3, finished=3, fault=False))
        self.assertIs(legsmod.span_result(rc=0, planned=3, finished=3, fault=False, restore_proven=True)
                      ["restore_proven"], True)
        self.assertIn("restore_proven", desk.RESULT_KEYS)

    def test_restore_unproven_stop(self):
        rules = campaign_kit()["stop_rules"]
        meter = {"present": True, "proven_stopped": True, "bad_polls": 0, "usb_errors": 0}
        base = {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": False, "outcome": "MEASURED_OK"}
        span = lambda result: {"result": result, "meter": meter, "feeds_proven_stopped": True, "legs": []}  # noqa: E731
        self.assertIn("RESTORE_UNPROVEN", stopsmod.CODES)
        self.assertEqual(stopsmod.evaluate_named_stops(rules, span({**base, "restore_proven": True})), [])
        self.assertEqual(stopsmod.evaluate_named_stops(rules, span(base)), [])          # an Automatic span
        fired = stopsmod.evaluate_named_stops(rules, span({**base, "restore_proven": False}))
        self.assertEqual([s["code"] for s in fired], ["RESTORE_UNPROVEN"])


# --------------------------------------------------------------------------
# The runner's High Power path, on the mock host's fake power world
# --------------------------------------------------------------------------
class HighPowerSpanTests(HostStateSandbox):
    def span(self, name="hp", kit=None, faults=(), leg_ids=None, mutate=None, pre=None, t0="2026-11-15T13:20",
             deadline=None):
        """One span on the mock host. ``mutate(deps, out)`` edits the deps before the span; ``pre(deps)`` runs at
        the span's ``frozen`` step (the output directory exists; no host step has run yet)."""
        kit = kit or hp_kit()
        out = self.root / name
        clock = runner.FakeClock(local(t0))
        deps = runner.mock_deps(out, clock, power_faults=faults)
        deps.max_span_s = runner.max_span_s()
        if mutate:
            mutate(deps, out)
        if pre:
            frozen = deps.verify_frozen

            def verify(kit):
                pre(deps)
                return frozen(kit)
            deps.verify_frozen = verify
        plan = legsmod.plan_span(kit, t0_epoch=clock.time(), windows=NEW_WINDOW, leg_ids=leg_ids)
        rc = runner.run_span(kit=kit, kit_sha256="f" * 64, output=out, windows=NEW_WINDOW, deps=deps, leg_ids=leg_ids,
                             deadline=deadline(clock) if deadline else runner.launch_deadline(plan))
        receipt = json.loads((out / runner.RECEIPT_NAME).read_text())
        summary, stops = desk.build_desk(plan_id="t", input_dir=out / runner.DESK_BUNDLE, out_dir=out / "desk",
                                         adapter="leg-summary-v1", stop_rules=kit["stop_rules"])
        return out, rc, receipt, deps, summary, stops

    def commands(self, deps):
        return [c["argv"] for c in deps.host.power_calls]

    def assert_proven_automatic(self, receipt, deps):
        proof = receipt["high_power"]["close_proof"]
        self.assertEqual((proof["ac_powermode"], proof["host_marker_present"], proof["proven"]), (0, False, True))
        self.assertIs(receipt["span_result"]["restore_proven"], True)
        self.assertEqual(deps.host.mode, 0)
        self.assertFalse(deps.host.host_marker_path().exists())
        self.assertTrue(powermode.HostLock(deps.host.state_dir / "night.lock", role="probe").acquire())  # released

    def test_full_span_runs_its_legs_in_high_power_and_proves_automatic_at_the_close(self):
        out, rc, receipt, deps, summary, stops = self.span()
        self.assertEqual(rc, 0, receipt.get("error"))
        self.assertEqual(stops, [])
        names = [s["name"] for s in receipt["steps"]]
        # Preflight order: the lock and the marker check before any feed; the guard after read_power.
        self.assertLess(names.index("condition13"), names.index("host_lock"))
        self.assertLess(names.index("host_lock"), names.index("high_power_marker_absent"))
        self.assertLess(names.index("high_power_marker_absent"), names.index("start-agents"))
        self.assertLess(names.index("read_power"), names.index("powermode_guard"))
        self.assertLess(names.index("powermode_guard"), names.index("soak"))
        # High Power is set after the soak and before the first leg; every leg attempt is checked first.
        self.assertEqual(names[names.index("soak") + 1:names.index("soak") + 4],
                         ["high_power", "before-L001-agents", "before-L001-meter"])
        for i in range(1, 13):
            self.assertEqual(names[names.index(f"L{i:03d}.a1") - 1], f"L{i:03d}.a1-powermode")
        # The close: guard restore, proof, lock release, then the feeds.
        last = names.index("L012.a1")
        self.assertEqual(names[last + 1:last + 8], ["power_last_look", "restore", "power_proof", "host_lock_release",
                                                    "stop-volumes", "stop-meter", "stop-agents"])
        # The soak ran in Automatic and every leg recorded High Power; every leg is admitted under rule 6.
        self.assertEqual(deps.fake.soak_modes, [0])
        self.assertTrue(all(leg["admitted"] for leg in summary["legs"]))
        self.assertEqual(len(summary["legs"]), 12)
        # The fake power commands, in order: the rule listed, Automatic proved, then marker-first High Power.
        cmds = self.commands(deps)
        self.assertEqual(cmds[:3], [LIST, AUTO, QUERY])
        high = cmds.index(HIGH)
        self.assertEqual(cmds[high - 1], QUERY)
        self.assertTrue(deps.host.power_calls[high]["marker_present"], "the marker predates powermode 2")
        self.assertEqual(deps.host.power_calls[high]["mode"], 0)
        self.assertEqual(cmds.count(HIGH), 1)
        self.assertEqual(cmds[-4:], [QUERY, AUTO, QUERY, QUERY])   # the last look, restore, read-back, proof
        self.assertEqual(receipt["high_power"]["before_restore"]["marker_is_this_spans"], True)
        self.assertNotIn("revoked", receipt["high_power"])
        self.assert_proven_automatic(receipt, deps)
        hp = receipt["high_power"]
        self.assertEqual(hp["block_power_mode"], 2)
        self.assertEqual(hp["restore"], {"action": "restore_automatic", "ok": True, "deferred": False, "attempts": 1})
        self.assertEqual([r["point"] for r in hp["guard"]][-2:], ["restore_automatic", "after_restore_automatic"])

    def test_the_marker_names_this_span_and_is_an_owed_restore_for_every_later_session(self):
        seen = {}

        def mutate(deps, out):
            real = deps.run_leg

            def leg(attempt_dir, *a):
                marker = deps.host.host_marker_path()
                seen.update(text=marker.read_text(), mode=deps.host.mode)
                # A session start while the span holds the host lock never restores under it.
                other = powermode.HostLock(deps.host.state_dir / "night.lock", role="session start")
                seen["session_start"] = powermode.restore_owed([marker], runner=deps.host.pmset, lock=other,
                                                               reason="session_start")
                return real(attempt_dir, *a)
            deps.run_leg = leg
        out, rc, receipt, deps, *_ = self.span(leg_ids=["L001"], mutate=mutate)
        self.assertEqual(rc, 0, receipt.get("error"))
        self.assertEqual(seen["mode"], 2)
        self.assertTrue(seen["text"].startswith(powermode.R1_MARKER_TEXT + "\n"))   # an owed restore, not a W1 night's
        self.assertFalse(seen["text"].startswith(powermode.W1_MARKER_TAG))
        owner = json.loads(seen["text"].splitlines()[1])
        self.assertEqual((owner["writer"], owner["campaign_id"], owner["output"]), ("cadence span", "cl-test-01", str(out)))
        self.assertEqual(seen["session_start"]["action"], "deferred_measuring_night")
        self.assert_proven_automatic(receipt, deps)

    def test_a_killed_runner_leaves_a_marker_that_the_next_session_start_restores(self):
        # SIGKILL skips every close. What survives is the marker written before powermode 2.
        host = runner.FakeHost(self.root / "killed", power_faults=())
        lock = host.host_lock()
        self.assertTrue(lock.acquire())
        guard = runner.power_guard_class()(host.power_runner(), host.host_marker_path(), lock=lock,
                                           owner={"writer": "cadence span"})
        guard.__enter__()
        guard.high()
        lock.release()                      # the kernel drops the flock when the process dies
        self.assertEqual(host.mode, 2)
        self.assertFalse(powermode.w1_marker(host.host_marker_path()))   # an R1-tag marker: owed, not a W1 night's
        obs = {"high_power_marker": host.host_marker_path().exists(), "powermode": host.mode}
        lines = {line["kind"]: line["ok"] for line in kitmod.evaluate_checklist(hp_kit(), obs, expected_kit_sha256="")}
        self.assertEqual((lines["no_high_power_marker"], lines["powermode_zero"]), (False, False))
        record = powermode.restore_owed([host.host_marker_path()], runner=host.pmset,
                                        lock=powermode.HostLock(host.state_dir / "night.lock"), reason="session_start")
        self.assertEqual(record["action"], "restored")
        self.assertEqual(host.mode, 0)
        self.assertFalse(host.host_marker_path().exists())

    # --- every other exit path ------------------------------------------------------------------
    def test_a_leg_runtime_failure_restores_and_proves(self):
        def mutate(deps, out):
            real = deps.run_leg

            def leg(attempt_dir, *a):
                if Path(attempt_dir).parent.name == "L002":
                    raise runner.LegRuntimeError("L002: leg runtime exit 3")
                return real(attempt_dir, *a)
            deps.run_leg = leg
        out, rc, receipt, deps, summary, stops = self.span(mutate=mutate)
        self.assertEqual(rc, 2)
        self.assertEqual(deps.fake.calls, ["L001"])
        self.assertEqual([s["code"] for s in stops], ["REFUSAL"])
        self.assert_proven_automatic(receipt, deps)

    def test_sigterm_in_a_leg_restores_and_proves(self):
        def mutate(deps, out):
            real = deps.run_leg

            def leg(attempt_dir, *a):
                if Path(attempt_dir).parent.name == "L003":
                    # The span's own installed handler, called as a delivered SIGTERM would call it.
                    signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None)
                return real(attempt_dir, *a)
            deps.run_leg = leg
        out, rc, receipt, deps, summary, stops = self.span(mutate=mutate)
        self.assertEqual(rc, 128 + signal.SIGTERM)
        self.assertIn("SystemExit", receipt["error"])
        self.assertEqual(deps.fake.calls, ["L001", "L002"])
        self.assert_proven_automatic(receipt, deps)

    def test_a_work_deadline_after_high_power_restores_and_proves(self):
        out, rc, receipt, deps, *_ = self.span(deadline=lambda clock: clock.time() + 7200)
        self.assertEqual(rc, 2)
        self.assertIn("plan needs", receipt["error"])
        self.assertNotIn(HIGH, self.commands(deps))            # refused before the soak: never set
        # The entered guard (which already ran one Automatic restore) restores again at the close.
        self.assertEqual(self.commands(deps), [LIST, AUTO, QUERY, AUTO, QUERY, QUERY])
        self.assertEqual(receipt["high_power"]["restore"]["action"], "restore_automatic")
        self.assert_proven_automatic(receipt, deps)

    def test_set_high_failure_restores_the_marker_it_wrote(self):
        out, rc, receipt, deps, summary, stops = self.span(faults=("high_fails",))
        self.assertEqual(rc, 2)
        self.assertIn("high_failed", receipt["error"])
        self.assertEqual(deps.fake.calls, [])
        self.assertTrue(next(c for c in deps.host.power_calls if c["argv"] == HIGH)["marker_present"])
        self.assert_proven_automatic(receipt, deps)

    def test_powermode_that_does_not_read_back_two_refuses_before_any_leg(self):
        out, rc, receipt, deps, *_ = self.span(faults=("high_ignored",))
        self.assertEqual(rc, 2)
        self.assertIn("high_unconfirmed", receipt["error"])
        self.assertEqual(deps.fake.calls, [])
        self.assert_proven_automatic(receipt, deps)

    def test_a_mode_change_mid_span_stops_before_the_next_leg(self):
        def mutate(deps, out):
            real = deps.run_leg

            def leg(attempt_dir, *a):
                value = real(attempt_dir, *a)
                if Path(attempt_dir).parent.name == "L002":
                    deps.host.mode = 0               # something outside the span restored Automatic
                return value
            deps.run_leg = leg
        out, rc, receipt, deps, summary, stops = self.span(mutate=mutate)
        self.assertEqual(rc, 2)
        self.assertIn("High Power not held", receipt["error"])
        self.assertEqual(deps.fake.calls, ["L001", "L002"])
        # F3: L002 ran with the mode changed under it, so it is not admitted; L001 (checked after it) stands.
        admitted = {leg["leg_id"]: leg["admitted"] for leg in summary["legs"]}
        self.assertEqual(admitted, {"L001": True, "L002": False})
        self.assertFalse(json.loads((out / "legs/L002/leg_summary.json").read_text())["admitted"])
        self.assertEqual([r["leg_id"] for r in receipt["high_power"]["revoked"]], ["L002"])
        self.assertIn("at the check after the leg", receipt["high_power"]["revoked"][0]["reason"])
        self.assert_proven_automatic(receipt, deps)

    def test_a_missing_marker_mid_span_stops_before_the_next_leg(self):
        def mutate(deps, out):
            real = deps.run_leg

            def leg(attempt_dir, *a):
                value = real(attempt_dir, *a)
                deps.host.host_marker_path().unlink()
                return value
            deps.run_leg = leg
        out, rc, receipt, deps, summary, stops = self.span(mutate=mutate)
        self.assertEqual(rc, 2)
        self.assertEqual(deps.fake.calls, ["L001"])
        self.assertEqual([(leg["leg_id"], leg["admitted"]) for leg in summary["legs"]], [("L001", False)])
        self.assert_proven_automatic(receipt, deps)

    def test_a_held_host_lock_refuses_and_issues_no_mode_command(self):
        def pre(deps):
            other = powermode.HostLock(deps.host.state_dir / "night.lock", role="another measuring night")
            self.assertTrue(other.acquire())
            self.addCleanup(other.release)
        out, rc, receipt, deps, summary, stops = self.span(pre=pre)
        self.assertEqual(rc, 2)
        self.assertIn("host night lock is held", receipt["error"])
        self.assertEqual(self.commands(deps), [QUERY])        # the read-only close proof only
        self.assertEqual(receipt["high_power"]["restore"]["action"], "none")
        self.assertTrue(receipt["high_power"]["close_proof"]["proven"])
        self.assertEqual(deps.feeds[0].events, ["stop"])      # no feed started

    def test_a_marker_present_at_preflight_refuses_untouched_and_the_stop_fires(self):
        def pre(deps):
            powermode.write_host_marker(deps.host.host_marker_path(), tag=powermode.W1_MARKER_TAG,
                                        owner={"custody_root": "/elsewhere"})
            deps.host.mode = 2                     # a W1 session's High Power, not this span's
        out, rc, receipt, deps, summary, stops = self.span(pre=pre)
        self.assertEqual(rc, 2)
        self.assertIn("High Power marker is present", receipt["error"])
        self.assertEqual(self.commands(deps), [QUERY])        # never restored, never overwritten
        self.assertTrue(powermode.w1_marker(deps.host.host_marker_path()))
        self.assertEqual(deps.host.mode, 2)
        self.assertIs(receipt["span_result"]["restore_proven"], False)
        self.assertIn("RESTORE_UNPROVEN", [s["code"] for s in stops])

    def test_a_stale_marker_at_automatic_refuses_and_the_proof_fails_on_the_marker_alone(self):
        def pre(deps):
            powermode.write_host_marker(deps.host.host_marker_path(), tag=powermode.R1_MARKER_TEXT)
        out, rc, receipt, deps, summary, stops = self.span(pre=pre)
        self.assertEqual(rc, 2)
        proof = receipt["high_power"]["close_proof"]
        self.assertEqual((proof["ac_powermode"], proof["host_marker_present"], proof["proven"]), (0, True, False))
        self.assertEqual({s["name"]: s["rc"] for s in receipt["steps"]}["power_proof"], 2)
        self.assertIn("RESTORE_UNPROVEN", [s["code"] for s in stops])

    def test_a_host_at_high_power_without_a_marker_refuses_and_the_proof_fails_on_the_mode_alone(self):
        def pre(deps):
            deps.host.mode = 2
        out, rc, receipt, deps, summary, stops = self.span(pre=pre)
        self.assertEqual(rc, 2)
        self.assertIn("requires observed Automatic", receipt["error"])        # read_power refused
        self.assertEqual(self.commands(deps), [QUERY])
        proof = receipt["high_power"]["close_proof"]
        self.assertEqual((proof["ac_powermode"], proof["host_marker_present"], proof["proven"]), (2, False, False))
        self.assertIn("RESTORE_UNPROVEN", [s["code"] for s in stops])

    def test_a_w1_marker_found_after_the_lock_retake_is_never_undone(self):
        def mutate(deps, out):
            real = deps.run_leg

            def leg(attempt_dir, *a):
                value = real(attempt_dir, *a)
                powermode.write_host_marker(deps.host.host_marker_path(), tag=powermode.W1_MARKER_TAG,
                                            owner={"custody_root": "/a-w1-session"})
                return value
            deps.run_leg = leg
        out, rc, receipt, deps, summary, stops = self.span(leg_ids=["L001"], mutate=mutate)
        self.assertEqual(rc, 2)
        self.assertEqual(receipt["high_power"]["restore"],
                         {"action": "restore_automatic", "ok": False, "deferred": True, "attempts": 1})
        # The marker after L001 is not this span's, so L001 loses its admission at the close's last look.
        self.assertEqual([r["leg_id"] for r in receipt["high_power"]["revoked"]], ["L001"])
        self.assertFalse(summary["legs"][0]["admitted"])
        self.assertEqual(receipt["high_power"]["guard"][-1]["point"], "restore_deferred")
        self.assertEqual(self.commands(deps).count(AUTO), 1)         # only the entry's proof; never the W1 mode
        self.assertTrue(powermode.w1_marker(deps.host.host_marker_path()))
        self.assertIn("RESTORE_UNPROVEN", [s["code"] for s in stops])

    def test_a_missing_sudo_rule_refuses_before_any_mode_command(self):
        out, rc, receipt, deps, *_ = self.span(faults=("sudo_rule_missing",))
        self.assertEqual(rc, 2)
        self.assertIn("sudo_rule_missing", receipt["error"])
        self.assertEqual(self.commands(deps), [LIST, QUERY])
        self.assert_proven_automatic(receipt, deps)

    def test_a_journal_failure_at_the_close_still_restores(self):
        def mutate(deps, out):
            real_start = legsmod.StageJournal.start

            def start(journal, stage_id, *a, **kw):
                if stage_id == "restore":
                    raise OSError(28, "No space left on device")
                return real_start(journal, stage_id, *a, **kw)
            patcher = patch.object(legsmod.StageJournal, "start", start)
            patcher.start()
            self.addCleanup(patcher.stop)
        out, rc, receipt, deps, *_ = self.span(leg_ids=["L001"], mutate=mutate)
        self.assertEqual(rc, 2)
        self.assert_proven_automatic(receipt, deps)

    # --- cold seat fixes F1 to F6 -------------------------------------------------------------------
    def test_f3_a_mode_change_after_the_last_leg_revokes_it_at_the_close(self):
        def mutate(deps, out):
            real = deps.run_leg

            def leg(attempt_dir, *a):
                value = real(attempt_dir, *a)
                if Path(attempt_dir).parent.name == "L003":
                    deps.host.mode = 0
                return value
            deps.run_leg = leg
        out, rc, receipt, deps, summary, stops = self.span(leg_ids=["L001", "L002", "L003"], mutate=mutate)
        self.assertEqual(rc, 0, receipt.get("error"))
        self.assertEqual([(leg["leg_id"], leg["admitted"]) for leg in summary["legs"]],
                         [("L001", True), ("L002", True), ("L003", False)])
        self.assertEqual(receipt["high_power"]["before_restore"]["ac_powermode"], 0)
        self.assertEqual([r["leg_id"] for r in receipt["high_power"]["revoked"]], ["L003"])
        self.assert_proven_automatic(receipt, deps)

    def test_f4_a_transient_close_restore_failure_is_retried(self):
        out, rc, receipt, deps, summary, stops = self.span(faults=("close_restore_fails_once",), leg_ids=["L001"])
        self.assertEqual(rc, 0, receipt.get("error"))
        self.assertEqual(receipt["high_power"]["restore"],
                         {"action": "restore_automatic", "ok": True, "deferred": False, "attempts": 2})
        self.assertEqual(stops, [])
        self.assert_proven_automatic(receipt, deps)

    def test_f4_the_retry_is_bounded(self):
        out, rc, receipt, deps, summary, stops = self.span(faults=("close_restore_fails",), leg_ids=["L001"])
        self.assertEqual(receipt["high_power"]["restore"]["attempts"], 3)
        cmds = self.commands(deps)
        self.assertEqual(cmds[cmds.index(HIGH):].count(AUTO), 3)
        self.assertIn("RESTORE_UNPROVEN", [s["code"] for s in stops])

    def test_f4_a_restore_that_raises_is_retried(self):
        def mutate(deps, out):
            real, raised = deps.host.pmset, []

            def pmset(argv):
                if list(argv) == AUTO and deps.host.mode == 2 and not raised:
                    raised.append(True)
                    raise subprocess.TimeoutExpired(argv, 15)
                return real(argv)
            deps.host.pmset = pmset
        out, rc, receipt, deps, *_ = self.span(leg_ids=["L001"], mutate=mutate)
        self.assertEqual(rc, 0, receipt.get("error"))
        self.assertEqual(receipt["high_power"]["restore"]["attempts"], 2)
        self.assertIn("restore_raised", [r["point"] for r in receipt["high_power"]["guard"]])
        self.assert_proven_automatic(receipt, deps)

    def test_f5_a_second_signal_while_the_close_starts_cannot_skip_it(self):
        real_signal, fired, at_close = signal.signal, [], []

        def signal_once(signum, handler):
            if signum == signal.SIGINT and handler == signal.SIG_IGN and not fired:
                fired.append(True)
                signal.getsignal(signal.SIGINT)(signal.SIGINT, None)   # a second signal arriving now
            return real_signal(signum, handler)

        def mutate(deps, out):
            real = deps.run_leg

            def leg(attempt_dir, *a):
                if Path(attempt_dir).parent.name == "L002":
                    signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None)
                return real(attempt_dir, *a)
            deps.run_leg = leg
            real_pmset = deps.host.pmset

            def pmset(argv):
                if list(argv) == AUTO and deps.host.mode == 2:      # the close's restore
                    at_close.append({s: signal.getsignal(s) for s in runner.SIGNALS})
                return real_pmset(argv)
            deps.host.pmset = pmset
            patcher = patch.object(runner.signal, "signal", signal_once)
            patcher.start()
            self.addCleanup(patcher.stop)
        out, rc, receipt, deps, summary, stops = self.span(mutate=mutate)
        self.assertEqual(fired, [True])
        self.assertEqual(rc, 128 + signal.SIGTERM)
        self.assertEqual(receipt["late_signals"], [f"SystemExit: {128 + signal.SIGINT}"])
        self.assertEqual(at_close, [{s: signal.SIG_IGN for s in runner.SIGNALS}])   # every signal ignored
        self.assert_proven_automatic(receipt, deps)

    def test_f6_a_mode_change_during_the_soak_refuses_before_the_marker(self):
        def mutate(deps, out):
            real = deps.run_soak

            def soak(*a):
                value = real(*a)
                deps.host.mode = 2
                return value
            deps.run_soak = soak
        out, rc, receipt, deps, *_ = self.span(mutate=mutate)
        self.assertEqual(rc, 2)
        self.assertIn("not_automatic_before_high", receipt["error"])
        self.assertNotIn(HIGH, self.commands(deps))
        self.assertEqual(deps.fake.calls, [])
        self.assert_proven_automatic(receipt, deps)

    def test_f6_a_marker_that_is_not_this_spans_stops_the_span(self):
        def mutate(deps, out):
            real = deps.run_leg

            def leg(attempt_dir, *a):
                value = real(attempt_dir, *a)
                powermode.write_host_marker(deps.host.host_marker_path(), tag=powermode.R1_MARKER_TEXT,
                                            owner={"writer": "R1 driver"})
                return value
            deps.run_leg = leg
        out, rc, receipt, deps, summary, stops = self.span(mutate=mutate)
        self.assertEqual(rc, 2)
        self.assertIn("'marker_is_this_spans': False", receipt["error"])
        self.assertEqual(deps.fake.calls, ["L001"])
        self.assertEqual([(leg["leg_id"], leg["admitted"]) for leg in summary["legs"]], [("L001", False)])

    def test_f1_an_absent_proof_on_a_high_power_span_is_a_stop(self):
        out, rc, receipt, deps, summary, stops = self.span(leg_ids=["L001"])
        self.assertEqual(stops, [])
        (out / runner.DESK_BUNDLE / "span/result.json").unlink()        # a receipt lost with the result
        for mode, expect in ((2, ["REFUSAL", "RESTORE_UNPROVEN"]), (0, ["REFUSAL"])):
            _, fired = desk.build_desk(plan_id="t", input_dir=out / runner.DESK_BUNDLE, out_dir=out / f"desk{mode}",
                                       adapter="leg-summary-v1", stop_rules=hp_kit()["stop_rules"], block_mode=mode)
            self.assertEqual(sorted(s["code"] for s in fired), expect)

    def test_f1_the_air_desk_reads_the_blocks_mode_from_the_kit(self):
        from scripts.air import cadence_desk
        out, rc, receipt, deps, summary, stops = self.span(leg_ids=["L001"])
        (out / runner.DESK_BUNDLE / "span/result.json").unlink()
        kit_path = self.root / "hp-kit.json"
        kit_path.write_text(json.dumps(hp_kit(), indent=1))
        with patch("sys.stdout", io.StringIO()) as stdout:
            code = cadence_desk.main(["build", "--plan-id", "t", "--input", str(out / runner.DESK_BUNDLE),
                                      "--out", str(self.root / "air-desk"), "--kit", str(kit_path),
                                      "--lock", str(self.root / "AIR-QUIET.lock")])
        self.assertEqual(code, 3)
        self.assertIn("STOP RESTORE_UNPROVEN", stdout.getvalue())

    def test_f2_the_marker_names_the_restore_and_when_it_is_safe(self):
        seen = {}

        def mutate(deps, out):
            real = deps.run_leg

            def leg(attempt_dir, *a):
                seen["owner"] = powermode.marker_owner(deps.host.host_marker_path())
                return real(attempt_dir, *a)
            deps.run_leg = leg
        self.span(leg_ids=["L001"], mutate=mutate)
        self.assertEqual(seen["owner"]["restore_with"], runner.RESTORE_OWED_COMMAND)
        self.assertEqual(seen["owner"]["safe_when"], runner.RESTORE_OWED_SAFE_WHEN)
        line = next(x for x in kitmod.evaluate_checklist(hp_kit(), {"high_power_marker": True}, expected_kit_sha256="")
                    if x["kind"] == "no_high_power_marker")
        self.assertFalse(line["ok"])
        self.assertIn("scripts/cadence_legs_runner.py restore-owed", line["detail"])
        self.assertIn("LaunchAgent job has exited", line["detail"])

    # --- RL-155 section 5.2's extra line: a failing restore at the close, and the stop fires -----
    def test_a_failing_close_restore_keeps_the_marker_and_fires_restore_unproven(self):
        out, rc, receipt, deps, summary, stops = self.span(faults=("close_restore_fails",), leg_ids=["L001", "L002", "L003"])
        self.assertEqual(rc, 2)
        self.assertEqual(deps.fake.calls, ["L001", "L002", "L003"])
        self.assertTrue(all(leg["admitted"] for leg in summary["legs"]))     # the legs themselves stand
        proof = receipt["high_power"]["close_proof"]
        self.assertEqual((proof["ac_powermode"], proof["host_marker_present"], proof["proven"]), (2, True, False))
        self.assertIs(receipt["span_result"]["restore_proven"], False)
        self.assertEqual(sorted(s["code"] for s in stops), ["REFUSAL", "RESTORE_UNPROVEN"])
        self.assertTrue(deps.host.host_marker_path().exists())       # the owed restore stays durable
        rows = {s["name"]: s for s in receipt["steps"]}
        self.assertEqual((rows["restore"]["rc"], rows["power_proof"]["rc"], rows["host_lock_release"]["rc"]), (2, 2, 0))
        self.assertTrue(powermode.HostLock(deps.host.state_dir / "night.lock", role="probe").acquire())

    def test_a_restore_that_does_not_read_back_zero_keeps_the_marker_and_fires_the_stop(self):
        out, rc, receipt, deps, summary, stops = self.span(faults=("close_restore_ignored",), leg_ids=["L001"])
        self.assertEqual(rc, 2)
        self.assertEqual(receipt["high_power"]["restore"]["ok"], False)
        self.assertIn("RESTORE_UNPROVEN", [s["code"] for s in stops])
        self.assertTrue(deps.host.host_marker_path().exists())

    def test_mock_cli_fail_close_restore(self):
        kit_path = self.root / "hp-kit.json"
        kit_path.write_text(json.dumps(hp_kit(), indent=1))
        with patch("sys.stdout", io.StringIO()) as stdout:
            rc = runner.main(["mock", "--kit", str(kit_path), "--output", str(self.root / "cli"),
                              "--t0-local", "2026-11-15T13:20", "--batch-window", "02:00-02:35",
                              "--legs", "L001,L002,L003", "--fail-close-restore"])
        printed = json.loads(stdout.getvalue())
        self.assertEqual(rc, 2)
        self.assertIn("RESTORE_UNPROVEN", [s["code"] for s in printed["stops"]])
        with patch("sys.stdout", io.StringIO()) as stdout:
            rc = runner.main(["mock", "--kit", str(kit_path), "--output", str(self.root / "cli-ok"),
                              "--t0-local", "2026-11-15T13:20", "--batch-window", "02:00-02:35",
                              "--legs", "L001,L002,L003"])
        self.assertEqual((rc, json.loads(stdout.getvalue())["stops"]), (0, []))

    # --- an Automatic kit is untouched ----------------------------------------------------------
    def test_an_automatic_kit_never_touches_the_power_world(self):
        out, rc, receipt, deps, summary, stops = self.span(kit=campaign_kit())
        self.assertEqual(rc, 0, receipt.get("error"))
        self.assertEqual(deps.host.power_calls, [])
        self.assertNotIn("high_power", receipt)
        self.assertNotIn("restore_proven", receipt["span_result"])
        names = [s["name"] for s in receipt["steps"]]
        for name in ("host_lock", "high_power_marker_absent", "powermode_guard", "high_power", "power_proof",
                     "host_lock_release", "L001.a1-powermode"):
            self.assertNotIn(name, names)
        self.assertEqual(deps.host.calls[-1], "restore")


class UnprovenChildStopTests(HostStateSandbox):
    """``run_child``'s "process group not proven stopped" refusal (PR #789 row-1 LOW 1; RL-157 Q2 condition 1).

    The leg goes through the real ``run_child`` with a fake ``Popen`` (no process starts), a stubbed
    ``PartDeadline`` (no watchdog thread, nothing it could signal) and an injected terminator that cannot
    prove the group stopped for L002. The tripwire stays on: no real process or signal is involved."""

    class FakePopen:
        next_pid = 4_000_000          # beyond any real pid; never signalled (the terminator is injected)

        def __init__(self, argv, **kw):
            self.argv = list(argv)
            self.pid = UnprovenChildStopTests.FakePopen.next_pid
            UnprovenChildStopTests.FakePopen.next_pid += 1
            self.returncode = None

        def poll(self):
            self.returncode = 0
            return 0

        def wait(self, timeout=None):
            self.returncode = 0
            return 0

    class FakeDeadline:
        fired_for = ()               # legs whose deadline watchdog "fired" and could not prove the group stopped

        def __init__(self, child, **kw):
            self.child = child

        def start(self):
            pass

        def expired(self):
            return False

        def cancel(self):
            if self.child.argv[-1] in self.fired_for:
                return {"fired": True, "pgid": self.child.pid, "proven": False, "injected": True}
            return None

    def span(self, kit, fired_for=()):
        from scripts import run_align_r1_smoke as smoke, run_night as night
        terminated = []
        self.FakeDeadline.fired_for = tuple(fired_for)
        self.addCleanup(setattr, self.FakeDeadline, "fired_for", ())

        def terminator(child, evidence=None, **kw):
            proven = "L002" not in child.argv[-1]
            evidence.update(pgid=child.pid, proven=proven, injected=True)
            terminated.append((child.argv[-1], proven))
            return proven
        patches = [patch.object(runner.subprocess, "Popen", self.FakePopen),
                   patch.object(smoke, "PartDeadline", self.FakeDeadline),
                   patch.object(night, "_terminate_process_group", terminator)]
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)

        out = self.root / "unproven"
        clock = runner.FakeClock(local("2026-11-15T13:20"))
        deps = runner.mock_deps(out, clock)
        deps.max_span_s = runner.max_span_s()
        fake_leg = deps.run_leg

        def run_leg(attempt_dir, spec_path, soak_reference, cap_s, feeds, work_remaining):
            leg_dir = Path(attempt_dir).parent
            result = runner.run_child(name=f"{leg_dir.name}.a1", argv=["fake-leg-runtime", leg_dir.name], cap_s=cap_s,
                                      log_dir=leg_dir, feeds=feeds, work_remaining=work_remaining)
            self.assertTrue(result["proven_stopped"])
            return fake_leg(attempt_dir, spec_path, soak_reference, cap_s, feeds, work_remaining)
        deps.run_leg = run_leg
        plan = legsmod.plan_span(kit, t0_epoch=clock.time(), windows=NEW_WINDOW)
        rc = runner.run_span(kit=kit, kit_sha256="f" * 64, output=out, deadline=runner.launch_deadline(plan),
                             windows=NEW_WINDOW, deps=deps)
        receipt = json.loads((out / runner.RECEIPT_NAME).read_text())
        summary, stops = desk.build_desk(plan_id="t", input_dir=out / runner.DESK_BUNDLE, out_dir=out / "desk",
                                         adapter="leg-summary-v1", stop_rules=kit["stop_rules"])
        return out, rc, receipt, deps, summary, stops, terminated

    def check_refusal(self, out, rc, receipt, summary, stops, terminated):
        # (a) the refusal names the leg attempt
        self.assertEqual(rc, 2)
        self.assertIn("SpanRefusal: L002.a1 process group not proven stopped", receipt["error"])
        row = next(r for r in receipt["steps"] if r["name"] == "L002.a1")
        self.assertEqual(row["rc"], 2)
        self.assertIn("L002.a1 process group not proven stopped", row["error"])
        if terminated is not None:
            self.assertEqual(terminated, [("L001", True), ("L002", False)])
        # (b) the attempt is neither summarized nor counted finished; nothing after it runs
        self.assertFalse((out / "legs/L002/leg_summary.json").exists())
        self.assertFalse((out / runner.DESK_BUNDLE / "legs/L002").exists())
        self.assertEqual([leg["leg_id"] for leg in summary["legs"]], ["L001"])
        legs = {leg["leg_id"]: leg for leg in receipt["legs"]}
        self.assertNotIn("summary", legs["L002"])
        self.assertNotIn("L003", legs)
        self.assertEqual((receipt["legs_finished"], receipt["span_result"]["verdict"]), (1, "1/12 legs run"))
        self.assertEqual(receipt["span_result"]["chain_outcome"], "INCOMPLETE")
        self.assertIn("REFUSAL", [s["code"] for s in stops])

    def test_an_unproven_leg_group_refuses_the_span_on_an_automatic_kit(self):
        out, rc, receipt, deps, summary, stops, terminated = self.span(campaign_kit())
        self.check_refusal(out, rc, receipt, summary, stops, terminated)
        self.assertEqual(deps.host.calls[-1], "restore")

    def test_an_unproven_leg_group_still_restores_and_proves_automatic_in_high_power(self):
        out, rc, receipt, deps, summary, stops, terminated = self.span(hp_kit())
        self.check_refusal(out, rc, receipt, summary, stops, terminated)
        # (c) the close still restores Automatic and proves powermode 0 and no marker
        self.assertEqual(receipt["high_power"]["restore"],
                         {"action": "restore_automatic", "ok": True, "deferred": False, "attempts": 1})
        proof = receipt["high_power"]["close_proof"]
        self.assertEqual((proof["ac_powermode"], proof["host_marker_present"], proof["proven"]), (0, False, True))
        self.assertIs(receipt["span_result"]["restore_proven"], True)
        self.assertNotIn("RESTORE_UNPROVEN", [s["code"] for s in stops])
        self.assertEqual((deps.host.mode, deps.host.host_marker_path().exists()), (0, False))
        self.assertEqual([c["argv"] for c in deps.host.power_calls][-4:], [QUERY, AUTO, QUERY, QUERY])


    def test_a_fired_deadline_that_cannot_prove_the_group_stopped_refuses_and_still_proves_automatic(self):
        # The deadline watchdog's own teardown (``PartDeadline.cancel`` returns its record) is the proof
        # run_child uses when it fired; an unproven one refuses exactly as the terminator's does.
        out, rc, receipt, deps, summary, stops, terminated = self.span(hp_kit(), fired_for=("L002",))
        self.assertEqual(terminated, [("L001", True)])           # the injected terminator never ran for L002
        self.check_refusal(out, rc, receipt, summary, stops, None)
        self.assertIn("'fired': True", receipt["error"])
        self.assertIs(receipt["span_result"]["restore_proven"], True)
        self.assertEqual((deps.host.mode, deps.host.host_marker_path().exists()), (0, False))


class RestoreOwedTests(HostStateSandbox):
    """Cold seat F2: ``cadence_legs_runner.py restore-owed``, the human's restore after a span died without its
    close. The host-state directory is the test seam; the pmset world is the fake host's."""

    def setUp(self):
        super().setUp()
        self.host = runner.FakeHost(self.root / "host-state-seam")
        patcher = patch.object(powermode, "_run", self.host.pmset)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.marker = Path(powermode.host_marker_path())
        self.assertEqual(self.marker, self.host.host_marker_path())

    def test_a_dead_spans_marker_is_restored_and_proven(self):
        powermode.write_host_marker(self.marker, tag=powermode.R1_MARKER_TEXT, owner={"writer": "cadence span"})
        self.host.mode = 2
        with patch("sys.stdout", io.StringIO()) as stdout:
            rc = runner.main(["restore-owed"])
        record = json.loads(stdout.getvalue())
        self.assertEqual((rc, record["action"], record["after"]["proven"]), (0, "restored", True))
        self.assertEqual((self.host.mode, self.marker.exists()), (0, False))

    def test_it_defers_while_a_night_holds_the_lock_and_refuses_a_w1_marker(self):
        powermode.write_host_marker(self.marker, tag=powermode.R1_MARKER_TEXT, owner={"writer": "cadence span"})
        self.host.mode = 2
        other = powermode.HostLock(role="a measuring night")
        self.assertTrue(other.acquire())
        record, proven = runner.restore_owed()
        other.release()
        self.assertEqual((record["action"], proven, self.host.mode), ("deferred_measuring_night", False, 2))
        powermode.write_host_marker(self.marker, tag=powermode.W1_MARKER_TAG, owner={"custody_root": "/w1"})
        record, proven = runner.restore_owed()
        self.assertEqual((record["action"], proven, self.host.mode), ("refused", False, 2))
        # A deferred restore with the host already at 0 still leaves the marker: not proven.
        powermode.write_host_marker(self.marker, tag=powermode.R1_MARKER_TEXT, owner={"writer": "cadence span"})
        self.host.mode = 0
        self.assertTrue(other.acquire())
        record, proven = runner.restore_owed()
        other.release()
        self.assertEqual((record["action"], record["after"]["ac_powermode"], proven), ("deferred_measuring_night", 0, False))
        self.assertNotIn(AUTO, [c["argv"] for c in self.host.power_calls])


class ProductionSeamTests(HostStateSandbox):
    def test_production_power_seams_are_the_fixed_paths_and_the_narrow_rule(self):
        from scripts import run_align_r1_smoke as smoke
        host = runner.ProductionHost("fake-pmset")
        self.assertIs(host.power_runner(), smoke.host_run)        # identity only; never called here
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop(powermode.HOST_STATE_ENV, None)
            self.assertEqual(host.host_marker_path(), Path("/Users/Shared/JouleWise/host-power/high-power.marker"))
            lock = host.host_lock()
            self.assertEqual((lock.path, lock.held), ("/Users/Shared/JouleWise/host-power/night.lock", False))
        guard = runner.power_guard_class()
        self.assertTrue(issubclass(guard, r1.PowerModeGuard))
        self.assertEqual((guard.AUTO, guard.HIGH), (("sudo", "-n", "/usr/bin/pmset", "-c", "powermode", "0"),
                                                    ("sudo", "-n", "/usr/bin/pmset", "-c", "powermode", "2")))

    def test_the_tripwire_holds(self):
        with self.assertRaisesRegex(AssertionError, "host power or signal command"):
            subprocess.run(["/usr/bin/pmset", "-g", "custom"])
        with self.assertRaisesRegex(AssertionError, "signal a process"):
            os.kill(os.getpid(), 0)


# --------------------------------------------------------------------------
# The committed kit cl-hp-01
# --------------------------------------------------------------------------
class CommittedHighPowerKitTests(HostStateSandbox):
    def load(self, name, window=kitmod.OS_BATCH_WINDOW):
        return kitmod.load_kit(KITS / f"{name}.json", batch_window=window)

    def test_cl_hp_01_mirrors_dev_01_cell_for_cell_in_high_power(self):
        hp, _ = self.load("cl-hp-01")
        self.load("cl-hp-01", NEW_WINDOW[0])
        dev, _ = self.load("cl-dev-01")
        self.assertEqual((hp["campaign_id"], kitmod.power_mode(hp), hp["ruling"]),
                         ("cl-hp-01", 2, {"id": "RL-149 §2", "authorizes_spans": True}))
        self.assertEqual(len(hp["legs"]), 12)
        cell = lambda kit: {(leg["prefill_tokens"], leg["decode_tokens"], leg["start_band"]) for leg in kit["legs"]}  # noqa: E731
        self.assertEqual(cell(hp), cell(dev))
        for key in ("model", "leg_defaults", "span_template", "checklist", "looks", "desk", "runner"):
            self.assertEqual(hp[key], dev[key], key)
        self.assertEqual({k: v for k, v in hp["seed_law"].items() if k != "master_seed"},
                         {k: v for k, v in dev["seed_law"].items() if k != "master_seed"})
        self.assertNotEqual(hp["seed_law"]["master_seed"], dev["seed_law"]["master_seed"])
        self.assertLessEqual(set(dev["frozen"]["paths"]), set(hp["frozen"]["paths"]))
        ids = [r["id"] for r in hp["inclusion_rules"]]
        for rule in ("block_power_mode", "hp_smoke_counted", "never_in_the_fit"):
            self.assertIn(rule, ids)
        self.assertNotIn("pilot_counted", ids)
        rule6 = next(r["text"] for r in hp["inclusion_rules"] if r["id"] == "block_power_mode")
        self.assertIn("powermode 2", rule6)
        for words in ("the runner survives", "SIGKILL", "restore-owed", "withdrawn", "absent proof"):
            self.assertIn(words, rule6)                     # cold seat F7 and F3
        # RL-161: the master seed is unique among the kits (2026111403 collided with cl-dev-03's on #788).
        self.assertEqual(hp["seed_law"]["master_seed"], 2026111404)
        others = [json.loads(path.read_text())["seed_law"]["master_seed"] for path in KITS.glob("*.json")
                  if path.name != "cl-hp-01.json"]
        self.assertNotIn(2026111404, others + [2026111403])
        self.assertEqual(kitmod.deny_scan(hp), [])

    def test_spans_plan_inside_the_launch_ceiling(self):
        hp, _ = self.load("cl-hp-01")
        pilot = legsmod.plan_span(hp, t0_epoch=local("2026-11-15T13:20"), windows=NEW_WINDOW,
                                  leg_ids=["L001", "L002", "L003"], max_span_s=runner.max_span_s())
        rest = legsmod.plan_span(hp, t0_epoch=local("2026-11-16T13:20"), windows=NEW_WINDOW,
                                 leg_ids=[f"L{i:03d}" for i in range(4, 13)], max_span_s=runner.max_span_s())
        self.assertEqual((pilot["expected_s"], pilot["worst_case_s"]), (6903, 16650))
        self.assertEqual((rest["expected_s"], rest["worst_case_s"]), (14409, 32850))

    def test_frozen_paths_hash_at_the_frozen_commit(self):
        hp, _ = self.load("cl-hp-01")
        have = subprocess.run(["git", "-C", str(runner.ROOT), "cat-file", "-e", hp["frozen"]["commit"] + "^{commit}"],
                              capture_output=True)
        if have.returncode:
            self.skipTest("frozen commit not in this clone")
        self.assertEqual(kitmod.verify_frozen(hp, runner.ROOT), [])

    def test_mock_span_on_the_committed_kit(self):
        hp, sha = self.load("cl-hp-01")
        rc, summary, stops, deps = runner.run_mock(kit=hp, kit_sha256=sha, output=self.root / "kit-mock",
                                                   t0_epoch=local("2026-11-15T13:20"), windows=NEW_WINDOW,
                                                   leg_ids=["L001", "L002", "L003"])
        self.assertEqual((rc, stops), (0, []))
        self.assertTrue(all(leg["admitted"] for leg in summary["legs"]))
        rc, summary, stops, deps = runner.run_mock(kit=hp, kit_sha256=sha, output=self.root / "kit-mock-fail",
                                                   t0_epoch=local("2026-11-15T13:20"), windows=NEW_WINDOW,
                                                   leg_ids=["L001", "L002", "L003"], power_faults=("close_restore_fails",))
        self.assertEqual(rc, 2)
        self.assertIn("RESTORE_UNPROVEN", [s["code"] for s in stops])


if __name__ == "__main__":
    unittest.main()
