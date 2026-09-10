# 99 — Operating runbook (DRAFT) for the agent-free calibration derivation nights, lane ACCEPTANCE-EPOCH-25G83-01

STATUS: **DRAFT. Authorizes nothing.** This file is desk text written at the
bench by a writer seat that ran no capture, armed no night, and changed no Git
state. Every command below is prospective. The lane's code was still on seat
branches when this was written and its whole-suite replay at integration head
`51565cee` was **RED** (report
[98-integration-replay-red.md](98-integration-replay-red.md): 227 modules,
5773 tests, failures = 5, errors = 9, all fourteen new and on this lane's
files). **No plan may pin this chain until a fresh sharded replay at the fixed
head is green and the lane's PR is merged.** Sections marked
`[UNVERIFIED: …]` are facts this seat could not establish from the sources it
was given; they are open questions for the operator, not instructions.

**Changelog — revision 3 (2026-09-10, writer seat), one line: revised against
the lane's INTEGRATION head, which moved three things this runbook operates —
the capture chain now DISPATCHES on the writer's exact status (a non-valid
capture no longer ends the night), the issuer now enforces the pre-registration
and the campaign's declared shape at `prepare-candidate`, and the wrapper
generator now PARSES the two desk-produced JSON inputs instead of only hashing
them.** What that forced: §0.3 gains the `check --preregistration` desk step
and the warning that its return code cannot report the result; §0.5 gains the
pinned pre-registration digest that `prepare-candidate` later demands; §1.1a
gains the generator's anchor-text citation discipline; §1.1b step 3 gains the
input validation and the ledger's slot-count ceiling; §1.2's worked example
gains the **Δ** term between `t0` and the chain's actual start, which the
previous example silently idealised to zero (seam finding N-3); §2.1, §2.4 and
§5 carry the three-way dispatch, in which `slot_refused` ends the night with
the session OPEN and the operator's answer is desk recovery, never a retry;
§4.1 and §4.2 carry the issuer's exact flag set and the two written-ruling
escapes; §6 gains clause 11; §7 and §8 are updated. Revision 2 (same day)
closed the §1.1 `[UNVERIFIED]` on how the night driver supplies the chain's
environment — it does not, by design; a generated wrapper carries it. The four
`[UNVERIFIED]` blocks — the live `check` output strings (§0.3), the
identity-epoch / T1-bindings producer (§0.8), the 06:05 last-start cutoff
(§1.3) and the complete night-gate refusal list (§5) — are still true and are
kept verbatim.

Audience: the operator is the **next magistrate activation** — the Claude
session that a relaunch prompt starts, holding the frozen triple and the
project's standing authorities. It is a desk operator: it prepares, notices,
arms, exits, and later harvests. It never observes a capture, because these
nights are agent-free by construction (§0.6).

---

## What these three nights are for, in one paragraph

Every calibration capture is judged against thresholds that live in one JSON
artifact called the **acceptance** — the issued file whose corpus statistics
set the numbers later captures are compared to. An acceptance binds an
**identity epoch**: the six-field vector `{os_build, hardware_model,
power_policy, sampling_interval_ms, estimator_revision, pulse_protocol_id}`
describing the machine and estimator it was derived on. This machine's
`os_build` moved from `25F84` to `25G83`, so the live acceptance
`d079_calibration_acceptance_v2_n17_r6` binds an epoch that no longer exists
and refuses every ordinary capture (D-102 clause 2). A new acceptance needs a
corpus of captures taken on the NEW epoch — but those captures must happen
before any acceptance of their own epoch exists to judge them. The lane's
answer is a **derivation-only capture**: an observation taken expressly to
build a future acceptance, which licenses no measurement of anything. Three
agent-free nights of twelve such captures each produce the corpus. This
runbook operates those three nights.

Source for this paragraph: the pre-registration
`configs/calibration/preregistration_d079_epoch_25g83_rev1.md` on branch
`feat/2026-09-10-epoch-s6-docs-prereg` (read via
`git -C /Users/edr/code/JouleWise-wt-s6-docs-prereg show HEAD:<path>`),
§"Why this registration exists".

## Terms, glossed here because every later section uses them

- **Slot** — one declared, ordered place for one capture inside a session,
  named `d01`…`d12`. Declared before the night runs; a slot the window cannot
  reach is recorded **unused**, never retried and never replaced.
- **Session** — a ledger capability that reserves several attempts under one
  open receipt while the repository-committed head pin stays put. A
  `derivation`-kind session is the only route these captures may take.
- **Registration** — the set of ledger sessions (here: exactly three, one per
  night) that the pre-registration declares this corpus is drawn from. A valid
  same-epoch observation captured OUTSIDE the registration refuses issuance
  rather than being quietly absorbed.
- **Epoch** — the six-field identity vector above.
- **Head pin** — the repository-committed file naming the ledger receipt count
  and last digest that consumers trust. *Head-equals-pin* means the physical
  ledger head matches that file exactly.
- **Screen** — a threshold a capture's value is compared against. Two matter
  here: the **level screen** (an acceptance's corpus maximum, the preflight
  bound a single capture is refused above) and the **bracket screen** (its
  corpus range, the drift below which a measurement window passes without
  spending error budget).
- **Ceiling** — the **budget ceiling**, the largest drift a generation will
  ever budget for. Issuance refuses when the bracket screen is not strictly
  below it.
- **Prior set** — an acceptance's list of every ledger observation through
  its cutoff receipt. **Corpus** — the subset of the prior set whose values
  the statistics are computed from; **retained n** is the corpus size.
- **Blind** — no person and no agent examines any member value, screen, or
  statistic before the third night's session is terminal. This is not a
  convention; the issuer enforces it in code (§2.2, §4.1).
- **Dead-man** — the second LaunchAgent installed alongside the night agent,
  which fires at a fixed local minute and stands the night down if the night's
  completion time has passed without completion.
- **Fence** — a half-open local-time interval in which the watchdog refuses to
  launch or adopt a session: `[02:45:00, 03:30:00)` and `[07:00:00, 07:01:00)`
  (`docs/process/MAGISTRATE_WATCHDOG.md:52`).
- **Handback** — `docs/process/NIGHT_HANDBACK.md`, the file the night courier
  reads first; the magistrate rewrites its three night-specific sections before
  every armed night and commits that rewrite with the night's plan.
- **Email-then-arm** — the standing arming procedure: Ed is emailed the night
  notice, and the arm proceeds without waiting for a reply; **Ed's NO
  overrides** and stands the night down
  (`docs/process/MAGISTRATE_WATCHDOG.md:329`).

A first-use table for every term of art in this file is at §8.

---

## 0. Preconditions and desk checks

Do all of §0 before authoring any plan. Each check is cheap; each failure is a
reason not to arm tonight, never a reason to work around it.

### 0.1 The lane's code is merged at a reviewed head H

`H` is the full 40-character SHA of the commit on `origin/main` that carries
BOTH the merged ACCEPTANCE-EPOCH-25G83-01 lane (seats S1–S6) AND the night's
handback rewrite and production inventory row. There is exactly one H; the
plan's `repo_head`, the plan's `measurement_head`, the handback commit, and
the clone's detached HEAD are all H.

```zsh
set -euo pipefail
: "${BOOKKEEPING_ROOT:?the activation's authorized linked worktree}"
cd "$BOOKKEEPING_ROOT"
test "$PWD" != /Users/edr/code/JouleWise
git fetch origin main
export H="$(git rev-parse origin/main)"
git log --oneline -1 "$H"
```

Do not arm on a head whose replay is not green. The lane's own report 98 is the
standing example of why: five modules failed only under the whole suite, never
under any seat's focused set.

### 0.2 A fresh clone at H is the measurement root

The **measurement root** is a fresh, independent GitHub clone detached at H,
from which BOTH night agents are installed. Its path is recorded in
`configs/production_custody_inventory.json` inside H itself, so the clone name
carries no SHA. Use the fresh-clone recipe rather than fast-forwarding or
renaming any provisional clone; renaming moves venv and editable-install
absolute paths (runbook 68 §"Fresh clone at H").

```zsh
set -euo pipefail
: "${H:?}"
export REMOTE_URL=https://github.com/mpmdw/JouleWise
export MEASUREMENT_ROOT=/Users/edr/JouleWise-measurement-<NIGHT_DATE>-derivation
remote_main="$(git ls-remote --exit-code "$REMOTE_URL" refs/heads/main)"
test "${remote_main%%$'\t'*}" = "$H"
test ! -e "$MEASUREMENT_ROOT" && test ! -L "$MEASUREMENT_ROOT"
git clone --no-hardlinks "$REMOTE_URL" "$MEASUREMENT_ROOT"
git -C "$MEASUREMENT_ROOT" checkout --detach "$H"
```

The production ledger lives in this clone's own
`runs/calibration_observation_ledger.jsonl`, restored byte-exact from the
canonical ledger and then authenticated with `verify_custody=True`. Custody
locators are absolute iCloud paths; copy no custody directories and rewrite no
locator (record 05 / file 11 route).

### 0.3 The epoch watch: `check` must exit 3, and that is the expected result

```zsh
cd "$MEASUREMENT_ROOT"
.venv/bin/python scripts/issue_calibration_acceptance_generation.py check
echo "check rc=$?"
```

`check` is read-only. It authenticates the ACTIVE issued acceptance and the
ledger, then prints a four-row table comparing the epoch that acceptance binds
against the machine observed right now: `os_build` and `hardware_model` read
from `/usr/sbin/sysctl`, `powermetrics_sha256` hashed from `/usr/bin/powermetrics`
(the binary is hashed, never executed), and `mlx_version` from the **T1 bindings** of the ledger's last row — T1
bindings being the toolchain-identity block a finalization receipt records
(among them the MLX version in force at that capture). **With no `--session-ids` argument it returns 3 when any
field mismatches or any error was found, and 0 otherwise**
(`scripts/issue_calibration_acceptance_generation.py:305`).

Gloss, because the sign is inverted from the usual: **rc 3 is the expected,
correct result throughout this lane.** The whole reason the lane exists is that
`os_build` moved to `25G83` while the live acceptance still binds `25F84`. An
rc 0 here would mean the machine's identity now matches the old artifact —
i.e. the OS was rolled back, or the wrong acceptance file was read — and is a
**stop**, not a green light. Record the printed table verbatim; the `os_build`
row must read expected `25F84`, observed `25G83`, status `MISMATCH`.
`[UNVERIFIED: the exact expected/observed strings this machine prints. This
seat ran no live command; the field names and the rc-3 rule are read from
code, the values are not.]`

**Then run `check` a second time with `--preregistration`, and read the line it
appends.** The pre-registration names the `/usr/bin/powermetrics` SHA-256 the
campaign is registered under —
`b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5` — and says
in terms that a change to it voids the registration. The sampler binary is the
instrument: a different binary is a different measuring device, and a corpus
half-captured on each is two corpora. `check --preregistration` is the desk step
that reads that literal out of the registration text and compares it against the
binary hashed on this machine right now:

```zsh
cd "$MEASUREMENT_ROOT"
.venv/bin/python scripts/issue_calibration_acceptance_generation.py check \
  --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md
echo "check --preregistration rc=$?"
```

Without the flag the watch output is byte-identical to the table above; with it,
exactly one line is APPENDED after the table, and nothing else changes:

```
pre-registered powermetrics sha256 b762e5bf…30c5: match
```

or, when they differ, `…: MISMATCH — the registration is void`.

**The return code cannot tell you which.** `check` returns 3 when any watched
field mismatches OR any error was recorded, and the `os_build` mismatch of §0.3
already forces 3 for this entire lane; a sampler mismatch only adds one more
error to a code that was 3 already. So the expected result here is still rc 3,
and rc 3 is not the check — the printed line is. Record that line verbatim in
the arm materials for every night. `MISMATCH` is a stop that voids the
registration: no night may be armed under it, and a mismatch discovered after
captures exist is a matter for Ed's written ruling, not a re-arm.

### 0.4 Ledger authenticated and head-equals-pin

The same `check` invocation loads the ledger snapshot with
`require_committed_pin=True, verify_custody=True, mode="read_replay"`. Any
refusal reason is printed on the `ledger: …` line. A `ledger:` line is a stop:
the night's first machine action opens a session at head-equals-pin, and a
ledger that will not authenticate at the desk will not authenticate at 03:00
either. Record the head pin's sequence and digest now — the pre-registration's
`[SEQ]` and `[DIGEST]` fields are filled from the pin in force at the FIRST
night's open, and are then frozen for all three nights.

### 0.5 Pre-registration committed, with its bracket fields filled

`configs/calibration/preregistration_d079_epoch_25g83_rev1.md` must be
committed inside H with `[DD]`, `[MLX_VERSION]`, `[SEQ]`, `[DIGEST]` and
`[CHAIN_SHA256]` filled. Those five are facts that did not exist when the text
was written; filling them reopens no scientific rule. The plan's
`registration_path` points at this file (`joulewise/night_gate.py:38`).

`[CHAIN_SHA256]` takes the **tracked chain's** SHA-256 — one value shared by all
three nights — and NOT any night's wrapper digest. The registration reserves a
single blank for it, and three nights produce three different wrappers (three
plans, three session IDs, three `t0`s), so only the tracked chain's digest can
fill it. That digest is also the literal each night's wrapper compares against
before it `exec`s (§1.1a step 4), which is what makes the registered value and
the value in force at capture the same number.

**Pin the pre-registration's own digest into the arm materials.** Once the file
is committed inside H with those five fields filled, hash the committed bytes
in the measurement clone and carry the value in every night's arm record:

```zsh
shasum -a 256 "$MEASUREMENT_ROOT/configs/calibration/preregistration_d079_epoch_25g83_rev1.md"
```

The clean-tree check of §0.8 is what makes this the committed bytes rather than
a working-copy edit. The digest is not decoration: `prepare-candidate` takes it
as the required `--preregistration-sha256` and refuses —
`pre-registration sha256 <observed> does not match the pinned <given>; not
issued` — if the file's bytes moved between the arm and issuance (§4.2). A
pre-registration exists to fix the rules BEFORE the data; this pin is what makes
"before" checkable by someone reading the artifacts months later, because
without it the tool would derive against whatever the file says on the day it
runs, which is exactly the edit the document exists to forbid. Record it once,
at night 1's arm, and re-record the same value at nights 2 and 3 — a change
between nights is a stop, not a new pin.

**V3 requires Ed's affirmative written acknowledgment before the first
capture's arm — silence is not consent for V3.** V3 is the night count, the
slots per night, and the retained-corpus minimum: three nights × 12 slots,
retained n ≥ 19. Every other rule in the registration is a proposed default
adopted by cold gate 46 under an open Ed veto. Do not arm night 1 without that
acknowledgment recorded.

### 0.6 Census clean, and the night is agent-free

`[QUIET-MAC]` nights are agent-free. The magistrate exits before `t0 − 25
minutes`; that boundary is the closed start of the plan span, and the resident
supervisor's cooperative ladder enforces it: `standdown.request` at
`t0 − 25 min`, TERM no later than `t0 − 16 min`, KILL no later than
`t0 − 15 min` (`docs/process/MAGISTRATE_WATCHDOG.md:56,60`).

Before the arm census, stop all own seats, delegated tasks and background jobs
using the activation's real task controls; record the task IDs and results and
invent none. Then inspect and classify by ancestry:

```zsh
ps -axo pid,ppid,command | grep -E 'claude (daemon run|bg-spare|bg-pty-host)|--resume'
```

A no-match `grep` exit 1 is the expected outcome, not a failure to be
suppressed. "Own" means this activation and its attached descendants: prior
activations, interactive sessions, foreign seats, daemons, spares, resumed
twins and PID-1 orphans are **not** own. Foreign or unclassifiable processes
abort the arm; do not signal them. Never run the chain, the driver, a full
preflight or a calibration capture from the live activation as a quietness
test.

### 0.7 Nothing else is armed or discoverable

No stand-down, no Ed NO, no unresolved owner-authored `directive` issue, no
discoverable prior plan root, no active or indeterminate measurement ownership.
Remove every `REHEARSAL_STUB` plan root before arming any real plan
(`docs/process/MAGISTRATE_WATCHDOG.md:329`).

### 0.8 The clone's tree is clean, and the two desk-produced JSON inputs exist

**Clean tree** means: the measurement clone has no uncommitted change of any
kind — no modification, no staged file, no untracked file. Check it and record
the output verbatim in the night's arm materials:

```zsh
git -C "$MEASUREMENT_ROOT" status --porcelain
```

The expected output is **nothing at all**, zero bytes. Any line is a stop:
stand the night down and re-cut the clone (§0.2).

Why this is a precondition and not a nicety: the night gate binds the clone by
its committed `HEAD` only — it checks `git rev-parse HEAD` equals the plan's
`measurement_head` and nothing more (`joulewise/night_gate.py:1006–1029`, read
by the S7 contract refuter, report 105 §5.2). Nothing anywhere excludes
uncommitted edits. The wrapper of §1.1a closes this for exactly one file, the
capturing chain, by comparing its bytes against a digest baked in at arm time;
`recover_calibration_ledger.py`, `reserve_calibration_window_bracket.py` and
`validate_powermetrics_fiducial.py` — the three programs that actually open the
session, reserve the slots and write the captures — remain bound by `HEAD`
alone. So an edited working copy of any of them would run all night with no
signal. **This check is procedure, not code**: no tool enforces it, which is
precisely why it is written here and recorded in the arm record.

The night root `<NIGHT_ROOT>` must also hold two desk-produced JSON files
before the wrapper can be generated: `identity_epoch.json` (the six-field
identity vector) and `t1_bindings.json` (the T1 bindings block). The
reservation copies the CONTENTS of both verbatim into every slot record
(`scripts/reserve_calibration_window_bracket.py:216–220`, report 105 §2), so
their bytes are part of what every capture is bound to, and the generator pins
each one's SHA-256 into the wrapper as a literal.

`[UNVERIFIED: which tool produces <NIGHT_ROOT>/identity_epoch.json and
<NIGHT_ROOT>/t1_bindings.json for a DERIVATION night, and where their custody
copy lives. The exact question to answer before the first arm: is the producer
`scripts/generate_g2a_probe_inputs.py bind-window` — the G2-a analogue, which
records `{"identity_epoch": {"path", "sha256"}, "t1_bindings": {"path",
"sha256"}}` and replays them under its own `check` (report 105 §5.1) — or the
new epoch issuer `scripts/issue_calibration_acceptance_generation.py`, or a
third desk tool? Seat S7 left this open deliberately and made both files
explicit required inputs rather than inventing a producer (report 103 §7.1).
Once the producer is named: run it IN the measurement clone at arm time,
record both paths AND both SHA-256 digests in the arm record, and re-derive
both if `os_build`, `powermetrics_sha256`, `mlx_version`, `estimator_revision`
or `protocol_sha256` moved since the previous night — the writer compares its
measured bindings against the reserved slot's, so a drift between arm and t0
refuses at slot `d01` and costs the whole night.]`

---

## 1. Night 1 arm

### 1.1 The plan is `joulewise.night_plan.v2`, class `DIAGNOSTIC_NO_PACK`

`DIAGNOSTIC_NO_PACK` is the receipt class for a night that runs no measurement
pack: it requires a registration path and marks only the pack-ARM condition
(C2) not-applicable. The transaction-authorization, quiet-census, boot/clock
and no-retry conditions all still have to pass.

The v2 plan's required keys are exactly (`joulewise/night_gate.py:112–127`):

| Key | Value for night 1 |
|---|---|
| `schema` | `joulewise.night_plan.v2` |
| `schema_version` | integer `2` |
| `plan_id` | `<PLAN_ID>` — e.g. `d079-epoch-25g83-derivation-n1-<YYYYMMDD>` |
| `receipt_class` | `DIAGNOSTIC_NO_PACK` |
| `t0_epoch_s` | `<t0>` (integer Unix seconds) |
| `window_max_s` | `9000` (derived in §1.2) |
| `authored_epoch_s` | authoring time; must be within 36 h of both now and `t0` |
| `repo_head` | `<H>` |
| `measurement_root` | `<CLONE>` — the §0.2 clone path, absolute |
| `measurement_head` | `<H>` — equal to `repo_head` |
| `chain_path` | `<NIGHT_ROOT>/chain.zsh` — the **emitted wrapper** of §1.1a, NOT the tracked chain |
| `chain_sha256_path` | `<NIGHT_ROOT>/chain.zsh.sha256` — exactly `chain_path` plus `.sha256`; the generator refuses any other value |
| `custody_root` | `<NIGHT_ROOT>` — e.g. `/Users/edr/night-custody/<PLAN_ID>` |
| `registration_path` | the committed pre-registration of §0.5 |

The plan carries no pack block: `_PACK_NIGHT_KEYS` belongs to pack nights, and
this night has no pack.

### 1.1a The wrapper: what `chain_path` actually points at, and why

**The forcing problem.** The night driver launches the file the plan names in
`chain_path` with a fixed, four-variable environment and NO command-line
arguments: it sets `NIGHT_PLAN_ID`, `MEASUREMENT_ROOT`, `MEASUREMENT_HEAD` and
`PY` from the plan, and runs `/bin/zsh <chain_path>` with nothing after it
(`scripts/run_night.py:430–444`, pinned by `tests/test_run_night.py:348–380`,
which asserts the argv is exactly `["/bin/zsh", <chain_path>]`; scout report 101
§0). The tracked derivation chain
`scripts/night_chains/calibration_derivation_only.zsh` needs far more than
that: **thirteen** further environment variables, each behind a
`: "${NAME:?required}"` guard, and **twenty-four** command-line arguments — one
`--slot-attempt-id` and one `--slot-custody-locator` per slot — which it
forwards verbatim to the session reservation as `"$@"`. There is no production
code that bridges the gap, and there never was: G2-a does not need one, because
its chain carries its own environment inside its own bytes (scout 101 §2).

So a plan whose `chain_path` named the tracked chain directly would launch a
chain with ten of its thirteen variables unset. It would exit 1 on the first
`:?required` guard before spending any window time — safe, but a burned night
out of the three the corpus has.

**The mechanism.** A night is armed by pinning a **wrapper**: a generated zsh
file, one per night, written into the night root (the custody directory the
plan calls `custody_root`), which carries that night's whole environment as
literal `export` lines and then hands control to the tracked chain. The
generator is `scripts/gen_derivation_night.py`. In order, the wrapper:

1. **Refuses any night but its own.** It checks that `MEASUREMENT_ROOT` is
   present, absolute and free of control characters, that `MEASUREMENT_HEAD` is
   a 40-character lowercase hex SHA-1, and then that each of `NIGHT_PLAN_ID`,
   `MEASUREMENT_ROOT` and `MEASUREMENT_HEAD` equals the literal frozen into
   these bytes at arm time. It then reads the clone's actual
   `git rev-parse --verify HEAD` and requires it to equal `MEASUREMENT_HEAD`,
   and requires `<MEASUREMENT_ROOT>/.venv/bin/python` to exist and be
   executable.
2. **Exports the thirteen chain variables as literals** — `SESSION_ID`,
   `WINDOW_ID`, `PLAN_ID`, `PLAN_SHA256`, `PLAN`, `EVIDENCE_ROOT_ID`,
   `RUNS_ROOT`, `WINDOW_CUSTODY_ROOT`, `CALIBRATION_LEDGER`, `LEDGER_HEAD_PIN`,
   `IDENTITY_EPOCH_JSON`, `T1_BINDINGS_JSON`, `WINDOW_END_EPOCH_S` — plus six
   more the chain would otherwise default from whatever shell armed the night:
   `SLOT_COUNT`, `SETTLE_S`, `SLOT_CADENCE_S`, `SLOT_CAPTURE_BUDGET_S`, `SLEEP`
   and `DATE`. The last six are pinned because the driver hands the child
   `os.environ.copy()`, so an inherited `SETTLE_S` from the arming operator's
   shell would silently retime the night. `WINDOW_END_EPOCH_S` is
   `int(t0_epoch_s + window_max_s)` — the same derivation §1.2 does by hand.
3. **Authenticates the three desk-produced inputs before any window time is
   spent.** For the frozen calibration plan `PLAN`: it must exist, parse as
   JSON, carry a `plan_id` equal to the `PLAN_ID` literal, and hash to the
   `PLAN_SHA256` literal. For `IDENTITY_EPOCH_JSON` and `T1_BINDINGS_JSON`:
   each must exist and hash to its own baked-in SHA-256 literal.
4. **Verifies the tracked chain's bytes** — `shasum -a 256` of
   `<CLONE>/scripts/night_chains/calibration_derivation_only.zsh` must equal a
   SHA-256 literal inside the wrapper. This is the link that makes the
   attestation transitive: the plan pins the wrapper's digest, the wrapper's
   own bytes contain the chain's digest, so the plan-pinned digest moves
   whenever the capturing bytes move.
5. **`exec`s the tracked chain** with the twenty-four per-slot bindings as
   argv: `--slot-attempt-id '<SESSION_ID>-dNN'` and
   `--slot-custody-locator '<RUNS_ROOT>/instrument_validation/<SESSION_ID>-dNN'`
   for `dNN` = `d01`…`d12`. `exec`, never `source`: the chain derives its
   repository root from its own `$0` with the line `cd "${0:A:h:h:h}"`, so it
   must run as `$0` at its in-clone path.

Every refusal above prints `FAIL <reason>` to stderr and exits 1. That stream
is the driver's `<NIGHT_ROOT>/night/chain.stderr.log`, and on an agent-free
night it is the only forensic record a 3 a.m. refusal leaves.

**The three emitted files.** One generator run writes exactly three files into
the night root. A **sidecar** here means a small companion file holding another
file's SHA-256 in `shasum` output form — the digest, two spaces, a name:

| File | Role |
|---|---|
| `<NIGHT_ROOT>/chain.zsh` | The wrapper. The plan's `chain_path` must be this exact path. |
| `<NIGHT_ROOT>/chain.zsh.sha256` | The wrapper's sidecar. The plan's `chain_sha256_path` must be this exact path; the driver refuses the night unless the wrapper's bytes still hash to it. |
| `<NIGHT_ROOT>/chain.zsh.chain-source.sha256` | **Advisory only** — the tracked chain's digest, named by its repository-relative path so an operator can run `shasum -a 256 -c` on it by hand from the clone. **Advisory** means nothing reads it at launch: the wrapper carries the same digest as a literal in its own bytes, so deleting or rewriting this file changes nothing about what the night will accept. |

**How the generator cites the chain, and why the operator should care.** Every
reference `gen_derivation_night.py` makes into the tracked chain is an **anchor
text** — one exact line of the chain, quoted in full and held in the
generator's `CHAIN_ANCHORS` table — and never a line number. Examples of the
anchors it holds: `cd "${0:A:h:h:h}"`, `SETTLE_S="${SETTLE_S:-600}"`,
`SLOT_CAPTURE_BUDGET_S="${SLOT_CAPTURE_BUDGET_S:-480}"`, and
`    if (( writer_rc == 0 )); then`. `tests/test_gen_derivation_night.py`
resolves every anchor against the chain's current bytes, so a chain edit that
moves or rewrites a cited line fails a test rather than shipping a false
citation into a night's artifact. Two of those anchors are the chain's
**writer-status dispatch** — its branch on the exact status number a capture
returns, built in full at §2.4 — because the wrapper's window arithmetic
assumes every declared slot is attempted. "A non-valid capture does not stop
the night" is therefore part of the contract the generator depends on, and is
pinned as such rather than left to a reader's assumption. When this runbook and
the code disagree, grep the quoted line: it is the citation that is guaranteed
to still exist.

### 1.1b Arm order: five steps, each depending on the one before

1. **Cut the clone at H** (§0.2) and record `git -C "$MEASUREMENT_ROOT" status
   --porcelain`; it must be empty (§0.8).
2. **Author the night plan** (§1.1 table), with `chain_path` =
   `<NIGHT_ROOT>/chain.zsh` and `chain_sha256_path` = that path plus `.sha256`.
   The plan must exist FIRST: the generator reads `t0_epoch_s`,
   `window_max_s`, `custody_root`, `measurement_root`, `measurement_head`,
   `receipt_class`, `chain_path` and `chain_sha256_path` out of it, and refuses
   if `chain_path` is anything else.
3. **Generate the wrapper**, run from the measurement clone. Six flags are
   required and there are no others to supply for an ordinary twelve-slot
   night:

   ```zsh
   cd "$MEASUREMENT_ROOT"
   "$PY" -B scripts/gen_derivation_night.py \
     --plan "$NIGHT_ROOT/night_plan.json" \
     --session-id "$SESSION_ID" \
     --evidence-root-id "$EVIDENCE_ROOT_ID" \
     --calibration-plan "$NIGHT_ROOT/calibration_plan.json" \
     --identity-epoch-json "$NIGHT_ROOT/identity_epoch.json" \
     --t1-bindings-json "$NIGHT_ROOT/t1_bindings.json"
   ```

   On success it prints `emitted <NIGHT_ROOT>/chain.zsh sha256=<64 hex>` and
   exits 0. Notes on the flags, because getting them wrong is a refusal:
   `--out` defaults to the plan's `chain_path` AND is refused if it is anything
   else, so do not pass it. `--window-id` defaults to the plan's `plan_id`;
   `--runs-root` to `<custody_root>/runs`; `--ledger` to
   `<measurement_root>/runs/calibration_observation_ledger.jsonl`; `--head-pin`
   to `<measurement_root>/configs/calibration/calibration_ledger_head.json` —
   pass any of these four only to override a default, and re-record the value
   if you do. `--slot-count` defaults to 12. There is **no `--repo-root`
   flag**: the generator digests the tracked chain from the clone the night
   will run, i.e. from `plan.measurement_root`, never from the checkout the
   generator happens to execute in. `--evidence-root-id` has no derivable
   default; state its literal value and the record that registers it in the arm
   record alongside `--session-id`.

   **The generator PARSES the two desk-produced JSON inputs; it does not only
   hash them.** Hashing pins WHICH file the night will use. Parsing is what
   tells the operator, at the desk and before any window exists, that the file
   can do its job at all. `identity_epoch.json` must be a JSON object whose keys
   are EXACTLY the six `IDENTITY_EPOCH_FIELDS`, with every value present and
   scalar — a non-empty string, or a number, because `sampling_interval_ms` is
   an integer in every issued acceptance — and whose `power_policy` is exactly
   `ac_high_power`. The three refusals name what is wrong: `identity epoch json
   keys are not exactly the six IDENTITY_EPOCH_FIELDS (missing=[…],
   extra=[…])`, `identity epoch json fields are empty or not scalar: […]`, and
   `identity epoch power_policy is '<x>', but the chain captures with
   --power-policy ac_high_power; the writer would refuse at d01 with the settle
   already spent`. `t1_bindings.json` must parse as a JSON object, and nothing
   more is asserted about its fields, because the ledger — not this tool — owns
   that block's shape.

   That last message states the forcing problem for all three. The chain
   hardcodes `--power-policy ac_high_power` on every capture, and the writer
   compares its measured bindings against the reserved slot's identity epoch,
   whose contents are copied verbatim from this very file. So an epoch naming a
   different policy used to fail at `d01`: after the driver's gate work, after
   the reservation, after 600 s of settle, with the session already open and
   eleven further slots that would fail the same way. The same JSON handed to
   the generator at the desk now costs a re-written file and no window time.
   **Learn it at the desk, not at d01** is the whole of the design.

   **The ledger's ceiling on declared slots.** A `--slot-count` above
   `MAX_DECLARED_SESSION_SLOTS` (99, `joulewise/calibration_ledger.py:76`) is
   refused here — `slot count <n> exceeds the ledger's
   MAX_DECLARED_SESSION_SLOTS (99); the reservation would refuse it after the
   settle` — for the same reason: the reservation would otherwise refuse it
   INSIDE the window, after the settle, with the night spent. Twelve is the only
   value these nights use; the ceiling matters solely as the reason a large
   number fails at the desk instead of at 03:10.
4. **Re-derive and assert byte equality** — the arm-time **tripwire**, meaning
   a check that writes nothing and whose only job is to fail loudly if an input
   drifted between generation and arming. Same command as step 3 plus
   `--verify`:

   ```zsh
   "$PY" -B scripts/gen_derivation_night.py --plan "$NIGHT_ROOT/night_plan.json" \
     --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID" \
     --calibration-plan "$NIGHT_ROOT/calibration_plan.json" \
     --identity-epoch-json "$NIGHT_ROOT/identity_epoch.json" \
     --t1-bindings-json "$NIGHT_ROOT/t1_bindings.json" \
     --verify
   ```

   It renders the wrapper again from the same inputs and compares both the
   wrapper and its sidecar byte-for-byte with the installed files. **rc 0**
   prints `VERIFIED <path> sha256=<64 hex>`. **rc 3** prints `FAIL wrapper
   bytes differ from re-derivation: re-derived sha256=… installed sha256=… at
   <path>`, with `<absent>` in place of the installed digest if the file is
   missing. Emission is deterministic, so a difference means an input drifted —
   the tracked chain, the frozen calibration plan, the identity-epoch or
   T1-bindings bytes, or the plan's own coordinates. Do not re-emit over the
   difference; find it.
5. **Syntax-check the wrapper, then install the plan.**

   ```zsh
   /bin/zsh -n "$NIGHT_ROOT/chain.zsh"
   ```

   `zsh -n` parses the file and runs none of it; rc 0 is the only acceptable
   result. Then install the plan (§1.4). From here the plan pins the wrapper's
   digest and the wrapper pins the chain's, so the plan's attestation reaches
   the bytes that actually capture.

One wrapper per night: three nights means three plans, three session IDs and
three wrappers, and the generator refuses to reuse one wrapper across plans.

### 1.2 WINDOW_MAX_S, with the arithmetic

The chain's programmed schedule uses its own defaults, read from
`scripts/night_chains/calibration_derivation_only.zsh`:
`SLOT_COUNT=12`, `SETTLE_S=600`, `SLOT_CADENCE_S=600`, `SLOT_CAPTURE_BUDGET_S=480`.

The night's shape is: one settle, then twelve captures at a **start-to-start**
cadence — meaning slot `d(k+1)` starts 600 s after slot `dk` STARTED, not after
it finished, and a long capture is never caught up by compressing a later slot.
So the programmed span from chain start to the end of the last capture's budget
is:

```
  settle                               600 s
+ 11 cadence gaps (d01 → d12)   11 × 600 = 6600 s
+ the last capture's budget            480 s
------------------------------------------------
  programmed span                     7680 s  = 2 h 08 min
```

7680 s is the same 128 minutes the pre-registration states for a 12-slot night,
which is the cross-check that this arithmetic matches the registered design.

Margin on top of the programmed span covers three things the 7680 s does not:
the chain's pre-settle work (input preflight, the `--phase pre-reserve`
readiness check, and the session reservation, all of which run BEFORE the
settle so that an unusable declaration costs no window time), per-capture
overrun beyond 600 s pushing later slots later, and the driver's own work
before it starts the chain. Allocate **1320 s (22 min)**:

```
WINDOW_MAX_S = 7680 + 1320 = 9000 s   (2 h 30 min)
```

This is an operational allocation, not a measured completion guarantee. Do not
shorten the settle, the cadence, the slot count or the capture budget to fit a
window; shorten nothing and move `t0` earlier instead.

**The generator's floor under this allocation.** `gen_derivation_night.py`
refuses to emit a wrapper at all unless the window can hold the programmed
span plus a **pre-settle allowance** of 300 s. The pre-settle allowance is the
first of the three margin items above, isolated and made mandatory: the time
spent INSIDE the window but BEFORE the settle begins — the chain's input
preflight, its `--phase pre-reserve` readiness check and the session
reservation, plus the driver's own gate work before it starts the chain at all.
The refusal is arithmetic, and its message states both numbers:

```
required window = programmed span + pre-settle allowance
                = 7680 + 300
                = 7980 s          ← the generator's hard floor for 12 slots
```

`window_max_s 3600 < required 7680 + 300 = 7980 s: … lengthen the window rather
than shortening the schedule` is what a too-short window prints. **7980 is a
floor, not a recommendation: 9000 s remains the value to author**, because 7980
leaves nothing for the second margin item — per-capture overrun beyond 600 s,
which pushes every later slot later and is the realistic way a night loses its
last slot to `window_exhausted`. A `--allow-slot-count` departure recomputes
this floor from the new slot count rather than bypassing it.

Those are the registration's three durations, and it states all three together
precisely because confusing them is how a night opens a session it cannot
finish: **programmed span 7680 s (128 min)**, **generator minimum 7980 s
(133 min)**, **armed `window_max_s` 9000 s (150 min)**. A fourth number,
210 min, belongs to none of them — it is the install span 03:00–06:30 of §1.3,
an operator-facing block of the clock, and a 150 min window sits inside it with
an hour to spare. The two measure different things and neither is derived from
the other.

**The dead-man check.** The rule is `t0 + window_max_s + 300 < the next 07:00`,
where 300 s is the **courier allowance** and 07:00 is the dead-man minute. Two
different 300 s budgets appear in this section; they are unrelated and happen
to share a number. The pre-settle allowance above is spent INSIDE the window,
before the settle. The courier allowance is spent AFTER the window ends: it is
the time the driver reserves for the courier to send the night's result before
the dead-man fires. Neither is a substitute for the other, and widening the
window consumes dead-man slack while widening nothing else. Worked
with real numbers, using the coordinates the prior night's runbook 68 pinned
purely as an arithmetic example (`t0 = 2026-09-12 02:56:00 PDT`, epoch
`1789206960`; that morning's 07:00 is epoch `1789221600`):

```
t0                    = 1789206960   (02:56:00 PDT)
t0 + 9000             = 1789215960   (05:26:00 PDT)   ← acquisition allocation ends
t0 + 9000 + 300       = 1789216260   (05:31:00 PDT)   ← courier deadline
next 07:00            = 1789221600   (07:00:00 PDT)
1789216260 < 1789221600                               ✓ PASS, 89 minutes of slack

strict maximum window_max_s for this t0
  = 1789221600 - 1789206960 - 301 = 14339 s
9000 ≤ 14339                                          ✓
```

(The `-301` is `-300` for the courier and `-1` because the comparison is
strict. All four epoch↔local conversions above were verified with
`TZ=America/Los_Angeles date -r <epoch>` in this drafting session.)

The chain's own end boundary follows: `WINDOW_END_EPOCH_S = t0 + WINDOW_MAX_S`
= `1789215960` in the example. Check that the last slot is admitted rather than
skipped — the chain refuses to START a slot whose 480 s budget would cross that
end.

**The schedule does not begin at `t0`, so name the gap before doing the
arithmetic.** Call it **Δ**: the elapsed time between the plan's `t0` and the
moment the chain's settle actually begins. Three things happen inside Δ, in
this order, and none is instantaneous:

1. **The driver's gate work.** The night gate evaluates its conditions,
   authenticates the plan and the registration, verifies the wrapper's bytes
   against its sidecar, and only then launches the wrapper.
2. **The chain preflight.** The wrapper's own checks (one `git rev-parse`, the
   three input digests, one `shasum` of the tracked chain — all sub-second on
   this hardware), then the chain's input preflight and its `--phase
   pre-reserve` readiness check.
3. **The session reservation.** The ledger call that opens the
   `derivation`-kind session and declares all twelve slots. The chain logs
   `chain_start` only after this returns; the settle begins immediately after.

Items 2 and 3 plus the driver's launch are exactly what the generator's 300 s
pre-settle allowance is a floor for; item 1 is the driver's own work. Every
time in the programmed schedule is therefore `t0 + Δ + <programmed offset>`:

```
d01 start      = t0 + Δ + 600
d12 start      = t0 + Δ + 600 + 11 × 600 = t0 + Δ + 7200
d12 budget end = t0 + Δ + 7680
```

and the admission test the chain actually runs — it refuses the slot when
`slot_start + 480 > WINDOW_END_EPOCH_S` — collapses to one inequality in Δ:

```
t0 + Δ + 7680  ≤  t0 + 9000
          Δ    ≤  1320 s   (22 min)
```

**That is what the 1320 s allocated above buys: 22 minutes of Δ before `d12` is
dropped.** The generator's mandatory 300 s covers only the part of Δ it can
reason about; the remaining 1020 s is the operator's headroom, and the second
margin item eats it from the other end — a capture that overruns 600 s pushes
every later slot later, which is arithmetically the same as a larger Δ.

Worked at Δ = 0 — the idealisation, labelled as one — and then at the largest Δ
that still admits `d12`, using the same example coordinates:

```
Δ = 0 s      d12 start      = t0 + 7200 = 1789214160  (04:56:00 PDT)
             d12 budget end = t0 + 7680 = 1789214640  (05:04:00 PDT)
             05:04:00 ≤ window end 05:26:00        ✓ admitted, 22 min unused

Δ = 1320 s   d12 budget end = t0 + 9000 = 1789215960  (05:26:00 PDT)
             05:26:00 ≤ window end 05:26:00        ✓ admitted, nothing left

Δ = 1321 s   d12 budget end = t0 + 9001 = 1789215961  (05:26:01 PDT)
             05:26:01 >  window end 05:26:00        ✗ d12 recorded unused
```

Δ cannot be measured at the desk — it is whatever the machine takes that night —
so the operator's rule is the one those three lines state: a night whose chain
starts more than 22 minutes after `t0` loses `d12`, and
`slot_unused slot=d12 reason=window_exhausted` in the chain log is the evidence
that it did. The realized Δ of a finished night is readable at the harvest: the
`chain_start` line's timestamp in `derivation-chain.log` minus `t0` (§2.1).

If your chosen `<t0>` fails either check, move `<t0>` earlier. Never raise
`window_max_s` past the strict maximum and never move the dead-man.

### 1.3 Install span and the exit boundary

Install BOTH agents on the calendar day BEFORE `t0`, between **03:00 and 06:30
local**. Never install in the 07:xx hour. The first 07:00 dead-man firing after
installation should stand down, because the night's completion time has not yet
arrived; that stand-down line in `night.log` is expected evidence, not a fault.

The activation's absolute exit boundary is `t0 − 25 minutes` (§0.6). Finish
recording and exit before it. Do not remain resident until `t0`.

`[UNVERIFIED: whether a 06:05 "Block B last start" cutoff should carry over to
these nights. Runbook 68 §"Pins and preconditions" marks its own 06:05 rule
PROPOSED for that runbook and notes runbook 67 contains no such rule. Treat it
as the recommended operational cutoff, not a ratified gate: if the email-and-
install block cannot begin by 06:05, do not arm — author the next night's
notice instead.]`

### 1.4 Email, then arm

Order is fixed: **after H is committed and pushed, after any prior stub or plan
root is retired, and BEFORE the plan is moved into its discoverable place.**
There is no minimum notice interval beyond that ordering.

Send Ed the night notice with the activation's mail tool, under its standing
email authority, containing: plan ID; class `DIAGNOSTIC_NO_PACK`; the full H
twice; the handback commit (= H); measurement root, night custody root and runs
root; `t0` local and UTC; `window_max_s` = 9000; the emitted wrapper's digest
and its sidecar path (§1.1a), and the tracked chain's digest the wrapper pins;
the courier deadline; the exit boundary; the planned install span; and the
cancellation instruction — **launch needs no action from Ed unless he replies
NO**. Record the actual send acceptance, time, message and thread IDs, and
which NO relay is available. A headless activation that cannot read the thread
must say so; it cannot certify that no reply went unseen. Recheck owner-authored
open `directive` issues immediately before publication.

Then, in one foreground block: reassert the pins, run the final raw census,
atomically move the staged plan into `<NIGHT_ROOT>/night_plan.json` with
`os.replace` (same filesystem device, target must not pre-exist and must not be
a symlink), install both agents FROM `<CLONE>`, and inspect the installed state
— both `launchctl` labels present, both calendars, WorkingDirectory, exact
driver/plan/courier argv, `RunAtLoad=false` — and record the post-install
`night/` inventory as the baseline the morning harvest is compared against.
Runbook 68 §"Block B" is the executable template; its plan-assertion block is
the one to adapt, replacing its `t0`/`window_max_s`/pack assertions with this
night's and adding `assert p.registration_path` is the committed
pre-registration. If any step after publication fails, uninstall, copy the
published plan aside, compare it byte-for-byte with the staged copy, remove it,
and record the failure. If recovery itself fails, record the surviving labels
and the discoverable plan and escalate; never claim nothing was armed.

### 1.5 Record and exit

Write the arm record and its evidence directory in the authorized linked
bookkeeping worktree, commit, push, and exit before `t0 − 25 min`. Carry the
**frozen triple** — the three values `(<PLAN_ID>, <CLONE>, <H>)` that the next
relaunch prompt must repeat verbatim so the successor activation harvests the
night this one armed — into that prompt until the night completes. No own background work may remain alive.

---

## 2. Morning harvest

The next activation harvests only after the plan span's closed completion
boundary has passed, the courier marker exists, and recorded process ownership
is clear. An early chain exit alone does not authorize early resumption, and
`courier.sent` alone clears neither chain nor campaign ownership.

### 2.1 What to read

| Artifact | What it establishes |
|---|---|
| `<NIGHT_ROOT>/night.log` | The driver's own log: the prior morning's dead-man stand-down line, then this night's gate verdict line. |
| `<NIGHT_ROOT>/night/result.json` | The verdict, the chain's exit code, and where the receipt or refusal is. Read this first; it directs the rest. |
| `<NIGHT_ROOT>/night/receipt.json` or `refusal.json` | The C1–C5 condition rows, or the refusal reason and detail. C2 is `NOT_APPLICABLE`/`no_pack_by_design` for this class. |
| `<WINDOW_CUSTODY_ROOT>/operator_logs/derivation-chain.log` | The chain's own lifecycle: `session_open kind=derivation slots=12`, `chain_start` (its timestamp minus `t0` is the night's realized Δ, §1.2), `settle_complete`, then twelve `slot_start` lines each answered by exactly one of `slot_end … disposition=valid`, `slot_end … disposition=non-valid` (a normal record, §2.4) or `slot_refused slot=dNN rc=<n>` (the night stopped here, session OPEN), and finally `derivation_night_complete slots=12` — or `slot_unused … reason=window_exhausted` followed by `session_abort`. |
| `<NIGHT_ROOT>/night/chain.started`, `chain.exited`, `censuses.jsonl`, `chain.stdout.log`, `chain.stderr.log` | Launchd lineage, actual chain termination, and the production census the driver takes at launch and every 30 s. |
| `<NIGHT_ROOT>/night/courier.sent`, `courier.json`, `courier.heartbeat` | Send time and message ID; verify the email separately in Ed's inbox. |
| launchd `.out`/`.err` for both labels | Present or absent, complete bytes, sizes, nanosecond mtimes — compare against the arm-time baseline. |
| `check --session-ids <SESSION_ID>` (§2.2) | The night's session kind, state, terminality, declared and filled slot counts, exclusion counts by mechanism. |

Preserve the full custody root byte-exact outside watchdog discovery before any
removal, and keep a separate `lstat` inventory of the original with sizes and
`mtime_ns`; a backup's copied timestamps do not substitute for it.

### 2.2 The one mid-campaign query, and what it may not tell you

```zsh
cd "$MEASUREMENT_ROOT"
.venv/bin/python scripts/issue_calibration_acceptance_generation.py check \
  --session-ids "<NIGHT_1_SESSION_ID>"
echo "rc=$?"
```

With at least one non-empty `--session-ids`, `check` prints the epoch-watch
table byte-identically to §0.3 and then APPENDS a **registration dry run**: for
each named session its kind, its state and whether that state is terminal, how
many slots it declared and how many are filled, how many captures are excluded
under each named mechanism, then how many prior-set prefix rows are pending or
unresolved, and finally the line `registration admissible for
prepare-candidate: yes|no` with a `blocker:` line for each obstacle. Every
field is a count, a state name, or a mechanism name.

**Return code when a session is named: 0 = admissible, 5 = inadmissible**
(`DRY_RUN_INADMISSIBLE_EXIT = 5`, script line 160; `check` returns the dry
run's code, deliberately, so that a drifted epoch does not mask the question
actually asked). After night 1 and night 2 the expected code is **5**, with the
blocker naming the sessions that are not yet terminal. That is the correct
mid-campaign answer.

### 2.3 What NOT to read — the blindness fence

Do not open, print, extract, summarise, or ask any agent about ANY captured
value: no `b_fiducial_s`, no minimum, maximum, range, mean or SD, no screen, no
statistic, and no comparison against one. Not from the bundles, not from the
ledger rows, not from a plot, not "just to see if the night worked". The dry
run of §2.2 answers whether the campaign is on schedule; **it cannot answer
what the campaign got, and that is the point.**

The fence is installed in code, not left to discipline: `prepare-candidate`
refuses while any session named in the registration is not terminal, and names
the session it found open. Terminal means the session's last declared slot is
final or the session was aborted. Blindness is why the pre-registration also
fixes membership, exclusion mechanisms, stopping and analysis before any data
exists — so that nothing can be chosen after seeing values.

Whether a capture's bound exceeded r6's level screen `0.032898493715362` IS
recorded in the hashed evidence as a diagnostic — recorded, not read. Leave it
until §4.

### 2.4 The writer-status dispatch: how a slot ends, and how a night ends early

Every capture hands the chain a status number, and the chain **dispatches** on
it — meaning it branches on the exact value rather than treating "non-zero" as
a single outcome. The three branches are not interchangeable, and the harvest
reads a different thing for each:

| Writer status | The ledger row | Chain log line | What the night does |
|---|---|---|---|
| `0` | finalized, disposition `valid` | `slot_end slot=dNN disposition=valid` | Continues to the next declared slot on the unchanged start-to-start cadence. |
| `1` | **finalized**, disposition not `valid` | `slot_end slot=dNN disposition=non-valid` | **Continues, identically.** This is a normal record, not a failure. |
| `≥ 2` | **not finalized** | `slot_refused slot=dNN rc=<status>` | **Stops the night, leaving the session OPEN.** The chain exits with the writer's own status. |

**Why a non-valid capture does not end the night.** The writer exits 1 when the
capture's disposition is not `valid` and 0 when it is, and the ledger row is
FINALIZED either way. An ordinary-invalid capture is a legitimate outcome the
pre-registration already handles, by named-mechanism exclusion at issuance —
and derivation slots are INDEPENDENT of one another: none is an endpoint that
another depends on, unlike a bracket session's two ends. So one non-valid
capture must never cost the captures after it. The chain runs the writer as an
`if` condition for exactly this reason, so that `set -e` cannot exit on status 1
before the dispatch is reached. **Expect `disposition=non-valid` lines in a
healthy night's log** — the pre-registration's own projection assumes a valid
rate near 30/38 — and record their count without reading a value.

**Why a refusal does end it.** Status 2 is the writer's refusal exit
(`emit_refusal`); anything above it is a crash. In both cases the row is NOT
finalized, so continuing would write later slots into a session whose declared
list has a hole nothing accounts for. The chain stops instead — and
deliberately does NOT call `abort-session`. It leaves the session OPEN so that
what this night amounts to is decided at the desk by a person reading the
refusal, rather than by the chain's own guess at 3 a.m.

**Operator action on `slot_refused` — desk recovery, never a retry.** *Desk
recovery* means the S2 recovery tool run by the operator, at the desk, after
the night is over, against the measurement clone: never inside the window, and
never as a re-arm of the same night.

```zsh
cd "$MEASUREMENT_ROOT"
.venv/bin/python scripts/recover_calibration_ledger.py \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  abort-session --session-id "<SESSION_ID>" --plan "<PLAN>" \
  --reason "<the named reason this night actually stopped>"
```

Read the refusal in `chain.stderr.log` and name THAT as the reason. Do not
reach for `window_exhausted`: that is the window's reason and belongs to the
chain's own abort path below. Until the session is closed the ledger head does
not settle, so §3 item 4 bites — the next night cannot open at head-equals-pin,
and a refused night blocks its successor until the desk clears it.

**The other early end: `window_exhausted`.**

If the chain could not reach every slot it logs `slot_unused slot=dNN
reason=window_exhausted`, calls `recover_calibration_ledger.py … abort-session
--reason window_exhausted`, and exits 0. An aborted session IS terminal, and
its finalized observations remain in the prior set.

The correct response is: record the unused count, and **do nothing else**. The
registration forbids top-ups, retries, early stops and outcome-driven extra
nights. All three nights run all twelve declared slots regardless of interim
values; a night that lost slots to the window simply contributed fewer members,
and the shortfall (if any) is resolved at §4, in the open, under Ed's written
ruling. Do not add a fourth night to make the numbers work.

Everything else that can fail mid-night — a refused readiness check, a refused
reservation, a `slot_refused` dispatch — stops the chain with the session still
OPEN, either under `set -e` or by the dispatch's own `exit`. The answer is the
same in every case: desk recovery with the named reason, above. Never a retry
inside the window.

---

## 3. Nights 2 and 3

Identical to §1 and §2, with these differences and no others:

1. **The same registration.** Each night opens its OWN `derivation`-kind
   session with its own `<SESSION_ID>`, and all three session IDs together are
   the registration. Record every session ID in the arm record; §4 passes all
   three to the issuer.
2. **A new plan ID and new coordinates.** Fresh `<PLAN_ID>`, fresh `<t0>`,
   fresh `authored_epoch_s`, fresh night custody root, and the §1.2 arithmetic
   recomputed for that night's dead-man. Never re-arm a published plan and
   never silently edit one.
3. **Distinct calendar days.** The registration requires three windows on
   distinct calendar days.
4. **The terminal pin candidate is reviewed and committed at the desk before
   the next night opens.** The night itself never commits Git. Each night opens
   at head-equals-pin, so an uncommitted terminal pin candidate blocks the next
   night's session open. The pre-registration's `[SEQ]`/`[DIGEST]` fields stay
   as the FIRST night's pin; they are the registration's baseline, not a
   per-night field.
5. **A `check` dry run precedes EVERY arm**, not just the first (§0.3 plus
   §2.2). This is the T38j lesson stated as a rule: the OS-build mismatch that
   voided the previous acceptance was found only because a dry run was run.
   Never skip it because last night's passed.
6. **Every arm goes through email-then-arm** (§1.4), every time. Ed's NO on any
   night's notice stands that night down.

Why three nights, stated before capture (pre-registration §"Why three nights of
twelve slots"): at the historical valid rate 30/38 and r6's replay-retention
ratio 17/19, two nights of 12 slots project
`24 × (30/38) × (17/19) = 16.95` retained observations — below the required 19.
Three nights project `36 × (30/38) × (17/19) = 25.4`. The margin is deliberate,
not generous.

---

## 4. After night 3 is terminal

### 4.1 Confirm admissibility, still blind

```zsh
cd "$MEASUREMENT_ROOT"
.venv/bin/python scripts/issue_calibration_acceptance_generation.py check \
  --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md \
  --session-ids "<S1>" --session-ids "<S2>" --session-ids "<S3>"
echo "rc=$?"
```

Expect **rc 0** and `registration admissible for prepare-candidate: yes`. An
rc 5 prints its blockers: a non-terminal session, or pending/unresolved rows in
the prior-set prefix. Clear the named blocker at the desk — do not capture more
to make it go away.

Carry `--preregistration` here too, and read its appended line (§0.3): it must
still say `match` on the sampler digest. The dry run's return code is what the
command returns when sessions are named, so the sampler comparison is again
reported only in the printed line, never in the code.

### 4.2 Prepare the candidate

```zsh
cd "$MEASUREMENT_ROOT"
.venv/bin/python scripts/issue_calibration_acceptance_generation.py prepare-candidate \
  --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md \
  --preregistration-sha256 "<the digest pinned at night 1's arm, §0.5>" \
  --registration-session-id "<S1>" \
  --registration-session-id "<S2>" \
  --registration-session-id "<S3>" \
  --d125-ruling "<the ruling reference that fixes the D-125 envelope rule>" \
  --out /Users/edr/night-custody/<PLAN_ID>/candidate_acceptance_25g83.json
echo "rc=$?"
```

That is the exact flag set for an ordinary campaign: nothing else is required,
and every remaining flag is an escape or an override discussed below.

**The four fences this command applies, and what each one refuses.** Each was a
promise the pre-registration made that no code read until the arm gate closed
it; they are the reason the flag set is what it is.

1. **The document itself.** `--preregistration-sha256` is argparse-required.
   The tool hashes the file it was handed and refuses `pre-registration sha256
   <observed> does not match the pinned <given>; not issued` on any difference,
   so a candidate can only ever attest to the text the campaign was armed under.
2. **The night count.** Exactly three `--registration-session-id` values, or
   the run refuses `registration names <n> sessions, not the pre-registered 3`.
3. **The slots per night.** Every named session must have DECLARED twelve
   slots — declared, not filled, so a night that lost slots to the window still
   passes — or the run refuses `session <id> declared <n> slots, not the
   pre-registered 12`. Twelve declared × three nights is the n ≤ 36 ceiling the
   registration's admissible degrees-of-freedom range is derived from, which is
   why a differently-shaped corpus is a different experiment whatever its
   statistics say.
4. **The machine.** The `os_build` carried by the registration's rows must equal
   the one parsed out of the pre-registration text, and every member row's T1
   `powermetrics_sha256` must equal the sampler digest that text names;
   otherwise `the registration is void`. This is where the registration's "a
   change to either voids this registration" stops being decorative.

**The two written-ruling escapes.** A *written-ruling escape* is a flag that
permits departure from one pre-registered number, and only by naming the
written ruling that authorised it — the departure is then recorded in the
artifact rather than being invisible. Fences 2 and 3 have one each:
`--nights-ruling` for a session count other than three, `--slot-count-ruling`
for a session that declared other than twelve slots. Both take a reference to
Ed's or a cold gate's written ruling. **When they apply: only after that ruling
exists, and never to make a shortfall issue.** A campaign that came up short
does not acquire a fourth night and then name a ruling for it; the shortfall is
resolved in the open, under §2.4's no-top-up rule and §4.2's corpus floor. The
generator has the matching pair at the other end of the campaign
(`--allow-slot-count` with `--slot-count-ruling`, §1.1b), and the corpus floor
has its own (`--minimum-corpus-size 17` with `--ed-ruling`).

`--out` is **required and has no default**, deliberately: writing into
`configs/calibration/` is the D-138 transaction's act, never this tool's, so
the destination must be named and must be outside `configs/`. `--d125-ruling`
is deliberately NOT `required=True` in argparse, so that its absence produces
the ruled refusal with its reason rather than a usage error.
`--predecessor-acceptance` defaults to the ACTIVE issued acceptance and should
be left alone; it is the artifact the ceiling and the level screen are read
from (below).

The command writes exactly one file, marked `candidate_not_issued: true`,
which the production acceptance loader refuses to load. It licenses nothing.
It derives three OPERATIVES from the corpus: the **bracket screen S**, the
**budget ceiling C**, and the **level screen**. Under the D-125 envelope,
`S = max(new range quantized to 1e-6 s ROUND_HALF_EVEN, 0.010818)` and
`C = max(predecessor ceiling, new Q99)`, where Q99 is the two-draw prediction
at p = 0.995. Issuance refuses `successor_screen_exceeds_budget_ceiling` when
`S >= C`, and that refusal is never cured by lowering S.

Corpus size: `--minimum-corpus-size` defaults to 19
(`SUCCESSOR_MINIMUM_CORPUS_SIZE`); the only other permitted value is 17, and
only with `--ed-ruling` naming Ed's written ruling
(`RULED_ALTERNATIVE_CORPUS_SIZE = 17`). Nothing issues below 19 without it.

**Screen challenge.** If two or more retained members exceed r6's preflight
level screen `0.032898493715362`, the corpus is **not issued** and Ed rules in
writing before any further capture. That threshold is no longer a literal in
the issuer: it is read at run time from the authenticated predecessor
acceptance, at `decimal_derivation.ratified_operatives.preflight_level_screen_s`
— the artifact is the number's one home, so the issuer cannot drift from the
generation it is judging against.

A second diagnostic is recorded but edits no membership: whether the new maximum
exceeds r6's maximum plus r6's range, `0.04262208300415633` (the Decimal sum of
`0.03289849371536248` and `0.00972358928879385`). That one IS a ruled literal in
the issuer, because a ruling fixed its last digits — and it is checked at run
time against the predecessor's own `source_statistics`, refusing `predecessor
maximum plus range <x> does not equal the ruled diagnostic <y>` if the literal
ever stops describing the artifact it was derived from.

### 4.3 The cold science gate packet

The candidate goes to a **cold science gate** — a fresh adjudicating seat with
no campaign context, ruling on a mechanically assembled packet — because no one
who sat on the capture may sit on the exclusions. Assemble the packet from
primary artifacts only:

1. The committed pre-registration at its committed SHA, and the arm records for
   all three nights.
2. The candidate file written in §4.2, whole.
3. The three sessions' dry-run outputs and the chain logs, including every
   `slot_unused`/abort line.
4. The excluded-member list with, per member, its named mechanism, `member_id`,
   `manifest_sha256` and `instrument_evidence_sha256` — and the assertion, to be
   checked, that `affine_clock_fit_empty` is the ONLY registered exclusion
   mechanism, so that an unresolved anchor carrying any other reason must have
   refused issuance rather than quietly excluding a member.
5. The `quantile_proof` block: for each of p = 0.975 and p = 0.995, the
   quantile to 20 decimal places, the forward residual (bound: ≤ 1e-30), the
   agreement digit count between the two independent routes (bound: ≥ 30
   significant digits), both bounds, the closed-form method string, and the
   working precision. Those two bounds are the issuer's DECLARED bounds, not
   ratified constants.
6. The two screen-challenge diagnostics of §4.2 and the S-vs-C comparison.
7. The per-night distribution, order, exclusions and clock-residual margins —
   reported as diagnostics that authorize no trimming.
8. The pre-registration's own **known conditions** — recorded facts about the
   corpus that are not rules and edit no membership. One matters to a reader of
   the resulting acceptance: the night gate does not constrain the display's
   state at `t0` (it requires the screensaver's `idleTime` to read exactly `0`
   and merely records `pmset -g`'s `displaysleep` value), and the derivation
   chain omits the `--sleep-display-before-capture` flag the G2-a chain passes,
   because no operator is present to schedule a display action. These captures
   may therefore differ systematically in display state from the G2-a corpus
   the resulting acceptance will judge. It travels with the packet so the gate
   rules with it in view; it licenses no re-capture and moves no threshold.

### 4.4 The D-138 transaction — named, and out of scope here

Issuing the successor is the **D-138 atomic transaction**: the single reviewed
commit that swaps the live acceptance and every pin that names it. It is out of
scope for this runbook, has its own gate, and must not be started from the same
turn that prepared the candidate.

---

## 5. Failure table

The four tables below are in the order the night can reach them: the generator
refuses at the desk, the wrapper refuses at launch, the chain exits during the
night, and the writer and issuer refuse inside a capture or at the desk after.

Generation-time refusals (`scripts/gen_derivation_night.py`, §1.1b step 3).
Every one prints `FAIL <reason>` on stderr and **exits 2**, and **nothing is
written** — no wrapper, no sidecar, no advisory sidecar. All of them are desk
failures with no window cost:

| Refusal (abridged text) | Meaning | Operator action |
|---|---|---|
| `emit mode requires --<flag> …` | One of the six required emit flags was omitted. | Supply it; see §1.1b step 3 for the full six. |
| `night plan is unreadable` / `night plan is not an exact v2 plan: …` | The plan file will not read, or its key set is not exactly the v2 key set. | Re-author the plan against the §1.1 table. The generator validates through the driver's own parser, so this is the same refusal the night would give. |
| `a derivation night is DIAGNOSTIC_NO_PACK; this plan is <class>` | The plan's `receipt_class` is something else. | A `TRANSACTION_PACK` plan launches a pack launcher instead of the plan's chain, and a `REHEARSAL_STUB` never runs its chain at all, so the wrapper would never execute. Fix the class or stop. |
| `window_max_s <n> < required 7680 + 300 = 7980 s …` | The window cannot hold the programmed span plus the pre-settle allowance (§1.2). | Lengthen the window or move `t0` earlier. Never shorten the settle, cadence, slot count or capture budget. |
| `plan overruns the dead-man: t0 + window_max_s + 300 = <n> is not before the next local 07:00 = <n>; move t0 earlier` | The §1.2 dead-man arithmetic fails. | Move `t0` earlier. Never raise `window_max_s` past the strict maximum and never move the dead-man. |
| `--out <path> is not the plan's chain_path '<path>'` | An output path other than the plan's `chain_path` was requested. | Do not pass `--out`. The refusal exists so the plan and the artifact cannot disagree. |
| `plan chain_sha256_path '<path>' is not '<chain_path>.sha256'` | The plan's sidecar path is not the wrapper's path plus `.sha256`. | Fix the plan; this is stricter than the driver, and it refuses rather than mis-writing. |
| `slot count <n> is not the pre-registered 12; pass --allow-slot-count with --slot-count-ruling <ref> to override` | A slot count other than twelve without the two-flag override. | Use twelve. A departure needs a named written ruling and is announced on stderr and in the wrapper's own header. |
| `--allow-slot-count requires --slot-count-ruling <ref>` / `slot-count ruling reference must be one line of [A-Za-z0-9._:/#@ -]` | The override was requested without an authority, or with one that is not a single line of ordinary reference characters. | Name the ruling in one plain line. The reference is interpolated into the wrapper's header, so a multi-line paste could open a comment and start a live line. |
| `<field> contains the census substring 'codex' \| 'claude' \| 't3': …` | Some emitted literal — a plan ID, session ID, window ID, evidence root ID, frozen plan ID, or any absolute path — contains one of the three substrings the night's own agent census matches. | Rename it. The census runs every 30 s against the process table and would match the wrapper's own command line and kill the night. |
| `<field> must be an absolute path: …` | A path literal is relative. | Use absolute paths everywhere; the wrapper runs with no useful working directory. |
| `frozen calibration plan is unreadable or carries no plan_id` / `a pinned input is unreadable: …` | The frozen calibration plan, the identity-epoch JSON, the T1-bindings JSON, or the tracked chain inside the clone could not be read. | Re-check §0.8 and the night root's contents. The chain is read from the CLONE, so this also catches a mis-cut clone. |
| `--verify`: `FAIL wrapper bytes differ from re-derivation: …` (**rc 3**, not 2) | The installed wrapper or its sidecar is not what these inputs render (§1.1b step 4). | An input drifted. Find which — chain, frozen plan, identity epoch, T1 bindings, or the plan's coordinates. Do not re-emit over the difference. |

Launch-time refusals (the emitted wrapper, §1.1a). Every one prints
`FAIL <reason>` on stderr and **exits 1** before the session is opened, so no
window time and no ledger state is spent. On an agent-free night the only
record is `<NIGHT_ROOT>/night/chain.stderr.log` — read it first:

| `FAIL <reason>` | Meaning | Operator action |
|---|---|---|
| `measurement_root is required` / `must be an absolute path` / `contains control characters` / `measurement_head must be a full 40-character lowercase SHA-1` | The driver's four-variable environment was malformed. | Should be impossible from a valid plan; treat as a driver or plan defect and escalate before re-arming. |
| `night plan id does not match the wrapper` | `NIGHT_PLAN_ID` is not the plan this wrapper was frozen against. | The wrong wrapper was pinned, or a wrapper was reused across nights. Re-emit per night (§1.1b). |
| `measurement_root does not match the wrapper` / `measurement_head does not match the wrapper` | The plan's clone path or head is not the one baked in at arm time. | The plan was edited after emission, or the wrong clone was named. Re-cut, re-author, re-emit. |
| `checkout HEAD cannot be read` / `checkout HEAD does not equal measurement_head` | The clone is gone, is not a repository, or moved off H. | Stand down. Re-cut the clone at H (§0.2) and re-verify §0.8. |
| `measurement venv Python is missing or not executable` | `<CLONE>/.venv/bin/python` is absent. | The clone was renamed or its venv never built; renaming moves editable-install absolute paths (§0.2). |
| `frozen calibration plan is missing` / `identity epoch json is missing` / `t1 bindings json is missing` | A desk-produced input is not in the night root. | Produce it before arming (§0.8) — this is the failure that open question makes likely. |
| `frozen plan is not valid JSON` / `frozen plan has no plan_id` | The frozen calibration plan is corrupt. | Re-freeze at the desk; do not hand-edit. |
| `frozen plan id does not equal the arm-time literal` / `frozen plan bytes do not equal the arm-time digest` | The plan file in the night root is not the one the wrapper was generated from — a swapped or re-written file. | Stop and account for the change. Then re-emit and re-`--verify`; never edit the wrapper. |
| `identity epoch bytes do not equal the arm-time digest` / `t1 bindings bytes do not equal the arm-time digest` | One of the two files whose CONTENTS are copied into every slot record changed after emission. | Same: account for it, re-derive both (§0.8), re-emit, re-`--verify`. |
| `tracked derivation chain bytes do not match the arm-time digest` | The capturing chain inside the clone is not the reviewed bytes — an uncommitted edit, or a clone at the wrong head. | Stand down the night. This is the tripwire §0.8's clean-tree check exists to keep from ever firing at 03:00. |
| exit 1 with **no** `FAIL` line, on a `:?required` guard | The tracked chain ran without the wrapper's environment — i.e. the plan pinned the tracked chain directly instead of the emitted wrapper. | Re-author the plan per §1.1: `chain_path` is `<NIGHT_ROOT>/chain.zsh`. No window time was spent. |

Chain exits (`scripts/night_chains/calibration_derivation_only.zsh`):

| Signal | Meaning | Operator action |
|---|---|---|
| exit 64 | A knob (`SLOT_COUNT`, `SETTLE_S`, `SLOT_CADENCE_S`, `SLOT_CAPTURE_BUDGET_S`, `WINDOW_END_EPOCH_S`) was not a non-negative integer string, or failed the positivity check — which now covers `SLOT_CAPTURE_BUDGET_S` as well as `SLOT_COUNT`, `SLOT_CADENCE_S` and `SETTLE_S`. Refused before the settle, the reservation and any operator-log write. | The environment or plan is malformed. No window time was spent and no partial night exists. Fix at the desk; author a fresh plan for a later night. **Why the budget is in the positivity guard:** at `SLOT_CAPTURE_BUDGET_S=0` the window test `slot_start + budget > WINDOW_END_EPOCH_S` becomes vacuous, so a slot could start one second before the agent-free window ends and capture straight past it. |
| exit 66 `derivation_chain_input_missing: <path>` | One of `PLAN`, `IDENTITY_EPOCH_JSON`, `T1_BINDINGS_JSON`, `CALIBRATION_LEDGER`, `LEDGER_HEAD_PIN` was absent. | The clone is incomplete or a path in the plan is wrong. Re-verify §0.2 and §0.4 before authoring the next night. |
| exit 1 | **Ambiguous — read `chain.stderr.log` to disambiguate.** With a `FAIL <reason>` line it is a wrapper refusal (table above). Without one it is the tracked chain's own `:?required` guard, meaning the chain ran without the wrapper's environment. | Both are pre-window failures costing no window time. Resolve per the matching row above before re-arming. |
| `readiness --phase pre-reserve` non-zero | The ledger was not ready; nothing was written and no window time was spent. It never authorizes ARM even when it passes. | Desk-repair the ledger; do not re-arm the same night on the same signature. |
| `slot_end slot=dNN disposition=non-valid`, night continues | **Not a failure.** The writer exited 1: the row is finalized with a disposition other than `valid`, and the next declared slot runs on the unchanged cadence (§2.4). | Record the count of such slots. Do nothing else, and read no value. Exclusion is decided at issuance, by named mechanism. |
| `slot_refused slot=dNN rc=2` + chain exits 2, session left OPEN | The writer REFUSED this capture (`emit_refusal` exits 2). The row is **not** finalized, so the chain stops rather than continuing over an unrecorded slot — and deliberately does not abort the session. | Read the refusal in `chain.stderr.log`, then **desk recovery**: `recover_calibration_ledger.py … abort-session --session-id <id> --plan <plan> --reason <the named reason>` (§2.4). Never a retry inside the window. Until the session is closed the next night cannot open at head-equals-pin. |
| `slot_refused slot=dNN rc=<n≥3>` + chain exits with that status, session left OPEN | The writer crashed rather than refusing. Same dispatch branch, same unfinalized row. | Same desk recovery, and account for the crash before any further night is armed: a crash is a defect, not an outcome. |
| `slot_unused … reason=window_exhausted` + `session_abort` + exit 0 | The window could not finish a slot's 480 s budget. Slots are recorded unused, never compressed or retried. Δ larger than 1320 s is the usual cause (§1.2). | Record the count. No top-up, no fourth night (§2.4). |
| Any other non-zero exit, with a `session_open` line already in the chain log | A ledger call failed under `set -e` after the session was opened. | Treat exactly as `slot_refused`: read the log, then desk recovery with a named reason. A `session_open` line with no `session_abort` and no terminal slot means the session is still open, whatever the exit code was. |

Writer refusals (`scripts/validate_powermetrics_fiducial.py`, codes in
`joulewise/calibration_exits.py:96–101`):

| Refusal code | Meaning | Operator action |
|---|---|---|
| `calibration_derivation_only_epoch_unchanged` | `--derivation-only` was used while the live identity epoch still matches the active acceptance's. Derivation-only exists only when no acceptance binds the current epoch. | **Stop.** Either the OS reverted or the wrong acceptance was read. Re-run §0.3; do not force the flag. |
| `calibration_derivation_only_session_kind_required` | `--derivation-only` without a declared `derivation`-kind session slot. | The reservation did not open a derivation session, or the slot name is not in its declared list. Fix the reservation; never capture outside the registration. |
| `calibration_derivation_session_requires_derivation_only` | A `derivation`-kind session slot was captured WITHOUT `--derivation-only` — the mid-night flag-loss case the guard exists for. | The chain's writer invocation lost the flag. Stop the night's remaining slots at the desk; the session is recoverable, the mixed evidence is not. |
| `writer_bracket_arguments` | `--session-id`, `--slot` and `--attempt-id` are all-or-none; a partial triple refuses. | Fix the invocation; three values or none. |
| `quiet_mac_auth_required` / `power_policy_required` | `--allow-live` absent, or `--power-policy` not given. | The chain passes `--allow-live` and `ac_high_power`; a refusal here means the invocation was not the chain's. |

Issuer return codes (`scripts/issue_calibration_acceptance_generation.py`):

| Command | rc | Meaning | Operator action |
|---|---|---|---|
| `check` (no `--session-ids`) | 3 | Identity mismatch and/or an acceptance/ledger error. | **Expected throughout this lane** (§0.3). Read the table; confirm the mismatch is `os_build` and only the expected fields. |
| `check` (no `--session-ids`) | 0 | No mismatch, no error. | **Unexpected — stop.** The machine now matches the old epoch; the lane's premise is gone. Escalate before capturing. |
| `check --session-ids …` | 0 | Registration would be admissible. | Proceed to §4.2. Expected only after night 3 is terminal. |
| `check --session-ids …` | 5 | Inadmissible; each blocker is printed. | Expected after nights 1 and 2. Clear the named blocker at the desk; never capture more to clear it. |
| `prepare-candidate` | 3 | `REFUSED: <reason>` and nothing written — a non-terminal session, absent `--d125-ruling`, corpus below the minimum, a pending/unresolved prior-set row, a valid same-epoch observation outside the registration, a member whose stored bytes disagree with its ledger row, a failed quantile proof, `S >= C`, or two or more retained members over the level screen. | Read the reason literally. Several of these are science stops requiring Ed's written ruling (§4.2), not defects to fix. |
| `prepare-candidate` | 3 | The arm-gate fences of §4.2, same `REFUSED:` shape: `pre-registration sha256 … does not match the pinned …; not issued`; `registration names <n> sessions, not the pre-registered 3`; `session <id> declared <n> slots, not the pre-registered 12`; `registration os_build … is not the pre-registered …; the registration is void`; `registration powermetrics sha256 … is not the pre-registered …; the registration is void`; `predecessor maximum plus range … does not equal the ruled diagnostic …`. | None of these is fixed by re-running with different flags. The first three are answered by naming the correct file and sessions, or by a written-ruling escape that already exists (§4.2) — never by inventing one. The two `void` refusals mean the campaign was captured on a machine the registration does not describe: stop, and take it to Ed in writing. |
| `prepare-candidate` | 0 | One candidate file written, `candidate_not_issued: true`. | It licenses nothing. Go to §4.3. |

Night-gate refusals to expect in `result.json`/`refusal.json` (names from
`joulewise/night_gate.py:88–110`): `night_plan_malformed`,
`night_plan_overruns_deadman` (the §1.2 arithmetic was wrong),
`night_refused_agent_present` (§0.6 was violated), `night_refused_boot_clock`,
`night_refused_registration` (the `registration_path` did not authenticate).
`[UNVERIFIED: the full refusal list and each one's exact operator remedy; this
seat read the names and the two lines around them, not each refusal's
implementation.]`

---

## 6. What this runbook does NOT authorize

1. **No G2-a measurement window.** Nothing here licenses one. A G2-a window
   becomes possible only after the D-138 transaction issues the successor
   acceptance — that is the frozen constraint this lane exists to satisfy.
2. **No issuance.** `prepare-candidate` writes a candidate the production
   loader refuses. Issuing is D-138's single reviewed commit (§4.4).
3. **No writing into `configs/calibration/`.** Not by this runbook, not by the
   issuer, not "just to stage it".
4. **No look at any value before night 3 is terminal** (§2.3).
5. **No extra, replacement, top-up or retry night**, no early stop, and no
   outcome-driven schedule change (§2.4).
6. **No amendment of the pre-registration** to accommodate what the data did.
   Its rules were fixed before capture precisely so they could not be.
7. **No arm without Ed's affirmative acknowledgment of V3**, and no arm that
   skips the email-then-arm handback or the pre-arm `check` dry run.
8. **No agent present during any of the three nights**, and no use of the
   chain, driver or a live capture as a quietness test from a live session.
9. **No claim, floor, or paper number** may consume a derivation observation:
   derivation observations are corpus members and never bracket endpoints,
   before or after issuance, and no G2-a, floor or claim output is an input to
   this derivation.
10. **This draft itself authorizes nothing** until the lane is merged, the
    replay is green, and a magistrate ruling adopts it.
11. **No departure from three nights, or from twelve declared slots a night.**
    Nothing here authorises one. Both tools refuse a departure that is not
    accompanied by the written ruling they each require — the generator's
    `--allow-slot-count` with `--slot-count-ruling` at the arm (§1.1b), the
    issuer's `--nights-ruling` and `--slot-count-ruling` at issuance (§4.2) —
    and this runbook does not supply, imply or stand in for such a ruling. The
    flags exist so that a ruled departure is RECORDED in the artifact, not so
    that a campaign can reshape itself around what the nights produced.

---

## 7. Fact table — where each load-bearing fact came from

Read-only sources, all via `git -C <worktree> show HEAD:<path>` except the two
files read in the bookkeeping worktree.

| Fact | Source |
|---|---|
| Chain order, `SLOT_COUNT=12`, `SETTLE_S=600`, `SLOT_CADENCE_S=600`, `SLOT_CAPTURE_BUDGET_S=480`, exits 64/66, `window_exhausted` abort, required env | `JouleWise-wt-epoch-integration` `scripts/night_chains/calibration_derivation_only.zsh` |
| The three-way writer-status dispatch (0 → `disposition=valid` continue; 1 → row finalized `disposition=non-valid`, continue; ≥ 2 → `slot_refused slot=dNN rc=<n>`, exit with the session OPEN and no abort), the writer run as an `if` condition so `set -e` cannot pre-empt it, and the positivity guard covering `SLOT_CAPTURE_BUDGET_S` | same file at the INTEGRATION head, the slot loop and the pre-settle guards |
| `chain_start` logged AFTER the reservation and immediately before the settle — the fact that makes Δ measurable at harvest | same file |
| Chain's own SKELETON / unlanded-surface banner | same file, header comment |
| Chain env fixture (the exact 13 required variables) | `JouleWise-wt-epoch-integration` `tests/test_issue_calibration_acceptance_generation.py:304–345` |
| Writer flags `--allow-live --derivation-only --session-id --slot --attempt-id --power-policy`; all-or-none bracket triple | `JouleWise-wt-s1-writer-derivation` `scripts/validate_powermetrics_fiducial.py:1750–1790`, `:1789` |
| The three derivation refusal codes | `JouleWise-wt-s1-writer-derivation` `joulewise/calibration_exits.py:96–101`; raised at `validate_powermetrics_fiducial.py:1464,1938,1944,1965` |
| `check` semantics, rc 3, dry-run fields, `DRY_RUN_INADMISSIBLE_EXIT = 5` | `JouleWise-wt-s4-issuer-prepare` `scripts/issue_calibration_acceptance_generation.py:160,225–243,254–312` |
| `prepare-candidate` flags, `--out` required and defaultless, `--d125-ruling` not argparse-required, rc 3 on refusal | same file, `:1034–1041`, `:1534–1614` |
| `SUCCESSOR_MINIMUM_CORPUS_SIZE = 19`, `RULED_ALTERNATIVE_CORPUS_SIZE = 17` | same file, `:357,363` at the integration head |
| `check --preregistration` (optional; parses the registered `powermetrics` digest, APPENDS one comparison line, adds an error rather than changing rc); `prepare-candidate --preregistration-sha256` required, `PREREGISTERED_NIGHT_COUNT = 3` and `PREREGISTERED_SLOTS_PER_NIGHT = 12` with `--nights-ruling` / `--slot-count-ruling` escapes; the `os_build` and sampler-digest void refusals; the level screen read from the authenticated predecessor's `ratified_operatives.preflight_level_screen_s`; `R6_MAXIMUM_PLUS_RANGE_S` re-checked against the predecessor's `source_statistics` | `JouleWise-wt-epoch-integration` HEAD `scripts/issue_calibration_acceptance_generation.py` (`preregistration_epoch_pins`, `_authenticated_predecessor`, and the `prepare-candidate` body and parser); these are the three arm-gate blockers report 109 recorded as unenforced, now enforced |
| Three nights × 12 slots, retained n ≥ 19, 16.95/25.4 projections, 128 min schedule, blindness, screen challenge, D-125 envelope, halt on `S >= C`, `0.04262208300415633`, `0.010818`, predecessor ceiling `0.010164834757777545` | `JouleWise-wt-s6-docs-prereg` `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` |
| Fences `[02:45,03:30)` / `[07:00,07:01)`, plan span from `t0 − 25 min`, stand-down ladder −25/−16/−15, 15-minute watchdog liveness, email-then-arm with Ed's NO overriding, `measurement_root`/`measurement_head` install rule | `docs/process/MAGISTRATE_WATCHDOG.md:31,42,46–60,77,329` (bookkeeping worktree) |
| Handback's role, courier reading order, campaign/chain process checks | `docs/process/NIGHT_HANDBACK.md:1–40` (bookkeeping worktree) |
| v2 plan required keys, `night_plan_overruns_deadman`, `registration_path` | `JouleWise-wt-epoch-integration` `joulewise/night_gate.py:38,88–110,112–127,195–276` |
| Generation-time parsing of the two JSON inputs (six exact `IDENTITY_EPOCH_FIELDS`, scalar non-empty values, `power_policy == ac_high_power`; T1 bindings parsed as an object only), `MAX_DECLARED_SESSION_SLOTS = 99` as a desk-time ceiling, and the `CHAIN_ANCHORS` anchor-text discipline | `JouleWise-wt-epoch-integration` HEAD `scripts/gen_derivation_night.py` (`_validated_identity_epoch`, `_validated_json_object`, `CHAIN_ANCHORS`, and the slot-count and window checks in `build_spec`), with `MAX_DECLARED_SESSION_SLOTS` from `joulewise/calibration_ledger.py:76` |
| Δ ≤ 1320 s for `d12` to be admitted at `window_max_s = 9000`; the three components of Δ | the chain's admission test read against the wrapper's pinned knobs; corroborated by the S7 execution refuter's independent derivation (report 104 §7, "the night tolerates up to 1320 s of launch delay") and named as a runbook defect by the seam finding N-3 |
| The three durations reconciled — programmed span 7680 s (128 min), generator minimum 7980 s (133 min), armed `window_max_s` 9000 s (150 min) — and the note that 210 min is the install span, not a window | `JouleWise-wt-epoch-integration` HEAD `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, §"Why three nights of twelve slots" |
| Display state at `t0` is unconstrained by the night gate, recorded as a known condition and not a rule | same file, §"Known conditions (recorded, not rules)" |
| Runbook shape, install span 03:00–06:30, never 07:xx, `t0+window_max_s+300 < 07:00`, strict-maximum arithmetic, Block A/B/record-and-exit structure | `12-arm-runbook-68-g2a-20260912.md` and `11-night-handback-draft-g2a-20260912.md` at `JouleWise-wt-epoch-integration` HEAD |
| Supersession banner shape and the "read the newest activation records" instruction | `13-activation-checklist-2026-09-11.md` at the same head |
| Integration replay RED at `51565cee` | [98-integration-replay-red.md](98-integration-replay-red.md) in this trace directory |
| Epoch↔local conversions and the four arithmetic results in §1.2 | computed this session with `TZ=America/Los_Angeles date -r <epoch>` and shell arithmetic |
| The wrapper mechanism, the thirteen + six exports, the three emitted files, the five-step arm order, the six required emit flags and their defaults, `--verify` rc 0 / rc 3, every generation-time refusal text, `PRE_SETTLE_ALLOWANCE_S = 300`, `programmed_span_s` = 7680 for twelve slots, `CENSUS_SUBSTRINGS` | `JouleWise-wt-s7-night-wrapper` HEAD: `scripts/gen_derivation_night.py` (module docstring and the symbols `programmed_span_s`, `_census_clean`, `_validated_ruling`, `_next_deadman_epoch`, `build_spec`, `render_wrapper`, `emit`, `verify`, `build_parser`, `main`) and the `derivation-night-wrapper` generated region of `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`. `--help` text captured this session by running that file's HEAD bytes read-only from `/tmp`. Cited by symbol, not line: S7's own finding S-2 was that its line citations went stale, and its tests now resolve anchor TEXTS instead |
| Driver hands the chain four variables and no argv (`scripts/run_night.py:430–444`, `tests/test_run_night.py:348–380`); the gate binds the clone by `HEAD` only (`joulewise/night_gate.py:1006–1029`); the reservation copies the identity-epoch and T1-bindings CONTENTS verbatim into every slot record (`scripts/reserve_calibration_window_bracket.py:216–220`) | scout report 101 §0–§2 and S7 contract-lens refuter report 105 §2, §5 (`/tmp/magistrate-96bfeca7/reports/`). Line numbers are quoted as those reports recorded them and were not re-derived by this seat |
| Clean tree and identity-epoch / T1-bindings provenance as arm-checklist items, and "one wrapper per night" | S7 seat report 103 §7.1–§7.4 and its fix-round-1 items B-1, B-2, S-1, S-4; refuter 105 §5 |

Not verified, and flagged in place: the live output strings of `check` on this
machine (§0.3); the producer and custody location of `identity_epoch.json` and
`t1_bindings.json` (§0.8); the 06:05 last-start cutoff's status (§1.3); the
complete night-gate refusal list (§5). **Closed since revision 1:** the driver's
supply of the chain environment and of the per-slot binding argv (§1.1, §1.1a) —
there is no such driver code by design, and the emitted wrapper supplies both.
The wrapper generator's tests live in `tests/test_gen_derivation_night.py`; the
chain's own tests live in `tests/test_issue_calibration_acceptance_generation.py`
under no `test_night_chain_*` name.

---

## 8. First-use table

Every term of art in this file, where it is built, and in one line what it
means. A term is listed only if it does technical work.

| Term | Built at | One-line meaning |
|---|---|---|
| acceptance | §"What these three nights are for" | The issued artifact whose corpus statistics set the thresholds later captures are judged against. |
| identity epoch / epoch | same | The six-field vector `{os_build, hardware_model, power_policy, sampling_interval_ms, estimator_revision, pulse_protocol_id}` an acceptance binds. |
| derivation-only capture | same | A capture taken to BUILD a future acceptance; it licenses no measurement. |
| slot | §Terms | One declared, ordered place for one capture inside a session (`d01`…`d12`). |
| session | §Terms | A ledger capability reserving several attempts under one open receipt at a fixed head pin. |
| registration | §Terms | The set of ledger sessions the pre-registration declares the corpus is drawn from. |
| head pin / head-equals-pin | §Terms | The committed file naming the trusted receipt count and last digest; equality with the physical ledger head. |
| screen / level screen / bracket screen | §Terms, operatives in §4.2 | A threshold a value is compared against; corpus maximum; corpus range. |
| ceiling (budget ceiling) | §Terms, §4.2 | The largest drift a generation will ever budget for; the bracket screen must be strictly below it. |
| blind / blindness | §Terms, enforced §2.3 | No value, screen or statistic is examined before night 3's session is terminal. |
| dead-man | §Terms | The second LaunchAgent that fires at a fixed local minute and stands the night down if completion has passed. |
| fence | §Terms | A half-open local-time interval in which the watchdog refuses to launch or adopt. |
| handback | §Terms | `docs/process/NIGHT_HANDBACK.md`, rewritten and committed with every armed night. |
| email-then-arm | §Terms, §1.4 | Email Ed the notice, arm without waiting for a reply; Ed's NO overrides. |
| `[QUIET-MAC]` | §0.6 | The agent-free machine discipline a capture night runs under. |
| measurement root / measurement head | §0.2, §1.1 | The fresh clone both night agents are installed from, and the commit it is detached at. |
| `DIAGNOSTIC_NO_PACK` | §1.1 | The receipt class for a night with no measurement pack; only C2 is not-applicable. |
| clean tree | §0.8 | The measurement clone has no uncommitted change of any kind: `git status --porcelain` prints zero bytes. |
| wrapper | §1.1a | The generated zsh file, one per night, that carries the night's whole environment as literal `export` lines, authenticates its pinned inputs, and then `exec`s the tracked chain. The plan's `chain_path` names it. |
| night root | §1.1a | `<NIGHT_ROOT>`, the custody directory the plan calls `custody_root`; the three emitted files and the night's desk-produced JSON inputs live in it. |
| sidecar | §1.1a | A small companion file holding another file's SHA-256 in `shasum` output form — the digest, two spaces, a name. |
| advisory (of the third emitted file) | §1.1a | Written for a human's hand-check only; nothing reads it at launch, so deleting or rewriting it changes nothing about what the night will accept. |
| tripwire | §1.1b step 4 | A check that writes nothing and exists only to fail loudly if an input drifted — here, `--verify` re-deriving the wrapper and comparing it byte-for-byte. |
| `zsh -n` | §1.1b step 5 | A syntax check: zsh parses the file and runs none of it. |
| census substring | §1.1b, §5 | `codex`, `claude` or `t3` — the strings the night's own 30 s process census matches; the generator refuses to bake any of them into an emitted literal. |
| programmed span | §1.2 | Chain start to the end of the last slot's capture budget: settle + (slots − 1) × cadence + one budget = 7680 s for twelve slots. |
| pre-settle allowance | §1.2 | 300 s INSIDE the window and BEFORE the settle — the chain's input preflight, its pre-reserve readiness check and the session reservation, plus the driver's pre-launch work. The generator refuses a window below programmed span + this. |
| start-to-start cadence | §1.2 | Slot `d(k+1)` starts 600 s after `dk` STARTED; a long capture is never caught up by compressing a later slot. |
| window_max_s / `WINDOW_END_EPOCH_S` | §1.2 | The plan's window length in seconds, and the exclusive window end the chain enforces. |
| courier / courier deadline / courier allowance | §1.2, §2.1 | The process that emails the night's result; the 300 s the deadline arithmetic reserves for it AFTER the window ends. Distinct from the pre-settle allowance, which is spent inside the window; the two share a number by coincidence. |
| plan span / exit boundary | §0.6, §1.3 | The interval from `t0 − 25 min` in which no agent may be resident; the activation's hard exit time. |
| census | §0.6 | The enumerated process inventory proving no foreign or own agent is live. |
| T1 bindings | §0.3 | The toolchain-identity block a finalization receipt records, including the MLX version in force. |
| frozen triple | §1.5 | `(plan id, measurement root, H)`, repeated verbatim in the next relaunch prompt so the successor harvests the right night. |
| terminal (session) | §2.2 | The session's last declared slot is final, or the session was aborted. |
| dispatch (writer-status) | §2.4 | The chain branching on the capture's EXACT status number rather than on "non-zero": 0 valid and 1 non-valid both finalize the row and continue the night; 2 or more is a refusal or crash that stops it with the session open. |
| desk recovery | §2.4 | Closing an open session with `recover_calibration_ledger.py … abort-session --reason <named>`, run by the operator at the desk after the night is over — never inside the window and never as a re-arm. |
| written-ruling escape | §4.2 | A flag that permits departure from one pre-registered number, and only by naming the written ruling that authorised it, so the departure is recorded in the artifact: `--nights-ruling`, `--slot-count-ruling`, `--allow-slot-count`, `--ed-ruling`. |
| Δ (delta) | §1.2 | The elapsed time from the plan's `t0` to the moment the chain's settle begins: driver gate work + chain preflight + session reservation. `d12` is admitted only while Δ ≤ 1320 s. |
| known condition | §4.3 | A recorded fact about how the corpus was captured that is deliberately not a rule — it edits no membership, moves no threshold, and licenses no re-capture. |
| anchor text | §1.1a | One exact line of the chain, quoted in full as a citation instead of a line number, and resolved against the chain's current bytes by a test. |
| `window_exhausted` | §2.4 | The abort reason recorded when the window cannot finish a slot's capture budget. |
| prior set / corpus / retained n | §Terms | Every ledger observation through the cutoff; the subset whose values are computed from; the corpus size. |
| Q99 / two-draw prediction | §4.2 | `t(0.995, n−1) × sample SD × √2`: how far apart two fresh draws fall at that confidence. |
| quantile proof | §4.3 | The recorded evidence that the Student-t quantile for the realized degrees of freedom was computed correctly two independent ways. |
| screen challenge | §4.2 | The pre-registered halt: two or more retained members over `0.032898493715362` means not issued, Ed rules in writing. |
| cold science gate | §4.3 | A fresh adjudicating seat with no campaign context, ruling on a mechanically assembled packet. |
| D-138 transaction | §4.4 | The single reviewed commit that swaps the live acceptance and every pin naming it. |
| candidate / `candidate_not_issued` | §4.2 | The one file `prepare-candidate` writes, which the production loader refuses; it licenses nothing. |
