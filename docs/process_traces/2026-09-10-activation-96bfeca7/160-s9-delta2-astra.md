```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "No new code findings; the demonstrated long-s bypass is closed. Requested temporary-symlink coverage is blocked by the read-only sandbox.",
  "workspace": {
    "base_requested": "c4092284",
    "base_mode": "informational",
    "head_start": "fb63063904cf8b010831a70685a8e9167ddab3fb",
    "head_end": "fb63063904cf8b010831a70685a8e9167ddab3fb",
    "upstream_end": "fb63063904cf8b010831a70685a8e9167ddab3fb",
    "branch": "feat/2026-09-10-epoch-equivalence-check"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [],
    "F2": "The reported long-s instance is closed on this Mac. configſ/calibration is the same directory by samefile(), and the guard refuses it with force=True. Disabling the lexical guard still produces an identity refusal.",
    "normalization": "NFC café.json and NFD café.json under the actual acceptance directory both refuse. These tests establish refusal of composed/decomposed output names, not filesystem equivalence of differently normalized parent directories.",
    "symlink": "Not executed: this session's filesystem sandbox prohibits writes, including temporary creation. Inspection predicts a stable symlink to configs/calibration will resolve into the protected directory and refuse.",
    "edge_cases": "A nonexistent parent and an ordinary relative output are allowed without exceptions. A relative acceptance output refuses. A parent that is a file, and a deeper path beneath that file, are allowed without guard exceptions. This guard does not validate destination writability; later mkdir/write operations can fail on those invalid paths.",
    "round_2b": "The shared-constant dependency is gone. ACCEPTANCE_DIR is independently initialized from literal configs/calibration components. With FORBIDDEN_OUT_PARTS patched to never/matches, the extracted fb9f530b guard allows the destination and fb630639 refuses it. The current identity regression passes. No remaining coupling of that shape was found in the delta.",
    "same_signature": "The specific Unicode spelling bypass is closed for stable paths whose immediate parent is this checkout's acceptance directory: identity does not depend on spelling. The entire path-guard bypass class is not closed by construction. The guard checks once, then run() later opens the original pathname; concurrent symlink retargeting remains a plausible same-signature route. No additional static bypass was demonstrated."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "python3 -B -c 'from pathlib import Path\nfrom unittest.mock import patch\nimport unicodedata\nfrom scripts import epoch_equivalence_check as c\ndef check(name,p,expected):\n    try: c._refuse_out_path(p,True); actual='\\''ALLOW'\\''\n    except c.EquivalenceRefusal: actual='\\''REFUSE'\\''\n    assert actual==expected,(name,actual)\n    print(name+'\\'': '\\''+actual)\nalias=c.REPO_ROOT/'\\''config\\u017f/calibration'\\''\nassert alias.samefile(c.ACCEPTANCE_DIR)\nprint('\\''long_s_parent_samefile: True'\\'')\ncheck('\\''long_s'\\'',alias/'\\''calibration_acceptance_d079_v2_n17_r6.json'\\'','\\''REFUSE'\\'')\nfor form in ('\\''NFC'\\'','\\''NFD'\\''):\n    check(form,c.ACCEPTANCE_DIR/unicodedata.normalize(form,'\\''caf\\u00e9.json'\\''),'\\''REFUSE'\\'')\nmissing=Path('\\''/tmp/s9-audit-absent-fb630639/record.json'\\'')\nassert not missing.parent.exists()\ncheck('\\''missing_parent'\\'',missing,'\\''ALLOW'\\'')\ncheck('\\''relative_safe'\\'',Path('\\''s9-audit-absent-fb630639.json'\\''),'\\''ALLOW'\\'')\ncheck('\\''relative_acceptance'\\'',Path('\\''configs/calibration/record.json'\\''),'\\''REFUSE'\\'')\nassert Path('\\''README.md'\\'').is_file()\ncheck('\\''parent_is_file'\\'',Path('\\''README.md/record.json'\\''),'\\''ALLOW'\\'')\nwith patch.object(c,'\\''FORBIDDEN_OUT_PARTS'\\'',('\\''never'\\'','\\''matches'\\'')):\n    check('\\''identity_only'\\'',c.ACCEPTANCE_DIR/'\\''record.json'\\'','\\''REFUSE'\\'')\n    check('\\''identity_only_long_s'\\'',alias/'\\''record.json'\\'','\\''REFUSE'\\'')\nprint('\\''READ_ONLY_GUARD_CHECKS_OK'\\'')\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "long_s_parent_samefile: True",
          "long_s: REFUSE",
          "NFC: REFUSE",
          "NFD: REFUSE",
          "missing_parent: ALLOW",
          "relative_safe: ALLOW",
          "relative_acceptance: REFUSE",
          "parent_is_file: ALLOW",
          "identity_only: REFUSE",
          "identity_only_long_s: REFUSE",
          "READ_ONLY_GUARD_CHECKS_OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "READ_ONLY_GUARD_CHECKS_OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest -v tests.test_epoch_equivalence_check.EpochEquivalenceCheckTest.test_an_out_path_that_is_the_acceptance_directory_by_identity_refuses",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.000s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 -B -c 'import ast,subprocess\nfrom scripts import epoch_equivalence_check as c\nfor rev,expected in [('\\''fb9f530b'\\'','\\''ALLOW'\\''),('\\''fb630639'\\'','\\''REFUSE'\\'')]:\n    tree=ast.parse(subprocess.check_output(['\\''git'\\'','\\''show'\\'',rev+'\\'':scripts/epoch_equivalence_check.py'\\'']))\n    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='\\''_refuse_out_path'\\'')\n    ns=dict(vars(c),FORBIDDEN_OUT_PARTS=('\\''never'\\'','\\''matches'\\''))\n    exec(compile(ast.Module(body=[fn],type_ignores=[]),'\\''<audit>'\\'','\\''exec'\\''),ns)\n    try: ns['\\''_refuse_out_path'\\''](c.ACCEPTANCE_DIR/'\\''record.json'\\'',True); result='\\''ALLOW'\\''\n    except c.EquivalenceRefusal: result='\\''REFUSE'\\''\n    assert result==expected\n    print(rev+'\\'': '\\''+result)\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["fb9f530b: ALLOW", "fb630639: REFUSE"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "fb9f530b: ALLOW\\nfb630639: REFUSE"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The requested /tmp symlink creation cannot run under this session's higher-priority read-only filesystem restriction. The initial here-document command failed before Python started: can't create temp file for here document: operation not permitted. Subsequent probes used python3 -B -c and made no filesystem changes.",
      "needs": "Lead: in a session permitting /tmp writes, create an accented-name symlink to ACCEPTANCE_DIR; call _refuse_out_path through its NFC and NFD spellings, confirm samefile identity and refusal, then remove the link."
    }
  ]
}
```

## Residual risk

**Same-signature statement:** the observed long-s bypass is closed; the broader class is not proven closed. A third round is plausible through a check-to-write filesystem race. That possibility was identified by inspection, not reproduced.

The identity fallback checks only the immediate parent against this checkout’s acceptance directory. Descendants and other checkouts additionally depend on the lexical guard.

The full fixture suite was not run under the read-only restriction. Repository files and HEAD remained unchanged.