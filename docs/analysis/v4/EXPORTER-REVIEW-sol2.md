# Native exporter review — Sol seat 2

**Verdict: HOLD.** Reviewed 2026-11-08 (PST), `6d0f9c731` on
`align/2026-11-08-exporter-review-sol2`, against release runbook §6a/§6a.2
and `origin/main:RUN_STATE.md` items 235–247. Synthetic evidence only.
No production code changed; fixes and final admission belong to the lead.

## Findings

### F1 — HIGH: an empty capture census hides manifest-bound captures

`scripts/export_v4_series.py:649–672,728–730` makes opening the finalized
manifest/session conditional on `record.captures()` being nonempty. With all
capture descriptors accidentally null, `session` stays null, so the later
`capture_missing_from_record` check cannot see any plist. The committed
finalized manifest itself can already name all 22 captured C1 plists.

Witness: `test_all_null_captures_cannot_hide_manifest_bound_plists`. It changes
only the committed capture census and its inventory, retaining the original
committed finalized manifest and original restored session. The required
behavior is refusal, not a zero-capture export.

This is an operator/inventory-builder failure, not a rename race. Both builds
would receive the same false absence; a retry/replacement decision can then
discard an actually captured window. Check capture presence against the
record-bound inventory even when the census is empty; do not require real
custody to be present merely to inspect that committed inventory. Preserve
genuine zero-capture attempts and their retries.

### F2 — HIGH: incremental export trusts prior state despite new record pointers

`scripts/export_v4_series.py:1000,1016,1032–1040` accepts a landed state solely
by `attempt_id`. It never compares its recorded commit/path to the configured
entry (and does not bind the configured `final_record` adjudication either).
Exporting C1 with a corrected/replaced W1 pointer can silently keep the old W1
cohort, exclusions, reference energies, roster and files in both layouts.

Witness: `test_incremental_export_must_bind_prior_state_to_configured_record`.
The newly committed W1 contains an unknown key: reading it explicitly refuses,
but exporting C1 is allowed to reuse the older W1 state without reading that
record. The malformed replacement is a sharp demonstration of the missing
binding; the same path applies to a legitimate corrected adjudication.

Compare the complete custody/adjudication identity before reusing a landed
state. Refuse a changed prior identity and require an explicit rebuild into a
new export root. An attempt ID alone is not an immutable custody identity.

### F3 — MEDIUM: terminal evidence is not bound to its own night plan

`scripts/export_v4_series.py:612–628` checks the result schema, exit code,
presence of `courier_sent`, and equality to restored result bytes, but never
checks `result.plan_id` against the committed night plan. A stale GO result
copied into the current window can satisfy all these checks. Both builds
then use the same unrelated successful terminal result.

Witness: `test_terminal_result_must_belong_to_its_night_plan` supplies a real
temporary, digest-bound result with `plan_id=previous-window`, while the
record's plan says `current-window`; matching chain exit and restored bytes
do not make it this plan's result. Refuse the mismatch/missing ownership and
retain the existing digest checks. This witness exercises the terminal helper,
not a complete forged production session.

### F4 — MEDIUM: an inconsistent W1 stage becomes a shared wrong covariate

`scripts/export_v4_series.py:384–386` trusts the collection row's stage suffix.
The production W1 kit fixes ordinals 1–9 in stage a and 10–18 in b
(`scripts/align_v4_kit.py:1392–1408`). An ordinal-6 `stage_id` accidentally
changed from a to b is accepted although its run ID/config still name a.
The exporter then sets BOTH the engine row's `stage` and the recompute's
`contrast.stage` to 1. Agreement cannot detect this mislabeled stage covariate.

Witness: `test_w1_contrast_stage_must_match_registered_ordinal`. Check the
stage against the production ordinal/run-ID/config allocation and refuse an
inconsistency rather than silently relabeling it.

### F5 — MEDIUM: mandatory series-input digests are optional in code

Runbook §6a.1 requires `u3_bar`, `registration_inputs` and `r1_references` to
be `{path, sha256}`. `scripts/export_v4_series.py:267–275` only checks a digest
when supplied. A config missing the hash reads whatever currently occupies
that path and derives both builds' inputs from it. A digest checked on the
derived export does not bind those inputs to the intended registered source.

Witness: `test_series_reference_requires_a_digest`, with a wrong-digest
negative control. Require a correctly shaped 64-hex SHA-256 on every external
reference before reading. Allocation has its own exact frozen pin already.

## Coverage and limits

| Requested area | Review result |
|---|---|
| `identity_sha256` | Canonical ordered per-turn prompt/output pairs from verified `align_turns.jsonl`; null if either list is absent. Unit witnesses pin order and boundaries. No new defect found. |
| `registered_span_ns` | Matches WP22: first G0 start, otherwise episode start, through episode end. No new defect found. |
| Thermal journal | Engine gets the verified original rows as JSON; recompute gets production `normalize_journal` output. The new positive control exercises production reading/session shapes. No new projection defect found. |
| Raw/config/plan digests | Captured-member config/kit writer chain, own-window collection plan, raw plist/capture digest, meter stream digest and journal read all have explicit verification. F1 bypasses that path for a falsely empty window; F3 adds missing terminal ownership; F5 concerns external series inputs. |
| Plan ownership | C/T header, manifest and optional attempt checked; W1 kit header checked. F4 identifies missing stage consistency within an otherwise owned plan. |
| Seed index / derived seed | Episode seed is copied verbatim; every roster member carries both seed values. Both pinned consumers independently perform config/seed checks, including anchors. No exporter seed substitution found. |
| Production names | C/T non-anchor names are checked by ordinal; anchor aliases are slot/record bound. W1 names are passed through from its committed plan. The existing producer run exercises these names. |
| R24 | Exact native-manifest SHA-256 `21313cc2791865e01f322c24606db62ba2ac6a65adda6d737e5b7432bef2ad5c`, 18-window order; recompute gets those bytes, engine gets the checked analysis projection. No new allocation defect found. |
| A27 | Positive executing control: scored C-sabotage primary and battery-member rows seal. Primary member/token/cache and U1/U2/battery aggregate print paths were traced; 30B anchor-sabotage exemption is preserved. No new defect found. |
| Zero capture / retries | Genuine C2-z1 then C2 retry covered; F1 distinguishes genuine absence from a contradictory census. |
| `kit_not_normalized` | Correct refusal for a valid non-normalized kit; malformed configs remain consumer-owned `config_invalid`. Existing focused witnesses exercise both. |
| Incremental export | Per-window immutable landing and prefix ordering work for unchanged identities; F2 is a stale-identity bypass. |
| Determinism | New controls compare retry re-export and independently fresh W1 output, excluding only the intentionally appended timing log. |
| Refusal / guessing | Several explicit refusals work; F1–F5 are accepted inconsistent or unbound inputs. No threat-model argument is needed for those cases. |

**Rejected A27 candidate.** My initial static trace suspected that retaining
`battery.members` in the aggregate printer leaked SOC/charger arrays. The
executing witness passed: engine.py:675–678 already wraps every battery member
with `_member_output`, before engine.py:700–708. The actual pinned-engine fill
seals scored C1 ordinals 9/18, including their battery rows. That candidate is
withdrawn; the witness is retained as a positive control. This executing check
prevents the incomplete source trace from becoming a false HOLD reason.

**DC span needs a lead interpretation, not a new ruling here.** The exporter
sets `member_span_ns` to Episode start/end. Production `km003c.session_report`
uses `harvest.member_spans(metadata, events)['member']`, which includes the
sampler/battery hull and can be longer. The positive diagnostic
`test_dc_export_span_differs_from_production_whole_member_span` demonstrates
the difference on the synthetic native bundle. Runbook §6a.2 already lists
this as open. Both analysis builds use Episode spans, so their agreement does
not validate a production whole-member DC number. This is secondary,
print-only; no claim of a registered GPU-score defect is made.

**Air/JW-EXT path check.** The exporter consumes the restored session, not
the compressed inbox directly. Harvest-off `unpack` takes the configured
JW-EXT inbox path and restores at the finalized absolute `source_root`;
export then requires that exact path as `session_root`. Records, kit and
reference paths are also configuration, with no hard-coded `/Users/edr`
source in the exporter. The native synthetic fixture really finalizes,
packs, moves away the MBP-side session, unpacks, and deletes the old session
and pack before export. This establishes restored-copy consumption in the
synthetic regular-file layout. No real JW-EXT inbox, real custody, external
measurement path, network or native hardware was accessed. Native N1 census,
cross-host closure/identity and real SSD restore remain lead-owned gates.

The branch's known §6a.2 producer/consumer prefix disagreements remain known
limitations; this review does not mistake their expected failure for a release
AGREE, nor validate later engine/recompute patches by inspection alone.

## Files and verification

- `tests/v4_export/__init__.py`
- `tests/v4_export/test_review_sol2.py`
- `docs/analysis/v4/EXPORTER-REVIEW-sol2.md`

Focused modules ran sequentially under Python 3.13.18:

- `python3.13 -B -m unittest tests.v4_release.test_exporter_units`:
  16 tests, all pass, 0.793 s.
- `python3.13 -B -m unittest tests.v4_release.test_exporter_e2e`:
  34 tests, 33 pass and the existing documented release-agreement expected
  failure, 879.530 s. Both consumers exited 0. This includes first-time
  synthetic fixture generation and real finalize/pack/unpack.
- Seat-2 module: final rerun, 11 tests in 68.732 s, exit 0: six controls pass
  and five expected failures reproduce F1–F5. Those `expectedFailure`
  decorators mark unfixed defects, not successful property checks.
  The exact invocation also prints each expected
  failure's traceback tail to check that it failed at the intended assertion:

```sh
python3.13 -B - <<'PY'
import unittest
suite = unittest.defaultTestLoader.loadTestsFromName('tests.v4_export.test_review_sol2')
result = unittest.TextTestRunner(verbosity=2).run(suite)
for test, detail in result.expectedFailures:
    print('\nWITNESS:', test.id())
    print('\n'.join(detail.splitlines()[-12:]))
raise SystemExit(not result.wasSuccessful())
PY
```

The first diagnostic run took 78.191 s and exited 1 solely because the
suspected A27 defect unexpectedly passed. Its five actual defect witnesses
failed at their intended assertions: F1/F2 returned `(0, exported)`, while
F3/F4/F5 did not raise `Refused`. I retracted the A27 candidate, removed that
expected-failure marker, strengthened its two-row presence control and added
an explicit Python 3.13 gate for the pinned engine. The final run above uses
those corrected tests.

Total test time, including both review-module runs: 1,027.246 s (17 min 7 s).
Every module ran in its own process, one at a time. The A27 native-consumer
control is gated to Python 3.13 because the release engine's identity pin
requires that interpreter; no control skipped in this run.

`git diff --cached --check` and a targeted AST syntax parse also pass. No
full-suite run is authorized. No MLX code changed; native MLX, SMC and live
measurement validation were not attempted.

Coordination files and kernel tasks are untouched, per the review brief.
No subagents, cross-model calls, network, push or merge were used.

**Next exact step:** lead adjudicates F1–F5, fixes the exporter,
removes the corresponding `expectedFailure` decorators as properties turn
green, and reruns these focused modules plus the §6a.2 real-producer synthetic
rehearsal at the final release pins. Resolve the DC-span interpretation before
labeling any printed DC number a production whole-member integral.
