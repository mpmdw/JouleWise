# `_v4` FAMILY PUBLICATION MARKER — schema v1, builder, consumer

Independent design seat (Opus), D-144 co-design round under r5 **V-6**
("the marker schema+consumer … gets its OWN bounded D-144 co-design round
… BEFORE implementation; no waiver"). Written blind: no other seat's
output was sought or read.

Repo read-only at `1ba04a83b6dacc2ea904c7936901922857ac89d4` (`1ba04a8`).
No repository file was modified.

---

## 0. What is ruled, and what this design is therefore allowed to decide

| Ruled input | Text | Consequence for this design |
|---|---|---|
| MAGISTRATE-RULING-r2 **A-1** option (a) | "real schema string + consumer land in the `_v4` install transaction; the marker INSTANCE … is built after pack bytes are final, external to pack roots; publication refuses until the instance validates" | Schema string + consumer are transaction-scoped code; the instance is built post-freeze, outside every pack root. |
| Ed **D-150** (this session) | marker BUILT AT THE FAMILY BOUNDARY; **custody-external** (built/verified outside the git tree, in transaction custody; NOT tracked repo files); **changed-set contract stays 112** | r4-1's conditional "plus exactly two marker paths iff Ed rules V6 option (a) with a tracked marker" is **NOT triggered**. The 112-path allowlist of runsheet §2.1 is unchanged. §3.8's 114-path branch and O-2's tracked variant are closed. |
| r4-5 | four-type V4 allocation … **CUSTODY {FAMILY_PUBLICATION}** | The registry's `FAMILY_PUBLICATION` refusal entry carries `"type": "CUSTODY"`. |
| r2 A-5.6 | "PACK_FAMILY third-carry TERMINAL (non-discharge by the marker pass escalates to Ed)" | The roster binding (§2.4) is the marker's discharge of the PACK_FAMILY third carry; if any part of it cannot be built as specified, that is an Ed escalation, not a downgrade. |
| r5 V-6 | "S-1..S-5 land as ONE composed merge with ONE pre-merge two-seat pass" | Schema/consumer/gate land together; the schema-bump decisions in §4.4 are free precisely because nothing has been emitted in production yet. |
| runsheet §1.3 | the S-0 custody inputs' CLI "is exactly the one in §3.7 [/§3.8]" | Every CLI flag added here is **optional with a fail-closed default**; the two §3.8 invocations must run verbatim. Verified against §3.8 in §3.1/§4.1. |

Everything else below is this seat's design and is offered for the debate.

---

## 1. The forcing problem (what the marker is for, in one paragraph)

Three `_v4` packs are minted in one transaction, then **published** — where
"published" has, today, no mechanical meaning at all. The gates that exist
each answer a *local* question: the changed-set gate asks "did any
non-allowlisted repository path change since this pack's evidence was
derived?" (`arm_readiness.py:3916-3964`, refusal `:4038-4049`); the
historical-semantics verifier asks "do this pack's committed bytes still
match its governed pins?" (`docs/contracts/receipt_histsem_verifier.md`);
the freeze chain asks "does this pack present an authenticated
predecessor?". **None of them asks a family-level question.** Nothing
today refuses when:

* pack ALPHA is armed while pack GAMMA of the same family was never
  frozen, or was frozen from different bytes (a *partial family* — the
  PACK_FAMILY carry that r2 A-5.6 calls TERMINAL);
* a pack is armed at a head where the family's freeze receipts exist but
  the family was never published to `origin/main` (an *unpublished* arm —
  histsem's `histsem_commit_unpublished` is **advisory** in the pre-arm
  lane by design, so the pack itself will not refuse);
* the R1 registry that names the family's three members is edited after
  publication, silently changing which packs "the family" means;
* a freeze receipt carrying `status: REFUSE` is the one the family is
  standing on (r4-2's poison question);
* the family whose bytes are armed is not the family Ed confirmed at the
  step-6 exact-byte gate (r2 A-5.1).

The marker is the artifact that makes "this `_v4` family — these three
exact packs — is published, at this git head, with these exact freeze
receipts" a **checkable proposition**, and the `FAMILY_PUBLICATION`
refusal role (`arm_readiness.py:493`; census in `decision_log.md:9299`)
the mechanical answer when it is false.

### 1.1 Truth boundary, stated before any field is defined

The marker is **not a trust anchor and carries no authority of its own.**
Every assertion in it except one is *recomputed from Git objects and pack
bytes at consult time*; a forged marker therefore buys an attacker
nothing, because the forgery must also make the recomputation agree.
The one assertion that is not recomputable is **Ed's step-6 confirmation**
(§2.6): it is bound by digest, so substitution is *detectable to anyone
holding the custody copy*, and nothing more is claimed. In the words the
histsem contract uses of itself: this is **detectability, not integrity**,
and the marker adds no defence against a history-rewriting in-process
actor.

This matters for the custody-external ruling: because the marker is not
trusted, its being untracked costs the design almost nothing. What it
does cost is stated honestly in §5.4 and §7.

---

## 2. Marker schema v1

### 2.0 Identity, canonical form, determinism

* **Schema string** (the value Ed installs into the registry's
  `successor_policy.family_publication_marker_schema`, currently
  `ED_RESERVED:family-publication-marker-schema`,
  `arm_readiness.py:543-545`):

  ```
  joulewise.d117_family_publication_marker.v1
  ```

  This is the exact string the S-0 runsheet §3.8 already expects, so the
  runsheet's expectation line is satisfied verbatim. The registry
  validator today only requires this to be *a string*
  (`arm_readiness.py:1768-1769`); §4.5 adds the check that makes it
  load-bearing.

* **Canonical bytes**: `arm_readiness.render_json` —
  `json.dumps(value, indent=2, sort_keys=True) + "\n"`, UTF-8
  (`arm_readiness.py:1033-1036`). The verifier parses with
  `parse_json_bytes(raw, require_canonical=True)`; non-canonical bytes
  refuse. Reuse, never reimplement, both helpers.

* **Exact-key discipline**: every object below is validated with
  `_require_exact_keys`. An unknown key refuses; a missing key refuses.
  This is the house rule (`FREEZE_RECEIPT_KEYS`, `ARM_RECEIPT_KEYS`,
  `RECEIPT_KEYS`) and it is what makes a "helpfully extended" marker fail
  instead of pass.

* **No absolute paths anywhere in `body`.** Pack roots, freeze-receipt
  paths, the registry path and the confirmation record are all recorded
  **repository-relative** or **marker-directory-relative**. Two reasons,
  both load-bearing: (i) relocating custody must not change the bytes, so
  replay stays deterministic; (ii) the histsem contract's *archival
  location rule* ("it never compares a freeze receipt's
  `pack_identity.pack_root` with the verifier's current working
  directory") is honoured rather than quietly contradicted.

* **Determinism**: `body` contains no wall-clock, no UUID, no hostname,
  no ordering that depends on filesystem iteration (members are sorted by
  `pack_id`). Two builds from the same repository state produce
  **byte-identical `body`**. All non-deterministic facts live in
  `provenance`, which is excluded from `body_sha256` (§2.7). Testable in
  one line; test T-D1 in §6.

* **`marker_id`** is derived, not minted:
  `f"{family_id}@{publication_head}"`. A UUID would have made two markers
  for the same family indistinguishable in a log; the derived id makes a
  head substitution visible in the filename and in every receipt that
  quotes it.

### 2.1 Top level

```json
{
  "schema_version": "joulewise.d117_family_publication_marker.v1",
  "marker_kind": "family_publication",
  "marker_id": "d117_v4@<publication_head>",
  "lane": "publication",
  "body": { ... },
  "body_sha256": "<sha256 of render_json(body)>",
  "provenance": { ... }
}
```

`lane` ∈ {`publication`, `rehearsal`} — the two build modes defined in
§3.3. The authoritative copy is **`body.lane`**, inside the digested
body, so editing it breaks `body_sha256`. The top-level `lane` is a
convenience mirror for a reader skimming the file; the verifier refuses
if the two disagree (`familypub_lane_inconsistent`). The mirror earns its
place by that refusal: an operator who hand-edits the visible field to
promote a rehearsal marker gets a refusal instead of a silent lie in the
transcript.

`marker_kind`, `marker_id` and `schema_version` sit outside `body` for
the same reason — they are what a custody index quotes — and each is
re-derived and compared against `body` during verification (§4.5.1).

### 2.2 `body.registry` — the semantic frame

```json
"registry": {
  "registry_path": "configs/arm_readiness/d117_row_registry_v1.json",
  "registry_id": "d117-row-registry-v1",
  "registry_schema_version": "joulewise.arm_readiness_row_registry.v2",
  "registry_sha256": "<sha256 of the blob at publication_head>",
  "marker_schema_declared": "joulewise.d117_family_publication_marker.v1"
}
```

| Binding | Recomputation at consult time | Tamper detected |
|---|---|---|
| `registry_sha256` | `git show <publication_head>:<registry_path>` hashed; **and** the same blob at `HEAD` hashed; both must equal | The registry was edited after publication — roster swapped, allowlist widened, refusal codes respelled, horizons changed. Without this the marker's whole vocabulary could be redefined under it. |
| `registry_id` / `registry_schema_version` | compared with the parsed registry | A different registry file substituted at the same path. |
| `marker_schema_declared` | must equal both `schema_version` **and** the registry's `successor_policy.family_publication_marker_schema` at both coordinates | A marker built to a different (older/looser) marker contract than the installed registry declares. This is the field that discharges F2's economics: the registry token stops being decorative. |

### 2.3 `body.git` — the publication coordinate

```json
"git": {
  "root_commit": "<oid of the repository's initial commit>",
  "publication_head": "<40-hex commit oid>",
  "publication_head_tree": "<40-hex tree oid>",
  "evidence_derivation_commit": "<40-hex commit oid>",
  "terminal_review": {
    "source_kind": "GIT",
    "source_path": "<repo-relative TERMINAL_REVIEW source>",
    "source_sha256": "<sha256 of that blob at publication_head>",
    "head_tree_oid": "<40-hex tree oid>"
  }
}
```

| Binding | Recomputation | Tamper detected |
|---|---|---|
| `publication_head` | must be an **ancestor of the consulting repo's `HEAD`** and an **ancestor of `origin/main`** (hard in the publication lane) | Arming a family that was never published, or on a divergent lineage. The `origin/main` conjunct is the *only* mechanical meaning "published" has (it is what histsem's `histsem_commit_unpublished` keys on, `arm_readiness.py:3225-3232`); the marker makes it **hard** where histsem's pre-arm lane leaves it advisory. |
| `publication_head_tree` | `git rev-parse <publication_head>^{tree}` | A commit object swapped for one with the same id-adjacent metadata but a different tree (belt-and-braces; a rewrite changes the commit oid anyway). |
| `terminal_review.head_tree_oid` | must equal `publication_head_tree`, and the TERMINAL_REVIEW source blob at `publication_head` must hash to `source_sha256` | The family was published at a tree Ed did not terminally review. R1 clause 3 already binds `head_tree_oid` unconditionally at authoring (`arm_readiness.py:3904-3910`); the marker carries that binding *forward past publication*, where nothing else does. |
| `evidence_derivation_commit` | equals every member's evidence `derivation_commit` | A family whose members were derived at different heads — i.e. not one family. |
| `root_commit` | `git rev-list --max-parents=0 HEAD` | A marker carried into a different repository entirely. Weak (a full rewrite changes it too, and a clone shares it) — kept because it costs one git call and turns an otherwise-silent cross-repo mistake into a refusal. Flagged as weak in §7.2. |

**Why ancestry and not equality.** The stricter alternative
(`HEAD == publication_head`) was considered and is recorded as the
standing dissent (§7.3). It is rejected because the question "may
unrelated commits exist between publication and arm?" is already owned by
the changed-set allowlist (`:4038-4049`) and by G4's `reviewed_main
exact_match`; a second, differently-shaped authority over the same
question is how contradictory gates get born. The marker instead binds
**ancestry plus dual-coordinate byte equality** (§2.4) — the family's own
bytes must be identical at `publication_head` and at `HEAD`, which is the
precise proposition "these exact packs, unchanged since publication",
with no opinion about anyone else's commits.

### 2.4 `body.family` — the roster (the PACK_FAMILY discharge)

```json
"family": {
  "family_id": "d117_v4",
  "family_generation": 4,
  "member_count": 3,
  "members": [ <exactly three, sorted by pack_id> ]
}
```

Each member:

```json
{
  "profile": "ALPHA",
  "pack_id": "d117_floor_qwen25_1p5b_v4",
  "pack_path": "configs/campaigns/d117_floor_qwen25_1p5b_v4",
  "pack_digest_algorithm": "joulewise.committed_pack_tree_sha256.v1",
  "published_pack_sha256": "<committed pack tree digest at publication_head>",
  "plan_id": "<plan.plan_id from plan_tree.json>",
  "plan_tree_sha256": "<sha256 of plan_tree.json>",
  "plan_tree_sidecar_sha256": "<sha256 of plan_tree.sha256>",
  "evidence_set_sha256": "<domain-framed digest of the eleven evidence blobs>",
  "freeze_receipt": {
    "ordinal": 4,
    "path": "arm_readiness.freeze.receipts/freeze-0004.json",
    "sidecar_path": "arm_readiness.freeze.receipts/freeze-0004.json.sha256",
    "sha256": "<sha256 of the receipt blob>",
    "sidecar_sha256": "<sha256 of the sidecar blob>",
    "receipt_id": "<uuid from the receipt>",
    "receipt_schema_version": "joulewise.arm_readiness_freeze_receipt.v2",
    "status": "PASS",
    "arm_disposition": "GO",
    "predecessor": {
      "pack_id": "d117_floor_qwen25_1p5b_v3",
      "freeze_receipt_id": "<v3 receipt id>",
      "freeze_receipt_sha256": "<v3 receipt digest>"
    }
  }
}
```

| Binding | Recomputation | Tamper detected |
|---|---|---|
| `profile` → `pack_id` | must equal the registry's `successor_policy.successor_pack_ids` mapping exactly (set equality over {ALPHA,BETA,GAMMA}, `arm_readiness.py:1732-1751`) | A pack substituted into a profile slot; a fourth pack; two packs claiming one profile. |
| `member_count: 3` + exactly three entries + unique `pack_id` | structural | **Partial family** — the r2 A-5.6 TERMINAL carry. Two published packs and one silently missing is now a refusal instead of a shrug. |
| `family_generation` | must equal the `_v<N>` suffix of **every** member (`_PACK_GENERATION_RE`, `arm_readiness.py:244`) and the marker's `family_id` suffix | A `_v5` pack smuggled into a `_v4` marker; a `_v4` marker re-presented for a `_v5` family. |
| `published_pack_sha256` | computed **twice by independent routes**: pure-Git tree walk at `publication_head` under `PACK_DIGEST_DOMAIN` (the `historical_pack_tree_sha256` framing) **and** `committed_pack_tree_sha256(pack_root)` at `HEAD`; both must equal the recorded value | Any change to any pack byte after publication, in the worktree or in a later commit. The dual route is the K5/K12 pattern of the histsem contract and is what makes a *reimplemented* digest impossible to slip past. |
| `plan_tree_sha256` / `plan_tree_sidecar_sha256` | hashed at both coordinates | The plan tree re-rendered post-publication (the exact slot the freeze-slot normalization touches — see the risk in §7.4). |
| `evidence_set_sha256` | recomputed over the eleven evidence blobs named by the census (`arm_readiness.py:4956-4982`; `arm_readiness_evidence.py:1688-1710`) under a domain-framed digest | Evidence swapped between family members; an evidence file added or removed after publication. Also mechanically re-asserts the eleven-slug census the 112 contract depends on. |
| `freeze_receipt.sha256` + `sidecar_sha256` + `receipt_id` + `ordinal: 4` | blob hashes at both coordinates; `ordinal` parsed from the filename, matching the code's own rule that generation derives from the directory/receipt name (r2 A-4, `arm_readiness.py:5427-5432,5489-5500` per r4's labels) | A re-minted `freeze-0004` (the idempotent-replay lock), a `freeze-0005` substituted, or an edited sidecar. This is the ruling's "with these exact freeze receipts", literally. |
| `status: "PASS"` / `arm_disposition: "GO"` | re-read from the receipt; the **builder refuses** to build over a non-PASS receipt (§3.4) and the **verifier refuses** if the receipt disagrees with the marker | r4-2's poison question: a refusal-carrying mint that idempotent replay then locks. The family cannot be published standing on a REFUSE receipt, and cannot later be *made* to look published by editing the marker. |
| `predecessor.*` | compared with the receipt's own v2 `predecessor` block (`FREEZE_PREDECESSOR_KEYS`, `arm_readiness.py:382-392`) | A chain fork: two `_v4` families both claiming the same `_v3` ancestor, or a family with no lineage. Adjacent to the `SUCCESSOR_CHAIN` role; the marker does not duplicate that gate, it records the coordinate so a fork is visible at family scope. |

### 2.5 `body.lifecycle` — the refusal frame

```json
"lifecycle": {
  "family_publication_code": "<registry FAMILY_PUBLICATION code>",
  "family_publication_type": "CUSTODY"
}
```

Recomputed against `_r1_refusal_entry(registry, "FAMILY_PUBLICATION")`
(`arm_readiness.py:1854-1868`) at both coordinates. Detects: the marker
built against a registry whose FAMILY_PUBLICATION spelling differs from
the one installed now — i.e. a registry respelling that would otherwise
let a refusal be emitted under a code no consumer is watching. `type` is
pinned to `CUSTODY` per r4-5.

### 2.6 `body.publication` — Ed's act

```json
"publication": {
  "confirmation_kind": "ED_EXACT_BYTE_CONFIRMATION",
  "confirmation_path": "ed-step6-confirmation.json",
  "confirmation_sha256": "<sha256 of that file>",
  "confirmed_at_utc": "<UTC from inside the confirmation record>"
}
```

`confirmation_path` is **relative to the marker file's own directory**
(§5.1). The verifier hashes the sibling file and refuses on mismatch
(`familypub_confirmation_mismatch`) or absence
(`familypub_confirmation_missing`) in the publication lane.

This is the one binding whose *authority* is not recomputable (§1.1): the
digest proves the record has not changed since the marker was built, not
that Ed wrote it. Ed's step-6 gate is reserved by r2 A-5.1 and D-139 A3;
this field is where that human act becomes a checkable artifact rather
than a line in a transcript. An **optional strengthening that would close
the gap and costs no changed-set path** is offered in §7.5 (a signed Git
tag — refs are not paths).

In the `rehearsal` lane the three confirmation fields are `null` and the
verifier records `gate_admissible: false`.

### 2.7 `provenance` (excluded from `body_sha256`)

```json
"provenance": {
  "built_at_utc": "2026-08-2xT..Z",
  "builder_source_sha256": "<sha256 of build_family_marker.py>",
  "builder_git_describe": null,
  "python_version": "3.11.x"
}
```

`builder_source_sha256` earns its place: the S-0 candidate manifest names
the reviewed builder bytes (runsheet §1.3.4), so this field lets a
reviewer prove *which reviewed bytes* produced this marker without
trusting the transcript. It is deliberately outside `body_sha256` so that
a rebuild from the same repo state is byte-identical in `body`.

---

## 3. Builder contract — `build_family_marker.py`

### 3.1 CLI (superset-compatible with runsheet §3.8, verbatim)

```
build_family_marker.py
  --repository <path>                # required (§3.8 passes "$CLONE")
  --head <commit>                    # required (§3.8 passes "$PINSET_COMMIT")
  --pack-root <repo-relative> x3     # required, exactly three (§3.8)
  --output <path>                    # required (§3.8)
  [--confirmation <path>]            # optional; absent ⇒ lane=rehearsal
  [--lane {publication,rehearsal}]   # optional; default derived from --confirmation
  [--reproduce <existing marker>]    # optional; copies provenance for byte-equality replay
```

The four required flags are exactly §3.8's. No other flag is required, so
the runsheet's literal invocation runs unchanged. **There is no
`--force`, no `--overwrite`, no `--skip-*`, and no environment variable
is read** — a grep-testable no-bypass property (test T-N1), mirroring the
schedgate ruling's "No bypass flag (grep-testable); no waiver of any arm
gate".

Stdout is a canonical JSON build report (schema
`joulewise.d117_family_publication_marker_build.v1`) carrying the marker
path, `body_sha256`, file digest, lane, and the recomputation results —
this is what §3.8 redirects into `081-marker-build.json`.

### 3.2 Determinism

* Members sorted by `pack_id`; all maps rendered with `sort_keys=True`.
* No filesystem iteration order, locale, or `$TZ` reaches `body`.
* Every digest is taken from **Git objects at `--head`**, not from the
  worktree, except the deliberate second-route worktree recomputation
  used as an equality check (§2.4). If the two routes disagree, the
  builder refuses (`familypub_pack_digest_mismatch`) — a dirty worktree
  can never be laundered into a marker.
* `--reproduce` copies `provenance` verbatim from an existing marker so a
  reviewer can assert **whole-file** byte equality, not just `body`
  equality (test T-D2).

### 3.3 Lanes

| Lane | When | Effect |
|---|---|---|
| `rehearsal` | S-0 clone-proof, any pre-publication build (no `--confirmation`) | `publication.*` fields null; `origin/main` ancestry conjunct is **advisory** (recorded as an advisory string, as histsem does at `arm_readiness.py:3225-3232`); the marker is stamped `lane: rehearsal`. |
| `publication` | the real transaction, `--confirmation` supplied | all conjuncts hard, including `origin/main` ancestry and the confirmation digest. |

**A rehearsal marker can never be laundered into a gate**: every gate
calls the library with `require_publication_lane=True` (§4.2), which is
not reachable from any CLI flag. The rehearsal lane exists only so S-0
can prove the mechanism before the family is published — exactly the
two-lane shape the histsem contract already uses ("CI-hard verification"
vs "pre-arm library verification").

### 3.4 Refusal conditions (the builder refuses to produce a marker at all)

Fail-closed, each with a distinct `familypub_*` sub-code (§4.3):

1. `--output` resolves **inside the repository worktree** (`git
   rev-parse --show-toplevel`) or inside any pack root →
   `familypub_output_in_tree`. **This is the mechanical enforcement of
   D-150's custody-external ruling and of the 112-path contract**: the
   builder physically cannot add a repository path. Prose would not have
   bound this; a `realpath` prefix check does.
2. `--output` already exists → `familypub_output_collision` (`O_EXCL`
   create; no overwrite lane, matching the histsem contract's "no update,
   regenerate, repair, or auto-reseal lane").
3. The registry at `--head` contains any `ED_RESERVED:` value
   (`_r1_contains_reserved` at `arm_readiness.py:1533`, applied at `:1828-1836`) →
   `familypub_registry_dormant`. A marker built against a dormant
   registry would bind meaningless semantics; this mirrors G1's ruled
   dormant-R1 refusal ("the scheduler never trusts a dormant gate").
4. The three `--pack-root` values ≠ the registry's
   `successor_pack_ids` values → `familypub_roster_mismatch`.
5. Any member lacks `freeze-0004.json` or its sidecar, or the receipt's
   `status` ≠ `PASS` / `arm_disposition` ∉ {`GO`} →
   `familypub_freeze_not_pass`.
6. Members disagree on `evidence_derivation_commit`, or any generation
   suffix differs → `familypub_family_incoherent`.
7. `git status --porcelain` is non-empty for any pack path or for the
   registry path → `familypub_worktree_dirty`.
8. `HEAD` ≠ `--head`, the repository is shallow, or any bounded git call
   fails → `familypub_head_mismatch` / `familypub_history_shallow` /
   `familypub_git_unavailable`.
9. TERMINAL_REVIEW source absent, or its `head_tree_oid` ≠ tree of
   `--head` → `familypub_terminal_review_mismatch`.
10. Publication lane with `--confirmation` absent/unreadable →
    `familypub_confirmation_missing`.

**No network, no fetch, no repair, no checkout swapping**, and every Git
call goes through a bounded helper with a timeout (the `_histsem_git`
shape, `arm_readiness.py:2734-2750`). A refusal writes **no output file**
(build to a temp path in the same directory, `fsync`, then `O_EXCL`
rename — a half-written marker is itself a hazard the fail-closed
consumer would report as `familypub_marker_noncanonical`, but never
producing one is better).

### 3.5 Placement

Library logic in `joulewise/family_publication.py` (validation,
recomputation, refusal vocabulary — importable by `arm_readiness` and
`scheduler_gates` without a circular import: it may import
`arm_readiness` helpers, and `arm_readiness` calls it through one
thin gate function, the same shape `_gate_receipt_histsem` uses).
Thin CLIs in `scripts/build_family_marker.py` and
`scripts/verify_family_marker.py`. For S-0, the reviewed custody copies
sit in `$INPUT` per runsheet §1.3.4 with their `.sha256` sidecars, and
their bytes must be identical to the in-tree scripts landed by the
candidate patch (test T-C1 asserts this equality, so S-0 cannot prove a
mechanism the transaction will not ship).

---

## 4. Consumer contract — `verify_family_marker.py` + gate integration

### 4.1 CLI (superset-compatible with runsheet §3.8, verbatim)

```
verify_family_marker.py
  --repository <path>          # required (§3.8)
  --marker <path>              # required (§3.8)
  [--pack-root <repo-relative>]# optional, repeatable: also assert this pack is a member
  [--lane {publication,rehearsal,marker}]  # default: marker (use the marker's own lane)
  [--require-publication-lane] # CLI mirror of the gate's hard setting
```

Exit codes: `0` PASS, `2` REFUSE (governed), `1` reserved for
environment/usage errors. Stdout is canonical JSON:

```json
{
  "schema_version": "joulewise.d117_family_publication_verification.v1",
  "status": "PASS",
  "lane": "rehearsal",
  "gate_admissible": false,
  "marker_id": "d117_v4@<head>",
  "marker_sha256": "...", "body_sha256": "...",
  "publication_head": "...", "consult_head": "...",
  "members": [ {"pack_id": "...", "checks": {...}} ],
  "advisories": ["familypub_head_unpublished"],
  "refusals": []
}
```

**Runsheet erratum (flagged, §8.2):** §3.8's expected-output list should
gain `"lane": "rehearsal"` and `"gate_admissible": false`. Under this
design the §3.8 verify still **PASSes** (status PASS on the conjuncts its
lane governs), so the runsheet's "consumer PASS" expectation holds
verbatim; but a reader comparing transcripts should see the lane
explicitly, and a PASS with `gate_admissible: true` in S-0 would be the
defect, not the success.

Also flagged: §3.8's **option (b)** branch (`--expect-token UNBUILT.v0
--publication-canary`) is closed by D-150. Those flags are **not**
implemented — a dead flag in a fail-closed verifier is attack surface,
and `verify_family_marker.py` must have exactly one job.

### 4.2 Which gates consult it, and when

| Consult point | Engagement rule | Lane | Refusal surface |
|---|---|---|---|
| `generate_arm_receipt` — before any custody output, adjacent to the existing `_gate_receipt_histsem` call | pack_id ∈ registry `successor_pack_ids` values | publication (hard) | receipt refusal carrying the registry's FAMILY_PUBLICATION code |
| `generate_freeze_receipt`, **predecessor mode only**, applied to the **predecessor** pack | predecessor pack_id ∈ registry `successor_pack_ids` values | publication (hard) | same |
| `scheduler_gates` **G7** (new) | window_class ∈ {SHAKEDOWN, CLAIM}; always evaluates | publication (hard) | `scheduler_family_unpublished` (+ mirrored lifecycle code, §4.3) |
| `launch_window.py` consume seam (schedgate **R-3**) | consume already requires a valid gate receipt; add: re-verify the marker and require its file digest to equal the one recorded in the gate receipt | publication (hard) | `launch_binding_mismatch` + gate refusal |
| the transaction's own publication step (runsheet Post-publication) | always | publication (hard) | publication does not complete (MARKER-A1: "publication refuses until the instance validates") |
| `dry-run` receipt generation | **never** | — | records `family_publication: NOT_EVALUATED` |

**The bootstrap deadlock, and its exact cure.** The `_v4` freeze-0004
mints happen *before* the marker can exist (the marker binds the freeze
receipts). If the freeze gate engaged on the pack being minted, `_v4`
could never be created. The rule above is therefore precise: **freeze
engages only on the predecessor**, never on the pack being minted. `_v3`
packs are not registry-installed successors, so the `_v4` mints see no
engagement; a future `_v5` mint in predecessor mode *will* require the
`_v4` marker — which is exactly the retrofit-avoidance benefit A-1 option
(a) was bought for. This is the single most dangerous ordering fact in
the design and is called out again in §6 (test T-B1) and §7.1.

**Engagement is bound to tracked bytes, never to the marker's presence.**
The engagement predicate reads `successor_pack_ids` from the *committed*
registry (`git show HEAD:configs/arm_readiness/d117_row_registry_v1.json`,
the same HEAD-anchored read the histsem gate uses at
`arm_readiness.py:3466-3487`). Deleting or hiding the untracked marker
therefore **cannot** disengage the gate; it converts to
`familypub_marker_absent` and refuses. Any design in which the untracked
file decides its own governance is fatal, and is rejected explicitly in
§7.3.

### 4.3 Exact refusal vocabulary

Two levels, deliberately:

**(a) Receipt-facing — exactly one code, registry-owned.** The R1 census
(`decision_log.md:9296-9302`, `arm_readiness.py:487-498`) registers
`FAMILY_PUBLICATION` **once**, with an Ed-reserved spelling. The consumer
therefore emits, at the receipt boundary, `_r1_refusal_entry(registry,
"FAMILY_PUBLICATION")["code"]` — *sourced from the registry at runtime,
never hardcoded* (the same discipline the runsheet uses at §3.9/§4 when
it extracts `DEPENDENCY_CHANGED_SET`/`DEPENDENCY_MANIFEST` spellings).
Inventing twelve receipt-facing codes would break the census and require
Ed to re-reserve; it is not on offer.

**(b) Diagnostic — a closed `familypub_*` sub-code set**, disjoint from
`READINESS_REASON_CODES` and from `histsem_*`, carried in the refusal
`detail` and in the verification JSON's `refusals[]`. Closed set:

```
familypub_marker_absent            familypub_marker_unreadable
familypub_marker_noncanonical      familypub_marker_schema_mismatch
familypub_marker_self_digest_mismatch
familypub_lane_inconsistent        familypub_lane_inadmissible
familypub_registry_mismatch        familypub_registry_dormant
familypub_roster_mismatch          familypub_roster_incomplete
familypub_pack_not_member          familypub_family_incoherent
familypub_head_mismatch            familypub_head_unpublished
familypub_head_unresolvable        familypub_history_shallow
familypub_git_unavailable          familypub_worktree_dirty
familypub_pack_digest_mismatch     familypub_plan_binding_mismatch
familypub_evidence_set_mismatch    familypub_freeze_binding_mismatch
familypub_freeze_not_pass          familypub_predecessor_mismatch
familypub_terminal_review_mismatch familypub_confirmation_missing
familypub_confirmation_mismatch    familypub_output_in_tree
familypub_output_collision         familypub_internal_error
```

`familypub_internal_error` exists so that **no bare exception escapes**:
both library boundaries catch `FamilyPublicationError` and map it, the
way the histsem contract requires ("no bare exception may escape and no
coincidental downstream `readiness_*` refusal substitutes for a required
histsem refusal"). Test T-E1 asserts an injected `OSError` becomes a
governed refusal, not a traceback — this is r4-5's `EvidenceLifecycleError`
escape-site lesson applied prospectively rather than retrofitted.

### 4.4 Code-delta manifest (what the transaction must add)

1. **`CUSTODY_REASON_CODES` gains one member.** Verified gap: no existing
   code fits, and `arm_readiness.py:1468` / `:4457` require every receipt
   refusal code to be a member of `READINESS_REASON_CODES`. So an
   Ed-reserved registry spelling that is *not* in the code set would blow
   up at the receipt boundary rather than refuse cleanly. **Recommended
   spelling for Ed's reservation: `readiness_family_publication_refused`**
   (type `CUSTODY`, per r4-5).
2. **New registry validation conjunct** (§4.5) — every registry refusal
   code must be a member of `READINESS_REASON_CODES`. Today
   `arm_readiness.py:1795-1799` checks only the regex
   `[a-z][a-z0-9_]*`. This is a genuine hole: a typo'd or divergent
   Ed-reserved spelling installs cleanly and only fails at the moment a
   refusal is needed — i.e. fails **open at install, closed at the worst
   possible time**. One `set` check closes it.
3. **`scheduler_gates`**: `GATE_IDS` gains `G7`;
   `GATE_EVALUATION_ORDER` becomes `("G5","G1","G2","G3","G4","G6","G7")`;
   `G7_REASON_CODES = {scheduler_family_unpublished,
   scheduler_family_marker_absent, scheduler_family_marker_invalid,
   scheduler_family_marker_lane_inadmissible,
   scheduler_family_boot_pin_mismatch}` with
   `_REASON_TYPE_BY_CODE` → `CUSTODY` and
   `_MIRRORED_FROM_BY_CODE` → `arm_readiness_lifecycle`; `RECEIPT_KEYS`
   gains `family_publication`:

   ```json
   "family_publication": {
     "marker_path": "<campaign-custody-relative>",
     "marker_sha256": "...", "body_sha256": "...",
     "marker_id": "...", "publication_head": "...",
     "lifecycle_code": "<registry FAMILY_PUBLICATION code>"
   }
   ```

   Because `RECEIPT_KEYS` is exact-key enforced, this is a **key add**,
   and R-2's ruled precedent ("`ARM_RECEIPT_KEYS` is exact-key enforced;
   no in-place key add") binds: the gate receipt schema becomes
   `joulewise.window_scheduler_gate_receipt.v2`. That is free here only
   because nothing has been emitted in production yet and V-6 lands
   S-1..S-5 as one composed merge; the bump must ride **this** wave.
4. **G7 conjuncts**: marker verifies in the publication lane; the pack
   being scheduled is a member; `family.family_id` equals the campaign
   boot pin's `family_id` (`BOOT_PIN_KEYS`,
   `scheduler_gates.py:155-157`) — catching a boot pin created for a
   different family; and the marker file digest equals the one the
   window was scheduled with. G7 evaluates for **both** SHAKEDOWN and
   CLAIM (a diagnostic shakedown of an unpublished family is exactly the
   thing that later gets mistaken for a claim run; S-2's
   `claim_admissible: false` stamping is a separate control and does not
   cover it).
5. `arm_readiness`: one thin `_gate_family_publication(pack_root, *,
   marker_ref, require_publication_lane=True)` called at the two
   boundaries of §4.2, structurally parallel to `_gate_receipt_histsem`.

### 4.5 How custody-external verification binds to the repo head at consult time

Stated as the exact conjunct list the consumer evaluates, in order (all
must hold; the first failure refuses, and every conjunct is recomputed —
nothing is taken from the marker on trust):

1. Marker file parses as canonical JSON; exact keys; `schema_version` is
   the v1 string; `body_sha256` equals `sha256(render_json(body))`; the
   top-level mirrors (`lane`, `marker_id`) are re-derived from `body` and
   must match; the GNU sidecar (if present) verifies. → structural
   integrity.
2. Repository is resolved **from the pack root** when called from a gate
   (`_repository_and_pack_relative`), never from a caller-supplied root.
   The CLI's `--repository` is honoured but must contain every
   `pack_path` named in the marker.
3. `git rev-parse --is-shallow-repository` is false; all git calls
   bounded and read-only; no fetch.
4. `body.git.publication_head` resolves; is an ancestor of `HEAD`; is an
   ancestor of `origin/main` (hard in publication lane, advisory in
   rehearsal).
5. Registry blob at `publication_head` **and** at `HEAD` both hash to
   `body.registry.registry_sha256`; parsed registry's
   `family_publication_marker_schema` equals the marker's
   `schema_version`; its FAMILY_PUBLICATION entry equals
   `body.lifecycle`.
6. Roster equals the registry's `successor_pack_ids`; generations
   uniform; exactly three members.
7. Per member: pack digest recomputed at **both** coordinates equals
   `published_pack_sha256`; plan/evidence/freeze/predecessor blobs hash
   to their recorded values at both coordinates; freeze receipt parses
   and its `status`/`arm_disposition`/`receipt_id` agree with the marker.
8. TERMINAL_REVIEW source blob at `publication_head` hashes to
   `source_sha256` and its `head_tree_oid` equals
   `publication_head_tree` equals `rev-parse publication_head^{tree}`.
9. Publication lane: confirmation sibling file hashes to
   `confirmation_sha256`.
10. If `require_publication_lane` and `body.lane != "publication"` →
    `familypub_lane_inadmissible`.

**Absent / malformed / mismatch semantics are uniform and fail-closed**:
each of the three maps to a governed refusal (`familypub_marker_absent`,
`familypub_marker_unreadable|noncanonical|schema_mismatch`, and the
specific mismatch sub-code), and each surfaces at the receipt boundary as
the single registry FAMILY_PUBLICATION code. There is no "warn and
continue" state anywhere, and no lane in which an engaged pack proceeds
without a marker.

---

## 5. Custody convention

### 5.1 The marker is a directory, not a file

```
<transaction custody root>/family-publication/d117_family_publication_v4/
  d117_family_publication_v4.json          # the marker (runsheet §3.8's --output name)
  d117_family_publication_v4.json.sha256   # GNU sidecar, `shasum -a 256 -c` verifiable
  ed-step6-confirmation.json               # Ed's exact-byte confirmation record
  ed-step6-confirmation.json.sha256
  081-marker-build.json                    # builder report
  082-marker-verify.json                   # verifier report at publication
```

Sibling-relative paths inside `body` (§2.6) make the whole directory
relocatable without changing a byte. Runsheet §3.8 writes the marker to
`$CUSTODY/marker-candidate/d117_family_publication_v4.json`; that is the
rehearsal instance of this same directory and needs no change.

### 5.2 Deployment to the campaign

At publication the directory is **copied** (never moved) to the campaign
custody root as `<campaign_root>/family_publication/`, and the copy is
verified by digest equality against the transaction custody original
before the first window is scheduled. The scheduler resolves the marker
at that fixed relative location **and** requires the caller (window
scheduling context / arm context key `family_publication_marker`) to
state the expected file digest; both must agree. Two independent
statements of the same digest is what turns "the operator pointed at the
wrong marker" from a silent success into a refusal.

### 5.3 GO-receipt linkage

```
marker file  --sha256-->  window_scheduler_gate_receipt.v2.family_publication
             --sha256-->  GO receipt (binds the gate receipt by sha, schedgate ruling)
             --sha256-->  launch consumption (R-3 seam re-verifies and compares)
```

Every GO receipt therefore names the exact family marker its window stood
on, and a later reader can re-run `verify_family_marker.py` against the
recorded digest. Per-window re-pin (r4-4) already records "same boot,
reviewed HEAD, earliest remaining deadline, acceptance + estimator shas";
`marker_sha256` and `publication_head` join that list.

### 5.4 The retrospective tracked anchor (what custody-external costs, and the mitigation)

Because the marker is untracked, it gets **no CI byte-pin** — the control
the histsem pinset has via `tests/test_receipt_histsem.py`. The mitigation
is a *retrospective* anchor: the marker's `marker_id`, file digest and
`body_sha256` are recorded in the first tracked commit **after** the
V-3(c) commit-freeze span ends (the RUN_STATE / decision-log entry that
closes the campaign). This adds **zero** paths to the 112 contract
because it lands outside the derivation→publication span. It does not
retro-protect the campaign; it makes post-hoc substitution of the
archived marker detectable, which is the honest scope. Recorded as a
residual, not a cure (§7.2).

---

## 6. Discriminating test surface

Every row is a *falsifier*: it must fail before the fix and pass after,
and each tamper must produce its **specific** sub-code — a test that only
asserts "some refusal" would pass against a gate that refuses for the
wrong reason.

**Tamper cases, one per binding (§2 order).** Each mutates exactly one
thing in an otherwise-passing fixture:

| # | Mutation | Required outcome |
|---|---|---|
| T1 | flip one hex char of `body_sha256` | `familypub_marker_self_digest_mismatch` |
| T2 | flip one hex char anywhere in `body` (leaving `body_sha256` stale) | same as T1 — proves the self-digest covers the whole body |
| T3 | re-render marker with `indent=4` | `familypub_marker_noncanonical` |
| T4 | add one unknown key to `body.family` | exact-key refusal, `familypub_marker_schema_mismatch` |
| T5 | `schema_version` → `…marker.v2` | `familypub_marker_schema_mismatch` |
| T6 | registry's `family_publication_marker_schema` changed post-publication | `familypub_registry_mismatch` |
| T7 | registry `successor_pack_ids` swapped ALPHA↔BETA post-publication | `familypub_registry_mismatch` (registry digest) **and**, with digest re-stated, `familypub_roster_mismatch` — run both variants |
| T8 | drop one member (2-pack family) | `familypub_roster_incomplete` — **the PACK_FAMILY carry** |
| T9 | member `pack_id` → a `_v5` name | `familypub_family_incoherent` |
| T10 | one byte changed in a pack's `plan_tree.json` in the worktree | `familypub_pack_digest_mismatch` (worktree route) |
| T11 | same change committed on top of `HEAD` | `familypub_pack_digest_mismatch` (HEAD-coordinate route) — proves both routes are live |
| T12 | `plan_tree.sha256` sidecar edited | `familypub_plan_binding_mismatch` |
| T13 | one evidence blob swapped between two members | `familypub_evidence_set_mismatch` |
| T14 | `freeze-0004.json` re-minted with different bytes | `familypub_freeze_binding_mismatch` |
| T15 | marker points at `freeze-0005` | `familypub_freeze_binding_mismatch` (ordinal) |
| T16 | freeze receipt with `status: REFUSE` | builder: `familypub_freeze_not_pass`; verifier on a hand-edited marker: same |
| T17 | predecessor block altered | `familypub_predecessor_mismatch` |
| T18 | `publication_head` → a sibling commit not on `HEAD`'s ancestry | `familypub_head_mismatch` |
| T19 | `origin/main` moved so `publication_head` is unpublished | publication lane: `familypub_head_unpublished`; rehearsal lane: advisory + PASS |
| T20 | TERMINAL_REVIEW source blob altered | `familypub_terminal_review_mismatch` |
| T21 | `head_tree_oid` ≠ tree of `publication_head` | `familypub_terminal_review_mismatch` |
| T22 | confirmation file deleted / one byte changed | `familypub_confirmation_missing` / `familypub_confirmation_mismatch` |
| T23 | registry containing `ED_RESERVED:` | `familypub_registry_dormant` (build **and** verify) |
| T24 | marker deleted entirely, pack still registry-installed | `familypub_marker_absent` **and** the arm receipt carries the registry FAMILY_PUBLICATION code — the single most important test in the suite |
| T25 | rehearsal-lane marker presented to G7 / to the arm gate | `familypub_lane_inadmissible` |
| T26 | top-level `lane` ≠ `body.lane` | `familypub_lane_inconsistent` |
| T27 | a pack not in the roster passed as `--pack-root` to verify | `familypub_pack_not_member` |

**Mechanism tests:**

* **T-B1 (bootstrap)**: minting `freeze-0004` for a registry-installed
  `_v4` pack with **no marker in existence** must succeed. If this test
  fails, the family can never be created (§4.2).
* **T-B2**: a `_v5`-shaped freeze in predecessor mode over a `_v4`
  predecessor **without** a valid `_v4` marker must refuse.
* **T-D1 (determinism)**: two builds from identical repo state produce
  identical `body` bytes and identical `body_sha256`.
* **T-D2 (replay)**: `--reproduce` yields whole-file byte equality.
* **T-C1 (custody/tree identity)**: the `$INPUT` custody copies are
  byte-identical to the in-tree scripts landed by the candidate patch.
* **T-N1 (no bypass)**: source grep proves no `os.environ` read for
  marker location/lane, no `--force|--skip|--allow|--no-verify` option in
  either CLI, and no call site passes `require_publication_lane=False`
  outside tests.
* **T-O1 (custody-external)**: `--output` inside the worktree refuses
  with `familypub_output_in_tree`; a run of the builder leaves `git
  status --porcelain` empty — the mechanical proof that the 112 contract
  is untouched.
* **T-E1 (no escape)**: an injected `OSError`/`subprocess` failure in the
  git helper yields a governed refusal, never a traceback (r4-5's
  escape-site lesson, applied prospectively).
* **T-R1 (registry code membership)**: a registry whose
  FAMILY_PUBLICATION code is not in `READINESS_REASON_CODES` refuses at
  **validation** time (§4.4.2), not at refusal time.
* **T-G1 (gate composition)**: a gate receipt cannot be `GO` while G7 is
  `REFUSE`/`NOT_EVALUATED`; `family_publication` keys are present and
  exact; schema is `…gate_receipt.v2`.
* **T-S1 (S-0 integration)**: the two §3.8 invocations run **verbatim**
  and produce `081-`/`082-` transcripts with `lane: rehearsal`,
  `gate_admissible: false`, `status: PASS`.

Per r5's **R12** discipline ("no review credit until the specified test
pins RUN in a writable worktree"), none of the above earns credit until
executed.

---

## 7. Risks, residuals, rejected alternatives

### 7.1 Risks carried

* **Bootstrap ordering (highest).** The freeze-engagement rule of §4.2 is
  the only thing standing between this design and an uncreatable family.
  Mitigated by T-B1/T-B2 and by making engagement a single predicate with
  one call site per boundary.
* **Custody loss is fatal-by-design.** Lose the marker directory and every
  `_v4` arm refuses. This is *correct* fail-closed behaviour, and it is
  recoverable: the builder is deterministic, so the marker rebuilds
  byte-identically from the repository — **except** the confirmation
  record, which only Ed can reissue. Ed should hold a second copy.
* **Double authority over pack bytes.** `published_pack_sha256` overlaps
  histsem's K12. Deliberate: different anchors (publication_head vs the
  HEAD pinset) and different failure meanings. The risk is divergence
  (one refuses, the other passes, and a reader believes the passing one);
  mitigated by T10/T11 asserting both routes and by the marker recording
  which coordinate failed.
* **G7 arrives with G1/G2/G3/G6 still `NOT_IMPLEMENTED`.** G7 is
  implementable today (its inputs all exist at head) and composition
  already refuses `GO` while anything is `NOT_IMPLEMENTED`, so no false
  GO is possible; but reviewers must not read a G7 PASS as window
  readiness.

### 7.2 Residuals recorded, not cured

* No CI byte-pin for an untracked artifact (§5.4) — retrospective anchor
  only.
* `root_commit` is a weak repository binding (a clone shares it).
* The confirmation digest proves immutability, not authorship (§1.1);
  §7.5 offers the closure if Ed wants it.
* Detectability, not integrity, against a history-rewriting in-process
  actor — inherited verbatim from the histsem truth boundary.

### 7.3 Rejected alternatives (with the reason each was rejected)

1. **Tracked marker at `configs/campaigns/d117_family_publication_v4.json[.sha256]`** — ruled out by Ed (D-150) and by the 112 contract; r4-1's conditional clause is not triggered. Cost accepted: §7.2's first bullet.
2. **Engagement by marker presence** (gate engages only if a marker file is found) — **fatal**: deleting an untracked file would disengage governance. Engagement is registry-bound (§4.2).
3. **Trusting the marker's sidecar as its authority** — a self-produced digest proves nothing about the producer; verification is by recomputation (§1.1).
4. **A distinct receipt-facing reason code per tamper** — breaks the R1 census's single FAMILY_PUBLICATION registration (`decision_log.md:9296-9302`) and would require Ed to re-reserve. Diagnostic granularity lives in the `familypub_*` sub-codes instead (§4.3).
5. **`HEAD == publication_head` exact equality** — recorded as the standing dissent. Stricter, and defensible during the frozen span; rejected because it duplicates authority the changed-set gate and G4 already own, and it would kill legitimate post-span arms for reasons the marker has no business judging. Ancestry + dual-coordinate byte equality gives the same protection over the family's own bytes (§2.3).
6. **Folding the check into an existing gate (G3 admission)** — G3 is blocked on the B-22 track (S-2/r5 S-2); coupling publication verification to an unrelated blocker is how a mechanism arrives after the campaign it was built for.
7. **An environment variable or `--force` escape** — no. Grep-tested absent (T-N1).
8. **Adding the marker as a histsem pinset row** — collides with runsheet Open Item **O-1** (the pinset byte-pin has no update lane) and would need a `_v5`-cost change to alter. The marker's job is family-scope publication, not per-pack historical semantics.
9. **`--expect-token UNBUILT.v0 --publication-canary` (runsheet §3.8 option (b))** — closed by D-150; not implemented (§4.1).

### 7.4 One watch item for the implementation seat

r4-1's companion code delta ("freeze-slot normalization extends to ALL
THREE registry-declared successor plan trees") mutates the plan-tree
freeze slot to `null` for comparison purposes. The marker records
`plan_tree_sha256` of the **committed** bytes, not the normalized ones —
these are different objects and must not be conflated. The implementation
must take the raw blob digest (`sha256_bytes(tree_raw)`, the
`_pack_record` route at `arm_readiness.py:4508-4530`), and a test should
pin that a normalization change does not move the marker's value.

### 7.5 Optional strengthening that costs zero changed-set paths

A **signed annotated Git tag** at the publication head —
`git tag -s d117-family-v4-published <publication_head>` — would bind
Ed's key to the exact published commit. Refs are not repository *paths*,
so this adds **nothing** to the 112 contract and does not touch the
commit freeze. The marker would gain
`body.publication.signed_tag: {name, tag_object_oid}` and the verifier a
`git verify-tag` conjunct (advisory unless Ed rules it hard). Offered as
an Ed item, **not** assumed: it needs Ed's key and hands, and this design
is complete without it.

---

## 8. Items needing an Ed ruling, and source conflicts

### 8.1 Ed rulings required (each blocks a specific byte)

1. **The FAMILY_PUBLICATION refusal code spelling** — Ed-reserved under
   R1 clause 6; blocks the registry bytes. **Recommendation:
   `readiness_family_publication_refused`, type `CUSTODY`** (r4-5). It
   must simultaneously be added to `CUSTODY_REASON_CODES`
   (`arm_readiness.py:127-139`) or the receipt boundary at
   `arm_readiness.py:1468`/`:4457` rejects it — see §4.4.1. *This
   coupling appears not to be stated in any ruling read for this design
   and is flagged as a new finding.*
2. **The marker schema string** for
   `successor_policy.family_publication_marker_schema`.
   **Recommendation: `joulewise.d117_family_publication_marker.v1`** —
   the value runsheet §3.8 already expects.
3. **Gate-receipt schema bump to `…gate_receipt.v2`** (§4.4.3) — within
   the magistrate's authority as a schema-design call under V-6, but it
   changes a ruled artifact name and is flagged for the record.
4. **Optional**: the signed publication tag (§7.5).

### 8.2 Conflicts / errata against binding sources

* **r4-1 vs D-150** — r4-1 admits "exactly two marker paths iff Ed rules
  V6 option (a) **with a tracked marker**". D-150 rules option (a)
  *without* tracking, so the conditional is **not triggered** and 112
  stands. No conflict, but the two documents must be read together;
  recorded here so a later reader does not "restore" the two paths.
* **Runsheet §3.8 erratum** — the expected-output list should gain
  `"lane": "rehearsal"` and `"gate_admissible": false` (§4.1). The
  invocations themselves need no change.
* **Runsheet §3.8 option (b) is dead** — closed by D-150; the `(b)`
  branch and its `--expect-token/--publication-canary` flags should be
  struck from the runsheet, and §1.3's input list reduces to the
  option-(a) set (`build_family_marker.py`, `verify_family_marker.py`,
  both with sidecars).
* **Runsheet Open Item O-2 is discharged** by D-150 (option (a),
  custody-external, 112). **O-1 (histsem byte-pin vs the 112 contract)
  remains open and is untouched by this design** — the marker adds no
  path, so it neither helps nor worsens O-1.
* **Registry validation gap** (§4.4.2): `arm_readiness.py:1795-1799`
  regex-checks refusal codes but never checks membership in
  `READINESS_REASON_CODES`, and `class_mismatches`
  (`:1592,1613,1818-1821`) governs *freshness classes*, not codes. A
  divergent Ed-reserved spelling therefore installs cleanly and fails
  only when a refusal is first needed. Recommended as a `_v4` code-delta
  addition with test T-R1.

---

## Debate — reply to the Sol seat

Read: `marker-design-sol.md` (654 lines), plus two sources that post-date
my blind phase — **D-150** (`73764f0`) and **D-151** (`2a9257d`,
`docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md`).
Sections above are preserved unedited as the blind record; where this
reply supersedes them it says so explicitly.

### D-0. Concessions I make outright (with grounds)

**D-0.1 — Sol's separate confirmation record wins. My §2.6 is withdrawn.**
Sol's ground (`marker-design-sol.md:358`) is exactly right and I checked
my own construction honestly: my §2.6 puts `confirmation_path`,
`confirmation_sha256` and `confirmed_at_utc` **inside `body`**, and
`body_sha256` covers `body`. So the order would have to be: build marker
→ Ed confirms bytes → write confirmation → **rebuild the marker** to
embed the confirmation digest → the bytes Ed confirmed no longer exist.
That is a cycle, and r4-3's ruled order ("marker candidate + Ed's
exact-byte step-6 → atomic publication", `v4-plan-ruling-r4draft.md:53-57`;
r2 A-5.1) cannot be satisfied by any single-artifact design. The one
repair that keeps a single artifact — putting the confirmation fields
outside the digested body — creates a worse defect: "the marker's digest"
becomes ambiguous (pre- vs post-confirmation), and that digest is what
every downstream receipt binds. **Two artifacts, marker immutable from
build, confirmation pointing at the marker digest.** §D-4 shows D-151
forces the same conclusion independently.

**D-0.2 — my "blocking finding" in §4.4.1/§8.1.1 is a REDISCOVERY, not a
new finding, and my recommended spelling was wrong.** The R1 registry
ruling's **V4** (`MAGISTRATE-RULING.md:84-93`) already ruled: eight
`readiness_r1_*` codes, per-role types, and — verbatim — "REQUIRED
same-commit code deltas: four typed frozensets unioned into
READINESS_REASON_CODES + REASON_TYPE_BY_CODE, AND the registry-load
closure check (refuse unclosed codes at load — both seats executed the
double failure: bare codes explode at issuance today while the validator
accepts them at load)." That is precisely the `:1468`/`:4457` explosion I
described and the `:1795-1799` load-time gap I proposed to close. I
withdraw the novelty claim and my proposed spelling
`readiness_family_publication_refused` (outside the ruled `readiness_r1_*`
prefix). **Adopt Sol's `readiness_r1_family_publication` / role
FAMILY_PUBLICATION / type CUSTODY.** My §8.1.1 stops being an Ed item and
becomes a citation to V4.

**D-0.3 — the registry coordinate in my §2.2 is wrong.** I used the
current tracked `configs/arm_readiness/d117_row_registry_v1.json`. RULED
(`MAGISTRATE-RULING.md:124-131`): outer id `d117-row-registry-v2`, path
`configs/arm_readiness/d117_row_registry_v2.json`, inner lifecycle id
`d117-r1-lifecycle-v1`, with the `ROW_REGISTRY_RELATIVE_PATH` code delta
(`arm_readiness.py:80`) in the same commit and the v1 file staying
in-tree, unreferenced, sha-pinned. Sol has all of this right. Adopt Sol's
`lifecycle_registry` block verbatim.

**D-0.4 — no G7. Adopt Sol's parallel pre-arm conjunct.** My §4.4.3
proposed extending `GATE_IDS`. Sol's placement (`sol:455`, `:476-484`) is
less invasive and, decisively, the **ratified** schedgate text says "All
six gates always evaluate (no short-circuit)"
(`schedgate-ruling.md:76-77`). Changing gate cardinality edits a ruled
design; adding a sibling root conjunct extends a receipt. Under the
lieutenant's forbidden list (rule 11: no amending ruled doctrine), the
conservative reading wins. I concede, and attach one strengthening Sol
left implicit: the conjunct records its verdict **on PASS as well as
REFUSE** (a silently-absent block must be indistinguishable from nothing,
i.e. must refuse), and never short-circuits the six.

**D-0.5 — adopt Sol's tool self-hash refusal** (`sol:223`, `:300`) over my
weaker `provenance.builder_source_sha256` record — with one correction in
§D-3.4 for the S-0 lane, where it refuses as written.

**D-0.6 — adopt Sol's `candidate/` → `published/` two-stage custody
layout** (`sol:512-540`) in place of my single directory (§5.1). It makes
"which bytes did Ed confirm" a filesystem fact (byte-identical create-only
copy) and gives a crash story that yields non-published, never
half-published.

**D-0.7 — adopt Sol's strict head equality; my ancestry model (§2.3) is
withdrawn.** I argued ancestry + dual-coordinate byte equality so an
unrelated docs commit would not kill an arm. Under V-3(c) that commit is
**forbidden** for the whole span (`rulings-r5-consolidation.md:129-137`)
and G4's `exact_match` already refuses it, so my permissiveness bought
nothing and weakened the assertion. Sol's `head_commit == HEAD == local
main == origin/main`, `clean`, `exact_match` is right for the ruled span.
I keep only the *dual-coordinate digest recomputation* (§D-2), which is
orthogonal to which head is required.

### D-1. Convergences to record (both seats, independently)

Schema id `joulewise.d117_family_publication_marker.v1`; D-134 canonical
JSON + GNU sidecar; exact-key validation at every level; exactly three
members bound to the registry's `successor_pack_ids` (never directory
scan); `committed_pack_tree_sha256` reused, never reimplemented;
`freeze-0004` ordinal-exact with sidecar and status PASS; one common
evidence derivation commit across the three packs; determinism with no
wall clock, no randomness, no absolute paths in the bytes; create-only,
no overwrite, no repair lane; output refused inside the Git tree; no
bypass flag and a grep-testable proof of it; exactly ONE externally
visible reason code; scheduler receipt bumped to
`joulewise.window_scheduler_gate_receipt.v2`; both SHAKEDOWN and CLAIM
gated; zero tracked paths, r4-1's conditional two-path clause not
engaged, changed-set stays 112.

That is convergence on the whole spine. The rest is placement.

### D-2. Consult points — reconciling replay vs recomputation

Sol runs **full freeze semantic replay** (`require_pass=True`) at every
published-phase consult; I ran **two-coordinate digest recomputation**
(bytes at `publication_head` and at `HEAD`) and delegated replay to the
arm path. These are complements, not rivals: digests catch byte
substitution, replay catches a receipt whose bytes are intact but whose
evidence no longer authenticates. Neither subsumes the other. Per consult
point:

| Consult | Digests (both coordinates) | Full semantic replay | Ground |
|---|---|---|---|
| **publication** (one-shot) | yes | **yes** | Cost is irrelevant once; this is the gate the whole transaction exists for. |
| **scheduler pre-arm** | yes | **yes (fail-early)** | The arm's own replay (`arm_readiness.py:6161-6185`) is the LOAD-BEARING check for exactly `freeze-0004.json`, its sidecar, `plan_tree.sha256` and the plan-tree freeze slot — r5 **V-1.iv** says so in terms. Duplicating it early is the ruled G4 pattern ("the latter exists as the refusal itself; the guard makes it fail-early", V-3(b)), not redundancy. |
| **T-0** | yes | yes | Sol is right and I under-specified this (§4.2 had only the launch seam). The head can move and an external file can be swapped between pre-arm and T-0; adopt Sol's re-verify immediately before GO and the five-way GO binding (`sol:492-501`). |
| **launch/consume (`execve`)** | **hash equality only** | no | Sol's cost call (`sol:504`) is right: the T-0 verifier did the walk; the final re-hash closes accidental replacement. |

**Where I keep my position: the arm library boundary.** Sol integrates at
scheduler pre-arm, T-0 and launch — all *scheduler-path* consults. A
direct `scripts/generate_arm_readiness.py arm` invocation therefore mints
an arm receipt for an unpublished family with no publication refusal
anywhere. R-3's consume seam stops that receipt being *consumed*, so the
residual is bounded — but an arm receipt reading GO for an unpublished
family is exactly the artifact a reviewer trusts, and minting it burns
custody. **Recommend both**: Sol's scheduler/T-0/launch fan-out **plus**
my `_gate_family_publication` at the two library boundaries histsem
already uses (`arm_readiness.py:3449-3506` shape), with my anti-deadlock
rule intact — **freeze engages only on the PREDECESSOR pack, never on the
pack being minted**, or `_v4` can never be created (§4.2, tests T-B1/T-B2).
Sol's design does not hit this deadlock only because it does not
integrate at the freeze boundary at all — which also forfeits the `_v5`
payoff that A-1's F2 economics were bought for.

**Second position I keep: the TERMINAL_REVIEW binding (§2.3).** Sol binds
`publication_git.head_tree_oid` (the tree *of* the head) but nothing ties
publication to the tree Ed **terminally reviewed**. R1 clause 3 binds
`head_tree_oid` unconditionally at authoring (`arm_readiness.py:3904-3910`)
and r4-3 makes the terminal-review attestation *the* common derivation
head; carrying that binding past publication costs one blob hash and
turns "published at a tree nobody reviewed" into a refusal.

### D-3. Refusal vocabulary — synthesis

**Does Sol's shape hit my blocking finding?** Yes — and V4 already cures
it (§D-0.2). `readiness_r1_family_publication` is a bare code today; it
explodes at `arm_readiness.py:1468`/`:4457` unless V4's ruled same-commit
delta lands (typed frozensets unioned into `READINESS_REASON_CODES` +
`REASON_TYPE_BY_CODE`) **and** the registry-load closure check refuses
unclosed codes at load. Neither seat may treat that delta as optional; it
is the marker's precondition, and I recommend the magistrate restate it in
the ruling so the S-1 candidate cannot ship the registry without it.

**Which diagnostic vocabulary is right?** Sol's placement, my closure
discipline:

* **One externally visible reason code** — converged. My 30-code
  `familypub_*` set is **withdrawn as a reason-code vocabulary**: a second
  `*_*` code family sitting next to `readiness_*`, `histsem_*` and
  `scheduler_*` invites exactly the census confusion R1 clause 6 exists to
  prevent, and Sol is right that check IDs suffice for diagnosis.
* **But free-form `check_id` strings are untestable for exhaustiveness.**
  Adopt them as a **CLOSED, code-enumerated frozenset**
  (`FAMILY_PUBLICATION_CHECK_IDS`), with a test asserting every refusal
  path maps to a member and that no free-form string is ever emitted —
  the same closed-enumeration instinct D-151 condition 6 applies to the
  pinset chain. My §4.3 list becomes that frozenset with the `familypub_`
  prefix dropped, so nothing can be mistaken for a reason code.
* Keep Sol's rule that a registry which cannot be authenticated refuses
  under `readiness_row_registry_mismatch` and the consumer never fabricates
  the FAMILY_PUBLICATION entry (`sol:442`). That is the correct
  authority-source-first ordering.

**D-3.4 — a defect in Sol's tool self-hash, for the S-0 lane.** "Each
script also self-hashes at execution and refuses if its executing bytes
differ from the committed blob" (`sol:223`) **refuses in S-0**: at the
pinned HEAD these scripts do not exist, and the runsheet requires them to
run from `$INPUT` custody copies (`s0-runsheet.md:141-156`). Repair: bind
to the committed blob in **published** phases; in candidate phase bind to
the digest the S-0 candidate manifest names (§1.3.4), and record both.
Without this the design cannot execute its own clone proof.

### D-4. The join: Ed's confirmation — one artifact, two consumers

**New binding context.** D-151 adopts **O-1-D**, whose condition 2 reads:
"The successor class is DIGEST-CONDITIONAL against Ed's step-6
confirmation-table digest — V-1(vi) exercised, not waived; this is what
makes O-1-D lawful where Option 1 is not"
(`MAGISTRATE-RULING-O1.md:47-50`). So Ed's step-6 table is now
**load-bearing for the pinset**, not only for the family.

**Adjudication: TWO artifacts, not three.**

1. **The marker** — deterministic, immutable from build, contains **no**
   confirmation field (§D-0.1).
2. **Ed's step-6 confirmation table** — ONE artifact, ONE digest, with
   **two sections**: a `family` section (Sol's ordered three-row
   `{profile, pack_id, pack_sha256, freeze_receipt_sha256}` table + the
   marker digest) and a `pinset` section (successor-pinset SHA + counts,
   per D-151 conditions 2-3). Sol's
   `joulewise.d117_family_publication_confirmation.v1` is this artifact's
   family section; it should be generalised, not duplicated.

**Why not three (a family confirmation *and* a pinset confirmation).**
There is exactly one step-6 moment in r4-3's order and one human act; r2
A-5.1 names one gate ("publication ONLY on Ed's confirmed yes over the
exact bytes"). Two separately-digested records of the same act at the
same moment is a second home for one authority (the defect r2 A-2
adjudicated under R1 clause 7's verbatim single-home requirement,
`decision_log.md:9306-9308`) and creates the state where they disagree and
nobody can say which one Ed said yes to. One table, one digest, two
sections; each consumer binds the table digest **and** checks its own
section.

**Why not one (fold the marker into the table).** The table is written
*after* the marker exists and *names* it; folding is the cycle of §D-0.1.

**Three consequences neither seat stated:**

* **The confirmation table is CUSTODY-EXTERNAL and must never enter any
  allowlist.** D-151 condition 7 mints the standing fixed-point rule: "no
  authenticator path ever enters any allowlist, in any transaction"
  (`:70-74`). Under condition 2 the table **is** an authenticator. A
  tracked table inside the 112 would therefore be a V-1(vi) tripwire
  event routing to the derived manifest — not an amendment. This is a hard
  constraint on the join and it also independently re-confirms D-150's
  custody-external placement for the marker's whole family of records.
* **My §5.4 "retrospective tracked anchor" and D-151's fixation are the
  same slot** — "the first commit after window close" (condition 3). They
  should be ONE commit carrying two *new* assertions (successor pinset SHA
  literal + the marker/confirmation digests), with condition 3's
  independent reviewer recomputing **both** against Ed's step-6 table.
  That is strictly stronger than either alone and costs no extra commit.
* **Candidate-mode green is forged-`origin/main` green.** D-151 condition
  4 makes the two-part-green rule material: S-0's clone forges the ref
  (`s0-runsheet.md:85`), so Sol's `origin_main_commit` equality passes
  against a forged OID. The marker verifier must therefore **record the
  forged OID in candidate mode** and no transcript may report candidate
  PASS as published PASS — the same discipline D-151 imposes on the
  histsem suite. Both seats missed this; it lands in the contract text.

**Ownership.** The table is neither marker-specific nor pinset-specific,
so it gets its **own ONE home**: a new
`docs/contracts/ed_step6_confirmation_table.md` (schema, digest rule,
section registry, custody-external + fixed-point constraint). The marker
contract (`docs/contracts/family_publication_marker.md`, new, owning §§2-5
of this design as amended) and the histsem contract
(`receipt_histsem_verifier.md`, already amended by D-151) each *reference*
it and own only their own section's semantics. Homing it inside either
consumer's contract would make the other consumer's authority a
cross-reference into someone else's document — the exact single-home
defect R1 clause 7 forbids.

### D-5. Scheduler receipt v2 — convergence and exact delta

Converged, on independent grounds: Sol from the exact-schema constant
(`scheduler_gates.py:30`) and the exact v1 receipt; me from
`RECEIPT_KEYS` exact-key enforcement (`scheduler_gates.py:132-149`) plus
R-2's ruled precedent that an exact-key receipt takes a version bump
rather than an in-place key add (`schedgate-ruling.md:33-38`). Both seats
add exactly ONE root key.

**Recommended union (mine, minimal):**

```
family_publication = {
  family_id, marker_path, marker_sha256, confirmation_sha256,
  verification_receipt {path, sha256}, publication_head, verdict, refusals
}
```

Dropped from my blind proposal: `body_sha256` and `marker_id` (derivable;
the marker is immutable from build so the file digest suffices) and
`lifecycle_code` (present in `refusals[]` when refusing, derivable from the
registry otherwise). Added from Sol: `confirmation_sha256`,
`verification_receipt`, `verdict`, `refusals`. Kept from mine:
`marker_path` and `publication_head` — the two fields a human reading a
GO receipt actually needs.

Rules carried from Sol unchanged: G5 first; all six G gates evaluate
regardless; `SCHEDULER_GATE_REASON_CODES` unchanged and the nested
refusal not unioned into it; `GO` requires six PASS/RECORD_ONLY **and**
`family_publication.verdict == PASS`; `claim_admissible` false whenever
publication fails.

**Do I concur that the bump is magistrate-adjudicated, not an Ed ruling?
Yes, fully — and I withdraw my §8.1.3 framing**, which listed it under
"Items needing an Ed ruling". Grounds: r5 **V-6** gives this D-144 round
authority over the marker schema+consumer *and* the scheduler mechanical
gates as schema/contract design, and names the owner — "the Fable ruling
on its findings is the MAGISTRATE'S (named owner)"
(`rulings-r5-consolidation.md:159-164`). The bump is a *mechanical
consequence* of exact-key enforcement, not a policy choice, so there is no
discretion at Ed's level to exercise. Sol's added point is right and
should be in the ruling: silently retaining v1 while claiming the marker
is scheduler-bound would be a **false binding**.

### D-6. Remaining disagreements (grounds, for the magistrate to rule)

| # | Disagreement | My position | Sol's | Ground |
|---|---|---|---|---|
| 1 | Arm/freeze **library-boundary** gate | required, in addition to scheduler/T-0/launch | absent (scheduler-path only) | A direct arm invocation otherwise mints a GO-reading receipt for an unpublished family; R-3 blocks consumption, not minting. Cost: one call site per boundary. |
| 2 | Freeze-boundary engagement on the **predecessor** | required (`_v5` requires published `_v4`) | not addressed | This is the A-1/F2 payoff — the reason option (a) was bought. Must carry the anti-deadlock rule or `_v4` is uncreatable. |
| 3 | **TERMINAL_REVIEW** `head_tree_oid` binding | required | absent | Ties publication to the tree Ed reviewed; one blob hash. |
| 4 | Diagnostic IDs | closed, code-enumerated frozenset | free-form `check_id` | Exhaustiveness must be testable; placement is Sol's, closure is mine. |
| 5 | `publication_state: "PUBLISHED"` | delete (nit) | keep | A field with exactly one legal value enables only a refusal that exact-value validation already gives free; the design itself says the assertion is not authoritative without the confirmation. Harmless either way. |

### D-7. Recommendation set for the magistrate

1. **Adopt Sol's spine** for schema placement, custody staging
   (`candidate/`→`published/`), strict head equality, tool self-hash, and
   the single `readiness_r1_family_publication` / CUSTODY code.
2. **Adopt the two-artifact confirmation split**, with the confirmation
   generalised to the **one step-6 table, two sections** shape of §D-4;
   home it in a new `docs/contracts/ed_step6_confirmation_table.md`.
3. **Record as binding**: the table is custody-external and may never
   enter any allowlist (D-151 condition 7); candidate-mode verification
   records the forged `origin/main` OID and candidate green is never
   reported as published green (D-151 condition 4).
4. **Merge fixation**: D-151's post-window-close fixation commit carries
   the marker/confirmation digests alongside the successor-pinset SHA, one
   independent reviewer recomputing both against Ed's table.
5. **Add my three coverage items** (D-6 rows 1-3): arm/freeze library
   boundary, predecessor engagement with the anti-deadlock rule,
   TERMINAL_REVIEW binding.
6. **Restate V4's required same-commit code delta** (typed frozensets +
   `REASON_TYPE_BY_CODE` + registry-load closure check) as an explicit
   precondition of the marker consumer, so S-1 cannot ship the registry
   without it.
7. **Ratify scheduler receipt v2** with the §D-5 union field set, as this
   round's own adjudication — no Ed item.
8. **Fix Sol's S-0 self-hash rule** (§D-3.4) or the clone proof cannot run.
9. **No Ed ruling is required by this design.** My blind §8.1 items 1-3
   are withdrawn or reassigned (V4 owns the code spelling;
   `MAGISTRATE-RULING.md:124-131` owns the registry coordinate; the
   magistrate owns the v2 bump). The only Ed-facing item left is the
   **optional** signed publication tag (§7.5), which remains
   non-blocking.
