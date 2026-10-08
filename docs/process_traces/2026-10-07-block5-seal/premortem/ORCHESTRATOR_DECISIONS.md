# Orchestrator's decisions on the pre-mortem's questions (2026-10-07 22:55 PDT)

Source: `PREMORTEM.md` (55 findings; 25 verified, all confirmed; none refuted) and its questions O-1 to O-11.

- **O-1. Hold H_claim for the full Linux matrix: yes.** The CI lane (`../ci/NOTES.md`, branch
  `lane/2026-10-07-ci-linux-fixes`) must show every shard and both exclusive jobs green, or name each remaining
  failure as test-side, before the head is frozen.
- **O-2. The watchdog changes M2 and PD-3: not before the freeze.** They are optional, they touch
  `scripts/magistrate_watchdog.py`, and the watchdog runs from the canonical root, never the clone. They go to the
  first desk session after ALPHA-1, landing on main. Until then the cure is operational: the account that will last
  is logged in and a headless mail test passes before the stop ref is deleted (runbook A9).
- **O-3. `docs/process/NIGHT_HANDBACK.md` and the relaunch prompt are rewritten in a documents commit BEFORE
  H_claim** (lane `lane/2026-10-07-prefreeze-docs`), so the clone, checked out at the seal commit, holds them.
- **O-4. The harvest lane is to be pinned before the arm** (lane `lane/2026-10-07-harvest-lane`, launched; its
  executing review and cold Fable pass must pass). Then the brief's "harvest at once" variant applies: the
  magistrate harvests ALPHA-1 right after its window and arms BETA. If the lane has not passed when everything
  else is ready, the arm does not wait for it: the "hold for the desk session" variant applies to ALPHA-1 only.
- **O-5. ALPHA-1 is the measurement** of this machine's contention; no separate quiet census first.
- **O-6. The desk root** is its own clone at the harvest lane's head, at `/Users/edr/night-custody/desk/b5-harvest`.
  The orchestrator writes the addendum (files, SHA-256s, the desk clone's commit).
- **O-7. What may be opened before the release event.** The magistrate: `harvest.json` (the verdict, `claim_usable`,
  the window reasons), `derived/code-identity.json`, `night/hazard_result.json`. A consult seat may also read the
  monitor's contention journal. Nobody opens `derived/flags.jsonl`, `derived/exclusions.json` or
  `derived/window_flags.json` (judge's SG-12).
- **O-8. Issues #416 and #421 stay open**; they are Ed's directives. The RUN_STATE sentences carry the evidence.
- **O-9. The scratch rigs under `/private/tmp` (`reh1`, `reh2`, `reh3`, `dd5-isreview`, about 259 GiB) are
  deleted** (done 22:52; their records are in `~/night-archive/gate-prune/rehearsal-r1`, `-r2` and
  `rehearsal-real`). Free disk is re-read before the release; the runbook requires 170 GiB.
- **O-10. No GAMMA rehearsal before the seal.** The risk is recorded: GAMMA's verdict writer has never run on real
  bundles with a valid closing calibration, and the writer is the clone's program. ALPHA-1 and BETA-1 exercise the
  writer's passing path on real data first; what is specific to GAMMA is the midpoint at the arm boundary and the
  two diagnostic references, covered by tests on synthetic bundles only. A rehearsal that could yield a valid
  calibration needs a quiet machine for about two hours, which is the first window's slot. If ALPHA-1 or BETA-1
  shows a writer defect, the cure and a re-issued seal come before GAMMA.
- **O-11. The permission sentences for headless seats name block-1 programs.** A suspicion from a lens, untested.
  The orchestrator does not edit permission settings on a subagent's report. It is put to Ed.

Questions that are Ed's (E-1 to E-6 of `PREMORTEM.md`) are put to him in the session and in the `/exit` email.

Clock note: this session's log labels in `WAVE.md` between 21:21 and 22:50 PDT were estimates and run up to about
half an hour ahead of the machine's clock. Labels from here on are read from `date`.
