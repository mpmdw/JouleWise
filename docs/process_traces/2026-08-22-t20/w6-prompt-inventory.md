# W-6 — the prompt inventory for the real `_v4` transaction

**For Ed, to read before he sits down.** D-155 work order W-6, ruled under
NR-10. Built read-only against `main` at `3c96b18f` (the declared reviewed
head), against the measurement checkout
`/Users/edr/JouleWise-measurement-20260813` (verified at the same commit,
`3c96b18f`), and against the permission rules actually on this machine on
2026-08-26.

## 1. What this document is, and the one question it answers

When the transaction session runs a shell command, the Claude Code harness
decides one of two things: run it silently, or stop and put the exact command
line in front of Ed and wait. D-150(1) chose the *stopping* behaviour as the
operational form of the mint license — six commands, at Ed's hands, approved
one at a time as they execute. There is no settings rule granting them; the
prompt **is** the license.

That choice only works if the prompts actually fire. A permission rule that
matches a licensed command would remove its prompt without announcing that it
had, and the license would be silently spent. NR-10 ruled that this be checked
mechanically, in advance, rather than discovered at 11pm.

So this document answers one question, for every command the runbook issues in
Phases A–H:

> **Will Ed see this command, or not?**

and then checks the ruled expectation: **exactly six** commands should stop and
wait — two command classes across three packs.

**The short answer up front.** The six licensed commands are *not* matched by
any allow rule at their `_v4` spellings, so on the rule table alone they stop
and wait, as ruled. But three things found during this inventory can defeat
that, and all three are Ed's hands, not an agent's. They are in
[§7, NEEDS-ED](#7-needs-ed--three-items-ed-must-settle-with-his-own-hands).
The most important is that this machine's **default permission mode is `auto`**,
which is a mode that decides at runtime rather than from the rule table — and
the whole D-150(1) design assumes deterministic prompting.

## 2. Vocabulary, built before it is used

**An allow rule.** A line in a `settings.json` / `settings.local.json` file
under `permissions.allow`, e.g. `Bash(python3 scripts/*)`. When a rule matches
the command the harness is about to run, the command runs with no prompt and Ed
sees nothing. Rules are matched against the **literal text of the command
line** — not against what the command means, and not after shell variables are
expanded. `$PY scripts/x.py` and `.venv/bin/python3 scripts/x.py` are two
different strings to the matcher even when they are the same command.

**Permission mode.** A session-wide setting that decides what happens when *no*
rule matches. In **`manual`** mode (the mode formerly called `default`; both
spellings are accepted), no match means a prompt — deterministically. In
**`auto`** mode the harness applies its own runtime classifier to unmatched
commands, silently running the ones it scores as harmless. `auto` is what is
configured on this machine today (§3). The full set of modes this CLI accepts
is `manual`, `auto`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan`.

**An `ask` rule.** A line under `permissions.ask`. It forces a prompt for a
matching command **even when an allow rule would otherwise match it, and even
in `auto` mode**. It grants nothing; it only guarantees the stop. This is the
instrument §7 item 1 recommends for the six licensed commands.

**The invocation form.** The exact spelling and the working directory the
command is issued from. Two forms of the same operation get different answers:
issued from a shell whose working directory is already the measurement
checkout, `.venv/bin/python3 scripts/gen_state.py` is one string; issued as
`cd /Users/edr/JouleWise-measurement-20260813 && .venv/bin/python3
scripts/gen_state.py` it is a different, longer string that matches different
rules. The magistrate controls this, which is why the runbook fixes the bare
relative form throughout.

**The spelling trap.** `.venv/bin/python` and `.venv/bin/python3` are the same
interpreter inside a virtual environment and different literal strings to the
matcher. Only the `python3` spelling is named by any rule here. Every command in
this inventory uses `python3`.

**The four classes** used in the table below:

| Class | Meaning |
|---|---|
| **ALLOW** | A rule matches the exact string. Runs silently. Ed sees nothing. |
| **ASK** | No rule matches, and the command changes repository or published state. Under `manual` mode this stops and waits. **Under `auto` mode it is a runtime judgement, not a rule-table fact** — see §7 item 1. |
| **UNCERTAIN-PROBE** | The rule table is silent and this inventory could not observe the harness's actual behaviour for this form. Recorded, not guessed. |
| **DENY-EXPECTED** | Must never run in this session at all. If a prompt for one of these appears, that is a defect — decline it and stop. |

**Working-directory shorthand** used in the table:

| Symbol | Absolute path |
|---|---|
| `MEAS` | `/Users/edr/JouleWise-measurement-20260813` — the declared measurement checkout (D-155 NR-1) |
| `DEV` | `/Users/edr/code/JouleWise` — the development worktree; Phase D1 pushes from here |
| `CUSTODY` | the transaction custody root, created outside every repository at §1.5; its absolute path is the magistrate's to fix on the night |
| `PUBCO` | the clean separate checkout at `ATTESTATION_HEAD` that Phase F's long suite runs in |
| `WCUST` | `/Users/edr/JouleWise-window-custody` — where the commit-freeze sentinel lives |

## 3. The rules that are actually in force

Four files can carry permission rules for this session. All four were read on
2026-08-26:

| File | Contents |
|---|---|
| `/Users/edr/.claude/settings.json` (user, all projects) | `permissions.defaultMode = "auto"`. **No allow, ask, or deny lists.** |
| `/Users/edr/code/JouleWise/.claude/settings.json` (project, tracked) | **Absent.** |
| `/Users/edr/code/JouleWise/.claude/settings.local.json` (project, untracked) | 24 allow rules. No `deny` list. No `ask` list. Last modified 2026-08-19 18:17 — the `_v3` mint evening. |
| `/Users/edr/JouleWise-measurement-20260813/.claude/settings.json` and `.local.json` | **Both absent. The measurement checkout carries no permission rules of its own.** |

That last row has an operational consequence that is easy to miss:

> **The session must be launched from `DEV`, not from `MEAS`.** Claude Code
> loads project rules from the directory the session is rooted in. A session
> started inside `/Users/edr/JouleWise-measurement-20260813` would load *no*
> project allow rules at all — every one of the ~40 commands below would be
> decided by the `auto` classifier with no rule table behind it. The runbook's
> whole invocation discipline (bare relative form, working directory already at
> the measurement checkout) assumes a session rooted at `DEV` that has *changed
> directory into* `MEAS`. Launch it that way.

### 3.1 The 24 allow rules, grouped by what they do here

Rules that bear on this transaction:

| # | Rule | Bearing on this session |
|---|---|---|
| 1 | `Bash(gh pr merge:*)` | **Hazard.** Would let any session merge a PR — a push to `main` — silently, inside the freeze span. See §7 item 3. |
| 2 | `Bash(gh run *)` | Covers the CI conclusion-field check in §1.1. Read-only. Benign. |
| 3 | `Bash(python3 scripts/*)` | **The first swallow candidate.** See §6. |
| 4 | `Bash(.venv/bin/python3 scripts/*)` | **The second swallow candidate.** See §6. |
| 5 | `Bash(cd /Users/edr/JouleWise-measurement-20260818 && *)` | **Hazard.** A blanket allow for the *rejected* checkout. Any command mistyped against `-20260818` runs silently. See §7 item 2. |
| 6 | `Bash(git -C /Users/edr/JouleWise-measurement-20260818 *)` | Same hazard, git form. |
| 7 | `Bash(caffeinate *)` | Benign and wanted. |
| 8 | `Bash(PYTHONDONTWRITEBYTECODE=1 python3 -m unittest *)` | Does **not** match Phase F3's form (`.venv/bin/python3 -m unittest discover -s tests`, no `PYTHONDONTWRITEBYTECODE=` prefix). |
| 9 | `Bash(sysctl -n kern.bootsessionuuid)` | Exactly Phase B3. ALLOW. |
| 10–11 | `Bash(git -C /Users/edr/JouleWise-measurement-20260818 log --oneline -1)`, `… status --short` | Wrong checkout; inert here. |
| 12 | `Read(//Users/edr/JouleWise-measurement-20260818/**)` | **There is no equivalent rule for `-20260813`.** File reads at the real measurement checkout have no allow rule. |
| 13–14, 22 | Three exact-command rules naming `configs/campaigns/d117_floor_qwen25_1p5b_v3` | `_v3` pack path. **Does not match any `_v4` command.** |
| 15 | `Bash(python3 -)` | Allows a bare stdin/heredoc Python. Note it does **not** cover `.venv/bin/python3 -`, which is the form this transaction uses. |
| 16 | `Bash(/Users/edr/JouleWise-measurement-20260818/.venv/bin/python3 -c '…')` | Wrong checkout; inert. |
| 17–18, 20–21 | `Bash(python3 scripts/gen_state.py --check)`, `Bash(python3 scripts/gen_state.py)`, two `echo "… exit=$?"` literals | Bookkeeping; not used in Phases A–H. |
| 19 | `Bash(PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gen_state tests.test_docs_freshness)` | Not used here. |
| 23 | `Bash(python3 -c ' *)` | Covers inline `python3 -c '…'` asserts **in the bare `python3` spelling only**. |
| 24 | `Bash(python3 scripts/generate_arm_readiness.py freeze --help)` | An earlier probe of exactly this kind. Evidence, discussed in §6. |

## 4. The ordered inventory, Phases A–H

Read the **cwd** column as "the shell's working directory is already this before
the command is typed". Where a step repeats per pack, the repetition count is
in the step name and the exact strings are given for the six licensed commands
only — those are the ones that must be verbatim.

`<HEAD>`, `<CUSTODY>`, `<hC>` and the head names (`EVIDENCE_DERIVATION_HEAD`,
`PINSET_MINT_HEAD`, `ATTESTATION_HEAD`) are values fixed during execution; they
do not change any classification, because no rule matches these strings with or
without them.

### 4.0 Pre-session (W-1 relock and the arming checks; any prior day)

| # | Phase | Step | Exact command | cwd | Class | Rule matched / reason |
|---|---|---|---|---|---|---|
| 0.1 | pre | W-1 relock | `mv .venv .venv.pre-v4` | `MEAS` | n/a | **Ed's own terminal, not the harness.** Outside this inventory by construction (§1.1 rules the relock to Ed's hands). |
| 0.2 | pre | W-1 relock | `python3.13 -m venv .venv` | `MEAS` | n/a | Ed's own terminal. |
| 0.3 | pre | W-1 relock | `.venv/bin/python3 -m pip install -c env/mac-measurement-lock.txt -e ".[mac]"` | `MEAS` | n/a | Ed's own terminal. A `pip` operation in a measurement environment is never an agent's. |
| 0.4 | pre | W-1 gate | `.venv/bin/python3 -m pip freeze --exclude-editable \| sort > /tmp/have.txt` | `MEAS` | UNCERTAIN-PROBE | No rule. Read-only, but writes to `/tmp` and contains a pipe and a redirect. Magistrate-run per §1.1. |
| 0.5 | pre | W-1 gate | `grep -Ev '^(#\|[[:space:]]*$)' env/mac-measurement-lock.txt \| sort > /tmp/want.txt` | `MEAS` | UNCERTAIN-PROBE | No rule. Read-only. |
| 0.6 | pre | W-1 gate | `diff /tmp/want.txt /tmp/have.txt` | `MEAS` | UNCERTAIN-PROBE | No rule. Read-only. **This exit-0 is the acceptance, not a version print.** |
| 0.7 | pre | NR-1 sync | `git fetch origin` | `MEAS` | UNCERTAIN-PROBE | No rule. Moves only `refs/remotes/origin/main`. **Already done:** `MEAS` is at `3c96b18f`. |
| 0.8 | pre | NR-1 sync | `git merge --ff-only origin/main` | `MEAS` | UNCERTAIN-PROBE | No rule. **Already done.** |
| 0.9 | pre | §1.5 env hygiene | `env \| grep -i JOULEWISE_` | `MEAS` | UNCERTAIN-PROBE | No rule. Read-only. **Must print nothing** — see §8. |
| 0.10 | pre | §1.5 sentinel arming | `mkdir -p /Users/edr/JouleWise-window-custody` | `DEV` | UNCERTAIN-PROBE | No rule. Creates a directory outside every repository. |
| 0.11 | pre | §1.5 sentinel arming | `touch /Users/edr/JouleWise-window-custody/COMMIT_FREEZE_OPEN` | `DEV` | UNCERTAIN-PROBE | No rule. Test sentinel only; removed at 0.13. |
| 0.12 | pre | §1.5 sentinel arming | `scripts/window_status.sh between "W-6 sentinel arming check" "sentinel present" "None."` | `DEV` | ASK | No rule. **Must print the literal line `freeze span open: status written locally, not published.`** If it prints anything else the guard is off. |
| 0.13 | pre | §1.5 sentinel arming | `rm /Users/edr/JouleWise-window-custody/COMMIT_FREEZE_OPEN` | `DEV` | UNCERTAIN-PROBE | No rule. The real sentinel is created at C11.1, not here. |
| 0.14 | pre | §1.1 CI gate | `gh run view <id> --json conclusion` | `DEV` | **ALLOW** | Rule 2, `Bash(gh run *)`. |

### 4.1 Phase A — desk preflight (MAGISTRATE, the evening before; Ed is NOT present)

**Read this line before Phase A: every ASK in Phase A stalls the desk work,
because Ed is not at the machine.** Phase A is scheduled the evening before
precisely so Ed need not attend it. Any command here that stops and waits will
sit there until someone answers it.

| # | Phase | Step | Exact command | cwd | Class | Rule matched / reason |
|---|---|---|---|---|---|---|
| A.1 | A | A1 `$BASE` gate | `git rev-parse HEAD` | `MEAS` | UNCERTAIN-PROBE | No rule. Read-only. |
| A.2 | A | A1 | `git status --porcelain=v1` | `MEAS` | UNCERTAIN-PROBE | No rule. Read-only. |
| A.3 | A | A1 | `git show <HEAD>:docs/process_traces/2026-08-22-t20/s0-fixation-delta.patch > <CUSTODY>/004-base-delta.patch` | `MEAS` | UNCERTAIN-PROBE | No rule. Read-only plus a redirect into custody. |
| A.4 | A | A1 | `shasum -a 256 <CUSTODY>/004-base-delta.patch` | `MEAS` | UNCERTAIN-PROBE | No rule. Read-only. |
| A.5 | A | A1 (×4 tools) | `git cat-file -e <HEAD>:scripts/build_v4_histsem_pinset.py` — and the same for `scripts/build_family_marker.py`, `scripts/verify_family_marker.py`, `scripts/verify_receipt_histsem.py` | `MEAS` | UNCERTAIN-PROBE | No rule. Read-only existence checks. |
| A.6 | A | A1 | `git cat-file -e <HEAD>:configs/arm_readiness/d117_row_registry_v2.json` | `MEAS` | UNCERTAIN-PROBE | No rule. Read-only. |
| A.7 | A | A1 (×4 absence) | `git cat-file -e <HEAD>:configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json` — and the three `_v4` pack roots. **Each must FAIL.** | `MEAS` | UNCERTAIN-PROBE | No rule. Read-only. A non-zero exit is the pass here. |
| A.8 | A | A2 anchor map | `.venv/bin/python3 <CUSTODY>/tools/s0_anchor_map.py /Users/edr/JouleWise-measurement-20260813 <HEAD> > <CUSTODY>/005-anchor-map.json` | `MEAS` | **ASK** | No rule. Rules 3–4 name `scripts/…`; this tool lives in custody, outside the repository, so `.venv/bin/python3 scripts/*` cannot match it. |
| A.9 | A | A2 | `.venv/bin/python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["matched"]==15, d["matched"]' <CUSTODY>/005-anchor-map.json` | `MEAS` | **ASK** | No rule. Rule 23 is `Bash(python3 -c ' *)` — the **bare** `python3` spelling only, not `.venv/bin/python3 -c`. |
| A.10 | A | A3 manifest | `.venv/bin/python3 - /Users/edr/JouleWise-measurement-20260813 <CUSTODY>/s0-candidate-manifest.json <HEAD> <ci_run_id> <<'PY' … PY` | `MEAS` | **ASK** | No rule. Rule 15 is `Bash(python3 -)`, not `.venv/bin/python3 -`. Heredoc bodies also carry shell-metacharacter weight with the classifier. |
| A.11 | A | A3 | `.venv/bin/python3 -m json.tool <CUSTODY>/s0-candidate-manifest.json` | `MEAS` | **ASK** | No rule. |
| A.12 | A | A3 | `shasum -a 256 <CUSTODY>/s0-candidate-manifest.json > <CUSTODY>/007-manifest-sha256.txt` | `MEAS` | UNCERTAIN-PROBE | No rule. Read-only over the manifest. |
| A.13 | A | A4 registry-v1 sweep | `git grep -nE 'd117_row_registry_v1\|d117-row-registry-v1' -- joulewise/ > <CUSTODY>/010-joulewise-v1-hits.txt` | `MEAS` | UNCERTAIN-PROBE | No rule. Read-only. Must be `git grep`, never a worktree `grep -r` (the `__pycache__` hazard the runsheet documents). |
| A.14 | A | A4 | `.venv/bin/python3 - <CUSTODY>/010-joulewise-v1-hits.txt <<'PY' … PY` | `MEAS` | **ASK** | No rule; same reason as A.10. |
| A.15 | A | A5 tool materialisation | `cat > <CUSTODY>/tools/s0_allowlist_contract.py <<'PY' … PY` (and the same for `check_census.py`, `s0_anchor_map.py`) | `MEAS` | **ASK** | No rule. Writes an executable file outside the repository. |
| A.16 | A | A5 | `chmod 0555 <CUSTODY>/tools/s0_allowlist_contract.py` (×3 tools) | `MEAS` | UNCERTAIN-PROBE | No rule. |
| A.17 | A | A5 | `.venv/bin/python3 -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' <CUSTODY>/tools/check_census.py` | `MEAS` | **ASK** | No rule; `.venv/bin/python3 -c` is not rule 23. |
| A.18 | A | A5 | `shasum -a 256 <CUSTODY>/tools/*.py > <CUSTODY>/011-custody-tools-materialized.txt` | `MEAS` | UNCERTAIN-PROBE | No rule. |
| A.19 | A | §2.1 shape | `.venv/bin/python3 - configs/arm_readiness/d117_row_registry_v2.json <<'PY' … PY` | `MEAS` | **ASK** | No rule. |
| A.20 | A | §2.1 shape | `.venv/bin/python3 <CUSTODY>/tools/s0_allowlist_contract.py --registry configs/arm_readiness/d117_row_registry_v2.json --shape-only` | `MEAS` | **ASK** | No rule; custody path, not `scripts/`. **`expected_count` must be 112.** |
| A.21 | A | §1.5 suite baseline | `.venv/bin/python3 -m unittest discover -s tests` on a scratch checkout | scratch | **ASK** | No rule. Rule 8 requires the `PYTHONDONTWRITEBYTECODE=1 python3` prefix, which this form does not have. Long-running; §3 says measure it here rather than discover it on the night. |

### 4.2 Phase B — reboot and pin (ED)

| # | Phase | Step | Exact command | cwd | Class | Rule matched / reason |
|---|---|---|---|---|---|---|
| B.1 | B | B1 | *(notification; no shell command)* | — | n/a | D-150a state-change ping. |
| B.2 | B | B2 | *(Ed reboots the Mac)* | — | n/a | Ed's hands. No harness command. |
| B.3 | B | B3 | `sysctl -n kern.bootsessionuuid` | `MEAS` | **ALLOW** | Rule 9 matches this string exactly. Runs silently — which is correct; this is a read. |

### 4.3 Phase C — the scripted band (Ed present through C10)

| # | Phase | Step | Exact command | cwd | Class | Rule matched / reason |
|---|---|---|---|---|---|---|
| C.1 | C | C1 emit ×3 | `.venv/bin/python3 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py --pack-id d117_contrast_qwen25_1p5b_vs_7b_v4 --family-suffix _v4 --no-preserve-current-frozen-bytes` — then the `d117_floor_qwen25_1p5b_v3` and `d117_floor_qwen25_7b_v3` generators with their own `_v4` pack ids | `MEAS` | **ASK** | No rule. The generator lives under `configs/campaigns/…`, not `scripts/`, so rules 3–4 cannot match. **Three ASKs if the classifier prompts.** Repository-mutating. |
| C.2 | C | C1 | `git add -A` | `MEAS` | UNCERTAIN-PROBE | No rule. |
| C.3 | C | C1 | `git commit -m 'v4: emit the three _v4 pack roots from the reviewed generators'` | `MEAS` | UNCERTAIN-PROBE | No rule. Local commit; not pushed until Phase D. |
| C.4 | C | C2 runtime gate | `.venv/bin/python3 - /Users/edr/JouleWise-measurement-20260813 <<'PY' … PY` (interpreter, versions, checkout-first import assertion) | `MEAS` | **ASK** | No rule. |
| C.5 | C | C2 weight presence | `.venv/bin/python3 - /Users/edr/JouleWise-measurement-20260813 <<'PY' … PY` (every `_v3`-declared weight file present at its recorded size) | `MEAS` | **ASK** | No rule. Reads `/Users/edr/jw_models` read-only. |
| C.6 | C | C3 guard (×3) | `git status --porcelain=v1` — **must be empty before each freeze** | `MEAS` | UNCERTAIN-PROBE | No rule. |
| **C.7** | **C** | **C3 — PROMPT 1 (GAMMA)** | `.venv/bin/python3 scripts/project_identity_pins.py freeze configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4` | `MEAS` | **ASK (licensed)** | No exact rule. Swallow candidate: rule 4 `Bash(.venv/bin/python3 scripts/*)` — see §6. Preceded by `export HF_HUB_OFFLINE=1` and `export TRANSFORMERS_OFFLINE=1`. |
| **C.8** | **C** | **C3 — PROMPT 2 (ALPHA)** | `.venv/bin/python3 scripts/project_identity_pins.py freeze configs/campaigns/d117_floor_qwen25_1p5b_v4` | `MEAS` | **ASK (licensed)** | Same. Note rules 13/22 name the `_v3` pack path (`…_1p5b_v3`) — a different literal, so they do **not** match. |
| **C.9** | **C** | **C3 — PROMPT 3 (BETA)** | `.venv/bin/python3 scripts/project_identity_pins.py freeze configs/campaigns/d117_floor_qwen25_7b_v4` | `MEAS` | **ASK (licensed)** | Same. |
| C.10 | C | C3 per-pack asserts (×3) | `.venv/bin/python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="PASS" and d["mutated"] is True, d' <CUSTODY>/030-u11-<label>.stdout.json` | `MEAS` | **ASK** | No rule; `.venv/bin/python3 -c` is not rule 23. |
| C.11 | C | C3 per-pack commit (×3) | `git add -- configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4` then `git commit -m "v4 U11 identity-pin projection for <label>"` | `MEAS` | UNCERTAIN-PROBE | No rule. **One pack per commit; the next freeze refuses on a dirty tree.** |
| C.12 | C | C4 post-conditions | `.venv/bin/python3 - /Users/edr/JouleWise-measurement-20260813 <<'PY' … PY` (three per-pack commits exist; checkout-first import after mutation; `_v4` weight digests equal the committed `_v3` receipts') | `MEAS` | **ASK** | No rule. |
| C.13 | C | C4 | `git rev-parse HEAD` → recorded as `EVIDENCE_DERIVATION_HEAD` | `MEAS` | UNCERTAIN-PROBE | No rule. Read-only. |
| C.14 | C | C5 common-head gate | `git rev-parse HEAD 'HEAD^{tree}'` and `git status --porcelain=v1` | `MEAS` | UNCERTAIN-PROBE | No rule. Read-only. |
| C.15 | C | C5 | `.venv/bin/python3 - <CUSTODY>/s0-candidate-manifest.json <<'PY' … PY` (the manifest declares exactly the two modules this step runs) | `MEAS` | **ASK** | No rule. |
| C.16 | C | C5 | `.venv/bin/python3 -m unittest -v tests.test_arm_readiness_schemas tests.test_receipt_histsem` | `MEAS` | **ASK** | No rule. Rule 8 needs the `PYTHONDONTWRITEBYTECODE=1 python3` prefix; rule 19 names different modules. |
| C.17 | C | C6 author ×3 | `.venv/bin/python3 scripts/author_arm_readiness_evidence.py --pack-root configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4` — and the same for the ALPHA and BETA `_v4` pack roots | `MEAS` | **ASK** | No exact rule; **swallow candidate under rule 4** (`scripts/…`). **This is the boot-binding boundary and T+0 on the 168 h clock.** |
| C.18 | C | C6 census | `.venv/bin/python3 <CUSTODY>/tools/check_census.py <CUSTODY>/040-author-*.stdout.json > <CUSTODY>/041-applicability-census.json` | `MEAS` | **ASK** | No rule; custody path. Must show exactly eleven kinds per pack. |
| C.19 | C | C6 | `git add -- configs/campaigns/d117_floor_qwen25_1p5b_v4 configs/campaigns/d117_floor_qwen25_7b_v4 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4` then `git commit -m 'v4 common-head R1 evidence for all three packs'` | `MEAS` | UNCERTAIN-PROBE | No rule. **One commit for all three; no commit between the three author commands.** |
| C.20 | C | C7 sacrificial clone | `git clone --no-local /Users/edr/JouleWise-measurement-20260813 <CUSTODY>/pre-mint-clean` | `DEV` | **ASK** | No rule. ~650 MB. **This is the one clone that survives; it is a screen protecting a create-only slot, not rehearsal scaffolding.** |
| C.21 | C | C7 | `git -C <CUSTODY>/pre-mint-clean checkout --detach <EVIDENCE_COMMIT>` | `DEV` | UNCERTAIN-PROBE | No rule. |
| C.22 | C | C7 preflight freeze ×3 | `.venv/bin/python3 <CUSTODY>/pre-mint-clean/scripts/generate_arm_readiness.py freeze --pack-root <CUSTODY>/pre-mint-clean/configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4 --predecessor-pack-root <CUSTODY>/pre-mint-clean/configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3` — and the same for ALPHA and BETA | `MEAS` | **ASK** | No rule: the script path is absolute into custody, so rules 3–4 (`scripts/…` relative) cannot match. **All three must be a clean PASS or the primary mint does not happen.** |
| C.23 | C | C7 | `rm -rf <CUSTODY>/pre-mint-clean` | `DEV` | **ASK** | No rule. A recursive delete; expect it to stop and wait. |
| **C.24** | **C** | **C8 — PROMPT 4 (GAMMA)** | `.venv/bin/python3 scripts/generate_arm_readiness.py freeze --pack-root configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4 --predecessor-pack-root configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3` | `MEAS` | **ASK (licensed)** | No exact rule. Swallow candidate: rule 4 — see §6. Rule 24 names the `--help` form, a different literal. |
| **C.25** | **C** | **C8 — PROMPT 5 (ALPHA)** | `.venv/bin/python3 scripts/generate_arm_readiness.py freeze --pack-root configs/campaigns/d117_floor_qwen25_1p5b_v4 --predecessor-pack-root configs/campaigns/d117_floor_qwen25_1p5b_v3` | `MEAS` | **ASK (licensed)** | Same. |
| **C.26** | **C** | **C8 — PROMPT 6 (BETA)** | `.venv/bin/python3 scripts/generate_arm_readiness.py freeze --pack-root configs/campaigns/d117_floor_qwen25_7b_v4 --predecessor-pack-root configs/campaigns/d117_floor_qwen25_7b_v3` | `MEAS` | **ASK (licensed)** | Same. |
| C.27 | C | C8 asserts (×3) | `.venv/bin/python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="PASS" and d["mutated"] is True and not d["reason_codes"] and d["receipt_path"].endswith("freeze-0004.json"), d' <CUSTODY>/060-freeze-<label>.stdout.json` | `MEAS` | **ASK** | No rule. |
| C.28 | C | C8 | `git add -- <the three _v4 pack roots>` then `git commit -m 'v4 freeze-0004 receipts for all three packs'` | `MEAS` | UNCERTAIN-PROBE | No rule. One freeze commit for all three. |
| C.29 | C | C9 tool authentication | `.venv/bin/python3 - /Users/edr/JouleWise-measurement-20260813 <CUSTODY>/s0-candidate-manifest.json <<'PY' … PY` | `MEAS` | **ASK** | No rule. Each executing custody tool's SHA-256 vs the manifest digest for its repository-relative path. |
| C.30 | C | C10 step 1 | `.venv/bin/python3 scripts/build_v4_histsem_pinset.py --repository /Users/edr/JouleWise-measurement-20260813 --base-pinset configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json --historical-head <EVIDENCE_DERIVATION_HEAD> --current-head <FREEZE_COMMIT> --pack-root configs/campaigns/d117_floor_qwen25_1p5b_v4 --pack-root configs/campaigns/d117_floor_qwen25_7b_v4 --pack-root configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4 --output configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json` | `MEAS` | **ASK** | No exact rule; **swallow candidate under rule 4** (`scripts/…`). **This is the mint.** `--historical-head` is the derivation head, never the evidence commit. Output path is create-only. |
| C.31 | C | C10 step 2 | `.venv/bin/python3 - configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json <CUSTODY>/070-build-v4-pinset.json <<'PY' … PY` (3 packs, 33 receipts, the three exact pack ids) | `MEAS` | **ASK** | No rule. |
| C.32 | C | C10 step 2 | `git diff --exit-code -- configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json` | `MEAS` | UNCERTAIN-PROBE | No rule. The `_v1` member must be byte-unchanged. |
| C.33 | C | C10 step 2 | `git add -- configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json` then `git commit -m 'v4: mint the historical-semantics successor pinset'` → **`PINSET_MINT_HEAD`** | `MEAS` | UNCERTAIN-PROBE | No rule. This head is the **allowlist-contract closure**, and no transcript may call it "window close". |
| C.34 | C | C10 step 3 | `.venv/bin/python3 <CUSTODY>/tools/s0_allowlist_contract.py --registry configs/arm_readiness/d117_row_registry_v2.json --repo /Users/edr/JouleWise-measurement-20260813 --derivation <EVIDENCE_DERIVATION_HEAD> --head <PINSET_MINT_HEAD>` | `MEAS` | **ASK** | No rule; custody path. Closes the contract at exactly 112. |
| C.35 | C | C10 step 3 | `.venv/bin/python3 scripts/verify_receipt_histsem.py --repository-root /Users/edr/JouleWise-measurement-20260813 --require-published --pack-root configs/campaigns/d117_floor_qwen25_1p5b_v4 --pack-root configs/campaigns/d117_floor_qwen25_7b_v4 --pack-root configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4` | `MEAS` | **ASK** | No exact rule; **swallow candidate under rule 4**. |
| C.36 | C | C10 step 3 | `.venv/bin/python3 - /Users/edr/JouleWise-measurement-20260813 <PINSET_MINT_HEAD> <<'PY' … PY` → records `hS` from the bytes **committed at the mint head** | `MEAS` | **ASK** | No rule. `hS` is a coordinate of the closure head, not the published head. |
| C.37 | C | **C11.1** | `mkdir -p /Users/edr/JouleWise-window-custody` then `touch /Users/edr/JouleWise-window-custody/COMMIT_FREEZE_OPEN` | `DEV` | UNCERTAIN-PROBE | No rule. **This opens the freeze span. It must exist before the attestation commit.** |
| C.38 | C | C11.2 | `git status --porcelain=v1 --untracked-files=all` (must be empty) and `git rev-parse HEAD` (must equal `PINSET_MINT_HEAD`) | `MEAS` | UNCERTAIN-PROBE | No rule. Read-only. |
| C.39 | C | C11.3 | `git rev-parse HEAD^{tree}` | `MEAS` | UNCERTAIN-PROBE | No rule. Read-only. |
| C.40 | C | C11.3 (×3 packs) | `.venv/bin/python3 - configs/campaigns/d117_floor_qwen25_1p5b_v4 <<'PY'` … `from joulewise.arm_readiness import committed_pack_tree_sha256` … `PY` — and the same for the BETA and GAMMA `_v4` pack roots | `MEAS` | **ASK** | No rule. Per the amended window runbook §5C producer. |
| C.41 | C | C11.3 | `git commit --allow-empty --cleanup=verbatim -m 'JouleWise terminal review attestation' -m 'JouleWise-Terminal-Review: PASS' -m "JouleWise-Terminal-Review-Tree-Oid: <TREE_OID>" -m "JouleWise-Terminal-Review-Pack-Sha256: <ALPHA>" -m "JouleWise-Terminal-Review-Pack-Sha256: <BETA>" -m "JouleWise-Terminal-Review-Pack-Sha256: <GAMMA>"` → **`ATTESTATION_HEAD`** | `MEAS` | UNCERTAIN-PROBE | No rule. **`--cleanup=verbatim` is load-bearing** — the default cleanup strips lines the parser needs. |
| C.42 | C | C11.4 | `.venv/bin/python3 <CUSTODY>/tools/s0_allowlist_contract.py --registry configs/arm_readiness/d117_row_registry_v2.json --repo /Users/edr/JouleWise-measurement-20260813 --derivation <EVIDENCE_DERIVATION_HEAD> --head <ATTESTATION_HEAD>` | `MEAS` | **ASK** | No rule. Still exactly 112 — an empty commit adds no paths, but the assertion is re-run rather than reasoned about. |

### 4.4 Phase D — publication (MAGISTRATE)

| # | Phase | Step | Exact command | cwd | Class | Rule matched / reason |
|---|---|---|---|---|---|---|
| D.1 | D | D1 | `git fetch /Users/edr/JouleWise-measurement-20260813 main` | `DEV` | UNCERTAIN-PROBE | No rule. **Plain local path, not a `file://` URL** — the `file://` form appears in no source. |
| D.2 | D | D1 | `git push origin FETCH_HEAD:main` | `DEV` | **ASK** | No rule. **The single irreversible step of the session.** From here a mechanism failure abandons the family, not the attempt. |
| D.3 | D | D2 | `git fetch origin` | `MEAS` | UNCERTAIN-PROBE | No rule. Licensed inside the freeze span: it moves only `refs/remotes/origin/main`, creates no commit, and four-way equality requires it. |
| D.4 | D | D2 | `.venv/bin/python3 -c "import json,sys;from joulewise.arm_readiness import reviewed_main;print(json.dumps(reviewed_main(sys.argv[1]),indent=2))" configs/campaigns/d117_floor_qwen25_1p5b_v4` | `MEAS` | **ASK** | No rule; `.venv/bin/python3 -c` is not rule 23. Pass a **pack root**, not a repository path. Require `exact_match: true`, `clean: true`, `head_commit == ATTESTATION_HEAD`. |
| D.5 | D | D3 | *(notification)* | — | n/a | Published at `ATTESTATION_HEAD`; freeze span open. |

### 4.5 Phase E — marker, table, delegated confirmation (order E1 → E3 → E4 → E2 → E5)

| # | Phase | Step | Exact command | cwd | Class | Rule matched / reason |
|---|---|---|---|---|---|---|
| E.1 | E | E1 | `mkdir -p <CUSTODY>/marker-candidate` | `MEAS` | UNCERTAIN-PROBE | No rule. |
| E.2 | E | E1 | `.venv/bin/python3 scripts/build_family_marker.py --repository /Users/edr/JouleWise-measurement-20260813 --head <ATTESTATION_HEAD> --pack-root configs/campaigns/d117_floor_qwen25_1p5b_v4 --pack-root configs/campaigns/d117_floor_qwen25_7b_v4 --pack-root configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4 --output <CUSTODY>/marker-candidate/d117_family_publication_v4.json --phase publication` | `MEAS` | **ASK** | No exact rule; **swallow candidate under rule 4**. **No `--candidate-manifest` on this invocation** (D-155 NR-4). |
| E.3 | E | E3 | *(render the DRAFT step-6 table `C`)* — a file write, by editor or heredoc, into `<CUSTODY>` | `MEAS` | **ASK** | No rule if done by heredoc. **Write no `.sha256` sidecar here** — the sidecar is written once, at E4, over the final bytes. |
| E.4 | E | E4 part 1 | `shasum -a 256 <CUSTODY>/marker-candidate/d117_family_publication_v4.json` → `hM` | `MEAS` | UNCERTAIN-PROBE | No rule. Recomputed from the artifact, never taken from a report. |
| E.5 | E | E4 part 1 | `git show <PINSET_MINT_HEAD>:configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json \| shasum -a 256` → `hS` | `MEAS` | UNCERTAIN-PROBE | No rule. Note the head: the **closure** head, not the published head. |
| E.6 | E | E4 parts 3–4 | *(write `confirmation.statement`, render the FINAL canonical bytes)* | `MEAS` | **ASK** | No rule if done by heredoc. |
| E.7 | E | E4 part 5 | `shasum -a 256 <CUSTODY>/windows/family_publication/d117_step6_confirmation_table_v4.json` → **`hC`, recorded in custody only** | `MEAS` | UNCERTAIN-PROBE | No rule. `hC` never enters a repository path, in this transaction or any other. |
| E.8 | E | E4 part 6 | `shasum -a 256 <table> > <table>.sha256` | `MEAS` | UNCERTAIN-PROBE | No rule. Render final, **then** sidecar — in that order and not before. |
| E.9 | E | E2 | `.venv/bin/python3 scripts/verify_family_marker.py --repository /Users/edr/JouleWise-measurement-20260813 --marker <CUSTODY>/marker-candidate/d117_family_publication_v4.json --phase publication --confirmation <CUSTODY>/…/d117_step6_confirmation_table_v4.json --expected-confirmation-digest <hC>` | `MEAS` | **ASK** | No exact rule; **swallow candidate under rule 4**. Assert `status: PASS` and `origin_main_commit == ATTESTATION_HEAD`. Any transcript carrying the phrase `FORGED_ORIGIN_MAIN_OID` in this session is a defect. |
| E.10 | E | E5 | `mkdir -p <CUSTODY>/windows/family_publication` then `cp -p` the marker, its sidecar, the table and its sidecar | `MEAS` | UNCERTAIN-PROBE | No rule. **Promotion copies; it never edits.** |

### 4.6 Phase F — the published-green half

| # | Phase | Step | Exact command | cwd | Class | Rule matched / reason |
|---|---|---|---|---|---|---|
| F.1 | F | F1 | `git -C <PUBCO> rev-parse HEAD`, `… rev-parse refs/heads/main`, `… rev-parse refs/remotes/origin/main`, `… status --porcelain=v1` — all four must agree on `ATTESTATION_HEAD` | `DEV` | UNCERTAIN-PROBE | No rule (the only `git -C …` rules name `-20260818`). |
| F.2 | F | F2 | `.venv/bin/python3 <PUBCO>/scripts/verify_family_marker.py --repository <PUBCO> --marker <CUSTODY>/windows/family_publication/d117_family_publication_v4.json --phase publication --confirmation <CUSTODY>/windows/family_publication/d117_step6_confirmation_table_v4.json --expected-confirmation-digest <hC>` | `PUBCO` | **ASK** | No rule: absolute script path, so rules 3–4 cannot match. Require `lane: "published"`, `gate_admissible: true`, `publication_authorized: true`, and both `confirmation_missing` and `confirmation_mismatch` in the executed-checks list. |
| F.3 | F | F3 | `.venv/bin/python3 -m unittest discover -s tests` | `PUBCO` | **ASK** | No rule. **45–180 min, serial, single-process.** Start it as soon as F1–F2 pass and let Phase G run against `MEAS` meanwhile. |

### 4.7 Phase G — the dry-run ceremony (no arm)

| # | Phase | Step | Exact command | cwd | Class | Rule matched / reason |
|---|---|---|---|---|---|---|
| G.1 | G | dry-run ×3 | `.venv/bin/python3 scripts/generate_arm_readiness.py --expected-confirmation-digest <hC> dry-run --pack-root configs/campaigns/d117_floor_qwen25_1p5b_v4 --window-custody-root <CUSTODY>/windows --rehearsal-id <id> --synthetic-root <CUSTODY>/synthetic` — and the same for the BETA and GAMMA `_v4` pack roots | `MEAS` | **ASK** | No exact rule; **swallow candidate under rule 4**. **This is `dry-run`, never `arm`** (D-155 NR-6). Assert per pack: `status: PASS`, `refusals: []`, `head_binding == ATTESTATION_HEAD`, `receipt_kind: dry_run`, `mode: dry_run`, `arm_disposition: NOT_APPLICABLE`, `evidence: []`. |

### 4.8 Phase H — close the session

| # | Phase | Step | Exact command | cwd | Class | Rule matched / reason |
|---|---|---|---|---|---|---|
| H.1 | H | H1 | `chmod -R a-w <CUSTODY>/transcripts` (or equivalent read-only seal) | `DEV` | UNCERTAIN-PROBE | No rule. Sealed means nothing already written is ever mutated; custody stays open for exactly one appended record (`campaign-close.json`, days later). |
| H.2 | H | H2 | **STRUCK** | — | **DENY-EXPECTED** | No `RUN_STATE.md` header update on transaction night. It would be an ordinary commit inside the freeze span, and it would take the slot D-153 A1 reserves for the fixation commit. |
| H.3 | H | H3 | *(notification)* | — | n/a | Campaign span open; per-window notices to follow. |
| H.4 | H | H4 | *(record the D-153 W5 limitation in custody)* | `DEV` | n/a | A custody write, no commit. |

## 5. Prompt-count summary

Counted by **row** in §4. Several rows are a per-pack repetition (`×3`, `×4`),
so the number of individual executions is larger than the row count — but each
of the six licensed commands is one row and one execution, which is the number
that matters.

| Bucket | Rows | Notes |
|---|---|---|
| **ASK (licensed)** — the six D-150(1) prompts | **6** | C.7, C.8, C.9 (U11 projection ×3) and C.24, C.25, C.26 (readiness freeze ×3). One execution each. |
| **ALLOW** — runs silently, Ed sees nothing | 2 | B.3 `sysctl -n kern.bootsessionuuid`; 0.14 `gh run view … --json conclusion`. Both reads. |
| **ASK (unlicensed)** — no rule matches, mutating or heavy | 41 | Every row marked **ASK** that is not one of the six, plus 0.12 (the sentinel arming check). |
| **UNCERTAIN-PROBE** | 45 | Rule table silent; read-only or local-only. In `manual` mode these prompt; in `auto` mode the classifier decides at runtime (§9). |
| **DENY-EXPECTED** | 1 in-table (H.2) plus the list at §6.3 | Must never run. |

**Ed sees exactly two of these commands run silently, and both are reads.**
Everything else is either a licensed prompt or an unlicensed one — which is why
NEEDS-ED item 1 matters more than the raw count: the six are only *guaranteed*
to be six once the mode is deterministic and the licensed classes are on an
`ask` list.

## 6. Verifying the ruled expectation: exactly six ASK events

### 6.1 The six, and why nothing matches them

The ruled expectation is **two licensed command classes × three packs = six**.
All six exact strings are in the table at C.7–C.9 and C.24–C.26. Against the 24
allow rules:

| Candidate rule | Does it match a licensed `_v4` command? |
|---|---|
| Rule 13 `Bash(python3 scripts/project_identity_pins.py freeze configs/campaigns/d117_floor_qwen25_1p5b_v3)` | **No.** The pack path ends `_v3`; the licensed commands end `_v4`. Different literal, and `_v3` is not a prefix of `_v4`. |
| Rule 22 — the same command in the `.venv/bin/python3` spelling | **No**, same reason. |
| Rule 14 — the same command with `--help` | **No.** |
| Rule 24 `Bash(python3 scripts/generate_arm_readiness.py freeze --help)` | **No.** `--help` is not `--pack-root …`. |
| Rule 3 `Bash(python3 scripts/*)` | **Wrong spelling** — the licensed commands use `.venv/bin/python3`. Cannot match. |
| **Rule 4 `Bash(.venv/bin/python3 scripts/*)`** | **This is the swallow candidate.** Read as a glob, `.venv/bin/python3 scripts/` followed by anything, it covers all six literally. |
| Rule 5 `Bash(cd /Users/edr/JouleWise-measurement-20260818 && *)` | **No** — provided the runbook's bare-relative form is used and the working directory is `-20260813`. This rule is precisely why NR-1 rejected `-20260818`. |

So the whole question reduces to **rule 4**.

### 6.2 What the evidence says about rule 4

Two independent lines, and they point the same way.

**Line 1 — the file's own history.** `settings.local.json` contains, at
positions 13, 14, 22 and 24, four *exact-command* rules of a shape the harness
writes when a person approves a prompt and asks not to be asked again for that
exact command:

- `Bash(python3 scripts/project_identity_pins.py freeze configs/campaigns/d117_floor_qwen25_1p5b_v3)`
- the same with `--help`
- the same in the `.venv/bin/python3` spelling
- `Bash(python3 scripts/generate_arm_readiness.py freeze --help)`

The broad rules 3 and 4 sit at positions 3 and 4 — earlier in the array, and
harness-written rules append. So rules 3 and 4 were already present when those
four were created. **If rule 3 or rule 4 had suppressed those prompts, the
approvals that created positions 13/14/22/24 could never have happened.** Their
existence is direct evidence that a `scripts/… freeze …` command prompted with
the broad rules already in place.

**Line 2 — the `_v3` precedent.** `docs/process/ed-s5-mint-decision-2026-08-19.md`
records that on 2026-08-19 both mint classes were "BLOCKED by the Claude Code
permission classifier — for both the executing agent and the lead", and its
confirmation table records the mints as executed "via Ed-approved manual
prompts". `settings.local.json`'s modification time is 2026-08-19 18:17, the
same evening. The prompts fired.

**Conclusion:** the ruled expectation of six is **not currently contradicted by
the rule table or by the recorded history of this machine.** The six licensed
commands should stop and wait.

**But this is evidence, not proof.** Rule 4 covers all six on a plain glob
reading, and the cost of being wrong is the silent loss of the mint license —
the one thing D-150(1) exists to prevent. A prediction that rests on inferred
array ordering is not the standard this transaction holds anything else to.
**Hence NEEDS-ED item 1**, which replaces the inference with a mechanism.

### 6.3 Commands that must never run — DENY-EXPECTED

If a prompt for any of these appears, decline it and stop the transaction; a
prompt for one of them means a step ran that should not exist.

| Command class | Why it must not run |
|---|---|
| `.venv/bin/python3 scripts/generate_arm_readiness.py arm …` | **No arm in this session.** D-155 NR-6: the family's first real arm is the shakedown window's, under its D-149 GO receipt. |
| `… generate_arm_readiness.py verify --arm-receipt …` / `… consume …` | Both are arm-path steps; there is no arm receipt in this session. |
| `git update-ref refs/remotes/origin/main …` | S-0 scaffolding. In the real lane `origin/main` is a real remote-tracking reference that moves only when something is actually pushed. |
| `git push` issued from `MEAS` | The `_v3` doctrine, preserved verbatim by NR-2: the measurement checkout consumes references and never publishes. The push is D.2, from `DEV`. |
| Any ordinary `git commit` on `MEAS` after C11.3 | The freeze span. Any commit invalidates every armed pack for the rest of the campaign. |
| `git apply …/s0-fixation-delta.patch` and any fixation commit | Fixation is the first commit *after* the freeze closes, days from now (§6 item 2). |
| `.venv/bin/python3 -m unittest tests.test_receipt_histsem.SuccessorPinsetDigestConditionTests` (the `118-*` byte-pin probe) | Requires the fixation commit to exist; the pinned method exists at no head reachable in this session. |
| `scripts/window_status.sh …` run with the sentinel absent, at any time from C11.1 onward | It would commit and push `WINDOW_STATUS.md` — a path outside the 112 — breaking the freeze and adding changed-set residue that refuses every subsequent arm. |
| `gh pr merge …` | A merge is a push to `main`. See NEEDS-ED item 3 — **this one has an allow rule and would run silently.** |
| Anything naming `/Users/edr/JouleWise-measurement-20260818` | The rejected checkout. See NEEDS-ED item 2 — **it has a blanket allow rule and would run silently.** |
| Any `[QUIET-MAC]` measurement, campaign launch, or dry-run of a window | §6 item 1: no measurement window occurs in this session. |
| Adding any authenticator path to any allowlist to make the NR-11 cure land mid-transaction | D-151 condition 7 tripwire, not an amendment lane. Stop and land the cure through the ordinary review lane at a new head. |

## 7. NEEDS-ED — three items Ed must settle with his own hands

No agent modifies permission settings. These are for Ed, and all three are
minutes of work.

### Item 1 (most important) — the session's permission mode is `auto`

`/Users/edr/.claude/settings.json` sets `permissions.defaultMode = "auto"`.
In that mode, a command with no matching allow rule is not automatically a
prompt: the harness applies runtime judgement and silently runs what it reads
as harmless. **The D-150(1) license is a prompt. A mode that decides at runtime
is not a mode in which a prompt count can be guaranteed in advance** — which is
exactly what NR-10 asked for.

The transaction session should be run in **`manual` permission mode**, not
`auto`, so that "no rule matches" means "prompt", deterministically, and this
inventory's predictions become guarantees rather than expectations. Launch it
with `claude --permission-mode manual`, or cycle to it in-session with
Shift+Tab (the footer shows a grey ⏸ badge when manual mode is active).

**And, belt and braces, put the two licensed classes beyond the reach of any
allow rule.** A `permissions.ask` rule forces a prompt even when an allow rule
matches, **and it fires in `auto` mode too** — this CLI's own approval dialog
names the `permissions.ask` rule as the cause when it does. Adding these four
lines to `/Users/edr/code/JouleWise/.claude/settings.local.json` makes the six
prompts structural rather than inferred, and does so independently of item 1:

```json
"ask": [
  "Bash(python3 scripts/project_identity_pins.py freeze *)",
  "Bash(.venv/bin/python3 scripts/project_identity_pins.py freeze *)",
  "Bash(python3 scripts/generate_arm_readiness.py freeze *)",
  "Bash(.venv/bin/python3 scripts/generate_arm_readiness.py freeze *)"
]
```

This is not the standing allow-rule form D-150 declined — it is the opposite of
one. It *forces* the prompt D-150(1) chose; it does not grant anything.

### Item 2 — the blanket allow for the rejected checkout

Rules 5, 6, 10, 11, 12 and 16 all name `/Users/edr/JouleWise-measurement-20260818`,
and rule 5 is `Bash(cd /Users/edr/JouleWise-measurement-20260818 && *)` — a
blanket allow for *any command whatsoever* in that directory. NR-1 rejected that
checkout, and one of its three grounds was this very rule. It is now worse than
inert: a command mistyped against `-20260818` during the transaction would run
**silently**, with no prompt and no record that anything unusual happened.

**Delete rules 5, 6, 10, 11 and 16 before the session.** Nothing in Phases A–H
touches that path.

Related, and cheap: there is a `Read(//Users/edr/JouleWise-measurement-20260818/**)`
rule and **none for `-20260813`**. Every file read at the real measurement
checkout will therefore prompt. If Ed would rather not answer those, replacing
rule 12 with `Read(//Users/edr/JouleWise-measurement-20260813/**)` removes a
class of nuisance prompts without touching any command's execution — reads
mutate nothing.

### Item 3 — `Bash(gh pr merge:*)` inside the freeze span

Rule 1 allows `gh pr merge` with no prompt. A merge is a push to `main`. From
C11.1 onward — for the whole week the freeze span runs — a single merge from
*any* session on this machine invalidates every armed pack for the rest of the
campaign, and it would happen silently.

**Remove rule 1 for the duration of the freeze span**, and restore it after the
fixation commit is pushed. This is the same hazard class as
`WINDOW-STATUS-FREEZE-GUARD-01`, which got a code guard; `gh pr merge` has no
guard, only this rule.

The standing "keep the remote current" habit is suspended for the same span, by
the same reasoning: no bookkeeping commits, no docs pushes, no status
publication, from C11.1 until fixation.

## 8. Never export `JOULEWISE_STATUS_REPO` or `JOULEWISE_COMMIT_FREEZE_SENTINEL`

`scripts/window_status.sh` at this head reads two environment variables, each
with a default:

```sh
REPO="${JOULEWISE_STATUS_REPO:-/Users/edr/code/JouleWise}"
COMMIT_FREEZE_SENTINEL="${JOULEWISE_COMMIT_FREEZE_SENTINEL:-/Users/edr/JouleWise-window-custody/COMMIT_FREEZE_OPEN}"
```

Both exist so the W-2 regression can point the script at a temporary directory.
Neither may be set in any shell in Phases A–H.

**If `JOULEWISE_STATUS_REPO` is exported**, the status publisher writes,
commits and pushes `WINDOW_STATUS.md` inside whatever repository it names. Point
it at the measurement checkout and it makes an ordinary commit on the one branch
whose head must not move — inside the freeze span, on a path outside the 112.
That is simultaneously a freeze break and changed-set residue that refuses every
subsequent arm.

**If `JOULEWISE_COMMIT_FREEZE_SENTINEL` is exported to any path other than the
real sentinel**, the guard looks for a file that is not there, concludes the
freeze span is closed, and **publishes normally**. The failure is silent: the
script prints its ordinary success output. This is the same defect the §1.5
arming check exists to catch — which is why that check asserts the observed line
`freeze span open: status written locally, not published.` and not the sentinel
file's existence.

**The check, before Phase C1:**

```sh
env | grep -i JOULEWISE_        # must print nothing
```

Run it in the transaction shell, and confirm neither variable is exported from
a shell profile. Environment variables do not persist between the harness's
command invocations, so the realistic source of a leak is `~/.zshrc` or a
`window.env` sourced by hand — not a stray `export` in an earlier step.

## 9. Method, and what this inventory could not establish

**Method (NR-10).** Every command was taken from the runbook at `3c96b18f` and,
where the runbook defers to it, from `s0-runsheet-r4.md` at the same head, then
rewritten into the real-lane invocation form the runbook rules: the measurement
checkout's own `.venv/bin/python3`, the `python3` spelling, bare relative paths,
issued from a working directory already at `MEAS`. Each resulting literal string
was compared against all 24 allow rules by hand.

**The probes.** Two harmless `--help` variants of the licensed classes were
executed at the measurement checkout:

```
.venv/bin/python3 scripts/project_identity_pins.py freeze --help
.venv/bin/python3 scripts/generate_arm_readiness.py freeze --help
```

Both returned argparse usage and exit 0, which confirms the measurement venv
resolves and both subcommands exist with the flags this inventory records. It
confirms **nothing about prompting**, for two reasons, and both are recorded
rather than glossed:

1. **The prompt is not observable from inside.** A command that is auto-approved
   and a command that was never going to prompt look identical from the tool's
   side. Nothing in the transcript distinguishes them.
2. **The probe could not use the real invocation form.** These probes ran as
   `cd /Users/edr/JouleWise-measurement-20260813 && …` — a different literal
   string from the bare relative form the runbook rules, and one that matches
   different rules (specifically, none).

Every row this affects is marked **UNCERTAIN-PROBE** rather than assigned a
class. The rule-table implication is stated in each row's reason column.

**What is solid.** The rule inventory (§3), the non-matching of every `_v3` and
`--help` rule against the six `_v4` literals (§6.1), the array-ordering evidence
about rules 3 and 4 (§6.2), the `auto` default mode (§7 item 1), the absence of
any permission file inside the measurement checkout (§3), and the two
environment variables and their defaults (§8) were all read directly from the
files named.

**What is not.** Whether rule 4 glob-matches at execution time; and what the
`auto` classifier does with any given unmatched command on the night. NEEDS-ED
items 1 and 2 exist so that neither question has to be answered correctly for
the transaction to be safe.

---

**Sources.** `docs/process_traces/2026-08-22-t20/real-transaction-runbook.md`
(Phases A–H, §1.5, §7 NR-10) · `docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md`
§§1.1, 1.3, 2.1, 2.2, 3.1–3.10 · `docs/phase_2/window_runbook.md` §5C (the
amended three-pack producer) · `docs/process/ed-s5-mint-decision-2026-08-19.md`
(the `_v3` blocked-class precedent) · `scripts/window_status.sh`,
`scripts/generate_arm_readiness.py`, `scripts/project_identity_pins.py` at
`3c96b18f` · `/Users/edr/.claude/settings.json` and
`/Users/edr/code/JouleWise/.claude/settings.local.json`, read 2026-08-26 and
never modified.
