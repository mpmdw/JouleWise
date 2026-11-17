# Fresh read-only review and builder disposition — 2026-11-16 PST

Repository `docs/orchestration.md` requires fresh reviewer separation; the repository AGENTS instructions authorize useful multi-agent work under the same safety rules. One read-only Codex peer (`/root/review_drafts`) reviewed the generated qualification/F0 items, gates, generator and tests against the owning rulings. A second turn reviewed the corrected deltas. The peer wrote no files and contacted no hardware or real measurement/custody data. Primary builder owns final diff review, verification, Git actions and every response to the advice; no admission or hardware authority was delegated.

| Finding | Disposition by primary builder |
|---|---|
| P1: stripping UTC from every non-campaign F0 basename could reuse a fixed `r1-partc-f0.ok`, and invented an F0-marker requirement absent from item346 | Fixed. Campaign `.ok`/`.air.ok` remains. Non-campaign latest Check/copy proof must bind exact EFF_PATH and EFF_EPOCH, with an explicit record pointer. Added stale-epoch and wrong-receipt refusal cases under both shells; no F0 marker is assumed. RL-171 §6.1 / RL-173 A. |
| First predecessor confirmation appeared in every item | Fixed: only qual01-s01 invites lead confirmation of dev-05-s02/latest campaign identity. Later chain entries are fixed. |
| Renewal inherited “replaces c3f4bacd8” as if current | Fixed: renewal supersedes item346 at expiry; earlier pin carry history explicitly historical. |
| STATUS overstated OPEN Q1 as blocking default dates; copy input table implied universal marker | Fixed wording: Q1 is needed only to loosen conservative shared-date handling. Q2 remains a default issue/arm prerequisite; input table allows exact non-campaign Check/copy proof. |

Peer delta conclusion: “no remaining blocking bug”; it checked corrected copy binding, all-launched-roster counting, 24-leg/two-block cap, earliest-block-start 10 h reading, same-block s02, predecessor/renewal wording and repeated pinned checklist calls. Primary verified the two final wording corrections against that advice. These findings are process evidence, not independent cold-seat ADMIT, CI equality, freeze2 proof or live hardware validation.

The first synthetic gate run exposed six test-fixture failures: exact-24 cases for each s02 forgot the predecessor's six same-date legs. The implementation correctly refused 30 legs. Builder fixed the fixture's residual count, retained all-launched-leg counting, and re-ran the final checks. This was not a production gate relaxation.
