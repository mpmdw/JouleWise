# B6 NEEDS_RULING: lead ruling (activation af419b16, Opus 5.5, 2026-10-20)

Council: two blind seats, both executed on the synthetic campaign through the real CLI stage chain.
Fable 5.1 (JouleWise-data `claude/b6-nr-council-fable` 1a668af, `reports/b6-nr-council/fable.md`) and Sol 6.1
(`codex/b6-nr-council-sol` 20f10f6, `reports/b6-nr-council/sol.md`). Brief: `../2026-10-20-magistrate-6cff3515/COUNCIL-B6-NR.md`.
No BYTES data exist yet, so both rulings are prospective registration text.

## Q1. One pass's withheld file is missing: RULED

**Ruling.** A missing withheld file is a flag on the *pass*. The pass's cell prints `missing` with the flag
(`bytes.withheld_missing`) and the sidecar's withheld row count. The model then follows Addendum 7 D9 as registered:
if the other pass computes, the model's point is that pass, labelled `one_pass` and carrying the flag, and H1 and H2 use
it (D9 (a)); if both passes are missing the model prints `missing`, has no point and no H1 word, H2 runs on the models
with points (D9 (b)) and the two-pass sensitivity line prints (D9 (c)). No stage refuses for a missing file, including
the blinded post-commit agreement run. This clarifies blinding-ruling item 4 (4b350f47): "the model prints `missing`"
applies when no pass of the model survives.

**Why.** Item 4 was the lead's own process text, written before D9's interaction was examined; it is not registered
arithmetic and no data have been seen. Reading it as "the model prints `missing` even when one pass computed" would
exclude 50 valid runs over a file-custody fault, which a disclose-only flag must not do. The surviving pass is the
same data the model's point would be had pass 2 never been collected (R6's one-pass minimum).

**Dissent recorded.** Sol read item 4 strictly (model `missing`, survivor as a labelled alternative) on precedence
grounds, and wrote that it would support the lead prospectively amending it to a flagged primary survivor rule before
real data. This ruling is that amendment, so no cold judge is needed on Q1.

**Registration text** (`docs/registrations/bytes_pack_v1.md`): Fable's four edits (§11 item 4 slot, §7 one-pass
fallback (a), §15, §18), as written in its report section "Q1 / Smallest change".

**Code, folded into one B4 fix round** (`lane/2026-10-20-b6-blinding-group`), from both seats' executed findings:
1. Census the expected withheld files against the registered sessions and passes *before* reduction, so a whole store
   or CSV that is absent becomes flagged placeholder records, never a pass that silently vanishes from the census
   (Sol: a removed pass CSV currently disappears from `load_records`).
2. Blinded post-commit path (`--stage blinded --stage1-commit`): keep the `withheld_missing` result instead of
   discarding it and emit the same placeholders, so it prints the same `one_pass` / `missing` as stage 2 (Fable Q1.2,
   Q1.4: today the flag is dropped, and with every store missing the run prints only the fit models).
3. `scripts/bytes_analyze.py` `_missing_labels`: union the flag into the point's flags, never replace the list.
4. A model with no point prints explicit `missing` H1 and active-or-resident rows, not an empty list (Sol: `MoE rows=0`).
5. Tests, through the CLI stage chain: one file missing, both missing, and a genuinely uncollected optional pass (R6),
   which is `one_pass` without the missing flag. Give the synthetic campaign one session per sub-pack for this test so
   a missing file costs one pass of one or two held-out models, as in production (Fable: the current fixture puts all
   seven held-out models in one session per pass).

## Q2. A module fix between the stage-1 commitment and held-out release: TO A COLD JUDGE

The seats disagree on a science question: which evaluation is the registered result. Fable: the fixed module evaluates
commitment 1's committed content (content check without the module digest, flagged), commitment 2 beside it. Sol: keep
the equality guard; commitment 1 evaluated by its own retained source tree is the registered result, commitment 2 by the
corrected tree is the labelled alternative, marked as made after exposure to blinded held-out rows. Both print both.
Cold Fable 5.1 judge launched (Claude cloud `session_01Nh33XtHQTeQ56HHJtYCVBh`, prompt
`/Users/edr/night-archive/af419-b6q2-judge/PROMPT.md`, report JouleWise-data `claude/b6-q2-judge*`,
`reports/b6-q2-judge/fable.md`), asked to replay a comment-only change, a held-out-path defect and a fit-line defect.
The §11 held-out-agreement slot stays open until the judge reports. Nothing waits on it before BYTES pass 1's arm.

## Q2: RULED by the cold judge, adopted (16:35 PDT)

Judge: Fable 5.1 cold, JouleWise-data `claude/b6-q2-judge` 57ed4c2 (`reports/b6-q2-judge/fable.md`; its last test
module run was still going at 16:27, ruling and executed facts complete). It replayed a comment-only change, a
held-out-path defect and fit-line and shared-reduce defects through the CLI chain.

**Ruling.** The registered result is the first commitment's committed content evaluated as data by the fixed module;
the defective module is never run for the record. A second commitment is always written by `--stage fit` under the fixed
module from the same inputs, committed in git before the stage-2 release, labelled `post-agreement fix` and marked as
written after both implementations ran on blinded held-out rows; it is printed beside the registered result as the
labelled alternative. Under the committing module the rebuild check stays a refusal; under a changed module it is
reported with two disclose-only flags (`bytes.module_changed_after_commitment`, `bytes.commitment_not_rebuilt`).
A fix of an implementation defect restores the registered arithmetic (the text), so it does not change it.

**Why the lead adopts it.** It takes Fable's evaluation (Sol's procedure prints, as registered, numbers that violate
registered rules: the judge's case shows a wrong MoE answer and 84 of 120 wrong held-out intervals) and Sol's
after-exposure label, and it fixes a gap neither seat closed (a shared-reduce fix changes fit points while the committed
lines still rebuild, so only the second commitment detects it). No new bar: every added comparison is exact equality of
files written by identical code.

**Installed:** registration §11 held-out agreement row, §11 commitment row, §13, §15, §18 on
`docs/2026-10-20-bytes-registration` 2f034fdfb (text verbatim from the judge's section 1, plus the new
`⟦B4: --stage1-commit⟧` slot listed in §18). **Code** (`judge.patch`, 18 lines in `scripts/bytes_analyze.py`): applied
to the B4 lane after the Q1 fix round lands, since that round edits the same function.
