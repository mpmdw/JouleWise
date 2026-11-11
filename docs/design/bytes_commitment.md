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
explicit `--commitment-repo` must resolve to the same Git toplevel as the running
script checkout. An unrelated checkout is refused before receipt or data reads.
`--stage1-receipt` defaults to `docs/bytes/stage1/push-receipt.json` there.

The check reads exactly:

- The selected checkout's Git objects and refs: the full supplied commit object,
  `HEAD`, refs under `refs/remotes/origin/`, the receipt's origin tip, commit
  committer time, the prediction/sidecar/source blobs at the supplied commit,
  and the retained Git history of the two metadata paths below. It never fetches.
  Global/system Git configuration and lazy object fetching are disabled.
- The named push receipt. Required fields are schema
  `joulewise.bytes_push_receipt.v1`, `stage1_commit`, repository-relative
  `predictions_path`, `origin_ref`, `origin_tip`, UTC `pushed_utc`,
  `github_activity_raw` (the exact JSON response) and `force_push: false`.
  `github_repository` must match the owner/repo in the local GitHub origin URL;
  the API path is derived from that origin, rather than gh's default repository.
  The saved activity must name a normal push to
  `refs/heads/records/2026-11-bytes-stage1`, with `after` equal to `origin_tip`.
  `pushed_utc` must equal that event's server `timestamp`. A force-push activity
  or true force flag refuses. GitHub's ordinary `activity_type: push` excludes
  force pushes even when the response has no separate boolean force flag.
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
estimator. Its committer timestamp and the recorded server push timestamp must precede
every heldout event/release timestamp; equality with an unblinding timestamp
refuses. The push timestamp cannot precede the commit or be in the future.
For every nonempty historical metadata revision, the commitment must also be a
**strict ancestor of that revision**. Backdating a new prediction commit cannot
repair an earlier committed unblinding record. Malformed/missing required
metadata refuses. Every journal event and heldout release must name the same
`stage1_commit`; an intact journal therefore refuses a replacement prediction
commit regardless of backdated clocks.

The journal contains one JSON object per line, with `event` (`heldout_rows`,
`heldout_keys`, or `heldout_analysis`), UTC `unblinded_utc`, and `stage1_commit`.
A guarded command locks the journal and requires its bytes to equal the regular
blob at `HEAD:docs/bytes/stage1/unblinding.jsonl`. It then checks, appends, flushes
and fsyncs an admission attempt
**before** opening heldout rows or keys. A later command failure leaves the
attempt recorded conservatively. After each append it prints the instruction to
commit and push the journal before another heldout command. A second admission
refuses until the previous line is committed; a truncated committed journal also
refuses. The twin forwards the external guard's diagnostic so the instruction
reaches its caller. Outputs retain the verification receipt,
including the push time, origin snapshots and analysis head.

## Operator sequence (future lead-controlled use only)

1. Reconcile any pre-existing unblinding metadata into the canonical journal
   before using this gate. Do not initialize a fresh empty history if an earlier
   attempt occurred. No code scans custody/data directories to discover records.
2. Before the original prediction commitment, create and track the empty
   `docs/bytes/stage1/unblinding.jsonl` if no heldout attempt has occurred. Copy
   `predictions.json`/`predictions.sha256` into that directory as the existing
   stage-1 plan specifies. Commit them from the registered estimator checkout.
3. The lead performs the authorized push to `records/2026-11-bytes-stage1` and
   refreshes the local origin ref. The lead reports GitHub ruleset
   `protect-records-branches` already protects `records/**` against deletion and
   non-fast-forward pushes. That server configuration was not queried in this
   offline implementation seat.
4. On the networked Air, run `python3 scripts/bytes_commitment.py record-push
   --stage1-commit HASH`. This command alone runs
   `git ls-remote origin refs/heads/records/2026-11-bytes-stage1` and requires
   exact equality with the local `origin_tip`. It obtains the push event with
   `gh api repos/{owner}/{repo}/activity?ref=refs/heads/records/2026-11-bytes-stage1&activity_type=push&per_page=100`.
   The event must be in that response; absent/ambiguous evidence refuses, so
   record it promptly after the push. No typed push timestamp is accepted.
   It exclusively creates and commits `push-receipt.json`, preserving the raw
   response. Push that receipt commit to the protected records branch before
   proceeding. The utility does not push or fetch. Its two network calls use an
   injectable runner; all tests use recorded synthetic responses.
5. `python3 scripts/bytes_commitment.py check --stage1-commit HASH` is read-only.
   Then use the existing post-commit analysis/twin/release commands, adding the
   real `--stage1-commit HASH` also to heldout analysis and twin stage 2.
   `--predictions` and its SHA sidecar must be supplied to heldout analysis; other
   commands default to the receipt locator. Preserve heldout `release.json` as
   `docs/bytes/stage1/heldout-release.json`. Commit and push the journal after
   **each** admission, including attempts whose downstream command failed. Never
   commit factors/keys. No stage-2 operation is authorized by this implementation
   handoff.

## Limits of this evidence

`record-push` obtains a live origin comparison and a GitHub server timestamp.
`check` and `admit` remain offline: they replay saved JSON and local origin refs,
without contacting GitHub or authenticating a hand-edited receipt independently.
The committed receipt, protected remote history, and journal are the durable
record; this is not a defense against an operator fabricating all local evidence.
Commit clocks are self-reported; journal commit identity and graph/history checks
provide the additional clock-independent anchors. Admission requires a local
journal commit but cannot verify its push offline; the printed push instruction
remains an operator duty. A fresh clone without an unpushed admission cannot
recover that line.
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
