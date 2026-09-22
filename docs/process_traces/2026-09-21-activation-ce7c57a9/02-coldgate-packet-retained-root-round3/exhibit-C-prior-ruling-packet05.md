# Exhibit C — prior cold-gate ruling (packet 05 of activation 29ea94df), verbatim; the ruled passages the round-2 head carries

# Cold-gate Fable ruling — packet 05 (A230 retained-root discovery, census helpers)

Judge: Claude Fable 5.1, cold session, worktree `JouleWise-wt-coldgate-29ea94df` at `9e0a4995`. Wall: 22:04:45–22:14 PDT 2026-09-21. Foreground only, no subagents.

## Contamination disclosure

Auto-loaded before I could refuse: `~/.claude/CLAUDE.md` (global rules), the worktree `CLAUDE.md`, and the memory index `MEMORY.md` (one-line pointers only; several lines mention this activation, a t0 of 22:38, and PR #378). I opened no memory file, no `CLAUDE.local.md`, `RUN_STATE.md`, narrative trace, or `TASK_QUEUE.md` beyond line 858 (exhibit C3, verified by `git show`). Charter digest: expected `099de884…c95d81` (from the convening prompt), observed `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` by `shasum -a 256`; packet expected `8b4865d6…345de`, observed identical. Validator: first run with the prompt's typo'd charter sha → `REFUSE charter_trusted_observed_mismatch` rc=2; rerun with the correct sha → `PASS` rc=0, four exhibits expected=observed. Exhibits A1–A8, B1, B2, C1, C2, C3 each diffed byte-for-byte against `git show 9e0a4995:<path>` (A8 differs by one trailing blank line only).

## Packet hygiene

- **BLOCKER — the object of Q1 was moved during packet assembly and the packet does not say so.** At my probe (22:06) `/Users/edr/night-custody/` holds three plan roots, not four: `d079-epoch-25g83-derivation-n1-20260916` is gone, and `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260916-plan-root-retired-1790053407` exists with a 1.26 MB `SHA256SUMS` and inventory dated 22:03 (epoch 1790053407 = 22:03:27 PDT). Exhibit D is dated 21:58–22:05 and says "Four roots were found"; the packet says only that "nothing is armed." Consult 18 (B2, verified) says "Never delete or hide roots to pass discovery." The retirement happened minutes after `check` refused on exactly that root and before this gate ruled, while lane A230 (C3) says the root "goes to the cold gate or Ed before the next harvest retires or retains a root." I do not rule on intent. Effect: Q1's clause "the 2026-09-16 root then classifies as retained" is moot; Q1 remains decidable as a rule for future roots. Q2 option (i) was de facto executed for this root before the ruling. The lead's synthesis must disclose actor, time, reason, and the digest files, and the next `check` record must note that item 4 now passes because of the move, not because of any cure.
- **MATERIAL — C2 used beyond its admissible object.** The handback addendum is admissible only because its words are Q2's object. The Q1 narrative uses it as authority ("the handback's dated addendum says … RETAINED"). I disregarded C2 for Q1.
- **MATERIAL — wrong probe cost.** The packet says the test module takes "about 60 s". Measured: 92 tests, 179.9 s, OK.
- **NIT** — D9 (a bench script's "diagnostic only" label from a retired staging directory) is prior practice, not authority. The packet does not ask me to reinterpret it; used fairly.
- Otherwise neutral: options are symmetrically stated, exhibits are verbatim, questions are atomic.

## Q1 — which night records classify a discovered root as retained: AFFIRM (a), with a precedence rule added

Deciding exhibits: A4 (installer's night-record set, verified at `night_agent_install.py:1133-1138`), A5 (`run_night._refusal_paths`, `scripts/run_night.py:282-285`), A3 (`plan_span_active`, `magistrate_watchdog.py:781-786`: chain open = active), B2 (consult 18: "unknown or active ownership stops"). The project already defines, in code, both "this root has been used" (A4) and "this root is still active" (A3). Item 4 should use those definitions, not a two-entry subset that leaves a refused night UNKNOWN forever. Option (b) is rejected as a rule: it needs a move for every refused night and collides with B2. Option (a) as written has one defect: it lists the retained test before the active test, so a root with `chain.started`, no `chain.exited`, and a `calibration-refusal.json` written mid-chain would read retained while the chain is alive. Cure: active is tested first.

Ruled classification (labels `ACTIVE`, `retained`, `UNKNOWN`; `night/` means `<root>/night/`; every path must satisfy `safe_path(...).is_file()`):

1. `ACTIVE` if `night/chain.started` is a regular file and `night/chain.exited` is not. Refuses.
2. else `retained` if any of these is a regular file: `night/courier.sent`, `night/result.json`, `night/chain.exited`, or any path returned by `run_night._refusal_paths(night)` (`refusal.json`, `refusal-N.json`, `calibration-refusal.json`, `calibration-refusal.json.*.json`). `evidence` lists every one found.
3. else `UNKNOWN`. Refuses.

Replacement for B1 lines 205–206 (contract `docs/contracts/evidence_night_entry.md`, replacing "An existing regular `night/courier.sent` … Otherwise it is UNKNOWN and refuses."):

> A root whose `night/chain.started` is a regular file without a regular `night/chain.exited` is ACTIVE and refuses. Otherwise an existing regular `night/courier.sent`, `night/result.json`, `night/chain.exited`, or any regular file matched by `run_night._refusal_paths` (`refusal.json`, `refusal-N.json`, `calibration-refusal.json`, `calibration-refusal.json.*.json`) classifies its root as retained; the record lists every marker found. Otherwise it is UNKNOWN and refuses.

This is a contract change (the marker set is contract text) and a change to `evidence_night.retained_roots`; it pairs refuters. Severity of the underlying defect: MATERIAL (a refused night blocks every later arm until someone moves a root, which is the behaviour B2 forbids).

## Q2 — lane A230, which text holds: AFFIRM (ii)

I have authority: the lane text itself (C3) assigns the choice to "the cold gate or Ed", the convening trigger is rule 11, and the question is atomic. Deciding exhibits: B2 (retained roots stay discoverable by design, "never delete or hide roots to pass discovery"), A3 (the watchdog fences spans, not the glob), C3's own verified statement that the installer reads no sibling. §0.7's "expect no output" is a precondition the project's own retention rule makes unsatisfiable, so it cannot be the text that holds. Option (i) makes moving roots a precondition of arming, which is B2's forbidden act performed on schedule. Option (ii) states the check the machinery already applies. Retirement of a harvested root stays permitted as housekeeping with digests, never as a way to satisfy §0.7.

Replacement text for C1 from "Check it, and expect no output:" to the end of the fenced block:

> Check it. Prior roots may be discoverable; what stops an arm is any root whose chain is open, whose span is active, whose night agents are installed, or whose records show no terminal state. The executable form is `python -m joulewise.evidence_night check --candidate STAGING`, whose `night_agents` and `retained_roots` items must both pass with every inventoried root classified `retained` (contract item 4: `ACTIVE` and `UNKNOWN` refuse). For a manual read:
>
> ```zsh
> for p in /Users/edr/night-custody/*/night_plan.json(N); do
>   n=${p:h}/night; r=${p:h:t}
>   if [[ -f $n/chain.started && ! -f $n/chain.exited ]]; then print -r -- "$r: ACTIVE"; continue; fi
>   m=($n/courier.sent(N) $n/result.json(N) $n/chain.exited(N) $n/refusal.json(N) $n/refusal-<0-9>*.json(N) $n/calibration-refusal.json(N) $n/calibration-refusal.json.*.json(N))
>   (( $#m )) && print -r -- "$r: retained ${m[1]:t}" || print -r -- "$r: UNKNOWN"
> done
> ```
>
> Every line must read `retained`; an `ACTIVE` or `UNKNOWN` line, or any installed night plist, stops the arm. Do not move or edit a root to change its line.

The handback's retention sentence (C2) then stands unchanged; the two texts agree. Severity: MATERIAL (contradictory arm preconditions in tracked process text).

## Q3 — the magistrate's own idle MCP helpers: AFFIRM (a), with a preferred durable form named

Deciding exhibits: A7 (`arm_census.py:209` own = ancestor chain of the caller; `:226-230` idle exemption only for `REHEARSAL_STUB`), A9 (contract: "Any FOREIGN PID … refuses"), A8 (`evidence_night.py:725` instruction "helpers must be gone before REQUEST"), D8 (75861/75865 are children of session root 75838, not ancestors of the caller). Under the contract as written the helpers are FOREIGN and the refusal is correct; D9 shows the bench scripts proceeded on the same shape with a label, which the tracked check rightly does not allow. Option (b) changes the classifier that `arm_census.py:309` also uses on the night-driver path, so it is measurement-adjacent, needs a contract change and paired refuters, and buys nothing the procedure does not. Option (a) it is.

Handbook step (exact text, to precede `check`):

> Before running `check` on a real plan, this session terminates its own idle MCP helpers. List the children of the session root: `pgrep -lP <session-root-pid>`. For every child whose command line contains `codex mcp-server`, send SIGTERM to that child and its descendants (`pkill -TERM -P <child-pid>`; `kill -TERM <child-pid>`), wait until `pgrep -f 'codex mcp-server'` lists no descendant of the session root, and record the PIDs terminated in the check record. Terminate nothing outside the session root's descendants. Then run `check`. If the census still reports any descendant of the own session root as foreign, stop; never relabel it "diagnostic".

Preferred durable form (option (c), not ruled here because its launcher lives outside this packet's exhibits): launch the headless magistrate without the project MCP server (Claude Code's strict MCP-config flags), so no helper exists to terminate. That change needs its own packet. Severity: MATERIAL (the tracked entry point cannot pass on the standard launch).

## Q4 — regression specification for the ruled cures

Add beside A6 in `tests/test_evidence_night.py`, each root built as in A6 (a `night_plan.json` file plus `night/`), reading `checked("retained_roots")["checks"]["retained_roots"]`:

1. Only `night/refusal.json` → `retained`, `evidence == [that path]`, verdict `pass`. Kills: marker list reverted to the two entries.
2. Only `night/chain.exited` → `retained`. Kills: `chain.exited` dropped from the set.
3. Only `night/refusal-3.json`; separately only `night/calibration-refusal.json.2.json` → `retained`. Kills: a literal `refusal.json` check replacing `_refusal_paths`.
4. `night/chain.started` alone → `ACTIVE`, verdict `fail`, and `check()` refuses naming `retained_roots`. Kills: active test removed.
5. `night/chain.started` + `night/calibration-refusal.json`, no `chain.exited` → `ACTIVE`. Kills: retained tested before active (the precedence defect above).
6. `night/chain.started` + `night/chain.exited` → `retained`. Kills: `ACTIVE` keyed on `chain.started` alone.
7. `night/refusal.json` as a directory → not counted, root `UNKNOWN`. Kills: `is_file` replaced by `exists`/`lexists`.
8. Plan file only → `UNKNOWN`, verdict `fail` (retain A6's existing case).
9. Q3 is procedure, so no test; the handbook step is checked by the check record listing the terminated PIDs.

Acceptance: `env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_evidence_night`. On main `9e0a4995` today: `Ran 92 tests in 179.932s — OK`, rc 0.

## Executed probes (all read-only)

- `scripts/validate_gate_packet.py … --expected-charter-sha256 …a880…` → `REFUSE`, rc=2; rerun with `…a870…` → `PASS`, rc=0.
- `shasum -a 256` charter, packet → match the pins above.
- `diff <(git show 9e0a4995:<path> | sed -n …) <(exhibit block)` for A1–A8, B1, B2, C1, C2 (lines 488–502 read for selective-quotation check: the paragraph is complete and unaltered), C3.
- `ls -la /Users/edr/night-custody/` at 22:06:13 → roots present: `…n1-20260919`, `…n2-20260919`, `qpe01-pilot-n1-20260920`, `qpe01-pilot-n1-20260921-2238-…` (the candidate); the 2026-09-16 root absent; `ls …/night-archive/ | grep 20260916` → `…-plan-root-retired-1790053407` with `.SHA256SUMS` (1,262,072 B) and `.lstat-inventory.txt`, both 22:03; the harvest archive `…-harvest-20260916/` intact. Marker loop over the three live roots: all `courier.sent=y result.json=y chain.started=y chain.exited=y`.
- `git show 9e0a4995:joulewise/arm_census.py | sed -n 132,170p` (`_own_root`), `git grep classify_arm_census 9e0a4995` → callers at `arm_census.py:309` and `evidence_night.py:687`.
- `python3 -B -m unittest tests.test_evidence_night` → 92 tests OK, 179.9 s, rc 0.
- NOT EXECUTED: no read inside the retired root directory (outside my allowed read set); no probe of the magistrate launcher for Q3 option (c).
