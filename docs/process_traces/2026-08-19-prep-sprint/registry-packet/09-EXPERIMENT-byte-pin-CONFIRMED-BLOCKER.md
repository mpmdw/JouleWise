# REGISTRY-SHA BYTE-PIN EXPERIMENT — executed disposition of OPEN-ITEM 2 / §4 BLOCKER

**Date:** 2026-08-19
**Convening item:** `docs/process_traces/2026-08-19-prep-sprint/registry-packet/07-council-brief.md` §4;
`08-open-items.md` OPEN-ITEM 2.
**Mandate discharged:** *"Refute or confirm it, executably. Build a scratch clone, write a v2
registry to the path, commit, and run freeze-verify / dry-run against a `_v3` pack. Report the
observed reason code."* (07-council-brief.md §4.1)

## VERDICT: **CONFIRMED-BLOCKER**

The packet's code reading is correct, and the executed behaviour is **worse than the packet
predicted in two respects**:

1. The byte-pin lives in the **frozen `plan_tree.json`**, not only in the freeze receipt — so the
   refusal fires at the *first* gate (`_valid_plan_attachment`), upstream of every receipt check.
2. **Re-minting the freeze receipt does not repair it.** `generate_freeze_receipt` is itself gated
   on the same plan-tree pin and refuses, so the "just re-mint freeze-0004" instinct is closed by
   execution, not merely by D-131 policy.

No supersession, grandfathering, or multi-registry acceptance path exists anywhere in the code.
The packet's cure candidate #2 ("new registry path") was tested and **also fails**.

---

## 1. Isolation and method

Fully isolated. **The real worktrees and checkouts were never written to.** All work happened in
three throwaway `git clone --local` copies under this directory. Ed's measurement checkout
`/Users/edr/JouleWise-measurement-20260818` was confirmed to exist and was **not touched**
(existence check only). Nothing is deleted; the clones remain for auditors.

| Clone | HEAD | Registry sha256 | Role |
|---|---|---|---|
| `repo-baseline/` | `2243137` (pristine) | `d248fdc5…39a2e5` | CLI baseline arm |
| `repo/` | `2f2574d` (= `2243137` + M1) | `cc27b280…c48eb5` | mutated arm |
| `repo-pathtest/` | `0d39915` (= `2243137` + M3) | `d248fdc5…39a2e5` at a **new path** | path-term arm |

Clones are real git repos (required: `committed_pack_tree_sha256` and `_registry_reference` both
read `git HEAD` blobs).

### Baseline facts reproduced (all three `_v3` packs)

`shasum -a 256 configs/arm_readiness/d117_row_registry_v1.json` =
`d248fdc521cb904b7ad8f1c4ecb834f7810a1d8f39697b462591f2feac39a2e5`

All three `_v3` packs pin **identical** `row_registry` objects in **both** `freeze-0003.json`
*and* `plan_tree.json`:

```json
{"path": "configs/arm_readiness/d117_row_registry_v1.json",
 "plan_profile": "ALPHA|BETA|GAMMA",
 "registry_id": "d117-row-registry-v1",
 "sha256": "d248fdc521cb904b7ad8f1c4ecb834f7810a1d8f39697b462591f2feac39a2e5"}
```

The packet's measured facts are confirmed verbatim.

---

## 2. Which verifiers consult `row_registry.sha256` (asked by the method, step 2/4)

`_registry_reference` (`arm_readiness.py:2764`) is the **sole** builder of the live reference. It
is called from **four independent entry points** — each lane consults it itself; there is no shared
cache or single choke point that could be patched once:

| # | Entry point | Line | Reached by |
|---|---|---|---|
| 1 | `generate_freeze_receipt` | `:5423` | `generate_arm_readiness.py freeze` (mint / **re-mint**) |
| 2 | `generate_dry_run_receipt` | `:5804` | `… dry-run` |
| 3 | `generate_arm_receipt` | `:6108` | `… arm` |
| 4 | `_derive_arm_semantics_for_verification` | `:6300` | `… verify` (via `_verify_arm_receipt` `:6559`) **and consumption** (via `_replay_consumed_arm` `:7158`) |

**The answer to "does the arm/dry-run lane consult the registry sha independently?" is YES** — and
so do freeze, verify, and consumption.

Consumption chain confirmed: `scripts/launch_window.py:231/235/257` → `_consume_launch_capability`
(`:7297` → `_verify_arm_receipt` `:7372`) and `verify_consumed_launch` (`:7179` →
`_replay_consumed_arm` `:7197`) → both land on `_derive_arm_semantics_for_verification`. The
standalone `consume` CLI subcommand is retired and redirects to `launch_window.py`
(`generate_arm_readiness.py:117-121`).

### The three equality gates (all whole-dict `!=`, all four keys compared)

```python
item["row_registry"] != expected      # :2798  _valid_plan_attachment   ← PLAN TREE (earliest)
receipt["row_registry"] != registry_reference   # :5181  _load_freeze_reference  ← FREEZE RECEIPT
receipt["row_registry"] != registry_reference   # :6303  _derive_arm_semantics…  ← ARM RECEIPT
```

Gate ordering inside `_load_freeze_reference` matters and was verified: the **registry** check
(`:5181`) precedes the **pack-identity** check (`:5186`).

---

## 3. Confound found and neutralized (methodological note — read this before trusting arm 1)

The first baseline run **refused**, at `readiness_freeze_receipt_mismatch`, *before* any mutation.
Cause: `_pack_identity` (`:3702-3717`) includes `"pack_root": str(pack_root.resolve())` — an
**absolute path**. The frozen `_v3` receipts pin:

```
"pack_root": "/Users/edr/JouleWise-measurement-20260818/configs/campaigns/d117_floor_qwen25_1p5b_v3"
```

So the `_v3` packs authenticate **only** at Ed's measurement checkout; in *any* other checkout
(including `wtS0` and `main`) they already refuse on the location term. That is orthogonal to the
registry question but would have masked it.

**Control:** `probe.py --control` rewrites **only** the `pack_root` key of `_pack_identity`'s
return to the frozen value, leaving every other term — crucially `row_registry` — untouched. This
makes the registry byte-pin the single independent variable. Both controlled and uncontrolled arms
are reported below; they agree.

> *Incidental finding worth the council's attention:* the `_v3` family cannot be verified from the
> repository checkout at all, by design of the absolute-path identity term. Any future
> "verify the packs" instruction that does not run at
> `/Users/edr/JouleWise-measurement-20260818` will get `readiness_freeze_receipt_mismatch` and
> should not be misread as pack corruption.

---

## 4. Arm M1 — minimal, registry-**valid** byte change

**Design point:** the mutation had to keep the registry *loadable and valid*, otherwise a refusal
would prove only "invalid registries are rejected" rather than "the sha pin breaks the family".
`load_registry` (`:2508`) enforces `parse_json_bytes(raw, require_canonical=True)` and
`_require_exact_keys`, so formatting-only edits and added keys are both impossible under the v1
schema. `render_json` was verified to round-trip the live file byte-identically.

Chosen change — one row's `predicate_id` (only `_require_string`-validated, `:1880`):

```
rows[clock.correct_and_prior_state].predicate_id
  "clock.correct_and_prior_state.v1"  ->  "clock.correct_and_prior_state.v2"
```

Committed in the scratch clone as `2f2574d`. New sha
`cc27b28036a99dc7d4449f15bf136f91acf0d9ec122624acc2a693d305c48eb5`.

### In-process results (`probe.py`, all three `_v3` packs, identical outcomes)

| Probe | BASELINE + control | MUTATED + control | MUTATED plain |
|---|---|---|---|
| P1 `_registry_reference` | **OK** | **OK** | **OK** |
| P2 `_load_freeze_reference` | **OK** | **REFUSE** `readiness_row_registry_mismatch`<br>*"plan arm-readiness declaration differs from D-134"* | same |
| P3 `_derive_arm_semantics_for_verification` | passes the registry gate (refuses later only on the deliberately-null stub field) | **REFUSE** `readiness_row_registry_mismatch`<br>*"arm receipt registry binding differs from committed bytes"* | same |

**P1 stays OK in the mutated arm.** This is the decisive control: the registry still loads,
validates, and matches committed HEAD bytes. The refusal is caused by the **sha pin alone**, not by
schema invalidity. The baseline `P2 -> OK` establishes that the full freeze-reference path
(plan attachment, receipt registry binding, pack identity, predecessor authentication, profile
rows) is otherwise clean — the mutation is the only thing that breaks it.

### End-to-end CLI results (`cli_probe.sh`, pack `d117_floor_qwen25_1p5b_v3`)

**dry-run** — the registry refusal *appears* in the receipt's reason codes:

```
BASELINE  reason_codes: [readiness_freeze_receipt_mismatch,
                         readiness_ledger_preflight_refused,
                         readiness_reviewed_main_mismatch]        ← no registry code
MUTATED   reason_codes: [readiness_ledger_preflight_refused,
                         readiness_reviewed_main_mismatch,
                         readiness_row_registry_mismatch]         ← APPEARS
```
(dry-run collects rather than raises: `_registry_reference` is outside the `try` at `:5804`, while
`_load_freeze_reference` at `:5806` is inside it, so the mismatch is recorded as a refusal in the
issued dry-run receipt. `status: REFUSE`, `arm_disposition: NOT_APPLICABLE`.)

**arm** — hard refusal, reason code flips:

```
BASELINE  {"arm_disposition":"NO_GO","reason_codes":["readiness_freeze_receipt_mismatch"],
           "detail":"freeze receipt pack identity differs from committed pack bytes"}   ← location term
MUTATED   {"arm_disposition":"NO_GO","reason_codes":["readiness_row_registry_mismatch"],
           "detail":"plan arm-readiness declaration differs from D-134"}                ← EXACTLY the packet's prediction
```

The mutated refusal is the packet's predicted string verbatim, and it fires *earlier* than the
location term because the plan-attachment gate (`:2803`, via `:5161`) precedes pack identity.

---

## 5. Repair routes tested (method step 5)

### 5a. Re-mint the freeze receipt — **FAILS**

```
$ generate_arm_readiness.py freeze --pack-root <mutated>/…/d117_floor_qwen25_1p5b_v3
{"arm_disposition":"NOT_APPLICABLE","reason_codes":["readiness_row_registry_mismatch"],
 "detail":"plan arm-readiness declaration differs from D-134","status":"REFUSE"}
```
`git status` clean afterwards — freeze refused **before writing**.

Mechanism: `generate_freeze_receipt` calls `_valid_plan_attachment(readiness, registry_reference)`
at `:5426`, comparing the **frozen `plan_tree.json`**'s pinned `row_registry` to the live
reference. The plan tree is inside the byte-immutable pack. **Therefore the pin cannot be cured by
minting a new receipt** — the packet's "unrepairable by re-mint" is confirmed *by execution*, and
for a stronger reason than the packet gave (it is the plan tree, not the receipt, that closes the
door).

Regenerating the plan tree is equally closed: `plan_arm_readiness_attachment` (`:2846-2905`) builds
`row_registry` from live bytes (`:2900`), so a regenerated plan tree carries the new sha — which
changes `plan_tree_sha256`, `committed_pack_tree_sha256`, and hence `pack_identity`, invalidating
`freeze-0003` (and D-131 forbids rewriting issued bytes regardless).

### 5b. Does anything accept a superseding registry alongside the pinned one? — **NO**

- `ROW_REGISTRY_RELATIVE_PATH` (`:80`) is a single unconditional constant. Its only uses are
  `:2509`, `:2768`, `:2778`, `:2900` — no alternate, no list, no fallback.
- `load_registry` is called from exactly two sites (`:2766`, `:2848`), both reading that one path.
- `ROW_REGISTRY_REFERENCE_KEYS = {"registry_id","path","sha256","plan_profile"}` (`:319`) is
  enforced by `_require_exact_keys` (`:1350`). There is **no field** in which a superseding or
  prior registry could be recorded, and none could be added without a receipt-schema change.
- Grep for `supersed|grandfather|previous_registry|prior_registry|accepted_registr|registry_history|legacy_registry|allowed_registr` across `joulewise/` returns **no registry-supersession mechanism**. The `supersedes` hits are pack/identity-pin supersession, unrelated.
- `V1_GRANDFATHERING` (`:497`, used `:3186`, `:4226`) is a **refusal role that raises**
  (`"legacy generic evidence may not enter the R1 lifecycle"`) — the opposite of an acceptance
  path. It cannot be used as a cure.

### 5c. What does the freeze-receipt schema say about registry supersession? — **nothing**

`FREEZE_RECEIPT_V2_KEYS = (FREEZE_RECEIPT_KEYS - {"supersedes"}) | {"predecessor"}` (`:393`), and
`FREEZE_PREDECESSOR_KEYS` (`:382-392`) = `{pack_id, pack_path, pack_digest_algorithm, pack_sha256,
plan_id, plan_sha256, freeze_receipt, identity_receipt, evidence_set_sha256}`.

Verified against the live `_v3` receipt (`schema_version: joulewise.arm_readiness_freeze_receipt.v2`):
**no registry term in `predecessor`.** A successor pack structurally *cannot* record "my
predecessor was authored under registry X and I am under registry Y". The v2 chain binds packs,
not registries.

### 5d. Packet cure candidate #2, "new registry path" — **tested, FAILS** (arm M3)

Identical registry **bytes** (same sha `d248fdc5…`) committed at
`configs/arm_readiness/d117_row_registry_v2.json`, with `ROW_REGISTRY_RELATIVE_PATH` relocated:

```
frozen pin    : {"path": "…d117_row_registry_v1.json", …, "sha256": "d248fdc5…"}
live reference: {"path": "…d117_row_registry_v2.json", …, "sha256": "d248fdc5…"}
sha identical?: True
RESULT        : REFUSE readiness_row_registry_mismatch | plan arm-readiness declaration differs from D-134
```

Because the comparison is **whole-dict equality**, the `path` term breaks the family on its own even
when the bytes are untouched. The packet's suspicion ("probably worse, not better") is confirmed.
By the same equality, **`registry_id` also breaks it independently** — which directly constrains
OPEN-ITEM 6: under the v2 schema branch `registry_id` is unconstrained (`:1859-1861`), so any v2
registry that adopts a new id (e.g. the fixture's `test-r1-row-registry-v2`) breaks the `_v3`
family *even if* the sha problem were somehow solved.

---

## 6. What this means for the council's §1e disposition

Of the packet's four candidates:

| Candidate | Status after this experiment |
|---|---|
| **Defer the install** past the windows | **The only one still open.** `_v3` keeps arming via the existing route; the R1 lifecycle mechanism stays dormant for this campaign. |
| New registry path | **Executably refuted** (§5d). Fails on the `path` term with identical bytes. |
| A fourth `_v4` family minted after the install | Still technically available; unchanged enormous cost (new freeze cycle at the measurement checkout, new confirmation table). Note it must be minted *after* the registry lands, and the registry is then frozen for that family's life. |
| Code-level grandfathering of the registry reference | Requires a contract change on the authentication path. Nothing in the current code supports it (§5b/5c); it would be new schema surface, not a configuration choice. |

Additional constraint the experiment surfaces, not in the packet: **any** change to *any* of the
four reference keys — `sha256`, `path`, `registry_id`, `plan_profile` — breaks the family. The
install cannot be made safe by holding the sha stable; the whole reference object is pinned.

Under CLAUDE.local.md rule 11 this remains a contract-bearing, irreversible-adjacent call for the
**magistrate with a cold-instance pass**. This document supplies the executed evidence that §4.1
required; it does not rule.

---

## 7. Artifacts (retained for auditors — nothing deleted)

```
registry-experiment/
├── EXPERIMENT.md          this file
├── probe.py               in-process 4-path probe (--control neutralizes the location term)
├── cli_probe.sh           end-to-end dry-run + arm CLI probe
├── pathtest.py            arm M3, the new-registry-path cure test
├── baseline-inprocess.json   uncontrolled baseline (shows the location confound)
├── baseline-control.json     controlled baseline  — P1 OK, P2 OK
├── mutated-control.json      controlled mutated   — P2/P3 readiness_row_registry_mismatch
├── mutated-plain.json        uncontrolled mutated — same conclusion
├── cli-baseline.log          CLI baseline envelopes
├── cli-mutated.log           CLI mutated envelopes
├── m3-pathtest.log           path-term result
├── cli-scratch/              dry-run receipts written by the CLI probes
├── repo/                     scratch clone @ 2f2574d  (M1 mutation)
├── repo-baseline/            scratch clone @ 2243137  (pristine)
└── repo-pathtest/            scratch clone @ 0d39915  (M3 relocation)
```

### Containment verified after the run

- `/Users/edr/code/JouleWise` — clean but for the pre-existing `?? .decisive-replay/`;
  registry sha still `d248fdc5…`.
- `scratchpad/wtS0` — clean; advanced to `6240724` by *other* concurrent work (`2243137` is its
  parent), not by this experiment; registry sha still `d248fdc5…`.
- `/Users/edr/JouleWise-measurement-20260818` — registry sha still `d248fdc5…` (read-only check).
- Experiment commits `2f2574d` and `0d39915` are **absent** from the real repository object store
  (`git cat-file -e` fails in `/Users/edr/code/JouleWise`); they exist only inside the scratch
  clones.

Reproduce:

```bash
cd registry-experiment
python3 probe.py repo-baseline BASELINE-CONTROL control   # P1 OK, P2 OK
python3 probe.py repo          MUTATED-CONTROL  control   # P2/P3 readiness_row_registry_mismatch
./cli_probe.sh "$PWD/repo-baseline" BASELINE
./cli_probe.sh "$PWD/repo"          MUTATED
python3 pathtest.py repo-pathtest
```
