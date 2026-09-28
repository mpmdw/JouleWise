SEAT: Opus 5.5 — NTP-ENFORCE-DESIGN-01

Read at `d5f624b6` (worktree). Nothing run beyond reading. "Inference" marks what I did not execute.

## 1. Architecture: one window record, checked where it is used

I back the scout's attestation-plus-admission design over a pending-to-final ledger. Finalized rows are immutable, and three sites must agree exactly on the ledger's endpoint universe (`calibration_bracketing.py:1845-1847, 2189-2221, 2711-2731`; the comment at 2724-2729 says one-sided drift refuses every window "forever"). So an H6-failed row **stays in the universe** and is refused where it would be used, exactly as an invalid endpoint is.

**Producer: the night driver, not the chains.** Every headless route (calibration, evidence, pack) passes one process, `scripts/run_night.py`: pack preparation or quiet binding (3057-3075), then `_run_chain_once` (3217). The driver owns H5 and the H6 query for all kinds, so the pinned derivation chain does not change (A3 §4.4 permits "setting the state from the arming session, outside the capture chain"). The records go in `<custody>/night/network_time/` and are written once (exclusive create):
- `h5-off.json`, `h5-on.json`: argv, exit code, exact stdout, wall time, monotonic time and `kern.bootsessionuuid`;
- `h6-query-N.txt`: the raw `log show` bytes;
- `h6-window-N.json`: argv, exit code, the raw file's sha256, whether the header matched, the query time on both clocks, the boot id, the witness line and its UTC time, every marker with its UTC time, any parse refusals, plan/window/session ids, and the sha256 of `h5-off.json`.

The window record holds **no per-capture verdicts**. A capture's verdict is computed where it is used, by one pure function, `capture_verdict(window_records, capture_bounds)`. `capture_bounds` holds the capture's first and last paired readings, read from its own hashed evidence (the same bytes that carry B). The capture is clean only if all of these hold:
1. at least one query run passes conditions (1) to (3);
2. the witness is older than the capture's first reading minus 180 s;
3. the first reading is at least 600 s after OFF on both clocks, in the same boot;
4. the query ran after the capture's last reading plus 1 s, on both clocks;
5. no valid run has a marker from 180 s before the capture to 1 s after it, each end taken from the wider of the two clocks (reuse the union rule of `quiet_predicate_campaign.py:610-635`).

Anything else is `network_time_unattested`, except a marker, which is `network_time_slew_attested`. **A missing record gives unattested.** So no roster has to be complete, and a manual run leaves nothing to trust: `launch_window.py`, a direct campaign run, or a desk writer run have no driver record, so their captures are unattested.

**Proposed tightening (judge to rule):** the query starts 3,600 s before the OFF moment, which is earlier than the ruled S, and ends when the query runs. The witness must also be older than OFF. Because OFF comes at least 600 s before every capture, this implies A3's witness rule and removes any dependence on which capture was first. The 3,600 s before OFF is longer than `timed`'s longest recorded silence, 1,881 s (A3 B1). If the judge refuses the tightening, the driver seals the roster when it queries (fallback).

**Which windows H6 applies to.** H6 is required unless a closed exemption list covers the capture: the pre-25G83 identity epochs, and the W1/W2 session ids that their sealed registration governs. An unknown future build therefore requires H6 by default.

**Consumers:**

| Route | Where it refuses |
|---|---|
| Derivation → issuance | `_select_members` (`issue_calibration_acceptance_generation.py:1255-1323`) checks H6 **before** the anchor replay. A failed capture becomes a named exclusion with the H6 reason, which takes precedence. Add both strings to `REGISTERED_CORPUS_EXCLUSION_REASONS` (`calibration_bracketing.py:293`). The issued file gains `network_time.windows[]` (digests) and a state for each member. The completeness validator (`:996-1027`) refuses a member that has no clean verdict. `tests/verify_calibration_acceptance_corpus.py` recomputes each verdict from the committed raw bytes. The issuer needs one record per registration session: a missing command-line flag refuses (operator error), while a record that says "no valid query" excludes (A3). |
| Bracket pre/post | `build_calibration_bracket_binding` (`:1302-1381`) and `build_bracket_binding.py:250-258` refuse an H6-failed endpoint as they refuse an invalid one. The binding digest covers the H6 record's sha256. `validate_calibration_bracket_binding` checks it again. Endpoint selection skips H6-failed rows but keeps them in the universe. |
| Evidence and idle nights | `pilot_summary` (`quiet_predicate_campaign.py:1139`; the verdict read at `:1302-1308`) requires **both** verdicts: the unchanged per-envelope query and the window verdict. It uses the two strings that are already registered (`:55-56`). |
| Claim pack | Claim evaluation calls `capture_verdict` for every claim-bearing capture and bracket; one failure holds the whole claim. The scout did not find the pack's harvester (report §map, pack row). Phase 2. |

**No-route tests** (`tests/test_network_time_routes.py`):
- **NR-1:** one window with three ledger-valid captures: clean, marker at −179 s, and no record. It is driven through every production consumer above, plus the `build_bracket_binding.py` CLI and `calibration_bracket_for_bundles`. The assertions are the H6 reason (not `off_ledger_artifact`) and anti-withholding equality intact.
- **NR-2:** the same inputs with the record made clean, and everything admits. This proves the refusals come from H6, as D-138's HR-4 does.
- **NR-3:** an AST census of production call sites of the entry points (`_select_members`, `_candidate_from_observation`, `discover_calibration_candidates`, `build_calibration_bracket_binding`, `evaluate_calibration_bracket`, `pilot_summary`) and of `== "valid"` disposition comparisons, against a pinned list. It is a tripwire only; NR-1 is the proof. The D-138 hold refuter showed that a literal census can be escaped (`50-d138-issuance-seat/refuters/hold-refuter-2-opus.md:87`).
- **NR-4:** a synthetic future epoch with no record is refused.

## 2. H5 lifecycle

- **Who sets OFF.** The driver's first machine action after authenticating the plan and before binding or pack preparation (`run_night.py:~3057`). It reuses `arm_readiness.EXPECTED_NETWORK_TIME_OFF_STDOUT` (`:104`, which includes the newline). Anything other than an exact success refuses the night before any chain runs (cap C9). The evidence campaign's own OFF/ON toggles (`:1626`, `:1767`) and the arm probe (`arm_readiness_evidence_t0.py:1225-1256`) stay. Setting OFF twice is harmless, and the driver's receipt is the one of record.
- **Proof of 600 s.** Both clocks are compared per capture in rule 3 above. Proof of same boot: the boot id at OFF equals the boot id at query time. Both stamps use `time.monotonic()` (`joulewise/clock.py:59`; `set_network_time`, `quiet_predicate_campaign.py:348-354`).
- **Restoring ON.** A `try/finally` around everything after OFF: query first, then ON. A `restore-pending` marker is created at OFF and removed once the ON receipt is written. `dead_man` (`run_night.py:3353`) and any later driver start see the marker: they run the query if none was valid, then set ON. The restore never raises; a failed restore is reported and changes no verdict (the campaign's precedent, `:394-469`). If termination is not proven, no query runs next to a live capture (`:869`, `capture_still_live` rationale); `dead_man` queries later. Whether the watchdog's stand-down reaches `dead_man` is not checked (inference).

## 3. Files, scope, order

**Seat P1 (critical path, before cap step 10). WRITE_SCOPE, exhaustive:** `joulewise/network_time_window.py` (new), `tests/test_network_time_window.py` (new), `tests/test_network_time_routes.py` (new), `scripts/run_night.py`, `tests/test_run_night.py`, `scripts/issue_calibration_acceptance_generation.py`, `tests/test_issue_calibration_acceptance_generation.py`, `joulewise/calibration_bracketing.py` (the reason set, the exemption tables and the validator hook only), `tests/test_calibration_bracketing.py`, `tests/verify_calibration_acceptance_corpus.py`.

P1 also adds a driver interlock: `NETWORK_TIME_ENFORCED_KINDS = {"calibration"}`. Any other kind refuses to launch until its consumer lands, which keeps H5 and H6 "in force before the next window of any kind" by refusal.

**Seat P2:**
- the evidence consumer: `quiet_predicate_campaign.py` and its tests. This moves the sealed per-file manifest; A3's vocabulary is unchanged.
- bracket binding: `calibration_bracketing.py`, `build_bracket_binding.py`, `tests/test_bracket_binding_cli.py`.
- the pack harvester, once found, plus `launch_window.py`.

**Composing with D-138.** D-138's R-1/R-2 already keep 25G83 claims closed (claim-bearing preflight refuses at the R7 default). Add, next to R-2, an import-time guard that refuses a 25G83 default while `PACK_NETWORK_TIME_ENFORCED` is False. The hold then cannot be released without P2.

**Order:**
1. D-138 issuance merges (cap step 1).
2. P1 rebases on it (both touch `calibration_bracketing.py`) and lands as cap step 2.
3. The bench check (§4).
4. Cap steps 3–9. Freeze is unaffected: no pinned estimator file is touched.
5. Test: replaying W1/W2 is unchanged (exempt), which keeps step 7's B-identity check intact.
6. The successor registration (step 10) carries H5–H7.
7. P2 lands before step 16.

P1 must land before step 10, because a later derivation-path fix re-runs both windows (cap step 15).

**Tests.** A3's six synthetic tests, plus:
- a nonzero exit with a plausible witness;
- a header with trailing spaces (the real one has them);
- a marker on a tab continuation line (169 such lines in the preserved pull) inheriting its parent's time, and a continuation line before any timestamp → unattested;
- offsets −0700 and −0800, and a window crossing a daylight-saving change → unattested;
- first reading at 599 s on one clock and 600 s on the other;
- a boot change;
- a query run before the last reading → that capture unattested;
- run 1 timed out and run 2 valid → clean; two valid runs that disagree → unattested;
- a raw-digest mismatch;
- all restore paths: normal, chain nonzero, refusal, exception, SIGTERM, driver death then `dead_man`;
- a C9 mutation: remove the OFF refusal and the test goes red.

## 4. Owner and bench

**Owner.** Fold H5–H7 into the successor registration that the owner already signs at cap step 10, instead of a separate amendment (A3 §4.4 needs them in "the registration the window runs under"). Draft text:

> **H5.** Every window runs with macOS network time OFF, set by `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off`. The window starts only on exit 0 with the exact output `setUsingNetworkTime: Off`. Arguments, exit status, output, wall and monotonic time and boot id are kept. A capture counts only if its first paired clock reading is at least 600 s after that receipt on both clocks, in the same boot. After the last capture network time is set ON, and that receipt is kept.
> **H6.** As A3 §4.5, with the query taken from at least 3,600 s before OFF to the moment it runs, and the witness older than OFF. A capture recorded `network_time_slew_attested` or `network_time_unattested` is excluded by that named mechanism, which takes precedence over the anchor-replay exclusion.
> **H7.** Each member's network-time state is recorded. The 12 W1/W2 members (ON) and OFF-state members are [combined under rule X | not combined]. The issuer refuses mixed states unless this clause names a rule. The first OFF window's comparison is reported with the first claim-bearing results.

**Bench (lead, no capture running):**
- the real OFF and ON outputs and exits through `sudo -n`;
- A3's old-log test: a real query over a deleted period gives all captures unattested;
- whether `log show --start` accepts an explicit offset (if not, keep local strings and refuse windows that cross a daylight-saving change);
- whether switching OFF or ON writes a marker (A3 §9 says this is not established);
- how often `timed` writes a witness while OFF;
- query latency, to size the timeout;
- a driver-death drill on a throwaway label, confirming `dead_man` sets ON.

## 5. Ways the record could lie, and the refusal for each

- **Log deleted, or queried late:** the witness older than OFF is missing, so every capture is unattested.
- **Time zone:** parse each line's explicit offset. The current parser drops it (`quiet_predicate_campaign.py:535-563`), so do not reuse it. A malformed or ambiguous time on any `timed` line makes the whole window unattested.
- **Continuation lines:** they inherit the parent line's time, and an orphan refuses.
- **Query run early:** rule 4 gives that capture unattested.
- **Header or argv drift:** condition (2) fails, and each consumer checks the argv against the ruled template.
- **OFF reported but not in effect:** markers appear, the capture is slew-attested, and cap K3 returns the question to council.
- **Reboot:** the boot ids differ, so all captures are unattested.
- **Record edited by accident:** the digest chain catches it. Deliberate forgery by the operator is out of scope (D-161).
- **Residual, not refusable by H6:** a new build that corrects the clock without these marker strings. The clock fit and H7 are the only backstop (inference).

Do not wire `scheduler_c4_network_time_on` (`scheduler_gates.py:94`) without these checks behind it; alone it would be cosmetic.
