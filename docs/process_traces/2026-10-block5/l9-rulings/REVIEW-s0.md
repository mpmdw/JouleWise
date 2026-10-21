# Stage S0 (window index, attempt reader, archive handle): independent review and dispositions

Reviewer: a Sonnet 5.5 agent that did not write the code, executing lens, commit `11e56c010`. Its run: the
four fast modules pass (51 tests); it did not run the fixture-shapes module (the lead did: 13 tests pass).
Probes and mutants: `/Users/edr/night-archive/b5-consults/l9-rulings/s0/review-scratch/`. No blocker. It
verified `seal_pins.json` against the seal record's text and against the git objects (four heads, 13 file
digests, eight sealed digests, both epochs), and the frozen-file test against all 388 files.

| # | Finding (executed unless marked) | Disposition |
|---|---|---|
| S1 | The index's `pack` label is bound to nothing: a BETA archive indexed as `gamma` is selected as the analysed GAMMA window | Fix: `plan_id` must begin `v5-b5-<pack>-a<attempt>-`, and `pack_id` must be the sealed pack directory's id for that pack (`window_index_pack_mismatch`) |
| S2 | A gap in a pack's attempt numbers loads, so an omitted earlier attempt silently changes which window is analysed; t0 order is not checked against attempt order | Fix: per pack and seal the attempts are exactly 1 to n, with t0 non-decreasing (`window_index_attempts_incomplete`) |
| S3 | Documents that authenticate and disagree all load: `window_flags.json` naming another attempt, plan or pack; `release_blocked` differing between the two documents or from "an unclassified code exists"; `claim_usable` true with reasons present; `harvest.json` window reasons present while claim-usable; flag totals differing | Fix: each equality is checked (`attempt_record_inconsistent`). `flags.unclassified` is read |
| N1 | Malformed fields raise raw Python exceptions; a string of reasons is read as characters; the step-4 classifier raises on a malformed spec | Fix: refusals with codes; element types validated |
| N2 | Five mutants survive the tests (the second-seal filter; the symlink bound; the records-against-index order check; the p42 equality turned into subset; the digest pattern of `outputs` values). The code is right in each case | Fix: tests that kill all five |
| N3 | Only `select_analysed_attempts` enforces the selection; a caller can build an analysed window from any claim-usable record and open it | Fix: `open_archive` accepts only a window the selection produced (a module-private token), tested |
| N5 | Relative roots load and would resolve against the working directory; a string given as the superseded-roots list becomes characters; a `no_archive` entry may say `COLLECTED`; t0 has no range check | Fix: absolute paths only; types checked; `no_archive` is never `COLLECTED`; t0 positive |
| N6 | `status_lines` is tested with `!= 0`, so `False` passes | Fix: the type is `int` and not `bool` |
| N7 | The step-4 classifier requires all p42 cells refused, stricter than the plan's "only the p42 floor cells" | Kept, recorded: stricter can only stop more. Stage S10 revisits it with the real extractor's exit |
| N8 | The one-window pin exception of ruling J4 item 6 needs `plan_id` passed to `governing_pin` and the hard-coded shape names generalised | Deferred to the lane that would need it (only if a tripwire fires) |
| N4 | `output_bytes` will serve `derived/flags.jsonl` (listed under `outputs`, restricted) | Kept: ruling P9 bounds what a program lets out, not what it reads |

Fix round (Sol 6.1): every row marked Fix is built and tested on the lane (`83c1e0f1c`); the lead's run of the four fast modules: 82 tests pass; the seat's 30 mutants are caught. The tightened readers refuse the older synthetic windows of three test files; their migration is a separate brief (`BRIEF-sol-migrate.md`).
