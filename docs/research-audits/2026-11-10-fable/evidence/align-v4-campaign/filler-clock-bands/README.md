# Filler launch bands at the two pinned runners

All endpoints are inclusive, in America/Los_Angeles. The pinned launcher plans gave the same bands on November 20 and 21, 2026 (PST). The tables describe clock admission. Item 422's ladder selects among READY work after the applicable gates pass.

## Pin A

`2d347f721552fe03bdd19f113e7bad7a7c24908e` serves f2-inst-01 through -03 and f2-stab-01 through -14. The one-leg cases were f2-inst-02 L005 and f2-stab-01 L001. The two-leg cases were f2-inst-02 L005,L006 and f2-inst-03 L001,L002. The alternate argument's earlier two-leg morning cutoff is covered by the default argument.

| Legs | Worst case | Batch window | Admits t0 | Refuses t0 | Refused time per day |
| ---: | ---: | --- | --- | --- | ---: |
| 1 | 5,850 s | `02:00-02:35` | 02:35:00–10:50:00, 13:15:00–23:48:10 | 00:00:00–02:34:59, 10:50:01–13:14:59, 23:48:11–23:59:59 | 5:11:48 |
| 1 | 5,850 s | `13:14-13:15` | 00:00:00–10:50:00, 13:15:00–23:59:59 | 10:50:01–13:14:59 | 2:24:59 |
| 2 | 8,550 s | `02:00-02:35` | 02:35:00–10:50:00, 13:15:00–23:03:10 | 00:00:00–02:34:59, 10:50:01–13:14:59, 23:03:11–23:59:59 | 5:56:48 |
| 2 | 8,550 s | `13:14-13:15` | 00:00:00–10:17:10, 13:15:00–23:59:59 | 10:17:11–13:14:59 | 2:57:49 |

With both arguments available, pin A still refuses every t0 from 10:50:01 through 13:14:59. That costs **8,699 launch seconds per day (2:24:59, about 2.42 hours)** for either roster size when only pin A has READY work.

## Pin B

`6e9d42f1dd3d308bc9239143d0d634ab965e50e1` serves the one-leg f2-stab-15 and -16 filler queues. The swept roster was f2-stab-15 L003. The pin uses an empty window list when the argument is omitted. Naming the old window still enables overlap refusal.

| Legs | Worst case | Batch window | Admits t0 | Refuses t0 | Refused time per day |
| ---: | ---: | --- | --- | --- | ---: |
| 1 | 5,850 s | Omitted | 00:00:00–23:59:59 | None | 0:00:00 |
| 1 | 5,850 s | `02:00-02:35` | 00:00:00–00:22:30, 02:35:00–23:59:59 | 00:22:31–02:34:59 | 2:12:29 |

## Pick the argument

| Local t0 | Pin A, one leg | Pin A, two f2-inst legs | Pin B, one f2-stab leg |
| --- | --- | --- | --- |
| 00:00:00–02:34:59 | `13:14-13:15` | `13:14-13:15` | Omit the argument |
| 02:35:00–10:50:00 | `02:00-02:35` | `02:00-02:35` | Omit the argument |
| 10:50:01–13:14:59 | Refused | Refused | Omit the argument |
| 13:15:00–23:03:10 | `02:00-02:35` | `02:00-02:35` | Omit the argument |
| 23:03:11–23:48:10 | `02:00-02:35` | `13:14-13:15` | Omit the argument |
| 23:48:11–23:59:59 | `13:14-13:15` | `13:14-13:15` | Omit the argument |

A READY pin B leg leaves **zero clock-only dead time** in the filler ladder. During pin A's midday gap, check the higher rungs and use f2-stab-15 or -16 at rank 4 when available. The first f2-stab leg of the local date can use pin B at 00:00:00 at rank 1.

`pick_filler_arg.sh EPOCH A|B 1|2` encodes the table. `NO-WINDOW` means omit the flag entirely. `NONE` means there is no applicable launch for the given inputs. The current pin B filler queues have one-leg entries, so `B 2` returns `NONE`. Use the pin's native plan at the actual t0.

## Verification

- The launcher function took the immutable kit path, explicit roster, optional argument, and epoch t0. Each of the 10 filler cases covered 1,440 minute samples and the final second on both dates. Each observed transition was bisected and checked at the transition second and the adjacent seconds. [Second-level bands and witnesses](bands.json) · [Sweep samples with exact refusal text](sweep-samples.tsv.gz)
- Item 406's f2-inst-01 L001,L002,L003 regression passed on Nov 17, 20 and 21. With the default argument, the last evening admit was 22:18:10. The alternate admitted at 09:32:10 and refused at 09:32:11. Both refused at 10:50:01 and admitted at 13:15:00. [Regression bands](bands.json)
- The pinned `cadence_queue.py validate-kit --repo` checked frozen paths. The pinned `cadence_legs_runner.py plan --t0` matched the launcher function inside each admitted and refused band. [Native CLI results](native-cli.json)
- Three synthetic runner mocks used `nice -n 10` and `--t0-local`. On pin B, L003 ran at 11:30 and at 01:50 with no window. The latter's soak and leg both overlapped 02:00–02:35. On pin A, L005,L006 ran at 01:45 with the alternate and crossed 02:00–02:35. All returned rc 0 and recorded zero blackout holds. [Mock stage timings](mock-spans.jsonl)
- The picker passed in Bash and zsh, executed and sourced. The test compares both edges of observed bands and adjacent sampled seconds, including midnight between the two sweep dates. [Picker test](test_pick_filler_arg.py) · [Counts and hashes](VERIFICATION.json)

To repeat a case, use the checked-out pin and the corresponding audit-tree kit.

```sh
export PYTHONDONTWRITEBYTECODE=1
python3.13 -I -B sweep_plan.py --checkout "$PIN_CHECKOUT" --kit "$KIT" \
  --legs L005,L006 --batch-window 13:14-13:15 --day 2026-11-20 --day 2026-11-21
python3.13 -I -B test_pick_filler_arg.py
```

Read the lead's proposed [RUN_STATE item body](ITEM-BODY.md) and the [run report](../../../../../run_reports/2026-11-19-filler-clock-bands.md).
