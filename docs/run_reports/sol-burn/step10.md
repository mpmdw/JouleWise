# Block 5 STEP 10: per-pack warm-cache transport

Date: 2026-11-06. Scope: synthetic data only; no production or restricted
experiment path was opened.

## Finding

`pack_map` formerly snapshotted the complete run physics store into every
`PackTask`, independently of the pack call. With two STEP 10 calls this meant
serializing and sending every warm partition twice. The task construction now
walks the already-loaded call graph for `instrument_calibration.b_fiducial_s`,
uses the same `_effective_bound_partition` function as the cache itself, and
copies only matching partitions. The walk performs no file read. An unfamiliar
call graph that exposes no partition retains the former full-store snapshot;
the optimization therefore cannot make such a warm call cold.

The implementation is in `joulewise/b5_analysis/pack_parallel.py:122-169`.
The synthetic equality and scheduler-wiring tests are in
`tests/b5_analysis/test_pack_parallel.py:40-117`.

## Synthetic measurement

I constructed three partitions of 1,000 float entries each and selected the
first pack's bound. `pack_parallel.dumps` measured **60,103 bytes** for the old
whole-store payload and **20,044 bytes** for the slice: **40,059 bytes fewer
(66.65%)**. The slice contained **1 partition instead of 3**, and its selected
mapping compared equal to the corresponding whole-store mapping. This is an
illustration of transport scaling, not a production timing claim.

Exact command:

```sh
python3 - <<'PY'
from joulewise.b5_analysis import pack_parallel as p
store={float(i).hex():{f'fit-{j:04d}':float(j) for j in range(1000)} for i in (1,2,3)}
call=(({"instrument_calibration":{"b_fiducial_s":1}},),{})
s=p._pack_physics(store,call)
print('whole_partitions',len(store),'slice_partitions',len(s))
print('whole_bytes',len(p.dumps(store)),'slice_bytes',len(p.dumps(s)))
print('equal_selected',s[float(1).hex()]==store[float(1).hex()])
PY
```

Output: `whole_partitions 3 slice_partitions 1`, `whole_bytes 60103
slice_bytes 20044`, and `equal_selected True`.

## Equality evidence

The focused tests prove three boundaries:

1. alpha and beta receive only their respective cache partitions, and every
   selected partition is value-equal to the old whole-store source;
2. opaque argument shapes fall back to a separately snapshotted payload whose
   serialized bytes equal the old whole-store payload; and
3. `pack_map` actually embeds the two distinct slices in its two `PackTask`s,
   while both synthetic computations complete successfully.

`python3 -m unittest tests.b5_analysis.test_pack_parallel` passed all **10 tests
in 84.549 s** after the implementation and all three equality boundaries were
in place.
