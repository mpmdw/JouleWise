"""A self-contained copy of the look's pinned files, for tests of the entry points' pin checks.

``mini_repo(test)`` copies every file lm-interim-01 pins (look code, dependencies, schemas, the step 3 file), the
manifest, LOOKS.json and the cited evidence into a temporary directory. A pinned file this branch does not carry
(the analyst seat's fit_interim.py and cadence_look_run.py live on PR #795) is written as a stub. It then re-pins
the copy with the real ``pin --write``, so the copy's manifest, LOOKS.json and files agree. The copy is a git
repository whose HEAD is also ``origin/main``, so the committed-ledger gate (``manifest.committed_ledger``) runs
against real git state. Entry points are run from the copy as files under ``-I``, so ``verify_pins`` checks the
copy's own bytes. Synthetic only.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from joulewise.cadence_looks import manifest as lm
from tests.cadence import custody_pin_fixture
from tests.git_fixture import init_git_fixture

REPO = Path(__file__).resolve().parents[2]
LOOKS_DIR = "docs/process/cadence/looks"
MANIFEST = f"{LOOKS_DIR}/lm-interim-01.json"
TWIN_PATH = "scripts/synthetic_pin.py"
TWIN_SOURCE = b"# Synthetic pin fixture. No independent fit or executable implementation.\n"
TWIN_PIN = {"path": TWIN_PATH, "sha256": hashlib.sha256(TWIN_SOURCE).hexdigest()}
STUB = "# stub: the pinned file lives on another branch (PR #795)\n"


def synthetic_reservation_name(parent):
    """Use the contract name where the local filesystem permits the generated test artifact."""
    import errno
    probe = Path(parent) / "RESTRICTED"
    try:
        probe.mkdir(mode=0o700)
    except PermissionError as exc:
        if exc.errno != errno.EPERM:
            raise
        return "synthetic-reservation"
    probe.rmdir()
    return probe.name


def to_draft(doc):
    """The manifest as a draft, whatever the checked-in status (Mythos round-4 N2: after the lead's freeze commit the
    checked-in manifest is committed; the draft-mode tests and the mini repo work on a draft of it)."""
    doc = json.loads(json.dumps(doc))
    doc["status"] = "draft"
    return doc


def _draft_ledger(ledger, doc_sha):
    for row in ledger["looks"]:
        if row["look_id"] == "lm-interim-01":
            for k in lm.LOOK_ROW_HASHES:
                row.pop(k, None)
            row.update(status="draft", sha256=doc_sha)
    return ledger


def fixture_sources(doc):
    return ({path for _, path, _ in lm.code_refs(doc)} | set(lm.EVIDENCE)
            | {MANIFEST, lm.LOOK_LEDGER_PATH, lm.Q11_EVIDENCE["path"]} | qualification_files())


def copy_missing_fixture_sources(root):
    for rel in fixture_sources(json.loads((REPO / MANIFEST).read_bytes())):
        target = root / rel
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / rel, target)


def mini_repo(test):
    root = Path(tempfile.mkdtemp(prefix="lm-mini-"))
    test.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
    doc = json.loads((REPO / MANIFEST).read_text(encoding="utf-8"))
    for rel in sorted(fixture_sources(doc)):
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if (REPO / rel).is_file():
            shutil.copyfile(REPO / rel, dst)
        else:
            dst.write_text(STUB, encoding="utf-8")
    draft = to_draft(doc)                         # the copy starts as a draft, whatever the checked-in status
    draft["fit"]["twin"] = None
    (root / MANIFEST).write_text(json.dumps(draft, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ledger = json.loads((root / lm.LOOK_LEDGER_PATH).read_text(encoding="utf-8"))
    (root / lm.LOOK_LEDGER_PATH).write_text(json.dumps(_draft_ledger(ledger, lm.sha256_file(root / MANIFEST)),
                                                       indent=2) + "\n", encoding="utf-8")
    run([sys.executable, "-B", str(root / "scripts/cadence_look_manifest.py"), "pin", str(root / MANIFEST),
         "--repo", str(root), "--write"], root, check=True)
    init_git_fixture(root, "-q", "-b", "main")          # the shared helper: no detached auto-maintenance
    git(root, "remote", "add", "origin", str(root / ".no-such-remote"))   # the shared ref's remote (never fetched)
    git_commit(root, "mini repo")
    return root


def git(root, *args):
    return run(["git", "-c", "user.name=look-test", "-c", "user.email=look-test@example.invalid", "-C", str(root),
                *args], root, check=True)


def git_commit(root, message, *, publish=True):
    """Commit every change; with ``publish``, move origin/main to HEAD (the shared history)."""
    git(root, "add", "-A")
    git(root, "commit", "-q", "--allow-empty", "-m", message)
    if publish:
        git(root, "update-ref", "refs/remotes/origin/main", "HEAD")


def run(argv, cwd, check=False, env=None):
    r = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, timeout=300, env=env)
    if check and r.returncode != 0:
        raise AssertionError(f"{argv[2:4]} exit {r.returncode}: {r.stdout[-800:]} {r.stderr[-800:]}")
    return r


def stage_span_dirs(argv):
    """{span id: directory} a stage-1 or stage-2 command line reads, from its roster or stage-1 file, ``--custody``
    and ``--span-dir``; None when the command reads no custody or its inputs cannot be read here."""
    argv = list(map(str, argv))
    if not argv or argv[0] not in ("stage1", "stage2") or "--custody" not in argv:
        return None
    try:
        source = json.loads(custody_pin_fixture.quiet_bytes(
            argv[argv.index("--roster" if argv[0] == "stage1" else "--stage1") + 1]))
        ids = [span["span_id"] for span in (source if argv[0] == "stage1" else source["roster"]["spans"])]
    except (OSError, ValueError, KeyError, TypeError, IndexError):
        return None
    custody = Path(argv[argv.index("--custody") + 1])
    dirs = {sid: custody / sid for sid in ids}
    for index, word in enumerate(argv[:-1]):
        if word == "--span-dir":
            sid, _, path = argv[index + 1].partition("=")
            if sid in dirs and path:
                dirs[sid] = Path(path)
    return dirs


def pin_custody(root, argv):
    """Stand in for the lead's ``pin-inputs`` and commit (RL-194): before a committed stage reads generated custody,
    make the copy's inputs file pin that custody as it is now, with a RUN_STATE whose Check items the pins chain to,
    and commit it on the shared history. Does nothing for a draft run, a manifest that is not committed, a copy with
    uncommitted or unpublished changes (a test of those states must reach its own refusal), or a pin list that already
    matches. A test of the pins themselves passes ``pin_custody=False`` to its launcher and edits custody afterwards."""
    argv = list(map(str, argv))
    dirs = stage_span_dirs(argv)
    if dirs is None or "--allow-draft" in argv or "--custody-pins" in argv or "--stage-archives" in argv:
        return False
    m = root / MANIFEST
    try:
        doc = json.loads(m.read_text(encoding="utf-8"))
        if doc.get("status") != "committed" or git(root, "status", "--porcelain").stdout.strip():
            return False
        if git(root, "rev-parse", "HEAD").stdout != git(root, "rev-parse", "refs/remotes/origin/main").stdout:
            return False
        pins = custody_pin_fixture.dump(custody_pin_fixture.synthetic_pins(dirs))
    except Exception:  # noqa: BLE001 - custody the fixture cannot pin is the stage's to refuse
        return False
    if (root / lm.INPUTS_PATH).read_bytes() == pins:
        return False
    doc["inputs"]["pins"]["sha256"] = write_pins(root, dirs)
    m.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    looks = json.loads((root / lm.LOOK_LEDGER_PATH).read_text(encoding="utf-8"))
    next(r for r in looks["looks"] if r["look_id"] == doc["look_id"])["sha256"] = lm.sha256_file(m)
    (root / lm.LOOK_LEDGER_PATH).write_text(json.dumps(looks, indent=2) + "\n", encoding="utf-8")
    git_commit(root, "pin the generated custody")
    return True


def py(root, rel, *args, tmpdir=None, pin=True):
    """Run a copied entry point as a file under -I, from outside the copy; ``tmpdir``: the child's private TMPDIR.
    A committed stage on generated custody first has that custody pinned in the copy (``pin_custody``)."""
    if pin and rel == "scripts/cadence_look_run.py":
        pin_custody(root, args)
    env = None if tmpdir is None else {**os.environ, "TMPDIR": str(tmpdir)}
    return run([sys.executable, "-I", "-B", str(root / rel), *map(str, args)], tmpdir or tempfile.gettempdir(), env=env)


def write_pins(root, span_dirs=None):
    """RL-194: fill the copy's inputs file with the pins of generated custody (``{span id: directory}``; without
    one, a placeholder list no roster names) and write a RUN_STATE whose Check items those pins chain to. Returns
    the inputs file's sha256, for the manifest's ``inputs.pins``."""
    pins = custody_pin_fixture.synthetic_pins(span_dirs) if span_dirs else custody_pin_fixture.placeholder_pins()
    for rel, data in ((lm.INPUTS_PATH, custody_pin_fixture.dump(pins)),
                      ("RUN_STATE.md", custody_pin_fixture.run_state(pins).encode("utf-8"))):
        target = root / rel
        target.unlink(missing_ok=True)       # never write through a hard link into the checkout (frozen_copy)
        target.write_bytes(data)
    return lm.sha256_file(root / lm.INPUTS_PATH)


def commit(root, *, stage1_sha256=None, roster_sha256=None, verdicts_sha256=None, publish=True, git_commit_it=True,
           span_dirs=None):
    """Mark the copy's manifest committed (status and LOOKS.json row) and commit it with git, as the lead's commit
    would. ``git_commit_it=False`` leaves the change in the working tree only (a loose ledger). A committed look
    pins its inputs (RL-194): ``span_dirs`` names the generated custody the copy's pin list is made from."""
    m = root / MANIFEST
    doc = json.loads(m.read_text(encoding="utf-8"))
    doc["status"] = "committed"
    if span_dirs or not json.loads((root / lm.INPUTS_PATH).read_bytes())["spans"]:     # keep a list already filled
        doc["inputs"]["pins"]["sha256"] = write_pins(root, span_dirs)
    (root / TWIN_PATH).write_bytes(TWIN_SOURCE)
    doc["fit"]["twin"] = TWIN_PIN
    drift = next(d for d in doc["decisions"] if d["id"] == "drift_tripwire")
    if drift.pop("pending", None) is not None:  # a committed manifest carries Q11's disposition (synthetic here)
        drift["disposed_by"] = "RL-999"               # synthetic disposing ruling
    m.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    looks = json.loads((root / lm.LOOK_LEDGER_PATH).read_text(encoding="utf-8"))
    row = next(r for r in looks["looks"] if r["look_id"] == doc["look_id"])
    row.update(sha256=lm.sha256_file(m), status="committed")
    if roster_sha256 or verdicts_sha256:          # the inputs stage 1 is given (Mythos round-3 N8)
        row.update(roster_sha256=roster_sha256 or "0" * 64, verdicts_sha256=verdicts_sha256 or "1" * 64)
    if stage1_sha256:
        row.update(status="stage1_committed", stage1_sha256=stage1_sha256, roster_sha256=roster_sha256 or "0" * 64,
                   verdicts_sha256=verdicts_sha256 or "1" * 64)
    (root / lm.LOOK_LEDGER_PATH).write_text(json.dumps(looks, indent=2) + "\n", encoding="utf-8")
    if git_commit_it:
        git_commit(root, "commit the look", publish=publish)


def _link_or_copy(src, dst):
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


FROZEN_COPY_ENV = "JW_LOOK_FROZEN_COPY"
FROZEN_TREES = ("joulewise", "scripts", "tests", ".github", "docs/process/cadence", "configs/align/v4")


def qualification_files():
    ledger = json.loads((REPO / lm.LOOK_LEDGER_PATH).read_bytes())
    manifests = {row["manifest_path"] for row in ledger["looks"] if row["status"] == "registered"}
    return manifests | {"joulewise/cadence_looks/qualification_manifest.py",
                        f"{LOOKS_DIR}/look_manifest.v2.schema.json", f"{LOOKS_DIR}/qualification-kit-commitments.json"}


def frozen_copy(test):
    """The repository's look-relevant trees (hard links where the filesystem allows) with the lead's freeze commit
    applied to the copy's manifest and LOOKS.json (status committed, Q11's note disposed, the row's hash) and its
    inputs file filled (RL-194), so the look's tests can be run on the frozen state (Mythos round-4 N2). The edited
    files are real copies, so the edit never reaches the checkout."""
    root = Path(tempfile.mkdtemp(prefix="lm-frozen-"))
    test.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
    for tree in FROZEN_TREES:
        shutil.copytree(REPO / tree, root / tree, copy_function=_link_or_copy,
                        ignore=shutil.ignore_patterns("__pycache__", "fixtures"))
    for rel in qualification_files():
        target = root / rel
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / rel, target)
    for rel in (MANIFEST, lm.LOOK_LEDGER_PATH, lm.INPUTS_PATH):          # every file the freeze commit rewrites
        (root / rel).unlink()
        shutil.copy2(REPO / rel, root / rel)
    commit(root, git_commit_it=False)
    return root
