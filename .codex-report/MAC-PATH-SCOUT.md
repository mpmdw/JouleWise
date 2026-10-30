# Mac path scout — 2026-10-30, activation 4e748ac1

## Scope and verdict

Read-only inspection of existing branches; only this report is committed. No hardware, models, real data, capture, admission, merge or messages to Ed. All verification Python commands executed here used Python 3.13.5, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`, and `-B`.

Evidence aliases below are immutable snapshots: **K** = `codex/2026-10-28-kb-v2` at `aa101880c777a41d5cd0063abe8ccadc3312c80a` (fetched head; reader work can advance), **E** = `desk/2026-10-29-byext-slots` at `ee439ce193606dd388db5a54464ffb4e8b6c5797`, **X** = `lane/2026-10-27-bytes-extension` at `d29c29fb04210137ecd0481cc2733484a9a040ab` (BY-EXT-1), **M** = main `3b0ad9b5a`. File:line references are relative to that alias, not to this report's branch.

**Neither requested run has a complete, executable Mac recipe today.** K has no continuous-capture launcher or arbitrary-span harvest producer. E has a valid fixed kit but no H-compatible registration/sizing inputs and no kit-selecting runner. An exact arm command for either would conceal missing implementation. These are engineering blockers, not NEEDS_RULING. K's own report explicitly disclaims implementing the capture/harvest extension (K `.codex-report/KB-V2.md:137-144`); E's README delegates launching to existing tooling (E `configs/campaigns/bytes_mac_check_ext/README.md:18-45`).

## A. Commands, lifecycle and preconditions

### Common Mac preflight

Only the lead works at the desk after the last pass-2 desk, with the BYTES loop held/DONE and no competing night job. No agent survives into capture. The current handoff explicitly schedules extension steps and KB after the last desk (M `RUN_STATE.md:895-904`); machine-state doctrine forbids agent-time capture (M `AGENTS.md:62-68`). This scout cannot certify current Mac disk, model inventory, launchd state or venv.

Use a separate non-claim checkout, preserve collected checkouts and their ledgers, and integrate/review the relevant source before preparing. K contains the stream tool; E contains extension support. Plain main lacks `scripts/bytes_h_session.py` (verified with `git show origin/main:scripts/bytes_h_session.py`). Use the checkout's own Python 3.13 `.venv/bin/python`; the lock's install recipe is `python3 -m pip install -c env/mac-measurement-lock.txt -e ".[mac]"` (K `env/mac-measurement-lock.txt:1-7`). Locked MLX/MLX-LM/MLX-Metal are in lines 25-27. K's registered comparison includes Python and package disclosures and physical-stack comparisons (K `scripts/bytes_stream_test.py:46-52,108-144`; rule `:206-239`). Do not silently upgrade the capture stack.

The commands below are instructions for the future Mac lead, **not commands executed by this scout**. `MROOT` means the reviewed non-claim checkout, `PY="$MROOT/.venv/bin/python"`, `SESSION` a new empty absolute session directory, and `DESK` a separate output directory. These are shell path selectors, not hidden program environment variables. In live collection `JW_B5_SYNTHETIC_ONLY` must be unset (E README `:24-25`); keep `PYTHONDONTWRITEBYTECODE=1`. The stream probe itself has no synthetic-only interlock: its lazy import reaches MLX whenever a real probe is requested (K stream `:1121-1127`). Never use the environment guard as a substitute for avoiding live commands.

### 1. KB-V2

First the lead must admit the reading rule; it still says pending and must bind before the test (K rule `:3-23`). After review of the final K head, the available exact CLI pieces are:

```sh
"$PY" -B "$MROOT/scripts/bytes_stream_test.py" --bytes "$PAYLOAD_BYTES" --repeats "$REPEATS" --device macbook_m3_max --idle-s 0 --settle-s 0 --out "$RECEIPT"
"$PY" -B "$MROOT/scripts/bytes_stream_test.py" scan "$SCAN_JSON" > "$SCAN_RESULT"
"$PY" -B "$MROOT/scripts/bytes_stream_test.py" --bytes "$PAYLOAD_BYTES" --repeats "$REPEATS" --device macbook_m3_max --idle-s 57.6 --settle-s 3 --out "$RECEIPT"
"$PY" -B "$MROOT/scripts/bytes_stream_test.py" read "$INPUT_JSON" > "$READ_RESULT"
```

These lines describe separate phases, not an executable four-command campaign. Scan calls use payloads `2**k`, k=14..35, three receipts per size, repeats chosen for about two seconds at that payload; stop at the largest allocatable buffer. Preserve the completed prefix, assemble its receipts into the JSON list SCAN_JSON, and run `scan` once. No retry into acceptance. A refused knee ends the measured test (K rule `:88-144`). No fixed numeric repeat list exists before observing timings.

On success use the scan's B, Bc1, Bc3, Bc2. Make eight measured calls S,C1,C3,C2,C2,C3,C1,S; per-call repeats are floor(planned call length / observed dispatch time at that exact payload), with the same planned length for each arm's pair (K rule `:66-86,138-165`). `macbook_m3_max` is the committed hardware ID (E extension r01 config `:2-8`; K reference stack `:49`). CLI options above are the complete probe interface; `scan` and `read` each accept one positional JSON path (K stream `:1180-1209`). There is no `prepare`, `install`, `arm`, detached launcher, launchd label or quiet-wait option for KB in this script. Its sleeps are settles and baselines, not a quiet-machine admission test (K stream `:1132-1160`).

**Missing before launching:** one unattended driver must run the scan, select counts, execute the palindrome under one continuous powermetrics capture and one continuous KM003C stream, and produce the governed harvest inputs using one meter clock fit. The requirement and missing producer are explicit (K rule `:248-251,474-496`; K report `:139-144`). Do not substitute `run_campaign.py` per-call captures or pretend the H model kit runs this probe.

The probe writes a v2 receipt with raw-clock endpoints, counts, stack comparisons and clock metadata; local comparison leaves capture fields pending (K stream `:108-144,1169-1177`). INPUT_JSON must contain the scan result and eight `{receipt, harvest}` records. Harvest supplies stream energy integrals, native idle rows, anchor/timing/latency bounds, meter/battery edges, capture identity and gap/source disclosures; `read` consumes them, it does not generate them (K rule `:474-496`). Preserve raw capture/journals, all scan/probe receipts, scan result, INPUT_JSON and reader output. No KB-specific disk allowance or named capture launcher is supplied by those files; free RAM for the scan's allocatable prefix and disk for continuous raw capture must be checked by the missing setup, not guessed from H sizing.

Ed's arm notice still applies to a future quiet window: H's handoff requires notice and says Ed's NO overrides (E `RUN_STATE.md:297-298`); the general rule requires an exit warning if an interactive session is alive (E `RUN_STATE.md:571`). No KB code sends or waits on that notice. The lead must supply this lifecycle before capture; this scout sent nothing.

### 2. Extension kit

E records that the download was completed, with a size-matched receipt; do not repeat the stale claim that the model is still deleted. Its model path is `/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit`, revision `815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9`, int8/group 64 (E `configs/campaigns/bytes_v1/extension/slots.json:12-31,53`; E r01 config `:13-23`). Recheck the actual files at the desk. Also retain the scaffold's reference model: this is not a five-model-call-only session (E README `:6-16`).

Desk commands available on E, from MROOT as working directory:

```sh
"$PY" -B scripts/bytes_manifest.py headers --model-dir /Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit --revision 815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9 --out "$DESK/Qwen3.8-27B-8bit.headers.json"
"$PY" -B scripts/bytes_manifest.py kv --model-dir /Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit --revision 815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9 --out "$DESK/Qwen3.8-27B-8bit.kv.json"
"$PY" -B scripts/bytes_manifest.py merge --headers "$DESK/Qwen3.8-27B-8bit.headers.json" --kv "$DESK/Qwen3.8-27B-8bit.kv.json" --out "$DESK/bytes_manifest_extension.json"
"$PY" -B scripts/bytes_mac_kit.py --extension qwen38-27b-8bit --check
"$PY" -B scripts/check_b5_chain.py --pack-root configs/campaigns/bytes_mac_check_ext --no-live-identity
```

Headers/KV/merge come from X `.codex-report/BY-EXT-1.md:127-137`, with the filled E revision substituted. KV performs inference; run only at the held desk. Keep the explicit separate merge destination outside repository configs; E protects those destinations and frozen-manifest aliases (E `.codex-report/BY-EXT-2.md:59-72`). E fixes the architecture refusal described by the old slot note (same report `:9,28-30`).

**H lifecycle once repaired, not currently executable for extension:**

```sh
"$PY" -B scripts/bytes_h_session.py prepare --measurement-root "$MROOT" --session-root "$SESSION" --kit configs/campaigns/bytes_mac_check_ext
# Lead reads STAGED, plan hash, t0, disk and flags; sends/checks Ed's notice.
"$PY" -B scripts/bytes_h_session.py install --session-root "$SESSION"
# Exit all agents. Resume only after custody/night/result.json exists.
"$PY" -B scripts/bytes_h_session.py desk --session-root "$SESSION"
```

`--kit` above is a proposed interface, absent today (E H `:870-886`). Today those prepare arguments are rejected; omitting it prepares the original kit. H prepare reads kit-local registration sizing, pins and artifact inventory, verifies every listed model file, requires empty SESSION and free bytes >= P, collects identities, writes plan/view/session records and reports STAGED or INPUTS_ONLY (E H `:286-377`). It requires the real default ledger and its matching committed head pin; never fabricate a ledger or reuse an advanced ledger with a stale pin (E `joulewise/b5/plan.py:835-848`).

H computes t0 from loop.json launch_lead_s (default 420 s, minimum 300 s), rounded up to a minute (E H `:43-47,302-306`). It does not implement the b6 loop's notice/veto wait. Do not apply a loop notice delay to an already expiring H plan: complete notice handling before a fresh final prepare, or change scheduling consistently. No `JW_B6_LOOP_TICK` or loop bootstrap belongs to this isolated kit.

Install uses `scripts/install_night_agent.sh --plan PLAN --python VIEW/.venv/bin/python --courier-bin VIEW/scripts/b6_courier.sh --launchctl-bin launchctl`; publishes `com.joulewise.night.plist` and `com.joulewise.night.deadman.plist` in `~/Library/LaunchAgents`, records installer stdout/stderr and exits (E H `:380-437`). It does not write collection.active. At t0 the driver refuses an agent-present census, performs the hazard arm including dwell/instrument checks and network-time OFF, and checks the census again (E `joulewise/b5/driver.py:3-29,2194-2243`). H is not a loop PRECHECK waiting indefinitely for agents. Per-member idle admission retries under its existing cap and remaining session budget, records the ledger and skips on exhaustion (E `joulewise/controller.py:2044-2065,2163-2177`).

Desk refuses without the terminal record. It harvests with `--plan`, `--archive-root SESSION/archive`, `--registration-dir` from session state, `--pack-records-root SESSION/private`, `--export-dir SESSION/export`, `--non-claim`; preserves harvest logs and derives MEASUREMENTS.json (E H `:809-832`). Preserve native EXPORT.runs.csv and EXPORT.session.json together, including failed/skipped corpus rows. Extension evaluation must use:

```sh
"$PY" -B scripts/bytes_mac_kit.py --extension qwen38-27b-8bit --runs "$EXPORT_CSV" --measurements "$SESSION/MEASUREMENTS.json" --out "$SESSION/resolvability.json"
```

Use the session's exact commit; compare the recorded tree hash. Exit 0 passes, 2 fails; malformed inputs error. Five succeeded/unexcluded 512-token runs with positive finite decode duration contained in request are required; all scaffold inventory rows must survive export. Missing measured sizing leaves S unavailable (E README `:34-70`; E kit `:389-467`). H currently instead calls bytes_gates.py and writes C5.json/desk.json: that is not the extension verdict (E H `:830-866`). After terminal/desk, uninstall using `scripts/install_night_agent.sh --plan "$PLAN" --uninstall --launchctl-bin launchctl` (E RUN_STATE.md:270). No automatic claim registration follows.

## B. Smallest coherent runner change and integration

A global KIT assignment alone is insufficient. Parameterize `prepare(..., kit=KIT)` and `measurement_view(..., kit, pack_id)`; derive pack_id from the selected tree's b6_layout.packs singleton, persist kit path and pack ID in session.json, and use persisted values in measurements/desk, defaulting for historical H sessions. Replace every KIT/PACK_ID use, including staging directory, registration path, export membership check and checker plan (E H `:41-42,134-139,247,289-290,339,365,620-626,832`). Validate the selected path within the measurement checkout. Add the extension roster when mapping model source to identity: the registered-only lookup currently maps unknown sources to neg8_reference, colliding with actual scaffold references (E H `:149-150,184-198`).

Select the extension checker in desk with the exact argv above and preserve its verdict/logs; keep original C5 behavior for original sessions. Supply reviewed extension-local registration inputs: acceptance/calibration references, artifact pins/inventory and a sourced sizing/disk row under the extension pack ID. E commits no extension registration directory at all (enumerated git tree); H unconditionally loads it. The old derivation helpers also hard-code original KIT/roster and original model timing inputs (K `configs/campaigns/bytes_mac_check/registration/derive_identity_pins.py:22-54`; `derive_sizing.py:41-65`); copying their outputs would not authenticate or size the extension.

Expected touched files: scripts/bytes_h_session.py, tests/test_bytes_h_session.py, extension README and reviewed extension launch-input files/generator. Test original-session compatibility; selected-tree/pack/hash persistence across separate prepare/install/desk processes; real fixed-tree staging with synthetic model files and matching synthetic ledger; distinct Qwen/reference identities; extension harvest membership; extension checker pass/fail/malformed input; missing sizing/model/stale pin failures. Existing tests already provide synthetic registration/prepare seams (K tests/test_bytes_h_session.py:23-39,298-335). No implementation was made in this scout.

Land this work on an extension launch follow-up based on E, carrying K's manifest-ID correction, rather than expanding the reader's round-9 fix. Direct K-versus-E H diff is only two substitutions: external_ids keys and lookup change from manifest path to manifest_id (K H `:153-154,210`; E same lines). A path-selector change need not conflict semantically; preserve K's corrected ID mapping. Both branches add the whole script relative to their common base `6731d5249`, and main lacks it, so integrating both independently may produce an add/add conflict. Resolve to one combined script; do not overwrite K's fix with E's version.

## C. Shared quiet time and duration

There is no supported one-prepare/one-arm combination. H stages one fixed model tree and KB needs an independent scan plus continuous capture across eight probe calls. Neither selected tree dispatches KB (E kit builder `:105-168`; K stream CLI `:1180-1209`). They can occupy consecutive parts of a long human-reserved quiet period, but today require separate execution lifecycles. Combining them would require an explicit composite driver, not a shell flag; no scientific ruling is needed merely to keep the lifecycles separate.

KB's source plan is 3,573.6 s (59.56 min, arithmetic conversion), comprising 921.6 s idle + 72 s settles + about 80 s setup + 2,500 s streams. S calls are 500 s each and cache calls 250 s each (K rule `:162-165`). The full scan plans 66 calls at about 2 s, hence about 132 s of timed scan work, plus allocation/warm-up/metadata overhead (K rule `:88-91,474-475`). These are planning totals, not a measured end-to-end guarantee.

**Extension wall time is not yet numerically determined.** The kit has five science runs split 3/2, planned corpus 18 stopping at 12 valid, and start/mid/end references 3/1/3 (E README `:6-16`; E kit `:452-463`). It has no kit sizing file. Its reported S projects the later 50-science/25-reference/seven-collection pack, expressly not this kit's duration (E README `:64-68`). Do not quote S, original-H's 27,370.23694186782 s (E original registration/sizing_b5.json:363), or BY-H2's historical duration as an extension estimate. H's maximum scheduling formula is minute-ceil(programmed span + 3300 + 7200 + 7200), sourced from E plan_inputs.py:56-59 and b5/plan.py:59-67; these are allowances, not expected wall time, and cannot be evaluated without extension sizing. No new numeric margin is recommended.

## D. Executed checks and blockers

Executed in disposable detached checkouts, with the synthetic guards stated above:

- K bounded `ReceiptTests`, `ReadingRuleArithmeticTests`, `ExactKneeTests`: 29 tests, OK. The optional full stream module was started and stopped during its generated real-CLI fault matrix; it is incomplete, not a passing suite.
- E `scripts/bytes_mac_kit.py --extension qwen38-27b-8bit --check`: PASS, verified non-claim Mac kit.
- E `scripts/check_b5_chain.py --pack-root configs/campaigns/bytes_mac_check_ext --no-live-identity`: PASS, clean true, errors 0. Initial sandbox run could not create tempfile; rerun with disposable fixture-write access passed. This proves static structure, not arm readiness.
- E `python3.13 -B -m unittest tests.test_bytes_mac_kit tests.test_bytes_extension`: 24 tests, OK.
- E original `scripts/bytes_mac_kit.py --check`: FAIL, drift at configs/campaigns/bytes_mac_check/stages/check-qwen3-8b-8bit/bytes-mac-check-check-qwen3-8b-8bit-r01.json, matching E BY-EXT-2:76-78. No protected kit was regenerated.
- E in-memory selector-only experiment (set KIT to extension path and PACK_ID to extension ID, then call prepare): fails at registration.load_sizing with FileNotFoundError for the absent extension registration directory, before creating SESSION. No source was changed. This directly confirms that a selector alone cannot launch the kit.
- E H `prepare` without a selector: refuses models missing at the original Llama-70B source on this Linux scout, before creating SESSION. This demonstrates original-kit selection, not a missing-file finding about today's Mac.

Known blockers from code: KB admission and external capture/harvest/quiet launcher; extension selector, pack identity/model mapping, checker dispatch and absent launch registration/sizing/pins. E slots still have manifest/KV/resolvability and future-pack sizing/disk/clock/est_minutes pending (E slots.json:33-51,56-85). Future-pack slots are not a reason to register the diagnostic or feed invented sizing; X BY-EXT-1:144-156 makes them downstream of the kit. Model download identity is filled, but actual current files/free disk remain Mac-local verification. Ledger pin and calibration acceptance must be checked in the chosen checkout, not assumed from historical BY-H2.

No full repository suite: report-only work plus focused synthetic checks. No NEEDS_RULING: missing implementation and missing observations are determinate engineering work. Any later proposal changing counted data or a printed number must use the owning rule/gate; this report proposes none.
