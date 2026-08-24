# S-1 CANDIDATE — INDEPENDENT WRITER≠REVIEWER SEAT VERDICT

**Target:** worktree `/Users/edr/code/JouleWise-wt-s1`, branch `impl/s1-candidate` @ `c1b87f6`
(9 commits over `main@5523003`).
**Seat:** fresh instance, deliberately not the implementing agent. Read-only throughout;
`git status --porcelain` empty and HEAD still `c1b87f6` at close.
**Scope audited:** whole candidate (`git diff main...HEAD`), with emphasis on the two rounds no
reviewer had seen — the finish round `23e185d..9ed6025` and the G-11 round `c1b87f6`.
**Governing authorities:** kernel row `S1-CANDIDATE-01` (TASK_QUEUE.md A81); D-151 conditions
1/2/6/8 (`docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md`); the marker
ruling and its six splits (`docs/process_traces/2026-08-22-t20/marker-codesign/MAGISTRATE-RULING-MARKER.md`);
and `docs/process_traces/2026-08-22-t20/s1-candidate/MANIFEST.md`, every § claim of which was
treated as an assertion to verify rather than a fact.

---

# VERDICT: REFUTED

Three blockers. The candidate is not gauntlet-ready; two of the three are cheap to fix, but one
of them would have propagated a false conclusion into the ruling the candidate implements.

**Counts: 3 blockers, 12 should-fix, 4 nits**, plus two recorded observations and one
honest-counts note.

---

## Blockers

### B-1. The §9.3.6 open finding is a misdiagnosis, and its proposed resolution would have voided D-151's own basis.

`MANIFEST.md:794-856` escalates a dilemma — is the reviewed-HEAD gate over-broad, or does it
legitimately subsume re-derivation? — to this seat. Neither. It is a fixture defect, proven by
execution.

The 112-entry allowlist is **pack-name-exact** to the three `_v4` packs (no globs, deliberately:
`docs/contracts/receipt_histsem_verifier.md:145-146`). Three of the four staged tests build a pack
named `d117_floor_qwen25_1p5b_v1` — the default at
`tests/test_arm_readiness_evidence_author.py:103`. Those 33 paths are absent from the allowlist the
candidate itself authored, so gate 4 (`joulewise/arm_readiness.py:4308-4314`) fires. Rename the
fixture pack to an allowlisted `_v4` one and run the *identical* variant-4 coherent rewrite: gate 4
does not fire, control reaches `_r1_rederive_at_arm`, and it refuses with
`DOCTRINE_PIN ARM re-derivation differs from authored semantics`
(`joulewise/arm_readiness_evidence.py:1852`). The candidate's own fourth test already uses `_v4` and
lands exactly on the re-derivation raise at `arm_readiness.py:5470`; `MANIFEST.md:849-856` records
that and does not draw the inference.

An alternative hypothesis — that the fixture merely failed to repoint the receipt's own
`derivation_commit` — was tested and **refuted**: the construction is circular, since rewriting the
receipts is itself a change to those same paths, so `git diff N..N+1` returns the same 33 paths and
gate 4 fires again.

Why this is a blocker and not a should-fix: per the S-0 runsheet's mechanism proof
(`s0-runsheet-r1.md:704-706,725`), the listed authenticator for the 99 allowlisted
source/evidence/sidecar paths is `readiness_evidence_digest_mismatch` — a digest check, which a
coherent rewrite defeats by construction. Semantic replay is the *only* remaining authenticator for
those paths. Adopting the "legitimately subsumed" horn would have removed the independent
authentication that makes the 112-path allowlist lawful under V-1(iii) — the exact ground on which
D-151 refuted Option 1.

**Fix:** retarget the fixtures to an allowlisted pack; delete the §9.3.6 finding; the four tests then
become ordinary green (after B-2 below).

### B-2. The 21 S0-BLOCKED markings are vacuous, misattributed, carry no machine-readable reason at all, and one can never flip green — yet `MANIFEST.md:741-745` promotes all 21 into S-0 acceptance.

Five distinct defects:

- **`@unittest.expectedFailure` passes on *any* exception.** These 21 cover the end-to-end
  ALPHA/BETA/GAMMA arm path, boot-session voiding, dry-run staleness, symlink escape, atomic
  launch-capability races and the ACID T-0 suite. They now assert nothing; an import error or a
  security-relevant refusal ceasing to fire both read as "expected."

- **There is no reason string at all.** `MANIFEST.md:743-744` states that every entry is "marked
  `@unittest.expectedFailure` with the reason string `S0-BLOCKED: requires minted _v4 packs`." That
  is false as a matter of Python: verified by probe, `unittest.expectedFailure` has signature
  `(test_item)` and sets exactly one attribute, `__unittest_expecting_failure__`. The text is a
  trailing **source comment** on the decorator line, attached to nothing, absent from every pytest
  and unittest report, and invisible to any tooling that inspects markers. Combined with the
  docstring gap below, the S0-BLOCKED set **cannot be mechanically enumerated at all** — yet
  `MANIFEST.md:744-745` makes flipping precisely those 21 an S-0 acceptance criterion. S-0 has no way
  to know which tests it is being graded on.

- **The reason is measured-wrong for the dominant cause.** The observed refusal is
  `legacy generic freeze evidence may not enter the R1 lifecycle`
  (`joulewise/arm_readiness.py:5317-5325`), whose two conjuncts are properties of this branch's own
  registry repoint plus `make_go_fixture` authoring legacy-schema evidence. Minting `_v4` pack bytes
  changes neither — and `MANIFEST.md:747-752` concedes exactly this, contradicting the comment
  attached to all 21.

- **`tests/test_arm_readiness_lifecycle.py:2033` can never flip green.** It asserts
  `predecessor.name in readiness._PROFILE_BY_PACK` (`:2051`); `PACK_NAME` is
  `d117_floor_qwen25_1p5b_v4` (`:54`), so the predecessor is `_v3`; and `_PROFILE_BY_PACK`
  (`joulewise/arm_readiness.py:287-291`) is a static code dict holding only the three `_v1` ids. S-0
  mints bytes, not source-map entries. Two docstrings additionally claim S-0 mints the `_v3`
  predecessor bytes — but `configs/campaigns/` already contains all three `_v3` packs
  (`d117_floor_qwen25_1p5b_v3`, `d117_floor_qwen25_7b_v3`, `d117_contrast_qwen25_1p5b_vs_7b_v3`).

- **`MANIFEST.md:744-745`'s "a docstring stating what unblocks it" is false: 3 of 21 have one.**
  Verified by AST parse across the five files: 21 `expectedFailure` decorators, 3 with an
  S0-BLOCKED docstring. (Test #21,
  `tests/test_arm_readiness_evidence_t0.py::test_acid_real_boot_session_then_real_arm_generator_reaches_go`,
  has no docstring at all — its body opens with `try:`.)

Two further confirmations: all 21 markers were applied to **pre-existing, previously-live tests**
(the branch added zero new tests to those five files, bar one unrelated addition), and there were
**zero xpassed**, so the marked tests do genuinely fail — the defect is the misattributed cause and
the vacuity, not a mislisted passing entry.

The manifest applies the correct standard at `:852-855` ("a wrongly listed entry would corrupt the
S-0 acceptance gate") to justify *not* marking the four §9.3.6 tests, then violates it in the 21.

**Fix:** `@unittest.skip("<measured cause>")` — which takes a real, reportable argument and does not
swallow arbitrary exceptions — and retire or reconstruct the historical-pairing test on ruled grounds.

### B-3. The variant-4 in-test comments assert as fact the claim B-1 refutes.

`tests/test_arm_readiness_evidence_author.py:569-578` and `:627-633` state that the added commit +
`update-ref` lines put the fixture in the world where "every integrity gate passes and only
re-derivation is left." Measured, the commit is what *creates* the `DEPENDENCY_CHANGED_SET` refusal.
Future readers will trust the comment.

---

## Should-fix

**4. Ungoverned exception escape at the library boundary** — `joulewise/arm_readiness.py:9991`.
`validate_step6_confirmation_table` calls `_require_string`, which raises `ArmReadinessError`
(`:1305`), *not* `FamilyPublicationError`. Probed and confirmed: a table with a non-string or empty
`transaction_id` raises `ArmReadinessError` (`FamilyPublicationError` MRO is
`FamilyPublicationError → ValueError`, so it is not a parent-class catch).
`_require_confirmed_conditional_path:4232` and `_gate_family_publication:10744` both catch only
`FamilyPublicationError`, and `generate_arm_receipt` (7273-7506) has no `ArmReadinessError`
catch-all — so it propagates ungoverned. This falsifies the docstring at `:4203-4207` ("Every other
outcome... raises `DEPENDENCY_CHANGED_SET`") and is the ungoverned-explosion class marker-ruling ¶4
was written to cure. The scheduler is defended by a catch-all at `joulewise/scheduler_gates.py:936`;
the library boundary — split S-3's entire point — is strictly weaker than the layer it is supposed to
backstop.

**5. Wrong-expectation** — `tests/test_arm_readiness_evidence_author.py:645`. Expects
`"differs from freshly derived bytes"`, the **legacy v1-path** message
(`joulewise/arm_readiness_evidence.py:2194`). The R1 path emits
`"ARM re-derivation differs from authored semantics"`. Wrong even after B-1's fix.

**6. Confirmation-table defaulting asymmetry.** `generate_arm_receipt:7301-7305`,
`_derive_arm_semantics_for_verification:7533-7534` and
`joulewise/scheduler_gates.py::evaluate_scheduler_gates:1030-1032` all default to campaign custody;
`generate_freeze_receipt:6521` threads a bare `None` with no default; and `_authenticate_existing_r1`
(`joulewise/arm_readiness_evidence.py:2308`) is not threaded at all. All fail closed, so no bypass —
but `MANIFEST.md:530`'s "threaded from the arm, freeze, verification, and marker-replay entry points"
is materially misleading. Freeze is harmless in the intended order (the pinset does not exist at
freeze time); the authoring path is an ordering fragility.

**7. No runtime closure check binds `R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS`
(`joulewise/arm_readiness.py:2864`) to the registry allowlist.** A spelling drift on either side
makes the intersection empty and the path is then subtracted **unconditionally** — it fails *open*.
Currently caught only by a hardcoded literal at `tests/test_arm_readiness_schemas.py:377-378`.
Contrast the reason-code vocabulary, which got a real registry-load closure check per marker-ruling ¶4.

**8. `tests/test_scheduler_gates.py:368` tautological; `:161` vacuous.** Verified by probe:
`_g7_scheduler_code("banana")` returns `scheduler_family_marker_invalid`, which is in
`G7_REASON_CODES` — the function (`joulewise/scheduler_gates.py:836-847`) is *total* into that set
via its catch-all, so the loop's input is irrelevant. `:161` is the same generic shape that the
sibling test at `:346` exists to cure.

**9. `tests/test_family_marker.py:432`** — the predecessor-refusal half of its docstring never runs;
the stub's `raise` at `:448-450` is dead code. This is MANIFEST's claimed G-8 item-1 cure.

**10. G7's PASS path has never been exercised against a real marker** —
`verify_family_publication_marker` is mocked at `tests/test_scheduler_gates.py:220,318` with the
on-disk marker being `b"marker"`.

**11. `getsource` source greps went 9 → 13 across `tests/` versus merge-base**, against
`MANIFEST.md:885-887`'s "four... rewritten as behavioural tests."
`tests/test_family_marker.py:650` is fully redundant with the behavioural test at `:826`.

**12. `test_every_check_id_has_a_raise_site` (`tests/test_family_marker.py:339`)** is satisfied by
commented-out or docstring text, proves presence not reachability, and its generic clause can launder
`worktree_dirty`/`head_mismatch`.

**13. `tests/test_arm_readiness_evidence_author.py:494`** — the `assertNotIn` arm is implied by
`_require_exact_keys` on the line above; and no test anywhere pins `R1_EVIDENCE_FRESHNESS_CLASSES`, so
a kind silently reclassified to `RE_DERIVABLE` would lose its boot binding undetected.

**14. The dual-coordinate archival half (`tests/test_arm_readiness_registry.py:177-183`) is a
static-bytes pin.** Probed: the frozen `_v1..._v3` packs do **not** resolve under the live code
(`successor ID 'd117_floor_qwen25_1p5b_v3' is not installed by the R1 registry`), so the comment's "a
frozen recorded reference must keep resolving" is not true of anything runtime.

**15. The suite cannot be run to completion under pytest.** It hard-crashes with `SIGABRT` (exit 134)
at ~9%, in `joulewise/adapters/mlx_runtime.py:1159` reached via the ACID tests in
`tests/test_arm_readiness_evidence_t0.py`. This reproduces at merge-base `5523003` (verified by
extracting the base tree with `git archive`), so it is **not a branch regression**. But the aborting
tests are **inside** the S0-BLOCKED 21 (#18-#21), and `expectedFailure` cannot contain a process-level
abort — an xfail marker on a test that kills the interpreter does not make the suite green, it makes
it uncollectable. With those four deselected the run completes:
`6 failed, 3763 passed, 95 skipped, 4 deselected, 17 xfailed, 19674 subtests passed in 2904.34s`.

---

## Nits

**16. `MANIFEST.md:26` calls `b1c6bee` "the last COMMIT BEARING CODE"** — false; `c1b87f6` changes
`joulewise/arm_readiness.py` and `joulewise/arm_readiness_evidence.py`. Consequently §9.4's
frozen-surface re-verification was never run at the actual head. Re-run independently at `c1b87f6`:
all five still identical by blob OID.

**17. The `dynamic` set (`joulewise/arm_readiness_evidence.py:1434-1450`) and `dynamic_or_defensive`
(`tests/test_arm_readiness_integration.py:566-584`) are hand-mirrored** with no mechanical link,
despite the comment requiring they stay in step.

**18. `generate_freeze_receipt:6564-6570` moves the predecessor `resolve(strict=True)` out of the
guarded condition**, so it now runs in registry configurations where it previously never ran.
Fail-closed and an improvement, but a scope expansion the comment does not name.

**19. Minor test nits:** `tests/test_scheduler_gates.py:338` accepts swapped diagnostics;
`tests/test_arm_readiness_schemas.py:400` writes a subset check as `S == RRC & S`;
`tests/test_receipt_histsem.py:127-135` forbidden-substring greps fire on comments.

---

## Recorded observations (not findings against the candidate)

**O-1. `tests/test_calibration_exits.py` flake.** Two of the six failures in the completing run are a
pre-existing non-deterministic flake in that file — unmodified on this branch, and it fails at base
`5523003` with a *different* byte diff each run (it captures an ambient process command line). Not a
branch defect. But it does mean `MANIFEST.md:617-620`'s `failures=2, errors=2, expected failures=21`
is a `unittest` run over a narrower radius (1,368 tests, 13 min) and does not characterise the
repository (~3,880 tests + 19,674 subtests, 48 min).

**O-2. Honest-counts note.** §2.5's twenty, §9.5's "+12 test methods", and §9.3's one lifecycle
addition sum to the measured net +33 (34 added, 1 renamed away). **No discrepancy** — this manifest
count is accurate.

---

## What was verified as TRUE (against active attempts to break it)

The **G-2 cure survives adversarial attack**, and this is the strongest part of the candidate. The
subtraction at `joulewise/arm_readiness.py:4294-4307` is correctly ordered — only
`allowlist - conditional` is subtracted unconditionally, and a conditional path is discarded only
*after* the check returns. Six constructed bypasses all failed:

1. absent table → `confirmation_path is None` → refuse;
2. malformed / noncanonical / sidecar-inconsistent table → `FamilyPublicationError` → refuse;
3. subtraction-before-check → not reachable; the loop discards only on a clean return;
4. "digest of the WRONG bytes" → the authenticator reads `git show <head>:<path>`, and the *gating*
   reader `_gate_receipt_histsem:3650-3664` also reads committed bytes, so they agree (the disk-reading
   `_load_histsem_pinset:3174` is the standalone-CLI path, not the gate);
5. a table naming a different path → `section["path"] != relative_path` → refuse;
6. conditional path present in the code set but absent from the registry allowlist → stays in
   `outstanding` → refuses as relevant.

`authority == "ED"` and `decision == "YES"` are enforced (`:10062-10066`).
`tests/test_receipt_histsem.py:598-657` is the strongest new test on the branch — it proves the
condition is on bytes-at-HEAD rather than path membership by re-mutating the same path against the
same table.

Also verified true:

- **Both fences hold.** No authenticator path in the 112-entry allowlist, asserted mechanically at
  `tests/test_arm_readiness_schemas.py:379-380` (zero paths matching `d117_step6_confirmation` or
  `family_publication`); allowlist is 112, sorted, unique.
- **All four r6-pinned estimator sources and the v1 registry are byte-identical to merge-base by blob
  OID**, re-verified independently at `c1b87f6` (not at `b1c6bee` as the manifest did).
- **All four tool sidecars match** in uniform GNU form.
- **The `verify_receipt_histsem.py` docstring edit invalidates no recorded pin.**
- **Both lease-extension cures are correct and minimal:** `joulewise/arm_readiness.py:6559-6584`
  (predecessor resolved once, governed `_successor_chain_refusal` instead of a bare `FileNotFoundError`)
  and `joulewise/arm_readiness_evidence.py:1433-1450` (seven `readiness_r1_*` codes added to the
  `dynamic` census set; the census asserts exact set equality, and the mirrored set in
  `tests/test_arm_readiness_integration.py:566-584` matches with per-code justifications).

---

## Meta-observation for the lead

Both blockers share a signature: the implementer reasoned carefully to a conclusion and never tested
the cheapest falsifier. §9.3.6 walked four gates without checking whether the fixture's pack was in
the allowlist it had itself authored; the 21 markings were written without running one of them to see
what actually raised. That is a two-round same-signature pattern, and it argues the next pass should
be measurement-first rather than another reasoning round.

---

## Headline

S-1 candidate REFUTED at `c1b87f6` — 3 blockers (§9.3.6's "unreachable re-derivation" is a fixture
defect disproven by execution and its proposed resolution would have voided D-151's V-1(iii) basis;
the 21 S0-BLOCKED markings are vacuous, misattributed, carry no machine-readable reason at all yet
gate S-0 acceptance, and one can never flip green; variant-4 in-test comments assert the refuted claim
as fact), 12 should-fix, 4 nits — while the G-2 digest-conditional cure survived six bypass attempts
and all frozen surfaces re-verified clean.
