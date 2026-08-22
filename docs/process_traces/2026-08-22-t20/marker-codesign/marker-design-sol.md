<!-- Seat: Sol (gpt-5.6-sol, xhigh, read-only MCP, blind) -->
<!-- Thread: 01a02b69-4c97-7a11-9ab6-5b37b50a7981 -->
<!-- BASE_HEAD: 73764f0169c196363d986925a8305a4c3a5ba524 (= 1ba04a8 + D-150 rulings commit) -->
<!-- Envelope: DISCUSSION, pathspec [], flags [no_edits, read_only, blind_seat] — protocol-valid -->

# `_v4` Family Publication Marker Design — Blind Seat

## Positions

### 1. Marker schema v1

The marker is one custody-external, family-boundary artifact. It is built only after all three `_v4` packs and their `freeze-0004` receipts are final. It never lives inside a pack or the Git tree.

Normative schema identifier:

```text
joulewise.d117_family_publication_marker.v1
```

The marker uses strict D-134 canonical JSON: UTF-8, duplicate keys forbidden, non-finite numbers forbidden, lexicographically sorted object keys, two-space indentation, and one trailing newline. Its companion is a GNU SHA-256 sidecar:

```text
<64 lowercase hex><two spaces>d117_family_publication_v4.json\n
```

#### Exact top-level field set

| Field | Type | Required value or invariant |
|---|---|---|
| `schema_version` | string | Exactly `joulewise.d117_family_publication_marker.v1` |
| `marker_kind` | string | Exactly `FAMILY_PUBLICATION` |
| `family_id` | string | Exactly `d117-v4` |
| `family_generation` | integer | Exactly `4`; booleans are invalid |
| `publication_state` | string | Exactly `PUBLISHED`; this assertion is authoritative only with the confirmation record described below |
| `publication_git` | object | Exact final publication checkout |
| `common_evidence_git` | object | Common derivation coordinate authenticated across the three receipts' generic evidence |
| `lifecycle_registry` | object | Exact installed R1 registry reference and FAMILY_PUBLICATION vocabulary |
| `members` | array | Exactly three entries, ordered `ALPHA`, `BETA`, `GAMMA` |
| `authoring_context` | object | Deterministic construction provenance |
| `assurance` | object | Exact D-120 qualifier |

No unknown or omitted key is accepted at any nesting level.

#### `publication_git`

Exact keys:

```text
head_commit
head_tree_oid
local_main_commit
origin_main_commit
clean
exact_match
```

The four commit values are lowercase 40-hex Git OIDs, with:

```text
head_commit == local_main_commit == origin_main_commit
clean is true
exact_match is true
```

`head_tree_oid` is the tree OID of `head_commit`. The consumer recomputes every value at consult time. Matching the tree alone is insufficient: a different commit with the same tree still refuses.

#### `common_evidence_git`

Exact keys:

```text
head_commit
head_tree_oid
```

The builder authenticates all generic evidence referenced by the three `freeze-0004` receipts, collects their `derivation_commit` values, and requires one unique value. `head_tree_oid` is resolved locally from that commit. A mixed-head three-pack family therefore cannot be marked published.

#### `lifecycle_registry`

Exact keys:

```text
path
schema_version
registry_id
sha256
lifecycle_registry_id
family_publication_marker_schema
family_publication_refusal
```

Required values:

```text
path                              configs/arm_readiness/d117_row_registry_v2.json
schema_version                    joulewise.arm_readiness_row_registry.v2
registry_id                       d117-row-registry-v2
lifecycle_registry_id             d117-r1-lifecycle-v1
family_publication_marker_schema  joulewise.d117_family_publication_marker.v1
```

`family_publication_refusal` has exact keys and values:

```json
{
  "code": "readiness_r1_family_publication",
  "role": "FAMILY_PUBLICATION",
  "type": "CUSTODY"
}
```

This spelling follows the surviving V4 ruling and its CUSTODY allocation (`docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING.md`, V4, lines 84–93; `v4-plan-ruling-r4draft.md`, r4-5, lines 81–91). The marker consumer must obtain the entry from the authenticated registry and then compare it with these exact values; it must not hardcode a fallback that could remain usable when the registry is malformed.

#### `members`

Each entry has this exact key set:

```text
profile
pack_id
pack_path
pack_digest_algorithm
pack_sha256
plan_tree
frozen_plan
freeze_receipt
```

The array is exactly:

| Profile | Exact `pack_id` | Exact `pack_path` |
|---|---|---|
| `ALPHA` | `d117_floor_qwen25_1p5b_v4` | `configs/campaigns/d117_floor_qwen25_1p5b_v4` |
| `BETA` | `d117_floor_qwen25_7b_v4` | `configs/campaigns/d117_floor_qwen25_7b_v4` |
| `GAMMA` | `d117_contrast_qwen25_1p5b_vs_7b_v4` | `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4` |

`pack_digest_algorithm` is exactly:

```text
joulewise.committed_pack_tree_sha256.v1
```

`pack_sha256` is the existing domain-separated committed-pack digest over every committed relative path, mode, length, and blob SHA-256. The builder and consumer use `committed_pack_tree_sha256`; neither reimplements its framing.

`plan_tree` has exact keys:

```text
path
sha256
sidecar_path
sidecar_sha256
```

with paths exactly `plan_tree.json` and `plan_tree.sha256`. `sha256` hashes `plan_tree.json`; `sidecar_sha256` hashes the sidecar bytes themselves.

`frozen_plan` has exact keys:

```text
plan_id
window_id
path
sha256
```

These values are derived from the authenticated plan tree and must equal the freeze receipt's `pack_identity`.

`freeze_receipt` has exact keys:

```text
schema_version
receipt_id
ordinal
path
sha256
sidecar_path
sidecar_sha256
status
```

Required constants are:

```text
schema_version  joulewise.arm_readiness_freeze_receipt.v2
receipt_id      freeze-0004
ordinal         4
path            arm_readiness.freeze.receipts/freeze-0004.json
sidecar_path    arm_readiness.freeze.receipts/freeze-0004.json.sha256
status          PASS
```

The consumer parses `receipt_id` independently and requires its parsed ordinal to equal `ordinal`. It authenticates the receipt and sidecar, checks the plan-tree attachment points to the same receipt digest, validates the v2 schema and predecessor chain, and performs the existing semantic replay with `require_pass=True`.

#### `authoring_context`

Exact keys:

```text
transaction_id
source_commit_time_utc
construction_phase
custody_class
builder
consumer
```

Required derived values:

```text
transaction_id      d117-v4@<publication_git.head_commit>
construction_phase  POST_FREEZE_FAMILY_BOUNDARY
custody_class       TRANSACTION_EXTERNAL
```

`source_commit_time_utc` is the publication commit's committer timestamp normalized to UTC, not the wall-clock time at which the script happened to run. This preserves deterministic marker bytes.

`builder` and `consumer` each have exact keys `path` and `sha256`, naming:

```text
scripts/build_family_marker.py
scripts/verify_family_marker.py
```

The SHA-256 is computed over the blob at the publication commit. Each script also self-hashes at execution and refuses if its executing bytes differ from the committed blob.

`assurance` is exactly:

```json
{
  "independent_attestation": false,
  "model": "single_authority_hash_bound_replay.v1"
}
```

The later Ed confirmation is distinct from this construction assurance.

#### Digest bindings and detected attacks

| Binding | What it covers | Detects |
|---|---|---|
| Marker `.sha256` | Every canonical marker byte | Any isolated marker edit, reordering, truncation, or replacement |
| `publication_git` commit + tree | Published repository coordinate | Wrong checkout, moved main, same-tree/different-commit substitution, post-publication commit |
| Registry SHA plus IDs and schema token | Exact installed R1 authority | Registry replacement, typoed or inert marker schema, wrong refusal spelling/type, wrong successor mapping |
| Exact three-member set | Family completeness | Missing, extra, duplicate, role-swapped, `_v3`/`_v4`-mixed, or unrelated pack |
| `pack_sha256` | All committed bytes, paths, and executable modes in each pack | Any final-pack mutation, extra/missing file, worktree/commit disagreement, or mode change |
| Plan-tree and sidecar hashes | Frozen attachment graph | Plan-tree swap, freeze-slot retarget, sidecar-only corruption |
| Frozen-plan SHA and identity | Executable plan selected by each pack | Wrong plan, plan ID/window ID substitution |
| Freeze receipt SHA, sidecar, ID, ordinal, and replay | Exact `freeze-0004` receipt and its authenticated evidence/predecessor semantics | Wrong generation, receipt swap, REFUSE receipt, edited receipt, altered predecessor, receipt/plan mismatch |
| `common_evidence_git` | One derivation coordinate across all three packs | Family assembled from independently authored or stale heads |
| Tool SHA fields | Reviewed constructor and consumer bytes | Running an unreviewed custody copy of either helper |
| Confirmation record and its sidecar | Ed's yes over the marker digest and exact member summary | Candidate presented as published, marker substituted after confirmation, wrong-head confirmation |
| Scheduler and GO receipt fan-out | Marker/verification digest at pre-arm and T-0 | External-custody replacement between publication, arm, and launch |

A coherent attacker who rewrites the marker, sidecar, confirmation, all downstream custody receipts, and the relevant Git refs is outside the current detectability threat model. This mechanism is hash-bound detectability, not signed integrity, consistent with the truth boundary in `docs/contracts/receipt_histsem_verifier.md`, lines 125–133.

### 2. Builder contract — `build_family_marker.py`

#### CLI

```bash
python3 scripts/build_family_marker.py \
  --repository <repository-root> \
  --head <full-40-hex-publication-head> \
  --pack-root configs/campaigns/d117_floor_qwen25_1p5b_v4 \
  --pack-root configs/campaigns/d117_floor_qwen25_7b_v4 \
  --pack-root configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4 \
  --output <external-custody>/d117_family_publication_v4.json
```

The three `--pack-root` arguments may arrive in any order; the builder derives profiles and emits the fixed `ALPHA`, `BETA`, `GAMMA` order. Pack roots must be normalized repository-relative paths. `--output` must be absolute and outside the repository and all pack roots. The adjacent `.sha256` path is implied.

This preserves the S-0 §3.8 input shape while making the marker instance external (`s0-runsheet.md`, lines 460–475).

#### Determinism

The builder:

- reads no wall clock, randomness, hostname, username, environment-specific absolute pack path, or network state into the marker;
- performs no fetch, unshallow, repair, or Git mutation;
- derives authoring time from the named commit;
- derives `transaction_id` from the family ID and full publication head;
- sorts every derived collection under the schema's fixed ordering;
- emits canonical bytes through the shared D-134 renderer;
- produces byte-identical marker and sidecar outputs for identical repository bytes and arguments, regardless of pack-argument order or output directory.

A repeated build into a different empty custody directory must compare byte-for-byte equal. Existing output is never overwritten.

#### Required input authentication

Before writing, the builder must:

1. Require `--head` to equal `HEAD`, local `main`, and `origin/main`; require a clean worktree and record the matching tree OID.
2. Require all pack roots to resolve inside the same repository and at the same commit.
3. Load the v2 row registry from its code-owned path with `require_resolved=True`.
4. Require its successor mapping to be exactly the three marker members.
5. Require the real marker-schema token and exact FAMILY_PUBLICATION refusal entry.
6. Authenticate each pack through the existing pack record, plan-tree, registry-reference, and freeze-replay functions.
7. Require exactly one plan-pinned `freeze-0004` receipt per pack, status `PASS`, v2 schema, ordinal 4, valid sidecar, and a matching plan-tree attachment.
8. Require all three freeze receipts to reference the same outer registry bytes and correct profile.
9. Require one common generic-evidence derivation commit and resolve its tree.
10. Require executing builder and consumer bytes to equal their committed blobs.

#### Refusal conditions

The builder refuses without a successful marker result for:

- dirty, detached-from-main, unpublished, unavailable, or mismatched Git state;
- pack roots from different repositories or heads;
- missing, extra, duplicate, incorrectly named, or incorrectly profiled packs;
- unresolved, malformed, wrong-path, wrong-ID, wrong-SHA, or wrong-schema registry state;
- marker token other than the exact v1 schema;
- missing or non-CUSTODY FAMILY_PUBLICATION entry;
- missing, extra, unpinned, malformed, REFUSE, wrong-ordinal, or wrong-schema freeze receipt;
- receipt/sidecar, receipt/plan, receipt/registry, pack/plan, or predecessor mismatch;
- mixed evidence derivation heads;
- pack digest failure, untracked pack entry, symlink, special file, or committed/worktree byte disagreement;
- executing tool bytes differing from the committed tooling;
- output inside the Git tree, an escaping/symlinked output path, an existing output or sidecar, or any no-clobber/durability failure.

Writes are create-only, regular-file, no-follow operations. The marker is file-fsynced before its sidecar; the sidecar and parent directory are then fsynced. If a crash leaves only one candidate file, it is preserved as incomplete custody and a new candidate directory is used—no repair-in-place or overwrite.

Exit behavior is:

- `0`: canonical PASS build report on stdout;
- `2`: governed REFUSE report, no traceback;
- no other exit is treated as success.

The build report includes marker path/SHA, sidecar path/SHA, family ID, head commit/tree, and `status`.

### 3. Consumer contract — `verify_family_marker.py` and gate integration

#### CLI

```bash
python3 scripts/verify_family_marker.py \
  --repository <repository-root> \
  --marker <external-marker.json> \
  --phase candidate
```

Published modes are:

```bash
python3 scripts/verify_family_marker.py \
  --repository <repository-root> \
  --marker <external-marker.json> \
  --confirmation <external-confirmation.json> \
  --phase publication|pre-arm|t0 \
  --receipt-out <external-verification-receipt.json> \
  [--target-pack-root <one exact v4 pack root>]
```

`candidate` forbids treating the result as publication authority. Its result may be `PASS`, but carries `publication_authorized: false`. The S-0 clone proof uses this mode.

`publication`, `pre-arm`, and `t0` require the confirmation and produce `publication_authorized: true` only after every live check passes. Production gate call sites must always supply one of these explicit published phases; a grep/static-call test rejects any gate use of candidate mode.

#### Confirmation record

Because the marker candidate must exist before Ed's exact-byte yes, the marker cannot digest-bind a later confirmation without changing the bytes Ed reviewed. Publication therefore requires a separate external record:

```text
joulewise.d117_family_publication_confirmation.v1
```

Its exact fields are:

```text
schema_version
receipt_kind
family_id
verdict
confirmed_by
confirmed_at_utc
publication_git
marker
members
```

Required constants are:

```text
receipt_kind  family_publication_confirmation
family_id     d117-v4
verdict       YES
confirmed_by  Ed
```

`publication_git` contains the marker's head commit and tree. `marker` contains the basename and SHA-256 of the exact marker. `members` is the exact ordered three-row human-visible table of `{profile, pack_id, pack_sha256, freeze_receipt_sha256}` and must match the marker. The confirmation uses canonical JSON and a GNU sidecar.

The marker's `PUBLISHED` assertion becomes authoritative only when this confirmation and sidecar exist and validate. This preserves the required order: marker candidate, Ed exact-byte yes, then publication (`MAGISTRATE-RULING-r2.md`, A-5.1, lines 90–95; `v4-plan-ruling-r4draft.md`, r4-3, lines 46–57).

#### Verification algorithm

Every published-phase consultation independently:

1. Loads and validates the current resolved R1 registry before interpreting marker failure.
2. Reads marker and sidecar as non-symlink regular files outside the Git tree.
3. Requires exact sidecar bytes and strict canonical JSON.
4. Validates every exact field, constant, set, order, and type above.
5. Recomputes live `HEAD`, tree, local main, origin main, cleanliness, and exact match.
6. Requires the marker's publication coordinate to equal that live coordinate.
7. Authenticates current registry bytes and the exact marker-schema/refusal values.
8. Derives the expected three members from the registry, never from directory scanning alone.
9. Recomputes every pack, plan, sidecar, receipt, and common-head binding.
10. Performs full freeze semantic replay with `require_pass=True`.
11. In published phases, validates the confirmation and sidecar and requires its marker/head/member summary to match.
12. If a target pack is supplied, requires its resolved identity to be exactly one marker member.
13. Writes a verification receipt and sidecar only after evaluation completes.

The verification receipt schema is `joulewise.d117_family_publication_verification.v1`, with exact fields:

```text
schema_version
receipt_kind
phase
checked_at_utc
status
publication_authorized
family_id
marker
confirmation
consulted_git
checks
refusals
detail
assurance
```

`confirmation` is `null` only in candidate mode. Each `checks` item has exact keys `{check_id, status}`. On a marker-boundary refusal, `refusals` contains exactly the registry-derived FAMILY_PUBLICATION refusal object; `detail` identifies the failed check but is not another reason code.

#### Refusal vocabulary

There is exactly one publication-boundary reason:

```text
role  FAMILY_PUBLICATION
code  readiness_r1_family_publication
type  CUSTODY
```

Missing marker, missing sidecar, malformed marker, incomplete family, wrong head, wrong pack, wrong receipt, failed replay, missing confirmation, confirmation mismatch, and custody-path violations all emit that code/type. Diagnostic `check_id` values distinguish the cause without multiplying externally visible reason codes.

A registry that cannot itself be authenticated refuses under its existing registry-owned `readiness_row_registry_mismatch`/structural path; the consumer must not fabricate the FAMILY_PUBLICATION entry when its authority source cannot be loaded.

All failures are fail-closed:

- no marker or confirmation is equivalent to unpublished;
- malformed or unknown fields never degrade to warnings;
- no "best matching" family is selected;
- a marker for another generation cannot authorize `_v4`;
- a PASS freeze receipt is still fully replayed;
- no flag bypasses confirmation, live-head equality, or member authentication.

#### Scheduler integration

No individual G1–G6 gate owns publication, and G6 must not be overloaded: G6 already owns D-149 C1–C5. Publication is a parallel scheduler pre-arm conjunct, evaluated in the same invocation while all six ruled gates still run.

The current scheduler receipt v1 is exact-key enforced, so production binding requires:

```text
joulewise.window_scheduler_gate_receipt.v2
```

It adds one root field, `family_publication`, with exact keys:

```text
family_id
marker_sha256
confirmation_sha256
verification_receipt
verdict
refusals
```

`verification_receipt` is `{path, sha256}`. Marker or confirmation SHA may be `null` only on REFUSE because the file was unavailable.

Rules:

- G5 remains first; all six G gates evaluate even if family publication refuses.
- `SCHEDULER_GATE_REASON_CODES` remains unchanged.
- The nested refusal is validated against the R1 lifecycle registry and is not unioned into scheduler reason codes.
- Scheduler `GO` requires all six G verdicts to be `PASS`/`RECORD_ONLY` **and** `family_publication.verdict == PASS`.
- `claim_admissible` is false whenever publication fails.
- Both SHAKEDOWN and CLAIM windows require publication; r4 orders publication before shakedown.
- The evaluator writes no pack or repository bytes.

This version bump is the honest consequence of the current strict v1 receipt shape, not an Ed-policy change. It belongs to this D-144 contract round and its magistrate adjudication. Smuggling the binding into the open-ended `assurance` object is rejected.

#### T-0 and launch integration

Pre-arm verification is necessary but not sufficient because the marker is external custody and the repository head may move.

At T-0, the D-149 evaluator re-runs published verification immediately before issuing GO. Under C2, the GO receipt binds:

```text
marker path + sha256
confirmation path + sha256
pre-arm family verification receipt path + sha256
T-0 family verification receipt path + sha256
window scheduler gate receipt path + sha256
```

The five D-149 conditions remain unchanged; publication is a C2 arm-admission prerequisite rather than a new C6.

`launch_window.py`'s ruled scheduler-receipt enforcement must accept only scheduler receipt v2 for `_v4`, validate the referenced family verification receipt, and re-hash the marker and confirmation immediately before capability consumption. It need not repeat the complete pack walk at `execve`; the T-0 verifier did that, while the final hash comparison closes accidental external-file replacement between verification and consumption.

### 4. Custody convention

Let `$V4_TRANSACTION_CUSTODY_ROOT` be a lead-selected directory outside every Git worktree and pack root.

Canonical layout:

```text
$V4_TRANSACTION_CUSTODY_ROOT/
  family-publication/
    d117-v4/
      candidate/
        d117_family_publication_v4.json
        d117_family_publication_v4.json.sha256
        candidate-verification.json
        candidate-verification.json.sha256
      published/
        d117_family_publication_v4.json
        d117_family_publication_v4.json.sha256
        family_publication_confirmation_v1.json
        family_publication_confirmation_v1.json.sha256
        publication-verification.json
        publication-verification.json.sha256
```

Publication protocol:

1. Build and intrinsically verify the candidate after all three final freezes and pinset verification.
2. Copy the exact candidate bytes and sidecar create-only into `published/`; fsync them.
3. Ed reviews the exact marker/member/receipt digest table.
4. On Ed's `YES`, create the confirmation JSON and then its sidecar, both create-only and durable.
5. Run `verify_family_marker.py --phase publication`; persist its PASS receipt and sidecar.
6. Only then record atomic publication complete and run the published-head suite.
7. Never edit or overwrite any of these files; a correction uses a new transaction custody directory and cannot silently reuse `d117-v4`.

Any absent or mismatched member of the published set makes the consumer refuse. Thus a crash during publication yields a recoverable but non-published state, never a half-valid family.

For each window:

- copy the canonical published set into `$ARM_READINESS_CUSTODY_ROOT/family_publication/`, preserving exact bytes and digests;
- store the pre-arm verification receipt there;
- write the fresh T-0 verification receipt under `$WINDOW_CUSTODY_ROOT/family_publication/`;
- bind both receipts, marker, confirmation, and scheduler receipt into the GO receipt;
- carry the same digest references into close-out custody so later claim admission can prove which published family authorized the window.

The family material sits at the custody-root family level, never under ALPHA, BETA, or GAMMA. No pack is treated as the marker's owner.

The marker instance and all companion custody records add zero tracked paths. They do not engage r4-1's conditional two-path clause, so this design does not alter the ruled 112-path marker accounting. Any separate O-1 change is outside this marker design.

### 5. Discriminating test surface

#### Schema and canonicalization

- Golden exact-schema marker validates.
- Missing or extra key at every nesting level refuses.
- Duplicate JSON key, noncanonical whitespace/order, invalid UTF-8, non-finite number, uppercase/short digest, malformed Git OID, or boolean-as-integer refuses.
- Member order other than ALPHA/BETA/GAMMA refuses.
- `publication_state` other than `PUBLISHED` refuses.

#### Builder

- Two builds from identical inputs into distinct empty custody directories are byte-identical.
- Permuting `--pack-root` arguments does not change bytes.
- Existing output, orphan primary/sidecar, symlink output, repository-contained output, or simulated fsync/write failure refuses without overwrite.
- Dirty worktree; HEAD/local-main mismatch; HEAD/origin-main mismatch; unavailable origin; different pack repositories/heads all refuse.
- Missing, duplicate, extra, wrong-generation, or role-swapped pack refuses.
- Wrong registry path/ID/SHA, unresolved token, wrong marker schema, or wrong FAMILY_PUBLICATION code/type refuses.
- Missing `freeze-0004`; `freeze-0003`; ordinal/id disagreement; REFUSE receipt; wrong receipt schema; wrong sidecar; receipt/plan mismatch; receipt/registry mismatch; predecessor replay failure each refuses.
- Mixed evidence derivation commits refuse.
- Executing builder or consumer bytes differing from the committed blob refuses.
- Repository and all three pack roots are byte-for-byte unchanged after success and every failure.

#### Per-binding tamper tests

- Change marker only.
- Change marker and recompute its sidecar, but not confirmation.
- Change marker, sidecar, and confirmation coherently, but not live Git/pack bytes.
- Change head only; tree only; same tree under a different commit.
- Swap two member profiles; duplicate one; omit one; add a fourth.
- Substitute a `_v3` pack or another valid `_v4`-shaped ID not in the registry.
- Change pack bytes without commit; commit the change at a different head; change executable mode only.
- Change plan-tree bytes only; coherently update plan sidecar but not pack/member digest; retarget the freeze attachment.
- Change receipt bytes; receipt sidecar only; ID only; ordinal only; status to REFUSE.
- Coherently rewrite receipt and sidecar but leave plan attachment old.
- Coherently rewrite receipt, sidecar, and plan attachment but leave marker pack/receipt hashes old.
- Use a valid receipt from the wrong profile.
- Alter a predecessor binding or referenced generic evidence so semantic replay refuses.
- Mix otherwise valid receipts authored at different derivation commits.
- Change builder/consumer tool references.

#### Publication and gate tests

- Candidate mode PASS always has `publication_authorized: false`.
- Published modes refuse absent confirmation, confirmation sidecar, non-YES verdict, wrong marker SHA, wrong head/tree, wrong family/member summary, or wrong confirmer.
- Gate code paths cannot invoke candidate mode.
- Marker refusal still executes all six scheduler gates; composed verdict is NO-GO and `claim_admissible` is false.
- Scheduler-specific reason vocabulary remains disjoint; the nested refusal remains `readiness_r1_family_publication`/`CUSTODY`.
- Scheduler v1 cannot authorize an `_v4` window; valid v2 round-trips exactly.
- Both SHAKEDOWN and CLAIM refuse without publication.
- A head move, marker replacement, or confirmation replacement after pre-arm is caught at T-0.
- `launch_window.py` refuses absent/invalid scheduler v2, GO binding, T-0 verification receipt, or final marker/confirmation hash.
- No bypass flag exists.
- Complete published custody passes from a different clean checkout at the same commit, proving the marker contains no absolute pack-root dependency.
- The changed-set proof remains 112 with no marker-instance path.

### 6. Risks and rejected alternatives

1. **External custody is not cryptographic authorship.** Hash fan-out raises the cost of undetected alteration but does not defeat an actor able to rewrite all custody and Git references. A signing key would change the authority model and requires an Ed ruling. It is not required for v1.

2. **Strict head equality is availability-fragile by design.** Any ordinary commit or origin-main movement refuses publication at pre-arm/T-0, including docs-only commits. That is consistent with the ruled commit freeze (`rulings-r5-consolidation.md`, V-3, lines 120–138).

3. **Scheduler receipt v2 has integration cost.** The current v1 exact schema cannot honestly carry the publication proof. Versioning is preferred over hiding the digest in `assurance` or overloading G6.

4. **The marker does not prove freshness.** It proves family publication identity. G1 still recomputes deadlines from authenticated evidence, and G5 still owns the boot-span pin. A marker PASS never substitutes for arm or scheduler PASS.

5. **Private helper coupling is a maintenance risk.** Implementation should promote a small public package API for pack-record derivation and full freeze replay rather than duplicating `committed_pack_tree_sha256` or receipt semantics in scripts.

6. **The v1 schema is deliberately `_v4`-exact.** It does not generalize ordinals or scan for future families. A `_v5` registry/family receives its own reviewed schema or versioned extension, consistent with the standing price that registry changes force a new family.

Rejected alternatives:

- **Tracked marker files:** directly contradicts D-150 and would engage r4-1's conditional marker paths.
- **Per-pack markers:** contradicts the ruled family boundary and permits partial publication.
- **Marker inside a pack or freeze receipt:** creates the recorded self-hash cycle or requires forbidden post-mint pack mutation.
- **Building only after Ed's yes:** prevents Ed from reviewing the marker's exact bytes, contrary to the ruled order.
- **Embedding Ed confirmation in the marker:** requires changing already reviewed candidate bytes after confirmation.
- **Directory scanning as family selection:** allows missing, extra, or wrong-profile packs; registry membership is authoritative.
- **Trusting marker plus sidecar without live recomputation:** permits coherent external rewrite.
- **Adding multiple publication reason codes:** violates the one registry-owned FAMILY_PUBLICATION role; discriminating check IDs provide diagnostics.
- **Unioning the R1 code into scheduler reason codes:** conflicts with the scheduler ruling's vocabulary separation.
- **Putting publication in G6:** conflates family custody with D-149 C1–C5.
- **Pre-arm-only verification:** misses marker or head drift before T-0.
- **T-0-only verification:** detects defects too late and needlessly loses a window.
- **Absolute pack roots in marker bytes:** harms archival relocation and is unnecessary because repository-relative identity plus the live repository coordinate is sufficient.

## Disagreements

The earlier unratified sketch proposed a tracked canonical path, and r4-1 priced two tracked paths conditionally. D-150 supersedes that placement choice: the marker is custody-external and the marker portion of the changed-set contract remains unchanged. This design therefore rejects the tracked-path branch without reopening it.

The scheduler receipt v2 extension is a new consequence of integrating publication into the existing exact v1 receipt. It does not revise any G1–G6 predicate or vocabulary and requires magistrate adjudication as part of this D-144 round, not a new Ed ruling.

## Open questions

None block implementation. No additional Ed ruling is required for this design.

The magistrate should record the scheduler v2 consequence explicitly when composing the two seats, because silently retaining v1 while claiming the marker is scheduler-bound would be a false binding.

## Recommendation

Adopt this family-exact schema and external-custody protocol. Build deterministic marker bytes after all three final freezes; activate them only through Ed's digest-bound confirmation; verify at publication, scheduler pre-arm, and T-0; carry the resulting receipts into scheduler and GO custody; and keep the single registry-owned `readiness_r1_family_publication`/`CUSTODY` refusal outside the six scheduler gate vocabularies.

<!-- Debate round: same Sol thread 01a02b69-4c97-7a11-9ab6-5b37b50a7981, continued at HEAD 2a9257d (D-151 landed). Envelope: DISCUSSION, pathspec [], protocol-valid. -->

## Debate — reply to the Opus seat

### Positions

#### 1. The receipt-boundary defect is real; my original design has the same hole

I verified the finding against HEAD `2a9257d823c7332d5b52a38e4e06e3e44f55db2f`.

The failure chain is:

- `validate_r1_lifecycle_registry` accepts a resolved refusal spelling based only on its regex and an independently valid type; it does not check membership in `READINESS_REASON_CODES` or agreement with `REASON_TYPE_BY_CODE` (`joulewise/arm_readiness.py:1771-1812`).
- `EvidenceLifecycleError` therefore accepts that registry entry and can emit it through `.refusal()` (`:962-988`).
- Receipt validation later rejects an unregistered code at `_validate_refusal` (`:1466-1475`). A call through `_receipt_refusal` fails even earlier (`:4454-4465`).
- The generated freeze and arm receipts are validated at `:6419` and `:7122`, so this becomes an exception from receipt construction rather than the governed `FAMILY_PUBLICATION` refusal the design promised.

My `readiness_r1_family_publication` / `CUSTODY` single-code design does have this omission. The single receipt-facing code is still the right shape; its code/install coupling was underspecified.

The exact cure is the previously ruled V4 code delta, not Opus's newly proposed `readiness_family_publication_refused` spelling:

```python
R1_LIFECYCLE_CUSTODY_CODES = frozenset(
    {"readiness_r1_family_publication"}
)

READINESS_REASON_CODES = frozenset().union(
    ...,
    R1_LIFECYCLE_CUSTODY_CODES,
)

REASON_TYPE_BY_CODE = {
    ...,
    **{code: "CUSTODY" for code in R1_LIFECYCLE_CUSTODY_CODES},
}
```

The resolved-entry branch of the registry refusal loop must additionally enforce:

```python
if not code.startswith(_R1_ED_RESERVED_PREFIX) and (
    code not in READINESS_REASON_CODES
    or reason_type != REASON_TYPE_BY_CODE[code]
):
    raise ArmReadinessError(
        "readiness_row_registry_mismatch",
        f"R1 refusal_vocabulary[{index}] is not a closed reason code",
    )
```

That is already the mechanism mandated in `docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING.md:84-92`; its exact family spelling and typed-set construction are recorded at `docs/process_traces/2026-08-20-go-session/opus-reg-report.md:353-404`. Later r4-5 changes `FAMILY_PUBLICATION`'s allocation to `CUSTODY` but does not reopen its spelling (`v4-plan-ruling-r4draft.md:81-91`).

Required falsifiers:

1. A regex-valid divergent family code must refuse while loading the registry with `readiness_row_registry_mismatch`.
2. The exact registered code must survive `generate_arm_receipt`, receipt serialization, and `validate_arm_receipt`, yielding a normal REFUSE receipt rather than an exception.
3. Its receipt `type` must be exactly `CUSTODY`.
4. The diagnostic `familypub_*` subcode stays detail only; it must never enter `READINESS_REASON_CODES`.

#### 2. Head binding: strict equality for authorization, ancestry for historical consumption

The two designs describe useful but different modes. Opus's ancestry construction belongs in archival and successor-predecessor verification. It is insufficient at the three authorizing consult points in this round.

| Consult point | Required binding |
|---|---|
| Publication completion | `publication_head == HEAD == refs/heads/main == refs/remotes/origin/main`, clean checkout, exact `publication_head_tree` |
| Scheduler pre-arm | The same equality, plus the existing G4 exact-match evaluation |
| T-0 / launch consumption | Recompute the same equality and compare the marker and confirmation-table digests with the scheduler receipt and GO receipt |
| Archival verification or a future `_v5` predecessor check | `publication_head` ancestor of current `HEAD` and `origin/main`, plus dual-coordinate equality of the predecessor family's bytes; never gate-admissible as a `_v4` arm |

This is not needless duplication of G4. G4 proves that the consulting checkout agrees with its local and remote main references. Marker equality additionally proves that those references have not advanced together past the exact head Ed published. Without it, a coordinated ordinary commit and push can leave G4 `exact_match=true` while changing the publication coordinate.

The binding grounds are explicit:

- V-3 requires `reviewed_main exact_match` before every arm, freezes both local main and `origin/main`, and prohibits pushes from any machine during the span (`rulings-r5-consolidation.md:120-138`).
- r4-3 says even a docs-only commit disarms T-0 and holds the commit freeze from terminal attestation through window close (`v4-plan-ruling-r4draft.md:46-60`).
- D-151 permits the first successor-pinset fixation commit only after window close (`MAGISTRATE-RULING-O1.md:36-55`). That post-window commit is the natural point at which strict authorization ends and archival ancestry becomes useful.

The publication operation therefore has two phases:

1. Pre-publication candidate verification at the final local head: intrinsic checks pass, but the result is `gate_admissible: false` while that head is not yet the exact published remote head.
2. After the exact head is published, re-resolve `origin/main`, require all four coordinates equal, and only then activate the custody directory atomically.

Rollback analysis:

- Under Opus's authorizing rule, checking out an old published head `P` passes `P ancestor HEAD` trivially and also passes `P ancestor origin/main` after origin has advanced to `Q`; dual-coordinate bytes also pass because the checkout itself is back at `P`. Thus the marker verifier alone admits rollback-to-`P`.
- G4 can incidentally stop that state if its current remote ref remains `Q`, but the publication consumer and arm integration should not depend on another call site to repair their authorization semantics.
- Strict equality refuses because `P != origin/main`.
- Neither design defeats an actor who forges the local `origin/main` tracking ref or rewrites both histories. D-151's forged-ref-conditional local green explicitly demonstrates that boundary. Published green and the custody record remain required; the mechanism claims detectability, not integrity against that actor.

I therefore retain strict equality for publication, pre-arm, and T-0, while conceding Opus's ancestry-plus-dual-byte construction for non-arm archival verification and future predecessor-family chaining.

#### 3. Confirmation must not be digest-folded into the marker

Opus's proposed dependency has a cycle.

Its marker body contains `publication.confirmation_sha256`, and the marker's `body_sha256` covers that field. The step-6 table, however, must identify the marker bytes and marker digest: that is the exact-byte confirmation pattern required by A-5.1 (`MAGISTRATE-RULING-r2.md:90-95`) and by the transaction design that r4-3 orders as "marker candidate + Ed's exact-byte step-6" (`v4-plan-ruling-r4draft.md:53-56`).

Let `M` be the marker and `C` the confirmation record. Opus's construction requires:

```text
hash(M) depends on hash(C)
hash(C) depends on hash(M)
```

No construction or prescribed fixed-point search resolves that. Operationally, the rehearsal marker has null confirmation fields; inserting the confirmation digest changes the marker body, `body_sha256`, and whole-file digest after Ed has confirmed the candidate.

There are only two apparent escapes:

- If `C` does not bind `M`, the cycle disappears, but Ed has not confirmed the final marker bytes.
- If the confirmation digest is excluded from the marker's digested body, the design has become the one-way external construction recommended below.

No cycle-breaking mechanism appears in the Opus design, so I retain separation. I do, however, revise my design in one important way: the marker should not have a candidate/publication lane field whose value changes. The exact final marker bytes are built once before step 6. Candidate versus publication is a verifier invocation state determined by the presence and validity of the external Ed table.

The marker body should bind only this confirmation contract:

```json
"publication_authority": {
  "authority_role": "ED",
  "confirmation_schema": "joulewise.d117_step6_confirmation_table.v1",
  "required_decision": "YES"
}
```

It must not contain the confirmation table's path, digest, confirmation timestamp, or any other post-marker value.

#### 4. Engagement must be tracked-state-driven; candidate mode is safe with one correction

I adopt Opus's decisive engagement rule:

> Marker presence never decides whether publication governance engages.

For a current-family arm or scheduler consult, engagement is determined from the committed registry at `HEAD`: if the pack identity is one of the exact `successor_policy.successor_pack_ids`, `FAMILY_PUBLICATION` is engaged. A missing marker or confirmation table then refuses; deletion cannot disengage governance.

My original design loaded and bound the registry roster but did not state this engagement/deletion invariant strongly enough. It needs that correction.

The freeze bootstrap requires a separate predicate. The marker cannot be required while minting the `_v4` receipts it binds. The safe rule is:

- `generate_freeze_receipt` never evaluates publication for the pack being minted.
- In predecessor mode, it evaluates publication only for the predecessor.
- A predecessor generation below the first governed generation (`v4`) needs no marker.
- A predecessor at generation `v4` or later must present its family marker and step-6 table; their absence refuses before successor custody output.
- That predecessor verification uses the historical ancestry/dual-coordinate mode from point 2, because the repository and current successor registry may legitimately have advanced to `_v5`.

The engagement threshold must itself be tracked code or tracked registry policy—e.g. a closed constant `FAMILY_PUBLICATION_FIRST_GENERATION = 4`—not inferred from marker presence.

There is one defect in Opus's literal engagement table: it says the predecessor gate engages when the predecessor's `pack_id` is in the current registry's `successor_pack_ids`. During `_v4` minting, the predecessor is `_v3` while the registry names `_v4`; during `_v5`, the predecessor is `_v4` while the current registry names `_v5`. That predicate is false in both cases. The predecessor-generation rule above is the exact repair.

Candidate mode is sufficient for S-0 and safe if implemented as follows:

- The marker bytes are identical to the eventual publication marker; there is no mutable `lane` field.
- `verify_family_marker --phase candidate` verifies all intrinsic marker, Git, registry, roster, pack, plan, evidence, and freeze bindings but requires no Ed table.
- It returns `status: PASS`, `phase: candidate`, and `gate_admissible: false`.
- Every production call site hardcodes publication or predecessor mode; no production caller accepts a CLI-selected candidate phase.
- S-0 must prove both halves: candidate intrinsic PASS and production-gate refusal while the table is absent.
- No real arm is attempted before publication, matching r4-3's dry-run-only order.

This avoids both bootstrap deadlock and candidate laundering.

#### 5. Scheduler receipt v2 is a real convergence

Both seats correctly conclude that the scheduler receipt must become `joulewise.window_scheduler_gate_receipt.v2`. At HEAD, `SCHEDULER_GATE_RECEIPT_SCHEMA` is v1 and `RECEIPT_KEYS` is exact (`joulewise/scheduler_gates.py:30,132-149`), so adding publication custody in place would violate the existing receipt contract.

I now recommend adopting Opus's explicit G7 shape rather than my earlier hidden parallel conjunct, subject to the magistrate explicitly amending the schedgate ruling's "all six gates" statement (`schedgate-ruling.md:63-87`).

The exact v2 delta should be:

- `GATE_IDS = ("G1","G2","G3","G4","G5","G6","G7")`.
- Evaluation order is `("G5","G1","G2","G3","G4","G6","G7")`.
- All seven evaluate without short-circuiting.
- G7 runs for both SHAKEDOWN and CLAIM.
- G7 PASS requires:

  1. current-family engagement from the committed registry;
  2. the marker and unified step-6 table to verify in publication mode;
  3. strict publication-head equality from point 2;
  4. the scheduled pack to be one of the three members;
  5. the marker family ID to equal the campaign boot-pin family ID;
  6. the presented marker/table hashes to equal the campaign-custody expected hashes.

- G7's scheduler-only refusal set is:

```python
G7_REASON_CODES = frozenset(
    {
        "scheduler_family_unpublished",
        "scheduler_family_marker_absent",
        "scheduler_family_marker_invalid",
        "scheduler_family_confirmation_absent",
        "scheduler_family_confirmation_invalid",
        "scheduler_family_boot_pin_mismatch",
    }
)
```

These remain in `SCHEDULER_GATE_REASON_CODES`, typed `CUSTODY`, and are not unioned into readiness vocabulary. The corresponding G7 observation carries the distinct lifecycle refusal:

```json
{
  "role": "FAMILY_PUBLICATION",
  "type": "CUSTODY",
  "code": "readiness_r1_family_publication",
  "diagnostic": "familypub_*"
}
```

`RECEIPT_KEYS` gains the exact-key block:

```json
"family_publication": {
  "family_id": "d117_v4",
  "marker_path": "family_publication/d117_family_publication_v4.json",
  "marker_id": "d117_v4@<publication-head>",
  "marker_sha256": "<sha256-or-null-on-refusal>",
  "marker_body_sha256": "<sha256-or-null-on-refusal>",
  "confirmation_table_path": "family_publication/d117_step6_confirmation_table_v4.json",
  "confirmation_table_sha256": "<sha256-or-null-on-refusal>",
  "publication_head_commit": "<oid-or-null-on-refusal>",
  "publication_head_tree": "<oid-or-null-on-refusal>",
  "consult_head_commit": "<current oid>",
  "registry_sha256": "<sha256-or-null-on-refusal>",
  "lifecycle_code": "readiness_r1_family_publication"
}
```

A G7 refusal leaves unverifiable values null; it must not copy unverified claims from a malformed marker.

The composite scheduler verdict and `claim_admissible` cannot be GO/true unless G7 is PASS. The R-3 launch seam and T-0 evaluator then reverify both custody artifacts and require their hashes to equal this v2 block and the GO receipt. That prevents swapping an external marker between scheduling and launch.

#### 6. My confirmation record and D-151's table should be one artifact

They are the same authority act and should be one physical artifact. Keeping both would require two Ed yeses or create two nominally authoritative digests for one step-6 decision.

I withdraw `joulewise.d117_family_publication_confirmation.v1` as a separate emitted schema and recommend the shared name:

```text
joulewise.d117_step6_confirmation_table.v1
```

Its normative home should be a transaction-level confirmation-table contract, not the marker or histsem contract—proposed home: `docs/contracts/d117_step6_confirmation_table.md`. The marker contract and `receipt_histsem_verifier.md` should each reference that one home.

Every object is exact-key validated; paths are repository-relative or confirmation-directory-relative. The field set is:

```json
{
  "schema_version": "joulewise.d117_step6_confirmation_table.v1",
  "table_kind": "D117_FAMILY_PUBLICATION",
  "transaction_id": "d117-v4-publication",
  "family_id": "d117_v4",
  "git": {
    "head_commit": "<40-hex>",
    "head_tree": "<40-hex>"
  },
  "registry": {
    "path": "configs/arm_readiness/d117_row_registry_v1.json",
    "registry_id": "<id>",
    "schema_version": "<schema>",
    "sha256": "<resolved-registry-sha256>",
    "archived_preinstall_sha256": "<old-registry-sha256>"
  },
  "family_marker": {
    "path": "d117_family_publication_v4.json",
    "schema_version": "joulewise.d117_family_publication_marker.v1",
    "marker_id": "d117_v4@<head>",
    "body_sha256": "<sha256>",
    "sha256": "<whole-marker-sha256>"
  },
  "histsem_successor": {
    "path": "<D-151 exact successor-pinset path>",
    "schema_version": "joulewise.receipt_histsem_pinset.v1",
    "sha256": "<successor-pinset-sha256>",
    "pack_count": 3,
    "receipt_count": "<integer>",
    "fact_count": "<integer>"
  },
  "members": [
    {
      "profile": "ALPHA",
      "pack_id": "d117_floor_qwen25_1p5b_v4",
      "pack_path": "configs/campaigns/d117_floor_qwen25_1p5b_v4",
      "pack_tree_sha256": "<sha256>",
      "plan_tree_sha256": "<sha256>",
      "evidence_set_sha256": "<sha256>",
      "freeze_receipt": {
        "ordinal": 4,
        "path": "arm_readiness.freeze.receipts/freeze-0004.json",
        "receipt_id": "<id>",
        "sha256": "<sha256>",
        "sidecar_sha256": "<sha256>"
      }
    },
    {
      "profile": "BETA",
      "...": "same exact keys"
    },
    {
      "profile": "GAMMA",
      "...": "same exact keys"
    }
  ],
  "temporal": {
    "boot_session_id": "<uuid>",
    "earliest_evidence_deadline_monotonic_ns": "<integer>",
    "earliest_evidence_deadline_evidence_id": "<id>"
  },
  "confirmation": {
    "authority": "ED",
    "authority_basis": "D-139-A3+MAGISTRATE-RULING-r2-A-5.1",
    "decision": "YES",
    "statement": "I confirm these exact bytes for d117_v4 family publication."
  }
}
```

Members are in the fixed order ALPHA, BETA, GAMMA. The artifact contains no self-digest and no post-confirmation timestamp. The actual event time belongs in the immutable custody transcript. Before prompting Ed, the tool renders the exact final bytes—including the literal proposed `YES` statement—and computes their digest. Those bytes are not authoritative while staged. Ed's explicit yes names that digest, after which the same bytes are promoted without mutation.

The digest flow is acyclic:

1. Build the final marker bytes `M`; compute `hM`.
2. Commit D-151's successor pinset `S` at the common head; compute `hS`.
3. Build the table `C` containing `hM`, `hS`, the common head/tree, registry digest, and member/freeze digests; compute `hC`.
4. Present exact `C` bytes and `hC` to Ed. Ed confirms `hC`; no artifact byte changes afterward.
5. Atomic publication activates `M`, `C`, and their GNU sidecars as one custody directory.
6. The marker consumer validates `C → M`.
7. D-151's changed-set checker validates `C → S`; the expected `hC` is Ed's custodied step-6 digest.
8. Scheduler receipt v2 and every GO receipt record both `hM` and `hC`.
9. At the first commit after window close, D-151 fixation independently recomputes `hS` and checks it against the `histsem_successor` row in the Ed-confirmed `C`.

Thus one Ed yes authenticates both the family publication and the versioned-successor allowlist class, exactly matching D-151's adoption (`MAGISTRATE-RULING-O1.md:36-74`). The marker never points back to `C`, so there is no digest cycle.

### Final convergences

The seats now substantially converge on:

- One custody-external marker at the three-pack family boundary.
- Exact canonical bytes, exact-key schemas, three-member registry roster, common head/tree, exact pack/tree/freeze receipt bindings, and fail-closed absence.
- One receipt-facing `FAMILY_PUBLICATION` refusal with `CUSTODY` type and diagnostic subcodes beneath it.
- Registry-driven engagement, never marker-presence-driven engagement.
- Predecessor-only freeze integration to avoid the `_v4` bootstrap deadlock.
- A non-authorizing S-0 candidate verification path.
- Scheduler receipt v2, a G7 publication check, and launch/T-0 re-verification.
- One Ed confirmation artifact rather than duplicate yes records.
- D-151's successor digest and marker digest joined through that one step-6 table.

### Remaining disagreements, with grounds

1. **Authorizing head semantics.** I retain exact equality for publication, pre-arm, and T-0. Opus's ancestry rule admits rollback to an old published checkout and contradicts V-3's no-ordinary-commit span. I accept ancestry only for archival and future predecessor verification.

2. **Confirmation direction.** I reject embedding `confirmation_sha256` in the marker's digested body because the exact-byte table also binds the marker, creating a cycle. The one-way table-to-marker binding is mechanically constructible under r4-3's order.

3. **Freeze engagement predicate.** I accept predecessor-only engagement but reject membership of the predecessor in the current successor roster as the predicate; that predicate never engages across adjacent generations. Generation-threshold engagement from tracked code/policy is required.

4. **Refusal spelling.** The Opus blocker is correct, but `readiness_family_publication_refused` would reopen an already selected vocabulary. The install should use the ruled `readiness_r1_family_publication`.

### Open questions

No additional Ed decision blocks the schema design. The magistrate should make three implementation choices explicit in this ruling:

- Amend the scheduler ruling's six-gate enumeration to seven and authorize the v2 field set.
- Adopt `joulewise.d117_step6_confirmation_table.v1` as the single confirmation-table schema and normative contract home.
- Record `v4` as the first publication-governed predecessor generation, either through a closed tracked constant or an exact registry policy field. I recommend the tracked constant for this D117-specific v1 consumer; a future generalized schema can move it into registry policy.

### Recommendation set for the magistrate

1. Adopt Opus's receipt-boundary finding and require the ruled typed-set plus registry-load closure delta.
2. Preserve the exact `readiness_r1_family_publication` / `CUSTODY` registration.
3. Require strict head/local-main/origin-main equality at all current-family authorizing consults; define ancestry mode as non-arm archival/predecessor verification only.
4. Remove confirmation digest/path/time from the marker body; build the marker once and bind it one-way from the unified step-6 table.
5. Merge my confirmation artifact with D-151's confirmation table under the exact schema and digest flow above.
6. Bind engagement to committed registry/code state; require marker absence to refuse after engagement.
7. Use predecessor-generation engagement for freeze bootstrap and prove `_v4` mint success plus `_v5`-shaped predecessor refusal.
8. Adopt scheduler receipt v2 with G7, record both marker and confirmation-table digests, and reverify both at launch/T-0.
9. Require discriminating regressions for registry-code divergence, receipt-boundary non-escape, rollback-to-old-head, confirmation-cycle prevention, marker deletion, candidate laundering, predecessor bootstrap, table-to-marker tamper, table-to-successor tamper, and scheduler/GO digest substitution.
