#!/usr/bin/env python3
"""Encode the blind allocation in the target schema and compare every leaf.

The allocation is exclusively derive_slots.derive(), committed before the
target JSON was read. Schema names, descriptive strings and metadata spelling
were inspected afterwards in that JSON; the series builder was never read or
imported. This distinction matters: matching wrapper prose is not independent
scientific evidence. No production file is written by this script.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

from derive_slots import KIT, ROOT, compact, derive

HERE = Path(__file__).absolute().parent
TARGET = KIT / "series/series_manifest.json"
CANONICAL_SHA256 = "01e2363d1d45e3593def99e538761bd8424fdd962faa12576559733a11964672"
FILE_SHA256 = "eba6fb0732ec26996a0c63bb679a899b71dc2009474502e59048dd67d764f0c7"
SLOTS_SHA256 = "58365e68525d521740534fd9fb3f8ef8fd05629b7ab28f392bf17e454b91ad53"
FIELDS = ("task_pair", "condition", "seed_index", "expected_episode_seed",
          "model_id", "role", "ordinal")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pretty(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def turn_zero(seed):
    return int.from_bytes(hashlib.sha256(compact(
        ["align-p4-turn-v1", seed, 0])).digest()[:8], "big")


def encode_manifest(windows):
    """Schema adapter; never accepts the target manifest as an input."""
    encoded = []
    for window in windows:
        name = window["window_id"]
        cohort = "selection" if name == "W1" else "calibration" if name[0] == "C" else "test"
        members = []
        for row in window["slots"]:
            role = row["role"]
            if name == "W1":
                pool = "selection"
            elif role == "anchor":
                pool = "anchor"
            elif role.startswith("sentinel_"):
                pool = "sentinel"
            elif cohort == "calibration" and role == "held_out_sabotage":
                pool = "known_h"
            else:
                pool = cohort
            member = dict(ordinal=row["ordinal"], pair=row["task_pair"],
                          condition=row["condition"], seed_index=row["seed_index"],
                          episode_seed=row["expected_episode_seed"],
                          model_id=row["model_id"], pool=pool,
                          turn_seed_0=turn_zero(row["expected_episode_seed"]))
            if name == "W1":
                member["role"] = role
            members.append(member)
        entry = dict(id=name, role=cohort, aliases=["D" + name[1:]] if name[0] == "C" else [],
                     members=members)
        if name != "W1":
            entry["midpoint_after_ordinal"] = 11
        encoded.append(entry)
    return dict(
        schema="joulewise.align_v4.series.v1",
        authority="RUN_STATE 226 R15",
        status="FROZEN_PER_RUN_STATE_226_R15_PENDING_PAIRED_SEED_CHECK",
        d_mapping="alias_calibration", test_windows=3,
        test_shape="v4: 14 benign + 2 sabotage; no v5 attacks or physical controls",
        seed_law="align-p4-v1", turn_seed_law="align-p4-turn-v1",
        seed_allocation=dict(
            held_out_start=2, reserved=[1, *range(91, 100)],
            order="per pair, kit order: window order then ordinal; distinct indices",
            zero_capture_rearm="reuses the same seeds"),
        calibration=dict(counted_windows=8, benign_per_pair_per_window=7,
                         minimum_eligible_per_pair=39, replacements=0, fence_from="C6"),
        sentinel=dict(source="W1:5", late_replay_of=5,
                      extra_on_inconclusive=2, escalated_ceiling_s=62400),
        open_rulings=["paired seed check of these manifest bytes before signing",
                      "placement of the two escalation sentinels (U4/U5 inconclusive)"],
        order=[w["window_id"] for w in windows], windows=encoded)


def differences(expected, actual, path="$"):
    """Enumerate every changed leaf, including missing/extra keys or members."""
    if type(expected) is not type(actual):
        return [dict(path=path, expected=expected, actual=actual)]
    if isinstance(expected, dict):
        rows = []
        for key in sorted(expected.keys() | actual.keys()):
            child = path + "." + key
            if key not in expected:
                rows.append(dict(path=child, expected_absent=True, actual=actual[key]))
            elif key not in actual:
                rows.append(dict(path=child, expected=expected[key], actual_absent=True))
            else:
                rows.extend(differences(expected[key], actual[key], child))
        return rows
    if isinstance(expected, list):
        rows = []
        for index in range(max(len(expected), len(actual))):
            child = f"{path}[{index}]"
            if index >= len(expected):
                rows.append(dict(path=child, expected_absent=True, actual=actual[index]))
            elif index >= len(actual):
                rows.append(dict(path=child, expected=expected[index], actual_absent=True))
            else:
                rows.extend(differences(expected[index], actual[index], child))
        return rows
    return [] if expected == actual else [dict(path=path, expected=expected, actual=actual)]


def actual_slot(member, name):
    if name == "W1":
        role = member.get("role")
    else:
        pool = member.get("pool")
        if pool == "anchor":
            role = "anchor"
        elif pool == "sentinel":
            role = {5: "sentinel_early", 22: "sentinel_late"}.get(member.get("ordinal"),
                                                                 "unexpected_sentinel")
        elif pool == "known_h":
            role = "held_out_sabotage"
        elif pool in ("calibration", "test"):
            role = "held_out_" + str(member.get("condition"))
        else:
            role = "unexpected_pool:" + str(pool)
    return dict(task_pair=member.get("pair"), condition=member.get("condition"),
                seed_index=member.get("seed_index"),
                expected_episode_seed=member.get("episode_seed"),
                model_id=member.get("model_id"), role=role, ordinal=member.get("ordinal"))


def slot_comparison(expected_windows, actual):
    normalized = [dict(window_id=w.get("id"),
                       slots=[actual_slot(m, w.get("id")) for m in w.get("members", [])])
                  for w in actual.get("windows", [])]
    return differences(expected_windows, normalized)


def anchor_evidence():
    """Check real config bytes against original repository objects, not weights."""
    rows = []
    for ordinal in range(1, 5):
        filename = f"align-pilot-v3-episodes-a-e{ordinal:02}.json"
        source = "configs/campaigns/align_pilot_v3/stages/episodes-a/" + filename
        original = subprocess.run(["git", "show", "83e2dac59:" + source],
                                  cwd=ROOT, check=True, capture_output=True).stdout
        current = (KIT / "stages/episodes-a" / filename).read_bytes()
        rows.append(dict(ordinal=ordinal, source="83e2dac59:" + source,
                         original_sha256=sha(original), kit_sha256=sha(current),
                         byte_identical=original == current))
    return rows


def check():
    blind = (HERE / "independent_slots.json").read_bytes()
    windows = derive()
    expected = encode_manifest(windows)
    generated_raw = pretty(expected)
    target_raw = TARGET.read_bytes()
    actual = json.loads(target_raw)
    slots = slot_comparison(windows, actual)
    full = differences(expected, actual)
    anchors = anchor_evidence()
    checks = dict(
        precomparison_snapshot_unchanged=sha(blind) == SLOTS_SHA256,
        rederived_slots_equal_precomparison_snapshot=pretty(windows) == blind,
        all_slots_match=not slots,
        every_manifest_leaf_matches=not full,
        original_anchor_bytes_match=all(r["byte_identical"] for r in anchors),
        canonical_hash_matches_brief=sha(compact(actual)) == CANONICAL_SHA256,
        rederived_canonical_hash_matches_brief=sha(compact(expected)) == CANONICAL_SHA256,
        file_hash_matches_brief=sha(target_raw) == FILE_SHA256,
        rederived_file_hash_matches_brief=sha(generated_raw) == FILE_SHA256,
        byte_identical_manifest=generated_raw == target_raw)
    receipt = dict(
        verdict="MATCH" if all(checks.values()) else "MISMATCH", checks=checks,
        independent_slots_sha256=sha(blind),
        expected_canonical_sha256=sha(compact(expected)),
        actual_canonical_sha256=sha(compact(actual)),
        expected_file_sha256=sha(generated_raw), actual_file_sha256=sha(target_raw),
        slot_count=sum(len(w["slots"]) for w in windows),
        fields_compared_per_slot=list(FIELDS),
        role_encoding="W1: role; C/T: pool plus sentinel ordinal and held-out condition",
        slot_differences=slots, manifest_differences=full, original_anchors=anchors,
        windows=[dict(id=w["window_id"], members=len(w["slots"])) for w in windows],
        provenance=dict(
            allocation="derive_slots.py and independent_slots.json committed before target inspection",
            wrapper="literal schema/metadata spelling inspected from target JSON after allocation freeze",
            series_builder="never read or imported by this checker"))
    return generated_raw, receipt


if __name__ == "__main__":
    generated, receipt = check()
    if sys.argv[1:] == ["--write"]:
        (HERE / "series_manifest.json").write_bytes(generated)
        (HERE / "comparison.json").write_bytes(pretty(receipt))
    elif sys.argv[1:]:
        raise SystemExit("usage: check_manifest.py [--write]")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    raise SystemExit(0 if receipt["verdict"] == "MATCH" else 1)
