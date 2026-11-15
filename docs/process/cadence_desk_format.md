# Desk bundle, transition record and desk verdict: the one contract (desk ↔ queue controller)

RL-172 §(c) and §(g); RL-149 §2.8 line 9 (k+2). The lead's decision of 15 Nov: this file is the single
contract, and the queue controller (#800) conforms to it. The desk side lives in #799:
- `joulewise/cadence/desk_final.py` packs, judges and verifies a verdict;
- `joulewise/cadence/desk_transport.py` signs, verifies and publishes;
- `scripts/air/cadence_desk.py` is the CLI.

The scratch copy at `/Volumes/JW-EXT/scratch/desk-final/FORMAT.md` is this file, byte for byte.

## 0. Keys and principals

| Principal | Key lives on | Signs | Verified by |
|---|---|---|---|
| `cadence-controller` | MBP (controller config `signing_key`) | bundle commits | Air: `allowed_signers` naming this key |
| `cadence-desk` | Air | verdict commits | MBP controller: `verdict_signers` naming this key |

Both use SSH signatures (`gpg.format=ssh`, namespace `git`). Allowed-signers lines read
`<principal> namespaces="git" <public key>`. A signature by any other principal is a refusal.

## 1. The bundle (MBP → Air)

**Ref:** `refs/heads/desk-bundles/<plan_id>`. It holds **one parentless commit**, SSH-signed by
`cadence-controller`. Its subject is exactly `cadence close bundle <plan_id>`. It is created once; a different
tree for the same plan id is a controller refusal.

**Tree.** It holds exactly these entries, all regular blobs (mode 100644), and nothing else:

```
transition.json
bundle/BUNDLE_MANIFEST.json
bundle/runner_receipt.json                 # verbatim <span output>/runner_receipt.json
bundle/span_plan.json                      # verbatim <span output>/span_plan.json (absent only if the span refused before its plan)
bundle/legs/<leg_id>/leg_summary.json      # verbatim from <span output>/desk-bundle/
bundle/span/result.json                    # verbatim from <span output>/desk-bundle/
bundle/span/meter.json                     # verbatim from <span output>/desk-bundle/
```

- There are no runtime dirs, `hazards/`, meter stream, journals, soak reference, maintenance log or symlinks.
- Anything outside this shape is refused **before any blob is read**, on both sides:
  - the packer, `desk_final.pack_bundle` and `desk_transport.sign_bundle`, refuses to read it;
  - the Air, `desk_transport.extract_bundle`, refuses the commit.
- A rejected input is never shipped (Sol 2).

**`bundle/BUNDLE_MANIFEST.json`** (schema `joulewise.cadence_desk_bundle.v1`). The required keys are closed;
`producer` and `controller` are optional free objects, which are scanned for denied keys.

```json
{"schema": "joulewise.cadence_desk_bundle.v1",
 "plan_id": "cq-<span_id>-a<attempt>", "queue_id": "cq-...", "span_id": "...", "attempt": 1,
 "kit": {"path": "<queue entry kit.path>", "sha256": "<queue entry kit.sha256>",
         "campaign_id": "<kit campaign_id>", "frozen_commit": "<kit frozen.commit>"},
 "receipt": {"path": "runner_receipt.json", "sha256": "<= files['runner_receipt.json']>"},
 "files": {"<path relative to bundle/>": "<sha256 of its bytes>", "...": "every bundle file except the manifest"},
 "reference": null | {"capture_leg": "<roster[0]>", "attempt": <its accepted attempt>,
                      "record_sha256": null | "<the capture's reference record sha256>"},
 "producer": {"...": "free strings"}, "controller": {"...": "free"}}
```

- **Packer.** Build it with `desk_final.pack_bundle(span_dir, bundle_dir, plan_id=, queue_id=, span_id=,
  attempt=, kit=, roster=, reference_record_sha256=None, producer=None)`. There is one packer, one allowlist
  and one layout.
- **Identities** come from the queue entry the controller armed and the kit it pinned, never from the receipt.
- **`reference`** is filled by the packer whenever a leg consumed a span reference. `record_sha256` is
  optional. When present, every consumer's `g0_reference_record_sha256` must equal it. Either way, every
  consumer's `g0_reference_source` must name the capture's accepted run (Sol 1).

**`transition.json`**: the controller's per-span transition record (RL-172 (g) 8). It is the anchor.

```json
{"schema": "joulewise.cadence_controller_transition.v1",
 "plan_id": "...", "queue_id": "...", "span_id": "...", "attempt": 1,
 "queue": {"path": "<path on the audit branch>", "sha256": "<queue file bytes>", "commit": "<audit commit armed from>"},
 "kit": {"path": "...", "sha256": "..."},
 "plan_sha256": "<sha256 of bundle/span_plan.json>",
 "arm_proof_sha256": "...", "arm_command_sha256": "...", "close_proof_sha256": "...",
 "status": "CLOSED_OK | STOPPED | REFUSED | STRANDED | CLOSE_UNPROVEN",
 "manifest_sha256": "<sha256 of bundle/BUNDLE_MANIFEST.json>", "t0_epoch": 0, "receipt_epoch": 0}
```

- These keys are required. Extra keys (for example `soak_attempts`) are allowed and ignored, as long as they
  pass the denied-key scan.
- `desk_transport.sign_bundle(repo, bundle_dir, transition, plan_id=, signing_key=)` sets `manifest_sha256`
  itself and builds the commit.
- **The Air checks:**
  - the signature;
  - the subject;
  - that the manifest hashes to `manifest_sha256`;
  - that `plan_id`, `queue_id`, `span_id`, `attempt` and the kit sha match the queue entry;
  - that the queue bytes hash to `queue.sha256` (by default the Air reads the queue from
    `queue.commit:queue.path`);
  - that `span_plan.json` hashes to `plan_sha256`.
- A `status` other than `CLOSED_OK` is a REFUSAL in the verdict, which holds the next arm.

**A refused or faulted span still gets a bundle**, provided its receipt is readable. A negative result is
also a receipt.

## 2. What the Air runs

```
git fetch origin '+refs/heads/desk-bundles/*:refs/remotes/origin/desk-bundles/*' \
                 '+refs/heads/<audit branch>:refs/remotes/origin/<audit branch>'
python3.13 -B scripts/air/cadence_desk.py final --plan-id PLAN --repo CLONE \
    --bundle-ref refs/remotes/origin/desk-bundles/PLAN --allowed-signers SIGNERS --kit KIT.json --out DIR \
    --history-prefix refs/remotes/origin/cadence-desk-final/ [--hand-table hand_table.json] [--hand-sample]
python3.13 -B scripts/air/cadence_desk.py publish --plan-id PLAN --out DIR --repo CLONE --signing-key AIR_KEY
```

- **Lock.** `final` runs under `AIR-QUIET.lock` and always writes `DIR/desk_verdict.json`. When the bundle
  can be read it also writes `JOURNAL-TABLE.md`, `desk_summary.json` and `stops.json`.
- **Exit codes:**
  - 0: final and nothing held;
  - 3: not final, or a hold;
  - 1: the desk refused or erred (a verdict is still written);
  - 4: the lock is busy (no verdict, retry);
  - 2: usage.
- **History.** `--history-prefix` rebuilds the campaign's earlier summaries from the signed verdict records.
  `--history FILE` is accepted, and the verdict then says `history_source: "file"`.
- **Synthetic runs.** `--bundle DIR --manifest-sha256 HEX --allow-unsigned --queue Q` judges an unsigned
  directory; that verdict says `transport.signed: false` and never counts. `--allow-mock` accepts a mock
  receipt, and that verdict says `mock: true` and never counts.

## 3. The verdict (Air → MBP)

**Ref:** `refs/heads/cadence-desk-final/<plan_id>`, written by `cadence_desk.py publish` on the Air
(`desk_transport.publish_verdict`).
- **Commit:** SSH-signed by `cadence-desk`, with subject `cadence desk verdict <plan_id>` and the trailers
  `Verdict-SHA256: <hex>` and `Desk-Final: true|false`.
- **Tree:** `desk_verdict.json` and `desk_summary.json`.
- **Later judgments** of the same plan, such as after a hand table arrives, are child commits, so the ref
  only moves forward. The tip is the current verdict.
- **Why a ref per plan, not the audit branch:** the Air never pushes to the lead's branch (no
  non-fast-forward races), and a verdict cannot be edited in place.

**`desk_verdict.json`** (schema `joulewise.cadence_desk_verdict.v1`):

```json
{"schema": "joulewise.cadence_desk_verdict.v1", "plan_id": "...", "queue_id": "...", "span_id": "...", "attempt": 1,
 "desk_final": true, "reasons": ["CODE: detail"], "named_stops": [{"code", "kind", "detail"}],
 "pending": [{"code": "HAND_TABLE_DUE", ...}], "next_arm_hold": false,
 "holds": [{"code", "scope": "queue" | "kit:<campaign_id>", "cleared_by", "gate"?}],
 "hand_gates": [{"gate", "status": "hand gate required", "ruling", "holds", "why", "print"}],
 "hand_table": {"required", "triggers", "supplied", "agrees", "problems", "differences", "sample"},
 "identities": {"kit_sha256", "campaign_id", "frozen_commit", "roster", "capture_leg", "manifest_sha256", "receipt_sha256"},
 "transport": {"signed", "bundle_commit", "signer", "queue_commit"}, "history_source": "signed-records|file|none",
 "mock": false, "summary_sha256": "...", "opened": [...], "error": null, "desk_code": {...}, "built_at": "...",
 "verdict_sha256": "<sha256 of the canonical JSON of every other key>"}
```

- **Canonical JSON:** `json.dumps(body, sort_keys=True, separators=(",", ":"))`, in UTF-8.
- **Stable gate names:** `class A smoke hand-read`, `L002 consumer gate`, `L005 consumer gate`,
  `RL-158 Q1 reference print`.

**Codes:**

| Kind | Codes | Effect |
|---|---|---|
| integrity | `DESK_UNAUTHENTICATED`, `DESK_IDENTITY`, `DESK_ROSTER`, `DESK_NO_LEG_ROWS`, `DESK_DUPLICATE`, `DESK_ATTEMPTS`, `DESK_SCHEMA`, `DESK_FEED_PROOF`, `DESK_REFUSAL`, `DESK_ERROR` | not final; holds |
| operational | `REFUSAL`, `INSTRUMENT_FAULT`, `CONTAMINATED_REDOS`, `LEG_OVERTIME` | holds; the record may still be final |
| hand | `HAND_TABLE_DISAGREES`, `HAND_TABLE_INVALID` | not final; holds |
| pending | `HAND_TABLE_DUE` | not final; no hold |

REFUSAL includes each of these:
- a receipt rc other than 0, or an error;
- a missing or failed restore;
- any failed stage, except a refused soak that was retried and the runner's non-fatal `display`;
- no accepted soak;
- a transition `status` other than `CLOSED_OK`.

**The soak.** Receipts from pins with RL-171's retry carry `soak_attempts`. A `soak` stage with rc ≠ 0
followed by an accepted `soak.a2` is a completed soak; it is never read as a stop, and it puts the span on
the hand table (RL-172a). Receipts from the development pins (`b4b6aeb19`, `2d347f721`) carry no such
field: exactly one `soak` stage with rc 0 is one accepted soak, and a `soak.a<k>` stage without the field
is `DESK_ATTEMPTS`. The refusal text and its kind (`slope`, `load`, `settle_or_quiet`) are kept in
`desk_summary.json` and the hand gate's print.

## 4. What the controller must do with it

1. **k+2 (line 9).** Read the verdict with `desk_transport.read_verdict(repo, ref, allowed_signers=, plan_id=)`.
   It checks the signature by `cadence-desk`, the subject, both trailers, `verify_verdict`, the plan id and
   the summary hash. Then apply `desk_final.counts_as_final(doc, plan_id=, queue_id=, span_id=, attempt=,
   manifest_sha256=<the transition record's>)`. With `allow_mock=True`, which is for synthetic runs only, it
   also admits `mock: true`. It requires:
   - `desk_final: true`;
   - `mock: false`;
   - `transport.signed: true`;
   - the exact identities and anchor.

   A verdict that is missing, unreadable, unsigned, mismatched or false is **not final**. Never default to
   final, and never reuse a verdict across plan ids.
2. **Holds.** `next_arm_hold: true` (any named stop) holds the next arm of the queue until the lead's
   disposition record. A `kit:<campaign_id>` hold (a hand gate) holds that kit's next span until the lead's
   gate record.
3. **Derive the gates; do not wait for the verdict.** The next span can arm 300 s after a close, so the
   controller derives the hand gates at the close:
   - the consumer gates from `desk_final.consumer_gates(campaign_id, kit_legs, roster)`, which uses
     `CONSUMER_GATES`;
   - class A from "the roster holds the kit's first leg".

   A verdict naming a gate the controller did not derive is a disagreement and halts.
4. **Across queues.** The k+2 debt is counted in machine order across queues (RL-172 (g) 2).
5. **Not-final spans.** A span that is not desk-final (for example, refused with fewer legs than its roster)
   leaves the k+2 count only through the lead's disposition (`rerun` or `withdrawn`). A re-run is a new
   plan id with `attempt + 1`. The desk refuses a receipt already judged under another plan id.

## 5. The hand table and the seeded draw

- **When it is mandatory.** A hand table is mandatory on:
  - a redo;
  - an exclusion;
  - a retried soak;
  - a schema change (no earlier summary, or a different kit schema or leg-field set);
  - a span selected by the seeded draw;
  - a span the lead selects (`--hand-sample`).
- **Until it is supplied** the verdict is `HAND_TABLE_DUE`.
- **`hand_table.json`** (schema `joulewise.cadence_hand_table.v1`) needs `plan_id`, `legs`, `named_stops`
  (a list of codes) and `soak_attempts` (a count). Every row carries `leg_id`, `attempts`,
  `contaminated_redos`, `g0_outcome`, `g0_s`, `wall_s`, `band_reached` and `admitted`; v1.1 rows also carry
  `g0_role` and `span_reference`.
- **Comparison.** A missing, duplicate, mistyped or non-finite field makes the table `HAND_TABLE_INVALID`.
  Every field is compared, seconds within 1.0 s.
- **The draw** (`sha256-hand-sample-v1`, seed 2026111501, block 4) is fixed in code before any span it
  selects has run.
  - The stratum is the kit sha256 and the span's G0 shape (`span` if a leg after the first consumes, else
    `own`).
  - A queue's spans in a stratum, in seq order, fall in blocks of four; the last block may be shorter.
  - In each block exactly one position is drawn from sha256 of the law, the seed, the queue id, the stratum
    and the block.
  - `cadence_desk.py sample-plan --queue Q --kit K` prints the selection at READY, so it is prospective.
