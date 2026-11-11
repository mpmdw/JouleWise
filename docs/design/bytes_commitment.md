# BYTES original stage-1 commitment preflight (RL-7a)

The driver gate is `scripts/bytes_commitment.py`. It does not import or modify the
registered estimator. The one registered source file, used by all three
registered estimator functions in §13/§21, is `joulewise/bytes_analysis.py`, SHA-256
`18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`.

`bytes_analyze.py` checks before admitting post-commit blinded rows or running
heldout analysis. `bytes_twin.py` invokes the guard in a separate process before
those same reads; its arithmetic still imports only the standard library.
`b6_release_subset.py` checks before reading/copying BYTES heldout keys.
`b6_unblind.py` checks before its `--stage1-commit` path opens the export/store.
The digest-pinned library's low-level `stage1_commit` parameter is unchanged;
study commands must use these guarded entry points, not call that library as an
independent authorization mechanism.

## Evidence read, and what is checked

The analysis checkout defaults to the directory containing the scripts. An
explicit `--commitment-repo` selects the analysis Git checkout; it must name the
checkout whose analysis head is being asserted, not an unrelated custody repo.
`--stage1-receipt` defaults to `docs/bytes/stage1/push-receipt.json` there.

The check reads exactly:

- The selected checkout's Git objects and refs: the full supplied commit object,
  `HEAD`, refs under `refs/remotes/origin/`, the receipt's origin tip, commit
  committer time, the prediction/sidecar/source blobs at the supplied commit,
  and the retained Git history of the two metadata paths below. It never fetches.
  Global/system Git configuration and lazy object fetching are disabled.
- The named push receipt. Required fields are schema
  `joulewise.bytes_push_receipt.v1`, `stage1_commit`, repository-relative
  `predictions_path`, `origin_ref`, `origin_tip`, and UTC `pushed_utc`.
- The local prediction JSON (`--predictions`, otherwise the receipt locator) and
  adjacent `predictions.sha256`. Their bytes/digest must equal the committed
  regular blobs. The JSON's estimator digest must also equal the registered pin.
- The committed regular estimator blob, independently hashed against the pin.
- Current `docs/bytes/stage1/unblinding.jsonl` (required, possibly empty), current
  `docs/bytes/stage1/heldout-release.json` if present, and **every retained Git
  revision of both paths across all refs**, including deleted records. An
  analysis/twin invocation with `--key-dir` additionally checks that directory's
  `release.json` if present; `check`/`admit` accept explicit
  `--unblinding-record` metadata paths. Fit release records are ignored for
  chronology: fit keys must be released before predictions can be produced.

The object must itself be a commit, be an ancestor of the selected analysis
`HEAD`, and be reachable from the receipt's local origin ref. The receipt tip
must contain the commitment and remain an ancestor of the current origin tip.
The commitment must contain both frozen prediction blobs and the registered
estimator. Its committer timestamp and the attested push timestamp must precede
every heldout event/release timestamp; equality with an unblinding timestamp
refuses. The push timestamp cannot precede the commit or be in the future.
For every nonempty historical metadata revision, the commitment must also be a
**strict ancestor of that revision**. Backdating a new prediction commit cannot
repair an earlier committed unblinding record. Malformed/missing required
metadata refuses.

The journal contains one JSON object per line, with `event` (`heldout_rows`,
`heldout_keys`, or `heldout_analysis`), UTC `unblinded_utc`, and `stage1_commit`.
A guarded command locks, checks, appends, flushes and fsyncs an admission attempt
**before** opening heldout rows or keys. A later command failure leaves the
attempt recorded conservatively. Outputs retain the verification receipt,
including the push time, origin snapshots and analysis head.

## Operator sequence (future lead-controlled use only)

1. Reconcile any pre-existing unblinding metadata into the canonical journal
   before using this gate. Do not initialize a fresh empty history if an earlier
   attempt occurred. No code scans custody/data directories to discover records.
2. Before the original prediction commitment, create and track the empty
   `docs/bytes/stage1/unblinding.jsonl` if no heldout attempt has occurred. Copy
   `predictions.json`/`predictions.sha256` into that directory as the existing
   stage-1 plan specifies. Commit them from the registered estimator checkout.
3. The lead performs the authorized push and refreshes/verifies the local origin
   ref. Record the actual UTC push time. No push/fetch is performed by the guard.
4. Run `python3 scripts/bytes_commitment.py record-push --stage1-commit HASH
   --pushed-utc UTC_TIME --origin-ref refs/remotes/origin/records/2026-11-bytes-stage1`.
   It checks the evidence before exclusively creating `push-receipt.json`.
   Preserve that receipt with the commitment records.
5. `python3 scripts/bytes_commitment.py check --stage1-commit HASH` is read-only.
   Then use the existing post-commit analysis/twin/release commands, adding the
   real `--stage1-commit HASH` also to heldout analysis and twin stage 2.
   `--predictions` and its SHA sidecar must be supplied to heldout analysis; other
   commands default to the receipt locator. Preserve heldout `release.json` as
   `docs/bytes/stage1/heldout-release.json` and preserve/commit the journal. Never
   commit factors/keys. No stage-2 operation is authorized by this implementation
   handoff.

## Limits of this evidence

Git has no authenticated push timestamp. `pushed_utc` is explicitly an operator
attestation, and local origin refs are an offline snapshot, not a query of the
server. The lead must verify freshness and the actual push time before study
use. Commit clocks are also self-reported; the additional graph/history check
protects against ordinary retrospective mistakes, not a dishonest operator.
The check covers the named metadata inventory, not events omitted from it or
Git objects no longer reachable from any ref. It reads no archive, outcome,
withheld store or blinding factor. A successful fixture check is not evidence
that a real commitment exists or that heldout custody has been reviewed.

This gate validates the **original registered** commitment. A changed evaluator
may still evaluate those original lines with the registration's provenance
flags. It cannot substitute predictions carrying an unregistered estimator
hash. The separately labelled post-agreement second-commitment procedure in
§11 needs its own lead disposition; this gate does not relabel it as a blind
original commitment or erase earlier unblinding history.
