"""Synthetic X6 custody controls; no hardware or launch authority is exercised."""
import copy
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from joulewise import arm_readiness as ar, battery_float, night_gate, v5_qualification as q
from joulewise.night_plan_writer import night_plan_mapping
from scripts import assemble_v5_battery_boundaries as assembler
from tests.test_battery_float import raw, UPDATE
from tests.test_night_gate import make_plan


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(ar.render_json(value))
    return q.reference(path)


def battery_fixture(root, plan_id="plan", *, charged_t0=False):
    """Native lifecycle shapes with physical probe seams injected explicitly."""
    root = Path(root)
    t0_wall = UPDATE + 100
    plan = make_plan(plan_id=plan_id, custody_root=str(root), t0_epoch_s=t0_wall,
                     authored_epoch_s=UPDATE - 100, window_max_s=3600)
    plan_path = root / "night_plan.json"
    plan_ref = put(plan_path, night_plan_mapping(plan))
    observations = {}
    for index, role in enumerate(q.BATTERY_BOUNDARY_PHASES):
        directory = root / "arm-attempts/000001" if role == "publication" else root
        name = "battery-float-at-publication" if role == "publication" else role
        payload = raw("charging-synthetic-from-real.ioreg") if role == "t0" and charged_t0 else raw()
        record, body = battery_float.observe(phase=q.BATTERY_BOUNDARY_PHASES[role], plan_id=plan_id,
            wall_time_s=UPDATE + index * 50, monotonic_ns=lambda: (index + 1) * 100,
            runner=lambda argv: subprocess.CompletedProcess(argv, 0, payload, b""))
        if role == "t0":
            record["raw_stdout"] = body.decode()
            receipt = {"schema": night_gate.SCHEMA, "plan_id": plan_id,
                       "authored_monotonic_ns": 310, "conditions": [
                           {"condition_id": "C3", "measured": {"battery_float": record}}]}
            receipt_ref = put(root / "night/receipt.json", receipt)
            record = {**record, "source_capture": receipt_ref}
        observations[role] = q.persist_battery_observation(directory, name, record, body)
    prepare_ref = put(root / "prepare.json", {
        "schema": "joulewise.evidence_prepare.v1", "plan_id": plan_id,
        "custody_root": str(root), "plan_path": str(plan_path),
        "digests": {str(plan_path): plan_ref["sha256"]}})
    arm_ref = put(root / "lifecycle/check.json", {
        "schema": "joulewise.evidence_check.v1", "prepare_sha256": prepare_ref["sha256"],
        "started_epoch_s": UPDATE - 1, "finished_epoch_s": UPDATE + 1,
        "fake_launchctl": False, "checks": {"battery_float": {
            **observations["arm"], "observation": q.read(Path(observations["arm"]["record"]["path"]))}}})
    attempt = root / "arm-attempts/000001"
    publication_ref = put(attempt / "install.json", {
        "schema": "joulewise.evidence_install.v1", "plan_sha256": plan_ref["sha256"],
        "published_plan": str(plan_path), "attempt_path": str(attempt),
        "fake_launchctl": False, "outcome": "installed",
        "started_epoch_s": UPDATE + 49, "published_epoch_s": UPDATE + 51})
    lifecycle = {"plan": plan_ref, "prepare": prepare_ref, "arm_check": arm_ref,
                 "publication": publication_ref, "t0_receipt": receipt_ref}
    return observations, lifecycle


class BatteryLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.observations, self.lifecycle = battery_fixture(self.root)

    def assemble(self):
        return assembler.assemble("plan", self.observations, self.root / "boundaries.json", lifecycle=self.lifecycle)

    def test_native_shapes_order_and_failed_physics_are_replayed(self):
        ref = self.assemble()
        self.assertTrue(q.battery_boundaries(Path(ref["path"]), ref["sha256"], "plan",
                                            plan_path=Path(self.lifecycle["plan"]["path"])))
        root = self.root / "charged"
        observations, lifecycle = battery_fixture(root, charged_t0=True)
        ref = assembler.assemble("plan", observations, root / "boundaries.json", lifecycle=lifecycle)
        self.assertFalse(q.battery_boundaries(Path(ref["path"]), ref["sha256"], "plan"))

    def test_unbound_archived_readings_do_not_publish(self):
        with self.assertRaisesRegex(q.HarvestRefusal, "lifecycle_missing"):
            assembler.assemble("plan", self.observations, self.root / "boundaries.json")
        self.assertFalse((self.root / "boundaries.json").exists())

    def test_reversed_and_stale_boundary_times_refuse_even_after_rehash(self):
        for role, key, value in (("arm", "monotonic_before_ns", 400),
                                 ("publication", "wall_time_s", UPDATE - 500),
                                 ("t0", "wall_time_s", UPDATE - 1)):
            with self.subTest(role=role):
                candidate = self.root / role
                observations, lifecycle = battery_fixture(candidate)
                path = Path(observations[role]["record"]["path"])
                record = q.read(path)
                record[key] = value
                if key == "monotonic_before_ns": record["monotonic_after_ns"] = value
                observations[role]["record"] = put(path, record)
                if role == "arm":
                    arm_path = Path(lifecycle["arm_check"]["path"])
                    arm = q.read(arm_path); arm["checks"]["battery_float"].update(
                        observation=record, **observations[role])
                    lifecycle["arm_check"] = put(arm_path, arm)
                with self.assertRaises(q.HarvestRefusal):
                    assembler.assemble("plan", observations, candidate / "boundaries.json", lifecycle=lifecycle)
                self.assertFalse((candidate / "boundaries.json").exists())

    def test_swapped_occurrence_lifecycle_and_wrong_harvest_plan_refuse(self):
        ref = self.assemble()
        other = self.root / "other.json"; put(other, {})
        with self.assertRaisesRegex(q.HarvestRefusal, "plan_locator_mismatch"):
            q.battery_boundaries(Path(ref["path"]), ref["sha256"], "plan", plan_path=other)
        lifecycle = copy.deepcopy(self.lifecycle)
        prepare_path = Path(lifecycle["prepare"]["path"])
        prepare = q.read(prepare_path); prepare["plan_id"] = "other"
        lifecycle["prepare"] = put(prepare_path, prepare)
        with self.assertRaises(q.HarvestRefusal):
            assembler.assemble("plan", self.observations, self.root / "wrong.json", lifecycle=lifecycle)

    def test_same_plan_id_receipt_from_another_custody_root_refuses(self):
        copied = self.root / 'foreign/night/receipt.json'
        receipt_ref = put(copied, q.read(Path(self.lifecycle['t0_receipt']['path'])))
        self.lifecycle['t0_receipt'] = receipt_ref
        observation_path = Path(self.observations['t0']['record']['path'])
        observation = q.read(observation_path)
        observation['source_capture'] = receipt_ref
        self.observations['t0']['record'] = put(observation_path, observation)
        with self.assertRaisesRegex(q.HarvestRefusal, 't0_receipt_locator_mismatch'):
            self.assemble()

    def test_old_arm_check_cannot_be_replayed_as_current_publication_authority(self):
        arm_path = Path(self.lifecycle['arm_check']['path'])
        arm = q.read(arm_path)
        # Keep the battery reading inside its check window, but move that
        # window's finish back beyond the native publish-install freshness cap.
        arm['started_epoch_s'] = UPDATE - 4001
        arm['finished_epoch_s'] = UPDATE - 4000
        observation_path = Path(self.observations['arm']['record']['path'])
        # A physics refusal is valid archival evidence; it cannot make an old
        # lifecycle check fresh. Preserve its replayed parser result.
        parsed = battery_float.observe(phase='arm_check', plan_id='plan',
            wall_time_s=UPDATE - 4000, monotonic_ns=lambda: 100,
            runner=lambda argv: subprocess.CompletedProcess(argv, 0, raw(), b''))[0]
        self.observations['arm']['record'] = put(observation_path, parsed)
        arm['checks']['battery_float'].update(observation=parsed, **self.observations['arm'])
        self.lifecycle['arm_check'] = put(arm_path, arm)
        with self.assertRaisesRegex(q.HarvestRefusal, 'order_or_timing_invalid'):
            self.assemble()


class StageListTests(unittest.TestCase):
    def test_chain_bound_list_preflight_rejects_missing_mutated_symlink_and_unpinned(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            path = root / "before_midpoint_stages.txt"
            body = b"configs/campaigns/science\n"
            digest = ar.sha256_bytes(body)
            chain = ('test "$(/usr/bin/shasum -a 256 "$1/before_midpoint_stages.txt" | '
                     "/usr/bin/awk '{print $1}')\" = \"" + digest + '"\n').encode()
            with self.assertRaises(ValueError): ar.authenticated_stage_list(root, chain)
            path.write_bytes(body)
            self.assertEqual(ar.authenticated_stage_list(root, chain), q.reference(path))
            path.write_bytes(body + body)
            with self.assertRaises(ValueError): ar.authenticated_stage_list(root, chain)
            path.unlink(); other = root / "other.txt"; other.write_bytes(body); path.symlink_to(other)
            with self.assertRaises(ValueError): ar.authenticated_stage_list(root, chain)
            path.unlink(); path.write_bytes(body)
            with self.assertRaises(ValueError): ar.authenticated_stage_list(root, b"cat before_midpoint_stages.txt\n")


class ClockSizingTests(unittest.TestCase):
    def setUp(self):
        from tests.test_v5_qualification_plan import PlanWriterTests
        self.fixture = PlanWriterTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.write()
        self.input_root = self.fixture.custody / self.fixture.pack.name / 'arm_readiness.t0.inputs'

    def test_budget_is_derived_from_sources_pinned_by_authorized_chain(self):
        maximum, refs = q.authenticated_clock_budget(self.input_root, self.fixture.pack)
        self.assertEqual(maximum, 100.)
        self.assertEqual(len(refs), 5)
        for ref in refs: q.authenticated_reference(ref)

    def test_short_gate_cannot_override_sizing_even_after_internal_rehash(self):
        from joulewise import kernel_clock
        from tests.test_kernel_clock import frequency_probe
        path = self.input_root / 'kernel-frequency-gate.json'
        put(path, kernel_clock.frequency_gate(frequency_probe(), 1))
        with self.assertRaisesRegex(q.HarvestRefusal, 'stream_maximum_mismatch'):
            q.authenticated_clock_budget(self.input_root, self.fixture.pack)

    def test_changed_sizing_and_fresh_locator_still_need_authorized_chain_binding(self):
        binding_path = self.input_root / 'kernel-frequency-binding.json'
        binding = q.read(binding_path)
        path = Path(binding['sizing']['path'])
        sizing = q.read(path)
        sizing['streams']['calibration-pre']['seconds'] = 1
        binding['sizing'] = put(path, sizing)
        put(binding_path, binding)
        with self.assertRaisesRegex(q.HarvestRefusal, 'sizing_source_mismatch'):
            q.authenticated_clock_budget(self.input_root, self.fixture.pack)

    def test_arm_numeric_replay_rechecks_the_bound_maximum(self):
        from tests.test_v5_block4_clock import Block4ClockTests
        value, receipt = Block4ClockTests().derive(1000, stream_max=100.)
        value['clock_sizing_binding'] = q.reference(self.input_root / 'kernel-frequency-binding.json')
        self.assertTrue(ar._clock_probe_predicate_passes(receipt, value, ar._PREDICATE_LIVE_ANCHOR_NOT_APPLICABLE))
        value['t_stream_max_s'] = 1
        self.assertFalse(ar._clock_probe_predicate_passes(receipt, value, ar._PREDICATE_LIVE_ANCHOR_NOT_APPLICABLE))

    def test_r0_and_author_recheck_real_sizing_authority(self):
        from types import SimpleNamespace
        from joulewise import arm_readiness_evidence_t0 as author, kernel_clock
        from scripts import capture_t0_step as capture
        from tests.test_arm_readiness_evidence_t0 import _clock_reference_value, TEST_BOOT_SESSION_ID
        from tests.test_kernel_clock import frequency_probe
        boot = TEST_BOOT_SESSION_ID
        stdout = ar.render_json(_clock_reference_value(boot_session_id=boot,
                                                       anchor_monotonic_raw_ns=1_000_000_000_000))
        context = SimpleNamespace(input_root=self.input_root, pack_root=self.fixture.pack,
            repository=self.fixture.repo, boot_session_id=boot)
        completed = SimpleNamespace(kernel_frequency=frequency_probe(), stdout=stdout,
                                    stderr=b'', returncode=0)
        with (mock.patch.object(capture, '_load_context', return_value=context),
              mock.patch.object(capture, '_prepare_derived_inputs', return_value=[]),
              mock.patch.object(capture, '_require_sequence'),
              mock.patch.object(capture, '_command_for_step', return_value=['/fixture/collector']),
              mock.patch.object(capture, '_current_boot_session_id', return_value=boot),
              mock.patch.object(capture, '_arm_reference', return_value=(completed, 20)),
              mock.patch.object(capture, '_validate_result'),
              mock.patch.object(kernel_clock, 'read_kernel_frequency', return_value=frequency_probe())):
            result = capture._capture_step_with_dependencies('clock-reference', self.fixture.pack,
                self.fixture.custody, self.fixture.root, monotonic_ns=lambda: 10)
            captured = q.read(Path(result['capture_path']))
            self.assertEqual(captured['t_stream_max_s'], 100.)
            Path(result['capture_path']).unlink()
            put(self.input_root / 'kernel-frequency-gate.json', kernel_clock.frequency_gate(frequency_probe(), 1))
            with self.assertRaisesRegex(capture.CaptureT0Error, 'stream_maximum_mismatch'):
                capture._capture_step_with_dependencies('clock-reference', self.fixture.pack,
                    self.fixture.custody, self.fixture.root, monotonic_ns=lambda: 10)
        put(self.input_root / 'kernel-frequency-gate.json', kernel_clock.frequency_gate(frequency_probe(), 100))
        context = SimpleNamespace(pack_root=self.fixture.pack, values={}, boot_session_id=boot,
                                  custody_pack_root=self.input_root.parent)
        captured['argv'] = ['/fixture/collector']
        with (mock.patch.object(author, '_capture', return_value=(captured, {})),
              mock.patch.object(author, '_clock_reference_capture_argv', return_value=captured['argv']),
              mock.patch.object(ar, 'requires_t0_frequency_gate', return_value=True)):
            value, _identity, _agreement = author._captured_clock_reference(context, kind='CLOCK_ATTESTATION')
            self.assertEqual(value['clock_sizing_binding'], q.reference(self.input_root / 'kernel-frequency-binding.json'))
            context.values.clear()
            captured['t_stream_max_s'] = 1.
            with self.assertRaisesRegex(author.T0EvidenceAuthoringError, 'authenticated sizing'):
                author._captured_clock_reference(context, kind='CLOCK_ATTESTATION')

    def test_g4_replays_real_binding_and_refuses_rehashed_short_maximum(self):
        from dataclasses import replace
        from joulewise import kernel_clock, t0_rehearsal as t0
        from tests.test_kernel_clock import frequency_probe
        from tests.test_t0_rehearsal import FixtureBuilder, fixture_bundle
        root = FixtureBuilder(self.fixture.root / 'g4').build()
        namespace = root / 't0-namespace'
        source_path = namespace / 'arm_readiness.t0.sources/clock-correct-and-prior-state.json'
        source = q.read(source_path)
        value = source['facts'][0]['value']
        capture = namespace / 'arm_readiness.t0.inputs/clock-reference.json'
        r0 = q.read(capture)
        r0.update(kernel_frequency=frequency_probe(), t_stream_max_s=100.)
        put(capture, r0)
        maximum, refs = q.authenticated_clock_budget(self.input_root, self.fixture.pack)
        value.update(anchor_check_version=kernel_clock.ANCHOR_CHECK_VERSION,
            r0_kernel_frequency=frequency_probe(), kernel_frequency=frequency_probe(),
            t_stream_max_s=maximum, anchor_residual_ns=0.,
            clock_sizing_binding=q.reference(self.input_root / 'kernel-frequency-binding.json'))
        source['input_artifacts'][0] = q.reference(capture)
        source['input_artifacts'].extend(refs)
        receipt_path = next((namespace / 'arm_readiness.evidence').glob('*clock-correct*'))

        def replay():
            put(source_path, source)
            receipt = q.read(receipt_path)
            receipt['facts'][0].update(value=value, source_sha256=q.sha(source_path))
            put(receipt_path, receipt)
            bundle = fixture_bundle(root)
            # Source custody for these independently authenticated plan inputs
            # is explicit, as it is in a retained production bundle.
            extra = tuple(t0.EvidenceArtifact(ref['path'], Path(ref['path']),
                Path(ref['path']).read_bytes(), ref['sha256'],
                q.read(Path(ref['path'])) if ref['path'].endswith('.json') else None) for ref in refs)
            return t0.evaluate_g4(replace(bundle, artifacts=bundle.artifacts + extra))

        result = replay()
        self.assertEqual(result.status.value, 'PASS', result.message)
        value['t_stream_max_s'] = 1.
        r0['t_stream_max_s'] = 1.
        source['input_artifacts'][0] = put(capture, r0)
        result = replay()
        self.assertEqual(result.status.value, 'FAIL')
        self.assertIn('authenticated sizing', result.message)


class StageLaunchBoundaryTests(unittest.TestCase):
    def test_missing_list_refuses_launcher_before_capability_consumption(self):
        from types import SimpleNamespace
        from scripts import launch_window as launch
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            pack = root / 'pack'; pack.mkdir()
            window = root / 'window'; window.mkdir()
            (window / 'window.env').write_text('fixture\n')
            chain = window / 'window-chain.zsh'
            chain.write_text('test "$(/usr/bin/shasum -a 256 "$1/before_midpoint_stages.txt" | '
                             "/usr/bin/awk '{print $1}')\" = \"" + 'a' * 64 + '"\n')
            arm = root / 'arm.json'; arm.write_bytes(b'{}\n')
            go = root / 'go.json'; go.write_bytes(b'{}\n')
            manifest_path = root / 'launch.json'; manifest_path.write_bytes(b'{}\n')
            manifest = {'window_plan_root': str(window), 'launch_command': ['/fixture/no-exec']}
            args = SimpleNamespace(night_plan=root / 'plan.json', go_receipt=go,
                pack_root=pack, arm_readiness_custody_root=root, arm_receipt=arm,
                launch_manifest=manifest_path, step6_confirmation_table=root / 'confirmation.json',
                expected_confirmation_digest='a' * 64)
            with (mock.patch.object(launch, '_admit_pack_launch_go', return_value={}),
                  mock.patch.object(launch, '_load_manifest_input', return_value=(manifest, manifest_path, b'{}\n')),
                  mock.patch.object(launch, 'validate_arm_receipt', return_value={}),
                  mock.patch.object(launch, '_verify_arm_receipt', return_value={
                      'receipt_sha256': q.sha(arm), 'receipt_path': str(arm)}),
                  mock.patch.object(launch, '_consume_launch_capability') as consume,
                  self.assertRaises(ar.LaunchLineageError) as caught):
                launch._launch(args, None)
            self.assertEqual(caught.exception.reason_code, 'launch_binding_mismatch')
            consume.assert_not_called()

    def test_author_attests_the_list_and_missing_list_cannot_publish(self):
        from joulewise import arm_readiness_evidence_t0 as author
        from tests.test_arm_readiness_evidence_t0 import make_t0_fixture, author_environment
        temporary, repository, pack, custody, _context, inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        put(inputs / 'kernel-frequency-binding.json', {'pack_root': str(pack), 'fixture_only': True})
        window = Path(q.read(inputs / 'launch-manifest.json')['window_plan_root'])
        path = window / 'before_midpoint_stages.txt'
        body = b'configs/campaigns/fixture-science\n'
        chain = window / 'window-chain.zsh'
        guard = ('test "$(/usr/bin/shasum -a 256 "$1/before_midpoint_stages.txt" | '
                 "/usr/bin/awk '{print $1}')\" = \"" + ar.sha256_bytes(body) + '"\n')
        chain.write_text(guard + chain.read_text())
        # Clock/physical seams are unrelated to this launch-input proof. The
        # real sizing binding is independently tested by ClockSizingTests.
        with author_environment(repository), mock.patch.object(q, 'authenticated_clock_budget', return_value=(320., ())):
            with self.assertRaises(author.T0EvidenceAuthoringError):
                author.author_arm_readiness_evidence_t0(pack, custody)
            self.assertFalse((inputs.parent / 'arm_readiness.evidence').exists())
            path.write_bytes(body)
            result = author.author_arm_readiness_evidence_t0(pack, custody)
        self.assertEqual(result['status'], 'PASS')
        receipt_path = next(Path(value) for value in result['receipt_paths'] if 'single-launch-capability' in value)
        receipt = q.read(receipt_path)
        source = q.read(custody / pack.name / receipt['facts'][0]['source_path'])
        self.assertIn(q.reference(path), source['input_artifacts'])
