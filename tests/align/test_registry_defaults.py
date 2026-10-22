"""Default lane factories, built through the runner exactly as a matrix spec would."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from joulewise.align import runner
from joulewise.align.records import read_episodes


def _context(clock=lambda: 5):
    return runner.FactoryContext("shade/ledger_review", "benign", 0, "matrix", "episode.domain", clock)


class RegistryDefaultsTests(unittest.TestCase):
    def setUp(self):
        import joulewise.align.registry_defaults as defaults
        defaults.register_defaults()

    def test_factories_construct_from_json_shaped_configs(self):
        context = _context()
        endpoint = runner._make("endpoint", {"factory": "openai_compat", "config": {
            "base_url": "http://127.0.0.1:8000/v1", "model": "served"}}, context)
        self.assertEqual(endpoint.identity, "openai_compat:served@http://127.0.0.1:8000/v1")
        with tempfile.TemporaryDirectory() as directory:
            task = runner._make("task", {"factory": "shade", "config": {
                "upstream": {"cache_dir": directory, "allow_fetch": False},
                "judge_endpoint": {"base_url": "http://127.0.0.1:8001/v1", "model": "judge"}}},
                context)
            self.assertEqual(task.task_pair, "shade/ledger_review")
            self.assertEqual(task.judge_endpoint.identity, "openai_compat:judge@http://127.0.0.1:8001/v1")
            # A task whose pinned source cannot load raises from reset (shade
            # review-3 R3-F2 stopgap), so the runner measures no turns.
            with self.assertRaises(RuntimeError):
                task.reset(0)
            self.assertIn("upstream_cache_missing", task.flags)
        nvml = runner._make("sampler", {"factory": "nvml", "config": {"device_indices": [0]}}, context)
        self.assertEqual((nvml.clock_domain, nvml._clock()), ("episode.domain", 5))
        own = runner._make("sampler", {"factory": "nvml", "config": {"clock_domain": "gpu.host"}}, context)
        self.assertEqual(own.clock_domain, "gpu.host")
        self.assertIsNot(own._clock, context.clock)

    def test_matrix_import_installs_ina3221_on_the_episode_clock(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sys").mkdir()
            spec = {
                "matrix_id": "registry-defaults", "imports": ["joulewise.align.registry_defaults"],
                "clock_domain": "mock.monotonic", "clock": {"factory": "mock.clock"},
                "task_pairs": [{"factory": "mock.inbox", "task_pair": "mock/inbox-a"}],
                "conditions": ["benign"], "seeds": [0],
                "endpoints": [{"factory": "mock.scripted"}],
                # An empty sysfs tree: the sampler reports, it does not raise.
                "samplers": [{"factory": "ina3221", "config": {
                    "sysfs_root": str(root / "sys"), "sample_interval_ns": 10_000_000}}],
                "max_turns": 40, "max_tokens": 600, "temperature": 0.0, "output_dir": "out",
            }
            path = root / "matrix.json"
            path.write_text(json.dumps(spec), encoding="utf-8")
            (episode,) = read_episodes(runner.run_matrix(path))
        self.assertEqual([trace.clock_domain for trace in episode.power_traces], ["mock.monotonic"])
        self.assertIn("power.unavailable.ina3221_unavailable", episode.flags)
        self.assertNotIn("clock.unmapped", episode.flags)
        self.assertFalse([flag for flag in episode.flags if flag.startswith(("factory.", "matrix."))])

    def test_token_counter_raises_on_a_failure_after_a_longer_successful_history(self):
        """The endpoint clears its flags per operation, so the counter reads the outcome flag.

        First /tokenize: the vLLM-shaped body is refused (404), the llama.cpp body
        succeeds: two flags. Second: HTTP 500 on both shapes ends with
        tokenize_unavailable. A slice taken at the old flag length would see nothing.
        """
        import threading
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

        calls = []

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                calls.append(body)
                if len(calls) == 1 and "prompt" in body:
                    self.send_response(404)
                    self.end_headers()
                    return
                if len(calls) >= 3:
                    self.send_response(500)
                    self.end_headers()
                    return
                payload = json.dumps({"tokens": [1, 2, 3]}).encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_address[1]}/v1"
            counter = runner._make("token_counter", {"factory": "openai_compat", "config": {
                "base_url": base, "model": "served"}}, _context())
            self.assertEqual(counter.count_tokens("a b c"), 3)  # three tokens served: integer identity
            self.assertEqual(len(counter.endpoint.flags), 2)
            with self.assertRaises(RuntimeError):
                counter.count_tokens("d e f")
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
