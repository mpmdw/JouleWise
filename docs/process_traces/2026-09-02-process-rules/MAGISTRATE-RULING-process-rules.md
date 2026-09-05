# Magistrate ruling — two proposed process rules (Opus 159 §E; ruling 171a R-10)

Date: 2026-09-02. Main @ `6075389a` at gate time (now `3e6243df`; the files
cited did not change between the two). Trigger: CLAUDE.local.md rule 11
"any proposed process rule" → cold gate. Instruments: cold Fable adjudicator
(`196-coldfable-process.md`, sealed) and Opus 5 contract-lens refuter
(`197-opus-refute-process.md`, sealed), both run from the same packet
(`coldgate-process.md`) with deliverable-only brief differences. Both verified
the charter digest `099de884…` before the merits and both disclosed the same
unavoidable contamination (harness-injected CLAUDE*.md and the memory index;
neither opened a narrative state doc). The synthesizing magistrate is not a
seat (three-seat rule).

## Disposition

| Q | Cold Fable | Opus refuter | Ruling |
|---|---|---|---|
| Q1 clause→assertion map | AMEND (2 MATERIAL, 1 NIT) | BLOCKER ×2, MATERIAL ×2, NIT | **AMEND — 196 §1.5 ruled text, with two synthesis clauses below** |
| Q2 cross-pack equality check | AMEND (1 MATERIAL, 2 NIT); sweep home REJECTED | BLOCKER ×2, MATERIAL ×3, NIT | **AMEND — 196 §2.5 ruled text; sweep home REJECTED; one synthesis clause** |

The two seats converge. Every Opus BLOCKER is cured by the cold Fable's
amended text rather than contradicting it:

- Opus Q1-BLOCKER-1 ("a test-NAME map filled from `145:179` pairs P-5 with a
  real test that does not bite; zero rounds saved") is the cold Fable's second
  MATERIAL defect (196 §1.2: "the row needs the production site(s) and the
  counterfactual edit, not just a test name"). The ruled text's third cell —
  "counterfactual (the one-site edit that assertion fails on)" — and the duty
  "the execution-lens refuter executes the named counterfactuals before
  choosing its own" are exactly Opus's own diagnosis (197 :45-47: the mutant
  set "was ruled by name (six) instead of derived one per clause").
- Opus Q1-BLOCKER-2 (the vacuity is the confident row) is answered by the same
  cell: a CONFIRMED row without an executed counterfactual is handed to the
  refuters as a finding (196 §1.5).
- Opus Q1-MATERIAL-3 (no carrier; prose no consumer parses "is the very shape
  T26 item 1 was convened to end") — the cold Fable made the `## Clause map`
  heading shape test *optional* (196 §1.5). **Synthesis clause S1: it is
  mandatory**, prospective over custodied `*-impl.md` reports in
  `docs/process_traces/<date>-*/` dated ≥ 2026-09-03, mirroring T26 item 4's
  test. This strengthens the verdict within its own text; it is not an
  overrule.
- Opus Q1-MATERIAL-4 (fan-out blocked on the magistrate reading the
  implementer's self-map anchors the adjudicator; `bridge_protocol.md:65-66`
  ROLE separation). **Synthesis clause S2:** the map is a TARGET LIST for the
  execution-lens refuter, not an input to the contract-lens refuter — the
  contract lens enumerates the ruling's clauses independently and opens the
  map only after recording its own list; the magistrate's pre-fan-out read is
  retained (196 §1.5) because its purpose is to hand `NOT PINNED` rows out as
  findings, which is a targeting act, not an adjudication. Recorded here so Ed
  sees it; the cold text is otherwise adopted verbatim.
- Opus Q2-BLOCKER-6 (the packet's field path `unit.config_set_sha256`
  resolves to `None` on both sides, so `None == None` would CONFIRM the false
  clause) is the strongest finding of the gate and is cured by the cold
  Fable's exhibit form: "the artifact pair (repo-relative paths at a named
  revision), the field, and both observed values" — a lookup that returns
  nothing cannot produce two observed values. **Synthesis clause S3:** the
  field is named as a full JSON pointer, and the pair is the pair the clause
  QUANTIFIES OVER (Opus Q2-MATERIAL-10: floor `alpha` vs floor
  `alpha/prefill_p256` is two units in one receipt, not cross-pack).
- Opus Q2-BLOCKER-7 / MATERIAL-9 (the sweep home does not exist and is the
  wrong stage) = cold Fable §2.2 MATERIAL; both REJECT the sweep home; the
  ruled home is T26 item 4 / D-160 R-5 as amended, enforced by item 4's
  `## Executed evidence` shape test (a receipt-pair exhibit is a `file:line`
  citation) — no new test.
- Opus Q2-MATERIAL-8 (predicate-indifferent failure mode; equality is
  narrower than the evidence): RESIDUAL, recorded. T26 item 4 already covers
  "a path does/doesn't yield an artifact"; this amendment adds "two artifacts
  agree on a field"; any further predicate class is a new proposal with its
  own forcing instance, not a widening here.
- Packet hygiene H1 (both seats): the "171a seat brief Change section"
  precedent was cited without a path — it lives in the magistrate's scratchpad
  brief, not in custody. Magistrate's error; the sub-question was decided from
  rule shape (196 §1.5 last paragraph) and the outcome does not depend on it.

## Ruled text (operative; adopted from 196 with S1–S3)

**Q1 (home: `docs/contracts/bridge_protocol.md` §1 after the
`ACCEPTANCE`/`VERIFICATION` bullets `:48-49`, plus a §10 inventory row; M0
one-line pointer; shape test in `tests/test_docs_freshness.py`):**

> A delegated implementation brief whose `AUTHORITY` includes a ruling with
> implementation clauses carries, as an `ACCEPTANCE` item, the CLAUSE MAP. The
> brief-writer decomposes the ruling into rows, one per proposition that a
> single production-site edit can falsify while every other row stays true (a
> value, a key set, a refusal code, a status literal, a hash binding, a call
> count), each row quoting the phrase with ruling `file:line`. The seat's
> final report returns the map under a `## Clause map` heading with three
> cells per row: production site (`file:line` where the bytes are produced —
> one row per site when a clause is realized at several), biting assertion
> (test method `file:line`), and counterfactual (the one-site edit that
> assertion fails on) — or `NOT PINNED: <reason>`. Every fix round returns
> the delta for the rows it touched. The refuter fan-out launches only after
> the magistrate has read the map; every `NOT PINNED` row and every row
> lacking a counterfactual is handed to the refuters as a finding; the
> execution-lens refuter executes the named counterfactuals before choosing
> its own; the contract-lens refuter enumerates the ruling's clauses
> independently and opens the map only after recording its own list (S2).
> Custodied `*-impl.md` reports dated ≥ 2026-09-03 carry the heading (S1,
> shape test).

**Q2 (home: D-160 R-5 as amended by D-170 / T26 item 4, additive):**

> The same inadmissibility applies to a ruling, addendum, or draft contract
> clause whose dispositive premise asserts that a named field is equal, or a
> set identical, across two artifacts, packs, or units (producer vs consumer,
> floor vs contrast, unit A vs unit B). The custody directory must carry, as
> a listed packet input, the artifact pair the clause quantifies over
> (repo-relative paths at a named revision), the field as a full JSON
> pointer, and both observed values (S3). Where no committed pair exists the
> clause is recorded `UNVERIFIED against artifacts` and may enter contract
> text only as a stated assumption, never as a MUST. Duty on the packet
> assembler or drafter; a seat that finds no exhibit returns the question
> UNRULED. The S9-shape sweep does not carry this check: it grades
> installation, not truth. The consult-brief "Executed:" block gains the
> words "or artifact-pair exhibit".

## Installation (decided ≠ done; T26 item 1 form)

Both rules are installed. The T26 install branch
(`feat/2026-09-02-t26-install`) merged as PR #273, and the former installing
row `T26-RULING-INSTALL-01` is retired. D-170's dated addendum records the
producer evidence. The installed sites are the D-170 Q1/Q2 paragraph, the
D-160 pointer, `bridge_protocol.md` §§1 and 10, the Mission M0 pointer, and
`test_custodied_impl_reports_carry_clause_map` beside the item-4 test. This
ruling and both sealed outputs remain custodied under
`docs/process_traces/2026-09-02-process-rules/`.

## Executed evidence

Receipt-pair exhibit for Q2 (bench, main `3e6243df`), the JSON pointer being
`/identity_units/<i>/model_runtime_config/config_set_sha256`; the packet's
`/identity_units/<i>/config_set_sha256` resolves to `None` on every unit:

```
$ python3 - <<'EOF'
import json
for p in ["configs/campaigns/d117_floor_qwen25_1p5b_v3/identity_pin_projection.receipts/projection-0001.json",
          "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/identity_pin_projection.receipts/projection-0001.json"]:
    d=json.load(open(p))
    for u in d["identity_units"]:
        print(p.split("/")[2], u.get("config_set_sha256"), u["model_runtime_config"]["config_set_sha256"][:8])
EOF
d117_floor_qwen25_1p5b_v3 None bf0ea6a3
d117_floor_qwen25_1p5b_v3 None 67059870
d117_contrast_qwen25_1p5b_vs_7b_v3 None 604f6e22
d117_contrast_qwen25_1p5b_vs_7b_v3 None 365b4a41
d117_contrast_qwen25_1p5b_vs_7b_v3 None fc4b4e76
d117_contrast_qwen25_1p5b_vs_7b_v3 None 9c6fda6f
exit 0
```

Charter digest: `shasum -a 256 docs/process/coldgate_charter.md` →
`099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` (both
seats, verified before merits). Q1 home anchors: `docs/contracts/bridge_protocol.md:48-49`
(`ACCEPTANCE`/`VERIFICATION` bullets), `:787` (§10 heading).

## Addendum 2026-09-02 (Sol 241 fresh pass, F3) — packet basename

The gate-record paragraph above names the packet as `coldgate-process.md`.
The custodied file is `PACKET-coldgate-process.md` in this directory
(`test -e docs/process_traces/2026-09-02-process-rules/coldgate-process.md`
returns 1; `test -e docs/process_traces/2026-09-02-process-rules/PACKET-coldgate-process.md`
returns 0). The body is left as sealed; this addendum is the correction.
