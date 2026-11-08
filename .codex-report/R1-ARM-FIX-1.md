```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented D2 crossing sizing, D3 recorded display dwell and D5 literal chain pin; requested synthetic and compatibility checks pass.",
  "workspace": {
    "base_requested": "5c0b79d31",
    "base_mode": "exact",
    "head_start": "5c0b79d31c0b2128dda3669a9af105c475232e05",
    "head_end": "5c0b79d31c0b2128dda3669a9af105c475232e05",
    "upstream_end": "5c0b79d31c0b2128dda3669a9af105c475232e05",
    "branch": "lane/2026-11-08-r1-arm-fixes"
  },
  "pathspec": ["joulewise/align/r1_arm.py", "scripts/arm_align_r1.py", "tests/align/test_r1_arm.py", "docs/align/r1_arm_runbook.md", ".codex-report/R1-ARM-FIX-1.md"],
  "unowned_dirty": [],
  "verdict": {"implementation": "implemented", "acceptance": "pending_verification"},
  "verification": [
    {"id":"V1","kind":"test","cmd":"JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -m unittest tests.align.test_r1_arm -v","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"(?m)^OK$"}},
    {"id":"V2","kind":"test","cmd":"JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -m unittest tests.align.test_v4_kit -v","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"(?m)^OK$"}},
    {"id":"V3","kind":"test","cmd":"JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -m unittest tests.align.test_r1_runtime -v","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"(?m)^OK$"}},
    {"id":"V4","kind":"smoke","cmd":"JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -m unittest tests.align.test_r1_arm.ArmTests.test_production_route_completes_with_synthetic_runtime tests.align.test_r1_arm.ArmTests.test_mid_high_power_interrupt_restores_and_releases_host_lock -v","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"(?m)^OK$"}},
    {"id":"V5","kind":"lint","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}
  ],
  "flags": [
    {"id":"F1","kind":"environment","level":"nonblocking","text":"ps is denied by the sandbox (exit 127: operation not permitted). The inherited synthetic process-table and group-census seams remain; these runs do not validate live census or hardware.","needs":"Lead owns live process/hardware verification in a clean session."},
    {"id":"F2","kind":"verification_gap","level":"nonblocking","text":"Agreement requires independent executing review of the final arm module. This worker's checks are complete; that lead-owned gate is pending.","needs":"Independent reviewer re-executes V1, then magistrate reviews and commits the five scoped files."}
  ]
}
```

## Change

Authority: `/Users/edr/night-archive/seats-b17edfbb/R1-ARM-AGREEMENT.md`, section 5
and Recommendation to the lead, plus this brief. Read the reference generator
and runbook at `d5882a34e`; retained Sol's HAZARD_PACK route. No R1 chain,
driver, runtime, kit, shared launcher, b5 module or watchdog bytes changed.
The initial workspace was clean at the exact requested base.

Diff summary: the author now derives a t0-dependent window and retains the
derivation in `arm.json`; the CLI prints it through both `size` and `prepare`.
The wrapper pins the measurement checkout's R1 shell-chain SHA-256 as a literal
and re-hashes before its first helper. Changed/unreadable source exits 65.
It then sleeps the display and records a 300 s dwell before the diagnostic
pre bookend. Nonzero or missing pmset is recorded as `r1.display_sleep_failed`
and still receives the full dwell. An unsuccessful dwell helper cannot fall
through to measurement. Diagnostic bookend behavior remains unchanged.

The runbook now chooses t0 at least 15 min ahead, records
`df -g /Users/edr` in `$S/df-arm.txt`, requires display sleep before the
magistrate exits, forbids git operations in the measurement checkout between
install and t0, and restores network time at the next activation with
`sudo -n systemsetup -setusingnetworktime on`. The notice takes its ceiling
from the generated record and asks Ed to leave the display asleep through
the latest end. The existing interrupt monitor/meter warning remains.

### Decisions I made

1. D2 uses the existing exact base:
   `96,427 + 3,300 + 2*(1,800 + 600) + 600 = 105,127 s`.
   D3 explicitly adds 300 s, so the final base is **105,427 s**. The brief's
   D2 examples are tested before that addition and the full window is tested
   separately. Keeping 105,127 s as the final value would omit the required
   new dwell; no existing allowance was silently reduced to hide it.
2. Add `max(0, crossings - 1) * 11,164 s`, recalculating local-calendar
   11:45 crossings until the window stops changing. One encounter is already
   in the floor. The zone is America/Los_Angeles, including DST.
3. Differences from Opus `size_window`: retain Sol's route allowances; add
   the required 300 s dwell; omit Opus's separate 30 s meter allowance because
   the shared driver already owns meter startup/close within Sol's unchanged
   arm/close budgets. Do not round up to a minute: the brief's D2 arithmetic
   preserves exact seconds. Use the brief's half-open `[t0, end)` rather than
   Opus's inclusive end. Iterate without Opus's arbitrary eight-iteration cap:
   the added encounter is shorter than a local day, including a DST-shortened
   day, so the monotone sizing sequence converges.
4. D5 pins `scripts/night_chains/align_r1_rehearsal.zsh`, the same source
   authenticated by the Opus wrapper and named in agreement D5. The literal
   is generated from the actual measurement-root bytes, not this worker's
   checkout, a sidecar or a mutable environment variable. This is not a hash
   census of transitive Python dependencies; no broader source contract was
   invented. The shell compares exact SHA-256 equality before display sleep,
   dwell, either bookend or R1. A failed shasum also fails that equality.
5. Enforce the brief's 15-minute notice at preparation, in addition to the
   unchanged shared installer cutoff. Keep df recording as an explicit arm
   procedure, with no new disk threshold or fabricated footprint estimate.

### Sizing table

All seconds below derive from the terms above. Each extra crossing costs
11,164 s; only the first is covered by the 96,427 s floor.

| t0 (America/Los_Angeles) | Local 11:45s counted | D2 extra encounter seconds | D2 on old base | Added D3 dwell | Final window_max_s |
|---|---|---:|---:|---:|---:|
| 2026-11-08 13:30 PST | Nov 9 | 0 | 105,127 | 300 | 105,427 |
| 2026-11-08 08:00 PST | Nov 8, Nov 9 | 11,164 | 116,291 | 300 | 116,591 |
| 2026-10-31 07:00 PDT (fall-back within 30 h) | Oct 31 | 0 | 105,127 | 300 | 105,427 |
| 2026-03-07 06:00 PST (spring-forward within 30 h) | Mar 7, Mar 8 | 11,164 | 116,291 | 300 | 116,591 |

Fall-back makes the next day's 11:45 **29 h 45 min** after its t0, beyond the
base; spring-forward makes it **28 h 45 min**, inside the base. Tests also
include an 11:45 exactly at t0 and exclude one exactly at the end.

### Tests run with counts

| Check | Count | Result |
|---|---:|---|
| Baseline arm module, before edits (`JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.align.test_r1_arm -v`) | 4 | OK |
| V1 arm module after changes | 9 | OK |
| V2 v4 kit | 116 | OK |
| V3 R1 runtime | 33 | OK |
| V4 separate normal + interrupt synthetic rerun | 2 | OK |
| V5 whitespace check | — | pass |

The 158 tests across V1–V3 pass; V4 repeats the two e2e cases explicitly.
V1 includes a one-byte post-generation source mutation: the real zsh wrapper
returns 65, executes no helper sentinel, and creates no display journal,
bookend or R1 output. An environment digest set to the mutated bytes cannot
override the literal. Sizing CLI output is parsed and compared to the
derivation for both requested t0 examples. Display tests exercise success,
nonzero pmset and missing pmset, with a virtual clock verifying the full dwell.

Both e2e cases run the real `run_night` hazard path, generated wrapper,
unchanged shell chain and real R1 driver. Real lineage publication, signals,
flock, power markers and terminal writes run; hardware, process tables,
monitor/meter/collectors, reporting transport and runtime work remain the
original explicit synthetic boundaries. The new host display command and
300 s wait are also explicit seams; the real helper writes both timestamps.
The pre bookend verifies dwell-end already exists. A synthetic pmset failure
does not veto either e2e. Normal: exit 0, R1 complete, slots written.
Interrupt: TERM during the B leg, competing host lock blocked, exit 130,
R1 aborted, child terminations proven in the fixture census. Both restore
Automatic, remove power markers, reacquire the host lock and write
`chain.exited`. These are synthetic proofs, not live hardware validation.

### NEEDS_RULING

None. No scope expansion is requested. Nothing was armed, installed or
loaded; no launchctl, real pmset or sudo command was run. Changes remain
uncommitted for the magistrate; no Git metadata write was attempted.

## Verification notes

The read-only diagnostic `ps -p $$ -o pid= && git diff --check` exited 127
with `zsh:1: operation not permitted: ps`; its chained diff check did not run.
V5 ran independently and passed. This environment restriction affects live
process-table evidence, not the explicit fixture censuses or observed test
outcomes. The full suite was deliberately not run, as the brief directs.

Next exact step: the lead's independent executing reviewer runs V1 on this
diff; the magistrate performs final review and commits the five scoped files.
Live arming remains a separate, clean-session task.

## Residual risk

The inherited disk allocation is still unsized unless the operator supplies
a sourced estimate; shared arm headroom/live disk floors remain. The inherited
hazard interrupt path can retain monitor/meter processes until dead-man
recovery; the next activation checks for strays. The shell-source pin does
not authenticate transitive imports or close a post-check file-write race;
measurement checkout custody and the no-git rule remain required.
