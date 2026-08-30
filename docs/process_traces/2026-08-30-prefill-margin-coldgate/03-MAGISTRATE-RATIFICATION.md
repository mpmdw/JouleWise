# Cold-gate ruling on the D-166 prefill rule — magistrate ratification (Fable, 2026-08-30)

Seats: cold Fable instance (`01-COLD-RULING.md`), Opus contract-lens refuter
(`02-refuter-opus.md`, verdict RATIFY-WITH-AMENDMENTS). Both agree on the two
holdings; the refuter's four amendment groups are ACCEPTED IN FULL. This
document is the synthesis; the ruling BINDS AS AMENDED below.

## Ratified holdings

1. **Reading B binds:** "margin ≥ 5" = overlapping-record count ≥ 5 per
   small-model member (`sample_count_margin` ≥ 2). The bare word "margin"
   does not survive into the pre-registration; the rule is stated as a count.
2. **The ladder extends to {512, 1024, 2048, 4096}** — selection-preserving
   (appending a rung to a shortest-that-clears ladder cannot change any
   outcome where an original rung clears), ruled before any G2 measurement
   executes.

## Amendments accepted (refuter A1–A4)

**A1 (record corrections).** The cold ruling's "8 appears nowhere in the
record" is corrected: the Sol seat stated the count-margin-relative-to-three
convention (`01-sol-seat.md:138`, `:53`), and the pre-fix #229 runsheet §D2
implemented Reading A (`count−3 ≥ 5`). Reading B still binds — on the
refuter's own analysis the conclusion survives; the premise is repaired, not
the verdict. The "+2" is ratified as what it is: a DECLARED pre-registration
safety factor chosen at the desk (adverse record alignment is measured;
merged records are measured in occurrence but unquantified in frequency).

**A2 (exhausted-ladder branch, rewritten).** Pre-registration refusal and
instrument refusal are distinct and the paper never prints a reducer code the
reducer did not emit. If no rung clears the count-≥5 floor: the prefill arm
is still collected at 4096; if the reducer itself refuses
(`not_resolvable_sample_count`, count < 3), that refusal is the printed
result; if the reducer resolves but the pre-registered floor failed
(count 3–4), the printed result is the PRE-REGISTRATION refusal, stated in
the paper's own vocabulary ("below the pre-registered count floor of 5"),
with the reducer's resolvable result disclosed alongside. Holm family stays
m = 2 (already enforced; no work).

**A3 (implementation sites, exhaustive).** The refuter's eleven-site list is
the implementation checklist, owned by the `_v5` stream (PR #241 follow-up
round): `_PROSPECTIVE_PREFILL_ARMS` gains `prefill_p4096`
(`analysis_manifest_v3.py:322-324`); the generator candidate guard
(`generate_configs.py:869-870`) and argparse `choices` (`:3256`) gain 4096;
`prefill_prompt_pin` schema bumps to v2 to carry the ruled pre-registration
fields (ladder, count floor, pinned `MIN_PHASE_SAMPLES` consistency check,
selection expression, G2 hash binding, refusal branch); the two pinning
tests update; the #229 runsheet's §D2 jq (Reading-A arithmetic and
`length == 3`) is superseded by the fix-round-2 G2-a rewrite. The floor-pack
clause is CLOSED as the refuter shows (`_v5` is fully parameterized; the
p256 cells belong to the never-collected `_v4`).

**A4 (executability precondition).** The ruled G2 record as it stood yields
ZERO rung observations (decode blocks; 2 small-model members). The selection
rule is executable only through the G2-a prefill sweep now being installed
on PR #229 (H-4: probes at all four lengths, diagnostic, non-claim, own runs
root, independent of the frozen pack — which also dissolves the refuter's
circularity finding). RULED member minimum: **≥ 5 small-model probe members
per rung**; the count floor must hold in EVERY one; large-model probes are
collected for the record but do not gate. G2-a landing with the four-rung
sweep is a PRECONDITION of the selection; the pre-registration object
records the G2-a record hash it selected from.

## Bindings

- The D-166 index row is amended with the cold ruling's §2 sentence, further
  amended by A2's branch text and A4's member minimum (the committed row is
  the binding form).
- Implementation lands via the `_v5` stream (PR #241 follow-up) and the #229
  fix round 2; estate 12 proves the result. Decided ≠ done: the A3 checklist
  is tracked in WAVE-ROWS until every site is closed.
