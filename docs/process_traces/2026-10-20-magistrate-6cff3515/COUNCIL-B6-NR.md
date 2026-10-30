# Council seat brief: two BYTES registration questions (activation 6cff3515, 2026-10-20)

You are one of two blind seats; the other seat is a different model and you will not see its answer. The lead writes
the ruling from both. You have licence to disagree with any text below, including the framing of the questions.

Code: JouleWise public clone. Fetch `lane/2026-10-20-bytes-integration` (d924e7acf) and, on JouleWise-data, the branch
`claude/bytes-b6-registration` (4101114): apply `ports/b6/*.patch` with `git am` on d924e7acf in a scratch worktree to get
the draft `docs/registrations/bytes_pack_v1.md` (B6's report: `reports/b6/REPORT.md`, section NEEDS_RULING). Governing
texts, later winning over earlier: BYTES ruling R1-R8 and Addenda 1-8 in `docs/design/bytes_pack_design.md` @ 298a292a7
(fetch `lane/2026-10-15-bytes-build`); the 2026-10-20 blinding ruling in
`docs/process_traces/2026-10-20-magistrate-4b350f47/RECORD.md` §"Ruling" on main; block 5's registered arithmetic wins on
arithmetic. `JW_B5_SYNTHETIC_ONLY=1` for every run; no real archive or key directory.

Project rules that bind your answer: physics refuses, every non-physical condition is a recorded flag; no change to
registered arithmetic or exclusions after data are seen; if a registered rule proves too strict, print the registered
result and a labelled alternative beside it; every number carries its derivation.

## Q1. One pass's withheld file is missing

Blinding ruling item 4: a missing withheld file is a flag and the model prints `missing`, never a refusal. Addendum 7
D9 (a): when one pass of a model refuses and the other computes, the surviving pass is the model's point (`one_pass`).
When one pass's withheld file is missing and the other pass's rows are present, does the model print `missing`, or the
D9 (a) one-pass point (flagged)? Both passes missing?

## Q2. A fix to `bytes_analysis.py` between the stage-1 commitment and held-out key release

The stage-1 commitment pins the module's sha256 (Addendum 4 item 8(d)). `--stage heldout` rebuilds `frozen_predictions`,
which embeds the current module's sha256, and refuses unless it equals the committed file (`scripts/bytes_analyze.py`,
"frozen line/fit-point mismatch"). Blinding ruling item 3 places a real-data held-out agreement run (twin vs module)
after the commit and before held-out keys. If that run finds a module defect and the module is fixed: is a second
commitment made before held-out release, and how are both printed? What, if anything, must the code change so the
original commitment stays evaluable?

## What to do

Run the code to settle each fact you rely on (synthetic campaign `tests/fixtures/bytes/campaign.py` through the real
stage chain; show the refusal or the output). For each question give: your answer in one paragraph; the facts you executed
with commands and outputs; which data count and what prints under your answer; the smallest change to the registration
text and code. Report on JouleWise-data branch `<your branch>` file `reports/b6-nr-council/<seat>.md`, first line your
model id. Do not edit JouleWise.
