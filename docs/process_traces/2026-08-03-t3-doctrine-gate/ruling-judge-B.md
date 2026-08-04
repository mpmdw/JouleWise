# Cold judge ruling B — SEALED verbatim from thread transcript

Thread session: cf8bca73-2a52-4c42-ad13-098485c3ed2a (t3 fresh Fable thread; transcript sha256 1dbe7e5a174e81f2295b5a700f4e82dc793001eb32daa5e1fc226078591da2e0;
harvested from ~/.claude/projects/ by the lead at seal time).
Kickoff paste path per Ed: one desktop, one phone (dual-path probe; marker: phone-paste).
Sealed before synthesis and before the refuter returned, per charter §5.

---

All verification is complete. I have everything needed to rule. This final message is the complete, self-contained ruling.

---

# COLD-GATE RULING — T3 Code control-plane doctrine packet

**Gate:** rule-11 trigger #4 (proposed process rule) · **Packet:** `docs/process_traces/2026-08-03-t3-doctrine-gate/PACKET.md` (FROZEN 2026-08-03 ~22:45 PT) · **Judge:** cold Fable instance, 2026-08-03 · **Charter:** `docs/process/coldgate_charter.md` v2

## 0. Preflight verification record (completed before reading any merits)

| Artifact | Expected sha256 (supplied at launch, independent of packet) | Observed | Method |
|---|---|---|---|
| Charter | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | identical | `shasum -a 256` |
| Packet | `1f027d0714f0669a63405c9e245ad2e98f78034bd6608b4130084593e173b616` | identical | `shasum -a 256` |

All six manifest exhibits recomputed with `shasum -a 256`; all six observed digests identical to the packet manifest (`charter-consult-record.md` a2a087a4…, `final-message-1f59-7ec.md` 756bc851…, `final-message-2511-742.md` 3ed20243…, `final-message-710c-75d.md` d303eaf2…, `rollout-pins.txt` 77dcf6c0…, `runstate-t3-block.md` 2d1f6fb6…). Trust-anchor cross-check: the registry (`docs/process/coldgate_charter_registry.md`) pins the same charter digest and the same frozen-packet digest supplied at launch. No mismatch; the gate proceeds.

## 1. Contamination disclosure (mandatory candor; also the basis of finding B1)

This judge was launched in the **main checkout**. Before any adjudication act, the session harness auto-injected: the repo `CLAUDE.md`, the full `CLAUDE.local.md` rule-11 operating doctrine, the user-global `CLAUDE.md`, and the session-memory index — material squarely inside charter §4's forbidden class. I could not refuse delivery; it preceded my first action. Mitigation applied: no conclusion below rests on any injected content; every load-bearing claim is cited to the packet, a scoped exhibit, a cited authority, or evidence I recomputed myself. I additionally verified E1's probe claim is self-consistent with the cure: the packet records `CLAUDE.local.md` ABSENT in all worktrees (E1 lines 68–69). This leak is a BLOCKER-tier finding on the convening machinery (B1, §4 below), not on any question's text.

## 2. Evidence I personally verified

- **E1 fidelity:** the exhibit body (7,328 bytes) is a byte-exact contiguous substring of `git show e3612f5:RUN_STATE.md` (mechanical substring check; no other portion of that document was read). e3612f5 is Ed-authored, 2026-08-03 21:34:49 -0700.
- **E7:** commit `97d6e3d` exists — Ed R, 2026-08-03 21:28:33 -0700, RUN_STATE.md only, 107 insertions, pushed (in main history).
- **E9:** commit `14c9f05` exists — Ed R, 2026-08-03 22:04:47 -0700; its 10-line diff carries exactly the packet's claims (post-hoc notification finding, 22:04:04→22:04:04, corrected prior inference, legibility hazard, capability matrix TODO).
- **E10:** `~/t3-supervised-probe.txt` — mtime `2026-08-03 22:27:34`, content `22:27:34`, verified by `stat`/read on this machine. Send/tap times remain Ed-reported (admissible operator observation per E10's own model-blindness finding, which I credit: the probe thread's self-report contradicted observable blocking, so thread-side reports are rightly inadmissible on approval semantics).
- **E8/E5:** the native rollout `…019fcb0b-710c-75d2…jsonl` recomputes to `7ffe06b2…` (matches the E5 pin); its `session_meta` carries `originator: "t3code_desktop"`, `cwd /Users/edr/code/JouleWise`, `cli_version 0.146.0` — exactly as the packet states. The two wrapper-route rollouts (`16b03d03…`, `f22e48da…`) and the E6 consult rollout (`87f36e68…`) all recompute to their pins and all carry `originator: "codex_cli_rs"` — the discriminator discriminates, verified live on all four transcripts.
- **Cited authorities:** D-080 (`docs/decision_log.md:4917` ff.) and bridge protocol §4 (task-shape routing) / §6 (lease events incl. `owner_kind`) read directly.

## 3. Verdicts (per atomic question)

**Q1a — AFFIRM.** Prohibiting "Full access" is conservative and correct regardless of the exact flag mapping (E1 records live process-table confirmation of the bypass-flag mapping; I could not re-verify it, but the prohibition is safe even if the mapping were imprecise). Supervised/Auto-only is affirmed **with finding M4**: E9 (commit-verified) establishes Auto-mode phone cards are post-hoc notifications and Auto self-approved a sandbox-disabled write; the ratified doctrine split (Supervised gates, Auto notifies, anything needing Ed's eyes uses Supervised) must carry the corollary that an Auto-mode card is never citable as approval evidence in any record, and the E9 capability-profile matrix should be filled before Auto is relied on for anything operator-facing.

**Q1b — AFFIRM.** Manifest-recorded PIDs verified by start-time + ancestry, no pattern kills. Sound on its face given the shared process table of sibling threads (E1); no contrary evidence.

**Q1c — AFFIRM.** Text matches Sol's independently exhibited design positions verbatim in substance (E2 §2: stop writers, capture manifest/diff, record, re-baseline; "A checkpoint must never be cited as D-064 evidence"; E2 Disagreements: "A T3 checkmark is not a valid envelope"). Both instruments converge; no dissent exists on this point.

**Q1d — AFFIRM.** Matches E2 §5 ("Native T3 Codex sibling: supplemental exploratory/design lens only… does not satisfy a cold gate, mandatory rotating lens, final-head review, or merge license") and E2 Disagreements ("does not become gate-bearing merely because Ed can see more of it"). The ingestion-note requirement is the right consumption discipline.

**Q1e — AFFIRM**, with NIT N2: E2 recommended the route-(b) conditional default be **piloted for two arcs with recorded calibration** (Fable overhead/value, wrapper failures, latency, whether Ed used the activity view) and counted as a subagent invocation under D-080 accounting, not silently deduplicated. The order text is consistent with E2's scoping (background/parallel rounds only); carry the calibration duty and the D-080-counting rule into the amendment text.

**Q2 — AFFIRM as a shape**, with MATERIAL conditions (M2). The work-chunk anchor fixes a real defect of pure invocation counting (a sweep landing mid-chunk reviews unconsumed state), and the mechanical backstop counter honors D-080's ratified rationale, which explicitly rejected arguable cadences (`docs/decision_log.md:4954–4963` — "a cadence that can be argued about is a cadence that will be argued away"). Conditions the D-080 amendment must satisfy before the trigger is operative: (1) a numeric backstop threshold (the ratified text has none; D-080's "10" was explicitly provisional); (2) "materially consumed invocation" defined by the existing manifest consumption event, not judgment; (3) the anchor events ("substantial rounds / merge waves / adjudications") enumerated mechanically — "substantial" as bare adjective reintroduces exactly the arguability D-080 rejected; the backstop bounds but does not eliminate that risk.

**Q2b — REFUSE** (packet defect; disagreement with the lead's proposed AFFIRM). Whether the shape unblocks D080-TRIGGER-01 "**as drawn**" requires the drawn text of queue row A52, which is not exhibited, and the queue is a status document I may not go read (charter §4, final paragraph: packet gap → REFUSE, don't go looking). Minimum cure: a one-line verbatim exhibit of row A52 at an immutable revision (admissible — its exact words are the object of this sub-question), resolvable at synthesis without re-convening. I note E1's own ruling text says the "row stays BLOCKED until the D-080 amendment ratifies it" — so on the packet's own evidence the answer is at most "this ratification licenses the amendment, which then unblocks the row," not a direct unblock.

**Q3a — AFFIRM the rule text** (a standing tracked charter replaces operating-doctrine ingestion), **with BLOCKER B1 on the convening machinery**: charter-suppression was not achieved for this very gate (§1 above). The principle is right; the launch procedure does not yet deliver it.

**Q3b — AFFIRM.** External registry trust anchor + launch-time digest independent of the packet + judge-side recompute, fail-closed. Exercised live tonight and it worked (§0). The validator is queued, not built; the registry's interim manual procedure (registry lines 36–38) was followed and suffices until the build — keep the build queued, not optional.

**Q3c — AFFIRM.** Cold judge + cross-model contract-lens refuter, same frozen packet and questions, both outputs sealed before synthesis, refuter charged with falsifying packet/disposition/contract-application (not an unseen ruling), override only by a separately labeled written document citing both sealed outputs, presented to Ed. Matches charter §5; the cross-model topology is supported by E3's conflict-disclosed recommendation (E3 Q4 position).

**Q3d — AFFIRM: ratify the charter text at digest `099de884…`.** I read it in full and operated under it for a real adjudication; it is procedurally sound, neutral in framing, and the E6-recorded v1 seams (bias leakage, missing doctrine, §4 laundering, §5 composition holes, packet-local hash) are demonstrably closed in v2 — the §4 excerpt rule in particular did real work tonight (it structured E1's admissibility and grounded my Q2b refusal). No byte change is required to ratify. **Recommended for v3 (new candidate, new gate, non-blocking to this ratification):** a launch-environment clause — the convening procedure must launch cold instances in an environment verified free of doctrine auto-load, and the judge's ruling must open with a contamination disclosure. Until v3, this requirement should live in the registry's convening procedure (see B1 cure).

**Q3e — AFFIRM the lead's composition rule**, as ratifiable text:

> When a standing Ed effort directive conflicts with a ruled gate composition's stated tier, the Ed directive governs. The deviation is recorded in the gate synthesis with the ruled tier and its reasoning preserved unaltered; a failed or materially degraded round under the capped tier is the recorded datum that justifies a one-off escalation request to Ed. A ruled composition never silently overrides an Ed directive; an Ed directive never silently rewrites the ruled composition record.

Basis: Ed's directives are TIER 1 in the packet's own authority chain; a composition tier inside a ruling is subordinate operator-resource policy. The lead's cited supporting evidence is partly verifiable (the E6 charter consult ran at Sol high and delivered a blocker-grade live catch — the §4 laundering demonstration); the "B1 refuter" instrument is not exhibited (NIT N3) but the disposition is argument, not evidence, and the rule stands without it. Live consequence, to be recorded in this gate's synthesis: R2 spells "Sol xhigh refuter"; under the standing high-only directive this gate's refuter runs at high, deviation recorded.

**Q4 — AFFIRM the compressed shadow cutover**, with conditions on the three open gates (§5) and finding M3. Verified gate evidence: isolated-native-write (E7, commit-verified, small doc-only write, pushed); native-discussion (E4/E8, rollout-verified, ingestion note = the E1 gate-log entry); phone-approval CLEARED on the Supervised cell (E10, probe file verified by me; blocking semantics evidenced by the ~90 s send-to-mtime gap and the observed held readback) with the E9 Auto caveat (commit-verified). E3's exhibited conditions for compressed-cutover soundness are met: rollback = pre-t3 mechanism per route with TUI available (R3 text), and no repo write preceded the isolated-native-write gate — the gate exercise *was* the first write (NIT N4: self-declared on the same commit; acceptable for a small reviewed doc write, but future gate exercises should be predeclared). Sol's dissent is noted per the packet; see M3 on its citation.

**Q5 — AFFIRM.** The discriminator is real and I verified it on all four available transcripts: native t3 session → `originator: "t3code_desktop"`; all wrapper/MCP-route sessions → `originator: "codex_cli_rs"` (same CLI version 0.146.0, so the field, not the version, is the discriminator). Fold into bridge-protocol §4/§6 alongside the existing provenance fields (`owner_kind` etc., §6). NIT N1: `originator` is client-self-reported metadata — the amendment should label it a mechanical evidence-stream discriminator, never an enforcement or authority-bearing field.

## 4. Findings (tiered; severity independent of verdicts)

- **B1 (BLOCKER, convening machinery):** The cold instance was launched in the main checkout and received the full operating doctrine and session memory by harness auto-injection before adjudicating — charter-suppression failed live on the mechanism's first use. **Cure (evidenced by the packet itself):** convene cold instances from a git worktree (`CLAUDE.local.md` provably absent in all worktrees, E1 probe) or an equivalently verified doctrine-free environment with memory/global-instruction loading suppressed; add this to the registry's convening procedure now and to charter v3 at next revision; require a contamination-disclosure line in every cold ruling. Until adopted, "cold" is aspirational and future rulings from contaminated launches invite exactly the laundering challenge charter §4 exists to prevent.
- **M1 (MATERIAL):** Q2b packet defect — A52 row not exhibited (cure named in the verdict).
- **M2 (MATERIAL):** R1's backstop counter has no threshold and its anchor events lack mechanical definitions; conditions listed under Q2 bind the D-080 amendment.
- **M3 (MATERIAL):** The "Sol full-shadow preference" dissent is cited to E3, but E3's exhibited final message contains no full-shadow statement — its recorded position is *conditional* soundness of the compressed story plus corrections. The dissent may exist in the full transcript (pin `f22e48da…`) or the lost-thread recap; the gate record currently attributes to an exhibit words the exhibit does not contain. Cure: extract the dissent's verbatim lines from the pinned rollout into the gate record, or restate the dissent as E3's conditional-soundness position. Not verdict-changing for Q4 (the misattribution overstates, not understates, opposition).
- **M4 (MATERIAL):** Auto-mode semantics corollary under Q1a — Auto cards never citable as approval evidence; capability matrix before operator-facing reliance on Auto.
- **N1–N4 (NIT):** originator field is self-reported (Q5); route-(b) two-arc calibration + D-080 counting duty rides the amendment (Q1e); lead disposition cites an unexhibited "B1 refuter" instrument (Q3e basis); isolated-native-write gate exercise was self-declared on the commit that performed it (Q4).

## 5. Conditions on the three open acceptance gates

1. **checkpoint-restore:** scratch-repo probe with predeclared semantics before any workflow relies on checkpoint/restore; until then order 1c's fences are the operative protection.
2. **app-death recovery:** evaluate the next real quit/relaunch against E3's predeclared criteria verbatim — history/checkpoint, cwd/worktree, provider, permission mode, epoch continuity, no duplicated turn or side effect.
3. **cold-packet-handoff:** this ruling is non-REFUSE on Q3 and on the exact frozen bytes, so the drawn criterion's judge-leg is satisfied once both instrument outputs are sealed. **Recorded disagreement with unconditional clearing:** the handoff mechanics passed, but the suppression leg failed live (B1). I recommend the gate be recorded as cleared **jointly with** adoption of the B1 clean-launch convening requirement; clearing it without that adoption should require the charter §5 written-override path.

## 6. Disagreements with the lead's labeled disposition (explicit, per charter §8)

The lead proposed AFFIRM on all questions. I diverge in two places: **Q2b is REFUSE** (packet defect, curable at synthesis), and my Q3 affirmations carry **B1**, which the disposition did not anticipate and which conditions the cold-packet-handoff clearing. On Q3e I concur with the lead's rule as proposed. Silence elsewhere is concurrence.

Bootstrap note: per packet §7, Ed's declaration authorized digest `099de884…` solely as the procedural candidate and is not treated as ratification evidence here; Q3d is affirmed on the text's merits. Any post-ruling byte change to charter or packet is a new candidate requiring a new gate.

— End of ruling. Read-only conduct confirmed: no file modified, no state-changing command executed.
