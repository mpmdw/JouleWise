FINAL PASS: PASS

Cold final pass on PR #471 (`feat/2026-10-04-g2a-issuer-harvest-bound`), head `c783f0ee`, parent on main `8fa002f7`.
Judge: Claude Fable 5.1, cold, detached checkout, 2026-10-04. Scope: `scripts/issue_g2a_prefill_prompt_pin.py`,
`tests/test_issue_g2a_prefill_prompt_pin.py`, `tests/test_summarize_g2a_prefill_probe.py`.

No BLOCKER and no MAJOR. Five MINOR and five NIT findings below; none changes which record can fix the
parameter. The seal record's open obligation (a) and (b) is met by this change.

## What I ran

- Both test files, unmodified: 50 passed, 95 subtests passed.
- 42 single-line mutations of the issuer, applied in memory only (the checkout was never edited;
  `git status` stayed clean), each run against the issuer tests plus the desk-chain and valid-filter tests.
  28 killed, 14 survived. Harness: `/tmp/dd5-fable-is/mut.py`.
- The real issuer CLI on the real block-3 archive, output to `/tmp/dd5-fable-is/real/` only. It issued
  (exit 0); the pin's `g2a_record_sha256` equals the seal record's selection sha256 `c694c488…8222`; the
  bundle's `selection.json` copy hashes to the same value; the pin length equals the selection record's
  collection length and the token-id list has that length. (Length deliberately not printed here.)
- Fifteen refusal probes of the real CLI against real archives (table under question 1). Every one refused
  with exit 2 and wrote no file.
- By hand on the real archive, without printing any count: the four-row summary equals the aggregation of
  the receipt rows; every receipt row's count equals the count in that member's archived
  `summary_metrics.json` (all rungs, not only the selected one); the selection record equals
  `selector.select(summary)`.

## The five questions

### 1. Can any record other than the block-3 SELECT harvest's own selection produce a pin? Can a superseded or non-block-3 record count toward the end state?

No, on both counts, with one caveat recorded as MINOR-2 (the anchor is the checkout's `HEAD`, not `main`).

The binding chain in SELECT mode (`_prepare_pin`, issuer:739-763; `_load_harvest`, issuer:236-328):

1. The `harvest.json` bytes given on the command line must equal the bytes git holds at
   `HEAD:docs/process_traces/2026-10-03-design-block3/windows/<plan_id>/harvest.json` (issuer:155-172, 270).
   This one comparison excludes block-2 windows (no directory under the block-3 path), the superseded
   first harvest (committed as `harvest-r1-recover.json`, a different name) and any edited copy.
2. That record must say `verdict == "SELECT"` with empty `cause_codes` (issuer:245-248) and must sit in the
   archive directory it names (`archive_root`, issuer:241-244).
3. The selection file is the one the record names; it must lie inside the archive, hash to
   `selection.sha256` and to `outputs["selection.json"]`, and equal the committed `selection.json` byte for
   byte (issuer:743-760).
4. Block-3 identity is checked three more ways: the inventory and the frozen calibration plan both name the
   block-3 campaign policy by path and sha256 (issuer:273-281), the chain's `POLICY` literal is that policy
   path (issuer:308), and the plan's measurement-clone name ends in `b3w1` or `b3w2` (issuer:293-295).

Real-CLI evidence (all exit 2, no output file):

| Input | Mode | Refusal |
|---|---|---|
| superseded first harvest of `b3w1` (RECOVER, archive `…1305Z`) | end state | `harvest_committed_harvest_mismatch` |
| the same | SELECT | `harvest_verdict_not_select` |
| the SELECT harvest (`…1305Z-r2`) | end state | `harvest_recover_required` |
| block-3 NULL window (`…0526Z`) | end state | `harvest_recover_required` |
| block-2 `…0820Z`, `…1748Z` (first harvests) | end state | `harvest_recover_required` |
| block-2 `…0820Z-r2`, `…1748Z-r2` (RECOVER) | end state, singly and as a pair | `committed_window_record_missing` |
| all four block-2 archives | SELECT | `harvest_verdict_not_select` |
| the committed copy of `harvest.json` (path in the repo, not the archive) | SELECT | `harvest_archive_root_mismatch` |
| SELECT harvest plus a stray `--recover-harvest` | SELECT | `issuer_mode_inputs_invalid` |

With the records committed at this head, no end-state pin can be issued at all: the only block-3
`harvest.json` records are one NULL and one SELECT.

### 2. Does the issuer read only the archive and committed records (never `/Users/edr/night-g2a`)?

Yes. Every recorded live coordinate is translated to its archive copy without opening the source
(`_copied_path`, issuer:139-152; `_Harvest.mapped`, issuer:219-223); every archive file is resolved and
must stay inside the archive root, so a symlink out of the archive refuses (`_archive_file`, issuer:130-136);
and `_read_bytes` refuses any path that resolves under the live root (issuer:68-75). The one read that does
not go through `_read_bytes` is the summarizer's read of a member's `config.json`
(`summarize_g2a_prefill_probe.py:345`); its path is built from the mapped archive runs root and the same
file is confinement-checked one line earlier (issuer:676). The old code's `_resolve_inventory_config_root`
and `Path(receipt["runs_root"])` reads, which did open recorded live paths, are gone from the diff.

Other reads, all outside the live root: the repository working tree (registration, ruling traces, the
block-3 policy file, each hash- or path-checked), `git show HEAD:…`, and the tokenizer under
`/Users/edr/jw_models` (hash-bound to the ladder's tokenizer sha256, issuer:408-414).

Evidence: mutation M05 (guard removed) is killed by `test_archive_only_reads_when_live_window_is_absent`;
the real run issued with every read inside the archive or the repository.

### 3. Does the re-derivation (summary → selector rule → selection) still bind, including with invalid members excluded?

Yes. The input is the harvest's regenerated valid-member summary `derived/summary.json`, bound by its
sha256 in the committed `harvest.json` (`_harvest_summary`, issuer:346-364). The selection record must
equal `selector.select(summary, summary_sha256=…)` as a whole object (issuer:448-460). The chain's own
copies are checks only: bytes must match when the harvest recorded `equal`; when it recorded
`differs_invalid_members_excluded` they are not compared, as registration §8 requires. The receipt check
recomputes each selected-rung row from the archived bundle through the summarizer's own `_run_provenance`,
for exactly the members the committed harvest marks valid, and the receipt's selected-rung run set must
equal that set (issuer:649-707), so an invalid member can neither be counted nor re-enter.

Evidence: M06 (selection-equals-rule check removed), M14 (valid filter removed), M15 (large-member floor
back to 1), M18 (run-set check removed), M23 (row recomputation removed) are all killed.

### 4. Is the §7 end-state trigger implemented exactly as the registration text says?

Yes (issuer:367-397). Registration §7: at least 5 members whose `clock_anchor_status` is other than
`not recorded`, and more than half of those other than `bounded`, read from the `harvest.json` of the first
RECOVER that made a capture; or the recovery window also ends RECOVER; a null window or a captureless
RECOVER never triggers. The code: `recorded` = statuses other than `not recorded`;
`len(recorded) >= 5 and 2 * (non-bounded) > len(recorded)`; one record with that property, or two records
(first `b3w1`, second `b3w2`, later t0, different plan id) without it; `capture_made is True` on every
record (issuer:249); NULL and SELECT records refuse on verdict. The output is fixed at 4096 with no
selection record read and no selector call (the test deletes `derived/selection.json` first), and the
end-state record carries only schema, registration sha256, harvest paths and sha256s, and the trigger.

Evidence: M03a (5→4), M03b (`>`→`>=`), M03c (count `not recorded`), M03d (5→6), M04 (capture requirement
removed), M28 (length changed) are all killed.

Under the orchestrator's ruling the end-state pin still carries the static `exhausted_ladder_branch`
constant, whose text includes `no_rung_clears_pre_registered_count_floor`. I read it as ruled: it is the
same constant in every pin, including a SELECT pin, and the end-state record itself says nothing of the
kind (asserted by the tests, test file:835-836). Not a finding.

### 5. Do the tests kill the regressions they claim?

The claimed ones, yes: committed-record anchor for harvest and selection (M01, M02), superseded-r1
exclusion (unit test on the real committed bytes plus my real-CLI probe), trigger boundaries (M03a-d),
capture requirement (M04), live-root guard (M05), rule re-derivation (M06), archive checksums (M09), frozen
plan policy and digest (M20, M33), chain policy (M21), valid-member SELECT (M14, M15), verdict (M25).

Fourteen mutations survived. Five are pairs or triples of overlapping checks where each alone is covered by
its neighbours (M26/M34 selection output hash; M07c/M19/M29 second-window label, t0 order, distinct plan
id). The rest are real gaps in the tests, not in the code; they are MINOR-4, MINOR-5, NIT-1 and NIT-2 below.

## Findings

### MINOR-1. A file missing from the archive's `SHA256SUMS` is read with no checksum, and the archive's `SHA256SUMS` is never compared with its committed copy

`scripts/issue_g2a_prefill_prompt_pin.py:193-203` and `:175-190`. `_checked_archive_file` checks a file only
`if expected is not None`; an archive whose `SHA256SUMS` lacked a line (or was empty) would pass every
source-file check vacuously. Separately, a committed copy of each window's `SHA256SUMS` exists
(`windows/<plan_id>/SHA256SUMS`; for the real window it is byte-equal to the archive's, checked) and the
issuer does not use it.

Why this is not higher: in SELECT mode every file that decides the pin is bound from the committed
`harvest.json` without `SHA256SUMS` (plan by `plan_sha256`; summary, receipt, selection by `outputs`;
inventory and ladder by the receipt; configs by the inventory). On the real run the only file read without
a checksum was `harvest.json` itself, which is byte-anchored to git. In end-state mode the inventory, ladder
and chain rest on `SHA256SUMS` alone, but the pin's content there is the 4096 rung, which is rebuilt from
the fixed sentence and re-tokenized. Suggested follow-up, two lines: `_reviewed_record(plan_id,
"SHA256SUMS", raw)` in `_load_harvest`, and refuse an unlisted file under `g2a-root/` or `night-custody/`.

### MINOR-2. "Committed" means the issuing checkout's `HEAD`, not `main`

`scripts/issue_g2a_prefill_prompt_pin.py:157`. `git show HEAD:<path>` accepts whatever the current checkout
has committed, including an unmerged branch or a stale worktree. The ruling describes the anchor as records
committed on main. Against the stated threat (mistakes, stale paths) the realistic case is issuing from a
branch that carries an unreviewed record. Either state in the desk-day procedure that the issuer runs from a
checkout of main, or have the issuer require `HEAD` to be an ancestor of `origin/main`.

### MINOR-3. The issuer does not recompute the four-row summary from the receipt rows it authenticates

`scripts/issue_g2a_prefill_prompt_pin.py:592-707`. Only the selected rung's rows are recomputed from
bundles, and the summary row is never compared with those rows; rungs shorter than the selected one are
taken from the hash-bound summary as written. This predates the change and the summary is bound to the
committed harvest, so it is not a regression. For this record I closed the gap by hand: summary equals the
aggregation of the receipt rows, and every receipt row (all rungs) equals its archived bundle. Worth a
follow-up of a few lines so the issuer itself shows that no shorter rung qualifies.

### MINOR-4. End-state bindings of the ladder and the panel are not pinned by any test

`scripts/issue_g2a_prefill_prompt_pin.py:336-343` and `:777-780`; survivors M35 and M32. In SELECT mode the
receipt check repeats the ladder binding, so the tests cover it there; in end-state mode `_harvest_ladder`
is the only ladder-to-inventory check and the panel comparison is the only panel check, and removing either
leaves all tests green. The code is correct as written; a refactor could drop them silently.

### MINOR-5. Window-identity checks are not pinned independently

`scripts/issue_g2a_prefill_prompt_pin.py:273-277` and `:304-306`; survivors M11, M30, M31. Removing the
inventory's block-3 policy check, the inventory `window_id` check, or the chain `G2A_ROOT ==
/Users/edr/night-g2a/<plan_id>` check leaves all tests green (the policy case is masked because the frozen
plan check raises the same code). Each is one of several layers and the committed-record anchor stands in
front of all of them, so no wrong record gets through today.

### NIT-1. A systematic first RECOVER followed by a second RECOVER refuses in the two-record form

`scripts/issue_g2a_prefill_prompt_pin.py:386-391`. Registration §7 joins the two triggers with "or"; if both
hold (a recovery window was run although the first RECOVER was systematic) the issuer refuses two records
and accepts the first alone. Same pin; the second window's harvest is then not bound in the end-state
record. Contrary-to-protocol corner, untested (survivors M17a, M17b).

### NIT-2. Small test gaps

`tests/test_issue_g2a_prefill_prompt_pin.py:744-758`: no case with two distinct `b3w1` RECOVER records, so
the second-window label check alone is unpinned (M07c). `:760-789`: `--harvest` together with
`--recover-harvest` is untested (M22); the code refuses it (real-CLI probe). `:550-632`: a
`chain_summary_copy` status outside the two allowed values is untested (M36).

### NIT-3. The test double for the git anchor returns a different refusal code than production

`tests/test_issue_g2a_prefill_prompt_pin.py:64-65, 872`. The mocked `_committed_record_bytes` raises
`committed_window_record_unreadable:` for a missing record; production raises
`committed_window_record_missing` (confirmed on block-2 archives). The real git path is exercised by one
unit test (`:906-916`) and by my real-CLI runs.

### NIT-4. End-state record stores absolute archive paths

`scripts/issue_g2a_prefill_prompt_pin.py:395`. `recover_harvests[].path` is the machine path of each
archive, so the record's sha256 (which becomes `g2a_record_sha256`) depends on where the archive sits. The
sha256 of each harvest is the binding; the path could be the plan id.

### NIT-5. Live-root guard compares against the unresolved constant

`scripts/issue_g2a_prefill_prompt_pin.py:70`. `path.resolve()` is tested against the literal
`/Users/edr/night-g2a`; if that directory were itself a symlink the guard would not match. It is a real
directory today (checked).

## Ruling

PASS. Merge as is. MINOR-1 and MINOR-2 are the two I would schedule: each is a one- or two-line
strengthening that closes the anchor the orchestrator's ruling describes. None of the findings affects the
pin issued from the block-3 SELECT record, which I reproduced from the archive and the committed records.
