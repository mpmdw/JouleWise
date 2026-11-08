# RUN-ME: km003c-rs re-delivery kit (item D)

Prepared read-only on 2026-11-07. No upstream code has been built, run or
imported, and nothing has been posted. Every script here is UNRUN. Static
checks only: `bash -n` and Python `ast.parse`. The patches were checked to
apply with `git apply --cached` on a scratch index, and the patched file was
checked with `rustfmt --check` (formatting only).

Second static review (another agent, 2026-11-07, also read-only): re-read the
upstream files at the pin, re-traced both tests by hand, re-applied both
patches in a scratch index in either order (same blob `8a7babec…`), re-ran
`rustfmt --check` on the result, confirmed via the GitHub API that the pin is
still the tip of `main` and that there are 0 open issues. Changes made by the
review are listed in section 6.

- Upstream: https://github.com/okhsunrog/km003c-rs
- Pin: `71f69e4a35c1184cc114a62145b8a8241d3e13e9` (main, 2026-11-04)
- Read-only clone with git objects only and no checkout:
  `/private/tmp/jwoss-ro/km003c-rs-redelivery/src`. Read a file with
  `git -C /private/tmp/jwoss-ro/km003c-rs-redelivery/src show 71f69e4a35c1184cc114a62145b8a8241d3e13e9:<path>`.

## 1. Files

| File | What it is |
|---|---|
| `FACT-SHEET.md` | The problem, repro, root cause (file:line), fix, tests and risk. Facts only, for you to restate. |
| `failing-test.patch` | +45 lines, `km003c-lib/src/measurement.rs` tests module only. Two `#[test]`s that fail at the pin. |
| `fix.patch` | +32 lines, `km003c-lib/src/measurement.rs` only. Applies before or after the test patch; either order gives the same file. |
| `repro.sh` | Staged runner: `fetch`, `surface`, `fail`, `fixed`, `regress`. UNRUN. |
| `model_push.py` | Stdlib-only Python model of `push()`, pin vs fix. Runs no upstream code. UNRUN. |
| `SHA256SUMS` | Checksums of the files above. |

## 2. Read this before any cargo command

Compiling `km003c-lib` runs code: build scripts and proc macros in its
dependencies, then the test binary itself. Check the following first.

**The repo's own build scripts.** None run here.

- `km003c-lib/` has no `build.rs`, and its `Cargo.toml` has no `build =` key.
  The workspace root has no `build.rs` either.
- The repo's only build scripts are `km003c-slint/build.rs` and
  `km003c-slint/slint-realtime-plot/build.rs`. `km003c-slint` is not a
  workspace member (the members are km003c-lib, km003c-cli, km003c-egui and
  realtime-plot). Nothing in this kit builds it.

**Config that cargo reads at the pin.**

- `.cargo/config.toml`: two lines, wasm32 `rustflags` only. There are no
  aliases, runners or env settings.
- `rust-toolchain.toml`: channel `1.99.1`, components clippy and rustfmt,
  target `wasm32-unknown-unknown`.
  - A **rustup proxy** `cargo` would download and install that toolchain.
  - **Homebrew's** `/opt/homebrew/bin/cargo` (1.97.1 on this Mac, with
    `cargo-fmt` and `cargo-clippy` beside it) ignores the file. `repro.sh`
    uses that path by default. `~/.rustup` exists with a stable toolchain but
    there is no `~/.cargo/bin`, so `which cargo` is also the Homebrew one.
  - The MSRV is 1.97 (`Cargo.toml` `rust-version`; the CI msrv job runs
    1.97.0).
- `Cargo.toml` and `km003c-lib/Cargo.toml`: `default = []`. The optional
  pyo3, polars, parquet, reqwest, serde, usbpd and firmware-catalog crates
  are not built.

**Direct dependencies built** (versions from `Cargo.lock`):

- modular-bitfield 0.13.1
- nusb 0.2.7, with the tokio feature
- thiserror 2.0.20
- tracing 0.1.44
- tokio 1.53.1, with sync, macros, io-util, rt, time and rt-multi-thread
- bytes 1.12.1
- num_enum 0.7.6
- zerocopy 0.8.57, with derive
- strum_macros 0.28.0
- hex 0.4.3
- aes 0.9.3
- crc32fast 1.5.2
- rand 0.10.2
- uom 0.36.0
- futures-util 0.3.34, without default features
- cbc 0.2.1

There are no native dev-dependencies.

**Proc macros expected in the graph:**

- modular-bitfield-impl 0.13.1
- num_enum_derive 0.7.6
- strum_macros 0.28.0
- thiserror-impl 2.0.20
- tokio-macros 2.7.1
- tracing-attributes 0.1.31
- zerocopy-derive 0.8.57
- rustversion 1.0.23

**Build scripts.** I could not list these without downloading crate sources.
The `surface` stage writes the exact list of build scripts and proc macros to
`$WORK/build-surface.txt`, with the path of each crate. Read every `build.rs`
it lists. The `fail` stage refuses to run until you set
`I_READ_THE_BUILD_SURFACE=1`.

**Upper bound from `Cargo.lock`** (94 crates; `cargo tree` gives the exact
set): aes, allocator-api2, autocfg, bitflags, block-padding, bytes, cbc,
cfg-if, chacha20, cipher, core-foundation, core-foundation-sys, cpubits,
cpufeatures, crc32fast, crossbeam-{deque,epoch,utils}, crypto-common, either,
equivalent, errno, foldhash, futures-{channel,core,io,macro,sink,task,util},
getrandom, hashbrown, heck, hex, hybrid-array, indexmap, inout, io-kit-sys,
libc, libm, lock_api, log, mach2, memchr, mio, modular-bitfield(-impl),
num-{bigint,complex,integer,rational,traits}, num_enum(_derive), nusb,
once_cell, parking_lot(_core), pin-project-lite, proc-macro-crate,
proc-macro2, quote, rand, rand_core, rayon(-core), rustix, rustversion,
scopeguard, signal-hook-registry, slab, smallvec, socket2, static_assertions,
strum_macros, syn 2 and 3, thiserror(-impl), tokio(-macros),
toml_{datetime,edit,parser}, tracing(-attributes,-core), typenum,
unicode-ident, uom, valuable, winnow, zerocopy(-derive).

**What the tests themselves execute.**

- `fail` and `fixed` run only the 10 tests in `measurement::tests`. These are
  pure arithmetic with no I/O.
- `regress` runs every default-feature unit test in `km003c-lib`. Under
  default features none of them touches USB, the network or the filesystem:
  `preferences.rs` is behind the `preferences` feature, and
  `recording/{export,journal,writer}.rs` (the temp-dir writers and the one
  `#[ignore]`d hardware test at `writer.rs:424`) are behind `polars`, so they
  are not even compiled. `memory.rs` uses `include_bytes!` fixtures. The
  `firmware`, `session` and `install` async tests use in-process fakes.

## 3. Run

Use a fresh directory outside `~`. The clone, `CARGO_HOME` and
`CARGO_TARGET_DIR` all go under
`WORK=/private/tmp/jwoss-run/km003c-rs-redelivery`. Your `~/.cargo` is not
touched.

```sh
# 0. Optional, runs no upstream code: the arithmetic, pin vs fix.
python3 -I /private/tmp/jwoss-ro/km003c-rs-redelivery/kit/model_push.py
mkdir -p /private/tmp/jwoss-run
git -C /Users/edr/code/CapstoneProject/jw-wt/handoff show origin/main:tests/fixtures/km003c/redelivery1000_slice.jsonl > /private/tmp/jwoss-run/redelivery1000_slice.jsonl
python3 -I /private/tmp/jwoss-ro/km003c-rs-redelivery/kit/model_push.py /private/tmp/jwoss-run/redelivery1000_slice.jsonl

# 1. Verify the kit, then read repro.sh and both patches.
cd /private/tmp/jwoss-ro/km003c-rs-redelivery/kit && shasum -a 256 -c SHA256SUMS

# 2. Clone the pin and apply the failing tests (git only).
bash /private/tmp/jwoss-ro/km003c-rs-redelivery/kit/repro.sh fetch

# 3. List the build surface (downloads crate sources; compiles nothing). Read it.
bash /private/tmp/jwoss-ro/km003c-rs-redelivery/kit/repro.sh surface
less /private/tmp/jwoss-run/km003c-rs-redelivery/build-surface.txt

# 4. FIRST STEP THAT EXECUTES UPSTREAM CODE: watch the new tests fail.
I_READ_THE_BUILD_SURFACE=1 bash /private/tmp/jwoss-ro/km003c-rs-redelivery/kit/repro.sh fail

# 5. Apply the fix and watch them pass.
I_READ_THE_BUILD_SURFACE=1 bash /private/tmp/jwoss-ro/km003c-rs-redelivery/kit/repro.sh fixed

# 6. Regression: all km003c-lib unit tests, plus rustfmt and clippy if installed.
I_READ_THE_BUILD_SURFACE=1 bash /private/tmp/jwoss-ro/km003c-rs-redelivery/kit/repro.sh regress

# 7. Clean up.
rm -rf /private/tmp/jwoss-run/km003c-rs-redelivery
```

Equivalent bare commands, run from `$WORK/src` with the same environment:
`cargo test -p km003c-lib --lib --locked measurement::tests`, then
`git apply /private/tmp/jwoss-ro/km003c-rs-redelivery/kit/fix.patch` and the
same test again.

## 4. Expected results

These are predicted by hand trace and have not been observed.

- **Step 0, synthetic (A).** Pin: elapsed 45000, 47 accepted, 8 discarded.
  Fix: 27000, 28, 27.
- **Step 0, observed sequence (B).** Pin: 1217000, 1219, 8. Fix: 1199000,
  1200, 27.
- **Step 0, fixture.** Same counts as B. The pin's energy is about 1.30 J
  higher.
- **Step 4.** `test result: FAILED. 8 passed; 2 failed`.
  - `a_redelivery_longer_than_the_restart_threshold_is_not_integrated_twice`:
    `left: 45000`, `right: 27000`.
  - `an_observed_1000_sps_redelivery_keeps_device_time`: `left: 1217000`,
    `right: 1199000`.
- **Step 5.** `test result: ok. 10 passed; 0 failed`.
- **Step 6.** All unit tests pass (0 ignored under default features), rustfmt
  is clean, and clippy raises no warnings.

`repro.sh fail` and `repro.sh fixed` now check their own logs for exactly
these lines and exit 1 with an `UNEXPECTED:` message otherwise. If that
happens, stop: the hand trace is wrong somewhere. Fix the kit before writing
anything upstream.

## 5. Afterwards (you write and post everything yourself)

- **Issue.** Restate `FACT-SHEET.md` in your own words. Cite `WEB.md:265-267`
  and PR #54: the maintainer already noted the symptom. Attach the failing
  test, and offer the fix rather than pushing it. The maintainer usually
  re-implements and credits.
- **Hardware.** The maintainer will probably ask for runs at 50 and
  1000 SPS. That needs the meter.
- **Separate docs item.** A docs PR to km003c-protocol-research is a
  separate item and is not prepared here.
- **Scrubbing.** Quote only sequence numbers from the JouleWise fixture. Do
  not quote the meter serial or hardware ID, and do not mention night-archive
  provenance.
- **If the maintainer asks for a PR instead.** There is no CONTRIBUTING file
  or CLA; `README.md:543-545` just says "Contributions welcome!". The gates
  are CI (`.github/workflows/ci.yml`) and `justfile ci`: `cargo fmt --all --
  --check`, `cargo test --workspace --all-targets [--all-features] --locked`,
  `cargo clippy --workspace --all-targets [--all-features] -- -D warnings`,
  `cargo doc` with `RUSTDOCFLAGS=-D warnings`, MSRV 1.97, edition 2024.
  `CHANGELOG.md` follows Keep a Changelog with an `## [Unreleased]` section;
  the previous fix in this area is logged there (`CHANGELOG.md:165-168`), so
  add a `### Fixed` line. Also update `km003c-egui/WEB.md:265-267`, which
  would otherwise describe the pre-fix behaviour.

## 6. Changes made by the second static review

- `failing-test.patch`: the second test used
  `(..).chain(..).filter_map(..).last()`. That chain is a
  `DoubleEndedIterator`, and clippy's `double_ended_iterator_last` (warn by
  default since 1.86; CI and `regress` run `-D warnings`) may fire on it even
  though `next_back()` would be wrong here (the closure has side effects).
  Rewritten as a plain `for` loop with `if let`. +43 -> +45 lines; same
  assertions; still fails at the pin with `left: 1217000, right: 1199000`.
- `repro.sh fail`: exits 1 unless the log contains
  `test result: FAILED. 8 passed; 2 failed` and both predicted `left:`
  values, so a compile error or a different failing test is not mistaken for
  the repro.
- `repro.sh fixed`: idempotent (skips `git apply` when the fix is already
  applied) and exits 1 unless the log contains
  `test result: ok. 10 passed; 0 failed`.
- RUN-ME section 2: corrected the `regress` description. The temp-dir tests
  and the hardware test are feature-gated and not built; "one ignored" was
  wrong for default features.
- RUN-ME section 5: added the PR conventions above.
- `FACT-SHEET.md`: line counts; one added risk (the 64-sample window at
  2 SPS spans 32 s, so the restart there rests entirely on the grid argument);
  GitHub API confirmation of the pin and open-issue count.
- `SHA256SUMS` regenerated.
