GPT-6 (Codex/Sol; exact runtime model ID not exposed)

# H disk ruling implementation — complete; lead verification pending

Activation 283e9802, 2026-10-21. Branch `lane/2026-10-21-bytes-h-session`, starting and ending HEAD `a043c85d77aed5538a05b5070ccf1a2a0168316f` (upstream unchanged). Continued the authorized uncommitted partial work in place. No commit, install, quiet measurement, or out-of-scope repository write. Pre-existing untracked `.venv` symlink preserved. Lead-owned state, queue and run reports were not modified.

## Authority and decisions

Read the full lead ruling, including addendum 1, at `/Users/edr/code/JouleWise-wt-283-rec/docs/process_traces/2026-10-21-magistrate-283e9802/H-DISK-RULING.md`; the named file is absent from this lane. Read the full adopted Fable report with `git -C /Users/edr/code/JouleWise-data show origin/claude/bytes-h-disk-consult-fable:reports/bytes-h-disk-consult/fable.md`. Mission M0 intake found no active stop card. The explicit lead brief selects this bounded AGENT implementation instead of the stale generated lane heads.

- Disk terms use Fraction arithmetic over committed JSON decimal values, with one ceiling per complete stream basis, wall basis and WAIT. Each model contributes its own count × allowance. The reference stream allowance is `(mean reference request + max stream non-request) × (1 + measured margin)`.
- Stream basis = 27,802,317,346 B; wall basis = 26,878,191,539 B; B = their maximum. WAIT = ceil(max observed bytes/stream_s × registered 7,200 s) = 13,292,701,363 B per copy. c = 2 from raw plus roster-partitioned rsync backups; the harvest archive is `cp -c`. Fixed = committed 4,046,531,103 B. P = 2 × (27,802,317,346 + 13,292,701,363) + 4,046,531,103 = **86,236,568,521 B**, bit-exact.
- The prior partial run regenerated via `--disk-only` to preserve committed fixed artifacts and original timing/source evidence; `sizing_evidence.json` was byte-identical. The full source derivation calls the same disk calculation. This continuation's H test rederived the complete sizing row and asserted exact equality with the committed output.
- Prepare uses only statvfs f_bavail × f_frsize for admission and refuses strictly below P. Foundation available-for-important-usage is queried separately; unreadable results print null with `disk.purgeable_unreadable`. No reserve term.
- **Lead ruling resolved:** encode P in H's existing native caller fields. The native arm budgets three whole-roster targets. q = floor(2B / (3 × 123)) = **150,690,066 bytes_per_member**. Remainder = 2 × 27,802,317,346 − 3 × 123 × 150,690,066 = **338 B**. Headroom = 338 + 2 × 13,292,701,363 + 4,046,531,103 = **30,631,934,167 B**. Native total = 3 × 123 × 150,690,066 + 30,631,934,167 = **86,236,568,521 B = P**. Integer `divmod` computes q and remainder; no floating-point or rounded-up per-member excess enters the native budget.
- The H plan's disk receipt (`session.json.disk.native_arm_budget`) explicitly says “budget encoding derived from P”, records its formula, native copy count, q, remainder and headroom, and carries `disk.budget_encoded_from_p` in `session.json.disk.flags`. Prepare prints the same receipt before admission. q is an encoding, not a physical per-copy member size. The registered physical per-member estimate remains unchanged. No native driver or plan-writer edit.
- Desk samples free once before harvest/output writes, selects native arm disk targets matching the session volume device, subtracts desk-start free, prints allocation beside c, and persists the receipt in `desk.json.disk`. Missing arm or unreadable desk free gives null and a flag. No drawdown refusal.
- The existing PHYSICS refusal census entry now describes the ruled guard. No new refusal site or frozen-baseline edit. This continuation needed no additional census enrollment.

## Files modified

The complete continued task delta contains:

- `scripts/bytes_h_session.py`
- `tests/test_bytes_h_session.py`
- `configs/campaigns/bytes_mac_check/registration/derive_sizing.py`
- `configs/campaigns/bytes_mac_check/registration/sizing_b5.json`
- `configs/campaigns/bytes_mac_check/registration/README.md`
- `configs/gates/hazard_refusals.json`
- `.codex-report/bytes-h-disk.md`

This continuation changed the H caller, its tests, registration README and this report. The other authorized changes were carried forward from the partial run. `.venv` is the only unowned dirty path.

## Verification after addendum 1

Every invocation set `JW_B5_SYNTHETIC_ONLY=1` and used a fresh `TMPDIR` under `/private/tmp`. Installer tests use stubs; no live install was invoked.

| Check | Count | Exit | Result |
| --- | ---: | ---: | --- |
| `tests.test_bytes_h_session` | 30 | 0 | OK, 86.909 s; includes the real writer/native-target equality check |
| `tests.test_bytes_mac_kit` | 4 | 0 | OK, 0.217 s |
| Five registry modules listed below | 45 | 1 | 44 pass; same single census-dependent import-graph failure, 16.886 s |
| `tests.hazards.refusal_census` | census, not unittest | 0 | zero unlisted, stale, miscounted, guard-changed sites or scope gaps |
| `git diff --check` | whitespace inspection | 0 | clean |

The H module covers the exact H derivation, per-model counts, wall-basis dominance, stream-rate WAIT, purgeable disclosure, below-P refusal despite abundant purgeable bytes, equality admission, native budget encoding/disclosure, measured desk drawdown and the real non-claim harvest/export/gates chain.

Its synthetic nine-session replay derives B = 20,962,266,546 B from r4-alpha's committed observed stream/wall sums; WAIT = 13,292,701,363 B; fixed = 1,438,707,712 B. P = 2 × (20,962,266,546 + 13,292,701,363) + 1,438,707,712 = **69,948,643,530 B**. All nine synthetic desk-start free values (minimum 113,618,456,576 B) exceed P: **0 refusals of 9**. This is synthetic replay, not live hardware validation.

The registry failure is `tests.hazards.test_import_graph.ImportGraphTests.test_a_complete_arm_and_monitor_run_load_no_retired_module`: expected GO, observed NULL. It repeats the partial run's failure; that run's direct unchanged-Rig diagnostic identified `census_exit_3: sysmon request failed with error: sysmond service not found / pgrep: Cannot get process list`. This continuation did not repeat that diagnostic or change/bypass the process census. The lead owns the outside-sandbox replay.

No full suite was started in this continuation, per the lead's explicit instruction. The prior partial attempt had started then interrupted the canonical suite (exit 130; no completed total); it is not a suite pass. Final full-suite verification remains with the lead outside the sandbox. The requested explicit module/census set was used for this continuation's verification.

Exact continuation commands (all run from this worktree):

```sh
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d /private/tmp/bytes-h-ruling-h.XXXXXX)" /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_h_session > /private/tmp/bytes-h-ruling-h.log 2>&1
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d /private/tmp/bytes-h-ruling-kit.XXXXXX)" /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_mac_kit > /private/tmp/bytes-h-ruling-kit.log 2>&1
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d /private/tmp/bytes-h-ruling-registry.XXXXXX)" /opt/homebrew/bin/python3.13 -B -m unittest tests.hazards.test_import_graph tests.hazards.test_physics_coverage tests.hazards.test_refusal_allowlist tests.flags.test_flags_catalog tests.flags.test_flags_import_graph > /private/tmp/bytes-h-ruling-registry.log 2>&1
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$(mktemp -d /private/tmp/bytes-h-ruling-census.XXXXXX)" /opt/homebrew/bin/python3.13 -B -m tests.hazards.refusal_census > /private/tmp/bytes-h-ruling-census.log 2>&1
git diff --check
```

## Real dry prepare — retained from partial run

The lead explicitly waived a rerun for this continuation. The following full printout predates addendum 1 and therefore does not contain the new native-budget metadata/flag. The disk check and P are unchanged. Absence of `/private/tmp/bytes-h-dry2` was rechecked (exit 0).


Command (fresh TMPDIR and `JW_B5_SYNTHETIC_ONLY=1`):

```sh
python3 -B scripts/bytes_h_session.py prepare --measurement-root /Users/edr/code/JouleWise-wt-283-h --session-root /private/tmp/bytes-h-dry2
```

Exit **1**. Disk passes. The later identity producer fails before the calibration-ledger check because this sandbox denies `/usr/sbin/sysctl -n kern.osversion`. The producer's captured stderr was inspected separately; its final line was:

```text
write_derivation_night_inputs.NightInputsRefusal: machine vector derivation failed: CalledProcessError: Command '['/usr/sbin/sysctl', '-n', 'kern.osversion']' returned non-zero exit status 1.
```

No ledger was fabricated. The full final dry prepare stdout/stderr follows. `/private/tmp/bytes-h-dry2` was deleted and absence verified after the command.

```text
session_id: bytes-h-20261021T152626855890Z
candidate_t0: 2026-10-21T15:34:00+00:00
maximum_duration_s: 45120; programmed_span_s: 27371
disk: {"available_for_important_usage_bytes": null, "derivation": {"B_bytes": 27802317346, "allowances_by_model": {"llama-70b": {"count": 21, "member_allowance_s": {"denominator": 20000000000000, "numerator": 4746400816793639}, "stream_allowance_s": {"denominator": 50000000000000, "numerator": 9548214357147367}}, "neg8_reference": {"count": 37, "member_allowance_s": {"denominator": 100000000000000, "numerator": 14122618421581197}, "stream_allowance_s": {"denominator": 25000000000000000000000000000000000, "numerator": 2475038689504830954481754541426818773}}, "qwen3-14b": {"count": 5, "member_allowance_s": {"denominator": 50000000000000, "numerator": 7997038194774761}, "stream_allowance_s": {"denominator": 10000000000000, "numerator": 1170599756606169}}, "qwen3-1p7b": {"count": 5, "member_allowance_s": {"denominator": 100000000000000, "numerator": 14339574436176383}, "stream_allowance_s": {"denominator": 50000000000000, "numerator": 5038150164881857}}, "qwen3-30b-a3b": {"count": 5, "member_allowance_s": {"denominator": 250000000000, "numerator": 37123965755447}, "stream_allowance_s": {"denominator": 100000000000000, "numerator": 10528254686699321}}, "qwen3-32b": {"count": 5, "member_allowance_s": {"denominator": 50000000000000, "numerator": 9232807294442027}, "stream_allowance_s": {"denominator": 10000000000000, "numerator": 1415345379187543}}, "qwen3-4b": {"count": 5, "member_allowance_s": {"denominator": 50000000000000, "numerator": 7339681227489939}, "stream_allowance_s": {"denominator": 100000000000000, "numerator": 10409182074417483}}, "qwen3-8b": {"count": 5, "member_allowance_s": {"denominator": 100000000000000, "numerator": 15232309187894657}, "stream_allowance_s": {"denominator": 100000000000000, "numerator": 10923731127617711}}, "qwen3-8b-8bit": {"count": 5, "member_allowance_s": {"denominator": 5000000000000, "numerator": 804528133384583}, "stream_allowance_s": {"denominator": 4000000000000, "numerator": 472061748361189}}, "qwen3-next-80b": {"count": 9, "member_allowance_s": {"denominator": 50000000000000, "numerator": 7752958077403059}, "stream_allowance_s": {"denominator": 100000000000000, "numerator": 10830196702074579}}, "qwen35-122b": {"count": 21, "member_allowance_s": {"denominator": 100000000000000, "numerator": 17078676005436927}, "stream_allowance_s": {"denominator": 100000000000000, "numerator": 11577116221769523}}}, "authority": "H-DISK-RULING, activation 283e9802, 2026-10-21; Fable section 1 adopted", "estimated_footprint_bytes": 86236568521, "extra_wait_peak_bytes": 26585402726, "extra_wait_raw_bytes": 13292701363, "fixed_retained_bytes": 4046531103, "formula": "P = c*(B+WAIT)+fixed; B=max(ceil(max bytes/stream_s * sum(count*own stream allowance)), ceil(max bytes/member_wall_s * sum(count*own member allowance))); WAIT=ceil(max bytes/stream_s * 7200); c=2 (raw + partitioned rsync backups; archive cp -c clone); fixed unchanged; no reserve", "max_observed_bundle_bytes_per_stream_s": {"denominator": 8813392312498763, "numerator": 16271360000000000000000}, "max_observed_bundle_bytes_per_wall_s": {"denominator": 893951484135219, "numerator": 1162240000000000000000}, "max_observed_fixed_session_bytes": 1438707712, "observed_member_wall_sum_s": 16042.009888648987, "peak_copies": 2, "reference_stream_allowance_s": {"denominator": 25000000000000000000000000000000000, "numerator": 2475038689504830954481754541426818773}, "rounding": "exact rational arithmetic from committed decimal lexemes; ceiling each total basis and WAIT once", "session_wait_budget_s": 7200, "stream_basis_bytes": 27802317346, "stream_seconds": {"denominator": 25000000000000000000000000000000000, "numerator": 376478564112515239815824918032792294601}, "wall_basis_bytes": 26878191539, "wall_seconds": {"denominator": 100000000000000, "numerator": 2067369839006041683}, "window_max_s": 45120}, "estimated_footprint_bytes": 86236568521, "f_bavail": 27528894, "f_frsize": 4096, "flags": ["disk.purgeable_unreadable"], "free_bytes": 112758349824, "member_count": 123, "prepare_free_bytes": 112758349824, "purgeable_bytes": null, "required_free_bytes": 86236568521}
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-283-h/scripts/bytes_h_session.py", line 762, in <module>
    raise SystemExit(main())
                     ~~~~^^
  File "/Users/edr/code/JouleWise-wt-283-h/scripts/bytes_h_session.py", line 749, in main
    prepare(args.measurement_root, args.session_root)
    ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/edr/code/JouleWise-wt-283-h/scripts/bytes_h_session.py", line 230, in prepare
    identities, notes = desk_identity.collect(measurement, session / 'staging/inputs', run=run)
                        ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/edr/code/JouleWise-wt-283-h/joulewise/b6/desk_identity.py", line 31, in collect
    result = run([str(measurement / ".venv/bin/python"), "-B", "-c", IDENTITY_SOURCE,
                  str(measurement / "scripts/write_derivation_night_inputs.py")],
                 check=True, capture_output=True, text=True, timeout=120)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/subprocess.py", line 578, in run
    raise CalledProcessError(retcode, process.args,
                             output=stdout, stderr=stderr)
subprocess.CalledProcessError: Command '['/Users/edr/code/JouleWise-wt-283-h/.venv/bin/python', '-B', '-c', 'import base64, importlib.util, json, sys\nfrom pathlib import Path\nsource = Path(sys.argv[1])\nsys.path.insert(0, str(source.parent.parent))\nspec = importlib.util.spec_from_file_location("write_derivation_night_inputs", source)\nmodule = importlib.util.module_from_spec(spec)\nsys.modules[spec.name] = module\nspec.loader.exec_module(module)\nepoch, t1 = module._derive_planned_vectors("ac_high_power")\nprint(json.dumps({name: base64.b64encode(module._json_bytes(value)).decode("ascii")\n    for name, value in (("identity-epoch.json", epoch), ("t1-bindings.json", t1))}))\n', '/Users/edr/code/JouleWise-wt-283-h/scripts/write_derivation_night_inputs.py']' returned non-zero exit status 1.
```

## NEEDS_RULING

None. Addendum 1 and the continuation prompt resolve the native-arm encoding question. No scope expansion is requested.

## Handoff and remaining verification

Implementation is complete within WRITE_SCOPE. The remaining verification gap is the sandbox-dependent registry test and the lead-owned canonical suite. Next exact step: the lead reviews this uncommitted diff, reruns the census-dependent test and full suite outside this sandbox, then decides whether to commit. No H collection, live install or final hardware validation is claimed.
