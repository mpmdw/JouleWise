# Block-5 analysis driver robustness: synthetic end-to-end equality evidence

Date: 2026-11-06/07 UTC

## Scope and blinding

This report compares the synthetic S10 end-to-end output from reference commit
`288c094f4598d1040bc7718432e5ec19471cea74` (BASE) with robustness commit
`bd4e141a94737e069e4f26bc62320c7817e3e6ee` (HEAD). Only the committed synthetic
fixtures and the harness-created scratch custody were used. The scratch custody
was not inspected directly; output identity was evaluated only through each
harness-produced `summary.json` manifest and digests. The same scratch path was
used serially, and `/tmp/jwb5e2e/run` was deleted between runs.

Environment:

- Python: `Python 3.13.13` (`PYENV_VERSION=3.13`; `python3` in each command)
- `nproc`: `3`
- Workers: `2`

## Stop-after-5 pair

The BASE worktree was detached at `288c094f4`. The exact harness command was:

```sh
mkdir -p /tmp/jwb5e2e/tmp && TMPDIR=/tmp/jwb5e2e/tmp python3 -B scripts/b5_e2e_synthetic.py --scratch /tmp/jwb5e2e/run --out /tmp/jwb5e2e/out/base --workers 2 --stop-after 5
```

The HEAD worktree was detached at `bd4e141a9`. After deleting
`/tmp/jwb5e2e/run`, the exact harness command was:

```sh
mkdir -p /tmp/jwb5e2e/tmp && TMPDIR=/tmp/jwb5e2e/tmp python3 -B scripts/b5_e2e_synthetic.py --scratch /tmp/jwb5e2e/run --out /tmp/jwb5e2e/out/head --workers 2 --stop-after 5
```

| Run | Outer wall time | Joined-driver wall time | Process exit | Joined-driver exit | `record_sha256` | `manifest_sha256` | Files |
|---|---:|---:|---:|---:|---|---|---:|
| BASE | 1,395 s | 1,310.087849479 s | 1 | 2 | `8def95ee9566462a5cdf27b54d1aaee9ea7fe4a74fb2cab06d723fc9b0c20fb4` | `b01649b97e4ae1f0209725dc2c6dab6f1ab9e6bbe5628d9411c1f4204a05afc8` | 1,358 |
| HEAD | 1,424 s | 1,325.4517795800002 s | 1 | 2 | `8def95ee9566462a5cdf27b54d1aaee9ea7fe4a74fb2cab06d723fc9b0c20fb4` | `d017914895eec3aaf3857740ddc2f66d81b186d288361579676d4c6df048d652` | 1,358 |

Process exit 1 with joined-driver exit 2 is the expected `--stop-after 5`
closure at step 8.

### Equality verdict: NOT EQUAL

`record_sha256` is equal, but the full manifests are not equal. There are three
path-level differences (names and digests only):

| Path | BASE digest | HEAD digest |
|---|---|---|
| `dry-run/restricted/logs/runtime-phases.jsonl` | `136f658b0268997a64a906b6ee670ce19a97779b820a01b995f61bd61ec7e9a3` | `ff5b4a0ebfeffb9b5148939cf7c09a77f07eb8f2e218b4ba8edf511e6cedc454` |
| `dry-run/restricted/logs/runtime-stack-6093.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | missing |
| `dry-run/restricted/logs/runtime-stack-7344.txt` | missing | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

HEAD has **no** `restricted/resume/` path in its manifest.

The preserved harness outputs are [`base/summary.json`](base/summary.json),
[`base/stderr.txt`](base/stderr.txt), [`head/summary.json`](head/summary.json), and
[`head/stderr.txt`](head/stderr.txt).

## Full-run pair

Not run. The required serial stop-after pair consumed approximately 47 minutes
including harness setup and teardown, so no remaining execution window was
committed to the substantially longer optional full pair.
