"""Run the writer's synthetic control with the W1 launcher and kit."""

from contextlib import ExitStack
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch


class ExpectedRefusal(Exception):
    """The expected refusal was observed before the fixture cleans up."""


def check(repo, launcher_source, fault):
    suite_path = repo / "tests/frozen/partc-v4/suite-v4/tests/align/test_partc_writer_v4.py"
    spec = spec_from_file_location("partc_v4_writer", suite_path)
    suite = module_from_spec(spec)
    sys.modules[spec.name] = suite
    spec.loader.exec_module(suite)

    with TemporaryDirectory(prefix="jw-w1-part-c-") as tmp:
        root = Path(tmp).resolve()
        # The writer loads its other dependencies in this private tree. Stage
        # the checkout's launcher and kit before the pinned loader fills it.
        scripts = root / "src/scripts"
        scripts.mkdir(parents=True)
        launcher = scripts / "run_align_r1_smoke.py"
        launcher.write_bytes(launcher_source.read_bytes())
        kit = scripts / "align_r1_followup_kit.py"
        kit.write_bytes((repo / "scripts" / kit.name).read_bytes())

        with suite.v4_context(root), ExitStack() as stack:
            smoke = suite.fixture.smoke
            assert Path(smoke.__file__).resolve() == launcher
            assert Path(suite.fixture.kit.__file__).resolve() == kit
            published = suite.published
            verify_publication = suite.evidence.verify_part_c_publication

            if fault == "handoff-ledger":
                part_argv = smoke.part_argv

                def wrong_handoff_hash(args, which):
                    argv = part_argv(args, which)
                    if which == "C":
                        index = argv.index("--soak-ledger-sha256") + 1
                        reference_hash = sha256(Path(args.soak_reference).read_bytes()).hexdigest()
                        assert argv[index] != reference_hash, "the launcher already supplied the reference hash"
                        argv[index] = reference_hash
                    return argv

                stack.enter_context(patch.object(smoke, "part_argv", wrong_handoff_hash))
            elif fault in {"publication-ledger", "publication-reference"}:
                def wrong_publication_hash(run_root, ledger_sha, reference_sha):
                    assert ledger_sha != reference_sha
                    if fault == "publication-ledger":
                        return verify_publication(run_root, reference_sha, reference_sha)
                    return verify_publication(run_root, ledger_sha, ledger_sha)

                stack.enter_context(patch.object(suite.evidence, "verify_part_c_publication", wrong_publication_hash))

            def check_handoff(case, rc):
                attempt = case.attempt
                ledger_path = attempt.output / "evidence_ledger.jsonl"
                evaluation = suite.read(attempt.output / "smoke.json")["evaluation"]
                runner = suite.read(attempt.root / "runner_receipt.json")
                if fault == "handoff-ledger":
                    assert rc == runner["rc"] == 2 and runner["parts"] == {"C": False}
                    assert not ledger_path.exists(), "a wrong handoff hash reached row zero"
                    assert evaluation["evidence_failures"] == {"source_integrity": "source_integrity"}
                    raise ExpectedRefusal

                assert ledger_path.is_file(), f"W1 launcher failed before row zero: {evaluation['evidence_failures']}"
                first, *members, final = suite.rows(ledger_path)
                for field, path in (("soak_ledger", attempt.ledger), ("soak_reference", attempt.reference)):
                    assert first[field] == {"path": str(path), "sha256": sha256(path.read_bytes()).hexdigest()}
                assert [row["kind"] for row in members] == list(suite.pc.KINDS)
                assert final["verdict"] == evaluation["verdict"] == "pass"
                if fault:
                    assert rc == runner["rc"] == 2 and runner["parts"] == {"C": False}
                    assert "verdict_binding" in runner["error"]
                    raise ExpectedRefusal
                return published(case, rc)

            stack.enter_context(patch.object(suite, "published", check_handoff))
            try:
                missing = suite.control(root / "base")
            except ExpectedRefusal:
                assert fault
            else:
                assert fault is None, f"W1 accepted {fault}"
                assert not missing, f"missing descriptor bindings: {missing}"


if __name__ == "__main__":
    check(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), sys.argv[3] if len(sys.argv) > 3 else None)
