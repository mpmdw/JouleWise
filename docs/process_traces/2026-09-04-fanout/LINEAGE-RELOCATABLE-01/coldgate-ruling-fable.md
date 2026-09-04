# Cold-gate ruling — LINEAGE-RELOCATABLE-01 (Fable cold seat, 2026-09-04)

Seat: claude-fable-5-1, single non-interactive session, no subagents, no
background tasks. Sitting opened 22:22 UTC, probes closed 22:31 UTC.

## 1. Contamination disclosure

Auto-loaded into context before any duty ran: `~/.claude/CLAUDE.md` (global
rules), project `CLAUDE.md`, and the memory index `MEMORY.md` (one-line
pointers only). Used as authority: none. Not read: `CLAUDE.local.md`,
`RUN_STATE.md`, `TASK_QUEUE.md`, any council log, run report, or narrative
state doc. Read set: the packet, its eleven exhibits, the charter registry at
`cc56a9a7` (trust anchor only), and the pinned tree at `b420a45a` via a
scratch worktree.

## 2. Digests and validator receipt

| Object | Expected | Observed |
|---|---|---|
| charter `docs/process/coldgate_charter.md` | `099de884…c95d81` | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` match |
| packet `coldgate-packet-lineage.md` | `8f63f448…599eaf` | `8f63f44864e4cabce723fcab3d85332a7b455bda4f94b78928f6922c6c599eaf` match |

Validator: `scripts/validate_gate_packet.py` → `"result":"PASS"`, rc=0,
schema `coldgate-validator-receipt/v2`, all 11 exhibits expected==observed,
manifest sha256 `a701b8f2…41ebdc`. All 11 exhibits also re-hashed from
`git show b420a45a:<source>`; every one matches its manifest digest
byte-for-byte. Branch tip during this sitting was `9830cb21` (one commit past
the pin); this ruling covers `b420a45a` only.

## 3. Executed evidence

Scratch worktree `/private/tmp/cold-lineage-36459` at `b420a45a`
(`git rev-parse HEAD` confirmed). Removed after the sitting.

| # | Probe | Result |
|---|---|---|
| E1 | Required replay (§7 command, verbatim) | rc=0, `Ran 11 tests in 9.102s`, `OK`; tail identical to the packet's 11-line tail |
| M1 | `_relocation_target` symlink refusal disabled (C1 9147) | KILLED by `test_relocation_target_symbolic_link_keeps_launch_binding_mismatch` |
| M2 | `_read_exact_launch_reference` skips byte digest when `read_path` given (C1 9054) | KILLED by `test_relocated_tamper_keeps_launch_binding_mismatch` |
| M3 | bundle path drops `relocation.source_locator_sha256` comparison (C1 11017-11021) | KILLED by `test_relocation_source_locator_digest_is_mandatory` |
| M4 | direct API loads raw carrier instead of refusing (C1 10294-10298; the DR-01 counterfactual) | KILLED by `test_direct_relocation_refuses_carrier_without_locator_authentication` |
| M5 | pack mismatch refuses only on `content`, ignores location kinds (C1 9540) | KILLED by `test_relocated_repository_relative_move_keeps_launch_binding_mismatch` |
| M6 | carrier `repository_root` consistency check disabled (C1 9235) | SURVIVED (all 11 pass) |
| M7 | post-hoc guard on private `_relocation` + `require_current_boot`/`require_completion_absent` disabled (C1 10304) | SURVIVED |
| M8 | `scripts/launch_window.py` `lifecycle()` carrier guard disabled (C2 281) | SURVIVED |
| P0 | fixture relocated, explicit carrier | ACCEPTED |
| P1 | one byte changed in the issued consumption receipt, sidecar regenerated | REFUSED `launch_consumption_invalid: consumption digest reference disagrees` |
| P2/P7 | one byte changed in the issued arm receipt (`GO`→`G0`; then a benign id byte), sidecar regenerated | REFUSED `launch_consumption_invalid` (predecessor invalid; predecessor reference disagrees) |
| P3 | root locator rewritten with a forged lineage, sidecar regenerated, carrier digest matched to the forgery | REFUSED `launch_binding_mismatch: bundle launch lineage differs from its authenticated root locator` |
| P4 | carrier `window_plan_root` retargeted at a sibling copy whose `window.env` differs by one byte | REFUSED `launch_binding_mismatch: bound launch artifact bytes changed` |
| P5 | empty commit on the clone (new HEAD, identical pack tree) | ACCEPTED, returned `pack_sha256` equals the fresh committed tree digest |
| P6 | carrier `custody_pack_root` retargeted at a copy whose basename differs from the pack | REFUSED `launch_binding_mismatch: … basenames differ` |
| P8 | `launch_window.lifecycle()` called with a carrier argument | REFUSED `launch_binding_mismatch: launch-lineage relocation is post-hoc only` |

Scratch tree was `git status` clean after every mutation. Nothing installed;
no claude/codex launched; `~/night-custody` untouched.

## 4. Q-NR1 — authority of the carrier: AFFIRM (both parts)

Carrier fields are exactly `schema_version`, `source_locator_sha256`,
`repository_root`, `campaign_pack_root`, `custody_pack_root`,
`window_plan_root` (C1 729-736; exact key set enforced at 9172). Every
non-digest field is consumed only as a read target: custody roots select
where the consumption, arm, start, settle and completion receipts are read
(C1 9497-9500, 10339-10343, 10527-10532, 10553-10558, 10614-10618), the
window root selects `window.env`/`window-chain.zsh` (10461-10486), the pack
root selects the clone whose committed tree is re-hashed (9519-9525,
5263-5285). Each artifact read through a carrier target is then compared to
the issued reference digest (9054-9058 for manifest/env/chain; 10349,
10538, 10565, 10667 for receipts; 9540-9553 for the pack). The only carrier
field with evidential shape, `source_locator_sha256`, must equal the
authenticated locator digest (11019-11021) and so can only confirm, never
authorize. `repository_root` is never read after loading (M6 survives;
grep finds no use) — it can authorize nothing. The returned lineage is a
deep copy of the caller's issued object (10714), no reference is rewritten.
T1 bites: the positive at 1806-1827 first requires the absolute route to
refuse, then requires exact lineage equality, exact consumption digest and a
fresh committed-tree digest; M2/M3/M4/M5 show these and the locator tests
fail under a reference-rewriting or authoritative carrier. No carrier field
or code path can authorize changed evidence bytes.

## 5. Q-NR2 — post-hoc boundary and refusal legs

1. Live campaign replay: AFFIRM. C1 10852-10856 refuses every carrier before
   any read; T1 1829-1838 pins code and detail; replayed in E1.
2. Live launch: AFFIRM, with AMEND. C2 244-249 refuses in `launch()` before
   input assembly; C2 280-285 refuses in `lifecycle()`; option exposed at
   C2 61. T2 82-90 pins only `launch()`. Executed: P8 confirms `lifecycle()`
   refuses at this head, but M8 shows no named test pins it. Amendment: add
   a `lifecycle()` twin of T2 82-90 (non-blocking; the refusal exists).
3. Tamper: AFFIRM. T1 1840-1843; refusal at C1 9054-9058; M2 killed.
4. Committed-pack-change: AFFIRM. T1 1845-1859; refusal at C1 9540-9544
   via `_pack_mapping_mismatch_kind` "content" (7068-7075).
5. Repository-relative-move: AFFIRM. T1 1861-1879; refusal at C1 9548-9553
   via projection compare 7120-7127; M5 killed.
6. Swapped-chain: AFFIRM. T1 1881-1895; start read with
   `expected_kind="launch_start"` (C1 10534) rejects a settle body →
   `launch_consumption_invalid` preserved.
7. Traversal: AFFIRM. T1 1897-1900; `_require_relative_path` (1359-1370)
   raises "escapes its namespace", wrapped to `launch_binding_mismatch` at
   C1 9200-9203; `_relocation_target` and `relative_to(base)` are second and
   third layers (9137, 9206-9210).
8. Symbolic-link: AFFIRM. T1 1926-1930; refusal at C1 9147-9150; M1 killed.

## 6. Q-NR3 — every newly accepted state is same-byte/same-pack: AFFIRM

R4 177-195 re-executed via E1, not accepted on report. Acceptance route
enumerated end to end in C1: locator (10758-10775 sidecar-bound primary,
11011-11021 bound to bundle stamp and carrier), consumption (10349), arm
(9511-9516), pack content and repository-relative location (9519-9553),
manifest fixed location and bytes (10405-10425), window artifacts fixed
locations and bytes (10437-10486), argv (10488-10511), start/settle fixed
locations, digests, identities, predecessors, ordering (10513-10610),
completion (10643-10701), locator role/path vs arm context (11035-11047).
Counterexample search P1-P4, P6, P7 and the six named legs: every one-byte
change to an issued artifact, every different committed tree, every
different repository suffix, and every retargeted carrier root refused with
the artifact-specific code. P5 shows the one state accepted only because a
carrier is present: the same committed pack tree at the same
repository-relative suffix under a different absolute clone path, which is
the relocation A0 permits. Scope note (not contrary): under 7076-7089 a
pack whose registry generation is not successor-relative refuses with
"archival_location" on any absolute-path change, so relocation is accepted
only for successor-relative packs. Fail-closed; consistent with NR-3.

## 7. Merge verdict: AFFIRM — the landing at `b420a45a` satisfies A0 NR-1..NR-3

No blocker. Non-blocking amendments, each with the counterfactual that
would make it bite: (a) T2 twin for `lifecycle()` (counterfactual: M8);
(b) either test or remove the `_relocation`+`require_current_boot` guard at
C1 10304 (counterfactual: M7; unreachable today because only 11033 passes
`_relocation`, with `require_completion` alone); (c) either use or drop the
carrier `repository_root` field (counterfactual: M6). R5's residual note
stands: no analysis/reduce caller yet forwards a carrier; that is plumbing
outside this gate, not a soundness gap.

## 8. Packet hygiene

No omitted contrary evidence found; R5 DR-01 and its cure R6 are both in
the read set and the cure is verified by M4. §5 part 2 bundles two code
sites under one test citation (T2 pins one of them) — a mild compound; ruled
above with the split. No unsupported claim: every cited line range resolved
to the described code at the pin. The packet correctly disclaims merge
authority; this seat rules on satisfaction of A0 only.

## 9. NOT EXECUTED

- R4's "removing the relocation dispatch makes the second half repeat the
  first refusal" — not re-run as stated; covered indirectly by M2-M5 (the
  positive and negatives fail when the acceptance route is weakened).
- Repository-wide suite, hardware, campaign, or quiet-machine runs — out of
  gate scope per packet §7.
- Commit `9830cb21` (past the pin) — outside this ruling by charter;
  `git diff --stat b420a45a..9830cb21` shows it adds only the packet, its
  exhibit copies and the derived receipt (13 files, no code or test edits).
