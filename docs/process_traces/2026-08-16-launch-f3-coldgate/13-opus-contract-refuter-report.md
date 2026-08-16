# PAIRED REFUTER REPORT — WO-LAUNCH-BINDING F3 cold gate
**Lens:** CONTRACT (adopted WO contract + F2 mechanism, `docs/decision_log.md`; launch-lineage consult; D-078 refusal discipline)
**Target:** `12-cold-adjudicator-ruling.md`
**Code independently traced at `66884c6`** in the read-only branch worktree (nothing modified).

---

## Q1 — Finding 1.2's evidence chain: does it reach digest-bound LAUNCH_RECIPE identities?

### F-R1 — **WEAKENED (materially): the chain reaches the identities, but NOT where the ruling says. The stated hop is schema-impossible.**

The ruling's §2.1 Anchor column and Finding 1.2 both assert:

> arm receipt → `t0.single_launch_capability` row → evidence receipt `input_artifacts`

**The evidence receipt cannot contain `input_artifacts`.** `EVIDENCE_RECEIPT_KEYS` (`/Users/edr/code/JouleWise/joulewise/arm_readiness.py:344-358`) is `{schema_version, evidence_id, kind, status, issued_at_utc, boot_session_id, valid_until_monotonic_ns, pack_sha256, head_commit, facts, checks, reason_codes, assurance}` — no such key. It is enforced by `_require_exact_keys` (`arm_readiness.py:~740`, strict: unknown keys raise `readiness_unknown_key`). A receipt carrying `input_artifacts` would be **rejected**, not accepted. Likewise the arm receipt's own hops carry no artifact digests: `EVIDENCE_ITEM_KEYS` = `{evidence_id, receipt_kind, namespace, path, sha256, schema_version, status}` (`:248`) and `ROW_KEYS` = `{row_id, evaluation_phase, applicability, verdict, predicate_id, evidence_ids}` (`:257`).

`input_artifacts` lives one hop further out, in the **T-0 source record**: `_SOURCE_KEYS` (`joulewise/arm_readiness_evidence_t0.py:163-176`), written by `_source_bytes` (`:1638-1660`), populated for LAUNCH_RECIPE by `_derive_launch(... input_artifacts=(*artifacts, arm_identity, reservation_identity))` (`:1569`) where `artifacts = (manifest_identity, env_identity, chain_identity, arm_identity)` (`:723`), each `{path, sha256}` from `_input_identity` (`:353-355`).

**The good news — the chain IS fully digest-bound, via five hops, and I verified every link:**

| Hop | Mechanism | Evidence |
|---|---|---|
| arm receipt → evidence list | `receipt["evidence"] != evidence_items` ⇒ `readiness_evidence_reference_invalid`; items carry `{path (relative), sha256}` | `arm_readiness.py:4185-4190` (in `_derive_arm_semantics_for_verification`), called from `_verify_arm_receipt:4349` |
| evidence item → receipt bytes | sidecar + `sha256_bytes(raw)` compared, canonical-JSON parse | `arm_readiness.py:2830-2842` |
| receipt → T-0 source | per fact: `_resolve_namespace_path(custody_pack_root, fact["source_path"])`, read, **`sha256_bytes(source_raw) != fact["source_sha256"]` ⇒ `readiness_evidence_digest_mismatch`** | `arm_readiness.py:2869-2887` |
| source → artifact identities | `input_artifacts[] = {path, sha256}`, exact-key validated | `arm_readiness_evidence_t0.py:163-177`, `1652-1657` |
| fact ← source digest authored | `"source_sha256": sha256_bytes(source_raw)` | `arm_readiness_evidence_t0.py:1687-1688` |

Root-anchoring is sound: `source_root = pack_root if namespace == "PACK" else custody_pack_root` (`:2869`), and the consumer already pins `custody_pack_root == receipt_path.parent.parent` (`arm_readiness.py:4844-4849`). The LAUNCH_RECIPE row additionally **cannot** be satisfied from the PACK namespace (`arm_readiness.py:2989-2999`), and `_discover_evidence` is called with `include_pack=False` for arm derivation (`:4143`), so the anchor is necessarily the live custody T-0 source. Duplicate evidence IDs refuse (`:2870-2874`), and adding any file to the evidence namespace post-arm breaks the `receipt["evidence"] == evidence_items` equality — so the anchor set is frozen at arm time.

**Verdict on Finding 1.2's conclusion:** *completability* **CONFIRMED**. *The stated chain* **REFUTED**.

**Why this matters concretely, and it is not pedantry.** §2.1 closes with: "If the implementer finds the evidence-receipt chain is not digest-bound tightly enough to serve as the I1-I3 anchor, that is `NEEDS_RULING`, not improvisation." A fresh round-3 Sol session handed §2.1 verbatim will look for `input_artifacts` on the evidence receipt, will not find it, and will hit exactly that clause — **and the clause's literal reading is satisfied**, so the correct behavior under the ruling is to stop and fire NEEDS_RULING. The ruling therefore ships with a built-in stall at the precise step it was convened to unblock. Alternatively the session improvises against `facts[0].value` (the four booleans) or `derivation.launch_command` — neither of which carries artifact digests — and we get failure 4 of the same family.

This is **Finding 1.3's defect reproduced inside the ruling that diagnoses it**: the adopted text names "reauthenticate against the arm-attested identity" without a correct anchor location. That is the single most important thing the paired lens found.

### F-R2 — **CONFIRMED, with a correction the ruling should absorb: a simpler, contract-native anchor already exists.**

At T-0, `_launch_manifest` reads the manifest from a **fixed root-local path**: `context.custody_pack_root / "arm_readiness.t0.inputs" / "launch-manifest.json"` (`arm_readiness_evidence_t0.py:606`, `_INPUT_DIRECTORY` at `:42`). The consumer already knows `custody_pack_root` (`arm_readiness.py:4844`). So the consumer can derive the canonical manifest path **root-locally, ignoring the caller's `launch_manifest` argument entirely**, exactly as the adopted F2 mechanism prescribes for the lineage locator ("fixed root-local locator, 8-point writer auth, no argv/env" — `docs/decision_log.md:9320`). The digest chain then confirms the bytes; the locator confirms the location. The ruling's table takes only half of this and drops the half that the WO's own adopted mechanism is built on.

---

## Q2 — Sufficiency of the I1–I6 table

I constructed the attacks. Results:

### F-R3 — mix-and-match within one pack, across bracket sessions/attempts: **attack REFUTED (table holds).**
Re-arming requires a changed `arm-context.json` → changed T-0 source bytes → changed `fact.source_sha256` → changed evidence-receipt digest → the *older* arm receipt's `receipt["evidence"] == evidence_items` equality fails (`arm_readiness.py:4185`). Prior arms self-invalidate. Only one LAUNCH_RECIPE evidence receipt can exist (`_evidence_id` is row-deterministic; duplicates refuse). No cross-session mixing survives I1–I3.

### F-R4 — superseded-but-once-attested manifest: **attack REFUTED, and supersession need not be separately checked.**
Arm supersession is checked (`arm_readiness.py:4318-4329`); evidence expiry is checked live at consume time via `now_monotonic_ns=time.monotonic_ns()` (`:4143`). An attacker restoring the once-attested bytes reproduces *the honest context for that arm* — zero gain. I1–I3 are sufficient here.

### F-R5 — **REAL GAP the table does not close: path binding was dropped, and it is load-bearing for downstream durability.**
§2.1's I1 is sha256-only. Delta-2's own `required` text said "…or expected custody input path" (packet 10, F1 cause) — the ruling silently dropped it.

Consequence: a byte-identical manifest at an attacker-chosen path passes I1–I6, and the consumption record then permanently stores that path — `"launch_manifest": manifest_ref` where `manifest_ref = _launch_artifact_reference(launch_manifest)` (`arm_readiness.py:4452`, `4903`). Every downstream consumer reopens **by recorded path**: `_read_exact_launch_reference` (`:4503-4529`) reads `Path(str(reference["path"]))` and refuses `launch_consumption_invalid` if unreadable — used at `verify_consumed_launch:4712` and at lifecycle `:5372`. So an attacker (or merely a sloppy caller) who supplies a copy under a scratch directory produces a **legitimately-consumed window whose lineage becomes unverifiable the moment that copy is deleted**. That is a durable claim-integrity harm reachable *while satisfying all six reconciliations*.

**Amendment A1: add path equality to I1 (and to I2/I3 implicitly, since they derive from the manifest's `window_plan_root`)** — resolved caller path must equal both the attested `input_artifacts[].path` and the root-locally derived canonical path.

### F-R6 — **TOCTOU: REAL, fenced, but the ruling's own contract sentence overclaims past the fence.**
`launch()` sequence (`scripts/launch_window.py:229-247`): assemble → `_consume_launch_capability` → `verify_consumed_launch` → `os.execve(argv[0], argv, dict(os.environ))`. `argv[3]` is `window-chain.zsh`, **opened fresh by zsh after execve**. A same-UID process swapping the chain bytes after the last check and before execve satisfies I1–I6 completely and runs foreign code in the armed window, with a consumption record attesting the honest digest.

This is fenced by the consult's residual R1 ("does not cryptographically prove that every writer's Unix parent is the frozen zsh chain", `consult.md` residual-risk section) and by the registered same-UID limitation (`docs/decision_log.md:9416-9426`). **In scope: no.** But §2.1 states "byte equality with the attested artifacts makes any self-authored or foreign artifact refuse regardless of internal consistency" — unqualified, present tense, about *artifacts*, not about *reconciliation time*. That is the same class of overclaim the ruling's own §2.4 orders cured in the decision log.

**Amendment A2: qualify §2.1 and Disposition 1 with "at reconciliation time", and require the §2.4 doc cure to carry the same qualifier.** A gate that prescribes a de-overclaiming cure must not ship an overclaim.

### F-R7 — **NEW, not in the ruling or any packet report: `window-chain.zsh` content is not content-bound to the frozen pack.**
T-0 attests the chain, but validates its *content* with exactly two regexes: `REPO=` must be the single reviewed repository (`arm_readiness_evidence_t0.py:677-679`) and `^QUARANTINE_ROOT=` must be absent (`:680-681`). Nothing else — no pack-frozen template, no digest against committed bytes (confirmed by exhaustive grep: the only other `window-chain.zsh` references are path constructions in `arm_readiness.py:4471/4733/5372`, `launch_window.py:139`, `capture_t0_step.py:446-465`).

So I1–I3 bind consumption to **the attested chain**, not to **a reviewed chain**. Whoever authored the chain before T-0 determines what the window runs. Disposition 1's honest-contract sentence ("byte-identical to the launch context the arm receipt's T-0 evidence chain attested") is, gratifyingly, *exactly right* about this — but §2.1's "any self-authored … artifact refuses" is true only of artifacts self-authored **after** arming. **Amendment A3: state the pre-arm authoring surface explicitly in the round-3 prompt's contract paragraph**, so the decision-log cure in §2.4 does not re-import the overclaim from a different direction.

### F-R8 — expired/superseded arm receipt as the attack vector: **REFUTED.** `_verify_arm_receipt` checks boot session (`:4295`), monotonic expiry (`:4299`), namespace governance (`:4304-4312`), and semantic supersession (`:4318-4329`) at consume time. `require_unconsumed=False` at `:4816` is deliberate and correct — the atomic no-clobber primary is the linearization point.

### F-R9 — I4 is **redundant, not wrong.** `manifest.boot_session_id` was already checked against the boot session at T-0 (`arm_readiness_evidence_t0.py:620-622`), and `_discover_evidence` pins evidence boot to receipt boot (`:2857-2864`). Once I1 passes, I4 cannot fail. Keep it (cheap), but the round-3 prompt should not present it as independent assurance.

**Net Q2 verdict: the I1–I6 table is sufficient against the delta-2 attack family, with one real omission (A1/path binding) and two contract-language overclaims (A2, A3). No attack survives a correctly-anchored, path-bound I1–I3 within the fenced threat model.**

---

## Q3 — Refusal-code mapping

### F-R10 — `launch_binding_mismatch` is **CONTRACT-CORRECT, and the ruling under-cites its own authority.**
The ruling quotes the consult's terser row ("…pack, HEAD, boot, arm context, **recipe**, roots, or argv", `consult.md:195`). The **registered D-078 spelling** in the adopted amendment is far more direct: `launch_binding_mismatch` — "authenticated records disagree on pack, plan, reviewed HEAD, arm context, collection boot, session IDs, roots, **launch recipe bytes**, or exact exec argv" (`docs/decision_log.md:9179-9181`). I1–I3 *are* launch-recipe-bytes disagreement, verbatim. **No new code needs registration.** **Amendment A4: cite `decision_log.md:9179-9181`, not the consult row.**

### F-R11 — **The exception-family hedge is not a contingency; it is a certainty — and the ruling should have pre-decided it instead of deferring a fact it could have checked.**
§2.2: "If exception-family plumbing (ArmReadinessError vs LaunchLineageError) forces a different registered code, `NEEDS_RULING`."

The plumbing **does** force it, deterministically:
- `READINESS_REASON_CODES` (`arm_readiness.py:142-150`) unions STRUCTURE/CUSTODY/GIT/LIFECYCLE/POLICY/IDENTITY/ENVIRONMENT — **it does not include `LAUNCH_LINEAGE_REASON_CODES`** (`:131-141`).
- `ArmReadinessError.__init__` raises `ValueError: unregistered readiness reason code` for anything outside that union (`:707-708`).
- `LaunchLineageError` is a **sibling** of `ArmReadinessError`, both `ValueError` — not a subclass (`:696`, `:723`).
- `_consume_launch_capability` today raises `ArmReadinessError` exclusively; `verify_consumed_launch` raises `LaunchLineageError` exclusively. The ruling's "one shared helper" spans both.

So round 3 hits NEEDS_RULING at bullet one of §2.2 — a guaranteed round-trip, immediately after a standing escalation trigger fired.

**But the answer is already determinate and needs no ruling:** raise `LaunchLineageError("launch_binding_mismatch", …)` from inside the consumer. `main()` in `scripts/launch_window.py:281-292` catches **both** families and renders identical `{"status":"REFUSE","reason_codes":[code]}`. Precedent exists on the same path (`_assemble_launch_inputs` already raises `LaunchLineageError` with `launch_binding_mismatch` at `launch_window.py:100`, `:113-115`, `:125`, `:132`). Blast radius is 4 files: `scripts/launch_window.py:231`, `tests/test_arm_readiness.py:124,529`, `tests/test_launch_window.py` (mocked). `readiness_usage_invalid` stays an `ArmReadinessError` — mixed families in one function are already the norm here.

**Amendment A5: replace the conditional with a decision — "the shared helper raises `LaunchLineageError('launch_binding_mismatch')`; `readiness_usage_invalid` remains `ArmReadinessError`; no new code is registered; both are already handled by `launch_window.main`."**

*Non-blocking note:* the D-078 registration enumerates the boundaries at which these codes are mandatory as "collection, post-hoc reduction, bound derivation, whole-window verdict, extraction, and mint" (`decision_log.md:9161-9164`) — the consumer is not in that list. The existing launcher precedent settles that this is a floor, not a whitelist. Worth one sentence in the round-3 prompt so a literal-minded session doesn't stall on it.

---

## Q4 — Process dispositions

### The strongest version of "the partition is post-hoc"

Finding 1.1 partitions failures 1–2 (caller-identity) from failure 3 (data authentication). Argue against it as hard as it can be argued:

**F3 was never raised as a caller-identity finding.** Its origin (packet 01, F3) is *"standalone consumption is not fully retired"* — a public writer reachable without the ceremony. Round 1 (packet 04, F3) is *"public entrypoint remains reachable and its launcher-context check is forgeable."* Round 2 is *"foreign context consumes."* Under the invariant framing that F3 was actually opened on — **"CONSUMED must be unreachable without the genuine armed launch context"** — all three are one class with three formulations, which is verbatim the standing trigger's language ("another failed formulation"). "Caller identity" vs "data authentication" is a *mechanism* distinction, and mechanism changes at every fix round by construction. If a mechanism change re-partitions the class, **the standing trigger can never fire**, since round N+1 never uses round N's mechanism. That is a trigger-eating pattern, and rule 11 exists because triggers were eaten on 2026-07-26/27.

### F-R12 — **My honest verdict: the partition survives, but the ruling supports it with the wrong evidence.**

Two facts decide it, and the ruling states neither:

1. **The partition is contemporaneous, not post-hoc.** The consult's F1 — "Mutable frame metadata cannot enforce the sole-launcher claim" — was recorded in packet 06, **before** round 2 was implemented and **before** failure 3 existed. A partition drawn in the record ahead of the failure it later explains is by definition not constructed to excuse it. The ruling asserts the pivot "was correct" but never says it was *prior*. That is the load-bearing point and it should be in the text.

2. **The trigger was not eaten — it was over-discharged.** The standing trigger says the next spend after two same-signature rounds is "a CONSULT, not round three." A consult was spent (packets 05/06). A mandatory cold gate was *then* convened after failure 3. The process obligation was met twice. So the live question is not "may we skip escalation" but "may the cold instance license one more implementation round" — and rule 11 vests exactly that authority in the cold instance. **Disposition 3.3 is CONFIRMED; the partition is CONFIRMED with the above two citations added.**

### F-R13 — **The one process gap the ruling does not see: round 3's formulation is itself unreviewed.**

The consult designed round 2's mechanism, and round 2 failed. The cold gate is now designing round 3's mechanism (the §2.1 table) **single-instance, from a mechanically assembled packet** — and it got the anchor location wrong (F-R1), which is the *same* anchor-underspecification defect it names in Finding 1.3 as failure 3's proximate cause. §3.4's own hygiene rule ("the adopted text must enumerate the *anchor*") is therefore violated by the document that promulgates it.

The cure is cheap and does not need another round-trip: **Amendment A6 — before round 3 launches, the corrected §2.1 anchor must be verified against the code by the prompt author** (I have done so above; the chain, the five hops, and their line numbers are stated). §3.4 should be extended: *the anchor must be cited to file:line and confirmed present at that location*, not merely named. Asserted anchors are how we got here twice.

### F-R14 — Dispositions 3.1 and 3.2: **CONFIRMED.** Fresh Sol at xhigh is right (rule 10: third round, material cost of error). "No quarantine" is right — delta-2 independently confirmed the round-2 deletions held (public name absent, both frame guards gone, honest single-use, replay refusal, null-context refusal). The NDF1/Phase-2 AXI release gate is orthogonal and correctly parked (`decision_log.md:9435-9448`).

### F-R15 — Q4 observations, audited
- **4.1 CONFIRMED** and stronger than stated. `arm_readiness_evidence_t0.py` holds not only the reconciliation semantics but the *only* copy of the attested identities. Verified: nothing in `arm_readiness.py` exposes a source-record resolver — `_discover_evidence` verifies the source digest at `:2869-2887` and then **discards the source content**, returning only receipts. Round 3 must write ~20 lines of resolver. Still completable; but "the exact reconciliation already exists, one module away" is generous — what exists is the *authoring-side* reconciliation, not a reusable consumer-side lookup.
- **4.2 CONFIRMED.** `verify_consumed_launch:4668-4760` binds identity, expiry, argv, and artifact *self*-consistency (`_read_exact_launch_reference:4503`) but never touches attested identities. It is the pre-`execve` gate at `launch_window.py:239-247`. Binding both sites is correct.
- **4.3 CONFIRMED, and it is the sharpest thing in the ruling.** Today a foreign-context call writes the primary at `arm_readiness.py:4925` and irrevocably burns a window Ed armed (`decision_log.md:9128-9130`: "Consumption is irrevocable… absence or any post-claim failure never reopens the capability"). Denial, not stealth, is the cheap attack. The no-burn assertions are claim-bearing. Placing the reconciliation before `consumption_dir.mkdir` (`:4918`, not "~4940") gives genuine zero-filesystem-effect — verified feasible: `_verify_arm_receipt` and the whole evidence chain are read-only.
- **4.4 CONFIRMED.**

### F-R16 — Citation drift (tightening, not a finding)
The ruling's line numbers run ~20–25 lines high throughout: `_verify_arm_receipt` call is **4816**, not 4838; the self-comparison is **4876**, not 4862–4890; the `mkdir` is **4918**, not ~4940; `_consume_launch_capability` starts at **4764**. For a bar advertised as *mechanically verifiable by a fresh delta*, the citations must resolve on first `sed`. Delta-3 will be checking against these.

---

## Amendments (consolidated)

- **A0 (blocking the round-3 prompt).** Correct §2.1's Anchor column to the real five-hop chain: *arm receipt `evidence[]` item for the LAUNCH_RECIPE evidence_id (path `arm_readiness.evidence/<name>` relative to `custody_pack_root`, digest-pinned by `receipt["evidence"] == evidence_items`, `arm_readiness.py:4185`) → evidence receipt (sidecar + sha verified, `:2830-2842`) → `facts[0].source_path` / `source_sha256` resolved against `custody_pack_root` (`:2869-2887`) → T-0 source record → `input_artifacts[] = {path, sha256}` (`arm_readiness_evidence_t0.py:163-177`, `1652-1657`, authored `:723`/`:1569`).* State explicitly that `input_artifacts` is **not** on the evidence receipt and that the resolution root is `custody_pack_root`, never `pack_root`, for this row.
- **A1.** Add path binding to I1: caller's resolved manifest path must equal the attested `input_artifacts[].path` **and** the root-locally derived `custody_pack_root/arm_readiness.t0.inputs/launch-manifest.json` (`arm_readiness_evidence_t0.py:606`, `:42`). Rationale: the consumption record stores the caller's path and downstream reopens *by that path* (`:4503-4529`, `:4712`, `:5372`) — digest-only I1 permits a durable lineage-fragility harm. This restores a check delta-2 named and the ruling dropped.
- **A2.** Qualify §2.1 and Disposition 1 with "at reconciliation time"; carry the qualifier into the §2.4 decision-log cure. The exec-time chain swap (`launch_window.py:247`) is fenced by consult R1 but is not refuted by I1–I6.
- **A3.** Add to the honest-contract paragraph: `window-chain.zsh` content is validated only for the reviewed `REPO=` and absence of `QUARANTINE_ROOT=` (`arm_readiness_evidence_t0.py:677-681`) — I1–I3 bind to *the attested* chain, not to *a reviewed* chain.
- **A4.** Cite `docs/decision_log.md:9179-9181` ("launch recipe bytes") as the code authority, not the consult's terser row.
- **A5.** Convert §2.2's exception-family hedge from `NEEDS_RULING` to a decision: shared helper raises `LaunchLineageError("launch_binding_mismatch")`; `readiness_usage_invalid` stays `ArmReadinessError`; no new registration; both handled by `launch_window.main:281-292`. The two vocabularies are disjoint (`:131-150`) and the classes are siblings (`:696`, `:723`) — this is determinate, and leaving it conditional guarantees a stall.
- **A6.** Extend §3.4: a consult or gate that mandates reauthentication must cite the anchor **to file:line and confirm it resolves there**. Asserted-but-unverified anchors caused failure 3 and recurred in this ruling.
- **A7.** Add to §2.1: the anchor selection must be deterministic — exactly one evidence receipt satisfying `t0.single_launch_capability`; zero or more than one refuses `launch_binding_mismatch`. (Uniqueness holds today via row-deterministic `_evidence_id` + duplicate refusal, but the consumer must not rely on it silently.)
- **A8.** Add a discriminating regression **R6 (path substitution):** byte-identical manifest supplied from a non-canonical path → refuses `launch_binding_mismatch`, no side effect, capability not burned. This is the A1 check's kill test; without it A1 is decorative.
- **A9.** Add to §2.3's held-property battery: an **honest end-to-end launcher pass post-fix**, to prove I1–I3 do not break the real ceremony (nothing writes `window.env`/`window-chain.zsh` between T-0 and launch today, but that is an assumption the battery should pin).
- **A10.** Fix the line citations throughout (F-R16).
- **A11 (record).** Add to Finding 1.1/Disposition 3.3 the two facts that actually carry the partition: the caller-identity/data-authentication pivot is recorded in the consult **before** failure 3 (so it is contemporaneous, not post-hoc), and the standing trigger was discharged **twice** (consult after failure 2, cold gate after failure 3) — so licensing round 3 is an exercise of rule-11 cold-instance authority, not a bypass. Also record the counter-argument explicitly: F3's origin framing (packet 01: "standalone consumption is not fully retired") is invariant-level, under which all three failures are one class — and note the general hazard that mechanism-level re-partition, applied without a prior-record test, would render the standing trigger unfireable.

## Position

**CONCUR-WITH-AMENDMENTS** (A0–A11).

Every load-bearing conclusion of the ruling survives adversarial trace: `ADOPT_PRIVATE_REQUIRED_CONTEXT_API` is structurally sound; the round-2 gap is a completable implementation defect, not a design failure; the attested identities genuinely exist and are genuinely digest-bound; one further implementation round to a fresh instance is licensed; no quarantine; no stage re-scope; the escalation path was operated correctly. The I1–I6 table, once path-bound (A1), defeats every attack I could construct inside the fenced threat model.

**A0 and A5 are blocking on the round-3 prompt, not on the ruling.** As written, §2.1's anchor is schema-impossible and §2.2's hedge is a guaranteed stall — a fresh session obeying the text lands in `NEEDS_RULING` twice before it writes a line. Fixing both is a text edit, not another round. I do not dissent, because the ruling's *reasoning* is right and its *conclusion* is right; but the gate must not ship a prescription containing the very defect it diagnosed, and Finding 1.3 is the reason it must be caught here rather than by delta-3.
