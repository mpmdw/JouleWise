# cProfile run failure

The synthetic-only joined driver completed steps 0, 1, 2, 3, and 3b, then
returned exit code 2 after step 4 reported `tooling_refusal`. Consequently,
steps 5, 8, 6, 9, 9b, 10, and 11 did not run. The profiles that existed at
process exit were rendered into `report.txt`; this directory must not be read
as a complete profile of the full driver.

Command:

```text
TMPDIR=/tmp/jwprof/tmp /root/.pyenv/versions/3.13.13/bin/python3.13 -B scripts/b5_e2e_synthetic.py --scratch /tmp/jwprof/run --out /tmp/jwprof/out --label head-cprofile --workers 2 --cprofile /tmp/jwprof/prof
```

Driver result: `exit_code=2`, profiled-run wall time `3155.426879516999 s`.

## stderr tail

```text
step 0 - ok
step 1 - ok
step 2 - ok
step 3 - ok
step 3b - ok
step 4 - tooling_refusal
step 5 - not_run
step 8 - not_run
step 6 - not_run
step 9 - not_run
step 9b - not_run
step 10 - not_run
step 11 - not_run
```
