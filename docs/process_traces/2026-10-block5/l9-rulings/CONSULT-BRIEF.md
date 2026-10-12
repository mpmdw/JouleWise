# Consult brief: lane L9 (the block-5 analysis code), four design questions before code

You are one of two blind seats. You do not see the other seat's answer. You are licensed to disagree with
anything in this brief and in the design, including its framing; the lead decides and records dissent.
Read-only: change nothing on the machine or in any repository; write nothing except the one report your
launcher names. Start no other agent (`claude`, `codex`), no background task, no network request, no `sudo`.
Run every probe in the foreground and finish in one session. Budget: about 40 minutes.

## What this is

Block 5 is a sealed, pre-registered measurement block. Its three analysed windows (packs ALPHA, BETA, GAMMA)
are collected and nobody has read a measured value. Lane L9 is the analysis program that will compute the
claim numbers. Its design is written and has had two critics; no code exists. The design is one file:
`/Users/edr/night-archive/gate-prune/wave-1007b/l9/L9_DESIGN.md` (SHA-256 `3465acf9…2e7d`). Section 0 defines
its terms. Your working directory is the repository's main at `3c05b8076`. The harvest program that produced
each window's archive is not on main: read it with `git show b039c0257:joulewise/b5/harvest.py` and
`git show b039c0257:joulewise/whole_window.py` (ALPHA's pin is `224a264c5`). Sealed texts:
`configs/campaigns/v5_claim_25g83/registration_block5.md` and `analysis_plan_block5.md`; the three admitted
errata are `docs/process_traces/2026-10-block5/{corpus18-erratum,sources-erratum,trigger-erratum}/ERRATUM.md`.

## Blinding (binding)

Until a recorded release event that has not happened, nobody reads an energy, a power, a phase duration or
anything derived from one. Do NOT open anything under `/Users/edr/night-custody/v5-b5-*`, `/Users/edr/night-b5/`,
`/Users/edr/night-g2a/`, `/Users/edr/night-archive/harvest-v5-b5-*`, or any runs root of the measurement clone
under `/Users/edr/night-custody/measurement/`, and run no program over them. Nobody opens `derived/flags.jsonl`,
`derived/exclusions.json` or `derived/window_flags.json` of any attempt, or an archive's `sources/` or
`withheld/`. Your report carries structure only: no energy, power or duration of a real window, no member's
name. Made-up numbers are allowed and labelled made-up. The owner's name and address go into no file and no
request. Do not read `RUN_STATE.md`, CLAUDE.md files, `docs/orchestration.md` or decision logs.

## Questions

**Q1 (the design's O2; the main question).** The analysis plan (section 11, row L9-NEG8, near line 744)
requires one design round by two different model families before code for the validator change. Read the
design's sections 3.5 (the archive context and "answered conditions") and 4.5 (L9-NEG8 as changed), with 9.2
(the design's own strongest objection). Every block-5 stored verdict row reads failed, and the row validator
(`joulewise/whole_window.py`) today refuses every claim on such a row. The design lets the validator set a
stored condition aside when a record of the harvest archive has decided the same thing again. Your task:
**name a row that this validator would admit and that should not bear a number.** Concretely, try to
construct, from the code on main and at the pin, a stored verdict row plus archive state for which (a) the
design's table in 3.5 answers every stored condition, and (b) some member, reference or window that the
sealed registration or an erratum removes still contributes to a number or to a drift allowance. Check in
particular: the cache keyed without an archive identity (`whole_window.py` near 6210 to 6257); the path with
`archive_context=None`, which must behave byte for byte as today; a member reason whose named member is a
NEG-8 reference or spare; the Erratum 2 item 9 replay standing in for the membership check; a row whose
conditions list holds a condition the table does not name. If you find no such row, say what you checked and
what would have to be true for one to exist. A separate cold judge is ruling which condition families may be
set aside at all (the design's J1); do not rule that, but say if your finding depends on it.

**Q2 (the design's O6).** At finalization, the custody check stops when a historical calibration capture
file listed in the ledger cannot be read. The registration (near line 4444) says of the harvest's disclosed
flag: "A file that cannot be read is not evidence of a change, and the ledger's hash chain and pin are still
checked". The design proposes: on a block-5 root, verify the window's own two captures and the hash chain and
pin for the rest; an unreadable historical capture is a recorded flag, not a stop. Is that safe? Name the
case, if any, in which an unreadable historical capture could hide something that changes a number of this
block, and what the check must keep to exclude it.

**Q3 (the design's O13).** The load-correlated sensitivity line (analysis plan lines 529 to 536). The design
proposes, for a contrast: the mean difference and its metrology interval over the restored quads with
"(n = …)", and no Holm test, floor decision or outcome word, as the registered battery-assist contrast line
does (plan 558 to 561); for reported cells: the mean, half-width and counts as the plan's example; no line
for floor cells. Does the plan's text support that, and is anything a reader needs missing?

**Q4 (open).** Read the stage graph (section 5) and section 6 (files every window executed). Name the single
most likely way this build puts a wrong number into the paper without any test or gate noticing, and the
cheapest check that would catch it.

## Report

For each question: your answer in one or two lines first, then the evidence (file and line; what you read,
what you executed). Label anything you did not verify. End with the line `RECOMMENDATION:` followed by one
paragraph: what the lead should change in the design before stage S3's code is written.
