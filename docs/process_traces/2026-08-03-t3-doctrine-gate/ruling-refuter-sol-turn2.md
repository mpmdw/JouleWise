Preflight

Packet expected/observed SHA-256: `1f027d0714f0669a63405c9e245ad2e98f78034bd6608b4130084593e173b616`. Charter expected/observed SHA-256: `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`. Method: `shasum -a 256`. All six exhibit hashes and three rollout pins matched; extracted finals matched their transcripts byte-for-byte; E8’s originator was confirmed; E7 and E9 existed with matching diff descriptions.

Verdicts

Q1a — REFUSE. The Full-access-to-bypass-flags mapping lacks primary argv, transcript, or version-bound probe evidence (`PACKET.md:35-37`; `docs/process/coldgate_charter.md:108-112`).

Q1b — AFFIRM. The proposed prohibition is supported by the repository’s explicit ban on sandbox and approval bypass flags (`PACKET.md:38-39`; `AGENTS.md`, Bidirectional Agent Bridge).

Q1c — REJECT. Re-baselining after a revert must resolve active leases and begin under a fresh invocation and lease (`PACKET.md:40-43`; `docs/contracts/bridge_protocol.md:347-370`).

Q1d — REJECT. Material native-output consumption requires a tracked ingestion event binding session identity, output digest, disposition, and process trace (`PACKET.md:44-46`; `docs/decision_log.md:3328-3347`).

Q1e — REJECT. The proposition overgeneralizes a conditional route and omits the two-arc pilot qualification (`PACKET.md:47-49`; `inputs/final-message-2511-742.md:35-48`).

Q2 — REJECT. The replacement trigger is not mechanically fireable and removes D-080’s explicit invocation and phase-boundary cadence without defining an equivalent threshold (`PACKET.md:51-53`; `docs/decision_log.md:4949-4963`).

Q2b — REFUSE. D080-TRIGGER-01’s exact text, acceptance criteria, and dependency edges are absent from the packet (`PACKET.md:54-55`; `docs/process/coldgate_charter.md:64-66`).

Q3a — AFFIRM. The standing Ed effort directive is controlling authority (`PACKET.md:58-60`).

Q3b — AFFIRM. A gate tier is a default unless expressly marked mandatory (`PACKET.md:61-63`).

Q3c — AFFIRM. The controlling directive and effective tier must be recorded at launch and synthesis (`PACKET.md:64-66`).

Q3d — AFFIRM. An expressly mandatory conflicting tier requires prospective Ed resolution before launch or consumption (`PACKET.md:67-70`).

Q3e — REJECT. The packet presents an open question rather than exact atomic ratification text, and a failed capped round is not a prerequisite to requesting an authority ruling (`PACKET.md:71-74`).

Q4 — REJECT. TUI availability must exclude claim-bearing `[QUIET-MAC]` work, which requires an ordinary guarded shell and zero active agent sessions (`PACKET.md:76-79`; `AGENTS.md:60-65`).

Q5 — REJECT. `originator` is not established as a stable, exhaustive routing contract and must remain only a recorded hint corroborated by authoritative launch-route fields (`PACKET.md:81-84`; `docs/contracts/bridge_protocol.md:223-234,304-323`).

Findings

Tier mapping: prior P1 = BLOCKER; prior P2 = MATERIAL. There were no NIT findings.

- BLOCKER — Refuse claims relying on the inadmissible E1 excerpt. E1 gives no exact original line range and uses narrative gate/probe assertions as factual evidence; proposition-specific excerpts and non-narrative primary artifacts are required (`PACKET.md:98-103`; `docs/process/coldgate_charter.md:58-62`).

- BLOCKER — Supply primary evidence for the Full access mapping. No argv capture, transcript, or version-bound probe establishes that T3 Full access maps to the named bypass flags (`PACKET.md:35-37`; `docs/process/coldgate_charter.md:108-112`).

- BLOCKER — Resolve active leases before re-baselining reverts. Release or abandon active leases and start a fresh invocation and governing lease before re-baselining (`PACKET.md:40-43`; `docs/contracts/bridge_protocol.md:347-370`).

- MATERIAL — Bind native ingestion to tracked consumption evidence. The event must record session identity, output digest, disposition, and tracked process trace (`PACKET.md:44-46`; `docs/decision_log.md:3328-3347`).

- MATERIAL — Preserve conditional routing and pilot qualification. Narrow the rule to background or parallel work needing phone-visible lifecycle and retain the two-arc pilot (`PACKET.md:47-49`; `inputs/final-message-2511-742.md:35-48`).

- BLOCKER — Define one mechanical trigger before replacing D-080. “Work chunk,” “substantial,” and “materially consumed” are undefined, and the backstop counter has no threshold (`PACKET.md:51-53`; `docs/decision_log.md:4949-4963`).

- BLOCKER — Include D080-TRIGGER-01 before ruling Q2b. Supply an immutable bounded copy containing its exact text, acceptance criteria, and dependency edges (`PACKET.md:54-55`; `docs/process/coldgate_charter.md:64-66`).

- BLOCKER — Present exact Q3e text instead of an open question. The current wording asks reviewers to invent governing authority and recording requirements rather than ratify an atomic proposition (`PACKET.md:71-74`).

- BLOCKER — Qualify TUI availability outside quiet-machine work. Claim-bearing quiet runs require an ordinary guarded shell with zero agent sessions (`PACKET.md:76-79`; `AGENTS.md:60-65`).

- BLOCKER — Keep the isolated-native-write gate open. Commit `97d6e3d` does not prove native T3 authorship, governed ceremony, or review/push verification; E8 began after the commit and produced only a readiness message (`PACKET.md:155-158`; artifact `97d6e3d`: commit metadata/diff; artifact `E8`: session timing/final message).

- BLOCKER — Keep the phone-approval gate open. E9 is a narrative assertion from one Auto probe, while E10 lacks custody-listed transcript/stat/timestamp evidence and reports a write about 11 seconds before the tap (`PACKET.md:159-167`; artifact `E9`: commit narrative; artifact `E10`: reported write/tap timestamps).

- BLOCKER — Predeclare pass criteria for the open cutover gates. Checkpoint restore, app death, and cold handoff lack complete immutable clearance criteria (`PACKET.md:171-178`).

- BLOCKER — Do not use originator as the sole session discriminator. The three rollout samples do not establish a stable or exhaustive enum, ownership, unknown-value behavior, versioning, or fallback (`PACKET.md:81-84`; `docs/contracts/bridge_protocol.md:223-234,304-323`).

Disposition disagreements

I depart from the lead’s blanket AFFIRM. I concur only on Q1b and Q3a–Q3d; I REFUSE Q1a and Q2b, and REJECT Q1c, Q1d, Q1e, Q2, Q3e, Q4, and Q5. I also reject the lead’s proposed Q3e failed-round prerequisite: a failed capped round is not required before requesting Ed’s prospective ruling on an expressly mandatory tier conflict.

Q3e ratifiable text

“A standing Ed effort directive controls. A gate tier is a default unless expressly marked mandatory; record the directive and effective tier at launch and in synthesis. If an expressly mandatory tier conflicts, do not launch or consume the instrument until Ed prospectively rules; a failed capped round is not required before requesting that ruling.”

Acceptance-gate conditions

- Isolated native write: provide route-bound native-session and manifest evidence tied to the commit, including governed ceremony and review/push verification.

- Phone approval: provide a custody-pinned harness event and filesystem timeline proving that Supervised execution waited for approval; do not infer a categorical Supervised/Auto split from one narrative probe.

- Checkpoint restore: predeclare and capture scratch-repository before/after state, lease-safe rebaseline behavior, revert criteria, and idempotence.

- App death: predeclare and capture history, cwd/worktree, provider, mode, epoch, and proof of no duplicate side effect.

- Cold handoff: require digest validation, both sealed outputs, no protocol failure, and an explicit disposition of refuter disagreement.

- Quiet-machine cutover: keep TUI activity outside `[QUIET-MAC]`; run claim-bearing measurements from an ordinary guarded shell with zero active agent sessions.

BRIDGE_REPORT_V1
{"status":"DONE","summary":"Reissued the unchanged cold-gate contract-lens refutation with charged finding tiers and the required bridge-report/v1 trailer.","pathspec":[],"verification":["shasum -a 256 for packet and charter","validated all six exhibit hashes","validated three rollout pins","compared extracted finals byte-for-byte with transcripts","confirmed E8 originator","confirmed E7 and E9 existence and matching diff descriptions"],"flags":["resend_for_envelope"]}