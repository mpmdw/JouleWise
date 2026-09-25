"""Reviewed, byte-pinned v1 claim replay before the CG-4 source changes."""

from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from unittest import mock

from scripts.capture_claim_replay_golden import (
    GOLDEN, ROOT, SELECTED_PATHS, _tracked_json, _issuance_gate,
    _window_transitions, canonical_bytes, capture,
)


# Update only alongside a reviewed refresh of tests/golden/claimgate_v1_replay.json.
GOLDEN_BLOB_SHA = "82450aa5499fb25967714835cb0d0aaecb92d372"
APPLIED_TRANSITIONS: frozenset[str] = frozenset()


def _blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()


def _assert_matches_golden(actual: bytes) -> None:
    if actual != GOLDEN.read_bytes():
        raise AssertionError("claim replay differs from reviewed golden")


class ClaimReplayGoldenTests(unittest.TestCase):
    def test_golden_blob_pinned(self) -> None:
        self.assertEqual(_blob_sha(GOLDEN.read_bytes()), GOLDEN_BLOB_SHA)

    def test_claimgate_v1_replay_golden_unchanged(self) -> None:
        expected = GOLDEN.read_bytes()
        self.assertEqual(expected, canonical_bytes(json.loads(expected)))
        actual = capture()
        pinned = json.loads(expected)
        self.assertEqual(actual["selected_paths"], list(SELECTED_PATHS))
        self.assertEqual(pinned["selected_paths"], list(SELECTED_PATHS))
        _assert_matches_golden(canonical_bytes({**pinned, "invariant": actual["invariant"],
                                                "v1_golden_manifest_ids": actual["v1_golden_manifest_ids"]}))

    def test_transitions_match_applied_state(self) -> None:
        pinned = json.loads(GOLDEN.read_bytes())["transitions"]
        actual = {"WR-6": _window_transitions(),
                  "V1-ISSUANCE-GATE-EVIDENCE-CLASS-01": {"real_v1_wire": _issuance_gate()}}
        self.assertEqual(set(actual), set(pinned))
        for ruling_id, scenarios in pinned.items():
            self.assertEqual(set(actual[ruling_id]), set(scenarios))
            for name, states in scenarios.items():
                current = actual[ruling_id][name]["pre"]
                with self.subTest(ruling_id=ruling_id, scenario=name):
                    if ruling_id not in APPLIED_TRANSITIONS:
                        self.assertEqual(current, states["pre"])
                    elif ruling_id == "WR-6":
                        expected = states["post"]["claim_evaluation"]
                        observed = current["claim_evaluation"]
                        self.assertEqual({k: v for k, v in observed.items() if k != "reason_codes"},
                                         {k: v for k, v in expected.items() if k != "reason_codes"})
                        self.assertEqual(set(observed["reason_codes"]),
                                         set(states["pre"]["claim_evaluation"]["reason_codes"])
                                         | set(states["post"]["reason_codes_added"]))
                        self.assertEqual(current["manifest_id"], states["pre"]["manifest_id"])
                        self.assertEqual(current["validator_errors"], states["pre"]["validator_errors"])
                    else:
                        self.assertEqual({k: v for k, v in current.items() if k != "direct_call"},
                                         {k: v for k, v in states["post"].items() if k != "shim"})

    def test_golden_branch_coverage_complete(self) -> None:
        from scripts.claimgate_golden_sweep import coverage_sweep
        result = coverage_sweep()
        self.assertEqual(result["unlisted"], [], result["unlisted"])

    def test_golden_mutation_sweep_zero_unlisted_survivors(self) -> None:
        from scripts.claimgate_golden_sweep import mutation_sweep
        result = mutation_sweep()
        self.assertEqual(result["unlisted_survivors"], [], result["unlisted_survivors"])

    def test_golden_detects_one_number_mutation(self) -> None:
        with mock.patch("joulewise.analysis_engine._resolve_contrast_floor", return_value=[]):
            with self.assertRaises(AssertionError):
                _assert_matches_golden(canonical_bytes(capture()))

    def test_golden_refresh_isolated(self) -> None:
        present = subprocess.run(["git", "rev-parse", "--verify", "origin/main"],
                                 cwd=ROOT, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
        if present.returncode:
            self.skipTest("origin/main absent; cannot check golden refresh isolation")
        base = subprocess.check_output(["git", "merge-base", "HEAD", "origin/main"],
                                       cwd=ROOT, text=True).strip()
        changed = subprocess.run(["git", "diff", "--quiet", base, "HEAD", "--",
                                  "tests/golden/claimgate_v1_replay.json"], cwd=ROOT)
        if changed.returncode == 1:
            source_changes = subprocess.check_output(
                ["git", "diff", "--name-only", base, "HEAD", "--", "joulewise/",
                 "scripts/epoch_equivalence_check.py"], cwd=ROOT, text=True)
            self.assertEqual(source_changes, "", "golden refresh shares a commit range with decision code; a stale local origin/main produces this failure, and CI fetches full depth")
        else:
            self.assertEqual(changed.returncode, 0)

    def test_new_matching_paths_are_informational(self) -> None:
        selected = set(json.loads(GOLDEN.read_bytes())["selected_paths"])
        additions = []
        for path in _tracked_json():
            rel = path.relative_to(ROOT).as_posix()
            if rel in selected:
                continue
            try:
                value = json.loads(path.read_bytes())
            except (ValueError, UnicodeError):
                continue
            if isinstance(value, dict) and value.get("schema_version") in {
                "joulewise.claim_verdicts.v1", "joulewise.analysis_manifest.v1",
                "joulewise.analysis_manifest.v2", "joulewise.analysis_manifest.v3",
                "joulewise.analysis_manifest.v3.prospective",
                "joulewise.analysis_manifest.v3.finalized",
                "joulewise.analysis_registry.v1", "joulewise.analysis_registry.v2",
            }:
                additions.append(rel)
        print("new tracked matching replay paths (informational):", sorted(additions))


if __name__ == "__main__":
    unittest.main()
