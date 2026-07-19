# Doctor Preflight Contract

`joulewise doctor` is a read-only evidence report. It consolidates configuration
and host checks before a measurement window; it is not a supported-hardware
certificate and cannot prove that a machine is quiet.

## Invocation

```text
python3 -m joulewise doctor [CONFIG ...] [--campaign]
    [--ack-config-warnings] [--backup-destination PATH] [--json]
```

- Inspection mode is the default. Unknown schema-0.1 keys remain visible
  warnings and do not make the command fail.
- Campaign mode makes any `ConfigKeyWarning` a failed preflight unless
  `--ack-config-warnings` is present.
- `--ack-config-warnings` acknowledges only the exact warnings emitted by the
  supplied config set. It does not make an invalid config valid and does not
  change normalized config bytes or config identity.
- `--backup-destination` names an existing destination to inspect. Doctor never
  creates it.
- `--json` selects the machine-readable representation. Human and JSON output
  describe the same report and use the same ordered checks.

Exit status is 1 only when at least one check has status `fail`; `pass` and
`warn` reports exit 0. Input or command-line usage errors retain the CLI's
ordinary exit-2 behavior.

## Stable Report Shape

The machine schema is `joulewise.doctor.v1`:

```json
{
  "schema_version": "joulewise.doctor.v1",
  "mode": "inspection|campaign",
  "verdict": "pass|warn|fail",
  "checks": [
    {"id": "config", "status": "pass|warn|fail", "summary": "...", "details": {}}
  ]
}
```

Checks always appear in this order:

1. `config`
2. `versions_arch`
3. `model_tokenizer_identity`
4. `powermetrics`
5. `samplers`
6. `thermal_pressure`
7. `backup_destination`
8. `quiet_machine`

JSON object keys are sorted when rendered. Config, warning, model, tokenizer,
and sampling rows are ordered by config path; config warnings are additionally
ordered by field path and warning code. The human table follows the check order
above. Doctor includes no timestamp, so identical config bytes plus an
identical injected probe snapshot render byte-identically.

## Check Semantics

### Configuration and acknowledgement

Doctor parses with the binding schema-0.1 warn-and-ignore policy. Unknown keys
are reported as structured `ConfigKeyWarning` rows (`code`, `path`, `message`,
and `config`). Campaign-mode acknowledgement is represented as:

```json
{
  "scope": "config_warnings",
  "mode": "campaign",
  "required": true,
  "acknowledged": true,
  "mechanism": "--ack-config-warnings",
  "warning_count": 1,
  "warnings": []
}
```

Campaign execution reuses this doctor-owned gate. Its terminal
`joulewise.campaign_verdict.v2` JSONL row records the doctor schema and the
complete `config_warning_acknowledgement` under `preflight`. An unacknowledged
warning executes no benchmark, records collection `invalid`, and leaves
claim-input readiness in the existing P2-041 vocabulary (`not_assessed` when no
analysis manifest makes a stronger determination). The acknowledgement is a
preflight fact, never a collection verdict, claim outcome, waiver, or
publication act.

### Versions, architecture, and identities

The report includes Python, operating-system, architecture, hardware model,
CPU, logical CPU count, and available package versions. Each valid config adds
its configured model name, source, revision, and weight format. Tokenizer
identity uses the runtime's configured source/revision fallback and, for suite
manifests, reports the tokenizer-scoped suite identity when it is present in
the manifest. Missing source/revision identity is a warning, never silently
invented.

### Powermetrics and sampler fields

Doctor checks whether `/usr/bin/powermetrics` exists and is executable. The
non-interactive privilege check is exactly an inspect-only policy query:

```text
sudo -n -l /usr/bin/powermetrics
```

Doctor never runs `powermetrics`, never asks for a password, never edits
sudoers, and records `privileged_command_invoked: false`. Missing capability is
a failure only when a supplied config selects the powermetrics backend;
otherwise it is a warning.

Sampler evidence includes the adapter's requested powermetrics samplers
(`cpu_power`, `gpu_power`, `ane_power`, `thermal`) plus every config's telemetry
backend, requested power rate, idle duration, and post-warmup settling duration.
Doctor does not claim that a requested sampler produced data; bundle evidence
owns that fact.

### Thermal pressure, backup, and quietness

Thermal pressure uses the unprivileged `pmset -g therm` status. Nominal output
passes; elevated or unavailable output warns. It is an ambient heuristic, not
a calibration.

The backup check reports the exact configured path, whether it is an existing
directory, and free bytes from a read-only filesystem-statistics query. Missing
destinations and less than the 10 GiB operational preference warn. Doctor does
not create, mount, download, pin, copy to, or verify restoration from a backup.

Quiet-machine output always warns that quietness cannot be certified from a
snapshot. It additionally reports detectable concerns such as battery power,
low-power mode, elevated one-minute load, active displays, an engaged
screensaver, non-Nominal thermal pressure, and failed environment probes. The
quiet-machine check consumes the same pure environment-policy evaluator as the
campaign guard, but only advisorily: its report remains `warn`, including when
all observed critical findings pass. No doctor result is a quietness
certificate or authorizes a `[QUIET-MAC]` collection while agent load is
present.

The advisor's nullable sudo-free snapshot includes `external_connected`,
`low_power_mode`, `display_power_state` (`all_asleep`, `any_awake`, or
`unknown` across all online displays), `screensaver_engaged`,
`screensaver_module`, `screensaver_delay_s`, `hid_idle_s`, and thermal
pressure. Display evidence comes from `pmset -g systemstate`; screensaver
configuration comes from `defaults -currentHost read
com.apple.screensaver`, with an absent `idleTime` interpreted as the macOS
1200-second default; current HID idle comes from `ioreg -c IOHIDSystem`.
Unrecognized output or probe failure is unknown/null, never a pass.

Load averages remain useful preflight evidence and doctor may warn on an
elevated one-minute value, but load is not a campaign member-admission
predicate. The enforcing campaign preflight separately runs after campaign
lock acquisition and records the exact evaluator findings and snapshot
digests. It requires the policy-selected critical fields to pass and fails
closed on critical unknowns; this enforcement does not strengthen the
meaning of a prior doctor report.

## Testability and Mutation Boundary

The report builder consumes a complete probe fixture. Deterministic tests pass
fixtures for every check and never access live host state. The live collector
is separate and limited to file metadata, filesystem statistics, package and
platform metadata, existing sudo-free environment probes, `pmset -g therm`,
and the inspect-only sudo policy query above. Doctor opens no repository or
system file for writing and launches no benchmark, telemetry capture, backup,
or privileged command.
