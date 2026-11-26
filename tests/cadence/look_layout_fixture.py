"""The look's executor takes no path (audit 2, lead ruling): every file is a fixed name under the root the manifest
registers (``manifest.LookLayout``). Tests written against its former options keep their shape through this module,
which belongs to the tests and never to the executor: it places each file a former option named at its fixed name
under a registered root, writes the manifest that registers the root and carries the pin list, and afterwards copies
the outputs back to the names the test asked for.

Everything here is synthetic. A span is placed by hard links (a symlink in the source stays a symlink, so a test of
a linked file still meets the refusal it is about). The pin list of generated custody is made from its bytes as they
are when the command runs, unless the test names its own with ``--custody-pins``.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tarfile
import tempfile

from joulewise.cadence_looks import custody_pins, manifest as lm
from tests.cadence import custody_pin_fixture as fixture

LOOK = lm.INTERIM_LOOK_ID
# former options that named a path, and the fixed file each now is
VALUE_OPTIONS = {"--manifest", "--out", "--input", "--roster", "--custody", "--rules-3-4", "--span-dir",
                 "--write-input", "--stage-archives", "--staging-root", "--superseded-stage1", "--superseded-input",
                 "--custody-pins", "--run-state", "--stage1", "--energy", "--looks"}
# former options that named a record source: a committed run reads public records only from origin/main after a
# fetch (audit 3, rule P3), so the option is dropped
DROPPED_VALUE_OPTIONS = {"--ledger-ref"}
KEPT_VALUE_OPTIONS = {"--ruled-exclusion", "--stage1-sha256"}
INPUT_FILES = {"--roster": "roster", "--rules-3-4": "rules_3_4", "--stage1": "stage1", "--input": "input_level_r",
               "--energy": "input_level_e", "--superseded-stage1": "superseded_stage1",
               "--superseded-input": "superseded_level_r"}
OUTPUT_FILES = {"--out": "stage1", "--write-input": "level_r"}
_ROOTS = {}
_STAGE1_PINS = {}       # sha256 of a stage-1 file -> the pin list it was made under: its stage 2 runs under that list


def parse(argv):
    """(the command, {option: [values]}, [the arguments the executor still takes])."""
    argv = [os.fspath(word) if isinstance(word, os.PathLike) else str(word) for word in argv]
    if not argv:
        return None, {}, []
    values, kept, index = {}, [argv[0]], 1
    while index < len(argv):
        word = argv[index]
        if word in VALUE_OPTIONS and index + 1 < len(argv):
            values.setdefault(word, []).append(argv[index + 1])
            index += 2
        elif word in DROPPED_VALUE_OPTIONS and index + 1 < len(argv):
            index += 2
        elif word in KEPT_VALUE_OPTIONS and index + 1 < len(argv):
            kept += [word, argv[index + 1]]
            index += 2
        else:
            kept.append(word)
            index += 1
    return argv[0], values, kept


def _quiet(path):
    return fixture.quiet_bytes(path)


def _write(path, data):
    """Write below ``open``: a test that spies on the executor's opens does not see the placement."""
    with io.FileIO(str(path), "w") as handle:
        handle.write(data)


def registered_root(key):
    """A canonical directory outside every repository, one per key for the life of the test process."""
    if key not in _ROOTS:
        made = Path(os.path.realpath(tempfile.mkdtemp(prefix="jw-look-root-")))
        _ROOTS[key] = made
    return _ROOTS[key]


def _remove(path):
    if os.path.islink(path) or os.path.isfile(path):
        os.unlink(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)


def _link_tree(source, target):
    """``source`` at ``target`` by hard links (copies across devices); a symlink stays a symlink."""
    if os.path.islink(source):
        os.symlink(os.readlink(source), target, target_is_directory=os.path.isdir(source))
        return

    def link(src, dst):
        try:
            os.link(src, dst, follow_symlinks=False)
        except OSError:
            shutil.copy2(src, dst, follow_symlinks=False)
    shutil.copytree(source, target, symlinks=True, copy_function=link)


def _span_ids(command, values):
    """The span ids a stage reads: its roster's, or its stage-1 file's roster's."""
    try:
        if command == "stage1" and "--roster" in values:
            return [row["span_id"] for row in json.loads(_quiet(values["--roster"][-1]))]
        if command == "stage2" and "--stage1" in values:
            return [row["span_id"] for row in json.loads(_quiet(values["--stage1"][-1]))["roster"]["spans"]]
    except (OSError, ValueError, KeyError, TypeError):
        return []
    return []


def _staged_pins(plan_path):
    """{span id: pins} of the spans a staging plan names, from each archive's SHA256SUMS and member sizes."""
    staged = {}
    for entry in json.loads(_quiet(plan_path)):
        with tarfile.open(fileobj=io.BytesIO(_quiet(entry["archive"]))) as tar:
            sizes = {m.name.split("/", 1)[1]: m.size for m in tar if m.isfile()}
        staged[entry["span_id"]] = custody_pins.span_pins(entry["span_id"], _quiet(entry["manifest"]), sizes,
                                                          runner_commit="0" * 40, close_item=2, check_item=1)
    return staged


class Placed:
    """A legacy command line placed on the fixed layout."""

    def __init__(self, argv, root=None, manifest=None, run_state=None, ledger=None, exports=None, placed=False):
        self.argv, self.root, self.manifest, self.run_state = argv, root, manifest, run_state
        self.ledger, self.exports, self.placed = ledger, exports or {}, placed

    def collect(self):
        """Copy each output the test asked for back to its name; returns the names copied. A stage-1 file made here
        is remembered with the pin list it was made under."""
        made = self.root / LOOK / lm.LOOK_FILES["stage1"] if self.root is not None else None
        if made is not None and self.argv and self.argv[0] == "stage1" and made.is_file():
            _STAGE1_PINS[hashlib.sha256(_quiet(made)).hexdigest()] = self.manifest["inputs"]["pins"]
        copied = []
        for key, target in self.exports.items():
            source = self.root / LOOK / lm.LOOK_FILES[key]
            if source.is_file():
                Path(target).parent.mkdir(parents=True, exist_ok=True)
                _write(target, _quiet(source))
                copied.append(target)
        return copied


def place(argv, *, repo, minirepo=False):
    """Place a former command line on the fixed layout. ``minirepo``: the manifest is the copy's own, at its fixed
    path, with its root registered already (``look_minirepo``); otherwise a manifest is written for this run (the
    test's ``--manifest``) and the test harness names it to the executor in place of the repository's."""
    command, values, kept = parse(argv)
    if command not in ("stage1", "stage2"):         # another tool's command line (row, host-id): as it is
        return Placed([os.fspath(word) if isinstance(word, os.PathLike) else str(word) for word in argv])
    repo = Path(repo)
    manifest_path = repo / lm.INTERIM_MANIFEST_PATH
    if minirepo:
        base = json.loads(manifest_path.read_text(encoding="utf-8"))
        root = Path(base["custody"]["root"])
    else:
        base = json.loads(_quiet(values["--manifest"][-1])) if "--manifest" in values else \
            json.loads(manifest_path.read_text(encoding="utf-8"))
        key = (hashlib.sha256(json.dumps(base, sort_keys=True).encode()).hexdigest(),
               os.path.realpath(values["--custody"][-1]) if "--custody" in values else None)
        root = registered_root(key)
    look = root / LOOK
    look.mkdir(parents=True, exist_ok=True)
    for name in (*lm.LOOK_FILES.values(), lm.ARCHIVES_DIR):
        _remove(look / name)

    # each span at <root>/<span id>
    ids = _span_ids(command, values)
    custody = Path(values["--custody"][-1]) if "--custody" in values else None
    overrides = dict(pair.partition("=")[::2] for pair in values.get("--span-dir", []))
    staged = _staged_pins(values["--stage-archives"][-1]) if "--stage-archives" in values else {}
    dirs = {}
    for sid in ids:
        source = Path(overrides[sid]) if sid in overrides else (custody / sid if custody else None)
        target = root / sid
        if source is not None and os.path.lexists(source) and os.path.realpath(os.path.dirname(source)) == \
                os.path.realpath(root) and Path(source).name == sid:
            dirs[sid] = target                  # the custody already is the registered root: nothing to place
            continue
        if os.path.lexists(target):
            _remove(target)
        if sid in staged or source is None or not os.path.lexists(source):
            continue
        _link_tree(source, target)
        dirs[sid] = target

    # each input at its fixed name
    for option, key in INPUT_FILES.items():
        if option in values and os.path.isfile(values[option][-1]):     # an absent input stays absent
            _write(look / lm.LOOK_FILES[key], _quiet(values[option][-1]))
    if "--stage-archives" in values:
        archives = look / lm.ARCHIVES_DIR
        archives.mkdir()
        for entry in json.loads(_quiet(values["--stage-archives"][-1])):
            for kind, suffix in lm.ARCHIVE_SUFFIXES.items():
                _write(archives / f"{entry['span_id']}{suffix}", _quiet(entry[kind]))
        kept.append("--stage-archives")
    if "--input" in values:
        kept.append("--level-r")
    if "--energy" in values:
        kept.append("--level-e")

    # the pin list the manifest carries: the test's own; for stage 2, the list its stage 1 ran under (a committed
    # look's pins are fixed before stage 1, so a copy changed afterwards meets them); else one made from the custody
    # as it is now
    pins = base["inputs"]["pins"]
    stage1_key = (hashlib.sha256(_quiet(values["--stage1"][-1])).hexdigest()
                  if command == "stage2" and "--stage1" in values and os.path.isfile(values["--stage1"][-1]) else None)
    if "--custody-pins" in values:
        pins = json.loads(_quiet(values["--custody-pins"][-1]))
    elif stage1_key in _STAGE1_PINS:
        pins = _STAGE1_PINS[stage1_key]
    elif dirs or staged:
        try:
            made = fixture.synthetic_pins({sid: path for sid, path in dirs.items() if path.is_dir()})
            made["spans"] += list(staged.values())
            made["spans"].sort(key=lambda span: span["span_id"])
            for index, span in enumerate(made["spans"]):          # one Check item per span
                span.update(check_item=2 * index + 1, close_item=2 * index + 2)
            pins = made
        except Exception:  # noqa: BLE001 - custody the fixture cannot pin is the stage's to refuse
            pass
    pins = json.loads(json.dumps(pins, sort_keys=True))     # one key order, whatever the source: equal lists, equal bytes
    doc = json.loads(json.dumps(base))
    doc["custody"]["root"] = str(root)
    doc["inputs"]["pins"] = pins
    run_state = (_quiet(values["--run-state"][-1]).decode("utf-8") if "--run-state" in values
                 else fixture.run_state(pins))
    ledger = values["--looks"][-1] if "--looks" in values else None
    exports = {key: values[option][-1] for option, key in OUTPUT_FILES.items() if option in values}
    return Placed(kept, root=root, manifest=doc, run_state=run_state, ledger=ledger, exports=exports, placed=True)


def span_dirs(custody, pairs=None):
    """{span id -> directory} for a test that calls a reader in-process: each span under ``custody``, or where a
    ``SPAN_ID=PATH`` pair puts it. The executor itself has no such option; it reads ``<root>/<span id>`` only."""
    found = {}
    for pair in pairs or []:
        sid, _, path = str(pair).partition("=")
        found[sid] = Path(path)
    return lambda sid: found.get(sid, Path(custody) / sid)
