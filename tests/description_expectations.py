"""Apply the two lead-authorized ADMIT expectations to frozen v4 at test load."""

from functools import partialmethod
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
VARIANTS = ("same_index", "late_index")
INDEX = "f2-stab/KITS.json"


def _registered_world(suite, base, variant):
    manifests = {}
    seal = suite.Book.seal

    def defer_registration(book, label):
        if label == "register public designs and identifiers before any close":
            for path in (book.path / "manifests").glob("*.json"):
                manifests[path] = path.read_bytes()
                path.unlink()
        return seal(book, label)

    class RegisteredWorld(suite.World):
        def named(self, name, path, document):
            if name == "roster":
                self.index_commit = self.book.seal("commit the index before final registration")
                for manifest, payload in manifests.items():
                    suite.put(manifest, payload)
                self.reg = self.book.seal("register both final manifests")
            super().named(name, path, document)

    with patch.object(suite.Book, "seal", defer_registration):
        return RegisteredWorld(base, suite.IDS[2], variant)


def _expect_admit(test, suite, variant):
    look = suite.IDS[2]
    test.admissible_control(look)
    world = _registered_world(suite, test.base, variant)
    test.assertEqual((world.repo / INDEX).read_bytes(), suite.committed_index())
    test.assertEqual(suite.git_ok(world.repo, "cat-file", "-e", f"{world.receipts}:{INDEX}"),
                     variant == "same_index")
    test.assertTrue(suite.git_ok(world.repo, "cat-file", "-e", f"{world.index_commit}:{INDEX}"))
    test.assertNotEqual(world.index_commit, world.reg)
    test.assertTrue(suite.git_ok(world.repo, "merge-base", "--is-ancestor", world.index_commit, world.reg))
    for stability_look in suite.IDS[1:]:
        path = f"manifests/{stability_look}.json"
        test.assertFalse(suite.git_ok(world.repo, "cat-file", "-e", f"{world.index_commit}:{path}"))
        test.assertTrue(suite.git_ok(world.repo, "cat-file", "-e", f"{world.reg}:{path}"))
    test.assertIn("f2-stab-15/L001", world.good)
    test.stage1(world)
    test.assertEqual(suite.reservation_boundary(test, world), [str(world.private)])
    test.assertFalse(world.private.exists() or world.public.exists())


def apply(suite):
    corrections = json.loads((HERE / "description_expectation_corrections.json").read_bytes())
    manifest = (HERE / "description-v4.sha256").read_bytes()
    cases = {f"test_desc_looks_acceptance.Checks.test_lm_stab_02_refuse_{variant}": variant
             for variant in VARIANTS}
    if (corrections["version"], corrections["authority"], corrections["suite_manifest_sha256"],
        corrections["expect_admit"]) != (1, "RL-190 §1.3", sha256(manifest).hexdigest(), cases):
        raise ValueError("description expectation correction does not match the authorized v4 cases")
    for line in manifest.decode("ascii").splitlines():
        digest, name = line.split()
        if Path(name).name != name or sha256((HERE / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"description freeze differs from the correction manifest: {name}")
    for test_id, variant in cases.items():
        method = test_id.rsplit(".", 1)[1]
        if not callable(getattr(suite.Checks, method, None)):
            raise ValueError(f"corrected frozen method is missing: {test_id}")
        setattr(suite.Checks, method, partialmethod(_expect_admit, suite, variant))
    print("RL-190 §1.3 ADMIT expectations: " + ", ".join(cases), flush=True)
