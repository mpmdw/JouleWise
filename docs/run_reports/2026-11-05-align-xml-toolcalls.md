# ALIGN Qwen3.5/3.8 XML tool calls — 2026-11-05

Branch: `lane/2026-11-05-align-xml-toolcalls`.
Base: `origin/lane/2026-11-05-align-pilot9-benign`,
`c9a0a39437614176bf4e14ff1565a6e4537328fb`.
Implementation commits:

- `d64149f84` — `ALIGN: parse Qwen3.5 and Qwen3.8 XML tool calls by model family`.
- `b492c8164` — `ALIGN: preserve XML parameter order for prompt-cache reuse`.

This report is a separate local documentation commit. Nothing was pushed.

## Scope and authority

The owner's brief selects this bounded AGENT task and overrides the usual
coordination-state and full-suite requirements. Read the repository instructions,
M0, stop card (NONE), restart/queue sections, ALIGN interface/workload/cache code,
and relevant dependency/evidence conventions. No kernel tasks were registered.
`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and
`tests/test_gen_state.py` were not edited. No network, analysis pipeline,
external measurement-file reads, hardware generation, or quiet-window collection
was used. Validation used repository source/configs, tracked test fixtures, and
temporary synthetic runs. Process deviations are disclosed below.

## Implementation and files

- `joulewise/align/apple/xml_tool_calls.py`: stdlib-only pseudo-XML grammar and
  schema-directed argument decoding. This syntax is not standards-compliant XML:
  tag names use `=` and string values are unescaped.
- `joulewise/align/apple/endpoint.py`: explicit `config.model.family` dispatch,
  including the token-limit parsing path; XML-specific assistant history
  rendering and reasoning separation.
- `tests/align/test_xml_tool_calls.py`: 16 unittest tests covering strict refusal,
  schema types, family dispatch, reasoning, the actual template, history,
  prefix/cache behavior, and frozen JSON behavior.
- `tests/align/fixtures/qwen38_chat_template.jinja` and its
  `.provenance.json`: exact supplied template and provenance.
- `tests/align/fixtures/json_tool_calls_c9a0a3943.json`: 14 frozen legacy parsing
  cases, including emitted-byte-derived call IDs and flags.
- `tests/align/fixtures/json_endpoint_c9a0a3943.json`: original template arguments
  and three complete synthetic mock endpoint results, frozen by loading
  `endpoint.py` directly from the base Git object.
- This report.

XML selection uses exact HF-style family spellings: `qwen3_5`, `qwen3_5_moe`,
`qwen3_5_text`, `qwen3_5_moe_text`, and corresponding `qwen3_8` spellings.
The supplied Qwen3.8 configuration actually declares `model_type=qwen3_5`
(`text_config.model_type=qwen3_5_text`); use that configured family for this
artifact. Neither model name nor emitted syntax enables XML. `qwen3_moe`
(Qwen3-30B) and `qwen3_next` retain the JSON path.

The parser accepts sibling tool calls with optional natural-language text before
them. It refuses malformed/unclosed/nested control tags, multiple functions
inside one envelope, suffix prose, unknown functions, undeclared or duplicate
parameters, missing required arguments, and invalid types. Any invalid call
invalidates all actions in the turn; original visible text remains available and
`malformed_tool_call:xml:...` records the refusal. Other recognized foreign
tool-like syntax receives `unsupported_tool_call_format`.

The template puts one LF before and after every argument. The parser removes
those framing LFs only. String arguments retain whitespace, Unicode, quotes,
JSON-looking text, entities, and ordinary markup literally. Non-string values
use strict JSON decoding, including arrays, objects, numbers, booleans, and null.
Duplicate JSON object keys and non-finite numeric values are refused. Type
checking includes nested objects/arrays, required properties, enums/constants,
unions, and local `$ref` definitions; booleans cannot stand in for integers.
XML argument mappings retain emitted parameter order so re-rendering does not
introduce a parameter-order rewrite. A nonalphabetical two-parameter cache
regression verifies this independently of the compact-formatting probe.
This is wire type/shape validation, not a complete JSON Schema validator:
patterns, ranges, and similar semantic constraints remain the tool's job.
Undeclared top-level parameter names are conservatively refused even if a
schema permits additional properties.

Two unavoidable wire ambiguities are handled conservatively: a string-or-null
parameter containing `null` cannot distinguish the string from JSON null, and
unescaped literal tool/function/parameter control tags cannot distinguish values
from nested calls. Such cases are refused rather than guessed. Reasoning tags
inside string parameters survive parsing; tool syntax inside an explicitly open
reasoning span never executes.

XML history rendering converts arguments to mappings, which this template's
`arguments|items` loop requires, and passes earlier reasoning through
`reasoning_content`. It supports both workload.py's raw assistant records and
structured calls without rendering an action twice. Prefilled reasoning openers
and thoughts quoting tool syntax are covered. No workload/cache policy or pilot
configuration was changed.

The legacy JSON parser still checks a nonempty function name, preserves supplied
argument JSON strings, canonicalizes argument objects, and derives IDs from
emitted bytes and ordinal. It does not gain XML schema validation. Golden tests
compare exact serialized output bytes for both JSON families, including raw
usage, flags, call IDs, and tokenizer arguments. These are bounded regression
evidence, not a proof over every possible completion.

## Real template provenance and round trip

Source repository: `mlx-community/Qwen3.8-27B-8bit`; supplied revision: **main**
(mutable; no resolved commit was supplied). SHA-256 of the exact template:
`c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041`.
The fixture is copied byte for byte from `.hf-qwen38/chat_template.jinja`.

The real Jinja template rendered an assistant turn with three calls:
`update`, `end_task`, `update`. Parsing returned identical function names,
argument values/types, and order, including multiline/Unicode strings, empty
strings, integers, floats, booleans, arrays, objects, and null. The template does
not serialize call IDs; emitted-byte-derived IDs are generated on parsing.

The measurement Mac pins **815b83c0**. **This fixture has not been verified
against that revision.** Verify the pinned template and digest there before
measurement. No separate Qwen3.5 MoE template was supplied; its compatibility
here is based on the stated shared protocol, not a separate template or model
execution test.

## Thinking controls and prefix measurements

The supplied template behaves as follows:

| Keyword | Behavior |
|---|---|
| `enable_thinking` absent/true | Uses reasoning effort and prefills `<think>\n`. |
| `reasoning_effort` absent | Defaults to `xhigh`, inserting the longer reasoning instruction in the system message. |
| `reasoning_effort=low` | Inserts the brief-thinking instruction. |
| `reasoning_effort=medium` | Inserts no reasoning-effort instruction; still opens thinking. |
| Other effort values while thinking | Raises a template error, including `high` and null. |
| `enable_thinking=false` | Omits the effort instruction/validation and prefills an empty closed think block. It does not by itself erase historical reasoning. |
| `preserve_thinking` absent/true | Preserves earlier assistant reasoning. |
| `preserve_thinking=false` | Removes reasoning and its wrapper from assistants before the latest real user query; retains reasoning in the current tool chain. |

The ALIGN endpoint currently forwards `EpisodeSpec.enable_thinking` directly
to `apply_chat_template`. There is no general `chat_template_kwargs` EpisodeSpec
field, and this change adds no `reasoning_effort` or `preserve_thinking` controls;
those use template defaults. Keep settings fixed within an episode.

Measured the longest common UTF-8 byte prefix (LCP) over five transitions in
synthetic six-assistant-turn conversations. `old_bytes - LCP` is the old suffix
invalidated by the next rendering, not a model-token count:

| Probe | Old bytes at transitions to turns 2–6 | LCP bytes | Invalidated old suffix bytes |
|---|---|---|---|
| Six user-query turns, default/true preservation | 1906, 2010, 2114, 2218, 2322 | Same as old bytes | 0, 0, 0, 0, 0 |
| Six user-query turns, preservation false | 1906, 1983, 2060, 2137, 2214 | 1860, 1937, 2014, 2091, 2168 | 46, 46, 46, 46, 46 |
| One query and six tool-call turns, any preservation setting | 1988, 2207, 2426, 2645, 2864 | Same as old bytes | 0, 0, 0, 0, 0 |
| Actual endpoint: previous prompt + canonical emitted call + EOS, default preservation | 1987, 2206, 2425, 2644, 2863 | Same as old bytes | 0, 0, 0, 0, 0 |
| Actual endpoint: previous prompt + compact emitted call + EOS, default preservation | 1981, 2200, 2419, 2638, 2857 | 1898, 2117, 2336, 2555, 2774 | 83, 83, 83, 83, 83 |

Thus message rendering is append-only under default preservation in these
fixtures. Turning preservation off rewrites earlier dialogue when a new real
query arrives. Native cache reuse also depends on emitted formatting: converting
compact calls back through the multiline template rewrites the action suffix
even with default preservation. Whitespace normalization can likewise matter.
The existing `EpisodePromptCache` compares actual token IDs, trims to their
common prefix when supported, and rebuilds the entire cache on an untrimmable
rewrite. It was not changed. Neither these byte probes nor synthetic cache tests
establish pinned-tokenizer counts, native hybrid-cache behavior, or hardware
validation. Reproduce the probes with `synthetic_prefix_probe` and
`synthetic_endpoint_cache_probe` in the new test module.

## Verification

Final relevant runs (all unittest; no full suite):

| Command | Result |
|---|---|
| `python3 -B -m unittest tests.align.test_xml_tool_calls` | Python 3.14.6, installed Jinja2: 16 passed, no skips (0.046 s). |
| `python3.13 -B -m unittest tests.align.test_xml_tool_calls` | 16 run: 10 passed, six real-template tests skipped because that interpreter lacks optional Jinja2 (0.013 s). |
| `python3.13 -B -m unittest tests.align.test_apple_endpoint` | 9 passed (24.459 s). |
| `python3.13 -B -m unittest tests.align.test_pilot3_cache` | 12 passed (1.467 s). |
| Guarded Python 3.13 unittest invocation for `tests.align.test_pilot4` (below) | 18 run: 17 passed, one external-cache test explicitly unavailable/skipped (35.291 s). |
| `python3.13 -B -m compileall -q joulewise/align/apple/endpoint.py joulewise/align/apple/xml_tool_calls.py tests/align/test_xml_tool_calls.py` | Passed. |
| `git diff --cached --check` | Passed for the implementation commit. |

The real template was exercised using installed Jinja2, with HF-style JSON
serialization in its sandbox environment. No renderer existed in the searched
repository code to vendor. Bare-interpreter CI can run the core tests without
adding dependencies, per D-009; the six template tests require Jinja2. Python
3.11 was not run. Aggregate test runtime, including repeated checks, was well
under the requested 20-minute cap.

The safe pilot-4 rerun used this guard before importing the test module:

```python
from pathlib import Path
import unittest
from unittest.mock import patch

clone = str(Path.cwd())
original_is_dir = Path.is_dir

def guarded_is_dir(path):
    text = str(path)
    if text == '/Users/edr/.cache/joulewise/shade':
        return False  # No filesystem query.
    if 'restricted' in path.parts:
        raise AssertionError('restricted directory probe blocked')
    if text.startswith('/Users/edr/') and text != clone and not text.startswith(clone + '/'):
        raise AssertionError('external directory probe blocked')
    return original_is_dir(path)

with patch.object(Path, 'is_dir', guarded_is_dir):
    unittest.main(module='tests.align.test_pilot4', argv=['guarded-pilot4'])
```

## Process deviations and uncertainty

The initial unguarded pilot-4 module import executed its existing
`Path(kit.SHADE_CACHE).is_dir()` decorator against
`/Users/edr/.cache/joulewise/shade`. That was an external metadata query and
violated the owner's no-stat rule. The cache-dependent test skipped; that check
did not open cache contents. The guarded rerun above prevents that query.
One fast XML-module rerun also briefly overlapped the initial pilot-4 run after
I misread a still-running poll, violating the requested serial test ordering.
Later runs were serialized. These deviations are not described as compliant
validation.

Initial file-name discovery included the clone root before explicit
`restricted` exclusions were added to subsequent searches. No restricted path
appeared in its output and no such file contents were opened. The returned
names alone do not establish which directories the file-name walker traversed.

Git used its automatically configured committer identity for the local commit;
no identity settings were changed. There was no peer review or live model test.

## Remaining gate and next exact step

On the measurement Mac, verify the template against pinned revision `815b83c0`
and confirm the exact family in the production model config. Check a separate
Qwen3.5 MoE pinned template before treating that family as template-verified.
Then the lead can schedule a clean, agent-free live gate with token-ID cache
diagnostics. This branch supplies parser/fixture evidence only and does not
authorize or perform that measurement. No other blocking design question remains.

## Fix round

2026-11-05, PR #659; branch `fix/2026-11-05-pr-659`, starting at `d01288e25`.
This section supersedes the original implementation's family list, ambiguous-null
policy, test counts, and remaining B2 work above. The earlier sections retain
their original-run evidence and limitations.

Intake: read `/private/tmp/jwsol/rev-659.json` first (two HIGH, three MEDIUM,
three LOW; no refuted notes), then repository M0, stop card (NONE), current
queue/do-not-do-yet, orchestration, and targeted dependency authority (D-009).
The user's fix brief selects this AGENT task and prohibits coordination-state
edits, full-suite runs, network access, and real measurement-data access.
Those four lead-owned paths remain untouched; no kernel task was registered.
No measurements, analysis pipeline, network calls, dependency installations,
delegated agents, pushes, or remote PR edits ran in this round.

The named council remote ref is absent from this clone. Git object enumeration
in the explicitly allowed shared object store recovered council commit
`219fb151515383cbbcde887d096837a829c67396`; `git show` supplied FINAL-DESIGN.md,
including the B1/B2 build clauses in §2.8. Amendment 1 is absent from that tree
and was not located as a commit in the available objects. Its text was therefore
not independently verified. Apply the owner's explicit amendment instruction:
W1's new cell is Qwen3.8-27B only; Qwen3-Next is dropped, Flash-Next is later.
No window roster or model config was changed here. The brief supplied no new
branch name, so the branch above was selected and disclosed during work.

### Finding-to-commit map

Identifiers below follow severity and order in the supplied review JSON.
Every fix group includes a regression observed failing before the fix and
passing afterward. The documentation handoff is a separate final commit.

| Finding | Commit | Fix and regression |
|---|---|---|
| H1: cap-cut reparsing exposes template-prefilled reasoning | `bf0f0227b` | Remove the redundant second parse; the first parse already honors the template opener and hides the entire unfinished span. Endpoint-level synthetic native streams cover `finish_reason=length`, drafted actions, and a quoted `<think>` for both XML and JSON. The two nested-opener subcases executed a call before the fix. |
| H2: dotted family labels silently select JSON | `142a9ab0b` | Normalize `qwen3.5`/`qwen3.8` (including underscore suffixes), then check configured and loaded XML/JSON protocol membership at prepare and endpoint construction. Check `model_config_name`, top-level `model_type`, and nested `text_config.model_type` when available. Reject contradictions before a turn. Alias and mismatch regressions had six failing subcases before the fix. |
| M1: unverified 122B scalar template | `2b6652561` | Remove `qwen3_5_moe`/`qwen3_5_moe_text` from the supported set; refuse them and their dotted aliases explicitly, including an artifact presented under another configured family. Three subcases failed before the fix. F is unsupported until the pinned `e9c67b08` template and decoder/replay are verified. No F boolean/null byte-stability claim is made. |
| M2: Any, Optional[str], and mixed string unions | `61e9d1c48` | Prefer schema-valid JSON for Any and string/non-string unions, including bare `null` → None; preserve literal text for declared strings. Tests cover numbers, arrays, quoted Any strings, booleans, optional strings, and string/integer and string/array unions. Eight subcases failed under the old ambiguity refusal. |
| M3: B2 controls and identity missing; PR body stale | `88e7772fa` | Add optional `assistant_history` and `chat_template_kwargs`, omit None from spec text, pass controls through workload and both render paths, include effective controls in endpoint and governed execution-policy identity, and keep counterbalance cells separate. Existing implicit XML history also gets an explicit identity entry. New `test_history_rendering` failed with six errors before implementation; actual runtime identity hashes differ across effort levels afterward. Update the legacy cache-test omission list. Current replacement PR body appears below; remote editing remains pending under the no-network rule. |
| L1: real-template tests skipped by CI; byte-only prefix probes | `9d6439519` | Add a dedicated Python 3.13 CI job with optional Jinja2 and explicit real-template modules (history-module step added with M3). The CI-wiring regression failed before the change. Local Python 3.14 runs all Jinja tests. **Disposition:** pinned token-level coverage is written as two opt-in native tests and remains unexecuted here; no pinned tokenizer is supplied and MLX cannot run in this sandbox. |
| L2: shared consumers lose XML reasoning | `4a694ce32` | Add a `reasoning_text` alias without duplicating serialized reasoning; update scrubbing to replace only actual dataclass fields. Monitor full/no-scratchpad views and per-call coalescing retain the intended visibility. The alias/monitor regression failed before the fix. Protocol-v4 integration disclosure follows below. |
| L3: literal think tags inflate hidden-token counts | `0be7fc4b9` | Stop XML output-ID accounting at the first tool-call delimiter outside reasoning, including initial prefilled-opener inference. Keep counting tool syntax genuinely inside reasoning. Endpoint regression counted 46 synthetic byte IDs instead of 5 before the fix. Native pinned-ID regression is supplied but unrun here. |

### Behavior and protocol-v4 integration disclosures

- H1 deliberately changes the affected **legacy JSON cap-cut path**, including
  Qwen3-Next templates with a prefilled opener. Draft actions stay hidden and
  cannot execute; the unfinished reasoning text is retained intact. Frozen
  pilot-9 JSON parser/render/result fixtures still pass. Byte identity beyond
  those fixtures is not claimed for this changed cap-cut behavior.
- Both new spec fields are omitted when None. Existing JSON families retain
  raw assistant history by default. XML families retain the branch's separate
  reasoning history, now represented in execution identity even if the spec
  field is unset. New v4 D specs should explicitly set
  `assistant_history="reasoning_content"` and carry the selected effort in
  `chat_template_kwargs`. Effort, history mode, and kwargs affect identity;
  counterbalancing does not pair different policies.
- XML/D judge input contains visible content and structured calls; reasoning
  is available through `reasoning_text` for full visibility and omitted for
  no-scratchpad visibility. Legacy 30B default transcripts retain raw think
  tags and JSON tool text in content. **The family-dependent judge input is a
  protocol-v4 disclosure**, not evidence of equivalent judge prompts. No
  `pilot_protocol_v4.md` exists on this branch; the lead should carry this
  paragraph into that document when integrating B10.
- The supplied Qwen3.8 fixture remains unverified against pin `815b83c0`.
  No actual SHADE schema census or live R0 parse-rate tally was run. R0 should
  tally XML refusal reasons per tool using the real schemas before W1.
- Noncanonical replay can rewrite prefixes even with separate reasoning.
  The review reports **13 tokens** for compact `[1,2]`, **12** for `2.50`, and
  **27** for a single-LF prose/call separator per transition. These are
  review-provided observations, not measurements repeated in this round.
  Retain these classes in R0's round-trip report. The local effort-ladder
  probe checks canonical bytes only and reports zero rewritten bytes.

### Verification

Final targeted results (each listed module was rerun on the final code):

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_xml_tool_calls` | 21 run, OK; seven Jinja tests skipped (Jinja absent in this interpreter). |
| `python3 -B -m unittest tests.align.test_xml_tool_calls` | Python 3.14.6 / Jinja2 3.1.6: 21 passed, no skips. |
| `python3.13 -B -m unittest tests.align.test_history_rendering` | 9 run, OK; one Jinja and two native tests skipped. |
| `python3 -B -m unittest tests.align.test_history_rendering` | 9 run, OK; seven passed, two native tests skipped. Includes xhigh/medium/low six-turn byte-prefix and historical-reasoning scrub probes. |
| `python3.13 -B -m unittest tests.align.test_xml_fixround` | 7 passed. |
| `python3.13 -B -m unittest tests.align.test_pilot3_cache` | 12 passed. Initial run found a stale test-side optional-field omission list, corrected in M3. |
| `python3.13 -B -m unittest tests.align.test_apple_endpoint` | 9 passed (23.968 s). |
| `python3.13 -B -m unittest tests.align.test_apple_campaign` | 12 passed (71.540 s). |
| `python3.13 -B -m unittest tests.align.test_apple_support_edges` | 4 passed. |
| `python3.13 -B -m compileall -q` on the four changed source files and four changed/new test files | Passed. |
| `git diff --check` | Passed. |

Total test execution was well below 20 minutes. No full suite was run, per the
owner's machine-load rule. **Serial-order deviation:** one campaign-module
invocation started after a poll returned a still-running endpoint module.
Both completed successfully; later modules ran only after process completion.
This brief overlap was a mistake and is not described as serial validation.
The deviations recorded in the original report above belong to the earlier
implementation sessions, not this fix round. No outside-clone `/Users/edr`
filesystem path was queried in this round except Git's permitted shared
repository object access. No real `restricted/` directory was accessed.

### Lead's next exact checks

1. Provide/verify Amendment 1's actual Git object and verify that the brief's
   W1 override matches it. Review the eight fix commits and the final diff.
2. Outside this sandbox, with native MLX and transformers installed, run the
   two tests in
   `tests.align.test_history_rendering.NativeHistoryRenderingTests`:

   ```sh
   JW_ALIGN_NATIVE_TESTS=1 JW_ALIGN_QWEN38_MODEL=/path/to/local/815b83c0-snapshot \
     python3.13 -B -m unittest tests.align.test_history_rendering.NativeHistoryRenderingTests
   ```

   They check the local template digest, six-turn **token-ID** prefix stability
   (one call, two calls, no-content calls, and prose), and literal think-tag
   accounting using native MLX arrays. Imports are gated; tokenizer loading is
   local-only. They load no weights and do not substitute for live generation,
   real SHADE parse-rate, or cache validation in R0. A digest mismatch must be
   resolved as a provenance issue, not waived as a successful test.
3. Carry the judge-input disclosure into protocol v4; apply the replacement
   PR body below when network use is authorized. Run the remaining owning R0
   and review gates under lead control before W1. F remains unsupported.

### Offline replacement PR body

The following is ready for the lead to copy to PR #659. The actual GitHub body
was not read or changed because this session has no network authority.

> Qwen3.8 emits pseudo-XML tool calls and requires separate historical reasoning.
> This change parses schema-directed XML arguments, preserves reasoning in
> assistant history, and adds spec-carried history/template kwargs (including
> the effort ladder) to execution identity. Dotted family aliases are supported;
> loaded artifact/config protocol mismatches fail before a turn. Unverified
> Qwen3.5 MoE templates are explicitly unsupported.
>
> The fix round also prevents draft tool execution at reasoning token cuts,
> supports Any/optional/union parameter shapes, preserves reasoning in monitor
> views, and excludes literal think tags in XML arguments from hidden-token
> counts. JSON cap-cut behavior intentionally changes for affected prefilled
> templates; the frozen pilot-9 JSON fixtures continue to pass.
>
> Validation: the parser/template module has 21 tests, all passing locally with
> Jinja. History policy has 9 tests (7 passed with Jinja, 2 native tests pending);
> fix-round regressions have 7 passing tests. Endpoint (9), campaign (12), cache
> (12), and support edges (4) pass. A dedicated CI job installs Jinja. Full suite
> omitted by owner instruction during the long analysis job.
>
> Pending: pinned `815b83c0` template/tokenizer verification and the two native
> tests; real R0 schema parse-rate, token-level rewrite classes, and live cache
> checks; protocol-v4 judge-input disclosure; lead verification of Amendment 1.
> W1's new model is Qwen3.8-27B only; Next is dropped and Flash-Next is later.
> B2's history/kwargs implementation is complete. No hardware validation is
> claimed. Finding-to-commit details are in this run report's Fix round section.
