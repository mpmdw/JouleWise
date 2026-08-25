# Magistrate ruling — freeze-receipt pack_root identity semantics (D-154)

Magistrate: Fable 5, T23/T24 session, 2026-08-25.
Trigger: estate-7 execution — probe 4(a) refused at the pack-identity
equality (`arm_readiness.py:6448`) before reaching the changed-set gate; the
recorded `pack_identity.pack_root` is the ABSOLUTE minting path, so every
`new_case` freeze replay in §4 (101, 104, 105, the eight 110-*, 119, 121,
and the 123 arm) refuses on location, not content. Verified at the bench:
byte-identical pack trees between freeze and mint; the recorded vs case
paths differ only in the clone prefix. The Opus seat further verified that
7/7 resolvable committed receipts on main differ from this checkout ONLY on
`pack_root` — the readiness replay engine has never been exercisable outside
the two measurement directories.

Seats: `01-opus-seat.md` (global-relativization recommendation, attack
steelman, reader survey, detail-string defect, mint-time re-siting of the
locality lens) and `02-sol-seat.md` (successor-scoped repo-relative
projection, preserving the 2026-08-20 v3 location ruling). Cross-model per
the diversity directive; probe-cure options refuted independently by both.

## Rulings

**R-1 — Code cure, Sol's successor-scoped shape, ADOPTED.** For
registry-governed generations at or above
`family_publication_first_generation` (= 4), the `_load_freeze_reference`
identity comparison treats `pack_root` as repository-relative structural
identity (both sides projected; lexical validation of the recorded path —
it need not exist; no normcase; non-repo packs keep refusing). `_v3` and
earlier keep absolute semantics: the 2026-08-20 magistrate ruling (lines
138-141) pins v3 replay to its archival location, and this cure must not
silently supersede a standing ruling — that avoidance, not convenience, is
why Sol's scoping beats Opus's global drop. Opus's stronger point is also
adopted inside the shape: the repo-relative projection REMAINS a compared
identity term (a byte-identical pack at a different repo-relative path
still refuses), so no lens is dropped.

**R-2 — Refusal details become true, per branch.** The content-mismatch
branch keeps "freeze receipt pack identity differs from committed pack
bytes" (now true — it fires only on content). The v4+ projection-mismatch
branch gets its own detail naming the repository-relative location
difference. The v3 absolute-mismatch branch gets a detail naming the
location binding and the ruling that imposes it. No new reason codes
(D-151 condition 1e).

**R-3 — The locality lens is re-sited, not retired (rule 11).** The one
real event the absolute comparison ever caught (T10 wtTXN mint) is better
caught ONCE, AT MINT, against a declared target: a kernel row registers the
mint-time measurement-checkout declaration check (new reason code +
registry entry, fenced outside the S-0 window). Until it lands, the
recorded absolute path remains in every receipt as provenance, and the T10
class remains detectable by inspection of that recorded value.

**R-4 — Estate 7 disposition: instrument failure; STRUCK.** The runsheet's
failure semantics govern (environment/dependency precondition false →
cured on main, re-ratified, restart from §1.1). Estate 7's custody is
preserved read-only, and its positive results STAND AS EVIDENCE OF
EXECUTABILITY for §§1.1-3.10-local (bootstrap, three freezes, third mint,
S0-O3 074 in-band, marker + deferral disclosure, Ed-confirmed table at
hC e5a1caaf…, first-ever §3.9 arms with the C+hC pair, eleven-kind census,
full-suite local green) — none of that is claim custody, all of it is
instrument-proof. Estate 8 runs at the cured head after re-ratification.

**R-5 — Implementation gauntlet (C-028):** Sol implements (WRITE_SCOPE:
joulewise/arm_readiness.py + the two test modules the seats name), with the
seats' combined regression list: cross-clone idempotent replay green;
wrong repo-relative location refuses; every non-pack_root content mutation
still refuses with the byte-mismatch detail; v3 stays location-bound;
histsem foreign-root PASS retained; the mutant restoring the absolute term
in the v4+ branch goes red. Opus part-3 doc corrections ride along
(tests/test_arm_readiness_lifecycle.py:2265-2270 docstring re-derivation;
readiness↔histsem contract cross-reference). Fresh cross-model refuter,
then merge, then estate 8. The runsheet needs no §4 edits for this cure —
the probes' expectations were correct; the gate now lets them reach their
targets.

**R-6 — Scorekeeping (rule 2).** Sol-only: the v3-ruling collision (the
decisive point), the registry-scoping mechanism, the too-weak-drop
refinement. Opus-only: the 7/7 empirical sweep on main (turning an S-0 bug
into a repo-wide finding), the falsifiability framing for the paper, the
mint-time re-siting design, the detail-string defect, the reader survey
with the reauthor_clean precedent. Both: probe-cure refutation, estate-8
acceptance. The two-seat spend earned its cost again.
