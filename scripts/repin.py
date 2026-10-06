#!/usr/bin/env python3
"""Check and regenerate hard-coded pins: one command instead of hand repins.

Lane L7 (Ed's point c, 2026-10-05). Pins that must stay hard-coded (Kind P in
``configs/pins/registry.json``: they protect a number) are checked here, and a
stale one fails with the command that regenerates it::

    pin <name> stale: <detail>: run python scripts/repin.py --write <name>

Usage::

    python scripts/repin.py --check              # every family (CI runs this)
    python scripts/repin.py --check <name> ...   # named families only
    python scripts/repin.py --write <name>       # regenerate one family
    python scripts/repin.py --list               # family names
    python scripts/repin.py check | repin <name> # the same, as subcommands

Families:

- ``g2_phase_d``, ``state``, ``paper_custody_fixture`` and ``pack:<pack>``
  wrap the existing generators' ``--check`` and write modes.
- ``registry`` re-verifies every resolved Kind-P row of the pin registry: it
  recomputes the pinned target's digest by the recorded method and requires
  the pinning file to still carry it. A tampered pack config, prompt pin or
  acceptance artifact therefore fails here. ``--write registry`` re-runs the
  census (new or moved literals); it never changes a pin.
- A registry family name (``pinned_config_copy``, ``estimator_code``, ...)
  given to ``--write`` rewrites stale literal copies held in test files. It
  refuses for issued artifacts (re-issue them with their issuer) and for
  frozen code (revert the edit or re-freeze through review); a pack's own
  pins are rewritten only by its generator.

CI only checks. Nothing here repins on its own.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from scripts import digest_pin_census as census  # noqa: E402

# Pack generators with a byte-exact --check. Frozen packs replay their issued
# bytes only in preserve mode. Packs whose generator has no --check (and the
# shared contrast library, which needs arguments) are covered by the registry
# rows alone.
PACK_CHECK_ARGS: dict[str, tuple[str, ...]] = {
    "d117_contrast_qwen25_1p5b_vs_7b_v1": (),
    "d117_contrast_qwen25_1p5b_vs_7b_v2": ("--preserve-current-frozen-bytes",),
    "d117_contrast_qwen25_1p5b_vs_7b_v3": ("--preserve-current-frozen-bytes",),
    "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5": (),
    "d117_floor_qwen25_1p5b_v1": (),
    "d117_floor_qwen25_1p5b_v2": ("--preserve-current-frozen-bytes",),
    "d117_floor_qwen25_1p5b_v3": ("--preserve-current-frozen-bytes",),
    "d117_floor_qwen25_7b_v1": (),
    "d117_floor_qwen25_7b_v2": ("--preserve-current-frozen-bytes",),
    "d117_floor_qwen25_7b_v3": ("--preserve-current-frozen-bytes",),
    "d117_floor_qwen3-1p7b_v5": (),
    "d117_floor_qwen3-8b_v5": (),
}

Runner = Callable[[list[str]], "subprocess.CompletedProcess[str]"]


def _run(argv: list[str]) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(argv, cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, check=False)


def _tail(output: str) -> str:
    lines = [line.strip() for line in output.strip().splitlines() if line.strip()]
    return lines[-1] if lines else "no output"


@dataclass
class CommandFamily:
    """A family whose generator has a check mode and a write mode."""

    name: str
    check_argv: list[str]
    write_argv: list[str]
    description: str
    runner: Runner = field(default=_run, repr=False)

    def stale(self) -> list[str]:
        result = self.runner(self.check_argv)
        return [] if result.returncode == 0 else [f"{_tail(result.stdout)} (exit {result.returncode})"]

    def write(self) -> int:
        result = self.runner(self.write_argv)
        sys.stdout.write(result.stdout)
        return result.returncode


def _py(*parts: str) -> list[str]:
    return [sys.executable, "-B", *parts]


def command_families(root: Path = REPO_ROOT, runner: Runner = _run) -> dict[str, CommandFamily]:
    families = {
        "g2_phase_d": CommandFamily(
            "g2_phase_d", _py("scripts/gen_g2_phase_d.py", "--check"), _py("scripts/gen_g2_phase_d.py"),
            "G2 runsheet regions generated from the window runbook", runner),
        "state": CommandFamily(
            "state", _py("scripts/gen_state.py", "--check"), _py("scripts/gen_state.py"),
            "RUN_STATE and TASK_QUEUE views generated from the state kernel", runner),
        "paper_custody_fixture": CommandFamily(
            "paper_custody_fixture", _py("tests/fixtures/paper_custody/repin.py", "--check"),
            _py("tests/fixtures/paper_custody/repin.py"),
            "fixture roles leave the committed supply map; the spec fixture matches its generator", runner),
    }
    for pack, extra in sorted(PACK_CHECK_ARGS.items()):
        generator = f"configs/campaigns/{pack}/generate_configs.py"
        if not (root / generator).is_file():
            continue
        families[f"pack:{pack}"] = CommandFamily(
            f"pack:{pack}", _py(generator, "--check", *extra), _py(generator, *extra),
            f"pack {pack}: config bytes, plan tree and order manifests", runner)
    return families


# --------------------------------------------------------------------------
# The pin registry


@dataclass(frozen=True)
class StaleRow:
    path: str
    pointer: str
    family: str
    target: str
    reason: str
    expected: str | None
    remedy: str


def _pointer_value(document: object, pointer: str) -> object:
    if pointer.endswith("#key"):
        pointer = pointer[:-4]
        parent, _, last = pointer.rpartition("/")
        container = _pointer_value(document, parent)
        key = last.replace("~1", "/").replace("~0", "~")
        if isinstance(container, dict) and key in container:
            return key
        raise KeyError(pointer)
    value = document
    for token in pointer.split("/")[1:]:
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            value = value[int(token)]
        elif isinstance(value, dict):
            value = value[token]
        else:
            raise KeyError(pointer)
    return value


class _Files:
    def __init__(self, root: Path) -> None:
        self.root = root
        self._text: dict[str, str | None] = {}
        self._json: dict[str, object] = {}

    def text(self, path: str) -> str | None:
        if path not in self._text:
            try:
                self._text[path] = (self.root / path).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                self._text[path] = None
        return self._text[path]

    def json(self, path: str) -> object:
        if path not in self._json:
            text = self.text(path)
            try:
                self._json[path] = None if text is None else json.loads(text)
            except ValueError:
                self._json[path] = None
        return self._json[path]


def _carries(files: _Files, path: str, pointer: str, digest: str) -> bool:
    text = files.text(path)
    if text is None:
        return False
    if path.endswith(".json") and not pointer.startswith("#"):
        document = files.json(path)
        if document is not None:
            try:
                value = _pointer_value(document, pointer)
            except (KeyError, IndexError, ValueError):
                value = None
            if isinstance(value, str):
                return digest in value
    return digest in text


def registry_stale(root: Path = REPO_ROOT, registry: dict | None = None) -> tuple[list[StaleRow], list[str]]:
    """Return (stale Kind-P rows, warnings). Warnings never fail the check."""

    registry = census.load_registry(root) if registry is None else registry
    targets = registry["targets"]
    files = _Files(root)
    digests: dict[str, str | None] = {}
    stale: list[StaleRow] = []
    warnings: list[str] = []
    for entry in registry["files"]:
        path = entry["path"]
        if files.text(path) is None:
            warnings.append(f"pinning file {path} is gone; refresh with python scripts/repin.py --write registry")
            continue
        for pointer, family, target_index in entry["rows"]:
            if family not in census.FAMILIES:
                warnings.append(f"{path} {pointer}: unknown family {family}")
                continue
            if not census.is_checked(path, family, target_index):
                continue
            key = targets[target_index]
            if key not in digests:
                method, _, target_path = key.partition(":")
                digests[key] = census.target_digest(root, census.Target(target_path, method))
            digest = digests[key]
            remedy = census.regenerator(family, path, root) or family
            if digest is None:
                stale.append(StaleRow(path, pointer, family, key, "pinned target is missing", None, remedy))
            elif not _carries(files, path, pointer, digest):
                stale.append(StaleRow(path, pointer, family, key,
                                      "no longer carries the target's current digest", digest, remedy))
    return stale, warnings


def _literal_at(files: _Files, row: StaleRow) -> str | None:
    """The single 64-hex literal a stale row holds now, or None if ambiguous."""

    if row.pointer.startswith("#L"):
        match = re.match(r"#L([0-9]+)", row.pointer)
        lines = (files.text(row.path) or "").splitlines()
        number = int(match.group(1)) if match else 0
        found = census.HEX64.findall(lines[number - 1]) if 0 < number <= len(lines) else []
    else:
        try:
            value = _pointer_value(files.json(row.path), row.pointer)
        except (KeyError, IndexError, ValueError, TypeError):
            return None
        found = census.HEX64.findall(value) if isinstance(value, str) else []
    return found[0] if len(found) == 1 else None


def write_registry_family(family: str, root: Path = REPO_ROOT) -> int:
    """Rewrite stale test-held copies of one registry family; refuse the rest."""

    stale, _warnings = registry_stale(root)
    rows = [row for row in stale if row.family == family]
    if not rows:
        print(f"pin {family}: nothing stale")
        return 0
    files = _Files(root)
    write = census.FAMILIES[family]["write"]
    refused = 0
    edits: dict[str, list[tuple[str, str, StaleRow]]] = {}
    for row in rows:
        pack = census.pack_dir(row.path)
        if row.expected is None:
            print(f"REFUSED {row.path} {row.pointer}: pinned target {row.target} is missing; restore it or "
                  "remove the pin, then python scripts/repin.py --write registry")
        elif pack and row.remedy.startswith("pack:"):
            print(f"REFUSED {row.path} {row.pointer}: a pack's pins are rewritten by its generator: "
                  f"python scripts/repin.py --write {row.remedy}")
        elif write == "none":
            print(f"REFUSED {row.path} {row.pointer}: recorded evidence {row.target} changed. Evidence bytes "
                  "are immutable and protect a number: restore them from custody")
        elif write == "review":
            print(f"REFUSED {row.path} {row.pointer}: frozen code {row.target} changed. This pin protects a "
                  "number: revert the edit, or re-freeze from the reviewed base (never from a head) and "
                  "re-issue what was issued against it")
        elif write != "rewrite_tests" or not row.path.startswith("tests/"):
            print(f"REFUSED {row.path} {row.pointer}: issued artifact pinning {row.target}. This pin protects "
                  "a number: re-issue the artifact with its issuer; repin.py never rewrites one")
        else:
            old = _literal_at(files, row)
            if old is None:
                print(f"REFUSED {row.path} {row.pointer}: the stale literal moved; refresh with "
                      "python scripts/repin.py --write registry, then retry")
            else:
                edits.setdefault(row.path, []).append((old, row.expected, row))
                continue
        refused += 1
    for path, changes in sorted(edits.items()):
        text = files.text(path) or ""
        for old, new, row in changes:
            text = text.replace(old, new)
            print(f"repinned {path} {row.pointer}: {old[:12]}... -> {new[:12]}... ({row.target})")
        (root / path).write_text(text, encoding="utf-8")
    if edits:
        print("These pins protect a number: commit them with the review the target change needs.")
    return 1 if refused else 0


# --------------------------------------------------------------------------
# CLI


def all_names(root: Path = REPO_ROOT) -> list[str]:
    return [*command_families(root), "registry"]


def check(names: list[str] | None = None, root: Path = REPO_ROOT, runner: Runner = _run,
          out=None) -> int:
    out = sys.stdout if out is None else out
    commands = command_families(root, runner)
    selected = names or all_names(root)
    failures = 0
    for name in selected:
        if name == "registry" or name in census.FAMILIES:
            stale, warnings = registry_stale(root)
            for warning in warnings:
                print(f"note: {warning}", file=out)
            for row in stale:
                if name != "registry" and row.family != name:
                    continue
                failures += 1
                print(f"pin {row.remedy} stale: {row.path} {row.pointer} ({row.family}) {row.reason} "
                      f"[{row.target}]: run python scripts/repin.py --write {row.remedy}", file=out)
            continue
        family = commands.get(name)
        if family is None:
            print(f"unknown pin family {name!r}; known: {', '.join(all_names(root))}", file=out)
            failures += 1
            continue
        for detail in family.stale():
            failures += 1
            print(f"pin {name} stale: {detail}: run python scripts/repin.py --write {name}", file=out)
    if failures == 0:
        print(f"PASS {len(selected)} pin families current", file=out)
    return 1 if failures else 0


def write(name: str, root: Path = REPO_ROOT, runner: Runner = _run) -> int:
    if name == "registry":
        return census.main(["--write", "--root", str(root)])
    if name in census.FAMILIES:
        return write_registry_family(name, root)
    family = command_families(root, runner).get(name)
    if family is None:
        print(f"unknown pin family {name!r}; known: {', '.join(all_names(root))}")
        return 2
    return family.write()


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    # Plan wording: ``check`` and ``repin <family>`` subcommands.
    if argv[:1] == ["check"]:
        argv = ["--check", *argv[1:]]
    elif argv[:1] == ["repin"]:
        argv = ["--write", *argv[1:]]
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", nargs="*", metavar="NAME", help="check all or the named families")
    mode.add_argument("--write", metavar="NAME", help="regenerate one family")
    mode.add_argument("--list", action="store_true", help="list family names")
    args = parser.parse_args(argv)
    if args.list:
        commands = command_families()
        for name in all_names():
            description = commands[name].description if name in commands else "Kind-P rows of configs/pins/registry.json"
            print(f"{name}: {description}")
        for name, spec in census.FAMILIES.items():
            print(f"{name} (registry family, {spec['kind']}, write={spec['write']}): {spec['description']}")
        return 0
    if args.write is not None:
        return write(args.write)
    return check(args.check or None)


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
