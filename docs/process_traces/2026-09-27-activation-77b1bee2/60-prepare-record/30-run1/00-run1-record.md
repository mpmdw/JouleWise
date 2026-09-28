# Prepare step, run 1 (the only run), recorded verbatim (statement item 2(f))

- **Time:** 16:25:42 → 16:26:39 PDT 09-27.
- **Where:** run from the run checkout `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2` at commit **`e7c8bcc68d9a1c4f20e11c1904e49552c81ffcd1`**.
- **Tool:** sha256 `21b2eea8c64e5fe1ca41474927e2b15471ceb11f2bd7e5f31b89445d3f53060c`.
- **Interpreter:** `.venv/bin/python` (Python 3.13.1).
- **Command:** `run1-command.txt`. It is the statement's item 2(a) command plus exactly two ruled arguments: `--corpus-root /Users/edr/night-custody` (ruling 71 §6.4 / item 2(c)) and `--predecessor-acceptance configs/calibration/calibration_acceptance_d079_v2_n17_r7.json` (PREDECESSOR-PATH-01).
- **Output** (`run1-output.txt`, whole):
  - `candidate written (NOT ISSUED): …/candidate_acceptance_25g83.json`
  - `corpus n: 12`
  - `screen_rule: floored_range_envelope_screen`
  - **rc 0**

**Post-run checks** (ruling 71 §8.11, PREDECESSOR-PATH-01 C6, R3; `post-run-checks.txt`):
- The candidate's sha256 is **`dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2`**. A byte copy is kept here as `candidate_acceptance_25g83.json`.
- `verify-members --corpus-root /Users/edr/night-custody` printed **12 PASS lines, rc 0**.
- No string in the file begins with `/`.
- `derivation_notes.predecessor.relative_path` is `configs/calibration/calibration_acceptance_d079_v2_n17_r7.json`, and its `file_sha256` equals the r7 pin.
- `candidate_not_issued: true`, and the `member_custody` note is present.
- **The custody digest list after the run is byte-identical to the list before it** (20,527 files; R3 holds).

**R9 disclosure.** The issuing tool was repaired after capture and before any B value was read (PR #436, council synthesis `50-custody-outside-repo/30-lead-synthesis.md`, final-diff ruling `50-custody-outside-repo/71-coldgate-final-diff-ruling.md`). The fixed command was amended by one argument before any value was read (PREDECESSOR-PATH-01).

**Rule outcomes recorded in the candidate.** This is the first reading of any value, after the step. The science gate rules on them.
- `bracket_screen_s` (S) = 0.013701, from the range 0.013701485…, quantized; not floor-bound.
- `preflight_level_screen_s` = 0.038078579302948.
- `headroom_status` = positive_headroom; `excursion_member_count` = 0, so there is no `excursion_limited` mark.
- **`screen_challenge_member_count` = 2** against the r6 threshold 0.032898493715362.
- `new_maximum_exceeds_prior_maximum_plus_range` = False; predecessor ceiling 0.010164834757777545.
