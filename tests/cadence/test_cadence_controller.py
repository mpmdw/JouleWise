"""The standing-queue controller (scripts/cadence_controller.py): the real end-to-end runs (RL-172 (i) row 5), and a
regression for each controller-side gate finding (Sol 2026-11-15 #800 gate; Mythos #800 gate). Synthetic only: no
host command, no run bundle; the spans are the pinned runners' own mocks."""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

from joulewise.cadence import desk_transport, standing as law
from scripts import cadence_controller as cc, cadence_controller_synthetic as synth

ROOT = Path(__file__).resolve().parents[2]
HAVE_TOOLS = shutil.which("git") is not None and shutil.which("ssh-keygen") is not None
L = synth.L


def quiet(*_a, **_k):
    pass


class WorldCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def world(self, **kw):
        w = synth.World(Path(self.tmp.name) / "w", **kw)
        w.controller()
        return w

    def pilot_world(self, key="cl-dev-05", **kw):
        w = self.world(**kw)
        sid = "dev-04-s01" if key == "cl-dev-04" else "dev-05-s01"
        w.queue("pilot", [w.span(1, sid, key, L[:6])], role="smoke")
        return w

    def state(self, w, *parts):
        return Path(w.cfg["state_dir"]).joinpath(*parts)

    def pages(self, w):
        return json.dumps([p["reasons"] for p in w.ctl.unacked_pages()])


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class Gate6Controller(WorldCase):
    def prior_receipt_world(self, *, clean=False):
        w = self.pilot_world(prior_evidence=False)
        prior = w.standing['prior_spans'][-1]
        source = Path(w.cfg['output_root']) / prior['campaign_id'] / (prior['plan_id'] + '-20261116T180000Z')
        source.mkdir(parents=True)
        receipt = source / cc.RECEIPT
        receipt.write_text(json.dumps({
            'roster': prior['roster'], 'kit': {'sha256': prior['kit_sha256'],
                                            'campaign_id': prior['campaign_id']},
            'rc': 0 if clean else 9, 'error': None if clean else 'restore failed',
            'span_result': {'chain_exit_code': 0 if clean else 9,
                            'chain_outcome': 'COMPLETE' if clean else 'FAILED',
                            'fault': not clean, 'outcome': 'MEASURED_OK' if clean else 'FAILED'},
            'steps': [{'name': 'soak', 'rc': 0}, {'name': 'restore', 'rc': 0 if clean else 9}],
            'feeds': {'meter': {'stop': {'proven_stopped': clean}}},
            'legs_finished': len(prior['roster']), 'legs_planned': len(prior['roster']),
            'legs': [{'leg_id': lid, 'summary': {'g0_outcome': 'released'}} for lid in prior['roster']]}))
        ended = law.parse_time(prior['closed'])
        os.utime(receipt, (ended, ended))
        marker = synth.offload_marker(prior['plan_id'], w.env.now(), str(source))
        (Path(w.cfg['copy_marker_dir']) / (prior['plan_id'] + '.ok')).write_text(json.dumps(marker))
        return w

    def test_failed_prior_receipt_halts_despite_matching_identity_and_verified_copy(self):
        w = self.prior_receipt_world()
        status = w.tick()
        self.assertIn(status['state'], ('PAGED', 'HALTED'))
        self.assertIn('SPAN_BAD_TERMINAL', self.pages(w))
        self.assertEqual(w.launcher.launched, [])

    def test_clean_prior_receipt_still_allows_the_successor(self):
        w = self.prior_receipt_world(clean=True)
        status = w.tick()
        self.assertEqual(status['state'], 'LIVE', self.pages(w))

    def test_declared_predecessor_requires_its_own_receipt_and_copy(self):
        w = self.world(prior=False)
        pid = "cq-dev-04-s01-a1"
        w.standing["prior_spans"] = [{
            "plan_id": pid, "campaign_id": "cl-dev-04", "block_id": "dev-04",
            "kit_sha256": w.sha["cl-dev-04"], "roster": L[:6], "legs": 6, "mixed": True,
            "t0": "2026-11-17T03:30:00-08:00", "closed": "2026-11-17T07:00:00-08:00",
            "desk_final": "synthetic hand table",
        }]
        w.lead_release(pid, "class-a")
        w.lead_release(pid, "L005")
        w.queue("pilot", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6])], role="smoke")
        census = w.ctl.census()
        self.assertEqual(census["campaign"], [])
        self.assertIn("old-smoke", census["newest"][1])
        self.assertFalse((Path(w.cfg["copy_marker_dir"]) / f"{pid}.ok").exists())
        self.assertIn(w.tick()["state"], ("PAGED", "HALTED"))
        self.assertIn("RECEIPT_MISSING", self.pages(w))
        self.assertEqual(w.launcher.launched, [])

    def test_prior_receipt_path_must_match_its_campaign(self):
        w = self.prior_receipt_world(clean=True)
        prior = w.standing["prior_spans"][-1]
        receipt = Path(w.ctl.census()["campaign"][0])
        wrong_campaign = receipt.parent.parent.with_name("cl-dev-04")
        wrong_campaign.mkdir()
        source = receipt.parent.rename(wrong_campaign / receipt.parent.name)
        marker_path = Path(w.cfg["copy_marker_dir"]) / (prior["plan_id"] + ".ok")
        marker_path.write_text(json.dumps(synth.offload_marker(prior["plan_id"], w.env.now(), str(source))))
        self.assertIn(w.tick()["state"], ("PAGED", "HALTED"))
        self.assertIn("PRIOR_CONTRADICTS", self.pages(w))
        self.assertEqual(w.launcher.launched, [])

    def test_predecessor_copy_is_due_when_a_different_receipt_is_newer_on_disk(self):
        w = self.prior_receipt_world(clean=True)
        prior = w.standing["prior_spans"][-1]
        (Path(w.cfg["copy_marker_dir"]) / f"{prior['plan_id']}.ok").unlink()
        other = w.standing["prior_spans"][0]
        path = w.record_prior_close(other)
        newer = law.parse_time(prior["closed"]) + 300
        os.utime(path, (newer, newer))
        marker = synth.offload_marker(other["plan_id"], newer, str(path.parent))
        (Path(w.cfg["copy_marker_dir"]) / f"{other['plan_id']}.ok").write_text(json.dumps(marker))
        self.assertEqual(w.ctl.census()["campaign_newest"][1], str(path))
        status = w.tick()
        self.assertEqual(status["state"], "WAIT")
        self.assertIn("JOURNAL_COPY", status["detail"]["codes"])
        self.assertIn(prior["plan_id"], status["detail"]["detail"])
        self.assertEqual(w.launcher.launched, [])

    def test_duplicate_prior_restore_stages_hold_despite_successful_last_stage(self):
        for first_rc in (9, 0):
            with self.subTest(first_rc=first_rc):
                w = self.prior_receipt_world(clean=True)
                path = Path(w.ctl.census()["campaign"][0])
                receipt = json.loads(path.read_text())
                receipt["steps"].insert(1, {"name": "restore", "rc": first_rc})
                path.write_text(json.dumps(receipt))
                ended = law.parse_time(w.standing["prior_spans"][-1]["closed"])
                os.utime(path, (ended, ended))
                self.assertIn(w.tick()["state"], ("PAGED", "HALTED"))
                self.assertIn("CLOSE_UNPROVEN", self.pages(w))
                self.assertEqual(w.launcher.launched, [])

    def test_watchdog_removal_of_expired_fence_requires_acknowledgement(self):
        w = self.pilot_world(prior=False)
        self.assertEqual(w.ctl.startup_fence(), 'held')
        w.env.t = cc.fence.read_fence(w.ctl.custody)['deadline'] + 1
        (w.ctl.custody / cc.fence.FENCE_NAME).unlink()  # synthetic stale cleanup, no watchdog invocation
        w.controller()
        self.assertEqual(w.tick()['state'], 'HALTED')
        self.assertIn('ARM_INDETERMINATE', self.pages(w))
        self.assertEqual(w.launcher.launched, [])
        w.controller()
        self.assertEqual(w.ctl.startup_fence(), 'paged')
        self.assertTrue(w.tick()['detail']['silent'])
        w.ack_all()
        self.assertEqual(w.tick()['state'], 'LIVE')

    def test_pid_changing_restart_preserves_an_expired_lease(self):
        w = self.pilot_world(prior=False)
        self.assertEqual(w.ctl.startup_fence(), 'held')
        old = cc.fence.read_fence(w.ctl.custody)
        w.env.t = old['deadline'] + 1
        w.controller()
        w.ctl.pid = old['pid'] + 1000000
        w.env.pid_alive = lambda pid: pid != old['pid']
        self.assertEqual(w.ctl.startup_fence(), 'lapsed')
        self.assertEqual(cc.fence.read_fence(w.ctl.custody), old)
        self.assertEqual(w.tick()['state'], 'HALTED')
        self.assertIn('ARM_INDETERMINATE', self.pages(w))
        self.assertEqual(w.launcher.launched, [])

    def test_unexpected_removal_before_deadline_also_halts(self):
        w = self.pilot_world(prior=False)
        w.ctl.startup_fence()
        (w.ctl.custody / cc.fence.FENCE_NAME).unlink()
        self.assertEqual(w.tick()['state'], 'HALTED')
        self.assertEqual(w.launcher.launched, [])

    def test_failed_night_observation_retains_the_owned_fence(self):
        w = self.pilot_world(prior=False)
        self.assertEqual(w.ctl.startup_fence(), 'held')
        w.env.launchctl_rc = 5
        self.assertEqual(w.tick()['detail']['codes'], ['NIGHT_UNKNOWN'])
        self.assertIsNotNone(cc.fence.read_fence(w.ctl.custody))
        w.env.launchctl_rc = 0
        self.assertEqual(w.tick()['state'], 'LIVE')

    def test_unknown_observation_after_a_known_handoff_stays_released(self):
        w = self.pilot_world(prior=False)
        w.ctl.startup_fence()
        w.env.night_labels = ['com.joulewise.night.synthetic']
        self.assertEqual(w.tick()['detail']['codes'], ['NIGHT_AGENT'])
        self.assertIsNone(cc.fence.read_fence(w.ctl.custody))
        w.env.launchctl_rc = 5
        w.controller()
        self.assertEqual(w.tick()['detail']['codes'], ['NIGHT_UNKNOWN'])
        self.assertIsNone(cc.fence.read_fence(w.ctl.custody))

    def test_unsafe_kit_paths_never_write_outside_staging(self):
        from unittest import mock
        for kind in ('absolute', 'traversal'):
            with self.subTest(kind=kind):
                w = synth.World(Path(self.tmp.name) / kind, prior=False)
                w.controller()
                sentinel = Path(self.tmp.name) / (kind + '-sentinel.json')
                sentinel.write_text('immutable synthetic sentinel')
                span = w.span(1, 'dev-05-s01', 'cl-dev-05', L[:6])
                span['kit']['path'] = str(sentinel) if kind == 'absolute' else '../' + sentinel.name
                w.queue('pilot', [span], role='smoke')
                original = tempfile.TemporaryDirectory
                with mock.patch.object(cc.tempfile, 'TemporaryDirectory', lambda: original(dir=self.tmp.name)):
                    snap, _ = w.ctl.snapshot(w.env.now(), [])
                self.assertEqual(sentinel.read_text(), 'immutable synthetic sentinel')
                self.assertIn('QUEUE_INVALID', [r['code'] for r in law.select(snap).reasons])


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class Gate5Controller(WorldCase):
    def keyless_world(self):
        w = self.pilot_world(prior_evidence=False)
        prior = w.standing['prior_spans'][-1]
        prior.update(t0='2026-11-16T07:00:00-08:00', closed='2026-11-16T10:00:00-08:00')
        w.commit({f'{synth.RD}/STANDING.json': w.standing}, 'early prior close', w.env.now() - 100)
        source = Path(w.cfg['output_root']) / prior['campaign_id'] / (prior['plan_id'] + '-20261116T150000Z')
        source.mkdir(parents=True)
        receipt = source / cc.RECEIPT
        receipt.write_text(json.dumps({'roster': prior['roster'], 'kit': {'sha256': prior['kit_sha256'],
                                                                      'campaign_id': prior['campaign_id']},
                                      'rc': 0, 'span_result': {'chain_exit_code': 0, 'chain_outcome': 'COMPLETE',
                                                             'fault': False, 'outcome': 'MEASURED_OK'},
                                      'steps': [{'name': 'soak', 'rc': 0}, {'name': 'restore', 'rc': 0}],
                                      'feeds': {'meter': {'stop': {'proven_stopped': True}}},
                                      'legs_planned': len(prior['roster']),
                                      'legs': [{'leg_id': x, 'summary': {'g0_outcome': 'released'}}
                                               for x in prior['roster']], 'legs_finished': len(prior['roster'])}))
        closed = law.parse_time(prior['closed'])
        os.utime(receipt, (closed, closed))
        marker = synth.offload_marker(prior['plan_id'], law.KEY_SECOND_COPY_DEADLINE - 3600, str(source))
        marker['key_second_copy'] = None
        path = Path(w.cfg['copy_marker_dir']) / (prior['plan_id'] + '.ok')
        path.write_text(json.dumps(marker))
        return w

    def test_an_early_keyless_copy_blocks_admission_after_the_deadline(self):
        w = self.keyless_world()
        self.assertEqual(w.tick()['state'], 'PAGED')
        self.assertIn('OFFLOAD_FAILED', self.pages(w))
        self.assertEqual(w.launcher.launched, [])

    def test_a_key_deadline_crossed_after_the_final_authority_read_blocks_launch(self):
        from unittest import mock
        w = self.keyless_world()
        original = w.ctl.notice

        def slow_notice(issue, text):
            w.env.t += 20
            return original(issue, text)

        w.ctl.notice = slow_notice
        with mock.patch.object(law, 'KEY_SECOND_COPY_DEADLINE', w.env.now() + 10):
            status = w.tick()
        self.assertEqual(status['state'], 'WAIT')
        self.assertIn('LEASE_EXPIRED', status['detail']['codes'])
        self.assertEqual(w.launcher.launched, [])
        self.assertFalse((w.ctl.span_dir('cq-dev-05-s01-a1') / 'intent.json').exists())

    def test_a_tick_cannot_renew_away_an_expired_fence(self):
        w = self.pilot_world(prior=False)
        w.ctl.startup_fence()
        w.env.t = cc.fence.read_fence(w.ctl.custody)['deadline'] + 1
        self.assertEqual(w.ctl.startup_fence(), 'lapsed')
        self.assertEqual(w.tick()['state'], 'HALTED')
        self.assertIn('ARM_INDETERMINATE', self.pages(w))
        self.assertEqual(w.launcher.launched, [])
        w.controller()  # the unacknowledged lapse survives a controller restart
        self.assertEqual(w.ctl.startup_fence(), 'paged')
        self.assertTrue(w.tick()['detail']['silent'])
        self.assertEqual(w.launcher.launched, [])

    def test_an_unreadable_local_history_is_never_asserted_empty_at_close(self):
        w = self.world(prior=False)
        pid = 'cq-dev-05-s01-a1'
        directory = w.ctl.span_dir(pid)
        cc.atomic_json(directory / 'intent.json', {'kit': {'path': '/synthetic/kit.json'}})
        cc.atomic_json(directory / 'close.json', {'pushed': True, 'bundle_commit': 'a' * 40})
        w.ctl.git.local_refs = lambda _prefix: None
        w.ctl.host_run = lambda *_a, **_kw: self.fail('desk launched with unreadable history')
        w.ctl.desk_close(pid)
        close = cc.read_json(directory / 'close.json')
        self.assertIn('history refs could not be listed', close['mbp_desk']['problem'])
        self.assertIsNone(close['mbp_desk']['published'])

    def test_a_guard_lapse_during_the_authority_read_halts_before_network(self):
        w = self.pilot_world(prior=False)
        original = w.ctl.git.fetch_audit

        def delayed_fetch():
            w.env.t = cc.fence.read_fence(w.ctl.custody)['deadline'] + 1
            return original()

        w.ctl.git.fetch_audit = delayed_fetch
        self.assertEqual(w.tick()['state'], 'HALTED')
        self.assertIn('ARM_INDETERMINATE', self.pages(w))
        self.assertEqual(w.ctl.network_log, [])
        self.assertEqual(w.launcher.launched, [])

    def test_an_informational_stall_keeps_the_fence_until_and_after_restart(self):
        w = self.world(prior=False)
        w.queue('pilot', [dict(w.span(1, 'dev-05-s01', 'cl-dev-05', L[:6]), not_before='2026-11-18')], role='smoke')
        for _ in range(int(law.stall_bound(['NOT_BEFORE']) / 60) + 3):
            status = w.tick()
            self.assertEqual(status['detail']['codes'], ['NOT_BEFORE'])
            cur = cc.fence.read_fence(w.ctl.custody)
            self.assertIsNotNone(cur)
            self.assertGreater(cur['deadline'], w.env.now())
            w.env.t += 60
        self.assertIn('WAIT_STALL', self.pages(w))
        self.assertEqual(w.launcher.launched, [])
        w.controller()
        self.assertEqual(w.ctl.startup_fence(), 'held')
        w.tick()
        self.assertIsNotNone(cc.fence.read_fence(w.ctl.custody))

    def test_failed_authority_listings_hold_both_reads(self):
        for target in ('sessions', 'q1', 'local_refs'):
            for fail_on in (1, 2):
                with self.subTest(target=target, fail_on=fail_on):
                    w = synth.World(Path(self.tmp.name) / f'{target}-{fail_on}', prior=False)
                    w.controller()
                    w.queue('pilot', [w.span(1, 'dev-05-s01', 'cl-dev-05', L[:6])], role='smoke')
                    original = w.ctl.git.git
                    reads = []

                    def git(*args, **kw):
                        matched = ((target != 'local_refs' and args[0] == 'ls-tree'
                                    and args[-1] == f'{synth.RD}/{target}/')
                                   or (target == 'local_refs' and args[0] == 'for-each-ref'
                                       and args[-1] == cc.MBP_VERDICT_PREFIX))
                        if matched:
                            reads.append(args)
                            if len(reads) == fail_on:
                                return cc.Result(128, '', 'synthetic authority listing failure')
                        return original(*args, **kw)

                    w.ctl.git.git = git
                    status = w.tick()
                    self.assertEqual(status['state'], 'WAIT')
                    self.assertEqual(len(reads), fail_on)
                    self.assertIn('FETCH_FAILED', status['detail']['codes'])
                    self.assertEqual(w.launcher.launched, [])

    def test_an_unreadable_ready_directory_cannot_cede_or_arm(self):
        w = self.pilot_world(prior=False)
        w.commit({f'{synth.RD}/sessions/READY-r1-slot-1.json': {
            'schema': law.SESSION_READY_SCHEMA, 'session_id': 'r1-slot-1', 'by': 'lead',
            'ready_at': cc.iso(w.env.now() - 30)}}, 'ready session', w.env.now() - 20)
        snap, _ = w.ctl.snapshot(w.env.now(), [])
        self.assertEqual(law.select(snap).action, 'cede')
        original = w.ctl.git.git
        w.ctl.git.git = lambda *a, **kw: cc.Result(128, '', 'synthetic listing failure') if (
            a[0] == 'ls-tree' and a[-1] == f'{synth.RD}/sessions/') else original(*a, **kw)
        status = w.tick()
        self.assertEqual(status['state'], 'WAIT')
        self.assertIn('FETCH_FAILED', status['detail']['codes'])
        self.assertNotIn('V4_SESSION_READY', self.pages(w))
        self.assertEqual(w.launcher.launched, [])


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class EndToEnd(WorldCase):
    """RL-172 (i) row 5: the controller, the pinned runner, the signed bundle, the real Air desk, the signed verdict."""

    def test_clean_span(self):
        synth.scenario_clean(Path(self.tmp.name) / "clean", log=quiet)

    def test_retried_soak_span(self):
        _w, v = synth.scenario_soak_retry(Path(self.tmp.name) / "soak", log=quiet)
        self.assertTrue(any("retried soak" in t for t in v["hand_table"]["triggers"]), v["hand_table"])

    def test_g0_timeout_l005_span(self):
        _w, v = synth.scenario_l005_timeout(Path(self.tmp.name) / "l005", log=quiet)
        self.assertIn("L005 consumer gate", {h.get("gate") for h in v["holds"]})

    def test_redo_span(self):
        synth.scenario_redo(Path(self.tmp.name) / "redo", log=quiet)

    def test_tampered_bundle_and_verdict(self):
        synth.scenario_tampered(Path(self.tmp.name) / "tampered", log=quiet)


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class BundleProtocol(WorldCase):
    def test_the_pushed_commit_is_exactly_the_format_tree(self):          # Sol 1, Mythos F1
        w = self.pilot_world()
        w.tick()
        w.launcher.finish()
        self.assertEqual(w.tick()["state"], "CLOSED")
        close = json.loads(self.state(w, "spans/cq-dev-05-s01-a1/close.json").read_text())
        ref = "refs/remotes/origin/desk-bundles/cq-dev-05-s01-a1"
        synth.git(w.seed, "fetch", "-q", "origin", "+refs/heads/desk-bundles/*:refs/remotes/origin/desk-bundles/*")
        tree = sorted(synth.git(w.seed, "ls-tree", "-r", "--name-only", ref).decode().split())
        self.assertEqual(tree, sorted(["transition.json", "bundle/BUNDLE_MANIFEST.json", "bundle/runner_receipt.json",
                                       "bundle/span_plan.json", "bundle/span/result.json", "bundle/span/meter.json",
                                       *[f"bundle/legs/{x}/leg_summary.json" for x in L[:6]]]))
        transition = json.loads(synth.git(w.seed, "show", f"{ref}:transition.json"))
        self.assertEqual(desk_transport.validate_transition(transition), [])
        self.assertEqual(transition["manifest_sha256"], close["manifest_sha256"])
        subject = synth.git(w.seed, "log", "-1", "--format=%s", ref).decode().strip()
        self.assertEqual(subject, "cadence close bundle cq-dev-05-s01-a1")
        self.assertTrue(desk_transport.verify_signed_commit(str(w.seed), ref, allowed_signers=w.keys["ctl"]["allowed"],
                                                            principal="cadence-controller"))

    def test_an_unexpected_file_is_never_read_or_shipped(self):          # Sol 2
        w = self.pilot_world()
        w.tick()
        live = w.launcher.finish()
        (live["output"] / "desk-bundle" / "meter-samples.txt").write_text("SYNTHETIC-CANARY\n")
        self.assertEqual(w.tick()["state"], "HALTED")
        close = json.loads(self.state(w, "spans/cq-dev-05-s01-a1/close.json").read_text())
        self.assertIn("BUNDLE_REFUSED", {r["code"] for r in close["reasons"]})
        remote = synth.git(w.seed, "ls-remote", "origin", "refs/heads/desk-bundles/*").decode()
        self.assertEqual(remote.strip(), "")
        self.assertFalse(self.state(w, "spans/cq-dev-05-s01-a1/publish").exists())


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class LiveInterlock(WorldCase):
    def test_a_held_fence_past_its_deadline_alarms_and_never_closes(self):   # Sol 3
        w = self.pilot_world()
        self.assertEqual(w.tick()["state"], "LIVE")
        (w.launcher.live["output"] / cc.RECEIPT).unlink()       # an unfinished runner
        w.ctl.git.fetch_audit = lambda: self.fail("network while the span holds the host")
        w.env.t += 14 * 3600
        self.assertEqual(w.tick()["state"], "LIVE")
        self.assertFalse(self.state(w, "spans/cq-dev-05-s01-a1/close.json").exists())
        self.assertIn("STRANDED_ALARM", self.pages(w))
        with self.assertRaises(cc.NetworkClosed):
            w.ctl.guard("anything")

    def test_no_transport_retry_while_another_run_holds_the_host(self):   # Sol 3
        w = self.pilot_world()
        w.tick()
        w.launcher.finish()
        w.ctl.git.push_commit = lambda sha, ref: (None, "synthetic outage")
        w.tick()
        self.assertFalse(json.loads(self.state(w, "spans/cq-dev-05-s01-a1/close.json").read_text())["pushed"])
        cc.fence.write_fence(Path(w.cfg["custody_root"]), {"purpose": "align-r0:f0", "pid": os.getpid(),
                                                            "deadline": w.env.now() + 9000})
        w.ctl.git.push_commit = lambda sha, ref: self.fail("pushed while a foreign fence was live")
        self.assertEqual(w.tick()["detail"]["codes"], ["SPAN_LIVE"])

    def test_the_standing_fence_is_taken_when_the_launch_fence_goes(self):   # Mythos F14, Sol 15
        w = self.pilot_world()
        w.tick()
        seen = []
        w.ctl.close = lambda rec, stranded=None: seen.append(cc.fence.read_fence(Path(w.cfg["custody_root"]))) or {}
        w.launcher.finish()
        w.tick()
        self.assertTrue(seen and seen[0]["purpose"].startswith(cc.STANDING_FENCE_PREFIX), seen)

    def test_a_foreign_close_is_unproven_until_noted(self):                 # Sol 10
        w = self.pilot_world()
        custody = Path(w.cfg["custody_root"])
        cc.fence.write_fence(custody, {"purpose": "align-r0:f0", "pid": os.getpid(), "deadline": w.env.now() + 9000})
        self.assertEqual(w.tick()["detail"]["codes"], ["SPAN_LIVE"])
        cc.fence.clear_owned(custody, "align-r0:f0")
        w.env.t += 1300
        self.assertIn(w.tick()["state"], ("PAGED", "HALTED"))
        self.assertIn("FOREIGN_CLOSE_UNPROVEN", self.pages(w))
        with contextlib.redirect_stdout(io.StringIO()):
            cc.cmd_note_run(w.cfg, type("A", (), {"run_id": "align-r0:f0", "kind": "F0", "t0": w.env.now() - 9000,
                                                  "closed": w.env.now() - 1300, "restore_ok": "yes",
                                                  "evidence": "RUN_STATE 999 Check: every restore line OK"}))
        w.ack_all()
        self.assertIn("GAP", w.tick()["detail"]["codes"])   # the floor counts from the observed close, never earlier
        w.advance_wait(law.GAP_AFTER_OTHER_S)
        self.assertEqual(w.tick()["state"], "LIVE")

    def test_an_expired_foreign_fence_with_a_live_pid_still_holds_the_host(self):   # Sol R2
        w = self.pilot_world()
        w.tick()
        w.launcher.finish()
        w.ctl.git.push_commit = lambda sha, ref: (None, "synthetic outage")
        w.tick()
        cc.fence.write_fence(Path(w.cfg["custody_root"]), {"purpose": "align-r0:f0", "pid": os.getpid(),
                                                            "deadline": w.env.now() - 1})
        w.ctl.git.push_commit = lambda sha, ref: self.fail("pushed while a live foreign PID held the host")
        w.ctl.git.fetch_audit = lambda: self.fail("fetched while a live foreign PID held the host")
        self.assertEqual(w.tick()["detail"]["codes"], ["SPAN_LIVE"])

    def test_our_fence_gone_and_another_run_up_is_no_close(self):     # Mythos N9
        w = self.pilot_world()
        w.tick()
        live = w.launcher.finish()
        cc.fence.write_fence(Path(w.cfg["custody_root"]), {"purpose": "align-r0:other", "pid": os.getpid(),
                                                            "deadline": w.env.now() + 9000})
        s = w.tick()
        self.assertEqual(s["state"], "CLOSING")
        self.assertFalse(self.state(w, "spans/cq-dev-05-s01-a1/close.json").exists())
        cc.fence.clear_owned(Path(w.cfg["custody_root"]), "align-r0:other")
        self.assertEqual(w.tick()["state"], "CLOSED")
        self.assertIn("align-r0:other", self.state(w, "external.jsonl").read_text())
        del live


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class SecondGate(WorldCase):
    """The second gate's controller-side findings, each run through the real synthetic chain."""

    def test_denied_key_scenario(self):                                  # Mythos N1, Sol R1
        synth.scenario_denied_key(Path(self.tmp.name) / "denied", log=quiet)

    def test_a_denied_key_in_the_transition_record_is_refused_at_signing(self):   # Mythos N1 (desk scan at sign)
        w = self.pilot_world()
        w.tick()
        w.launcher.finish()
        push = w.ctl.git.push_commit
        w.ctl.git.push_commit = lambda sha, ref: (None, "synthetic outage")
        w.tick()
        path = self.state(w, "spans/cq-dev-05-s01-a1/close.json")
        close = json.loads(path.read_text())
        self.assertFalse(close["pushed"])
        close["transition"]["power_w"] = "SYNTHETIC_DENIED_KEY_CANARY"   # signed with transition.json: refused
        path.write_text(json.dumps(close))
        w.ctl.git.push_commit = push
        s = w.tick()     # the retry signs: refused, the span is STOPPED, and the halt pages
        self.assertEqual((s["state"], s["detail"]["codes"]), ("PAGED", ["SPAN_BAD_TERMINAL"]))
        close = json.loads(path.read_text())
        self.assertEqual((close["status"], close["pushed"]), ("STOPPED", None))
        self.assertIn("BUNDLE_REFUSED", {r["code"] for r in close["reasons"]})
        self.assertEqual(synth.git(w.seed, "ls-remote", "origin", "refs/heads/desk-bundles/*").decode().strip(), "")
        self.assertFalse(self.state(w, "spans/cq-dev-05-s01-a1/publish").exists())
        self.assertIn("bundle_refused", self.state(w, "transitions.jsonl").read_text())

    def test_prior_gate_scenario(self):                                  # Mythos N2
        synth.scenario_prior_gate(Path(self.tmp.name) / "prior", log=quiet)

    def test_recovery_scenario(self):                                    # Mythos N3, Sol R9
        synth.scenario_recovery(Path(self.tmp.name) / "recovery", log=quiet)

    def test_repage_scenario(self):                                      # Mythos N4
        synth.scenario_repage(Path(self.tmp.name) / "repage", log=quiet)

    def test_night_window_scenario(self):                                # Mythos N5, N15, Sol R2
        synth.scenario_night_window(Path(self.tmp.name) / "night", log=quiet)

    def test_a_symlinked_desk_bundle_root_is_refused_unread(self):       # Sol R1
        w = self.pilot_world()
        w.tick()
        live = w.launcher.finish()
        real = live["output"] / "desk-bundle"
        moved = live["output"].parent / "elsewhere"
        real.rename(moved)
        os.symlink(moved, real)
        self.assertEqual(w.tick()["state"], "HALTED")
        close = json.loads(self.state(w, "spans/cq-dev-05-s01-a1/close.json").read_text())
        self.assertIn("BUNDLE_REFUSED", {r["code"] for r in close["reasons"]})
        self.assertEqual(synth.git(w.seed, "ls-remote", "origin", "refs/heads/desk-bundles/*").decode().strip(), "")

    def test_a_rolled_back_verdict_ref_halts(self):                      # Mythos N10
        w = self.pilot_world()
        w.tick()
        w.launcher.finish()
        w.tick()
        w.air_final("cq-dev-05-s01-a1")
        first = synth.git(w.seed, "rev-parse", "refs/remotes/origin/cadence-desk-final/cq-dev-05-s01-a1").decode().strip()
        w.air_final("cq-dev-05-s01-a1", hand_table=True)
        w.copy_journals("cq-dev-05-s01-a1")
        w.env.t += 400
        w.tick()                                          # reads and remembers the later tip
        synth.git(w.seed, "push", "-q", "-f", "origin", f"{first}:refs/heads/cadence-desk-final/cq-dev-05-s01-a1")
        w.ack_all()
        w.env.t += 60
        w.tick()
        self.assertIn("rolled back", self.pages(w))

    def test_no_verdict_signers_file_halts_before_any_launch(self):      # Mythos N14
        w = self.pilot_world()
        os.unlink(w.cfg["verdict_signers"])
        self.assertEqual(w.tick()["state"], "HALTED")
        self.assertIn("SIGNING_UNAVAILABLE", self.pages(w))
        self.assertEqual(w.launcher.launched, [])

    def test_the_first_arm_launches_over_the_standing_fence(self):       # Sol R7
        w = self.pilot_world()
        self.assertEqual(w.tick()["state"], "LIVE")
        self.assertTrue(w.launcher.fences_at_launch[0]["purpose"].startswith(cc.STANDING_FENCE_PREFIX))

    def test_slow_clock_and_notice_calls_spend_the_lease(self):          # Sol R3, Mythos N7
        w = self.pilot_world()

        def slow_clock():
            w.env.t += 100
            return w.env.now()
        notice = w.ctl.notice

        def slow_notice(issue, text):
            w.env.t += 30
            return notice(issue, text)
        w.ctl.clock, w.ctl.notice = slow_clock, slow_notice
        s = w.tick()
        self.assertEqual(s["detail"]["codes"], ["LEASE_EXPIRED"])
        self.assertEqual(w.launcher.launched, [])


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class FreshAuthority(WorldCase):
    def hook_prep(self, w, action):
        check = w.ctl.preparer.check

        def wrapped(*a, **k):
            action()
            return check(*a, **k)
        w.ctl.preparer.check = wrapped

    def test_a_veto_issued_during_preparation_stops_the_arm(self):        # Sol 4
        w = self.pilot_world()
        self.hook_prep(w, lambda: w.issues.append({"number": 9, "title": "STOP", "labels": [{"name": "directive"}],
                                                   "author": {"login": "mpmdw"}, "state": "OPEN"}))
        self.assertNotEqual(w.tick()["state"], "LIVE")
        self.assertEqual(w.launcher.launched, [])
        self.assertIn("VETO_OPEN", self.pages(w))

    def test_a_session_ready_during_preparation_cedes(self):              # Sol 4
        w = self.pilot_world()
        self.hook_prep(w, lambda: w.commit({f"{synth.RD}/sessions/READY-r1-slot-1.json": {
            "schema": law.SESSION_READY_SCHEMA, "session_id": "r1-slot-1", "by": "lead",
            "ready_at": "2026-11-17T07:59:00-08:00"}}, "ready", w.env.now() - 5))
        w.tick()
        self.assertEqual(w.launcher.launched, [])
        self.assertIn("V4_SESSION_READY", self.pages(w))

    def test_a_watcher_stamp_gone_stale_during_preparation_halts(self):   # Sol 4
        w = self.pilot_world()
        stale = {"schema": law.WATCHER_STAMP_SCHEMA, "watcher": synth.WATCHER, "by": "lead",
                 "observed_live_at": "2026-11-16T07:00:00-08:00"}
        self.hook_prep(w, lambda: w.commit({f"{synth.RD}/watcher-stamp.json": stale}, "stale stamp", w.env.now() - 5))
        w.tick()
        self.assertEqual(w.launcher.launched, [])
        self.assertIn("WATCHER_STALE", self.pages(w))

    def test_the_lease_binds_the_date_and_the_actual_t0_is_recorded(self):   # Sol 4, Mythos F10, F19
        w = self.pilot_world()
        w.tick()
        intent = json.loads(self.state(w, "spans/cq-dev-05-s01-a1/intent.json").read_text())
        self.assertLessEqual(intent["lease_until"], law.date_end("2026-11-17") - law.MIDNIGHT_MARGIN_S)
        self.assertLessEqual(intent["lease_until"], intent["decided_epoch"] + cc.LEASE_S)
        w.launcher.finish()
        w.tick()
        close = json.loads(self.state(w, "spans/cq-dev-05-s01-a1/close.json").read_text())
        arm = json.loads(self.state(w, "spans/cq-dev-05-s01-a1/arm.json").read_text())
        receipt = json.loads((Path(arm["output"]) / cc.RECEIPT).read_text())
        self.assertEqual(close["transition"]["t0_epoch"], receipt["started"]["epoch_s"])   # the runner's own t0

    def test_an_expired_lease_is_refused_by_the_arm_child(self):          # Sol 4
        w = self.pilot_world()
        launch = w.launcher.launch
        w.launcher.launch = lambda req: launch({**req, "lease_until": w.env.now() - 1})
        self.assertEqual(w.tick()["state"], "HALTED")
        self.assertIn("LAUNCH_REFUSED", self.pages(w))
        self.assertEqual(w.launcher.launched, [])

    def test_a_host_clock_off_the_servers_halts(self):                    # Mythos F23
        w = self.pilot_world()
        w.ctl.clock = lambda: w.env.now() + 600
        w.tick()
        self.assertIn("CLOCK_SKEW", self.pages(w))
        self.assertEqual(w.launcher.launched, [])

    def test_the_standing_notice_line_posts_before_the_launch(self):      # Mythos F16
        w = self.pilot_world()
        self.assertEqual(w.tick()["state"], "LIVE")
        self.assertEqual([n[0] for n in w.notices], [900])
        self.assertIn("cq-dev-05-s01-a1", w.notices[0][1])

    def test_no_notice_line_no_arm(self):                                  # Mythos F16
        w = self.pilot_world()
        w.ctl.notice = lambda issue, text: False
        self.assertEqual(w.tick()["state"], "WAIT")
        self.assertEqual(w.launcher.launched, [])


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class QueueAuthority(WorldCase):
    def test_a_force_pushed_rewrite_of_the_audit_branch_halts(self):      # Mythos F4
        w = self.world()
        w.queue("dev05", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6], nb="2026-11-18")], role="smoke")
        self.assertIn("NOT_BEFORE", w.tick()["detail"]["codes"])   # read and remembered
        path = w.seed / synth.RD / "queues/QUEUE-dev05.json"
        doc = json.loads(path.read_text())
        doc["spans"][0]["legs"], doc["spans"][0]["not_before"] = L[6:12], "2026-11-17"
        path.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
        synth.git(w.seed, "commit", "-q", "-a", "--amend", "-m", "rewrite", epoch=w.env.now() - 5)
        synth.git(w.seed, "push", "-q", "-f", "origin", f"HEAD:refs/heads/{synth.AUDIT}")
        w.env.t += 600
        w.tick()
        self.assertIn("AUDIT_REWRITTEN", self.pages(w))
        self.assertEqual(w.launcher.launched, [])

    def test_a_missing_listed_queue_halts_while_another_could_arm(self):  # Sol 5
        w = self.world()
        w.standing["queues"].append({"path": f"{synth.RD}/queues/QUEUE-gone.json", "role": "standing"})
        w.queue("dev05", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6])], role="smoke")
        w.tick()
        self.assertIn("QUEUE_MISSING", self.pages(w))
        self.assertEqual(w.launcher.launched, [])

    def test_a_ready_session_silences_the_network_until_acknowledged(self):   # Mythos F5
        w = self.pilot_world()
        w.commit({f"{synth.RD}/sessions/READY-r1-slot-1.json": {
            "schema": law.SESSION_READY_SCHEMA, "session_id": "r1-slot-1", "by": "lead",
            "ready_at": "2026-11-17T07:00:00-08:00"}}, "ready", w.env.now() - 5)
        self.assertEqual(w.tick()["state"], "PAGED")
        w.ctl.git.fetch_audit = lambda: self.fail("network while ceded")
        for _ in range(3):
            w.env.t += 60
            self.assertTrue(w.tick()["detail"].get("silent"))
        self.assertIsNone(cc.fence.read_fence(Path(w.cfg["custody_root"])))


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class BoundsAndLedger(WorldCase):
    def test_an_arm_internal_wait_pages_after_its_bound(self):            # Mythos F7
        w = self.pilot_world()

        def agent(kind, allowed=()):
            p = synth.clean_proof(kind)
            if kind == "arm":
                p["lines"]["agents"] = {"ok": False, "detail": "4242 claude"}
            return p
        w.ctl.proof = agent
        self.assertEqual(w.tick()["detail"]["codes"], ["AGENT_PRESENT"])
        w.advance_wait(law.STALL_SHORT_S + 60)
        self.assertEqual(w.tick()["state"], "PAGED")
        self.assertIn("WAIT_STALL", self.pages(w))

    def test_the_ledger_records_failed_prerequisites_and_refusals(self):  # Sol 14
        w = self.pilot_world()

        def bad(kind, allowed=()):
            p = synth.clean_proof(kind)
            p["lines"]["powermode"] = {"ok": False, "detail": "powermode 2"}
            return p
        w.ctl.proof = bad
        self.assertEqual(w.tick()["state"], "HALTED")
        doc = json.loads(self.state(w, "critical-path/dev-05-s01.json").read_text())
        self.assertIsNone(doc["ready_all"])
        self.assertIsNone(doc["prereqs"]["HOST_PROOF_FAILED"]["ready_at"])
        self.assertIsNotNone(doc["prereqs"]["PREPARE"]["ready_at"])
        self.assertIn("HOST_PROOF_FAILED", doc["refusal"] or "")

    def test_no_signing_key_halts_before_any_launch(self):                 # Mythos F11
        w = self.pilot_world()
        os.unlink(w.cfg["signing_key"])
        self.assertEqual(w.tick()["state"], "HALTED")
        self.assertIn("SIGNING_UNAVAILABLE", self.pages(w))
        self.assertEqual(w.launcher.launched, [])

    def test_a_journal_copy_marker_is_needed_after_a_campaign_close(self):   # Sol 11
        w = self.pilot_world()
        w.tick()
        w.launcher.finish()
        w.tick()
        w.queue("rest", [w.span(1, "dev-05-s02", "cl-dev-05", L[6:])])
        w.lead_release("cq-dev-05-s01-a1", "class-a")
        w.env.t += 400
        self.assertIn("JOURNAL_COPY", w.tick()["detail"]["codes"])
        w.copy_journals("cq-dev-05-s01-a1")
        self.assertEqual(w.drive(lambda s: s["state"] == "LIVE")["detail"]["plan_id"], "cq-dev-05-s02-a1")


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class Restart(WorldCase):
    def test_restart_adopts_a_launched_span_and_never_relaunches(self):
        w = self.pilot_world()
        self.assertEqual(w.tick()["state"], "LIVE")
        self.state(w, "spans/cq-dev-05-s01-a1/arm.json").unlink()   # crash before the record
        calls = []
        launch = w.launcher.launch
        w.launcher.launch = lambda req: calls.append(req) or launch(req)
        w.controller()
        self.assertEqual(w.tick()["state"], "LIVE")
        w.launcher.finish()
        self.assertEqual(w.tick()["state"], "CLOSED")
        self.assertEqual(calls, [])

    def test_a_launch_fence_without_output_is_waited_for_not_adopted(self):   # Mythos F21
        w = self.pilot_world()
        w.tick()
        live = w.launcher.live
        self.state(w, "spans/cq-dev-05-s01-a1/arm.json").unlink()
        moved = live["output"].with_name(live["output"].name + ".hidden")
        live["output"].rename(moved)
        w.controller()
        self.assertEqual(w.tick()["state"], "WAIT")
        self.assertFalse(self.state(w, "spans/cq-dev-05-s01-a1/arm.json").exists())
        moved.rename(live["output"])
        self.assertEqual(w.tick()["state"], "LIVE")

    def test_restart_with_no_trace_of_a_launch_halts(self):
        w = self.pilot_world()
        w.launcher.launch = lambda req: (_ for _ in ()).throw(SystemExit("crash inside the launch"))
        with self.assertRaises(SystemExit):
            w.tick()
        calls = []
        w.launcher.launch = lambda req: calls.append(req)
        w.controller()
        self.assertEqual(w.tick()["state"], "HALTED")
        self.assertEqual(calls, [])
        self.assertIn("ARM_INDETERMINATE", self.pages(w))


class ArmChild(unittest.TestCase):
    """The arm child: the atomic fence transfer, the lease, the pin's own deadline, and a foreign fence refused."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        (self.tmp / "repo/scripts").mkdir(parents=True)
        shutil.copy(ROOT / "scripts/launch_align_r0.py", self.tmp / "repo/scripts/launch_align_r0.py")
        (self.tmp / "repo/scripts/cadence_legs_runner.py").write_text(
            "def launch_deadline(plan):\n    return plan['t0'] + 1000.0\n")
        (self.tmp / "repo/scripts/launch_cadence_span.py").write_text(
            "import json, os, subprocess, sys, time\nfrom pathlib import Path\nfrom scripts import launch_align_r0 as base\n"
            "def cadence_plan(kit, legs=None, batch_window=None, t0=None):\n    return {'t0': 5000.0}\n"
            "def main(argv):\n"
            "    root = Path(argv[argv.index('--custody-root') + 1]); pid = int(argv[argv.index('--magistrate-pid') + 1])\n"
            "    path = root / base.FENCE_NAME\n"
            "    race = (root / 'race').read_text() if (root / 'race').exists() else None\n"
            "    with base.fence_lock(root):\n"
            "        if race == 'remove before read': path.unlink()\n"
            "        cur = base.read_fence(root)\n"
            "        if cur and base.pid_alive(cur['pid']):\n"
            "            print('active fence', file=sys.stderr); return 2\n"
            "        if race == 'replace after read':\n"
            "            change = json.loads(path.read_text()); change['deadline'] -= 1\n"
            "            path.write_text(json.dumps(change))\n"
            "        existed = path.exists()\n"
            "        base.write_fence(root, {'purpose': 'align-r0:t', 'pid': pid, 'deadline': 4e9})\n"
            "    if race == 'remove before bootstrap':\n"
            "        path.unlink()\n"
            "        subprocess.run(['/usr/bin/true', 'bootstrap'], check=True)\n"
            "    (root / 'argv.json').write_text(json.dumps({'argv': argv, 'fence_existed_at_write': existed}))\n"
            "    print(json.dumps({'fence': {'purpose': 'align-r0:t'}, 'next': 'exit the magistrate session now'}))\n"
            "    return 0\n")
        self.custody = self.tmp / "custody"
        self.custody.mkdir()

    def run_child(self, lease=4e9):
        req = {"repo": str(self.tmp / "repo"), "python": sys.executable, "kit": "/k.json", "legs": "L001,L002",
               "batch_window": None, "output": "/o", "custody_root": str(self.custody), "lease_until": lease,
               "standing_purpose": "cadence-controller:abc", "controller_pid": os.getpid()}
        return subprocess.run([sys.executable, "-I", "-B", "-c", cc.ARM_CHILD, json.dumps(req)], capture_output=True,
                              text=True, cwd=self.tmp / "repo")

    def test_the_standing_fence_is_replaced_atomically(self):            # Sol 15
        cc.fence.write_fence(self.custody, {"purpose": "cadence-controller:abc", "pid": os.getpid(), "deadline": 4e9})
        done = self.run_child()
        self.assertEqual(done.returncode, 0, done.stderr)
        rec = json.loads((self.custody / "argv.json").read_text())
        self.assertTrue(rec["fence_existed_at_write"], "the controller's fence stood until the launch fence replaced it")
        argv = rec["argv"]
        child = json.loads(done.stdout.splitlines()[-1])
        self.assertEqual(argv[argv.index("--magistrate-pid") + 1], str(child["arm_child_pid"]))
        self.assertEqual(float(argv[argv.index("--deadline") + 1]), 5000.0 + 1000.0 + 60)   # Mythos F10
        self.assertNotIn("--batch-window", argv)
        self.assertEqual(cc.fence.read_fence(self.custody)["purpose"], "align-r0:t")

    def test_a_foreign_fence_is_refused_untouched(self):
        cc.fence.write_fence(self.custody, {"purpose": "align-r0:other", "pid": os.getpid(), "deadline": 4e9})
        done = self.run_child()
        self.assertEqual(done.returncode, 3)
        self.assertEqual(cc.fence.read_fence(self.custody)["purpose"], "align-r0:other")
        self.assertFalse((self.custody / "argv.json").exists())

    def test_an_expired_lease_launches_nothing(self):                    # Sol 4
        cc.fence.write_fence(self.custody, {"purpose": "cadence-controller:abc", "pid": os.getpid(), "deadline": 4e9})
        done = self.run_child(lease=time.time() - 1)
        self.assertEqual(done.returncode, 4)
        self.assertFalse((self.custody / "argv.json").exists())
        self.assertEqual(cc.fence.read_fence(self.custody)["purpose"], "cadence-controller:abc")

    def test_fence_loss_or_replacement_after_precheck_refuses_launch(self):
        for race in ("remove before read", "replace after read", "remove before bootstrap"):
            with self.subTest(race=race):
                (self.custody / "argv.json").unlink(missing_ok=True)
                (self.custody / "race").write_text(race)
                standing = {"purpose": "cadence-controller:abc", "pid": os.getpid(), "deadline": 4e9}
                cc.fence.write_fence(self.custody, standing)
                done = self.run_child()
                self.assertNotEqual(done.returncode, 0, done.stdout)
                self.assertIn("arm_indeterminate", done.stdout)
                self.assertFalse((self.custody / "argv.json").exists())
                expected = {**standing, "deadline": 4e9 - 1} if race == "replace after read" else None
                self.assertEqual(cc.fence.read_fence(self.custody), expected)

    def test_expired_standing_fence_refuses_launch(self):
        cc.fence.write_fence(self.custody, {"purpose": "cadence-controller:abc", "pid": os.getpid(),
                                           "deadline": time.time() - 1})
        done = self.run_child()
        self.assertNotEqual(done.returncode, 0, done.stdout)
        self.assertFalse((self.custody / "argv.json").exists())


class ArmChildBootstrapLease(unittest.TestCase):
    """Sol R3: the lease is enforced at the launcher's bootstrap call itself, not only before the launcher starts."""

    def test_a_lease_that_expires_inside_the_launcher_refuses_the_bootstrap(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        (tmp / "repo/scripts").mkdir(parents=True)
        shutil.copy(ROOT / "scripts/launch_align_r0.py", tmp / "repo/scripts/launch_align_r0.py")
        (tmp / "repo/scripts/cadence_legs_runner.py").write_text("def launch_deadline(plan):\n    return 9e9\n")
        (tmp / "repo/scripts/launch_cadence_span.py").write_text(
            "import json, subprocess, sys, time\nfrom pathlib import Path\n"
            "from scripts import launch_align_r0 as base\n"
            "def cadence_plan(kit, legs=None, batch_window=None, t0=None):\n    return {}\n"
            "def main(argv):\n"
            "    root = Path(argv[argv.index('--custody-root') + 1])\n"
            "    with base.fence_lock(root):\n"
            "        base.read_fence(root)\n"
            "        base.write_fence(root, {'purpose': 'align-r0:t', 'pid': 123, 'deadline': 9e9})\n"
            "    time.sleep(1.5)       # the launcher's own work, after the arm child's first check\n"
            "    try:\n"
            "        subprocess.run(['/usr/bin/true', 'bootstrap', 'gui/0', 'x.plist'], check=True)\n"
            "    except subprocess.SubprocessError as exc:\n"
            "        print(f'campaign launch refused: {exc}', file=sys.stderr)\n"
            "        return 2\n"
            "    return 0\n")
        (tmp / "custody").mkdir()
        cc.fence.write_fence(tmp / "custody", {"purpose": "cadence-controller:abc", "pid": os.getpid(),
                                              "deadline": 4e9})
        req = {"repo": str(tmp / "repo"), "python": sys.executable, "kit": "/k.json", "legs": "L001",
               "batch_window": None, "output": "/o", "custody_root": str(tmp / "custody"),
               "lease_until": time.time() + 1.0, "standing_purpose": "cadence-controller:abc",
               "controller_pid": os.getpid()}
        done = subprocess.run([sys.executable, "-I", "-B", "-c", cc.ARM_CHILD, json.dumps(req)], capture_output=True,
                              text=True, cwd=tmp / "repo")
        self.assertEqual(done.returncode, 2, done.stderr)
        self.assertIn("lease expired before bootstrap", done.stderr)
        self.assertIsNone(json.loads(done.stdout.splitlines()[-1])["t0"])


PIN_QUAL = "e1b85a59c53bfbeaa3477df46bcbe9dd8fdfc427"
FAKE_LAUNCHCTL = r"""#!/usr/bin/env python3
import json, os, plistlib, subprocess, sys
from pathlib import Path
args = sys.argv[1:]
row = {"verb": args[0]}
if args[0] == "bootstrap":
    spec = plistlib.load(open(args[2], "rb"))
    pa = spec["ProgramArguments"]
    root, purpose, mpid = Path(pa[4]), pa[5], int(pa[6])
    sys.path.insert(0, spec["WorkingDirectory"])
    from scripts import launch_align_r0 as base
    row["fence_at_bootstrap"], row["magistrate_pid"] = base.read_fence(root), mpid
    agent = subprocess.Popen(["/bin/sleep", "5"], start_new_session=True)
    with base.fence_lock(root):
        base.write_fence(root, {"purpose": purpose, "pid": agent.pid, "deadline": float(pa[7])})
with open(os.environ["FAKE_LAUNCHCTL_LOG"], "a") as fh:
    fh.write(json.dumps(row) + "\n")
"""


@unittest.skipUnless(subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{PIN_QUAL}^{{commit}}"],
                                    capture_output=True).returncode == 0, "the qualification pin is not in this clone")
class ArmChildRealPin(unittest.TestCase):
    """Mythos N17: the real arm child against the qualification pin's real frozen launcher (exported from git); a fake
    launchctl bootstraps nothing and claims the fence as the LaunchAgent's wrapper would."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.pin = self.tmp / "pin"
        self.pin.mkdir()
        archive = subprocess.run(["git", "-C", str(ROOT), "archive", PIN_QUAL, "joulewise", "scripts", "configs"],
                                 capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", str(self.pin)], input=archive, check=True)
        self.launchctl = self.tmp / "launchctl"
        self.launchctl.write_text(FAKE_LAUNCHCTL.replace("#!/usr/bin/env python3", f"#!{sys.executable}"))
        self.launchctl.chmod(0o755)
        self.custody = self.tmp / "custody"
        self.custody.mkdir()
        self.log = self.tmp / "launchctl.jsonl"

    def run_child(self, lease, *, standing=True):
        if standing:
            cc.fence.write_fence(self.custody, {"purpose": "cadence-controller:abc", "pid": os.getpid(),
                                               "deadline": 4e9})
        req = {"repo": str(self.pin), "python": sys.executable, "kit": str(ROOT / "docs/process/cadence/kits/cl-qual-01.v1.1.json"),
               "legs": "L001,L002,L003,L004,L005,L006", "batch_window": None, "output": str(self.tmp / "out"),
               "custody_root": str(self.custody), "lease_until": lease, "standing_purpose": "cadence-controller:abc",
               "controller_pid": os.getpid(), "launchctl_bin": str(self.launchctl)}
        return subprocess.run([sys.executable, "-I", "-B", "-c", cc.ARM_CHILD, json.dumps(req)], capture_output=True,
                              text=True, cwd=self.pin, timeout=120,
                              env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "HOME": str(self.tmp),
                                   "FAKE_LAUNCHCTL_LOG": str(self.log)})

    def test_the_real_launcher_receives_the_fence_atomically_and_bootstraps_once(self):
        done = self.run_child(time.time() + 120)
        self.assertEqual(done.returncode, 0, done.stderr[-800:])
        rows = [json.loads(x) for x in self.log.read_text().splitlines()]
        boot = [r for r in rows if r["verb"] == "bootstrap"]
        self.assertEqual(len(boot), 1)
        self.assertEqual(boot[0]["fence_at_bootstrap"]["pid"], boot[0]["magistrate_pid"])   # the launch fence, ours gone
        child = json.loads(done.stdout.splitlines()[-1])
        self.assertTrue(child["transferred"])
        self.assertIsNotNone(child["t0"])

    def test_an_expired_lease_reaches_no_bootstrap(self):
        done = self.run_child(time.time() - 1)
        self.assertEqual(done.returncode, 4)
        self.assertFalse(self.log.exists())
        self.assertEqual(cc.fence.read_fence(self.custody)["purpose"], "cadence-controller:abc")

    def test_the_real_launcher_cannot_bootstrap_without_a_standing_fence(self):
        done = self.run_child(time.time() + 120, standing=False)
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("arm_indeterminate", done.stdout)
        self.assertFalse(self.log.exists())
        self.assertIsNone(cc.fence.read_fence(self.custody))


class FakeRunEnv(cc.Env):
    def __init__(self, table, freq=0):
        self.table, self.freq, self.t = table, freq, 1.8e9

    def now(self):
        return self.t

    def run(self, argv, **_kw):
        key = " ".join(str(a) for a in argv)
        for prefix, result in self.table.items():
            if key.startswith(prefix):
                return result
        return cc.Result(1, "", "")       # pgrep: none

    def kernel_frequency(self):
        return {"raw_word": self.freq}


class HostProofParsing(unittest.TestCase):
    GOOD = {"/usr/bin/pmset -g batt": cc.Result(0, "Now drawing from 'AC Power'\n -InternalBattery-0 100%\n", ""),
            "/usr/bin/pmset -g": cc.Result(0, "System-wide power settings:\nCurrently in use:\n powermode            0\n", ""),
            "/usr/bin/sudo -n /usr/sbin/systemsetup": cc.Result(0, "Network Time: Off\n", ""),
            "/usr/bin/sudo -n -l": cc.Result(0, "/bin/kill\n", ""),
            "/bin/launchctl list": cc.Result(0, "PID\tStatus\tLabel\n-\t0\tcom.apple.x\n", ""),
            "/bin/zsh": cc.Result(0, "verify OK\n", "")}

    def cfg(self, tmp):
        return {"high_power_marker": str(Path(tmp) / "marker"), "custody_root": str(Path(tmp) / "custody"),
                "measurement_mode_script": "/x.zsh"}

    def proof(self, table, kind, freq=0):
        with tempfile.TemporaryDirectory() as tmp:
            p = cc.host_proof(self.cfg(tmp), FakeRunEnv(table, freq), kind)
        p["lines"]["signing"] = p["lines"]["verdict_signers"] = p["lines"]["desk_commit"] = {"ok": True}
        p["lines"]["controller_signers"] = {"ok": True}
        return p

    def test_clean_host(self):
        self.assertEqual(law.proof_reasons(self.proof(dict(self.GOOD), "arm")["lines"], "arm"), [])

    def test_each_bad_readback(self):
        cases = {"/usr/bin/sudo -n /usr/sbin/systemsetup": cc.Result(0, "Network Time: On\n", ""),
                 "/usr/bin/pmset -g batt": cc.Result(0, "Now drawing from 'Battery Power'\n", ""),
                 "/bin/launchctl list": cc.Result(0, "123\t0\tcom.joulewise.night.plan\n", ""),
                 "/usr/bin/pgrep -u root -x powermetrics": cc.Result(0, "4242\n", ""),
                 "/usr/bin/pgrep -fl km003c": cc.Result(2, "", "pgrep: error"),
                 "/bin/zsh": cc.Result(1, "FAIL spotlight agent loaded\nFAIL agent process present\n", "")}
        for key, result in cases.items():
            table = {key: result, **{k: v for k, v in self.GOOD.items() if k != key}}
            self.assertEqual(law.category(law.proof_reasons(self.proof(table, "close")["lines"], "close")), "halt", key)

    def test_frequency_word_and_marker(self):
        self.assertFalse(self.proof(dict(self.GOOD), "close", freq=397)["lines"]["kernel_frequency"]["ok"])
        with tempfile.TemporaryDirectory() as tmp:
            Path(self.cfg(tmp)["high_power_marker"]).write_text("")
            proof = cc.host_proof(self.cfg(tmp), FakeRunEnv(dict(self.GOOD)), "close")
            self.assertFalse(proof["lines"]["high_power_marker"]["ok"])

    def test_an_agent_at_the_arm_is_a_wait(self):
        table = {"/usr/bin/pgrep -x claude": cc.Result(0, "777\n", ""), **self.GOOD}
        self.assertEqual(law.category(law.proof_reasons(self.proof(table, "arm")["lines"], "arm")), "wait")

    def test_a_full_issue_page_is_unreadable(self):                       # Mythos F22
        page = json.dumps([{"number": i} for i in range(cc.VETO_LIMIT)])
        env = FakeRunEnv({"gh": cc.Result(0, page, "")})
        self.assertIsNone(cc.read_issues({"gh_argv": ["gh"], "repo_slug": "r", "owner_login": "o"}, env, lambda w: None))


class ConfigAndInstall(unittest.TestCase):
    def cfg(self):
        return json.loads((ROOT / "configs/launchd/cadence-controller.config.json.template").read_text()
                          .replace("@@MEASUREMENT_PYTHON@@", "/opt/venv/bin/python3.13")
                          .replace("@@DESK_COMMIT@@", "e" * 40))

    def test_config_template_loads_and_refusals(self):
        base = self.cfg()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "c.json"
            path.write_text(json.dumps(base))
            self.assertEqual(set(cc.load_config(path)), cc.CONFIG_KEYS)
            saved = os.environ.pop("JW_B5_SYNTHETIC_ONLY", None)
            try:
                for over in ({"git_dir": cc.CANONICAL_ROOT}, {"output_root": base["custody_root"] + "/out"},
                             {"output_root": "/Users/edr/night-custody/x"}, {"hold_standing_fence": "yes"},
                             {"poll_live_s": 2}, {"accept_mock_verdicts": True}):
                    path.write_text(json.dumps({**base, **over}))
                    with self.assertRaises(cc.ConfigError, msg=over):
                        cc.load_config(path)
            finally:
                if saved is not None:
                    os.environ["JW_B5_SYNTHETIC_ONLY"] = saved

    def test_launchd_template_is_a_keepalive_loop(self):
        plist = plistlib.loads((ROOT / "configs/launchd/com.joulewise.cadence-controller.plist.template").read_bytes())
        self.assertIs(plist["KeepAlive"], True)
        self.assertNotIn("StartInterval", plist)
        self.assertNotEqual(plist.get("ProcessType"), "Background")
        self.assertEqual(plist["ProgramArguments"][-3:], ["loop", "--config", "@@CONFIG@@"])

    def test_prompt_names_the_controller_and_its_heartbeat_within_twenty_five_lines(self):   # Mythos F15
        prompt = (ROOT / "docs/process/MAGISTRATE_RELAUNCH_PROMPT.md").read_text()
        self.assertLessEqual(len(prompt.splitlines()), 25)
        self.assertIn("com.joulewise.cadence-controller", prompt)
        self.assertIn("cadence_controller.py ack", prompt)
        self.assertIn("check-heartbeat", prompt)

    def test_heartbeat_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = {"state_dir": tmp}
            args = type("A", (), {"max_age": 300})
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cc.cmd_check_heartbeat(cfg, args), 1)
                cc.atomic_json(Path(tmp) / "heartbeat.json", {"pid": 1, "epoch": time.time(), "state": "WAIT"})
                self.assertEqual(cc.cmd_check_heartbeat(cfg, args), 0)


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class RL173EndToEnd(WorldCase):
    """RL-173's owner list for the controller builder, end to end (synthetic scenarios), plus the MBP desk step."""

    def test_actions_watcher(self):                          # C.4
        synth.scenario_actions_watcher(Path(self.tmp.name) / "aw", log=quiet)

    def test_offload_failed_or_unverified_holds_the_next_arm_and_f0(self):   # A.2, A.7
        synth.scenario_offload(Path(self.tmp.name) / "off", log=quiet)

    def test_l002_timeout_holds_every_arm(self):            # E
        synth.scenario_l002_timeout(Path(self.tmp.name) / "l002", log=quiet)

    def test_the_fence_is_continuous(self):                  # E
        synth.scenario_fence(Path(self.tmp.name) / "fence", log=quiet)

    def test_the_copy_gate_is_per_span(self):                # gate 3, Opus 1
        synth.scenario_copy_gate(Path(self.tmp.name) / "copy", log=quiet)

    def test_the_mbp_desk_runs_in_the_close_interval_and_counts(self):        # B
        w = self.pilot_world()
        w.tick()
        w.launcher.finish()
        s = w.tick()
        self.assertEqual(s["state"], "CLOSED", s)
        close = json.loads(self.state(w, "spans", "cq-dev-05-s01-a1", "close.json").read_text())
        rec = close["mbp_desk"]
        self.assertTrue(rec["published"] and rec["rc"] == 3 and rec["problem"] is None, rec)
        doc, _ = desk_transport.read_verdict(w.cfg["git_dir"], f"{cc.MBP_VERDICT_PREFIX}cq-dev-05-s01-a1",
                                             allowed_signers=w.cfg["controller_signers"], plan_id="cq-dev-05-s01-a1",
                                             principal=desk_transport.CONTROLLER_PRINCIPAL)
        self.assertEqual(doc["history_source"], "signed-records")
        self.assertEqual(doc["transport"]["signer"], "cadence-controller")
        self.assertEqual(doc["identities"]["manifest_sha256"], close["manifest_sha256"])
        # the desk ran after the push, inside the close: the floor counts from after it
        rows = [json.loads(x) for x in self.state(w, "transitions.jsonl").read_text().splitlines()]
        kinds = [r["transition"] for r in rows if r["plan_id"] == "cq-dev-05-s01-a1"]
        self.assertLess(kinds.index("bundle_pushed"), kinds.index("mbp_desk"))
        # the off-host desk (the Air) re-checks the pushed bundle and agrees on the automatic part
        w.copy_journals("cq-dev-05-s01-a1")
        w.queue("rest", [w.span(1, "dev-05-s02", "cl-dev-05", L[6:])])
        v = w.air_final("cq-dev-05-s01-a1", hand_table=True)
        self.assertTrue(v["desk_final"])
        self.assertEqual(desk_final_compare(doc, v), [])
        w.lead_release("cq-dev-05-s01-a1", "class-a")
        s = w.drive(lambda s: s["state"] == "LIVE")
        self.assertNotIn("DESK_DISAGREEMENT", self.pages(w))

    def test_a_desk_run_that_left_no_verdict_is_retried_next_tick(self):
        w = self.pilot_world()
        calls = []
        real = w.ctl.host_run

        def flaky(argv, **kw):
            calls.append(argv)
            if len(calls) == 1:
                return cc.Result(4, "LOCK held", "")
            return real(argv, **kw)
        w.ctl.host_run = flaky
        w.tick()
        w.launcher.finish()
        w.tick()
        close = json.loads(self.state(w, "spans", "cq-dev-05-s01-a1", "close.json").read_text())
        self.assertIsNone(close["mbp_desk"]["published"])
        w.env.t += 400
        w.tick()
        close = json.loads(self.state(w, "spans", "cq-dev-05-s01-a1", "close.json").read_text())
        self.assertTrue(close["mbp_desk"]["published"], close["mbp_desk"])
        self.assertEqual(len(calls), 2)


def desk_final_compare(a, b):
    from joulewise.cadence import desk_final
    return desk_final.compare_verdicts(a, b)


class RL173Units(unittest.TestCase):
    def test_read_watcher_run(self):
        cfg = {"gh_argv": ["gh"], "repo_slug": "o/r", "watcher_name": "mbp-watcher.yml"}
        run = {"id": 5, "path": ".github/workflows/mbp-watcher.yml", "status": "completed", "conclusion": "success",
               "run_started_at": "2026-11-17T08:00:00Z", "updated_at": "2026-11-17T08:01:00Z", "secret": "x"}
        env = FakeRunEnv({"gh api repos/o/r/actions/workflows/mbp-watcher.yml/runs?status=completed&per_page=1&branch=main&event=schedule":
                          cc.Result(0, json.dumps({"workflow_runs": [run]}), "")})
        got = cc.read_watcher_run(cfg, env, lambda w: None)
        self.assertEqual(got["id"], 5)
        self.assertNotIn("secret", got)
        env = FakeRunEnv({"gh api": cc.Result(0, json.dumps({"workflow_runs": []}), "")})
        self.assertIsNone(cc.read_watcher_run(cfg, env, lambda w: None))
        for res in (cc.Result(1, "", "HTTP 502"), cc.Result(0, "not json", ""), cc.Result(0, "{}", "")):
            self.assertEqual(cc.read_watcher_run(cfg, FakeRunEnv({"gh api": res}), lambda w: None), "unreadable")

    def test_config_watcher_kind_and_offload_argv(self):
        base = ConfigAndInstall.cfg(self)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "c.json"
            for over in ({"watcher_kind": "air"}, {"watcher_kind": "actions", "watcher_name": "com.joulewise.air-watch"},
                         {"offload_argv": ["offload", "{plan_id}"]}, {"offload_argv": ["/bin/offload"]},
                         {"offload_argv": "/bin/offload {plan_id}"}, {"controller_signers": "rel/path"}):
                path.write_text(json.dumps({**base, **over}))
                with self.assertRaises(cc.ConfigError, msg=over):
                    cc.load_config(path)
            for over in ({"watcher_kind": "stamp", "watcher_name": "com.joulewise.air-watch"},
                         {"offload_argv": ["/usr/local/bin/jw-offload", "--plan", "{plan_id}", "--out", "{output}"]}):
                path.write_text(json.dumps({**base, **over}))
                cc.load_config(path)

    def test_the_fence_is_renewed_before_every_network_call_and_never_taken_after_a_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = synth.World(Path(tmp) / "w", prior=False)
            ctl = w.controller()
            root = Path(w.cfg["custody_root"])
            self.assertEqual(ctl.hold_fence(), "held")
            first = cc.fence.read_fence(root)["deadline"]
            w.env.t += 500
            ctl.guard("a network call")
            self.assertEqual(cc.fence.read_fence(root)["deadline"], first + 500)
            ctl.release_fence()
            ctl.guard("another")
            self.assertIsNone(cc.fence.read_fence(root))       # a release is deliberate: guard never re-takes it
            self.assertEqual(ctl.refresh_fence(), "not held")
            self.assertEqual(ctl.startup_fence(), "held")
            w.env.night_labels = ["com.joulewise.night.w1"]
            ctl.release_fence()
            self.assertEqual(ctl.startup_fence(), "night")      # a loaded v4 window: the queue is ceded
            self.assertIsNone(cc.fence.read_fence(root))


class Gate3Controller(unittest.TestCase):
    """Gate 3 (Opus 4, 8, 9) on the controller's side."""

    def test_a_failing_desk_step_is_named_not_silent(self):
        recs = [{"plan_id": "p1", "mbp_desk": {"published": None, "problem": "desk rc 4: LOCK stale (pid gone; not stolen)",
                                               "attempts": 1}},
                {"plan_id": "p2", "mbp_desk": {"published": None, "problem": "desk rc 1: x", "attempts": 3}},
                {"plan_id": "p3", "mbp_desk": {"published": None, "problem": "desk rc 1: x", "attempts": 1}},
                {"plan_id": "p4", "mbp_desk": {"published": "c" * 40, "problem": None, "attempts": 1}}]
        self.assertEqual([r["span"] for r in cc.Controller.desk_step_reasons(recs)], ["p1", "p2"])
        self.assertEqual(law.category(cc.Controller.desk_step_reasons(recs)), "halt")

    def test_the_desk_commit_is_pinned(self):
        head = "a" * 40
        env = FakeRunEnv({f"git -C {cc.ROOT} rev-parse HEAD": cc.Result(0, head + "\n", ""),
                          f"git -C {cc.ROOT} status": cc.Result(0, "", "")})
        self.assertTrue(cc.desk_commit_check({"desk_commit": head}, env)["ok"])
        self.assertFalse(cc.desk_commit_check({"desk_commit": "b" * 40}, env)["ok"])
        env = FakeRunEnv({f"git -C {cc.ROOT} rev-parse HEAD": cc.Result(0, head + "\n", ""),
                          f"git -C {cc.ROOT} status": cc.Result(0, " M joulewise/cadence/desk_final.py\n", "")})
        self.assertFalse(cc.desk_commit_check({"desk_commit": head}, env)["ok"])
        lines = {name: {"ok": True} for name, kinds in law.PROOF_LINES.items() if "arm" in kinds}
        lines["desk_commit"] = {"ok": False, "detail": "pinned elsewhere"}
        self.assertEqual(law.category(law.proof_reasons(lines, "arm")), "halt")

    @unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
    def test_the_fence_is_taken_before_the_network_after_an_acknowledged_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = synth.World(Path(tmp) / "w", prior=False)
            ctl = w.controller()
            w.queue("pilot", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6], nb="2026-11-18")], role="smoke")
            w.issues.append({"number": 9, "title": "STOP", "labels": [{"name": "directive"}],
                             "author": {"login": "mpmdw"}, "state": "OPEN"})
            w.tick()
            self.assertIsNone(cc.fence.read_fence(Path(w.cfg["custody_root"])))     # the page released it
            w.ack_all()
            w.issues.clear()
            seen = []
            fetch = ctl.git.fetch_audit

            def watched():
                cur = cc.fence.read_fence(Path(w.cfg["custody_root"]))
                seen.append(cur is not None and cur["purpose"] == ctl.standing_purpose())
                return fetch()
            ctl.git.fetch_audit = watched
            w.env.t += 300
            w.tick()
            self.assertTrue(seen and all(seen), seen)


class Gate3ControllerMythos(unittest.TestCase):
    """Gate 3 (Mythos T4, T8, T12, T14, T17) on the controller's side."""

    def world(self, tmp):
        w = synth.World(Path(tmp) / "w", prior=False)
        w.controller()
        return w

    def test_an_own_fence_with_time_to_spare_is_not_rewritten_and_a_lapse_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = self.world(tmp)
            root = Path(w.cfg["custody_root"])
            w.ctl.hold_fence()
            before = (root / cc.fence.FENCE_NAME).stat().st_mtime_ns
            w.env.t += 100
            self.assertEqual(w.ctl.hold_fence(), "held")
            self.assertEqual(w.ctl.refresh_fence(), "held")
            self.assertEqual((root / cc.fence.FENCE_NAME).stat().st_mtime_ns, before)   # no write: no self-wake
            w.env.t += 2000
            self.assertEqual(w.ctl.refresh_fence(), "lapsed")

    @unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
    def test_a_stranded_page_leaves_the_fence_released_until_acknowledged(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = self.world(tmp)
            w.queue("pilot", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6])], role="smoke")
            w.tick()
            live = w.launcher.finish()
            root = Path(w.cfg["custody_root"])
            busy = [cc.Result(0, "123 cadence_legs_runner.py", "")]
            real_run = w.env.run
            w.env.run = lambda argv, **kw: busy[0] if "pgrep" in str(argv[0]) else real_run(argv, **kw)
            w.tick()
            w.env.t += cc.STRANDED_GRACE_S + 60
            w.tick()
            self.assertIn("STRANDED_ALARM", json.dumps([p["reasons"] for p in w.ctl.unacked_pages()]))
            self.assertIsNone(cc.fence.read_fence(root))
            w.env.t += 60
            w.tick()
            self.assertIsNone(cc.fence.read_fence(root))               # still released: the page is delivered
            w.ack_all()
            w.tick()
            self.assertIsNotNone(cc.fence.read_fence(root))
            self.assertTrue(live)

    def test_the_controller_signers_are_probed_at_the_arm(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = self.world(tmp)
            self.assertTrue(cc.controller_signers_check(w.cfg)["ok"])
            self.assertFalse(cc.controller_signers_check(dict(w.cfg, controller_signers=str(Path(tmp) / "none")))["ok"])
            self.assertFalse(cc.controller_signers_check(dict(w.cfg, controller_signers=w.cfg["verdict_signers"]))["ok"])

    @unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
    def test_a_failed_offload_is_retried_in_the_close_interval_then_held(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = self.world(tmp)
            w.cfg["offload_argv"] = ["/bin/false", "{plan_id}"]
            w.controller()
            calls = []
            real = w.ctl.host_run
            w.ctl.host_run = lambda argv, **kw: (calls.append(argv), real(argv, **kw))[1]
            w.queue("pilot", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6])], role="smoke")
            w.tick()
            w.launcher.finish()
            w.tick()
            for _ in range(4):
                w.env.t += 300
                w.tick()
            offloads = [a for a in calls if a[0] == "/bin/false"]
            self.assertEqual(len(offloads), cc.OFFLOAD_ATTEMPTS)
            self.assertIn("OFFLOAD_FAILED", json.dumps([p["reasons"] for p in w.ctl.unacked_pages()]))

    @unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
    def test_a_second_veto_pages_while_an_acknowledged_one_is_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = self.world(tmp)
            w.queue("pilot", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6], nb="2026-11-18")], role="smoke")
            veto = {"number": 901, "title": "STOP one", "labels": [{"name": "directive"}],
                    "author": {"login": "mpmdw"}, "state": "OPEN"}
            w.issues.append(veto)
            w.tick()
            w.ack_all()
            w.issues.append(dict(veto, number=907, title="STOP two"))
            w.env.t += 300
            w.tick()
            self.assertTrue(w.ctl.unacked_pages())


if __name__ == "__main__":
    unittest.main()


class Gate4Controller(unittest.TestCase):
    def test_a_missing_public_key_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            signers = root/'allowed'
            signers.write_text('cadence-controller ssh-ed25519 wrong-key\n')
            self.assertFalse(cc.controller_signers_check({'controller_signers': str(signers),
                                                         'signing_key': str(root/'missing')})['ok'])

    def test_production_cannot_disable_the_continuous_fence(self):
        from unittest import mock
        cfg = ConfigAndInstall().cfg()
        cfg['hold_standing_fence'] = False
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {'JW_B5_SYNTHETIC_ONLY': '0'}):
            path = Path(tmp)/'config.json'
            path.write_text(json.dumps(cfg))
            with self.assertRaisesRegex(cc.ConfigError, 'hold_standing_fence'):
                cc.load_config(path)

    @unittest.skipUnless(HAVE_TOOLS, 'synthetic git tools')
    def test_every_mid_arm_fence_lapse_halts_before_intent(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = synth.World(Path(tmp)/'w', prior=False)
            ctl = w.controller()
            w.queue('pilot', [w.span(1, 'dev-05-s01', 'cl-dev-05', L[:6])], role='smoke')
            check = ctl.preparer.check
            def slow_check(*a, **kw):
                result = check(*a, **kw)
                w.env.t += cc.STANDING_FENCE_S+1
                return result
            ctl.preparer.check = slow_check
            self.assertEqual(w.tick()['state'], 'HALTED')
            self.assertFalse((Path(w.cfg['state_dir'])/'spans/cq-dev-05-s01-a1/intent.json').exists())
            self.assertIn('ARM_INDETERMINATE', json.dumps(ctl.unacked_pages()))

    def test_upload_retry_reserves_full_timeout_and_resets_the_floor(self):
        from unittest import mock
        with tempfile.TemporaryDirectory() as tmp:
            ctl = object.__new__(cc.Controller)
            ctl.state = Path(tmp)/'state'
            ctl.custody = Path(tmp)/'custody'
            ctl.cfg = {'hold_standing_fence': True, 'offload_argv': ['/fake/upload', '{plan_id}', '{marker}'],
                       'copy_marker_dir': str(Path(tmp)/'markers')}
            ctl.env = synth.FakeEnv(10000)
            ctl.token, ctl.pid = 'test', os.getpid()
            path = ctl.span_dir('p1')
            cc.atomic_json(path/'intent.json', {'output': str(Path(tmp)/'output')})
            cc.atomic_json(path/'close.json', {'closed_epoch': 9000, 'offload': {'ok': False, 'attempts': 1, 'ended': 9000}})
            ctl.hold_fence(4500)
            ctl.env.t += 1500   # 3000 left, less than timeout
            left = []
            def upload(argv, **kwargs):
                left.append(cc.fence.read_fence(ctl.custody)['deadline']-ctl.env.now())
                ctl.env.t += cc.OFFLOAD_TIMEOUT_S
                return cc.Result(0, '', '')
            ctl.host_run = upload
            ctl.transition = mock.Mock()
            result = ctl.offload_close('p1')
            self.assertTrue(result['ok'])
            self.assertGreater(left[0], cc.OFFLOAD_TIMEOUT_S)
            self.assertGreater(cc.fence.read_fence(ctl.custody)['deadline'], ctl.env.now())
            self.assertEqual(cc.read_json(path/'close.json')['closed_epoch'], ctl.env.now())

    def test_upload_retries_wait_five_then_fifteen_minutes(self):
        from unittest import mock
        with tempfile.TemporaryDirectory() as tmp:
            ctl = object.__new__(cc.Controller)
            ctl.state, ctl.custody = Path(tmp)/'state', Path(tmp)/'custody'
            ctl.cfg = {'hold_standing_fence': False, 'offload_argv': ['/fake/upload', '{plan_id}'],
                       'copy_marker_dir': str(Path(tmp)/'markers')}
            ctl.env = synth.FakeEnv(10000)
            ctl.host_run = mock.Mock(return_value=cc.Result(7, '', 'provider down'))
            ctl.transition = mock.Mock()
            cc.atomic_json(ctl.span_dir('p1')/'intent.json', {'output': '/synthetic/output'})
            cc.atomic_json(ctl.span_dir('p1')/'close.json', {'closed_epoch': 9000})
            ctl.offload_close('p1')
            for step in (60, 60, 179):
                ctl.env.t += step
                self.assertIsNone(ctl.offload_close('p1'))
            ctl.env.t += 1
            ctl.offload_close('p1')
            ctl.env.t += 899
            self.assertIsNone(ctl.offload_close('p1'))
            ctl.env.t += 1
            ctl.offload_close('p1')
            ctl.env.t += 900
            self.assertIsNone(ctl.offload_close('p1'))
            self.assertEqual(ctl.host_run.call_count, 3)


class Gate4TickClock(unittest.TestCase):
    def test_snapshot_uses_the_clock_after_close_retries(self):
        from unittest import mock
        with tempfile.TemporaryDirectory() as tmp:
            ctl = object.__new__(cc.Controller)
            ctl.state, ctl.env = Path(tmp), synth.FakeEnv(1000)
            ctl.records = lambda: ([{'plan_id': 'p1', 'status': 'CLOSED_OK', 'closed_epoch': 900}], [])
            ctl.refresh_fence = ctl.hold_fence = mock.Mock(return_value='held')
            ctl._foreign_fence = lambda: None
            ctl.record_acked_sessions = lambda now: None
            ctl.unacked_pages = lambda: []
            ctl.night_agents = lambda: ([], True)
            ctl.desk_close = lambda plan: None
            def slow_upload(plan):
                ctl.env.t += 400
            ctl.offload_close = slow_upload
            clocks = []
            ctl.snapshot = lambda now, records: (clocks.append(now), ({}, {}))[1]
            ctl.critical_path = mock.Mock()
            ctl.act = lambda *args: {'state': 'WAIT'}
            ctl.settle_pages = mock.Mock()
            with mock.patch.object(law, 'select', return_value=law.Decision('wait', [])):
                ctl.tick()
            self.assertEqual(clocks, [1400])
