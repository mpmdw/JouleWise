# Verbatim: RUN_STATE.md T3-CUTOVER checkpoint block (as committed at e3612f5)

## ✅ CHECKPOINT 2026-08-03 late night — T3 CUTOVER (successor session, ACTIVE)

**T3 Code (Alpha) is now the standing control plane** (Ed directive,
TIER 1 — outranked only by measurement-pollution constraints). It is
the PRESENTATION/CONTROL plane, never the compliance plane: envelopes,
leases, manifests, WRITE_SCOPE, and every gauntlet layer remain
authoritative and unchanged. Full adjudication record: two Sol xhigh
design consults (threads `019fca7c` — lost to MCP recycle, conclusions
recapped+adopted in `019fcac1` — and `019fcac1`) plus a Sol high night-
plan review (`019fcafc`); run report + council row at session close.

**Operating orders effective NOW (Ed-directed interim; rule-11
ratification rides tomorrow's cold-gate packet):**
1. t3 thread mode **"Full access" is PROHIBITED for this repo** — it
   maps to `--permission-mode bypassPermissions
   --allow-dangerously-skip-permissions` (confirmed live from process
   table). Supervised/Auto only.
2. **Never pattern-kill** (`pkill -f "codex exec"` etc.) — sibling t3
   threads make the process table shared. Kill only PIDs recorded in
   your own manifest/scratchpad, verified by start-time + ancestry.
3. **t3 checkpoint-REVERT is forbidden in the main tree**; in a
   worktree it is a workspace mutation → stop writers, capture
   manifest/diff, record it, re-baseline before delegation resumes. A
   t3 checkpoint ref is never audit evidence; a t3 checkmark is never
   an envelope.
4. **t3-native Codex threads are Ed-direct only** — never targets for
   lead-delegated or gate-bearing work (that stays on wrapped routes);
   material consumption of native-thread output requires a
   lead-authored ingestion note in the session manifest (interim form).
5. Delegated-run visibility: substantial background Sol rounds go
   through the tracked codex subagent (visible "Subagent task"
   activity) — lifecycle visibility only; envelope/manifest ceremony
   unchanged underneath.

**Ed rulings tonight (ratification via packet):** R1 — fresh-eyes
sweep cadence is WORK-CHUNK-ANCHORED (post-consumption of substantial
rounds / merge waves / adjudications) with a mechanical
materially-consumed-invocation backstop counter; this rules the shape
`D080-TRIGGER-01` (queue A52) was blocked on — row stays BLOCKED until
the D-080 amendment ratifies it. R2 — cold gate uses
CHARTER-SUPPRESSION (standing tracked hash-pinned charter replaces
`CLAUDE.local.md` ingestion; packet validator refuses hash mismatch);
cold FABLE judge + Sol xhigh contract-lens refuter (cross-model
diversity; Sol's conflict-disclosed concurrence on topology). R3 —
COMPRESSED shadow cutover: six acceptance gates during real work, no
fictional shadow period; rollback = pre-t3 mechanism per route, TUI
operation remains available; Sol's full-shadow preference recorded as
dissent. Gates: native-discussion, phone-approval, app-death recovery,
checkpoint-restore, isolated-native-write, cold-packet-handoff. **This
checkpoint's commit is the isolated-native-write gate exercise** (first
governed t3-native repo write: small, reviewed, pushed, verified).

**GATE/PROBE LOG (live, same night):** isolated-native-write ✅
(97d6e3d). Native-discussion ✅ — Ed ran a native t3 Codex thread in
the repo (rollout `019fcb0b-710c-75d2-8aaf-adb69680ea7d`, benign test
exchange, ingestion note = this entry); BONUS: rollout `session_meta`
carries `originator: "t3code_desktop"` — a mechanical provenance
discriminator for native-vs-wrapper Codex sessions, free in the
evidence stream (fold into the §4/§6 amendment). Phone-approval ❌ NOT
cleared + A3 FINDING: in t3 "Auto" mode Claude's classifier
SELF-APPROVED a sandbox-disabled home-dir write with NO prompt relayed
— Auto ≠ human-in-loop; only Supervised guarantees a tap; anything
requiring Ed's eyes uses a Supervised thread or waits (gate re-run:
flip a thread to Supervised, one prompt, one phone tap). Probes:
CODEX_HOME default (no provider override — ~/.codex recipes valid);
CLAUDE.local.md ABSENT in all worktrees (rule-11 doctrine provably
main-checkout-only — charter urgency confirmed); git common-dir
reachable/writable from worktrees (bookkeeper root feasible); t3
server = single origin 127.0.0.1:3773, pid-matched, but bound 0.0.0.0
(LAN-exposed, ticket-auth'd — Ed to check the Network-access toggle).

**TONIGHT'S NIGHT PLAN (Sol-corrected order, thread `019fcafc`).**
Window execution stays CONDITIONAL on the 16h-runway block's Window-C
conditions (adapter identity ≥140W resolved — 70W negotiation open
question; fresh ED-5A; guarded-launcher conditions; battery-cap
consult). If conditions do not resolve: desk-only night = probes +
gates + packet prep (characterization captures may still run,
non-claim).
- **A (this t3 session, ~1h):** Phase-0 probes — provider CODEX_HOME;
  CLAUDE.local.md worktree loading; Supervised/Auto EFFECTIVE
  capability probes (approval/sandbox/write behavior, not just flag
  mapping); native context-provenance probe (charter/suppression
  behavior in a real spawned context); t3 RPC recon (read-only, no
  thread spawning); checkpoint-restore semantics on a SCRATCH repo;
  git-common-dir reachability from a t3 worktree. Phone-approval +
  native-discussion gates complete BEFORE the runway (gate activity
  resets the idle runway).
- **B (window block, old doctrine unchanged):** app-UP non-claim idle
  capture (t3 resident, threads dormant) → hand-off note OFF-REPO
  (memory dir, NOT a repo commit) → freeze measurement head → QUIT t3
  AND inventory/stop survivors (cloudflared, helpers, resource
  monitor — verify, don't assume) → app-DOWN non-claim capture
  (separate custody; shares NO baselines/calibration/NEG-8 evidence
  with the claim chain) → end characterization → ≥10-min untouched
  runway → ED-5A (Ed, physical) → governed settles → COMPACT claim
  windows, each independently calibrated/verdicted/backed-up, launched
  from an ORDINARY GUARDED SHELL with ZERO agent sessions (an idle
  claude session is 12–18% CPU of agent load per D-099 — none allowed)
  → post-cal → verdict → immutable backup → THEN relaunch t3 →
  app-death gate vs predeclared criteria (history/checkpoint,
  cwd/worktree, provider, mode, no duplicated turn/side effect).
- **Aborts:** any surviving agent/helper process; head or frozen-plan
  drift; failed 5A/prep/admission; nonempty runs root; custody/trap
  failure; third same-cause failure (standing escalation trigger).
- **App-up window operation remains PROHIBITED** until the
  characterization pair + the quiet-guard WO (host-wide quiet lease,
  refuse-at-arm, characterized resident watcher — to be minted as
  QUIET-GUARD-01) land through the full gauntlet.

**TOMORROW (order):** (1) CAL-BRACKET B1 rule-11 gate — FIRST repo-work
item, gates everything mint-ward; (2) t3 doctrine cold-gate packet →
fresh-t3-thread Fable judge + Sol xhigh refuter (first live use of the
new cold-gate mechanism, on the packet that defines it); (3)
quiet-guard WO spec consult (Sol xhigh); (4) WO-T3-VIS (t3-thread-
bridge: audited wrapper dispatching `thread.create`/`thread.turn.start`
so delegated Sol rounds appear as REAL t3 threads — full council, new
adapter) probes + spec; (5) contract §4/§6/§7/§8 + skills amendment
drafting (visibility axis, four-axis provenance fields, owner-kind,
transient-write limitation, top-level redefinition).

