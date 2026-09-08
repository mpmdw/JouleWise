# Magistrate synthesis — rehearsal-arming authority (interactive magistrate, 2026-09-08 ~01:50 PDT; Ed present, may veto)

Inputs: cold Fable ruling (`10-coldgate-fable-ruling.md`, verdict AMEND, six conditions) and the Opus contract-lens
refutation (`11-coldgate-opus-refutation.md`, verdict AMEND, six conditions). Both uphold the holding that the
watchdog-relaunched headless magistrate is the arming party (MAGISTRATE_WATCHDOG.md line 86; prompt lines 11-13)
and that a `/private/tmp` detached checkout violates no fence for a REHEARSAL_STUB. Both reject my original
four-condition formulation. The disagreements were synthesized, not majority-voted:

1. **"Already armed" is not a usable partition** (Opus finding 1, bench-checked: `plan_is_armed`,
   `scripts/magistrate_watchdog.py:740-750`, is true from the authored epoch). The cold judge's replacement text
   used that partition; it is amended so the session keeps re-arm/remove authority over the ONE plan it authored.
2. **A malformed-but-complete plan inside the watchdog's glob can brick the loop** (Opus finding 2:
   `HOLD_UNSAFE` + drain ladder, `:1206-1210`, `:1729-1745`). The cold judge relied on `write_night_plan`
   atomicity, which prevents half-written plans but not malformed ones. Adopted: stage outside the glob, validate
   with `scripts/install_night_agent.sh --render-only DIR` (flag verified at `scripts/install_night_agent.sh:5,21`),
   then `os.replace` into the plan directory.
3. **Condition "no agent session alive" must read "no OTHER agent session"** (both seats); the driver's own
   census stays its first act (D-169).
4. **Pin durability** (cold judge finding 5): the pinned commit lives only on a bookkeeping branch; preserve it
   while the plan is armed.

## Ruling (AMEND; supersedes the packet's four conditions and my first message to the headless magistrate)

Relaunch prompt line 19 is replaced by:

> Do not write, move, or delete watchdog-owned state (`state.json`, `magistrate.lock`, `watchdog.lock`,
> `standdown.request`, `events.jsonl`, `STOP`, `attempts/`) or the `com.joulewise.magistrate` launchd
> configuration except through the heartbeat and notice-acknowledgment interfaces. Do not alter, move, or delete
> any plan directory, night record, or night LaunchAgent except (a) a plan this session authored under the
> NIGHT_HANDBACK procedure, which it may re-arm or remove under that same procedure, and (b) the documented
> uninstall after a plan's completion. Authoring a new plan with `joulewise.night_plan_writer.write_night_plan`
> and installing its two night agents under the NIGHT_HANDBACK procedure is arming, not an alteration under
> this line.

Conditions on rehearsal-20260909 (all eight required):

1. `NIGHT_HANDBACK.md` re-dated with the real pins and committed before the arm email (satisfied at ae8f074f).
2. The plan is authored ONLY by `write_night_plan`, to a staging path NOT matched by
   `~/night-custody/*/night_plan.json`, validated there with `scripts/install_night_agent.sh --plan <staged>
   --hour H --minute M --render-only <dir>` run FROM `/private/tmp/joulewise-rehearsal-20260909-checkout` at
   ae8f074f, and only then moved with `os.replace` into its plan directory.
3. The plan's `custody_root` equals its plan directory and holds no prior night record; both night agents install
   from that same checkout with `--hour/--minute` equal to the plan's t0 in local time (02:56 PDT).
4. The arm email names t0, `measurement_root`, `measurement_head`, receipt class REHEARSAL_STUB and the courier
   deadline, and precedes the move in (2). No NO on the thread when the move begins.
5. No agent session OTHER than the arming session is alive at arm time; the arming session re-runs the census
   immediately before the move in (2). The driver's census remains its own first act.
6. `origin/bookkeeping/2026-09-08-activation-evidence` (or main once PR #295 merges) keeps ae8f074f reachable
   until the stub plan root and checkout are removed.
7. The arming session exits by t0 − 25 min per line 12; the frozen triple enters the next relaunch prompt.
8. Re-arm or removal of THIS plan by a later headless session follows (2)-(5) again; every other plan, record,
   lock, request, event and `state.json` stays barred.

Recorded as decision D-175 (Ed may veto). The line-19 text lands on main via PR; until it merges, the headless
magistrate operates under this synthesis as the ruling of record.
