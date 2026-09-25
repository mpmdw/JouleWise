# 16/14 — Sweep 3 invocation (A292-ESC-01 G6(iv) custody copy)

Sweep 3 at 241ea65c: 119 mutants, 117 killed, M081 and M083 equivalent (proofs in ex-11), zero non-equivalent survivors.

Scripts (byte copies, tracked here):
- `12-sweep3-script.py.txt` = `/tmp/152c9255/a292-round2-sol/sweep.py`, sha256 `554720d351346b5a1e66bd9898108d1f038b8bda57cc6fcf09c99dfd9b1c814d`
- `13-differential-script.py.txt` = `/tmp/152c9255/a292-round2-sol/differential.py`, sha256 `4f22e9a039159eeafdd0c74390f8b20ec9955b13c7e570b5601aec9d2e08e6da`

Verbatim command lines (ex-11 V2–V6):
```
python3 -B /tmp/152c9255/a292-round2-sol/sweep.py > /tmp/152c9255/a292-round2-sol/sweep3.log
A292_START=0 A292_STOP=50 python3 -B /tmp/152c9255/a292-round2-sol/differential.py > /tmp/152c9255/a292-round2-sol/differential_0_50.log
A292_START=50 A292_STOP=100 python3 -B /tmp/152c9255/a292-round2-sol/differential.py > /tmp/152c9255/a292-round2-sol/differential_50_100.log
A292_START=100 A292_STOP=150 python3 -B /tmp/152c9255/a292-round2-sol/differential.py > /tmp/152c9255/a292-round2-sol/differential_100_150.log
A292_START=150 A292_STOP=200 python3 -B /tmp/152c9255/a292-round2-sol/differential.py > /tmp/152c9255/a292-round2-sol/differential_150_200.log
```
