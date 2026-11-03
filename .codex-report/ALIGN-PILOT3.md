```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"findings","completion":"complete","summary":"Implemented pilot-3 cache reuse, observe-only repetition, desk diagnostics and the 24-member kit; focused checks pass; hardware rehearsal remains lead-owned.","workspace":{"base_requested":"8510e77b2","base_mode":"exact","head_start":"8510e77b2a1493eb9a591f5dd20cacd6a8190caf","head_end":"8510e77b2a1493eb9a591f5dd20cacd6a8190caf","upstream_end":null,"branch":"lane/2026-11-02-align-pilot3"},"pathspec":[".codex-report/ALIGN-PILOT3-tests.json",".codex-report/ALIGN-PILOT3.md","configs/campaigns/align_pilot_v2/README.md","configs/campaigns/align_pilot_v2/collection_plan.json","configs/campaigns/align_pilot_v2/plan_tree.json","configs/campaigns/align_pilot_v2/registration/acceptance.json","configs/campaigns/align_pilot_v2/registration/derive_identity_pins.py","configs/campaigns/align_pilot_v2/registration/derive_sizing.py","configs/campaigns/align_pilot_v2/registration/identity_pins.json","configs/campaigns/align_pilot_v2/registration/local_file_verification.json","configs/campaigns/align_pilot_v2/registration/model_artifact_inventory.json","configs/campaigns/align_pilot_v2/registration/registration.json","configs/campaigns/align_pilot_v2/registration/sizing_b5.json","configs/campaigns/align_pilot_v2/registration/sizing_evidence.json","configs/campaigns/align_pilot_v2/stages/episodes-a/align-pilot-v2-episodes-a-e01.json","configs/campaigns/align_pilot_v2/stages/episodes-a/align-pilot-v2-episodes-a-e02.json","configs/campaigns/align_pilot_v2/stages/episodes-a/align-pilot-v2-episodes-a-e03.json","configs/campaigns/align_pilot_v2/stages/episodes-a/align-pilot-v2-episodes-a-e04.json","configs/campaigns/align_pilot_v2/stages/episodes-a/align-pilot-v2-episodes-a-e05.json","configs/campaigns/align_pilot_v2/stages/episodes-a/align-pilot-v2-episodes-a-e06.json","configs/campaigns/align_pilot_v2/stages/episodes-a/align-pilot-v2-episodes-a-e07.json","configs/campaigns/align_pilot_v2/stages/episodes-a/align-pilot-v2-episodes-a-e08.json","configs/campaigns/align_pilot_v2/stages/episodes-a/align-pilot-v2-episodes-a-e09.json","configs/campaigns/align_pilot_v2/stages/episodes-a/align-pilot-v2-episodes-a-e10.json","configs/campaigns/align_pilot_v2/stages/episodes-a/align-pilot-v2-episodes-a-e11.json","configs/campaigns/align_pilot_v2/stages/episodes-a/align-pilot-v2-episodes-a-e12.json","configs/campaigns/align_pilot_v2/stages/episodes-a/order_manifest.json","configs/campaigns/align_pilot_v2/stages/episodes-b/align-pilot-v2-episodes-b-e13.json","configs/campaigns/align_pilot_v2/stages/episodes-b/align-pilot-v2-episodes-b-e14.json","configs/campaigns/align_pilot_v2/stages/episodes-b/align-pilot-v2-episodes-b-e15.json","configs/campaigns/align_pilot_v2/stages/episodes-b/align-pilot-v2-episodes-b-e16.json","configs/campaigns/align_pilot_v2/stages/episodes-b/align-pilot-v2-episodes-b-e17.json","configs/campaigns/align_pilot_v2/stages/episodes-b/align-pilot-v2-episodes-b-e18.json","configs/campaigns/align_pilot_v2/stages/episodes-b/align-pilot-v2-episodes-b-e19.json","configs/campaigns/align_pilot_v2/stages/episodes-b/align-pilot-v2-episodes-b-e20.json","configs/campaigns/align_pilot_v2/stages/episodes-b/align-pilot-v2-episodes-b-e21.json","configs/campaigns/align_pilot_v2/stages/episodes-b/align-pilot-v2-episodes-b-e22.json","configs/campaigns/align_pilot_v2/stages/episodes-b/align-pilot-v2-episodes-b-e23.json","configs/campaigns/align_pilot_v2/stages/episodes-b/align-pilot-v2-episodes-b-e24.json","configs/campaigns/align_pilot_v2/stages/episodes-b/order_manifest.json","docs/align/pilot_protocol_v2.md","joulewise/adapters/mlx_runtime.py","joulewise/align/apple/campaign.py","joulewise/align/apple/diagnostics.py","joulewise/align/apple/endpoint.py","joulewise/align/apple/prompt_cache.py","joulewise/align/apple/workload.py","joulewise/align/runner.py","scripts/align_pilot_kit.py","scripts/align_pilot_session.py","tests/align/fixtures/pilot2_cache_ids.json.gz","tests/align/fixtures/pilot2_repetition.json.gz","tests/align/test_apple_endpoint.py","tests/align/test_pilot2_round1.py","tests/align/test_pilot3.py","tests/align/test_pilot3_cache.py","tests/test_align_pilot_session.py"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"pending_verification"},"verification":[{"id":"V1","kind":"test","cmd":"TMPDIR=$(mktemp -d /tmp/align-p3-final-focused.XXXXXX) PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/jw-wt/align-pilot3/tests /opt/homebrew/bin/python3.13 -m unittest tests.test_mlx_runtime tests.test_mlx_runtime_detokenizer tests.align.test_pilot3_cache tests.align.test_pilot3 tests.align.test_apple_campaign","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 80 tests in 134.563s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V2","kind":"test","cmd":"TMPDIR=$(mktemp -d /tmp/align-p3-final-session.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_align_pilot_session tests.align.test_pilot2 tests.align.test_pilot2_round1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 43 tests in 70.605s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V3","kind":"test","cmd":"TMPDIR=$(mktemp -d /tmp/align-p3-final-cache.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.align.test_pilot3_cache tests.align.test_pilot3","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 18 tests in 3.622s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V4","kind":"test","cmd":"TMPDIR=$(mktemp -d /tmp/align-p3-runner.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.align.test_runner tests.align.test_runner_review tests.align.test_runner_fixround tests.align.test_runner_matrix tests.align.test_apple_support_edges tests.align.test_apple_sampler tests.align.test_shade","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 98 tests in 16.139s","OK (skipped=8)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V5","kind":"test","cmd":"TMPDIR=$(mktemp -d /tmp/align-p3-final-endpoint.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.align.test_apple_endpoint tests.align.test_apple_campaign","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 21 tests in 168.035s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V6","kind":"build","cmd":"TMPDIR=$(mktemp -d /tmp/align-p3-final-check2.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 /Users/edr/code/jw-wt/align-pilot3/scripts/align_pilot_kit.py --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["verified align pilot kit"]},"expected":{"exit_code":0,"tail_regex":"verified align pilot kit"}},{"id":"V7","kind":"inspection","cmd":"git -C /Users/edr/code/jw-wt/align-pilot3 diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}],"flags":[{"id":"F1","kind":"verification_gap","level":"nonblocking","text":"Fixture and synthetic-chain checks do not establish native token identity, memory, live energy, thermal behavior or timing/disk bounds.","needs":"Lead: run the three-member quiet hardware rehearsal below before trusting cached measurements or freezing a span."},{"id":"F2","kind":"residual_risk","level":"nonblocking","text":"Cache sizing remains a conditional transferred planning bound; unexpected whole-cache rebuilds can exceed its prefill envelope.","needs":"Retain sizing.planning_bound_unmeasured and replace transfers with rehearsal receipts."}]}
```

## Change

Implemented all five build items within WRITE_SCOPE. No model was loaded, no MLX generation or quiet-Mac capture was run, and no files were staged, committed or pushed. HEAD remains the requested base. The queue/state files are lead-owned and were preserved.

### Diff summary by item

1. **Cache:** an episode-local represented-ID ledger reconciles the full prompt against native state, leaves nonempty fed input, verifies trim return counts and attention offsets, and rebuilds the entire non-trimmable cache on a rewrite. The opt-in generation path measures reconciliation in generation_setup and labels full/cached/fed prefill separately. Custody retains full prompt/output IDs, fed IDs/digest, cache classes, offsets, trims and fallback reasons. Legacy hidden-prefill counterfactual semantics remain; separate cached/fresh hidden annotations split a single full-prompt delimiter walk. Sampler identity hashes the execution policy; unset controls retain legacy serialization/projection. Campaign matching includes cache policy when set.
2. **Repetition:** canonical tool arguments and UTF-8 result bytes are compared across adjacent complete tool turns. Both run-length flags are retained per turn, with no stop, retry, advice injection or changed sampling. The original b-e05 and b-e12 tool transcripts are also replayed from immutable-source fixtures: the preview loop fires, and all 20 b-e12 turns fire neither flag.
3. **Desk:** I4 compares output IDs exactly and prints not_evaluated below two comparable repeats. Energy spreads additionally require equal accounting and full prompts. Added cross-pilot prompt/output comparisons, cache totals, OS onset relative to start/end, last observed OS level and sample age at each turn start, action counts beyond read-marking, bank progress, every harvest flag and battery receipt per member, phase-kind reason counts, and the non-claim identity explanation.
4. **Kit/protocol:** 12 A members then 12 C, 40,960 cap, hint on, both pairs/conditions, three repeats, 300-second idle, midpoint between the blocks, 25 scaffold members. The new namespace is align_pilot_v2 / align-pilot-v2; pilot-2 bytes are untouched. Episode specs differ from pilot 2 only by prompt_cache (tested). New sizing evidence is derived from pilot-2 files with source SHA-256s. Expected collection 19,848.153 s (5.51 h); no savings 31,430.709 s (8.73 h); conditional planning bound 41,761.980 s (11.60 h). Expected two-copy disk 32,196,224,559 bytes; bound 53,020,386,358 bytes. Mac file pins and package observations are inherited with explicit provenance; a fresh Mac receipt survives generate and --check.
5. **Tests:** stateful fake caches expose represented tokens, not just counters. Recorded prompt/output IDs cover 55 turns including B suffix rewrites, a-e01 turn 11's 143-token rewind, and a-e03 turns 8/10's 560/257-token rewinds. Tests cover EOS consumed/unconsumed state, empty delta, non-trimmable rebuild, warmup/member isolation, unchanged legacy identity, changed policy identity, and duplicated/omitted-prefix/wrong-trim mutations. Synthetic native streams pass through the real prepare/warmup/controller/reducer/identity path; the desk uses two repeats per cell and a copied comparator. The kit goes through real preparation, authenticated dispatch and harvest on synthetic bundles.

### Decisions I made

- Kept every spec's seed at pilot 2's seed 1; repeat ordinals are collection metadata/tags/manifest rep fields. This makes prompt_cache the only episode-spec difference and follows the identity-preserving ruling.
- Alternated pair order spam/bank, bank/spam, spam/bank within each block. Spam condition order is BS/SB/BS and bank is SB/BS/SB. Blocks stay contiguous with the midpoint after all 12 A members.
- Reconcile in the measured generation_setup phase, after full render/encode in tokenize; use actual attention offsets as the native consumed-length witness. Recurrent layers without offsets are never partially trimmed. Offset inconsistency or a bad trim fails and invalidates state, rather than reporting a successful hit.
- Split hidden-ID counts in one full-prompt delimiter walk so a cache boundary inside a delimiter or reasoning span cannot change the count. Kept prior_hidden_prefill_tokens and its chat-template counterfactual method unchanged. No hidden-work predictor or residual-analysis input was changed.
- Observe run lengths from the first recurrence (two observations). Multi-call turns compare ordered complete call lists. Canonical arguments use sorted compact JSON; invalid argument JSON is observed as its original string and cannot turn the guard into a stop.
- Kept I4 solely an output-ID equality check. Separate accounting/prompt equality gates energy spreads. Missing ID coverage is not_evaluated, never a count-based substitute for passing I4.
- OS onset is the first recorded nonzero sample within the member interval, which can precede episode start or follow episode end. Per-turn levels use the last recorded sample with its age; no interpolation, freshness threshold or recovery wait was invented.
- Contacts/emails count observed state-changing calls with the relevant tool names; payments count attempts regardless of state change. These are progress diagnostics, not evaluator success assertions. get_unread_emails remains state-changing but is removed from acted_beyond_read_marking.
- Used unrounded pilot-2 campaign duration rows and bundle inventories for OLS (member intercept 519.234919 s, slope 1.151109687; disk intercept 212148182.416 bytes, slope 470678.819 bytes/s), minimum measured phase rates per block, the existing pilot-1 tool allowance, and no second 300-second idle adjustment. The cache envelope is explicitly conditional, not a physical worst-case guarantee.
- Bootstrap new file identities from the authenticated pilot-2 Mac receipt, cross-check against BYTES pins, label inherited observations, preserve fresh local derivations, and refuse changed fresh inputs instead of overwriting their receipt.
- Left records.v1 unchanged: existing context/prefill fields already encode the required accounting. Did not edit calibration-pinned powermetrics/reducer code or either legacy MLX test module. No ruling or scope expansion was needed.

### Hardware rehearsal checklist — lead only

Run after the agent session ends, on the clean lead-controlled real chain scaffold, with the unchanged 300-second idle before each cached member. These are the three original pilot-2 specs with only prompt_cache added; retain all attempted members and divergences.

| Pilot-2 reference spec | New kit member | What it must show |
|---|---|---|
| a-e01: A / spam / benign | stages/episodes-a/align-pilot-v2-episodes-a-e01.json | Exact prompt/output ID equality or first divergent turn; the recorded turn-11 rewind is 143 tokens if the trajectory stays equal; newly fed counts are deltas. GPU energy reference is about 2.5 kJ, a projection to inspect, not a pass threshold. |
| a-e03: A / bank / sabotage | stages/episodes-a/align-pilot-v2-episodes-a-e03.json | Exact IDs or first divergence; expected rewinds 560 at turn 8 and 257 at turn 10 under the recorded trajectory; preserve the old hidden counterfactual and separate cached/fresh hidden counts. This is the costliest cached onset probe; inspect about 6.9 kJ against recorded work, not a tolerance. |
| b-e10: C / spam / sabotage | stages/episodes-b/align-pilot-v2-episodes-b-e14.json | Exact IDs or first divergence; append-only Next reuse, normally no trims/rebuilds; whole-cache rebuild with reason if a rewrite occurs; the same context_limit:11 if tokens stay equal. Inspect the approximately 1.9 kJ projection, not a pass threshold. |

For each member:

1. Compare actual full prompt IDs and output IDs exactly against `/Users/edr/night-align/pilot-v1-20261102T183609Z` bundles, turn by turn. Name the first divergence and retain both trajectories. Check fixed-transcript replay where needed to distinguish numerical divergence from changed subsequent inputs; never relabel changed work as an energy saving.
2. Verify native offsets, cache classes, represented-ID ledger digests, trim return counts, fallback records, full = cached + fed, Turn.context_tokens = cached and Turn.prefill_tokens = fed. Check consumed EOS and nonempty fed input. The non-trimmable fallback must rebuild every layer together; no attention-only trim beside recurrent state. If exercising an unexpected rewrite diagnostically, keep it separate from identity-preserving scientific members.
3. Record per-token prefill/decode rates at 15–30k context, memory/peak-memory receipts, phase/event coverage, request/episode energy and existing attribution agreement (1% of the smallest recorded half-width; no new tolerance). Inspect the projected energies beside the actual work and flags.
4. Require recorded OS level 0 throughout for an unthrottled interpretation, or print first nonzero onset relative to both episode start/end, per-turn levels with sample ages, and observed recovery. Do not invent a safe dwell/duty/episode limit from these fixtures.
5. Harvest once. Read every contention/idle/thermal/identity/battery flag and battery discharged energy. The existing thermal exclusion remains. With thermal absent, inspect contention in particular; it affected 9/12 pilot-2 align members. Keep every flag/status and PROVISIONAL label until the live gate is satisfied.
6. Run the desk end to end with `--compare-session /Users/edr/night-align/pilot-v1-20261102T183609Z`; use --no-harvest for repeated inspection. I4 is not_evaluated for cells having only one comparable rehearsal member. Confirm cache totals, progress, guard flags, phase-kind reasons and first divergence output.
7. Replace transferred timing/disk/memory receipts before sealing a programmed span or trusting cached data. If a-e03 throttles, keep the roster and expect flagged A/bank cells; if it does not, keep the same roster. The rehearsal determines operating limits; this implementation does not.

## Verification notes

The full suite was deliberately not run: the task assigns it to CI. Final focused checks are in the envelope; every unittest invocation, including corrected failures and earlier passes, is listed below and in `ALIGN-PILOT3-tests.json`. Commands run from the repository root; each allocates a fresh TMPDIR under /tmp. The bare interpreter's eight existing optional/dependency skips remain disclosed.

The initial command had two invocation errors and one pre-existing /tmp alias assertion. Subsequent development failures were confined to new test-fixture setup (missing governed identity metadata, incompatible base prompt fields, and a config symlink violating the composer's existing path fence); each was corrected and rerun. No failing verification remains. A read-only process inspection attempt was denied by the sandbox (`ps: operation not permitted`); it did not block verification and no bypass was attempted.

**T1** — exit 1. Initial command used a nonexistent test_apple_pilot module; detokenizer tests require tests on PYTHONPATH. The existing session test also compared /tmp and /private/tmp lexically. Corrected invocation and resolved the synthetic test root; no legacy runtime tests edited.

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-baseline.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_mlx_runtime tests.test_mlx_runtime_detokenizer tests.align.test_apple_pilot tests.test_align_pilot_session
```

```text
Ran 60 tests in 65.316s
FAILED (failures=1, errors=2)
```

**T2** — exit 0

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-runtime.XXXXXX) PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/jw-wt/align-pilot3/tests /opt/homebrew/bin/python3.13 -m unittest tests.test_mlx_runtime tests.test_mlx_runtime_detokenizer tests.align.test_runner
```

```text
Ran 75 tests in 0.232s
OK
```

**T3** — exit 1. New identity fixture omitted required source stack metadata: ValueError: source stack identity fields are unavailable. Replaced it with governed metadata.

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-cache.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.align.test_pilot3_cache
```

```text
Ran 8 tests in 0.249s
FAILED (errors=1)
```

**T4** — exit 0

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-endpoint.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.align.test_apple_endpoint tests.align.test_apple_campaign
```

```text
Ran 21 tests in 164.860s
OK
```

**T5** — exit 1. New identity fixture retained incompatible base prompt fields: ValueError: config cannot be normalized into scientific identity. Switched to the existing as_config helper.

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-cache2.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.align.test_pilot3_cache
```

```text
Ran 9 tests in 0.722s
FAILED (errors=1)
```

**T6** — exit 1. New Mac-pin preservation fixture symlinked config inputs outside its temporary repository: ValueError: config escaped repository. It now copies the 49 MiB config inputs; the production confinement check remains intact.

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-cachedesk.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.align.test_pilot3_cache tests.align.test_pilot3
```

```text
Ran 15 tests in 2.784s
FAILED (errors=1)
```

**T7** — exit 0

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-session.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_align_pilot_session tests.align.test_pilot2 tests.align.test_pilot2_round1
```

```text
Ran 43 tests in 73.409s
OK
```

**T8** — exit 0

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-cachedesk2.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.align.test_pilot3_cache tests.align.test_pilot3
```

```text
Ran 15 tests in 3.840s
OK
```

**T9** — exit 0. Existing optional/dependency skip gates; no model or hardware evidence supplied by this run.

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-runner.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.align.test_runner tests.align.test_runner_review tests.align.test_runner_fixround tests.align.test_runner_matrix tests.align.test_apple_support_edges tests.align.test_apple_sampler tests.align.test_shade
```

```text
Ran 98 tests in 16.139s
OK (skipped=8)
```

**T10** — exit 0

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-final-runtime.XXXXXX) PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/jw-wt/align-pilot3/tests /opt/homebrew/bin/python3.13 -m unittest tests.test_mlx_runtime tests.test_mlx_runtime_detokenizer tests.align.test_pilot3_cache tests.align.test_pilot3
```

```text
Ran 67 tests in 3.644s
OK
```

**T11** — exit 0

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-final-endpoint.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.align.test_apple_endpoint tests.align.test_apple_campaign
```

```text
Ran 21 tests in 168.035s
OK
```

**T12** — exit 0

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-final-focused.XXXXXX) PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/jw-wt/align-pilot3/tests /opt/homebrew/bin/python3.13 -m unittest tests.test_mlx_runtime tests.test_mlx_runtime_detokenizer tests.align.test_pilot3_cache tests.align.test_pilot3 tests.align.test_apple_campaign
```

```text
Ran 80 tests in 134.563s
OK
```

**T13** — exit 0

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-final-session.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_align_pilot_session tests.align.test_pilot2 tests.align.test_pilot2_round1
```

```text
Ran 43 tests in 70.605s
OK
```

**T14** — exit 0

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-final-cache.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.align.test_pilot3_cache tests.align.test_pilot3
```

```text
Ran 18 tests in 3.622s
OK
```

CLI derivation/generation/check receipts (no model work):

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-sizing.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 /Users/edr/code/jw-wt/align-pilot3/configs/campaigns/align_pilot_v2/registration/derive_sizing.py --pilot-session /Users/edr/night-align/pilot-v1-20261102T183609Z
```

```text
derived pilot2 sizing evidence (no model work)
```

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-generate.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 /Users/edr/code/jw-wt/align-pilot3/scripts/align_pilot_kit.py
```

```text
generated align pilot kit
```

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-generate2.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 /Users/edr/code/jw-wt/align-pilot3/scripts/align_pilot_kit.py
```

```text
generated align pilot kit
```

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-final-generate.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 /Users/edr/code/jw-wt/align-pilot3/scripts/align_pilot_kit.py
```

```text
generated align pilot kit
```

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-final-generate2.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 /Users/edr/code/jw-wt/align-pilot3/scripts/align_pilot_kit.py
```

```text
generated align pilot kit
```

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-final-check.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 /Users/edr/code/jw-wt/align-pilot3/scripts/align_pilot_kit.py --check
```

```text
verified align pilot kit
```

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-final-check2.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 /Users/edr/code/jw-wt/align-pilot3/scripts/align_pilot_kit.py --check
```

```text
verified align pilot kit
```

```sh
TMPDIR=$(mktemp -d /tmp/align-p3-identityhelp.XXXXXX) PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 /Users/edr/code/jw-wt/align-pilot3/configs/campaigns/align_pilot_v2/registration/derive_identity_pins.py --help
```

```text
  --root ROOT
```

Final diff/authority inspection: every modified path is within the exhaustive allowlist; all changed Python files parse. Both legacy MLX test modules and calibration estimator files have empty diffs. The final git diff whitespace check passes. The recorded prompt fixtures and sizing inputs carry their immutable source-file digests. No unrelated or concurrent dirt was observed.

## Residual risk

Native cache numerical equality, actual memory, live phase/energy coverage, thermal onset/recovery and empirical timing/disk behavior remain unverified until the lead's three-member rehearsal. The synthetic checks establish orchestration and exact ID accounting only. The planning prefill envelope assumes bounded rewinds and can be exceeded by unexpected whole-cache rebuilds; retain sizing.planning_bound_unmeasured. No cached measurement is promoted to trusted hardware evidence by this report.
