```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "B0-R2 contains contradictory routing rules and an unworkable third-row notice requirement; G1 alone does not certify third-row routing.",
  "workspace": {
    "base_requested": "2ea6a7ec",
    "base_mode": "descendant",
    "head_start": "bee658c5acc4dd860a382317c40ec4421587a13a",
    "head_end": "bee658c5acc4dd860a382317c40ec4421587a13a",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "text": "R1 forbids presentation reads and selects from state.kind, but the existing third-row notice tests omit state.kind and require authenticated wrapper/source selection."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "text": "R2 and R5 preserve base success for calibration-shaped presentation calls, while brief 10 requires a row without an approved evidence handler to refuse typed."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "text": "R4 says every non-string state.kind takes a base refusal, but base notice_subject succeeds for a list kind; R2 and G1 require that success."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "text": "G4 does not freeze P-editable third-row witnesses, and G1's corpus contains no third row."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "text": "P3 leaves K's read-only mutation method and report committer unspecified, and its no-round-4 stop rule has an automatic slice exception."
      },
      {
        "id": "F6",
        "severity": "should_fix",
        "text": "G8 leaves valid calibration undefined and checks corpus adequacy only after P's round."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "python3 -B -c 'import ast,subprocess,types; s=subprocess.check_output([\"git\",\"show\",\"2ea6a7ec:joulewise/evidence_night.py\"],text=True); n=next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name==\"notice_subject\"); g={\"KIND\":\"quiet_predicate_evidence\",\"kind_row\":lambda k:types.SimpleNamespace(receipt_class=\"DIAGNOSTIC_NO_PACK\")}; exec(compile(ast.Module(body=[n],type_ignores=[]),\"base\",\"exec\"),g); print(*(str(k)+\"=\"+g[\"notice_subject\"]({\"plan_id\":\"x\",\"attempt\":1,\"kind\":k}) for k in (\"calibration\",[],\"test_night\")),sep=\"\\n\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "calibration=NIGHT NOTICE — x (EVIDENCE; DIAGNOSTIC_NO_PACK) — attempt 1",
          "[]=NIGHT NOTICE — x (EVIDENCE; DIAGNOSTIC_NO_PACK) — attempt 1",
          "test_night=NIGHT NOTICE — x (EVIDENCE; DIAGNOSTIC_NO_PACK) — attempt 1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "test_night=NIGHT NOTICE"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -B -c 'import subprocess; s=subprocess.check_output([\"git\",\"show\",\"eb8d745f:tests/parity/b0_corpus.py\"],text=True); g={}; exec(compile(s,\"corpus\",\"exec\"),g); print(\"third_row_axis=\",any(\"test_night\" in v for v in g[\"AXES\"].values())); print(\"operations=\",len(g[\"OPERATIONS\"])); t=subprocess.check_output([\"git\",\"show\",\"bee658c5:tests/test_night_kinds.py\"],text=True); a=t.index(\"state = {\\\"custody_root\\\":\",t.index(\"def test_unhandled_third_row_routes_or_refuses_across_shared_entries\")); b=t.index(\"with mock.patch.object(night_kinds\",a); print(\"third_row_notice_state_has_kind=\", \"\\\"kind\\\"\" in t[a:b])'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "third_row_axis= False",
          "operations= 28",
          "third_row_notice_state_has_kind= False"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "third_row_notice_state_has_kind= False"
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
        "tail_regex": "## HEAD \\(no branch\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No full parity run was repeated; the review used executed focused probes and inspected the frozen runner and its recorded results.",
      "needs": ""
    }
  ]
}
```

## Findings

| ID | Severity | Counterexample and exact replacement text |
|---|---|---|
| F1 | **BLOCKER** | The existing third-row tests at `bee658c5:tests/test_night_kinds.py:435–467,584–602` pass no `state.kind`. They expect the notice to select `TEST` from authenticated chain material and to refuse after source drift. R1 permits no presentation read, so it can only take the idle fallback. **Replace R1’s presentation sentences with:** “Presentation uses the unchanged base path for base-shaped states. A non-base row may be *hinted* by existing state fields, but the hint grants no authority: before producing row-specific output, authenticate the sealed wrapper and source against the binding. New reads are confined to that non-base branch. Preserve the base parser, reads, order, and result for every base-shaped input.” |
| F2 | **BLOCKER** | At `2ea6a7ec`, `notice_subject` succeeds with `state.kind="calibration"` and emits the idle subject. R2/R5 require that result; brief 10 §1(d) says a row with no approved evidence handler fails closed with a typed refusal. Enforcing both changes a G1 observation. **Replace R5 with:** “Legacy operations that succeeded at `2ea6a7ec` retain their exact result for calibration-shaped inputs, without gaining arm, registration, or successor-release authority. This is an explicit exception to brief 10 §1(d)’s typed no-handler requirement at those legacy operations. Newly admitted operations and rows without handlers refuse typed.” That exception needs an authoritative ruling before P starts. |
| F3 | **BLOCKER** | The executed base function also succeeds when `state.kind=[]`. R2 says run base code; R4 says take a base refusal that does not exist at this site. **Replace R4 with:** “Check that a kind is a string before table lookup. For a non-string, execute that site’s exact base path, including its success or refusal. Do not invent a refusal at a legacy presentation site.” |
| F4 | MATERIAL | The frozen corpus has no test-only third row. G1 can reach zero **in principle** if authentication reads occur only on a non-base branch; new private API diagnostics are avoidable by deleting `_custody_row`. Thus G1 itself is achievable, but it cannot prove the third-row requirement. P may also edit `tests/test_night_kinds.py`. **Replace G4 with:** “K runs the unchanged bee658c5 third-row notice and dispatch witnesses, verifies their function-source hashes, and adds an independent scratch witness: altering a state hint while holding sealed wrapper/source bytes fixed must never select a different row. P may add tests but may not weaken those pinned assertions.” |
| F5 | MATERIAL | K is read-only, yet G7 asks it to move code, and P3 requires a packet-committed K report. “PARK (no round 4)” then permits a further slice without saying who authorizes it. **Replace the relevant P3 sentences with:** “K performs G7 mutations only in disposable `/tmp` archives; these runs are diagnostic and do not replace the committed-sha G1 run. The lead commits K’s report after reviewing it. If G1 is red, park B0. A per-surface slice requires a new written magistrate ruling and counts as a new round; this text grants no automatic exception.” |
| F6 | MATERIAL | G8 does not define whether “valid calibration” means a recognized wrapper, a C5 PASS receipt, or an accepted operation. Its result may stop the round after P has spent the allotted time. **Replace G8 with:** “Before P starts, K lists exact corpus case IDs for each driver and installer operation where the calibration discriminant is reached with a coherent wrapper, sidecars, source, plan, and receipt, and states the observed branch. If any required operation lacks such a case, return NEEDS_RULING before commissioning P.” |

**Final-text disposition, one line per accepted text:**

| Final text | Disposition |
|---|---|
| 1. Title | Accept. |
| 2. R1–R5 | Replace R1, R4, and R5 as above; the brief 10 exception in F2 needs a ruling. |
| 3. G1–G8 | Retain G1’s exact committed-sha comparison; replace G4 and G8 as above. |
| 4. Seats and stop rule | Replace the P3 sentences identified in F5. |
| 5. Standing clause | Accept. |

**Probe tails:** V1 showed the same idle subject for calibration, list, and test-only kinds. V2 showed `third_row_axis=False` and confirmed the existing third-row notice state has no `kind`. V3 confirmed the checkout stayed clean.

## Residual risk

The full 99,443-observation parity run was not repeated. These findings establish contradictions in the proposed text; they do not assess a future fix commit.