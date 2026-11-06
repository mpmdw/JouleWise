# qwen4_exp port r2: when and how it replaces the Saturday pin

Port r2 (`lane/2026-11-06-qwen4exp-port-r2`) merges the two reviewed port
lanes: MISSING-11 compiled decode (`lane/2026-11-06-sol-qwen4exp-compiled-decode`
at `4383e89d7`) and MISSING-12 maxfit4 contingency profile
(`lane/2026-11-06-sol-qwen4exp-maxfit4` at `7200b076c`). The merged
`joulewise/align/models/qwen4_exp.py` is sha256
`c3d4a0bf8d137c6673f1c7e3f92745f9ce45d223e55566704ba27fc4365783bb`
(`MODULE_SHA256` in `scripts/align_convert_qwen4_exp.py`; canonical.md "Pin").

## The Saturday pin stays

`lane/2026-11-06-sat-kit-integrated` (checked at `32392612d` and again at `bb921a127`) pins the
round-1 module, sha256
`f4ec75d16f0af0517b63e202abeef704c9a775e9111949ab003250d51d982c37`, in three
places: the file itself, `MODULE_SHA256` in
`scripts/align_convert_qwen4_exp.py`, and the record in canonical.md "Pin"
(`docs/run_reports/2026-11-06-qwen4exp-synthetic-artifact.md` also cites it).
Port r2 does not touch that branch. The Saturday live tests run on `f4ec75d1`.

## When

Not before the Saturday live tests are finished and their results are
recorded against `f4ec75d1`. Swapping the module mid-run would mix two
modules in one result set. Port r2 is adopted only in a kit revision made
after that, as a cited rebind of the kit's pin.

## How

1. Merge port r2 into the post-Saturday kit branch. The kit's
   `MODULE_SHA256` and canonical.md "Pin" become `c3d4a0bf…` (the suite fails
   `test_r1_load_verified_model_requires_both_pins` if they disagree). Update
   the synthetic-artifact report's module citation at the same time.
2. Gate natively on the pinned venv (mlx 0.31.2 / mlx-lm 0.31.3), as listed
   under "MISSING-11 compiled decode boundary" in canonical.md:
   `python -m unittest -v tests.align.test_qwen4_exp_canonical`, then the
   kit's step-8 gold-adapter tiny command, then its step-8 live tiny command.
3. Artifacts carry their own copy of `qwen4_exp.py`, so existing maxfit /
   maxfit5 artifacts do not pick up the change. Do not reconvert: copy the
   artifact directory, replace only `qwen4_exp.py`, write a new
   `manifest.json` whose `files["qwen4_exp.py"]` and `module_sha256` are
   `c3d4a0bf…`, and record the new manifest sha256 externally. Weight and
   table payloads are unchanged. A maxfit4 artifact does not exist yet and
   needs a fresh conversion with `--profile maxfit4`.
4. Re-attest gold units against the new manifest/module pair. The compiled
   decode path is bitwise-equal to eager on the fixture; `compile_decode:
   false` in `config.json` (or the `model_config` override) is the
   bitwise-reference switch if a live comparison is needed.
