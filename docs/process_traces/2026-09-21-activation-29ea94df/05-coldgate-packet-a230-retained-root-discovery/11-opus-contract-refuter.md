# Contract-lens refuter — packet 05 (A230 retained-root discovery)

Model: Claude Opus 5. Charge: falsify the packet's claims, the lead's labeled
disposition (Q1 (a), Q2 (ii), Q3 (a)), and the asserted application of
`docs/contracts/evidence_night_entry.md` at `9e0a4995`. Read-only from the
worktree at that revision. Terms: *custody root* = a directory under
`/Users/edr/night-custody/` holding one night's `night_plan.json` and its
`night/` evidence; *discovery* = the glob `night-custody/*/night_plan.json`;
*marker* = a file the code reads as fact by its existence alone.

## Validator result

`scripts/validate_gate_packet.py` with both expected digests → `"result":
"PASS"`; all four exhibit digests observed == expected. Charter digest expected
`099de884…` from the convening prompt (independent of the packet); observed the
same.

## Contamination disclosure

The harness auto-injected the global and project `CLAUDE.md`, `CLAUDE.local.md`
and a session-memory index before I could prevent it; I acted on and cite
none. I did not open `RUN_STATE.md`, `TASK_QUEUE.md` (beyond C3's quoted line),
`NIGHT_HANDBACK.md`, or any trace outside this packet.

## Q1 — marker set for a discovered custody root

**Verdict on the lead's disposition (a): REJECT. Severity: BLOCKER.**

**R1 — the deciding artifact is gone; option (b) was executed before the packet
was frozen.** The packet asserts four discovered roots and rests Q1 and Q2 on
the 2026-09-16 root, which is no longer in discovery:

`ls -la /Users/edr/night-custody/` lists n1-20260919, n2-20260919,
qpe01-pilot-n1-20260920, the new candidate root, magistrate, magistrate-bench,
active-campaigns, retired-v1 — and **no 09-16 root**; dir mtime 22:03:29.
`ls -la /Users/edr/night-archive | grep 20260916` shows
`d079-…-n1-20260916-plan-root-retired-1790053407/` with `.SHA256SUMS` and
`.lstat-inventory.txt` written Sep 21 22:03; `fromtimestamp(1790053407)` =
2026-09-21 22:03:27.

The root was moved out of discovery into `night-archive` at **22:03:27 PDT**,
contents intact (`night/chain.exited`, `chain.started`, `refusal.json`,
`receipt.json` all present in the retired copy). The packet is dated "Assembled
2026-09-21 22:05 PDT" and offers as live option (b) "retire the 2026-09-16 root
out of `/Users/edr/night-custody` into `/Users/edr/night-archive` … so discovery
no longer sees it". That had happened already. Consequences:
(1) `retained_roots` now passes with **no rule change at all** — the forcing
problem Q1 exists to solve was removed by action, not by ruling. (2) Consult
18, the contract's own cited authority, says "Never delete or hide roots to
pass discovery" (verified verbatim at `9e0a4995:…/2026-09-20-activation-
21752427/18-consult-…-astra.md:53`); moving a root so the glob cannot see it
hides it from discovery. (3) Lane A230's own text, quoted as C3,
records that this root "was NOT moved (the launch charge forbids moving plan
directories this session did not author)" and that the lane "Goes to the cold
gate or Ed **before** the next harvest retires or retains a root."

I establish the time and the state, not the author. Cure: disclose the
retirement, its author and its authority, and restate Q1/Q2 against actual
state — or reverse the move pending a ruling.

**R2 — (a) misclassifies a root whose night is still running; the packet's own
artifact is the counterexample.** (a) calls a root `retained` when `night/`
holds any `_refusal_paths` match, and separately calls `chain.started` without
`chain.exited` `ACTIVE`, stating no precedence. The 09-16 night satisfied both
for seven hours: `night/refusal.json` written 13:20, reason `night_chain_alive`,
detail "chain process group is still alive or cannot be disproven", pgid 20946
— while `chain.exited` was not written until `epoch_s` 1789617139 =
**2026-09-16 20:52:19** (both `cat`-verified in the retired copy). Option (c)'s
own bar, "must refuse a root whose chain is open", is unmet.

**R3 — `chain.exited` is evidence of death, including of a chain that never
launched.** `run_night.py:415-427` (`_record_chain_exit`) writes it with
optional `"launch_failed": true` and `"reaped_by"`, and `run_night.py:3342-3352`
shows the **dead-man** writing it as `exit_code=None, reaped_by="dead-man",
launch_failed=True` when `chain.started` holds no readable process-group
identity. Under (a) a root whose night never launched, holding no measurement
data, classifies `retained`. The 09-16 case is milder: `{"exit_code": -15}` is
SIGTERM; nothing about harvest or completion follows.

**R4 — "retained" under (a) is not disjoint from "active" under the watchdog.**
`magistrate_watchdog.py:775-790` (`plan_span_active`) returns True for the whole
interval `now <= t0 + window_max_s + COURIER_DEADLINE_S` *after* `chain.exited`
exists, then until `deadman_epoch + COURIER_LOCK_FRESH_S` unless `courier.sent`
exists. A root that died ten minutes after t0 is `retained` by (a) and
span-ACTIVE at once; the prose quotes branches 1 and 3 only.

## Q2 — lane A230: which text holds

**Verdict on the lead's disposition (ii): REJECT. Severity: BLOCKER.**

**R1 — (ii)'s factual premise is false.** (ii) restates §0.7 as "no plan whose
span is active or whose agents are installed" and asserts "the tracked check
item 0 plus the Q1 classification implement" it. Item 0 covers the agents half
(contract 180-186: any loaded `com.joulewise.night*` label, plist or
`.plist.prior` sidecar refuses). The **span** half is not implemented:
`retained_roots` (`evidence_night.py:657-668`, verified verbatim) does no time
arithmetic at all — it never reads `t0_epoch_s`, `window_max_s`,
`COURIER_DEADLINE_S` or `deadman_epoch`, every one of which `plan_span_active`
needs (`magistrate_watchdog.py:771-790`). (ii) would write into an arm
precondition an equivalence the code does not supply, weakening §0.7 to a test
blind to an active span.

**R2 — the option set comes from a narrative state document.** Exhibit C3 is
`TASK_QUEUE.md:858`. Charter §4 admits such an excerpt "ONLY when its exact
words are themselves the object of an enumerated question", "never for process
authority, rationale, background, severity, or disposition". Q2's object is C1
and C2; C3 supplies the background, the framing, and options (i) and (ii)
themselves — the excluded uses. The only amendment authority C3 offers is
"(rule 11)", a citation into a document the judge may not read and the packet
does not supply. A judge may properly REFUSE Q2 on this ground. Cure: cite the
authority to amend §0.7 and `NIGHT_HANDBACK.md` by immutable revision and
location, independent of C3.

**R3 — omitted contrary text inside the handback.** C3 states the handback rule
as "only a refused night's plan root is retired". The packet supplies C2 (the
addendum saying this root is RETAINED) and not the text of that rule. This
night's verdict was `"verdict": "REFUSED"`, reason `night_chain_alive`. If
C3's paraphrase is accurate, the handback's
general rule points to retiring this root while the packet quotes only the
addendum pointing to retaining it: the one root the packet turns on is where
two halves of one document disagree, and only one is in evidence.

## Q3 — the magistrate's own idle MCP helpers

**Verdict on the lead's disposition (a): REJECT. Severity: MATERIAL.**

I do **not** find that (a) hides state: killing a process removes it rather
than concealing it, and `check.json` still records the session root and
`own_pids`. The rejection rests on three other grounds.

1. **(a) preserves a code-versus-authority mismatch instead of curing it.**
   Consult 18:53 requires "owned helpers gone before **REQUEST**"; the code
   refuses at **check** time. `classify_arm_census` (`arm_census.py:206-239`,
   verified verbatim) sets `exempt = set(own)` — the caller's ancestor chain
   only — and gates `idle_exemption` on `plan.receipt_class ==
   "REHEARSAL_STUB"`, so on a real plan the magistrate's own idle MCP children
   land in `foreign`, and `census_check` (`evidence_night.py:697-725`) fails on
   any non-empty `foreign_pids`. The check is stricter than its own authority;
   (b) aligns them, (a) leaves the mismatch and pays a destructive step first.
2. **(a) carries no executed evidence, unlike every other claim in the
   packet.** No probe shows that terminating PIDs 75861/75865 leaves the
   magistrate functional, or that the harness will not respawn an MCP server.
   If it respawns, `check.json` records a quiet machine that is not quiet at
   REQUEST — less faithful than today's honest failure. The packet concedes the
   census refuses tonight on the owner's sessions, so (a) cannot be validated
   tonight.
3. **Q3's deciding exhibits are unverifiable by construction.** D1/D2/D8 come
   from `night-plan-staging/<candidate>/lifecycle/check.json` and D9 from a
   `night-archive` staging-retired directory, both outside the read set the
   packet grants reviewers. Cure: copy them into the packet, digest-pinned.

If (a) is ruled anyway, attach two conditions: an executed probe that the
magistrate survives termination, and a re-observation just before REQUEST.

## Q4 — regression specification

**No labeled disposition to affirm or reject. Gap: MATERIAL.** Q4's three
mutations are sound but incomplete. Add at least: (i) `refusal.json`
present **and** `chain.started` without `chain.exited` → ACTIVE (kills Q1 R2's
ambiguity); (ii) `chain.exited` carrying `"launch_failed": true` → not
retained; (iii) a root inside `t0 + window_max_s + COURIER_DEADLINE_S` with
`chain.exited` and no `courier.sent` → the assertion must say whether
discovery defers to `plan_span_active`.

## Packet hygiene findings

- **BLOCKER — undisclosed prior execution of a live option.** The 09-16 root
  was retired at 22:03:27, two minutes before the stated assembly time, while
  option (b) offers that retirement as a choice and C3 says it awaits this gate.
  Q1, Q2.
- **BLOCKER — narrative-source framing.** Q2's options come from
  `TASK_QUEUE.md:858`, a use charter §4 excludes; amendment authority is cited
  only as "rule 11", unreadable by the judge. Q2.
- **MATERIAL — asymmetric option framing.** Option (b) alone carries an adverse
  note; (a) carries none, though it admits a root whose chain is open and a
  root that never launched. Q1.
- **MATERIAL — selective quotation of `plan_span_active`:** two of four
  branches; the omitted two keep a plan active after `chain.exited`. Q1/2.
- **MATERIAL — unverifiable exhibits** D1/D2/D8/D9 sit in paths the packet
  forbids reviewers to read. Q3 and the Q1 root inventory.
- **MATERIAL — unflagged authority conflict (also supports a judge REFUSE of
  Q1):** B1:208 ("does not certify process liveness or completed delivery") vs
  consult 18:53 ("establish harvest/ownership/completion"), both controlling.
- **NIT:** `evidence_night_entry.md:206` ends with the bare word "Discovery",
  opening a sentence completed on 207, so replacing "lines 205–206" literally
  breaks it. Scope by sentence.
- **Credit where due:** exhibits A1, A3–A5, A7–A9, B1, B2, C1 are verbatim and
  accurate against `9e0a4995`, and D3/D4/D6/D7 reproduce exactly against the
  retired copy. The defects are of scope and of a state change that outran the
  freeze.

## Executed probes

`git show 9e0a4995:<path> | sed -n <range>p`, each matched verbatim to its
exhibit: `evidence_night.py` 657–669, 697–726; `evidence_night_entry.md`
142–158, 180–226 (item 0 at 180–186, item 4 at 203–208, item 5 at 213–220; 206
ends "Discovery"); `magistrate_watchdog.py` 770–800; `run_night.py` 415–432,
3335–3355; `arm_census.py` 206–240 plus `grep -n "_own_root" -A14`;
`…18-consult-…-astra.md` 48–56; the runbook 695–732. On disk,
read-only: the `ls`/`stat` output in Q1 R1, and `cat` of `chain.exited`,
`chain.started`, `refusal.json` in the retired root (Q1 R2/R3).
`env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest
tests.test_evidence_night` → `Ran 92 tests in 178.969s … OK` (exit 0): baseline
green before any cure. No file outside this report was created or changed; the canonical
checkout, `JouleWise-measurement-*`, `night-plan-staging`,
`night-custody/magistrate` and `~/Library/LaunchAgents` were untouched.
