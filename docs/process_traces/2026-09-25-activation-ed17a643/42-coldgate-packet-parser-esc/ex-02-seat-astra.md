```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend a fixed whole-output grammar with independent inline value parsing; prototype accepts the real capture and rejects 62 adversarial cases.",
  "workspace": {
    "base_requested": "faf0ea01",
    "base_mode": "exact",
    "head_start": "faf0ea014e7320eb5758ab4ef4ceb0af60a09854",
    "head_end": "faf0ea014e7320eb5758ab4ef4ceb0af60a09854",
    "upstream_end": "422bfca2df938749e4b0b1d893fbceca2c85e98f",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "Adjudicate grammar", "action": "start_now"},
      {"row": "Implement and independently test", "action": "wait_for"},
      {"row": "Change registered argv to -a", "action": "needs_ruling"},
      {"row": "Live measurement", "action": "do_not_start"}
    ],
    "diagnosis": "Both round-two false GO cases reproduce at the pinned HEAD despite all seven existing ParserTests passing. The defect is structural inference from partial matches and cross-line depth bookkeeping. Replace that architecture instead of extending its exceptions.",
    "design": {
      "profile": "A deliberately conservative grammar for the supplied capture format, not a claim to recognize every possible ioreg rendering. Unsupported formatting is a probe error. No recovery, normalization, ignored body lines, or early success.",
      "bytes": "Require bytes, at most 1048576 bytes, and only LF or printable ASCII bytes 0x20..0x7e. Require a final LF. Split only on b'\\n'; never use splitlines(), strip(), universal-newline decoding, or whitespace normalization. Preserve and hash original bytes.",
      "header_fullmatch_regex": "\\+-o AppleSmartBattery  <class AppleSmartBattery, id 0x[0-9a-f]+, registered, matched, active, busy [0-9]+ \\([0-9]+ ms\\), retain [0-9]+>",
      "key_regex": "\"([A-Za-z0-9_][A-Za-z0-9_.-]*)\"",
      "property_grammar": "fullmatch: exactly six ASCII spaces + KEY + exactly ' = ' + nonempty VALUE. Opening line must equal b'    {'; closing line must equal b'    }'. All regex matches consume the complete physical line unless explicitly tokenizing VALUE.",
      "document_pseudocode": [
        "Line 1 must fullmatch HEADER; line 2 must equal OPEN.",
        "Start BODY with an empty property map.",
        "In BODY: exact CLOSE transitions permanently to TAIL. Every other line must fullmatch PROPERTY; reject duplicate top-level keys; validate its entire VALUE before recording the property.",
        "In TAIL: every remaining line must fullmatch ASCII-space-only regex ' *'.",
        "Reject EOF without CLOSE. Reject missing required keys. Only after the entire document succeeds may predicate evaluation run.",
        "No nesting state exists between physical lines. Nested values cannot add entries to the top-level map."
      ],
      "value_grammar": [
        "VALUE := UINT | 'Yes' | 'No' | STRING | DATA | DICT | ARRAY",
        "UINT := [0-9]+",
        "DATA := <(?:[0-9a-fA-F]{2})*>",
        "ARRAY := '(' [VALUE (',' VALUE)*] ')'",
        "DICT := '{' [MEMBER (',' MEMBER)*] '}'",
        "MEMBER := KEY '=' [VALUE]",
        "STRING: consume opening double quote; then printable ASCII characters except unescaped double quote/backslash; a backslash must be followed by double quote or backslash; consume closing double quote.",
        "No whitespace outside STRING within a VALUE. No escaped keys, trailing commas, empty array members, or unsupported tokens.",
        "Parse recursively with a cursor. Each production must consume its own matching delimiter; require cursor == len(value) at completion. Enforce unique keys separately in every DICT.",
        "Limit VALUE recursion depth to 128 and every body/tail line to 262144 bytes. Any exceeded limit rejects the observation."
      ],
      "empty_nested_values": "The optional VALUE in MEMBER is intentional: real BatteryData contains AdapterPower=, IdealCRate=, and SystemPower= with empty RHS. Permit emptiness only immediately before a dictionary comma or closing brace. Never permit empty top-level values or treat empty nested members as predicate data.",
      "predicate_boundary": "Require exactly one top-level ExternalConnected, IsCharging, InstantAmperage, and UpdateTime. Boolean values must be exactly Yes or No. Required integer lexemes must fullmatch [0-9]{1,20} and be below 2**64. Decode InstantAmperage as n-2**64 when n>=2**63. Apply the existing registered current and age thresholds only after complete structural acceptance. Structural failure must produce probe_error and never passed=true.",
      "compatibility": "Rejecting CRLF, tabs, escaped keys, non-ASCII strings, alternative header metadata, and multiline containers is intentional for this profile. A newly observed legitimate format requires an explicit grammar extension with positive and negative fixtures; do not add a permissive fallback.",
      "argv_recommendation": "Yes: recommend asking the owner for a separately approved future migration to -a, because a standard structured format reduces bespoke parsing. It is not required for this cure. Retain the exact registered argv now. A plist implementation would still need exact object/type checks and explicit duplicate-key rejection."
    },
    "must_refuse": [
      "Missing object closing brace; wrong object name; AppleSmartBattery name with class OtherBattery; arbitrary header contents; class-name prefixes/suffixes or injected extra class fields.",
      "Required keys only inside an inline dictionary; required keys only inside a multiline dictionary; an unclosed outer dictionary whose inner close formerly reset depth and exposed nested required keys.",
      "Duplicate required, optional, or unknown top-level keys, whether values agree or conflict; duplicate keys inside any individual inline dictionary.",
      "CRLF, bare CR, tabs in indentation or values, vertical tabs, NUL, other control bytes, and non-ASCII bytes.",
      "Trailing garbage, properties after CLOSE, extra closing braces, a second object, leading blank lines, blank body lines, and header-only or empty stdout.",
      "Wrong opening/closing indentation; uniformly wrong property indentation; mixed property indentation; missing opening brace; trailing property whitespace; missing final LF.",
      "Escaped quotes or backslashes in keys, including unknown keys; malformed key quoting; unsupported key characters.",
      "Unclosed or mismatched inline containers, delimiter underflow, unclosed strings, dangling or unsupported escapes, malformed data blobs, and unsupported square-bracket arrays.",
      "Balanced but syntactically invalid values such as {garbage}; multiple adjacent values; a second assignment on one line; bare garbage; empty top-level RHS; empty array elements; trailing commas.",
      "Missing required keys or substitution by aliases; quoted, nested, signed, overflowing, or otherwise malformed required numbers; non-boolean required booleans.",
      "Resource-limit violations. Properly framed charging, disconnected, excessive-current, or stale observations must also never reach GO, through the existing semantic rules."
    ],
    "tests": {
      "executed": "Scratch prototype: 8 positive and 62 negative cases passed. Positives cover the real capture, minimal object, reordered properties, empty containers, nested empty RHS, quoted delimiters/escapes, nested shadow names, and trailing space-only blank lines. Existing ParserTests: 7 passed. Both reported round-two false GO cases independently reproduced against current production parse().",
      "implementation_acceptance": [
        "Port every named scratch case to repository tests; retain the exact real capture as a positive fixture.",
        "For each structural negative, assert both parse refusal and observe(probe_error=true, passed=false), including failures after otherwise valid required properties.",
        "Test each required-key omission and alias substitution; duplicate identical and conflicting values; ensure nested names never satisfy a missing top-level key.",
        "Test signed-current boundaries +200, -200, +201, -201, zero, uint64 maximum/overflow, and update-age boundaries 180 and just over 180 seconds using controlled clocks.",
        "Test raw byte/hash identity, nonzero exit, timeout, malformed output, and no downstream authorization on parse failure.",
        "Add grammar-based mutations that delete or mismatch delimiters, move required lines into containers, append suffixes, and alter indentation. Assert rejection independently of the parser's internal state representation.",
        "After implementation, run focused regressions and the canonical suite; a separate reviewer should challenge the grammar and test oracle."
      ]
    },
    "capture_evidence": {
      "path": "/tmp/ed17a643/esc/real-ioreg-capture.txt",
      "sha256": "582475270c35c51cc05c2020f500d8c7dfba3eb9a6436a0186cb5ce18a851631",
      "bytes": 17337,
      "physical_lines": 64,
      "properties": 59,
      "rejected_lines": 0,
      "layout": "Header 1; opening brace 2; properties 3-61; closing brace 62; blank lines 63-64.",
      "required_values": {"ExternalConnected": "Yes", "IsCharging": "No", "InstantAmperage": "0", "UpdateTime": "1790394405"},
      "qualification": "Offline structural acceptance of retained bytes, not a fresh battery-state or live hardware validation."
    },
    "scratch_artifact": "/tmp/ed17a643/esc/astra-consult/grammar_probe.py"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /tmp/ed17a643/esc/astra-consult/grammar_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["BASELINE false-GO reproduced: wrong-class-field", "BASELINE false-GO reproduced: early-depth-return-unclosed-outer", "RESULT PASS (offline grammar experiment; no live probe)"]},
      "expected": {"exit_code": 0, "tail_regex": "RESULT PASS \\(offline grammar experiment; no live probe\\)"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_battery_float.ParserTests -v",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {"id": "F1", "kind": "baseline_drift", "level": "nonblocking", "text": "The local origin branch ref points to 422bfca2; this consult stayed on the explicitly requested faf0ea01 detached HEAD. Repository remained clean.", "needs": "Apply conclusions to the pinned implementation, then verify any newer candidate separately."},
    {"id": "F2", "kind": "verification_gap", "level": "nonblocking", "text": "Design experiment only; no repository implementation changes, canonical suite, or live probe. Scratch artifacts are under /tmp.", "needs": "Lead owns implementation authorization and final verification."}
  ]
}
```

## Scheduling matrix

Row | action | wait_for | collision surface
--- | --- | --- | ---
Adjudicate grammar | start_now | — | Accepted text-format profile
Implement and independently test | wait_for | Lead adopts design and grants write scope | Parser and regression tests
Change registered argv to `-a` | needs_ruling | Owner approval | Registration and evidence format
Live measurement | do_not_start | Clean, lead-controlled session | Quiet-machine gate

## Critical path

Grammar adoption → authorized implementation → independent adversarial review → lead verification. Approval for `-a` is not a dependency of the proposed text-parser cure.