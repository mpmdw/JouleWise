import json
KP = "docs/process/state_kernel.json"
k = json.load(open(KP)); T = k["tasks"]

GEN = {"path": "tests/test_gen_state.py",
       "label": "D-170 item 1 installed: test_satisfied_decision_dependency_requires_named_test_regression fails when a satisfied kind:decision dependency carries no producer-regression pointer (PR #273)"}
ARM = {"path": "tests/test_arm_readiness.py",
       "label": "D-170 item 3 installed: test_t0_liveness_bound_refuses_at_600s_plus_1ns fails when the 600 s liveness conjunct is absent (PR #274)"}

# 1. satisfy every pending D-170 dependency
n = 0
for tid, t in T.items():
    for d in t["dependencies"]:
        if d["kind"] == "decision" and d["target"] == "D-170" and d["state"] == "pending":
            d["state"] = "satisfied"
            d["evidence"] = dict(ARM if tid == "V5-TRANSACTION-01" else GEN)
            n += 1
print("D-170 deps satisfied:", n)

# 2. rows whose ONLY pending dep was D-170 -> queued
for tid in ["GAMMA-UNIT-ROSTER-GUARD-01", "S9-01B-REFUSAL-PRODUCER-CHECK-01",
            "S9-02-W10-SCOPE-P256-M1-01", "S9-03-GAMMA-PREFILL-PROMPT-OWNER-01",
            "S9-05-CAL-SCREEN-FLOOR-RULING-01", "S9-06-WINDOW-T0-GO-RECEIPT-GATE-01"]:
    t = T[tid]
    assert not any(d["state"] == "pending" and d["scope"] == "start" and d["strength"] == "hard"
                   for d in t["dependencies"]), tid
    assert t["status"] == "blocked", (tid, t["status"])
    t["status"] = "queued"
    t["status_note"] = ("UNBLOCKED 2026-09-03: the only thing holding this row was D-170's "
                        "hard-start decision gate, and D-170's three installing pull requests "
                        "(#273 items 1 and 4, #275 item 2, #274 item 3) are all merged to main. "
                        + t.get("status_note", ""))

# 3. T26-RULING-INSTALL-01 retired
t = T["T26-RULING-INSTALL-01"]
t["status"] = "shelved"
t["status_note"] = ("RETIRED 2026-09-03 (closed, not abandoned): this row existed to install the "
    "four T26 cold-gate verdicts, and all three of its branches have merged - #273 for items 1 and 4 "
    "(decision-log status form, Mission M0 line, D-160 pointer, gen_state producer-regression gate, "
    "tests/test_gen_state.py and tests/test_docs_freshness.py), #275 for item 2 (tracked pull-request "
    "template, advisory gate-ledger CI job, scripts/check_gate_ledger.py, tests/test_check_gate_ledger.py), "
    "and #274 for item 3 (the 600 s liveness conjunct in joulewise/arm_readiness.py with its boundary "
    "regressions in tests/test_arm_readiness.py and tests/test_arm_readiness_evidence_t0.py). Item 4's "
    "packet-input-list amendment was deferred to charter v3 by D-170 itself and now has its own owner row. "
    "The kernel has no retired status word, so this is recorded as shelved. Retirement prescribed by the "
    "2026-09-02 fresh-Fable docs-vs-truth audit A3. Prior note follows. " + t["status_note"])

# 4. ED-BRANCH-PROTECTION-E1-01 unblocked
t = T["ED-BRANCH-PROTECTION-E1-01"]
for d in t["dependencies"]:
    if d["target"] == "T26-RULING-INSTALL-01":
        d["state"] = "satisfied"
        d["evidence"] = {"path": "docs/decision_log.md",
                         "label": "T26-RULING-INSTALL-01 closed 2026-09-03: D-170's three installing PRs #273, #274 and #275 are merged and the gate-ledger job is live and advisory"}
t["status"] = "queued"
t["status_note"] = ("UNBLOCKED 2026-09-03 per the fresh-Fable docs-vs-truth audit A3: the installing row "
    "is closed and the advisory gate-ledger job is live, so the only thing left is Ed's hand on branch "
    "protection. " + t.get("status_note", ""))

json.dump(k, open(KP, "w"), indent=2, sort_keys=True, ensure_ascii=False)
open(KP, "a").write("\n")
print("ok")
