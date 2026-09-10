# Opus contract-lens refutation — cold-gate ruling 35 (row-9 waiver, PR #314 @ `beb808bc`)

**Summary.** The disposition is right: option (a) survives every probe I could run, and I added a fourth reproduction — the failing test fails **alone at the PR head itself** (`beb808bc`, 07:41:56–07:42:32 PDT, 36.297 s, line 1675, the same two strict reasons). But the ruling's central independence argument is **wrong as written**, in the same defect class refuter 57 R1 named: "the PR changes no byte the failing test executes" is false, and the verbatim ledger row that W3 makes mandatory contains two refutable claims (`cooldown_gate` "a function with one caller"; the diff intersects the failing path "in ONE file"). The true independence argument is stronger and available from evidence already in the packet. W7's standing bar on future waivers exceeds a packet ruling and contradicts the symmetry of 44 C4 / 56 Q2. One condition is missing (no machine census for the replay window itself), and one reproduction (the lead's 05:05 run) has no primary artifact anywhere in the record.

## Findings

| id | severity | claim | evidence |
|---|---|---|---|
| R1 | should_fix | Ledger row says `cooldown_gate` is "a function with one caller, … `controller.py:3072`". There are **two** production call sites. | `grep -n cooldown_gate joulewise/*.py scripts/*.py` → `controller.py:2464` def, `controller.py:3072`, **`scripts/run_campaign.py:4149` import + `:4174` call** (thermal-recovery note). Conclusion survives: `tests/test_controller.py` never imports `run_campaign` (grep empty). |
| R2 | blocker (text, not merge) | Reason 3's "the PR changes no byte the failing test executes" and the row's "intersects the failing path … in ONE file" are false. `joulewise/environment_admission.py` is changed **and executed** by the failing test. | `cli._strict_problems` → `reduce_bundle` → `reduce.py:711` calls `current_environment_refusals` under strict for non-mock telemetry; the PR edits exactly that function (`environment_admission.py` +5/−3). Failing path also includes `reduce.py`, omitted from the row's enumerated set. |
| R3 | cleared (R2's conclusion) | The change cannot cause or mask the two `idle_drift` messages. | It is a monotone widening 1e-9 → `ADMISSION_TIME_ROUNDING_S` = 1e-6 at three comparisons that only ever **withdraw** the reason `environment_admission_missing`; the two failing messages are emitted at `cli.py:1408/1416`, byte-identical to main. Independently: seat 08 F2 reproduced the failure with `environment_admission.py` restored to base bytes, and `git diff --stat ee25c47f..078a13a4 -- joulewise scripts tests` is **empty**, so seat 08's "HEAD bytes" *are* main `078a13a4`'s bytes. The ruling never used this — its own best evidence. |
| R4 | should_fix | W7's second sentence ("NO further row-9 waiver is available for this test name on any PR until that lane lands") binds future cold gates. A packet ruling may not. | Rule 11: the cold gate rules on a mechanically-assembled packet. 44 C4 forbids precedent; 56 Q2 + 57 refused a *general clause* on exactly that ground — a standing prohibition is as much a general rule as a standing permission. It is also redundant: 44 C4 already makes any future rc≠0 replay its own mandatory trigger. |
| R5 | should_fix | Missing condition: nothing records the machine state during the replay window, though host timing is the whole causal account. | W4 qualifies the three reproductions "machine census not recorded" but no condition covers 05:52:48–07:31:40. An unrecorded host is *the* qualification of this waiver. |
| R6 | should_fix | "Fails on clean main 078a13a4 (lead, 05:05, 73 tests, failures=1)" has **no primary artifact** in the packet. | Exhibit C is a lead note with no tail. Exhibit B **F1**: "Both targeted unittest invocations stopped in setUp because the read-only sandbox cannot create a temporary directory" — record 19 never reached the test body. No verbatim clean-main tail exists anywhere on the record. |
| R7 | nit | "the four changed modules restored to HEAD bytes (seat 08)" mis-names the set. | Seat 08 pathspec/F2: `environment_admission.py`, `reduce.py`, `controller.py`, `load_transition_alignment.py`. `reduce.py` is **not** changed by the final PR (R2 blocked by D-138, seat-08 F1), and `scripts/generate_g2a_probe_inputs.py` was not in the set. Conservative superset → conclusion unaffected; the row should name them. |
| R8 | nit | Reason 6 states as fact that a four-shard run "cannot make the failure go away". That is a prediction about a timing-dependent test. | Immaterial to the decision, but it should be recorded as reasoning. The verified fact is stronger: the test fails **alone**, in ~36 s, at both `58d4696b` and `beb808bc`. |
| R9 | cleared | Every checkable number in the verbatim sentences. | See Q4 table below. |
| R10 | nit | "on a loaded host the capture times out" (exhibit A / reason 4 framing). | It also times out **unloaded** — two alone-in-process runs, 36.8 s and 36.3 s. The ledger's own wording ("on a slow host") is the correct one; keep it and do not import "loaded". |

## Q1 — Reachability

All three `controller.py` hunks are inside `cooldown_gate`: `@@ -2516` (`coverage_rounding_s = 0.0`), `@@ -2523` (`+= math.ulp(evidence_end) + math.ulp(clipped_start)`), `@@ -2552` (span slack 1e-9 → 1e-6; `coverage_slack_s = max(1e-6, coverage_rounding_s + math.ulp(coverage_s))`). Def at `:2464`; `+9/−2`. **Confirmed.** Two callers, not one (R1). The failing test is a `HappyPathTests` single-run case; it configures no cooldown policy, `grep -c cooldown_gate tests/test_controller.py` = 0, and it does not import `run_campaign`. **Unreachable — upheld.**

`powermetrics.py`, `uncertainty_evidence.py`, `cli.py` (and `reduce.py`): `git diff 078a13a4..beb808bc --stat` over those paths is **empty**. **Confirmed byte-identical.**

`environment_admission.py` (R1 repair) **is** on the failing path — that is my one substantive refutation. `validate_bundle(strict=True)` → `_strict_problems` → `reduce_bundle` → `reduce.py:711` `current_environment_refusals(...)`, guarded only by `strict and telemetry_source != "mock" and bundle_path and measured_window`; the test drives a real `PowermetricsTelemetryAdapter` subclass and asserts a powermetrics `--samplers` command line, so the branch is taken. It cannot **produce** the two messages (different emitter, `cli.py:1408/1416`) and cannot **mask** anything relevant, because the direction of the change is monotone-permissive on one reason name that is not in the failure list — and because the failure reproduces with those bytes reverted to main's. The ruling reached the right answer by an argument that a two-line grep refutes.

## Q2 — The three reproductions

- **Lead on clean main `078a13a4` @ 05:05** — asserted only in exhibit C. No tail, no log. Exhibit B F1 shows record 19's own invocations died in `setUp`. **Not corroborated by a primary artifact.**
- **Seat 08 with restored bytes** — real, quoted verbatim: *"test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce fails on idle_drift and idle_drift_bound_w reconstruction. Replaying it with all four production modules restored to original HEAD reproduced the same failure; the issued-pin test passed on that baseline."* (`08-gate-repairs-r1-r4-astra-report.md`, flag F2, `level: nonblocking`.) Seat head `190e11b6`, base `ee25c47f`; `ee25c47f` is **not** an ancestor of `078a13a4`, but their `joulewise/ scripts/ tests/` trees are identical, so "HEAD bytes" = main bytes. Stronger than the ruling claimed.
- **Cold judge on `58d4696b`** — its byte-identity premise verifies exactly: `git diff --name-only 58d4696b..beb808bc` = `docs/contracts/measurement_methodology.md` **only**. Rounds 3–6 were prose-only.
- **New (mine): head `beb808bc` directly**, 36.297 s, line 1675, both reasons. This retires the byte-identity argument entirely.

## Q3 — Conditions W1–W8

Enforceable and sound: W1, W2, W3 (as amended), W5, W8. W6 is sound but over-broad in prose ("no second full replay … to see if it goes green") — it forbids the cheap module-level re-run that W7's own addendum later mandates; read it as scoped to *full-suite* replays. W7: first sentence binds fine as a magistrate obligation of **this** waiver; second sentence does not bind and must be re-shaped (R4). Missing: the replay-window census (R5). Contradiction with precedent: none in the disposition; the "no precedent" clause is correctly carried, but W7 quietly violates its spirit in the restrictive direction.

## Q4 — The verbatim sentences, fact by fact

| fact | status |
|---|---|
| line `tests/test_controller.py:1675` = `self.assertEqual(validate_bundle(bundle_path, strict=True), [])` | verified |
| hunks at `:2516`, `:2523`, `:2552`; `cooldown_gate` def `:2464`; `controller.py` +9/−2 | verified |
| caller `controller.py:3072` | verified — but **not the only one** (R1) |
| `powermetrics.py` / `uncertainty_evidence.py` / `cli.py` / `reduce.py` byte-identical to main | verified |
| `078a13a4` is an ancestor of `beb808bc` | verified |
| Actions run **34479219008**, exactly 18 pass rows across 3.11/3.14 and eight shards; `gate-ledger` red in a **different** run, 34479219037 | verified against exhibit E (row count = 18) |
| main `078a13a4` CI success `2026-09-10T11:14:03Z` | verified against exhibit F (a timestamp, not a run id — W5 calls it "run") |
| that those 18 checks are at head `beb808bc` | **unverified in session** (no `gh` in my charge; exhibit E asserts it) |
| `Ran 5668 tests in 5930.030s` / `FAILED (failures=1, skipped=109)` / `rc=1`, 05:52:48–07:31:40 | **unverified in session** (1 h 39 min; exhibit A is the only witness). Wall arithmetic is consistent: 5932 s elapsed vs 5930.030 s reported. |
| lead's 05:05 main run, 73 tests | **unverified anywhere** (R6) |
| "`--no-sleep` control agrees exactly"; timeout `powermetrics.py:1468–1470` = 17.5 s | consistent with exhibit B ll. 146–195 |

## Q5 — Economics against option (b)

Sound in outcome, loose in argument. Your hypothesis — fewer concurrent processes could reduce load — is already falsified empirically: the test fails **alone, in-process, in ~36 s**, twice, at two heads. The minimum-load configuration has been run and it fails, so "a serial single-module run alone might pass" is refuted, not merely improbable. The four-shard runner adds four concurrent workers, i.e. strictly more load. And for row 9's *purpose*: 44 C1's accepted tail was itself a `WORKERS SUMMARY shards=4` — the shard runner is the **weaker** instrument, so option (b) would substitute a partial run for the unpiped single-process run row 9 actually asks for. That is backwards. The only defect is presenting a prediction ("cannot make the failure go away") where a measurement exists.

## Verdict — **UPHOLD WITH AMENDMENTS**

Option (a), merge at `beb808bc` under the named waiver, is upheld. Four amendments, exact text:

**A1 — replace the independence clause in the ledger row** (from "Independence from this PR, shown by reachability:" to "…byte-identical to main."):

> Independence from this PR, shown by reachability: the failing test executes `tests/test_controller.py`, `joulewise/adapters/powermetrics.py`, `joulewise/uncertainty_evidence.py`, `joulewise/cli.py`, `joulewise/reduce.py`, `joulewise/controller.py` and `joulewise/environment_admission.py`; of these the PR changes TWO — `joulewise/controller.py` (+9/−2) and `joulewise/environment_admission.py` (+5/−3) — and neither can bear on the failing assertion. (i) The three `controller.py` hunks all sit inside `cooldown_gate` (def `:2464`; hunks `:2516`, `:2523`, `:2552`), which has two call sites, `controller.py:3072` (between-member campaign cooldown) and `scripts/run_campaign.py:4174` (imported `:4149`, thermal-recovery note); the failing test is a single-run `HappyPathTests` case that drives neither — it configures no cooldown, never imports `run_campaign`, and `grep -c cooldown_gate tests/test_controller.py` = 0. (ii) The `environment_admission.py` change IS executed (strict validation reaches `current_environment_refusals` via `reduce.py:711`) but is a monotone widening of one tolerance, 1e-9 → `ADMISSION_TIME_ROUNDING_S` = 1e-6, at three comparisons that can only ever WITHDRAW the reason `environment_admission_missing`; it cannot emit either `idle_drift` reason, and seat 08 reproduced the failure with `environment_admission.py`, `controller.py`, `load_transition_alignment.py` and `reduce.py` restored to base bytes (`git diff --stat ee25c47f..078a13a4 -- joulewise scripts tests` is empty, so those base bytes are main's). The capture, salvage and strict-validation code that emits the two reasons (`powermetrics.py`, `uncertainty_evidence.py`, `cli.py:1408/1416`, `reduce.py`) is byte-identical to main.

**A2 — replace the reproduction clause** (W4 and the row):

> Pre-existing on the merge base in the same machine state: fails on clean main `078a13a4` (lead, 05:05 PDT, 73 tests, failures=1 — asserted in the record-19 lead note, tail NOT captured; record 19's own targeted invocations never reached the test body, F1), with `environment_admission.py`, `controller.py`, `load_transition_alignment.py` and `reduce.py` restored to base bytes (seat 08 F2), on `58d4696b` whose `joulewise/` tree is byte-identical to `beb808bc` (cold judge 35, 07:33 PDT, 36.840 s), and at head `beb808bc` itself (Opus refuter 36, 07:41:56–07:42:32 PDT, 36.297 s, same line 1675, same two reasons, unittest FAILED); all alone in-process, machine census not recorded.

**A3 — W7 re-shaped:**

> **W7 (amended).** Addendum obligation, written into the row at merge time: when FIXTURE-SENTINEL-CONTROLLER-01 lands, the magistrate runs `python3 -m unittest tests.test_controller` alone on then-current main and records the tail; if it is not `OK`, the failure is an open defect on main with its own lane, the merge stands, and the record says so. The next PR whose replay shows this test name does NOT inherit this disposition — it is a fresh mandatory cold-gate trigger under 44 C4 — and this ruling RECOMMENDS that the next cold gate refuse a further waiver absent the cure. A standing bar on future waivers is a process rule, is NOT ruled here, and may be adopted only by the magistrate, on the record and visibly to Ed.

**A4 — new condition:**

> **W9.** The row records what is known of the machine state during the replay window 05:52:48–07:31:40 PDT (power source, power mode, concurrent agent or background load, whether any interactive session was live), or states in those words that no census was taken. The waiver's causal account is host timing; the unrecorded host is its qualification and is written down, not left implicit.

**Terminal-review line** — replace "is unreachable from the PR's only controller hunks (all inside `cooldown_gate`)" with: "and is unaffected by both production changes the PR makes on its path — the three `controller.py` hunks sit inside `cooldown_gate`, which the test never reaches, and the `environment_admission.py` tolerance widening can only withdraw an admission refusal, never emit an `idle_drift` reason".

Nothing was fixed, edited, or committed; the only write was the permitted test's own temp directory.
