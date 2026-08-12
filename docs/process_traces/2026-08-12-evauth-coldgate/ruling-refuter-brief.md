## Refuter brief — WO-EVIDENCE-AUTHOR-01, defect B1 second round

**Bottom line up front:** the delta's B1 is a real *contract* defect and a false *security* defect. Its prescribed remedy is executable-refuted as closure and confirmed only as drift-prevention. Meanwhile the same bytes carry a provenance gap that neither lens, nor the fix round, nor the delta found, and that no consumer layer re-catches. Holding the freeze on the DERIVERS round *as framed* is disproportionate; holding it on a ~30-line bench round including the missed finding is proportionate.

---

### 1. B1 reachability through tonight's path — **REFUTED as framed / CONFIRMED as contract defect**

The CLI (`scripts/author_arm_readiness_evidence.py`, 63 lines) takes exactly one operator input, `--pack-root <path>`, and calls `author_arm_readiness_evidence(root)`. No path in that file, or in the module, assigns to `DERIVERS`. The mutation is reachable **only** by an in-process caller that has already imported the module and is executing arbitrary Python — i.e. by someone who has already replaced the program.

Executed distinction (PROBE-1): the CLI is launched with a bare `#!/usr/bin/env python3`, **no `-I`, `-E`, or `-S`**. Ambient `PYTHONPATH` + `sitecustomize.py` executes arbitrary code inside the authoring process before `main()`:

```
PROBE-1 sitecustomize executed inside the CLI process; DERIVERS mutated -> forged
```

So the *only* CLI-reachable route to the DERIVERS mutation is ambient-environment code injection — and that route is not narrowed one bit by privatizing the mapping (the same `sitecustomize` patches `_DERIVERS`, or anything else). The irony is on the record: the child suite interpreter **is** hardened (`-I`, `PYTHONNOUSERSITE`, `PYTHONPATH` pinned, in-child `sys.path[:]` rewrite, `arm_readiness_evidence.py:319-344`); the parent that mints the receipts is not.

### 2. "Private immutable dispatch" as remedy — **REFUTED as adversarial closure, CONFIRMED as drift-prevention**

- PROBE-2: `MappingProxyType` is not immutable in-process. `gc.get_referents(proxy)[0]` returns the live backing dict; one line mutates it. Underscore/name-mangling is not a barrier — `setattr(module, "_DERIVERS", ...)` rebinds.
- PROBE-3: `DERIVERS` is **1 of 53** module-level substitution points of equal or greater power in `arm_readiness_evidence` + `arm_readiness` (`_run_suite`, `_committed_artifact`, `_assemble_receipt`, `readiness.validate_evidence_receipt`, `readiness.sha256_bytes`, `_current_boot_session_id`, …). Closing 1.9% of a surface is not closure.
- PROBE-4 is the decisive one. With **`DERIVERS` completely untouched**, substituting two internal helpers reproduces the delta's exact payload through the real, unmodified deriver:

```
PROBE-4 real deriver, DERIVERS untouched:
  facts: {'desk.three_window_regression.v1': {..., 'three_window_live_ledger_regression_status': 'PASS'}}
  derivation: {'bound_head': '...', 'exact_test_count': 777}
```

The class is structural. Python has no in-process integrity boundary, and the only real boundary — the subprocess/OS one — is already where the suite execution lives.

**What D-134 cl.6 actually demands.** Verbatim: *"every row verdict, applicability, digest, identity pin, and evidence binding is derived; operators supply paths and irreducible attestations, never conclusions."* This governs the **operator input surface**, not Python's object model. An in-process Python caller is not an operator supplying an input — it is an author replacing the program; cl.6 has no more to say about it than about `sed -i` on the module. So cl.6 is satisfied by: the public entry point accepting only a path (already true, and asserted at import, `:1731-1739`), **and the module not advertising a conclusion-supplying seam as public API**. It does advertise one: `DERIVERS` is in `__all__` (`:1743`), as are all twelve `derive_*` functions. *That* is the whole of the genuine defect, and its whole remedy is `__all__` hygiene plus an underscore — no proxy, no mangling, no subprocess re-architecture.

One precision correction against the delta: the sentinel tests use `mock.patch.dict(evidence.DERIVERS, ..., clear=True)` (`test_…author.py:614, 653`) — context-managed and **restored**. The delta's "normalize the surviving injection surface" is right about advertising, wrong if read as leakage.

**Answer to Q1: (a), with the boundary stated as I have stated it** — in-process attribute substitution is outside the threat model because it is outside *any* Python program's threat model, and the honest value of the fix is drift-prevention (accidental mutation, test-normalized seams) and contract hygiene. Not (b): subprocess-boundary authoring buys nothing PROBE-1 does not already defeat, and costs a re-architecture on freeze night.

### 3. What everyone missed on the same bytes

**NEW-FINDING A — the author does not bind its own bytes; and it may come from a different repository than the evidence.** *(This is the finding I would refuse to discharge.)*

No receipt records which authoring code minted it. Grepping every `_committed_artifact` call site (29 of them), the authenticated primary artifacts are `arm_readiness.py`, `identity_pins.py`, `calibration_*.py`, `floor_extraction.py`, `receipt_oracle.py`, the mint scripts and test files — **`joulewise/arm_readiness_evidence.py` and `scripts/author_arm_readiness_evidence.py` appear in none of them.** The one file whose integrity every fact depends on is the one file no fact is bound to.

Worse, PROBE-6: the authoring logic is loaded from `Path(__file__).resolve().parents[1]` (CLI `:11`), while the repository, HEAD, artifacts, and suite execution all come from `readiness._repo_for_pack(pack_root)`. There is **no guard that these are the same tree**:

```
PROBE-6 authoring code loaded from: .../scratchpad/wtEVAUTH
PROBE-6 _repo_for_pack(pack) -> /Users/edr/code/JouleWise
PROBE-6 guard comparing script repo to pack repo present: False
```

That is lens A's B2 (cross-repository execution) surviving one level up: B2 hardened the *child*; the *parent* still authors repo B's receipts with repo A's uncommitted code. Tonight this is not hypothetical — the three files are **untracked in wtEVAUTH right now** (`git status --porcelain`: `?? joulewise/arm_readiness_evidence.py` …). A run from the wrong tree produces twelve perfectly-valid receipts derived by code that exists in no commit, and nothing in the artifact says so.

**NEW-FINDING B — the packet's defense-in-depth premise is false: the author is the sole layer that establishes the truth of the facts.** The packet states "the receipts' consumers re-validate everything … the author is one layer of a defense-in-depth stack, not the sole gate." Executed on the consumer bytes:

- No consumer imports the author at all (`grep -rl author_arm_readiness_evidence joulewise scripts` → only the author and its own CLI). Nothing re-derives, nothing re-runs a suite.
- `generate_freeze_receipt` calls `_discover_evidence(..., pack_sha256=None, head_commit=None, ...)` (`arm_readiness.py:3021-3028`). Freeze **does not check the receipts' pack digest or HEAD at all**.
- `_predicate_passes` (`:2584`) is pure static content matching via `_content_matches` (subset match, `:2571`). The delta's forged `status: "PASS"` fact satisfies it by construction.
- Arm never re-reads the in-pack evidence (`include_pack=False`, `:3626`); it replays the freeze receipt's recorded items via `_freeze_evidence_for_arm`, which calls `_authenticate_generic_evidence_item` with only `expected_boot_session_id` — pack sha and HEAD again `None` (`:2955-2962`).

What the consumers *do* re-catch is real but narrow: byte/sidecar identity, canonical JSON, schema, fact-source digests, boot-session fence, monotonic expiry, duplicate IDs. That is **tamper-after-authoring**, not **falsehood-at-authoring**. The stack is deep on custody and flat on truth. This does not change my verdict on B1 (still unreachable tonight), but it does mean NEW-FINDING A is the load-bearing one: if no layer re-derives, the identity of the deriving code is the only thing a reviewer can ever check.

**NEW-FINDING C — the pack digest in these receipts is unverifiable by construction.** `committed_pack_tree_sha256` hashes every committed pack blob *and refuses on any untracked pack entry* (PROBE-5):

```
PROBE-5a clean pack digest: 6957fe3abfa0d1f3
PROBE-5b after authoring writes evidence: readiness_pack_not_committed | untracked pack directory: b'arm_readiness.evidence'
```

Therefore: the receipts record the pack digest *before* the evidence existed; once the evidence is committed (as it must be — see D), the live digest necessarily differs; so no consumer can ever compare them, which is exactly why freeze passes `pack_sha256=None`. The field is decorative. Related: `_authenticate_existing` takes `context.pack_sha256` from the receipt itself (`:1471-1484`) and re-derives sources against it, so the re-authentication path can never detect a wrong pack digest either. Not exploitable without in-process control; register it, do not hold on it.

**NEW-FINDING D — tonight's operational sequence is mandatory, undocumented in the tool, and has no recovery path.** Because of PROBE-5, `generate_freeze_receipt`'s first act — `pre_freeze_pack_sha = committed_pack_tree_sha256(root)` (`:3014`, comment: *"The pre-freeze pack must be an exact committed tree"*) — hard-refuses `readiness_pack_not_committed` if the authored evidence is sitting untracked. And `reviewed_main` requires `head == local main == origin/main` with a clean `--untracked-files=all` status, or freeze/arm append `readiness_git_tree_dirty` / `readiness_reviewed_main_mismatch` (`:3328-3330, 3681-3686`). The only place this sequence is encoded is the test, at `test_…author.py:829-831`: `git add .` → `commit` → `update-ref origin/main HEAD`. Three problems for 2am:

1. The CLI's PASS output says nothing about it. An operator who runs `freeze` next gets an opaque `readiness_pack_not_committed`.
2. `git add .` is over-broad. Copied to the real repo it sweeps any stray untracked file into the frozen HEAD — including, ironically, leftover `.arm-readiness-evidence-*` staging dirs (`:1663`, created in `root.parent`, i.e. inside `configs/campaigns/`) if a run dies hard.
3. **No re-author path.** Committing the evidence moves HEAD; `_authenticate_existing` then refuses `evidence_author_existing_stale` on `receipt["head_commit"] != head` (`:1437`). A reboot does the same via the boot-session check. So any reboot, any HEAD change, or any need to re-mint requires `git rm -r` of two committed directories and a commit, before re-running. That is fail-closed (good) but undiscoverable under time pressure.

This is all fail-closed, so it is not a soundness hold — it is a runbook hold.

**CONFIRMED sound (attacked, held):** boot-session identity is derived from `sysctl kern.bootsessionuuid` with no env override (`:708-737`) — the arm-time fence cannot be steered by the operator's environment; `grep os.environ joulewise/*.py` finds no production backdoor outside `controller.py`'s unrelated campaign policy. Freshness rides `time.monotonic_ns` + boot session rather than wall clock, so the window's deliberate clock manipulation cannot forge or void validity. The staging/`os.replace`/rollback path and `_reauthenticate_primary_artifacts` are clean. The predicate gate is a genuine backstop against empty-fact receipts on the first-authoring path.

### 4. Proportionality and Q2

**Holding the freeze on the round *as the delta framed it* is not proportionate.** B1's exploit requires in-process code execution; PROBE-4 shows the prescribed remedy does not prevent it; PROBE-1 shows the one CLI-reachable variant is untouched by it. A third delegated round on "private immutable dispatch" would spend the night raising a bar that has no top.

**Waiving the round entirely is also wrong**, because NEW-FINDING A is cheap, real, and precisely the kind of thing that cannot be fixed after the receipts exist.

Q2 — **N1 is separable; N2 is not, but is bench-sized.** N1 (locale/`PYTHONHASHSEED` under `-I`) cannot perturb the authored bytes: the child's payload is fully sorted (`sort_keys`, sorted `sys.modules`, sorted `failed_ids`, deterministic `visit` order), so hash randomization can only surface as a flaky suite, which fails closed. Defer. N2 leaks descendants of JouleWise's own test subprocesses with no process-group supervision (`:337-344`) — the tonight-specific consequence is not evidence integrity but a stray descendant surviving into a quiet-machine measurement period. `start_new_session=True` + `killpg` on both exit and timeout is ~6 lines; take it at the bench rather than delegate it.

---

## Minimum acceptable condition set for tonight

One bounded **bench** round (lead-side, not a delegated cycle), then go. Roughly 40 lines total.

**C1 (blocker, cl.6 — the only part of the delta's B1 I sustain).** Rename `DERIVERS` → `_DERIVERS` (plain dict; **no** `MappingProxyType` — it buys nothing and would misrepresent the guarantee), drop it and the twelve `derive_*` names from `__all__`, leaving the public namespace as the author function, the error class, and the four constants. Repoint the two sentinel tests at `_DERIVERS` (keep `mock.patch.dict`, which restores). Add one regression asserting `__all__` equals the intended set and that `DERIVERS` is absent from it.

**C2 (blocker, NEW-FINDING A).** Self-bind and same-tree guard: (i) add `joulewise/arm_readiness_evidence.py` and `scripts/author_arm_readiness_evidence.py` to the primary artifacts of at least one authored kind — `_committed_artifact` then forces both to be byte-identical to the authoring HEAD, which both pins the deriving code in the receipt and makes authoring from an uncommitted worktree impossible; (ii) refuse at entry unless `readiness._repo_for_pack(root)` resolves equal to the CLI's own `REPO_ROOT`, with a named reason code. Regression for each.

**C3 (blocker, no code — runbook + CLI output, NEW-FINDING D).** The freeze checklist must carry the exact sequence, and the CLI's PASS payload must echo the next step: author → `git add <pack>/arm_readiness.sources <pack>/arm_readiness.evidence` (**explicit paths, never `git add .`**) → commit → push so `origin/main == HEAD` → freeze. Plus the stated recovery fact: a reboot or any HEAD change between author and freeze voids all twelve receipts and requires `git rm -r` of the two committed directories before re-authoring.

**C4 (should-fix, take it because it is 6 lines).** N2: `start_new_session=True` on the suite child and `killpg` the group on both timeout and normal completion.

**Explicitly NOT required tonight, registered instead:** N1 (no effect on authored bytes); the `_authenticate_existing` receipt-sourced pack digest (NEW-FINDING C — unverifiable by construction, and that path is dead once the evidence is committed); the freeze/arm layers' non-checking of evidence pack/HEAD bindings (NEW-FINDING B — structural, compensated by the first-authoring binding, and not fixable on freeze night); any further hardening of in-process attribute substitution (refuted class).

**Verification bar before freeze:** the existing 16 author tests plus the new C1/C2 regressions green, and — since the delta's V-block never ran it — the canonical suite, or an explicit lead-signed waiver naming G2 as accepted residual risk.
