# Exhibit B — the real-load regression at `498ad1d0` (`tests/test_sample_quiet_predicate_evidence.py` lines 600–654)

```python
    @unittest.skipUnless(sys.platform == "darwin", "native QoS requires macOS")
    def test_real_load_tracks_point_one_core_and_guards_worker_budget(self):
        # +/- .04 cores permits .12 CPU seconds of startup, timer and scheduling
        # variation in a 3 s calibration-only window; it still rejects 1 core.
        # Use 500 ms periods: this host can coalesce sleeps by ~150 ms, longer
        # than a 100 ms period, and the controller deliberately never catches up.
        # Check config BEFORE launch so the cores mutation cannot burn a core.
        context = harness.multiprocessing.get_context("spawn")
        def process(*args, **kwargs):
            self.assertEqual(kwargs["args"][1]["share"], .1)
            return context.Process(*args, **kwargs)
        guarded = SimpleNamespace(Pipe=context.Pipe, Process=process)
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(harness.multiprocessing, "get_context", return_value=guarded):
            args = harness.parser().parse_args(["load", "--cores", "0.1", "--duration-s", "3",
                "--period-ms", "500", "--qos", "user-initiated", "--profile", "scalar",
                "--seed", "1", "--log", str(Path(tmp) / "load.json")])
            harness.load(args)
            report = json.loads(Path(args.log).read_text())
        self.assertIsNone(report["error"], report["error"])
        periods = [p for worker in report["workers"] for p in worker["periods"]]
        fraction = sum(p["cpu_used_s"] for p in periods) / args.duration_s
        late_s = sum(p["wake_late_s"] for p in periods)
        # Over-burning is a budgeting defect under any scheduling: never allowed.
        self.assertLessEqual(fraction, .1 + .04, f"over-burned: {fraction:.4f} cores; late {late_s:.3f} s")
        if late_s <= .12:
            # The scheduler kept its wake promises: the tight two-sided check.
            self.assertAlmostEqual(fraction, .1, delta=.04)
        else:
            # Scheduler starvation observed (delta re-audit D5-T1): the controller never
            # catches up, so the deficit must be explained by the late wakes alone.
            self.assertGreaterEqual(fraction, .1 - .04 - .1 * late_s / args.duration_s,
                f"deficit not explained by late wakes: {fraction:.4f} cores; late {late_s:.3f} s")
        self.assertTrue(report["cleanup"])
        for child in report["cleanup"]:
            self.assertFalse(child["alive"])
            self.assertEqual(child["exitcode"], 0)
            with self.assertRaises(ProcessLookupError):
                os.kill(child["pid"], 0)

    def test_cpu_budget_overshoot_and_frozen_duty(self):
        clock = FakeClock()
        periods = harness.duty_periods(.2, 9, .1, clock.burn, clock)
        self.assertAlmostEqual(sum(p["cpu_used_s"] for p in periods), 1.8, delta=.01)
        for period in periods:
            self.assertLessEqual(period["overrun_cpu_s"], period["overshoot_bound_cpu_s"] + 1e-10)
            self.assertLess(period["overrun_cpu_s"], .0002)
            self.assertLess(period["wake_late_s"], .0002)
        frozen = [p for p in periods if not p["calibrating"]]
        self.assertGreater(len(frozen), 30)
        self.assertEqual(len({p["duty"] for p in frozen}), 1)
        self.assertEqual(len({p["batch"] for p in frozen}), 1)

    def test_stationarity_stationary_and_known_drift(self):
        periods = [{"start_mono_s": i, "end_mono_s": i + 1, "elapsed_s": 1,
```
