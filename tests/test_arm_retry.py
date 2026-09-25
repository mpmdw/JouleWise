"""Offline A172 oracles; no processes, network, installers or machine probes."""

import ast
import copy
import hashlib
import json
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

from joulewise import arm_retry, night_gate
from scripts import run_night


ROOT = Path(__file__).resolve().parents[1]
RETRY = {
    "arm_idle_interactive", "arm_notice_mismatch",
    "arm_watchdog_uncertain", "arm_transport",
}
# Independent literals, not derived from the implementation or renderer.
COLD = {
    "night_refused_agent_present", "night_refused_not_quiet", "night_refused_bind_expired",
    "night_refused_hid_idle", "night_refused_boot_clock",
    "night_refused_registration", "night_window_expired", "night_plan_stale",
    "measurement_root_outside_custody",
    "night_plan_malformed", "night_chain_digest_mismatch",
    "launch_go_receipt_missing", "launch_go_receipt_invalid",
    "night_refused_class_unbuilt", "night_receipt_class_invalid",
    "night_probe_error", "night_aborted_agent_present",
    "night_chain_already_started", "night_chain_alive", "night_chain_launch_failed",
    "night_courier_running", "night_courier_unavailable",
    "night_plan_overruns_deadman", "night_record_exists",
    "night_calibration_refused", "night_window_exceeded",
    # Cold gate QPE01-DAEMON-CONTAMINATION-01 ruling 10 Q2 (2026-09-23): the
    # two-consecutive-envelope machine-state abort.  It keeps the
    # registration's exclusion spelling so the refusal document and the
    # excluded envelopes name the same cause; `classify_abort` already
    # defaulted it to cold_gate, so nothing about retry policy moves.
    "non_observer_process_busy",
}
INSTALLER = {
    "install_span_closed", "install_outside_span", "plan_t0_in_the_past",
    "night_agent_already_loaded", "plan_outside_custody_root", "night_plan_malformed",
    "plan_schedule_unrepresentable", "install_spans_unresolvable_on_day",
    "plan_t0_not_minute_aligned", "plan_t0_ambiguous_local_time",
    "retained prior plist: <path>; re-run --uninstall",
    "unsupported plist destination: <path>",
    "--render-only directory must differ from launch_dir",
}
DOCS = ("docs/process/NIGHT_HANDBACK.md", "docs/phase_2/derivation_night_runbook.md")


class ArmRetryTests(unittest.TestCase):
    def setUp(self):
        # Resolve actual local dates using the LIVE constant, never fake spans.
        self.day = datetime(2026, 9, 15).date()
        self.spans = [span for offset in range(3)
                      for span in run_night.install_spans_for_day(self.day + timedelta(days=offset))]
        self.now = self.spans[0][1] - 600
        self.candidate = dict(plan_id="a172-offline", receipt_class="REHEARSAL_STUB",
                              repo_head="a" * 40, measurement_head="a" * 40,
                              authored_epoch_s=self.now - 3600, t0_epoch_s=self.now + 6000)
        raw = json.dumps(self.candidate).encode()
        self.plan = dict(plan_bytes=raw, saved_plan_bytes=raw, reviewed_head="a" * 40,
                         install_close_epoch_s=run_night.install_close_epoch(SimpleNamespace(**self.candidate)),
                         plan_max_age_s=night_gate.PLAN_MAX_AGE_S)
        digest = hashlib.sha256(raw).hexdigest()
        self.attempts = [dict(attempt=1, attempt_epoch_s=self.now - 60,
                              abort_epoch_s=self.now - 30, cause="arm_transport",
                              receipt_class="REHEARSAL_STUB", plan_sha256=digest,
                              message_id="earlier-message", outcome="not_published")]
        self.notice = dict(accepted=True, message_id="fresh-message", thread_id="thread",
                           sent_epoch_s=self.now, attempt=2, plan_id="a172-offline",
                           receipt_class="REHEARSAL_STUB", measurement_head="a" * 40,
                           plan_sha256=digest, prerequisites_clear=True, veto_clear=True,
                           latest_no_epoch_s=None, latest_abort_epoch_s=self.now - 30,
                           blocking_causes=[])

    def decide(self, now=None):
        return arm_retry.retry_allowed(self.now if now is None else now,
                                       self.plan, self.attempts, self.notice)

    def change_candidate(self, **changes):
        self.candidate.update(changes)
        raw = json.dumps(self.candidate).encode()
        self.plan.update(plan_bytes=raw, saved_plan_bytes=raw,
                         install_close_epoch_s=run_night.install_close_epoch(SimpleNamespace(**self.candidate)))
        digest = hashlib.sha256(raw).hexdigest()
        self.notice["plan_sha256"] = digest
        for prior in self.attempts:
            prior["plan_sha256"] = digest

    def test_retry_enumeration_and_unknowns(self):
        self.assertEqual(set(arm_retry.RETRY_CAUSES), RETRY)
        self.assertEqual(arm_retry.UNCERTAIN_STATES, ("CLOCK_UNCERTAIN", "NETWORK_UNCERTAIN"))
        for cause in RETRY:
            self.assertEqual(arm_retry.classify_abort(cause), "retry", cause)
        for cause in (None, {}, [], "", "transport", "CLOCK_UNCERTAIN", "NETWORK_UNCERTAIN",
                      "arm_transport,night_probe_error", "future_reason"):
            self.assertEqual(arm_retry.classify_abort(cause), "cold_gate")

    def test_every_cold_assignment_is_explicit(self):
        self.assertEqual(set(arm_retry.COLD_GATE_CODES), COLD)
        self.assertEqual(set(arm_retry.COLD_GATE_CODES),
                         night_gate.NIGHT_GATE_REASON_CODES | night_gate.NIGHT_DRIVER_REASON_CODES)
        self.assertEqual(set(arm_retry.INSTALLER_REFUSALS), INSTALLER)
        self.assertEqual(set(arm_retry.OTHER_REFUSALS), {"HOLD_CENSUS", "slot_refused"})
        self.assertFalse(RETRY & (COLD | INSTALLER | {"HOLD_CENSUS", "slot_refused"}))
        self.assertEqual(set(arm_retry.DISPOSITIONS), RETRY | COLD | INSTALLER | {"HOLD_CENSUS", "slot_refused"})
        for cause in COLD | INSTALLER | {"HOLD_CENSUS", "slot_refused"}:
            self.assertEqual(arm_retry.classify_abort(cause), "cold_gate", cause)
            self.assertEqual(arm_retry.DISPOSITIONS[cause], "cold_gate", cause)

    def test_installer_table_is_the_live_complete_table(self):
        text = (ROOT / DOCS[1]).read_text()
        table = text.split("| Refusal | Exit code | Condition / recovery |\n", 1)[1].split("\n\n", 1)[0]
        observed = {line.split("`", 2)[1] for line in table.splitlines() if line.startswith("| `")}
        self.assertEqual(observed, INSTALLER)

    def test_rendered_registration_refusal_preserves_ruled_digest_and_chain_binding(self):
        self.assertIn(
            "| `night_refused_registration` | The registration digest is not in the ruled table, "
            "or its bound chain-source digest differs from the measured source. |",
            arm_retry.render_policy().splitlines(),
        )

    def test_both_document_blocks_are_exact(self):
        begin = b"<!-- BEGIN ARM-RETRY-POLICY v1 -->"
        end = b"<!-- END ARM-RETRY-POLICY v1 -->\n"
        for name in DOCS:
            raw = (ROOT / name).read_bytes()
            self.assertEqual(raw.count(begin), 1, name)
            self.assertEqual(raw.count(end), 1, name)
            block = raw[raw.index(begin):raw.index(end) + len(end)]
            self.assertEqual(block, arm_retry.render_policy().encode(), name)

    def test_stale_plan_operator_description_names_clone_cleanliness(self):
        self.assertEqual(
            arm_retry.COLD_GATE_CODES["night_plan_stale"],
            "Plan age, pinned head, or a clean measurement clone failed; not a stale notice.",
        )
        for name in DOCS:
            self.assertIn(
                "| `night_plan_stale` | Plan age, pinned head, or a clean measurement clone failed; not a stale notice. |",
                (ROOT / name).read_text(),
            )

    def test_runbook_describes_t0_clone_status_and_recut_remedy(self):
        text = (ROOT / DOCS[1]).read_text()
        section = text.split("### 0.8 The clone's tree is clean", 1)[1].split(
            "#### The two desk inputs", 1)[0]
        for phrase in ("At t0", "untracked files included", "fsmonitor hook disabled",
                       "`night_plan_stale`", "`night_probe_error`",
                       "find what wrote into the", "re-cut it", "Re-arming with a fresh plan"):
            self.assertIn(phrase, section)

    def test_r2_and_per_attempt_custody(self):
        sentence = ("A retry-class abort recorded by a prior activation authorises a successor's ordinary "
                    "fresh-plan arm of the same class without a new cold gate; the predecessor's published "
                    "plan directory, if any, stays untouched under the existing human-resolution path.")
        self.assertIn(sentence, (ROOT / DOCS[0]).read_text())
        text = (ROOT / DOCS[1]).read_text()
        self.assertNotIn('$STAGE/failed-night_plan.json', text)
        self.assertNotIn('$STAGE/arm-night_plan.json', text)
        self.assertIn('$ATTEMPT_DIR/failed-night_plan.json', text)
        self.assertIn('mkdir "$ATTEMPT_DIR"', text)

    def test_spacing_59_vs_60(self):
        self.assertTrue(self.decide().allowed)
        self.attempts[0]["attempt_epoch_s"] += 1
        self.assertEqual(self.decide(), arm_retry.Decision(False, "retry_spacing"))
        self.attempts[0]["attempt_epoch_s"] -= 1
        self.assertTrue(self.decide().allowed)

    def test_install_close_before_at_after(self):
        close = self.plan["install_close_epoch_s"]
        for delta, expected in ((-1, True), (0, False), (1, False)):
            with self.subTest(delta=delta):
                self.assertEqual(self.decide(close + delta).allowed, expected)
                if not expected:
                    self.assertEqual(self.decide(close + delta).reason, "install_closed")

    def test_plan_age_at_and_over_maximum(self):
        # At max age t0 cannot remain ahead of install close: assert that the
        # age guard passes to that independent cutoff, not a fictitious arm.
        maximum = night_gate.PLAN_MAX_AGE_S
        self.change_candidate(authored_epoch_s=self.now - maximum, t0_epoch_s=self.now)
        self.assertEqual(self.decide().reason, "install_closed")
        self.change_candidate(authored_epoch_s=self.now - maximum - 1)
        self.assertEqual(self.decide().reason, "plan_age")

    def test_plan_age_future_authored_and_t0_bound(self):
        self.change_candidate(authored_epoch_s=self.now + 1)
        self.assertEqual(self.decide().reason, "plan_age")
        self.change_candidate(authored_epoch_s=self.now - 100,
                              t0_epoch_s=self.now - 100 + night_gate.PLAN_MAX_AGE_S + 1)
        self.assertEqual(self.decide().reason, "plan_age")

    def test_midnight_retry_two_days_later_before_install_close(self):
        # Sep 15 23:49 attempt, Sep 17 00:05 retry, close at 00:15.
        # Whole-day spans must not discard the last 15 minutes of eligibility.
        third_open = self.spans[2][0]
        self.assertEqual(self.attempts[0]["attempt_epoch_s"], self.spans[0][1] - 660)
        # Derive the arm-to-t0 lead from the live driver so the cell holds under
        # any PLAN_LEAD_S / INSTALL_CLOSE_MARGIN_S (LEAD-MARGIN-01 shortens them).
        probe_t0 = third_open + 6000
        lead = probe_t0 - run_night.install_close_epoch(SimpleNamespace(**dict(self.candidate, t0_epoch_s=probe_t0)))
        self.change_candidate(t0_epoch_s=third_open + 900 + lead)
        self.assertEqual(self.plan["install_close_epoch_s"], third_open + 900)
        self.notice["sent_epoch_s"] = third_open + 300
        self.assertEqual(self.decide(third_open + 300), arm_retry.Decision(True, "allowed"))

    def test_truncated_abort_transcription_denied(self):
        aborted = self.now - 30 + 0.6
        self.attempts[-1]["abort_epoch_s"] = aborted
        self.notice["latest_abort_epoch_s"] = aborted
        self.assertTrue(self.decide().allowed)
        self.notice["latest_abort_epoch_s"] = int(aborted)
        self.assertEqual(self.decide(), arm_retry.Decision(False, "notice_abort_mismatch"))

    def test_invalid_history_and_candidate_head_mismatch(self):
        for case in ("abort_before_start", "abort_in_future", "overlapping_attempts",
                     "repo_head", "measurement_head"):
            with self.subTest(case=case):
                self.setUp()
                if case == "overlapping_attempts":
                    self.attempts.insert(0, dict(
                        self.attempts[0], attempt_epoch_s=self.now - 180,
                        abort_epoch_s=self.now - 120, message_id="first-message"))
                    self.attempts[1]["attempt"] = 2
                    self.notice["attempt"] = 3
                self.assertEqual(self.decide(), arm_retry.Decision(True, "allowed"))
                if case == "abort_before_start":
                    self.attempts[0]["abort_epoch_s"] = self.now - 61
                elif case == "abort_in_future":
                    self.attempts[0]["abort_epoch_s"] = self.now + 1
                elif case == "overlapping_attempts":
                    self.attempts[1]["attempt_epoch_s"] = self.now - 121
                else:
                    self.change_candidate(**{case: "b" * 40})
                self.notice["latest_abort_epoch_s"] = self.attempts[-1]["abort_epoch_s"]
                reason = ("candidate_head_mismatch" if case in ("repo_head", "measurement_head")
                          else "invalid_history")
                self.assertEqual(self.decide(), arm_retry.Decision(False, reason))

    def test_notice_well_formedness_precedes_reuse(self):
        self.attempts[0]["message_id"] = ""  # prior attempt never sent mail
        self.notice["message_id"] = ""
        self.assertEqual(self.decide(), arm_retry.Decision(False, "notice_not_current"))
        self.attempts[0]["message_id"] = "earlier-message"
        self.notice.update(message_id="earlier-message", attempt=1)
        self.assertEqual(self.decide(), arm_retry.Decision(False, "notice_not_current"))
        self.notice["attempt"] = 2
        self.assertEqual(self.decide(), arm_retry.Decision(False, "notice_reused"))

    def test_stale_notice_digest_head_abort_no_and_attempt(self):
        changes = (
            ("plan_sha256", "0" * 64, "notice_binding_mismatch"),
            ("measurement_head", "b" * 40, "notice_binding_mismatch"),
            ("plan_id", "another", "notice_binding_mismatch"),
            ("receipt_class", "DIAGNOSTIC_NO_PACK", "notice_binding_mismatch"),
            ("latest_abort_epoch_s", self.now + 1, "notice_abort_mismatch"),
            ("latest_no_epoch_s", self.now + 1, "owner_no"),
            ("latest_no_epoch_s", self.now - 3600, "owner_no"),
            ("attempt", 1, "notice_not_current"),
            ("message_id", "earlier-message", "notice_reused"),
            ("sent_epoch_s", self.now - 31, "notice_timing"),
        )
        for key, value, reason in changes:
            with self.subTest(key=key, value=value):
                old = self.notice[key]
                self.notice[key] = value
                self.assertEqual(self.decide().reason, reason)
                self.notice[key] = old
        self.assertTrue(self.decide().allowed)

    def test_exact_bytes_not_parsed_json(self):
        self.plan["plan_bytes"] += b"\n"
        self.assertEqual(self.decide().reason, "candidate_changed")
        self.plan["saved_plan_bytes"] = self.plan["plan_bytes"]
        self.attempts = []
        self.notice.update(attempt=1, latest_abort_epoch_s=None)
        self.assertEqual(self.decide().reason, "notice_binding_mismatch")

    def test_current_notice_lead_is_ordering_only(self):
        self.assertEqual(arm_retry.NOTICE_LEAD_S, 0)
        self.assertTrue(self.decide().allowed)
        self.notice["sent_epoch_s"] += 0.01
        self.assertEqual(self.decide().reason, "notice_timing")
        self.notice["sent_epoch_s"] = self.now - 30
        self.assertTrue(self.decide().allowed)

    def test_initial_arm_has_no_retry_spacing_or_extra_notice_age(self):
        self.attempts = []
        self.notice.update(attempt=1, latest_abort_epoch_s=None, sent_epoch_s=self.now - 3600)
        self.assertTrue(self.decide().allowed)

    def test_no_attempt_count_cap(self):
        base = self.attempts[0]
        self.attempts = [dict(base, attempt=i + 1, attempt_epoch_s=self.now - 600 + 60 * i,
                              abort_epoch_s=self.now - 590 + 60 * i, message_id="old-" + str(i))
                         for i in range(10)]
        self.notice.update(attempt=11, latest_abort_epoch_s=self.attempts[-1]["abort_epoch_s"])
        self.assertTrue(self.decide().allowed)

    def test_refusals_override_every_retry_cause(self):
        for cause in RETRY:
            self.attempts[0]["cause"] = cause
            self.assertTrue(self.decide().allowed)
            for refusal in COLD | INSTALLER | {"HOLD_CENSUS", "slot_refused", "unknown"}:
                self.notice["blocking_causes"] = [refusal]
                self.assertEqual(self.decide().reason, "cold_gate_evidence")
            self.notice["blocking_causes"] = []
        for refusal in COLD | INSTALLER | {"HOLD_CENSUS", "slot_refused", "unknown"}:
            self.attempts[0]["cause"] = refusal
            self.assertEqual(self.decide().reason, "cold_gate_history")

    def test_policy_prose_pins_unreadable_thread_is_not_a_stop(self):
        # Delta re-audit F1: the R1 correction must not be revertible in prose alone.
        policy = arm_retry.render_policy()
        self.assertIn("Record an unreadable notice thread as a limitation in the attempt directory; it is not a stop", policy)
        self.assertIn("neither clearance boolean requires reading it", policy)
        self.assertIn("An unreadable notice thread is recorded as a limitation", arm_retry.retry_allowed.__doc__)
        self.assertNotIn("unreadable veto channel is not clear", policy)

    def test_runbook_pins_byte_for_byte_abort_copy(self):
        # Delta re-audit F2: the R3 instruction must survive a docs-only reversion.
        runbook = (ROOT / DOCS[1]).read_text(encoding="utf-8")
        needle = "`latest_abort_epoch_s` is copied byte-for-byte from\n   `attempts[-1].abort_epoch_s`, never re-typed, rounded or truncated"
        self.assertIn(needle, runbook)

    def test_headless_unreadable_thread_recorded_without_observed_no_allows(self):
        # Memory-only attempt-directory evidence: lack of thread access is a
        # recorded limitation, not a veto. Only authorized observations clear it.
        attempt_directory = {
            "notice-thread-limitation.txt": "Notice thread unreadable in this headless activation.",
            "directive-issues.json": {"standing_no_epoch_s": None},
            "stop-check.json": {"standdown_requested": False, "stop_present": False},
            "relayed-no.json": {"standing_no_epoch_s": None},
        }
        self.assertIn("unreadable", attempt_directory["notice-thread-limitation.txt"])
        stops = attempt_directory["stop-check.json"]
        observed_no = [attempt_directory[name]["standing_no_epoch_s"]
                       for name in ("directive-issues.json", "relayed-no.json")
                       if attempt_directory[name]["standing_no_epoch_s"] is not None]
        self.notice.update(veto_clear=not any(stops.values()) and not observed_no,
                           prerequisites_clear=True,
                           latest_no_epoch_s=max(observed_no) if observed_no else None)
        self.assertEqual(self.decide(), arm_retry.Decision(True, "allowed"))
        self.attempts = []
        self.notice.update(attempt=1, latest_abort_epoch_s=None)
        self.assertEqual(self.decide(), arm_retry.Decision(True, "allowed"))
        # An observed NO still stops, even with the thread unreadable.
        self.notice["latest_no_epoch_s"] = self.now - 3600
        self.assertEqual(self.decide(), arm_retry.Decision(False, "owner_no"))

    def test_uncleared_and_unknown_evidence_never_authorizes(self):
        for key in ("accepted", "veto_clear", "prerequisites_clear"):
            for value in (False, "true", 1, None):
                old = self.notice[key]
                self.notice[key] = value
                self.assertFalse(self.decide().allowed, (key, value))
                self.notice[key] = old
        for outcome in ("committed", "held", "retained", "unknown", "restoration_failed"):
            self.attempts[0]["outcome"] = outcome
            self.assertEqual(self.decide().reason, "cold_gate_history")
        self.attempts[0]["outcome"] = "restored_unpublished"
        self.assertTrue(self.decide().allowed)

    def test_malformed_inputs_fail_closed_without_mutation(self):
        before = copy.deepcopy((self.plan, self.attempts, self.notice))
        self.assertTrue(self.decide().allowed)
        self.assertEqual(before, (self.plan, self.attempts, self.notice))
        for container in (self.plan, self.notice, self.attempts[0]):
            for key in list(container):
                value = container.pop(key)
                self.assertFalse(self.decide().allowed, key)
                container[key] = value
        for now in (float("nan"), float("inf"), True, None, "123"):
            self.assertFalse(arm_retry.retry_allowed(now, self.plan, self.attempts, self.notice).allowed)

    def test_foreground_publication_executes_real_guard_before_move(self):
        # Execute the actual documented consumer with memory-only paths. The
        # operational consumer imports a real module; it never extracts code.
        text = (ROOT / DOCS[1]).read_text()
        source = text.split('# 5. Publication: the one irreversible instant.\n', 1)[1]
        source = source.split("<<'PY'\n", 1)[1].split('\nPY\n', 1)[0]
        tree = ast.parse(source)
        tree.body = [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom))]
        executable = compile(tree, '<runbook publication>', 'exec')
        for alteration in (None, "initial", "bytes", "digest", "no", "attempt", "cutoff"):
            with self.subTest(alteration=alteration):
                notice = dict(self.notice)
                attempts = self.attempts
                if alteration == "initial":
                    attempts = []
                    notice.update(attempt=1, latest_abort_epoch_s=None)
                if alteration == "digest":
                    notice["plan_sha256"] = "0" * 64
                if alteration == "no":
                    notice["latest_no_epoch_s"] = self.now
                if alteration == "attempt":
                    notice["attempt"] = 1
                files = {
                    'staged': self.plan['plan_bytes'] + (b'\n' if alteration == 'bytes' else b''),
                    'attempt/plan.json': self.plan['saved_plan_bytes'],
                    'attempt/notice.json': json.dumps(notice).encode(),
                    'attempt/attempts.json': json.dumps(attempts).encode(),
                }
                class MemoryPath:
                    def __init__(self, name):
                        self.name = name

                    def __truediv__(self, other):
                        return MemoryPath(self.name + '/' + other)

                    def read_bytes(self):
                        return files[self.name]

                    def read_text(self):
                        return self.read_bytes().decode()

                    def exists(self):
                        return self.name in files

                    def is_symlink(self):
                        return False

                moves = []
                env = dict(ATTEMPT_DIR='attempt', STAGED_PLAN='staged', NIGHT_ROOT='night',
                           ARM_ATTEMPT='1' if alteration == 'initial' else '2', H='a' * 40)
                namespace = dict(
                    json=json, Path=MemoryPath,
                    os=SimpleNamespace(environ=env, replace=lambda *args: moves.append(args)),
                    time=SimpleNamespace(time=lambda: self.plan['install_close_epoch_s']
                                         if alteration == 'cutoff' else self.now),
                    NightPlan=SimpleNamespace(from_mapping=lambda row: SimpleNamespace(**row)),
                    PLAN_MAX_AGE_S=night_gate.PLAN_MAX_AGE_S,
                    install_close_epoch=run_night.install_close_epoch,
                    retry_allowed=arm_retry.retry_allowed,
                )
                if alteration in (None, "initial"):
                    exec(executable, namespace)
                    self.assertEqual(len(moves), 1)
                else:
                    with self.assertRaises(SystemExit):
                        exec(executable, namespace)
                    self.assertEqual(moves, [])

    def test_runtime_modules_never_import_arm_retry(self):
        for path in ("joulewise/night_gate.py", "scripts/run_night.py"):
            tree = ast.parse((ROOT / path).read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    self.assertFalse(any("arm_retry" in alias.name.split(".") for alias in node.names), path)
                elif isinstance(node, ast.ImportFrom):
                    self.assertNotIn("arm_retry", (node.module or "").split("."), path)
                    self.assertFalse(any(alias.name == "arm_retry" for alias in node.names), path)

    def test_module_uses_only_stdlib_and_python39_syntax(self):
        tree = ast.parse((ROOT / "joulewise/arm_retry.py").read_text(), feature_version=(3, 9))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.assertTrue(all(alias.name in {"hashlib", "json", "math", "re"} for alias in node.names))
            elif isinstance(node, ast.ImportFrom):
                self.assertIn(node.module, {"dataclasses", "typing"})


if __name__ == "__main__":
    unittest.main()


class ZeroCaptureSuccessorTests(unittest.TestCase):
    """Door 1 reads shared disk facts; C5 is deliberately bare."""

    def evidence(self):
        from joulewise.zero_capture_facts import ZeroCaptureFacts
        result = dict(verdict="REFUSED", aborted_reason="night_refused_not_quiet",
                      plan_id="predecessor", chain_exit_code=None, chain_sha256=None,
                      ended_epoch_s=100.0)
        receipt = dict(verdict="REFUSED", plan_id="predecessor",
                       refusal={"reason": "night_refused_not_quiet"},
                       conditions=[dict(condition_id="C5", measured={})])
        facts = ZeroCaptureFacts(True, True, True, True, 0, 0, 0, "empty", 0, True)
        delivery = {"courier.sent": True, "message_id": "sent-message", "plan_id": "predecessor"}
        claims = dict(candidate_plan_id="successor", candidate_sha256="a" * 64,
                      predecessor_sha256="b" * 64, predecessor_is_successor=False,
                      existing_claim=None)
        return result, receipt, facts, delivery, claims

    def test_bare_c5_needs_composed_disk_facts_and_delivery(self):
        result, receipt, facts, delivery, claims = self.evidence()
        self.assertTrue(arm_retry.successor_license(result, receipt, facts, delivery, claims, 160).allowed)
        self.assertFalse(arm_retry.successor_license(result, receipt, None, delivery, claims, 160).allowed)
        self.assertEqual(arm_retry.successor_license(result, receipt, facts,
            dict(delivery, **{"courier.sent": False}), claims, 160).reason, "delivery_incomplete")
        self.assertEqual(arm_retry.successor_license(result, receipt, facts, delivery,
            claims, 159.99).reason, "successor_spacing")

    def test_each_disk_fact_and_claim_refuses(self):
        from dataclasses import replace
        result, receipt, facts, delivery, claims = self.evidence()
        for name, value in (("chain_started", 1), ("reservation_markers_found", 1),
                            ("capture_entries_found", 1), ("envelopes_captured", 1),
                            ("scan_complete", False),
                            ("custody_root_present", False)):
            with self.subTest(name=name):
                self.assertFalse(arm_retry.successor_license(result, receipt,
                    replace(facts, **{name: value}), delivery, claims, 160).allowed)
        self.assertEqual(arm_retry.successor_license(result, receipt, facts, delivery,
            dict(claims, existing_claim=dict(successor_plan_id="other", successor_sha256="c" * 64)),
            160).reason, "successor_already_used")
        self.assertEqual(arm_retry.successor_license(result, receipt, facts, delivery,
            dict(claims, predecessor_is_successor=True), 160).reason, "successor_already_used")

    def test_f3_receipt_without_c5_row_licenses_nothing(self):
        result, receipt, facts, delivery, claims = self.evidence()
        for rows in ([], [dict(condition_id="C4", measured={})],
                     [dict(condition_id="C5", measured={}), dict(condition_id="C5", measured={})]):
            with self.subTest(rows=rows):
                bad = dict(receipt, conditions=rows)
                # Release keeps the receipt's veto-only role; only the successor route tightens.
                self.assertTrue(arm_retry.terminal_zero_capture_refusal(result, bad).allowed)
                self.assertEqual(arm_retry.successor_license(result, bad, facts, delivery,
                                                             claims, 160).reason,
                                 "malformed_successor_evidence")
        five = [dict(condition_id=c, measured={}) for c in ("C1", "C2", "C3", "C4", "C5")]
        self.assertTrue(arm_retry.successor_license(result, dict(receipt, conditions=five),
                                                    facts, delivery, claims, 160).allowed)

    def test_f5_each_identity_and_delivery_comparison_refuses(self):
        result, receipt, facts, delivery, claims = self.evidence()
        def reason(**overrides):
            return arm_retry.successor_license(result, receipt, facts,
                dict(delivery, **overrides.pop("delivery", {})),
                dict(claims, **overrides), 160).reason
        self.assertEqual(reason(delivery=dict(plan_id="other")), "handoff_plan_mismatch")
        self.assertEqual(reason(delivery=dict(message_id="")), "delivery_incomplete")
        self.assertEqual(reason(delivery=dict(message_id=None)), "delivery_incomplete")
        self.assertEqual(reason(candidate_plan_id="predecessor"), "predecessor_rearm")
        self.assertEqual(reason(candidate_sha256="b" * 64), "predecessor_rearm")
        self.assertEqual(reason(existing_claim=dict(successor_plan_id="successor",
                                                    successor_sha256="c" * 64)),
                         "successor_already_used")
        self.assertEqual(reason(existing_claim=dict(successor_plan_id="other",
                                                    successor_sha256="a" * 64)),
                         "successor_already_used")
        self.assertEqual(reason(existing_claim=dict(successor_plan_id="successor",
                                                    successor_sha256="a" * 64)),
                         "new_plan_only")

    def test_door_disjointness_and_same_candidate_retry(self):
        result, receipt, facts, delivery, claims = self.evidence()
        result["aborted_reason"] = receipt["refusal"]["reason"] = "non_observer_process_busy"
        self.assertEqual(arm_retry.successor_license(result, receipt, facts, delivery,
            claims, 160).reason, "not_zero_capture_machine_refusal")
        fixture = ArmRetryTests()
        fixture.setUp()
        fixture.attempts[0]["cause"] = "night_refused_not_quiet"
        self.assertEqual(fixture.decide().reason, "cold_gate_history")
