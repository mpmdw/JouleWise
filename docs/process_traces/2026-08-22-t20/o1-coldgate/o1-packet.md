# O-1 COLD-GATE PACKET — RH pinset rows vs the no-update byte pin (mechanically assembled 2026-08-22)

Ruling sought: how S-0/S-1 append the mandatory post-freeze _v4 pinset rows while the ruled 112-path changed-set contract and the normative pinset byte-pin test both bind. Marker context: Ed ruled V6 option (a) custody-external (contract stays 112; no marker paths engage).

## A. The runsheet's O-1 statement (s0-runsheet.md §7, verbatim)
### O-1 — NEEDS_RULING: RH pinset rows versus the no-update byte pin

Question: how can S-0 append the mandatory post-freeze `_v4` pinset rows while retaining both the exact 112 post-derivation changed set and the normative literal SHA assertion over the entire pinset?

Facts: RH-8 requires the three rows after freeze x3 and adds only the pinset path (111 -> 112). HISTSEM-CONTRACT requires the literal pinset SHA in `tests/test_receipt_histsem.py:30-31,53-60` with no update/reseal lane. The final pinset bytes cannot be known at evidence derivation because freeze receipts include newly minted, code-derived content. Updating the test after derivation creates path 113; leaving it unchanged fails the mandated byte-pin test.

Options considered:

1. Amend the ruled contract to 113 and authorize the exact test path plus a one-time reviewed literal update.
2. Rule a different stable authentication construction whose already-pinned bytes can authenticate append-only `_v4` rows without changing the test path; this requires a reviewed code delta before S-0.
3. Waive the `_v4` rows or the byte pin. Not recommended: each contradicts a binding RH obligation.

Recommendation: option 2 if a stable authenticated-root design already exists and can be reviewed before candidate derivation; otherwise the narrow, explicit 113-path amendment in option 1. Blocked work: §3.7 commit onward, final contract, histsem present, arm/verify, and acceptance closure. All earlier assembly remains executable.

### O-2 — Ed’s V6 marker ruling
## B. rh-ruling.md item 8 (verbatim)
8. SCHEDULING CONSTRAINT (binding on the `_v4` transaction): this
   verifier LANDS BEFORE the `_v4` re-freeze; the `_v4` pinset row
   mints AFTER freeze-0004 ×3 AND BEFORE Ed's exact-byte step-6
   (the r4-3 step reference — the ambiguous "S5" label is retired) —
   retrofitting reproduces C1's shape (an expected value nobody
   supplied). COLD-PASS AMENDMENT TO r5 V-1 (ruled by that pass):
   the allowlist value goes 111 → 112, adding the pinset's exact
   path (pack-and-ordinal-exact per V-1(v); `_v5` gets its own entry,
   never a glob) — without it, the post-mint pinset commit trips the
   whole-repo changed-set gate and refuses every subsequent `_v4`
   arm. S-0's clone proof extends to exercise the histsem gates and
   the pinset (present → arms cross; absent → the pinset-absent
   refusal; the 112-entry candidate contract still fails on
   missing/extra/unused).

## C. The byte-pin test at HEAD 1ba04a8 (tests/test_receipt_histsem.py:25-80, verbatim)
    verify_receipt_histsem_pack,
)


ROOT = Path(__file__).resolve().parents[1]
PINSET = ROOT / "configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json"
PINSET_SHA256 = "d81515505d677c2ca045238e721c87eae8f38439a89a5377e58fa9064eaf2f21"
REPRESENTATIVE_PACK = ROOT / "configs/campaigns/d117_floor_qwen25_1p5b_v3"


def git(repository: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args),
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )


def write_pinset(path: Path, mutate: callable) -> Path:
    value = json.loads(PINSET.read_bytes())
    row = next(item for item in value["packs"] if item["pack_id"] == REPRESENTATIVE_PACK.name)
    mutate(row)
    path.write_bytes(render_json(value))
    return path


class ReceiptHistoricalSemanticsTests(unittest.TestCase):
    def test_pinset_is_byte_pinned_and_has_no_update_lane(self) -> None:
        self.assertEqual(hashlib.sha256(PINSET.read_bytes()).hexdigest(), PINSET_SHA256)
        script = (ROOT / "scripts/verify_receipt_histsem.py").read_text(encoding="utf-8")
        self.assertNotIn("--update", script)
        value = json.loads(PINSET.read_bytes())
        self.assertEqual(len(value["packs"]), 9)
        self.assertEqual(sum(row["receipt_count"] for row in value["packs"]), 99)

    def test_verifier_cli_refusal_is_canonical_and_exit_two(self) -> None:
        completed = subprocess.run(
            (
                "python3",
                "scripts/verify_receipt_histsem.py",
                "--repository-root",
                ".",
                "--pinset",
                "/definitely/absent/receipt-histsem-pinset.json",
            ),
            cwd=ROOT,
            check=False,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "REFUSE")
        self.assertEqual(payload["reason_codes"], ["histsem_pinset_absent"])
        self.assertEqual(completed.stdout, render_json(payload))

## D. HISTSEM-CONTRACT sections (docs/contracts/receipt_histsem_verifier.md, verbatim)

## Governed identity and activation

The governed pinset is
`configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json`. A pack is a
legacy histsem pack exactly when its immutable repository identity — the pair
`(pack_id, pack_path)` — is a member of the committed pinset. Receipt counts,
receipt filenames, evidence-ID prefixes, and other scanned pack contents do
not decide whether the gate engages. Consequently, adding, removing, or
renaming an unreferenced receipt cannot disengage verification for a governed
pack.

The in-library gate runs before custody output in both entry points:

- `generate_arm_receipt` verifies the governed pack being armed.
- `generate_freeze_receipt` verifies the governed predecessor when operating
  in predecessor mode.

The pinset carries each pack's explicit historical and current digests,
historical commit, post-authoring delta, freeze binding, plan bindings, and
complete legacy-receipt inventory. Its bytes are SHA-256-pinned by
`tests/test_receipt_histsem.py`. There is no update, regenerate, repair, or
auto-reseal lane; a new governed value requires an explicit versioned change.

Eligibility is based only on a successful `git ls-tree HEAD -- <pinset>` presence check followed by a `git show HEAD:<pinset>` read: after canonical validation, membership of `(pack_id, pack_path)` engages the gate and a membership miss returns normally. An unambiguous result that the pinset path does not exist in `HEAD` also returns to ordinary readiness; it is an absence-of-governance answer, not a `histsem_pinset_absent` refusal. In that state the library must not inspect receipt schemas, names, counts, or inventories. Any other failure to obtain the HEAD pinset refuses, and an invalid HEAD pinset refuses. The HEAD read prevents worktree pinset deletion or mutation from disengaging a pack whose HEAD row exists, and the gate verifies against those same HEAD-anchored rows. Committed pinset mutation or deletion is owned by the byte-pin and changed-set CI controls. Residual: absent a HEAD pinset, the library cannot distinguish a synthetic/pre-governance repository from a history whose pinset was removed.


## Coordinates and checks

The verifier has two coordinates, and they are not interchangeable.

| Coordinate | Governed checks |
|---|---|
| `HISTORICAL` (`head_commit`) | Pure-Git `ls-tree` plus `cat-file blob` recomputation under the existing `PACK_DIGEST_DOMAIN` framing; K5 comparison with `historical_pack_sha256`; receipt `head_commit`/`pack_sha256`; the pre-authoring invariant; ancestry to `HEAD`, with the lane-specific `origin/main` rule below. |
| `HEAD` | K12 comparison of the committed current pack tree with `current_pack_sha256`; receipt-to-sidecar-to-freeze-to-plan binding; mandatory `facts[].source_sha256` binding; exact pinned receipt inventory; predecessor binding. |

K7 compares `head_commit` to `HEAD`: there must be zero deletions, additions
must be confined to the four custody directories encoded in the library, and
modifications must be drawn only from the closed freeze-retarget set encoded
there. K5 and K12 are the load-bearing historical and current byte checks. K7
is layered delta-shape hardening and the bootstrap check used when a new
pinset row is minted; it is not the sole byte-integrity check.

The differential self-test over every governed pack mechanically requires
`historical_pack_tree_sha256(..., "HEAD")` to equal
`committed_pack_tree_sha256(...)`. This pins the framing without relying on a
prose reimplementation.


## `_v4` transaction sequencing

This verifier and its refusal vocabulary land before the `_v4` re-freeze.
After all three `freeze-0004` artifacts exist, and before Ed's exact-byte step
6, the `_v4` pinset rows are minted and checked against the transaction's
confirmation table. The pinset path is the pack-and-ordinal-exact 112th entry
in the whole-repository changed-set allowlist. Retrofitting the rows after the
transaction would recreate the missing-expected-value defect; a later family
gets its own exact entry, never a glob.


## Truth boundary

This is DETECTABILITY, not integrity — the verifier does not stop a
history-rewriting in-process actor (that residual is a REGISTERED LIMITATION
under D-139 A1, which is why it is recorded rather than a gap); it raises
forgery cost from a 6-file commit to a history rewrite that breaks merge-base
ancestry against `origin/main` and contradicts the hand-published S5 digest
table. The paper must state this detectability boundary in those words and
must not claim that the mechanism establishes integrity against that actor.


## E. r5 V-1 allowlist provisions (rulings-r5-consolidation.md:78-107, verbatim)
V-1 (allowlist, refuter #1/#2/#3/#4 + cold conditions): the ruled
value is THE LITERAL 111-PATH LIST, generated and carried in the
transaction custody (generator: a script enumerating, per `_v4`
root: arm_readiness.sources/<slug>.json for the eleven slugs [NO
sidecar]; arm_readiness.evidence/evidence-<slug>.json AND
.json.sha256; arm_readiness.freeze.receipts/freeze-0004.json AND
.json.sha256; plan_tree.json; plan_tree.sha256). Recorded
provisions: (i) U11-BEFORE-DERIVATION IS A PRECONDITION OF THE VALUE
(the projection writes projection-0001.json/.sha256 +
producer_contract.json + a plan_tree re-render — 119 paths if
mis-ordered); (ii) the applicability census mechanically reads the
hardcoded issued-acceptance set (arm_readiness.py:4143-4150) — a
`_v4` acceptance growth makes it 12 slugs/120 paths; (iii) the
double-crossover is recorded (Opus conceded to the derived manifest;
Sol conceded back to the static list CONDITIONAL on independent
authentication of all allowed bytes); (iv) Sol's proviso is PARTLY
FALSE as R1 binding — freeze-0004.json, its sidecar,
plan_tree.sha256, and the plan-tree freeze slot have NO R1
manifest binding; the LOAD-BEARING check for those four is the
ARM-time semantic replay gate (readiness_dependency_refused,
arm_readiness.py:5344-5348, backed by :5185-5190/:5233-5241/
:4211-4215) — recorded as such; (v) allowlist entries are
PACK-AND-ORDINAL-EXACT (freeze-0004 literal, no generalization to
`_v5`); (vi) S-0 executes a PER-CLASS TAMPER PROBE over every
allowlisted path class, proving refusal through
manifest/authentication/replay for each; any class with no
authenticator moves to digest-conditional subtraction, and any probe
failure REOPENS the mechanism question to the derived manifest (the
tripwire); (vii) the derived, digest-authenticated manifest is
recorded as the standing dissent/alternative.
