#!/usr/bin/env python3
"""Offline source/Git census. Never fetch, tag, delete, or follow source paths.

Main is scanned in full; each HOLD tip is scanned as a delta against main.
Unchanged blobs inherit main's scan. Symlinks/submodules and sealed paths are
excluded before any blob read. Output is a review snapshot, not authorization.
"""
import argparse
from bisect import bisect_left
import csv
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

HEX = re.compile(r"(?<![0-9a-fA-F])[0-9a-f]{7,40}(?![0-9a-fA-F])")
DIGEST = re.compile(r"(?<![0-9a-fA-F])[0-9a-f]{64}(?![0-9a-fA-F])")
SEALED = {"restricted", "night-custody", "night-archive"}


def git(repo, *args, data=None):
    return subprocess.run(["git", "-c", "gc.auto=0", "-C", str(repo), *args],
                          input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          check=True).stdout


def rows(path):
    with Path(path).open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def write_tsv(path, fields, records):
    with Path(path).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def allowed(path):
    if set(PurePosixPath(path).parts) & SEALED:
        return False
    # Source/config/registration census, never a raw-capture reader. Old lanes
    # contain fixture traces too; their code/config references are scanned,
    # their data payloads are unnecessary for a commit-citation check.
    if path.startswith("tests/fixtures/"):
        if "custody_store" in PurePosixPath(path).parts or "raw" in PurePosixPath(path).parts:
            return False
        if not path.endswith((".py", ".sh", ".js", ".mjs", ".md", ".rst")):
            return False
    return True


def commit_literals(text):
    for match in HEX.finditer(text):
        value = match.group()
        if value.isdecimal():
            before = text[max(0, match.start() - 40):match.start()]
            after = text[match.end():match.end() + 1]
            quoted = before.endswith(("`", "'", '"')) and after.startswith(("`", "'", '"'))
            named = re.search(r"(?:commit|sha|head|revision|pin)[\W_]*$", before[-40:], re.I)
            if not (quoted or named):
                continue
        yield value


def classify(repo, base, previous):
    """New/moved refs default HOLD; never expand an approved candidate set."""
    ancestors = set(git(repo, "rev-list", base).decode().splitlines())
    old = {r["branch"]: r for r in previous}
    result = []
    raw = git(repo, "for-each-ref", "--format=%(refname) %(objectname) %(symref)",
              "refs/remotes/origin").decode()
    for line in raw.splitlines():
        fields = line.split()
        ref, sha = fields[:2]
        name = ref.removeprefix("refs/remotes/origin/")
        prior = old.get(name, {})
        candidate = (len(fields) == 2 and sha in ancestors
                     and prior.get("disposition") == "MERGED-CANDIDATE"
                     and prior.get("snapshot_commit") == sha
                     and name not in {"main", "HEAD"}
                     and not name.startswith(("ops/", "night", "archive/", "records/")))
        result.append(dict(branch=name, snapshot_commit=sha,
                           disposition="MERGED-CANDIDATE" if candidate else "HOLD"))
    return result


def scope(base, branches):
    return [("refs/remotes/origin/main", base)] + [
        ("refs/remotes/origin/" + r["branch"], r["snapshot_commit"])
        for r in branches if r["disposition"] != "MERGED-CANDIDATE"
        and r["branch"] not in {"main", "HEAD"}]


def blobs(repo, base, commit):
    """Yield regular tracked blobs; delta scanning is equivalent to full tips."""
    if commit == base:
        raw = git(repo, "ls-tree", "-r", "-z", commit)
        for record in raw.split(b"\0"):
            if not record:
                continue
            meta, path = record.split(b"\t", 1)
            mode, kind, oid = meta.decode().split()
            name = path.decode()
            if mode in {"100644", "100755"} and kind == "blob" and allowed(name):
                yield name, oid
    else:
        raw = git(repo, "diff-tree", "-r", "--no-commit-id", "--raw", "-z",
                  "--no-renames", base, commit).split(b"\0")
        for index in range(0, len(raw) - 1, 2):
            meta, path = raw[index].decode().split(), raw[index + 1].decode()
            if meta[1] in {"100644", "100755"} and allowed(path):
                yield path, meta[3]


def text_blobs(repo, objects):
    """Stream bounded batches; avoid one process per blob and binary payloads."""
    for start in range(0, len(objects), 128):
        chunk = objects[start:start + 128]
        raw = io.BytesIO(git(repo, "cat-file", "--batch",
                             data=("\n".join(chunk) + "\n").encode()))
        for oid in chunk:
            header = raw.readline().split()
            if len(header) != 3 or header[1] != b"blob":
                raise ValueError("unavailable source blob " + oid)
            content = raw.read(int(header[2]))
            if raw.read(1) != b"\n":
                raise ValueError("malformed cat-file stream")
            try:
                text = content.decode("utf-8") if b"\0" not in content else ""
            except UnicodeDecodeError:
                text = ""
            yield oid, text


def reachable(repo, refs):
    if not refs:
        return set()
    return set(git(repo, "rev-list", "--stdin", data=("\n".join(refs) + "\n").encode())
               .decode().splitlines())


def resolve_literals(repo, values):
    # Most candidates are numeric fixture data. Index object names once rather
    # than asking Git to search the alternate pack index for every absent token.
    objects = sorted(set(git(repo, "cat-file", "--batch-all-objects", "--unordered",
                             "--batch-check=%(objectname)").decode().splitlines()))
    possible = []
    for value in values:
        index = bisect_left(objects, value)
        if index < len(objects) and objects[index].startswith(value):
            possible.append(value)
    if not possible:
        return {}
    checks = git(repo, "cat-file", "--batch-check=%(objectname) %(objecttype)",
                 data="".join(v + "^{commit}\n" for v in possible).encode()).decode().splitlines()
    return dict(zip(possible, checks, strict=True))


def inventory(repo, output, previous):
    output.mkdir(parents=True, exist_ok=True)
    base = git(repo, "rev-parse", "refs/remotes/origin/main^{commit}").decode().strip()
    branches = classify(repo, base, previous)
    sources = {}
    scopes = scope(base, branches)
    for index, (ref, sha) in enumerate(scopes):
        for path, oid in blobs(repo, base, sha):
            sources.setdefault(oid, []).append(f"{ref}@{sha}:{path}")
        if index % 100 == 0:
            print(f"scope {index + 1}/{len(scopes)}; unique blobs {len(sources)}", flush=True)
    literals, digests = {}, []
    for blob_index, (oid, content) in enumerate(text_blobs(repo, sorted(sources))):
        if blob_index % 2000 == 0:
            print(f"text blobs {blob_index}/{len(sources)}", flush=True)
        source_samples = sorted(sources[oid])[:3]
        source_code = next((s for s in sources[oid] if any(
            f":{root}/" in s for root in ("joulewise", "scripts", "tools"))
            and s.endswith((".py", ".sh", ".js", ".mjs"))), None)
        for line, text in enumerate(content.splitlines(), 1):
            values = set(commit_literals(text))
            digest_values = set(DIGEST.findall(text)) if source_code else set()
            if not values and not digest_values:
                continue
            locations = [f"{s}:{line}" for s in source_samples]
            for value in values:
                record = literals.setdefault(value, {"count": 0, "locations": []})
                record["count"] += len(sources[oid])
                record["locations"] = sorted(set(record["locations"] + locations))[:3]
            for value in sorted(digest_values):
                # Unique blob locations are sufficient; scope records every tip.
                digests.append(dict(source_location=f"{source_code}:{line}", sha256_literal=value,
                                    blob=oid))
    print(f"scanned {len(sources)} unique blobs; resolving {len(literals)} literals", flush=True)
    values = sorted(literals)
    checks = resolve_literals(repo, values)
    main_set = reachable(repo, [base])
    tag_refs = git(repo, "for-each-ref", "--format=%(refname)", "refs/tags").decode().splitlines()
    # Only tags peeling to commits can retain commit ancestry.
    tags = []
    for ref in tag_refs:
        try:
            tags.append(git(repo, "rev-parse", ref + "^{commit}").decode().strip())
        except subprocess.CalledProcessError:
            pass
    tag_set = reachable(repo, tags)
    pull_refs = git(repo, "for-each-ref", "--format=%(objectname)",
                    "refs/remotes/pull", "refs/pull").decode().splitlines()
    pull_set = reachable(repo, pull_refs)
    all_set = reachable(repo, [sha for _, sha in scopes] + [r["snapshot_commit"] for r in branches])
    resolved, unresolved = {}, []
    numeric_unresolved = 0
    for literal in values:
        check = checks.get(literal, "missing")
        rec = literals[literal]
        parts = check.split()
        if len(parts) == 2 and parts[1] == "commit":
            sha = parts[0]
            coverage = ("MAIN" if sha in main_set else "TAG" if sha in tag_set
                        else "HOLD-BUNDLE-ONLY" if sha in all_set else
                        "PR-BUNDLE-ONLY" if sha in pull_set else "UNRETAINED")
            record = resolved.setdefault(sha, dict(commit=sha, coverage=coverage,
                                                   source_locations="", source_location_count=0))
            record["source_location_count"] += rec["count"]
            record["source_locations"] = ";".join(sorted(set(
                record["source_locations"].split(";") + rec["locations"]) - {""})[:3])
        else:
            if literal.isdecimal():
                numeric_unresolved += 1
            else:
                unresolved.append(dict(literal=literal, classification="UNRESOLVED-TEXT-REFERENCE",
                                       first_source=rec["locations"][0], source_location_count=rec["count"]))
    write_tsv(output / "BRANCH-TRIAGE.tsv", ["branch", "snapshot_commit", "disposition"], branches)
    write_tsv(output / "PIN-COMMITS.tsv", ["commit", "coverage", "source_locations", "source_location_count"],
              sorted(resolved.values(), key=lambda r: r["commit"]))
    write_tsv(output / "PIN-UNRESOLVED.tsv", ["literal", "classification", "first_source", "source_location_count"], unresolved)
    write_tsv(output / "SOURCE-DIGESTS.tsv", ["source_location", "sha256_literal", "blob"], digests)
    write_tsv(output / "CENSUS-SCOPE.tsv", ["ref", "commit", "scan"],
              [dict(ref=r, commit=s, scan="FULL" if s == base else "DELTA-PLUS-MAIN") for r, s in scopes])
    (output / "CENSUS.json").write_text(json.dumps(dict(
        main=base, scope_tips=len(scopes), unique_blobs=len(sources), commits=len(resolved),
        unresolved=len(unresolved), network_verified=False,
        numeric_only_unresolved_omitted=numeric_unresolved,
        exclusions=sorted(SEALED) + ["fixture data payloads (only fixture source/docs are scanned)"],
        numeric_policy="numeric-only candidates require quoting or commit/SHA/head/revision/pin context",
        source_locations="up to 3 samples per identity; counts are complete",
    ), indent=2, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--triage", type=Path, default=Path("docs/ops/BRANCH-TRIAGE.tsv"))
    args = parser.parse_args()
    inventory(args.repo, args.output, rows(args.triage))


if __name__ == "__main__":
    main()
