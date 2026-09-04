# Cold-gate contract-lens refutation — packet 21 (magistrate relaunch watchdog, third convening)

Seat: Opus contract-lens refuter, paired with an unseen cold Fable judge under
`docs/process/coldgate_charter.md` §5. Charge: attempt falsification of the
packet's claims, the magistrate's labeled dispositions, and the asserted
application of the controlling rulings — not of the judge's unseen ruling.
Date: 2026-09-04. Object: `fdbb840c11aea3f6abd30c9ad5c199487fe7299c`.

---

## 1. Validator receipt

Command (run in `/Users/edr/code/JouleWise-wt-packet21`):

```
python3 scripts/validate_gate_packet.py \
  --packet docs/process_traces/2026-09-02-hands-free-week/21-coldgate-packet-watchdog-v3.md \
  --charter docs/process/coldgate_charter.md \
  --expected-charter-sha256 099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81 \
  --expected-packet-sha256 $(shasum -a 256 <packet> | cut -d' ' -f1)
```

Result: `"result":"PASS"`, exit 0. Schema `coldgate-validator-receipt/v2`.

- expected charter sha256 `099de884…c95d81` — observed identical (supplied to me
  independently of the packet, in the launching brief).
- packet sha256 observed `177d4359c5ef7aba6713767da79f97334b59ab3ccfa30d8efe5c0749d60be6e2`.
- exhibit manifest sha256 `7c6f54bbcef3060948b1ba281ca6ac2f433ba269a732450c4f5cc4aabfc28442`;
  all 43 exhibits' `expected_sha256` == `observed_sha256`.
- `"binding_scope":"validation_time_observation_only"`, `"judge_handoff_bound":false`.
  I record that flag: the receipt does not bind a judge handoff, so the receipt
  proves byte-identity at validation time only and is not launch authority
  (packet §6 says the same).

### 1a. Independent exhibit-fidelity receipt (not required by the packet)

I fetched `origin/feat/2026-09-03-magistrate-watchdog`, confirmed
`fdbb840c11aea3f6abd30c9ad5c199487fe7299c` exists (`git cat-file -t` → `commit`,
`Fri Sep 4 05:28:14 2026 -0700`, subject "watchdog: delta re-audit round 9 CLEAN
(26) — final pre-gate head"), created a detached scratch worktree at that commit,
and compared each code/doc exhibit byte-for-byte with its source at that head:

| exhibit | source at fdbb840c | result |
|---|---|---|
| `magistrate_watchdog.py` | `scripts/magistrate_watchdog.py` | MATCH |
| `install_magistrate_watchdog.sh` | `scripts/install_magistrate_watchdog.sh` | MATCH |
| `night_plan_writer.py` | `joulewise/night_plan_writer.py` | MATCH |
| `test_install_magistrate_watchdog.py` | `tests/test_install_magistrate_watchdog.py` | MATCH |
| `test_magistrate_watchdog_cli.py` | `tests/test_magistrate_watchdog_cli.py` | MATCH |
| `MAGISTRATE_WATCHDOG.md` | `docs/process/MAGISTRATE_WATCHDOG.md` | MATCH |
| `MAGISTRATE_RELAUNCH_PROMPT.md` | `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md` | MATCH |
| `NIGHT_HANDBACK.md` | `docs/process/NIGHT_HANDBACK.md` | MATCH |

I also tested the packet §3 "final delta audit is CLEAN" lineage. Exhibit
`26-delta-reaudit-round-9.md:41` pins its own run at HEAD
`80741aad80618b96181265f7b75615d11cf5e782`, not at `fdbb840c`.
`git diff --stat 80741aad fdbb840c` = one file, `26-delta-reaudit-round-9.md`,
+70 lines. **No code or test byte differs between the audited head and the packet
pin.** The lineage claim survives; I could not refute it.

### 1b. Executed probes (all in a scratch worktree of `fdbb840c`, removed after)

1. Six-module suite, `python3 -m unittest tests.test_magistrate_watchdog
   tests.test_magistrate_watchdog_cli tests.test_install_magistrate_watchdog
   tests.test_night_gate tests.test_run_night tests.test_install_night_agent`
   → `Ran 184 tests in 29.299s` / `OK`.
   Per-module: 60 / 3 / 8 / 47 / 55 / 11 = 184.
2. Four named C-1/C-5 `SupervisorTests` (deadline clamping) → `Ran 4 tests` / `OK`.
3. Independent replay of delta 9's six-case installer rollback matrix →
   `6/6 failure-state cases byte-exact; launchctl stub argv exact`.
4. Real-CLI plan-classification matrix, eight cases, temp custody roots (below).
5. Real-CLI fence-conflict matrix, three cases, real temp git checkouts (below).
6. Real-CLI clamped-drain matrix, four cases, **real `/bin/ps` process table and
   real child processes** — no injected process seam (below).
7. Installer refusal from a temp non-canonical copy → rc 3 `noncanonical_checkout`.
8. Fixture-removal probe on a shadow tree copy.

The real launchctl was never invoked; every launchctl call went to the temp-HOME
PATH stub. No file outside the scratch worktree, `/private/tmp`, and this report
was written.

---

## 2. Verdict table

Legend: **REFUTED** = I found evidence the answer should not be affirmed as
posed. **PARTIAL** = the affirmable core survives but a named limb does not, or
the packet's prose overstates the exhibits. **NOT REFUTED** = I tried and failed.

| Question | Refutation result | Load-bearing evidence |
|---|---|---|
| Q-B1 | **NOT REFUTED** (one residual, NIT) | `21-exhibits/magistrate_watchdog.py:110-141,649-699`; executed cases A–H below |
| Q-CLI | **PARTIAL** | `21-exhibits/test_magistrate_watchdog_cli.py:159-207,292-391`; executed probe 6 |
| Q-SIG-a | **NOT REFUTED** as posed | `21-exhibits/15-delta-reaudit-round-5.md:248`; `21-exhibits/18-delta-reaudit-round-6.md:133`; charter §9 |
| Q-SIG-b | **PARTIAL** — quotes fair; a *third* same-signature YES has no licensing record and no question | `21-exhibits/24-delta-reaudit-round-8.md:134,136`; exhibit gap between 24 and 25 |
| Q-HANDOFF | **PARTIAL** | `21-exhibits/MAGISTRATE_WATCHDOG.md:88-220`; executed probe 6; `21-exhibits/19-sol-fix-round-7-report.md:153-159` |
| Q-INSTALL | **REFUTED — BLOCKER** | `21-exhibits/MAGISTRATE_WATCHDOG.md:105-127`; canonical checkout state (§4 B-A below) |
| Q-C9 | **NOT REFUTED** on the merits; **PARTIAL** on scope | `21-exhibits/17n-bench-launchd-spawn.md:1-12`; `21-exhibits/magistrate_watchdog.py:79-96` |
| Q-FENCE | **NOT REFUTED** (one wording caveat) | `21-exhibits/magistrate_watchdog.py:761-807,1202-1210`; executed probe 5 |
| Q-PROC | **NOT REFUTED** — correctly labeled NOT ADOPTED | `21-exhibits/13-magistrate-synthesis-and-round-5-brief.md:21` |
| P-4 | **REFUTED on verifiability** — MATERIAL hygiene | source file absent from the manifest (§5 H-1) |
| P-5 | **REFUTED on verifiability** — MATERIAL hygiene | source file absent from the manifest (§5 H-1) |
| R-6 | **NOT REFUTED** | `21-exhibits/17j-proposed-ruling-addenda.md:3`; `21-exhibits/19-coldgate-fable-ruling-packet-17.md:29` |
| R-7 | **NOT REFUTED** | `21-exhibits/17j-proposed-ruling-addenda.md:5` |
| R-9 | **PARTIAL** — one clause asserts a state of affairs the artifacts do not exhibit | `21-exhibits/MAGISTRATE_RELAUNCH_PROMPT.md:12` (§5 F-3) |

---

## 3. Per-question refutation attempts

### Q-B1 — merged-tree classifier invariant → NOT REFUTED

`is_retired_v1_plan` (`magistrate_watchdog.py:132-141`) requires
`schema == "joulewise.night_plan.v1"` **and** exact key-set equality with the
golden fixture (`keys <= RETIRED_V1_KEYS and RETIRED_V1_REQUIRED_KEYS <= keys`,
both bound to the same import-time fixture load at `:110-129`). Everything else
falls through to `NightPlan.from_mapping` plus a future-authorship check
(`:685-697`), and every failure populates `PlanSnapshot.errors`, which the
decision path converts to `HOLD_UNSAFE` (`:1206-1210`).

I executed eight real-CLI cases (`python3 scripts/magistrate_watchdog.py tick
--custody-root <temp>`), each with a valid production-written v2 sibling plus one
mutant, and read the resulting `state.json`:

| case | mutant | observed |
|---|---|---|
| A | golden retired-v1 sibling | `decision=HOLD_CENSUS`, v1 ignored, no `HOLD_UNSAFE` |
| B | valid plan truncated to 40 % | `HOLD_UNSAFE` `night_plan_unreadable … JSONDecodeError` |
| C | valid plan minus `measurement_head` | `HOLD_UNSAFE` `night_plan_malformed … missing='measurement_head'` |
| D | v2 body relabeled `schema: …v1` | `HOLD_UNSAFE` `night_plan_malformed … v1 is retired` |
| E | golden v1 + one extra key | `HOLD_UNSAFE` `night_plan_malformed … keys are not exact` |
| F | golden v1 key set, **all values null** | *ignored* — `HOLD_CENSUS`, no hold |
| G | v2 authored 24 h in the future | `HOLD_UNSAFE` `night_plan_malformed … authored_epoch_s is in the future` |
| H | plan file chmod 000 | `HOLD_UNSAFE` `night_plan_unreadable … PermissionError` |

No case produced `LAUNCHING`, and no `attempts/` directory was created in any
hold case. The round-4 fail-open does not recur.

Case F is the only crack and I do not think it is a blocker. Identification is by
key set + schema string, never by value. Any object carrying exactly the v1 key
set is ignored regardless of contents. The counterfactual that would matter — a
current v2 plan degrading into exactly the v1 key set — is not reachable: the v2
required key set is disjoint enough (`measurement_root`, `measurement_head`,
`schema_version`), and `write_night_plan` publishes atomically, so a torn write
yields case B, which holds. The unit test at
`tests/test_magistrate_watchdog.py:214-250` covers golden, golden+v2-key,
v2-minus-version and v2-version-1, but not case F.

**Finding B-1r (NIT):** the packet's phrase "positively identified by the
complete golden retired-v1 shape" should be read as *key-set-and-schema*, not
*value-golden*. Minimum cure if the judge wants it closed: assert in
`is_retired_v1_plan` that every value is of the fixture's per-key JSON type, or
state the key-set-only semantics in `MAGISTRATE_WATCHDOG.md`.

**On "the merged tree."** The packet's Q-B1 stem says "on the merged tree." The
object `fdbb840c` is *not* merged with the current canonical `main`:
`git merge-base --is-ancestor origin/main fdbb840c` fails; `origin/main` carries
119 commits and 194 changed files absent from `fdbb840c`. I tested whether this
is a real hazard and it is not a textual one — `comm -12` over the two
changed-path sets against merge-base `46eaf18c` returns **zero** overlapping
files, and no main-side commit touches `joulewise/night_gate.py`,
`joulewise/night_plan_writer.py`, `scripts/run_night.py`,
`scripts/install_night_agent.sh`, `configs/launchd/`, or any of the six test
modules. So I could not refute Q-B1 on merge grounds. The divergence does
however carry the Q-INSTALL blocker below.

### Q-CLI — production-shaped CLI gate → PARTIAL

The test is genuinely production-shaped where it claims to be: it invokes
`sys.executable` + the real `SCRIPT_PATH` as a subprocess
(`test_magistrate_watchdog_cli.py:141-156`), crosses `main()`, argument parsing,
service locking, `real_dependencies()`, and the classifier, and authors its plans
through the production `write_night_plan` (`:120-127`). Delta 5's R-2/R-3 clause
map (`21-exhibits/15-delta-reaudit-round-5.md:188-189`) checks out against the
file.

Two seams the packet's own wording ("a real subprocess invocation of the real
entry point … real dependency construction") does not disclose, and which I name
as the minimum missing production seams:

1. **The process table is injected in the two drain tests.**
   `test_real_cli_adopts_recorded_resident_on_unsafe_replacement_tick`
   (`:292-386`) runs the CLI through a `-c` shim that replaces
   `deps.processes` with a hand-written `Table` and monkey-patches
   `wd.real_dependencies` (`:331-340`). So the adoption/PID-reuse logic that
   Q-HANDOFF depends on is *not* crossed against a real `/bin/ps` in any
   committed test. Delta 8 flagged the cause honestly
   (`21-exhibits/24-delta-reaudit-round-8.md:103-104`: "The sandbox denied
   `/bin/ps`"), and left live verification to this gate.
   **I closed that gap myself** — see probe 6 below, which reruns the same
   scenarios with real children and real `/bin/ps` and passes.
2. **The positive control never crosses the spawn.** The `FENCED`/`HOLD_CENSUS`
   control runs with `--dry-run` (`:197-207`), so `start_session` /
   `deps.spawn` / `session_argv` are not crossed in any CLI test. The only
   evidence for the spawn is `17n-bench-launchd-spawn.md`, a one-shot manual
   bench with a "reply OK" prompt.

Neither seam is fatal — the class the gate was built to close (unit-green /
production-broken *classification and control flow*) is genuinely closed — but
"real dependency construction" is doing unpaid work in the packet's prose for
the two drain tests. **PARTIAL: affirm the classification limb; do not affirm
that the CLI gate crosses the production process table or the production spawn.**

### Q-SIG-a — did the second consecutive YES require a consult? → NOT REFUTED as posed

Both quotations are byte-exact against their exhibits (I diffed
`15-delta-reaudit-round-5.md:248` and `18-delta-reaudit-round-6.md:133` line by
line, and read lines 244-250 and 128-136 for surrounding context — no selective
quotation; each YES is immediately followed by its RESIDUAL verdict line, which
the packet does not quote but which is not favourable to the magistrate). The
magistrate's own trace 13 concedes the earlier pattern in the same terms
(`13-magistrate-synthesis-and-round-5-brief.md:3`: "rounds 3 and 4 failed with
the same signature … the spend was a CONSULT, not round five"). The question is
posed neutrally and with the contrary evidence in view. I could not refute it.

### Q-SIG-b — does the dissent stand? → PARTIAL

The packet's characterisation of the dissent is accurate:
`16-magistrate-ruling-after-delta-5.md:7` does say the residuals were "gaps in
the magistrate's own round-5 contract, not a re-failure of the seat on a
specified cure," does license round 6 on precise specifications "rather than a
second consult," and does label itself the written dissent. Line 23 does narrow
S-2 to S-2b after delta 6. Fairly represented.

**What the packet does not ask about is a third same-signature YES.** Delta 8
issued `Same-signature statement: **YES**, narrowly for the broader signature
"permitted tests green while an untested production control-flow path fails"`
(`24-delta-reaudit-round-8.md:134`) with `Verdict line: **RESIDUAL**` (`:136`).
Round 9 then proceeded (`25-sol-fix-round-9-report.md`). **There is no exhibit
between 24 and 25** — no magistrate ruling licensing round 9, and no written
dissent for that decision. Charter §9's second bullet ("licensing another
same-shape round requires explicit justification") is therefore unsatisfied on
the record the packet supplies for the round-8→round-9 step, and no atomic
question presents it.

The packet does disclose the delta-8 YES in §2 and quotes it in full in Q-SIG,
so this is an omitted *question*, not omitted evidence. In mitigation, the
round-7→round-8 step was preceded by a full independent counter-review
(`21-opus-counter-review-final.md`), which is a redesign in substance; and
round 9 cured only a should-fix plus a nit. I record it as MATERIAL, not
BLOCKER.

**Minimum cure:** add an atomic question — "did the delta-8 same-signature YES
require a consult or written dissent before round 9?" — or supply the ruling
exhibit that licensed round 9.

### Q-HANDOFF — first unattended handoff mechanism → PARTIAL

Mechanism limbs I verified in code and in execution:

- `owned` vs `unclassified_candidates` separation and explicit
  `--adopt-pid/--start` promotion: `MAGISTRATE_WATCHDOG.md:105-118`, unit tests
  `tests/test_magistrate_watchdog.py:1207,1265`, both green.
- Root-last ordering, per-signal revalidation, absence-is-success,
  start-token-change is reuse-skip, recorded pairs must all be absent
  independently of the census: `MAGISTRATE_WATCHDOG.md:128-219`.
- S-2b replacement-tick adoption and persisted ladder: verified live, not by
  test double. **Probe 6**, real children with real `/bin/ps` start tokens, a
  live recorded session in `state.json`, a truncated sibling plan, and a valid
  plan supplying the deadline:

| t0 | expected clamp | observed state / stage | events | child |
|---|---|---|---|---|
| now+22 min | REQUEST due (t0−25 past) | `HOLD_UNSAFE` / `REQUEST` | `plan_unreadable, transition, resident_adopted, resident_drain_started` | alive, `standdown.request` written |
| now+16 min | TERM due (t0−16 past) | `HOLD_UNSAFE` / `TERM` | …+ `signal` SIGTERM | alive (child ignores TERM — correct) |
| now+14 min | KILL due (t0−15 past) | `HOLD_CENSUS` | …+ `signal` SIGTERM, `signal` SIGKILL, `census`, `transition` | **killed** |
| now+8 h | no clamp | `HOLD_UNSAFE` / `REQUEST` | cooperative only | alive |

That is exactly C-1/C-5 as specified, produced by the real entry point against
the real process table. This is stronger evidence than the packet supplies.

**Why still PARTIAL.** Q-HANDOFF asks whether the mechanism is sufficient "to
authorize the first unattended handoff," and the handoff's *failure* branch has
no addressee. `MAGISTRATE_WATCHDOG.md:220-222` step 6 says "Read the verification
log from an observer after the magistrate exits" and "a nonempty census before
that tick or absence of the new attempt after it is a failed handoff" — but the
acting magistrate has by then killed itself (step 5), Ed is away, and nothing in
the mechanism emails or otherwise reports a failed handoff. Compounding this,
`MAGISTRATE_WATCHDOG.md:61` makes the liveness contract self-referential: "no
`state.json` write for more than 15 minutes means the watchdog is dead, and the
courier email for the next window must say so" — the only writer of that email
is a session the dead watchdog would have had to spawn. **A dead watchdog reports
nothing, to no one, for the whole away week.**

I probed the most plausible cause of exactly that state. `RETIRED_V1_KEYS =
_load_retired_v1_keys()` executes at module import
(`magistrate_watchdog.py:126`), reading `REPO_ROOT/tests/fixtures/
night_plan_v1_retired.json` (`:61`). On a shadow tree with that file removed:

```
RuntimeError: retired-v1 fixture is unavailable: [Errno 2] No such file or directory: …
RC=1
ls: …/magistrate: No such file or directory
```

No argv parsing, no `state.json`, no event, no launch — fail-closed against a
launch, but also fail-silent against detection: under launchd this is a
non-zero exit every 300 s into `launchd.err` with nobody reading it. The
mechanism is honest about having no watchdog-for-the-watchdog
(`MAGISTRATE_WATCHDOG.md:61`); the defect is that the *stated* compensating
control (the next window's courier email) cannot fire in the case it names.

**Finding H-2 (MATERIAL).** Counterfactual input: delete or corrupt
`/Users/edr/code/JouleWise/tests/fixtures/night_plan_v1_retired.json` (or move the
canonical checkout off a commit that carries it) at any point in the away week.
Result: permanently dead supervisor, zero notifications, until Ed returns.
Minimum cure: either (a) reword the liveness clause to name a detector that does
not depend on the watchdog being alive, or (b) make the fixture load lazy inside
`load_plans` so an import failure becomes a written `HOLD_UNSAFE` with an event
rather than an import-time abort.

### Q-INSTALL — executable install/handoff checklist → REFUTED (BLOCKER)

**Blocker B-A: the checklist cannot execute at the pinned object, because the
canonical checkout does not contain the software it tells the magistrate to run,
and the checklist never says to put it there.**

Verified state, this session:

```
/usr/bin/git -C /Users/edr/code/JouleWise rev-parse --abbrev-ref HEAD  → main
/usr/bin/git -C /Users/edr/code/JouleWise rev-parse HEAD               → a6e9edde082f460fbe335d2eac8021f77258b8e6
ls /Users/edr/code/JouleWise/scripts/magistrate_watchdog.py            → No such file or directory
git cat-file -e origin/main:scripts/magistrate_watchdog.py             → does not exist in 'origin/main'
git cat-file -e origin/main:scripts/install_magistrate_watchdog.sh     → does not exist in 'origin/main'
git cat-file -e origin/main:tests/fixtures/night_plan_v1_retired.json  → does not exist in 'origin/main'
```

The checklist steps are:

- `MAGISTRATE_WATCHDOG.md:105,108` — "First `cd /Users/edr/code/JouleWise`, the
  canonical checkout"; `:112` — `scripts/magistrate_watchdog.py handoff-inventory
  > "$handoff_file"`.
- `:119,122` — "Install from that same magistrate session and canonical
  checkout"; `scripts/install_magistrate_watchdog.sh --install`.

The installer *enforces* this: `install_magistrate_watchdog.sh:67-76` refuses any
other resolved repo or git top level, and I confirmed the refusal by executing it
from a temp copy — `noncanonical_checkout: --install requires
/Users/edr/code/JouleWise (script repo=/private/tmp/opus21-instcopy git
root=unavailable)`, rc 3. So there is exactly one place the installer may run
from, and at gate time that place has neither the installer nor the watchdog nor
the import-time-required fixture.

I grepped the whole checklist region (`:88-222`) for a landing step —
`merge|pull|land|main|branch|PR` — and the only hits are the kill-switch
`refs/heads/main` probe (`:59,63`) and step 6's citation of a trace "on main"
(`:220`). **There is no step that lands `feat/2026-09-03-magistrate-watchdog`
into the canonical checkout.**

Counterfactual input: a magistrate with no human present executes step 3
verbatim tonight. Result: `zsh: no such file or directory:
scripts/magistrate_watchdog.py`; no handoff inventory; step 4 unreachable; the
handoff does not occur, and nothing reports that it did not.

This is not a mere documentation gap, because the missing action is one the
process reserves. Landing the branch into `main`/canonical is irreversible
(charter §3 item 3), and the relaunch prompt itself forbids the relaunched
session from doing it — `MAGISTRATE_RELAUNCH_PROMPT.md:22`: "do not merge,
install, deploy, or take irreversible action without its normal authority and
gates." So the checklist's first missing step is precisely a **missing human
decision**, which is the condition Q-INSTALL says must be absent before AFFIRM.
Note also that the merge is not a formality with respect to this gate: the merged
tree — 119 main commits plus this branch — has never had the six-module suite run
against it, and no exhibit reports such a run.

**Minimum cure (both limbs):** (a) insert an explicit, authority-named landing
step before step 3 — who merges, under what authority, and the exact
post-merge verification (`git -C /Users/edr/code/JouleWise rev-parse HEAD`
recorded; six-module suite green on the merged canonical tree); and (b) add the
precondition assertions the checklist currently lacks — `test -x
scripts/magistrate_watchdog.py && test -f
tests/fixtures/night_plan_v1_retired.json` — so a wrong-state canonical checkout
fails loudly at step 3 rather than by shell error.

**What I could NOT refute in Q-INSTALL.** Opus B-2/S-2/S-3 (canonical pinning,
behavioral installer coverage, rollback ordering) are genuinely cured:

- C-2: the temp-copy `--install` refusal above; `--render-only` from a
  non-canonical copy still renders `WorkingDirectory
  /Users/edr/code/JouleWise` and program argument
  `/Users/edr/code/JouleWise/scripts/magistrate_watchdog.py` (I read the
  rendered plist).
- C-8: the same rendered plist pins the absolute interpreter
  `/opt/homebrew/opt/python@3.14/bin/python3.14`; `/usr/bin/env` is absent;
  the installer rejects `/usr/bin/python3` with `unacceptable_system_python`
  (`install_magistrate_watchdog.sh:55-58`).
- C-4/rollback: I independently replayed delta 9's six-case matrix (three failure
  points × prior-plist present/absent) in a temp HOME with a stubbed
  `launchctl`: all six restored the pre-state **byte-for-byte**, and the stub
  argv sequences were exactly `[]`, `[bootout, bootstrap]`, and
  `[bootout, bootstrap, print, bootout]`. Output:
  `6/6 failure-state cases byte-exact; launchctl stub argv exact`.
- Step 5's reaper hardcodes `/usr/bin/python3`, which the installer rejects for
  the plist. I suspected an inconsistency and tested it: `/usr/bin/python3`
  (3.9.6) imports `scripts.magistrate_watchdog` and resolves
  `STOP_COOPERATIVE_S`/`production_census` successfully. **Not a defect.**

One residual worth recording: the installer's behavioral tests reach the
`--install` path only by *rewriting the script's source* to point
`canonical_repo` at a shadow repo
(`test_install_magistrate_watchdog.py:90-96`). The literal canonical string is
exercised only on the refusal path. That is the right trade given no test may
write the canonical checkout, but it means no committed test proves an install
against the real canonical constant. NIT.

### Q-C9 — unexercised courier/Gmail path → NOT REFUTED on the merits; PARTIAL on scope

The packet is candid and its citation holds. `17n-bench-launchd-spawn.md` (the
whole 12-line file) proves only that a launchd-spawned, `ppid 1`, no-TTY
`claude -p` returned one assistant message `"OK"` with `rc=0` in 35 s. **No tool
call, no MCP server, no Gmail send.** I could not find any exhibit that exercises
the courier path, so the packet's claim that it was never exercised is correct
and correctly disclosed.

Where I do push back is scope. Q-C9 frames the gap as the Gmail send. The
unexercised surface is wider: `magistrate_watchdog.py:81-96` launches the session
with `--permission-mode auto --permission-prompts none` and an `--allowedTools`
list of fifteen entries including `Bash`, `Edit`, `Write`, `Agent`,
`mcp__codex__codex` and `mcp__claude_ai_Gmail__send_message`. The code's own
comment at `:79-80` concedes the state of that evidence: "The magistrate can
change one tuple **after the owed permission-prompt bench**." So the packet asks
whether *email* works in a context where whether *any tool* works is, by the
implementation's own admission, an owed bench. That is compounded by the failure
handling: `MAGISTRATE_RELAUNCH_PROMPT.md:21` routes a Gmail failure to a local
file under the custody root — a channel with no reader during an away week.

**PARTIAL. Minimum pre-night evidence** (narrower and cheaper than a night):
re-run the 17n throwaway LaunchAgent once with the *real* rendered prompt shape
and argv tuple, and require the transcript to show (i) a successful
`mcp__claude_ai_Gmail__send_message` tool call, (ii) at least one `Bash` and one
`Edit`/`Write` call completing without a permission prompt, and (iii) the
`heartbeat` and `notice.ack` files written in the documented order. Paste the
`stream-json` tail. Absent (i), the entire notification contract — launch email,
stand-down email, pending notices, forced-stand-down report — is unevidenced.

### Q-FENCE — dynamic checkout fence and conflicts → NOT REFUTED

All four limbs verified by execution against real temp git checkouts:

| scenario | observed |
|---|---|
| one measurement root, two heads | `decision=HOLD_UNSAFE reason=plan_conflict: one measurement_root has multiple heads: root=… heads=['1afb1cbb…','e34e76f7…']` |
| overlapping spans, different roots | `decision=HOLD_UNSAFE reason=plan_conflict: overlapping spans use different measurement roots: a=…, b=…` |
| non-overlapping spans, different roots | `decision=LAUNCHING reason=all launch predicates clear`; prompt rows = canonical repo + both plans |

Code: `plan_conflicts` at `magistrate_watchdog.py:765-795`, `fenced_checkout_rows`
at `:797-807` (row 0 is `["__canonical_repo__", str(CANONICAL_REPO), None]`),
recomputed every tick from `armed_plans` at `:1202-1204` and `:1195-1201`.
`plan_is_armed` (`:1694-1705`) is exactly "authored and not completed": authored
in the past, and either `chain.started` without `chain.exited`, or no
`courier.sent` and inside the deadman window. The packet's description matches.

**Caveat (NIT), not a refutation.** "Dynamic" here means the row set is
recomputed each tick from the pinned triples — **not** that the watchdog reads
any measurement root's actual HEAD. It never does; nothing in the watchdog
detects a post-arm move. Enforcement of `MAGISTRATE_WATCHDOG.md:86`'s "a post-arm
move invalidates the pin" rests on (a) the prompt sentence at
`MAGISTRATE_RELAUNCH_PROMPT.md:10`, i.e. the agent's compliance, and (b) the
night gate's `night_plan_stale` check at run time. A judge affirming Q-FENCE
should affirm the four enumerated limbs as written and not read "fully enforce
the dynamic checkout fence" as watchdog-side HEAD verification.

### Q-PROC — process proposal → NOT REFUTED

The text is quoted exactly from
`13-magistrate-synthesis-and-round-5-brief.md:21`, which itself reads "Process
proposal (NOT adopted here; for packet 21 / the cold gate)". The packet's
`PROPOSAL — NOT ADOPTED` label is faithful, and I found no place in the exhibits
or the code where the rule is treated as binding. Correctly labeled.

### Q-PROP — P-4, P-5, R-6, R-7, R-9

**P-4 and P-5 — REFUTED on verifiability (MATERIAL).** Their source,
`docs/process_traces/2026-09-02-hands-free-week/15-watchdog-gate-synthesis.md:23-25`,
is **not in the exhibit manifest** — I grepped all 43 entries; the packet cites
it only by a digest recorded inside another exhibit
(`17-coldgate-packet-planpin-watchdog.md:33-35`). I verified the digest
mechanically: `shasum -a 256` of that file =
`f6c80cbaff8a03d4c56a1e93608d661cf853624565a679c8a6d5db5964dd17f2`, matching the
packet, and the file is exactly 25 lines. But a digest proves only that some
file is unmodified; it cannot show that the quoted bullets are complete or
neutrally excerpted. The cold judge is barred by charter §4 from reading a
narrative synthesis that is not a bounded admissible exhibit, and I am
identically bounded by my brief — so **neither reviewer can perform the
selective-quotation check that charter §4 requires**, which is the express
condition for REFUSE.

Worse, the packet asserts a check that its own bytes do not support: "the heading
plus both contiguous bullets are represented here so selective quotation can be
checked." **No heading appears anywhere in the P-4/P-5 subsection** — only the two
bullet texts. That is prose claiming something the packet does not show.

Minimum cure: copy `15-watchdog-gate-synthesis.md` (or its lines 20-25, heading
included) into `21-exhibits/` and add it to the manifest, exactly as 17j was
handled.

**R-6 — NOT REFUTED.** The amended text is consistent with the shipped behavior
I could check: `NightPlan` carries `measurement_root`/`measurement_head`;
future-authorship and exact-key checks fire at load
(`magistrate_watchdog.py:685-697`, executed cases C/E/G above); retired v1 is
rejected at the v2 path with the "is retired" message (case D). The integration
of `17j:3` + `18-coldgate-opus-refutation-packet-17.md:99-103` +
`19-coldgate-fable-ruling-packet-17.md:29` is fairly described, and 17j is an
exhibit whose line 3 I read.

**R-7 — NOT REFUTED.** 17j line 5 is the R-7 addendum; the amended text adds
nothing the exhibits contradict.

**R-9 — PARTIAL.** Most clauses are corroborated by the shipped artifacts: the
25/16/15-minute ladder and the clamp (`MAGISTRATE_WATCHDOG.md:44-48`, and my
probe 6 which produced exactly those boundaries); ten-second resident poll
(`tests/test_magistrate_watchdog.py:544`); no network I/O on the enforcement path
(`MAGISTRATE_WATCHDOG.md:40,59`); the 300 s tick (plist `StartInterval 300`);
the `refs/heads/ops/stop*` glob (`MAGISTRATE_WATCHDOG.md:63`); nine-minute
cooperative + one-minute TERM→KILL outside a plan (`STOP_COOPERATIVE_S=540`,
`STOP_TERM_GRACE_S=60`).

**Finding F-3 (NIT, but it makes the text non-installable as written):** R-9
asserts "**Both the magistrate and night LaunchAgents are named as wake
sources.**" I grepped `docs/process/` for "wake source". The only occurrence is
`MAGISTRATE_RELAUNCH_PROMPT.md:12` — "the LaunchAgent is then the wake source",
**singular**, naming one agent. If R-9 is ratified verbatim it asserts a state of
affairs the artifacts do not exhibit, and would be non-conformant on the day it
is adopted. Exact replacement wording for that sentence: *"The magistrate
LaunchAgent `com.joulewise.magistrate` is the wake source for the relaunched
session; the night LaunchAgent is the wake source for the measurement chain.
Both must be named as wake sources in `MAGISTRATE_RELAUNCH_PROMPT.md` before
this clause takes effect."*

---

## 4. Blockers and findings, with counterfactual inputs

**B-A — BLOCKER (Q-INSTALL).** The checklist has no step landing the watchdog
implementation into the canonical checkout, and the canonical checkout does not
contain it. Counterfactual input: run `MAGISTRATE_WATCHDOG.md:108-112` verbatim
against `/Users/edr/code/JouleWise` at `a6e9edde` (main). Result: no such file;
handoff and install do not happen; no failure notification. The missing step is
also an irreversible action the relaunch prompt (`:22`) forbids the session to
take on its own — a missing human decision. Cure in §3 Q-INSTALL.

**H-2 — MATERIAL (Q-HANDOFF, Q-INSTALL).** The liveness contract at
`MAGISTRATE_WATCHDOG.md:61` names, as the detector for a dead watchdog, an email
that only a watchdog-spawned session can send. Counterfactual input: remove
`tests/fixtures/night_plan_v1_retired.json` from the canonical checkout (executed
on a shadow tree: `RuntimeError: retired-v1 fixture is unavailable`, rc 1, no
`state.json`, no event). Result: silent permanent stop for the away week. Also
applies to a failed handoff (step 6 has no addressee once the acting magistrate
has exited). Cure in §3 Q-HANDOFF.

**S-A — MATERIAL (Q-SIG-b).** A third same-signature YES
(`24-delta-reaudit-round-8.md:134`, verdict RESIDUAL at `:136`) licensed round 9
with no exhibited ruling and no written dissent, and no atomic question presents
it. Counterfactual input: ask what authority licensed round 9; the exhibit set
between 24 and 25 is empty. Cure in §3 Q-SIG-b.

**H-1 — MATERIAL, packet hygiene (P-4, P-5).** Their source file is outside the
manifest, so charter §4's completeness/neutrality check is impossible for both
reviewers; and the packet's assertion that "the heading … [is] represented here"
is not borne out by its own bytes. Affects P-4 and P-5 only. Cure in §3 Q-PROP.

**C-A — PARTIAL, scope (Q-C9).** The never-exercised surface is the whole
headless tool-permission path (`magistrate_watchdog.py:79-96`, whose comment
names an "owed permission-prompt bench"), not only Gmail. Minimum pre-night
evidence in §3 Q-C9.

**Nits.** B-1r (retired-v1 identification is key-set-only, values unvalidated —
executed case F). Q-CLI seams 1 and 2. Q-FENCE "dynamic" wording. F-3 (R-9 wake
sources). Install-path canonical constant exercised only via a source-rewritten
shadow.

---

## 5. Additional packet-hygiene observations

- **H-3 (NIT).** `tests/test_magistrate_watchdog.py` — 60 of the 184 tests, and
  the *only* test coverage for the C-1 deadline clamping that Q-INSTALL and
  Q-HANDOFF depend on — is **not** in the 43-exhibit manifest, while the two
  smaller test modules are. The packet tells the judge that "code locations below
  refer to the copied exhibits," so a judge confined to exhibits cannot verify
  that coverage. Cure: add it to `21-exhibits/`.
- **H-4 (NIT).** §5's carry-forward disclosure is scrupulous and I verified it
  arithmetically: round 8's per-module tails 60/3/6/47/55/11 = 182
  (`23-sol-fix-round-8-report.md:99-125`); round 9 touched only the installer
  module (+2 tests) and `test_magistrate_watchdog`; my six-module run at the
  packet pin gives 60/3/8/47/55/11 = **184 OK**. The packet's refusal to claim a
  round-9 six-module command it did not run is exactly right, and this seat's
  execution now supplies it.
- **H-5 (NIT).** Q-HANDOFF cites `MAGISTRATE_WATCHDOG.md:88-220` and Q-INSTALL
  cites `:88-222` for the same checklist; 221-222 is the arming/rehearsal
  paragraph. Harmless inconsistency.
- I found **no** cherry-picked excerpt, no unlabeled argument, and no asymmetric
  framing in the two Q-SIG quotations or the Q-PROC label. Where the packet knew
  a fact was unfavourable — the C-9 gap, the round-9 carry-forward, the retained
  live-evidence gap at `19-sol-fix-round-7-report.md:153-159`, the prior seat's
  REJECTs — it stated it in the stem. That is materially better hygiene than the
  packet-17 convening.

## 6. Explicit disagreement with the magistrate's labeled dispositions

- I **disagree** that the install/handoff checklist is executable tonight by a
  magistrate with no human present (Q-INSTALL): finding B-A.
- I **disagree** that the packet's Q-SIG set is complete: the delta-8 YES and the
  unlicensed round 9 are not presented as a question (S-A).
- I **disagree** that P-4 and P-5 are in a rulable state on this record (H-1);
  on the charter's own terms those two are REFUSE candidates.
- I **concur** with the magistrate's labeling of Q-PROC and every Q-PROP text as
  NOT ADOPTED, with the dissent at `16-…:7` standing as to rounds 6 and 7, with
  the C-9 gap being real and correctly exposed rather than absorbed, and with the
  C-1 through C-8 cures being genuine — several of which I verified live and more
  strictly than the packet claims.
- Nothing irreversible is requested by the packet itself; it makes no merits
  claim and supplies no launch authority. The irreversible action that Q-INSTALL
  *implies* — landing the branch into the canonical checkout — is the one the
  packet does not name and for which no rollback is stated. That is B-A.

Seat: Opus contract-lens refuter. Sealed for synthesis under charter §5.
