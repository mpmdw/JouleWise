# Charge — cold confirm WAVE-CONFIRM-01: the exact merge heads of PR-L and PR-R after their final passes

Assembled 2026-09-25 12:27 PDT (clock-read) by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed. The relaunch contract requires a cold Fable verdict on the exact merge candidate. Both heads moved after their final passes, so this confirms the moves.

## The two heads

- **PR-L** (PR #412, `feat/2026-09-25-acc-launch-context`).
  - PRL-FINALPASS-01 ruled MERGE on `99495ba9` (ruling: `docs/process_traces/2026-09-25-activation-152c9255/24-finalpass-packet-prl/20-fable-final-pass-prl.md`, in the head).
  - The head is now **58d9ddc3**. The delta has two parts:
    - (i) a test-fixture fix for a Linux-only hosted-CI failure (`ex-01`, the full non-records diff). Two installer tests failed under the runner's UTC timezone, because the fixture rendered the probe receipt in the test process's timezone while the installer subprocess runs with `TZ=America/Los_Angeles`. The bench runs `tests.test_install_night_agent` OK under UTC, Los Angeles and Tokyo, and the seven PR-L modules OK under UTC (613 tests; record 00 item 84);
    - (ii) a records-only commit.
- **PR-R** (`feat/2026-09-25-acc-registration-rev5`).
  - PRR-FINALPASS-01 ruled FIX-FIRST; F1–F3 plus the ratified A-R5a-1 were applied at `2bbcc779`, and a one-lens conformance audit found CONFORMS (`docs/process_traces/2026-09-25-activation-152c9255/15-prr-review/06-final-conformance-lens.md`, in the head).
  - The head is now **e77ec15d**, a records-only change (`ex-02`).
- **Gate row 9:** `ex-03`, the full suite at the first integration tree: 7,166 tests, one known timing flake and one known live-census parse defect, both passing alone. `ex-04`, the focused re-run of every delta module on the final integration tree: 674 OK.

## Questions

- **C1.** PR-L: verify `git diff 99495ba9 58d9ddc3` outside `docs/process_traces/2026-09-25-activation-152c9255/` equals ex-01. Say whether that test-only fix is correct and weakens nothing the final pass relied on. Run `TZ=UTC python3 -m unittest tests.test_install_night_agent` at 58d9ddc3 in a /tmp clone. Rule CONFIRM MERGE of 58d9ddc3, or not.
- **C2.** PR-R: verify `git diff 2bbcc779 e77ec15d` is records-only. Rule CONFIRM MERGE of e77ec15d, to be merged after PR-L, or not.
- **C3.** Is row 9 adequately evidenced by ex-03 plus ex-04 for this wave? Yes, or the exact additional run required.
- A 2-line summary.

## Constraints on the judge

- Read-only.
- Never run `sudo`, `launchctl` or `powermetrics`.
- Never touch `/Users/edr/code/JouleWise` (the canonical root) or `/Users/edr/night-custody`.
- The discovery suite and background tasks are not allowed.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs or memory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
02537836140d694ecc484388059042f57dd75451293a149e364d54d36e694030  ex-01-prl-post-finalpass-code-delta.md
e54814a4c34cc18562e99fbe5ef93e503bb856382d3b9203bf29218f797bb200  ex-02-prr-post-conformance-delta.md
0a7a0c08b3fc0d16882a6e48377bec86f9c5b25b620cfa9df5a94fc6054f3bb9  ex-03-fullsuite-summary.md
2c5582637069bd484637789b9f0f57bc2ee64d310635dedf12964935565e0c47  ex-04-focused-integ2.md
```
