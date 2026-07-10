# Spec: DOC-009 status-authority reconciliation + REPRO-001 environment lock & external re-reduction

Status: ADJUDICATED 2026-07-09 (C-028) — rulings in `ADJUDICATION.md` in this directory AMEND this spec wherever they conflict with its body text

Queue rows: 0r (DOC-009, P4, TOP-5/REV-8) and 0u (REPRO-001, P2, NEG-9; extends P2-027 row 11c).
Sources: `docs/reviews/2026-07-09-c027-whole-project-review.md` §7 rows TOP-5/REV-8/NEG-9;
`docs/reviews/c027/lens-topdocs.md` finding 5; `lens-reverse.md` finding 8;
`lens-negspace.md` finding 9; D-023 (`docs/decision_log.md:1130`).

---

## Part A — DOC-009: status-authority reconciliation

Problem: D-023 makes the phase exit-checklist evidence matrices the SOLE
per-item status authority, but three matrix rows contradict shipped
evidence and the queue's completed rows. Every fix below is an in-place
status-cell update in the checklist's existing convention — status cell
becomes `complete (DATE; evidence summary)` — plus, where the surrounding
text is prose rather than a matrix row, a dated append-only addendum
line. No history rewriting; the old wording stays visible in git.

### DOC9-1: Phase 3 KV-size helper row (`docs/phase_3/phase_3_exit_checklist.md:10`)

Current: `| 3.0.0 kv-size helper | required | pending | ... |`
Shipped: PR #2 (merge `b9f93d6`, branch `stream/kv-size-helper`), queue
completed row `TASK_QUEUE.md:161` dated 2026-07-07.

Change the Status cell to:

```
complete (2026-07-09 reconciliation; shipped 2026-07-07 via PR #2 — module + CLI verb, anchors verified against both mirrored models; reconciled per DOC-009/TOP-5 after the row was left stale at queue close)
```

Queue cross-reference fix: append to the KV-SIZE completed row's evidence
cell (`TASK_QUEUE.md:161`): `; matrix row: phase_3_exit_checklist.md §3.0.0`.

### DOC9-2: Phase 4 related-work row (`docs/phase_4/phase_4_exit_checklist.md:17`)

Current: `| 4.6 related-work draft | required (ungated; may close early) | pending | ... |`
Shipped: commit `c31ffac` "P3-001: background/related-work draft (Stage 4.6)",
queue completed row `TASK_QUEUE.md:166` dated 2026-07-06; artifact
`docs/phase_4/related_work_draft.md` (11 sources, independently verified
citations).

Change the Status cell to:

```
complete (2026-07-09 reconciliation; drafted 2026-07-06 via c31ffac — docs/phase_4/related_work_draft.md, 11 sources, citations independently verified; reconciled per DOC-009/REV-8)
```

Note: "complete" here means the *draft* stage 4.6 exit criterion is met;
the row's Required Evidence text is unchanged.

Queue cross-reference fix: append to the P3-001 completed row's evidence
cell (`TASK_QUEUE.md:166`): `; matrix row: phase_4_exit_checklist.md §4.6`.

### DOC9-3: Phase 1 Mac rows (`docs/phase_1/phase_1_exit_checklist.md:253` and `:315`)

Contradiction: line ~255 says Mac support is "partially checked on the
current Apple Silicon controller" while line ~315 records the binding
verdict "supported, end to end (2026-07-06)" (Slice 2I flagship, 3
strict-valid real energy bundles, run report
`2026-07-06-slice-2i-first-real-energy.md`). The later verdict is
correct; the earlier prose is a stale snapshot.

Fix (prose section, so append-only addendum rather than cell edit):
immediately under the `Status: partially checked ...` bullet at ~:253,
append one indented dated line:

```
  - ADDENDUM (2026-07-09, DOC-009 reconciliation): superseded — the
    binding verdict below (this file, "Current verdict" section) is
    **supported, end to end (2026-07-06)** per the Slice 2I flagship
    (3 strict-valid real energy bundles). This earlier "partially
    checked" line reflects the pre-2I snapshot and is retained for
    history only.
```

No change to the ~:315 verdict block (it is the correct authority).

### DOC9-4: standing reconciliation rule (stop the drift)

DECISION: the rule lives in `TASK_QUEUE.md`, as a new numbered item in
the existing "## Intake Rule For New Tasks" section (renumber-free:
append as item 10), because queue closure is the act that drifted —
putting the rule anywhere else re-creates the split-authority problem.

Exact text to append:

```
10. Closure rule (D-023): a row may move to Completed only after the
    corresponding phase exit-checklist matrix row already shows the same
    status with dated evidence, and the Completed row's evidence cell
    must cite that matrix row (file + item id). If no matrix row exists
    for the work, say so explicitly in the evidence cell.
```

Record the convention as a decision-log entry (one short entry citing
DOC-009 and D-023) so it binds future sessions per global rule 5.

Acceptance (DOC-009): the three checklist rows match evidence with dated
reconciliation text; both queue completed rows cite their matrix rows;
intake item 10 present; decision-log entry landed.

---

## Part B — REPRO-001: environment lock + published pack + external re-reduction

### REPRO-1: exact environment lock

Facts on the ground (lock what IS — see Fences): `pyproject.toml` core is
stdlib-only with extras `analysis = ["matplotlib"]` and
`mac = ["mlx-lm>=0.31.3", "transformers<5.13"]`; the Mac measurement venv
is `.venv` (Python 3.13.1) with mlx/mlx-lm/transformers; bundle metadata
already records exact mlx, mlx-lm, transformers versions per run
(`joulewise/environment.py` `_package_version_record`).

DECISIONS:

1. **Mechanism:** two committed `pip freeze` lockfiles under a new
   `env/` directory:
   - `env/mac-measurement-lock.txt` — frozen from the Mac measurement
     venv (`.venv`), the environment that produced the six corpus
     bundles. Header comment records Python version (3.13.1), macOS
     version, and freeze date.
   - `env/analysis-lock.txt` — frozen from the analysis environment
     (the env used for reduction/figures; if analysis currently runs in
     the same `.venv`, freeze that and say so in the header — do not
     invent a separate env).
2. **Relation to pyproject:** pyproject stays the *intent* spec (loose
   pins, installer-facing); the lockfiles are *reconstruction* specs.
   They are used as constraints, not as a parallel dependency list:
   `python3 -m pip install -c env/mac-measurement-lock.txt -e ".[mac]"`.
   This keeps one dependency-declaration surface (pyproject) and makes
   the lock purely additive. No `requirements-lock` install-everything
   file — constraints only.
3. **Regeneration command** (documented at the top of each lockfile):
   `.venv/bin/python -m pip freeze --exclude-editable > env/mac-measurement-lock.txt`
   (analogous for analysis). Regeneration is only legal after a
   deliberate, decision-logged dependency change — see Fences.
4. **CI check (cheap — do it):** one pytest that (a) both lockfiles
   exist, are non-empty, and every non-comment line is `==`-pinned;
   (b) the mac lock's mlx, mlx-lm, and transformers versions equal the
   versions recorded in `runs/example-mac-mlx-local__r1/metadata.json`
   (the canonical corpus bundle). This turns "lock matches the measured
   environment" into an enforced invariant, not a hope. Skip (b) with a
   clear skip reason if the runs/ corpus is absent (clean CI checkout
   without bundles).

### REPRO-2: bundle-pack publication

Corpus: six strict-valid real bundles under `runs/` — three 1.5B reps
(`example-mac-mlx-local__r{1,2,3}`, Qwen2.5-1.5B-Instruct-4bit, ~16 MiB
each) and three 122B reps (`example-mac-mlx-qwen35-122b-512t__r{1,2,3}`,
Qwen3.5-122B-A10B-4bit, ~20 MiB each).

DECISIONS:

1. **Selection (3 bundles, ~52 MiB total):**
   `example-mac-mlx-local__r1`, `example-mac-mlx-local__r2`, and
   `example-mac-mlx-qwen35-122b-512t__r1`. Rationale: one 1.5B and one
   122B rep satisfy the P2-027 row's model coverage; the second 1.5B
   rep lets the external party see repetition-level consistency, the
   cheapest nontrivial cross-bundle check, at +16 MiB.
2. **Pack command** (PR #25 tooling):
   `python3 scripts/package_bundle_pack.py --output dist/jw-pack-2026-07-09 runs/example-mac-mlx-local__r1 runs/example-mac-mlx-local__r2 runs/example-mac-mlx-qwen35-122b-512t__r1`
   The tool embeds git provenance and per-file sha256s in
   `MANIFEST.json` and generates the pack `README.md`.
3. **Where published:** GitHub Release asset on `mpmdw/JouleWise`
   (tag `repro-pack-v1`), as a single `.tar.gz` of the pack directory
   (~52 MiB — far under the 2 GiB asset limit). NOT committed to the
   repo (52 MiB of binary-ish payload in git history is permanent
   weight) and NOT the Lakebed capsule (1 MiB cap). The release body
   quotes the pack's top-level sha256 so the download is checkable
   out-of-band. Copy `env/analysis-lock.txt` INTO the pack directory
   before tarring so the pack is self-sufficient.
4. **One-command instructions text** (goes in the release body and the
   pack README; the "one command" is PR #25's verify, which includes
   strict re-reduction of every bundle):

   ```
   # Requires: Python 3.11+, git. No JouleWise install needed beyond the repo.
   git clone https://github.com/mpmdw/JouleWise && cd JouleWise
   python3 -m venv .repro && .repro/bin/python -m pip install -c env/analysis-lock.txt -e .
   tar xzf ~/Downloads/jw-pack-2026-07-09.tar.gz
   .repro/bin/python scripts/package_bundle_pack.py --verify jw-pack-2026-07-09
   # Expected final line: "valid bundle pack: jw-pack-2026-07-09"
   ```

### REPRO-3: external re-reduction protocol

1. **Who counts as external:** an uninvolved person — not Ed, not any
   agent operating in this repo, and no one with commits in the
   JouleWise history or prior access to the corpus (per NEG-9
   "uninvolved"; a classmate, labmate, or the advisor's designee
   qualifies). Ed recruits; the person's role, not name, is what the
   record needs (name optional, with consent).
2. **What they run:** the REPRO-2 instructions text, verbatim, on their
   own machine (any OS with Python 3.11+; hardware rerunning is
   explicitly out of scope per NEG-9 — this is re-*reduction*, not
   re-measurement).
3. **What they report back:** (a) the full terminal output of the
   verify command; (b) OS + Python version; (c) the sha256 of the
   downloaded tarball; (d) date; (e) one sentence on anything that
   didn't work first try (friction counts as findings).
4. **Where the attestation is recorded:** new file
   `docs/repro/2026-MM-DD-external-rereduction.md` containing the
   verbatim report, the pack tag/sha256 it ran against, and the
   external party's role. The REPRO-001 queue row closes citing this
   file (and, per DOC9-4, the matrix row if one exists).
5. **Claim upgrade unlocked:** per the P2-027 row (TASK_QUEUE.md:129),
   this converts auditability from a design property (L0-scoped claim
   in the review doc) to a **demonstrated** property. On attestation:
   update the P2-027/REPRO-001 rows, and amend the whole-project review
   doc's auditability claim scope from L0 to demonstrated, citing the
   attestation file. Until then the L0 scoping stays.

Acceptance (REPRO-001): lockfiles committed + CI check green; release
asset live with sha256 in the body; attestation file recorded; claim
scope updated. Partial credit is real: lock + published pack land
[AGENT]-side now; the attestation tail is [ED-EXTERNAL] and must not
block the software work from merging.

---

## Fences

- **No dependency upgrades while locking.** Lock the environments AS
  THEY ARE (the environments that produced the corpus). If `pip freeze`
  surfaces something surprising, record it — do not "fix" it. Upgrades
  are separate, decision-logged work that also invalidates REPRO-1's
  CI cross-check by design.
- **Bundle content is immutable.** The pack copies bundles verbatim
  (the tool already refuses symlinks/non-verbatim copies); nothing in
  `runs/` is edited, ever. If a selected bundle fails strict validation
  at pack time, pick a different rep and record why — never touch the
  bundle.
- DOC-009 edits are reconciliations of the status *surface* only: no
  evidence text is altered, and every reconciliation line carries its
  own date distinct from the shipping date.

## DEVIATIONS / OPEN QUESTIONS

1. **Analysis env identity:** if analysis has only ever run inside the
   Mac `.venv`, REPRO-1 collapses to one lockfile plus a header note;
   the spec author could not confirm a separate analysis venv exists.
   Implementer verifies and records which case holds.
2. **`--exclude-editable` flag:** confirm the freeze excludes the
   editable joulewise install (it must — the lock pins third-party
   packages; joulewise itself is pinned by the git tag).
3. **Release tag vs commit:** `repro-pack-v1` should tag the exact
   commit whose tree packed the bundles, so `MANIFEST.json` git
   provenance and the tag agree. If the pack is built on a dirty tree
   the tool records `dirty` — do not publish a dirty-tree pack.
4. **Second 1.5B rep (r2) inclusion** is a recommendation, not a
   requirement; dropping to 2 bundles (~36 MiB) is acceptable if the
   lead prefers the minimal P2-027 reading.
5. **Phase 1 Mac addendum placement:** exact line for the addendum
   depends on the current bullet layout around :253; implementer keeps
   it inside the "Apple Silicon / Mac" subsection, directly under the
   stale Status bullet.
