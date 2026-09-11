# 144 — PR #316 FINAL-HEAD FRESH-EYES, pass 2 (gate ledger row 10)

- Tree: `/Users/edr/code/JouleWise-wt-s8-night-inputs` — STRICTLY READ-ONLY.
  `git status --porcelain` empty at entry and at exit; no git state changed.
  All scratch writes went to `/tmp/row10pass2/`. `/Users/edr/code/JouleWise`
  and `/Users/edr/night-custody` were never touched.
- HEAD reviewed: `bc1d7ef9f421d75b7ed0f92d1598dedef5179c66`
  ("docs: derivation-night runbook revision 5 — every variable built before use …")
- Base of the delta: `1dd40460`
- Reviewer: Opus 5, fresh eyes (row 10, pass 2)
- Inputs consumed: contract review 141, writer report 142

## VERDICT: **CLEAN** (row 10 PASS)

Every named finding of review 141 that revision 5 claimed to close — **S-1, S-2,
S-3, S-4, S-7 and the term-flip nits** — is closed, and each closure was verified
by execution, not by reading the claim. Scope is exactly the one declared file.
Zero volatile literals, zero code line pins, `tests.test_docs_freshness` green.

Residue: **one low should-fix** (`settle` is still used 659 lines before it is
built, and revision 5 *widened* that gap) and **four nits**. None blocks the
merge; the document still carries STATUS: DRAFT.

### Scope

```
$ git diff --stat 1dd40460..HEAD
 docs/phase_2/derivation_night_runbook.md | 587 ++++++++++++++++++++++++++-----
 1 file changed, 496 insertions(+), 91 deletions(-)
$ git diff --name-only 1dd40460..HEAD
docs/phase_2/derivation_night_runbook.md
$ wc -l docs/phase_2/derivation_night_runbook.md
    1997
```

Exactly the declared scope: one docs file, 1593 → 1997 lines (the brief said
~1996; the file is 1997, one line of drift in the brief, not in the file).

---

## 1. S-1 — every `$VAR` in every fenced `zsh` block is built before use: **CLOSED**

Mechanically extracted all fenced blocks from the file (22 `zsh`, 10 unlabelled)
and diffed used names against assigned / exported / `:?`-guarded names.
Script: `/tmp/row10pass2/s1.py`.

| `$VAR` | first use | built at | how | verdict |
|---|---|---|---|---|
| `BOOKKEEPING_ROOT` | L196 | L196 | `: "${BOOKKEEPING_ROOT:?the activation's authorized linked worktree}"` | OK (`:?`-guarded at use) |
| `H` | L201 | L200 | `export H="$(git rev-parse origin/main)"` | OK |
| `NIGHT_DATE` | L227 | L225 | `export NIGHT_DATE=<YYYYMMDD>` (§0.2) | OK |
| `REMOTE_URL` | L228 | L226 | `export` | OK |
| `remote_main` | L229 | L228 | assignment | OK |
| `MEASUREMENT_ROOT` | L230 | L227 | `export` | OK |
| `PY` | L241 | L240 | `export` | OK |
| `PLAN_ID` | L287 | L284 | `export` (§0.2 new block) | OK |
| `STAGE` | L289 | L288 | `export` | OK |
| `NIGHT_ROOT` | L290 | L287 | `export` | OK |
| `SESSION_ID` | L295 | L285 | `export` | OK |
| `EVIDENCE_ROOT_ID` | L295 | L286 | `export` | OK |
| `CALIBRATION_PLAN` | L296 | L290 | `export` | OK |
| `STAGED_PLAN` | L864 | L289 | `export` | OK |
| `CALIBRATION_LEDGER` | L1366 | L291 / L1355 | `export` (arm) and re-exported in §2.0 | OK |
| `LEDGER_HEAD_PIN` | L1367 | L292 / L1356 | same | OK |
| `NIGHT_HOUR` | L1254 | L1198 | `export NIGHT_HOUR=<t0's local hour …>` (§1.4) | OK |
| `NIGHT_MINUTE` | L1254 | L1199 | `export` | OK |
| `WINDOW_CUSTODY_ROOT` | L1366 | L1354 | `export WINDOW_CUSTODY_ROOT="$NIGHT_ROOT"` | OK |
| `PLAN` | L1367 | L1364–1365 | `eval "$(grep -E '^export (SESSION_ID\|EVIDENCE_ROOT_ID\|PLAN\|RUNS_ROOT)=' …)"` then `export` | OK |
| `RUNS_ROOT` | L1367 | L1364–1365 | same | OK |
| `p` | L1268 | L1268 | python comprehension binding, not shell | n/a |

**UNRESOLVED: none.** (The naive scanner reported `PLAN` / `RUNS_ROOT` as
unassigned because it does not model `eval`; both are recovered from the
wrapper's own `export` lines and then re-exported at L1365. That recovery was
executed end to end — see §3 below.)

Guarded re-entry points are real, not decorative: L1196–1197 re-guards
`NIGHT_ROOT`, `PY`, `STAGE`, `STAGED_PLAN`, `SESSION_ID`, `EVIDENCE_ROOT_ID`,
`CALIBRATION_PLAN` at the top of §1.4's arm block, and L283 re-guards
`H`/`NIGHT_DATE`/`MEASUREMENT_ROOT` at the top of §0.2's new block, so a
fresh shell fails loudly instead of interpolating empty strings.

**Cross-activation completeness (the real S-1/S-3 risk).** Every `$VAR` used in
a `zsh` block after §2.0 is one §2.0 itself exports:

```
L1406 MEASUREMENT_ROOT | L1407 PY | L1408 SESSION_ID
L1487 MEASUREMENT_ROOT | L1488 PY | L1489 CALIBRATION_LEDGER, LEDGER_HEAD_PIN | L1490 PLAN, SESSION_ID
L1567 MEASUREMENT_ROOT | L1568 PY | L1587 MEASUREMENT_ROOT | L1588 PY
```

So the harvesting activation, which never runs §0.2, is fully coordinatized.

**The `set -e` AND-OR cure is real and was needed.** §0.2 L305–308 now writes
`test ! -e "$NIGHT_ROOT"` and `test ! -L "$NIGHT_ROOT"` as separate statements
and states why. The defect it cures is live in the source template: record 12
L523–524 uses `test ! -e "$NIGHT_ROOT/night" && test ! -L "$NIGHT_ROOT/night"`,
which under `set -e` does not abort when the left side fails.

---

## 2. S-2 — staged plan vs published `night_plan.json`: **CLOSED, and the
load-bearing claim is proven by byte witness**

### 2a. The sequence is consistent with the generator's own contract

```
$ python3 scripts/gen_derivation_night.py --help
  --plan PLAN           frozen v2 night plan JSON (emit mode)
  --out OUT             default: the plan's chain_path
  --verify              emit mode: write nothing; re-derive the wrapper from
                        the same inputs and compare it byte-for-byte with the
                        installed file at the plan's chain_path (and that
                        file's sidecar)
```

`--plan` is an INPUT, and `--out` is refused if it is not the plan's
`chain_path` (`build_spec` L537–542). So the wrapper is written **into the night
root** (the plan's `chain_path` = `$NIGHT_ROOT/chain.zsh`) while the plan itself
sits at `$STAGED_PLAN` — exactly what §1.1b step 4 says ("Only the plan is
staged; the wrapper it describes is written where the night will run it").

### 2b. "wrapper bytes depend on plan CONTENT, not path" — HOLDS (executed)

Source: `plan_path` appears twice in the whole generator, both in `build_spec`,
both reads:

```
$ grep -rn 'plan_path' scripts/gen_derivation_night.py
469:    plan_path = Path(args.plan).expanduser()
471:        raw = json.loads(plan_path.read_text(encoding="utf-8"))
```

Every `WrapperSpec` field is resolved from decoded plan fields or from argv;
none from the plan's location. Byte witness — the same plan bytes at two
deliberately unrelated paths:

```
--plan /tmp/row10pass2/pathtest/stageA/night_plan.json
  rc=0  emitted …/chain.zsh sha256=46826a30752a0ce26d179d101f252c2cf273fb842f4984bd72f04fa0c3b88aba
--plan /tmp/row10pass2/pathtest/totally/different/dir/B/night_plan.json
  rc=0  emitted …/chain.zsh sha256=46826a30752a0ce26d179d101f252c2cf273fb842f4984bd72f04fa0c3b88aba
IDENTICAL: True
```

And `--verify` returns rc 0 from the staged path, from an unrelated path, and
from the published path after simulating the `os.replace`:

```
--verify with staged plan (pre-move):                rc=0 VERIFIED …/chain.zsh sha256=46826a30…
--verify with published-path plan copy (post-move):  rc=0 VERIFIED …/chain.zsh sha256=46826a30…
--verify with PUBLISHED …/night-custody/…/night_plan.json: rc=0 VERIFIED …/chain.zsh sha256=46826a30…
```

The runbook's "it is a free re-assertion, not a second, different check"
(L864–866) is exactly right. Negative control, to prove `--verify` is not vacuous:
appending two bytes to the installed wrapper produced

```
FAIL wrapper bytes differ from re-derivation: re-derived sha256=46826a30… installed sha256=0f0238db… at …/chain.zsh
rc=3
```

matching §1.1b step 4's quoted rc-3 text including the `<absent>` fallback
(source L902–905).

### 2c. Consistent with the watchdog contract's install step and discovery model

- Discovery glob — `scripts/magistrate_watchdog.py:258–259`
  `return sorted(self.root.parent.glob("*/night_plan.json"))`, with
  `DEFAULT_CUSTODY_ROOT = Path.home() / "night-custody" / "magistrate"` (L55).
  Parent = `/Users/edr/night-custody`, so the enumerated set is exactly
  `/Users/edr/night-custody/*/night_plan.json`, one level, that filename.
  `/Users/edr/night-plan-staging/<PLAN_ID>/night_plan.json` is not one level
  below `night-custody` and is therefore never enumerated. §0.7 L523–532 states
  precisely this and is correct.
- The driver discovers nothing — `scripts/run_night.py:1846`
  `command.add_argument("--plan", required=True, …)`. §0.7's claim holds.
- `os.replace`, target must not pre-exist — record 12 §"Block B":
  `assert not target.exists() and not target.is_symlink()` then
  `os.replace(os.environ['STAGED_PLAN'], target)`. §1.4 step 5 reproduces it
  verbatim.
- §0.7's own "expect no output" check
  (`print -rl -- /Users/edr/night-custody/*/night_plan.json(N)`) was NOT run —
  `/Users/edr/night-custody` is out of scope for this pass by instruction.

The collision review 141 found (step 3's `--plan` input vs §1.4's
must-not-pre-exist target) is gone, and §0.7's discoverability precondition
survives authoring.

---

## 3. S-3 — the frozen triple's exact fields: **CLOSED**

The runbook §1.5 L1306–1313 says it is "three fields and only three:
`(plan_id, root, head)`". Quoted sources, verbatim:

- `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md`, line 9:
  > Frozen checkout triples `(plan_id, root, head)` for this activation: @@FENCED_CHECKOUTS@@.
- `docs/process/MAGISTRATE_WATCHDOG.md`, §"Complete write inventory" (line 106,
  confirmed under that heading by a programmatic heading-membership scan):
  > At each launch, `@@FENCED_CHECKOUTS@@` is rendered as a deterministic JSON list containing the canonical repository and every authored, not-completed v2 plan's canonical measurement root and head. The prompt forbids Git operations in the canonical root and forbids moving every listed measurement root. … A post-arm move invalidates the pin and requires a re-arm with a re-pinned plan.
- Code corroboration — `scripts/magistrate_watchdog.py:795–805`:
  ```
  rows = [["__canonical_repo__", str(CANONICAL_REPO), None]]
  rows.extend([plan.plan_id, _canonical_measurement_root(plan), plan.measurement_head] for plan in plans)
  ```
  Three columns, in that order. The runbook's §1.5 table (`plan_id` → `$PLAN_ID`,
  `root` → `$MEASUREMENT_ROOT`, `head` → `$H`) matches field for field, and its
  "the successor activation does not choose the list and this runbook cannot
  widen it" is correct.

**§2.0's reconstruction was executed.** Against a real emitted wrapper:

```
$ grep -nE "^export (SESSION_ID|EVIDENCE_ROOT_ID|PLAN|RUNS_ROOT|WINDOW_CUSTODY_ROOT|CALIBRATION_LEDGER|LEDGER_HEAD_PIN)=" chain.zsh
37:export SESSION_ID='derivation-20260912-epoch'
41:export PLAN='…/night-custody/derivation-20260912/calibration_plan.json'
42:export EVIDENCE_ROOT_ID='EV-1'
43:export RUNS_ROOT='…/night-custody/derivation-20260912/runs'
44:export WINDOW_CUSTODY_ROOT='…/night-custody/derivation-20260912'
45:export CALIBRATION_LEDGER='<measurement_root>/runs/calibration_observation_ledger.jsonl'
46:export LEDGER_HEAD_PIN='<measurement_root>/configs/calibration/calibration_ledger_head.json'

$ zsh -c 'eval "$(grep -E "^export (SESSION_ID|EVIDENCE_ROOT_ID|PLAN|RUNS_ROOT)=" chain.zsh)"; …'
derivation-20260912-epoch
EV-1
…/calibration_plan.json
…/runs
rc=0
```

All four recover. §2.0's provenance table is accurate on every row:
`WINDOW_CUSTODY_ROOT == custody_root == NIGHT_ROOT` (`build_spec`:
`window_custody_root=plan.custody_root`), and `CALIBRATION_LEDGER` /
`LEDGER_HEAD_PIN` are the generator's `--ledger` / `--head-pin` defaults
(`build_spec` L555–559), measurement-root-relative. `PLAN` is indeed the frozen
calibration plan. The "verify the sidecar before reading anything out of the
wrapper, and a failed check is a stop" instruction is the right ordering.

---

## 4. S-4 — §1.4's commands vs record 12 and the installer: **CLOSED**

Record 12 resolves in the merged tree:
`docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md`
is tracked and **present on `origin/main`** and at HEAD (`git cat-file -e` on both).
*(Note for the caller: it is NOT present in `/Users/edr/code/JouleWise-wt-bk-96bfeca7`,
whose head `9af519f9` lacks records 11–13; I read the s8 copy at HEAD instead.
The runbook's path citation is nevertheless valid in the merged tree.)*

§1.4's block maps step for step onto record 12 §"Block B" (L549–693):

| §1.4 step | record 12 §"Block B" | verdict |
|---|---|---|
| `test -s "$STAGE/notice-evidence.txt"` | same command, step 6 | match |
| `test "$(git rev-parse HEAD)" = "$H"`; clean porcelain; `git fetch origin main`; `git merge-base --is-ancestor "$H" origin/main` | same four, steps 4 and 6 | match |
| wrapper `--verify` | **deliberate substitution**, named in the runbook's text (record 12 renders the G2-a runsheet instead) | declared |
| `NightPlan.from_mapping` assertions | same mechanism; this night's constants (`DIAGNOSTIC_NO_PACK`, `window_max_s == 9000`, this registration path) — **named as changed** in the text | declared |
| same-device assert `st_dev` | identical assertion | match |
| final raw census `ps -axo … \|\| true` | identical `ps`/`grep` | match |
| `assert not target.exists() and not target.is_symlink()` + `os.replace` | verbatim | match |
| `install_night_agent.sh --plan --hour --minute` | verbatim | match |
| `launchctl list \| grep joulewise` + `{'com.joulewise.night','com.joulewise.night.deadman'} <= labels` | verbatim | match |
| post-install `night/` inventory (name/size/mtime_ns) | same, runbook adds `if night.is_dir() else []` tolerance | match + hardened |
| `cmp "$NIGHT_ROOT/night_plan.json" "$STAGE/arm-night_plan.json"` | verbatim | match |
| rollback: `--uninstall` → `cp` → `cmp` → `rm` | verbatim (`rollback_this_attempt`) | match |

Installer flags exist, executed:

```
$ scripts/install_night_agent.sh --help
usage: usage --plan PLAN.json --hour H --minute M [--uninstall] [--render-only DIR] [--launchctl-bin PATH]
```

`--hour 7` refusal, executed against a plan pinned to this HEAD:

```
$ scripts/install_night_agent.sh --plan … --hour 7 --minute 0 --render-only /tmp/row10pass2/plists
refusing --hour 7: it is the dead-man hour (DEADMAN_HOUR=7); arm the night in another hour
rc=2
```

One invocation installs both labels and `--uninstall` removes both
(`scripts/install_night_agent.sh` L160–175); `--hour`/`--minute` are validated
as integers in range before anything else.

---

## 5. S-7 — `fence`: **CLOSED**, definition quotes the contract and 02:56 is consistent

§Terms L152–166 splits the two senses and states the convention that the
unqualified word means the watchdog sense. Every clause checks out against the
contract's own words:

| Runbook clause (L152–166) | Contract text |
|---|---|
| "refuses to LAUNCH OR ADOPT a magistrate **agent** session" | `MAGISTRATE_WATCHDOG.md:54` — "the short tick returns `FENCED` with `adopt=False` and does not launch or adopt a supervisor" |
| "Three things fence" | `:31` — "`FENCED`: a plan span, the 02:45–03:30 belt, or the 07:00 minute forbids launch." |
| "a valid plan's span (opening at the closed boundary `t0 − 25 min`)" | `:46` — "The plan span begins at the closed boundary `t0 - 25 minutes`." |
| "both fixed intervals are half-open" | `:52` — "The local fixed fences are half-open: `[02:45:00, 03:30:00)` and `[07:00:00, 07:01:00)`." |
| cited as §"Safety model and state machine" and §"Fence and deadlines" | heading-membership scan: `:31` is under `## Safety model and state machine` (L19); `:52` and `:54` are under `## Fence and deadlines` (L40). Both citations resolve. |

The 02:56 example is consistent and now *explained where the term is built*:
"What a fence forbids is an agent being started, never a night being run … the
night's own two LaunchAgents are not magistrate sessions". Corroboration cited
and verified — `docs/process/NIGHT_HANDBACK.md:93–94`:

> It fired at 02:56 PDT on 2026-09-09: result `REHEARSAL_ONLY`, chain exit 0 …

`Session` (L98–103) now says unqualified it is the ledger object and the
watchdog's *agent session* is always written out in full, which removes the
§Terms-plus-§Terms inference that made §1.2's `t0` look fenced. The
`blindness fence` entry (L162–166) marks itself as a different object and §2.3's
sentence reads "The blindness fence is installed in code". Two related citations
also verified: `§"Install handoff"` closing sentence quoted verbatim at
`MAGISTRATE_WATCHDOG.md:329`, and `§"Fence and deadlines", the boundary table`
(cited by §0.6) exists at `:56–62` with exactly the `−25 / −16 / −15` rows.

---

## 6. Volatile literals, line pins, tests

```
$ grep -nE 'PR #|Ran [0-9]+ tests|\bCodex\b|\bSol\b|\bAstra\b|\bOpus\b|\bFable\b|gpt-|claude-' docs/phase_2/derivation_night_runbook.md
(zero hits)

$ grep -nE '\.py:[0-9]+|\.md:[0-9]+|\.zsh:[0-9]+|\.sh:[0-9]+|\.json:[0-9]+|:L[0-9]+' docs/phase_2/derivation_night_runbook.md
(zero hits)

$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness
Ran 31 tests in 0.915s
OK

$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gen_derivation_night
Ran 40 tests in 20.033s
OK
```

**Volatile literals: zero. Code line pins: zero.** Two near-misses, both examined
and both judged acceptable, recorded so the check is auditable:

- L103 contains the word "Claude" ("a running Claude activation"). It is the
  agent runtime's name, not a rotating model name; the watchdog contract uses it
  the same way, and §0.2's census substring check greps `claude` literally. Not a
  volatile literal.
- L1308 says the relaunch prompt "carries them at line 9". That is the file's
  ONLY line-number citation — see NIT-1.

---

## 7. First-use test over §Terms, §0, §1.1a/§1.1b, §1.4, §2.0

**Closed by revision 5** (each verified: term now built at or before first use):
`wrapper` (§Terms L140), `night root` (§Terms L143), `tracked chain` (§Terms
L134 plus the path and a `shasum` command at first demand, §0.5 L450–455),
`fence` / `blindness fence` / `Session` (§Terms), `frozen calibration plan` and
`PLAN` (built at first use, §0.2 table L319), `night root` creation (§0.2
replaces "Create it first"), `<NIGHT_DATE>` format (§0.2 L257–261), `[DD]`
(§0.5 L447–449, glossed from the registration's own §"Fields filled at commit"),
`staging path` / `$STAGED_PLAN` (§0.2 + §1.1b step 2), `published` (§1.4),
`desk-inputs writer` vs `capture writer` (§0.8 opens with the bold convention;
the single surviving bare "writer" at L901 is inside a verbatim generator
refusal string — `gen_derivation_night.py:226` — which the convention paragraph
accounts for).

Also verified built-at-or-before-first-use: `tripwire` (L930, at use),
`sidecar` (L789, at use), `paste lines` (L646–648, at use), `stale field`,
`head pin`, `courier allowance` vs `pre-settle allowance` (explicitly
disambiguated), `desk recovery` (L1481, at use).

**Still open — one term:**

- **`settle`** is used as a term of art at **L319** (§0.2's new variable table:
  "fails before the settle rather than at `d01`"), **L666** (§0.8 refusal table:
  "with the settle already spent"), L901, L917, L926–927 — and is not built
  until **L978/L985** (§1.2: "The night's shape is: one settle, then twelve
  captures…", `settle 600 s`). There is no §Terms entry and **no §8 first-use
  row** (`grep -n '| settle'` → zero hits). Review 141 flagged this at a gap of
  278 lines; revision 5 **widened it to 659 lines** by adding the L319 use. See
  SF-1.

**Known-open, outside the named sections** (the writer declared these
deliberately untouched, and I confirm they are unchanged): `C1–C5` is still used
once at L1392 (§2.1) with the five conditions never enumerated; `the live
preflight` at L640 (§0.8) is still unglossed as a component.

---

## Findings

### BLOCKERS — none

### SHOULD-FIX (low)

**SF-1 — `settle` fails the first-use test, and revision 5 widened the gap.**
First technical use `docs/phase_2/derivation_night_runbook.md` §0.2 variable
table (`CALIBRATION_PLAN` row) and §0.8's first refusal row; built only in §1.2.
Under Ed's binding writing standard a term doing technical work must be built,
glossed at use, or deleted. One §Terms entry closes it — e.g. *"**Settle** — the
600 s the chain idles after it opens its session and before the first capture,
so the machine's thermal and power state is the one the captures are taken in;
a night refused at `d01` has already spent it."* Add the matching §8 row.

### NITS

**N-1 — the file's only line pin, into a sibling process doc.** §1.5 L1308 says
the relaunch prompt "carries them at line 9". §7 states the file's own rule —
citations by symbol and record, never by line number — and the other 1996 lines
honour it. The locator is currently correct (verified: line 9 of
`MAGISTRATE_RELAUNCH_PROMPT.md` is the Frozen-checkout-triples line), and there
is project precedent (`MAGISTRATE_WATCHDOG.md` says "Prompt line 24" and "prompt
lines 15, 22 and 23"), and `test_prompt_has_at_most_twenty_five_lines_and_required_order`
pins the prompt's length and ordering but **not** that this clause is line 9.
Cheapest cure: drop "at line 9" and keep the verbatim quote, which is already there.

**N-2 — the `--hour 7` refusal is quoted as a prefix, not verbatim.** §1.4
L1287 quotes `refusing --hour <h>: it is the dead-man hour`. Executed, the
message is `refusing --hour 7: it is the dead-man hour (DEADMAN_HOUR=7); arm the
night in another hour` (`scripts/install_night_agent.sh` L113). Everywhere else
the runbook quotes refusal strings in full, so this one reads as complete when it
is not. Add the tail or an ellipsis.

**N-3 — a citation's position claim is wrong (the citation itself resolves).**
§0.2 L248–250 calls the lock-diff "the same assertion the prior night's arm
runbook runs (record 12, §"Block A", last command)". The `diff -u … mac-measurement-lock.txt`
command is at record 12 L359, early in Block A (which runs L253–534); the last
command of Block A is `print 'block A rc=0'` at L533. Drop "last command".

**N-4 — one precondition from the source template was not carried over.**
Record 12 §"Block A" asserts `test ! -e "$NIGHT_ROOT/night"` and
`test ! -L "$NIGHT_ROOT/night"` before publication; §1.4's assertion block does
not (it asserts only the `night_plan.json` target). Low risk, because §0.2 now
asserts `$NIGHT_ROOT` does not pre-exist and creates it, and because the
installer is what creates `night/` (`install_night_agent.sh`:
`mkdir -p "$custody_root/night"` on install) — which is also why §1.4's tolerant
`if night.is_dir() else []` baseline is correct. Worth one line for symmetry.

**Observation, not a finding** — §1.4's block runs `install_night_agent.sh` as a
bare command under `set -euo pipefail`, whereas record 12 wraps it in
`if ! … then rollback_this_attempt; fi`. A failed install therefore aborts the
shell and leaves rollback to the operator. The runbook states this ("If any step
AFTER publication fails, recover in this exact order"), so it is a declared
simplification, not a defect.

**Also observed** — every `zsh` block containing an operator fill placeholder
(`export NIGHT_DATE=<YYYYMMDD>` L225, `EVIDENCE_ROOT_ID` L286, `NIGHT_HOUR`/
`NIGHT_MINUTE` L1198–1199, §2.0's three triple fills L1349–1351) is a **zsh
parse error** if pasted unsubstituted:
`zsh -c 'set -euo pipefail; export NIGHT_DATE=<YYYYMMDD>; echo ok'` →
`zsh:1: parse error near ';'`, rc 1. That is fail-closed — the whole block
refuses to parse, so nothing runs with an empty value — and it is the file's
consistent `<…>` fill convention. Recorded only so the S-1 claim
"runnable as written" is understood precisely: runnable after substitution,
fail-loud before it.

---

## Summary

Revision 5 does what its changelog claims, and the five named findings are
closed with executed evidence rather than assertion: every shell variable is
built, exported or `:?`-guarded before use with zero unresolved names; the
staged-plan path is provably safe because the wrapper's bytes are byte-identical
from two unrelated plan paths and `--verify` returns rc 0 before and after the
publish (with a rc-3 negative control proving the check is not vacuous); the
staging root is outside the watchdog's one-level `*/night_plan.json` glob and the
driver discovers nothing; the frozen triple is exactly `(plan_id, root, head)`
per the relaunch prompt, the watchdog's write inventory and
`fenced_checkout_rows`, and §2.0's eval-recovery of the remaining four
coordinates was executed against a real wrapper; §1.4 now carries the real
install and rollback commands, matching record 12 §"Block B" step for step with
its two departures named in the text, and the installer's flags and dead-man-hour
refusal reproduce; and `fence` is split into two senses whose every clause quotes
the watchdog contract, with the 02:56 `t0` explained rather than contradicted.
Scope is one file, tests are green, and there are zero volatile literals and zero
code line pins.

**Verdict: CLEAN. Row 10 PASS.** One low should-fix (`settle`) and four nits, all
one-line bench edits, none blocking the merge of a document that still carries
STATUS: DRAFT.
