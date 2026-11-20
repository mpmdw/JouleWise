# 2026-11-20 · Stability pair review exhibits

Tier 0 documentary work for the later paired cold pass. The [review
exhibits](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/stability-pair-review-exhibits.md)
carry the public kit identity and positional comparison, hand cases, and
the per-manifest source and owner matrix.

## Intake and findings

Mission M0 used the public status snapshot through item 483 and the current
pointer on the target branch `audit/2026-11-10-fable` at
`d6016f406496ac4d0c82f70811da2a5bab82ea35`. The active stop-card pointer
was null. The measurement pointer belongs to the magistrate. This work
used the agent-compatible documentary lane at the user's direction.
The clean worktree was already at the target tip and the named branch
`cadence/2026-11-20-stability-paired-review-exhibits` had no remote ref at intake.

| Finding | Focused check | Result |
| --- | --- | --- |
| The committed index has 14 base kits on `2d347f721` and two extensions on `6e9d42f1d`. | Compare all 16 exhibit rows and file bytes to the index and filler registry. Check that the base 14 alone match the look commitments and the draft. | PASS |
| The 16 kits preserve the positional layout of `f2-inst-01`. The two extensions change frozen runner provenance as well as the design identity and seeds. | Compare each parsed design after accounting for the exact declared differences. | PASS |
| The first-read draft still has the old coalescence and receipt chronology. The companion file is absent at the target snapshot. | Check draft and index bytes on pinned refs, companion path absence, and the matrix against RL-190 §§1.3 and 1.5. | PASS |
| The six public fields and the two private views survive the later rulings. | Hand-check the seven invented cuts against RL-181, RL-190, RL-192b and the v3 DELTA's one- and thirteen-date expected counts. Read the manifest matrix against the draft release inventory. | PASS (documentary) |
| Sources resolve at their cited revisions. | Verify the exhibit's 30 pinned Git object links, object types and cited line bounds. | PASS |

Sources were the audit ruling and index at `04d8aa778`, the public draft
and registries at `c05bcfc45`, and the requested MANIFEST-GAPS, PACKET and
v3 DELTA text. The DELTA reports the older replay's early-lock refusals.
The hand cases give the ruled outcomes. Successor executable verification
remains with PR #868. Focused checks fit this two-Markdown-file diff.
The local full suite was omitted for this documentary scope.

## Reproduce the public design checks

Run from the worktree root with the pinned public refs available. The
commands read only the exhibit and the named public design and source
records. They compare committed bytes without running the executor.

```sh
git diff --check d6016f406
python3 -B - <<'PY'
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
from subprocess import check_output

audit = "04d8aa778"
main = "c05bcfc45"
target = "d6016f406"
ev = "docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign"
looks = "docs/process/cadence/looks"

def blob(ref, path):
    return check_output(["git", "show", f"{ref}:{path}"])

index_path = f"{ev}/f2-stab/KITS.json"
index_bytes = blob(audit, index_path)
assert blob(target, index_path) == index_bytes
assert sha256(index_bytes).hexdigest() == (
    "9fd3d49c0a51ab75a1c4e20fb784f9f656fb70e9cfca8e2b9ff304c0eba70dae"
)
index = json.loads(index_bytes)
rows = index["rows"]
ids = [f"f2-stab-{i:02}" for i in range(1, 17)]
assert index["base_kits"] == ids[:14]
assert [row["kit_id"] for row in rows] == ids
base_ids = set(ids[:14])
all_ids = set(ids)

def stable_registry(name):
    path = f"{looks}/{name}"
    data = blob(main, path)
    assert blob(audit, path) == blob(target, path) == data
    return json.loads(data)

filler = stable_registry("filler-kit-registry.json")["kit_sha256_by_id"]
commitments = stable_registry("look-kit-commitments.v2.json")
digests = {row["kit_id"]: row["sha256"] for row in rows}
base_digests = {kit_id: digests[kit_id] for kit_id in ids[:14]}
assert {k: v for k, v in filler.items() if k.startswith("f2-stab-")} == digests
assert commitments["lm-stab-01"]["kit_sha256_by_id"] == base_digests
assert "lm-stab-02" not in commitments

draft_path = f"{ev}/looks/lm-stab-01.manifest.json"
draft_bytes = blob(main, draft_path)
assert blob(target, draft_path) == draft_bytes
draft = json.loads(draft_bytes)
assert draft["status"] == "draft"
assert len(draft["kits"]) == 14
assert {row["kit_id"]: row["sha256"] for row in draft["kits"]} == base_digests
assert len(draft["code_pins"]) == 8
assert all(pin["sha256"] == "PENDING:CODE" for pin in draft["code_pins"].values())
pub = draft["outputs"]
assert pub["public_file"] == "PUBLIC.json"
assert pub["identifiers"] + pub["hashes"] + pub["counts"] == [
    "look_id", "commit", "manifest_sha256", "stage1_sha256", "n_legs", "n_local_dates",
]
assert not check_output([
    "git", "ls-tree", target, "--", f"{ev}/looks/lm-stab-02.manifest.json",
])

instrument_path = f"{ev}/item-drafts-f2/f2-inst-01.v1.1.json"
instrument_bytes = blob(audit, instrument_path)
instrument_digest = sha256(instrument_bytes).hexdigest()
assert instrument_digest == (
    "651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b"
)
assert filler["f2-inst-01"] == commitments["lm-inst-01"]["kit_sha256_by_id"][
    "f2-inst-01"
] == instrument_digest
instrument = json.loads(instrument_bytes)
assert [leg["leg_id"] for leg in instrument["legs"]] == [
    f"L{i:03}" for i in range(1, 13)
]
assert [leg["prefill_tokens"] for leg in instrument["legs"]] == [
    19458, 256, 2000, 2000, 256, 19458, 256, 2000, 19458, 2000, 19458, 256,
]
assert all(
    (leg["decode_tokens"], leg["g0_shape"], leg["start_band"]) == (512, "own", "q600")
    for leg in instrument["legs"]
)

exhibit = Path(f"{ev}/stability-pair-review-exhibits.md").read_text(encoding="utf-8")
printed = re.findall(
    r"^\| `(f2-stab-\d\d)` \| `([0-9a-f]{9})` \| `([^`]+)` "
    r"\| `([0-9a-f]{64})` \| (\d+) \|$",
    exhibit, re.MULTILINE,
)
assert [row[0] for row in printed] == ids
design = blob(audit, f"{ev}/f2-stab/MANIFEST.md").decode()
pins = {
    "2d347f721": "2d347f721552fe03bdd19f113e7bad7a7c24908e",
    "6e9d42f1d": "6e9d42f1dd3d308bc9239143d0d634ab965e50e1",
}
assert instrument["frozen"]["commit"] == pins["2d347f721"]
extension_frozen = None
seeds_by_position = [set() for leg in instrument["legs"]]
for row, exhibit_row in zip(rows, printed, strict=True):
    kit_id = row["kit_id"]
    is_base = kit_id in base_ids
    pin = "2d347f721" if is_base else "6e9d42f1d"
    directory = "f2-stab" if is_base else "f2-stab/qual-pin"
    relative = f"{directory}/{kit_id}.v1.1.json"
    assert row["runner_pin"] == pin
    assert row["path"] == f"{ev}/{relative}"
    data = blob(audit, row["path"])
    assert blob(target, row["path"]) == data
    assert sha256(data).hexdigest() == row["sha256"]
    kit = json.loads(data)
    seed = kit["seed_law"]["master_seed"]
    assert exhibit_row == (kit_id, pin, relative, row["sha256"], str(seed))
    candidates = seed - 2026111444 + 1
    design_row = next(line for line in design.splitlines() if line.startswith(f"| [{kit_id}]"))
    assert f"`{row['sha256']}` | `{pins[pin]}` | {seed} | {candidates} | 0 |" in design_row

    assert kit["campaign_id"] == kit_id and kit["ruling"]["id"] == "RL-179"
    assert seed != instrument["seed_law"]["master_seed"]
    assert kit["frozen"]["commit"] == pins[pin]
    comparable = deepcopy(kit)
    comparable["campaign_id"] = instrument["campaign_id"]
    comparable["ruling"]["id"] = instrument["ruling"]["id"]
    comparable["seed_law"]["master_seed"] = instrument["seed_law"]["master_seed"]
    for position, (leg, original) in enumerate(
        zip(comparable["legs"], instrument["legs"], strict=True)
    ):
        assert leg["seed"] != original["seed"]
        assert leg["seed"] not in seeds_by_position[position]
        seeds_by_position[position].add(leg["seed"])
        leg["seed"] = original["seed"]
    if not is_base:
        frozen = kit["frozen"]
        assert frozen.keys() == instrument["frozen"].keys()
        expected_paths = instrument["frozen"]["paths"]
        assert len(frozen["paths"]) == 38 and frozen["paths"].keys() == expected_paths.keys()
        assert sum(frozen["paths"][path] != digest for path, digest in expected_paths.items()) == 7
        if extension_frozen is None:
            extension_frozen = frozen
        assert frozen == extension_frozen
        comparable["frozen"] = instrument["frozen"]
    assert comparable == instrument, kit_id

assert len(all_ids - base_ids) == 2
print("PASS: 14 base + 2 extensions, all kit and index SHA-256 links, both registries,")
print("      positional differences, main draft inventory and target companion absence")
PY
```

## Publication and remaining owner inputs

Draft [PR #915][pr] targets `audit/2026-11-10-fable`. GitHub confirmed the
initial head `b1a0892af07b1420208da78ed890d3c2f882fa1d` and base
`d6016f406496ac4d0c82f70811da2a5bab82ea35`, with exactly the two authorized
Markdown paths. Every finding above is in that exhibit commit.

Hosted `changes`, `fences`, and `build` passed on the verified exhibit head.
The audit workflow scheduled the full hosted matrix. GitHub keeps the
conclusion for the report-only follow-up head in the [PR checks][checks].
The initial run and the draft-skipped gate ledger are recorded separately.
[Initial CI run][initial-ci] · [Initial gate-ledger run][initial-ledger]

Verify the current hosted head, base, draft state and CI rollup together.

```sh
gh pr view 915 --repo mpmdw/JouleWise \
  --json headRefOid,baseRefName,baseRefOid,isDraft,statusCheckRollup
```

- PR #868 supplies the integrated executor and schema byte records, final
  validation, synthetic verification, rehearsal and once-per-ID evidence.
- Opus and the authorized source owner fill both final manifest hashes
  and main registration commits, the row-7 evidence, effective freeze-2
  proof, the stage-1 cuts and their ledger and digest bindings.
- The lead supplies the committed lock and ledger state. Fable through
  Opus supplies the paired exact-hash ruling and applicable signatures.
- NEEDS_SPEC: none found. Any new scientific choice goes to Fable through
  Opus. Depletion forecasting stays with its assigned owner.

Next owner action is for PR #868's author to supply accepted artifacts and
verification. Opus then assembles the two final manifests and exact-byte
evidence for Fable's paired review.

[pr]: https://github.com/mpmdw/JouleWise/pull/915
[checks]: https://github.com/mpmdw/JouleWise/pull/915/checks
[initial-ci]: https://github.com/mpmdw/JouleWise/actions/runs/44767894237
[initial-ledger]: https://github.com/mpmdw/JouleWise/actions/runs/44767894225
