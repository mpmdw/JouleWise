```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "The custody collision is confirmed and a bounded design is ready, but the unruled ownership and liveness contract blocks implementation.",
  "workspace": {"base_requested":null,"base_mode":null,"head_start":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","head_end":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","upstream_end":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","branch":"feat/2026-09-04-fan-NODE-CUSTODY-DEFAULT-01"},
  "pathspec": ["docs/process_traces/2026-09-04-fanout/NODE-CUSTODY-DEFAULT-01/01-sol-report.md"],
  "unowned_dirty": [],
  "verdict": {"implementation":"no_change","acceptance":"needs_ruling"},
  "verification": [
    {"id":"V1","kind":"test","cmd":"python3 -m unittest tests.test_node_client","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["....................","----------------------------------------------------------------------","Ran 20 tests in 6.654s","","OK"]},"expected":{"exit_code":0,"tail_regex":"^OK$"}},
    {"id":"V2","kind":"inspection","cmd":"python3 -c 'import json,pathlib,re; p=pathlib.Path(\"docs/process_traces/2026-09-04-fanout/NODE-CUSTODY-DEFAULT-01/01-sol-report.md\"); s=p.read_text(); m=re.match(r\"```json\\n(.*?)\\n```\",s,re.S); assert m; d=json.loads(m.group(1)); assert d[\"schema\"]==\"claude-codex-report/v1\" and d[\"genre\"]==\"implementation\"; print(\"report envelope: OK\")'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["report envelope: OK"]},"expected":{"exit_code":0,"tail_regex":"^report envelope: OK$"}}
  ],
  "flags": [
    {"id":"F1","kind":"lead_ruling","level":"blocking","text":"No adopted ruling defines how a unique default client namespace proves that its owner is inactive before another process reclaims its manifest.","needs":"Rule the namespace and liveness contract; recommendation: unique per-client directories under the stable default base, each protected by a lifetime advisory lease, with later processes scanning only lease-acquirable directories and preserving the existing scope equality check."}
  ]
}
```

## Change

No production or test code changed because the missing choice is a custody contract, not a mechanical detail. The row was traced through its complete kernel entry, its cited desk-session report, the node-worker protocol, the NVIDIA stream ledger, the adapter registry, the client implementation, and the focused client and integration tests.

### Forcing problem

`DEFAULT_RETENTION_ROOT` is one fixed temporary directory. A retention manifest is the local index that records remote evidence which must not be deleted until a durable local copy exists. File locking makes each manifest rewrite atomic, but it does not assign ownership: a newly constructed client sweeps every record with the same scope. Here, scope means the transport implementation, destination, and remote work root. Two live clients with that same scope can therefore treat each other's in-progress records as abandoned. Merely giving each client a unique directory prevents that interference but also prevents a later process from finding an abandoned manifest.

The existing safety boundary must remain intact: a later sweep may delete remote material only after collection, response-identity validation, and an on-disk custody acknowledgement. Nothing in the proposed design weakens those checks.

### Options requiring a ruling

| Option | Namespace and liveness rule | Consequence |
|---|---|---|
| A — recommended | Keep the stable default path as a discovery base. Give each default-constructed client a unique child directory and hold an advisory owner lease for that client's lifetime. A later process scans child directories, skips every lease it cannot acquire immediately, and applies the existing exact scope match before reclaiming a record. | Separates live clients while preserving automatic later-process discovery. The operating system releases the lease after process termination, including an abrupt exit. The existing manifest schema and explicit `retention_root` behavior can remain unchanged. |
| B | Keep one stable directory, but give each client a unique manifest and owner-lease file within it. Later processes scan manifests whose lease is acquirable. | Preserves a flatter layout, but couples multiple manifest and lease filenames in one directory and requires a larger refactor of path handling. |
| C | Retain the fixed shared manifest and record the collision as accepted operational risk. | Preserves current reclamation but does not meet the kernel acceptance requiring non-collision for concurrent default clients. |

Recommendation: Option A. It makes ownership visible in the directory tree, leaves the evidence record format alone, and composes with the existing scope entitlement and custody-before-cleanup checks. The scan must reject symbolic-link child paths and must not block on a live owner's lease.

### NEEDS_RULING checklist

- Question: what mechanism proves that a default retention namespace is abandoned and therefore eligible for reclamation?
- Options considered: unique child directories with lifetime owner leases and discovery scanning (Option A); unique manifest-and-lease files in one directory (Option B); or acceptance of the shared-manifest risk (Option C).
- Recommendation: adopt Option A, after the independent design and bounded debate required by D-144. This report supplies the Sol design seat; it does not substitute for the other required seat or the magistrate's ruling.
- Blocked work: production root selection, orphan discovery, owner-liveness enforcement, the counterfactual regressions, and any normative node-worker protocol amendment.
- Resume condition: an issued ruling states the chosen option, lease lifetime, discovery boundary, treatment of explicit `retention_root`, and whether abandoned empty namespaces are retained or removed.

### Worked example

Clients Alpha and Beta start concurrently for the same remote node. Each receives a different child directory under the stable discovery base and holds that directory's owner lease. Beta's first reclamation scan sees Alpha's held lease and skips Alpha's manifest, so Alpha can continue updating its own record. If Alpha's process later terminates before collection finishes, the operating system releases its lease. A client in a later process can then acquire Alpha's lease, read Alpha's manifest, select only records whose existing scope exactly equals its own, and run the unchanged sequence: collect evidence, validate the response identity and custody token, write the durable acknowledgement, then delete the authorized remote path.

### Mechanical work after the ruling

The implementation should remain confined to `joulewise/adapters/node_client.py` and `tests/test_node_client.py` unless review finds an explicit contract-document amendment necessary. The focused regressions should establish:

- two default-constructed clients in one process receive separate manifests, and one client's first sweep cannot remove or mutate the other's record;
- an active owner lease prevents cross-process reclamation;
- after the owner process exits, a later process discovers the abandoned manifest, reclaims only a matching-scope record, and leaves a non-matching scope untouched;
- explicit `retention_root` callers retain their current single-root behavior and every collection, identity, acknowledgement, and path-containment assertion remains unchanged.

The first and later-process regressions are counterfactual-shaped. Reverting to the fixed shared root makes the live-client test fail when one client sweeps the other's record. Making roots unique without discovery makes the later-process test fail because the abandoned manifest is never found.

### Finding and decision table

| Finding | Evidence | Disposition |
|---|---|---|
| The collision is semantic, not an atomic-write defect. | `NodeWorkerClient.run_task` performs a first-use sweep; `_sweep_retained_artifacts_locked` accepts every equal-scope record; manifest read-modify-write operations already use `flock` and atomic replacement. | Confirmed; changing only manifest write locking cannot close the row. |
| A unique path alone breaks automatic reclamation. | The client reads only `self.retention_manifest_path`; no discovery index or directory scan exists. The protocol requires a later retention-manifest sweep for ambiguous sessions. | Confirmed; uniqueness must be paired with discovery. |
| Scope equality already defines which remote records a client may reclaim. | `_retention_scope` binds transport class, destination, and remote work root, and the sweep ignores unequal scopes. | Preserve exactly; do not broaden entitlement. |
| The owner-liveness mechanism is not settled by an adopted artifact. | The kernel status note calls this a deferred `NEEDS_RULING` tradeoff; D-144 bars implementing a new design without the required independent designs, debate, and lead ruling. The task prompt also directs unruled design-bearing choices to `NEEDS_RULING`. | Blocking `NEEDS_RULING`; Option A recommended. |
| No hardware action is needed for the desk design or focused regressions. | The affected behavior is local temporary-directory, process, file-lock, and manifest logic; the remote transport can remain a deterministic test double. | Desk-completable after ruling; live NVIDIA promotion remains governed separately by the protocol's existing provisional label. |

### Lead-owned follow-up

After the ruling and implementation gate, the magistrate should update `docs/process/state_kernel.json`, `TASK_QUEUE.md`, and `RUN_STATE.md`; those files were explicitly excluded from this worker's authority. If Option A changes normative protocol wording, the smallest expected documentation amendment is the reclamation paragraph in `docs/contracts/node_worker_protocol.md`.

## Verification notes

The focused node-client module passes at the unchanged baseline. This confirms that the existing custody-before-cleanup assertions remain green; it does not close the missing concurrency and discovery acceptance. The repository-wide test suite was not run, as required by the preflight rule.

## Residual risk

Until a ruling lands and the implementation is completed, production default clients that share the same scope still share one manifest and can mistake live peer records for abandoned custody.
