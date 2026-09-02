```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"Draft matches most executable behavior, but cannot yet be rebuilt from text alone and has two unpinned test-map claims.",
  "workspace":{"base_requested":"a37b0b9f","base_mode":"exact","head_start":"a37b0b9f72928e345739c8ef88a28b4198dd1133","head_end":"a37b0b9f72928e345739c8ef88a28b4198dd1133","upstream_end":null,"branch":null},
  "pathspec":[],
  "unowned_dirty":["docs/contracts/identity_pin_projection.md"],
  "verdict":{"findings":[
    {"id":"P1","severity":"blocker","doc_line":61,"title":"The initial projection envelope is absent"},
    {"id":"F1","severity":"blocker","doc_line":179,"title":"Scientific-tag normalization is not reproducible exactly"},
    {"id":"P2","severity":"should_fix","doc_line":390,"title":"Worked example omits required hash preimages and rule coverage"},
    {"id":"T1","severity":"should_fix","doc_line":507,"title":"Named freeze test has no biting sidecar-binding assertion"},
    {"id":"T2","severity":"should_fix","doc_line":523,"title":"Launch non-rederivation clause has no biting test"}
  ]},
  "verification":[
    {"id":"V1","kind":"inspection","cmd":"git rev-parse HEAD && git status --short --branch","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["a37b0b9f72928e345739c8ef88a28b4198dd1133","?? docs/contracts/identity_pin_projection.md"]},"expected":{"exit_code":0,"tail_regex":"a37b0b9f.*identity_pin_projection\\.md"}},
    {"id":"V2","kind":"other","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -c 'import hashlib,json; from pathlib import Path; line=Path(\"docs/contracts/identity_pin_projection.md\").read_text().splitlines()[410]; checks=[(hashlib.sha256(b\"joulewise.prompt_token_ids.v1\"+bytes([0])+json.dumps([11,22,33,44],separators=(\",\",\":\")).encode()).hexdigest(),\"10e6c1854858d7cdd278400c11706ebd2a43fe79ffa241bd5c1d0f6fe665a9fe\"),(hashlib.sha256(b\"TOY\"+bytes([10])).hexdigest(),\"6361d8e661d28948e82e68ed04a7d5becdc39bc6a94176bd805003b90991fdfb\"),(hashlib.sha256(line.encode()).hexdigest(),\"6d3a16628cdda16cfd1b0bc3fba680b600e5e25e15f606986aa9ed92967fd1cd\")]; assert all(a==b for a,b in checks); print(\"example token/model/projection hashes: PASS\")'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["example token/model/projection hashes: PASS"]},"expected":{"exit_code":0,"tail_regex":"^example token/model/projection hashes: PASS$"}}],
  "flags":[
    {"id":"ENV1","kind":"environment","level":"nonblocking","text":"The requested joulewise/mlx_runtime.py and joulewise/launch_window.py do not exist; review used the draft's actual paths, joulewise/adapters/mlx_runtime.py and scripts/launch_window.py.","needs":""},
    {"id":"VG1","kind":"verification_gap","level":"nonblocking","text":"Full test suite intentionally not run per instruction; mapped assertions were inspected only.","needs":""}
  ]
}
```

## Findings

### Lens 1 — pedagogy

PASS summary: the remaining defined vocabulary concepts and table-defined JSON literals are introduced at use. Mechanical first-use failures:

| Line | Term(s) | Verdict | First text / defect |
|---:|---|---|---|
| 1 | identity-pin projection; receipt | FAILS | “Identity-pin projection receipt contract” — meanings arrive at lines 9 and 23. |
| 10 | tokenizer behavior; runtime behavior | FAILS | “model bytes, tokenizer behavior, runtime behavior” — operational meanings arrive later. |
| 19 | governed floor artifact | FAILS | “issues the governed floor artifact” — never explains what that artifact is. |
| 21 | `unprojected`; write-fixed | FAILS | “changing the pack from unprojected to write-fixed” — neither state is defined here. |
| 23 | hash-authenticated | FAILS | “a hash-authenticated receipt” — authentication mechanics arrive only with sidecars at line 87. |
| 35 | lexically sorted | FAILS | “lexically sorted list” — no ordering rule in plain words. |
| 38–40 | followed-byte digest; symbolic link | FAILS | “followed-byte digest… symbolic link” — target-following semantics arrive later and are never plain-glossed. |
| 41–44 | prepare/probe/cleanup; measured member | FAILS | “one prepare/probe/cleanup use” — the three operations and excluded collection action are not built. |
| 46 | run-instance IDs; calibration bookkeeping tags | FAILS | “removed” tags are neither identified nor explained. |
| 77 | floor mint | FAILS | “same functions used by the floor mint” — this named mechanism remains undefined. |
| 104 | `model_artifact_identity` | FAILS | “described below” defers the exact result shape to lines 107–119. |
| 111 | lexical model-root-relative POSIX path | FAILS | Its path basis and POSIX meaning are not glossed. |
| 129 | dataclass mapping | FAILS | “complete dataclass mapping” assumes an implementation construct without explanation. |
| 141 | conditional prompt realization | FAILS | The condition arrives only on line 142. |
| 164, 168 | ruling 44c/150a R-150-4; governed observation | FAILS | Both carry mechanism/policy weight without an in-document meaning. |
| 179–182 | replacement/calibration tags | FAILS | “removing replacement, calibration-collection…” does not give the exact match rules; see F1. |
| 185 | `STACK_IDENTITY_FIELDS` | FAILS | “the eleven fields listed by…” points outside the document rather than listing them. |
| 195 | `TypeError` | FAILS | The fallback depends on it, but it is not glossed as the tokenizer API’s keyword-rejection signal. |
| 256 | path-safe session ID | FAILS | “requires a path-safe session ID” gives no permitted/forbidden form. |
| 258 | committed successor | FAILS | The successor search/meaning is not built before use. |
| 290 | U8; U11 | FAILS | “U8 arm mapper… U11 projection evidence” are unexplained subsystem labels. |
| 301 | `execve` | FAILS | “before `execve`” is an unexplained launch boundary. |
| 310 | D-119 conservative-language rule | FAILS | Policy is invoked without stating the operative rule. |

| ID | Severity | Doc line | Code / test | Defect and proposed fix |
|---|---|---:|---|---|
| P1 | blocker | 61, 93 | `joulewise/identity_pins.py:79-96,474-548` | “Freeze means the sole `unprojected` to `frozen` transition…” and “`_derive_projection_units` walks `projection.identity_units`…” never specify the initial eight-key `identity_pin_projection` envelope, its `mode`, `required_before_arm`, null pins/receipt, or supersession shape. Add the full unprojected schema and a minimal valid JSON example before section 3. |
| F1 | blocker | 179–182 | `joulewise/identity_pins.py:217-243` | “removing replacement, calibration-collection, and `rep[0-9]+` tags” is broader than executable matching: code removes only `analysis-replacement-of=`, `analysis-replacement-reason=`, four exact calibration prefixes, and full-match `rep[0-9]+`. State these exact predicates and that other `run_metadata` keys are discarded when tags are normalized. |
| P2 | should_fix | 390–419 | `joulewise/identity_pins.py:217-243,255-345` | “Their raw-byte digests are respectively…” and “They normalize to one scientific-config digest” give no raw config bytes, normalized JSON, or 11-field stack preimage. Token/model/projection-input/runtime hashes recompute correctly; the two config-byte hashes and `config_set_sha256` do not. Include both raw configs, normalized identity JSON, and stack JSON; add one non-happy path for a config/model/runtime rule. |
| T1 | should_fix | 507 | `tests/test_identity_pins.py:552-574` | “Exact receipt, sidecar binding…” is mapped to a test that never reads, tampers with, or asserts the `.sha256` sidecar. Add an explicit sidecar-byte assertion plus a mutated/missing-sidecar refusal assertion. |
| T2 | should_fix | 523 | `scripts/launch_window.py:102-167,239-264` | “Launch does not re-derive after arm \| No test…” is executablely true: launch only authenticates/replays inputs, consumes, verifies consumption, and `execve`s. Add a launch-window test that makes projection/runtime/tokenizer rederivation fail if called. |

Worked-hash result: `[11,22,33,44]`, `[11,22,33,45]`, `TOY\n`, the line-411 projection input, and the reconstructed 11-field stack all match the published hashes, including runtime identity `e2dc…c4e36`.

### Lens 2 — fidelity

The normative schema, seven hash-input fields, canonical serialization, prompt realization checks/IDs, five-code vocabulary, freeze/arm lifecycle, and launch residual-risk statement otherwise agree with code: `identity_pins.py:1256-1696,1819-2234`; `adapters/mlx_runtime.py:315-349,940-946,1109-1114`; `arm_readiness.py:5681-5729`; `scripts/launch_window.py:102-167,239-264`.

Clause-to-test audit: 17 of 19 map entries have biting assertions. Direct assertions are at `test_identity_pins.py:469,474;493-501;586-602;729-740;1203-1218;1237-1242;1261-1270;1325-1331;1348-1352,1377-1380;1401-1421;1442-1447,1499-1507;1561-1569;1618-1634;1649,1657,1671,1694-1700;1703-1714,1722-1726`, and `test_arm_readiness_integration.py:411-423,589-639`. The two exceptions are T1 and T2.

First place a rebuilder gets stuck: creating the initial unprojected pack attachment before calling `freeze_projection`; the receipt schema is documented, but the required projection envelope is not.

Pedagogy verdict: BLOCKER — not independently rebuildable yet.

Fidelity verdict: FINDINGS — implementation agreement is strong, but exact config normalization and two claimed test bindings need repair.

## Residual risk

No live adapter, hardware, or physical-energy validation was run; this was a static/code-and-hash review as instructed.