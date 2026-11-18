"""Synthetic gate evidence for the Part C cited rebind."""
from contextlib import contextmanager
from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
from types import ModuleType
import unittest
from unittest.mock import patch

from scripts import align_r1_part_c as pc

from scripts.align_r1_part_c import g1_records, gate_durations


def interval(kind, turn, seconds, outcome="released"):
    return {"kind": kind, "turn": turn, "outcome": outcome,
            "start_ns": 1_000_000_000, "end_ns": int((1 + seconds) * 1_000_000_000),
            "duration_s": seconds}


class PartCGateEvidenceTests(unittest.TestCase):
    def test_every_later_admitted_turn_needs_its_own_release(self):
        turns = [{"index": i} for i in range(3)]
        g0, g1, g2 = interval("G0", 0, 10), interval("G1", 1, 20), interval("G1", 2, 30)
        self.assertTrue(g1_records(turns, [g0, g1, g2])["pass"])
        for rows in ([g0], [g0, g1, g1, g2], [g0, g1, {**g2, "turn": 3}],
                     [g0, g1, {**g2, "outcome": "unobserved"}]):
            with self.subTest(rows=rows):
                self.assertFalse(g1_records(turns, rows)["pass"])
        self.assertTrue(g1_records(turns[:1], [g0])["pass"])

    def test_duration_reconciles_to_monotonic_bounds_before_a_total(self):
        g0, g1, hold = interval("G0", 0, 10), interval("G1", 1, 20), interval("H", 1, 30)
        self.assertEqual(gate_durations([g0, g1, hold]), {"pass": True, "errors": [], "total_s": 60})
        for wrong in (0, -1, float("nan"), float("inf"), "20", None):
            with self.subTest(duration=wrong):
                evidence = gate_durations([g0, {**g1, "duration_s": wrong}, hold])
                self.assertFalse(evidence["pass"])
                self.assertIsNone(evidence["total_s"])
        self.assertFalse(gate_durations([g0, {**g1, "end_ns": None}, hold])["pass"])


@contextmanager
def evaluator_world():
    """Supply the two W1-only imports absent on main; keep every Part C check real.

    These doubles accept only this world's clean inputs (three admitted turns,
    fresh stamps). On W1 use the actual helpers instead. Neither double decides
    whether timeout or interval evidence is acceptable.
    """
    modules = {}
    try:
        from scripts.align_r1_rehearsal import turn_check
    except ModuleNotFoundError:
        rehearsal = ModuleType("scripts.align_r1_rehearsal")

        def turn_check(count, x7, flags, minimum):
            clean = x7 is False and isinstance(flags, list) and not flags
            return count >= minimum, {"own_stop": clean, "why": ", ".join(flags or []) or None}

        rehearsal.turn_check = turn_check
        modules[rehearsal.__name__] = rehearsal
    try:
        from joulewise.align.apple.rl145_prints import stamp_fresh
    except ModuleNotFoundError:
        prints = ModuleType("joulewise.align.apple.rl145_prints")
        prints.FRESH_STAMP_S = 2.0  # RL-152 section 1.6, the existing evaluator constant.

        def stamp_fresh(age):
            return type(age) in (int, float) and -2.0 <= age <= 2.0

        prints.stamp_fresh = stamp_fresh
        modules[prints.__name__] = prints
    with patch.dict(sys.modules, modules):
        yield


def clean_facts(*, contrast=False):
    """Production fact shape: three admissions, no holds, readable flags and G0/G1."""
    status = {"os_level": 0, "pm_state": "Nominal", "pm_age_s": 0.5}
    return {
        "turns": [{"index": i, "decode_tokens": 1500,
                   "first_reading_after_start": dict(status)} for i in range(3)],
        "intervals": [{**interval(kind, i, 20), "release_status": dict(status)}
                      for i, kind in enumerate(("G0", "G1", "G1"))],
        "t_dead_s": 1000.0, "x7": False, "episode_flags": [],
        "role": "x-g" if contrast else "d-bank",
    }


STEP = {"g0_outcome": "released", "g0_wait_s": 20.0,
        "release": {"fast_c": 35.4, "slow_c": 35.4},
        "reference": {"fast_c": 35.0, "slow_c": 35.0},
        "slope_c_per_min": 0.05}


def write_receipt(directory, value):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / pc.RECEIPT_NAME).write_text(json.dumps(value), encoding="utf-8")


def synthetic_episode(role, **fields):
    identities = {
        "predecessor": ("Qwen3-30B-A3B-4bit", "shade/spam_filter_update", "benign", 1),
        "step-d": ("Qwen3.8-27B-8bit", "r1/planning_turn_step", "benign", 1),
        "d-bank": ("Qwen3.8-27B-8bit", "shade/bank_transfer_2", "benign", 1),
        "x-g": ("Qwen3-30B-A3B-4bit", "shade/spam_filter_update", "sabotage", 16),
    }
    model, task, condition, seed = identities[role]
    return {"agent_model": model, "task_pair": task, "condition": condition, "seed": seed, "flags": [], **fields}


def write_predecessor(segment, receipt=None):
    mode = {"value": 0, "source": "pmset -g custom (AC Power block, exact powermode key)",
            "observed_at": "episode_start"}
    if receipt is None:
        receipt = {"bundle": "runs/predecessor", "ac_powermode": mode, "admitted_turns": 1}
    write_receipt(segment, receipt)
    outputs = segment / receipt["bundle"] / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)
    episode = synthetic_episode("predecessor", turns=[{}], hardware={"ac_powermode": receipt["ac_powermode"]})
    (outputs / "align_episode.json").write_text(json.dumps(episode), encoding="utf-8")
    return receipt


def member_record(root, role, facts, *, save=True):
    """Build paired synthetic evidence from the facts used by the verdict tests."""
    member = deepcopy(facts)
    segment = root / pc.SEGMENTS[role]
    member.setdefault("bundle_path", str(segment / "runs/member"))
    turns = member.setdefault("turns", [])
    if turns and all("start_ns" not in turn for turn in turns):
        for gate in member.get("intervals", []):
            # Place fixture intervals on separate turn timelines.
            offset = gate["turn"] * 10_000_000_000_000
            for key in ("start_ns", "end_ns"):
                if type(gate.get(key)) is int:
                    gate[key] += offset
    for row in member.setdefault("intervals", []):
        row.setdefault("token_count", None)
        row.setdefault("exit_sample_ns", row.get("end_ns"))
        row.setdefault("release", deepcopy(STEP["release"]))
        row.setdefault("reference", deepcopy(STEP["reference"]))
        row.setdefault("slope_c_per_min", STEP["slope_c_per_min"])
    stamps = {row["exit_sample_ns"] for row in member["intervals"] if type(row["exit_sample_ns"]) is int}
    gates = {row["turn"]: row for row in member["intervals"] if row["kind"] in ("G0", "G1")}
    for i, turn in enumerate(turns):
        end = gates.get(i, {}).get("end_ns", i * 10_000_000_000_000)
        turn.setdefault("start_ns", end + 1_000_000_000)
        turn.setdefault("end_ns", turn["start_ns"] + 5_000_000_000)
        turn.setdefault("prefill_tokens", 50)
        status = turn.get("first_reading_after_start")
        if role == "d-bank" and isinstance(status, dict):
            sample = status.setdefault("sample_ns", turn["start_ns"] + 1_000_000_000)
            stamps.add(sample)
    member.setdefault("reading_stamps", sorted(stamps))
    member.setdefault("episode_flags", [])
    member.setdefault("raw_episode_flags", deepcopy(member["episode_flags"]))
    member.setdefault("thermal_flags", [])
    member.setdefault("journal_flags", [])
    member.setdefault("journal_intervals", [{k: deepcopy(v) for k, v in row.items() if k != "release_status"}
                                            for row in member["intervals"]])
    g0 = next((row for row in member["intervals"] if row["kind"] == "G0"), {})
    reference = g0.get("reference") or STEP["reference"]
    receipt = {
        "admitted_turns": len(member["turns"]), "member_status": "succeeded",
        "bundle": "runs/member", "episode_flags": deepcopy(member["episode_flags"]),
        "g0_outcome": g0.get("outcome"), "g0_wait_s": g0.get("duration_s"), "g0_timeout_s": 1200,
        "g0_reference": deepcopy(g0.get("reference")), "reference_c": reference["slow_c"],
        "reference_fast_c": reference["fast_c"], "operating_reference": {**reference, "source_member": "member"},
        "reference_source": "member", "inter_member_idle_s": 300,
        "gate_waits_s": {kind: [row["duration_s"] for row in member["intervals"] if row["kind"] == kind]
                         for kind in ("G0", "G1", "H")},
        "decode_tokens": sum(turn["decode_tokens"] for turn in member["turns"]),
        "prefill_tokens": sum(turn["prefill_tokens"] for turn in member["turns"]),
        "x7": member.get("x7"), "deadman": {"T_dead_s": member.get("t_dead_s", 1000)},
    }
    if role == "step-d":
        receipt.update(g0_released=True, g0_release=deepcopy(g0["release"]))
    receipt.update(member.get("runtime") or {})
    member["runtime"] = receipt
    if save:
        write_receipt(segment, receipt)
        (segment / "runs/member").mkdir(parents=True, exist_ok=True)
    return member


def step_record(root, step, n_chunk, *, receipt=None, save=True, budget=1000.0):
    turn = {"index": 0, "decode_tokens": 1500}
    gate = {**interval("G0", 0, step["g0_wait_s"], step["g0_outcome"]),
            **{key: step[key] for key in ("release", "reference", "slope_c_per_min")}}
    saved = {"slots": {"N_chunk": n_chunk, "B_D": 6144, "T_dead": budget}} if receipt is None else receipt
    member = member_record(root, "step-d", {"turns": [turn], "intervals": [gate], "runtime": saved}, save=save)
    return {**step, "member": member}


def evaluation_inputs(root, *, step_d=STEP, d_bank=None, x_g=None, n_chunk=4096):
    predecessor = write_predecessor(root / "capture_predecessor_30b")
    step = dict(step_d)
    if "member" not in step and all(step.get(key) is not None for key in STEP):
        wait = step["g0_wait_s"]
        if type(wait) in (int, float) and pc._finite(wait):
            step = step_record(root, step, n_chunk, budget=(d_bank or {}).get("t_dead_s", 1000.0))
    return {"predecessor": predecessor, "step_d": step,
            "d_bank": None if d_bank is None else member_record(root, "d-bank", d_bank),
            "x_g": None if x_g is None else member_record(root, "x-g", x_g),
            "n_chunk": n_chunk}


def evaluate_world(*, d_bank=None, x_g=None, step_d=STEP, **kwargs):
    with evaluator_world(), TemporaryDirectory() as tmp:
        return pc._judge_observations(
            **evaluation_inputs(Path(tmp), step_d=step_d,
                                d_bank=clean_facts() if d_bank is None else d_bank,
                                x_g=clean_facts(contrast=True) if x_g is None else x_g),
            **kwargs)


class PartCEvaluatorTimeoutTests(unittest.TestCase):
    def test_flag_only_timeout_on_next_unadmitted_turn_fails(self):
        # The workload waits for G1 before admitting the next turn. The three
        # earlier admissions and their G1s are valid; attempted turn 3 timed out,
        # but its interval row was lost. Only the episode flag records it.
        for role in ("d_bank", "x_g"):
            with self.subTest(role=role):
                facts = clean_facts(contrast=role == "x_g")
                facts["episode_flags"] = ["thermal.gate_timeout:3"]
                result = evaluate_world(**{role: facts})
                self.assertFalse(result["pass"])
                self.assertEqual(result["verdict"], "other_failure")
                check = (result["lines"][role] if role == "x_g" else
                         result["lines"]["d_bank_mechanics"]["checks"]["no_g1_timeout"])
                self.assertFalse(check["pass"])
                self.assertIn("thermal.gate_timeout:3", check["gate_timeout_flags"])

    def test_clean_three_admission_world_still_passes(self):
        result = evaluate_world()
        self.assertTrue(result["pass"], result)
        self.assertEqual(result["verdict"], "pass")
        # X_G's explicitly permitted unobserved outcome also stays permitted.
        contrast = clean_facts(contrast=True)
        contrast["intervals"][1]["outcome"] = "unobserved"
        self.assertTrue(evaluate_world(x_g=contrast)["pass"])

    def test_interval_timeout_and_absent_g1_evidence_fail(self):
        for role in ("d_bank", "x_g"):
            for damage in ("timeout", "missing"):
                with self.subTest(role=role, damage=damage):
                    facts = clean_facts(contrast=role == "x_g")
                    if damage == "timeout":
                        facts["intervals"][-1]["outcome"] = "timeout"
                    else:
                        facts["intervals"].pop()
                    result = evaluate_world(**{role: facts})
                    self.assertFalse(result["pass"])
                    check = (result["lines"][role] if role == "x_g" else
                             result["lines"]["d_bank_mechanics"]["checks"]["no_g1_timeout"])
                    self.assertFalse(check["pass"])
                    self.assertEqual(check["g1_timeout_turns"] if damage == "timeout" else
                                     check["missing_g1_turns"], [2])

    def test_bare_timeout_flag_is_not_lost(self):
        for role in ("d_bank", "x_g"):
            with self.subTest(role=role):
                facts = clean_facts(contrast=role == "x_g")
                facts["episode_flags"] = ["thermal.gate_timeout"]
                self.assertFalse(evaluate_world(**{role: facts})["pass"])


class PartCEvidenceReconciliationTests(unittest.TestCase):
    def test_failure_in_either_flag_source_or_later_interval_fails_both_roles(self):
        for role in ("d_bank", "x_g"):
            for source, flag in (("runtime", "thermal.gate_timeout:3"),
                                 ("runtime", "episode.deadman:3"),
                                 ("episode", "episode.deadman:3"),
                                 ("thermal", "thermal.gate_timeout:3"),
                                 ("interval", None)):
                with self.subTest(role=role, source=source, flag=flag):
                    facts = clean_facts(contrast=role == "x_g")
                    facts["runtime"] = {"admitted_turns": 3, "episode_flags": []}
                    if source == "interval":
                        facts["intervals"].append(interval("G1", 3, 20, outcome="deadman"))
                    elif source == "runtime":
                        facts["runtime"]["episode_flags"] = [flag]
                    else:
                        facts[f"{source}_flags"] = [flag]
                    self.assertEqual(evaluate_world(**{role: facts})["verdict"], "other_failure")

    def test_admissions_count_cannot_be_reconciled_to_truncated_turns(self):
        for role in ("d_bank", "x_g"):
            with self.subTest(role=role):
                facts = clean_facts(contrast=role == "x_g")
                facts["runtime"] = {"admitted_turns": 4, "episode_flags": []}
                self.assertEqual(evaluate_world(**{role: facts})["verdict"], "other_failure")

    def test_runtime_gate_waits_cannot_disagree_with_the_bundle(self):
        for role in ("d_bank", "x_g"):
            with self.subTest(role=role):
                facts = clean_facts(contrast=role == "x_g")
                facts["runtime"] = {"admitted_turns": 3, "g0_outcome": "released", "g0_wait_s": 20,
                                    "deadman": {"T_dead_s": 1000}, "gate_waits_s": {"G0": [20], "G1": [20, 20], "H": []}}
                self.assertTrue(evaluate_world(**{role: facts})["pass"])
                facts["runtime"]["gate_waits_s"]["G1"][1] = 30
                self.assertEqual(evaluate_world(**{role: facts})["verdict"], "other_failure")

    def test_runtime_and_bundle_duty_budgets_are_reported_and_must_match(self):
        facts = clean_facts()
        facts["runtime"] = {"admitted_turns": 3, "deadman": {"T_dead_s": 2000.0}}
        result = evaluate_world(d_bank=facts)
        self.assertEqual(result["verdict"], "other_failure")
        budget = result["lines"]["d_bank_mechanics"]["checks"]["duty_budget"]
        self.assertEqual((budget["runtime_s"], budget["bundle_s"]), (2000.0, 1000.0))

    def test_step_d_g0_interval_must_agree_with_summary_and_bounds(self):
        good = {**interval("G0", 0, 20), **{k: STEP[k] for k in ("release", "reference", "slope_c_per_min")}}
        for damage in ({"outcome": "timeout"}, {"end_ns": 1_202_000_000_000},
                       {"end_ns": 0}, {"duration_s": 19, "end_ns": 20_000_000_000}):
            with self.subTest(damage=damage), patch.object(pc, "facts_from_bundle",
                                                          return_value={"intervals": [{**good, **damage}]}):
                step = pc.step_d_facts(Path("/synthetic"), STEP)
                self.assertEqual(evaluate_world(step_d=step)["verdict"], "other_failure")
        with patch.object(pc, "facts_from_bundle", return_value={"intervals": [good]}):
            self.assertTrue(pc.step_d_line(pc.step_d_facts(Path("/synthetic"), STEP))["pass"])

    def test_step_d_requires_finite_nonnegative_wait_and_finite_release_facts(self):
        cases = ({"g0_wait_s": -1}, {"g0_wait_s": float("nan")}, {"g0_wait_s": True},
                 {"reference": {"fast_c": float("inf"), "slow_c": 35.0}},
                 {"slope_c_per_min": float("nan")})
        for damage in cases:
            with self.subTest(damage=damage):
                self.assertEqual(evaluate_world(step_d={**STEP, **damage})["verdict"], "other_failure")

    def test_reused_start_time_cannot_hide_a_hot_turn(self):
        with TemporaryDirectory() as tmp, evaluator_world():
            root = Path(tmp)
            inputs = evaluation_inputs(root, d_bank=clean_facts(), x_g=clean_facts(contrast=True))
            turns = inputs["d_bank"]["turns"]
            turns[2]["first_reading_after_start"]["os_level"] = 2
            self.assertEqual(pc._judge_observations(**inputs)["verdict"], "start_state_failed")
            # Reproject the benign sample which the changed start would select.
            turns[2]["start_ns"] = turns[1]["start_ns"]
            turns[2]["first_reading_after_start"] = deepcopy(turns[1]["first_reading_after_start"])
            result = pc._judge_observations(**inputs)
            self.assertEqual(result["verdict"], "other_failure")
            self.assertIn("overlaps", result["evidence_failures"]["d_bank"])

    def test_admission_gate_must_finish_before_its_turn(self):
        with TemporaryDirectory() as tmp, evaluator_world():
            inputs = evaluation_inputs(Path(tmp), d_bank=clean_facts(), x_g=clean_facts(contrast=True))
            bank = inputs["d_bank"]
            turn = bank["turns"][2]
            turn["start_ns"] = bank["intervals"][2]["end_ns"] - 1
            turn["first_reading_after_start"]["sample_ns"] = bank["intervals"][2]["exit_sample_ns"]
            result = pc._judge_observations(**inputs)
            self.assertEqual(result["verdict"], "other_failure")
            self.assertIn("ends after turn 2 starts", result["evidence_failures"]["d_bank"])

    def test_receipt_pair_cannot_supply_a_missing_or_corrupt_predecessor_episode(self):
        for damage in ("missing", "truncated", "bundle"):
            with self.subTest(damage=damage), TemporaryDirectory() as tmp, evaluator_world():
                root = Path(tmp)
                inputs = evaluation_inputs(root, d_bank=clean_facts(), x_g=clean_facts(contrast=True))
                bundle = root / "capture_predecessor_30b" / inputs["predecessor"]["bundle"]
                episode = bundle / "outputs/align_episode.json"
                if damage == "missing":
                    episode.unlink()
                elif damage == "truncated":
                    episode.write_text("{")
                else:
                    shutil.rmtree(bundle)
                result = pc._judge_observations(**inputs)
                self.assertEqual(result["verdict"], "other_failure")
                self.assertIn("predecessor_episode", result["evidence_failures"]["predecessor_receipt"])

    def test_matching_receipts_cannot_override_independent_evidence(self):
        for role, field, value, reason in (
            ("step-d", "T_dead", None, "step_configuration"),
            ("step-d", "g0_release", {"fast_c": 38, "slow_c": 38}, "Step-D receipt release"),
            ("d-bank", "reference_source", "different source", "reference_source"),
            ("d-bank", "inter_member_idle_s", None, "inter_member_schedule"),
            ("d-bank", "decode_tokens", 4501, "decode_tokens"),
        ):
            with self.subTest(field=field), TemporaryDirectory() as tmp, evaluator_world():
                root = Path(tmp)
                inputs = evaluation_inputs(root, d_bank=clean_facts(), x_g=clean_facts(contrast=True))
                if role == "step-d":
                    receipt = inputs["step_d"]["member"]["runtime"]
                else:
                    receipt = inputs["d_bank"]["runtime"]
                if field == "T_dead":
                    del receipt["slots"][field]
                else:
                    receipt[field] = value
                write_receipt(root / pc.SEGMENTS[role], receipt)
                result = pc._judge_observations(**inputs)
                self.assertEqual(result["verdict"], "other_failure")
                self.assertIn(reason, " ".join(result["evidence_failures"].values()))


class PartCRawBoundaryTests(unittest.TestCase):
    def test_raw_episode_identity_and_presence_mutations(self):
        count = 0
        for role in ("predecessor", "step-d", "d-bank", "x-g"):
            control = synthetic_episode(role)
            self.assertEqual(pc._episode_payload(json.dumps(control), role), control)
            for field, value in control.items():
                mutations = [
                    json.dumps({k: v for k, v in control.items() if k != field}),
                    json.dumps({**control, field: None}),
                    json.dumps({**control, field: True}),
                    "{" + json.dumps(field) + ':null,' + json.dumps(control)[1:],
                ]
                # A valid cut is retained by parsing and judged later.
                if field != "flags":
                    changed = value + 1 if type(value) is int else "other"
                    mutations.append(json.dumps({**control, field: changed}))
                for mutated in mutations:
                    with self.subTest(role=role, field=field, wire=mutated):
                        with self.assertRaises(ValueError):
                            pc._episode_payload(mutated, role)
                        count += 1
        self.assertEqual(count, 96)
        print(f"Part C raw episode field mutations rejected: {count}")

    def test_strict_json_rejects_utf8_overflow_nested_duplicates_and_trailing_records(self):
        for wire in (b'{"x":"\xff"}', b'{"n":1e1000}', b'{"x":{"flags":[1],"flags":[]}}', b'{}{}', b'{'):
            with self.subTest(wire=wire), self.assertRaises(ValueError):
                pc.parse_evidence_json(wire)


def evidence_paths(value, prefix=()):
    """Visit every child, including whole rows and empty containers."""
    children = value.items() if isinstance(value, dict) else enumerate(value) if isinstance(value, list) else ()
    for key, child in children:
        at = (*prefix, key)
        yield at, child
        yield from evidence_paths(child, at)


def change_evidence(original, path, *replacement):
    value = deepcopy(original)
    parent = value
    for key in path[:-1]:
        parent = parent[key]
    if replacement:
        parent[path[-1]] = replacement[0]
    else:
        del parent[path[-1]]
    return value


class PartCMutationTests(unittest.TestCase):
    def test_no_single_evidence_mutation_can_pass(self):
        bank = clean_facts()
        contrast = clean_facts(contrast=True)
        for member in (bank, contrast):
            for i, row in enumerate(member["intervals"]):
                offset = i * 100_000_000_000
                row["start_ns"] += offset
                row["end_ns"] += offset
                row["release_status"]["pm_age_s"] = 2.0
            for turn in member["turns"]:
                turn["first_reading_after_start"]["pm_age_s"] = 2.0
        mutations = 0
        with TemporaryDirectory() as tmp, evaluator_world():
            root = Path(tmp)
            control = evaluation_inputs(root, d_bank=bank, x_g=contrast)
            self.assertTrue(pc._judge_observations(**control)["pass"])

            def rejected(label, inputs=control):
                nonlocal mutations
                mutations += 1
                with self.subTest(mutation=label):
                    result = pc._judge_observations(**inputs)
                    self.assertFalse(result["pass"], result)
                    self.assertIn(result["verdict"], ("other_failure", "start_state_failed",
                                                      "mechanics_gate_time_failed"))

            for segment in ("capture_predecessor_30b", *pc.SEGMENTS.values()):
                path = root / segment / pc.RECEIPT_NAME
                original = path.read_text(encoding="utf-8")
                saved = json.loads(original)
                path.unlink()
                rejected(("delete receipt", segment))
                path.write_text("{", encoding="utf-8")
                rejected(("truncate receipt", segment))
                for at, value in evidence_paths(saved):
                    path.write_text(json.dumps(change_evidence(saved, at)), encoding="utf-8")
                    rejected(("delete receipt field", segment, at))
                    if type(value) in (int, float):
                        path.write_text(json.dumps(change_evidence(saved, at, value + 1)), encoding="utf-8")
                        rejected(("perturb receipt field", segment, at))
                path.write_text(original, encoding="utf-8")

            fields = {"step_d": ("g0_outcome", "g0_wait_s", "release", "reference", "slope_c_per_min"),
                      "d_bank": ("x7", "t_dead_s"), "x_g": ("x7",)}
            member_fields = ("runtime", "bundle_path", "episode_flags", "raw_episode_flags", "thermal_flags", "journal_flags",
                             "reading_stamps", "turns", "intervals", "journal_intervals")
            for key in control:
                rejected(("delete evaluator input", key), change_evidence(control, (key,)))
            rejected(("perturb configured chunk",), change_evidence(control, ("n_chunk",), 4097))
            for role, role_fields in fields.items():
                member_at = (role, "member") if role == "step_d" else (role,)
                member = control["step_d"]["member"] if role == "step_d" else control[role]
                paths = list(evidence_paths({key: control[role][key] for key in role_fields}, (role,)))
                paths.extend(evidence_paths({key: member[key] for key in member_fields}, member_at))
                for at, value in paths:
                    # Release and dispatch status decide D_bank only.
                    if ("first_reading_after_start" in at or "release_status" in at) and role != "d_bank":
                        continue
                    rejected(("delete evidence", at), change_evidence(control, at))
                    # A one-unit change of an unpaired turn timestamp can still
                    # satisfy the timing rule. Its presence is checked above.
                    if type(value) in (int, float) and not ("turns" in at and at[-1] in ("start_ns", "end_ns")):
                        rejected(("perturb evidence", at), change_evidence(control, at, value + 1))
                for source in ("episode_flags", "raw_episode_flags", "thermal_flags", "journal_flags"):
                    at = (*member_at, source)
                    rejected(("insert cut flag", at), change_evidence(control, at, ["episode.time_guard:3"]))
            self.assertTrue(pc._judge_observations(**control)["pass"])
        print(f"Part C evidence mutations rejected: {mutations}")


class PartCPublicVerdictTests(unittest.TestCase):
    def test_passing_observations_cannot_bypass_native_binding(self):
        with TemporaryDirectory() as tmp, evaluator_world():
            observations = evaluation_inputs(Path(tmp), d_bank=clean_facts(), x_g=clean_facts(contrast=True))
            self.assertIs(pc._judge_observations(**observations)["pass"], True)
            verdict = pc.evaluate(**observations)
        self.assertEqual((verdict["pass"], verdict["verdict"]), (False, "other_failure"))
        self.assertEqual(verdict["evidence_failures"], {"evidence_unverifiable": "evidence_unverifiable"})
