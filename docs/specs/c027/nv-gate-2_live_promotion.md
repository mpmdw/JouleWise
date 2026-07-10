# NV-GATE-2: NVIDIA Live-Promotion Hard Acceptance Gates

Status: ADJUDICATED 2026-07-09 (C-028) — rulings in `ADJUDICATION.md` in this directory AMEND this spec wherever they conflict with its body text

Queue anchor: `TASK_QUEUE.md` row P2-005 (NV-GATE-2 list). Source findings:
`docs/reviews/2026-07-09-c027-whole-project-review.md` §3 B7(b) and §7 rows
ARC-1, ARC-2, ARC-6 (remote half), ARC-7, ARC-11; detail in
`docs/reviews/c027/lens-arch.md` findings 1, 2, 6, 7, 11.

Scope ruling (binding): these are **acceptance gates at NVIDIA live
promotion**, not pre-Window-A work. Nothing here blocks Window A. Units
NV-2, NV-3 (fixture half), NV-4 (code half), and NV-5 are implementable
now without hardware; NV-1 capture and all checklist rows execute only at
first live contact. No NVIDIA protocol pin changes before live contact —
provisional pins stay provisional until the evidence rows below are
recorded (checklist §7 "De-Provisionalization Notes" remains the exit
door).

Definition of "live promotion": the first claim-bearing NVIDIA/vLLM run —
i.e., any 2K bundle whose numbers would be cited beyond the live
verification checklist itself. All six units below must be CLOSED (green
or explicitly waived by the lead with a decision-log entry) before that
point.

---

## NV-1: vLLM stream token semantics (ARC-1, B7(b))

**Problem.** `_run_vllm_runtime()` (`joulewise/adapters/node_worker.py`
~360–400) increments `token_count` once per SSE text fragment and writes
one `tokens.jsonl` record per fragment. SSE chunk boundaries are not
guaranteed to be tokenizer boundaries; the fixture (`tests/test_node_worker.py`
~402) hardcodes `["A","B","C"]`, baking the chunk==token assumption into
the tests. Every downstream number keyed on output tokens (throughput,
J/output-token, token timestamps, requested-vs-emitted budget check) is
wrong if a live server coalesces or pads deltas.

**Live-pinning protocol (executed at first live contact, not before):**

1. Issue the standard streamed completion via the JouleWise prepare/run
   path AND capture, from the same server:
   a. the final SSE `usage` block if the server emits one under
      `stream_options: {"include_usage": true}` (OpenAI-compatible vLLM
      does; this is the candidate authoritative count);
   b. the non-streamed twin of the same request (`stream: false`, same
      prompt/params/seed) and its `usage.completion_tokens`;
   c. the raw SSE transcript (verbatim bytes to a raw artifact) so chunk
      boundaries are re-derivable offline.
2. Record three integers side by side: SSE chunk count, streamed
   `usage.completion_tokens` (if present), non-streamed
   `usage.completion_tokens`. Also tokenize the concatenated output text
   with the pinned tokenizer and record that fourth count.
3. Pin the observed relationship (equal / coalesced / padded) in checklist
   §7 as the de-provisionalization evidence for the stream-semantics pin.

**Code change shape (agree with the queue's preference; adopted):**

- Prefer **server-reported token counts**: parse the terminal `usage`
  block from the stream (request `stream_options.include_usage` in the
  payload) and use `usage.completion_tokens` as `token_count` when
  present.
- Chunk count remains ONLY as a labeled fallback. Introduce
  `token_count_source` in the runtime result metadata with values aligned
  to the claims-ladder vocabulary (P2-016(i)): `"server_usage"` |
  `"stream_chunk_fallback"`. A fallback-sourced count must never be
  silently equal-status: strict/claim paths treat
  `stream_chunk_fallback` as claim-ineligible for per-token metrics
  (request-level joules remain eligible — the denominator, not the
  numerator, is suspect).
- Per-chunk timestamps in `tokens.jsonl` are re-labeled honestly: the
  record key stays but the file header/metadata gains
  `"record_unit": "sse_chunk"` — they are chunk arrival times, not
  token times, until live evidence shows equality. Do NOT rename the
  artifact (raw-verbatim/D-002 discipline; the semantics label is
  metadata).
- The `["A","B","C"]` fixture is retained but joined by a coalesced
  fixture (`["AB","C"]` with `usage.completion_tokens: 3`) asserting the
  server-usage path wins and the fallback path labels itself.
- Implementation of the payload/parse change may land pre-live (it is
  additive and fixture-tested); the **pin flip** — declaring which count
  is authoritative for claims — happens only after step 1–3 evidence.

**Checklist row** (append to `docs/phase_1/2k_live_verification_checklist.md`,
new §8; exact lines in NV-6).

## NV-2: NVIDIA cooldown context fix (ARC-7) — code-now

**Problem.** `run_experiment()` generates an experiment id, but
`_cooldown_between_reps()` (`joulewise/controller.py` ~1198) resolves
telemetry and calls `cooldown_gate(telemetry, ...)` with no `RunContext`.
`NvidiaSmiTelemetry._task_run_id()` (`joulewise/adapters/nvidia_smi.py`
~344) raises `AdapterFailure` when neither `context.run_id` nor
`config.run_id` exists; `_cooldown_between_reps` converts that to
`{"result": "skipped"}`. Net effect: every generated-id multi-rep NVIDIA
experiment silently skips all D-014 thermal-recovery gates.

**Exact fix.**

1. Thread a `RunContext` (or minimally the run id) into the cooldown
   path: `_cooldown_between_reps` constructs a cooldown-scoped context
   with `run_id = f"{experiment_id}-cooldown-{after_member}"` (unique per
   gate invocation so node-side artifact/pidfile isolation holds — see
   checklist §2 evidence rules) and passes it through `cooldown_gate` to
   the telemetry adapter's idle-measure call. Signature change is
   internal to `controller.py` + `cooldown_gate`; no schema change.
2. The cooldown note records the id used (`"cooldown_run_id"` key) so the
   manifest is auditable against node-side artifacts.

**Test obligation (testable NOW, no hardware).** A multi-repetition
NVIDIA fixture experiment (extending `tests/test_nvidia_node_integration.py`)
with NO `run_id` in config must produce a manifest whose every
`cooldown[]` note has `result` in the executed set (`ok`/`cap_hit` per
the gate vocabulary) and NOT `skipped`. Mutation-style per STA-11: this
test must FAIL against current behavior before the fix lands. A second
assertion pins the negative: mock telemetry still records
`skipped/"mock telemetry"`.

## NV-3: strict raw-to-trace lineage for nvidia_smi (ARC-2)

**Problem.** `_strict_raw_to_trace_problems` (`joulewise/cli.py` ~713) is
powermetrics-shaped: for any other telemetry backend with no
`raw/power_samples.raw` it returns `[]` — strict validation performs zero
raw-lineage verification for NVIDIA bundles, even though the integration
test proves re-derivation is possible (`tests/test_nvidia_node_integration.py`
~420).

**Relationship to P2-016d (binding).** This unit **supersedes and
implements** queue item P2-016(d) "per-backend raw-to-trace strict
generalization (with 2K live)". On adjudication of this spec, P2-016(d)'s
row gains the note "implemented by NV-GATE-2 unit NV-3; see
`docs/specs/c027/nv-gate-2_live_promotion.md`". No second implementation.

**Registry shape.**

- Replace the single function with a per-backend verifier registry in
  `cli.py`:

  ```python
  RAW_TO_TRACE_VERIFIERS: dict[TelemetryBackend, RawToTraceVerifier] = {
      TelemetryBackend.POWERMETRICS: _verify_powermetrics_raw_to_trace,
      TelemetryBackend.NVIDIA_SMI: _verify_nvidia_smi_raw_to_trace,
  }
  ```

  where `RawToTraceVerifier = Callable[[BundleReader], list[str]]`.
- Strict dispatch: resolve the bundle's validated telemetry backend; if a
  verifier is registered, run it — the raw artifact being MISSING is a
  strict failure for registered backends (fail-closed), matching current
  powermetrics behavior. If NO verifier is registered (mock, future
  backends), strict emits an explicit advisory problem-or-note
  `"strict: raw-to-trace: no verifier registered for backend X"` rather
  than silent `[]` — adjudication point: advisory note (preferred, keeps
  mock green) vs hard failure.
- `_verify_nvidia_smi_raw_to_trace` re-derives trace rows from
  `raw/nvidia_smi.csv` using the same parser + clock-offset application
  the adapter uses (share the derivation function from
  `adapters/nvidia_smi.py`; do not duplicate parsing), then compares
  row-count, timestamps, and power values against `power_trace.csv`
  exactly as the powermetrics verifier does.

**Fixture obligations (code-now).** Committed NVIDIA fixture bundle must
pass strict; a tampered twin (one edited `raw/nvidia_smi.csv` power cell)
must fail strict with a raw-to-trace problem. Both are ordinary pytest
fixtures — no hardware.

**Legacy-bundle ruling.** Existing committed bundles: the six legacy Mac
bundles are powermetrics and unaffected. Any pre-existing NVIDIA
*fixture* bundles must be regenerated or gain the required raw artifact;
there are no legacy claim-bearing NVIDIA bundles (all NVIDIA numbers are
still pre-live), so **no legacy allowlist entry is created** — the D-033
frozen six-identity allowlist does not grow.

## NV-4: remote temp-artifact cleanup surfacing (ARC-6, remote half)

**Coordination.** P2-040 owns the LOCAL half (controller-side cleanup
failure surfaced into run quality; `node_client.py` ~229 leaks one
`tempfile.mkdtemp(prefix="joulewise-node-artifacts-")` per task with no
removal). This unit owns the REMOTE side; the local `mkdtemp` leak sits
on the boundary — ruling: the per-task local temp dir is cleaned by
`NodeWorkerClient` itself (try/finally after status parse + artifact
move), and its failure reporting rides this unit's mechanism since the
client is remote-path-only code.

**What gets recorded.**

- `NodeWorkerClient` gains a `cleanup_report` accumulated across tasks:
  per task, `{task_id, remote_path, removed: bool, error: str|None}` for
  the remote task directory teardown, plus the local temp-dir twin.
- The controller merges this into run metadata under
  `metadata.extra.node_cleanup` and into measurement quality: a new
  quality entry `remote_cleanup_failed` listing the paths that survived.

**When cleanup failure flips run status.** Ruling (mirrors lens-arch
finding 6's failure scenario — a surviving vLLM server poisons the next
rep):

- Failure to remove remote FILES/directories → run stays `succeeded`,
  quality-flagged (`remote_cleanup_failed`), and the experiment manifest
  cooldown/gap notes carry it forward. Claim paths may still consume the
  bundle.
- Failure to terminate a remote PROCESS the worker started (vLLM server,
  nvidia-smi sampler — i.e., `runtime cleanup` or `stop_sampling` task
  reports the pid still alive) → the run is DEMOTED from `succeeded`:
  status `failed` with `FailureReason` cleanup-specific reason code. A
  live process is a measurement-integrity threat to the NEXT rep, not a
  hygiene issue.

**Test obligation (code-now).** Fixture worker task whose cleanup handler
reports a live pid → run status failed; fixture reporting only an
unremovable directory → succeeded + `remote_cleanup_failed` present.

## NV-5: localhost subprocess integration test (ARC-11) — code-now

**Problem.** `StubNode.run_task` (`tests/test_nvidia_node_integration.py`
~104) synthesizes worker status and artifacts itself: client tests,
worker tests, and "integration" tests can all stay green while request
fields or artifact names drift between `NodeWorkerClient` and the real
`node_worker.py`. This is the exact blind spot class that produced every
hardware-side surprise to date.

**Shape.** New `tests/test_node_worker_subprocess.py`:

- Launches the REAL `joulewise/adapters/node_worker.py` as a subprocess
  (`sys.executable`, localhost, local-filesystem transport standing in
  for SSH — the transport seam is not under test; the client↔worker JSON
  contract is).
- Fake backend executables on PATH in a temp dir: a `vllm` stand-in that
  serves a minimal OpenAI-compatible SSE endpoint (canned chunks +
  `usage` block per NV-1's fixture shape) and a `nvidia-smi` stand-in
  emitting the pinned CSV query shape.
- Must exercise, through the real handler table
  (`OPERATION_HANDLERS`, `node_worker.py` ~1501):
  1. request/artifact NAME PARITY client↔worker — every artifact name the
     client expects to collect is asserted against what the worker
     actually wrote (the drift detector);
  2. the tokens file: `tokens.jsonl` produced by the real
     `_run_vllm_runtime` against the fake server, including the NV-1
     `token_count_source` metadata;
  3. artifact collection round-trip into the client's local artifacts
     dir, including status.json parse and the NV-4 cleanup report.

**Marking ruling: always-on**, not `skipUnless`. It needs only Python and
localhost sockets — no GPU, no vLLM install (the server is faked). If CI
sandboxing forbids localhost sockets, fall back to
`@pytest.mark.skipif(no_localhost_sockets)` with the probe recorded — but
the default posture is always-on precisely because opt-in integration
tests rot. StubNode is NOT deleted (it remains the fast fixture for
adapter-logic tests) but loses the word "integration": rename/comment so
no one mistakes it for contract coverage.

## NV-6: go/no-go wiring

**Code-now (pre-live, ordinary [AGENT] work, fixture-verified):**

- NV-2 fix + failing-first test.
- NV-3 verifier registry + NVIDIA fixture pass/tamper-fail pair
  (supersedes P2-016d).
- NV-4 cleanup report + status-demotion rule + fixtures.
- NV-5 subprocess test.
- NV-1's parsing/labeling change (usage-block parse, `token_count_source`,
  coalesced fixture) MAY land pre-live; its authoritative-count pin flip
  MAY NOT.

**Live-window-only:**

- NV-1 capture steps 1–3 and the de-provisionalization notes.
- Live re-execution evidence for NV-2/NV-3/NV-4 rows below.

**Exact acceptance lines appended to
`docs/phase_1/2k_live_verification_checklist.md` as new §8 (items 16–20,
continuing the existing numbering; §7 De-Provisionalization Notes moves
after or renumbers to §9 — editor's choice, keep anchors stable):**

```markdown
## 8. NV-GATE-2 Live Promotion Acceptance (C-027)

16. Stream-vs-token pin (NV-1): capture raw SSE transcript, streamed
    `usage.completion_tokens`, non-streamed twin's count, and pinned-
    tokenizer count for one live request. Expected evidence: all four
    integers recorded side by side; bundle metadata shows
    `token_count_source: server_usage`; relationship (equal/coalesced)
    recorded in the De-Provisionalization Notes.
17. Cooldown executes under generated ids (NV-2): one live n>=2 NVIDIA
    experiment with no config `run_id`. Expected evidence: every
    manifest `cooldown[]` note has result ok/cap_hit (never skipped) and
    a `cooldown_run_id`; node listing shows matching artifact dirs.
18. Strict lineage live (NV-3): `validate-bundle --strict` passes on a
    live NVIDIA bundle; hand-tamper one `raw/nvidia_smi.csv` cell on a
    COPY and re-validate. Expected evidence: pristine passes, tampered
    fails with a raw-to-trace problem naming nvidia_smi.
19. Remote cleanup surfaced (NV-4): after item 17's experiment, list the
    node work root and local temp root. Expected evidence: no surviving
    per-task dirs; `metadata.extra.node_cleanup` present with
    removed=true rows; simulate one kill mid-cleanup and confirm the
    demotion path (status failed on surviving process).
20. Subprocess parity suite green on the promotion commit (NV-5):
    `pytest tests/test_node_worker_subprocess.py` output recorded.
    Expected evidence: pass at the exact SHA being promoted.
```

Go/no-go rule: NVIDIA live promotion requires items 16–20 recorded green
(or lead-waived with a decision-log entry). Items 17–20 are expected
formalities if the code-now work landed; item 16 is the only genuinely
new live evidence.

## Fences

- No protocol pin changes before live contact; every pin touched here
  (stream semantics, CSV query shape, artifact names) stays PROVISIONAL
  until its §8 row is recorded.
- NV-1's fallback path must remain labeled — deleting the
  `stream_chunk_fallback` branch entirely is out of scope until live
  evidence shows `usage` is always present.
- No growth of the D-033 legacy allowlist (NV-3 ruling).
- This spec adds no Window-A work; if any unit is discovered to block a
  Mac-side path, that is a spec bug — escalate, don't absorb.

## DEVIATIONS / OPEN QUESTIONS

1. NV-3 unregistered-backend posture: advisory note (spec preference) vs
   hard strict failure for backends with no verifier. Lead to adjudicate;
   hard-fail would break mock bundles unless mock gets a trivial verifier.
2. NV-4 demotion granularity: demote on ANY surviving worker-started
   process, or only runtime processes (vLLM) and not the sampler?
   Spec says any; a surviving sampler also contaminates the next idle
   baseline.
3. NV-2 cooldown id shape (`{experiment_id}-cooldown-{after_member}`)
   assumes worker-side run-id validation accepts it (length/charset per
   the protocol contract) — verify against `node_worker_protocol.md`
   during implementation; if constrained, fall back to a fresh generated
   id + manifest note linking it.
4. NV-1: whether `stream_options.include_usage` is accepted by the pinned
   vLLM version is itself provisional — the payload addition must degrade
   gracefully (server rejects unknown field → retry without it, fallback
   label applies).
5. Checklist §7/§8 renumbering: this spec appends §8 after §7; if the
   editor prefers De-Provisionalization Notes to stay last, renumber to
   §9 — content above is numbering-agnostic except item ids 16–20.
