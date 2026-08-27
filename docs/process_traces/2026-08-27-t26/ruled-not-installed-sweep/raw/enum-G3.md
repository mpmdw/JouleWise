# G3 enumeration — D-126, D-127, D-128, D-129, D-130, D-131, D-132

Method note: every line cited below was opened and read at the stated line.
Branch-only implementations were checked with `git merge-base --is-ancestor`
against HEAD (`2fd7c920`, main) before being called NOT INSTALLED.

---

### D-126 · clause 1
- clause (verbatim): "Q4 (plus the two-site freeze test obligation on `_SUPPORTED_COUNT_BOUNDARY_RULES` and its recompute branch)"
- source: docs/decision_log.md:8149-8151
- status: C
- evidence: `grep -rn "SUPPORTED_COUNT_BOUNDARY" . --include=*.py --include=*.json --include=*.md` → the ONLY hit outside `.git/` and `docs/process_traces/` is docs/decision_log.md:8150 (the ruling itself). No Python symbol exists anywhere in the working tree.
- evidence: `git log --oneline -S"_SUPPORTED_COUNT_BOUNDARY_RULES" --all` → `e5cf2443` ("U2 rework round 2 (D-126 dispositions + D-125 envelope design) … Q4 two-site freeze test") and `6fc33b00`.
- evidence: `git merge-base --is-ancestor e5cf2443 HEAD` → NOT in main; `git branch -a --contains e5cf2443` → `impl/d117-u2-successor` / `remotes/origin/impl/d117-u2-successor` only.
- producer: none found on main (the U2 successor issuance path does not exist at HEAD)
- transaction_relevant: yes — the D-079/U2 acceptance corpus feeds the calibration acceptance bound that the floor mint and claim edge consume.
- note: the implementation exists on the UNMERGED branch `impl/d117-u2-successor`; nothing on main.

### D-126 · clause 2
- clause (verbatim): "Q5 (the cold judge's closure definition is BINDING — an observation ceases to be \"new\" only via an explicit decision-log disposition by content_id plus the next successor's prior_observation_set recording the disposing decision ID; consuming code lands with the first disposing ruling, not before)"
- source: docs/decision_log.md:8151-8156
- status: C
- evidence: joulewise/calibration_ledger.py:256 — `def content_id_from_artifact_hashes(...)` exists (the content_id primitive), but no disposition/closure seam consumes it: `grep -rn "disposing_decision_id\|prior_observation_set" joulewise scripts` returns only the ledger's *reading* of `prior_observation_set` (joulewise/calibration_bracketing.py:412, 1342, 1350, 1742; scripts/calibration_ledger_bootstrap.py:192-323) — no disposition record, no decision-log resolution.
- evidence: `git log -S"disposing_decision_id"` → the seam is on `e5cf2443` ("Q5 disposing_decision_id record seam only"), NOT an ancestor of HEAD.
- producer: none found on main
- transaction_relevant: yes — governs when the acceptance corpus may be closed and a successor bound minted, i.e. the claim edge.
- note: the ruling's own text ("consuming code lands with the first disposing ruling, not before") makes the absence of consuming code CONFORMANT so long as no disposing ruling has issued; but the record seam ruled in the same clause is also absent.

### D-126 · clause 3
- clause (verbatim): "Q8 (registry authority ratified; the migration shim DELETED by convergent ruling — `_load_registry_for_current_active_selection` collapses to the plain committed load)"
- source: docs/decision_log.md:8156-8159
- status: C
- evidence: `grep -rn "_load_registry_for_current_active_selection" .` (excluding `.git/`, `docs/process_traces/`) → only docs/decision_log.md:8157. The symbol has never existed on main.
- evidence: `git log --oneline -S"_load_registry_for_current_active_selection" --all` → `878ce9ed`, `e5cf2443`, both on `impl/d117-u2-successor` only.
- producer: none found on main
- transaction_relevant: yes — registry authority for the acceptance/successor selection consumed at mint time.
- note: this is NOT "deletion already done": the shim and its removal both live only on the unmerged branch.

### D-126 · clause 4
- clause (verbatim): "the Q13 n>=19 licensing floor"
- source: docs/decision_log.md:8159-8160
- status: C
- evidence: `grep -rn "licensing_floor\|budget_ceiling\|lineage_monotone\|screen_budget" joulewise scripts configs tests` → single hit, tests/test_whole_window_selection.py:116 (`test_screen_budget_refusals_are_bidirectionally_registered`), which is the unrelated whole-window claim-family screen (joulewise/whole_window.py:1789-1792, 2040), not the U2 licensing floor.
- evidence: joulewise/calibration_bracketing.py — no `n >= 19` / licensing-floor predicate (grepped for `19` filtered on floor/licen/minimum).
- producer: none found on main
- transaction_relevant: yes — an n floor on the acceptance corpus gates what may be licensed for claims.

### D-126 · clause 5
- clause (verbatim): "The silent clamp is removed; issuance refuses `successor_screen_exceeds_budget_ceiling` when screen >= ceiling; cap = ceiling − screen with no max(0,·); runtime classification and record fields per consult §6."
- source: docs/decision_log.md:8161-8165
- status: C
- evidence: `grep -rn "successor_screen_exceeds"` (whole tree minus `.git/` and process traces) → only docs/decision_log.md:8163.
- evidence: `git log --oneline -S"successor_screen_exceeds_budget_ceiling" --all` → `e5cf2443` only ("clamp removed, successor_screen_exceeds_budget_ceiling issuance refusal") — NOT an ancestor of HEAD.
- evidence: scripts/reissue_calibration_acceptance.py:1-9 — the only successor tooling on main is explicitly "preparation tooling only. It never writes an issued artifact: every output carries ``candidate_not_issued: true``… A later, separately governed issuance transaction must remove that marker".
- producer: scripts/reissue_calibration_acceptance.py is the nearest producer and has NO ceiling/screen refusal
- transaction_relevant: yes — issuance refusal on the acceptance bound is a claim-edge gate.

### D-126 · clause 6
- clause (verbatim): "Packet rule hardened (second occurrence of the truncation class): register/finding quotes run to END OF DOCUMENT SECTION, never to an assembler-chosen paragraph boundary."
- source: docs/decision_log.md:8166-8169
- status: C
- evidence: `grep -rn "END OF DOCUMENT SECTION\|end of document section\|run to end of" --include=*.md docs /Users/edr/.claude/skills .claude` (excluding process traces) → only docs/decision_log.md:8168. The rule appears in no packet-assembly doc, no skill (`council`, `adversarial-review`), no checklist, and no script.
- producer: packet assembly is agent-performed; no assembler script or brief template carries the rule
- transaction_relevant: no — governs adjudication-packet assembly, not any transaction artifact.

### D-126 · clause 7
- clause (verbatim): "Q10 DEFERRED to the recovery gate; the exception may not be exercised on a live night before the predicate re-verifies on the ledger-resident substrate."
- source: docs/decision_log.md:8170-8172
- status: C
- evidence: `grep -rn "Q10\|ledger-resident" joulewise scripts configs docs/phase_2 docs/process` → no live-night refusal predicate, no arm-readiness row, and no runbook line naming the deferred exception. The arm registry rows (configs/arm_readiness/d117_row_registry_v1.json, v2.json) contain no Q10 / ledger-resident-substrate row.
- producer: none found (the live-night gate would be joulewise/arm_readiness.py's row evaluation; no such row exists)
- transaction_relevant: yes — "may not be exercised on a live night" is an arm/window-time refusal that is not installed at arm.

### D-126 · clause 8
- clause (verbatim): "CH-1 (writer copied-scalar unit) deadline is before the first successor issuance or any live night relying on writer dispositions, whichever comes first."
- source: docs/decision_log.md:8173-8176
- status: A
- evidence: joulewise/arm_readiness.py:818 — `"copied_scalar_accepted": False,` inside the expected-fact block for the writer-acceptance readiness predicate (a readiness row PASSES only when the observed fact is `False`).
- evidence: joulewise/arm_readiness_evidence.py:929 — `copied_scalar_accepted = (` … :949 `if copied_scalar_accepted or unknown_key_accepted or not owner_verified:` (refusal branch) … :956 `"copied_scalar_accepted": False,` (the PASS record).
- evidence: TASK_QUEUE.md:391-397 — "AMENDED (2026-08-12, T6, CH-1 pre-merge lens): after CH-1's harness fix … PR #142 both interpreters green".
- producer: joulewise/arm_readiness_evidence.py (the readiness-evidence author) refuses at authoring time; joulewise/arm_readiness.py re-checks the fact at readiness evaluation.
- transaction_relevant: yes — a live-night arm gate.

### D-126 · clause 9
- clause (verbatim): "The U2 landing gauntlet REQUIRES a writer≠reviewer lens over the 965-line successor test surface (torn-publication, rollback, durability-uncertain, receipt-authentication paths). No successor can issue until rework round 2 + the remand resolution + the landing gauntlet + CH-1 have all landed."
- source: docs/decision_log.md:8176-8181
- status: C
- evidence: scripts/reissue_calibration_acceptance.py:1-9 — no issuance path exists on main at all, so nothing can enforce (or violate) the precondition; there is no gate script, no CI job, and no TASK_QUEUE acceptance predicate naming the four preconditions (`grep -rn "landing gauntlet" TASK_QUEUE.md docs/process/state_kernel.json` → no hit).
- producer: none found
- transaction_relevant: yes — gates issuance of the acceptance successor the mint would consume.
- note: currently vacuous (no issuance path), but the gate itself is uninstalled: were an issuance path added, nothing mechanical would hold it.

### D-126 · clause 10
- clause (verbatim): "Tuple rule: this decision ID replaces `COLD-GATE-U2-PENDING`; an issued artifact may never embed a tuple member with no decision-log entry."
- source: docs/decision_log.md:8181-8184
- status: C
- evidence: `grep -rn "COLD-GATE-U2-PENDING" .` (minus `.git/`, process traces) → docs/decision_log.md:8138, 8181 and docs/strategy/2026-08-08-40h-plan.md:60 only. No issued artifact embeds it.
- evidence: joulewise/calibration_bracketing.py:483 — `or value.get("decision_ids") != ["D-102", "D-109"]` — the only decision-ID check on main is an EXACT hard-coded two-element pin for the one live acceptance artifact. It is not a resolution of tuple members against docs/decision_log.md.
- evidence: `grep -rn "decision_ids\|decision_log" joulewise scripts` → the only other decision-log reader is joulewise/arm_readiness_evidence.py:813, which digests `docs/decision_log.md` as a committed artifact (byte pin) and never resolves IDs.
- producer: scripts/reissue_calibration_acceptance.py (candidate-only) — writes no decision-log resolution
- transaction_relevant: yes — issued acceptance/floor artifacts are consumed at mint and claim time.
- note: the branch commit `6fc33b00` records "five-ID decision-log resolution regression needs D-125/D-126 rows" — the resolver exists only on `impl/d117-u2-successor`.

---

### D-127 · clause 1
- clause (verbatim): "Claude Code drives the full experiment loop across multi-day unattended stretches: harvest → mint → judge → build/freeze next pack → toggle network time off → launch the supervisor → EXIT for the capture; the window's final step relaunches a fresh headless session."
- source: docs/decision_log.md:8192-8198
- status: C
- evidence: `grep -rln "relaunch\|supervisor\|launchd\|heartbeat\|liveness" scripts joulewise tests configs` → scripts/window_status.sh:28 and scripts/prewindow_check.sh:10 are COMMENTS ("None -- diagnosing, will relaunch automatically"; "diagnose-wait-relaunch cycle"), scripts/ed_session/sampler-checklist.sh:90 is the sampler-lifetime supervisor (unrelated), joulewise/controller.py:1235 is a sampler-liveness comment. No supervisor step, no relaunch, no headless-session launcher.
- evidence: `find . -name "*.plist" -not -path "./.git/*"` → only powermetrics fixtures and run outputs. No launchd job.
- evidence: scripts/launch_window.py:262-264 — "Successful execve never returns. There is deliberately no child process, wait path, or automatic retry after the capability's linearization point." The one launcher on main is explicitly non-supervisory.
- producer: none found
- transaction_relevant: yes — the measurement window's launch/relaunch lifecycle.
- note: registered but unbuilt as TASK_QUEUE.md:644 `A81 | UNATTENDED-LAUNCH-01 | BLOCKED — T0-UNATTENDED-01 … Build the unattended launch/relaunch harness (D-127 clause 4 …)`.

### D-127 · clause 2
- clause (verbatim): "Zero-agent during capture is UNCHANGED. The agent fully exits for the ~3h capture; this charter removes the human toggle and the relaunch gap, not the contamination fence."
- source: docs/decision_log.md:8199-8203
- status: A
- evidence: joulewise/arm_readiness_evidence_t0.py:1397 — `_fresh_probe(context, kind, "agent", ("/usr/bin/pgrep", "-lf", "codex|claude|t3"))` inside `_derive_process_census`.
- evidence: joulewise/arm_readiness_evidence_t0.py:1401-1402 — `for label, probe in zip(("keep-awake", "agent", "browser", "monitor"), probes, strict=True): _expect_absent(probe, kind=kind, label=label)` — an agent process present makes the row underivable, i.e. no T-0 evidence, i.e. no GO.
- evidence: joulewise/arm_readiness_evidence_t0.py:1404-1406 — the emitted row is `t0.no_stray_keepawake` with `{"absent_process_classes": ["agent", "browser", "keep_awake", "monitor"], "fresh_process_census": True}`.
- producer: joulewise/arm_readiness_evidence_t0.py `_derive_process_census` — the T-0 evidence author refuses to write the fact when an agent process is live.
- transaction_relevant: yes — the arm/T-0 gate on the measurement window.

### D-127 · clause 3
- clause (verbatim): "Scoped toggle. Sudoers rule for exactly the two fixed systemsetup network-time commands (exact path, exact argv, no wildcards)."
- source: docs/decision_log.md:8204-8206 (index row 152: "QUIET-GUARD sudoers slice: exactly the two fixed systemsetup network-time commands, exact binary path + exact argv, no wildcards")
- status: A
- evidence: scripts/joulewise-network-time.sudoers:2 — `Cmnd_Alias JOULEWISE_NETWORK_TIME = /usr/sbin/systemsetup -setusingnetworktime off, /usr/sbin/systemsetup -setusingnetworktime on` (absolute path, exact argv, no wildcards); :4 `edr ALL=(root) NOPASSWD: JOULEWISE_NETWORK_TIME`.
- evidence: scripts/capture_t0_step.py:616-622 — `("/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-setusingnetworktime", "off")` — the T-0 producer issues exactly the granted vector with `-n` (no password prompt).
- evidence: joulewise/arm_readiness_evidence_t0.py:864 — `if not _systemsetup_argv(disable["argv"], ("-setusingnetworktime", "off")):` — the evidence author refuses any other argv shape; :910-912 emits `clock.network_time_off` with `{"fresh_probe": True, "network_time": "off"}`.
- evidence: joulewise/arm_readiness.py:807-810 — `"clock.network_time_off.v1": {… "network_time": "off" …}` registered readiness predicate.
- evidence: tests/test_capture_t0_step.py:516-525 — `test_capture_paths_contain_no_privileged_network_time_get` asserts `self.assertNotIn("-getusingnetworktime", source)` (the un-granted vector can never be issued).
- producer: scripts/capture_t0_step.py `_command_for_step` (issues the argv) + joulewise/arm_readiness_evidence_t0.py `_derive_clock_probe` (refuses a wrong argv at evidence-authoring time)
- transaction_relevant: yes — T-0 clock discipline for the measurement window.

### D-127 · clause 4
- clause (verbatim): "D-115's install conditions bind (sudo -k fresh auth; authenticated staged content; interpreter isolation); Ed personally runs the single sudo install command after the artifacts clear their gauntlet."
- source: docs/decision_log.md:8210-8213
- status: A
- evidence: joulewise/arm_readiness.py:903-912 — three registered readiness predicates: `"privilege.fresh_authorization.v1": {"fresh_authorization_sequence": True, "sudo_k_reviewed": True}`, `"privilege.installed_bytes.v1": {"installed_digests_match_pack_staged_digests": True}`, `"privilege.isolated_interpreter.v1": {"frozen_isolated_interpreter_contract": True}`.
- evidence: joulewise/arm_readiness.py:1004-1007 — each maps to evidence kind `"PRIVILEGE_INSTALLATION"`.
- evidence: configs/arm_readiness/d117_row_registry_v1.json:27, 68, 109 — `"privilege.installed_bytes"` is a required row in all three plan profiles; :321-325 gives its predicate binding `"predicate_id": "privilege.installed_bytes.v1"`.
- evidence: docs/phase_2/window_runbook.md:555-578 — the tracked fragment's exact bytes + SHA-256 `7dfe980be89a7912d69c6e72b5582649fc4c50db88bf709bcfbb4a1c34e4406d`, and the ED-OWED install step "Ed alone installs `/etc/sudoers.d/joulewise-network-time`; no repository script runs as root."
- producer: joulewise/arm_readiness.py row evaluation refuses arm when the privilege rows do not carry PASS facts
- transaction_relevant: yes — arm-readiness gate.
- note: the installed-bytes digest itself is off-repo operator evidence (docs/run_reports/2026-08-18-t10-session.md:104 records the verified install). docs/phase_2/alpha_arm_readiness.md:130 is STALE — it still reads "STAGED BY #152; INSTALL EVIDENCE PENDING".

### D-127 · clause 5
- clause (verbatim): "Shape: preflight (binary, auth, disk state) → launch → liveness proof (the fresh session's first scripted action writes a heartbeat/claim file; launcher stands down only on proof) → bounded retries with backoff → independent launchd fallback timer as the second wake layer. Never one mechanism."
- source: docs/decision_log.md:8214-8222
- status: C
- evidence: same greps as D-127 clause 1 — no heartbeat/claim file writer, no retry/backoff loop, no launchd plist anywhere in the tree.
- evidence: TASK_QUEUE.md:644 — the row that would build it is `BLOCKED — T0-UNATTENDED-01`, with acceptance "A reviewed launch/relaunch harness exists implementing D-127 clause 4: autonomous initial foreground launch, verified post-window relaunch, liveness proof, bounded retries, independent launchd fallback" — i.e. the queue itself records the clause as unbuilt.
- producer: none found
- transaction_relevant: yes — the window launch lifecycle.

---

### D-128 · clause 1
- clause (verbatim): "\"Defensible\" is the bar, and it is conservative: the P1 MVP paper carrying measured numbers whose every claim survives the adjudicated trust model, the results-prose acceptance contract (template landed 1e6fa16), D-119 conservative wording, and the D-078 attribution-limited floors doctrine."
- source: docs/decision_log.md:8236-8242
- status: A (for the named artifact only)
- evidence: `git show --stat 1e6fa16` → merge "results-prose template with terminating conditional structure + fail-closed linter", adding `docs/process_traces/2026-08-07-plan-factory/lint_results_prose_template.py` (1006 lines) and `tests/test_results_prose_template.py` (180 lines).
- evidence: scripts/render_results_fills.py:58 — `/ "lint_results_prose_template.py"`; :73 `"results_prose_canonical_linter", CANONICAL_LINTER_PATH` — the renderer loads the canonical linter, so the acceptance contract is enforced at the point results prose is produced.
- evidence: docs/paper/results-fill-registry.md:95 — names the same linter path as the canonical authority.
- producer: scripts/render_results_fills.py (fail-closed via the loaded linter)
- transaction_relevant: yes — the claim edge (results prose carries the measured numbers).

### D-128 · clause 2
- clause (verbatim): "Unchanged fences (this mandate relaxes NOTHING): zero-agent capture; the full D-118 gate + D-121 terminal review on every merge; standing same-signature escalation and cold-gate triggers (U2's count-3 freeze stands as precedent); the lieutenant-forbidden list; Ed's owed rulings (Window-C funding, ruling 8 spec governance, wall-meter/artifact scope) remain his; any external claim release or publication remains Ed-gated."
- source: docs/decision_log.md:8243-8250
- status: A (zero-agent leg) / process elsewhere
- evidence: zero-agent leg — joulewise/arm_readiness_evidence_t0.py:1397, 1401-1402 (see D-127 clause 2).
- evidence: D-121 terminal review is a registered readiness row — joulewise/arm_readiness.py:1001 `"desk.terminal_review.v1": "TERMINAL_REVIEW"`, and joulewise/arm_readiness.py:5981-5982 `if row_id == "desk.terminal_review": return "readiness_terminal_review_missing"`.
- producer: joulewise/arm_readiness.py row evaluation
- transaction_relevant: yes — arm gate.
- note: the remaining legs (escalation triggers, lieutenant-forbidden list, Ed-gated publication) are authority rulings with no artifact and are skipped per the brief's exclusion.

### D-128 · clause 3
- clause (verbatim): "Morning surface. Each cycle leaves Ed a one-page morning state (what ran, what minted or refused and why, what the next night does, anything parked awaiting him) — RUN_STATE stays the pointer."
- source: docs/decision_log.md:8250-8251
- status: B
- evidence: RUN_STATE.md:1-17 — the file exists and opens as the pointer ("This file is the single running pointer for the project: the one doc to read to get back here") and carries a current-state block ("**T25 (2026-08-26) — PAUSED at an Ed checkpoint … RESUME FROM: …**").
- evidence: no producer-side check — `grep -rn "morning state\|morning surface" scripts joulewise docs/process/state_kernel.json` → no generator, no acceptance predicate, no test. scripts/gen_state.py:530 only emits a decision-log link, not a morning state.
- producer: none — RUN_STATE.md is hand-maintained; nothing refuses a cycle that ends without a morning state.
- transaction_relevant: no — an operator-communication surface, not a transaction artifact.

---

### D-129 · clause 1
- clause (verbatim): "Standing fan-out order. Fan-out to the degree demonstrated in T3 (~8 concurrent streams …) is the DEFAULT whenever it speeds work — not a per-session grant."
- source: docs/decision_log.md:8259-8266
- status: C
- evidence: `grep -rn "D-129" docs/orchestration.md docs/agent_playbook.md /Users/edr/.claude/skills` → the only doc hits are docs/orchestration.md:37 and :40, which record clause 3 (the stream-director amendment), NOT the fan-out order. The `multi-stream-worktrees` skill carries no D-129 fan-out default.
- producer: none — process directive; lives in the user's memory index (`standing-fanout-order.md`) which is outside this repo
- transaction_relevant: no — orchestration policy.

### D-129 · clause 2
- clause (verbatim): "Codex service tier. Fast-tier usage drops by roughly 60%. Default tier is the norm; the wrappers' 2026-08-08 fast-standing-default is superseded (their env default may lag — override per call with `CODEX_SERVICE_TIER=default`)."
- source: docs/decision_log.md:8267-8272
- status: B
- evidence: .claude/skills/codex/SKILL.md:58-63 — "Service tier (Ed 2026-08-09, supersedes the T1 fast-default): DEFAULT tier is the norm — launch with `CODEX_SERVICE_TIER=default` (the wrappers may still carry the old fast default; override it per call). Fast is reserved for the single run whose wall-clock directly gates the … merge/milestone; consolidate (one xhigh) rather than multiply fast runs. CODEX ONLY, never Anthropic fast."
- evidence: no producer-side enforcement — the wrapper (`~/.local/bin/codex-run-v3`) is personal tooling outside the repo and the ruling itself concedes "their env default may lag"; nothing in `scripts/codex-bridge`, `scripts/codex-run`, or `.mcp.json` sets or checks `CODEX_SERVICE_TIER` (`grep -rn CODEX_SERVICE_TIER scripts .mcp.json` → no hit).
- producer: the launch wrapper, which is not in this repo and does not enforce the default
- transaction_relevant: no — delegation-cost policy.

### D-129 · clause 3
- clause (verbatim): "This amends the operative \"stream director is now the exception\" framing in `docs/orchestration.md` (the C-009/C-010 stamped council consensus remains in place as the dated record it is); Opus-directed Sol lanes are now the standing default shape."
- source: docs/decision_log.md:8283-8288
- status: A
- evidence: docs/orchestration.md:37-41 — "mid-stream judgment, as a stream director. AMENDED by D-129 … default shape under the lead-token economy (current model assignments live in D-129 and the memory index, not here) — the \"exception rather …\"" — the required documentation change is present at the named file.
- producer: docs/orchestration.md (the doc named by the clause)
- transaction_relevant: no — orchestration doctrine.

---

### D-130 · clause 1
- clause (verbatim): "evidence bundle posted to the PR pre-merge and committed at `docs/evidence/d117-v2-decisive-20260811/` (contemporaneous worktree/interpreter/store attestations; durable copy in the window-custody store)"
- source: docs/decision_log.md:8318-8321
- status: A
- evidence: `ls docs/evidence/d117-v2-decisive-20260811/` → `EVIDENCE.md`, `decisive-local.log`, `decisive-local-py311.log`, `fullsuite-summary.log` — the committed bundle exists at the exact ruled path.
- producer: committed repository bytes
- transaction_relevant: yes — the D-117 production proof underwrites the trust chain the transaction depends on.

### D-130 · clause 2
- clause (verbatim): "the workflow de-triggered to `workflow_dispatch` in the first post-merge commit"
- source: docs/decision_log.md:8321-8323
- status: A
- evidence: .github/workflows/d117-production-proof.yml:12-13 — `on:` / `  workflow_dispatch:` (that is the entire trigger block).
- evidence: .github/workflows/d117-production-proof.yml:3-11 — the header comment records the closure and the 2026-08-16 re-deferral verbatim.
- producer: .github/workflows/d117-production-proof.yml
- transaction_relevant: yes — CI proof gate on the trust core.

### D-130 · clause 3
- clause (verbatim): "the two tracked \"required\"-wording contract sentences amended in the same commit"
- source: docs/decision_log.md:8323-8324
- status: UNVERIFIED
- evidence: `grep -rn "d117-production-proof" --include=*.md docs README.md` (excluding process traces) → only docs/council_log.md:89/3294/3345/3359 and docs/decision_log.md — no contract doc at HEAD contains a "required" sentence about the workflow; `grep -rn "advisory\|dispatch-only\|not a required" docs/contracts docs/process | grep -i "proof\|decisive\|d117"` → no output.
- producer: unknown
- transaction_relevant: yes — citation/claim wording about the decisive proof.
- note: UNVERIFIED — the clause does not name the two files or sentences, and I could not locate them at HEAD by phrase search; they may have been amended and since rewritten. I did not guess a status.

### D-130 · clause 4
- clause (verbatim): "WO-CI-RESTRUCTURE registered in TASK_QUEUE (matrix-split the attack legs to fit hosted limits; full trust gauntlet — proof-semantics work; deadline: before any claim publication and before the pack-freeze merge wave …)"
- source: docs/decision_log.md:8324-8330
- status: A
- evidence: TASK_QUEUE.md:130 — the registered row "WO-CI-RESTRUCTURE | P1 Phase Gate | 2026-08-11 | Split the D-117 decisive production proof into a registry-certified hosted matrix under the runner cap … Merged via #129 (`7a76a29`)".
- evidence: TASK_QUEUE.md:213 — "## WO-CI-RESTRUCTURE — CLOSED (D-130 condition; recorded 2026-08-15)".
- producer: TASK_QUEUE.md
- transaction_relevant: yes — the pack-freeze merge wave was gated on it.

### D-130 · clause 5
- clause (verbatim): "a committed one-command replay recipe (scripts/replay_d117_decisive.sh is the template)"
- source: docs/decision_log.md:8290 index row (line 155) / body 8289-8330 five-part substitution test
- status: A
- evidence: `ls -la scripts/replay_d117_decisive.sh` → present, mode 0755, 2143 bytes.
- producer: committed repository bytes
- transaction_relevant: yes — the substitution test for any future decisive-run venue call.

### D-130 · clause 6
- clause (verbatim): "a Python 3.11 local decisive replay owed post-merge (the decisive test has completed on no CI interpreter; refuter C3)"
- source: docs/decision_log.md:8329-8330
- status: A
- evidence: `docs/evidence/d117-v2-decisive-20260811/decisive-local-py311.log` exists in the committed bundle — the owed py3.11 replay is discharged in-repo.
- producer: committed repository bytes
- transaction_relevant: yes — interpreter coverage of the decisive proof.

### D-130 · clause 7 (closure section)
- clause (verbatim): "D-130's temporary mandatory wording — \"lead-verified locally … + CI-verified transport/authentication chain\" — is no longer required for future summaries … descriptions of that merge must still identify the custodied local decisive execution rather than recast it as a hosted decisive run."
- source: docs/decision_log.md:9831-9838
- status: B
- evidence: RUN_STATE.md:1903 — "lead-verified locally (custodied bundle: docs/evidence/d117-v2-decisive-20260811/)" — the historical description does carry the ruled provenance wording.
- evidence: no mechanical check — `grep -rn "CI-proven decisive"` returns nothing anywhere (so the forbidden phrase is absent), but neither scripts/claims_lint.py nor scripts/check_paper_replay_fence.py contains any rule about decisive-run provenance wording (`grep -n "decisive" scripts/claims_lint.py scripts/check_paper_replay_fence.py` → no hit).
- producer: prose authors; no linter enforces the provenance sentence
- transaction_relevant: yes — claim-edge citation discipline.

### D-130 · clause 8 (addendum)
- clause (verbatim): "The workflow returns to `workflow_dispatch` and WO-PROOF-RUNNABILITY-REPAIR is registered: repair the fixture drift under the full proof-semantics trust gauntlet the WO-CI-RESTRUCTURE registration prescribed, prove the matrix green at a current-main head, then restore automatic triggering in the same change."
- source: docs/decision_log.md:9840-9854
- status: A
- evidence: .github/workflows/d117-production-proof.yml:12-13 — trigger is `workflow_dispatch` only.
- evidence: TASK_QUEUE.md:634 — "A62 | WO-PROOF-RUNNABILITY-REPAIR | P2 Next Slice | READY [AGENT] | Repair the decisive-proof fixture drift against current main under the trust gauntlet and restore the workflow's automatic triggering".
- evidence: docs/process/state_kernel.json:4119-4151 — `"WO-PROOF-RUNNABILITY-REPAIR"` with its acceptance pointer and the inherited "WO-CI-RESTRUCTURE registration: proof-semantics work carries the full trust gauntlet" condition.
- producer: TASK_QUEUE.md + docs/process/state_kernel.json (the declared work-selection authority)
- transaction_relevant: yes — the decisive matrix is currently NOT runnable at main (the addendum's own finding).

---

### D-131 · clause 1
- clause (verbatim): "Receipt and custody. Identity projection uses the exact-key `joulewise.identity_pin_projection_receipt.v1` schema with no self-hash. Freeze receipts append under the pack's `identity_pin_projection.receipts/` directory and are authenticated by GNU-style SHA-256 sidecars plus the final plan tree. Arm re-verification is pack-read-only and writes its receipt under the bracket session in the window custody root. `projection_input_sha256` binds the closed declaration, config, model-file, and live-probe inventory rather than the final tree."
- source: docs/decision_log.md:8378-8388
- status: A
- evidence: joulewise/identity_pins.py:33-35 — `IDENTITY_PIN_PROJECTION_RECEIPT_SCHEMA = ("joulewise.identity_pin_projection_receipt.v1")`.
- evidence: joulewise/identity_pins.py:1866-1876 — `receipt_dir = root / "identity_pin_projection.receipts"`; the append number is `max(existing_numbers, default=0) + 1` and `receipt_rel = f"identity_pin_projection.receipts/{receipt_name}"`.
- evidence: joulewise/identity_pins.py:1905-1927 — the write set contains the receipt, its `.sha256` GNU sidecar (`_gnu_sidecar(receipt_sha, receipt_name)`), `plan_tree.json` and `plan_tree.sha256`, published through `_atomic_write_set(writes)`.
- evidence: joulewise/identity_pins.py:1835 — `receipt_units, projection_input_sha, checks = _derive_projection_units(root, projection)` — the input digest is derived from the declaration/config/model/probe inventory (joulewise/identity_pins.py:1330-1440), not from the final tree.
- evidence: joulewise/arm_readiness.py:2949-2952 — `"identity_pin_projection.receipts"` is a recognised custody directory; :2968 "``identity_pin_projection.receipts`` holds U11 identity-pin projection…".
- evidence: joulewise/arm_readiness.py:5122-5152 — `_read_identity_projection_receipt` recomputes the digest and requires `sidecar == gnu_sidecar(digest, path.name)`, else `readiness_identity_pinset_frozen_mismatch`.
- evidence: tests/test_identity_pins.py:508 `test_freeze_writes_authenticated_exact_key_receipt_and_is_idempotent`; :532 `test_verify_is_pack_read_only_and_writes_custody_receipt`.
- producer: joulewise/identity_pins.py `freeze_projection` (writes) — refuses non-conforming state before writing; joulewise/arm_readiness.py `_read_identity_projection_receipt` re-checks at arm.
- transaction_relevant: yes — the `_v4` freeze/projection step and the arm gate.

### D-131 · clause 2a (gamma roster)
- clause (verbatim): "Gamma carries exactly four ordered units: `A/decode`, `A/prefill_p256`, `B/decode`, and `B/prefill_p256`; A references the 1.5B producer and B references the 7B producer."
- source: docs/decision_log.md:8390-8393
- status: B
- evidence: configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:1622-1626 — `for arm, measurement_arm in (("A", "decode"), ("A", "prefill_p256"), ("B", "decode"), ("B", "prefill_p256")):` — the generator emits exactly the four ordered units; :1636 `"identity_unit_id": f"{arm}/{measurement_arm}"`.
- evidence: configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:1611-1620 — `producer_plans = {"A": {…qwen25-1p5b…}, "B": {…qwen25-7b…}}`, satisfying the A→1.5B / B→7B binding.
- evidence: NO producer-side check on the roster — joulewise/identity_pins.py:469-544 `validate_identity_pin_projection` (which the generator calls at :1676) enforces exact keys, lifecycle state, null-pins-before-projection and ID UNIQUENESS (`if len(unit_ids) != len(set(unit_ids))`, :531-535) but contains **no** cardinality, ordering, or per-family roster rule. A gamma pack declaring three units, or `B/decode` before `A/decode`, or a `C/decode`, validates clean.
- evidence: arm-side is equally roster-blind — joulewise/arm_readiness.py:5205-5208 compares the receipt's unit list to the PACK's unit list (`[unit["identity_unit_id"] for unit in receipt…] != [… for unit in projection…]`), i.e. self-consistency, never against the ruled canonical roster.
- producer: configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v{1,2,3}/generate_configs.py — emits the right value; no check refuses a wrong one
- transaction_relevant: yes — the gamma unit roster is what the `_v4` freeze projects and what arm re-verifies; a wrong roster would freeze and arm clean.
- note: this is the D-157 shape in miniature — right bytes today, by hand-written literal, with no rule that would catch a regeneration that drifted.

### D-131 · clause 2b (alpha/beta cardinality)
- clause (verbatim): "Alpha and beta each carry one ordered identity unit."
- source: docs/decision_log.md:8389-8390
- status: D
- evidence: configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:1755-1796 — the alpha pack emits TWO units, `"identity_unit_id": "alpha"` (:1757) and `"identity_unit_id": "alpha/prefill_p256"` (:1796). Same shape for beta: configs/campaigns/d117_floor_qwen25_7b_v3/generate_configs.py:1316 (`"beta"`) and :1355 (`"beta/prefill_p256"`).
- evidence: superseded by D-139 clause A2 — docs/decision_log.md:164 (index) "A2 stats delegated — Holm alpha=0.05 m=2 family (decode + prefill_p256, two-sided) adopted, **dedicated p256 floor**"; body at docs/decision_log.md:8825-8826 "A2: Holm alpha=0.05 m=2 family (decode + prefill_p256, two-sided); dedicated p256 floor."
- producer: configs/campaigns/d117_floor_qwen25_*/generate_configs.py
- transaction_relevant: yes — the alpha/beta packs are `_v4` mint inputs.
- note: D — the dedicated p256 floor ruled by D-139 A2 (docs/decision_log.md:164, 8825-8826) adds the second unit; D-131's one-unit statement no longer binds.

### D-131 · clause 2c (shared triple)
- clause (verbatim): "Every unit carries the same model/runtime/config triple used by the shared floor mint. The former gamma A/B model map and pack-wide runtime/config pins are invalid."
- source: docs/decision_log.md:8393-8396
- status: A
- evidence: joulewise/identity_pins.py:1424-1428 — the freeze compares the runtime-probe model digest against the shared enumeration and raises `readiness_identity_projection_mint_divergence` ("identity unit … runtime/shared model enumeration diverged") on any difference.
- evidence: joulewise/identity_pins.py:73-77 `MODEL_RUNTIME_CONFIG_FIELDS` is a per-UNIT field set; joulewise/identity_pins.py:497-521 validates it per unit (`identity_units[{index}].model_runtime_config`) — there is no pack-wide pin slot to populate.
- evidence: the shared implementation is genuinely shared — scripts/mint_floor_artifact.py:48 and scripts/mint_floor_artifact_generalized.py:59 both import from `joulewise.identity_pins`; tests/test_identity_pins.py:399 `test_synthetic_pack_triple_equals_generalized_mint_rederivation`.
- producer: joulewise/identity_pins.py `_derive_projection_units` — refuses at freeze time
- transaction_relevant: yes — the `_v4` mint and freeze.

### D-131 · clause 3
- clause (verbatim): "Derive; never enter. No operator, CLI option, launch recipe, or public verifier callable may supply or override an identity pin. Model enumeration, scientific-config identity, the governed eleven-field stack identity, and triple derivation have one shared implementation consumed by runtime collection, both mint paths, analysis, detection-floor validation, freeze, and arm verification. Any pack-versus-config or frozen-versus-live mismatch fails closed."
- source: docs/decision_log.md:8396-8405
- status: A
- evidence: scripts/project_identity_pins.py:23-38 — the entire CLI surface is `freeze <pack_root>` and `verify <pack_root> --window-custody-root --bracket-session-id`. No pin option exists.
- evidence: joulewise/identity_pins.py:520-524 — unprojected packs must carry null pins: `if set(runtime.values()) != {None} or projection["projection_receipt"] is not None: raise … "unprojected state requires null pins and null receipt"` — a serialized operator-entered pin is refused.
- evidence: one shared implementation, consumed where ruled — joulewise/analysis_manifest_v3.py:3122 (`from joulewise.identity_pins import build_stack_identity, stack_identity_sha256`, used :3150-3156) = analysis; joulewise/detection_floor.py:42-45 = detection-floor validation; scripts/mint_floor_artifact.py:48 and scripts/mint_floor_artifact_generalized.py:59 = both mint paths; joulewise/analysis_engine/inputs.py:58-60 = claim-side inputs; joulewise/arm_readiness.py:28 = arm verification; joulewise/identity_pins.py `freeze_projection` = freeze; joulewise/identity_pins.py:1251 `_runtime_probe_metadata` = runtime collection.
- evidence: fail-closed — joulewise/identity_pins.py:1346-1352 (config bytes changed → `readiness_identity_environment_dirty`), :1376-1382 (pack-vs-config declaration mismatch), :1424-1428 (frozen-vs-live model divergence).
- evidence: tests/test_identity_pins.py:1105 `test_cli_and_public_arm_callables_accept_no_identity_values`; :1128 `test_cli_refuses_unknown_identity_override_options`; :1144 `test_unprojected_pack_refuses_serialized_operator_pin_values`; :671 `test_one_byte_model_perturbation_changes_hash_and_refuses_dirty`.
- producer: joulewise/identity_pins.py `freeze_projection` / `_derive_projection_units`
- transaction_relevant: yes — the `_v4` freeze/projection and arm verification.

### D-131 · clause 4
- clause (verbatim): "Lifecycle and successor. Active packs are `unprojected` or `frozen`; `superseded` is inactive. Null pins and a null receipt are legal only before projection. Freeze is the sole `unprojected` to `frozen` transition and is byte-idempotent on the identical frozen projection; verify cannot mutate the pack. Reissue creates a new pack/custody root and appends a new receipt whose `supersedes` record binds the old pack, receipt, and readiness hashes; old receipts are never edited or deleted, and an opened session or attempt ID is never reused."
- source: docs/decision_log.md:8405-8412
- status: A
- evidence: joulewise/identity_pins.py:479-483 — state is validated against exactly `{"unprojected", "frozen", "superseded"}`.
- evidence: joulewise/identity_pins.py:1831-1834 — `if projection["state"] == "superseded": raise … "superseded packs cannot be frozen"`.
- evidence: joulewise/identity_pins.py:1838-1864 — the already-frozen branch re-derives and requires `projection_input_sha256` and every unit's `model_runtime_config` to match, then returns `"mutated": False` — byte idempotence, refusing with `"frozen projection is not idempotent"` otherwise.
- evidence: joulewise/identity_pins.py:1866-1874 — the receipt number is `max(existing)+1` and the name is `projection-{number:04d}.json`, so an existing receipt is never overwritten; joulewise/identity_pins.py:958-964 pins the receipt-name regex used for successor discovery.
- evidence: joulewise/identity_pins.py:444-467 `_validate_supersedes` validates the supersession record fields (:146-152 `SUPERSESSION_FIELDS`).
- evidence: tests/test_identity_pins.py:769 `test_successor_reissue_appends_supersession_without_reusing_receipt`; :745 `test_frozen_pin_mutation_refuses_with_frozen_mismatch`; :532 (verify is pack-read-only).
- producer: joulewise/identity_pins.py `freeze_projection`; the only other writer-shaped function, joulewise/arm_readiness_evidence.py:1303-1384 `_replay_projection_write_set`, RETURNS a write set for byte comparison and does not write (and refuses an already-frozen or superseded anchor at :1327-1337).
- transaction_relevant: yes — freeze/reissue at the `_v4` transaction.

### D-131 · clause 5
- clause (verbatim): "Readiness boundary. U11 exposes `verify_frozen_projection()` and its CLI receipt only. U8 owns the readiness-record `identity_pin_projection` section binding frozen and arm receipt path/SHA pairs, derivation contract, ordered unit IDs, and PASS status. Every U11 reason makes readiness REFUSE. No D-117 pack may arm before that U8 consumer lands and passes."
- source: docs/decision_log.md:8412-8415
- status: A
- evidence: joulewise/arm_readiness.py:846-848 — the registered predicate `"desk.identity_pin_projection.v1": {"projection_status": "PASS"}`; :993 maps it to evidence kind `"IDENTITY_PIN_PROJECTION"`.
- evidence: joulewise/arm_readiness.py:5164-5231 `_load_frozen_identity_evidence` binds the FROZEN receipt path/SHA and compares ordered unit IDs and triples (:5205-5208), returning the reason codes on any mismatch; :5214-5215 `if receipt["status"] != "PASS": return None, None, list(receipt["reason_codes"])`.
- evidence: joulewise/arm_readiness.py:5233-5281 `_run_identity_arm_reverification` calls `verify_frozen_projection(pack_root, custody_root, bracket_session_id)`, requires the receipt to live under the window custody pack root (else `readiness_identity_artifact_unreadable`, :5246-5250), and returns its status + reasons.
- evidence: every U11 reason forces REFUSE — joulewise/arm_readiness.py:6656-6658 and :7676-7678 pass `forced_reason_codes={"desk.identity_pin_projection": identity_reasons}` into `_evaluate_rows`; joulewise/arm_readiness.py:5982-5983 `if row_id == "desk.identity_pin_projection": return "readiness_identity_artifact_unreadable"` for a missing row.
- evidence: the row is required in every plan profile — configs/arm_readiness/d117_row_registry_v1.json:27, 68, 109 and d117_row_registry_v2.json:456, 559, 600.
- evidence: tests/test_identity_pins.py:1064 `test_u8_consumption_seam_can_fail_closed_on_u11_result`.
- producer: joulewise/arm_readiness.py readiness-record minting (`_evaluate_rows` + the forced-reason plumbing)
- transaction_relevant: yes — the arm gate for every `_v4` pack.

### D-131 · clause 6 (index row: closed refusal vocabulary)
- clause (verbatim): "closed refusal vocabulary"
- source: docs/decision_log.md:156 (index row D-131)
- status: A
- evidence: joulewise/identity_pins.py:38-47 — `IDENTITY_PIN_PROJECTION_REASON_CODES = frozenset(…)`.
- evidence: tests/test_identity_pins.py:1169 `test_projection_reason_vocabulary_is_closed`; :1183 `test_projection_reasons_are_registered_in_d078_decision_vocabulary`.
- producer: joulewise/identity_pins.py — every refusal path raises `IdentityPinProjectionError` with a code from the closed set
- transaction_relevant: yes — refusal codes cross the arm/consumption edge.

---

### D-132 · clause 1
- clause (verbatim): "REVIVAL DESIGN (round 6): delete the public registered surface entirely; the estimator becomes internal to the governed extraction pipeline and a registered result exists only as an artifact of that path — the admitted-input class closes by construction."
- source: docs/decision_log.md:8455-8461
- status: D
- evidence: superseded by D-133 — docs/decision_log.md:158 (index) "FCM-01 DISPOSITION — HYBRID + ALT-D120 (cold gate revised sitting, 2026-08-11): round-6 delta REJECT (FCM6-01, forged registration admitted by validators) … FCM-01 continues unmerged under ALT-D120 — DELETE serialized registration vocabulary so forgeries die as closed-profile unknown-key refusals"; body docs/decision_log.md:8471-8500, disposition (2) at :8497-8500.
- evidence: on main the estimator is already internal-only — joulewise/floor_mint_estimator.py:1-5 "The committed extraction spec is the only estimator authority. Registration data authorizes an internal arithmetic path; it is never projected into an extraction report, floor artifact, or artifact provenance record."; `__all__` at :32-36 exposes only `selection_from_authenticated_spec`, `recompute_comparative_estimate`, `bind_v2_floor_artifact_evidence`.
- evidence: D-133's bench findings hold at HEAD — `grep -n "register" joulewise/floor_mint_estimator.py` shows no serialized registration vocabulary; the round-6 revival lives on the unmerged branches `impl/floor-commonmode-01` / `impl/tighter-floor-respec`.
- producer: joulewise/floor_mint_estimator.py (internal), consumed by scripts/mint_floor_artifact.py:59 and scripts/mint_floor_artifact_generalized.py:58
- transaction_relevant: yes — the floor mint feeds the claim edge.
- note: D — D-133 (docs/decision_log.md:158; body 8471) rejected the round-6 delta and replaced the revival design with ALT-D120; TASK_QUEUE.md:833-834 records "FCM-01's withdrawal (D-133)".

### D-132 · clause 2
- clause (verbatim): "The re-spec-to-default branch stays unmerged as the ready fallback until the revival round's delta verdict."
- source: docs/decision_log.md:8461-8464
- status: D
- evidence: `git branch -a` → `respec/d124-withdrawn` and `remotes/origin/respec/d124-withdrawn` exist and are unmerged (also `impl/tighter-floor-respec`, `impl/floor-commonmode-01`).
- evidence: superseded by D-133 disposition (1) — docs/decision_log.md:8496-8499: "Fallback `respec/d124-withdrawn` (681ab49) merges after its own gate shape (fresh delta audit + re-verified generator/--check/dual-interpreter evidence + D-121); the pack-freeze lane unblocks at that merge and FCM-01 may not gate it thereafter."
- producer: git branch state
- transaction_relevant: yes — the pack-freeze lane was gated on it.
- note: D — D-133 changed the branch's condition from "stays unmerged until the delta verdict" to "merges after its own gate shape".

### D-132 · clause 3
- clause (verbatim): "Rust disposition (Ed's question answered): a Rust core would hold the unforgeable-token property Python cannot … It is affirmed as the H2/H3 answer for the next-generation instrument core, not a P1 dependency."
- source: docs/decision_log.md:8465-8470
- status: skipped — not an implementation clause
- evidence: names no artifact, no check, and no required document; explicitly deferred out of P1.
- producer: n/a
- transaction_relevant: no

### D-132 · clause 4 (the principle)
- clause (verbatim): "meta-process stop rules exist to kill non-converging loops — same defect recurring, no durable progress. They must NEVER terminate work on an instrument or component that is demonstrably converging … PROGRESS TOWARD A PUBLISHABLE PAPER IS THE HIGHEST-ORDER GOAL and all process rules rank below it"
- source: docs/decision_log.md:8438-8447
- status: C (borderline — see note)
- evidence: `grep -rn "D-132" docs/orchestration.md docs/agent_playbook.md /Users/edr/.claude/skills` → the ONLY hits are in the personal skill-usage log (/Users/edr/.claude/skills/skill-usage-log.md:553, 563), which is a dated session record, not a rule surface. Neither the `council` skill (which owns stopping rules and the fresh-eyes sweep) nor `adversarial-review` (which owns the round-count triggers) carries the D-132 carve-out.
- producer: none — the doctrine lives only in the decision log
- transaction_relevant: no — process doctrine.
- note: borderline under the brief's exclusion for "pure authority/process rulings with no artifact". I record it as C because the ruling amends stopping rules whose ONE home is the `council` / `adversarial-review` skills, and that amendment was never propagated there — a future stopping-rule execution reading those skills would not see the carve-out.
