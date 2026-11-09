# R11 delta6 — independent Sol review seat 2

Date: 2026-11-08. Verdict: **HOLD**.

Reviewed `356c41c82..c742e5722` on branch
`align/2026-11-08-r11-delta6-sol2`, excluding the already-reviewed
timing-receipts merge content. Authority: `origin/main` RUN_STATE items 234
(R22), 235 (R23), 236 (R24), and 238 (R24 correction), read at
`0942742cf73bb4d0581d47c90267bee7a43f2a94`. No production changes were made.
This review changes only this report and
`tests/align/test_r11_delta6_sol2.py`.

F1 and F2 are plausible ordinary functional failures and independently justify
HOLD. F3 is a demonstrated pool-admission inconsistency; F4 is an incorrect
required disclosure. These require no adversary or race.

## F1 — HIGH: contention still excludes in the common desk and fails its gate

Locations: `scripts/align_v4_session.py:314`, `:322`, `:189`;
`scripts/align_pilot_session.py:329`, `:364`, `:375`, `:393`.

The new hook strips `contention.*` only from its **separate thermal records**.
The common desk has already set its own members and summaries to `excluded`
from the unfiltered harvest exclusions. Its `chain_eligibility` and
`no_member_exclusions` remain false; its eligible-member list and analysis
also retain the exclusion. `full_desk_gate_pass` neutralizes charging-only
exclusions, but not contention-only ones. The common desk additionally calls
the harvest status `members_excluded`, which `builder.desk_passes` refuses.

Failure scenario: an otherwise sound W1 contains only
`contention.request_overlap` (or a monitor outage produces
`contention.unmeasured`). The new thermal record correctly says not excluded,
but the common desk still excludes the member and the mandatory post-W1 full
desk cannot pass. Later windows can also be blocked. This contradicts R22-1's
disclosure-only rule; a clean window's success does not exercise this path.

Witness: `ContentionWitnesses.test_f1_contention_only_common_desk_member_must_not_fail_full_desk`.
Both catalogued exclusion codes fail, while a clean control passes and a
non-contention exclusion still fails as required. The witness calls the real
common instrument checks and v4 full-desk gate; it mocks only bundle disclosure
I/O for the separate thermal record.

Suggested repair: normalize v4 contention codes before all common-desk
eligibility/check/analysis decisions, retaining the raw codes as disclosures.
Reconcile the desk harvest-status consumer too; changing only the thermal
record or only the full-desk boolean is insufficient. Preserve v3 behavior.

## F2 — HIGH: C9–C14 were added without a U3 comparison scope

Locations: `scripts/align_v4_u3_export.py:32`;
`joulewise/align/apple/thermal_desk.py:887`;
`scripts/align_v4_next_arm_packet.py:299`.

The production U3 policy template still declares W1, C1–C8, and T1–T3
(16 comparisons). None of C9–C14 is present. The thermal desk explicitly sets
U3 to `inconclusive` when a replay's window lacks a scope. The new reserve
manifest and kits do not install another scope or map a reserve to a replaced
comparison slot.

Failure scenario: a barred primary C window licenses a healthy C9. Its two
sentinels have identical tokens, energies, clocks and configuration; U1 and U2
pass. U3 nevertheless becomes `inconclusive` solely because C9 is missing from
the policy. The same happens through C14. The packet reader requires U1–U3
all pass before counting a calibrator, so these healthy reserves contribute
zero eligible benign members. With three primary bars, even five perfect
remaining primaries provide at most 35 per pair; these unusable reserves
cannot restore 39. The U1–U3 escalation check also treats the inconclusive
scope as needing escalation. R24's usable replacement capacity is therefore
not implemented by the ordinary policy-producing path.

Witness: `ReserveU3Witnesses.test_f2_all_armable_reserve_windows_need_usable_u3_scope`.
A synthetic adopted bar whose scope equals the production policy template
passes an identical C8 replay and fails the contract assertion for each of
C9–C14. No thermal or U3 calculation is mocked.

Suggested repair/open question for the lead: install a prospective U3 scope
for replacements and settle its series comparison budget. Simply adding six
names without revisiting N=16 would change the registered false-fail budget.
Whether replacements inherit barred slots or expand the prospective roster
is an authority choice, not one this review silently makes.

## F3 — MEDIUM: terminal-barred windows can still pass with a nonempty pool

Locations: `scripts/align_v4_next_arm_packet.py:606` and `:705`.

The new history pass derives `whole_window_capture_failure` and zeros its
counts. The separate `cohort_pool_rules` check still forbids pool entry only
for U1–U3 non-pass or a member exclusion. It never checks that terminal bar.

Failure scenario: the chain stops after usable captures (for example, a
later chain/cleanup failure), and the series ledger retains one captured
calibrator in `pool_members`. The committed result says `CHAIN_STOPPED`, exit
1, with matching closure. The builder labels C1 barred and excludes its
counts, yet reports `cohort_pool_rules: pass`, `packet_preflight.ready: true`,
and its own rebuilt packet binds successfully for C2. R22-2 says a barred
window enters no pool and permits no partial use.

Witness: `CommittedBarWitnesses.test_f3_terminal_bar_must_also_refuse_partial_pool_entry`.
The empty-pool counterpart passes. All record, terminal, closure, pool and
history inputs are committed in a fresh synthetic Git repository. No builder
decision is mocked.

Suggested repair: reuse the same committed-record structural-bar predicate
in pool admission. Limit of evidence: the calibration **count** summary is
correctly zero; this witness proves that a contradictory pool declaration
passes admission, not that a downstream numerical fit actually consumed it.

## F4 — MEDIUM: balance silently drops contention disclosure events

Locations: `joulewise/align/apple/v4_balance.py:26`;
`joulewise/align/apple/v4_contention.py:131`;
`scripts/align_v4_session.py:322`.

Contention codes are moved out of exclusions into
`record.contention.disclosed_codes`; newly detected coverage flags are also
nested in `record.contention`. The balance event counter reads only the
top-level flags and calibration exclusions. Thus the real normalized desk
records lose these events from the printed balance check. The existing
balance test passes an unnormalized contention exclusion, bypassing the
actual producer/consumer mismatch.

Failure scenario: a benign member has one contention-overlap event and no
other flags, while sabotage has none. After the new normalization, the balance
report prints zero events rather than one, understating the condition-specific
contention imbalance that R22-3 requires disclosing. This does not itself
change the eligibility count or gate.

Witness: `ContentionWitnesses.test_f4_balance_must_include_contention_events_moved_to_disclosure`.
The real attachment moves the code and correctly preserves eligibility;
the real balance report then returns 0 instead of 1.

Suggested repair: include the normalized contention disclosure codes/flags
in the balance event inventory with a documented duplicate-count convention.

## Nonblocking documentation correction

`docs/align/pilot_protocol_v4.md:1037` and
`docs/align/squeeze/fanout/r11-dispositions.md:181` still say drift lowers
gate-admitted FPR as the cap increases. RUN_STATE 238 corrects this: under the
registered T-after-stop placement, C14 raises it versus C10 by 0.03–0.17
percentage points in the b=.05 stress settings; C14 stands, and drift/T
placement is disclosed. Update those derived explanations. This is not a
request to alter the frozen manifest or a HOLD reason on its own.

## Checks that held

- Frozen manifest SHA-256 is unchanged:
  `21313cc2791865e01f322c24606db62ba2ac6a65adda6d737e5b7432bef2ad5c`.
  Its bytes match the generator. W1, C1–C8 and T1–T3 match the base manifest
  window objects exactly. Each pair's reserve indices are C9 100–107 through
  C14 140–147, contiguous, with no development indices.
- Structural-bar derivation reads committed thermal and terminal sources;
  irrelevant scores/counts do not make a completed GO chain barred. Barred
  rows' calibration counts are zero. F3 identifies the separate pool gap.
- The ledger requires reserves in order after primary slots and only for
  bars; eight unbarred low-m windows do not license C9. Six bars can be
  replaced to reach exactly eight admitted windows. A seventh structural bar
  gives `insufficient_calibration`; a seventh zero-capture retry bar escalates.
- The latest U4-only sentinel check and thermal-desk consequence have the
  intended inconclusive trigger. U5 inconclusive alone does not request extra
  sentinels; U4 inconclusive does. Existing U5 FAIL descriptive consequence
  remains in the protocol; this review does not treat that as the removed
  inconclusive sentinel trigger.
- The R1 export fixture runs successfully with injected clocks, including
  the simulated OS-batch wait. No real wait or measurement was performed.

## Verification and handoff

Every unittest invocation used Python 3.13, synthetic inputs, one module per
process, sequentially. Full-suite execution was expressly forbidden and was
not attempted. Timing-receipts tests were excluded from this review.

| Command | Result |
| --- | --- |
| `python3.13 -B -m unittest tests.align.test_v4_replacement_windows` | PASS, 20 tests, 38.981 s |
| `python3.13 -B -m unittest tests.align.test_v4_contention` | PASS, 7 tests, 3.238 s |
| `python3.13 -B -m unittest tests.align.test_r1_turn_counts_export` | PASS, 13 tests, 1.641 s |
| `python3.13 -B -m unittest tests.align.test_v4_next_arm_packet` | PASS, 32 tests, 379.901 s |
| `python3.13 -B -m unittest tests.align.test_v4_balance` | PASS, 4 tests, 0.001 s |
| `python3.13 -B -m unittest tests.align.test_v4_series_r20` | PASS, 10 tests, 5.985 s |
| `python3.13 -B -m unittest tests.align.test_r11_delta6_sol2` | Final run: 11 tests, 37.202 s; four witness methods red, 10 failing assertions including subtests, no errors; seven control methods pass. Initial run had the same findings in 14.868 s. |

The six existing modules pass all 86 tests. Total unittest time including both
witness runs is 481.817 s (about eight minutes). Witness syntax parsing and
Git whitespace checks pass. No full compile or full-suite run was needed for
these two review-only files.

The new witnesses intentionally assert the rulings and fail on the reviewed
head. They are not marked expected failures. No implementation fix is hidden
in this review commit.

No network, weights, native MLX, hardware probes, measurement pipelines or
real custody paths were used. Test data consisted of this clone's code/configs
and synthetic temporary repositories/files; shared Git objects were read as permitted.
Coordination files were left unchanged per the brief; this report is the
handoff record. No agents were spawned and no external consult was used.

Next exact step: lead dispositions F1–F4, decides the U3 replacement scope,
and lands repairs with these witnesses rerun. Then rerun the focused modules
listed here and the lead's native arm/desk rehearsal on synthetic inputs. Native
MLX behavior and Python 3.11 were not exercised here; any native integration
claim remains for the lead outside this sandbox. Do not perform live
measurements in an agent session.
