# Exhibit D — tests that pin the census at main 4b9a34111d33a04727a09127a1c1fbd8aab87052

## tests/test_arm_readiness_evidence_t0.py around line 2509
```python
            [probe.exit_code for probe in probes],
        )
        self.assertEqual(
            [probe["argv"] for probe in source["probes"]],
            [list(command) for command in commands],
        )
        self.assertEqual(
            [probe["stdout"] for probe in source["probes"]],
            [probe.stdout for probe in probes],
        )
        self.assertEqual(
            [probe["stderr"] for probe in source["probes"]],
            [probe.stderr for probe in probes],
        )
        return probes, source

    @unittest.skipUnless(
        sys.platform == "darwin", "requires Darwin's real pgrep command semantics"
    )
    def test_real_maintenance_census_executes_pgrep_and_binds_output(self) -> None:
        self._real_probe_source(
            "MAINTENANCE_CENSUS",
            (
                (
                    "/usr/bin/pgrep",
                    "-lf",
                    "XProtect|mds_stores|mdworker|mdbulkimport|backupd|photoanalysisd|softwareupdated|Spotlight|mediaanalysisd",
                ),
            ),
        )

    @unittest.skipUnless(
        sys.platform == "darwin", "requires Darwin's real pgrep command semantics"
    )
    def test_real_process_census_executes_pgrep_and_binds_output(self) -> None:
        self._real_probe_source(
            "PROCESS_CENSUS",
            (
                ("/usr/bin/pgrep", "-x", "caffeinate"),
                ("/usr/bin/pgrep", "-lf", "codex|claude|t3"),
                (
                    "/usr/bin/pgrep",
                    "-lf",
                    "Safari|Google Chrome|Chromium|Firefox|browser automation",
                ),
                (
                    "/usr/bin/pgrep",
                    "-lf",
                    "powermetrics|window-chain|run_campaign|tail -f|watch",
                ),
            ),
        )

    @unittest.skipUnless(
        sys.platform == "darwin", "requires Darwin's real sysctl command"
    )
    def test_real_boot_census_executes_sysctl_and_binds_machine_result(self) -> None:
        probes, _source = self._real_probe_source(
            "MACHINE_PREFLIGHT",
            (("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid"),),
        )
        probe = probes[0]
        if probe.exit_code == 0:
            self.assertRegex(
                probe.stdout.strip().lower(),
                r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
            )
        else:
            self.assertTrue(probe.stderr.strip())

    def test_missing_first_artifact_refuses_without_output(self) -> None:
        temporary, repository, pack, custody, _context, inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        (inputs / "clock-reference.json").unlink()
        with author_environment(repository), self.assertRaises(T0EvidenceAuthoringError) as caught:
            author_arm_readiness_evidence_t0(pack, custody)
        self.assertEqual(caught.exception.kind, "CLOCK_ATTESTATION")
        self.assertEqual(
            caught.exception.reason_code, "evidence_author_t0_clock_attestation_missing"
        )
        self.assertFalse((custody / pack.name / t0._SOURCE_DIRECTORY).exists())
        self.assertFalse((custody / pack.name / t0._EVIDENCE_DIRECTORY).exists())

    def test_named_refusal_matrix_covers_every_distinct_kind(self) -> None:
        cases = (
            ("CLOCK_ATTESTATION", lambda _r, _p, _c, _x: ( _x / "clock-reference.json").unlink(), {}),
            ("CLOCK_PROBE", lambda *_args: None, {"probe": lambda argv, *, cwd: _probe_result(argv, cwd, exit_code=1, stderr="sudo refused\n") if "systemsetup" in " ".join(argv) else passing_probe(argv, cwd=cwd)}),
            ("TERMINAL_REVIEW", lambda *_args: None, {"patch_message": True}),
            ("MAINTENANCE_CENSUS", lambda *_args: None, {"probe": lambda argv, *, cwd: _probe_result(argv, cwd, exit_code=0, stdout="123 XProtect\n") if "XProtect" in " ".join(argv) else passing_probe(argv, cwd=cwd)}),
            ("ROOT_PREFLIGHT", lambda _r, _p, c, _x: (Path(c["claim_runs_root"]) / "campaign.lock").write_text("busy\n"), {}),
            ("MACHINE_PREFLIGHT", lambda _r, _p, _c, x: _write_json(x / "quiet-mac-prep.json", {**json.loads((x / "quiet-mac-prep.json").read_text()), "stdout": "READY.\n"}), {}),
```

## tests/test_arm_readiness_integration.py around line 418
```python
        self.addCleanup(temporary.cleanup)
        with author_environment(
            repository, probe=passing_probe, now_monotonic_ns=now,
            sample_anchor=coherent_clock_anchor,
        ):
            authored = author_arm_readiness_evidence_t0(pack, custody)
        self.assertEqual(authored["status"], "PASS", authored)
        self.assertEqual(len(authored["authored_rows"]), 15)
        with mock.patch.object(
            readiness, "verify_frozen_projection",
            side_effect=synthetic_identity_verifier,
        ):
            arm = generate_arm_receipt(pack, context, custody)
        self.assertEqual(arm["status"], "PASS", arm)
        self.assertEqual(verify_arm_receipt(pack, arm["receipt_path"])["status"], "PASS")
        before = {path: Path(path).read_bytes() for path in authored["receipt_paths"]}
        for pattern, kind in (
            ("XProtect", "MAINTENANCE_CENSUS"),
            ("codex|claude|t3", "PROCESS_CENSUS"),
        ):
            for exit_code, stdout in (
                (0, "123 forbidden-process\n"), (2, ""), (1, "123 stale-output\n")
            ):
                with self.subTest(pattern=pattern, exit_code=exit_code, stdout=stdout):
                    observed = []

                    def bad_probe(argv, *, cwd):
                        if argv[0] == "/usr/bin/pgrep" and pattern in argv[-1]:
                            observed.append(tuple(argv))
                            return _probe_result(
                                argv, cwd, exit_code=exit_code, stdout=stdout
                            )
                        return passing_probe(argv, cwd=cwd)

                    with author_environment(
                        repository, probe=bad_probe, now_monotonic_ns=now,
                        sample_anchor=coherent_clock_anchor,
                    ):
                        with self.assertRaises(T0EvidenceAuthoringError) as caught:
                            author_arm_readiness_evidence_t0(pack, custody)
                    self.assertTrue(observed)
```
