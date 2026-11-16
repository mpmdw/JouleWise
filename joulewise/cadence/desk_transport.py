"""Signed transport between the MBP queue controller and the Air desk (``docs/process/cadence_desk_format.md``).

* **Bundle, MBP to Air.** The controller commits one parentless commit, SSH-signed by the principal
  ``cadence-controller``, with the subject ``cadence close bundle <plan_id>``, to
  ``refs/heads/desk-bundles/<plan_id>``. Its tree is exactly ``transition.json`` (the controller's per-span
  transition record, RL-172 (g) 8, which carries the manifest's sha256 and the queue commit armed from) and
  ``bundle/<the closed layout of desk_final>``. ``extract_bundle`` verifies the signature against an
  allowed-signers file, refuses any tree entry outside that shape without reading it, writes ``bundle/`` out
  and checks the manifest against the transition record. Nothing else on the Air authenticates a bundle
  (Mythos F1).
* **Verdict, Air to MBP.** ``publish_verdict`` commits ``desk_verdict.json`` and ``desk_summary.json``,
  SSH-signed by the principal ``cadence-desk``, with the message ``cadence desk verdict <plan_id>`` and the
  trailers ``Verdict-SHA256`` and ``Desk-Final``, to ``refs/heads/cadence-desk-final/<plan_id>``. A later
  judgment of the same span (a hand table supplied) is a child commit on the same ref, so the ref only moves
  forward. ``read_verdict`` is the controller's reader: signature, trailers, ``verify_verdict``, plan id.
* **History.** ``history_from_records`` rebuilds the campaign's earlier desk summaries from those signed
  records, so ``--history`` need not be typed (Mythos F1).

Every git call is local except the ``fetch``/``push``/``ls-remote`` in ``publish_verdict``. No energy, power,
meter-sample or transcript file is in any tree this module reads or writes; blobs are read only at paths the
layout allows.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from joulewise.cadence import desk_final

BUNDLE_REF_PREFIX = "refs/heads/desk-bundles/"
VERDICT_REF_PREFIX = "refs/heads/cadence-desk-final/"
CONTROLLER_PRINCIPAL = "cadence-controller"
DESK_PRINCIPAL = "cadence-desk"
BUNDLE_SUBJECT = "cadence close bundle {plan_id}"
VERDICT_SUBJECT = "cadence desk verdict {plan_id}"
_GOOD = re.compile(r'^Good "git" signature for (\S+) with ', re.M)
_TRAILER = re.compile(r"^([A-Za-z0-9-]+): (\S+)$", re.M)
FIXED_DATE = "2000000000 +0000"
TRANSITION_NAME = "transition.json"
TRANSITION_SCHEMA = "joulewise.cadence_controller_transition.v1"
TRANSITION_KEYS = {"schema", "plan_id", "queue_id", "span_id", "attempt", "queue", "kit", "plan_sha256",
                   "arm_proof_sha256", "arm_command_sha256", "close_proof_sha256", "status", "manifest_sha256",
                   "t0_epoch", "receipt_epoch"}     # required; other keys are allowed if they pass the deny scan


class TransportRefusal(RuntimeError):
    pass


def _git(repo, *args, input_bytes=None, config=(), env=None, timeout=120):
    argv = ["git", "-C", str(repo)]
    for item in config:
        argv += ["-c", item]
    full_env = {**os.environ, "LC_ALL": "C", "GIT_TERMINAL_PROMPT": "0", **(env or {})}
    return subprocess.run([*argv, *args], input=input_bytes, capture_output=True, timeout=timeout, env=full_env)


def _out(res):
    return res.stdout.decode("utf-8", "replace").strip()


def verify_signed_commit(repo, commit, *, allowed_signers, principal):
    """True when ``commit`` carries a good SSH signature by ``principal`` in ``allowed_signers``."""
    if not Path(allowed_signers).is_file():
        raise TransportRefusal(f"no allowed-signers file at {allowed_signers}")
    res = _git(repo, "verify-commit", "--raw", commit,
               config=("gpg.format=ssh", f"gpg.ssh.allowedSignersFile={allowed_signers}"))
    text = res.stderr.decode("utf-8", "replace") + res.stdout.decode("utf-8", "replace")
    m = _GOOD.search(text)
    if res.returncode != 0 or not m:
        raise TransportRefusal(f"{commit[:12]}: no good SSH signature ({text.strip()[:160]})")
    if m.group(1) != principal:
        raise TransportRefusal(f"{commit[:12]}: signed by {m.group(1)}, not {principal}")
    return True


def _commit_message(repo, commit):
    raw = _git(repo, "cat-file", "commit", commit).stdout.decode("utf-8", "replace")
    head, _, body = raw.partition("\n\n")
    parents = [line.split()[1] for line in head.splitlines() if line.startswith("parent ")]
    return body, parents


def _trailers(body):
    return {k: v for k, v in _TRAILER.findall(body)}


def resolve(repo, ref):
    res = _git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    sha = _out(res)
    if res.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40,64}", sha):
        raise TransportRefusal(f"{ref}: no such commit")
    return sha


def validate_transition(doc):
    """The transition record's shape (FORMAT section 1). Returns problems."""
    from joulewise.cadence import desk
    if not isinstance(doc, dict):
        return ["transition.json: not an object"]
    problems = []
    missing = sorted(TRANSITION_KEYS - set(doc))
    if missing:
        problems.append(f"transition.json: missing {missing}")
    if doc.get("schema") != TRANSITION_SCHEMA:
        problems.append(f"transition.json schema {doc.get('schema')!r}")
    q, k = doc.get("queue"), doc.get("kit")
    if not (isinstance(q, dict) and isinstance(q.get("path"), str) and isinstance(q.get("sha256"), str)
            and desk_final.HEX64.fullmatch(q["sha256"]) and isinstance(q.get("commit"), str)
            and re.fullmatch(r"[0-9a-f]{40,64}", q["commit"])):
        problems.append("transition.json queue: {path, sha256, commit}")
    if not (isinstance(k, dict) and isinstance(k.get("sha256"), str) and desk_final.HEX64.fullmatch(k["sha256"])):
        problems.append("transition.json kit: {path, sha256}")
    if not (isinstance(doc.get("manifest_sha256"), str) and desk_final.HEX64.fullmatch(doc["manifest_sha256"])):
        problems.append("transition.json manifest_sha256")
    return problems


def extract_bundle(repo, ref, dest, *, allowed_signers, plan_id, principal=CONTROLLER_PRINCIPAL):
    """Verify the signed bundle commit at ``ref`` and write its ``bundle/`` tree to ``dest`` (created; must not
    exist). Returns the transport record {signed, bundle_commit, signer, manifest_sha256, transition}. Raises
    TransportRefusal; a tree entry outside the shape is refused before any blob is read."""
    sha = resolve(repo, ref)
    verify_signed_commit(repo, sha, allowed_signers=allowed_signers, principal=principal)
    body, parents = _commit_message(repo, sha)
    if parents:
        raise TransportRefusal(f"{sha[:12]}: a bundle commit has no parent")
    if body.splitlines()[:1] != [BUNDLE_SUBJECT.format(plan_id=plan_id)]:
        raise TransportRefusal(f"{sha[:12]}: subject is not {BUNDLE_SUBJECT.format(plan_id=plan_id)!r}")
    listing = _git(repo, "ls-tree", "-r", "-z", "--full-tree", sha)
    if listing.returncode != 0:
        raise TransportRefusal(f"{sha[:12]}: ls-tree failed")
    entries = []
    for item in listing.stdout.decode("utf-8", "replace").split("\0"):
        if not item:
            continue
        meta, _, path = item.partition("\t")
        mode, kind, obj = meta.split()
        entries.append((mode, kind, obj, path))

    def allowed(p):
        if p == TRANSITION_NAME:
            return True
        rel = p[len("bundle/"):] if p.startswith("bundle/") else None
        return rel is not None and (rel == desk_final.MANIFEST_NAME or bool(desk_final.BUNDLE_PATH_RE.fullmatch(rel)))
    bad = [p for mode, kind, _, p in entries if mode != "100644" or kind != "blob" or not allowed(p)]
    if bad:
        raise TransportRefusal(f"{sha[:12]}: tree entries outside the bundle layout (not read): {bad[:5]}")
    if TRANSITION_NAME not in [p for *_, p in entries]:
        raise TransportRefusal(f"{sha[:12]}: no {TRANSITION_NAME}")
    blobs = {}
    for _, _, obj, path in entries:
        blob = _git(repo, "cat-file", "blob", obj)
        if blob.returncode != 0:
            raise TransportRefusal(f"{path}: blob unreadable")
        blobs[path] = blob.stdout
    desk_final.refuse_denied_content(blobs)     # Mythos N1, Sol R1: DeniedContent, before anything is trusted
    try:
        transition = json.loads(blobs[TRANSITION_NAME])
    except ValueError:
        raise TransportRefusal(f"{sha[:12]}: {TRANSITION_NAME} is not JSON") from None
    problems = validate_transition(transition)
    if problems:
        raise TransportRefusal(f"{sha[:12]}: " + "; ".join(problems))
    if transition["plan_id"] != plan_id:
        raise TransportRefusal(f"{sha[:12]}: the transition record is for {transition['plan_id']!r}")
    manifest = blobs.get(f"bundle/{desk_final.MANIFEST_NAME}")
    if manifest is None or desk_final.sha256_bytes(manifest) != transition["manifest_sha256"]:
        raise TransportRefusal(f"{sha[:12]}: the manifest does not hash to the transition record's manifest_sha256")
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=False)
    for path, raw in blobs.items():
        if path == TRANSITION_NAME:
            continue
        target = dest / path[len("bundle/"):]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    return {"signed": True, "bundle_commit": sha, "signer": principal,
            "manifest_sha256": transition["manifest_sha256"], "transition": transition}


def queue_from_transition(repo, transition, dest):
    """The queue file the span armed from: ``git show <queue.commit>:<queue.path>``, checked against its
    sha256 in the signed transition record, written to ``dest``."""
    q = transition["queue"]
    res = _git(repo, "show", f"{q['commit']}:{q['path']}")
    if res.returncode != 0:
        raise TransportRefusal(f"queue {q['path']} at {q['commit'][:12]} is not in this clone (fetch the audit branch)")
    if desk_final.sha256_bytes(res.stdout) != q["sha256"]:
        raise TransportRefusal(f"queue {q['path']} at {q['commit'][:12]} does not hash as the transition record says")
    Path(dest).write_bytes(res.stdout)
    return Path(dest)


def tree_of(repo, files):
    """A tree object of ``files`` ({path: bytes}), built in a throwaway index. Returns its sha."""
    index = Path(tempfile.mkdtemp(prefix=".cadence-index-")) / "index"
    env = {"GIT_INDEX_FILE": str(index)}
    try:
        for name, raw in sorted(files.items()):
            blob = _git(repo, "hash-object", "-w", "--stdin", input_bytes=raw)
            if blob.returncode != 0:
                raise TransportRefusal(f"hash-object {name}: {blob.stderr.decode()[:160]}")
            add = _git(repo, "update-index", "--add", "--cacheinfo", f"100644,{_out(blob)},{name}", env=env)
            if add.returncode != 0:
                raise TransportRefusal(f"update-index {name}: {add.stderr.decode()[:160]}")
        tree = _git(repo, "write-tree", env=env)
        if tree.returncode != 0:
            raise TransportRefusal(f"write-tree: {tree.stderr.decode()[:160]}")
        return _out(tree)
    finally:
        shutil.rmtree(index.parent, ignore_errors=True)


def _signed_commit(repo, files, *, message, signing_key, principal, parents=()):
    """One signed commit of ``files`` ({path: bytes}); returns its sha. Local objects only."""
    tree = tree_of(repo, files)
    args = ["commit-tree", "-S", tree]
    for p in parents:
        args += ["-p", p]
    who = {"GIT_AUTHOR_NAME": principal, "GIT_AUTHOR_EMAIL": f"{principal}@localhost", "GIT_AUTHOR_DATE": FIXED_DATE,
           "GIT_COMMITTER_NAME": principal, "GIT_COMMITTER_EMAIL": f"{principal}@localhost",
           "GIT_COMMITTER_DATE": FIXED_DATE}
    res = _git(repo, *args, input_bytes=(message + "\n").encode(), env=who,
               config=("gpg.format=ssh", f"user.signingkey={signing_key}"))
    if res.returncode != 0:
        raise TransportRefusal(f"commit-tree -S: {res.stderr.decode()[:200]}")
    return _out(res)


def sign_bundle(repo, bundle_dir, transition, *, plan_id, signing_key, principal=CONTROLLER_PRINCIPAL):
    """The controller's side, for reference and for synthetic runs: commit a packed bundle directory and the
    transition record as the signed parentless bundle commit. ``transition['manifest_sha256']`` is set from
    the bundle. Returns (commit sha, manifest sha256). Opens only layout paths."""
    bundle_dir = Path(bundle_dir)
    files = {}
    for path in sorted(bundle_dir.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(bundle_dir).as_posix()
        if path.is_symlink() or not (rel == desk_final.MANIFEST_NAME or desk_final.BUNDLE_PATH_RE.fullmatch(rel)):
            raise TransportRefusal(f"{rel}: not in the bundle layout (not read)")
        files[f"bundle/{rel}"] = path.read_bytes()
    anchor = desk_final.sha256_bytes(files[f"bundle/{desk_final.MANIFEST_NAME}"])
    transition = {**transition, "manifest_sha256": anchor}
    problems = validate_transition(transition)
    if problems:
        raise TransportRefusal("; ".join(problems))
    files[TRANSITION_NAME] = (json.dumps(transition, indent=1, sort_keys=True) + "\n").encode()
    desk_final.refuse_denied_content(files)     # the same deny scan the Air runs, before anything is signed
    return _signed_commit(repo, files, message=BUNDLE_SUBJECT.format(plan_id=plan_id), signing_key=signing_key,
                          principal=principal), anchor


def publish_verdict(repo, out_dir, *, plan_id, signing_key, remote="origin", ref_prefix=VERDICT_REF_PREFIX,
                    principal=DESK_PRINCIPAL, push=True):
    """Commit ``desk_verdict.json`` (and ``desk_summary.json`` when present) from ``out_dir`` as a signed
    commit on ``<ref_prefix><plan_id>``, a child of the ref's current tip, and push it. Returns the commit."""
    out_dir = Path(out_dir)
    raw = (out_dir / desk_final.VERDICT_NAME).read_bytes()
    doc = json.loads(raw)
    if not desk_final.verify_verdict(doc) or doc.get("plan_id") != plan_id:
        raise TransportRefusal("the verdict does not verify or names another plan id")
    files = {desk_final.VERDICT_NAME: raw}
    summary_path = out_dir / desk_final.SUMMARY_NAME
    if doc.get("summary_sha256") is not None or summary_path.exists():
        try:
            summary_raw = summary_path.read_bytes()
            summary = json.loads(summary_raw)
        except (OSError, ValueError) as error:
            raise TransportRefusal("the declared summary is missing or unreadable") from error
        if desk_final.canonical_sha256(summary) != doc.get("summary_sha256"):
            raise TransportRefusal("the summary is not the verdict's")
        files[desk_final.SUMMARY_NAME] = summary_raw
    ref = f"{ref_prefix}{plan_id}"
    parents = []
    if push:
        remote_tip = _git(repo, "ls-remote", remote, ref, timeout=120)
        if remote_tip.returncode != 0:
            raise TransportRefusal(f"ls-remote {remote} {ref}: {remote_tip.stderr.decode()[:160]}")
        if _out(remote_tip):
            tip = _out(remote_tip).split()[0]
            if _git(repo, "fetch", "--quiet", remote, tip, timeout=120).returncode != 0:
                raise TransportRefusal(f"fetch {tip[:12]} failed")
            parents = [tip]
    elif _git(repo, "rev-parse", "--verify", "--quiet", ref).returncode == 0:
        parents = [_out(_git(repo, "rev-parse", ref))]
    message = (f"{VERDICT_SUBJECT.format(plan_id=plan_id)}\n\nVerdict-SHA256: {doc['verdict_sha256']}\n"
               f"Desk-Final: {str(doc['desk_final']).lower()}")
    sha = _signed_commit(repo, files, message=message, signing_key=signing_key, principal=principal, parents=parents)
    if push:
        res = _git(repo, "push", "--quiet", remote, f"{sha}:{ref}", timeout=300)
        if res.returncode != 0:
            raise TransportRefusal(f"push {ref}: {res.stderr.decode()[:200]}")
    else:
        _git(repo, "update-ref", ref, sha)
    return sha


def read_verdict(repo, ref, *, allowed_signers, plan_id, principal=DESK_PRINCIPAL):
    """The controller's reader: the verdict at the tip of ``ref``, verified (signature by ``principal``,
    subject, Verdict-SHA256 trailer, ``verify_verdict``, plan id, and the summary's hash). Returns
    (verdict, summary or None). Raises TransportRefusal; a missing ref is the caller's 'not final'."""
    sha = resolve(repo, ref)
    verify_signed_commit(repo, sha, allowed_signers=allowed_signers, principal=principal)
    body, _ = _commit_message(repo, sha)
    if body.splitlines()[:1] != [VERDICT_SUBJECT.format(plan_id=plan_id)]:
        raise TransportRefusal(f"{sha[:12]}: subject is not {VERDICT_SUBJECT.format(plan_id=plan_id)!r}")
    show = _git(repo, "show", f"{sha}:{desk_final.VERDICT_NAME}")
    if show.returncode != 0:
        raise TransportRefusal(f"{sha[:12]}: no {desk_final.VERDICT_NAME}")
    doc = json.loads(show.stdout)
    trailers = _trailers(body)
    if (not desk_final.verify_verdict(doc) or doc.get("plan_id") != plan_id
            or trailers.get("Verdict-SHA256") != doc.get("verdict_sha256")
            or trailers.get("Desk-Final") != str(doc.get("desk_final")).lower()):
        raise TransportRefusal(f"{sha[:12]}: the verdict does not verify against its commit")
    summary = None
    s = _git(repo, "show", f"{sha}:{desk_final.SUMMARY_NAME}")
    if s.returncode != 0 and doc.get("summary_sha256") is not None:
        raise TransportRefusal(f"{sha[:12]}: declared {desk_final.SUMMARY_NAME} missing or unreadable")
    if s.returncode == 0:
        summary = json.loads(s.stdout)
        if desk_final.canonical_sha256(summary) != doc.get("summary_sha256"):
            raise TransportRefusal(f"{sha[:12]}: the summary is not the verdict's")
    return doc, summary


def history_from_records(repo, ref_prefix, *, allowed_signers, campaign_id, exclude_plan_id=None,
                         principal=DESK_PRINCIPAL):
    """The campaign's earlier desk summaries, from signed verdict records, in machine order (the first leg's
    start). A record that does not verify is a refusal, never skipped."""
    refs = _git(repo, "for-each-ref", "--format=%(refname)", ref_prefix.rstrip("/") + "/")
    out = []
    for ref in _out(refs).splitlines():
        plan_id = ref[len(ref_prefix.rstrip("/")) + 1:]
        if not plan_id or plan_id == exclude_plan_id:
            continue
        doc, summary = read_verdict(repo, ref, allowed_signers=allowed_signers, plan_id=plan_id, principal=principal)
        if summary is not None and summary.get("campaign_id") == campaign_id:
            out.append(summary)
    return sorted(out, key=lambda s: (s.get("first_leg_start_epoch_s") or 0, s.get("plan_id") or ""))


def extract_to_temp(repo, ref, parent, *, allowed_signers, plan_id, principal=CONTROLLER_PRINCIPAL):
    """``extract_bundle`` into a fresh directory under ``parent``. Returns (dir, transport record)."""
    Path(parent).mkdir(parents=True, exist_ok=True)
    base = Path(tempfile.mkdtemp(prefix=".bundle-", dir=parent))
    try:
        record = extract_bundle(repo, ref, base / "bundle", allowed_signers=allowed_signers, plan_id=plan_id,
                                principal=principal)
    except Exception:
        shutil.rmtree(base, ignore_errors=True)
        raise
    return base, record
