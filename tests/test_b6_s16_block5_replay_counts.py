"""S-16 Block 5 replay counts (scripts/b6_s16_block5_replay_counts.py) on synthetic flag fixtures."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "b6_s16_block5_replay_counts", ROOT / "scripts" / "b6_s16_block5_replay_counts.py")
s16 = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
sys.modules[_SPEC.name] = s16
_SPEC.loader.exec_module(s16)

PLANS = {
    "alpha": "v5-b5-alpha-a1-20261009T2312Z",
    "beta": "v5-b5-beta-a6-20261011T2011Z",
    "gamma": "v5-b5-gamma-a1-20261012T0420Z",
}
KEPT_MEMBER = ("member.admission_aborted", "member.span_unknown", "member.target_phase_precheck_failed")
DISCLOSED = ("calibration.refit_cache_miss", "neg8.reference_lost", "neg8.midpoint_lost", "clock.arm_unmeasured",
             "whole_window.not_passed")


def catalogs() -> tuple[dict, dict]:
    """Minimal Block 5 and Block 6 catalogs consistent with the script's rule list."""
    b5: dict[str, dict] = {}
    b6: dict[str, dict] = {}
    for rule in s16.RULES:
        for code in rule.codes:
            if rule.b5_effect:
                b5[code] = {"effect": rule.b5_effect}
            if rule.b6_effect:
                b6[code] = {"effect": rule.b6_effect}
        for code in rule.counterparts:
            b5.setdefault(code, {"effect": "EXCLUDE_WINDOW"})
            b6.setdefault(code, {"effect": "DISCLOSE"})
    for code in KEPT_MEMBER:
        b5[code] = b6[code] = {"effect": "EXCLUDE_MEMBER"}
    for code in ("cell.below_minimum",):
        b5[code] = b6[code] = {"effect": "EXCLUDE_WINDOW"}
    for code in DISCLOSED:
        b5[code] = b6[code] = {"effect": "DISCLOSE"}
    return b5, b6


def flag(plan_id: str, code: str, *, run_id: str | None = None, observed: dict | None = None) -> dict:
    return {"code": code, "observed": observed,
            "scope": {"level": "member" if run_id else "window", "plan_id": plan_id, "run_id": run_id}}


class Fixture:
    def __init__(self, tmp: Path) -> None:
        self.tmp = tmp
        self.b5, self.b6 = catalogs()

    def write_catalogs(self) -> tuple[Path, Path]:
        p5, p6 = self.tmp / "b5.json", self.tmp / "b6.json"
        p5.write_text(json.dumps({"codes": self.b5}))
        p6.write_text(json.dumps({"codes": self.b6}))
        return p5, p6

    def session(self, pack: str, flags: list[dict], *, n_science: int = 8, n_aux: int = 2,
                members_excluded: int | None = None, claim_usable: bool = True) -> Path:
        plan_id = PLANS[pack]
        root = self.tmp / f"harvest-{plan_id}"
        (root / "derived").mkdir(parents=True)
        members = ([{"kind": "science", "run_id": f"s{i}"} for i in range(n_science)]
                   + [{"kind": "auxiliary", "run_id": f"x{i}"} for i in range(n_aux)])
        (root / "derived/roster.json").write_text(json.dumps({"plan_id": plan_id, "members": members}))
        (root / "derived/flags.jsonl").write_text("".join(json.dumps(f) + "\n" for f in flags))
        if members_excluded is None:
            runs = {f["scope"]["run_id"] for f in flags
                    if f["scope"]["run_id"] and self.b5.get(f["code"], {}).get("effect") == "EXCLUDE_MEMBER"}
            members_excluded = len(runs)
        (root / "derived/exclusions.json").write_text(json.dumps(
            {"claim_usable": claim_usable, "members_excluded": [{}] * members_excluded}))
        return root

    def standard(self) -> list[Path]:
        a, b, g = PLANS["alpha"], PLANS["beta"], PLANS["gamma"]
        return [
            self.session("alpha", [
                flag(a, "contention.request_overlap", run_id="s1"),
                flag(a, "contention.request_overlap", run_id="x0"),
                flag(a, "member.admission_aborted", run_id="s2"),
                flag(a, "calibration.refit_cache_miss", run_id="s3"),
            ]),
            self.session("beta", [
                flag(b, "contention.request_overlap", run_id="s4"),
                flag(b, "member.admission_aborted", run_id="s5"),
                flag(b, "whole_window.not_passed"),
            ]),
            self.session("gamma", [
                flag(g, "neg8.reference_lost", observed={
                    "planned_reference_counts": {"start": 3, "midpoint": 1, "end": 3},
                    "reference_counts": {"start": 2, "midpoint": 1, "end": 3}}),
            ], n_science=6),
        ]


def run_replay(fx: Fixture, roots: list[Path]) -> dict:
    sessions = [s16.load_session(r) for r in roots]
    return s16.replay(sessions, fx.b5, fx.b6)


class ReplayCounts(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.fx = Fixture(Path(self._tmp.name))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def rows(self, result: dict) -> dict:
        return {r["rule_id"]: r for r in result["rules"]}

    def test_contention_becomes_a_flag_and_its_runs_are_kept(self) -> None:
        result = run_replay(self.fx, self.fx.standard())
        con = self.rows(result)["8.3.3-CON"]
        self.assertEqual(con["runs_removed"], 0)
        self.assertEqual(con["runs_flagged"], 3)
        self.assertEqual(con["runs_flagged_by_pack"], {"alpha": 2, "beta": 1, "gamma": 0})
        self.assertEqual(con["runs_flagged_science"], 2)
        self.assertEqual(con["b5_runs_removed"], 3)
        self.assertEqual(con["sessions_removed"], 0)

    def test_summary_keeps_only_runs_with_no_kept_excluding_code(self) -> None:
        result = run_replay(self.fx, self.fx.standard())
        tot = result["summary_totals"]
        self.assertEqual(tot["runs"], 10 + 10 + 8)
        self.assertEqual(tot["science_runs"], 8 + 8 + 6)
        self.assertEqual(tot["b5_runs_removed"], 5)          # s1, x0, s2 (alpha); s4, s5 (beta)
        self.assertEqual(tot["b6_catalog_runs_removed"], 2)  # s2, s5 by member.admission_aborted
        self.assertEqual(tot["kept_by_block6_changes"], 3)   # s1, x0, s4
        self.assertEqual(tot["kept_by_block6_changes_science"], 2)
        self.assertEqual(tot["runs_with_changed_run_code"], 3)
        self.assertEqual(tot["b6_catalog_sessions_removed"], 0)

    def test_row_states_and_no_count_outside_counted_or_derived(self) -> None:
        result = run_replay(self.fx, self.fx.standard())
        self.assertEqual(result["open"], ["8.3.3-PST"])
        by_state = result["rows_by_state"]
        self.assertEqual(by_state["derived"], ["8.2-P3", "8.6-S7"])
        self.assertEqual(by_state["no_replay_owed"],
                         ["8.2-N1", "8.2-N2", "8.2-W1", "8.2-W2", "8.2-W3", "8.2-D1", "8.2-S1", "8.2-PRE"])
        self.assertEqual(by_state["no_block5_input"], ["8.3.2-SLP", "8.3.2-AGT", "8.3.2-SKP"])
        self.assertEqual(by_state["not_counted_alternative"], ["8.3.3-CONALT"])
        rows = self.rows(result)
        for rule_id in by_state["no_replay_owed"] + by_state["no_block5_input"] + ["8.3.3-CONALT", "8.3.3-PST"]:
            self.assertNotIn("runs_removed", rows[rule_id])
            self.assertNotIn("sessions_removed", rows[rule_id])
            self.assertTrue(rows[rule_id]["reason"])
        md = s16.render_markdown(result, commit="abc", date="2026-11-13")
        self.assertIn("| OPEN | OPEN |", md)
        self.assertIn("| no replay owed | no replay owed |", md)
        self.assertIn("| no Block 5 input | no Block 5 input |", md)
        self.assertIn("| not counted (alternative) | not counted (alternative) |", md)
        self.assertNotIn("not evaluated", md)
        self.assertNotIn("bracket-binding", md + json.dumps(result))

    def test_bop_stop_is_derived_for_alpha_and_gamma_only(self) -> None:
        result = run_replay(self.fx, self.fx.standard())
        p3 = self.rows(result)["8.2-P3"]
        self.assertEqual(p3["state"], "derived")
        self.assertEqual(p3["sessions_removed_by_pack"], {"alpha": 0, "beta": None, "gamma": 0})
        self.assertEqual(p3["sessions_with_line"], 2)
        md = s16.render_markdown(result, commit="abc", date="2026-11-13")
        self.assertIn("| 0 (0, -, 0) | 0 (0, -, 0) (derived) |", md)

    def test_more_codes_count_is_computed(self) -> None:
        result = run_replay(self.fx, self.fx.standard())
        row = self.rows(result)["8.3.2-AGT"]
        row["codes"] = [f"agent.c{i}" for i in range(6)]
        md = s16.render_markdown(result, commit="abc", date="2026-11-13")
        self.assertIn("`agent.c3` and 2 more", md)
        self.assertIn("and 21 more", md)   # the 25 session codes

    def test_counterpart_counts_are_reported_beside_not_evaluated_rules(self) -> None:
        result = run_replay(self.fx, self.fx.standard())
        skp = self.rows(result)["8.3.2-SKP"]
        self.assertEqual(skp["b5_counterpart"]["runs"], {"alpha": 1, "beta": 1, "gamma": 0})
        self.assertEqual(skp["b5_counterpart"]["sessions_flagged"], 2)

    def test_twenty_five_session_codes_and_midpoint(self) -> None:
        result = run_replay(self.fx, self.fx.standard())
        rows = self.rows(result)
        self.assertEqual(len(rows["8.2-25"]["codes"]), 25)
        self.assertEqual(rows["8.2-25"]["sessions_removed"], 0)
        self.assertEqual(rows["8.2-MID"]["gamma_sessions"], 1)
        self.assertEqual(rows["8.2-MID"]["b5_rule_would_remove_sessions"], 0)

    def test_lost_midpoint_is_counted_from_reference_counts(self) -> None:
        roots = self.fx.standard()
        g = PLANS["gamma"]
        (roots[2] / "derived/flags.jsonl").write_text(json.dumps(flag(g, "neg8.reference_lost", observed={
            "planned_reference_counts": {"start": 3, "midpoint": 1, "end": 3},
            "reference_counts": {"start": 3, "midpoint": 0, "end": 3}})) + "\n")
        mid = self.rows(run_replay(self.fx, roots))["8.2-MID"]
        self.assertEqual(mid["b5_rule_would_remove_sessions"], 1)
        self.assertEqual(mid["sessions_removed"], 0)

    def test_clock_hold_is_not_evaluated_for_an_unmeasured_arm(self) -> None:
        roots = self.fx.standard()
        b = PLANS["beta"]
        with (roots[1] / "derived/flags.jsonl").open("a") as fh:
            fh.write(json.dumps(flag(b, "clock.arm_unmeasured")) + "\n")
        hold = self.rows(run_replay(self.fx, roots))["8.6-S7"]
        self.assertEqual(hold["state"], "derived")
        self.assertEqual(hold["sessions_not_derived"], ["beta"])
        self.assertIsNone(hold["sessions_removed_by_pack"]["beta"])
        self.assertEqual(hold["sessions_removed_by_pack"]["alpha"], 0)

    def test_section17_line(self) -> None:
        result = run_replay(self.fx, self.fx.standard())
        result["catalog_sha256"] = {"b5": "5d77c725d4bf", "b6": "b5bce6c64bbc"}
        line = s16.section17_line(result, commit="deadbeef1", date="2026-11-13")
        self.assertTrue(line.startswith("- 2026-11-13, §17-S16 (RL-134 item 17, RL-140). **Kind.** Slot fill: "
                                        "S-16, Block 5's half, in part. Read after the Block 5 release"))
        self.assertIn("@ `deadbeef1`, under Block 5's catalog `5d77c725…` and Block 6's `b5bce6c6…`", line)
        self.assertIn("28 runs: 22 science, 6 auxiliary", line)
        self.assertIn("only `contention.request_overlap` fired in Block 5: 3 runs (2, 1, 0; 2 science). Block 5 "
                      "removed all 3, and none carries a code that still removes it.", line)
        self.assertIn("Block 6's catalog removes 2 runs (1, 1, 0) where Block 5 removed 5 (3, 2, 0).", line)
        self.assertIn("The b_op stop (139 ms, ALPHA and GAMMA; §8.2 P3) stops 0 of 2:", line)
        self.assertIn("aborted 2 runs (1, 1, 0) at admission instead", line)
        self.assertIn("needs each run's idle-baseline rails: `OPEN[S-16: P*]`.", line)
        self.assertNotIn("Where evaluated", line)

    def test_section17_line_with_pstar(self) -> None:
        result = run_replay(self.fx, self.fx.standard())
        line = s16.section17_line(result, commit="c1", date="2026-11-13", pstar={
            "tool": "scripts/x.py", "commit": "c2", "removed": 0, "removed_by_pack": {"alpha": 0, "beta": 0,
                                                                                    "gamma": 0},
            "max_baseline_mw": "1.23", "lowest_line_w": "0.24"})
        self.assertIn("Block 5's half. Read after", line)
        self.assertIn("(d) The desk exclusion at P* (§8.3 item 3, S-9), replayed on each run's idle-baseline rails by "
                      "`scripts/x.py` @ `c2`: removes 0 of 28 runs (0, 0, 0); largest baseline mean 1.23 mW against "
                      "the lowest line 0.24 W.", line)
        self.assertNotIn("OPEN[S-16", line)

    def test_line_refuses_when_another_changed_run_code_fired(self) -> None:
        roots = self.fx.standard()
        with (roots[0] / "derived/flags.jsonl").open("a") as fh:
            fh.write(json.dumps(flag(PLANS["alpha"], "member.cooldown_cap_hit", run_id="s6")) + "\n")
        (roots[0] / "derived/exclusions.json").write_text(json.dumps(
            {"claim_usable": True, "members_excluded": [{}] * 4}))
        result = run_replay(self.fx, roots)
        with self.assertRaisesRegex(s16.Refusal, "line_premise: the changed run codes that fired"):
            s16.section17_line(result, commit="c", date="2026-11-13")


class Refusals(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.fx = Fixture(Path(self._tmp.name))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_b5_exclusion_count_must_match_exclusions_json(self) -> None:
        roots = self.fx.standard()
        excl = roots[0] / "derived/exclusions.json"
        excl.write_text(json.dumps({"claim_usable": True, "members_excluded": [{}]}))
        with self.assertRaisesRegex(s16.Refusal, "b5_member_exclusion_count_differs"):
            run_replay(self.fx, roots)

    def test_uncovered_catalog_change_refuses(self) -> None:
        self.fx.b6["thermal.new_member_rule"] = {"effect": "EXCLUDE_MEMBER"}
        with self.assertRaisesRegex(s16.Refusal, "catalog_change_not_covered_by_a_rule: thermal.new_member_rule"):
            run_replay(self.fx, self.fx.standard())

    def test_effect_changed_but_not_listed_refuses(self) -> None:
        self.fx.b6["member.span_unknown"] = {"effect": "DISCLOSE"}
        with self.assertRaisesRegex(s16.Refusal, "member.span_unknown"):
            run_replay(self.fx, self.fx.standard())

    def test_no_emitter_rule_with_a_block5_code_refuses(self) -> None:
        self.fx.b5["sleep.in_run"] = {"effect": "DISCLOSE"}
        with self.assertRaisesRegex(s16.Refusal, "rule_marked_no_emitter_but_b5_has_code"):
            run_replay(self.fx, self.fx.standard())

    def test_session_not_claim_usable_refuses(self) -> None:
        roots = self.fx.standard()
        (roots[2] / "derived/exclusions.json").write_text(json.dumps({"claim_usable": False,
                                                                      "members_excluded": []}))
        with self.assertRaisesRegex(s16.Refusal, "session_not_claim_usable"):
            run_replay(self.fx, roots)

    def test_usable_session_with_a_window_exclusion_refuses(self) -> None:
        roots = self.fx.standard()
        with (roots[2] / "derived/flags.jsonl").open("a") as fh:
            fh.write(json.dumps(flag(PLANS["gamma"], "neg8.screen_failed")) + "\n")
        with self.assertRaisesRegex(s16.Refusal, "usable_session_carries_b5_window_exclusion"):
            run_replay(self.fx, roots)

    def test_flag_for_a_run_outside_the_roster_refuses(self) -> None:
        roots = self.fx.standard()
        with (roots[0] / "derived/flags.jsonl").open("a") as fh:
            fh.write(json.dumps(flag(PLANS["alpha"], "calibration.refit_cache_miss", run_id="ghost")) + "\n")
        with self.assertRaisesRegex(s16.Refusal, "flag_run_not_in_roster"):
            run_replay(self.fx, roots)

    def test_unknown_block5_code_refuses(self) -> None:
        roots = self.fx.standard()
        with (roots[0] / "derived/flags.jsonl").open("a") as fh:
            fh.write(json.dumps(flag(PLANS["alpha"], "mystery.code", run_id="s5")) + "\n")
        with self.assertRaisesRegex(s16.Refusal, "b5_flag_code_not_in_b5_catalog"):
            run_replay(self.fx, roots)


class Cli(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.fx = Fixture(self.tmp)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def argv(self) -> list[str]:
        p5, p6 = self.fx.write_catalogs()
        argv = ["--b5-catalog", str(p5), "--b6-catalog", str(p6), "--date", "2026-11-13", "--commit", "c0ffee000",
                "--json-out", str(self.tmp / "out.json"), "--md-out", str(self.tmp / "out.md")]
        for root in self.fx.standard():
            argv += ["--session", str(root)]
        return argv

    def test_pinned_mode_refuses_synthetic_inputs(self) -> None:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = s16.main(self.argv())
        self.assertEqual(code, 4)
        self.assertIn("b5_catalog_digest_mismatch", err.getvalue())

    def test_unpinned_run_writes_table_and_line(self) -> None:
        self.assertEqual(s16.main(self.argv() + ["--unpinned"]), 0)
        out = json.loads((self.tmp / "out.json").read_text())
        self.assertEqual(out["schema"], s16.SCHEMA)
        self.assertFalse(out["pinned"])
        self.assertEqual([s["pack"] for s in out["sessions"]], ["alpha", "beta", "gamma"])
        md = (self.tmp / "out.md").read_text()
        self.assertIn("| Rule | Change | Block 6 effect | Runs removed (of 28; 22 science)", md)
        self.assertIn("## The §17 line (kind: slot fill)", md)
        self.assertIn("@ `c0ffee000`", md)

    def test_contention_run_with_a_kept_excluding_code_exits_4(self) -> None:
        argv = self.argv()
        alpha = self.tmp / f"harvest-{PLANS['alpha']}"
        with (alpha / "derived/flags.jsonl").open("a") as fh:
            fh.write(json.dumps(flag(PLANS["alpha"], "member.span_unknown", run_id="s1")) + "\n")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = s16.main(argv + ["--unpinned"])
        self.assertEqual(code, 4)
        self.assertIn("runs carrying a changed run code (3) differ from the runs Block 6 keeps (2)", err.getvalue())

    def test_pstar_result_closes_row_e(self) -> None:
        argv = self.argv()
        pstar = {"schema": "joulewise.b6_s16_block5_pstar.v1", "desk_sha256": s16.PSTAR_DESK_SHA256,
                 "sessions": [{"plan_id": p} for p in PLANS.values()], "runs": 28, "science_runs_examined": 22,
                 "removed": 1, "removed_by_pack": {"alpha": 0, "beta": 1, "gamma": 0},
                 "max_baseline_mean_mw_text": "80.00", "lowest_line_w_text": "0.0723"}
        (self.tmp / "pstar.json").write_text(json.dumps(pstar))
        self.assertEqual(s16.main(argv + ["--unpinned", "--pstar-json", str(self.tmp / "pstar.json"),
                                          "--pstar-commit", "p1"]), 0)
        out = json.loads((self.tmp / "out.json").read_text())
        self.assertEqual(out["open"], [])
        self.assertIn("8.3.3-PST", out["rows_by_state"]["counted"])
        line = out["section17_line"]
        self.assertIn("Slot fill: S-16, Block 5's half. Read after", line)
        self.assertIn("by `scripts/b6_s16_block5_pstar.py` @ `p1`: removes 1 of 28 runs (0, 1, 0); largest baseline "
                      "mean 80.00 mW against the lowest line 0.0723 W.", line)

    def test_pstar_result_from_another_function_refuses(self) -> None:
        argv = self.argv()
        (self.tmp / "pstar.json").write_text(json.dumps({"schema": "joulewise.b6_s16_block5_pstar.v1",
                                                         "desk_sha256": "0" * 64}))
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(s16.main(argv + ["--unpinned", "--pstar-json", str(self.tmp / "pstar.json")]), 4)
        self.assertIn("pstar_result_not_from_the_pinned_desk_function", err.getvalue())

    def test_pins_cover_the_three_released_sessions(self) -> None:
        self.assertEqual(sorted(s16.PINS["sessions"]), sorted(PLANS.values()))
        for files in s16.PINS["sessions"].values():
            self.assertEqual(sorted(files), ["derived/exclusions.json", "derived/flags.jsonl", "derived/roster.json"])


if __name__ == "__main__":
    unittest.main()
