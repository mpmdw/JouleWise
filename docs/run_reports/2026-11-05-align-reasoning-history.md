# ALIGN assistant reasoning history — 2026-11-05

Continuation of `lane/2026-11-05-align-xml-toolcalls`, starting at
`8c0a76510`. One local commit, `ALIGN: store separate reasoning in XML assistant history`;
no push. Prior evidence: [XML parser report](2026-11-05-align-xml-toolcalls.md).

## Authority and scope

The owner's continuation brief authorizes this AGENT task and one local commit,
and overrides coordination-state updates and the full-suite requirement. M0,
repository instructions, the inactive stop card, restart/queue sections, owning
ALIGN endpoint/workload interfaces, and D-009 were inspected. No coordination
files or kernel tasks were changed. No network, analysis pipeline, real
measurement-data access, hardware inference, or quiet-window collection occurred.

The named `origin/lane/2026-11-05-align-window-council` ref is absent in this
clone (`git show ...:docs/align/council-2026-11-05/FINAL-DESIGN.md` failed with
`invalid object name`). The finding supplied in the owner's brief is the
authority used here; the full council document was not independently read.

## Changes

- `joulewise/align/apple/endpoint.py`: XML-family history now retains the
  completion parser's separate `reasoning_content`, final `content`, and
  structured `tool_calls`. The parser uses the actual template's prefilled
  `<think>` opener and `</think>` closer. Validated call envelopes are removed
  from stored visible content and rendered once from the structured calls.
  Already separated visible text is not interpreted as another think block,
  including when reasoning is empty. Legacy raw-history input remains supported.
  Hidden-prefill accounting handles the separate field, and synthetic mock
  serialization handles the structured calls.
- `joulewise/align/apple/workload.py`: stores each assistant result through the
  endpoint's family-gated history method before the next turn.
- `tests/align/test_xml_tool_calls.py`: covers exact family selection, stored
  message fields, literal visible think tags, real two-turn mock workloads,
  JSON transcript compatibility, and six-turn real-template replay through
  `MlxEndpoint.chat` and `MlxRuntimeAdapter._generate` with only native
  computation replaced by an ASCII synthetic stream. The byte-ID fixture also
  checks that historical reasoning is counted once (8 bytes per prior turn).
- `tests/align/fixtures/flashnext_chat_template.jinja` and its provenance JSON:
  exact copy of the supplied Flash-Next template, retained for offline replay.
- This report.

Selection reuses `XML_MODEL_FAMILIES` without adding name/syntax heuristics.
`qwen3_moe` (Qwen3-30B anchors) and `qwen3_next` retain their raw `ChatMessage`
history and existing template arguments. The frozen JSON parsing, rendered
arguments, and endpoint-result bytes still match the pilot-9 fixtures. The new
workload regression also checks unchanged JSON assistant transcript records.

The starting lane already had a render-time raw-history splitter and its
canonical prefix probe passed. This continuation moves the authoritative split
to stored turn history and avoids reinterpreting already split text. It does
not establish a cache improvement over that starting lane on its existing
canonical fixture. The content-only mapping described in the council finding
is reproduced explicitly as a negative control below, rather than mislabeled
as the immediate pre-change endpoint.

## Real templates and six-turn prefix probe

The supplied `.hf-qwen38/chat_template.jinja` and
`.hf-qwen38/flashnext_chat_template.jinja` are byte-identical. Both fixtures and
both supplied files have SHA-256:
`c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041`.
Both assistant branches read earlier reasoning from `message.reasoning_content`
only, trim that field, and default to preserving earlier thinking. Neither
`preserve_thinking` nor `enable_thinking` was passed to the endpoint probe.

Each row compares the previous rendered prompt + synthetic emitted text +
consumed `<|im_end|>` spelling with the next real-template prompt. There is no
invented newline after EOS. Invalidated bytes = old UTF-8 bytes minus longest
common prefix; these are not Qwen tokenizer counts or native cache measurements.
Results are the same for both templates:

| Case | Old bytes before turns 2–6 | Common prefix bytes | Invalidated bytes |
|---|---|---|---|
| Stored split history, canonical tool chain | 1987, 2206, 2425, 2644, 2863 | 1987, 2206, 2425, 2644, 2863 | 0, 0, 0, 0, 0 |
| Stored split history, six user queries | 1905, 2009, 2113, 2217, 2321 | 1905, 2009, 2113, 2217, 2321 | 0, 0, 0, 0, 0 |
| Stored split history, compact tool calls | 1981, 2200, 2419, 2638, 2857 | 1898, 2117, 2336, 2555, 2774 | 83, 83, 83, 83, 83 |
| Simulated content-only mapping, canonical tool chain | 1987, 2217, 2447, 2677, 2907 | 1868, 2098, 2328, 2558, 2788 | 119, 119, 119, 119, 119 |
| Simulated content-only mapping, six user queries | 1905, 2020, 2135, 2250, 2365 | 1868, 1983, 2098, 2213, 2328 | 37, 37, 37, 37, 37 |

The compact-call suffix rewrite remains: the template expands compact XML into
its canonical multiline form. Separate reasoning does not remove that formatting
effect. Cache policy and native cache reconciliation were not changed.

Reproduce the positive cases with `synthetic_endpoint_cache_probe` in the test
module, calling `template_renderer` for each fixture (import `jinja2.sandbox`
first). Its `dialogue=True`, `compact=True`, and `multiple_parameters=True`
options cover the other cases. The new
`QwenTemplateTests.test_both_real_templates_replay_six_split_assistant_turns`
also reproduces the negative control: it patches `_render_xml_prompt` to pass
only role/content and supplies raw history, bypassing both stored fields and
the existing raw-history compatibility splitter.

## Verification

Targeted unittest modules ran serially; no full suite was run, as instructed
while the long analysis job is active. Aggregate runtime was far below 20 min.

| Command | Final result |
|---|---|
| `python3 -B -m unittest tests.align.test_xml_tool_calls` | Python 3.14.6 with Jinja2: 20 passed, no skips (0.405 s). Starting baseline: 16 passed. |
| `python3.13 -B -m unittest tests.align.test_xml_tool_calls` | 20 run: 13 passed, seven optional Jinja2 tests skipped (0.054 s); this interpreter lacks Jinja2. |
| `python3.13 -B -m unittest tests.align.test_apple_endpoint` | 9 passed (32.320 s). |
| `python3.13 -B -m unittest tests.align.test_pilot3_cache` | 12 passed (1.520 s). |
| `python3.13 -B -m compileall -q joulewise/align/apple/endpoint.py joulewise/align/apple/workload.py tests/align/test_xml_tool_calls.py` | Passed. |
| `git diff --check` / `git diff --cached --check` | Passed before commit. |

The new workload regression initially caught a second-turn mock failure:
`ToolCallRequest` was not JSON serializable through the old `__dict__` path.
The XML-only dataclass serialization fix above resolved it; JSON serialization
is unchanged. No dependencies were installed. Python 3.11 was not run.

An initial baseline invocation yielded without its session metadata being
retained; the baseline was rerun successfully. A process-list check intended to
check that invocation was denied by the sandbox; no broader access was requested.
Initial file-name discovery searched the clone root without a `restricted`
exclusion. No restricted path appeared and no restricted contents were opened;
the returned names cannot prove which directories the walker traversed.
Subsequent discovery was limited to named source directories with exclusions.

## Limits and next exact step

There is no blocking implementation question. Flash-Next's supplied template
has no supplied repository/revision provenance; no production Flash-Next config
or weights were loaded. Its marketing name must not enable XML for the JSON
`qwen3_next` family. Confirm the configured family separately at the live gate.
As recorded previously, the 27B template came from mutable `main` and has not
been verified against measurement revision `815b83c0`; no separate Qwen3.5
template was supplied. Preserve those limitations.

Next: lead reviews this local commit, then verifies pinned template/config
identity before any separately authorized, agent-free hardware/cache gate.
No hardware validation or native token-cache benefit is claimed here.
