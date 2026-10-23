Adapted from t3code (MIT, T3 Tools Inc.), commit defb7e6e, packages/effect-codex-app-server/src/replay.ts and apps/server/src/orchestration-v2/testkit/fixtures/

The top-level NDJSON fixtures are projections of T3's recorded **0.156.1** Codex transcripts, updated
to the supplied **0.163.0** JSON schemas and this adapter's policy. They are
not live 0.163.0 validation. Each first-line `transcript_start` records its
source path, source version, adaptation, and any scripted mutation.

- `normal`, `restart_start`, and `resume` retain recorded turn/message events.
- `command_declined` and `file_declined` change recorded approval acceptance
  to decline. Downstream recorded text is not evidence that a write occurred.
- `cancel` adapts the recorded interrupt exchange onto the simple transcript.
- `archived_resume`, `rerouted`, `failed`, `crash`, `malformed`, and
  `other_declined` identify synthetic fault/request insertions in metadata.
- `legacy_declined` inserts both legacy approval methods and their 0.163.0
  schema's `{decision:{denied:{rejection:...}}}` answers mid-turn.
- `initialize_only` stops after initialization, so any thread RPC is unexpected.

The peer checks outbound method/parameter subsets, remaps client request ids,
checks response correlation, ignores clock fields, and emits `afterMs` delays.
An error `runtime_exit` exits with its scripted status after checking that no
entries remain. A successful `runtime_exit` waits for EOF or SIGTERM, matching
the live recorder's teardown boundary after the caller receives its last result.
An exhausted transcript also keeps the peer alive until EOF or SIGTERM.
The cursor advances only after matching each expected outbound frame. Every
complete replay prints `REPLAY OK <scenario>`; unconsumed expectations or extra
frames produce `REPLAY ERROR`, including during teardown and scripted crashes.

`live/live_0163_smoke.ndjson` is a separate privacy projection of the lead's
real **0.163.0** capture. It is not T3-derived. Its header records the original
three MCP calls and their results: LIVE_OK_1, LIVE_OK_2 on the same thread,
and a read-only write attempt with one declined command approval. Regenerate:

```sh
python3 -B tests/fixtures/codex_app_server/scrub_recording.py <raw-frames.ndjson> <smoke.json> tests/fixtures/codex_app_server/live/live_0163_smoke.ndjson
```

The projection preserves frame order, timestamps, ids and non-private content.
Hostname and installation id become fixed strings; account/rate-limit payloads
become schema-valid empty objects, without plan or credit keys. User agents
retain the client/version with fixed OS-detail text, home paths use
`/home/replay-user`, and cwd uses `{{CWD}}` (substituted at replay time).
The schema checks include every live frame; only the T3 attribution assertion
is limited to the top-level fixtures.

Every start/resume expectation includes both forced reverse-Claude settings:
disabled plus `/usr/bin/false`. Caller MCP-server overrides are refused rather
than merged. The obsolete `profiles.*` policy checks were removed after the
reviewer's real 0.163.0 probe returned: `failed to load configuration: legacy
profile = "x" config is no longer supported; use --profile x with x.config.toml
instead` (the CLI quotes those config/command fragments with backticks).
The archived-resume fixture uses the real error wording with its fixture
thread id substituted.

`schema-catalog.json` is a validation-only projection of first-party CLI
0.163.0 schemas: the retained envelopes, response schemas, and reachable
definitions, without descriptions/defaults/titles. The dependency-free schema
test validates every kept frame; the deliberately malformed frame is the sole
negative exception. It rejects unsupported schema validation keywords.
`python3 -B tests/fixtures/codex_app_server/validate_schemas.py <schema-dir>`
rechecks the same frames directly against the full CLI-generated schemas.

For the lead's real smoke, `CODEX_MCP_FRAME_LOG=<path>` records the complete
app-server exchange (including prompt and response text) in this replay
format. The header version comes from initialize's userAgent; a server that
answers only `Already initialized` has version `unknown`. Review and sanitize
such a recording before adding it here. Keep recorded evidence immutable;
make a separate fixture projection if policy or path normalization is needed.

T3's license for the adapted protocol/replay material follows:

MIT License

Copyright (c) 2026 T3 Tools Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
