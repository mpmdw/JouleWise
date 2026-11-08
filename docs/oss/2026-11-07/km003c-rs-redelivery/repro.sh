#!/usr/bin/env bash
# UNRUN: written by an agent on 2026-11-07 and never executed. Read it in full
# before running any stage.
#
# km003c-rs item D: a re-delivery longer than 8 samples is integrated twice.
# Reproduces it at the pinned upstream commit, then checks fix.patch.
#
# Run one stage at a time:
#   bash /private/tmp/jwoss-ro/km003c-rs-redelivery/kit/repro.sh fetch
#       git only: clone the pin, apply failing-test.patch. Runs no upstream code.
#   bash /private/tmp/jwoss-ro/km003c-rs-redelivery/kit/repro.sh surface
#       cargo tree: downloads crate sources into $WORK/cargo-home and lists
#       every build script and proc macro the test build would run. Compiles nothing.
#   I_READ_THE_BUILD_SURFACE=1 bash /private/tmp/jwoss-ro/km003c-rs-redelivery/kit/repro.sh fail
#       FIRST STEP THAT EXECUTES UPSTREAM CODE (build scripts, proc macros, tests).
#       Expect: "test result: FAILED. 8 passed; 2 failed".
#   I_READ_THE_BUILD_SURFACE=1 bash /private/tmp/jwoss-ro/km003c-rs-redelivery/kit/repro.sh fixed
#       Applies fix.patch. Expect: "test result: ok. 10 passed; 0 failed".
#   I_READ_THE_BUILD_SURFACE=1 bash /private/tmp/jwoss-ro/km003c-rs-redelivery/kit/repro.sh regress
#       All km003c-lib unit tests with the fix, plus rustfmt and clippy if present.
#       Default features only: the temp-file tests (preferences, recording/journal,
#       recording/writer) and the one hardware test are feature-gated and not compiled.
#
# Statically reviewed by a second agent on 2026-11-07: both patches re-applied to
# the pin in a scratch index in either order (same blob), patched file passes
# rustfmt --check (max_width 120), script passes bash -n. Still never executed.
#
# Everything lands under $WORK (default /private/tmp/jwoss-run/km003c-rs-redelivery):
# the clone, CARGO_HOME and CARGO_TARGET_DIR. Delete it with rm -rf when done.
set -euo pipefail

PIN=71f69e4a35c1184cc114a62145b8a8241d3e13e9
URL=https://github.com/okhsunrog/km003c-rs
KIT=/private/tmp/jwoss-ro/km003c-rs-redelivery/kit
WORK=${WORK:-/private/tmp/jwoss-run/km003c-rs-redelivery}
SRC=$WORK/src
# Homebrew's cargo ignores rust-toolchain.toml (which pins 1.99.1 plus a wasm32
# target). A rustup proxy would try to install that toolchain instead.
CARGO_BIN=${CARGO_BIN:-/opt/homebrew/bin/cargo}
export RUSTC=${RUSTC:-/opt/homebrew/bin/rustc}
export CARGO_HOME=$WORK/cargo-home
export CARGO_TARGET_DIR=$WORK/target

gate() {
  if [ "${I_READ_THE_BUILD_SURFACE:-}" != 1 ]; then
    echo "Stop: read RUN-ME.md section 2 and $WORK/build-surface.txt, then set I_READ_THE_BUILD_SURFACE=1." >&2
    exit 2
  fi
  test "$(git -C "$SRC" rev-parse HEAD)" = "$PIN"
}

fetch() {
  if [ -e "$SRC" ]; then
    echo "$SRC exists; rm -rf $WORK for a fresh run." >&2
    exit 1
  fi
  mkdir -p "$WORK"
  git init -q "$SRC"
  git -C "$SRC" remote add origin "$URL"
  git -C "$SRC" fetch -q --depth 1 origin "$PIN"
  git -C "$SRC" -c core.hooksPath=/dev/null -c advice.detachedHead=false checkout -q --detach FETCH_HEAD
  test "$(git -C "$SRC" rev-parse HEAD)" = "$PIN"
  git -C "$SRC" apply "$KIT/failing-test.patch"
  git -C "$SRC" apply --check "$KIT/fix.patch"
  git -C "$SRC" diff --stat
  echo "Fetched $PIN and applied failing-test.patch. Nothing was built or run."
}

surface() {
  cd "$SRC"
  command -v "$CARGO_BIN" "$RUSTC"
  "$CARGO_BIN" --version
  "$RUSTC" --version
  "$CARGO_BIN" tree -p km003c-lib --locked -e normal,build,dev --prefix none --no-dedupe --format '{p}' |
    sort -u >"$WORK/tree.txt"
  echo "$(wc -l <"$WORK/tree.txt") packages in the km003c-lib build (default features, host target)."
  # Code that runs at compile time: build scripts and proc macros.
  : >"$WORK/build-surface.txt"
  found=0
  while read -r name version _; do
    version=${version#v}
    dir=$(ls -d "$CARGO_HOME"/registry/src/*/"$name-$version" 2>/dev/null | head -1 || true)
    [ -n "$dir" ] || continue
    found=$((found + 1))
    kinds=""
    [ -f "$dir/build.rs" ] && kinds="$kinds build.rs"
    /usr/bin/grep -q -E '^[[:space:]]*build[[:space:]]*=[[:space:]]*"' "$dir/Cargo.toml" && kinds="$kinds build-key"
    /usr/bin/grep -q -E '^[[:space:]]*proc-macro[[:space:]]*=[[:space:]]*true' "$dir/Cargo.toml" && kinds="$kinds proc-macro"
    [ -z "$kinds" ] || printf '%-28s %-12s%-28s %s\n' "$name" "$version" "$kinds" "$dir" >>"$WORK/build-surface.txt"
  done <"$WORK/tree.txt"
  if [ "$found" -eq 0 ]; then
    echo "No crate sources under $CARGO_HOME/registry/src: the list below is empty, not clean." >&2
    echo "Run '$CARGO_BIN fetch --locked' in $SRC (downloads only) and repeat this stage." >&2
    exit 1
  fi
  echo "$found registry crates found; with build scripts or proc macros:"
  cat "$WORK/build-surface.txt"
  echo "In-repo build scripts on this path (expect none):"
  find "$SRC/km003c-lib" -name build.rs -print
  ls "$SRC"/build.rs 2>/dev/null || true
  echo "Read every file listed above before the fail stage. Nothing was compiled."
}

fail() {
  gate
  cd "$SRC"
  set +e
  "$CARGO_BIN" test -p km003c-lib --lib --locked measurement::tests 2>&1 | tee "$WORK/fail.log"
  status=${PIPESTATUS[0]}
  set -e
  if [ "$status" -eq 0 ]; then
    echo "UNEXPECTED: the new tests passed without the fix." >&2
    exit 1
  fi
  /usr/bin/grep -E "^test result:|left:|right:|panicked" "$WORK/fail.log" || true
  if ! /usr/bin/grep -q "^test result: FAILED. 8 passed; 2 failed" "$WORK/fail.log"; then
    echo "UNEXPECTED: not 'FAILED. 8 passed; 2 failed' (compile error, or another test failed?). Read $WORK/fail.log." >&2
    exit 1
  fi
  if ! /usr/bin/grep -q "left: 45000" "$WORK/fail.log" || ! /usr/bin/grep -q "left: 1217000" "$WORK/fail.log"; then
    echo "UNEXPECTED: the failures are not the predicted 45000/27000 and 1217000/1199000. The hand trace is wrong; stop." >&2
    exit 1
  fi
  echo "As predicted: only the two new tests fail at the pin, with the hand-traced values."
}

fixed() {
  gate
  cd "$SRC"
  if git apply --check -R "$KIT/fix.patch" 2>/dev/null; then
    echo "fix.patch is already applied; re-running the tests."
  else
    git apply "$KIT/fix.patch"
  fi
  "$CARGO_BIN" test -p km003c-lib --lib --locked measurement::tests 2>&1 | tee "$WORK/fixed.log"
  if ! /usr/bin/grep -q "^test result: ok. 10 passed; 0 failed" "$WORK/fixed.log"; then
    echo "UNEXPECTED: not 'ok. 10 passed; 0 failed' with the fix. Read $WORK/fixed.log; stop before writing upstream." >&2
    exit 1
  fi
}

regress() {
  gate
  cd "$SRC"
  git apply --check -R "$KIT/fix.patch" 2>/dev/null || {
    echo "fix.patch is not applied; run the fixed stage first." >&2
    exit 1
  }
  "$CARGO_BIN" test -p km003c-lib --lib --locked 2>&1 | tee "$WORK/regress.log"
  if "$CARGO_BIN" fmt --version >/dev/null 2>&1; then
    "$CARGO_BIN" fmt -p km003c-lib -- --check
  fi
  if "$CARGO_BIN" clippy --version >/dev/null 2>&1; then
    "$CARGO_BIN" clippy -p km003c-lib --lib --tests --locked -- -D warnings
  fi
}

case "${1:-}" in
  fetch | surface | fail | fixed | regress) "$1" ;;
  *)
    echo "usage: $0 fetch|surface|fail|fixed|regress" >&2
    exit 2
    ;;
esac
