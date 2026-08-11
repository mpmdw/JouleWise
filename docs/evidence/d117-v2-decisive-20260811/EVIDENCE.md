# Decisive-run evidence bundle — PR #122 head e871f5b (magistrate-attested, 2026-08-11)

Per condition 1 of the 2026-08-11 cold-gate ruling on decisive-run authority.

## Method statement (attested by the magistrate, who executed the run)

- Head under test: `e871f5b577407a75e3fb199b3922ab49013396e2` (PR #122 final head),
  checked out as a detached worktree; tree state clean.
- Machine: Ed's MacBook Pro (M3 Max, macOS Darwin 25.5.0), unloaded of other
  measurement or suite workloads during the run (concurrent editor/agent
  processes only; no other test suites, no mint-grade jobs).
- Hydration (identical to the CI workflow's steps 2-6):
  1. `curl --fail --location --retry 3` of
     `releases/download/fixture-d117-v2-production-v1/d117_v2_production_custody_store.tar.zst`
     (anonymous; no credentials).
  2. `shasum -a 256` = `f1286bc814c9b392667a82443a2aa73df087ca126056d5046da597a310db9553`,
     equal to `archive_sha256` in the committed
     `tests/fixtures/d117_v2_production/transport_descriptor.json` at e871f5b.
     (Independently re-hashed by the cold-gate instance during adjudication.)
  3. `python3 scripts/hydrate_d117_fixture.py --archive <asset>
     --descriptor tests/fixtures/d117_v2_production/transport_descriptor.json
     --census tests/fixtures/d117_v2_production/custody_store/manifest.json
     --destination <store>` → reported logical_bytes=3333877627,
     logical_file_count=191.
  4. `cmp` of the committed census manifest vs the hydrated store manifest:
     byte-identical.
- Execution (identical to the CI workflow's step 8-9, unpiped, output to file):
  `JOULEWISE_D117_CUSTODY_STORE=<store> JOULEWISE_REQUIRE_D117_FULL_FIXTURE=1
  python3 -m unittest -v
  tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_coordinated_report_and_pin_change_refuses_against_floor_evidence`
- UTC timing: START 2026-08-10T21:16:58Z → END 2026-08-11T00:52:37Z.
- Result: `Ran 1 test in 12938.543s` / `OK` / `rc=0`.
- Interpreter: CPython 3.13.1 (Homebrew), the repository's primary local
  interpreter; the same head also passed the full unpiped suite on this
  machine the same night: `Ran 2945 tests in 1589.651s / OK (skipped=89)`.

## Raw log (decisive-local.log, verbatim)

```
START 2026-08-10T21:16:58Z
test_coordinated_report_and_pin_change_refuses_against_floor_evidence (tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_coordinated_report_and_pin_change_refuses_against_floor_evidence) ... ok

----------------------------------------------------------------------
Ran 1 test in 12938.543s

OK
END 2026-08-11T00:52:37Z rc=0
```

## Hermeticity note

The decisive test at this head runs with the store-exclusive plumbing and the
round-1/round-2 hermeticity assertions (exit code 2 on any legacy
custody-locator read; the campaign authentication registry must contain every
store identity and no legacy identity). A green result is therefore
hermetic-by-construction: any read outside the hydrated store would have
failed the run, exactly as it did in CI decisive rounds 1 and 2.

## CI corroboration

- Workflow steps 1-7 (anonymous transport, digest-exact archive gate,
  governed hydration, census byte-equality, 190/190 issued-ledger
  authentication) ran GREEN on GitHub-hosted runners at earlier branch heads.
- The decisive step 8-9 was cancelled at exactly the 360-minute hosted-runner
  platform cap on both attempts at e871f5b
  (2026-08-10T04:33:06→10:33:25Z; 2026-08-10T21:15:41→2026-08-11T03:16:02Z).
## Contemporaneous attestations (captured 2026-08-11, run worktree intact)
```
worktree: /private/tmp/claude-501/-Users-edr-code-JouleWise/626c524c-1d57-4bd5-89f7-973d608cb83b/scratchpad/trustverify
HEAD: e871f5b577407a75e3fb199b3922ab49013396e2
porcelain: [0 entries]
interpreter: Python 3.13.1 (main, Dec  3 2024, 17:59:52) [Clang 16.0.0 (clang-1600.0.26.4)]
store: /private/tmp/claude-501/-Users-edr-code-JouleWise/626c524c-1d57-4bd5-89f7-973d608cb83b/scratchpad/d117-v2-custody-store (191 files)
store manifest sha256: dc90e366235343abeca97f7fc16b6cb5d257cb4a9c9a17d6042b12a4dec49370
archive sha256: f1286bc814c9b392667a82443a2aa73df087ca126056d5046da597a310db9553
```

## D-130 condition C3 — Python 3.11 replay (discharged 2026-08-11)

The identical decisive test, same worktree (e871f5b, clean) and same hydrated
store, on CPython 3.11 (Homebrew /opt/homebrew/bin/python3.11 — the CI-pinned
interpreter): START 2026-08-11T03:47Z -> END 2026-08-11T08:05:52Z,
`Ran 1 test in 15485.553s` / `OK` / rc=0 (raw log:
decisive-local-py311.log). The decisive proof has now completed on both the
primary local interpreter (3.13.1, 12939s) and the CI interpreter (3.11,
15486s), against the same digest-pinned store.
