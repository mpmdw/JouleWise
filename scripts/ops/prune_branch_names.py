#!/usr/bin/env python3
"""Grep candidate branch names in code/config/registrations on main + HOLD tips.

Exit 1 means matches need owner dispositions. No branch is ever approved here.
Unchanged HOLD files inherit main's results; changed files are grepped at tip.
"""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile

from prune_inventory import blobs, rows, scope, text_blobs, write_tsv

ROOTS = {"joulewise", "scripts", "tools", "tests", "configs", ".github"}


def literal_pattern(values):
    """Share prefixes explicitly; a flat union retries hundreds of impl/ names."""
    root = {}
    for value in values:
        node = root
        for character in value:
            node = node.setdefault(character, {})
        node[None] = True

    def encode(node):
        choices = [re.escape(char) + encode(child) for char, child in node.items() if char is not None]
        body = choices[0] if len(choices) == 1 else "(?:" + "|".join(choices) + ")"
        if not choices:
            return ""
        return "(?:" + body + ")?" if None in node else body

    return re.compile(encode(root))


def scan(repo, census, output):
    branches = rows(census / "BRANCH-TRIAGE.tsv")
    candidates = sorted(r["branch"] for r in branches if r["disposition"] == "MERGED-CANDIDATE")
    base = next(r["commit"] for r in rows(census / "CENSUS-SCOPE.tsv") if r["scan"] == "FULL")
    matches = []
    if candidates:
        sources = {}
        scopes = scope(base, branches)
        for index, (ref, sha) in enumerate(scopes):
            for path, oid in blobs(repo, base, sha):
                if (path.split("/", 1)[0] in ROOTS
                        or (path.startswith("docs/") and "registration" in path.lower())):
                    sources.setdefault(oid, []).append((ref, sha, path))
            if index % 100 == 0:
                print(f"name scope {index + 1}/{len(scopes)}", flush=True)
        with tempfile.TemporaryDirectory(prefix="jw-prune-names-") as tmp:
            names = Path(tmp) / "names.txt"
            # A literal-regex prefilter streams each eligible blob once. Only
            # positive blobs need Git grep's comparatively expensive per-object
            # revision setup. Escaping preserves exactly the fixed-string set;
            # Git grep below remains the line/match authority.
            pattern = literal_pattern(candidates)
            groups = {}
            for oid, content in text_blobs(repo, sorted(sources)):
                if pattern.search(content):
                    relevant = tuple(n for n in candidates if n in content)
                    groups.setdefault(relevant, []).append(oid)
            print(f"name scan: {len(sources)} source blobs; {sum(map(len, groups.values()))} positives", flush=True)
            # Grep each distinct allowed regular blob once, then expand hits to
            # every source ref/path. No pathspec can follow a symlink or expand
            # into a sealed path; Git receives exact blob object IDs only.
            for relevant, objects in groups.items():
                # Irrelevant patterns cannot match these blobs. Grouping avoids
                # asking Git to retry all ~700 names on every positive line.
                names.write_text("\n".join(relevant) + "\n")
                for start in range(0, len(objects), 128):
                    proc = subprocess.run(["git", "-c", "gc.auto=0", "-C", str(repo), "grep", "--threads=1",
                                           "-n", "-I", "-F", "-f", str(names.resolve()),
                                           *objects[start:start + 128]], capture_output=True, text=True)
                    if proc.returncode not in {0, 1}:
                        raise RuntimeError(proc.stderr)
                    for line in proc.stdout.splitlines():
                        oid, number, text = line.split(":", 2)
                        for name in relevant:
                            if name not in text:
                                continue
                            for ref, sha, path in sources[oid]:
                                matches.append(dict(ref=ref, commit=sha, path=path, line=number,
                                                    candidate=name, disposition="REVIEW", text=text.strip()[:240].rstrip()))
    write_tsv(output, ["ref", "commit", "path", "line", "candidate", "disposition", "text"], matches)
    return bool(matches)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--census", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(scan(args.repo, args.census, args.output))


if __name__ == "__main__":
    main()
