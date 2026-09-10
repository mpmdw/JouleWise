# Cold-gate packet 31 — does the 07:00 dead-man firing of 2026-09-10 satisfy NIGHT-REHEARSAL-01 acceptance item 5?

Mechanically assembled by the resident magistrate (activation 96bfeca7) at 2026-09-10 ~07:10 PDT. Trigger: the 09-11
harvesting activation must accept or refuse item 5 mechanically, and checklist 13 (Exhibit B, "Dead-man wrote anything into
`night/`, including launchd stream files") forbids the resident magistrate from exempting stream files locally; applying an
acceptance criterion whose literal wording is unmeetable by construction is a verdict-criterion question for the cold gate
(rule 11), paired with an Opus refuter.

## The observation (Exhibit A, record 30 — read it first)

At 07:00:02.092 PDT the dead-man wrote the exact expected line to `night.log`. `night/` (empty at install, baseline `[]`)
now holds exactly `launchd.deadman.out` and `launchd.deadman.err`, both 0 bytes, birth 07:00:01.948 — 144 ms BEFORE the
driver's log line — at the `StandardOutPath`/`StandardErrorPath` the installer rendered into the plist (Exhibit C). The
driver's `dead_man` (Exhibit D) wrote no record. The first rehearsal's harvest (record 21i line 21, on this checkout at
`docs/process_traces/2026-09-02-hands-free-week/21i-rehearsal-20260909-harvest-record.md`) treated the night agent's
`launchd.night.out` in `night/` as the courier transcript, i.e. launchd's file there was the design.

## The criterion's lineage (read these on this checkout)

- Kernel acceptance text (docs/process/state_kernel.json, NIGHT-REHEARSAL-01 acceptance evidence): "A rehearsal with the
  agents installed the MORNING BEFORE the armed night, so the pre-night 07:00 dead-man firing is observed standing down
  without writing anything but a log line (coldgate-d1 R-7 amendment)".
- Cold-gate ruling 61 (`docs/process_traces/2026-09-09-rehearsal-harvest/61-coldgate-ruling-second-stub-night.md`, lines
  ~125–140, item 5 paragraph) and refuter 62; magistrate synthesis 65 (same directory) — the wording "and `night/` holds
  nothing from that dead-man firing. Record any deviation; do not silently exempt a file from this wording" was carried
  into runbook 67 §Expected observations and harvest acceptance (same directory, 67-arm-runbook-rehearsal-20260911.md).
- Checklist 13 (Exhibit B) §2 table row for `launchd.night.out` etc. ("do not exclude stream files from item 5") and the
  "What can go wrong" row.

## Questions

Q1. Is item 5 MET by this observation? Options: (a) MET — the criterion's object is what the DRIVER writes ("without
writing anything but a log line"); the two zero-byte files are launchd's stdio handles, created before the driver ran, at
paths the installer chose by design, and carry no bytes; (b) NOT MET — the literal `night/`-holds-nothing wording governs;
cure = installer renders the stream paths outside `night/` (with a test) and a third stub night observes a clean firing;
(c) MET, with a registered follow-up so the criterion becomes mechanical (either move the stream paths outside `night/`
in the installer, or amend the wording to name the two zero-byte launchd handles as the only permitted entries); (d) other.
Give the ruling with reasoning sized to what the criterion guards (a pre-night dead-man writing a refusal/courier record
that would poison the night's own records).

Q2. Whatever the ruling, state the EXACT mechanical predicate the 09-11 activation runs at harvest to close or refuse
item 5 (entries allowed in `night/` from the 07:00 firing by name and size; ordering of the log line vs the verdict line;
what any other entry means), and the sentence to record under NIGHT-REHEARSAL-01.

Q3. Does the same reasoning cover the night agent's own `launchd.night.out`/`.err` that will appear at 02:56 on 09-11
(item 6 harvest), given record 21i already used that file as the courier transcript?

Constraints: this packet asks for an application of an existing acceptance criterion, not a new process rule; if you find
that only a rule change can resolve it, say so and route it to Ed with your recommendation. Ruling file:
`10-coldgate-fable-ruling.md` in this directory, with an "Executed probes" section (you may `stat`/`cat` the custody files
listed in Exhibit A read-only; never write, move or delete anything under `/Users/edr/night-custody`).
