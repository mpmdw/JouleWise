# S-0 CLONE-PROOF RUNSHEET R4 — JouleWise `_v4` transaction

This is a bench runsheet, not an execution transcript. The magistrate executes
it in the throwaway clone defined in §1.1 and reads every transcript. It never
uses or reads `/Users/edr/JouleWise-measurement-20260818`.

R4 supersedes `s0-runsheet-r2.md` and the r3 draft, which was never executed.
R2 and its three dated amendment blocks are retained unchanged as the record;
nothing in them binds execution any more. r3 exists only as commit `926826b` on
this branch — it was refused by both ratification seats and no estate ran it.

---

## Revision history

**r6 (2026-08-25): probe-reachability cure.** A revision of this file, not a new
instrument: the filename, the estate layout and every record below stand
unchanged. Estate 9 (BASE `5a034f84`) ran the §4 probe battery continue-on-fail
and six probe blocks failed with ONE shared signature — the refusal each probe
was written to elicit is masked by a gate that fires EARLIER in the real
execution order, so the probe stopped on a refusal it was not testing for and
the gate under test was never reached. The six: `104-plan-current`,
`105-plan-sibling`, the `110-*` class block (at `freeze-json`), `119-manifest-binding`,
`121-s6-r1` and `123-c-to-s-later-rewrite`. None of them impeaches an estate-9
green: every failure is instrument-side probe SHAPE, and no estate precondition
was false — the magistrate dispositions them as §6 ordinary defects and sends
estate 10 to run the cured battery at the merged head.

Authority: the read-only Sol xhigh reachability consult and the ruling over it,
custodied at `docs/process_traces/2026-08-25-probe-reachability/`
(`01-sol-consult.md`, `02-MAGISTRATE-ADJUDICATION.md`). The consult traced each
probe's ACTUAL first-firing gate in `joulewise/arm_readiness.py` at `5a034f84`,
re-derived a mutation that reaches the INTENDED gate from the same case base,
and wrote the replacement block; the ruling accepts all six verbatim. What
changed:

- **`window_id` → `evidence_root_id` in every plan-tree mutation** (`104`,
  `105`, `121`, and the `110-*` `plan-json` class). `window_id` is one of the
  six terms `_pack_identity()` binds (`arm_readiness.py:4959`), and freeze
  replay compares pack identity at `:6513-6521` before R1 ever runs.
  `evidence_root_id` is manifest-visible and identity-invisible: see §4(c).
- **`105` changes VEHICLE.** Its original claim — that the FIRST pack's replay
  refuses a mutation to a SIBLING pack's plan tree — is unreachable by design,
  because a pack's R1 manifest derives its dependencies only from that pack's
  own evidence sources (`arm_readiness.py:4280-4309`). Estate 9 returned
  `rc=0`/`PASS`/`mutated=false`, which is the mechanism behaving correctly. The
  probe now mutates the SECOND pack's plan tree and replays the SECOND pack; the
  family-wide-allowlist goal the old claim was reaching for stays with the
  candidate-shape triplet `106-*`/`107-*`/`108-*` in §4(d).
- **`110-*` collapses to ONE block with EXACT per-class assertions** — each
  class's `reason_codes` LIST and `detail` STRING are compared for equality,
  which strictly subsumes r5's substring greps and its two separate absence
  sweeps. Three class expectations were re-derived: `freeze-json` now recomputes
  its sidecar and expects `readiness_freeze_receipt_mismatch` / "existing freeze
  receipt is not plan-pinned" (**amended in the r6 fix round** — the consult
  predicted the exactness detail from `:6503-6506`, but the plan-pin filter at
  `:6848-6862` discards the tampered receipt first; two concurring derivations,
  ruled in `03-FREEZE-JSON-AMENDMENT.md`); `freeze-sidecar` expects
  `readiness_receipt_namespace_anomalous` / "sidecar mismatch for
  freeze-0004.json"; `plan-json` uses the manifest-only mutation.
- **`119` propagates the digest chain** so the evidence-digest authenticator at
  `:5460-5465` cannot fire first, and **`123` mutates a SIBLING pinset row
  canonically** so the arm-entry histsem gate at `:7537-7546` cannot fire first.
- **The confirmation-pair preamble is unchanged in SUBSTANCE and shortened in
  COMMENT.** All six replacement blocks re-paste `ED_STEP6_CONFIRMED_SHA256`,
  validate it as lowercase 64-hex and cross-check it against the `085-*`
  witness, exactly as ruling R-2 requires; only the inline comment is now the
  one-liner "CONFIRMATION PAIR, re-pasted per block." The full statement of why
  `085-*` is a cross-check and never the source lives in §3.9 and is unchanged.
- **Predictions, not observations.** Every expected `reason_codes` and `detail`
  in the six replacement blocks is CODE-DERIVED — read off the raise sites at
  `5a034f84`, not observed in a run. Estate 10 confirms them by execution. A
  mismatch there is a FINDING to adjudicate, never a license to improvise the
  assertion at the bench (§6 applies unchanged).

**Anchor remap round 4 (2026-08-25, D-154).** PR #192 inserted the
`_freeze_pack_identity_mismatch_detail` helper into `joulewise/arm_readiness.py`
(+65 lines before the old comparison site, +69 after it), so every
`arm_readiness.py` anchor and citation at or beyond old line 6410 was
re-derived from a fresh difflib map: +0 through 6409, +65 for 6410-6447, +69
from 6449 on (57 substitution events; the replaced comparison lines 6448/6451
no longer exist and no citation names them). The AST anchor map returns 15/15
against a fresh clone at bf88212e. Estate 8's §1.1 anchor gate found the drift.

**r5 (2026-08-24): D-153 sweep cure.** A revision of this file, not a new
instrument: the filename, the estate layout and every r4 record below stand
unchanged. Authority: the two-seat D-153 fixation-family / confirmation-supply
sweep and its ruling — `docs/process_traces/2026-08-24-d153-sweep/03-MAGISTRATE-SYNTHESIS.md`
(rulings R-1 through R-6), over `01-opus-contract-lens-seat.md` (contract-lens
findings F0–F15) and `02-sol-semantic-seat.md` (semantic findings 1–62 and the
consolidated cure list). The sweep's shared root cause, in one sentence: this
runsheet's consumers were written against interfaces and orderings that D-153
and the step-6 contract later moved out from under them, and the instrument
carried no assertion class able to notice. Cure items 2–19 land here; item 1 is
the parallel code change that gives the `freeze` verb a
`--step6-confirmation-table` flag, and this revision is written against that
flag's contract.

- **The confirmation pair now reaches every post-mint enforcing consumer**
  (ruling R-2, Sol 45–55). Each such block re-pastes
  `ED_STEP6_CONFIRMED_SHA256` — Ed's out-of-band confirmed digest `hC` over the
  step-6 table — validates it as lowercase 64-hex, and cross-checks it against
  the `085-*` witness; `freeze` replays additionally pass
  `--step6-confirmation-table`. Before this revision **no live post-mint call
  in this runsheet supplied the pair at all**, which is why all three of estate
  6's §3.9 arms refused with "no expected confirmation digest supplied."
- **Refusals are asserted by DETAIL, not by refusal code alone** (Opus F0). The
  digest-conditional raise runs BEFORE the ordinary-changed-path raise and both
  carry the same registry code, so a code-only grep cannot tell the two causes
  apart. Every R1 probe now also asserts the presence or absence of the detail
  string `digest-conditional allowlist path`.
- **The `118-*` byte-pin probe moves to §4.10, after the fixation commit**, and
  its tamper becomes a SHAPE-PRESERVING canonical re-mint: a naive byte tamper
  is already caught pre-fixation by the canonicality check; the re-mint of
  identical shape reaches the fixation head with canonical bytes, and the byte
  pin's OWN failure is then proven by name, independent of which other tests
  also redden (F1, F2).
- **Epoch prose, A6 vocabulary and file citations are repaired**: §3.9's
  heading, §3.8's fixation wording, the reserved "window close" spellings, the
  fixation commit message, the post-W1 `tests/test_receipt_histsem.py` line
  coordinates (now also symbol-anchored), and the `084-*` transcript rename
  (F4–F14).
- **§5 acceptance** now requires pair-bearing evidence, splits the
  pre-fixation and post-fixation coordinates, and states correctly what
  `074-*` evidences.
- **§3.10's published-green half** names the WINDOW-CLOSE head rather than the
  fixation head (F11; D-153 A1 + A3) and carries an explicit, pair-bearing
  publication marker-replay block.

**Estate 6 is STRUCK (2026-08-24).** Not a discretionary call. §6's own failure
semantics classify both "a command that names a file, flag or refusal code that
does not exist" and "a step sequenced after the step that needs its output" as
INSTRUMENT failures — cured on main, re-ratified, restarted from §1.1 — and
estate 6 hit both: first the §3.8 `074-*` producer/consumer inversion (S0-O3),
then three §3.9 arms refusing because the runsheet never handed any consumer
`hC`. A same-estate continuation was not available either: it would have had to
re-run blocks that call `record_env` three times over already-recorded names,
and a `record_env` duplicate independently supersedes an estate under §6's
execution-defect clause. **Custody is preserved, READ-ONLY, and nothing is
deleted.** Estate 6's `091-*` REFUSE transcripts are RETAINED as live
NEGATIVE-LEG evidence: they are the standing demonstration that the C→S gate
really does fail closed when the confirmation pair is absent, which is the
mirror of the positive legs the cured blocks below now run. Its
instrument-correction notes stand. Estate 7 is cut only after the cure PRs land
AND re-ratification is recorded. Authority: synthesis R-3; §6 failure
semantics.

**S0-O3 recorded and cured (2026-08-24, estate 6).** Estate 6 ran clean through
§3.8's marker build — the first estate past the S0-O2 boundary — and the §3.8
Ed-confirmation block then refused at its final stanza: it reads
`074-successor-sha256.txt`, which this runsheet only produced in §4.10. The
inversion is D-153 fallout: fixation (and its transcript family 073–075/077–078)
moved from the mint side to §4.10, and the §3.8 consumer kept reading a record
that no longer existed yet. A mechanical producer/consumer sweep over every
`$TRANS/` reference found exactly this one inversion. Cure: §3.7 step 3 now
records the successor digest from the bytes committed at `$PINSET_MINT_HEAD`
(the moment the digest first exists) into `074-successor-sha256.txt`; §3.8's
consumer is unchanged; §4.10 step 2 recomputes the digest from the worktree at
fixation time and refuses if it differs from the mint-time record before
substituting the sentinel — a strictly stronger check than the old
produce-at-fixation shape, which could not have noticed the successor moving
inside the window. The 074 ordinal stays positional-historic with its family.

**Anchor remap round 3 + S0-O2 cure expectations (2026-08-24).** The marker
cure inserts into joulewise/arm_readiness.py, so every arm_readiness.py anchor
and citation was re-derived from a fresh difflib map (116 substitutions). The
shift is steeply piecewise — +0 below the first insertion, then +74, +86, +103,
+105 and +109 across the bands — so a single offset would have been wrong for
most citations. The AST checker returns 13/13 at the cure head. §3.8 and §5 now
expect the marker's required conditional_paths_deferred disclosure, with a
mechanical assertion on its gate identifier, its deferred_paths, and the four
enforcing entry points.


**S0-O2 recorded (2026-08-24).** Estate 5 ran clean through §3.7's mint and
refused at the §3.8 candidate marker build. The supply-line trace and the
step-6 contract's acyclicity clause are recorded in §3.8: the block order there
is contract-correct and is NOT the cause, so it is left unchanged; the defect is
that the marker build evaluates a C→S condition it has no contract-sanctioned
way to satisfy. The estate resumes at §3.8 without a re-cut once that code
question is ruled.


**Anchor refresh + builder cure (2026-08-24).** +40 anchor shift from the
pinset-builder cure, re-verified mechanically. The cure inserts into
`joulewise/arm_readiness.py`, so every `arm_readiness.py` anchor and citation was
re-derived from an exact old→new line map rather than by a blanket offset — the
shift is **piecewise**, +43 for sites between the cure's two hunks
(`_load_histsem_pinset` `:3242-3302` → `:3285-3345`) and +40 after them. §0.2's
anchor table, the embedded `s0_anchor_map.py` ANCHORS tuple, §0.3's pinned
mechanics map and every inline citation are updated together; the AST checker
returns 13/13 at the cure head. The remap was recomputed against the W2
restructure at merge time, not carried over from the pre-W2 computation. §3.7's
`--historical-head` is corrected to `$EVIDENCE_DERIVATION_HEAD` in the same
round, with the reason stated in place.


**r4 (2026-08-24).** A targeted delta over the refused r3 draft. Both r3
ratification seats returned REFUSE/REFUTED while certifying 12 of the 14 F-cures
and roughly twenty executed checks, and both prescribed a delta rather than a
rewrite. Everything r3 established stands; the eight cures below are the whole
difference, plus one finding r4 surfaces without deciding.

| # | Cure | Severity | Status |
|---|---|---|---|
| N-1 / R3-1 | `"$BASE:configs/…"` → `"${BASE}:configs/…"`; zsh's `:c` history modifier ate a character and the §1.1 gate refused a CLEAN base. Three-party reproduced. §0.1 gains the bracing rule and a lint, because `zsh -n` cannot catch it. | BLOCKER | fixed; blast-radius sweep re-run, and this revision satisfies the stricter "zero unbraced `$VAR:`" lint |
| N-2 | §3.9's arm-side eleven-kind census could not pass — `arm` runs `include_pack=False` (`:7602`) and `_discover_evidence` drops the PACK namespace (`:5655-5657`). The census moves to where the kinds are actually discovered (§3.4 authoring, §3.6 freeze); §3.9 keeps the forbidden-code check and rc alternatives. **No custody evidence is seeded.** | BLOCKER | fixed |
| R3-2 | `s0_anchor_map.py` validated line TEXT, so a commit with the pinned lines inside a module string passed 13/13 while defining nothing. Replaced with AST validation (parse + symbol/statement/owner), stdlib-only. | BLOCKER | fixed; forge reproduced and now REFUSED 0/13 |
| D-1 | §5 cited transcript range `080-*`–`085-*`; no step produces `083-*`. | defect | fixed: the five actual transcripts are named |
| D-2 / N-3 | Citation drift: `:7601`→`:7602` (second site `:7833`), `:7657-7666`→`:7655`. | defect | fixed |
| N-4 | `env.sh`'s `MARKER_BRANCH` read raised a raw Python traceback during `source` on a key-less manifest. | defect | fixed: exits 3 and `die`s with a runsheet message |
| F-10 | §4(e.1) writes into the transaction's own `$CUSTODY/windows` and mints `arm-0002`, superseding `arm-0001`. | note | folded: recorded as deliberate custody mixing, and every arm-receipt read is ordinal-pinned to `arm-0001` |
| F-11 | §2.2's `check_census.py` heredoc was never run in the r2 estate while §3.4 invoked it. | note | folded: §2.2 materialization is a checked step with transcript `011-*`, and §3.4 asserts the tool first |

**Packet-5 errata (2026-08-24), from D-153 — work order W2.** Packet 5 ruled
alpha-prime SPLIT-AND-SEQUENCE in amendment form and recorded it as D-153. Four
changes land here, and together they RESOLVE R4-O1.

| D-153 | Change |
|---|---|
| A6 | `WINDOW_CLOSE_HEAD` is renamed **`PINSET_MINT_HEAD`** throughout (17 sites). "Window close" is reserved for the r4-3 commit-freeze close; the mint-side event this runsheet performs is the ALLOWLIST-CONTRACT CLOSURE. Binding the two names together is what created R4-O1. `PINSET_COMMIT` is recorded alongside it as the same commit under its transaction-facing name. |
| A1 | The fixation steps move out of §3.7 and become **§4.10**, after the probe battery, renumbered 1–4. The marker (§3.8), the arm and verify (§3.9), the local green record (§3.10) and every §4 probe now run at `$PINSET_MINT_HEAD`, on a tree with no fixation commit on it. §4.10 states in its own text that this late placement is **CLONE-PROOF-ONLY** and that the REAL transaction fixates post-window per D-153 A1. |
| W2(c) | The **clean-arm block** is appended to §3.9: empty residue at `$PINSET_MINT_HEAD` (transcript `098-clean-arm-residue.json`), no `$CHANGED_CODE`, and **the eleven-kind census, RETURNED** — `want <= kinds` over the arm receipt. |
| A2 | The fixation delta shrinks to the hS byte pin plus its sentinel guard. Every digest-independent chain consequence moved into the pre-derivation candidate (work order W1). |

**R4-O1 is RESOLVED, not merely re-priced.** D-153 finding 1 settles that the
whole-tree R1 diff is intended design, not a defect: packet 5 repaired a
vocabulary collision and a sequencing trap around a correct gate. With fixation
last, the arm's changed set is fully allowlisted, the residue is empty,
`freeze_items` survives, and the census that r4 recorded as deferred is asserted
again. The interim "expected `DEPENDENCY_CHANGED_SET`" machinery, its `099-*`
isolating diagnostic, and the "positive obligation" framing are all withdrawn;
the §3.9 blockquote retains the history.

**§3.2 amendment (2026-08-24), from REAL EXECUTION.** The first cut of r4 was
executed against a fresh estate and reached §3.2, where the first U11 freeze
PASSED under the measurement venv — the first real U11 freeze ever to pass, and
live proof of amendment 3's mechanism — and the second refused
`readiness_identity_environment_dirty`. Cause: `freeze_projection` →
`_mint_git_anchor` (`identity_pins.py:788-806`) runs the v2 issuance mint's
whole-tree Git gate, which requires a CLEAN tree per freeze, while §3.2
sequenced all three freezes before one commit — so freeze #2 saw freeze #1's
uncommitted projection receipts and plan rewrite. **No ratification battery
could reach this**: it needs a freeze to have actually mutated the tree, and
every prior check stopped at preconditions. §3.2.b is now a per-pack
**freeze → assert → commit** interleave with a clean-tree guard before and
after each freeze; `$EVIDENCE_DERIVATION_HEAD` is the head after the third
commit, so every projection path stays strictly before it and §2.1's 112
exclusion and §3.3's common-head authoring are unchanged (stated in place).
Custody: `s0-clone-proof-r4/custody/transcripts/031-stop-u11-sequencing.md`.
Estate r4 (first cut) is superseded for custody hygiene. Verified red-before /
green-after by two REAL freezes on this machine — see the battery note in §0.1.

**Fix round 2 (2026-08-24), from the delta re-audit.** All seven r4 cures
confirmed and both r3 blockers dead; these were the residuals. D-3: §1.3's
library sweep moves to `git grep -- joulewise/` over TRACKED bytes — a worktree
recursion descends into `joulewise/__pycache__` once any step imports
`joulewise`, and those `.pyc` files really do contain both literals (verified),
so whether the sweep breaks depends on the grep implementation (the bench ugrep
7.8.4 drops binary matches silently; GNU grep would emit a `Binary file …
matches` line and fail the equality assertion). D-4: the four R4-O1-affected
sites are annotated in place, and the two that carried now-inverted assertions
were retargeted onto the residue rather than left to fire. D-5: the r2 banner
says r4. §0.2 gains the plain statement that the anchor map is a DRIFT TRIPWIRE
and never an integrity control — the re-audit's second forge showed symbol
anchors pass 13/13 over gutted function bodies. §0.1 folds the column-zero
invariant into the lint block as executable checks.

**r3 (2026-08-24) — REFUSED by both ratification seats; never executed.** A clean instrument. Amendments 1–3 are folded into the
body text — there are no amendment blocks below — and the fourteen findings of
the R-3 executability audit are cured. Binding records:

| Record | Custody path (2026-08-24 session) | What it settled |
|---|---|---|
| Packet 1 + 2 syntheses | `custody/transcripts/006`–`013` | registry-v1 census scope (the hyphen-form id constant is CORRECT ARCHIVAL RETENTION); the §1.3 classification fence (mechanical classification only; in-clone doc edits FORBIDDEN) |
| Packet 3 synthesis | `custody/transcripts/034`–`036` | U11 environment: remedy (a''), §3.2 runs under the pinned host measurement venv, read-only, zero installs anywhere; fresh estate; one-command-per-shell execution discipline |
| Custody anomaly | `custody/transcripts/035` | transcripts 031/032 of the r2 estate are VOID; compound scripts swallowed the failing gate assertions |
| Executability audit verdict | `custody/transcripts/037` | F-1…F-14; full cold re-ratification made mandatory; the instrument advances to r3 |

### What changed from r2 to r3 (retained: r4 inherits all of it)

1. **Execution contract (F-4, F-5, R-5).** A new §0.1 states the shell contract:
   the executing shell is **zsh 5.9 with 1-based arrays**, and **no shell state
   survives between tool invocations**. Every variable, array and helper now
   lives in `$PROOF/env.sh`, written once in §1.1 and re-sourced by every
   command block. Every `for i in 0 1 2` / `${PACKS[0]}` construct is gone,
   replaced by value iteration and named pack variables. Every gate assertion
   inside a loop carries an explicit `|| die` instead of relying on `set -e`,
   which the 035 anomaly proved is not reliable inside compound constructs.
   `$MARKER_BRANCH` is read from the candidate manifest in `env.sh`.
2. **Custody tools execute from the clone (F-1).** §3.7 and §3.8 invoke
   `$CLONE/scripts/<tool>.py`, never `$INPUT/<tool>.py`. Each tool sets
   `REPO_ROOT = Path(__file__).resolve().parents[1]`, so a copy outside the
   repository cannot `import joulewise` at all. A new §3.6.1 pre-execution step
   asserts each executing file's SHA-256 against the manifest's `custody_tools`
   digest before any tool runs, so the split S-5 lane rule is preserved
   verbatim: candidate mode authenticates the executing bytes against a
   document written before execution, never against a self-recomputed sidecar.
3. **The fixation delta now exists (F-2).** `s0-fixation-delta.patch` and its
   GNU sidecar are committed beside this runsheet, digest-bound in the
   candidate manifest, and applied **before** the step that runs
   `tests.test_receipt_histsem`. R2 sequenced the apply after the suite run and
   named a delta that had never been authored; that combination made the step-6
   suite red by construction. **That was the r3 cure, and it applied the delta
   in §3.7**; it is retained here as the record of what r3 settled. D-153 A1
   then moved the delta application, the suite run and the byte-pin probe out
   of §3.7 and into **§4.10**, after the probe battery — the apply-before-suite
   ordering the F-2 cure established is preserved there, at the new site.
4. **§4(h) probes what it claims to probe (F-3).** An out-of-enumeration
   `--pinset` override refuses `histsem_pinset_invalid`, not
   `histsem_pinset_absent` (`arm_readiness.py:3293-3304`, and the committed
   `tests/test_receipt_histsem.py:146-165` asserts exactly that). The probe now
   runs inside a `new_case` clone where the enumerated successor member has been
   `git rm`'d and is passed as `--pinset`, which is the only path that reaches
   the `present == 0` branch at `arm_readiness.py:3340-3344`.
5. **§4(b) targets a reachable signal (F-6).** `arm` discovery runs with
   `include_pack=False` (`arm_readiness.py:7602`), so an unexpected file in the
   *pack's* evidence directory is invisible to it. The probe is now two probes:
   4(b.1) puts the unexpected file in the **window-custody** evidence namespace,
   which `arm` does scan; 4(b.2) puts it in the **pack** namespace and freezes
   from a case at `$EVIDENCE_COMMIT`, the mint path, where `include_pack`
   defaults to true.
6. **§3.3 names its tests honestly (F-7).** The §1.3 manifest now carries a
   mechanically generated `test_modules` array; §3.3 asserts the manifest
   declares exactly the two modules it runs.
7. **§5 matches the superseded-by-merge reality (F-8).** The acceptance box that
   demanded a candidate patch, four tool sidecars and a `$INPUT` tool set now
   demands the mechanical manifest, the clone-tool digest equalities, the
   fixation-delta digest equality, and the clone provenance line.
8. **Notes folded.** §4(g) states the governed-nonzero alternative as an
   admissible outcome (F-9). §3.9 tolerates `receipt_path: null` on an early
   governed refusal (F-12). `$SESSION` is an operator input, not a literal
   (F-13). The §1.3 sweep uses `grep -E`; there is no `rg` binary on this bench
   (F-14).
9. **Anchor map machine-checked.** The thirteen-anchor map was verified 13/13 at
   `d19df05` by the audit; §0.2 restates it and adds a mechanical re-check
   against `$BASE` so drift stops being a prose claim. The pinned mechanics map
   is re-derived at the same head, so the r2 wart "where this map and an inline
   citation disagree, THIS MAP governs" is gone: they agree.
10. **`$BASE` selection is a gate, not a literal.** R2 pinned `1ba04a8` and then
    overrode it in prose. §1.1 instead takes the green head as an operator input
    and gates it mechanically: it must contain this delta's exact bytes, the four
    custody tools, the v2 registry, and none of the `_v4` output.

---

# 0. HOW TO EXECUTE THIS INSTRUMENT

### 0.1 Execution contract — read before running anything

**The shell.** Commands run under **zsh 5.9**. Two consequences bind every
block below:

- **Arrays are 1-based.** `${PACKS[0]}` is the empty string, not the first
  pack. In r2 that silently dropped the third pack from every
  `for i in 0 1 2` loop and made every gate assertion after the first a no-op.
  R4 contains no numeric array indexing at all: loops iterate values
  (`for pack in "${PACKS[@]}"`), and the three packs also have named variables
  (`$FIRST_PACK`, `$SECOND_PACK`, `$THIRD_PACK`) for the places that need one
  pack by name.
- **`set -e` is not trustworthy inside compound constructs.** Custody 035
  records a `for` loop that continued past failed assertions and then wrote
  later steps' evidence with the wrong head. Every assertion in r4 therefore
  ends in `|| die '<message>'`. `die` prints and exits; it never depends on
  the shell's errexit context.

- **Every `$VAR:` must be written `${VAR}:`.** In zsh a colon directly after
  an unbraced parameter name starts a *history modifier*, and the modifier
  silently eats the following character: `$BASE:configs/...` expands to
  `deadbeefonfigs/...` because `:c` is a modifier. `:t`, `:h`, `:r`, `:e`,
  `:a`, `:A`, `:g`, `:G`, `:l`, `:u`, `:p`, `:q`, `:Q`, `:s`, `:x` and `:&`
  all fire the same way. This produced a BLOCKER in r3 (`$BASE:configs/...`
  in the §1.1 `$BASE` gate), where the gate refused a perfectly clean base by
  looking up a corrupted object path. **`zsh -n` cannot catch this** — the
  construct is syntactically valid and the corruption happens at expansion
  time, so a parse check passes and the command fails only at run time
  against real data. It therefore needs its own lint, which every future
  revision of this instrument must run over its own text:

  The lint runs over the EXTRACTED COMMAND BLOCKS, not the prose — prose
  legitimately quotes the broken form, as the paragraph above does. Extract
  the blocks the same way the `zsh -n` pass does, then:

  **Both extractors anchor on `^```zsh` — column zero.** An executable step that
  is accidentally indented would escape the `zsh -n` pass and both lints
  silently, so the column-zero invariant is checked in the same block rather
  than asserted in prose.


  ```zsh
  RUNSHEET=docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md
  awk '/^```zsh/{f=1;next} f&&/^```/{f=0;next} f' "$RUNSHEET" > /tmp/s0-blocks.zsh
  # Blast-radius lint: any $VAR: immediately followed by a modifier letter.
  grep -nE '\$[A-Z_]+:[aAcegGhlpqQrstux&]' /tmp/s0-blocks.zsh
  # Stricter uniform lint, which this revision satisfies: ZERO unbraced $VAR:
  grep -nE '(^|[^{])\$[A-Za-z_][A-Za-z_0-9]*:' /tmp/s0-blocks.zsh
  # Column-zero invariant: exactly two INDENTED ```zsh blocks exist, both
  # illustrative (the source example above and this snippet).  Any third means
  # an executable step was indented and silently escaped every check above.
  ALL=$(grep -cE '^[[:space:]]*```zsh' "$RUNSHEET")
  COL0=$(grep -c '^```zsh' "$RUNSHEET")
  test "$((ALL - COL0))" = 2 || echo "INDENTED-BLOCK INVARIANT BROKEN: $((ALL - COL0))"
  test "$COL0" = 48 || echo "EXECUTABLE BLOCK COUNT CHANGED: $COL0"
  ```

  Both must print nothing (grep exits 1). A hit is a defect in the
  instrument, not in the bench.

  **`zsh -n` is run PER BLOCK, and §1.1's first block is the one exemption.**
  Concatenating the blocks and parsing the result is meaningless — later blocks
  legitimately reopen constructs the earlier ones closed — so the pass runs on
  each extracted block separately. Every block parses clean except §1.1's
  first, and that one cannot: its three `NAME=<description>` operator
  placeholders (`SESSION`, `BASE`, `CI_RUN_ID`) leave an unsubstituted
  `<`/`>`, which is a redirection with no target. (`MEASURE_PY`, the fourth
  operator input named above, is not one of them — it is written into `env.sh`
  as a literal path, not as a placeholder.) That block is the block the operator substitutes before running, so
  the exemption is bounded and disclosed here rather than rediscovered as
  drift. Any OTHER block failing `zsh -n` is an instrument defect. (Recorded
  by r5, from running the pass.)

- **The `env.sh` heredoc is UNQUOTED (`<<ENVEOF`) on purpose**, so that the
  operator's `$SESSION`, `$BASE` and `$CI_RUN_ID` are baked into the file as
  literals. Everything else inside it must be escaped: every `$` that belongs to
  env.sh is written `\$`, and **backticks must never appear inside it, not even
  in a comment** — the shell runs them. During this revision a comment
  containing a backticked word executed that word as a command while env.sh was
  being written. `zsh -n` does not catch this either; only executing §1.1 does,
  which is why the block battery in §0.1's self-review bar is mandatory.
  The same lesson recurred one layer deeper in §3.2: a defect that needs a REAL
  MLX freeze to have mutated the tree cannot be found by any check that stops at
  preconditions. This machine can run a real single-pack freeze (measurement
  venv plus weights on disk, a few minutes of model load), so **the battery for
  any future revision of §3.2 must include two real freezes back to back** —
  the second one proving that the interleave leaves a clean tree for it.

- **The bench `grep` is ugrep 7.8.4, not GNU grep.** It is API-compatible for
  everything this runsheet does, with one behavioural difference that matters:
  it drops binary-file matches silently where GNU grep prints
  `Binary file … matches`. Any sweep whose result is compared for equality must
  therefore not depend on the grep implementation — which is the second reason
  §1.3's library sweep uses `git grep` over tracked bytes rather than a worktree
  recursion. (`rg` does not exist on this bench at all; see F-14.)

**No state survives between command blocks.** Each block below runs in a fresh
shell: exported variables, shell functions and `cd` are all gone by the next
block. Therefore:

- **`$PROOF/env.sh` is the single home of execution state.** §1.1 writes it
  once. It contains `set -euo pipefail`, every path variable, the pack arrays,
  and the helper functions. Heads computed mid-transaction
  (`$S0_BOOTSTRAP_HEAD`, `$EVIDENCE_DERIVATION_HEAD`, `$EVIDENCE_COMMIT`,
  `$FREEZE_COMMIT`, `$PINSET_MINT_HEAD`, `$FIXATION_COMMIT`,
  `$FORGED_ORIGIN_MAIN_OID`, `$PROBE_BASE`) are **appended** to it by
  `record_env` at the moment they are computed.
- **Every command block below begins with the literal line**

  ```zsh
  source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
  ```

  Before pasting a block, prepend the one-line assignment that §1.1 writes into
  `$TRANS/000-source-line.txt` (it reads `S0_ENV=/abs/path/to/env.sh`). A block
  pasted without it aborts immediately on the `:?` guard. That abort is the
  guard working; it is never a reason to improvise the missing state.
- **One command block per shell invocation.** Do not concatenate two blocks
  into one call, and do not wrap a block in an outer script. This is R-5 of the
  packet-3 ruling and it is the direct cure for the 035 defect class.

**`record_env` refuses to redefine a name.** If a head is already recorded,
`record_env` stops rather than shadowing the earlier value. A re-run that trips
this is telling you the estate is no longer clean: start a fresh estate (§6),
do not delete the line.

**Transcripts.** Every tool run is captured as a stdout/stderr/rc triplet under
`$TRANS`. The magistrate reads every one. Authority: R4 r4-2; R5 V-2.

### 0.2 Anchor map — 15 anchors, validated through the AST

The R-3 executability audit verified the first thirteen anchors at `d19df05`
(2026-08-24). **r5 adds two more** — the two `tests/test_receipt_histsem.py`
methods this runsheet cites — because the D-153 sweep found (Opus F13) that
every citation into that file was still in PRE-W1 coordinates while being read
at a post-W1 head, and no mechanical check could see it: §1.1's line audit
asserts only that its extract is non-empty, so it was green over the wrong
lines. A symbol anchor catches the next shift by NAME. Both new anchors were
derived from the committed file at the r5 head. All fifteen are the drift
tripwire for every inline citation in this runsheet; §1.1 re-checks them
mechanically against `$BASE` before any transaction work.

**The two test-file coordinates are epoch-bound.** They are valid at E0–E3 —
the post-W1 candidate through the allowlist-contract closure — which is where
`$BASE` and every step before §4.10 sit. The fixation delta adds lines to the
same file, so anything cited from a post-fixation head shifts again and is not
covered by this map.

**Text equality is not enough, and r3 relied on it.** Both r3 ratification
seats executed the same forge: a commit whose files contain the pinned line
text inside a module-level string still matched all thirteen lines, so r3's
checker returned `PASS 13/13` on a repository whose `arm_readiness.py` defines
nothing at all. Reproduced during this revision — r3's checker: `PASS 13/13` on
the forge; r4's checker: `REFUSE 0/13`. Each anchor therefore now carries a
**kind** and an **owner**, and §1.1's checker validates them through Python's
`ast`:

- the file must **parse** at `$BASE` — a non-parsing file is never 15/15;
- a **symbol** anchor must be a real `def`/`class` of the named symbol
  *beginning* at the pinned line;
- a **statement** anchor must be executable code beginning at the pinned line,
  inside the named enclosing symbol, and not in the body of a multi-line
  string;
- the line text must still match, so a semantically equivalent rewrite is still
  reported as drift.

A single-line string on the pinned line is not a forge — real code such as
`allowlist = set(governed["irrelevant_path_allowlist"])` contains one. The
check is for the pinned line sitting in the *body* of a multi-line literal,
which is what a docstring forge always produces. Non-Python anchors would fall
back to text equality and be labelled as such; all fifteen are Python today,
so none does.

**The anchor map is a DRIFT TRIPWIRE, never an integrity control, and no step
below may be read as relying on it for integrity.** It answers one question —
"do the fifteen citations in this runsheet still point at the code they
claim?" — and nothing more. The r4 delta re-audit made the limit concrete with a
second forge: a commit whose functions keep their names and signatures at the
pinned lines but whose BODIES are gutted passes the AST check 13/13, because
every anchor is a definition site rather than a behaviour. Integrity comes from
three other places and only from them: the §1.3 manifest digests over committed
bytes, §3.6.1's authentication of the executing custody tools against those
digests, and the fact that `$BASE` is a merged head with green CI. If the anchor
map ever appears to be doing integrity work, that is a defect in the reasoning,
not a strength of the check.

| # | File | Line | Kind | Owner | Expected content at that line |
|---|---|---|---|---|---|
| 1 | `joulewise/arm_readiness.py` | 1050 | symbol | `EvidenceLifecycleError` | `class EvidenceLifecycleError(ValueError):` |
| 2 | `joulewise/arm_readiness.py` | 2025 | statement | `validate_registry` | `- set(lifecycle["irrelevant_path_allowlist"])` |
| 3 | `joulewise/arm_readiness.py` | 3753 | symbol | `_gate_receipt_histsem` | `def _gate_receipt_histsem(pack_root: Path, *, require_published: bool = False) -> None:` |
| 4 | `joulewise/arm_readiness.py` | 4229 | symbol | `_r1_changed_paths` | `def _r1_changed_paths(` |
| 5 | `joulewise/arm_readiness.py` | 4426 | statement | `validate_r1_evidence_lifecycle` | `allowlist = set(governed["irrelevant_path_allowlist"])` |
| 6 | `joulewise/arm_readiness.py` | 5409 | symbol | `_authenticate_generic_evidence_item` | `def _authenticate_generic_evidence_item(` |
| 7 | `joulewise/arm_readiness.py` | 6475 | symbol | `_load_freeze_reference` | `def _load_freeze_reference(` |
| 8 | `joulewise/arm_readiness.py` | 6749 | symbol | `generate_freeze_receipt` | `def generate_freeze_receipt(` |
| 9 | `joulewise/arm_readiness.py` | 6790 | statement | `generate_freeze_receipt` | `generation = _pack_generation(root.name)` |
| 10 | `joulewise/identity_pins.py` | 1826 | symbol | `freeze_projection` | `def freeze_projection(pack_root: Path \| str) -> Mapping[str, Any]:` |
| 11 | `scripts/generate_arm_readiness.py` | 28 | symbol | `_parser` | `def _parser() -> argparse.ArgumentParser:` |
| 12 | `scripts/project_identity_pins.py` | 23 | symbol | `parse_args` | `def parse_args(argv: list[str] \| None = None) -> argparse.Namespace:` |
| 13 | `scripts/verify_receipt_histsem.py` | 22 | symbol | `_parser` | `def _parser() -> argparse.ArgumentParser:` |
| 14 | `tests/test_receipt_histsem.py` | 160 | symbol | `test_pinset_is_byte_pinned_and_has_no_update_lane` | `def test_pinset_is_byte_pinned_and_has_no_update_lane(self) -> None:` |
| 15 | `tests/test_receipt_histsem.py` | 220 | symbol | `test_verifier_cli_refusal_is_canonical_and_exit_two` | `def test_verifier_cli_refusal_is_canonical_and_exit_two(self) -> None:` |

### 0.3 Pinned mechanics map — re-derived at `d19df05`

R2 carried ranges pinned at `1ba04a8` that had wholly drifted, plus a rule
saying the header map won on disagreement. R4 removes the disagreement: every
range below was re-derived at `d19df05` by symbol extraction, and every entry
names its symbol so the next drift is detectable by name rather than by line.

- R1 `EvidenceLifecycleError` is a `ValueError`, not an `ArmReadinessError`:
  `joulewise/arm_readiness.py:1050-1076`.
- Registry cross-check of conditional paths inside `validate_registry`:
  `:1999-2120` (the allowlist subtraction line is `:2025`).
- Histsem pinset chain loader `_load_histsem_pinset`: `:3285-3345`; the
  **only** promise of `histsem_pinset_absent` is its `present == 0` branch at
  `:3340-3344`; the out-of-enumeration override refuses
  `histsem_pinset_invalid` at `:3301-3304`.
- Whole-corpus verifier `verify_all_receipt_histsem`: `:3719-3750`.
- Freeze/arm histsem gate `_gate_receipt_histsem`: `:3753-3821`; its two call
  sites are freeze `:6774` and arm `:7537`.
- Changed-set enumeration `_r1_changed_paths`: `:4229-4277` (its
  `DEPENDENCY_CHANGED_SET` refusals at `:4262` and `:4274`).
- Dependency-manifest helper `_r1_manifest_dependencies` and the
  digest-conditional confirmed-path requirement
  `_require_confirmed_conditional_path`: `:4280-4367`.
- R1 primary gate `validate_r1_evidence_lifecycle`: `:4370-4542`. Allowlist
  subtraction plus conditional-path logic `:4426-4465`; manifest binding
  half 1 (source/receipt) `:4467-4484`; half 2 (nonempty/canonical plus
  derivation and current dependency) `:4485-4542`.
- Issued-acceptance census `_issued_d079` and the row-applicability rule that
  consumes it: `:5357-5397`.
- Evidence-directory namespaces `_evidence_directories`: `:5400-5406` — the
  `WINDOW_CUSTODY` namespace appears only when the custody pack root differs
  from the pack root, which is why §4(b) is two probes.
- Generic-item authentication `_authenticate_generic_evidence_item`:
  `:5409-5630` (its R1 refusals at `:5580`, `:5604`, `:5626`).
- Evidence discovery `_discover_evidence`: `:5633-5888`; the unexpected-output
  rejection is `:5659-5686`; `include_pack` defaults true and is passed False
  by arm `:7602` and verify `:7833`.
- Predecessor authentication and semantic replay
  `_authenticate_freeze_predecessor`: `:6243-6369`; predecessor derivation
  `_derive_freeze_predecessor`: `:6372-6407`.
- Freeze reference load / idempotent replay `_load_freeze_reference`:
  `:6475-6691`.
- `generate_freeze_receipt`: `:6749-7025`; generation gate `:6790`; the new
  mint unconditionally writes and plan-pins PASS **or** REFUSE at `:6978-7024`.
- `generate_arm_receipt`: `:7525-7771`; governed arm receipt construction and
  external write `:7737-7771`.
- Candidate/production tool-authentication lane `_family_tool_reference`:
  `:10464-10518`; the manifest digest reader `_candidate_manifest_tool_digest`:
  `:10417-10461`; marker construction `build_family_publication_marker`:
  `:10630-10783` (it writes the marker **and** its GNU sidecar at `:10771-10772`).
- U11 projection `joulewise/identity_pins.py:1826-1935`.
- Generic applicability rows `joulewise/arm_readiness_evidence.py:1709-1731`;
  authoring implementation `:2379-2618`.
- CLIs: freeze/arm/verify `scripts/generate_arm_readiness.py:28-192` (exit
  semantics `:175-192`: 0 PASS, 1 governed REFUSE, 2 raised
  `ArmReadinessError`); identity U11 `scripts/project_identity_pins.py:23-60`;
  histsem `scripts/verify_receipt_histsem.py:22-73`; evidence author
  `scripts/author_arm_readiness_evidence.py:25-112`.
- Generator preserve-mode echo hole
  `configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:1942-1955`;
  its CLI `:2657-2681`.
- Python is `>=3.11`, core dependencies are empty: `pyproject.toml:1-16`. Note
  that `[project.optional-dependencies]` is where `mac` lives — see §1.2.
- The v1 pinset byte pin literal `PINSET_SHA256` is
  `tests/test_receipt_histsem.py:33` (`:32` is `PINSET`, the path it hashes),
  and it is asserted with no update/reseal lane by
  `test_pinset_is_byte_pinned_and_has_no_update_lane` at `:160-166`; the
  explicit-override CLI refusal test
  `test_verifier_cli_refusal_is_canonical_and_exit_two` at `:220-238` expects
  `histsem_pinset_invalid`. **These are POST-W1 coordinates** (D-153 work order
  W1 shifted this file by +22 below ~line 145); r4 and earlier carried the
  pre-W1 numbers `:138-145` and `:146-165`, which now land on unrelated code.
  Authority: Opus F13.

### 0.4 Binding-source shorthand

- **R4** = `docs/process_traces/2026-08-20-go-session/v4-plan-ruling-r4draft.md`, cited by `r4-N`.
- **R5** = `docs/process_traces/2026-08-20-go-session/rulings-r5-consolidation.md`, cited by `S-N`, `V-1.i`–`V-1.vii`, or `V-2`.
- **RH-8** = `docs/process_traces/2026-08-20-go-session/rh-ruling.md`, item 8 and its normative annexes `rh-terra-debate.md` and `rh-opus-debate.md`.
- **SIT-C3** = `docs/process_traces/2026-08-20-go-session/ready-sitting-ruling.md`, C-3, with `readiness-sitting/seat-L5.md`, F2.
- **MARKER-A1** = `docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING-r2.md`, A-1.
- **HISTSEM-CONTRACT** = `docs/contracts/receipt_histsem_verifier.md`, especially "Pinset artifact and schema," "Gate integration," "Failure semantics," and "`_v4` transaction sequencing." Its rule-11 absence clarification supersedes the original library-absence wording without changing the explicit-CLI absence probe.
- **D-151** = `docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md`, adopting O-1-D and its incorporated nine-condition set.
- **D-150 / MARKER-RULING** = `docs/process_traces/2026-08-22-t20/marker-codesign/MAGISTRATE-RULING-MARKER.md`; D-150 selects option (a), BUILD-AT-BOUNDARY, CUSTODY-EXTERNAL, with the changed-set contract remaining 112.
- **REGISTRY-V2 RULING** = `docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING.md:124-131`; the RULED live coordinate is outer id `d117-row-registry-v2`, path `configs/arm_readiness/d117_row_registry_v2.json`.
- **S-1 MANIFEST** = `docs/process_traces/2026-08-22-t20/s1-candidate/MANIFEST.md`, now merged to main; its §9 was an implementing-seat self-report and was independently reviewed before the merge.
- **PACKET-3 RULING** = `custody/transcripts/036-magistrate-synthesis-packet3.md` of the 2026-08-24 session, R-1 through R-5.
- **AUDIT** = `custody/transcripts/037-executability-audit-verdict.md`, findings F-1…F-14.

### 0.5 Authority for the boundaries

Lead ruling records Ed's mint license as granted, so license is not an S-0
blocker. Execution still stops at the reviewed-custody boundary in §1.3 and at
the Ed-confirmed step-6 publication boundary in §§3.7–3.9. Candidate-lane work
in this clone is never publication. Authority:
`docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md`
(D-151 conditions 3–5) and
`docs/process_traces/2026-08-22-t20/marker-codesign/MAGISTRATE-RULING-MARKER.md`
(ratified items 1–3).

---

# 1. CLONE SETUP

### 1.1 Create the proof estate, the commit-exact clone, and `env.sh`

Four operator inputs are substituted into the first block, and only there:

- `SESSION` — the absolute path of this session's scratchpad root. It is an
  input, not a literal: r2 hard-coded a superseded session id.
- `BASE` — the green `main` head to clone. It is gated, not trusted: the
  assertions below require it to contain this instrument's fixation delta bytes,
  the four custody tools, and the v2 registry, and to contain none of the `_v4`
  output.
- `CI_RUN_ID` — the id of the green CI run for `$BASE`, conclusion-field
  verified. It is recorded as half of the provenance line.
- `MEASURE_PY` — the pinned host measurement interpreter (§1.2).

This block runs in Bash **or** zsh; every later block is zsh. It refuses if a
prior proof directory exists; custody and receipts are never reused.

```zsh
set -euo pipefail

SESSION=<absolute path of this session's scratchpad root>
BASE=<green main head SHA that satisfies the gate below>
CI_RUN_ID=<green CI run id for $BASE>

SOURCE=/Users/edr/code/JouleWise
PROOF="$SESSION/s0-clone-proof-r4"
CLONE="$PROOF/repo"
CUSTODY="$PROOF/custody"
TRANS="$CUSTODY/transcripts"
CASES="$PROOF/cases"
INPUT="$PROOF/input"

test ! -e "$PROOF" || { echo 'S-0 STOP: proof estate already exists'; exit 1; }
test "$(git -C "$SOURCE" rev-parse "$BASE^{commit}")" = "$BASE" \
  || { echo 'S-0 STOP: BASE does not resolve in the source repository'; exit 1; }
mkdir -p "$PROOF" "$CUSTODY" "$TRANS" "$CASES" "$INPUT" "$CUSTODY/tools"
git clone --no-local "$SOURCE" "$CLONE"
git -C "$CLONE" checkout --detach "$BASE"
test "$(git -C "$CLONE" rev-parse HEAD)" = "$BASE" || { echo 'S-0 STOP: clone head'; exit 1; }
test -z "$(git -C "$CLONE" status --porcelain=v1)" || { echo 'S-0 STOP: dirty clone'; exit 1; }
git -C "$CLONE" switch -c s0-transaction
git -C "$CLONE" config user.name 'S-0 clone-proof magistrate'
git -C "$CLONE" config user.email 's0-clone-proof.invalid'
git -C "$CLONE" config gc.auto 0
git -C "$CLONE" config maintenance.auto false
git -C "$CLONE" update-ref refs/remotes/origin/main "$BASE"

python3 -c 'import sys; assert sys.version_info >= (3,11), sys.version'
python3 -m venv "$PROOF/venv"
PY="$PROOF/venv/bin/python"
"$PY" -c 'import sys; assert sys.version_info >= (3,11); print(sys.version)'

cat > "$PROOF/env.sh" <<ENVEOF
set -euo pipefail

export SESSION=$SESSION
export SOURCE=$SOURCE
export BASE=$BASE
export CI_RUN_ID=$CI_RUN_ID
export PROOF=$PROOF
export CLONE=$CLONE
export CUSTODY=$CUSTODY
export TRANS=$TRANS
export CASES=$CASES
export INPUT=$INPUT
export PY=$PY
export S0_ENV=$PROOF/env.sh

# The pinned host measurement venv.  READ-ONLY use, in section 3.2 only.
export MEASURE_PY=/Users/edr/code/JouleWise/.venv/bin/python

export REGISTRY=\$CLONE/configs/arm_readiness/d117_row_registry_v2.json
export MANIFEST=\$INPUT/s0-candidate-manifest.json
export DELTA=\$CLONE/docs/process_traces/2026-08-22-t20/s0-fixation-delta.patch
export SUCCESSOR_PINSET=configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json
export BASE_PINSET=configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json

export FIRST_PACK=configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4
export SECOND_PACK=configs/campaigns/d117_floor_qwen25_1p5b_v4
export THIRD_PACK=configs/campaigns/d117_floor_qwen25_7b_v4
PACKS=("\$FIRST_PACK" "\$SECOND_PACK" "\$THIRD_PACK")
typeset -A PRED_OF
PRED_OF=(
  "\$FIRST_PACK"  configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3
  "\$SECOND_PACK" configs/campaigns/d117_floor_qwen25_1p5b_v3
  "\$THIRD_PACK"  configs/campaigns/d117_floor_qwen25_7b_v3
)

die() { printf 'S-0 STOP: %s\n' "\$*" >&2; exit 1; }

record_env() {
  local name=\$1 value=\$2
  if grep -qE "^export \${name}=" "\$S0_ENV"; then
    die "\$name is already recorded in env.sh; a re-run needs a fresh estate"
  fi
  printf 'export %s=%s\n' "\$name" "\${(q)value}" >> "\$S0_ENV"
}

capture() {
  local label=\$1; shift
  set +e
  "\$@" >"\$TRANS/\$label.stdout.json" 2>"\$TRANS/\$label.stderr.txt"
  local rc=\$?
  set -e
  printf '%s\n' "\$rc" >"\$TRANS/\$label.rc"
}

expect_rc() {
  local label=\$1 expected=\$2
  test "\$(cat "\$TRANS/\$label.rc")" = "\$expected"
}

no_traceback() {
  local label=\$1
  ! grep -Eq 'Traceback \(most recent call last\)|^[A-Za-z]+Error:' \
    "\$TRANS/\$label.stdout.json" "\$TRANS/\$label.stderr.txt"
}

commit_case() {
  local repo=\$1 message=\$2
  git -C "\$repo" add -A
  git -C "\$repo" commit -m "\$message"
  git -C "\$repo" update-ref refs/remotes/origin/main "\$(git -C "\$repo" rev-parse HEAD)"
}

new_case() {
  # zsh expands every word of a single 'local' statement BEFORE performing any
  # of its assignments, so target="\$CASES/\$name" read an UNSET \$name under
  # nounset — and the abort inside a command substitution returned rc 0,
  # yielding an empty result instead of a failure (found by real execution at
  # §3.5, fourth estate; same class as the §0.1 backtick rule). One
  # declaration per line; forward references only to completed assignments.
  local name=\$1
  local commit=\$2
  local target="\$CASES/\$name"
  test ! -e "\$target" || die "probe case \$name already exists"
  git clone --no-local "\$CLONE" "\$target" >/dev/null
  git -C "\$target" checkout --detach "\$commit" >/dev/null
  git -C "\$target" config user.name 'S-0 probe'
  git -C "\$target" config user.email 's0-probe.invalid'
  git -C "\$target" update-ref refs/remotes/origin/main "\$commit"
  printf '%s\n' "\$target"
}

if [ -f "\$MANIFEST" ]; then
  # A malformed or key-less manifest must STOP with a runsheet message.  Reading
  # it with a bare subscript raised a Python KeyError traceback while env.sh
  # was being sourced, which is neither a governed refusal nor readable.
  MARKER_BRANCH=\$("\$PY" -c '
import json,sys
try:
    value = json.load(open(sys.argv[1]))["marker_branch"]
except (OSError, ValueError, KeyError) as exc:
    sys.stderr.write("manifest marker_branch unreadable: %r\\n" % (exc,))
    raise SystemExit(3)
print(value)
' "\$MANIFEST") || die 'candidate manifest has no readable marker_branch'
fi
ENVEOF

printf 'S0_ENV=%s\n' "$PROOF/env.sh" > "$TRANS/000-source-line.txt"
git -C "$CLONE" rev-parse HEAD > "$TRANS/001-base-head.txt"
git -C "$CLONE" status --porcelain=v1 > "$TRANS/002-base-status.txt"
printf 'head=%s\nci_run_id=%s\nprovenance=merged candidate on main, green CI, conclusion-field verified\n' \
  "$BASE" "$CI_RUN_ID" > "$TRANS/003-clone-provenance.txt"
cat "$TRANS/000-source-line.txt"
```

Paste the line printed at the end as the assignment that precedes every block
from here on.

**`$BASE` gate.** Run next, in its own shell.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# The delta committed at BASE must be byte-identical to the delta this
# instrument was ratified with, proven by its own committed GNU sidecar.
DELTA_REL=docs/process_traces/2026-08-22-t20/s0-fixation-delta.patch
git -C "$CLONE" show "${BASE}:${DELTA_REL}" > "$TRANS/004-base-delta.patch" \
  || die "BASE does not contain the r4 fixation delta"
DELTA_SHA=$(shasum -a 256 "$TRANS/004-base-delta.patch" | awk '{print $1}')
SIDECAR_SHA=$(awk '{print $1}' "$CLONE/$DELTA_REL.sha256")
test "$DELTA_SHA" = "$SIDECAR_SHA" \
  || die "fixation delta at BASE does not match its committed sidecar"

for tool in \
  scripts/build_v4_histsem_pinset.py \
  scripts/build_family_marker.py \
  scripts/verify_family_marker.py \
  scripts/verify_receipt_histsem.py
do
  git -C "$CLONE" cat-file -e "${BASE}:${tool}" || die "BASE lacks custody tool $tool"
done
git -C "$CLONE" cat-file -e "${BASE}:configs/arm_readiness/d117_row_registry_v2.json" \
  || die "BASE lacks the v2 registry"

# BASE must contain NONE of the _v4 output that S-0 itself generates.
for absent in "$SUCCESSOR_PINSET" "$FIRST_PACK" "$SECOND_PACK" "$THIRD_PACK"; do
  if git -C "$CLONE" cat-file -e "${BASE}:${absent}" 2>/dev/null; then
    die "BASE already contains _v4 output at $absent"
  fi
done
printf 'delta_sha256=%s\ntools=4/4 present\nregistry_v2=present\nv4_output=absent\n' \
  "$DELTA_SHA" >> "$TRANS/003-clone-provenance.txt"
```

**Anchor-map re-check.** Run next, in its own shell. Any mismatch is a
precondition defect: stop, re-derive the map on main through the ordinary
review lane, and restart from a fresh estate.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

cat > "$CUSTODY/tools/s0_anchor_map.py" <<'PY'
#!/usr/bin/env python3
"""Re-check the fifteen pinned anchors against a committed revision.

Text equality alone is forgeable: a commit that moves the pinned line into a
docstring, a comment, or any string literal -- or that does not parse as Python
at all -- still matches the text and would pass a text-only check 15/15. Every
Python anchor is therefore validated through the AST:

  * the file must PARSE at the revision (a non-parsing file is never 15/15);
  * a "symbol" anchor must be a real ``def``/``class`` of the named symbol
    starting exactly at the pinned line;
  * a "statement" anchor must be executable code at the pinned line, inside the
    named enclosing symbol, and NOT inside any string literal;
  * the line text must still match, so a semantically equivalent rewrite is
    still reported as drift.

Non-Python anchors fall back to text equality alone and are labelled as such.
"""
import ast, json, subprocess, sys

# (path, line, kind, owner, expected text). kind is "symbol" (a def/class that
# begins at this line), "statement" (executable code inside `owner`), or "text"
# (non-Python file; text equality only).
ANCHORS = (
 ("joulewise/arm_readiness.py", 1050, "symbol", "EvidenceLifecycleError",
  "class EvidenceLifecycleError(ValueError):"),
 ("joulewise/arm_readiness.py", 2025, "statement", "validate_registry",
  '- set(lifecycle["irrelevant_path_allowlist"])'),
 ("joulewise/arm_readiness.py", 3753, "symbol", "_gate_receipt_histsem",
  "def _gate_receipt_histsem(pack_root: Path, *, require_published: bool = False) -> None:"),
 ("joulewise/arm_readiness.py", 4229, "symbol", "_r1_changed_paths",
  "def _r1_changed_paths("),
 ("joulewise/arm_readiness.py", 4426, "statement", "validate_r1_evidence_lifecycle",
  'allowlist = set(governed["irrelevant_path_allowlist"])'),
 ("joulewise/arm_readiness.py", 5409, "symbol", "_authenticate_generic_evidence_item",
  "def _authenticate_generic_evidence_item("),
 ("joulewise/arm_readiness.py", 6475, "symbol", "_load_freeze_reference",
  "def _load_freeze_reference("),
 ("joulewise/arm_readiness.py", 6749, "symbol", "generate_freeze_receipt",
  "def generate_freeze_receipt("),
 ("joulewise/arm_readiness.py", 6790, "statement", "generate_freeze_receipt",
  "generation = _pack_generation(root.name)"),
 ("joulewise/identity_pins.py", 1826, "symbol", "freeze_projection",
  "def freeze_projection(pack_root: Path | str) -> Mapping[str, Any]:"),
 ("scripts/generate_arm_readiness.py", 28, "symbol", "_parser",
  "def _parser() -> argparse.ArgumentParser:"),
 ("scripts/project_identity_pins.py", 23, "symbol", "parse_args",
  "def parse_args(argv: list[str] | None = None) -> argparse.Namespace:"),
 ("scripts/verify_receipt_histsem.py", 22, "symbol", "_parser",
  "def _parser() -> argparse.ArgumentParser:"),
 # r5 (Opus F13): the two test-file methods this runsheet cites.  A SYMBOL
 # anchor is used deliberately -- W1 shifted this file by +22 and every prose
 # citation into it went stale silently, because the only mechanical check that
 # touched those coordinates (the line audit below) asserts non-emptiness, not
 # content.  A symbol anchor fails by NAME on the next shift.  Coordinates are
 # valid at E0-E3 only; the fixation delta shifts this file again.
 ("tests/test_receipt_histsem.py", 160, "symbol",
  "test_pinset_is_byte_pinned_and_has_no_update_lane",
  "def test_pinset_is_byte_pinned_and_has_no_update_lane(self) -> None:"),
 ("tests/test_receipt_histsem.py", 220, "symbol",
  "test_verifier_cli_refusal_is_canonical_and_exit_two",
  "def test_verifier_cli_refusal_is_canonical_and_exit_two(self) -> None:"),
)

DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def _blob(repository, revision, path):
    return subprocess.run(["git", "-C", repository, "show", f"{revision}:{path}"],
                          check=True, capture_output=True).stdout.decode()


def _inside_multiline_string(tree, line):
    """True if `line` falls in the BODY of a multi-line string literal.

    A single-line string on the pinned line does not count: real code such as
    ``allowlist = set(governed["irrelevant_path_allowlist"])`` contains a string
    constant whose span is exactly that line. What we are detecting is the forge
    where the pinned TEXT was moved into a docstring or block comment, which
    always means the line sits strictly inside a multi-line literal.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            start, end = node.lineno, node.end_lineno
            if start is None or end is None or end == start:
                continue
            if start < line <= end:
                return True
    return False


def _has_executable_node_at(tree, line):
    """True if some non-string AST node BEGINS at `line`.

    This is what separates code from commentary: a docstring that merely quotes
    the pinned text has its Expr node at the docstring's opening line, so no
    node begins at the quoted interior line.
    """
    for node in ast.walk(tree):
        if getattr(node, "lineno", None) != line:
            continue
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            continue
        return True
    return False


def _defs_covering(tree, line):
    covering = []
    for node in ast.walk(tree):
        if isinstance(node, DEFS) and node.lineno <= line <= (node.end_lineno or node.lineno):
            covering.append(node)
    covering.sort(key=lambda n: n.lineno)
    return covering


def check(repository, revision):
    report, ok = [], True
    caches = {}
    for path, line, kind, owner, expected in ANCHORS:
        entry = {"path": path, "line": line, "kind": kind, "owner": owner,
                 "expected": expected}
        try:
            if path not in caches:
                caches[path] = _blob(repository, revision, path)
            source = caches[path]
        except subprocess.CalledProcessError as exc:
            entry.update({"match": False, "detail": f"blob unavailable: {exc}"})
            report.append(entry); ok = False; continue

        lines = source.splitlines()
        actual = lines[line - 1].strip() if 0 < line <= len(lines) else "<out of range>"
        entry["actual"] = actual
        text_ok = actual == expected.strip()

        if kind == "text":
            entry.update({"match": text_ok, "ast": "not applicable (non-Python anchor)"})
            ok &= text_ok
            report.append(entry); continue

        try:
            tree = ast.parse(source, filename=path)
        except SyntaxError as exc:
            entry.update({"match": False, "detail": f"file does not parse: {exc}"})
            report.append(entry); ok = False; continue

        if kind == "symbol":
            node = next((n for n in ast.walk(tree)
                         if isinstance(n, DEFS) and n.name == owner and n.lineno == line), None)
            ast_ok = node is not None
            entry["ast"] = ("definition of %s begins at this line" % owner if ast_ok
                            else "NO definition named %s begins at line %d" % (owner, line))
        else:
            in_string = _inside_multiline_string(tree, line)
            is_code = _has_executable_node_at(tree, line)
            covering = _defs_covering(tree, line)
            innermost = covering[-1].name if covering else None
            ast_ok = is_code and (not in_string) and innermost == owner
            entry["ast"] = {
                "inside_multiline_string": in_string,
                "executable_node_begins_here": is_code,
                "innermost_enclosing_symbol": innermost,
                "required_enclosing_symbol": owner,
            }

        entry["match"] = bool(text_ok and ast_ok)
        entry["text_match"] = text_ok
        entry["ast_match"] = bool(ast_ok)
        ok &= entry["match"]
        report.append(entry)

    return ok, report


def main():
    repository, revision = sys.argv[1], sys.argv[2]
    ok, report = check(repository, revision)
    print(json.dumps({"revision": revision,
                      "validation": "AST + text (text-only for non-Python anchors)",
                      "status": "PASS" if ok else "REFUSE",
                      "checked": len(ANCHORS),
                      "matched": sum(1 for item in report if item["match"]),
                      "anchors": report}, indent=2, sort_keys=True))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
PY
chmod 0555 "$CUSTODY/tools/s0_anchor_map.py"
"$PY" "$CUSTODY/tools/s0_anchor_map.py" "$CLONE" "$BASE" \
  > "$TRANS/005-anchor-map.json" || die "anchor map drifted at BASE; see 005"
"$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["matched"]==15, d["matched"]' \
  "$TRANS/005-anchor-map.json" || die "anchor map is not 15/15"
```

**Immutable line audit.** Run next, in its own shell. The ranges are the §0.3
map; each is a whole symbol, so a rename shows up as a shifted or empty extract
rather than as silently wrong bytes.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

for spec in \
  'joulewise/arm_readiness.py 1050,1076p;1999,2120p;3168,3228p;3605,3636p;3639,3707p;4115,4163p;4166,4253p;4256,4399p;5214,5263p;5266,5485p;5488,5743p;6098,6224p;6227,6262p;6265,6475p;6531,6807p;7307,7553p;10160,10261p;10370,10514p' \
  'joulewise/identity_pins.py 1826,1935p' \
  'joulewise/arm_readiness_evidence.py 1709,1731p;2379,2618p' \
  'scripts/generate_arm_readiness.py 28,192p' \
  'scripts/project_identity_pins.py 23,60p' \
  'scripts/verify_receipt_histsem.py 22,73p' \
  'scripts/author_arm_readiness_evidence.py 25,112p' \
  'tests/test_receipt_histsem.py 30,33p;160,166p;220,238p' \
  'configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py 1942,1955p;2657,2681p' \
  'pyproject.toml 1,16p'
do
  source_file=${spec%% *}; line_ranges=${spec#* }
  git -C "$CLONE" show "${BASE}:${source_file}" | nl -ba | sed -n "$line_ranges" \
    || die "line audit failed for $source_file"
done > "$TRANS/006-pinned-line-audit.txt"
test -s "$TRANS/006-pinned-line-audit.txt" || die 'line audit is empty'
```

Authority: R4 r4-2, r4-3, r4-7 and the task's immutable-HEAD verification
requirement; R5 V-2.

### 1.2 The environment contract

**No `pip install` anywhere.** Not into the estate venv, not into the host, not
into any environment. `$PY` — the estate venv built in §1.1 — is stdlib-only
and is the interpreter for every step **except** §3.2.

**§3.2 is the one exception, and it is not an install.** R2's §1.1 claimed the
core command surfaces are stdlib-only. That sentence was false for §3.2 and was
never true on any host: `scripts/project_identity_pins.py freeze` on a real pack
resolves the pack's declared runtime backend and hashes its weight files
(`identity_pins.py:1826-1935` → `MlxRuntimeAdapter.prepare`), so it imports
`mlx_lm`. `pyproject.toml:1-16` predicts the exact structured refusal S-0
observed on 2026-08-24: `readiness_identity_artifact_unreadable`, rc 2, with the
"install the [mac] extra" message. Nothing was installed to cure this. Instead
§3.2 runs under the **pinned existing host measurement venv**,
`$MEASURE_PY = /Users/edr/code/JouleWise/.venv/bin/python`, read-only — the
locked environment of `env/mac-measurement-lock.txt`, verified on 2026-08-24 to
be Python 3.13.1 with `mlx_lm` 0.31.3 and `transformers` 5.12.1. §3.2 carries
four guards: clone-first import assertion before and after,
`HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`, weight-file preconditions and a
digest post-condition against the committed `_v3` projection receipts, and the
interpreter path plus resolved versions recorded to transcript `029`.

Reading `/Users/edr/jw_models` (read-only hashing of weights) is permitted; it
is not the forbidden measurement checkout. Never run a dry-run, launch,
measurement, or quiet-Mac command in S-0. Exit code 134 anywhere in §3.2 is the
A85 abort firing outside pytest: STOP and escalate; never retry.

Authority: PACKET-3 RULING R-1; R4 r4-2, r4-3, r4-7; R5 V-2;
`pyproject.toml:1-16`.

### 1.3 Reviewed candidate inputs — hard precondition

**Superseded by merge.** The candidate merged to main before S-0 execution,
which is strictly stronger provenance than a patch plus a sidecar. The clone in
§1.1 is cut from a green merged head, which already contains the v2 registry,
all four custody tools, both contract documents, and this runsheet's fixation
delta — and correctly does **not** contain the generated `_v4` pack output.
What survives of the pre-merge design is exactly three things:

- **(a) the provenance line** — head SHA plus the green CI run id, recorded in
  `$TRANS/003-clone-provenance.txt` by §1.1 and gated by the `$BASE` block;
- **(b) the mechanical manifest** — generated below from committed bytes at the
  clone head, never hand-typed;
- **(c) every stop condition** — an `ED_RESERVED:` string, a digest mismatch, or
  a missing tool still stops execution.

`$INPUT` holds the generated manifest and nothing else. **No tool is ever
executed from `$INPUT`.** Each custody tool sets
`REPO_ROOT = Path(__file__).resolve().parents[1]` and inserts it at the front of
`sys.path`, so a copy outside the repository cannot `import joulewise` at all;
r2's `$INPUT/<tool>.py` invocations could not have run. Tools execute from
`$CLONE/scripts/`, authenticated against this manifest in §3.6.1.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

"$PY" - "$CLONE" "$MANIFEST" "$BASE" "$CI_RUN_ID" <<'PY'
import hashlib, json, pathlib, subprocess, sys
clone, manifest_path, head, ci_run_id = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3], sys.argv[4]
root = pathlib.Path(clone)

def blob(relative):
    return subprocess.run(["git", "-C", clone, "show", f"{head}:{relative}"],
                          check=True, capture_output=True).stdout

tools = (
    "scripts/build_v4_histsem_pinset.py",
    "scripts/build_family_marker.py",
    "scripts/verify_family_marker.py",
    "scripts/verify_receipt_histsem.py",
)
delta = "docs/process_traces/2026-08-22-t20/s0-fixation-delta.patch"
registry = json.loads(blob("configs/arm_readiness/d117_row_registry_v2.json"))
lifecycle = registry["freeze_evidence_lifecycle"]

manifest = {
    "schema_version": "joulewise.s0_candidate_manifest.v1",
    "head_commit": head,
    "ci_run_id": ci_run_id,
    "provenance": "merged-to-main; green CI; conclusion-field verified",
    "marker_branch": "BUILD-AT-BOUNDARY",
    "registry_id": registry["registry_id"],
    "registry_path": "configs/arm_readiness/d117_row_registry_v2.json",
    "refusal_vocabulary": {item["role"]: item["code"] for item in lifecycle["refusal_vocabulary"]},
    "custody_tools": {name: hashlib.sha256(blob(name)).hexdigest() for name in tools},
    "custody_inputs": {delta: hashlib.sha256(blob(delta)).hexdigest()},
    "test_modules": ["tests.test_arm_readiness_schemas", "tests.test_receipt_histsem"],
}
assert manifest["registry_id"] == "d117-row-registry-v2", manifest["registry_id"]
raw = json.dumps(manifest, indent=2, sort_keys=True).encode() + b"\n"
assert b"ED_RESERVED:" not in raw, "manifest carries an unresolved ED_RESERVED value"
manifest_path.write_bytes(raw)
print(json.dumps({"status": "PASS", "manifest_sha256": hashlib.sha256(raw).hexdigest(),
                  "tools": len(tools), "inputs": 1}, indent=2, sort_keys=True))
PY

"$PY" -m json.tool "$MANIFEST" >/dev/null || die 'manifest is not valid JSON'
shasum -a 256 "$MANIFEST" > "$TRANS/007-manifest-sha256.txt"
cp -p "$MANIFEST" "$TRANS/008-s0-candidate-manifest.json"
```

The manifest digest is the candidate-mode tool authority. Sidecars prove
transfer integrity, but the executing marker tools are authenticated against the
already-written `s0-candidate-manifest.json` `custody_tools` digests, never
against committed blobs and never by recomputing a self-authenticating sidecar
(`arm_readiness.py:10430-10518`). Production and publication phases retain
committed-blob equality. Because the manifest is generated from the committed
bytes at `$BASE`, that equality is exact by construction; what §3.6.1 then
proves is that the executing worktree files were not modified after the manifest
was written. The *review* provenance comes from the merge plus green CI, not
from the manifest generating itself. Authority: MARKER-RULING split S-5; S-1
MANIFEST §§6 and 9.1 G-4.

If any input is absent, mismatched, or contains `ED_RESERVED:`, stop: this is
missing custody, not authority to improvise mechanism. Authority: R4 r4-5,
r4-7; R5 S-6, V-1, V-2.

**Registry-v1 literal sweep.** Before mint, perform the ruled literal-string
consistency sweep for the registry repoint. Frozen campaign evidence and
historical process traces retain their archival v1 bytes; they are never bulk
rewritten. Classify each of the eleven live surfaces as either a correct
archival reference retained or a stale live pointer already repointed by the
merged candidate, and append that per-file disposition to the transcript. There
is no `rg` binary on this bench; the sweep uses `grep -E`.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

LIVE_V1_SURFACES=(
  docs/decision_log.md
  docs/phase_2/alpha_arm_readiness.md
  docs/phase_2/beta_arm_readiness.md
  docs/phase_2/gamma_arm_readiness.md
  docs/phase_2/window_runbook.md
  tests/test_arm_readiness_evidence_t0.py
  tests/test_arm_readiness_integration.py
  tests/test_arm_readiness_lifecycle.py
  tests/test_arm_readiness_registry.py
  tests/test_arm_readiness_schemas.py
  tests/test_d117_decode_contrast_plan.py
)
set +e
( cd "$CLONE" && grep -nE 'd117_row_registry_v1|d117-row-registry-v1' \
    "${LIVE_V1_SURFACES[@]}" ) > "$TRANS/009-registry-v1-literal-sweep.txt"
SWEEP_RC=$?
set -e
if [ "$SWEEP_RC" != 0 ] && [ "$SWEEP_RC" != 1 ]; then
  die "registry sweep failed with rc $SWEEP_RC"
fi

# The hyphen-form id constant in the library is IN SCOPE for this sweep and is
# ruled CORRECT ARCHIVAL RETENTION (packet 1).  Any OTHER joulewise/ hit stops.
# `git grep -- joulewise/` reads TRACKED BYTES, which is what the REGISTRY-V2
# ruling governs.  A worktree recursion (`grep -rn ... joulewise/`) descends into
# joulewise/__pycache__ as soon as any earlier step imports joulewise, and those
# .pyc files really do contain both literals (verified).  Whether they then
# surface is grep-implementation-dependent -- the bench ugrep drops binary
# matches silently, GNU grep would emit a "Binary file ... matches" line that
# breaks the equality assertion below -- so the worktree form makes this step
# non-re-runnable and host-dependent.  git grep removes both problems.
set +e
git -C "$CLONE" grep -nE 'd117_row_registry_v1|d117-row-registry-v1' -- joulewise/ \
  > "$TRANS/010-joulewise-v1-hits.txt"
LIB_RC=$?
set -e
if [ "$LIB_RC" != 0 ] && [ "$LIB_RC" != 1 ]; then
  die "library sweep failed with rc $LIB_RC"
fi
"$PY" - "$TRANS/010-joulewise-v1-hits.txt" <<'PY'
import pathlib, sys
lines = [line for line in pathlib.Path(sys.argv[1]).read_text().splitlines() if line.strip()]
allowed = 'joulewise/arm_readiness.py:46:ROW_REGISTRY_ID = "d117-row-registry-v1"'
unexpected = [line for line in lines if line.strip() != allowed]
assert not unexpected, unexpected
print("PASS: only the ruled archival id constant remains under joulewise/")
PY
```

Two rulings bind this clause's application:

1. *Census scope (packet 1, two-seat concurrence).* The sweep greps both
   literal forms while S-1 MANIFEST §7's census and its "no file under
   `joulewise/`" claim cover the underscore filename form only. The clause
   therefore also fires on the hyphen-form id constant
   `joulewise/arm_readiness.py:46` (`ROW_REGISTRY_ID = "d117-row-registry-v1"`),
   whose ruled disposition is **correct archival retention**: it is reachable
   only for v1-schema documents, selects nothing live
   (`ROW_REGISTRY_RELATIVE_PATH` at `:88` is the live pointer), and mirrors the
   documented `FREEZE_RECEIPT_V1_SCHEMA` retention pattern. That hit does not
   stop S-0. Follow-up naming row REGISTRY-ID-NAMING-01 is registered and fenced
   outside the transaction window.
2. *Fence (packet 2, magistrate synthesis adopting the refuter).* The
   classification lanes here admit **only** mechanical classification of hits
   into the two listed classes. Any hit whose disposition would require more
   than that — a repoint, a rewritten sentence, a resolved semantic conflict,
   any new `joulewise/` hit — is a candidate precondition defect: stop, correct
   the candidate on main through the ordinary review lane, and restart S-0 from
   a fresh estate. In-clone documentation edits are **forbidden** in S-0
   because DOCTRINE_PIN mints whole-file hashes of `window_runbook.md` and
   `decision_log.md` (`arm_readiness_evidence.py:799-888`): an in-clone edit
   would certify bytes no reviewed candidate ever contained.

At least `tests/test_arm_readiness_schemas.py` is a correct retention because it
pins the archival v1 SHA (`:420-422`). Authority: REGISTRY-V2 RULING
(`MAGISTRATE-RULING.md:124-131`); S-1 MANIFEST §7 and §9.3.1 item 3.

---

# 2. ALLOWLIST GENERATION

### 2.1 Generate, never hand-type, the base 112-path contract

This custody-only checker generates 37 exact paths per pack: 11 source JSONs,
11 evidence JSONs, 11 evidence sidecars, `freeze-0004.json` plus sidecar, and
`plan_tree.json` plus sidecar. The versioned successor pinset
`configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json` is the 112th
allowlist entry in the membership sense; it **replaces**, rather than
supplements, the old v1 pinset in this slot. Projection receipts,
`producer_contract.json`, identity-projection paths, and every authenticator
path are intentionally absent because U11 precedes derivation and D-151's
fixed-point principle forbids authenticators in any allowlist. Authority: D-151
conditions 1, 2 and 7; S-1 MANIFEST §3.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

cat > "$CUSTODY/tools/s0_allowlist_contract.py" <<'PY'
#!/usr/bin/env python3
import argparse, json, pathlib, subprocess, sys

ROOTS = (
 "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4",
 "configs/campaigns/d117_floor_qwen25_1p5b_v4",
 "configs/campaigns/d117_floor_qwen25_7b_v4",
)
SLUGS = (
 "acceptance-owner", "doctrine-pin", "estimator-identity", "mint-trust",
 "multicell-mint", "pack-authentication", "pack-family",
 "reason-code-coverage", "receipt-oracle", "recovery-ledger-test",
 "three-window-regression",
)
PINSET = "configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json"

def expected():
    paths=[]
    for root in ROOTS:
        paths += [f"{root}/arm_readiness.sources/{s}.json" for s in SLUGS]
        paths += [f"{root}/arm_readiness.evidence/evidence-{s}.json" for s in SLUGS]
        paths += [f"{root}/arm_readiness.evidence/evidence-{s}.json.sha256" for s in SLUGS]
        paths += [f"{root}/arm_readiness.freeze.receipts/freeze-0004.json"]
        paths += [f"{root}/arm_readiness.freeze.receipts/freeze-0004.json.sha256"]
        paths += [f"{root}/plan_tree.json", f"{root}/plan_tree.sha256"]
    paths.append(PINSET)
    return sorted(paths)

ap=argparse.ArgumentParser()
ap.add_argument("--registry", type=pathlib.Path, required=True)
ap.add_argument("--repo", type=pathlib.Path)
ap.add_argument("--derivation")
ap.add_argument("--head", default="HEAD")
ap.add_argument("--candidate-list", type=pathlib.Path)
ap.add_argument("--observed-list", type=pathlib.Path)
ap.add_argument("--shape-only", action="store_true")
a=ap.parse_args()
reg=json.loads(a.registry.read_text())
life=reg["freeze_evidence_lifecycle"]
candidate=(json.loads(a.candidate_list.read_text()) if a.candidate_list else
           life["irrelevant_path_allowlist"])
exp=expected()
bad_forbidden=[p for p in candidate if "identity_pin_projection" in p or p.endswith("/producer_contract.json")]
result={"status":"PASS", "expected_count":len(exp), "candidate_count":len(candidate),
 "candidate_missing":sorted(set(exp)-set(candidate)),
 "candidate_extra":sorted(set(candidate)-set(exp)),
 "candidate_not_sorted_unique":candidate != sorted(set(candidate)),
 "forbidden":bad_forbidden}
if not a.shape_only:
    if a.observed_list:
        observed=json.loads(a.observed_list.read_text())
    else:
        if not a.repo or not a.derivation: ap.error("full check needs --repo and --derivation")
        raw=subprocess.check_output(["git","-C",str(a.repo),"diff","--name-only","-z",f"{a.derivation}..{a.head}","--"])
        observed=sorted(x for x in raw.decode().split("\0") if x)
    result.update({"observed_count":len(observed),
      "unused_allowlist":sorted(set(candidate)-set(observed)),
      "changed_not_allowlisted":sorted(set(observed)-set(candidate)),
      "observed_missing_from_literal":sorted(set(exp)-set(observed)),
      "observed_extra_to_literal":sorted(set(observed)-set(exp))})
ok=all(not v for k,v in result.items() if k not in {"status","expected_count","candidate_count","observed_count"})
ok &= len(exp)==112 and len(candidate)==112
result["status"]="PASS" if ok else "REFUSE"
print(json.dumps(result, indent=2, sort_keys=True))
sys.exit(0 if ok else 2)
PY
chmod 0555 "$CUSTODY/tools/s0_allowlist_contract.py"

"$PY" - "$REGISTRY" <<'PY'
import json,sys
registry=json.load(open(sys.argv[1]))
assert registry["registry_id"] == "d117-row-registry-v2"
assert registry["schema_version"] == "joulewise.arm_readiness_row_registry.v2"
PY
"$PY" "$CUSTODY/tools/s0_allowlist_contract.py" \
  --registry "$REGISTRY" --shape-only | tee "$TRANS/020-allowlist-shape.json"
test "$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["expected_count"])' \
  "$TRANS/020-allowlist-shape.json")" = 112 || die 'allowlist shape is not 112'
```

The arithmetic is `3 × (11 + 11 + 11 + 1 + 1 + 1 + 1) + 1 = 3 × 37 + 1 = 112`.
R5 V-1 supplies the three 37-path packs (111); O-1-D supplies exactly
`configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json` as the `+1`.
The old `legacy_receipt_histsem_pinset_v1.json` remains archival and byte-pinned
but is **not** in this allowlist. "112th entry" means membership; the stored
list is sorted, so the successor need not be physically last. The contract
remains pack-and-ordinal exact (`freeze-0004`, not a glob), and the
custody-external marker contributes zero tracked paths. The live registry
coordinate used throughout is outer id `d117-row-registry-v2`, path
`configs/arm_readiness/d117_row_registry_v2.json`; the archival v1 registry
remains untouched for frozen historical references. Authority: D-151 conditions
1–2 and Consequences; D-150 / MARKER-RULING opening constraints; REGISTRY-V2
RULING; S-1 MANIFEST §§3–4, 2.1, 8.3 and 9.3.1 item 3.

### 2.2 Applicability census

After the evidence-author commands in §3.4, assert the exact eleven generic
kinds.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

cat > "$CUSTODY/tools/check_census.py" <<'PY'
import json,sys
want=sorted(["ACCEPTANCE_OWNER","DOCTRINE_PIN","ESTIMATOR_IDENTITY","MINT_TRUST",
 "MULTICELL_MINT","PACK_AUTHENTICATION","PACK_FAMILY","REASON_CODE_COVERAGE",
 "RECEIPT_ORACLE","RECOVERY_LEDGER_TEST","THREE_WINDOW_REGRESSION"])
for p in sys.argv[1:]:
 d=json.load(open(p)); assert d["status"]=="PASS" and d["mutated"] is True
 assert sorted(d["authored_kinds"])==want, (p,d.get("authored_kinds"))
print(json.dumps({"status":"PASS","packs":len(sys.argv)-1,"generic_kinds":want}))
PY
chmod 0555 "$CUSTODY/tools/check_census.py"

# F-11: in the r2 estate this heredoc was NEVER RUN -- custody/tools/ held only
# s0_allowlist_contract.py -- while section 3.4 invoked check_census.py.  A
# heredoc merely printed in a runsheet is not a materialized tool, so
# materialization is a checked step with its own transcript.
test -f "$CUSTODY/tools/check_census.py" || die 'check_census.py was not materialized'
"$PY" -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' \
  "$CUSTODY/tools/check_census.py" || die 'check_census.py does not parse'
shasum -a 256 "$CUSTODY/tools"/*.py > "$TRANS/011-custody-tools-materialized.txt"
"$PY" - "$CUSTODY/tools" <<'PY'
import pathlib, sys
tools = pathlib.Path(sys.argv[1])
required = {"s0_anchor_map.py", "s0_allowlist_contract.py", "check_census.py"}
present = {path.name for path in tools.glob("*.py")}
missing = sorted(required - present)
assert not missing, f"custody tools not materialized: {missing}"
print(f"PASS: {len(present)} custody tools materialized, all required present")
PY
```

Every tool this runsheet writes as a heredoc is materialized by RUNNING the
block that contains it. `011-custody-tools-materialized.txt` is the record that
the three tools needed before §3 exist on disk with their digests; §4's one
remaining custody tool, `tamper_class.py`, is materialized and checked in its own
section. (r6 removed `mutate_plan.py`: §4(c), §4(e) and §4(g) each mutate a
different plan tree now, so each carries its own driver as a block-local
heredoc.) §3.4 re-asserts the census tool before invoking it.

Any future issued-acceptance corpus growth must mechanically change the census
to 12 slugs per pack and the contract to 120 paths; no operator may preserve 112
by prose. Authority: R5 V-1.ii; `arm_readiness.py:5357-5397`;
`arm_readiness_evidence.py:1709-1731`.

---

# 3. FULL THREE-PACK TRANSACTION

`$PACKS`, `$PRED_OF`, `$FIRST_PACK`, `$SECOND_PACK` and `$THIRD_PACK` are
defined in `env.sh` (§1.1). There is no index arithmetic anywhere below;
`${PRED_OF[$pack]}` supplies each pack's predecessor by key.

### 3.1 Materialize the `_v4` roots from the reviewed generators

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"

"$PY" configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py \
  --pack-id d117_contrast_qwen25_1p5b_vs_7b_v4 --family-suffix _v4 \
  --no-preserve-current-frozen-bytes | tee "$TRANS/021-emit-contrast-v4.txt"
"$PY" configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py \
  --pack-id d117_floor_qwen25_1p5b_v4 --family-suffix _v4 \
  --no-preserve-current-frozen-bytes | tee "$TRANS/022-emit-1p5b-v4.txt"
"$PY" configs/campaigns/d117_floor_qwen25_7b_v3/generate_configs.py \
  --pack-id d117_floor_qwen25_7b_v4 --family-suffix _v4 \
  --no-preserve-current-frozen-bytes | tee "$TRANS/023-emit-7b-v4.txt"

for pack in "${PACKS[@]}"; do
  test -f "$CLONE/$pack/plan_tree.json" || die "generator produced no plan tree for $pack"
done
git add -A
git commit -m 'S-0 bootstrap reviewed candidate and generated v4 roots'
S0_BOOTSTRAP_HEAD=$(git rev-parse HEAD)
git update-ref refs/remotes/origin/main "$S0_BOOTSTRAP_HEAD"
record_env S0_BOOTSTRAP_HEAD "$S0_BOOTSTRAP_HEAD"
printf '%s\n' "$S0_BOOTSTRAP_HEAD" > "$TRANS/024-bootstrap-head.txt"
```

Expected: each generator prints `generated <pack-id> ... 100 science configs`
with plan hashes; no evidence or `freeze-0004` output exists yet. Authority: R4
r4-3, r4-7; R5 V-1.i; generator CLI `:2657-2681`.

### 3.2 U11 on all three packs, before allowlist derivation

This is the one step that runs under `$MEASURE_PY`. It performs **no install**
of any kind. Run each of the three blocks below in its own shell.

**3.2.a — record and gate the runtime environment.**

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

test -x "$MEASURE_PY" || die 'the pinned measurement interpreter is absent'
"$MEASURE_PY" - "$CLONE" > "$TRANS/029-u11-runtime-environment.txt" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import joulewise, mlx.core, mlx_lm, transformers
print("interpreter:", sys.executable)
print("python:", sys.version.split()[0])
print("joulewise.__file__:", joulewise.__file__)
print("mlx_lm:", mlx_lm.__version__)
print("transformers:", transformers.__version__)
PY
IMPORTED=$(grep -F 'joulewise.__file__:' "$TRANS/029-u11-runtime-environment.txt" | awk '{print $2}')
case "$IMPORTED" in
  "$CLONE"/joulewise/*) ;;
  *) die "clone-first import assertion FAILED before U11: joulewise resolved to $IMPORTED" ;;
esac

# Weight preconditions, from the committed _v3 projection receipts.
"$PY" - "$CLONE" <<'PY'
import json, pathlib, sys
clone = pathlib.Path(sys.argv[1])
predecessors = (
 "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3",
 "configs/campaigns/d117_floor_qwen25_1p5b_v3",
 "configs/campaigns/d117_floor_qwen25_7b_v3",
)
checked = 0
for pack in predecessors:
    receipt = clone / pack / "identity_pin_projection.receipts/projection-0001.json"
    value = json.loads(receipt.read_bytes())
    for unit in value["identity_units"]:
        for item in unit["model_file_inventory"]:
            path = pathlib.Path(item["resolved_path"])
            assert path.is_file(), f"declared weight file is absent: {path}"
            assert path.stat().st_size == item["size_bytes"], (str(path), path.stat().st_size, item["size_bytes"])
            checked += 1
print(json.dumps({"status": "PASS", "weight_files_checked": checked}, indent=2, sort_keys=True))
PY
```

The precondition checks presence and size, not digests. The digest equality is
proven as a **post-condition** in 3.2.c, where the `_v4` projection receipt's own
`model_file_inventory[].sha256` is compared against the committed `_v3`
receipt's for the same resolved path. That is the same evidence at zero extra
cost: `freeze_projection` hashes every weight file anyway, so a pre-hash would
mean hashing several gigabytes twice. This is a deliberate, recorded departure
from the letter of PACKET-3 RULING R-1(iii), which asked for a precondition; the
evidentiary content is unchanged and the placement is strictly later, so a
missing or moved weight file still stops the step before any mutation.

**3.2.b — the three freezes, each committed before the next begins.**

**The tree must be CLEAN at every freeze.** `freeze_projection` calls
`_mint_git_anchor` (`identity_pins.py:788-806`), which invokes the v2 issuance
mint's fixed-repository, **whole-tree** Git gate; a dirty working tree refuses
`readiness_identity_environment_dirty`. r4's first cut sequenced all three
freezes before a single commit, so freeze #2 saw freeze #1's uncommitted
`projection-0001.json`, its sidecar, and the rewritten plan bytes — and refused.
This was found by REAL EXECUTION, not by review: the first freeze passed (the
first real U11 freeze ever to pass, proving amendment 3's mechanism live) and
the second refused. No battery that stops at preconditions can reach it, because
it needs one freeze to have actually mutated the tree. Custody:
`s0-clone-proof-r4/custody/transcripts/031-stop-u11-sequencing.md`.

The cure is a per-pack **freeze → assert → commit** interleave. Run this block
**once per pack**, in pack order, each in its own shell, and do not start the
next pack until the previous one's commit exists.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

# PACK is the ONE pack this invocation freezes.  Paste the pack path here:
#   first  invocation: $FIRST_PACK
#   second invocation: $SECOND_PACK
#   third  invocation: $THIRD_PACK
PACK=$FIRST_PACK

label=$(basename "$PACK")
# Amendment-3 guard, re-asserted per freeze: the tree must be clean BEFORE this
# freeze, or the v2 git anchor refuses readiness_identity_environment_dirty.
test -z "$(git -C "$CLONE" status --porcelain=v1)" \
  || die "tree is dirty before the U11 freeze of ${label}: commit the previous pack first"

capture "030-u11-$label" "$MEASURE_PY" scripts/project_identity_pins.py freeze "$PACK"
rc=$(cat "$TRANS/030-u11-$label.rc")
if [ "$rc" = 134 ]; then
  die "exit 134 in section 3.2 for ${label}: A85 SIGABRT outside pytest. STOP, escalate, never retry."
fi
test "$rc" = 0 || die "U11 freeze rc=$rc for ${label}"
no_traceback "030-u11-$label" || die "U11 freeze traceback for ${label}"
"$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="PASS" and d["mutated"] is True, d' \
  "$TRANS/030-u11-$label.stdout.json" || die "U11 freeze is not PASS/mutated for ${label}"
test -f "$CLONE/$PACK/identity_pin_projection.receipts/projection-0001.json" \
  || die "no projection receipt for ${label}"
# The sidecar is projection-0001.sha256, NOT projection-0001.json.sha256 --
# verified against a live freeze and against the committed _v3 packs.
test -f "$CLONE/$PACK/identity_pin_projection.receipts/projection-0001.sha256" \
  || die "no projection sidecar for ${label}"

# Commit THIS pack only, so the next freeze starts from a clean tree.
git add -- "$PACK"
git commit -m "S-0 U11 identity-pin projection for ${label}"
test -z "$(git -C "$CLONE" status --porcelain=v1)" \
  || die "tree still dirty after committing ${label}: the freeze wrote outside its pack"
printf '%s %s\n' "$label" "$(git rev-parse HEAD)" >> "$TRANS/030-u11-commits.txt"
```

The trailing clean-tree assertion is load-bearing in its own right: it proves
each freeze wrote only inside its own pack root. A freeze that touched anything
else would leave the tree dirty after a pack-scoped `git add`, and the next
pack's freeze would refuse anyway — better to stop here, where the cause is
named.

**Why the 112-path argument is unchanged.** `$EVIDENCE_DERIVATION_HEAD` is now
the head after the **third** commit rather than after a single combined commit.
Every projection path — `projection-0001.json`, its sidecar, and the rewritten
plan bytes for all three packs — is written by one of the three commits, so all
of them remain **strictly before** `$EVIDENCE_DERIVATION_HEAD`. §2.1's argument
that projection receipts and identity-projection paths are "correctly absent
from the 112" therefore holds exactly as before: the changed-set window that
§3.7 closes runs from `$EVIDENCE_DERIVATION_HEAD` forward, and nothing written
in §3.2 is inside it. §3.3's common-head requirement is likewise unaffected —
it requires the three *evidence-authoring* commands in §3.4 to run at one
common head with no commit between them, which is a property of §3.4, not of
how many commits §3.2 made.

**3.2.c — post-conditions, then the derivation head.** Run after all three
per-pack commits exist. There is no commit of its own to make: the three
commits from §3.2.b already carry every projection path, and this block only
records which head they ended at.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"

# All three per-pack freezes ran and were committed, in order, one each.
test "$(wc -l < "$TRANS/030-u11-commits.txt" | tr -d ' ')" = 3 \
  || die 'expected exactly three per-pack U11 commits; see 030-u11-commits.txt'
for pack in "${PACKS[@]}"; do
  grep -qF "$(basename "$pack") " "$TRANS/030-u11-commits.txt" \
    || die "no U11 commit recorded for $(basename "$pack")"
done
test -z "$(git status --porcelain=v1)" || die 'tree is dirty at the derivation head'

# Clone-first import assertion AFTER the mutation.
"$MEASURE_PY" -c 'import sys; sys.path.insert(0,sys.argv[1]); import joulewise; print(joulewise.__file__)' \
  "$CLONE" > "$TRANS/029-u11-import-after.txt"
case "$(cat "$TRANS/029-u11-import-after.txt")" in
  "$CLONE"/joulewise/*) ;;
  *) die 'clone-first import assertion FAILED after U11' ;;
esac

# Weight-digest post-condition: the _v4 projections must have hashed the same
# weight bytes the committed _v3 projection receipts recorded.
"$PY" - "$CLONE" <<'PY'
import json, pathlib, sys
clone = pathlib.Path(sys.argv[1])
pairs = {
 "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4": "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3",
 "configs/campaigns/d117_floor_qwen25_1p5b_v4": "configs/campaigns/d117_floor_qwen25_1p5b_v3",
 "configs/campaigns/d117_floor_qwen25_7b_v4": "configs/campaigns/d117_floor_qwen25_7b_v3",
}
def inventory(pack):
    receipt = clone / pack / "identity_pin_projection.receipts/projection-0001.json"
    value = json.loads(receipt.read_bytes())
    return {item["resolved_path"]: item["sha256"]
            for unit in value["identity_units"] for item in unit["model_file_inventory"]}
compared = 0
for successor, predecessor in pairs.items():
    new, old = inventory(successor), inventory(predecessor)
    assert set(new) == set(old), (successor, sorted(set(new) ^ set(old)))
    for path, digest in new.items():
        assert digest == old[path], (path, digest, old[path])
        compared += 1
print(json.dumps({"status": "PASS", "weight_digests_compared": compared}, indent=2, sort_keys=True))
PY

# EVIDENCE_DERIVATION_HEAD is the head after the THIRD per-pack commit.  Every
# projection path was written by one of those three commits, so all of them are
# strictly BEFORE this head and stay outside the 112-path window that section
# 3.7 closes from this head forward.
EVIDENCE_DERIVATION_HEAD=$(git rev-parse HEAD)
test "$EVIDENCE_DERIVATION_HEAD" = "$(tail -1 "$TRANS/030-u11-commits.txt" | awk '{print $2}')" \
  || die 'HEAD is not the third per-pack U11 commit'
git update-ref refs/remotes/origin/main "$EVIDENCE_DERIVATION_HEAD"
record_env EVIDENCE_DERIVATION_HEAD "$EVIDENCE_DERIVATION_HEAD"
printf '%s\n' "$EVIDENCE_DERIVATION_HEAD" > "$TRANS/031-common-derivation-head.txt"
```

Expected per pack: PASS, `mutated:true`, `reason_codes: []`,
`projection-0001.json` and `projection-0001.sha256` (the sidecar drops the
`.json`, unlike every other sidecar in this runsheet), and updated plan bytes. All three packs' paths are written by the three §3.2.b
commits and are therefore before `$EVIDENCE_DERIVATION_HEAD`, so they remain
correctly absent from the 112.
Transcripts `031` and `032` are written **only** after this commit exists — the
r2 estate wrote them from a compound script that continued past failed
assertions, and both were voided (custody 035). Authority: PACKET-3 RULING R-1
and R-5; R4 r4-1, r4-2, r4-3; R5 V-1.i; `identity_pins.py:1826-1935`.

### 3.3 Terminal common-head evidence

The candidate must bind the exact common HEAD and tree and contain no
unresolved registry values. The manifest declares its terminal-review modules in
`test_modules`; the block asserts the declaration matches what it runs, so an
undeclared substitution is a failed proof rather than an unnoticed one. Do not
create any commit between the three author commands.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"

git rev-parse HEAD 'HEAD^{tree}' > "$TRANS/032-terminal-common-head.txt"
test "$(git rev-parse HEAD)" = "$EVIDENCE_DERIVATION_HEAD" || die 'HEAD is not the derivation head'
test -z "$(git status --porcelain=v1)" || die 'tree is dirty before authoring'

"$PY" - "$MANIFEST" <<'PY'
import json, sys
declared = json.load(open(sys.argv[1]))["test_modules"]
expected = ["tests.test_arm_readiness_schemas", "tests.test_receipt_histsem"]
assert declared == expected, (declared, expected)
print("PASS: manifest declares exactly the two modules this step runs")
PY

set +e
"$PY" -m unittest -v \
  tests.test_arm_readiness_schemas \
  tests.test_receipt_histsem > "$TRANS/033-pre-author-tests.txt" 2>&1
PRE_AUTHOR_RC=$?
set -e
test "$PRE_AUTHOR_RC" = 0 || die "pre-author suite failed with rc $PRE_AUTHOR_RC; see 033"
```

Authority: R4 r4-3, r4-5; R5 V-1.iii, V-2; AUDIT F-7.

### 3.4 Author all 33 generic receipts at the common head, then one evidence commit

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"

test -f "$CUSTODY/tools/check_census.py" \
  || die 'check_census.py is absent: re-run section 2.2 before authoring'

author_logs=()
for pack in "${PACKS[@]}"; do
  label=$(basename "$pack")
  capture "040-author-$label" "$PY" scripts/author_arm_readiness_evidence.py --pack-root "$pack"
  expect_rc "040-author-$label" 0 || die "author rc for $label"
  no_traceback "040-author-$label" || die "author traceback for $label"
  author_logs+=("$TRANS/040-author-$label.stdout.json")
done
test "${#author_logs[@]}" = 3 || die "expected three author logs, have ${#author_logs[@]}"
"$PY" "$CUSTODY/tools/check_census.py" "${author_logs[@]}" \
  > "$TRANS/041-applicability-census.json" || die 'applicability census failed'
git add -- "${PACKS[@]}"
git commit -m 'S-0 common-head R1 evidence for all v4 packs'
EVIDENCE_COMMIT=$(git rev-parse HEAD)
git update-ref refs/remotes/origin/main "$EVIDENCE_COMMIT"
record_env EVIDENCE_COMMIT "$EVIDENCE_COMMIT"
printf '%s\n' "$EVIDENCE_COMMIT" > "$TRANS/042-evidence-commit.txt"
```

The `test "${#author_logs[@]}" = 3` line is the direct guard against the r2
defect class: a loop that silently processed fewer packs than it claimed. Every
loop below that accumulates results carries the same cardinality assertion.

Expected: each output is PASS/`mutated:true`, with exactly the eleven kinds in
§2.2; the commit adds 11 source JSON + 11 receipt JSON + 11 sidecars per pack.
Authority: R4 r4-2, r4-3; R5 V-1.ii, V-1.iii; author CLI `:25-112`;
implementation `arm_readiness_evidence.py:2379-2618`.

### 3.5 Mandatory sacrificial pre-mint refusal check

Pinned mechanics answer the poison question **YES**: `generate_freeze_receipt`
evaluates refusals and then unconditionally writes and plan-pins the PASS **or**
REFUSE receipt at `arm_readiness.py:6978-7024`; replay authenticates and returns
that conclusion through `_load_freeze_reference` `:6475-6691`. Therefore, before
touching the primary clone's unbuilt freeze slots, mint all three in a
sacrificial clone and require PASS.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

PREFLIGHT=$(new_case pre-mint-clean "$EVIDENCE_COMMIT")
minted=0
for pack in "${PACKS[@]}"; do
  label=$(basename "$pack")
  set +e
  "$PY" "$PREFLIGHT/scripts/generate_arm_readiness.py" freeze \
    --pack-root "$PREFLIGHT/$pack" \
    --predecessor-pack-root "$PREFLIGHT/${PRED_OF[$pack]}" \
    > "$TRANS/050-preflight-$label.stdout.json" \
    2> "$TRANS/050-preflight-$label.stderr.txt"
  rc=$?
  set -e
  printf '%s\n' "$rc" > "$TRANS/050-preflight-$label.rc"
  test "$rc" = 0 || die "sacrificial preflight refused for $label (rc $rc): STOP before primary mint"
  "$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="PASS" and d["mutated"] is True and not d["reason_codes"], d' \
    "$TRANS/050-preflight-$label.stdout.json" || die "preflight not clean PASS for $label"
  minted=$((minted + 1))
done
test "$minted" = 3 || die "preflight minted $minted packs, expected 3"
```

Any REFUSE here is a **STOP before primary mint**. Authority: R4 r4-2 poison
question; R5 V-2; `arm_readiness.py:6475-6691,6760-6806`.

### 3.6 Primary freeze ×3 and freeze commit

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"

frozen=0
for pack in "${PACKS[@]}"; do
  label=$(basename "$pack")
  capture "060-freeze-$label" "$PY" scripts/generate_arm_readiness.py freeze \
    --pack-root "$pack" --predecessor-pack-root "${PRED_OF[$pack]}"
  expect_rc "060-freeze-$label" 0 || die "primary freeze rc for $label"
  no_traceback "060-freeze-$label" || die "primary freeze traceback for $label"
  "$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="PASS" and d["mutated"] is True and not d["reason_codes"] and d["receipt_path"].endswith("freeze-0004.json"), d' \
    "$TRANS/060-freeze-$label.stdout.json" || die "primary freeze not clean PASS for $label"
  frozen=$((frozen + 1))
done
test "$frozen" = 3 || die "froze $frozen packs, expected 3"
git add -- "${PACKS[@]}"
git commit -m 'S-0 freeze-0004 receipts for all v4 packs'
FREEZE_COMMIT=$(git rev-parse HEAD)
git update-ref refs/remotes/origin/main "$FREEZE_COMMIT"
record_env FREEZE_COMMIT "$FREEZE_COMMIT"
printf '%s\n' "$FREEZE_COMMIT" > "$TRANS/061-freeze-commit.txt"
```

Expected per pack: `status:PASS`, `mutated:true`, `freeze-0004.json`, its
sidecar, and updated `plan_tree.json`/sidecar. The predecessor path is supplied;
all IDs, hashes and ordinal 0004 are derived by code
(`arm_readiness.py:6372-6407`, `:6749-7025`). A primary REFUSE here is
recoverable only by abandoning this clone and restarting from `$EVIDENCE_COMMIT`
— §4(i) proves the refusal is plan-pinned. Authority: R4 r4-2, r4-3; R5 V-1.iv,
V-1.v; RH-8.

### 3.6.1 Authenticate the executing custody tools — before any tool runs

Every custody tool executes from `$CLONE/scripts/`. Before the first one runs,
each executing file's SHA-256 must equal the digest the reviewed manifest
records for its repo-relative path. This is the same comparison the library
performs internally in candidate mode (`arm_readiness.py:10430-10518`); doing it
here first means a mismatch stops S-0 at a named step instead of surfacing as a
`tool_mismatch` refusal in the middle of the marker build.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

"$PY" - "$CLONE" "$MANIFEST" <<'PY'
import hashlib, json, pathlib, sys
clone, manifest_path = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
recorded = json.loads(manifest_path.read_bytes())["custody_tools"]
expected = {
 "scripts/build_v4_histsem_pinset.py",
 "scripts/build_family_marker.py",
 "scripts/verify_family_marker.py",
 "scripts/verify_receipt_histsem.py",
}
assert set(recorded) == expected, sorted(set(recorded) ^ expected)
for relative, digest in sorted(recorded.items()):
    executing = clone / relative
    actual = hashlib.sha256(executing.read_bytes()).hexdigest()
    assert actual == digest, (relative, actual, digest)
    # The builder is located as a SIBLING of the executing consumer
    # (arm_readiness.py:11017), so both must live in the same directory.
    assert executing.parent == clone / "scripts", executing
print(json.dumps({"status": "PASS", "tools_authenticated": len(recorded),
                  "lane": "candidate", "rule": "manifest digest, not committed blob"},
                 indent=2, sort_keys=True))
PY
"$PY" - "$CLONE" "$MANIFEST" <<'PY'
import hashlib, json, pathlib, sys
clone, manifest_path = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
inputs = json.loads(manifest_path.read_bytes())["custody_inputs"]
relative = "docs/process_traces/2026-08-22-t20/s0-fixation-delta.patch"
actual = hashlib.sha256((clone / relative).read_bytes()).hexdigest()
assert inputs[relative] == actual, (actual, inputs[relative])
sidecar = (clone / f"{relative}.sha256").read_text().split()[0]
assert sidecar == actual, (sidecar, actual)
print(json.dumps({"status": "PASS", "fixation_delta_sha256": actual}, indent=2, sort_keys=True))
PY
```

Authority: MARKER-RULING split S-5; S-1 MANIFEST §§6 and 9.1 G-4; AUDIT F-1.

### 3.7 Mint the versioned successor and close the 112-path allowlist contract

The reviewed custody tool executes from the clone. Its exact interface:

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

test ! -e "$CLONE/$SUCCESSOR_PINSET" || die 'successor pinset output path is create-only and already exists'
"$PY" "$CLONE/scripts/build_v4_histsem_pinset.py" \
  --repository "$CLONE" \
  --base-pinset "$CLONE/$BASE_PINSET" \
  --historical-head "$EVIDENCE_DERIVATION_HEAD" \
  --current-head "$FREEZE_COMMIT" \
  --pack-root "$FIRST_PACK" --pack-root "$SECOND_PACK" --pack-root "$THIRD_PACK" \
  --output "$CLONE/$SUCCESSOR_PINSET" \
  > "$TRANS/070-build-v4-pinset.json" || die 'successor pinset build refused; see 070'
```

`--historical-head` is `$EVIDENCE_DERIVATION_HEAD`, not `$EVIDENCE_COMMIT`:
§3.4 authors every generic receipt AT the derivation head, so that is the
coordinate each receipt's `derivation_commit` records and the only value the
builder's receipt-coordinate check accepts, while the same head satisfies the
pre-authoring check because §3.2's U11 projection custody -- committed before
authoring -- is excluded from that test (`_HISTSEM_AUTHORING_CUSTODY_DIRECTORIES`);
`$EVIDENCE_COMMIT` is the post-authoring commit and fails the pre-authoring
check outright.

The output path is create-only and must be absent before the command. The v1
artifact is an immutable member 1 of the code-enumerated chain
(`arm_readiness.py:3285-3345`) and is never modified. The successor is member 2
and carries exactly one row per `_v4` pack (three rows, 33 receipts total), with
no `(pack_id, pack_path)` duplicated across chain members; a tool that copies
the nine v1 rows into the successor is refused by the chain-integrity rule at
`:3332-3337`. Each new row derives `freeze-0004`, current and historical pack
hashes, plan hashes, receipt inventory and post-authoring delta from local Git
objects, sets `receipt_count:11`, and refuses network or fetch. Authority:
D-151 conditions 1, 3 and 6; `docs/contracts/d117_step6_confirmation_table.md`
exact `successor_pinset` schema; S-1 MANIFEST §§2.4 and 3.

The builder and verifier transcripts must adjudicate every normative-annex
component, not merely emit schema-valid JSON: mandatory `facts[].source_sha256`;
K5 historical recomputation against each receipt's recorded pack digest; K12
pinned current-tree digest; K7 zero-delete/custody-add/freeze-retarget delta
envelope as bootstrap hardening; the historical-versus-HEAD coordinate split;
derivation ancestry with `origin/main` hard in this clone-proof lane;
predecessor binding and predecessor-mode freeze gate; the HEAD differential
self-test using the unchanged pack-digest framing; and no fetch, repair,
checkout swapping, or network. K5 and K12 are load-bearing; K7 is layered
bootstrap hardening, never sole closure. Authority: RH-8 ruled design items 1–8
and normative annexes, especially consolidated items D2–D8 and D10–D15.

**Step 2 — assert the minted shape and close the ALLOWLIST CONTRACT.**

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

"$PY" - "$CLONE/$SUCCESSOR_PINSET" "$TRANS/070-build-v4-pinset.json" <<'PY'
import json,sys
pinset=json.load(open(sys.argv[1])); build=json.load(open(sys.argv[2]))
assert build["status"] == "PASS", build
assert len(pinset["packs"]) == 3, len(pinset["packs"])
assert sum(row["receipt_count"] for row in pinset["packs"]) == 33
assert {row["pack_id"] for row in pinset["packs"]} == {
 "d117_contrast_qwen25_1p5b_vs_7b_v4",
 "d117_floor_qwen25_1p5b_v4",
 "d117_floor_qwen25_7b_v4",
}
PY
git -C "$CLONE" diff --exit-code -- "$BASE_PINSET" || die 'the v1 pinset member was modified'
git -C "$CLONE" add -- "$SUCCESSOR_PINSET"
git -C "$CLONE" commit -m 'S-0 mint v4 historical-semantics successor pinset'
PINSET_MINT_HEAD=$(git -C "$CLONE" rev-parse HEAD)
git -C "$CLONE" update-ref refs/heads/main "$PINSET_MINT_HEAD"
git -C "$CLONE" update-ref refs/remotes/origin/main "$PINSET_MINT_HEAD"
record_env PINSET_MINT_HEAD "$PINSET_MINT_HEAD"
# PINSET_COMMIT is the same commit under its transaction-facing name; both are
# recorded so downstream text can use whichever reads better at its site.
record_env PINSET_COMMIT "$PINSET_MINT_HEAD"
printf '%s\n' "$PINSET_MINT_HEAD" > "$TRANS/071-pinset-mint-head.txt"
```

**Step 3 — close the contract at exactly 112 and verify the present chain.**

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

"$PY" "$CUSTODY/tools/s0_allowlist_contract.py" \
  --registry "$REGISTRY" --repo "$CLONE" \
  --derivation "$EVIDENCE_DERIVATION_HEAD" --head "$PINSET_MINT_HEAD" \
  > "$TRANS/090-final-allowlist-contract.json" || die 'the 112-path window did not close; see 090'
capture 072-histsem-present "$PY" "$CLONE/scripts/verify_receipt_histsem.py" \
  --repository-root "$CLONE" --require-published \
  --pack-root "$FIRST_PACK" --pack-root "$SECOND_PACK" --pack-root "$THIRD_PACK"
expect_rc 072-histsem-present 0 || die 'present-chain verification did not PASS'
no_traceback 072-histsem-present || die 'present-chain verification traceback'

# S0-O3 cure: record the successor pinset digest from the bytes COMMITTED at
# the mint head, at the moment the digest first exists.  Section 3.8 compares
# Ed's confirmed table against this record, and section 4.10 proves the bytes
# never moved between mint and fixation.  The 074 ordinal is
# positional-historic: it rides with the fixation family that D-153 moved to
# section 4.10, and it keeps its number so every existing consumer reads the
# same transcript name.
"$PY" - "$CLONE" "$PINSET_MINT_HEAD" > "$TRANS/074-successor-sha256.txt" <<'PY'
import hashlib, subprocess, sys
raw = subprocess.run(
    ["git", "-C", sys.argv[1], "show",
     sys.argv[2] + ":configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json"],
    check=True, capture_output=True).stdout
print(hashlib.sha256(raw).hexdigest())
PY
test -s "$TRANS/074-successor-sha256.txt" || die 'the successor digest record is empty'
```

`090-final-allowlist-contract.json` closes the changed-set window at exactly 112.
The successor is the sole digest-conditional class: allowlist membership makes it
eligible for subtraction but never authenticates it. Until Ed confirms the
unified step-6 table's `C → S` edge, no claim-bearing arm may use it. The
changed-set contract is a property of this closed window, not a standing
repository invariant, and no authenticator path enters it. Authority: D-151
conditions 2, 5, 7 and 8.

The 112-path allowlist contract is now closed at `$PINSET_MINT_HEAD`. **Fixation
does NOT happen here.** Under D-153 A1 "window close" is the r4-3 commit-freeze
close, and fixation is the first commit after *that*; the mint-side event this
section performs is the ALLOWLIST-CONTRACT CLOSURE, whose head is
`$PINSET_MINT_HEAD` (D-153 A6). The fixation steps therefore run at the very end
of this runsheet, in §4.10, after the probe battery. Everything between here and
there — the marker, the arm and verify, the local green record, and every probe
— executes at `$PINSET_MINT_HEAD`, on a tree that does NOT yet contain the
fixation commit. That is what makes the arm clean; see §3.9.

### 3.8 Family marker — D-150 option (a) only, custody-external

D-150 leaves one legal branch: `BUILD-AT-BOUNDARY`, CUSTODY-EXTERNAL. It
contributes no tracked path and leaves the contract at 112.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

test "$MARKER_BRANCH" = 'BUILD-AT-BOUNDARY' \
  || die "manifest marker_branch is $MARKER_BRANCH, not BUILD-AT-BOUNDARY"
printf '%s\n' "$MARKER_BRANCH" > "$TRANS/080-marker-decision.txt"
```

> **STOP — S0-O2. The candidate marker build cannot satisfy the C→S condition,
> and the block order below is NOT the cause.** Estate 5 ran clean through the
> mint and then refused here; recorded, not decided.
>
> *The observed refusal* (estate 5, transcript 081):
> check_id evidence_set_mismatch, reason readiness_r1_family_publication,
> detail "digest-conditional allowlist path
> 'configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json': no expected
> confirmation digest supplied".
>
> *The supply-line trace, end to end.* build_family_publication_marker calls
> _family_member at arm_readiness.py:10707 as
> _family_member(repository, root, registry, reference) — with NEITHER
> step6_confirmation_table NOR expected_confirmation_digest, both of which
> default to None. _family_member forwards those Nones into
> _load_freeze_reference (:10418-10420), whose R1 lifecycle evaluation reaches
> the digest-conditional allowlist path because the successor was minted into
> the changed set at PINSET_MINT_HEAD. _require_confirmed_conditional_path then
> calls _authenticate_confirmation_table(None, None), which raises
> confirmation_missing at :10686-10689. The FamilyPublicationError is caught at
> :10422-10427 and re-raised as evidence_set_mismatch. **There is no supply
> line**: build_family_marker.py's CLI has no --confirmation and no
> --expected-confirmation-digest flag, and build_family_publication_marker does
> not accept either parameter. The verifier has both flags and passes them at
> :10806-10817 — but suppresses them when phase is candidate.
>
> *Why reordering the blocks below does NOT fix it, and would make things
> worse.* The step-6 contract is explicit that the table C contains hM in
> family_publication and hS in successor_pinset, that the only edges are C→M and
> C→S, and that "neither M nor S names C, so the graph is acyclic" — the marker
> binds this table's contract identifier and the required decision YES, "never
> the table path, digest, or event time"
> (docs/contracts/d117_step6_confirmation_table.md:21-25). So the table can only
> be rendered AFTER the marker exists, because it carries the marker's digest.
> Building the table first would require the marker first, which is the cycle
> the contract says does not exist. The contract's own enforcement clause names
> the entry points that supply the table as "the arm, freeze, verification, and
> marker-REPLAY entry points" (:143-160) — marker-BUILD is deliberately absent
> from that list. **The block order below is contract-correct and is left
> unchanged.**
>
> *What this leaves.* The defect is code-side: the marker build evaluates a
> condition that, by contract, it must not be able to satisfy. Two candidate
> cures, neither taken here because both touch manifest-pinned custody and
> contract semantics: (i) the marker build suppresses the C→S conditional the
> way the verifier does for the candidate phase, so a minted successor in the
> changed set is not evaluated at build time; or (ii) build_family_marker.py
> gains the verifier's two flags and the runsheet supplies the table on the
> replay path only. (i) matches the contract's acyclicity argument; (ii)
> contradicts it unless restricted to replay.
>
> *Estate resumption.* Estate 5 holds at block-21-complete. The refusal was
> fail-closed — the marker-candidate directory is empty and no clone mutation
> occurred — so once the code question is ruled the estate RESUMES at this
> section unchanged. **No re-cut and no re-ordering are required**, and none of
> §§1-3.7's completed work is invalidated.

After freeze ×3 and successor verification, and **before** fixation, run the
reviewed constructor and consumer in explicit **candidate** mode. (Under D-153
A1 fixation is the last commit of this clone proof, in §4.10; r4 said "and
fixation" here, which was pre-D-153 residue.) Candidate-mode tool
authentication compares the executing bytes — in `$CLONE/scripts/` — to the
digests recorded in `$MANIFEST`; it does not use committed-blob equality and
cannot be selected by sidecar presence (`arm_readiness.py:10477-10518`). The S-0
marker stays outside the Git worktree.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

mkdir -p "$CUSTODY/marker-candidate"
"$PY" "$CLONE/scripts/build_family_marker.py" \
  --repository "$CLONE" --head "$PINSET_MINT_HEAD" \
  --pack-root "$FIRST_PACK" --pack-root "$SECOND_PACK" --pack-root "$THIRD_PACK" \
  --output "$CUSTODY/marker-candidate/d117_family_publication_v4.json" \
  --phase candidate \
  --candidate-manifest "$MANIFEST" \
  > "$TRANS/081-marker-build.json" || die 'marker build refused; see 081'
test -f "$CUSTODY/marker-candidate/d117_family_publication_v4.json.sha256" \
  || die 'marker sidecar was not written'

"$PY" "$CLONE/scripts/verify_family_marker.py" \
  --repository "$CLONE" \
  --marker "$CUSTODY/marker-candidate/d117_family_publication_v4.json" \
  --phase candidate \
  --candidate-manifest "$MANIFEST" \
  > "$TRANS/082-marker-verify.json" || die 'marker verification refused; see 082'

FORGED_ORIGIN_MAIN_OID=$(git -C "$CLONE" rev-parse refs/remotes/origin/main)
record_env FORGED_ORIGIN_MAIN_OID "$FORGED_ORIGIN_MAIN_OID"
"$PY" - "$TRANS/082-marker-verify.json" "$FORGED_ORIGIN_MAIN_OID" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
assert d["status"] == "PASS", d
assert d["phase"] == "candidate" and d["lane"] == "candidate", d
assert d["gate_admissible"] is False and d["publication_authorized"] is False, d
assert d["consulted_git"]["origin_main_commit"] == sys.argv[2], d["consulted_git"]
PY
# S0-O2 cure: the marker BUILD defers the C-to-S conditional rather than
# refusing, and must DISCLOSE that it did.  An empty deferred_paths list is the
# positive statement that nothing was deferred, so the field is never absent --
# which is why this asserts its shape rather than its presence alone.  At this
# point in the transaction the successor has been minted into the changed set,
# so it is exactly the one path expected to be deferred.
"$PY" - "$CUSTODY/marker-candidate/d117_family_publication_v4.json" "$SUCCESSOR_PINSET" <<'MARKERPY'
import json, sys
marker = json.load(open(sys.argv[1]))
successor = sys.argv[2]
disclosure = marker["conditional_paths_deferred"]
assert disclosure["gate"] == "R1_DIGEST_CONDITIONAL", disclosure
assert disclosure["deferred_paths"] == [successor], disclosure
assert disclosure["deferred_paths"] == sorted(disclosure["deferred_paths"]), disclosure
assert disclosure["enforced_at_entry_points"] == [
    "arm", "freeze", "verification", "marker-replay",
], disclosure   # the contract's four enforcing entry points; build is absent
print(json.dumps({"status": "PASS", "deferral_disclosed": disclosure["deferred_paths"],
                  "gate": disclosure["gate"]}, indent=2, sort_keys=True))
MARKERPY

# F14: this transcript classifies the MARKER's forged-ref conditionality, not
# the local suite.  §3.10 writes the local-green classification to
# 094-local-green-classification.txt; two files sharing a basename stem while
# meaning different things is how §5 came to cite them as if they were one
# family.  The name states which is which.
printf 'FORGED_ORIGIN_MAIN_OID=%s\nclassification=forged-ref-conditional; not published PASS\n' \
  "$FORGED_ORIGIN_MAIN_OID" > "$TRANS/084-marker-forged-ref-classification.txt"
```

Expected marker schema: `joulewise.d117_family_publication_marker.v1`, all three
exact pack IDs, `freeze-0004` receipt IDs and hashes, common Git head and tree,
the required `conditional_paths_deferred` disclosure, and candidate consumer
PASS. That disclosure is the S0-O2 cure made visible: the marker BUILD has no
contract-sanctioned access to `hC` (the table carries the marker's digest, so it
cannot precede the marker), so instead of refusing it DEFERS the C→S conditional
and records what it deferred — the gate identifier `R1_DIGEST_CONDITIONAL`, the
sorted `deferred_paths`, and the entry points where the condition IS enforced.
An empty `deferred_paths` is the positive statement that nothing was deferred,
which is why the key is required rather than optional. At this point the
successor is in the changed set, so `deferred_paths` is exactly the successor
pinset path. The verification transcript must carry
`lane: "candidate"` and `gate_admissible: false`; a candidate receipt can never
gate publication. Authority: MARKER-RULING ratified items 1–3 and S-4, plus
Consequences; D-151 condition 4.

The marker and successor are the two immutable consumers of the unified table
`joulewise.d117_step6_confirmation_table.v1`. The table is custody-external and
has exactly the two edges `C → M` and `C → S`; its path is an authenticator and
never enters any allowlist. The lead renders the exact canonical candidate table
and GNU sidecar according to the ONE HOME,
`docs/contracts/d117_step6_confirmation_table.md`, presents digest `hC` to Ed,
and stops until Ed's YES names that digest. The literal YES is already in the
immutable bytes Ed hashes; no timestamp or self-digest is added.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

STEP6_CANDIDATE="$CUSTODY/step6-candidate/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_CANDIDATE" || die 'the rendered step-6 candidate table is absent'
test -f "$STEP6_CANDIDATE.sha256" || die 'the step-6 candidate sidecar is absent'
# ED_STEP6_CONFIRMED_SHA256 is transcribed from Ed's out-of-band YES over hC and
# pasted into THIS block; it is deliberately not recorded in env.sh.
test -n "${ED_STEP6_CONFIRMED_SHA256:-}" || die "Ed's step-6 confirmation digest is not set"
test "$(shasum -a 256 "$STEP6_CANDIDATE" | awk '{print $1}')" = "$ED_STEP6_CONFIRMED_SHA256" \
  || die 'the rendered table does not match the digest Ed confirmed'

"$PY" - "$CLONE" "$STEP6_CANDIDATE" \
  "$CUSTODY/marker-candidate/d117_family_publication_v4.json" \
  "$SUCCESSOR_PINSET" "$PINSET_MINT_HEAD" <<'PY'
import hashlib,json,pathlib,sys
root=pathlib.Path(sys.argv[1]); table_path=pathlib.Path(sys.argv[2])
marker_path=pathlib.Path(sys.argv[3]); successor=sys.argv[4]; head=sys.argv[5]
sys.path.insert(0, str(root))
from joulewise import arm_readiness as r
raw=table_path.read_bytes(); table=r.validate_step6_confirmation_table(
 r.parse_json_bytes(raw, require_canonical=True))
assert table_path.with_name(table_path.name+".sha256").read_bytes() == r.gnu_sidecar(
 hashlib.sha256(raw).hexdigest(), table_path.name)
assert table["git"]["head_commit"] == head
assert table["registry"]["registry_id"] == "d117-row-registry-v2"
assert table["registry"]["path"] == "configs/arm_readiness/d117_row_registry_v2.json"
assert table["family_publication"]["marker"]["sha256"] == hashlib.sha256(marker_path.read_bytes()).hexdigest()
assert table["successor_pinset"]["path"] == successor
assert table["successor_pinset"]["sha256"] == hashlib.sha256((root/successor).read_bytes()).hexdigest()
assert table["successor_pinset"]["pack_count"] == 3
assert table["successor_pinset"]["receipt_count"] == 33
PY
printf '%s\n' "$ED_STEP6_CONFIRMED_SHA256" > "$TRANS/085-ed-step6-confirmed-sha256.txt"

# The successor digest Ed confirmed must equal the MINT-TIME successor digest
# recorded at §3.7 step 3.  Nothing is pinned yet at this point in the
# transaction: §4.10 has not run, so there is no fixation pin to compare
# against.  What §4.10 then proves is the other half — that the bytes did not
# move between this comparison and the substitution.
test "$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["successor_pinset"]["sha256"])' \
  "$STEP6_CANDIDATE")" = "$(cat "$TRANS/074-successor-sha256.txt")" \
  || die "Ed's table names a successor digest different from the mint-time record (074)"
```

The `sys.path.insert` in that block is required: `$PY` is the estate venv and
`joulewise` is importable only from the clone. R2 omitted it and would have
raised `ModuleNotFoundError`.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

STEP6_CANDIDATE="$CUSTODY/step6-candidate/d117_step6_confirmation_table_v4.json"
PUBLISHED_DIR="$CUSTODY/windows/family_publication"
mkdir -p "$PUBLISHED_DIR"
cp -p "$CUSTODY/marker-candidate/d117_family_publication_v4.json" \
  "$CUSTODY/marker-candidate/d117_family_publication_v4.json.sha256" \
  "$PUBLISHED_DIR/"
cp -p "$STEP6_CANDIDATE" "$PUBLISHED_DIR/d117_step6_confirmation_table_v4.json"
cp -p "$STEP6_CANDIDATE.sha256" "$PUBLISHED_DIR/d117_step6_confirmation_table_v4.json.sha256"
cmp "$CUSTODY/marker-candidate/d117_family_publication_v4.json" \
  "$PUBLISHED_DIR/d117_family_publication_v4.json" || die 'marker promotion is not byte-exact'
cmp "$STEP6_CANDIDATE" "$PUBLISHED_DIR/d117_step6_confirmation_table_v4.json" \
  || die 'table promotion is not byte-exact'
```

Promotion copies exact immutable bytes; it never edits either consumer or the
table. Authority: D-151 conditions 2–3; MARKER-RULING ratified items 1–2.

### 3.9 Arm and verify all three at the allowlist-contract closure head

The exact 112 allowlist contract was closed at `$PINSET_MINT_HEAD` in §3.7, and
this section runs at that same head: under D-153 the fixation commit is made
last, in §4.10, so it is not present here and cannot enlarge anything. This clone proof
may arm only after the exact marker and Ed-confirmed table have been placed in
`$CUSTODY/windows/family_publication`. Any arm or verify result here is
non-claim-bearing and forged-ref-conditional; publication acceptance is the
separate published-green step in §3.10.

**Pre-declared expected refusal.** Under the stdlib `$PY`, the
`u11-arm-reverification` leg refuses with
`readiness_identity_artifact_unreadable` (`arm_readiness.py:7655` calls
`_run_identity_arm_reverification`, defined at `:5235`, which resolves the
runtime backend the same way §3.2 does). That refusal is EXPECTED and admissible here — the eleven
asserted `want` kinds below exclude the identity item — and it is pre-declared
so it is never read as a finding. Live arm-side U11 re-verification is proven by
the real transaction in the measurement environment, not by S-0.

**Early governed refusal tolerance.** `generate_arm_receipt` can return a
governed REFUSE with `receipt_path: null` before it writes any receipt (for
example when the family-publication or histsem gate refuses at
`arm_readiness.py:7537`). R2 asserted `d["receipt_path"]` unconditionally and
would have died on that shape. The block below records the null case, skips the
paired `verify` for that pack, and continues; a null receipt path for **all
three** packs is a STOP, because then nothing was armed at all.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# ---- CONFIRMATION PAIR — the standard post-mint preamble (ruling R-2) ----
# Every post-mint ENFORCING consumer needs BOTH halves of the step-6 pair:
#   C  = the promoted confirmation table (a file path), and
#   hC = ED_STEP6_CONFIRMED_SHA256, the digest Ed confirmed OUT OF BAND.
# _authenticate_confirmation_table refuses if EITHER is None, and that refusal
# carries the same registry code an ordinary changed path produces.  r4 handed
# neither half to any live consumer, so all three of estate 6's arms refused
# here with "no expected confirmation digest supplied" and no assertion in the
# instrument could tell that apart from the refusal the step was testing for.
#
# hC is RE-PASTED BY THE OPERATOR INTO THIS BLOCK, exactly as in §3.8.  It is
# never written to env.sh and never carried across blocks, because the
# contract's image is that the operator supplies the digest to each consumer
# through that consumer's own explicit input, and the rehearsal must rehearse
# that.  A mistyped paste fails loudly at the next line; an in-band supply
# would fail silently, as a norm.
#
# $TRANS/085-ed-step6-confirmed-sha256.txt is the WITNESS of the §3.8 paste,
# NEVER THE SOURCE.  It is read only to compare against what the operator has
# just typed, which turns a transcription slip into an immediate, well-named
# refusal.  No block in this runsheet recovers hC from 085.
STEP6_TABLE="$CUSTODY/windows/family_publication/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_TABLE" || die 'the promoted step-6 confirmation table is absent'
test -n "${ED_STEP6_CONFIRMED_SHA256:-}" \
  || die "Ed's step-6 confirmation digest (hC) is not pasted into this block"
"$PY" -c 'import re,sys; raise SystemExit(0 if re.fullmatch("[0-9a-f]{64}", sys.argv[1]) else 1)' \
  "$ED_STEP6_CONFIRMED_SHA256" \
  || die 'ED_STEP6_CONFIRMED_SHA256 is not a lowercase 64-hex digest'
test "$ED_STEP6_CONFIRMED_SHA256" = "$(cat "$TRANS/085-ed-step6-confirmed-sha256.txt")" \
  || die 'the pasted hC differs from the 085 witness of the §3.8 confirmation'
# -------------------------------------------------------------------------

FINAL_HEAD=$(git -C "$CLONE" rev-parse HEAD)
# Under D-153 the arm runs at the ALLOWLIST-CONTRACT CLOSURE head, BEFORE the
# fixation commit (which §4.10 makes last).  This is what makes the arm clean.
test "$FINAL_HEAD" = "$PINSET_MINT_HEAD" \
  || die 'HEAD is not the allowlist-contract closure head; fixation must not have run yet'
record_env FINAL_HEAD "$FINAL_HEAD"
record_env PROBE_BASE "$FINAL_HEAD"

ARM_CONTEXT=$("$PY" -c 'import json,sys; r=sys.argv[1]; print(json.dumps({
"bracket_session_id":"s0-clone-proof", "pre_attempt_id":"s0-pre",
"post_attempt_id":"s0-post", "clock_route":"MANUAL",
"claim_runs_root":r+"/claim", "bound_runs_root":r+"/bound",
"custody_root":r+"/custody", "quarantine_root":r+"/quarantine",
"claim_backup_destination":r+"/backup-claim",
"bound_backup_destination":r+"/backup-bound", "waiver_path":r+"/waivers.json"}))' \
  "$CUSTODY/arm-context")
record_env ARM_CONTEXT "$ARM_CONTEXT"

armed=0
receipts=0
for pack in "${PACKS[@]}"; do
  label=$(basename "$pack")
  # The table path resolves from --window-custody-root; hC is the half the CLI
  # cannot derive, so it is passed explicitly on every arm.
  capture "091-arm-$label" "$PY" "$CLONE/scripts/generate_arm_readiness.py" arm \
    --pack-root "$CLONE/$pack" --arm-context "$ARM_CONTEXT" \
    --window-custody-root "$CUSTODY/windows" \
    --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256"
  no_traceback "091-arm-$label" || die "arm traceback for $label"
  if grep -F 'no expected confirmation digest supplied' \
      "$TRANS/091-arm-$label.stdout.json" "$TRANS/091-arm-$label.stderr.txt" > /dev/null; then
    die "arm for $label refused for want of hC: the confirmation pair did not reach the gate"
  fi
  rc=$(cat "$TRANS/091-arm-$label.rc")
  if [ "$rc" != 0 ] && [ "$rc" != 1 ]; then
    die "arm rc=$rc for $label (2 means a raised ArmReadinessError, not a governed refusal)"
  fi
  armed=$((armed + 1))
  ARM_RECEIPT=$("$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("receipt_path") or "")' \
    "$TRANS/091-arm-$label.stdout.json")
  if [ -z "$ARM_RECEIPT" ]; then
    printf 'pack=%s rc=%s receipt_path=null (early governed refusal; verify skipped)\n' \
      "$label" "$rc" >> "$TRANS/096-early-governed-refusals.txt"
    continue
  fi
  receipts=$((receipts + 1))
  capture "092-verify-$label" "$PY" "$CLONE/scripts/generate_arm_readiness.py" verify \
    --pack-root "$CLONE/$pack" --arm-receipt "$ARM_RECEIPT" \
    --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256"
  no_traceback "092-verify-$label" || die "verify traceback for $label"
  if grep -F 'no expected confirmation digest supplied' \
      "$TRANS/092-verify-$label.stdout.json" "$TRANS/092-verify-$label.stderr.txt" > /dev/null; then
    die "verify for $label refused for want of hC: the confirmation pair did not reach the gate"
  fi
  vrc=$(cat "$TRANS/092-verify-$label.rc")
  if [ "$vrc" != 0 ] && [ "$vrc" != 1 ] && [ "$vrc" != 2 ]; then
    die "verify rc=$vrc for $label"
  fi
done
test "$armed" = 3 || die "armed $armed packs, expected 3"
test "$receipts" != 0 || die 'every pack refused before writing an arm receipt: nothing was armed'
printf 'armed=%s receipts_written=%s\n' "$armed" "$receipts" > "$TRANS/097-arm-cardinality.txt"
```

The arm may be GO only if all non-S-0 custody and T0 prerequisites are
legitimately present. Otherwise a **governed**, non-null arm receipt and
canonical verify REFUSE (often `readiness_dependency_refused`) is acceptable;
S-0 must not fabricate T0 or measurement evidence.

**The eleven-kind census IS asserted at §3.9, and it reaches the arm receipt by
a route worth naming.** r4's first draft said it was,
and the delta re-audit corrected that: `arm`'s own *discovery* does find zero
generic items (it calls `_discover_evidence` with `include_pack=False`,
`arm_readiness.py:7602`, and `_discover_evidence` drops the `PACK` namespace at
`:5655-5657`), yet the eleven kinds still reach the arm receipt by a second
route — `_freeze_evidence_for_arm` (`:6694-6746`) deep-copies the freeze
receipt's evidence, and `evidence_items.extend(freeze_items)` merges it at
**`:7643`**. A clean arm therefore *does* carry the eleven kinds. They are absent
today for one reason only: R4-O1's changed-set refusal empties `freeze_items` at
`:7633-7635`.

Two consequences, both binding:

- **Do not seed custody evidence** into
  `<window custody root>/<pack>/arm_readiness.evidence/` to make an arm-side
  census pass. The generic receipts live in the pack, which is where the ruled
  design puts them; seeding would fabricate the artifacts the proof exists to
  authenticate.
- **The census has RETURNED.** Packet 5 (D-153) restored a clean arm by putting
  fixation last, so `freeze_items` survives and `want <= kinds` over the arm
  receipt's `evidence[].receipt_kind` is asserted in the clean-arm block below.
  It was deferred for one revision, never retired.

Meanwhile the eleven kinds are asserted where they are proven unconditionally,
and both assertions already run earlier in this runsheet:

- **§3.4** — `check_census.py` asserts `sorted(authored_kinds) == want` over
  each of the three author outputs, PASS and `mutated:true`, transcript
  `041-applicability-census.json`. That is the authoring coordinate.
- **§3.6** — the clean freeze PASS is the discovery coordinate.
  `generate_freeze_receipt` calls `_discover_evidence` with the default
  `include_pack=True` (`:6943`), so the pack namespace IS scanned; a missing,
  unreadable, or inventory-violating evidence directory becomes a refusal and
  the freeze cannot return `status:PASS` with an empty `reason_codes`. §3.6
  asserts exactly that for all three packs, and a committed freeze receipt
  carries all eleven `receipt_kind` values plus `freeze_projection` (verified
  against `d117_floor_qwen25_1p5b_v3/…/freeze-0003.json`: twelve items, eleven
  generic kinds).

> **R4-O1 — RESOLVED by packet 5 (D-153), 2026-08-24.** Recorded here as the
> instrument's own history, because the resolution changed what this section
> asserts.
>
> *What it was.* Surfaced while curing N-2 and confirmed by the r4 delta
> re-audit: r4 armed at `$FIXATION_COMMIT`, where
> `tests/test_receipt_histsem.py` is a changed path outside the ruled 112 (all
> 112 are under `configs/`), so `validate_r1_evidence_lifecycle` raised
> `DEPENDENCY_CHANGED_SET` (`:4422-4465`) — which also emptied `freeze_items` at
> `:7633-7635` and took the eleven kinds out of the arm receipt with it. The
> interim ruling pre-declared that refusal as expected and pinned it to its
> cause.
>
> *What packet 5 settled.* D-153 finding 1: **the whole-tree R1 diff is intended
> design, not a defect.** Packet 5 never reopened a wrong ruling — it repaired a
> vocabulary collision and a sequencing trap around a correct gate. D-153
> finding 2: "window close" is the r4-3 commit-freeze close, and binding it to
> the mint commit is what created R4-O1; the mint-side head is renamed
> `PINSET_MINT_HEAD` (A6). D-153 A1 puts fixation after the window, and this
> runsheet consequently makes the fixation commit LAST, in §4.10.
>
> *What follows for this section.* The arm now runs at `$PINSET_MINT_HEAD`, a
> head with no fixation commit on it, so the changed set is fully allowlisted,
> the residue is EMPTY, `$CHANGED_CODE` does not appear, and `freeze_items`
> survives — which means **the eleven-kind census RETURNS** (D-153 W2). The
> interim form's expected-refusal machinery is gone; what replaces it is the
> clean-arm block below, which asserts the positive outcome directly.
>
> **ERRATUM (r5, 2026-08-24) — the CAUSE recorded above is REOPENED.** The
> original text is left exactly as it was written; this note is appended, not
> substituted. What is withdrawn is not the resolution but the *diagnosis of
> why* r4's arm refused. The record above attributes the
> `DEPENDENCY_CHANGED_SET` refusal to `tests/test_receipt_histsem.py` being a
> changed path outside the ruled 112. Opus finding F0 shows that attribution is
> UNPROVEN and probably wrong: inside `validate_r1_evidence_lifecycle` the
> digest-conditional loop raises **before** the ordinary-path check, and both
> raises carry the same registry role and therefore the same refusal code
> (`arm_readiness.py:4426-4465`). At any post-mint head where no `hC` was
> supplied — which is every head r4 armed at — the refusal is the C→S one
> regardless of what else is outstanding. r4 could not have noticed, because it
> asserted the refusal CODE alone. That is now mechanical: every R1 probe below
> also asserts the refusal DETAIL shape, requiring the string
> `digest-conditional allowlist path` to be ABSENT wherever an ordinary or
> manifest cause is claimed and PRESENT in `123-*`, where the C→S cause is the
> whole point of the probe. The next estate settles the attribution by
> execution rather than by inference. Authority:
> `docs/process_traces/2026-08-24-d153-sweep/01-opus-contract-lens-seat.md` F0;
> `03-MAGISTRATE-SYNTHESIS.md` item 18.

**The clean-arm block.** Three assertions, all now achievable because fixation
has not yet happened. The residue computation is the same arithmetic the gate
itself runs (`arm_readiness.py:4422-4465`), recomputed from primary evidence —
the registry allowlist, the real digest-conditional constant, and `git diff`.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

"$PY" - "$CLONE" "$REGISTRY" "$EVIDENCE_DERIVATION_HEAD" "$PINSET_MINT_HEAD" \
  > "$TRANS/098-clean-arm-residue.json" <<'PY'
import json, pathlib, subprocess, sys
clone, registry_path, derivation, head = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
sys.path.insert(0, clone)
from joulewise import arm_readiness as r   # the REAL digest-conditional constant

lifecycle = json.loads(pathlib.Path(registry_path).read_bytes())["freeze_evidence_lifecycle"]
allowlist = set(lifecycle["irrelevant_path_allowlist"])
assert len(allowlist) == 112, len(allowlist)
conditional = allowlist & set(r.R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS)
assert conditional == {"configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json"}, conditional

raw = subprocess.run(["git", "-C", clone, "diff", "--name-only", "-z",
                      f"{derivation}..{head}", "--"],
                     check=True, capture_output=True).stdout
changed = sorted(item for item in raw.decode().split("\0") if item)

# Exactly the gate's arithmetic at arm_readiness.py:4422-4465.
outstanding = set(changed) - (allowlist - conditional)
# Ed's confirmed table discharges the digest-conditional member.
residue = sorted(outstanding - conditional)

assert residue == [], {
    "residue": residue,
    "meaning": "a path outside the ruled 112 changed between the derivation head "
               "and the allowlist-contract closure; under D-153 this head must be "
               "clean, so this is a mechanism failure",
}
print(json.dumps({"status": "PASS", "changed_paths": len(changed),
                  "allowlisted": len(allowlist), "residue": [],
                  "ruling": "D-153: at PINSET_MINT_HEAD the changed set is fully "
                            "allowlisted; the arm is clean"},
                 indent=2, sort_keys=True))
PY
```

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

"$PY" - "$REGISTRY" "$CUSTODY/windows" <<'PY'
import json,pathlib,sys
reg=json.load(open(sys.argv[1]))["freeze_evidence_lifecycle"]
codes={x["role"]:x["code"] for x in reg["refusal_vocabulary"]}
# D-153: BOTH R1 codes are forbidden at a clean arm.  The interim ruling's
# "CHANGED_SET is expected" is withdrawn -- it was an artifact of arming at the
# fixation commit, which this runsheet no longer does.
bad={codes["DEPENDENCY_CHANGED_SET"],codes["DEPENDENCY_MANIFEST"]}
want={"ACCEPTANCE_OWNER","DOCTRINE_PIN","ESTIMATOR_IDENTITY","MINT_TRUST",
"MULTICELL_MINT","PACK_AUTHENTICATION","PACK_FAMILY","REASON_CODE_COVERAGE",
"RECEIPT_ORACLE","RECOVERY_LEDGER_TEST","THREE_WINDOW_REGRESSION"}
root=pathlib.Path(sys.argv[2])
# arm-0001 ONLY: section 4(e.1)'s probe mints arm-0002 into this same custody
# root (recorded there as deliberate custody mixing), so a bare arm-*.json glob
# would read a PROBE receipt as transaction evidence.
receipts=sorted(root.glob("*/arm_readiness.receipts/arm-0001.json"))
assert receipts, "no transaction arm receipt (arm-0001) under the window custody root"
seen=0
for path in receipts:
 d=json.load(open(path))
 present={r["code"] for r in d["refusals"]}
 forbidden=sorted(bad & present)
 assert not forbidden, (str(path), forbidden)
 # THE ELEVEN-KIND CENSUS, RETURNED (D-153 W2).  The kinds reach the arm
 # receipt through the freeze-item merge at arm_readiness.py:7643, which
 # survives now that no R1 refusal empties freeze_items.
 kinds={e.get("receipt_kind") for e in d["evidence"]}
 assert want <= kinds, (str(path), sorted(want-kinds))
 seen+=1
print(json.dumps({"status":"PASS","transaction_arm_receipts":seen,
 "ordinal_pinned":"arm-0001","eleven_kind_census":"PASS (returned under D-153)",
 "crossed_actual_gate":"arm_readiness.py:4426-4465",
 "forbidden_codes":sorted(bad)}, indent=2, sort_keys=True))
PY
```

**What the arm side then proves, under D-153.** Neither `$CHANGED_CODE` nor
`$MANIFEST_CODE` appears; no arm or verify transcript carries "no expected
confirmation digest supplied", so each one crossed the gate with the complete
`C + hC` pair rather than dying before it; the residue at `$PINSET_MINT_HEAD`
is empty; the arm receipt carries all eleven generic `receipt_kind` values; no
traceback occurs; and an arm receipt is written. The blocks above assert
exactly that.

Authority: R4 r4-2; R5 V-1.iii, V-2; actual changed-set site
`arm_readiness.py:4426-4465`; CLI exit semantics
`scripts/generate_arm_readiness.py:175-192`; AUDIT F-12.

### 3.10 Two-part green record — local conditional, then PUBLISHED

Run the complete local suite. Record the forged remote-ref OID beside the
result. Even at return code 0, this transcript's classification is
**`LOCAL GREEN — FORGED-origin/main-CONDITIONAL at <OID>`**; neither its
filename nor its prose may say "suite green" or "published green."

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"

test "$(git -C "$CLONE" rev-parse refs/remotes/origin/main)" = "$FORGED_ORIGIN_MAIN_OID" \
  || die 'the forged origin/main OID moved since the marker was verified'
set +e
"$PY" -m unittest discover -s tests > "$TRANS/093-local-forged-ref-conditional.txt" 2>&1
LOCAL_SUITE_RC=$?
set -e
test "$LOCAL_SUITE_RC" = 0 || die "local suite failed with rc $LOCAL_SUITE_RC; see 093"
printf 'classification=LOCAL GREEN — FORGED-origin/main-CONDITIONAL\noid=%s\n' \
  "$FORGED_ORIGIN_MAIN_OID" > "$TRANS/094-local-green-classification.txt"
```

Acceptance does **not** close here, and r5 corrects **which head** closes it.

**The published head is the WINDOW-CLOSE head, and fixation follows
publication.** r4 said acceptance waits until "the lead actually publishes the
accepted fixation head." That names the wrong commit and rebuilds the exact
collision D-153 A6 was written to break. Two ruled facts settle it. Under
**D-153 A1**, fixation is the FIRST COMMIT AFTER the r4-3 commit-freeze window
close — so the fixation commit does not exist yet when the window closes, and
the head that closes the window is the head that gets published. Under **D-153
A3**, the green being published is green *without* the byte pin: the pin's
value is the successor digest, which cannot be substituted before the mint that
produces it, so requiring the published head to carry the pin is requiring the
head to contain a value derived from itself. Binding publication acceptance to
the fixation head therefore recreates the sequencing trap; binding it to the
window-close head does not.

There is a mechanical corroboration inside the tool: publication-lane marker
replay refuses `head_unpublished` unless the marker's own
`publication_git.head_commit` equals live `origin/main`
(`arm_readiness.py:10913-10919`). The marker is built BEFORE fixation, at the
head whose bytes it binds. So the tool itself will only admit a published head
that the pre-fixation marker names — which is the window-close head, never a
later fixation commit.

(This clone proof's §4.10 placement of fixation is a separate, CLONE-PROOF-ONLY
artifact of needing to run arm, verify and the probes at the contract head. It
is not evidence about either the real ordering or the published head; see
§4.10's own note. Authority for this paragraph: D-153 A1 and A3; Opus F11;
synthesis item 19.)

A clean checkout at the published window-close head must then prove strict
four-way equality (publication head == HEAD == local `main` == `origin/main`),
run the complete suite against that real published ref, and record
`PUBLISHED GREEN` with its OID in separate immutable custody. Candidate marker
verification from §3.8 is NOT reusable: publication verification runs in the
COMMITTED-BLOB lane — no `--candidate-manifest` — with the Ed-confirmed table
and its out-of-band digest both supplied, semantic replay, and a transcript
carrying `lane: "published"` and `gate_admissible: true`. No S-0 clone command
may forge that claim.

**r4 specified all of that as prose and none of it as a command**, which is the
defect Sol finding 59 records: the publication replay IS an enforcing entry
point under the step-6 contract, so it needs the confirmation pair exactly like
every other enforcing consumer, and "must use the Ed-confirmed table" supplies
nothing to any process. The block below is that command. **It does not run
inside the clone estate**: it runs later, in the real published checkout, and
writes into a custody directory of its own. It sources `env.sh` only for `$PY`,
`$CUSTODY`, `die` and the promoted table, and it takes the same operator-pasted
`hC` as every other enforcing block.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# Two operator inputs, substituted HERE and nowhere else.  The guards below
# refuse an unsubstituted block rather than letting it run against a literal.
PUBLISHED_HEAD=REPLACE_WITH_PUBLISHED_WINDOW_CLOSE_HEAD_SHA
PUBLISHED_CHECKOUT=REPLACE_WITH_ABSOLUTE_PATH_OF_CLEAN_PUBLISHED_CHECKOUT
test "$PUBLISHED_HEAD" != REPLACE_WITH_PUBLISHED_WINDOW_CLOSE_HEAD_SHA \
  || die 'substitute the published WINDOW-CLOSE head (not the fixation commit) first'
test "$PUBLISHED_CHECKOUT" != REPLACE_WITH_ABSOLUTE_PATH_OF_CLEAN_PUBLISHED_CHECKOUT \
  || die 'substitute the published checkout path first'

# CONFIRMATION PAIR, re-pasted per block (ruling R-2; §3.9 states in full why
# 085 is a cross-check and never the source).
STEP6_TABLE="$CUSTODY/windows/family_publication/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_TABLE" || die 'the promoted step-6 confirmation table is absent'
test -n "${ED_STEP6_CONFIRMED_SHA256:-}" \
  || die "Ed's step-6 confirmation digest (hC) is not pasted into this block"
"$PY" -c 'import re,sys; raise SystemExit(0 if re.fullmatch("[0-9a-f]{64}", sys.argv[1]) else 1)' \
  "$ED_STEP6_CONFIRMED_SHA256" \
  || die 'ED_STEP6_CONFIRMED_SHA256 is not a lowercase 64-hex digest'
test "$ED_STEP6_CONFIRMED_SHA256" = "$(cat "$TRANS/085-ed-step6-confirmed-sha256.txt")" \
  || die 'the pasted hC differs from the 085 witness of the §3.8 confirmation'

PUBGREEN="$CUSTODY/published-green"
test ! -e "$PUBGREEN" || die 'published-green custody already exists; this step runs once'
mkdir -p "$PUBGREEN"

# Strict four-way ref equality at the PUBLISHED head.
test "$(git -C "$PUBLISHED_CHECKOUT" rev-parse HEAD)" = "$PUBLISHED_HEAD" \
  || die 'the published checkout HEAD is not the published head'
test "$(git -C "$PUBLISHED_CHECKOUT" rev-parse refs/heads/main)" = "$PUBLISHED_HEAD" \
  || die 'local main is not the published head'
test "$(git -C "$PUBLISHED_CHECKOUT" rev-parse refs/remotes/origin/main)" = "$PUBLISHED_HEAD" \
  || die 'origin/main is not the published head'
test -z "$(git -C "$PUBLISHED_CHECKOUT" status --porcelain=v1)" \
  || die 'the published checkout is dirty; a live marker consult requires a clean tree'
printf 'four_way=publication_head==HEAD==main==origin/main\noid=%s\n' \
  "$PUBLISHED_HEAD" > "$PUBGREEN/150-four-way-equality.txt"

# Publication-lane marker replay.  No --candidate-manifest: the committed-blob
# tool lane is selected by --phase alone, and the pair is passed explicitly.
"$PY" "$PUBLISHED_CHECKOUT/scripts/verify_family_marker.py" \
  --repository "$PUBLISHED_CHECKOUT" \
  --marker "$CUSTODY/windows/family_publication/d117_family_publication_v4.json" \
  --phase publication \
  --confirmation "$STEP6_TABLE" \
  --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256" \
  > "$PUBGREEN/151-marker-publication-replay.json" \
  || die 'publication-lane marker replay refused; see 151'
"$PY" - "$PUBGREEN/151-marker-publication-replay.json" "$PUBLISHED_HEAD" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d["status"] == "PASS", d
assert d["phase"] == "publication" and d["lane"] == "published", d
assert d["gate_admissible"] is True and d["publication_authorized"] is True, d
assert d["consulted_git"]["origin_main_commit"] == sys.argv[2], d["consulted_git"]
assert d["confirmation"] is not None, d
ids = {c["check_id"] for c in d["checks"]}
assert {"confirmation_missing", "confirmation_mismatch"} <= ids, sorted(ids)
print(json.dumps({"status": "PASS", "lane": "published",
                  "gate_admissible": True,
                  "confirmation_checks_executed": True},
                 indent=2, sort_keys=True))
PY

cd "$PUBLISHED_CHECKOUT"
set +e
"$PY" -m unittest discover -s tests > "$PUBGREEN/152-published-green.txt" 2>&1
PUBLISHED_SUITE_RC=$?
set -e
test "$PUBLISHED_SUITE_RC" = 0 \
  || die "the published-ref suite failed with rc $PUBLISHED_SUITE_RC; see 152"
printf 'classification=PUBLISHED GREEN\nhead=%s\nlane=published\ngate_admissible=true\n' \
  "$PUBLISHED_HEAD" > "$PUBGREEN/153-published-green-classification.txt"
```

Pass iff the four-way equality holds at the published window-close head, the
marker replay returns `lane: "published"` with `gate_admissible: true` **and
with the two confirmation checks in its executed-checks list** (which is how the
transcript proves the pair was actually authenticated rather than skipped), and
the suite is rc 0 against the real ref. Authority: D-151 condition 4;
MARKER-RULING ratified items 2–3 and split S-1; D-153 A1 and A3; the step-6
contract's enforcing-entry-point clause; Sol finding 59; Opus F11.

---

# 4. PROBE BATTERY

Each probe uses a fresh `new_case` clone at `$PROBE_BASE` (recorded in §3.9);
never reuse a case after a mutation. For R1 codes, extract the exact
candidate-owned spellings first.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

CHANGED_CODE=$("$PY" -c 'import json,sys; r=json.load(open(sys.argv[1]))["freeze_evidence_lifecycle"]; print(next(x["code"] for x in r["refusal_vocabulary"] if x["role"]=="DEPENDENCY_CHANGED_SET"))' "$REGISTRY")
MANIFEST_CODE=$("$PY" -c 'import json,sys; r=json.load(open(sys.argv[1]))["freeze_evidence_lifecycle"]; print(next(x["code"] for x in r["refusal_vocabulary"] if x["role"]=="DEPENDENCY_MANIFEST"))' "$REGISTRY")
test -n "$CHANGED_CODE" || die 'DEPENDENCY_CHANGED_SET code is empty'
test -n "$MANIFEST_CODE" || die 'DEPENDENCY_MANIFEST code is empty'
record_env CHANGED_CODE "$CHANGED_CODE"
record_env MANIFEST_CODE "$MANIFEST_CODE"
printf 'DEPENDENCY_CHANGED_SET=%s\nDEPENDENCY_MANIFEST=%s\n' \
  "$CHANGED_CODE" "$MANIFEST_CODE" > "$TRANS/100-r1-code-map.txt"
```

Both codes are recorded in `env.sh`, so every probe block below gets them by
sourcing rather than by re-deriving.

### 4(a). Ordinary changed path refuses

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# CONFIRMATION PAIR, re-pasted per block (ruling R-2; §3.9 states in full why
# 085 is a cross-check and never the source).
STEP6_TABLE="$CUSTODY/windows/family_publication/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_TABLE" || die 'the promoted step-6 confirmation table is absent'
test -n "${ED_STEP6_CONFIRMED_SHA256:-}" \
  || die "Ed's step-6 confirmation digest (hC) is not pasted into this block"
"$PY" -c 'import re,sys; raise SystemExit(0 if re.fullmatch("[0-9a-f]{64}", sys.argv[1]) else 1)' \
  "$ED_STEP6_CONFIRMED_SHA256" \
  || die 'ED_STEP6_CONFIRMED_SHA256 is not a lowercase 64-hex digest'
test "$ED_STEP6_CONFIRMED_SHA256" = "$(cat "$TRANS/085-ed-step6-confirmed-sha256.txt")" \
  || die 'the pasted hC differs from the 085 witness of the §3.8 confirmation'

CASE=$(new_case ordinary-path "$PROBE_BASE")
printf 'S-0 ordinary-path probe\n' > "$CASE/s0-ordinary-probe.txt"
commit_case "$CASE" 'S-0 probe ordinary changed path'
capture 101-ordinary "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$FIRST_PACK" --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}" \
  --step6-confirmation-table "$STEP6_TABLE" \
  --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256"
rc=$(cat "$TRANS/101-ordinary.rc")
if [ "$rc" != 1 ] && [ "$rc" != 2 ]; then die "ordinary-path probe rc=$rc"; fi
grep -F "$CHANGED_CODE" "$TRANS/101-ordinary.stdout.json" > /dev/null \
  || die 'ordinary changed path did not produce the DEPENDENCY_CHANGED_SET code'
if grep -E 'digest-conditional allowlist path|no expected confirmation digest supplied' \
    "$TRANS/101-ordinary.stdout.json" "$TRANS/101-ordinary.stderr.txt" > /dev/null; then
  die 'the ordinary-path probe refused on the CONFIRMATION path, not on its own mutation: the pair did not reach the intended gate'
fi
no_traceback 101-ordinary || die 'ordinary-path probe traceback'
```

Pass iff the exact registry code for `DEPENDENCY_CHANGED_SET` appears and no
pack bytes change. This probe reaches the R1 gate through the **replay** path:
at `$PROBE_BASE` the pack already carries a plan-pinned `freeze-0004`, so
`generate_freeze_receipt` enters `_load_freeze_reference` (`:6475-6691`), where
the changed-set gate runs. Authority: R4 r4-2; R5 V-1;
`arm_readiness.py:4229-4277,4300-4322`.

### 4(b). Unexpected output-directory file refuses

R2 ran this at the `arm` verb against the pack's own evidence directory. That
cannot work: `arm` calls `_discover_evidence` with `include_pack=False`
(`arm_readiness.py:7602`), so the pack namespace is dropped from the scan
(`_evidence_directories`, `:5400-5406`) and what actually refuses is the
pack-digest / changed-set code, not `readiness_evidence_unreadable`. The single
directory-inventory check at `:5659-5686` governs **both** namespaces, so it
takes two probes to exercise it in both.

**4(b.1) — window-custody namespace, at `arm`, pack untouched.** The custody
pack root is `<window custody root>/<pack name>` (`:7583`), and that namespace
IS scanned at arm.

*Expected rc, derived* (the r3 ratification flagged this as unverified): the
inventory check **appends** to the governed refusal list rather than raising —
`refusals.append(_receipt_refusal("readiness_evidence_unreadable"))` at
`:5669` and `:5678` — so `generate_arm_receipt` returns a result mapping with
`status: "REFUSE"`, not an `ArmReadinessError`. The CLI maps that to
`return 0 if result.get("status") not in {"REFUSE"} else 1`
(`scripts/generate_arm_readiness.py:192`), i.e. **rc 1**. rc 2 would mean a
raised `ArmReadinessError` — a different, non-governed path — and is a failure
of this probe, not a pass. Under D-153 this arm carries no R1 code at all, so
`readiness_evidence_unreadable` is the refusal under test in isolation. Nothing in the repository is modified, so this probe proves
exactly what r2's prose claimed: a governed arm REFUSE naming
`readiness_evidence_unreadable`, an external refusal receipt, and an unchanged
pack snapshot.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# CONFIRMATION PAIR, re-pasted per block (ruling R-2; §3.9 states in full why
# 085 is a cross-check and never the source).
STEP6_TABLE="$CUSTODY/windows/family_publication/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_TABLE" || die 'the promoted step-6 confirmation table is absent'
test -n "${ED_STEP6_CONFIRMED_SHA256:-}" \
  || die "Ed's step-6 confirmation digest (hC) is not pasted into this block"
"$PY" -c 'import re,sys; raise SystemExit(0 if re.fullmatch("[0-9a-f]{64}", sys.argv[1]) else 1)' \
  "$ED_STEP6_CONFIRMED_SHA256" \
  || die 'ED_STEP6_CONFIRMED_SHA256 is not a lowercase 64-hex digest'
test "$ED_STEP6_CONFIRMED_SHA256" = "$(cat "$TRANS/085-ed-step6-confirmed-sha256.txt")" \
  || die 'the pasted hC differs from the 085 witness of the §3.8 confirmation'

PROBE_CUSTODY="$CUSTODY/probes/102-unexpected"
mkdir -p "$PROBE_CUSTODY/$(basename "$FIRST_PACK")/arm_readiness.evidence"
mkdir -p "$PROBE_CUSTODY/family_publication"
cp -p "$CUSTODY/windows/family_publication/"* "$PROBE_CUSTODY/family_publication/"
printf 'unexpected\n' \
  > "$PROBE_CUSTODY/$(basename "$FIRST_PACK")/arm_readiness.evidence/unexpected.txt"
BEFORE=$(git -C "$CLONE" rev-parse HEAD)
# The table path resolves from $PROBE_CUSTODY/family_publication, copied above;
# hC is the half the CLI cannot derive, so it is passed explicitly.
capture 102-unexpected "$PY" "$CLONE/scripts/generate_arm_readiness.py" arm \
  --pack-root "$CLONE/$FIRST_PACK" --arm-context "$ARM_CONTEXT" \
  --window-custody-root "$PROBE_CUSTODY" \
  --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256"
expect_rc 102-unexpected 1 || die 'custody-namespace probe did not return a governed REFUSE'
grep -F 'readiness_evidence_unreadable' "$TRANS/102-unexpected.stdout.json" > /dev/null \
  || die 'custody-namespace probe did not name readiness_evidence_unreadable'
# The isolation claim in the prose above is only true if NO R1 code and no
# confirmation refusal appears alongside it.
if grep -E 'digest-conditional allowlist path|no expected confirmation digest supplied' \
    "$TRANS/102-unexpected.stdout.json" "$TRANS/102-unexpected.stderr.txt" > /dev/null; then
  die 'the custody-namespace probe refused on the CONFIRMATION path, not on its own mutation: the pair did not reach the intended gate'
fi
if grep -F "$CHANGED_CODE" "$TRANS/102-unexpected.stdout.json" > /dev/null; then
  die 'the custody-namespace probe carries an R1 changed-set code; readiness_evidence_unreadable is not isolated'
fi
if grep -F "$MANIFEST_CODE" "$TRANS/102-unexpected.stdout.json" > /dev/null; then
  die 'the custody-namespace probe carries an R1 manifest code; readiness_evidence_unreadable is not isolated'
fi
no_traceback 102-unexpected || die 'custody-namespace probe traceback'
test "$(git -C "$CLONE" rev-parse HEAD)" = "$BEFORE" || die 'the probe moved the clone HEAD'
test -z "$(git -C "$CLONE" status --porcelain=v1)" || die 'the probe dirtied the clone'
```

**4(b.2) — pack namespace, at the freeze mint path.** `include_pack` defaults to
true and `generate_freeze_receipt` uses the default (`:6943`), so the pack
namespace is scanned there. The case is cut at `$EVIDENCE_COMMIT`, before
`freeze-0004` exists, so the mint path runs rather than the replay path — the
mint path performs no changed-set comparison (it passes `head_commit=None`), so
the unexpected-output signal is not masked. The refusal is written and
plan-pinned exactly as §4(i) proves for the poison case; the pack's **source and
evidence** bytes are unchanged, but `freeze-0004.json` and the plan pin are
written. That is the ruled mint semantics, not a probe defect.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

CASE=$(new_case unexpected-pack-output "$EVIDENCE_COMMIT")
printf 'unexpected\n' > "$CASE/$FIRST_PACK/arm_readiness.evidence/unexpected.txt"
commit_case "$CASE" 'S-0 probe unexpected pack evidence output'
capture 103-unexpected-pack "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$FIRST_PACK" --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}"
expect_rc 103-unexpected-pack 1 || die 'pack-namespace probe did not return a governed REFUSE'
no_traceback 103-unexpected-pack || die 'pack-namespace probe traceback'
"$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="REFUSE" and d["mutated"] is True and "readiness_evidence_unreadable" in d["reason_codes"], d' \
  "$TRANS/103-unexpected-pack.stdout.json" \
  || die 'pack-namespace probe did not name readiness_evidence_unreadable on a written refusal'
git -C "$CASE" diff --exit-code -- "$FIRST_PACK/arm_readiness.sources" \
  || die 'the probe changed pack source bytes'
git -C "$CASE" diff --exit-code -- "$FIRST_PACK/arm_readiness.evidence" \
  || die 'the probe changed pack evidence bytes'
```

Pass iff both namespaces refuse through the directory-inventory check.
Authority: R4 r4-2; R5 V-2; `arm_readiness.py:5400-5406,5514-5541,6725,7384` (second `include_pack=False` site: `:7833`);
the CLI enforces read-only pack snapshots for non-freeze verbs at
`scripts/generate_arm_readiness.py:100-110,113-174`; AUDIT F-6.

### 4(c). Manifest-only plan mutation — the current pack, and the sibling pack replaying itself

**What "manifest-only" means, and why r5's mutation could not reach the gate.**
The R1 `DEPENDENCY_MANIFEST` gate compares the bytes a pack's dependencies have
NOW against the derivation binding that pack's own receipts recorded. To reach
it, a mutation has to change bytes the manifest binds while leaving untouched
every term an EARLIER authenticator reads. r5 mutated
`window_identity.window_id`. That field is one of the six terms
`_pack_identity()` binds (`arm_readiness.py:4959`), and existing-receipt freeze
replay compares pack identity at `:6513-6521` — before it authenticates generic
evidence at `:6577-6598` and long before R1 lifecycle validation at
`:5608-5619`. Estate 9 executed the block and got exactly that ordering: `rc=2`,
`readiness_freeze_receipt_mismatch`, detail "freeze receipt pack identity
differs from committed pack bytes". The refusal was real, it just was not the
one the probe exists to obtain, and a substring grep for the manifest code could
not tell the difference between "the gate refused" and "the gate was never
reached."

`window_identity.evidence_root_id` is the field that does reach it, and the two
properties that make it the right vehicle are worth naming separately.
MANIFEST-VISIBLE: it lives in `plan_tree.json`, so changing it changes the
normalized plan-tree bytes the R1 manifest binds, and R1 sees a current
dependency that no longer matches its recorded derivation.
IDENTITY-INVISIBLE: it is NOT one of `_pack_identity()`'s six terms, so the
identity comparison at `:6513-6521` still passes — as do the calibration-plan
digest, the U11 binding, the freeze receipt and the evidence receipt, none of
which bind it. Nothing upstream of R1 has anything to complain about, so
execution runs on to R1 and refuses there, by name.

Each block below carries its own mutation driver as an inline heredoc rather
than sharing a materialized `custody/tools/mutate_plan.py`. r5 used a shared
file because a shell function does not survive from one block to the next; r6
does not, because the three plan mutations are no longer the same mutation (the
current pack, the sibling pack, and §4(g)'s S-6 case each write their own
target) and a heredoc driver is already block-local. `tamper_class.py` in §4(e)
is still a materialized file, because its eight classes share one driver.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# CONFIRMATION PAIR, re-pasted per block.
STEP6_TABLE="$CUSTODY/windows/family_publication/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_TABLE" || die 'the promoted step-6 confirmation table is absent'
test -n "${ED_STEP6_CONFIRMED_SHA256:-}" \
  || die "Ed's step-6 confirmation digest (hC) is not pasted into this block"
"$PY" -c 'import re,sys; raise SystemExit(0 if re.fullmatch("[0-9a-f]{64}",sys.argv[1]) else 1)' \
  "$ED_STEP6_CONFIRMED_SHA256" \
  || die 'ED_STEP6_CONFIRMED_SHA256 is not a lowercase 64-hex digest'
test "$ED_STEP6_CONFIRMED_SHA256" = "$(cat "$TRANS/085-ed-step6-confirmed-sha256.txt")" \
  || die 'the pasted hC differs from the 085 witness of the §3.8 confirmation'

CASE=$(new_case plan-current "$PROBE_BASE")
"$PY" - "$CASE/$FIRST_PACK/plan_tree.json" <<'PY' \
  || die 'current-plan mutation driver failed'
import hashlib, json, pathlib, sys
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text())
d["window_identity"]["evidence_root_id"] += "-s0-mutation"
raw = (json.dumps(d, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
p.write_bytes(raw)
p.with_name("plan_tree.sha256").write_text(
    hashlib.sha256(raw).hexdigest() + "  plan_tree.json\n"
)
PY
commit_case "$CASE" 'S-0 probe current plan manifest-only mutation'

capture 104-plan-current "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$FIRST_PACK" \
  --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}" \
  --step6-confirmation-table "$STEP6_TABLE" \
  --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256"
expect_rc 104-plan-current 1 \
  || die 'current-plan manifest probe did not return rc 1'
"$PY" - "$TRANS/104-plan-current.stdout.json" "$MANIFEST_CODE" "$FIRST_PACK" <<'PY' \
  || die 'current-plan mutation did not reach the exact DEPENDENCY_MANIFEST gate'
import json, sys
d = json.load(open(sys.argv[1]))
detail = f"current dependency differs from its derivation binding: {sys.argv[3]}/plan_tree.json"
if d.get("reason_codes") != [sys.argv[2]] or d.get("detail") != detail:
    raise SystemExit(repr(d))
PY
no_traceback 104-plan-current || die 'current-plan probe traceback'
```

**The sibling direction changes VEHICLE, because its original claim is
unreachable by design.** r5's `105` mutated the SECOND pack's plan tree and then
replayed the FIRST pack, asserting that the first pack's freeze refuses with
`DEPENDENCY_MANIFEST`. Estate 9 returned `rc=0`, `status=PASS`,
`mutated=false` — no gate fired at all — and none can:
`_r1_manifest_dependencies()` (`arm_readiness.py:4280-4309`) derives a pack's
dependencies ONLY from the evidence sources that pack's own receipts name, so
the first pack's manifest never mentions the second pack's plan tree and cannot
notice it moving. (The changed-set computation at `:4423-4458` separately
subtracts all three allowlisted plan paths, so nothing else notices either, and
the replay returns PASS at `:6902-6911`.) The claim "the first pack's replay
rejects a sibling-plan mutation via `DEPENDENCY_MANIFEST`" is therefore FALSE
ABOUT THE MECHANISM, not merely unproven, and is retired rather than repaired.

What the sibling direction can prove — and what `105` now proves — is that the
manifest binding is a PER-PACK property that holds in a pack other than
`$FIRST_PACK`: the second pack's own replay refuses its own manifest-only
mutation, with the same code and the same detail shape, naming its own plan
path. The goal r5's `105` was reaching for, that family-wide allowlist
membership is exact so no pack's plan can be forgiven by another pack's
allowlist entry, is enforced elsewhere and evidenced elsewhere: the
candidate-shape triplet `106-missing`, `107-extra` and `108-unused` in §4(d).

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# CONFIRMATION PAIR, re-pasted per block.
STEP6_TABLE="$CUSTODY/windows/family_publication/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_TABLE" || die 'the promoted step-6 confirmation table is absent'
test -n "${ED_STEP6_CONFIRMED_SHA256:-}" \
  || die "Ed's step-6 confirmation digest (hC) is not pasted into this block"
"$PY" -c 'import re,sys; raise SystemExit(0 if re.fullmatch("[0-9a-f]{64}",sys.argv[1]) else 1)' \
  "$ED_STEP6_CONFIRMED_SHA256" \
  || die 'ED_STEP6_CONFIRMED_SHA256 is not a lowercase 64-hex digest'
test "$ED_STEP6_CONFIRMED_SHA256" = "$(cat "$TRANS/085-ed-step6-confirmed-sha256.txt")" \
  || die 'the pasted hC differs from the 085 witness of the §3.8 confirmation'

CASE=$(new_case plan-sibling "$PROBE_BASE")
"$PY" - "$CASE/$SECOND_PACK/plan_tree.json" <<'PY' \
  || die 'second-pack plan mutation driver failed'
import hashlib, json, pathlib, sys
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text())
d["window_identity"]["evidence_root_id"] += "-s0-mutation"
raw = (json.dumps(d, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
p.write_bytes(raw)
p.with_name("plan_tree.sha256").write_text(
    hashlib.sha256(raw).hexdigest() + "  plan_tree.json\n"
)
PY
commit_case "$CASE" 'S-0 probe second-pack plan manifest mutation'

capture 105-plan-sibling "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$SECOND_PACK" \
  --predecessor-pack-root "$CASE/${PRED_OF[$SECOND_PACK]}" \
  --step6-confirmation-table "$STEP6_TABLE" \
  --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256"
expect_rc 105-plan-sibling 1 \
  || die 'second-pack manifest probe did not return rc 1'
"$PY" - "$TRANS/105-plan-sibling.stdout.json" "$MANIFEST_CODE" "$SECOND_PACK" <<'PY' \
  || die 'second-pack mutation did not reach the exact DEPENDENCY_MANIFEST gate'
import json, sys
d = json.load(open(sys.argv[1]))
detail = f"current dependency differs from its derivation binding: {sys.argv[3]}/plan_tree.json"
if d.get("reason_codes") != [sys.argv[2]] or d.get("detail") != detail:
    raise SystemExit(repr(d))
PY
no_traceback 105-plan-sibling || die 'second-pack manifest probe traceback'
```

Pass iff both directions return `rc=1` with `reason_codes` exactly
`[$MANIFEST_CODE]` and the exact detail `current dependency differs from its
derivation binding: <that pack>/plan_tree.json`, despite `plan_tree.json` and its
sidecar both being allowlisted paths. Asserting the exact code LIST and the
exact DETAIL — rather than grepping for the code as a substring — is what makes
the r5 masking visible at all: a masked run carries a different code entirely,
and a confirmation-path refusal carries the SAME code with a different detail.
This is L5-F2's outstanding mutation falsifier. Both expected details are
CODE-DERIVED predictions (r6); estate 10 confirms them by execution, and a
mismatch is adjudicated under §6, never patched at the bench. Authority:
`docs/process_traces/2026-08-25-probe-reachability/` (`01-sol-consult.md`
finding rows `104-plan-current` and `105-plan-sibling`,
`02-MAGISTRATE-ADJUDICATION.md`); R4 r4-2; SIT-C3 and seat-L5 F2; R5 S-6, V-1.vi;
`arm_readiness.py:4485-4542`.

### 4(d). Missing, extra, and unused candidate entries all fail

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

"$PY" - "$TRANS" "$REGISTRY" <<'PY'
import json,pathlib,sys
t=pathlib.Path(sys.argv[1]); json.load(open(t/"020-allowlist-shape.json"))
# Recreate from the registry rather than trusting transcript order.
reg=json.load(open(sys.argv[2]))["freeze_evidence_lifecycle"]["irrelevant_path_allowlist"]
assert len(reg)==112, len(reg)
(t/"020-candidate-exact.json").write_text(json.dumps(reg))
(t/"106-missing-list.json").write_text(json.dumps(reg[1:]))
(t/"107-extra-list.json").write_text(json.dumps(sorted(reg+["docs/s0-extra"])))
(t/"108-unused-observed.json").write_text(json.dumps(reg[:-1]))
PY

set +e
"$PY" "$CUSTODY/tools/s0_allowlist_contract.py" --registry "$REGISTRY" --shape-only \
  --candidate-list "$TRANS/106-missing-list.json" > "$TRANS/106-missing.json"
MISSING_RC=$?
"$PY" "$CUSTODY/tools/s0_allowlist_contract.py" --registry "$REGISTRY" --shape-only \
  --candidate-list "$TRANS/107-extra-list.json" > "$TRANS/107-extra.json"
EXTRA_RC=$?
"$PY" "$CUSTODY/tools/s0_allowlist_contract.py" --registry "$REGISTRY" \
  --candidate-list "$TRANS/020-candidate-exact.json" \
  --observed-list "$TRANS/108-unused-observed.json" > "$TRANS/108-unused.json"
UNUSED_RC=$?
set -e
test "$MISSING_RC" = 2 || die "missing-entry variant returned rc $MISSING_RC, expected 2"
test "$EXTRA_RC" = 2 || die "extra-entry variant returned rc $EXTRA_RC, expected 2"
test "$UNUSED_RC" = 2 || die "unused-entry variant returned rc $UNUSED_RC, expected 2"
"$PY" - "$TRANS" <<'PY'
import json,pathlib,sys
t=pathlib.Path(sys.argv[1])
assert json.load(open(t/"106-missing.json"))["candidate_missing"]
assert json.load(open(t/"107-extra.json"))["candidate_extra"]
assert json.load(open(t/"108-unused.json"))["unused_allowlist"]
print("PASS: each variant names its own defect field")
PY
```

Pass iff the three reports respectively name `candidate_missing`,
`candidate_extra` and `unused_allowlist`, all with exit 2. The registry is the
RULED live coordinate; the candidate authors the previously absent
`freeze_evidence_lifecycle.irrelevant_path_allowlist` key there. Authority:
REGISTRY-V2 RULING; D-151 condition 8 and Consequences; R4 r4-2; R5 V-1.v.

### 4(e). Per-class tamper probes over every allowlisted path class

Install the exact tamper driver, then run one fresh case per class and replay
`freeze-0004` for the affected pack. Each mutation remains schema-shaped where
that is necessary to reach the intended authenticator.

**What r6 changed here, and why it is one block instead of two.** r5 ran the
tamper loop in one block and its per-class verdicts in a second, and both used
substring greps: `grep -F <code>` for the expected code, plus two sweeps for
strings that must be absent (`no expected confirmation digest supplied` on every
class, `digest-conditional allowlist path` on the seven ordinary ones). A
substring grep cannot distinguish "this class refused through the authenticator
under test" from "this class refused earlier, for something else, and the code
happens to appear in the payload." Estate 9 proved that the hard way: the loop
stopped at `freeze-json`, which returned `readiness_receipt_namespace_anomalous`
rather than the expected freeze-receipt mismatch, and the run never reached the
second block at all — leaving two further class expectations (`freeze-sidecar`
and `plan-json`) untested and, as it turns out, also wrong.

r6 asserts each class by EQUALITY on both fields at once: `reason_codes` must
equal the expected one-element list and `detail` must equal the expected string.
That is strictly stronger than everything r5 checked — an exact detail match
entails the absence of both forbidden strings — so the two absence sweeps are
subsumed and the second block is gone rather than merely moved. The whole class
battery therefore lives in ONE block, and the executable-block count in §0.1
drops by one accordingly.

Three class expectations were re-derived from the raise sites at `5a034f84`:

- **`freeze-json`** changed its shape, not just its expectation, and then
  changed its expectation again in the r6 fix round. Bumping `issued_at_utc`
  invalidates the freeze receipt's own GNU sidecar, and
  `generate_freeze_receipt()` scans the receipt namespace at `:6848` — which
  authenticates every sidecar at `:4713-4725` — BEFORE anything downstream can
  look at the plan's recorded freeze pin. So the tamper recomputes the freeze
  JSON's sidecar and leaves the PLAN's recorded freeze SHA fixed, and namespace
  authentication passes. **What refuses next is the PLAN-PIN FILTER, not the
  exactness check.** Immediately after the namespace scan, `:6848-6862` compares
  each scanned receipt's `{path, sha256}` pair against the plan's recorded pin
  and discards any receipt that does not match, refusing before
  `_load_freeze_reference()` is ever called. The recomputed sidecar changed the
  receipt's own SHA, so the tampered receipt is exactly the receipt that filter
  rejects. The expected pair is therefore
  `[readiness_freeze_receipt_mismatch]` with detail **"existing freeze receipt
  is not plan-pinned"**, at `rc=2` — not the exactness detail "plan freeze
  reference is not exact" that the consult predicted from `:6503-6506`, which is
  reached only by a receipt that survives plan-pinning. Both fix-round seats
  re-derived this independently and concurred; the correction is ruled in
  `docs/process_traces/2026-08-25-probe-reachability/03-FREEZE-JSON-AMENDMENT.md`.
- **`freeze-sidecar`** is the class whose expectation r5 got wrong for the same
  reason and in the opposite direction: zeroing that sidecar is precisely a
  namespace-authentication failure, so its refusal is
  `readiness_receipt_namespace_anomalous`, never a freeze-receipt mismatch.
- **`plan-json`** carried r5's `window_id` mutation and would have reproduced
  `104`'s identity masking exactly. It now makes the manifest-only
  `evidence_root_id` change of §4(c), with the corrected plan sidecar.

The two classes whose refusal is an R1 refusal — `plan-json` and `pinset-json` —
exit `1`; the other six exit `2`. The loop asserts the exit code per class
rather than merely asserting nonzero, because "refused with the wrong exit code"
is a mechanism finding and r5's `!= 0` test could not see it.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# CONFIRMATION PAIR, re-pasted per block.
STEP6_TABLE="$CUSTODY/windows/family_publication/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_TABLE" || die 'the promoted step-6 confirmation table is absent'
test -n "${ED_STEP6_CONFIRMED_SHA256:-}" \
  || die "Ed's step-6 confirmation digest (hC) is not pasted into this block"
"$PY" -c 'import re,sys; raise SystemExit(0 if re.fullmatch("[0-9a-f]{64}",sys.argv[1]) else 1)' \
  "$ED_STEP6_CONFIRMED_SHA256" \
  || die 'ED_STEP6_CONFIRMED_SHA256 is not a lowercase 64-hex digest'
test "$ED_STEP6_CONFIRMED_SHA256" = "$(cat "$TRANS/085-ed-step6-confirmed-sha256.txt")" \
  || die 'the pasted hC differs from the 085 witness of the §3.8 confirmation'

cat > "$CUSTODY/tools/tamper_class.py" <<'PY'
import argparse, hashlib, json, pathlib
ap = argparse.ArgumentParser()
ap.add_argument("kind")
ap.add_argument("repo", type=pathlib.Path)
ap.add_argument("pack")
a = ap.parse_args()
root = a.repo / a.pack

def render(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
    path.write_bytes(raw)
    return raw

def sidecar(path, raw):
    path.with_name(path.name + ".sha256").write_text(
        hashlib.sha256(raw).hexdigest() + "  " + path.name + "\n"
    )

def zero_sidecar(path, target):
    path.write_text("0" * 64 + "  " + target + "\n")

if a.kind == "source-json":
    p = root / "arm_readiness.sources/acceptance-owner.json"
    d = json.loads(p.read_text())
    d["primary_artifacts"][0]["sha256"] = "0" * 64
    render(p, d)
elif a.kind == "evidence-json":
    p = root / "arm_readiness.evidence/evidence-acceptance-owner.json"
    p.write_bytes(p.read_bytes() + b" ")
elif a.kind == "evidence-sidecar":
    p = root / "arm_readiness.evidence/evidence-acceptance-owner.json.sha256"
    zero_sidecar(p, "evidence-acceptance-owner.json")
elif a.kind == "freeze-json":
    p = root / "arm_readiness.freeze.receipts/freeze-0004.json"
    d = json.loads(p.read_text())
    d["issued_at_utc"] = d["issued_at_utc"].replace("2026-", "2027-", 1)
    raw = render(p, d)
    sidecar(p, raw)
elif a.kind == "freeze-sidecar":
    p = root / "arm_readiness.freeze.receipts/freeze-0004.json.sha256"
    zero_sidecar(p, "freeze-0004.json")
elif a.kind == "plan-json":
    p = root / "plan_tree.json"
    d = json.loads(p.read_text())
    d["window_identity"]["evidence_root_id"] += "-s0-tamper"
    raw = render(p, d)
    p.with_name("plan_tree.sha256").write_text(
        hashlib.sha256(raw).hexdigest() + "  plan_tree.json\n"
    )
elif a.kind == "plan-sidecar":
    zero_sidecar(root / "plan_tree.sha256", "plan_tree.json")
elif a.kind == "pinset-json":
    p = a.repo / "configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json"
    d = json.loads(p.read_text())
    d["packs"][0]["plan_sha256"] = "0" * 64
    render(p, d)
else:
    raise SystemExit("unknown class")
PY
chmod 0555 "$CUSTODY/tools/tamper_class.py"

tampered=0
for kind in source-json evidence-json evidence-sidecar freeze-json freeze-sidecar plan-json plan-sidecar pinset-json; do
  CASE=$(new_case "tamper-$kind" "$PROBE_BASE")
  "$PY" "$CUSTODY/tools/tamper_class.py" "$kind" "$CASE" "$FIRST_PACK" \
    || die "tamper driver failed for $kind"
  commit_case "$CASE" "S-0 per-class tamper $kind"
  capture "110-tamper-$kind" "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
    --pack-root "$CASE/$FIRST_PACK" \
    --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}" \
    --step6-confirmation-table "$STEP6_TABLE" \
    --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256"
  case "$kind" in
    plan-json|pinset-json)
      expect_rc "110-tamper-$kind" 1 \
        || die "tamper class $kind did not return rc 1"
      ;;
    *)
      expect_rc "110-tamper-$kind" 2 \
        || die "tamper class $kind did not return rc 2"
      ;;
  esac
  no_traceback "110-tamper-$kind" || die "tamper class $kind failed ugly"
  tampered=$((tampered + 1))
done
test "$tampered" = 8 || die "ran $tampered tamper classes, expected 8"

"$PY" - "$TRANS" "$FIRST_PACK" "$MANIFEST_CODE" "$CHANGED_CODE" "$SUCCESSOR_PINSET" <<'PY' \
  || die 'one or more tamper classes returned the wrong exact refusal'
import json, pathlib, sys
t = pathlib.Path(sys.argv[1])
pack, manifest, changed, pinset = sys.argv[2:]
expected = {
    "source-json": (
        ["readiness_evidence_digest_mismatch"],
        "evidence fact source digest mismatch",
    ),
    "evidence-json": (
        ["readiness_evidence_digest_mismatch"],
        "evidence item digest differs from authenticated bytes",
    ),
    "evidence-sidecar": (
        ["readiness_evidence_digest_mismatch"],
        "evidence item digest differs from authenticated bytes",
    ),
    "freeze-json": (
        ["readiness_freeze_receipt_mismatch"],
        "existing freeze receipt is not plan-pinned",
    ),
    "freeze-sidecar": (
        ["readiness_receipt_namespace_anomalous"],
        "sidecar mismatch for freeze-0004.json",
    ),
    "plan-json": (
        [manifest],
        f"current dependency differs from its derivation binding: {pack}/plan_tree.json",
    ),
    "plan-sidecar": (
        ["readiness_pack_digest_mismatch"],
        "plan-tree sidecar does not authenticate exact bytes",
    ),
    "pinset-json": (
        [changed],
        f"digest-conditional allowlist path {pinset!r}: "
        "bytes at the reviewed HEAD differ from Ed's confirmed step-6 digest",
    ),
}
for kind, pair in expected.items():
    observed = json.load(open(t / f"110-tamper-{kind}.stdout.json"))
    if (observed.get("reason_codes"), observed.get("detail")) != pair:
        raise SystemExit(f"{kind}: {observed!r}")
PY
```

The complete enumerated classes and counts are, with the exact
`reason_codes`/`detail` pair each one must return:

| Class (count) | Representative mutation | rc | Expected `reason_codes` | Expected `detail` |
|---|---|---|---|---|
| source JSON (33) | change one primary-artifact digest without changing its receipt | 2 | `[readiness_evidence_digest_mismatch]` | `evidence fact source digest mismatch` |
| evidence JSON (33) | change one receipt byte | 2 | `[readiness_evidence_digest_mismatch]` | `evidence item digest differs from authenticated bytes` |
| evidence sidecar (33) | replace its digest with 64 zeroes | 2 | `[readiness_evidence_digest_mismatch]` | `evidence item digest differs from authenticated bytes` |
| freeze JSON (3) | change its still-valid timestamp **and recompute its own sidecar**, leaving the plan's recorded freeze SHA fixed | 2 | `[readiness_freeze_receipt_mismatch]` | `existing freeze receipt is not plan-pinned` |
| freeze sidecar (3) | replace its digest with 64 zeroes | 2 | `[readiness_receipt_namespace_anomalous]` | `sidecar mismatch for freeze-0004.json` |
| plan-tree JSON (3) | manifest-only `window_identity.evidence_root_id` change plus corrected sidecar (the §4(c) mutation) | 1 | `[$MANIFEST_CODE]` | `current dependency differs from its derivation binding: $FIRST_PACK/plan_tree.json` |
| plan-tree sidecar (3) | replace its digest only | 2 | `[readiness_pack_digest_mismatch]` | `plan-tree sidecar does not authenticate exact bytes` |
| successor pinset JSON (1) | change one governed `_v4` row's `plan_sha256`, re-rendered canonically | 1 | `[$CHANGED_CODE]` | `digest-conditional allowlist path '$SUCCESSOR_PINSET': bytes at the reviewed HEAD differ from Ed's confirmed step-6 digest` |

Two rows carry a claim that is easy to lose, so it is stated rather than
implied. **The successor-pinset class can produce NO `histsem_*` code at all.**
`generate_freeze_receipt` calls `_gate_receipt_histsem` on the PREDECESSOR pack
first (`arm_readiness.py:6774`), but this tamper re-renders the successor pinset
as canonical, schema-valid JSON with the same pack identities, so the chain
loads clean and that gate returns without raising. Execution then reaches
`_require_confirmed_conditional_path` (`:4312-4367`), whose `refuse()` helper is
hardwired to the `DEPENDENCY_CHANGED_SET` role (D-151 condition 1e: no new
refusal codes), and the replay boundary returns that role's code with that
raise's detail (`:6883-6890`). r5 first asked for a `histsem_*` code here as
well; the two assertions are mutually unreachable, and the C→S one is correct.
The hS byte pin is a POST-FIXATION property and is probed separately, at
`$FIXATION_COMMIT`, in §4.10 step 4. **And the digest-conditional detail is the
discriminator, not decoration**: the digest-conditional raise runs BEFORE the
ordinary-path raise and shares its registry code, so `pinset-json` must show the
AUTHENTICATED bytes-differ detail above and never the missing-input refusal
`no expected confirmation digest supplied`, while the seven ordinary classes
must show their own details and therefore no digest-conditional detail at all.
The equality assertions in the block enforce both directions at once.

All eight `detail` strings above are CODE-DERIVED predictions read off the raise
sites at `5a034f84`, not observations from a run (r6). Estate 10 confirms them by
execution; a mismatch is a finding adjudicated under §6, not an assertion to
relax at the bench.

**Two coordinates, and r4 collapsed them into one.** r4 ran the byte-pin probe
here, inside the `tamper-pinset-json` case, from a case cut at `$PROBE_BASE`.
Three things were wrong with that, and all three are cured by moving the probe
(Sol 24–25; Opus F1–F2; ruling item 9):

1. **The method did not exist at this coordinate.** `SUCCESSOR_PINSET_SHA256`
   and `test_successor_pinset_hs_byte_pin` are added by the fixation delta,
   which §4.10 applies. A case cut at `$PROBE_BASE` contains neither.
2. **The grep named a method that exists nowhere.** r4 grepped
   `test_successor_pinset_is_byte_pinned_at_fixation` — a name that exists
   nowhere in the repository, and which appears in this runsheet only in this
   sentence, as the record of the defect, never again as a command. The delta
   defines `test_successor_pinset_hs_byte_pin`. Under §6 that is an instrument failure
   — "a command that names a file, flag or refusal code that does not exist" —
   not a typo to be fixed at the bench.
3. **Deleting the grep would have made it worse, not better.** The suite would
   still have gone red in that case, because the tamper reddens the whole-corpus
   verifier test. The probe would then have PASSED for a reason with nothing to
   do with a byte pin — the most expensive kind of green.

There is a fourth defect in the *case design*, and it is the one that matters
most: **this tamper is not byte-only.** It rewrites `plan_sha256` and
re-renders canonical JSON, so pack/receipt shape and canonicality both change,
and `tests/test_receipt_histsem.py`'s canonicality check already catches that
BEFORE fixation — i.e. the case cannot show the byte pin doing any work the
file was not already doing. The case that can is a SHAPE-PRESERVING canonical
re-mint: identical `pack_count`, `receipt_count` and `pack_ids`, canonical
bytes, one differing `plan_sha256`. That case is what §4.10 step 4 runs, and it
is the case in which the byte pin's own failure is attributable to the byte pin
rather than to canonicality or shape.

**It is NOT the only test that reddens on that case, and this runsheet does not
claim it is.** The same re-mint changes a governed row's `plan_sha256`, which
the full-corpus test independently catches as `histsem_binding_mismatch`. That
is fine and expected. What §4.10 step 4 proves is narrower and stronger than
"only this test fails": it proves that
`test_successor_pinset_hs_byte_pin` — the byte pin's own assertion — is itself
in the failure list, BY NAME. That claim is independent of how many other tests
also go red, which is exactly why the probe asserts the method name rather than
the suite's exit code.

So the two coordinates are now stated separately and evidenced separately:

- **`110-*` stays PRE-FIXATION**, at `$PROBE_BASE`. It evidences the seven
  ordinary tamper classes plus the successor's structural and authenticated
  C→S refusals. None of these needs the hS pin.
- **`118-*` moves POST-FIXATION**, to a case cut at `$FIXATION_COMMIT` in §4.10
  step 4, where the pin exists. It evidences one property: over a
  shape-preserving canonical re-mint, `test_successor_pinset_hs_byte_pin`
  itself fails, by name. Other tests fail on that case too
  (`histsem_binding_mismatch` in the full-corpus test); the by-name assertion
  is what makes the evidence about the byte pin regardless.

Pass iff **all eight** classes refuse through an independent digest, binding or
semantic-replay authenticator. For the successor class, the Ed-confirmed C→S
edge is load-bearing and "the test run itself" is never an authenticator. If any
class has no such authenticator, apply V-1.vi's digest-conditional subtraction
rule: it may not remain a static allowlist subtraction; remove that class from
the candidate allowlist, bind it in the authenticated derived manifest, and
reopen the mechanism proof. Authority: D-151 conditions 2–3; R5 V-1.iv, V-1.vi,
V-1.vii; RH-8; semantic replay `arm_readiness.py:6243-6369`.

### 4(e.1). Digest-conditional successor subtraction — actual C→S edge

The synthetic unit probe and the transaction probe are both mandatory. The
focused class must prove: the exact confirmed digest subtracts the successor; no
table, an absent or invalid table, a wrong path, a wrong digest, and any later
successor rewrite all refuse with the pre-existing `DEPENDENCY_CHANGED_SET`
role; and `R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS` is exactly the successor path.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"

set +e
"$PY" -m unittest -v tests.test_receipt_histsem.SuccessorPinsetDigestConditionTests \
  > "$TRANS/122-c-to-s-unit-probes.txt" 2>&1
CTOS_RC=$?
set -e
test "$CTOS_RC" = 0 || die "C-to-S unit probes failed with rc $CTOS_RC; see 122"

# Transaction PASS side: section 3.9's 091-* arms used Ed's exact table at
# $CUSTODY/windows/family_publication.  (D-153) Under the clean arm the PASS
# side is BOTH properties at once: no changed-set code appears in any arm
# transcript, AND Ed's exact table discharged the digest-conditional successor,
# i.e. the successor path is absent from the gate's residue (which is empty).
# Transcript 098 computes that residue with the gate's own arithmetic.
checked=0
for p in "$TRANS"/091-arm-*.stdout.json; do
  test -s "$p" || die "arm transcript $p is empty"
  if grep -F "$CHANGED_CODE" "$p" > /dev/null; then
    die "arm transcript $p carries the changed-set code; under D-153 the arm at PINSET_MINT_HEAD must be clean"
  fi
  checked=$((checked + 1))
done
test "$checked" = 3 || die "checked $checked arm transcripts, expected 3"
"$PY" - "$TRANS/098-clean-arm-residue.json" "$SUCCESSOR_PINSET" <<'PY'
import json, sys
residue = json.load(open(sys.argv[1]))["residue"]
successor = sys.argv[2]
assert successor not in residue, (
    "the successor pinset is in the changed-set residue: Ed's confirmed table "
    "did NOT discharge the digest-conditional path", residue)
assert residue == [], residue
print(json.dumps({"status": "PASS",
                  "c_to_s_edge": "successor discharged by Ed's confirmed digest",
                  "residue": residue}, indent=2, sort_keys=True))
PY
```

**Deliberate custody mixing — recorded, not accidental (F-10).** Every other
probe writes under `$CUSTODY/probes/<label>`. The block below is the one
exception: it arms with `--window-custody-root "$CUSTODY/windows"`, the
transaction's OWN custody root. That is necessary — the C→S edge is enforced
against Ed's confirmed table and the family-publication marker, which live only
there, and copying them into a probe root would change the very bytes under
test. The consequence is recorded here rather than discovered later:
`generate_arm_receipt` numbers receipts from the existing namespace
(`number = max(...) + 1`, `:7584-7588`) and records a `supersedes` binding
(`:7712-7723`), so **this probe mints `arm-0002`, which supersedes the
transaction's `arm-0001`.** Two rules follow, both already enforced above:

1. §3.9's census block globs `arm-0001.json` by exact ordinal, never `arm-*`,
   so it reads transaction evidence even when re-run after §4.
2. Any later step, or any reviewer, re-reading arm receipts under
   `$CUSTODY/windows` must pin the ordinal the same way. An `arm-*` glob after
   this point is a custody error, not a convenience.

**Why the later rewrite must be CANONICAL, and confined to a sibling row.**
r5 produced the "later rewrite" by appending a newline to the committed
successor pinset. That is a byte change, but it is also a CANONICALITY change,
and the `arm` verb's very first act is `_gate_receipt_histsem(root)`
(`arm_readiness.py:7535-7546`), whose canonical-parse check refuses
`histsem_pinset_invalid` at `:3792-3799` — before `_load_freeze_reference()` at
`:7564` and before any R1 validation whatsoever. Estate 9 executed it and got
exactly that: `rc=1`, `histsem_pinset_invalid`, detail "committed
receipt-histsem pinset is invalid". The C→S gate was never reached, and the
probe's real subject was untested.

r6 rewrites the pinset the way an actual later commit would: it changes ONE
field — a SIBLING row's `plan_sha256` — and re-renders the whole file
canonically. Three properties follow, and all three are needed. The file stays
schema-valid and canonical, so the histsem shape check passes. The row the arm
actually verifies is the TARGET pack's row, and `:3497-3519` examines only that
row, which this mutation leaves fixed — so target histsem verification passes
too. What HAS changed is the file's whole-file digest, and that is precisely the
value R1 compares against Ed's confirmed step-6 table at `:4364-4367`. The
refusal is therefore the authenticated C→S one, reached by the intended route.

**This probe is the arm-entry route, not the primary C→S vehicle.** The
synthetic unit battery `122-*` and the freeze-path `110-tamper-pinset-json`
class remain the primary vehicles for the digest-conditional edge; what the
amended `123` adds, and the only thing it is now claimed to add, is that the
same edge is enforced when the transaction is entered through `arm` rather than
through freeze replay — an entry point with a different gate order in front of
it, as estate 9 demonstrated.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# CONFIRMATION PAIR, re-pasted per block.
STEP6_TABLE="$CUSTODY/windows/family_publication/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_TABLE" || die 'the promoted step-6 confirmation table is absent'
test -n "${ED_STEP6_CONFIRMED_SHA256:-}" \
  || die "Ed's step-6 confirmation digest (hC) is not pasted into this block"
"$PY" -c 'import re,sys; raise SystemExit(0 if re.fullmatch("[0-9a-f]{64}",sys.argv[1]) else 1)' \
  "$ED_STEP6_CONFIRMED_SHA256" \
  || die 'ED_STEP6_CONFIRMED_SHA256 is not a lowercase 64-hex digest'
test "$ED_STEP6_CONFIRMED_SHA256" = "$(cat "$TRANS/085-ed-step6-confirmed-sha256.txt")" \
  || die 'the pasted hC differs from the 085 witness of the §3.8 confirmation'

CASE=$(new_case c-to-s-later-rewrite "$PROBE_BASE")
"$PY" - "$CASE/$SUCCESSOR_PINSET" "$FIRST_PACK" <<'PY' \
  || die 'later-rewrite sibling-row mutation failed'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
target = pathlib.PurePosixPath(sys.argv[2]).name
d = json.loads(p.read_text())
siblings = [row for row in d["packs"] if row["pack_id"] != target]
if not siblings:
    raise SystemExit("pinset has no sibling row")
siblings[0]["plan_sha256"] = "0" * 64
p.write_bytes(
    (json.dumps(d, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
)
PY
commit_case "$CASE" 'S-0 C-to-S probe: schema-valid sibling-row rewrite'

capture 123-c-to-s-later-rewrite "$PY" "$CASE/scripts/generate_arm_readiness.py" arm \
  --pack-root "$CASE/$FIRST_PACK" \
  --arm-context "$ARM_CONTEXT" \
  --window-custody-root "$CUSTODY/windows" \
  --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256"
expect_rc 123-c-to-s-later-rewrite 1 \
  || die 'later-rewrite probe did not return rc 1'
"$PY" - "$TRANS/123-c-to-s-later-rewrite.stdout.json" "$CHANGED_CODE" "$SUCCESSOR_PINSET" <<'PY' \
  || die 'later rewrite did not reach the authenticated C-to-S gate'
import json, sys
d = json.load(open(sys.argv[1]))
detail = (
    f"digest-conditional allowlist path {sys.argv[3]!r}: "
    "bytes at the reviewed HEAD differ from Ed's confirmed step-6 digest"
)
if d.get("reason_codes") != [sys.argv[2]] or d.get("detail") != detail:
    raise SystemExit(repr(d))
PY
no_traceback 123-c-to-s-later-rewrite \
  || die 'C-to-S rewrite probe traceback'
```

Pass iff the valid transaction crosses the changed-set gate only against Ed's
exact table digest **(D-153: at `$PINSET_MINT_HEAD` the residue is empty and no
arm transcript carries the changed-set code, so "crosses" means both that the
successor was discharged and that nothing else was outstanding)**, while the
later committed rewrite is refused by `DEPENDENCY_CHANGED_SET` before it can be
forgiven by allowlist membership. The
table and its sidecar are immutable during the probe. Authority: D-151
condition 2; `docs/contracts/d117_step6_confirmation_table.md` "Where the
`C → S` edge is enforced." The `123` block's expected `reason_codes` and detail
are CODE-DERIVED predictions (r6, `docs/process_traces/2026-08-25-probe-reachability/`);
estate 10 confirms them by execution.

### 4(f). `DEPENDENCY_MANIFEST` conjunct — both halves

**Source/receipt half — and the digest chain the mutation must carry with it.**
The subject of this half is one specific inconsistency: an evidence receipt
whose facts point at the CURRENT source bytes while its
`dependency_manifest_sha256` still records the OLD ones. To put that
inconsistency in front of R1, every OTHER digest binding between the mutated
source and the pack's plan tree has to be made consistent first, because each
one is authenticated earlier and each one would otherwise refuse first.

r5 propagated only half the chain: it changed the source, updated the receipt's
`facts[*].source_sha256`, and re-sidecarred the receipt — but left the FROZEN
receipt's evidence item still recording the receipt's old SHA.
`_authenticate_generic_evidence_item()` checks exactly that binding at
`:5460-5465`, before it reads fact sources at `:5531-5570` and before lifecycle
validation at `:5608-5619`. Estate 9 executed it and got `rc=2`,
`readiness_evidence_digest_mismatch`, "evidence item digest differs from
authenticated bytes" — a true statement about a binding the probe broke by
accident, not the manifest disagreement it exists to show.

r6 propagates the whole chain, in the order the authenticators read it:

1. mutate `arm_readiness.sources/acceptance-owner.json` (one primary-artifact
   digest zeroed) and re-render it canonically;
2. write the source's NEW SHA into every `facts[*].source_sha256` of
   `arm_readiness.evidence/evidence-acceptance-owner.json`, and **deliberately
   leave `dependency_manifest_sha256` at its old value** — this is the mutation
   under test, and the block asserts the old and new source digests actually
   differ so the case cannot silently degenerate;
3. re-render the receipt canonically and recompute its `.sha256` sidecar;
4. write the receipt's new SHA into the matching `evidence[]` item of the frozen
   receipt the plan's `arm_attachments.arm_readiness.freeze_receipt` names,
   re-render that freeze receipt and recompute its sidecar;
5. write the freeze receipt's new SHA into that same plan freeze slot, re-render
   `plan_tree.json` and recompute `plan_tree.sha256`.

Step 5 is the one that looks dangerous and is not: touching the plan tree is
exactly what §4(c) does to trip R1's manifest gate, so the obvious worry is that
this probe now has two manifest causes and cannot attribute its refusal. The
freeze slot is an ENUMERATED SUBTRACTION at `:4170-4213` — the manifest
deliberately does not bind the freeze-receipt pointer, because that pointer is
rewritten by every legitimate freeze — so propagating it creates no competing
manifest failure. Execution reaches the source/receipt conjunct at
`:4467-4484`, which is the only manifest disagreement left standing.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# CONFIRMATION PAIR, re-pasted per block.
STEP6_TABLE="$CUSTODY/windows/family_publication/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_TABLE" || die 'the promoted step-6 confirmation table is absent'
test -n "${ED_STEP6_CONFIRMED_SHA256:-}" \
  || die "Ed's step-6 confirmation digest (hC) is not pasted into this block"
"$PY" -c 'import re,sys; raise SystemExit(0 if re.fullmatch("[0-9a-f]{64}",sys.argv[1]) else 1)' \
  "$ED_STEP6_CONFIRMED_SHA256" \
  || die 'ED_STEP6_CONFIRMED_SHA256 is not a lowercase 64-hex digest'
test "$ED_STEP6_CONFIRMED_SHA256" = "$(cat "$TRANS/085-ed-step6-confirmed-sha256.txt")" \
  || die 'the pasted hC differs from the 085 witness of the §3.8 confirmation'

CASE=$(new_case manifest-binding "$PROBE_BASE")
"$PY" - "$CASE/$FIRST_PACK" <<'PY' \
  || die 'manifest-binding mutation driver failed'
import hashlib, json, pathlib, sys
root = pathlib.Path(sys.argv[1])

def render(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
    path.write_bytes(raw)
    return raw

def sidecar(path, raw):
    path.with_name(path.name + ".sha256").write_text(
        hashlib.sha256(raw).hexdigest() + "  " + path.name + "\n"
    )

source_path = root / "arm_readiness.sources/acceptance-owner.json"
receipt_path = root / "arm_readiness.evidence/evidence-acceptance-owner.json"
plan_path = root / "plan_tree.json"

source = json.loads(source_path.read_text())
source["primary_artifacts"][0]["sha256"] = "0" * 64
source_raw = render(source_path, source)
source_sha = hashlib.sha256(source_raw).hexdigest()

receipt = json.loads(receipt_path.read_text())
old_manifest_sha = receipt["dependency_manifest_sha256"]
if old_manifest_sha == source_sha:
    raise SystemExit("mutation did not change the source digest")
for fact in receipt["facts"]:
    fact["source_sha256"] = source_sha
# Deliberately leave dependency_manifest_sha256 fixed.
receipt_raw = render(receipt_path, receipt)
sidecar(receipt_path, receipt_raw)
receipt_sha = hashlib.sha256(receipt_raw).hexdigest()

plan = json.loads(plan_path.read_text())
freeze_ref = plan["arm_attachments"]["arm_readiness"]["freeze_receipt"]
freeze_path = root / freeze_ref["path"]
freeze = json.loads(freeze_path.read_text())
matches = [
    item for item in freeze["evidence"]
    if item["path"] == "arm_readiness.evidence/evidence-acceptance-owner.json"
]
if len(matches) != 1:
    raise SystemExit(f"expected one acceptance-owner freeze item, got {len(matches)}")
matches[0]["sha256"] = receipt_sha
freeze_raw = render(freeze_path, freeze)
sidecar(freeze_path, freeze_raw)
freeze_ref["sha256"] = hashlib.sha256(freeze_raw).hexdigest()

plan_raw = render(plan_path, plan)
plan_path.with_name("plan_tree.sha256").write_text(
    hashlib.sha256(plan_raw).hexdigest() + "  plan_tree.json\n"
)
PY
commit_case "$CASE" 'S-0 authenticated manifest source-receipt conjunct'

capture 119-manifest-binding "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$FIRST_PACK" \
  --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}" \
  --step6-confirmation-table "$STEP6_TABLE" \
  --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256"
expect_rc 119-manifest-binding 1 \
  || die 'manifest-binding probe did not return rc 1'
"$PY" - "$TRANS/119-manifest-binding.stdout.json" "$MANIFEST_CODE" <<'PY' \
  || die 'source/receipt conjunct did not reach DEPENDENCY_MANIFEST'
import json, sys
d = json.load(open(sys.argv[1]))
if (
    d.get("reason_codes") != [sys.argv[2]]
    or d.get("detail")
    != "evidence source and receipt dependency-manifest bindings disagree"
):
    raise SystemExit(repr(d))
PY
no_traceback 119-manifest-binding || die 'manifest-binding probe traceback'
```

**Derivation/current dependency half.** The exact coherent manifest-only plan
commands are §4(c), transcripts `104-plan-current` (the first pack, replaying
itself) and `105-plan-sibling` (the second pack, replaying itself — see §4(c)
for why the cross-pack form of this claim is unreachable by design). Both must
return `reason_codes` exactly `[$MANIFEST_CODE]` from
`arm_readiness.py:4485-4542`, each with the current-dependency detail naming its
OWN pack's `plan_tree.json`. All three outputs must be nonzero and
traceback-free. Both logical halves are conjunctive; one does not substitute for
the other. The `119` block's expected detail — `evidence source and receipt
dependency-manifest bindings disagree` — is a CODE-DERIVED prediction (r6);
estate 10 confirms it by execution. Authority:
`docs/process_traces/2026-08-25-probe-reachability/`; R5 S-6 and V-1.vi; SIT-C3;
`arm_readiness.py:4467-4542`.

### 4(g). S-6 dual-validator falsifiers

In a fresh case make the SAME manifest-only plan mutation as §4(c) — the
`window_identity.evidence_root_id` change, never the `window_id` one — then run
both genuinely different validators over that one case. r5 used the shared
`mutate_plan.py` and therefore inherited §4(c)'s masking exactly: estate 9
returned `rc=2` and `readiness_freeze_receipt_mismatch` here for the same
reason, the identity comparison at `arm_readiness.py:6513-6521` firing ahead of
R1. The mutation is now inline in this block (see §4(c) on why the shared driver
file is gone), and the S-6 preserve-mode half of the probe is unchanged in
substance: it still records which of the two admissible dispositions the
candidate is in, and it now applies the fail-ugly traceback check in BOTH
branches rather than only in the nonzero one, since a traceback under `rc=0` is
just as much a mechanism failure.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# CONFIRMATION PAIR, re-pasted per block.
STEP6_TABLE="$CUSTODY/windows/family_publication/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_TABLE" || die 'the promoted step-6 confirmation table is absent'
test -n "${ED_STEP6_CONFIRMED_SHA256:-}" \
  || die "Ed's step-6 confirmation digest (hC) is not pasted into this block"
"$PY" -c 'import re,sys; raise SystemExit(0 if re.fullmatch("[0-9a-f]{64}",sys.argv[1]) else 1)' \
  "$ED_STEP6_CONFIRMED_SHA256" \
  || die 'ED_STEP6_CONFIRMED_SHA256 is not a lowercase 64-hex digest'
test "$ED_STEP6_CONFIRMED_SHA256" = "$(cat "$TRANS/085-ed-step6-confirmed-sha256.txt")" \
  || die 'the pasted hC differs from the 085 witness of the §3.8 confirmation'

CASE=$(new_case s6-dual "$PROBE_BASE")
"$PY" - "$CASE/$FIRST_PACK/plan_tree.json" <<'PY' \
  || die 'S-6 plan mutation driver failed'
import hashlib, json, pathlib, sys
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text())
d["window_identity"]["evidence_root_id"] += "-s0-s6-mutation"
raw = (json.dumps(d, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
p.write_bytes(raw)
p.with_name("plan_tree.sha256").write_text(
    hashlib.sha256(raw).hexdigest() + "  plan_tree.json\n"
)
PY
commit_case "$CASE" 'S-0 S-6 dual-validator manifest-only mutation'

set +e
"$PY" "$CASE/$FIRST_PACK/generate_configs.py" --check \
  --pack-id d117_contrast_qwen25_1p5b_vs_7b_v4 \
  --family-suffix _v4 \
  --preserve-current-frozen-bytes \
  > "$TRANS/120-s6-preserve-check.txt" 2>&1
PRESERVE_RC=$?
set -e
if grep -Eq 'Traceback \(most recent call last\)|^[A-Za-z]+Error:' \
    "$TRANS/120-s6-preserve-check.txt"; then
  die "preserve-mode --check failed ugly (rc $PRESERVE_RC)"
fi
if [ "$PRESERVE_RC" = 0 ]; then
  printf 'disposition=ECHO-HOLE PRESENT\n' >> "$TRANS/120-s6-preserve-check.txt"
else
  printf 'disposition=ECHO-HOLE FIXED (governed nonzero check, rc %s)\n' \
    "$PRESERVE_RC" >> "$TRANS/120-s6-preserve-check.txt"
fi

capture 121-s6-r1 "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$FIRST_PACK" \
  --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}" \
  --step6-confirmation-table "$STEP6_TABLE" \
  --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256"
expect_rc 121-s6-r1 1 \
  || die 'S-6 R1 half did not return rc 1'
"$PY" - "$TRANS/121-s6-r1.stdout.json" "$MANIFEST_CODE" "$FIRST_PACK" <<'PY' \
  || die 'S-6 R1 half did not reach the exact DEPENDENCY_MANIFEST gate'
import json, sys
d = json.load(open(sys.argv[1]))
detail = f"current dependency differs from its derivation binding: {sys.argv[3]}/plan_tree.json"
if d.get("reason_codes") != [sys.argv[2]] or d.get("detail") != detail:
    raise SystemExit(repr(d))
PY
no_traceback 121-s6-r1 || die 'S-6 R1 probe traceback'
```

Expected falsifier: preserve-mode `--check` returns 0 because it echoes
checked-out bytes into its comparison
(`generate_configs.py:1942-1955`), while R1 refuses the same mutation with
`$MANIFEST_CODE` (`arm_readiness.py:4485-4542`). Both dispositions are
admissible and both are recorded: if the candidate intentionally fixed the echo
hole, the first result becomes a **governed nonzero check** and the S-1 manifest
must say so. The R1 half is mandatory either way; only that half can fail this
probe. The `121` expectation is the SAME exact pair as `104` — `reason_codes`
exactly `[$MANIFEST_CODE]`, detail `current dependency differs from its
derivation binding: $FIRST_PACK/plan_tree.json` — because it is the same
mutation on the same pack; that identity is deliberate, and any divergence
between the two transcripts is itself a finding. The pair is a CODE-DERIVED
prediction (r6); estate 10 confirms it by execution. The `120-*` transcript no
longer carries a bare `preserve_check_rc=` line: the disposition line records
the rc where it is not already implied (`ECHO-HOLE PRESENT` is rc 0 by
construction), and the fail-ugly check now runs before either branch. Authority:
`docs/process_traces/2026-08-25-probe-reachability/`; R5 S-6; SIT-C3; AUDIT F-9.

### 4(h). Histsem and pinset probes

Present was captured at `072-histsem-present` and must PASS before arm; because
this clone's reviewed ref is forged, that PASS is local and conditional, not
published green.

**Explicit absence must be probed through an enumerated member.** R2 passed an
invented path (`$CASES/definitely-absent-pinset.json`) as `--pinset` and expected
`histsem_pinset_absent`. That is unreachable: `_load_histsem_pinset`
(`:3285-3345`) rejects any override outside the closed enumeration with
`histsem_pinset_invalid` at `:3301-3304` before it ever reads a file, and the
committed `tests/test_receipt_histsem.py:220-238`
(`test_verifier_cli_refusal_is_canonical_and_exit_two`, post-W1 coordinates)
pins exactly that behaviour.
The only path to `histsem_pinset_absent` is the `present == 0` branch at
`:3340-3344`, reached by naming an **enumerated** member that is absent from the
worktree. The probe therefore removes the successor member in a fresh case and
names it.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

CASE=$(new_case histsem-successor-absent "$PROBE_BASE")
git -C "$CASE" rm -q -- "$SUCCESSOR_PINSET" || die 'could not remove the enumerated successor member'
commit_case "$CASE" 'S-0 probe: enumerated successor member absent'
test ! -e "$CASE/$SUCCESSOR_PINSET" || die 'the successor member is still on disk'
capture 130-histsem-absent "$PY" "$CASE/scripts/verify_receipt_histsem.py" \
  --repository-root "$CASE" --pinset "$SUCCESSOR_PINSET" --require-published
expect_rc 130-histsem-absent 2 || die 'the absent-member probe did not exit 2'
"$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="REFUSE" and d["reason_codes"]==["histsem_pinset_absent"], d' \
  "$TRANS/130-histsem-absent.stdout.json" \
  || die 'the absent-member probe did not produce histsem_pinset_absent alone'
```

**The out-of-enumeration override is a second, distinct probe** — it proves the
closed enumeration is actually closed, which is the property r2's probe
accidentally exercised while claiming something else.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

ABSENT="$CASES/definitely-absent-pinset.json"
test ! -e "$ABSENT" || die 'the out-of-enumeration probe path already exists'
capture 131-histsem-out-of-enumeration "$PY" "$CLONE/scripts/verify_receipt_histsem.py" \
  --repository-root "$CLONE" --pinset "$ABSENT" --require-published
expect_rc 131-histsem-out-of-enumeration 2 || die 'the override probe did not exit 2'
"$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="REFUSE" and d["reason_codes"]==["histsem_pinset_invalid"], d' \
  "$TRANS/131-histsem-out-of-enumeration.stdout.json" \
  || die 'an out-of-enumeration override did not refuse histsem_pinset_invalid'
```

Pass iff the closed v1→successor chain verifies, arms cross the actual
changed-set gate only under the confirmed C→S condition **(D-153: cleanly, at
`$PINSET_MINT_HEAD`)**, an absent **enumerated**
member produces `histsem_pinset_absent`, an out-of-enumeration override produces
`histsem_pinset_invalid`, and all three malformed candidate variants of §4(d)
fail. D-151 condition 6 preserves the rule-11 clarification unchanged: an absent
enumerated member does not tighten the library's default HEAD-absence semantics;
only this explicit CLI/worktree verifier path promises `histsem_pinset_absent`.
Authority: D-151 conditions 2 and 6; RH-8 and normative annexes;
HISTSEM-CONTRACT "Failure semantics"; `verify_receipt_histsem.py:22-73`;
`arm_readiness.py:3285-3345`; `tests/test_receipt_histsem.py:220-238`; AUDIT F-3.

### 4(i). Poison question — direct code-path probe

Create a case at `$EVIDENCE_COMMIT`, delete one generic evidence pair, mint,
commit the refused mint, then replay unchanged.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

CASE=$(new_case poison "$EVIDENCE_COMMIT")
git -C "$CASE" rm -q -- \
  "$FIRST_PACK/arm_readiness.evidence/evidence-acceptance-owner.json" \
  "$FIRST_PACK/arm_readiness.evidence/evidence-acceptance-owner.json.sha256"
commit_case "$CASE" 'S-0 poison input: missing evidence'
capture 140-poison-first "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$FIRST_PACK" --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}"
"$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="REFUSE" and d["mutated"] is True and d["receipt_path"].endswith("freeze-0004.json"), d' \
  "$TRANS/140-poison-first.stdout.json" || die 'poison mint did not write a plan-pinned REFUSE'
commit_case "$CASE" 'S-0 poison refused freeze becomes plan-pinned'
capture 141-poison-replay "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$FIRST_PACK" --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}"
"$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="REFUSE" and d["mutated"] is False and d["receipt_path"].endswith("freeze-0004.json"), d' \
  "$TRANS/141-poison-replay.stdout.json" || die 'poison replay was not idempotent'
```

At the pinned HEAD the expected answer is **YES**. Consequence: the clean
sacrificial PASS in §3.5 is mandatory before each primary mint; after a primary
REFUSE write, abandon the primary clone and restart from `$EVIDENCE_COMMIT` — do
not try to repair the plan-pinned refusal in place. If a candidate changes the
first result to `mutated:false` with no freeze or plan write, record **NO**,
retain the preflight as a defence-in-depth check, and verify no pack bytes
changed. Any third outcome (partial write, traceback, or replay not idempotent)
reopens the mechanism. Authority: R4 r4-2 poison question; R5 V-2;
`arm_readiness.py:6475-6691,6760-6806`.

---

### 4.10 FIXATION — the last commit of the clone proof

**Ordering note: this placement is CLONE-PROOF-ONLY.** In S-0 the fixation
commit is made *after* the probe battery, so that the marker, the arm and
verify, the local green record and every probe in §4 all run at
`$PINSET_MINT_HEAD` — a tree that does not yet contain
`tests/test_receipt_histsem.py`'s fixation edit. That is what makes the arm
clean and is the direct cure for R4-O1 (§3.9).

**The REAL transaction does not do this.** Under D-153 A1 the real transaction
fixates POST-WINDOW: "window close" is the r4-3 commit-freeze close, and the
fixation commit is the first commit after it. S-0's late placement is an
artifact of the clone proof needing to exercise arm, verify and the probes
against the contract head; it is not a claim about transaction sequencing and
must not be cited as one. Authority: D-153 A1 and A6; D-151 condition 3 as
amended.

The delta this applies is the post-D-153 one: it carries ONLY the hS byte pin
and its loud-fail sentinel guard. Every digest-independent consequence of the
chain read now lives in the pre-derivation candidate (D-153 A2), so nothing
mint-falsifiable sits in this commit.

**Step 1 — apply the reviewed fixation delta. This precedes the suite run.**

The fixation commit is the first commit after the ALLOWLIST-CONTRACT CLOSURE in
this clone proof, and it is made only now, after the probe battery. At this hard
review boundary, apply the reviewed mechanical fixation delta committed beside
this runsheet. Its digest was authenticated in §3.6.1 against both the manifest
and its own GNU sidecar. The operator does not invent the edits at the bench:
the delta owns them, and it substitutes exactly one value — the successor's
SHA-256, which cannot exist before the mint. The delta's header explains that
design choice in full.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"

test -z "$(git status --porcelain=v1)" || die 'tree is dirty before the fixation delta'
git apply --check "$DELTA" || die 'the reviewed fixation delta does not apply cleanly: STOP'
git apply "$DELTA"
git diff --name-only > "$TRANS/073-fixation-changed-paths.txt"
test "$(cat "$TRANS/073-fixation-changed-paths.txt")" = 'tests/test_receipt_histsem.py' \
  || die 'the fixation delta touched something other than tests/test_receipt_histsem.py'
```

**Step 2 — substitute the one bench value and prove the substitution happened.**

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# S0-O3 cure: 074 is now PRODUCED in section 3.7 at the mint head.  Here the
# digest is RECOMPUTED from the worktree bytes and compared against that
# record before it is substituted — the successor pinset must not have moved
# between the allowlist-contract closure and fixation.
# Both checks below are the load-bearing ones in this step, so neither may be
# a bare assert statement: python -O strips assert statements, and a
# substitution that silently skipped its equality check would pin an unverified
# digest into the permanent record.  An explicit raise cannot be optimized away.
"$PY" - "$CLONE" "$(cat "$TRANS/074-successor-sha256.txt")" \
  > "$TRANS/078-fixation-substituted-digest.txt" <<'PY'
import hashlib, pathlib, sys
root = pathlib.Path(sys.argv[1])
recorded = sys.argv[2].strip()
pinset = root / "configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json"
digest = hashlib.sha256(pinset.read_bytes()).hexdigest()
if digest != recorded:
    raise SystemExit(
        "successor pinset bytes moved between the allowlist-contract closure "
        f"and fixation: recorded {recorded}, recomputed {digest}")
target = root / "tests/test_receipt_histsem.py"
text = target.read_text(encoding="utf-8")
sentinel = '"S0-FIXATION-SUBSTITUTION-PENDING"'
count = text.count(sentinel)
if count != 1:
    raise SystemExit(f"sentinel appears {count} times, expected exactly 1")
target.write_text(text.replace(sentinel, f'"{digest}"'), encoding="utf-8")
print(digest)
PY
# The digest actually substituted is now an ARTIFACT, not just stdout on the
# operator's terminal: §5 has to be checkable by a reviewer who was not in the
# room, and r5's first cut cited "step 2's stdout" as evidence when nothing
# captured it.
test -s "$TRANS/078-fixation-substituted-digest.txt" \
  || die 'the substituted-digest record is empty'
test "$(cat "$TRANS/078-fixation-substituted-digest.txt")" = "$(cat "$TRANS/074-successor-sha256.txt")" \
  || die 'the substituted digest is not the mint-time record from 074'
if grep -qF 'S0-FIXATION-SUBSTITUTION-PENDING' "$CLONE/tests/test_receipt_histsem.py"; then
  die 'the fixation sentinel survived the substitution'
fi
grep -qF "$(cat "$TRANS/074-successor-sha256.txt")" "$CLONE/tests/test_receipt_histsem.py" \
  || die 'the substituted successor digest is not present in the fixed test file'
git -C "$CLONE" diff --name-only > "$TRANS/075-fixation-changed-paths-after-substitution.txt"
test "$(cat "$TRANS/075-fixation-changed-paths-after-substitution.txt")" = 'tests/test_receipt_histsem.py' \
  || die 'substitution widened the changed set'
```

**Step 3 — run the suite over the FIXED WORKTREE, then make the fixation
commit.** The suite below runs after the substitution and **before** the
fixation commit exists, so it is the fixed-worktree pre-commit run, not a
"post-fixation" one; r4 called it post-fixation, which named a commit that had
not been made yet (Sol 33).

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"

set +e
"$PY" -m unittest -v tests.test_receipt_histsem \
  > "$TRANS/076-histsem-differential-bytepin-tests.txt" 2>&1
HISTSEM_RC=$?
set -e
test "$HISTSEM_RC" = 0 \
  || die "fixed-worktree histsem suite failed with rc $HISTSEM_RC; see 076"
# The byte-pin method must have RUN and PASSED here, on the untampered pinset.
# Its failing counterpart at §4.10 step 4 is what makes this PASS informative.
grep -F 'test_successor_pinset_hs_byte_pin' \
  "$TRANS/076-histsem-differential-bytepin-tests.txt" > /dev/null \
  || die 'the hS byte-pin method did not run in the fixed worktree; see 076'
if grep -E '^(FAIL|ERROR): test_successor_pinset_hs_byte_pin' \
    "$TRANS/076-histsem-differential-bytepin-tests.txt" > /dev/null; then
  die 'the hS byte-pin method FAILED on the untampered pinset; the substitution is wrong'
fi

git -C "$CLONE" diff --exit-code "$PINSET_MINT_HEAD" -- "$BASE_PINSET" \
  || die 'the v1 pinset member changed after the allowlist-contract closure'
git -C "$CLONE" add -- tests/test_receipt_histsem.py
# A6 vocabulary, and A2 content: this commit pins the successor hS byte digest
# and NOTHING else.  The counts moved into the pre-derivation candidate under
# D-153 A2, so r4 message ("SHA and counts after window close") named a change
# this commit does not make, in a reserved vocabulary, in the permanent record.
git -C "$CLONE" commit -m 'S-0 fixation: pin successor pinset SHA-256 (hS) after the allowlist-contract closure'
FIXATION_COMMIT=$(git -C "$CLONE" rev-parse HEAD)
# CLONE-PROOF-ONLY evidence.  This proves the fixation commit is the first
# commit in THIS CLONE after the allowlist-contract closure head.  It is NOT
# evidence that fixation is the first commit after the r4-3 commit-freeze
# window close -- the clone proof has no commit-freeze window at all, and §5
# records the real first-post-window placement as a separate obligation.
test "$(git -C "$CLONE" rev-list --count "$PINSET_MINT_HEAD..$FIXATION_COMMIT")" = 1 \
  || die 'the fixation commit is not the FIRST commit after the allowlist-contract closure'
git -C "$CLONE" update-ref refs/heads/main "$FIXATION_COMMIT"
git -C "$CLONE" update-ref refs/remotes/origin/main "$FIXATION_COMMIT"
record_env FIXATION_COMMIT "$FIXATION_COMMIT"
printf '%s\n' "$FIXATION_COMMIT" > "$TRANS/077-fixation-commit.txt"
```

**Step 4 — the hS byte pin fails BY NAME over a shape-preserving re-mint
(`118-*`), at the fixation head.** Relocated here from §4(e) by ruling item 9
(Opus F1/F2, Sol 25). This is the first head at which `SUCCESSOR_PINSET_SHA256`
and `test_successor_pinset_hs_byte_pin` exist at all, so it is the first head
at which the probe can mean anything.

The tamper is a **shape-preserving canonical re-mint**: same `pack_count`, same
`receipt_count`, same `pack_ids`, canonically rendered bytes, one differing
`plan_sha256`. That shape is chosen for one reason. A crude byte edit is caught
before fixation by this file's canonicality check, and a shape change is caught
by the shape tests, so on either of those cases the pin's verdict is redundant
with a check that already existed. A well-formed re-mint of identical shape is
the case where the pin's verdict is its own.

**Other tests redden on this case too, and that is expected.** Changing a
governed row's `plan_sha256` also trips `histsem_binding_mismatch` in the
full-corpus test. This step makes no claim that the byte pin is the only thing
that notices; the runsheet does not need that claim and it is not true.

What this step DOES claim is narrower and is the reason the assertion is
written the way it is: **the byte pin's own assertion fails, and is named as
having failed.** So the check is not "the suite went red" — r4's probe would
have passed on that noise alone — but `^(FAIL|ERROR):
test_successor_pinset_hs_byte_pin` in the transcript's failure list. That holds
however many other tests also fail.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

CASE=$(new_case pinset-hs-byte-pin "$FIXATION_COMMIT")
"$PY" - "$CASE/$SUCCESSOR_PINSET" <<'PY'
import hashlib, json, pathlib, sys

path = pathlib.Path(sys.argv[1])
raw_before = path.read_bytes()
before = json.loads(raw_before.decode("utf-8"))


def shape(value):
    return (len(value["packs"]),
            sum(row["receipt_count"] for row in value["packs"]),
            sorted(row["pack_id"] for row in value["packs"]))


after = json.loads(raw_before.decode("utf-8"))
row = after["packs"][0]
row["plan_sha256"] = "1" * 64 if row["plan_sha256"] == "0" * 64 else "0" * 64
raw_after = (json.dumps(after, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()

if shape(after) != shape(before):
    raise SystemExit("the re-mint changed the pinset shape; it is no longer a byte-pin-only case")
reround = (json.dumps(json.loads(raw_after.decode("utf-8")), indent=2,
                      sort_keys=True, ensure_ascii=False) + "\n").encode()
if reround != raw_after:
    raise SystemExit("the re-mint is not canonical; canonicality would catch it before hS does")
if hashlib.sha256(raw_after).hexdigest() == hashlib.sha256(raw_before).hexdigest():
    raise SystemExit("the re-mint did not change the bytes; there is nothing for hS to catch")
path.write_bytes(raw_after)
print(json.dumps({"status": "PASS",
                  "shape_preserved": True,
                  "canonical": True,
                  "sha256_before": hashlib.sha256(raw_before).hexdigest(),
                  "sha256_after": hashlib.sha256(raw_after).hexdigest()},
                 indent=2, sort_keys=True))
PY
commit_case "$CASE" 'S-0 probe: shape-preserving canonical re-mint of the successor pinset'
cd "$CASE"

set +e
"$PY" -m unittest -v tests.test_receipt_histsem > "$TRANS/118-pinset-byte-pin.txt" 2>&1
BYTE_PIN_RC=$?
set -e
test "$BYTE_PIN_RC" != 0 || die 'the re-minted successor pinset PASSED the byte-pin suite'
grep -F 'test_successor_pinset_hs_byte_pin' "$TRANS/118-pinset-byte-pin.txt" > /dev/null \
  || die 'the hS byte-pin method did not run in the re-minted case'
grep -E '^(FAIL|ERROR): test_successor_pinset_hs_byte_pin' \
  "$TRANS/118-pinset-byte-pin.txt" > /dev/null \
  || die 'the suite went red without the hS byte-pin method failing: this probe proves nothing'
```

Pass iff the re-mint is shape-preserving and canonical, and
`test_successor_pinset_hs_byte_pin` is named in the transcript FAIL/ERROR list.
Authority: D-151 condition 3; D-153 A2; Opus F1 and F2; synthesis item 9.

**Step 5 — independent recomputation.** An independent reviewer recomputes the
successor SHA-256 and its pack/receipt counts from the committed blob at
`$FIXATION_COMMIT`, checks them against `074-successor-sha256.txt` and against
the substituted literal in `tests/test_receipt_histsem.py`, and later checks the
same SHA against Ed's exact step-6 table (§3.8). A mismatch is a mechanism
failure, not an invitation to reseal.

The local chain verification and fixation tests are necessary but remain
forged-`origin/main`-conditional in this clone. Transcript labels must say
exactly that; they must not say "suite green." R2's activation delta over the 21
`S0-BLOCKED` methods is STRUCK (see §5.1): those are A84/A85 work and no
activation edit over them belongs to the fixation commit. Authority: D-151
conditions 3–4 and Consequences; S-1 MANIFEST §§9.3 and 9.3.5; AUDIT F-2.


---

# 5. ACCEPTANCE CHECKLIST

Evidence root: `$CUSTODY/transcripts` (all referenced artifacts are clone-proof
custody, never a measurement checkout). Check a box only after independently
reading its named artifacts.

- [ ] **r4-2** — One full three-pack sequence is evidenced by `030-*`, `031-*`,
  `032-*`, `040-*`, `042-*`, `050-*`, `060-*`, `061-*`, `070-*`–`078-*`
  (**073, 075, 076, 077 and 078 are produced at §4.10, not at the mint; `074-*`
  is positional-historic — it is produced at §3.7 step 3 and keeps its ordinal
  so its consumers read the same name**), `080-*`, `081-*`, `082-*`,
  `084-marker-forged-ref-classification.txt` (the MARKER's forged-ref
  classification — not to be confused with `094-*`, the local-green one),
  `085-*`, `090-*`, `091-*`, `092-*` and `097-*` (there is no `083-*`: no step
  produces one), plus `098-*`; every pack crosses the actual changed-set gate
  CLEANLY **(D-153: the residue at `$PINSET_MINT_HEAD` is empty, no arm
  transcript carries the changed-set code, and the eleven-kind census has
  returned)**; ordinary path, both unexpected-output namespaces, both plan-tree
  directions, candidate-shape triplet, C→S, and poison probes adjudicate as
  specified. **Every post-mint enforcing transcript was produced with the
  complete `C + hC` confirmation pair**: no transcript in `091-*`, `092-*`,
  `101-*`, `102-*`, `104-*`, `105-*`, `110-*`, `119-*`, `121-*` or `123-*`
  contains "no expected confirmation digest supplied". **(r6: for `104-*`,
  `105-*`, every `110-*` class, `119-*`, `121-*` and `123-*` this is now proven
  MECHANICALLY rather than by a separate grep — each of those probes asserts its
  `detail` string by EQUALITY, and no confirmation-path detail can equal the
  expected one.)** Every cardinality assertion (`3` packs, `8` tamper classes,
  `3` arm transcripts) is recorded, not assumed. **The `105-*` transcript is the
  SECOND pack replaying itself (r6)**, not the first pack replaying a sibling
  mutation; §4(c) records why the cross-pack claim was unreachable by design and
  was retired rather than repaired.
- [ ] **V-2** — Lead/magistrate custody and nondelegation are recorded in
  `001-*` through `010-*`; S-6 both validators are `120-*`/`121-*`; governed arm
  and verify and every transcript have been read with no fail-ugly traceback.
  **Refusal DETAIL, not only refusal code, has been read on every R1
  transcript** (Opus F0): `digest-conditional allowlist path` is ABSENT from
  `101-*`, `104-*`, `105-*`, the seven ordinary `110-*` classes, `119-*` and
  `121-*`, and PRESENT — as the authenticated `bytes at the reviewed HEAD
  differ from Ed's confirmed step-6 digest` detail — in `110-tamper-pinset-json`
  and `123-*`. A code-only reading cannot separate the two causes and is not
  acceptance. **(r6) The reading is now an EQUALITY reading, not a
  presence/absence one**: `104-*`, `105-*`, all eight `110-*` classes, `119-*`,
  `121-*` and `123-*` each assert an exact `reason_codes` LIST and an exact
  `detail` STRING, which is what makes the difference between "the gate under
  test refused" and "an earlier gate refused first" visible at all — the failure
  mode estate 9 found in all six of them. Every one of those expected pairs is a
  CODE-DERIVED prediction until estate 10 executes it; where an estate's
  observation disagrees, the transcript is the finding and the runsheet is
  amended by ruling, never at the bench.
- [ ] **V-1.vi / D-151 C→S** — Split by COORDINATE and by AUTHENTICATOR, which
  r4 ran together and could not have satisfied:
  - **Pre-fixation, at `$PROBE_BASE` (`110-*`, eight cases).** Each of the
    seven ordinary classes refuses through its own digest, binding or
    semantic-replay authenticator, matching the exact `reason_codes`/`detail`
    pair tabulated in §4(e) — which entails that no digest-conditional detail is
    present. **(r6) Two of those seven pairs are not what r5 recorded**:
    `freeze-sidecar` refuses `readiness_receipt_namespace_anomalous` ("sidecar
    mismatch for freeze-0004.json"), because zeroing that sidecar IS a
    namespace-authentication failure; and `freeze-json`, whose tamper now
    recomputes its own sidecar, refuses `readiness_freeze_receipt_mismatch` with
    the detail "existing freeze receipt is not plan-pinned" — the PLAN-PIN
    FILTER at `:6848-6862`, which discards any scanned receipt whose
    `{path, sha256}` disagrees with the plan's pin before
    `_load_freeze_reference()` runs at all, and therefore before the exactness
    check the consult originally predicted (r6 fix round; see
    `03-FREEZE-JSON-AMENDMENT.md`). The two R1 classes
    (`plan-json`, `pinset-json`) exit `1` and the other six exit `2`; the block
    asserts the exit code per class, not merely nonzero. The successor class
    refuses through the authenticated C→S edge ALONE: `reason_codes` exactly
    `[DEPENDENCY_CHANGED_SET]` plus the bytes-differ detail. **No `histsem_*`
    code is expected or admissible for that class** — the tamper stays canonical
    and schema-valid, so the histsem gate returns before raising, and the C→S
    raise owns the refusal. The manifest halves are `104-*` and `105-*` (the
    derivation/current-dependency half, each pack replaying ITSELF) and `119-*`
    (the source/receipt half).
  - **Post-fixation, at `$FIXATION_COMMIT` (`118-*`, one case).** The
    shape-preserving canonical re-mint fails `test_successor_pinset_hs_byte_pin`
    BY NAME in the transcript's FAIL/ERROR list. Other tests fail on that case
    as well — the changed `plan_sha256` also trips `histsem_binding_mismatch`
    in the full-corpus test — and no claim is made that the byte pin is the
    only thing that notices; the by-name assertion is what makes this evidence
    about the byte pin. This case cannot exist pre-fixation, because the method
    does not exist there.
  - **C→S conditionality (`122-*`/`123-*`).** Successor subtraction is
    conditional on Ed's exact table digest, and a later rewrite refuses with the
    authenticated bytes-differ detail rather than a missing-input one **(D-153;
    the subtraction is evidenced by the successor's ABSENCE from `098-*`'s empty
    residue)**. **(r6) The primary C→S vehicles are `122-*` (the synthetic unit
    battery) and `110-tamper-pinset-json` (the freeze path); `123-*` is the
    ARM-ENTRY route** — the same edge reached through the `arm` verb, whose gate
    order puts `_gate_receipt_histsem` in front of everything else. Its rewrite
    is therefore a canonical change to a SIBLING pinset row, leaving the armed
    pack's own row fixed, so neither the pinset shape check nor target-row
    histsem verification can claim the refusal first.
  Any unauthenticated class has triggered the derived-manifest reopen rather
  than being waived. Authority: D-151 condition 2; synthesis items 9, 10 and 15.
- [ ] **rh-8 / D-151 successor** — The 112 arithmetic and the exact
  **ALLOWLIST-CONTRACT CLOSURE** are PASS in `020-*`/`090-*` (A6: "window close"
  is reserved for the r4-3 commit-freeze close and is not what `090-*`
  evidences); present chain and arm crossing are `072-*`/`091-*`; explicit
  enumerated-member absence is `130-*` and the out-of-enumeration refusal is
  `131-*`; missing/extra/unused are `106-*`–`108-*`; all three `_v4` rows and
  local-Git provenance are in the create-only successor at `070-*`; the v1
  member is byte-unchanged. **Fixation placement is TWO separate obligations,
  and only the first is discharged here:** (i) in this clone, `077-*` plus the
  `rev-list --count` assertion prove the fixation commit is the first commit
  after the allowlist-contract closure head — CLONE-PROOF-ONLY, since the clone
  has no commit-freeze window at all; (ii) in the REAL transaction, fixation
  being the first commit after the r4-3 commit-freeze window close is an
  EXTERNAL obligation discharged by that transaction's own record, and no
  transcript in this runsheet may be cited for it. Authority: D-151 conditions
  1–3 and 6; D-153 A1 and A6; Opus F9 and F10.
- [ ] **D-150 marker** — Only `BUILD-AT-BOUNDARY`, CUSTODY-EXTERNAL ran;
  candidate transcript `082-*` says `lane: candidate`, `gate_admissible: false`,
  and names the forged OID; the built marker carries its
  `conditional_paths_deferred` disclosure with gate `R1_DIGEST_CONDITIONAL` and
  `deferred_paths` naming exactly the successor pinset — a deferral that is
  disclosed, never silent (S0-O2 cure); the marker, table and authenticators are
  absent from every allowlist. Authority: MARKER-RULING opening constraints,
  ratified item 2 and Consequences; the step-6 contract's deferral clause.
- [ ] **Custody surface (superseded-by-merge shape)** — The clone provenance
  line (`003-*`: head SHA, green CI run id, the `$BASE` containment gate) is
  present; the mechanically generated manifest and its digest are `007-*`/`008-*`;
  the four executing custody tools in `$CLONE/scripts/` matched their manifest
  `custody_tools` digests before any tool ran (§3.6.1); the fixation delta
  matched both its manifest `custody_inputs` digest and its committed GNU
  sidecar; the anchor map re-checked 15/15 at `$BASE` (`005-*`); and HEADs, Git
  statuses and complete stdout/stderr/exit-code triplets are present under the
  custody root. There is **no** candidate patch, no `$INPUT` tool set and no
  tool sidecar check in this lane: the merge supersedes all three. Authority:
  S-1 MANIFEST §§2.4, 4, 6 and 9.1 G-1/G-4; AUDIT F-1, F-8.
- [ ] **Fixation delta** — `s0-fixation-delta.patch` applied cleanly
  (`073-*`) and touched only `tests/test_receipt_histsem.py` (`073-*`/`075-*`).
  Its single sentinel was substituted with the digest **recomputed from the
  worktree at fixation time and proven equal to the mint-time record** — that
  record is `074-*`, which is what `074-*` evidences; the substitution itself is
  evidenced by `075-*`, by the sentinel-absence grep, and by
  `078-fixation-substituted-digest.txt`, which records the digest step 2
  actually substituted and is asserted equal to `074-*` (Opus F12). The sentinel does not survive anywhere in the fixed file. The
  **fixed-worktree pre-commit** histsem suite is rc 0 (`076-*`) and
  `test_successor_pinset_hs_byte_pin` ran and PASSED in it by name; its failing
  counterpart over the shape-preserving re-mint is `118-*`. Ed's confirmed table
  names the same successor digest. Authority: D-151 condition 3; AUDIT F-2;
  Opus F12; Sol 40.
- ~~S0-BLOCKED addendum~~ **STRUCK 2026-08-23 by magistrate ruling** (recorded in
  the S-1 fix-round packet and MANIFEST §9.3): the 21-method flip theory was
  DISPROVEN BY MEASUREMENT — the partition is S0-BLOCKED 0 / STRUCTURAL 17 /
  CRASH 4; none flips on the S-0 mint. S-0 acceptance is the proving-obligations
  checklist above ALONE. The 17 structural entries ride kernel row A84
  (FIXTURE-MODERNIZATION-01) and the 4 crash entries A85 (MLX-ACID-SIGABRT-01,
  which also requires A84).
- [ ] **Two-part green** — `093-*`/`094-*` are recorded only as local
  forged-`origin/main`-conditional with the exact forged OID. A separate clean,
  strict-four-way real-ref run records PUBLISHED GREEN before acceptance
  closure, **at the published WINDOW-CLOSE head — never at the fixation commit**
  (D-153 A1 + A3; Opus F11), and it is EVIDENCED BY COMMANDS, not by prose:
  `150-*` (four-way ref equality), `151-*` (publication-lane marker replay,
  committed-blob lane, carrying the confirmation pair, `lane: "published"`,
  `gate_admissible: true`, with `confirmation_missing` and
  `confirmation_mismatch` in its executed-checks list) and `152-*`/`153-*` (the
  real-ref suite and its classification), all under
  `$CUSTODY/published-green`. No transcript calls local green "suite green."
  Authority: D-151 condition 4; D-153 A1 and A3; Sol 59.
- [ ] No command touched or read `/Users/edr/JouleWise-measurement-20260818`; no
  quiet-Mac measurement, freeze outside the clone, dry-run, arm launch, consume
  or publication occurred. §3.2's read-only use of
  `/Users/edr/code/JouleWise/.venv` and read-only hashing of
  `/Users/edr/jw_models` are the two permitted host reads and are recorded in
  `029-*`.

### 5.1 S0-BLOCKED set — STRUCK 2026-08-23

Historical text preserved in `s0-runsheet-r2.md` §5.1. The 21 methods are A84
(FIXTURE-MODERNIZATION-01) and A85 (MLX-ACID-SIGABRT-01) work; their markers are
`unittest.skip`, not `expectedFailure`, since the fix round. No activation delta
over them belongs to the S-0 fixation commit, and S-0 does not run a
21-method acceptance command.

---

# 6. FAILURE SEMANTICS

**Mechanism failures — trip V-1.vi and REOPEN to the derived authenticated
manifest.** An ordinary non-allowlisted path crosses **(D-153: at
`$PINSET_MINT_HEAD` the residue must be EMPTY; anything appearing in `098-*`'s
residue is this failure)**; an unexpected evidence
output is accepted in either namespace; either current or sibling coherent
non-freeze plan mutation crosses R1; any missing/extra/unused candidate variant
is accepted; any one of the eight allowlisted classes lacks an independent
tamper authenticator; either `DEPENDENCY_MANIFEST` half crosses; S-6's R1
validator crosses; the successor contains a cross-member duplicate, is
subtracted without the exact C→S edge, remains forgiven after a later rewrite,
or differs from Ed's confirmed digest; an authenticator enters an allowlist;
histsem present does not gate arm or freeze; an absent enumerated member does
not produce `histsem_pinset_absent`; an out-of-enumeration override does not
produce `histsem_pinset_invalid`; or a refusal mint partially writes, fails
ugly, or cannot be safely screened by the sacrificial preflight. A candidate-lane
receipt with `gate_admissible:true`, or any local-green transcript presented as
published or suite green, is also a mechanism failure. The response is not "fix
a test expectation": derive an authenticated manifest, remove every
unauthenticated subtraction, rerun all of S-0, and preserve the failed
transcript. Authority: D-151 conditions 2, 4, 6 and 7; MARKER-RULING ratified
item 2; R5 V-1.vi, V-1.vii, V-2; R4 r4-2; RH-8.

**Instrument failures — STOP, amend on main through the review lane, restart
from a fresh estate.** A step whose environment or dependency precondition is
false; a cited anchor that has drifted; a command that names a file, flag or
refusal code that does not exist; a step sequenced after the step that needs its
output. These are not ordinary defects and they are not fixed at the bench: they
produced cold-gate packets 1, 2 and 3 and then the executability audit, and each
one cost a full estate. The 2026-08-24 record is the precedent — an instrument
defect is cured on main, re-ratified, and S-0 restarts from `§1.1`. Authority:
PACKET-3 RULING R-2 through R-4; AUDIT ruling.

**Ordinary defects — fix and restart the affected clean case or the whole
transaction as indicated.** Wrong CLI spelling, missing custody input, sidecar
checksum mismatch, malformed probe fixture that fails before reaching its
intended gate, transcript collision, or a legitimate non-S-0 T0 refusal after
all lifecycle gates crossed. A primary freeze REFUSE is recoverable only by
abandoning that primary clone and restarting from the committed evidence state
because §4(i) proves it is plan-pinned. A baseline candidate test failure, an
unresolved `ED_RESERVED:` value, an anchor-map or line-audit mismatch, an
11/112 count mismatch, or a dirty reviewed tree is a precondition defect: stop
before mint, correct the candidate, and start again. Authority: R4 r4-2, r4-3,
r4-5; R5 S-6, V-1, V-2.

**Execution defects — the estate is superseded.** A `record_env` duplicate, a
block executed without sourcing `env.sh`, two blocks concatenated into one
shell, or any transcript written by a step whose gate assertions did not all
pass. Custody 035 is the worked example: a compound script continued past failed
U11 assertions and wrote transcripts `031`/`032` with the bootstrap head. Both
files were voided and the estate was superseded. Void the affected transcripts
in writing, then restart from a fresh estate. Authority: PACKET-3 RULING R-4 and
R-5; custody 035.

---

# 7. RESOLVED R1 ITEMS AND ACTIVE CAUTIONS

### O-1 — RESOLVED by D-151

O-1-D is controlling: the successor path replaces v1 in the 112-member contract;
S-0 mints into the successor; subtraction is conditional on Ed's unified-table
C→S edge; and fixation is the first commit after window close — which D-153 A1
binds to the r4-3 COMMIT-FREEZE close, not to the mint (this clone proof's own
late placement in §4.10 is clone-proof-only). The refuted
113-path/test-source option is not an alternate lane. Authority: D-151 Ruling
and Consequences.

### O-2 — RESOLVED by D-150 / marker ruling

The sole branch is BUILD-AT-BOUNDARY, CUSTODY-EXTERNAL, with no tracked marker
paths and a 112-path contract. Authority: D-150 / MARKER-RULING opening
constraints and Consequences; S-1 MANIFEST §4.

### O-3 — RESOLVED by the merge; the custody precondition changed shape

R2 held reviewed-candidate custody as a `$INPUT` precondition: an exported
patch, a binding manifest, and four tool/sidecar pairs. The candidate merged to
main with green CI before S-0 execution, which is strictly stronger provenance.
The precondition is now the `$BASE` containment gate plus the mechanical
manifest of §1.3, and the executing-tool authentication of §3.6.1. S-0 may
verify and execute those bytes but never invent them. Authority: S-1 MANIFEST
§§6, 9.1 and closing provenance; AUDIT F-1, F-8.

### O-4 — RESOLVED before execution

The §9.3.6 re-derivation finding was resolved by the independent seat plus the
fix round: the re-derivation path is proven live and the fixture defect is
cured. O-4 is discharged and the four
`tests/test_arm_readiness_evidence_author.py` methods are ordinary green. If any
of them is red at `$BASE`, that is a baseline candidate test failure under §6
"ordinary defects": stop before mint. Authority: S-1 MANIFEST §9.3.6 and its
fix-round disposition.

### O-5 — ACTIVE: the U11 leg proves less than the rest of S-0

§3.2 runs under a host interpreter that S-0 does not own, and §3.9's
`u11-arm-reverification` leg refuses by design under `$PY`. What S-0 therefore
proves about U11 is: the projection freezes deterministically against the same
weight bytes the committed `_v3` receipts recorded, from the clone's own code,
offline. What it does **not** prove is live arm-side U11 re-verification; that
is proven by the real transaction in the measurement environment. No S-0
transcript may claim otherwise. Authority: PACKET-3 RULING R-1; AUDIT
interpreter-split cross-check ("no dependence").
