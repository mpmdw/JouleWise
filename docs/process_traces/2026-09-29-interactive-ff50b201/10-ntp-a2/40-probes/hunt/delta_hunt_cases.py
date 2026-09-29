"""Delta-3 hunt cases (scratch; not a repository file). Run from a worktree root."""
import json, os, time
from pathlib import Path
from unittest import mock
from tests import test_run_night as trn
from joulewise import network_time_window, night_gate

setUpModule = trn.setUpModule
tearDownModule = trn.tearDownModule


class DeltaHunt(trn.NightDriverTests):
    def _completion(self):
        plan = self.driver._load_plan(self.plan_path)
        return plan, plan.t0_epoch_s + plan.window_max_s + self.driver.COURIER_DEADLINE_S

    def _docs(self, night):
        return [(p.name, json.loads(p.read_text())["refusal"]["reason"]) for p in self.driver._refusal_paths(night)]

    def test_DM1_deadman_null_claim_without_launch_error(self):
        night = self.custody / "night"; night.mkdir()
        (night / "chain.started").write_text(json.dumps({"pid": None, "pgid": None, "popen_attempted": False}))
        plan, completion = self._completion()
        with mock.patch.object(self.driver.time, "time", return_value=completion):
            code = self.driver.dead_man(self.plan_path)
        exited = json.loads((night / "chain.exited").read_text()) if (night / "chain.exited").exists() else None
        print(f"\nDM1 exit={code} chain.exited={exited} docs={self._docs(night)}")

    def _deadman_after_failed_recovery_proof(self, census_refuses):
        night = self.custody / "night"; night.mkdir()
        (night / "chain.started").write_text(json.dumps({"pid": 999991, "pgid": 999991, "epoch_s": time.time()}))
        (night / "chain.exited").write_text(json.dumps({"pid": 999991, "exit_code": 0}))
        plan, completion = self._completion()
        network_time_window.RESTORE_PENDING_PATH.unlink(missing_ok=True)
        self.addCleanup(network_time_window.RESTORE_PENDING_PATH.unlink, missing_ok=True)
        network_time_window.create_restore_marker(self.custody, plan.plan_id,
            marker_path=network_time_window.RESTORE_PENDING_PATH)
        on_calls, proof_calls = [], []
        refusal = night_gate.Refusal("night_aborted_agent_present", "agent seen", ()) if census_refuses else None
        with mock.patch.object(self.driver.time, "time", return_value=completion), \
             mock.patch.object(network_time_window, "recover_network_time", side_effect=trn.REAL_NT_RECOVER), \
             mock.patch.object(network_time_window, "set_network_time_on", side_effect=lambda *a, **k: on_calls.append(1)), \
             mock.patch.object(network_time_window, "run_window_query", side_effect=lambda *a, **k: on_calls.append("q")), \
             mock.patch.object(self.driver, "_prove_capture_absent",
                               side_effect=lambda *a, **k: proof_calls.append(1) or (False, {"check": "P3", "matches": [{"pid": 4242}]})), \
             mock.patch.object(self.driver, "agent_census", return_value=(None, refusal)), \
             mock.patch.object(self.driver, "_append_census"):
            code = self.driver.dead_man(self.plan_path)
        print(f"\nDM2 census_refuses={census_refuses} exit={code} proof_calls={len(proof_calls)} on_or_query={on_calls} "
              f"marker_kept={network_time_window.RESTORE_PENDING_PATH.exists()} result.json={(night/'result.json').exists()} "
              f"docs_after_deadman={self._docs(night)} courier_called={self.driver.run_courier.called}")
        return plan, night

    def test_DM2a_deadman_failed_recovery_proof_no_census_refusal(self):
        self._deadman_after_failed_recovery_proof(False)

    def test_DM2b_deadman_census_doc_then_hung_driver_result_step(self):
        plan, night = self._deadman_after_failed_recovery_proof(True)
        # The hung driver resumes: failed proof, then the result step as at :3425 and :1630.
        abort = self.driver._capture_unproved_abort(night, plan, self.custody, None,
            "capture process absence could not be proved", {"check": "P3", "matches": [{"pid": 4242}]})
        if "document" not in abort:
            self.driver._write_driver_refusal(night / "refusal.json", plan, abort["reason"], abort["detail"], abort["evidence"])
        result = self.driver._write_result(self.custody, night, plan, "REFUSED", 3, abort["reason"], plan.t0_epoch_s, 1, "f" * 64, 0)
        print(f"DM2b final docs={self._docs(night)} result.aborted_reason={result['aborted_reason']} "
              f"refusal_documents={result['refusal_documents']} prior_documents={abort['evidence'].get('prior_documents')}")

    def test_SF_watchdog_supersede_failure_fallback(self):
        night = self.custody / "night"; night.mkdir()
        plan, _ = self._completion()
        allocated = []
        self.driver._write_driver_refusal(night / "refusal.json", plan, "night_window_exceeded", "deadline",
                                          {"pgid": 1}, allocated=allocated)
        prior = {"reason": "night_window_exceeded", "detail": "deadline", "evidence": {"pgid": 1},
                 "document": allocated[0].name}
        real_replace = os.replace
        def failing_replace(src, dst, *a, **k):
            if ".supersede.tmp" in str(src):
                raise OSError("injected: custody volume refused the replace")
            return real_replace(src, dst, *a, **k)
        with mock.patch.object(self.driver.os, "replace", side_effect=failing_replace):
            abort = self.driver._capture_unproved_abort(night, plan, self.custody, prior,
                "capture process absence could not be proved", {"check": "P3"})
        if "document" not in abort:
            self.driver._write_driver_refusal(night / "refusal.json", plan, abort["reason"], abort["detail"], abort["evidence"])
        result = self.driver._write_result(self.custody, night, plan, "REFUSED", 3, abort["reason"], plan.t0_epoch_s, 1, "f" * 64, 0)
        print(f"\nSF docs={self._docs(night)} result.aborted_reason={result['aborted_reason']}")

    def test_SS_watchdog_supersede_normal_prior_documents(self):
        night = self.custody / "night"; night.mkdir()
        plan, _ = self._completion()
        allocated = []
        self.driver._write_driver_refusal(night / "refusal.json", plan, "night_window_exceeded", "deadline",
                                          {"pgid": 1}, allocated=allocated)
        prior = {"reason": "night_window_exceeded", "detail": "deadline", "evidence": {"pgid": 1},
                 "document": allocated[0].name}
        abort = self.driver._capture_unproved_abort(night, plan, self.custody, prior,
            "capture process absence could not be proved", {"check": "P3"})
        print(f"\nSS docs={self._docs(night)} document={abort.get('document')} prior_documents={abort['evidence'].get('prior_documents')}")

    def test_DM3_watchdog_doc_then_driver_never_resumes_deadman_proof_fails(self):
        night = self.custody / "night"; night.mkdir()
        plan, completion = self._completion()
        # The watchdog thread fired and proved the chain's group gone, then the main loop never resumed.
        self.driver._write_driver_refusal(night / "refusal.json", plan, "night_window_exceeded", "deadline", {"pgid": 999991})
        (night / "chain.started").write_text(json.dumps({"pid": 999991, "pgid": 999991, "epoch_s": time.time()}))
        network_time_window.RESTORE_PENDING_PATH.unlink(missing_ok=True)
        self.addCleanup(network_time_window.RESTORE_PENDING_PATH.unlink, missing_ok=True)
        network_time_window.create_restore_marker(self.custody, plan.plan_id, marker_path=network_time_window.RESTORE_PENDING_PATH)
        on_calls = []
        with mock.patch.object(self.driver.time, "time", return_value=completion), \
             mock.patch.object(network_time_window, "recover_network_time", side_effect=trn.REAL_NT_RECOVER), \
             mock.patch.object(network_time_window, "set_network_time_on", side_effect=lambda *a, **k: on_calls.append(1)), \
             mock.patch.object(self.driver, "_prove_capture_absent", return_value=(False, {"check": "P3", "matches": [{"pid": 4242}]})), \
             mock.patch.object(self.driver, "agent_census", return_value=(None, None)), \
             mock.patch.object(self.driver, "_append_census"):
            code = self.driver.dead_man(self.plan_path)
        print(f"\nDM3 exit={code} ON={on_calls} marker_kept={network_time_window.RESTORE_PENDING_PATH.exists()} "
              f"result.json={(night/'result.json').exists()} docs={self._docs(night)} courier_called={self.driver.run_courier.called}")
