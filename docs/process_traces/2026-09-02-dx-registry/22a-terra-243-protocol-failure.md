```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "VERDICT: CLEAN — the docstring-only patch is truthful at head; census closure, custody hashes, ruling replays, and retained-corpus tests all pass.",
  "workspace": {
    "base_requested": "4c88b941",
    "base_mode": "exact",
    "head_start": "3efa807ea1017f72fa44ef90b9412315ade8d0c9",
    "head_end": "3efa807ea1017f72fa44ef90b9412315ade8d0c9",
    "upstream_end": null,
    "branch": "HEAD (detached)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [],
    "verdict": "CLEAN",
    "census": "grep finds exactly class:143, raises:899/920/949, handler:1027. replay_half is the sole handler-reachable producer; no other ArtifactsUnavailable route exists.",
    "custody_sha256": {
      "01-coldfable-r7f.md": "c5638dfd38b4c096654f59d8548075af1f1a92d4a6f276c7c6736f6584f0ca7c",
      "02-opus-refute-r7f.md": "2d1e0d50871d7db63ec34639e4137bbe69d3fe1d8b09d44d439ec969c99e1212"
    },
    "sentence_audit": [
      "14-15: main:1024-1026 invokes replay_half; replay_half:901-958 uses TMPDIR, runs XS/AS, and byte-compares XD/F4/AQ.",
      "16-19: replay_half:897-899, 918-922, and 947-951 are the three exit-3 sources; XS:135/163/170,800-802 and AS:646-653,721-723 support their producer-preflight descriptions.",
      "19: main:1027-1030 returns 3, never 0.",
      "19-20: main:1024 guard skips replay for --literals-only.",
      "22-24: main:1017-1022,1024-1036 implements 0/2/3 mapping, including non-3 producer failures collected by replay_half:923-924,952-953.",
      "24-25: digest_half executes at main:1017 before replay and its mismatch return is main:1018-1022.",
      "25-28: main:1025-1030 handles the raised exit 3 instead of extending replay comparisons.",
      "26-28: XD/F4 comparisons are local at replay_half:926-932; AS exit 3 at 947-951 prevents their return/printing.",
      "28-30: XS treats retained-sha mismatch as ArtifactsUnavailable at paper_excursion_decomposition.py:169-170,800-802.",
      "31: main:1032-1036 and _print_tail:985-987 produce successful full-replay tail.",
      "31-32: main:1034 selects the distinct literals-only token.",
      "32-34: main:1027-1030 prints CORPUS UNAVAILABLE and bypasses _print_tail.",
      "34-42: exactly the three raise sites feed the handler; producer details are normalized by _producer_unavailable_message:857-861.",
      "35-39: _required_corpus_paths:797-838 supplies the first absent path; corpus root resolves at main:1014; directory entry is :810.",
      "39-41: _producer_unavailable_message:851-861 concatenates stdout/stderr, strips, splits, and joins with ` | `.",
      "41-43: its no-output fallback is resolved corpus_root; preflight:897-899 establishes that root exists in normal non-concurrent execution.",
      "43-46: forms (ii)/(iii) are arbitrary producer text or root fallback by :857-861, so only preflight form (i) is safely a missing path."
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_round7_artifacts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".........",
          "----------------------------------------------------------------------",
          "Ran 45 tests in 481.548s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 45 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 scripts/check_paper_round7_artifacts.py --literals-only | tail -1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 scripts/check_paper_round7_artifacts.py --corpus-root /Users/edr/code/JouleWise | tail -2",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "R7F PLACED 0/16",
          "R7F COMPARED 184 / MISMATCHES 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R7F COMPARED 184 / MISMATCHES 0"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "grep -n ArtifactsUnavailable scripts/check_paper_round7_artifacts.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "143:class ArtifactsUnavailable(RuntimeError):",
          "899:            raise ArtifactsUnavailable(str(path))",
          "920:                raise ArtifactsUnavailable(",
          "949:                raise ArtifactsUnavailable(",
          "1027:        except ArtifactsUnavailable as exc:"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "three raises and one handler"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff 4c88b941..3efa807e -- scripts tests | grep -c '^[+-]'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "46"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "46"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --no-ext-diff --unified=0 4c88b941..3efa807e -- scripts tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Only scripts/check_paper_round7_artifacts.py changed; every hunk is inside its opening docstring."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "docstring-only"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git -C /Users/edr/code/JouleWise-wt-dx show 74fb5206:scripts/check_paper_round7_artifacts.py | grep -n \"ArtifactsUnavailable\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "127:class ArtifactsUnavailable(RuntimeError):",
          "883:            raise ArtifactsUnavailable(str(path))",
          "904:                raise ArtifactsUnavailable(",
          "933:                raise ArtifactsUnavailable(",
          "1011:        except ArtifactsUnavailable as exc:"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "exactly three raises and one handler"
      }
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git -C /Users/edr/code/JouleWise-wt-dx show 74fb5206:scripts/check_paper_round7_artifacts.py | sed -n 794p",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "        corpus_root / \"runs\" / \"instrument_validation\","
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "runs/instrument_validation"
      }
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "cd /Users/edr/code/JouleWise-wt-dx && python3 scripts/check_paper_round7_artifacts.py --help | grep -c \"exactly three sites\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1"
      }
    },
    {
      "id": "V10",
      "kind": "inspection",
      "cmd": "find docs/process_traces/2026-09-02-coldgate-r7f-unavailable -maxdepth 1 -type f -print0 | sort -z | xargs -0 shasum -a 256",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "c5638dfd38b4c096654f59d8548075af1f1a92d4a6f276c7c6736f6584f0ca7c  docs/process_traces/2026-09-02-coldgate-r7f-unavailable/01-coldfable-r7f.md",
          "2d1e0d50871d7db63ec34639e4137bbe69d3fe1d8b09d44d439ec969c99e1212  docs/process_traces/2026-09-02-coldgate-r7f-unavailable/02-opus-refute-r7f.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "c5638.*01-coldfable.*\\n2d1e.*02-opus"
      }
    }
  ],
  "flags": []
}
```