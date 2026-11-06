# ALIGN v4 R0, 2026-11-06: failed at model-load (launcher defect), not re-run

Record: `/Users/edr/night-align/r0-v4-20261106T1605Z`, launched by magistrate
activation 39a55bff about 08:03 PST (launch id `f975ba0bd3d94eaeb52336518889ccf1`),
exited after 20.8 s. Read and committed by activation 0e88b99f.

- sha256 `report.json` 72ae3ac5d426ab0bcc2d716b0b8940e5d87497c5634ea94f9371f73f0504d281
- sha256 `report.md`   525087da1e05e561f0663aa66be22279a3225bb3fb8d9bd00c46d33973652771
- SMC journal: none. The run stopped at model-load, before any SMC capture.

Checks: host pass, disk diagnostic, host-identity pass (Mac15,9, 128 GiB),
model-load FAIL (`PackageNotFoundError: No package metadata was found for mlx`).
No later check ran, so there is no SMC key classification, rung selection, B7
verdict or peak memory.

**Cause.** `scripts/launch_align_r0.py` on main resolves every path argument with
`Path.resolve()`, including `--python-bin`. The venv interpreter
`$M/.venv/bin/python` is a symlink chain to `/opt/homebrew/opt/python@3.13/bin/python3.13`,
so `runner.json` carried the bare Homebrew interpreter. Python finds a venv from
the path it was invoked by (`pyvenv.cfg` beside it), so the runner lost the venv:
Homebrew 3.13 has no `mlx` distribution, the venv has mlx 0.31.2. Preflight (1b)
ran the venv path directly, which is why it passed.

**D pin verification** (`align_v4_verify_d_pins.py`): FAIL, but only on 41 extra
files under `.cache/huggingface/` (the `hf download --local-dir` lock/metadata
bookkeeping, 5,782 bytes in total, which is exactly the disk check's
observed-minus-design difference). The revision, every pinned size and every LFS
sha256 match. The weights are the pinned weights; the failure is the verifier
counting hub bookkeeping as model files.

Spotlight after the run: corespotlightd 716 `S`, spotlightknowledged 73957 `S`;
no `spotlight-stopped` record. Fence cleared; the R0 LaunchAgent is gone.

Per item 176 (2) R0 is not re-run here; the laptop lead decides.
