"""Lane L9-ENV-5 (O-F1): the inverted-corner clamp is opt-in.

``AuthenticatedConsumptionSession(..., analysis_clamp=False)`` is the default
and is origin/main's session: the operative re-derivation is reduce's own, so
a dominated member whose re-derivation omits an envelope is refused exactly as
before.  Only the analysis consumers pass ``analysis_clamp=True``;
``scripts/run_campaign.py``'s collection-time whole-window verdict never does.
"""

from __future__ import annotations

import ast
import contextlib
import inspect
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import joulewise.reduce as reduce_module
import joulewise.whole_window as whole_window
from tests.test_whole_window_inverted_corner_clamp import (
    ORIGIN_MAIN_COMMIT,
    PREFILL,
    UNRECORDED,
    _bundle_fixture,
    _phase_durations,
    run_session,
    whole_window_at,
)

ROOT = Path(__file__).resolve().parents[1]
CONSTRUCTOR = "AuthenticatedConsumptionSession"
# Every analysis consumer that constructs a session, with its call count.
ANALYSIS_CONSUMERS = {
    "joulewise/floor_extraction.py": 1,
    "joulewise/analysis_engine/inputs.py": 3,
    "joulewise/b5_analysis/dry_run.py": 1,
    "joulewise/paper_reported_energy_issuer.py": 1,
    "joulewise/window_duration_margins.py": 1,
    "joulewise/floor_mint_estimator.py": 1,
    "joulewise/analysis_manifest_v3.py": 1,
    "scripts/mint_floor_artifact.py": 2,
    "scripts/check_window_provenance.py": 1,
    "scripts/produce_b5_disclosures.py": 1,
}
COLLECTION = "scripts/run_campaign.py"


def _constructor_calls(relative: str) -> list[ast.Call]:
    tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
    return [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and (getattr(node.func, "id", None) == CONSTRUCTOR or getattr(node.func, "attr", None) == CONSTRUCTOR)
    ]


def _keyword(call: ast.Call, name: str) -> ast.keyword | None:
    return next((keyword for keyword in call.keywords if keyword.arg == name), None)


class FlagOffIsOriginMainTests(unittest.TestCase):
    """(i) Flag off: origin/main's session on the permanent-widening fixture."""

    _cache: dict[str, float] = {}

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls._tmp.name)
        class_scope = SimpleNamespace(addCleanup=cls.addClassCleanup)
        cls.bundle, cls.minted, cls.minted_bound = _bundle_fixture(class_scope, cls.root / "fixture")
        span_s = cls.minted["energy_anchor_shift_envelopes"][PREFILL][
            "wall_minus_monotonic_independent_edge_span_s"]
        critical_s = _phase_durations(cls.minted)["prefill"] / 2.0 - span_s
        cls.just_under, cls.just_over = critical_s + 0.002, critical_s - 0.002

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def _run(self, name: str, bound_s: float, **kwargs):
        return run_session(
            self, self.root / name, bundle=self.bundle, minted=self.minted, minted_bound=self.minted_bound,
            operative_bound=bound_s, rederive=reduce_module._rederive_summary_for_authenticated_fiducial_bound,
            **kwargs)

    @staticmethod
    def _state(session) -> str:
        return json.dumps({
            "ready": session.ready,
            "refusal_reasons": list(session.refusal_reasons),
            "path_refusal_reasons": {
                key: sorted([list(path), list(reasons)] for path, reasons in value.items())
                for key, value in sorted(session.path_refusal_reasons.items())
            },
            "removed_member_preparation": session.removed_member_preparation,
            "operative_fiducial_bound_s": session.operative_fiducial_bound_s,
            "summaries": {key: session._summaries[key] for key in sorted(session._summaries)},
            "provenance": {key: session._provenance[key] for key in sorted(session._provenance)},
        })

    def test_default_is_off(self) -> None:
        parameter = inspect.signature(whole_window.AuthenticatedConsumptionSession).parameters["analysis_clamp"]
        self.assertIs(parameter.default, False)
        self.assertIs(parameter.kind, inspect.Parameter.KEYWORD_ONLY)
        for value in (None, 1, "yes"):
            session = whole_window.AuthenticatedConsumptionSession(
                self.root / "unused", set(), analysis_clamp=value,
                calibration_ledger_snapshot=object())
            self.assertIs(session.analysis_clamp, False)

    def test_flag_off_refuses_permanent_widening_like_origin_main(self) -> None:
        origin_main = whole_window_at(ORIGIN_MAIN_COMMIT)
        self.assertFalse(hasattr(origin_main, "_rederive_operative_summary"))
        states = {}
        for name, kwargs in (
            ("default", {}),
            ("explicit-false", {"analysis_clamp": False}),
            ("origin-main", {"module": origin_main}),
        ):
            with self.subTest(case=name):
                session = self._run("under-" + name, self.just_under, **kwargs)
                self.assertFalse(session.ready)
                self.assertEqual(session.refusal_reasons, (UNRECORDED,))
                states[name] = self._state(session)
        self.assertEqual(states["default"], states["origin-main"])
        self.assertEqual(states["explicit-false"], states["origin-main"])
        # Contrast: the analysis consumers' flag clamps and the session is ready.
        clamped = run_session(
            self, self.root / "under-on", bundle=self.bundle, minted=self.minted,
            minted_bound=self.minted_bound, operative_bound=self.just_under,
            rederive=whole_window._rederive_operative_summary, analysis_clamp=True)
        self.assertTrue(clamped.ready, clamped.refusal_reasons)
        self.assertEqual(clamped.provenance_for("member")["operative_envelopes"][PREFILL]["lower_j"], 0.0)

    def test_flag_off_ready_session_is_origin_main_bytes(self) -> None:
        current = self._run("over-default", self.just_over)
        baseline = self._run("over-origin-main", self.just_over, module=whole_window_at(ORIGIN_MAIN_COMMIT))
        self.assertTrue(current.ready, current.refusal_reasons)
        self.assertEqual(self._state(current), self._state(baseline))

    def test_flag_off_session_never_calls_the_clamp(self) -> None:
        """Unpatched re-derivation entry: the default session calls reduce's
        function object itself and never the analysis clamp."""

        with (
            mock.patch.object(whole_window, "_clamp_inverted_operative_envelopes",
                              side_effect=AssertionError("clamp reached")) as clamp,
            mock.patch.object(whole_window, "_rederive_summary_for_authenticated_fiducial_bound",
                              wraps=reduce_module._rederive_summary_for_authenticated_fiducial_bound),
        ):
            session = self._run("direct-default", self.just_under)
        self.assertEqual(session.refusal_reasons, (UNRECORDED,))
        clamp.assert_not_called()

    def test_removed_member_audit_sessions_inherit_the_flag(self) -> None:
        tree = ast.parse((ROOT / "joulewise/whole_window.py").read_text(encoding="utf-8"))
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                 and getattr(node.func, "id", None) == CONSTRUCTOR]
        self.assertEqual(len(calls), 1)
        keyword = _keyword(calls[0], "analysis_clamp")
        self.assertIsNotNone(keyword)
        self.assertEqual(ast.unparse(keyword.value), "self.analysis_clamp")


class CallSiteTests(unittest.TestCase):
    """(ii) Static: run_campaign never opts in; every analysis consumer does."""

    def test_run_campaign_never_passes_the_flag(self) -> None:
        source = (ROOT / COLLECTION).read_text(encoding="utf-8")
        self.assertNotIn("analysis_clamp", source)
        calls = _constructor_calls(COLLECTION)
        self.assertEqual(len(calls), 1)
        # No **kwargs splat could smuggle the flag in either.
        self.assertTrue(all(keyword.arg is not None for keyword in calls[0].keywords))
        self.assertIsNone(_keyword(calls[0], "analysis_clamp"))

    def test_every_analysis_consumer_passes_true(self) -> None:
        for relative, count in ANALYSIS_CONSUMERS.items():
            calls = _constructor_calls(relative)
            with self.subTest(path=relative):
                self.assertEqual(len(calls), count)
                for call in calls:
                    keyword = _keyword(call, "analysis_clamp")
                    self.assertIsNotNone(keyword, f"{relative}:{call.lineno}")
                    self.assertIsInstance(keyword.value, ast.Constant)
                    self.assertIs(keyword.value.value, True)

    def test_no_unlisted_constructor(self) -> None:
        found = set()
        for directory in ("joulewise", "scripts"):
            for path in sorted((ROOT / directory).rglob("*.py")):
                relative = path.relative_to(ROOT).as_posix()
                if CONSTRUCTOR in path.read_text(encoding="utf-8", errors="replace") and _constructor_calls(relative):
                    found.add(relative)
        self.assertEqual(found, set(ANALYSIS_CONSUMERS) | {COLLECTION, "joulewise/whole_window.py"})


class _Constructed(Exception):
    pass


def _spy(record: list):
    def construct(*args, **kwargs):
        record.append(kwargs)
        raise _Constructed

    return construct


class BlockFiveDryRunPathTests(unittest.TestCase):
    """(iii) The block-5 dry run constructs its sessions with the clamp on."""

    def test_step_4_runs_floor_extraction_through_extract_detection_floors(self) -> None:
        tree = ast.parse((ROOT / "joulewise/b5_analysis/dry_run.py").read_text(encoding="utf-8"))
        step_4 = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "step_4")
        imports = [(node.module, [alias.name for alias in node.names])
                   for node in ast.walk(step_4) if isinstance(node, ast.ImportFrom)]
        self.assertIn(("scripts.extract_detection_floors", ["main"]), imports)
        from scripts import extract_detection_floors as cli
        from joulewise import floor_extraction

        self.assertIs(cli.extract_cells, floor_extraction.extract_cells)
        source = inspect.getsource(cli.extract_indexed_pack)
        self.assertIn("return extract_cells(window.claim_runs_root, spec, kept_units=kept, archive_context=context,",
                      source)

    def test_floor_extraction_with_kept_units_opts_in(self) -> None:
        """The extract_indexed_pack shape: kept units, block-5 semantics."""

        from joulewise import floor_extraction as fe
        from tests.b5_analysis.test_floor_kept_units import arithmetic, arithmetic_seams, units_for

        base, spec = arithmetic()
        with tempfile.TemporaryDirectory(prefix="flag-") as tmp:
            root = Path(tmp) / "runs"
            shutil.copytree(base, root)
            record: list[dict] = []
            real = fe.AuthenticatedConsumptionSession
            with arithmetic_seams():
                seen: list[dict] = []

                def spy(*args, **kwargs):
                    seen.append(kwargs)
                    from tests import test_floor_extraction as old

                    return old.prepared_minted_consumption_session(*args, **kwargs)

                with mock.patch.object(fe, "AuthenticatedConsumptionSession", side_effect=spy):
                    report = fe.extract_cells(root, spec, kept_units=units_for(spec))
                record.extend(seen)
            self.assertIs(real, whole_window.AuthenticatedConsumptionSession)
        self.assertEqual(len(record), 1)
        self.assertIs(record[0]["analysis_clamp"], True)
        self.assertTrue(report["cells"])

    def test_dry_run_step_results_session_opts_in(self) -> None:
        from joulewise.b5_analysis import context as context_module, dry_run

        window = SimpleNamespace(record=SimpleNamespace(entry=SimpleNamespace(superseded_archive_roots=())),
                                 claim_runs_root=Path("/nonexistent-claim-runs"))
        state = SimpleNamespace(
            repo_root=ROOT,
            windows={"alpha": window},
            rows={"alpha": {"idle_admission_core": {}, "evaluation_basis": {"sha256": "a" * 64}}},
            contexts={"alpha": SimpleNamespace(removed_bundle_ids=frozenset())},
            archives={"alpha": object()},
            kept={"alpha": SimpleNamespace(cells={}, kept_run_ids=lambda _cid: ())},
        )
        record: list[dict] = []
        with (
            mock.patch.object(context_module, "rebuilt_roster", return_value={"members": []}),
            mock.patch.object(context_module, "survivor_set", return_value=set()),
            mock.patch.object(context_module, "_excluded", return_value={}),
            mock.patch.object(dry_run, "require_primary_context"),
            mock.patch("joulewise.analysis_engine.inputs.archive_snapshot", return_value=None),
            mock.patch.object(whole_window, CONSTRUCTOR, side_effect=_spy(record)),
            contextlib.suppress(_Constructed),
        ):
            dry_run._step_results(state)
        self.assertEqual(len(record), 1)
        self.assertIs(record[0]["analysis_clamp"], True)
        self.assertEqual(record[0]["mode"], "read_replay")


if __name__ == "__main__":
    unittest.main()
