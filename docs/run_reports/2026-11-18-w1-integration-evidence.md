# W1 integration rehearsal and signing-head evidence index

**2026-11-18 · Register 28 and 30 · RED for adoption.** An off-ref object rehearsal of the current qualification, S-row and S/Q heads preserves all **10/10** issued R1 blobs. Adding the current W1 evaluator rebind leaves **8/10**. The first mismatch in the evaluator history is the rehearsal driver at `5434cb49d805768f6d5b8f82d71a3bef04901aba`. Workload first differs at `b3b88c6965963beaeb413fd15b39fecca6e71eaf`. No approved combined code commit, signing head, or final candidate CI run was supplied. The document is Tier 0. The code decisions and review remain Tier 2. [Pipeline §§1, 3–4](https://github.com/mpmdw/JouleWise/blob/211ff50330f6ba5223687306c7a76663406fdee7/docs/process/PIPELINE.md#L6) · [RL-107](https://github.com/mpmdw/JouleWise/blob/f9b03c33d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L6054)

## Ref and object basis

The prepared report worktree started clean at `2bb70e14379b7b82b02019674be4f1bf82f5b193`, equal to refreshed `origin/main` (0 ahead, 0 behind). The personal report branch had neither a remote head nor an existing PR at intake. Mission M0 found no active stop card in the prepared checkout. The comparison uses the issued R1 commit `b2e01464d6d4fbf2901ff4d4154df9455104a12a`, also the refreshed #734 head and W1 ref. The R1 path set comes from `R1_EXECUTED_SOURCES` at that **issued commit**. Rows 11–17 extend it to the prior Part C census. Comparisons use full Git blob OIDs, with a missing object counted as a difference. The lead establishes the original-night commit identity and runs the actual signing-tree verifier. [Issued list](https://github.com/mpmdw/JouleWise/blob/b2e01464d6d4fbf2901ff4d4154df9455104a12a/joulewise/align/apple/v4_registration.py#L489) · [Prior Part C census](https://github.com/mpmdw/JouleWise/blob/f9b03c33d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L16256)

| Component | Head commit | Direct parent(s) | Tree |
|---|---|---|---|
| Issued R1 / #734 | `b2e01464d6d4fbf2901ff4d4154df9455104a12a` | `e5b4f4f7fbc05d3c1ff661356867f95a24e0cf9a`, `ca02c76e3b06118a6bcb5d612f034c93ceafb003` | `c904864e46879a4adfbdf0b467d4da1ee5928285` |
| #812 earlier | `df261f6a235e976be8859ab5314af737a08f6d7d` | `ab32a6c915a9a78f92554a89c5d0eb93333b7a39` | `ea6f5fc234e63e1c2e93eb70ecd0c892c6ed8bc5` |
| #812 current | `0d03cb7833bb8b15bc391127a7fe5519b7d98602` | `df261f6a235e976be8859ab5314af737a08f6d7d` | `421f5c2694234e6f906f34980b3df3920ed402a0` |
| #787 | `0a032c835de1af8ba180f6e0356feae129b01456` | `c4c8f37f306b3774b2a4e36c96714750bbc88ef5` | `00d53212210b325e8d3703f47bef093c0e5e52bf` |
| #813 earlier | `a36b28b732e9423387be41372671e1cc083d3b6d` | `13c79eaaf24c94af7d8659fb905641e6d02fc8a5` | `e2a4fdf83379112870c158bed902c294c0001ad5` |
| #813 intermediate | `e25779d16c26810f4c69a067b982ba7b3dac8c22` | `a36b28b732e9423387be41372671e1cc083d3b6d` | `236876827b163605b62eec7db57a63e1343a9bb6` |
| #813 current | `802a29728138717653b2869e4859b955d632d800` | `e25779d16c26810f4c69a067b982ba7b3dac8c22` | `d3b27d4b2609be03891937bce5a7e481ae5825e1` |
| #809 main earlier | `da71c46670baed7c23b914d7d68749f6fa7c687c` | `29620d0705eda9f31d20f4fdca689e7635ab895a` | `9d942ce77a0b54edd688d52fc5da5af153d5a942` |
| #809 main current | `ecf69bc80d2424ceb66116600133f5724139ee4f` | `da71c46670baed7c23b914d7d68749f6fa7c687c` | `0d32bb710f575714c2f0daba62cf2ddd4643dbf2` |
| #809 W1 earlier | `e26b04b53049ba285e9b36299393b7895475ea5d` | `5434cb49d805768f6d5b8f82d71a3bef04901aba` | `e2958708a56adb42810469a5114f914695889fde` |
| #809 W1 current | `b3b88c6965963beaeb413fd15b39fecca6e71eaf` | `e26b04b53049ba285e9b36299393b7895475ea5d` | `e667e818d15d915f0b62158ab7cbf1fa1c37cf46` |
| #774 merged desk base | `9848520a4cc03cbd95d77a0a3f7b57e306224007` | `e4ffd6af7a762424e50669368727157cd6683d6a` | `b19fb42f87e1d2aa1ab9ee3ab5da63ce0327e523` |
| #694 R0 | `d7b27961f809f3b2accba3a19194fb5a28cda7a9` | `4182378a1e436fcc19742e5744583567dc0e3f82`, `5f817856b33f65b269a44ea52811dbbed28d02a8` | `a1cb900754f1b95c7a38c5c1e53a1441d073e82f` |

## Seventeen-path census

| # | Repository source path | Issued blob OID |
|---:|---|---|
| 1 | `scripts/align_r1_rehearsal.py` | `33c6876e6a988bee93fc49a0ba554f7c2c3bf277` |
| 2 | `scripts/align_r1_runtime.py` | `96b249a6eb44c4de2887aeeadff089c3040d8cfa` |
| 3 | `joulewise/align/apple/r1_runtime.py` | `261761f1a5e39220614b74d53d125022278502db` |
| 4 | `joulewise/align/apple/r1_runtime_contract.py` | `1ef822bee6d3b4951ad24cd1991ea31741d30161` |
| 5 | `joulewise/align/apple/smc_enumeration.py` | `8a1a96dcb10ebb16809717af15918d5366b0d31c` |
| 6 | `joulewise/align/apple/thermal_gates.py` | `b46769d70df02de09dbeb07e4c0020c472477dcb` |
| 7 | `configs/align/v4/r1_runtime.json` | `bf8479b26774b4d6a7bb3d44c6e2d662ddeb199e` |
| 8 | `joulewise/align/apple/r1_phase_table.py` | `e412bb4389aae4e4239b47842512db178d4b53a2` |
| 9 | `joulewise/align/apple/workload.py` | `ff30c29178ad9ccceab96140c569b8f14afa16e9` |
| 10 | `joulewise/align/apple/thermal.py` | `e7cbd6808c5a407524e3a85254090a46c33fa910` |
| 11 | `scripts/launch_align_r0.py` | `d2e8cba01753817979a5e2b70e39442092643420` |
| 12 | `scripts/run_align_r0_launchagent.sh` | `d451ec67c5331266a8556e9ce626f02b5d57e329` |
| 13 | `scripts/run_align_r1_smoke.py` | `393e6fce05ae39f48d33c9fc56af92ce8cec81b4` |
| 14 | `scripts/align_r1_followup_kit.py` | `aa036ce5b55d28fc701e9c892793e0a74bc6868d` |
| 15 | `scripts/align_r1_part_c.py` | `89862a56b55fa9d9f92cdd08d6dc9e260b824bd1` |
| 16 | `joulewise/align/apple/rl145_prints.py` | `48014de5bbd8ae2c5289fb2e372207dd0f930642` |
| 17 | `joulewise/align/apple/v4_registration.py` | `e47f4331132faf1c5c2d28762139db3c2dc5885a` |

The rows below list every change **within the census**, with whole-tree path counts in parentheses. Merge-bases are measured against the lane named in the second column. The tip comparison always uses issued R1.

| Head | Merge-base and lane | Merge-base → tip | R1 → tip |
|---|---|---|---|
| #812 `df261f6a2` | W1 `c3f4bacd8013ca98c19cf8d41f830c701930cd41` | None (37) | 17 (77), inherited. **10/10 PASS** |
| #812 `0d03cb783` | W1 `c3f4bacd8013ca98c19cf8d41f830c701930cd41` | None (37) | 17 (77), inherited. **10/10 PASS** |
| #812 `0d03cb783` with PR base | kit-v1-1 `9cbb365a6957c3737617d8604ba6d06071ab018c` | 1, 7, 13–17 (66) | 17 (77). GitHub's review base is the kit lane |
| #787 `0a032c835` | W1 `ae340d3da62192403fc0e9cfcc10f04fe19fd2e6` | None (4) | 1, 7, 13–17 (61), inherited. Raw tip **8/10** |
| #813 `a36b28b73` | W1 `b2e01464d6d4fbf2901ff4d4154df9455104a12a` | 17 (13) | 17 (13). **10/10 PASS** |
| #813 `802a29728` | W1 `b2e01464d6d4fbf2901ff4d4154df9455104a12a` | 17 (18) | 17 (18). **10/10 PASS** |
| #809 W1 `e26b04b53` | W1 `b2e01464d6d4fbf2901ff4d4154df9455104a12a` | 1, 14, 15 (6) | 1, 14, 15 (6). **9/10 FAIL** |
| #809 W1 `b3b88c696` | W1 `b2e01464d6d4fbf2901ff4d4154df9455104a12a` | 1, 9, 14, 15 (8) | 1, 9, 14, 15 (8). **8/10 FAIL** |
| #809 main `da71c4667` and `ecf69bc80` | main `2f9e8b6f605dc14bd3358d5278387596f5d2fb45` | 15 (20 each) | 1–11 and 13–17 (12,956 each). All ten R1 paths absent |
| #774 `9848520a4` | historical W1 base `c3f4bacd8013ca98c19cf8d41f830c701930cd41` | 17 (17) | None (24). This head is already an ancestor of issued R1 |
| #734 `b2e01464d` | v4-r11 `b4a6c217f0285a20aff33a8407160dd77af2a8a6` | 1, 3, 4, 7–11, 13–17 (305) | **CONTROL REFUSED.** Same commit as issued R1 |
| #694 `d7b27961f` | pilot10-benign `5f817856b33f65b269a44ea52811dbbed28d02a8` | None (7) | 1–17 (623). The R0 branch predates several W1 sources |

- **#812 base.** `git merge-base` against issued W1 returns `c3f4bacd8` for both heads. The current pair has 31 commits unique to W1 and 31 to #812. GitHub's separate kit-base test merge `1f0375153a6af4e2424b658bd0b78844ede607c5` has #812's tree `421f5c2694234e6f906f34980b3df3920ed402a0`. The W1 rehearsal has a different tree. [PR #812](https://github.com/mpmdw/JouleWise/pull/812)
- **#787 base.** The PR API recorded `f30a97d008b57acde9adec0f789dff13c9d6ef23` as its base snapshot. The W1 and historical-base merge-base is `ae340d3da`. #787's own delta adds four S-row implementation, test and twin files, touching none of the 17. The driver's `2d6b24c13034850d616955c1d3a5e1dad7df6381` and runtime config's `a784f7811ffe74d91622c7bdb3b077dce826a2f6` are both identical to the older merge-base blobs. The rehearsal retains issued rows 1 and 7. [PR #787](https://github.com/mpmdw/JouleWise/pull/787)
- **#813 refreshed.** The prepared branch snapshot saw `a36b28b73`; the remote subsequently advanced through `e25779d16` to `802a29728` for the RL-182 edits. Row 17 has the same blob at both endpoints. The replay below retains both states. [PR #813](https://github.com/mpmdw/JouleWise/pull/813)
- **#809 first mismatch.** The earlier W1 sequence `f618364409d00dc3a02d34d10ca32e42ae5340ed`, `bdb1d232f1c2a945557e8ae29cffc791731aeace`, `4d7dd28cc93bb02f6f6782dacd7af04abd6eda8e` preserves all ten. `5434cb49d` introduces driver blob `baff8f949affadfcfe5b99e1e76095e0260c78f1`, which persists at `e26b04b53`. `b3b88c696` replaces that driver blob and introduces the workload difference. The PR body's renewal self-check gives no post-R1 evidence: a value of `executed_commit` taken from the candidate would compare the candidate to itself. [PR #809](https://github.com/mpmdw/JouleWise/pull/809) · [W1 rebind](https://github.com/mpmdw/JouleWise/commit/b3b88c6965963beaeb413fd15b39fecca6e71eaf)

## Object rehearsal

I applied the known component deltas with Git's three-way merge preview in seat-private Git object storage. The inputs below are either full commits from the first table or earlier output trees. There were **zero textual conflicts** across these eight previews. For each #813 state, the two evaluator previews start from the matching three-component tree. Row 17 is a #813 change to the registration implementation and remains part of the signing closure review. The later desk follow-up, approval of edited #813, final evaluator and lead-owned signing inputs are pending.

| Incoming | First input | Second input | Merge-base | Result tree | Changed rows vs issued R1 |
|---|---|---|---|---|---|
| #812 | `b2e01464d6d4fbf2901ff4d4154df9455104a12a` | `0d03cb7833bb8b15bc391127a7fe5519b7d98602` | `c3f4bacd8013ca98c19cf8d41f830c701930cd41` | `90e98003429577d21d48b49d289edbbba8bd3a0b` | None |
| #787 | `90e98003429577d21d48b49d289edbbba8bd3a0b` | `0a032c835de1af8ba180f6e0356feae129b01456` | `ae340d3da62192403fc0e9cfcc10f04fe19fd2e6` | `83702d70b74f73345d724a80f108b1d637f7a9a9` | None |
| #813 earlier | `83702d70b74f73345d724a80f108b1d637f7a9a9` | `a36b28b732e9423387be41372671e1cc083d3b6d` | `b2e01464d6d4fbf2901ff4d4154df9455104a12a` | `09a3f6a6857a6b05b54f5561df2a14eb4fcc5b32` | 17. **10/10 PASS** |
| Prior evaluator with earlier #813 | `09a3f6a6857a6b05b54f5561df2a14eb4fcc5b32` | `e26b04b53049ba285e9b36299393b7895475ea5d` | `b2e01464d6d4fbf2901ff4d4154df9455104a12a` | `3475c9c56e39a6d145e80f261f2d93a2e5d79d4b` | 1, 14, 15, 17. **9/10 FAIL** |
| Current evaluator with earlier #813 | `09a3f6a6857a6b05b54f5561df2a14eb4fcc5b32` | `b3b88c6965963beaeb413fd15b39fecca6e71eaf` | `b2e01464d6d4fbf2901ff4d4154df9455104a12a` | `069a9463639d1c0945583cc39c033013921310d5` | 1, 9, 14, 15, 17. **8/10 FAIL** |
| #813 current | `83702d70b74f73345d724a80f108b1d637f7a9a9` | `802a29728138717653b2869e4859b955d632d800` | `b2e01464d6d4fbf2901ff4d4154df9455104a12a` | `583506894e3d0751839bb793628debd6c8e64f60` | 17. **10/10 PASS** |
| Prior evaluator with current #813 | `583506894e3d0751839bb793628debd6c8e64f60` | `e26b04b53049ba285e9b36299393b7895475ea5d` | `b2e01464d6d4fbf2901ff4d4154df9455104a12a` | `8888acfa4817187bc1d7d0c2ef6989730c64a249` | 1, 14, 15, 17. **9/10 FAIL** |
| Current evaluator with current #813 | `583506894e3d0751839bb793628debd6c8e64f60` | `b3b88c6965963beaeb413fd15b39fecca6e71eaf` | `b2e01464d6d4fbf2901ff4d4154df9455104a12a` | `d0e2dfd3ec3707bf4d7bb321f5bc4cbc95dfb22f` | 1, 9, 14, 15, 17. **8/10 FAIL** |

| Changed row | Prior evaluator tree | Current evaluator tree | Owning delta |
|---:|---|---|---|
| 1 | `baff8f949affadfcfe5b99e1e76095e0260c78f1` | `366c5b7fc3c79f08b7a6588501e7de94593c1faa` | W1 evaluator integration owner |
| 9 | Issued blob | `a8c7acfcd13de7c0000719073e55c1e036542b98` | W1 evaluator integration owner |
| 14 | `ff9784bbc0c9c09c543fd8aef934a2d8f2bd91ae` | `d4650e4975375fd26a35891e7a7f5552d9c4a69b` | W1 evaluator integration owner |
| 15 | `d01c6692e98c6112f9a02b723096ad1a4cdac214` | `b113064cde92a83a528df64b0f7b026885c371c5` | W1 evaluator integration owner |
| 17 | `bc958e4c2c4dbc5b4eb694a1807b3a919aedc52b` | `bc958e4c2c4dbc5b4eb694a1807b3a919aedc52b` | S/Q and signing-closure owners |

The W1 evaluator owner owns the two failed R1 comparisons even though every changed blob is attributable to a component. Across these previews there were zero unassigned census differences. The absent desk/evaluator successors still need the same check. For the R0 owner, #694 previewed against refreshed pilot10-benign `9c40e4e5d9fa453cce3c70984e11fa382b7d4591` exited 1 with three content conflicts: `joulewise/align/r0_host.py`, `joulewise/align/r0_runner.py`, and `tests/align/test_r0_host.py`. The R0 integration owner owns the #699 interaction and delta review. [PR #694](https://github.com/mpmdw/JouleWise/pull/694)

## Component CI and decisions

GitHub's PR-run `head_sha` identifies the source head. The checkout line in the jobs identifies the code actually executed. A PR merge tree is evidence for its tree only. Run counts below are check-run snapshots, including individually identified skipped or unsuccessful checks.

| Component and owner | Exact head CI | Last recorded disposition and remaining work |
|---|---|---|
| #734, W1 integration lead | `b2e01464d`, [CI success](https://github.com/mpmdw/JouleWise/actions/runs/43712204542), 21 successes and [1 skipped draft gate ledger](https://github.com/mpmdw/JouleWise/actions/runs/43712204538/job/132806019030). Checkout `690b0bcf5c0f4fd4da307a6e1c4f4dfa90ed9fcb` has identical tree `c904864e46879a4adfbdf0b467d4da1ee5928285`. | Fable and Opus admitted earlier parts. The final combined code, authorized landing and lead signing proofs are pending. [PR #734](https://github.com/mpmdw/JouleWise/pull/734) |
| #812, qualification integration owner | `0d03cb783`, [CI running](https://github.com/mpmdw/JouleWise/actions/runs/44270871439), all twelve ordinary shards running at the 09:15 UTC check-run snapshot. Two draft ledger skips [one](https://github.com/mpmdw/JouleWise/actions/runs/44270871492/job/134686914718) and [two](https://github.com/mpmdw/JouleWise/actions/runs/44272384451/job/134691949541). `df261f6a2` [CI cancelled](https://github.com/mpmdw/JouleWise/actions/runs/44265227537), ordinary shards 1, 3, 6, 7, 8, 9, 10 and 11 cancelled, two draft ledger skips [one](https://github.com/mpmdw/JouleWise/actions/runs/44265228982/job/134668044753) and [two](https://github.com/mpmdw/JouleWise/actions/runs/44268148079/job/134677718402). | Register snapshot predates the exact-head Astra pipeline **MERGE** on the launcher repair, recorded by `ab63e041f`. The updated builder reports 111 focused tests and 1,552 Bash/Zsh and 91 pinned checks on synthetic inputs. Qualification remains HOLD_FOR_FIT_FREEZE. Per-kit admission, line-2 baseline test equivalence and combined W1 CI remain separate. [Astra disposition record](https://github.com/mpmdw/JouleWise/commit/ab63e041fa324709991786c6a57b6ace69dac0e5) · [PR #812](https://github.com/mpmdw/JouleWise/pull/812) |
| #787, S-row integration owner | `0a032c835`, [CI success](https://github.com/mpmdw/JouleWise/actions/runs/43657595771), 21 successes and three draft ledger skips [one](https://github.com/mpmdw/JouleWise/actions/runs/43657595787/job/132639495495), [two](https://github.com/mpmdw/JouleWise/actions/runs/43657630879/job/132639615313) and [three](https://github.com/mpmdw/JouleWise/actions/runs/43657645666/job/132639659089). | Fable RL-154 ADMIT WITH FIXES on `e15687f94`, independent item 5 satisfied under RL-160. Ordinary delta review and final A/B dispositions remain with the owners. RL-182 places the admitted row builder and release caller at the C1 gate, with permission to include both in the one W1 receipt if ready. [PR #787](https://github.com/mpmdw/JouleWise/pull/787) · [RL-182 §1.5](https://github.com/mpmdw/JouleWise/blob/ab63e041fa324709991786c6a57b6ace69dac0e5/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19776) |
| #813 earlier, S/Q integration owner | `a36b28b73`, [CI success](https://github.com/mpmdw/JouleWise/actions/runs/44260632270), 21 successes and three draft ledger skips [one](https://github.com/mpmdw/JouleWise/actions/runs/44260632190/job/134652828011), [two](https://github.com/mpmdw/JouleWise/actions/runs/44260860507/job/134653588601) and [three](https://github.com/mpmdw/JouleWise/actions/runs/44268676653/job/134679480040). PR merge `7a1b0851d85db9dc809773c90dca3df05ae8c439` has the head tree. | Builder evidence and RL-182 cold verdict reached this exact head. **Not sign-ready**: E1–E17, green CI, lead diff and Astra audit close remain. This was the verdict on the earlier head. [PR #813](https://github.com/mpmdw/JouleWise/pull/813) · [RL-182 §§1.1, 1.3](https://github.com/mpmdw/JouleWise/blob/ab63e041fa324709991786c6a57b6ace69dac0e5/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19644) |
| #813 current, S/Q integration owner | `802a29728`, [CI in progress](https://github.com/mpmdw/JouleWise/actions/runs/44276193248), draft [ledger skipped](https://github.com/mpmdw/JouleWise/actions/runs/44276193418/job/134704834938). The intermediate `e25779d16` has zero check runs. | Builder reports the E1–E17 edits and 105 focused synthetic passes, including the new registration witnesses. Lead diff, Astra close and current-head CI remain. [Builder report](https://github.com/mpmdw/JouleWise/blob/802a29728138717653b2869e4859b955d632d800/docs/run_reports/2026-11-18-rl182-build.md) |
| #809 W1 evaluator, evaluator integration owner | `e26b04b53` and `b3b88c696`: **zero check runs each**, no W1 CI log. Main `da71c4667` [CI success](https://github.com/mpmdw/JouleWise/actions/runs/44262561748). Main `ecf69bc80` [CI success](https://github.com/mpmdw/JouleWise/actions/runs/44269716531), 20 successes and two draft ledger skips [one](https://github.com/mpmdw/JouleWise/actions/runs/44269716312/job/134682977937) and [two](https://github.com/mpmdw/JouleWise/actions/runs/44269877551/job/134683580754). | Four VERIFIED HIGHs blocked `da71c4667` and `e26b04b53`. Builder reports successor synthetic replays passed 16/16 on each line. Independent review of the successor and the W1 source-identity ruling are pending. Main CI belongs to the main PR. [PR #809](https://github.com/mpmdw/JouleWise/pull/809) |
| #774 and outstanding follow-up, desk-seal and U3 owners | `9848520a4`, [historical CI failure](https://github.com/mpmdw/JouleWise/actions/runs/43680343309). Shard [5](https://github.com/mpmdw/JouleWise/actions/runs/43680343309/job/132709565524) failed `LiveTraceTests.test_a_fresh_process_running_the_minimal_dry_run_stays_inside_the_committed_trace`. Shard [7](https://github.com/mpmdw/JouleWise/actions/runs/43680343309/job/132709565579) failed `ExecutedClosureBindingTests.test_artifact_set_has_no_duplicates_or_missing_files_and_matches_template`. The [ready ledger](https://github.com/mpmdw/JouleWise/actions/runs/43684628581/job/132722393349) failed format; three earlier ledger jobs skipped [one](https://github.com/mpmdw/JouleWise/actions/runs/43680343306/job/132709385519), [two](https://github.com/mpmdw/JouleWise/actions/runs/43680361660/job/132709438064) and [three](https://github.com/mpmdw/JouleWise/actions/runs/43684609646/job/132722340526). | The historical ruling carried Part C across #774 and required the substantive follow-up. The issued #734 CI logs below show those two tests green on its tree. The protected desk/U3 successor, its verdict and its CI are pending. [PR #774](https://github.com/mpmdw/JouleWise/pull/774) · [Desk ruling](https://github.com/mpmdw/JouleWise/blob/f9b03c33d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L16256) |
| #694, R0 integration owner | `d7b27961f`, [CI success on old R0 base](https://github.com/mpmdw/JouleWise/actions/runs/42404174164), 21 successes and three draft ledger skips [one](https://github.com/mpmdw/JouleWise/actions/runs/42404174115/job/128498233540), [two](https://github.com/mpmdw/JouleWise/actions/runs/42418795077/job/128542548283) and [three](https://github.com/mpmdw/JouleWise/actions/runs/42418811324/job/128542599670). | Fable ADMIT WITH FIXES on `b02f0ac56`; current pilot10-benign preview conflicts. The owner must rebase and get the #699 delta reviewed. [PR #694](https://github.com/mpmdw/JouleWise/pull/694) |

## Signing-head test index

The #787 run checked out `1f76bc064341cd73d8439cec17ac3c8b23180ed8`, which has the #787 head tree. The refreshed W1-base GitHub preview `52b628e53e2e6fbe6bf21430268f7f774ae2ae21` has a different tree, `215f4d4a8e82aadf00ebd2929462e85653e8082a`. The #809 main run checked out `5598f2df431a585982c80c7f1ba30f36c4277bfe` on main tree `cac46128db252d9c4834f1082e19311f73a4fbce`. The historical #774 and #694 runs checked out `93cea5e52032e06e76398d83bf7c8c0c0eacd0a4` and `70abe6192cf817738088889a563b3da52c92d2b3`, respectively, with their listed head trees. The updated #813 and current #812 logs were unavailable for checkout-line inspection while their runs were in progress.

Historical evidence below is from the **issued tree** checked out by PR #734. The right column is the evidence owed on the eventual immutable candidate. The original R1 identity check, the actual `verify_r1_executed_sources` return, and RL-111's four authorized host-state fields stay lead-owned.

| Named unit or gate | Issued-tree CI evidence | Approved candidate |
|---|---|---|
| `tests.align.test_v4_registration.R1ExecutedSourceTests.test_condition13_names_exactly_the_ten_ruled_sources` | [PASS, shard 5](https://github.com/mpmdw/JouleWise/actions/runs/43712204542/job/132806132428) | Pending |
| `tests.align.test_v4_registration.R1ExecutedSourceTests.test_condition13_changes_each_file_commit_and_missing_phase_module` | [PASS, shard 5](https://github.com/mpmdw/JouleWise/actions/runs/43712204542/job/132806132428) | Pending |
| `tests.align.test_r1_followup.DefaultBundleTests.test_default_member_bundle_equals_pre_callback_workload_bytes` | [PASS, shard 8](https://github.com/mpmdw/JouleWise/actions/runs/43712204542/job/132806132512) | Pending |
| `tests.align.test_r1_followup.DispatchTests.test_observed_timeout_runs_only_with_callback_and_keeps_null_reference` | [PASS, shard 8](https://github.com/mpmdw/JouleWise/actions/runs/43712204542/job/132806132512) | Pending |
| `tests.test_w1_reliability_r2.TerminalRestoreTests.test_normal_mode_zero_r1_chain_restores_both_before_delivery` | [PASS, shard 3](https://github.com/mpmdw/JouleWise/actions/runs/43712204542/job/132806132365) | Pending |
| `tests.test_w1_reliability_r2.TerminalRestoreTests.test_refusal_and_failed_readbacks_are_recorded_and_keep_owed_marker` | [PASS, shard 3](https://github.com/mpmdw/JouleWise/actions/runs/43712204542/job/132806132365) | Pending |
| `tests.test_w1_reliability_r4.HostCloseTests.test_hazard_unproven_chain_defers_both_settings_through_real_result_close` | [PASS, shard 8](https://github.com/mpmdw/JouleWise/actions/runs/43712204542/job/132806132512) | Pending |
| `tests.test_w1_reliability_r4.HostCloseTests.test_pre_off_refusal_does_not_enable_network_time` | [PASS, shard 8](https://github.com/mpmdw/JouleWise/actions/runs/43712204542/job/132806132512) | Pending |
| `tests.test_w1_reliability.OutcomeTests.test_nonzero_chain_exit_faults_result_hazard_and_courier_without_changing_go` | [PASS, shard 5](https://github.com/mpmdw/JouleWise/actions/runs/43712204542/job/132806132428) | Pending |
| `tests.align.test_v4_registration` module | [24 passed, shard 5](https://github.com/mpmdw/JouleWise/actions/runs/43712204542/job/132806132428) | Pending |
| `tests.align.test_v4_dynamic_closure`, including `LiveTraceTests.test_a_fresh_process_running_the_minimal_dry_run_stays_inside_the_committed_trace` | [10 passed, shard 5](https://github.com/mpmdw/JouleWise/actions/runs/43712204542/job/132806132428) | Pending |
| `tests.align.test_v4_executed_closure`, including `ExecutedClosureBindingTests.test_artifact_set_has_no_duplicates_or_missing_files_and_matches_template` | [6 passed, shard 7](https://github.com/mpmdw/JouleWise/actions/runs/43712204542/job/132806132451) | Pending |
| WP22 default, `tests.align.test_v4_w1_synthetic`, including `MinimalDryRunTests.test_minimal_synthetic_w1_reaches_the_desk` | [7 passed, 15 skipped, shard 3](https://github.com/mpmdw/JouleWise/actions/runs/43712204542/job/132806132365) | Pending |
| `tests.align.test_v4_opus_cold_witnesses.Wp22DryRunReachesTheDesk.test_minimal_synthetic_w1_produces_a_desk_record` | [PASS, shard 11](https://github.com/mpmdw/JouleWise/actions/runs/43712204542/job/132806132442) | Pending |
| WP22 full, `JW_WP22_FULL=1` | Unavailable from inspected issued-tree CI | Pending |
| Ordinary PREQUAL and `--w1-next w1` | Separate ordinary PREQUAL report and next-arm report unavailable from inspected CI | Both pending |
| RL-172(i) row 5 / RL-179 F-11 full synthetic launch-to-close with a consumer | No single matching run identified | Pending candidate CI job, test ID and log |
| Candidate sharded CI | No candidate SHA | Pending CI URL, checked-out SHA and tree |

All 15 issued-tree WP22 skips below share the `JW_WP22_FULL=1` opt-in reason. IDs are relative to `tests.align.test_v4_w1_synthetic`. Full mode also needs the actual outcome of `InjectedWindowTests.test_collector_death_is_x4_and_episode_continues`, marked `expectedFailure` on the issued tree for WP22 F3. Record its outcome explicitly, including an unexpected success.

```text
CleanWindowTests.test_all_members_succeed_without_exclusions
CleanWindowTests.test_clean_window_passes_the_signed_battery_consequence
CleanWindowTests.test_desk_energy_matches_independent_world_integral
CleanWindowTests.test_u1_u3_and_contrast_match_design
InjectedWindowTests.test_30b_u1_counts_the_x1_member_and_passes
InjectedWindowTests.test_clean_members_succeed
InjectedWindowTests.test_collector_death_is_x4_and_episode_continues
InjectedWindowTests.test_contrast_verdict_matches_design_rule
InjectedWindowTests.test_d_u1_counts_two_thermal_exclusions_and_fails
InjectedWindowTests.test_deadman_is_x7
InjectedWindowTests.test_desk_runs_on_a_window_with_failed_members
InjectedWindowTests.test_g0_timeout_ends_the_member_promptly_as_x2
InjectedWindowTests.test_malformed_xml_stops_and_is_excluded
InjectedWindowTests.test_os_level_nonzero_is_x1
InjectedWindowTests.test_u4_to_u6_inconclusive_in_w1
```

### Reproduce on approved bytes

Run Git comparisons from the report worktree. Put temporary objects under the seat directory by setting `GIT_OBJECT_DIRECTORY` to a fresh directory there and `GIT_ALTERNATE_OBJECT_DIRECTORIES` to `$(git rev-parse --path-format=absolute --git-common-dir)/objects`. For each rehearsal row, run `git merge-tree --write-tree --name-only --messages --merge-base="$merge_base" "$first_input" "$second_input"` with the three full OIDs in that row. Require exit 0 and the recorded result-tree OID. On exit 1, keep the conflict path names and stop that preview. For each component, `git diff --no-ext-diff --no-renames --name-only "$merge_base" "$head"` and `git diff --no-ext-diff --no-renames --name-only "$issued" "$head"` produce the two path sets. Use `git show -s --format='%H %P %T' "$head"` for provenance.

The following comparison accepts a full commit or scratch tree OID as its argument. In the signing-head run, supply the lead's full code or receipt-carrying **commit** OID. Run it again if either head changes. It extracts the list from the issued source, refuses both an identical endpoint and the issued root tree as a raw input, accounts for every path and exits nonzero at any mismatch.

```python
import ast
import re
import subprocess
import sys

issued = "b2e01464d6d4fbf2901ff4d4154df9455104a12a"
target = sys.argv[1]

def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()

if not re.fullmatch(r"[0-9a-f]{40}", target):
    sys.exit("REFUSED: target requires a full Git object ID")
kind = git("cat-file", "-t", target)
if kind not in ("tree", "commit"):
    sys.exit("REFUSED: target must be a tree or commit")
if target in (issued, git("rev-parse", issued + "^{tree}")):
    sys.exit("REFUSED: issued endpoint compared to itself")

source = ast.parse(git("show", issued + ":joulewise/align/apple/v4_registration.py"))
paths = next(
    ast.literal_eval(node.value)
    for node in source.body
    if isinstance(node, ast.Assign)
    and any(isinstance(name, ast.Name) and name.id == "R1_EXECUTED_SOURCES"
            for name in node.targets)
)
if len(paths) != 10 or len(set(paths)) != 10:
    sys.exit("REFUSED: issued census must contain ten distinct paths")

def blobs(object_id):
    result = {}
    for entry in git("ls-tree", "-r", object_id, "--", *paths).splitlines():
        detail, path = entry.split("\t", 1)
        _, object_type, oid = detail.split()
        if object_type == "blob":
            result[path] = oid
    return result

expected = blobs(issued)
if set(expected) != set(paths):
    sys.exit("REFUSED: issued tree is missing a census blob")
observed = blobs(target)
differs = []
for path in paths:
    if expected[path] != observed.get(path):
        differs.append(path)
        print("FAIL", path, expected[path], observed.get(path, "MISSING"))
print(f"{len(paths) - len(differs)}/{len(paths)} equal")
sys.exit(int(bool(differs)))
```

Use a fresh, detached checkout on the off-host CI worker. Record `git rev-parse HEAD HEAD^{tree}` and `git status --porcelain` before and after. A CI PR event's source `head_sha` alone cannot establish the checkout. Compare the executed tree to the approved tree and retain the immutable commit's own run for any gate that checks checkout identity. Run with Python 3.13, a scratch-only fixture root, the suite's `tests.host_command_guard` active in the parent and child interpreters, and fake host tools. Verify the expected failures, skips and host-guard diagnostics by ID. Keep raw logs in the authorized runner. Attach links and permitted test statuses to the report.

```sh
# Targeted signing and closure witnesses
python3.13 -B -m unittest -v \
  tests.align.test_v4_registration \
  tests.align.test_v4_dynamic_closure \
  tests.align.test_v4_executed_closure \
  tests.align.test_r1_followup.DefaultBundleTests \
  tests.align.test_r1_followup.DispatchTests \
  tests.test_w1_reliability_r2.TerminalRestoreTests.test_normal_mode_zero_r1_chain_restores_both_before_delivery \
  tests.test_w1_reliability_r2.TerminalRestoreTests.test_refusal_and_failed_readbacks_are_recorded_and_keep_owed_marker \
  tests.test_w1_reliability_r4.HostCloseTests.test_hazard_unproven_chain_defers_both_settings_through_real_result_close \
  tests.test_w1_reliability_r4.HostCloseTests.test_pre_off_refusal_does_not_enable_network_time \
  tests.test_w1_reliability.OutcomeTests.test_nonzero_chain_exit_faults_result_hazard_and_courier_without_changing_go

# Both WP22 modes, each in a fresh interpreter
env -u JW_WP22_FULL python3.13 -B -m unittest -v \
  tests.align.test_v4_w1_synthetic tests.align.test_v4_opus_cold_witnesses
JW_WP22_FULL=1 python3.13 -B -m unittest -v tests.align.test_v4_w1_synthetic

# Evaluator regressions on the accepted W1 repair
python3.13 -B -m unittest -v tests.align.test_rl145_part_c tests.test_part_c_gate_evidence

# Canonical split suite on an off-host runner
python3.13 -B scripts/shard_tests.py --workers 8 --split
```

- **Evaluator replay.** Capture the cases for missing G1 evidence, duration reconciliation, turn/source binding and conflicting flags on the approved repair. The W1 module's named anchors include `PartCGateEvidenceTests.test_every_later_admitted_turn_needs_its_own_release`, `PartCGateEvidenceTests.test_duration_reconciles_to_monotonic_bounds_before_a_total`, `PartCEvidenceReconciliationTests.test_reused_start_time_cannot_hide_a_hot_turn`, `PartCEvidenceReconciliationTests.test_failure_in_either_flag_source_or_later_interval_fails_both_roles` and `PartCMutationTests.test_no_single_evidence_mutation_can_pass`. On the final tree confirm the IDs still address the actual execution path. [Rebind test source](https://github.com/mpmdw/JouleWise/blob/b3b88c6965963beaeb413fd15b39fecca6e71eaf/tests/test_part_c_gate_evidence.py)
- **RL-179 launch-to-close.** Use one synthetic run through the approved candidate's launch, producer and consumer, terminal close and automatic desk, with a successful consumer using the producer's bound reference. Record the one CI job, synthetic test IDs and named terminal assertions, including restore/readback and close. The qualification branch's `tests.cadence.test_span_reference.RunnerThroughTheLegRuntime.test_three_legs_the_two_warm_ones_consume_l001` exercises the consumer and the runner's close boundary. WP22's `KitBridgeTests.test_consumer_custody_rebinds_to_synthesized_capture_bytes` exercises the W1 handoff. Keep these module witnesses alongside the single integrated-run log. [Consumer runner test](https://github.com/mpmdw/JouleWise/blob/0d03cb7833bb8b15bc391127a7fe5519b7d98602/tests/cadence/test_span_reference.py#L299) · [RL-172(i) row 5](https://github.com/mpmdw/JouleWise/blob/f9b03c33d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L17331)
- **PREQUAL.** On the authorized off-Mac setup, run the ordinary `scripts/align_v4_prequal.py` procedure for the W1 pin and require `prequal.json` status `pass`, exact clean checkout and matching implementation digests. Run `scripts/align_v4_prequal.py --w1-next w1 --output "$out" --series-projection "$series_projection" --deadline-projection "$deadline_projection"` with the lead's authorized arguments. Require `prequal-w1.json` status `PASS`, exact clean checkout and bound plan, triage, projections and implementation. Record blocking, PENDING and WARN rows by check. The off-host synthetic-fixture lane can exercise the probes and WP22. A full PREQUAL whose approved inputs or platform are unavailable stays pending. [Ordinary PREQUAL](https://github.com/mpmdw/JouleWise/blob/b2e01464d/docs/align/v4/PREQUAL.md#L144) · [W1 extension](https://github.com/mpmdw/JouleWise/blob/b2e01464d/docs/align/v4/W1-SMOKE.md#L50)
- **#813 signing edits.** Record the exact-head outcomes of `tests.align.test_rl182_registration.RegistrationEditsTests.test_each_of_the_seventeen_edits_appears_once_at_each_ruled_location` and `tests.align.test_rl182_registration.RegistrationEditsTests.test_named_power_script_reproduces_both_columns`, pending on the combined tree. Keep the lead's amendment diff and the Astra close alongside them. [Named registration witnesses](https://github.com/mpmdw/JouleWise/blob/802a29728138717653b2869e4859b955d632d800/tests/align/test_rl182_registration.py)
- **C1 release seam.** If the S-row builder and caller travel in the W1 receipt, record the exact-commit synthetic stored-records-to-word test for 102 and 101 out of 154, the caller ID and four bindings under RL-182 §1.5. Otherwise this stays a C1 gate. [RL-182 §1.5](https://github.com/mpmdw/JouleWise/blob/ab63e041fa324709991786c6a57b6ace69dac0e5/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19776)

The code-candidate suite and targeted commands were **not run in this seat** because the immutable approved bytes are pending. The historical CI checks listed above were inspected by name. Report-only verification covers the Git comparisons, reproduction, one-file scope and Markdown/diff checks.

## One proposed W1 transition

**Issued W1 `b2e01464d6d4fbf2901ff4d4154df9455104a12a` → lead-approved receipt-carrying W1 head PENDING.** Stage the authorized integration off the issued ref. Bring the approved qualification delta and any mandated desk follow-up onto the #734 basis, take the accepted W1 evaluator disposition and the RL-182-corrected S/Q amendment, and include #787 plus the caller in the same signing closure if both are ready and admitted. Record each required merge event. After R1 returns and its original identity is established, bind the frozen code/data commit, the receipt commit and the exact runtime tree. The lead owns stage A/B, C1(b), the required rule dispositions and the one closure regeneration for W1 signing. The lead records the actual signing-tree verifier return and its named test receipts before making the transition. The first native run on the new W1 pin is the one Part C, followed by the automatic desk and required hand-read. W1's separate native smoke has a 45-minute budget. [RL-149 step 13](https://github.com/mpmdw/JouleWise/blob/f9b03c33d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L12868) · [RL-151 §4.5](https://github.com/mpmdw/JouleWise/blob/f9b03c33d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L13538) · [RL-179 rows 8–11](https://github.com/mpmdw/JouleWise/blob/f9b03c33d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L18915)

Every **intermediate issued W1 pin** adds one Part C, about **2 h expected / 3 h 23 min worst case** on the old route, plus review and any scheduling wait. Use the approved pin's actual bounds when scheduled.

| If this group advances W1 separately before the final pin | Extra Part Cs |
|---|---:|
| #812 qualification | +1 |
| Evaluator repair | +1 |
| Desk follow-up | +1 |
| #787 row builder or its later caller when part of a separate W1 pin | +1 per changed pin |
| #813 S/Q amendment | +1 |
| #734 intermediate base merge or a separate receipt/repair pin | +1 per changed pin |
| #694 if a distinct W1 port is required and issued | +1 |

The proposed transition is **1 promotion / 1 Part C**. Qualification then final costs **2 / 2**. Qualification, evaluator then final costs **3 / 3**. Issuing each of the six register groups on its own pin, with the last group carrying the final receipt, costs **6 / 6** (about 12 h expected or 20 h 18 min at the old worst-case bound). A draft report, a CI merge object, #694 on R0 only, a qualification-only pin or a main-only ops change adds zero W1 Part Cs. The already-carried counted Part C and F0 run 11 add zero to this proposal. A later C1 receipt under RL-182 still carries the W1-line pin-change cost if it advances that line. [Pinned budget and carry](https://github.com/mpmdw/JouleWise/blob/211ff50330f6ba5223687306c7a76663406fdee7/RUN_STATE.md#L6149) · [RL-179 F-4](https://github.com/mpmdw/JouleWise/blob/f9b03c33d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L18713)

## NEEDS_SPEC and handoff

- **Q1, evaluator route.** The two frozen differences go to the evaluator integration owner and research lead. The owner can present a repair that preserves all ten while retaining the four HIGH repairs. Any proposal to carry the original artifacts across changed bytes or to obtain a new qualifying R1 run needs prospective research-lead disposition under RL-107. Adoption remains blocked on the failed comparison.
- **Q12/Q14, staging and signing authority.** The lead confirms the authorized merge events that satisfy pre-sign requirements and the permitted route for binding the private inputs. This report supplies Git evidence and test IDs.
- **Pending exact inputs.** Accepted evaluator SHA, admitted desk follow-up SHA, lead acceptance of edited #813, selected integration parents, immutable code SHA and tree, receipt-carrying SHA and runtime tree, candidate CI URL, full synthetic job and both PREQUAL receipts. The lead supplies the eligible combined bytes. Re-run the census first, then publish the named candidate-only test and CI evidence. Track original R1 identity and the actual signing comparison through the lead's dossier.
