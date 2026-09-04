#!/usr/bin/env python3
"""Check first-use glosses and numeric provenance in the runnable paper block."""

from __future__ import annotations

import re
import json
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs/paper/draft-v2-skeleton.md"
REGISTRY = ROOT / "docs/paper/results-fill-registry.md"
WORKED_EXAMPLE = (
    ROOT
    / "docs/process_traces/2026-09-04-fanout/transfer-fiducial/worked-example.json"
)
BEGIN = "<!-- BEGIN TRANSFER-FIDUCIAL-RUNNABLE -->"
END = "<!-- END TRANSFER-FIDUCIAL-RUNNABLE -->"

TERM_RULES = {
    "diagnostic protocol": "study that tests the timing method",
    "small-model identity": "the exact model name, revision",
    "output yield": "the moment the generator returns its first output item",
    "command stamp": "a paired wall-clock and monotonic-clock reading",
    "injected clock": "the clock object also used for event times",
    "synchronization function": "which waits for queued work to finish",
    "transport-edge test": "covering drain, sleep, and restart",
    "fitted-edge problem": "the existing detector fits positive power pulses",
    "residual interval": "an allowed signed residual interval",
    "edge radius": "defines its edge radius as",
    "transfer residual": "the pre-registered transfer residual",
}

NUMBER_WORD_RE = re.compile(
    r"(?<![\w.])(?:\d+(?:\.\d+)?|one|two|first|second|ten)(?!\w)",
    re.IGNORECASE,
)


def prose_sentences() -> list[str]:
    text = PAPER.read_text(encoding="utf-8")
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise SystemExit("transfer_fiducial_prose_markers_not_exactly_once")
    block = text.split(BEGIN, 1)[1].split(END, 1)[0]
    block = re.sub(r"<!--.*?-->", " ", block, flags=re.DOTALL)
    block = re.sub(r"\s+", " ", block).strip()
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z])", block)
        if sentence.strip()
    ]


def validate_worked_example() -> None:
    artifact = json.loads(
        WORKED_EXAMPLE.read_text(encoding="utf-8"), parse_float=Decimal
    )
    inputs = artifact["example_inputs"]
    outputs = artifact["example_outputs"]
    anchor = inputs["effective_clock_anchor_bound_s"]
    falling = max(
        abs(value) for value in inputs["falling_edge_residual_interval_s"]
    ) + anchor
    rising = max(
        abs(value) for value in inputs["rising_edge_residual_interval_s"]
    ) + anchor
    residual = max(falling, rising)
    if outputs["falling_edge_radius_s"] != falling:
        raise SystemExit("worked_example_falling_radius_mismatch")
    if outputs["rising_edge_radius_s"] != rising:
        raise SystemExit("worked_example_rising_radius_mismatch")
    if outputs["residual_transfer_s"] != residual:
        raise SystemExit("worked_example_transfer_residual_mismatch")
    bound = artifact["bound_source"]["value_s"]
    expected_verdict = "supported" if residual <= bound else "exceeds_bound"
    if outputs["verdict"] != expected_verdict:
        raise SystemExit("worked_example_verdict_mismatch")
    registry = REGISTRY.read_text(encoding="utf-8")
    if (
        f"| {artifact['bound_source']['registry_row']} —" not in registry
        or str(bound) not in registry
    ):
        raise SystemExit("worked_example_bound_registry_mismatch")


def number_source(sentence: str) -> str:
    lowered = sentence.lower()
    if not NUMBER_WORD_RE.search(sentence):
        return "not numeric"
    if "worked arithmetic" in lowered or "their radii" in lowered:
        return "issued worked-example artifact"
    if "0.022 s; because" in lowered:
        return "issued worked-example artifact and bound registry"
    if "ten otherwise" in lowered:
        return "registered task ruling and campaign-bound generator"
    return "held implementation branch and executable source"


def main() -> int:
    validate_worked_example()
    sentences = prose_sentences()
    if not sentences:
        raise SystemExit("transfer_fiducial_prose_block_empty")

    first_use_by_sentence: dict[int, list[str]] = {}
    lowered_sentences = [sentence.lower() for sentence in sentences]
    for term, gloss in TERM_RULES.items():
        indexes = [
            index
            for index, sentence in enumerate(lowered_sentences)
            if term in sentence
        ]
        if not indexes:
            raise SystemExit(f"first_use_term_missing:{term}")
        first = indexes[0]
        if gloss not in lowered_sentences[first]:
            raise SystemExit(f"first_use_gloss_missing:{term}:sentence_{first + 1}")
        first_use_by_sentence.setdefault(first, []).append(term)

    print("| Sentence | Opening words | New technical term(s) | First-use test | Number source |")
    print("|---|---|---|---|---|")
    for index, sentence in enumerate(sentences):
        terms = ", ".join(sorted(first_use_by_sentence.get(index, []))) or "none"
        opening = " ".join(sentence.replace("|", "\\|").split()[:10])
        if len(sentence.split()) > 10:
            opening += "…"
        source = number_source(sentence)
        if NUMBER_WORD_RE.search(sentence) and source == "not numeric":
            raise SystemExit(f"number_source_missing:sentence_{index + 1}")
        print(f"| S{index + 1:02d} | {opening} | {terms} | PASS | {source} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
