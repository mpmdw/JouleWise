# lm-ctl-01 bundle acceptance · freeze 1

All values, sources of authority, spans and leg records in this directory are synthetic. `bundles.tar.xz` holds the frozen files; extraction yields **two** span trees with twelve accepted runtime directories. The KM003C input occurs once per span. There is no per-leg DC CSV or joined episode. Each scenario starts in an empty temporary directory. Negative cases mutate its copy. The archive and oracles are immutable.

## Files and scope

| File | Purpose |
|---|---|
| `bundles.tar.xz` | Raw source-shaped files plus two private synthetic instrument outputs and a synthetic Check/kit anchor. Inspect with `tar -tf bundles.tar.xz`. |
| `make_fixture.py` | Reproducible offline generator against runner `043b972f999913d248769237f1901d78119ceb72`. It runs the scripted mock endpoint and real `EpisodeRuntimeAdapter.run_workload` on a fake clock, saves only the episode from its output artifacts, calls `RunBundleWriter.write_power_trace` and uses the terminal hash-map writer. |
| `check_inputs.py` | Replays the real `read_episode_bundle` and KM003C parser, verifies terminal/close hashes, 20 ms spacing, rail/source keys, offsets, per-leg DC samples, and physical-call durations. Does not run the candidate or assign a release status. |
| `cases.json`, `run_suite.py` | Frozen cases, mutations, actual filesystem assertions, public projection, private numerical oracles and external-driver contract. A missing driver never gives a candidate pass. |
| `audited-kernel.json` | Exact raw SHA-256 of the four kernel files at `82542232d` and three dependency files at the audited print head. The final installed byte pass compares these pins and executes the existing independent hand vectors. |
| `SUITE.sha256` | All other top-level suite files, including the archive, scripts, cases and this README. A second manifest beside SPEC.md verifies the distributed suite from the delivery root. |

The test backend supplies a synthetic released G0, native-shaped interval telemetry, and invented KM003C monitor lines (50 Hz batched, little-endian 20-byte samples). The kit starts with the public draft's deterministic 3+9 layout and applies the ruled 60 s split gap; the 600 s recovery and the 128/256/512 doses are real-time units on a fake clock. Stamps and envelopes come from the mock workload/physical calls. The checked-in role projections for metadata, close, reference and instrument records contain the fields needed by this contract. `authority/check.json` stands in for an independent Check/offload trust root. It maps span → relative close/operational file → SHA-256. The kit/receipts deliberately identify a draft/mock source. A test registrar supplies the separate synthetic ledger, hand-read, instrument roster and freeze authorities. The fixture omits irrelevant archive constituents, ancillary feeds, native host attestations, journal samples and production credentials. No tolerance for draft/mock records may be added to a production launcher.

Representative archive paths (B = `spans/ctl-01-s01/legs/L002/runtime/runs/cadence-cl-ctl-01-L002`):

```text
authority/{kit,check}.json
spans/ctl-01-s01/runner_receipt.json
spans/ctl-01-s01/hazards/meter/stream-001.jsonl
spans/ctl-01-s01/legs/L002/{leg_spec,leg_record}.json
spans/ctl-01-s01/legs/L002/runtime/{runtime_result,runtime_custody,script-work}.json
B/outputs/align_episode.json
B/config.json
B/metadata.json
B/power_trace.csv
instrument/{hold,edges}.json
```

## Reproduce

Run from this directory with Python 3.13 and the specified runner's public source and synthetic test helpers on its normal import path. `RUNNER_SRC` denotes that checkout. All commands below use synthetic files only.

```sh
shasum -a 256 -c SUITE.sha256
PYTHONPATH="$RUNNER_SRC" python3.13 -B check_inputs.py
# Optional rebuild into a new path; the archive, not a regeneration, is the frozen input.
PYTHONPATH="$RUNNER_SRC" python3.13 -B make_fixture.py /tmp/ctl-synthetic-new
# When there is an independently built candidate and a synthetic test driver:
python3.13 -B run_suite.py --driver /absolute/path/to/test-driver
```

The self-check runs against the runner that exists. Candidate acceptance must run through the registered launcher, actual stage-1 builder, actual provenance checks, first_read and private/public writers. The suite deliberately ships no substitute look or self-answering driver.

## Acceptance driver for the implementation seat

The driver is test code external to the freeze. It receives `OP SOURCE BENCH FAULT`. SOURCE is the unpacked tree. BENCH contains actual private/public parent directories at `private/lm-ctl-01` and `public/lm-ctl-01`. The driver runs the installed candidate in a fresh child with the synthetic checkout/host binding. It returns the child's exit code and blind stdout/stderr verbatim. Configure synthetic roots in the test registry before launching; never expose test path or injection switches in the production CLI. Run under an unprivileged identity on an owner-enforcing, hard-link-capable volume. Run pytest or other outer tooling with bytecode/cache storage outside this frozen directory.

- `install` provisions only the synthetic authority, public Git history, private instrument operands and stable control/lock files. Use the real registry schema and the same store/Check builder used at the look with an invented trusted Check upstream. Materialize exact fixture bytes; use the public/digest and private/operand roles specified in SPEC. Install an instrument schema with the prospective closed reason vocabulary for the legal-null cases. Use a synthetic, authorized, qualified two-member instrument roster and eligible token-floor decision. Protect fixture-only authority with test isolation. It cannot authorize a live look.
- `stage1` runs the actual stage-1 entry and writes the verified candidate to the fixed private parent as `stage1.json`. The executable cannot accept prepared joined Episodes, parsed traces or a caller-chosen roster. `commit-stage1` is the independent test registrar. It binds those exact bytes to its test ledger and writes the five expected public fields to `BENCH/registered-public.json` from that committed authority.
- `preflight` runs the standalone bound preflight, including actual link/cleanup, with no claim. The healthy and 0555 cases repeat it twice before running stage 2.
- `stage2` invokes the launcher and its own preflight. Use the real OS and descriptor operations for linkability, publication and reservation. Record test-observer events in `BENCH/events.jsonl`, outside the release outputs. Each line is a JSON string: `"claim"` when exclusive reservation mkdir succeeds, `"start"` after durable read-start, `"first_read"` on real reader entry and `"ctl_value_decode"` at the first value-consuming call (including any premature calls by preflight). Observe at the low-level boundary across child processes; append events in call order. An emitting mock that chooses the output, bypasses the release worker or tests the case id cannot satisfy this suite. Disable ordinary banner/debug printing. The oracle reads the real fixture-only output files itself.
- The only fault parameter on ordinary invocations is `none`. `mkdir_sync_once` raises a single sync error after the successful reservation mkdir, before the marker, then permits rollback syncs. `post_marker_oserror` raises an actual OSError just after durable start and before publication. No process signal is needed. `installed_kernel_drift` supplies an on-disk loaded source that differs from its registered hash. `kernel_matches_manifest_but_not_byte_pass` changes both the test manifest pin and installed kernel while the byte-pass record still binds the audited kernel and vector run. A simple manifest-to-working comparison would wrongly admit it. `other_worktree_parent` puts the private parent within a second registered test worktree. `ownership_disabled` changes only the mount-protection observation to the unsupported state. `tracked_hold_blob` places the synthetic private operand bytes in the public test tree under another name; `sibling_ledger_only` puts the required receipt on a nonauthoritative sibling, absent from the first-parent ledger. Installation faults provision their condition before the candidate validates it. No controller or scorer behavior may be stubbed.
- `before` mutations are part of an independently invented close or instrument read and are re-anchored before registration. `after` mutations are damage or state changes after stage-1 commitment and keep the old pins. Missing roles/source support diagnose `INPUT_CHANNELS` before hash-mismatch comparison of remaining files. An existing role whose bytes conflict yields `INPUT_BINDING`. A preflight reason may be exposed only from the closed blind allowlist. For fresh cases changed before registration, a stage-1 refusal is sufficient if it is the expected reason and nothing was claimed/read. Other cases drive stage 2. Run the 0555 test as the real effective identity; a privileged writable directory invalidates the test.
- `spent_reservation` is a second invocation in exactly the same bench after success. `failure_after_start` also retries after exit 1. Empty and orphan-stream claims stay byte-preserved and half-made. The rollback case requires that the same owner demonstrably failed before marker installation, left no claim and can make one successful fresh attempt. Each retry uses the real durable state.

## Independent numeric expectations

Native rails run at 10 Hz; baseline CPU/GPU/ANE are 2/3/1 W. During every physical call the increments are 1/2/0.5 W. DC baseline is `10 + numeric leg id` W; calls add 4 W. These levels bracket each call by real samples. At the recovery end both 40 s windows lie on the idle plateau. Each hidden call lasts `2 + 0.01 × delivered_tokens` seconds. Accordingly the respective CPU/GPU/package/DC slopes are 0.01/0.02/0.035/0.04 J per token; intercepts are 2/4/7/8 J. For the L005 128-token leg, DC above-baseline hidden call is 13.12 J, of which 5.12 J is decode. Wrong leg assignments change DC baselines even on equal-dose legs. RAW is 7 s ahead of the episode clock and rail epoch is 18,000 s ahead. An offset sign error does not pass.

Both legal-null cases require the numeric survivor's floor where available. An unrecognized reason refuses before the claim. The gapped DC case cuts about 2.5 s early in L002's recovery while leaving its baseline window intact. Rail gaps, localized malformed legs and zero denominators assert the already-defined invariants; a new ruling on marks/reason tokens requires a separately named supplemental freeze. The tests do not assign a new paper-facing vocabulary.
