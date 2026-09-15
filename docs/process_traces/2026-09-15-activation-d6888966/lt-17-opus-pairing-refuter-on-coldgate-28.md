# lt-17 — Opus pairing refuter (contract lens) on cold-gate packet 28, INSTALL-WINDOWS-MULTI-01 round 3

Rule 11 pairing seat. Packet sha `6e0514da…424b35` and charter `099de884…c95d81` recomputed, both match the
convening pins; all eight exhibit digests match the manifest. Code read at `9a7bacdf` in
`/Users/edr/code/JouleWise-wt-coldgate-iw2`, `install_night_agent.sh:250-374` in full. Read-only; probes under
`/tmp/opus-refuter-28/` on the tracked stub seams; no real `launchctl` call at all.

## Independent answers (written before reading the ruling) — 2026-09-15 10:28 PDT (clock read, `date`)

### Executed probes (mine) — `/tmp/opus-refuter-28/probe.py`, subclassing `tests/test_install_night_agent.py`

Under `python3.12`. The 91 inherited tests also ran, **all OK** at `9a7bacdf` — independent confirmation of exhibit B
item 3.

| Probe | Observation |
|---|---|
| **A** — clock advanced past `install_close` *during* `rm -rf "$plist_backup"` (`:374`), via a PATH `rm` shim | `rc=0`, both labels loaded, both plists present, clock 600 s past close, "validated pins:" printed. **F1(a) reproduced.** |
| **B1/B2** — that same `rm` fails (once / always) | `rc=1`; **both labels bootouted, both plists removed**; "validated pins:" already on stdout; **stderr empty**. Last four launchctl calls `bootout,bootout,print,print`. |
| **C** — `--uninstall` with both `bootout`s rc=1, both jobs loaded | `rc=0`, both still loaded, **both plists deleted**, `installed_agent_fence(...) = None`. **F2 reproduced.** |
| **D** — `--uninstall` where only the **dead-man** bootout fails, then a NEXT install (stub modelling launchd EALREADY) | step 1 `rc=0`, dead-man loaded, plists gone. Step 2: the `:294` check **does not fire** (night label only); the run renders, bootstraps night, fails the dead-man, teardown retains both plists, exit **4**. |

B1/B2 make the lieutenant's half of F1 worse than exhibit A states it: the teardown is **silent** — stdout says
`validated pins: …`, and nothing on stderr says the night was just disarmed.

### Q1 — F1 cure: **(a)**, with one required amendment; definition ruled narrowly

(a) — but ruling 10's "in every case `rm -rf "$plist_backup"`" sits inside its `result != 0` branch and reads as
"whichever per-plist branch was taken", so the landed early `return 0` at `:312` is a defensible reading, not defiance.
Dictate the cure as text, with a clause ruling 10 never had: **non-fatal on success**.

> Delete `:374`. Replace `:312` (`(( result != 0 )) || return 0`) with
> `if (( result == 0 )); then rm -rf "$plist_backup" 2>/dev/null; return 0; fi`.
> After the gate at `:372` the only remaining statement is the success `print` at `:373`.

A *fatal* removal on the success path — at `:374` or inside `teardown` — reintroduces B1 exactly. Regressions: (1) clock advance during backup removal → `rc=0`,
both loaded, both plists present, **no backup dir left** (also kills the `:312` survivor, Q5); (2) injected
backup-removal failure after the gate → `rc=0`, both loaded, both plists, zero launchctl calls after the verifications.

**Definition.** Class 1 covers **launchd (machine-state) mutations only**, not every statement before exit: a
`TMPDIR` removal mutates no launchd state, so probe A's end state is the *intended* installed state and `:372` proved
the bound at the last launchd mutation. It gains one companion clause, which is what F1 breaks:

> **After the commit gate, no statement may change the process exit status or fire the EXIT trap.**

F1(a) is then definitional and closes under that clause; F1(b) is a blocker on its own and is not definitional.

### Q2 — F2 scoping: **(i)**, blocks this lane; a scope expansion, not a design change

(1) Probe C is the exact class the lane exists to eliminate, at a site that runs **after every night** (runbook
`:1596-1606`). (2) The cure is the mechanism this round already built and proved for `teardown` (`:317-331`) — bootout
both, re-read `print`, refuse to delete under a loaded label, distinct non-zero exit — ~8 lines plus one cell mirroring
cell 9. (3) Option (ii)'s risk statement **cannot be written truthfully today**: probe D shows the FIX-4 refusal at
`:294` queries the **night label only**, so a stuck dead-man passes it and only launchd's own already-loaded
`bootstrap` failure then prevents a double-arm — modelled in my stub, unverifiable here.

**Not a contract change to exhibit H.** H's "`--uninstall` unchanged" sits in the *label-collision* row as a scope
note — what refuse-if-loaded did not require — not an adjudicated property of uninstall. Verified bootout changes no
invariant, refusal-code set or kernel clause; it adds one non-zero exit to a command whose callers are the runbook
harvest step and tests. **WRITE_SCOPE expansion + an amended scope note**, the magistrate's to grant.

**Addition the packet does not carry (MATERIAL).** The same shape exists again at
`scripts/install_magistrate_watchdog.sh:199-201` (`bootout … || true`, `rm -f "$plist"`, `exit 0`) for the magistrate's
own agent. Whatever lane takes F2 must cover **both** installers.

### Q3 — round 3: justified narrowly; STOP CONDITION

**Justified** under charter §9 only in this shape: round 3 carries **F1 + F2 and nothing else**, as dictated
single-statement changes inside structure proved load-bearing by the isolated reversions (exhibit A); no new
mechanism is invented.

> **STOP CONDITION.** Delta 3 answers same-signature **YES** if, as an *executed* case at the round-3 head, either:
> (class 1) the installer exits 0 with either label loaded while a clock read taken after the commit gate is at or past
> `min(selected_span_close, install_close_epoch)`; or (class 2) any path in `scripts/install_night_agent.sh` ends with a
> label loaded and its plist absent, **or** exits 0 while a label it attempted to bootout is still loaded.
> On YES: **there is no round 4.** The lieutenant launches no fix seat, hands back, and the magistrate convenes the cold
> gate on the restructure question, Ed emailed the same activation. The count is **per class, not per site** — closing
> one site while the class remains open does not reset it. **Decider: the magistrate**, never the lieutenant (rule 11
> reserves "continuing past an escalation trigger").

**Pre-committed outcome on YES: escalate, restructure leading — not "land with the residue."** The residue is
fence-blinding state, letting the magistrate believe nothing is armed while a job is loaded; D-161 keeps fail-closed
for exactly such evidence-bearing classes. "Land with registered lanes" is admissible only once every survivor is
*proved* non-fence-blinding — the proof two deltas have failed to make.

### Q4 — F3/F4: **register, do not fold** (`INSTALLER-SIGNAL-ATOMICITY-01`)

Both pre-existing, both reproduced at `df86cee6` (exhibit A), neither blinds the fence (F3 leaves both jobs unloaded;
F4 nothing loaded, priors intact). F3's honest cure is not one line — signals blocked across the restore loop, or
restore-to-temp-then-rename — so folding it forfeits the justification Q3 rests on, and round 2 showed that widening a
round manufactures the next round's blocker. Cheapest admissible fold: `trap '' INT TERM HUP` around `teardown`'s
restore loop (`:332-338`), with a signal-injected regression.

### Q5 — survivors: **PACKET GAP**; two must die, the rest equivalent or diagnostic

Exhibit A gives **counts only** (8 + 3); no exhibit lists the survivors, so a judge confined to the packet cannot name
them. The enumeration sits outside the packet in `/tmp/magistrate-d6888966/lt-10-delta2.md` (outside-packet
evidence); its table lists **seven** rows while its prose says eight.

- **Must die — `:312` success guard** ("returns 1 not 0"): dies by construction under the Q1 cure if the success
  control asserts no `night-agent-install.*` backup dir survives a successful install.
- **Must die — `:316` `trap - EXIT` removal**: it guards re-entry of the retention `exit 4`. Run it against **cell 9**,
  not the isolated probe, asserting the `:328` diagnostic appears **exactly once**.
- **Diagnostic/equivalent, record only:** `:322`/`:325` flag `1`→`2`; reorderings `:319-320`, `:312-314`, `:314-316`;
  `:316-331` trap relocation (equivalent only because the launchctl block cannot exit). The three `:339` tail survivors
  **dissolve** under the Q1 cure (make `:339` non-fatal too).
- **Independent of Q5:** lt-04's 22-survivor list was never re-run at this head (exhibits A and B); that gap must close
  before landing whatever Q5 is ruled.

### Q6 — the three round-2 rulings

1. **Mutation-oracle replacement — AFFIRM.** The original was unsatisfiable against the adopted Opus amendment (the
   re-read `print`s are necessarily last); the replacement is strictly stronger (nine cells RED vs one). It changes an
   oracle, not an invariant.
2. **`exit 4` not `return 4` — AFFIRM.** The requirement was "a distinct non-zero status"; on zsh 5.9 `return` from an
   EXIT-trap function cannot deliver it (measured twice). `exit 4` inside the trap needs `trap - EXIT` first, and
   `:316` does it. Verb changed, requirement preserved.
3. **Render-only teardown makes zero launchctl calls — AFFIRM; correct contract.** `--render-only` writes to a render
   directory and never bootstraps, so it cannot create the loaded-job-no-plist state; bootouting there only destroys
   state the run did not create — here, an armed night. **And no: the installer must NOT refuse render-only when a
   label is loaded.** `:294` exempts render-only deliberately (a tracked test pins it); refusing would break validating
   a successor plan while a night is armed — the capability this lane delivers. Condition: zero launchctl calls across
   the **whole** render-only run, failure paths included (the F3 regression).

## Pairing refutation of ruling 10 — 2026-09-15 10:33 PDT (clock read)

Read only after the section above was written. **Its probes ran**: `/tmp/coldgate-iw2/probe_q1.py` 10:22,
`probe_q2.py` 10:23, both before the 10:24 ruling. Citations spot-checked, all correct (`tests:849-853, 882-887,
:1026`; code `:317, :321, :324, :329, :334`). **Rule/doctrine amendments attempted: NONE.** It stays inside exhibit E
(Q1 = E's Q3 step 1), F (Q2 reuses the re-read / refuse-to-delete amendment) and H (uninstall = scope note); D-161:
both new refusals fail closed on an evidence-bearing class.

**Q1 — AFFIRM + AMEND (MATERIAL).** Same cure and definition I reached independently; its warning line betters mine.
But it rules the definition without stating a positive rule, so the cure closes a SITE and leaves the class enumerable
— this lane's exact failure mode. Record: *after the commit gate, no statement may fire `teardown`'s failure branch.*
Its SIGPIPE NIT is then correctly out of scope (rc=141 leaves the installed state; teardown never runs).

**Q2 — AFFIRM**, including the `:294` both-label line my probe D reached independently. **AMEND (MATERIAL, omitted
consequence):** it adds a second occupancy `print`, so tracked `tests/test_install_night_agent.py:216`
(`assertEqual(3, … "print ")`) must become **4** — name it, or the seat will "fix" the assertion. Cleared by probe: its
dictated `for … && arr+=()` block does not trip `set -e` (zsh 5.9 → rc=0).

**Q3 — AFFIRM the authorisation; AMEND the stop condition**, not yet judgment-free: (a) "ANY class-1 or class-2 site"
is not an observable — bolt on the two predicates in my Q3 above; (b) add *the count is per CLASS, not per site*, since
the "different site ⇒ not the same failure" move used in its own §9 justification licenses round 4 identically;
(c) "informs Ed in the PR body" fails on the stop path, where no PR exists — Ed's channel is email, same activation.

**Q4 — F3: I reverse my own answer and AFFIRM the fold** (`trap '' INT TERM HUP` is genuinely one line; I
overestimated the cure), conditional on the seat landing it with its regression and nothing else. **F4: AFFIRM** the
`INSTALLER-BACKUP-WINDOW-01` lane. **Q5 — AFFIRM the REFUSE** (same gap); add the `:312` success guard to its
non-binding must-die list. **Q6 — AFFIRM all three**, identical to mine, including that render-only must not refuse
loaded labels.
