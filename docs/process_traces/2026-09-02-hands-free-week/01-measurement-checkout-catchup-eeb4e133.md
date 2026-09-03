# Measurement checkout update + venv relock — executed evidence

**Checkout:** `/Users/edr/JouleWise-measurement-20260813`  
**Date:** 2026-09-02  **Operator:** Opus lieutenant (hands-free, per D-171)  
**Procedure followed:** `docs/process_traces/2026-08-22-t20/real-transaction-runbook.md` §1.1 (the venv relock checklist, D-155 operator fixes) + `docs/phase_2/window_runbook.md` §1 (MEASUREMENT_REPO rules) and §2 (command-surface confirmation).

## Headline

- HEAD **before**: `3c96b18f3f1646ecbeec766e184cf06eface1b8b` ("D-155 W-2: terminal-review membership …")
- HEAD **after**: `eeb4e133815d0c12486d597d9434a2c18c83c1c4` ("D-171: index row")
- Fast-forward only, on `main`, no reset, no branch change, no other checkout touched.
- venv rebuilt from `env/mac-measurement-lock.txt`; **acceptance gate (empty diff) PASSES**, 37/37 lines.
- `reviewed_main` four-way equality: `exact_match: true`, `clean: true`.

## Deviations / things to know (read these)

1. **origin/main had moved past the ruled head.** The brief named `0f9b1be6`; by fetch time `origin/main` was `eeb4e133`. I verified `0f9b1be6` is an **ancestor** of `eeb4e133` and that the only intervening commit is `eeb4e133 "D-171: index row"` (a docs index row). I fast-forwarded to `origin/main` as the documented command literally specifies (`git merge --ff-only origin/main`), because §1.1's four-way-equality predicate requires local `main` == `origin/main`; stopping at `0f9b1be6` would have failed that gate.
2. **The old venv was preserved under a NEW name.** §1.1 step 1 says `mv .venv .venv.pre-v4`, but `.venv.pre-v4` **already existed** (from the 2026-08-27 relock). Following the letter would have destroyed that rollback point, so I used `mv .venv .venv.pre-relock-20260902`. Both rollback environments are intact; both are gitignored (tree still clean).
3. **Three lock-named packages are no longer pulled transitively — I installed them explicitly.** After the canonical `pip install -c env/mac-measurement-lock.txt -e ".[mac]"`, the gate diff showed `charset-normalizer==3.4.8`, `requests==2.34.2`, `urllib3==2.7.0` MISSING (34/37). The lock is a 2026-07-09 `pip freeze` snapshot; today's clean resolution of the same pins does not require `requests` (huggingface_hub 1.22.0 uses `httpx`). §1.1's fallback rule ("stop; do not accept a partial lock") triggers only when a pinned **wheel cannot be obtained** — these were obtainable, so I completed the environment to the lock with `pip install -c <lock> requests==2.34.2 urllib3==2.7.0 charset-normalizer==3.4.8`. Constraints guaranteed no other package moved; the gate then passed 37/37 with an empty diff and `pip check` clean. **Flagging for the magistrate:** if the intent is that the environment be exactly what a clean canonical install produces, the lock file itself is what needs a decision-logged regeneration — not the venv. Also note pip warned `charset-normalizer 3.4.8` is a **yanked** release on PyPI.
4. **The heavy test suite was deliberately NOT run here**, per real-transaction-runbook.md line ~1133: "Not the measurement checkout: the suite is long and heavy and the measurement checkout should be left alone." I ran the documented light checks instead (command surface, imports, doctor).
5. **No `scripts/check_measurement_checkout*` exists** in this checkout — the named verification is the `reviewed_main` exact_match probe, which I ran.
6. Nothing outside the checkout was modified. No sudo. No permission was denied.

## Verbatim transcript

### 1. Pre-state

```
$ git -C /Users/edr/JouleWise-measurement-20260813 status --short --branch
## main...origin/main
$ git -C ... rev-parse HEAD
3c96b18f3f1646ecbeec766e184cf06eface1b8b
$ git -C ... log -1 --format="%h %s"
3c96b18f D-155 W-2: terminal-review membership (both parsers) + window-status freeze-span sentinel (#199)
$ which python3.13 ; python3.13 --version
/opt/homebrew/bin/python3.13
Python 3.13.1
# pre-relock gate against the OLD venv (already in lock):
want lines: 37
(diff empty)  diff exit=0
```

### 2. Fetch + fast-forward

```
$ git -C ... fetch origin
From https://github.com/mpmdw/JouleWise
   3c96b18f..eeb4e133  main                    -> origin/main
   (plus many new remote branches listed; full output 185KB, elided here)
$ git -C ... rev-parse origin/main
eeb4e133815d0c12486d597d9434a2c18c83c1c4
$ git -C ... merge-base --is-ancestor HEAD origin/main ; echo exit=$?
is-ancestor exit=0
$ git -C ... merge --ff-only origin/main
   (Fast-forward; large file list elided)
$ git -C ... rev-parse HEAD ; git -C ... log -1 --format="%h %s"
eeb4e133815d0c12486d597d9434a2c18c83c1c4
eeb4e133 D-171: index row
$ git -C ... status --short --branch
## main...origin/main

# ruled-head ancestry confirmation:
$ git -C ... merge-base --is-ancestor 0f9b1be6 HEAD ; echo exit=$?
exit=0
$ git -C ... log --oneline 0f9b1be6..HEAD
eeb4e133 D-171: index row
$ git -C ... diff --stat 3c96b18f..HEAD -- env/mac-measurement-lock.txt pyproject.toml
(empty — neither the lock nor pyproject changed in the fast-forward)
$ git -C ... status --short ; echo exit=$?
status exit=0   (empty)
```

### 3. venv rebuild (§1.1 D-155 three steps)

```
$ cd /Users/edr/JouleWise-measurement-20260813
$ mv .venv .venv.pre-relock-20260902      # DEVIATION: .venv.pre-v4 already existed
MOVED ok
$ python3.13 -m venv .venv
VENV created
$ .venv/bin/python3 --version
Python 3.13.1
$ .venv/bin/python3 -m pip --version
pip 24.3.1 from /Users/edr/JouleWise-measurement-20260813/.venv/lib/python3.13/site-packages/pip (python 3.13)

$ .venv/bin/python3 -m pip install -c env/mac-measurement-lock.txt -e ".[mac]"
  (tail)
Building wheels for collected packages: joulewise
  Building editable for joulewise (pyproject.toml): finished with status "done"
Successfully built joulewise
Successfully installed MarkupSafe-3.0.3 annotated-doc-0.0.4 anyio-4.14.1 certifi-2026.6.17 click-8.4.2 filelock-3.29.6 fsspec-2026.6.0 h11-0.16.0 hf-xet-1.5.1 httpcore-1.0.9 httpx-0.28.1 huggingface-hub-1.22.0 idna-3.18 jinja2-3.1.6 joulewise-0.1.0 markdown-it-py-4.2.0 mdurl-0.1.2 mlx-0.31.2 mlx-lm-0.31.3 mlx-metal-0.31.2 numpy-2.5.1 packaging-26.2 protobuf-7.35.1 pygments-2.20.0 pyyaml-6.0.3 regex-2026.6.28 rich-15.0.0 safetensors-0.8.0 sentencepiece-0.2.1 shellingham-1.5.4 tokenizers-0.22.2 tqdm-4.68.3 transformers-5.12.1 typer-0.26.8 typing-extensions-4.16.0
PIP_EXIT=0
# note: mlx-metal==0.31.2 — the wheel §1.1 named as the plausible failure — installed fine.
```

### 4. First gate run — FAILED by three packages

```
$ .venv/bin/python3 -m pip freeze --exclude-editable | sort > /tmp/have.txt
$ grep -Ev "^(#|[[:space:]]*$)" env/mac-measurement-lock.txt | sort > /tmp/want.txt
37 /tmp/want.txt
34 /tmp/have.txt
$ diff /tmp/want.txt /tmp/have.txt
4d3
< charset-normalizer==3.4.8
27d25
< requests==2.34.2
37d34
< urllib3==2.7.0
GATE_DIFF_EXIT=1
```

### 5. Completing the environment to the lock

```
$ .venv/bin/python3 -m pip install -c env/mac-measurement-lock.txt requests==2.34.2 urllib3==2.7.0 charset-normalizer==3.4.8
WARNING: The candidate selected for download or install is a yanked version: "charset-normalizer" candidate (version 3.4.8 ...)
Reason for being yanked: <none given>
Installing collected packages: urllib3, charset-normalizer, requests
Successfully installed charset-normalizer-3.4.8 requests-2.34.2 urllib3-2.7.0
PIP_EXIT=0
```

### 6. ACCEPTANCE GATE — re-run, PASSES (freshly executed below)

```
$ .venv/bin/python3 -m pip freeze --exclude-editable | sort > /tmp/have.txt
$ grep -Ev "^(#|[[:space:]]*$)" env/mac-measurement-lock.txt | sort > /tmp/want.txt
want=37 have=37
GATE_DIFF_EXIT=0   <-- 0 = gate satisfied, empty diff

$ .venv/bin/python3 -m pip check
No broken requirements found.
```

### 7. venv verification — imports, provenance, versions (freshly executed)

```
$ .venv/bin/python3 -c "import sys, importlib.metadata as md, mlx.core, mlx_lm, transformers, joulewise; ..."
python 3.13.1
mlx 0.31.2
mlx-lm 0.31.3
mlx-metal 0.31.2
transformers 5.12.1
mlx.core ok: mlx.core
mlx_lm from: /Users/edr/JouleWise-measurement-20260813/.venv/lib/python3.13/site-packages/mlx_lm/__init__.py
joulewise from: /Users/edr/JouleWise-measurement-20260813/joulewise/__init__.py
sys.prefix: /Users/edr/JouleWise-measurement-20260813/.venv
```

Matches §1.1's smoke expectation exactly (`python 3.13.1`, `mlx 0.31.2`, `mlx_lm 0.31.3`, `transformers 5.12.1`). `mlx_lm` resolves from the venv; `joulewise` resolves from the measurement checkout (editable), which is what the runbook's §5C assertion requires.

> Note: `mlx` exposes no `__version__` attribute; version read via `importlib.metadata`. `import mlx` alone is a namespace package — `import mlx.core` is the real check and it passes.

### 8. `reviewed_main` four-way equality probe (freshly executed)

```
$ .venv/bin/python3 -c "import json,sys;from joulewise.arm_readiness import reviewed_main;print(json.dumps(reviewed_main(sys.argv[1]),indent=2))" configs/campaigns/d117_floor_qwen25_1p5b_v3
{
  "head_commit": "eeb4e133815d0c12486d597d9434a2c18c83c1c4",
  "head_tree_oid": "d75a3b806b0bf30e324fd84509acd912d248421e",
  "local_main_commit": "eeb4e133815d0c12486d597d9434a2c18c83c1c4",
  "origin_main_commit": "eeb4e133815d0c12486d597d9434a2c18c83c1c4",
  "clean": true,
  "exact_match": true
}
exit=0
$ .venv/bin/python3 -c "import json,sys;from joulewise.arm_readiness import reviewed_main;print(json.dumps(reviewed_main(sys.argv[1]),indent=2))" configs/campaigns/d117_contrast_v5
{
  "head_commit": "eeb4e133815d0c12486d597d9434a2c18c83c1c4",
  "head_tree_oid": "d75a3b806b0bf30e324fd84509acd912d248421e",
  "local_main_commit": "eeb4e133815d0c12486d597d9434a2c18c83c1c4",
  "origin_main_commit": "eeb4e133815d0c12486d597d9434a2c18c83c1c4",
  "clean": true,
  "exact_match": true
}
exit=0
```

Required by the runbook: `exact_match: true`, `clean: true`, and `head_commit` == the reviewed head. **All three hold**, at `eeb4e133815d0c12486d597d9434a2c18c83c1c4`.

### 9. Command-surface confirmation (window_runbook §2, freshly executed)

```
$ .venv/bin/python3 scripts/run_campaign.py --help   # required options check
--arm-quiet-mode                     PRESENT
--arm-countdown-s                    PRESENT
--log                                PRESENT
--instrument-calibration-dir         PRESENT
--instrument-power-policy            PRESENT
--derive-neg8-drift-bound            PRESENT
--neg8-drift-bound-output            PRESENT
--whole-window-verdict               PRESENT
--neg8-drift-bound                   PRESENT
--bracket-binding                    PRESENT
--whole-window-verdict-output        PRESENT
```

All eleven options the runbook requires (§2 plus the bracket-binding pair) are present on the merged CLI.

### 10. Light smoke — CLI + doctor (freshly executed)

```
$ .venv/bin/python3 -m joulewise --help
usage: joulewise [-h]
                 {validate-config,print-config-schema,print-output-schema,doctor,kv-size,run,validate-bundle,reduce,output-identity-report,analyze-claims,report,envelope-gate,determinism-gate} ...

positional arguments:
cli_exit=0

$ .venv/bin/python3 -m joulewise doctor --json   | head -8
{
  "checks": [
    {
      "details": {
        "acknowledgement": {
          "acknowledged": false,
          "mechanism": null,
          "mode": "inspection",
doctor_exit=0  (runs; reports Apple M3 Max / Mac15,9 / arm64)
```

### 11. Final state (freshly executed)

```
$ git status --short          # must be empty
status_lines=0

$ git status --short --branch
## main...origin/main

$ git rev-parse HEAD
eeb4e133815d0c12486d597d9434a2c18c83c1c4

$ ls -d .venv*
.venv
.venv.pre-relock-20260902
.venv.pre-v4
```

Both preserved environments (`.venv.pre-v4` from the 2026-08-27 relock, `.venv.pre-relock-20260902` from tonight) are gitignored, so the tree is clean. Rollback is one `mv`.

## Anything the checklist asked for that I could not do

- **Nothing was blocked by permissions.** No sudo was needed; no operation was denied.
- **The heavy test suite was intentionally skipped** (documented rule: it belongs in a separate published checkout, not here).
- **CI conclusion check not run.** §1.1 also asks that the reviewed green head be CI-verified via `gh run view <id> --json conclusion`. That is a check on the *reviewed head selection*, made against the development side, and it needs a run id I was not given; it is outside this task's scope (no git ops on other checkouts). **Flagging it as open** for whoever arms the window: `eeb4e133` has not been CI-conclusion-verified by me.
- **The `$BASE` gate ("that head contains none of the `_v4` output")** was not run as a scripted gate, but I observed directly that `configs/campaigns/` contains no `_v4` pack roots at this head — only `_v1`/`_v2`/`_v3` and `d117_contrast_v5`.

---

## Magistrate bench verification (joulewise-60, 2026-09-02 21:03 PDT)

```
$ git -C /Users/edr/JouleWise-measurement-20260813 log --oneline -1
eeb4e133 D-171: index row
$ git -C /Users/edr/JouleWise-measurement-20260813 status --short | wc -l
       0
$ cd /Users/edr/JouleWise-measurement-20260813 && .venv/bin/python3 -c "import joulewise; print(joulewise.__file__)"
/Users/edr/JouleWise-measurement-20260813/joulewise/__init__.py
$ .venv/bin/python3 -c "import mlx_lm; print(mlx_lm.__version__)"
0.31.3
$ diff <(.venv/bin/pip freeze | grep -v -i "^-e\|^joulewise" | sort -f) <(grep -v "^#\|^$\|^-e" env/mac-measurement-lock.txt | sort -f) && echo "sorted lock diff: empty"
sorted lock diff: empty
```

Note for the next arm: the runbook's four-way equality gate (local main == origin/main) means this checkout must be fast-forwarded again immediately before each arm; main had already moved to `b4cc8e50` when this verification ran.
