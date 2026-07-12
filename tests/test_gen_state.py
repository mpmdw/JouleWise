"""DOC-008 Stage-1 tests: state-kernel validity, migration fidelity, and
generator determinism / --check self-consistency.

The live RUN_STATE.md / TASK_QUEUE.md have NOT been converted to marker
fences yet (adjudication-gated), so --check runs against generator-produced
fixture files, i.e. against the kernel itself.
"""

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import gen_state  # noqa: E402

KERNEL_PATH = os.path.join(ROOT, "docs", "process", "state_kernel.json")
SCHEMA_PATH = os.path.join(ROOT, "docs", "process", "state_kernel.schema.json")
GEN = os.path.join(ROOT, "scripts", "gen_state.py")

EXPECTED_IDS = {
    # [AGENT]
    "P2-035", "P2-036", "P3-000", "P2-022", "P2-023",
    "P2-024", "P2-028", "P3-001b", "P2-004", "P2-005", "P2-016",
    "P2-047A", "P2-048", "CI-003", "DOC-010",
    # [QUIET-MAC]
    "P2-015-SMOKE", "P2-015", "P2-006", "P2-010", "P2-019", "P2-020",
    "P2-012", "P2-038", "P2-046B", "P2-047B",
    # [ED-EXTERNAL]
    "P1-008", "P2-027", "P1-001", "P1-003", "P1-004", "P1-006",
}

TERMINAL_IDS = {"P2-015-PREP", "P2-029", "P2-030", "P2-031", "P2-032", "P2-034",
                "DOC-008"}


def load_kernel():
    with open(KERNEL_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def run_gen(*args):
    return subprocess.run(
        [sys.executable, GEN, *args], capture_output=True, text=True
    )


class TestKernelValidity(unittest.TestCase):
    def test_schema_declares_v2_authority_contract(self):
        with open(SCHEMA_PATH, encoding="utf-8") as fh:
            schema = json.load(fh)
        self.assertEqual(schema["properties"]["schema_version"]["const"], 2)
        self.assertIn("authority", schema["required"])
        self.assertEqual(
            schema["properties"]["authority"]["const"],
            gen_state.AUTHORITY_NOTICE,
        )

    def test_kernel_validates(self):
        gen_state.validate(load_kernel())

    def test_kernel_bytes_are_canonical(self):
        with open(KERNEL_PATH, "rb") as fh:
            raw = fh.read()
        self.assertEqual(raw, gen_state.canonical_bytes(json.loads(raw.decode("utf-8"))))

    def test_invalid_kernels_rejected(self):
        base = load_kernel()
        cases = [
            ("unknown top-level field", lambda k: k.update(surprise=1)),
            ("bad schema_version", lambda k: k.update(schema_version=1)),
            ("missing authority", lambda k: k.pop("authority")),
            ("altered authority", lambda k: k.update(authority="AUTHORITATIVE")),
            ("id/key mismatch", lambda k: k["tasks"]["P2-028"].update(id="P2-999")),
            ("terminal status", lambda k: k["tasks"]["P2-028"].update(status="done")),
            ("duplicate lane rank", lambda k: k["tasks"]["P2-028"].update(rank=0)),
            ("blocked without hard start dep", lambda k: k["tasks"]["P2-028"].update(status="blocked")),
            ("queued with hard start dep", lambda k: k["tasks"]["P2-035"].update(status="queued")),
            ("dangling pending task dep",
             lambda k: k["tasks"]["P2-035"]["dependencies"][0].update(target="NOPE-1")),
            ("self-dependency",
             lambda k: k["tasks"]["P2-035"]["dependencies"][0].update(target="P2-035")),
            ("pending dep with evidence",
             lambda k: k["tasks"]["P2-035"]["dependencies"][0].update(
                 evidence={"path": "docs/decision_log.md", "label": "x"})),
            ("missing pointer target",
             lambda k: k["tasks"]["P2-028"]["authority"].update(path="docs/does_not_exist.md")),
            ("absolute pointer path",
             lambda k: k["tasks"]["P2-028"]["authority"].update(path="/etc/passwd")),
            ("pipe in goal", lambda k: k["tasks"]["P2-028"].update(goal="a | b")),
            ("unknown flag", lambda k: k["tasks"]["P2-028"].update(flags=["nope"])),
            ("quiet_mac without lead_only",
             lambda k: k["tasks"]["P2-019"].update(flags=[])),
            ("blocked_post_2m without P2-006 dep",
             lambda k: k["tasks"]["P2-022"].update(
                 dependencies=[d for d in k["tasks"]["P2-022"]["dependencies"]
                               if d["target"] != "P2-006"], status="queued")),
        ]
        for name, mutate in cases:
            kernel = copy.deepcopy(base)
            mutate(kernel)
            with self.assertRaises(gen_state.KernelError, msg=name):
                gen_state.validate(kernel)

    def test_cycle_rejected(self):
        kernel = copy.deepcopy(load_kernel())
        kernel["tasks"]["P2-015"]["dependencies"] = [
            {"kind": "task", "target": "P2-035", "required": "cycle",
             "state": "pending", "strength": "hard", "scope": "start",
             "evidence": None}
        ]
        with self.assertRaises(gen_state.KernelError):
            gen_state.validate(kernel)


class TestRefreshedStateFidelity(unittest.TestCase):
    """Assertions against the final C-028 live-state refresh."""

    def setUp(self):
        self.kernel = load_kernel()
        self.tasks = self.kernel["tasks"]

    def test_exact_live_id_set_31(self):
        self.assertEqual(set(self.tasks), EXPECTED_IDS)
        self.assertEqual(len(self.tasks), 31)

    def test_schema_v2_authority_notice(self):
        self.assertEqual(self.kernel["schema_version"], 2)
        self.assertEqual(
            self.kernel["authority"], gen_state.AUTHORITY_NOTICE
        )

    def test_terminal_ids_absent_from_kernel_present_in_completed_table(self):
        self.assertFalse(TERMINAL_IDS & set(self.tasks))
        with open(os.path.join(ROOT, "TASK_QUEUE.md"), encoding="utf-8") as fh:
            queue_text = fh.read()
        completed = queue_text.split("## Completed Queue Items", 1)[1]
        completed = completed.split("## Shelved Follow-Ups With Triggers", 1)[0]
        for tid in sorted(TERMINAL_IDS):
            self.assertIn(f"| {tid} |", completed)

    def test_stop_card_cleared(self):
        self.assertIsNone(self.kernel["active_stop_card"])
        for task in self.tasks.values():
            self.assertIsNone(task["stop_card"])

    def _hard_start_targets(self, tid):
        return {
            d["target"] for d in self.tasks[tid]["dependencies"]
            if d["scope"] == "start" and d["strength"] == "hard"
            and d["state"] == "pending" and d["kind"] == "task"
        }

    def test_p2_015_dependency_set(self):
        self.assertEqual(
            self._hard_start_targets("P2-015"),
            {"P2-015-SMOKE", "P2-038"},
        )
        all_targets = {d["target"] for d in self.tasks["P2-015"]["dependencies"]}
        self.assertEqual(
            all_targets,
            {"P0-003", "P2-015-SMOKE", "P2-038", "P2-039", "P2-043"},
        )

    def test_p2_006_gates(self):
        self.assertIn("P2-015", self._hard_start_targets("P2-006"))
        interpret = {
            d["target"] for d in self.tasks["P2-006"]["dependencies"]
            if d["scope"] == "interpret" and d["strength"] == "hard"
        }
        self.assertEqual(interpret, {"P2-037", "P2-041", "P2-044", "P2-045"})
        for dep in self.tasks["P2-006"]["dependencies"]:
            if dep["target"] in interpret:
                self.assertEqual(dep["state"], "satisfied")
                self.assertIsNotNone(dep["evidence"])

    def test_post_2m_flags_and_p2_023_chain(self):
        for tid in ("P2-022", "P2-023"):
            self.assertIn("blocked_post_2m", self.tasks[tid]["flags"])
            self.assertIn("D-041", self.tasks[tid]["authority"]["label"])
            self.assertIn("P2-006", self._hard_start_targets(tid))
        self.assertIn("P2-022", self._hard_start_targets("P2-023"))

    def test_p2_016_conservatively_post_2m_at_parent(self):
        self.assertIn("blocked_post_2m", self.tasks["P2-016"]["flags"])
        self.assertEqual(self.tasks["P2-016"]["status"], "blocked")
        self.assertIn("P2-006", self._hard_start_targets("P2-016"))

    def test_p2_027_has_satisfied_repro_predecessors(self):
        self.assertEqual(self.tasks["P2-027"]["lane"], "ed_external")
        deps = {
            d["target"]: d for d in self.tasks["P2-027"]["dependencies"]
        }
        self.assertEqual(set(deps), {"REPRO-001", "REPRO-002"})
        for dep in deps.values():
            self.assertEqual(dep["state"], "satisfied")
            self.assertIsNotNone(dep["evidence"])

    def test_p1_008_is_first_external_record(self):
        external = [
            task for task in self.tasks.values() if task["lane"] == "ed_external"
        ]
        self.assertEqual(min(task["rank"] for task in external), 1)
        self.assertEqual(self.tasks["P1-008"]["rank"], 1)

    def test_quiet_mac_all_lead_only_and_smoke_first(self):
        quiet = [t for t in self.tasks.values() if t["lane"] == "quiet_mac"]
        self.assertEqual(len(quiet), 10)
        for task in quiet:
            self.assertIn("lead_only", task["flags"])
        self.assertLess(
            self.tasks["P2-015-SMOKE"]["rank"], self.tasks["P2-015"]["rank"]
        )
        self.assertEqual(self.tasks["P2-038"]["status"], "partial")

    def test_new_hardening_followups(self):
        self.assertIn("P2-038", self._hard_start_targets("P2-046B"))
        self.assertEqual(
            self._hard_start_targets("P2-047B"), {"P2-015", "P2-047A"}
        )
        for tid in ("P2-048", "CI-003", "DOC-010"):
            self.assertEqual(self.tasks[tid]["status"], "shelved")

    def test_lane_inference_flags(self):
        for tid in ("P2-004", "P2-005"):
            self.assertEqual(self.tasks[tid]["lane"], "agent")
            self.assertIn("migration_inferred_lane", self.tasks[tid]["flags"])
        self.assertIn("provisional_until_live", self.tasks["P2-005"]["flags"])

    def test_doc_008_retired(self):
        # DOC-008 completed (PR #60 merged 2026-07-11); the kernel holds only
        # live tasks, and DOC-010's trigger became an event dependency.
        self.assertNotIn("DOC-008", self.tasks)
        (dep,) = self.tasks["DOC-010"]["dependencies"]
        self.assertEqual(dep["kind"], "event")
        self.assertEqual(dep["state"], "pending")


class TestGeneratorSelfConsistency(unittest.TestCase):
    """--check against the kernel itself via generator-produced fixtures."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="gen_state_test.")
        self.addCleanup(shutil.rmtree, self.tmp)
        self.run_state = os.path.join(self.tmp, "RUN_STATE.md")
        self.queue = os.path.join(self.tmp, "TASK_QUEUE.md")
        with open(self.run_state, "w", encoding="utf-8") as fh:
            fh.write(
                "# Run State\n\nLast updated: 2026-07-09 (manual)\n\n"
                f"{gen_state.RS_BEGIN}\n{gen_state.RS_END}\n\n## Hand-authored facts\n\nkept.\n"
            )
        with open(self.queue, "w", encoding="utf-8") as fh:
            fh.write(
                "# Task Queue\n\n## Current Queue\n\n"
                f"{gen_state.Q_BEGIN}\n{gen_state.Q_END}\n\n## Completed Queue Items\n\nkept.\n"
            )
        self.paths = ["--run-state", self.run_state, "--queue", self.queue]

    def read(self, path):
        with open(path, "rb") as fh:
            return fh.read()

    def test_generate_then_check_is_clean_and_byte_stable(self):
        self.assertEqual(run_gen(*self.paths).returncode, 0)
        first_rs, first_q = self.read(self.run_state), self.read(self.queue)
        # --check: exact agreement with the kernel.
        check = run_gen("--check", *self.paths)
        self.assertEqual(check.returncode, 0, check.stderr)
        # Second generation changes no bytes.
        self.assertEqual(run_gen(*self.paths).returncode, 0)
        self.assertEqual(self.read(self.run_state), first_rs)
        self.assertEqual(self.read(self.queue), first_q)
        # Hand-authored text outside markers preserved.
        self.assertIn(b"## Hand-authored facts", first_rs)
        self.assertIn(b"## Completed Queue Items", first_q)

    def test_stdout_render_is_deterministic(self):
        a = run_gen("--stdout", "queue")
        b = run_gen("--stdout", "queue")
        self.assertEqual(a.returncode, 0, a.stderr)
        self.assertEqual(a.stdout, b.stdout)
        c = run_gen("--stdout", "run-state")
        d = run_gen("--stdout", "run-state")
        self.assertEqual(c.returncode, 0, c.stderr)
        self.assertEqual(c.stdout, d.stdout)

    def test_one_byte_drift_detected_read_only(self):
        run_gen(*self.paths)
        drifted = self.read(self.queue).replace(b"READY", b"REKDY", 1)
        with open(self.queue, "wb") as fh:
            fh.write(drifted)
        check = run_gen("--check", *self.paths)
        self.assertEqual(check.returncode, 1)
        # --check is read-only even on failure.
        self.assertEqual(self.read(self.queue), drifted)

    def test_missing_and_duplicate_markers_fatal(self):
        with open(self.queue, "w", encoding="utf-8") as fh:
            fh.write("# Task Queue\n\nno markers here\n")
        self.assertEqual(run_gen("--check", *self.paths).returncode, 2)
        with open(self.queue, "w", encoding="utf-8") as fh:
            fh.write(
                f"{gen_state.Q_BEGIN}\n{gen_state.Q_END}\n"
                f"{gen_state.Q_BEGIN}\n{gen_state.Q_END}\n"
            )
        self.assertEqual(run_gen("--check", *self.paths).returncode, 2)
        with open(self.queue, "w", encoding="utf-8") as fh:
            fh.write(f"{gen_state.Q_END}\n{gen_state.Q_BEGIN}\n")
        self.assertEqual(run_gen("--check", *self.paths).returncode, 2)

    def test_invalid_kernel_exits_2(self):
        bad = os.path.join(self.tmp, "kernel.json")
        kernel = load_kernel()
        kernel["schema_version"] = 99
        with open(bad, "wb") as fh:
            fh.write(gen_state.canonical_bytes(kernel))
        self.assertEqual(
            run_gen("--check", "--kernel", bad, *self.paths).returncode, 2
        )

    def test_non_canonical_kernel_bytes_exit_2_on_check(self):
        loose = os.path.join(self.tmp, "kernel.json")
        with open(loose, "wb") as fh:
            fh.write(gen_state.canonical_bytes(load_kernel()))
        run_gen("--kernel", loose, *self.paths)  # populate regions first
        with open(loose, "w", encoding="utf-8") as fh:
            json.dump(load_kernel(), fh)  # then de-canonicalize the bytes
        self.assertEqual(
            run_gen("--check", "--kernel", loose, *self.paths).returncode, 2
        )


if __name__ == "__main__":
    unittest.main()
