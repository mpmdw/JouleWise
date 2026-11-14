#!/usr/bin/env bash
# CI range classifier, targeted-docs lane: decides whether a docs range needs no tests or only some.
# Usage: ci_docs_targeted.sh <before sha> <after sha>   (run from the repository root)
# Exit 1 (stdout empty): run the full suite. Exit 0: the range touches only docs paths, and stdout is
# one line, either
#   docs-only                      no file under joulewise scripts tests configs .github pyproject.toml
#                                  names any changed path (the ci_docs_only.sh result, now also for images)
#   targeted <module> [<module>..] every referencing file is a tests/**/test_*.py module; run only these
#                                  unittest modules (e.g. tests.test_docs_freshness)
# A docs path is Markdown under docs/ or at the root, or an image (.svg .png .jpg .jpeg .webp .gif)
# under docs/assets/. docs/registrations|contracts|process_traces|null|site/ are read by glob: full suite.
# A reference is the full path OR the basename (code builds paths like REPO_ROOT / "docs" / "x.md"), as a
# fixed string, in joulewise scripts tests configs .github pyproject.toml or any docs/**/*.py. A reference
# from anything but a tests/**/test_*.py module (code, helpers, fixtures, json) runs the full suite, because
# a helper can be imported by many modules. References are checked at both ends of the range. Any detector
# error, a symlink or gitlink in the range, or a module path that is not plain identifiers (no dots in a
# directory name, no component named py) runs the full suite.
set -u
before=${1:-}; after=${2:-}
[[ "$before" =~ ^[0-9a-f]{40}$ && "$before" != 0000000000000000000000000000000000000000 ]] || exit 1
[[ "$after" =~ ^[0-9a-f]{40}$ && "$after" != 0000000000000000000000000000000000000000 ]] || exit 1
git cat-file -e "$before^{commit}" 2>/dev/null || exit 1
git cat-file -e "$after^{commit}" 2>/dev/null || exit 1
paths=$(git diff --name-only --no-renames "$before..$after") || exit 1
[[ -n "$paths" ]] || exit 1
# Symlinks (120000) and gitlinks (160000) at either end are not docs: full suite.
raw=$(git diff --raw --no-renames "$before..$after") || exit 1
awk '{ if ($1 == ":120000" || $1 == ":160000" || $2 == "120000" || $2 == "160000") bad = 1 } END { exit bad }' \
  <<< "$raw" || exit 1
modules=
while IFS= read -r path; do
  case "$path" in
    # Directories that code or tests read by glob rather than by literal path: run everything.
    docs/registrations/*|docs/contracts/*|docs/process_traces/*|docs/null/*|docs/site/*) exit 1 ;;
    docs/assets/*.svg|docs/assets/*.png|docs/assets/*.jpg|docs/assets/*.jpeg|docs/assets/*.webp|docs/assets/*.gif) ;;
    docs/*.md) ;;
    */*) exit 1 ;;
    *.md) ;;
    *) exit 1 ;;
  esac
  for rev in "$before" "$after"; do
    hits=$(git grep -l -F -e "$path" -e "${path##*/}" "$rev" -- joulewise scripts tests configs .github pyproject.toml 'docs/*.py' 2>/dev/null)
    status=$?
    [[ $status -le 1 ]] || exit 1   # 0 = referenced, 1 = not, >1 = grep error
    [[ $status -eq 1 ]] && continue
    while IFS= read -r hit; do
      file=${hit#"$rev":}
      # Non-test reference (or an odd test path): full suite.
      [[ "$file" =~ ^tests(/[A-Za-z0-9_]+)*/test_[A-Za-z0-9_]*\.py$ && "/$file" != */py/* ]] || exit 1
      module=${file%.py}; module=${module//\//.}
      modules+="$module"$'\n'
    done <<< "$hits"
  done
done <<< "$paths"
modules=$(printf '%s' "$modules" | sort -u | tr '\n' ' ')
modules=${modules% }
if [[ -z "$modules" ]]; then echo "docs-only"; else echo "targeted $modules"; fi
exit 0
