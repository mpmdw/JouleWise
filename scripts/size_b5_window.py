#!/usr/bin/env python3
"""Size the three block-5 windows (ALPHA, BETA, GAMMA): programmed span, T_stream_max, window maximum.

Registration FILL B5-SIZING-OUTPUTS needs, per full pack, the chain's
programmed span and T_stream_max as sizing allowances
(``{seconds, source: {path, sha256}, source_pointer}``, the form of block 4's
``configs/campaigns/v5_qualification_25g83/sizing_allowances.json``), which the
block-5 plan writer (``joulewise.b5.plan.read_allowance``) reads against a
committed sizing output. This program writes that output,
``configs/campaigns/v5_claim_25g83/sizing_b5.json``, and prints the six
allowance objects that point into it (they cannot live inside the file they
hash).

Inputs, all committed:

* block 4's sizing source (``sizing_sources/sizing_source_v2.json``), found and
  authenticated through block 4's adapter: per-member allowances for the small
  (Qwen3-1.7B) and large (Qwen3-8B) models (load, warm-up, prefill, forced
  decode, the cooldown at its 300 s cap and both idle-admission attempts),
  stream lengths, the calibration pair, the bound derivation, the terminal
  shutdown, the 3300 s T-0 stage cap and the labelled stage-custody terms of
  its formula string;
* the model of each block-4 member, from the configs that source names, which
  gives each model its class (auxiliary NEG-8 and reference members use the
  small proxy, as block 4 did: ruling 76 A.3);
* each pack's ``plan_tree.json`` stage graph, walked with
  ``joulewise.b5.chain.stage_plan`` (the chain renderer's own walk), and each
  collection stage's order manifest and configs (bytes checked against their
  recorded SHA-256), which give the roster: members per stage and per class,
  and each stage's ``--arm-countdown-s``;
* the chain's settle, ``joulewise.b5.chain.SETTLE_S`` (180 s, before the pre
  slot and before every collection stage).

Programmed span (block 4's conventions with block 5's chain)::

    (1 + stages) * settle + sum(stage countdowns) + calibration pair
    + bound derivation + sum(member allowances)
    + stages * stage overhead + members * (reduction + native sampler start + wind-down)
    + calibration captures * bracket writer custody + reservation + terminal custody
    + terminal shutdown

Block 4's 360 s pack launch allowance is not in the chain any more (the arm's
3300 s holds the launch; registration 5.5). The same arithmetic with block 4's
600 s settle and that 360 s reproduces block 4's committed 3571 s custody,
22494 s span and 25800 s window, or this program refuses.

``WINDOW_MAX_S`` = 60 * ceil((span + 3300) / 60), the plan writer's formula.
T_stream_max: each pack's longest member or bracket stream is recorded, and
every pack's ``T_stream_max_s`` is the longest stream any ``_v5`` member can
have (the maximum over the three packs), as registration 0.14 and 5.5 define
it. The clock gate 3.7 ms + (|f| + 0.25 ppm) * T_stream_max <= 5 ms
(``joulewise.hazards.clock.frequency_bound``) must still pass at |f| = 3.6 ppm;
a pack whose longest stream fails it is reported and the exit status is 3.

Nothing here reads a bundle, arms, installs or launches.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import math
import os
import re
import sys
import tempfile
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.b5 import chain as b5_chain  # noqa: E402
from joulewise.hazards import clock as clock_hazard  # noqa: E402

SCHEMA = "joulewise.b5_sizing.v1"
STATUS_UNSEALED = "UNSEALED_DRAFT"
DEFAULT_OUTPUT = "configs/campaigns/v5_claim_25g83/sizing_b5.json"
DEFAULT_ADAPTER = "configs/campaigns/v5_qualification_25g83/sizing_allowances.json"
ADAPTER_SCHEMA = "joulewise.v5_qualification_sizing_allowances.v1"
DEFAULT_PACKS = (
    ("ALPHA", "configs/campaigns/d117_floor_qwen3-1p7b_v5"),
    ("BETA", "configs/campaigns/d117_floor_qwen3-8b_v5"),
    ("GAMMA", "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"),
)
MEMBER_TERMS = ("load", "warmup", "prefill", "forced_decode", "cooldown", "idle_admission")
REQUIRED_ABS_F_PPM = Fraction(36, 10)
COUNTDOWN_FLAG = "--arm-countdown-s"

# Block 4's labelled stage-custody allocations, read from the source's formula string.
CUSTODY_FORMULA_POINTER = "/derivations/stage_custody/formula"
CUSTODY_FORMULA_RE = re.compile(
    r"^(?P<stages>\d+)\*(?P<stage_overhead>\d+) stage overhead "
    r"\+(?P<captures>\d+)\*(?P<reduction>\d+) reductions "
    r"\+(?P<brackets>\d+)\*(?P<bracket_custody>\d+) bracket writer custody "
    r"\+(?P<reservation>\d+) reservation "
    r"\+(?P<terminal_custody>\d+) terminal custody "
    r"\+(?P<captures2>\d+)\*\((?P<sampler_start>\d+)\+(?P<sampler_winddown>\d+)\) native sampler custody "
    r"=(?P<total>\d+)$")
SETTLES_FORMULA_POINTER = "/derivations/fixed_settles"
SETTLES_FORMULA_RE = re.compile(
    r"^(?P<settles>\d+)\*(?P<settle>\d+) \+ (?P<countdowns>\d+)\*(?P<countdown>\d+) =(?P<total>\d+)\b")


class SizingError(ValueError):
    """The windows cannot be sized from the committed inputs; nothing was written."""


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise SizingError(detail)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _read_json(path: Path, label: str) -> tuple[Any, bytes]:
    try:
        raw = path.read_bytes()
        return json.loads(raw), raw
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SizingError(f"{label} {path} cannot be read: {exc}") from exc


def _relative(root: Path, value: Any, label: str) -> Path:
    _require(isinstance(value, str) and value and not PurePosixPath(value).is_absolute()
             and ".." not in PurePosixPath(value).parts, f"{label} must be a relative path without '..'")
    return root / value


def json_pointer(document: Any, pointer: str) -> Any:
    _require(isinstance(pointer, str) and pointer.startswith("/"), f"pointer {pointer!r} must start with /")
    node = document
    for part in pointer[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(node, list) and part.isdigit() and int(part) < len(node):
            node = node[int(part)]
        elif isinstance(node, Mapping) and part in node:
            node = node[part]
        else:
            raise SizingError(f"pointer {pointer!r} does not resolve in the sizing source")
    return node


@dataclasses.dataclass(frozen=True)
class Source:
    """Block 4's committed sizing source, authenticated through its adapter."""

    path: str  # relative to the repository
    sha256: str
    document: Mapping[str, Any]
    adapter_path: str
    adapter_sha256: str
    adapter: Mapping[str, Any]

    def allowance(self, pointer: str) -> dict[str, Any]:
        value = json_pointer(self.document, pointer)
        _require(isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0,
                 f"{pointer} is not a non-negative number")
        return {"seconds": value, "source": {"path": self.path, "sha256": self.sha256}, "source_pointer": pointer}

    def seconds(self, pointer: str) -> int:
        value = self.allowance(pointer)["seconds"]
        _require(float(value).is_integer(), f"{pointer} is not a whole number of seconds")
        return int(value)


def _adapter_allowances(node: Any) -> list[Mapping[str, Any]]:
    if isinstance(node, Mapping):
        if set(node) == {"seconds", "source", "source_pointer"}:
            return [node]
        return [item for value in node.values() for item in _adapter_allowances(value)]
    return []


def load_source(repo: Path, adapter_relative: str = DEFAULT_ADAPTER) -> Source:
    adapter, adapter_raw = _read_json(_relative(repo, adapter_relative, "adapter"), "sizing adapter")
    _require(isinstance(adapter, Mapping) and adapter.get("schema_version") == ADAPTER_SCHEMA,
             f"{adapter_relative} is not a {ADAPTER_SCHEMA} document")
    allowances = _adapter_allowances(adapter)
    sources = {(item["source"].get("path"), item["source"].get("sha256")) for item in allowances
               if isinstance(item.get("source"), Mapping)}
    _require(len(sources) == 1, f"{adapter_relative} must cite exactly one sizing source, found {sorted(sources)}")
    path, digest = next(iter(sources))
    document, raw = _read_json(_relative(repo, path, "sizing source"), "sizing source")
    _require(sha256_bytes(raw) == digest, f"sizing source {path} does not hash to the adapter's {digest}")
    for item in allowances:
        _require(json_pointer(document, item["source_pointer"]) == item["seconds"],
                 f"adapter allowance {item['source_pointer']} disagrees with the source")
    return Source(path, digest, document, adapter_relative, sha256_bytes(adapter_raw), adapter)


@dataclasses.dataclass(frozen=True)
class Custody:
    stage_overhead_s: int
    reduction_s: int
    bracket_custody_s: int
    reservation_s: int
    terminal_custody_s: int
    sampler_start_s: int
    sampler_winddown_s: int

    def total(self, *, stages: int, members: int, calibrations: int, reservations: int) -> int:
        return (stages * self.stage_overhead_s + members * self.reduction_s
                + calibrations * self.bracket_custody_s + reservations * self.reservation_s
                + self.terminal_custody_s + members * (self.sampler_start_s + self.sampler_winddown_s))


def custody_terms(source: Source) -> tuple[Custody, dict[str, int]]:
    """Block 4's labelled stage-custody allocations, checked against its own numbers."""

    formula = json_pointer(source.document, CUSTODY_FORMULA_POINTER)
    match = CUSTODY_FORMULA_RE.match(formula) if isinstance(formula, str) else None
    _require(match is not None, f"{CUSTODY_FORMULA_POINTER} is not the stage-custody formula this program reads: "
                                f"{formula!r}")
    values = {name: int(value) for name, value in match.groupdict().items()}
    _require(values["captures"] == values["captures2"], "the custody formula counts captures twice differently")
    terms = Custody(values["stage_overhead"], values["reduction"], values["bracket_custody"],
                    values["reservation"], values["terminal_custody"], values["sampler_start"],
                    values["sampler_winddown"])
    recomputed = terms.total(stages=values["stages"], members=values["captures"], calibrations=values["brackets"],
                             reservations=1)
    _require(recomputed == values["total"] == source.seconds("/fixed/stage_custody"),
             f"the custody formula evaluates to {recomputed}, states {values['total']}, the source fixes "
             f"{source.seconds('/fixed/stage_custody')}")
    _require(terms.reduction_s == source.seconds("/derivations/stage_custody/reduction_allowance_s"),
             "the formula's reduction allowance differs from /derivations/stage_custody/reduction_allowance_s")
    _require(terms.sampler_start_s + terms.sampler_winddown_s
             == source.seconds("/derivations/stream_max/native_sampler_overhead/per_member_wall_s"),
             "the formula's native sampler custody differs from per_member_wall_s")
    return terms, values


def member_allowance(source: Source, klass: str) -> int:
    return sum(source.seconds(f"/members/{klass}/{term}") for term in MEMBER_TERMS)


def class_map(source: Source, repo: Path) -> tuple[dict[str, str], str]:
    """Model source -> member class, from block 4's members; and the auxiliary class."""

    members = (source.adapter.get("sizing") or {}).get("members") or {}
    inventory = {row.get("run_id"): row for row in
                 (source.document.get("provenance") or {}).get("config_inventory") or []}
    mapping: dict[str, set[str]] = {}
    for run_id, terms in members.items():
        classes = {str(item["source_pointer"]).split("/")[2] for item in terms.values()}
        _require(len(classes) == 1, f"block-4 member {run_id} mixes member classes {sorted(classes)}")
        row = inventory.get(run_id)
        _require(isinstance(row, Mapping), f"block-4 member {run_id} has no config in the source inventory")
        config, raw = _read_json(_relative(repo, row["source"]["path"], "block-4 config"), "block-4 config")
        _require(sha256_bytes(raw) == row["source"]["sha256"], f"block-4 config of {run_id} changed")
        mapping.setdefault(config["model"]["source"], set()).update(classes)
    _require(bool(mapping) and all(len(classes) == 1 for classes in mapping.values()),
             f"block-4 members do not give each model one class: {mapping}")
    streams = (source.adapter.get("sizing") or {}).get("streams") or {}
    auxiliary = {str(item["source_pointer"]).split("/")[2] for name, item in streams.items()
                 if name not in members and not str(item["source_pointer"]).endswith("/bracket")}
    _require(len(auxiliary) == 1, f"block-4 auxiliary streams use more than one class: {sorted(auxiliary)}")
    return {model: next(iter(classes)) for model, classes in sorted(mapping.items())}, next(iter(auxiliary))


def _recorded_digests(tree: Mapping[str, Any], pack: Path, repo: Path) -> dict[Path, set[str]]:
    """Every SHA-256 the plan tree records for a config or order manifest, by resolved path.

    The floor packs record stage inputs as ``input`` (repository-relative) and
    the shared auxiliary members under ``external_inputs.manifests``; the
    contrast pack records ``input_ref`` (pack-relative) and lists
    ``external_inputs`` with each manifest's path and digest. Science rows and
    the identity units' config inventories name every science config.
    """

    recorded: dict[Path, set[str]] = {}

    def note(base: Path, relative: Any, digest: Any) -> None:
        if isinstance(relative, str) and relative and isinstance(digest, str):
            recorded.setdefault((base / relative).resolve(), set()).add(digest)

    def note_either(relative: Any, digest: Any) -> None:
        if isinstance(relative, str):
            note(repo if relative.startswith("configs/") else pack, relative, digest)

    for row in tree.get("stage_graph") or []:
        for key in ("input", "input_ref"):
            item = row.get(key)
            if isinstance(item, Mapping):
                note_either(item.get("path"), item.get("sha256"))
    external = tree.get("external_inputs")
    manifests = external.get("manifests", []) if isinstance(external, Mapping) else (external or [])
    for manifest in manifests:
        if isinstance(manifest, Mapping):
            note_either(manifest.get("manifest_path"), manifest.get("manifest_sha256"))
            for member in manifest.get("members") or []:
                if isinstance(member, Mapping):
                    note_either(member.get("path"), member.get("sha256"))
    for row in tree.get("science") or []:
        if isinstance(row, Mapping):
            note_either(row.get("config_path"), row.get("config_sha256"))
    projection = (tree.get("arm_attachments") or {}).get("identity_pin_projection") or {}
    for unit in projection.get("identity_units") or []:
        for row in unit.get("config_inventory") or []:
            note(pack, row.get("path"), row.get("sha256"))
    return recorded


def _authenticated(path: Path, recorded: Mapping[Path, set[str]], also: Any, label: str) -> tuple[Any, bytes]:
    """Read ``path``; its bytes must match every digest recorded for it, and at least one must exist."""

    document, raw = _read_json(path, label)
    digests = set(recorded.get(path.resolve(), set()))
    if isinstance(also, str):
        digests.add(also)
    _require(bool(digests), f"{label} {path} has no recorded SHA-256 in the plan tree or its manifest")
    _require(digests == {sha256_bytes(raw)}, f"{label} {path} hashes to {sha256_bytes(raw)}, recorded {sorted(digests)}")
    return document, raw


def pack_roster(pack: Path, repo: Path, classes: Mapping[str, str], auxiliary_class: str) -> dict[str, Any]:
    """The pack's in-chain stages and members, with each member's class.

    Each collection stage's members are the ``executed_order`` of the order
    manifest in the directory its campaign command names (the first argument,
    a repository path): what the chain runs.
    """

    tree, raw = _read_json(pack / "plan_tree.json", "plan tree")
    try:
        stages = b5_chain.stage_plan(tree)
    except b5_chain.ChainRenderError as exc:
        raise SizingError(f"{pack.name}: stage graph: {exc}") from exc
    recorded = _recorded_digests(tree, pack, repo)
    rows = []
    for stage in (stage for stage in stages if stage.in_chain):
        entry: dict[str, Any] = {"stage_id": stage.stage_id, "ordinal": stage.ordinal, "kind": stage.kind}
        if stage.kind == "campaign_collection":
            first = stage.commands[0].arguments[0] if stage.commands[0].arguments else {}
            _require(first.get("kind") == "repo_path",
                     f"{stage.stage_id}: the campaign command's first argument is not a repository path")
            directory = _relative(repo, first["value"], f"{stage.stage_id} config directory")
            manifest_path = directory / "order_manifest.json"
            manifest, manifest_raw = _authenticated(manifest_path, recorded, None, f"{stage.stage_id} order manifest")
            order = manifest.get("executed_order") if isinstance(manifest, Mapping) else None
            _require(isinstance(order, list) and len(order) == stage.expected_count,
                     f"{stage.stage_id}: order manifest lists {len(order or [])} members, the stage expects "
                     f"{stage.expected_count}")
            science = pack.resolve() in directory.resolve().parents
            counts: dict[str, int] = {}
            for member in order:
                config, _config_raw = _authenticated(directory / str(member.get("config")), recorded,
                                                     member.get("config_sha256"), f"{stage.stage_id} config")
                model = (config.get("model") or {}).get("source")
                if science:
                    _require(model in classes, f"{stage.stage_id}: science model {model} has no block-4 class")
                    klass = classes[model]
                else:
                    klass = classes.get(model, auxiliary_class)
                counts[klass] = counts.get(klass, 0) + 1
            literals = [argument["value"] for argument in stage.commands[0].arguments
                        if argument["kind"] == "literal"]
            countdown = 0
            if COUNTDOWN_FLAG in literals:
                position = literals.index(COUNTDOWN_FLAG)
                _require(position + 1 < len(literals) and literals[position + 1].isdigit(),
                         f"{stage.stage_id}: {COUNTDOWN_FLAG} has no whole-second value")
                countdown = int(literals[position + 1])
            entry.update({"science": science, "members": stage.expected_count, "classes": dict(sorted(counts.items())),
                          "arm_countdown_s": countdown,
                          "order_manifest": {"path": manifest_path.resolve().relative_to(repo.resolve()).as_posix(),
                                             "sha256": sha256_bytes(manifest_raw)}})
        rows.append(entry)
    return {"plan_tree": {"path": (pack / "plan_tree.json").resolve().relative_to(repo.resolve()).as_posix(),
                          "sha256": sha256_bytes(raw)},
            "stages": rows}


def span_breakdown(*, settle_s: int, stages: int, countdowns_s: int, calibrations: int, reservations: int,
                   derivations: int, members_by_class: Mapping[str, int], member_s: Mapping[str, int],
                   calibration_pair_s: int, derivation_s: int, terminal_shutdown_s: int, custody: Custody,
                   pack_t0_s: int = 0) -> dict[str, int]:
    """Block 4's programmed-span arithmetic, with the chain's own counts."""

    _require(calibrations == 2, "a window has exactly one pre and one post calibration capture")
    members = sum(members_by_class.values())
    parts = {
        "pack_t0_s": pack_t0_s,
        "settles_s": (1 + stages) * settle_s,
        "arm_countdowns_s": countdowns_s,
        "pre_post_calibration_s": calibration_pair_s,
        "bound_derivation_s": derivations * derivation_s,
        "members_s": sum(count * member_s[klass] for klass, count in members_by_class.items()),
        "stage_custody_s": custody.total(stages=stages, members=members, calibrations=calibrations,
                                         reservations=reservations),
        "terminal_shutdown_s": terminal_shutdown_s,
    }
    parts["programmed_span_s"] = sum(parts.values())
    return parts


def window_max_s(span_s: int, t0_stage_cap_s: int) -> int:
    return 60 * math.ceil((span_s + t0_stage_cap_s) / 60)


def block4_reproduction(source: Source, custody: Custody, formula: Mapping[str, int],
                        auxiliary_class: str) -> dict[str, Any]:
    """Block 4's committed totals, recomputed with this program's arithmetic, or a refusal."""

    settles_formula = json_pointer(source.document, SETTLES_FORMULA_POINTER)
    match = SETTLES_FORMULA_RE.match(settles_formula) if isinstance(settles_formula, str) else None
    _require(match is not None, f"{SETTLES_FORMULA_POINTER} is not the settle formula this program reads")
    settles = {name: int(value) for name, value in match.groupdict().items()}
    stages, captures = formula["stages"], formula["captures"]
    _require(settles["settles"] == stages + 1 and settles["countdowns"] == stages
             and settles["total"] == source.seconds("/fixed/fixed_settles"),
             "block 4's settle formula does not match its stage count")
    members = (source.adapter.get("sizing") or {}).get("members") or {}
    science: dict[str, int] = {}
    for terms in members.values():
        klass = str(next(iter(terms.values()))["source_pointer"]).split("/")[2]
        science[klass] = science.get(klass, 0) + 1
    by_class = dict(science)
    by_class[auxiliary_class] = by_class.get(auxiliary_class, 0) + captures - sum(science.values())
    member_s = {klass: member_allowance(source, klass) for klass in by_class}
    parts = span_breakdown(settle_s=settles["settle"], stages=stages, countdowns_s=stages * settles["countdown"],
                           calibrations=formula["brackets"], reservations=1, derivations=1,
                           members_by_class=by_class, member_s=member_s,
                           calibration_pair_s=source.seconds("/fixed/pre_post_calibration"),
                           derivation_s=source.seconds("/auxiliary/gamma-bound-derivation"),
                           terminal_shutdown_s=source.seconds("/fixed/terminal_shutdown"), custody=custody,
                           pack_t0_s=source.seconds("/fixed/pack_t0"))
    window = window_max_s(parts["programmed_span_s"], source.seconds("/fixed/t0_stage_cap"))
    committed = {"E_small_L": source.seconds("/totals/E_small_L"), "E_large_L": source.seconds("/totals/E_large_L"),
                 "NIGHT_PROGRAMMED_SPAN_S_s1": source.seconds("/totals/NIGHT_PROGRAMMED_SPAN_S_s1"),
                 "WINDOW_MAX_S_s1": source.seconds("/totals/WINDOW_MAX_S_s1"),
                 "stage_custody": source.seconds("/fixed/stage_custody")}
    recomputed = {"E_small_L": member_s.get("small"), "E_large_L": member_s.get("large"),
                  "NIGHT_PROGRAMMED_SPAN_S_s1": parts["programmed_span_s"], "WINDOW_MAX_S_s1": window,
                  "stage_custody": parts["stage_custody_s"]}
    _require(recomputed == committed, f"this program's arithmetic does not reproduce block 4: "
                                      f"recomputed {recomputed}, committed {committed}")
    return {"members_by_class": dict(sorted(by_class.items())), "settle_s": settles["settle"], "stages": stages,
            "breakdown": parts, "window_max_s": window, "committed": committed, "reproduced": True}


def clock_gate(t_stream_max_s: int, required_ppm: Fraction = REQUIRED_ABS_F_PPM) -> dict[str, Any]:
    """``hazards.clock.frequency_bound`` at |f| = required_ppm (word rounded up) for this T_stream_max."""

    thresholds = dict(clock_hazard.DEFAULT_THRESHOLDS)
    thresholds["t_stream_max_s"] = t_stream_max_s
    raw_word = math.ceil(required_ppm * clock_hazard.FREQUENCY_SCALE)
    gate = clock_hazard.frequency_bound(raw_word, thresholds)
    return {"t_stream_max_s": t_stream_max_s, "required_abs_frequency_ppm": float(required_ppm),
            "bound_ms_at_required": gate["bound_ms"], "limit_ms": gate["limit_ms"],
            "max_abs_frequency_ppm": gate["max_abs_frequency_ppm"], "passes_at_required": bool(gate["passes"])}


def stream_limit_s(required_ppm: Fraction = REQUIRED_ABS_F_PPM) -> float:
    """The longest stream for which the gate still passes at |f| = required_ppm."""

    thresholds = clock_hazard.DEFAULT_THRESHOLDS
    h_s = Fraction(str(thresholds["h_ms"])) / 1000
    limit_s = Fraction(str(thresholds["limit_ms"])) / 1000
    margin = Fraction(str(thresholds["frequency_margin_ppm"]))
    return float((limit_s - h_s) * 1_000_000 / (required_ppm + margin))


def derive_document(repo: Path, packs: Sequence[tuple[str, str]], adapter: str = DEFAULT_ADAPTER) -> dict[str, Any]:
    source = load_source(repo, adapter)
    custody, formula = custody_terms(source)
    classes, auxiliary_class = class_map(source, repo)
    member_classes = sorted(set(classes.values()) | {auxiliary_class})
    member_s = {klass: member_allowance(source, klass) for klass in member_classes}
    stream_s = {klass: source.seconds(f"/streams/{klass}") for klass in member_classes}
    bracket_stream_s = source.seconds("/streams/bracket")
    t0_cap_s = source.seconds("/fixed/t0_stage_cap")
    reproduction = block4_reproduction(source, custody, formula, auxiliary_class)
    packs_out: dict[str, Any] = {}
    for label, relative in packs:
        pack = _relative(repo, relative, f"pack {label}")
        roster = pack_roster(pack, repo, classes, auxiliary_class)
        collections = [stage for stage in roster["stages"] if stage["kind"] == "campaign_collection"]
        by_class: dict[str, int] = {}
        for stage in collections:
            for klass, count in stage["classes"].items():
                by_class[klass] = by_class.get(klass, 0) + count
        kinds = [stage["kind"] for stage in roster["stages"]]
        parts = span_breakdown(
            settle_s=b5_chain.SETTLE_S, stages=len(collections),
            countdowns_s=sum(stage["arm_countdown_s"] for stage in collections),
            calibrations=kinds.count("calibration_capture"), reservations=kinds.count("bracket_reservation"),
            derivations=kinds.count("bound_derivation"), members_by_class=by_class, member_s=member_s,
            calibration_pair_s=source.seconds("/fixed/pre_post_calibration"),
            derivation_s=source.seconds("/auxiliary/gamma-bound-derivation"),
            terminal_shutdown_s=source.seconds("/fixed/terminal_shutdown"), custody=custody)
        longest = max([stream_s[klass] for klass in by_class] + [bracket_stream_s])
        packs_out[label] = {
            "pack_id": pack.name,
            **roster,
            "members": sum(by_class.values()),
            "science_members": sum(stage["members"] for stage in collections if stage["science"]),
            "auxiliary_members": sum(stage["members"] for stage in collections if not stage["science"]),
            "members_by_class": dict(sorted(by_class.items())),
            "collection_stages": len(collections),
            "breakdown": parts,
            "programmed_span_s": parts["programmed_span_s"],
            "window_max_s": window_max_s(parts["programmed_span_s"], t0_cap_s),
            "pack_longest_stream_s": longest,
        }
    block_stream = max(pack["pack_longest_stream_s"] for pack in packs_out.values())
    limit = stream_limit_s()
    for pack in packs_out.values():
        pack["T_stream_max_s"] = block_stream
        pack["clock_gate"] = {"at_T_stream_max": clock_gate(block_stream),
                              "at_pack_longest_stream": clock_gate(pack["pack_longest_stream_s"]),
                              "pack_longest_stream_within_limit": pack["pack_longest_stream_s"] <= limit}
    return {
        "schema_version": SCHEMA,
        "status": STATUS_UNSEALED,
        "sealed": False,
        "note": ("UNSEALED DRAFT. Generated by scripts/size_b5_window.py from block 4's committed sizing source "
                 "and the three packs' stage graphs, order manifests and configs. The seal binds this file's "
                 "SHA-256 (FILL[B5-SIZING-OUTPUTS]); the window plan inputs cite /packs/<label>/programmed_span_s "
                 "and /packs/<label>/T_stream_max_s in it."),
        "source": {"path": source.path, "sha256": source.sha256},
        "adapter": {"path": source.adapter_path, "sha256": source.adapter_sha256},
        "conventions": [
            "programmed span = (1 + collection stages) * settle + stage arm countdowns + pre/post calibration pair "
            "+ bound derivation + member allowances + stage custody + terminal shutdown",
            "member allowance = load + warmup + prefill + forced_decode + cooldown (300 s cap) + idle_admission "
            "(both attempts), per class from block 4's source",
            "stage custody = stages * stage overhead + members * reduction + calibration captures * bracket writer "
            "custody + reservation + terminal custody + members * (native sampler start + wind-down)",
            "auxiliary NEG-8 and reference members use the small-model allowance (block 4, ruling 76 A.3)",
            "block 4's 360 s pack launch allowance is outside the chain in block 5 (registration 5.5)",
            "WINDOW_MAX_S = 60 * ceil((programmed span + T0_STAGE_CAP_S) / 60)",
            "T_stream_max_s = the longest stream any _v5 member can have (registration 0.14, 5.5); "
            "pack_longest_stream_s is the pack's own",
        ],
        "terms": {
            "members": {klass: {term: source.allowance(f"/members/{klass}/{term}") for term in MEMBER_TERMS}
                        for klass in member_classes},
            "member_allowance_s": member_s,
            "streams": {name: source.allowance(f"/streams/{name}") for name in member_classes + ["bracket"]},
            "pre_post_calibration": source.allowance("/fixed/pre_post_calibration"),
            "bound_derivation": source.allowance("/auxiliary/gamma-bound-derivation"),
            "terminal_shutdown": source.allowance("/fixed/terminal_shutdown"),
            "t0_stage_cap": source.allowance("/fixed/t0_stage_cap"),
            "clean_dwell_cap": source.allowance("/derivations/t0_stage_cap/clean_dwell_cap_s"),
            "reduction_per_member": source.allowance("/derivations/stage_custody/reduction_allowance_s"),
            "native_sampler_per_member": source.allowance(
                "/derivations/stream_max/native_sampler_overhead/per_member_wall_s"),
            "stage_custody_formula": {"source": {"path": source.path, "sha256": source.sha256},
                                      "source_pointer": CUSTODY_FORMULA_POINTER,
                                      **dataclasses.asdict(custody)},
            "settle_s": {"seconds": b5_chain.SETTLE_S, "source": "joulewise/b5/chain.py SETTLE_S"},
        },
        "class_map": {"model_source": classes, "auxiliary": auxiliary_class,
                      "derived_from": "block 4's adapter members and the configs its source inventory names"},
        "block4_reproduction": reproduction,
        "clock_gate": {"source": "joulewise/hazards/clock.py DEFAULT_THRESHOLDS and frequency_bound",
                       "h_ms": clock_hazard.DEFAULT_THRESHOLDS["h_ms"],
                       "frequency_margin_ppm": clock_hazard.DEFAULT_THRESHOLDS["frequency_margin_ppm"],
                       "limit_ms": clock_hazard.DEFAULT_THRESHOLDS["limit_ms"],
                       "required_abs_frequency_ppm": float(REQUIRED_ABS_F_PPM),
                       "stream_limit_s": limit},
        "block": {"T_stream_max_s": block_stream,
                  "longest_packs": sorted(label for label, pack in packs_out.items()
                                          if pack["pack_longest_stream_s"] == block_stream)},
        "packs": packs_out,
    }


def allowances(document: Mapping[str, Any], path: str, sha256: str) -> dict[str, dict[str, Any]]:
    """The window plan inputs' two sizing allowances per pack, pointing into the written file."""

    return {label: {name: {"seconds": pack[name], "source": {"path": path, "sha256": sha256},
                           "source_pointer": f"/packs/{label}/{name}"}
                    for name in ("programmed_span_s", "T_stream_max_s")}
            for label, pack in document["packs"].items()}


def render(document: Mapping[str, Any]) -> bytes:
    return (json.dumps(document, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _atomic_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        if os.path.exists(temporary):
            os.unlink(temporary)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", type=Path, default=REPO_ROOT, help="checkout holding the packs and block 4's source")
    parser.add_argument("--adapter", default=DEFAULT_ADAPTER, help="block 4's sizing adapter, relative to --repo")
    parser.add_argument("--pack", action="append", default=None, metavar="LABEL=PATH",
                        help="pack label and directory relative to --repo (repeatable; default ALPHA, BETA, GAMMA)")
    parser.add_argument("--out", default=DEFAULT_OUTPUT, help="output, relative to --repo")
    parser.add_argument("--check", action="store_true", help="compare with the existing file instead of writing")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo = args.repo.resolve()
    packs = DEFAULT_PACKS
    if args.pack:
        packs = tuple(tuple(item.split("=", 1)) for item in args.pack)  # type: ignore[misc]
        if any(len(item) != 2 for item in packs):
            print("REFUSED: --pack takes LABEL=PATH", file=sys.stderr)
            return 2
    try:
        out = _relative(repo, args.out, "--out")
        document = derive_document(repo, packs, args.adapter)
    except SizingError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    raw = render(document)
    digest = sha256_bytes(raw)
    if args.check:
        if not out.is_file() or out.read_bytes() != raw:
            print(f"DIFFERS: {out} is not what the sizer writes now", file=sys.stderr)
            return 1
    else:
        _atomic_write(out, raw)
    failing = sorted(label for label, pack in document["packs"].items()
                     if not pack["clock_gate"]["pack_longest_stream_within_limit"]
                     or not pack["clock_gate"]["at_T_stream_max"]["passes_at_required"])
    summary = {label: {"programmed_span_s": pack["programmed_span_s"], "window_max_s": pack["window_max_s"],
                       "T_stream_max_s": pack["T_stream_max_s"], "pack_longest_stream_s": pack["pack_longest_stream_s"],
                       "max_abs_frequency_ppm": pack["clock_gate"]["at_T_stream_max"]["max_abs_frequency_ppm"]}
               for label, pack in document["packs"].items()}
    print(json.dumps({"path": args.out, "sha256": digest, "status": document["status"], "packs": summary,
                      "allowances": allowances(document, args.out, digest),
                      "clock_gate_failing_packs": failing}, indent=2, sort_keys=True))
    if failing:
        print(f"CLOCK GATE: {failing} have a stream longer than {document['clock_gate']['stream_limit_s']:.2f} s, "
              f"so the frequency gate would refuse below |f| = 3.6 ppm", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
