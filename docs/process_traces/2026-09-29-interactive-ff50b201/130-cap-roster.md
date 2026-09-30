CAP-ROSTER

# Replay roster for the estimator-cap re-size (CAP-RULE-25G83-2, rule R2)

Prepared 2026-09-30 by a read-only Sonnet 5.5 subagent of orchestrator session ff50b201. Nothing in the repository was modified; no iCloud dataless file was downloaded; no replay was run. This file is the only file created (scratch scripts were kept in the session scratchpad, outside the repository).

## 1. What the rulings name (R0/R2 sources)

- Ruling text: `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/20-cap-council/31-addendum-ruling.md` (CAP-RULE-25G83-2, replaces `21-coldgate-fable-ruling.md`'s CAP-RULE-25G83-1) and the erratum `/Users/edr/code/JouleWise-wt-bk-ff50b201/docs/process_traces/2026-09-29-interactive-ff50b201/40-cap-a2/31-coldgate-erratum-ruling.md` (leaves R2 unchanged; its step 7 adds: "If the roster includes probe `a7e8b412`, its result is stated here and nowhere else").
- R2(a) **sizing set**: every retained protocol-v3 capture taken on this machine by a registered derivation chain or window chain, in any launch context: all of W1 and W2 (2026-09-27), all of n1 and n2 (2026-09-19), and every unique protocol-v3 bundle named in `docs/process_traces/2026-08-18-shakedown-first-light/03-budget-calibration-sweep.md`, the shakedown included. That is 12 + 12 + 12 + 12 + 40 = **88 captures** (sections A1, A2, B1, B2, C).
- R2(b) **check set** (replayed and listed with need; does not set the cap): every retained validation-only capture under protocol v3, among them the eight knife-edge captures of 2026-08-18 and probe `20260818T182149-a7e8b412`. Found and listed: nine 2026-08-18 captures outside the sweep record (three shakedown validations plus six `spacing_probe` bundles; these are the eight plus the probe) and three window-c quarantine validation captures. That is **12 captures** (sections D1, D2).
- R2(c) captures whose median frame is outside 100-150 ms stay in the sizing set (can raise the cap, cannot lower it). R2(d) a capture with no need is listed with its reason and contributes nothing, never zero; a capture whose raw bytes are not retained is listed as such with any need on record and its source. R2(e) any replay reaching 5,000,000 cells or 3,600 s refuses the rule and returns to council; R8(c) a wall-deadline stop in a replay is a failed replay to be repeated.
- R0: need = cells evaluated when the harness replays the stored raw bytes at cell limit 5,000,000 and wall deadline 3,600 s, alignment resolved, all 59 pulses fitted; the harness prints cells, frame lengths, dispositions, stop triggers, elapsed seconds and a stored-B-reproduced flag, and no B. Total roster: **100 captures** (100 distinct content ids).

## 2. Method and honesty notes

- **Discovery**: `find -name instrument_evidence.json` over `/Users/edr/code/JouleWise` (main checkout, including its ignored `runs*` directories), `/Users/edr/JouleWise-window-custody`, `/Users/edr/night-archive`, `/Users/edr/night-custody`, `/Users/edr/night-custody-archive`, `/Users/edr/night-bench`, `/Users/edr/night-plan-staging` and the iCloud `JouleWise-backup` (1,867 evidence files, all protocol `powermetrics_pulse_fiducial_v3`). Many are per-run `instrument_calibration/` copies of the same validation bundle; they collapse to **100 distinct content ids**, which are exactly the 88 + 12 above. Worktrees other than the main checkout were not scanned (none is expected to hold raw captures). The iCloud tree was scanned by directory listing only; before any file in it was opened its `SF_DATALESS` flag was checked.
- **Content id** = `joulewise.calibration_ledger.content_id_from_artifact_hashes({"instrument_evidence.json": sha256(file), "manifest.json": sha256(file)})` (`/Users/edr/code/JouleWise/joulewise/calibration_ledger.py:269`; it hashes the canonical JSON of those two entries), computed from the local files of the capture directory named in the row. Identical across every copy of a capture (checked: the copies grouped by this id share one `validation_id`).
- **Raw bytes**: for each capture every copy directory (bundle directories, custody/replay-work `store/` copies and iCloud copies; the thousands of per-run `instrument_calibration/` duplicates were not hashed) was checked for `raw/powermetrics.plist`; every copy that is a real local file (not dataless) was hashed and compared with the sha256 that the capture's own `manifest.json` records (`artifacts["raw/powermetrics.plist"]`). For all 100 captures the other manifest artifacts (`events.jsonl`, `instrument_evidence.json`, `power_trace.csv`) of the directory named in the tables also hash to the manifest values (0 mismatches). Result: **96 captures have a local, hash-verified raw plist inside their own capture directory (READY). 4 captures (windows b and d: `20260726T000039-491995f3`, `20260726T031222-e0ce33f5`, `20260727T020611-4a409a30`, `20260727T050047-95e2f87e`) have their raw plist pruned from the repository bundle directory (D-078 archival prune) and are RAW_IN_ICLOUD_LOCAL**: an already-downloaded iCloud copy hashes to the manifest value, and so do two local copies outside iCloud in `/Users/edr/JouleWise-window-custody/ed-qual-20260817/decisive-replay-work{,2}/store/<hash>/raw/powermetrics.plist` (byte-identical). Their commands use `--raw-powermetrics` with the non-iCloud `decisive-replay-work/store` copy (safer against iCloud eviction); the iCloud path is listed as the alternate. Dataless iCloud placeholders exist only for duplicate copies (per-run `instrument_calibration/` copies and three older `window_a2/a3/a8` bundle copies), were not downloaded or read, and are irrelevant because a local verified copy exists for every capture.
- **Restored raw plists**: the three window-a9 members (`20260725T005132-a64711b7`, `...T011533-0b5ec77c`, `...T022712-0a9534f5`) had empty local `raw/` directories on 2026-09-29 (`23-sonnet-r7-raw-bytes.md`); on 2026-09-30 their local `raw/powermetrics.plist` files exist (mtime Sep 29 18:48) and hash to the manifest values. They are READY.
- **Status vocabulary**: READY = local raw plist in the capture directory, sha256 equals manifest; RAW_IN_ICLOUD_LOCAL = raw absent from the capture directory and located by manifest hash in the iCloud backup (already downloaded; for these four a byte-identical non-iCloud store copy also exists), needing `--raw-powermetrics`; DATALESS = the only copies are iCloud placeholders (not downloaded, reported); NOT_RETAINED = no copy found. Counts: READY 96, RAW_IN_ICLOUD_LOCAL 4, DATALESS 0, NOT_RETAINED 0, hash mismatch 0.
- **Recorded production disposition** is read from each capture's own `instrument_evidence.json` fields `status`, `reasons`, `clock_anchor_resolved`, `detection_projection.disposition` and `detection_projection.diagnostics.trigger` only. Categories: `valid`; `cap stop` (trigger `evaluated_cell_budget`, disposition `detection_nonconvergent`); `clock` (`clock_anchor_unresolved`); `other` (reasons listed, e.g. `pulse_detection_incomplete`). No `b_fiducial_s`, bound or residual field was intentionally read. "Recorded cells" is the stored `evaluated_cell_count` where the field exists (present only in the newer evidence schema); it is a count, not a B, and is not the replay need.
- **R11 disclosure**: while sampling the evidence schema I once printed a whole top-level evidence document of one copy of capture `20260730T210703-f76b5771` (sweep row C-31) and so saw its stored `b_fiducial_s` value. It was not recorded, used or copied anywhere. Everything else was type-only or restricted to the fields above.
- **Sweep-record cross-check (section C)**: the last column reproduces the August sweep record's own result for each bundle (`59/59` plus its cell count, or `anchor unresolved`); those were produced under the older clock-alignment method and are provided for orientation only (the addendum notes today's bytes may differ). All 40 sweep IDs were found in the archive; nothing in the sweep is NOT_RETAINED.
- **Probe `a7e8b412`**: FOUND (contrary to erratum E9, whose search was by name under repository roots and the iCloud archive only): `/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/spacing_probe/20260818T182149-a7e8b412`, raw 91,628,714 bytes, hash-verified, row D1-09. Its recorded disposition is in the table. The shakedown custody `spacing_probe/` directory also holds the other five probe bundles.
- **Harness**: `scripts/cap_replay_harness.py` does not yet exist in `/Users/edr/code/JouleWise` or in `/Users/edr/code/JouleWise-wt-bk-ff50b201` (checked 2026-09-30). Commands below use the interface given in the brief.

## 3. Counts (recorded production dispositions; read from each capture's own evidence)

| Section | Captures | valid | cap stop | clock | other |
|---|---:|---:|---:|---:|---:|
| A1 | 12 | 6 | 3 | 3 | 0 |
| A2 | 12 | 6 | 5 | 1 | 0 |
| B1 | 12 | 4 | 0 | 2 | 6 |
| B2 | 12 | 7 | 0 | 0 | 5 |
| C | 40 | 33 | 1 | 6 | 0 |
| D1 | 9 | 5 | 0 | 4 | 0 |
| D2 | 3 | 3 | 0 | 0 | 0 |
| **All** | **100** | 64 | 9 | 16 | 11 |

Sizing set (A1-C) = 88; check set (D1-D2) = 12.

## 4. Roster tables

Columns: `#` roster id; `capture directory` (absolute; pass this to the harness); `content id` (64 hex); `raw` = size in bytes of `<capture directory>/raw/powermetrics.plist`, hash matches manifest; `status`; `recorded disposition` (from the capture's evidence); `recorded cells` where stored.

### A1. Sizing set - W1 (2026-09-27, derivation night, 25G83)

| # | capture directory | content id | raw bytes (hash-verified) | status | recorded disposition | recorded cells |
|---|---|---|---:|---|---|---:|
| A1-01 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d01` | `5286b307b90c8d35e04c278b073d8f6216b1a1a540f5d3c1304111937572f6a6` | 82,958,403 | READY | clock (clock_anchor_unresolved) | 0 |
| A1-02 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d02` | `51c31db00a91285766305e3dd80eb2be7e50985ee2f6cb9c6047eafa12d545a7` | 82,947,906 | READY | cap stop (detection_nonconvergent / evaluated_cell_budget) | 165,000 |
| A1-03 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d03` | `361d05fdb73b957d1d131a0415ad7039346108df9a9acf0c4e2d83379cbf3123` | 82,836,504 | READY | cap stop (detection_nonconvergent / evaluated_cell_budget) | 165,000 |
| A1-04 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d04` | `e055af15ca06ebaad7d3cd3dfc9163840219e6610a2e5e197b3cbbc76d64956f` | 83,139,610 | READY | valid | - |
| A1-05 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d05` | `0af949aecb4d30109a9389637ac2c801ea1258284b0b20be6b5f90eb239c467c` | 83,498,273 | READY | valid | - |
| A1-06 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d06` | `79bda70471f19d75ef63ee4b847b2908eaed554e474c623a2612ae392d82aa2d` | 83,002,804 | READY | valid | - |
| A1-07 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d07` | `554d13ec9e9603e471cadfed74d0cbc36f4625f92e94ea942e7734353b5ea01d` | 83,030,420 | READY | valid | - |
| A1-08 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d08` | `41d35b5e30099c9f67b9f8e23ae877bb97503044aa1becf122571e9eff3d0446` | 83,011,425 | READY | clock (clock_anchor_unresolved) | 0 |
| A1-09 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d09` | `2e31c3d14289df686a9c45b05657a778fcd4e2d1e7fd9ac57a8388754f0f2f81` | 82,688,012 | READY | cap stop (detection_nonconvergent / evaluated_cell_budget) | 165,000 |
| A1-10 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d10` | `37dd0834396ea4337f510c4f4bddcdfdd6ce60afa495ccf5d79e6646d9d86dd3` | 83,456,454 | READY | valid | - |
| A1-11 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d11` | `2383b51dc8a49a8ff234740e6d53c65e1d4a902061262145c05534c0e90c9d36` | 83,082,985 | READY | clock (clock_anchor_unresolved) | 0 |
| A1-12 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d12` | `c1d9d5369b8317ade1c1d9229b5738b59ec733b51b931d033ccbf386731d132d` | 83,278,531 | READY | valid | - |

### A2. Sizing set - W2 (2026-09-27, derivation night, 25G83)

| # | capture directory | content id | raw bytes (hash-verified) | status | recorded disposition | recorded cells |
|---|---|---|---:|---|---|---:|
| A2-01 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d01` | `641c1240dd6c523b5abb8096d84dfe67b1ad1a1307c2e705578a264530fb838e` | 83,198,257 | READY | valid | - |
| A2-02 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d02` | `fd2561b1bd6c5666dd0269d24766fa4d5af41362afa71976db21bdde68443746` | 83,349,497 | READY | cap stop (detection_nonconvergent / evaluated_cell_budget) | 165,000 |
| A2-03 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d03` | `a9007b73fd91198f6d87fd5bc0195824543a18c4b751e408d6289b79e2ac2b41` | 83,004,771 | READY | valid | - |
| A2-04 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d04` | `4ff672124f72ca261dd2e9063527abcb08108f588fbc75c45169ae926a7519cc` | 83,561,060 | READY | valid | - |
| A2-05 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d05` | `2d81bed3f4b2f2b7c92b1488b465f53ed932ca982fea9a337086e4032dbbe3b9` | 83,549,096 | READY | valid | - |
| A2-06 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d06` | `63d2c4ee381016d96c730d1228fcc870b5416e245d20f4eb332c37d76dc2a6ed` | 83,051,322 | READY | cap stop (detection_nonconvergent / evaluated_cell_budget) | 165,000 |
| A2-07 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d07` | `d0942448d08578d945b7d36db9feef10c73d8dc18ddcf56633b0e03d741957bd` | 82,964,137 | READY | clock (clock_anchor_unresolved) | 0 |
| A2-08 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d08` | `8127f5390f30373651720018a4da2d21d4f901447760c7c70de96e60ee5ad10f` | 83,284,220 | READY | cap stop (detection_nonconvergent / evaluated_cell_budget) | 165,000 |
| A2-09 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d09` | `4154f1f4001e660d40ba88a60b40f3be11be2128deace4db14d02210eea295b2` | 83,295,510 | READY | valid | - |
| A2-10 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d10` | `372eafc180693b3a21053ce2133472a8918fdf300730c04245cb709bd823ccb0` | 82,755,729 | READY | valid | - |
| A2-11 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d11` | `f860a632932b34cbdf7b913acdf4e2e1fee61fe0cb3ca29c88eab4d6d321c6bb` | 82,747,303 | READY | cap stop (detection_nonconvergent / evaluated_cell_budget) | 165,000 |
| A2-12 | `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d12` | `5e991d11877004780d28226af26aa76d5002aee2d9404c5c7713f3c33cc38780` | 82,895,736 | READY | cap stop (detection_nonconvergent / evaluated_cell_budget) | 165,000 |

### B1. Sizing set - n1 (2026-09-19, derivation night, 25G83)

| # | capture directory | content id | raw bytes (hash-verified) | status | recorded disposition | recorded cells |
|---|---|---|---:|---|---|---:|
| B1-01 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d01` | `08cf2f19ca7d2b1881e9ed426bbf2c4039e1b425e1ba999a5527bcee4e743cb6` | 45,687,056 | READY | valid | - |
| B1-02 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d02` | `236636a63392ca842f233bf132539e73e5b824cd5173dd10086af60e0cdc7909` | 44,578,529 | READY | other (not_all_pulses_detected,pulse_detection_incomplete) | - |
| B1-03 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d03` | `697ad07383e83bca6e031dd40708595d1f59227fece3c3eb8e6d04c8c2318dca` | 44,630,868 | READY | valid | - |
| B1-04 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d04` | `4eb3ce0912ae002dc6a5cb5ee671be5636ecb42dcf8752518825843ccfebbc4b` | 45,227,412 | READY | other (not_all_pulses_detected,pulse_detection_incomplete) | - |
| B1-05 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d05` | `e7e313e191bc844b49f4ddb18cbea5e17ca8367faa097f81aa699fc89a2d81a1` | 44,848,806 | READY | valid | - |
| B1-06 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d06` | `3616ae76d346dc9c8de40094133918d052a7c4b8201d0d95e882b05f22672565` | 45,578,212 | READY | other (not_all_pulses_detected,pulse_detection_incomplete) | - |
| B1-07 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d07` | `5a675edfb08e2b433dc9d41b2b1447f795a00b630bd83c1b6f7581583c5ed07f` | 44,849,239 | READY | clock (clock_anchor_unresolved) | 0 |
| B1-08 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d08` | `5aa5c8ff05cc0b93feb6712f212797c3921e2169ff3eb00421d74673ca42cac7` | 45,098,504 | READY | other (not_all_pulses_detected,pulse_detection_incomplete) | - |
| B1-09 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d09` | `f797be992838db288689b3281e807f4f795a416dd1ad5c9ca0f5739a9a0f3e6b` | 45,209,596 | READY | other (not_all_pulses_detected,pulse_detection_incomplete) | - |
| B1-10 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d10` | `4a4ac7d782dd571092a5ffa389bbbfac33e1533e3a27a2b5258f1ac7dbb5918f` | 44,900,904 | READY | clock (clock_anchor_unresolved) | 0 |
| B1-11 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d11` | `7d34edec09f8c7db7862a98bd387942444622fafdb49ed597833273c4b94b6fb` | 45,206,351 | READY | other (not_all_pulses_detected,pulse_detection_incomplete) | - |
| B1-12 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d12` | `a1975da884533272159688d260aa034fe7f4ccfb30e4abaa67cde14977bc38fc` | 44,840,974 | READY | valid | - |

### B2. Sizing set - n2 (2026-09-19, derivation night, 25G83)

| # | capture directory | content id | raw bytes (hash-verified) | status | recorded disposition | recorded cells |
|---|---|---|---:|---|---|---:|
| B2-01 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d01` | `7bce01d1490e10190958052c770f790a2ea2733c5091c605f2fdc86a09afb1c2` | 45,211,525 | READY | valid | - |
| B2-02 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d02` | `3c78c44752b15c2b5aa14d68a1aa6fe1b64b868de75b77a1770bdcc0f7b90711` | 45,106,776 | READY | other (not_all_pulses_detected,pulse_detection_incomplete) | - |
| B2-03 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d03` | `ba83eb6f2b3dfb2e72e5cf37fe25df8d3387e70dafc6e8fe384b1f650003a236` | 45,839,404 | READY | valid | - |
| B2-04 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d04` | `c76b8987205bd6b6160344f8b52f7e831b7c67b3d46a33ed5bf6f8d0ee5b0faa` | 46,189,382 | READY | other (not_all_pulses_detected,pulse_detection_incomplete) | - |
| B2-05 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d05` | `fc6e8fb3d3d69ef157407f0ecb565e6952e977e84f637c151c1edcfb402cf57f` | 45,105,819 | READY | valid | - |
| B2-06 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d06` | `c331b245c00a96c73c86938537e2129ddfa23cbc6aa7e23d0d3753e1b95e0b1b` | 45,272,229 | READY | other (not_all_pulses_detected,pulse_detection_incomplete) | - |
| B2-07 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d07` | `64fc21fb609d5baba98dc686dff12ab803b6294474639551f23fdb0a078257cd` | 45,211,108 | READY | valid | - |
| B2-08 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d08` | `29991b93c38691bdc45b57128206b1314077ed1b261394f5976556d0aebf3f22` | 45,360,920 | READY | other (not_all_pulses_detected,pulse_detection_incomplete) | - |
| B2-09 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d09` | `45731bb9943b9f29a3f3d6fc2175c7b66ad11987f88de1868fb79fb8f87d1cdb` | 44,223,275 | READY | valid | - |
| B2-10 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d10` | `d1da6a7eb082533b420c58a0dc0183298514febf06e857f0e5c9a3413c7dd2af` | 44,337,316 | READY | other (not_all_pulses_detected,pulse_detection_incomplete) | - |
| B2-11 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d11` | `150e6e9b1c0b04a440a2b9b63f858fd92a8f0e4f858b512ab7d627ced71b82a3` | 44,372,068 | READY | valid | - |
| B2-12 | `/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d12` | `748018ce72e41600464dcb9f2fddcc466e2e3c0ebfcf6474828d908239c36b7b` | 43,909,331 | READY | valid | - |

### C. Sizing set - the 40 unique protocol-v3 bundles named in the August sweep record (shakedown 20260818T045736-4d9e9db9 included)

| # | capture directory | content id | raw bytes (hash-verified) | status | recorded disposition | recorded cells | sweep-record result (Aug, older alignment) | sweep-record cells |
|---|---|---|---:|---|---|---:|---|---:|
| C-01 | `/Users/edr/code/JouleWise/runs_window_a_20260722/instrument_validation/20260722T145535-e941c821` | `c2a4412ee77fd2c10a397c8c4072d06c31bf26ea6b6a9a2ad1764dced71de2e9` | 87,774,105 | READY | valid | - | 59/59 | 117669 |
| C-02 | `/Users/edr/code/JouleWise/runs_window_a2_20260722/instrument_validation/20260722T194118-9dc0749d` | `029a412be038ce88428ff1e8d302d90f2020e5cb0179ef4a750613fffc51f8ee` | 87,498,518 | READY | valid | - | 59/59 | 122431 |
| C-03 | `/Users/edr/code/JouleWise/runs/instrument_validation/20260722T213749-563b9849` | `ec850ad5359df234cf091b452194753acbd609f8c5102443fca8cfb40b3c72aa` | 87,314,873 | READY | clock (clock_anchor_unresolved) | - | anchor unresolved | — |
| C-04 | `/Users/edr/code/JouleWise/runs_window_a3_20260722/instrument_validation/20260722T214220-1acdbbc0` | `7232cfa1de9e6e19543d00c976e184ee23f8e4a17d2b05f7f4fa44fc6461f01f` | 87,257,591 | READY | valid | - | 59/59 | 119273 |
| C-05 | `/Users/edr/code/JouleWise/runs_window_a4_20260722/instrument_validation/20260722T215127-eeef661a` | `7d7e898178e7fac74d9733a6703319d3458785abb671a2d43907a1018549f554` | 87,334,240 | READY | valid | - | 59/59 | 119631 |
| C-06 | `/Users/edr/code/JouleWise/runs_window_a4_20260722/instrument_validation/20260722T222332-901c5c13` | `273e6326b8a43c4b97d2d9437cee84320488dc5857cf3bd663e916c53601f02f` | 87,235,803 | READY | valid | - | 59/59 | 123575 |
| C-07 | `/Users/edr/code/JouleWise/runs_window_a5_20260723/instrument_validation/20260722T232509-82642517` | `5092d2cd9912f5dd0fa79161e86e7eb07c0196f61585a0770500a27be46df55c` | 87,228,271 | READY | valid | - | 59/59 | 122023 |
| C-08 | `/Users/edr/code/JouleWise/runs_window_a5_20260723/instrument_validation/20260723T023058-8732d1c9` | `08ea40cb06c6290ad056a698a0803e4dbfc4591203121f4524169e380d8fc7fa` | 87,746,426 | READY | valid | - | 59/59 | 122313 |
| C-09 | `/Users/edr/code/JouleWise/runs_window_a5_20260723/instrument_validation/20260723T052051-d9358c8a` | `eac62f5e4fa7600afbb6d822b6770e25513ae79e00a5e2ad12c0e89cfb205df1` | 87,252,845 | READY | valid | - | 59/59 | 121811 |
| C-10 | `/Users/edr/code/JouleWise/runs_window_a6_20260723/instrument_validation/20260723T183306-4ce692b4` | `c75a8d727664c28ff3bbce88eab6e4065e00bc965f2f447fb2a41df488faa9fd` | 87,387,711 | READY | valid | - | 59/59 | 116173 |
| C-11 | `/Users/edr/code/JouleWise/runs_window_a6_20260723/instrument_validation/20260723T194632-d04e038e` | `0c5851939bac8e93973dbf8464e7c053ce4b1da0a708efa062a80d169004e6d9` | 87,220,854 | READY | valid | - | 59/59 | 128607 |
| C-12 | `/Users/edr/code/JouleWise/runs_window_a7_20260723/instrument_validation/20260723T195730-bc4ba14a` | `2ae2573af972e9c9b3fbe0aa98d57d265056b58902b35eb5995925fa10c1fbe8` | 87,480,438 | READY | valid | - | 59/59 | 121443 |
| C-13 | `/Users/edr/code/JouleWise/runs_window_a7_20260723/instrument_validation/20260723T221449-e9ae755e` | `418db55fa63dd5a0bae1ebb2291d860748df350d1b94aae4645d858c0527741c` | 86,892,434 | READY | valid | - | 59/59 | 117043 |
| C-14 | `/Users/edr/code/JouleWise/runs_window_a8_20260723/instrument_validation/20260723T223406-314f6d9e` | `f3db4bc343a25c25734a017a02089ddc15db5169d67b222356d5a6fc09e143e4` | 87,353,243 | READY | valid | - | 59/59 | 124447 |
| C-15 | `/Users/edr/code/JouleWise/runs_window_a8_20260723/instrument_validation/20260724T014109-57844352` | `35ae646c47747e8561982ec8a7128e2e1a84e5c3255de66ee18ba51415017dc3` | 87,270,101 | READY | valid | - | 59/59 | 137189 |
| C-16 | `/Users/edr/code/JouleWise/runs_window_a9_20260724/instrument_validation/20260725T005132-a64711b7` | `bf7c217c20effafa210cb53e86db0e6743df4e5eafca779d79ae0e8073c8f7b3` | 86,371,900 | READY | valid | - | 59/59 | 119891 |
| C-17 | `/Users/edr/code/JouleWise/runs_window_a9_20260724/instrument_validation/20260725T011533-0b5ec77c` | `10fe0bff822d2c2546f2cbc45d85e9fb46cbd739dc4a972585775a2e2f29a0ec` | 87,027,099 | READY | valid | - | 59/59 | 119055 |
| C-18 | `/Users/edr/code/JouleWise/runs_window_a9_20260724/instrument_validation/20260725T022712-0a9534f5` | `ff6de7a0496f834973007f3c355b3c2dd3bd37e9701b632b049904f134f52e00` | 87,293,622 | READY | valid | - | 59/59 | 119479 |
| C-19 | `/Users/edr/code/JouleWise/runs_window_a10_20260725/instrument_validation/20260725T030533-d3f076e5` | `51f24f06cc5d99a58fc354423f4b08b03dfe5c2e8ece4ea148967896802cb984` | 87,549,490 | READY | valid | - | 59/59 | 122065 |
| C-20 | `/Users/edr/code/JouleWise/runs_window_a10_20260725/instrument_validation/20260725T055825-b10cb348` | `1ef9ce6167865f3e04304b73ada774e11515b3895a5b51d5c1d8b7eb18af9aea` | 87,071,431 | READY | clock (clock_anchor_unresolved) | - | anchor unresolved | — |
| C-21 | `/Users/edr/code/JouleWise/runs_window_a10_20260725/instrument_validation/20260725T060617-97c5cba6` | `ac89c0d106fdf4aff146f11f77c95dea4682d35d71e6c3582c9169772149acc9` | 87,432,988 | READY | valid | - | 59/59 | 117563 |
| C-22 | `/Users/edr/code/JouleWise/runs_window_b_20260726/instrument_validation/20260726T000039-491995f3` | `03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710` | 86,816,875 | RAW_IN_ICLOUD_LOCAL (raw: `/Users/edr/JouleWise-window-custody/ed-qual-20260817/decisive-replay-work/store/03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710/raw/powermetrics.plist`; alternates: `/Users/edr/JouleWise-window-custody/ed-qual-20260817/decisive-replay-work2/store/03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710/raw/powermetrics.plist`; `/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/window_b_20260726/instrument_validation/20260726T000039-491995f3/raw/powermetrics.plist`) | valid | - | 59/59 | 123267 |
| C-23 | `/Users/edr/code/JouleWise/runs_window_b_20260726/instrument_validation/20260726T031222-e0ce33f5` | `20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb` | 86,623,043 | RAW_IN_ICLOUD_LOCAL (raw: `/Users/edr/JouleWise-window-custody/ed-qual-20260817/decisive-replay-work/store/20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb/raw/powermetrics.plist`; alternates: `/Users/edr/JouleWise-window-custody/ed-qual-20260817/decisive-replay-work2/store/20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb/raw/powermetrics.plist`; `/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/window_b_20260726/instrument_validation/20260726T031222-e0ce33f5/raw/powermetrics.plist`) | valid | - | 59/59 | 122947 |
| C-24 | `/Users/edr/code/JouleWise/runs_window_c_20260726/instrument_validation/20260726T225227-1f550773` | `ce9373a047879fbf94c30d5119b2735ca6a9b9f16ddb460f8310f8654642b96b` | 87,181,087 | READY | clock (clock_anchor_unresolved) | - | anchor unresolved | — |
| C-25 | `/Users/edr/code/JouleWise/runs_window_c_20260726/instrument_validation/20260726T225920-ab4272f5` | `8872864d1c97f40987dab4d693479fee6405c8616ea1effdf2a0457c10f5a8f8` | 87,187,101 | READY | valid | - | 59/59 | 115197 |
| C-26 | `/Users/edr/code/JouleWise/runs_window_c_20260726/instrument_validation/20260727T015824-45feb516` | `03497b300c7d35bd6fe08855dc468687e788f81481ab7285b04fa726a202d440` | 86,979,055 | READY | valid | - | 59/59 | 133883 |
| C-27 | `/Users/edr/code/JouleWise/runs_window_d_20260726/instrument_validation/20260727T020611-4a409a30` | `51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca` | 87,322,360 | RAW_IN_ICLOUD_LOCAL (raw: `/Users/edr/JouleWise-window-custody/ed-qual-20260817/decisive-replay-work/store/51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca/raw/powermetrics.plist`; alternates: `/Users/edr/JouleWise-window-custody/ed-qual-20260817/decisive-replay-work2/store/51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca/raw/powermetrics.plist`; `/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/window_d_20260726/instrument_validation/20260727T020611-4a409a30/raw/powermetrics.plist`) | valid | - | 59/59 | 126103 |
| C-28 | `/Users/edr/code/JouleWise/runs_window_d_20260726/instrument_validation/20260727T050047-95e2f87e` | `20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37` | 87,081,750 | RAW_IN_ICLOUD_LOCAL (raw: `/Users/edr/JouleWise-window-custody/ed-qual-20260817/decisive-replay-work/store/20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37/raw/powermetrics.plist`; alternates: `/Users/edr/JouleWise-window-custody/ed-qual-20260817/decisive-replay-work2/store/20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37/raw/powermetrics.plist`; `/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/window_d_20260726/instrument_validation/20260727T050047-95e2f87e/raw/powermetrics.plist`) | valid | - | 59/59 | 120551 |
| C-29 | `/Users/edr/code/JouleWise/runs_window_7bfloor_20260729/instrument_validation/20260729T204105-39d25f8a` | `7410aafd9448b8da07e4b919e324b24bc7b15ac9b01a3200e39ef6f615cadfc3` | 87,299,324 | READY | valid | - | 59/59 | 129965 |
| C-30 | `/Users/edr/code/JouleWise/runs_window_7bfloor_20260729/instrument_validation/20260730T014035-124df355` | `4451d9a9cd5c6b5a801d146908b549886bd11559fc4c2ee3e771434fb4b95bd9` | 87,189,898 | READY | valid | - | 59/59 | 135513 |
| C-31 | `/Users/edr/code/JouleWise/runs_window_contrast_20260730/instrument_validation/20260730T210703-f76b5771` | `6026cb9f72b5a76f2a4b5b4f88bde06d644e3cd47e4e0cdc11d44ab6ecf5fabf` | 86,927,272 | READY | valid | - | 59/59 | 112205 |
| C-32 | `/Users/edr/code/JouleWise/runs_window_contrast_20260730/instrument_validation/20260731T012210-374020b6` | `e522d8fabdebaa446776c52f8c263be6d853b700107d21c835557be475b165c2` | 87,131,446 | READY | valid | - | 59/59 | 122117 |
| C-33 | `/Users/edr/code/JouleWise/runs_window_metrologyA_20260731/instrument_validation/20260731T161713-b8b08280` | `bd170c828910f4543f60ee76fae1f04b10707c58cd907be4c707706faea78aae` | 87,121,550 | READY | valid | - | 59/59 | 131065 |
| C-34 | `/Users/edr/code/JouleWise/runs_window_metrologyA_20260731/instrument_validation/20260731T214355-126fc2ab` | `ff49477c8c7d71df3a9b7f86681e436ede8b7c1ac8c2b3fb2ee745cd6421ada1` | 87,442,497 | READY | clock (clock_anchor_unresolved) | - | anchor unresolved | — |
| C-35 | `/Users/edr/code/JouleWise/runs_window_metrologyA_20260731/instrument_validation/20260731T215120-fa1e9cda` | `45a676d1f9f75c8817bbcf2e97c07171adb04bc4a0d2aa742c3b894a394a990d` | 87,842,690 | READY | valid | - | 59/59 | 117057 |
| C-36 | `/Users/edr/code/JouleWise/runs_window_metrologyB_20260801/instrument_validation/20260801T010113-e859f3aa` | `473a8aec1aba846e270ddccaa6bbea5b315cd36f28616e2daff2d7edefe52518` | 87,278,253 | READY | clock (clock_anchor_unresolved) | - | anchor unresolved | — |
| C-37 | `/Users/edr/code/JouleWise/runs_window_metrologyB_20260801/instrument_validation/20260801T010805-ff3fdc88` | `9add6b6926ef2eb45722cfcdc8562a643dba0fd43f045ae534419fc7a7ecfd21` | 87,017,149 | READY | clock (clock_anchor_unresolved) | - | anchor unresolved | — |
| C-38 | `/Users/edr/code/JouleWise/runs_window_metrologyB_20260801/instrument_validation/20260801T014059-8c3bfe9e` | `ea0c34c63f1c9bed2649081eab80a3fbaf5c4ffd1ea37da12bc11945053aefca` | 87,428,332 | READY | valid | - | 59/59 | 132861 |
| C-39 | `/Users/edr/code/JouleWise/runs_window_metrologyB_20260801/instrument_validation/20260801T064830-c76f5d1c` | `ef01bcca6caf35f7abea2dcaa7acf8cc53d5a9e3463c413dba61d17f9179c448` | 87,384,231 | READY | valid | - | 59/59 | 119223 |
| C-40 | `/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/instrument_validation/20260818T045736-4d9e9db9` | `821b9042731d1c22e52758a402d81215379110a85fbf8804eccb3a7615d8e069` | 91,664,519 | READY | cap stop (detection_nonconvergent / evaluated_cell_budget) | 100,000 | 59/59 | 124029 |

### D1. Check set - the nine other 2026-08-18 captures (three shakedown validations, six spacing probes; probe a7e8b412 is the last row)

| # | capture directory | content id | raw bytes (hash-verified) | status | recorded disposition | recorded cells |
|---|---|---|---:|---|---|---:|
| D1-01 | `/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/instrument_validation/20260818T163440-8eab7b5a` | `f30687dbf5adddd14ef62178d66581f51aed7a7533342aede7b205cac077ec3c` | 91,775,728 | READY | valid | - |
| D1-02 | `/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/instrument_validation/20260818T165057-81acfefe` | `476b8dbf68a06b08a0279d2ea516fc505651e1e1a7c9bee3865ec4b32f43caf4` | 91,550,753 | READY | valid | - |
| D1-03 | `/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/instrument_validation/20260818T165459-f22b25aa` | `098d8fa23a5f7b51bc95c8fea20b172bcae8c0e9bd0ccbdb3af4265393c03988` | 91,580,769 | READY | valid | - |
| D1-04 | `/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/spacing_probe/20260818T173136-bc9bff8e` | `3b0204a10ab973e04063e1bc3bde38cdeb69a8a7fc243234487c28a012c72f3b` | 91,481,772 | READY | clock (clock_anchor_unresolved) | 0 |
| D1-05 | `/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/spacing_probe/20260818T173559-b192892b` | `c8858a53c05768c663a0071465e77c0dbeeeab769056b07852ad767e9623b49f` | 91,606,368 | READY | clock (clock_anchor_unresolved) | 0 |
| D1-06 | `/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/spacing_probe/20260818T175421-912e9ed4` | `1203d136bcabdb76e1e1ecf0b279dff3e484a93edb72ecadd648fd59960bd35d` | 91,722,826 | READY | valid | - |
| D1-07 | `/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/spacing_probe/20260818T175854-918be2ce` | `5945a7b84b9ffac671f241346d4fe7b963f25ab5821900ff8d72640e8eb9ab52` | 91,512,360 | READY | clock (clock_anchor_unresolved) | 0 |
| D1-08 | `/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/spacing_probe/20260818T181717-4bae4cd2` | `0d98646e91fa63b55056490c342b42ae95a3e6c5f4672d6ef00a7fce7f63d044` | 91,668,229 | READY | valid | - |
| D1-09 | `/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/spacing_probe/20260818T182149-a7e8b412` | `7aeba46a8eb11e9cfd0fb541c01547bb1ae7c020a3f00cd9044008db1d3fb5f5` | 91,628,714 | READY | clock (clock_anchor_unresolved) | 0 |

### D2. Check set - three window-c quarantine validation captures (attempts 1-3, 2026-07-26/27)

| # | capture directory | content id | raw bytes (hash-verified) | status | recorded disposition | recorded cells |
|---|---|---|---:|---|---|---:|
| D2-01 | `/Users/edr/JouleWise-window-custody/window_c_20260726/quarantine/attempt1-clock-anchor-20260726T113500Z/runs_window_c_20260726/instrument_validation/20260726T032104-68077be5` | `568255fb8e127c33fb4d844ee551acf7c7ff7be67e1a7d05c823f9973612dabd` | 87,119,226 | READY | valid | - |
| D2-02 | `/Users/edr/JouleWise-window-custody/window_c_20260726/quarantine/attempt2-clock-anchor-r11-20260727T010928Z/runs_window_c_20260726/instrument_validation/20260726T043835-d5a2fec7` | `58ccfe6ba7da98e61dde4729dfed2c138e71d29760882ab58afa5974753ebb78` | 87,455,035 | READY | valid | - |
| D2-03 | `/Users/edr/JouleWise-window-custody/window_c_20260726/quarantine/attempt3-xprotect-20260727T053447Z/runs_window_c_20260726/instrument_validation/20260726T222513-20308e1b` | `6c2f867562c048614588f83ff5743cef09f5a76b6f9ef03de1db671857f8065a` | 86,678,898 | READY | valid | - |

## 5. Commands for the orchestrator

Run from a checkout that contains the committed harness, on a quiet machine, one batch at a time (sequential; a replay can take minutes and the rule fixes the deadline at 3,600 s, so do not start a replay while another agent session is active). The batches are ordered so the sizing set comes first and the check set last. Batches 01-14 and 19-21 hold READY captures (raw inside the capture directory, no override); batches 15-18 are the four RAW_IN_ICLOUD_LOCAL captures, one per command, with `--raw-powermetrics`.

```
cd /Users/edr/code/<checkout-holding-the-committed-harness>
```

Batch 01 (A1, READY captures 1-6 of 12):

```
python3 -B scripts/cap_replay_harness.py SIZING \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d01" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d02" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d03" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d04" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d05" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d06"
```

Batch 02 (A1, READY captures 7-12 of 12):

```
python3 -B scripts/cap_replay_harness.py SIZING \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d07" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d08" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d09" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d10" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d11" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d12"
```

Batch 03 (A2, READY captures 1-6 of 12):

```
python3 -B scripts/cap_replay_harness.py SIZING \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d01" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d02" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d03" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d04" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d05" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d06"
```

Batch 04 (A2, READY captures 7-12 of 12):

```
python3 -B scripts/cap_replay_harness.py SIZING \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d07" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d08" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d09" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d10" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d11" \
  "/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d12"
```

Batch 05 (B1, READY captures 1-6 of 12):

```
python3 -B scripts/cap_replay_harness.py SIZING \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d01" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d02" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d03" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d04" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d05" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d06"
```

Batch 06 (B1, READY captures 7-12 of 12):

```
python3 -B scripts/cap_replay_harness.py SIZING \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d07" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d08" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d09" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d10" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d11" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d12"
```

Batch 07 (B2, READY captures 1-6 of 12):

```
python3 -B scripts/cap_replay_harness.py SIZING \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d01" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d02" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d03" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d04" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d05" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d06"
```

Batch 08 (B2, READY captures 7-12 of 12):

```
python3 -B scripts/cap_replay_harness.py SIZING \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d07" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d08" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d09" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d10" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d11" \
  "/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n2-20260919-d12"
```

Batch 09 (C, READY captures 1-6 of 36):

```
python3 -B scripts/cap_replay_harness.py SIZING \
  "/Users/edr/code/JouleWise/runs_window_a_20260722/instrument_validation/20260722T145535-e941c821" \
  "/Users/edr/code/JouleWise/runs_window_a2_20260722/instrument_validation/20260722T194118-9dc0749d" \
  "/Users/edr/code/JouleWise/runs/instrument_validation/20260722T213749-563b9849" \
  "/Users/edr/code/JouleWise/runs_window_a3_20260722/instrument_validation/20260722T214220-1acdbbc0" \
  "/Users/edr/code/JouleWise/runs_window_a4_20260722/instrument_validation/20260722T215127-eeef661a" \
  "/Users/edr/code/JouleWise/runs_window_a4_20260722/instrument_validation/20260722T222332-901c5c13"
```

Batch 10 (C, READY captures 7-12 of 36):

```
python3 -B scripts/cap_replay_harness.py SIZING \
  "/Users/edr/code/JouleWise/runs_window_a5_20260723/instrument_validation/20260722T232509-82642517" \
  "/Users/edr/code/JouleWise/runs_window_a5_20260723/instrument_validation/20260723T023058-8732d1c9" \
  "/Users/edr/code/JouleWise/runs_window_a5_20260723/instrument_validation/20260723T052051-d9358c8a" \
  "/Users/edr/code/JouleWise/runs_window_a6_20260723/instrument_validation/20260723T183306-4ce692b4" \
  "/Users/edr/code/JouleWise/runs_window_a6_20260723/instrument_validation/20260723T194632-d04e038e" \
  "/Users/edr/code/JouleWise/runs_window_a7_20260723/instrument_validation/20260723T195730-bc4ba14a"
```

Batch 11 (C, READY captures 13-18 of 36):

```
python3 -B scripts/cap_replay_harness.py SIZING \
  "/Users/edr/code/JouleWise/runs_window_a7_20260723/instrument_validation/20260723T221449-e9ae755e" \
  "/Users/edr/code/JouleWise/runs_window_a8_20260723/instrument_validation/20260723T223406-314f6d9e" \
  "/Users/edr/code/JouleWise/runs_window_a8_20260723/instrument_validation/20260724T014109-57844352" \
  "/Users/edr/code/JouleWise/runs_window_a9_20260724/instrument_validation/20260725T005132-a64711b7" \
  "/Users/edr/code/JouleWise/runs_window_a9_20260724/instrument_validation/20260725T011533-0b5ec77c" \
  "/Users/edr/code/JouleWise/runs_window_a9_20260724/instrument_validation/20260725T022712-0a9534f5"
```

Batch 12 (C, READY captures 19-24 of 36):

```
python3 -B scripts/cap_replay_harness.py SIZING \
  "/Users/edr/code/JouleWise/runs_window_a10_20260725/instrument_validation/20260725T030533-d3f076e5" \
  "/Users/edr/code/JouleWise/runs_window_a10_20260725/instrument_validation/20260725T055825-b10cb348" \
  "/Users/edr/code/JouleWise/runs_window_a10_20260725/instrument_validation/20260725T060617-97c5cba6" \
  "/Users/edr/code/JouleWise/runs_window_c_20260726/instrument_validation/20260726T225227-1f550773" \
  "/Users/edr/code/JouleWise/runs_window_c_20260726/instrument_validation/20260726T225920-ab4272f5" \
  "/Users/edr/code/JouleWise/runs_window_c_20260726/instrument_validation/20260727T015824-45feb516"
```

Batch 13 (C, READY captures 25-30 of 36):

```
python3 -B scripts/cap_replay_harness.py SIZING \
  "/Users/edr/code/JouleWise/runs_window_7bfloor_20260729/instrument_validation/20260729T204105-39d25f8a" \
  "/Users/edr/code/JouleWise/runs_window_7bfloor_20260729/instrument_validation/20260730T014035-124df355" \
  "/Users/edr/code/JouleWise/runs_window_contrast_20260730/instrument_validation/20260730T210703-f76b5771" \
  "/Users/edr/code/JouleWise/runs_window_contrast_20260730/instrument_validation/20260731T012210-374020b6" \
  "/Users/edr/code/JouleWise/runs_window_metrologyA_20260731/instrument_validation/20260731T161713-b8b08280" \
  "/Users/edr/code/JouleWise/runs_window_metrologyA_20260731/instrument_validation/20260731T214355-126fc2ab"
```

Batch 14 (C, READY captures 31-36 of 36):

```
python3 -B scripts/cap_replay_harness.py SIZING \
  "/Users/edr/code/JouleWise/runs_window_metrologyA_20260731/instrument_validation/20260731T215120-fa1e9cda" \
  "/Users/edr/code/JouleWise/runs_window_metrologyB_20260801/instrument_validation/20260801T010113-e859f3aa" \
  "/Users/edr/code/JouleWise/runs_window_metrologyB_20260801/instrument_validation/20260801T010805-ff3fdc88" \
  "/Users/edr/code/JouleWise/runs_window_metrologyB_20260801/instrument_validation/20260801T014059-8c3bfe9e" \
  "/Users/edr/code/JouleWise/runs_window_metrologyB_20260801/instrument_validation/20260801T064830-c76f5d1c" \
  "/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/instrument_validation/20260818T045736-4d9e9db9"
```

Batch 15 (C, single capture 20260726T000039-491995f3, raw plist supplied explicitly):

```
python3 -B scripts/cap_replay_harness.py SIZING "/Users/edr/code/JouleWise/runs_window_b_20260726/instrument_validation/20260726T000039-491995f3" --raw-powermetrics "/Users/edr/JouleWise-window-custody/ed-qual-20260817/decisive-replay-work/store/03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710/raw/powermetrics.plist"
```

Batch 16 (C, single capture 20260726T031222-e0ce33f5, raw plist supplied explicitly):

```
python3 -B scripts/cap_replay_harness.py SIZING "/Users/edr/code/JouleWise/runs_window_b_20260726/instrument_validation/20260726T031222-e0ce33f5" --raw-powermetrics "/Users/edr/JouleWise-window-custody/ed-qual-20260817/decisive-replay-work/store/20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb/raw/powermetrics.plist"
```

Batch 17 (C, single capture 20260727T020611-4a409a30, raw plist supplied explicitly):

```
python3 -B scripts/cap_replay_harness.py SIZING "/Users/edr/code/JouleWise/runs_window_d_20260726/instrument_validation/20260727T020611-4a409a30" --raw-powermetrics "/Users/edr/JouleWise-window-custody/ed-qual-20260817/decisive-replay-work/store/51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca/raw/powermetrics.plist"
```

Batch 18 (C, single capture 20260727T050047-95e2f87e, raw plist supplied explicitly):

```
python3 -B scripts/cap_replay_harness.py SIZING "/Users/edr/code/JouleWise/runs_window_d_20260726/instrument_validation/20260727T050047-95e2f87e" --raw-powermetrics "/Users/edr/JouleWise-window-custody/ed-qual-20260817/decisive-replay-work/store/20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37/raw/powermetrics.plist"
```

Batch 19 (D1, READY captures 1-6 of 9):

```
python3 -B scripts/cap_replay_harness.py SIZING \
  "/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/instrument_validation/20260818T163440-8eab7b5a" \
  "/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/instrument_validation/20260818T165057-81acfefe" \
  "/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/instrument_validation/20260818T165459-f22b25aa" \
  "/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/spacing_probe/20260818T173136-bc9bff8e" \
  "/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/spacing_probe/20260818T173559-b192892b" \
  "/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/spacing_probe/20260818T175421-912e9ed4"
```

Batch 20 (D1, READY captures 7-9 of 9):

```
python3 -B scripts/cap_replay_harness.py SIZING \
  "/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/spacing_probe/20260818T175854-918be2ce" \
  "/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/spacing_probe/20260818T181717-4bae4cd2" \
  "/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/spacing_probe/20260818T182149-a7e8b412"
```

Batch 21 (D2, READY captures 1-3 of 3):

```
python3 -B scripts/cap_replay_harness.py SIZING \
  "/Users/edr/JouleWise-window-custody/window_c_20260726/quarantine/attempt1-clock-anchor-20260726T113500Z/runs_window_c_20260726/instrument_validation/20260726T032104-68077be5" \
  "/Users/edr/JouleWise-window-custody/window_c_20260726/quarantine/attempt2-clock-anchor-r11-20260727T010928Z/runs_window_c_20260726/instrument_validation/20260726T043835-d5a2fec7" \
  "/Users/edr/JouleWise-window-custody/window_c_20260726/quarantine/attempt3-xprotect-20260727T053447Z/runs_window_c_20260726/instrument_validation/20260726T222513-20308e1b"
```

Template for a single capture whose raw plist lives elsewhere (one capture per invocation; the iCloud archive path pattern is `/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/<archive>/runs/instrument_validation/<id>/raw/powermetrics.plist`, usable only while the file is not dataless),

```
python3 -B scripts/cap_replay_harness.py SIZING <capture-dir-with-manifest-and-evidence> --raw-powermetrics "<raw plist path>"
```

Report mode (stated by R0/R8 for windows; not part of this roster run) takes the same directories under the harness's report subcommand.

Commands: 21 in total (READY batches of up to 6 captures, then the single-capture override commands).
