# Rulings and scope decisions owed from the 2026-09-04 fan-out

## C3-RECOGNIZER-EXACT-01  [findings/partial]
- (verification_gap, blocking) D-105 requires an independent delta audit at the exact landed head; this session neither commits nor starts another agent by instruction.
  needs: After harvest and commit, run a fresh independent audit over the exact commit.

## CGV-HARDEN-01  [blocked/partial]
- (lead_ruling, blocking) No convening cold-gate runner exists at the requested base, so no contract-defined production call site can be wired.
  needs: Choose the runner file, command interface, receipt directory, and naming rule.
  NEEDS_RULING block:
  NEEDS_RULING: choose among a persistence-only command, a validator wrapper, or integration into the future convening runner. Recommendation: integrate `persist_validator_receipt` into the future runner so error handling remains unified and `COLDGATE-HANDOFF-01` stays a separate contract.
  
  After that ruling:
  
  1. Wire the exact validator standard-output bytes into the primitive.
  2. Add a production-call-site regression.
  3. Have the magistrate update `docs/process/state_kernel.json` and regenerate `TASK_QUEUE.md` and `RUN_STATE.md`.

## CHARTER-V3-PACKET-INPUTS-01  [blocked/partial]
- (lead_ruling, blocking) NEEDS_RULING: the candidate cannot become operative until Ed re-ratifies its exact bytes.
  needs: Approve candidate SHA-256 9275316e46c6c7bf084e35caa927dae9727dd544dae72656bed22ba82d22b977, or provide exact wording changes. Recommendation: approve if REFUSE-with-merits-unruled correctly preserves the charter's verdict vocabulary.
  NEEDS_RULING block:
  NEEDS_RULING: Ed must approve the exact candidate digest or request revised wording. After approval, the lead must atomically promote the candidate, update the registry, and record ratification before any cold gate uses v3.

## COLDGATE-HANDOFF-01  [blocked/partial]
- (lead_ruling, blocking) The controlling consult leaves the actual judge transport undecided.
  needs: Choose the transport contract and first launcher; option A in 00-design.md is recommended.
- (lead_ruling, blocking) The Ed-ratified charter registry still requires amendment and was expressly read-only.
  needs: Cold-gate ruling and Ed ratification of the proposed registry text.
- (verification_gap, blocking) No actual judge request or identity-bound runner receipt exists yet.
  needs: Implement and live-verify the ruled launcher adapter and runner receipt.
- (residual_risk, blocking) Validator PASS remains validation-only and must not convene a cold judge.
  needs: Retain the operational fence until complete transport verification.
  NEEDS_RULING block:
  NEEDS_RULING:
  
  1. Choose the exact byte-to-request transport and first judge launcher. Recommendation: canonical JSON with base64 source bytes, delivered once through standard input with a transport-observed request digest.
  2. Cold-gate and Ed-ratify the proposed charter-registry amendment.
  3. Implement the runner receipt binding request digest and judge request/session identity.
  4. Perform the lead-owned clean-environment live launch.
  5. Only then update the protected kernel, queue, and run-state files and remove the operational fence.

## EPOCH-LINT-01  [blocked/partial]
- (lead_ruling, blocking) No cited authority selects how future revisions declare a complete obligation census or represent a source commit created only while the runsheet executes.
  needs: Choose inline declarations or a digest-bound sidecar, and choose authenticated patch overlays or pre-materialized preview commits.
  NEEDS_RULING block:
  NEEDS_RULING:
  
  - Choose inline obligation declarations in the runsheet (recommended) or a digest-bound sidecar.
  - For patch-created symbols, choose an authenticated patch overlay on a named base (recommended) or require a pre-materialized preview commit.
  
  After ruling: encode the complete census, add declaration-removal regressions, wire the command into revision ratification, and retain the clean JSON transcript.

## FLOOR-WORKLOAD-SIZING-01  [blocked/partial]
- (lead_ruling, blocking) D-166 now owns production workload selection and conflicts with treating the older effect-to-floor idea as another selector.
  needs: Rule whether FLOOR-WORKLOAD-SIZING-01 is retired as superseded (recommended) or retained as a separate diagnostic study that cannot alter v5.
- (verification_gap, blocking) No issued G2-a live record exists, so the exact prefill size, measured pilot ratios, and regenerated successor configurations cannot yet be produced.
  needs: Complete the lead-owned quiet-machine G2-a window, issue its immutable summary and selection record, then generate and verify the successor packs.
  NEEDS_RULING block:
  NEEDS_RULING: retire the row as superseded by D-166 (recommended), or authorize a separately preregistered, non-selecting diagnostic margin study.

## GENERATOR-CORE-01  [blocked/partial]
- (lead_ruling, blocking) Nine historical generator sources are authenticated pack-tree files; modifying them makes committed_pack_tree_sha256 refuse.
  needs: Rule whether frozen historical snapshots are exempt from deduplication. Recommendation: exempt them and require the core for unfrozen and future producers.
- (lead_ruling, blocking) The next Qwen3 floor producers exist only on unmerged branch feat/2026-09-02-v5-floor-generator at 557b7fc5.
  needs: Recommendation: land this core first, then rebase that reviewed branch and replace its copied mechanics with shared-core imports.

## MIDCAMPAIGN-CURE-GENERATION-01  [blocked/partial]
- (lead_ruling, blocking) The current paper draft lacks the required interruption limitation, but this task expressly forbids editing docs/paper/draft-v2-skeleton.md.
  needs: Have the paper owner apply the proposed paragraph from the report to Further limitations, or designate another canonical reader-facing paper artifact.
  NEEDS_RULING block:
  NEEDS_RULING:** the paper-facing acceptance clause remains open because its canonical target was explicitly write-protected. No prohibited or out-of-scope file was changed.

## MODULARITY-01  [blocked/partial]
- (lead_ruling, blocking) NEEDS_RULING: place chat-template and thinking-mode prompt realization in the runtime adapter or a new workload-renderer interface.
  needs: Recommend a runtime-owned capability emitting runtime-neutral provenance.
- (lead_ruling, blocking) NEEDS_RULING: parameterize the issued A/B/B/A estimator or add a sibling registry-dispatched estimator.
  needs: Recommend preserving issued semantics and adding an authenticated sibling estimator.

## NODE-CUSTODY-DEFAULT-01  [blocked/partial]
- (lead_ruling, blocking) No adopted ruling defines how a unique default client namespace proves that its owner is inactive before another process reclaims its manifest.
  needs: Rule the namespace and liveness contract; recommendation: unique per-client directories under the stable default base, each protected by a lifetime advisory lease, with later processes scanning only lease-acquirable directories and preserving the existing scope equality check.

## PHASE-SHARE-ESTIMAND-01  [findings/partial]
- (lead_ruling, blocking) Exact measured-curve arithmetic refutes the row's expected scalar uncertainty reduction, and no authority defines a different publishable joint estimand.
  needs: Close the scalar phase-share/asymmetry proposal as a null result (recommended), or authorize a separately pre-registered phase-allocation/closure estimand.
  NEEDS_RULING block:
  NEEDS_RULING: close the expected scalar improvement as a measured null result, or authorize a new closure estimand with prospective analysis-plan, floor-transport, provenance, and claim-ceiling rules. The magistrate must also update the lead-owned kernel, queue, run-state, and decision records.

## PREWINDOW-REGEX-01  [findings/complete]
- (lead_ruling, nonblocking) Ruling S-7 requires the owning environmental-census seat's assent to be solicited at the next council touch.
  needs: Record that assent; implementation is not blocked.
  NEEDS_RULING block:
  NEEDS_RULING, nonblocking:
  
  - The magistrate should mark the already-landed row complete in the reserved kernel and regenerate `TASK_QUEUE.md` and `RUN_STATE.md`.
  - The next council touch should record the owning environmental-census seat’s assent required by ruling S-7.

## QUIET-GUARD-01  [findings/partial]
- (verification_gap, blocking) The opt-in live macOS kernel inventory test and root-owned installation were not exercised.
  needs: Lead-owned live test and Ed/lead interactive inactive-install verification.
- (baseline_drift, blocking) The kernel row still contains the T3-CHAR-PAIR-01 dependency and superseded full-rollout wording despite D-114 and merged PR #107.
  needs: Magistrate reconciliation of the prohibited kernel and generated projections.
- (lead_ruling, blocking) NEEDS_RULING QG-R1: whether installed-INACTIVE acceptance requires observation on Ed's host is not settled.
  needs: Choose (A, recommended) require inactive host installation before closure, or (B) close software acceptance and register installation separately.
- (verification_gap, blocking) The new repair has not received the row-required independent audit and delta re-audit.
  needs: Run the gauntlet after harvest and commit.

## R7F-EXIT3-SEMANTICS-01  [blocked/partial]
- (lead_ruling, blocking) The authority explicitly did not decide whether earlier mismatches survive a later producer exit 3 or whether retained-digest drift is exit 2 or exit 3.
  needs: Choose design option A, B, or C from the report; recommendation: A.
- (verification_gap, blocking) A counterfactual regression cannot honestly encode an expected disposition before that choice is ruled.
  needs: Resume implementation after the ruling and add the report's mixed-failure, digest-drift, disposition-consistency, and silent-producer regressions.
  NEEDS_RULING block:
  NEEDS_RULING: choose option A, B, or C. Option A is recommended: exit 2 means established disagreement; exit 3 means incomplete replay; earlier mismatches remain visible when a later unavailable input makes exit 3 primary.
  
  No executable change was made because either code path would make an explicitly deferred policy choice.
  
  ## Verification notes
  
  The focused ten-test set passed. The repository-wide suite and retained-corpus replay were not run, as instructed.
  
  ## Residual risk
  
  Current behavior remains fail-closed but can hide an earlier mismatch when a later producer exits 3, and it labels some present-byte digest disagreements as unavailable.

## doc008  [blocked/partial]
- (scope_deviation, blocking) DOC-008 conditions 8 and 9 require excluded root files.
  needs: Expand scope for AGENT_PLAN.md, README.md, and PROJECT_STATUS.md.
- (lead_ruling, blocking) PROJECT_STATUS.md compaction and semantic claims are explicitly lead-authored.
  needs: Lead compacts and signs off PROJECT_STATUS.md, including reconciliation to D-171.

## docs-vs-truth  [blocked/partial]
- (scope_deviation, blocking) README.md and PROJECT_STATUS.md are mission targets but are excluded by the exhaustive write scope.
  needs: Resume with those two paths added to WRITE_SCOPE, or accept the authorized partial implementation.

## instrument-path-pin  [blocked/partial]
- (scope_deviation, blocking) The edited estimator module no longer matches the digest in the active issued calibration-acceptance artifact, so that artifact is correctly reported as stale.
  needs: Authorize the successor artifact path and resume this task.

## p1-rows  [clean/complete]
- (lead_ruling, nonblocking) P1-008 combines unresolved academic dates with scope and hardware questions governed elsewhere.
  needs: Retire P1-008 and open a narrow external-input row for the final-report and colloquium dates.

## p2-rows  [findings/complete]
- (lead_ruling, nonblocking) The retirement recommendations require the magistrate to amend the protected task registry.
  needs: Adjudicate P2-027, P2-035, P2-047A, and P2-050, then update the kernel and regenerate its projections.

## rq-refresh  [findings/complete]
- (lead_ruling, nonblocking) The audit leaves four non-registry paper characterizations outside _v5 and does not settle whether to collect a bounded null or narrow the paper section.
  needs: Resolve in the paper-owning lane; no choice was invented here.

## v5-desk-gaps  [blocked/partial]
- (lead_ruling, blocking) The requested final mint inputs contain post-collection evidence and cannot truthfully be frozen inside the pre-collection pack.
  needs: Rule the artifact lifecycle; the report recommends freezing a non-mintable requirements record and issuing final inputs in transaction custody.
- (lead_ruling, blocking) No authority chooses a shared extraction specification or one specification per floor-producing model.
  needs: Choose the topology; the report recommends one specification per producer.
- (lead_ruling, blocking) The paper rows do not fix reader-facing component labels, sentence grammar, the authenticated renderer input, or the final-night completion field.
  needs: Issue those contracts and decide whether acceptance covers the complete current renderer or only close-out-backed fills.
- (baseline_drift, blocking) The close-out-backed paper rows are absent at this head and exist only on the unmerged paper outcome branch.
  needs: Land or nominate that branch before vocabulary-synchronized implementation.
- (scope_deviation, blocking) The generated packs and paper surfaces are outside the exhaustive write allowlist.
  needs: Expand scope only if this lane must land those files.
  NEEDS_RULING block:
  NEEDS_RULING` table with options and recommendations, scope request, follow-on checklist, executed evidence, and pasted first-use audit.
  
  No production code was changed because each route would either invent an unsettled evidence contract or write outside the allowlist.
  
  ## Verification notes
  
  The repository-wide suite was not run. All focused pack, close-out, and frozen-renderer tests passed.
  
  ## Residual risk
  
  Implementation should resume only after the lead rules the custody lifecycle, extraction topology, and rendering contract, and resolves the requested scope expansion.