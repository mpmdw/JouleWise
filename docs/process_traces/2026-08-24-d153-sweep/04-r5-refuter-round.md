# r5 cure PR #187 — refuter round and magistrate adjudication

Refuter: Sol gpt-5.6-sol xhigh, read-only, audited (run key
20260825T055820Z-35398-pr187-refuter-report, thread 01a0377f-8963-…), verdict
**REFUTED**, coordinated and independently replayed by an in-session
lieutenant agent. Target: PR #187 head d7275732.

Findings: **F1 blocker** — for `110-tamper-pinset-json` the runsheet requires
`histsem_*_(mismatch|invalid)` AND the C→S `digest-conditional allowlist
path` / bytes-differ detail in the same transcript; the raise site
(`_require_confirmed_conditional_path`, caught at the replay boundary and
returned as `reason_codes=[DEPENDENCY_CHANGED_SET]`) can never emit a
`histsem_*` string — the two assertions are mutually unreachable. **F2
blocker** — the relocated 118 probe's "SOLE discriminator" claim is false:
the shape-preserving re-mint also reddens the full-corpus test through
`histsem_binding_mismatch` on the changed `plan_sha256`. **F3 should-fix** —
§5 cites "step 2's stdout," which is never redirected to a transcript. **F4
nit** — the §0.1 exemption says four placeholders; the block has three.
Item-18 deviation (PRESENT for the pinset class): **SUSTAINED** by refuter
and magistrate.

## Adjudication

1. **F1 and F2 are cure-round defects, not a recurrence of the sweep's
   epoch/supply signature.** The standing same-signature escalation trigger
   is NOT met: this is the first fix round on this stream and the defect
   class (over-assertion introduced while composing cures) differs from the
   consult's root cause. The refuter's flag is answered here rather than
   looped past: a SECOND failed fix round on these same formulations would
   meet the trigger and go to the cold gate.
2. **F1 cure:** for the pinset class only, the expected refusal is the C→S
   one — assert `DEPENDENCY_CHANGED_SET` by name plus the authenticated
   bytes-differ detail; drop the `histsem_*` expectation for that class and
   keep it wherever a class actually reaches the histsem layer (re-derive per
   class from the raise sites, do not assume).
3. **F2 cure is prose, not case redesign.** The R-1 item-9 amendment's
   isolation rationale was hS-versus-canonicality; "sole" over-claimed. The
   case design stands (fixation-head cut, shape-preserving canonical
   re-mint, by-name assertion). The claim becomes: the byte pin's OWN failure
   is proven by name, independent of which other tests also redden; §5
   language follows. No cold-gate question is needed — this resolves the
   magistrate's own amendment wording against replayed mechanics, in the
   direction of claiming less.
4. **F3 cure:** make the §5 citation true — capture the step-2 stdout to a
   named transcript or cite only artifacts that exist; whichever keeps the
   acceptance check mechanical.
5. **F4:** fix the count.
6. After the fix round: the already-mandated JOINT delta re-audit over both
   stream heads (runsheet + freeze-CLI) remains the re-ratification gate.
