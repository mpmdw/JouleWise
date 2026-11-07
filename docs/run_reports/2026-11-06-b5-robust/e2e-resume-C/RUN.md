# Block-5 interrupted/resumed synthetic-chain run C

- Git HEAD: `150b8e7b3b2627607e6e3b4c481331ed370fc321`
- Python: `Python 3.12.13`
- `nproc`: `3`
- Command: `mkdir -p /tmp/jwr/tmp && TMPDIR=/tmp/jwr/tmp python3 -B scripts/b5_e2e_synthetic.py --scratch /tmp/jwr/run --out /tmp/jwr/out/C --workers 2 --stop-after 5 --interrupt-in-step 5 > /tmp/jwr/C.stdout 2> /tmp/jwr/C.stderr`
- Harness exit: `1` (normal synthetic-stop closure; joined-driver exit `2`)
- Wall time: `3038` seconds
- Summary `record_sha256`: `5d561618daa4ba0e8966bb443c911fd4b2b5dc2e658ec2d645fed3ca16e7306a`
- Summary `exit_code`: `2`
