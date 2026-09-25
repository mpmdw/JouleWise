# Charge — cold gate ACCEPTANCE-25G83-02: rule the reopened D-184 council on the launch-context cure

Assembled 2026-09-25 ≈04:50 PDT by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed.

## Background in plain words

Every science measurement night needs a calibration acceptance that is bound to the live macOS build. This machine runs 25G83, and the active acceptance, r7, is for 25F84.

On the 09-19 nights, `powermetrics` delivered samples about every 0.245 s instead of r6's ~0.120 s, and 13 of 24 calibration captures failed. The prior cold ruling (`ex-31-prior-acceptance-ruling.md`) treated that slowness as a property of the OS build and cured it with 2 s pulses (protocol v4), a science-neutral reissue r8, and a Revision 4 registration.

An interactive seat, working with Ed present, then measured the real cause, recorded in `docs/process_traces/2026-09-24-interactive-4b/` (records 01, 21, 24, 26–29). The night job's launchd plist has no `ProcessType` key, so macOS coalesces its timers. Marking the job `ProcessType=Interactive` gives ≈132 ms.

A four-model council answered the reopened question (`ex-00-question.md`): Sol `ex-02-seat-sol.md`, Astra `ex-02-seat-astra.md`, Opus `ex-02-seat-opus.md`, Fable `ex-02-seat-fable.md`. The magistrate's synthesis and proposals are in `ex-30-synthesis.md`: U1–U8 unanimous, F1 a fact found by two seats, S1–S10 splits with a proposal each. You are the cold judge. The seats and the synthesis are arguments before you, not authorities.

Ed's standard, verbatim: the orchestration exists for "preventing bad science, not progress on the paper when models agree". On this exact question (09-19): "make sure the barriers to acceptance aren't overly strict for no reason". Under the D-184 addendum (Ed, 2026-09-24), the four-model council decides experiment design; Ed owns only hardware, sudo, a notice NO and claim publication.

## Questions (for each: AFFIRM / write a different ruling; give the final text; tier concerns BLOCKER / MATERIAL / NIT)

- **J1.** U1–U3: the cure (A), with the installer refusal and child inheritance. Verify the interior geometry against `joulewise/powermetrics_fiducial.py` and at least one raw-data recomputation of the Interactive and default cadence distributions. The data are read-only under `/Users/edr/osctx-mvp-01/` and `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/`.
- **J2.** F1: the n1/n2 same-epoch disposition. Verify `scripts/issue_calibration_acceptance_generation.py:1273-1290` and the D-126 disposition mechanism in `docs/decision_log.md`. Rule the exact mechanism and text.
- **J3.** S1: whether to take the equivalence path (D-102 addendum, prereg `:421-470`). Check Opus's P(PASS | identical distribution) ≈ 0.48, and the magistrate's claim that a FAIL night counts as W1 under the existing rule, which makes the path cost no extra window.
- **J4.** S2–S5: the real-path check, the display state, the W1 stops, and the excursion refusal. Check Opus's 8.7 % versus 0.5 % false-stop figures.
- **J5.** U4, S6, S8–S10: the v4 salvage (in particular, whether any salvaged part touches the D-138 pin set, `docs/decision_log.md` ≈`:10361-10375`), the simulation re-run, the revision number, the PR shape and order, and the fallback trigger.
- **J6.** U5–U7, §4 and §5: the history and disclosure, the window conditions, authority, the rules-before-data note, and the order of steps. Also anything the synthesis dropped or merged wrongly.

Finish with **"Acceptance rulings v2 (final texts)"**: one numbered paragraph per ruling, executable without choosing, plus a plain-language summary of at most 10 lines for Ed, with no project shorthand.

## Constraints on the judge

- Read-only; nothing is armed.
- Never run `sudo`, `launchctl`, `powermetrics`, `systemsetup` or `pmset`.
- Never touch `/Users/edr/code/JouleWise` (the canonical root), `/Users/edr/night-custody`, any `/Users/edr/JouleWise-measurement-*` directory, or `~/Library/LaunchAgents`. Archived data under `/Users/edr/night-archive` and `/Users/edr/osctx-mvp-01` may be read.
- Repository evidence may be read in your worktree, including `git show origin/feat/2026-09-24-acc-25g83-v4-rev4:<path>`.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, run reports, memory, or any `docs/process_traces` file outside this packet directory, except `docs/process_traces/2026-09-24-interactive-4b/`, the 2026-09-24-activation-278ebc9e directories `31-coldgate-packet-acceptance/`, `38-coldgate-packet-acc-replay/` and `19-desk-simulations/`, and the held v4 branch's own files.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
a8288e7cef7c11370be1f651987b91f3e512f3acae5ce5a07a833092e32a271e  ex-00-question.md
fc74dfd96b188469d5368ce70efe06977fc4e9625d537a8375ad1ef50f601e5e  ex-02-seat-astra.md
7a645a389c16f29b0be8536138308740d8401794ff525ac86b19dbe9f8c1f5e4  ex-02-seat-fable.md
81f01c38e4f099541eba0f45c9d3f44363f94e5f094e6aa65d987e604a2ff852  ex-02-seat-opus.md
51c0f00f012b8f2e6295a34831d2e61f08169e7f436cdabb7cf18f19db9f8a41  ex-02-seat-sol.md
581690f18c56b6e0c0a90ca49e2ec714985eb879592dd64076d0e4e691ff924a  ex-30-synthesis.md
b8e5a98de55f8622f4fe5754e3368cbc2955b3de410b3ac77450734034ee1e8f  ex-31-prior-acceptance-ruling.md
```
