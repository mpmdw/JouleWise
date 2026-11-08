# v5 ruling delta7 — Sol2 independent review

2026-11-08. **SIGN at design-ruling level. LOCAL_ONLY; no push.**
Branch `align/2026-11-08-v5design-ruling-delta7-sol2` was already checked
out and clean at intake, based on candidate
`4078c08509d81d61818dc477e1368ef6672b3e5f`.

The [review](../align/squeeze/v5-design/ruling-delta7-review-sol2.md)
quotes output and records the detailed judgments. The spawn transport fix
works. Exact author jobs reproduce MDEs .12/.12/.12/.14/.14 under stress,
the +24-window stress sizing choice and +8 intermediate choice. The
byte-identical prior independent simulator reproduces its earlier MDEs;
its coupled stress law reaches the H1/conjunction target at +16, and
also clears it at the author's more conservative +24. This difference
comes from the distinct joint laws, including identical H1/H3 in my toy
law, rather than a remaining transport bug.

The new honest bar is reasonable as a gross-inflation screen. At nominal
iid .05 FPR its per-rule false fail is 1.4327%; six independent rules fail
8.2942% of the time. In the independent common-score simulation, all-six
false fail is 7.170% iid and 14.245% with within-pair/window alarm ICC .09.
The Hoeffding width is .0731404260, so 22/280 alarms has upper bound
.1517118546. These do not establish operating FPR≤.05.

No blocking question remains for this ruling signature. G12 must still
freeze dependence-appropriate rate UCBs, the ICC estimator/uncertainty
treatment, the full-stage coupled/calibrated law, and every resized roster
denominator. In particular, choose prospectively whether an expanded
design's honest gate uses a preassigned 280 or a new all-member cutoff;
22 alarms over all 520 would falsely fail a nominal iid rule 75.46% of
the time. The existing full-stage G12 and CAP gates remain mandatory;
the stress increment is 470.4 reserved hours, not demonstrated available
capacity. Native detector rates, calibration-threshold variation and
actual calendar feasibility remain unknown.

Files added:

- `docs/align/squeeze/v5-design/ruling-delta7-review-sol2.md`: verdict,
  output, power/gate tables, judgments and registration carry-forwards.
- `docs/align/squeeze/v5-design/power_sim_sol2.py`: byte-identical restoration
  from the prior delta5-sol2 branch; SHA-256
  `1ed19bfb3a63337ccc53ecd85e982858eafa4e57d5a5e5c35c9f18f2ebe2760e`.
- `docs/align/squeeze/v5-design/power_delta7_sol2.py`: synthetic sequential
  replay/roster/gate/transport harness; SHA-256
  `8be7ee1c11b0b6906b6935ffcabd1c329aa0fe2b1bee90c0d6e6fce2b2f4299f`.
- `docs/align/squeeze/v5-design/ruling-delta7-sol2-output.jsonl`: complete
  stdout, 122 JSON records / 40,569 bytes; SHA-256
  `b90aa230bd2a227159d1c2b07363282e139df6b17aa25c39c27297289f526103`.
- This run report. Candidate ruling, author code/tests and coordination
  state are untouched.

Verification commands, from the repository root, run one at a time:

```sh
python3.13 -I -B -m unittest discover -s docs/align/squeeze/v5-design -p test_ruling_power_sim.py -v
python3.13 -I -B docs/align/squeeze/v5-design/power_sim_sol2.py --self-test
python3.13 -I -B docs/align/squeeze/v5-design/power_delta7_sol2.py independent --reps 2000
python3.13 -I -B docs/align/squeeze/v5-design/power_delta7_sol2.py author --reps 2000
python3.13 -I -B docs/align/squeeze/v5-design/power_delta7_sol2.py gates --reps 20000
python3.13 -I -B docs/align/squeeze/v5-design/power_delta7_sol2.py icc --reps 2000
python3.13 -I -B docs/align/squeeze/v5-design/power_delta7_sol2.py transport --reps 64
git diff --check
git diff --cached --check
```

Results: **3/3 supplied and 6/6 independent unit tests pass** (0.088 s /
0.038 s). All simulation modes complete successfully. The final transport
probe confirms stress parameters and byte-identical sorted-JSON output
between sequential and one-worker spawn. All four Python source files parse
with `ast.parse`; the combined evidence parses and its job/effective values
match. Targeted verification stayed under the requested ~20-minute budget.

No full suite, pytest, production pipeline, real measurements, restricted
directories, network, weights or MLX execution. No new MLX/native code or
native test is introduced. The lead must still run the ruling's native
G4–G9 qualifications and complete G12 outside this sandbox; these results
are synthetic planning/review evidence only. The running analysis job was
not inspected or controlled. Git operations used only this clone and
allowed shared repository objects. No subagent or peer consult was used;
this remains the independently assigned Sol2 seat.

The user brief overrides normal coordination writes and full-suite workflow:
`RUN_STATE.md`, `TASK_QUEUE.md`, the state kernel and `tests/test_gen_state.py`
are unchanged; no kernel task was registered. The supplied branch receives
one local commit, `review(align): sign v5 revision 7 from Sol2 power replay`;
the final handoff names its exact SHA. No push is authorized or attempted.

Next exact step: the lead reads this report and the independently assigned
Sol1 verdict, adjudicates/signs the ruling if both agree, and carries the
named G12/roster/CAP obligations into registration before data.
