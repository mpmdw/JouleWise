```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Cured all 11 retired-term occurrences over eight lines; regenerated A4; all four authorized tests pass.",
  "workspace": {
    "base_requested": "c6dbf952",
    "base_mode": "exact",
    "head_start": "c6dbf952ac0b76b866946472924c3d58374d4372",
    "head_end": "c6dbf952ac0b76b866946472924c3d58374d4372",
    "upstream_end": "c6dbf952ac0b76b866946472924c3d58374d4372",
    "branch": "feat/2026-09-05-d165-relabel"
  },
  "pathspec": [
    "docs/paper/draft-v2-skeleton.md",
    "docs/paper/figures/build_mechanism_figures.py",
    "docs/paper/figures/figA4_shared_signs.svg",
    "docs/paper/protocol/first-use-audit-ledger.md",
    "docs/process_traces/2026-09-05-d165-relabel/15-wording-cure-report.md",
    "tests/test_paper_first_use_ledger.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest tests.test_d165_rationale_census",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 8 tests in 7.560s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 8 tests in [0-9.]+s\\n\\nOK\\n?$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 16 tests in 2.510s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 16 tests in [0-9.]+s\\n\\nOK\\n?$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest tests.test_paper_first_use_ledger",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 11 tests in 2.378s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 11 tests in [0-9.]+s\\n\\nOK\\n?$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest tests.test_select_outcome_branches",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 5 tests in 0.230s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 5 tests in [0-9.]+s\\n\\nOK\\n?$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check",
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
    }
  ],
  "flags": []
}
```

## Change

Replaced the eight census-red lines (11 overlapping retired-phrase occurrences)
with plain descriptions of applying the same timing shift to every block. The
replay denial and absence of a proven bound on that shift's effect both remain.
This follows the registered v2 rationale and the existing paper-M distinction
between scalar energy signs and physical timing shifts. It adds no term of art,
changes no arithmetic, and makes no new claim about absolute timing uncertainty.

Exact old → new source lines follow; line numbers did not move. The introductory
denial spans lines 156–157, so those two entries form one sentence.

`docs/paper/draft-v2-skeleton.md:156`

Old:

```text
one local sign per block. It does not globally replay one physical common-time
```

→ New:

```text
one local sign per block. It does not replay the same timing shift in every block
```

`docs/paper/draft-v2-skeleton.md:157`

Old:

```text
shift and has no proven conservatism for common-time motion. Both ratios
```

→ New:

```text
or prove that its limit covers the effect of such a shift. Both ratios
```

`docs/paper/draft-v2-skeleton.md:396`

Old:

```text
within-block construction is not a global common-time replay across blocks.
```

→ New:

```text
within-block construction does not replay the same timing shift in every block.
```

`docs/paper/draft-v2-skeleton.md:811`

Old:

```text
no proven conservatism for physical common-time motion. The floor construction in protocol P.3 is operational; it supplies no new model
```

→ New:

```text
no proof that its limit covers the effect of the same timing shift in every block. The floor construction in protocol P.3 is operational; it supplies no new model
```

`docs/paper/protocol/first-use-audit-ledger.md:137`

Old:

```text
| \(R_{cm}\) | 1. Introduction | glossed-at-first-use | Shared-energy-sign/local-corner sensitivity diagnostic with one shared sign for block-level energy allowances and one local sign per block; it is not a physical common-time replay. |
```

→ New:

```text
| \(R_{cm}\) | 1. Introduction | glossed-at-first-use | Shared-energy-sign/local-corner sensitivity diagnostic with one shared sign for block-level energy allowances and one local sign per block; it does not replay the same timing shift in every block. |
```

`docs/paper/protocol/first-use-audit-ledger.md:138`

Old:

```text
| shared-energy-sign/local-corner sensitivity diagnostic / shared-energy-sign/local-corner ratio | 1. Introduction | glossed-at-first-use | Registered comparative diagnostic that retains scalar energy-allowance signs without claiming common-time conservatism. |
```

→ New:

```text
| shared-energy-sign/local-corner sensitivity diagnostic / shared-energy-sign/local-corner ratio | 1. Introduction | glossed-at-first-use | Registered comparative diagnostic that retains scalar energy-allowance signs without claiming that its limit covers the effect of the same timing shift in every block. |
```

`docs/paper/figures/build_mechanism_figures.py:80`

Old:

```text
t(s,30,392,'A shared energy sign does not replay one physical time shift across blocks; no common-time conservatism is proven.')
```

→ New:

```text
t(s,30,392,"A shared energy sign does not replay one timing shift across all blocks or prove its limit covers that shift's effect.")
```

`docs/paper/figures/figA4_shared_signs.svg:18`

Old:

```text
<text x="30" y="392" font-size="15">A shared energy sign does not replay one physical time shift across blocks; no common-time conservatism is proven.</text>
```

→ New:

```text
<text x="30" y="392" font-size="15">A shared energy sign does not replay one timing shift across all blocks or prove its limit covers that shift&#x27;s effect.</text>
```

`tests/test_paper_first_use_ledger.py:98`

Old:

```text
        "does not globally replay one physical common-time shift",
```

→ New:

```text
        "does not replay the same timing shift in every block",
```

`tests/test_paper_first_use_ledger.py:99`

Old:

```text
        "has no proven conservatism for common-time motion",
```

→ New:

```text
        "or prove that its limit covers the effect of such a shift",
```

The final two entries update the existing first-use assertions to enforce both
halves of the cured denial. The allowlist and terms-lint test file remain
byte-for-byte unchanged. Inspection found no A4 SVG digest pin in terms lint;
the pinned SVG digests there belong to other figures, so no pin was changed.
The Abstract bytes are unchanged. The ledger still ends with
`Terms inventoried: 265; FAILS: 0.`

## Verification notes

The initial census reproduced the reported failure before edits, using the same
command as V1: `Ran 8 tests in 7.010s`, `FAILED (failures=1)`. Its failure listed
exactly the 11 occurrences on the eight requested lines. V1 records the cured
run. V1–V4 ran separately and sequentially with the required corpus root; their
exact clean tails are in the envelope. No discovery suite or other test module
was run. No Claude/Codex process, live capture, commit, or out-of-scope repository
write was started.

The figures README documents that the generator writes eight SVGs. To preserve
write scope, the complete figures directory was copied into a temporary tree,
the edited generator was run there, and only A4 was copied back. All other SVGs
were byte-identical. Running the generator again reproduced A4 exactly. The
exact regeneration command was:

```bash
python3 -B - <<'PY'
from pathlib import Path
import hashlib
import shutil
import subprocess
import tempfile
root = Path.cwd()
figures = root / 'docs/paper/figures'
with tempfile.TemporaryDirectory(prefix='d165-wording-') as scratch:
    staged = Path(scratch) / 'docs/paper/figures'
    shutil.copytree(figures, staged)
    subprocess.run(['python3', '-B', str(staged / 'build_mechanism_figures.py')], cwd=scratch, check=True)
    changed = [p.name for p in staged.glob('*.svg') if p.read_bytes() != (figures / p.name).read_bytes()]
    assert changed == ['figA4_shared_signs.svg'], changed
    target = figures / changed[0]
    target.write_bytes((staged / changed[0]).read_bytes())
    subprocess.run(['python3', '-B', str(staged / 'build_mechanism_figures.py')], cwd=scratch, check=True)
    assert target.read_bytes() == (staged / target.name).read_bytes()
    print('Generated SVG changes: ' + ', '.join(changed))
    print('A4 repeat-generation byte equality: PASS')
    print('A4 SHA-256: ' + hashlib.sha256(target.read_bytes()).hexdigest())
PY
```

Observed output:

```text
Generated SVG changes: figA4_shared_signs.svg
A4 repeat-generation byte equality: PASS
A4 SHA-256: b9295b136eb2f8ba41d5fe228b0bc99579e3f8c52c6a92770109a0e8650aa397
```

This command records the mutation from the baseline: after the cure has been
applied, the first comparison correctly reports no changed SVGs instead of A4.
For a subsequent byte-consistency check, compare every staged SVG against its
repository counterpart without copying back.

The first attempt to write this report failed during shell parsing because a
nested here-document reused the outer delimiter; it executed no writes. A
distinct outer delimiter fixed the report command. This did not affect any test
or implementation result.

Intake: no active stop card or global gate; this bounded AGENT task is the
explicitly delegated continuation of A152 / D165-RELABEL-01. The checkout began
clean at the requested exact head. Lead-owned state, queue, and other reports
were preserved under the exhaustive write scope. No blocker remains. Next exact
step: lead reviews this diff and report; the changes are uncommitted.
