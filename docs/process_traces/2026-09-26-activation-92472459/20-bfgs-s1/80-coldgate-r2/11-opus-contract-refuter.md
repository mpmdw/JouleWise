# Cold gate BFGS-S1-R2-01: paired Opus contract-lens refuter

Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), contract lens, paired with the cold Fable judge. One foreground session; no subagents, no background tasks. I did not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, the decision log, or memory or skill files. I edited no repository file. Every probe ran in a shared clone `/tmp/oc2/head` checked out at `49d77c74` (the charge's head), not in any `JouleWise-wt-*` worktree. Probe scripts: `/tmp/oc2/q2.py`, `/tmp/oc2/q1b.py`, `/tmp/oc2/sweep4.py` (and `/tmp/bfgs_execution_probe.py`, Sol's, re-run unchanged).

Texts read (verbatim, from their files): FT v1.1 texts 9, 10, 12, §E, §F (`2026-09-26-activation-6bec2aa6/.../21-coldgate-fable-addendum-ruling.md` §4); amendment 26 (erratum, `2026-09-26-activation-f8d6cab1/.../30-erratum/...` §3); amendments 36 (round-2 rule), 41 (round-2 note), 42 (`20-bfgs-s1/40-coldgate/30-erratum/...` §4); amendments 47, 48 (`70-consult-samesig/30-erratum/...` §8).

Terms. **Gate**: `bundle_read.authenticate_window_members(members)`; it returns a verdict per member or raises `WindowBatteryRefusal` (status refusals, every member named) or `CustodyFailure`/`CustodyUnreadable` (custody: the file whose digest was recorded is gone or changed). Both are `RuntimeError` subclasses. **Direct read**: code that opens the bytes of a bundle's `metadata.json`, `summary_metrics.json` or `power_trace.csv` without going through `BundleReader`'s gated accessors. **Sweep**: `tests/test_bfgs_consumer_sweep.py`, the AST scan text 12 requires.

---

## Section A — independent answers (written before any ruling existed)

### Q1. Is the quarantined supersession copy a window member? — YES. Uphold Sol F1 (BLOCKER).

**What the text says.** Text 12: "`members` = every finalized bundle of the window, `FAILED` included, **and** every attempt the attempt ledger records, selected or superseded". The supersession copy qualifies under the *first* clause alone: it is a bundle the window finalized (it was declared, run and emitted; the supersession record's `superseded_occurrences` names it; `validate_occurrence_supersession_entry` digest-binds its `config.json`, `metadata.json` and `summary_metrics.json`, `whole_window.py:2819-2839`). Moving it outside `runs_dir` changes where it lives, not whether the window produced it. Why the rule exists physically: the charger state is a property of the machine during the window. A confounded first occurrence says the machine was charging during the window; rerunning the block and selecting the rerun does not un-charge the machine for the other members. Leaving the quarantined copy out is exactly the "select the rerun, hide the bad one" path that the supersession docstring (`whole_window.py:3052-3058`, "that default is what stops outlier laundering") exists to prevent.

**Executed evidence (at `49d77c74`).** `/tmp/bfgs_execution_probe.py` unchanged:
```text
campaign_helper ['pass'] quarantine_included False
ruled_set [('superseded', 'battery_float_confounded')]
aggregate_selected_mean 42.0
```

**Which consumers have the omission.** Production requires the quarantine to lie outside `runs_dir` (`run_campaign.py:6109-6111` at record time; `whole_window.py:2826` at validation), so no consumer whose member set is built from paths under `runs_dir` can contain it. By construction, then:
- `scripts/run_campaign.py::_authenticate_whole_window_members` (`:6197`): omits it (executed above).
- `joulewise/analysis_engine/inputs.py::load_analysis_inputs` (`:3131-3140`): builds `battery_paths` only from manifest entries under `runs_root`, although the same module resolves supersessions for campaign provenance (`:2189-2430`). Omits it (code reading; NOT EXECUTED as a probe).
- `whole_window.AuthenticatedConsumptionSession._prepare` (`:679`) gates whatever `bundle_paths` its caller passes; it inherits the caller's omission.
- The other five consumers (floor_extraction, aggregate, window_duration_margins, mint_floor_artifact, extract_detection_floors) do not read supersession records at all (`grep -n supersession` finds nothing), so if a supersession exists in their window they omit it too.

**A second, related omission (same clause).** Several member sets are enumerated from what is on disk, not from what is recorded: `inputs.py:3133` (`if path.is_dir()`), `run_campaign.py:2801` (`if bundle_dir.is_dir()`), `:8931` (`if evaluation.bundle_path.is_dir()`), and the AXI `attempt_root.rglob("metadata.json")` (`inputs.py:3137`, `run_campaign.py:6212`). A recorded member whose directory has been deleted is silently dropped from the gate. The gate itself would have said custody (executed, `/tmp/oc2/q1b.py`):
```text
symlinked member raised CustodyUnreadable raw path traverses a symlink: .../b
absent member raised CustodyUnreadable gone: missing required artifact: metadata.json
```
Pre-filtering with `is_dir()` turns a custody fact (a recorded member is gone) into an omission. Whether a number then reaches an output depends on each consumer's later missing-member handling; NOT EXECUTED.

**Smallest text (proposed amendment wording).**
> **Text 12, member set, authentication of recorded members.** A consumer builds `members` from the records that name them, never from directory listings alone: (a) every bundle its manifest, attempt ledger or campaign log names; (b) for every supersession record that the consumer's own membership resolution accepts (the record `validate_occurrence_supersession_entry` returns `True` for), the quarantined copy at `record["quarantine"]["path"]`, passed to the gate as recorded (not re-resolved), labelled `"<bundle_id>@superseded"`; (c) every AXI attempt the attempt ledger records, at the path the ledger names. No `is_dir()`, `exists()` or `rglob` result may remove a recorded member from `members`; an absent or symlinked recorded member reaches the gate, which raises `CustodyUnreadable` naming it. Directory listings may add members (an unrecorded finalized bundle on disk is still a member), never remove them. This applies to `run_campaign._authenticate_whole_window_members`, `run_campaign.run_campaign`'s final gate, and `inputs.load_analysis_inputs`; the other five consumers carry a named statement in the S1 report that their member source cannot contain a supersession, or they apply (b).

**Test rows** (production call sites named; each must fail under the named counterfactual):
- Q1-1, `_authenticate_whole_window_members` via `_run_whole_window_verdict_locked`: one canonical selected pass bundle under `runs_dir`, one charging-pair quarantined copy outside it, a valid supersession record → `WindowBatteryRefusal` naming `"<id>@superseded"` as `battery_float_confounded`. Counterfactual: the helper at `49d77c74` (returns `['pass']`).
- Q1-2, same site: the quarantined copy's `raw/battery_float.post.ioreg` deleted → `CustodyFailure` with `window_member == "<id>@superseded"`. Counterfactual: quarantine omitted (no raise).
- Q1-3, `load_analysis_inputs`: the same shape through a manifest whose campaign log carries the supersession → refuses naming the superseded copy. Counterfactual: `battery_paths` from manifest entries only.
- Q1-4, `run_campaign` final gate and `load_analysis_inputs`: a recorded member whose directory is deleted → `CustodyUnreadable` naming it. Counterfactual: the `is_dir()` pre-filter.

### Q2. Text 9, windowless placements and the `no_bundle` marker. — Uphold Opus B-2 (BLOCKER on the contract; no production caller today).

**What the text says.** Key set = every placement with status ≠ `not_started`, "whether or not a capture window exists". Each entry is a bundle `PairVerdict`; its digest "**where a capture window exists** must equal" the window's. The marker is for "a placement **the roster records as having finalized no bundle**", accepted "only when it equals the roster's own observation status".

**What the code does** (`scored_reduce.py:127-138`): every `PairVerdict` must bind to a window (`digest is not None and ...`), and the marker is accepted for any windowless placement whose marker equals its status. The roster vocabulary is `{completed, cut_off, not_started}` (`scored_packer.py:237, 402`); no roster field records bundle finalization. So the ruled condition "the roster records as having finalized no bundle" is unsatisfiable by any roster fact, and the implementation replaced it by "has no capture window".

**Executed evidence** (`/tmp/oc2/q2.py`, fixture `_terminal_night(width=2, kind="ceiling_violation")`):
```text
marker entries: Counter({('voided', 'cut_off'): 2, ('voided', 'completed'): 2, ('terminal', 'completed'): 2})
target ('large:decode:1:0', 0) ('voided', 'cut_off')
pass -> refused ("battery_evidence_unbound: ('large:decode:1:0', 0)",)
confounded -> refused ("battery_evidence_unbound: ('large:decode:1:0', 0)",)
marker -> REDUCTION PRODUCED dict
```
A started, windowless placement whose bundle is confounded can be excused by the only input the reducer accepts for it, so a window with a confounded member yields a reduction.

**Smallest text (outcome table; replaces the marker sentence of text 9).**

| Placement status | Capture window | Entry | Outcome |
|---|---|---|---|
| `not_started` | — | any entry | `battery_evidence_unbound` (as now) |
| `completed` / `cut_off` | exists | bundle `PairVerdict`, digest = window digest | `pass` → continue; `battery_float_confounded` → that code; any other status → `battery_float_evidence_missing` |
| `completed` / `cut_off` | exists | `PairVerdict` with another digest, or marker | `battery_evidence_unbound` |
| `completed` / `cut_off` | none | bundle `PairVerdict` with a 64-hex digest | digest must equal no window's digest and no other entry's digest (else `window_bundle_duplicate` / `battery_evidence_duplicate`); then status decides exactly as in row 2 |
| `completed` / `cut_off` | none | marker | `battery_evidence_unbound`, until a ruled harvest fact records that the placement finalized no bundle |

> **Text 9, marker (amendment wording).** "No roster field records bundle finalization. Until the scored campaign's harvest step is ruled and records, per placement, that no bundle was finalized, the `{"no_bundle": ...}` marker is admissible for no status; a marker on any key raises `battery_evidence_unbound`. A windowless started placement carries its bundle `PairVerdict`, which is not bound to a window (none exists) but is unique by digest across entries and windows, and whose status refuses the reduction exactly as a windowed entry's does. The harvest ruling that introduces the finalization fact re-admits the marker by naming that fact and the statuses it covers."

Why "admissible for no status" is safe now: `reduce` has no production caller (text 9), so the only effect is on fixtures, and a real started block that crashed before its bundle finalized makes the reduction refuse, which is fail-closed.

**Test rows** (production call site: `scored_reduce.reduce`; the fixture producer `_battery_fixture` must stop emitting markers for started placements):
- Q2-1: confounded `PairVerdict` on the voided `cut_off` placement above → `battery_float_confounded`. Counterfactual: `49d77c74` (refuses `unbound`, i.e. the refusal code hides the physics).
- Q2-2: passing `PairVerdict` on that placement → reduction produced. Counterfactual: `49d77c74` (`unbound`).
- Q2-3: marker on a `completed` and on a `cut_off` windowless placement → `battery_evidence_unbound`. Counterfactual: `49d77c74` (reduction produced).
- Q2-4: windowless `PairVerdict` whose digest equals another placement's window digest → `window_bundle_duplicate` or `battery_evidence_duplicate`. Counterfactual: a uniqueness check over windows only.

### Q3. The sweep. — Uphold Sol F2 and Opus B-1 (BLOCKER).

**What the text says.** Text 12: the sweep "flags ... **any direct read** of `summary_metrics.json`, `metadata.json` or `power_trace.csv`, in a function that does not call `authenticate_window_members` or `BundleReader.metadata()`; every exemption is a named allowlist row with a reason (classes `non_claim`, `historical`, `strict_validation`)". Amendment 41: the sweep "**must report**" `issue_dg071_dg075_statistics.py`'s read.

**Defects** (`test_bfgs_consumer_sweep.py:119-150`, unchanged by fix round 2): a read is seen only when the filename literal sits inside the read call's own subtree and the call is one of seven names; the gate test is "any call named `metadata` on any receiver, anywhere in the function"; amendment 41's witness is met by a clause hard-coded to `build_payload`/`actual_path`. Sol's mutants reproduced at `49d77c74`:
```text
sweep_mutant literal [('joulewise/new_claim.py', 'claim', 'direct:read_bytes', 2)]
sweep_mutant assigned []
sweep_mutant read_before_gate []
sweep_real_paper [] allowlist_rows []
```

**Inventory** (`/tmp/oc2/sweep4.py` over `git ls-files joulewise scripts` at `49d77c74`: intraprocedural taint from watched-filename literals and module constants through assignments, `for` targets and `with` targets; a read is any call named in the sweep's `READS`, `open_authentication_input`, `DictReader`, `reader`, `load`, or a name matching `_?(read|load|open)…`/`…_json_object`/`…_json_file` whose argument or receiver is tainted; gate order compared by line). 47 ungated or read-before-gate sites; 26 are in the allowlist; **21 are neither listed nor reported**. A coarser pass (any function that mentions a filename and calls a read) adds helper-by-parameter sites. My classification of every unlisted site, for a by-name ruling:

| # | Path : line | Function | What it reads | Class |
|---|---|---|---|---|
| 1 | `joulewise/floor_extraction.py:1734` | `_read_summary` | summary **energy metrics** of floor members | **behind_gate** (only callers `extract_absolute_cell`/`extract_comparative_cell`, both public in `__all__`, reached in production only from `extract_cells`, gated at `:2879`) |
| 2 | `joulewise/floor_extraction.py:1924` | `_evaluate_member` | metadata (admission) | behind_gate, same chain |
| 3 | `joulewise/floor_extraction.py:1852` | `_cpu_admission_bundle_reasons` | metadata identity | behind_gate, same chain |
| 4 | `joulewise/whole_window.py:4770` | `_validated_evaluation_basis` | digests of config/metadata/summary | strict_validation (digest only) |
| 5 | `joulewise/whole_window.py:2830` | `validate_occurrence_supersession_entry` | digests of the quarantined copy | strict_validation (digest only) — and see Q1: its bundle must then be gated |
| 6 | `joulewise/salvage_dangler.py:641` | `_telemetry_timestamp_bounds` | `power_trace.csv` rows incl. `power_w` (parsed for finiteness; returns time bounds) | strict_validation (returns timestamps, no energy) |
| 7 | `joulewise/bundle_read.py:3198` | `_check_power_trace` | trace structure (reader's `problems()`) | strict_validation |
| 8 | `joulewise/cli.py:1856` | `_cmd_reduce` | stored summary `summary_provenance` (reducer version) | strict_validation (single-bundle reduce; `reduce.py` authenticates `metadata()`) |
| 9 | `joulewise/determinism_gate.py:724` | `_check_gate_json_evidence_for_duplicate_keys` | duplicate-key scan | strict_validation |
| 10 | `joulewise/envelope_gate.py:692` | `_bundle_hashes` | digests | strict_validation |
| 11 | `joulewise/output_identity.py:157` | `_bundle_reference` | run id, identity fields | non_claim |
| 12-14 | `joulewise/analysis_manifest_v3.py:3103, 3220, 3350` | `_verify_basis_members`, `_derive_arms_and_entries`, `_floor_consumer_contexts` | digests; realized config/metadata identity; telemetry backend | strict_validation (manifest finalization; not one of the eight; no energy value) |
| 15 | `scripts/run_campaign.py:5980` | `_basis_member_occurrences` | digests | strict_validation |
| 16 | `scripts/run_campaign.py:6119` | `_run_record_supersession_locked` | digests at record time | strict_validation |
| 17 | `scripts/run_campaign.py:2929` | `summary_status` (path by parameter; caller `evaluate_member`) | summary `status` only | strict_validation |
| 18 | `scripts/package_bundle_pack.py:135, 172` | `_bundle_id`, `_summary_status` | run id, status | non_claim |
| 19 | `scripts/check_window_provenance.py:734` (+ `check_a2` `:676`) | `_run_assertions.check_a3` | summary incl. `gross_energy_j` (cooldown metric) | **other**: diagnostic checker reading an energy value; needs a ruled class or a gate |
| 20 | `scripts/summarize_g2a_prefill_probe.py:477` | `summarize` | summary + metadata of probe runs (provenance, no `energy` token in file) | non_claim, if the ruling agrees the probe summary feeds no claim |
| 21 | `scripts/paper_prefill_resolvability_projection.py:252` (helpers `read_model`, `read_prefill_phases`, `read_support_intervals`) | `scan_corpora` | metadata model, trace **timestamps only**, record count | **other**: paper-facing, non-energy count; Sol proposes `historical` |
| 22 | `scripts/issue_dg071_dg075_statistics.py:281` | `_read_records` (path by parameter; caller `build_payload`, already listed) | `power_trace.csv` rows | historical, amendment 41 |
| 23 | `scripts/build_battery_float_historical_bundles.py` | `build`, `witness` | metadata `run_id`, digests | strict_validation |
| 24 | `scripts/validate_powermetrics_fiducial.py:2531` | `main` | its own capture's trace (not a bundle) | non_claim (not a bundle read) |

Allowlisted-but-dubious: `whole_window.whole_window_refusal_reasons`, `_current_core_rederivation_reasons`, `_validate_row_uncached` and friends carry `strict_validation` with the reason "called behind the window gate". That is a claim about the call graph, which no test checks; it is the same class as rows 1-3.

**Contract gaps in text 12's allowlist rule.** (i) Rows 1-3 are energy reads that are gated only at their caller; none of the three ruled classes fits ("non_claim" is false, "strict_validation" is false, "historical" is false). Either they gate themselves (N-7 says the singleton gates already there are redundant re-hashing) or the rule gains a class whose truth a test checks. (ii) Rows 19 and 21 are neither. (iii) "Function that calls `BundleReader.metadata()`" is unverifiable as written without receiver and order.

**Smallest text (proposed amendment wording).**
> **Text 12, sweep, what counts.** (a) A *watched value* is a string constant containing `metadata.json`, `summary_metrics.json` or `power_trace.csv`, a module-level name bound to one, or any local name bound (by assignment, walrus, `for` target or `with` target) from an expression containing a watched value. (b) A *read* is any call whose receiver or argument contains a watched value, except the path-inspection calls `exists`, `is_file`, `is_dir`, `lstat`, `stat`, `relative_to`, `resolve`, `as_posix`, `str`, `joinpath`, the `/` operator, and `with_name`; `open_authentication_input` and helpers taking the path are reads. (c) A function is *gated* only if a call to `authenticate_window_members`, or `.metadata()` on a receiver that is a `BundleReader(...)` construction or a local name bound to one, precedes every read in source order. (d) The site-specific clause for amendment 41 is deleted; the generic rule must report that site. (e) Allowlist keys are `(path, qualified function, operation)` as now; the class set gains `behind_gate`, whose row names the gated caller(s) as `path::function`, and a test asserts that every production call of the function (resolved by name within tracked `joulewise/` and `scripts/`) lies in a function that is gated or itself `behind_gate`, and that the function is not exported in `__all__` (rows 1-3: remove `extract_absolute_cell`/`extract_comparative_cell` from `__all__` or gate them). (f) A read of an energy field (a key containing `energy`, `joule`, `power_w`, or a `power_trace.csv` value column) may carry `historical` or `behind_gate` only; `non_claim` and `strict_validation` are for identity, status, time or digest reads. Every row of the 24 above is ruled by name with one class; rows 19 and 21 are the ones this ruling must decide.

**Test rows** (production call site: `sweep_tracked()` over the real tree, plus `sweep_source` self-tests):
- Q3-1: mutants M1 (assigned path), M1c (module constant), M1d (`open_authentication_input` + `DictReader`), M1e (`event.metadata()` then a read), and a read-before-gate mutant are each reported. Counterfactual: `49d77c74` (all return `[]`).
- Q3-2: with the amendment-41 special clause deleted, the sweep still reports `issue_dg071_dg075_statistics.py::build_payload`. Counterfactual: the literal-only matcher.
- Q3-3: the `behind_gate` call-graph check fails when a new ungated production caller of `_read_summary`'s chain is added. Counterfactual: a check that trusts the row's text.
- Q3-4: the tracked sweep's result set equals the ruled allowlist exactly (no unlisted report, no stale row). Counterfactual: `test_all_ungated_reads_have_named_reason` at head, which passes with 21 unreported sites.

### Q4. S-1 and S-2.

**S-1 — a breach; UPHOLD (SHOULD-FIX, not BLOCKER).** Amendment 36's round-2 rule: consumers "do not catch `CustodyFailure`, by that name or through `except Exception`". `except (OSError, RuntimeError, TypeError, ValueError)` at `inputs.py:1751` catches `CustodyFailure` through its superclass `RuntimeError`, which is the thing `except Exception` names by example; the rule's stated reason ("the window gate labels it with the member, so a consumer needs no handler") applies to any superclass. The site converts custody into the reason string `salvage_floor_verdict_revalidation_failed: ...: whole_window_verdict_provenance_invalid` in `global_problems`, which is precisely "a read failure into a per-bundle reason" (the round-2 brief's hard constraint). Fail-closed (every cell refuses), so no number escapes; hence SHOULD-FIX. The handler predates round 2 but round 2 made the gate reachable through it, so it is round 2's to close.
> **Amendment 36, round-2 rule, clarifying wording.** Replace "through `except Exception`" by "through any handler whose type is, or whose tuple contains, `CustodyFailure`, `WindowBatteryRefusal` or any superclass of either (`RuntimeError`, `Exception`, `BaseException`), or a bare `except:`, unless the handler's first statement re-raises the caught object unchanged; a handler that must keep catching other `RuntimeError`s places `except WindowBatteryRefusal: raise` and `except RuntimeError as exc: if getattr(exc, 'window_member', None) is not None: raise` before its own clause (neither needs a `battery_float` import)."
Test: `bind_floor_artifact_evidence` with a salvage component whose post raw is deleted → `CustodyFailure` with `window_member`; counterfactual: `49d77c74` (string reason). Plus an AST check over the eight modules for the handler rule.

**S-2 — REMOVE the collection-time gate (SHOULD-FIX).** Text 12 scopes `run_campaign.py` to "its final analysis and whole-window verdict". `evaluate_member` runs per member during collection (`run_axi_spec_campaign :7445, :7687, :7717, :7948`; `run_campaign :8495, :8617, :8788`) and before `record_campaign_member_provenance`. The singleton gate there is unruled production-night behaviour, names only the first bad member (amendment 42 exists to name every one), and aborts before the member's provenance row is written, so the campaign log loses the record that the bad member ever existed. That last effect runs against Q1's rule (members come from records): a resumed campaign's membership would be built from a log that never recorded the confounded bundle. Remove the gate from `evaluate_member`; keep `:8928` (made record-driven per Q1); give `evaluate_member`'s `summary_status` read a `strict_validation` row. Test: a campaign whose member 2 is charging writes member 2's provenance row, reaches the final gate, and refuses naming member 2 (and every other bad member). Counterfactual: `49d77c74` (aborts at member 2, no provenance row).

### Q5. R47-4. — The classification rule governs.

The rule is the ruled mechanism; the row is its witness and must agree with it. Amendment 47's rule: text includes "every `.json` or `.jsonl` file that fails to parse"; a candidate with no table row in a file not ending `.md`/`.html`/`.txt` makes the builder exit `unclassified candidate pair`, because such a file "may be a citation source that nobody has classified". A `.json` file is exactly a data file that might cite a digest. The row's counterfactual ("today's `continue`, which skips the file") is about scanning, not classing, and survives the correction. Executed: no tracked `.json`/`.jsonl` at `1417c0c4` that fails to parse holds a text candidate (22 unparseable files, 0 candidates), so the raise cannot fire on the real tree and R47-5's "69 entries byte-identical" holds.
> **Corrected R47-4.** Input: `broken.json` that fails to parse and holds the line of R47-1, with no classification row. Expected: stderr names `broken.json` as unparseable, then `ValueError` matching `unclassified candidate pair` naming key `bundle_tree_sha256` and `broken.json`. Must fail under: today's `continue` (returns `([], [])`, exits zero). **R47-4b.** The same file with a classification-table row for (`bundle_tree_sha256`, `broken.json`) → one listed candidate with that row's class. Must fail under: a rule that raises on every unparseable-JSON candidate regardless of the table.

### Q6. S-3, S-4, S-5, NITs.

- **S-4, S-5, N-1, N-2, N-3, N-4, N-8**: test or comment fixes, no text change. Confirm. N-2's constants are anchored to `1417c0c4` (ledger `sequence 176`, committer time `1790462247`); main has moved to `97a48451` since, with no change under `configs/calibration/` (`git diff --stat 1417c0c4 origin/main -- configs/calibration` empty), so the constants stay valid unless S1 rebases onto a main that changes the ledger.
- **S-3 is not purely a test fix.** Its behavioural rows are tests, but "the spec-only member sets" of `mint_floor_artifact`, `window_duration_margins` and `aggregate` is the Q1 member-set question; it needs the Q1 text (members from records, supersession copies, no disk pre-filter) before tests can be written. The import-matcher fix (`from joulewise import battery_float`) and the handler AST check are tests under the existing round-2 rule and the Q4 wording.
- **N-5 is a production behaviour change** (handlers that cannot reach the gate narrowed from `Exception`, so `AttributeError`, `IndexError`, `BundleReadError` now crash where they used to produce a structured refusal or cleanup). No ruled text asks for it. Rule: revert every narrowing whose try-body cannot reach the gate, or list each in the PR body as intended; this is a code fix in fix round 3, not a test fix.
- **N-6** (result-shape additions without a schema bump): PR-body record, no text change, provided no stored pre-S1 verdict or receipt exists (Opus lens found none).
- **N-7** folds into Q3's `behind_gate` class.

**Recommended fix round 3 contents (Section A view):** Q1 member-set text and rows; Q2 marker and windowless rows; Q3 sweep detector, `behind_gate` class, the 24-row ruling, self-tests; Q4 handler rule and removal of the collection gate; Q5 corrected R47-4/4b; S-3 behavioural rows per consumer; S-4, S-5, N-1–N-5 (revert), N-8. Then round F as ruled (amendment 38).

---

## Section B — refutation of `21-coldgate-fable-ruling.md` (amendments 49 to 54)

Read after Section A was written. New probes (all at `49d77c74`, in `/tmp/oc2/head`): `/tmp/oc2/sweep_holes.py` (the ruling's own prototype `/tmp/cg_r2/sweep49.py` on six new sources) and `/tmp/oc2/gate_try.py` (every `try` in tracked `joulewise/` and `scripts/` whose body calls the gate or `_prepare` directly, with a broad handler).

**Agreement first.** On every question, the ruling and Section A reach the same verdict: Q1 upheld, Q2 marker admitted for no status, Q3 re-specified detector with a checked `behind_gate` class, Q4 S-1 a breach and S-2 remove, Q5 the rule governs, Q6 test fixes. Amendment 50 matches my outcome table row for row, and I have no finding against it beyond one NIT. The findings below are about places where the ruled text still lets custody become a status, or still lets an ungated read count as gated.

### BLOCKER

**RB-1. Amendment 49 (c): a deleted or altered quarantined bundle turns into a verdict-row condition, not custody. R49-3 is placed where it cannot see this.**

49 (c) says "A quarantined bundle is never skipped because it is absent: the record says it exists, so its absence is a custody failure", and §11 says it "raises through the gate's existing custody path (E4)". That holds only at the helper, with a hand-built resolution. On the production path, item 4 includes only records that pass `validate_occurrence_supersession_entry` (49 (b) 4, "Valid' means the record passes …"). That function returns `False` when the quarantine path does not resolve (`whole_window.py:2823-2826`, `resolve(strict=True)` under `except (OSError, RuntimeError): return False`) or when any of its three recorded digests fails to match (`:2828-2845`). The resolver then does the following:
- `_resolve_ordinary_occurrence` marks the id `ambiguous` (`run_campaign.py:5471-5478`);
- the membership candidate is skipped (`:5852-5853`, `if failed: continue`);
- the fallback membership carries the condition `whole_window_campaign_membership_ambiguous` or `whole_window_campaign_membership_unresolved` (`:5934-5958`);
- `_run_whole_window_verdict_locked` gates the fallback list, which never holds the quarantine, adds the condition to `core["conditions"]` (`:6349`), and writes a verdict row with `status` `failed` (production) or `flagged` (exploratory) (`:6372-6379`).

On `inputs.py`, the same invalid record gives the member `refusal_payload` (`:2425-2429`), which is a per-member reason. In both cases the bytes the record digest-binds are missing or changed, which is the ruling's own definition of custody (§1), and the result is a status string. No number is released, since the status is `failed` or the member is refused. The kept-intact claim is still false, and the charge lists "turn custody into a status" as a refutation ground. (Read, not run: I did not build a full campaign log. The helper-level R49-3 passes by construction.)

Replacement text, appended to 49 (c):
> "The record's validity and the quarantined bundle's custody are decided separately. `validate_occurrence_supersession_entry` decides validity from the record's own fields only (schema, record type, runs root, ids, reason, occurrence descriptors, `entry_sha256`, `quarantine.path` a non-empty string naming a location outside the runs directory, three 64-hex digests). For a record valid in that sense, the quarantined bundle is a member under item 4 whatever the state of its directory. Its absence, a symlink, or a mismatch between a recorded digest and the file's bytes is a custody failure: the resolver passes the recorded path to the gate, which raises `CustodyUnreadable` for absence or a symlink, and the resolver raises `CustodyFailure` labelled `superseded:<bundle_id>:<recorded path>` for a digest mismatch. It never resolves the id `ambiguous` or `unresolved` on those grounds."

Rows (production call sites, not the helper):
- **R49-3b.** `run_whole_window_verdict`, where the log holds a record written by `_run_record_supersession_locked` and the quarantine directory is deleted afterwards. Expected: `CustodyUnreadable` with `window_member` starting `superseded:`, and no verdict row appended. Must fail under the code at `49d77c74`, which appends a `failed` row carrying `whole_window_campaign_membership_ambiguous`.
- **R49-3c.** The same record, with one byte appended to the quarantined `summary_metrics.json`. Expected: `CustodyFailure`, no row. Same counterfactual.
- **R49-7b.** `load_analysis_inputs`, with the quarantine deleted. Expected: custody raised. Must fail under the code at `49d77c74`, which gives the member `refusal_payload`.

### SHOULD-FIX

**RS-1. Amendment 51 (d) counts a gate inside a `try` or `with` body as dominating, even when a handler swallows it. A read inside the `except` handler counts as gated.** The ruling's own prototype (`/tmp/cg_r2/sweep49.py`) on new sources:
```text
silent    H1 gate swallowed by try/except Exception, read after []
silent    H2 gate under contextlib.suppress []
silent    H4 gate in try body, read in except handler []
REPORTED  H5 early return before gate on a branch, read after [...]
```
H4 is the worst case: the read runs exactly when the gate raised. Amendment 52 closes H1 and H2 only in the eight consumer modules, but the sweep covers every tracked file. Replacement for 51 (d), last sentence:
> "The body of a `try` counts as a branch unless every handler of that `try` whose caught types include `CustodyFailure`, `WindowBatteryRefusal` or an ancestor of either (or that names no type) is preceded by `except GATE_EXCEPTIONS: raise` or ends in a bare `raise`. A read site inside a handler, `else` or `finally` of a `try` whose body holds the gate call is never gated by that call. The body of a `with` counts as a branch when its context expression is a call named `suppress`."

Rows: R51-18 (H1), R51-19 (H2) and R51-20 (H4) are each reported. Counterfactual: rule (d) as ruled (the prototype output above).

**RS-2. Amendment 52 stops at the eight modules. At least one ninth site converts the gate's exceptions into a refusal code.** `/tmp/oc2/gate_try.py`:
```text
joulewise/analysis_manifest_v3.py:3712 handler ['KeyError', 'OSError', 'RuntimeError', 'TypeError', 'ValueError'] bare_reraise=False gate_line=3704 (_prepare)
scripts/run_campaign.py:8996 handler ['BaseException'] bare_reraise=True gate_line=8928 (authenticate_window_members)
```
`analysis_manifest_v3.py:3704-3716` calls `session._prepare` (whose gate is `whole_window.py:679`). It catches `RuntimeError` and re-raises the failure as `AnalysisManifestFinalizationError("analysis_finalization_attachment_invalid", …)`. That is custody turned into a finalization code. `:4499` does the same through `except Exception`, returning a `ManifestRefusal` (the Opus round-2 lens noted both). Both fail closed. §11's sentence "Amendment 52 removes the one place found where a custody failure became a reason string" is therefore not accurate. The file is outside S1's WRITE_SCOPE. Replacement: add to 52:
> "(g) Residual, stated: `joulewise/analysis_manifest_v3.py:3712` and `:4499` catch the gate's exceptions through `_prepare` and convert them to finalization refusals. They are outside S1's WRITE_SCOPE. They are either added to S1 by name, with the clause of (c), or registered as a lane that must close before any analysis manifest is finalized over a post-S1 bundle."

R52-4's syntax-tree check should also run over every tracked module that calls `authenticate_window_members` or `_prepare` directly. Where such a module is out of scope, the check lists it as the named residual rather than skipping it.

**RS-3. Amendment 53 (b) ("over every evaluated member whose bundle directory exists") and 49 (b) keep member lists that come from the disk, not from the record.** A recorded, finalized member whose directory is gone is dropped before the gate, although E4 shows the gate would raise custody for it:
- `run_campaign.py:8931` (`if evaluation.bundle_path.is_dir()`);
- `inputs.py:3133` (`if path.is_dir()`), after which `_read_bundle` gives the member the per-bundle reason `bundle_missing` (`inputs.py:2770-2783`), so the analysis continues without it;
- items 3 and 49 (e), which enumerate AXI attempts by `rglob`/`finalized_bundles` and not by the attempt-ledger rows that text 12 names ("every attempt the attempt ledger records").

A confounded bundle deleted after finalization would therefore be an exclusion, not custody. That is the path the charge names ("a custody-failed bundle reach a number"). Whether the remaining members then yield a number is NOT EXECUTED. `bundle_missing` is also the honest state of a run that never finalized, so the replacement keys on the record:
> "A member whose record carries a digest of its bytes (a campaign provenance row, an evaluation-basis occurrence, an attempt-ledger row naming a finalized run, a supersession record) is finalized. If its directory is absent it is passed to the gate, which raises `CustodyUnreadable`. `bundle_missing` and `terminal_absent` remain only for members that no such record names. In 53 (b), 'whose bundle directory exists' is replaced by 'whose evaluation recorded a finalized bundle'. In 49 (b) 3 and (e), the attempts are the attempt ledger's rows, each at the path the ledger names."

Row: R53-4. `run_campaign`, member 2 finalized and evaluated, its directory deleted before the final gate. Expected: `CustodyUnreadable` naming it. Must fail under the `is_dir()` filter.

**RS-4. The premise of 49 (b) for `run_campaign` ("a supersession is recorded only after collection") hides the rerun's own final analysis.** The ruled operator workflow is printed by `run_campaign.py:8509-8511`: "quarantine the failed fragment, rerun, and record ordinary occurrence supersession". The rerun is a `run_campaign` invocation, and its final analysis (`:8928`) runs while the first occurrence is already outside the runs directory and **no record yet exists**. So that final analysis gates a list without the (possibly confounded) first occurrence. The whole-window verdict run afterwards is covered by 49. The rerun's collection-level row is not. The replacement follows from RS-3's rule: the campaign log's provenance row for occurrence 1 carries its digests (`_basis_member_occurrences`), so under RS-3 the rerun's final analysis raises custody for the moved copy. That would stop the ruled workflow. The smaller alternative text:
> "`run_campaign`'s final analysis licenses no claim for a member id that the campaign log records with more than one occurrence. Only the whole-window verdict, under item 4, may license it."

Test: rerun after a manual quarantine, with the first occurrence charging. The final analysis output carries no claim licence for that id. Must fail under the code at `49d77c74`. NOT EXECUTED.

**RS-5. The `BundleReader` gate form in 51 (c) does not bind the reader to the read.** The prototype on `BundleReader(a).metadata(); return BundleReader(b).raw_summary()` gives `silent H6`. The four tolerant accessors are read through a reader object, so the smallest fix is:
> "A tolerant-accessor read site (b) 1 is gated by the `BundleReader` form only if its receiver is the same name, or the same `self`, whose `.metadata()` call is the gate."

A read through `authenticate_window_members` (member list against read path) stays unbound. State that as a residual in (h).

### NIT

- **RN-1 (amendment 50, R50-8).** The expected text says the producer at `49d77c74` "emits five markers". On the row's own named fixture, `_terminal_night(width=2, kind="ceiling_violation")`, I count six (`/tmp/oc2/q2.py`: voided `cut_off` 2, voided `completed` 2, terminal `completed` 2). The Opus lens counted four for `completed`. Replace the count with "emits at least one marker", or name the fixture that gives five.
- **RN-2 (amendment 49 (f)).** A set consumer relies on the verdict row having gated the superseded runs. Consumption-time revalidation (`whole_window._prepare`, `:679`) re-gates only the referenced members, so a verdict row written by pre-49 code is not re-checked for superseded runs. Today this is harmless, because every bundle collected after the base is refused as a prospective bundle until S1 merges, and E5 shows the seven existing supersessions are all refused. Add one sentence to (f) saying so, so that the reasoning survives if the historical set ever grows.
- **RN-3 (amendment 51 (f), `non_claim` (ii)).** Clause (ii) lets an energy read be `non_claim` on the claim that "nothing the function returns or writes is consumed by a claim artifact". That claim is about downstream use, and no test checks it. For example, `scripts/check_window_provenance.py::_run_assertions.check_a3` reads `gross_energy_j`. Require the reason for (ii) to name the output path, and require the refuter to check each (ii) row by grep for consumers of that path.
- **RN-4 (amendment 53 (e)).** Agreed as flagged. Round F should be told that R53-1-shaped fixtures replace the MOCK campaigns that used to abort at member 1, so that no one "fixes" the new refusal by re-adding a collection-time gate.

### Tier summary

BLOCKER RB-1 (49 (c): custody of the quarantined bundle becomes a verdict condition; add R49-3b, R49-3c, R49-7b at the production call sites). SHOULD-FIX RS-1 (51 (d): swallowed gates count as dominating; H1, H2, H4 silent in the ruling's own prototype), RS-2 (52 is limited to the eight modules; `analysis_manifest_v3.py:3712/:4499`), RS-3 (disk-driven member lists in 53 (b), `inputs.py:3133` and 49 (b) 3/(e)), RS-4 (the rerun's final analysis runs before any supersession record exists), RS-5 (the `BundleReader` gate is not bound to its reader). NIT RN-1 to RN-4. No finding against amendments 50 (beyond RN-1) or 54.
