# 12 — Cold Fable gate ruling: which registration document row C1 binds the equivalence night to (packet 10, refuter 07 finding B-1)

Judge: cold Fable 5.1 seat, single non-interactive session, worktree
`/Users/edr/code/JouleWise-wt-coldgate-b1` at HEAD `1dddcfea573d85ee8facebc2b50dac412cb3b69f`.
Session opened 2026-09-11 14:29:47 UTC; last probe 14:31:44 UTC (`date -u`, executed).
No background tasks, no subagents, no network, no launchctl, no `~/night-custody`, no file modified
other than this record.

## 0. Contamination disclosure

- **Injected before I could refuse:** the harness placed into my system prompt the contents of
  the project `CLAUDE.md`, the user's global `~/.claude/CLAUDE.md`, and the memory index
  `MEMORY.md` (one-line pointers per memory, including checkpoint summaries naming PR numbers,
  "Ed's ruling (#316)", "night one = equivalence check vs r6", and the interpreter-cure thread).
  I did not open any of those files myself and I did not open any memory file they point to.
  None of that material is cited below; every conclusion rests on files I read in this session.
- **Not opened at all:** `RUN_STATE.md`, `CLAUDE.local.md`, `TASK_QUEUE.md`,
  `docs/council_log.md`, any `.claude/` skill, records 01–05 and 08 of this activation, and
  `docs/decision_log.md` outside the five permitted entries. For `docs/decision_log.md` I ran one
  `grep -n` for entry headers, which printed the header lines (only) of D-103, D-162, D-167 and
  D-176 alongside the permitted ones; I read no body text of those.
- **Incidental exposure:** `git log --format='%h %ad %s'` on the pre-registration and the runbook
  printed commit subjects (narrative one-liners about seat rounds and reviews). I used those only
  for the dates and hashes that F3 and F7 assert.
- **Record 07:** I read section 3 (lines 176–263) and the `grep` of its `##`/`###` headings. I did
  not read its other sections.

## 1. Trust anchors (executed, `shasum -a 256`)

| file | expected | observed | result |
|---|---|---|---|
| `docs/process/coldgate_charter.md` | `099de884…95d81` | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | MATCH |
| `…/10-packet-c1-registration-seam-B1.md` | `ea386cd7…1020` | `ea386cd7961915d12caa35302664b69972e2890586ce0ad65c9151c2204a1020` | MATCH |

Both verified before either file was read.

## 2. Fact verification (F1–F8)

**F1 — VERIFIED.** `joulewise/night_gate.py:1300-1326` (executed `sed -n 1295,1335p`):
`if plan.receipt_class in {"DIAGNOSTIC_NO_PACK", "REHEARSAL_STUB"}:` … `registration_text =
probes.read_text(plan.registration_path)` … `if registration_sha256 != D166_REGISTRATION_SHA256:`
→ `Refusal("night_refused_registration", f"registration sha256 {registration_sha256} does not
match D-166 registration", …)`; on match `rows["C1"].measured["detail"] = "D-166 registration hash
passed"`. Lines 32–41: the comment `# 2026-09-05: D-165 v2 relabel supersedes the v1 registration
digest`, `D166_REGISTRATION_SHA256 = ("dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265")`,
`D166_REGISTRATION_PATH = ("configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json")`.
The block has no branch on chain, plan field, or class beyond the two-class membership test.

**F2 — VERIFIED.** Executed digests: the d166 JSON hashes to `dfe55f8d…ac265` (equals the constant);
`configs/calibration/preregistration_d079_epoch_25g83_rev1.md` hashes to
`ca2430ddd04b4a95b3ea0420ecf4d0897e1d1409f9d4f9f102414d00c37a5da7` (does not).

**F3 — VERIFIED, with one provenance correction.** `docs/phase_2/derivation_night_runbook.md`
line 488: "The plan's `registration_path` points at this file (`NightPlan` in
`joulewise/night_gate.py`)"; line 760: "| `registration_path` | the committed pre-registration of
§0.5 |"; line 1238: "a `registration_path` equal to the committed pre-registration of §0.5";
lines 1283–1284: `assert plan.registration_path.endswith('configs/calibration/preregistration_d079_epoch_25g83_rev1.md')`;
line 2054: "`night_refused_registration` (the `registration_path` did not authenticate)".
Provenance: `git log -S` shows the §0.5 sentence arrived with `7a0511d6` (revision 4) as the packet
says, but the arm-block `assert … endswith(...)` first appears in `bc1d7ef9` (revision 5), not
revision 4. Immaterial to the ruling; recorded for accuracy. The consequence the packet draws is
correct: a plan armed as lines 1283–1284 require hashes to `ca2430dd…` and F1 refuses it.

**F4 — VERIFIED.** `scripts/gen_derivation_night.py:687`:
`"registration_path": "<repo-relative path of the committed pre-registration>",` (the example
plan the generator renders into `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`,
`RUNSHEET_PATH` at lines 49–51). `build_parser()` lines 833–872 has no pre-registration argument.
The wrapper's exports (lines 281–300) are the thirteen `:?required` chain variables (chain lines
58–70, executed) plus `SLOT_COUNT`/`SETTLE_S`/`SLOT_CADENCE_S`; the arm-time digest literals the
wrapper re-checks are the plan (`PLAN_SHA256`, line 396), the identity epoch and T1 bindings
(lines 399–405) and the tracked chain (line 411). No pre-registration digest anywhere. The chain
names the pre-registration only in comments at lines 12, 145, 211 (executed grep).

**F5 — VERIFIED.** `scripts/issue_calibration_acceptance_generation.py:305-319` (`check
--preregistration`: parses `preregistration_epoch_pins(text)`, appends
"MISMATCH — the registration is void", line 342 returns 3) and lines 1169–1181
(`prepare-candidate`: `if preregistration_sha256 != args.preregistration_sha256:` → "pre-registration
sha256 … does not match the pinned …; not issued"); `--preregistration-sha256` is `required=True`
at line 1796. Nothing on the night path reads the pre-registration (F4).

**F6 — PARTLY VERIFIED.** `01-harvest-evidence/night_plan.json` line 10:
`"registration_path": "configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json"`,
line 9 `"receipt_class": "REHEARSAL_STUB"`, line 8 `"plan_id": "rehearsal-20260911"`. The 09-09
plan and "the G2-a packet 04 plan" were NOT EXECUTED (outside the packet's custody inputs).
Consistent corroboration: `tests/fixtures/night_plan_v1_retired.json:12` and
`tests/test_launch_window.py:2379` carry the same d166 path.

**F7 — VERIFIED.** Runbook lines 526–528: "Record it once, at the first night's arm, and re-record
the same value at every night that follows — a change between nights is a stop, not a new pin."
`git log` on the pre-registration: `07995051 2026-09-10` and `12162263 2026-09-10 Record Ed's
ruling (directive issue 316): pre-registration revision 2 …` — both dated 09-10 (the packet says
"09-10/11"; the commit dates are 09-10). D-166's body (`docs/decision_log.md:10751-10758`) is
"the workload … `_v5` decode arm = real pinned prompts through the Qwen3 chat template"; the file
C1 hashes is `d166_dominance_criterion_registration.json` under `configs/campaigns/d117_contrast_v5/`
— the D-117 contrast campaign's dominance-criterion registration (D-165 body, line 10734: "the
dominance RATIO R ≥ 2 … is pre-registered into the `_v5` pack"). A different scientific object
from the D-079/25G83 calibration pre-registration, as the packet says.

**F8 — VERIFIED.** Record 146 (30 lines, read whole), decision 4: "blindness for this campaign
means 'every rule fixed before data', which this issue satisfies, not 'no one may look'"; heading:
"night one is an EPOCH-EQUIVALENCE CHECK, rule fixed here before any capture"; item 1: "run by the
merged chain exactly as built (PR #315 …). Nothing about the arm, the chain, the settle, the
census, or the dead-man changes."; item 3: "lands it through the normal PR gate as the smallest
possible change and reports the diff"; item 4: "the pre-registered three-night derivation proceeds
as written in configs/calibration/preregistration_d079_epoch_25g83_rev1.md … Night one COUNTS as
registration night one." Record 147 line 3: "This is Ed's ruling, not a magistrate amendment".
The D-102 evening addendum (`docs/decision_log.md:6700-6797`) transcribes the same words. The
packet's phrase "smallest change that preserves byte-identity of r6 and its pins" is a paraphrase;
the ruled words are "smallest possible change" (item 3) and "nothing about the arm … changes"
(item 1). I rule on the ruled words.

**Additional fact the packet omits (F9, executed).** The pre-registration's bytes are NOT final.
Lines 139 and 143 still read `Committed head pin sequence [SEQ] digest [DIGEST]` and `chain digest
[CHAIN_SHA256]`; line 136 `[MLX_VERSION]`; the file's own §"Fields filled at commit" (lines
279–284) says these are filled "at the first night's open". Runbook §0.5 lines 484–486 requires them
"committed inside H with … filled". So the digest of the document the night must be bound to does
not exist until the arm-day fill commit, and will differ from today's `ca2430dd…`. Any option that
pins that digest as a **code constant** (packet option (ii), first form) requires a code PR between
the fill commit and the arm on the same day, on the night-critical path. This fact decides against
(ii)-as-constant on its own and the packet should have carried it (§6 packet hygiene, MATERIAL:
omission of evidence bearing on the cost column of option (ii); it does not change the answer to
the Question, it sharpens it).

## 3. Packet hygiene (charter §6)

- MATERIAL: F9 omitted (above).
- NIT: F3 attributes the arm assert to revision 4; it is revision 5 (`bc1d7ef9`).
- NIT: F7 says the bytes changed "09-10/11"; both commits are dated 09-10.
- NIT: F8 paraphrases Ed's "smallest possible change" as "smallest change that preserves
  byte-identity of r6 and its pins"; the extra clause is the packet author's, not Ed's.
- The Question is compound (choose an option + arm-record contents + FAIL-route behaviour +
  WRITE_SCOPE + tests) but the parts are separable and the convening prompt asks for all of them;
  I answer each.
- Options are presented symmetrically with a cost line each; no cherry-picking found.

## 4. Analysis

**4.1 What the night actually consumes.** The chain and wrapper never read the pre-registration
(F4, F5). The captures' bytes cannot depend on the pre-registration's bytes. A night-time hash of the
pre-registration therefore protects nothing the data depend on; it attests only that the file at t0
equalled the file at arm. The pre-registration governs how the values are USED afterwards: the
equivalence rule on the PASS route (D-102 addendum lines 6720–6752) and the derivation on the FAIL
route (`prepare-candidate`, F5).

**4.2 What "rules fixed before data" requires.** It requires that the rule text exist, committed,
with a recoverable digest, before the first capture; and that the consumers of the data bind to
that digest. The repository already provides exactly this on both routes: the runbook's §0.5 pin
"into the arm materials" (lines 510–512, "carry the value in every night's arm record"), the
clean-tree check at §0.8 (line 517, "what makes this the committed bytes rather than a working-copy
edit"), and `prepare-candidate --preregistration-sha256` (F5). What is missing is not enforcement of
the pre-registration; it is that the runbook told the operator to put the pre-registration where
the gate expects the D-166 literal (F3), which loses the night (F1+F2).

**4.3 D-161 lens.** D-161 (`docs/decision_log.md:10684-10696`): "the operative test is MISTAKE vs
DELIBERATE (fail-closed for physics/evidence, pre-registration and operator mistakes;
deliberate-only guards retire)". The mistake class here is "the operator armed with the wrong path"
(exactly what the runbook currently instructs) and "the pre-registration's bytes moved between
nights". The first is caught by C1 at t0 — too late, night lost — and is better caught at the desk
by the arm assert and by a test on the generator's example. The second is caught at the desk by the
§0.5 re-record rule and, as a backstop, by `prepare-candidate` refusing issuance against night 1's
pin. A t0 tripwire ((ii) or (iii)) catches only a byte change between the arm and t0 of the same
night, by the sole operator, with no data consequence: a deliberate-only guard under D-161.

**4.4 D-175 lens.** D-175's eight arm conditions (`docs/decision_log.md:11433-11440`) bind the
plan to be validated "with `install_night_agent.sh --render-only` from the pinned measurement
checkout" and installed "from that checkout". Options (ii) and (iii) change `night_gate.py` or the
generator+chain in that checkout, so the measurement head H moves after the code PR and the arm
must be re-derived from the new H. Option (i) changes docs, the generator's example string, and
tests; the wrapper bytes the generator emits for a real plan do not include the example text
(`example_spec`/`render_region` are the docs-region path, lines 628–695), so H can move without
altering the wrapper or gate that the 09-09 rehearsal exercised.

**4.5 Ed's item 1 lens.** "run by the merged chain exactly as built … Nothing about the arm, the
chain, the settle, the census, or the dead-man changes." (ii) changes the gate that arms; (iii)
changes the chain wrapper and the generator. (i) changes neither.

**4.6 The "ceremony" cost of (i).** True: for this class C1 authenticates the D-117 dominance
registration, which is scientifically irrelevant to a calibration night. But C1 was that ceremony
on 09-09 and on rehearsal-20260911's plan (F6), the gate's own words are "D-166 registration hash
passed" (F1), and the tests `test_d166_registration_digest_is_the_ruled_literal` and
`test_d166_registration_file_hashes_to_the_ruled_literal` (`tests/test_night_gate.py:241-266`)
pin that meaning. Retiring the ceremony is a class-table redesign for a future lane, not the
smallest correct change before a 09-12 night. The packet's Question asks for the smallest correct
change; ceremony is a cost in elegance, not in soundness.

**4.7 Why not (ii) with a plan-carried digest.** `_PLAN_KEYS` (night_gate.py:109-135) is
exhaustive and tested (`tests/test_night_plan_writer.py:53`, `test_night_gate.py:338`); adding a
key touches `NightPlan.from_mapping`, the writer, the receipt validator, watchdog and install
tests, and the D-175 render-only validation. A plan-carried digest is self-attesting (author writes
path and digest) and duplicates what the arm record already carries. Not smallest.

## 5. Ruling on the Question

**Chosen: (i) DOCS + PLAN, with two additions that are still docs/tests only.** The equivalence
night's plan carries `registration_path = D166_REGISTRATION_PATH`; C1 stays as coded; the
pre-registration is bound to the night by the arm record's digest and by the desk consumers on
both routes.

**Additions to plain (i) (otherwise (i) leaves the PASS route unpinned):**
1. The arm record's pre-registration line is mandatory and includes the commit that holds the
   bytes (below), so "before" is checkable months later without trusting a working copy.
2. The runbook's §2.5 PASS-route procedure must instruct the magistrate to quote the arm record's
   pre-registration digest in the continuation addendum and to re-hash the committed file at H
   before applying the rule (a docs sentence; `scripts/epoch_equivalence_check.py` has no
   pre-registration flag — executed grep of its parser, lines 668–712 — and I do NOT rule that one
   be added: the rule constants it applies are the D-102 addendum's, whose commit is itself pinned
   in the arm record).

**Exact WRITE_SCOPE for the implementing PR:**
- `docs/phase_2/derivation_night_runbook.md` — §0.5 lines 484–489 (replace "The plan's
  `registration_path` points at this file" with: the plan's `registration_path` is the gate's
  class-registered D-166 literal; the pre-registration is bound by the digest pinned at lines
  510–528); §1.1 line 760 table cell; §1.4 line 1238; arm block lines 1283–1284 (assert
  `plan.registration_path == night_gate.D166_REGISTRATION_PATH` and that the file at that path in
  `$MEASUREMENT_ROOT` hashes to `night_gate.D166_REGISTRATION_SHA256`); §5 line 2054 gloss ("the
  `registration_path` did not hash to the D-166 literal C1 expects; the pre-registration is not
  what C1 checks"); §2.5 the one PASS-route sentence of addition 2; changelog line for revision 7.
- `scripts/gen_derivation_night.py:687` — example `registration_path` becomes the imported
  `D166_REGISTRATION_PATH` literal (import from `joulewise.night_gate`, already the module the
  plan schema comes from), plus the regenerated region in
  `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md` (the generator's `--check`
  mode will otherwise refuse).
- `tests/test_gen_derivation_night.py` — the example-plan test at lines 1040–1055 stops overriding
  `registration_path` with `configs/campaigns/example/registration.json` and asserts the literal.
- `tests/test_night_gate.py` — new defect-shaped tests T1/T2 below.
- Nothing in `joulewise/night_gate.py`, `scripts/night_chains/`, `scripts/run_night.py`,
  `scripts/issue_calibration_acceptance_generation.py`, or `docs/decision_log.md`.

**Defect-shaped tests (each fails on main at `1dddcfea`, by inspection of the current text):**
- **T1** (`tests/test_gen_derivation_night.py`): `GEN.example_night_plan(spec)["registration_path"]
  == night_gate.D166_REGISTRATION_PATH` and `sha256(read_text(REPO_ROOT / that path).encode())
  == night_gate.D166_REGISTRATION_SHA256`. Fails on main: line 687 is the placeholder string
  `<repo-relative path of the committed pre-registration>`.
- **T2** (`tests/test_night_gate.py`): extract the runbook's foreground arm block (the fenced
  python containing `assert plan.receipt_class == 'DIAGNOSTIC_NO_PACK'`, lines ~1275–1290), and
  assert it contains `registration_path == ` with `D166_REGISTRATION_PATH` and does NOT contain
  `preregistration_d079_epoch_25g83_rev1.md`. Fails on main: lines 1283–1284.
- **T3** (`tests/test_night_gate.py`): every runbook line matching `registration_path` (executed
  grep: 488, 760, 1238, 1283, 2054, 2141) either names `D166_REGISTRATION_PATH`/"D-166" or is the
  §7 symbol-index row (2141). Fails on main at 488, 760, 1238, 2054.
- **T4** (`tests/test_night_gate.py`, counterfactual, no constant mock): a DIAGNOSTIC_NO_PACK plan
  whose `registration_path` is the pre-registration, evaluated with a `read_text` that returns the
  real file's text, yields `night_refused_registration`; the same plan with the D-166 path yields
  C1 PASS with detail "D-166 registration hash passed". This one PASSES on main (it documents the
  seam rather than the defect) and is worth keeping as the reason T1–T3 exist; label it so.

**What the arm record must carry (every night, equivalence and any FAIL-route night):**
1. `plan_id`, the frozen plan's sha256 (the wrapper's `PLAN_SHA256` literal), and the plan's
   `registration_path` verbatim with the digest of that file in `$MEASUREMENT_ROOT`
   (`dfe55f8d…ac265` expected).
2. The pre-registration: repo-relative path, `shasum -a 256` of the committed bytes in
   `$MEASUREMENT_ROOT` after the §0.5 fields are filled (runbook line 515 command), the measurement
   head `H` (40-hex), and `git -C $MEASUREMENT_ROOT rev-parse H:configs/calibration/preregistration_d079_epoch_25g83_rev1.md`
   (the blob id, so the bytes are recoverable from history without the working copy).
3. The D-102 evening-addendum commit (the rule text the PASS route applies) and the runbook
   revision the arm followed, both as commit ids.
4. The wrapper chain sha256, identity-epoch and T1-bindings digests, `EVIDENCE_ROOT_ID` — already
   required by the runbook (lines 358, 596–617, 694–706); listed so the record is one table.
5. For night 2/3 on the FAIL route: item 2's digest re-recorded, with the words "equal to night 1"
   or a STOP.

**FAIL-route night 2/3 when the pre-registration's bytes change (F7), under (i):**
- At the desk, before arm: the re-hash in item 2 differs from night 1's → do not arm; this is the
  runbook's "a change between nights is a stop, not a new pin" (lines 526–528). The operator files
  the discrepancy and Ed rules; a new pin is never written silently. C1 is unaffected because it
  binds D-166, so nothing at t0 can misfire on this.
- If a night was armed anyway (operator mistake): `prepare-candidate --preregistration-sha256
  <night-1 pin>` refuses issuance ("does not match the pinned …; not issued", F5) and the
  registration is not consumed. Under D-161 that is the fail-closed pre-registration guard, and it
  fires where the data are used, not where they are captured.
- For comparison, under (ii)-constant the same change forces a code re-pin (forbidden by the stop
  rule) or a silent t0 refusal that loses a quiet window; under (iii) the wrapper's literal refuses
  at chain start with the same loss. Both convert a desk-time STOP with an operator present into an
  unattended night loss. The arm-record re-record is earlier and cheaper.

## 6. Disagreement with the lead's labelled disposition

The packet labels no preferred option; record 07 §3 names the cure as "either (i) … or (ii)" and
calls it "a design decision, not a typo fix". I concur it is design-bearing (which document the
night is bound to) and rule (i) with the two additions. I disagree with the packet's cost line for
(i) only in degree: "C1 becomes a ceremony for this class" was already true on every night to date
(F6) and is not a new cost of (i).

## 7. Severity register

- BLOCKER (confirmed, record 07 B-1): armed per runbook lines 1283–1284 the night refuses at C1.
  Cure = option (i) as scoped above; must land before any DIAGNOSTIC_NO_PACK arm.
- MATERIAL (packet hygiene): F9 omitted — the pre-registration's bracket fields are unfilled, so
  its final digest does not yet exist; any code-constant pin is infeasible before the fill commit.
- NIT ×3: F3 revision attribution; F7 date; F8 paraphrase.

## 8. NOT EXECUTED

- The 09-09 rehearsal plan and "the G2-a packet 04 plan" (F6 second and third clauses).
- Running the test suite (no tests were run; the defect-shaped tests are judged to fail on main by
  reading the current text they assert against).
- `scripts/gen_derivation_night.py --check` against the runsheet region.
- Any file under `~/night-custody`.

VERDICT: (i) — bind the plan to the D-166 literal C1 already enforces and pin the pre-registration in the arm record and at the desk consumers, because the night never reads the pre-registration, its final bytes do not yet exist (F9), and Ed ruled that nothing about the arm or chain changes and that the change be the smallest possible.
