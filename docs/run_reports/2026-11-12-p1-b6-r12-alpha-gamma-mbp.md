# P1 Block 6 R12 — full-volume ALPHA and GAMMA sessions on the MBP

Written 2026-11-12 23:05 PST (`/bin/date`), **before any ALPHA/GAMMA
collection**. Synthetic only: no custody, no real session, no Block 5/6 data.
Branch `analysis/2026-11-12-b6-r12-alpha-gamma`, off
`analysis/2026-11-11-b6-r12` @ `be02cd695`. The R12 seat's report
(`docs/run_reports/2026-11-11-p1-b6-r12-r3.md`) is not edited here.

**Authority.** Ed, 2026-11-12 ~22:55 PST, via the lead: start the R12
full-volume ALPHA and GAMMA sessions on the idle measurement MacBook Pro now,
in parallel with the full BETA root `r12-r3-full-beta-23` already running on
the Air, "unless waiting strengthens the science". Waiting for root 23's gate
would not strengthen it: the ALPHA/GAMMA inputs, collector, courier profile
and predictions below are fixed now and do not depend on any BETA outcome,
and the roots are independent. Its only value is economic: if root 23 exposes
a profile defect in the ordinary full phase, these two roots share that
profile and would be discarded too, costing idle MBP hours only. The seat
report's "no other cohort before the full gate" sequencing is superseded by
Ed's instruction for these two roots; nothing in RL-48/49/98 requires it.

Obligation served: RL-48 item 5 / RL-98 term 3, "§13 full-size through the
real stage chain shown for N of 3 packs". RL-98 needs one; these add ALPHA and
GAMMA. They are not the closed nine-session dry run, carry no closed-nine or
serial/pool claim, and are not the Air dry-run wall/memory of RL-48.

## Host

MacBook Pro **Mac15,9**, 16 CPUs, 128 GiB (137,438,953,472 bytes), macOS
uptime 29 days, sleep prevented by an existing `caffeinate` assertion (read
with `pmset -g`, not changed). Interpreter
`/opt/homebrew/opt/python@3.13/bin/python3.13` = **Python 3.13.1**; zstd
1.5.7 at `/opt/homebrew/bin/zstd`. The Air (root 23) runs Python 3.13.18 from
the same Homebrew path. The runtime's stdlib seams were developed on 3.13.18;
a 3.13.1 incompatibility would surface in the smoke phase and is a failure,
never patched around.

**Per-host numbers.** Native generation ratios, wall times and RSS from these
sessions are MBP numbers, measured with **two sessions running concurrently**
on the MBP. They are reported per session and per host and are **not pooled**
with Air sessions (root 23 or any other). **No cross-host byte-equality claim**
is made for anything generated here.

## Code: what changed, and what BETA root 23 hashes

Changed on this branch only:

- `scripts/b6_r12_profile_session.py`: the fresh-root gate admits
  `--pack alpha|beta|gamma` (still only `--scenario plain --volume full`, new
  root). Declaration text for BETA is byte-identical to root 23's; ALPHA/GAMMA
  name their pack.
- `scripts/b6_r12_full_verify.py`: per-pack `PACK_EXPECTATIONS`, session id
  `r1-<pack>` instead of the literal `r1-beta`; refuses anything but a
  completed plain/full single-pack courier-profile root.
- `scripts/b6_r12_full_supervise.py`: new `--generation-only` (exclusive with
  `--stem`) stops after the original ordinary desk, journal status
  `generated`. Default behaviour unchanged.
- `tests/test_b6_r12_session_fixture.py`: `FullProductionSessionTests` take
  per-pack expectations; new control class `FullPackExpectationTests`.
- `scripts/b6_r12_mbp_pair.zsh`: the external launcher used below.

Byte-identical to root 23's recorded `generator_files_sha256`: courier profile
`4e7a8ae47fcc…`, runtime `14ec9e7dfd31…`, orchestrate `cb40e3eee692…`, session
fixture `c1e89033033c…`, verify `947d1c3d43ec…`, chain fixture
`125ed289f12f…`; the single-pack runner and reduced-set initializer are
unchanged. Only `b6_r12_profile_session.py` differs, as expected. The seat's
worktree and root 23 are not touched.

## Prior chain root

**The cohort-16 seed is valid for ALPHA/GAMMA but cannot be used on the MBP.**

- Pack validity: `b6_r12_orchestrate.seed_calibration` builds the seed from
  one fixed prerequisite (`d117_floor_qwen3-1p7b_v5`, pinned smoke driver,
  two valid captures, `smoke.copy_ledger`). Nothing in it is pack-specific;
  the per-session smoke runs inside each session. ALPHA r1 already ran from
  this seed (`r12-r3-cohort-17`, `r12-r3-reduced-18`).
- Not relocatable: `b6_r12_reduced_set.initialize` requires
  `seed-receipt.json`'s absolute `smoke.measurement` to lie inside the given
  prior root (`child()`), and the seed's calibration ledger embeds 10 absolute
  `/Volumes/JW-EXT/...` capture locators. A copy at another path is refused at
  initialization. The MBP cannot create `/Volumes/JW-EXT` without root, so the
  seed is not copied there at all.

**MBP prior**: a fresh seed, written by the same pinned prerequisite path that
made cohort-16's (`b6_r12_batch.py` step "seed"):
`b6_r12_session_fixture.py --out <T>/r12-r3-mbp-seed-1 --synthetic-models
--volume prerequisite --seed-probe`. Its exit code goes to
`<seed>/generator-parent-exit.txt`, as `b6_r12_batch.py ended()` writes it.
Copied runtime is the same `14ec9e7dfd31…` as cohort-16's. Air time was
265.8 s. Both MBP sessions read this one seed (read-only, hash-checked per
session). Different seed bytes from root 23's prior is a declared input
difference, not a science difference.

## Paths (deviation from the brief, forced by the code)

Every R12 entry point refuses a root under `/Users/edr` (`prepare()`,
`safe_root()`, `bootstrap()`), and the fixture's audit guard denies every
access under `/Users/edr` lexically. That guard is what keeps the fixture away
from the MBP's real custody and models. Roots therefore cannot live under
`/Users/edr/code/jw-wt/`. They live at **`T=/private/tmp/r12-mbp-tmp`**
(resolved, outside `/Users/edr`, user-writable, no mount, no sudo). This path
also exists on the Air, so a completed root can be moved there at the same
absolute path for the reader. The repository clone is
`/Users/edr/code/jw-wt/r12-mbp` (fresh `git clone` from GitHub). Only outer
generator processes read it; any fixture-child access would be denied and
show up in `denials.jsonl` and the smoke phase.

macOS `periodic daily` deletes `/tmp` files not accessed for 3 days: run the
reader, or move the roots, within about 2 days of completion.

## Reader deferred to the Air

`b6_r12_verify.prepare_run_inputs` writes `"host": "Air"` into the option (c)
input document, and `independent_recompute_b6.py` refuses any other host
(`run_host_or_audit_invalid`). Running the reader on the MBP would record a
false host. So the MBP runs **generation only** (seed, smoke driver, smoke
desk, ordinary full driver, ordinary full desk). The production reader and the
two named tests run later on the Air, from a checkout of this branch, against
the root at the identical path:

```sh
# on the Air, after both MBP journals say "generated"
mkdir -p /private/tmp/r12-mbp-tmp
rsync -a mbp-ts:/private/tmp/r12-mbp-tmp/r12-r3-full-<pack>-mbp-1 /private/tmp/r12-mbp-tmp/
/usr/bin/env -u PYTHONPATH -u PYTHONSTARTUP -u PYTHONHOME PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_ATTR_NOSYSTEM=1 XDG_CONFIG_HOME=/private/tmp/r12-mbp-tmp/r12-xdg-empty PYTHONNOUSERSITE=1 TMPDIR=/private/tmp/r12-mbp-tmp /opt/homebrew/opt/python@3.13/bin/python3.13 -B scripts/b6_r12_full_verify.py --cohort-root /private/tmp/r12-mbp-tmp/r12-r3-full-<pack>-mbp-1 --stem full-reader-air-20261113
```

Reader wall and RSS are then Air numbers. The native generation interval is
read from file mtimes (declaration through final desk compression log), so
the move must keep mtimes. `rsync -a` keeps them; nanosecond precision
depends on the rsync build, so the lead should also record the MBP-side mtimes
(`stat -f %Fm`) of `fixture-manifests/r1-<pack>.json` and
`<archive>.desk/compression.jsonl` before moving.

## Predictions, per pack (declared before collection)

Arithmetic from the pinned code/config at `f31aca19f`
(`configs/campaigns/<campaign>/plan_tree.json`, `stage_graph`,
`campaign_collection` `expected_count`), as the BETA section did. Source policy
(unchanged from BETA): 335 s model-source dwell, 10 Hz plist, 16 CPU
entries/frame, token inputs 1.0/0.05 s, normal OFF. Test floor 334 s.

| | ALPHA | GAMMA |
|---|---|---|
| campaign | `d117_floor_qwen3-1p7b_v5` | `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` |
| session id | `r1-alpha` | `r1-gamma` |
| science collections | 10+20+20+10+20+20 = 100 | 20+20+20+20 = 80 |
| bound collection | 18 | 18 |
| reference collections | 3+1+3 = 7 | 3+1+1+1+3 = 9 |
| roster members = executed primary streams | **125** | **107** |
| target frames at 335 s (3,350/member) | 418,750 | 358,450 |
| target CPU entries (×16) | 6,700,000 | 5,735,200 |
| target primary seconds | 41,875 | 35,845 |
| test floor at 334 s: frames / CPU entries | 417,500 / 6,680,000 | 357,380 / 5,718,080 |
| production session keys (registry) | **122** (`ALPHA`) | **93** (`GAMMA`) |

Counts and cadence are measured from actual writer bytes, never read off these
targets. Calibration copies and validation captures never enter the primary
census. Both sessions: 50 Hz / 20 ms meter with zero drops, duplicates and
irregular gaps; meter span ≥ summed primary durations; registered monitor
cadences with 0 errors; original smoke courier sent and heartbeat seen, with
file-transport records (the supervisor checks this before any ordinary
collection); ordinary courier records file transport and no mail; one original
loop attempt ending at ROTATE; generator parent exit 0. Then, on the Air:
option (c) exits 0 and the comparator agrees, and the emitted session keys
equal the registry list exactly. These are the two
`FullProductionSessionTests` with the per-pack table above.

**Stated risk, GAMMA keys.** A lone GAMMA session has no counting ALPHA/BETA
floor session in its archive set, so `attach_gamma` takes the "floor
unavailable" branch. Whether that still emits all 93 registered keys (some may
be null) is not established. The prediction is 93, stated in advance. A
mismatch is reported as observed; the registry and the test are not edited
afterwards.

**Native time.** Per session, from the completed receipts: native wall
(declaration through final desk compression) over summed primary seconds, and
over whole-meter span, reported separately. Expectation, not a prediction:
root 23's Air phases give smoke driver 124 s and smoke desk 126 s. Retired
BETA cohort-15's full collection took 14,928 s for 41,973 primary-seconds
(ratio 0.356). Scaling by primaries gives ALPHA ≈ 4.2 h and GAMMA ≈ 3.6 h of
ordinary collection. Add seed (~4.5 min), smoke (~4 min) and desk. Expected
MBP wall time from launch to `generated`: **ALPHA ~4.5–6 h, GAMMA ~4–5.5 h**
(contention between two concurrent sessions, and the 3.13.1 interpreter,
widen this), so about 03:30–05:30 PST on 13 Nov.

**Disk.** Root 23 grew 1.3 → 1.7 GiB in its first ~40 min of ordinary
collection; retired cohort-15's full BETA main was 5.4 GiB before desk
compression. Estimate ≤ 15 GiB per root, two roots plus seed ≤ 31 GiB, from
88 GiB free on the MBP data volume: ≥ 57 GiB left, above the 30 GiB floor.

## Commands (MBP)

Fresh clone of this branch at `/Users/edr/code/jw-wt/r12-mbp`; the generator
commit is that clone's HEAD (this report's commit), which every manifest
records. The canonical clone `/Users/edr/code/JouleWise` is not used.

```sh
mkdir -p /private/tmp/r12-mbp-tmp
cd /Users/edr/code/jw-wt/r12-mbp
nohup /bin/zsh -f scripts/b6_r12_mbp_pair.zsh /private/tmp/r12-mbp-tmp r12-r3-mbp-seed-1 \
    alpha:r12-r3-full-alpha-mbp-1 gamma:r12-r3-full-gamma-mbp-1 \
    > /private/tmp/r12-mbp-tmp/launcher.log 2>&1 < /dev/null &
```

Inside the launcher, every step runs under the same sanitized environment as
the Air BETA command (`env -u PYTHONPATH -u PYTHONSTARTUP -u PYTHONHOME`,
`PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin`, `GIT_CONFIG_GLOBAL=/dev/null`,
`GIT_CONFIG_NOSYSTEM=1`, `GIT_ATTR_NOSYSTEM=1`,
`XDG_CONFIG_HOME=/private/tmp/r12-mbp-tmp/r12-xdg-empty`, `PYTHONNOUSERSITE=1`,
`TMPDIR=/private/tmp/r12-mbp-tmp`), from the clone root:

1. `python3.13 -B scripts/b6_r12_session_fixture.py --out /private/tmp/r12-mbp-tmp/r12-r3-mbp-seed-1 --synthetic-models --volume prerequisite --seed-probe`
   (exit code written to the seed root's `generator-parent-exit.txt`; both
   sessions start only if it is 0);
2. per pack, concurrently:
   `python3.13 -B scripts/b6_r12_profile_session.py --out /private/tmp/r12-mbp-tmp/r12-r3-full-<pack>-mbp-1 --prior-chain-root /private/tmp/r12-mbp-tmp/r12-r3-mbp-seed-1 --pack <pack> --scenario plain --volume full`,
   and only after its actual exit 0 (`&&`)
   `python3.13 -B scripts/b6_r12_full_supervise.py --cohort-root /private/tmp/r12-mbp-tmp/r12-r3-full-<pack>-mbp-1 --generation-only`.

Receipts beside the roots in `/private/tmp/r12-mbp-tmp/`: `launcher.events`,
`<root>.events` (each step's pid, native start/end, actual exit), `<root>.log`.
Each root's `segments.json` and `full-reader-supervision.json` remain the
authoritative phase records. An interrupted phase or inflight journal makes
that root ineligible; it is never resumed, and a fresh root is used.

## Tests (Air, before launch)

Sanitized environment, `TMPDIR=/Volumes/JW-EXT/tmp/r12-alpha-gamma`, `nice -n 10`:

- `FullPackExpectationTests SchedulerBoundaryTests FullProductionSessionTests`:
  **13 tests, 11 passed, 2 skips** (the full-session tests need a completed
  root), 0.350 s.
- Whole module `tests.test_b6_r12_session_fixture`: **63 tests, 49 passed,
  14 integration skips, 51.177 s, exit 0** (was 60/46/14 at `be02cd695`).
  `git diff --check` clean.
- Launcher dry run with a stub interpreter: seed receipt written, supervisor
  started only after the first step's exit 0, per-step pid/exit recorded.

No native MLX/Metal, weights, network or real data is used by any of these.

## Live status

(Appended after launch: pids, start times and first-step state.)

## GAMMA root -1 failure and relaunch

Written 2026-11-12 23:30 PST (`/bin/date`), **before any collection in the
replacement GAMMA root**. ALPHA root `r12-r3-full-alpha-mbp-1` is untouched
and still running from clone `/Users/edr/code/jw-wt/r12-mbp` at `68be80a79`.

### What failed

`r12-r3-full-gamma-mbp-1`: seed exit 0 (shared with ALPHA); first step
(profile session, smoke driver) exit 0 at 23:11:02; supervisor step
"smoke desk" exit **1** at 23:12:51 with `b6_r12_orchestrate.loop_fixture`
`RuntimeError: development tick bound reached` after `loop 1..299 NEXT`.

The tick bound is **not** the cause and raising it would not help. The
pinned loop's own records show it is idle, not progressing:

- `loop/state.json`: `state NEXT`, `session null`, pack `gamma`
  `status held`, `hold_reason smoke_hold:roster.no_science_bundles,
  stage_failed:gamma-science-01-decode-contrast-blocks-01-05,
  stage_failed:gamma-science-03-prefill-p2048-contrast-blocks-01-05,
  structure.missing_stage_bundles`; no attempts.
- The original smoke desk held the only open pack (`Loop._hold_packs`, first
  occurrence → `NEXT`); `Loop._next` then gets `queue.Idle` every tick and
  waits for an operator resume. No terminal state can follow, so
  `loop_fixture`'s 300-tick guard is the correct way this scheduler reports
  "no progress".
- The smoke night itself: `verdict GO`, chain exit 0, but
  `night/stage_yield.jsonl` has both GAMMA science stages `rc 1`, `ZERO`
  (0/20 present); the two reference stages ran (`LOW`, 1/3, as reduced smoke
  does). Each science stage log
  (`operator-logs/04-…decode…log`, `05-…prefill…log`) ends:
  `analysis_prospective_identity_mismatch: manifest.frozen_semantics_sha256
  does not match the frozen projection; analysis_prospective_identity_mismatch:
  manifest.manifest_id does not match canonical content`, collection verdict
  `invalid`, i.e. the pinned `run_campaign.resolve_prospective_analysis_manifest_v3`
  refused the stage before any member ran.

### Root cause (generator input defect, not session shape)

GAMMA's contrast campaign is the only B6 pack with a prospective
`analysis_manifest_v3.json`. That manifest quotes raw config digests
(`config_sha256`, `manifest_sha256`, …) **and** binds two canonical content
identities over them: `frozen_semantics_sha256`
(`analysis_semantics_sha256_v1`) and `manifest_id` (`calculate_manifest_id`).
`b6_r12_runtime.make_synthetic_inputs` rebinds model/tokenizer identities
and then propagates raw-file digests through the input graph, so the overlaid
manifest gets new `config_sha256` values but keeps the pinned semantic
identities. The pinned resolver recomputes both and refuses. The same function
already recomputes the analogous canonical digest for suite manifests; the
analysis manifest case was simply missing.

This is independent of session order. It is not the stated "floor
unavailable" risk (that concerns reader-side `attach_gamma` keys, after
collection) and GAMMA r1 alone is a valid loop shape: the pinned loop
selected `r1-gamma`, prechecked it and ran its smoke. Every R12 root built by
the old runtime would refuse every GAMMA science stage the same way, including
the nine-session cohorts, which never reached GAMMA (all GAMMA rows in the R12
seat report are still "pending"). ALPHA and BETA science stages never consult
this manifest, which is why they passed.

Reproduced off-MBP before the fix: new test
`BootstrapTests.test_synthetic_inputs_keep_prospective_analysis_identity`
(make-inputs, then the pinned resolver over all four contrast stage dirs)
**failed, 12.2 s**, with exactly the root -1 refusal text.

### Fix — DECLARED PROFILE DIFFERENCE for MBP GAMMA

**`scripts/b6_r12_runtime.py` changed — a file BETA root 23 hashes.** No other
root-23-hashed file (courier profile, orchestrate, session fixture, verify,
chain fixture, single pack, reduced set) changed. Runtime SHA-256 is now
`a08bc6ea3984a1f60ab92d92ca8662e2d0622d2c1e0b4671d019ee12110f0ad1`
(root 23 / ALPHA root -1 / GAMMA root -1: `14ec9e7dfd31…`). Root 23 is
unaffected: its runtime copy lives in its own root and the seat worktree.

`make_synthetic_inputs` (`scripts/b6_r12_runtime.py:1228-1263`, called inside
the digest-propagation loop at `:1283`): for each pinned
`joulewise.analysis_manifest.v3.prospective` config whose pinned
`frozen_semantics_sha256` and `manifest_id` were self-consistent, recompute
both with the pinned functions after each propagation pass (semantics first,
then the id over it) and replace exactly those two field values; the raw digest
of the rebound manifest then propagates like any other. It refuses if either
identity is quoted by any other config or is not a unique field. No pinned
file, judgment, threshold, roster or registry is edited; a pinned manifest
that was already inconsistent would not be "repaired".

Scope of the input difference, measured (same root path, old vs new runtime,
deterministic: new vs new again differs in 0 files): 403 overlays either way,
**8 overlay files differ**: the contrast `analysis_manifest_v3.json`,
`plan_tree.json`, `plan_tree.sha256`; `configs/b6/registration/identity_pins.json`
and `sizing_b5.json`; `configs/campaigns/v5_claim_25g83/{identity_pins,
sealed_inventory,sizing_b5}.json`. These differ only by the propagated digests
of the GAMMA manifest. Consequence: MBP GAMMA root -2 has different runtime
bytes and these 8 input files relative to ALPHA root -1 and BETA root 23; no
byte-equality claim across them is made (none was made before either). Any
future R12 root that runs GAMMA (including the closed nine-session set) needs
this runtime.

### Tests (Air, sanitized env, `TMPDIR=/Volumes/JW-EXT/tmp/r12-ag-fix`, `nice -n 10`)

- New `test_synthetic_inputs_keep_prospective_analysis_identity`: before fix
  1 failure (12.2 s, root -1's refusal); after fix it and the existing
  `test_synthetic_inputs_keep_canonical_suite_bindings`: **2 passed, 24.7 s**.
- `BootstrapTests FullPackExpectationTests SchedulerBoundaryTests
  FullProductionSessionTests`: **35 tests, 33 passed, 2 skips** (full-session
  tests need a completed root), 46.1 s, exit 0. `git diff --check` clean.

### Relaunch plan (declared before launch)

The ALPHA supervisor re-invokes `scripts/b6_r12_profile_session.py` (and its
imports) from `/Users/edr/code/jw-wt/r12-mbp` and checks hashes against its
root, so that clone stays at `68be80a79`. GAMMA uses a **second clone**
`/Users/edr/code/jw-wt/r12-mbp-2` at this commit. New root
`/private/tmp/r12-mbp-tmp/r12-r3-full-gamma-mbp-2`, same seed
`r12-r3-mbp-seed-1` (read-only, hash-checked), same sanitized environment and
step order as the launcher: profile session (`--pack gamma --scenario plain
--volume full`), then, only after its actual exit 0,
`b6_r12_full_supervise.py --generation-only`. Receipts:
`/private/tmp/r12-mbp-tmp/r12-r3-full-gamma-mbp-2.events` / `.log`.
Root -1 stays in place, **ineligible** (failed smoke desk, cause above), and
is never resumed. Predictions for GAMMA are unchanged from the table above;
new prediction for the smoke desk: both GAMMA science stages run (no
`analysis_prospective_identity_mismatch`), the pack is not smoke-held, and the
supervisor proceeds to "ordinary full driver".
