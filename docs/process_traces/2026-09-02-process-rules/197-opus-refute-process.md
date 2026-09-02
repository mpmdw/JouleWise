# 197 — contract-lens refutation of the two draft process rules (Q1, Q2)

Opus 5, contract-lens refuter paired with a cold Fable adjudicator. Charge (packet :116-124): BREAK both
drafts — duplication/contradiction with binding text, vacuous satisfaction, cost per seat. Not improve them.

## 0. Disclosures (charter §4, §9)

**Digest.** Expected `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` (packet :14-15);
observed via `shasum -a 256 docs/process/coldgate_charter.md`: identical. **MATCH**, verified before any
merits. `git rev-parse HEAD` = `6075389a13df206205651175a7a9d52135df6fde`, matching packet :8; tree clean,
and clean again at exit (`git status --porcelain` → 0 lines).

**CONTAMINATION — material, unavoidable.** My harness injects as system context, before any tool call,
`~/.claude/CLAUDE.md`, `JouleWise/CLAUDE.md`, `JouleWise/CLAUDE.local.md` (the rule-11 doctrine) and a
session-memory index. Charter §4 forbids exactly these; I could not decline delivery. I did not seek them,
did not open the memory files they link, and no conclusion below rests on them — every claim cites a repo
path I opened this session. Discount any place I appear to know undisclosed doctrine. Rule 11 also reached
me admissibly through the packet (`159:313-315`, quoted as the object of Q1). Also received: a `git status`
snapshot with five commit subjects (narrative); not relied on.

**Read set.** Packet; charter; the nine evidence paths at packet :26-47; the binding texts the deliverable
names (`docs/contracts/bridge_protocol.md` §1-§2, S9 `METHOD.md`, `scripts/gen_state.py`,
`state_kernel.schema.json`, `state_kernel.json`); plus `145-sol-proj02-impl.md` §Change/§Tests/§Mutants —
the implementing seat's report, without which Q1's causal claim cannot be tested at all. No
README/RUN_STATE/TASK_QUEUE/orchestration/agent_playbook, no CLAUDE*.md or memory file opened by me. No
state-changing command, nothing written under the repo, no codex/claude process launched.

**Packet hygiene (§6).** Two defects (H1, H2). Otherwise neutrally assembled: it volunteers evidence
against both its own proposals (:109-113, :93-96).

## Q1 — clause→assertion map as a brief deliverable

**Q1-BLOCKER-1 — replayed on its own incident, the rule produces a filled-in row and the defect still
ships.** The implementing seat already delivered a clause→site map with file:line per clause
(`145-sol-proj02-impl.md:174-181`, P-1..P-7), a counterfactual per test (`:183-193`), and an executed
six-mutant table (`:195-204`, "All six were executed from isolated copies"). The ruling itself named
assertions: P-10 is "seven named tests" with exact method names (`151-opus-proj02-contract.md:18`). Fill
Q1's map from `145:179`: P-5 → `identity_pins.py:1685` →
`test_projection_check_ids_carry_shared_mint_projection` (`tests/test_identity_pins.py:1382`) — a real,
on-topic test, **not** a NOT PINNED row. `149-terra-proj02-exec.md` EXE-02 proves that pairing false:
dropping `prompt_realizations` from the hashed `probe_metadata` at `:1685` **passed 219 tests** (V8,
`"result":"pass"`, `Ran 219 tests … OK`); `151:37` reproduces it independently (`Ran 75 tests in 6.008s /
OK`, "survives every one of the seven ruled tests"). The map's atom is a test *name*; the defect class is an
assertion that does not *bite*. Counterfactual: adopt Q1 verbatim and replay round 1 — map delivered, no NOT
PINNED rows, fan-out launches, EXE-02 still found in round 2. Zero rounds saved. What actually caught all
four instances was mutant execution (149 V7-V9; 151 F1; 157 V2-V4), which the brief **already required** —
it failed only because the mutant *set* was ruled by name (six) instead of derived one per clause.

**Q1-BLOCKER-2 — the vacuity is the confident row, not the NOT PINNED row.** Packet :121-122 anticipates an
all-"NOT PINNED: by design" map; that failure is self-flagging. The real one is ten CONFIRMED rows of which
one does not bite — i.e. `159:25` ("All ten are pinned except one clause inside P-5"), reached only after
four seats over three rounds. The draft text (:60-65) requires a name, never the counterfactual input that
would fail, and is self-certified by the author of both artifacts.

**Q1-MATERIAL-3 — no mechanical carrier in either proposed home.** `bridge_protocol.md` §1 (`:26-83`) has no
map field, and its `ACCEPTANCE` ("Observable conditions required for completion", `:47-48`) plus
`VERIFICATION` (`:49-50`) already obligate this content — a ruling's clauses absent from `ACCEPTANCE` is
already a §1 non-conformance, so Q1 duplicates it. §2 forecloses the envelope route twice: exactly two lines
and "No non-whitespace content may follow its JSON line" (`:143-144`, `:178-179`), so a ~110-line map cannot
ride after it; and "Unknown additional object keys are tolerated **and ignored**" (`:180-181`), so a map key
inside it is contractually inert; its `verification` is defined as "Checks actually performed and their
results" (`:158-159`) — the map is neither. Packet :69 concedes no shape test. The kernel cannot hold it
either: `gen_state.py:101-105` `_check_cell_text` rejects newlines and `|`, and
`state_kernel.schema.json:62-75` types `acceptance.evidence` as arrays of such cells — a table is
structurally inexpressible. Net: ratified into prose no consumer parses and no test enforces, the very shape
T26 item 1 was convened to end, which binds process rules to the decision log, Mission M0 and *tests*
(`COLD-GATE-RULING.md:104-111`).

**Q1-MATERIAL-4 — the gate ordering inverts review and anchors the adjudicator.** "The refuter fan-out is
launched only after the magistrate has read the map" (:63-65). The map is the implementer's self-assessment,
and §1 `ROLE` "MUST NOT combine implementation, independent review, and final adjudication"
(`bridge_protocol.md:65-66`). All four catches came from seats not handed it — 151 contract, 149 execution,
157 delta, 159 apex (`159:305-310`) — and the map's only demonstrated value came from being written by the
*fourth* seat (`159:315-316`). Q1 makes fan-out block on a magistrate read to buy that.

**Q1-NIT-5 — cost.** `159` §A is `:23-133` = 111 lines / 10 clauses ≈ 11 lines/clause, plus a blocking read
per brief, against zero demonstrated catches. Small; not the reason to reject.

**H1 — packet defect (Q1, MATERIAL).** :109-113 asks whether Q1 is new or an amendment of the 171a seat
brief's "Change" section, but that brief is not in the evidence list and is absent from the repo at
`6075389a` (`grep -rln "NOT DONE (why)" docs/` → no match; not under
`docs/process_traces/2026-09-02-projection-02/`). That sub-question is undecidable from the read set.
**Minimum cure:** supply path, revision, exact line range. BLOCKER-1 is unaffected — it rests on
`145:166-204`, a stronger instance of the same precedent.

## Q2 — receipt-pair check for cross-pack equality clauses

**Q2-BLOCKER-6 — executed vacuity: the rule as written returns EQUAL on the very pair meant to refute the
clause.** Packet :38-40 directs "compare each unit's `config_set_sha256`". Doing exactly that over
`identity_units[]` in both receipts yields **`None` for all six units in both files** — no such unit-level
field exists. `None == None`, so the seat records "checked, equal" and **confirms** the erroneous "producer
and consumer sets equal" draft. Absent-on-both-sides reads as agreement. The real values sit at
`identity_units[i].model_runtime_config.config_set_sha256`: floor `alpha` = `bf0ea6a3…`,
`alpha/prefill_p256` = `67059870…`
(`configs/campaigns/d117_floor_qwen25_1p5b_v3/identity_pin_projection.receipts/projection-0001.json`);
contrast `A/decode` = `604f6e22…`, `A/prefill_p256` = `365b4a41…`, `B/decode` = `fc4b4e76…`,
`B/prefill_p256` = `9c6fda6f…` (same filename under `d117_contrast_qwen25_1p5b_vs_7b_v3/`). Both receipts
`status: PASS`. Contrast `A/decode` carries `producer_plan_reference.plan_id =
plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v3` — the floor's own plan — yet a different digest,
so **the packet's substantive Q2 fact (:101-106) is CONFIRMED**; only its field path is wrong. Generalized:
a clause names a concept in prose, a receipt keys a JSON path; without requiring the resolved path and both
observed values quoted, a missing-field lookup is indistinguishable from a passing check.

**Q2-BLOCKER-7 — the home does not exist, and the named document cannot hold it.** (i) `state_kernel.json`
at `6075389a` holds 116 tasks; none is a standing pre-window S9-shape sweep row (no task mentioning both a
sweep and pre-window/S9-shape; no `T26`/`SWEEP` ids). The S9-derived rows present are per-finding cures
(`:455`, `:1721`, `:1879`). Packet :93-95 concedes the install is unmerged — so adoption mints a new
ruled-not-installed clause, the exact class `COLD-GATE-RULING.md:45-101` exists to end. (ii) METHOD.md is a
frozen record: titled "method of record" (`:1`), pinned to baseline `0dd3b6dc` with "Every `file:line`
citation in this trace was read at that commit" (`:15-17`), closing with "Standing bias of this method"
about a sweep already run (`:75-80`); adding "a new step" edits the record of a completed sweep. T26 put the
residual in a **kernel row**, not METHOD.md: "re-run before every transaction (record as a standing
pre-window row)" (`COLD-GATE-RULING.md:100-101`) — so Q2's proposed home **contradicts** the text it claims
to extend. (iii) Acceptance evidence is an array of `cellText` (`state_kernel.schema.json:62-75`) barring
newlines and `|` (`gen_state.py:101-105`), validated only for non-emptiness (`_check_pointer:131-165`
validates pointers, not prose).

**Q2-MATERIAL-8 — duplicates a stronger installed check, or has no carrier.** T26 item 1 already requires,
for any registered implementation clause, that the kernel dependency reach `satisfied` only with an
`evidence` pointer to "the regression that FAILS when the ruled value is absent at the producer"
(`COLD-GATE-RULING.md:78-82`), enforced by `gen_state.py:185-191` plus CI. A biting regression strictly
dominates "open one committed receipt pair and compare the named field". So Q2 is a weaker duplicate for
registered clauses and unattached for the rest. Its scope is also narrower than its evidence: it fires only
on *equality* predicates, while the R-10 failure mode — prose promoted to contract text with no artifact
opened — is predicate-indifferent.

**Q2-MATERIAL-9 — wrong stage.** R-10's incident (`171a:124-129`) is a defect in draft contract text during
synthesis, corrected at ruling time (`171a:102-104`, "not required to be equal"). A *pre-transaction* sweep
runs after such a clause is already installed; the mechanism that actually caught it was the ruling review
itself. The cure is bound to a stage that, in the one instance of record, would have been too late.

**Q2-MATERIAL-10 — "a receipt pair" need not exercise the clause.** The text (:79-81) binds nothing to the
units the clause quantifies over: a seat satisfies it by comparing floor `alpha` (`bf0ea6a3…`) against floor
`alpha/prefill_p256` (`67059870…`) — two units, one committed receipt, not cross-pack at all. And
`UNVERIFIABLE` (:81) has no consumer: no status vocabulary admits it, no check refuses on it,
`gen_state.py` carries no invariant over it.

**Q2-NIT-11 — cost.** One resolved-path field comparison per clause; my own resolution took three probes
because the path is undocumented in the clause. Cheap. Cost is not the objection.

**H2 — packet defect (Q2, NIT).** :38-40 names a field path that does not resolve (BLOCKER-6); the
underlying proposition is nonetheless verified. **Minimum cure:** restate as the full JSON pointer. Not
disqualifying — the packet inadvertently supplied the strongest evidence against its own Q2 draft.

## Where I disagree with the magistrate's framing (§8 — silence reads as concurrence)

The packet frames both items as candidate *additions*. On the evidence I opened, Q1's forcing problem is an
unenforced artifact, not a missing one — the mutants were ruled by name rather than derived one per clause
(`145:197-204` vs `159:25`); and Q2's is a clause admitted to contract text with no artifact opened at
*drafting* time (`171a:96-104`), not a missing sweep step. Both drafts, as written, are satisfiable without
touching either forcing problem. Tiers: Q1 — BLOCKER ×2, MATERIAL ×2 (+H1 MATERIAL), NIT ×1; Q2 — BLOCKER
×2, MATERIAL ×3, NIT ×1 (+H2 NIT). I make no disposition recommendation; that is the cold adjudicator's, and
I have not seen its ruling.
