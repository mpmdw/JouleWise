# Record 05 — round-3 seats, cold gate 2 (packet 06), close (activation ce7c57a9)

Branch `fix/2026-09-21-retained-root-terminal-markers`. Round-3 head `cfc56921` (record 03); seats sealed at `0d717dc1`; the commit that adds this record is the merge candidate (its sha is row 12 of the PR ledger). Main `ecefd46a` is merged in; `origin/main` unchanged at this record.

## §1 The two round-3 seats (record 03 §5; both on `cfc56921`, both detached)

| seat | verdict | executed evidence |
|---|---|---|
| Sol delta re-audit 4 (high), `04b-delta-reaudit-4-sol.md` | no blocker; should-fix F1: the ruled runbook sentence "a `Refused:` exit (for example a symlink anywhere under a root)" is FALSE (unrelated symlink under `night/` → `retained`, `pass`); nit F2: m16 (ruled reason assigned before the span rule, string unchanged) survives; closure A1-F2, A1-F3, A2-F1..F4 CLOSED; fidelity of every packet-02 text MATCH; m8/m12/m14/m15 KILLED; `gen_state --check` rc 0; kernel pointers resolve; recommendation: return to the gate | its V1–V8 |
| Blind Fable pedagogy-and-contract lens (high), `04-pedagogy-lens-round3.md` | rule-sentence audit: two FALSE — R6 (the same runbook sentence) and H1 (handbook preamble "the census classifies every process outside the caller's ancestor chain as foreign"; foreign = argv-matched `codex|claude|t3` PIDs minus the caller's ancestors, `arm_census.py:237`, `night_gate.py:90`); first-use test: nine FAILS (every process; plan span; older sibling plan; session root; custody root; arm; entry checkout; timing constants; diagnostic), two borderline; §4 PROPOSED wording, not applied | its probes S/N/W/Y and the single permitted unittest run |

Both are same-signature findings under packet 02's Q1 item 4, so no bench round 4: packet 06 (`06-coldgate-packet-retained-root-round3-return/00-PACKET.md`, exhibits A–D incl. the bench re-execution of the false R6: unrelated symlinks → `retained pass`; symlinked `courier.sent` → `Refused`) went to a second cold Fable judge paired with a second Opus contract-lens refuter (both detached, ~5 min).

## §2 Gate 2: ruling and refutation (magistrate synthesis)

Ruling `06-…/10-coldgate-fable-ruling.md`, refutation `06-…/11-opus-contract-refuter.md`. The refuter converges on every question; divergences and the disposition:

| Q | ruling | refuter | taken |
|---|---|---|---|
| Q1 R6 | three sentences naming exactly the inspected paths and that a symlink elsewhere does not refuse (probe E1, seven rows) | same substance, lists the directories differently | ruling text verbatim |
| Q2 H1 | preamble restated on the census population and the foreign rule (probe E2) | same substance; warns that "never foreign, whatever its ancestry" invites the false inference that such a process cannot stop the check (workloads also refuse, `evidence_night.py:801`) | ruling text verbatim; the refuter's caveat is recorded here (the sentence is true of "foreign"; a workloads clause would be magistrate-authored prose) |
| Q3 first-use | five glosses now (plan span + timing constants; entry checkout + older sibling plan; `custody_root`; session root; diagnostic), "every process" cured by Q2; deferred to a follow-up lane: "arm", "retained" (runbook/comment), "chain is open" | three must + four should now; "arm" and operator verbs to a lane | ruling: all five texts verbatim; lane registered as `ARM-VOCABULARY-GLOSSARY-01` (A266, rank 266, p3_tooling) with the ruling's goal sentence |
| Q4 m16 | order requirement WITHDRAWN as unobservable; string/classification pins (m12, m15) stand; no code or test change | same | withdrawn; Sol F2 closes "withdrawn by the gate" |
| Q5 closing | (a): no further seat pass; merge record carries fidelity MATCH ×8, the gate's two probe scripts re-run at the bench with row-for-row matching output, the filtered unittest, the full sharded replay, `gen_state --check` rc 0, the live `descendants()` run, the m16 disposition, the follow-up row id | (a) plus the bench re-execution (same as the ruling's item 2) | (a); every item is in §3–§4 |
| Q6 refusals | do not touch the `_refusal_paths` glob or C8; keep "a `Refused:` exit" (not `REFUSED:`/rc 2); reject `$PPID` and a local "arm" gloss; the corrected preamble must carry the packet 06 attribution | same list plus: do not "align" `TERMINAL_NIGHT_RECORDS` with the installer's superset | none of these edits was made |

## §3 The change after `0d717dc1` (docs, kernel, records only; code and code tests unchanged since `cfc56921`)

Texts extracted from the ruling file by script (`/tmp/magistrate-ce7c57a9/round3b.py`: blockquote under each marker, re-wrapped at 79 columns, no word changed) and checked back whitespace-normalized:

| text | file | fidelity |
|---|---|---|
| Q1 R6 sentence ×3 | `docs/phase_2/derivation_night_runbook.md` §0.7 | MATCH |
| Q2 H1 preamble | `docs/process/NIGHT_HANDBACK.md` pre-check step | MATCH |
| Q3.1 plan-span sentence | `docs/contracts/evidence_night_entry.md` item 4, before "A retained root whose plan span…" | MATCH |
| Q3.2 entry-checkout / sibling clause | contract item 4 | MATCH |
| Q3.3 `custody_root` clause | contract item 4 | MATCH |
| Q3.4 session-root sentences | handbook ruled text | MATCH |
| Q3.5 diagnostic parenthesis | handbook ruled text, last sentence | MATCH |

Also: kernel row A266 registered, `latest_report` → this record, regions regenerated, ID oracle 222 + 1 = 223; `git diff --check` clean.

## §4 Executed evidence (bench, this worktree, 00:0x PDT 2026-09-22, python3 3.14.7)

The gate's probe scripts, copied verbatim (`05a-gate2-probe-symlinks.py`, `05b-gate2-probe-census.py`) and run on this head:

```
$ python3 -B 05a-gate2-probe-symlinks.py /private/tmp/r3gate2-bench
S unrelated symlinks night/stray, <root>/unrelated, <root>/scratch/x -> [('S', 'retained')] verdict pass
W night/courier.sent is a symlink -> Refused: symlink/path collision: …/night-custody/W/night/courier.sent
N night/ is a symlink -> Refused: symlink/path collision: …/night-custody/N/night/courier.sent
K night_plan.json is a symlink -> Refused: symlink/path collision: …/night-custody/K/night_plan.json
Z the root directory itself is a symlink (ancestor of the plan) -> Refused: symlink/path collision: …/night-custody/Z/night_plan.json
R7 refusal-7.json regular + result.json symlink -> Refused: symlink/path collision: …/night-custody/R7/night/result.json
Q refusal-02.json is a symlink (refusal-glob hit) -> Refused: symlink/path collision: …/night-custody/Q/night/refusal-02.json
$ python3 -B 05b-gate2-probe-census.py
own_pids (100, 200) foreign_pids (300, 600) diagnostics ()
outside ancestor chain of 200: [1, 300, 310, 400, 500, 600] -> foreign: [300, 600]
unreadable hit 700: foreign (300, 600) diagnostics ('pid=700 unknown: no exact record',)
```

Row for row equal to the ruling's E1 and E2. Filtered unittest on this head:

```
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_evidence_night -k retained -k discovery -k span -k realpath -k deep_json
Ran 9 tests in 13.254s
OK
```

`python3 -B scripts/gen_state.py --check` rc 0; `tests.test_gen_state` 44 tests OK. The live `descendants()` run (Q5 item 4) is in record 03 §4 verbatim (root 53476, child 53477, grandchild 53480, tree empty after TERM). Full sharded replays: `shard_tests.py --workers 4` on `cfc56921` (code identical to this head) and on this head, plus the quick tier on this head — tails in §6.

## §5 Terminal review (magistrate, full session context, of the merge candidate)

Read in this session: the code diff `9e0a4995..cfc56921` for `joulewise/evidence_night.py` and `tests/test_evidence_night.py` (record 03 §3; the retained reason is assigned only after the span rule, `RecursionError` is caught at the parse boundary, the three regressions are defect-shaped and their kills are reproduced above and in the seat), the three document diffs at both rounds (every sentence is gate-supplied, fidelity MATCH, and each rule sentence has an executed probe in a ruling or in records 03/05), the kernel diff (A230 retired to the Completed Queue Items table with A263; A264, A265, A266 registered with resolving pointers; regions regenerated). Classification unchanged from the packet-05 ruling: open chain → ACTIVE; terminal record incl. `_refusal_paths` names → retained unless the plan is unparseable / foreign `custody_root` (UNKNOWN) or the span is active (ACTIVE); verdict `pass` only when every row is `retained`. Real roots on this machine: three harvested nights, all `retained` (record 02 exhibit A1 Q3). Nothing in the candidate touches arming, the installer, the watchdog, or a measurement root. MERGE, on the green replay and quick tier of §6 and the hosted matrix per the post-merge CI ruling.

## §6 Replay tails (appended before merge)

Both replays ran detached at the bench (`scripts/shard_tests.py --workers 4`, python3 3.14.7), then `scripts/quick_suite.py --tier touched --since 9e0a4995`; logs `/tmp/magistrate-ce7c57a9/12-…15-…`.

Round-3 head `cfc56921` (code identical to the candidate), started 23:40 PDT, 68 min:

```
WORKERS SUMMARY shards=4 modules=245 tests=6717 failures=0 errors=0 skipped=109 failed_shards=none result=PASS
shard rc=0
QUICK SUMMARY tier=touched modules=173 excluded=72 failures=0 seconds=767.801 result=PASS
quick rc=0
```

Merge candidate `36ddbb37` (this record's first commit), started 00:07 PDT, 61 min + quick 11 min:

```
SHARD SUMMARY index=1/4 modules=62 tests=1822 failures=0 errors=0 skipped=17 result=PASS
SHARD SUMMARY index=2/4 modules=60 tests=1453 failures=0 errors=0 skipped=6 result=PASS
SHARD SUMMARY index=3/4 modules=62 tests=2332 failures=0 errors=0 skipped=80 result=PASS
SHARD SUMMARY index=4/4 modules=61 tests=1110 failures=0 errors=0 skipped=6 result=PASS
WORKERS SUMMARY shards=4 modules=245 tests=6717 failures=0 errors=0 skipped=109 failed_shards=none result=PASS
shard rc=0
QUICK SUMMARY tier=touched modules=173 excluded=72 failures=0 seconds=644.039 result=PASS
quick rc=0
```

Hosted matrix on `36ddbb37` (PR #379): every job green (build, changes, fences, installed-wheel, quick, gate-ledger after the ledger cells were reduced to one `RUN <path>` each, calibration-exits-exclusive, calibration-writer-crash-matrix-exclusive ×2, test ×6). The commit that appends this section is docs-only (this file); it is the final head named in ledger row 12; per the post-merge CI ruling the hosted run on it is post-merge confirmation.
