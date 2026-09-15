# Cold-gate packet 65 — the Ed-hands desk proof for ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01 (directive #337 ruling 3): which pack root, what the acceptance requires, and when (assembled mechanically by activation 24b9d3dd, 2026-09-14 17:10 PDT)

Convened under rule 11 because two items are reinterpretations the magistrate may not decide alone: (1) whether a throwaway clone may carry a PATCHED arm-readiness registry so that an existing pack resolves (a reinterpretation of an installed roster, never merged); (2) what the lane's acceptance sentence actually requires, given that the tool emits the acceptance evidence only on a full fifteen-row PASS. Ed's directive #337 ruling 3 (exhibit D) orders the magistrate to prepare the pack root and window-custody root and email Ed the exact command and when; it does not rule either item.

## What was found

- The desk tool `scripts/author_arm_evidence_t0.py` takes exactly `--pack-root` and `--custody-root`; the census row `t0.no_stray_keepawake` is the 10th of 15 T-0 rows; the four probes must each exit 1 with empty stdout; the source record that the acceptance names is written ONLY when all fifteen rows derive (exhibit A §0, §D.1; `joulewise/arm_readiness_evidence_t0.py:2318-2401`). The six preceding captures require `sudo -n systemsetup -setusingnetworktime off`, `quiet_mac_prep.sh` (display asleep), `prewindow_check.sh --wait` (≥600 s clean dwell), a real ledger reservation with `--execute`, and the whole sequence inside a 10–60 minute span (exhibit A §0, §B).
- No committed pack root on main carries the tool past pack resolution: the `_v1` packs refuse at plan resolution or root-leaf shape; the `_v2`/`_v3` packs have the right shape but the live registry's `successor_pack_ids` name three `_v5` Qwen3 packs whose directories do not exist (exhibit A §A2; exhibit C). A read-only experiment showed that patching `successor_pack_ids` to name `d117_floor_qwen25_1p5b_v3` makes that pack resolve; the registry bytes must equal HEAD's, so the patch would have to be COMMITTED in the throwaway clone, plus an empty terminal-review trailer commit and `update-ref` of `refs/heads/main` and `refs/remotes/origin/main` in that clone (exhibit A §A2, §A4).
- Nothing in the tool, the capture tool, `quiet_mac_prep.sh` or `prewindow_check.sh` reads launchd, `night_plan.json` or `night-custody`; live agent processes refuse twice (the census row and `prewindow_check.sh`). No run of this tool has ever completed on this machine (exhibit A §C, §D.3).
- The lane's acceptance (exhibit B) says: run the tool "against a TRANSACTION_PACK pack root built from this checkout plus a window-custody root, with no browser open, Claude Code, the Claude and ChatGPT desktop apps and every codex MCP server closed, and no caffeinate running; the emitted t0.no_stray_keepawake source record must show the two new argv with exit 1 and empty stdout. A refusal on an earlier T-0 row is reported, not read as a census failure."
- D-161 (exhibit E): operator-only-adversary refusals are over-engineering; fail-closed only for physics/evidence/pre-registration. The desk proof produces no measurement and no claim input.

## Q1 — the pack root (rule one option, or write a better one)

(a) The throwaway clone `/Users/edr/JouleWise-desk-proof-20260915` MAY carry a committed registry patch naming `d117_floor_qwen25_1p5b_v3` as a successor pack, plus the terminal-review trailer commit and the two `update-ref`s, PROVIDED the clone is never pushed, never used for any measurement, and the desk-proof record states the patch sha and that the proof was made against a patched roster. (b) NOT allowed: the proof must wait for a real pack the live registry installs (which means a registry/pack PR under the gate first — name what that PR must contain). (c) A registry PR under the gate that names an existing `_v3` pack as an installed successor on main (a roster change), after which the proof runs from a clean clone. (d) Another option the judge writes.

Rule which, with the reason, and state whether the option is a contract change (needing Ed) or a bench decision.

## Q2 — what the acceptance requires (rule one option, or write a better one)

(i) As written: a full fifteen-row PASS is required; the desk proof therefore IS the complete T-0 ceremony (sudo network-time off, quiet-mac prep with display asleep, ≥10 min dwell, a real ledger reservation against a scratch ledger copy) run by Ed's hands; nothing cheaper counts. (ii) A cheaper proof is acceptable under D-161: a run that refuses at a row AFTER the census (11–15) proves the census row passed, and the REFUSE JSON plus the captured probe outputs are the evidence — say whether the tool actually exposes the probe outputs in that branch (exhibit A says nothing is written on refusal; the judge must not assume it does). (iii) Split the lane: the pattern proof (the two ruled argv returning exit 1 with empty stdout on Ed's quiet machine with no agents) is taken by a standalone probe run (`/usr/bin/pgrep -lf <pattern>; echo $?` for both patterns plus the agent pattern), recorded by Ed's hands, and closes THIS lane; the full-row proof is folded into the first pack night's own T-0 rehearsal, which already runs the tool. State whether (iii) changes the ruled acceptance text (it does) and who may change it (the cold gate may rule it; the magistrate records).

## Q3 — for the record

When is the earliest safe time for Ed's run, relative to the armed night `d079-epoch-25g83-derivation-n1-20260915` (t0 2026-09-15 02:56 PDT, courier deadline 05:31, dead-man 07:00, both agents installed) and its post-night uninstall? May the run happen while the night agents are still installed but idle? What must the magistrate prove at the bench (with agents running, no sudo) before booking Ed — is exhibit A's A5 dry gate (expected refusal `evidence_author_t0_clock_attestation_missing`) the right bar?

## Constraints on the judge

Rule only the questions above; do not amend any rule, decision-log entry or skill doctrine (name text changes as text for the magistrate to record). Cite exhibits by name; code by file:line only if you read it in this checkout. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE.local.md or process traces outside this packet; `docs/decision_log.md` only at D-161 and D-180/D-181 headings. Never run the test suite, never touch measurement clones, night-custody or LaunchAgents. Write the ruling to `docs/process_traces/2026-09-13-activation-24b9d3dd/65-coldgate-packet-desk-proof/10-coldgate-fable-ruling.md`, under 14 KB, sections: disclosure of auto-loaded files; validation result; Q1; Q2; Q3; text for the record.

## Charter pin

`docs/process/coldgate_charter.md` sha256 `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`.

## Exhibit manifest

- `exhibit-A-research-report-64.md` sha256 `3f251e3a90d9f10f9e040849c8cd0b11f473387eececdb0be30f0933330ac3c2`
- `exhibit-B-kernel-lane-row.md` sha256 `5cf62a154a61b45bed04db9c1b1d565234e600b2fa44c39c8a72d28d16db6228`
- `exhibit-C-registry-and-packs.md` sha256 `59ca4a57f43e22881f0b82b9e44ba22369e28f1a96288fd66d8cbad12e447634`
- `exhibit-D-directive-337-ruling-3.md` sha256 `ab3b4211a7a4b497cc5c61edd39e65581ef7fb01e74b61f6be2181bb3118df73`
- `exhibit-E-d161-threat-model.md` sha256 `70bc1de36c6cf983744035fac3aaab1ddaa8fd3161d809c665d9aa982a70aa55`
