# Harvest lane: what must land in the desk checkout after the seal and before ALPHA-1's harvest

Authority: the seal gate's stage-1 ruling (`~/night-archive/gate-prune/seal-gate/RULING_STAGE1.md`, "The harvest
lane" and items K-4 to K-7), the orchestrator's ruling on the seal-landing review (`../seal-land/ORCHESTRATOR_RULING.md`)
and cold pass 5. The lane changes `joulewise/b5/harvest.py`, `joulewise/whole_window.py` (the replay's authenticity
pass and `_derived_neg8_decision` only), `scripts/harvest_b5_window.py`, their tests and fixtures, and nothing the
chain or the members execute. It lands in a desk checkout only; the measurement clone stays at the seal commit plus
pin-only commits. It is pinned by an addendum to the seal record (files, SHA-256s, the desk checkout's commit) before
ALPHA-1's harvest runs. It gets an independent executing review and a cold Fable pass (claim-path code).

| Item | What | Source |
|---|---|---|
| K-4 | a reference that succeeded but whose energy cannot be read is lost (`energy_unreadable`), by the writer's own predicate; the replay's authenticity pass reproduces a no-energy entry; survivors re-screen | judge RF-1 |
| K-5 | malformed-flag candidates limited to codes a program writing before the harvest can emit (`PRE_HARVEST_CODES`, held equal to those writers' tables by a test) | judge RF-3 |
| K-6 | `contention.unmeasured`, `battery.unmeasured`, `env.member_quiet_state_violated`, `battery.capture_pair_failed` lose a reference | judge RF-5 |
| K-7 | `harvest.json` and `exclusions.json` record the harvest checkout's commit | judge SG-8, SG-11 |
| H-8 | a differing code file in `driver_checkout` is a difference (`code.executed_differs_from_sealed`) | review F1 |
| H-9 | `record_only` becomes a positive list in the harvest's head comparison | review F2 |
| H-10 | an inventory with no `head` is `code.identity_unmeasured` | review F3 |
| H-11 | `errors="replace"` when decoding changed paths | review F6 |
| H-12 | a commit confined to another claim pack's directory is recorded, not a difference | cold pass 5, C6 |
| H-13 | the stale clause in the harvest docstring (`model.identity_underivable` is in the catalog, EXCLUDE_MEMBER) | reg-prep note, cold pass 5 |

Tests the judge's stage 2 will look for: a synthetic window for each of RF-1 (a succeeded reference with no
envelope), RF-3 (a line torn inside `calibration.capt`) and RF-5 (a journal gap over one reference), with the ruled
outcome; `git diff --name-only H_claim..<lane head>` lists only the permitted files.

Also for this lane's design, from the judge's finding 11 (not ruled): the corpus rule keeps corpus members whose
physics is unmeasured; consider consistent treatment with RF-5 before GAMMA-1.

Related, not this lane: lane L9-NEG8 (one survivor logic for every claim consumer, `../l9/L9NEG8_DESIGN.md`) and the
rest of lane L9 (analysis code), before any claim.
