# Exhibit D — observer floor and stop branch (executed at the bench, generator inline in the synthesis commit; read-only archives)

Generated 2026-09-23 00:14:07 PDT at main `258c90ed`.

## D1 — `joulewise/quiet_predicate_campaign.py` at 258c90ed: `stop_branch` (925–940) and the observer-floor derivation (1064–1073)
```
925: def stop_branch(*, s_upper=None, observer_floor=None, block_two_upper_j=None, protocol=None):
926:     """Apply only ruled stop conditions; absent evidence is never a pass."""
927:     protocol = frozen_protocol() if protocol is None else protocol
928:     smallest_share = protocol["block_two"]["smallest_holdable_share"]
929:     for value in (s_upper, observer_floor, smallest_share, block_two_upper_j):
930:         if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
931:             raise ValueError("stop-branch evidence must be finite and nonnegative")
932:     causes = []
933:     pairs = None if s_upper is None else size_block_two(s_upper, protocol)
934:     if pairs is not None and pairs > protocol["sizing"]["maximum_pairs"]:
935:         causes.append("sized_pairs_above_24")
936:     if observer_floor is not None and observer_floor > smallest_share:
937:         causes.append("observer_floor_above_smallest_holdable_share")
938:     if block_two_upper_j is not None and block_two_upper_j > protocol["sizing"]["delta_j"]:
939:         causes.append("block_two_upper_bound_above_1_J")
940:     return {"outcome": protocol["stop_branches"][causes[0]] if causes else "no decision", "causes": causes, "pairs": pairs}
...
1064:     s_upper = pair_sd * factor if sufficient else None
1065:     # Whole-round measured cost, including rejected envelopes; never subtract
1066:     # it from energy or use it as an envelope retention input.
1067:     observer_rows = [r for r in all_rows if harness.number(r.get("observer_cpu_s")) is not None
1068:                      and harness.number(r.get("round_mono_start_s")) is not None
1069:                      and harness.number(r.get("round_mono_end_s")) is not None
1070:                      and r["round_mono_end_s"] > r["round_mono_start_s"]]
1071:     observer_support_s = sum(r["round_mono_end_s"] - r["round_mono_start_s"] for r in observer_rows)
1072:     observer_floor = sum(r["observer_cpu_s"] for r in observer_rows) / observer_support_s if observer_support_s else None
1073:     stop = stop_branch(s_upper=s_upper, observer_floor=observer_floor, protocol=protocol)
```

## D2 — registration v2 fields that the stop branch reads
```
block_two = {"authored_after_pilot": true, "contrast": "idle-load-idle bracket", "levels": [0, 0.05], "one_profile": true, "one_qos": true, "smallest_holdable_share": 0.05, "upper_bound": "one-sided 95% paired-contrast upper bound"}
stop_branches = {"block_two_upper_bound_above_1_J": "no cutoff qualifies", "observer_floor_above_smallest_holdable_share": "no cutoff qualifies", "sized_pairs_above_24": "no cutoff qualifies"}
sizing = {"assumption": "independent normally distributed disjoint pair differences", "chi_square_lower_tail_probability": 0.1, "confidence": 0.9, "delta_j": 1, "formula": "max(3, ceil(8 * s_upper**2 / delta_j**2))", "maximum_pairs": 24, "minimum_pairs": 3, "multiplier": 8, "reference_factors": {"n_4": 2.266, "n_6": 1.762}, "s_pair": "sample SD of retained disjoint differences, df = n - 1", "s_upper": "s_pair * sqrt((n - 1) / chi_square_quantile(0.10, n - 1))"}
power_interval_ms = 100
sample_interval_s = 30
envelope_s = 600
interior_s = 480
```

## D3 — both nights' observer floor and stop causes (summary.json, read-only archives)
```
PRIOR 20260922-0217 sha256 9121f080c97e4b2f8f01261d0a2f9f407840dea9a6c8ca4468406617403d6f04
  observer_floor_cores 0.05309837244298898 observer_support_s 7088.112265665026 whole_campaign_observer_cpu_s 1339.078336
  observer_definition "SELF + reaped CHILDREN, including collector, recorder, sampler and census; never subtracted"
  block_two_stop {"causes": ["observer_floor_above_smallest_holdable_share"], "outcome": "no cutoff qualifies", "pairs": null, "pairs_reason": "not available in source evidence"}
  per-envelope (index, observer_cpu_s, recorder_observer_cpu_s, whole_envelope_observer_cpu_s): [(1, 31.401336999999995, 4.426482, 104.38084200000002), (2, 31.408472000000003, 4.421089000000001, 106.76108599999999), (3, 31.388097000000002, 4.3935960000000005, 104.02904900000001), (4, 31.556651999999996, 4.169250000000005, 103.363427), (5, 31.311549999999997, 4.403691999999996, 106.206999), (6, 31.302491000000014, 4.463497999999994, 104.77170900000002), (7, 31.260666999999994, 4.37169200000001, 103.130313), (8, 31.264636999999997, 4.15359700000004, 107.03923), (9, 31.411355999999987, 4.389597000000009, 105.476834), (10, 31.30837, 4.376050999999997, 103.56611799999999), (11, 31.541455999999997, 4.3452069999999665, 106.031936), (12, 31.212139999999994, 4.143810000000002, 106.11325799999999)]
  excess over smallest_holdable_share: 0.00310 cores; at 0.3125 W per busy core (exhibit C8) over the 480 s interior = 0.465 J; over 600 s = 0.581 J
TONIGHT 20260922-2100 sha256 84bfcafb84cb08ddb6b4c1e2fe707ac2b74a1e5b055ecba204a3740c58fe2bc2
  observer_floor_cores 0.05282276792404742 observer_support_s 7181.620632706385 whole_campaign_observer_cpu_s 1239.619517
  observer_definition "SELF + reaped CHILDREN, including collector, recorder, sampler and census; never subtracted"
  block_two_stop {"causes": ["sized_pairs_above_24", "observer_floor_above_smallest_holdable_share"], "outcome": "no cutoff qualifies", "pairs": 517081}
  per-envelope (index, observer_cpu_s, recorder_observer_cpu_s, whole_envelope_observer_cpu_s): [(1, 31.928024999999995, 4.517104999999999, 101.05070299999998), (2, 31.310905000000005, 4.424526, 94.42216400000001), (3, 31.613000999999997, 4.436396000000002, 95.17352999999999), (4, 31.659441, 4.158046999999996, 97.04074), (5, 31.547155, 4.3493730000000035, 96.072779), (6, 31.63373, 4.213099000000007, 96.625665), (7, 31.649067, 4.355274000000005, 96.094765), (8, 31.551395, 4.360983999999995, 97.286111), (9, 31.635490000000004, 4.21699000000001, 97.157064), (10, 31.617785, 4.421622000000006, 96.61626799999999), (11, 31.597317000000007, 4.193398999999992, 95.240092), (12, 31.609768999999996, 4.4256480000000025, 95.975961)]
  excess over smallest_holdable_share: 0.00282 cores; at 0.3125 W per busy core (exhibit C8) over the 480 s interior = 0.423 J; over 600 s = 0.529 J
```

## D4 — the recorder's own cost per 30 s journal row (evidence_busy_cores.jsonl `observer_cpu_s`)
```
PRIOR sha256 39224eb543f582d62ee2d8fdb1d93e6d83ebab7188d3740a55057a1fd84313db rows 238 observer_cpu_s/row median 0.236 mean 0.230; row duration median 30.40 s; recorder share 0.0076 cores
TONIGHT sha256 4ad71d0be4f6af605871b8531db44e305a3ed3e157c91e9c6bfa4e21a392f86c rows 245 observer_cpu_s/row median 0.236 mean 0.232; row duration median 30.40 s; recorder share 0.0076 cores
```

## D5 — `night_gate` load path at 258c90ed (refuter M1)
```
1262: def _check_machine(plan, probes, rows, evidence, *, legacy_load=True):
1530:     refused = _check_machine(plan, probes, rows, evidence, legacy_load=False)
1540: def evaluate_night(plan: NightPlan, probes: Probes, *, pack_arm_receipt=None, pack_conditions=None) -> Receipt:
1575:     refused = _check_machine(plan, probes, rows, evidence)
tonight receipt C3 detail: "agent, HID, AC, display, load, and thermal predicates passed" load_1m 1.03
```
