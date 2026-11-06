# Main repository pruning plan

Date: 2026-11-06

Scope: tracked files on `main`; planning only (this report deletes nothing).

## Decision rule and safety boundary

This plan distinguishes **safe-delete** (remove from the next pruning change),
**archive** (remove from the live code/document surface but retain in a clearly
historical in-repository location or release bundle), and **keep** (live or
custody-bearing). A zero textual-reference count is discovery evidence, not by
itself deletion authority. Before any deletion, repeat the reference census at
the landing commit, inspect dynamic imports/CLI entry points and pins, and run
the focused tests plus the canonical suite.

Measurement custody is an absolute exclusion. Do **not** delete or rewrite raw
captures, manifests, receipts, hashes, calibration acceptances, registrations,
analysis inputs/outputs, fixtures that replay those objects, or process traces
that establish issuance, supersession, review, or chain of custody. This follows
the repository's own finding that backups and custody-store manifests are
required for every replayed energy/bound/floor and are classified KEEP
(`docs/process_traces/2026-09-29-interactive-ff50b201/80-prune/10-code-sol.md:341-342`).
Likewise, old calibration files are **not unused configs**: for example the r2
acceptance is named by its successor and by extraction specs
(`configs/calibration/calibration_acceptance_d079_v2_n17_r3.json:498`,
`configs/floor_mint/d117_qwen25_7b_v2_extraction_spec.json:93-94`). Git history
alone is not an acceptable substitute for custody evidence.

## Measured baseline and method

At this checkout, `git ls-files` reports **13,031 tracked files**. The largest
candidate surface is not ordinary source: `docs/process_traces/` contains
**8,105 files / 174,388 KiB**, compared with **109 / 1,588 KiB** in
`docs/run_reports/`, **177 / 5,400 KiB** in `scripts/`, **2,511 / 27,132 KiB**
in `configs/`, and **1,048 / 80,964 KiB** in `tests/` (all sizes from `du -sk`).
Those process-trace bytes are large but custody-sensitive, so size is not a
safe-delete argument.

Discovery used only tracked repository content:

```text
git ls-files
git ls-files '<root>/**' | wc -l
du -sk docs/process_traces docs/run_reports scripts configs tests
rg -n -F '<path>' -g '!docs/site/**' -g '!node_modules/**'
rg -n -i 'superseded|deprecated|obsolete|retired|historical only' scripts configs docs
```

The earlier read-only code census is useful corroboration, not fresh authority:
it examined 103 production, 82 script, and 169 test modules and explicitly calls
its counts lexical rather than independent gates
(`docs/process_traces/2026-09-29-interactive-ff50b201/80-prune/10-code-sol.md:122-133`).

## Classified inventory

| ID | Class | Concrete target | Evidence and disposition |
|---|---|---|---|
| SD-1 | **safe-delete** | `tests/test_s0_line_audit_guard.py` and the obsolete “Immutable line audit” block it solely guards | The test declares that it protects a runsheet excerpt (`tests/test_s0_line_audit_guard.py:1-4`) rather than a measurement result. The prior census classifies this coordinate fortification DELETE because source-reading custody is not measurement custody (`docs/process_traces/2026-09-29-interactive-ff50b201/80-prune/10-code-sol.md:365`). Remove the test and guarded historical block together; retain the underlying run report and any measurement evidence. Gate: `rg -n 'Immutable line audit|test_s0_line_audit_guard'` must show no live contract consumer after the change. |
| SD-2 | **safe-delete** | exact duplicate font weights `docs/site/fonts/IBMPlexSans-600.woff2` and `docs/site/fonts/Fraunces-900.woff2`, after CSS aliasing to their byte-identical retained files | SHA-256 census found each pair byte-identical: Plex 400/600 are both `056e4e2459f5…` (40,240 bytes) and Fraunces 600/900 are both `48282a415ec2…` (67,388 bytes). Keep one file per digest and update only generated-site font references. Gate: rebuild the site, verify the two retained digests, and run link/site tests. These presentation assets contain no measurement custody. |
| A-1 | **archive** | inactive quiet-lease implementation: `joulewise/quiet_guard.py`, `scripts/quiet_guard.py`, `scripts/quiet_guard_privileged.py`, `scripts/setup_quiet_guard.sh`, and their lease-only tests | The client calls itself inactive (`scripts/quiet_guard.py:1-2`); the engine says it cannot promote a production lease (`joulewise/quiet_guard.py:1-5`) and hard-refuses live promotion (`joulewise/quiet_guard.py:119`, `joulewise/quiet_guard.py:222`). Archive a source snapshot plus design note; remove it from runtime/test discovery. **Do not remove** shared active process-census primitives. This matches the prior DELETE-engine-only finding (`docs/process_traces/2026-09-29-interactive-ff50b201/80-prune/10-code-sol.md:326`). |
| A-2 | **archive** | staged scheduler façade `joulewise/scheduler_gates.py` and its dedicated tests/schema, subject to a fresh import/caller census | The prior census found no active production/script caller, 1,078 production lines, and an always-NO-GO façade because stages remain unimplemented (`docs/process_traces/2026-09-29-interactive-ff50b201/80-prune/10-code-sol.md:351`). Archive the design and typed receipt examples; retain the actual checks in the launch path. Gate: AST import census, CLI/help census, and focused launch/night tests at landing. |
| A-3 | **archive** | historical agent bridge adapters, converging on one supported runner: evaluate `scripts/codex-run`, `scripts/codex-bridge`, `scripts/codex-app-bridge.mjs`, and `scripts/codex-mcp-server.mjs`; retain `scripts/bridge` until the replacement proves scope/report parity | The repository currently carries parallel runner routes; the prior assessment says to retain scope enforcement, IPC ownership, sandboxing, and one report format while retiring compatibility adapters (`docs/process_traces/2026-09-29-interactive-ff50b201/80-prune/10-code-sol.md:366`). This is archive, not immediate delete, because the current reference census still finds non-trace references to all five routes. Preserve prompt/report records in process traces. |
| A-4 | **archive** | superseded operational prose in `docs/agent_playbook.md` under “Historical Missions M1–M10” | The document itself says these wrappers are retained implementation history and must not be selected (`docs/agent_playbook.md:57-63`). Move the section verbatim to `docs/legacy/` and leave a short pointer in the live playbook. This removes stale “next/gate/branch” language without erasing history. |
| A-5 | **archive** | verified logical-deletion workflow `scripts/reauthor_clean.py` and `tests/test_reauthor_clean.py`, only after the runbook adopts preserve-and-new-namespace semantics | The script remains pinned and tested, so it is not dead today (`configs/pins/registry.json:2794`, `tests/test_reauthor_clean.py:23`). However, the prior assessment found its output is a destruction receipt, not a measurement, and recommends preserving the old namespace and creating a fresh one (`docs/process_traces/2026-09-29-interactive-ff50b201/80-prune/10-code-sol.md:328`). Archive only after removing live callers and pins; never delete existing cleanup receipts or custody traces. |
| K-1 | **keep** | all `docs/process_traces/**`, `docs/evidence/**`, tracked analysis/figure artifacts, and historical run reports | These files include review exhibits, supersession evidence, manifests, hashes, and custody records. Exact duplicates inside packets are intentional self-contained exhibits; deduplicating them would change packet bytes and invalidate historical hashes. Keep byte-identical. A future storage migration may pack immutable directories only if a verified index preserves path, digest, size, and restore behavior. |
| K-2 | **keep** | `scripts/backup_runs.sh`, package/hydrate tools, custody readers, and restore tests | `run_campaign.py` actively names the backup script (`scripts/run_campaign.py:714`), and the prior census classifies this mechanism KEEP because primary evidence custody is necessary (`docs/process_traces/2026-09-29-interactive-ff50b201/80-prune/10-code-sol.md:341`). |
| K-3 | **keep** | `scripts/mint_floor_artifact.py`, `scripts/mint_floor_artifact_generalized.py`, extraction/mint modules, and their tests | These look duplicated by name, but both are pinned (`configs/pins/registry.json:2763-2764`), while the generalized producer is still prescribed by the live v5 analysis plan (`configs/campaigns/v5_claim_25g83/analysis_plan_block5.md:165`). Exact recomputation prevents understated floors, so the prior assessment classifies the mechanism KEEP (`docs/process_traces/2026-09-29-interactive-ff50b201/80-prune/10-code-sol.md:342`). Consolidation may share internals but must preserve both frozen entry points and byte-identical happy-path output. |
| K-4 | **keep** | calibration acceptances/preregistrations, `configs/arm_readiness/*`, campaign plan trees, pin registries, and old schema fixtures | These form explicit predecessor/successor chains and replay inputs. The live arm-readiness code directly names the legacy histsem pinset (`joulewise/arm_readiness.py:3268`), and v5 plan trees name the v2 row registry (`configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json:3157`). “Legacy”, version suffixes, or supersession are evidence of lineage, not evidence of non-use. |
| K-5 | **keep** | whole-window joins, identity pins, environment/sampler gates, analysis registries, scored reducers, numerical paper suppliers, and their behavior tests | These mechanisms protect population membership, model/prompt identity, contamination, sample registration, numerator/denominator conservation, and published quantities. The earlier assessment explicitly classifies whole-window custody KEEP (`docs/process_traces/2026-09-29-interactive-ff50b201/80-prune/10-code-sol.md:329`), identity projection KEEP (`docs/process_traces/2026-09-29-interactive-ff50b201/80-prune/10-code-sol.md:334`), and environment controls KEEP after observed contamination of 43/50 bundles (`docs/process_traces/2026-09-29-interactive-ff50b201/80-prune/10-code-sol.md:347`). They may be internally simplified only with equivalence proofs, never pruned as “unreferenced.” |

## Landing sequence

1. **Freeze the custody exclusion list.** Generate a manifest of every proposed
   path with SHA-256, size, Git object id, textual referrers, pin-registry rows,
   and whether it is contained by a sealed inventory. Any custody/pin/seal hit
   changes the classification to KEEP unless an owning contract explicitly
   authorizes archival relocation.
2. **Land SD-1 alone.** Remove the obsolete coordinate guard and its guarded
   historical block, run its reference census, documentation checks, and the
   canonical suite. No analysis output should change.
3. **Land SD-2 alone.** Alias CSS to one file for each identical font digest,
   rebuild the site, compare all non-font generated bytes, and visually inspect
   the rendered pages. Treat any rendering or non-font byte delta as failure.
4. **Archive A-1/A-2 in separate PRs.** First prove no live imports, CLI entry
   points, config strings, or dynamic loaders. Move source snapshots and design
   rationale to `docs/legacy/`, then remove runtime/test wiring. Run focused
   launch/night/process tests plus the canonical suite.
5. **Consolidate A-3 rather than deleting blindly.** Select one runner, publish
   a compatibility table (write-scope, report envelope, cancellation, IPC
   ownership, sandbox, one-hop behavior), migrate live docs/config, then archive
   adapters one at a time. Process traces remain untouched.
6. **Archive A-4 verbatim.** Check every inbound link and leave a stable live
   pointer. This is documentation movement only.
7. **Defer A-5 until policy changes.** Adopt preserve-and-new-namespace in the
   owning runbook, demonstrate that no live command invokes reauthor cleanup,
   and preserve all prior destruction receipts. Then archive code and tests.

## Required proof for every pruning PR

* Record before/after `git ls-files`, byte totals, exact removed paths, inbound
  references, pins, sealed-inventory hits, and Git blob ids.
* Run `python3 -m unittest discover -s tests`. Focused checks supplement rather
  than replace it for code/config changes.
* For any analysis-adjacent change, run the owning replay/equivalence test and
  compare happy-path outputs byte-for-byte. A changed digest is a failed prune,
  not an acceptable regeneration.
* For site-only changes, rebuild, run link/site checks, compare non-target
  outputs byte-for-byte, and capture a screenshot.
* Do not combine pruning with refactors or schema changes. One mechanism per PR
  keeps reversibility and makes a changed output attributable.

## Expected result

The first two safe deletes remove one obsolete process-only guard and two
duplicate presentation blobs without touching scientific computation or
custody. The archive queue then removes inactive runtime surface and stale live
instructions while retaining their history. The largest directory remains in
place deliberately: its apparent duplication is dominated by self-contained
review packets and measurement-custody history, where deletion would cost more
trust than it saves in bytes.
