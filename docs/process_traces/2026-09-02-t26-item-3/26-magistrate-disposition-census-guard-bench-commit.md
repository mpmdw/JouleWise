# Magistrate disposition of the census-guard gate — the bench commit, 2026-09-02

This file records what the bench commit carrying it changes, per the
synthesis in file 25, and the executed evidence behind each change.

| Change | Source | Where |
| --- | --- | --- |
| Enumerated `indirect` block replaced by the generic identifier-field census (every str-valued field of every AST node; permitted mentions = the one `FunctionDef.name` + the `Name.id` of each counted direct call) | Fable ruling Q2 (file 23), ast-field shape | `tests/test_arm_readiness_evidence_t0.py::test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census` |
| Post-R1 count derived from DISTINCT direct-call nodes attributed to the innermost enclosing function (closure double count cured) | both seats (Fable M35, Opus 19/25) | same test |
| Docstring rewritten: pins provenance arithmetic; states the runtime-envelope forms it does not see; cites the 715 s correction and the two kernel rows; names the deliberate-only residual | Opus Q4 (file 24), Fable Q3 | same test |
| Kernel row `T0-PROBE-CENSUS-RESOURCE-01` (p3_hardening_candidates, agent lane, queued): census the resource (`_execute_probe` sites, `_boot_probe` outside the window, `_DERIVERS` injective, no loop ancestor) | Opus Q2 (iv)-(v), Fable M14/M34; NOT in-PR by ruling | `docs/process/state_kernel.json`, `TASK_QUEUE.md`, `tests/test_gen_state.py` (127 → 128) |
| The raw-text token-count whitelist | rejected by both seats | not installed |

## Executed evidence (bench, `/Users/edr/code/JouleWise-wt-t26-b`, this session, `TMPDIR` under the scratchpad)

```
$ python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census
Ran 1 test in 0.044s
OK
$ python3 <scratch>/probe-t26c.py    # guard re-implemented from the new test body; 27 in-memory mutants of joulewise/arm_readiness_evidence_t0.py; checkout untouched
base: SURVIVES
alias (Sol 256)                               KILLED stray=[('Name', 'id', 1834)]
globals literal                               KILLED stray=[('Constant', 'value', 1834)]
stored callback                               KILLED stray=[('Name', 'id', 1834)]
twelfth direct call                           KILLED post_r1=12
ImportFrom shadow after def (terra 257)       KILLED stray=[('alias', 'name', 498)]
import x as _fresh_probe                      KILLED stray=[('alias', 'asname', 498)]
local import-as in _derive_power              KILLED stray=[('alias', 'asname', 1834)]
class redefinition                            KILLED stray=[('ClassDef', 'name', 498)]
async def redefinition                        KILLED stray=[('AsyncFunctionDef', 'name', 498)]
parameter named _fresh_probe                  KILLED stray=[('arg', 'arg', 1834), ('Name', 'id', 1835)]
except as                                     KILLED stray=[('ExceptHandler', 'name', 1836)]
keyword arg                                   KILLED stray=[('keyword', 'arg', 1834)]
match capture                                 KILLED stray=[('MatchAs', 'name', 1835)]
escaped string constant                       KILLED stray=[('Constant', 'value', 1834)]
implicit concat constant                      KILLED stray=[('Constant', 'value', 1834)]
NFKC homoglyph ImportFrom                     KILLED stray=[('alias', 'name', 498)]
NFKC homoglyph alias+call                     KILLED stray=[('Name', 'id', 1834)]
decorator @_fresh_probe                       KILLED stray=[('Name', 'id', 498)]
nested redefinition                           KILLED defs=2
__all__ string                                KILLED stray=[('Constant', 'value', 498)]
M35b one closure site added                   KILLED post_r1=12
M35 two sites removed, one closure site       KILLED post_r1=10
module-level direct call                      KILLED post_r1=12
global rebinding                              KILLED stray=[('Global', 'names', 1834), ('Name', 'id', 1835)]
BENIGN docstring mention                      SURVIVES
BENIGN comment mention                        SURVIVES
computed name (residual)                      SURVIVES
$ python3 scripts/gen_state.py && python3 scripts/gen_state.py --check && echo CHECK-OK
CHECK-OK
$ python3 -m unittest tests.test_gen_state tests.test_docs_freshness
Ran 65 tests in 1.994s
OK
$ python3 -m unittest tests.test_arm_readiness_evidence_t0   # background, under the integration replay's load
Ran 66 tests in 201.327s

OK (skipped=7)
rc=0
```
