# Evidence index for the 2026-09-03 post-merge kernel batch

Some sources for this batch live on branches that are not merged to `main`, so
their pointers cannot resolve from a `main` checkout (`scripts/gen_state.py`
requires every kernel pointer target to exist as a file). This file carries the
load-bearing passages verbatim so the kernel rows can cite an on-`main` file
without losing the words they rest on.

Read at `origin/main` = `46eaf18c` on 2026-09-03 by the Opus lieutenant.

---

## Source A — decode-identity trace, file 32 (S3 ruling)

Off-main path:
`docs/process_traces/2026-09-02-decode-identity-set/32-magistrate-synthesis-s1-s3.md`,
branch `fix/2026-09-02-decode-identity-set`, worktree
`/Users/edr/code/JouleWise-wt-decode-id` (read-only).

> ## S3 — machine-absolute pack root (SPLIT; ruled (d) for this lane)
>
> Ruling: **(d) for this lane.** Sol's widening is the honest version of (a)
> and shows why (a) does not fit here: once the pack root is re-rooted at the
> replay, the consumption receipt, launch manifest, window root and lifecycle
> receipts are still resolved by absolute path, so clone-reproducibility needs
> a relocatable-lineage design across `arm_readiness` authentication — a
> design lane with its own consult, not a should-fix on the decode-identity
> branch. Nothing is lost mechanically today (the gate refuses correctly; the
> label reached only through the direct seam is the honest one for "the gate
> could not authenticate the pack"). What lands in this lane: (i) a contract
> paragraph stating the limitation at the lineage layer, dictated below;
> (ii) the direct-seam missing-root refusal test (closes luna 263's residual);
> (iii) a kernel row `LINEAGE-RELOCATABLE-01` in the post-merge kernel batch
> (bench, main).

Owner row: `LINEAGE-RELOCATABLE-01`.

---

## Source B — decode-identity trace, file 46 (cold Fable ruling on packet 45), residual nits

Off-main path:
`docs/process_traces/2026-09-02-decode-identity-set/46-coldgate-fable-ruling-packet-45.md`.

> - NIT-1: `arm_readiness.py:9020` (`expected_path.resolve(strict=True)`) and
> `:10222` (`Path(str(consumption["launch_manifest"]["path"])).resolve(strict=True)`)
> resolve strictly outside any `try`; if the expected file vanishes between the
> earlier strict resolve and these lines, a raw `FileNotFoundError` escapes
> `authenticate_launch_lineage`, and `_read_bundle` (`inputs.py:2778-2782`)
> catches only `LaunchLineageError`. Surfaced by my harness (E2a first attempt;
> cascade S6 first run), reachable in production only as a race. Not a question
> in this packet.
> - NIT-2: the only end-to-end test of the one-use consumption write,
> `test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses`,
> is `@unittest.skip`'d ("STRUCTURAL-BLOCKED",
> `tests/test_arm_readiness_lifecycle.py:751-755`); the "one-use" claim in Cure
> C(i) rests on the primitive (E1) and a code-read mapping.

Owner rows: `LINEAGE-RESOLVE-RACE-01` (NIT-1), `ONE-USE-CONSUMPTION-TEST-01` (NIT-2).

---

## Source C — fresh-Fable docs-vs-truth audit, 2026-09-02

Off-main path:
`docs/process_traces/2026-09-02-fresh-fable-audit/02-audit-docs-vs-truth.md`,
same branch and worktree as sources A and B.

Ranking rule the audit states for itself:

> Rank = how badly a fresh reader (a new session, or Ed's advisor) is misled.
> Tier A: a restarting session would ACT on it and be wrong. Tier B:
> advisor-facing surfaces describe a different project. Tier C: internal
> retensing.

Findings this batch acts on:

- **A3** — D-170 is installed. Evidence cell: "all three landed: #273
  `e0f258ed`, #275 `33f61285`, #274 `b81a2ac5`", with the mechanisms on `main`
  at `.github/pull_request_template.md`, `.github/workflows/gate-ledger.yml`,
  `joulewise/arm_readiness.py` (`_T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS =
  600_000_000_000`), `docs/agent_playbook.md:57`, `tests/test_docs_freshness.py`,
  `docs/orchestration.md:82`. Correction: "Flip D-170 index+body to `adopted`
  naming #273/#274/#275; retire `T26-RULING-INSTALL-01`; mark the 9 deps
  `satisfied` with a `def test_` evidence pointer (D-170's own fence);
  `ED-BRANCH-PROTECTION-E1-01` ... → `queued` [ED-EXTERNAL]." The nine rows
  named: `GAMMA-UNIT-ROSTER-GUARD-01`, `L10-SACRIFICIAL-REHEARSAL-SCHEDULE-01`,
  `S9-01B`, `S9-02`, `S9-03`, `S9-05`, `S9-06`, `T26-RULING-INSTALL-01`,
  `V5-TRANSACTION-01`.
- **A4** — `V4-TRANSACTION-01`. Evidence cell quotes `docs/decision_log.md:210`
  (D-164): "`_v4` is never collected", and D-167 installing `V5-TRANSACTION-01`
  "as the live successor to the retired Qwen2.5 Q2-Q4 windows". Correction:
  "Retire `V4-TRANSACTION-01` by supersession (D-167 pattern used for
  WINDOW-COUNCIL-GATE), keeping its S-0 record as history in the status note ...
  (Retiring a claim-path row is a magistrate call — record it as a D-167
  addendum, not a silent kernel edit.)"
- **A5** — `PIPELINE-SMOKE-LIVE-01`. Evidence cell: "dependency `kind: event`,
  `state: pending`, `target: V5-QWEN3-PACK-GENERATED-S15` — and that row is
  MISSING from the kernel (retired after #241 merged 2026-08-30). The dep can
  never be satisfied mechanically; the row is blocked on a ghost. The true
  remaining precondition is the freeze of the three `_v5` packs (owned by
  `V5-DECODE-IDENTITY-SET-01` ...)." Correction: "Retarget the dep to
  `V5-DECODE-IDENTITY-SET-01` (+ the pack-freeze event) and replace "`_v4`
  manifest" with "`_v5` pack" in the goal."
- **A7** — rulings that promised kernel rows which do not exist. The audit's
  own count: "These are the 3rd–6th 'ruled ≠ installed' instances since
  T26-RULING-INSTALL-01 was created to cure the pattern." The four:
  `LINEAGE-RELOCATABLE-01` (MISSING), `R7F-EXIT3-SEMANTICS-01` (MISSING,
  "#272 merged 20:17Z, batch never run"), "a `_v5` prewindow-pin row (or extend
  PREWINDOW-REGEX-01's acceptance)" for the
  `MAGISTRATE-RULING-UNATTENDED-STAGE1.md` R-12 pin while
  `scripts/prewindow_check.sh:51` still reads "the governed family is the `_v2`
  campaign packs", and "a charter-v3 owner row" for D-170's deferral of item
  4's packet-input-list amendment. The same item also asks for a fifth
  `NIGHT-REHEARSAL-01` acceptance row, ruled by
  `docs/process_traces/2026-09-01-unattended/coldgate-d1-RULING.md` R-7.
- **A9** — `T0-UNATTENDED-01`. Evidence cell quotes the row's own status-note
  tail: "branch impl/t0-unattended-01 is content-identical to main ... the
  remaining rehearsal-evaluator blockers are folded into the D-169 unattended
  lane and will be scheduled by that lane's staged ruling rather than as a
  separate PR." Correction: "Set `T0-UNATTENDED-01` to `blocked` on the D-169
  stage-2 ruling ... so the queue view stops advertising it as READY."
- **A2, B1, B2, B3, B4, C1** — the RUN_STATE and README staleness items applied
  in this batch; each is quoted in `01-lieutenant-report.md` with the bench
  command that confirmed it still holds at `46eaf18c`.

The audit also carries a "soundness fences — KEEP even though old (do not
'reconcile' these)" list. Nothing in this batch touches it; in particular the
D-078 voiding language in `README.md` and the `V5-TRANSACTION-01` fences are
left exactly as they stand.

---

## Source D — code-and-tests audit, 2026-09-02 (on main)

On-main path:
`docs/process_traces/2026-09-02-hands-free-week/13-audit-code-tests-opus.md`.
Section 5 ("The five changes I would make first") is the source of
`RAW-CAPTURE-DIGEST-01`, `SILENT-REFUSAL-TESTS-01`,
`CANONICAL-JSON-ONE-HOME-01`, `INSTRUMENT-PATH-PIN-01` and
`GENERATOR-CORE-01`, in that order.

**Recorded discrepancy inside that audit.** Its §5 item 2 says "Make the six
silent refusals fail a test ... one counterfactual regression per code in the
§2.2 SILENT rows". The §2.2 table does not carry six SILENT rows. It carries
one — M6, `readiness_pack_not_committed` — verdict "**SILENT — no
counterfactual test**"; three rows marked "narrow set silent" (M4, M9, M13) that
each flipped to **COVERED** once a wider module set was run (M4b, M9c, M13b);
and one row, M8 (`launch_binding_mismatch`), whose mutant and verdict cells were
never filled (`<!--M8-->`, `<!--M8V-->`). §2.3 states the count plainly: "Nine
of the ten sampled refusals have a real counterfactual test" and "**One sampled
refusal is unguarded (M6).**" §2.3 separately names four refusals that are
"silent against the module a developer would reach for first" — a coverage-cost
finding, not an absence of coverage. `SILENT-REFUSAL-TESTS-01` is therefore
scoped to what §2.2/§2.3 support, and the "six" is left as an open reconciliation
in that row's status note.

---

## Source E — `_v5` floor-generator counter-review CR-3, 2026-09-02

Off-main path:
`docs/process_traces/2026-09-02-v5-floor-generator/07-opus-counter-review-0f545c33.md`,
branch `feat/2026-09-02-v5-floor-generator`.

> v3's `load_and_verify_families()` carried **six drift refusals** —
> source-byte pin + domain-hash pin for each of decode/prefill/p256, decode
> read from `SOURCE_DECODE_FAMILY_REL` and byte-compared. v5 deletes all six:
> families are generated in-file, and
> `DECODE/PREFILL/P512_FAMILY_DOMAIN_SHA256` init `""` and are **assigned at
> runtime**. Only the schema validator survives. Defensible at authoring time,
> but unlike `CURRENT_FROZEN_RECEIPT_SHA256 = ""` (fail-closed, with a re-pin
> path) this guard class is gone outright with **no registered step to restore
> it after V5-DESK-DAY-01 freezes the packs**.

The review verdict says to register CR-3 before the desk day. The magistrate
selected option 1 for its row state: the freeze is a pending hard start
dependency, so kernel invariant 3 requires `BLOCKED`.

Owner row: `FLOOR-V5-DRIFT-REPIN-01`.
