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
import io
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
    """A synthetic draft with an empty custody registration, whatever is registered in the checked-in manifest."""
    doc = json.loads(json.dumps(doc))
    doc["status"] = "draft"
    doc["custody"]["root"] = None
    doc["inputs"]["pins"]["spans"] = []
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
    # its own realpath: no path the look reads may pass through a link (audit 3, rule P1), and a system temporary
    # directory may (macOS: /var -> /private/var)
    root = Path(os.path.realpath(tempfile.mkdtemp(prefix="lm-mini-")))
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
    draft["custody"]["root"] = str(registered_root(test, root))     # the copy's one registered root (audit 2)
    (root / MANIFEST).write_text(json.dumps(draft, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ledger = json.loads((root / lm.LOOK_LEDGER_PATH).read_text(encoding="utf-8"))
    (root / lm.LOOK_LEDGER_PATH).write_text(json.dumps(_draft_ledger(ledger, lm.sha256_file(root / MANIFEST)),
                                                       indent=2) + "\n", encoding="utf-8")
    run([sys.executable, "-B", str(root / "scripts/cadence_look_manifest.py"), "pin", str(root / MANIFEST),
         "--repo", str(root), "--write"], root, check=True)
    init_git_fixture(root, "-q", "-b", "main")          # the shared helper: no detached auto-maintenance
    # the shared history: a local bare origin, which a committed run fetches before reading any public record
    # (audit 3, rule P3); publishing a commit pushes it there
    git(root, "remote", "add", "origin", str(bare_origin(test, root)))
    git_commit(root, "mini repo")
    return root


def bare_origin(test, copy):
    """A bare repository beside ``copy`` to stand for its origin, removed with it."""
    made = Path(os.path.realpath(str(copy))).with_name(Path(copy).name + "-origin.git")
    made.mkdir()
    init_git_fixture(made, "-q", "--bare", "-b", "main")   # the shared helper: no detached auto-maintenance
    if test is not None:
        test.addCleanup(lambda: shutil.rmtree(made, ignore_errors=True))
    return made


def registered_root(test, copy):
    """The copy's registered look root: a canonical directory beside the copy, never inside it, removed with it."""
    made = Path(os.path.realpath(str(copy))).with_name(Path(copy).name + "-root")
    made.mkdir(exist_ok=True)
    (made / lm.INTERIM_LOOK_ID).mkdir(exist_ok=True)
    if test is not None:
        test.addCleanup(lambda: shutil.rmtree(made, ignore_errors=True))
    return made


def git(root, *args):
    return run(["git", "-c", "user.name=look-test", "-c", "user.email=look-test@example.invalid", "-C", str(root),
                *args], root, check=True)


def git_commit(root, message, *, publish=True):
    """Commit every change; with ``publish``, push it to origin's main and move origin/main to HEAD (the shared
    history). A copy whose origin is not a repository (an older fixture) only moves the ref."""
    git(root, "add", "-A")
    git(root, "commit", "-q", "--allow-empty", "-m", message)
    if publish:
        run(["git", "-C", str(root), "push", "-q", "--force", "origin", "HEAD:refs/heads/main"], root)
        git(root, "update-ref", "refs/remotes/origin/main", "HEAD")


def run(argv, cwd, check=False, env=None):
    r = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, timeout=300, env=env)
    if check and r.returncode != 0:
        raise AssertionError(f"{argv[2:4]} exit {r.returncode}: {r.stdout[-800:]} {r.stderr[-800:]}")
    return r


def place_in(root, argv, *, pin=True):
    """A former stage command line placed on the copy's fixed layout (``look_layout_fixture.place``). With ``pin``
    the copy's manifest then pins the generated custody as it is now, with a RUN_STATE the pins chain to, as the
    lead's pin-inputs and commit would: written in place for a draft; committed and published for a committed copy,
    unless the copy has uncommitted or unpublished changes (a test of those states must reach its own refusal) or
    the pins already match. A test of the pins themselves passes ``pin=False`` and edits custody afterwards."""
    from tests.cadence import look_layout_fixture
    placed = look_layout_fixture.place(argv, repo=root, minirepo=True)
    if not (pin and placed.placed):
        return placed
    m = root / MANIFEST
    doc = json.loads(m.read_text(encoding="utf-8"))
    if doc["inputs"]["pins"] == placed.manifest["inputs"]["pins"]:
        return placed
    committed = doc.get("status") == "committed"
    if committed:
        if git(root, "status", "--porcelain").stdout.strip():
            return placed
        if git(root, "rev-parse", "HEAD").stdout != git(root, "rev-parse", "refs/remotes/origin/main").stdout:
            return placed
    doc["inputs"]["pins"] = write_pins(root, pins=placed.manifest["inputs"]["pins"])
    m.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if committed:
        looks = json.loads((root / lm.LOOK_LEDGER_PATH).read_text(encoding="utf-8"))
        next(r for r in looks["looks"] if r["look_id"] == doc["look_id"])["sha256"] = lm.sha256_file(m)
        (root / lm.LOOK_LEDGER_PATH).write_text(json.dumps(looks, indent=2) + "\n", encoding="utf-8")
        git_commit(root, "pin the generated custody")
    return placed


def py(root, rel, *args, tmpdir=None, pin=True):
    """Run a copied entry point as a file under -I, from outside the copy; ``tmpdir``: the child's private TMPDIR.
    The executor takes no path (audit 2): a former stage command line is placed on the copy's fixed layout first
    and its outputs are copied back (``place_in``); with ``pin`` its generated custody is pinned in the copy's
    manifest first, as the lead's pin-inputs would."""
    env = None if tmpdir is None else {**os.environ, "TMPDIR": str(tmpdir)}
    if rel == "scripts/cadence_look_run.py":
        placed = place_in(root, args, pin=pin)
        if placed.ledger:                  # a draft copy reads its own LOOKS.json in place of a scratch ledger
            shutil.copyfile(placed.ledger, root / lm.LOOK_LEDGER_PATH)
        if placed.argv[0] == "stage1" and "--allow-draft" not in placed.argv:
            seed_rules34_receipt(root, placed.root / lm.INTERIM_LOOK_ID)
        result = run([sys.executable, "-I", "-B", str(root / rel), *placed.argv], tmpdir or tempfile.gettempdir(),
                     env=env)
        placed.collect()
        return result
    return run([sys.executable, "-I", "-B", str(root / rel), *map(str, args)], tmpdir or tempfile.gettempdir(), env=env)


def seed_rules34_receipt(repo, look):
    """Attest a generated verdict for tests that exercise later stage-1 checks with planted inputs."""
    path = look / lm.LOOK_FILES["rules_3_4"]
    if not path.is_file():
        return
    try:
        head, ref, ledger = lm.committed_ledger(repo, ledger_ref=lm.PUBLIC_RUN_STATE_REF)
    except lm.ManifestError:
        return  # the test must reach its own checkout or ledger refusal
    row = lm._look_row(ledger, lm.INTERIM_LOOK_ID)
    digest = lm.sha256_file(path)
    if row.get("verdicts_sha256") != digest:
        return
    gate = {"commit": head, "ref": ref, "ref_commit": lm.shared_ref(repo, ref)[1]}
    pins, _ = lm.input_pins(repo, lm.load_json(repo / MANIFEST), complete=True)
    receipt = lm.rules34_receipt(repo, gate, row, digest, pins)
    (look / lm.LOOK_FILES["rules_3_4_receipt"]).write_bytes(lm.release.dump(receipt))


def write_pins(root, span_dirs=None, pins=None):
    """RL-194: the copy's manifest pin list for generated custody (``{span id: directory}``; without one, a
    placeholder list no roster names), and a RUN_STATE whose Check items those pins chain to. Returns the pin list
    for the manifest's ``inputs.pins``; the caller writes the manifest."""
    if pins is None:
        pins = custody_pin_fixture.synthetic_pins(span_dirs) if span_dirs else custody_pin_fixture.placeholder_pins()
    target = root / "RUN_STATE.md"
    target.unlink(missing_ok=True)           # never write through a hard link into the checkout (frozen_copy)
    with io.FileIO(str(target), "w") as handle:          # below ``open``: a spying test does not see it
        handle.write(custody_pin_fixture.run_state(pins).encode("utf-8"))
    return pins


def commit(root, *, stage1_sha256=None, roster_sha256=None, verdicts_sha256=None, publish=True, git_commit_it=True,
           span_dirs=None):
    """Mark the copy's manifest committed (status and LOOKS.json row) and commit it with git, as the lead's commit
    would. ``git_commit_it=False`` leaves the change in the working tree only (a loose ledger). A committed look
    pins its inputs (RL-194): ``span_dirs`` names the generated custody the copy's pin list is made from."""
    m = root / MANIFEST
    doc = json.loads(m.read_text(encoding="utf-8"))
    doc["status"] = "committed"
    if span_dirs or not doc["inputs"]["pins"]["spans"]:     # keep a list already filled
        doc["inputs"]["pins"] = write_pins(root, span_dirs)
    if doc["custody"].get("root") is None:                  # a committed look registers its root (audit 2)
        doc["custody"]["root"] = str(registered_root(None, root))
    if doc["fit"]["twin"] is None:
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
    root = Path(os.path.realpath(tempfile.mkdtemp(prefix="lm-frozen-")))
    test.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
    for tree in FROZEN_TREES:
        shutil.copytree(REPO / tree, root / tree, copy_function=_link_or_copy,
                        ignore=shutil.ignore_patterns("__pycache__", "fixtures"))
    for rel in qualification_files():
        target = root / rel
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / rel, target)
    manifest = root / MANIFEST
    manifest.unlink()
    draft = to_draft(lm.load_json(REPO / MANIFEST))
    manifest.write_text(json.dumps(draft, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ledger = root / lm.LOOK_LEDGER_PATH
    ledger.unlink()
    shutil.copy2(REPO / lm.LOOK_LEDGER_PATH, ledger)
    commit(root, git_commit_it=False)
    registered = registered_root(test, root)
    doc = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    assert doc["custody"]["root"] == str(registered)
    return root
