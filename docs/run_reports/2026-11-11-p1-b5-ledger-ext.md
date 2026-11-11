# Paper 1 Block 5 ledger extension — rounds 1 and 2

2026-11-11 · Sol seat `p1-b5-ledger-ext` · no network or delegation.

**Current handoff:** [Round 2](#round-2--pinned-descendants-authorized) completes
this reader's extension: 618 further rows, 1,419 total, with all previously
committed rows unchanged. The new table commit is
`87a698c0f90aec5c037ed38ced586855be1bdbfa`. Opus cold review and lead
adjudication remain owed. The round-1 access hold below is retained as history.

## Round 1 — historical partial pass

**Result:** appended 263 independently checked aggregate/word rows, physical
TSV lines 540–802. No new numeric or factual mismatch. The full assignment is
**incomplete** because the prompt also forbids every real `restricted/`
directory, while its required pinned disclosure/projection files are under
`dry-m/dry-run/restricted/`. I asked for a ruling before touching that subtree;
no answer had arrived when this report was written. Independent work from
the explicitly allowed, non-restricted RC file is committed for review.

## Authority and commits

- Clean starting HEAD and `origin/main`: `41c7a14440131f6f836f266e9ce898232deccab3`.
  The requested local branch already existed at that HEAD:
  `analysis/2026-11-11-b5-ledger-ext`.
- Read RL-3, RL-38, RL-39, RL-41, RL-42 and RL-52 verbatim from
  `origin/audit/2026-11-10-fable` at
  `a23943cf1de24e4a4c53a8cc208231a413cbe9de`.
- Read seat 12's report from `origin/docs/2026-11-11-paper1-b5-fill` at
  `e5fd296715f21c7c3792e4f9743b7494b07813ec`. Its pending list defines the
  extension; the paper fill itself is not this seat's work.
- **New extended-table / print-authority candidate commit:**
  `b9ea4cd111be1c6faae4f4a990ed1b1121e711da`,
  `docs: append independently checked RL-52 ledger rows pending access ruling`.
  It contains the extended TSV, SHA-256
  `913423195a6981827b041d78cb1675da7414cf7d43c0a39456334db73d631004`.
  This is not a claim that RL-52's full gate has closed: the remaining sourcing,
  the new Opus cold review and lead adjudication are still owed. The original
  print authority remains `0b8763f0a8291bfa5d47fdc18aa64ef3aa33ec1b` for its
  unchanged 538 rows. This report is committed separately so it can name the
  immutable extended-table SHA.
- No push, merge, publication, external message or integration authorization.

Mission M0 was applied proportionately: AGENTS/CLAUDE, the playbook,
orchestration, the source-of-truth map, stop-card/lane/workspace pointers,
queue intake and Do-Not-Do-Yet, D-165/D-168 and targeted decision-log authority,
the registered Block 5 analysis plan and registration, earlier reader reports
and scripts. No stop card was active. This explicit [AGENT] assignment takes
priority over ordinary queue selection. Coordination state was preserved as
the user requires. The speed toolbox was read with `git show origin/main:`;
this work changes no throughput, batching, caching or measured-episode behavior.

## Every custody file opened, with hashes

Exactly **one** custody file was opened. No custody directory was inventoried.
Every inspection/replay authenticated its bytes before JSON parsing and
re-hashed the same file at the end, including failed development runs, using
a `finally` block. All before/after hashes were equal.

| Alias and exact file | Expected SHA-256 (RESULTS §0) | Before and after SHA-256 |
|---|---|---|
| RC: `/Users/edr/jw-b5-custody/release-check-final-20261108T0942Z/recompute.json` | `c06ee7c8cbf85a68dcebc24a73e0372fd6f8d825fc3acf30ec352304dd93cacc` | `c06ee7c8cbf85a68dcebc24a73e0372fd6f8d825fc3acf30ec352304dd93cacc` |

The new reader permits only this root, basename, alias and full digest; it
refuses other sources before filesystem access. No dry-m file or real
restricted directory was opened, listed or statted. No other home path,
night custody/archive, raw measurement file, Block 6, BYTES or ALIGN v4 output
was accessed. Paths named inside repository or custody records stayed text.
Only Git accessed the permitted shared object store. No analysis pipeline,
repository recomputation/comparator, hardware measurement, model load/download
or long-running-job inspection/control was performed.

## Changes and findings

Changed files:

- `docs/analysis/b5/rederivation.tsv`: appended 263 rows; its original header
  and all 538 original rows are byte-identical to `0b8763f0a`.
- `docs/analysis/b5/REDERIVATION.md`: partial-extension notice and the required
  **Rows not printed by RESULTS.md (RL-52)** section, with row ranges and limits.
- `docs/analysis/b5/hand_check_rl52.py`: data-free, stdlib independent arithmetic,
  pinned RC-only reader, rounded serialization and append-only writer/checker.
- `docs/analysis/b5/hand_check_phase2.py`: confines historical RL-41/RL-42
  replay/counts to the original 538 rows and preserves appended bytes on write.
- `docs/analysis/b5/opus_coldreview_check.py`: explicitly checks only its original
  538-row scope in repository mode; it does **not** review new rows.
- `tests/b5_analysis/test_hand_check_phase2.py`: nine new synthetic/boundary/
  precision checks; 27 tests total. No new test module, so no timing-file edit.
- This report.

The new rows include eight R, their 16 unguarded numerator/denominator terms,
eight n and pass words, four comparative floors, and four R_cm with all their
operands and n. All eight R pass; three R_cm fail; branch B follows. There is
no nonpositive denominator. The shared trace-sweep widths are pinned inputs,
as in the accepted earlier hand checks; scalar member energies do not
independently reconstruct those trace sweeps.

For each target cell the extension checks B's three kind averages, the
first-kind attaining run and minimum, removed-unit codes/counts, per-cell
battery/load numeric lines and counts, and cross-session inputs/agree booleans.
The other two B kinds have no unique attaining run: interval-support
interpolation is zero and the drift kind is constant within the session.
The battery-assist counts are copied recorded inputs, not re-detected current
flags; numeric without-assist results are conditional on those recorded inputs.
Load restoration requires every removal code to be load-only. The nine removed
contrast quads have their code unions as row values. The extension also checks
all three packs' model-specific request-level ρ summaries and the ALPHA/BETA
gross-family NEG-8 bound terms/counts/allowances.

Cross-session agreement is computed, not a recorded judgment:
`abs(G-F) <= hypot(h_G,h_F)`, with G/h_G from GAMMA quad-arm means and F/h_F from
the fixed 0.2/0.8 floor-session estimator. The four deltas agree at the precision
of physical rows 169–172. Direct equality to DISC's agree/differ leaves remains
pending; the new rows currently source RC's agree booleans.

All re-derived numeric values are committed at ledger precision, with residuals
to two significant figures. No member energy/current/temperature/timing values
or series were written outside custody. Unit IDs, code sets and an attaining-run
name are the authorized provenance fields, not a member-value release.

## Counts, every MISMATCH and source-outside-unseal list

| Ledger word | New rows | Whole ledger |
|---|---:|---:|
| exact | 118 | 379 |
| within-rounding | 137 | 393 |
| recorded-judgment | 8 | 14 |
| single-source | 0 | 14 |
| MISMATCH | 0 | 1 |
| source-outside-unseal | 0 | 0 |
| Total | 263 | 801 |

**Every MISMATCH:** original physical row **249**, the unchanged RL-39
“four different causes” wording erratum (four losses, three distinct causes).
No new row is MISMATCH. During development, a midpoint-ID selector incorrectly
expected a trailing hyphen; correcting this hand-check script's selector made
the gross NEG-8 arithmetic agree. No source, analysis code or RESULTS was repaired.

**Source-outside-unseal list:** none established in this partial pass. No file
outside the two roots is needed by the arithmetic completed here. The blocked
files below are *inside* a named root but also inside the separately forbidden
real `restricted/` subtree. Assigning them `source-outside-unseal` or MISMATCH
would confuse an authority question with a geographic or factual finding.

## Verification

All final commands/checks below passed:

| Command/check | Result |
|---|---|
| `python3.13 -B -m unittest tests.b5_analysis.test_hand_check_phase2` | Baseline 18 passed; final 27 passed, 0.246 s. Includes immutable prefix, access refusal before stat, pin-drift refusal, precision, mixed-code load restoration, kind averages, quad identity, arm-level scatter and quantiles. |
| `python3.13 -I -B docs/analysis/b5/hand_check_rl52.py --write` | Initial append: 263 rows, expected words, before/after RC hash equality. |
| `python3.13 -I -B docs/analysis/b5/hand_check_rl52.py` | Replayed member arithmetic; extended ledger byte-identical; RC hash unchanged. |
| `python3.13 -I -B docs/analysis/b5/hand_check_phase2.py --repo-only` | Original 538-row disposition/counts and 157-row hand table preserved; new rows explicitly outside this historical check. |
| `python3.13 -I -B docs/analysis/b5/opus_coldreview_check.py --repo-only` | Original review residuals/dispositions/hand links pass; no new Opus review claimed. |
| In-memory `compile()` on four changed Python files | Passed, no bytecode written. |
| Independent table/protected-file audit | Original prefix byte-identical; 263 unique new keys; all new numeric residuals at most two significant digits; total 801 rows; RESULTS and protected files unchanged. |
| `git diff --check` / `git diff --cached --check` | Passed for the extended-table commit. |

Only the named unittest module ran, sequentially, with cumulative test time far
under 20 minutes. No full suite, pytest, model or hardware test was run. No MLX
code changed and no native MLX test is needed for these stdlib scripts.

`RESULTS.md` stays SHA-256
`fb5f81e8741532d79b059b2ca7c44b1c479f0f983c28527ab6e2511d7dfb6f55`.
`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`,
`tests/test_gen_state.py`, `scripts/test_timings.json`, `phase2_sources.tsv`
and `hand_checks_phase2.tsv` were preserved; no kernel task was registered.

## NEEDS_RULING — authority gap and next exact step

**Question:** does the RL-38 exception authorize the exact hash-pinned
descendants of `/Users/edr/jw-b5-custody/dry-m/dry-run/restricted/`, despite
the additional instruction “NEVER … any real restricted/ directory”?

**Options considered:** (1) permit only the exact pinned FILL, DISC, EXC,
projection and other phase-2/3 source files needed by this assignment inside
the two roots; (2) keep the real restricted subtree closed and hand back the
remaining work. Earlier seat-4 reports treated those pinned descendants as
authorized, but that history does not settle this prompt's explicit conflict.

**Recommendation:** explicitly authorize option 1, restricted to the named
pins and with the same hash-before/after and no-path-following conditions.

**Blocked work:** primary disclosure/projection equality for the new rows;
ALPHA/BETA attempt verdict/cause/count disclosures; arm hazard measurements,
physics counts and stage temperatures; monitor costs; floor-limit class leaves;
complete NEG-8 two-family verdict, lost/spare/midpoint/corpus-cap/reason lines;
DISC agree/differ leaves. Some per-cell load lines may be refusals in DISC,
with only uncompared numeric values in RC; this must be sourced rather than
guessed. No composite placeholder is declared fully fillable by this report.

**Next exact step:** lead answers the access question in a resumed prompt.
Then authenticate the necessary pinned files, append the remaining source/rule
rows without changing the already committed rows, re-hash every opened file,
record a successor extended-table commit, and obtain the RL-52 Opus cold review.
Lead audits this seat's event log and adjudicates the extension before the
second fill. AGENTS.md requires compliant early return for an authority gap:
“Do not guess and do not invent: finish independent authorized work, then stop
with a blocking question.” This report is that handoff, not a completion claim.

## Round 2 — pinned descendants authorized

2026-11-11 · resumed from clean HEAD
`aeab066c16ea10a0f4a7fbc78d0ca8615a0502ff` on the same named branch.
The lead's resumed brief prospectively authorizes descendants of the two
RL-38 roots, including the real `dry-run/restricted/` subtree, **only for
files already pinned in RESULTS §0 or the seat-4 phase-2/3 opened-file tables**.
That resolves round 1's authority question. It grants no directory inventory,
unlisted-file access, custody writes or path following.

**Result:** appended **618** rows at physical TSV lines **803–1420**. The full
ledger has **1,419 rows**. The header, 538 original rows and 263 round-1 rows
are byte-identical to `b9ea4cd111be1c6faae4f4a990ed1b1121e711da`.
No new numeric or factual mismatch and no source-outside-unseal row was found.
This completes the Sol reader's assigned extension; it does not substitute
for the prescribed Opus cold review or the lead's event-log audit/adjudication.

### New print-authority commit

**Extended-table / new print-authority candidate:**
`87a698c0f90aec5c037ed38ced586855be1bdbfa`,
`docs: complete RL-52 ledger sourcing and independent round-2 checks`.
That immutable commit contains the extended table, documentation, data-free
reader and synthetic tests. The table's SHA-256 is
`5546bfd273fee3fc1f5277fed6d8ea8492f6ee02465541e10ba00a4363026008`.
This report follows in a separate commit so it can name the table commit.
The original 538-row print authority remains `0b8763f0a`; the extension's
final acceptance/print licence is the lead's after the Opus review.

### Every custody file opened, with hashes

Exactly **six distinct custody files** were opened during round 2. This table
covers structural inspections, development failures, initial serialization
and final replay. Every open hashes bytes before JSON parsing, requires the
full expected digest, and re-hashes the opened file in `finally`. All observed
before/after hashes equal the expected hash below. No directory listing or
inventory was performed. No other custody file was opened.

| Alias | Exact path | Expected = every before = every after SHA-256 |
|---|---|---|
| RC | `/Users/edr/jw-b5-custody/release-check-final-20261108T0942Z/recompute.json` | `c06ee7c8cbf85a68dcebc24a73e0372fd6f8d825fc3acf30ec352304dd93cacc` |
| FILL | `/Users/edr/jw-b5-custody/dry-m/dry-run/restricted/outputs/a29c6cf296199d70d9154719608ad21c07e08fda077224aa05a914b5ecf1f9b4-results-fill-input.json` | `a29c6cf296199d70d9154719608ad21c07e08fda077224aa05a914b5ecf1f9b4` |
| DISC | `/Users/edr/jw-b5-custody/dry-m/dry-run/restricted/disclosures/77be1a3ed3a851206a0762334cbdeaab5b40e83e3d9fcdbcf404da5e4d871f6a.json` | `77be1a3ed3a851206a0762334cbdeaab5b40e83e3d9fcdbcf404da5e4d871f6a` |
| EXC | `/Users/edr/jw-b5-custody/dry-m/dry-run/restricted/finalized/analysed-attempt-exclusions-a9954365ef44c1b8a65603dd0ba52140109b45569fc795783ca6663d54586f46.json` | `a9954365ef44c1b8a65603dd0ba52140109b45569fc795783ca6663d54586f46` |
| PROJ-A | `/Users/edr/jw-b5-custody/dry-m/dry-run/restricted/outputs/ed3cadb1f0ac2fc137efab3f4528702c704055ffa5bdf24399c335081570f5bf-projection-alpha.json` | `ed3cadb1f0ac2fc137efab3f4528702c704055ffa5bdf24399c335081570f5bf` |
| PROJ-B | `/Users/edr/jw-b5-custody/dry-m/dry-run/restricted/outputs/db6d525129f90ef24bb46f83ab5e66283424970c743f35d322c8961f9b683e2e-projection-beta.json` | `db6d525129f90ef24bb46f83ab5e66283424970c743f35d322c8961f9b683e2e` |

RESULTS §0 supplies full RC/FILL/DISC/EXC pins. PROJ-A/B use the **full** hashes
in seat 4's phase-2 report and `phase2_sources.tsv`, with equality to the
content-addressed filenames; §0's shortened prefixes are not treated as full
pins. No REC read was needed. The reader refuses all other aliases before
filesystem access and rejects symlinks/path traversal through the earlier
independent reader's boundary helper. Paths named inside records stayed text.

### Coverage, findings and limits

The row-range/source map is in
[REDERIVATION.md, round 2](../analysis/b5/REDERIVATION.md#round-2-access-clarified-reader-extension-complete).
The registered rules were read from analysis-plan §§4–9, registration §0.12,
D-078/D-165/D-168 and the adapter contract; RL-3/38/39/41/42/52 and seat 12's
pending list were reread at the brief's exact refs. No source policy was
re-decided. A narrow search of the disclosure producer identified only the
`reference_spare` output label, to check a zero-record count; none of that
producer's numerical code is imported or used for arithmetic.

- **Dominance:** independently reconstructs all eight R and four R_cm
  operands/n; direct DISC rows agree. All eight R pass, three R_cm fail, branch
  B and the unlicensed dominance sentence are reproduced. The four comparative
  floors and FILL's class/source words agree. The attribution floor class is
  kept distinct from the dominance branch.
- **ALPHA/BETA:** individual attempt/cause records match the committed index;
  per-cause multiplicities are counted. Analysed succeeded/planned counts are
  recounted from pinned member records. Earlier non-null counts are labelled
  single-source disclosures; no failed attempt is re-analysed. Removed-unit
  code/family unions, physics counts, monitor cost, arm readings/verdicts,
  per-cell battery/load lines and model-specific ρ summaries all have rows.
- **B:** PROJ-A/B's three kind averages agree with fixed 0.2/0.8 member
  arithmetic. The attribution-floor maximum's attaining run/minimum agree.
  The interpolation and drift kinds are constant and have no unique attaining
  run; no such fields are invented.
- **Cross-session words:** the registered `abs(G-F) <= hypot(h_G,h_F)` rule
  reproduces DISC's four booleans and sentences: three agree, one differ (8B
  prefill). Original physical rows 169–172 are checked in the round-1 replay.
  These are computed words, never recorded judgments.
- **NEG-8:** both families are hand-checked from member values, including the
  idle-subtracted rail request deltas in RC's whole-machine member records.
  Envelope/Student bounds use realised endpoint sizes; screen words require
  both families; allowance includes midpoint excursion. Reference losses,
  midpoint presence, measured-spare-record and deciding-spare counts, corpus
  losses and desk cap are checked over stored memberships/codes. Both floor
  sessions have no disclosed measured spare records and no deciding spares.
- **Contrast removal:** nine per-quad code/family sets and all 15 triggering
  members' code/family sets are row values, not only notes.

**Registered refusal, preserved:** BETA decode's load-correlated line has
`status=refused`, `code=whole_window_verdict_provenance_invalid`. Its round-1
RC numeric result remains independently hand-checked and **uncompared**.
ALPHA prefill and BETA prefill do have agreeing registered numeric lines;
ALPHA decode has no load-triggered line. The fill must state the BETA refusal
beside the uncompared number, rather than imply the registered program
computed/compared it. This is not a numerical mismatch or a repair request.
The status/code rows are exact **sourcing of metadata**; this reader does not
independently reproduce the provenance predicate that caused the refusal.

Arm readings/verdicts, battery-assist counts, attempt verdict/cause leaves and
harvest stage flags remain attributed recorded judgments. Monitor cost and
earlier attempts' non-null count leaves carry the disclosure-only label.
Temperature rises/plateaux/producer flags are calculated from readings;
physics/cause counts are over stored flags. Shared trace-sweep widths and
clean-corpus selection remain pinned inputs, as in the accepted earlier
reader. No raw trace integration, clock refit, raw eligibility revalidation,
hazard re-detection or raw retry-log replay is claimed.

No member-level energy, temperature/current/timing series or new per-member
value was committed. IDs and code sets are the requested provenance fields;
temperature outputs are stage aggregates/words, never the reading arrays.
Residuals are two significant figures, classified before rounding.

### Full counts, every MISMATCH, source-outside-unseal

| Ledger word | Round 2 | Combined extension (rounds 1+2) | Full ledger |
|---|---:|---:|---:|
| exact | 352 | 470 | 731 |
| within-rounding | 162 | 299 | 555 |
| recorded-judgment | 84 | 92 | 98 |
| single-source | 20 | 20 | 34 |
| MISMATCH | 0 | 0 | 1 |
| source-outside-unseal | 0 | 0 | 0 |
| Total | 618 | 881 | 1419 |

**Every MISMATCH:** unchanged physical row **249**, RL-39's already ruled
"four different causes" versus three distinct causes in four losses. No new
MISMATCH. **Source-outside-unseal list: empty.** No row in this assignment
requires another file once the accepted recorded/single-source limits are
applied. The real-`restricted/` authority hold is resolved, not relabelled as
a source mismatch.

### Verification and protected boundaries

| Command/check | Result |
|---|---|
| `python3.13 -B -m unittest tests.b5_analysis.test_hand_check_phase2` | Baseline 27 passed; final 37 passed, 0.240 s. Ten new synthetic tests cover exact alias/full-pin access, hash-before-parse and final rehash, changed-prefix/append refusal, unequal NEG-8 endpoints/midpoint/thresholds, temperature thresholds, battery-inclusive ρ and impossible negative-energy spread exclusion, and no label masking a disagreement. |
| `python3.13 -I -B docs/analysis/b5/hand_check_rl52_round2.py --write` | Appended 618 rows; all six before/after hashes equal their expected pins. |
| `python3.13 -I -B docs/analysis/b5/hand_check_rl52_round2.py` | Final replay byte-identical; round-1 arithmetic and immutable 801-row prefix also reproduced; six end hashes unchanged. |
| `python3.13 -I -B docs/analysis/b5/hand_check_phase2.py --repo-only` | Original 538-row counts/placement and 157-row hand table unchanged. |
| `python3.13 -I -B docs/analysis/b5/opus_coldreview_check.py --repo-only` | Original review residuals and hand-table links unchanged; explicitly no review of extension rows. |
| Independent in-memory audit/`compile()` | 801 committed rows byte-identical; 618 unique new keys; all new residuals at most two significant figures; changed Python compiles; protected files unchanged. |
| `git diff --check` and `git diff --cached --check` | Passed for the table commit. |

Only the named unittest module ran, sequentially. Cumulative unittest time was
under five seconds, far below the brief's 20-minute limit. No full suite or
pytest was run, under the standing blinded-job constraint. Development caught
two reader-selector errors (projection model aliases and failed roster members
without request energies); they were fixed before table serialization. Both
failed invocations re-hashed all opened files. No source was changed to make
a check pass.

Changed files in round 2: `rederivation.tsv`, `REDERIVATION.md`, the new
`hand_check_rl52_round2.py`, the existing
`tests/b5_analysis/test_hand_check_phase2.py`, and this report. No new test
module was added, so `scripts/test_timings.json` was not edited. Historical
round-1 script remains scoped to its original append; the round-2 checker is
the current complete extension replay and includes that arithmetic.

RESULTS remains SHA-256
`fb5f81e8741532d79b059b2ca7c44b1c479f0f983c28527ab6e2511d7dfb6f55`.
`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`,
`tests/test_gen_state.py`, `scripts/test_timings.json`, `phase2_sources.tsv`
and `hand_checks_phase2.tsv` are unchanged. No kernel task was registered.
No network, custody write, model load/download, Block 5 pipeline,
repository recompute/comparator, hardware/MLX operation, other unseal child,
night custody/archive, Block 6, BYTES or ALIGN v4 output was accessed.
No process inspection/control was performed against the long-running job;
no persistent test fixture was launched. No native MLX test is required for
these stdlib-only changes.

**Next exact step:** lead assigns the RL-52 Opus cold review of this table
commit/independent hand checks under the same six pins, audits this seat's
event log, and adjudicates. Then the second fill can cite the accepted new
authority. No new research ruling is requested by this reader; the recorded
limits and registered refusal above must remain visible to the reviewer/fill.
Local commits only; no push, PR, merge or publication was attempted.
