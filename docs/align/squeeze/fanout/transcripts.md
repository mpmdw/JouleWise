# v4 transcript retention — 2026-11-08 brief

Branch: `align/2026-11-08-v4-transcripts`, based on W1 kit R10
`d600baba029f70592bb8e792098338e4cd6811d3`. Local work: 2026-11-07 PST.

Implemented the transcript addition only. No model, prompt, roster, seed,
budget, thermal policy, energy estimator, exclusion or replacement rule changed.
No transcript monitor was introduced or called. Existing v4 task/capability
scores remain unchanged; “unscored” below means no transcript suspicion scoring.

## Evidence and custody

- `endpoint.py` adds `raw_text` to each existing `align_turns.jsonl` record.
  This is the generated completion before reasoning/tool parsing, including
  whitespace, malformed/refused calls and truncated reasoning. The existing
  `align_transcript.jsonl` retains system/user messages, assistant history with
  reasoning, parsed tool calls/arguments and tool results. Model history and
  `ChatResult` do not change. The raw completion is essential because D's
  history formatter splits reasoning and trims the call envelope.
- New `transcript_custody.py` copies both logs without rewriting their bytes.
  Each member gets `withheld/align-transcripts/<run_id>.json` under the night
  custody. This deterministic envelope contains base64 of the original files,
  preserving even malformed JSON/UTF-8. SHA-256 covers the entire envelope;
  the receipt also records the two original-file hashes.
- `collection/align-transcripts.json` contains only member IDs, existence,
  completeness, relative custody paths, hashes and structural flags. It says
  `sealed_unscored`, `release_after: v5_registration`. All planned members
  appear, including anchors, contrasts, benign/sabotage D members, excluded
  members and occurrences that never ran. No missing content is reconstructed.
- The existing night driver invokes this only for `align-v4` / `align-v4-*`
  packs, after the chain is proven gone and the hazard monitor has closed.
  Pre-chain refusals record missing transcripts. Unproven termination records
  `transcript.chain_not_quiescent` and defers sealing. Other packs are untouched.
  Custody faults are flags; they do not change the v4 verdict.
- The v4 session desk verifies/retries custody **before the harvest snapshot**,
  including the existing logical `.zst` reader, and attaches the receipt to every
  member. Terminal records alone cannot clear an unproven chain. The generic
  pilot runner has an optional hook for this; its v3 default is unchanged.
  After the existing
  identity/residual checks, it replaces transcript-bearing summary fields,
  decodable token IDs and evaluator text with hashes. The standalone v4 thermal
  desk likewise exports `tokens: {sealed_sha256: ...}` after its checks; equal
  token sequences still compare equal between these exports. Numeric task
  scores and instrument results are preserved. Generic v3 desk behavior stays
  unchanged.

Seals are atomically published, fsynced, owner-only files (0600), with exclusive
creation and exact-byte verification on retry. Changed source/seal bytes cause
a recorded custody fault and never overwrite first evidence. The full files,
original run bundles and backups remain under the same **procedural withheld
custody / no-read embargo as energy outcomes**. No human or monitor may read,
render or score them before v5 registration. There is no release/scoring API
here. This is not encryption or protection against the owner account bypassing
custody permissions; those stronger guarantees are not supplied by the existing
energy custody pattern either.

Flags distinguish missing history, missing turn logs, unreadable/malformed
logs, absent legacy raw completions, turn-count mismatch, incomplete generation
and custody failure. A partial native generation that never returns recoverable
evidence cannot be reconstructed: it remains incomplete/missing. These are
transcript-custody flags, not new registered v4 X exclusions.

## Verification

Failing-first commit `e42967126`: six synthetic tests failed on missing raw-text
logging, sealing and desk receipts. Additional failing tests caught desk text
disclosure and custody errors incorrectly stopping the desk before those fixes.

Targeted unittest modules, each in its own process:

| Command (`python3.13 -B -m unittest …`) | Result |
|---|---|
| `tests.align.test_v4_transcripts` | 16 passed |
| `tests.align.test_v4_powermode_record` | 9 passed |
| `tests.align.test_apple_endpoint` | 9 passed |
| `tests.align.test_xml_tool_calls` | 25 run, 7 optional-Jinja2 skips |
| `tests.align.test_thermal_desk` | 24 passed |
| `tests.align.test_apple_campaign` | 12 passed |
| `tests.align.test_v4_kit` | 116 passed; committed configuration bytes reproduce |
| `tests.align.test_pilot4` (with `JW_ALIGN_REAL_SHADE_TEST=0`) | 18 run, 1 real-SHADE skip |

`python3.13 -B -m compileall -q joulewise tests` and `git diff --check`: passed.
No full suite, analysis pipeline, real measurement data, weights, network,
integration install, state-kernel edit or R1-lane mutation was used.

Process caveats: the kit module accidentally overlapped the campaign module
for about 10 seconds; remaining modules were sequential. An initial synthetic
driver probe could not prove process-group exit because this sandbox denies
`ps`; it correctly deferred sealing. The final lifecycle test substitutes the
chain/monitor lifecycle and asserts sealing after monitor stop. Two temporary
fake monitor sleepers from the initial probe (PIDs 68267, 68871; 600-second
self-exit) could not be signalled for cleanup because the sandbox denied it.
No production process was signalled. Their termination was not independently
verified. A test initially wrote a synthetic roster into a clone configuration
directory; that file was removed and the fixture corrected to use only its
temporary pack directory.

## Authority, uncertainty and next step

Assumed the brief's two-addition v4 freeze, no monitor/human transcript scoring
before v5 registration, and no new transcript-based v4 exclusion rule. The
KM003C, m >= 39, positive-control and adaptive-red-team work belongs to the
other fan-out lanes; this change does not implement or qualify it.

Used the supplied cached design/reviewer/registration/preregistration refs and
`origin/main` items 202–210; no fetch under the binding no-network rule. Older
design suggestions to score pilot transcripts do not authorize scoring v4.

Native process-group and MLX/Metal behavior remain **unqualified here**. The
lead should run `tests.align.test_v4_transcripts` and the focused endpoint and
thermal modules individually outside the sandbox, then verify only receipt
presence, flags and hashes on the next already-authorized W1/D closeout. Do
not inspect real transcript contents before registration. No extra collection
or native model run is authorized by this report.

No design ruling is requested. Future D-kit integration must preserve the
`align-v4` / `align-v4-*` pack identity and `collection_plan.json` member roster,
or explicitly connect its equivalent roster to `seal_window`. A future consumer
of exported thermal token identities must accept the digest representation;
the original IDs remain in sealed custody. Release after registration stays
lead-owned.
