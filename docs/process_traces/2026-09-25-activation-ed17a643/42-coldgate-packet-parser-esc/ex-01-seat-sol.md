```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "A whole-stdout, fail-closed text grammar accepts the real capture and refuses the reproduced parser defects; no repository files were changed.",
  "workspace": {
    "base_requested": "origin/feat/2026-09-25-bfg-d",
    "base_mode": "informational",
    "head_start": "faf0ea014e7320eb5758ab4ef4ceb0af60a09854",
    "head_end": "faf0ea014e7320eb5758ab4ef4ceb0af60a09854",
    "upstream_end": "422bfca2df938749e4b0b1d893fbceca2c85e98f",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "G1",
        "action": "start_now",
        "wait_for": "",
        "collision_surface": "joulewise/battery_float.py",
        "decision": "Replace depth recovery with a whole-stdout grammar. Any unrecognized byte or line refuses the observation."
      },
      {
        "row": "G2",
        "action": "wait_for",
        "wait_for": "G1 implementation",
        "collision_surface": "tests/test_battery_float.py",
        "decision": "Pin the real capture and adversarial cases as parser regressions."
      },
      {
        "row": "G3",
        "action": "do_not_start",
        "wait_for": "A separately approved registration revision, if later wanted",
        "collision_surface": "registered probe command and raw-output custody",
        "decision": "Keep /usr/sbin/ioreg -r -c AppleSmartBattery. I do not recommend asking to switch to -a for this cure; consider an owner-approved format revision only if legitimate text output varies beyond the captured grammar."
      }
    ],
    "design": {
      "byte_framing": "Require nonempty bytes, LF termination, ASCII printable bytes plus LF only; refuse CR, TAB, other controls, non-ASCII, output over 1 MiB, or a property line over 65536 bytes. Split on LF without universal-newline normalization.",
      "whole_stdout": "HEADER LF '    {' LF PROPERTY+ LF '    }' LF BLANK*; HEADER is first, with no leading blank; BLANK is zero or more ASCII spaces followed by LF. No blank or other line is permitted inside the block. Require exactly one object.",
      "header_regex": "^\\+-o AppleSmartBattery  <class AppleSmartBattery, id 0x[0-9A-Fa-f]+, registered, matched, active, busy [0-9]+ \\([0-9]+ ms\\), retain [0-9]+>$",
      "property_regex": "^ {6}\"([A-Za-z][A-Za-z0-9_-]*)\" = (.+)$",
      "value_grammar": "Parse the entire captured value with bounded recursive descent: value := atom | quoted | hex | tuple | map; atom := [A-Za-z0-9_+.-]+; quoted := double-quoted printable ASCII with only escaped quote, backslash, n, r, or t; hex := '<' one-or-more hex digits '>'; tuple := '(' [value (',' value)*] ')'; map := '{' [pair (',' pair)*] '}'; pair := quoted '=' [value]. An empty map value is allowed only immediately before ',' or '}', because the capture contains entries such as \"AdapterPower\"=,. Require complete value consumption, matched delimiters and quotes, and nesting depth at most 64.",
      "keys_and_predicate": "Record only the 59-style six-space property lines; refuse a duplicate of any top-level key. Require ExternalConnected, IsCharging, InstantAmperage, and UpdateTime exactly once at top level. Give the first two only Yes/No values and the latter two unsigned decimal uint64 values. Apply the existing signed two's-complement amperage and age/predicate rules after structural acceptance.",
      "construction_invariant": "The parser never skips malformed interior lines or changes depth across physical lines. The sole outer closing brace is the exact four-space line after fully parsed properties; any following nonblank line refuses."
    },
    "must_refuse": [
      "Missing outer closing brace; a header naming OtherBattery; required keys appearing only inside a nested dictionary.",
      "Header object name AppleSmartBattery with <class OtherBattery, ...>; multiline nesting that returns a depth counter to top level early while the outer dictionary is still open.",
      "Duplicate required or optional top-level keys; CRLF; tabs; trailing garbage; a top-level key containing an escaped quote; a second object.",
      "Empty stdout; header-only stdout; wrong property indentation; blank or multiline nested content inside the block; unmatched or crossed inline delimiters; unterminated inline quote; malformed hex; trailing bytes after a value."
    ],
    "tests": [
      "Accept the retained 64-line real capture and check all 59 distinct top-level keys, four required values, and trailing space-only/empty lines.",
      "Table-test every must-refuse case above, including both reproduced round-2 defects.",
      "Accept balanced inline maps, tuples, hex blobs, quoted delimiters, and the observed empty nested map values; refuse one-byte deletion or substitution of each delimiter and quote.",
      "Preserve predicate boundary tests: signed two's-complement amperage at plus/minus 200 and 201 mA; age at 180 and 181 seconds; each Boolean value; uint64 overflow."
    ],
    "executed_evidence": {
      "capture_sha256": "582475270c35c51cc05c2020f500d8c7dfba3eb9a6436a0186cb5ce18a851631",
      "capture_result": "Accepted: 59 distinct property lines, closing brace at line 62, then only blank lines. No real capture line was refused.",
      "mutations": "Scratch grammar refused all 19 adversarial mutations exercised.",
      "current_parser": "Current parse returned passed=True for the real capture, a changed <class OtherBattery, ...> header, and an unclosed outer dictionary whose required keys follow an inner close."
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 /tmp/bfg_design_check.py /tmp/ed17a643/esc/real-ioreg-capture.txt",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "capture: (59, 62, 2)",
          "multiline_nested_map REFUSE unclosed map",
          "blank_inside_block REFUSE bad property line 54"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "capture: \\(59, 62, 2\\)[\\s\\S]*blank_inside_block REFUSE"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONPATH=. python3 /tmp/bfg_existing_repro.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "real True",
          "wrong_class True",
          "unclosed_outer True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "real True\\nwrong_class True\\nunclosed_outer True"
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
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The whitelist is validated against one real machine capture. A future legitimate ioreg text variant may be refused until reviewed.",
      "needs": "Retain fail-closed refusal and review new raw captures before expanding the grammar."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| G1 Parser grammar | start_now | — | `joulewise/battery_float.py` |
| G2 Regression tests | wait_for | G1 implementation | `tests/test_battery_float.py` |
| G3 Switch to `-a` | do_not_start | Separately approved registration revision | Probe command and raw-output custody |

## Critical path

G1 defines the accepted text format; G2 then pins that format and its refusals. The scratch implementation accepted every line of the real capture and refused all 19 exercised mutations. The existing parser still returned `passed=True` for both reproduced round-2 defects.