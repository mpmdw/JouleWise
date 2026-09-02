# Sol 241 final-head fresh pass (file 18, @ 162049bd) — magistrate disposition 2026-09-02

Envelope: `semantic_status=findings`, `completion=complete`, wrapper
`run_status=OK rc=0 scope_action=passed` (the worktree held no magistrate
untracked files this time). Verdict `SHOULD-FIX 2`, `NIT 1`; "code, kernel,
delta cures, and required checks pass". Nothing applied silently; each finding
was replicated at the bench before the cure.

| Finding | Replicated | Disposition |
|---|---|---|
| F1 (should-fix) — `2026-09-02-process-rules/README.md:5-6` cites three `file:line` anchors that no longer measure their targets (`tests/test_docs_freshness.py:313` blank, clause-map tests at `:670`/`:710`; `docs/decision_log.md:10351` is the smoke-corpus trace, the Q2 amendment is at `:10355`; `:10567` is a dependency sentence, the Q1/Q2 summary at `:10583`) | yes — `sed -n 313p` blank; `grep -n "def test.*clause"` → 670/679/710/722/729; `grep -n "AMENDED (cross-artifact equality"` → 10355; `grep -n "Cold gate 2026-09-02 (process rules"` → 10583 | ACCEPTED, cured at the bench with DURABLE anchors instead of fresh line numbers: test function names, the bridge_protocol §1 bullets, the agent_playbook M0 grep, and the two decision-log paragraph openers. Line numbers drifted within one day and drift again at every merge of main; the README now says so. |
| F2 (should-fix) — `MAGISTRATE-NOTES.md:26` promises a bench commit "below" but the Bench-commits section lists only `d8451daa`/`f84be217`, and the displayed `git log main..HEAD` output stops at `f84be217` (omits `10845c14`, `c05cf181`, `162049bd`) | yes — the section and the log block read as Sol describes | ACCEPTED, cured at the bench: row 26 names `c05cf181` (and `162049bd` for the luna cures); `git show --stat` blocks added for `c05cf181` and `162049bd`, `10845c14` named as custody-only; the branch log re-executed at `162049bd` and labelled as such. The commit landing this cure cannot name its own hash; the PR #273 gate ledger names the head. |
| F3 (nit) — `MAGISTRATE-RULING-process-rules.md:8` names the packet `coldgate-process.md`; the custodied file is `PACKET-coldgate-process.md` | yes — `test -e` old → 1, new → 0 | ACCEPTED as a DATED ADDENDUM on the ruling (custodied rulings are corrected by addendum, not body edit — PD-1); the sealed body is unchanged. |

Signature check (rule 11 / charter §3): F1–F3 are stale custody-index
anchors and ledger omissions — a new signature on this lane (rounds 1–2 were
kernel/test/contract defects; luna 238 was a date gloss, an evidence block,
and a provenance line). No same-signature trigger; no cold gate. A fresh pass
by a different model over this cure commit is required by operation-loop §5
before merge.

## Executed evidence

```
$ cd /Users/edr/code/JouleWise-wt-t26-a
$ sed -n 313p tests/test_docs_freshness.py | wc -c
       1
$ grep -n "def test.*clause" tests/test_docs_freshness.py
670:    def test_custodied_impl_reports_carry_clause_map(self) -> None:
679:    def test_clause_map_mutations_and_per_row_escape(self) -> None:
710:    def test_bridge_protocol_clause_map_pins_s1_and_s2(self) -> None:
722:    def test_bridge_protocol_clause_map_s2_deletion_bites(self) -> None:
729:    def test_bridge_protocol_clause_map_s2_rewrap_passes(self) -> None:
$ test -e docs/process_traces/2026-09-02-process-rules/coldgate-process.md; echo $?
1
$ test -e docs/process_traces/2026-09-02-process-rules/PACKET-coldgate-process.md; echo $?
0
```
