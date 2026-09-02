# File 27 — luna 261 (xhigh, read-only) operation-loop §5 fresh pass over the census-guard bench commit `47eb43d7..1e00e9ce`, 2026-09-02

Custodied verbatim from `<scratchpad>/out/261-luna-t26-fresh27.md` (scratchpad paths redacted). Brief: `<scratchpad>/t26-fresh-pass-27.md` (D1–D5; reproduced below the report).

---

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Fresh diff-only review complete: focused checks pass; one trace path-hygiene issue and one docstring wording nit remain.",
  "workspace": {
    "base_requested": "47eb43d7..1e00e9ce",
    "base_mode": "exact",
    "head_start": "47eb43d7359a706b87f8a4e9a63e81bee80096c5",
    "head_end": "1e00e9ce7105c6696f5063663a9a03675cc659f2",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 1,
      "nit": 1
    },
    "findings": [
      {
        "id": "D5-PATH-01",
        "severity": "should_fix",
        "title": "New trace files embed host-specific checkout and home paths."
      },
      {
        "id": "D2-DOC-01",
        "severity": "nit",
        "title": "The docstring overstates that docstrings may name _fresh_probe freely."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/joulewise-t26-review.N784Yp python3 -m unittest tests.test_arm_readiness_evidence_t0",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 66 tests in 203.271s",
          "",
          "OK (skipped=7)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 66 tests in [0-9.]+s\\n\\nOK \\(skipped=7\\)"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/joulewise-t26-review.N784Yp python3 -m unittest tests.test_gen_state tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 65 tests in 1.959s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 65 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/joulewise-t26-review.N784Yp python3 -m unittest tests.test_arm_readiness_evidence_t0 tests.test_gen_state tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 131 tests in 206.799s",
          "",
          "OK (skipped=7)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 131 tests in [0-9.]+s\\n\\nOK \\(skipped=7\\)"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "TMPDIR=/private/tmp/joulewise-t26-review.N784Yp python3 scripts/gen_state.py --check && echo CHECK-OK",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CHECK-OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^CHECK-OK$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check 47eb43d7 1e00e9ce",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The six runtime-envelope mutation forms remain outside this static census; T0-LIVENESS-BOUND-EMPIRICAL-01 remains the empirical closure route.",
      "needs": "Lead should retain the documented residual and close the empirical row before relying on the 600 s envelope."
    }
  ]
}
```

## Findings

- D5-PATH-01 — should-fix. New trace files expose `~/.claude/CLAUDE.md`, `CLAUDE.local.md`, and `/Users/edr/code/JouleWise-wt-t26-b` in [trace 24](/Users/edr/code/JouleWise-wt-t26-b2/docs/process_traces/2026-09-02-t26-item-3/24-coldgate-opus-refutation-census-guard.md:7), [trace 25](/Users/edr/code/JouleWise-wt-t26-b2/docs/process_traces/2026-09-02-t26-item-3/25-magistrate-synthesis-census-guard-gate.md:126), and [trace 26](/Users/edr/code/JouleWise-wt-t26-b2/docs/process_traces/2026-09-02-t26-item-3/26-magistrate-disposition-census-guard-bench-commit.md:14). These are host-specific and the absolute checkout path is not this checkout.

- D2-DOC-01 — nit. The sentence at [test line 890](/Users/edr/code/JouleWise-wt-t26-b2/tests/test_arm_readiness_evidence_t0.py:890) says docstrings “are not AST fields and may name the helper freely.” Normal prose docstrings survive, as required, but an exact docstring value `_fresh_probe` is parsed as `Constant.value` and is killed. The wording is technically overbroad but has no runtime impact.

## D1 — independent in-memory census table

The unmutated source survived with `post_r1=11`. No checkout file was modified.

| Form | Result | Observed |
|---|---|---|
| (a) `from x import _fresh_probe` | KILLED | `stray=[('alias','name',498)]` |
| (b) `import x as _fresh_probe` | KILLED | `stray=[('alias','asname',498)]` |
| (c) `p = _fresh_probe; p(...)` | KILLED | `stray=[('Name','id',1834)]` |
| (d) one closure call in `_derive_power` | KILLED | `post_r1=12` from 13 direct nodes, not 13 |
| (e) two direct sites deleted plus closure | KILLED | `post_r1=10` |
| (f) keyword `_fresh_probe=` | KILLED | `stray=[('keyword','arg',1834)]` |
| (g) decorator `@_fresh_probe` | KILLED | `stray=[('Name','id',498)]` |
| (h) valid NFKC identifier `_ｆｒｅｓｈ_ｐｒｏｂｅ` | KILLED | parser normalizes to `_fresh_probe`; `stray=[('Name','id',1834)]` |
| (i) implicit concat `"_fresh_" "probe"` | KILLED | `stray=[('Constant','value',1834)]` |
| (j) `global _fresh_probe` | KILLED | `stray=[('Global','names',1834)]` |
| (k) prose docstring mentioning `_fresh_probe` | SURVIVES | `post_r1=11` |
| (l) `# _fresh_probe` comment | SURVIVES | `post_r1=11` |
| (m1) loop around a post-R1 site | SURVIVES | `post_r1=11` |
| (m2) second `_DERIVERS` row | SURVIVES | `post_r1=11` |
| (m3) `_boot_probe` moved above `validity_origin` | SURVIVES | `post_r1=11` |
| (m4) `_time.sleep(30)` in `_fresh_probe` | SURVIVES | `post_r1=11` |
| (m5) retry loop in `_fresh_probe` | SURVIVES | `post_r1=11` |
| (m6) wait added in `arm_readiness.py` | SURVIVES | censused source unchanged; `post_r1=11` |
| Own: `context._fresh_probe` attribute lookup | KILLED | `stray=[('Attribute','attr',1834)]` |
| Own: nested `class _fresh_probe` | KILLED | `stray=[('ClassDef','name',1834)]` |
| Own: computed-name call | SURVIVES | `post_r1=11`, as documented |
| Own: timeout changed 45→44 | KILLED | timeout assertion fails; arithmetic becomes `589 != 600` |

The exact spelling `＿fresh＿probe` from the prompt is rejected by this Python parser as invalid U+FF3F; it is not normalized. The valid NFKC letter-homoglyph form above is caught.

## D2 — docstring sentence table

| # | Sentence | Grade |
|---:|---|---|
| 1 | “The ruled 600 s = (post-R1 ``_fresh_probe`` sites) × 45 s + 105 s.” | PROVEN |
| 2 | “What this test pins: the PROVENANCE ARITHMETIC of cold gate T26 item 3, which states the constant as eleven governed post-R1 probe sites times ``_PROBE_TIMEOUT_SECONDS`` plus 105 s of ungoverned work.” | PROVEN |
| 3 | “Each factor is read from the code (the sites by an AST census of direct ``_fresh_probe`` calls, the timeout from the module constant), so an edit to either factor fails here while the constant stays 600 s.” | PROVEN; the timeout mutant failed |
| 4 | “The one site inside ``_fresh_clock_reference_batch`` IS R1 and is excluded.” | PROVEN |
| 5 | “What this test does NOT protect: the runtime R1→stamp envelope.” | PROVEN |
| 6 | “A static census counts sites, not seconds — a loop around a site, a deriver registered for a second row, a direct ``_execute_probe`` caller such as ``_boot_probe`` moved above the ``validity_origin`` stamp, a retry inside ``_fresh_probe``, or a wait in another module all change the envelope while this test stays green.” | PROVEN |
| 7 | “The ruling's 2026-09-02 correction already records the fixed subtotal as 715 s (495 s probes + 220 s git ceilings) against the ruled 600 s; the runtime interval is unmeasured and is carried by kernel row ``T0-LIVENESS-BOUND-EMPIRICAL-01`` (the census-the-resource hardening is ``T0-PROBE-CENSUS-RESOURCE-01``).” | PROVEN |
| 8 | “Completeness of the census: direct calls must be the ONLY way the module reaches ``_fresh_probe``.” | PROVEN for AST-visible literal references; computed-name exceptions are explicitly disclosed |
| 9 | “Rather than enumerating reference forms (two rounds showed the enumeration is never complete — Sol 256 F1, terra 257 F1; cold gate files 22–25), every string-valued field of every AST node is censused: the identifier may appear only as the single ``FunctionDef.name`` and as the ``Name.id`` of a counted direct call.” | PROVEN |
| 10 | “Aliases, stored callbacks, attribute lookups, string constants (including escaped or implicitly concatenated spellings and NFKC-normalised homoglyphs, which the parser folds), import shadows, ``as``-bindings, class/async redefinitions, parameter, keyword, ``except … as`` and ``match`` captures all fail.” | PROVEN for the exercised forms and generic field census |
| 11 | “Comments and docstrings are not AST fields and may name the helper freely.” | OVERCLAIMED technically; ordinary prose mentions survive, but an exact-only docstring is an AST `Constant` and is killed |
| 12 | “Deliberately constructed names (``"_fresh_" + "probe"``, ``importlib`` lookups, star-import rebinding) are invisible to any static check and are not guarded (D-161: deliberate-only, no mistake reaches them).” | PROVEN |
| 13 | “Sites are counted as DISTINCT call nodes, attributed to the innermost enclosing function, so a call inside a nested closure is counted once.” | PROVEN by the 12-site closure mutant |
| 14 | “The equality with ``_MIN_IDLE_NS`` that the ruling noted is a coincidence of two unrelated quantities (anchor span floor, idle capture floor) and is deliberately not pinned.” | PROVEN; no such equality is asserted |

The docstring names both residual classes in substance: deliberate name construction and ordinary runtime-envelope changes. It names both kernel rows. It no longer contains the retracted claim that a twelfth site fails instead of silently changing the governed envelope.

## D3 — kernel row and factual anchors

| Anchor | Row text | Code verification | Result |
|---|---|---|---|
| `_execute_probe` resource | Exactly two direct call sites inside `_fresh_probe` and `_boot_probe` | `grep` found calls at lines 493 and 501; line 427 is only the definition | PASS |
| `_boot_probe` placement | Both author calls outside R1→stamp | Calls at 2284 and 2359; `validity_origin` is line 2325. The first is pre-R1; the second is post-stamp | PASS |
| `_DERIVERS` injectivity | No deriver registered for a second row | 15 rows, 15 unique values, `injective=True` | PASS |
| Loop ancestry | No post-R1 site has a loop ancestor | All 11 post-R1 sites have no `For`, `While`, or comprehension ancestor; the R1 site at 1101 is inside the excluded batch loop | PASS |
| Supersession | Empirical row supersedes static hardening | Kernel fallback says the census row is superseded once `T0-LIVENESS-BOUND-EMPIRICAL-01` closes with retained receipts carrying both stamps | PASS |

The kernel row text matches file 25 §“New kernel row” in substance. `TASK_QUEUE.md` carries the generated projection, and `tests/test_gen_state.py` updates the expected ID set and count from 127 to 128.

## D4 — exact verification tails

The requested combined command:

```text
Ran 131 tests in 206.799s

OK (skipped=7)
```

Standalone T0 module:

```text
Ran 66 tests in 203.271s

OK (skipped=7)
```

State/docs pair:

```text
Ran 65 tests in 1.959s

OK
```

Generator check:

```text
CHECK-OK
```

## Residual risk

The static census does not establish elapsed runtime. All six requested runtime-envelope forms survived, as the docstring claims. The empirical row remains the authoritative closure route for the 600-second liveness question.

## What this pass did NOT check

- The canonical `unittest discover` suite, per instruction.
- The rest of the branch or unrelated historical commits.
- Live hardware timing or real T-0 rehearsals.
- Runtime execution of mutated production modules; mutations were AST/source-text experiments only.
- Any writes, merges, commits, or changes under the checkout.

---

## Brief (verbatim)

WRITE_SCOPE: []
ORIGIN: claude-magistrate  HOP: 1  GENRE: review  READ-ONLY (workspace-write with an empty write scope: write NOTHING under the checkout; use only $TMPDIR)

# Operation-loop §5 fresh pass over ONE bench commit — the `_fresh_probe` census-guard cure (`47eb43d7..1e00e9ce`)

Checkout: `/Users/edr/code/JouleWise-wt-t26-b2`, detached at `1e00e9ce`. Review ONLY `git diff 47eb43d7 1e00e9ce` (4 tracked files + 3 new trace files). You have not seen this item; do not re-audit the rest of the branch — the earlier passes own it.

What the commit claims (verify, don't trust): the test
`tests/test_arm_readiness_evidence_t0.py::…::test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census`
was rewritten after a cold gate (read `docs/process_traces/2026-09-02-t26-item-3/25-magistrate-synthesis-census-guard-gate.md` for the ruling and `26-…bench-commit.md` for the magistrate's executed mutant table). It now (1) censuses every str-valued field of every AST node in `joulewise/arm_readiness_evidence_t0.py` for the literal `_fresh_probe`, permitting only the one `FunctionDef.name` and the `Name.id` of direct `Call.func` nodes; (2) counts post-R1 sites as `len(direct_call_names) - 1` (distinct nodes, not a per-function sum); (3) claims in its docstring to pin the ruling's PROVENANCE ARITHMETIC only (11 × 45 s + 105 s), naming two residual classes it does NOT guard.

## Questions (executed evidence for each; in-memory mutation of the SOURCE TEXT the test parses — never write under the checkout)

D1. Build your OWN mutant table by re-implementing the test's census on a mutated copy of the module text (read `t0.__file__`, mutate the string, `ast.parse`, run the same logic). Required forms, each reported KILLED/SURVIVES with the stray tuple or count observed: (a) `from x import _fresh_probe` after the def; (b) `import x as _fresh_probe`; (c) alias `p = _fresh_probe; p(...)` added inside a post-R1 function; (d) a closure inside `_derive_power` that calls `_fresh_probe` once (the M35 double-count form — the count must be 12, not 13); (e) two direct sites deleted + one closure site added (must be 10); (f) a keyword named `_fresh_probe=`; (g) a decorator `@_fresh_probe`; (h) NFKC homoglyph identifier (e.g. fullwidth `＿fresh＿probe` — Python normalises it to ASCII at parse time); (i) an implicit-concat string `"_fresh_" "probe"`; (j) a `Global` statement `global _fresh_probe`; (k) BENIGN: a docstring mentioning `_fresh_probe` — must SURVIVE; (l) BENIGN: a `# _fresh_probe` comment — must SURVIVE; (m) six RUNTIME-ENVELOPE forms the docstring says are NOT guarded — confirm each SURVIVES, as the docstring claims, and say whether the docstring names its class: a `for` loop wrapped around an existing post-R1 site; a second row appended to `_DERIVERS` pointing at an existing deriver; `_boot_probe` (a direct `_execute_probe` caller) moved above the `validity_origin` stamp; a `time.sleep(30)` inserted into `_fresh_probe`'s body; a retry loop inside `_fresh_probe`; a wait added in `joulewise/arm_readiness.py` (outside the censused file). Any form in (a)–(j) that SURVIVES, or in (k)–(l) that is KILLED, is a finding. Add at least two forms of your own.
D2. Docstring vs behaviour: quote every sentence of the new docstring and mark each as PROVEN by D1, OVERCLAIMED, or UNDERCLAIMED. Does the docstring name both residual classes (deliberate name construction; ordinary-maintenance runtime-envelope changes) and the kernel row that carries the second? Does it still make the retracted claim that a twelfth site "fails here instead of silently changing the governed envelope"?
D3. Kernel row `T0-PROBE-CENSUS-RESOURCE-01` in `docs/process/state_kernel.json` (+ `TASK_QUEUE.md`, `tests/test_gen_state.py`): does its text match what file 25 §"New kernel row" ruled (census `_execute_probe`'s two direct callers, both `_boot_probe` calls outside the R1→stamp window, `_DERIVERS` injective, no loop ancestor on a governed site; stop card = the empirical row supersedes)? Verify the four factual anchors in the row against the code: `_execute_probe` callers (`grep -n "_execute_probe(" joulewise/arm_readiness_evidence_t0.py`), `_boot_probe` call lines vs the `validity_origin` line, `_DERIVERS` row count. Any anchor that is wrong in the row is a finding.
D4. Run `python3 -m unittest tests.test_arm_readiness_evidence_t0 tests.test_gen_state tests.test_docs_freshness` and `python3 scripts/gen_state.py --check`, `TMPDIR` under your scratch dir; report exact tails (expected 66 OK skipped=7 for the first module; 65 OK for the pair; CHECK-OK).
D5. Anything in the diff outside the four claims above (an unrelated edit, a leaked path, a volatile literal in a README-facing surface)?

Do NOT run `python3 -m unittest discover`. Do not read files outside the checkout.

## Report

`claude-codex-report/v1` envelope, genre review; `verdict` = `{counts, findings}` ONLY (ids, severity, title — JSON block under 8 KB). Markdown body: the D1 table, D2 sentence table, D3 anchor table, D4 tails, residual risk, "what this pass did NOT check". Grade honestly; do not lower a severity to avoid a fix round.
