# What I read

- Every module under `joulewise/`, including adapter implementations, controller lifecycle, bundle I/O, reducer, strict validator, reporting, aggregation, campaign configuration, and CLI.
- All documents under `docs/contracts/`, plus the relevant accepted entries in `docs/decision_log.md`; decision-log entries were treated as authoritative.
- All example configurations under `configs/examples/`.
- A broad test sample covering schemas, controller failures, bundle validation, reduction, reporting, mock CLI end-to-end, MLX/powermetrics, SSH/node-worker, vLLM/NVIDIA fixtures, and NVIDIA integration.
- `scripts/run_campaign.py` for unattended-run and partial-bundle behavior.

# Findings

1. **BLOCKER — vLLM stream chunks are treated as output tokens.**  
   [`_run_vllm_runtime()`](/Users/edr/code/JouleWise/joulewise/adapters/node_worker.py:360) increments `token_count` once per yielded SSE text fragment. The stream parser yields `choice.text` or delta content, whose chunk boundaries are not guaranteed to equal tokenizer boundaries. The test fixture explicitly supplies `["A", "B", "C"]`, embedding that assumption ([test](/Users/edr/code/JouleWise/tests/test_node_worker.py:402)).  
   **Failure scenario:** a server coalesces several tokens into one SSE delta or emits an empty/non-token delta. The fixed output budget, token timestamps, throughput, and joules/output-token are all wrong while the run remains successful. This blocks claim-bearing NVIDIA results until live protocol behavior is pinned.

2. **BLOCKER — strict raw-lineage validation only verifies powermetrics.**  
   The strict path calls the raw-to-trace verifier only for the powermetrics raw artifact and skips other telemetry backends ([CLI](/Users/edr/code/JouleWise/joulewise/cli.py:713)). NVIDIA’s integration test separately re-derives its trace, but that is not part of `validate-bundle --strict` ([test](/Users/edr/code/JouleWise/tests/test_nvidia_node_integration.py:420)).  
   **Failure scenario:** `raw/nvidia_smi.csv` is hand-edited or partially corrupted while `power_samples.csv` and `summary.json` remain unchanged; strict validation still passes. The same omission would apply to Jetson telemetry and to raw vLLM token/response evidence. Strict is correctly scoped by the contract as internal artifact consistency, not physical truth, but it is not yet complete even within that scope.

3. **BLOCKER — a zero-length measured window can be a successful, strict-valid measurement.**  
   The reducer deliberately returns a succeeded zero summary for `start == stop` ([reducer](/Users/edr/code/JouleWise/joulewise/reduce.py:751)), while strict’s sampling-floor check is conditional on positive duration ([CLI](/Users/edr/code/JouleWise/joulewise/cli.py:294)). A test pins the zero-window success behavior ([test](/Users/edr/code/JouleWise/tests/test_reduce.py:406)).  
   **Failure scenario:** a clock/marker bug collapses the interval to zero. The sanctioned reducer produces `0 J`, no sample-floor violation occurs, and strict blesses a bundle containing no usable measurement. Claim eligibility may later reject it, but “strict-valid succeeded run” is already too permissive.

4. **SHOULD-FIX — the transport seam is two incompatible protocols, and remote execution hardcodes SSH.**  
   The public transport contract is `run_command/collect_artifact` ([interfaces](/Users/edr/code/JouleWise/joulewise/interfaces.py:190)); `NodeWorkerClient` instead consumes `run/put_file/collect` ([node client](/Users/edr/code/JouleWise/joulewise/adapters/node_client.py:34)). The registry then rejects every remote transport except SSH and constructs `SshTransport` directly ([registry](/Users/edr/code/JouleWise/joulewise/adapters/__init__.py:83)).  
   **Failure scenario:** a Jetson agent, Kubernetes exec transport, or local subprocess transport fully implements the documented `TransportAdapter`, yet vLLM/NVIDIA still fail with “requires ssh.” It requires registry and client surgery rather than registration.

5. **SHOULD-FIX — there is checkpointing, but no actual experiment resume; manifest writes are not atomic.**  
   The controller claims a killed experiment leaves a valid partial manifest ([controller](/Users/edr/code/JouleWise/joulewise/controller.py:1123)), but the manifest is overwritten with `write_text()` ([bundle writer](/Users/edr/code/JouleWise/joulewise/bundle.py:92)). A rerun begins again at repetition one, whose immutable bundle directory already exists. The campaign runner explicitly classifies partial experiments for operator intervention rather than resuming them ([campaign script](/Users/edr/code/JouleWise/scripts/run_campaign.py:959)).  
   **Failure scenario:** power is lost after repetition 3/5, possibly during manifest replacement. The next unattended launch collides with repetition 1 or stops on a damaged manifest and requires manual relocation. If automatic resume was a premise, that premise is false.

6. **SHOULD-FIX — cleanup failures do not change success status, and local/remote temporary artifacts accumulate.**  
   Controller cleanup exceptions are recorded but leave the run’s successful status unchanged ([controller](/Users/edr/code/JouleWise/joulewise/controller.py:508)). `NodeWorkerClient` creates a new local temporary directory per task without removing it ([client](/Users/edr/code/JouleWise/joulewise/adapters/node_client.py:229)); remote task directories are likewise retained.  
   **Failure scenario:** SSH cleanup fails and leaves a vLLM process running. The bundle is still successful and may pass strict validation, while the next repetition starts another server and OOMs. Long campaigns also fill controller or node temporary storage.

7. **SHOULD-FIX — generated-ID NVIDIA repetitions silently skip cooldown.**  
   `run_experiment()` creates an experiment ID for the run context, but passes the original configuration to cooldown ([controller](/Users/edr/code/JouleWise/joulewise/controller.py:1185)). NVIDIA telemetry requires either `context.run_id` or an explicit configuration `run_id` ([adapter](/Users/edr/code/JouleWise/joulewise/adapters/nvidia_smi.py:344)); cooldown calls it without context and converts the failure to a skipped cooldown.  
   **Failure scenario:** a multi-repetition NVIDIA experiment omits an explicit `run_id`. Every measurement succeeds, but all inter-repetition thermal-recovery checks are skipped, undermining accepted decision D014 without stopping the campaign.

8. **SHOULD-FIX — configuration typos are silently discarded, and `sampling.warmup_seconds` has no behavior.**  
   Schema construction extracts known fields but rejects no unknown keys ([schemas](/Users/edr/code/JouleWise/joulewise/schemas.py:359)); a test expressly requires unknown workload keys to be ignored ([test](/Users/edr/code/JouleWise/tests/test_audit_schema_edges.py:53)). `warmup_seconds` is accepted and appears in examples but has no production consumer ([schema](/Users/edr/code/JouleWise/joulewise/schemas.py:293)).  
   **Failure scenario:** `power_hzz: 10` silently becomes the default 1 Hz, or an operator sets `warmup_seconds: 5` believing stabilization occurs when it does nothing. Reject unknown keys and either implement or delete the unused field.

9. **SHOULD-FIX — generated reports do not implement accepted token-normalization decision D058.**  
   The report emphasizes energy/token and TTFT ([report](/Users/edr/code/JouleWise/joulewise/report.py:303)) but does not co-display request energy, tokenizer identity, boundary identity, and stack identity as required by the accepted decision and binding token-normalization contract ([contract](/Users/edr/code/JouleWise/docs/contracts/token_normalization.md:18), [decision](/Users/edr/code/JouleWise/docs/decision_log.md:2729)).  
   **Failure scenario:** two runs using different tokenizers or accounting boundaries are presented as directly ranked by J/token, without the primary request-energy metric or the metadata needed to see that the denominator changed.

10. **SHOULD-FIX — the documented runtime contract promises split modes that the code cannot express.**  
    The adapter contract says runtimes may execute prefill-only, decode-only, and replay modes ([contract](/Users/edr/code/JouleWise/docs/contracts/adapter_contracts.md:156)), but `RuntimeAdapter` only exposes monolithic `run_workload()` ([interfaces](/Users/edr/code/JouleWise/joulewise/interfaces.py:113)). The node protocol advertises transfer task types, while the worker handler table contains no transfer handler ([worker](/Users/edr/code/JouleWise/joulewise/adapters/node_worker.py:1501)).  
    **Failure scenario:** a second implementer adds the documented split methods or transfer task, but neither controller nor worker can invoke it. D008 correctly anticipates core Phase 3 changes, so the problem is the present contract overstating current extensibility.

11. **SHOULD-FIX — the remote “integration” path reimplements the worker and does not test client/worker composition.**  
    The NVIDIA integration test’s `StubNode.run_task` synthesizes worker status and artifacts itself ([test](/Users/edr/code/JouleWise/tests/test_nvidia_node_integration.py:104)). Interface tests mostly use runtime-checkable `isinstance`, which verifies attribute presence rather than signatures or semantics ([test](/Users/edr/code/JouleWise/tests/test_interfaces.py:28)). The mock CLI E2E is explicitly in-process ([test](/Users/edr/code/JouleWise/tests/test_cli_run.py:1)).  
    **Failure scenario:** a request field or artifact name drifts between `NodeWorkerClient` and the real node worker; client tests, worker tests, and stub integration tests all stay green. Add a localhost subprocess test using the actual node worker and fake backend executables, plus a reusable semantic adapter-conformance suite.

12. **NIT — binding prose conflicts on split-node event fields and clock domains.**  
    The bundle layout fixes the event schema to five keys and places node identity in metadata ([layout](/Users/edr/code/JouleWise/docs/contracts/run_bundle_layout.md:149)), then later describes merged events with a `node` field. Measurement methodology says no non-epoch timebase appears in artifacts, while the node-worker protocol says raw files remain in node clock domains ([protocol](/Users/edr/code/JouleWise/docs/contracts/node_worker_protocol.md:236)).  
    **Failure scenario:** one implementer adds a top-level `node` key and is rejected by the exact event parser; another rewrites raw timestamps and violates D002’s raw-verbatim rule. The exact five-key schema and raw-preservation decisions should win; the conflicting prose should be corrected.

# Design judgment

The architecture is credible for additional **single-node, monolithic** backends, but “new adapters without core surgery” is only partially true. A runtime that returns the existing `RuntimeResult`, telemetry that emits controller-domain `PowerSample`s, and an existing transport can reuse the controller, bundle writer, and reducer. It still requires enum/schema additions and edits to the registry’s explicit dispatch chain. Remote runtimes additionally enter the SSH-specific node-client path.

A Jetson backend would require:

- A Jetson telemetry implementation and resolver branch.
- Worker task configuration, artifact mappings, raw-lineage validation, fixtures, and an example configuration.
- A runtime resolver/worker path if it uses llama.cpp or another runtime not already supported.
- Potential rail-manifest and boundary-policy work, but not necessarily a new single-node reducer if it preserves existing sample and phase contracts.

Phase 3 is not an ordinary adapter extension. D008 and the Phase 3 plan correctly imply core changes: multi-target schemas, multi-node controller orchestration, prefill/decode/transfer state machines, per-node clock mappings and error bounds, composite bundle layouts, multiple idle baselines, composite reduction, strict validation per node, and report/aggregate discovery. The existing adapters can remain useful leaf components, but the controller and evidence model need a new composite orchestration layer. Large KV-transfer artifacts also do not fit comfortably into today’s `dict[str, str]` output-artifact model.

Contract quality is strongest around failure/status ownership, phase markers, rail alignment, immutable raw evidence, and the explicit provisional NVIDIA protocol pins. It is weaker at behavioral compatibility: metadata dictionaries are open-ended, the two transport interfaces disagree, stream/token semantics are underspecified, and there is no executable adapter conformance suite.

The tests are not broadly tautological: controller finalization, adversarial bundle validation, raw parser fixtures, and reduction invariants are substantial. The weak seam is where mocks stand in for process behavior, streaming APIs, privilege boundaries, SSH copying, and cross-clock execution. Real Mac evidence reduces that risk for MLX/powermetrics; the NVIDIA path remains appropriately provisional.

I would simplify the design by:

- Collapsing `TransportAdapter` and `NodeTransport` into one protocol and passing the resolved instance into `NodeWorkerClient`.
- Replacing adapter `if` chains with explicit factory maps while retaining schema allowlists.
- Sharing the runtime-side suite marker/state-machine scaffolding between mock and MLX; D045 still requires the item loop to remain runtime-side.
- Consolidating event/suite parsing and strict checks into typed readers plus a backend raw-verifier registry.
- Deleting `warmup_seconds` unless it receives defined lifecycle semantics.

# Checks performed

Static source/contract/test cross-read; decision-log precedence review; read-only Git inspection at `529bffa`; no suite, imports, hardware commands, or file writes. Pre-existing working-tree changes were left untouched.