# Contract-lens refutation and ruling — D-176 F1/F2

## Q1 — `PRODUCTION_CUSTODY_ROOTS`

**Q1.1 — Shape: a frozen tuple of `(role, derivation, operand)`, not a frozen list of paths.** The census that is frozen is the *role set and its derivation rule*; the resolved paths are recomputed each evaluation. Four derivations only: `LITERAL`, `HOME_RELATIVE`, `ARM_DECLARED`, `CLONE_DERIVED`. A reviewed diff is required to add/remove a role or change a derivation. Rejected: an all-literal census — it goes stale at every measurement clone (`/Users/edr/JouleWise-measurement-v5-<date>-<sha>`) and every window custody dir, and a stale census **false-PASSes G6** while the rehearsal writes into live production.

**Q1.2 — The four production-window roots are `ARM_DECLARED`, not literal.** They already exist, exactly and exhaustively, as `ARM_CONTEXT_KEYS` `claim_runs_root, bound_runs_root, custody_root, quarantine_root` plus `claim_backup_destination, bound_backup_destination` (`joulewise/arm_readiness.py:363–374`), and are enforced fresh/distinct/empty at `joulewise/arm_readiness.py:8095–8155` and re-checked at consumption `:9679–9683`. The constant names these six keys; `resolve_production_custody_roots(receipt)` reads them from `receipt["arm_context"]`. Substitution is then an **ARM digest mismatch** (GO binds `arm_receipt.sha256`, §2), never a lookup.

**Q1.3 — `~/night-custody` is never a root; `~/night-custody/magistrate` is (`HOME_RELATIVE`).** Source: `scripts/magistrate_watchdog.py:55–57`, `docs/process/MAGISTRATE_WATCHDOG.md:3`. Rejected: "custody parent" as a root — the rehearsal lives at `~/night-custody/rehearsal-20260909`, so G6 becomes **unpassable**, which buys pressure to weaken the predicate.

**Q1.4 — Repo runs/ledger root is `CLONE_DERIVED`:** `Path(arm_readiness.__file__).resolve().parents[1] / "runs"`, matching `joulewise/calibration_ledger.py:94–95`. True in every clone; no literal to go stale.

**Q1.5 — iCloud backup root is `LITERAL`,** the single tuple entry at `scripts/check_paper_replay_fence.py:86–88` (mirrored `paper_excursion_decomposition.py:95`). The constant **ignores** `JOULEWISE_BACKUP_ROOTS` (`check_paper_replay_fence.py:333–335`). Rejected: honouring the env override — the census becomes shrinkable from the rehearsal's own environment.

**Q1.6 — Predicate: bidirectional component-prefix on `resolve(strict=True)`.** Keep `_contains` (`joulewise/t0_rehearsal.py:741–746`) and both-direction use (`:785`) — `Path.relative_to` after strict resolve is realpath-based, follows symlinks, treats equality as overlap, and cannot produce the `rehearsal-2` / `rehearsal-20260909` false hit a string prefix would. Any `resolution_error` FAILs (`:782–783`); a non-resolvable production root is never "disjoint by absence".

**Q1.7 — Consumer-side gap (blocking, contract text).** `night_gate.py:277` requires `custody_root` to be only a *non-empty string* (unlike `measurement_root`, `:263–268`). §6 says "resolved `measurement_root` and `custody_root`" but nothing forbids a relative `custody_root`, which resolves against CWD and makes the predicate CWD-dependent. Add to §6: both must be absolute and `resolve(strict=True)`; otherwise refuse `launch_go_receipt_invalid`, detail `rehearsal_roots_not_disjoint`.

**Q1.8 — G6 reads the constant; the manifest key is retired.** `EvidenceBundle.production_roots` (`joulewise/t0_rehearsal.py:196,206`) is populated from `resolve_production_custody_roots(<the bundle's ARM receipt>)`, and `production_roots` is **deleted** from the bundle-manifest schema (`scripts/rehearse_t0_unattended.py:149–175`); the exact-key manifest check (`:127`) then refuses any bundle still carrying it. Rejected: caller-supplied roots — precisely the "incomplete root census" forgery §7's replay list already requires refusing.

## Q2 — deterministic input lookup

**Q2.1 — `pack_root` is not looked up: it is the plan's `measurement_root`** (`night_gate.py:263–268`, absolute, inside the plan bytes GO pins as `plan_sha256`). The driver passes it verbatim as `--pack-root`. Substitution is already a refusal: `arm_readiness.py:9684–9688` requires `window_custody_root/pack_root.name == arm_receipt.parent.parent`.

**Q2.2 — Option (c) for the ARM receipt; no selection, ever.** The driver's own ARM step writes `arm-NNNN.json` and returns `{receipt_path, receipt_sha256}` (`arm_readiness.py:8410,8465–8469`); the driver carries that pair forward and writes it into GO `arm_receipt` (§2). A glob, a "latest", or a plan-declared locator is refused. Rejected: option (a) plan-carried locators — a locator whose target digest is not co-located is a **redirection surface**, i.e. an ambiguity rather than a mismatch.

**Q2.3 — Option (b) for the remaining two, fixed names under plan `custody_root`,** matching the existing `night/` convention (`run_night.py:775`) and the watchdog's fixed `night_plan.json` (`magistrate_watchdog.py:259`): `night/launch_manifest.json` (keys `arm_readiness.py:708–714`), `night/go_receipt.json` (§10.1 F2). Absent → `launch_go_receipt_missing`; any second candidate under a different name, or a symlink, → `launch_go_receipt_invalid`. Each is digest-pinned in GO (`launch_manifest_sha256`).

**Q2.4 — Preparation is a new `run_night.py prepare --plan` subcommand** (`run_night.py:1458–1470`); it writes `night/launch_manifest.json`, `step6_confirmation_record.json` and the authorization record, then re-authors the plan bindings via `write_night_plan` (`night_plan_writer.py:38`). Preparation never issues GO.

**Q2.5 — Sequence, exact reads/writes.** prepare (reads plan; writes the three records) → ARM verify (reads pack + custody; writes `arm-NNNN.json` + sidecar) → GO issue (reads plan bytes, ARM receipt, manifest, `window.env`, chain, T-0 set; writes create-once 0600 `night/go_receipt.json`) → launcher argv `--pack-root/--arm-receipt/--arm-readiness-custody-root/--launch-manifest/--night-plan/--go-receipt/--step6-confirmation-table/--expected-confirmation-digest` (`launch_window.py:39–58`). GO is refused if the ARM step did not run this night in this boot session.

**Q2.6 — Refusal rule.** Missing → `launch_go_receipt_missing`; duplicate/ambiguous candidate, or any digest disagreement between plan, GO and bytes on disk → `launch_go_receipt_invalid`, `detail` naming the field. No fallback path resolves an ambiguity by preference order.

**VERDICT: adopt Q1.1–Q1.8 and Q2.1–Q2.6; the constant freezes roles-and-derivations (six ARM-declared, one home-relative, one clone-derived, one literal), and every driver input is either digest-pinned or self-written, so substitution is a digest mismatch — subject to the Q1.7 contract amendment requiring an absolute, strictly-resolved plan `custody_root`.**
