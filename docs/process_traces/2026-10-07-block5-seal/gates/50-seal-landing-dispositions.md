# Orchestrator's ruling on the seal-landing lane and its review (2026-10-07 22:50 PDT)

**The procedure of `SEAL_LANDING.md` is accepted** and the lane is merged into the integration branch at
`9395cecfbc40fb93e87a7657ec0ba5da0ca9ef3a`. The independent executing review (`REVIEW.md`: every one-byte change to a
window input still excludes, in 16 cases; every permitted commit raises no flag; the procedure is internally
consistent and reproducible) and the Fable delta cold pass 5 (PASS WITH NOTES) both hold the lane's briefed change
sound. The lane's wider "still caught" scope (all of `configs/` and the runbook) is accepted.

Rulings on the review's findings. None changes a window input before the head is frozen: each finding's check lives
in the harvest, which runs after a window from a desk checkout, and the judge has already ruled that a harvest lane
lands there after the seal and before ALPHA-1's harvest.

| Finding | Ruling |
|---|---|
| F1 (MAJOR): a driver checkout whose code files differ from the sealed code raises no flag | **Harvest lane, item H-8, before ALPHA-1's harvest**: the harvest's `code_identity` treats a differing code file in `driver_checkout` as a difference (`code.executed_differs_from_sealed`, already in the catalog and the allowlist) and replays the two checkout checks on its porcelain; identical bytes stay a record. Unreachable when the runbook is followed (the launch agent is installed from the measurement clone). The registration states both: the agent is installed from the clone, and a differing driver checkout is a difference decided at the harvest. |
| F2 (MINOR): `record_only` is "every path not listed" | **Harvest lane, H-9**: the harvest's head comparison makes `record_only` a positive list (`docs/` except the runbook, `tests/`, dot-directories, root `*.md`); every other path is a window input. Unreachable in the registered sequence (the pin advance is the only committer in the clone and refuses anything but the pin). The arm collector compares a head with itself in production, so it does not need the change before the head is frozen. |
| F3 (MINOR): an inventory with `files` and no `head` is compared with nothing | **Harvest lane, H-10**: a missing sealed head is `code.identity_unmeasured`. The seal itself is covered by the landing test. |
| F4: later commits to the registration or plan are silent | By the accepted procedure: the seal record binds them. |
| F5: a re-harvest after a re-issued seal needs the inventory in force at that window's arm | Runbook and magistrate brief. |
| F6: a changed path that is not UTF-8 faults the harvest | Harvest lane, H-11 (one line). |
| F7: draft labels are part of the sealed bytes of three window inputs | `identity_pins.json` and `sizing_b5.json` keep their generators' `status` and `sealed` fields (no code reads them; the registration says the seal record's digest seals them). The catalog's status note is rewritten BEFORE H_claim to a sentence that is true before and after the seal: the file is frozen at the code head of block 5 and is sealed when the seal record of registration section 12 exists and pins its SHA-256. |
| F8: the commit after the seal commit must carry the test fixtures the seal commit forces | Accepted: the record commit carries them, and the suite and CI are required green at the record commit (the pull request's head), not at the seal commit alone. |
| F9: the harvest archive records nothing about the harvest program | The judge's K-7. |

Cold pass 5's defect (a commit confined to another claim pack's directory flags a window that never read it):
harvest lane, H-12, flag-not-refuse, as the pass itself disposed.
