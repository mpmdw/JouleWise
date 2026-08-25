# pack_root identity consult — Opus seat (verbatim)

Seat: Opus (general-purpose agent, first-principles/evidence-doctrine lens,
independent of the Sol seat). Anchor: main f82247ee. Received by the
magistrate 2026-08-25 midday; recorded verbatim below.

---

## Raw findings

### Mechanism, confirmed at f82247ee

- `_pack_identity` (`/Users/edr/code/JouleWise/joulewise/arm_readiness.py:4948`) returns six terms; five are content (`pack_id`, `plan_id`, `window_id`, `plan_path`, `plan_sha256`), one is environment: `"pack_root": str(pack_root.resolve())`.
- `_load_freeze_reference` (`joulewise/arm_readiness.py:6410`) compares the whole dict for equality at **:6448**, raising `readiness_freeze_receipt_mismatch` / *"freeze receipt pack identity differs from committed pack bytes"* (:6449-6452).
- The registry check (`receipt["row_registry"] != registry_reference`, :6444) fires first; everything else in the loader — evidence-digest authentication, the R1 changed-set gate via `validate_r1_evidence_lifecycle` (:4370, `DEPENDENCY_CHANGED_SET` at :4262/:4274/:4336/:4435/:4461), identity-projection binding, row evaluation — is **downstream of :6448**.
- `generate_freeze_receipt`'s idempotent-replay branch calls `_load_freeze_reference` **in full before returning `mutated:false`** (:6805-6813; the in-source comment at :6796-6800 explicitly says it re-checks "`pack_identity` against the committed pack bytes"). The `except` there catches only `EvidenceLifecycleError`, so the :6448 `ArmReadinessError` propagates.

**Empirical confirmation.** I recomputed `_pack_identity` against all nine committed freeze receipts in this checkout:

```
d117_contrast_..._v1/v2/v3   DIFF-KEYS = ['pack_root']
d117_floor_qwen25_1p5b_v2/v3 DIFF-KEYS = ['pack_root']
d117_floor_qwen25_7b_v2/v3   DIFF-KEYS = ['pack_root']
d117_floor_qwen25_1p5b_v1, _7b_v1 → readiness_pack_unreadable (retired R2 spelling, unrelated)
```

`pack_root` is the **sole** differing key in 7/7 resolvable packs. Every committed receipt names `/Users/edr/JouleWise-measurement-20260813` or `-20260818`; **no pack in `/Users/edr/code/JouleWise` can pass this gate**, and none ever could.

### Blast radius in the S-0 runsheet (r4, `docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md`)

`new_case` (:715-729) does `git clone --no-local "$CLONE" "$CASES/<name>"`. §3.6 (:1762-1786) mints `freeze-0004` ×3 **at `$CLONE`** and commits it. Therefore any case forked at `$PROBE_BASE` inherits a receipt pinned to `$CLONE` and refuses at :6448 before reaching its gate:

| Probe | Transcript | Fork | Status |
|---|---|---|---|
| 4(a) ordinary changed path | `101` freeze | `$PROBE_BASE` | **BROKEN** — dies on `grep -F "$CHANGED_CODE"`, message blames the mutation |
| 4(c) plan current + sibling | `104`,`105` freeze | `$PROBE_BASE` | **BROKEN** |
| 4(e) per-class tamper loop | `110-tamper-*` freeze | `$PROBE_BASE` | **BROKEN**, one case per allowlisted path class |
| 4(e.1) C→S subtraction | `123` arm | `$PROBE_BASE` | **BROKEN** |
| 4(f) DEPENDENCY_MANIFEST | `119` freeze | `$PROBE_BASE` | **BROKEN** |
| 4(g) S-6 dual-validator | `121` freeze | `$PROBE_BASE` | **BROKEN** |
| 4(b.2), 4(i) poison | `103`,`140`,`141` freeze | **`$EVIDENCE_COMMIT`** | **OK** — each mints its own freeze at its own path |
| 4(b.1), 4(h) `131` | `102`,`131` | run at `$CLONE` | OK |
| 4(h) `130` histsem | `130` | `$PROBE_BASE` | OK — histsem is location-agnostic by contract |

The two surviving freeze probes survive *only* because they fork pre-freeze. That is the tell: the runsheet already contains the working pattern, and the broken cases can't adopt it — they need §3.7's pinset closure and §3.8's marker, which don't exist at `$EVIDENCE_COMMIT` and can't be replayed per case (§3.8 needs Ed's step-6 confirmation digest).

---

## 1. What the absolute path authenticates

**No byte.** All five other terms are content facts that clone perfectly; `committed_pack_tree_sha256`, `reviewed_main` (clean + HEAD==main==origin/main, `--untracked-files=all`), the sidecar chain and the plan-tree pin cover the bytes. The path adds exactly one proposition: **transaction-locality** — *every phase of one freeze→arm→verify transaction executed against the same working copy.*

**The one attack it blocks (steelmanned):** *mid-transaction checkout substitution.* Freeze in checkout A (the quiet measurement machine: pinned venv, model files, sudoers, no editors, no indexers), then arm/verify in checkout B — a second clean, origin/main-exact clone of the identical commit. Every byte gate passes; the gitignored, execution-relevant state (venv contents, `.git` hooks, resident daemons, a second Python) differs, and that state is structurally invisible to content gates. The `pack_root` term is the only mechanism that fires.

**Why it is nonetheless a weak instrument for that property:**
- It is not the property wanted. The runbook rule is `MEASUREMENT_REPO`; :6448 enforces "*wherever you froze*", not "*the designated checkout*". A wrong first choice is propagated, not caught — precisely the 2026-08-18 event (`docs/run_reports/2026-08-18-t10-session.md:776-790`), where the magistrate's own `freeze-0002` wave was minted at `/private/tmp/.../wtTXN/...`, valid at :6448 forever, and was caught only because an unrelated rehearsal happened to clone.
- It is forgeable at zero cost (`mkdir -p /Users/edr/JouleWise-measurement-20260818`) and breaks under a rename. Cheap to forge, cheap to break by accident — the worst quadrant for an authenticator.
- It authenticates nothing about the machine, the volume, or the environment it is a proxy for.
- **Every other consumer of the same identity already ignores it.** `_authenticate_freeze_predecessor` (:6313-6320) compares `pack_id`/`plan_id`/`plan_sha256` and deliberately skips `pack_root`. `identity_pins._frozen_pack_identity_matches_receipt` (`joulewise/identity_pins.py:1760-1771`) compares `pack_id`/`plan_id`/`window_id` only. `docs/contracts/receipt_histsem_verifier.md:133-139` **rules the question**: *"The verifier is location-agnostic by design. It never compares a freeze receipt's `pack_identity.pack_root` ... this verifier does not add a `pack_root` equality check."* `tests/test_receipt_histsem.py:294` pins that behavior against a real foreign-path receipt. The readiness gate is the outlier, not the standard.

**And the audit value the paper claims comes from recording, not comparing.** `docs/paper/draft-v1.md` A.2 item 3: *"The retained plans record that path inside themselves, so a reader can see which checkout produced a plan."* That claim is satisfied by `_pack_identity` writing the path; it does not depend on :6448 comparing it.

## 2. The detail string

**Yes — a defect, and a load-bearing one.**

It asserts a byte difference. In 7/7 real cases the committed pack bytes are *identical* and the only divergence is an environment path. `readiness_freeze_receipt_mismatch` is a coarse code shared by at least four distinct conditions (:6444 "plan freeze reference is not exact"; :6448 identity; :6791 "existing freeze receipt is not plan-pinned"; :6843 "unreferenced freeze receipt exists") — the **detail string is the operator's only discriminator**, and this one points at the wrong remedy ("your pack is corrupt, re-mint") instead of the right one ("run from the minting checkout"). The runsheet itself now treats detail strings as contract surface: r4 revision note :41 — *"Every R1 probe now also asserts the presence or absence of the detail."* The historical cost is on the record: `ROW-L8` B4 (`docs/process_traces/2026-08-19-prep-sprint/ready-packet/17-ROW-L8-operator-recovery.md:133`) and the T10 revert wave both had to re-derive the true cause from a string that named the wrong one.

## 3. Reader survey — who consumes the recorded absolute path

**`pack_identity.pack_root` (freeze receipt).** Exactly one functional consumer: the equality at `arm_readiness.py:6448`. Everything else reads only the content terms:
- `_validate_pack_identity` :1480-1485 — string non-emptiness, no path semantics.
- `_authenticate_freeze_predecessor` :6313-6320 — content terms only.
- `arm_readiness.py:3617-3622`, `:10522-10541`; `scripts/build_v4_histsem_pinset.py:181-184` — `plan_path`/`plan_sha256`/`plan_id`/`pack_id` only.
- `scripts/verify_receipt_histsem.py` — never touches it (contract §"Archival location rule").
- Tests: `tests/test_receipt_histsem.py:294` **requires** a foreign path to pass; `tests/test_d117_decode_contrast_plan.py:628`, `tests/test_arm_readiness_dry_run.py:125`, `tests/test_arm_readiness_evidence_t0.py:363`, `tests/test_arm_readiness_integration.py:101` all run in-tree (recomputed and recorded paths coincide) and stay green either way.

**`pack.pack_root` (arm/dry-run record, `_pack_record` :4923) — a different field on a different receipt, untouched by any change at :6448.** It is genuinely path-live at four sites: `arm_readiness.py:8567-8578` (resolves the recorded path `strict=True`, compares to `expected_pack_root`, then re-derives `_pack_record` and compares whole-dict at :8587); `:9788` (uses it as the live root for `relative_to` over config paths); `joulewise/bundle.py:127`; `scripts/validate_powermetrics_fiducial.py:739,866`. Also whole-dict `_pack_record` equalities at `:7282` (dry-run staleness) and `:7715` (verify). All of these are self-consistent within one checkout because the arm receipt is minted there.

**Would relativizing the comparison break any reader? No.** I found **no test anywhere that asserts a relocated pack must refuse.** The only artifact that would change meaning is a *docstring*: `tests/test_arm_readiness_lifecycle.py:2265-2270` states GAMMA v1 "refuses all three at freeze-receipt authentication (`readiness_freeze_receipt_mismatch`)" — my diff shows that refusal is caused **solely** by `pack_root`, so the sentence needs re-deriving (at this head GAMMA v1 refuses earlier anyway, at `readiness_row_registry_mismatch`, since the registry installs only `_v4`).

**In-repo precedent for the exact surgical move:** `scripts/reauthor_clean.py:733-741` neutralizes one non-authenticating field before a dict equality, with a one-line reason — *"HEAD is informational; an unrelated movement with the same pack tree is allowed."* Same file also shows the content-addressed alternative to a path: `pack_tree_git_oid` (:281-283). Note the contrast that makes the doctrine clean: `reauthor_clean`'s own `canonical_pack_path` **is** path-bound and correctly so — it is machine-local resumable state, not a committed, published attestation.

## 4. Which semantics serves the paper — and what is promised

**The paper's replay promise routes around this gate entirely.** `docs/paper/draft-v1.md:621` (Step 1) tells a replicator to *"Clone the repository normally"*, and Step 6 — *"verify the receipt chain from version-control objects ... the strongest check available without the evidence archive"* — is `python3 scripts/verify_receipt_histsem.py --repository-root . --require-published`, i.e. the **location-agnostic** verifier. Steps 1-6 are declared runnable "in a checkout holding no measured evidence." Steps 7-11 need the archive and run against bundles, not the readiness gates.

So: **nowhere does the repo promise that `freeze`/`dry-run`/`arm`/`verify` replay from a foreign checkout** — and one contract explicitly promises the opposite for the verifier that *is* published. The only surface that would break under relativization is an unwritten expectation.

But the converse matters more for the paper's posture: with absolute semantics, **the entire readiness gate engine is unexercisable outside two directories on Ed's machine** — including by the development checkout, by CI, by S-0's own falsification battery, and by any future third party who wants to check that a refusal actually refuses. That is a self-inflicted ceiling on falsifiability, in a project whose claim is that refusals are mechanical. Repo-relative comparison serves the paper; absolute serves nothing the paper says.

## 5. Recommendation — code cure

**Recommend the code cure. The probe cure does not avoid estate-8 and costs more soundness.**

*Why not the probe cure.* Three variants, all bad:
1. **Fork affected cases at `$EVIDENCE_COMMIT`** (the 4(i) pattern): impossible — 4(a)/4(e)/4(e.1)/4(f) need §3.7's pinset closure and §3.8's marker, and §3.8 needs Ed's step-6 confirmation digest. Not mechanically replayable per case.
2. **Path-swap (`mv` the case into `$CLONE`'s path per probe):** ~30+ renames of the directory holding the only copy of the un-re-mintable `freeze-0004` receipts (§3.6 note :1792 — "a primary REFUSE is recoverable only by abandoning this clone"). One `die` mid-probe under the runsheet's one-command-per-shell discipline leaves the swap un-restored. It also collapses every transcript's recorded paths into one, degrading the custody record.
3. **Rewrite §4 (30+ cases):** that is an instrument amendment → main → re-ratification → fresh estate anyway, plus a rewritten falsification battery that then needs its own ratification.

Every route spends estate-8. Given that, spend it on the defect rather than on working around it. Note the classification question the magistrate must settle explicitly, because it decides whether estate-7 survives at all: §6 lists *"malformed probe fixture that fails before reaching its intended gate"* under **ordinary defects** (restart the affected case) but *"a step whose environment or dependency precondition is false"* under **instrument failures** (main → re-ratify → §1.1). This is both, and the code cure forces the instrument-failure path regardless.

**Minimal diff (Part 1, mandatory).** At `arm_readiness.py:6448`, following the `reauthor_clean.py:736` pattern:

```python
    current_identity = _pack_identity(pack_root, tree)
    # pack_root records WHICH CHECKOUT minted the receipt; it authenticates no
    # committed byte, and every other reader of this identity already ignores it
    # (:6313 predecessor chain, identity_pins.py:1760, and the histsem verifier's
    # ruled archival-location rule).  It is recorded, never compared.
    if {k: v for k, v in receipt["pack_identity"].items() if k != "pack_root"} != {
        k: v for k, v in current_identity.items() if k != "pack_root"
    }:
        raise ArmReadinessError(
            "readiness_freeze_receipt_mismatch",
            "freeze receipt pack identity differs from committed pack bytes",
        )
```

Recorded bytes, schema, `PACK_IDENTITY_KEYS`, and `_validate_pack_identity` all unchanged — no receipt is re-minted, no reason code is added, no registry entry moves, no paper sentence changes. The detail string becomes true. Regression to land with it (defect-shaped, with mutation-kill evidence per doctrine): copy a frozen fixture pack to a second path in its own repo, assert `_load_freeze_reference` now authenticates, assert a one-byte plan mutation still refuses with the byte string; the mutant that restores the `pack_root` term must turn it red.

I checked `require_pass` as a cheaper discriminator — it is **not** one: dry-run (:7166), arm (:7495) and verify (:7740) all pass `require_pass=False`; only the family-publication marker gate (:10480) passes `True`. And a new mode flag would reintroduce exactly the mode-keyed gate class the 2026-08-18 cold-gate campaign eliminated.

**Part 2, register — do not silently drop the lens.** The property at :6448 caught one real event (T10 F1). Relativizing retires a mechanism, which rule 11 forbids the lieutenant to do alone. Register a row that re-sites it correctly: **check once, at mint, against the intended value** — `generate_freeze_receipt` requires the minting root to lie under an operator-declared measurement checkout (env or CLI, recorded into the receipt), refusing with its own code — instead of checking forever after against itself. That is the version that would have caught the `wtTXN` mint at the moment it happened rather than after three commits and a revert wave. It needs a new reason code and a registry entry, so it must be fenced outside the S-0 window.

**Part 3, one-line doc corrections:** the `tests/test_arm_readiness_lifecycle.py:2265-2270` docstring (re-derive the GAMMA v1 refusal cause), and a cross-reference from the readiness contract to `receipt_histsem_verifier.md:133-139` so the two gates state one doctrine.
