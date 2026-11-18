# STRUCTURE: the replacement

Mythos 5.2 process audit, 2026-11-17. Sources: `origin/main` at `2e07ef699`, `origin/audit/2026-11-10-fable` at `aeadb9122`. Companion files: `RULES.md` (inventory), `CUT.md` (what goes), `MIGRATION.md` (the order of work).

## 0. The one idea

**The machine never waits for a person, a second computer, a clock or a count. Only a queue entry can wait, and only for a reason the scheduler can name as PHYSICS, VALIDITY or SAFETY.**

Today a rule is a paragraph. The magistrate (an LLM) reads it, the lead copies it into the next item as shell, and it never expires. The record for 15 to 17 November shows the result (`RULES.md` section 1): of 72 hours the MBP spent 26.4 h on work that produces evidence, 19.8 h on F0 (a diagnostic the research lead calls "load without product", `RLD:17172`) and 25.7 h idle.

The replacement has four parts:

| Part | What it is | Replaces |
|---|---|---|
| **Queue** (`docs/process/mbp/QUEUE.json`) | Every piece of work the MBP may run, as data: counted spans, v4 sessions, product fillers, diagnostic fillers | Per-span RUN_STATE items of about 56 KB with about 450 lines of shell each |
| **Register** (`docs/process/RULES.json`) | Every stop condition, as data: class, reason, owner, review date, and the name of the function that tests it | Standing items 346, 347, 348, 388, 395, 396, 399, 409, 415 and the operational clauses of RL-149 to RL-177 |
| **Scheduler** (`scripts/mbp_sched.py`) | One function: queue + register + host facts + clock gives one decision and its reason | The magistrate's reading of prose; the "Start and check" blocks |
| **Log** (`RUN_STATE.md`, typed items only) | What happened, written by tools, a few lines per event | 20,909 lines that are part history, part law, part program |

"RLD" below means `docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md` on the audit branch. "RS" means `RUN_STATE.md` on main.

---

## (a) The MBP scheduler

### a.1 Host states

There is one host and it is in exactly one state.

| State | Meaning | What runs on the host |
|---|---|---|
| `FREE` | Nothing is armed. The last run is closed and its close is proven | The tick (magistrate activation now; a LaunchAgent later) |
| `ARMING` | The tick has chosen an entry and called its pinned launcher. The launch lock is held | The launcher |
| `RUNNING` | A launcher fence names a live run | The pinned runner and its collectors. No agent, no SSH, no other job |
| `CLOSING` | The run ended. Close steps are owed | The close script |
| `HALTED` | A fault that re-checking cannot clear | Nothing. Ed and the lead are paged |

Transitions:

| From | To | Trigger | What is written |
|---|---|---|---|
| `FREE` | `ARMING` | `next` returns an entry. It always does unless a host stop holds (a.2) | Ledger line: entry id, the predicates evaluated |
| `ARMING` | `RUNNING` | Launcher exits 0 and its fence is claimed | Typed RUN_STATE line (generated); arm notice where the entry's route requires one |
| `ARMING` | `FREE` | The launcher refuses on one of its own checks | Refusal record with the launcher's reason. That entry is ineligible until one of its inputs changes (a.3, E6). `next` is evaluated again at once |
| `RUNNING` | `CLOSING` | Fence gone and process group absent | Nothing yet |
| `RUNNING` | `HALTED` | Fence deadline passed and a process of the run is still alive | Page |
| `CLOSING` | `FREE` | Close proof passes: receipt present, every restore line read back, every feed proven stopped. The copy has started; it need not have finished (a.5) | Close record (JSON) and one typed RUN_STATE line (generated) |
| `CLOSING` | `HALTED` | A restore line cannot be proven | Page |
| `HALTED` | `FREE` | A typed clear record that names the halt and the evidence | The clear record |

A run that ends with no receipt and no live process is closed as `STRANDED`: host state is restored by the runner's own restore command, the directory is kept and copied, and the host returns to `FREE`. It does not wait for the lead.

### a.2 Host stops: the complete list

These are the only conditions under which a `FREE` host launches nothing. Each is a physical fact about the machine or a safety fault. None names a person, the Air, a calendar date, a time of day or a count.

| Id | Class | Condition | What the tick does |
|---|---|---|---|
| H1 power | PHYSICS | Not on AC, or charging when the kit requires a floating battery | Re-check every 5 min; page after 15 min |
| H2 disk | PHYSICS | Free space below the floor (today 60 GiB; the floor should be three times the largest span output) | Evict local copies of already-uploaded archives, then re-check; page if still below |
| H3 meter | PHYSICS | The KM003C is absent or not polling | Page |
| H4 unclean host | SAFETY | The last close is unproven, a runner process group is alive, or a High Power marker exists with no owner | `HALTED` |
| H5 foreign load | PHYSICS | An agent, SSH job, packer or any process outside the measurement set is alive at the arm (the meaning of "quiet", Ed 11-14, RLD:17041) | Wait and re-check; this is the only wait whose length the scheduler cannot predict. A magistrate activation's own process tree is exempt, as now, because it exits before the soak starts |
| H6 owner stop | owner | A `directive` issue from Ed that starts STOP, NO, HALT or VETO (RLD:12661), or the watchdog's STOP card | Launch nothing new |

Thermal state is not on this list because it is not a scheduling question. Every span begins with its own soak and its own G0 thermal gate inside the pinned runner (RLD:17154, "the start state belongs to the successor's own soak"). The scheduler adds no clock gap on top of it once question F-2 in `CUT.md` is answered; until then the two gaps (300 s after a campaign close, 1,200 s after anything else) stay as a timed predicate on the entry, E2.

### a.3 Entry eligibility: the complete list of predicate kinds

An entry is eligible now if every predicate it names holds. An entry that is not eligible is skipped; the host does not wait for it.

| Id | Class | Predicate | Where its parameters come from |
|---|---|---|---|
| E1 pin | VALIDITY (prereg) | The entry's pin, kit hash and queue hash are on the admitted list | Written when the kit PR merges |
| E2 window | VALIDITY (independence) | The registered timing conditions of this entry: its t0-date window and the day-balance counts (RLD:17228-17233); for a qualification span, clear of the predicted OS batch (RLD:17822); phase order (no qualification before the freeze-2 hash is on main, RLD:12659); the close gap until F-2 is ruled | The kit's own committed queue file and the receipts of spans already run |
| E3 dependency | VALIDITY | The first span of this block closed clean; a consumer leg's span reference exists (the runner checks this itself); any hand gate the research lead keeps, as a typed gate record | Receipts; gate records |
| E4 fits | PHYSICS (contention) | This entry's worst case plus its close ends before the latest feasible start of every higher-priority entry. Latest feasible start is worked backward from the end of that entry's window through everything that must still run in it (Astra window-schedule finding 4) | Computed |
| E5 launcher | PHYSICS / VALIDITY | The pinned launcher's own dry run admits this t0 (`plan`, `validate-kit`, the fence and batch-window code that is frozen in the pin) | The launcher. The scheduler calls it; it does not re-implement it |
| E6 not refused | SAFETY | This entry was not refused since its inputs last changed. Inputs are the queue commit, the kit and pin, and the host fact the refusal named | Refusal records |
| E7 session route | VALIDITY (registered) | For a v4 session only: the READY record, the owner notice and the veto interval of its registered arming procedure | The session's own route |

There is no predicate for: the lead being present, the Air being present, a watcher heartbeat, the age of an entry, how many entries are issued ahead, a desk being final two spans back, a count of runs per day, spacing between fillers, or a pre-launch record. Those are the PACING rows in `RULES.md`.

### a.4 The queue

One file on main, `docs/process/mbp/QUEUE.json`, validated in CI. An entry:

```json
{
  "id": "f2-inst-p2-L004",
  "kind": "product_filler",
  "launcher": "cadence_span",
  "worktree": "/Users/edr/code/jw-wt/cadence-f2-inst-p2",
  "argv": ["<the pinned launcher's command line>"],
  "plan_argv": ["<the pinned launcher's dry run, where it has one>"],
  "pin": "2d347f721552fe03bdd19f113e7bad7a7c24908e",
  "kit_sha256": "<64 hex>",
  "expected_s": 3600,
  "worst_case_s": 5850,
  "close_gap_s": 1200,
  "requires": ["pin-admitted", "counted-fits", "launcher-admits", "not-refused"],
  "params": {},
  "repeat": false,
  "product": "instrument characterization (RL-169)"
}
```

Kinds, in priority order:

| Priority | Kind | Examples | Notes |
|---|---|---|---|
| 1 | `v4_session` | The R1 slot session, W1, C and T windows | Takes the next clean close once READY (RLD:17288). **If its arm refuses it is not eligible, and the ladder continues.** READY priority never idles the host |
| 2 | `counted` | dev, qual, ctl, reserve spans | Earliest latest-feasible-start first. Within a block, the second span outranks everything once the first has run |
| 3 | `product_filler` | F2 pieces and single F2 legs (RLD:17159), hp-02, the dated transfer block once designed (RLD:17278), Flash-Next on real weights (F1, RLD:14394) | Finite. Produces something the paper or the next design uses |
| 4 | `diagnostic_filler` | F0 while it is kept; any standing instrument series | Standing (`repeat: true`). No prerequisites that need a person |
| 5 | `maintenance` | Disk packing, a restart, a host-setting change | Scheduled like work so its cost shows in the ledger. Never posted as a prose hold |

`requires` lists register rows by id (section b.1); each row names the predicate of a.3 that tests it. A counted span adds `registered-window` and `block-dependency`, with its date window and caps in `params`. Brief A in `briefs/` fixes the exact fields.

**The queue invariant: at least one `repeat: true` entry whose `requires` holds no window (E2), dependency (E3) or session-route (E7) rule.** CI refuses a queue file without one. That entry is what makes "no gap ever waits for the lead" true by construction. If `next` still finds nothing eligible, it returns `QUEUE_EMPTY` and pages the lead at once (RLD:12668 already makes "MBP unarmed with no job queued" an alarm; the audit found the code word `DESIGN_QUEUE_LOW` used twice in all of RUN_STATE).

**Choosing among fillers.** Take the first in ladder order that passes E4. When a counted entry carries `expected_ready_by` (the typed form of RL-175's pre-notice, RLD:17723), prefer a filler whose expected end is before it. A short filler is how priority inversion is avoided; holding the host empty is not.

**Who writes the queue.** The lead, by a commit. The interim lead and the magistrate may append entries from committed drafts (RS:2979, item 388 fallback 4). Nothing in an entry expires by age. An entry stops being valid when its pin or kit hash leaves the admitted list or its window closes.

### a.5 The close

One script, `scripts/mbp_close.py`, with no model in the loop:

1. Prove the close: receipt present and parsed for structure only; every restore line read back (power mode, network time off, frequency word 0, no stray monitor, no High Power marker); every feed proven stopped.
2. Run the automatic desk (deterministic, no energy fields, RLD:17462) and the automatic checks that are done by hand today: the consumer-gate read (L002/L005), the reference print, the maintenance-log table. A failure here marks dependents ineligible (E3). It does not stop the host.
3. Start the encrypted cloud copy. **The copy is a debt, not a gate** (`CUT.md` O-02): the next arm does not wait for the provider's confirmation. The copy tool is stopped before the next soak starts (RLD:17452) and resumes at the next close. Originals are never deleted on this path.
4. Write the close record and one generated RUN_STATE line.

Copy debt is bounded as a SAFETY rule: page the lead when any span has been uncopied for 2 h; hold `counted` and `v4_session` entries (not fillers) when counted data has been uncopied for 24 h.

### a.6 Who runs the tick

- **Now:** the magistrate. Each activation runs `python3 scripts/mbp_sched.py tick`, which closes if a close is owed, then prints one decision and the exact launcher command. The magistrate runs that command as its last action and exits. It does not read rules from RUN_STATE.
- **Later, only if the record supports it:** a LaunchAgent runs the same `tick` every 60 s with no model. This is tier 2 (it arms). It is built only after `next` has agreed with the magistrate's own decisions on 10 consecutive closes in shadow. It replaces PR #800, whose 2,400-line controller exists to enforce rules this audit cuts.

### a.7 The ledger

Every tick appends one line to `mbp_ledger.jsonl` in the custody root: time, state, entry, and for any wait the id of the register row that caused it. `mbp_sched.py report --since <date>` prints hours by state and hours by rule. This is the "productive fraction" Ed asked for on 11-08, and it is what the retirement pass reads (b.4). No rule's cost is estimated by hand again.

---

## (b) How a rule is written, expires and is retired

### b.1 A rule exists only as a register row

`docs/process/RULES.json`, one row per rule:

| Field | Content |
|---|---|
| `id` | Short stable name |
| `class` | `PHYSICS`, `VALIDITY` or `SAFETY`. There is no fourth value. CI refuses any other |
| `protects` | One sentence naming the physical quantity, the claim or registration, or the data that would be lost. "So the lead can check" and "to be safe" are not accepted |
| `test` | The name of the scheduler predicate or close step that evaluates it, or `pipeline:<step>` for a review rule |
| `scope` | Entry kinds or the PR tier it applies to |
| `source` | The ruling or decision that introduced it |
| `owner` | Who may retire it: `lead`, or `research_lead` when `protects` is blinding, prereg or physical safety |
| `added`, `review_by` | Dates. `review_by` is at most 14 days after `added` or the last renewal, or `end of <campaign or pin>` for a VALIDITY row tied to a registration |
| `status` | `LIVE`, `FLAG` or `RETIRED` |

**The scheduler evaluates only `LIVE` rows that name a `test`.** A paragraph in a RUN_STATE item, a ruling, an email or a kit README that says "never", "always" or "at most" and has no row is not executed, because nothing executes prose any more. This is what "a rule without a stated physical, validity or safety reason does not exist" means in practice.

### b.2 How a rule is added

One commit that adds the row and, when a new `test` is needed, the predicate and its test. The commit message states the incident or ruling. A research-lead ruling that carries operational clauses ends with a block "Register: rows added, rows retired"; the lead commits those rows with the ruling. A clause with no row is commentary.

### b.3 Expiry

- A row past `review_by` whose owner is `lead` becomes `FLAG` automatically: the scheduler prints it and does not stop on it. Nobody has to remember to retire it.
- A row past `review_by` whose owner is `research_lead` stays `LIVE` and the lead is paged daily until it is renewed or retired. Blinding, prereg and physical-safety rules do not lapse by neglect.
- A VALIDITY row scoped to a campaign or pin is retired by the commit that closes that campaign or retires that pin.

### b.4 The retirement pass

At each block close, or every 14 days, the lead runs `mbp_sched.py report` and for each `LIVE` row reads two numbers: hours of WAIT it caused and the count of times it fired. A row that never fired in two passes is retired unless its owner renews it with a reason. A row that cost more than 30 minutes a day is brought to its owner the same day with the number.

### b.5 No waivers

A rule that needed a waiver is wrong. The response is to retire the row or change its `test`, in the register (Ed, 11-17, on item 412). The register has no "waived once" status.

---

## (c) The pipeline from idea to merged code

`docs/process/PIPELINE.md` (merged 11-17 with PR #810) already has the right shape: three tiers and a three-round cap. Eight changes make it match the rest of this structure and the record in `RULES.md` section 3.10. They are edits to that file, not a new document.

| # | Change | Why |
|---|---|---|
| 1 | **Narrow tier 2.** Tier 2 is: code on a frozen measurement path (it changes what is measured); code that deletes or moves an original; code that reads sealed outcomes or computes, selects or excludes a claim number; and anything that arms without a model or person in the loop. Copy-only tools, read-only schedulers, records, queue and register data, and kit data on an admitted pin are tier 1 or tier 0 | "Arms, measures, offloads or deletes on the MBP" (PIPELINE.md:14) swept the copy tool, the desk transport and the queue controller into tier 2, and four coupled PRs then cost more than ten review rounds between them |
| 2 | **Kits are data.** A new kit on an admitted runner pin is tier 0: `validate-kit`, a mock span in CI, merge. It gets a cold seat only when it is a new leg type (RLD:12720) | RL-172 (i) row 1 already ruled "one runner pin per phase with kits as data" (RLD:17327). READY work is the binding limit (RLD:17068); this is what makes READY work cheap |
| 3 | **One accept, not two.** The lead is the integration owner unless the PR body names someone else. "Integration owner accepts, then lead accepts" (PIPELINE.md:14) becomes one line | Fewer hand-offs |
| 4 | **A finding must point at the spec or a reproduction.** A reviewer's finding is admissible only if it cites a failing acceptance scenario from the frozen spec or comes with a reproduction. Everything else goes to a backlog file and drives no work | PIPELINE §2 labels findings after the fact; this stops round n+1 from being generated by taste |
| 5 | **Retire the older review rules by name:** paired Sol and Opus builds with an agreement report for every block or window design (RS:12916, item 220; RS:12914); "every step gets two Sol xhigh seats" (lead note `main-goal-v4-squeeze`); the research lead's cold review of everything (lead note `fable-research-lead`). The independent recompute of claim numbers stays (PIPELINE.md:20-22) | These were never withdrawn and contradict the tiers |
| 6 | **One tier system.** The required gate-ledger check reads PIPELINE's tier line. Tier 0 needs CI. Tier 1 needs CI and one review row. Tier 2 needs the full ledger. The older `Tier: full` or `light` rule (`docs/orchestration.md:247-268`, the PR template, `scripts/check_gate_ledger.py:192-199`) is deleted in the same PR, with "No fixed round caps" (`docs/orchestration.md:95-101`) | Two tier systems are live on main and the required check enforces the older one, under which "any change to code or configs is FULL-TIER". PRs opened on 11-17 carry both forms |
| 7 | **The seat that raised a finding reviews its fix.** One fresh seat reads the whole change once, at the end of a tier 2 review. No fresh seat per round | On #800 each fix round went to a new cold reader, and the last four gates found 1, 1, 3 and 2 HIGH: different findings each time, never fewer |
| 8 | **Enforce the freeze.** A ruling that lands while a PR is in review goes into the next spec version (PIPELINE.md:40). Rulings for a phase are asked for as one batch before its build starts | RL-173 to RL-177 each entered open PRs mid-review; nothing merged for 60.5 h |

The resulting path:

| Tier | What | Steps | Hand-offs |
|---|---|---|---|
| 0 | Docs, records, queue and register data, kits on an admitted pin, tests, small fixes | build, CI, builder merges | 0 |
| 1 | Normal code, including the scheduler in read-only form, the close script and the copy tool | build, CI, one cross-family review, lead merges | 1 |
| 2 | The four cases in change 1 | one-page spec with acceptance scenarios as failing tests, freeze, build, CI, review of at most 3 rounds, lead merges | 2 |

A change that needs a research-lead ruling gets it at the spec stage, once. A ruling that lands during the build goes into the next spec version (PIPELINE.md:40).

---

## (d) What RUN_STATE becomes

| Today | Replacement |
|---|---|
| The law: standing items and rule lists | `RULES.json`. The magistrate prompt stops pointing at RUN_STATE for instructions |
| The program: "Start and check", "Run" and "Check" shell blocks | `mbp_sched.py`, `mbp_close.py` and the pinned launchers. `run_state_add.py` refuses a body that contains a fenced shell block |
| The work list: issued items | `QUEUE.json` |
| The pointer | `CURRENT.json`, generated as now |
| The history | `RUN_STATE.md`: typed items only, written by `run_state_add.py`, each a few lines |

Three kinds of typed item remain:

1. **Event** (generated by the tick and the close script): launch, close, refusal, halt, clear. One line of facts plus the item block.
2. **Decision** (lead, interim lead or research lead): what was decided and why, and the register rows or queue entries the same commit changes. A decision that changes neither is a note.
3. **Incident**: a fault and what was done.

`run_state_add.py` gets a body limit of 40 lines for events and decisions. The legacy region (everything below the typed cutover, about 20,000 lines) moves unchanged to `docs/archive/RUN_STATE-legacy-2026-11-17.md` in one tier-0 PR. Git keeps every byte; the magistrate stops loading it.

The lead's own work list (lanes, PRs, what is owed to Fable) does not belong in RUN_STATE. On 11-17 eight items (384, 390, 391, 402, 403, 404, 408, 409) recorded the Air being paused and resumed and handed lead work back and forth. With the MBP self-sufficient, the Air's state changes nothing on the MBP, and the lead's lanes go in `TASK_QUEUE.md` as they did before.

---

## What this structure does not change

- Anything inside a leg, a soak, a gate or a pinned runner. No frozen byte moves because of this audit.
- Blinding. The scheduler and the close script read receipt structure, never an energy, power or meter value.
- The registered arming route of v4 sessions, including Ed's notice and veto.
- The research lead's authority over anything paper-bound. The questions that touch it are one batch in `CUT.md` section 3.
- The language. The control plane stays stdlib Python; `MIGRATION.md` section 6 gives the evidence against a rewrite.
