```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"clean","completion":"complete","summary":"Implemented all accepted ruling 163a contract and sidecar-test fixes with green named tests and a killed sidecar mutant.","workspace":{"base_requested":"a37b0b9f","base_mode":"exact","head_start":"a37b0b9f72928e345739c8ef88a28b4198dd1133","head_end":"a37b0b9f72928e345739c8ef88a28b4198dd1133","upstream_end":null,"branch":null},"pathspec":["docs/contracts/identity_pin_projection.md","tests/test_identity_pins.py"],"unowned_dirty":["docs/contracts/identity_pin_projection.md (pre-existing untracked draft at intake; edited under WRITE_SCOPE)"],"verdict":{"implementation":"implemented","acceptance":"ready"},"verification":[{"id":"V1","kind":"suite","cmd":"TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/proj02-fix-170 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_identity_pins","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 35 tests in 6.757s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 35 tests in .*s\\s+OK"}},{"id":"V2","kind":"test","cmd":"TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/proj02-fix-170 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_identity_pins.ProjectionLifecycleTests.test_freeze_writes_authenticated_exact_key_receipt_and_is_idempotent","cwd":"/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/proj02-fix-170/mutant","observed":{"result":"pass","exit_code":1,"tail":["AssertionError: IdentityPinProjectionError not raised","Ran 1 test in 0.158s","FAILED (failures=1)"]},"expected":{"exit_code":1,"tail_regex":"IdentityPinProjectionError not raised[\\s\\S]*FAILED \\(failures=1\\)"}},{"id":"V3","kind":"inspection","cmd":"git diff --check && git status --porcelain && git rev-parse HEAD && git branch --show-current","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[" M tests/test_identity_pins.py","?? docs/contracts/identity_pin_projection.md","a37b0b9f72928e345739c8ef88a28b4198dd1133"]},"expected":{"exit_code":0,"tail_regex":" M tests/test_identity_pins.py\\n\\?\\? docs/contracts/identity_pin_projection.md\\na37b0b9f.*"}}],"flags":[]}
```

## Change

| Ruling | Implementation |
|---|---|
| R-163-1 | Added the complete eight-key unprojected envelope, nested unit/supersession shapes, null pins/receipt rules, and validated pasteable example at doc lines 142–214. |
| R-163-2 | Added the exact executable tag predicate and discarded-metadata rule at lines 17–25, 48–69, and 313–320. |
| R-163-3 | Added both raw files, normalized identity, eleven-field stack, recomputable hashes, and `TOY\n`→`TOZ\n` arm refusal at lines 545–671. |
| R-163-4 | Asserted exact sidecar bytes and one-hex-digit mutated-sidecar refusal with pack preservation at test lines 569–597. |
| R-163-5 | Preserved the no-test map row and documented the scheduled boundary move at doc lines 455–468 and 731–735. |
| R-163-6 | Reworked first uses throughout and moved policy/subsystem labels to the closing provenance note. |

### First-use walk

| First occurrence | Term(s) | Result |
|---:|---|---|
| 9–25 | identity-pin projection, tokenizer/runtime behavior, identity pins, SHA-256, normalized scientific configuration | BUILT |
| 27–44 | campaign pack, floor mint/artifact, freezing, unprojected/frozen, authenticated receipt | BUILT |
| 48–69 | scientific workload and every removed/retained tag predicate | BUILT |
| 70–77 | identity unit, quantization, declaration | GLOSSED |
| 78–93 | inventories, lexical ordering, followed bytes, symbolic link, prepare/probe/cleanup, measured member | BUILT |
| 94–109 | prompt expectation/domain/count, realization, canonical JSON, projection input | BUILT |
| 110–140 | freeze/arm, PASS/REFUSE, drift/dirty/unreadable, custody/check, shared mint, re-derive/replay, idempotence, sidecar | BUILT |
| 144–214 | mode, required-before-arm, null pins/receipt, supersession and unit envelope | BUILT |
| 217–333 | model-artifact shapes, model-root-relative POSIX paths, NUL, probe metadata, allowlist, eleven stack fields | BUILT |
| 337–374 | encoder, `TypeError`, Python `finally` | GLOSSED |
| 380–405 | producer contract, mint Git anchor, derivation identity, GNU sidecar form, durable writes | BUILT |
| 409–453 | path-safe ID, committed checkout/successor, readiness mapper | BUILT |
| 457–478 | launch manifest, consumption record, `execve`, succeeded bundle, assurance boundary | BUILT |
| 480–671 | receipt/refusal schema, raw-byte preimages, canonical stack, non-happy paths | BUILT |
| 672–707 | every diagram box and arrow | BUILT |
| 737–748 | rulings, D-119/D-131, U8/U11 | GLOSSED |

Zero FAILS.

## Verification notes

Hash recomputation command:

```sh
TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/proj02-fix-170 \
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python - <<'PY'
import hashlib, json, os
from pathlib import Path
from joulewise.identity_pins import canonical_json_bytes, canonical_json_sha256, scientific_config_identity, scientific_config_identity_sha256, stack_identity_sha256, validate_identity_pin_projection
text=Path("docs/contracts/identity_pin_projection.md").read_text(); lines=text.splitlines()
raw=[x for x in lines if x.startswith('{"hardware_target":{"id":"example-mac"')][:2]
paths=[Path(os.environ["TMPDIR"])/f"member-{n}.json" for n in (1,2)]
for path,line in zip(paths,raw): path.write_bytes((line+"\n").encode())
configs=[json.loads(path.read_bytes()) for path in paths]
identities=[scientific_config_identity(c) for c in configs]; assert identities[0]==identities[1]
stack=json.loads(next(x for x in lines if x.startswith('{"batching_concurrency_policy":')))
projection=json.loads(next(x for x in lines if x.startswith('[{"config_inventory":')))
print("raw",*[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths])
print("config",scientific_config_identity_sha256(configs[0]))
print("runtime",stack_identity_sha256(stack))
print("projection",canonical_json_sha256(projection))
print("model",hashlib.sha256(b"TOY\n").hexdigest())
print("model_changed",hashlib.sha256(b"TOZ\n").hexdigest())
PY
```

```text
raw 5bee74bfc11a663e7b4c364d24c33883930438a60d126d99ab400a4e7cfa9805 bca6b55f312abf6783a5eed1297c9d45de2f86e9197f60394d4f16dca95400b0
config 95367df3b83bf6995b5d054f5d21114744b14614b999071a801b3189c107c019
runtime e2dc2bd8a10f4f4029443d824ed21756d5d3146671998b12324d7791685c4e36
projection 6d3a16628cdda16cfd1b0bc3fba680b600e5e25e15f606986aa9ed92967fd1cd
model 6361d8e661d28948e82e68ed04a7d5becdc39bc6a94176bd805003b90991fdfb
model_changed 89da779ae2224b826aee3408c1a107cede3bc2e3c4089c80ea81bfde592eb14f
```

Mutant tail after disabling only `_load_frozen_receipt`’s sidecar comparison:

```text
AssertionError: IdentityPinProjectionError not raised
----------------------------------------------------------------------
Ran 1 test in 0.158s

FAILED (failures=1)
```

Named suite: 35 tests, OK. Workspace status contains exactly the two WRITE_SCOPE paths.