# Post-seal runbook for measurement block 5: from "the seal gate's second stage has passed" to "the stop ref is deleted"

**State of this copy (2026-10-08).** This is the runbook as it was committed beside the seal record. The
orchestrator's decisions of 2026-10-07 23:55 on the hand-off drafts are applied in the text: the directory and the
file names of the seal record and of the gate's records; the harvest addendum as a section of the seal record;
the arm record among what the magistrate may open; no closing of the owner's issues; the owner's answers left at
their defaults. Every value that was known when the copy was made is filled in. Steps 0 to 7 had been run by
then, and each carries a paragraph "As run" that says what departed from the printed step. Steps 8 to 15 had not
been run and are printed as planned; a value that did not exist yet is marked with the word PENDING and a name in
square brackets. What each step printed is in `00-seal-and-arm-record.md` beside this file. The owner's mail
address is not printed in this copy: it is held in the local file
`/Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh` and nowhere in the repository.

This is the list of steps the orchestrator runs, in order, on the night of the seal. The **orchestrator** is
the interactive Opus 5.5 session that leads the work. It starts when the seal gate's second stage has ended
with the line `SEAL: ADMIT`, and it ends when the remote branch `ops/stop-pause` is deleted. That deletion
releases the **magistrate**: the headless Opus 5.5 session that a scheduled job, the **watchdog**, starts on
this Mac whenever no measurement window is in progress. While a remote branch named `ops/stop*` exists the
watchdog starts nothing; the branch is called the **stop ref**. From the release on, the magistrate works
alone from its brief (`40-magistrate-brief.md` beside this file), and arms the first window about 35 minutes
later.

## How to read a step

Each step gives the directory, the exact command, the output to expect, the check that proves the step, and
one of two statuses:

- **ESTABLISHED**: the command exists in the code or was run in a recorded procedure. The citation follows.
- **UNKNOWN**: the command or its outcome could not be established. The step says what was looked at and what
  to do if it does not behave as written.

**One rule for every command block.** Each Bash tool call of a Claude Code session starts a new shell. A
variable set in one call is empty in the next, and `cd ""` returns 0 and stays where it was. So this runbook
keeps its values in one file, `/Users/edr/night-plan-staging/b5-bench/runbook-env.zsh`. Step 0 creates it,
each later step appends what it learns, and every command block begins by sourcing it. (Probed on 2026-10-07
by the pre-mortem's magistrate lens and by its synthesizer; `PREMORTEM.md` finding M5.)

## Terms

- A **window** is one unattended measurement run. Block 5 has three **packs** (fixed sets of experiment
  inputs), run in the order ALPHA, BETA, GAMMA; ALPHA-1 is the first attempt of ALPHA.
- A **window input** is a tracked file a window can read while it is planned, armed or run: every file under
  `joulewise/`, `scripts/` and `configs/`, and the one document `docs/phase_2/window_runbook.md`.
- **H_claim**, also called the **head commit**, is the last commit that changes a window input. The three
  **seal documents** are `sealed_inventory.json`, `registration_block5.md` and `analysis_plan_block5.md` in
  `configs/campaigns/v5_claim_25g83/`. The **sealed inventory** lists the SHA-256 of every file under
  `joulewise/`, `scripts/` and the three packs as H_claim holds them, and names H_claim in its `head` field. A
  file cannot name the commit that contains it, so the filled inventory lands one commit later: the **seal
  commit** is the only child of H_claim on the integration branch and changes only the three seal documents. The **record commit** is
  the child of the seal commit; it changes no window input and adds the **seal record**, the document that
  lists the SHA-256 of every sealed file.
- The **measurement clone** is the one git checkout every window of the block runs from. The **desk clone**
  (the brief calls it the desk root) is a second checkout, from which the **harvest** runs: the program that
  checks a finished window's bytes and writes its verdict. The **canonical root** is
  `/Users/edr/code/JouleWise`, the checkout the watchdog and the magistrate run from.
- The **harvest lane** is the branch `lane/2026-10-07-harvest-lane`, which carries the harvest changes the
  seal gate's first stage required. A **harvest addendum** is a section appended to the seal record that
  names the commit the desk clone is checked out at and the SHA-256 of each harvest program file. The harvest
  program is **pinned** when the addendum's line `B5-HARVEST-PIN: <that commit>` is in the canonical root's
  copy of the seal record. The magistrate harvests only with a pinned program.
- The **calibration ledger** is the append-only file of calibration captures in the measurement clone
  (`runs/calibration_observation_ledger.jsonl`); the **pin** is the committed file that names its last row.
- The **agent census** is the listing of Claude and Codex processes that a window takes at its start time
  **t0** and every 30 seconds afterwards. A window refuses to start, or stops, when the census finds one.

## Values

| Name | What it is | Value |
|---|---|---|
| `B5-DOCS` | the directory, relative to the repository root, that holds the seal record and the hand-off records | `docs/process_traces/2026-10-07-block5-seal`: the sealed registration prints the seal record as `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md`, and the brief's harvest test reads that file |
| `H-CLAIM` | 40 hexadecimal characters: the head commit | `a64000884ef5bb4b76415835f02f39803f6eb620` |
| `DESIGN-HEAD` | the commit of the design branch whose registration and analysis plan stage 2 admitted | `cf92f73ec207634d5b2b3a76cae41d3e626befee` |
| `REG-SHA256` | SHA-256 of the admitted registration | `4d321fe3756076aed508dbed4284b2103cdc4e9c1adc18f496e9d3a617410841` |
| `PLAN-SHA256` | SHA-256 of the admitted analysis plan | `1172a4501e2311a98508e6102420de657daa88c8c455603717b8ff7b2a1e1b8a` |
| `INVENTORY-SHA256` | SHA-256 of the sealed inventory | `57ee5d4a8ce632dfca7858f8f834d75dce463276b35fffc4edad91af2d76312a` |
| `CATALOG-SHA256` | SHA-256 of the flag catalog | `5d77c725d4bf482bd667ca4c3a926e2f6471d55d196cd4b4addee435da01ee8d` |
| `SIZING-SHA256` | SHA-256 of the sizing output | `89e7ea70be34d855285c7d2c87df42b646d179a632a1e05ed57a4682a961b3aa` |
| `SEAL-HEAD` | the seal commit (step 2 wrote it into `runbook-env.zsh`) | `ab7b21e576a2d74f0b25d9a26b463d6934588368` |
| `MEASUREMENT-ROOT` | the measurement clone's path (step 3 wrote it into `runbook-env.zsh`) | `/Users/edr/night-custody/measurement/JouleWise-measurement-20261008T0817Z-b5` |
| `HARVEST-LANE-HEAD` | the head of the harvest lane as its review and its cold pass judged it | `c10257418a9d7d2173bec306c0b1deb38e144343`; with H_claim merged in (step 7) it is `7e6158d669cbb6fb35761aee18abf363f07c5d36`, the commit the desk clone is checked out at |
| `E-2a`, `E-2b`, `E-3`, `E-4`, `E-6` | Ed's answers to the questions in the exit email | the defaults stand (`NO`, `NO`, `NO`, `1800`, `NO`): the orchestrator's decision of 2026-10-07 23:55 |

Everything else the steps compute.

---

## Step 0. The values file, and the state at the start

- **Directory:** any.
- **Command:**
```zsh
mkdir -p /Users/edr/night-plan-staging/b5-bench /private/tmp/b5-seal
cat > /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh <<'EOF'
# Values of the post-seal runbook for block 5. Each step appends what it learns.
export REMOTE_URL=https://github.com/mpmdw/JouleWise
export PR_BRANCH=integrate/2026-10-07-int5
export W=/Users/edr/code/JouleWise-wt-int5
export CANON=/Users/edr/code/JouleWise
export BENCH=/Users/edr/night-plan-staging/b5-bench
export NOTES=/Users/edr/night-archive/gate-prune/wave-1007b
export D5=configs/campaigns/v5_claim_25g83
export T=/private/tmp/b5-seal
export B5_DOCS='docs/process_traces/2026-10-07-block5-seal'
export H_CLAIM='a64000884ef5bb4b76415835f02f39803f6eb620'
export REG_SHA256='4d321fe3756076aed508dbed4284b2103cdc4e9c1adc18f496e9d3a617410841'
export SIZING_SHA256='89e7ea70be34d855285c7d2c87df42b646d179a632a1e05ed57a4682a961b3aa'
EOF
/bin/zsh -n /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh && cat /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh
launchctl list | awk '$3 ~ /^com[.]joulewise[.]night/ {print $3}'
ls /Users/edr/night-custody | grep -c '^v5-b5-'
git ls-remote https://github.com/mpmdw/JouleWise.git 'refs/heads/ops/stop*'
python3 -c 'import json; s=json.load(open("/Users/edr/night-custody/magistrate/state.json")); print(s["state"], s["reason"])'
```
- **Expected:** the file is printed; the `launchctl` line prints nothing (no window job is loaded); the count
  is `0` (no block-5 plan exists); `ls-remote` prints one line ending `refs/heads/ops/stop-pause`; the last
  line begins `STOPPED`.
- **Check:** all four as expected. `W` is the worktree of the integration branch, the branch pull request
  #489 is opened from; `T` is scratch, and its path contains neither "claude" nor "codex" (the agent census
  matches those strings in a path).
- **Status:** ESTABLISHED. All four readings were taken on 2026-10-07 between 23:20 and 23:45 PDT with the results above.
  The stop mechanism is `magistrate_watchdog.py` `STOP_REF_GLOB` and `remote_stop_probe`.
- **As run** (2026-10-08, about 01:10 PDT). The four readings were as expected. The values file was written
  without `REG_SHA256` and `SIZING_SHA256` at first; the later steps appended those two and `CATALOG_SHA256`,
  `SEAL_HEAD`, `PLAN_SHA256`, `INVENTORY_SHA256`, `IDENTITY_PINS_SHA256`, `MEASUREMENT_ROOT`, `PY` and
  `HARVEST_HEAD` as each became known.

## Step 1. The head commit: confirm that H_claim is what stage 2 judged

- **Directory:** any (the commands name the worktree).
- **Command:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh
test "$(git -C "$W" rev-parse HEAD)" = "$H_CLAIM" && echo "the integration worktree is at H_claim"
test -z "$(git -C "$W" status --porcelain=v1 --untracked-files=all)" && echo "worktree clean"
git ls-remote "$REMOTE_URL" "refs/heads/$PR_BRANCH"
for c in 2737ef88c 4070d7a95 a0920cb8c; do git -C "$W" merge-base --is-ancestor "$c" "$H_CLAIM" && echo "$c is in H_claim"; done
git -C "$W" show "$H_CLAIM:$D5/flag_catalog.json" | shasum -a 256
git -C "$W" show "$H_CLAIM:$D5/flag_catalog.json" | python3 -c 'import json,sys; print("cell minimum", json.load(sys.stdin)["rules"]["cell_unit_minimum"])'
git -C "$W" show "$H_CLAIM:$D5/sizing_b5.json" | shasum -a 256
git -C "$W" show "$H_CLAIM:$D5/sealed_inventory.json" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["status"], d["head"], d["files"])'
( cd "$W" && TMPDIR="$T" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_b5_seal_landing 2>&1 | tail -3 )
```
- **Expected:** the two `echo` lines; `ls-remote` prints H_claim (the branch is pushed); three lines
  `… is in H_claim`; the catalog's digest equals
  `5d77c725d4bf482bd667ca4c3a926e2f6471d55d196cd4b4addee435da01ee8d`; `cell minimum 5`; the sizing digest
  equals `89e7ea70be34d855285c7d2c87df42b646d179a632a1e05ed57a4682a961b3aa`; `STUB_NOT_SEALED None None`; `OK`.
- **Check:** the three ancestors are the seal-landing change (`2737ef88c`: without it every window is
  excluded because the seal landed), the documents commit (`4070d7a95`: the hand-back text the window's
  courier reads from the measurement clone, and the relaunch prompt) and the seal-rulings lane (`a0920cb8c`:
  the cell minimum of 5). If a later commit replaced one of them, check for that commit instead. The
  inventory at H_claim is still the stub, and the landing test passes in the stub state.
- **What must already be on record for H_claim** (gates that ran before stage 2; this step only cites them):
  the whole suite and the refusal census at H_claim, and every Linux job of CI green on a tree whose files
  under `joulewise/`, `scripts/` and `configs/` equal H_claim's (the orchestrator's decision O-1). Write
  their paths into the hand-off record of step 8.
- **Status:** ESTABLISHED (`SEAL_LANDING.md` section 4, step 1). The commands were run on 2026-10-07 at
  about 23:40 PDT against `cc0b3446d`, the integration head at that time: `2737ef88c` and `a0920cb8c` are in it,
  the cell minimum is 5, the inventory is the stub, and the landing test passes (9 tests). **`4070d7a95` was
  not in it yet:** the documents lane `lane/2026-10-07-prefreeze-docs` must be merged into the integration
  branch before the head is frozen, or the measurement clone will hold the block-1 hand-back text.
- **As run** (2026-10-08 01:10 PDT). Every check passed at H_claim `a64000884ef5bb4b76415835f02f39803f6eb620`. The
  documents commit `4070d7a95` had been merged into the integration branch at `4394ca891` on 2026-10-07, so all
  three commits of the loop are in H_claim. Two further commits changed a window input after the commits the
  loop names and before H_claim: the admitted flag catalog and one sentence of the refusal allowlist, both at
  `1704059cc`, as the seal gate's stage 2, part A required. The catalog digest and the cell minimum that this
  step checks are the ones of that commit.

## Step 2. The seal commit

- **Directory:** `/Users/edr/code/JouleWise-wt-int5`.
- **Command, part 1: generate the inventory from H_claim and place the admitted text.**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh; cd "$W" || exit 3
DESIGN=/Users/edr/code/JouleWise-wt-ia-claim; DESIGN_HEAD='cf92f73ec207634d5b2b3a76cae41d3e626befee'
/opt/homebrew/bin/python3.13 -B "$NOTES/seal-land/make_sealed_inventory.py" "$W" "$T/sealed_inventory.json"
cp "$T/sealed_inventory.json" "$D5/sealed_inventory.json"
git -C "$DESIGN" show "$DESIGN_HEAD:$D5/registration_block5.md" > "$D5/registration_block5.md"
git -C "$DESIGN" show "$DESIGN_HEAD:$D5/analysis_plan_block5.md" > "$D5/analysis_plan_block5.md"
shasum -a 256 "$D5/sealed_inventory.json" "$D5/registration_block5.md" "$D5/analysis_plan_block5.md"
grep -o 'FILL\[[A-Z0-9-]*\]' "$D5/registration_block5.md" "$D5/analysis_plan_block5.md" | sort | uniq -c
git status --porcelain=v1 --untracked-files=all
```
- **Expected:** the generator prints `head=<H_claim> files=<n> sha256=<…>`; the three digests equal
  `57ee5d4a8ce632dfca7858f8f834d75dce463276b35fffc4edad91af2d76312a`,
  `4d321fe3756076aed508dbed4284b2103cdc4e9c1adc18f496e9d3a617410841` and
  `1172a4501e2311a98508e6102420de657daa88c8c455603717b8ff7b2a1e1b8a`; `git status` prints exactly three
  lines, each ` M` followed by one of the three paths.
- **Check on the `grep` line.** The sealed registration's bytes can never change after this commit: every
  window plan records its SHA-256 and the harvest faults on a difference. So no marker that stands for a
  value may be left in it. A marker name may remain only where the text uses it as the name of a section of
  the seal record (the release event, the regenerated plans). **UNKNOWN:** which marker names the admitted
  text keeps is the stage-2 ruling's to state; compare the `grep` output with that ruling, and do not commit
  if a marker stands where a value belongs.
- **Command, part 2: commit, and prove the landing before pushing.**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh; cd "$W" || exit 3
git add "$D5/sealed_inventory.json" "$D5/registration_block5.md" "$D5/analysis_plan_block5.md"
git commit -q -m "Block 5 seal commit: the sealed inventory, the registration and the analysis plan" \
  -m "The only child of H_claim $H_CLAIM. It changes the three seal documents and nothing else: the inventory generated from H_claim, and the registration and analysis plan as the seal gate's second stage admitted them." \
  -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
S="$(git rev-parse HEAD)"
test "$(git rev-list --parents -n 1 "$S" | wc -w)" -eq 2 && test "$(git rev-parse "$S^")" = "$H_CLAIM" && echo "one parent, and it is H_claim"
git diff --name-only --no-renames "$H_CLAIM" "$S"
TMPDIR="$T" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_b5_seal_landing 2>&1 | tail -3
/opt/homebrew/bin/python3.13 -B "$NOTES/seal-land/make_sealed_inventory.py" "$W" "$T/sealed_inventory.at-seal.json"
python3 -c 'import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:3])
assert a["files"] == b["files"], "the files map differs between H_claim and the seal commit"
assert a["head"] == sys.argv[3] and a["status"] == "SEALED", "the committed inventory does not name H_claim"
print("same files map:", len(a["files"]), "files; the committed head is H_claim")' "$D5/sealed_inventory.json" "$T/sealed_inventory.at-seal.json" "$H_CLAIM"
/opt/homebrew/bin/python3.13 -B scripts/gen_state.py --check; echo "gen_state rc=$?"
/opt/homebrew/bin/python3.13 -B scripts/repin.py --check; echo "repin rc=$?"
echo "export SEAL_HEAD='$S'" >> "$BENCH/runbook-env.zsh"
```
- **Expected:** `one parent, and it is H_claim`; the `diff` prints the three seal documents and nothing else;
  the landing test prints `OK` (now in the sealed state); `same files map: … files; the committed head is
  H_claim`; both return codes 0.
- **Check:** the landing test reads stored commits and the generator reads files on disk, so the last two
  are independent readings of the same inventory. If `repin.py --check` or `gen_state.py --check` fails here
  and its cure is a file under `configs/`, `scripts/` or `joulewise/`, stop: that cure is a change to a
  window input and belongs before H_claim, so the seal commit is discarded (`git reset --hard "$H_CLAIM"`,
  nothing was pushed) and the head is frozen again. A cure under `tests/` or `docs/` goes into the record
  commit of step 8.
- **Command, part 3: push.**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh
git -C "$W" push origin "$PR_BRANCH" && git ls-remote "$REMOTE_URL" "refs/heads/$PR_BRANCH"
```
- **Expected:** `ls-remote` prints the seal commit.
- **Status:** ESTABLISHED for the commit shape and its three checks (`SEAL_LANDING.md` section 4, steps 2 to
  4; run end to end on a disposable clone, `../seal-land/proof-landing.log`, and reviewed in
  `../seal-land/REVIEW.md`). UNKNOWN for `repin.py --check` and `gen_state.py --check` at a seal commit:
  neither the landing lane's proof nor its review ran them there. The pin registry
  (`configs/pins/registry.json`) names none of the three seal documents (searched 2026-10-07), so no failure
  is expected.
- **As run** (2026-10-08 01:30 PDT). The seal commit is `ab7b21e576a2d74f0b25d9a26b463d6934588368`: one parent, H_claim;
  its difference from H_claim is the three seal documents; the inventory lists 682 files; the landing test ran 9
  tests, OK; the regenerated map equals the committed one; `gen_state.py --check` and `repin.py --check` both
  returned 0, which settles this step's two UNKNOWN checks. No marker is left in the registration; the analysis
  plan keeps eleven markers that belong to the analysis code, which is written after the windows. Part 3 was not
  run as printed: the seal commit was pushed first to the branch `seal/2026-10-08-block5-seal-candidate`, and
  the integration branch on the remote stayed at H_claim until the seal gate's part B had written its line,
  `SEAL: ADMIT`.

## Step 3. A fresh measurement clone, checked out at the seal commit

- **Directory:** none (the step creates the clone).
- **Why a new clone.** Blocks 1 to 3 each ran from a fresh clone under
  `/Users/edr/night-custody/measurement/` (ten are there). The older checkout the notes name,
  `/Users/edr/JouleWise-measurement-20260818`, was offloaded to iCloud on 2026-10-05 and is not a directory.
- **Command:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh
M="/Users/edr/night-custody/measurement/JouleWise-measurement-$(date -u +%Y%m%dT%H%MZ)-b5"
case "$(printf %s "$M" | tr '[:upper:]' '[:lower:]')" in *codex*|*claude*) echo "an agent-census string is in the path"; exit 3;; esac
test ! -e "$M" || { echo "already exists: $M"; exit 3; }
git clone -q --no-hardlinks "$REMOTE_URL" "$M" && git -C "$M" checkout -q --detach "$SEAL_HEAD"
git -C "$M" config user.name  "Ed R"
git -C "$M" config user.email "edr@Eds-MacBook-Pro.local"
echo "export MEASUREMENT_ROOT='$M'" >> "$BENCH/runbook-env.zsh"
echo "export PY='$M/.venv/bin/python'" >> "$BENCH/runbook-env.zsh"
```
- **The two `git config` lines.** After every window a program makes one commit in this clone (the pin
  advance), so the clone needs a commit identity, and this machine has no global one. The identity set here
  is the one every commit of the earlier measurement clones carries, and the one the integration branch's
  own commits carry (`git log -1 --format='%an <%ae>'` in the integration worktree, and in eight of the ten
  earlier clones, printed `Ed R <edr@Eds-MacBook-Pro.local>` on 2026-10-07). It is the address git derives
  from the machine's host name, it is already public in the repository's history, and it is not the address
  Ed receives mail at. That mail address appears in no `git config` line and in no command of this runbook
  except as the recipient of a Gmail message.
- **Check:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh; C="$MEASUREMENT_ROOT/$D5"
test "$(git -C "$MEASUREMENT_ROOT" rev-parse HEAD)" = "$SEAL_HEAD" && test "$(git -C "$MEASUREMENT_ROOT" rev-parse "$SEAL_HEAD^")" = "$H_CLAIM" && echo "the clone is at the seal commit, whose parent is H_claim"
git -C "$MEASUREMENT_ROOT" diff --name-only --no-renames "$H_CLAIM" HEAD
test -z "$(git -C "$MEASUREMENT_ROOT" status --porcelain=v1 --untracked-files=all)" && echo "clone clean"
test "$(shasum -a 256 "$C/registration_block5.md" | cut -d' ' -f1)" = "$REG_SHA256" && echo "registration digest equals the seal's"
test "$(shasum -a 256 "$C/sizing_b5.json" | cut -d' ' -f1)" = "$SIZING_SHA256" && echo "sizing digest equals the seal's"
python3 -c 'import json, sys
d = json.load(open(sys.argv[1]))
assert d["files"], "the inventory is still the stub"
assert d["head"] == sys.argv[2], "the inventory names another commit than H_claim"
print("the inventory is filled and names H_claim")' "$C/sealed_inventory.json" "$H_CLAIM"
```
- **Expected:** the five `echo` and `print` lines, and the `diff` lists exactly the three seal documents.
- **Why the `diff` matters.** At a window's start the driver compares the clone with the plan's own head,
  which the installer forces to equal the clone's head, so that comparison is the clone with itself. The
  harvest is the first program to compare a window with H_claim, after the window has run its whole span.
  This `diff`, and the desk seal check of step 6, make the comparison before any window. (`PREMORTEM.md`
  findings PD-6, SC-3.) It is a full clone, made without `--depth`, because the harvest's comparison needs
  H_claim in the clone's history.
- **One clone for the whole block.** It is never pulled, fetched, merged, checked out, edited or deleted
  before the release of the measured values. Its only later commits are pin advances, each changing
  `configs/calibration/calibration_ledger_head.json` alone.
- **Status:** ESTABLISHED (the block-3 arm recipe
  `docs/process_traces/2026-10-03-design-block3/40-g2a-b3-arm-recipe.md`, `step1-clone.zsh`, run for five
  real windows; `SEAL_LANDING.md` section 4, step 7). The two lenses of the pre-mortem built scratch clones
  by these commands.
- **As run** (2026-10-08). The clone is `/Users/edr/night-custody/measurement/JouleWise-measurement-20261008T0817Z-b5`.
  Every check printed what the step expects.

## Step 4. The relock, and `brew pin python@3.13`

- **Directory:** the measurement clone. It needs the network (the Python package index) for about two
  minutes.
- **What a relock is.** Building a new virtual environment in the clone from the committed lock file
  `env/mac-measurement-lock.txt` (37 pinned packages) and accepting it only when the installed list equals
  the lock line for line.
- **Command:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh; cd "$MEASUREMENT_ROOT" || exit 3
test "$(/opt/homebrew/bin/python3.13 --version)" = "Python 3.13.1" && echo "Python 3.13.1"
HOMEBREW_NO_AUTO_UPDATE=1 brew pin python@3.13 && HOMEBREW_NO_AUTO_UPDATE=1 brew list --pinned
/opt/homebrew/bin/python3.13 -m venv .venv
"$PY" -m pip install -q -c env/mac-measurement-lock.txt -e ".[mac]"
"$PY" -m pip install -q -c env/mac-measurement-lock.txt charset-normalizer requests urllib3
```
- **Expected:** `Python 3.13.1`; the pinned list prints `python@3.13`; the three install commands print
  nothing.
- **Why the pin.** The clone's interpreter is not a copy: `.venv/bin/python` is a chain of links ending in
  Homebrew's `python@3.13`. An upgrade of that formula (3.13.16 is pending, and nine installed formulae
  depend on it) changes the interpreter of the existing environment in place. The sealed interpreter digest
  covers the string 3.13.1, so every window armed afterwards would run its whole span and be excluded.
  (`PREMORTEM.md` finding CE-3.) `brew list --pinned` printed nothing on 2026-10-07 between 23:20 and 23:45 PDT: the pin is
  not set yet.
- **Check 1, the lock:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh; cd "$MEASUREMENT_ROOT" || exit 3
diff -u <(grep -Ev '^(#|[[:space:]]*$)' env/mac-measurement-lock.txt | sort) <("$PY" -m pip freeze --exclude-editable | sort) && echo "the environment equals the lock"
"$PY" -m pip check
test -z "$(git status --porcelain=v1 --untracked-files=all)" && echo "clone clean"
```
- **Check 2, the sealed interpreter digest:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh; cd "$MEASUREMENT_ROOT" || exit 3
PYTHONDONTWRITEBYTECODE=1 "$PY" -B -c '
import json, sys
from joulewise.flags import collect
versions = collect.runtime_versions(sys.argv[1])
pin = json.load(open("configs/campaigns/v5_claim_25g83/identity_pins.json"))["runtime_versions_sha256"]
print(collect.runtime_versions_sha256(versions), pin)
assert collect.runtime_versions_sha256(versions) == pin, "the relocked interpreter is not the pinned one"
' "$PY"
```
- **Check 3, every identity unit against this interpreter and the model files on disk:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh; cd "$MEASUREMENT_ROOT" || exit 3
mkdir -p "$T/pins-check"
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/write_b5_identity_pins.py --repo "$MEASUREMENT_ROOT" --runtime-python "$PY" --hash-local-models --out "$T/pins-check/identity_pins.regenerated.json" > /dev/null; echo "generator rc=$?"
python3 -c 'import json, sys
new, sealed = (json.load(open(p)) for p in sys.argv[1:3])
for doc in (new, sealed):
    doc["sources"]["runtime_probe"].pop("python")     # the probed interpreter path: differs for every clone
for key in ("units", "runtime_versions", "runtime_versions_sha256", "sources"):
    assert new[key] == sealed[key], key + " differs from the sealed pins"
print("equal to the sealed pins:", sorted(new["units"]))' "$T/pins-check/identity_pins.regenerated.json" configs/campaigns/v5_claim_25g83/identity_pins.json
```
- **Expected:** check 1 prints `the environment equals the lock`, `No broken requirements found.` and
  `clone clean`; check 2 prints `9033a69906aab1f0ff5724b5a6c2f3efd623512ee49a7048713e2410e701c794` twice;
  check 3 prints `generator rc=0` and `equal to the sealed pins:` with nine names.
- **If a check fails.** A package that cannot be installed at its pinned version is a stop, not a
  substitution. A failed check 3 is never cured by writing a new `identity_pins.json`: that file is a window
  input, and the edit would exclude every window.
- **Status:** ESTABLISHED (the three install commands are the block-3 recipe and the relock records of
  2026-08-27 and 2026-09-02; check 2's digest was read from the block-3 clone of 2026-10-04, built by the
  same commands; check 3 was run with its correction by two pre-mortem lenses on scratch clones,
  `PREMORTEM.md` findings CE-1 and SC-4). `brew pin` is an ordinary Homebrew command and was not run before
  tonight because it changes a machine setting.
- **As run** (2026-10-08). `brew pin python@3.13` returned 0, and the pinned list then printed `python@3.13`
  (nothing was pinned before). The install commands were not silent: pip printed its notice of a newer pip
  twice and, on the second install, a warning that `charset-normalizer` 3.4.8, the version the lock pins, is a
  release its publisher has withdrawn. Neither changed what was installed: check 1 printed that the
  environment equals the lock (37 lines), check 2 printed the sealed digest twice, and check 3 printed nine
  units equal to the sealed pins.

## Step 5. The ledger seed

- **Directory:** the measurement clone.
- **What the seed is.** Block 5 starts from the calibration ledger as block 3 left it: 402 rows, with the
  committed pin naming row 402 (registration section 4.6 item 6). The seed is a copy of block 3's terminal
  ledger, placed at the one path the code reads.
- **Command:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh; cd "$MEASUREMENT_ROOT" || exit 3
SEED=/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2/derived/terminal-ledger.jsonl
LEDGER="$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
test "$(shasum -a 256 "$SEED" | cut -d' ' -f1)" = 6ee89e5a1b83c88d865a65cca71177d19a4b23b47d6af2979f92a6840857530e || exit 3
mkdir -p "$MEASUREMENT_ROOT/runs"; test ! -e "$LEDGER" || { echo "a ledger is already there"; exit 3; }
rsync -a --checksum "$SEED" "$LEDGER" && cmp "$SEED" "$LEDGER" && echo "seed installed"
```
- **Check:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh; cd "$MEASUREMENT_ROOT" || exit 3
PYTHONDONTWRITEBYTECODE=1 "$PY" -B -c '
import json; from pathlib import Path; from joulewise.b5 import plan
s = plan.ledger_head_status(Path(".").resolve())
assert s["blocking"] == [] and s["open_sessions"] == [] and s["physical"]["sequence"] == s["pinned"]["sequence"] == 402, s
print("ledger head 402 equals the committed pin; nothing blocks a plan")'
PYTHONDONTWRITEBYTECODE=1 "$PY" -B -c '
from pathlib import Path
from joulewise.calibration_ledger import load_calibration_ledger_snapshot as load
root = Path(".").resolve(); pin = root/"configs/calibration/calibration_ledger_head.json"
s = load(root/"runs/calibration_observation_ledger.jsonl", pin, repo_root=root, require_committed_pin=True,
         verify_custody=True, mode="read_replay")
print("refusals:", [str(getattr(r, "value", r)) for r in s.refusal_reasons], "head:", s.head_sequence)
assert not s.refusal_reasons'
test -z "$(git status --porcelain=v1 --untracked-files=all)" && echo "clone clean"
```
- **Expected:** `seed installed`; `ledger head 402 equals the committed pin; nothing blocks a plan`;
  `refusals: [] head: 402` in about 5 seconds; `clone clean` (the `runs/` directory is ignored by git).
- **If the second reading reports a refusal:** a capture the ledger names is no longer at its recorded path.
  That is a disclosed flag at the harvest, not a lost window, but find what moved before the release: the
  ledger names 116 older capture directories (in the iCloud Drive folder `JouleWise-backup`, in six custody
  roots `/Users/edr/night-custody/d079-epoch-25g83-*` and under `/Users/edr/night-g2a`).
- **Status:** ESTABLISHED (the block-3 recipe's copy and loader check; both readings were run on scratch
  clones by two pre-mortem lenses on 2026-10-07 with the expected results, `PREMORTEM.md` finding CE-5).
- **As run** (2026-10-08). Both readings were as expected. `runs/` then held the ledger alone: the read-only
  checks of this step made no `.lock` file beside it.

## Step 6. The bench: the helpers, the two files the brief reads, and a scratch plan for each pack

- **Directory:** the measurement clone for the proof; `/Users/edr/night-plan-staging/b5-bench` holds the
  files.
- **What the bench is.** Four small programs the magistrate uses at every arm, kept outside the repository
  because a new file under `scripts/` would be a file the sealed inventory does not list; and two files the
  brief's command blocks read: the fixed values, and Ed's answers.
- **Command 1, the helpers:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh; P="$NOTES/premortem"
cp "$P/b5_plan_inputs.py" "$P/b5_desk_identity.py" "$P/b5_agent_check.py" "$P/seal-consistency-probes/b5_desk_seal_check.sh" "$BENCH/"
( cd "$BENCH" && shasum -a 256 b5_plan_inputs.py b5_desk_identity.py b5_desk_seal_check.sh b5_agent_check.py )
```
- **Expected:**
  `f77f60c16e2122e1aa0cfe1ef2eb47fb88808e969cc8f5c7319766d664420f3b  b5_plan_inputs.py`,
  `6c46fab80ed8f6d9b1d57949211a8197f70dd510e4559eeeb6415ab44dea48cf  b5_desk_identity.py`,
  `c609714cb3eb745e474870295fe47b93f040e2a46d7bfd5f126e5d32fac5b381  b5_desk_seal_check.sh`,
  `5d6fac1279430998cc3219a73d4a02914479443a342ebe594ad01c364d14080d  b5_agent_check.py`
  (the digests of the source files, read again on 2026-10-07 between 23:20 and 23:45 PDT). The brief prints the same four.
- **Command 2, the fixed-values file and the answers file:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh
cat > "$BENCH/b5-fixed-env.zsh" <<EOF
# Fixed values of measurement block 5. Every command block of the magistrate brief sources this file first.
export MEASUREMENT_ROOT='$MEASUREMENT_ROOT'
export PY='$MEASUREMENT_ROOT/.venv/bin/python'
export H_CLAIM='$H_CLAIM'
export SEAL_HEAD='$SEAL_HEAD'
export REG_SHA256='$REG_SHA256'
export BENCH='$BENCH'
export DESK_ROOT=/Users/edr/night-custody/desk/b5-harvest
export HARVEST_ADDENDUM='$CANON/$B5_DOCS/SEAL_RECORD.md'
export RECORDS_BRANCH=records/2026-10-block5
export RECORDS_WT=/Users/edr/code/JouleWise-wt-b5-records
export ANSWERS='$BENCH/owner-answers.txt'
export NOTICE_TO='<the notice address of the owner: typed here when this step is run, kept in this local file only>'
# A window's own values (written by brief section 5.2): set P to its plan id before sourcing this file.
if [ -n "\${P:-}" ]; then source "/Users/edr/night-plan-staging/\$P/arm-env.zsh" || echo "no arm-env.zsh for plan id \$P"; fi
EOF
/bin/zsh -n "$BENCH/b5-fixed-env.zsh" && cat "$BENCH/b5-fixed-env.zsh"
cat > "$BENCH/owner-answers.txt" <<'EOF'
E-2a=NO
E-2b=NO
E-3=NO
E-4=1800
E-6=NO
EOF
cat "$BENCH/owner-answers.txt"
```
- **Expected:** both files are printed; every value of the first is a literal (no `$` is left except in the
  last line, which is meant to be evaluated when the file is sourced).
- **The answers file starts with the defaults.** Each line is one of Ed's answers; the brief's section 2
  says what each means. Replace a line when Ed answers, for example
  `sed -i '' 's/^E-2a=.*/E-2a=YES/' /Users/edr/night-plan-staging/b5-bench/owner-answers.txt`. The defaults
  stand as written (the orchestrator's decision of 2026-10-07 23:55); a question he has not
  answered by step 15 keeps its default, and the magistrate replaces the line itself when his answer arrives
  by mail.
- **The line `NOTICE_TO`** holds the address Ed reads. It is written into this local file so that the
  magistrate passes it to the Gmail tool as a recipient, and it is used for nothing else. This copy of the
  runbook does not print it, and the copy of the file under `bench/` in the repository does not either.
- **Command 3, for each pack, write a plan in scratch from the real clone and check it.** Nothing is created
  under `/Users/edr/night-custody`, so the watchdog never sees these plans.
```zsh
source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; cd "$MEASUREMENT_ROOT" || exit 3
S="/private/tmp/b5-seal/planproof-$(date +%s)"; mkdir -p "$S"; echo "$S" > /private/tmp/b5-seal/planproof.path
T0=$(( ( $(date +%s) / 60 + 120 ) * 60 ))
for PACK in alpha beta gamma; do
  ID="PROOF-b5-$PACK"; D="$S/$ID"; mkdir -p "$D/stage" "$D/runs"
  PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$BENCH/b5_desk_identity.py" --measurement-root "$MEASUREMENT_ROOT" --stage-dir "$D/stage"
  PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$BENCH/b5_plan_inputs.py" --measurement-root "$MEASUREMENT_ROOT" --pack "$PACK" \
    --plan-id "$ID" --attempt 1 --t0-epoch-s "$T0" --g10 false --stage-dir "$D/stage" --custody-root "$D/custody" \
    --runs-parent "$D/runs" --claim-backup "$D/backup-claim" --bound-backup "$D/backup-bound" \
    --registration-sha256 "$REG_SHA256"
  PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/write_b5_window_plan.py --inputs "$D/stage/plan-inputs.json" > "$D/plan-record.json"
  python3 -c 'import json, sys
r = json.load(open(sys.argv[1])); p = json.load(open(r["plan"]["path"])); a = r["thresholds_audit"]
assert r["status"] == "STAGED" and a["differences_from_defaults"] == [] and a["keys_not_in_contract"] == [], a
assert p["hazard_window"]["thresholds"]["contention"]["clean_s"] == 180 and not r["pack_digest_error"], r["pack_digest_error"]
print(sys.argv[1], "members", r["member_count"], "window_max_s", r["window_max_s"])' "$D/plan-record.json"
  /bin/zsh -n "$D/custody/chain.zsh" && ( cd "$D/custody" && shasum -a 256 -c chain.zsh.sha256 )
  PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/check_b5_chain.py --plan "$D/custody/night_plan.json" > "$D/chain-check.json"; echo "check_b5_chain rc=$?"
  scripts/install_night_agent.sh --plan "$D/custody/night_plan.json" --python "$PY" --render-only "$D/rendered-agents"
  /bin/zsh "$BENCH/b5_desk_seal_check.sh" "$MEASUREMENT_ROOT" "$H_CLAIM" "$D/custody/night_plan.json" "$D/desk-seal-check"; echo "desk seal check rc=$?"
  shasum -a 256 "$D/stage/plan-inputs.json" "$D/plan-record.json"
done
git status --porcelain=v1 --untracked-files=all; ls "$MEASUREMENT_ROOT/runs"
```
- **Expected, per pack:** `"status": "WRITTEN"` from the identity helper; members 119, 119 and 101;
  `window_max_s` 102180, 104580 and 91020; `chain.zsh: OK`; `check_b5_chain rc=0`; the desk seal check prints
  `no flag: the clone's code, pack, models and interpreter are the sealed ones` and `desk seal check rc=0`.
  At the end `git status` prints nothing and `runs/` holds only the ledger and its `.lock` file.
- **What the desk seal check is.** It runs the four identity checks a window runs at its start, but compares
  the clone with H_claim instead of with the clone's own head, in about ten seconds. Every flag it can print
  removes a whole window, so a flag here means: do not release. The six plan-record and plan-input digests it
  prints go into the seal record's section `B5-PLANS-REGENERATED` (step 8).
- **Status:** ESTABLISHED for the plan writer, the chain check and the installer's render mode (they are the
  repository's programs; the pre-mortem's plans-and-driver lens wrote all three packs' plans this way on
  2026-10-07). The four helpers are new programs of the pre-mortem, each tested in scratch
  (`../premortem/POST_SEAL_RUNBOOK.md`, Appendix A). UNKNOWN until run: the three expected `window_max_s`
  values were read at `9395cecfb`; if H_claim's sizing output differs they differ, and the value to trust is
  the plan record's.
- **As run** (2026-10-08). `b5-fixed-env.zsh` was written with `HARVEST_ADDENDUM` naming `SEAL_RECORD.md`.
  The loop of command 3 was refused by a built-in command check of the session (a false alarm about a
  removal; the loop removes nothing), so the same commands were run pack by pack, unchanged. Each pack gave
  what the step expects: members 119, 119 and 101; `window_max_s` 102180, 104580 and 91020, which settles this
  step's UNKNOWN; the chain check 0; the desk seal check "no flag" with return code 0. `runs/` held the ledger
  alone, with no `.lock` file. The six digests are in the seal record's section "Plans written after the
  seal".

## Step 7. The desk clone at the harvest lane's head

Do this step only if the harvest lane has passed its two gates: an independent executing review and a cold
Fable 5.1 pass, with every finding dispositioned. If it has not when everything else is ready, skip the step
(the orchestrator's decision O-4: the arm does not wait for the lane). The brief's fallback then applies: the
magistrate arms ALPHA only, and after ALPHA-1's window it does this step itself (brief section 4.5, variant
B). What changes in the later steps is said in each.

- **Directory:** `/Users/edr/code/JouleWise-wt-harvest` (the lane's worktree), then none.
- **Why the lane's head must descend from H_claim.** The seal gate's stage-1 ruling requires that
  `git diff --name-only H_claim..<lane head>` list only the files the lane may change, and the brief's
  harvest test requires that H_claim be an ancestor of the desk clone's commit. The lane was cut from
  `9395cecfb`, before H_claim. So H_claim is merged into the lane first. The lane's three program files are
  untouched by that merge exactly when H_claim did not change them after `9395cecfb`, which the first command
  proves; the review and the cold pass then still describe the bytes that are pinned.
- **Command 1, bring the lane onto H_claim:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh; cd /Users/edr/code/JouleWise-wt-harvest || exit 3
LANE_HEAD='c10257418a9d7d2173bec306c0b1deb38e144343'
test "$(git rev-parse HEAD)" = "$LANE_HEAD" && test -z "$(git status --porcelain=v1 --untracked-files=all)" && echo "the lane worktree is at the reviewed head, clean"
git diff --quiet 9395cecfb "$H_CLAIM" -- joulewise/b5/harvest.py joulewise/whole_window.py scripts/harvest_b5_window.py && echo "H_claim did not change the three harvest program files"
git fetch -q origin "$PR_BRANCH" && git merge -q --no-ff -m "Merge H_claim into the harvest lane, so the desk clone's commit descends from the sealed head" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" "$H_CLAIM"
git diff --quiet "$LANE_HEAD" HEAD -- joulewise/b5/harvest.py joulewise/whole_window.py scripts/harvest_b5_window.py && echo "the three files are byte-identical to the reviewed lane head"
git diff --name-only --no-renames "$H_CLAIM" HEAD
git diff --name-only --no-renames "$H_CLAIM" HEAD | grep -v -e '^joulewise/b5/harvest\.py$' -e '^joulewise/whole_window\.py$' -e '^scripts/harvest_b5_window\.py$' -e '^tests/' ; echo "paths outside the permitted list: rc=$? (1 means none)"
TMPDIR="$T" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_b5_seal_landing tests.test_neg8_survivors tests.flags.test_flags_collect 2>&1 | tail -3
git push -q origin lane/2026-10-07-harvest-lane && echo "export HARVEST_HEAD='$(git rev-parse HEAD)'" >> "$BENCH/runbook-env.zsh"
```
- **Expected:** the three `echo` lines; the first `diff` lists only `joulewise/b5/harvest.py`,
  `joulewise/whole_window.py`, `scripts/harvest_b5_window.py` and paths under `tests/`; the `grep` prints
  nothing and `rc=1`; the tests print `OK`. Then run `tests.test_harvest_b5_window` by itself in the same way
  (about ten minutes on a quiet machine; it must print `OK`).
- **If the second `echo` does not print** (H_claim changed one of the three files), the merge is a real
  merge of program text and the review and cold pass no longer describe its result: stop, and treat the lane
  as not passed (skip this step).
- **Command 2, the desk clone:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh
mkdir -p "$(dirname "$DESK_ROOT")"; test ! -e "$DESK_ROOT" || { echo "already exists: $DESK_ROOT"; exit 3; }
git clone -q --no-hardlinks "$REMOTE_URL" "$DESK_ROOT" && git -C "$DESK_ROOT" checkout -q --detach "$HARVEST_HEAD"
test "$(git -C "$DESK_ROOT" rev-parse HEAD)" = "$HARVEST_HEAD" && git -C "$DESK_ROOT" merge-base --is-ancestor "$H_CLAIM" HEAD && test -z "$(git -C "$DESK_ROOT" status --porcelain=v1 --untracked-files=all)" && echo "desk clone at the lane's head, descends from H_claim, clean"
( cd "$DESK_ROOT" && shasum -a 256 joulewise/b5/harvest.py joulewise/whole_window.py scripts/harvest_b5_window.py )
S="$(cat /private/tmp/b5-seal/planproof.path)"
for PACK in alpha beta gamma; do D="$S/PROOF-b5-$PACK"
  PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$NOTES/premortem/seal-consistency-probes/harvest_identity_probe.py" "$DESK_ROOT" "$D/custody/night_plan.json" "$D/harvest-probe" "$PACK" | tee "$D/harvest-probe.out"
done
test -z "$(git -C "$DESK_ROOT" status --porcelain=v1 --untracked-files=all)" && echo "desk clone still clean"
```
- **Expected:** the `echo` line; three digests, which go into the addendum (step 8); for each pack the probe
  prints a line naming the harvest module under the desk clone, no `FLAG` line, `step errors: []`,
  `comparison=compared` and an empty `window_input` list; `desk clone still clean`.
- **What the probe is.** A rehearsal of the harvest's own identity steps, run from the desk clone against the
  real measurement clone, on the scratch plans of step 6. It writes into the scratch custody only.
- **Status:** ESTABLISHED for the clone and the probe (`../premortem/POST_SEAL_RUNBOOK.md` step A5b; the probe
  was run by the seal-consistency lens and its verifier at `9395cecfb`, and the desk clone's path is the
  orchestrator's decision O-6). UNKNOWN for command 1: merging H_claim into the lane is this runbook's
  proposal, because no ruling says how the lane's head comes to descend from H_claim; and the probe has not
  been run against the lane's code, whose identity comparison gained five changes (H-8 to H-12).
- **As run** (2026-10-08, 01:23 to 01:37 PDT). The step was done: the lane had passed its independent
  executing review and its cold Fable pass at `c10257418`
  (`gates/13-harvest-lane-executing-review.md`, `gates/14-harvest-lane-cold-pass.md`), and the orchestrator's
  decision of 2026-10-07 23:55 fixed the desk clone's commit as the lane merged with H_claim. Command 1 ran
  without its `git fetch`, because H_claim was already in the repository's store of commits. The merge was
  clean; its head is `7e6158d669cbb6fb35761aee18abf363f07c5d36`; the three harvest program files are byte-identical
  to the reviewed head's; the five quick modules ran 204 tests, OK, and `tests.test_harvest_b5_window` alone
  ran 204 tests, OK; the lane was pushed. The desk clone is at that head, descends from H_claim and is clean.
  The probe returned 0 for each pack with no `FLAG` line, `comparison=compared` and an empty `window_input`
  list, which settles this step's UNKNOWN for the lane's code.

## Step 8. The record commit

- **Directory:** `/Users/edr/code/JouleWise-wt-int5`.
- **As run** (2026-10-08). This step was prepared away from the integration worktree, on the branch
  `lane/2026-10-08-seal-record` (worktree `/Users/edr/code/JouleWise-wt-record`, created from the seal commit),
  by a separate Opus 5.5 seat, so that it could be written while the gate's part B, the clones and the suite
  were still running. The two command blocks printed below were not run as printed. The gate records were
  copied byte for byte by a script, and four documents were written by scripts kept in
  `/Users/edr/night-archive/gate-prune/wave-1007b/handoff/record/`: the seal record (every digest computed with
  `git show <commit>:<path> | shasum -a 256`), `RULING_STAGE2.md`, the brief and this copy. The seal gate's part
  B then attached a condition to this commit that this step did not foresee: the paths that differ between
  the seal commit and the record commit lie under `docs/` and `tests/` only, and the merge commit holds exactly
  the record commit's files. `RUN_STATE.md` is at the repository's root, so under that condition it is not part
  of the record commit: PENDING[RUNSTATE-LANDING] (the orchestrator's ruling on which commit carries it).
- **What it carries.** Documents, records and tests only; no window input. Everything a later reader, the
  magistrate and the pull request's ledger need from tonight:

  | Path under `docs/process_traces/2026-10-07-block5-seal/` | Content |
  |---|---|
  | `SEAL_RECORD.md` | the seal record (its required content is below) |
  | `RULING_STAGE1.md`, `REFUTER_STAGE1.md`, `RULING_STAGE2.md` | the seal gate's records, under the names the sealed registration prints; the third holds part A's ruling and then part B's |
  | `00-seal-and-arm-record.md` | the hand-off record: what each step of this runbook printed, with the digests |
  | `30-post-seal-runbook.md` | this runbook, markers filled |
  | `40-magistrate-brief.md` | the brief, markers filled |
  | `bench/` | the four helpers; `b5-fixed-env.zsh` as written, except that the owner's address is not printed; `make_sealed_inventory.py`; and `check_seal_record.py`, which recomputes every digest of the seal record |
  | `premortem/PREMORTEM.md`, `premortem/ORCHESTRATOR_DECISIONS.md` | the findings the brief's bracketed ids name, and the decisions on them |
  | `gates/` | the gate records the pull request's ledger cites, and the other reviews, passes and rulings of the seal |

  and outside that directory: `RUN_STATE.md` (the new top block, drafted as `RUN_STATE_BLOCK.md` in `/Users/edr/night-archive/gate-prune/wave-1007b/handoff/`), and
  any test fixture that the seal commit forces to change (the seal-landing ruling F8). Such a fixture names
  lines of a seal document, as `tests/fixtures/d165_rationale_allowlist.json` names lines of the analysis
  plan; the seal commit may not touch it, so it is corrected here.
- **The seal record's required content** (registration section 12, and `SEAL_LANDING.md` section 4 step 5):
  H_claim; the seal commit; the rulings of both stages and the refuter's record, by path; the seats; the
  SHA-256 at the seal commit of `sealed_inventory.json`, `registration_block5.md` and
  `analysis_plan_block5.md`; the SHA-256 at H_claim of `flag_catalog.json`, the three packs' plan trees, the
  model panel, the idle policy, the calibration acceptance, the nine pin-bundle files, `sizing_b5.json`,
  `identity_pins.json` and `docs/phase_2/window_runbook.md`. Then the named sections that exist only after
  the seal commit: "Plans written after the seal" (the six digests of step 6, the helper digests, and the
  sentence that no plan or plan-input file written before the seal exists outside the rehearsal archives),
  "Release event" (empty until the measured values are opened), and, when step 7 was done, the harvest addendum
  in exactly this shape:
```
## Addendum 1: the harvest program (written <date>, by a seat that has read no claim-window energy)

B5-HARVEST-PIN: <the 40-character commit the desk clone is checked out at>

Desk clone: /Users/edr/night-custody/desk/b5-harvest. Files at that commit, with their SHA-256:
joulewise/b5/harvest.py <sha256>; joulewise/whole_window.py <sha256>; scripts/harvest_b5_window.py <sha256>.
The lane: lane/2026-10-07-harvest-lane, items K-4 to K-7 and H-8 to H-13. Its independent executing review:
<path>. Its cold Fable pass: <path>. git diff --name-only <H_claim> <that commit> lists only those three
files and paths under tests/.
```
  The line `B5-HARVEST-PIN:` starts in the first column and holds nothing but the commit: the magistrate's
  harvest test reads it with `grep "^B5-HARVEST-PIN: <commit>$"`. When step 7 was skipped the seal record
  has no such line, and the brief's fallback writes the addendum later.
- **Command 1, place the files:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh; cd "$W" || exit 3
mkdir -p "$B5_DOCS/bench" "$B5_DOCS/premortem" "$B5_DOCS/gates"
fill() { sed -e '/^<!-- DRAFT-NOTE-BEGIN/,/^DRAFT-NOTE-END -->/d' -e "s|FILL\[B5-DOCS\]|$B5_DOCS|g" -e "s|FILL\[MEASUREMENT-ROOT\]|$MEASUREMENT_ROOT|g" -e "s|FILL\[H-CLAIM\]|$H_CLAIM|g" -e "s|FILL\[SEAL-HEAD\]|$SEAL_HEAD|g" -e "s|FILL\[REG-SHA256\]|$REG_SHA256|g" "$1"; }
fill "$NOTES/handoff/MAGISTRATE_BRIEF.md" > "$B5_DOCS/40-magistrate-brief.md"
fill "$NOTES/handoff/POST_SEAL_RUNBOOK.md" > "$B5_DOCS/30-post-seal-runbook.md"
grep -n 'FILL\[' "$B5_DOCS/40-magistrate-brief.md"; echo "markers left in the brief: rc=$? (1 means none)"
cp "$BENCH/b5_plan_inputs.py" "$BENCH/b5_desk_identity.py" "$BENCH/b5_desk_seal_check.sh" "$BENCH/b5_agent_check.py" "$BENCH/b5-fixed-env.zsh" "$NOTES/seal-land/make_sealed_inventory.py" "$B5_DOCS/bench/"
cp "$NOTES/premortem/PREMORTEM.md" "$NOTES/premortem/ORCHESTRATOR_DECISIONS.md" "$B5_DOCS/premortem/"
G=/Users/edr/night-archive/gate-prune
cp "$NOTES/seal-land/REVIEW.md"              "$B5_DOCS/gates/10-seal-landing-review.md"
cp "$NOTES/seal-land/ORCHESTRATOR_RULING.md" "$B5_DOCS/gates/50-seal-landing-dispositions.md"
cp "$NOTES/seal-land/SEAL_LANDING.md"        "$B5_DOCS/gates/12-seal-landing-procedure.md"
cp "$G/cold-pass-5/REPORT.md"                "$B5_DOCS/gates/40-cold-pass-5.md"
cp "$G/seal-gate/RULING_STAGE1.md"           "$B5_DOCS/RULING_STAGE1.md"
cp "$G/seal-gate/REFUTER_STAGE1.md"          "$B5_DOCS/REFUTER_STAGE1.md"
cp "$G/FROZEN_HEAD_4.md"                     "$B5_DOCS/gates/21-frozen-head-4.md"
git status --porcelain=v1 --untracked-files=all | head -40
```
- **Expected:** `markers left in the brief: rc=1`; `git status` lists only new files under `docs/process_traces/2026-10-07-block5-seal/`.
  The runbook's own copy still shows the markers this command does not fill (the stage-2 values, the harvest
  lane's head and Ed's answers): their values are in the hand-off record and the seal record.
  Then, by hand (Opus writes; these are documents a person reads): the seal record; the hand-off record; the
  stage-2 ruling as `RULING_STAGE2.md` (part A's ruling and then part B's, each byte for byte under its own
  heading); the whole-suite record of step 9 as
  `gates/20-whole-suite.md` (added in a second commit, see step 9); the earlier reviews and cold passes
  listed in `PR_BODY_DRAFT.md` (in the same hand-off directory outside the repository); and the top block of `RUN_STATE.md`, pasted above the block that starts
  `**▶▶▶ HANDOFF 2026-10-05 09:45 PDT`.
- **Command 2, find the fixtures the seal commit forces, then commit:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh; cd "$W" || exit 3
TMPDIR="$T" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_d165_rationale_census tests.test_digest_pin_census tests.test_b5_seal_landing tests.flags.test_flags_collect tests.test_docs_freshness tests.test_gen_state tests.test_magistrate_watchdog 2>&1 | tail -4
/opt/homebrew/bin/python3.13 -B scripts/gen_state.py --check; echo "gen_state rc=$?"
grep -c '^B5-ARM-RELEASED: ' RUN_STATE.md
git add -A "$B5_DOCS" RUN_STATE.md tests
git diff --cached --name-only --no-renames | grep -e '^joulewise/' -e '^scripts/' -e '^configs/' -e '^docs/phase_2/window_runbook\.md$'; echo "window inputs staged: rc=$? (1 means none)"
git commit -q -m "Block 5 record commit: the seal record, the hand-off records and the magistrate brief" \
  -m "Documents, records and tests only; no window input. Adds the seal record for seal commit $SEAL_HEAD (H_claim $H_CLAIM), the post-seal runbook as run, the magistrate brief, the bench helpers, the pre-mortem, the gate records the pull request cites, and the block-5 top block of RUN_STATE.md." \
  -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git diff --name-only --no-renames "$SEAL_HEAD" HEAD | grep -e '^joulewise/' -e '^scripts/' -e '^configs/' -e '^docs/phase_2/window_runbook\.md$'; echo "window inputs changed after the seal commit: rc=$? (1 means none)"
git push origin "$PR_BRANCH" && echo "export RECORD_HEAD='$(git rev-parse HEAD)'" >> "$BENCH/runbook-env.zsh"
```
- **Expected:** the tests print `OK` (a failure in `tests.test_d165_rationale_census` or
  `tests.test_digest_pin_census` names the fixture line to correct: correct it, run again); `gen_state rc=0`;
  the count is `1` (the line the magistrate greps is there once, in the first column); both `rc=1` lines.
- **Check:** `git diff --name-only --no-renames <seal commit> <record commit>` lists no window input. That
  is the one rule of this commit; the last `grep` is that check.
- **Status:** ESTABLISHED for the commit's rule and its check (`SEAL_LANDING.md` section 4 step 5; ruling
  F8). UNKNOWN: which fixtures the seal commit forces. Nobody has run the suite on a real seal commit; the
  test modules named above are the ones that read a seal document or a fixture bound to one (searched
  2026-10-07), and the whole suite of step 9 is the complete answer.

## Step 9. The whole suite and CI at the record commit

Both must be green at the record commit, which is the pull request's head (ruling F8). They run at the same
time, and the pre-release readings of step 12 that do not need the merge can be taken while they run.

- **Directory:** a detached worktree at the record commit.
- **As run** (2026-10-08). The whole suite was started at the seal commit while the record commit was being
  prepared (run 9: worktree `/Users/edr/code/JouleWise-wt-suite9`, logs
  `/Users/edr/night-archive/gate-prune/frozen-suite-int5-9/`): PENDING[SUITE].
- **Command 1, the whole suite** by the method of the earlier frozen heads (the body of CI's "Unit tests"
  job in six shards, then the two modules that must run alone):
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh
L=/Users/edr/night-archive/gate-prune/frozen-suite-int5-9; mkdir -p "$L" /private/tmp/int5suite9
git -C "$W" worktree add -q --detach /Users/edr/code/JouleWise-wt-suite9 "$RECORD_HEAD"
cp /Users/edr/night-archive/gate-prune/frozen-suite-int5-8/shard_runner.py "$L/shard_runner.py"
cd /Users/edr/code/JouleWise-wt-suite9 || exit 97
export TMPDIR=/private/tmp/int5suite9 PYTHONDONTWRITEBYTECODE=1 SHARD_COUNT=6
git rev-parse HEAD > "$L/head.txt"
for i in 1 2 3 4 5 6; do
  SHARD_INDEX=$i /opt/homebrew/bin/python3.13 -B - < "$L/shard_runner.py" > "$L/shard$i.log" 2>&1 &
done
wait
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_calibration_exits > "$L/excl_exits.log" 2>&1
/opt/homebrew/bin/python3.13 -B -m unittest tests.test_calibration_writer_crash_matrix > "$L/excl_crash.log" 2>&1
tail -n 4 "$L"/shard?.log "$L"/excl_*.log
```
  Run it as a background task and wait for it: it took about an hour at `9395cecfb` on a loaded machine, and
  the Bash tool ends a foreground command after ten minutes.
- **Expected:** every log ends `OK`, except for the failures known from the run at `9395cecfb` (9,842 tests;
  five failures): three in `tests.test_sample_quiet_predicate_evidence` LoadTests, one in
  `tests.test_v5_s1_qualification` (courier timing), one error in `tests.test_harvest_b5_window`
  WorkerPoolTests. All five pass alone, and the first and last kind are artefacts of this method: they
  reproduce whenever the runner's text is fed on standard input, because a worker process the test starts
  tries to run `<stdin>` again, and they pass when the same runner is a file
  (`/Users/edr/night-archive/gate-prune/frozen-suite-int5-8/`, the `probe_stdin_*` and `probe_file_*` logs).
  Rerun each failing class alone and require `OK`:
  `/opt/homebrew/bin/python3.13 -B -m unittest tests.test_sample_quiet_predicate_evidence tests.test_v5_s1_qualification tests.test_harvest_b5_window`
  (same directory and `TMPDIR`). Any other failure is real: fix it by a commit that changes no window input,
  and run the suite again at the new head.
- **Record:** write `docs/process_traces/2026-10-07-block5-seal/gates/20-whole-suite.md` (the head, the count, the exact last lines of
  each log, the reruns) and commit it to the branch. It is a documents-only commit; it moves the pull
  request's head, so append the new head as `RECORD_HEAD` to `runbook-env.zsh` again and let CI run on it.
  The suite itself is not repeated for a commit that adds one file under `docs/process_traces/`, and the
  record says which head it ran at.
- **Command 2, CI:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh
gh pr checks 489 --repo mpmdw/JouleWise --watch
gh pr view 489 --repo mpmdw/JouleWise --json headRefOid --jq .headRefOid
```
- **Expected:** every check passes (main requires all 18), and the head the pull request reports equals the
  last `RECORD_HEAD`. A red job is fixed, never waived: a test-side cure is a commit here; a cure under
  `joulewise/`, `scripts/` or `configs/` cannot land after H_claim without issuing the seal again.
- **Status:** ESTABLISHED for both commands (`frozen-suite-int5-8/run.sh` is the suite run of 2026-10-07 at
  `9395cecfb`; `.github/workflows/ci.yml`). UNKNOWN: whether feeding the runner as a file instead of on
  standard input removes the artefact failures for the whole run. The earlier seat showed it for the two test
  classes one at a time and did not write the changed run script.

## Step 10. The pull request's six-key ledger

- **Directory:** `/Users/edr/code/JouleWise-wt-int5`.
- **What the six keys are.** The pull request template has five table rows and an Impact statement of six
  lines; a workflow checks them on every push. Each row's evidence is `RUN <path relative to the repository
  root>` or `RUN <commit sha>`, in plain text, and the path must be a file at the pull request's head. That
  is why step 8 committed the gate records. Row 3 is the head's own sha.
- **Command:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh; cd "$W" || exit 3
sed -e '/^<!-- DRAFT-NOTE-BEGIN/,/^DRAFT-NOTE-END -->/d' -e "s|FILL\[B5-DOCS\]|$B5_DOCS|g" -e "s|FILL\[H-CLAIM\]|$H_CLAIM|g" -e "s|FILL\[SEAL-HEAD\]|$SEAL_HEAD|g" -e "s|FILL\[RECORD-HEAD\]|$RECORD_HEAD|g" "$NOTES/handoff/PR_BODY_DRAFT.md" > "$T/pr-body.md"
grep -n 'FILL\[' "$T/pr-body.md"; echo "markers left in the body: rc=$? (1 means none)"
test "$(git rev-parse HEAD)" = "$RECORD_HEAD" && python3 scripts/check_gate_ledger.py --body-file "$T/pr-body.md" --head-sha "$RECORD_HEAD" --repo-root .; echo "ledger rc=$?"
gh pr edit 489 --repo mpmdw/JouleWise --title "Block 5: sealed claim-block code and registration" --body-file "$T/pr-body.md"
gh pr ready 489 --repo mpmdw/JouleWise
```
- **Expected:** `markers left in the body: rc=1` once the markers this command does not fill (the stage-2
  ruling's last line, the suite's tail, CI's result, the inventory's file count, the Opus audit's path) have
  been written in by hand, in `PR_BODY_DRAFT.md` before the command or in `$T/pr-body.md` after it; then
  `gate-ledger: full tier passes (5 rows, Impact statement answered)` and `ledger rc=0`.
- **Check:** the checker passes locally before the body is posted; the pull request's `gate-ledger` check
  passes after it. Pull request #489 exists already as a draft; it is edited and marked ready, and no second
  pull request is opened.
- **Status:** ESTABLISHED (`.github/pull_request_template.md`, `scripts/check_gate_ledger.py`,
  `.github/workflows/gate-ledger.yml`).

## Step 11. The merge, the canonical root, and the records worktree

- **Directory:** any, then `/Users/edr/code/JouleWise`.
- **Command 1, merge with a merge commit:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh
gh pr merge 489 --repo mpmdw/JouleWise --merge
MAIN="$(git ls-remote "$REMOTE_URL" refs/heads/main | cut -f1)"; echo "main is at $MAIN"
git -C "$W" fetch -q origin main && git -C "$W" merge-base --is-ancestor "$SEAL_HEAD" "$MAIN" && git -C "$W" merge-base --is-ancestor "$H_CLAIM" "$MAIN" && echo "main contains H_claim and the seal commit"
test -z "$(git -C "$W" diff --name-only "$RECORD_HEAD" "$MAIN")" && echo "the merge commit has the record commit's tree"
echo "export MAIN_AFTER_MERGE='$MAIN'" >> "$BENCH/runbook-env.zsh"
```
- **Expected:** both `echo` lines. **Never squash or rebase:** either would replace H_claim and the seal
  commit by new commits, and both the landing test and every harvest's comparison need H_claim in main's
  history. The measurement clone stays at the seal commit; it is not moved to the merge.
- **Command 2, fast-forward the canonical root.** The watchdog's script, the relaunch prompt it renders and
  the `RUN_STATE.md` the magistrate reads are files of the canonical root. At its present commit
  (`e0c738e9c`) the root has no block-5 code: the old watchdog cannot parse a block-5 plan, and one plan it
  cannot parse stops every launch. So the root moves before the stop ref is deleted.
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh
launchctl list | awk '$3 ~ /^com[.]joulewise[.]night/ {print $3}'
ls ~/Library/LaunchAgents/ | grep 'com.joulewise.night'
git -C "$CANON" status --porcelain=v1
git -C "$CANON" pull --ff-only
test "$(git -C "$CANON" rev-parse HEAD)" = "$MAIN_AFTER_MERGE" && echo "the canonical root is at the merge"
grep -m1 '^B5-ARM-RELEASED:' "$CANON/RUN_STATE.md"
grep -c '^B5-HARVEST-PIN: ' "$CANON/$B5_DOCS/SEAL_RECORD.md"
grep -c HAZARD_PACK "$CANON/scripts/magistrate_watchdog.py"
grep -n '^PLAN_LEAD_S = \|^TERM_LEAD_S = \|^KILL_LEAD_S = ' "$CANON/scripts/magistrate_watchdog.py"
sed -n '11p;13p' "$CANON/docs/process/MAGISTRATE_RELAUNCH_PROMPT.md" | cut -c1-120
/opt/homebrew/opt/python@3.14/bin/python3.14 "$CANON/scripts/magistrate_watchdog.py" tick --dry-run
```
- **Expected:** the first two lines print nothing (no window job is loaded or installed); `git status` shows
  only the one known untracked backup file `CLAUDE.local.md.bak-20261002T153934`; `the canonical root is at
  the merge`; the released line reads `B5-ARM-RELEASED: alpha beta gamma` when step 7 was done and
  `B5-ARM-RELEASED: alpha` when it was skipped; the pin-line count is `1` when step 7 was done and `0` when
  it was skipped; the `HAZARD_PACK` count is above 0; the three leads read 180, 90 and 60 seconds; the two
  prompt lines are the block-5 wording ("the arming procedure that the top block of `RUN_STATE.md` names",
  "a v2 plan or, in measurement block 5, under a `HAZARD_PACK` plan"); the dry tick prints
  `decision=STOPPED` with the stop ref in its reason.
- **If the dry tick prints `decision=HOLD_UNSAFE`:** the new watchdog cannot read something under
  `/Users/edr/night-custody/`. Read the reason and cure it before step 15.
- **Command 3, the magistrate's records worktree** (the brief's `$RECORDS_WT`):
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh
git -C "$W" worktree add -q -b records/2026-10-block5 /Users/edr/code/JouleWise-wt-b5-records "$MAIN_AFTER_MERGE"
git -C /Users/edr/code/JouleWise-wt-b5-records push -q -u origin records/2026-10-block5 && git -C /Users/edr/code/JouleWise-wt-b5-records status -sb | head -1
```
- **Expected:** `## records/2026-10-block5...origin/records/2026-10-block5`.
- **Status:** ESTABLISHED (`SEAL_LANDING.md` section 4 step 6 for the merge; the relaunch prompt's line 10
  for moving the canonical root with nothing armed; `magistrate_watchdog.py` `build_parser` for the dry
  tick, which writes nothing and launches nothing). The records worktree is an ordinary linked worktree.

## Step 12. The readings before the release

Take them in this order. Readings 1 to 3 need nothing from steps 10 and 11 and can be taken while the suite
and CI run; the rest come after step 11. Every reading must be as expected before step 13.

- **Directory:** as each block says.
- **Reading 1, free disk: at least 170 GiB.**
```zsh
df -g /Users/edr | tail -1
```
  The fourth column is free space in GiB. *Why 170:* a window is refused at its start unless the volume has
  free three copies of the window's planned bytes plus 20 GiB (88 GiB for ALPHA and BETA, 78 for GAMMA), and
  each collected window keeps about 22 GiB. From a free space F before ALPHA, GAMMA starts only if F is at
  least 122, and each repeated attempt needs 22 more: 145 with one repeat, 167 with two. It read 197 GiB on
  2026-10-07 between 23:20 and 23:45 PDT, after the rehearsal scratch was deleted. If it is below 170, delete scratch under
  `/private/tmp` and the worktrees of merged lanes first; nothing the block reads is there.
- **Reading 2, the headless mail path.** The magistrate and the window's courier both send through the Gmail
  connector of the Claude account logged in on this Mac, each as a `claude -p` process started by launchd. A
  send from the interactive session worked on 2026-10-07 at 21:25; a send from a headless process has not
  been tested. (Which account is logged in is Ed's business and is not part of this reading.)
```zsh
source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; mkdir -p /private/tmp/b5-seal/mailtest; cd /private/tmp/b5-seal/mailtest || exit 3
env -i HOME="$HOME" USER="$USER" LOGNAME="$LOGNAME" PATH=/Users/edr/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin \
  /Users/edr/.local/bin/claude -p 'Reply with the one word READY and do nothing else.' --output-format stream-json --verbose \
  --permission-mode auto --permission-prompts none --model opus --effort high > launch-shape.jsonl 2> launch-shape.err; echo "launch shape rc=$?"
head -1 launch-shape.jsonl | python3 -c 'import json, sys
r = json.loads(sys.stdin.readline())
print(r.get("type"), r.get("subtype"), r.get("model"), r.get("permissionMode"))
print([(m.get("name"), m.get("status")) for m in r.get("mcp_servers", [])])'
cd "$MEASUREMENT_ROOT" || exit 3
env -i HOME="$HOME" USER="$USER" LOGNAME="$LOGNAME" PATH=/Users/edr/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin \
  /Users/edr/.local/bin/claude -p "Send one email with the Gmail tool to $NOTICE_TO. Subject: JouleWise block 5, headless mail test. Body: This message tests the path a window's result email takes. No action is needed. Then print the Gmail message id and stop." \
  --output-format text --allowedTools "Read,Glob,Grep,Bash,Edit,Write,mcp__claude_ai_Gmail__send_message" > /private/tmp/b5-seal/mailtest/courier-shape.out 2>&1; echo "courier shape rc=$?"
tail -3 /private/tmp/b5-seal/mailtest/courier-shape.out
test -z "$(git -C "$MEASUREMENT_ROOT" status --porcelain=v1 --untracked-files=all)" && echo "clone still clean"
```
  **Expected:** `launch shape rc=0`; the first record shows the model `claude-opus-5-5`, the permission mode
  `auto`, and the connector `claude.ai Gmail` with the status `connected`; `courier shape rc=0` and a Gmail
  message id; `clone still clean`. Then, with the Gmail tool of this session, find the test message in the
  mailbox. The first command is the watchdog's own launch shape and environment
  (`magistrate_watchdog.py` `SESSION_ARGV_AFTER_PROMPT`; the launchd job's `PATH`); the second is the
  courier's (`scripts/run_night.py` `COURIER_ALLOWED_TOOLS`), run from the measurement clone as the driver
  runs it. `USER` and `LOGNAME` are passed because the same program reports "Not logged in" without them.
  **If the send fails,** the release does not wait for a person: record it, and expect that a finished
  window will be held about a day (the watchdog releases a finished window only when the courier's delivery
  record exists). Tell Ed so in the exit email in one sentence.
- **Reading 3, the fallback transport for a notice** (Ed's ruling in issue #349: when Gmail is down the arm
  notice goes out as a GitHub issue labelled `directive-notice`). The label did not exist on 2026-10-07.
```zsh
gh label list --repo mpmdw/JouleWise | grep -c '^directive-notice' || gh label create directive-notice --repo mpmdw/JouleWise --description "Arm notice sent as an issue because Gmail was unavailable"
gh issue create --repo mpmdw/JouleWise --label directive-notice --title "Test of the fallback transport for an arm notice (no action needed)" --body "This issue tests whether a notice opened from the measurement Mac reaches the owner as a notification. It can be closed."
```
  **Expected:** an issue URL. Its number goes into the exit email as question E-3. The title and the body
  carry no address and no name.
- **Reading 4, nothing armed, the ledger reservable, the clock, the privileged commands, the build:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; cd "$MEASUREMENT_ROOT" || exit 3
launchctl list | awk '$3 ~ /^com[.]joulewise[.]night/ {print $3}'
PYTHONDONTWRITEBYTECODE=1 "$PY" -B -c 'from pathlib import Path; from joulewise.b5 import plan; s=plan.ledger_head_status(Path(".").resolve()); print(s["blocking"], s["open_sessions"]); assert not s["blocking"]'
PYTHONDONTWRITEBYTECODE=1 "$PY" -B -c 'import json; from joulewise.hazards import clock; f=clock.read_frequency(); print(json.dumps(clock.frequency_bound(f["raw_word"], clock.DEFAULT_THRESHOLDS)))'
/usr/bin/sudo -n -l | grep -c -e 'NOPASSWD: /usr/sbin/systemsetup -setusingnetworktime off' -e 'NOPASSWD: /usr/bin/powermetrics'
test "$(sw_vers -buildVersion)" = 25G83 && echo "build 25G83"
HOMEBREW_NO_AUTO_UPDATE=1 brew list --pinned
git diff --name-only --no-renames "$H_CLAIM" HEAD
```
  **Expected:** nothing from `launchctl`; `[] []`; a record with `"passes": true` (on 2026-10-07 the bound
  was 4.845 ms against a limit of 5.0 ms); `2`; `build 25G83`; `python@3.13`; the three seal documents. If the
  clock record says `false`, do the frequency redraw of registration section 3 (brief section 5.1) before
  the release.
- **Reading 5, the lid and the charger:**
```zsh
ioreg -r -k AppleClamshellState -d 4 | grep '"AppleClamshellState"'
pmset -g batt | tail -1
```
  **Expected:** `"AppleClamshellState" = No` (the lid is open), and a line containing `AC attached; not
  charging`. The Mac's only display is the built-in one, so a closed lid puts it to sleep; and a window is
  refused at its start while the battery is charging or discharging.
- **Reading 6, no stale instruction waits for the magistrate.** At every launch the magistrate reads Ed's
  unread mail and the open issues labelled `directive`, and treats each as an instruction.
```zsh
gh issue list --repo mpmdw/JouleWise --label directive --state open --json number,title --jq '.[] | "\(.number) \(.title[0:70])"'
```
  With the Gmail tool of this session, search for unread mail from the owner's notice address (held in the local file b5-fixed-env.zsh, not in the repository):
  the query is `from:<address> is:unread` with the value of `NOTICE_TO`. **Expected:**
  the search returns nothing (mark the two messages of 2026-10-05 read: they carry the G10 ruling, which is
  applied); the issue list shows only issues the RUN_STATE block says how block 5 discharges. On 2026-10-07
  it showed #405, #408, #416, #417, #421 and #422. None of them is closed: they are Ed's issues (the
  orchestrator's decisions O-8 and of 2026-10-07 23:55), and the RUN_STATE block says for each how block 5
  discharges it.
- **Reading 7, the applications.** Quit Firefox, the ChatGPT app and the Claude app, and everything else in
  the foreground except Finder and Terminal.
```zsh
osascript -e 'tell application "System Events" to get name of every process whose background only is false'
ps -axo pid=,comm= | grep -iE '/(Claude|ChatGPT|T3 Code[^/]*|Google Chrome)\.app/'
pgrep -lx firefox
```
  **Expected:** `Finder, Terminal`; nothing; nothing. On 2026-10-07 between 23:20 and 23:45 PDT Firefox was open and the
  others were not. Quit an application through its own Quit command or with `osascript -e 'quit app
  "Firefox"'`, with Ed's word in the session; an application he still needs (to read the exit email on this
  Mac, for one) is named in the exit email as his to quit. *Why:* opening the Claude app, the ChatGPT app,
  T3 Code or Chrome starts an agent process within seconds, and a window stops when its census sees one; a
  browser is not an agent, but while in use it exceeds the window's limit for a competing process and removes
  the measurements it overlaps.
- **Reading 8, the agent check.**
```zsh
source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; cd "$MEASUREMENT_ROOT" || exit 3
/usr/bin/pgrep -a -lf '[c]odex|[c]laude' | PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$BENCH/b5_agent_check.py"; echo "agent check rc=$?"
```
  The program is `premortem/b5_agent_check.py`, installed in the bench by step 6. It prints three things:
  `own_session_pid`, the orchestrator's own session, which ends when Ed exits it; `foreign_agents`, agent
  processes outside this session (another session, an application's helper); and `own_seats_still_running`,
  seats this session started that are still alive. **Expected at this reading:** `foreign_agents` is empty.
  `own_seats_still_running` may still list the wave's agents; step 13 empties it.
- **Status:** ESTABLISHED for readings 1 and 4 to 8 (each command was run on this machine on 2026-10-07, by
  the pre-mortem or by this runbook's author; the citations are `PREMORTEM.md` findings CE-4, AH-4, WR-3,
  M12, M13, C3, AH-3, C1 and C2). UNKNOWN for reading 2: neither command has been run; the field names of the
  first record are the ones the pre-mortem's magistrate lens read, so if the `python3` line prints `None`,
  print the record and read the three facts from it. UNKNOWN for reading 3: whether an issue opened by Ed's
  own GitHub account notifies him is exactly what question E-3 asks.

## Step 13. Stop every agent

- **Directory:** any.
- **Why now, and why completely.** Deleting the stop ref starts an arm about 35 minutes later whether or not
  the Mac is free of agents: the watchdog launches the magistrate without looking at the census. A window
  refuses to start while any Claude or Codex process is alive; and after such a refusal the watchdog starts
  nothing for as long as that process lives, up to t0 plus the window's programmed span plus 300 seconds,
  which is 28 hours 28 minutes for ALPHA. So the release is the last act of the last agent session on the
  Mac. (`PREMORTEM.md` findings C1, C2, M4.)
- **Command:** stop every workflow, Codex seat, background task and subagent of this session with the tools
  that started them, and wait for each stop to complete. Their state is on pushed branches and in the wave's
  notes directory. Then:
```zsh
source /Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh; cd "$MEASUREMENT_ROOT" || exit 3
pkill -f 'sleep 5400'; echo "orphan sleepers signalled: rc=$? (1 means there were none)"
/usr/bin/pgrep -a -lf '[c]odex|[c]laude' | PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$BENCH/b5_agent_check.py"; echo "agent check rc=$?"
pgrep -fl 'unittest|shard_runner|harvest_b5_window|run_campaign' | head
```
- **Expected:** `agent check rc=0`: `foreign_agents` and `own_seats_still_running` are both empty, and
  `own_session_pid` is this session. The last line prints nothing (no test run or harvest of the wave is
  still working; one left running would be a competing process at the window's start).
- **Status:** ESTABLISHED (`../premortem/POST_SEAL_RUNBOOK.md` step A10 item 1; the `sleep 5400` orphan is
  the one a Codex seat's wrapper leaves, `COMMON.md`).

## Step 14. Email Ed to `/exit`

- **Directory:** none (the Gmail tool of this session).
- **Command:** send `EXIT_EMAIL_DRAFT.md` (in `/Users/edr/night-archive/gate-prune/wave-1007b/handoff/`) with its markers filled, to the address in
  `NOTICE_TO`, as plain text. Fill the latest time for the `/exit` as the present time plus 20 minutes.
  Record the Gmail message id in the hand-off notes.
- **Expected:** Gmail returns a message id.
- **Check:** the email is sent before the ref is deleted, never after: if the send fails, do not delete the
  ref; tell Ed in the session instead, and delete only when he has the text.
- **Status:** ESTABLISHED (Ed, 2026-10-07: "ping me when to /exit this interactive session so you can have a
  quiet machine"; the send from this session worked at 21:25).

## Step 15. Delete the stop ref

- **Directory:** any worktree with the remote; not the canonical root.
- **Command:**
```zsh
source /Users/edr/night-plan-staging/b5-bench/runbook-env.zsh
git ls-remote https://github.com/mpmdw/JouleWise.git 'refs/heads/ops/stop*'
git -C "$W" push origin --delete ops/stop-pause
git ls-remote https://github.com/mpmdw/JouleWise.git 'refs/heads/ops/stop*' | wc -l
test ! -e /Users/edr/night-custody/magistrate/STOP && echo "no local STOP file"
echo "RELEASED: type /exit now"
```
- **Expected:** the first `ls-remote` shows `refs/heads/ops/stop-pause`; after the delete the count is `0`;
  `no local STOP file`; then the line `RELEASED: type /exit now`, which is the line the exit email tells Ed
  to wait for.
- **What happens next, without this session.** Within 300 seconds the watchdog's next run finds no stop and
  starts the magistrate. The magistrate reads the state from the disk, runs the agent check, and writes no
  plan while a Claude or Codex process outside its own session is alive: so if this session is still open it
  costs time, not a window. With the Mac free it writes ALPHA-1's plan with a start time about 30 minutes
  ahead, emails Ed the arm notice, installs the window's two jobs and exits.
- **After this step, do nothing more in this session:** no command, no summary, no further tool call that
  starts a process. End the turn with the line above as the last output. The one exception is an answer Ed
  types in the session before his `/exit`: write it into `owner-answers.txt` with a file edit (step 6; the
  lead of E-4 is asked in minutes and stored in seconds). His YES to question O-11 (the permission sentence
  for headless sessions) is acted on only when he types it himself in this session, never on an email and
  never on an agent's suggestion; without it the settings are not touched.
- **If Ed does not exit.** The magistrate's check holds the arm and emails him after about half an hour
  (brief section 5.1). The older fallback, in which the session ends itself with the hand-off reaper of
  `docs/process/MAGISTRATE_WATCHDOG.md` section "Install handoff", is **UNKNOWN** at this version of the
  command-line program: it was last run on 2026-09-06, and it is not part of this runbook.
- **To pause later:** never by a STOP file and never by creating the ref again. A pause is pushed work and an
  idle machine.
- **Status:** ESTABLISHED (`magistrate_watchdog.py` `STOP_REF_GLOB`, `remote_stop_probe`; the delete is an
  ordinary `git push --delete`; the ref was read on 2026-10-07 between 23:20 and 23:45 PDT as `ops/stop-pause` at
  `e0c738e9c`).

---

## Status of every step

| Step | Status | Where it was established, or what is unknown |
|---|---|---|
| 0 values file, state | ESTABLISHED | read on this machine 2026-10-07 between 23:20 and 23:45 PDT |
| 1 head commit | ESTABLISHED | `SEAL_LANDING.md` section 4 step 1; checks run against `cc0b3446d` |
| 2 seal commit | ESTABLISHED; two checks UNKNOWN | `SEAL_LANDING.md` steps 2 to 4, `proof-landing.log`, `REVIEW.md`; `repin.py --check` and `gen_state.py --check` never run at a seal commit; which marker names the admitted registration keeps |
| 3 measurement clone | ESTABLISHED | block-3 recipe `step1-clone.zsh`; `SEAL_LANDING.md` step 7 |
| 4 relock, Homebrew pin | ESTABLISHED | block-3 recipe; relock records of 08-27 and 09-02; `PREMORTEM.md` CE-1, CE-3 |
| 5 ledger seed | ESTABLISHED | block-3 recipe; `PREMORTEM.md` CE-5 |
| 6 bench, scratch plans | ESTABLISHED; one value UNKNOWN | the repository's plan writer, chain check and installer; helpers tested in scratch; `window_max_s` read at `9395cecfb` |
| 7 desk clone | ESTABLISHED for the clone and probe; UNKNOWN for the merge of H_claim into the lane | decision O-6; pre-mortem step A5b; no ruling on how the lane's head comes to descend from H_claim |
| 8 record commit | ESTABLISHED; UNKNOWN which fixtures the seal forces | `SEAL_LANDING.md` step 5; ruling F8 |
| 9 suite and CI | ESTABLISHED; UNKNOWN whether a file-fed runner removes the artefact failures | `frozen-suite-int5-8/run.sh`; `ci.yml` |
| 10 six-key ledger | ESTABLISHED | `pull_request_template.md`; `check_gate_ledger.py` |
| 11 merge, canonical root | ESTABLISHED | `SEAL_LANDING.md` step 6; relaunch prompt line 10; watchdog `tick --dry-run` |
| 12 readings | ESTABLISHED for 1 and 4 to 8; UNKNOWN for 2 and 3 | run on this machine 2026-10-07; the headless send and the issue notification were never run |
| 13 stop every agent | ESTABLISHED | pre-mortem step A10 item 1; `b5_agent_check.py` tested with stand-ins |
| 14 exit email | ESTABLISHED | Ed's instruction of 2026-10-07; Gmail send from the session at 21:25 |
| 15 delete the stop ref | ESTABLISHED; the reaper fallback UNKNOWN | `STOP_REF_GLOB`, `remote_stop_probe` |
