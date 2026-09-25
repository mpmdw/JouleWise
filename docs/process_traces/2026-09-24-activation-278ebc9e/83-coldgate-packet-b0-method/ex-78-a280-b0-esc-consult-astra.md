```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Astra 6: replace witness-by-witness repair with operation-specific validation boundaries and differential acceptance.",
  "workspace": {
    "base_requested": "2ea6a7ec",
    "base_mode": "descendant",
    "head_start": "bee658c5acc4dd860a382317c40ec4421587a13a",
    "head_end": "bee658c5acc4dd860a382317c40ec4421587a13a",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"F1","severity":"blocker","summary":"Kind resolution changes operation-specific validation, refusal precedence and recovery behavior."},
      {"id":"F2","severity":"blocker","summary":"The driver resolver returns dispatch identity from an unauthenticated wrapper."},
      {"id":"F3","severity":"should_fix","summary":"Named witnesses do not constitute a generated differential acceptance test."}
    ]
  },
  "verification": [
    {
      "id":"V1",
      "kind":"smoke",
      "cmd":"python3 -B /tmp/278ebc9e/b0esc-astra/probe.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["no declaration: no sidecar/source/C5 -> calibration","idle declaration: no sidecar/source/C5 -> quiet_predicate_evidence","PROBES_COMPLETE"]},
      "expected":{"exit_code":0,"tail_regex":"PROBES_COMPLETE"}
    },
    {
      "id":"V2",
      "kind":"smoke",
      "cmd":"TMPDIR=/tmp/278ebc9e/b0esc-astra python3 -B /tmp/278ebc9e/b0esc-astra/notice_probe.py /tmp/278ebc9e/b0esc-astra/base chain_removed\nTMPDIR=/tmp/278ebc9e/b0esc-astra python3 -B /tmp/278ebc9e/b0esc-astra/notice_probe.py /Users/edr/code/wt-278ebc9e-b0esc-astra chain_removed",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["chain_removed candidate_state ACCEPTED","subject Refused candidate payload kind unreadable"]},
      "expected":{"exit_code":0,"tail_regex":"subject Refused candidate payload kind unreadable"}
    }
  ],
  "flags": [
    {
      "id":"R1",
      "kind":"lead_ruling",
      "level":"blocking",
      "text":"Some legacy operations succeed without accessible authenticated kind evidence. Requiring fresh authentication there conflicts with universal parity.",
      "needs":"Authorize operation-specific legacy idle compatibility boundaries before implementation."
    }
  ]
}
```

# Astra 6

## Findings

**F1 — BLOCKER. Q1: The structural error is treating kind resolution as a harmless lookup.** It is actually a new validation procedure with additional reads, decoding rules, failure modes and precedence.

Three concrete manifestations:

- `sealed_candidate` now reads and classifies the wrapper before the clone-side registration/sidecar checks (`joulewise/evidence_night.py:249`, `:271`, `:283`). `sealed_state` checks source binding before the existing checkout check (`:689`, `:691`). Moving these checks changes which defect wins.
- Cleanup validates receipt bytes at `scripts/run_night.py:1379`, then reopens the receipt as text through `_custody_row` at `:1009`. **Executed:** with a non-UTF-8 wrapper, UTF-8/BOM/UTF-16 receipts all passed the real validator. Base repaired all three; head repaired only UTF-8. BOM/UTF-16 produced no outcome file and zero refusal-writing calls. Cleanup and refusal-writing dependencies were mocked; receipt validation was real.
- `candidate_state` performs a dictionary lookup before the historical ownership predicate (`joulewise/evidence_night.py:639`). **Executed:** list/object kinds produce base `Refused("candidate is not a completed, owned preparation")` but head `TypeError`.

The cure briefing itself needs correction. Moving authentication into every notice path does not preserve all base behavior. Base `notice_subject` only formats supplied fields (`2ea6a7ec:joulewise/evidence_night.py:296`); head authenticates filesystem evidence first (`joulewise/evidence_night.py:340`). **Executed:** an otherwise owned candidate with its wrapper removed passes `candidate_state` on both trees; base returns its notice subject, head refuses.

Thus “validate as base, then route” is necessary but incomplete: **base success does not always establish authenticated kind identity.** Uninstall, recovery and presentation have different prerequisites from arming.

**F2 — BLOCKER. Immutable rows do not authenticate the selector.** `_custody_row` returns the wrapper’s parsed kind without requiring a receipt, sidecar or bound source (`scripts/run_night.py:1019`, `:1027`). **Executed:** a bare declarationless wrapper selected calibration; a bare idle declaration selected idle. This establishes a resolver-level authority defect, not a demonstrated public cleanup bypass.

Parsing an identity claim and authenticating that claim must be separate concepts. A validated receipt’s schema is likewise not, by itself, proof of its provenance; callers must retain the existing custody/binding guarantees.

**F3 — should_fix. Each round optimizes against examples rather than an equivalence obligation.** `test_refusal_parity` covers three cases (`tests/test_night_kinds.py:389`); the unreadable-wrapper repair regression writes ordinary text and mocks receipt validation (`:332`, `:335`). Those tests cannot expose the encoding interaction.

Lenses can find counterexamples, inspect authority flow and justify local equivalence where control flow is preserved. They cannot establish arbitrary-program equivalence by inspection. **Neither can a finite corpus.** Execution provides a reproducible acceptance boundary; structural review explains why unenumerated inputs should behave consistently. Both are required.

**Q2 — Candidate structural cures**

| Cure | Cost | Guarantee and limitation |
|---|---|---|
| **(a) Differential parity harness** | Highest initial test investment; reusable thereafter | Exact observational equality for enumerated states and deterministic schedules. Generates counterexamples instead of relying on reviewer imagination. Does not prove all possible inputs. |
| **(b) Validate as base, then route** | Moderate refactor | Preserve each operation’s legacy validation sequence and failures; select a row from evidence that sequence already authenticates. Where base never authenticated kind, preserve legacy idle behavior explicitly. Adding fresh validation there requires a contract ruling. |
| **(c) Per-surface PRs** | More integration/review overhead; smaller individual diffs | Limits interactions and permits focused corpora. Split generator/notice rendering, sealed lifecycle, installer/gate, then driver/recovery/release. Run the cumulative cross-surface corpus at every merge; splitting alone supplies no parity guarantee. |
| **(d) Carry authenticated evidence forward once** | Moderate architectural work | Existing validators return an internal immutable context containing the selected row and its established bindings. Dispatch consumes that context instead of reopening files. Do not persist a new authoritative `kind` field. The context’s constructor and provenance matter more than its type annotation. |

My recommendation combines **(a), (b), and (d)**, delivered in **(c)** increments.

Preserve the legacy failure/recovery paths, including their order and side effects. Parameterize successful handlers with a row derived at the existing authentication boundary. Use the already validated C5 object for cleanup; do not reinterpret its bytes through another parser. Keep reporting independent of kind availability.

For an operation that historically works without authenticated identity, retain its explicit idle compatibility behavior. That is a fixed legacy operation, not an inferred identity capable of granting another handler, arming or successor release. If “every site dispatches” forbids even this boundary, the lead must narrow that requirement or relax universal parity. Another patch cannot reconcile contradictory obligations.

**Q3 — Proposed next-round brief, executable after lead adoption**

1. **Seat: independent parity-harness implementer.**

   `WRITE_SCOPE: ["tests/test_b0_differential_parity.py", "tests/b0_parity_support.py"]`

   No production changes. Pin oracle `2ea6a7ec`; exercise candidate `bee658c5` initially. Run revisions in separate processes with independently restored fixture state. Freeze clocks, randomness, timezone and external responses. Use identical logical fixture paths; narrowly document any unavoidable relocation handling. Never normalize refusal text, missing output, exception type or call order.

2. **Enumerate the following corpus.**

   - Valid idle seeds for prepare/resume, notices, wrapper generation, sealing, installer render/probe, C5/C3, reporting/courier, cleanup, uninstall/veto/verify and zero-capture release.
   - Plan/state/receipt values: missing, truncated, malformed JSON, scalar/list/object, missing fields, wrong types, unknown kinds and stale/mismatched identities.
   - Encodings: UTF-8, BOM, UTF-16 variants, invalid bytes and truncated multibyte sequences. Do not assume every format is valid; base decides.
   - Wrapper/sidecar/manifest/source: missing, directory, symlink, unreadable, changed digest, stale binding, stripped declaration, duplicate declaration, unknown kind and calibration co-export.
   - Clone/source: intact, dirty, moved, archived, absent, changed working bytes and changed pinned binding.
   - Receipt/cleanup: absent/invalid/valid, C5 PASS/FAIL/absent/None/conflicting kind; chain-started marker present/absent; outcome absent, malformed, complete, partial or refused; existing refusal and cleanup proven/unproven.
   - Enumerate every single mutation and all pairs of validation faults to expose precedence. Exhaustively cross wrapper readability × receipt encoding × C5 state × outcome state. Add fixed-seed multi-fault generation, shrinking, and scheduled evidence changes between reads.
   - Retain every witness from 29a/29b/47b/72b and this consult.

   Compare returned values; exception class/message and refusal code; stdout/stderr; created, changed and deleted file bytes/modes; and ordered observable dependency calls with arguments. Stub hazardous OS effects, **not** kind parsing, receipt validation or chain authentication.

3. **Harness gate before production work.**

   Base-versus-base must be identical. Base-versus-current-head must expose known regressions, including BOM/UTF-16 repair and notice-subject behavior. Publish case counts, seeds, coverage by operation and minimized counterexamples. Independently audit the harness.

4. **Seat: production refactor implementer, one surface at a time.**

   Initial slice:

   `WRITE_SCOPE: ["scripts/run_night.py", "tests/test_run_night.py"]`

   Implement driver reporting/recovery using the accepted operation boundaries and existing authenticated evidence. Harness files remain independently owned. Issue a fresh exact allowlist for each subsequent surface; no implicit scope expansion.

5. **Acceptance gate for B0.**

   Zero idle differential mismatches across the cumulative corpus; unchanged existing goldens; independent third-row/unknown-kind tests proving authenticated routing and typed refusal; mutations caught for premature kind reads, changed refusal precedence and unauthenticated selection. Run the brief’s focused suite and canonical discovery suite. Resolve or explicitly adjudicate baseline environment failures before claiming a green gate. Lead reviews the final exact diff and retains final verification.

## Residual risk

This consult executed focused fixture probes, not the full suite or hardware validation. Sealing-order evidence combines source inspection with report 72b; I did not rerun its clone-based sealer probe. No repository files changed. Scratch artifacts are under `/tmp/278ebc9e/b0esc-astra/`.