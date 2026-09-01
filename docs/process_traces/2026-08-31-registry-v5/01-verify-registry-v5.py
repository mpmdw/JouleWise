#!/usr/bin/env python3
"""POINT-IN-TIME MIGRATION VERIFIER (2026-08-31): validates the _v4->_v5
regeneration diff against the pre-regeneration registry state. It is custody
evidence, not a standing gate; re-running it after later registry commits
compares the wrong baseline and its historical assertions may fail.

Fail-closed census for the 2026-08-31 `_v5` registry regeneration."""

from __future__ import annotations

from collections import Counter
import hashlib
from pathlib import Path
import re
import subprocess


REGISTRY_PATH = Path("docs/paper/results-fill-registry.md")
CHECKLIST_PATH = Path("docs/paper/round7/fill-checklist.md")
DRAFT_PATH = Path("docs/paper/draft-v1.md")
DRAFT_SHA256 = "939dfa23730a22d35e02154d7aa7904f396364d55c128e6715c72b849eaf39ab"


def exact_keys(text: str) -> list[str]:
    return [
        match.group(1)
        for match in re.finditer(r"^\| `(\[.*\])` \|", text, re.MULTILINE)
    ]


def prior_key(current: str) -> str:
    return (
        current.replace(
            "_1p7B_prefill_p[PREFILL_LENGTH]", "_1p5B_prompt"
        )
        .replace("_8B_prefill_p[PREFILL_LENGTH]", "_7B_prompt")
        .replace("_1p7B_decode", "_1p5B_decode")
        .replace("_8B_decode", "_7B_decode")
        .replace("_1p7B_floor_window", "_1p5B_floor_window")
        .replace("_8B_floor_window", "_7B_floor_window")
    )


def diagnostic_rows(text: str) -> dict[str, str]:
    return {
        match.group(1): match.group(0)
        for match in re.finditer(r"^\| (DG-[0-9]+) — .*$", text, re.MULTILINE)
    }


def main() -> None:
    registry = REGISTRY_PATH.read_text(encoding="utf-8")
    checklist = CHECKLIST_PATH.read_text(encoding="utf-8")
    draft = DRAFT_PATH.read_text(encoding="utf-8")
    old_registry = subprocess.check_output(
        ["git", "show", "HEAD:docs/paper/results-fill-registry.md"], text=True
    )

    draft_sha256 = hashlib.sha256(DRAFT_PATH.read_bytes()).hexdigest()
    assert draft_sha256 == DRAFT_SHA256
    assert len(draft.splitlines()) == 672
    pending = re.findall(r"\[PENDING[^]]*\]", draft)
    family = re.findall(
        r"\[(?:PENDING[^]]*|RESULT PENDING ISSUED ARTIFACTS[^]]*|"
        r"REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST)\]",
        draft,
    )
    assert (len(pending), sum(2 if "," in value else 1 for value in pending)) == (
        34,
        36,
    )
    assert (
        len(family),
        sum(2 if value.startswith("[PENDING,") else 1 for value in family),
    ) == (37, 39)
    assert len(re.findall(r"\[\[NEEDS-VALUE:", draft)) == 2

    old_keys = exact_keys(old_registry)
    new_keys = exact_keys(registry)
    assert len(old_keys) == len(set(old_keys)) == 109
    assert len(new_keys) == len(set(new_keys)) == 126
    rename_pairs = [
        (prior_key(current), current)
        for current in new_keys
        if prior_key(current) != current and prior_key(current) in old_keys
    ]
    renamed_new = {current for _, current in rename_pairs}
    added = [
        current
        for current in new_keys
        if current not in old_keys and current not in renamed_new
    ]
    assert len(rename_pairs) == 66
    assert len(added) == 17
    assert len(set(old_keys) & set(new_keys)) == 43
    assert not [
        key for key in new_keys if re.search(r"1p5B|_7B(?:_|\])", key)
    ]

    independent_r = [
        key for key in new_keys if re.match(r"^\[R_(?:1p7B|8B)_", key)
    ]
    common_mode_r = [
        key for key in new_keys if re.match(r"^\[R_cm_(?:1p7B|8B)_", key)
    ]
    assert len(independent_r) == 8
    assert len(common_mode_r) == 8
    assert sum("[PREFILL_LENGTH]" in key for key in new_keys) == 41
    for line in registry.splitlines():
        if line.startswith("| `") and "[PREFILL_LENGTH]" in line:
            assert "UNRESOLVED-UNTIL-G2A" in line
    assert sum(
        line.startswith("| ") and "UNRESOLVED-UNTIL-G2A" in line
        for line in registry.splitlines()
    ) == 59

    marker_pattern = (
        r"^\| ((?:DS|PG|DG)-[0-9]+[a-z]?) — .*\["
        r"(?:PENDING|RESULT PENDING ISSUED ARTIFACTS|"
        r"REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST)"
    )
    registry_rows = re.findall(marker_pattern, registry, re.MULTILINE)
    assert len(registry_rows) == len(set(registry_rows)) == 37
    assert "PG-03" not in registry_rows
    assert (
        len(
            re.findall(
                r"^\| (?:DS|PG|DG)-[0-9]+[a-z]? — .*\[PENDING",
                registry,
                re.MULTILINE,
            )
        )
        == 34
    )

    expected = [
        "DS-01",
        "DS-08a",
        *[f"DS-{number:02d}" for number in range(9, 35)],
        "PG-01",
        "PG-02",
        *[f"PG-{number:02d}" for number in range(4, 9)],
        "DG-071",
        "DG-075",
    ]
    placed = Counter(
        re.findall(
            r"^\| ((?:DS|PG|DG)-[0-9]+[a-z]?) \|",
            checklist,
            re.MULTILINE,
        )
    )
    assert len(expected) == 37
    assert set(placed) == set(expected)
    assert all(placed[row] == 1 for row in expected)

    ratio_keys = [
        key
        for key in new_keys
        if re.match(r"^\[(?:TERM_A|TERM_B|R(?:_cm)?)_(?:1p7B|8B)_", key)
    ]
    checklist_ratio = set(
        re.findall(
            r"^\| `((?:TERM_A|TERM_B|R(?:_cm)?)_[^`]+)` \|",
            checklist,
            re.MULTILINE,
        )
    )
    assert len(ratio_keys) == 32
    assert checklist_ratio == {key[1:-1] for key in ratio_keys}

    old_diagnostics = diagnostic_rows(old_registry)
    new_diagnostics = diagnostic_rows(registry)
    assert set(old_diagnostics) == set(new_diagnostics)
    assert {
        row
        for row in old_diagnostics
        if old_diagnostics[row] != new_diagnostics[row]
    } == {"DG-071", "DG-075"}
    for row in ("DG-071", "DG-075"):
        assert (
        "PROPOSED-FOR-RATIFICATION / VALUE_UNISSUED" in new_diagnostics[row]
        or (
            "RATIFIED-STATISTIC" in new_diagnostics[row]
            and "VALUE_UNISSUED" in new_diagnostics[row]
        )
    )
    assert re.search(
        r"^\| `\[B_decode_claim_J\]` .*\| STOP_FILL \|",
        registry,
        re.MULTILINE,
    )

    print(f"DRAFT_SHA256 {draft_sha256}")
    print("DRAFT_LINES 672")
    print("DRAFT_CENSUS literal=34/36 family=37/39 needs_value=2")
    print("KEY_CENSUS old=109 new=126 retained=43 renamed=66 added=17")
    print("UNRESOLVED exact_keys=41 all_registry_rows=59")
    print("MARKER_ROWS registry=37/37 checklist=37/37 semantic_slots=39")
    print("DOMINANCE_ROWS checklist=32/32")
    print("DIAGNOSTIC_PRESERVATION changed_only=DG-071,DG-075")
    print("B_DECODE_CLAIM_J STOP_FILL")


if __name__ == "__main__":
    main()
