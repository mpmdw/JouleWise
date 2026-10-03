Cold ruling, no prior context; judge only from the repository in this directory (JouleWise, detached at b39d7015, PR #460; base 4205713c). Read-only.

Question: the sealed registration `configs/campaigns/g2a_prefill_probe_25g83/registration_block2.md` pins `scripts/gen_g2_phase_d.py` (seal record `docs/process_traces/2026-10-02-design-block2/52-seal-record.md`, sha 69903ae2…). PR #460 changes that file (see `git diff 4205713c b39d7015 -- scripts/gen_g2_phase_d.py`): the generated chain exported G2A_ROOT with the plan-id suffix doubled, so the window's chain would have looked for its bound probe inputs under a nonexistent directory and refused at its input assertions. No window of this block has been armed yet.

Under registration §11 and §12, is this "a fix that only makes code agree with this text" (ordinary gated PR; the first window is armed from H′ = the merged head, and the seal record is extended with the H′ pins, no new seal), or a difference that needs a new seal or an erratum? Consider whether the change can alter any rule in §§3-10, any probe input, id, captured byte or admission other than removing the bogus path.

End with exactly one line: `RULING: EXTEND-SEAL-WITH-H-PRIME` or `RULING: NEW-SEAL-REQUIRED`, preceded by your reasons with file:line citations.
