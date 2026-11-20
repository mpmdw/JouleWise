# File prune g1: historical traces and reports

Branch: `ops/2026-11-10-file-prune-g1-traces`. Base: `origin/main`
`bfe0f4c78`. Local-only work; no push, network, model download, analysis
pipeline, or hardware collection. Coordination files and frozen B5 source
were preserved.

## Change and retention

Merged `origin/ops/2026-11-08-prune-execution` (`0b2f79bce`) first, retaining
its plan, census tools, historical evidence and rollback log. This also
includes `dcaf2ca2c`; no duplicate cherry-pick was needed. Its equivalence
test now requires the immutable `b5/analysis-r1-9bfix-ref` tag.

Deleted 111 dated run-report artifacts (93 under
`2026-11-06-b5-under-90`, 17 under `2026-11-06-b5-robust`, and the old
robust executing review). Every removed
file's Git blob equals the blob at
`archive/process-traces-before-release-prune-2026-11-08` (`901d7580d`).
No original registration, calibration record, issued artifact, seal record,
erratum, measurement bundle, or current runbook was selected for removal.

`docs/ops/FILE-PRUNE-G1.tsv` records all 806 examined paths: 111 DELETE and
695 KEEP decisions, including the specific reader or authority that caused
each KEEP. All 651 remaining process traces stay: current/frozen tests,
kernel/state pointers, seal/erratum/ruling authority, current runbooks and
transitive authority still bind them. The estate-12 anchor specification
stays as uncertain authority. Report/site-related capstone reports stay
under the deliverable deferral; newly imported seat reports whose exact
bytes are absent from the retaining tag also stay. Uncertain means KEEP.

Fable review F5 restored
`docs/legacy/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md`
byte-for-byte from the archive tag: ALIGN's `docs/align/apple_path.md:340`
cites it for the 0.0998 J/token design input. That provenance dependency makes
the inventory row KEEP. The revised stack deletes 409 files and retains 4,762
tracked files before adding the cold-review and fixes reports.

Edited `CANONICAL.md`, extended `docs/ARCHIVE.md`, regenerated
`configs/pins/registry.json`, and corrected the imported plan report's
nonexistent decision-range endpoint from 191 to 190. The docs check caught
that imported citation; no decision was invented. The registry refresh
reindexed targets and picked up existing main-line digest/line changes;
original source digests and protected number bytes were not edited.

## Reference and companion audits

The explicit tracked-source grep covered every deleted full path, including
code, configs, tests, scanners and `.github/`; it found **zero live hits**.
It found 33 historical-record hits and one qualified archive citation before
the new inventory/report were staged. Historical ops census/rollback tables
are immutable snapshot evidence, not checkout readers; the archive guide
now states their tree context. Independent review caught relative file and directory citations in the two
retained parent reports; these now use the archive tag:path form. No test module, refusal site, number-coverage row or timing-map
entry was deleted, so `hazard_refusals.json`, coverage tables and
`test_timings.json` need no change in this group.

## Verification

Local Python 3.13, modules run individually with bytecode disabled and
synthetic temporary directories. A supplementary Python guard rejects home,
real custody and network access; subprocess sources were reviewed separately.
An attempted additional OS sandbox returned `sandbox_apply: Operation not
permitted`; no bypass or escalation was attempted. The Python guard is not
an OS guarantee for arbitrary grandchildren.

- `python3 -m compileall -q joulewise scripts tests`: PASS.
- `python3.13 -B -m unittest tests.b5_analysis.test_frozen_files`: 4, PASS.
- `python3.13 -B -m unittest tests.test_b5_seal_landing`: 9, PASS.
- `python3.13 -B -m unittest tests.test_docs_freshness`: initially 31 with one
  imported dangling decision citation; after correction, 31 PASS.
- `python3.13 -B -m unittest tests.test_prune_ops`: 13, PASS.
- `python3 -B scripts/repin.py --write registry`: completed; subsequent
  `python3 -B scripts/repin.py --check`: PASS, 16 families current.
- `git diff --check`: PASS.

The actual local module commands used
`/private/tmp/jwsol-file-prune/guard_run.py -m unittest <module>` with
`TMPDIR=/private/tmp/jwsol/squeeze/file-prune/tmp`; that runner delegates to
unittest and records elapsed time. No full suite was run, per the brief.
CI remains the full-suite gate. No native MLX or hardware validation is
claimed or needed for these document removals.

## Remaining groups and deferrals

G2 retains all nine D117 Qwen2.5 generations unless their live historical
reader chain is migrated; G3 must preserve frozen `run_campaign.py` and
`whole_window.py` bytes while integrating #668; G4 rechecks already-removed
#654 candidates. Independent read-only review by task `prune_readers_review` (same clone, no
write authority) checked the original 112 blob identities (before F5 restored
the synthesis), the inventory/deletion set,
protected paths and preserved protected-P registry counts (23,594 rows,
15,880 resolved checks). Its relative-citation findings were fixed as above;
an already-missing `e2e-resume/RESULT.md` citation is outside this deletion
set and was not guessed into a different archive identity.

Deferred unchanged: `joulewise/b5_analysis/**`, the `whole_window.py` mirror,
remote node/SSH/vLLM/NVIDIA stack, site/report pipeline, `scored_*`, every
ALIGN v4 path and lane, BYTES, B6, x86 and port work. No coordination task was
registered. Next exact step: g2 on the g1 tip, preserving calibration-plan
and historical reader bindings.
