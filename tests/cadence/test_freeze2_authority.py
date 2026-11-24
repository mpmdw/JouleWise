"""Freeze-2 provider route checks against generated Git histories."""
import re
import subprocess
import unittest
from unittest import mock

from joulewise.cadence_looks import interim_release as C, manifest as M
from tests.cadence import look_minirepo as MR
from tests.cadence.test_interim_release import HOST_TOKEN, LOOK, digest, report


class ReportRoute(unittest.TestCase):
    def stage1(self, *, public_root="public"):
        mini = MR.mini_repo(self)
        MR.commit(mini, stage1_sha256="c" * 64)
        ledger = M.load_json(mini / M.LOOK_LEDGER_PATH)
        row = M._look_row(ledger, LOOK)
        row.update(public_root=public_root, custody_root=str(mini.parent / "synthetic-only"),
                   execution_host=HOST_TOKEN)
        self.commit_ledger(mini, ledger, "commit generated execution row")
        return mini, ledger, row

    @staticmethod
    def commit_ledger(mini, ledger, message):
        (mini / M.LOOK_LEDGER_PATH).write_bytes(C.dump(ledger))
        MR.git_commit(mini, message)

    def assert_refuses_before_report_read(self, mini, reason, route):
        run = subprocess.run
        root = route.removesuffix(f"/{LOOK}/PUBLIC.json")

        def observe(argv, **kwargs):
            paths = (str(arg).split(":", 1)[-1] for arg in argv)
            if any(path == root or path.startswith(f"{root}/") or path.endswith("/PUBLIC.json") for path in paths):
                self.fail(f"attempted Git report read: {argv}")
            return run(argv, **kwargs)

        with mock.patch.object(M.subprocess, "run", side_effect=observe):
            with self.assertRaisesRegex(M.ManifestError, f"{reason}.*{re.escape(route)}"):
                M.freeze2_authority(mini)

    def test_reserved_and_unlisted_routes_refuse_before_git_reads_report(self):
        for root, reason in (("invented/restricted", "reserved"), ("public/Sealed", "reserved"),
                             ("public/custody", "reserved"), ("public/PUBLIC.json", "reserved"),
                             ("invented/public", "allowed public root")):
            with self.subTest(root=root):
                mini, ledger, row = self.stage1(public_root=root)
                row.update(status="run", output_sha256="d" * 64, coefficients_sha256="e" * 64)
                self.commit_ledger(mini, ledger, "publish generated report commitments")
                self.assert_refuses_before_report_read(mini, reason, f"{root}/{LOOK}/PUBLIC.json")

    def test_allowed_route_requires_a_matching_execution_row_before_report_read(self):
        mini, ledger, row = self.stage1()
        row.update(status="run", execution_host="generated-other-host",
                   output_sha256="d" * 64, coefficients_sha256="e" * 64)
        self.commit_ledger(mini, ledger, "publish generated report commitments for a different host")
        self.assert_refuses_before_report_read(mini, "authenticate the execution row", f"public/{LOOK}/PUBLIC.json")

    def test_report_commit_can_inherit_the_authenticated_execution_row(self):
        mini, ledger, row = self.stage1()
        MR.git_commit(mini, "generated commit retaining the execution row")
        execution = MR.git(mini, "rev-parse", "HEAD").stdout.strip()
        record = dict(report(), commit=execution, manifest_sha256=row["sha256"])
        public = mini / "public" / LOOK / "PUBLIC.json"
        public.parent.mkdir(parents=True)
        raw = C.dump(record)
        public.write_bytes(raw)
        row.update(status="run", output_sha256=digest(raw), coefficients_sha256=record["coefficients_sha256"])
        self.commit_ledger(mini, ledger, "publish generated report")
        self.assertEqual(M.freeze2_authority(mini)[1]["decision_source"], "yes")

        # An earlier matching row cannot authorize the report's own claim to a different execution.
        wrong_commit = MR.git(mini, "rev-parse", "HEAD").stdout.strip()
        raw = C.dump(dict(record, commit=wrong_commit))
        public.write_bytes(raw)
        row["output_sha256"] = digest(raw)
        self.commit_ledger(mini, ledger, "publish generated report naming the wrong execution commit")
        with self.assertRaisesRegex(M.ManifestError, "execution commit does not authenticate"):
            M.freeze2_authority(mini)
