# DIFF-1: two changes queued for DIFFICULTY's next registration revision (2026-10-22)

Item DIFF-1 of the forward-work workflow (interactive session 2dc9c377). Ed asked on 2026-10-21 that the MagSafe
problem be remedied: "also iirc, there was a problem when the workload exceeded the consumption the magsafe power
supply is providing and you operate off battery, make sure that's remidied, if it was indeed even a problem".
DIFFICULTY's `wall` line has the gap BYTES had. A second DIFFICULTY change, the idle-power leak, was queued on
2026-10-20 with no lane carrying it.

Seat: Opus 5.5, local. Nothing blinded was read: the numbers are from rulings and from the non-claim BYTES check
session H (`bytes-h-20261021T185555335572Z`, root `/Users/edr/night-bytes/h-20261021T185555Z`), whose export was
written with blinding not applied.

**Status: queued, not applied.** This file does not edit the registration. DIFFICULTY stays December-January
(RUN_STATE item 53). When that lane resumes, both changes go into one revision (2.4) of
`docs/registrations/difficulty_pack_v2.md`, which takes its own cold gate before any DIFFICULTY energy exists. Line
numbers below are for that file at origin/main `bfab7c950`, re-checked on 2026-10-22. The file last changed at
`fe6d61b4f` (revision 2.3), so the lines are the same at `4d49364ca`, where this record was first written.

| Change | Clause | Governing source | Expected size on DIFFICULTY's models |
|---|---|---|---|
| 1. `wall` adds the battery term | §2, line 53 (and the adapter paragraph, line 55; §12) | `BAT-RULING.md` §6 (Q5) | 0 J per attempt on H for all three models at the registered weights. H read 0 J on every dense model up to 32B. The three models' largest 20 ms meter samples were 14.8 to 23.1 W below the adapter's ceiling of about 135 W, where H's assists came |
| 2. No idle quantity visible before release | §9 "Blinding", line 384 (and §12) | 4b350f47 record | 0 J moved. It closes a path that reads the hidden configuration factor to about 0.007 in ln (meter idle), against the factor's own spread of 0.025 |

## Change 1: the battery term in `wall`

**Clause (§2, line 53, current text):** "`wall`: the whole machine, from a USB-C power meter on the laptop's charging
cable. It is printed beside rails as a labelled line. When the laptop draws more than the charger supplies, the
battery covers the gap and this meter misses it; such runs carry the flag `battery_assist` (recorded, not
excluding)."

Lines that stay as they are: 214 (flag table: `battery_assist` is used and counted), 329 (`wall` is not in the
decision family) and 371 (`wall` is printed as a labelled line).

**Governing source.** `docs/process_traces/2026-10-22-forward/BAT-RULING.md` §6 (Q5), on
`lane/2026-10-22-battery-assist-audit` (draft PR #536, not yet on main). §6 was ruled at `e6595ae13`. It is
unchanged at `fc7548a17`, which adds the lead's executed re-run of the worked example, and at the branch head
`367a0fa6d`, which changes only BAT-1's record (checked by diff). That ruling came from two blind seats (Opus 5.5
and Sol 6.1 xhigh) and a cold Fable 5.1 judge, and all three agreed that DIFFICULTY's `wall` takes the correction.
The evidence is `BAT-1-BATTERY-ASSIST.md` on the same branch (first at `7e59b54ab`), in its "Boundary by boundary"
table, DIFFICULTY row. At `367a0fa6d` that row reads "Ruled, queued, not built" and points to this file at
`c400061a3`. The ruling's terms:

- `wall` energy is the meter energy plus E_b over the whole request, gross and signed.
- It uses block 5's request-level rule: the two terms of `km003c_parse.delta_machine_energy`, without its baseline
  subtraction, because DIFFICULTY's energy is gross.
- The adapter writes the meter joules and the battery joules separately.
- `battery_assist` stays recorded, request-scoped and non-excluding.
- No edge term is added.

**Proposed text, replacing line 53** (the ruling's §6 bullet, unchanged):

> - `wall`: the whole machine: the energy on the laptop's USB-C charging cable from a USB-C power meter, plus the
>   energy the battery supplied over the same request, read from the battery current and voltage that the laptop
>   reports with each meter reading (charging counts negative). It is printed beside rails as a labelled line, with
>   the battery's share as its own column. Runs where the battery helped carry the flag `battery_assist` (recorded,
>   not excluding).

**Proposed text, appended to the adapter paragraph (line 55):**

> On `wall` rows, `energy_j` is the meter's energy plus the battery term over the request. At each meter poll the
> battery's power into the machine is P_b = −B0AC × B0AV / 10⁶ W (B0AC is the battery current in mA, negative while
> the battery discharges; B0AV is its voltage in mV). Over a request of length T that holds n polls, the term is
> (T / n) × Σ P_b. This is block 5's request-level rule (`km003c_parse.delta_machine_energy`, without its baseline
> subtraction). The adapter also writes each `wall` row's meter joules and battery joules to a side table,
> `wall_battery.csv` (columns `model, mode, level, item_id, attempt, meter_j, battery_j`), multiplied by the same
> blinding factors as `energy_j`. `energy.csv` keeps its ten columns. The battery column printed beside each `wall`
> line covers each configuration and level: the sum of `battery_j` over the `wall` rows that line uses, divided by
> the sum of their `energy_j`, then the largest `battery_j` and the count of rows whose `battery_j` is not 0. If a
> request holds no poll with both readings, its `wall` row is written with the meter's energy alone and the flag
> `battery_unmeasured` (recorded, not excluding).

**Proposed §12 item 11:** "`wall` adds the battery term over the request, gross and signed. The meter and battery
parts go to a side table, and a missing battery reading is a recorded flag (BAT-2 ruling §6; DIFF-1)."

**Decisions I made beyond the ruling** (the ruling's text did not settle these; the cold gate should check them):

1. **A side table, not new `energy.csv` columns.** The ruling says the adapter writes the meter and battery joules
   "as their own columns". The registered twin refuses any `energy.csv` header other than the ten registered
   columns: `read_table` in `scripts/difficulty_twin.py` at `fc4078667`, line 178 (file SHA-256 `4ec1b833…`, as
   registered). I ran it on a file with an eleventh column, `battery_j`. It raised "expected columns
   model,mode,level,item_id,boundary,attempt,energy_j,prompt_tokens,generated_tokens,flags", and it accepted the
   ten-column file. Adding columns would therefore change registered code. With the side table, no registered hash
   changes. The battery column is computed from the side table, outside the six registered tables of §8.1.
2. **A missing battery reading is a flag, not a removal.** BYTES removes such a run from its DC-input cells (BAT-2
   ruling §2). For DIFFICULTY I kept block 5's existing behaviour: `delta_machine_energy` returns the meter term
   alone with `battery_term_available: false` (origin/main `joulewise/external/km003c_parse.py` line 397). The flag
   falls under the "any other adapter flag" row of line 214, so the flag table needs no edit. On record this
   affects 0 runs: 0 of H's 95 runs, and no `battery.smc_unavailable` flag in the nine block-6 sessions (BAT-1). On
   H, DIFFICULTY's three models had a battery term of 0 J.
3. **A known limit, not a proposal.** The laptop publishes battery readings up to τ late, and τ was 2.302 s on H
   (BAT-2 ruling §3). So battery energy in the last τ of a request can be reported after the request ends, and the
   request-span rule misses it. The ruling adds no edge term for `wall`, because DIFFICULTY's intervals are
   bootstrap intervals over attempts. On H, DIFFICULTY's models had no negative reading to miss.

**Expected size on DIFFICULTY's models.** H ran all three models at the revisions this registration fixes:
`Qwen3-1.7B-4bit` `3b1b1768…`, `Qwen3-4B-4bit` `4dcb3d10…` and `Qwen3-8B-4bit` `545dc425…` (from H's run
configs). Each model had 5 full-length runs, each with a 2,048-token prompt and 512 decoded tokens.

| H, per model | Qwen3-1.7B | Qwen3-4B | Qwen3-8B |
|---|---|---|---|
| Battery term per request, 0.2 s stream path / 1 s monitor path | 0.000 / 0.000 J (5 runs) | 0.000 / 0.000 J | 0.000 / 0.000 J |
| Negative battery reads in the stage (1 s path) | 0 of 694 | 0 of 706 | 0 of 741 |
| Largest 20 ms meter sample, member spans | 111.9 W | 114.9 W | 120.2 W |
| Peak SMC DC input in the stage (1 s readings; hides short peaks) | 89.7 W | 106.2 W | 109.0 W |
| Meter power over decode | 75.7 to 76.1 W | 84.7 to 85.0 W | 92.2 to 93.7 W |
| Rails power over decode | 25.7 to 26.0 W | 28.8 to 29.0 W | 31.1 to 31.8 W |

A member span runs from the member's preparation to its post-request sentinel, so it includes the warm-up generation
before each measured run.

What these numbers say:

- **What predicts a discharge.** BAT-1's third dispatch (`367a0fa6d`, `out/peaks_by_model.txt`) found that the
  battery helps when the meter's 20 ms samples reach the adapter's ceiling of about 135 W. Every H run with a sample
  at or above 135 W drew on the battery: 18 of 20 70B runs and 7 of 9 122B runs. The rest of those runs are the
  short test-7 runs. One run below 135 W drew on it: a Qwen3-Next-80B run took 0.14 J, with a largest sample of
  128.8 W. The SMC's DC input is read once a second and hides these short peaks: it read at most 130.8 W in the 70B
  stages. Its row in the table is kept for reference and does not predict assist. This replaces the second dispatch's
  argument from SMC stage peaks (8B's 109.0 W against 108.7 W).
- **Dense models up to 32B took nothing.** Largest 20 ms sample in the member spans, 5 runs each: Qwen3-1.7B
  111.9 W, Qwen3-4B 114.9 W, Qwen3-8B 120.2 W, Qwen3-14B 127.2 W, Qwen3-8B-8bit 127.6 W and Qwen3-32B 134.8 W. All 30
  runs took 0 J, warm-up included, and none had a sample at or above 135 W. The mixture-of-experts Qwen3-30B-A3B also
  took 0 J (largest sample 131.2 W). DIFFICULTY's three models peaked 14.8 to 23.1 W below 135 W, and 8.6 to 16.9 W
  below the lowest peak with any assist (128.8 W).
- **DIFFICULTY's prompts are shorter.** H's 70B and 122B assists began in prefill (BAT-1; BAT-2 ruling §4).
  DIFFICULTY's prompts are 33 to 454 tokens in the pilot, against H's 2,048. A shorter prompt shortens the time
  spent at prefill power but should not raise the peak. Decode is DIFFICULTY's long phase: in the pilot, the median
  answer was 457 to 474 generated tokens with thinking off (100 answers per model; each problem's run at the highest
  cap it was given) and 2,916 to 2,959 with thinking on for 4B and 8B, with caps of 4,096 and 16,384. On H, mean
  decode power at the meter was 41 to 59 W below 135 W.
- **What H did not cover.** H's decodes held at most 2,560 tokens of context (2,048 + 512). A thinking-on answer
  can run to 16,384, and decode power at that context was not measured.
- **Expected term: 0 J per attempt** for all four measured configurations and the optional 8B thinking-on.
- **Not a guarantee.** Three things could change this:
  - decode at thinking-on context lengths, as above;
  - a process running beside an attempt: the 2026-10-06 probe saw −5.3 A with 8B running beside a CPU burner (BAT-2
    ruling §6);
  - a change of model.

  Outside any model run, H's pre-calibration stage discharged 8.9 J, never below −20 mA (BAT-1). The term measures
  the battery instead of assuming 0 J, so `wall` stays right in each case.
- **Scale if a discharge did occur.** `wall` covers the whole request. Over that span, H's assists were 8.85 to
  27.05 J per run on 70B (18 runs, 0.099 to 0.295 % of the meter's request energy) and 0.80 to 1.43 J on 122B
  (7 runs, 0.060 to 0.106 %). These are 1 s path values from `h_battery_runs.csv`. On 122B almost all of it was drawn
  in prefill. BAT-1 reads the 0.56 to 1.15 J recorded in its decode stretch as prefill discharge reported up to τ
  late, because while writing tokens 122B drew about 80 W and never more than 92 W. Line 329 keeps `wall` out of the decision
  family, so no decision moves by it.

## Change 2: the idle-power leak

**Clause (§9, line 384, current text, last three sentences):** "The per-configuration factors can shift a blinded ln
ratio by up to ±0.06, so blinded verdicts cannot be read as results. The analysis runs on the blinded sessions as
they arrive; unblinding divides the factors out once. Accuracy and token counts are not energies and are not
blinded."

**Governing source.** `docs/process_traces/2026-10-20-magistrate-4b350f47/RECORD.md`, the BYTES blinding ruling
(lines 35 to 37: "Opus found a second leak: `idle_power_w` is scaled by the configuration factor, so its ratio to
the reference rows' idle power estimates the factor and removes it"). It queued the leak for every block-6 pack
whose question is a ratio between configurations, DIFFICULTY next (lines 53 to 55). The remedy named there: "the
exporter writes the idle-subtracted energy, blinded, and withholds raw per-run idle columns until release". The
record cites this to the Opus consult, JouleWise-data `claude/bytes-blinding-opus`,
`reports/bytes-blinding-consult/opus.md` §4. RUN_STATE item 54 records the same queue. The remedy is adapted here
because DIFFICULTY's energy is gross, not idle-subtracted (line 51).

**Why it leaks.**

- **What the blinding multiplies.** It multiplies every energy column by the pack factor times the configuration
  factor (line 384). In the code, `joulewise/b6/blinding.py` `_scale` multiplies columns ending `_j` or `_w` by f,
  and columns ending `_w2` by f² (`lane/2026-10-20-b6-blinding-group` at `0b6023dcc`).
- **What the exporter shows.** The block-6 exporter on that branch, `joulewise/b6/export_runs.py` (lines 24 to 26
  and 162 to 166), writes `idle_power_w`, `idle_variance_of_mean_w2`, `gross_energy_j`, `idle_subtracted_energy_j`
  and `energy_request_j` into the visible table.
- **Why that reveals the factor.** Idle power belongs to the machine, not to the loaded configuration. So the ratio
  of two configurations' mean blinded idle power is the ratio of their factors. DIFFICULTY's primary quantity is
  EPC 1.7B / EPC 4B. The pack factor cancels in that ratio, so the configuration factors are the only thing that
  blinds it.
- **Why withholding `idle_power_w` alone is not enough.** Gross minus idle-subtracted energy equals the blinded idle
  power times the request's duration, and durations are not blinded. On H's Qwen3 rows the two agree to within
  0.05 %.

**Proposed text, appended to line 384 after "unblinding divides the factors out once.":**

> Before release, no table outside the withheld store carries a per-run idle quantity on either boundary: not the
> idle baseline's mean power or its variance, not an idle-subtracted energy, and not the meter's idle power. The
> machine's idle power does not depend on which configuration is loaded, so its blinded value in two configurations
> would give the ratio of their factors. Gross minus idle-subtracted energy is the idle power times the request's
> duration, and durations are not blinded. These columns are written, already multiplied by the factors, to the
> withheld store and released with the factors. The energies visible before release are `energy_j` in `energy.csv`
> and `meter_j` and `battery_j` in the `wall` side table (section 2). On the non-claim session of 2026-10-21, the
> meter's idle power would have read the ratio of two configurations' factors to about 0.007 in ln at this pack's
> 190 thinking-off energy runs per configuration, against the factors' own spread of 0.025.

**Proposed §12 item 12:** "No per-run idle quantity is visible before release. The idle columns go to the
withheld store, because the machine's idle power reads the configuration factors (4b350f47 record; DIFF-1)."

**Expected size on DIFFICULTY's models.** The change moves no printed number (0 J). It changes only which columns
can be seen before release. How much the leak would reveal was measured on H, using the same three models with 5
runs each:

| H idle power, per run | Qwen3-1.7B | Qwen3-4B | Qwen3-8B |
|---|---|---|---|
| Meter (wall) idle, mean | 2.3615 W | 2.3762 W | 2.3969 W |
| Meter idle, per-run spread (CV) | 0.035 | 0.022 | 0.020 |
| Rails idle, mean | 0.0544 W | 0.0638 W | 0.0598 W |
| Rails idle, per-run spread (CV) | 0.41 | 0.44 | 0.26 |

Simulation (script below; 4,000 campaigns):

- **Method.** Each campaign draws the 1.7B and 4B configuration factors from U(0.97, 1.03). It resamples 190 runs
  per configuration from H's per-run idle powers. 190 is this pack's thinking-off energy runs per configuration:
  70 + 4 × 30. It multiplies each run by its factor and estimates ln(f_1.7B / f_4B) as the log ratio of the two mean
  blinded idle powers.
- **The hidden quantity.** ln(f_1.7B / f_4B) has a standard deviation of 0.0246 and a range of −0.059 to +0.058.
  This is the registration's ±0.06.
- **Meter idle.** The estimate's error has a standard deviation of 0.0027 and a mean of −0.0062, so its root mean
  square is 0.0068: about a quarter of the hidden spread. The −0.0062 is H's observed 1.7B-to-4B idle difference.
  That difference is within the noise of five runs per model, so whether idle power really differs between models
  at the 1 % level is unknown. A real difference of that size would still leave most of the factor readable.
- **Rails idle.** Noise alone gives an error standard deviation of 0.040, larger than the hidden spread. H's 5-run
  means for 1.7B and 4B also differ by 17 %, which is consistent with that noise. Rails idle reveals little at this pack's sizes.
- **So the current exporter leaks little.** It carries rails idle only, and the meter's idle stays in the harvest's
  `withheld/meter.json`.
- **The leak becomes large** if the `wall` adapter exports the meter's idle power, or both a gross and an
  idle-subtracted `wall` energy. The proposed text bars both on both boundaries, at no cost.
- **The pack factor too.** The absolute blinded meter idle, compared with H's 2.36 to 2.40 W, would also estimate
  the pack factor U(0.8, 1.25). How closely depends on how much idle power varies between sessions, which H alone
  does not show.

## For the lane when it resumes

- **No registered estimator hash changes.** `energy.csv` keeps its header, and the estimator and twin are
  unchanged. The changes are text, plus the behaviour of the unbuilt energy adapter and of the export.
- **What the adapter build carries.**
  - The battery term. It reuses the two `km003c_parse` functions that BYTES's term calls: `Stream.battery_watts` and
    `integrate`, on origin/main at lines 312 and 368.
  - The `wall_battery.csv` side table and the battery column.
  - The rule that idle columns go to the withheld store.
- **BYTES's term is built.** It is BAT-3, `lane/2026-10-22-bytes-battery-term` at `ddcbafc4d`, not merged. On H it
  gives the same battery term as BAT-1 in all 95 runs: the largest difference is 0.0 J
  (`forward-20261021/BAT-1/out/bat3_crosscheck.txt`). Both sides call the same two functions, so this confirms
  BAT-3's wiring, not the integration rule (BAT-1). BAT-3 integrates over BYTES's decode span and adds an edge term.
  The DIFFICULTY adapter integrates over the whole request and adds no edge term (ruling §6).
- **Tests.** Its synthetic worlds include a request with a battery burst of at least 1 J (the attribution limit, as
  BAT-2 ruling §12 sets for BYTES). This is claim-path code: an executing review and both cold passes.
- **Draft header for the revision:** "Revision 2.4 (date, still before any DIFFICULTY energy). `wall` adds the
  battery's energy over the request, because the meter on the charging cable misses what the battery supplies when
  the laptop draws more than its adapter delivers (BAT-2 ruling). No per-run idle quantity is visible before
  release, because the machine's idle power reads the configuration factors (4b350f47 record). No list, size,
  arithmetic or registered code hash changes."

## Reproduce

Inputs: H's root, and BAT-1's per-run battery table (`h_battery_runs.csv`, in
`/Users/edr/night-archive/forward-20261021/BAT-1/out/`; also on JouleWise-data `analysis/battery-assist-20261022`).
Run it as `/opt/homebrew/bin/python3.13 -I diff1_numbers.py /Users/edr/night-bytes/h-20261021T185555Z
/Users/edr/night-archive/forward-20261021/BAT-1/out`. It prints the per-run rows behind both tables and the
simulation lines quoted above. The stage counts and SMC peaks come from BAT-1's `out/batt_by_stage.txt`, and the
pilot's prompt lengths and answer lengths from `/Users/edr/night-archive/pilots/difficulty/results*.jsonl` (633
rows; prompt tokens 33 to 454; for answer lengths, each model, mode and problem keeps its row at the highest cap).

Second dispatch, 2026-10-22: the embedded script was re-run unchanged on the same inputs. Its output matches every
number in both tables and the simulation lines (exit 0). The stage table, the registration's line numbers, the
4b350f47 record's lines, the twin's `read_table` and the `km003c_parse` and `b6` code cited above were re-checked at
the anchors named. One correction came from the re-check: the pilot's thinking-off median answer length, first
written as about 500 to 600 tokens, is 457 to 474.

Third dispatch, 2026-10-22:

- **Anchors re-checked.** The BAT-2 ruling branch had moved to `367a0fa6d`, and `BAT-RULING.md` is unchanged there
  since `fc7548a17`. Main is still `bfab7c950`. The registration lines, the 4b350f47 record's lines and the
  `km003c_parse` lines cited here were re-checked at that commit.
- **First script below** (`diff1_numbers.py`). Re-run unchanged. Its output again matches both tables and the
  simulation lines (exit 0).
- **What changed and why.** BAT-1's third dispatch found that assist follows the meter's 20 ms peaks, not the SMC's
  1 s reading. So change 1's expected-size argument was rewritten around the 20 ms peaks, and the scale of a
  discharge is now given over the whole request, which is the span of `wall`.
- **20 ms peaks.** Rows come from BAT-1's `scripts/peaks_by_model.py`, re-run here with byte-identical output:
  `/opt/homebrew/bin/python3.13 -I /Users/edr/night-archive/forward-20261021/BAT-1/scripts/peaks_by_model.py
  /Users/edr/night-bytes/h-20261021T185555Z <km003c_parse.py from origin/main>
  /Users/edr/night-archive/forward-20261021/BAT-1/out/h_battery_runs.json`.
- **Request-span shares.** Computed by the second script below, with BAT-1's `out/` directory as its argument.
  Full-length runs are every run except test-7 r02 and r04. Its output:
  `llama-70b: 18 runs, 8.85 to 27.05 J, 0.099 to 0.295 %` and `qwen35-122b: 7 runs, 0.80 to 1.43 J, 0.060 to
  0.106 %`.

```python
import csv, json, math, random, re, statistics as st, sys
from pathlib import Path
H, OUT = Path(sys.argv[1]), Path(sys.argv[2])
MODELS = ("qwen3-1p7b", "qwen3-4b", "qwen3-8b")
def short(run_id):
    s = re.sub(r"-r\d+$", "", run_id.replace("bytes-mac-check-", ""))
    return re.sub(r"^(check|soak|test7)-", "", s)
export = {r["run_id"]: r for r in csv.DictReader(open(next((H / "export/bytes-mac-check").glob("*.runs.csv"))))}
meter = json.load(open(H / "archive/withheld/meter.json"))["members"]
battery = {r["run_id"]: r for r in csv.DictReader(open(OUT / "h_battery_runs.csv"))}
idle = {"meter": {m: [] for m in MODELS}, "rails": {m: [] for m in MODELS}}
for run_id, e in export.items():
    m = short(run_id)
    if m not in MODELS or e["status"] != "succeeded":
        continue
    b, w = battery[run_id], meter[run_id]["machine"]
    td = float(e["dur_decode_s"])
    print(f"{run_id}: battery request J {float(b['str_request_j']):.3f} (1 s path {float(b['mon_request_j']):.3f}), "
          f"meter decode W {float(b['meter_decode_j']) / td:.1f}, rails decode W {float(e['phase_decode_j']) / td:.1f}, "
          f"meter idle W {w['meter']['baseline_W']:.4f}, rails idle W {float(e['idle_power_w']):.4f}")
    idle["meter"][m].append(w["meter"]["baseline_W"]); idle["rails"][m].append(float(e["idle_power_w"]))
for boundary, by in idle.items():
    for m, v in by.items():
        print(f"{boundary} idle {m}: n {len(v)}, mean {st.fmean(v):.4f} W, per-run cv {st.stdev(v) / st.fmean(v):.3f}")
n, R, rng = 190, 4000, random.Random(20261022)
hidden = []
for boundary, by in idle.items():
    a, b, err = by["qwen3-1p7b"], by["qwen3-4b"], []
    for _ in range(R):
        fa, fb = rng.uniform(0.97, 1.03), rng.uniform(0.97, 1.03)
        est = math.log(st.fmean(rng.choice(a) for _ in range(n)) * fa / (st.fmean(rng.choice(b) for _ in range(n)) * fb))
        err.append(est - math.log(fa / fb))
        if boundary == "meter":
            hidden.append(math.log(fa / fb))
    print(f"{boundary} leak, n {n}: error mean {st.fmean(err):+.4f}, sd {st.stdev(err):.4f}, rms {math.sqrt(st.fmean(x * x for x in err)):.4f}")
print(f"hidden ln(f_1.7B / f_4B): sd {st.stdev(hidden):.4f}, range {min(hidden):+.4f} to {max(hidden):+.4f}")
```

```python
import csv, re, sys
rows = list(csv.DictReader(open(sys.argv[1] + "/h_battery_runs.csv")))
for m in ("llama-70b", "qwen35-122b"):
    full = [r for r in rows if r["model"] == m and not re.search(r"test7-.*-r0[24]$", r["run_id"])]
    j = [float(r["mon_request_j"]) for r in full]
    s = [float(r["mon_request_j"]) / float(r["meter_request_j"]) * 100 for r in full]
    print(f"{m}: {len(full)} runs, {min(j):.2f} to {max(j):.2f} J, {min(s):.3f} to {max(s):.3f} % of the meter's request energy")
```
