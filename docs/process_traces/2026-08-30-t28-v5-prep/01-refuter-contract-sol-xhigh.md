```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Two implementation blockers and one pre-freeze ruling blocker refute pack-prep completeness; the replay registration exists but its executable proof is incomplete.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "exact",
    "head_start": "5e477f656a4ff6debba27be3bb7d377fedcc0af2",
    "head_end": "5e477f656a4ff6debba27be3bb7d377fedcc0af2",
    "upstream_end": "619c826cdd8ee48b225d7ebbb0b09969ca82d6eb",
    "branch": "feat/v5-ladder-prep"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "questions": {
      "Q1": "holds",
      "Q2": "fails",
      "Q3": "holds-with-caveat",
      "Q4": "holds",
      "Q5": "fails",
      "R5": "needs-ruling"
    },
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The D-165 golden read-back is self-referential and does not freeze the registration",
        "evidence": [
          "configs/campaigns/d117_contrast_v5/generate_configs.py:456-546",
          "tests/test_d117_contrast_v5_pack.py:233-243",
          "tests/test_d117_contrast_v5_pack.py:298-316"
        ],
        "refutation": "Change all_must_pass to false, or lower DOMINANCE_THRESHOLD and its emitted value to 1.9. The registration-to-registration equality, semantics rehash, R==2 passing assertion, and zero-denominator assertion still pass."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "Tokenizer and template hashes are checked only against other declarations in the same panel",
        "evidence": [
          "joulewise/model_panel.py:562-617",
          "configs/campaigns/d117_contrast_v5/generate_configs.py:808-850",
          "tests/test_d117_contrast_v5_pack.py:177-201"
        ],
        "refutation": "Drift either local model's tokenizer.json or embedded chat template while leaving the panel unchanged. Generation still proceeds because it deliberately never reads the model mirror."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "Absolute-component R_cm is undefined by the registered comparative-only replay",
        "evidence": [
          "configs/campaigns/d117_contrast_v5/generate_configs.py:473-505",
          "configs/campaigns/d117_contrast_v5/generate_configs.py:629-645",
          "joulewise/floor_extraction.py:2280-2293",
          "joulewise/floor_extraction.py:2724-2745"
        ],
        "refutation": "There is no accepted mapping from an absolute cell's member energies and independent member widths to the replay's ABBA block-delta/sweep schema. Reusing the function necessarily invokes comparative_false_effect_floor and changes the estimand."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "The replay proof does not enforce the registered authentication fence and is only partially independent",
        "evidence": [
          "configs/campaigns/d117_contrast_v5/generate_configs.py:498-510",
          "configs/campaigns/d117_contrast_v5/generate_configs.py:556-645",
          "joulewise/floor_extraction.py:535-550",
          "joulewise/floor_extraction.py:577-610",
          "tests/test_d117_contrast_v5_pack.py:57-107"
        ],
        "refutation": "A replay with shared_edge_bound_s=0, zero_point_contrast_j=999 absent from one-element onset/offset sweeps, and deltas ±1 was accepted and returned R_cm=138.18123380775342; the governed floor path rejects those preconditions."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --check HEAD^ HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --exit-code HEAD^ HEAD -- joulewise/detection_floor.py joulewise/floor_extraction.py joulewise/floor_mint_estimator.py configs/floor_mint tests/test_d117_decode_contrast_plan.py configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## feat/v5-ladder-prep...origin/feat/v5-ladder-prep"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## feat/v5-ladder-prep"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d117_contrast_v5_pack",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found",
          "FAILED (errors=3)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "D-165 R-5 requires an explicit disposition for absolute-component R_cm before the v5 freeze.",
      "needs": "Rule absolute R_cm not-applicable with a cancellation reason, or define a new versioned absolute replay quantity and its distinct interpretation."
    },
    {
      "id": "FL2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The read-only sandbox exposes no writable temporary directory, so tempfile-based focused and canonical suites could not execute.",
      "needs": "Runner should replay the focused and canonical suites in its normal writable test environment."
    }
  ]
}
```

## Findings

### BLOCKER F1 — The “golden read-back” is tautological

The cold gate requires either a frozen implementation that reads the manifest’s threshold/definition or a golden test independently pinning the emitted object (`06-COLD-GATE-RULING.md:91-95`).

Neither exists:

- The registration and evaluator share generator-local constants at `generate_configs.py:456-546`.
- The pack test derives `expected` from `dominance_criterion_registration()` and compares it with another call to the same function at `tests/test_d117_contrast_v5_pack.py:233-235`.
- The named golden repeats that self-comparison at `:298-305`; it tests only that R=2 currently passes and the current zero reason raises at `:306-316`.

Refutation path: change `"all_must_pass"` to `false`, or change both threshold declaration and implementation to `1.9`. The existing “golden,” semantics rehash, R=2 assertion, and zero-denominator assertion remain green. The registered falsifier can therefore drift while its tests approve the drift.

### BLOCKER F2 — Panel pins are declared, not generation-time enforced

`load_model_panel` explicitly loads without probing the named model mirror (`joulewise/model_panel.py:562-617`). Generation then checks:

- model A’s declared hash against model B’s declared hash;
- the panel entry’s declared hash against the panel pinset’s declared hash;

at `generate_configs.py:808-850`.

The test positively enforces the absence of model-mirror reads at `tests/test_d117_contrast_v5_pack.py:177-201`.

Refutation path: alter the local `tokenizer.json` or model-carried chat template while leaving the panel unchanged. Generation cannot detect the drift. The runtime consumes the pre-rendered IDs directly (`generate_configs.py:1325-1334`; `mlx_runtime.py:886-888`), which preserves the declared ID sequence but does not prove that those IDs were derived from the presently pinned tokenizer/template/model bytes. This is the D-157 “contract input with no check” class.

### BLOCKER F3 — Absolute R_cm has no registered meaning

The registration declares `"kind": "comparative"` and references only `comparative_false_effect_floor` (`generate_configs.py:473-505`). Its executable replay likewise always calls the comparative estimator (`:629-645`).

The actual absolute path instead sends member values and independent member widths to `absolute_false_effect_floor` (`floor_extraction.py:2280-2293`). It does not produce ABBA block sweeps or a shared/local decomposition. Only the comparative path invokes the governed common-mode machinery (`:2724-2745`).

Consequently, an absolute component cannot be evaluated by the emitted replay without silently changing its estimand.

### SHOULD-FIX F4 — Route (ii) is registered, but its executable proof is not fence-complete

The emitted object does contain the required rule identity, input-field list, replay fence, and formula references at `generate_configs.py:498-510`. That part is real registration.

The executable helper, however, omits governed preconditions:

- The production path requires a positive operative bound authenticated against the calibration bracket (`floor_extraction.py:535-545`).
- It requires each zero point to appear exactly in both sweeps and approximately equal its block delta (`:577-610`).
- The replay helper accepts a zero bound and does not enforce either zero-point condition (`generate_configs.py:603-626`).

The “independent” test independently reimplements split and corner enumeration, but both sides call the same production `comparative_false_effect_floor` (`tests/test_d117_contrast_v5_pack.py:88-107`; generator `:629-645`). It is therefore independent only for the split/enumeration layer, not the entire registered arithmetic.

## Contract-lens holdings

- **Q1 — HOLDS.** The new object appears only in generator-emitted comparative-contrast dictionaries at `generate_configs.py:1649`, `:1668`, and `:2277`. The producer remains canonical at `detection_floor.py:483-536`; `COMMON_MODE_PARAMETER_SHA256` remains unchanged at `:178`. The six issued extraction specs are byte-identical across the commit and their 18 registrations still equal the canonical producer; their first registrations are at each file’s line 202. The committed `_v1` equality assertion remains unchanged at `tests/test_d117_decode_contrast_plan.py:2270-2285`. The combined Git-object inventory of the six specs, test, and `_v1` pack was identical before/after (`e5052a51…`).

- **Q2 — FAILS.** The emitted object contains the ruled operands, unguarded/unguarded basis, threshold, exact-equality text, per-component flag, all-pass rule, mixed null framing, and named zero-denominator refusal (`generate_configs.py:476-513`). But the required read-back enforcement is absent; F1 refutes the golden.

- **Q3 — HOLDS-WITH-CAVEAT.** Route (ii) is materially registered, not merely named. The fixture separately implements the shared/local split and sign enumeration. It shares the comparative floor primitive, however, and the executable helper does not enforce its claimed authenticated-input fence; see F4.

- **Q4 — HOLDS.** The supported set is closed at `analysis_manifest_v3.py:322-324`. Exactly one non-decode condition arm must resolve into that set (`:2119-2138`), otherwise the exact four-slot cover refuses (`:2139-2146`). Contrast condition identities must match the derived arm (`:2400-2412`), and the final arm set must equal decode plus that same prefill arm (`:2619-2630`). Zero non-decode arms, two arms, unsupported/case-variant arms, condition/contrast disagreement, and contrast-only arms all reached `analysis_prospective_contrast_cover_mismatch` in read-only in-memory probes. The refusal-code set itself is unchanged (`:303-324`); only existing-code details changed. The semantic projection is unchanged (`:1534-1555`), and finalized replay still delegates to prospective validation (`:3916-3942`). Pre/post validation of all three committed `_v1`/`_v2`/`_v3` manifests produced identical refusal tuples.

- **Q5 — FAILS.** The panel proves only internal declaration consistency. It never proves those hashes against the actual tokenizer/template bytes used by the selected model installation. The path in F2 permits generation after external drift.

## D-165 R-5 bench check

### (a) Is absolute R_cm defined under the registered rule?

**No.** The registered input domain is comparative ABBA blocks, and the registered formula ends in `comparative_false_effect_floor`. Absolute extraction supplies neither those block records nor the required shared/local split.

A natural mathematical extension can be written, but it is not the registered rule.

For absolute member energies \(x_i\), let

\[
\bar{x}=\frac1n\sum_i x_i,\qquad r_i=x_i-\bar{x}.
\]

The absolute point floor uses residuals \(r_i\), not raw energies (`detection_floor.py:917-926`). For a genuinely common shift \(c\),

\[
r_i'=(x_i+c)-(\bar{x}+c)=x_i-\bar{x}=r_i.
\]

The maximum absolute residual, residual standard deviation, and Student-t prediction component are therefore unchanged. A uniform shared shift cancels exactly.

With local perturbations \(e_i\),

\[
r_i' = r_i + e_i-\bar e,
\]

so only the centered local residuals affect the widened absolute floor.

### (b) Does that measure the same quantity as comparative R_cm?

**No.** The comparative estimator deliberately does not recenter its deltas (`detection_floor.py:950-969`). For block delta \(d_i\),

\[
F_{\mathrm{cmp}}(d)=
\max\left(
\max_i |d_i|,
|\bar d|+t\,s(d)\sqrt{1+1/n}
\right).
\]

Under a common shift \(c\),

\[
d_i'=d_i+c,\qquad \bar d'=\bar d+c.
\]

Both \(\max|d_i+c|\) and the \(|\bar d+c|\) term can change. With the registered block-specific shared widths \(s_i\), the replay enumerates

\[
d_i' = d_i+\sigma s_i+\tau_i\ell_i,
\]

with one shared sign \(\sigma\) and independent local signs \(\tau_i\) (`generate_configs.py:633-645`). Unequal \(s_i\) can also change scatter.

Thus comparative R_cm measures sensitivity to the shared-fiducial treatment. A hypothetical absolute ratio would collapse to a local-residual diagnostic after the common shift cancels. Calling both values R_cm would conflate different quantities.

### (c) Required registration disposition

**Register the absolute component as not applicable, with the reason.**

Recommended ruled meaning:

- Absolute independent-corner R remains reportable.
- Absolute R_cm: `not_applicable`.
- Reason: the absolute estimator is deviations-from-mean; a uniform shared fiducial shift cancels exactly, and route (ii) is registered only for comparative ABBA block inputs.
- Comparative R_cm remains mandatory and retains the `< 2` withdrawal rule.

If a local-only absolute diagnostic is desired, it needs a distinct versioned name and a caveat that it is not the comparative shared-fiducial-dominance quantity. This is the remaining D-165 R-5 NEEDS-RULING item before freeze.

## Residual risk

The read-only environment provides no writable temporary directory, so tempfile-dependent focused tests and the canonical suite could not run. The failures observed were environmental, not assertion failures. The worktree remained clean.