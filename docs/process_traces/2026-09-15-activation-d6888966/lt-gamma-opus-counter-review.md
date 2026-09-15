# GAMMA roots rename — Opus counter-review (gate ledger row 6)

- Reviewer: Opus 5 (1M), lieutenant seat, read-only.
- Opened: Tue Sep 15 07:23:13 PDT 2026 (clock read).
- Target: worktree `/Users/edr/code/JouleWise-wt-ref-gamma`, detached at `678d9bcc`.
- Diff: `git -C /Users/edr/code/JouleWise-wt-ref-gamma diff 664b3f6c..678d9bcc` — three files.
- Prior lens read: `/tmp/magistrate-d6888966/13-gamma-refuter-astra.md` (contract-lens refuter, FIX-FIRST on verification only).
- Lens: counter-review — design-level questions the refuters do not ask. No file in the target worktree
  was modified; no git state-changing command was run; canonical root and night-custody untouched.

## Verdict

**LANDABLE.** The one-line rename at
`configs/campaigns/d117_contrast_v5/generate_configs.py:2697` is the correct cure, both new regressions
are defect-shaped and mutation-proven, and nothing on `main` is invalidated. Two should-fix findings
(F2, F3) are **out of this diff's scope** and belong in the queue, not in this head. Two nits (F4, F5)
are optional and could ride a later touch of these files.

The prior refuter's blocker R1 ("FIX-FIRST for verification") is **an artifact of its runner's denied
`/tmp` writes, not a property of the head**. Re-executed here with writable `/tmp`, everything it could
not run passes or kills. R1 is discharged; see §Executed evidence.

## Executed evidence (this session, this worktree)

All commands run as `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest ...` from
`/Users/edr/code/JouleWise-wt-ref-gamma`.

| # | What | Result |
|---|---|---|
| E1 | The two new regressions, focused | `Ran 2 tests ... OK` |
| E2 | `tests.test_d117_contrast_v5_pack` + `tests.test_d117_floor_qwen3_v5_generate` | `Ran 58 tests ... OK` |
| E3 | `tests.test_gamma_unit_roster_guard` + `tests.test_issue_g2a_prefill_prompt_pin` + `tests.test_campaign_generator_core` | `Ran 19 tests ... OK` |
| E4 | `tests.test_d165_dominance_closeout` (imports the generator directly) | `Ran 59 tests ... OK` |
| E5 | **Mutation 1** — generator reverted to `{"claim_leaf", "bound_leaf"}` in memory (`/tmp/gamma-cr/mut1.py`, original `__file__` preserved so `REPO_ROOT` still resolves) | **KILLED by both tests.** Pack test fails on the mapping assert; T-0 test fails on the **positive** path with `T0EvidenceAuthoringError: arm roots do not derive from frozen leaves` at `arm_readiness_evidence_t0.py:1020` — i.e. it reproduces the production defect exactly |
| E5b | Historical sidecar integrity at this head: `plan_tree.sha256` vs `shasum -a 256 plan_tree.json` for contrast `_v1`/`_v2`/`_v3` | All three **match** (`8c53a834…`, `12ef6c10…`, `788f1a20…`) — no frozen byte disturbed |
| E6 | **Mutation 2** — reader at `joulewise/arm_readiness_evidence_t0.py:1017-1018` changed to require the LEGACY pair (`/tmp/gamma-cr/mut2.py`) | **KILLED.** `AssertionError: T0EvidenceAuthoringError not raised` at `tests/test_arm_readiness_evidence_t0.py:941` |

Mutation shape note: E5 and E6 mutate **production call sites** (the generator's emit, the reader's
accept predicate) and are exercised through the real `generator.generate` and the real
`t0._root_observation`, not through today's artifacts — the counterfactual rule is satisfied in both
directions.

## Findings

### F1 — Prior refuter's blocker R1 is discharged. Severity: **info (resolved)**
`/tmp/magistrate-d6888966/13-gamma-refuter-astra.md` R1, citing
`tests/test_d117_contrast_v5_pack.py:953` and `tests/test_arm_readiness_evidence_t0.py:912`. Its own V3
probe shows the cause: `PermissionError: [Errno 1] Operation not permitted: '/tmp/gamma-refute-…'`. Every
one of its 135 errors is `TemporaryDirectory` setup, and its focused failures V4/V5 are the same. Under a
runner with writable `/tmp` the same targets are green (E1–E4) and both withheld mutations kill (E5, E6).
Nothing in the head needs fixing for R1.

### F2 — The plan-tree `roots` schema has **no ONE home**. Severity: **should-fix, out of scope for this diff**
This is the question the brief asked me to answer, and the answer is the finding: **no contract or spec
names these keys.** Searched `docs/contracts/` (34 files), `docs/specs/`, and `docs/campaign_packs/` for
`claim_root_leaf` / `bound_root_leaf` / `plan_tree` + `roots`: zero schema definitions. The only mentions
anywhere in `docs/` are *narrative* — run reports and process traces recording the bug after the fact
(`docs/run_reports/2026-08-18-t10-session.md:382`;
`docs/process_traces/2026-09-13-activation-24b9d3dd/64-r3-desk-proof-research-opus-report.md:50`) — plus an
acceptance sentence in `docs/process/state_kernel.json:4809`.

The schema therefore lives only in code, in **two readers and ten emitters**:

- readers: `joulewise/arm_readiness_evidence_t0.py:1014-1020`, `joulewise/arm_readiness.py:8505-8521`
- emitters: one `roots` literal per campaign generator, `configs/campaigns/*/generate_configs.py`

That absence is the *mechanism* of this defect, not a bystander to it. A generator author had nothing to
copy from and no gate to fail against; the drift survived until a desk proof stumbled on it seven weeks
later. Recommended (separate item, magistrate's call — creating a contract is process-bearing): a short
plan-tree schema section in `docs/contracts/` naming `roots.claim_root_leaf` / `roots.bound_root_leaf` as
the sole canonical pair, plus a repo-wide regression asserting every generator on the **live registry
roster** emits that pair. Not a condition on this merge.

### F3 — The two readers of this binding have **divergent accept surfaces**, and the wider one has no producer. Severity: **should-fix, out of scope for this diff**
`joulewise/arm_readiness.py:8511-8514` accepts the canonical pair *and then lets* `tree["root_namespace"]`
(keys `claim_leaf` / `bound_leaf`) **override** it — including overriding a canonical `roots`.
`joulewise/arm_readiness_evidence_t0.py:1014-1020` has no such fallback. Same frozen-leaf binding, two
different accept surfaces, in a fail-closed evidence gate.

Verified: `grep -rl root_namespace configs/` returns **nothing** — no committed plan tree carries the key,
and the refuter's census found no producer anywhere. So this is a producer-less widening of a fail-closed
binding, reachable only by a hand-written tree, which is precisely the input class the binding exists to
refuse. The practical consequence today is nil (legacy v1–v3 trees carry no `root_namespace`, so both
readers refuse them identically — I confirmed all three trees: legacy `roots`, no `root_namespace`), but a
tree that did carry it would pass the receipt binding and be refused by the T-0 author: a split verdict
between two gates on one fact. Recommend deleting the fallback (or mirroring it), as its own item with its
own refuter. **Not** a fix for this head — it is a live-code change to a different module.

### F4 — The negative fixture is a synthetic two-key tree, not the generated tree with its keys renamed. Severity: **nit**
`tests/test_arm_readiness_evidence_t0.py:930` builds `SimpleNamespace(tree={"roots": roots}, …)` and
`:937-940` feeds it a bare legacy pair. Answering the brief's question 2 directly — **the stub fails
loudly, not silently, under the refactors that matter**:

- `_Context` is `_DerivationContext` (`joulewise/arm_readiness_evidence_t0.py:316-332`), a frozen dataclass
  with twelve fields. A refactor that made `_root_observation` read any of the other eleven
  (`pack_root`, `repository`, `captures`, `clock`, …) hits `AttributeError` on the `SimpleNamespace` — a
  loud error, not a pass.
- A refactor that moved the roots check **out** of `_root_observation` is caught by the negative assertion
  at `:941` (`T0EvidenceAuthoringError not raised`), which is exactly what E6 demonstrated.
- A refactor renaming the `values["arm_context"]` cache key stops the stub from short-circuiting
  `_arm_context`, which then runs against a context lacking `pack_root`/`captures` — again loud.

The one **silent** channel is tree shape: because the negative tree contains only `roots`, a future
`root_namespace` fallback mirroring `arm_readiness.py:8511` would leave both assertions green while
production quietly accepted a legacy tree that carried the namespace. One-line cure, if these files are
touched again: build the negative case from the real tree, `{**tree, "roots": legacy_roots}`, so the
fixture is tree-faithful rather than key-faithful. Optional; F3 is the better place to close that risk.

### F5 — Cross-module fixture reach-in diverges from the repo's own precedent. Severity: **nit**
`tests/test_arm_readiness_evidence_t0.py:909-911` constructs `gamma_fixture.D117ContrastV5PackTests()`
with no `methodName` and calls `setUp()` by hand. The established pattern for exactly this reach-in is
`tests/test_gamma_unit_roster_guard.py:13-16`, which passes `methodName=...`. The bare form works on
Python 3.11+ (and passes here), and `setUp` only loads a generator module so there is no cleanup debt —
but matching the precedent costs one keyword argument and removes a version-sensitive construction.

### F6 — Design answer: **refusing the legacy pair is correct**; do not add tolerance. Severity: **info (design ruling input)**
Four grounds, in descending weight:

1. **It is an evidence/pre-registration fence.** The check binds the basename of a live ARM runs root to a
   leaf frozen in a pre-registered plan tree. D-161's threat-model prune keeps fail-closed behaviour
   precisely for physics, evidence, and pre-registration bindings; this is the third of those.
2. **Tolerance buys zero live capability.** The live registry installs three `_v5` Qwen3 successors; no
   legacy-key pack is on the roster. Historical v1–v3 trees are consumed as **frozen bytes** — digest and
   sidecar authentication — never semantically for their roots (refuter's census, corroborated: the
   readers are the only semantic consumers). The only caller a tolerant reader would ever serve is a
   deliberate re-arm of a retired pack.
3. **The refusal has already proved useful as a signal.** In the 09-13 desk proof it is what correctly
   stopped a retired v1 pack from being armed
   (`docs/process_traces/2026-09-13-activation-24b9d3dd/64-r3-desk-proof-research-opus-report.md:50`).
   Converting that into a pass would have let a retired pack through a T-0 gate.
4. **Tolerance is a one-way ratchet.** Once two spellings are accepted, nothing stops a third, and the
   drift class is invisible by construction — this instance survived undetected until a desk proof.

Stress-tested against the **open** roster question (PACK-ROOT-SUCCESSOR-V5-01, cold gate 65 Q1): if Ed's
roster ruling ever readmits a legacy-key pack, the correct cure is still not a tolerant reader — D-134
and D-139 forbid mutating frozen pack bytes, so the answer is a regenerated successor pack under a new
name, which is the shape the `_v5` line already has. The design answer holds under both branches of the
open ruling.

### F7 — Nothing on `main` is invalidated by the rename. Severity: **info (verified)**
Answering question 3 with executed checks, not inference:

- `ls configs/campaigns | grep -i contrast` → `…_v1`, `…_v2`, `…_v3`, `d117_contrast_v5`. The GAMMA `_v5`
  pack root does not exist (refuter's V6 agrees).
- `ls configs/campaigns/d117_contrast_v5` → `generate_configs.py` plus two D-166 registration JSONs. **It
  is a generator-only directory**: no `plan_tree.json`, no `plan_tree.sha256`, no
  `arm_readiness.freeze.receipts`, no `arm_readiness.sources`, no `identity_pin_projection.receipts`.
  There is no frozen artifact for the rename to contradict.
- The generator's own digest is not pinned: the `main` blob's sha256
  (`ac2c974620cb87ba58e6e74b8abd4202c47061aee539717908816398e5d821b9`) appears **nowhere** in the
  repository. `generator_sha` in the tree is computed at generation time.
- The v1/v2/v3 packs' `plan_tree.json`, `plan_tree.sha256`, receipts, and their **own** generators
  (`…_v1/generate_configs.py:1708`, `…_v2:1708`, `…_v3:1852`, all still legacy) are untouched by this diff.
- Both floor `_v5` generators independently emit the canonical pair
  (`d117_floor_qwen3-1p7b_v5/generate_configs.py:2677,2871`, `d117_floor_qwen3-8b_v5:2677,2871`), so the
  three live-roster successors are now consistent.
- Every other test module that consumes this generator is green: E2, E3, E4 above —
  `test_gamma_unit_roster_guard`, `test_d165_dominance_closeout`, `test_issue_g2a_prefill_prompt_pin`,
  `test_campaign_generator_core`, `test_d117_floor_qwen3_v5_generate`.

### F8 — Nothing overbuilt. Severity: **info**
Answering question 4. The two regressions do not duplicate each other: one pins the **emitter's** output
shape at the generator, the other pins the **reader's** accept/refuse behaviour at the T-0 gate; E5 shows
both fire on the production defect and E6 shows only the second guards the reader. Cost is proportionate
(the pack module runs 58 tests in ~21 s with the new one included). The diff adds no production logic, no
compatibility shim, and no new abstraction — a one-line rename plus its two witnesses is the minimum that
closes the defect. Nothing is missing for merge-ability.

## Scope discipline note

F2 and F3 are real and I recommend they be registered, but neither should be folded into this head: F2
creates a contract (process-bearing, magistrate's decision), F3 edits a different production module
(`arm_readiness.py`) under a fail-closed binding that deserves its own refuter pass. Widening a cure
round to absorb adjacent findings is how fix rounds introduce defects; this one is complete as it stands.

