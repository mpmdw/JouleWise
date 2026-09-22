# 02 — A266 ARM-VOCABULARY-GLOSSARY-01: first-use pass over the four passages

Lane: A266, registered by the cold gate's packet-06 ruling (activation
ce7c57a9, `06-coldgate-packet-retained-root-round3-return/10-coldgate-fable-ruling.md`
§Q3, "Deferred to a registered follow-up lane"). Seat: implementation seat of
activation 32fd437d, worktree `/Users/edr/code/JouleWise-wt-a266-32fd437d`,
branch `docs/2026-09-22-arm-vocabulary-glossary`, based on `d45378c6`.
Docs plus one code comment; no behaviour change.

The three terms the gate deferred here are **"arm"/"arming"**, **"retained"**
(of a night root) and **"chain is open"/"open chain"**. The six terms the gate
itself glossed on 2026-09-21 (plan span, timing constants, entry checkout,
older sibling plan, `custody_root`, session root, plus the "diagnostic"
parenthesis) are untouched: this record confirms they are still present
verbatim and still PASS.

## 0. Which table is THE Terms table, and why

The runbook has two glossary surfaces:

- `docs/phase_2/derivation_night_runbook.md:155`, `## Terms, glossed here
  because every later section uses them` — a prose bullet list that BUILDS
  campaign-science terms (slot, session, registration, epoch, blind, dead-man,
  wrapper, night root, fence…).
- `docs/phase_2/derivation_night_runbook.md:3262`, the `| Term | Built at |
  One-line meaning |` table under `## 8. First-use table` — "Every term of art
  in this file, where it is built, and in one line what it means."

**THE Terms table for the arm vocabulary is §8.** Four pieces of the tracked
text decide it, none of them this seat's invention:

1. It is the only one of the two that is a table, and its first column is
   literally `Term`. The ruling's word was "the runbook's Terms table"; the
   kernel row's deliverable says "rows".
2. The runbook itself sends the reader there for exactly this vocabulary:
   §0.6 step 3b (`derivation_night_runbook.md:650`) says "Terms are defined in
   the first-use table (§8)", and that step is the arm-time census.
3. `docs/process/NIGHT_HANDBACK.md:179` already says "the runbook's §8 owns the
   term definitions" — a cross-document pointer that predates this lane, so
   pointing the other three passages at §8 creates no second home.
4. §8 already carried a partial `arm / arm-time census` row (one clause,
   "Publishing a plan and installing its night/report jobs"), which is what the
   kernel row's "add or COMPLETE rows" describes. §Terms has no arm row at all.

§Terms and §8 are one glossary in two parts — §Terms builds, §8 indexes, and
§Terms' own closing line (`:262`) says so ("A first-use table for every term of
art in this file is at §8"). This lane therefore wrote the three definitions
into §8 only and added nothing to §Terms: one home, no third home, no
duplicate. §8 sits at the end of a 3300-line file, which would violate
"definitions precede uses" on its own; the pointers required by the acceptance
are what repair that, and each pointer is at the first use.

## 1. FIRST-USE TEST, after the edits

Reader model: technical, has never seen this repository; lands on any one
passage alone and may follow only the pointers that passage gives.

Passages, at the branch head after the edits:

- **P1** `docs/contracts/evidence_night_entry.md:220–261` (contract item 4).
- **P2** `docs/phase_2/derivation_night_runbook.md:699–760` (§0.7 heading
  through the `Source:` paragraph).
- **P3** `docs/process/NIGHT_HANDBACK.md:303–346` (the pre-check step), plus
  the two handback sites this lane edited because the arm vocabulary's first
  uses in that FILE are there and not in the pre-check step: the header
  paragraph `:3–11` and the `**Census.**` paragraph `:245–251`.
- **P4** `joulewise/evidence_night.py:699–711` (the comment block above
  `TERMINAL_NIGHT_RECORDS`).

| Term | Passage(s) | Verdict | Sentence of first use, and why |
|---|---|---|---|
| "arm" / "arming" | P2, P3 | **PASS (pointer at first use)** | P2's first use is the §0.7 heading itself ("Nothing else is armed"), which cannot carry a citation, so the section's first body sentence is now "Three project-wide terms this section turns on — to **arm** a night, a **retained** root, and a root whose **chain is open** — are defined in the first-use table (§8)…" (`:701–704`). P3's first use is "before every armed night" (`:4`), now followed immediately by "(**arm**, **arming**: defined in the derivation-night runbook's first-use table, `docs/phase_2/derivation_night_runbook.md` §8 …)". The §8 row builds the mechanism: publish the approved plan into its night root, install the two named launchd jobs from it, nothing armed until both are loaded and accepted. Not used in P1 or P4 (checked; see §2 E4/E5). |
| "retained" (of a night root) | P1, P2, P3, P4 | **PASS** | P1 is the binding definition and builds it in place: "…classifies its root as retained" (`:228`) after the enumeration of the record names, then "Classifying a root `retained` certifies only that a terminal record exists and that … the plan's span [was] inactive" (`:256`). P2's first use is the §0.7 heading, covered by the new pointer sentence, which also names item 4 as binding. P3's first use in the root sense is "Retained production roots remain discoverable" (`:248`), now "(**retained**, of a night root: item 4 of `docs/contracts/evidence_night_entry.md` is the binding definition, indexed in the runbook's §8)". P4's first use is "a retained root whose plan span is still active" (`:705–706`), now preceded in the same comment by "\"An open chain\" and \"retained\" below are defined by item 4 of docs/contracts/evidence_night_entry.md". |
| "retained" (ordinary English, "kept") | P3 | PASS (different sense, correctly readable) | `NIGHT_HANDBACK.md:14` "the directory retaining that night's records", `:80`/`:107`/`:126` inside the byte-exact ARM-RETRY-POLICY block ("Committed, retained, unknown …", "retained even if normally unreachable", "`retained prior plist`"), `:222` "Insufficient retained evidence". None is the classification: each reads as the ordinary verb/adjective in its own sentence and none is applied to a discovered night root. The classification sense's first use is `:248`, which now carries the pointer. The policy block is pinned byte-for-byte by `tests/test_arm_retry.py::test_both_document_blocks_are_exact` and was not touched. |
| "chain is open" / "open chain" | P1, P2, P4 | **PASS** | P1 now NAMES the term where it already built the rule: "A root whose `night/chain.started` is a regular file without a regular `night/chain.exited` — its chain is open — is ACTIVE and refuses" (`:222–223`). That is what makes "contract item 4" a usable pointer target for the phrase. P2's first use is the new pointer sentence (`:702`); its rule use, "what stops an arm is any root whose chain is open" (`:731`), follows it. P4's "an open chain takes precedence over every marker" (`:704`) is preceded by the same comment's pointer to item 4. Not used in P3 (zero occurrences, E3). |
| "plan span" / "span is active" | P1, P2, P4 | GLOSSED (cold gate 2026-09-21, unchanged) | P1 `:235–244`: "The plan span is the interval in which the watchdog treats a plan as live, computed from that plan's own `t0_epoch_s` and `window_max_s` with the constants `PLAN_LEAD_S` (480 s) …" — the full rule, replicable. Present verbatim (E6). |
| "timing constants" | P1, P2 | GLOSSED (cold gate, unchanged) | P1 `:236–238` names the four constants in the plan-span sentence before "with the timing constants of the entry checkout". |
| "entry checkout" | P1, P2, P4 | GLOSSED (cold gate, unchanged) | P1 `:247–249`: "the timing constants of the entry checkout, the git checkout whose `joulewise/evidence_night.py` is executing rather than the measurement clone the plan names". |
| "older sibling plan" | P1 | GLOSSED (cold gate, unchanged) | P1 `:250–252`: "…an older sibling plan, another `<roots_under>/night-custody/*/night_plan.json` beside the candidate's written by an earlier checkout". |
| `custody_root` | P1, P4 | GLOSSED (cold gate, unchanged) | P1 `:253–255`: "whose `custody_root` field (the plan's own record of the directory it must live in) does not name its own directory". P4 says "custody root" as a plain noun for the directory, immediately after "a discovered custody root" — and now points at item 4 for the classification words. |
| "session root" | P3 | GLOSSED (cold gate, unchanged) | P3 `:318–322`: "Let `ROOT` be the PID of the session root: the interactive `claude` process this session is running in, which the census recognises by executable basename `claude` and an argv carrying no `-p` or `--print` …". |
| "foreign" | P3 | GLOSSED (cold gate Q2, unchanged) | P3 `:304–310`: "the census lists every process whose full command line matches `codex`, `claude` or `t3` … and classifies each listed process that is neither the checking process nor one of its ancestors as foreign". |
| "diagnostic" | P3 | GLOSSED (cold gate, unchanged) | P3 `:342–346`: "never relabel it \"diagnostic\" (a diagnostic is the census's own report that it could not observe something: …)". |
| "terminal record" / "terminal state" | P1, P2, P4 | GLOSSED | P1 enumerates the names (`night/courier.sent`, `night/result.json`, `night/chain.exited`, the refusal names) before "classifies its root as retained". P2's "whose records show no terminal state" (`:732`) is now covered twice over: the §0.7 pointer sentence sends the reader to §8, whose new `retained` row lists the four record families, and to item 4. |
| "marker" | P1, P2 | GLOSSED | P1 "the record lists every marker found" (`:229`), directly after the enumeration. |
| "check" (the command) | P1, P2, P3 | GLOSSED | P2 shows the executable form at first use: "`python -m joulewise.evidence_night check --candidate STAGING`" (`:733–734`). P3 names the same command in the arm procedure (`:291–301`) before the pre-check step uses the bare word. |
| "night agents" / "installed night plist" | P2 | GLOSSED by the mechanism beside it | P2 `:731–732` "whose night agents are installed", then `:734` names the `night_agents` item of the same check, and `:721–723` in the same section states the second fence: "the watchdog reads the `--plan` paths in both installed night plists". Two jobs, and their labels, are in §8's arm row, which the section's first sentence points at. |
| `Refused:` | P2 | GLOSSED | "a `Refused:` exit" followed immediately by the three-sentence rule the cold gate authored on what raises it (`:745–752`). |
| `roots_under` | P2 | GLOSSED | The dict literal in the manual command plus "one row per `/Users/edr/night-custody/*/night_plan.json`" (`:740–743`). |
| "MCP helpers" / `codex mcp-server` | P3 | GLOSSED | "Every child whose command line contains `codex mcp-server` is a helper" (`:324–325`). |
| `ACTIVE` / `UNKNOWN` | P1, P2, P4 | GLOSSED | P1 assigns both by rule in the sentences that introduce them; P2 says "(contract item 4: `ACTIVE` and `UNKNOWN` refuse)" at first use (`:735`). |
| "arm-time census" | P3 | GLOSSED | P3 `:246` "The arm-time census classifies every `[c]odex|[c]laude|[t]3` match by ancestry"; the handback's own definitions paragraph (`:54`, ruled A172 text) also carries it, and §8's completed row now defines it as "the separate process check immediately before that publication". |

FAILS: **none**. Every row is PASS or GLOSSED.

Two observations recorded rather than acted on, both out of this lane's
WRITE_SCOPE and neither a FAIL:

- `NIGHT_HANDBACK.md:54` (and its verbatim twin at
  `derivation_night_runbook.md:1855`) glosses "An **arm attempt** is one
  attempt to publish an approved candidate and install its two scheduled jobs."
  That is the A172/D-180 attempt-counting unit, not a gloss of the bare
  project-wide word "arm", and it agrees with §8's completed row. It is ruled
  text, duplicated across two documents, and was left untouched.
- `NIGHT_HANDBACK.md:58` glosses "plan span" locally ("the agent-free interval
  beginning eight minutes before `t0` …"), which now coexists with contract
  item 4's full rule. The cold gate glossed item 4 on 2026-09-21 and did not
  disturb this sentence; "plan span" is not one of this lane's three terms.
  Flagged for a future sweep, not changed here.

## 2. Executed evidence

All commands run in the worktree at the branch head, after the edits.

E1 — first use of each term inside runbook §0.7 (lines 699–761):

```
$ grep -niE '(^|[^a-z])(arm|arming|armed)([^a-z]|$)' docs/phase_2/derivation_night_runbook.md | awk -F: '$1>=699 && $1<=761' | head -3
699:### 0.7 Nothing else is armed, and every discoverable root is retained
701:Three project-wide terms this section turns on — to **arm** a night, a
709:Remove every `REHEARSAL_STUB` plan root before arming any real plan
$ grep -niE 'retain' docs/phase_2/derivation_night_runbook.md | awk -F: '$1>=699 && $1<=761' | head -3
699:### 0.7 Nothing else is armed, and every discoverable root is retained
702:**retained** root, and a root whose **chain is open** — are defined in the
707:discoverable prior plan root that is ACTIVE or UNKNOWN (a harvested, retained
$ grep -niE 'chain is open|open chain' docs/phase_2/derivation_night_runbook.md | awk -F: '$1>=699 && $1<=761' | head -3
702:**retained** root, and a root whose **chain is open** — are defined in the
731:chain is open, whose span is active, whose night agents are installed, or whose
```

E2 — the runbook's own pointers to §8 (existing, and the one added):

```
$ grep -n "§8\|first-use table" docs/phase_2/derivation_night_runbook.md | head
23:§1.2–§1.5, §2.1, §5, §7 and §8 carry the corresponding in-place updates.
55:sentence corrected; §7 gains the ruling's own fact row; and §8 builds
94:fact by SYMBOL and record number instead of by line number; §8 gains the desk
262:A first-use table for every term of art in this file is at §8.
650:first-use table (§8). Stop all own seats, delegated tasks and background jobs
703:first-use table (§8); for the last two the binding definition §8 points at is
```

E3 — handback first uses, and the absence of "chain is open" there:

```
$ grep -niE '(^|[^a-z])(arm|arming|armed)([^a-z]|$)' docs/process/NIGHT_HANDBACK.md | head -3
4:The magistrate rewrites the three sections below before every armed night
5:(**arm**, **arming**: defined in the derivation-night runbook's first-use
6:table, `docs/phase_2/derivation_night_runbook.md` §8, which §"Arm-time census
$ grep -niE 'retained' docs/process/NIGHT_HANDBACK.md | head -6
80:| `arm_transport` | … Committed, retained, unknown or failed-restoration outcomes stop. |
107:| `night_plan_overruns_deadman` | Completion/dead-man schedule was refused; retained even if normally unreachable. |
126:| `retained prior plist: <path>; re-run --uninstall` | A saved previous job file remains; …
222:qualifies". Insufficient retained evidence is INCONCLUSIVE, with no
248:REQUEST (ruling 87a F6). Retained production roots remain discoverable
249:(**retained**, of a night root: item 4 of
$ grep -ciE 'chain is open|open chain' docs/process/NIGHT_HANDBACK.md
0
```

(The `:80`, `:107` and `:126` rows are inside the byte-exact ARM-RETRY-POLICY
block, lines 71–147, and use the ordinary English sense; see §1.)

E4 — contract item 4 (lines 220–261), every occurrence of the three terms; no
occurrence of "arm" in the item:

```
$ awk 'NR>=220 && NR<=261' docs/contracts/evidence_night_entry.md | grep -niE 'retained|chain is open|(^|[^a-z])arm([^a-z]|$)'
4:   `night/chain.exited` — its chain is open — is ACTIVE and refuses. Otherwise
9:   `calibration-refusal.json.*.json`) classifies its root as retained; the
25:   up to the minute) plus `COURIER_LOCK_FRESH_S`. A retained root whose plan
37:   has no fixed root count. Classifying a root `retained` certifies only that a
```

E5 — the code comment as it now stands:

```
$ sed -n '699,711p' joulewise/evidence_night.py
# Night records that classify a discovered custody root. "An open chain" and
# "retained" below are defined by item 4 of
# docs/contracts/evidence_night_entry.md, their binding definition; the
# derivation-night runbook's first-use table (section 8 of
# docs/phase_2/derivation_night_runbook.md) indexes both. Several families can
# coexist (a refusal written mid-chain, then chain.exited); an open chain takes
# precedence over every marker, and a retained root whose plan span is still
# active by the watchdog's rule is ACTIVE too. The installer refuses re-admission
# on the same names (night_agent_install); the refusal names come from the
# driver's own run_night._refusal_paths, and the span rule from the watchdog's
# plan_span_active — both entry-checkout modules, evaluated with the entry
# checkout's constants.
TERMINAL_NIGHT_RECORDS = ("courier.sent", "result.json", "chain.exited")
```

E6 — the six cold-gate-supplied glosses of 2026-09-21 are still verbatim
(whitespace-normalized substring test over the three documents):

```
$ python3 - <<'PY'
from pathlib import Path
n = lambda p: " ".join(Path(p).read_text().split())
C, H = n("docs/contracts/evidence_night_entry.md"), n("docs/process/NIGHT_HANDBACK.md")
for name, hay, needle in (
  ("plan span", C, "The plan span is the interval in which the watchdog treats a plan as live, computed from that plan's own `t0_epoch_s` and `window_max_s` with the constants `PLAN_LEAD_S` (480 s), `COURIER_DEADLINE_S` (300 s), `COURIER_LOCK_FRESH_S` (900 s) and `DEADMAN_GRACE_S` (3600 s)"),
  ("entry checkout/sibling", C, "with the timing constants of the entry checkout, the git checkout whose `joulewise/evidence_night.py` is executing rather than the measurement clone the plan names, which may differ from the head that authored an older sibling plan, another `<roots_under>/night-custody/*/night_plan.json` beside the candidate's written by an earlier checkout)"),
  ("custody_root", C, "or whose `custody_root` field (the plan's own record of the directory it must live in) does not name its own directory, is UNKNOWN and refuses"),
  ("H1 census", H, "the census lists every process whose full command line matches `codex`, `claude` or `t3`"),
  ("session root", H, "Let `ROOT` be the PID of the session root: the interactive `claude` process this session is running in"),
  ("diagnostic", H, "never relabel it \"diagnostic\" (a diagnostic is the census's own report that it could not observe something"),
): print(name, needle in hay)
PY
plan span True
entry checkout/sibling True
custody_root True
H1 census True
session root True
diagnostic True
```

E7 — every fact asserted by the three new/completed §8 rows, verified at the
branch head by line read:

| Fact in the row | Evidence |
|---|---|
| The two launchd labels are `com.joulewise.night` and `com.joulewise.night.deadman` | `joulewise/night_agent_install.py:39` `LABELS = ("com.joulewise.night", "com.joulewise.night.deadman")` |
| `publish-install` publishes and then installs | `joulewise/evidence_night.py:1211` `def publish_install(...)`; `:1295` `os.replace(plan, target)` where `target` is `<custody_root>/night_plan.json` (`sealed_state`, `:536`); `:1303` `invoke(None)` → `installer_call` (`:945`) |
| The installer is reached through the shell script, which execs the module | `joulewise/evidence_night.py:947` builds `scripts/install_night_agent.sh --plan …`; `scripts/install_night_agent.sh:91` `PYTHONPATH="$repo" exec "$python" -B -m joulewise.night_agent_install "${args[@]}"` |
| The plan is installed from `<custody_root>/night_plan.json` | `joulewise/night_agent_install.py:588` refuses unless `self.plan_path == (Path(self.plan.custody_root) / "night_plan.json").resolve()` |
| `retained` needs a terminal record AND an inactive span | `joulewise/evidence_night.py:711` `TERMINAL_NIGHT_RECORDS`; `:714` `retained_roots`; `:725–726` markers (terminal names + `_refusal_paths` hits); `:731–732` no markers → `UNKNOWN`; `:740–742` span active → `ACTIVE`; `:743–744` the retained reason |
| `ACTIVE` and `UNKNOWN` stop the arm | `:749` verdict is `pass` only if every row is `retained`; `check` binds it at `:922` (`inspect("retained_roots", …)`) |
| An open chain is `chain.started` without `chain.exited`, and takes precedence | `:727–730` `chain_open = safe_path(night/"chain.started").is_file() and not safe_path(night/"chain.exited").is_file()`, tested before the marker branches |
| The driver claims the start once-only and records the exit | `scripts/run_night.py:526` `_claim_chain_start` opens `chain.started` with `O_CREAT|O_EXCL`; `:551` `os.replace(temporary, night_dir / "chain.started")`; `:411` `_record_chain_exit`, writing `night_dir / "chain.exited"` at `:427` |

## 3. Diff and checks

```
$ git diff --stat
 docs/contracts/evidence_night_entry.md   |  7 ++++---
 docs/phase_2/derivation_night_runbook.md |  9 ++++++++-
 docs/process/NIGHT_HANDBACK.md           | 11 ++++++++---
 joulewise/evidence_night.py              |  6 +++++-
 4 files changed, 25 insertions(+), 8 deletions(-)
```

The contract diff is three lines wider than the inserted clause because the
clause pushed the paragraph's fill: only the wrap points of the following two
lines moved, no word changed. The whole edit set is additive except that one
rewrap and the completion of §8's existing `arm` row.

```
$ python3 -m unittest tests.test_evidence_night 2>&1 | tail -3
Ran 103 tests in 181.834s

OK
$ python3 -m unittest tests.test_docs_freshness 2>&1 | tail -3
Ran 31 tests in 0.435s

OK
$ python3 -m unittest tests.test_arm_retry tests.test_night_gate 2>&1 | tail -3
Ran 107 tests in 0.796s

OK
```

(The last pair is not required by the lane but is the pin on the byte-exact
ARM-RETRY-POLICY block and on the runbook's registration/first-use prose.)

FULL_SUITE_PLACEHOLDER
