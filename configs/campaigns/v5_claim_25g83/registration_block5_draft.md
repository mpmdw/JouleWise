# Registration V5-CLAIM-25G83-B5: the first claim-bearing `_v5` windows (measurement block 5)

Status: **DRAFT UNSEALED, 2026-10-05.** Written by an Opus 5.5 design seat for the lead, on branch
`design/2026-10-05-v5-claim-block-draft`, based on the block-4 design head `4fc184bd`. This file
authorizes no arm, no launch and no analysis. It becomes binding only when a cold gate seals it together
with its companion analysis plan `configs/campaigns/v5_claim_25g83/analysis_plan_block5_draft.md`
(§13). Until block 4 qualifies, every clause that depends on a block-4 outcome is an explicit
`FILL[...]`. A **FILL** is a value that must be bound from authenticated bytes before the due point named
in §14; it is never a default, and an arm with an unresolved FILL due at or before that arm refuses.
No claim-eligible `_v5` energy data exists at this writing, and none was read (§16).

## 0. Terms, built in the order they are used

The machine is one Apple M3 Max laptop (model identifier Mac15,9) running macOS build 25G83 on mains
power. Everything below happens on that one machine.

- **Sampler.** macOS `powermetrics`, which writes one power record every 100 ms. Each record states the
  average power of the processor rails over its 100 ms.
- **Member.** One run of one inference request in its own process: idle baseline, warm-up, the measured
  request, cleanup, then the **reducer** (the program that turns the raw power records and event
  timestamps into a summary of energies). Its files form one immutable directory, the **bundle**. A member's **sampler stream** is the one continuous `powermetrics` recording that runs
  from just before its idle baseline to just after its measured request.
- **Phase.** A named part of the measured request: **prefill** (the model reads the whole prompt,
  ending at the first output token) and **decode** (the model writes the remaining output tokens). A
  member's **phase energy** is the energy the reducer assigns to that phase from the power records
  that overlap it in time (gross energy: no idle power is subtracted).
- **Prompt length L.** The prefill workload uses a prompt of exactly L = 2048 tokens. L was selected
  by block 3 (`selection.json`, SHA-256 `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222`)
  as the shortest of 512/1024/2048/4096 at which every small-model probe member's prefill overlapped at
  least five power records. The decode workload uses the real prompt 0 of `real_prompts_v1`, rendered
  through the Qwen3 chat template with thinking off; its prefill is 42 tokens long (the **p42** phase),
  and decode is forced to exactly 512 output tokens with greedy decoding (D-166 and its 2026-09-04
  addendum).
- **Stage.** One ordered list of members that `scripts/run_campaign.py` runs as a unit. Every stage
  starts with a 180 s **settle** (the chain sleeps so the machine returns to idle; runbook `SETTLE_S`).
- **Pack.** The frozen, hash-pinned set of stages, configurations and plans for one window. Three
  packs exist (PR #477, branch `origin/desk/2026-10-04-v5-pin-and-packs`, head `db41703c`):
  **ALPHA** `d117_floor_qwen3-1p7b_v5` (Qwen3-1.7B, 4-bit), **BETA** `d117_floor_qwen3-8b_v5`
  (Qwen3-8B, 4-bit) and **GAMMA** `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` (both models).
- **A/B/B/A block.** Four consecutive members in the order A1, B1, B2, A2. In GAMMA, A is Qwen3-1.7B and
  B is Qwen3-8B, so the block compares the models while cancelling a slow linear drift (A's members sit
  at both ends); the 8B-minus-1.7B difference in a phase energy, estimated over GAMMA's blocks, is a
  **contrast**. In ALPHA and BETA, A and B are the *same* model and workload: a **null block**, whose
  apparent A-versus-B difference can only come from the instrument and the machine.
- **Absolute repeat.** One member run on its own (not in a block), ten in a row per workload.
- **Independence unit.** A group of members treated as one independent draw. Consecutive members share
  slow drifts (temperature, background load), so the four members of a block are one unit, and each
  absolute repeat is one unit. D-179 fixes 20 units per reported cell: 10 repeats plus 10 blocks.
- **Reported cell.** One registered energy number per model and phase, computed over a fixed ordered
  list of exactly 50 members (10 absolute repeats + the 40 members of 10 null blocks): three per floor
  pack, six in all (`d117-reported-mean-ph-{decode,prefill-p42,prefill-p2048}-{qwen3-1p7b,qwen3-8b}`).
- **Floor.** The smallest apparent effect the instrument can produce when nothing differs, measured
  from the null blocks and absolute repeats; a **mint** is the authenticated issuance of the floor
  artifact (`joulewise.detection_floor_artifact.v2`). A contrast that does not exceed its floor is
  reported as not resolvable.
- **Pulse calibration.** A capture in which the GPU is switched on and off 59 times on a commanded
  schedule, so the sampler's timing error can be measured; the result is its **fiducial bound**. The
  **pre** and **post** calibrations enclose a window; together they are its **bracket**. The
  **acceptance** (`d079_calibration_acceptance_v2_n24_25g83_r2`) is the issued file that says which
  calibration results are in family and how far pre and post may drift apart. The **ledger** is the
  append-only record of every calibration capture; its committed head is the **ledger pin**. The
  acceptance was derived from the ledger up to sequence 376, its **cutoff**; brackets are judged
  against that cutoff, while the live ledger keeps growing.
- **References.** Members of one fixed reference workload (Qwen2.5-1.5B, 1024-token prompt, 256 output
  tokens). Twelve at the start of a window form the **NEG-8 bound corpus**, from which the window's
  drift bound is derived; the **start triplet**, the interior references and the **end triplet** are
  later repeats whose energy drift across the window is checked against that bound.
- **Whole-window verdict.** One row, written after collection, stating whether the window as a whole
  passed: every member admitted, the AC adapter's reported wattage unchanged throughout, CPU admission held, the reference drift
  inside the NEG-8 bound, and the bracket bound to the window (`joulewise/whole_window.py`).
- **Idle admission.** Before each member's request, its idle baseline (30 s in `_v5` configs) must show
  a quiet machine (production policy: CPU busy ratio p95 ≤ 0.5 over ≥ 30 records, processor combined
  power p95 ≤ 1.0 W, GPU idle, displays asleep, AC, thermal nominal). One retry follows immediately;
  a second rejection aborts the member. In a claim window an aborted member aborts the whole window
  (pack attempt policy `abort_window_on_any_required_member_failure`, zero replacements).
- **Clock anchor.** The sampler stamps its own records; the clock anchor is the offset that places those
  stamps on the machine's clocks, found as the set of offsets consistent with every record of the
  stream. Its **effective bound** is the half-width h of that set plus the span by which the wall clock
  and the monotonic clock drift apart over the stream. A member is valid only when that bound is at most
  5 ms (`uncertainty_evidence.clock_anchor.status` equal to `bounded`).
- **Network-time OFF receipt.** A write-once record that automatic network time was off (setter exit 0,
  standard output `setUsingNetworkTime: Off` or `Network Time is already off`). Network time stays off
  for the whole block; nothing turns it on (D-186).
- **Battery float.** The battery neither charges nor discharges: `ExternalConnected=Yes`,
  `IsCharging=No`, signed `InstantAmperage` within ±200 mA, ioreg `UpdateTime` at most 180 s old
  (directive #421, block-4 §3 item 7).
- **Driver, T-0, ARM, GO, launch.** The **driver** (`scripts/run_night.py`) is the unattended program
  that arms, checks and launches a window. T-0 is a window's scheduled start, at which machine-authored
  evidence of the clock, quietness and battery is captured. **ARM** is the authenticated readiness
  receipt the driver authors before T-0; **GO** (`joulewise.pack_night_go_receipt.v1`) is its permission receipt,
  produced only after ARM verifies; the **launch** consumes the GO exactly once. An **authorization
  record** names the pack, attempt, permitted chain, purpose and claim eligibility (D-176 §2); claim
  windows use purpose `CAMPAIGN_TRANSACTION` and `claim_eligible=true`.
- **Chain.** The shell program the driver launches (`scripts/run_night.py run`); it runs the pack's
  stages in order. **Clean dwell**: after the OFF receipt the driver waits at least 600 s and at most
  2700 s for a quiet machine before the chain may start. `NIGHT_PROGRAMMED_SPAN_S` is the sum of the
  chain's planned durations and `WINDOW_MAX_S` the hard cap after which the driver stops a window; the
  chain may start no later than `t0 + WINDOW_MAX_S − NIGHT_PROGRAMMED_SPAN_S` (§5).
- **Harvest.** The desk program run after a window: it archives the window's bytes, authenticates them
  and writes one mechanical verdict (§7). **`s1`** is block 4's non-claim shakedown: one consuming
  launch of the real GAMMA pack that collects a single A/B/B/A block. **G3** is the fixed read-only desk
  checker, proved on `s1`, that must pass on every claim window's bytes before the next arm (D-162, row
  V5-NIGHTLY-G3-01).
- **H.** An exact git commit. **H_claim** is the commit whose code runs every window of this block (§12).
- **R3.** The standing route for a tooling fault: fix it in a reviewed, gated pull request, merge, then
  re-run the failed *desk* step on identical bytes. R3 never re-collects anything.
- **Consult.** One blind round from two seats (Sol 6.1 high and Opus 5.5), each licensed to disagree;
  the lead decides and records dissent. **Cold gate.** An independent adjudication of a named question by
  a seat with no prior involvement (judge), checked by a second independent seat (refuter).

## 1. Purpose, and what each window can support

Block 5 collects the three claim-bearing `_v5` windows. Their bytes are the only sources of the
`_v5` numbers the capstone paper can print: the reported phase energies of each model (D-179), the
floors (D-117/D-124), the dominance ratios (D-165/D-168) and the two model contrasts (GAMMA's frozen
prospective analysis manifest). The claims ladder (`docs/contracts/claims_ladder.md`) fixes the ceiling
of each. Its rungs: **L1** says a quantity was observed on this exact stack, boundary and workload;
**L2** says one condition differed from another within one boundary, with intervals reported and the
effect above the floor; L3 (a fitted model checked on held-out cells) and L4 (replicated across
machines or boundaries) are out of reach here. **Holm** is the correction that keeps the chance of any
false positive across the two contrasts at 5%. **R** is the factor by which a floor grows when phase
edges may move within their timing uncertainty, and **R_cm** the same factor under a shared-sign replay
(analysis plan §6); the **contingent subtitle** is the "attribution-limited" paper subtitle that D-165
licenses only when every required ratio passes.

| Window(s) | What it can support | Rung | Why not higher |
|---|---|---|---|
| ALPHA alone | Reported phase energy of Qwen3-1.7B for decode and prefill-p2048 (p42 computed and retained), each with its D-179 interval and runtime-observed J/token; the 1.7B floor cells | L1 instrument result | One stack, one boundary, no comparison |
| BETA alone | The same for Qwen3-8B | L1 | Same |
| ALPHA beside BETA | Side-by-side L1 cells only, labelled as collected in separate windows in a fixed order | L1 | The claims ladder keeps forced block order below L2; the two models were never interleaved |
| GAMMA with the ALPHA/BETA floors | Two primary contrasts (8B minus 1.7B phase energy, decode and prefill-p2048), Holm family of two | L2 comparative, if and only if the claim gate returns `direction_supported` with the registered positive direction and `claim_ready_for_l2_l3` | No held-out cells (L3) and no second machine (L4) |
| Floors + GAMMA | Dominance ratios R and R_cm; the dominance sentence and the contingent subtitle only if every required ratio is at least 2 | Disclosure (not a rung) | D-165 addendum: R_cm licenses no physical-common-time robustness claim |

Every phase-energy sentence carries the D-177 limitation (phase attribution was not characterized by
a measured instrument check). Nothing here supports a prompt-population claim (one fixed decode
prompt), a claim outside `M3 Max / MLX / powermetrics` (boundary label `FILL[BOUNDARY-LABEL]`), or a
claim about lengths other than 2048. What the paper prints, and from which artifact, is fixed in the
analysis plan §9; under the current D-174 fallback no `_v5` result has a paper placement, so printing
anything needs the placement ruling in §15 Q5.

## 2. Preconditions for the first claim arm

All must hold, each evidenced by a path and SHA-256, before the first ALPHA attempt (`ALPHA-1`, §3.1)
arms:

1. Block 4 qualified: `FILL[B4-STRUCTURAL-VERDICT]` and `FILL[B4-QUALIFICATION-VERDICT]` are both PASS
   on `s1` (or its allowed `s2`), harvested from authenticated archives.
2. The L10-A record is ratified (`proof_scope=L10_A_G2B_CONTRACT_PREFIX`: the desk proof, on `s1`'s
   bytes, that strict validation, reduction and the deliberately incomplete finalization behave exactly
   as registered): `FILL[L10-A-RATIFICATION-RECORD]`.
3. The liveness limitation Q110 is closed (the readiness evidence must be under 600 s old when it is
   judged; at least three real receipt bundles must all show that margin) or re-ruled by a cold gate
   before ALPHA: `FILL[Q110-CLOSURE]`.
4. H_claim is fixed and covered by block 4's qualification (§12): `FILL[H-CLAIM]`.
5. The launch-realization recheck (A6, PR #475: the check at launch that the bytes launched are the
   reviewed bytes) is present at H_claim: `FILL[A6-AT-H-CLAIM]`.
6. This registration and the analysis plan are sealed (§13): `FILL[B5-SEAL-RECORD]`.
7. The #416 pre-arm triple audit has run at H_claim and every verified BLOCKER is cleared (§10.1):
   `FILL[416-AUDIT-RECORD]`.
8. Every launch-path program a claim window executes is present at H_claim (§12.2):
   `FILL[CLAIM-LAUNCH-CODE-AT-H]`.
9. A `CAMPAIGN_TRANSACTION` authorization record exists for the attempt (D-176 §2; issued by the lead
   under D-171 §3 and Ed's 2026-10-05 ruling that owner-reserved steps are agent-run):
   `FILL[AUTH-<label>]`, with `permitted_blocks` per `FILL[CAMPAIGN-PERMITTED-BLOCKS]`.
10. The step-6 confirmation record for the pack family (`d117_step6_confirmation_table_v5.json`) is in
    transaction custody: `FILL[STEP6-RECORD]`.

## 3. Occurrences and schedule

### 3.1 Three windows, in a fixed order

| Label | Pack | Science members | Auxiliary members | Calibrations | Units it delivers |
|---|---|---:|---:|---:|---|
| `ALPHA-n` | ALPHA | 100: decode 10 absolute + 40 in 10 null blocks; prefill-p2048 10 + 40 | 12 NEG-8 + 3 start + 1 midpoint + 3 end = 19 | 2 | 20 units for each 1.7B reported cell (decode and p42 share the same 50 members; p2048 has its own 50) |
| `BETA-n` | BETA | 100, same shape | 19 | 2 | 20 units for each 8B reported cell |
| `GAMMA-n` | GAMMA | 80: decode 10 A/B/B/A blocks (40) then prefill-p2048 10 blocks (40) | 12 NEG-8 + 3 start + 3 interior (decode midpoint, arm boundary, prefill midpoint) + 3 end = 21 | 2 | 10 block differences for each of the two contrasts |

`n` is the attempt ordinal persisted in the plan (`attempt_id = "<plan_id>/<n>"`, pack GO contract
§8.2); the first attempt of each pack is `n = 1`. Each pack's stage order is its committed
`plan_tree.json` `stage_graph`, unchanged. All 20 units of a reported cell come from one window, and
no member, block or cell is ever pooled across attempts or windows, topped up or replaced (D-078).

The order is ALPHA, then BETA, then GAMMA, and a window arms only after the previous one is PASS (§7).
The order is fixed in advance so that no arming decision can depend on what an earlier window showed;
it is the D-117 order, it puts the floor windows (instrument characterization) before the contrast
that consumes them, and it lets the L10-B rehearsal mint (§3.3) test the floor path before GAMMA spends
a window.

### 3.2 Back-to-back cadence (one machine, physics-only waits)

Windows run back to back. The only waits are physical: the OFF receipt and its 600 s clean dwell,
battery float, recovered idle power, and the end of any backup upload (§4 item 8). Between windows the
desk steps below run; all agent seats exit by `t0 − 8 min` of the next window and none runs during a
window.

One floor window (ALPHA or BETA), left to right in time; GAMMA has the same frame with its four
20-member contrast stages and three interior references in place of D1–D3, mid and P1–P3:

```
 T-0                    chain start                                       captures end
  |                          |                                                  |
  [OFF][dwell][set][pre][NEG8][start][D1][D2][D3][mid][P1][P2][P3][end][post][verdict][backup] | desk gap | next T-0
```

Every element: `T-0` = scheduled start with its machine-authored evidence; `OFF` = network-time OFF
receipt; `dwell` = clean dwell, 600–2700 s; `chain start` = the moment `night/chain.started` is
written; `set` = 180 s chain-owned settle; `pre`, `post` = pulse calibrations; `NEG8` = 12-member bound
corpus, then the bound derivation; `start`, `mid`, `end` = reference stages (3, 1 and 3 members);
`D1` = 10 decode absolute repeats; `D2`, `D3` = the two 20-member decode null-block stages; `P1`–`P3` =
the same for prefill-p2048; `captures end` = the last sampler stops; `verdict` = whole-window verdict;
`backup` = two verified backups; `desk gap` = harvest, G3, the merged ledger-pin advance and, between
BETA and GAMMA only, the L10-B rehearsal (§3.3). Each stage boundary inside the brackets also carries
its own 180 s settle, not drawn.

### 3.3 Desk steps between windows

After each window: harvest (§7) → G3 desk checker on the window's bytes → ledger-pin advance from the
harvest's terminal ledger (records-only commit, §12 class (i)) → plan, authorization, arm notice (the
email to Ed before each arm, which his NO overrides) and T-0 for the next window. After `BETA` PASS and before `GAMMA-1` arms: the L10-B rehearsal extraction and
mint on a scratch copy of the ALPHA and BETA bytes (`docs/process/v5-l10-rehearsal-phase.md` §L10-B),
serializing only structure (§9). An L10-B refusal routes to its owner row; GAMMA arms only when the
lead has classified the refusal (a cure that touches no collection code lets GAMMA proceed; one that
touches collection code follows §7.4).

### 3.4 Expected duration

From §5's sizing, an all-PASS block takes about 8.1 h (ALPHA) + 8.4 h (BETA) + 7.2 h (GAMMA) of chain
time, plus three clean dwells (10–45 min each) and two desk gaps of roughly 1–2 h each: about 27–30 h of
machine time.

## 4. Operating conditions and fixed inputs (checked by code at arm or T-0 unless marked)

1. **Machine.** As §0; AC, battery float, power mode `ac_high_power`, sampler interval 100 ms; no
   agent or operator process from T-0 to the chain's exit (driver census first, repeated every 30 s;
   `pgrep` exit exactly 1 with empty stdout); driver stdin `/dev/null`.
2. **Acceptance.** `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json`, SHA-256
   `f949f511254e03b50b0be1cea37f74c1e8e6b4c49926c6c197024beea07b3660`, ledger cutoff sequence 376. One
   acceptance for all three windows. If a prospective-rederivation trigger of the acceptance fires
   during the block, no further window arms; the question goes to a cold gate (§15 Q13).
3. **Models.** `mlx-community/Qwen3-1.7B-4bit` and `mlx-community/Qwen3-8B-4bit` at the revisions,
   tokenizer bytes and file hashes of `configs/model_panels/qwen3_4bit.json` at H_claim.
4. **Packs.** The three packs at H_claim, identified by `FILL[ALPHA-PACK-DIGEST-AND-FREEZE]`,
   `FILL[BETA-PACK-DIGEST-AND-FREEZE]`, `FILL[GAMMA-PACK-DIGEST-AND-FREEZE]` (block-4 register).
   Plan trees at `db41703c`: ALPHA `e30fdf675e8b18e76142723c4f12baaf9366c0a74f37a5070e3e87d32eb2aefa`,
   BETA `c2c483525cde4d36e46bbd8f9edcf29be9b24bda212ed06d9eba086f297d64a7`,
   GAMMA `995c7ca548c718c96ef2b44b7efa37d356ba82619f391ac6abe2ecb636d0c730`. The pin bundle is block 4
   §3 item 4's (prompt pin `d1209f6d…dccb`, selection `c694c488…8222`, ladder `43a77ea9…1885`).
5. **Policy.** `configs/campaign_policies/quiet_mac_p2_production.json`, SHA-256
   `b0d7b228b88bea717aa9269c103aca760cc36cf05239e0f86c235b4b29665efd` (pinned by every plan tree).
   Its idle-admission retry is immediate (no `retry_backoff_s`, controller default 0). §15 Q1 asks
   whether this is acceptable for ~120-member windows; changing it changes the packs.
6. **Ledger.** The measurement clone's (the dedicated checkout a window runs from) ledger is restored
   byte-exact from the source whose head equals
   the committed pin at the arm head. For `ALPHA-1` that source is block 4's final harvest terminal
   ledger, `FILL[LEDGER-SEED-AFTER-B4]`; for each later window it is the previous window's harvest
   `derived/terminal-ledger.jsonl`, whose head the merged pin advance names. Brackets are judged
   against the acceptance cutoff 376, not the live head.
7. **Network time.** OFF throughout (§0). Each attempt has its own fresh OFF receipt on its own boot,
   at least 600 s before the first capture on both clocks; no reused receipt; no ON at any point.
8. **Disk and backups (checked by the lead at arm, read-only `df`; not yet machine-checked).** The 24
   block-3 member bundles occupied 4.26 GiB, about 182 MiB each (each embeds a ~79 MiB copy of the
   pre-calibration capture). A `_v5` window therefore writes about 119 × 182 MiB ≈ 21 GiB (GAMMA
   101 × 182 MiB ≈ 18 GiB), about 60 GiB for the block; two backups on the same volume would make that
   about 181 GiB. On 2026-10-05 the data volume had 184 GiB free. Arm refuses unless free space ≥
   3 × (this window's estimate) + `FILL[DISK-MARGIN-GB]`, and the backup destinations of
   `FILL[BACKUP-DESTINATIONS]` are named and reachable. If a destination uploads off-machine (the
   runbook names iCloud Drive), the next T-0 is authored only after that upload has finished
   (`FILL[UPLOAD-QUIESCENCE-CHECK]`), because upload work during the next clean dwell would make that
   window NULL.
9. **Battery (#421).** §10.2.
10. **Not checked by code: background work during a member's measured request.** Idle admission
    screens the 30 s before each request; work that starts during the request is not screened. §8
    registers how this is diagnosed and disclosed.

A change to any item after the seal requires a prospective cold erratum before the next arm (§11).

## 5. Window shape and sizing

### 5.1 Shape

Each window runs its pack's `stage_graph` exactly: chain-owned settle, pre calibration and its screen
(a pre-calibration fiducial bound above the screen derived from the acceptance stops the chain before
any member), the NEG-8 bound corpus and bound derivation, the start triplet, the science stages with
the pack's interior references in their registered places, the end triplet, the post calibration, the
whole-window verdict and two backups. Nothing is shortened, skipped, reordered or repeated at arm or at
run time. There is no block limit: claim windows run every block of their pack.

### 5.2 Sizing method (source-bound, counted once)

`NIGHT_PROGRAMMED_SPAN_S` is the sum of the allowances below; `WINDOW_MAX_S = 60 × ceil((span +
2700) / 60)`, where 2700 s is the clean-dwell cap, added once. Every member allowance comes from the
block-3 SELECT archive `/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2`
(archive manifest `SHA256SUMS` `aeef9c9ae93a8513f1f6e3c7fb11028baecc5042eb0d2b9492b03f7216417977`;
diagnostic reading permitted after block 3 by its §10), read for event timestamps only. Block-3
members ran the same Qwen3 models with 512 output tokens; its p2048 prompt has the same token-ID hash
(`202e4913…1479`) as the `_v5` prefill members. They differ in one way that matters: block-3 idle
baselines were 75 s, `_v5`'s are 30 s. The allowance keeps the 75 s figure (so it carries a 45 s
per-member margin, which also covers one immediate admission retry); the expected figure subtracts it.

| Symbol | Value | Meaning | Source `{path, sha256, pointer}` |
|---|---:|---|---|
| `C_small` | 275 s | Start-to-start cycle of one small-model member inside a stage | `…/runs/g2a-small-p4096-r05/events.jsonl` `a24f97556b740044493c5b6723b3c371ef7ac42b89a6c2f8e2370f44e97d2e65` minus `…/g2a-small-p4096-r04/events.jsonl` `c1e31c26982f7729cb10d0e38eb2676f24e76442724fea2dd1dd5ad2336f41f6`, `run_started` timestamps: 274.9 s, the maximum of 16 observed cycles (median 236.5 s) |
| `C_large` | 286 s | Same for Qwen3-8B: `C_small` plus the large-minus-small run-wall difference at p2048 | 274.9 + (167.1 − 156.6) s from the two rows below |
| `W_small` | 157 s | Run wall (`run_started` to `run_finalized`) of the last small member of a stage | `…/g2a-small-p2048-r02/events.jsonl` `b03e3897fd7097e2eac546f5869d244761b39de78e3ebdc8516ba379a0db5079`: 156.6 s |
| `W_large` | 168 s | Same for Qwen3-8B | `…/g2a-large-p2048-r01/events.jsonl` `4727aee881bf68b8a8f223c816f494a75bc211d442e21671dd534d33ad77ecba`: 167.1 s |
| `HEAD`, `TAIL` | 39 s, 62 s | Stage start to first member, last member to stage end | `…/operator-logs/window-chain.log` `225772e7c71f5951aad117e1b04f757301e3e454bd6b2a7fd80cc277be12ad42`: max 38.4 s (large-p2048), 61.6 s (small-p4096) |
| `CAL` | 248 s | One pulse calibration | Same log: post-calibration 248.0 s after the last stage end; pre-calibration 247.0 s after the chain's 600 s settle (block 3's probe chain settled 600 s, not 180 s) |
| `SETTLE` | 180 s | Per-stage and chain-start settle | `docs/phase_2/window_runbook.md` `SETTLE_S=180` |

Stage allowance = `SETTLE + HEAD + (n − 1) × C + W + TAIL`. Worked example, ALPHA's 10-member decode
absolute stage: 180 + 39 + 9 × 275 + 157 + 62 = 2,913 s. GAMMA science stages alternate models, so they
use the mean of `C_small` and `C_large`. NEG-8 and reference members (Qwen2.5-1.5B, shorter output) use
the small-model figures.

Non-member components have no archive yet; their proposed allowances are FILLs to confirm before seal
(the structural stage timestamps of block 4's `s1` would confirm them if §9 classifies those
timestamps as releasable; §15 Q7):

| Component | Proposed allowance | FILL |
|---|---:|---|
| Launch lifecycle before the chain-owned settle | 120 s | `FILL[T-LAUNCH]` |
| NEG-8 bound derivation | 120 s | `FILL[T-BOUND-DERIVATION]` |
| Whole-window verdict (re-derives every bundle's summary, `joulewise/whole_window.py:847`; block-3 per-member reduction took at most 23.9 s) | 24 s × bundles | `FILL[T-VERDICT]` |
| Two verified backups | 600 s | `FILL[T-BACKUP]` |
| Terminal ledger finalization and stop | 120 s | `FILL[T-TERMINAL]` |

Resulting figures (scratch computation
`/Users/edr/night-archive/ia-0a40/claim/scratch-block5-sizing/size_block5.py`,
SHA-256 `014fbeb75dcd46acf29c0506730ed93fe70fa43204a4b58ffc1c15f498bbe834`, output `sizing.json`
`c28c424525f3972a9f46407433d5bb4886b26dd2be7295538c0754d014f1026c`):

| Window | Members (all stages) | Collection allowance | Programmed span | `WINDOW_MAX_S` | Expected chain time | Plan-tree `runtime_budget` |
|---|---:|---:|---:|---:|---:|---:|
| ALPHA | 119 | 34,355 s | 38,847 s | 41,580 s (11.6 h) | ≈ 29,300 s (8.1 h) | 22,704 s |
| BETA | 119 | 35,455 s | 39,947 s | 42,660 s (11.9 h) | ≈ 30,300 s (8.4 h) | 22,897 s |
| GAMMA | 101 | 29,823 s | 33,883 s | 36,600 s (10.2 h) | ≈ 25,800 s (7.2 h) | empty (pending G2-a) |

The packs' own `runtime_budget` (marked `planning_only`) is below even the expected chain time measured
from block 3; it must not set `WINDOW_MAX_S`. These figures are design estimates, not live validation.
`FILL[B5-SPAN-AND-WINDOW-MAX]` binds the final literals the plan writer emits once the non-member FILLs
are bound. A chain still running at `t0 + WINDOW_MAX_S` is stopped by the driver and the window is
RECOVER, never a partial PASS.

### 5.3 Longest sampler stream versus the 5 ms clock bound

Each member's effective clock bound is `h + ρ × T`, with h the anchor half-width, ρ the rate at which
wall and monotonic clocks drift apart, and T the member's stream length. Across block 3's 24 members
(`metadata.json` `uncertainty_evidence.clock_anchor`): h was 0.35–3.60 ms (maximum 3.598 ms,
`…/g2a-large-p4096-r01/metadata.json` `63bd62a1ca1652a0b9194885f75a4d59a8afde1b06d274dbfee21b6352d66c80`),
ρ was 3.20–3.21 ppm, T was 115–132 s, and the largest effective bound was 4.02 ms. A `_v5` member's
stream is about 45 s shorter (30 s idle), so at most about 87 s, and one immediate admission retry adds
about 60 s, so T ≈ 150 s at worst: 3.598 ms + 3.21 × 10⁻⁶ × 150 s × 1000 ms/s = 4.08 ms ≤ 5 ms, a 0.92 ms
margin. At the worst observed h, a stream may last up to (5 − 3.598) ms / 3.21 ppm ≈ 437 s before a
member is voided. This is why any added retry wait must stay below about 290 s (§15 Q1). The estimate
does not enforce anything: a member whose live anchor is not `bounded` is invalid (§6) and aborts its
window. `FILL[LONGEST-STREAM-SIZING]` re-binds h, ρ and T from the implementation's exact convention
before seal (block 4 §4 method).

## 6. Validity

- **Member.** Valid when its summary status is `succeeded`, its bundle passes strict validation
  (`python -m joulewise validate-bundle --strict`, which re-reduces the raw evidence), its clock anchor
  is `bounded`, its runtime-observed token counts are present (`source: runtime_observed`), and its
  #421 capture pair passes (§10.2). Validity never depends on any energy value.
- **Window.** Valid when every member of every stage (science, NEG-8, references) is valid, both
  calibrations pass the acceptance's bracketing decision (`joulewise/calibration_bracketing.py`: each
  slot authenticated and bound to the window's session, the pre slot within the screen, pre-to-post
  drift within the acceptance's rule, acceptance fresh), the bracket binding is written before exactly
  one authoritative whole-window verdict row and that row is `passed`, the NEG-8 bound was derived
  inside the window, the OFF receipt is admitted, the window battery verdict is `pass`, both backups
  verify, the launch lifecycle (start, settle, completion) is complete, and G3 passes. The ledger's
  `physical_ahead` terminal state (the window's ledger is ahead of the committed pin until the harvest
  advances it) is the expected hand-back boundary, not bracket evidence.

## 7. Verdicts, stop and recovery rules

### 7.1 Four mechanical verdicts per attempt

The harvest (`FILL[CLAIM-HARVEST-CLI]`, from authenticated immutable archives only) writes one:

- **PASS:** the chain exited with its registered success code `FILL[CLAIM-CHAIN-SUCCESS-RC]` and §6's
  window validity holds.
- **RECOVER:** `night/chain.started` exists and the attempt is not PASS. The harvest names the cause
  code(s) and one cause class: **T** tooling (code or recipe defect), **E** environment (idle-admission
  double rejection, environment guard, display, thermal, upload or other machine-state work), **I**
  instrument (pre-calibration screen, bracket, clock anchor not `bounded`, NEG-8 drift, authentic
  battery non-pass), **C** custody (backup or authentication failure after a complete collection).
  An ambiguous class is ruled by the lead before any further arm, with the evidence recorded.
- **NULL:** `night/chain.started` is absent (night-gate refusal, OFF receipt failure, dwell timeout,
  admission budget exceeded).
- **REFUSED:** the harvest itself could not archive or authenticate. Cured by R3 and re-harvested from
  identical bytes into a distinct derived archive; never a science outcome.

### 7.2 What happens next

| Outcome | Next step | If the same class occurs twice in a row for the same pack |
|---|---|---|
| PASS | Desk steps of §3.3, then the next window | — |
| NULL | Re-arm the same pack with a new attempt ordinal, plan, authorization and T-0 after the named cause is gone (D-182: a refusal before any capture licenses a new-plan successor) | The next step goes to a **consult**, not a third arm |
| RECOVER-E | A fresh complete attempt of the same pack (new ordinal, roots, bracket session, authorization, T-0) after the cause is named and, where possible, removed | **Consult**; it may authorize another unchanged attempt, a prospective change (cold erratum, §11) or END STATE |
| RECOVER-I | A fresh complete attempt after a named, removable cause is removed; with no removable cause named, the question goes to a **cold gate** | **Cold gate** |
| RECOVER-T | R3 cure. A cure touching no collection code: re-harvest or re-run the desk step on identical bytes. A cure touching collection code: §7.4 | **Consult** on the defect class before the next spend |
| RECOVER-C | Restore custody byte-exact from the archive and re-harvest; a collection whose evidence is lost is RECOVER-T for the custody code | **Cold gate** |

"Twice in a row" counts consecutive attempts of the same pack with the same class. These are
anti-spiral triggers that say where the question goes; none is a cap on attempts (D-186). If a
consult cannot settle the question, it goes to a cold gate; a cold-gate refusal goes to Ed. Ed's NO
stops any arm. Every attempt's bytes, verdict and cause stay in custody and are disclosed (analysis
plan §8); no member, block or cell is pooled, topped up or replaced across attempts (D-078). A fresh
attempt is not a re-collection of a failed member: it is a new complete window whose acceptance test
reads no energy value, so re-attempting cannot select on the outcome.

### 7.3 Systematic instrument trigger and END STATE

If, in any started attempt, at least five members have a recorded clock-anchor status (excluding
`not recorded`) and more than half of them are not `bounded`, the clock instrument is failing and
re-arming cannot cure it: the block goes to **END STATE** at once. END STATE also follows a cold-gate
ruling to stop. At END STATE: no further window arms under this registration; Ed is emailed; the next
step is a design record naming the cause, with a consult and a cold gate. Windows that already PASSED
keep their bytes; whether their L1 reported cells are analysed alone is decided in that design record
(analysis plan §2.3), never by default.

### 7.4 A defect found in the middle of the block

Collection code is any file in the sealed inventory (§13) that executes during a window or changes how
a window's bytes are produced. A cure touching collection code after any claim window has run makes
the new head differ from the head of the completed windows. GAMMA's contrasts are judged against floors
minted from ALPHA and BETA, so they must share one head, one acceptance and one macOS build. Such a
cure therefore **supersedes the whole block**: all completed windows are retained and disclosed, a new
registration (or a cold erratum to this one) is written, block 4's coverage rule decides whether the
new head needs a new qualification occurrence, and the block restarts at ALPHA. A defect in code that
does not run during collection (harvest, extraction, mint, analysis) is cured by R3 and re-run on
identical bytes; the block continues.

## 8. Environmental diagnostic (Sol consult record 31 §5)

**The forcing problem.** Idle admission proves the machine was quiet in the 30 s before each request.
It proves nothing about the request itself (§4 item 10). Block 3 could leave that unchecked because its
output was a record count; block 5 prints energies, and background work during a request adds energy
that would be attributed to the model. A typical macOS maintenance burst (Spotlight, media analysis)
lasts minutes; block 2's `w2` lost a member to one of about six minutes. A measured request lasts
about 11–20 s (block 3, `measured_run` stage).

**What is registered now.**

1. The diagnostic is outcome-independent: it reads no science phase energy and is computed by code
   before any energy is released (§9).
2. Its result never removes a member from a reported cell or a contrast (D-179 forbids a post-collection
   admission filter; a 49-member mean is never computed). It is disclosed per cell and per window
   (analysis plan §8).
3. Existing per-member evidence is recorded and disclosed for every science member:
   `uncertainty_evidence.idle_drift.status`, `pre_idle_window_suspect` and `post_idle_window_suspect`.
4. A rejected design is on record: applying the production CPU-admission predicate to each member's
   post-run idle sentinel flagged all 24 quiet block-3 members (`cpu_busy_ratio_p95_exceeded`; probe
   `/Users/edr/night-archive/ia-0a40/claim/scratch-block5-sizing/ed2_probe.py`, SHA-256
   `1e48e0677babd7fcb2926b747234a883ad377202d33ce020f39112ca0ba22b28`), because the member's own process
   is still tearing down. It cannot be the diagnostic.

**What must be fixed before seal (§15 Q2).** The member-level predicate `FILL[ED-PREDICATE]`, its
false-flag rate measured on block-3 archives (diagnostic only) and its flag counts on block 4's `s1`
(serialized as counts only), and the disposition `FILL[ED-DISPOSITION]`: report-only, or a window-level
trigger (for example, more than half of a window's science members flagged makes the window RECOVER-E,
by analogy with §7.3). The candidate with a physical basis is the QPE01 busy-core journal
(`docs/contracts/night_quiet_admission.md`; `joulewise/quiet_predicate_campaign.py`), which attributes
CPU work to each non-measurement process; it would have to run in the claim chain and therefore be in
H and exercised on `s1`.

## 9. Blinding

1. **Before seal.** No claim-eligible `_v5` byte exists. Block 4 §10 already withholds `s1`'s energies,
   powers and per-member durations from everyone who designs or seals this plan. This draft's author
   read none of them (§16).
2. **During the block.** From `ALPHA-1`'s launch until the block closes (GAMMA PASS, or END STATE),
   every harvest, G3 run, L10-B rehearsal, courier record, email and public summary releases structure
   only: verdicts, cause codes and classes, counts, paths, hashes, readiness and timing facts that are
   not per-member durations. Energies, powers, per-member durations, floor values, reported means,
   dominance ratios and calibration numeric diagnostics stay in restricted custody
   (`FILL[B5-BLIND-CUSTODY-MAP]`). Automation may validate, reduce and evaluate fixed predicates but
   serializes only structure. Every recovery decision in §7 is therefore made without seeing an
   outcome. The current driver excludes raw chain logs from durable courier records only for
   non-`CAMPAIGN_TRANSACTION` purposes (ruling 76 decision 9); `FILL[COURIER-BLINDNESS-CAMPAIGN]`
   extends that exclusion to claim windows (§15 Q3).
3. **Block 4's `s1` metrics** stay withheld until this block closes, so that any erratum written during
   the block is written blind (§15 Q11).
4. **Unblinding.** After the block closes, the lead records a release event binding this file's and the
   analysis plan's sealed SHA-256s and the final harvest records (`FILL[B5-RELEASE-EVENT]`); the analysis
   then runs exactly as registered. Analyses not registered there are labelled exploratory.

## 10. Directive gates

### 10.1 #416: pre-arm triple audit

Once, at H_claim, after this registration is sealed and before `ALPHA-1` arms: a fresh blind
full-system audit (adapters, calibration and issuance, night machinery, reduction, analysis and claims)
by three independent model families, findings cross-verified, BLOCKERs refuted by a different family
and cleared before arm. Ed's directive names Astra 6 xhigh, Fable 5.1 and Opus 5.5 xhigh; the seat
assignment under D-186 and Ed's 2026-10-05 wish to use Fable less is `FILL[416-SEATS]` (§15 Q6). It runs
once per frozen code or protocol change, never per window: a later change to collection code (§7.4)
triggers a diff-scoped re-audit of that change, not a full one. No audit work runs during a window.

### 10.2 #421: battery float, every window

At arm, immediately before publication and installation, and at T-0, a fresh authenticated raw `ioreg`
observation and the shared `joulewise/battery_float.py` reading must pass §0's predicate. Every capture
(both calibrations and every member) has a raw pre/post `ioreg` pair outside its clock-anchor stamps and
sampler lifetime. The harvest computes the window battery verdict from raw bytes before any energy is
read (A-R5b-1 reading: that harvest verdict is final for the window); a missing or unauthenticated
observation is a custody failure (REFUSED, cured by restoring bytes), an authentic non-pass is RECOVER-I. Paths: `FILL[B5-BATTERY-EVIDENCE-MAP]`; block
4's S3/S4 disposition `FILL[BATTERY-S3-S4-DISPOSITION]` carries over. Endpoint pairs cannot see an
excursion wholly between two observations; this limitation is disclosed.

### 10.3 Results and publication

Claim-bearing results are a cold-gate object (orchestration doctrine, gate 2): after the analysis runs,
one judge and one refuter re-derive every printed number from the preserved artifacts before any paper
sentence is filled.

## 11. Changes after the seal

None to §§3–10 for an armed or completed attempt. A rule, threshold, roster, purpose, recovery or
blinding change is a prospective cold erratum (one judge, one refuter), settled in one erratum rather
than a chain. A fix that only makes code agree with this text goes through a gated R3 pull request
whose final pass is the lead's measurement-code reviewer (`FILL[FINAL-PASS-SEAT]`); it never changes
collected bytes, and it follows §7.4 if it touches collection code.

## 12. Head rule

1. **H_claim** is block 4's qualified head H′ (H plus its record-47 terminal refresh), extended only by
   (i) merged ledger-pin advances from this block's harvests with their readiness and freeze refreshes,
   under block-4 record 47's changed-path proof (the list of files a pin advance may change, checked
   against `git diff --name-only`); (ii) gated R3 fixes to code that does not run during
   collection; (iii) commits touching only `docs/`, `tests/`, `RUN_STATE.md` or `TASK_QUEUE.md` that
   leave every pinned executable, generated config and chain source unchanged. Each extension carries a
   `git diff --name-only` map checked before the next arm.
2. Claim windows execute code that `s1` did not: the `CAMPAIGN_TRANSACTION` plan writer, a chain that
   runs every stage of a full pack (including GAMMA's three interior references), any §8 recorder and
   the claim-window courier exclusion. That code must be at H before block 4's `s1` arms, so that `s1`
   qualifies it, or a cold gate must rule prospectively that `s1`'s coverage extends to it
   (`FILL[CLAIM-LAUNCH-CODE-AT-H]`, §15 Q3).

## 13. Seal

A cold gate seals this file and the analysis plan together (`FILL[B5-SEAL-SEATS]`). The seal record
`FILL[B5-SEAL-RECORD]` pins, with SHA-256s at H_claim: both documents; H_claim; the three packs and their
freeze receipts; the panel, policy, acceptance and pin bundle; the claim plan writer, chain renderer,
`scripts/run_night.py`, `scripts/launch_window.py`, `scripts/run_campaign.py`, `joulewise/controller.py`,
`joulewise/night_gate.py`, `joulewise/night_plan_writer.py`, `joulewise/arm_readiness.py`,
`joulewise/arm_readiness_evidence_t0.py`, the calibration capture, ledger, bracketing, binding and
battery readers, `joulewise/whole_window.py`, the strict validator and reducer, the claim harvest, G3
and the §8 producer; the analysis programs named in analysis plan §11; and the two chain-source
documents `docs/phase_2/window_runbook.md` and
`docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`. Grouped entries are expanded file
by file in `FILL[B5-SEALED-FILE-INVENTORY]`.

## 14. Binding register

| Binding | FILL | Due |
|---|---|---|
| Block-4 verdicts | `B4-STRUCTURAL-VERDICT`, `B4-QUALIFICATION-VERDICT` | Seal |
| L10-A, Q110, A6 | `L10-A-RATIFICATION-RECORD`, `Q110-CLOSURE`, `A6-AT-H-CLAIM` | Before `ALPHA-1` arm |
| Head | `H-CLAIM`, `CLAIM-LAUNCH-CODE-AT-H` | Seal (code at H before block 4's `s1` arm) |
| Packs | `ALPHA-PACK-DIGEST-AND-FREEZE`, `BETA-…`, `GAMMA-…` | Seal |
| Ledger | `LEDGER-SEED-AFTER-B4`; per-window pin advance | `ALPHA-1` arm; each later arm |
| Authorization, step 6 | `AUTH-<label>`, `CAMPAIGN-PERMITTED-BLOCKS`, `STEP6-RECORD` | Semantics at seal; record each arm |
| Sizing | `T-LAUNCH`, `T-BOUND-DERIVATION`, `T-VERDICT`, `T-BACKUP`, `T-TERMINAL`, `B5-SPAN-AND-WINDOW-MAX`, `LONGEST-STREAM-SIZING` | Seal |
| Chain | `CLAIM-CHAIN-SUCCESS-RC`, `CLAIM-HARVEST-CLI` | Seal |
| Disk | `DISK-MARGIN-GB`, `BACKUP-DESTINATIONS`, `UPLOAD-QUIESCENCE-CHECK` | Seal; checked each arm |
| Environment diagnostic | `ED-PREDICATE`, `ED-DISPOSITION` | Seal (exercised on block 4's `s1`) |
| Blinding | `B5-BLIND-CUSTODY-MAP`, `COURIER-BLINDNESS-CAMPAIGN`, `B5-RELEASE-EVENT` | Seal; release after block close |
| Battery | `B5-BATTERY-EVIDENCE-MAP`, `BATTERY-S3-S4-DISPOSITION` | Seal; evidence each window |
| Audit, seats | `416-AUDIT-RECORD`, `416-SEATS`, `B5-SEAL-SEATS`, `FINAL-PASS-SEAT` | Seats at seal; audit before `ALPHA-1` |
| Boundary | `BOUNDARY-LABEL` | Seal |
| Seal | `B5-SEAL-RECORD`, `B5-SEALED-FILE-INVENTORY` | Seal |

## 15. Open questions for the lead (each names where it goes)

- **Q1. Admission bursts can end long windows (decide before block 4 seals; consult).** In block 2's
  `w2` (18:12–19:59 UTC on 2026-10-03) and block 3's SELECT window (13:26–16:43 UTC on 2026-10-04),
  37 members' idle admissions over about 5.0 chain-hours gave one member lost to two rejections inside
  one ~6-minute burst and one other admission that needed its retry. A claim window holds ~120 members
  over ~8 h, admission occupies roughly a third of every member cycle, and the production policy
  retries immediately, so a burst of that length during collection almost surely ends the window. If
  bursts arrive about once per 5 h, a window survives with probability about e^(−8/5) ≈ 0.20; at one
  per 24 h, about 0.72 per window and e^(−23.7/24) ≈ 0.37 for all three. The rate is poorly known.
  Options: (a) keep the policy and rely on §7.2's fresh attempts; (b) regenerate the packs with a retry wait below about 290 s (§5.3), which changes pack
  bytes and must therefore precede block 4's seal; (c) re-cut each floor pack into two shorter windows
  (new packs, new freeze). First step: estimate the burst rate from every retained 25G83 record
  (block 2/3 members, QPE01 envelopes, D-079 derivation windows).
- **Q2. Environmental diagnostic (§8; consult, before block 4 seals if a recorder is added).** Choose
  the predicate and the disposition; decide whether the QPE01 busy-core journal joins the claim chain
  and `s1`.
- **Q3. Claim-window launch code at H (before block 4's `s1` arms).** The `CAMPAIGN_TRANSACTION` plan
  writer, a full-pack chain renderer following each pack's stage graph, the claim harvest and the
  claim-window courier exclusion do not exist yet; without them at H, `s1` does not qualify the claim
  launch path (§12.2).
- **Q4. Disk and backups (lead).** About 60 GiB of collected bytes, and about 181 GiB with two
  on-volume backups, against 184 GiB free, before any L10 scratch copy; name the backup destinations and
  the upload-quiescence check (§4 item 8).
- **Q5. Paper placement (cold gate, ideally before seal).** D-174's methods/diagnostic fallback places
  no `_v5` result, and D-179 ruling 7 keeps the reported-energy placement X5 `RETIRED_FALLBACK`. The
  comparison-placement proposal (X1–X22) is `PROPOSED_STOP_FILL`. Pre-registering what is printed
  needs an adoption ruling.
- **Q6. Seats (lead; Ed may veto).** Seal gate, #416 composition and the measurement-code final pass,
  given #416's named seats, D-186's Sol default and Ed's 2026-10-05 "try using fable less for a bit".
- **Q7. Non-member stage timing (lead).** Confirm `T-VERDICT`, `T-BACKUP` and the launch prefix; decide
  whether block 4's `s1` non-member stage timestamps are structural (releasable) or withheld.
- **Q8. `permitted_blocks` for claim authorizations (lead).** The contract defines it only for G2-b
  (exactly 1). Proposed: the pack's full block count (ALPHA/BETA 20 null blocks, GAMMA 20 contrast
  blocks), recorded but not runtime-enforced, since claim chains run the whole pack.
- **Q9. §7.4 supersession (cold gate).** Opus consult record 32 §5 proposed it; confirm it, or allow a
  block-4-style coverage ruling to keep completed windows.
- **Q10. Analysis code timing (lead).** Production reported-energy issuance does not exist
  (`joulewise/paper_reported_energy.py:457`, "No production dispatch exists"), nor do the `_v5`
  pinset/input manifest, the mint-to-close-out adapter or the claim-verdict-to-results-fill adapter
  (`docs/process/v5-artifact-flow.md`). Preferred: merged and pinned before `ALPHA-1`; otherwise written
  blind before the release event.
- **Q11. Keep block 4's `s1` metrics withheld until block 5 closes (lead).** Recommended (§9.3).
- **Q12. L10-B between BETA and GAMMA (lead).** Proposed as blocking for `GAMMA-1` (§3.3).
- **Q13. Acceptance rederivation trigger mid-block (cold gate if it fires).** §4 item 2.

## 16. What the author read

From the block-3 SELECT archive (diagnostic, readable after block 3 by its §10): event timestamps and
the per-member and per-phase durations derived from them (for sizing), clock-anchor records,
idle-admission attempt counts and decisions, the CPU-admission predicate's decisions on post-run idle
sentinels (decisions only), the cluster-level CPU idle-ratio field (reads 0 throughout, so it cannot
serve as a diagnostic), bundle byte sizes, the selected length, and the window chain log, which also prints the block-3
pre-calibration fiducial bound (seen; not used). From block 2's `w2` archive: admission attempt counts
and decisions and the chain log's stage times. The packs' committed plan trees, including their
`runtime_budget` planning figures. No energy or power value of any block was read, nothing of block 4
exists yet, and no `_v5` claim byte exists.
