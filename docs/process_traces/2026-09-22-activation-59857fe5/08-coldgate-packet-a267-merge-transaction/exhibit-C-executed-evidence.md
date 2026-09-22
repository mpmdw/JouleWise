# Exhibit C — executed evidence (generator output, verbatim)

Generated 2026-09-22 11:14:33 PDT against repository `/Users/edr/code/JouleWise-wt-mag-59857fe5`. Revisions: feature head `489b0953`, scratch `447fd6bf..e52c7fbc`, main `c8812172`. Everything in C1–C5 was executed by this generator; C6 is quoted, not re-run.

## C1 — the four D-138 governed estimator files at the FINAL feature head vs the r7 candidate's pins

Re-executes record 01 step 8 at `489b0953` (the step was executed at `c5f4f9c6`, before the fix round's 15 commits). `pinned` is read out of the r7 artifact at `e52c7fbc`; `observed` is `sha256(git show 489b0953:<path>)`.

```
r7 acceptance_id: d079_calibration_acceptance_v2_n17_r7
r6 acceptance_id: d079_calibration_acceptance_v2_n17_r6
MATCH     joulewise/adapters/powermetrics.py
          pinned   70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4  (unchanged r6->r7)
          observed 70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4
MATCH     joulewise/powermetrics_fiducial.py
          pinned   386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92  (unchanged r6->r7)
          observed 386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92
MATCH     joulewise/reduce.py
          pinned   7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc  (unchanged r6->r7)
          observed 7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc
MATCH     joulewise/uncertainty_evidence.py
          pinned   b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8  (moved r6->r7)
          observed b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8
```

## C2 — derivation-digest recomputation through the production helper

Imported `joulewise.calibration_bracketing` from `/Users/edr/code/JouleWise-wt-mag-59857fe5/joulewise/calibration_bracketing.py` (sha256 `4a901778e5c0ae1f46cddc8f8d8551b340f67c520a33aba718752d74acd9271b`). The core is every key except `derivation_sha256`, exactly as the production validator builds it (`calibration_bracketing.py:680`).

```
r6: stored      18d09aa9d4accb16a8dff770de85cd7e7525bdb0b6e68f1de716e20fb8a9b9f3
r6: recomputed  18d09aa9d4accb16a8dff770de85cd7e7525bdb0b6e68f1de716e20fb8a9b9f3   MATCH
r7: stored      03d10ab282ad4c0929db86a299463c83b4255255369db7d5b85b83adfb12b9e4
r7: recomputed  03d10ab282ad4c0929db86a299463c83b4255255369db7d5b85b83adfb12b9e4   MATCH
```

## C3 — the header guard at `489b0953` over the three saved log bodies

The four definitions below are extracted by `ast` from `git show 489b0953:joulewise/quiet_predicate_campaign.py` and executed as-is; nothing else from the module is loaded.

```python
# joulewise/quiet_predicate_campaign.py:450-450 at 489b0953
TIMED_LOG_HEADER_FIELDS = ("Timestamp", "Process")

# joulewise/quiet_predicate_campaign.py:52-52 at 489b0953
TIMED_LOG_MARKERS = ("cmd,apply,src,", "ntp_adjtime", "settimeofday")

# joulewise/quiet_predicate_campaign.py:453-456 at 489b0953
def timed_log_has_header(text):
    """Did this body come from a ``log show`` that actually produced output?"""
    first = text.splitlines()[0] if text else ""
    return all(field in first for field in TIMED_LOG_HEADER_FIELDS)

# joulewise/quiet_predicate_campaign.py:475-478 at 489b0953
def timed_log_marker_lines(text):
    """Raw count of log lines carrying any applied-correction marker."""
    return sum(any(marker in line for marker in TIMED_LOG_MARKERS)
               for line in text.splitlines())
```

```
exhibit D (fixture, compact style)
  path      tests/fixtures/qpe01_pilot_n1_20260922/exhibit-D-timed-log.txt
  sha256    70218c4a41b0ee87e20f032790e442451f36d713df49933ccbaba907395797b6
  bytes     34705   lines 191
  line[0]   'Timestamp               Ty Process[PID:TID]'
  timed_log_has_header(text)   = True
  timed_log_marker_lines(text) = 30
  line[0].rstrip() == proposed syslog header constant: False
exhibit D2 (live syslog, 02:10-04:35 window)
  path      docs/process_traces/2026-09-22-activation-59857fe5/07c-exhibit-D2-timed-log-0210-0435-syslog.txt
  sha256    dba7fb7cb92e9179a8e4d09e40290b578bbd68d12f29bb42eb417abcf6a4eb63
  bytes     36434   lines 191
  line[0]   'Timestamp                       (process)[PID]    '
  timed_log_has_header(text)   = False
  timed_log_marker_lines(text) = 30
  line[0].rstrip() == proposed syslog header constant: True
exhibit D3 (live syslog, zero-match)
  path      docs/process_traces/2026-09-22-activation-59857fe5/07c-exhibit-D3-timed-log-zero-match-syslog.txt
  sha256    da1b28eff7848fc42698579387fb9881a2bd1ceda8151ba16617a3b63550718b
  bytes     51   lines 1
  line[0]   'Timestamp                       (process)[PID]    '
  timed_log_has_header(text)   = False
  timed_log_marker_lines(text) = 0
  line[0].rstrip() == proposed syslog header constant: True
```

### C3b — the lead's proposed Q2 guard evaluated over the same corpus

Proposed guard (lead's Q2 option (a)): the body's first line, right-stripped, equals the frozen constant `'Timestamp                       (process)[PID]'`. Evaluated here against the three saved bodies and against the four counterfactual bodies the lead's regression names. `entry line` is taken mechanically as exhibit D2's SECOND line, so it is a real headerless body, not a hand-written one.

```
True   proposed_guard  | False  guard at 489b0953  | D2 full body (live syslog, non-empty)
True   proposed_guard  | False  guard at 489b0953  | D3 full body (live syslog, zero match, header only)
False  proposed_guard  | True   guard at 489b0953  | D full body (compact-style fixture)
False  proposed_guard  | False  guard at 489b0953  | empty body
False  proposed_guard  | False  guard at 489b0953  | html error page
False  proposed_guard  | False  guard at 489b0953  | bare newline
False  proposed_guard  | False  guard at 489b0953  | headerless entry line (D2 line 2 onward)
False  proposed_guard  | True   guard at 489b0953  | compact header line alone
```

## C4 — revision topology and the scratch/feature path-overlap check

```
feature head                489b0953754da5abe41dc9e42ac04788293c4ff9
scratch head                e52c7fbcdb88a82f97951a472564aded2b282523
scratch base / feature base 447fd6bf915c75bdb58c3a15bf1c12ee2499ead0
main                        c8812172470a07ea9d3d5b3fd7f8c7033e221c9f
447fd6bf is ancestor of 489b0953: True
447fd6bf is ancestor of e52c7fbc: True

feature delta 447fd6bf..489b0953: 9 paths
  F  configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v2.json
  F  joulewise/night_gate.py
  F  joulewise/quiet_predicate_campaign.py
  F  scripts/run_night.py
  F  scripts/sample_quiet_predicate_evidence.py
  F  tests/test_night_gate.py
  F  tests/test_quiet_predicate_campaign.py
  F  tests/test_sample_quiet_predicate_evidence.py
  F  tests/test_uncertainty_evidence.py
scratch delta 447fd6bf..e52c7fbc: 10 paths
  S  configs/calibration/calibration_acceptance_d079_v2_n17_r7.json
  S  joulewise/arm_readiness.py
  S  joulewise/calibration_bracketing.py
  S  scripts/epoch_equivalence_check.py
  S  scripts/floor_mint_pinsets/schema_v2.json
  S  tests/test_calibration_bracketing.py
  S  tests/test_calibration_exits.py
  S  tests/test_capture_pipeline_era.py
  S  tests/test_powermetrics_fiducial.py
  S  tests/verify_calibration_acceptance_corpus.py

intersection: EMPTY
```

## C5 — the r7 candidate's registry pin vs its own bytes

The scratch head registers r7 in `ISSUED_ACCEPTANCE_REGISTRY` with a `file_sha256`. That pin is compared here against the artifact's bytes at the same revision.

```
ANCHOR_V3_R7_ACCEPTANCE_BOUND_SHA256 = 14c891eb94a72cb53552cc66f4f8b96ee3bad472a3c606afb7b0647175b56195
sha256(git show e52c7fbc:configs/calibration/calibration_acceptance_d079_v2_n17_r7.json)  = 14c891eb94a72cb53552cc66f4f8b96ee3bad472a3c606afb7b0647175b56195
verdict: MATCH
r6 bytes sha256                        = 0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d
```

## C6 — expensive runs: NOT re-executed, quoted verbatim from record 01

Each block below is a verbatim quotation from `docs/process_traces/2026-09-22-activation-59857fe5/01-launch-and-resume-record.md` at the bookkeeping head, labelled with the step that executed it. The generator does not re-run these.

**record 01 step 9, magistrate-executed — neutrality proof part 1 (`tests/verify_calibration_acceptance_corpus.py`)**

> r7 → `n=17 min=0.02317490442656863 (20260722T215127-eeef661a) max=0.03289849371536248 (20260722T214220-1acdbbc0) range=0.00972358928879385 mean=0.026848579671140323 sample_sd=0.002460856207694636 … PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK`; r6 under the same command prints the identical five statistics and `OK`.

**record 01 step 11, magistrate-executed — the six D-138-affected calibration modules on the scratch branch**

> `Ran 349 tests in 546.361s OK (skipped=5)`

**record 01 step 12, magistrate-executed — quick tier on the scratch head `e52c7fbc`**

> `modules=153 excluded=92 failures=0 seconds=72.139 result=PASS`

**record 01 step 18, magistrate-executed — corpus replay at `62412ee6` vs `corpus-v3-baseline-9b6b3f0e.json` (38 members)**

> **EQUAL 38, DIFF 0, NOT_EXECUTED 0** (v3 dict AND raw sha256 equal per member)

**record 01 step 14, seat-executed and magistrate-verified — the three brief-06 modules at the fix head**

> `Ran 224 tests in 55.218s OK` (177 before)

**record 01 step 22, magistrate-executed — the full seven-module exit-contract run at `62412ee6`, INCLUDING its one failure**

> `Ran 616 tests in 884.637s FAILED (failures=1)` — `tests.test_run_night.WindowDeadlineTests.test_a_grandchild_that_ignores_sigterm_is_killed_and_still_proven`. The record classifies it a contention flake rather than a delta defect: the three files it exercises are untouched by the fix round, the test alone re-ran `Ran 1 test in 7.340s OK`, and the whole module alone `Ran 228 tests in 108.994s OK`. The seat's own run of the same four modules was `Ran 392 tests in 742.268s OK` and the `c5f4f9c6` baseline `569 OK`.

**record 01 step 20, execution-lens-executed — byte invariance of a no-failure night between `c5f4f9c6` and `62412ee6`**

> `evidence_outcome.json`: zero differences; the only differences anywhere are the two additive keys (`network_time_attestation_wall_s`, `window_argv_epoch_s`) plus `summary.whole_campaign_observer_cpu_s`, which is the measured CPU of the test process.

Note on scope: steps 14, 18 and 20 were executed at `62412ee6`. The feature head `489b0953` is one further commit whose entire diff is inside the `record_attestation` docstring (record 01 step 19). The generator does not re-run them; the diff `62412ee6..489b0953` is printed here so the judge can size that gap itself.

```diff
diff --git a/joulewise/quiet_predicate_campaign.py b/joulewise/quiet_predicate_campaign.py
index 00833763..4b42760d 100644
--- a/joulewise/quiet_predicate_campaign.py
+++ b/joulewise/quiet_predicate_campaign.py
@@ -675,13 +675,13 @@ def record_attestation(out, attestation):
     The collector has exited, so the chain owns this write; temp plus rename
     means a reader never sees a half-written session record, and a write that
     cannot land is reported in the attestation rather than raised (an
-    unwritable envelope directory used to refuse the whole night from here).  The attestation
-    carries ``session_sha256_before`` -- the digest of the file this rewrite
-    replaced -- so the one edit made after the collector exits is auditable
-    from the record itself (A269 ruling 10 Q4 iii).  Nothing else rewrites
-    ``session.json`` after the collector exits: under cure 2 there is no
-    finaliser pass, so this digest can only ever name the collector's own
-    bytes.
+    unwritable envelope directory used to refuse the whole night from here).
+    The attestation carries ``session_sha256_before`` -- the digest of the
+    file this rewrite replaced -- so the one edit made after the collector
+    exits is auditable from the record itself (A269 ruling 10 Q4 iii).
+    Nothing else rewrites ``session.json`` after the collector exits:
+    under cure 2 there is no finaliser pass, so this digest can only ever
+    name the collector's own bytes.
     """
 
     path = out / "session.json"
```
