# L7 SEAM READER B — EXECUTION-DERIVED PRODUCER/CONSUMER GRAPH

**Seat:** L7 (high) — obligation graph derived from *actual runs*: tests, dry-runs, the freeze log, live CLI probes. L6's output not read.
**Audit baseline:** docs/process/audit-baseline-manifest.json @ HEAD **ac3fe1d** (origin/main ac3fe1d). Worktree HEAD 8937dec = baseline + 3 commits (the manifest commit itself + two RUN_STATE/README checkpoint edits). I verified every manifest-bound artifact byte-identical to its manifest digest at my worktree: runbook 25a4e809✓, state kernel f85ea964✓, row registry d248fdc5✓, all three pack digests recomputed **via the project's own `committed_pack_tree_sha256`** (f4c02c8a / 6a8a3bf6 / 1cc0c784)✓. Lens results therefore remain valid under amendment 12.
**Tree proof at exit:** `git status --porcelain=v1 --untracked-files=all` empty; HEAD unchanged (8937dec). All mutation-bearing probes ran in a disposable TMPDIR clone or TMPDIR roots, all deleted.

## 1. Evidence universe (enumerated before findings; 25 items, 21 examined)

| # | Artifact / behavior | Disposition |
|---|---|---|
| U1 | Frozen pack trees ×3 + committed digests | EXECUTED (digests recomputed, match manifest) |
| U2 | Pack generators `--check` ×3 | EXECUTED, PASS |
| U3 | D-134 freeze receipts ×3 + plan-tree pins | Parsed; pin enforcement observed via dry-run refusal + tests |
| U4 | 33 frozen evidence receipts + sidecars | Parsed; horizons computed live (see finding 1) |
| U5 | U11 identity projection receipts ×3 | Via tests (identity pins, pack plans) |
| U6 | Row registry d248fdc5 | Sha-verified vs manifest + freeze receipts |
| U7 | State kernel + `gen_state.py --check` | EXECUTED, PASS |
| U8 | Window runbook (obligation source, sha-pinned) | Read in full (1,589 lines) |
| U9 | Freeze-execution log + dryrun-alpha.json + off-repo §5C receipt | Read; off-repo receipt byte-hash MATCHES recorded sha 94837218… |
| U10 | Arm-readiness lifecycle (freeze/dry-run/arm/verify/consume) | EXECUTED dry-run CLI ×3 states + 638 tests green |
| U11 | T-0 evidence author + operator-input seam | EXECUTED through 4-stage fail-closed input chain |
| U12 | Arm-time freeze-evidence consumption path | Code-traced at all 3 call sites + tests |
| U13 | CLI bundle chain (produce→strict validate→reduce→revalidate) | EXECUTED + tamper falsifier |
| U14 | Campaign runner + frozen-stage `--dry-run` | EXECUTED (10 members enumerated) + test_run_campaign |
| U15 | Calibration ledger/reservation/custody/writer | Tests only (batch B); live `--execute` not run (ED row) |
| U16 | §5B fiducial screen derivation (CH-1) | test_powermetrics_fiducial green |
| U17 | NEG-8 bound mint + whole-window verdict | test_whole_window / _selection green |
| U18 | Extraction → floors → mint → analysis consumption | Batches A+B green; decisive full-fixture proof NOT executed (network) |
| U19 | Duration-margins recorder | test_window_duration_margins green |
| U20 | backup_runs.sh | EXECUTED, exit 0 |
| U21 | prewindow_check.sh | EXECUTED live (correctly NOT READY under fleet load) |
| U22 | quiet_mac_prep.sh | NOT executed (mutates display) — ED |
| U23 | claims_lint / claims index / release_check | EXECUTED + tests |
| U24 | docs freshness gate | test_docs_freshness green |
| U25 | CI-exclusive modules (calexits 2036 s, crash matrix 5317 s) | NOT re-run (budget); last green on #149 CI |

(a9/a10 retained basis = seat 11's scope, excluded.)

**Coverage: 21 / 25.** Unexecuted obligations are listed plainly in §5.

## 2. The execution-derived obligation graph

Every edge below was observed by running it (E) or by executing its test evidence (T):

1. `generate_configs.py` ×3 → **pack bytes** → `--check` byte-gate (E: PASS ×3) → `committed_pack_tree_sha256` (E: matches manifest) → `run_campaign --dry-run` member enumeration (E: 10 members with exact argv).
2. #145 evidence author → **11 PACK evidence receipts/pack + sidecars** → freeze-time `_discover_evidence` (expiry + boot ENFORCED, arm_readiness.py:3021-3027) → **freeze receipt evidence list** → arm/verify/consume via `_freeze_evidence_for_arm` (bytes + boot ONLY — see finding 1) (T + code trace).
3. `generate_arm_readiness.py freeze` → **freeze-0001.json + sidecar** → plan-tree pin → dry-run/arm binding checks (E: my dry-run REFUSE included readiness_freeze_receipt_mismatch when unpinned; T: no-clobber, byte-idempotency, can-never-carry-GO).
4. #147 `author_arm_evidence_t0.py` → **15 T-0 source/evidence pairs (WINDOW_CUSTODY)** → arm `_discover_evidence` with pack+head+boot+now ALL enforced (T; E: the operator-input chain fails closed input-by-input with distinct reason codes — clock-attestation missing → non-canonical bytes → stale/boot-case mismatch → clock-prior-state missing).
5. `arm` → **arm-NNNN.json GO** → `verify` → `consume` → **single-use consumption receipt** (T: atomic race = exactly one consumer; boot change voids all three refusal points; semantic supersession; dry-run receipt rejected by launcher).
6. Reservation CLI + ledger readiness → **reservation rows/head pin** → writer pre-slot lease → **calibration custody + instrument_evidence.json** → chain's §5B jq screen + session-status dispatch (T; live edge = ED).
7. `run_campaign` members → **bundles + campaign_log.jsonl** → `validate-bundle --strict` (E: PASS; tamper → exit 2 re-reduction mismatch) → `reduce` (E) → whole-window verdict → **evaluation_basis.sha256** → `extract_detection_floors` → **floor cells + allowances** → mint tools → analysis engine/claims → claims_lint (E+T all green).
8. `--derive-neg8-drift-bound` → **neg8-drift-bound.json** → verdict `--neg8-drift-bound` (T: stale/underived refusal codes exercised).
9. `record_window_duration_margins` → **margins receipt** → close-out (T).
10. `backup_runs.sh` → backup tree (E: exit 0) and t0.storage_backup_capacity row (T).
11. `prewindow_check.sh` → READY/NOT-READY gate (E: NOT READY, exit 1, under live fleet — the gate works).
12. §12 close-out receipt kinds census: **every named receipt has a producer** — root-preflight & waiver → T-0 ROOT_PREFLIGHT rows (t0.campaign_lock_absent, t0.fresh_roots_waivers); backup-preflight → t0.storage_backup_capacity; margins → U19; freeze/dry-run/arm/consumption → U3/U10. **Zero producerless receipts found at the current head** (the historical §0.6 15-row gap is closed by #147 — but see finding 2 for where that tool lives).

## 3. Executed falsifiers (READY-falsification attempts)

- **F1a** Uncommitted single-byte tamper of frozen ALPHA evidence → `committed_pack_tree_sha256` **REFUSED** (`disk and committed bytes/mode differ…`).
- **F1b** Same tamper committed → digest diverges (894a7cf2… ≠ f4c02c8a…) — every digest-bound consumer refuses.
- **F2** Tampered bundle measurand → `validate-bundle --strict` **exit 2**, names the differing key.
- **F3** dry-run at a non-reviewed head → **REFUSE exit 1** (readiness_reviewed_main_mismatch + freeze/ledger codes); REFUSE receipt still custodied.
- **F4** dry-run into a pre-existing synthetic root → **REFUSE** readiness_root_not_fresh.
- **F5** T-0 author with progressively-corrected operator inputs → **four distinct fail-closed refusals**, nothing authored from partial inputs.
- **F6** prewindow_check under live fleet → **NOT READY exit 1** (load BLOCK + 2 agent processes).

Every falsifier produced a refusal, not a silent pass. I could not make any probed consumer accept tampered or missing producer output.

## 4. Findings

**FINDING 1 (should_fix)** — *Frozen PACK evidence is consumed at arm without its declared horizon; all 33 horizons have already lapsed.* `_freeze_evidence_for_arm` (arm_readiness.py:2957; called at 3628 arm, 3801 verify/consume) authenticates pack evidence by bytes + boot session but never passes `now_monotonic_ns`, while the freeze path (3027) and the WINDOW_CUSTODY path (3620-3626) both enforce expiry. Live probe on the receipts' own boot session: `time.monotonic_ns()` = 1.997e15 > `valid_until_monotonic_ns` = 1.9868e15 for **33/33 receipts across all three packs** (lapsed ≈ 2.8 h before the probe; 24 h horizon from the 08-14 ~03:00 UTC authoring). Failure scenario: the arm consumes attestations whose own bytes declare them expired; a post-hoc reviewer impeaches the readiness chain — an output that neither traces cleanly nor fails closed. Needs a magistrate ruling before ALPHA: enforce (→ mandatory pre-arm re-author + re-freeze, since current evidence is void) or document PACK-namespace `valid_until` as freeze-time-only semantics and record a disposition for the lapsed receipts.

**FINDING 2 (should_fix)** — *The mandatory pre-arm sequence exists only implicitly.* Verified by execution: `git ls-tree 49dcc49 scripts` shows `author_arm_evidence_t0.py` **absent at the frozen measurement-checkout head** (only the freeze-time author + generator exist there; the 15-row ARM_ONLY gap was closed on main by #147/#149). #149 also edited all three packs' `generate_configs.py`, so the committed digests drifted (freeze-log 6246b618… → baseline f4c02c8a…). Consequences: arming at 49dcc49 refuses (gap + missing tool); arming at the current head requires advancing the measurement checkout, which by the runbook's own rule (and `test_dry_run_becomes_stale_after_later_head…`, green) **stales dry-run-0001** — a fresh lead §5C dry-run at the final head is mandatory. No standing doc (RUN_STATE T7 lines 31-33, ed-qualification-session.md step 6, 70h plan) names this sequence; RUN_STATE's "NO REBOOT preserves the frozen evidence" is incomplete. Fail-closed protects soundness; the cost is a burned night or improvisation. (NB: `reviewed_main` reads the *local* origin/main ref, so the un-fetched measurement checkout would also pass the exact-match check against a stale remote ref — the honest-operator threat model covers it, but the checkout-advance step should be explicit.)

**FINDING 3 (nit)** — `joulewise reduce` defaults its re-reduction artifact into the invoker's CWD (cli.py:1873-1875); observed dropping a file into my checkout root. A dirty measurement tree is itself an arm refusal — default elsewhere or require `--output`.

## 5. Unexecuted obligations
Live capture path (sudo powermetrics / MLX / display arming); CI-exclusive calexits + crash-matrix modules (2036 s / 5317 s — last green on #149 CI); the decisive full-fixture mint proof (network download); whole-window verdict + extraction CLIs on a real corpus (fixture-tested only); live reservation `--execute` on the production ledger; `quiet_mac_prep.sh`.

## 6. Ed-qualification rows
1. prewindow READY + quiet_mac_prep on the freed machine (my run proves it blocks while fleets live).
2. Fresh §5C dry-run PASS at the final reviewed head on the advanced measurement checkout (real reservation `--execute` + writer lifecycle, both slots).
3. Live sudo powermetrics fiducial seam (`validate_powermetrics_fiducial --allow-live` → instrument_evidence.json → §5B screen) — the one §6-chain edge unobservable in any test I ran.

## 7. Verdict

**NOT_READY** (component: the execution-derived seam graph), with two work orders:
- **WO-L7-1**: rule + fix the PACK-evidence horizon asymmetry; disposition for the 33 lapsed receipts before ALPHA.
- **WO-L7-2**: write the explicit pre-arm sequence (advance checkout → verify boot session → fresh §5C dry-run PASS at final head → E-steps) into RUN_STATE / ed-qualification / runbook §5C.

The graph itself is strong: 1,478 tests green, 7 executed falsifiers all refused, zero producerless required outputs at the current head, digests and off-repo custody bytes verified to the manifest. What is missing is exactly the two items above — both fail-closed protected, both cheap, both needed before a funded night can proceed as documented.