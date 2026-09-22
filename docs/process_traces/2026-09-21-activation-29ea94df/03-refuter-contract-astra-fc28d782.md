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