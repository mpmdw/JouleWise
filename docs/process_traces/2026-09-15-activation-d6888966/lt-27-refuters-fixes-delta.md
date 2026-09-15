# lt-27 — Transactional installer: refuters, two fix rounds, delta. Head `3b339ac9`

Written 15:41 PDT 2026-09-15 (clock read).

## Branch `feat/2026-09-15-install-windows-transactional`

| Sha | What |
|---|---|
| `8f334b8f` | D9 operator docs (T2) |
| `e867dee9` | the three-valued fake launchctl (the instrument) |
| `6dc86461` | the system-interpreter import guard (R5) |
| `490be1a3` | **the engine** (D1–D8/D10) |
| `96dee838` | fix round 1 — contract-refuter findings |
| `3b339ac9` | fix round 2 — the oracle correction |

## THE ACCEPTANCE, lead-verified at the bench (not taken from any seat)

```
class_1: NO
class_2: NO
```

I ran `/tmp/iw-txn-final-evidence/reproduce.py` myself, three times across the
round, most recently at `3b339ac9`. The output that matters most, because it is
the exact defect that killed the previous design — `bootout` rc 1 with `print`
rc 9:

```
{"case": "class_2_uninstall", "rc": 4, "loaded": ["com.joulewise.night"],
 "plists": ["com.joulewise.night", "com.joulewise.night.deadman"],
 "bootout_rc": 1, "print_rc": 9}
```

**rc 4 with both plists RETAINED.** The old shell exited **0** having deleted
both while the job was still loaded. The class-1 exploit cases now return rc 2
with zero labels loaded, and the mandated `control_cleanup_*` cases return rc 0
with both loaded and a post-gate clock read BEFORE the close — the control
passes and is correctly not class 1.

## Refuter round

**Contract lens** (pid 45351): `class_1: NO`, `class_2: NO`, with three
findings — a literal I1 bypass (`--help` exiting 0 through argparse), runbook
drift, and assertions lost in the port.

**Execution lens: FAILED THREE TIMES and produced no attack coverage.** Attempt 1
was interrupted mid-session; attempt 2 died with a wrapper error writing its
out-file; attempt 3 was defeated by its own harness (a git-archive snapshot
without Git metadata errored all 46 installer tests, a 180 s limit killed the
transaction module, a 0.12 s launchctl timeout broke its class-2 harness). Same
signature three times: **the seat's harness setup defeats the seat before it
attacks.** Per the standing discipline I did not spend a fourth — the next spend
after two same-signature failures is not another attempt.

**What I did instead, because rule 1 makes this mine anyway:** ran the
acceptance script myself at the bench, and relied on the delta auditor (below)
for the independent execution attacks, which it delivered — 473 cases including
360 INT/TERM/HUP/SIGKILL cuts. **The execution-lens gap is recorded as OPEN**:
no seat independently reproduced the full attack matrix at the refuter stage,
though the delta covered the same ground afterwards.

## Fix round 1 (`96dee838`)

FIX-1: argparse's automatic help exited 0 without passing the commit predicate.
It installs nothing, so never a safety defect — but the shell's `usage()` exits
2 and D9 requires today's exit codes. Automatic help disabled; `--help`, `-h`
and unknown flags all exit 2; a test now asserts no path reaches exit 0 without
the commit predicate, naming uninstall's exit 0 as the one D7 exception rather
than excluding it silently.

FIX-2: runbook drift, **the engine right in all three cases** — the single
commit predicate rather than per-bootstrap checks, where `liveness_unknown`
actually comes from, three missing refusals, and a **fourth outcome** the table
omitted (failed restoration leaves recovery files and returns 1, not the
retained 4). The table now names four outcomes honestly.

FIX-3: assertions lost in the port, restored into the **shared oracle every cell
calls** rather than into one cell, so coverage cannot be lost again by adding a
cell.

## Delta re-audit (fresh Astra xhigh, pid 88570)

`class_1: NO`, `class_2: NO`. **Must-die: 31 RED, 0 SURVIVED, no new
survivors.** 473 executed attack cases: six print faults across ten call sites,
rc-0-but-still-loaded bootouts, restore errors, 360 signal and SIGKILL cuts, 24
persistent-fault uninstall-twice cases. All four outcomes executed and matching
the table: committed 0, restored 3 with bytes and mtime, retained 4, failed
restoration 1.

Isolated reversions: FIX-1 RED (8 failures); FIX-3 examined assertion by
assertion — all 23 shared assertions individually removed, seven negative
witnesses RED at head and SURVIVING with the check removed. **FIX-2's docs-only
reversion left `docs_freshness` GREEN — "worthless as coverage for these prose
fixes",** which is honest and expected: freshness tests do not read prose
semantics.

### Its one finding, and why it mattered more than its label

`should_fix`: after a SUCCESSFUL bootout, `print` rc 9 is UNKNOWN even though
both markers are absent, so the correct rollback returns 4 with the label
unresolved — but the **new oracle expected `loaded=0`**, deriving its
expectation from MARKER EXISTENCE rather than from the QUERY OUTCOME.

That is D2's abolished assumption, quietly re-imported into the instrument built
to catch it. A wrong oracle does not fail loudly; it hides the next real defect.
This is the same shape as every defect in this lane's history — trusting a
convenient observable over the one the design says is authoritative.

## Fix round 2 (`3b339ac9`)

Expectations now derive from the query outcome, never from marker existence;
**60 absent-plus-UNKNOWN cells** added across the rollback and uninstall paths.
**The proof the fix is real:** against an engine mutated to treat UNKNOWN as
ABSENT, the corrected oracle FAILS with 60 failures (rollback 4 != 3, uninstall
4 != 0) where the previous oracle passed. 32 shared-oracle assertions preserved,
3 added; acceptance unchanged.

## Open

- **Row 6 (fresh Opus counter-review), row 9 (sharded full-suite replay), row 10 (fresh-eyes), and the ledger/PR-body successors** are not done.
- **A delta on fix round 2 itself** is not done (it is test-only and I re-ran the acceptance and must-die myself, but the discipline says every round gets one).
- **The execution-lens refuter gap** above.
- **The `tests/test_run_night.py` scope grant** — four stale caller failures keep the tree red.
