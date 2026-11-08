# ALIGN v4 R11 delta3 review — Sol2

**Verdict: HOLD.** The delta2 witnesses now pass. Three remaining findings
affect exact-candidate review, stream custody, and the claimed stale-packet
guard. These are bounded repairs; I found no reason to reopen the estimator,
fixed-eight rule, or the accepted top-up alternatives.

Candidate: `9891d679b`; reviewed range: `git diff f993b784f..9891d679b`
(33 files), with necessary callers and both delta2 seat reports from their
local origin refs. Seat: `align/2026-11-08-v4-r11-delta3-sol2` (already
provisioned and clean at intake). Witness commit: `6e3962cd6`.
Product code and coordination state are unchanged. The new witnesses are
deliberately red; this report does not authorize registration or a live arm.

## D3-S2-H1 — HIGH: the amendment allowlist includes actual execution code

`v4_registration.py:323–338` describes all 25 exceptions as not executed on
the W1/D/R1 path. This is false for both imports and actual launched tools.
The refusal census's `not_scanned` classes describe that census's scope;
they do not prove absence from execution.

The W1 install route is concrete:
`align_v4_session._arm_and_install` → `align_pilot_session.install` →
`bytes_h_session.install` (`:425`) launches
`scripts/install_night_agent.sh`. That wrapper (`:92`) execs
`python -m joulewise.night_agent_install`. **Both executable files are
amendable.** The synthetic installer witness calls the real session helper,
substitutes its process runner, and captures exactly this argv. No host
operation runs. Calling the installer retired or pre-arm tooling does not
make it irrelevant: it publishes the job and interpreter/plan arguments
that determine whether and what W1 runs.

A fresh subprocess importing the real production entry modules (without
calling any main/probe) executes **11 allowlisted module bodies**:

| Allowlisted file(s) | Current execution edge |
|---|---|
| `joulewise/adapters/nvidia_smi.py`, `joulewise/adapters/node_client.py` | `cli.py:35` imports NVIDIA helpers eagerly; NVIDIA imports the node client |
| `joulewise/arm_readiness_evidence_t0.py`, `joulewise/t0_rehearsal.py` | `run_night.py:50–51` explicitly imports retired dependencies eagerly for preflight |
| `joulewise/floor_extraction.py` | `run_campaign.py:210` imports it eagerly; `anchor_fallback_member_unusable` is also called at `:2933` and `:7581` |
| `joulewise/kv_size.py`, `joulewise/report.py` | `cli.py:71,98` eager imports, including on `python -m joulewise run` |
| `joulewise/night_agent_install.py` | The actual installer module above |
| `joulewise/session_structure.py` | `harvest_b6_session` imports B6 session/acceptance, which eagerly imports its stop-code definitions |
| `joulewise/zero_capture_facts.py`, `scripts/fixture_orphan_census.py` | `magistrate_watchdog.py:53,60` eager imports; zero-capture facts are used at `:887` |

Two additional allowlisted scripts are visibly launched by the current
session lifecycle: the installer above and `scripts/bytes_gates.py`
(`bytes_h_session.py:848`, the post-harvest desk). Thus **13 of 25** have
concrete execution edges in the inspected lifecycle. This is not a request
to treat a genuinely unused alternate platform as selected: Python executes
an eagerly imported module's body regardless of which CLI verb follows.

The remaining 12 entries are `arm_readiness_evidence.py`,
`quiet_predicate_campaign.py`, `v5_qualification.py`, `capture_t0_step.py`,
`check_v5_arm_abort.py`, `produce_t0_rehearsal_bundle.py`,
`write_v5_qualification_plan.py`, `envelope_gate.py`, `b6/precheck.py`,
`b6/smoke.py`, `advance_b5_ledger_pin.py`, and
`issue_calibration_acceptance_generation.py` (under their existing
`joulewise/` or `scripts/` prefixes). I inspected their import/launch
references; most belong to conditional retired, smoke, or issuance routes.
I did not demonstrate their execution on this W1 configuration, and do not
claim an exhaustive proof that they can never execute.

The new receipt witness commits changed startup-module bytes in an isolated
synthetic Git repository, supplies a correctly signed amendment, verifies
the tree is clean, and expects refusal. `validate_receipt` instead admits
it. Together with the actual installer edge, this affects the strict
execution-review obligation, not merely documentation precision. An
ordinary import break or installer change can strand a real arm under an
otherwise valid old receipt.

**Repair:** remove current execution paths from the exception list; or move
truly unused eager imports behind their unused branches and review that
strict caller change. Keep actual installation/acquisition and
number-bearing desk code strict. Check the allowlist against independent
production startup and mocked launch inventories, rather than the refusal
census category alone.

## D3-S2-H2 — HIGH: G3 accepts an unlisted or unsupervised stream as available DC

`km003c.session_report` (`:214–234`) uses `expected.get(name) is None`
for both a **recorded stream with a missing digest** and a file **absent
from the supervisor's stream inventory**. A missing/unreadable
`night/hazard_result.json` becomes an empty inventory, taking the same path.
Any globbed, parseable, unclosed stream whose timestamps cover a member can
then supply available DC energy with `meter.custody_hash_unrecorded`.

Two mistake-shaped witnesses reproduce this using only synthetic streams:

1. The supervisor names `stream-001.jsonl`; rename the sole unclosed file
   to `stream-099.jsonl`, which the supervisor never names. The covered
   member remains `status=available` instead of missing.
2. Remove the synthetic supervision record entirely. The same member still
   becomes available.

This can admit a wrong/copied stream. With no prior digest, byte corruption
or replacement is also not authenticated by hashing the newly read bytes;
the disclosure flag records that absence but supplies no capture identity.
The available row can enter benign DC fitting. This matters even though
the channel never changes rail admission: the protocol (`:791` onward)
retains whole-member DC as authority for small effects.

**What works:** if a digest was recorded, changed unclosed bytes are refused;
closed streams with missing/wrong hashes remain refused. A supervised
crashed stream retains only fully covered members, flags unclosed status,
and leaves the later uncovered member missing. Those controls pass.

**Repair:** distinguish inventory membership from a missing digest. Require
evidence that this reader/stream belongs to this window before numerical
salvage. Preserve a stopped reader's bytes through the existing custody
inventory when possible; if provenance/integrity cannot be established,
retain them as unverified diagnostics without presenting authenticated
available DC or using them for fitting. Do not add a rail/window refusal
or discard properly supervised, bound crash-prefix evidence.

## D3-S2-M1 — MED: G1 checks the latest change to a chosen path, not the latest window

`align_v4_session._record_bound` (`:267`) runs
`git log -1 --format=%H -- <packet.record_path>`. It correctly rejects a
record re-committed **at that path**, but neither fixes that path nor checks
an authoritative latest-window pointer.

The witness commits C2 at `staging/window-C2-record.json`, creates its
valid packet, then commits C3 at `staging/window-C3-record.json`. The C2
blob and its last-changing commit still match. `_record_bound` stays true
and the full `next_arm_triage` admits the old C2 packet and history. Both
Git commits and the worktree are ordinary, clean synthetic records.

No current contract requires all windows to overwrite one canonical record
path; per-window filenames are even used by the G1 fixture. This is an
ordinary stale-packet reuse case, not a fabricated signature. Consequently
the claim that a stale packet refuses is broader than the implemented guard.

**Repair:** enforce one canonical latest-record path, or bind the packet to
the authoritative latest-window identity/pointer and expected predecessor
of the next arm. Preserve unrelated-commit tolerance. Existing tests for
same-path updates, wrong hashes, missing blobs and unsafe paths all pass.

## Disposition of the seven requested checks

| Check | Assessment |
|---|---|
| Strict default / 300 bound paths | Prior missing `__main__`, configured R1 script/config and calibration launcher defects are fixed. H1 remains in the exception classification. |
| Dynamic trace / dropped hazard harness | The 159-path trace is useful positive evidence, not production completeness. The static walker currently finds 284 paths, all bound. The independent production-import inventory and all named W1 chain tools are also bound. I found **no concrete additional executed path missing from all 300 artifacts**; the demonstrated production gap is tier classification. Dropping the hazard harness leaves real startup/installer paths untraced, while the static inventory still covers those inspected paths. |
| Top-up evidence | ADMIT this repair: transitions require consecutive valid raw rows and <=300 s separation; errors/off-AC/untimed rows cannot vanish between them. Old-charge basis (b) requires continuous valid float and fresh tail. Recent-charge basis (a) separately allows a logging gap, preserves the inclusive 1800 s bound and fresh floating observation, and refuses subsequent valid charging. The live arm still probes its battery predicate and OBC attestation. |
| G1 record binding | Same-path freshness is fixed; M1 remains for distinct per-window record paths. |
| G2 chain script / doc | ADMIT the regeneration-order repair. Commands match, and regeneration precedes `--check`. Use `--write-contrast` for an unattended end-to-end wrapper run; otherwise step 5 only prints fields for manual installation, so stop there before continuing. Pending signatures/U3/WP19 still fail closed. |
| G3 crash salvage | Covered-prefix arithmetic and recorded-hash refusal pass. H2 remains for unlisted/unsupervised input. |
| Captured ceiling 24 | ADMIT: eight 24-capture windows complete with at most seven calibrators per pair/window; 25 captures or eight calibrators per pair refuse. This upper bound does not itself authenticate sentinel addition; the separate roster gate remains necessary. |

The continuous battery logger resolves the documented between-window gap
in synthetic evidence. Its real supervision, observer/load accounting,
initial charge acquisition and through-window continuity have **not** been
qualified by this review. I did not run it on this machine. Computed paths,
third-party dependencies, native execution and actual custody remain
separate live/lead boundaries; the trace is not a replacement for them.

## Verification and handoff

Every touched test module ran separately, serially, plus the separate full
WP22 and focused synthetic caller/parser checks: **361 baseline test
instances passed**, with the one documented WP22 collector-death expected
failure. Final new witness run: **13 tests, seven passing controls, six
failing methods (17 failure records including subtests), zero errors**.
The failures expose H1/H2/M1 and intentionally remain red. Compileall and
whitespace checks pass. Command counts/times, files and local commits are
recorded in `docs/run_reports/2026-11-08-align-v4-r11-delta3-sol2.md`.

No network, weights, native MLX, live collection, real measurement inputs,
sealed directories, full suite, job census/control, push or coordination
state edits were used. The additional parser selection was only synthetic
`tests.test_km003c_parse` plus `tests.external.test_km003c_parse.OffsetTests`;
the recorded-data fixture tests were not run. The review used repository
objects and synthetic temporary custody/Git repositories. No peer agent
was invoked; this is the independent Sol2 seat.

**Next exact step:** lead disposition these three findings with Sol1,
repair H1/H2/M1 at one candidate, then run both delta3 witness modules and
the affected modules one per process before Stage B. Preserve outstanding
U3, final-roster U6 OC, B consequence/charge hold, actual series manifest,
scorer/dependence, native identity/cache and live custody gates. This review
does not close any of them.
