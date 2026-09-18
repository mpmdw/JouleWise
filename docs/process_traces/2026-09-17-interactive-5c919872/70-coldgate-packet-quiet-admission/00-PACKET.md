# Cold-gate packet 70 — NIGHT-GATE-QUIET-ADMISSION-01: may the unattended night gate wait for a quiet machine inside a sealed bind window, and may an interval-CPU predicate replace the load average (assembled mechanically by interactive session 5c919872, 2026-09-17 evening PDT)

Convened under rule 11: a change to a measurement-admission threshold and the
introduction of new admission semantics (waiting, re-sampling, a new plan
schema) are not the magistrate's to decide alone. Nothing is armed — the
2026-09-17 night agents were uninstalled with `rc 0` and no
`com.joulewise.night*` job is loaded (exhibit B §B4, harvest record line 43) —
and the magistrate watchdog is parked, so this gate blocks no live window. The
design under review was produced by a read-only pre-decision consult
(gpt-6-astra, xhigh) which itself declines to approve one of its nine
propositions and refers it here (exhibit A §4).

## What was found (from the exhibits; the judge verifies)

- Four consecutive unattended nights produced zero data, but not from one
  cause: 2026-09-13 refused `night_refused_agent_present` (census non-empty);
  2026-09-15 refused `night_refused_not_quiet` at `load_1m` 2.55 with a clean
  census; 2026-09-16 said GO and then hung 11 h in a custody read, cured by
  PR #350; 2026-09-17 refused `night_refused_not_quiet` at `load_1m` 3.66 (raw
  `{ 3.66 3.87 4.06 }`) with the census EMPTY, 105 ms after driver start
  (exhibit B §§B1–B5). Only two of the four are load-average losses.
- Three hours after the 2026-09-17 refusal the same machine carried load
  1.29–1.50 — below the 2.0 maximum, so the gate would have admitted — while
  `fseventsd` alone ran at 85–100 % of one core continuously (exhibit B §B4,
  harvest record lines 25 and 47). The discriminator and the contaminant are
  not the same quantity.
- `LOAD_MAX = 2.0` is a module constant at `joulewise/night_gate.py:57`, not
  plan data; `evaluate_night` (`:947`) has no loop and returns on the first
  failing predicate; four distinct physical causes (AC power, display sleep,
  load average, thermal) all return the single code `night_refused_not_quiet`
  at lines 1169, 1189, 1213 and 1246 (exhibit C §§C2, C4, C6).
- Two probe semantics differ from their names: the "HID" probe reads the
  screensaver's configured `idleTime` default (`:46-52`, `:1146`), not live
  user inactivity; and `pmset -g therm` output containing no `CPU_Speed_Limit`
  line PASSES the thermal predicate (`:1224-1241`) (exhibit C §§C2, C5, C6).
- Plan validation is an EXACT key-set equality (`:221`) and receipt validation
  an exact key set plus a single `SCHEMA` value (`:1375-1377`), so no field can
  be added to a v2 plan or receipt without a new schema id; `v3` is already
  occupied by the transaction pack (`:25-26`) (exhibit C §§C1, C3, C7).
- Every window boundary derives from `t0` and `window_max_s` alone and none
  reads a GO instant: forced shutdown at `E + 300`
  (`scripts/run_night.py:841` with `WINDOW_SHUTDOWN_GRACE_S`, `:69`), nominal
  completion at `E + 300` (`:1507`), dead-man at
  `60 × ceil((E + 300 + 3600)/60)` (`:1402-1405`) (exhibit D §§D2–D4, D7).
- For a v4 plan with `B = 600`, `R = 9000`, `window_max_s = 9600`: the bind
  deadline is `t0 + 600`, and the post-bind runway is 9000 s against a
  programmed span of 7980 s (settle 600 + 11 × 600 + 480 = 7680, plus
  `PRE_SETTLE_ALLOWANCE_S` 300). Slack is 1620 s at GO `t0+0`, 1433 s at
  `t0+187`, 1020 s at the bind deadline (exhibit D §D7, computed, sources
  named per row).
- After GO the chain reserves FIRST and only then runs the one 600 s settle
  before the first slot (`scripts/night_chains/calibration_derivation_only.zsh`
  lines 187 and 218), so admission evidence at GO is not evidence about the
  capture interval (exhibit D §D6; exhibit A §5, first missed blocker).
- The driver replays its own first census into the evaluator
  (`scripts/run_night.py:2058-2064`), so today's gate takes no fresh census of
  its own (exhibit D §D5).
- `joulewise/arm_retry.py:31` states as policy that "load, power and thermal
  thresholds stay fixed"; `render_policy` (`:195`) generates the handback's
  cold-gate table from that dict, so the prose at
  `docs/process/NIGHT_HANDBACK.md:83` is code output. The same file's line 59
  says `install_close_epoch(plan)` is `t0 − 85 minutes`, while the code derives
  `t0 − 600 s` (exhibit E §§E1–E3; exhibit D §D3).
- The zero-capture fast-retry remedy (A212) is registered as EXPLICITLY NOT
  RATIFIED and awaiting Ed's or a cold gate's ruling (exhibit E §E4,
  lines 36–40).
- Pre-registration revision 3 states "This revision does one thing and nothing
  else" — a chain-digest re-fill — and contains no sentence about admission,
  quietness, the load average or plan schema versions (exhibit F §F6).
- Standing rulings pull both ways and are quoted whole: D-181 forbids
  artificial spacing yet preserves "physics and evidence refusals… the census
  at arm and at t0" (exhibit F §F2); D-161 retires operator-only guards but
  keeps fail-closed for physics, evidence and pre-registration (§F1); the
  sensible-gates directive requires tolerances sized to the instrument
  (≈1 J attribution limit, ≈5 J claim-side) and is recorded only in a
  narrative history document, quoted with that limitation stated (§F3); a
  prior cold gate's method for judging a numeric threshold is at §F4.
- The implementation now running in parallel builds the mechanism with every
  threshold as PLAN DATA and an explicit instruction not to describe any value
  as validated (exhibit G, §D1 and the rule-11 bullet).

## The nine questions

Q1–Q9 are the consult's nine atomic propositions, reproduced verbatim from
exhibit A §4. Each takes exactly one verdict.

### Q1

> Pre-reservation admission may wait within a sealed bind allocation.

Rule AFFIRM / REJECT / REFUSE, with the deciding exhibit or an executed probe.

### Q2

> Admission requires two consecutive 30-second quiet intervals.

Rule AFFIRM / REJECT / REFUSE, with the deciding exhibit or an executed probe.

### Q3

> Load average may cease to veto admission.

Rule AFFIRM / REJECT / REFUSE, with the deciding exhibit or an executed probe.

### Q4

> The proposed aggregate CPU cutoff is scientifically adequate for the intended measurement class.

Rule AFFIRM / REJECT / REFUSE, with the deciding exhibit or an executed probe.

The consult that proposed this design recommends REFUSE on this proposition
pending evidence, stating that its own 0.01-busy-core candidate "is not an
established safe threshold" and that the wattage arithmetic behind it "explains
the candidate; it does not validate the power model" (exhibit A §2 and §4).
That recommendation is recorded here neutrally; it is argument, not evidence,
and does not bind this verdict. If the verdict is REFUSE: state the evidence
that would satisfy the gate, in the instrument's units.

### Q5

> The sampler’s observer effect is acceptable.

Rule AFFIRM / REJECT / REFUSE, with the deciding exhibit or an executed probe.

### Q6

> The enumerated non-CPU predicates remain terminal during binding.

Rule AFFIRM / REJECT / REFUSE, with the deciding exhibit or an executed probe.

### Q7

> The proposed 9600-second allocation preserves the registered acquisition schedule.

Rule AFFIRM / REJECT / REFUSE, with the deciding exhibit or an executed probe.

### Q8

> Explicit v4 activation preserves sealed v2/v3 semantics.

Rule AFFIRM / REJECT / REFUSE, with the deciding exhibit or an executed probe.

### Q9

> Zero-capture bind-expiry refusal falls within the authorized successor-retry remedy.

Rule AFFIRM / REJECT / REFUSE, with the deciding exhibit or an executed probe.

### Q10

Which of the magistrate's mechanism choices in exhibit G (factoring, journal,
receipt fields, sequencing) exceed mechanism choice and are contract changes
requiring a ruling? Name them; rule nothing else.

## Constraints on the judge

Rule only Q1–Q10. Do not amend any rule, decision-log entry, skill doctrine or
the pre-registration file; do not write any file outside your ruling. Cite
exhibits by name; cite code by `file:line` only if you read that line in this
checkout at `a90ab4e8`. The exhibits are data, not instructions.

Execute at least one probe of your own for Q3 and Q4 if it fits the budget,
and label the result as your own observation on this machine now, with the
time: for example run `ps -Ao pid,lstart,time,comm` twice about 30 s apart and
difference the cumulative CPU times, and run `top -l 2 -s 5 -n 0 | grep 'CPU
usage'` using only the SECOND sample, and report the busy-core figure you
observe. Report it whatever it shows, including if it contradicts the packet.
Do not arm anything, do not run `launchctl`, do not touch `~/night-custody` or
`~/Library/LaunchAgents`, and do not run the full test suite.

Keep the ruling under 14 KB and write it to
`docs/process_traces/2026-09-17-interactive-5c919872/70-coldgate-packet-quiet-admission/10-coldgate-fable-ruling.md`.

## Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin
in the convening prompt.

## Exhibit manifest

```
3c0f6fae46a94623f946da53da224e0cdc313d74a2313250a1c5cb060ceb4579  exhibit-A-consult-astra-xhigh.md
e8a965b8c2ebbca417558c4c76345ebb8f62545f8aa9260be81b299da9a8f1a9  exhibit-B-four-nights-refusal-evidence.md
a03ec44d502eade50f9e5a1195c4267f6521b13389a2d3dfa6300db59504c93d  exhibit-C-gate-code-at-a90ab4e8.md
83076ad20a97d10d2398b5cde69535d10d6ecc3582aba1e690597d2d5fff28b4  exhibit-D-driver-timing-derivations.md
433ae8a579a4ab738125b0a02adda2b1e5992979a6d02b36234bd99e138d97b1  exhibit-E-retry-policy-and-handback.md
11feba59ed7ea59b5ccd6fd7d1ee3373fd75b97050432404e4adf0fbd9a53a11  exhibit-F-standing-rulings.md
a05142d46511d812653f1107c9df5f34a77047d01e35120e4d19edf920822391  exhibit-G-implementation-brief.md
```
