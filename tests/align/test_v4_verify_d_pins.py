import copy
import json
from pathlib import Path
import unittest

from scripts.align_v4_verify_d_pins import DEFAULT_PINS, verify


class VerifyDPinsTest(unittest.TestCase):
    def setUp(self):
        self.pins = json.loads(Path(DEFAULT_PINS).read_text())
        files = [{"path": p, "bytes": v["size"], "sha256": v["sha256"] or "0" * 64}
                 for p, v in self.pins["files"].items()]
        self.report = {"checks": [{"check": "disk", "models": {"D": {
            "revision": self.pins["revision"], "files": files}}}]}

    def test_pins_cover_all_d_files_with_lfs_hashes(self):
        self.assertEqual(self.pins["revision"], "815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9")
        self.assertEqual(len(self.pins["files"]), 19)
        weights = [p for p in self.pins["files"] if p.endswith(".safetensors")]
        self.assertTrue(weights)
        self.assertTrue(all(self.pins["files"][p]["sha256"] for p in weights))

    def test_matching_inventory_passes(self):
        self.assertEqual(verify(self.report, self.pins), [])

    def test_hash_size_missing_and_extra_fail(self):
        for mutate, word in (
                (lambda fs: fs[-1].__setitem__("sha256", "f" * 64), "sha256"),
                (lambda fs: fs[0].__setitem__("bytes", fs[0]["bytes"] + 1), "size"),
                (lambda fs: fs.pop(), "missing"),
                (lambda fs: fs.append({"path": "x.bin", "bytes": 1, "sha256": "a"}), "unpinned")):
            report = copy.deepcopy(self.report)
            files = report["checks"][0]["models"]["D"]["files"]
            files.sort(key=lambda f: f["path"].endswith(".safetensors"))
            mutate(files)
            problems = verify(report, self.pins)
            self.assertTrue(any(word in p for p in problems), (word, problems))

    def test_hf_local_dir_bookkeeping_is_ignored_but_counted(self):
        from scripts.align_v4_verify_d_pins import bookkeeping
        report = copy.deepcopy(self.report)
        files = report["checks"][0]["models"]["D"]["files"]
        files += [{"path": ".cache/huggingface/download/model.safetensors.lock", "bytes": 0, "sha256": "e"},
                  {"path": ".cache/huggingface/.gitignore", "bytes": 1, "sha256": "e"}]
        self.assertEqual(verify(report, self.pins), [])
        self.assertEqual(len(bookkeeping(report)), 2)
        # only the hf bookkeeping prefix is exempt
        for path in (".cache/other/x.bin", "cache/huggingface/x", "sub/.cache/huggingface/x"):
            r = copy.deepcopy(self.report)
            r["checks"][0]["models"]["D"]["files"].append({"path": path, "bytes": 1, "sha256": "a"})
            self.assertTrue(any("unpinned" in p for p in verify(r, self.pins)), path)

    def test_wrong_revision_or_no_disk_check_fails(self):
        report = copy.deepcopy(self.report)
        report["checks"][0]["models"]["D"]["revision"] = "x"
        self.assertTrue(verify(report, self.pins))
        self.assertTrue(verify({"checks": []}, self.pins))


if __name__ == "__main__":
    unittest.main()
