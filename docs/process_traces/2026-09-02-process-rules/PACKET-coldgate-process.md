# Cold-gate packet — two proposed process rules (Opus 159 §E; ruling 171a R-10)

Mandatory trigger (charter §3): "any proposed process rule". Neither proposal
is adopted; both are queued here by the magistrate under CLAUDE.local.md rule
11 (the lieutenant may not adopt process rules alone; the magistrate routes
them to a cold instance).

Read-only. Repo: /Users/edr/code/JouleWise (main @ 6075389a). Write NOTHING
under it; TMPDIR = a subdirectory you create under
<scratchpad>/.
Python: /Users/edr/code/JouleWise/.venv/bin/python. Do NOT launch any codex/
claude process. Do NOT run canonical `unittest discover`.

Charter: docs/process/coldgate_charter.md — expected sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81 (verify with
`shasum -a 256`; if it differs, say so in your disclosure and stop). Read
§3-§5 and §8 before anything else. Charter §4 read set: ONLY this packet and
the primary evidence cited below — no narrative process/state docs
(README.md, RUN_STATE.md, TASK_QUEUE.md, docs/orchestration.md,
docs/agent_playbook.md), no CLAUDE*.md doctrine, no memory files. Disclose
any contamination (anything you read outside the set, or prior context).

## Packet (read all, in this order)

1. This file, §Proposals and §Facts.
2. Evidence for Q1 (the four same-signature findings), all under
   docs/process_traces/2026-09-02-projection-02/:
   151-opus-proj02-contract.md (table row at :18, finding F1 at :37);
   149-terra-proj02-exec.md (envelope line :2, finding EXE-02; prose :9);
   157-luna-proj02-delta.md (envelope :2, F1; prose :15);
   159-opus-proj02-final.md (§A :23-133 — the clause→assertion map itself;
   §E :303-322 — the proposal, verbatim).
3. Evidence for Q2: docs/process_traces/2026-09-02-projection-02/
   171a-RULING-decode-identity.md (R-10 at :124-129; the contract text that
   carried the unchecked equality at :96-104); the receipt pair that would
   have refuted it:
   configs/campaigns/d117_floor_qwen25_1p5b_v3/identity_pin_projection.receipts/projection-0001.json
   and configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/identity_pin_projection.receipts/projection-0001.json
   (compare each unit's `config_set_sha256`; the point of R-10 is that a
   floor producer unit and the contrast consumer unit do NOT share one).
4. The existing home the proposals would extend:
   docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md
   item 1 (:45-111, especially :90-101: "That residual is by design the
   S9-shape sweep's job, re-run before every transaction (record as a
   standing pre-window row)") and
   docs/process_traces/2026-08-27-t26/ruled-not-installed-sweep/README.md,
   METHOD.md, SHORTLIST.md (what the S9 sweep actually does).
5. The binding pattern the T26 ruling prescribes for process rules
   (COLD-GATE-RULING.md :104-111): decision log "How To Use This Log",
   docs/agent_playbook.md Mission M0, tests — NOT orchestration.md or the
   council skill, because a seat never reads those at brief-writing time.

## Proposals (verbatim, then the magistrate's draft rule text)

Q1 — Opus 159 §E (:303-322): "The structural cure is to require that map
[clause → assertion] as a deliverable of the implementation brief — every
quoted phrase of the ruling paired with the assertion that bites it, written
BEFORE the refuter fan-out — so that 'ruled but unpinned' is caught by
construction instead of one clause per seat."
Draft rule (magistrate): "An implementation brief that installs a ruling
lists every ruled clause (quoted phrase, ruling file:line). The seat's FINAL
report carries a clause→assertion map: for each clause, the test method name
(file:line) whose assertion FAILS when that clause is violated, or NOT PINNED
with the reason. The refuter fan-out is launched only after the magistrate
has read the map; a NOT PINNED row is a finding the refuters receive."
Proposed homes: `docs/agent_playbook.md` Mission M0 one line; the codex
brief header contract in `docs/contracts/bridge_protocol.md` §1 (check
whether a report-shape field exists that could carry the map); a shape test
is NOT proposed (the map lives in scratchpad reports, not the repo).

Q2 — ruling 171a R-10 (:124-129): "Two seats plus the synthesis carried
'producer/consumer sets equal' from prose into draft contract text without
opening a committed receipt. The pre-transaction 'decided ≠ done' sweep gains
one line: any cross-pack equality clause is checked against one committed
receipt pair."
Draft rule (magistrate): "The S9-shape pre-transaction sweep (T26 item 1,
'record as a standing pre-window row') gains one check: every clause in a
contract or ruling that asserts equality of a value ACROSS packs or units
(producer vs consumer, floor vs contrast, unit A vs unit B) is checked by
opening one committed receipt pair and comparing the named field; a clause
with no receipt pair yet is recorded UNVERIFIABLE, never assumed."
Proposed home: the sweep's METHOD.md (a new step) and the standing pre-window
kernel row's acceptance evidence.

## Facts (bench-verified by the magistrate 2026-09-02; re-verify any you rely on)

- The T26 item-1 verdict (2026-08-27, PR #231) ruled "record as a standing
  pre-window row" for the S9-shape sweep. On 2026-09-02 the kernel
  (docs/process/state_kernel.json) held NO such row, no `open (installs via
  …)` form in the decision log, no status-vocabulary test, and the three
  other T26 verdict mechanisms were also absent (no PR template, no
  gate-ledger job, no 600 s liveness conjunct in joulewise/arm_readiness.py —
  its :6477-6479 comment still calls the bound "an open magistrate item").
  The install is in flight as kernel row T26-RULING-INSTALL-01 (branch
  feat/2026-09-02-t26-install; not on main yet). This is context for Q2's
  home, not a question for you.
- Q1 evidence: four seats across three rounds each found ONE instance of
  the same class — a ruled clause (P-5 binding) or ruled word (`PASS`)
  with no assertion that bites it. Opus 159 §A is the map that would have
  surfaced all four at once; it took the fourth seat to produce it.
- Q2 evidence: the 171 synthesis's draft D-131 text carried "producer and
  consumer sets equal"; the committed v3 receipt pair shows floor and
  contrast units with different `config_set_sha256` values, so the clause
  as drafted would have refused every real floor→contrast binding. The
  ruling corrected it (171a :96-104 "not required to be equal") before
  installation.
- Cost side: a clause→assertion map for the projection-02 ruling was ~110
  lines (159 §A); the equality check is one field comparison per clause.
- The repo already has an in-brief precedent for Q1's shape: the seat
  brief for ruling 171a requires a "Change" section listing every ruled
  clause R-1..R-8 with CONFIRMED (file:line) or NOT DONE (why) — a
  clause→SITE map, not a clause→ASSERTION map. Decide whether Q1 is a
  genuinely new rule or an amendment of that section's required content.
