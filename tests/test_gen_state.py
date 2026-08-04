"""DOC-008 state-kernel validity, work-selection fidelity, and drift tests."""

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import gen_state  # noqa: E402

KERNEL_PATH = os.path.join(ROOT, "docs", "process", "state_kernel.json")
SCHEMA_PATH = os.path.join(ROOT, "docs", "process", "state_kernel.schema.json")
GEN = os.path.join(ROOT, "scripts", "gen_state.py")
FIXTURE_DIR = os.path.join(ROOT, "tests", "fixtures", "state_kernel")

EXPECTED_IDS = {
    # [AGENT]
    "P2-035", "P2-036", "P3-000", "P2-022", "P2-023",
    "P2-024", "P3-001b", "P2-004", "P2-005", "P2-016",
    "P2-047A", "P2-048", "P2-050", "TOOL-01",
    "CI-003", "DOC-010",
    "DOC-008", "DOC-008-INTAKE", "DOC-008-REFLECTION", "DOC-008-STATUS",
    # audit close-out promotions (2026-07-15): deferred fix-wave orders
    "AUD-WO-033", "AUD-WO-034", "AUD-WO-035", "AUD-WO-036",
    "AUD-WO-037", "AUD-WO-038", "AUD-WO-039", "AUD-FOLLOWUPS",
    # D-078 confirmation-round-9 follow-up
    "FLOOR-BIND-01",
    # C-045 screen+budget gauntlet deferrals (2026-07-25)
    "CUSTODY-HARDEN-01",
    # 2026-07-25 attribution-limit adjudication (FLOOR-LABEL-01 completed
    # 2026-07-27 at 3055315 and left the live kernel)
    "FLOOR-WORKLOAD-SIZING-01",
    "FLOOR-COMMONMODE-01", "PHASE-SHARE-ESTIMAND-01",
    # 2026-07-29/30 mint-arc intake (82ca955; kernel rows added by ruling).
    # STACK-ID-BIND-01 completed 2026-07-30 in PR #88 (da83337).
    "MODULARITY-01",
    # 2026-07-30 cold-gate intake fold (D-088; PR #88 merge session).
    # COOLDOWN-JOIN-GAUNTLET-01 + QA-10A/QA-10B closed 2026-08-02 with
    # commit 3 (PR #93) and retired to the completed table.
    # MANIFEST-CONTRAST-01 closed 2026-08-02 (PR #95, v3 at audited head
    # e94d4a7) and retired to the completed table.
    "MINT-GENERALIZE-01",
    "SUPERSESSION-DUP-REFUSAL-01",
    # 2026-08-02 successor session: TEST-SPEED-01 minted per the
    # checkpoint resume script (Ed-ratified three levers 2026-08-03).
    "TEST-SPEED-01",
    # COOLDOWN-JOIN-DA1-01 was folded in 2026-07-31 (D-093) as P2-015
    # retired, and closed the same day inside the gauntlet's commit 2
    # (e749c95, PR #91 67d268a); it left the live kernel at close-out.
    # AXI extension agenda (D-070 + binding xhigh sequencing amendments);
    # AXI-SB-ADAPTER minted 2026-07-16 on the AXI-SB supported verdict
    "AXI-SB-ADAPTER", "AXI-SD", "AXI-SE",
    # 2026-08-01 metrology adjudication session (D-098..D-101):
    # MET-VERDICT-ADJ-01 was minted, completed the same day (D-100), and
    # left the live kernel. MET-DANGLER-DISPOSITION-01 (+ folded
    # MEMBERSHIP-READER-FAILOPEN-01) closed 2026-08-02 with PR #94
    # (audited head 05d99b6) and retired to the completed table.
    "CAL-BRACKET-D079-01",
    # 2026-08-02 D-106 clause 3 minted D100-BII-BINDING-01 (b-ii
    # capture-identity fixes); closed 2026-08-03 under D-108 (PR #99
    # merged 32d72fd + the clause-(d) three-occurrence re-record) and
    # retired to the completed table.
    # 2026-08-02 D-105 registration (C3 gauntlet close-out)
    "C3-RECOGNIZER-EXACT-01",
    # 2026-08-02 two-lens extension consult (Ed ratifies S2)
    "NVIDIA-PORTABILITY-01",
    # 2026-08-03 sleep-window: production-default custody hardening deferred
    # from NVIDIA-RETENTION-FLAKE-01 (PR #97 closed the test-side flake).
    "NODE-CUSTODY-DEFAULT-01",
    # [QUIET-MAC]
    "MET-WINDOW-C-01",
    "P2-006", "P2-010", "P2-019", "P2-020",
    "P2-012", "P2-046B", "P2-047B",
    # [ED-EXTERNAL]
    "P1-008", "P2-027", "P1-001", "P1-003", "P1-004", "P1-006",
}

TERMINAL_IDS = {"CAL-REBRACKET-01", "P2-015-PREP", "P2-029", "P2-030", "P2-031", "P2-032", "P2-034",
                "AXI-SA", "AXI-SB", "AXI-SC", "P2-038", "P2-015-SMOKE", "SITE-02", "SPLIT-AP",
                "FLOOR-LABEL-01", "STACK-ID-BIND-01", "P2-015",
                "COOLDOWN-JOIN-DA1-01", "MET-VERDICT-ADJ-01",
                "COOLDOWN-JOIN-GAUNTLET-01", "QA-10A-JOIN-OMISSION",
                "QA-10B-EXISTING-RETRY",
                "MET-DANGLER-DISPOSITION-01", "MANIFEST-CONTRAST-01",
                "MEMBERSHIP-READER-FAILOPEN-01", "NVIDIA-RETENTION-FLAKE-01"}


def load_kernel():
    with open(KERNEL_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def load_fixture(name):
    with open(os.path.join(FIXTURE_DIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def _retire_p2_015(task_ids):
    """Rewrite the frozen selection oracles' quiet-Mac head in place.

    The oracles are hand-written and frozen; P2-015 was retired from the
    kernel on 2026-07-31 and P2-006 (rank 2) inherited the quiet-Mac head.
    Patching here keeps the fixtures frozen, as the FLOOR-BIND-01 and
    P2-035 agent-head patches in the same tests already do.
    """
    for index, task_id in enumerate(task_ids):
        if task_id == "P2-015":
            task_ids[index] = "P2-006"
    return task_ids


def _retire_p2_015_in_scenarios(scenarios):
    """Apply the same P2-015 -> P2-006 head rewrite to gate allowlists."""
    for scenario in scenarios:
        _retire_p2_015(scenario["expected_selectable_task_ids"])
        for gate in scenario["active_global_gates"]:
            _retire_p2_015(gate["allowed_task_ids"])
    return scenarios


def run_gen(*args):
    return subprocess.run(
        [sys.executable, GEN, *args], capture_output=True, text=True
    )


class TestKernelValidity(unittest.TestCase):
    def test_schema_declares_v3_work_selection_authority_contract(self):
        with open(SCHEMA_PATH, encoding="utf-8") as fh:
            schema = json.load(fh)
        self.assertEqual(schema["properties"]["schema_version"]["const"], 3)
        self.assertIn("active_global_gates", schema["required"])
        self.assertEqual(
            schema["properties"]["authority"]["const"],
            gen_state.AUTHORITY_NOTICE,
        )
        gate = schema["$defs"]["globalGate"]
        self.assertEqual(gate["properties"]["scope"]["properties"]["operation"]["const"],
                         "select")
        self.assertEqual(
            set(gate["properties"]["scope"]["properties"]["lanes"]["items"]["enum"]),
            set(gen_state.LANES),
        )
        self.assertTrue(
            {"p3_hardening_candidates", "p3_tooling"}.issubset(
                schema["$defs"]["task"]["properties"]["priority"]["enum"]
            )
        )

    def test_kernel_validates(self):
        gen_state.validate(load_kernel())

    def test_kernel_bytes_are_canonical(self):
        with open(KERNEL_PATH, "rb") as fh:
            raw = fh.read()
        self.assertEqual(raw, gen_state.canonical_bytes(json.loads(raw.decode("utf-8"))))

    def test_invalid_kernels_rejected(self):
        base = load_kernel()
        # Gate-shaped mutations need a live gate; the audit gate was CLEARED
        # 2026-07-15 (Ed's adoption merge), so inject the frozen historical
        # gate artifact for mutation purposes.
        base["active_global_gates"] = copy.deepcopy(
            load_fixture("historical_audit_gate.json")["active_global_gates"])
        cases = [
            ("unknown top-level field", lambda k: k.update(surprise=1)),
            ("bad schema_version", lambda k: k.update(schema_version=1)),
            ("missing authority", lambda k: k.pop("authority")),
            ("altered authority", lambda k: k.update(authority="AUTHORITATIVE")),
            ("missing active_global_gates", lambda k: k.pop("active_global_gates")),
            ("bad gate operation",
             lambda k: k["active_global_gates"][0]["scope"].update(operation="run")),
            ("unknown gate lane",
             lambda k: k["active_global_gates"][0]["scope"]["lanes"].append("cloud")),
            ("duplicate gate id",
             lambda k: k["active_global_gates"].append(
                 copy.deepcopy(k["active_global_gates"][0]))),
            ("non-live gate allowlist ID",
             lambda k: k["active_global_gates"][0]["allowed_task_ids"].append("NOPE-1")),
            ("id/key mismatch", lambda k: k["tasks"]["P2-016"].update(id="P2-999")),
            ("terminal status", lambda k: k["tasks"]["P2-016"].update(status="done")),
            ("duplicate lane rank", lambda k: k["tasks"]["P2-016"].update(rank=0)),
            ("blocked without hard start dep", lambda k: k["tasks"]["P1-008"].update(status="blocked")),
            # P2-035's only hard start edge (P2-015) was satisfied at the
            # 2026-07-31 retirement; P2-024 now carries the pending edge these
            # dependency-shaped mutations need.
            ("queued with hard start dep", lambda k: k["tasks"]["P2-024"].update(status="queued")),
            ("dangling pending task dep",
             lambda k: k["tasks"]["P2-024"]["dependencies"][0].update(target="NOPE-1")),
            ("self-dependency",
             lambda k: k["tasks"]["P2-024"]["dependencies"][0].update(target="P2-024")),
            ("pending dep with evidence",
             lambda k: k["tasks"]["P2-024"]["dependencies"][0].update(
                 evidence={"path": "docs/decision_log.md", "label": "x"})),
            ("missing pointer target",
             lambda k: k["tasks"]["P2-016"]["authority"].update(path="docs/does_not_exist.md")),
            ("absolute pointer path",
             lambda k: k["tasks"]["P2-016"]["authority"].update(path="/etc/passwd")),
            ("pipe in goal", lambda k: k["tasks"]["P2-016"].update(goal="a | b")),
            ("unknown flag", lambda k: k["tasks"]["P2-016"].update(flags=["nope"])),
            ("quiet_mac without lead_only",
             lambda k: k["tasks"]["P2-019"].update(flags=[])),
            ("blocked_post_2m without P2-006 dep",
             lambda k: k["tasks"]["P2-022"].update(
                 dependencies=[d for d in k["tasks"]["P2-022"]["dependencies"]
                               if d["target"] != "P2-006"], status="queued")),
            ("DOC-010 missing G6 dependency",
             lambda k: k["tasks"]["DOC-010"].update(
                 dependencies=[d for d in k["tasks"]["DOC-010"]["dependencies"]
                               if d["target"] != "G6"])),
        ]
        for name, mutate in cases:
            kernel = copy.deepcopy(base)
            mutate(kernel)
            with self.assertRaises(gen_state.KernelError, msg=name):
                gen_state.validate(kernel)

    def test_cycle_rejected(self):
        # P2-024 already carries a pending hard start edge to P2-006; closing
        # the loop back from P2-006 makes a genuine cycle. Both ends are set
        # blocked so invariant 3 passes and the cycle check is what fires.
        kernel = copy.deepcopy(load_kernel())
        kernel["tasks"]["P2-006"]["dependencies"] = [
            {"kind": "task", "target": "P2-024", "required": "cycle",
             "state": "pending", "strength": "hard", "scope": "start",
             "evidence": None}
        ]
        kernel["tasks"]["P2-006"]["status"] = "blocked"
        with self.assertRaisesRegex(gen_state.KernelError, "dependency cycle"):
            gen_state.validate(kernel)


class TestRefreshedStateFidelity(unittest.TestCase):
    """Assertions against the final C-028 live-state refresh."""

    def setUp(self):
        self.kernel = load_kernel()
        self.tasks = self.kernel["tasks"]

    def test_exact_live_id_set_58(self):
        self.assertEqual(set(self.tasks), EXPECTED_IDS)
        self.assertEqual(len(self.tasks), 58)

    def test_schema_v3_work_selection_authority_notice(self):
        self.assertEqual(self.kernel["schema_version"], 3)
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

    def test_stop_card_cleared_and_audit_gate_cleared(self):
        # The comprehensive-audit gate was removed at close-out (Ed's
        # adoption merge of PR #66, 2026-07-15); gate semantics remain
        # tested against the frozen fixtures below.
        self.assertIsNone(self.kernel["active_stop_card"])
        for task in self.tasks.values():
            self.assertIsNone(task["stop_card"])
        self.assertEqual(self.kernel["active_global_gates"], [])
        selected = gen_state.selectable_task_ids(self.kernel)
        self.assertTrue({"P1-008", "P2-006"} <= selected)

    def test_axi_work_program_sequence_authority_and_window_fences(self):
        # AXI-S0 (2026-07-15), AXI-SA and AXI-SB (2026-07-16) completed and
        # left the live kernel; the Completed table owns their records.
        # AXI-SB-ADAPTER was minted on the SB supported verdict and takes
        # rank 4 with the verdict document as its authority (checked below
        # separately from the handoff-authority program rows).
        axi_ids = ("AXI-SD", "AXI-SE")
        self.assertEqual(
            {tid: self.tasks[tid]["rank"] for tid in axi_ids},
            {"AXI-SD": 6, "AXI-SE": 7},
        )
        adapter = self.tasks["AXI-SB-ADAPTER"]
        self.assertEqual(adapter["rank"], 4)
        self.assertEqual(adapter["status"], "queued")
        self.assertEqual(adapter["lane"], "agent")
        self.assertEqual(adapter["authority"]["path"],
                         "docs/specs/axi/sb_static_batch_verdict.md")
        self.assertTrue(any("Window A retains every quiet-Mac measurement slot"
                            in fence["rule"] for fence in adapter["fences"]))
        expected_authority_paths = {
            "docs/axi-handoff.md",
            "docs/decision_log.md",
            "docs/process_traces/2026-07-15-axi-xhigh-consult/response.md",
        }
        for tid in axi_ids:
            task = self.tasks[tid]
            self.assertEqual(task["lane"], "agent")
            pointer_paths = {task["authority"]["path"]}
            pointer_paths.update(fence["authority"]["path"] for fence in task["fences"])
            self.assertEqual(pointer_paths, expected_authority_paths)
            self.assertTrue(any("Window A retains every quiet-Mac measurement slot"
                                in fence["rule"] for fence in task["fences"]))

        self.assertEqual(self.tasks["AXI-SD"]["status"], "queued")
        # P2-015 retired 2026-07-31; AXI-SE's floors edge is satisfied.
        self.assertEqual(self._hard_start_targets("AXI-SE"), set())

    def _hard_start_targets(self, tid):
        return {
            d["target"] for d in self.tasks[tid]["dependencies"]
            if d["scope"] == "start" and d["strength"] == "hard"
            and d["state"] == "pending" and d["kind"] == "task"
        }

    def test_p2_015_retired_with_every_dependent_satisfied(self):
        # Retired 2026-07-31: claim-grade Window-A floors collected (a9/a10,
        # C, D), mint #1 mainline via PR #88, 7B and contrast windows passed.
        # Retirement convention is removal from the kernel, so no dependent
        # may be left holding a pending edge to it.
        self.assertNotIn("P2-015", self.tasks)
        dependents = {
            "AXI-SE", "P2-006", "P2-010", "P2-024",
            "P2-035", "P2-047A", "P2-047B",
        }
        for tid in sorted(dependents):
            dep = next(
                d for d in self.tasks[tid]["dependencies"]
                if d["target"] == "P2-015"
            )
            self.assertEqual(dep["state"], "satisfied", tid)
            self.assertIsNotNone(dep["evidence"], tid)
        for task in self.tasks.values():
            for dep in task["dependencies"]:
                if dep["target"] == "P2-015":
                    self.assertEqual(dep["state"], "satisfied", task["id"])

    def test_p2_006_gates(self):
        self.assertEqual(self._hard_start_targets("P2-006"), set())
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

    def test_quiet_mac_all_lead_only_and_p2_006_is_queued_lane_head(self):
        # P2-015 (rank 1) retired 2026-07-31; MET-WINDOW-C-01 took rank 1
        # on 2026-08-01 but sits BLOCKED behind the D-100 repair + Ed 5A,
        # so P2-006 remains the queued (selectable) lane head.
        quiet = [t for t in self.tasks.values() if t["lane"] == "quiet_mac"]
        self.assertEqual(len(quiet), 8)
        for task in quiet:
            self.assertIn("lead_only", task["flags"])
        self.assertEqual(self.tasks["MET-WINDOW-C-01"]["rank"], 1)
        self.assertEqual(self.tasks["MET-WINDOW-C-01"]["status"], "blocked")
        self.assertEqual(
            self.tasks["MET-WINDOW-C-01"]["rank"],
            min(task["rank"] for task in quiet),
        )
        queued = [t for t in quiet if t["status"] == "queued"]
        self.assertEqual(
            self.tasks["P2-006"]["rank"],
            min(task["rank"] for task in queued),
        )
        self.assertEqual(self.tasks["P2-006"]["status"], "queued")

    def test_new_hardening_followups(self):
        self.assertEqual(self._hard_start_targets("P2-046B"), set())
        p2_038_dep = next(
            dep for dep in self.tasks["P2-046B"]["dependencies"]
            if dep["target"] == "P2-038"
        )
        self.assertEqual(p2_038_dep["state"], "satisfied")
        self.assertIsNotNone(p2_038_dep["evidence"])
        self.assertEqual(
            self._hard_start_targets("P2-047B"), {"P2-047A"}
        )
        for tid in ("P2-048", "CI-003", "DOC-010"):
            self.assertEqual(self.tasks[tid]["status"], "shelved")

    def test_lane_inference_flags(self):
        for tid in ("P2-004", "P2-005"):
            self.assertEqual(self.tasks[tid]["lane"], "agent")
            self.assertIn("migration_inferred_lane", self.tasks[tid]["flags"])
        self.assertIn("provisional_until_live", self.tasks["P2-005"]["flags"])

    def test_doc_008_reopened_record_and_doc_010_two_part_fence(self):
        self.assertEqual(self.tasks["DOC-008"]["status"], "partial")
        self.assertEqual(
            {d["target"] for d in self.tasks["DOC-008"]["dependencies"]},
            {"DOC-008-INTAKE", "DOC-008-REFLECTION", "DOC-008-STATUS"},
        )
        for tid in ("DOC-008-INTAKE", "DOC-008-REFLECTION", "DOC-008-STATUS"):
            self.assertIn(tid, self.tasks)
        deps = self.tasks["DOC-010"]["dependencies"]
        self.assertEqual({d["target"] for d in deps}, {"DOC-008-proven-in-use", "G6"})
        for dep in deps:
            self.assertEqual(dep["kind"], "event")
            self.assertEqual(dep["scope"], "start")
            self.assertEqual(dep["strength"], "hard")
            self.assertEqual(dep["state"], "pending")
        with open(os.path.join(ROOT, "TASK_QUEUE.md"), encoding="utf-8") as fh:
            queue_text = fh.read()
        self.assertIn("| DOC-008 | P2 Next Slice | PARTIAL — REOPENED 2026-07-15 |",
                      queue_text)

    def _completed_queue_ids(self):
        with open(os.path.join(ROOT, "TASK_QUEUE.md"), encoding="utf-8") as fh:
            queue_text = fh.read()
        completed = queue_text.split("## Completed Queue Items", 1)[1]
        completed = completed.split("## Shelved Follow-Ups With Triggers", 1)[0]
        return {
            cells[1].strip()
            for line in completed.splitlines()
            if line.startswith("|")
            for cells in [line.split("|")]
            if len(cells) > 2 and cells[1].strip() not in ("ID", "---")
        }

    def _assert_pre_demotion_task_record_parity(self, tasks):
        snapshot = load_fixture("selection_semantics.json")[
            "pre_demotion_queue_snapshot"
        ]
        live_coverage = set(tasks)
        for source_id, successor_ids in snapshot["documented_id_migrations"].items():
            self.assertTrue(
                set(successor_ids).issubset(tasks),
                f"{source_id} migration successors missing",
            )
            live_coverage.add(source_id)
        self.assertTrue(
            set(snapshot["task_ids"]).issubset(
                live_coverage | self._completed_queue_ids()
            ),
            "pre-demotion queue task record silently lost",
        )

    def test_pre_demotion_task_record_parity(self):
        self._assert_pre_demotion_task_record_parity(self.tasks)
        # SITE-02 and SPLIT-AP completed 2026-07-16 (PRs #68/#69) and left
        # the live kernel; the parity negative check keeps the still-live
        # recovered rows.
        for task_id in ("P2-050", "TOOL-01"):
            with self.subTest(negative_removed_task_id=task_id):
                mutated = copy.deepcopy(self.tasks)
                mutated.pop(task_id)
                with self.assertRaises(AssertionError):
                    self._assert_pre_demotion_task_record_parity(mutated)

    def test_recovered_task_semantics(self):
        self.assertEqual(
            self.tasks["P2-050"]["priority"], "p3_hardening_candidates"
        )
        self.assertEqual(self.tasks["TOOL-01"]["priority"], "p3_tooling")
        self.assertEqual(
            self.tasks["TOOL-01"]["status_note"],
            "lead personal tooling, non-repo",
        )
        for task_id in ("P2-050", "TOOL-01"):
            self.assertEqual(self.tasks[task_id]["lane"], "agent")
            self.assertEqual(self.tasks[task_id]["status"], "queued")
            self.assertEqual(self.tasks[task_id]["dependencies"], [])

    def test_phase_c_has_one_generated_work_selection_region_per_surface(self):
        with open(os.path.join(ROOT, "RUN_STATE.md"), encoding="utf-8") as fh:
            run_state = fh.read()
        with open(os.path.join(ROOT, "TASK_QUEUE.md"), encoding="utf-8") as fh:
            queue = fh.read()

        self.assertEqual(run_state.count(gen_state.RS_BEGIN), 1)
        self.assertEqual(run_state.count(gen_state.RS_END), 1)
        self.assertEqual(queue.count(gen_state.Q_BEGIN), 1)
        self.assertEqual(queue.count(gen_state.Q_END), 1)

        run_outside = run_state.split(gen_state.RS_BEGIN, 1)[0]
        run_outside += run_state.split(gen_state.RS_END, 1)[1]
        queue_outside = queue.split(gen_state.Q_BEGIN, 1)[0]
        queue_outside += queue.split(gen_state.Q_END, 1)[1]

        self.assertNotIn("RESTART HERE (next session)", run_outside)
        self.assertNotIn("## What Is Next", run_outside)
        self.assertNotIn("explicitly non-authoritative", run_outside)
        self.assertIn("authoritative for work selection", run_outside)
        self.assertIn("Historical restart snapshot", run_outside)
        self.assertIn("Historical Next-Work Snapshot", run_outside)

        self.assertNotIn("SOFTWARE-READY", queue_outside)
        self.assertNotIn(
            "| Rank | ID | Priority | Status | Task | Evidence / Acceptance |",
            queue_outside,
        )
        self.assertEqual(queue_outside.count("## Current Queue"), 1)
        self.assertIn("sole live work-selection view", queue_outside)


class TestWorkSelectionFidelity(unittest.TestCase):
    """Exact selection assertions against hand-written, frozen JSON oracles."""

    def _kernel_with(self, active_global_gates):
        kernel = copy.deepcopy(load_kernel())
        kernel["active_global_gates"] = copy.deepcopy(active_global_gates)
        gen_state.validate(kernel)
        return kernel

    def _assert_oracle(self, kernel, oracle):
        self.assertSetEqual(
            gen_state.selectable_task_ids(kernel),
            set(oracle["expected_selectable_task_ids"]),
        )

    def test_frozen_historical_gate_artifact_suppresses_exactly(self):
        # The live-kernel equality pin was retired at gate clearance
        # (2026-07-15); the frozen artifact remains the migration fixture.
        oracle = load_fixture("historical_audit_gate.json")
        oracle["must_suppress_task_ids"].append("FLOOR-BIND-01")
        _retire_p2_015(oracle["must_suppress_task_ids"])
        kernel = self._kernel_with(oracle["active_global_gates"])
        self._assert_oracle(kernel, oracle)
        selected = gen_state.selectable_task_ids(kernel)
        self.assertTrue(set(oracle["must_suppress_task_ids"]).isdisjoint(selected))

    def test_run_state_suppressed_lane_heads_are_exactly_one_gated_entry_per_lane(self):
        gate_oracle = load_fixture("historical_audit_gate.json")
        head_oracle = load_fixture("cleared_audit_gate.json")
        head_oracle["expected_selectable_task_ids"][0] = "P2-035"
        _retire_p2_015(head_oracle["expected_selectable_task_ids"])
        kernel = self._kernel_with(gate_oracle["active_global_gates"])
        rendered = gen_state.render_run_state(kernel)
        gate_id = gate_oracle["active_global_gates"][0]["id"]
        expected_by_lane = {
            kernel["tasks"][task_id]["lane"]: task_id
            for task_id in head_oracle["expected_selectable_task_ids"]
        }
        self.assertEqual(set(expected_by_lane), set(gen_state.LANES))

        restart = rendered.split("## Restart By Machine-State Lane", 1)[1]
        for index, lane in enumerate(gen_state.LANES):
            section = restart.split(f"### {gen_state.LANE_LABEL[lane]}", 1)[1]
            if index + 1 < len(gen_state.LANES):
                section = section.split(
                    f"### {gen_state.LANE_LABEL[gen_state.LANES[index + 1]]}", 1
                )[0]
            entries = [line for line in section.splitlines() if line.startswith("- ")]
            self.assertEqual(len(entries), 1, lane)
            task_id = expected_by_lane[lane]
            task = kernel["tasks"][task_id]
            self.assertTrue(
                entries[0].startswith(
                    f"- GATED — {gen_state.LANE_PREFIX[lane]}{task['rank']} `{task_id}` "
                ),
                entries[0],
            )
            self.assertIn(f"(excluded by: {gate_id})", entries[0])
            self.assertNotIn("READY", entries[0])

    def test_clearing_gate_restores_exact_dependency_rank_heads(self):
        oracle = load_fixture("cleared_audit_gate.json")
        oracle["expected_selectable_task_ids"][0] = "P2-035"
        _retire_p2_015(oracle["expected_selectable_task_ids"])
        kernel = self._kernel_with(oracle["active_global_gates"])
        self._assert_oracle(kernel, oracle)

    def test_allowlist_lane_matching_and_multi_gate_intersection(self):
        fixture = load_fixture("selection_semantics.json")
        for scenario in _retire_p2_015_in_scenarios(fixture["scenarios"]):
            with self.subTest(scenario=scenario["name"]):
                kernel = self._kernel_with(scenario["active_global_gates"])
                self._assert_oracle(kernel, scenario)

    def test_stop_card_precedes_gates_and_clear_restores_still_active_gate(self):
        fixture = load_fixture("selection_semantics.json")
        lane_oracle = next(
            scenario for scenario in _retire_p2_015_in_scenarios(fixture["scenarios"])
            if scenario["name"] == "lane_matching"
        )
        kernel = self._kernel_with(lane_oracle["active_global_gates"])
        stop_fixture = fixture["stop_card_precedence"]
        card = copy.deepcopy(stop_fixture["active_stop_card"])
        # Invariant 7 needs an active/blocked stop-card holder. The fixture
        # names P2-035, which became queued when its P2-015 edge was
        # satisfied at the 2026-07-31 retirement; P2-024 is still blocked.
        stopped_task_id = stop_fixture["task_id"]
        if kernel["tasks"][stopped_task_id]["status"] not in ("active", "blocked"):
            stopped_task_id = "P2-024"
        kernel["active_stop_card"] = card
        kernel["tasks"][stopped_task_id]["stop_card"] = copy.deepcopy(card)

        with tempfile.TemporaryDirectory(prefix="state_kernel_stop_card.") as root:
            for name in os.listdir(ROOT):
                if name != "docs":
                    os.symlink(os.path.join(ROOT, name), os.path.join(root, name))
            docs = os.path.join(root, "docs")
            os.mkdir(docs)
            source_docs = os.path.join(ROOT, "docs")
            for name in os.listdir(source_docs):
                os.symlink(os.path.join(source_docs, name), os.path.join(docs, name))
            stop_cards = os.path.join(docs, "stop_cards")
            os.mkdir(stop_cards)
            with open(os.path.join(stop_cards, "fixture-active.md"), "w",
                      encoding="utf-8") as fh:
                fh.write("# Fixture Active Stop Card\n")

            with mock.patch.object(gen_state, "ROOT", root):
                gen_state.validate(kernel)
                self.assertEqual(gen_state.selectable_task_ids(kernel), set())
                stopped_queue = gen_state.render_queue(kernel)
                self.assertNotIn("| READY |", stopped_queue)
                self.assertNotIn("PARTIAL; READY", stopped_queue)
                self.assertIn("STOPPED — active stop card", stopped_queue)

                kernel["active_stop_card"] = None
                kernel["tasks"][stopped_task_id]["stop_card"] = None
                gen_state.validate(kernel)
                self._assert_oracle(kernel, lane_oracle)

    def test_priority_relabel_cannot_bypass_gate(self):
        oracle = load_fixture("historical_audit_gate.json")
        kernel = self._kernel_with(oracle["active_global_gates"])
        kernel["tasks"]["P2-004"]["priority"] = "p0_safety"
        gen_state.validate(kernel)
        self._assert_oracle(kernel, oracle)

    def test_only_both_doc_010_events_release_start(self):
        base = load_kernel()
        gate = {
            "id": "gate-fixture-doc-010",
            "summary": "Fixture gate permits DOC-010 in the agent lane.",
            "authority": ["Hand-written selection test setup"],
            "clearance": "Fixture-only clearance.",
            "scope": {"operation": "select", "lanes": ["agent"]},
            "allowed_task_ids": ["DOC-010"],
        }
        evidence = {
            "path": "docs/specs/c027/doc-008_state_kernel.md",
            "label": "DOC-008 state-kernel spec",
        }

        for only_target in ("DOC-008-proven-in-use", "G6"):
            with self.subTest(only_satisfied=only_target):
                kernel = copy.deepcopy(base)
                kernel["active_global_gates"] = [copy.deepcopy(gate)]
                task = kernel["tasks"]["DOC-010"]
                task["status"] = "blocked"
                dep = next(d for d in task["dependencies"] if d["target"] == only_target)
                dep["state"] = "satisfied"
                dep["evidence"] = copy.deepcopy(evidence)
                gen_state.validate(kernel)
                self.assertNotIn("DOC-010", gen_state.selectable_task_ids(kernel))

        kernel = copy.deepcopy(base)
        kernel["active_global_gates"] = [copy.deepcopy(gate)]
        task = kernel["tasks"]["DOC-010"]
        task["status"] = "queued"
        for dep in task["dependencies"]:
            dep["state"] = "satisfied"
            dep["evidence"] = copy.deepcopy(evidence)
        gen_state.validate(kernel)
        self.assertIn("DOC-010", gen_state.selectable_task_ids(kernel))

    def test_negative_gate_removed_and_allowlist_widened_fail_oracle(self):
        oracle = load_fixture("historical_audit_gate.json")

        removed = self._kernel_with([])
        with self.assertRaises(AssertionError):
            self._assert_oracle(removed, oracle)

        widened_gates = copy.deepcopy(oracle["active_global_gates"])
        widened_gates[0]["allowed_task_ids"] = ["P1-008"]
        widened = self._kernel_with(widened_gates)
        with self.assertRaises(AssertionError):
            self._assert_oracle(widened, oracle)

    def test_negative_doc_010_g6_drop_fails_validation(self):
        kernel = copy.deepcopy(load_kernel())
        kernel["tasks"]["DOC-010"]["dependencies"] = [
            dep for dep in kernel["tasks"]["DOC-010"]["dependencies"]
            if dep["target"] != "G6"
        ]
        with self.assertRaises(gen_state.KernelError):
            gen_state.validate(kernel)

    def test_gate_rendered_in_both_regions_and_forbidden_tasks_never_ready(self):
        gate = load_fixture("historical_audit_gate.json")["active_global_gates"]
        kernel = self._kernel_with(gate)
        run_state = gen_state.render_run_state(kernel)
        queue = gen_state.render_queue(kernel)
        for rendered in (run_state, queue):
            self.assertIn("## Active Global Work-Selection Gates", rendered)
            self.assertIn("gate-2026-07-13-comprehensive-audit", rendered)
            self.assertIn(gate[0]["clearance"], rendered)
            self.assertIn("Source of truth for work selection:", rendered)
            self.assertNotIn("Source of truth:", rendered)
        self.assertNotIn("- READY —", run_state)
        self.assertNotIn("| READY |", queue)
        self.assertNotIn("PARTIAL; READY", queue)

    def test_cleared_live_kernel_renders_no_gate_and_ready_heads(self):
        kernel = load_kernel()
        run_state = gen_state.render_run_state(kernel)
        queue = gen_state.render_queue(kernel)
        for rendered in (run_state, queue):
            self.assertIn("NONE — no global work-selection gate is active", rendered)
            self.assertNotIn("GATED —", rendered)
        self.assertIn("- READY —", run_state)


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
        drifted = self.read(self.queue).replace(b"Source of truth", b"Source of trvth", 1)
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
