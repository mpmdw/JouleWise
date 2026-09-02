ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: ["configs/campaigns/d117_contrast_v5/generate_configs.py", "joulewise/identity_pins.py", "joulewise/analysis_engine/inputs.py", "joulewise/analysis_engine/__init__.py", "tests/test_d117_contrast_v5_pack.py", "tests/test_identity_pins.py", "tests/test_analysis_inputs.py", "tests/test_analysis_engine.py", "docs/contracts/identity_pin_projection.md", "docs/phase_2/gamma_arm_readiness.md", "docs/contracts/d165_dominance_closeout.md", "docs/decision_log.md"]
GENRE: implementation
EFFORT: xhigh
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# FIX round 1 — decode-identity set (branch fix/2026-09-02-decode-identity-set @ 1a608089)

LINKED WORKTREE `/Users/edr/code/JouleWise-wt-decode-id`. Do NOT commit, do
NOT rebase, do NOT run canonical `python3 -m unittest discover`; the
magistrate commits. Never touch `runs*/`, `~/jw_models`, or any night custody
root. Do not read or write `/Users/edr/code/JouleWise-wt-decode-id2` / `-id3`.

AUTHORITY: `docs/process_traces/2026-09-02-projection-02/171a-RULING-decode-identity.md`
R-1..R-8 (read it first; R-7 `:86-100` is quoted below in F-K). Three
refuters found the defects below — luna 202 (contract lens), Opus 204
(analysis/consumer lens), terra 206 (execution lens: 14 mutations, 5
survived). Apply the dictated closures exactly; anything that does not fit
returns NEEDS_RULING, never improvisation.

HARD FENCE: `sha256(canonical_json_bytes(dominance_criterion_registration()))`
in `configs/campaigns/d117_contrast_v5/generate_configs.py` MUST remain
`1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b` (pinned at
`tests/test_d165_dominance_closeout.py:1770`, `tests/test_night_gate.py:188`,
`joulewise/night_gate.py:27`). Print it in the report after your edits.
`configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/` and every committed
receipt are frozen — never regenerate committed receipts; generate only into
TMPDIR.

## Dictated closures

### Blockers / material

F-A (luna F-R3-MANIFEST-CUSTODY, blocker). `joulewise/identity_pins.py:1593-1607`
looks up `declared_by_manifest.get(manifest_sha)` and compares only
`manifest_ref` to the declared reference; the manifest FILE bytes are never
authenticated against the effective SHA, so a probe that changed one manifest
byte still froze `PASS`. Closure: at freeze (and at verify, F-I), resolve each
declared member's manifest path under the pack root, hash the bytes, and
refuse with the EXISTING unauthenticated-member reason code when
`sha256(bytes) != manifest_sha` (or the file is absent). Regression in
`tests/test_d117_contrast_v5_pack.py`: generate into TMPDIR, flip one byte of
one decode manifest, freeze → refused with that reason code.

F-B (Opus F1, MATERIAL). `joulewise/analysis_engine/inputs.py:3886-3888` reads
`pack_root/plan_tree.json` by bare path inside the gate with no digest check;
a self-consistent forgery (swapped `config_inventory`, recomputed
`config_set_sha256`, re-rendered receipts + sidecars + both `plan_tree` refs)
made the gate return the prefill unit's set `365b4a41…` instead of decode
`604f6e22…`. Closure: authenticate the pack inside the gate — the lineage
dict already carries `pack_sha256` (see `joulewise/arm_readiness.py:10371`,
read-only) — by re-verifying the pack digest (or threading the authenticated
`plan_tree_sha256` in and checking the read bytes against it) BEFORE any
field is trusted; a mismatch returns the gate's refusal (None / fail-closed),
never a set. Regression (F-D below) is the tampered-pack test.

F-C (Opus F2, MATERIAL). `inputs.py:4081`, `:4122`: the fail-closed
`if matches or same_condition_seen: return None` guard moved INSIDE the
`consumer_identity is not None` block, so a multi-identity `_v5` decode unit
whose family has a same-condition exact cell silently takes a transported
floor where the old code refused. Closure: the `same_condition_seen` scan and
its refusal are unconditional; only the per-cell identity comparison is gated
on single-identity. Regression in `tests/test_analysis_inputs.py`: a
multi-identity evidence row with a same-condition exact cell present →
`floor_request_for_evidence` returns None (not a transported floor).

F-D (Opus F3, MATERIAL). `tests/test_analysis_inputs.py:438,:453` mock
`_frozen_consumer_identity_set`; gutting the gate to `return frozenset()`
stays green. Closure: add un-mocked tests that run gate + caller together
against a pack generated into TMPDIR: (1) tampered pack (one receipt byte
flipped after freeze, sidecars left stale) → `floor_request_for_evidence`
returns None; (2) `config_set_sha256` mismatch between receipt and plan tree
→ None; (3) multi-identity evidence without lineage → None (the legacy
refusal at `inputs.py:~4065`). Then confirm by a scratch mutation (revert
after) that `return frozenset()` in the gate now fails at least one of them.

F-E (terra F1 / M1, blocker). Deriving the decode `suite_manifest_set`
declaration by FOLDING emitted config rows (instead of the pre-registered
rotation rule) survived every test. Closure per R-7 ("computed from the
pre-registered rotation rule, never folded from emitted configs"): a test in
`tests/test_d117_contrast_v5_pack.py` that wraps `build_tree` during
generation, alters one staged decode config's manifest binding immediately
before the real builder runs, and asserts the DECLARATION still equals the
rule census `4/4/2/2/2/2/2/2` (a folding builder would change it) while the
freeze REFUSES on the emitted≠declared census.

F-F (terra F2 / M4, blocker). `identity_pins.py:1617` exact census equality
replaced by `emitted >= declared` survived. Closure: test that adds an extra
byte-identical decode config at a new, sorted inventory path in a TMPDIR
pack → freeze refuses (extra member); document in the test docstring that
`>=` would accept it.

F-G (terra F3 / M6, blocker). `identity_pins.py:1637` distinct-identity
count equality has no independent kill (its mismatch state is hard to reach
under the preceding checks). Closure: extract the cardinality check into a
pure helper (declared distinct count vs observed distinct identities →
refusal reason or None) and unit-test a synthetic mismatch in
`tests/test_identity_pins.py`; the freeze path calls the helper.

F-H (terra F4 / M10, blocker). `identity_pins.py:1778` "all members share the
runtime pins" assertion has no kill. Closure: freeze test whose metadata
gives ONE member a different runtime version/pin → freeze refuses with the
existing drifted-member reason code.

F-I (terra F5 / M11, blocker). `identity_pins.py:2384` verification-only
current-vs-frozen runtime-triple comparison has no kill. Closure: freeze and
commit with the normal fixture in TMPDIR, then re-verify after changing a
runtime-version metadata field that leaves declared fields intact →
verification refuses on the frozen/current triple mismatch.

### Should-fix

F-J (luna F-R7-ROSTER). The generic validator only requires a non-empty
unique-ID list; removing `B/prefill_p512` from a generated tree still froze
PASS with three units. Closure: a pack-specific test asserting the GAMMA
roster is EXACTLY the ordered four `A/decode, A/prefill_p512, B/decode,
B/prefill_p512` with A → smaller-model producer plan and B → larger (per
R-7), and that a three-unit tree is refused by the `_v5` pack's own check
(add the check in `generate_configs.py` verification path ONLY if it can be
done without touching `dominance_criterion_registration()`; otherwise pin it
in `identity_pins.py` as a pack-declared roster the generic validator
enforces when present).

F-K (luna F-R2-ROTATION). `decode_prompt_index` returns
`(block − 1) % len(DECODE_PROFILE["prompts"])`; nothing pins the ruled
`% 8`. Closure: test pins `len(DECODE_PROFILE["prompts"]) == 8` AND
`decode_prompt_index(b) == (b − 1) % 8` for b in 1..16, with the ruling
cited in the docstring. Do not change the production formula.

F-L (luna F-R7-DOC). Stale `prefill_p256` literals in governing text:
`docs/phase_2/gamma_arm_readiness.md:11-13` and
`docs/contracts/d165_dominance_closeout.md:61` → `prefill_p<N>` with one
sentence "N is fixed by the G2-a prefill_prompt_pin.v2 record (512 for
`_v5`; 256 was the `_v3` value)". In `docs/decision_log.md`, D-131 is NEVER
edited in place: append to the D-131 entry body a dated paragraph
"**Amendment (2026-09-02, ruling 171a R-7):**" quoting R-7 verbatim from
`171a-RULING-decode-identity.md:86-100` (the cl.2 replacement text) and, for
cl.3, one sentence naming the config-set digest (`config_set_sha256`; single
member = scientific hash, several = domain-separated set digest per R-1).
Index row for D-131 unchanged unless its status text must change — if so,
report NEEDS_RULING with the current row.

F-M (Opus F6). Any authentication failure collapses to
`unavailable_floor_resolution` (`joulewise/analysis_engine/__init__.py:422-423`),
indistinguishable from an ordinary no-match. Closure: emit a distinct reason
(e.g. `floor_identity_set_unauthenticated`) on the gate-refusal path; if a
reason-code census test exists, extend it in the same change and say where;
if the census lives in a file outside scope, return NEEDS_SCOPE naming it.

F-N (luna F-PEDAGOGY). `docs/contracts/identity_pin_projection.md:565-580,
949-958`: `U8`, `U11`, launch lineage, exact-cell route, condition-family
transport, transport group are USED before they are defined. Closure:
reorder or add a short definitions block BEFORE the analysis-gate section so
every term is glossed in plain words at first use (Ed's first-use test);
no term's meaning may arrive only in later text.

### Nits (do them; they are one-liners)

F-O (Opus F4). `inputs.py:3877-3882` `pack_roots` silently drops rows whose
lineage lacks a `pack_root` string → require every authenticated row to
carry the same non-empty `pack_root`; refuse otherwise.
F-P (Opus F5). `inputs.py:4051-4054` hash the identity already in hand
instead of recomputing.

## Mutation check (report each: KILLED by <test> / SURVIVED)

Re-run terra's five survivors after your closures: M1 (fold declaration from
emitted rows), M4 (`>=` census), M6 (drop distinct-count equality), M10 (drop
runtime-pin equality), M11 (drop verify-time triple comparison). Plus
M-gate (`_frozen_consumer_identity_set` → `return frozenset()`), M-guard
(re-nest the `same_condition_seen` refusal under `consumer_identity is not
None`), M-manifest (skip the manifest-bytes hash in F-A). Revert every
mutation; tree diff must equal your intended change only.

## ACCEPTANCE

- `python3 -m unittest tests.test_d117_contrast_v5_pack tests.test_identity_pins tests.test_analysis_inputs tests.test_analysis_engine tests.test_d165_dominance_closeout tests.test_night_gate tests.test_docs_freshness` green — paste exact tails.
- Registration digest printed and equal to `1c0a4a11…783a2b`.
- Regenerate the `_v5` GAMMA pack into TMPDIR and freeze+verify PASS (terra's V4 recipe: census `4/4/2/2/2/2/2/2`, decode 8 identities, prefill 1).
- `git status --short` shows only in-scope files; no committed receipt changed (`git diff --stat -- configs/campaigns/*/identity_pin_projection.receipts` empty).
- Same-signature statement: for each of luna 202 / Opus 204 / terra 206's findings say KILLED (by which test) or what remains.
- `## Clause map` (mandatory): one row per closure F-A…F-P — production site `file:line`, biting test `file:line`, counterfactual (the one-site edit that test fails on) or `NOT PINNED: <reason>`.

## VERIFICATION
`git diff --stat` in the report; nothing outside WRITE_SCOPE touched.
