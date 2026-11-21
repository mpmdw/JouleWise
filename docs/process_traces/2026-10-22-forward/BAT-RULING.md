# BAT-2 ruling: the battery term in BYTES' DC-input and rest boundaries (2026-10-21, 20:45 PDT)

Item BAT-2 of the forward-work workflow (interactive session 2dc9c377). It settles the science question that BAT-1
raised (`BAT-1-BATTERY-ASSIST.md` in this directory), for Ed's request of 2026-10-21: "also iirc, there was a problem
when the workload exceeded the consumption the magsafe power supply is providing and you operate off battery, make
sure that's remidied, if it was indeed even a problem".

Written by the Claude side (Opus 5.5, the item agent acting for the lead). Claim-path, because it defines a printed
boundary. BYTES is not registered and has no data, so its arithmetic may change now. Nothing here is blinded: every
number is from the non-claim BYTES check session H (`bytes-h-20261021T185555335572Z`).

Revision of 2026-10-22, 09:30 PDT (third dispatch of BAT-2; no council reconvened, no number changed). Every script
re-ran and reproduced byte for byte ("Executed evidence", third dispatch). Three additions by the lead's delegate:

- §8 now places the amendment of Addendum 1 item 2 in the registration text. The first text stated the amendment in
  §1 but gave no registration placement for it, and B6-1 (`b3b8f5b9d`, draft PR #537) proposes a meter-only fill
  for S-15.
- §4 and §8 state what the blinded stage prints for the decode marker. That is the build's choice (BAT-3 review
  finding 3), which this ruling had left open.
- §4 records what lies in the window after decode on H.

Revision of 2026-10-22, 14:40 PDT (fourth dispatch; no council reconvened, no number changed). Every script re-ran
and reproduced byte for byte. The build (BAT-3, `lane/2026-10-22-bytes-battery-term` @ `9bdcf6c95`) now agrees with
this ruling's formula on all 95 H runs, and §8's text is placed there in full ("Executed evidence", fourth dispatch).
Two build choices made since the third dispatch are recorded as this ruling's (§4): the marker is evaluated when the
meter value fails, and each run records whether its stream reaches τ after decode end. "Reopen if" gains one line.

## Who sat

- **Opus 5.5**, Claude cloud `session_016JB6H21N3PeACguhEyyh1L`. Report: JouleWise-data `claude/bat-council-opus`
  @ `baf7a8b`, `reports/bat-council-20261022/opus.md`.
- **Sol 6.1 xhigh.** The Codex Cloud task (thread `01a16179-72e9-72c3-b638-6244537b8027`; model and effort read back
  as gpt-6.1-sol and xhigh) stopped at once: "the workspace remains `starting` and offline". It was rerun on the Mac
  through codex-run-v3 (gpt-6.1-sol, xhigh; session `01a1618a-de9e-7f50-ad0c-d655236cbd29`), from a copy of the packet
  that held no other seat's files. Report: JouleWise-data `codex/bat-council-sol` @ `33cb503`,
  `reports/bat-council-20261022/sol.md`. The runner's SCOPE_VIOLATION covers only the scratch `tmp/` directory, which
  my preamble told the seat to use but left out of its write scope.
- **Cold judge, Fable 5.1**, Claude cloud `session_01NDo8JRpMryEMtapSQ5xStE`. The seats agreed on the verdict and
  disagreed on the bound, the marker and two smaller points, all of which move printed numbers. The judge saw both
  reports with the identities removed. Packet: JouleWise-data `analysis/bat-council-judge-20261022` @ `5dc0286`.
  Report: `claude/bat-council-judge-sv5af8` @ `8b5dd68`, `reports/bat-council-20261022/judge.md`. It ruled for the
  Opus seat on all four points (J1 to J4), and named three things the registration text must carry (adopted in §8).

Packet: JouleWise-data `analysis/bat-council-20261022` @ `cb272e3`. It holds the brief `PROMPT.md`, the governing texts
quoted verbatim in `texts/EXCERPTS.md`, the 2026-10-06 battery ruling, the BAT-1 record, and
`data/h_decode_extract.json`. The extract covers all 95 H runs: the decode, prefill, request and idle spans, every
0.2 s battery reading around the request, the meter samples at the decode edges, and the output of the real
`bytes_analysis.meter_decode` at `0743a7b90`, which is unchanged at the pass-1 head `5f89a9e00`. The ruling's own
scripts (`worked_example.py`, `ruling_table.py`, `lead/`) are on the same branch at `c17fdca` (§9, §11).

## The ruling in short

1. **DC input adds the battery.** Over each run's decode span, BYTES' DC input becomes the meter's energy plus the
   battery's signed energy, read from the battery current and voltage that ride on every 0.2 s meter poll. This is the
   rule block 5 already uses for its request-level whole-machine energy. Rest is the corrected DC input minus rails.
   Both the gross and the idle-subtracted bases get the term, and so do the NEG-8 reference energies that set the
   DC-input and rest drift allowance.
2. **The term carries its own edge term, v**, because the laptop publishes the battery reading late, by up to
   τ = 2.302 s on H. v joins the meter's edge term u in the bound B, in the meter attribution floor, in rest, and in
   NR1's coefficient alternative C_j.
3. **The without-assisted description line** keys on a decode-scoped marker, `bytes.decode_battery_assist`, which
   allows for that reporting delay. The harvest's request-scoped `battery.assist` is counted beside it and selects
   nothing.
4. **DIFFICULTY's `wall`** takes the same correction over the whole request. The DIFFICULTY lane writes this before
   any DIFFICULTY energy exists (DIFF-1).
5. **Addendum 1 item 2's last sentence does not decide any of this.** Both seats and the judge agree. The ruling
   amends that sentence so it can no longer import a meter-only battery treatment later.

Was it a problem? Yes, but a small one, and only for the whole-machine boundaries. On H, no 70B decode had battery
help except soak-r11 (0.40 J, a run the harvest already excludes). Every full-length Qwen3.5-122B decode read
0.56 to 1.15 J of battery energy, 0.063 to 0.129 % of its meter energy. All of it comes from polls received in the
first 1.93 s of decode: it is the prefill's discharge, reported late. The processor rails, which carry the claims,
never depended on the source of the power (2026-10-06 ruling; BAT-1's reopen tests).

## 0. A correction to the item brief

The brief said the 70B battery share is "about 55-60 J per run" and that the without-assisted line "would drop most
70B units". Both seats re-derived BAT-1's numbers from its tables (agreement 0 J, bar 1e-6 J):

- **Whole member, 70B:** 48.9 to 73.4 J on the 1 s path, with a mean of 58.7 J. Almost all of it falls in the warm-up
  run before measurement and in the 2,048-token prefill.
- **Decode, the span BYTES measures:** 0 J in 17 of 18 full-length 70B runs, and 0.396 J in soak-r11.
- **What drops 70B units:** the harvest's request-scoped flag, which counts the prefill. A decode-scoped marker keeps
  every 70B unit but r11's (§4).

## 1. Does Addendum 1 item 2 already decide Q1 and Q4? No

The clause reads: "If the block-5 whole-machine-per-phase definition is registered differently before the BYTES
registration, BYTES adopts that one." Its condition is not met:

- **Block 5** registers whole-machine energy only at request level. Its plan §8.2 reads "the harvest computes no
  phase-level figures". That registered definition is meter plus battery: ΔE_machine = meter + (−B0AC × B0AV) term.
- **Block 6** registration §9.5 item 5 (REGISTERED 2026-10-17) has a per-phase line that is meter-only, with the
  battery left at request level. But it defers "its exact definition" to the open slot S-15, "the one committed for
  block 5", and no such commit exists. Tonight's B6-1 draft (`301ea1474` §0 item 5) says so itself: "S-15 cannot be
  filled by pointing at a block-5 analysis commit". The draft's proposed fill is unruled.

Opus, Sol and the judge each read it this way. So the council ruled Q1 to Q5.

Block 6 gave two reasons for a meter-only per-phase line:

1. The battery is read once a second. That reason is real, and §3's edge term v carries it.
2. No reading falls inside 38 % of prefill phases. That reason does not hold for BYTES decode spans: every one of H's
   95 decode spans holds at least 4 polls, and the shortest full-length decode (1.7B, 2.32 s) holds 11.

**Amendment to Addendum 1 item 2** (this ruling): BYTES' DC input includes the battery term whatever S-15's fill
says. The clause's last sentence still governs the meter's own phase-edge and clock treatment. §8 places this
amendment in the registration's Authority paragraph and in §7 (added on the third dispatch). S-15 is still open on
main (`block6_replication_DRAFT.md` line 1037), and B6-1's third pass (`b3b8f5b9d` §7.1) keeps block 6's per-phase
value meter-only and says that BYTES no longer takes S-15's fill. Without the placement, the registration would still
list Addendum 1 as an authority with the old sentence in force.

## 2. Q1: the formula

Per run, over the decode span [d0, d1) of length T, on the host's raw monotonic clock:

- P_b = −B0AC [mA] × B0AV [mV] / 10⁶ W at every KM003C poll that carries both values. This is
  `km003c_parse.Stream.battery_watts`. P_b is positive while the battery discharges into the machine and negative while
  it charges.
- E_b = (T / n) × Σ P_b over the n polls whose receive time lies in [d0, d1). This is `km003c_parse.integrate`'s rule,
  which `delta_machine_energy` already applies to these polls for blocks 5 and 6.
- **Gross:** E_DC = E_meter + E_b. **Idle-subtracted:** E_DC,sec = E_meter,sec + E_b − P_b,idle × T, where P_b,idle
  is the same rule's mean over the run's own idle span. P_b,idle was 0 W in all 95 H runs, at 408 or more polls each.
- **Signed, not discharge-only.** Power that charges the battery passes through the meter but is not consumed by the
  machine, so clipping it would count battery storage as consumption. H had no charging reading at all. Charging above
  200 mA inside a run already excludes the run (`battery.member_span`). The flagged-inclusive line restores such runs,
  and there the signed term is the physically right one.
- **References.** The NEG-8 reference runs' DC-input and rest energies (whole request) use the same term over their
  request spans, so the drift allowance A_DC, A_rest and its scale are on the same boundary as the cells (Sol's point).
- **Printing.** Per run, the meter joules, the battery joules and their sum are recorded. Per cell, beside DC input
  and rest: the battery term's stratified mean and its largest value, the count of runs with a nonzero term, and the
  largest v. Meter-only is not printed as a separate estimate line, because it equals DC input minus the battery
  column. The boundary sentence printed with every DC-input and rest value reads: "whole-machine DC input plus the
  battery term, measured at the USB-C input; the adapter's AC-to-DC loss is not included" (block 5's wording).
- **No battery reading.** A run whose decode span or idle span holds no poll with both values gets no DC-input value
  (`bytes.meter_decode_unavailable`, reason "battery reading missing"). This is the existing rule for a missing clock
  fit (Addendum 3 item 10), so the run leaves the DC-input and rest cells only. Replay: 0 of H's 95 runs. In block 6,
  BAT-1 found complete SMC coverage (no `battery.smc_unavailable` in any of the nine sessions).

Executed on H (each seat, the judge, and me): see the per-run table in §9. Over the 25 full-length 70B and 122B runs,
four programs agree to 0 J with the real `km003c_parse.integrate` (bar 1e-6 J): Opus's, Sol's, the judge's and mine
(`lead/lead_table.py`).
The 0.2 s and 1 s read paths agree within their bar, 1 s × the span's largest battery power, in every comparison. The
largest share of the bar used was 0.57.

## 3. Q2: the edge term v, and how it joins u and C_j

**Forcing problem.** The meter is stamped on the host clock to within r_max = 17.8 ms. The battery reading is not: the
laptop's SMC (its system controller) publishes B0AC and B0AV about once a second, and each poll carries the latest
publication. So the battery joules near a phase edge can belong to the other side of the edge.

**The reporting delay, measured on H:**

- **Refresh.** Successive changes of the published (B0AC, B0AV) pair, over all 93,533 polls, have 1st, 25th and 50th
  percentiles of 0.991, 1.000 and 1.002 s. Over the 71 consecutive nonzero-to-nonzero changes the range is 0.993 to
  1.007 s (Sol). So T_SMC = 1.0 s, as the `km003c_parse` docstring states.
- **Poll interval:** median 0.200 s, largest 0.302 s.
- **Onset.** In the 33 discharges deeper than −200 mA, the first negative reading came 0.0 to 1.2 s (median 0.2 s)
  after the meter's 0.1 s mean reached within 3 W of its plateau (`lead/lag.py`; descriptive).
- **Tail.** After each of the seven full-length 122B prefill-to-decode power steps, discharge readings continue,
  counting the last negative reading's hold to the next poll, for 1.41, 2.13, 1.20, 1.79, 2.05, 1.87 and 1.84 s. One
  refresh (1.0 s) fails all 7. One refresh plus one poll (1.302 s) fails 6 of 7. Opus, Sol and I each reproduced these
  times.

A short onset and a long tail fit a reading that averages the second before it was published: it turns negative
within one refresh plus one poll, and stays negative until the averaged second has cleared.

**Rule (Opus seat; the judge's J1):**

- **Delay.** τ = 2 × T_SMC + Δt_p, where T_SMC = 1.0 s and Δt_p is the stream's own largest poll interval. Δt_p is
  read per stream, like r_max and the meter's Δt. On H, τ = 2 × 1.0 + 0.302 = 2.302 s.
- **Edge term.** Per run, v = v_start + v_end, where v_edge = (T / n) × Σ |P_b| over the polls received in
  [edge, edge + τ). T / n is the term's own weight per poll (0.196747 s on check-qwen35-122b-r01, not 0.2 s).

**Derivation.**

- A battery reading is an average over the second before it is published. The judge saw this in the tails: in 5 of
  the 7 122B runs, the last discharging value is 0.18 to 0.68 of the value before it. That is a partial average over a
  window that straddles the end of the discharge; for example, r05 reads −76 mA and then −14 mA.
- The reading stays the latest value until the next publication, at most T_SMC later.
- A poll sees it at most Δt_p after that.
- So energy that flows at time s is reported somewhere in (s, s + 2 × T_SMC + Δt_p], and never before s. H's largest
  observed tail, 2.130 s, is covered with 0.17 s to spare.

**Why v bounds the error.** Under that delay, the term can be wrong in only two ways:

- prefill energy reported in the first τ of decode, which the term counts with weight T / n (at most v_start);
- decode energy reported in the τ after decode, which the term misses (at most v_end).

So |E_b,true − E_b| ≤ v.

**How v joins the meter's terms.**

- **In B.** For DC input, B's phase-edge entry becomes the stratified mean of u + v. The meter attribution floor
  becomes the largest u + v over the kept runs. Rest carries the rails anchor-shift bound + u + v.
- **Both bases, no idle term.** v covers both bases, as u does (the `meter_decode` docstring: "The bound covers both
  bases"). No separate idle-span battery term is added, for three reasons:
  1. All 39,163 idle-span polls of the 95 H runs read B0AC = 0.
  2. The idle spans draw 2.3 to 3.3 W at the meter, and H reported discharge only in stages whose machine input
     reached at least 108.7 W.
  3. A nonzero idle reading would show in P_b,idle, which enters the value itself.
- **In C_j (NR1, registration §9).** Each run's term becomes max(P_start, P_end) × (r_max + Δt) + max(v_start, v_end).
  A delay shared by all models swaps one slice of energy in at the start edge and one out at the end edge. Both slices
  are at most their v, so the larger one bounds the error, which is the same structure as the meter's max(P). The
  sensitivity dβ/dδ stays meter-only: the polls carry host receive times, which the meter's label offset δ does not
  move.

**On H:**

- **122B:** v = 0.557 to 1.151 J. That equals the term itself in all 7 runs, because all of the battery energy lies in
  the first τ of decode. u = 5.85 to 6.43 J. The s6-shaped means over the 7 runs: u 6.190 J, v 0.824 J, u + v
  7.014 J; floor 7.384 J (u alone: 6.426 J).
- **70B:** v = 0 in all 18 runs. r11's discharge is in the middle of decode, 45.7 s in.

So, on H, the 122B battery term is compatible with zero within v. It is printed and counted, not rounded away: a term
below the ~1 J attribution limit is still a measured, one-signed quantity (Sol).

## 4. Q3: the without-assisted line

**Rule (Opus seat; the judge's J3).** A run is **decode-assisted** (`bytes.decode_battery_assist`, disclose only)
when a poll received in [d0 + τ, d1 + τ) reads B0AC < 0, with the same τ as §3. A reading received at time t
describes energy in [t − τ, t), so:

- readings in the first τ of decode can belong to the prefill;
- readings up to τ after decode can belong to the decode.

For every cell that holds a decode-assisted run, block 5's registered without-assisted line is printed beside it at
every boundary. It is the same estimator over the units with no decode-assisted run, labelled as description. Beside
it are printed, per stratum:

- the count of decode-assisted runs;
- the count of runs that carry the harvest's request-scoped `battery.assist`.

Below 5 units the line prints its counts and "below the registered minimum of 5 units". The line removes nothing from
the primary value.

**Counts on H** (full-length runs; "kept" means no EXCLUDE_MEMBER code; H has only repeats, so units = runs):

| Marker | 70B marked (of 18; kept of 13) | 122B marked (of 7; kept of 7) | Next-80B marked (of 7) | All 95 runs |
|---|---|---|---|---|
| Harvest `battery.assist` (whole request, prefill included) | 18 (13) | 7 (7) | 1 | 26 |
| Any negative reading held into [d0, d1) (Sol seat) | 1, r11 (0) | 7 (7) | 1 | 9 |
| **Ruled: a negative reading received in [d0 + τ, d1 + τ)** | **1, r11 (0)** | **0** | **0** | **1** |

**What each marker would do to the pass-1 sub-packs:**

- **s5 (70B).** The request flag would empty s5's line every time ("below the registered minimum"), which is the defect
  the item brief described. Under the ruled marker, no kept run is marked, so the line is not printed. The
  flagged-inclusive s5 line restores r11, and its companion line prints n = 13 on H.
- **s6 (122B).** Both the request flag and Sol's marker would mark all 7 runs, so the line could never be computed
  for 122B. Under the ruled marker, no 122B run is marked. Their decode-start readings are the prefill's discharge
  reported late:
  - the discharge begins 3.5 to 4.5 s into a 4.7 s prefill;
  - in the first 2 s of decode the meter reads 79 to 80 W, against 117 to 119 W in the prefill tail;
  - no report arrives more than 2.130 s after the prefill-to-decode power step.

  The battery column still prints those joules (mean 0.824 J), and v bounds them.

**Accepted cost.** An assist that really lies inside the first τ of decode goes unmarked. On H, Next-80B check-r03
(0.115 J) straddles a decode start that comes 2.02 s after its prefill start, and it is unmarked. Its energy is inside
the term and inside v.

**The window after decode** (added on the third dispatch; `gap_check.py`, Executed evidence). The marker and v_end
read polls up to τ after the decode end. On H that window holds nothing but the run's own quiet after its request:

- every request ends at its decode end (0.6 to 3.3 ms later);
- every idle baseline lies before its request;
- the next run's first span starts at least 45.0 s after the previous decode end (0 of 94 gaps below τ);
- all 1,102 polls received in [d1, d1 + τ) over the 95 runs read 0 mA.

A later schedule might start a run within τ of the previous decode end. Then that run's discharge would raise the
earlier run's v_end and could mark it. That makes the bound larger and the without-assisted line shorter. It cannot
move E_b, which counts only polls received in [d0, d1).

**Decodes no longer than τ.** Every full-length decode on H is longer than τ; the shortest is 1.7B's 2.324 s. The
22 NEG-8 reference decodes and six one-second `test7-*-start` runs of the 70B, Next-80B and 122B models last 0.99 to
1.01 s. The references take the term over their request spans (§2). For a decode no longer than τ, the marker's
window lies wholly after decode. A reading received there at time t describes energy in [t − τ, t), which is the
decode or the quiet after it and never the prefill. So the marker is still right when it fires. An assist reported
before d0 + τ goes unmarked, which is the accepted cost above.

**At the blinded stage** (added on the third dispatch; BAT-3 review finding 3, built at `552561b3f`). The marker is
read from the meter stream, and the blinded stage reads no meter stream. There, the count of decode-assisted runs
and the without-assisted line's numbers print as null, labelled "not evaluated at the blinded stage". Printing 0
would claim a count that was never taken. The count of runs carrying `battery.assist` comes from the harvest's
flags and prints at every stage. This changes no number. Every stage that reads the meter stream evaluates the
marker as above.

**When the meter value fails, or the window is cut short** (added on the fourth dispatch; BAT-3 fix round 1b,
`ac03d8cd0` and `3566073ae`). Two cases the text above left open. The build's choices are adopted:

- *The meter value fails* (for example `bytes.meter_decode_unavailable` for a missing clock fit). The run leaves the
  DC-input and rest cells, but it stays in the rails cells, and the without-assisted line is printed at every
  boundary. So the marker is still evaluated from the stream's polls in [d0 + τ, d1 + τ). If no stream mapped to the
  host clock has a poll in that window, the run records `decode_assist_evaluated` false with the cause. A cell that
  holds such a run prints the decode-assisted count and the line's numbers as null, with that cause and the run ids,
  never as 0. This is the blinded-stage rule above, for the same reason.
- *The stream ends before d1 + τ.* Then v_end and the marker read only the polls that exist, so v_end can be too
  small and a decode-end assist can go unmarked. Each run records `battery_end_window_complete` (true when a poll was
  received at or after d1 + τ). It is a recorded disclosure and removes nothing. On H it is true for 95 of 95 runs:
  the build says so, and the extract holds a poll at or after d1 + τ for every run.

## 5. Q4: rest

Yes. Rest = (E_meter + E_b) − E_rails per run, before any averaging, on both bases. Every battery joule is machine
energy, and the rails are measured independently of the supply, so the joules the meter misses belong to rest. On H's
122B runs that adds 0.56 to 1.15 J to a rest of about 577 J (0.10 to 0.20 %). Rest's phase-edge term in B becomes the
rails anchor-shift bound plus u plus v.

## 6. Q5: DIFFICULTY's `wall` line

Yes, as a revision of DIFFICULTY v2 §2 before any DIFFICULTY energy exists (DIFF-1 queues it for that lane).

- `wall` energy = meter energy + E_b over the whole request, gross and signed, with block 5's request-level rule
  (`delta_machine_energy`'s two terms without the baseline subtraction, since DIFFICULTY's energy is gross).
- The adapter writes the meter and battery joules as their own columns.
- `battery_assist` stays recorded, request-scoped and non-excluding.
- No edge term is added. DIFFICULTY registers no attribution bound for `wall`, since its intervals are bootstrap
  intervals over attempts. Its request also starts from a settled pre-request state.
- Expected size: on H, every full-length run of the models DIFFICULTY uses (Qwen3 1.7B, 4B and 8B), and of every
  model at or below 32B, read 0 J. That is a measurement, not a guarantee. The 2026-10-06 probe saw −5.3 A with 8B plus
  a CPU burner.
- Proposed §2 bullet text: "`wall`: the whole machine: the energy on the laptop's USB-C charging cable from a USB-C
  power meter, plus the energy the battery supplied over the same request, read from the battery current and voltage
  that the laptop reports with each meter reading (charging counts negative). It is printed beside rails as a
  labelled line, with the battery's share as its own column. Runs where the battery helped carry the flag
  `battery_assist` (recorded, not excluding)."

## 7. Flag codes

| Code | Class | When | H replay (95 runs) |
|---|---|---|---|
| `bytes.decode_battery_assist` | DISCLOSE, per run | §4's marker | 1 (soak-70b-r11) |
| `bytes.meter_decode_unavailable` (existing), reason "battery reading missing" | as today: the run leaves the DC-input and rest cells | no poll with both B0AC and B0AV in the decode or the idle span | 0 |
| `battery.assist` (harvest, existing) | DISCLOSE, counted beside the line; selects nothing in BYTES | unchanged | 26 |

## 8. Registration text (for `docs/registrations/bytes_pack_v1.md`)

Base text: `91b20d7c2`. The registration's editor places these and adds a §20 row "BAT-2 ruling → Authority, §1, §6,
§7, §9, §15, §16". Every term below is built before it is used.

Three placements were added on the third dispatch: the Authority insertion, the last paragraph of §6 and the
"Per-phase definitions registered elsewhere" paragraph of §7. BAT-3 placed this section's original text verbatim
on `lane/2026-10-22-bytes-battery-term` (`a846ba997`). These three are still to be placed there, and the §20 row
there gains "Authority".

**Authority paragraph, one insertion** (third dispatch). After "In order:", insert:

> the BAT-2 ruling (2026-10-21; `docs/process_traces/2026-10-22-forward/BAT-RULING.md`) on the battery term, its
> edge term v and the decode-assisted marker (§6, §7, §9), where it amends Addendum 1 item 2, Addendum 4 item 11 and
> Addendum 9's C_j; then

**§1, the DC-input bullet, replaced:**

> - **DC input**: the energy entering the whole machine. It is the power on its USB-C charging cable after the power
>   adapter, from a KM003C USB-C meter, plus the power the battery supplies when the machine draws more than the
>   adapter delivers (§7, "Battery term"). It is never called "wall" or "AC".

**§6, the "Battery assist" paragraph, replaced:**

> **Battery assist.** When the laptop draws more than its 140 W adapter delivers, the battery supplies the difference
> while the adapter stays connected. The meter on the adapter's cable does not see that energy, so DC input adds it
> back (§7, "Battery term"). Assist is disclosed, not excluded (R3; the battery-assist ruling of 2026-10-06), because
> removing assisted runs would select runs by load.
>
> The laptop reports its battery current up to a delay τ late (§7). So a run is **decode-assisted**
> (`bytes.decode_battery_assist`, disclose only) when a meter poll received between τ after its decode start and τ
> after its decode end reports a battery current below 0 mA. The rule is "τ after": a reading in the first τ of
> decode can describe the prefill, and a reading up to τ after decode can describe the decode.
>
> For every cell that holds a decode-assisted run, block 5's registered without-assisted line is printed beside it:
> the same estimator over the units with no decode-assisted run, labelled as description (Addendum 7 D10). Printed
> with it, per stratum, are the count of decode-assisted runs and the count of runs carrying the harvest's
> request-level `battery.assist`. Below 5 units the line prints its counts and "below the registered minimum of 5
> units".
>
> The marker is read from the meter stream, so only the stages that read that stream evaluate it. A stage that
> reads no meter stream (the blinded stage, §11) prints the count of decode-assisted runs and this line's numbers as
> null, labelled "not evaluated at the blinded stage", never as 0. The count of runs carrying `battery.assist`,
> which comes from the harvest's flags, is printed at every stage.
>
> *Expected, from the non-claim check session H (2026-10-21):*
> - Llama-3.3-70B: 1 decode-assisted run of 18 (0.40 J, a run the harvest excluded for an agent's presence).
> - Qwen3.5-122B: no decode-assisted run, but 0.56 to 1.15 J of battery energy in every full-length run, all of it
>   from meter polls received in the first 1.93 s of decode, and within its edge term v.
> - Every model at or below 32B: 0 J.

**§7, the bound table's "phase-edge timing" row:** the DC-input cell becomes "u + v, the meter and battery edge terms
below (Addendum 1 item 2; BAT-2 ruling)". The rest cell becomes "rails anchor-shift bound + u + v".

**§7, a new paragraph after "Meter edge term u":**

> **Battery term and its edge term v** (BAT-2 ruling).
>
> *The term.* Each meter poll, five a second, also carries the laptop's latest published battery current B0AC (mA,
> negative while the battery discharges) and battery voltage B0AV (mV). At a poll, the battery's power into the
> machine is P_b = −B0AC × B0AV / 10⁶ W. It is positive while the battery discharges and negative while it charges
> (`km003c_parse.Stream.battery_watts`). Over a span [start, end) of length T that holds n polls, the battery energy
> is E_b = (T / n) × Σ P_b over those polls. This is the mean-times-length rule that `km003c_parse.integrate`
> applies to the meter, and that blocks 5 and 6 apply to these polls (`delta_machine_energy`).
>
> DC-input energy over a span is the meter's energy plus E_b over the same span. The idle-subtracted basis subtracts
> the idle span's mean P_b × T, as it subtracts the meter's idle power. The NEG-8 reference runs' DC-input and rest
> energies, which set the drift allowance, include E_b over their request spans in the same way.
>
> *Why it needs an edge term.* The laptop's system controller publishes B0AC and B0AV once a second (T_SMC = 1.0 s;
> on H the median interval between changes of the published pair was 1.002 s). Each reading averages the second
> before its publication, and it stays current until the next publication. A poll then sees it up to one poll
> interval later. So battery energy is reported up to τ = 2 × T_SMC + Δt_p late, and never early. Δt_p is the
> stream's largest interval between polls (H: 0.302 s, so τ = 2.302 s). On H, after the prefill-to-decode power step
> of every Qwen3.5-122B run, discharge readings continued for 1.20 to 2.13 s.
>
> *The edge term.* Per run, v = v_start + v_end, where v_edge = (T / n) × Σ |P_b| over the polls received in
> [edge, edge + τ). At the start edge, v_start is all the battery energy the term counted that may be the prefill's.
> At the end edge, v_end is all the decode energy that may have been reported after the span.
>
> *Where it enters.* v is added to u in B (table above). The largest u + v over the kept runs is the cell's meter
> attribution floor. Beside DC input and rest are printed the battery term's stratified mean and largest value, the
> count of runs with a nonzero term, and the largest v.
>
> *Missing readings.* A run whose decode or idle span holds no poll with both readings has no DC-input value
> (`bytes.meter_decode_unavailable`, reason "battery reading missing").
>
> *Per-phase definitions registered elsewhere* (third dispatch). This amends the last sentence of Addendum 1 item 2.
> Block 5 or block 6 may later register a per-phase whole-machine energy (block-6 slot S-15). If one is registered
> before this registration, BYTES adopts its treatment of the meter's phase edges and clock, as that sentence says.
> BYTES' DC input and rest keep the battery term as defined here, whatever that definition says about the battery.

**§9, NR1's labelled alternative:** C_j's per-run term becomes max(P_start,i, P_end,i) × (r_max,i + Δt) +
max(v_start,i, v_end,i). The text adds one sentence: "The battery reading's delay is one-signed, like δ, so it also
moves every model's DC-input energy the same way; the edge with the larger v enters, as the edge with the larger meter
power does." The dβ/dδ disclosure is unchanged, because the polls carry host receive times.

**§15, printed list:** after "attribution floors", add "the battery term (stratified mean, largest, count of runs
with a nonzero term) and the largest v beside DC input and rest".

**§16, the harvest-dependency bullet:** replace "the harvest's `battery.assist` flag for battery assistance (item 11)"
with "for battery assistance in decode, the meter stream's own battery readings, the same readings that make the
battery term (§6, §7); the harvest's request-level `battery.assist` is counted only (BAT-2 ruling, which replaces
Addendum 4 item 11's dependency)".

## 9. Worked example (H, non-claim; `worked_example.py` on the packet branch)

**Per-run table under the ruled rule** (`ruling_table.py`; every run of H with a nonzero term or v, then the rest of
the full-length 70B runs; "marker" is `bytes.decode_battery_assist`; "harvest flag" is the request-scoped
`battery.assist`):

| run | T s | meter J | battery J | DC input J | DC idle-sub J | u J | v_start J | v_end J | u + v J | C_j term J | marker | harvest flag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| check-qwen3-next-80b-r03 | 7.14 | 437.902 | 0.115 | 438.017 | 421.360 | 4.528 | 0.115 | 0.000 | 4.642 | 2.413 | no | yes |
| check-qwen35-122b-r01 | 11.02 | 884.500 | 0.777 | 885.276 | 857.328 | 6.387 | 0.777 | 0.000 | 7.164 | 4.069 | no | yes |
| check-qwen35-122b-r02 | 10.99 | 890.241 | 0.958 | 891.199 | 863.373 | 6.426 | 0.958 | 0.000 | 7.384 | 4.242 | no | yes |
| check-qwen35-122b-r03 | 11.00 | 889.838 | 0.845 | 890.684 | 863.737 | 6.195 | 0.845 | 0.000 | 7.041 | 3.954 | no | yes |
| check-qwen35-122b-r04 | 10.98 | 890.983 | 0.782 | 891.765 | 864.314 | 6.297 | 0.782 | 0.000 | 7.079 | 3.945 | no | yes |
| check-qwen35-122b-r05 | 11.01 | 892.692 | 1.151 | 893.843 | 866.943 | 6.036 | 1.151 | 0.000 | 7.187 | 4.237 | no | yes |
| soak-llama-70b-r11 | 57.44 | 6423.531 | 0.396 | 6423.927 | 6261.634 | 8.547 | 0.000 | 0.000 | 8.547 | 4.489 | yes | yes |
| test7-qwen35-122b-start-r01 | 10.96 | 877.975 | 0.557 | 878.532 | 853.079 | 6.141 | 0.557 | 0.000 | 6.699 | 3.641 | no | yes |
| test7-qwen35-122b-start-r03 | 10.99 | 880.125 | 0.697 | 880.822 | 854.836 | 5.847 | 0.697 | 0.000 | 6.544 | 3.734 | no | yes |
| other 17 full-length 70B | 55.64 to 56.12 | 5995.367 to 6304.653 | 0 | = meter | 5831.293 to 6177.048 | 8.068 to 8.376 | 0 | 0 | = u | 4.203 to 4.307 | no | 17 of 17 |

The s6-shaped means over the 7 122B runs: meter 886.622 J, battery 0.824 J, DC input 887.446 J, u 6.190 J, v 0.824 J,
u + v 7.014 J. Over the 13 kept 70B runs: battery 0, mean u 8.255 J, floor 8.376 J (the judge's cell lines).

Run `worked_example.py` (§11). Rails decode energies are from H's export (`phase_decode_j`; blinding not applied).

**Llama-3.3-70B, check-r01.** The battery helped this run, but not in the span BYTES measures.

- **Where the battery helped:** in the warm-up run before the request (50.87 J on the 1 s path) and in prefill (8.00 J
  by the term's rule; 15 negative polls, lowest −426 mA). The last negative poll came 22.77 s before decode start.
  The harvest marks the run `battery.assist`, because that flag covers the whole request.
- **Decode span:** T = 56.018813 s, n = 280 polls, T / n = 0.200067 s. Every poll reads 0 mA, so Σ P_b = 0 W and
  E_b = 0 J.
- **DC input:** gross 6101.072862 + 0 = 6101.072862 J; idle-subtracted 5967.417892 + 0 − 0 × 56.02 = 5967.417892 J
  (idle P_b 0 W over 415 polls).
- **Rest:** 6101.072862 − 1954.281135 (rails) = 4146.791727 J, the same as meter-only.
- **Edge terms:** u = (113.678583 + 106.492041) × (0.017762388 + 0.020) = 8.314169 J. v_start: 12 polls in
  [d0, d0 + 2.302441 s), all 0, so 0 J. v_end: 12 polls, 0 J. So u + v = 8.314169 J.
- **C_j term:** 4.292775 + max(0, 0) = 4.292775 J.
- **Marker:** `bytes.decode_battery_assist` no. Under the request flag this run would leave s5's without-assisted
  line. Under the ruled marker it stays in.

**Qwen3.5-122B, check-r01.** The term is nonzero.

- **Decode span:** T = 11.017813 s, n = 56 polls, T / n = 0.196747 s. The nonzero polls are:
  - at +0.005 and +0.205 s: −37 mA × 12,773 mV = 0.472601 W each;
  - from +0.405 to +1.205 s, five polls: −47 mA × 12,774 mV = 0.600378 W each.
- **Battery term:** Σ P_b = 3.947092 W, so E_b = 0.196747 × 3.947092 = 0.776577 J.
- **DC input:** gross 884.499550 + 0.776577 = 885.276128 J (battery share 0.088 %); idle-subtracted
  856.551274 + 0.776577 = 857.327851 J (idle P_b 0 W over 417 polls).
- **Rest:** 885.276128 − 308.066123 = 577.210005 J (meter-only 576.433428 J).
- **Edge terms:** v_start = 0.196747 × 3.947092 = 0.776577 J (the 12 polls in [d0, d0 + τ) hold all 7 nonzero ones);
  v_end = 0. u = (81.966026 + 87.178466) × 0.037762388 = 6.387300 J, so u + v = 7.163877 J.
- **C_j term:** 3.292067 + 0.776577 = 4.068644 J.
- **Marker:** no. No negative poll was received in [d0 + τ, d1 + τ); every reading fits the prefill's discharge,
  reported late.

**Llama-3.3-70B, soak-r11** (excluded by the harvest; shown for the arithmetic).

- **Battery term:** five polls at −31 mA × 12,770 mV = 0.395870 W each, at +45.722 to +46.522 s into a 57.436307 s
  decode (287 polls). E_b = 0.200127 × 1.979350 = 0.396120 J.
- **DC input:** 6423.530864 + 0.396120 = 6423.926985 J.
- **Edge terms:** v = 0, because the discharge is in the middle of decode, so u + v = u = 8.547328 J.
- **Marker:** yes.

Lead re-run (on the Mac, against the extract): `worked_example.py`, `ruling_table.py`, `lead/lead_table.py`,
`lead/lead_check2.py` and `lead/lag.py`.
All three other councillors' scripts were re-run there too, and each reproduces its committed output byte for byte:
the Opus seat's `bat2_opus.py` (stdout), Sol's `analyse.py` (`analysis.json`) and the judge's `judge.py` (stdout).
Every per-run value in this file agrees across the four programs to the printed digit.

A second lead re-run at 22:31 PDT re-derived these worked examples and §4's counts from H's raw meter stream, without
the extract, through the real `km003c_parse` and `meter_decode` functions ("Executed evidence" below).

## 10. Dissent and what was dropped

**Agreed by both seats and the judge.**

- The clause does not decide Q1 or Q4.
- The term is signed, uses the same span and the same integration rule, and applies to both bases.
- Rest uses the corrected DC input.
- DIFFICULTY's `wall` takes the correction.
- One SMC refresh (1.0 to 1.3 s) is too short a delay.

**Sol's dissent, rejected by the judge (J1 to J4).** I adopt the judge's rulings.

1. **Delay.** Sol proposed L = max(1 s + largest poll gap, largest observed tail) = 2.130 s. That is H's own largest
   observation, so it covers H by construction and leaves no margin for the next stream. τ is derived from the
   reading's averaging and holding instead, and covers the observation with 0.17 s to spare.
2. **Bound form.** Sol proposed b = L × (Q_start + Q_end) + |I − H|, with a two-sided window and the largest power.
   That lets readings lead the energy, which causality rules out, and it is 1.3 to 2.1 J on 122B, against v = 0.56 to
   1.15 J for the same covered error. The |I − H| part is a difference between two integration rules, which bar 2
   checks, not an attribution term.
3. **Idle-basis allowance.** Sol's placeholder adds 8.3 to 10.4 J to 70B's idle-subtracted bound. It does so for an
   idle battery power that read 0 W at every one of 39,163 polls, and it uses the warm-up's power, which comes from a
   different span.
4. **C_j.** Sol proposed o_meter + b, which uses the two-edge sum. A delay shared by all models swaps one slice, so
   the larger edge bounds it.
5. **Marker.** Sol marks any negative reading held into decode, including readings taken before decode start. That
   marks all seven 122B runs on the prefill's late reports.
6. **Meter-only line.** Sol wanted meter-only as a labelled alternative line. The battery column carries the same
   information (meter-only = DC − battery) without a third line beside each primary line.

**Taken from Sol.**

- The NEG-8 reference energies get the term too. The Opus seat missed this; the judge listed it as text the
  registration must carry.
- A sub-1 J term is printed, not rounded to zero.
- The request-scoped count is printed beside the decode-scoped marker.

**Opus seat.** I adopt its answers to Q1 to Q5 with the two additions above. Its one uncertainty was whether the SMC
filter has a tail longer than one averaged second. A longer tail on a later stream would escape both τ and the marker.
The build's per-stream τ and the printed largest v make such a tail visible, and nothing more is added for it.

**My own first draft, dropped.** Before the seats reported, I proposed τ = 1.2 s (one refresh plus one nominal poll),
a two-sided window, and the edge's largest power × 1.2 s (`lead_table.py`, column `ub_J`). The 122B tails rule it out:
6 of 7 run past 1.302 s.

**Process added: none.** No gate, refusal, review round or new collection check. The only new code is one disclose-only
flag. The only removal rule is the existing missing-reading rule, applied to the battery reading, and it removes 0 of
95 H runs.

**Reopen if:**

- a later stream shows battery readings arriving later than its own τ after a power step;
- a decode battery term is large against u (on H the largest v / u is 0.19);
- a schedule starts a run's first span within τ of the previous run's decode end (H: at least 45.0 s, §4);
- any run records `battery_end_window_complete` false (H: 0 of 95, §4).

## 11. Re-running it

From any directory, with JouleWise-data checked out at `analysis/bat-council-20261022` @ `c17fdca` (as `$D`) and
JouleWise at `$R`:

```
P=$D/bat-council-20261022; K=$(mktemp -d)
git -C $R show origin/main:joulewise/external/km003c_parse.py > $K/km003c_parse.py
python3 -I -B $P/worked_example.py $P/data/h_decode_extract.json            # §9 worked examples
python3 -I -B $P/ruling_table.py $P/data/h_decode_extract.json             # §9 per-run table
python3 -I -B $P/lead/lead_check2.py $P/data/h_decode_extract.json         # tau, v, marker counts, the 122B tails
python3 -I -B $P/lead/lead_table.py $P/data/h_decode_extract.json \
  $D/battery-assist-20261022/tables/h_battery_runs.json $K/km003c_parse.py  # check 1 (1e-6 J) and check 2
```

`lead/lag.py` (the onset delays of §3) reads the whole H meter stream, so it runs only on the Mac:
`python3.13 -I -B lag.py /Users/edr/night-bytes/h-20261021T185555Z <joulewise source at 0743a7b90>`.

The extract was written by `data/extract.py` from H's session root, `/Users/edr/night-bytes/h-20261021T185555Z`, with
the real `meter_decode` at `0743a7b90`.

## 12. For the build (backlog item 9)

- `joulewise/bytes_analysis.py`: `meter_decode` adds E_b, its idle-subtracted counterpart, v_start, v_end and the
  marker from `stream.battery_watts()`, with τ computed from the stream's own largest poll interval.
- `neg8_inputs` uses the corrected DC input. `reduce_models` keys the without-assisted line on
  `bytes.decode_battery_assist`. Both are mirrored in the twin.
- The synthetic worlds get battery bursts of at least 1 J (the attribution limit, and far above the agreement bar
  of 1 % of h + B) in four places: inside decode, across the decode start, across the decode end, and in prefill only.
  The prefill-only burst checks that a prefill burst moves neither the term nor the marker beyond v.
- The flag catalog gains `bytes.decode_battery_assist`.
- This is claim-path code: an executing review and both cold passes, as for any BYTES analysis change.
- Added on the third dispatch:
  - The blinded-stage print of §4 is what the build already does (`552561b3f`, and its sentence in
    `docs/contracts/bytes_tables.md`). The twin mirrors it (BY-TWIN-BAT).
  - The three new §8 placements are text only. They go into `docs/registrations/bytes_pack_v1.md` on
    `lane/2026-10-22-bytes-battery-term`, or at BY-MERGE: the Authority insertion, the last paragraph of §6, and the
    last paragraph of §7. No code changes with them.
- Added on the fourth dispatch:
  - The three placements are done (`af821460d`). All of §8 is in the registration at `9bdcf6c95`.
  - The build at `9bdcf6c95` gives this ruling's values on all 95 H runs. What remains for backlog item 9 is the
    twin's battery update (BY-TWIN-BAT; PR #544's one failing test waits for it), then both cold passes.

## Executed evidence

Lead re-run of the worked example, 2026-10-21 22:31 PDT, on the Mac (`/opt/homebrew/bin/python3.13`, flags `-I -B`),
after BAT-2 was re-dispatched. Inputs:

- `$P`: JouleWise-data `analysis/bat-council-20261022` @ `c17fdca`, exported with `git archive`. It holds the packet,
  the extract and the ruling scripts; `$P/../battery-assist-20261022` holds BAT-1's tables from `0cb3eb6`.
- `$K`: `km003c_parse.py` from origin/main `bfab7c950`, byte-identical to the copy at `0743a7b90`.
- `$J`: `joulewise/` at `0743a7b90`.
- `$H`: `/Users/edr/night-bytes/h-20261021T185555Z`, H's session root, read only.
- `$L`: `/Users/edr/night-archive/forward-20261021/BAT-2/lead-rerun`, which holds the two new lead scripts
  (`lead_rerun.py`, sha256 `c5c39696…`; `lead_counts.py`, `56527848…`) and every output below.

```text
$ python3.13 -I -B $P/worked_example.py $P/data/h_decode_extract.json
exit 0
$ python3.13 -I -B $P/ruling_table.py $P/data/h_decode_extract.json
exit 0
$ python3.13 -I -B $P/lead/lead_check2.py $P/data/h_decode_extract.json
exit 0
$ python3.13 -I -B $P/lead/lead_table.py $P/data/h_decode_extract.json $P/../battery-assist-20261022/tables/h_battery_runs.json $K/km003c_parse.py
exit 0
$ python3.13 -I -B $L/lead_rerun.py $H $J
exit 0
$ python3.13 -I -B $L/lead_counts.py $H $J
exit 0
```

What the runs show:

1. `worked_example.py` prints every number in §9's three worked examples, to the printed digit. The output of
   `ruling_table.py` is identical to §9's per-run table (empty diff).
2. `lead_check2.py`: τ = 2.302440875 s; the marker marks 1 run of 95 (soak-llama-70b-r11); the 122B tails are 1.41,
   2.13, 1.20, 1.79, 2.05, 1.87 and 1.84 s; v ≥ |E_b| in every unmarked run. `lead_table.py`: check 1's largest
   difference is 0.0 J over 73 runs (bar 1e-6 J); check 2 has no failures.
3. `lead_rerun.py` is new and does not read the extract. It parses H's whole meter stream (`stream-001.jsonl`, 93,533
   polls, each with both battery values) with the real `km003c_parse.parse`. P_b comes from `Stream.battery_watts`,
   the integral from `km003c_parse.integrate`, the spans from `bytes_analysis._event_span`, the meter values from
   `meter_decode` at `0743a7b90`, and the rails from H's export CSV (`phase_decode_j`). On check-llama-70b-r01,
   check-qwen35-122b-r01 and soak-llama-70b-r11 it reproduces every value §9 prints: T, n, the meter's gross and
   idle-subtracted energy, E_b, DC input on both bases, rails, rest, u, v_start, v_end, u + v, the C_j term and the
   marker. The largest difference is 4.6e-7 J, the print rounding. Bar 1e-5 J: above 10⁶ × the float64 noise on the
   largest value compared (6,424 J × 2.2e-16 × 10⁶ = 1.4e-6 J) and above the 6-decimal rounding (5e-7 J), and below
   1 % of the smallest printed bound entry (v = 0.115 J, so 1.1e-3 J).
4. `lead_counts.py` is new and also reads the raw stream. Over all 95 runs the ruled marker marks 1
   (soak-llama-70b-r11), the harvest's `battery.assist` marks 26, and the held-into-decode marker marks 9. By model
   (harvest / ruled / held): 70B 18 / 1 / 1, 122B 7 / 0 / 7, Next-80B 1 / 0 / 1, as in §4's table. The 122B tails
   are as above: 7 exceed 1.0 s, 6 exceed 1.302 s, none exceeds τ. The 35 runs of models at or below 32B read 0 J.
   These are integer counts, compared by equality.

Acceptance checks made at the same time:

- Both seat reports answer the clause question first: the Opus report's §2 is headed "Does Addendum 1 item 2's last
  sentence decide Q1 and Q4? No."; the Sol report's first section is "Clause: does not decide Q1/Q4".
- The packet's copy of `RULING_battery_assist_2026-10-06.md` is byte-identical to
  `/Users/edr/night-archive/wallmeter-probe/verify/RULING_battery_assist_2026-10-06.md`. It holds no block-5 or
  block-6 claim value; its only measured numbers are the 10-06 probe's 8B tokens/s and battery currents.

### Third dispatch (2026-10-22, 09:00 to 09:30 PDT)

BAT-2 was dispatched a third time with the original brief. The council had already sat and the ruling stood, so no
seat or judge was reconvened. The lead's delegate re-ran everything and added the three text items in the revision
note at the top.

Inputs:

- `$P` is `analysis/bat-council-20261022` @ `c17fdca`, and BAT-1's tables are at `d4f9cd2`; both were exported with
  `git archive`.
- `$K` is `km003c_parse.py` from origin/main `81db9f355` (sha256 `e8fc584a…`). It is byte-identical to the copy at
  `0743a7b90`. The file is also unchanged on `lane/2026-10-20-l9-ruling-build`, compared against `bfab7c950` (empty
  diff).
- `$J` is `joulewise/` at `0743a7b90`.
- `$H` is H's session root, read only.
- Outputs are in `/Users/edr/night-archive/forward-20261021/BAT-2/lead-rerun/third-dispatch/out/`.

```text
$ python3.13 -I -B $P/worked_example.py $P/data/h_decode_extract.json        exit 0, identical to the 22:31 output
$ python3.13 -I -B $P/ruling_table.py $P/data/h_decode_extract.json          exit 0, identical
$ python3.13 -I -B $P/lead/lead_check2.py $P/data/h_decode_extract.json      exit 0, identical
$ python3.13 -I -B $P/lead/lead_table.py $P/data/h_decode_extract.json <BAT-1 h_battery_runs.json> $K/km003c_parse.py
                                                                             exit 0, identical
$ python3.13 -I -B $L/lead_rerun.py $H $J                                    exit 0, identical
$ python3.13 -I -B $L/lead_counts.py $H $J                                   exit 0, identical
$ python3.13 -I -B $L/third-dispatch/gap_check.py $P/data/h_decode_extract.json   exit 0 (new; sha256 5dac0ae3…)
```

"Identical" means byte for byte against `$L/out/` from 22:31 PDT. Item 3 of the list above (the raw-stream re-run
through the real `km003c_parse` and `meter_decode`) still gives a largest difference of 4.6e-7 J from the printed
values, against the bar of 1e-5 J.

`gap_check.py` orders integer nanosecond stamps and counts polls, so it needs no bar. It found:

- τ = 2.302440875 s;
- 95 of 95 idle baselines lie before their requests;
- request end minus decode end ranges from 0.000596 to 0.003278 s;
- the smallest gap from a decode end to the next run's first span is 45.029 s (`neg8-refcorpus-r15` to `-r16`),
  and 0 of 94 gaps are below τ;
- 1,102 polls were received in [d1, d1 + τ), with 0 nonzero B0AC;
- the shortest full-length decode is 2.324 s (qwen3-1p7b);
- 28 decodes are no longer than τ: the 22 NEG-8 references (0.990 to 1.006 s) and six `test7-*-start` runs.

State of the other parts at this dispatch, recorded only:

- Both seat branches and the judge's branch are on JouleWise-data's origin at the commits named in "Who sat".
- The build (BAT-3, PR #544) is at fix round 1 `a846ba997`. BAT-1's fourth dispatch found that it gives the same H
  output.
- PR #536's CI on `c220c6e78` was pending when this revision was written.

### Fourth dispatch (2026-10-22, 14:20 to 14:40 PDT)

BAT-2 was dispatched a fourth time with the original brief. The council had sat and every acceptance item was met,
so no seat or judge was reconvened. The lead's delegate re-ran everything, then checked the build and the
registration text against this ruling.

Inputs:

- `$P` is `analysis/bat-council-20261022` @ `c17fdca`, and BAT-1's tables are at `d425514`; both were exported with
  `git archive`.
- `$K` is `km003c_parse.py` from origin/main `c21c52dfa` (sha256 `e8fc584a…`), byte-identical to the copy at
  `0743a7b90`.
- `$J` is `joulewise/` at `0743a7b90`. `$H` is H's session root, read only.
- `$F` is `/Users/edr/night-archive/forward-20261021/BAT-2/lead-rerun/fourth-dispatch`. It holds the two new scripts
  (`build_vs_ruling.py`, sha256 `e0d34116…`; `regtext.py`, `318767d9…`) and every output.

```text
$ python3.13 -I -B $P/worked_example.py $P/data/h_decode_extract.json        exit 0, identical
$ python3.13 -I -B $P/ruling_table.py $P/data/h_decode_extract.json          exit 0, identical
$ python3.13 -I -B $P/lead/lead_check2.py $P/data/h_decode_extract.json      exit 0, identical
$ python3.13 -I -B $P/lead/lead_table.py $P/data/h_decode_extract.json <BAT-1 h_battery_runs.json> $K/km003c_parse.py
                                                                             exit 0, identical
$ python3.13 -I -B $L/lead_rerun.py $H $J                                    exit 0, identical
$ python3.13 -I -B $L/lead_counts.py $H $J                                   exit 0, identical
$ python3.13 -I -B $L/third-dispatch/gap_check.py $P/data/h_decode_extract.json   exit 0, identical
$ python3.13 -I -B $F/build_vs_ruling.py $P/data/h_decode_extract.json \
    <BAT-1 tables>/h_meter_decode_bat3_9bdcf6c95.json                        exit 0, 0 failures
$ python3.13 -I -B $F/regtext.py BAT-RULING.md <bytes_pack_v1.md at 9bdcf6c95>  22 of 22 found
```

"Identical" means byte for byte against the stored outputs of 22:31 PDT (`$L/out/`) and of the third dispatch
(`gap_check.txt`). So the worked examples of §9 reproduce again, to the printed digit.

`build_vs_ruling.py` is new. It computes the ruled quantities from the extract at full precision, as
`ruling_table.py` does, for all 95 H runs. It compares them with BAT-3's `meter_decode` output at `9bdcf6c95` (BAT-1's
table, whose runs equal the BAT-3 director's own output; only the recorded source path differs). Bars, set here:
joules 1e-5 J, as in item 3 of the first re-run (above 10⁶ × float64 noise on 6,424 J, which is 1.4e-6 J, and below
1 % of the smallest printed bound entry, v = 0.115 J); τ 1e-9 s, one tick of the integer-nanosecond stamps both
sides read; poll counts and the marker by equality. Results:

- 95 of 95 runs matched by id. τ = 2.302440875 s on both sides.
- Largest differences: battery term 1.1e-16 J; v_start, v_end and v 0 J; DC input on both bases 2.3e-13 J; u + v
  1.8e-15 J; C_j term 8.9e-16 J; τ 0 s. Battery poll counts and the marker are equal on every run.
- 9 runs have a nonzero term, and 1 is marked (soak-llama-70b-r11), as in §4 and §9.
- `battery_end_window_complete` is true on 95 of 95, and the extract holds a poll at or after d1 + τ for every run.

`regtext.py` is new. It checks every quoted paragraph of §8, and the quoted phrases of the §7 table, §9, §15, §16 and
§20 replacements, against the registration at `9bdcf6c95`. The match is exact after whitespace is collapsed. All 22
are present.

State of the other parts at this dispatch, recorded only:

- B6-1's fourth pass (`42dea5496`, draft PR #537) §7.1 still keeps block 6's per-phase value meter-only and states
  that BYTES no longer takes S-15's fill. Nothing in it changes this ruling.
- PR #544 is a draft at `9bdcf6c95`. BAT-1's fifth dispatch recorded 20 of 21 CI jobs passing; the one failure
  expects the twin's battery update.
- `ops/stop-pause` is present on origin (`dac3b7e62`). Nothing here touched a window.
