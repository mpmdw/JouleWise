# Seat: Mythos 5.2, #788 delta

Sat Nov 14 18:04:12 PST 2026 (`date`). Delta check of my own F3, F4, F6 and F8 and of RL-161's items, on both re-pins. I did not write the code or the kits.

## Verdict

| Kit | Pin | kit sha256 | Verdict |
|---|---|---|---|
| **v1.1** (class A) | `2d347f721` | `0f535774…e14b` | **ADMIT** |
| **v1.1a** (class B) | `1b20d3b0e` | `4bf7f294…d133` | **ADMIT** |

- **No finding needs a new pin or a kit text change.**
- **`thermal_gates.py` and `r1_runtime.py` are unchanged** from `b4b6aeb19` at both pins (RL-158 §2 line 2).
- **Two record items are owed by the lead before the arm:** D1 and D2 below. D3 to D6 are notes.
- **I could not run Python in this seat, again.** No test, mock, validator or `plan` was run by me. Every figure below is from reading the code at the pins, `shasum`, blob ids and hand arithmetic. The PR body's test counts are the builder's.

## Answers

**1. F3, F4, F6 and F8 are closed, and RL-161's five items are in.**

| Item | State |
|---|---|
| F3 (redo reference) | Closed. The receipt and each consumer's summary carry `span_reference` = first leg, supplying attempt, `redone`, `excluded`. The consumer's result carries the verified `record_sha256` |
| F4 (launch bounds) | Closed in code; see answer 3 |
| F6 (balance text) | Closed in both titles, both `bands_by_history` texts, the `kit_v11.py` docstring and design §14.2 |
| F8 (same span, desk role, seed, shared ids) | Closed. A consumer refuses a source outside `<this span>/legs/*/runtime`. The desk prints shape and role. The shared ids are stated in design §14.6 |
| Stop text (dev-01 F5) | In `stop_rules.notes` of both kits, with RL-149 §2.4's scope and who clears it |
| `admitted` column (dev-01 F8) | In `desk.py`, the same blob at both pins |
| Title reword | Done. Six span-shaped legs (L002, L004, L008, L009, L010, L012); 5 of 10 consume on 3 + 9. Both match the kit's leg list |
| Redo marking | Desk prints "MARK: reference from a redo" and "MARK: reference from an excluded leg". Both fire when the quota is spent |
| Seed | Unchanged: 2026111403, and the two drafts' leg seeds are equal |

**2. v1.1a is class B, and v1.1 is still class A with no gate-module edit.**
- **Same blob at `b4b6aeb19`, `1b20d3b0e` and `2d347f721`:** `cadence_leg_runtime.py`, `r1_runtime.py`, `thermal_gates.py`, `workload.py`, `align_r1_rehearsal.py`, `run_align_r1_smoke.py`.
- **`cadence_leg.py`** is the pilot's blob at `1b20d3b0e` (sha256 `c4dc0713…`, dev-01's hash). It changes only on the v1.1 line.
- **One precision on "every byte".** `legs.py`, `kit.py` and `desk.py` differ as files at `1b20d3b0e`, and the leg child imports them. Every name the leg calls is unchanged: `validate_leg_spec`, `guard_projection`, `LEG_KIND` and what they reach, including `PlanError`, `LeakRefusal` and `DENIED_KEY_RE`. The changed names are plan, arm, validate and print code.
- **The side line is `55a5670e8` plus class B changes only.** Its diff touches `desk.py`, `kit_v11.py`, `legs.py`, the runner, the launcher, `cadence_queue.py`, the design doc and tests.
- **The v1.1 smoke covers the new leg bytes.** L002 runs the same-span check and writes the record hash.

**3. The F4 bounds refuse what RL-155a §3, RL-157 §8 and RL-158 §3 rule, at both pins.**
- **What is refused:** a launch whose fence interval (t0, t0 + worst case + 1,460 s] meets 01:50 to 02:35, and any t0 strictly between 10:50 and 13:15. 10:50:00, 13:15:00 and a fence end at exactly 01:50:00 are legal, as the rulings write them.
- **Latest t0, by hand from the kit template** (3,150 s + (legs + 2) × 2,700 s):

| Legs | Worst + 1,460 s | Latest t0 |
|---|---|---|
| 3 | 18,110 s | 20:48:10 |
| 6 | 26,210 s | 18:33:10 |
| 9 | 34,310 s | 16:18:10 |
| 12 | 42,410 s | 14:03:10 |

- **Both kits share these values.** Their templates differ only in `leg_budget_s`.
- **Both bounds apply to these pins:** `ae340d3da` (#777's head) is not an ancestor of `2d347f721`.
- **No more:** a twelve-leg v1.1a span from 02:40 passes (fence end 14:26:50), as RL-158 §3 allows.
- **The flag is required** for a v1.1 kit in `plan`, `mock`, `run`, `launch` and `checklist`.
- **Three limits** are in D4.

**4. No fix changes dev-01, dev-02 or hp-01 on their own pins.**
- Neither diff touches `cl-dev-01.json`, `cl-dev-02.json` or `BLOCK-QUEUE.json` (same blobs at `17f478675` and `9cbb365a6`).
- The runner's preflight refuses any HEAD but the kit's frozen commit, so a v1 kit cannot run on the new bytes.
- `dd206025a` is on its own line (merge base `8bd31ae5a`) and is not touched.
- **One effect off the pins:** the Air desk is not pinned. See D1.

**5. The frozen hashes match their pins.**
- **Changed paths, by `shasum` at the pin:** six for v1.1 (`cadence_leg.py`, `desk.py`, `kit_v11.py`, `legs.py`, the runner, the launcher) and five for v1.1a (the same without `cadence_leg.py`). All match.
- **These are exactly the frozen paths that changed** between the old and new pins.
- **Every other path** keeps its hash line from the last drafts, which I checked at the old pins. The v1.1a kit's unchanged lines equal `cl-dev-01`'s.
- **The two drafts** differ only in title, pin, four hashes, `g0_shapes`, six `g0_shape` values, rule 2's text, `pilot_counted`, the budget sentence and `leg_budget_s`.

## Findings

**D1. The Air desk must run this line's `desk.py` for dev-03.** Medium, both kits; lead, no re-pin.
- Both pins now write four more keys into each `leg_summary.json` (`prefill_tokens`, `g0_shape`, `g0_role`, `span_reference`), under the same adapter name `leg-summary-v1`. This is new for v1.1a too.
- `desk._project` refuses unknown keys, and `scripts/air/cadence_desk.py` is not a frozen path. An Air checkout at `b4b6aeb19`, `main` or the hp-01 line refuses every dev-03 bundle and writes nothing, so the smoke would have no automatic table for the hand-read.
- The other way round, an Air desk on this line gives dev-01 and dev-02 tables the `admitted` column (summary and stops unchanged). For hp-01 it drops `restore_proven` and has no `block_mode` stop.
- Fix: each arm record names the Air desk's checkout. dev-03 uses either new pin (`desk.py` is one blob on both); hp-01 uses its own line.

**D2. Line 2 is not met for either pin yet, and a green run may not have run the identity tests.** Lead; carried from #788 F5.
- At about 17:55 the twelve `test` shards on head `9cbb365a6` were pending; `build`, `fences` and `quick` had passed.
- Head covers the v1.1 pin: it differs from `2d347f721` by the two kit files and three test lines.
- The side branch has no PR. I could not list its runs.
- On the side line the kit files are absent, so four tests skip, including the leg-byte identity test and the frozen-hash test. On the PR line they need `1b20d3b0e` in the clone, which is not an ancestor of the head; they skip without it.
- Fix: the lead records the run id and the skip count for each pin. If the identity tests skipped, one local run of `tests.cadence.test_kit_v11` with both commits fetched stands in.

**D3. The design doc contradicts itself.** Minor; builder at the next change. Not a frozen path.
- §14.5 still says `leg-summary-v1` is unchanged and the desk shows no cell column. §14.6 says the opposite.
- §6's input key list and §14.3's `span_window` row are stale in the same way.

**D4. What the code does not check.** Notes for the lead.
- **The flag's value.** Any `HH:MM-HH:MM` passes, so the arm record must show `02:00-02:35` (RL-150 F2).
- **`--deadline`.** The bound is on t0 + worst case + 1,460 s, not on the deadline the magistrate passes. The checklist's `span_window` line bounds the arm's `end_by`.
- **02:35:00 to 02:39:59.** Legal in code; the rulings' slots start at 02:40.
- **The `excluded` mark** is the runner's view (rules 1, 2, 5, 6). A first leg excluded at the look under rule 3 or 4 is not marked by the desk.
- **The same-span check** binds the directory, not "first leg". The runner always passes the first leg, and `g0_reference_source` names the actual source.

**D5. The checklist reads its soak window from `kit.OS_BATCH_WINDOW`; the launcher and `plan` read the driver's constant.** Minor; for the first pin on a #777 base.
- They are equal now (11:45-13:15).
- When #777 moves the driver's constant, the launcher's soak bound falls inside the fence bound, which is right. The checklist would still refuse 10:50 to 13:15, which RL-155a §3 then allows.

**D6. The v1.1a pin is on a side branch with no PR.** Minor; lead.
- Keep `align/2026-11-14-kit-v1-1a` (or tag the commit) until dev-03 is desk-final, or the pin cannot be fetched.
- The kit file is not on that line. It is taken from the PR head, as dev-01's was.

## Not done

- No test, mock, validator or `plan` was run.
- The F1, F2 and F7 rulings were read, not re-argued.
- Blinding held: no measurement, slot, transcript, energy, power, meter or powermetrics file was opened, nothing under `~/night-*` or `campaign-out`. No SSH. Nothing was written or edited.