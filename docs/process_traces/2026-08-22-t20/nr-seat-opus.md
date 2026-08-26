# NR adjudication — Opus seat (verbatim)

Delivered 2026-08-26 ~01:30. Escaped angle-bracket forms are harness transport artifacts.

---

## Verification pass first — what I re-derived from source, and where the packet is wrong

Read at `7a0631af`: `joulewise/arm_readiness_evidence_t0.py`, `joulewise/arm_readiness.py`, `scripts/capture_t0_step.py`, `scripts/window_status.sh`, `scripts/build_family_marker.py`, `configs/arm_readiness/d117_row_registry_v2.json`, `tests/test_arm_readiness_evidence_t0.py`, `tests/test_capture_t0_step.py`, `env/mac-measurement-lock.txt`, `.claude/settings.local.json`, `docs/contracts/d117_step6_confirmation_table.md`, `docs/decision_log.md` (D-150/150a/150b/151/153), `MAGISTRATE-RULING-O1.md`, `MAGISTRATE-RULING-r3.md`, `v4-plan-ruling-r4draft.md`, `readiness-sitting/VERDICT-PACKET.md`, `ed-s5-mint-decision-2026-08-19.md`, the runbook.

**Four findings that change rulings, none of which are in the packet:**

1. **NR-11 has a SECOND call site.** `scripts/capture_t0_step.py:288-316` (`_verify_terminal_review`) is a byte-duplicate of the evidence collector's parse-and-compare — same regex at `:302`, same `setdefault(...).append(...)` at `:306`, same `trailers.get(name) != [value]` at `:312` — refusing `evidence_author_t0_capture_terminal_review_missing`. It takes `pack_sha256 = readiness.committed_pack_tree_sha256(pack)` (`:367`) and is called from `_load_context` at `:494`, i.e. on **every one of the six `capture_t0_step.py` invocations per window** (`STEP_FILENAMES`, `:59-66`). So the three-pack collision bites at the *first* T-0 capture step of the first window whose pack is not the one the attestation names — before `_derive_terminal_review` is ever reached. The packet's answer-space D names only `arm_readiness_evidence_t0.py:928-944`; a cure landing there alone leaves the transaction dead at capture step 1. This is the "another missed call site" signature.
2. **`.claude/settings.local.json` carries `"Bash(cd /Users/edr/JouleWise-measurement-20260818 && *)"` — a blanket allow.** Choosing `-20260818` as the `_v4` checkout would therefore *suppress* the live permission prompts that D-150(1) chose as the operational form of the mint license. Independent mechanical ground to reject NR-1 branch B.
3. **r4-3 is internally incoherent as written on the freeze span.** `:57-60` says the freeze runs "from attestation through window close", while `:50-53` places the attestation *before* evidence ×3, freeze-0004 ×3 and the mint — four real commits. Under the packet's NR-12 placement B the sentence becomes exactly true. Nobody has flagged this.
4. **The `file-09` probe is not merely unwritten — its third property is unsatisfiable inside the ceremony B-4 defines.** `sol-design.md:260` gives P1/P2/P3 as: live registry reference loads / freeze reference authenticates / **arm semantics cross the registry gate**. I read `generate_dry_run_receipt` (`arm_readiness.py:7204-7290`): it calls `_registry_reference(root)` at `:7232` (P1) and `_load_freeze_reference(...)` at `:7234-7240` (P2), but emits `"evidence": []`, `arm_disposition: "NOT_APPLICABLE"` — no arm semantics, no registry-gate crossing. P3 requires the arm B-4 forbids. Same shape as V-6's recorded consequence at `VERDICT-PACKET.md:117`.

**Corrections to the packet's own claims:**

- NR-11 branch E ("mechanically empty") — **CONFIRMED**, and confirmed at both call sites. `context.pack_sha256` is `committed_pack_tree_sha256(root)` per pack root; three packs are three committed trees are three digests; one message yields a `Pack-Sha256` list of length 1 (passes exactly one pack) or ≥2 (passes none). No message satisfies three.
- Test coverage — **CONFIRMED unexercised**. `tests/test_arm_readiness_evidence_t0.py:329-347` builds a single-pack world (one `pack_sha`, one trailer line). `tests/test_capture_t0_step.py:547-566` tests only the absent-trailer refusal. No test constructs a multi-pack message at either site.
- The marker needs **no** NR-11 change: `arm_readiness.py:10749-10752` synthesises `terminal_review` as `{evidence_kind, head_tree_oid}` only, validated `_family_exact` at `:10230-10239` — pack-agnostic. `validate_terminal_review_head_tree` (`:4216-4226`) is likewise tree-only. Cure surface is exactly the two parsers.
- **The 112 allowlist contains no code, script, test, or doc path** — I enumerated it: 111 `configs/campaigns/**` paths plus `configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json` as the 112th (D-151 c1). This is the constraint that dates every ruling below.
- `-20260813`'s `49dcc49` **is** an ancestor of `7a0631af` (`git merge-base --is-ancestor` passes) — the fast-forward is clean.
- NR-6 branch C's stated cost is **wrong**. `MAGISTRATE-RULING-r3.md:59-66` (B-3) makes the shakedown a non-claim window whose GO receipt *is* the V5 measurement, halting the campaign "BEFORE any claim window" on a bounds violation. Deferring live arm-side U11 to it puts the first live exercise at a **non-claim** T-0, not a claim-bearing one.
- B-3 also supplies the ground the packet never surfaces for NR-6: "a ceremony arm is not free: it burns attempt/session IDs under D-131 cl.4, requires the ED-FIRST T-0 lane, and prepends a supersession link to the claim family's arm chain."

---

# Rulings

**Ten of twelve are zero-code. Only NR-11 and NR-13 require code before the window, and neither has a sound zero-code alternative — I say why at each.**

## NR-11 — RULE D (code cure, both call sites, pre-derivation)

**No zero-code branch exists.** A refuses all three (verified at `:939` / `:312`); B refuses two; C is barred by the freeze span and by the single published head the marker admits (`head_unpublished`, `arm_readiness.py:10917-10922`); E is empty (verified); F drops a mechanism *and* edits `configs/arm_readiness/d117_row_registry_v2.json`, which is not in the 112 — so it is itself a pre-derivation commit, buying nothing.

**Minimal cure.** At `joulewise/arm_readiness_evidence_t0.py:934-944` **and** `scripts/capture_t0_step.py:307-316`, split the comparison:

```python
    expected_exact = {
        "JouleWise-Terminal-Review": "PASS",
        "JouleWise-Terminal-Review-Tree-Oid": <tree>,
    }
    packs = trailers.get("JouleWise-Terminal-Review-Pack-Sha256", [])
    if (
        any(trailers.get(n) != [v] for n, v in expected_exact.items())
        or not packs
        or len(set(packs)) != len(packs)
        or <pack_sha256> not in packs
    ):
        raise <same _refuse call, same reason code>
```

`PASS` and `Tree-Oid` keep exactly-one semantics. `Pack-Sha256` becomes **non-empty, duplicate-free, containing this pack's digest**. Duplicate-free rather than bare membership keeps the trailer block a countable enumeration of the reviewed family (one line per pack) instead of an open set, and blocks a degenerate repeated line.

**Registry cost: zero.** Both sites keep their existing reason codes; `capture_t0_step.py`'s frozen `CAPTURE_REASON_CODES` (`:83-97`) is untouched. Only the message strings change, and messages are not vocabulary.

**Regressions** (`tests/test_arm_readiness_evidence_t0.py`, `tests/test_capture_t0_step.py`), defect-shaped, at both sites: (a) three-pack message → all three packs pass; (b) foreign digest not in the list → refuse; (c) duplicate line → refuse; (d) existing single-pack case unchanged; (e) trailing-token/comment line invisible to `fullmatch` → refuse (the packet's own assembly finding, currently untested).

**Producer edit.** `docs/phase_2/window_runbook.md:815-846`: the §5C block loops the three `$PACK_ROOT`s and emits three `-m "JouleWise-Terminal-Review-Pack-Sha256: $SHA"` lines. `:843-846` ("trailers from an ancestor do not transfer") stands unchanged. `docs/process/rehearsal-operator-card.md:30` is a `_v3` single-pack literal — mark it `_v3`-historical, do not update.

**D-151 fixed-point implications** — the load-bearing part:

1. The cure touches `joulewise/`, `scripts/`, `tests/`, `docs/`. **None is in the 112.** The changed-set window opens at the evidence-derivation head (D-153 A6), so the cure MUST land before `EVIDENCE_DERIVATION_HEAD` — in practice before Phase C1. Landing it later makes every arm refuse on residue.
2. **The forbidden repair is the tempting one.** Allowlisting `arm_readiness_evidence_t0.py` or the two test modules to let the cure land mid-transaction is precisely D-151 condition 7's fixed-point tripwire, and dies on the identical impossibility theorem that killed Option 1: a test-source path's final bytes are post-derivation, so no digest condition can be pre-committed. It routes to V-1(vii)'s derived manifest, not to an amendment lane. Write this into the runbook so no bench operator reaches for it under time pressure.
3. No ruled number is amended: the allowlist stays at 112 (D-151 c1).
4. The cure is digest-independent, so it belongs in the pre-derivation candidate by D-153 A2's own logic, and the published-head suite stays green.

**Strongest losing-side argument.** Membership weakens the binding from "this commit reviewed *this* pack" to "this commit reviewed a set containing this pack": an attestation could enumerate a pack that was never actually reviewed, and no gate catches it. Under a threat model admitting a careless producer, per-pack heads (C) preserve the strict binding. **Why it loses:** D-139 A1 rules the in-process adversary out; the residual is drift/bug, which duplicate-free enumeration plus exactly-once `Tree-Oid` still catches. The property being given up — "the message names exactly this pack and no other" — is made physically impossible by a three-pack family at one frozen head, which is a ruled fact, not a choice.

## NR-12 — RULE B (attestation is the LAST commit before publication), owner = MAGISTRATE

Placement A refuses at arm time: the expected `Tree-Oid` is `context.head_tree_oid` (`:936`, from `reviewed["head_tree_oid"]` at `:1929`), and under A the tree moves three more times (evidence, freeze, mint) after the attestation. `window_runbook.md:843-846` says so in terms. C is dominated — the first attestation would be dead trailers on a commit inside the freeze span with no consumer.

**Independent ground the packet does not give:** r4-3's own freeze-span sentence (`:57-60`, "commit-freeze … from attestation through window close") is *false under r4-3's own placement*, because r4-3 then schedules four more commits. Under B it is exactly true.

**Mechanical consequence chain.** New step **C11** after C10.3: at the mint tree, clean status, compute `TREE_OID` and the three `PACK_SHA256`s, one `git commit --allow-empty --cleanup=verbatim` with `PASS` + `Tree-Oid` + three `Pack-Sha256` lines. Resulting head = **`ATTESTATION_HEAD`**, and:

- `PINSET_MINT_HEAD` remains the **allowlist-contract closure head** (D-153 A6) and the coordinate `hS` is computed from. `hS` is unchanged by an empty commit.
- `ATTESTATION_HEAD` is the **published head**. The runbook's Phase D sentence "`PINSET_MINT_HEAD` is now the published head, and it is also the window-close head" is edited to name `ATTESTATION_HEAD`; closure head ≠ published head, and every step naming "the head" says which.
- C10.3's closure diff endpoint becomes `EVIDENCE_DERIVATION_HEAD..ATTESTATION_HEAD`. Identical set — an empty commit adds no paths — so "exactly 112" holds verbatim.
- Marker built at `--head ATTESTATION_HEAD`; `_authenticate_custody_tool`'s `git show {head}:{path}` returns the same blobs.
- Phase F `PUBLISHED_HEAD` = `ATTESTATION_HEAD`, not `PINSET_MINT_HEAD`.
- `validate_r1_evidence_lifecycle`'s `merge-base --is-ancestor` holds (derivation head is an ancestor).
- The freeze span opens at C11 ≈ publication, matching the runbook's "from D1 onward, an ordinary commit to `main` breaks the transaction."

**Owner.** Three texts conflict. D-150b (2026-08-23) post-dates both r4-3 (08-20) and `window_runbook.md` §5C, and delegates "the TERMINAL REVIEW" by name. Rule: **the magistrate performs it.** `window_runbook.md:818-819` survives in its operative half ("not an Ed hardware step") and is amended in its "not delegated" half; `v4-plan-ruling-r4draft.md:50` ("Ed's tree-preserving…") gets an amendment marker.

**Strongest losing-side.** r4-3 is the ORDER ruling and names the derivation head "THE common derivation head"; moving the attestation to the end makes the published head an empty commit that no receipt names as its derivation coordinate, forcing every consumer to carry two heads. **Why it loses:** the gap already exists by design — the changed-set gate is *defined* over `derivation commit .. reviewed HEAD`, so the machinery is built for exactly this — and placement A demonstrably refuses.

## NR-3 — RULE A (amend r4-3 to push-then-build). Zero code.

`arm_readiness.py:10664-10667` sits above every phase branch; `:10917-10922` refuses `head_unpublished`. B needs a forged ref and none exists in the real lane. **Edit:** `v4-plan-ruling-r4draft.md:51-54`, with an appended `AMENDED <date>` marker beneath the original text — never a silent rewrite of a ruling.

**Consequence the runbook does not yet reflect.** A `--phase publication` *verify* requires the confirmation pair: `if phase != "candidate": _authenticate_confirmation_table(...)` (`:10940-10943`), and that raises `confirmation_missing` when the digest is `None` (`:10833-10836`). So Phase E must be reordered to **E1 build → E3 render table → E4 delegated confirmation / compute `hC` → E2 verify → E5 promote.**

**Strongest losing-side.** The written order preserves "nothing is published until the confirmation gates it"; push-then-build makes publication irreversible before the confirmation is executed. **Why it loses:** gate admissibility is conferred by the marker receipt's `gate_admissible` / `publication_authorized` fields (`:11094-11098`) and the verify gate, not by the push. A pushed head with no admissible marker authorizes nothing. Push-then-build reorders a git operation, not the authority.

## NR-2 — RULE A (pull-into-dev → push → fetch-back). Zero code.

Preserves `ed-s5-mint-decision-2026-08-19.md:66` verbatim; the fetch is the minimum ref-moving operation. **Do not enshrine the runbook's `file://` command** — it appears in no source (the packet's paraphrase defect 3). Use the plain local-path form.

- **D1** (development worktree): `git fetch /Users/edr/JouleWise-measurement-20260813 main` then `git push origin FETCH_HEAD:main`.
- **D2** (measurement checkout): `git fetch origin`, then assert four-way equality **by running the predicate itself**, not by eye:
  `.venv/bin/python3 -c "import json,sys;from joulewise.arm_readiness import reviewed_main;print(json.dumps(reviewed_main(sys.argv[1]),indent=2))" <pack_root>` → require `exact_match: true`, `head_commit == ATTESTATION_HEAD`. `_repo_for_pack` (`:3903-3905`) derives the repository from the pack root, so passing a pack root is the non-guessable form and cannot disagree with any downstream gate.

**Freeze-span rule to state explicitly:** a `git fetch` at the measurement checkout is permitted inside the span (it moves only `refs/remotes/origin/main`, creates no commit, and is *required* for four-way equality); a commit, a push, or any move of `refs/heads/main` is not. Later windows need no further fetch; if `origin/main` ever does move, a fetch *reveals* the break rather than causing it.

**Strongest losing-side.** B is one operation instead of three and removes a class of wrong-tree operator error; the `_v3` "never push from it" rule was written for a *branch* mint at a checkout that never had to satisfy four-way equality on `main`. **Why it loses:** the rule's purpose (the measurement checkout consumes refs, never publishes) still holds, the cost of A is one `git fetch`, and B requires amending an Ed-facing decision doc mid-transaction.

## NR-1 (path) — RULE A: `/Users/edr/JouleWise-measurement-20260813`. Zero doc edits.

It is the declared default at `window_runbook.md:28-30`, the `window.env` template literal at `:190-196`, and the §5C producer's `cd` at `:822` — branch A edits nothing. `49dcc49` is a verified ancestor, so `git fetch origin && git merge --ff-only origin/main` on the clean tree is sufficient. B is rejected on three grounds, one of them new and decisive: it is not on `main`; its venv is 20 lines out of lock including `mlx` 0.32.1; and **the blanket `cd /Users/edr/JouleWise-measurement-20260818 && *` allow rule would suppress the D-150(1) live prompts** that are the ruled operational form of the mint license.

**Strongest losing-side (C, fresh checkout).** A fresh clone makes the §1.1 `$BASE` gate ("that head contains none of the `_v4` output") true by construction and eliminates the relock by building from the lock file. **Why it loses on balance:** ~650 MB plus a full MLX venv build against three doc literals and every dated operator path, versus a fast-forward and a relock. **But carry C as the named fallback**: if the relock (below) cannot reach the lock — a plausible failure is `mlx-metal==0.31.2` wheel availability — C becomes the cheaper path, and that must be discovered in the pre-window worklist, not at the bench.

## NR-4 — RULE A: build and verify both `--phase publication`. Zero code.

`build_family_marker.py:24-33` names publication "the strict production rule"; S-5 (`MAGISTRATE-RULING-MARKER.md:94-99`) makes candidate the S-0 accommodation for a condition (tools absent at the pinned head) that does not obtain — the tools are tracked blobs with committed `.sha256` sidecars. Candidate yields `gate_admissible: false`, `publication_authorized: false` (`:11094-11098`) and cannot gate, so a publication verify is required anyway; running candidate first only weakens the tool lane and forces constructing a real `$INPUT` manifest for the marker.

**Do not read this as deleting the manifest step.** Runsheet §1.3's mechanical candidate manifest is still produced at preflight (§1.5) because **C9 consumes it** — each executing custody tool's SHA-256 is compared against the digest the manifest records. Only the *marker* stops consuming it: no `--candidate-manifest` in either invocation.

**Strongest losing-side.** Candidate-then-publication is the shape S-0 rehearsed end to end; repeating it reduces the real lane's novelty. **Why it loses:** in the real lane the candidate build authenticates tools against a manifest instead of committed blobs — strictly weaker — and a cheap dry pass is available anyway by building `--phase publication` to a scratch output path and discarding it.

## NR-13 (scheduling) — RULE A, and EARLIER than the packet says

The packet times it "before the attestation commit opens the freeze span." **That is the wrong gate.** `scripts/window_status.sh` and its regression are not in the 112, so the binding constraint is the **changed-set window, which opens at `EVIDENCE_DERIVATION_HEAD`** (D-153 A6). Land it **before Phase C1**.

**Minimal cure, guard not removal.** A freeze-span sentinel **outside the repository** (transaction custody), path from an env var with a default: when present, the script writes `WINDOW_STATUS.md` and exits 0 *before* `git add` at `:95`, printing "freeze span open: status written locally, not published." Out-of-span behaviour byte-identical. A sentinel at a *repository* path would itself be residue — the reason it must live in custody.

**This answers the packet's B-interaction objection.** D-150a's committed visibility channel is the **push notification to Ed's phone** (runbook §4 table), not the git push; `WINDOW_STATUS.md` is still written locally under the guard, so nothing Ed was promised is withdrawn.

Regression exercises both branches per the kernel row's own acceptance evidence. While closing the row, fix the off-by-two citation (`92-104` → `94-105`) in D-153 W4 and the kernel `status_note`, and reconcile kernel `queued` against `TASK_QUEUE.md:647` `READY [AGENT]`.

**Strongest losing-side.** This is a code change on the critical path for a hazard a one-line operator rule would also close, and pre-window code changes carry their own defect risk. **Why it loses:** the hazard is silent and remote — the script is called by other sessions and crons that never read this runbook — and its consequence is not a stop at a named step but the invalidation of every armed pack for the rest of a seven-day campaign. Ten guarded lines with a two-branch regression against that asymmetry is not close.

## NR-6 — RULE B (dry-run ceremony, no real arm), P1/P2/P3 STRUCK, U11 at the shakedown. Zero code.

Grounds are B-4 plus B-3's cost accounting, not condition 5 (see NR-7): a ceremony arm "burns attempt/session IDs under D-131 cl.4, requires the ED-FIRST T-0 lane, and prepends a supersession link to the claim family's arm chain" (`MAGISTRATE-RULING-r3.md:52-55`). The ED-FIRST clause alone breaks the runbook's "Ed's presence = Phases B+C" budget.

**The probe is struck, not written, because it is unsatisfiable as specified.** P1 and P2 are already executed inside the ceremony's own dry-run — `_registry_reference(root)` at `arm_readiness.py:7232` and `_load_freeze_reference(...)` at `:7234-7240`. P3 ("arm semantics cross the registry gate") requires the arm B-4 forbids; the receipt carries `"evidence": []` and `arm_disposition: "NOT_APPLICABLE"`. Replace the probe with named assertions over the dry-run receipt, per pack: `status: PASS` with `refusals: []` (which entails P1 and P2 — a failure of either surfaces as a refusal at `:7234-7245`); the `same_head_pack_binding` check PASS with `head_binding == ATTESTATION_HEAD`; and `receipt_kind: dry_run` / `mode: dry_run` / `arm_disposition: NOT_APPLICABLE` / `evidence: []` as the positive statement that no arm occurred. Record **P3 as discharged at the shakedown GO receipt**, which B-4 already names as the V4-delta proof point.

Edits: `MAGISTRATE-RULING-r3.md:77`, `v4-plan-ruling-r4draft.md:54`, `docs/process/state_kernel.json:4041`.

**Arm-side U11.** `_run_identity_arm_reverification` is called only from the arm path (`arm_readiness.py:7655`), never from dry-run — so under B the obligation `s0-runsheet-r4.md:2298-2299` assigns to the real transaction is discharged at the **shakedown arm**, which B-3 makes a non-claim window. Name it there explicitly.

**Strongest losing-side.** `s0-runsheet-r4.md:2299` says live arm-side U11 re-verification is "proven by the real transaction in the measurement environment" — the shakedown is a different event, and B leaves the rehearsal's last open caution undischarged in this session while also giving up the empty-refusals arm receipt. **Why it loses:** B-4 already priced exactly that trade and recorded it; and a ceremony arm is not free in the three specific ways B-3 enumerates.

## NR-7 — RULE A with a B-shaped restatement. Zero code.

D-153 A4 amends *the same clause* ("condition 5: residual re-priced"), so A4 governs and the parenthetical "no claim-bearing arm occurs in it" is false of the re-priced interval by construction. But the parenthetical is still **true and load-bearing of a sub-interval**, so re-scope rather than strike. Amend `MAGISTRATE-RULING-O1.md:62-65` (amendment marker, original preserved):

> 5. The residual runs **mint → post-window fixation** (≤ ~8 days worst case, D-153 A4), with the per-phase controls named. Within it: the sub-interval **mint → the first consuming arm** carries no arm of any kind (r4-3 / B-4: dry-run ceremony only); the sub-interval **first consuming arm → post-window fixation** carries the campaign's claim-bearing arms under the published marker and confirmed table, which is the controlled state the residual prices.

Mirror the correction in the D-151 index row at `decision_log.md:175`, which currently renders the parenthetical as the whole clause. `decision_log.md:180` (D-153 A4) needs no edit. ONE home = `MAGISTRATE-RULING-O1.md:62-65`.

**Strongest losing-side.** Letting both stand costs nothing mechanical — no code reads either text — and every edit to an adopted cold-gate ruling is a chance to introduce a new inconsistency. **Why it loses:** the terra seat already used the literal reading of condition 5 as a ground to kill option beta. A clause that has demonstrably driven a real disposition is not inert prose.

## NR-8 — RULE: declare it, mechanically, in one act. Zero code.

- **Triggering fact.** The campaign's member set is fixed at publication by the marker's three members and their plans, so "last" is *determinable from the plan*, not judged.
- **The declaration names both coordinates at once**, resolving the unit mismatch the packet found (A6 says *arm*; the D-153 index row says *window*): (i) the **arm receipt id of the last consuming arm** — closes the changed-set window per A6; (ii) the **completion of that window's consume** — permits the commit-freeze close per A1. A6's normative text governs the unit; the index row is a paraphrase and gets a clarifying edit.
- **Owner: the magistrate**, under D-150b's own boundary. Comparing the executed arm set against the published campaign plan is a mechanical comparison — exactly the delegated class. What stays Ed's is **stopping early**: if the executed set does *not* equal the planned set, declaring the campaign complete is judgment-bearing and is Ed's ruling.
- **The record, in this order** (the trap is real): declaration transcript in transaction custody (no commit) → freeze close declared → D-150a "campaign done, freeze OFF" notification → **the fixation commit, which is the FIRST commit and carries exactly the `hS` literal plus its loud-fail guard (D-153 A1)** → only then `RUN_STATE.md`, `WINDOW_STATUS.md`, the decision-log row, and everything else. A `RUN_STATE` header update written before fixation would take the fixation commit's ruled slot.

Home: runbook §Phase H + §6.

**Strongest losing-side.** Naming a declaring act adds ceremony to something that will be obvious in practice. **Why it loses:** the fixation commit's content is ruled to the byte and its position is "first commit after"; with no declared close, the first commit after the last window is whatever a stray script writes — the NR-13 hazard wearing a different hat.

## NR-10 — RULE A (six ruled prompts) + a prompt inventory that makes the count exact. Zero code.

Verified harness state: `.claude/settings.local.json` allows `Bash(python3 scripts/*)` and `Bash(.venv/bin/python3 scripts/*)` — both **relative-form** patterns — plus the `-20260818` blanket. There is **no rule for `-20260813`**. So whether a command prompts is a function of *invocation form*, which the magistrate controls, not of the ruling.

**Rule the invocation form:** every transaction command is issued with the Bash working directory already at the measurement checkout, in bare relative form (`.venv/bin/python3 scripts/…`), so the existing relative allow rules apply and the only prompts Ed sees are the six classifier-blocked freeze/projection commands. `cd /Users/edr/JouleWise-measurement-20260813 && …` matches nothing and prompts. Note the spelling trap: the allow rule names `.venv/bin/python3` while the runbook Phase A says `.venv/bin/python` — same interpreter, different string, different outcome. Free fix: use the spelling the rule names.

**Pre-window prompt inventory** (magistrate, read-only): enumerate every command in Phases A–H, predict prompt/no-prompt against the effective allow list, and where prediction is uncertain, run a harmless `--help` variant *of the same spelling in the same cwd* and observe. Deliverable is a table Ed sees before he sits down, with the exact count and the exact strings. Do **not** take branch C: D-150 declined a standing settings rule in terms, and adding one needs Ed's hands anyway.

**Strongest losing-side.** If the classifier blocks a Phase D/E command, the operator hits an unwarned prompt after Ed has left — Ed's presence is Phases B+C only. **Why it loses:** that is precisely what the inventory removes, and any residual is a stop, not a corruption; §5's abort semantics already cover it.

## NR-9 part 3 (cadence) — NOT the magistrate's to rule; default-and-confirm

D-150a records it as Ed's pending preference. Recommended default, framed so it costs Ed one word: **batched to phase boundaries, immediate ping on mismatch.** Concretely, the step-6 execution record is appended to the Phase D3 notification rather than sent as its own ping (under NR-3=A the confirmation lands ~20 minutes after publication, so a separate ping is noise); any digest mismatch pings immediately, per D-150b's "Ed pinged on mismatch." Mechanically null — nothing in code consumes the notification. Edit on Ed's word: runbook §4 table, Phase E4 row, replacing "*(Cadence pending — NR-9.)*".

---

# OPERATOR-FIX items — exact entries

## 1. Venv relock at `/Users/edr/JouleWise-measurement-20260813` (ED's hands; `pip` in a measurement environment)

The lock header (`env/mac-measurement-lock.txt:5-7`) names the constraints form, but **constraints alone will not do this job**: the checkout has 13 packages *newer* than the pin and 3 the lock names that are *absent*, and `-c` neither downgrades an installed package nor installs one nothing requires. Use the requirements form:

```
cd /Users/edr/JouleWise-measurement-20260813
.venv/bin/python3 -m pip install -r env/mac-measurement-lock.txt
.venv/bin/python3 -m pip install -e ".[mac]" --no-deps
```

Second line reinstates the editable package without letting resolution re-drift the pinned set.

## 2. Verification of the relock (MAGISTRATE, read-only, transcript into transaction custody)

```
cd /Users/edr/JouleWise-measurement-20260813
.venv/bin/python3 -m pip freeze --exclude-editable | sort > /tmp/have.txt
grep -v '^#' env/mac-measurement-lock.txt | grep -v '^[[:space:]]*$' | sort > /tmp/want.txt
diff /tmp/want.txt /tmp/have.txt        # MUST be empty
.venv/bin/python3 -c "import mlx, mlx_lm, transformers, sys; print(sys.version.split()[0], mlx.__version__, mlx_lm.__version__, transformers.__version__)"
# MUST print: 3.13.1 0.31.2 0.31.3 5.12.1
```

Acceptance is the empty diff, not the three version strings — the drift is 22 lines, not one package (the packet's paraphrase defect 1). **If `mlx-metal==0.31.2` or any pinned wheel cannot be obtained, stop and fall back to NR-1 branch C** rather than accepting partial lock; this is the one discovery that changes the checkout ruling, which is why it runs early.

**Provenance rationale to carry into the runbook** (nothing refuses on drift): `identity_pins.py:291-318` stamps `runtime_version` into every projection receipt, and `scripts/make_figures.py:552` hardcodes "MLX 0.31.2 / mlx-lm 0.31.3" in the figure metadata. An out-of-lock U11 run passes both runsheet guards, hashes identical weight bytes, and silently publishes receipts whose runtime contradicts the paper's caption.

## 3. Contract sentence edit — `docs/contracts/d117_step6_confirmation_table.md`

Inside D-150b's bounds, verified admissible with zero code change: `arm_readiness.py:10404-10415` requires `confirmation` to be exact-key `{authority, decision, statement}` with `authority == "ED"`, `decision == "YES"`, and `statement` any **non-empty string**.

**Replace `:37-41`** ("The table contains no self-digest… publication promotes the same bytes without mutation.") with:

> The table contains no self-digest and no timestamp. Event time belongs in the immutable transaction transcript. The producer renders the final bytes including the literal proposed `YES` and computes `hC` over them.
>
> **Under D-150b (Ed, 2026-08-23) the exact-byte confirmation is a STANDING DELEGATION to the magistrate.** The confirming party independently recomputes every digest the table asserts — `hM` from the marker bytes on disk, `hS` from the bytes committed at the mint head — from the artifacts themselves, never from the producing session's report, and only then evaluates equality. `confirmation.authority` remains `"ED"` and `confirmation.decision` remains `"YES"`; `confirmation.statement` records that the confirmation was executed under the D-150b delegation and names what was independently recomputed. Any mismatch is a refusal and a ping to Ed, never a re-render. Ed is notified after execution rather than blocked on it; judgment-bearing publication decisions remain Ed's. Publication promotes the confirmed bytes without mutation.

**Also `:7-8`**, append to the authority sentence: "…and D-150b (delegated execution of the exact-byte confirmation)."

**Also the schema example at `:79`**, replace the `statement` literal with a D-150b-shaped exemplar: `"Confirmed under the D-150b standing delegation: hM recomputed from the marker bytes on disk and hS from the bytes committed at the mint head; both matched the values this table asserts."`

This is a `docs/` commit → not in the 112 → **lands before `EVIDENCE_DERIVATION_HEAD`.**

---

# Minimal ORDERED pre-window worklist

Everything in W-A and W-B is a repository commit and **all of it must be on the reviewed head before Phase C1**, because no code, script, test, or doc path is in the 112.

| # | Work | Owner | Gate |
|---|---|---|---|
| **W-0** | Magistrate ratifies this ruling package (rule 11: the lieutenant may not adopt process rulings alone). NR-9 part 3 goes to Ed as a one-word question. | Magistrate + Ed | — |
| **W-1** | **Ed: venv relock** at `-20260813` + magistrate verification (entries 1–2 above). **Run first**, in parallel with W-A — it is the only item that can force the NR-1 fallback to a fresh checkout. | Ed (10 min) | empty `diff` |
| **W-2 (W-A)** | **One code PR, two commits, full C-028 gauntlet + delta re-audit:** (a) NR-11 cure at *both* call sites + five regressions at each; (b) NR-13 `window_status.sh` custody-sentinel guard + two-branch regression. | Sol impl, Opus/Sol refuters, magistrate final verification | CI green by `conclusion` field |
| **W-3 (W-B)** | **One docs PR:** step-6 contract prose (entry 3); r4-3 order amendment (NR-3) and attestation-placement/owner amendment (NR-12); `window_runbook.md` §5C three-pack producer + owner; condition-5 re-scoping in `MAGISTRATE-RULING-O1.md` + `decision_log.md:175` (NR-7); ceremony redefinition in `MAGISTRATE-RULING-r3.md:77` / `v4-plan-ruling-r4draft.md:54` / `state_kernel.json:4041` (NR-6); NR-8 declaring-act procedure into runbook §H/§6; runbook Phase D/E reorder (E1→E3→E4→E2→E5) and Phase D published-head rename; NR-1/NR-2/NR-4/NR-10 rulings recorded; NR-13 line-number fix; the D-151 c7 "do not allowlist the cure" warning; one decision-log row for the package. | Sol xhigh drafts, magistrate verifies | CI green |
| **W-4** | **Declare the reviewed head** — `gh run view <id> --json conclusion`, never `gh run watch`, never absence of failure lines (errata E-1). | Magistrate | — |
| **W-5** | Fast-forward `-20260813` `main` to the reviewed head; run the four-way predicate; run runsheet §1.1 `$BASE` gate + the 15/15 anchor block against it. | Magistrate | `exact_match: true` |
| **W-6** | **Prompt inventory** (NR-10) — the exact command strings and the exact count, delivered to Ed. | Magistrate | — |
| **W-7** | **Measure the full suite** on a scratch checkout at the reviewed head, serial `unittest discover`. Sole unknown ≥ 45 min in the budget; nothing in custody records it. | Magistrate, background | a number |
| **W-8** | §1.5 preflight: custody root, §1.3 manifest + digest (still needed for C9), custody tools materialised and hashed, registry-v1 literal sweep, disk headroom ≥ several GB, D-150a "transaction open / push freeze ON" notification. | Magistrate | all boxes |

W-1 runs concurrently with W-2/W-3. W-6, W-7, W-8 run concurrently after W-4.

# Earliest-credible window shape

**Ed's total: ~1 h 15 m, in two sittings.** ~10 min for the relock (W-1, any prior day) + one word on cadence, then ~1 h on the night: reboot, then present through Phase C for six permission prompts. He leaves after C10/C11.

**Magistrate:** Phase A the evening before (60–90 min, suite baseline already measured at W-7). On the night: drives C, then D through H alone.

**Night wall clock** (runbook §3 with my rulings applied — NR-6=B removes the arm, NR-3/NR-4 reorder Phase E but do not change its cost):

| | |
|---|---|
| Ed arrives, reboot + boot pin (B) | 10 min |
| Phase C1–C11 incl. C3's MLX freezes and the new C11 attestation | 40–75 min — **Ed present** |
| Ed leaves | ≈ T+60–85 min |
| D publication (push, fetch-back, four-way) | 5–10 min |
| E1 build → E3 table → E4 delegated confirmation → E2 verify → E5 promote | 25–45 min |
| F1–F2 four-way + publication-lane replay | 2–5 min |
| F3 published-head suite | **45–180 min** (start it the moment F1–F2 pass) |
| G dry-run ceremony ×3 (runs against the measurement checkout while F3 runs) | 10–20 min |
| H close-out, custody seal, notifications | 15 min |
| **Total machine time** | **≈ 2.5 – 6 h** |

A 19:00 start puts close-out between ~21:30 and ~01:00, the spread owned entirely by W-7's unmeasured suite.

**Earliest credible date.** The pole is W-2: a two-part code change, gauntleted, refuted, delta-re-audited, CI green. That is one full work block plus CI on a clean first pass; W-3 can be drafted in parallel and merged behind it. With W-1 running concurrently, the realistic earliest transaction night is **two days out — not before 2026-08-28**, and only if W-2 clears review on the first pass. A second fix round on W-2 pushes it a day and, by the standing escalation trigger, a second round with the *same signature* (another missed call site) is a consult, not a round three.

**Hard downstream constraint on choosing the night.** C6 starts the 168-hour clock (D-150(2)); every consuming window must complete within seven days of the evidence commit, and there is no re-author after publication. Pick a transaction night followed by a week whose nights are actually available: clean-nightly finishes ≈ T+74 h, full-weather ≈ T+146 h, leaving ~22 h of margin in the bad case. Do not start the transaction into a week with two or more unusable nights.

---

**One adjacent item, flagged not ruled, outside my twelve:** `VERDICT-PACKET.md:117` records V-5 — B-3's **mechanical** halt-trigger gate in the window scheduler (T-0→arm ≤ 15 min, p99 arm→consume ≤ 4 min, "prose halt triggers are how stop signals get eaten") — as "**absent from `scripts/` and `joulewise/`** — executed". I found `arm_to_consume_budget_ns` enforcement at `arm_readiness.py:602/4554` but no scheduler-side pre-authorization bound check, and I did not chase it to a conclusion. It gates the shakedown→next-window transition, not this transaction, so it does not belong on the pre-window worklist — but it should be checked before the shakedown, and the check is cheap.
