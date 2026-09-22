# Exhibit D — round-1 refuters and the Opus counter-review (context for the same-signature question), verbatim

## D1 Astra contract lens on fc28d782
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Classifier matches Q1; documentation retains contradictions, and Q4's refusal-only verdict and exact evidence-path assertions are incomplete.",
  "workspace": {
    "base_requested": "9e0a4995",
    "base_mode": "descendant",
    "head_start": "fc28d7822c5b5eac8f42a3b56634fe86b08465a8",
    "head_end": "fc28d7822c5b5eac8f42a3b56634fe86b08465a8",
    "upstream_end": "fc28d7822c5b5eac8f42a3b56634fe86b08465a8",
    "branch": "fix/2026-09-21-retained-root-terminal-markers"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "F1", "severity": "should_fix", "location": "docs/phase_2/derivation_night_runbook.md:699", "title": "Section opening still prohibits discoverable retained roots"},
      {"id": "F2", "severity": "should_fix", "location": "docs/phase_2/derivation_night_runbook.md:724", "title": "Claimed active-span check is not implemented"},
      {"id": "F3", "severity": "should_fix", "location": "docs/phase_2/derivation_night_runbook.md:736", "title": "Ruled manual loop accepts marker directories"},
      {"id": "F4", "severity": "should_fix", "location": "tests/test_evidence_night.py:781", "title": "Refusal-only verdict and exact evidence paths are not pinned"},
      {"id": "F5", "severity": "nit", "location": "docs/process/NIGHT_HANDBACK.md:298", "title": "Handbook and runbook additions are not verbatim"},
      {"id": "F6", "severity": "nit", "location": "joulewise/evidence_night.py:657", "title": "Exactly-one-terminal-family comment is inaccurate"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_evidence_night -k retained -k discovery",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 4 tests in 6.008s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 4 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/retained-contract-review.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["wrong_evidence_path_mutant={\"tests\": 4, \"survived\": true, \"failures\": 0, \"errors\": 0}", "ALL_REVIEW_PROBES_OK"]},
      "expected": {"exit_code": 0, "tail_regex": "ALL_REVIEW_PROBES_OK"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse '@{upstream}' && git merge-base --is-ancestor 9e0a4995 HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["fc28d7822c5b5eac8f42a3b56634fe86b08465a8", "fc28d7822c5b5eac8f42a3b56634fe86b08465a8"]},
      "expected": {"exit_code": 0, "tail_regex": "fc28d7822c5b5eac8f42a3b56634fe86b08465a8"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "F2 and F3 are defects inherited from the ruling, not departures from its replacement text.",
      "needs": "Adjudicate corrections to the ruled executable text and the active-span guarantee."
    },
    {
      "id": "R2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Two in-memory mutants survived all four focused tests; full-suite and live validation were excluded from this review.",
      "needs": "Add isolated refusal-only success and exact full-path assertions."
    }
  ]
}
```

## Findings

**Blocker: none established.**

References below use **R** for `10-coldgate-fable-ruling.md` in the supplied packet directory on `origin/bookkeeping/2026-09-21-activation-29ea94df`.

**F1 — Should-fix: §0.7 still contradicts the retention rule.**  
`docs/phase_2/derivation_night_runbook.md:699–702` retains the heading “Nothing else is armed or discoverable” and the prohibition “no discoverable prior plan root.” A completed root containing `courier.sent` therefore satisfies the new paragraph at :724 but violates the opening paragraph. This leaves A230’s contradictory preconditions unresolved despite its DONE designation (`TASK_QUEUE.md:858`). R:35 explicitly permits discoverable retained roots.

**Cure:** Align the heading and opening prohibition with the ruled retention condition.

**F2 — Should-fix: the advertised executable check does not fence active spans.**  
`docs/phase_2/derivation_night_runbook.md:724–729` promises rejection of a root “whose span is active.” Concrete input: a root with regular `chain.exited`, no installed agents, and observation time `t0 + 1`, inside its window. `retained_roots` returns `retained/pass` (`joulewise/evidence_night.py:674–683`), while `plan_span_active` returns true (`scripts/magistrate_watchdog.py:786–787`). Item 0 checks jobs/plists, not sibling-plan times (`joulewise/evidence_night.py:743–773`).

This reproduces the supplied refuter’s Q2 R1 (`11-opus-contract-refuter.md:113–123`) and remains in tension with consult-18’s “unknown or active ownership stops” (`18-consult-evidence-installer-split-astra.md:53`). A263 registers it (`TASK_QUEUE.md:881`) but does not resolve it. **The implementation follows R:39 here; the ruling itself contains the mismatch.**

**Cure:** Obtain an amendment either requiring an explicit span check or precisely documenting and proving the separate enforcement boundary.

**F3 — Should-fix: the manual classifier violates regular-file semantics.**  
`docs/phase_2/derivation_night_runbook.md:736–737`: with only a **directory** named `night/refusal.json`, the copied zsh loop prints `prior: retained refusal.json`; Python returns `UNKNOWN/fail`. `(N)` suppresses unmatched globs but does not restrict matches to regular files. This contradicts R:21 and its directory regression at R:74. The loop is byte-for-byte identical to R:42–47.

**Cure:** Amend the ruled loop to apply the same file-type/path-safety checks, or direct manual inspection through the Python inventory.

**F4 — Should-fix: Q4 case 1 is incompletely asserted.**  
`tests/test_evidence_night.py:781–798` mixes successful and failing roots, asserting only the aggregate failing verdict. Evidence assertions at :788 and :793 compare basenames; :731 checks counts. Consequently, both these in-memory mutations survived **all four focused tests**:

- Fail every nonempty inventory lacking `courier.sent`, `result.json`, or `chain.exited`: refusal-only roots incorrectly refuse.
- Replace every evidence path with `/wrong-root/night/<same-basename>`.

R:68 requires refusal-only `pass` and `evidence == [that path]`.

**Cure:** Exercise an isolated refusal-only root through `check()`, asserting success and the complete expected path.

All eight ruled classification cases are present:

| Q4 case | Counterfactual caught by current assertions |
|---|---|
| 1: refusal only | Reverting to the original two markers; verdict/path gaps remain above |
| 2: exit only | Dropping `chain.exited` |
| 3: numbered refusal variants | Replacing refusal globs with literal `refusal.json` |
| 4: start only | Removing ACTIVE classification; isolated `check()` refusal is also asserted |
| 5: start + calibration refusal | Testing retained before ACTIVE |
| 6: start + exit | Keying ACTIVE on start alone |
| 7: refusal directory | Replacing marker `is_file()` with `exists()` |
| 8: plan only | Accepting UNKNOWN roots; existing discovery test checks refusal |

**F5 — Nit: exact-text differences.**  
Word-by-word comparison, preserving punctuation and Markdown:

- Contract `docs/contracts/evidence_night_entry.md:205–211` versus R:29: **no word or punctuation differences**; whitespace reflow only.
- Runbook :724–743 versus R:39–50: appends exactly `(Cold-gate ruling 2026-09-21, packet 05 Q2, lane A230.)`. Otherwise only prose reflow; fenced code is byte-exact.
- Handbook `docs/process/NIGHT_HANDBACK.md:298–309` versus R:60: replaces `Before` with `**Before`, and replaces `helpers.` with:
  ```
  helpers** (cold-gate ruling 2026-09-21, packet 05 Q3; the census classifies every process outside the caller's ancestor chain as foreign, and the tracked check refuses on any foreign PID).
  ```
  No other word/punctuation differences; remaining changes are line wrapping.

**Cure:** Preserve the ruled passages verbatim and place attribution/explanation separately.

**F6 — Nit: misleading production comment.**  
`joulewise/evidence_night.py:657–658` says the driver writes “exactly one of these families when a night ends.” The legitimate refusal-plus-exit root tested at `tests/test_evidence_night.py:737–752` has multiple families; R:19 also explains that refusals can appear mid-chain.

**Cure:** Describe these as potentially coexisting classification markers, with open-chain precedence.

**Q1 disposition:** No classification divergence found. `joulewise/evidence_night.py:662–683` matches the ruled marker set, effective ACTIVE precedence, regular-file checks, and complete marker listing. Its refusal patterns match `scripts/run_night.py:281–284`. Accepting `chain.exited` containing `launch_failed: true` follows the ruling; `_record_chain_exit` explicitly supports that record (`scripts/run_night.py:411–427`).

**Q4 scope disposition:** No executable scope creep found. A263/A264 are deferred registrations (`TASK_QUEUE.md:881–882`); the diff does not alter the watchdog, installer, census classifier, or custody roots. The substantive KEEP-row tension is F2.

## Residual risk

Full-suite, live arming, and MCP-helper termination validation were not run, as scoped. Fixture probes establish the reported counterexamples, not live machine clearance. Repository files and Git state remained unchanged.
## D2 Sol execution lens on fc28d782
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Python matches all 14 fixtures; all six mutations are killed; 94 tests pass; the ruled zsh loop falsely reports retained for three cases.",
  "workspace": {
    "base_requested": "9e0a4995d800cbebda223fb67981664f5f74b207",
    "base_mode": "descendant",
    "head_start": "fc28d7822c5b5eac8f42a3b56634fe86b08465a8",
    "head_end": "fc28d7822c5b5eac8f42a3b56634fe86b08465a8",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "docs/phase_2/derivation_night_runbook.md",
        "line": 733,
        "summary": "The manual loop accepts directory markers, symlinked markers, and non-regular plan files that retained_roots rejects.",
        "cure": "Amend the ruled manual procedure to use retained_roots or equivalent path guards, and add parity coverage."
      }
    ],
    "python_cases": "14/14 conform",
    "mutations": "6/6 killed",
    "module": "94 tests passed",
    "zsh_disagreements": 3
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/retention-audit-3pdov0/fixtures.py > /tmp/retention-audit-3pdov0/fixtures.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "Q1: 14/14 match ruled classification and path guards",
          "Q4 disagreements: 08-directory-marker, 10-symlink-marker, 14-directory-plan"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Q4 disagreements: $"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/retention-audit-3pdov0/mutations_verified.py > /tmp/retention-audit-3pdov0/mutations_verified.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "MUTATION SUMMARY: baseline PASS; 6/6 KILLED; every run selected 4 tests"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MUTATION SUMMARY: baseline PASS; 6/6 KILLED; every run selected 4 tests"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_evidence_night > /tmp/retention-audit-3pdov0/module.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 94 tests in 272.515s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 94 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/retention-audit-3pdov0/authority.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Q1 exact replacement sentence: MATCH (whitespace normalized)",
          "Q2 ruled zsh loop: BYTE-IDENTICAL (quote prefixes removed)",
          "Q2 replacement paragraph: MATCH (whitespace normalized)",
          "Q3 operative commands and stop rule: MATCH (whitespace normalized)",
          "A263 reproduced: {\"now_minus_t0_s\": 600, \"plan_span_active\": true, \"retained_roots\": \"retained\", \"verdict\": \"pass\"}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Q2 ruled zsh loop: BYTE-IDENTICAL"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "F1 reproduces a defect in the exact Q2 ruled shell text; the implementation copied that text faithfully.",
      "needs": "Obtain an amendment to the manual procedure and add the parity regression."
    },
    {
      "id": "R2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The bookkeeping remote-tracking ref advanced from 85ddb9ec to 0cd42bd7 during review. The ruling was unchanged; the revised Opus refuter was reread. The reviewed worktree HEAD and clean state remained unchanged.",
      "needs": ""
    }
  ]
}
```

## Findings

**Blocker: none.**

**F1 — should-fix: the manual loop produces three false `retained` lines.** At [derivation_night_runbook.md:733](/Users/edr/code/JouleWise-wt-retention2-29ea94df/docs/phase_2/derivation_night_runbook.md:733), `(N)` permits directory and symlink matches, and the loop never validates the plan’s file type. Python enforces those guards at [evidence_night.py:670](/Users/edr/code/JouleWise-wt-retention2-29ea94df/joulewise/evidence_night.py:670), consistent with [contract item 4:203](/Users/edr/code/JouleWise-wt-retention2-29ea94df/docs/contracts/evidence_night_entry.md:203).

Executed command, with only the loop’s discovery root changed:

```sh
/bin/zsh /private/tmp/retention-audit-3pdov0/runbook.zsh
```

Relevant output, exit 0:

```text
08-directory-marker: retained refusal.json
10-symlink-marker: retained refusal.json
14-directory-plan: retained refusal.json
```

Python returns `UNKNOWN/fail`, raises `Refused: symlink/path collision`, and raises `Refused: retained plan is not a regular non-symlink file`, respectively.

**Cure:** amend Q2’s manual procedure to use the Python classifier or equivalent guards, and pin these cases with a parity test. The tracked Python check already refuses them.

**Nit: none.**

**Q1/Q4 — fourteen executed cases**

Fixtures and full output: [fixtures.py](/tmp/retention-audit-3pdov0/fixtures.py), [fixtures.log](/tmp/retention-audit-3pdov0/fixtures.log). `/tmp` paths were resolved to `/private/tmp` before calling `safe_path`.

| Fixture | Python classification | Verdict | zsh classification |
|---|---|---|---|
| Only `refusal.json` | retained | pass | retained |
| Only `chain.exited` | retained | pass | retained |
| Only `refusal-3.json` | retained | pass | retained |
| Only `calibration-refusal.json.2.json` | retained | pass | retained |
| `chain.started` alone | ACTIVE | fail | ACTIVE |
| Started + calibration refusal | ACTIVE | fail | ACTIVE |
| Started + exited | retained | pass | retained |
| `refusal.json` directory | UNKNOWN | fail | **retained** |
| Plan only, empty `night/` | UNKNOWN | fail | UNKNOWN |
| `refusal.json` symlink to regular file | No classification | Refused | **retained** |
| Only `refusal.json.bak` | UNKNOWN | fail | UNKNOWN |
| Empty `night/` | UNKNOWN | fail | UNKNOWN |
| No `night/` | UNKNOWN | fail | UNKNOWN |
| Plan directory, regular refusal marker | No classification | Refused | **retained** |

No Python result contradicts the ruling. ACTIVE roots retain any terminal-marker evidence found; `chain.started` itself is excluded.

**Q2 — mutation results**

Executed [mutations_verified.py](/tmp/retention-audit-3pdov0/mutations_verified.py) against independent package copies. Each invocation asserted the imported module’s scratch path before loading tests. The filters `-k retained -k discovery` select **four** tests. The unchanged baseline passed.

Every mutation was killed by an assertion in `LifecycleTests.test_retained_root_classification_ruled_cases` ([test_evidence_night.py:760](/Users/edr/code/JouleWise-wt-retention2-29ea94df/tests/test_evidence_night.py:760)):

| Mutation | Result | Failing assertion/case |
|---|---|---|
| m1 Retained before ACTIVE | **KILLED** | Started + calibration refusal |
| m2 Remove `chain.exited` marker | **KILLED** | Exited only; started + exited |
| m3 Literal `refusal.json` only | **KILLED** | Numbered and calibration refusal cases |
| m4 Marker `is_file()` → `exists()` | **KILLED** | Directory marker must be UNKNOWN |
| m5 ACTIVE on started alone | **KILLED** | Started + exited must be retained |
| m6 Original two-marker set | **KILLED** | Refusal, exited, and refusal-family cases |

All mutant test processes exited 1. Mutation-induced `Refused` exceptions also occurred for m2/m5/m6; each had explicit assertion failures independently establishing the kill. [Detailed results](/tmp/retention-audit-3pdov0/replay/mutations.json).

**Q3 — full module**

Executed once:

```sh
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_evidence_night
```

Verbatim tail, exit 0:

```text
----------------------------------------------------------------------
Ran 94 tests in 272.515s

OK
```

**Authority comparison**

Both governing texts were read from `origin/bookkeeping/2026-09-21-activation-29ea94df`, ultimately pinned at `0cd42bd755b8db86d3f4e3df2ac453abfbf1326a`, under `docs/process_traces/2026-09-21-activation-29ea94df/05-coldgate-packet-a230-retained-root-discovery/`.

- `10-coldgate-fable-ruling.md:21–29`: Python classification and contract replacement conform.
- `10-coldgate-fable-ruling.md:39–50`: runbook paragraph conforms; shell loop is byte-identical after removing quotation prefixes. F1 therefore originates in the ruled text.
- `10-coldgate-fable-ruling.md:60`: handbook operative commands and stop rule conform.
- `10-coldgate-fable-ruling.md:68–75`: regression behaviors executed; all six requested mutations killed.

The refusal globs match `scripts/run_night.py:281–284`. Installer admission checks at `joulewise/night_agent_install.py:1130–1141` are broader than retention classification. `_record_chain_exit` at `scripts/run_night.py:411–427` also records failed launches; the ruling does not require successful execution for retention. Contract items 0 and 5 remain unchanged.

## Residual risk

A263 remains reproducible: at `t0 + 600`, a started-and-exited fixture returns `retained/pass` while `plan_span_active` returns `True`. This is the already-registered gap at `TASK_QUEUE.md:881`, described by `11-opus-contract-refuter.md:80–85` and implemented by `scripts/magistrate_watchdog.py:775–790`.

Live helper termination, respawn behavior, and hardware operation were not exercised. All writes stayed in scratch fixtures; the reviewed worktree remained clean at `fc28d782`. The next step is lead disposition of F1 and amendment of Q2’s manual loop.
## D3 Opus counter-review on 518a65a8
# Opus counter-review (gate ledger row 6) — 518a65a8 on fix/2026-09-21-retained-root-terminal-markers

Reviewer: Claude Opus 5, read-only, worktree `/Users/edr/code/JouleWise-wt-retention-29ea94df`, base main `9e0a4995`.

## Verdict: MERGE

No blocker. Four should-fixes are documentation/pinning, none of them changes an arm decision today, and all four are cheap follow-ups that do not need to gate this merge. The classifier is fail-closed in every state I could construct, the three real roots are unchanged, and the new tests kill the mutations the refuters named.

## Q1 — is the classification sound?

I tried to construct a custody root classified `retained` while a night process could still be alive or a courier could still write into it. Every construction is caught:

- **Refusal written before the chain, driver still running.** `scripts/run_night.py:625` writes `calibration-refusal.json` on the pre-chain path, so `chain.started` may be absent while the driver lives. Markers → `retained` by records alone; the span fence then reads `now <= plan_completion_epoch` (`magistrate_watchdog.py:774-776`) → `ACTIVE`. Caught, and only because of the fix round's span fence.
- **Courier still to write after `chain.exited`.** `plan_span_active` returns True through `t0 + window_max_s + COURIER_DEADLINE_S`, and after that until `deadman_epoch + COURIER_LOCK_FRESH_S` unless `courier.sent` exists. Caught.
- **Spurious second fire on a live root.** `_write_rerun_refusal` (`run_night.py:1740-1759`) writes `rerun.refusal*.json`, which matches none of `REFUSAL_RECORD_GLOBS` (`refusal-[0-9]*.json` does not match `rerun.refusal-01.json`). A rerun-only root stays UNKNOWN, which is the right answer, and the rerun itself does no work. Caught.
- **Unparseable or foreign-`custody_root` plan.** → UNKNOWN, refuses. Fail-closed.
- **Armed-but-not-started root (future t0).** No markers → UNKNOWN, refuses.

The one residual: **`plan_span_active` is evaluated with the ENTRY checkout's constants** (`PLAN_LEAD_S`, `COURIER_DEADLINE_S`, `COURIER_LOCK_FRESH_S`) against a sibling plan that may have been authored under a different repo head. If any of those constants shrinks, an old root could read `retained` while the watchdog that actually owns it still calls the span active. Not reachable today (the three live roots are long past every bound) and doubly fenced by check items 0 (`night_agents`) and 5 (census foreign-PID refusal), so it is a documentation debt, not a defect. Listed as should-fix S4.

Verdict on Q1: **sound for the purpose.** `retained_roots` is one of three independent fences in `check` (`evidence_night.py:909` night_agents, `:916` retained_roots, `:917` census); no single-fence evasion I could build survives all three.

## Q2 — is the `scripts.magistrate_watchdog` reuse legitimate?

**Yes, and it is established precedent in this very file.** `evidence_night.py:487` and `:569` already import `PLAN_LEAD_S, TERM_LEAD_S, KILL_LEAD_S` from the same module inside functions. The contract preamble scopes clone execution narrowly — "It checks plan identity, age and exclusive install close with the clone's code" (`evidence_night_entry.md:178-180`) — and item 5 names argv derivation and ancestry classification as the clone-executed pieces. Item 4 is not about H's artifacts at all: it judges *the machine's* sibling roots, which the clone has no privileged view of. Entry-checkout evaluation is the correct seat. `Storage(plan.parent)` is safe: `Storage.exists` (`magistrate_watchdog.py:272-273`) does not consult `self.root`, and `_write_path` is never reached because nothing writes. The function-local import keeps the 0.43 s watchdog import off the module path.

## Q3 — the three real roots (verbatim output)

`env PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'from joulewise import evidence_night as e; import json; print(json.dumps(e.retained_roots({"roots_under": "/Users/edr"}), indent=1))'`

```
{
 "inventory": [
  {
   "plan": "/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night_plan.json",
   "classification": "retained",
   "reason": null,
   "evidence": [
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night/courier.sent",
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night/result.json",
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night/chain.exited"
   ]
  },
  {
   "plan": "/Users/edr/night-custody/d079-epoch-25g83-derivation-n2-20260919/night_plan.json",
   "classification": "retained",
   "reason": null,
   "evidence": [
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n2-20260919/night/courier.sent",
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n2-20260919/night/result.json",
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n2-20260919/night/chain.exited"
   ]
  },
  {
   "plan": "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night_plan.json",
   "classification": "retained",
   "reason": null,
   "evidence": [
    "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night/courier.sent",
    "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night/result.json",
    "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night/chain.exited",
    "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night/refusal.json",
    "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night/refusal-01.json"
   ]
  }
 ],
 "now_epoch_s": 1790055130.28486,
 "verdict": "pass"
}
```

Three roots, all `retained`, verdict `pass`, no regression. `reason: null` proves the plans parsed and `plan_span_active` returned False for each (an unparsed plan would carry a `plan unreadable:` reason). The pilot root also exercises the new refusal-glob path with a real two-digit `refusal-01.json`.

## Q4 — tests

Fixtures are honest: `sibling_plan` (`tests/test_evidence_night.py:638-648`) is a full `joulewise.night_plan.v2` mapping, and the span test at `:826-833` proves it actually parses — `("ACTIVE", "plan span active (…)")` is only reachable through a successful `NightPlan.from_mapping`. No assertion is vacuous that I could find:

- `test_discovery_span_fence_reuses_the_watchdog_rule` walks all four branches of `plan_span_active` with explicit `now_epoch_s`, including both sides of `t0 + 9000 + COURIER_DEADLINE_S`, and imports the real constant rather than hard-coding it.
- `test_retained_root_classification_ruled_cases` covers all eight ruled Q4 cases plus the `refusal.json`-as-a-directory case, asserts exact full-path evidence lists (Astra F4's basename gap is cured), and separately pins the refusal-only **pass** verdict (`:781-798` rewrite) so the aggregate-fail assertion can no longer mask a wrong row.
- The precedence mutation (retained tested before active) is killed twice: `("chain.started", "calibration-refusal.json") → ACTIVE` and the courier-marker re-check at `:762`.

## Findings

**should-fix**

- **S1 — `joulewise/evidence_night.py:707` — `REFUSAL_RECORD_GLOBS` duplicates `run_night._refusal_paths` and nothing pins them together, while the contract (`docs/contracts/evidence_night_entry.md:224`) says classification is "any regular file matched by `run_night._refusal_paths`".** The stated rationale in the comment at `:703-705` ("mirrored here so the entry checkout classifies without importing the clone") is not correct: `scripts/run_night.py` is in the entry checkout exactly as `scripts/magistrate_watchdog.py` is — which the same function imports at `:713` — and it imports in ~0.00 s with no side effects (probed). Today the two glob tuples are character-identical, so this is drift risk, not a live defect. *Cure:* call `run_night._refusal_paths(night)` directly, or add one assertion test that `REFUSAL_RECORD_GLOBS` equals the globs `_refusal_paths` uses.
- **S2 — `docs/contracts/evidence_night_entry.md:234-235` — the retained trailing sentence now reads as a contradiction.** "Retention classification does not certify process liveness or completed delivery" sits nine lines below two new rules that are *exactly* liveness rules. A reader without project grounding will ask which one is true. *Cure:* rewrite as "Classifying a root `retained` certifies only that a terminal record exists and that the plan's span is over; it does not certify that the courier's delivery succeeded."
- **S3 — `docs/phase_2/derivation_night_runbook.md:743` — "Every line must read `retained`; an `ACTIVE` or `UNKNOWN` line … stops the arm."** Read alone this says the zsh loop is the gate. The correction — that the loop omits the span rule, so it can print `retained` where `check` says ACTIVE — arrives three paragraphs later at `:751-753`. *Cure:* put one clause at `:743` ("this loop reads records only and cannot see the span rule; `check` binds") instead of leaving it to the Source paragraph.
- **S4 — `docs/contracts/evidence_night_entry.md:230-232` — the span rule does not say whose constants apply.** `plan_span_active` runs from the entry checkout against plans authored under other repo heads, so `COURIER_DEADLINE_S` / `PLAN_LEAD_S` / `COURIER_LOCK_FRESH_S` may differ from those the plan was written under. *Cure:* add "evaluated with the entry checkout's timing constants, which may differ from the head that authored an older sibling plan."

**nit**

- **N1 — `docs/contracts/evidence_night_entry.md:226` — "`refusal-N.json`" is ungrounded.** The allocator writes two-digit names (`run_night.py:273`, `{index:02d}`) and the glob is `refusal-[0-9]*.json`. *Cure:* write "`refusal-01.json` and later numbers".
- **N2 — `joulewise/evidence_night.py:731` — `reason` is `null` for every retained row.** The record cannot distinguish "span evaluated and over" from "span never evaluated" without re-deriving it. *Cure:* set `reason = "terminal record present; plan span over"`.
- **N3 — `joulewise/evidence_night.py:736-737` — an unparseable plan on an otherwise plainly-harvested root is UNKNOWN with no cure but moving the root**, which is the property the ruling used to reject Q1 option (b) and which §0.7 now forbids ("Do not move or edit a root to change its line"). Not reachable today — all three live plans parse. *Cure:* none needed now; note it in A263's row so a future schema bump does not strand a harvested root.

## Q6 — merge-ability

Nothing to prune: I looked for overbuild and found none. The `now_epoch_s` parameter is load-bearing (it is the only way the span test pins both sides of a boundary), the `custody_root` realpath guard is what makes the borrowed span rule apply to the right root, and the `reason` field is the evidence the contract now promises. The two new tests plus the rewritten old one are proportionate to a contract change. Docs and code agree on every rule; TASK_QUEUE closes A230/A263 and opens A264 for the ruled Q3 follow-up, with both table copies (compatibility and lane) updated in step.

Missing for a safe merge: only the stated gate — local full replay green plus quick tier (the module alone was 92 tests / 180 s on `9e0a4995`, so the replay is the long pole), then hosted CI post-merge. I did not run the suite per my charge.

## Executed probes (all read-only, none inside the worktree)

- `git diff 9e0a4995..518a65a8` over all six files; `git log --oneline -3`.
- `git show origin/bookkeeping/…:…/10-coldgate-fable-ruling.md` (the ruling).
- The Q3 command above, verbatim output quoted.
- `sed -n 760,800p scripts/magistrate_watchdog.py` (`plan_span_active`, `plan_completion_epoch`), `grep -n "class Storage" -A 40` (`exists`, `_write_path`).
- `sed -n 270,300p scripts/run_night.py` (`_refusal_paths`, the `{index:02d}` allocator), `sed -n 1740,1775p` (`_write_rerun_refusal`), `grep -n 'rerun\.'`.
- `python3 -B -c "import scripts.magistrate_watchdog; import scripts.run_night"` with timing → 0.431 s / 0.000 s, no side effects.
- `sed -n 168,232p docs/contracts/evidence_night_entry.md`; `sed -n "$(grep -n 'def check(' …)",+45p joulewise/evidence_night.py`.
- `grep -nE "^[+-]\|" TASK_QUEUE.md` over the diff; scan of both refuter reports for their verdict blocks (Sol's A263 span gap, Astra's F4 evidence-path gap) to confirm the fix round answered them.
- NOT EXECUTED: the test suite (charge: a replay may be running in the worktree); no writes anywhere; no read of canonical, custody, staging, measurement or LaunchAgents paths beyond the Q3 probe's own discovery.
