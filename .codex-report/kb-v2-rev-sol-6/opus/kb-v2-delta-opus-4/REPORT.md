claude-opus-5-5
VERDICT: ACCEPT_WITH_FIXES

# KB-V2 round 6 delta review (Opus, executing): known-bytes reading rule

**Scope and checkout**
- Delta: `6847502b8..840137268` (`840137268e2c6f49fa369329a27f92de6c56a3f3`) on mpmdw/JouleWise `codex/2026-10-28-kb-v2`, draft PR #593.
- Code checkout: `/tmp/jw`, detached at `840137268`, read-only. A worktree at `6847502b8` (`/tmp/jw5`) was used for before/after comparisons.
- Scripts are in this directory and take the checkout as their first argument. Logs are in `logs/`.

**Summary**
- Every round-5 repro from both reports passes at `840137268`. H1–H5, H7 and H8 are implemented as ruled.
- H4 holds exactly: 1,248 checks, 0 failures, and retained coefficients are bit-identical.
- My leaf walk ran 44,816 mutations on the round-6 code: **0 crashes, 0 lost calls**, and 463/463 CLI re-runs exit 0 with the same classes.
- The worked values are unchanged. The builder's fixture changes move no tested number beyond float noise (≤1.1e-19 J/GB).
- One regression remains, introduced by this round's H6:
  - a negative `battery_edge_j` now enters the DC/rest **bound** with its sign;
  - it shrinks the bound with every class RESOLVED;
  - large enough, it crashes the reader (finding 1).
- Two smaller residuals:
  - three overflow tracebacks from finite accepted inputs, which predate this round (finding 2);
  - overlapping native rails/GPU intervals are accepted and shrink the rails bound (finding 3).

## Findings

### 1. MAJOR (H6 regression): signed `battery_edge_j` shrinks the DC/rest bound with all classes RESOLVED, and crashes the reader once the bound turns negative

**Where**
- `scripts/bytes_stream_test.py:677`: `("battery_edge_j", ("signed_edges", 2), ("dc",))`. In round 5 this was `EDGES`, whose elements had to be non-negative.
- `:795`: `edge = sum(h["meter_edge_w"])*(h["r_max_s"]+.020)+sum(h["battery_edge_j"])+gaps["bound_j"]`. This is a **bound** term, so a negative v subtracts from the half-width.
- `:901` (`format_interval`): `math.log10` of a negative half-width raises `ValueError: math domain error`.

**Physics.** The rule's §3 table (`docs/registrations/bytes_known_bytes_reading_rule_DRAFT.md:300`) inherits reg. §7's v. `docs/registrations/bytes_pack_v1.md:241` defines `v_edge = (T/n) × Σ |P_b|`, which is non-negative by construction. H6 says "battery edge energy stays signed", and the builder implemented that literally. Under either reading, the reader must not let it shrink a bound:
- If v can be negative (the H6 reading), a charging battery gives realistic inputs that shrink the bound, then crash.
- If v ≥ 0 (the reg. §7 reading), a negative v is malformed and must be a reasoned missing prerequisite, as it was in round 5.

**Repro:** `python3.13 -B overflow_battery_edge.py /tmp/jw /tmp/kb6` (`logs/overflow_battery_edge.log`). It sets the same value on both edges of all eight calls. Baseline DC half-width is 0.002527.
```
battery_edge_all_-10.0 OK ... 'dc': ('RESOLVED', 0.0016350595917928672), 'rest': ('RESOLVED', 0.0015534418397890...)
battery_edge_all_-20.0 OK ... 'dc': ('RESOLVED', 0.0007430964498849271), 'rest': ('RESOLVED', 0.0006614786978811...)
battery_edge_all_-40.0 ValueError math domain error @ bytes_stream_test.py 901 places = 1-math.floor(math.log10(rounded))
battery_edge_rec0_-1e6 ValueError math domain error @ bytes_stream_test.py 901
```
- At `6847502b8`, the same inputs give `dc UNDETERMINED (records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing))` and never crash.
- −20 J per edge makes the DC half-width 3.4× smaller with no reason printed. One record at −1e6 loses all output.

**Walk evidence.** All 18 walk cases with a negative `battery_edge_j` shrink the DC and rest bounds (`logs/classify_shrunk.log`). The builder's generated test does not see this: its spec still lists `battery_edge_j` as `probe.EDGES` (`tests/test_bytes_stream_test.py`, the `specs` dict), and its `negative` mode covers only non-battery `power_w` and `energy_j.rails`.

**Fix (needs a lead ruling between the two readings):**
- Either restore the non-negative check on `battery_edge_j` (reg. §7, v = Σ|P_b|).
- Or keep it signed as a disclosure and enter `abs()` of each edge in the bound.
- Either way, a negative half-width must never reach `format_interval`.

### 2. MINOR (H1, pre-existing): three overflow paths on accepted finite inputs still raise; the whole record is lost

H1 caught overflow in `idle_statistics` but not in these three places:
- **`:750`** `trim_ns = round(max(0,h["tau_s"]-receipt["settle_s"])*1e9)`: with `tau_s = 1e300` this is `round(inf)` → `OverflowError`. The `try` at `:753` catches only `KeyError`, `TypeError` and `ValueError`.
- **`:518`** `meter_gap_bound`: `math.fsum` of two finite gap terms near 1e308 (`adapter_max_w = 1e308`, two 50-sample gaps) → `OverflowError: intermediate overflow in fsum`.
- **`:911`** `printed_record`: `anchor_shift_j = 1e308` in all eight calls makes the half-width `inf`, so `classify` gives a class with no `description`. `json_evidence` then turns `inf` into the string `'inf'`, and `printed_record` raises `KeyError: 'description'`.

**Repro:** `probes6.py /tmp/jw /tmp/kb6` (`logs/probes6.log`, real CLI), plus `overflow_battery_edge.py` (`logs/overflow_battery_edge.log`):
```
[tau_s_1e300_rec0] TRACEBACK rc!=0: OverflowError: cannot convert float infinity to integer
[gap_fsum_overflow_rec3] TRACEBACK rc!=0: OverflowError: intermediate overflow in fsum
[anchor_shift_1e308_all] TRACEBACK rc!=0: KeyError: 'description'
```
All three fail identically at `6847502b8`, so this is not a regression. They break "never a traceback" only for absurd magnitudes no integrator emits. Same severity as round-5 Opus 1 / Sol 2.

**Fix:**
- Add `OverflowError` to the per-call `except`.
- Wrap `meter_gap_bound`'s `fsum` like `idle_statistics`.
- Treat a non-finite half-width as UNDETERMINED with a reason before `printed_record`.

### 3. MINOR (H2 completeness): overlapping native rails/GPU intervals are accepted and shrink the rails bound, with no reason printed

**Where.** `input_value` "native" (`:204-217`) checks three things:
- per-row `start_ns < end_ns`;
- non-decreasing `start_ns`;
- zero stamps.

It does not check that a row starts at or after the previous row's end. powermetrics intervals are consecutive and disjoint. The rule text added this round says native rows "must respect their recorded time order" (`DRAFT.md:236-237`).

**Repro:** `probes6.py` (full size, real CLI):
```
[rails_row_overlap_prev_rec1] rc=0 ... 'rails': ('RESOLVED', 0.0005732413065690482) ... shrunk=['rails']   (baseline 0.0005732822806092617)
```
- The walk's 15 `long` cases on rails/GPU lists duplicate the last interval exactly. All 15 shrink a rails or GPU bound, with all classes RESOLVED.
- The effect is small (relative 1e-5 to 7e-5), but a malformed row produces a smaller bound.

**Fix:** in the native branch, require `row[i].start_ns >= row[i-1].end_ns` for rails/GPU. A violation becomes the existing `invalid time order` reason naming the row.

### 4. NIT (for the lead; follows H3/H6 as written)

- **Signs not covered by H6.** `energy_j.gpu` and `energy_j.meter` are physically non-negative but stay signed, because H6's list omits them.
  - A negative value makes GPU NOT RESOLVED, or DC "contrast not resolved".
  - No bound shrinks (`probes6.py`: `energy_gpu_neg_rec0`, `energy_meter_neg_rec0`).
- **Scan status checked only as a string.** `scan.status` must be present and a string, as H3 says, but its value is not checked.
  - `status = "knee not found"` with a valid `K` reads as knee found: all RESOLVED (`scan_status_knee_not_found_with_K`).
  - No printed number changes.

## Checks requested

| # | Check | Result |
|---|---|---|
| 1 | Round-5 repros at `840137268` | **All pass.** Sol `extra.py`: `reversed_idle` and `huge_integer` exit 0 with leaf reasons; `bad_scan_status` → UNDETERMINED (`scan.status missing or invalid`). Sol `partial.py`: lost C3 prints `gamma_c 0.028000195821126284 alpha 0.0013999906666666668 gamma_d 0.09471662736453161 delta 0.06671643154340534`, equal to the independent values. Opus `probes.py` on the non-negative fixture: every case exits 0, nothing shrinks except `battery_edge_negative` (finding 1). The script's last display line raises `KeyError: 'rails'` because the corrected call now has no rails row; that is the harness, not the reader. Opus `g2_lost_calls.py`: 48 cases, 0 mismatches. Opus H8 environmental test: now passes on this seat. |
| 2 | H1–H6 fault walk | See the H1–H6 detail below this table. |
| 3 | H4 | `h4_arms.py`, 5 loss modes × 8 positions, plus three double losses: **1,248 checks, 0 failures**. S lost prints `gamma_c` and `alpha`. C1 or C2 lost prints none. C3 lost prints all four. Rails-only or meter-only losses touch only their boundaries. Every printed coefficient is bit-identical to the no-loss value; `r`, `halfwidth` and `epsilon_flip*` are `not defined (…)`; the class is UNDETERMINED. |
| 4 | Fixture changes | See the fixture detail below this table. |
| 5 | Shrink flags | My walk on the non-negative base: 214 flags (`classify_shrunk.py`). 129 are changed collections (dropped native row, duplicate poll stamp, short list, gap list changed); 46 are valid zeros (`meter_edge_w`, `anchor_shift_j`, `r_max_s`, `settle_s`, `missing_samples`); 6 are record-deletion index artefacts. **Defects: 18 negative `battery_edge_j` (finding 1) and 15 duplicated rails/GPU intervals (finding 3).** The builder files both under "signed-measurement changes / changed collections"; I do not. Four "short rails list" cases print a numeric rest half-width under an UNDETERMINED class. That is because §3 does not propagate C3's bound, and the input is valid-but-insufficient, not malformed, so it is not a finding. |
| 6 | Numbers | Bars: 5.7e-6 J/GB at `tests/test_bytes_stream_test.py:500-505,526` and 4.5e-7 GB/s at `:982-984`. Both are the lead's, unchanged, with derivations beside them; no new bar. New assertions use exact equality only for bit-identity (H4 coefficients, unaffected arms) and `>=` for no-shrink. Worked values (`logs/e2e_nonneg_840.log`): **rails 0.06672 ± 0.00057, DC 0.1929 ± 0.0025, rest 0.1262 ± 0.0024 J/GB, share 0.3458 ± 0.0075**. Program minus independent ≤ 2.81e-6 J/GB, inside the 5.7e-6 bar. |
| 7 | Tests, repin, CI | `tests.test_bytes_stream_test` + `tests.test_bytes_mac_kit`: **50 tests OK** (1,919.6 s; generated walk 900 CLI faults). `tests.test_bytes_h_session`: **36 OK** (2,169.5 s). `tests.test_repin`: **37 OK**. `repin.py --check`: `PASS 16 pin families current`. `bytes_mac_kit.py --check`: `verified non-claim Mac kit`. **CI not read** (see Executed). |

**Check 2 detail: H1–H6 fault walk**
- `probes6.py` runs 58 real-CLI cases on full-size records from the real `stream()` with a fake array module.
- `leafwalk.py` (round-5 walk, unchanged) runs 44,816 in-process cases, including huge integers, ±inf, NaN, negative and zero on every numeric leaf. Result: **0 crashes, 0 lost calls**.
- **Order (H2):**
  - Reversed and zero-stamp rows in the rails, GPU, meter and battery idle lists (pre and post), and in `battery_samples`, are UNDETERMINED with the row named.
  - A receipt start before the idle end, or `idle_pre_end < idle_pre_start`, is UNDETERMINED with the pair named.
- **Scan status (H3):** null, 7, a list, or absent → reasoned. A legitimate refusal (`knee not found`, K null) keeps `knee not found`.
- **Signs (H6):** negative rails/GPU/meter `power_w` and negative `energy_j.rails` are reasoned. Battery power and the battery integral stay signed, and zero stays valid.
- **Disclosure (H5):**
  - `python`, `packages.numpy`, `kernel_library` and `telemetry_backend` set to null, 7 or `''` change no class and print `not recorded (…)`.
  - The rail set is kept when `telemetry_backend` is bad.
  - Physical leaves (OS, hardware unit, MLX, MLX-Metal, runtime version, rail set) still charge the classes §2 names.
- **Exceptions:** findings 1–3.

**Check 4 detail: fixture changes**
- The builder's own ReaderTests fixture was built in each tree (`fixture_cmp.py`) and the results compared:
  - every boundary's delta, half-width, alpha, gamma_c, gamma_d and r differ by ≤ **1.1e-19 J/GB** (relative 1.9e-16); GPU, DC and rest are bit-identical;
  - idle pre/post means and governed SE agree to float noise;
  - printed contrasts are identical;
  - the minimum rails power was −0.21 W before and is +0.020 W now.
- The meter +10 W / battery −10 W split predates this round.
- Thinning (6×9.6 s → 4×14.4 s) applies only to the generated walk. It makes lags 0, and a single dropped row now stays computable rather than "below three bandwidths", so a silent row drop would now hit the no-shrink assertion. That makes the walk stricter, not weaker.
- My own non-negative real-stream fixture (`r5repro/r3/e2e_nonneg.py`) matches `6847502b8` bit-for-bit on the same fixture. Against the original round-5 fixture it differs by ≤ 5.6e-17 J/GB.

## Executed

- `bash tools/cloud/seat_setup.sh /tmp/jw` → ok. Python 3.13, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`, `TMPDIR` per shard.
- Fixtures:
  - `r5repro/r3/run_with_clock.py /tmp/jw r5repro/r3/e2e.py /tmp/kb`. The original round-5 fixture now **refuses under H6** (negative idle rails/GPU/meter powers), as the builder reported.
  - `e2e_nonneg.py` on both trees (`/tmp/kb6`, `/tmp/kb6old`), plus the original fixture on `6847502b8` (`/tmp/kb5old`).
- Sol scripts `extra.py` and `partial.py` (root path edited to `/tmp/jw`) on Sol's `compact.json` (no negative non-battery powers).
- Opus scripts on `/tmp/kb6`: `probes.py`, `g2_lost_calls.py`, and `leafwalk.py --cli-every 97`.
- Mine: `probes6.py`, `overflow_battery_edge.py` (both trees), `h4_arms.py`, `fixture_cmp.py` (both trees), `classify_shrunk.py`.
- The four test modules, `repin.py --check` and `bytes_mac_kit.py --check`, each run once in full. The H8 test was also run alone: OK.
- **Not run or read:**
  - **PR #593 CI.** This session's GitHub access is scoped to mpmdw/JouleWise-data only, so I did not query mpmdw/JouleWise Actions. Every job's state is UNREAD here, not green. The four modules CI runs for this area pass locally (above).
  - Whole suite, MLX, Metal and hardware.

## Decisions I made

- **Severities:**
  - Finding 1 is MAJOR. It is a regression in this round, and it violates "never a malformed input turning into a smaller bound" or, under H6's own reading, "never a traceback". A realistic charging-battery magnitude (−20 J per edge) cuts the DC half-width 3.4× with a RESOLVED class. The choice between the two readings belongs to the lead, so I name both fixes rather than pick one.
  - Findings 2 and 3 are MINOR: no production writer emits the inputs, and finding 2 predates this round.
  - Finding 4 items are NITs: no bound shrinks and no printed number changes.
- **Fixture:** I repaired the round-5 negative-power fixture the way the builder did: sparse non-negative pulses (63/−1 per 64 rows, zero mean, same governed SE) for rails and GPU, and a +10 W meter / −10 W battery split that leaves DC unchanged. I verified it reproduces the worked values bit-for-bit across both trees.
- **Reading the walk:** I counted a shrink as a defect only where the mutated input is malformed by physics or rule (negative v under reg. §7, overlapping intervals). Valid zeros, dropped or duplicate polls and collection changes I did not count.
- **CI:** I did not work around the repository scope (same as round 5).
- **Branch:** I pushed to `claude/kb-v2-delta-opus-4` as requested, and also to this session's designated branch `claude/kb-v2-delta-opus-4-d3mpnx`.
