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

VERDICT: ACCEPT_WITH_FIXES

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
