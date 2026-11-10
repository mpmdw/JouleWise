"""Read-only review probes; every custody path and process table is synthetic.

Run from the repository: PYTHONNOUSERSITE=1 python3.13 -B \
  docs/run_reports/interp-energy-desk/wdv5-rev-sol-probes.py
No launch, native census, model, network, or measurement operation is performed.
"""
from __future__ import annotations

import ast
import copy
import datetime as dt
import itertools
import json
import math
from pathlib import Path
import plistlib
import subprocess
import sys
import types
from unittest import mock

REPO = Path(__file__).resolve().parents[3]
BASE = "4bd293caa421d85f2d7b46c99276b7c80201c5c0"
ARMING = "20e9edbc446a9f89a68badc1bd32bb0934cbb86d"
sys.path.insert(0, str(REPO))

from joulewise import night_gate
from joulewise.night_plan_writer import night_plan_json_bytes, night_plan_mapping
from scripts import magistrate_watchdog as wd
from scripts import run_night
from tests.fixtures.b5_plan import fake_window
from tests.test_magistrate_watchdog import TerminalWindowReleaseTests, WatchdogTestCase
from tests.test_night_plan_writer import NightPlanWriterTests
from tests.test_post_window_unstrand import PostWindowUnstrandTests
from tests.test_quiet_admission import POLICY


def git_source(ref, path):
    return subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=REPO, text=True)


def load_source(name, source):
    module = types.ModuleType(name)
    sys.modules[name] = module
    exec(compile(source, name, "exec"), module.__dict__)
    return module


def parser_probes():
    fixture = NightPlanWriterTests()
    fixture.setUp()
    try:
        pack = night_plan_mapping(fixture.plan)
        plain = {key: value for key, value in pack.items() if key != "pack_night"}
        plain.update(schema="joulewise.night_plan.v2", schema_version=2,
                     receipt_class="REHEARSAL_STUB", registration_path="synthetic-registration")
        diagnostic = {**plain, "receipt_class": "DIAGNOSTIC_NO_PACK"}
        quiet = {**plain, "schema": "joulewise.night_plan.v4", "schema_version": 4,
                 "window_max_s": 9600, "quiet_admission": POLICY}
        hazard = fake_window.hazard_plan_mapping(
            fixture.root, plan_id="review-synthetic", t0_epoch_s=1000,
            authored_epoch_s=900, custody_root=fixture.custody,
            measurement_root=fixture.root / "measurement", pack_root=fixture.root / "pack")
        seeds = [plain, diagnostic, pack, quiet,
                 {**quiet, "receipt_class": "DIAGNOSTIC_NO_PACK"}, hazard]
        storage = wd.Storage(fixture.root / "watchdog")
        directory = fixture.root / "home/Library/LaunchAgents"
        directory.mkdir(parents=True)
        path = fixture.custody / "night_plan.json"
        for label in ("com.joulewise.night", "com.joulewise.night.deadman"):
            (directory / (label + ".plist")).write_bytes(plistlib.dumps({
                "ProgramArguments": ["python", "run_night.py", "run", "--plan", str(path)]}))

        def observe(value, allowed):
            path.write_text(json.dumps(value))
            with mock.patch.object(wd.Path, "home", return_value=fixture.root / "home"), \
                    mock.patch.object(storage, "glob_plans", return_value=[path]):
                errors = []
                installed = wd._installed_agent_plans(
                    dt.datetime.fromtimestamp(2000, dt.timezone.utc), storage, errors=errors)
                discovered = wd.load_plans(storage, now_epoch_s=2000)
                if allowed:
                    parsed = night_gate.NightPlan.from_mapping(value)
                    assert errors == [] and installed == [parsed]
                    assert discovered.errors == () and discovered.plans == (parsed,)
                    assert run_night._load_plan(path) == parsed
                else:
                    try:
                        night_gate.NightPlan.from_mapping(value)
                    except night_gate.PlanError:
                        pass
                    else:
                        raise AssertionError("invalid plan accepted")
                    assert not installed and len(errors) == 2
                    assert not discovered.plans and len(discovered.errors) >= 2

        positives = negatives = 0
        for seed in seeds:
            for mode in ("ABSENT", 0, 2):
                value = copy.deepcopy(seed)
                if mode != "ABSENT":
                    value["ac_powermode"] = mode
                observe(value, True)
                positives += 1
            for mode in (None, True, False, 0.0, 2.0, 1, -1, 3, "0", "2", [], {}, float("nan")):
                observe({**seed, "ac_powermode": mode}, False)
                negatives += 1
            for changes in ({"unknown": 0}, {"schema_version": True}, {"schema_version": 5.0},
                            {"schema": "joulewise.night_plan.v1"}, {"schema": "unknown"},
                            {"ac_powermode": 0, "unknown": 1}, {"t0_epoch_s": True},
                            {"authored_epoch_s": float("nan")}, {"window_max_s": 0},
                            {"window_max_s": True}, {"window_max_s": 60.0},
                            {"repo_head": False}, {"receipt_class": []}, {"measurement_root": 0}):
                observe({**seed, **changes}, False)
                negatives += 1
            for version in (1, 2, 3, 4, 5):
                if version != seed["schema_version"]:
                    observe({**seed, "schema": f"joulewise.night_plan.v{version}",
                             "schema_version": version}, False)
                    negatives += 1
        for changes in ({"hazard_window": {}}, {"hazard_window": None},
                        {"hazard_window": {**hazard["hazard_window"], "unknown": 1}},
                        {"pack_night": pack["pack_night"]}, {"quiet_admission": POLICY},
                        {"receipt_class": "REHEARSAL_STUB"}, {"receipt_class": "TRANSACTION_PACK"}):
            observe({**hazard, "ac_powermode": 0, **changes}, False)
            negatives += 1
        # Positive identification of the retired v1 shape is discovery-only:
        # installed v1 remains an error rather than being silently ignored.
        legacy = {key: plain[key] for key in wd.RETIRED_V1_KEYS}
        legacy["schema"] = "joulewise.night_plan.v1"
        observe(legacy, False)
        negatives += 1

        # Exact arming-side parser parity, from Git objects only.
        current = ast.parse((REPO / "joulewise/night_gate.py").read_text())
        arming = ast.parse(git_source(ARMING, "joulewise/night_gate.py"))
        def function(tree, owner, name):
            body = next(node for node in tree.body if getattr(node, "name", None) == owner).body if owner else tree.body
            return ast.dump(next(node for node in body if getattr(node, "name", None) == name), include_attributes=False)
        for owner, name in (("NightPlan", "from_mapping"), (None, "_plan_ac_powermode"),
                            (None, "validate_hazard_window")):
            assert function(current, owner, name) == function(arming, owner, name), name

        # Old-parser counterfactual in memory, without replacing source files.
        old = load_source("joulewise._wdv5_review_old_gate", git_source(BASE, "joulewise/night_gate.py"))
        old_writer = load_source("joulewise._wdv5_review_old_writer", git_source(BASE, "joulewise/night_plan_writer.py"))
        old_writer.NightPlan = old.NightPlan
        for seed in seeds[:-1]:
            assert night_plan_json_bytes(night_gate.NightPlan.from_mapping(seed)) == old_writer.night_plan_json_bytes(old.NightPlan.from_mapping(seed))
        path.write_text(json.dumps({**hazard, "ac_powermode": 0}))
        with mock.patch.object(wd, "NightPlan", old.NightPlan):
            errors = []
            assert wd._installed_agent_plans(
                dt.datetime.fromtimestamp(2000, dt.timezone.utc),
                storage, launch_agents_dir=directory, errors=errors) == []
            assert len(errors) == 2 and all("ac_powermode" in error for error in errors)
        print(f"parser: {positives} accepted, {negatives} refused through installed+discovery; arming AST parity; 5 legacy byte matches; old parser rejects")
    finally:
        fixture.doCleanups()


def release_probes():
    fixture = WatchdogTestCase()
    fixture.setUp()
    try:
        now = fixture.base.timestamp()
        custody = fixture.temp / "sessions/synthetic-installed/custody"
        night = custody / "night"
        night.mkdir(parents=True)
        mapping = fake_window.hazard_plan_mapping(
            custody, plan_id="review-installed", t0_epoch_s=now - 60,
            window_max_s=29 * 3600, authored_epoch_s=now - 3600, custody_root=custody,
            measurement_root=fixture.temp / "measurement", pack_root=fixture.temp / "pack")
        mapping["ac_powermode"] = 2
        path = custody / "night_plan.json"
        path.write_text(json.dumps(mapping))
        directory = wd.Path.home() / "Library/LaunchAgents"
        directory.mkdir(parents=True)
        for label in ("com.joulewise.night", "com.joulewise.night.deadman"):
            (directory / (label + ".plist")).write_bytes(plistlib.dumps({
                "ProgramArguments": ["python", "run_night.py", "run", "--plan", str(path)]}))
        plan, = wd.load_plans(fixture.harness.storage, now_epoch_s=now).plans
        assert not list(fixture.harness.storage.glob_plans())  # installed reader only
        checks = 0
        for started, exited, delivered in itertools.product((False, True), repeat=3):
            for verdict in ("GO", "CHAIN_STOPPED", "ABORTED", "REFUSED", "MAYBE"):
                for ended in (now, math.nextafter(now, math.inf), None, True):
                    for marker in ("chain.started", "chain.exited", "courier.sent", "result.json"):
                        (night / marker).unlink(missing_ok=True)
                    result = {"plan_id": plan.plan_id, "receipt_class": "HAZARD_PACK", "verdict": verdict,
                              "ended_epoch_s": ended, "chain_exit_code": 0 if started else None,
                              "chain_sha256": "a" * 64 if started else None}
                    (night / "result.json").write_text(json.dumps(result))
                    for marker, present in (("chain.started", started), ("chain.exited", exited),
                                            ("courier.sent", delivered)):
                        if present:
                            (night / marker).touch()
                    expected = (ended is not None and type(ended) is float and ended <= now and delivered
                                and ((started and exited and verdict in {"GO", "CHAIN_STOPPED", "ABORTED", "REFUSED"})
                                     or (not started and not exited and verdict == "REFUSED")))
                    state = wd.initial_state()
                    decision = wd.decide(fixture.harness.storage, fixture.harness.deps, state)
                    released = bool(state.get(wd.TERMINAL_RELEASE_STATE_KEY))
                    assert released == expected, (started, exited, delivered, verdict, ended, decision)
                    assert decision.launch == expected
                    assert (wd.installed_agent_fence(fixture.base, fixture.harness.storage, state=state) is None) == expected
                    checks += 1
        TerminalWindowReleaseTests.write_terminal(fixture, plan, ended=now)
        for seam in ("agent", "driver", "custody", "unreadable"):
            with mock.patch.object(fixture.harness.deps, "census", return_value=wd.CensusObservation(seam != "agent", 0, "", "")), \
                    mock.patch.object(fixture.harness.deps, "driver_probe", return_value=wd.CensusObservation(seam != "driver", 0, "", "")), \
                    mock.patch.object(fixture.harness.processes, "snapshot", **(
                        {"side_effect": PermissionError("synthetic denied")} if seam == "unreadable" else
                        {"return_value": [wd.ProcessInfo(123, 1, "start", f"zsh {custody}/chain.zsh")] if seam == "custody" else []})):
                state = wd.initial_state()
                assert not wd.decide(fixture.harness.storage, fixture.harness.deps, state).launch
                assert not state.get(wd.TERMINAL_RELEASE_STATE_KEY)
        state = wd.initial_state()
        assert wd.decide(fixture.harness.storage, fixture.harness.deps, state).launch
        # One-way latch survives the newly launched agent's census match.
        fixture.harness.census = wd.CensusObservation(False, 0, "synthetic live agent", "")
        later = wd.decide(fixture.harness.storage, fixture.harness.deps, state)
        assert later.state not in {"FENCED", "HOLD_CENSUS"}
        assert not wd.plan_span_active(plan, now, fixture.harness.storage, state)
        (night / "chain.exited").unlink()
        assert wd.plan_span_active(plan, now, fixture.harness.storage, state)
        print(f"release: {checks} installed-only marker/verdict/time combinations match the existing rules; 4 process holds; latch and open-chain checks")
    finally:
        fixture.tearDown()
        fixture.doCleanups()


def recovery_probes():
    fixture = PostWindowUnstrandTests()
    fixture.setUp()
    try:
        ps = fixture.bin / "ps"
        cases = (
            ('#!/bin/sh\necho "1 launchd"\necho denied >&2\nexit 0\n', "stderr despite zero status"),
            ('#!/bin/sh\nprintf "1 launchd\\n4242\\n"\n', "partial malformed row"),
            ('#!/bin/sh\nprintf "x launchd\\n"\n', "nonnumeric pid"),
            ('#!/bin/sh\nexit 127\n', "unavailable ps"),
        )
        for source, label in cases:
            ps.write_text(source)
            result = fixture.run_script("--go")
            assert result.returncode != 0 and not fixture.log.exists(), label
            fixture.assert_blinded(result)
        # Directories cannot be opened as records; the default still succeeds
        # and performs no launchctl calls. Includes a secret malformed event.
        ps.write_text('#!/bin/sh\nprintf "1 launchd\\n"\n')
        for marker in ("chain.exited", "courier.sent", "result.json"):
            path = fixture.night / marker
            path.unlink()
            path.mkdir()
        before = {p: p.read_bytes() for p in fixture.directory.iterdir()}
        result = fixture.run_script()
        assert result.returncode == 0 and "DRY RUN" in result.stdout and not fixture.log.exists()
        assert before == {p: p.read_bytes() for p in fixture.directory.iterdir()}
        fixture.assert_blinded(result)
        print("recovery: 4 additional process-observation failures refuse before uninstall; directory markers remain unopened; default dry run immutable")
    finally:
        fixture.doCleanups()


if __name__ == "__main__":
    parser_probes()
    release_probes()
    recovery_probes()
