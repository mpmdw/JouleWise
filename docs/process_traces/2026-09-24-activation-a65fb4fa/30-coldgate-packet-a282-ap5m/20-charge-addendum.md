# Charge — addendum to cold gate A282-AP5M-01: rule the paired refuter's objections to the final texts T-1..T-23

Assembled 2026-09-24 by the resident magistrate (Opus 5.5, activation a65fb4fa). Nothing is armed. Round 1 of this gate: charge `00-charge.md`, ruling `10-coldgate-fable-ruling.md` (cold Fable judge), and the paired Opus contract refuter `11-opus-contract-refuter.md`. The refuter attacked T-1..T-23 as an analyst replicating the analysis and an estimator implementer would have to apply them. It reports 17 findings, each with a counter-example and a replacement text, and states AGREE for the rest. The magistrate takes no position. The ruling binds the next draft's text; Ed adopts claim policy (his E2).

## Terms in plain words

The terms are as built in `00-charge.md` §"Terms" and the draft exhibit `ex-a65-07b-a282-ap5m-draft-v2.md`.

## Questions (for each: AFFIRM the ruling's text / ACCEPT the refuter's replacement / write a better text / reserve for Ed; give the final exact text)

- **A1 (refuter R1, BLOCKER).** T-3 G3 checks a block against one problem's worst case, so the gate cannot pass.
- **A2 (refuter R2, MATERIAL).** T-10's δ_upper is a two-point estimate with no noise allowance; a near-zero value turns off the drift check.
- **A3 (refuter R3, MATERIAL).** T-10 leaves open which cell `budget_j` comes from and at what n.
- **A4 (refuter R4, MATERIAL).** With T-13's per-night index, K22 can leave a night's offset uncancelled.
- **A5 (refuter R5, MATERIAL).** T-8's Holm membership list is incomplete.
- **A6 (refuter R6, MATERIAL).** T-14 cannot hold for problems left with no counted attempt.
- **A7 (refuter R7, MATERIAL).** T-15 and T-17(ii) disagree on when `s_per_token_upper` is falsified.
- **A8 (refuter R8, MATERIAL).** T-3 and T-10 add pilot-set values that K2 and §2.1 forbid.
- **A9 (refuter R9, MATERIAL).** T-3 names one shakedown night, but M13 allows one thinking arm per night.
- **A10 (refuter R10, MATERIAL).** T-4 and T-5 never say where each window's `anchor_j` comes from.
- **A11 (refuter R11, MATERIAL).** Standing K9 and K19 text contradicts T-1.
- **A12 (refuter R12, MATERIAL).** T-3 G2 lists "malformed" as a failing stop reason.
- **A13 (refuter R13, MATERIAL).** The code rules left standing in 45/21 §7 would refuse T-13's and K22's new paths.
- **A14 (refuter R14, NIT).** T-20 gives "window" a second meaning.
- **A15 (refuter R15, NIT).** T-7's promise that "the interval can be rebuilt exactly" is not met.
- **A16 (refuter R16, NIT).** T-21's "only by" is wrong about the importer.
- **A17 (refuter R17, NIT).** Four smaller gaps in the floor, level-status and interval texts.
- **A18.** Anything else in T-1..T-23 that the refuter's reading exposes.

Finish with one consolidated list, **"Final texts (paste verbatim into v3; supersede the named T-n)"**, so the draft quotes one place. Tier findings BLOCKER / MATERIAL / NIT.

## Constraints on the judge

Read-only; nothing armed. Never run `sudo`, `launchctl`, `powermetrics` or `systemsetup`. Never touch `/Users/edr/code/JouleWise` (canonical root), `/Users/edr/night-custody`, any `/Users/edr/JouleWise-measurement-*`, or `~/Library/LaunchAgents`. Write only the ruling file. Read the files in this packet directory only; do not read any other `docs/process_traces` file, or RUN_STATE.md, TASK_QUEUE.md, council logs, run reports or memory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
b8a7525abac7680a4a162babd941ed3b2319f5a36c1ac7a68f5cbb208884f02c  00-charge.md
62f2bd4d78ab788e93fdddae67488814f35efb608862a0d0e7b952932d207733  10-coldgate-fable-ruling.md
95cee3717f7279451319840a4551edc22ca785c848d93503ba22820ff2b5e6e4  11-opus-contract-refuter.md
9a36101bd90367de6d2c208c8dd78760098485d49ff5a4429f9a9014858c7719  ex-1d37-09-headline-packet-b-scored-night.md
0d1430bae90e55e65bcc9397e741f3a1cd6cde6cc9f34606488685bd8eff6f0d  ex-1d37-10-headline-packet-c-ap5-amendment.md
9668c50f764fb3f0688f56eedf36781bf3b89e7f64002d5d57af36d5f26b31a1  ex-1d37-18-headline-opus-integration.md
5134d0d89cc239c1c4972967e0a2c620cb55c387b521e222e5c70eb43d966104  ex-1d37-19-headline-integration-synthesis.md
55034d78b8e8ac2de4a0b5ae3f5ce1317ed8051e3c04c63273cfba3bcf5945b8  ex-1d37-40-fable-ruling-math.md
a2aec780860bbe5aa2c47ca9dc2ff5905438b0e1a3ac5f2968cb41d2aabe834b  ex-a65-07-a282-ap5m-draft.md
4f026ec118ffd677a1ec15c9ed5db6a4fd164e43ed3600c94686cce20b37a8ad  ex-a65-07b-a282-ap5m-draft-v2.md
3e046b298e2b294fc0d64a62982a606fa793762c2384b12ff486d1b1535c70d2  ex-a65-11-a282-fidelity-sol-lens.md
b25aa48c7bdc0468df6ae8d48c2782eb3d16541b047224ad636ffca4a2b43dfe  ex-a65-12-a282-pedagogy-opus-lens.md
45cb622cd20d9f4c4dac16e5cc058dcd8a73d48adbaae2c1a68c912bab609638  ex-a65-16-a282-v2-fidelity-delta-brief.md
846068445f6414334b98e22b6fc2cad88088e13f762834e90f568143d6d5e2c7  ex-a65-17-a282-v2-fidelity-delta.md
d64156a15f165f6bb773c427213a1f1f55442c3132bed8e9fe5c062093edcbbe  ex-a65-18-a282-v2-pedagogy-delta.md
715952a0e7a0c51be1cff131b4868b2e6873a4aaf17a1a673a99e7469bbf5b6b  ex-d8cc-08-a281-round1-synthesis-and-rulings.md
685730701d04829e1f50097d135388561778ee1c8aa8e88345208015334a943e  ex-d8cc-20-a281-opus-consult.md
4820950722be484c7ad1925aac328689014a5ddfb2747ea5d56ec65b696fb710  ex-d8cc-21-coldgate-packet-a281-00-charge.md
b8a66c41a1ede0e8df065956c176b2c86f2260110daf449853b3a13269050e2d  ex-d8cc-21-coldgate-packet-a281-10-coldgate-fable-ruling.md
02c55d4e5c135e90172deff0ca3307b0fa06dfa1267358716f0943b8ce88d2e0  ex-d8cc-21-coldgate-packet-a281-11-opus-contract-refuter.md
9fc61ee0765f37516580c1c8972b85638d61e1333a420691f9b30dd214d38b7a  ex-d8cc-45-coldgate-packet-a281a-recut-10-coldgate-fable-ruling.md
005c0c96ffe54885fbb0e4f37a6b2b25bea76f245d5e39dfae87ac9667ebfc84  ex-d8cc-45-coldgate-packet-a281a-recut-21-coldgate-fable-addendum-ruling.md
8a26356142bc15bcc09910bdcc43621336c41a1c808652ceba185b6b425ea0d1  ex-repo-docs-contracts-analysis_plans.md
fd32bd2279744376128cf3bf9df8b4c5cc30098db365e0a427d46127eb10097a  ex-repo-docs-decision_log.md
f9da074738d9a820894dfb58fc03713c0a5cffdb38fb2aa2f2cf110d82714ae1  ex-repo-docs-paper-artifact-guide.md
5e2bfb7f688304bde97b5af5d8b1bdcda13e91a6584f5f2ed877262f84159d89  ex-repo-docs-phase_2-detection_floor.md
dfe84c02df40193ac3c89672a9bf93704fd6d8735f7218e9c7d103c28fda72e1  ex-repo-docs-phase_2-suite_implementation_research.md
29d6e84ea136569a9452364a36ada61c620a462a9642f16b157eb00eaf799857  ex-repo-docs-research_question_bank.md
bdb165fd9052302a3ae5d4a22fe69b581105d15dfd9e5832c917dcb9eef1c391  ex-repo-joulewise-benchmark_import_math.py
```
