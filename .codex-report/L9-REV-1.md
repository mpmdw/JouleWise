# L9-REV-1: executing review of the L9-2 shared physics cache

Reviewer: L9-REV-1 (Claude Code cloud session, 2026-10-27). Independent of the author. I ran the code; I did not
edit the lane.

- Target: `lane/2026-10-27-l9-2`, `0576a734d` (BASE_HEAD) to `c20fa72`. Two runtime changes:
  - the cache, `b5df45a`, reviewed at `60473be` (§1-§4);
  - the tripwire, `96f1f1f`, reviewed as the delta `60473be..c20fa72` (§5).

  The other delta commits change only `.codex-report/`.
- Context read: `ED-RULING.md` and `BRIEF.md` (`docs/process_traces/2026-10-27-l9-restart/`, origin/main), and the
  lane's `.codex-report/L9-2.md`.
- Seat: 4 vCPU Linux VM, `/usr/bin/python3.13` (3.13.17), numpy 2.5.3. Every run used
  `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp` (short modules also used
  `JW_B5_S10_REAL_PROGRAMS=1` and a fresh TMPDIR each). Synthetic data only: members of the committed S10 ALPHA
  archive `tests/fixtures/b5_analysis/s10/alpha/archive.tar.xz`, extracted to `/tmp/jwtmp/alpha`.
- Setup deviations: no `/bin/zsh` and no `/opt/homebrew/bin/python3.13`. This session's permission policy refused
  the `/opt/homebrew` symlink (it writes outside the repo). No test I ran needs either path. zsh was not built.
- Scripts and raw outputs: `.codex-report/l9-rev-1/` on this branch. Ad hoc names below (A, B) are
  `runs_claim/neg8-window-end-r1` and `runs_claim/neg8-window-midpoint`. Both bind calibration evidence
  `a638eed8…` (raw `951ed3fa…`). That evidence is shared by 107 of the 109 `instrument_evidence.json` files under ALPHA
  `runs_claim/` and by all 18 `runs_bound` references. The other two are `instrument_validation/s10-alpha-bracket-post` (`75def1c8…`) and
  `instrument_validation/other-systematic` (`9d612ca1…`).

## 1. Scope (check 1): PASS

```
git diff --stat 0576a734d..60473be
 .codex-report/L9-2.md, .codex-report/l9-2/* (7 files)
 joulewise/b5_analysis/dry_run.py               |   6 +-
 joulewise/cli.py                               |  12 +-
 joulewise/whole_window.py                      |  50 +++++-
 tests/b5_analysis/test_shared_physics_cache.py | 188 ++++
```

No governed file changed. `powermetrics_fiducial.py`, `uncertainty_evidence.py`, `adapters/powermetrics.py` and
`reduce.py` are absent from the diff. Every path is in the permitted set. `cli.py` and `whole_window.py` are outside
the BRIEF's WRITE_SCOPE, and the BRIEF's A3 requires `whole_window.py` to be byte-identical. ED-RULING item 1
(amended 2026-10-27) explicitly authorises the wiring in those two files, so I do not count this as a scope breach.
The seat report does not yet record that (MINOR-1).

## 2. The author's test, then attempts to break it (check 2)

`python3.13 -m unittest -v tests.b5_analysis.test_shared_physics_cache`: **7/7 OK, 148.8 s.**

Break tests (`.codex-report/l9-rev-1/breakit.py`, `breakit.json`; `pool.py`, `pool.json`; `poison.py`,
`poison.json`):

| # | Attack | Result |
|---|---|---|
| T1 | Cross-member reuse in one run: steps 1+2 on A, then steps 1+2 on B, one shared dict | 1 refit for 4 program calls. Cache holds exactly one key, the SHA-256 of the evidence bytes (`a638eed8…`). A and B outputs are byte-identical to uncached (§3). |
| T2 | Wall deadline forced (powermetrics_fiducial clock +1000 s per read) only in step 2 (`reduce`) | Uncached: exit 0, `not_estimable`, `5ab0c4ba…`. Warm cache: exit 0, `bounded`, `3a867f60…` (identical to normal). See MINOR-2. |
| T3 | Deadline forced in step 1, then a normal step 1, same run | Forced: exit 2, cache `{}`. Normal: exit 0, cache gains the key. A failed or deadline-hit fit is never stored. |
| T4 | `strict_validate_bundles([A,B], workers=2)` (spawn pool) inside the run context | Workers do not inherit the contextvar. Each refits with its own per-worker dict. The shared dict stays empty, so no in-process fallback ran. Results equal serial results with and without the context. Correct, with no sharing on that path. No production caller passes `workers>1` (`whole_window.py:413`, `:7658` use `workers=1`). The first T4 attempt inside `breakit.py` is void because the script lacked a `__main__` guard and spawn children re-executed it. `pool.py` is the valid run. |
| T5 | Harvest path inside a run context: `harvest.strict_problems(A, own_cache)` | `own_cache` gets the key and the shared dict stays empty. The explicit cache wins (`cli.py:497-507`) and harvest's reduce passes its own cache explicitly (`b5/harvest.py:2489`). The dry-run imports of `joulewise.b5.harvest` (`sources_replay.py:198`, `context.py:109,121`) call no reducer or validator. |
| T6 | Plain `threading.Thread` and `ThreadPoolExecutor` inside the context | Both see `None`, so they fall back to per-call dicts, the old behaviour. No dry-run code path uses threads around these sites. |
| T7 | Three driver runs in one process, step 0 writes a poison key, step 1 raises (`RuntimeError`, `AnalysisRefusal`) | Every run starts with a new empty dict (`{}`, `{}`, `{}`, distinct ids). After every run, `shared_physics_cache()` is `None`. Nothing is reused across driver runs, including after an exception. |
| T8 | Right key, wrong value (`poison.py`) | `0.0`: accepted with no refit, output unchanged here. `5.0`: step 1 exit 2, but step 2 exit 0 with a different reduction `f8bd3dba…`. `-1.0`: step 1 exit 2, step 2 `not_estimable`. NIT-1. |

Different calibration bytes: the key is the reducer's `artifact_sha256` of the evidence document. That digest is
checked against the bytes and the manifest (`reduce.py:1284,1298`), and the raw and events hashes listed in the
evidence are checked (`reduce.py:1477-1486`), all before the cache lookup (`reduce.py:1526`). So a hit requires
identical evidence bytes, and through them identical raw and events bytes, clock anchor, protocol id and declared
pulses. The author's `test_cache_hit_requires_the_content_hash_key` and
`test_cached_bound_never_admits_changed_capture_bytes` pass. The stored value is
`max(metadata b_fiducial, fresh)`, and metadata `b_fiducial` must match the evidence value within 1e-12
(`reduce.py:1400`). This is the governed reducer's existing contract, unchanged here.

Non-dry-run callers: outside a `shared_instrument_calibration_physics_cache` block, `shared_physics_cache()` is
`None`. Every changed site then behaves as at BASE_HEAD. §3 shows this as byte-identical outputs. The six short
modules pass at the lane head (§4). Precedence in `_strict_problems` is explicit cache, then V2 session cache,
then the shared cache, as claimed. `test_authentication_io` passes.

## 3. Byte-identity (check 3)

`digests.py` runs `validate-bundle --strict` and `reduce` uncached on A, B and C = `neg8-window-start-r1`
(unreadable summary, a refusal case), once in a BASE_HEAD worktree and once at the lane head.
`breakit.py` T1 runs A and B with one shared cache.

| member | output | BASE_HEAD uncached | head uncached | head shared cache |
|---|---|---|---|---|
| A | validate exit / stdout | 0 / `16502e55…` | 0 / `16502e55…` | 0 / `16502e55…` |
| A | reduced JSON | `3a867f60…` | `3a867f60…` | `3a867f60…` |
| B | validate exit / stdout | 0 / `1781a2d1…` | 0 / `1781a2d1…` | 0 / `1781a2d1…` |
| B | reduced JSON | `78e31230…` | `78e31230…` | `78e31230…` (no refit) |
| C | validate / reduce exit | 2 / 2, stdout `4e53e318…` | 2 / 2, stdout `4e53e318…` | — |

`reduce` stdout differs between columns only because it prints the `--output` path. With the same path, the
base and head stdout are byte-identical (`f729837a…` both). The author's own byte-identity test passes
(uncached, cold and warm all identical). **Byte-identity holds whenever no wall deadline fires.** Under a firing,
the outputs differ by design (MINOR-2).

## 4. Six short modules at the lane head (`60473be`)

`.codex-report/l9-rev-1/short.sh`, one process per module, sequential:

| module | tests | result | wall s |
|---|---|---|---|
| tests.test_authentication_io | 22 | OK | 3.3 |
| tests.test_docs_freshness | 31 | OK | 1.1 |
| tests.b5_analysis.test_sensitivity_guard | 12 | OK | 93.0 |
| tests.b5_analysis.test_s10_chain_defects | 34 | OK | 10.1 |
| tests.test_r4_acceptance_oracle | 10 | OK | 5.8 |
| tests.b5_analysis.test_mint_kept_units | 87 | OK (1 skip: the declared `test_s10_sealed_floor_packs_bootstrap_their_producer_contracts`, as at `d850ff7`) | 901.4 |

The seat report's module table is still at `d850ff7`, before the runtime change. This table covers the change.

## 5. Tripwire delta `60473be..c20fa72` (check 4): PASS for step 2

`git diff --stat 60473be..c20fa72` touches these paths:

- `joulewise/b5_analysis/dry_run.py` (+37/-6);
- `tests/b5_analysis/test_deadline_tripwire.py` (new);
- `tests/b5_analysis/test_dry_run.py` (the step-2 double now echoes the stored refit-dependent keys);
- `configs/analysis/b5/dry_run_refusal_classes.json` (+1 tooling code; NIT-4);
- `.codex-report/`.

No governed file changed. `step_2` now compares four refit-dependent summary keys with the kept bundle's stored
summary. On a difference it refuses with tooling code `rereduction_calibration_dependent_fields_differ` and
unlinks the unregistered output.

Executed at `c20fa72`:

- `python3.13 -m unittest -v tests.b5_analysis.test_deadline_tripwire tests.b5_analysis.test_shared_physics_cache`:
  **13/13 OK, 256.9 s** (`l9-rev-1/lane_tests_c20fa72.txt`). The six tripwire tests cover four things:
  - a step-1 firing exits 2 with a tooling class;
  - a step-2 firing gives a tooling refusal, with only the earlier output registered and nothing on disk past it;
  - a mutation proof: with the check stubbed out, the firing passes silently;
  - an unforced step 2 has records and output bytes identical to a verbatim copy of the BASE_HEAD `step_2`.

  The driver stopping at a refused step 2 is shown with stub steps: every later step stays `not_run`.
- **False-refusal sweep** (`l9-rev-1/sweep.py`, `sweep.json`): an unforced `reduce` plus
  `require_rereduction_matches_stored` on every succeeded ALPHA claim member, with the shared cache on. 104
  admitted, 0 refused, 2 skipped (summary not `succeeded`), 0 reduce failures. **1 refit for 104 members.**
- **Tripwire × cache** (`l9-rev-1/interplay.py`, `interplay.json`), run through the real `step_2` and `StepRunner`
  with the lane test's harness:
  - Cold run cache, firing on the first reduce: `tooling_refusal` /
    `rereduction_calibration_dependent_fields_differ`. No output is registered and the cache stays empty.
  - Warm cache (as after step 1), firing forced on the second reduce: `ok`. Records and outputs are byte-identical
    to an unforced run, because step 2 does not refit and the forced clock is never read.

  So on the real driver path, the cache already prevents step-2 firings for every calibration step 1 verified. The
  tripwire is the backstop for a refit the cache misses (cold or out-of-process paths).

Other refit paths. The seat report lists three other refit sites (`L9-2.md:257-263`). It misses the separate,
**uncached** refit in `calibration_bracketing` → `powermetrics_fiducial.verify_stored_evidence_physics` →
`rederive_detection_from_artifacts` (`calibration_bracketing.py:1765`). That path is reached from
`b5_analysis/bracket.py:257` and from `whole_window.py:1207,6135`; see MINOR-4. For the `bracket.py` consumer,
every non-pass raises `window_bracket_not_passed`, and the shipped class table lists it under `tooling_refusal`
(executed lookup). That consumer fails closed. I did not trace the two `whole_window` consumers to a step outcome.

## 6. Lead's follow-up questions (message of 2026-10-27 20:01 UTC)

Repository unshallowed first: `git fetch --unshallow`. Probes ran on a worktree at `c20fa72`.

### (a) Can a legitimate run hit the tripwire spuriously? No, as far as can be checked here.

- **Who wrote the stored summary.** The harvest never writes `summary_metrics.json`. The measurement run wrote it,
  and the harvest reads it (`b5/harvest.py:2460`). At both block-5 harvest pins, `224a264c5` and `b039c0257`, the
  harvest re-reduces each member with its pinned code and records `identical_to_stored = raw == summary_raw`, a
  byte comparison (`harvest.py:2404` at `224a264c5`, `:2493` at `b039c0257`). A mismatch flags
  `member.reduction_mismatch`. `registration_block5.md:3684-3692` removes such a member from every cell. So every
  kept bundle's stored summary was byte-reproduced by the reducer at its harvest pin.
- **Reducer drift from the pins to the lane: none.** I ran a real strict reduction and listed every `joulewise`
  module it loads (31 modules, including the lazily imported `powermetrics_fiducial`).
  `git diff --stat 224a264c5 c20fa72 -- <those 31 files>` is empty, and so is the same diff from `b039c0257`.
- **Serialization cannot trip it.** The tripwire compares parsed JSON values per key
  (`require_rereduction_matches_stored`), not bytes. A whitespace or key-order difference between harvest and
  dry-run serialization cannot fire it.
- **Executed:** the false-refusal sweep (§5) admits 104/104 succeeded ALPHA members.
- **Residual risk.** Host numerics are the one remaining source: a different numpy, Python or libm build on the
  Mac between harvest and dry run could change a float. That would be a fail-closed tooling refusal, not a wrong
  number. Check `python3.13 -c 'import numpy,sys;print(sys.version,numpy.__version__)'` against the harvest host
  record before the dry run.

### (b) Are the other refit sites refusal-terminal?

There is one refit function, `powermetrics_fiducial.rederive_detection_from_artifacts`. It has two callers:
`reduce.py:1547` (this goes through the shared cache) and
`powermetrics_fiducial.verify_stored_evidence_physics` (not cached; reached from `calibration_bracketing.py:1765`).
Command: `grep -rn "rederive_detection_from_artifacts(\|verify_stored_evidence_physics(" joulewise --include=*.py`.
Each site's behaviour under a forced firing (pf clock +1000 s per read):

| site | firing with no cache | firing with a warm run cache | terminal? |
|---|---|---|---|
| step 1 `validate-bundle --strict` | exit 2, `kept_bundle_strict_validation_failed` (tooling) | no refit | **yes, executed** |
| step 2 `reduce` | tripwire: tooling refusal | no refit, outputs identical | **yes, executed** (§5) |
| `b5_analysis/bracket.py:257` → `calibration_bracketing` | any non-pass gives `window_bracket_not_passed` (tooling) | not cached (always refits) | yes, by reading plus a class-table lookup |
| `whole_window.py:1207`, `:6127` → `calibration_bracketing` | — | — | **not reached on the dry-run path.** `dry_run.py:1006-1008` always passes a consumption session and `archive_context`, so the bracket comes from the archived assessment (`whole_window.py:1195-1202`). The `:6127` pointwise path is the no-session fallback. |
| consumption session (`whole_window.py:1326-1345`) | member reason, `_fail_global`, session not ready, `whole_window_verdict_provenance_invalid` (`:7534-7560`), then the step-5 mint raises `MintError("<label>: authenticated whole-window consumption refused: …")` | no refit | stops, by reading only. **The record may show `unclassified_refusal`**, because `refusal_token` takes the text before the first `:`, and that is a label, not a classified code. |
| NEG-8 energy re-derivation (`_reference_energy_evidence_detail`, `:4617`) | **executed:** returns `precheck_ineligible`. The control returns the energies (`neg8_probe.json`). | executed: unchanged energies | see the next row |
| NEG-8 replay (`b5_analysis/sources_replay.py:246` → `_derived_neg8_decision`) | **executed:** the replay's `strict_invalid` callback on reference `runs_bound/neg8-refcorpus-r01` returns invalid (control: valid; `ref_strict_probe.json`). The replay passes no `stored_strict_losses`, so every reference counts as listed (`whole_window.py:5600-5612`): **the firing turns a reference into a `strict_invalid` LOSS, not a refusal.** An energy `precheck_ineligible` returns a problem code (`provenance`), which is a refusal. | executed: valid, no refit | **only through a later comparison, by reading.** The derived bracket must still match the archived one in `_neg8_reproduces` (`whole_window.py:245-252`), which compares every claim-family field except the bound-dependent ones, including `abs_delta_j` over the survivors. A changed loss set almost surely changes them, giving `whole_window_verdict_conflict` (tooling). If a loss breaks endpoint replication, the code is `sources_replay_screen_not_passed` or `provenance`. **Neither of those is in the class table, so they print `unclassified_refusal`.** |

So the author's three sites do end in a stop before any output. But two of them stop only as **unclassified**
refusals, and the NEG-8 replay's terminality rests on the endpoint comparison, not on the site itself. With the
shared cache, none of these later sites refits a calibration that step 1 verified. In ALPHA that is every one:
107 of 109 claim-side evidence files and all 18 references share `a638eed8…`. A firing there becomes impossible
after step 1. Whether that also holds for block 5's real references is a property of the archives, and I could not
check it here.

**Feasible fix, all in non-governed code** (`observer_probe.py`, `observer_probe.json`). The return value of
`rederive_detection_from_artifacts` carries `projection_budget_trigger`. It reads `null` on the control and
`"wall_deadline"` on the forced call. Both callers look the function up through the module, so a wrapper scoped to
one driver run can see every firing in the process. The wrapper sits in `dry_run.run`, alongside the cache
context, and must not mutate anything. If it records any firing, the step that saw it ends with one tooling code
(for example `calibration_wall_deadline_fired`). That would replace the four-key inference with a direct signal,
and it would cover the bracket, session and NEG-8 paths.

The consumption-session site could not be executed: its only executable harness (`chain_fixture()`) restores the
roughly 8 GB S10 chain and runs for hours. I stopped it after 25 min and deleted its temp tree.

## FINDINGS

### BLOCKER
None.

### MAJOR
None.

### MINOR

- **MINOR-1: the seat report is still partly stale.** At `c20fa72` it records the scope basis
  (`.codex-report/L9-2.md:120-122`). But `:98` still says "No `joulewise/` or `tests/` change yet", `:287` still
  calls the cache "Not in WRITE_SCOPE", and the module table (`:78`) is still at `d850ff7`, before both runtime
  commits. Command: `git show origin/lane/2026-10-27-l9-2:.codex-report/L9-2.md | grep -n "change yet\|Not in WRITE_SCOPE\|^Source head"`.
  §4 here gives the six modules at `60473be` (cache, before the tripwire).
- **MINOR-2: "byte-identical cached vs uncached" holds only when no deadline fires. The claim should say so.**
  T2 (`breakit.py`): a firing forced in step 2 gives `not_estimable`/`5ab0c4ba…` uncached, but
  `bounded`/`3a867f60…` (normal) with a warm cache, because step 2 does not refit a calibration step 1 verified
  (`whole_window.py:7075-7107`, `cli.py:1949-1955`). The tripwire (`dry_run.py:685-726` at `c20fa72`) now turns
  the uncached case into a tooling refusal (§5). The remaining issue is the wording of the claim: under the
  cache, outputs are identical to an uncached run with no firing, not to an uncached run in general.
- **MINOR-3: three of the five wired sites have no test under the shared cache.** The cache test exercises
  `cli._strict_problems`, `_cmd_reduce`, `strict_validate_bundles` and the driver scope. The
  `AuthenticatedConsumptionSession` site (`whole_window.py:1293`), `_reference_energy_evidence_detail`
  (`:4661-4665`) and `_current_core_rederivation_reasons` (`:6168`) are covered only by reading. They hand the
  dict to the same governed reducer, so the risk is low. Command:
  `grep -n "AuthenticatedConsumption\|_reference_energy\|_current_core" tests/b5_analysis/test_shared_physics_cache.py`
  returns no match.
- **MINOR-4: the fail-closed evidence omits the uncached bracket refit path** (`calibration_bracketing.py:1765` →
  `powermetrics_fiducial.verify_stored_evidence_physics`). Narrowed by §6(b): on the dry-run path only
  `b5_analysis/bracket.py:257` reaches it, and that caller fails closed with the tooling code
  `window_bracket_not_passed`. The `whole_window.py:1207,6127` callers are bypassed because the driver always
  supplies a session and `archive_context`. The seat report's site list (`L9-2.md:257-263`) should add this path.
- **MINOR-5: two later refit sites stop only as `unclassified_refusal`, and the NEG-8 replay turns a firing into a
  lost reference before anything refuses** (§6(b)). Executed: under a forced firing with no cache, the replay's
  `strict_invalid` callback marks a real reference invalid (`ref_strict_probe.json`). The energy re-derivation
  returns `precheck_ineligible` (`neg8_probe.json`). Terminality then rests on `_neg8_reproduces`
  (`whole_window.py:245`), by reading. The codes it can end in, `sources_replay_screen_not_passed` and
  `provenance`, and the step-5 mint's `<label>: authenticated whole-window consumption refused`, are not in the
  class table. A blind operator would see "unclassified refusal at step N" and could not tell it was a deadline
  firing. With the shared cache this cannot happen for any calibration step 1 verified. Fix (non-governed,
  feasibility executed in `observer_probe.json`): a driver-run observer on `rederive_detection_from_artifacts`'s
  `projection_budget_trigger` that turns any firing into one tooling code.

### NIT

- **NIT-1: the cache trusts any finite, non-negative value under the right key** (`reduce.py:1526-1535`). T8: the
  value `5.0` makes step 2 exit 0 with a different reduction. Only in-process code can write the dict, and the
  governed reducer is the only production writer. Harvest has the same trust model. Consider not exporting the
  live dict beyond the call sites.
- **NIT-2: the spawn-pool and thread paths get no sharing** (T4, T6). That is correct and matches the old
  behaviour. A `workers>1` caller on the dry-run path would silently lose the speedup. One comment at
  `whole_window.py:7184` would record this.
- **NIT-3: `_cmd_reduce` takes the shared cache but never the V2 session cache** (`cli.py:1949-1955`), while
  `_strict_problems` prefers the session cache (`cli.py:497-507`). The precedence is inconsistent but harmless.
- **NIT-4: the tripwire edits `configs/analysis/b5/dry_run_refusal_classes.json`** (+1 code). That file is outside
  the paths named for this change. The edit is disclosed (`L9-2.md:122`), and no tracked file pins the table's
  SHA-256 (searched for `45bfef86…` and `620a5960…`). The lead should accept it explicitly.
- **NIT-5: in the new `step_2`, a non-zero `reduce` exit that still wrote its output leaves that file on disk
  unregistered** (`dry_run.py` `step_2` at `c20fa72`). At BASE_HEAD, `invoke` registered it before the failure
  record. This is a failure path and the driver stops there, so it only affects the custody census.

## COULD NOT CHECK

- The six short modules at `c20fa72`: run at `60473be` only (§4). The delta changes `dry_run.py` and
  `test_dry_run.py`.
- Any full driver run (`test_dry_run`, full or reduced size) with the cache and tripwire on. It was not run, per
  instruction. The driver was checked with stubbed steps (author tests, T7), with the real `step_2`/`StepRunner`
  (§5), and with the step-1/step-2 programs directly.
- The consumption-session site under a forced firing (§6(b)): its harness is the multi-hour, ~8 GB S10 chain. It
  was stopped after 25 min.
- Whether block 5's real references share the kept members' calibration evidence. That needs the archives.
- The NEG-8 replay end to end under a forced firing. Only the site and the callback were executed; the
  `_neg8_reproduces` backstop is by reading.
- Real wall-time savings: only refit counts were measured (1 refit for 104 members).
- macOS, zsh, and the `/opt/homebrew` interpreter path (setup refused; see the header).

VERDICT at `c20fa72` (superseded by §7): ACCEPT_WITH_FIXES

- BLOCKER: none
- MAJOR: none
- MINOR-1 `.codex-report/L9-2.md:98,287,78`: seat report still says no code change, "Not in WRITE_SCOPE", and the module table predates both runtime commits
- MINOR-2 `joulewise/whole_window.py:7075`, `joulewise/cli.py:1949`: byte-identity holds only when no deadline fires; qualify the claim (the tripwire now refuses the uncached step-2 case)
- MINOR-3 `joulewise/whole_window.py:1293,4661,6168`: no executed test of these sites under the shared cache
- MINOR-4 `joulewise/calibration_bracketing.py:1765`: uncached bracket refit path missing from the seat report's site list; on the dry-run path only `bracket.py` reaches it, and it fails closed (tooling)
- MINOR-5 `joulewise/b5_analysis/sources_replay.py:246`, `joulewise/whole_window.py:5600`: an uncached firing becomes a lost NEG-8 reference, with terminality resting on `_neg8_reproduces`; session and replay stops surface as `unclassified_refusal`. Fix: a run-scoped observer on `projection_budget_trigger`
- NIT-1 `joulewise/reduce.py:1526`: cached value under the right key is trusted (existing reducer contract)
- NIT-2 `joulewise/whole_window.py:7184`: spawn pool and threads get no sharing (correct, but uncommented)
- NIT-3 `joulewise/cli.py:1949`: `reduce` ignores the V2 session cache while strict validation prefers it
- NIT-4 `configs/analysis/b5/dry_run_refusal_classes.json`: edit outside the named paths; disclosed, unpinned
- NIT-5 `joulewise/b5_analysis/dry_run.py` `step_2`: non-zero exit with output leaves an unregistered file


## 7. Addendum: fix round `5107713f5..f059286bc` (report at `35e0519e2`)

This reviews the fix round as one delta, `c20fa72..f059286bc`, with MINOR-5 as the focus. Executed on a worktree
at `f059286bc`.

**Scope.** No governed file changed: `git diff --stat c20fa72 origin/lane/2026-10-27-l9-2` on
`powermetrics_fiducial.py`, `uncertainty_evidence.py`, `adapters/powermetrics.py` and `reduce.py` is empty. The
code paths changed are:

- `b5_analysis/deadline_observer.py` (new), `b5_analysis/dry_run.py`, `b5_analysis/bracket.py`;
- a comment in `whole_window.py`;
- three new tooling codes in `dry_run_refusal_classes.json`;
- tests.

The seat report no longer carries the stale lines from MINOR-1.

**Mechanism.** `observe_wall_deadline()` takes a free `sys.monitoring` tool id and sets a local PY_RETURN event on
`powermetrics_fiducial.detect_pulses.__code__`. It counts returned detections whose `projection_budget_trigger` is
`"wall_deadline"`. It replaces no callable. `dry_run.run` opens it next to the cache. For each step it compares
the count before and after the step function. That covers ok, `AnalysisRefusal` and generic-exception exits: the
generic path no longer returns early (`dry_run.py:1240-1263`). On any change, the step's records become one record
with `calibration_wall_deadline_fired`, and every later step is `not_run`. If no tool id is free, every step
refuses with `calibration_deadline_observer_unavailable`. Both codes are tooling refusals in the class table.
`detect_pulses` is the only constructor of the wall budget (`powermetrics_fiducial.py:978`). It catches the
budget exception internally and returns the trigger (`:1011`), so every in-process firing reaches the observer.

Executed:

- **Lane tests:** `python3.13 -m unittest -v tests.b5_analysis.test_deadline_observer tests.b5_analysis.test_deadline_tripwire tests.b5_analysis.test_shared_physics_cache`:
  **28/28 OK, 353.2 s** (`l9-rev-1/fix_tests_f059286bc.txt`). The observer tests force a firing at each site:
  step-2 reduce, the bracket refit, the NEG-8 replay callback and the NEG-8 energy re-derivation. Each is counted.
  The driver tests show the single code and `not_run` afterwards, unforced records equal to a run without the
  observer, a counterfactual where an ok step passes without the observer, an unavailable observer, and the mint
  code mapping.
- **Break probes** (`l9-rev-1/observer_break.py`, `observer_break.json`):
  - **P1 unforced byte-identity.** `validate-bundle --strict` and `reduce` on A and B, plain and then under cache
    plus observer as `dry_run.run` opens them: identical exits, stdout and reduction bytes (`3a867f60…`,
    `78e31230…`), 0 firings.
  - **P2 threads.** A forced firing on a `threading.Thread` and on a `ThreadPoolExecutor` worker inside the
    observed scope is counted (2 of 2). `sys.monitoring` is interpreter-wide.
  - **P4 a competing tool.** Another tool with a PY_RETURN callback on the same code object that returns
    `DISABLE` does not blind the observer (1 of 1 counted). The observer took tool id 0 (see NIT-6).
  - **P3 a spawned worker (blind spot).** I forced the clock in every process via `forcedsite/sitecustomize.py`
    and called `strict_validate_bundles([A,B], workers=2)` inside the observed scope. The workers return one
    strict problem each, and the observer counts **0**. No dry-run caller passes `workers>1`
    (`whole_window.py:413,7658`). The only other process pool, `b5/harvest.py:2552`, is not on the dry-run path:
    the driver uses only harvest's roster and source functions, which do no refits. See NIT-7.
- **Six short modules at `f059286bc`:** all OK (`l9-rev-1/short_summary_f059286bc.txt`):
  - `test_authentication_io` 2.3 s;
  - `test_docs_freshness` 1.1 s;
  - `test_sensitivity_guard` 89.5 s;
  - `test_s10_chain_defects` 10.3 s;
  - `test_r4_acceptance_oracle` 5.5 s;
  - `test_mint_kept_units` 897.8 s (1 declared skip).

**Dispositions checked.**

| finding | status at `f059286bc` |
|---|---|
| MINOR-1 stale seat report | **closed.** The rewrite at `35e0519e2` drops the stale lines and states the ruling basis. |
| MINOR-2 byte-identity wording | **closed.** "Byte-identical when no deadline fires" (`L9-2.md:59`). |
| MINOR-3 untested wired sites | **partly closed.** `_reference_energy_evidence_detail` is now tested (`SharedCacheSiteTests`). The session (`whole_window.py:1293`) and core re-derivation (`:6168`) sites are deferred to the author's N3 fault-injection run. The observer makes a firing there a tooling refusal either way, so this is now test coverage only. **Carried open until N3 runs.** |
| MINOR-4 bracket refit | **closed.** `bracket.py`'s strict validation shares the run cache (`bracket.py:169-172,199`). The governed `verify_stored_evidence_physics` refit stays uncached, but a firing there is observed (`test_bracket_refit_firing_is_observed`). |
| MINOR-5 lost reference, unclassified stops | **closed for in-process firings.** Each firing site is observed and becomes `calibration_wall_deadline_fired` before any later step. The NEG-8 lost-reference path no longer relies on `_neg8_reproduces`. The mint's consumption refusal is the tooling code `mint_consumption_session_refused` (`dry_run.py:771-791`). |
| NIT-1, NIT-3 | kept by the author with reasons; I agree. |
| NIT-2 | comment added (`whole_window.py:7184`). |
| NIT-4 | the lead accepted the class-table edit. The fix round adds three more codes to the same table, disclosed in `L9-2.md:42-45`. |
| NIT-5 | **closed** (`dry_run.py:714-716`, `test_failed_reduce_leaves_no_unregistered_output`). |

**New findings in the delta.** Both are NITs.

- **NIT-6: the observer claims the first free tool id, which is usually 0 (`sys.monitoring.DEBUGGER_ID`)**
  (`deadline_observer.py:38`). A debugger that claims id 0 later in the run (for example a future `pdb` built on
  `sys.monitoring`) would fail to start. If a debugger already holds 0, the observer just takes the next id. It
  never fails open. Searching from 5 down to 0, or preferring 3-4, would avoid the reserved slots.
- **NIT-7: spawned worker processes are invisible to the observer** (P3). Today nothing on the dry-run path
  refits in a worker. A future `workers>1` caller would let a worker-side firing surface as an ordinary strict
  problem, not as `calibration_wall_deadline_fired`. Add a one-line note to the observer's docstring, or make
  `strict_validate_bundles` refuse `workers>1` inside an observed run.

**Not checked in this round.**

- The N3 end-to-end fault-injection run (`be5277e1f`, `4c5256ce7`) on the real driver.
- The full-size cached acceptance run (the author's).
- Whether block 5's real references share the kept members' calibration. This no longer matters for safety, only
  for run time.

FRESH VERDICT at `f059286bc` (report `35e0519e2`, superseded by §8): ACCEPT

- BLOCKER: none
- MAJOR: none
- MINOR-3 `joulewise/whole_window.py:1293,6168` (carried, coverage only): the session and core re-derivation sites have no direct test under the shared cache; deferred to N3
- NIT-6 `joulewise/b5_analysis/deadline_observer.py:38`: the observer takes the first free tool id, usually 0 (`DEBUGGER_ID`)
- NIT-7 `joulewise/b5_analysis/deadline_observer.py`: a firing in a spawned worker is not observed; no dry-run caller spawns refit workers today
- NIT-1 `joulewise/reduce.py:1526`, NIT-3 `joulewise/cli.py:1949`: kept as dispositioned

## 8. Delta check `f059286bc..2ea99f51f` (answers the Sol review, `review/2026-10-27-l9-sol-rev` @ `46c3f028`)

The lead asked for this on 2026-10-28. The commits are:

- `217094568`: partition the run cache by the metadata bound.
- `888548f98`: classify observer setup failures.
- `2ea99f51f`: choose the partition only from metadata a caller already holds.

Executed on worktrees at `2ea99f51f` (new), `f059286bc` (old) and `0576a734d` (base). Scripts and outputs are in
`l9-rev-1/delta3/`. I did not run the full-size `test_dry_run` with real programs.

**My miss.** Sol's MAJOR-1 is a defect I looked at and dismissed. In §2 I recorded that the cached value is
`max(metadata b_fiducial, fresh)` and that the metadata bound must only lie within 1e-12 of the evidence value
(`reduce.py:1400`). I called that "the governed reducer's existing contract, unchanged here". It was unchanged, but
sharing the dict across bundles and calls made it reachable across bundles. My §3 byte-identity check used
members whose bounds were identical, so it could not discriminate. Sol's finding stands. My verdicts at `c20fa72`
and `f059286bc` should have carried it as a MAJOR.

**What changed (runtime).**

- `whole_window.py`: the run store is now `{float.hex(metadata b_fiducial_s): {evidence sha256: bound}}`.
  - `physics_cache_for(local, metadata)` returns `local` unchanged outside a run, or when the bound is not a finite
    number.
  - Inside a run it returns `_RunPhysicsCacheView`: the caller's local dict first, then the run partition for
    that exact bound. A write goes to both.
  - The consumption-session (`:1331`, `:1397`) and core re-derivation (`:6187`) loops partition by the metadata
    each member already verified.
- `cli._strict_problems` partitions from `reader.raw_metadata()`, both for its own cache and for an explicit
  caller dict. `strict_validate_bundles` and `bracket.py` share the run store only through that path, and
  `bracket.py` is back to its BASE_HEAD bytes.
- `cli reduce` (step 2) and `_reference_energy_evidence_detail` hold no metadata, so they **return to BASE_HEAD
  code with no run cache** (NIT-8).
- `deadline_observer.py`: a missing `sys.monitoring`, a lost tool-id race, or a failed registration or event setup
  now yields `None`. The driver then refuses with `calibration_deadline_observer_unavailable`. Cleanup always frees
  the tool id.

**Governed files.** `ESTIMATOR_CODE_PATHS` at `2ea99f51f` is (`powermetrics_fiducial.py`, `uncertainty_evidence.py`,
`adapters/powermetrics.py`, `reduce.py`). Each blob's SHA-256 equals `0576a734d`'s (`bcdfeec0…`, `b583f35a…`,
`70f47086…`, `7b9c0d28…`), and `git diff --stat 0576a734d 2ea99f51f` over them is empty. The non-report files the
delta changes are `bracket.py`, `deadline_observer.py`, `cli.py`, `whole_window.py` and two test modules.

**Executed.**

- **Lane tests at `2ea99f51f`:** `tests.b5_analysis.test_shared_physics_cache`, `test_deadline_observer`,
  `test_deadline_tripwire` and `tests.test_authentication_io` (which includes
  `test_marked_v2_surface_has_no_direct_readable_io`): **56/56 OK, 558.1 s**.
- **Sol `cache_metadata_probe.py` at `2ea99f51f`** (`delta3/cache_metadata_probe_2ea99f51f.log`):
  - strict validation of the high and low bundles under the shared store: `0 0` (at `f059286bc`: `0 2`);
  - no differing summary keys;
  - the real step-1 driver comparison returns 0 with step 1 `ok` and every later step `ok`, equal to BASE_HEAD
    (at `f059286bc`: 2, `kept_bundle_strict_validation_failed`).

  Its `assert differences` now fails, as intended at a fixed head: there are no differences. Its `cache: {}` line
  is empty because the seed goes through `reduce`, which no longer uses the run store. The strict phase still
  exercises partitioning, because the high bundle's strict call seeds its own partition before the low one runs.
- **Sol `missing_monitoring.py` at `2ea99f51f`:**
  - missing API: return 2, record written (at `f059286bc`: `AttributeError`, no record);
  - tool-id race: return 2, record written, competing tool preserved (at `f059286bc`: `ValueError`, no record).

  My probe checks the record contents: step 0 is `tooling_refusal` / `calibration_deadline_observer_unavailable`,
  and step 1 is `not_run` (`partition_probe.json` `no_monitoring`).
- **My partition probes** (`delta3/partition_probe.py`, `partition_probe.json`). Five bundles share evidence
  `a638eed8…`, with metadata bounds `orig`, `orig±1 ulp` (`math.nextafter`) and `orig±5e-13`. Each has a stored
  summary regenerated by an uncached real `reduce`, so each is self-consistent.
  - **Uncached:** `validate-bundle --strict` on all five gives exit 0 and identical normalized stdout; 5 refits.
  - **Shared store, three orders** (forward, reversed, highest bound first), each validated twice:
    - every exit, stdout and stderr equals the uncached run;
    - 5 refits for 10 calls;
    - 5 partitions, one per exact bound, 1 entry each.
  - **Stored values per partition:** `orig`, `ulp_down` and `-5e-13` store the fresh bound `0.022708904442849103`,
    because at or below the fresh bound `max` picks fresh. `ulp_up` stores `…107` and `+5e-13` stores `…3349102`.
    The bound-equals-fresh case is `orig`.
  - **Real `step_1` in `dry_run.run`** with all five kept bundles, forward and reversed (other steps stubbed):
    return 0, steps 0-2 `ok`, 5 refits.
  - **`reduce` of `orig` after a `+5e-13` strict seed:** exit 0, bytes equal to the stored summary; refits 2,
    because `reduce` no longer reads the store.
- **Read counts and authentication behaviour, no-difference path** (`delta3/readcount_probe.py`; outputs
  `readcount_old.json` at `f059286bc` and `readcount_new.json` at `2ea99f51f`). Inside one
  `V2AuthenticationReadSession`, the probe runs strict validation of A and B, `reduce` A, and
  `strict_validate_bundles([A,B])`, with the run store off and then on. The two JSON files are **identical after
  path normalization**:
  - the same 34 authenticated files and 201 reads;
  - per-file `read_count`, SHA-256, grammar and strict-parse flags are equal;
  - exits, stdout and reduction bytes (`3a867f60…`) are equal;
  - in both trees the records are equal with the store on and off.
- **Within-call sharing** (`delta3/within_call_probe.py`, `within_call_probe.txt`). The probe runs one
  `strict_validate_bundles` call over `[orig, +5e-13]`; counts are strict problems per bundle.

  | case | `0576a734d` | `f059286bc` | `2ea99f51f` |
  |---|---|---|---|
  | low then high, one call | `[0,0]` | `[0,0]` | `[0,0]` |
  | high then low, one call | **`[0,1]`** | **`[0,1]`** | **`[0,1]`** |
  | high then low, separate calls in a run | — | **`[0,1]`** (Sol's MAJOR-1) | `[0,0]` |

  So the delta closes the cross-call regression and keeps BASE_HEAD's within-call behaviour byte for byte
  (OBS-1).

**Review of the code.**

- **Only three operations reach the view.** The reducer touches the cache only through `is not None`, `.get(key)`
  and `[key] = value` (`reduce.py:1527-1528,1593-1594`). Nothing reaches the view's empty underlying `dict` storage
  (`bool`, `len`, iteration or copies).
- **The partition key covers every input of the cached value.** That value is `max(float(metadata b), fresh)`.
  `fresh` depends only on bytes bound to the evidence hash. The partition is `float.hex` of the same metadata `b`
  the reducer folds in, so a hit equals what a fresh fit would return.
- **Edge values.** Distinct JSON spellings of one double share a partition. `-0.0` and `0.0` get separate
  partitions, which is safe (less sharing). A non-finite or non-numeric bound gets no partition, and the reducer
  refuses it anyway.
- **Partition source per site.** In `_strict_problems`, `reduce_bundle` re-reads the same `metadata.json` that
  `reader.raw_metadata()` returned within the call. In the session and core loops, the partition comes from the
  very member metadata whose `instrument_calibration` is passed to `_verify_instrument_calibration`.
- **Observer cleanup** runs in a nested `try/finally`, so a failed `set_local_events` still frees the tool id.

**Findings in this delta.**

- **NIT-8: step 2's `reduce` and the NEG-8 energy re-derivation are uncached again** (`cli.py:1953`,
  `whole_window.py:4663`). This is BASE_HEAD behaviour, so it is not a regression, but two things follow:
  - **Runtime:** step 2 refits once per kept member. Only step 1 and the whole-window loops keep the J2 saving.
  - **Exposure:** warm-cache immunity to step-2 firings (§5) is gone. A step-2 firing is again possible, and the
    observer and tripwire still turn it into a tooling refusal.

  Passing the reader's metadata into `reduce_bundle`'s call site would need a read the V2 guard forbids, which is
  why the author dropped it. The lead should weigh the runtime cost on the laptop run.
- **OBS-1 (pre-existing, not this change): within one caller-owned dict, bundles with the same evidence but
  metadata bounds that differ within the reducer's 1e-12 tolerance poison each other.** This is so at
  `0576a734d`. It affects the harvest's per-worker cache (`b5/harvest.py:2418`), one consumption session's member
  loop, a multi-path `strict_validate_bundles`, and `bracket.py`'s window-inputs dict. On the real archives this
  needs metadata `b_fiducial_s` to differ from the evidence value by a few ulps, which is unlikely if the writer
  copies the value. It would already have shown at harvest as `member.strict_validation_failed`, and the dry run
  reproduces it byte for byte. Suggested check on the laptop: for every kept member, confirm that
  `metadata.instrument_calibration.b_fiducial_s` has the same bits as its `instrument_evidence.json`
  `b_fiducial_s`.
- **NIT-6 stays** (`deadline_observer.py:46` still takes the first free id, usually 0). **NIT-7 stays**
  (spawned workers are unobserved).

**Not checked.** The full-size `test_dry_run` with real programs (the lead runs it). The N3 per-site fault
injection on the real driver. OBS-1 on the real archives.

FRESH VERDICT at `2ea99f51f`: ACCEPT

- BLOCKER: none
- MAJOR: none (Sol MAJOR-1 closed at `2ea99f51f`: cross-call reuse is exact per metadata bound; strict admission and outputs equal uncached in every order tested)
- MINOR: none (Sol MINOR-1 closed: observer setup failures give `calibration_deadline_observer_unavailable` with a written record)
- NIT-8 `joulewise/cli.py:1953`, `joulewise/whole_window.py:4663`: step-2 `reduce` and the NEG-8 energy re-derivation are uncached again (BASE_HEAD behaviour; runtime cost and step-2 firing exposure return, and the observer covers them)
- NIT-6 `joulewise/b5_analysis/deadline_observer.py:46`: first free tool id, usually 0
- NIT-7 `joulewise/b5_analysis/deadline_observer.py`: spawned workers unobserved
- OBS-1 `joulewise/b5/harvest.py:2418` (pre-existing at `0576a734d`): same-evidence bundles with metadata bounds that differ within 1e-12 poison one shared caller dict; check metadata and evidence `b_fiducial_s` bits on the real archives
