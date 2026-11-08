# R11 delta3 review — Sol1

**Verdict: HOLD.** The delta2 witnesses now pass, but the replacement receipt
boundary still admits changes to production execution without the required
delta review. G1 also permits an accidentally reused older-window packet; G3
permits an unrelated unclosed stream to replace the authenticated one. These
are candidate-validity and custody findings, not requests for more science or
for deliberate-forger defenses.

Candidate: **9891d679b**, range `git diff f993b784f..9891d679b` (33 paths).
Seat: `align/2026-11-08-v4-r11-delta3-sol1`. Read both independent delta2
reports from their origin refs and the relevant protocol, lead rulings,
callers and tests. New witnesses: `tests/align/test_r11_delta3_sol1.py`,
commit **a7300ba4f**. No product code changed. This review grants no W1 arm
or registration authority and does not admit the entire inherited stack.

## D3-S1-F01 — HIGH: eleven amendment exceptions execute on the production path

`v4_registration.py:316–338` says the allowlist contains modules proven not
executed on W1/D/R1. That claim is false for at least these eleven paths:

| Actual execution edge | Wrongly amendable files |
|---|---|
| `run_night.py:50–51`, eager imports, before choosing HAZARD_PACK | `joulewise/arm_readiness_evidence_t0.py`, `joulewise/t0_rehearsal.py` |
| `run_campaign.command_for` → `python -m joulewise` → `cli.py:35,71,98`; NVIDIA adapter also imports its client | `joulewise/adapters/nvidia_smi.py`, `joulewise/adapters/node_client.py`, `joulewise/kv_size.py`, `joulewise/report.py` |
| `magistrate_watchdog.py:53,60`, eager imports | `joulewise/zero_capture_facts.py`, `scripts/fixture_orphan_census.py` |
| `align_v4_session.install` → pilot installer → `bytes_h_session.install:425` → shell `:92` | `scripts/install_night_agent.sh`, `joulewise/night_agent_install.py` |
| pilot/session desk → `harvest_b6_session.py` → `b6.session` / `b6.acceptance` | `joulewise/session_structure.py` |

Fresh interpreters importing the production entry points demonstrate the
Python edges without calling any main or probe. Module-level Python bytes
execute on import, even when the selected subcommand never calls the imported
utility. The install shell and installer are actual launch-control code, not
retired T0 tools. The refusal census's `not_scanned` taxonomy classifies which
refusals it surveys; it is not proof of nonexecution.

The receipt witness makes a clean committed replacement of the install shell
and, separately, of `arm_readiness_evidence_t0.py`, adds a correctly chained
lead-signed amendment, and calls the real `validate_receipt`. **Both validate.**
Thus this is a working lighter-tier bypass of the scoped review requirement,
not just inaccurate comments. Import classification and the other launch
witnesses fail too. I have not proven the remaining fourteen exceptions
unreachable; the current justification cannot establish that.

**Repair:** remove actual execution dependencies from the allowlist, including
the install and watchdog paths. The smallest safe repair is an empty allowlist
until individual exceptions have a sound path argument. Alternatively make
unneeded imports lazy and then re-prove nonexecution, keeping genuinely used
installer/watchdog/desk dependencies strict. Update the protocol and receipt
tests that currently call `kv_size.py` analysis-only.

## Dynamic closure disposition: the missing scenario matters, but the eight Python paths are statically bound

The committed **159-path** trace's scenarios (`align_v4_dynamic_trace.py:39–46`)
do not include the actual HAZARD_PACK supervisor. WP22 exercises members/desk;
the arm/install suite substitutes the installer. A passing subset trace cannot
justify a negative claim about the rest of production.

I ran the existing short
`test_km003c.NightChainTests.test_existing_block_supervisor_covers_first_idle_through_last_member_and_hashes`
under the same tracer, in a fresh process, with synthetic children and its
mocked hardware/process census. It passes and records **101 paths**, including
these **eight absent from the committed trace**:

```text
joulewise/arm_readiness_evidence_t0.py
joulewise/arm_retry.py
joulewise/b5/driver.py
joulewise/b6/agent_pause.py
joulewise/b6/courier.py
joulewise/dwell.py
joulewise/t0_rehearsal.py
scripts/run_night.py
```

All eight are in the 300 receipt artifacts and the static walk; two are
wrongly amendable (F01). **This scenario does not show a new unbound Python
file.** Walking the Python/shell roots of all 300 artifacts also finds no
additional statically reachable file. That remains a syntactic check, not
proof of arbitrary configured/native execution. F02 is a concrete production
launch input outside both inventories.

Add this small production scenario, entry-point imports and installation/
watchdog coverage before using the trace to justify exceptions. No heavy
hardware run is needed. The new witness fails separately for its two
amendable paths and its eight missing committed-trace paths.

## D3-S1-F02 — HIGH: the production launch-argument template is outside the receipt

`configs/launchd/com.joulewise.night.plist.template` is absent from all 300
artifacts. `night_agent_install.validate_install:1217–1220` reads it;
`Prepared.render:656–677` uses it to construct the night and dead-man
`ProgramArguments`, environment and calendar. For HAZARD_PACK the production
argv comes directly from this template. The ProcessType check does not bind
the executable/arguments to the reviewed receipt.

The witness includes the actual template in the synthetic checkout at the
reviewed commit, changes its script argument in a later clean commit, then
expects receipt refusal. **The old receipt still validates.** A separate
passing control calls the real renderer without launching anything and
proves that the changed template changes the rendered executable argument.
Recording a hash of the newly rendered plist records the new choice; it does
not compare it to the reviewed registration's choice.

This is configuration that dispatches production execution, not an ordinary
data read. The Python/shell suffix filters in both closure mechanisms miss
it. **Repair:** bind this launch template strictly, audit the associated
launch/probe templates for their actual roles, and add the independent launch
configuration inventory to the receipt check. No change to native MLX is
required.

## D3-S1-F03 — HIGH: G1 checks the latest revision of a named path, not the latest window

`align_v4_session._record_bound:264–272` verifies a blob digest and runs
`git log -1 -- <packet.record_path>`. This correctly rejects a packet after
that *same file* is amended, and correctly tolerates unrelated documentation
commits. Those controls pass.

It does not reject an older-window packet when the next window has its own
record file. The witness commits `staging/window-C2-record.json`, builds a
passing C2 packet, then commits `staging/window-C3-record.json` with a thermal
failure. Reusing the unmodified C2 packet yields **`record_bound=True` and
`triage.admitted=True`**. C2 remains the last commit touching C2's path.
`arm_checks` derives no expected previous-window identity from the series or
arm state; `next_arm_triage` takes its previous-window identity and calibration
history from the reused packet. C3 can consequently disappear from the next
arm's escalation/count history without any contradictory packet field.

This models a stale file selection, not fabricated hashes. **Repair:** give
the arm an authoritative expected predecessor/record identity from the series
state or a canonical append-only current-record pointer, and compare the
packet, record identity and calibration-history tail to it. Keep the blob
digest and same-path revision checks. Do not replace this with a rule that
every unrelated Git commit stales a packet. The precise series-state contract
is lead-owned; this review does not invent one.

## D3-S1-F04 — MED: G3 conflates an unrecorded digest with an unrecorded stream

`km003c.session_report:214–234` discovers every `stream-*.jsonl` in the
directory. `expected.get(name) is None` is true both for a known supervised
stream with no digest and for a file absent from the supervisor's stream
roster. Either is salvaged when it has no trailer. `capture_member` takes
the first covering stream, so a stray file sorted first can replace the
correctly authenticated stream.

The witness preserves the genuine, correctly hashed `stream-001.jsonl` and
adds an unlisted `stream-000.jsonl` containing a different synthetic capture
at the same numeric clocks, with twice the current and no trailer. The desk
selects **000**, status **available**, and reports **168 J instead of 84 J**.
It discloses `meter.stream_unclosed` / `meter.custody_hash_unrecorded`, but
does not distinguish a known crashed reader from an unrelated input.

**Repair:** require explicit supervisor roster membership before applying
the missing-digest salvage exception; distinguish a missing key from a
listed null/missing digest. Prefer an authenticated covering stream over an
unhashed candidate. Retain source digests and unclosed/unrecorded disclosures.
This is a secondary, unregistered diagnostic: the witness changes no rail
exclusion, arm clearance, threshold or standardized score. Its issue is the
custody/source attribution of the printed DC number.

A recorded digest mismatch still refuses, including after trailer removal
(passing control). A known listed unclosed hashless stream salvages a fully
covered earlier member and leaves the later member missing (passing control).
With no prior digest the validator cannot establish byte integrity against
tampering; a digest computed while reading is provenance of the bytes now,
not authentication of the bytes at capture. I request the mistake-shaped
wrong-stream repair above, not an impossible or out-of-model forger defense.

## Admitted parts of this delta

**Top-up rules:** raw adjacency now prevents an off-AC/error row from
manufacturing a charging→float transition. Events require two consecutive
valid timed rows at most 300 s apart. Basis (a) accepts a fresh floating
observation after a sampling gap when the event is at most 1800 s old;
basis (b) requires complete float continuity for an older event. Untimed,
invalid and off-AC rows break (b); out-of-order and future timestamps refuse.
Boundary and gap controls pass. The continuous sampler procedure supplies
the previously missing way to preserve basis (b) across windows. These are
software checks, not live validation of its load or battery behavior.

**G2:** the command block equals `render()`, and kit regeneration occurs
after slot installation and contrast derivation, before `--check`. The first
three steps run against real code on synthetic lane-shaped inputs. Use
`--write-contrast` for a mechanical contrast merge, or stop at
`--until derive-contrast` and perform the documented manual merge before
continuing. Signatures, R10-2 decisions and other pending inputs remain
lead-owned; a pending `--check` still returns failure. No blocking G2 defect.

**Captured ceiling 24:** eight final 24-capture windows now complete with
56 eligible benign per pair. A 25th capture or eighth benign in a pair
refuses, and seven windows still cannot complete calibration. This does not
authorize adding sentinels without the prospective roster ruling; the
`sentinel_roster` triage row remains a gate. The error text still says
`0..22` although the actual check allows 24; cosmetic follow-up only.

Both delta2 witness modules and all touched test modules pass. Full WP22
passes with its one documented collector-death expected failure. No new
estimator or blinding regression was demonstrated by these checks.

## Handoff

The new witness module runs **17 tests: seven pass, ten methods fail**, with
**13 failure records** from subtests. These failures are intentional review
evidence, not a green admission gate. All **347 existing selected test
instances** pass (one documented expected failure). Full commands, timings,
safety exceptions and local commits are in
`docs/run_reports/2026-11-08-align-v4-r11-delta3-sol1.md`.

Next exact step: lead adjudicates F01–F04 with the independent Sol2 seat,
repairs the execution/launch-input and predecessor/source bindings, then runs
both delta3 witnesses and affected modules serially on the integrated
candidate. Keep the U3, final-roster U6, B consequence/charge, R13/R14/F-C-T,
actual series-manifest, native and live custody holds. Native tiny/offline
checks remain owed outside this sandbox; no weights should be downloaded.
