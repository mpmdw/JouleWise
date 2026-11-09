"""release_v4.py end to end on synthetic custody (no real data): stages (a)-(c), exit contract, tampering."""
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import support  # noqa: E402

sys.path.insert(0, str(support.REPO / "scripts"))
import release_v4  # noqa: E402


class ContractTests(unittest.TestCase):
    def test_precedence_refused_over_hold_over_agree(self):
        p = release_v4.precedence
        self.assertEqual(p("agree", "agree"), "agree")
        self.assertEqual(p("agree", "hold"), "hold")
        self.assertEqual(p("hold", "refused"), "refused")
        self.assertEqual(p("refused", "agree", "hold"), "refused")
        self.assertEqual([release_v4.EXIT[v] for v in ("agree", "hold", "refused")], [0, 1, 2])

    def test_guard_refuses_a_decimal_anywhere(self):
        v = {"schema": release_v4.SCHEMA, "verdict": "agree", "stages": {"x": {"note": "0.5 J"}}}
        self.assertEqual(release_v4.guard(v)["reason"], "verdict_not_structure_only")
        v = {"schema": release_v4.SCHEMA, "verdict": "agree", "stages": {"x": {"n": 12, "sha": "ab" * 32}}}
        self.assertEqual(release_v4.guard(v), v)

    def test_bars_pin_matches_the_tracked_bars(self):
        self.assertEqual(release_v4.sha256_file(release_v4.RELEASE_BARS), release_v4.RELEASE_BARS_SHA256)

    def test_runbook_command_matches_pins(self):
        # Seat 2 F6: the documented command passes no commit flag (the wrapper defaults to its pins), and every
        # flag it accepts exists; the runbook's build table names the pinned commits.
        text = (support.REPO / "docs/analysis/v4/RELEASE-RUNBOOK-v4.md").read_text()
        block = text.split("```bash", 1)[1].split("```", 1)[0]
        self.assertNotIn("-commit", block)
        flags = set(__import__("re").findall(r"(--[a-z-]+)", block))
        parser_flags = {"--engine-input", "--engine-out", "--engine-record", "--recompute-root", "--crosswalk",
                        "--restricted-out", "--workers", "--python", "--programs-repo"}
        self.assertLessEqual(flags, parser_flags)
        for pin in (release_v4.RELEASE_ENGINE_COMMIT, release_v4.RELEASE_RECOMPUTE_COMMIT):
            self.assertIn(pin[:9], text)

    def test_release_requires_cpython_3_13(self):
        release_v4.check_python(sys.executable if sys.version_info[:2] == (3, 13) else "python3.13")
        with self.assertRaises(release_v4.Refused) as ctx:
            release_v4.check_python("/usr/bin/false")
        self.assertEqual(ctx.exception.code, "release_python_not_3_13")

    def test_malformed_nested_shapes_refuse_with_fixed_codes(self):
        # Seat 2 F5: never an uncaught exception (exit 1 would read as hold); structure-only stdout.
        self.assertEqual(release_v4.member_refs({"journal": {"path": "j.json", "sha256": "a" * 64},
                                                 "dc_streams": [{"path": "m", "sha256": "b" * 64}]}),
                         [("journal", {"path": "j.json", "sha256": "a" * 64}),
                          ("dc_streams", {"path": "m", "sha256": "b" * 64})])
        for bad in ({"journal": {"path": "j.json"}}, {"x": [{"sha256": "zz"}]}):
            with self.assertRaises(release_v4.Refused) as ctx:
                release_v4.member_refs(bad)
            self.assertEqual(ctx.exception.code, "engine_census_malformed")


@unittest.skipUnless(support.have_commits(), "pinned build commits unavailable in this clone")
class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = support.rehearsal("full")
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        cls.checkout = support.release_checkout(cls.dir / "checkout")
        cls.code, cls.verdict, cls.wall = support.run_release(cls.checkout, cls.base, cls.dir / "out")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def custody_copy(self, name):
        dest = self.dir / name
        shutil.copytree(self.base, dest, copy_function=os.link)   # hard links: cheap; never write through them
        return dest

    def test_synthetic_release_agrees(self):
        v = self.verdict
        self.assertEqual((self.code, v["verdict"], v["reason"]), (0, "agree", None))
        self.assertEqual(v["stages"]["digests"]["status"], "verified")
        self.assertEqual(v["stages"]["recompute"]["exit"], 0)
        fams = v["stages"]["comparator"]["families"]
        held = {k for k, f in fams.items() if f["verdict"] not in ("agree", "exempt", "integrity_only", "expected_empty")}
        self.assertEqual(held, set())
        self.assertEqual(v["stages"]["comparator"]["unmapped_leaves"], 0)
        (self.dir / "release-wall-s.txt").write_text(str(self.wall))

    def test_verdict_is_structure_only_and_values_stay_restricted(self):
        out = self.dir / "out"
        text = (out / "verdict.json").read_text()
        self.assertIsNone(release_v4.FLOAT_TOKEN.search(text))
        self.assertEqual(stat.S_IMODE(out.stat().st_mode), 0o700)
        for name in ("recompute.json", "freeze.json", "comparison.json", "comparator.stdout", "recompute-full.stderr"):
            self.assertTrue((out / name).exists(), name)
        self.assertNotIn("rows", json.loads(text)["stages"]["comparator"])

    def _refuses(self, name, custody, reason, **kw):
        code, v, _ = support.run_release(kw.pop("checkout", self.checkout), custody, self.dir / name, **kw)
        self.assertEqual((code, v["verdict"], v["reason"]), (2, "refused", reason))
        return v

    def test_tampered_engine_output_refuses(self):
        c = self.custody_copy("t-fill")
        p = c / "engine-out" / "fill.json"
        data = p.read_bytes()
        p.unlink()
        p.write_bytes(data.replace(b'"synthetic":true', b'"synthetic":false', 1))
        self._refuses("o-fill", c, "release_digest_differs_from_record")

    def test_tampered_raw_input_refuses(self):
        c = self.custody_copy("t-raw")
        raw = next((c / "recompute" / "windows" / "C2" / "members").glob("*/raw/powermetrics.plist"))
        data = raw.read_bytes()
        raw.unlink()
        raw.write_bytes(data[:-2] + b"\x00\x00")
        self._refuses("o-raw", c, "release_digest_differs_from_record")

    def test_engine_refusal_refuses(self):
        c = self.custody_copy("t-ref")
        v = c / "engine-out" / "verdict.json"
        v.unlink()
        v.write_text(json.dumps(dict(schema="joulewise.align_v4.analysis_verdict.v1", status="refused",
                                     codes=["input_refused"])))
        (c / "engine-run-record.json").unlink()
        support.write_record(c)
        self._refuses("o-ref", c, "engine_run_refused")

    def test_wrong_commits_refuse(self):
        self._refuses("o-ec", self.base, "engine_commit_not_pinned", engine_commit=support.RECOMPUTE_COMMIT)
        self._refuses("o-rc", self.base, "recompute_commit_not_pinned", recompute_commit=support.ENGINE_COMMIT)
        self._refuses("o-hex", self.base, "pinned_commit_invalid", recompute_commit="c0d1efcae")

    def test_release_pins_the_rehearsed_builds(self):
        self.assertEqual((release_v4.RELEASE_ENGINE_COMMIT, release_v4.RELEASE_RECOMPUTE_COMMIT),
                         (support.ENGINE_COMMIT, support.RECOMPUTE_COMMIT))

    def test_dirty_checkout_and_changed_bars_refuse(self):
        co = support.release_checkout(self.dir / "co2")
        (co / "stray.txt").write_text("x")
        self._refuses("o-dirty", self.base, "release_checkout_not_clean", checkout=co)
        (co / "stray.txt").unlink()
        bars = co / "configs/analysis/v4/recompute_bars.json"
        doc = json.loads(bars.read_text())
        doc["families"]["scores"]["bar"] = 1e-3
        bars.write_text(json.dumps(doc))
        subprocess.run(["git", "-C", str(co), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "bars"],
                       check=True, capture_output=True)
        self._refuses("o-bars", self.base, "release_bars_differ", checkout=co)

    def test_crosswalk_must_match_both_rosters(self):
        c = self.custody_copy("t-cross")
        p = c / "crosswalk.json"
        doc = json.loads(p.read_text())
        doc["members"][30]["recompute_run_id"] += "-x"
        p.unlink()
        p.write_text(json.dumps(doc))
        self._refuses("o-cross", c, "crosswalk_differs_from_roster")

    def test_malformed_engine_shapes_refuse_2(self):
        # Seat 2 F5 end to end: valid JSON, malformed nesting -> exit 2 with a fixed code, never exit 1.
        cases = (("input_census", [None], "engine_census_malformed"),
                 ("input_census", [{"path": 3, "sha256": "x"}], "engine_census_malformed"),
                 ("input_census", "rows", "engine_census_missing"))
        for k, (key, value, want) in enumerate(cases):
            c = self.custody_copy(f"t-shape-{k}")
            p = c / "engine-out" / "fill.json"
            fill = json.loads(p.read_text())
            fill[key] = value
            body = {kk: v for kk, v in fill.items() if kk != "leaf_inventory"}
            sys.path.insert(0, str(support.REPO / "scripts"))
            import compare_v4_recompute as cmp
            fill["leaf_inventory"] = [dict(pointer=q, kind="null" if v is None else "bool" if type(v) is bool else
                                           "number" if type(v) in (int, float) else "string")
                                      for q, v in cmp.leaves(body).items()]
            p.unlink()
            p.write_text(json.dumps(fill))
            (c / "engine-run-record.json").unlink()
            support.write_record(c)
            code, v, _ = support.run_release(self.checkout, c, self.dir / f"o-shape-{k}", workers=1)
            self.assertEqual((code, v["verdict"], v["reason"]), (2, "refused", want))
            self.assertEqual(release_v4.guard(v), v)

    def test_existing_restricted_out_refuses(self):
        (self.dir / "exists").mkdir()
        code, v, _ = support.run_release(self.checkout, self.base, self.dir / "exists")
        self.assertEqual((code, v["reason"]), (2, "restricted_out_exists"))


if __name__ == "__main__":
    unittest.main()
