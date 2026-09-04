```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Round-7 fix 2b satisfies the ruled typed-scalar, placement-census, geometry, CLI, and --outt closures; all requested non-replay checks and scratch mutations passed.",
  "workspace": {
    "base_requested": "781c8d78",
    "base_mode": "exact",
    "head_start": "8efbb2007fa4fead3e975cfee52eb4353ff791ec",
    "head_end": "8efbb2007fa4fead3e975cfee52eb4353ff791ec",
    "upstream_end": null,
    "branch": "HEAD (detached)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "CLEAN",
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_paper_round7_artifacts.RegistryAndDigestTests tests.test_paper_round7_artifacts.RefusalTests tests.test_paper_round7_artifacts.TypedArtifactCliTests tests.test_paper_round7_artifacts.InvocationTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 43 tests in 0.809s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 43 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 scripts/check_paper_round7_artifacts.py --literals-only; echo EXIT=$?",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["R7F PLACED 0/16", "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0", "EXIT=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R7F PLACED 0/16.*R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0.*EXIT=0"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "grep -n 'Decimal(str(' scripts/check_paper_round7_artifacts.py; grep -n 'float(' scripts/check_paper_round7_artifacts.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Decimal(str(: no output (grep exit 1)", "570: return float(value)", "604-610: SVG shape.attrib reads and float(\"nan\")"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "no Decimal\\(str\\( and only permitted float sites"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "grep -n 'artifacts\\[\\|pulse\\[\\|resolve_field(' scripts/check_paper_round7_artifacts.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["10 hits; 0 unguarded artifact-scalar reads"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "0 unguarded"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "Scratch-copy mutations M1-M7 and O1-O3 under $TMPDIR/r7audit-*",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["M1-M7 KILLED", "O1-O3 KILLED", "detached-worktree porcelain empty"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "all mutations killed"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The retained-corpus replay and its omitted corpus-gated test class were not run, exactly as directed; the magistrate owns that bench gate.",
      "needs": "Run the full replay at the magistrate bench."
    }
  ]
}
```

## Findings

None.

## Contract lens

| Clause | Production | Biting test | Counterfactual | Verdict |
|---|---|---|---|---|
| A1.1 loader | `scripts/check_paper_round7_artifacts.py:344,788` use `parse_float=Decimal` | `tests/test_paper_round7_artifacts.py:693` | Fractional token `1.0000014999999999999999` would load as `float` and render `1.000002`; it remains Decimal and renders `1.000001`. | INSTALLED |
| A1.2 type-strict comparison | `scripts/check_paper_round7_artifacts.py:171` | `tests/test_paper_round7_artifacts.py:213`, P2 at `:621` | `(True, 1)`, `(True, 1.0)`, and `(1, 1.0)` are mismatches; `Decimal("1")` / `Decimal("1.0")` match. | INSTALLED |
| A1.3 resolver shape and message | `scripts/check_paper_round7_artifacts.py:392`, wrappers `:410,:414`; gate `:547`; failure ID `:510`; pulse leaf `:632` | `tests/test_paper_round7_artifacts.py:221` | Full ruled table is present: all specified rejects and accepts, return types, and byte-exact `SRC#path: expected …, found …` messages. | INSTALLED |
| P1 | Renderer path `checker:429,515-521` | `tests:597` | AQ `max_absolute_pct: "4.046812"` exits 2 and names `row DX-026` / `expected number, found str`. | INSTALLED |
| P2 | `checker:543-556` | `tests:621` | XD gate value `1` exits 2 and names the gate / `expected bool, found int`. | INSTALLED |
| P3 | `checker:621-645` | `tests:646` | XD pulse value `"16.0"` exits 2 and names `figure onset mark 0` / `expected number, found str`. | INSTALLED |
| P4 | `_typed` number branch `checker:395-400` | `tests:670` | JSON integer `4` is accepted as `Decimal(4)` and retains the `4.0 ms` rendering. | INSTALLED |
| Addendum geometry | `_geometry` `checker:568-570`; SVG reads `:604-610` | P3 test `tests:646` | No artifact scalar reaches `float()`; only `_geometry(Decimal)`, SVG attributes, and `float("nan")` do. | INSTALLED |
| A2 parsed 16-ID census | `_placement_row_ids` `checker:701`; `check_placement` `:712`; tail `:949` | `tests:252,736,759,797` | Parsed set is exactly DX-010…017 and DX-020…027; standing+15 markers names DX-027; marker without standing sentence fails; tail order is `PLACED` then `COMPARED`. | INSTALLED |
| A2 checklist disclosures | `docs/paper/round7/fill-checklist.md:29,30` | Literal inspection | Both required census/`PLACED` and deferred-prose-scan sentences are present. | INSTALLED |
| F-7 `--outt` | `_replace_command_value` `checker:832`; F4 argv `:856-858` | `tests:467` | Runtime `--out`→`--outt` is refused as `pinned F4 command must contain exactly one --out`. | INSTALLED |

The `_typed` message is byte-exact at `checker:405-407`:

`f"{field}: expected {kind}, found {type(value).__name__}: {value!r}"`

Comparison-call-site audit: normal literal replay types are all like-for-like: digest/identity/schema/field/render/literal checks are `str/str`; sizes and figure counts are `int/int`; path/gates are `bool/bool`. All remaining calls are intentional failure representations (`int/str` for producer exit or `bool/str` for refused/missing gates). No `Path`/`str`, `int`/`Decimal`, or `Decimal`/`str` legitimate comparison exists.

## Execution lens

`grep -n 'Decimal(str(' …` produced no lines (grep exit 1).

`grep -n 'float(' …` produced only:

    570:    return float(value)
    604:                    x = float(shape.attrib[x_key])
    605:                    y = float(shape.attrib[y_key])
    607:                    x = float(shape.attrib[x_key]) + float(shape.attrib["width"]) / 2.0
    608:                    y = float(shape.attrib[y_key]) + float(shape.attrib["height"]) / 2.0
    610:                positioned.append((float("nan"), float("nan")))

Scalar-read census classifications:

| Line | Classification |
|---|---|
| 348 | (ii) artifact-dictionary population; no scalar read |
| 352 | (i) direct `_typed` schema read |
| 359, 380 | (ii) resolver navigation/existence-only resolution |
| 429 | (ii) navigation feeding renderer wrappers, which call `_typed` |
| 459 | (ii) composite-dictionary navigation; scalar leaves at 465/466/468 are typed |
| 548 | (i) direct resolver result passed to `_typed` |
| 590 | (ii) per-pulse list navigation; leaf at 633 is typed |
| 627, 635 | (ii)/(i): label only, then direct typed pulse scalar |

There are zero unguarded artifact-scalar reads.

Scratch-copy mutation results:

| Probe | Result |
|---|---|
| M1 `_comparison` restored to equality only | KILLED by `RegistryAndDigestTests.test_comparison_requires_identical_python_types` and P2’s initial strict-comparison assertion: `AssertionError: True is not false`. |
| M2 remove loader `parse_float=Decimal` | KILLED by `TypedArtifactCliTests.test_decimal_loader_preserves_fixed_literal_across_float_roundtrip_edge`: loaded type was `float`, not `Decimal`. |
| M3 permit `str` as number | KILLED by resolver table and P1: no `ValueError`; P1 checker returned `0`, expected `2`. |
| M4 per-pulse coercion via `float()` | KILLED by P3: checker returned `0`, expected `2`. |
| M5 source command `--out`→`--outt` | KILLED during `RefusalTests` setup: `RegistryError: DX-003 must carry the exact full F4 replay command including --svg`. The dedicated F-7 test independently injects this mutation in-memory and passes on the landed bytes. |
| M6 remove standing-sentence branch | KILLED by `test_current_skeleton_passes_zero_placement_census`: observed 16 comparisons, expected 1. |
| M7 alter standing head by one character | KILLED by `test_standing_sentence_head_is_pinned_to_the_registry`. |
| O1 permit bool as number | KILLED by resolver table: `ValueError not raised` for `number, True`. |
| O2 swallow gate refusal as `True` | KILLED by P2: checker returned `0`, expected `2`. |
| O3 print `PLACED` after comparison tail | KILLED by `InvocationTests.test_literals_only_cli_passes`: penultimate line became the `COMPARED` tail. |

## Same-signature lens

This is structurally closed. Every artifact scalar either reaches `_typed` directly or is structural dict/list navigation whose consumed leaf is typed; the loader prevents JSON fractional floats, and comparison is type-strict. A third round on “scalar reads coerce instead of refuse” is structurally impossible. No remaining coercing read exists; therefore no standing escalation is triggered.

## Executed evidence

`python3 -m unittest tests.test_paper_round7_artifacts.RegistryAndDigestTests tests.test_paper_round7_artifacts.RefusalTests tests.test_paper_round7_artifacts.TypedArtifactCliTests tests.test_paper_round7_artifacts.InvocationTests`

    Ran 43 tests in 0.809s
    OK
    EXIT=0

`python3 scripts/check_paper_round7_artifacts.py --literals-only; echo EXIT=$?`

    R7F PLACED 0/16
    R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0
    EXIT=0

`git diff --check 781c8d78 8efbb200`

    EXIT=0

Scratch mutations and all targeted tests used `$TMPDIR/r7audit-*`; no repository files were mutated.

## Residual risk

The directed full retained-corpus replay remains for the magistrate bench.

VERDICT: CLEAN

`git status --porcelain`

    (empty)