# Independent contract-lens refuter — packet 05 (A230 retained-root discovery)

Model: Claude Opus 5. Charge: falsify the packet's claims, the lead's labeled
disposition (Q1 (a), Q2 (ii), Q3 (a)), and the asserted application of
`docs/contracts/evidence_night_entry.md` at `9e0a4995`. Read-only from
`/Users/edr/code/JouleWise-wt-coldgate-29ea94df` at main `9e0a4995`.
Terms: *custody root* = a directory under `/Users/edr/night-custody/` holding
one night's `night_plan.json` and its `night/` evidence. *Discovery* = the glob
`/Users/edr/night-custody/*/night_plan.json`. *Marker* = a file whose existence
alone the code reads as a classification fact.

## Validator result

`scripts/validate_gate_packet.py` with both expected digests → `"result":
"PASS"`; all four exhibit digests observed == expected. Charter digest expected
`099de884…` from the convening prompt, observed identical in the receipt,
method = the validator's hash of the charter bytes. Proceeded.

## Contamination disclosure

The harness auto-injected the user's global `CLAUDE.md`, the project
`CLAUDE.md`, `CLAUDE.local.md` and a session-memory index before I could
prevent it. I acted on none and cite none. I did not open `RUN_STATE.md`,
`TASK_QUEUE.md` (beyond C3's quoted line), `NIGHT_HANDBACK.md`, or any process
trace outside this packet directory. I am the refuter, not the cold judge.

---

## Q1 — marker set for classifying a discovered custody root

**Verdict on the lead's disposition (a): REJECT. Severity: BLOCKER.**

**R1 — the deciding artifact is gone; option (b) was executed before the packet
was frozen.** The packet asserts four discovered roots and rests Q1 and Q2 on
the 2026-09-16 root. That root is no longer in discovery:

```
ls -la /Users/edr/night-custody/  → n1-20260919, n2-20260919,
   qpe01-pilot-n1-20260920, qpe01-pilot-n1-20260921-2238-…, magistrate,
   magistrate-bench, active-campaigns, retired-v1   ← no 2026-09-16 root
stat -f '%Sm' /Users/edr/night-custody          → 2026-09-21 22:03:29
ls -la /Users/edr/night-archive | grep 20260916 →
   d079-epoch-25g83-derivation-n1-20260916-plan-root-retired-1790053407/
   …-1790053407.SHA256SUMS + …lstat-inventory.txt (Sep 21 22:03)
fromtimestamp(1790053407)                       → 2026-09-21 22:03:27
```

The root was moved out of discovery into `night-archive` at **22:03:27 PDT**,
contents intact (`night/chain.exited`, `chain.started`, `refusal.json`,
`receipt.json` all present in the retired copy). The packet is dated "Assembled
2026-09-21 22:05 PDT" and offers as live option (b) "retire the 2026-09-16 root
out of `/Users/edr/night-custody` into `/Users/edr/night-archive` … so
discovery no longer sees it". That had already happened. Three consequences:
1. `retained_roots` now passes with **no rule change at all**. The forcing
   problem Q1 exists to solve was removed by action, not by ruling.
2. Consult 18 — the contract's own cited authority — says "Never delete or hide
   roots to pass discovery" (verified at `9e0a4995:docs/process_traces/2026-09-
   20-activation-21752427/18-consult-evidence-installer-split-astra.md:53`).
   Moving a root so the glob cannot see it hides it from discovery.
3. Lane A230's own text, quoted by the packet as C3, records that this root
   "was NOT moved (the launch charge forbids moving plan directories this
   session did not author)" and that the lane "Goes to the cold gate or Ed
   **before** the next harvest retires or retains a root."

I establish the time and the state, not the author. Minimum cure: disclose the
retirement, its author and its authority, and restate Q1/Q2 against actual
state — or reverse the move pending the ruling.

**R2 — (a) misclassifies a root whose night is still running; the packet's own
artifact is the counterexample.** (a) calls a root `retained` when `night/`
holds any `_refusal_paths` match, and separately calls `chain.started` without
`chain.exited` `ACTIVE`. It states no precedence. The 2026-09-16 night
satisfied both for seven hours: `night/refusal.json` written 13:20, reason
`night_chain_alive`, detail "chain process group is still alive or cannot be
disproven", pgid 20946 — while `chain.exited` was not written until `epoch_s`
1789617139 = **2026-09-16 20:52:19** (both `cat`-verified in the retired copy).
Option (c)'s own bar, "must refuse a root whose chain is open", is not met by
(a) as drafted.

**R3 — `chain.exited` is evidence of death, and on one path of a chain that
never launched.** `scripts/run_night.py:415-427` (`_record_chain_exit`) writes
it with optional `"launch_failed": true` and `"reaped_by"`; `run_night.py:3342-
3352` shows the **dead-man** writing it as `exit_code=None,
reaped_by="dead-man", launch_failed=True` when `chain.started` holds no
readable process-group identity. Under (a) a root whose night never launched,
holding no measurement data, classifies `retained`. The 09-16 case is milder:
`{"exit_code": -15}` is SIGTERM — the chain died; nothing about harvest or
completion follows.

**R4 — "retained" under (a) is not disjoint from "active" under the watchdog.**
`scripts/magistrate_watchdog.py:775-790` (`plan_span_active`) returns True for
the whole interval `now <= t0 + window_max_s + COURIER_DEADLINE_S` *after*
`chain.exited` exists, then until `deadman_epoch + COURIER_LOCK_FRESH_S` unless
`courier.sent` exists. A root that died ten minutes after t0 is `retained` by
(a) and span-ACTIVE by the watchdog at the same instant. The packet's prose
quotes branches one and three and omits the two time-bounded branches that do
the contrary work.

**Unresolved authority conflict (supports a judge REFUSE).** B1:208 says
"Retention classification does not certify process liveness or completed
delivery"; consult 18:53 says discovery must "establish harvest/ownership/
completion". Both are named controlling; (a) widens the marker set without
resolving which governs, and the packet does not flag the clash.

**NIT — drafting.** `evidence_night_entry.md:206` ends with the bare word
"Discovery", which begins a sentence completed on 207, so the requested literal
replacement of "lines 205–206" breaks that sentence. Scope it by sentence.

## Q2 — lane A230: which text holds

**Verdict on the lead's disposition (ii): REJECT. Severity: BLOCKER.**

**R1 — (ii)'s factual premise is false.** (ii) restates §0.7 as "no plan whose
span is active or whose agents are installed" and asserts "the tracked check
item 0 plus the Q1 classification implement" it. Item 0 does implement the
agents half (contract 180-186: refuses any loaded `com.joulewise.night*` label,
any plist or `.plist.prior` sidecar). The **span** half is not implemented:
`retained_roots` (`joulewise/evidence_night.py:657-668`, verified verbatim)
does no time arithmetic at all — it never reads `t0_epoch_s`, `window_max_s`,
`COURIER_DEADLINE_S` or `deadman_epoch`, every one of which `plan_span_active`
needs (`magistrate_watchdog.py:771-790`). (ii) would write into an arm
precondition an equivalence the code does not supply, weakening §0.7 from
"nothing discoverable" to a test that cannot see an active span.

**R2 — the option set comes from a narrative state document.** Exhibit C3 is
`TASK_QUEUE.md:858`. Charter §4 admits such an excerpt "ONLY when its exact
words are themselves the object of an enumerated question", and "never for
process authority, rationale, background, severity, or disposition". Q2's
object is C1 and C2; C3 supplies the background, the framing, and options (i)
and (ii) themselves — the excluded uses. The only amendment authority C3 offers
is "(rule 11)", a citation into a document the judge may not read and the
packet does not supply. A judge may properly REFUSE Q2 on this ground. Cure:
state the amendment authority for `derivation_night_runbook.md` §0.7 and
`NIGHT_HANDBACK.md` by immutable revision and location, independent of C3.

**R3 — omitted contrary text inside the handback.** C3 states the handback rule
as "only a refused night's plan root is retired". The packet supplies C2 (the
addendum saying this root is RETAINED) and not the text of that retirement
rule. D4's verdict for this night was `"verdict": "REFUSED"`, reason
`night_chain_alive` — verified in the retired copy. If C3's paraphrase is
accurate, the handback's general rule points to retiring this root while the
packet quotes only the addendum pointing to retaining it: the one root the
packet turns on is where two halves of one document disagree, and only one half
is in evidence.

## Q3 — the magistrate's own idle MCP helper processes

**Verdict on the lead's disposition (a): REJECT. Severity: MATERIAL.**

I do **not** find that (a) hides state from the census: killing a process
removes it rather than concealing it, and `check.json` still records the
session root and `own_pids`. The rejection rests on three other grounds.

1. **(a) preserves a code-versus-authority mismatch instead of curing it.**
   Consult 18:53 requires "owned helpers gone before **REQUEST**". The code
   refuses at **check** time: `classify_arm_census`
   (`joulewise/arm_census.py:206-239`, verified verbatim) sets `exempt =
   set(own)` — the caller's ancestor chain only — and gates `idle_exemption` on
   `plan.receipt_class == "REHEARSAL_STUB"`, so for a real plan the
   magistrate's own idle MCP children land in `foreign`; `census_check`
   (`evidence_night.py:697-725`) fails on any non-empty `foreign_pids`. The
   check is stricter than its own authority. Option (b) aligns them; (a) leaves
   the mismatch and pays for it with a destructive step before every check.
2. **(a) carries no executed evidence, unlike every other claim in the
   packet.** No probe shows that terminating PIDs 75861/75865 leaves the
   magistrate functional, nor that the harness will not respawn an MCP server.
   If it respawns, `check.json` records a quiet machine that is not quiet at
   REQUEST — less faithful than today's honest failure. The packet concedes the
   census refuses tonight on the owner's sessions, so (a) cannot be validated
   tonight either.
3. **Q3's deciding exhibits are unverifiable by construction.** D1, D2 and D8
   come from `/Users/edr/night-plan-staging/<candidate>/lifecycle/check.json`
   and D9 from a `night-archive` staging-retired directory — both outside the
   read set the packet grants its reviewers. Cure: copy those JSON documents
   into the packet directory under the exhibit manifest, digest-pinned.

If (a) is ruled anyway, attach two conditions: an executed probe that the
magistrate survives the termination, and a census re-observation immediately
before REQUEST so the passing record is not stale.

## Q4 — regression specification

**Verdict: no labeled disposition to affirm or reject. Gap severity:
MATERIAL.** Q4's three mutations are sound but incomplete. A cure needs at
least: (i) `refusal.json` present **and** `chain.started` without
`chain.exited` → ACTIVE (kills Q1 R2's ambiguity); (ii) `chain.exited` carrying
`"launch_failed": true` → not retained; (iii) a root inside `t0 + window_max_s
+ COURIER_DEADLINE_S` with `chain.exited` and no `courier.sent` → the assertion
must say whether discovery defers to `plan_span_active`. Acceptance command as
stated.

## Packet hygiene findings

- **BLOCKER — undisclosed prior execution of a live option.** The 09-16 root
  was retired at 22:03:27, two minutes before the stated assembly time, while
  option (b) offers that retirement as a choice and C3 says it awaits this
  gate. Effect: Q1, Q2.
- **BLOCKER — narrative-source framing.** Q2's options are lifted from
  `TASK_QUEUE.md:858`, a use charter §4 excludes; amendment authority is cited
  only as "rule 11", unreadable by the judge. Effect: Q2.
- **MATERIAL — asymmetric option framing.** Option (b) alone carries an adverse
  note (handback contradiction, consult 18 prohibition); option (a) carries
  none, though it admits a root whose chain is open and a root that never
  launched. Effect: Q1.
- **MATERIAL — selective quotation of `plan_span_active`:** two of four
  branches; the omitted two keep a plan active after `chain.exited`. Q1, Q2.
- **MATERIAL — unverifiable exhibits** D1/D2/D8/D9 (paths the packet forbids
  reviewers to read). Effect: Q3, and the Q1 root inventory.
- **MATERIAL — unflagged authority conflict:** B1:208 vs consult 18:53. Q1.
- **NIT — line-range deliverable:** B1:206 ends mid-sentence.
- **Credit where due:** exhibits A1, A3–A5, A7–A9, B1, B2, C1 are verbatim and
  accurate against `9e0a4995`, and D3/D4/D6/D7's file facts reproduce exactly
  against the retired copy. The assembly is honest about what it captured; the
  defects are of scope, and of a state change that outran the freeze.

## Executed probes

`git show 9e0a4995:<path> | sed -n <range>p`, each verified verbatim against
its exhibit: `joulewise/evidence_night.py` 657–669 (A1) and 697–726 (A8);
`docs/contracts/evidence_night_entry.md` 142–158, 180–198, 198–215, 213–226
(item 0 at 180–186, item 4 at 203–208, item 5 at 213–220; line 206 ends with
the bare word "Discovery"); `scripts/magistrate_watchdog.py` 770–800 (A3);
`scripts/run_night.py` 415–432 and 3335–3355; `joulewise/arm_census.py` 206–240
plus `grep -n "_own_root" -A14` (A7); `…/18-consult-…-astra.md` 48–56 (B2);
`docs/phase_2/derivation_night_runbook.md` 695–732 (C1 complete).

On disk, read-only: the `ls`/`stat`/`fromtimestamp` block under Q1 R1; plus
`ls -la …-1790053407/night` and `cat …/night/chain.exited` → `{"epoch_s":
1789617139.0360892, "exit_code": -15, …}` = 09-16 20:52:19; `chain.started`
epoch 1789577102 = 09-16 09:45:02; `refusal.json` verdict `REFUSED`, reason
`night_chain_alive`.

`env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest
tests.test_evidence_night` → `Ran 92 tests in 178.969s … OK` (exit 0): baseline
green before any cure. No file outside this report was created or modified;
`/Users/edr/code/JouleWise`, `/Users/edr/JouleWise-measurement-*`,
`/Users/edr/night-plan-staging`, `/Users/edr/night-custody/magistrate` and
`~/Library/LaunchAgents` were untouched.
