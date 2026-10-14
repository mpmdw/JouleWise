"""Outbox and transport desk checks, with an in-process gh fake."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from joulewise.b6.mailer import GitHubTransport, Mailer, SMTPTransport, body, owner_no
from joulewise.flags.catalog import Catalog
from tests.test_b6_registration import CATALOG


class Clock:
    def __init__(self, now=1791936000): self.now = now
    def __call__(self): return self.now
    def advance(self, seconds): self.now += seconds


class Transport:
    def __init__(self):
        self.sent, self.closed, self.fail, self.no = [], [], False, False

    def send(self, entry):
        if self.fail:
            raise RuntimeError("synthetic failure")
        self.sent.append(entry)
        return {"issue_number": len(self.sent), "created_at": "2026-10-14T00:00:00Z"}

    def has_no(self, receipt, owner): return self.no
    def close(self, receipt): self.closed.append(receipt)


class MailerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.clock = Clock()
        self.transport = Transport()
        self.mailer = Mailer(self.root, CATALOG, clock=self.clock, transport=self.transport)

    def test_dedupe_two_holds_one_message(self):
        a = self.mailer.enqueue("loop_hold", "s1", "cause", {"state": "HOLD_LOOP"})
        b = self.mailer.enqueue("loop_hold", "s1", "cause", {"state": "HOLD_LOOP"})
        self.assertEqual(a, b)
        self.mailer.flush()
        self.mailer.flush()
        self.assertEqual(len(self.transport.sent), 1)

    def test_screen_energy_restricted_outcome_and_drop_free_text(self):
        catalog = Catalog({**CATALOG.codes, "synthetic.restricted": {"effect": "DISCLOSE", "blinding": "RESTRICTED"}}, None)
        for fields in ({"cause": "12 J"}, {"flags": ["synthetic.restricted"]}, {"cause": "positive"},
                       {"cause": "1.2 watts"}, {"verdict": "RESOLVED"}, {"flags": ["direction_supported"]},
                       {"cause": "not_estimable"}):
            text, blocked = body({"state": "HOLD_LOOP", **fields}, catalog)
            self.assertTrue(blocked)
            self.assertEqual(text, "state changed to HOLD_LOOP; details withheld")
        text, blocked = body({"state": "ARM_WAIT", "detail": "12 J positive", "flags": ["disk.low"]}, catalog)
        self.assertFalse(blocked)
        self.assertNotIn("12", text)

    def test_backoff_failure_recorded_retried_and_no_transport_default(self):
        key = self.mailer.enqueue("loop_hold", "s", "x", {"state": "HOLD_LOOP"})
        self.transport.fail = True
        self.mailer.flush()
        self.assertEqual(self.mailer.entry(key)["tries"], 1)
        self.assertEqual(self.mailer.entry(key)["retry_at"], self.clock() + 300)
        self.mailer.flush()
        self.assertEqual(self.mailer.entry(key)["tries"], 1)
        self.clock.advance(300)
        self.mailer.flush()
        self.assertEqual(self.mailer.entry(key)["retry_at"], self.clock() + 900)
        self.clock.advance(900)
        self.mailer.flush()
        self.assertEqual(self.mailer.entry(key)["retry_at"], self.clock() + 3600)
        self.clock.advance(3600)
        self.transport.fail = False
        self.mailer.flush()
        self.assertTrue(self.mailer.entry(key)["delivered"])
        self.assertEqual(len(list((self.root / "outbox").glob("*.json"))), 1)

    def test_owner_no_exact_author_and_after_notice(self):
        def comment(text="NO", login="mpmdw", date="2026-10-14T00:00:01Z"):
            return {"body": text, "user": {"login": login}, "created_at": date}
        notice = "2026-10-14T00:00:00Z"
        self.assertTrue(owner_no([comment("  NO\n")], "mpmdw", notice))
        for c in (comment("NO please"), comment("no"), comment(login="someone"), comment(date=notice),
                  comment(date="2026-10-13T23:59:59Z"), {}):
            self.assertFalse(owner_no([c], "mpmdw", notice))

    def test_notice_previous_session_and_no_flush_active_or_run_state(self):
        previous = {"verdict": "COLLECTED", "counting": {"alpha": True}, "flags": ["disk.low"],
                    "minutes": {"chain": 300, "harvest": 20, "desk": 5}}
        key = self.mailer.enqueue("arm_notice", "s", None, {"state": "ARM_WAIT", "previous": previous})
        self.assertEqual(json.loads(self.mailer.entry(key)["body"])["previous"], previous)
        (self.root / "collection.active").write_text("synthetic\n100\n")
        self.mailer.flush()
        self.assertEqual(self.transport.sent, [])
        (self.root / "collection.active").unlink()
        self.mailer.flush(state="SMOKE_RUN")
        self.assertEqual(self.transport.sent, [])
        self.mailer.flush(state="ARM_WAIT")
        self.assertEqual(len(self.transport.sent), 1)

    def test_gh_issue_comment_no_close_and_no_address_argv(self):
        calls = []
        def run(argv):
            calls.append(argv)
            self.assertFalse(any("@" in arg for arg in argv))
            endpoint = argv[2]
            if endpoint.endswith("comments") and "POST" not in argv:
                result = [[{"body": "NO", "user": {"login": "mpmdw"}, "created_at": "2026-10-14T00:00:01Z"}]]
            elif "?" in endpoint:
                result = [{"number": 8}]
            else:
                result = {"number": 9, "created_at": "2026-10-14T00:00:00Z"}
            return SimpleNamespace(returncode=0, stdout=json.dumps(result))
        gh = GitHubTransport("mpmdw/JouleWise", run)
        receipt = gh.send({"kind": "arm_notice", "body": "structure"})
        self.assertTrue(gh.has_no(receipt, "mpmdw"))
        gh.close(receipt)
        gh.send({"kind": "close", "body": "done"})
        self.assertTrue(any("labels[]=directive-notice" in argv for argv in calls))
        self.assertTrue(any("state=closed" in argv for argv in calls))

    def test_smtp_keychain_only_injected_no_default_sending(self):
        calls, sent = [], []
        smtp = SMTPTransport(lambda argv: (calls.append(argv) or SimpleNamespace(returncode=0, stdout="test-secret")),
                             lambda password, text: sent.append((password, text)))
        smtp.send({"body": "structure"})
        self.assertEqual(calls, [["security", "find-generic-password", "-s", "joulewise-b6-smtp", "-w"]])
        self.assertEqual(sent, [("test-secret", "structure")])
        safe = Mailer(self.root, CATALOG, clock=self.clock)
        key = safe.enqueue("close", "other", None, {"state": "DONE"})
        safe.flush()
        self.assertFalse(safe.entry(key)["delivered"])
