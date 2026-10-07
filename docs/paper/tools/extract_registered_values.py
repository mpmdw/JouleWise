#!/usr/bin/env python3
"""Build the table of registered design values that Paper B's text cites.

Why this exists.  Paper B describes the design of measurement block 5 before
any of its data exists: settles, thresholds, member counts, deadlines, the
flag catalog.  Each of those numbers already lives in a committed place (a
sizing output, a catalog, a module constant, a member configuration, a
fenced block of the registration).  A number typed into prose from memory
can be wrong, and it goes stale silently when the registration is revised.
So no author types one: this program reads every value from its committed
source and writes them, with the file and key each came from, into

    docs/paper/paper-b/registered-values.json

and ``tests/test_paper_b_registered_values.py`` regenerates that file and
compares bytes.  When a source value changes, the test fails and names the
entries that moved; the text that cites them is then re-synced.

What one entry holds.

    "chain.settle_s": {
      "value": 60,
      "unit": "s",
      "what": "Settle: the sleep before ...",
      "source": {"kind": "python", "file": "joulewise/b5/chain.py", "key": "SETTLE_S"},
      "also": [{"kind": "json", "file": ".../sizing_b5.json",
                "key": "/terms/settle_s/seconds", "value": 60}]
    }

``source`` is the one place the value was read from.  ``also`` lists other
committed places that state the same quantity, each with the value found
there.  If any of them differs from ``value`` the entry's id is listed under
the document's ``disagreements`` (the file is still written, so the
difference can be seen; the test requires the list to be empty).

Seven kinds of source.

``json``           the value at a JSON pointer (RFC 6901) of a JSON file.
``markdown-json``  the value at a JSON pointer inside the first fenced
                   ``json`` block under a named heading of a Markdown file.
                   The registration states its arm thresholds (section 4.3)
                   and harvest thresholds (section 6.9) this way, and the
                   window plan and the harvest read those same blocks.
``python``         the value a module constant has when the module is
                   imported.  The import runs in a child interpreter whose
                   import path starts at the repository root given, so a
                   scratch copy of the tree can be read without touching
                   this process, and the child proves each module was loaded
                   from that root.
``derived``        a count, sum or list computed from one JSON file by a
                   named rule (``RULES`` below); the entry's key states the
                   rule in words.
``config-set``     the one value that every member configuration under the
                   named directories has at a JSON pointer, or the number of
                   those configurations.  A member configuration is a
                   ``.json`` file, anywhere under the directory, whose
                   document is an object with both ``run_id`` and
                   ``sampling``.  If two configurations differ the
                   extraction fails: the table never prints "the" value of
                   a setting the packs do not share.
``markdown-line``  the text between ``Status: **`` and ``**`` on a
                   document's status line.
``markdown-table`` the whole number that opens one cell of a Markdown table,
                   before a named unit ("31,584 s (8.8 h)" with the unit "s"
                   gives 31584).  The table is the one table of the file
                   whose header row has the named column; the row is the one
                   row of it whose first cell is the named label.  The
                   registration states each pack's expected chain length
                   only this way (the table of its sizing section); the
                   sizing output holds the worst-case span and deadline and
                   has no key for the expected length.

The output carries no digest and no commit id on purpose: its bytes change
only when a value, a key or a description changes.

When the registration is revised or sealed.  The status lines and several
values are read from files that a revision or the seal rewrites, so on that
commit the byte comparison fails by design.  On the tree that holds the new
registration, sizing output, identity pins and sealed inventory, run this
program with ``--write`` and commit the regenerated table in the same pull
request.  The failure message lists the entries that moved; that list is the
paper text to re-sync.  If the program stops instead (exit 2), a source it
reads was renamed or reshaped: the message names it, and the entry of the
manifest below that reads it is what to correct.

Usage (from the repository root, any Python 3.11+; no third-party package):

    python3 -B docs/paper/tools/extract_registered_values.py            # same as --check
    python3 -B docs/paper/tools/extract_registered_values.py --write
    python3 -B docs/paper/tools/extract_registered_values.py --get chain.settle_s
    python3 -B docs/paper/tools/extract_registered_values.py --list

To cite a value in paper text, put ``<!-- rv: <id> -->`` beside the number.

This program reads only.  It writes one file, and only with ``--write``.
It never reads a bundle, an energy or any harvest output.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
TOOL_RELATIVE = "docs/paper/tools/extract_registered_values.py"
OUTPUT_RELATIVE = "docs/paper/paper-b/registered-values.json"
SCHEMA = "joulewise.paper_b_registered_values.v1"
CHILD_TIMEOUT_S = 300

CAMPAIGN = "configs/campaigns/v5_claim_25g83"
SIZING = f"{CAMPAIGN}/sizing_b5.json"
CATALOG = f"{CAMPAIGN}/flag_catalog.json"
PINS = f"{CAMPAIGN}/identity_pins.json"
INVENTORY = f"{CAMPAIGN}/sealed_inventory.json"
REGISTRATION = f"{CAMPAIGN}/registration_block5.md"
ANALYSIS_PLAN = f"{CAMPAIGN}/analysis_plan_block5.md"
POLICY = "configs/campaign_policies/quiet_mac_p2_b5.json"
ARM_HEADING = "Registered thresholds"      # registration section 4.3
HARVEST_HEADING = "Harvest thresholds"     # registration section 6.9
# Two columns of the table in registration section 5.5 (Sizing), one row per pack.  The first figure is built
# from timings measured in measurement block 3; the second subtracts the savings of later changes.
EXPECTED_MEASURED_COLUMN = "Expected chain, block-3 basis"
EXPECTED_PROJECTED_COLUMN = "Expected chain, projected"

ALPHA_DIR = "configs/campaigns/d117_floor_qwen3-1p7b_v5"
BETA_DIR = "configs/campaigns/d117_floor_qwen3-8b_v5"
GAMMA_DIR = "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"
PACK_DIRS = {"ALPHA": ALPHA_DIR, "BETA": BETA_DIR, "GAMMA": GAMMA_DIR}
CORPUS_DIR = "configs/campaigns/neg8_reference_corpus_v5"
REFERENCES_DIR = "configs/campaigns/window_references_v5"
SPARES_DIR = "configs/campaigns/window_reference_spares_v5"
INTERIOR_DIR = "configs/campaigns/gamma_interior_references_v5"
SCIENCE_DIRS = (ALPHA_DIR, BETA_DIR, GAMMA_DIR)
REFERENCE_DIRS = (CORPUS_DIR, REFERENCES_DIR, SPARES_DIR, INTERIOR_DIR)
PROFILE = "/workload_profile/name"
DECODE_PROFILE = "real_prompts_v1_chat_rendered"
PREFILL_PROFILE = "df_ph_prefill_p2048_candidate"

HAZ = "joulewise/hazards"
CHAIN_PY = "joulewise/b5/chain.py"
PLAN_PY = "joulewise/b5/plan.py"
DRIVER_PY = "joulewise/b5/driver.py"
HARVEST_PY = "joulewise/b5/harvest.py"
SPARES_PY = "joulewise/b5/reference_spares.py"
WHOLE_WINDOW_PY = "joulewise/whole_window.py"
RUN_CAMPAIGN_PY = "scripts/run_campaign.py"
ANCHOR_PY = "joulewise/uncertainty_evidence.py"
REDUCE_PY = "joulewise/reduce.py"
KERNEL_CLOCK_PY = "joulewise/kernel_clock.py"

PACK_LABELS = ("ALPHA", "BETA", "GAMMA")
UNITS = frozenset({
    "s", "ms", "ns", "ppm", "mA", "W", "K", "bytes", "CPU-s/s", "count", "fraction", "level",
    "exit code", "text", "sha256", "boolean", "list", "tokens", "bits", "units per ppm", "number", "Hz",
})


class ExtractionError(ValueError):
    """A source could not be read as the manifest says; nothing was written."""


# --------------------------------------------------------------------------
# Terms, built in the order the descriptions use them.  Written into the
# output ahead of the values so that no description uses an unbuilt word.

GLOSSARY: tuple[tuple[str, str], ...] = (
    ("machine",
     "One Apple M3 Max laptop on mains power. Every value in this table concerns that one machine."),
    ("sampler, power record",
     "The sampler is the macOS program powermetrics, asked for one power record every 100 ms. A power record "
     "states the average power of the processor rails (CPU, GPU and ANE together) over its own time span."),
    ("member",
     "One run of one inference request in its own process. In order: an idle baseline (the sampler records the "
     "idle machine), a warm-up (one untimed generation of the same request), the measured request, then "
     "cleanup."),
    ("phase, phase energy",
     "A phase is a named, timestamped part of a member's measured request. In the prefill phase the model reads "
     "the whole prompt and computes the first output token; in the decode phase it produces the remaining output "
     "tokens. A phase's energy adds, over the power records, each record's power times the overlap of its time "
     "span with the phase."),
    ("workload; decode workload, prefill workload",
     "A workload is one fixed request. Two are measured. The decode workload has a short prompt and a long "
     "output of fixed length; its decode phase is the one reported. The prefill workload has a long prompt; its "
     "prefill phase is the one reported."),
    ("sampler stream",
     "The one continuous sampler process that covers a member from the start of its idle baseline to the end of "
     "its measured request."),
    ("idle baseline, idle admission",
     "The idle baseline is the stretch at the start of a member in which the sampler records the idle machine. "
     "Idle admission is the test that the machine was quiet during that baseline. A refused baseline is retried "
     "once; a second refusal aborts the member."),
    ("member configuration",
     "The committed file that fixes one member: its model, its prompt, its output length and its sampler "
     "settings."),
    ("stage, collection stage",
     "A stage is one step of a run. A collection stage is an ordered list of members that one command runs "
     "together; each other stage does one step that runs no member."),
    ("settle",
     "A fixed sleep before a stage, so that the machine is back at idle when the stage starts."),
    ("cooldown",
     "The wait between two members of one stage. During it the idle machine's power is read in short readings; "
     "the next member starts at the first reading at or below a bound set from the previous member's idle "
     "baseline, or when a cap is reached."),
    ("pack; ALPHA, BETA, GAMMA",
     "A pack is one frozen set of stages and member configurations, run from its first stage to its last as a "
     "whole. There are three, named here by their repository labels: ALPHA measures Qwen3-1.7B, BETA measures "
     "Qwen3-8B, and GAMMA runs both models side by side to measure the difference between them."),
    ("chain",
     "The script that runs a pack's stages in order."),
    ("window, attempt",
     "A window is the stretch of machine time one run of one pack occupies, from its scheduled start to the exit "
     "of its chain. An attempt is one such run. The paper calls the windows of ALPHA, BETA and GAMMA the 1.7B "
     "window, the 8B window and the contrast window."),
    ("measurement block, registration, sealed",
     "A measurement block is a set of windows planned together; this table belongs to measurement block 5. Its "
     "registration is the document, fixed before any of its data exists, that states what is run, what stops a "
     "window and what removes data. The registration binds once it is sealed, that is, declared final after an "
     "independent review."),
    ("window plan",
     "The file written for one attempt that fixes its pack, its output directories and its thresholds."),
    ("calibration capture, pulse timing bound, bracket, bracket reservation",
     "A calibration capture (the paper's pulse calibration) drives the GPU through commanded on/off pulses; the "
     "largest timing error it finds between commanded and observed pulse edges is its pulse timing bound. One "
     "capture is taken before the window's members (pre) and one after them (post); the pair is the window's "
     "bracket. Before the pre capture the chain makes the bracket reservation: it opens an entry, in the running "
     "record of calibration captures, that names the window and against which both captures are recorded."),
    ("science member, repeat, quad, side, unit",
     "A science member is a member whose energy enters a reported number. Science members run alone (an absolute "
     "repeat) or in groups of four in the order A, B, B, A (a quad, whose two sides are A and B). A unit is one "
     "repeat or one quad."),
    ("reference member, reference corpus, triplet, midpoint reference, spare, reference drift check, "
     "reference drift bound",
     "A reference member is a member of one fixed reference workload, run to detect drift of the instrument "
     "across a window. Each window runs twelve at its start (the reference corpus; its repository label is "
     "NEG-8 corpus, an inherited name, not an abbreviation), three more before the stages of science members "
     "(the start triplet), one at the window's midpoint, and three after the stages of science members (the end "
     "triplet). A spare is a pre-registered extra copy of a reference, run only when a reference of its stage "
     "was lost. A reference that did not run, did not succeed or was removed is lost; the others survive. The "
     "reference drift check compares the mean energy of the surviving end references with that of the surviving "
     "start references, and passes when they differ by no more than the reference drift bound, a limit derived "
     "from the energies of the reference corpus."),
    ("identity unit",
     "A group of members that must all have run one model under one runtime configuration."),
    ("hazard, hazard check, arm, dwell",
     "A hazard is a physical condition of the machine that would corrupt a measured energy: the clock, the "
     "battery, thermal pressure, a competing process, free disk, or the sampler itself. A hazard check is the "
     "program that measures one hazard directly. The arm is the sequence of hazard checks run just before a "
     "window; it either lets the chain start or refuses. The dwell is the part of the arm that watches for "
     "competing processes and clock steps over consecutive intervals."),
    ("agent session, agent census",
     "An agent session is a running AI coding-assistant session on the machine. Its work would compete with a "
     "member for the processor, so the arm lists such sessions (the agent census) and refuses while one is "
     "alive."),
    ("clock anchor, frequency word, residual",
     "The clock anchor is wall-clock time minus the raw hardware counter, read in process. The frequency word "
     "is the kernel's stored rate correction for the wall clock, in parts per million (ppm). The residual is the "
     "anchor's movement minus the frequency word times the elapsed time; a clock step makes it jump."),
    ("half-width, member clock bound",
     "Each power record carries the sampler's own time label, while a member's phase edges are stamped on the "
     "machine's clocks. Placing the records against the edges needs the offset between the two time bases, which "
     "the records fix only within a range; half the width of that range is the half-width. The member clock "
     "bound is the upper limit on the error of that placement: the half-width, plus the change over the sampler "
     "stream of the difference between wall-clock time and the machine's steadily counting clock, plus a small "
     "fixed allowance."),
    ("frequency gate",
     "The arm's test, made before any member runs, that the clock's steady drift cannot push a member clock "
     "bound past its limit: a half-width term, plus (the size of the frequency word plus a margin) times the "
     "longest sampler stream, must not exceed the limit."),
    ("registry, SMC",
     "Two sources of battery evidence. The registry is the operating system's record of the battery, "
     "republished about once a minute; it gives the battery's state. The SMC (System Management Controller) is "
     "the power-management chip; it gives the battery current about once a second."),
    ("monitor",
     "A background process that records the hazards through the whole window."),
    ("driver",
     "The program that runs the arm, starts the monitor, launches the chain, and can stop the chain from "
     "outside."),
    ("flag, flag catalog, effect",
     "A flag is one recorded fact about a window, stage, quad or member, named by a code. The flag catalog gives "
     "each code exactly one effect: EXCLUDE_MEMBER (remove the member from every number it feeds), "
     "EXCLUDE_WINDOW (remove the window: it can support no claim) or DISCLOSE (record and report; remove "
     "nothing)."),
    ("harvest",
     "The program run after the chain exits. It re-derives the checks from the stored bytes and writes the "
     "flags."),
    ("programmed span, member allowance, window deadline",
     "The programmed span is the chain's length if every member took its longest allowed path; the time charged "
     "for one member on that path is its member allowance. The window deadline, measured from the scheduled "
     "start, is the programmed span plus the arm's allowance, rounded up to a whole minute. The programmed span "
     "and the window deadline are worst cases, not the length a window is expected to have: the driver stops a "
     "chain that is still running at the window deadline, and a chain that exits sooner ends its window when it "
     "exits."),
    ("expected chain length",
     "The length a pack's chain is expected to have when its members take their usual time and no spare runs. "
     "The registration states two planning figures for each pack: a slower one built from timings measured in "
     "an earlier measurement block, and a faster one that subtracts the time that changes made to the procedure "
     "since then are expected to save. Each is a third of the pack's window deadline or less, and nothing stops "
     "a chain at either. The arm of the next window starts once a chain has exited and the harvest has run, not "
     "at the window deadline; so the expected chain lengths, not the window deadlines, set how soon one window "
     "can follow another."),
)


# --------------------------------------------------------------------------
# References to sources


@dataclass(frozen=True)
class Ref:
    """One place a value is read from."""

    kind: str                              # json | markdown-json | python | derived | config-set |
    #                                        markdown-line | markdown-table
    file: str                              # repository-relative path (config-set: its directories)
    key: str                               # as printed in the output
    pointer: tuple[str | int, ...] = ()    # json / markdown-json / config-set tokens; python index path
    symbol: str = ""                       # python
    heading: str = ""                      # markdown-json
    rule: str = ""                         # derived; config-set: "common" or "count"
    args: tuple[Any, ...] = ()             # derived; markdown-table: (column, row, unit)
    dirs: tuple[str, ...] = ()             # config-set
    where: tuple[str, Any] | None = None   # config-set: (pointer, value) a configuration must have


@dataclass(frozen=True)
class Entry:
    id: str
    ref: Ref
    unit: str
    what: str
    also: tuple[Ref, ...] = ()


def pointer_tokens(pointer: str) -> tuple[str, ...]:
    """Split an RFC 6901 JSON pointer into its tokens ("" is the whole document)."""

    if pointer == "":
        return ()
    if not pointer.startswith("/"):
        raise ExtractionError(f"not a JSON pointer: {pointer!r}")
    return tuple(token.replace("~1", "/").replace("~0", "~") for token in pointer[1:].split("/"))


def J(file: str, pointer: str) -> Ref:
    return Ref("json", file, pointer, pointer=pointer_tokens(pointer))


def F(file: str, heading: str, pointer: str) -> Ref:
    return Ref("markdown-json", file, f'json block under the heading "{heading}": {pointer}',
               pointer=pointer_tokens(pointer), heading=heading)


def P(file: str, symbol: str, *path: str | int) -> Ref:
    key = symbol + "".join(f"[{json.dumps(step)}]" for step in path)
    return Ref("python", file, key, pointer=tuple(path), symbol=symbol)


def D(file: str, rule: str, *args: Any) -> Ref:
    if rule not in RULES:
        raise ExtractionError(f"unknown rule {rule!r}")
    _, template, value_positions = RULES[rule]
    shown = [json.dumps(arg) if index in value_positions else arg for index, arg in enumerate(args)]
    return Ref("derived", file, template.format(*shown), rule=rule, args=tuple(args))


def L(file: str) -> Ref:
    return Ref("markdown-line", file, 'the text between "Status: **" and "**" on the status line')


def T(file: str, column: str, row: str, unit: str) -> Ref:
    return Ref("markdown-table", file,
               f'the table with the column "{column}": the row "{row}", the whole number before " {unit}"',
               args=(column, row, unit))


def _config_set(dirs: Sequence[str] | str, where: tuple[str, Any] | None) -> tuple[tuple[str, ...], str]:
    dirs = (dirs,) if isinstance(dirs, str) else tuple(dirs)
    scope = "every member configuration under this directory" if len(dirs) == 1 else \
        "every member configuration under these directories"
    if where is not None:
        scope += f" whose {where[0]} is {json.dumps(where[1])}"
    return dirs, scope


def C(dirs: Sequence[str] | str, pointer: str, where: tuple[str, Any] | None = None) -> Ref:
    dirs, scope = _config_set(dirs, where)
    return Ref("config-set", "; ".join(dirs), f"the one value at {pointer} of {scope}",
               pointer=pointer_tokens(pointer), rule="common", dirs=dirs, where=where)


def CN(dirs: Sequence[str] | str, where: tuple[str, Any] | None = None) -> Ref:
    dirs, scope = _config_set(dirs, where)
    return Ref("config-set", "; ".join(dirs), f"the number of files: {scope}", rule="count", dirs=dirs,
               where=where)


# --------------------------------------------------------------------------
# Reading


def walk(document: Any, tokens: Sequence[str | int], *, where: str) -> Any:
    node = document
    for token in tokens:
        if isinstance(node, Mapping):
            if token not in node:
                raise ExtractionError(f"{where}: no key {token!r}")
            node = node[token]
        elif isinstance(node, list):
            try:
                node = node[int(token)]
            except (ValueError, IndexError) as exc:
                raise ExtractionError(f"{where}: no list item {token!r}") from exc
        else:
            raise ExtractionError(f"{where}: {token!r} is below a value that is not a container")
    return node


def _members(document: Any, pointer: str, *, where: str) -> list[tuple[str, Any]]:
    """The members of the object, or the items of the list, at a pointer."""

    node = walk(document, pointer_tokens(pointer), where=where)
    if isinstance(node, Mapping):
        return [(str(key), value) for key, value in node.items()]
    if isinstance(node, list):
        return [(str(index), value) for index, value in enumerate(node)]
    raise ExtractionError(f"{where}: {pointer} is neither an object nor a list")


def _rule_count(document: Any, pointer: str, *, where: str) -> int:
    return len(_members(document, pointer, where=where))


def _rule_count_where(document: Any, pointer: str, name: str, value: Any, *, where: str) -> int:
    return sum(1 for _, member in _members(document, pointer, where=where)
               if isinstance(member, Mapping) and member.get(name) == value)


def _rule_count_where2(document: Any, pointer: str, name1: str, value1: Any, name2: str, value2: Any, *,
                       where: str) -> int:
    return sum(1 for _, member in _members(document, pointer, where=where)
               if isinstance(member, Mapping) and member.get(name1) == value1 and member.get(name2) == value2)


def _rule_keys_where(document: Any, pointer: str, name: str, value: Any, *, where: str) -> list[str]:
    return sorted(key for key, member in _members(document, pointer, where=where)
                  if isinstance(member, Mapping) and member.get(name) == value)


def _rule_distinct(document: Any, pointer: str, name: str, *, where: str) -> list[Any]:
    found = {member.get(name) for _, member in _members(document, pointer, where=where)
             if isinstance(member, Mapping)}
    return sorted(found, key=lambda item: json.dumps(item, sort_keys=True))


def _rule_sum_where(document: Any, pointer: str, total: str, name: str, value: Any, *, where: str) -> int:
    result = 0
    for _, member in _members(document, pointer, where=where):
        if isinstance(member, Mapping) and member.get(name) == value:
            amount = member.get(total)
            if isinstance(amount, bool) or not isinstance(amount, int):
                raise ExtractionError(f"{where}: {pointer}: {total!r} is not an integer where {name!r} is {value!r}")
            result += amount
    return result


def _rule_sum_nested(document: Any, pointer: str, outer: str, inner: str, *, where: str) -> int:
    result = 0
    for _, member in _members(document, pointer, where=where):
        record = member.get(outer) if isinstance(member, Mapping) else None
        if record is None:
            continue
        amount = record.get(inner) if isinstance(record, Mapping) else None
        if isinstance(amount, bool) or not isinstance(amount, int):
            raise ExtractionError(f"{where}: {pointer}: {outer}.{inner} is not an integer")
        result += amount
    return result


def _rule_value_or_zero(document: Any, pointer: str, *, where: str) -> Any:
    tokens = pointer_tokens(pointer)
    parent = walk(document, tokens[:-1], where=where)
    if not isinstance(parent, Mapping):
        raise ExtractionError(f"{where}: the parent of {pointer} is not an object")
    return parent.get(tokens[-1], 0)


def _rule_common(document: Any, pointer: str, sub: str, *, where: str) -> Any:
    values = [walk(member, pointer_tokens(sub), where=f"{where} {pointer}/{key}")
              for key, member in _members(document, pointer, where=where)]
    if not values:
        raise ExtractionError(f"{where}: {pointer} has no members")
    if any(value != values[0] or type(value) is not type(values[0]) for value in values[1:]):
        raise ExtractionError(f"{where}: the members of {pointer} do not share one value at {sub}")
    return values[0]


def _rule_stage_rows(document: Any, pointer: str, *, where: str) -> list[dict[str, Any]]:
    rows = []
    for _, stage in _members(document, pointer, where=where):
        if not isinstance(stage, Mapping):
            raise ExtractionError(f"{where}: a stage under {pointer} is not an object")
        spare = stage.get("spare_retry")
        rows.append({
            "ordinal": stage.get("ordinal"),
            "kind": stage.get("kind"),
            "stage_id": stage.get("stage_id"),
            "members": stage.get("members"),
            "science": stage.get("science"),
            "runs_root": stage.get("runs_dir_binding"),
            "reference_corpus": bool(stage.get("neg8_corpus", False)),
            "spares": spare.get("max_spares") if isinstance(spare, Mapping) else None,
        })
    return rows


def _rule_first_sentence(document: Any, pointer: str, *, where: str) -> str:
    text = walk(document, pointer_tokens(pointer), where=where)
    if not isinstance(text, str) or "." not in text:
        raise ExtractionError(f"{where}: {pointer} is not text with a full stop")
    return text.split(".", 1)[0]


# rule name -> (function, the key text printed for it, the argument positions that hold a compared value
# and are therefore printed as JSON).  "Members" are the members of a JSON object or the items of a list.
RULES: dict[str, tuple[Callable[..., Any], str, frozenset[int]]] = {
    "count": (_rule_count, "the number of members of {0}", frozenset()),
    "count_where": (_rule_count_where, 'the number of members of {0} whose "{1}" is {2}', frozenset({2})),
    "count_where2": (_rule_count_where2,
                     'the number of members of {0} whose "{1}" is {2} and whose "{3}" is {4}', frozenset({2, 4})),
    "keys_where": (_rule_keys_where, 'the keys of the members of {0} whose "{1}" is {2}, sorted',
                   frozenset({2})),
    "distinct": (_rule_distinct, 'the distinct values of "{1}" over the members of {0}, sorted', frozenset()),
    "sum_where": (_rule_sum_where, 'the sum of "{1}" over the members of {0} whose "{2}" is {3}',
                  frozenset({3})),
    "sum_nested": (_rule_sum_nested, 'the sum of "{1}.{2}" over the members of {0} that have "{1}"',
                   frozenset()),
    "value_or_zero": (_rule_value_or_zero, "{0} (0 when the key is absent)", frozenset()),
    "common": (_rule_common, "the one value every member of {0} has at {1}", frozenset()),
    "stage_rows": (_rule_stage_rows,
                   "one row per member of {0}: ordinal, kind, stage_id, members, science, "
                   "runs_dir_binding (as runs_root), neg8_corpus (as reference_corpus), "
                   "spare_retry.max_spares (as spares)",
                   frozenset()),
    "first_sentence": (_rule_first_sentence, "the text of {0} up to its first full stop", frozenset()),
}

_FENCE_RE = re.compile(r"^```json[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*$", re.MULTILINE)
_SECTION_NUMBER_RE = re.compile(r"^[0-9]+(?:\.[0-9]+)*[ \t]+")
_STATUS_RE = re.compile(r"^Status: \*\*(.+?)\*\*", re.MULTILINE | re.DOTALL)
_TABLE_LINE_RE = re.compile(r"^[ \t]*\|.*\|[ \t]*$")
_CELL_BAR_RE = re.compile(r"(?<!\\)\|")


def fenced_json_span(text: str, heading: str, *, where: str) -> tuple[int, int]:
    """The character span of the first ``json`` fence body under a heading.

    The heading is matched by its text with any leading section number
    removed ("### 4.3 Registered thresholds" matches "Registered
    thresholds"), and must occur exactly once.  The section runs to the next
    heading of any level.
    """

    matches = [match for match in _HEADING_RE.finditer(text)
               if _SECTION_NUMBER_RE.sub("", match.group(2)).strip().lower() == heading.lower()]
    if len(matches) != 1:
        raise ExtractionError(f"{where}: expected one heading {heading!r}, found {len(matches)}")
    start = matches[0].end()
    following = _HEADING_RE.search(text, start)
    end = following.start() if following else len(text)
    fence = _FENCE_RE.search(text, start, end)
    if fence is None:
        raise ExtractionError(f"{where}: no json block under the heading {heading!r}")
    return fence.start(1), fence.end(1)


def fenced_json(text: str, heading: str, *, where: str) -> Any:
    start, end = fenced_json_span(text, heading, where=where)
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError as exc:
        raise ExtractionError(f"{where}: the json block under {heading!r} does not parse: {exc}") from exc


def status_line(text: str, *, where: str) -> str:
    match = _STATUS_RE.search(text)
    if match is None:
        raise ExtractionError(f"{where}: no status line of the form 'Status: **...**'")
    return " ".join(match.group(1).split())


def _table_cells(line: str) -> list[tuple[int, int]]:
    """The character spans of a table line's cells: the text between consecutive bars."""

    bars = [match.start() for match in _CELL_BAR_RE.finditer(line)]
    return [(bars[index] + 1, bars[index + 1]) for index in range(len(bars) - 1)]


def table_number_span(text: str, column: str, row: str, unit: str, *, where: str) -> tuple[int, int]:
    """The character span of the whole number that opens one cell of a Markdown table.

    A table is a run of consecutive lines that each begin and end with a
    bar; its first line is its header row.  The table wanted is the one
    table of the text whose header row has a cell reading ``column``; the
    row wanted is the one line of it whose first cell reads ``row``.  The
    cell under the column must open with a whole number, its digits plain or
    in groups of three ("31,584"), then one space and ``unit``, as in
    "31,584 s (8.8 h)".  No such table, row or number, or more than one
    table or row, fails: the table never prints a number it had to guess at.
    """

    tables: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] | None = None
    offset = 0
    for line in text.split("\n"):
        body = line.rstrip("\r")
        if _TABLE_LINE_RE.match(body):
            if current is None:
                current = []
                tables.append(current)
            current.append((offset, body))
        else:
            current = None
        offset += len(line) + 1
    found: list[tuple[list[tuple[int, str]], list[str]]] = []
    for table in tables:
        header_body = table[0][1]
        header = [header_body[start:end].strip() for start, end in _table_cells(header_body)]
        if column in header:
            found.append((table, header))
    if len(found) != 1:
        raise ExtractionError(f"{where}: expected one table with the column {column!r}, found {len(found)}")
    table, header = found[0]
    if header.count(column) != 1:
        raise ExtractionError(f"{where}: the table's header row names the column {column!r} more than once")
    rows = []
    for line_offset, body in table[1:]:
        spans = _table_cells(body)
        if spans and body[spans[0][0]:spans[0][1]].strip() == row:
            rows.append((line_offset, body, spans))
    if len(rows) != 1:
        raise ExtractionError(f"{where}: the table with the column {column!r} has {len(rows)} rows whose first "
                              f"cell is {row!r}, expected one")
    line_offset, body, spans = rows[0]
    if len(spans) != len(header):
        raise ExtractionError(f"{where}: the row {row!r} of the table with the column {column!r} has "
                              f"{len(spans)} cells, its header row {len(header)}")
    start, end = spans[header.index(column)]
    number = re.match(r"[ \t]*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]+) " + re.escape(unit) + r"(?![A-Za-z0-9])",
                      body[start:end])
    if number is None:
        raise ExtractionError(f"{where}: the cell {body[start:end].strip()!r} (row {row!r}, column {column!r}) "
                              f"does not open with a whole number and the unit {unit!r}")
    return line_offset + start + number.start(1), line_offset + start + number.end(1)


def table_number(text: str, column: str, row: str, unit: str, *, where: str) -> int:
    start, end = table_number_span(text, column, row, unit, where=where)
    return int(text[start:end].replace(",", ""))


class Tree:
    """The repository files under one root, with optional replacement bytes for some of them.

    ``overlay`` maps a repository-relative path to bytes that stand in for
    the file on disk; the test uses it to change one source value without
    copying the tree.
    """

    def __init__(self, root: Path, overlay: Mapping[str, bytes] | None = None) -> None:
        self.root = Path(root)
        self.overlay = dict(overlay or {})

    def read(self, relative: str) -> bytes:
        if relative in self.overlay:
            return self.overlay[relative]
        try:
            return (self.root / relative).read_bytes()
        except OSError as exc:
            raise ExtractionError(f"{relative}: cannot be read ({exc})") from exc

    def json_files(self, directory: str) -> list[str]:
        """Every ``.json`` file under a directory, as sorted repository-relative paths."""

        base = self.root / directory
        if not base.is_dir():
            raise ExtractionError(f"{directory}: not a directory")
        found = {path.relative_to(self.root).as_posix() for path in base.rglob("*.json") if path.is_file()}
        found.update(path for path in self.overlay if path.startswith(directory + "/") and path.endswith(".json"))
        return sorted(found)


class Sources:
    """Parsed source files, each read once.  A ``parent`` supplies every file the tree does not overlay."""

    def __init__(self, tree: Tree, parent: "Sources | None" = None) -> None:
        self.tree = tree
        self._parent = parent
        self._text: dict[str, str] = {}
        self._json: dict[str, Any] = {}

    def _inherited(self, relative: str) -> bool:
        return self._parent is not None and relative not in self.tree.overlay

    def text(self, relative: str) -> str:
        if self._inherited(relative):
            return self._parent.text(relative)
        if relative not in self._text:
            try:
                self._text[relative] = self.tree.read(relative).decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ExtractionError(f"{relative}: not UTF-8") from exc
        return self._text[relative]

    def json(self, relative: str) -> Any:
        if self._inherited(relative):
            return self._parent.json(relative)
        if relative not in self._json:
            try:
                self._json[relative] = json.loads(self.text(relative))
            except json.JSONDecodeError as exc:
                raise ExtractionError(f"{relative}: does not parse as JSON ({exc})") from exc
        return self._json[relative]


def member_configurations(sources: Sources, dirs: Sequence[str],
                          where: tuple[str, Any] | None) -> list[tuple[str, Mapping[str, Any]]]:
    """The member configurations under the directories: (path, document), in path order."""

    found: list[tuple[str, Mapping[str, Any]]] = []
    for directory in dirs:
        for relative in sources.tree.json_files(directory):
            document = sources.json(relative)
            if not (isinstance(document, Mapping) and "run_id" in document and "sampling" in document):
                continue
            if where is not None:
                try:
                    actual = walk(document, pointer_tokens(where[0]), where=relative)
                except ExtractionError:
                    continue
                if not same_value(actual, where[1]):
                    continue
            found.append((relative, document))
    return found


def resolve_config_set(ref: Ref, sources: Sources) -> Any:
    configurations = member_configurations(sources, ref.dirs, ref.where)
    if ref.rule == "count":
        return len(configurations)
    if not configurations:
        raise ExtractionError(f"{ref.file}: no member configuration matches ({ref.key})")
    first_path, first = configurations[0]
    value = walk(first, ref.pointer, where=first_path)
    for relative, document in configurations[1:]:
        if not same_value(walk(document, ref.pointer, where=relative), value):
            raise ExtractionError(f"{relative}: differs from {first_path} ({ref.key})")
    return value


# --------------------------------------------------------------------------
# Module constants, read in a child interpreter

_CHILD = r'''
import importlib, importlib.util, json, math, sys
from collections.abc import Mapping
from pathlib import Path

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root))
requests = json.load(sys.stdin)
real_stdout, sys.stdout = sys.stdout, sys.stderr   # an import that prints must not corrupt the reply
modules = {}


def load(relative):
    if relative in modules:
        return modules[relative]
    path = (root / relative).resolve()
    parts = Path(relative).with_suffix("").parts
    if parts[0] == "joulewise":
        module = importlib.import_module(".".join(parts))
    else:
        name = "_registered_values_" + "_".join(parts)
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    origin = Path(module.__file__).resolve()
    if origin != path:
        raise SystemExit(f"{relative}: imported from {origin}, not from {path}")
    modules[relative] = module
    return module


def plain(value, where):
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise SystemExit(f"{where}: not a finite number")
        return value
    if isinstance(value, (tuple, list)):
        return [plain(item, where) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((plain(item, where) for item in value), key=lambda item: json.dumps(item, sort_keys=True))
    if isinstance(value, Mapping):
        return {str(key): plain(item, where) for key, item in value.items()}
    raise SystemExit(f"{where}: a {type(value).__name__} cannot be written as JSON")


replies = []
for request in requests:
    where = request["file"] + " " + request["symbol"]
    module = load(request["file"])
    if not hasattr(module, request["symbol"]):
        raise SystemExit(f"{where}: no such name")
    value = getattr(module, request["symbol"])
    for step in request["path"]:
        try:
            value = value[step]
        except (KeyError, IndexError, TypeError) as exc:
            raise SystemExit(f"{where}: no item {step!r}") from exc
    replies.append(plain(value, where))
json.dump(replies, real_stdout)
'''

PythonKey = tuple[str, str, tuple[str | int, ...]]


def python_key(ref: Ref) -> PythonKey:
    return (ref.file, ref.symbol, ref.pointer)


def read_python_constants(root: Path, refs: Sequence[Ref]) -> dict[PythonKey, Any]:
    """Import each module from ``root`` in a child interpreter and read the named constants."""

    wanted: list[Ref] = []
    seen: set[PythonKey] = set()
    for ref in refs:
        if ref.kind == "python" and python_key(ref) not in seen:
            seen.add(python_key(ref))
            wanted.append(ref)
    if not wanted:
        return {}
    request = json.dumps([{"file": ref.file, "symbol": ref.symbol, "path": list(ref.pointer)} for ref in wanted])
    try:
        completed = subprocess.run([sys.executable, "-B", "-I", "-c", _CHILD, str(root)], input=request,
                                   capture_output=True, text=True, cwd=str(root), timeout=CHILD_TIMEOUT_S,
                                   check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ExtractionError(f"the child interpreter could not read the module constants: {exc}") from exc
    if completed.returncode != 0:
        tail = completed.stderr.strip().splitlines()[-1] if completed.stderr.strip() else "no message"
        raise ExtractionError(f"reading module constants failed: {tail}")
    try:
        replies = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ExtractionError("the child interpreter's reply does not parse") from exc
    if not isinstance(replies, list) or len(replies) != len(wanted):
        raise ExtractionError("the child interpreter answered a different number of requests")
    return {python_key(ref): reply for ref, reply in zip(wanted, replies)}


def resolve(ref: Ref, sources: Sources, python_values: Mapping[PythonKey, Any]) -> Any:
    where = f"{ref.file} {ref.key}"
    if ref.kind == "json":
        return walk(sources.json(ref.file), ref.pointer, where=where)
    if ref.kind == "markdown-json":
        return walk(fenced_json(sources.text(ref.file), ref.heading, where=ref.file), ref.pointer, where=where)
    if ref.kind == "markdown-line":
        return status_line(sources.text(ref.file), where=ref.file)
    if ref.kind == "markdown-table":
        return table_number(sources.text(ref.file), *ref.args, where=ref.file)
    if ref.kind == "derived":
        return RULES[ref.rule][0](sources.json(ref.file), *ref.args, where=ref.file)
    if ref.kind == "config-set":
        return resolve_config_set(ref, sources)
    if ref.kind == "python":
        if python_key(ref) not in python_values:
            raise ExtractionError(f"{where}: the module constant was not read")
        return python_values[python_key(ref)]
    raise ExtractionError(f"{where}: unknown kind {ref.kind!r}")


def same_value(left: Any, right: Any) -> bool:
    """Equal as registered values: 120 and 120.0 agree; true and 1 do not."""

    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(same_value(a, b) for a, b in zip(left, right))
    if isinstance(left, Mapping) and isinstance(right, Mapping):
        return set(left) == set(right) and all(same_value(left[key], right[key]) for key in left)
    return type(left) is type(right) and left == right


# --------------------------------------------------------------------------
# The manifest: every entry, with the place it is read from


def _pack(label: str) -> str:
    return {"ALPHA": "the ALPHA pack (the 1.7B window's)", "BETA": "the BETA pack (the 8B window's)",
            "GAMMA": "the GAMMA pack (the contrast window's)"}[label]


def _status_entries() -> list[Entry]:
    return [
        Entry("status.registration", L(REGISTRATION), "text",
              "The registration's own status line, verbatim. While it says DRAFT, every value below is a draft "
              "value."),
        Entry("status.analysis_plan", L(ANALYSIS_PLAN), "text", "The analysis plan's own status line, verbatim."),
        Entry("status.flag_catalog", D(CATALOG, "first_sentence", "/notes/status"), "text",
              "The first sentence of the flag catalog's status note."),
        Entry("status.sizing", J(SIZING, "/status"), "text",
              "Status field of the sizing output, the file that holds each pack's programmed span and window "
              "deadline."),
        Entry("status.sizing_sealed", J(SIZING, "/sealed"), "boolean", "Whether the sizing output is sealed."),
        Entry("status.identity_pins", J(PINS, "/status"), "text",
              "Status field of the identity pins, the file that fixes which model and which runtime "
              "configuration each identity unit must have run."),
        Entry("status.identity_pins_sealed", J(PINS, "/sealed"), "boolean",
              "Whether the identity pins are sealed."),
        Entry("status.sealed_inventory", J(INVENTORY, "/status"), "text",
              "Status of the sealed inventory, the list of file digests of the code every window runs. It is a "
              "stub until the registration is sealed."),
    ]


def _chain_entries() -> list[Entry]:
    budgets = {
        "bracket_reservation": "the bracket reservation, the first step of the chain",
        "pre_calibration_capture": "the pre calibration capture",
        "window_calibration_verdict": "the one fit of the pre calibration capture that members then reuse",
        "neg8_corpus_retry_decision": "the decision whether to run the reference corpus stage once more",
        "neg8_spare_retry_decision": "the decision, after a reference stage, whether to run its spares",
        "neg8_corpus_collected": "the copy of the list of reference corpus members that succeeded",
        "bound_derivation": "the derivation of the reference drift bound from the reference corpus",
        "session_status_record": "the record, made at the end of the chain, of the status of the entry the "
                                 "bracket reservation opened",
        "flag_record": "one flag written by the chain",
    }
    entries = [
        Entry("chain.settle_s", P(CHAIN_PY, "SETTLE_S"), "s",
              "Settle: the sleep before the pre calibration capture and before every collection stage.",
              also=(J(SIZING, "/terms/settle_s/seconds"),)),
        Entry("chain.exit.completed", P(CHAIN_PY, "EXIT_COMPLETED"), "exit code",
              "The chain's exit code when it reaches its end, whatever its stages returned."),
        Entry("chain.exit.reservation_failed", P(CHAIN_PY, "STOP_EXITS", "reservation_failed"), "exit code",
              "Chain exit code of the first of the three stops, all before the first member: the bracket "
              "reservation failed."),
        Entry("chain.exit.pre_calibration_capture_failed",
              P(CHAIN_PY, "STOP_EXITS", "pre_calibration_capture_failed"), "exit code",
              "Chain exit code of the second stop: the pre calibration capture failed."),
        Entry("chain.exit.pre_calibration_screen_failed",
              P(CHAIN_PY, "STOP_EXITS", "pre_calibration_screen_failed"), "exit code",
              "Chain exit code of the third stop: the pulse timing bound of the pre calibration capture is "
              "above the largest value the registration accepts."),
        Entry("chain.exit.inspection_refused", P(CHAIN_PY, "EXIT_INSPECTION_REFUSED"), "exit code",
              "Chain exit code when the chain file is started with a request only to inspect it; it then runs "
              "nothing."),
        Entry("chain.countdown_s.pre_calibration", P(CHAIN_PY, "CALIBRATION_ARM_COUNTDOWN_S", "pre"), "s",
              "Pause before the pre calibration capture starts (a settle already precedes it)."),
        Entry("chain.countdown_s.post_calibration", P(CHAIN_PY, "CALIBRATION_ARM_COUNTDOWN_S", "post"), "s",
              "Pause before the post calibration capture starts (no settle precedes it)."),
        Entry("chain.countdown_s.collection_stage", P(CHAIN_PY, "COLLECTION_ARM_COUNTDOWN_S"), "s",
              "Pause before each collection stage starts (a settle already precedes it).",
              also=(J(SIZING, "/terms/collection_arm_countdown_s/seconds"),)),
        Entry("chain.budget.expired_exit", P(CHAIN_PY, "BUDGET_EXPIRED_RC"), "exit code",
              "Return code a stage records when its wall budget (a limit on its elapsed time) expires."),
        Entry("chain.budget.kill_grace_s", P(CHAIN_PY, "BUDGET_GRACE_S"), "s",
              "After a wall budget expires the stage's processes are asked to stop; those still alive after this "
              "long are killed."),
        Entry("chain.budget.flag_write_deadline_s", P(CHAIN_PY, "FLAG_WRITE_DEADLINE_S"), "s",
              "The flag writer's own deadline inside the flag record's wall budget, so that it reports an "
              "unwritten flag before the budget stops it."),
        Entry("chain.horizon.calibration_s", P(CHAIN_PY, "CALIBRATION_HORIZON_S"), "s",
              "The calibration horizon: how long a window's calibration stays fresh, counted from the start of "
              "the pre calibration capture."),
        Entry("chain.horizon.member_allowance_s", P(CHAIN_PY, "HORIZON_MEMBER_ALLOWANCE_S"), "s",
              "Time charged per member when the chain decides whether a stage can still finish inside the "
              "calibration horizon (chain.horizon.calibration_s)."),
        Entry("chain.horizon.stage_overhead_s", P(CHAIN_PY, "HORIZON_STAGE_OVERHEAD_S"), "s",
              "Time charged per stage, beside its settle and its members, when the chain decides whether a "
              "stage can still finish inside the calibration horizon (chain.horizon.calibration_s)."),
        Entry("chain.horizon.post_reserve_s", P(CHAIN_PY, "HORIZON_POST_RESERVE_S"), "s",
              "Time kept free before the calibration horizon (chain.horizon.calibration_s) for the post "
              "calibration capture: one settle, the time allowed for the two calibration captures and a margin."),
        Entry("chain.horizon.skipped_exit", P(CHAIN_PY, "HORIZON_SKIPPED_RC"), "exit code",
              "Return code recorded for a stage the chain did not launch because it could not finish inside the "
              "calibration horizon (chain.horizon.calibration_s)."),
        Entry("chain.stage_kinds_in_chain", P(CHAIN_PY, "IN_CHAIN_KINDS"), "list",
              "The kinds of stage the chain runs."),
        Entry("chain.stage_kinds_at_desk", P(CHAIN_PY, "DESK_KINDS"), "list",
              "The kinds of stage that are not in the chain: they are run after the window has ended."),
    ]
    for stage, described in budgets.items():
        entries.append(Entry(f"chain.wall_budget_s.{stage}", P(CHAIN_PY, "STAGE_WALL_BUDGET_S", stage), "s",
                             f"Wall budget (limit on elapsed time) of {described}."))
    return entries


def _arm_entries() -> list[Entry]:
    def arm(module: str, key: str, unit: str, what: str, *also: Ref, default: bool = True) -> Entry:
        refs = ((P(f"{HAZ}/{module}.py", "DEFAULT_THRESHOLDS", key),) if default else ()) + also
        return Entry(f"arm.{module}.{key}", F(REGISTRATION, ARM_HEADING, f"/{module}/{key}"), unit, what, also=refs)

    return [
        arm("clock", "t_stream_max_s", "s",
            "The longest sampler stream any member can have: the stream length the clock's frequency gate "
            "assumes. Each window plan carries its own value in place of this one.",
            J(SIZING, "/block/T_stream_max_s")),
        arm("clock", "h_ms", "ms",
            "First term of the frequency gate: the largest half-width measured for a member in an earlier "
            "measurement block, plus a margin.", J(SIZING, "/clock_gate/h_ms")),
        arm("clock", "frequency_margin_ppm", "ppm",
            "Added to the size of the frequency word in the frequency gate, to allow for the clock's rate over a "
            "stream differing from the stored word.", J(SIZING, "/clock_gate/frequency_margin_ppm")),
        arm("clock", "limit_ms", "ms",
            "The frequency gate's limit. The gate is: h_ms, plus (the size of the frequency word plus "
            "frequency_margin_ppm, in ppm) times t_stream_max_s (ppm times seconds gives microseconds), must "
            "not exceed this.", J(SIZING, "/clock_gate/limit_ms")),
        arm("clock", "skew_max_ns", "ns",
            "At the arm: the longest allowed time between the two raw-counter reads that surround the wall-clock "
            "read of one anchor sample."),
        arm("clock", "residual_max_ns", "ns",
            "At the arm's dwell: the residual, sampled once a second, must stay within plus or minus this of its "
            "value at the start of the dwell."),
        arm("clock", "step_ns", "ns",
            "In the window: a residual that moves by more than this between consecutive samples is recorded as a "
            "clock step."),
        arm("battery", "limit_ma", "mA",
            "At the arm: the largest allowed size of the battery current, in either direction, on the idle "
            "machine."),
        arm("battery", "max_update_age_s", "s",
            "At the arm: the oldest allowed registry reading of the battery's state."),
        arm("battery", "max_unobserved_s", "s",
            "In the window: a stretch longer than this with no new registry publication counts as the battery "
            "state not having been measured."),
        arm("thermal", "max_level", "level",
            "At the arm: the highest allowed thermal-pressure level reported by the operating system (0 is "
            "nominal)."),
        arm("thermal", "max_gap_s", "s",
            "In the window: a gap longer than this between thermal readings counts as the thermal state not "
            "having been measured."),
        arm("contention", "cpu_limit_s_per_s", "CPU-s/s",
            "The most CPU time per second of wall time that a process which does not belong to the measurement "
            "may use (0.05 is 5% of one core)."),
        arm("contention", "interval_s", "s",
            "At the arm's dwell: the length of one interval over which each process's CPU time is measured."),
        arm("contention", "clean_s", "s",
            "At the arm's dwell: the length of the run of consecutive intervals, each with no process above the "
            "limit (arm.contention.cpu_limit_s_per_s), that lets the chain start.",
            P(f"{HAZ}/contention.py", "HAZARD_ARM_CLEAN_S")),
        arm("contention", "cap_s", "s",
            "At the arm's dwell: if no run of clean intervals of the required length (arm.contention.clean_s) "
            "appears within this long, the arm refuses.",
            P(PLAN_PY, "DWELL_CAP_S"), J(SIZING, "/terms/clean_dwell_cap/seconds")),
        arm("contention", "window_interval_s", "s",
            "In the window: the length of one interval over which the monitor measures each process's CPU time.",
            P(f"{HAZ}/monitor.py", "DEFAULT_CADENCE", "contention_s")),
        arm("contention", "aggregate_cpu_limit_s_per_s", "CPU-s/s",
            "The limit on the whole machine's busy CPU time at the dwell. Null means that total is recorded and "
            "not judged; only the per-process limit decides."),
        arm("disk", "planned_bytes", "bytes",
            "The bytes one window is planned to write, as shown in the registration's block of arm thresholds: "
            "the value for ALPHA. Each window plan carries its own value in place of this one.", default=False),
        arm("disk", "headroom_bytes", "bytes",
            "At the arm: free space required on a volume beyond the bytes planned for it."),
        arm("disk", "low_bytes", "bytes",
            "In the window: below this much free space the monitor records low disk and the chain is stopped."),
        arm("instrument", "frames", "count",
            "At the arm the sampler is run once on the idle machine as a test capture; this is the number of "
            "power records that capture must deliver, exactly."),
        arm("instrument", "bound_s", "s",
            "At the arm the sampler is run once on the idle machine as a test capture; this is the time within "
            "which that capture must finish."),
        arm("instrument", "median_ms_max", "ms",
            "At the arm the sampler is run once on the idle machine as a test capture; this is the largest "
            "allowed median time between consecutive power records of that capture."),
        arm("instrument", "max_ms_max", "ms",
            "At the arm the sampler is run once on the idle machine as a test capture; this is the largest "
            "allowed time between any two consecutive power records of that capture."),
        Entry("arm.hazard_modules", P(f"{HAZ}/arm.py", "MODULES"), "list",
              "The hazard checks the arm runs, by their names in the code."),
        Entry("arm.unmeasured_refuses", P(f"{HAZ}/arm.py", "UNMEASURED_REFUSES"), "list",
              "The hazards for which a failed measurement at the arm refuses the window. For every other hazard "
              "a failed measurement is recorded and the arm goes on."),
        Entry("arm.agent_census_command", P(f"{HAZ}/arm.py", "AGENT_CENSUS_ARGV"), "list",
              "The command whose output the arm searches for agent sessions."),
        Entry("arm.network_time_off_command", P(f"{HAZ}/arm.py", "NETWORK_TIME_OFF_ARGV"), "list",
              "The command the arm runs to turn network time (automatic clock setting from a time server) "
              "off."),
        Entry("arm.census_timeout_s", P(f"{HAZ}/arm.py", "CENSUS_TIMEOUT_S"), "s",
              "Time limit of the agent census command."),
        Entry("arm.network_time_off_timeout_s", P(f"{HAZ}/arm.py", "NETWORK_TIME_OFF_TIMEOUT_S"), "s",
              "Time limit of the command that turns network time (automatic clock setting from a time server) "
              "off."),
        Entry("arm.allowance_s", P(PLAN_PY, "T0_STAGE_CAP_S"), "s",
              "Time allowed for the whole arm, the dwell at its cap included; added to the programmed span to "
              "give the window deadline.", also=(J(SIZING, "/terms/t0_stage_cap/seconds"),)),
        Entry("clock.window_skew_divisor", P(f"{HAZ}/clock.py", "SKEW_DIVISOR_OF_STEP"), "number",
              "In the window an anchor sample is used only if its two raw-counter reads are at most the "
              "clock-step threshold (arm.clock.step_ns) divided by this apart."),
        Entry("clock.window_skew_max_ns", P(f"{HAZ}/clock.py", "WINDOW_SKEW_MAX_NS"), "ns",
              "In the window: the longest allowed time between the two raw-counter reads of one anchor sample, "
              "at the registered clock-step threshold (arm.clock.step_ns divided by clock.window_skew_divisor)."),
        Entry("clock.anchor_read_tries", P(f"{HAZ}/clock.py", "ANCHOR_TRIES"), "count",
              "How many times the monitor reads the anchor for one sample before recording the sample as not "
              "measured."),
        Entry("clock.frequency_word_units_per_ppm", P(KERNEL_CLOCK_PY, "FREQUENCY_SCALE"), "units per ppm",
              "The kernel stores the frequency word as an integer; this many of its units are one part per "
              "million.", also=(P(f"{HAZ}/clock.py", "FREQUENCY_SCALE"),)),
        Entry("battery.smc_max_gap_s", P(f"{HAZ}/battery.py", "SMC_MAX_GAP_S"), "s",
              "In the window: when two good SMC readings of the battery current are further apart than this "
              "inside a member, the registry's current is judged instead and the fallback is recorded and "
              "reported."),
        Entry("battery.smc_current_key", P(f"{HAZ}/battery.py", "SMC_CURRENT_KEY"), "text",
              "The SMC's name for the battery current (mA, negative when the battery discharges)."),
        Entry("battery.smc_voltage_key", P(f"{HAZ}/battery.py", "SMC_VOLTAGE_KEY"), "text",
              "The SMC's name for the battery voltage (mV)."),
        Entry("battery.smc_keys_recorded", P(f"{HAZ}/smc.py", "KEYS"), "list",
              "Every SMC reading the monitor records, by the SMC's own names."),
        Entry("contention.report_floor_cpu_s_per_s", P(f"{HAZ}/contention.py", "REPORT_FLOOR_CPU_S_PER_S"),
              "CPU-s/s",
              "Processes that do not belong to the measurement and use less CPU than this are counted, not "
              "listed by name."),
    ]


def _monitor_entries() -> list[Entry]:
    cadence = {
        "clock_s": "Seconds between two readings of the clock anchor by the monitor.",
        "frequency_s": "Seconds between two readings of the frequency word by the monitor.",
        "battery_s": "Seconds between two polls of the battery's state in the registry by the monitor.",
        "battery_smc_s": "Seconds between two readings of the battery current from the SMC by the monitor.",
        "battery_publication_s": "The registry's own publication period, as the monitor assumes it.",
        "battery_full_max_s": "The longest the monitor goes without reading the registry's whole battery record "
                              "while its poll works.",
        "battery_max_s": "The longest the monitor goes without reading the registry's whole battery record when "
                         "its poll does not work.",
        "thermal_s": "Seconds between two readings of the thermal-pressure level by the monitor.",
        "contention_s": "Length of one interval over which the monitor measures every process's CPU time.",
        "disk_s": "Seconds between two readings of free disk space by the monitor.",
        "self_s": "Seconds between two records of the monitor's own CPU time.",
    }
    entries = [Entry(f"monitor.every_s.{key.removesuffix('_s')}", P(f"{HAZ}/monitor.py", "DEFAULT_CADENCE", key),
                     "s", what) for key, what in cadence.items()]
    entries.append(Entry("monitor.fsync_interval_s", P(f"{HAZ}/monitor.py", "FSYNC_INTERVAL_S"), "s",
                         "The monitor forces its records to disk at most this often, so only a power loss can "
                         "drop the last few seconds."))
    return entries


def _driver_entries() -> list[Entry]:
    return [
        Entry("driver.monitor_post_chain_hold_s", P(DRIVER_PY, "MONITOR_POST_CHAIN_HOLD_S"), "s",
              "The monitor is stopped no sooner than this after the chain exits, so that its readings cover the "
              "end of the post calibration capture."),
        Entry("driver.monitor_outage_s", P(DRIVER_PY, "MONITOR_OUTAGE_S"), "s",
              "The chain is stopped when the monitor's battery record or its contention record has gained no "
              "error-free line for this long."),
        Entry("driver.disk_check_interval_s", P(DRIVER_PY, "DISK_CHECK_INTERVAL_S"), "s",
              "How often the driver checks for the monitor's low-disk record."),
        Entry("driver.lineage_retry_s", P(DRIVER_PY, "LINEAGE_RETRY_S"), "s",
              "Wait before the one retry of publishing the file that ties each member's output to its window."),
        Entry("driver.census_retries", P(DRIVER_PY, "CENSUS_RETRIES"), "count",
              "In the window: how many times an agent census that could not be read is retried before it is "
              "recorded as not measured."),
        Entry("driver.clock_step_control_timeout_s", P(DRIVER_PY, "G10_TIMEOUT_S"), "s",
              "Time limit of the clock-step control: a deliberate step of the clock, made after the chain of "
              "the first ALPHA window has exited, to confirm that a clock step is detected."),
        Entry("driver.clock_step_control_poll_s", P(DRIVER_PY, "G10_POLL_S"), "s",
              "While the clock-step control runs (driver.clock_step_control_timeout_s), the driver repeats "
              "its supervision of the monitor this often."),
        Entry("yield.stall_s", P(DRIVER_PY, "YIELD_STALL_S"), "s",
              "No new member output and no new stage record for this long is recorded as a stalled window."),
        Entry("yield.identical_refusals", P(DRIVER_PY, "YIELD_PRE_BUNDLE_RUN"), "count",
              "This many consecutive members that ended with no output for one shared cause are recorded once "
              "as a repeated refusal."),
        Entry("yield.min_valid.reference_endpoint", P(DRIVER_PY, "REFERENCE_ENDPOINT_MIN_VALID"), "count",
              "The fewest succeeded members of a start or end triplet that still leave the reference drift check able to "
              "run."),
        Entry("yield.min_valid.reference_midpoint", P(DRIVER_PY, "REFERENCE_MIDPOINT_MIN_VALID"), "count",
              "The fewest succeeded midpoint references the reference drift check needs."),
        Entry("yield.min_valid.science_numerator", P(DRIVER_PY, "SCIENCE_MIN_NUMERATOR"), "count",
              "A stage of science members is counted as low when fewer than a fixed fraction of its planned "
              "members succeeded (the product is rounded up); this is the fraction's numerator."),
        Entry("yield.min_valid.science_denominator", P(DRIVER_PY, "SCIENCE_MIN_DENOMINATOR"), "count",
              "A stage of science members is counted as low when fewer than a fixed fraction of its planned "
              "members succeeded (the product is rounded up); this is the fraction's denominator."),
    ]


def _member_entries() -> list[Entry]:
    cooldown = POLICY
    return [
        Entry("member.cap_s", P(RUN_CAMPAIGN_PY, "HAZARD_MEMBER_CAP_S"), "s",
              "The longest a member's process may run before it is stopped and recorded as timed out."),
        Entry("member.kill_grace_s", P(RUN_CAMPAIGN_PY, "HAZARD_MEMBER_TERM_GRACE_S"), "s",
              "A timed-out member is asked to stop; processes still alive after this long are killed."),
        Entry("member.timeout_drain_after", P(RUN_CAMPAIGN_PY, "HAZARD_MEMBER_TIMEOUT_DRAIN_AFTER"), "count",
              "After this many consecutive timed-out members the window runs only its end references and its "
              "post calibration."),
        Entry("policy.id", J(POLICY, "/policy_id"), "text",
              "Identifier of the campaign policy file that sets the cooldown rule and the idle-admission tests "
              "for every pack."),
        Entry("cooldown.cap_s", J(cooldown, "/cooldown/cap_s"), "s",
              "The longest a cooldown may last; the next member then starts anyway and the cap is recorded.",
              also=(J(SIZING, "/terms/members/small/cooldown/seconds"),
                    J(SIZING, "/terms/members/large/cooldown/seconds"))),
        Entry("cooldown.subwindow_s", J(cooldown, "/cooldown/subwindow_s"), "s",
              "The length of one idle reading taken during a cooldown."),
        Entry("cooldown.sustained_window_s", J(cooldown, "/cooldown/sustained_window_s"), "s",
              "Only the readings of the last this-many seconds decide whether the cooldown ends."),
        Entry("cooldown.coverage_fraction", J(cooldown, "/cooldown/coverage_fraction"), "fraction",
              "A cooldown ends on the idle readings of its most recent stretch (cooldown.sustained_window_s "
              "long); the readings must cover at least this fraction of that stretch."),
        Entry("cooldown.tolerance_fraction", J(cooldown, "/cooldown/tolerance_fraction"), "fraction",
              "The bound on the idle reading is the previous member's idle-baseline mean power times (1 + this)."),
        Entry("cooldown.require_thermal_nominal", J(cooldown, "/cooldown/require_thermal_nominal"), "boolean",
              "Whether the cooldown also waits for the operating system's thermal state to be nominal."),
        Entry("idle_admission.retry_attempts", J(POLICY, "/idle_admission/retry_attempts"), "count",
              "How many times a refused idle baseline is retried before the member is aborted."),
        Entry("idle_admission.on_fail", J(POLICY, "/idle_admission/on_fail"), "text",
              "What happens to a member whose idle baseline is still refused after the retry."),
        Entry("idle_admission.cpu_min_samples", J(POLICY, "/idle_admission_extension/cpu_criteria/min_samples"),
              "count", "The fewest CPU readings an idle baseline must hold for its CPU tests to be computed."),
        Entry("idle_admission.cpu_busy_ratio_p95_max",
              J(POLICY, "/idle_admission_extension/cpu_criteria/cpu_busy_ratio_p95_max"), "fraction",
              "Largest allowed 95th percentile, over the idle baseline, of the fraction of time the cores were "
              "not idle."),
        Entry("idle_admission.processor_power_w_p95_max",
              J(POLICY, "/idle_admission_extension/cpu_criteria/processor_combined_power_w_p95_max"), "W",
              "Largest allowed 95th percentile, over the idle baseline, of processor-rail power."),
        Entry("idle_admission.on_missing_cpu_readings",
              J(POLICY, "/idle_admission_extension/cpu_criteria/on_missing_telemetry"), "text",
              "What idle admission decides when the CPU readings are missing."),
        *[Entry(f"idle_admission.guard.{key}", J(POLICY, f"/environment_guard/{key}"), "boolean", what)
          for key, what in (
              ("require_ac_power", "Idle admission requires the machine to be on mains power."),
              ("require_external_connected", "Idle admission requires an external power adapter to be connected."),
              ("require_displays_asleep", "Idle admission requires the displays to be asleep."),
              ("require_screensaver_disengaged", "Idle admission requires the screensaver not to be running."),
              ("require_low_power_mode_off", "Idle admission requires Low Power Mode to be off."),
              ("require_thermal_nominal", "Idle admission requires the thermal state to be nominal."),
              ("critical_unknown_fail_closed",
               "Whether a required condition that cannot be read counts as not met."),
          )],
    ]


def _harvest_entries() -> list[Entry]:
    def threshold(key: str, unit: str, what: str, *also: Ref) -> Entry:
        return Entry(f"harvest.{key}", F(REGISTRATION, HARVEST_HEADING, f"/{key}"), unit, what, also=also)

    def arm(pointer: str) -> Ref:
        return F(REGISTRATION, ARM_HEADING, pointer)

    return [
        threshold("battery_limit_ma", "mA",
                  "At the harvest: the battery-current limit applied over each member's time span.",
                  arm("/battery/limit_ma")),
        threshold("battery_unmeasured_gap_s", "s",
                  "At the harvest: a stretch longer than this with no new registry publication inside a member "
                  "counts as the battery state not having been measured.", arm("/battery/max_unobserved_s")),
        threshold("battery_accumulator_watts_per_unit", "W",
                  "The registry also keeps running sums of battery power; this is the power one unit of those "
                  "sums stands for (they count milliwatts)."),
        threshold("thermal_unmeasured_gap_s", "s",
                  "At the harvest: a gap longer than this between thermal readings inside a member counts as the "
                  "thermal state not having been measured.", arm("/thermal/max_gap_s")),
        threshold("contention_cpu_s_per_s", "CPU-s/s",
                  "At the harvest: the per-process CPU limit applied to the intervals that overlap a member's "
                  "measured request.", arm("/contention/cpu_limit_s_per_s")),
        threshold("clock_step_ns", "ns",
                  "At the harvest: a residual move larger than this between consecutive samples is a clock step.",
                  arm("/clock/step_ns")),
        threshold("clock_unmeasured_gap_s", "s",
                  "At the harvest: a gap longer than this between clock samples inside a member counts as the "
                  "clock not having been measured."),
        threshold("disk_low_bytes", "bytes", "At the harvest: the free-space level below which disk was low.",
                  arm("/disk/low_bytes"), P(DRIVER_PY, "DISK_LOW_BYTES_DEFAULT")),
        threshold("clock_systematic_min_recorded", "count",
                  "A window is removed when at least this many of its members have a recorded status of their "
                  "member clock bound and more than half of those members do not meet the bound's conditions (a "
                  "long enough sampler stream, estimator.min_stream_s, and a bound within the limit, "
                  "estimator.member_clock_bound_max_s)."),
        Entry("harvest.raw_valid_min_stream_bytes", P(HARVEST_PY, "RAW_VALID_MIN_STREAM_BYTES"), "bytes",
              "At the harvest a member's raw sampler output counts as present when it is at least this large "
              "and no file is missing."),
        Entry("harvest.battery_temperature.rise_limit_k", P(HARVEST_PY, "BATTERY_RISE_LIMIT_K"), "K",
              "The battery temperature is read at the end of each cooldown. A stage whose temperature rose by "
              "more than this from its first reading to its last, without levelling off, is recorded and "
              "reported."),
        Entry("harvest.battery_temperature.plateau_spread_k", P(HARVEST_PY, "BATTERY_PLATEAU_SPREAD_K"), "K",
              "The battery temperature of a stage has levelled off when its last readings (their number is "
              "harvest.battery_temperature.plateau_readings) lie within this of one another."),
        Entry("harvest.battery_temperature.plateau_readings", P(HARVEST_PY, "BATTERY_PLATEAU_READINGS"), "count",
              "The number of last battery-temperature readings of a stage that are compared to decide whether "
              "the temperature has levelled off."),
    ]


def _reference_entries() -> list[Entry]:
    return [
        Entry("reference.corpus_minimum_n", P(WHOLE_WINDOW_PY, "NEG8_DRIFT_MINIMUM_N"), "count",
              "The fewest reference corpus members from which the reference drift bound may be derived. With fewer succeeded "
              "members the corpus stage is run once more.",
              also=(P(CHAIN_PY, "NEG8_RETRY_MINIMUM"), P(DRIVER_PY, "CORPUS_MIN_VALID"))),
        Entry("reference.endpoint_references_planned", P(WHOLE_WINDOW_PY, "NEG8_REPLICATED_ENDPOINT_N"), "count",
              "The planned number of reference members at each end of the window (one triplet)."),
        Entry("reference.survivor_endpoint_counts", P(WHOLE_WINDOW_PY, "NEG8_SURVIVOR_ENDPOINT_COUNTS"), "list",
              "The numbers of surviving reference members at one end of the window with which the reference drift check "
              "still runs."),
        Entry("reference.survivor_midpoint_counts", P(WHOLE_WINDOW_PY, "NEG8_SURVIVOR_MIDPOINT_COUNTS"), "list",
              "The numbers of surviving midpoint references with which the reference drift check still runs."),
        Entry("reference.count_adjusted_bound_formula", P(WHOLE_WINDOW_PY, "NEG8_COUNT_ADJUSTED_BOUND_FORMULA"),
              "text",
              "The reference drift bound for n_start surviving start references and n_end surviving end references, as "
              "the code states it."),
        Entry("reference.bound_max_age_s", P(WHOLE_WINDOW_PY, "NEG8_DRIFT_BOUND_MAX_AGE_S"), "s",
              "The age beyond which a derived reference drift bound is no longer fresh."),
        Entry("reference.spares.start", P(SPARES_PY, "SLOTS", "start", 3), "count",
              "Spares registered for the start triplet."),
        Entry("reference.spares.midpoint", P(SPARES_PY, "SLOTS", "midpoint", 3), "count",
              "Spares registered for the midpoint reference."),
        Entry("reference.spares.end", P(SPARES_PY, "SLOTS", "end", 3), "count",
              "Spares registered for the end triplet."),
    ]


def _estimator_entries() -> list[Entry]:
    return [
        Entry("estimator.member_clock_bound_max_s", P(ANCHOR_PY, "MAX_EFFECTIVE_CLOCK_ANCHOR_BOUND_S"), "s",
              "The largest allowed member clock bound; a member above it is removed."),
        Entry("estimator.min_stream_s", P(ANCHOR_PY, "MIN_RATE_FIT_BASELINE_S"), "s",
              "A member clock bound counts only when the member's sampler stream, as summed record time, is at "
              "least this long."),
        Entry("estimator.model_departure_allowance_s", P(ANCHOR_PY, "MAX_AFFINE_CLOCK_RESIDUAL_S"), "s",
              "The member clock bound assumes that wall-clock time is a straight-line function of the "
              "machine's steadily counting clock over one sampler stream; this is the allowance for departure "
              "from that line."),
        Entry("reducer.min_phase_records", P(REDUCE_PY, "MIN_PHASE_SAMPLES"), "count",
              "The fewest power records that must overlap a phase for its energy to be computed."),
    ]


def _workload_entries() -> list[Entry]:
    every = SCIENCE_DIRS + REFERENCE_DIRS
    decode, prefill = (PROFILE, DECODE_PROFILE), (PROFILE, PREFILL_PROFILE)
    alpha_manifest, beta_manifest = (f"{ALPHA_DIR}/decode_prompt_manifest.json",
                                     f"{BETA_DIR}/decode_prompt_manifest.json")
    return [
        Entry("member.idle_seconds", C(every, "/sampling/idle_seconds"), "s",
              "The idle-baseline setting of every member configuration. The sampler is asked for this setting "
              "divided by the requested record interval (1 divided by member.sampler_rate_hz), rounded up, in "
              "power records; so the setting fixes a number of records, not a duration."),
        Entry("member.sampler_rate_hz", C(every, "/sampling/power_hz"), "Hz",
              "The rate at which every member configuration asks the sampler for power records."),
        Entry("member.warmup_runs", C(every, "/workload_profile/warmup_runs"), "count",
              "Warm-up generations before the measured request, in every member configuration."),
        Entry("workload.decode.prompt_tokens", J(alpha_manifest, "/items/0/shape/planned_prompt_tokens"),
              "tokens", "Prompt length of the decode workload, the one whose decode phase is reported.",
              also=(J(beta_manifest, "/items/0/shape/planned_prompt_tokens"),)),
        Entry("workload.decode.output_tokens", C(SCIENCE_DIRS, "/workload_profile/output_tokens", decode),
              "tokens", "Output length of the decode workload.",
              also=(J(alpha_manifest, "/items/0/shape/planned_output_tokens"),
                    J(beta_manifest, "/items/0/shape/planned_output_tokens"))),
        Entry("workload.decode.configurations", CN(SCIENCE_DIRS, decode), "count",
              "Member configurations of the decode workload across the three packs."),
        Entry("workload.prefill.prompt_tokens",
              C(SCIENCE_DIRS, "/workload_profile/prompt_token_expectation/token_count", prefill), "tokens",
              "Prompt length of the prefill workload, the one whose prefill phase is reported."),
        Entry("workload.prefill.prompt_token_ids_sha256",
              C(SCIENCE_DIRS, "/workload_profile/prompt_token_expectation/token_ids_sha256", prefill), "sha256",
              "SHA-256 over the token identifiers of the prefill workload's prompt."),
        Entry("workload.prefill.output_tokens", C(SCIENCE_DIRS, "/workload_profile/output_tokens", prefill),
              "tokens", "Output length of the prefill workload."),
        Entry("workload.prefill.configurations", CN(SCIENCE_DIRS, prefill), "count",
              "Member configurations of the prefill workload across the three packs."),
        Entry("workload.reference.prompt_tokens", C(REFERENCE_DIRS, "/workload_profile/prompt_tokens"), "tokens",
              "Prompt length of the reference workload."),
        Entry("workload.reference.output_tokens", C(REFERENCE_DIRS, "/workload_profile/output_tokens"), "tokens",
              "Output length of the reference workload."),
        Entry("workload.reference.configurations.window_references", CN(REFERENCES_DIR), "count",
              "Configurations of the start triplet, the midpoint reference and the end triplet together."),
        Entry("workload.reference.configurations.gamma_interior", CN(INTERIOR_DIR), "count",
              "Configurations of the two extra reference members GAMMA runs in the middle of each half of its "
              "science stages; they are recorded only and do not enter the reference drift check."),
        Entry("workload.reference.configurations.spare_set_files", CN(SPARES_DIR), "count",
              "Spare configuration files across the committed spare sets. Each reference stage has one set per "
              "possible number of lost references, so one spare appears in more than one set."),
    ]


def _sizing_entries() -> list[Entry]:
    entries = [
        Entry("sizing.t_stream_max_s", J(SIZING, "/block/T_stream_max_s"), "s",
              "The longest sampler stream any member of the three packs can have."),
        Entry("sizing.longest_packs", J(SIZING, "/block/longest_packs"), "list",
              "The packs whose own longest sampler stream equals the longest of all (sizing.t_stream_max_s)."),
        Entry("sizing.frequency_gate.required_abs_frequency_ppm", J(SIZING, "/clock_gate/required_abs_frequency_ppm"),
              "ppm", "The sizing checks that the frequency gate passes for a frequency word of this size."),
        Entry("sizing.frequency_gate.stream_limit_s", J(SIZING, "/clock_gate/stream_limit_s"), "s",
              "The longest sampler stream at which the frequency gate still passes for a frequency word of the "
              "size the sizing checks (sizing.frequency_gate.required_abs_frequency_ppm)."),
        Entry("sizing.calibration_pair_s", J(SIZING, "/terms/pre_post_calibration/seconds"), "s",
              "Time charged for the pre and post calibration captures together."),
        Entry("sizing.bound_derivation_s", J(SIZING, "/terms/bound_derivation/seconds"), "s",
              "Time charged for deriving the reference drift bound from the reference corpus."),
        Entry("sizing.corpus_prune_s", J(SIZING, "/terms/corpus_prune/seconds"), "s",
              "Time charged for listing which reference corpus members the bound may use."),
        Entry("sizing.window_calibration_verdict_s", J(SIZING, "/terms/window_calibration_verdict/seconds"), "s",
              "Time charged for the one fit of the pre calibration capture that members then reuse."),
        Entry("sizing.terminal_shutdown_s", J(SIZING, "/terms/terminal_shutdown/seconds"), "s",
              "Time charged for the end of the chain after the post calibration capture."),
        Entry("sizing.member_allowance_s.1p7b", J(SIZING, "/terms/member_allowance_s/small"), "s",
              "Member allowance of one Qwen3-1.7B-class member (a Qwen3-1.7B member or a reference member): "
              "loading the model, the warm-up, the prefill phase, the decode phase at its fixed output length, "
              "the cooldown at its cap and both idle-admission attempts."),
        Entry("sizing.member_allowance_s.8b", J(SIZING, "/terms/member_allowance_s/large"), "s",
              "Member allowance of one Qwen3-8B member: loading the model, the warm-up, the prefill phase, the "
              "decode phase at its fixed output length, the cooldown at its cap and both idle-admission "
              "attempts."),
        Entry("sizing.reduction_per_member_s", J(SIZING, "/terms/reduction_per_member/seconds"), "s",
              "Time charged per member for turning its raw records into its summary."),
        Entry("sizing.sampler_start_and_winddown_per_member_s", J(SIZING, "/terms/native_sampler_per_member/seconds"),
              "s", "Time charged per member for starting the sampler and winding it down."),
        Entry("sizing.sampler_start_s", J(SIZING, "/terms/stage_custody_formula/sampler_start_s"), "s",
              "Time charged per member for starting the sampler."),
        Entry("sizing.sampler_winddown_s", J(SIZING, "/terms/stage_custody_formula/sampler_winddown_s"), "s",
              "Time charged per member for winding the sampler down."),
        Entry("sizing.stage_overhead_s", J(SIZING, "/terms/stage_custody_formula/stage_overhead_s"), "s",
              "Bookkeeping time charged per collection stage."),
        Entry("sizing.bracket_custody_s", J(SIZING, "/terms/stage_custody_formula/bracket_custody_s"), "s",
              "Bookkeeping time charged per calibration capture."),
        Entry("sizing.reservation_s", J(SIZING, "/terms/stage_custody_formula/reservation_s"), "s",
              "Time charged for the bracket reservation."),
        Entry("sizing.terminal_custody_s", J(SIZING, "/terms/stage_custody_formula/terminal_custody_s"), "s",
              "Bookkeeping time charged at the end of the chain."),
        Entry("sizing.stream_s.1p7b", J(SIZING, "/terms/streams/small/seconds"), "s",
              "The longest sampler stream of a Qwen3-1.7B-class member."),
        Entry("sizing.stream_s.8b", J(SIZING, "/terms/streams/large/seconds"), "s",
              "The longest sampler stream of a Qwen3-8B member."),
        Entry("sizing.earlier_block_reproduction.programmed_span_s",
              J(SIZING, "/block4_reproduction/committed/NIGHT_PROGRAMMED_SPAN_S_s1"), "s",
              "Before it sizes anything, the sizing program recomputes the programmed span that was committed "
              "for an earlier, unrun measurement block, and stops if its arithmetic does not reproduce it. This "
              "is the committed span.",
              also=(J(SIZING, "/block4_reproduction/breakdown/programmed_span_s"),)),
        Entry("sizing.earlier_block_reproduction.window_max_s",
              J(SIZING, "/block4_reproduction/committed/WINDOW_MAX_S_s1"), "s",
              "Before it sizes anything, the sizing program recomputes the window deadline that was committed "
              "for an earlier, unrun measurement block, and stops if its arithmetic does not reproduce it. This "
              "is the committed deadline.",
              also=(J(SIZING, "/block4_reproduction/window_max_s"),)),
        Entry("sizing.earlier_block_reproduction.reproduced", J(SIZING, "/block4_reproduction/reproduced"),
              "boolean",
              "Whether the sizing program's arithmetic reproduced the programmed span and window deadline "
              "committed for an earlier, unrun measurement block."),
    ]
    parts = {"load": "loading the model", "warmup": "the warm-up generation", "prefill": "the prefill phase",
             "forced_decode": "the decode phase at its fixed output length",
             "cooldown": "the cooldown at its cap", "idle_admission": "both idle-admission attempts"}
    for size, model in (("small", "1p7b"), ("large", "8b")):
        name = "Qwen3-1.7B-class" if size == "small" else "Qwen3-8B"
        for part, described in parts.items():
            entries.append(Entry(f"sizing.member_part_s.{model}.{part}",
                                 J(SIZING, f"/terms/members/{size}/{part}/seconds"), "s",
                                 f"Part of the member allowance of a {name} member: {described}."))
    span_parts = {
        "settles_s": "all settles",
        "arm_countdowns_s": "the pauses before collection stages",
        "pre_post_calibration_s": "the pre and post calibration captures",
        "bound_derivation_s": "the derivation of the reference drift bound",
        "corpus_prune_s": "listing which reference corpus members the bound may use",
        "window_calibration_verdict_s": "the one fit of the pre calibration capture",
        "members_s": "the sum of the member allowances",
        "stage_custody_s": "bookkeeping around stages and members",
        "terminal_shutdown_s": "the end of the chain",
        "corpus_retry_s": "one more run of the reference corpus stage",
        "reference_spare_retry_s": "every spare of every reference stage being run",
        "pack_t0_s": "a launch allowance that an earlier sizing charged and that lies outside the chain here",
    }
    for label in PACK_LABELS:
        base, pack = f"/packs/{label}", _pack(label)
        prefix = f"pack.{label}"
        entries += [
            Entry(f"{prefix}.pack_id", J(SIZING, f"{base}/pack_id"), "text", f"Identifier of {pack}."),
            Entry(f"{prefix}.plan_tree_sha256", J(SIZING, f"{base}/plan_tree/sha256"), "sha256",
                  f"SHA-256 of the file that lists the stages of {pack} in order."),
            Entry(f"{prefix}.members", J(SIZING, f"{base}/members"), "count",
                  f"Planned members of {pack}, spares not counted."),
            Entry(f"{prefix}.science_members", J(SIZING, f"{base}/science_members"), "count",
                  f"Planned science members of {pack}.",
                  also=(D(SIZING, "sum_where", f"{base}/stages", "members", "science", True),
                        CN(PACK_DIRS[label]))),
            Entry(f"{prefix}.auxiliary_members", J(SIZING, f"{base}/auxiliary_members"), "count",
                  f"Planned members of {pack} that are not science members: the reference corpus and the other "
                  "reference members."),
            Entry(f"{prefix}.members_1p7b_class", D(SIZING, "value_or_zero", f"{base}/members_by_class/small"),
                  "count", f"Planned members of {pack} charged the Qwen3-1.7B-class member allowance "
                  "(Qwen3-1.7B members and reference members)."),
            Entry(f"{prefix}.members_8b", D(SIZING, "value_or_zero", f"{base}/members_by_class/large"), "count",
                  f"Planned members of {pack} charged the Qwen3-8B member allowance."),
            Entry(f"{prefix}.stages", D(SIZING, "count", f"{base}/stages"), "count",
                  f"Stages of {pack}, counting the reservation, the two calibration captures and the bound "
                  "derivation."),
            Entry(f"{prefix}.collection_stages", J(SIZING, f"{base}/collection_stages"), "count",
                  f"Collection stages of {pack} (stages that run members).",
                  also=(D(SIZING, "count_where", f"{base}/stages", "kind", "campaign_collection"),)),
            Entry(f"{prefix}.reference_corpus_members", D(SIZING, "sum_where", f"{base}/stages", "members",
                                                      "neg8_corpus", True), "count",
                  f"Members of the reference corpus stage of {pack}.", also=(CN(CORPUS_DIR),)),
            Entry(f"{prefix}.bound_root_members", D(SIZING, "sum_where", f"{base}/stages", "members",
                                                     "runs_dir_binding", "bound_runs_root"), "count",
                  f"Planned members of {pack} written to the output directory from which the reference drift bound is "
                  "derived."),
            Entry(f"{prefix}.claim_root_members", D(SIZING, "sum_where", f"{base}/stages", "members",
                                                     "runs_dir_binding", "claim_runs_root"), "count",
                  f"Planned members of {pack} written to the claim output directory: every member except the "
                  "reference corpus, which has its own directory."),
            Entry(f"{prefix}.spares", D(SIZING, "sum_nested", f"{base}/stages", "spare_retry", "max_spares"),
                  "count", f"Spares registered across the reference stages of {pack}."),
            Entry(f"{prefix}.stage_order", D(SIZING, "stage_rows", f"{base}/stages"), "list",
                  f"The stages of {pack} in the order the chain runs them. Each row gives the stage's position, "
                  "kind and identifier, its planned members, whether they are science members, which output "
                  "directory they are written to, whether it is the reference corpus, and its registered spares."),
            Entry(f"{prefix}.programmed_span_s", J(SIZING, f"{base}/programmed_span_s"), "s",
                  f"Programmed span of {pack}: the length of its chain if every member took its longest allowed "
                  f"path. It is a worst case, not the length the chain is expected to have; for that see "
                  f"{prefix}.expected_chain_s.measured_basis (the slower of two planning figures) and "
                  f"{prefix}.expected_chain_s.projected (the faster).",
                  also=(J(SIZING, f"{base}/breakdown/programmed_span_s"),)),
            Entry(f"{prefix}.window_max_s", J(SIZING, f"{base}/window_max_s"), "s",
                  f"Window deadline of {pack}, measured from the scheduled start: the moment at which the driver "
                  f"stops a chain that is still running. It is a stop limit, not the length the window is "
                  f"expected to have: the chain's expected length, {prefix}.expected_chain_s.measured_basis (the "
                  f"slower of two planning figures) or {prefix}.expected_chain_s.projected (the faster), is a "
                  f"third of this deadline or less."),
            Entry(f"{prefix}.expected_chain_s.measured_basis", T(REGISTRATION, EXPECTED_MEASURED_COLUMN, label, "s"),
                  "s",
                  f"Expected chain length of {pack}: the slower of the registration's two planning figures. It "
                  "is built from timings measured in an earlier measurement block (for each member, the median "
                  "time from the start of one member to the start of the next) and counts every planned member, "
                  "no spare and no further run of the reference corpus stage. It serves planning only: nothing "
                  "stops a chain at it. The arm's time is not included. The registration's sizing section gives "
                  "the arithmetic."),
            Entry(f"{prefix}.expected_chain_s.projected", T(REGISTRATION, EXPECTED_PROJECTED_COLUMN, label, "s"),
                  "s",
                  f"Expected chain length of {pack}: the faster of the registration's two planning figures. It "
                  "starts from the mean time from the start of one member to the start of the next, measured in "
                  "an earlier measurement block, and subtracts the time that changes made to the procedure since "
                  "then are expected to save for each member and each collection stage; it has not itself been "
                  "measured. It counts every planned member, no spare and no further run of the reference corpus "
                  "stage. It serves planning only: nothing stops a chain at it. The arm's time is not included. "
                  "The registration's sizing section gives the arithmetic."),
            Entry(f"{prefix}.t_stream_max_s", J(SIZING, f"{base}/T_stream_max_s"), "s",
                  f"The stream length the frequency gate assumes for {pack}: the longest of the three packs.",
                  also=(J(SIZING, f"{base}/clock_gate/at_T_stream_max/t_stream_max_s"),)),
            Entry(f"{prefix}.longest_stream_s", J(SIZING, f"{base}/pack_longest_stream_s"), "s",
                  f"The longest sampler stream a member of {pack} itself can have.",
                  also=(J(SIZING, f"{base}/clock_gate/at_pack_longest_stream/t_stream_max_s"),)),
            Entry(f"{prefix}.frequency_gate.max_abs_frequency_ppm",
                  J(SIZING, f"{base}/clock_gate/at_T_stream_max/max_abs_frequency_ppm"), "ppm",
                  f"The largest size of the frequency word at which the frequency gate passes for {pack}."),
            Entry(f"{prefix}.frequency_gate.bound_ms_at_required",
                  J(SIZING, f"{base}/clock_gate/at_T_stream_max/bound_ms_at_required"), "ms",
                  f"The left side of the frequency gate for {pack} at the frequency-word size the sizing "
                  "checks (sizing.frequency_gate.required_abs_frequency_ppm)."),
            Entry(f"{prefix}.frequency_gate.passes_at_required",
                  J(SIZING, f"{base}/clock_gate/at_T_stream_max/passes_at_required"), "boolean",
                  f"Whether the frequency gate passes for {pack} at the frequency-word size the sizing checks "
                  "(sizing.frequency_gate.required_abs_frequency_ppm)."),
        ]
        for part, described in span_parts.items():
            entries.append(Entry(f"{prefix}.span_part_s.{part.removesuffix('_s')}",
                                 J(SIZING, f"{base}/breakdown/{part}"), "s",
                                 f"Part of the programmed span of {pack}: {described}."))
    return entries


def _catalog_entries() -> list[Entry]:
    effects = {"DISCLOSE": "is recorded and reported and removes nothing",
               "EXCLUDE_MEMBER": "removes the member",
               "EXCLUDE_WINDOW": "makes the window unable to support a claim"}
    classes = {"PHYSICS": "a physical condition of the machine",
               "NUMBER": "the integrity of a number",
               "REPRESENTATION": "how something is recorded, with no bearing on a number"}
    entries = [
        Entry("catalog.schema", J(CATALOG, "/schema_version"), "text", "Schema name of the flag catalog."),
        Entry("catalog.codes", D(CATALOG, "count", "/codes"), "count", "Flag codes in the catalog."),
        Entry("catalog.cell_unit_minimum", J(CATALOG, "/rules/cell_unit_minimum"), "count",
              "Every reported number must keep at least this many of its planned repeats and at least this many "
              "of its planned quads; otherwise the window cannot support a claim."),
        Entry("catalog.families", D(CATALOG, "distinct", "/codes", "family"), "list",
              "The families the catalog sorts its codes into."),
        Entry("catalog.codes_with_effect.EXCLUDE_WINDOW", D(CATALOG, "keys_where", "/codes", "effect",
                                                             "EXCLUDE_WINDOW"), "list",
              "Every code whose effect is EXCLUDE_WINDOW."),
        Entry("catalog.codes_with_effect.EXCLUDE_MEMBER", D(CATALOG, "keys_where", "/codes", "effect",
                                                             "EXCLUDE_MEMBER"), "list",
              "Every code whose effect is EXCLUDE_MEMBER."),
        Entry("catalog.codes_restricted", D(CATALOG, "keys_where", "/codes", "blinding", "RESTRICTED"), "list",
              "Every code whose flags are kept unread until the measurement block's energies may be read, "
              "because such a flag is computed from a science member's energy."),
    ]
    for effect, described in effects.items():
        entries.append(Entry(f"catalog.effect.{effect}", D(CATALOG, "count_where", "/codes", "effect", effect),
                             "count", f"Codes whose effect is {effect}: a flag with such a code {described}."))
    for klass, described in classes.items():
        entries.append(Entry(f"catalog.class.{klass}", D(CATALOG, "count_where", "/codes", "klass", klass),
                             "count", f"Codes of class {klass}: the flag concerns {described}."))
        for effect in effects:
            entries.append(Entry(f"catalog.class_effect.{klass}.{effect}",
                                 D(CATALOG, "count_where2", "/codes", "klass", klass, "effect", effect), "count",
                                 f"Codes of class {klass} whose effect is {effect}."))
    for blinding, described in (
            ("STRUCTURE", "may be read while the measurement block is still collecting, because they describe "
                          "structure and carry no energy"),
            ("RESTRICTED", "are kept unread until the measurement block's energies may be read, because such a "
                           "flag is computed from a science member's energy")):
        entries.append(Entry(f"catalog.blinding.{blinding}",
                             D(CATALOG, "count_where", "/codes", "blinding", blinding), "count",
                             f"Codes whose flags {described}."))
    for family in ("CALIBRATION", "CLOCK_SYSTEMATIC", "CODE_IDENTITY", "DIAGNOSTIC", "INSTRUMENT",
                   "MEMBER_VALIDITY", "MODEL_IDENTITY", "NEG8", "PACK_IDENTITY", "PHYSICS_IN_SPAN", "RECORDS",
                   "ROSTER"):
        entries.append(Entry(f"catalog.family.{family}", D(CATALOG, "count_where", "/codes", "family", family),
                             "count", f"Codes in the family {family}."))
    return entries


IDENTITY_UNITS: tuple[tuple[str, str, str], ...] = (
    # (key in identity_pins.json, id part, plain description)
    ("alpha", "alpha.decode", "the decode-workload members of the ALPHA pack"),
    ("alpha/prefill_p2048", "alpha.prefill_p2048", "the prefill-workload members of the ALPHA pack"),
    ("beta", "beta.decode", "the decode-workload members of the BETA pack"),
    ("beta/prefill_p2048", "beta.prefill_p2048", "the prefill-workload members of the BETA pack"),
    ("A/decode", "gamma.a.decode", "side A (Qwen3-1.7B) of the decode-workload quads of the GAMMA pack"),
    ("A/prefill_p2048", "gamma.a.prefill_p2048",
     "side A (Qwen3-1.7B) of the prefill-workload quads of the GAMMA pack"),
    ("B/decode", "gamma.b.decode", "side B (Qwen3-8B) of the decode-workload quads of the GAMMA pack"),
    ("B/prefill_p2048", "gamma.b.prefill_p2048",
     "side B (Qwen3-8B) of the prefill-workload quads of the GAMMA pack"),
    ("neg8_reference", "reference", "the reference members and their spares"),
)


def _identity_entries() -> list[Entry]:
    entries = [
        Entry("runtime.python", J(PINS, "/runtime_versions/python"), "text",
              "Version of the Python interpreter that runs the members."),
        Entry("runtime.versions_sha256", J(PINS, "/runtime_versions_sha256"), "sha256",
              "SHA-256 over the interpreter version (runtime.python) and the package versions "
              "(runtime.package.*)."),
        Entry("identity.units", D(PINS, "count", "/units"), "count", "Number of identity units."),
    ]
    for package in ("mlx", "mlx-lm", "mlx-metal", "numpy", "safetensors", "tokenizers", "transformers"):
        entries.append(Entry(f"runtime.package.{package}", J(PINS, f"/runtime_versions/packages/{package}"),
                             "text", f"Installed version of the Python package {package}."))
    stack = (
        ("os_version", "/stack_identity/os_version", "text",
         "The operating-system version string recorded for the members."),
        ("machine", "/stack_identity/hardware_unit/machine", "text", "The processor architecture."),
        ("hardware_config_id", "/stack_identity/hardware_unit/config_id", "text",
         "The project's identifier for the machine."),
        ("telemetry_backend", "/stack_identity/telemetry_backend", "text",
         "The sampler program, as named in every record."),
        ("boundary", "/stack_identity/measurement_boundary_label/boundary", "text",
         "What the sampler's power covers (the measurement boundary), as labelled in every record."),
        ("rails", "/stack_identity/measurement_boundary_label/rails", "list",
         "The sampler's power fields that are added to give the processor-rail power."),
        ("runtime_name", "/stack_identity/runtime_version/name", "text", "The inference runtime."),
        ("runtime_version", "/stack_identity/runtime_version/version", "text",
         "Version of the inference runtime."),
        ("sampler_kind", "/stack_identity/sampler_output_policy/sampler/kind", "text",
         "How the next output token is chosen."),
        ("sampler_temperature", "/stack_identity/sampler_output_policy/sampler/temperature", "number",
         "The sampling temperature (0 gives the most likely token every time)."),
        ("batching_policy", "/stack_identity/batching_concurrency_policy", "text",
         "How requests are batched."),
        ("quantization_bits", "/stack_identity/quantization/bits", "bits",
         "Bits per weight of every model used."),
        ("quantization_name", "/stack_identity/quantization/name", "text",
         "Name of the weight quantization of every model used."),
        ("output_policy", "/output_policy/name", "text", "How the length of a member's output is fixed."),
    )
    for name, sub, unit, what in stack:
        also = (J(PINS, "/runtime_versions/packages/mlx"),) if name == "runtime_version" else ()
        entries.append(Entry(f"stack.{name}", D(PINS, "common", "/units", sub), unit,
                             f"{what} Every identity unit states the same value.", also=also))
    for key, part, described in IDENTITY_UNITS:
        base = "/units/" + key.replace("~", "~0").replace("/", "~1")
        fields = (
            ("pack_id", "/pack_id", "text", "Identifier of the pack or reference set that holds"),
            ("model_name", "/model_name", "text", "Model run by"),
            ("model_revision", "/model_revision", "text", "Published revision of the model run by"),
            ("model_artifact_sha256", "/model_artifact_sha256", "sha256",
             "SHA-256 identifying the model files of"),
            ("runtime_identity_sha256", "/runtime_identity_sha256", "sha256",
             "SHA-256 over the whole runtime configuration (machine, system, runtime, model, quantization, "
             "sampler, output length) of"),
            ("config_count", "/config_count", "count", "Number of member configurations in the group:"),
            ("config_set_sha256", "/config_set_sha256", "sha256",
             "SHA-256 over the member configurations of"),
            ("requested_tokens", "/output_policy/requested_tokens", "tokens",
             "Output tokens generated, exactly, by each of"),
            ("stop_condition", "/output_policy/stop_condition", "text", "What ends the generation of each of"),
        )
        for name, sub, unit, lead in fields:
            entries.append(Entry(f"identity.{part}.{name}", J(PINS, base + sub), unit, f"{lead} {described}."))
    return entries


def manifest() -> list[Entry]:
    entries = (_status_entries() + _chain_entries() + _arm_entries() + _monitor_entries() + _driver_entries()
               + _member_entries() + _workload_entries() + _harvest_entries() + _reference_entries()
               + _estimator_entries() + _sizing_entries() + _catalog_entries() + _identity_entries())
    seen: set[str] = set()
    for entry in entries:
        if entry.id in seen:
            raise ExtractionError(f"the manifest names {entry.id} twice")
        if entry.unit not in UNITS:
            raise ExtractionError(f"{entry.id}: unit {entry.unit!r} is not in the unit list")
        seen.add(entry.id)
    return entries


def all_refs(entries: Sequence[Entry]) -> list[Ref]:
    return [ref for entry in entries for ref in (entry.ref, *entry.also)]


# --------------------------------------------------------------------------
# Building and rendering the document


def _ref_record(ref: Ref) -> dict[str, Any]:
    return {"kind": ref.kind, "file": ref.file, "key": ref.key}


def build_document(tree: Tree, python_values: Mapping[PythonKey, Any],
                   entries: Sequence[Entry] | None = None) -> dict[str, Any]:
    """Resolve every entry.  ``python_values`` comes from :func:`read_python_constants`."""

    entries = manifest() if entries is None else entries
    sources = Sources(tree)
    values: dict[str, Any] = {}
    disagreements: list[str] = []
    for entry in entries:
        value = resolve(entry.ref, sources, python_values)
        record: dict[str, Any] = {"value": value, "unit": entry.unit, "what": entry.what,
                                  "source": _ref_record(entry.ref)}
        if entry.also:
            record["also"] = []
            for ref in entry.also:
                other = resolve(ref, sources, python_values)
                record["also"].append({**_ref_record(ref), "value": other})
                if not same_value(value, other) and entry.id not in disagreements:
                    disagreements.append(entry.id)
        values[entry.id] = record
    files: set[tuple[str, str]] = set()
    for ref in all_refs(entries):
        if ref.kind == "config-set":
            files.update((directory, "directory of member configurations") for directory in ref.dirs)
        else:
            files.add((ref.file, "json" if ref.kind == "derived" else ref.kind))
    return {
        "schema": SCHEMA,
        "about": ("Registered design values of measurement block 5, each read from the committed file and key "
                  "named beside it. Generated; do not edit. Paper B takes its design numbers from here. It "
                  "holds no measured energy and no result."),
        "generated_by": TOOL_RELATIVE,
        "regenerate": f"python3 -B {TOOL_RELATIVE} --write",
        "how_to_cite": "In paper text, put <!-- rv: ID --> beside a number taken from this table, with ID the "
                       "entry's key under \"values\".",
        "reading_an_entry": ("\"value\" was read at \"source\" (file and key). \"also\" lists other committed "
                             "places that state the same quantity, each with the value found there; an entry "
                             "whose places differ is listed under \"disagreements\"."),
        "glossary": [{"term": term, "meaning": meaning} for term, meaning in GLOSSARY],
        "sources": [{"file": file, "kind": kind} for file, kind in sorted(files)],
        "disagreements": sorted(disagreements),
        "values": values,
    }


def render(document: Mapping[str, Any]) -> bytes:
    """The committed bytes: two-space indent, entries sorted by id, one trailing newline."""

    ordered = dict(document)
    ordered["values"] = {key: document["values"][key] for key in sorted(document["values"])}
    return (json.dumps(ordered, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def generate(root: Path) -> bytes:
    """Read every source under ``root`` and return the table's bytes."""

    entries = manifest()
    python_values = read_python_constants(root, all_refs(entries))
    return render(build_document(Tree(root), python_values, entries))


def describe_difference(committed: bytes, regenerated: bytes) -> list[str]:
    """Plain lines saying which entries differ between two renderings of the table."""

    try:
        old, new = json.loads(committed), json.loads(regenerated)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return ["the committed file does not parse as JSON"]
    lines: list[str] = []
    old_values, new_values = old.get("values", {}), new.get("values", {})
    for key in sorted(set(old_values) | set(new_values)):
        if key not in new_values:
            lines.append(f"{key}: in the committed file, no longer produced")
        elif key not in old_values:
            lines.append(f"{key}: produced now, missing from the committed file")
        elif old_values[key] != new_values[key]:
            before, after = old_values[key].get("value"), new_values[key].get("value")
            if before != after:
                lines.append(f"{key}: value {json.dumps(before)} in the committed file, {json.dumps(after)} now")
            else:
                lines.append(f"{key}: same value, but its source, unit or description changed")
    for key in sorted(set(old) | set(new)):
        if key != "values" and old.get(key) != new.get(key):
            lines.append(f"top-level field {key!r} differs")
    return lines or ["the bytes differ only in layout"]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract Paper B's registered design values.")
    parser.add_argument("--root", type=Path, default=REPO_ROOT,
                        help="the repository tree to read (default: the tree this program is in)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true",
                      help="regenerate and compare with the committed table; exit 1 if they differ (default)")
    mode.add_argument("--write", action="store_true", help="regenerate and write the table")
    mode.add_argument("--stdout", action="store_true", help="regenerate and print the table")
    mode.add_argument("--get", metavar="ID", help="print one entry of the regenerated table")
    mode.add_argument("--list", action="store_true", help="print every id with its value and unit")
    parser.add_argument("--against", type=Path, default=None,
                        help="with --check: the table to compare with (default: the one under --root)")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        produced = generate(root)
    except ExtractionError as exc:
        print(f"extract_registered_values: {exc}", file=sys.stderr)
        return 2
    document = json.loads(produced)
    for entry_id in document["disagreements"]:
        print(f"extract_registered_values: DISAGREEMENT {entry_id}: its sources state different values",
              file=sys.stderr)
    if args.write:
        target = root / OUTPUT_RELATIVE
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(produced)
        print(f"wrote {target} ({len(document['values'])} values)")
        return 0
    if args.stdout:
        sys.stdout.buffer.write(produced)
        return 0
    if args.get:
        if args.get not in document["values"]:
            print(f"extract_registered_values: no entry {args.get!r}", file=sys.stderr)
            return 2
        print(json.dumps({args.get: document["values"][args.get]}, indent=2, ensure_ascii=False))
        return 0
    if args.list:
        for entry_id, record in document["values"].items():
            print(f"{entry_id}\t{json.dumps(record['value'], ensure_ascii=False)}\t{record['unit']}")
        return 0
    against = args.against if args.against is not None else root / OUTPUT_RELATIVE
    try:
        committed = against.read_bytes()
    except OSError as exc:
        print(f"extract_registered_values: {against}: cannot be read ({exc})", file=sys.stderr)
        return 2
    if committed == produced:
        print(f"{against}: up to date ({len(document['values'])} values)")
        return 0
    print(f"{against}: differs from the values now in the sources. Regenerate with --write and re-sync the "
          "text that cites these entries:", file=sys.stderr)
    for line in describe_difference(committed, produced):
        print(f"  {line}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
