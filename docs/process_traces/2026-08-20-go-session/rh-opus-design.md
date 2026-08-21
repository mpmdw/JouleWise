# RECEIPT-HISTSEM-01 — historical receipt-semantics verifier (Opus design seat)

Worktree read at HEAD `bea0648`. All empirical claims below were executed in
that tree; scratch prototype at `rh-opus-scratch/proto.py`.

Authority: `docs/process_traces/2026-08-20-go-session/00-fix-gauntlet-synthesis.md:48-61`
(C1) + `docs/process_traces/2026-08-20-go-session/sol-refuter2-report.md:100-122,147-154`.
Acceptance: `docs/process/state_kernel.json:3062-3092`.

---

## 0. Corpus (measured, not assumed)

**99 legacy PACK receipts**: 9 packs × 11 receipts, every one
`joulewise.arm_readiness_evidence_receipt.v1`. Each pack carries exactly one
`(pack_sha256, head_commit)` pair shared by all 11 of its receipts. So the
verifier's historical work is **9 digest recomputations**, not 99.

| pack | head_commit | receipt pack_sha256 |
|---|---|---|
| `d117_floor_qwen25_1p5b_v1` | `3c8677d982cf…` | `7a41a8788242…` |
| `d117_floor_qwen25_7b_v1` | `6193379490de…` | `34f07db7db66…` |
| `d117_contrast_…_v1` | `c3d805ee9462…` | `5390a03aa5b9…` |
| `d117_floor_qwen25_1p5b_v2` | `54f990d156ee…` | `1b3892f4f40a…` |
| `d117_floor_qwen25_7b_v2` | `54f990d156ee…` | `7ada4f4f1e0c…` |
| `d117_contrast_…_v2` | `54f990d156ee…` | `edd0eaf9efcb…` |
| `d117_floor_qwen25_1p5b_v3` | `1d3873bb7a37…` | `b170fe0bb02f…` |
| `d117_floor_qwen25_7b_v3` | `1d3873bb7a37…` | `bd82f7da900a…` |
| `d117_contrast_…_v3` | `1d3873bb7a37…` | `07dff08b3200…` |

---

## 1. Git mechanics — ANSWERED, EXECUTED

### 1a. `committed_pack_tree_sha256` cannot do it. Two hard blockers.

`joulewise/arm_readiness.py:2553`:

- **`HEAD` is hardcoded** in the tree read: `arm_readiness.py:2563` —
  `_run_git(repository, "ls-tree", "-rz", "--full-tree", "HEAD", "--", pack_relative)`.
  No commit parameter exists; the signature is `(pack_root)` only.
- **It requires the worktree to equal the tree it hashes.** The framing loop
  reads `raw = path.read_bytes()` from disk (`arm_readiness.py:2658`) and
  refuses `readiness_pack_digest_mismatch` when disk ≠ blob
  (`arm_readiness.py:2663-2667`); the disk/committed namespace reconciliation
  at `arm_readiness.py:2636-2651` refuses untracked/missing entries. A
  historical tree has files the worktree does not (and vice versa), so this
  function structurally cannot describe any commit but the checked-out one.

**No checkout is needed anyway** — the equivalent function is pure-git.

### 1b. The equivalent: `historical_pack_tree_sha256(repo, commit, pack_relative)`

Same D-134 framing (`PACK_DIGEST_DOMAIN`, `arm_readiness.py:43`), two
substitutions:

1. `git ls-tree -rz --full-tree <commit> -- <pack_relative>` instead of `HEAD`
   (mirrors `arm_readiness.py:2563`) — supplies both the mode and the blob OID,
   so no `path.stat()` is needed.
2. `raw = git cat-file blob <oid>` instead of `path.read_bytes()`
   (mirrors the `_run_git(repository, "cat-file", "blob", oid)` already at
   `arm_readiness.py:2659`) — and **drop every disk-side check**
   (`arm_readiness.py:2605-2651`, `:2663-2667`), which is a *current-worktree*
   integrity property, not a historical one.

Framing bytes are then identical, because `committed_pack_tree_sha256` has
already proven `raw == blob` before framing (`arm_readiness.py:2663`). Same
admissibility gates carry over verbatim: mode ∈ {100644,100755} & type blob
(`:2590-2594`), UTF-8 paths (`:2581-2586`), no duplicates (`:2595-2599`),
non-empty (`:2600-2603`), bytes-sorted iteration (`:2653`).

### 1c. Executed — 9/9 exact matches

```
MATCH  d117_contrast_..._v1  c3d805ee94  5390a03aa5b90224 == receipt   nfiles 98   evfiles 0
MATCH  d117_contrast_..._v2  54f990d156  edd0eaf9efcbb6f9 == receipt   nfiles 98   evfiles 0
MATCH  d117_contrast_..._v3  1d3873bb7a  07dff08b32006a0f == receipt   nfiles 98   evfiles 0
MATCH  d117_floor_1p5b_v1    3c8677d982  7a41a8788242c18f == receipt   nfiles 117  evfiles 0
MATCH  d117_floor_1p5b_v2    54f990d156  1b3892f4f40a5a36 == receipt   nfiles 117  evfiles 0
MATCH  d117_floor_1p5b_v3    1d3873bb7a  b170fe0bb02fa29b == receipt   nfiles 117  evfiles 0
MATCH  d117_floor_7b_v1      6193379490  34f07db7db669838 == receipt   nfiles 117  evfiles 0
MATCH  d117_floor_7b_v2      54f990d156  7ada4f4f1e0cdd6d == receipt   nfiles 117  evfiles 0
MATCH  d117_floor_7b_v3      1d3873bb7a  bd82f7da900a00fe == receipt   nfiles 117  evfiles 0
```

**C1 is closable today, on the committed artifacts, with no checkout, no
`git worktree add`, no network.** The gap was never "unrecomputable"; it was
"never recomputed."

### 1d. Differential self-test (the anti-drift pin)

`historical_pack_tree_sha256(repo, "HEAD", rel) == committed_pack_tree_sha256(root)`
— executed, equal on `d117_floor_qwen25_1p5b_v3`
(`1e3f1fa31027e570…`), `d117_floor_qwen25_1p5b_v1` (`5def6e514116184d…`),
`metrology_v1` (`b2462b3d56048388…`). This is mandatory acceptance: it proves
the historical function is D-134's framing rather than a re-derivation that
drifted, and it goes red the moment anyone edits `arm_readiness.py:2653-2676`.

### 1e. Two facts the recompute revealed — both become checks

- **Pre-authoring invariant.** At every receipt's `head_commit` the pack tree
  contains **zero** files under `arm_readiness.evidence/`,
  `arm_readiness.freeze.receipts/`, `arm_readiness.sources/`,
  `identity_pin_projection.receipts/` (measured: `evfiles 0`, all 9). The
  recorded `pack_sha256` is by construction the *pre-authoring* digest. Any
  receipt whose `head_commit` tree already contains custody content is
  self-inconsistent.
- **Post-authoring delta envelope.** `git diff --name-status <head_commit> HEAD -- <pack>`
  is startlingly regular across all 9 packs: **37 additions, all four confined
  to the custody directories above; zero deletions**; modifications drawn only
  from `{plan_tree.json, plan_tree.sha256, producer_contract.json,
  generate_configs.py}` (`plan_tree.*` in 9/9 — freeze minting retargets
  `arm_attachments.arm_readiness.freeze_receipt`; `producer_contract.json` in
  6/9; `generate_configs.py` in the three `_v1` packs only). This delta is
  exactly what the C1 attack must hide in, which makes pinning it the highest-
  yield check in the design (§2 K7).

---

## 2. Per-receipt checks

Two coordinate systems, and conflating them is the design's main failure mode:

- **HISTORICAL** (`head_commit`): `pack_sha256`, pre-authoring invariant.
- **CURRENT** (`HEAD`): sidecar → freeze → plan binding. It *must* be HEAD,
  because `plan_tree.json` is **modified after** `head_commit` in 9/9 packs
  (measured) — the freeze mint writes the `freeze-0003` reference into it. A
  design that checks the plan binding historically refuses every pack.

Per pack (9 iterations), then per receipt (11 each):

**K1 `histsem_receipt_not_committed`** — receipt bytes, its `.sha256` sidecar,
the freeze receipt, its sidecar, `plan_tree.json`, `plan_tree.sha256` each
equal their `HEAD` blob. Reuses `_git_blob_at_head` (`arm_readiness.py:2910`).
Cheap; forces the attacker to commit, which is what makes K7 bite.

**K2 `histsem_receipt_head_malformed`** — `head_commit` (or, for older shapes,
`derivation_commit`; same fallback as `arm_readiness.py:4245`) is present and
40-hex lowercase; `pack_sha256` is 64-hex lowercase; `schema_version ==
joulewise.arm_readiness_evidence_receipt.v1`. Malformed ⇒ refuse, never skip.

**K3 `histsem_commit_unresolvable` / `histsem_history_shallow` /
`histsem_commit_off_lineage`** — the named unavailable-history family:
- `git rev-parse --is-shallow-repository` is `true` ⇒ `histsem_history_shallow`
  (measured `false` here; the `build` job at `.github/workflows/ci.yml:160`
  *is* shallow — hence §3's job placement).
- `git cat-file -e <head_commit>^{commit}` fails ⇒ `histsem_commit_unresolvable`.
- `git merge-base --is-ancestor <head_commit> HEAD` fails ⇒
  `histsem_commit_off_lineage`. **Hard.** Measured: all 5 distinct commits are
  ancestors of both `HEAD` and `origin/main`.
- `git merge-base --is-ancestor <head_commit> origin/main` fails ⇒
  `histsem_commit_unpublished`, **advisory in pre-arm** (a fresh mint is
  legitimately unpushed), **hard in CI**. Do not make this hard everywhere or
  the `_v4` mint cannot be gated on the night it is minted.

**K4 `histsem_pack_absent_at_commit` / `histsem_historical_tree_anomalous`** —
`ls-tree` at `head_commit` returns nothing for the pack path, or returns a
non-blob / non-{100644,100755} / non-UTF-8 / duplicate entry.

**K5 `histsem_pack_digest_mismatch`** — `historical_pack_tree_sha256(repo,
head_commit, pack_relative) != receipt["pack_sha256"]`. **This is C1's literal
closure**, the check `arm_readiness.py:4248-4262` skips whenever
`expected_pack_sha256 is None` — which is always, for PACK evidence
(`arm_readiness.py:5253-5264`, `:5383-5392`), and deliberately so at mint
(`arm_readiness.py:5507-5528`, `pack_sha256=None, head_commit=None`).

**K6 `histsem_historical_tree_not_pre_authoring`** — the historical tree
contains any path under the four custody directories. Enforces §1e.

**K7 `histsem_post_authoring_delta_unexpected`** — the `head_commit → HEAD`
delta for the pack must equal the pinned per-pack envelope (§4): exact added-
path set, exact modified-path set, zero deletions. **This is the check that
actually stops the C1 attack**, because K5 alone lets an attacker who edits a
*config* file at HEAD keep the receipt's historical claim truthful-looking; K7
makes any post-freeze edit to generator-owned pack content a named refusal.

**K8 `histsem_sidecar_mismatch`** — `sha256(receipt bytes)` equals the
receipt's `.sha256` sidecar in GNU form (`gnu_sidecar`, as
`arm_readiness.py:4210-4215` does). Same for the freeze receipt's sidecar and
`plan_tree.sha256`.

**K9 `histsem_freeze_binding_mismatch`** — the freeze receipt's `evidence[]`
entry for this receipt is byte-exactly the 7-key tuple recomputed from the
receipt (`evidence_id, receipt_kind, namespace, path, sha256, schema_version,
status`) — the same equality `arm_readiness.py:4234-4244` performs. Plus:
every one of the pack's 11 committed receipts appears in `evidence[]` and
`evidence[]` names no receipt absent from disk (closes add/remove, which the
per-item loop cannot see).

**K10 `histsem_plan_binding_mismatch`** — `plan_tree.json`
`arm_attachments.arm_readiness.freeze_receipt.{path,sha256}` resolves to the
freeze receipt and matches its digest (measured: `freeze-0003.json` /
`0abfddb1…` for 1p5b_v3); `pack_identity.plan_sha256` in the freeze receipt
equals `sha256(calibration_plan.json)`; `plan_tree.sha256` matches
`plan_tree.json`. Chain: receipt → sidecar → freeze → freeze sidecar → plan
tree → plan tree sidecar → plan.

**K11 `histsem_predecessor_binding_mismatch`** — free extra coverage, measured
green: the successor freeze receipt's `predecessor.pack_sha256` equals
`committed_pack_tree_sha256(predecessor pack)` at HEAD
(`95f7c51ca4f2833a…` / `e5ec0f74df3a61da…` / `2fe51b037ad063f9…`, all MATCH),
and `predecessor.freeze_receipt.sha256` matches the predecessor's
`freeze-0002.json` bytes. Chains the three families back through `_v2` to
`_v1`.

**K12 `histsem_pinset_mismatch` / `histsem_pinset_invalid`** — every field of
§4's pinset row is reproduced. This is what converts the run from "self-
consistent" to "matches a governed, human-approved expectation."

**Deliberately NOT re-implemented:** `facts[].source_sha256` → pack file. It
is already enforced at replay (`arm_readiness.py:4284-4321`, refusal at
`:4304`) — measured 108/108 green here. Offered as an opt-in `--recheck-facts`
for offline runs; not an acceptance item. Also NOT re-checked: expiry
(`valid_until_monotonic_ns`) and `boot_session_id`. The verifier is a
*historical* instrument; the `_v3` fuse already lapsed
(`RUN_STATE.md:41-45`) and enforcing expiry would make it refuse the entire
corpus it exists to attest.

---

## 3. Placement

### 3a. The seam precedent, applied

`sampler_teardown` is the template and it was learned the expensive way: the
first cut edited a pinned file, was remanded, and was restructured into a new
unpinned module that plugs into an *unpinned caller*
(`joulewise/sampler_teardown.py:112-149` `intercept_popen()`, wired at
`joulewise/controller.py:1645-1655`, call sites `:1018`, `:1227`, fail-closed
raise `:1631-1642`, tests `tests/test_sampler_teardown.py` +
`tests/test_controller.py:1704-1725`). Shape: **new module owns the check;
one small wrapper in the caller; every call site routes through it; the frozen
surface stays byte-identical.**

### 3b. Files

| artifact | role |
|---|---|
| `joulewise/receipt_histsem.py` | new, unpinned. Owns `historical_pack_tree_sha256`, `HistoricalSemanticsError`, `HISTSEM_REASON_CODES`, `verify_pack(...)`, `verify_all(...)`. Imports `arm_readiness` primitives (`_run_git` :2520, `_repository_and_pack_relative` :2540, `_git_blob_at_head` :2910, `sha256_bytes` :1026, `gnu_sidecar`, `PACK_DIGEST_DOMAIN` :43); **edits none of it.** |
| `scripts/verify_receipt_histsem.py` | new CLI. House pattern: `main(argv) -> int`, `raise SystemExit(main())`, canonical JSON to stdout, **exit 0 = PASS / 2 = refusal** (matches `scripts/validate_gate_packet.py:546-549,567-576` and `scripts/author_arm_readiness_evidence.py`). `--pinset`, `--pack-root` (repeatable), `--require-published`, `--output`. |
| `scripts/receipt_histsem/pinset_v1.json` | new governed pinset (§4). Mirrors `scripts/floor_mint_pinsets/mint1.json`. |
| `tests/test_receipt_histsem.py` | new. |
| `scripts/generate_arm_readiness.py` | **the one edit to existing code** — 3-line pre-arm seam. |
| `.github/workflows/ci.yml` | one step. |

### 3c. r6-pin compliance — clean

The four r6-pinned files are `joulewise/powermetrics_fiducial.py`,
`joulewise/uncertainty_evidence.py`, `joulewise/adapters/powermetrics.py`,
`joulewise/reduce.py` (declared
`configs/calibration/calibration_acceptance_d079_v2_n17_r6.json:39-43`,
enumerated `joulewise/calibration_bracketing.py:180-185`, D-138
`docs/decision_log.md:8791-8800`, hazard block `RUN_STATE.md:95-105`, enforced
by `tests/test_powermetrics_fiducial.py:1571-1576`). **None appears above.**

### 3d. The non-obvious constraint: no new readiness reason code

`ArmReadinessError` refuses any unregistered code
(`joulewise/arm_readiness.py:946-947`) against
`READINESS_REASON_CODES` (`:192-201`). Registering one costs **four**
coordinated changes: the category frozenset + `REASON_TYPE_BY_CODE`
(`:202-211`); the hard cardinality pin
`tests/test_arm_readiness_schemas.py:1003` (`assertEqual(len(...), 47)`); the
scrape-census `tests/test_arm_readiness_integration.py:546-567`; and
`_derive_reason_code_coverage` (`joulewise/arm_readiness_evidence.py:1394-1440`),
which re-derives from **committed HEAD bytes of `arm_readiness.py`** and
refuses at `:1428-1432` — i.e. it would perturb the very
`REASON_CODE_COVERAGE` receipts this row exists to attest.

**Therefore `HISTSEM_REASON_CODES` is a disjoint namespace owned by
`receipt_histsem.py`, all codes prefixed `histsem_`, asserted disjoint from
`READINESS_REASON_CODES` by a test.** Direct precedent: the scheduler-gate
design walls its codes out of `READINESS_REASON_CODES`
(`docs/process_traces/2026-08-20-go-session/schedgate-opus-design.md:67-79`).

### 3e. CI wiring

`.github/workflows/ci.yml`, job `test`, insert after the `gen_state.py --check`
step at `.github/workflows/ci.yml:25-26`. That job already checks out full
history — `fetch-depth: 0` at `.github/workflows/ci.yml:17-21`, with a comment
(`:19-20`) that is literally the precedent for needing history. Run
`--require-published` there (K3's `origin/main` ancestry hard).

Caveat: job `test` is an 8-way matrix (`:12-15`). Cost measured: 9 packs,
~1000 `git cat-file` invocations, seconds. Acceptable; if it isn't, guard with
`if: matrix.python == '3.13' && matrix.shard == 0`. **Do not** add it to job
`build` (`:157-173`) — its checkout at `:160` is shallow and K3 would refuse.

### 3f. Pre-arm seam

Arm issuance is `generate_arm_receipt` (`joulewise/arm_readiness.py:6099`);
its only production caller is the CLI `scripts/generate_arm_readiness.py`,
dispatch at `:108-113`, inside `main()` at `:89`.

**Hook: `scripts/generate_arm_readiness.py:92-96`, inside the existing `try:`,
before the command dispatch, for `args.command in {"arm", "freeze"}`.**

```
if args.command in {"arm", "freeze"}:
    receipt_histsem.gate(args.pack_root)      # raises HistoricalSemanticsError
```

plus one new `except HistoricalSemanticsError` arm alongside
`scripts/generate_arm_readiness.py:120` emitting the identical refusal envelope
shape (`{"status":"REFUSE","arm_disposition":"NO_GO","reason_codes":[…],"detail":…}`,
exit 2) with the `histsem_*` vocabulary.

Why here and not deeper: the CLI is unpinned and read-only-guarded
(`_pack_snapshot` before/after, `:92-95`, `:121-125`), so a gate that only
reads cannot violate the no-write invariant; it covers 100% of real arms; and
it keeps `joulewise/arm_readiness.py` byte-identical, which preserves arm-
receipt replay comparison and the schema/coverage pins in §3d. Including
`freeze` in the gate is the higher-value half: it refuses to mint a *new*
generation on top of a pack whose history no longer verifies, which is exactly
the `_v4` case (§5c).

Rejected: `scripts/launch_window.py:93-128` (post-arm — too late);
`scripts/prewindow_check.sh:16-19` (self-disclaims gate authority; rejected for
schedgate at `schedgate-opus-design.md:82-87`); inside `generate_arm_receipt`
itself (would edit the governed ceremony surface, §3d).

---

## 4. The pinset

`scripts/receipt_histsem/pinset_v1.json`, one row per pack:

```json
{"schema_version":"joulewise.receipt_histsem_pinset.v1",
 "packs":[{"pack_id":"d117_floor_qwen25_1p5b_v3",
   "pack_path":"configs/campaigns/d117_floor_qwen25_1p5b_v3",
   "head_commit":"1d3873bb7a37e9363202429f14587c85a0b4efc0",
   "historical_pack_sha256":"b170fe0bb02fa29b829203b759030048a1a5442f91603e000e18bb0f23845ddb",
   "current_pack_sha256":"1e3f1fa31027e57053c7d26bacf2f373cf2c9ed840ee2bb3befafd99302d63f6",
   "freeze_receipt":{"path":"arm_readiness.freeze.receipts/freeze-0003.json",
                     "sha256":"0abfddb13fe8c5e69df3e6be5e2e7efe28d3690b6947d5ed850fcb9652f6ec64"},
   "plan_sha256":"9ab4776f3c416284d6d01a5a49587eedcdfbcb8ef61428cdc1046e9b9d74a072",
   "receipt_count":11,
   "post_authoring_delta":{"added":[…37 paths…],
                           "modified":["plan_tree.json","plan_tree.sha256","producer_contract.json"],
                           "deleted":[]},
   "published_anchor":"docs/process/ed-s5-mint-decision-2026-08-19.md:82-84"}]}
```

Three properties make this a pin rather than a snapshot:

1. **Independent corroboration.** `current_pack_sha256` and
   `freeze_receipt.sha256` for all three `_v3` packs are already published, by
   hand, in the S5 confirmation table
   (`docs/process/ed-s5-mint-decision-2026-08-19.md:82-84` —
   `0abfddb1…/1e3f1fa3…`, `f232d076…/6d0b9b75…`, `f32bd3a8…/0d071941…`),
   verified equal to today's tree. The `_v2` predecessor freeze digests are
   published at `:78-80`. The pinset must be *checked against* that table when
   minted, not generated and trusted.
2. **Byte pin.** `tests/test_receipt_histsem.py` asserts a literal
   `sha256(pinset bytes)`, exactly the idiom of
   `tests/test_powermetrics_fiducial.py:1556-1559`. Any pinset edit turns a
   test red and surfaces in review.
3. **Extended by ruling, never regenerated.** No `--update` flag. A new family
   (`_v4`) gets a row at its S5, alongside its confirmation table.

---

## 5. Truth boundary

### 5a. What it establishes

Each legacy receipt's *coordinate claim* — "I describe pack tree X at commit
C" — is now arithmetically reproducible from the repository's own history,
and the tree at C is pre-authoring, on-lineage, and differs from today's tree
only by a pinned envelope. **Byte-consistency is upgraded to
history-consistency.**

### 5b. What it does NOT claim

- **Not an adversary defence.** D-139 A1 (`docs/decision_log.md:10049-10060`)
  rules the in-process adversary out of model family-wide; repo-write trust is
  language-independent. This verifier does not defend against someone who can
  rewrite git history *and* re-mint the pinset *and* revise the published S5
  table. What it changes is the **cost and visibility** of forgery: C1's
  attack was a coherent edit of ~6 files in one commit; it now additionally
  requires a history rewrite that breaks `merge-base --is-ancestor` against
  `origin/main` and contradicts a hand-published digest table. That is a
  detectability claim, not an integrity guarantee, and the paper must say so
  in those words.
- **Not semantic re-derivation.** It does not re-run the checks a receipt
  attests. `evidence-reason-code-coverage.json` says the census passed at
  `1d3873bb…`; the verifier confirms *which tree that sentence is about*, not
  that the census would pass again.
- **Not a D-134 readiness row.** It adds no row to `desk.current_pack`
  (siblings enumerated
  `docs/process_traces/2026-08-11-5c-readiness-contract/consult.md:211-225`)
  and no readiness reason code (§3d). It is an *external* gate, per the
  acceptance wording "outside the immutable frozen packs"
  (`docs/process/state_kernel.json:3085`).
- **Not a generator `--check` claim.** The gauntlet ruled receipt semantics
  outside frozen check-mode
  (`00-fix-gauntlet-synthesis.md:22-32`; execution-order proof
  `sol-refuter2-report.md:90-98`). This verifier does not reopen that and must
  not be described as fixing the `--check` observation, which was reclassified
  a non-defect (`00-fix-gauntlet-synthesis.md:36-44`).
- **Not a fuse/liveness check** (§2 close).

### 5c. The archival `_v3` coordinate

`1d3873bb7a37e9363202429f14587c85a0b4efc0` is now an **archival** coordinate,
not an operational one: the `_v3` fuse lapsed by ruling ~17:00Z 2026-08-20 and
the `_v4` re-freeze is compelled by executed code mechanics
(`RUN_STATE.md:41-45`). Consequences the design must own:

1. For `_v1/_v2/_v3` this verifier is **retrospective attestation**. Its CI
   value is drift detection over 99 archival receipts — real, and the only
   thing standing between those receipts and "trust the chain."
2. The **pre-arm gate first binds on `_v4`**. Which means: **mint the `_v4`
   pinset row inside the `_v4` transaction's S5, not afterwards.** Retro-
   fitting the pinset to `_v4` later reproduces C1's exact shape — an expected
   value nobody supplied. This is the single strongest scheduling
   recommendation in this spec, and it costs the `_v4` transaction ~one step.
3. `_v4` receipts will carry a `head_commit` that is briefly unpushed at mint
   time. K3's split (ancestor-of-`HEAD` hard, ancestor-of-`origin/main`
   advisory pre-arm / hard in CI) exists exactly for that night.

---

## 6. Defect-shaped regression

`tests/test_receipt_histsem.py`. The regression must reproduce **C1's own
attack**, not a byte corruption — the gauntlet already proved byte corruption
fails closed (`00-fix-gauntlet-synthesis.md:14-21`).

**Fixture** — a real throwaway git repo in `tmp_path` (`git init`, two
commits), holding a miniature pack: `calibration_plan.json`,
`plan_tree.json` + sidecars, 2-3 config files.

- **C1**: commit generator content only. Record `D1 =
  historical_pack_tree_sha256(repo, C1, pack)`.
- **C2**: author one evidence receipt with `pack_sha256=D1`,
  `head_commit=C1`; write its `.sha256`; mint a freeze receipt binding it;
  retarget `plan_tree.json` + `plan_tree.sha256`. Commit.

**T1 — baseline PASS.** `verify_pack` returns PASS at C2.

**T2 — THE DEFECT SHAPE (the load-bearing test).** At C3, edit a *config* file
inside the pack, then coherently repair the whole chain: receipt digest →
sidecar → freeze `evidence[]` entry → freeze sidecar → `plan_tree` freeze sha
→ `plan_tree.sha256`. Leave `pack_sha256=D1`, `head_commit=C1` untouched — the
receipt now truthfully names a tree that no longer describes the pack. Commit.
Then assert **both halves**:

- **CONTROL (proves the gap was real):** at C3,
  `committed_pack_tree_sha256(pack)` succeeds (disk == HEAD), and
  `arm_readiness._authenticate_generic_evidence_item(item, pack, pack)` —
  called exactly as frozen PACK evidence is called, i.e. **without**
  `expected_pack_sha256` (`arm_readiness.py:5253-5264`) — **returns without
  raising.** A regression that omits this control does not prove C1.
- **NEW:** `verify_pack` refuses `histsem_post_authoring_delta_unexpected`.

**T3 — fabricated historical digest.** Same coherent rewrite, but the attacker
also rewrites `pack_sha256` to the *current* digest. Chain still coherent; K5
refuses `histsem_pack_digest_mismatch`.

**T4 — off-lineage re-anchor.** Attacker creates a side commit containing the
edited tree and points `head_commit` at it. K5 would pass; K3 refuses
`histsem_commit_off_lineage`.

**T5 — evidence add/remove.** A twelfth receipt is added and bound into
`evidence[]`, or one is removed from both: `histsem_freeze_binding_mismatch`
(the per-item loop cannot see set changes — this is why K9 checks the set).

**T6 — unavailable history**, each named separately:
`histsem_history_shallow` (clone `--depth=1`), `histsem_commit_unresolvable`
(unknown SHA), `histsem_pack_absent_at_commit`,
`histsem_receipt_head_malformed`, `histsem_pinset_invalid`.

**T7 — differential self-test over the real repo.** For all 9 packs:
`historical_pack_tree_sha256(repo, "HEAD", rel) == committed_pack_tree_sha256(root)`
(§1d). Marked as the anti-drift pin.

**T8 — full-corpus green.** `verify_all` PASSes over the real 9 packs / 99
receipts against the committed pinset, and the pinset's own sha256 matches its
literal pin.

**T9 — vocabulary disjointness.** `HISTSEM_REASON_CODES ∩
READINESS_REASON_CODES == ∅`, and every member is raised somewhere (the
census idiom of `tests/test_arm_readiness_integration.py:546-567`).

**T10 — pre-arm seam.** `scripts/generate_arm_readiness.py arm` on a tampered
pack exits 2 with a `histsem_*` code, and the pack-byte no-write invariant
(`scripts/generate_arm_readiness.py:92-95,121-125`) still holds on the refusal
path.

---

## 7. WRITE_SCOPE and stages

Six stages, each its own delegated session with an exhaustive `WRITE_SCOPE`.
Stage 2 before stage 3 is deliberate: the attack test defines the API before
the pinset freezes any shape.

| # | stage | WRITE_SCOPE | gate |
|---|---|---|---|
| S1 | `historical_pack_tree_sha256` + error/vocabulary + `verify_pack` skeleton; T7, T9 | `["joulewise/receipt_histsem.py","tests/test_receipt_histsem.py"]` | T7 green on all 9 packs — the differential self-test is the whole point of S1 |
| S2 | K1–K11 + the defect-shaped regression T1–T6 (with its CONTROL half) | `["joulewise/receipt_histsem.py","tests/test_receipt_histsem.py"]` | T2's control assertion must be **observed failing before the new check exists** and passing after — record both in the report |
| S3 | pinset mint + K12 + T8; check every `_v3` value against the S5 table by hand | `["scripts/receipt_histsem/pinset_v1.json","joulewise/receipt_histsem.py","tests/test_receipt_histsem.py"]` | lead verifies the 6 `_v3` digests against `ed-s5-mint-decision-2026-08-19.md:82-84` **itself** (rule 1) |
| S4 | CLI + CI step | `["scripts/verify_receipt_histsem.py","tests/test_receipt_histsem.py",".github/workflows/ci.yml"]` | exit 0/2 discipline; CI green; not added to job `build` |
| S5 | pre-arm seam + T10 | `["scripts/generate_arm_readiness.py","joulewise/receipt_histsem.py","tests/test_receipt_histsem.py"]` | diff on `generate_arm_readiness.py` ≤ ~12 lines; `joulewise/arm_readiness.py` byte-identical (`git diff --stat` must show it absent) |
| S6 | kernel row closure + decision-log entry; `scripts/gen_state.py` regenerates `TASK_QUEUE.md`/`RUN_STATE.md` | `["docs/process/state_kernel.json","docs/decision_log.md","TASK_QUEUE.md","RUN_STATE.md"]` | `scripts/gen_state.py --check` clean (`.github/workflows/ci.yml:25-26`) |

**Standing prohibitions for every stage brief, stated verbatim:**

- `joulewise/powermetrics_fiducial.py`, `joulewise/uncertainty_evidence.py`,
  `joulewise/adapters/powermetrics.py`, `joulewise/reduce.py` — the four
  r6-pinned files — are OUT OF SCOPE in all six stages
  (`RUN_STATE.md:95-105`).
- `joulewise/arm_readiness.py` and `joulewise/arm_readiness_evidence.py` are
  READ-ONLY in all six stages. No new `READINESS_REASON_CODES` member (§3d).
- No file under `configs/campaigns/**` is written. The verifier reads.
- Effort: S1 `high`; S2 `xhigh` (adversarial/judgment-dense); S3 `high`;
  S4 `high`; S5 `xhigh` (governed-ceremony seam); S6 `high`.

---

## 8. Positions I expect to defend in debate

1. **K7 (delta envelope), not K5, is the check that closes C1.** K5 is the
   acceptance criterion's literal text and it must exist, but K5 alone is
   defeated by an attacker who edits pack content *after* the freeze and
   leaves the historical claim honest. Measuring the delta across all 9 packs
   (37 adds / 0 deletes / ≤4 modified paths) is what made this visible; a
   design written from the reports alone lands on K5 and stops.
2. **The plan binding is checked at HEAD, not at `head_commit`.** Measured:
   `plan_tree.json` differs between the two in 9/9 packs. A historical plan
   check refuses the whole corpus.
3. **New reason codes go in a `histsem_*` namespace, never in
   `READINESS_REASON_CODES`** — the registry has a hard cardinality pin at 47
   (`tests/test_arm_readiness_schemas.py:1003`) and a coverage census re-derived
   from committed HEAD bytes
   (`joulewise/arm_readiness_evidence.py:1394-1440`).
4. **Gate `freeze` as well as `arm`.** Gating only `arm` leaves the compelled
   `_v4` mint ungated at the exact moment it matters.
5. **Mint the `_v4` pinset row inside the `_v4` S5.** Retrofitting it later
   reproduces C1's shape verbatim.
6. **The regression is not done without its control half** — proving the
   pre-existing chain accepts the tamper is what makes it defect-shaped rather
   than merely a new assertion.
