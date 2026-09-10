# 11 — Dated addendum to cold-gate ruling 10 (packet 31): Opus pairing refuter amendments A1–A5, recorded 2026-09-10 ~07:25 PDT

Opus contract-lens refuter (rule 11 pairing; its full report is `12-opus-pairing-refuter-on-ruling-31.md`) verdict:
**UPHOLD WITH AMENDMENTS.** The magistrate records the amendments as this dated addendum; the verdict (item 5 MET with
registered follow-up NIGHT-STREAM-PATHS-01) is unchanged and the resident magistrate overrules nothing.

A1 (authority; closes R-1/R-2). The kernel carries the literal compression too, at
`/tasks/NIGHT-REHEARSAL-01/dependencies/1/required` ("… nothing written into `night/` (item 5) …"). That phrase is read
henceforth as the Q2 predicate, on the same ground as the 61→65→67 gloss: "written into `night/`" means written by the
driver. The ratified upstream authority, the coldgate-d1 R-7 amendment
(`docs/process_traces/2026-09-01-unattended/coldgate-d1-RULING.md:115–123`), is driver-scoped in terms — "before it, the
dead-man writes nothing but a log line and exits GO" — and its stage-2 acceptance case says only "the pre-night 07:00
firing is observed standing down". No text upstream of synthesis 65 requires `night/` to be empty, and no decision-log
entry or Ed ruling ever ratified the "holds nothing" formulation as a criterion.

A2 (probe 8 corrected; closes R-3). `tests/test_run_night.py:816–817` ASSERTS the template contains
`@@CUSTODY_ROOT@@/night/@@LOG_STEM@@.out` and `.err`, pinning the stream paths INSIDE `night/`; the render test at
1504–1505 asserts only that the night and dead-man paths differ.

A3 (follow-up scope; closes R-3/R-4). NIGHT-STREAM-PATHS-01: render `StandardOutPath`/`StandardErrorPath` outside `night/`
(for example `@@CUSTODY_ROOT@@/launchd/@@LOG_STEM@@.out`), with `scripts/install_night_agent.sh:125` extended to create the
new directory as well as `night/` (launchd cannot open a stream path whose parent does not exist),
`tests/test_run_night.py:816–817` amended to the new template strings, a new assertion that neither rendered path starts
with `<custody_root>/night/`, and the harvest rows updated to preserve the courier transcript from its new location;
historical traces that name `night/launchd.night.out` are not edited. Not a gate on the 09-11 harvest or the 09-12 arm.

A4 (P3 timing; closes R-5). P3 is evaluated on an inventory taken strictly before 07:00 PDT on 09-11 (epoch 1789135200).
At or after that instant the 09-11 dead-man firing may have re-opened and written through the same two handles on a
failed-courier night — a post-completion event outside item 5's object — in which case P3 is evaluated on the earliest
inventory taken before it, or, failing that, on P1/P2 plus the absence of any pre-t0 driver record, with the handles'
state recorded as post-t0.

A5 (Q3 expectation and probe 9; closes R-6/R-7). `launchd.night.out` is expected NON-empty (the courier is spawned with no
stdout redirection, `run_night.py:811–815`, and inherits launchd's handle); `launchd.night.err` is expected EMPTY (the
09-09 harvest recorded it at the empty-file digest `e3b0c442…`), and non-empty stderr is a finding for item 6. The only
`night_dir` checks on the run path are `_existing_record` by name (962, called at 1068, 1430); the file's one
custody-root enumeration, `control.rglob('*')` at 1316, belongs to `produce_g7_control`, a post-night command against a
separate fresh control root.

Also noted by the refuter (nit R-10): P1's `[F, F + 60 s]` window is retrospectively safe for the observed 09-10 firing
(F + 2.09 s) but brittle as a general form after a machine sleep; carried into NIGHT-STREAM-PATHS-01's notes, no change.
