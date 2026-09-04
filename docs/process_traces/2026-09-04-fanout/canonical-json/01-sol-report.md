# Canonical JSON consolidation report

## Terms

[A] Canonical JSON is a deterministic JSON byte representation: object keys are sorted, spacing is removed, Unicode text remains unescaped when JSON permits it, non-finite numbers are refused, and the result is encoded as UTF-8.

[B] SHA-256 is the hash algorithm used here to map bytes to a fixed-length hexadecimal value.

[C] A digest is that hexadecimal value and serves as a compact check that bytes have not changed.

[D] A re-export is an imported name exposed from its former module so existing callers do not need to change their imports.

[E] Object identity means that names refer to the same Python function object, not merely to functions that currently return equal values.

[F] A fixture corpus is a fixed collection of representative input values and expected results used by a regression test, which is a test that detects the return of a previously removed defect.

## Change

[G] The canonical JSON function used along the claim path now has its implementation in `joulewise/authentication_io.py`.

[H] The former definition sites re-export that function, preserving their public names while making object identity testable.

[I] The fixture corpus pins exact byte strings and the SHA-256 digests recorded before the move.

## Finding and decision table

| Finding | Executed evidence | Decision |
|---|---|---|
| Byte-identical claim-path definitions in the audit-named modules | Pre-move command below produced equal bytes and digests | Keep the implementation in the authentication input/output module and re-export it from the former sites |
| Risk of later divergence between copied functions | New regression compares Python object identity | Assert that every compatibility name is the owner function |
| Risk of changing claim-hash bytes during the move | Fixed corpus contains empty, key-order, nested-Unicode, and finite-number cases | Pin both exact bytes and their pre-move SHA-256 digests |
| Other same-named functions have distinct contracts or belong to other paths | Audit evidence names the claim-path definitions explicitly | Leave those unrelated functions unchanged |

## Executed evidence

[J] Before editing, the following command checked agreement among the old implementations and recorded each fixture's bytes and digest.

```console
python3 - <<'PY'
import hashlib
from joulewise.analysis_engine.artifact import canonical_json_bytes as artifact
from joulewise.analysis_manifest_v3 import canonical_json_bytes as manifest
from joulewise.identity_pins import canonical_json_bytes as identity

fixtures = {
    "empty_object": {},
    "key_order": {"z": 1, "a": 2},
    "nested_unicode": {
        "unicode": "café ☕",
        "nested": {"β": [True, None, "line\nbreak"]},
    },
    "finite_numbers": {"negative": -7, "fraction": 1.25, "zero": 0},
}
for name, value in fixtures.items():
    outputs = [function(value) for function in (identity, manifest, artifact)]
    if not outputs[0] == outputs[1] == outputs[2]:
        raise SystemExit(f"baseline divergence: {name}")
    print(f"{name}\t{outputs[0].decode('utf-8')}\t{hashlib.sha256(outputs[0]).hexdigest()}")
PY
```

[K] The pre-move output was the issued baseline artifact below.

```text
empty_object	{}	44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a
key_order	{"a":2,"z":1}	c2985c5ba6f7d2a55e768f92490ca09388e95bc4cccb9fdf11b15f4d42f93e73
nested_unicode	{"nested":{"β":[true,null,"line\nbreak"]},"unicode":"café ☕"}	e31f8df95c5415b98c966100471b346b6aac0c115083ef52ff25452267f16f89
finite_numbers	{"fraction":1.25,"negative":-7,"zero":0}	1178b0ad096dc037f4ea7f075a5f9da1db032b002ec5ad7c6d1901787c03c8ab
```

[L] After editing, this inspection found the sole claim-path definition at its new owner.

```console
rg -n "def canonical_json_bytes" joulewise/authentication_io.py joulewise/identity_pins.py joulewise/analysis_manifest_v3.py joulewise/analysis_engine/artifact.py
```

```text
joulewise/authentication_io.py:32:def canonical_json_bytes(value: Any) -> bytes:
```

[M] The following focused command ran the new regression and every test module that directly imports a former definition site.

```console
python3 -m unittest tests/test_canonical_json.py tests/test_analysis_claims.py tests/test_analysis_finalizer.py tests/test_analysis_integration.py tests/test_analysis_manifest_v3.py tests/test_analysis_ratio_integration.py tests/test_arm_readiness_evidence_t0.py tests/test_arm_readiness_integration.py tests/test_bracket_binding_cli.py tests/test_check_window_provenance.py tests/test_claims_index_lint.py tests/test_collector_analysis_manifest_id.py tests/test_d117_contrast_v5_pack.py tests/test_d117_decode_contrast_plan.py tests/test_d117_floor_qwen25_1p5b_plan.py tests/test_d117_floor_qwen25_7b_plan.py tests/test_d117_gamma_d139a2_families.py tests/test_d165_dominance_closeout.py tests/test_identity_pins.py tests/test_mint_analysis_admission.py tests/test_night_gate.py tests/test_pipeline_smoke_tail.py
```

```text
----------------------------------------------------------------------
Ran 641 tests in 899.037s

OK (skipped=14)
```

## Verification notes

[N] No repository-wide test suite was run because the issued preflight rule required focused modules only.

## First-use sentence audit

[O] The table below is the mechanical first-use result for every prose sentence marked by a bracketed letter in this report.

| Sentence | New technical term or phrase | First-use result |
|---|---|---|
| A | Canonical JSON; deterministic; Unicode; non-finite numbers; UTF-8 | Defined in the sentence |
| B | SHA-256; hash algorithm; hexadecimal value | Defined in the sentence |
| C | digest | Defined by reference to the preceding definition |
| D | re-export | Defined in the sentence |
| E | object identity; function object | Defined in the sentence |
| F | fixture corpus; regression test; defect | Defined in the sentence |
| G | claim path; implementation | Plain-language use; canonical JSON already defined |
| H | definition site; public name | Plain-language use; re-export and object identity already defined |
| I | byte string | Plain-language use; SHA-256 and digest already defined |
| J | old implementations; fixture | Plain-language use; fixture and digest already defined |
| K | baseline artifact | Plain-language use; artifact means the recorded command output shown immediately below |
| L | owner | Plain-language use for the module containing the implementation |
| M | focused command; test module; direct import | The sentence states the included boundary; re-export and regression test already defined |
| N | repository-wide test suite; preflight rule | The sentence states both the omitted scope and the governing instruction |
| O | mechanical first-use result; prose sentence | The sentence states the audit operation and its complete marked-sentence boundary |

```console
python3 - <<'PY'
import re
from pathlib import Path

path = Path("docs/process_traces/2026-09-04-fanout/canonical-json/01-sol-report.md")
text = path.read_text(encoding="utf-8")
visible = []
in_fence = False
for line in text.splitlines():
    if line.startswith("```"):
        in_fence = not in_fence
        continue
    if in_fence or not line or line.startswith("#") or line.startswith("|"):
        continue
    visible.append(line)
marked = re.findall(r"^\[([A-O])\] (.+)$", "\n".join(visible), re.MULTILINE)
rows = re.findall(r"^\| ([A-O]) \|", text, re.MULTILINE)
expected = list("ABCDEFGHIJKLMNO")
assert [label for label, _ in marked] == expected
assert rows == expected
assert all(sentence.endswith(".") for _, sentence in marked)
assert len(visible) == len(marked)
for label, pattern in {
    "A": r"\bis\b",
    "B": r"\bis\b",
    "C": r"\bis\b.*\bserves as\b",
    "D": r"\bis\b",
    "E": r"\bmeans\b",
    "F": r"\bis\b.*\bwhich is\b",
}.items():
    sentence = dict(marked)[label]
    assert re.search(pattern, sentence)
print("MARKED_SENTENCES=" + ",".join(label for label, _ in marked))
print("AUDIT_ROWS=" + ",".join(rows))
print("FIRST_USE_CHECK=OK")
PY
```

```text
MARKED_SENTENCES=A,B,C,D,E,F,G,H,I,J,K,L,M,N,O
AUDIT_ROWS=A,B,C,D,E,F,G,H,I,J,K,L,M,N,O
FIRST_USE_CHECK=OK
```
