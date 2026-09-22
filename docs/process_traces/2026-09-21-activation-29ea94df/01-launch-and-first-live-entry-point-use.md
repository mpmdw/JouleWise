# Record 01 — activation 29ea94df: launch, first live use of the tracked evidence-night entry point, two refusals, cold gate convened

Headless magistrate (Fable 5.1), launched by the watchdog at 21:50:57 PDT 2026-09-21 (attempt 68, after activation 21752427 exited on the checkout precondition and the watchdog's 300 s usage backoff). Canonical checkout `/Users/edr/code/JouleWise` at `7e35d16a` (fenced; no git operation performed there). Bookkeeping branch `bookkeeping/2026-09-21-activation-29ea94df` off main `9e0a4995`.

## §1 Launch (executed)

- Heartbeat written 21:51:15 (pid 75838, the claude process; first write used the shell pid and was corrected 8 s later).
- Durable sources read: AGENTS.md, RUN_STATE.md pointer (activation 21752427 EXIT block), state.json (attempt 68, `last_exit_class` still `usage_exhausted` from an earlier exit; events.jsonl 283 = clean activation exit), no standdown.request, no STOP, no open owner directive (`gh issue list … --label directive` → `[]` at 21:51, 21:57, 22:01, 22:05, 22:09).
- Launch email accepted by Gmail 21:53 PDT, id `1a0c7751da89c4ec`; `notice.ack` written.
- Machine state at launch: two interactive Claude sessions (pids 67916 ttys000 21:37, 68088 ttys001 21:38, each with a Codex MCP server); interactive session a87c3444 working branch `fix/2026-09-21-canonical-self-fast-forward` (D-183) in `JouleWise-wt-selfff`; PR #378 opened for it later this hour.

## §2 First live use of `python -m joulewise.evidence_night` (executed)

1. `prepare --kind quiet_predicate_evidence --t0 next --head 7e35d16ae07489364375d28bd41057d9aa4cfa48` (H pinned to the canonical HEAD, an ancestor of remote main, so the canonical checkout needs no move) — first run 21:56 **REFUSED**: `unidentified prior preparation output: /Users/edr/night-plan-staging/qpe01-pilot-n1-20260920` (the 09-19 pilot's staging directory, made by the record-17 script set, has no `prepare.json`).
2. Retired that staging directory (not a custody root; its plan was published, fired, harvested and uninstalled 09-20): 14 files digested before, `mv` to `/Users/edr/night-archive/qpe01-pilot-n1-20260920-staging-retired-1790052975`, digests re-checked after: 14/14 identical (`/tmp/magistrate-29ea94df/02-pilot-staging-{before,after}.sha256`).
3. `prepare` re-run 21:57 → **rc 0**: candidate `qpe01-pilot-n1-20260921-2238-20260921-2238-1790055480-7e35d16ae07489364375d28bd41057d9aa4cfa48` (plan id `qpe01-pilot-n1-20260921-2238`, t0 1790055480 = 22:38 PDT, install close 22:28, REQUEST 22:30, window end 01:08, dead-man 02:13); clone `/Users/edr/JouleWise-measurement-20260921-2238-1790055480-7e35d16a…-qpe01-pilot-n1`, locked venv built, plan authored, wrapper + three plists rendered; six step checkpoints complete.
4. `check --candidate <staging>` 21:58 → **rc 2**: `REFUSED: pre-arm checks failed: retained_roots, census`. Passed: sealed, night_agents (nothing loaded, no plists), canonical (contains H and the census fix, clean), supervisor (pid 75833 started 21:50:57 > H arrival 21:40:47, one continuous reflog entry), courier (claude on PATH), retry (no attempts). Failed:
   - `retained_roots`: `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916` UNKNOWN (no `courier.sent`/`result.json`; it holds `refusal.json` = `night_chain_alive`, `chain.started`, `chain.exited` exit -15). Its harvest archive verifies 20/20 against the live root. Lane A230 had registered the underlying contradiction (runbook §0.7 vs handback RETAINED) for the cold gate or Ed.
   - `census`: foreign = the owner's two interactive sessions and their Codex helpers AND this session's own idle Codex MCP server processes (75861, 75865: descendants of own root 75838, not in the caller's ancestor chain; `classify_arm_census` exempts only the ancestor chain for a real plan). The 09-19 pilot arm recorded the identical shape and proceeded under the bench scripts' "diagnostic only" reading; the tracked check refuses. Two unreadable PIDs (778, 68054 = the owner's `login` processes) also appear as diagnostics.
   Evidence: `<staging>/lifecycle/check.json`; packet exhibit D.

The candidate lapses at its install close (22:28) unless the census clears before then; a fresh `prepare --t0 next` is one command.

## §3 Cold gate convened (rule 11: proposed process rule; reinterpretation of a prior RETAINED verdict)

Packet `05-coldgate-packet-a230-retained-root-discovery/00-PACKET.md` (sha256 `8b4865d69b2e0bd6951474232cb91fde982414893c8085e1a9dda58d953345de`; validator PASS; four exhibits, all `git show 9e0a4995:` extracts or verbatim command output). Questions: Q1 which night records classify a discovered root as retained (lead: broaden to the driver's terminal records); Q2 lane A230 which text holds (lead: restate §0.7 as the executable "no active span / no installed agents"); Q3 the magistrate's own idle MCP helpers under item 5 (lead: terminate them before `check`, procedure only); Q4 regression specification. Judge: cold Fable, `claude -p` from the doctrine-free worktree `JouleWise-wt-coldgate-29ea94df`, launched detached 22:04:36 (pid 86668), 20-minute budget, ruling to `10-coldgate-fable-ruling.md`. Refuter: Opus contract lens, same packet, independent, `11-opus-contract-refuter.md`, launched 22:04:30. Neither sees the other before sealing.

## §4 Concurrent bench action by the interactive session (observed, not mine)

At 22:03:27 PDT the interactive session a87c3444 (Ed at the machine) retired the 09-16 root to `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260916-plan-root-retired-1790053407` under D-183 (its record 01 §7: SHA256SUMS + lstat inventory first, `mv`, 0 mismatches after). Verified here: 7705 files present, the 20-entry harvest sums check 20/20 against the retired copy. It named the follow-up lane RETAINED-ROOT-REFUSAL-CLASS-01, which is the Q1 cure drafted in §5. The `retained_roots` obstacle is therefore gone on disk for tonight; the ruling still governs the rule for every future root.

## §5 Cure drafted at the bench (branch `fix/2026-09-21-retained-root-terminal-markers`, worktree `JouleWise-wt-retention-29ea94df`)

`retained_roots`: a root is `retained` on any terminal driver record (`courier.sent`, `result.json`, `chain.exited`, or a `run_night._refusal_paths` name); `ACTIVE` (refuses) when `chain.started` exists without `chain.exited`; `UNKNOWN` otherwise. Contract item 4 rewritten to say so. Regressions: the marker table extended to eight shapes; a new test walks the 09-16 shape (refusal + open chain → ACTIVE; + chain.exited → retained; open chain with courier.sent → ACTIVE; receipt-only → UNKNOWN). Run against the live custody directory read-only: three roots retained (the 09-16 root already retired). Module replay recorded in §6 after the ruling; the PR waits for the ruling and for PR #378.
