# Courier finding — rehearsal-20260909 (written by the night courier, pid 82210)

Result record: verdict REHEARSAL_ONLY, chain_exit_code 0 (stands).
Receipt: verdict REFUSED, refusal reason `night_probe_error`,
detail `FileNotFoundError: [Errno 2] No such file or directory:
'/Users/edr/night-custody/rehearsal-20260909/chain.zsh'`.
Per NIGHT_HANDBACK.md this is NOT `night_refused_agent_present`, so it is a
finding and must be cured before any real plan is armed.

## Root cause (read from the stub checkout at ae8f074f, not executed)

- `joulewise/night_gate.py` `evaluate_night` (around line 681) reads
  `plan.chain_path` and `plan.chain_sha256_path` through `probes.read_text`
  for EVERY receipt class, including REHEARSAL_STUB.
- `scripts/run_night.py` line 1196-1199 substitutes the built-in stub chain
  (`/dev/null`, `sleep 2; echo REHEARSAL`) for REHEARSAL_STUB and never
  writes `chain.zsh` or its sidecar.
- The arm sequence (trace 21b) did not write `chain.zsh` either, so the gate
  hit a missing file and refused. The driver then ignored the refusal because
  `rehearsal_effective` is true for REHEARSAL_STUB (line 1169-1170), which is
  why result.json still says REHEARSAL_ONLY.

## Cure options (magistrate decides; do not re-arm this plan on this signature)

1. Gate side: in `evaluate_night`, skip the chain/sidecar read when
   `plan.receipt_class == "REHEARSAL_STUB"`, mirroring the driver, and record
   `chain_sha256: null` with basis `stub_by_design` in C5.
2. Arm side: have the stub arm write a `chain.zsh` + `.sha256` sidecar so the
   gate's read succeeds (the driver would still ignore them).
Option 1 keeps gate and driver in one truth; option 2 leaves the two sides
disagreeing about what the stub is. Recommend option 1, with a test that a
REHEARSAL_STUB plan whose chain_path is absent yields verdict REHEARSAL_ONLY
and no refusal.

## Secondary observation

A REFUSED receipt is silently overridden for REHEARSAL_STUB. The handback
only sanctions `night_refused_agent_present` as an acceptable stub refusal;
consider making the driver log the receipt refusal reason on the
`night gate verdict=` line so the courier and the log agree at a glance.

## Evidence
- results branch night-results/20260909 on origin at d4d494ec (verified via ls-remote)
- night.log: gate REFUSED 02:56:01, result REHEARSAL_ONLY 02:56:03, push 02:56:10
- watchdog state.json: FENCED, age 199.552 s at courier build (alive)
- courier email id 1a08599a4ff4d005 to Ed
- no 2026-09-08 07:00 dead-man line in night.log: agents were installed 2026-09-09 01:57, so that case did not apply

## Why tests missed it
`tests/test_night_gate.py::test_a_fully_green_rehearsal_can_never_yield_go`
evaluates a REHEARSAL_STUB plan against `FakeProbeSource()`, whose fake
`read_text` serves chain and sidecar text, so the gate's unconditional chain
read succeeds in the test and only fails on a real arm where no chain.zsh
exists. The cure needs a test whose probe source raises on chain_path for
REHEARSAL_STUB and still expects REHEARSAL_ONLY with no refusal.

Driver pid 82049 exited and wrote courier.json at 02:57; the courier is done.
