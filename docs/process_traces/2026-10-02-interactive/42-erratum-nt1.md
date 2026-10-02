# Erratum E-NT1 to Revision 6 of the 25G83 registration: the network-time OFF receipt's wording

Status: **ADOPTED** by a cold erratum gate on 2026-10-02 (judge: Claude Fable 5.1, cold, detached
worktree at `35515f83`; refuter: Claude Opus 5.5, independent findings first, then **AGREE**).
Recorded by the D-138 seat (Opus 5.5, headless orchestrator seat for the D-138 transaction). The
sealed registration file `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` is not
edited (sha256 `d0034003…7b78` unchanged); this record is the erratum.

- Charge: [40-erratum-nt1-charge.md](40-erratum-nt1-charge.md); refuter charge:
  [40r-erratum-nt1-refuter-charge.md](40r-erratum-nt1-refuter-charge.md).
- Ruling: [41-erratum-nt1-ruling.md](41-erratum-nt1-ruling.md) (first lines
  `ERRATUM E-NT1: ADOPT …` and `CHAIN: WITHIN TERMS`); session output
  [41-judge-stdout.txt](41-judge-stdout.txt).
- Refuter: [41r-erratum-nt1-refuter.md](41r-erratum-nt1-refuter.md) (`REFUTER E-NT1: AGREE`);
  session output [41r-refuter-stdout.txt](41r-refuter-stdout.txt).

## Why

Revision 6 §5 (sealed `46643f1d`) admits a window by one OFF receipt whose standard output "is
exactly `setUsingNetworkTime: Off`". Both counting windows of block 1 (sessions
`d079-epoch-25g83-r6-20261001T0617Z`, `d079-epoch-25g83-r6-20261001T2252Z`) recorded exit 0 and
`Network Time is already off.`, macOS's statement of the same end state when the setting was
already OFF. They were admitted by the recognizer widened in `2431dcaa` after the seal. The cold
science gate on the block 1 candidate and its refuter asked for an erratum before issuance; the
owner's refusal route R3 (2026-09-30, `835aaba3`) requires one when a fix makes code disagree with
the sealed text.

## The erratum (the ruling's adopted text, with the refuter's two cures applied)

> **E-NT1.** In Revision 6 §5 "Network time", the condition "its standard output is exactly
> `setUsingNetworkTime: Off`" reads: "its standard output states the OFF end state: after
> collapsing every run of whitespace to one space, trimming surrounding whitespace, removing any
> trailing periods and ignoring letter case, it equals either `setUsingNetworkTime: Off` (the
> setting was ON and is now OFF) or `Network Time is already off` (the setting was already OFF);
> any other output, including an ON statement, empty output, the getter form `Network Time: Off`,
> an output that states anything besides one admitted statement (for example an OFF statement
> followed by an ON statement), and the exit-0 `You need administrator access to run this tool...
> exiting!` text, is refused". The §7 JSON key `stdout_exact` is read the same way; the §7 JSON
> block itself is not edited (its sealed policy digest `dfa1ec73…` is unchanged). Every other
> receipt condition (exit status 0, same boot, at least 600 s before the first capture on both
> clocks, one receipt per window) is unchanged. Standard error is not a receipt condition: the
> sealed text tolerates the known `Error:-99` line and refuses no other stderr, and the code
> (`joulewise/network_time_off.py`, `admit()`) requires only that stderr be text; both admitted
> receipts have empty stderr. The registered operating condition, network time OFF and settled on
> the same boot, is unchanged, so the §5 sentence "a change to any of them voids this revision" is
> not reached: only the recognition of macOS's second statement of that same state changed. No
> number, member, statistic or operative changes.

Differences from the ruling's first line, both from the refuter (AGREE, defects 1 and 2), applied
here because the refuter's findings settle in this one erratum:
1. "a multi-line output" is replaced by "an output that states anything besides one admitted
   statement (…)": the code collapses newlines with other whitespace, so a single statement wrapped
   across lines is admitted; what it refuses is a second statement.
2. "the tolerated stderr diagnostic" is removed from the list of unchanged conditions and replaced
   by the sentence on standard error, which states what the code does. Whether to narrow the code
   to the `Error:-99` line is deferred to lane NT-STDERR-NARROW-01 (it affects no admitted receipt).

## The chain of two attempts before C1 (cold science gate §6 item 3)

`CHAIN: WITHIN TERMS`. Neither `…-c1-20261001T0137Z` (pre-start refusal at t0, `night_probe_error`
on the receipt wording) nor `…-c1-20261001T0555Z` (stopped by the bench battery gate before
publication) opened a ledger session; the ledger after the pinned head (sequence 276) holds only
the two admitted sessions; nothing was captured, so nothing could be selected; STOP-NULL-REPEAT was
never engaged; the two refusal signatures differ, so the owner's R5 bound never fired. Refuter
precision (defect 3), recorded: the re-arm after 0137Z is licensed by the owner's route R1/R3/R4
(a code defect is not one of D-182's machine-state codes), with D-182's own terms (zero capture,
new plan id, fresh notice, spacing) all met; 0555Z's stop is a battery-float arm refusal under
A-R5b.

## Findings and dispositions

| Source | Finding | Disposition |
|---|---|---|
| Refuter defect 1 | Adopted text says multi-line output is refused; code admits a wrapped statement | Fixed in the erratum text above |
| Refuter defect 2 | Code admits any stderr; text called the stderr tolerance "unchanged" | Fixed in the erratum text above (states what code does); narrowing deferred to lane NT-STDERR-NARROW-01 |
| Refuter defect 3 | 0137Z re-arm attributed to D-182 rather than the owner's route | Recorded above; conclusion unchanged |
| Refuter defect 4 | Judge quoted a D-182 sentence outside the charge's read list without disclosing it | Recorded; the answer does not rest on it (refuter's own reading) |
| Refuter defect 5 | A cited check row (6e) does not list the night-gate GO time | Rejected as immaterial: the refuter verified the GO time independently (0617Z `night.log` line 2) |
| Judge | Process deviation: this gate ran after the windows, not before proceeding | Recorded; changes no number |
| Judge contamination | Read `RUN_STATE.md` at `835aaba3` (lines 28-38) by `git show` to verify the quoted route text | Disclosed in the ruling; used only to verify the charge's quotation, which matched |
