# Cold gate BFGS-DESIGN-01 addendum 3: Opus contract-lens paired refuter (Opus 5.5)

Refuter: Claude Opus 5.5 (`claude-opus-5-5`), single foreground session, no subagents. Worktree `JouleWise-wt-s0cg-opus-f8d6cab1`, detached at `783a09bec56996f5cdeaa9d4c62c5d9e5246f0ed`, `git status --short` empty at start. Read-only on every repository; scratch in `/tmp/cgref/` only; this file is the only file written.

**Contamination disclosure.** The harness loaded the global `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, the private `CLAUDE.local.md` and the auto-memory index. I opened no memory file, `RUN_STATE.md`, `TASK_QUEUE.md` or decision log. I read the charge and every packet item it names, plus the collector, `pilot_summary`, `BundleReader.metadata`, the ledger's evidence parse and a grep of consumer exception handlers.

**Order of work.** Section A (independent answers) was written to this file at 12:17:56 PDT (file mtime), before the judge's ruling existed: a listing at 12:16:51 showed only `00-charge.md`, and the ruling's mtime is 12:23:12. Section A is unedited since, apart from this sentence. Section B (refutation) was written after the ruling stopped growing (23 759 bytes, stable at 12:24:56).

## A. Independent answers (written before the ruling existed)

### A.0 Executed evidence

All probes ran from the worktree root with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.`.

| # | Probe | Observed |
|---|---|---|
| X1 | Sol reproducer `10-s0-delta/10-sol-repro.py` | `quiet: CustodyFailure -> battery_float_evidence_missing`; `bundle: … -> battery_float_evidence_missing`; `capture: … -> battery_float_evidence_missing`; `deleted rounds.jsonl: CustodyFailure -> pass`. **F1 and F2 reproduced.** |
| X2 | `/tmp/cgref/collector_probe.py`: the real `sample_quiet_predicate_evidence.collect` with an injected clock, round runner and metadata reader, `power=False` | (i) refusal path: journal exists, 0 rows, no `end_stamp`, `round_workers` 0. (ii-a) completed with `duration_s=0` (the loop never runs): **journal exists and is empty**, `end_stamp` present, `round_workers` 0. (ii-b) completed with rounds: journal rows = 1 = `len(round_workers)`, each row's `raw.sha256` names `raw/battery_float.pre.ioreg` (every file directly under `raw/` is digested into every row, `:1201-1203`). (iii) collector raising after the `finally` (reduction failure): `session.json` is the **first** write (no `end_stamp`, `round_workers` 0), and the journal holds the **provisional** row whose `raw` is `{"paths": [], "sha256": {}}` (`new_row`, `:1002`). |
| X3 | Collector source | The refusal path writes `rounds.jsonl` empty at `:1082`. The capture path appends provisional rows at `:1140-1144` and **always** rewrites the journal at `:1205` before the final `session.json` write at `:1208`; `end_stamp` reaches disk only in that final write. Hence *`end_stamp` on disk ⇒ the finalized journal was written before it*. The executor kills a collector that exceeds `envelope_s + 30` (`quiet_predicate_campaign.py:1566-1575`, then `cleanup_groups` SIGTERM→SIGKILL), which leaves shape (iii) on disk. |
| X4 | `/tmp/cgref/helper_probe.py` P1: shape (iii) with the S2 pre record in the first write and one provisional row | **`CustodyFailure`** (`raw/battery_float.pre.ioreg expected b42e…`, observed `None`): the current cross-check treats a provisional row's empty digest map as a recorded digest. |
| X5 | P2: completed, zero rounds, empty journal | `pass ()` |
| X6 | P3: mismatching one-row journal, then truncated to empty | `CustodyFailure -> pass` (F2's twin: truncation instead of deletion). |
| X7 | P4: two rows (one agreeing, one mismatching), then the mismatching row removed | `CustodyFailure -> pass`. |
| X8 | P5/P6: tampered or deleted post raw, then the readable `session.json` has the post `raw_stdout_sha256` nulled, or `battery_float` removed; the journal still records the digest | `CustodyFailure -> battery_float_evidence_missing` (rung (a) fires first; the cross-check `continue`s when the session digest is not 64-hex). |
| X9 | P7/P8: deleted post raw plus `session.json` = `[]`, `null`, `{`, empty, or deleted | `battery_float_evidence_missing` (phase not recorded ×2) in all five. |
| X10 | P9: `session.json` replaced by a symlink to an outside copy | `pass ()`: containers are read following symlinks; only raw files get the C3 no-follow discipline. |
| X11 | P10–P12 bundle: malformed `events.jsonl` alone → `bundle span unavailable`; plus deleted post raw → `CustodyFailure`; `metadata.json='[]'` plus deleted post raw → `evidence_missing`; `events.jsonl` deleted plus deleted post raw → `CustodyFailure`. |
| X12 | `pilot_summary` (`quiet_predicate_campaign.py:1188-1209`) | Reads `session.json` and `rounds.jsonl` itself with plain `json.loads`; a missing or unparseable journal or session is `unreadable` → excluded `incomplete_interior_support` and `continue`, **before** text 6's battery authentication, which text 6 applies to "every readable envelope". The collector's `summarize` (`:1462-1470`) enumerates envelopes by `rglob("rounds.jsonl")`, so an envelope without a journal is invisible to it. |
| X13 | `BundleReader.metadata()` (`bundle_read.py:273-277`) | Raises `BundleReadError` on unparseable or non-object `metadata.json` before any battery step text 8 would add. `grep "except.*BundleReadError"` finds 30 handlers across `whole_window.py`, `analysis_engine/inputs.py`, `window_duration_margins.py`, `reduce.py`, `cli.py`, `bundle_read.py`, `calibration_bracketing.py:2665`; several map it to a per-bundle reason (e.g. `whole_window.py:4230` → `environment_admission_missing`). None catches `RuntimeError`, so `CustodyFailure`/`CustodyUnreadable` propagate through all of them; but `except Exception` / `except BaseException` handlers exist in text-12 consumers (`whole_window.py:3502`, `analysis_engine/inputs.py:1242,1886,2783`, `floor_extraction.py:359,1976`, `scripts/run_campaign.py` ×20+). |
| X14 | Ledger (`calibration_ledger.py:2978-2997, 3043-3049`) | Finalization parses `instrument_evidence.json` (`evidence.get("validation_id")`) and pins its sha256; an unparseable evidence file cannot finalize, and a post-finalization corruption fails text 10's evidence-digest check (`CustodyFailure`) before `authenticate_capture` runs. |
| X15 | S-1 feasibility on base `5d5a0b75` | Closure 39 names; **no** closure name is bound more than once at module scope (so a single-binding requirement is green on base); decorated closure members: `AuthenticatedSlot`, `AuthenticatedVerdict` only; decorated roots: none (roots are already hashed with `inspect.getsource`). So S-1 moves exactly two non-root pins and none of the ten root pins. |
| X16 | S-2 blast radius | `grep -rn "copy\.replace\|from copy import\|__replace__" joulewise scripts` → only `from copy import deepcopy` at `controller.py:60` and `reissue_calibration_acceptance.py:14`. No new allowlist row is needed. |

### A.1 Consumer map: who treats `evidence_missing` as an exclusion (texts 6–12)

| Text | Consumer | Non-pass effect | Custody effect |
|---|---|---|---|
| 6 | `pilot_summary`, `summarize` | whole night blanked (not an exclusion) | propagates, no summary |
| 6 | `pilot_summary` readability pre-check | **exclusion** (`incomplete_interior_support`) of a missing/unparseable session or journal, before the helper runs | not reached |
| 8 | `BundleReader.metadata()` | `BundleReadError`; swallowed into per-bundle reasons by several legacy handlers (X13) | propagates |
| 9 | `reduce(…, battery_evidence)` | whole reduction refused | propagates |
| 10 | `_battery_exclusion_for_observation` | **exclusion** (`continue`), listed under `battery_excluded_endpoints` | propagates; the evidence-digest check runs first (X14) |
| 11 | controller attachment | the attachment is refused | propagates |
| 12 | `bundle_read.authenticate_window_members` | whole set refused | propagates |

So the helper's `evidence_missing` becomes a selection only at text 10, where every container corruption is already preempted by the ledger digest (X14). The two consumer-level exclusions that can swallow a custody-class loss are **text 6's readability pre-check** and **legacy `BundleReadError` handlers** reached outside text 12's gate. Neither is an S0 site.

### A.2 Q1 (F2): a missing `rounds.jsonl`

- **(i) Exact refusal shape** (`error_class == QUIET_REFUSAL_ERROR_CLASS`, no `end_stamp`): the collector always writes an empty journal (X2 (i), X3). Missing → amendment 21 already yields `quiet span unavailable` (`evidence_missing`). Keep. It is not custody: the shape records no digest to lose.
- **(ii) Completed envelope (`end_stamp` present):** the finalized journal is always on disk before `end_stamp` is (X3). Missing → **`CustodyUnreadable("round journal missing")`**. **The magistrate's premise that a completed envelope always has a non-empty journal is false** (X2 (ii-a)): a completed envelope with zero rounds writes an empty journal honestly. The correct binding is the row count, not non-emptiness: `rows` must equal `len(session["round_workers"])` and row *k* must carry `round == session["round_workers"][k]["round"]`; any other count is `CustodyUnreadable("round journal incomplete")`. This also closes X6 (truncation) and X7 (row deletion), which a presence-only rule leaves open. Each finalized row must carry both battery digests (already enforced: a missing key is `observed None` → `CustodyFailure`). If `round_workers` is not a list, the record is structurally malformed → `evidence_missing` (rung (a) class, reason `round inventory missing`); every consumer refuses or blanks on it.
- **(iii) Any other shape** (no `end_stamp`, not the exact refusal shape; X2 (iii), reachable by the executor's timeout kill): span unavailable → `evidence_missing` (amendment 21). **The journal is provisional and must not be used as a digest reference**: today it raises a false `CustodyFailure` (X4), which under text 6 withholds the whole QPE night's summary for one killed collector. Rule: the journal cross-check and the row-count binding apply only when `end_stamp` is present. Whether the provisional journal is still parsed (C1's unreadable-journal custody) is a judgment call; a SIGKILL mid-append can truncate the last line honestly, so I would not make a provisional journal's parse failure custody either.
- **Present but empty for a completed envelope:** acceptable **iff** `round_workers` is empty (X5 is then correct). Not acceptable otherwise.

### A.3 Q2 (F1): an unreadable mandatory container

- **Present but unreadable, non-JSON, duplicate-key or non-object** (`session.json`, `metadata.json`, `instrument_evidence.json`) → **`CustodyUnreadable`**. Reason: coherence. C1 already makes a present-but-unparseable journal custody, and C4 already makes a duplicate-key container custody; a truncated container being `evidence_missing` while a duplicate-key one is custody is not a defensible line. A record that exists but cannot be read is a custody defect of the record store.
- **Absent** container → text 2(a) `evidence_missing` (nothing recorded, no reference digest), with the Q1(ii) exception that a finalized journal proves the session existed only if `session.json` is present, so no extra rule is needed.
- **Readable object with pair fields missing** → text 2(a) `evidence_missing`, unchanged (X8 stays as ruled; every consumer blanks or refuses on it, and at text 10 the ledger digest preempts it).
- **Consumer effect, stated so nobody reads the helper rule as closing the consumer paths:** text 6's own readability pre-check still excludes an unparseable `session.json` before the helper runs (X12); text 8's reader still raises `BundleReadError` for an unparseable `metadata.json` before the helper (X13). The helper rule is therefore effective at text 9's producer, text 10, text 11 and direct callers. Amendment 26 should say that a member whose `metadata()` raises `BundleReadError` is a named refusing member of `WindowBatteryRefusal` (not a skipped member), so the text-12 gate cannot turn an unreadable container into a selection. Honest truncation risk: the collector's `write_json` is a non-atomic `write_text` (`:142-143`), so a kill during the final write can truncate `session.json` honestly; text 6's exclusion is what keeps that from refusing a whole night, and I would keep it.

### A.4 Q3: other members of the class

1. **Journal truncation and row deletion** (X6, X7): same member as F2; closed by the row-count binding in A.2, not by presence alone.
2. **Provisional journal treated as a digest reference** (X4): the inverse direction (a false custody on an honest shape); closed by A.2 (iii).
3. **Container symlinks** (X10): containers are read following symlinks while raw files are not. Not a downgrade of a recorded-digest mismatch, but the same custody discipline C3 imposed on raw files; NIT-level: open containers with the `_raw_bytes` component check.
4. **Journal digest ignored when the session digest is erased** (X8): rung (a) order is ruled (T2); consumers refuse or blank. No change needed; record it.
5. **`events.jsonl` leniency** (X11): safe in the helper (`span unavailable`); the S1 reader must not read a malformed `events.jsonl` as "no obligation" (prior Opus N-9). Forward note for S1.

### A.5 Q4: S-1 and S-2

No conflict with ruled text. S-1 moves only the `AuthenticatedSlot`/`AuthenticatedVerdict` pins and none of the ten roots (X15), consistent with text 3 and amendment 28; the single-binding requirement is green on base. S-2 adds no allowlist rows (X16) and extends text 4's guard in the direction C8 was ruled.

## B. Refutation of the cold ruling (`10-coldgate-fable-ruling.md`, 23 759 bytes)

### B.0 Additional executed evidence

| # | Probe | Observed |
|---|---|---|
| X17 | `/tmp/cgref/count_probe.py`: the real `collect` (injected clock, `power=False`); round 2's sampler leaves a truncated `sampler.json` (`{"marks": {"ps_start": 1.0`), which is what a sampler worker killed mid-write leaves (it rewrites `sampler.json` non-atomically after every tool, `:590, :600`) | `end_stamp` present, `error: JSONDecodeError …`, **journal rows 1, `len(round_workers)` 2**. `session["round_workers"].append` runs at `:1120-1123`; the `sampler.json` parse at `:1124-1137` raises into the outer `except` (`:1146`) before `rows.append` (`:1139`); the `finally` and the final writes still run. An honest completed envelope therefore violates amendment 30's count rule. |
| X4 (repeated) | Shape (iii) with the S2 pre record in the first write and one provisional journal row (`raw.sha256 == {}`) | `CustodyFailure` today. Amendment 30 leaves "the per-row digest cross-check … unchanged and still runs on every row", so this stays `CustodyFailure` after the ruling. |
| X18 | Executor | Every launched collector gets an `envelopes` entry, with `collector_exit = 124` on timeout (`quiet_predicate_campaign.py:1566-1568, 1621-1623`); `cleanup_groups` then SIGTERM→SIGKILLs the collector's group. So shape (iii) with provisional rows (X2 (iii)) is an executor-produced shape, listed, and under amendment 32 authenticated first. |
| X19 | `summarize` enumeration (`scripts/sample_quiet_predicate_evidence.py:1462-1464`) | `paths = sorted(directory.rglob("rounds.jsonl"))`: an envelope whose journal is deleted is never visited. |

### B.1 Per-amendment verdicts

| Amendment | Closes F1/F2 and the class? | Consistent with text 2 order and E1/E12? | Implementable at the named sites? | Counterfactual tests? | Verdict |
|---|---|---|---|---|---|
| 29 (containers) | Yes for F1 (all three kinds) and the symlinked-container member (X10). | Yes: raises precede any status; the rung order inside `authenticate_pair` is untouched; the refusal-shape envelope has a readable `session.json`, so E1/E12 are unaffected. | Yes in `battery_float.py`. At text 8 the reader's `_strict_json` still raises `BundleReadError` first (X13), so the helper rule is not what governs there (see R-5). | Yes (T16-a names each corruption and each kind; RED today). | **Agree**, with R-3 (honest-producer consequences via amendment 32). |
| 30 (journal) | Closes F2, X6 (truncation) and X7 (row deletion). | E1/E12 preserved: the refusal shape has `round_workers == []` and an empty journal (X2 (i)), so the count rule passes it. | **No, as written**: the count witness is wrong (R-1), and shape (iii) keeps a false custody (R-2). | T30-a…h name counterfactuals, but none models the collector's exception path or a provisional journal. | **BLOCKER ×2** (R-1, R-2). |
| 31 (`events.jsonl`) | Closes E5's silent skip and the malformed/missing file in the helper. | Yes: raises before statuses; rung (f) keeps `bundle span unavailable` for a well-formed file lacking the stage events. | Yes in `authenticate_bundle`. The S1 clause covers malformed lines only (R-5). | Yes. | **Agree**, SHOULD-FIX on the S1 clause. |
| 32 (text 6 order) | Closes the consumer-level exclusion (E8). | Text 6's "authenticate before `all_rows.extend`" is kept; E12 is kept (the refusal envelope passes). | `pilot_summary`: yes. `summarize`: **no** (R-4). | T6 (a)/(b) are counterfactual for `pilot_summary`. | **Agree in direction**, with R-2, R-3 and R-4 raising its cost: it converts every false custody below into "no summary for the whole night". |
| Q4 (S-1, S-2) | n/a | No conflict. X15: no closure name is multiply bound on base; only `AuthenticatedSlot`/`AuthenticatedVerdict` pins move; no root pin moves. X16: no allowlist row needed. | Yes. | n/a | **Agree.** |

### B.2 Findings

#### R-1 BLOCKER: amendment 30's count witness, `len(session["round_workers"])`, disagrees with the journal on an honest completed envelope

- **Ruling's premise.** §2: "The collector appends to both lists once per round (`:1123`, `:1140`)"; E6: "`end_stamp` present ⟹ … its row count equals `len(round_workers)`."
- **Executed counter-example (X17).** The two appends are separated by the `sampler.json` parse (`:1124-1137`). Any exception there (truncated `sampler.json` from a sampler killed mid-write, a missing `marks`/`wall_reads` key) is caught by the outer `except`, and the envelope finalizes normally with `end_stamp`, `round_workers` = N+1 and N journal rows.
- **Effect under the ruling.** Amendment 30 raises `CustodyUnreadable("round journal holds 1 rows; session records 2 rounds")` on an unaltered collector output. Amendment 32 then withholds the **whole night's** summary and records a custody failure, which is a false record of tampering. Today this envelope is excluded as `collect_error`. This is the v1.1 blocker-1 / E12 shape: one envelope voids a real night.
- **Exact fix.** S2 (which owns the collector under text 5) writes `session["journal_rows"] = len(rows)` in the final `session.json` write, computed from the same `rows` list that `:1205` writes; amendment 30 binds the count to that field for shapes (i) and (ii). The refusal path writes `journal_rows: 0`. Amendment 30 applies only to envelopes carrying `battery_float`, which are all S2-era, so no historical envelope lacks the field. Alternative, if the lead prefers no new field: S2 moves the `round_workers.append` after `rows.append`. That is weaker, because any future edit between the two re-opens the defect.
- **Test.** The X17 shape through the real `collect` (injected clock and runner) passes `authenticate_quiet_session` with `pass`, or with the pair's own status; the same envelope with one journal row deleted raises `CustodyUnreadable`.

#### R-2 BLOCKER: shape (iii) with a provisional journal is a false `CustodyFailure`, contrary to the ruling's own table

- **Ruling text.** The table says shape (iii) is `evidence_missing: quiet span unavailable` and "cannot be `pass`". Amendment 30 says "In shape (iii) a missing journal is zero rows … The per-row digest cross-check is unchanged and still runs on every row". T30-f tests only an **absent** journal.
- **Executed (X2 (iii), X4, X18).** A collector killed or crashed after at least one round leaves `session.json` from the first write (with the S2 pre record, per text 5) and journal rows written by the provisional append (`:1140-1144`), whose `raw` is `{"paths": [], "sha256": {}}` (`new_row`, `:1002`). The cross-check reads `observed = None` against the pre's recorded digest and raises `CustodyFailure`. The executor produces this shape by design: a collector over `envelope_s + 30` gets `collector_exit = 124` and a SIGKILL (for example, a hung `recorder.finish()`, which the collector's own "power cleanup escalated" branch anticipates).
- **Effect under the ruling.** Amendment 32 authenticates every listed envelope first, so one timed-out collector means no summary for the night and a custody record that falsely implies altered bytes. Provisional rows record no digest, so there is no digest to disagree with. This is not custody under text 2(b)'s own definition.
- **Exact fix (amendment 30, shape (iii) sentence).** "In shape (iii) the journal is provisional: neither the count rule nor the per-row digest cross-check applies, and the verdict is `evidence_missing` at the span rung." Recommended in addition: a provisional journal's parse failure is not custody either. The append is a single `write`, and a SIGKILL during it can leave a truncated last line honestly. The residual downgrade (strip `end_stamp` to reach shape (iii)) yields a non-pass, which blanks the night under text 6, so no number escapes.
- **Tests.** X4's shape gives `evidence_missing` with reasons exactly `("quiet span unavailable",)` (RED today: `CustodyFailure`). The same shape with the pre raw deleted still raises `CustodyFailure`, from rung (b) and not from the journal.

#### R-3 SHOULD-FIX: amendments 29 and 32 together turn two honest collector artefacts into whole-night custody refusals

1. **Non-atomic final write.**
   - `write_json` is a plain `write_text` (`:142-143`; the ruling's own E6 notes this).
   - A kill during the final `session.json` write (`:1208`) leaves a truncated file.
   - Under amendment 29 that is `CustodyUnreadable`, and under amendment 32 the night gets no summary.
   - The window is narrow but real on the executor's timeout path.
   - **Fix:** S2 makes the collector's `session.json` writes and the final journal write atomic (temp file, `fsync`, `os.replace`, as `record_attestation` already does at `quiet_predicate_campaign.py:806`). After that, a present-but-unparseable file can no longer be an honest output, and amendment 29's premise holds.
2. **Startup crash before the first write.**
   - The executor lists every launched collector (X18).
   - A collector that dies before `:1081`/`:1084` writes no `session.json`. Under amendment 29 ("absent … is `CustodyUnreadable`") and amendment 32, that also means no summary for the night.
   - **Fix:** amendment 32 treats an envelope directory holding **no** collector output (no `session.json`, no `rounds.jsonl`, no `raw/battery_float.*`) as excluded `collect_error`, as today, because nothing was recorded whose custody could be lost. Any partial output keeps amendment 29's raise.
   - This differs from my A.3, where I would have left an absent container as text 2(a). The judge's "absent is custody" is defensible once the no-output carve-out exists.

#### R-4 SHOULD-FIX: amendment 32 is not implementable as written at `summarize`

- Amendment 32 binds "`pilot_summary` and `summarize`, for every envelope directory the executor lists". `summarize` has no executor list. It enumerates envelopes by `rglob("rounds.jsonl")` (X19), so T6 (b)'s deleted journal makes the envelope invisible there, which is an exclusion by omission.
- **Fix:** `summarize` enumerates envelope directories by `session.json` (or by the `envelope-*` directories), calls `authenticate_quiet_session` on each, and then reads the journals.
- **Test:** the T6 (b) shape through `summarize` raises.

#### R-5 SHOULD-FIX (S1 brief): the idiom the ruling names still has two homes on the bundle side

- **First home: `BundleReader.events()`.** It treats a **missing** `events.jsonl` as `[]` (the ruling's E9). Texts 7, 8 and 12 decide `not_reached` (no obligation) from that list.
  - Amendment 31's S1 clause covers only a `BundleReadError` from malformed lines, so a deleted `events.jsonl` still reads as "no `idle_baseline` start" at the reader. That is exactly the "`if path.exists(): … else: zero`" idiom that §4 names as the class.
  - **Fix sentence for S1:** "a bundle whose `metadata.json` carries a `battery_float` key and whose `events.jsonl` is missing is `BundleReadError`, never `not_reached`"; T8 gains that row.
- **Second home: the text-12 gate.** §3 asserts that bundles are "never excluded", but amendment 26 does not say what `authenticate_window_members` does with a member whose `metadata()` raises `BundleReadError`, for example an unparseable `metadata.json`, which the reader rejects before the helper runs (X13).
  - Thirty legacy `except … BundleReadError` handlers map that exception to per-bundle reasons.
  - **Fix sentence for amendment 26:** "a member whose classification raises `BundleReadError` is listed in `WindowBatteryRefusal`; the error is never propagated to a caller's `BundleReadError` handler."

#### R-6 NIT

1. **Journal row identity.** The count rule does not bind each row to its round. Rows could be reordered or duplicated at a constant count. The battery digests are identical across rows (every row digests every file directly under `raw/`), so this cannot mask a battery mismatch. **Optional fix:** row *k* has `round == k`.
2. **Historical-key escape.** Amendment 30's "no `battery_float` key → `evidence_missing`, amendment does not apply" allows a completed S2 envelope with the key deleted to skip the journal check. The result is a non-pass, which blanks the night (text 6), so no number escapes. Record it and do not change it.
3. **Broad handlers in text-12 consumers.** `except Exception` / `except BaseException` handlers exist in those consumers (`whole_window.py:3502`, `analysis_engine/inputs.py:1242, 1886, 2783`, `floor_extraction.py:359, 1976`, `scripts/run_campaign.py`, 20 or more). Their comments say they refuse. S1's text-12 refuter should confirm that none wraps the window gate in a way that turns `CustodyFailure` into a per-member reason.

### B.3 Agreement and disagreement per question

- **Q1: partial agreement.**
  - **Agree** with custody for a missing journal in shapes (i) and (ii), with rejecting "a completed envelope's journal is always non-empty" (my X2 (ii-a) and the judge's T30-c agree), and with a count binding rather than presence alone (I reached the same rule independently, A.2).
  - **Disagree** with the witness (`round_workers`, R-1) and with keeping the per-row cross-check in shape (iii) (R-2). Both are BLOCKERs because amendment 32 turns each into a whole-night false custody record.
- **Q2: agree** that present-but-unreadable, non-object, duplicate-key or symlinked containers are `CustodyUnreadable` (my A.3 reached the same result). On absent containers I defer to the judge, provided R-3's no-output carve-out and atomic writes are adopted.
- **Q3: agree** with "same signature: yes", and with both new members (E2 and E5), each of which I also reproduced or observed independently (X6, X7, X11). The sweep misses the reverse-direction member (R-2), the reader-side missing-events member (R-5) and the `summarize` enumeration (R-4).
- **Q4: agree** (X15, X16).

### B.4 What the next fix round's brief should carry, in addition to the ruling

1. R-1: the `journal_rows` witness, S2, plus the S0 count rule reading it.
2. R-2: the shape-(iii) sentence, plus the X4 test.
3. R-3: atomic collector writes (S2) and the no-output carve-out in amendment 32.
4. R-4: `summarize` enumeration.
5. R-5: the two S1 sentences.

Items 1–2 change ruled text (amendment 30). Under rule 11, the magistrate returns them to the cold judge as an addendum-3 erratum; they are not fixes the lead can make at the bench.
