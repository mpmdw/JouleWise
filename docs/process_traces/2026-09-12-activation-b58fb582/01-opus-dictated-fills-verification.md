# 01 — Opus dictated-fills verification of commit H's inputs (2026-09-12 00:52–00:57 PDT)

Read-only Opus seat (Agent tool, model opus) over the uncommitted diff in
`/Users/edr/code/JouleWise-wt-bk-b58fb582`; the magistrate dictated the five
pre-registration fills and the inventory row, the seat re-verified each
against its primary source. Report verbatim (table) with the magistrate's
disposition after it.

| Fact | Primary source checked | Verdict |
|---|---|---|
| `[DD]` → 10 | `git log --diff-filter=A` on the prereg file: first commit `64d1d6d3`, 2026-09-10 08:43:39 -0700. Every commit touching the file (9 of them, `64d1d6d3`…`07995051`) is dated 2026-09-10; revision 2 header also says 2026-09-10. Gloss: file §"Fields filled at commit" = "`[DD]` (authoring day)"; runbook "the authoring day of the registration text itself"; runbook fact table same | CONFIRMED — no rival date exists; authoring, first commit and last edit are all 09-10 |
| `[MLX_VERSION]` → 0.31.2 | `env/mac-measurement-lock.txt:25` `mlx==0.31.2`; live-observed 0.31.2 in records 131 (`mlx_version 0.31.2 0.31.2 match`), 134 and 135 | CONFIRMED |
| `[SEQ] [DIGEST]` → 76 / `08456d50…94d7` | `configs/calibration/calibration_ledger_head.json` (worktree and `origin/main`, byte-identical). Pin last changed 2026-08-06 (`a816036f`). HEAD == origin/main == `101eeb07`; `git ls-remote` agrees | CONFIRMED — the pin in force is 76, nothing advanced it |
| `[CHAIN_SHA256]` → `b8bf5b0a…cf` | Re-ran `shasum -a 256 scripts/night_chains/calibration_derivation_only.zsh` → exact match. Runbook §0.5 demands the **tracked chain's** digest, not a wrapper's | CONFIRMED |
| (a) `preregistration_epoch_pins` on edited text | Executed: returns `('25G83', 'b762e5bf…30c5')`, exactly one hit per regex | CONFIRMED |
| (b) Placeholders / digest pins elsewhere | No test or script pins the prereg file's digest as a literal; `tests/test_issue_calibration_acceptance_generation.py:65` hashes it live; `tests/test_night_gate.py` 224/265 use path/text only. Both suites: 172 passed | CONFIRMED |
| (c) Inventory row vs `production_custody_roots` | `joulewise/arm_readiness.py:291-307`: key set exact, id unique (5 unique), notes str, `measurement_root`/`ledger_path` absolute. JSON parses, 5 rows, single trailing newline. `tests/test_arm_readiness.py`, `test_t0_rehearsal.py`, `test_rehearse_t0_unattended.py`, and the other three census tests all pass. "76-record ledger": `wc -l` canonical ledger = 76 | CONFIRMED |
| (d) Sealed-block leftovers, lines 126-262 | Only `[QUIET-MAC]` (a term of art, not a fill field); no `[A-Z_]` placeholder remains. §281 gloss retains backticked names as intended | CONFIRMED |

**ANOMALY (blocker).** `tests/test_arm_readiness_schemas.py:1694`
`test_shipped_inventory_pins_all_four_retained_deployments` hard-pins
`assertEqual(4, len(inventory))` plus the exact four-entry id→root map. The
appended row makes it fail (`4 != 5`); full file: 1 failed, 49 passed.
Runbook §0.1 forbids arming on a head whose replay is not green, so H must
also update that test (count 5 + the new id/root) and, per
`docs/contracts/pack_night_go_receipt.md` §10.3 pins table, that test is a
named §10.3 pin.

**Observation (cosmetic).** The two digest fills leave lines 139 (169 chars)
and 144 (167) inside a sealed block whose every other line is ≤124;
unwrapped, unlike the surrounding text. No line-length test exists.

## Magistrate disposition

- Blocker ACCEPTED and cured in H: the test now pins FIVE retained
  deployments (the new id→root added, count 4→5, two-line comment naming the
  night). The pin's purpose — "a retained deployment disappears" is caught —
  is preserved; the function name keeps `all_four` so the contract's
  citation by name stays resolvable (rename + contract citation update
  queued as a nit for the next docs sweep, not done at the arm). This makes
  H a docs+config+one-assertion commit; it lands as the direct bookkeeping
  commit file 11 §"Exact activation Git sequence" prescribes, after the
  focused suites and with CI at H required before the arm.
- Cosmetic line length: left as is. Re-wrapping lines inside the sealed
  registration text would move sealed line breaks for no reader benefit;
  the digests are the fills the block reserved blanks for.
- Everything else CONFIRMED; no fact changed.
