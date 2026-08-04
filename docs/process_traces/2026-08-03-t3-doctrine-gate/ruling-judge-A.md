# Cold judge ruling A — SEALED verbatim from thread transcript

Thread session: 10cd3a80-7004-4b85-b567-a212f7348503 (t3 fresh Fable thread; transcript sha256 5a0bab47dc2074cb475489211c7d560089d7e5d4875c965ad42c7ef806be95f6;
harvested from ~/.claude/projects/ by the lead at seal time).
Kickoff paste path per Ed: one desktop, one phone (dual-path probe; marker: desktop-paste).
Sealed before synthesis and before the refuter returned, per charter §5.

---

All verification is complete. I have everything needed to rule; no further tool use. What follows is the complete ruling, written as the permanent gate artifact.

---

# COLD-GATE RULING — T3 Code control-plane doctrine packet (rule-11 trigger #4)

Cold adjudication instance, convened 2026-08-03/04, ruling under `docs/process/coldgate_charter.md` v2. This message is the complete, self-contained gate record of this instrument.

## 0. Preflight digest record (performed before reading any merits)

Method for all digests: `shasum -a 256` executed by this instance on the gate machine.

| Object | Expected (operator-supplied, independent of packet) | Observed | Result |
|---|---|---|---|
| Charter `docs/process/coldgate_charter.md` | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | same | MATCH |
| Packet `PACKET.md` | `1f027d0714f0669a63405c9e245ad2e98f78034bd6608b4130084593e173b616` | same | MATCH |

All six manifest exhibits recomputed and matched: `charter-consult-record.md` (`a2a087a4…`), `final-message-1f59-7ec.md` (`756bc851…`), `final-message-2511-742.md` (`3ed20243…`), `final-message-710c-75d.md` (`d303eaf2…`), `rollout-pins.txt` (`77dcf6c0…`), `runstate-t3-block.md` (`2d1f6fb6…`). The operator-supplied expected charter digest also matches the registry's operative row (`docs/process/coldgate_charter_registry.md:16`). No mismatches; the gate proceeds.

## 1. MANDATORY DISCLOSURE — suppression failure in this convening (BLOCKER)

The charter states (§ preamble) that the operating doctrine "is deliberately withheld from you." **It was not.** My launch context contained, via harness auto-injection: the project `CLAUDE.local.md` (the full rule 1–11 doctrine — the exact document R2's charter-suppression is designed to replace, per E1 line "standing tracked hash-pinned charter replaces `CLAUDE.local.md` ingestion"), the global and project `CLAUDE.md`, and the project's auto-memory index (session memory — a class charter §4 expressly forbids). This happened because the instance was launched in the main checkout; the E1 probe log itself records the cure direction ("CLAUDE.local.md ABSENT in all worktrees — doctrine provably main-checkout-only"), and the path-keyed memory directory would likewise not load from a worktree.

I did not consult any of that material for any ruling below; every load-bearing conclusion cites packet exhibits or primary evidence I verified myself, and per charter §9 I do not lose standing — I rule on the merits. But the defect is structural, it manifested in the mechanism's first live use, and it is dispositive for how Q3a and the cold-packet-handoff gate should be treated (see below).

## 2. Evidence personally verified (beyond the manifest)

- **E1 fidelity:** the excerpt body is byte-verbatim contained in `RUN_STATE.md` at `e3612f5` (mechanical containment check; no other content of that file was read). Block boundaries confirmed contiguous: preceded by the stream-state script line, followed by the next checkpoint heading — no evidence of internal elision.
- **E7:** commit `97d6e3d` exists (2026-08-03 21:28:33 −0700, `RUN_STATE.md`, +107/−6) and is an ancestor of `origin/main` (pushed). **E9:** commit `14c9f05` exists (22:04:47, +10/−1) and is on `origin/main`; its added lines match the packet's E9 characterization faithfully, including "PHONE CARDS ARE POST-HOC NOTIFICATIONS, NOT GATES," "a tapped card ≠ an approval," and the correction of the prior session's "permission prompts functioning" inference.
- **E10:** `~/t3-supervised-probe.txt` — mtime `2026-08-03 22:27:34`, content `22:27:34`, verified by `stat`/read on this machine. The Ed-reported send (~22:26) and tap (~22:27:45) times are operator testimony recorded at freeze; the filesystem half corroborates.
- **E5/E8:** all four rollout transcripts (three pinned in E5 plus the E6 consult rollout) recomputed against their pins — all match. The E8 rollout's `session_meta` carries `originator: "t3code_desktop"`, `cli_version: "0.146.0"`, `cwd: /Users/edr/code/JouleWise` — all as claimed.
- **Q5 discriminator, independently extended:** all three wrapper-route rollouts (MCP design consult `019fcac1`, night-plan review `019fcafc`, charter consult `019fcb1a`) carry `originator: "codex_cli_rs"` — the field genuinely discriminates native-desktop from wrapped sessions on tonight's evidence.
- **Registry and packet custody:** working tree clean for charter, registry, and packet directory; the packet is git-tracked from `6448bc0` through freeze at `a4bec94`.

## 3. Verdicts

### Q1 — Operating orders

**Q1a — AFFIRM.** "Full access" prohibition is supported by the live flag-mapping confirmation (E1) and, independently, by E9/E10: if even Auto self-approves a sandbox-disabled home-dir write, a bypass-permissions mode has no place in this repo. **MATERIAL finding:** the bare ratified text "Supervised/Auto only" does not itself carry the semantics that make it safe. The ratification must bind, as doctrine and not merely gate-log history: (i) Auto-mode phone cards are post-hoc notifications, never consent (E9); (ii) the model is blind to the approval layer, so thread-side reports are inadmissible as evidence of approval semantics — operator observation plus filesystem timestamps only (E10); (iii) anything requiring Ed's eyes uses a Supervised thread. Without these, the corrected "permission prompts functioning" inference will be re-derived by some future session from the same misleading UI.

**Q1b — AFFIRM.** Manifest-recorded-PID-only kills with start-time + ancestry verification, justified by the shared process table across sibling threads (E1). No findings.

**Q1c — AFFIRM.** Checkpoint-revert fencing, checkpoint-ref-never-evidence, checkmark-never-envelope — each independently grounded in the design record (E2 §2 and its Disagreements: "T3 revert is a human/control-plane mutation… stop writers, capture manifest/diff, record, rebaseline"; "Hidden checkpoint refs are not audit evidence"; "A T3 checkmark is not a valid envelope"). The rule fences checkpoint semantics rather than depending on them, so the still-open checkpoint-restore gate does not block ratification. No findings.

**Q1d — AFFIRM.** Native-thread authority ceiling matches E2 §5 ("supplemental exploratory/design lens only… does not satisfy a cold gate") and E2's disagreement that visibility confers gate-bearing status. Consistency note: this gate running in a fresh t3 *Claude* thread does not collide with 1d, which governs native *Codex* threads; E2 §5 expressly blesses a sealed-packet fresh Claude sibling for cold gates. No findings.

**Q1e — AFFIRM.** Subagent routing for substantial *background* Sol rounds matches E2 §1's route-(b) scoping (background/parallel, not every substantial call; thin dispatch steward, no adjudication authority). **NIT:** the ratification should carry E2's two provisos verbatim — the wrapper invocation counts as a subagent invocation under D-080 accounting ("do not silently deduplicate"), and the conditional default is piloted for two arcs with usage/overhead recorded.

### Q2 — R1 cadence

**Q2 — AFFIRM** the work-chunk-anchored shape with mechanical backstop. Anchoring fresh-eyes sweeps to consumption of substantial rounds / merge waves / adjudications matches what a sweep is *for* (reviewing consumed work), and the backstop prevents starvation on long quiet stretches. **MATERIAL finding:** the proposed text is not yet operative rule text — the backstop counter has no numeric threshold, and "substantial" and "materially consumed" are undefined in the ratified words. The D-080 amendment must fix the number and both definitions; until then the shape is ratified but nothing can mechanically fire.

**Q2b — REFUSE.** Defect: the packet supplies no exhibit of D080-TRIGGER-01 / queue row A52 "as drawn," and D-080 is not cited by immutable revision and exact location (charter §7). The source is a queue/status document in the charter §4 forbidden class, and §4 directs me to declare the packet defect rather than go looking. Minimum cure: a §4-compliant bounded verbatim excerpt of the A52 row and the controlling D-080 entry (or the drafted amendment text itself), cited by revision, in a follow-up packet or the synthesis round. **This is an explicit disagreement with the lead's proposed AFFIRM-on-all.**

### Q3 — R2 cold-gate mechanism

**Q3a — AFFIRM the mechanism text, with a BLOCKER finding on its implementation.** The principle — a standing tracked charter replaces operating-doctrine ingestion — is consult-endorsed (E6, Sol agreeing with R2's core architecture) and correct. But as §1 above discloses, "replaces ingestion" addressed only the operator-handover channel; the harness auto-injection channel defeated suppression in this very convening. **BLOCKER / minimum cure:** the convening procedure must require launching cold instances from a doctrine-free environment — a worktree (where `CLAUDE.local.md` is provably absent per the E1 probe and the path-keyed memory directory does not load) or an equivalently scrubbed context — plus a standing judge-side duty to disclose any doctrine/memory material present at launch. Encode both in the registry's convening/validator spec now (procedure lives outside the hashed charter bytes by design); fold into charter v3 at the next byte-change opportunity.

**Q3b — AFFIRM.** The validation chain was exercised live by this instance and worked end-to-end: operator-supplied expected digest independent of the packet, matching the registry's operative row; judge-side recompute; exhibit-manifest verification; fail-closed rule understood and armed. **NIT:** `scripts/validate_gate_packet.py` remains unbuilt; the interim registry-plus-recompute procedure sufficed tonight, but the build should stay queued, not drift.

**Q3c — AFFIRM.** Cold Fable judge + Sol contract-lens refuter, mutual blindness, sealed verbatim + hash-pinned outputs before synthesis, refuter charged against the packet/disposition/contract-application (not the unseen ruling), override only by a separately labeled written document citing both sealed outputs and presented to Ed. This matches charter §5, the E6 Q4 adoption record, and E3 Q4's topology recommendation (cross-model diversity, with Sol's conflict-of-interest disclosed). No findings.

**Q3d — AFFIRM** the charter text at `099de884…`. I operated under the full text; it is well-drafted — neutral framing, symmetric error control (§2), anti-laundering read-set (§4, which the packet's own restructuring demonstrates has teeth), sealed composition (§5), burden and evidence rules (§7), and verdict-standing rules (§9) are each individually sound and were each load-bearing in this ruling. **MATERIAL finding** (does not require rejecting the current digest): the environment-hygiene requirement and judge disclosure duty from the Q3a blocker belong in the judge-facing bytes eventually — registry convening spec now, charter v3 later; any byte change is a new candidate and a new gate per the bootstrap rule. **NIT:** §4 requires excerpts to state an "exact line range"; E1 identified its block by heading + revision instead. I verified fidelity mechanically, so no harm here — either packets comply literally, or v3 relaxes to "exact mechanical identification sufficient for verbatim verification."

**Q3e — AFFIRM the lead's composition rule, with one addition.** Ed's standing effort directives govern over a ruled composition's stated tier: operator resource authority outranks an implementation detail of a gate ruling, and the record supports capped tiers retaining teeth (E6 — a Sol *high* consult — produced confirmed blocker-grade catches, including the live laundering demonstration against this very packet). My addition, beyond the lead's proposal: the deviation must be recorded in the *gate record itself* and be Ed-visible at application time, not only preserved in synthesis — a quality-floor downgrade must never be discoverable only after the fact. Ratifiable text:

> When a standing Ed effort directive conflicts with a ruled gate composition's stated tier, the directive governs. The gate record and the synthesis must both record the deviation — ruled tier, applied tier, directive cited — preserving the original tier reasoning, visible to Ed. A round that fails, or a refuter that returns no unique catch, under the capped tier is the datum supporting a one-off escalation request to Ed. The lead may not raise or lower a ruled composition tier on its own authority.

### Q4 — R3 compressed cutover

**AFFIRM**, with Sol's full-shadow dissent (E3) duly recorded and the following conditions. The compressed shape is defensible *because* the cutover is confined to the presentation/control plane while the compliance plane is unchanged (E1, Tier-1 directive), and the gate evidence shows the acceptance gates are real, not ceremonial: phone-approval initially **failed** (E1 gate log), was refined by Ed's timed probe (E9), and cleared only in the Supervised cell with a genuine blocking observation (E10) — a gate that can fail and force doctrine refinement is doing its job. Verified cleared: isolated-native-write (E7, on `origin/main`), native-discussion (E4/E8, ingestion note in the E1 gate-log entry), phone-approval (E10, with the E9 Auto caveat).

Conditions and findings:
- **Cold-packet-handoff:** this ruling returns non-REFUSE on Q3 and on these exact packet bytes, so the criterion *as drawn* is met. However, per the Q3a BLOCKER, the criterion under-tests coldness — it never checks the judge's launch environment. My recommendation: mark the gate **cleared-with-exception** (mechanism validated end-to-end; environment hygiene defect disclosed and cured going forward) or re-run one packet from a clean worktree launch; that disposition is Ed's to make, not mine or the lead's.
- **Open gates stay open:** app-death recovery and checkpoint-restore must run against predeclared criteria (E3 Q2.3's list: history/checkpoint, cwd/worktree, provider, permission mode, epoch continuity, no duplicated turn or side effect). Ratifying the cutover doctrine does not advance either gate.
- **MATERIAL:** the t3 server's `0.0.0.0` binding (LAN-exposed, ticket-auth'd, E1 probe) is an open control-plane exposure during cutover; the Network-access toggle check should be resolved before the cutover is considered settled.
- **MATERIAL:** the E9 capability-profile matrix (mode × provider × blocking-semantics) remains unfilled; until it exists, per-cell approval semantics beyond the two probed cells (Auto, Supervised/Fable) are unverified and must not be assumed.
- **NIT:** the isolated-native-write gate was self-designated — the checkpoint commit *declaring* the gate is the gate exercise (E1: "This checkpoint's commit is the isolated-native-write gate exercise"), which technically satisfies Sol's E3 precondition ("no real repository write before the isolated-native-write gate") only by definitional fiat. The write was doc-only, reviewed, pushed, and verified, so I accept it; future first-writes-as-gates should be predeclared, not retro-designated.

### Q5 — Provenance fold-in

**AFFIRM.** The discriminator is real and I extended its verification beyond the packet: the native t3 rollout carries `originator: "t3code_desktop"` while all three wrapper-route rollouts from the same night (MCP and CLI routes alike) carry `originator: "codex_cli_rs"`. Provisos the §4/§6 amendment text must carry (**MATERIAL** as a set): (i) the field discriminates native-vs-wrapper only — it does *not* distinguish among wrapper routes (MCP vs audited CLI both read `codex_cli_rs`), so it is one field among the four-axis provenance set, necessary but never sufficient; (ii) it is provider-controlled metadata — a provenance signal, never authority or audit evidence; (iii) the observed value set is empirical and pinned to cli 0.146.0 — record values as observed-at-version, and treat unrecognized values as fail-closed unknowns, not as either class.

## 4. Packet hygiene (charter §6)

Above average. Contrary evidence is present and labeled (Sol's R3 dissent, E6's preserved disagreements, the initial phone-approval failure, the E10 model-blindness finding against the assembling side's own instrument class); the lead's views are confined to labeled sections; E1's admissibility limitation is stated in the exhibit itself. Defects, each already attached to its question: the Q2b exhibit gap (→ REFUSE); E9 presented as paraphrase-plus-commit-pointer rather than a fully §4-compliant excerpt (I verified the paraphrase faithful against the commit's added lines — NIT); E1's missing exact line range (NIT).

## 5. Disagreements with the lead's labeled disposition

The lead proposed AFFIRM on all questions. I diverge in three places: **Q2b is REFUSE** (evidence gap, cure named); **Q3a carries a BLOCKER** the disposition did not anticipate (suppression failed via harness auto-injection in this very gate); **Q3e is affirmed with an added Ed-visibility requirement** on deviation records. Everything else concurs, and silence elsewhere is concurrence per charter §8.

## 6. Summary table

| Q | Verdict | Findings |
|---|---|---|
| 1a | AFFIRM | MATERIAL: bind E9/E10 approval semantics into the ratified text |
| 1b | AFFIRM | — |
| 1c | AFFIRM | — |
| 1d | AFFIRM | — |
| 1e | AFFIRM | NIT: carry E2's D-080-counting + two-arc pilot provisos |
| 2 | AFFIRM | MATERIAL: backstop threshold and definitions unset — not yet operative |
| 2b | **REFUSE** | Packet defect: no scoped A52/D-080 exhibit; cure named |
| 3a | AFFIRM | **BLOCKER**: auto-injection defeated suppression this convening; cure named |
| 3b | AFFIRM | NIT: validator unbuilt |
| 3c | AFFIRM | — |
| 3d | AFFIRM | MATERIAL: environment/disclosure duty → registry now, v3 later; NIT: line-range clause |
| 3e | AFFIRM+ | Addition: deviation record Ed-visible in the gate record; text supplied §3 |
| 4 | AFFIRM | Conditions on 3 open gates; MATERIAL: 0.0.0.0 binding, capability matrix; NITs above |
| 5 | AFFIRM | MATERIAL: three provisos bound into the amendment text |

Ruling complete. Per charter §5, this output is to be sealed verbatim and hash-pinned before synthesis alongside the refuter's; I have not seen the refuter's output.
