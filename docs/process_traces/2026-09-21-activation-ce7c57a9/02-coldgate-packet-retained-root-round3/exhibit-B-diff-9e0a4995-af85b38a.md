# Exhibit B — git diff 9e0a4995..af85b38a (base main at lane start .. merge candidate), verbatim

```diff
diff --git a/TASK_QUEUE.md b/TASK_QUEUE.md
index aa14444a..0a3ec4f3 100644
--- a/TASK_QUEUE.md
+++ b/TASK_QUEUE.md
@@ -855,7 +855,7 @@ Generated compatibility table for repository consumers; the lane tables below ar
 | A226 | CUSTODY-REAPING-ATTRIBUTION-01 | P3 Hardening Candidates | READY [AGENT] | The custody worker (joulewise/calibration_custody_worker.py) is a short-lived child process the parent spawns to perform custody reads; production is required to reap it, that is, to call wait() on the child after termination so that no zombie (a finished process whose exit status no one has collected) is left behind. The late-child regression in tests/test_calibration_custody_worker.py performs that reap itself, via children[0].wait(), before making its assertions. Because the test collects the exit status, a mutant of production that terminates the worker but never reaps it passes both the pre-delta test (0.286 s) and the post-delta test (0.141 s). The test therefore does not attribute reaping to production code, and no other test does: the delta re-audit recorded this as verification gap R1, with replay script probe_reaping.py under /tmp/reaudit-A/mutation and logs reaping-base.log and reaping-only.log. The behaviour predates the NIGHT-RESERVE-HANG-01 delta; what is missing is proof, not the reaping itself. | A regression fails when production stops reaping the custody worker: the test must not call wait() on the child, and must observe from outside the parent -- for example, a separate process checking that no process in zombie state remains with the parent alive after the parent's custody call returns -- so that a terminate-without-reap mutant is killed. Demonstrate the kill by running the new test against a production copy with the reap removed and quoting the failing assertion. Existing custody-worker tests, including the launch-barrier and group-termination proofs, remain unchanged and still pass. Evidence: docs/process_traces/2026-09-16-activation-9853dd2b/27-seat-A-delta-reaudit-report.md flag R1 (verification_gap, nonblocking): the late-child test reaps via children[0].wait(), a terminate-without-reap mutant passes both the base test at 0.286 s and the revised test at 0.141 s, so production-owned reaping is not independently proved; replay probe_reaping.py in /tmp/reaudit-A/mutation, evidence reaping-base.log and reaping-only.log; tests/test_calibration_custody_worker.py (late-child test; the reap it performs itself is what masks the mutant); joulewise/calibration_custody_worker.py and the parent's spawn and collection path in joulewise/calibration_ledger.py (worker spawned at :2038, results required at :2100-2108). Authority: [2026-09-17 activation 9853dd2b, NIGHT-RESERVE-HANG-01 review findings; registration by the magistrate, not a ruling](docs/process_traces/2026-09-16-activation-9853dd2b/00-launch-record.md). Acceptance: [CUSTODY-REAPING-ATTRIBUTION-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-17 activation 9853dd2b: magistrate registration from the NIGHT-RESERVE-HANG-01 review round, not a ruling; not started; test-strength hardening, not night-critical. The re-audit recorded R1 as predating the delta and nonblocking; the replay materials under /tmp are scratch and may be gone, so the lane rebuilds the mutant rather than depending on them. Lands under the twelve-row gate. |
 | A228 | COLDGATE-CONVENE-DOCTRINE-FREE-01 | P3 Hardening Candidates | READY [AGENT] | The cold-gate charter (docs/process/coldgate_charter.md) says the charter is the ONE process context a cold adjudication instance receives and that the project's operating doctrine is deliberately withheld; the convening pattern in use runs the judge with `claude -p` from a linked JouleWise worktree, so the tracked project CLAUDE.md, the user-level ~/.claude/CLAUDE.md and the memory index MEMORY.md auto-load before the judge reads the packet (rulings 61 and 69 both disclose this honestly). The judge is asked to disclose auto-loads rather than prevented from receiving them, so 'cold' is nominal. Both rulings stood because the paired Opus refuter re-derived every load-bearing probe independently. | The council (not the magistrate) decides the convening shape: a judge tree without the tracked CLAUDE.md (e.g. an export of the checkout with that file removed, digests pinned) and a HOME override carrying no memory index or user doctrine; the convene script records what the judge could load; a regression or checklist item in the convening pattern fails the convening when a doctrine file is present in the judge's tree. Until decided, every convening records the auto-loaded files in the ruling's disclosure (already the practice) and pairs an Opus refuter (already the practice). Process observation for the council; no rule text is amended by this registration. Evidence: docs/process_traces/2026-09-16-activation-9853dd2b/69-coldgate-packet-prereg-chain-digest/12-opus-pairing-refuter-on-ruling-10.md (B1); docs/process_traces/2026-09-16-activation-9853dd2b/69-coldgate-packet-prereg-chain-digest/10-coldgate-fable-ruling.md (section 0 disclosure); docs/process/coldgate_charter.md (the ONE-context clause). Authority: [2026-09-17 activation 9853dd2b, flagged by the Opus pairing refuter of cold gate 69; registration by the magistrate for the council, not a ruling](docs/process_traces/2026-09-16-activation-9853dd2b/00-launch-record.md). Acceptance: [COLDGATE-CONVENE-DOCTRINE-FREE-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-17 activation 9853dd2b: registered for the council; not started; no night depends on it. |
 | A229 | TEST-WALLCLOCK-ABORT-FIXTURE-MARGIN-01 | P3 Hardening Candidates | READY [AGENT] | tests/test_run_night.py WindowDeadlineTests.test_an_abort_that_spends_its_whole_budget_is_not_interrupted (the NIGHT-STALL-WALLCLOCK-ABORT-01 regression) arms a chain that sleeps 3 s against a 2 s window plus a 3.0 s patched grace, so the chain must exit within a 1 s margin of the driver's wall-clock deadline. On the hosted runner at main c613e71e (run 35269617966, job test (3.13, 3)) it failed with AssertionError: 0 != 4 (the driver aborted the chain that was meant to finish inside the grace); locally at the same head it passed 4 of 5 runs, the one failure under load. The production inequality the test also asserts (CUSTODY_BUDGET_S 120 <= WINDOW_SHUTDOWN_GRACE_S 300 - TERMINATION_BOUND_S 70) is unaffected; the flake is the scaled fixture's margin. | The fixture's timing margin is widened (a larger patched grace against the same 3 s chain, or the deadline asserted from the driver's own recorded epochs rather than a live sleep race) so that ten consecutive runs under `python3 scripts/shard_tests.py`-level load pass locally and the hosted matrix is green at the fix head; the production inequality assertion is kept verbatim. Evidence: docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-record-n1-20260917.md (section Hosted CI at H); tests/test_run_night.py (WindowDeadlineTests, fixture _arm grace_s). Authority: [2026-09-17 activation 9853dd2b, arm record 77 (n1-20260917); registration by the magistrate, not a ruling](docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-record-n1-20260917.md). Acceptance: [TEST-WALLCLOCK-ABORT-FIXTURE-MARGIN-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-17 activation 9853dd2b: FIX MERGED as PR #356 (main 3fc54a6a; Opus refuter CONFIRM record 79; full replay record 80, 6352 tests 0 failures). The lane stays open for the refuter's two residual test-strength points only: (1) the widened fixture no longer discriminates partial-grace mutants (a grace/2 driver survives; sibling exact-arithmetic assertions cover it); (2) the test never asserts that the chain actually outlived the window end, so a later window_max_s edit could make it pass vacuously — add an explicit chain-end-vs-window-end assertion. Hosted CI failed the same shard a third time on the docs-only main 3d8e5807 before the fix; the successor confirms hosted CI green on 3fc54a6a or later. |
-| A230 | NIGHT-ROOT-RETENTION-DISCOVERY-01 | P2 Next Slice | READY [AGENT] | docs/phase_2/derivation_night_runbook.md section 0.7 says the arm precondition `print -rl -- /Users/edr/night-custody/*/night_plan.json(N)` must print nothing, while docs/process/NIGHT_HANDBACK.md section Next lane rules that the clone and night root of a night that opened a ledger session are RETAINED (only a refused night's plan root is retired). After the 2026-09-16 night, which opened a session, its root /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916 stays discoverable by that glob, so the two texts contradict each other for every retained root. The watchdog fences only active spans (plan_span_active, plan_is_armed in scripts/magistrate_watchdog.py) and the installer reads no sibling, so a completed retained root arms nothing; the 2026-09-17 arm proceeded on that reading and recorded it (arm record 77). | One rule holds in both documents, chosen by the cold gate or Ed (rule 11): either retained roots move out of discovery to a retained-custody location that is not /Users/edr/night-custody/<plan_id> (with the handback's retention wording and the inventory updated), or section 0.7's precondition is restated as 'no plan whose span is active or whose agents are installed', with the executable check that the watchdog already applies; the runbook and the handback then say the same thing and the arm scripts assert the executable form. Evidence: docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-record-n1-20260917.md (section Step 2, discovery bullet); docs/phase_2/derivation_night_runbook.md (section 0.7); docs/process/NIGHT_HANDBACK.md (section Next lane, retention sentence). Authority: [2026-09-17 activation 9853dd2b, arm record 77 (n1-20260917); registration by the magistrate, not a ruling](docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-record-n1-20260917.md). Acceptance: [NIGHT-ROOT-RETENTION-DISCOVERY-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-17 activation 9853dd2b: docs contradiction found at the arm; magistrate registration, not a ruling; the 09-16 root was NOT moved (the launch charge forbids moving plan directories this session did not author). Goes to the cold gate or Ed before the next harvest retires or retains a root. 2026-09-18 headless activation f0b608b7 (record 01): the 09-16 harvest archive `~/night-archive/d079-epoch-25g83-derivation-n1-20260916-harvest-20260916/`, found empty by arm record 21, was re-harvested byte-exact from the retained live root (20/20 sums OK against the live root and the copy, `SHA256SUMS` inside the archive, inventories identical); the 09-16 root remains retained under this lane's rule and may now be retired when the lane rules, with a complete archive. The 09-17 plan root was retired 2026-09-18 19:26 (arm record 21, step 0). 2026-09-19 — A third retained, inert night root (the directory holding a completed night's plan and evidence), `d079-epoch-25g83-derivation-n2-20260919`, now remains alongside the 2026-09-16 and `n1-20260919` roots. |
+| A230 | NIGHT-ROOT-RETENTION-DISCOVERY-01 | P2 Next Slice | DONE 2026-09-21 (cold-gate ruling packet 05 Q2 AFFIRMED option (ii): runbook §0.7 restated in the executable form, handback retention sentence unchanged; ruling docs/process_traces/2026-09-21-activation-29ea94df/05-coldgate-packet-a230-retained-root-discovery/10-coldgate-fable-ruling.md) [AGENT] | docs/phase_2/derivation_night_runbook.md section 0.7 says the arm precondition `print -rl -- /Users/edr/night-custody/*/night_plan.json(N)` must print nothing, while docs/process/NIGHT_HANDBACK.md section Next lane rules that the clone and night root of a night that opened a ledger session are RETAINED (only a refused night's plan root is retired). After the 2026-09-16 night, which opened a session, its root /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916 stays discoverable by that glob, so the two texts contradict each other for every retained root. The watchdog fences only active spans (plan_span_active, plan_is_armed in scripts/magistrate_watchdog.py) and the installer reads no sibling, so a completed retained root arms nothing; the 2026-09-17 arm proceeded on that reading and recorded it (arm record 77). | One rule holds in both documents, chosen by the cold gate or Ed (rule 11): either retained roots move out of discovery to a retained-custody location that is not /Users/edr/night-custody/<plan_id> (with the handback's retention wording and the inventory updated), or section 0.7's precondition is restated as 'no plan whose span is active or whose agents are installed', with the executable check that the watchdog already applies; the runbook and the handback then say the same thing and the arm scripts assert the executable form. Evidence: docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-record-n1-20260917.md (section Step 2, discovery bullet); docs/phase_2/derivation_night_runbook.md (section 0.7); docs/process/NIGHT_HANDBACK.md (section Next lane, retention sentence). Authority: [2026-09-17 activation 9853dd2b, arm record 77 (n1-20260917); registration by the magistrate, not a ruling](docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-record-n1-20260917.md). Acceptance: [NIGHT-ROOT-RETENTION-DISCOVERY-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-17 activation 9853dd2b: docs contradiction found at the arm; magistrate registration, not a ruling; the 09-16 root was NOT moved (the launch charge forbids moving plan directories this session did not author). Goes to the cold gate or Ed before the next harvest retires or retains a root. 2026-09-18 headless activation f0b608b7 (record 01): the 09-16 harvest archive `~/night-archive/d079-epoch-25g83-derivation-n1-20260916-harvest-20260916/`, found empty by arm record 21, was re-harvested byte-exact from the retained live root (20/20 sums OK against the live root and the copy, `SHA256SUMS` inside the archive, inventories identical); the 09-16 root remains retained under this lane's rule and may now be retired when the lane rules, with a complete archive. The 09-17 plan root was retired 2026-09-18 19:26 (arm record 21, step 0). 2026-09-19 — A third retained, inert night root (the directory holding a completed night's plan and evidence), `d079-epoch-25g83-derivation-n2-20260919`, now remains alongside the 2026-09-16 and `n1-20260919` roots. |
 | A232 | QUIET-PREDICATE-EVIDENCE-01 | P1 Phase Gate | READY [AGENT] | The busy-core cutoff (busy CPU seconds per elapsed second; 1.0 busy-core equivalent means one fully busy core) in NIGHT-GATE-QUIET-ADMISSION-01, the night gate repair that checks whether an unattended run may start, has no evidence behind it yet; the consult (section 2, "Science blocker") and the standing sensible-gates ruling (every tolerance sized to the instrument) both require the number to be derived from what the instrument reads, not from wattage arithmetic. Establish the cutoff's discrimination in the instrument's units: (1) sample the `cpu_interval_v1` predicate (busy-core equivalents, including the observer: the sampler and its children) on this machine across quiet and contaminated states (clean-state samples require an empty census, the scan for active AI-agent processes), recording alongside it the `powermetrics` macOS power sampler's CPU package power and per-cluster active residency (the fraction of time each CPU cluster is active) for the same intervals; (2) read the accepted clean captures (the r6 acceptance `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json` and its evidence bundles) for their idle CPU power and residency, so the accepted idle level is the reference; (3) express the cutoff as the busy-core level whose excess energy over 60 s stays under the ~5 J floor tolerance relative to that reference, and state the observer's own cost; (4) deliver a short evidence memo the cold gate (independent adjudication) can rule on (proposition 4 of packet 70, currently expected REFUSE pending evidence). | an evidence memo with real sampled numbers (state the sampling dates, machine state, and the exact commands), the derived cutoff with its physical rationale, the observer cost, and a recommendation the cold gate can AFFIRM or REJECT atomically; no threshold is written into any plan or code without that ruling; no `[QUIET-MAC]` exclusive window is consumed (sampling is read-only and may run beside other work, but the clean-state samples must come from a census-clean machine and say so). Evidence: docs/process_traces/2026-09-17-interactive-45a0774c/01-gate-redesign-consult.md (section 2, Science blocker; section 4, proposition 4); docs/process_traces/2026-09-17-activation-8789ee70/01-n1-20260917-harvest-record.md (findings 1–2; section 2.1 load and daemon observations); docs/process_traces/2026-09-09-rehearsal-harvest/121-ed-rulings-2026-09-10-recoverability-steerability.md:54–58 (Ed's gate-sensibility directive, 2026-09-10 ~04:20 PDT; citation supplied by the magistrate's resume ruling). Authority: [2026-09-17 interactive session 5c919872 (registration by the magistrate, not a ruling).](docs/process_traces/2026-09-17-interactive-5c919872/03-brief-lanes-registration-seat.md). Acceptance: [QUIET-PREDICATE-EVIDENCE-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-18 interactive 5c919872: the merged sampler's `--observation` mode is the driver's worker entry (needs `--job-id` and `--result-fd`, writes a framed envelope); sampling for this lane goes through the flagless smoke CLI (`python3 -B -m joulewise.quiet_admission --sample-interval-s 30`, whole-round observer cost 1.15 cpu-s per 30 s round on the desktop) or a harness that supplies the pipe; quote no observer floor from the worker mode (cold-gate ruling 71 Q5). 2026-09-18 headless activation f0b608b7 (record 14 of activation d8ca3a36, decisions 1–7): the campaign is two-stage — stage A is this lane (desk harness plus the observer-only and contaminated states now; census-clean idle and synthetic-load states only from a non-agent context, since a `claude -p` magistrate and every interactive session are themselves in the census), stage B is QUIET-PREDICATE-STAGE-B-CONFIRMATION-01 (240). Corrections to this text: the slot is 480 s, not 60 s; the ≈5 J floor tolerance is a clearance bar for the claim, not a contamination budget — the derivation bounds the incremental false effect; the reference is a fresh 25G83 census-clean idle recorded with the same harness in the same session as the load states (the r6 idle numbers, 0.07–0.70 W CPU rail, median ≈ 0.10 W, are the historical consistency check only); observer cost is the whole-round figure (1.15 cpu-s per 30 s round on the desktop; 1.67–1.80 under three seats), bracketed, never subtracted; E-placed and P-placed loads reported separately, worse bound taken. The sampling harness `scripts/sample_quiet_predicate_evidence.py` (collect / load / summarize, 31 offline tests) is on branch `feat/2026-09-18-quiet-predicate-evidence-harness` at `98336969`, bench-verified live (record 20), UNMERGED. 2026-09-19 — Stage A, the sampling-harness implementation, has pull request #360 open from `feat/2026-09-18-quiet-predicate-evidence-harness` after five fix rounds and two cold gates (independent adjudications); records are under `docs/process_traces/2026-09-19-activation-d0b83820/`. After merge, the Stage A evidence campaign measures joules per 480 s slot under synthetic load on a quiet machine with no agent session. 2026-09-19 afternoon — The sampling harness merged in pull request #360, main `0c529f99`. The unattended evidence executor task (`STAGE-A-EVIDENCE-EXECUTOR-01`) now carries the campaign. Part 1 of its implementation branch adds the operating-system build identifier and per-round AC-power (external power-source) and thermal-probe results to every harness row. |
 | A234 | WATCHDOG-EARLY-REFUSAL-RELEASE-01 | P2 Next Slice | READY [AGENT] | The magistrate watchdog, the scheduler that relaunches the headless lead agent (`scripts/magistrate_watchdog.py:771–790` on `a90ab4e8`), uses a census hold (keeping that agent absent from the scan for active AI-agent processes) and holds the headless magistrate out of the machine for the whole armed span through nominal completion even when the night gate, the pre-measurement admission check, has already refused at t0 (the planned start instant) with zero capture; on 2026-09-17 that hold cost about 2.5 h of idle machine after a 15:30 refusal (harvest at 18:09). The consult (section 2, "Retry reconciliation") names this as the second half of the zero-capture successor route: once the driver has written its terminal refusal and the courier (the process that delivers the night's result) has delivered (`courier.sent`), the hold has nothing left to protect. Release the hold on positive terminal evidence, proof that the night has finished refusing (terminal refusal result + delivery handoff complete + no start claim), never on the mere existence of a refusal file, so that the successor activation can harvest and re-plan within minutes (the refusal fast-retry ruling A212 (REFUSAL-FAST-RETRY-01)'s ~20 min target). | a regression where a refusal result plus `courier.sent` releases the hold before nominal completion, a second where a refusal file WITHOUT `courier.sent` keeps the hold, and a third where a started night keeps the hold through completion; the watchdog's existing armed-span, clock and reboot tests unchanged; lands under the twelve-row gate after NIGHT-GATE-QUIET-ADMISSION-01 (it consumes that lane's successor predicate). Evidence: docs/process_traces/2026-09-17-interactive-45a0774c/01-gate-redesign-consult.md (section 2, Retry reconciliation); scripts/magistrate_watchdog.py:771–790 on a90ab4e8 (plan_completion_epoch and plan_span_active; hold through nominal completion before courier.sent check); docs/process_traces/2026-09-17-activation-8789ee70/01-n1-20260917-harvest-record.md (launch 18:09 after the 15:30 refusal). Authority: [2026-09-17 interactive session 5c919872 (registration by the magistrate, not a ruling).](docs/process_traces/2026-09-17-interactive-5c919872/03-brief-lanes-registration-seat.md). Acceptance: [WATCHDOG-EARLY-REFUSAL-RELEASE-01 acceptance](docs/process/state_kernel.json). |
 | A235 | BIND-REQUEST-PAYLOAD-CAP-01 | P3 Hardening Candidates | READY [AGENT] | The bind loop, the night driver's bounded wait for sustained quiet before permitting an unattended measurement, sends requests to worker processes (child processes that perform individual checks) on the command line: `scripts/run_night.py` `_bind_argv` puts the whole static receipt (the recorded results of checks performed once before binding) into the `--request` argument as JSON. This is the one uncapped payload crossing a process boundary in a design whose result frame (a length-delimited reply sent through a pipe) is capped at 256 KiB. A request over the operating-system kernel's argument-length limit fails closed to `night_probe_error` (the refusal code for a failed probe), which is outside D-182's eligible successor set (the refusal outcomes that permit a fresh replacement night after zero capture), so such a night gets no successor. | Pass the worker request through a capped channel, either the same framed pipe (a pipe carrying length-delimited messages) or a bounded file the worker reads. Refuse before launching a worker when the request exceeds the cap, with a distinct detail identifying that cause. Add a regression with a synthetic oversized static receipt; existing supervision tests (tests of worker deadlines, termination and cleanup) remain unchanged and pass. Evidence: docs/process_traces/2026-09-17-interactive-5c919872/29-opus-counter-review-13d53ce2.md:18–37 (finding S1: uncapped request, argument-length failure and no D-182 successor). Authority: [registration by the magistrate (interactive session 5c919872), not a ruling](docs/process_traces/2026-09-17-interactive-5c919872/31-brief-lanes-post-pr358.md). Acceptance: [BIND-REQUEST-PAYLOAD-CAP-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-18 headless activation f0b608b7: record 19 confirmed the production `--request` argv is the only production payload that can hit the kernel argument limit; the test-fixture argv defect is separate (lane 238) and its fix does not touch this seam. |
@@ -878,6 +878,8 @@ Generated compatibility table for repository consumers; the lane tables below ar
 | A260 | WATCHDOG-COURIER-PATH-HOLD-01 | P3 Tooling | READY [AGENT] | The night driver’s own argv carries --courier-bin /Users/edr/.local/share/claude/versions/…, which the census regex matches from an INDEPENDENT producer: the watchdog’s production_census inside the plan span. At 00:43:45 PDT 2026-09-20, driver pid 79018 caused HOLD_CENSUS (production census non-empty inside plan span). This is never fatal to the night, but produces a false hold/notice every night. Use census-safe courier configuration (a path or indirection that does not contain an agent name), not output filtering. | The authorized driver’s courier configuration no longer triggers a false HOLD_CENSUS or notice from the independent watchdog inside the plan span. Use a census-safe path or indirection without an agent name; preserve raw census output and refusal of real foreign agents. Evidence: docs/process_traces/2026-09-20-activation-21752427/10-refuter-census-execution-astra.md (F2: executed production_census and decide probe; independent producer); docs/process_traces/2026-09-20-activation-21752427/01-qpe01-pilot-n1-20260920-harvest-record.md (§1: HOLD_CENSUS on driver pid 79018 at 00:43:45 PDT). Authority: [Record 10 F2: independent watchdog courier-path false hold; record 01 §1: observed hold](docs/process_traces/2026-09-20-activation-21752427/10-refuter-census-execution-astra.md). Acceptance: [WATCHDOG-COURIER-PATH-HOLD-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-20 activation 21752427 — queued [AGENT], p3_tooling. Registered from refuter 10 F2 and record 01 §1; separate from the concurrent-pgrep cure delivered by PR #371 (980f8d64). Census-safe courier configuration is the cure direction; no output filtering. |
 | A261 | TEST-FIXTURE-HOST-PATHS-01 | P3 Tooling | READY [AGENT] | Move remaining host-file paths in plan fixtures under each test’s temporary root: tests/test_magistrate_watchdog_cli.py:198 chain_path="/bin/true" is latent because the module never reaches the installer’s UTF-8 reader (refuter 06 item 4 substituted a binary and three tests still passed); tests/test_install_night_agent.py:110 chain_sha256_path="/tmp/install-night-agent-test.sha256" is inert today per Opus 07 finding 1’s executed trace. | Every plan fixture path lives under the test’s temporary root, including the watchdog CLI chain path and the installer sidecar path; focused fixture tests pass without depending on host-file existence or contents. Evidence: docs/process_traces/2026-09-20-activation-21752427/02-brief-seat-legacy-fixture-linux.md (delivered legacy fixture fix brief); docs/process_traces/2026-09-20-activation-21752427/06-refuter-legacy-fixture-astra.md (item 4: watchdog CLI binary substitution; three tests pass); docs/process_traces/2026-09-20-activation-21752427/07-opus-counter-review-legacy-fixture.md (finding 1: fixed sidecar path currently inert; executed trace); docs/process_traces/2026-09-20-activation-21752427/08-diff-gate-legacy-fixture.md (legacy fixture closure). Authority: [Records 06 item 4 and 07 finding 1: remaining host-path fixture follow-ups](docs/process_traces/2026-09-20-activation-21752427/06-refuter-legacy-fixture-astra.md). Acceptance: [TEST-FIXTURE-HOST-PATHS-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-20 activation 21752427 — queued [AGENT], p3_tooling. CI-LEGACY-FIXTURE-LINUX-01 retired by removal after PR #370 (merge d8e6761f, 2026-09-20 05:00 PDT); post-merge matrix run 35509175943 SUCCESS, including test (3.11, 3). Closure evidence: records 02/06/07/08 in docs/process_traces/2026-09-20-activation-21752427/. These remaining host-path fixtures are follow-ups, latent/inert today as executed in records 06/07. |
 | A262 | RUNBOOK-TRACKED-COMMANDS-01 | P3 Tooling | READY [AGENT] | Replace the per-night script-set procedure in `docs/phase_2/derivation_night_runbook.md` §0–§1.5 with the tracked-command checklist of NIGHT_HANDBACK §Census (prepare/check/notice/veto/publish-install/verify/uninstall), keeping every process rule verbatim; evidence: records 33 §4, 44 §4, 47. | The runbook §0–§1.5 uses the NIGHT_HANDBACK §Census tracked-command checklist (prepare/check/notice/veto/publish-install/verify/uninstall), with every process rule preserved verbatim. Evidence: docs/process_traces/2026-09-20-activation-21752427/33-diff-gate-evidence-night-lifecycle.md (§4); docs/process_traces/2026-09-20-activation-21752427/44-diff-gate-evidence-night-b2.md (§4); docs/process_traces/2026-09-20-activation-21752427/47-fresh-eyes-final-evidence-night-b2-round2.md. Authority: [Record 44 §4: successor runbook doc lane; records 33 §4 and 47](docs/process_traces/2026-09-20-activation-21752427/44-diff-gate-evidence-night-b2.md). Acceptance: [RUNBOOK-TRACKED-COMMANDS-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-20 activation 21752427, touch 6 — registered after slice B2 merged as PR #375 (`790cce67`); successor doc lane from records 33 §4, 44 §4, 47. Keep every process rule verbatim. |
+| A263 | RETAINED-ROOT-SPAN-ARITHMETIC-01 | P3 Hardening Candidates | DONE 2026-09-21 (same PR: `retained_roots` evaluates `plan_span_active` on each discovered root's own plan; span-active → ACTIVE, unparseable or foreign custody_root → UNKNOWN; test `test_discovery_span_fence_reuses_the_watchdog_rule`) — residual noted by the Opus counter-review: an unparseable plan (e.g. after a future plan-schema bump) on a plainly harvested root reads UNKNOWN with no cure but moving the root, which §0.7 forbids; on any schema bump, extend the classifier to parse the older schema before arming [AGENT] | `evidence_night.retained_roots` classifies a discovered root by night records only; the watchdog's `plan_span_active` (scripts/magistrate_watchdog.py:774-790) also keeps a plan active by time (until t0 + window_max_s + COURIER_DEADLINE_S, then until the dead-man + COURIER_LOCK_FRESH_S unless `courier.sent` exists). A root whose chain died inside its span is `retained` to the check and span-active to the watchdog at the same instant (Opus contract refuter, packet 05, Q1 R4). | Either the check reads t0 and window from each discovered root's plan and refuses inside the watchdog's span, or the contract records that the watchdog fences magistrate launches during active spans so the check cannot run inside one; a test pins the chosen rule. Evidence: docs/process_traces/2026-09-21-activation-29ea94df/05-coldgate-packet-a230-retained-root-discovery/11-opus-contract-refuter.md §Q1 R4. | [2026-09-21 activation 29ea94df, packet 05] |
+| A264 | MAGISTRATE-LAUNCH-WITHOUT-MCP-01 | P3 Tooling | READY [AGENT] | The headless magistrate is launched with the project Codex MCP server, so every activation owns two idle `codex mcp-server` processes that the pre-arm census classifies as foreign (descendants of the session root outside the caller's ancestor chain); the ruled cure is a manual termination step before `check` (NIGHT_HANDBACK §Arm procedure via the tracked commands). | The watchdog launches the headless magistrate without the project MCP server (Claude Code's strict MCP-config flags), the post-launch census shows no descendant of the session root, and the handbook step becomes a no-op check. Needs its own gate packet (cold-gate ruling packet 05 Q3, preferred durable form (c)). Evidence: docs/process_traces/2026-09-21-activation-29ea94df/05-coldgate-packet-a230-retained-root-discovery/10-coldgate-fable-ruling.md §Q3. | [2026-09-21 activation 29ea94df, packet 05 Q3] |
 
 ## Active Global Work-Selection Gates
 
@@ -1079,7 +1081,7 @@ NONE — no global work-selection gate is active.
 | A226 | CUSTODY-REAPING-ATTRIBUTION-01 | P3 Hardening Candidates | READY | The custody worker (joulewise/calibration_custody_worker.py) is a short-lived child process the parent spawns to perform custody reads; production is required to reap it, that is, to call wait() on the child after termination so that no zombie (a finished process whose exit status no one has collected) is left behind. The late-child regression in tests/test_calibration_custody_worker.py performs that reap itself, via children[0].wait(), before making its assertions. Because the test collects the exit status, a mutant of production that terminates the worker but never reaps it passes both the pre-delta test (0.286 s) and the post-delta test (0.141 s). The test therefore does not attribute reaping to production code, and no other test does: the delta re-audit recorded this as verification gap R1, with replay script probe_reaping.py under /tmp/reaudit-A/mutation and logs reaping-base.log and reaping-only.log. The behaviour predates the NIGHT-RESERVE-HANG-01 delta; what is missing is proof, not the reaping itself. | A regression fails when production stops reaping the custody worker: the test must not call wait() on the child, and must observe from outside the parent -- for example, a separate process checking that no process in zombie state remains with the parent alive after the parent's custody call returns -- so that a terminate-without-reap mutant is killed. Demonstrate the kill by running the new test against a production copy with the reap removed and quoting the failing assertion. Existing custody-worker tests, including the launch-barrier and group-termination proofs, remain unchanged and still pass. Evidence: docs/process_traces/2026-09-16-activation-9853dd2b/27-seat-A-delta-reaudit-report.md flag R1 (verification_gap, nonblocking): the late-child test reaps via children[0].wait(), a terminate-without-reap mutant passes both the base test at 0.286 s and the revised test at 0.141 s, so production-owned reaping is not independently proved; replay probe_reaping.py in /tmp/reaudit-A/mutation, evidence reaping-base.log and reaping-only.log; tests/test_calibration_custody_worker.py (late-child test; the reap it performs itself is what masks the mutant); joulewise/calibration_custody_worker.py and the parent's spawn and collection path in joulewise/calibration_ledger.py (worker spawned at :2038, results required at :2100-2108). Authority: [2026-09-17 activation 9853dd2b, NIGHT-RESERVE-HANG-01 review findings; registration by the magistrate, not a ruling](docs/process_traces/2026-09-16-activation-9853dd2b/00-launch-record.md). Acceptance: [CUSTODY-REAPING-ATTRIBUTION-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-17 activation 9853dd2b: magistrate registration from the NIGHT-RESERVE-HANG-01 review round, not a ruling; not started; test-strength hardening, not night-critical. The re-audit recorded R1 as predating the delta and nonblocking; the replay materials under /tmp are scratch and may be gone, so the lane rebuilds the mutant rather than depending on them. Lands under the twelve-row gate. |
 | A228 | COLDGATE-CONVENE-DOCTRINE-FREE-01 | P3 Hardening Candidates | READY | The cold-gate charter (docs/process/coldgate_charter.md) says the charter is the ONE process context a cold adjudication instance receives and that the project's operating doctrine is deliberately withheld; the convening pattern in use runs the judge with `claude -p` from a linked JouleWise worktree, so the tracked project CLAUDE.md, the user-level ~/.claude/CLAUDE.md and the memory index MEMORY.md auto-load before the judge reads the packet (rulings 61 and 69 both disclose this honestly). The judge is asked to disclose auto-loads rather than prevented from receiving them, so 'cold' is nominal. Both rulings stood because the paired Opus refuter re-derived every load-bearing probe independently. | The council (not the magistrate) decides the convening shape: a judge tree without the tracked CLAUDE.md (e.g. an export of the checkout with that file removed, digests pinned) and a HOME override carrying no memory index or user doctrine; the convene script records what the judge could load; a regression or checklist item in the convening pattern fails the convening when a doctrine file is present in the judge's tree. Until decided, every convening records the auto-loaded files in the ruling's disclosure (already the practice) and pairs an Opus refuter (already the practice). Process observation for the council; no rule text is amended by this registration. Evidence: docs/process_traces/2026-09-16-activation-9853dd2b/69-coldgate-packet-prereg-chain-digest/12-opus-pairing-refuter-on-ruling-10.md (B1); docs/process_traces/2026-09-16-activation-9853dd2b/69-coldgate-packet-prereg-chain-digest/10-coldgate-fable-ruling.md (section 0 disclosure); docs/process/coldgate_charter.md (the ONE-context clause). Authority: [2026-09-17 activation 9853dd2b, flagged by the Opus pairing refuter of cold gate 69; registration by the magistrate for the council, not a ruling](docs/process_traces/2026-09-16-activation-9853dd2b/00-launch-record.md). Acceptance: [COLDGATE-CONVENE-DOCTRINE-FREE-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-17 activation 9853dd2b: registered for the council; not started; no night depends on it. |
 | A229 | TEST-WALLCLOCK-ABORT-FIXTURE-MARGIN-01 | P3 Hardening Candidates | READY | tests/test_run_night.py WindowDeadlineTests.test_an_abort_that_spends_its_whole_budget_is_not_interrupted (the NIGHT-STALL-WALLCLOCK-ABORT-01 regression) arms a chain that sleeps 3 s against a 2 s window plus a 3.0 s patched grace, so the chain must exit within a 1 s margin of the driver's wall-clock deadline. On the hosted runner at main c613e71e (run 35269617966, job test (3.13, 3)) it failed with AssertionError: 0 != 4 (the driver aborted the chain that was meant to finish inside the grace); locally at the same head it passed 4 of 5 runs, the one failure under load. The production inequality the test also asserts (CUSTODY_BUDGET_S 120 <= WINDOW_SHUTDOWN_GRACE_S 300 - TERMINATION_BOUND_S 70) is unaffected; the flake is the scaled fixture's margin. | The fixture's timing margin is widened (a larger patched grace against the same 3 s chain, or the deadline asserted from the driver's own recorded epochs rather than a live sleep race) so that ten consecutive runs under `python3 scripts/shard_tests.py`-level load pass locally and the hosted matrix is green at the fix head; the production inequality assertion is kept verbatim. Evidence: docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-record-n1-20260917.md (section Hosted CI at H); tests/test_run_night.py (WindowDeadlineTests, fixture _arm grace_s). Authority: [2026-09-17 activation 9853dd2b, arm record 77 (n1-20260917); registration by the magistrate, not a ruling](docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-record-n1-20260917.md). Acceptance: [TEST-WALLCLOCK-ABORT-FIXTURE-MARGIN-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-17 activation 9853dd2b: FIX MERGED as PR #356 (main 3fc54a6a; Opus refuter CONFIRM record 79; full replay record 80, 6352 tests 0 failures). The lane stays open for the refuter's two residual test-strength points only: (1) the widened fixture no longer discriminates partial-grace mutants (a grace/2 driver survives; sibling exact-arithmetic assertions cover it); (2) the test never asserts that the chain actually outlived the window end, so a later window_max_s edit could make it pass vacuously — add an explicit chain-end-vs-window-end assertion. Hosted CI failed the same shard a third time on the docs-only main 3d8e5807 before the fix; the successor confirms hosted CI green on 3fc54a6a or later. |
-| A230 | NIGHT-ROOT-RETENTION-DISCOVERY-01 | P2 Next Slice | READY | docs/phase_2/derivation_night_runbook.md section 0.7 says the arm precondition `print -rl -- /Users/edr/night-custody/*/night_plan.json(N)` must print nothing, while docs/process/NIGHT_HANDBACK.md section Next lane rules that the clone and night root of a night that opened a ledger session are RETAINED (only a refused night's plan root is retired). After the 2026-09-16 night, which opened a session, its root /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916 stays discoverable by that glob, so the two texts contradict each other for every retained root. The watchdog fences only active spans (plan_span_active, plan_is_armed in scripts/magistrate_watchdog.py) and the installer reads no sibling, so a completed retained root arms nothing; the 2026-09-17 arm proceeded on that reading and recorded it (arm record 77). | One rule holds in both documents, chosen by the cold gate or Ed (rule 11): either retained roots move out of discovery to a retained-custody location that is not /Users/edr/night-custody/<plan_id> (with the handback's retention wording and the inventory updated), or section 0.7's precondition is restated as 'no plan whose span is active or whose agents are installed', with the executable check that the watchdog already applies; the runbook and the handback then say the same thing and the arm scripts assert the executable form. Evidence: docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-record-n1-20260917.md (section Step 2, discovery bullet); docs/phase_2/derivation_night_runbook.md (section 0.7); docs/process/NIGHT_HANDBACK.md (section Next lane, retention sentence). Authority: [2026-09-17 activation 9853dd2b, arm record 77 (n1-20260917); registration by the magistrate, not a ruling](docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-record-n1-20260917.md). Acceptance: [NIGHT-ROOT-RETENTION-DISCOVERY-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-17 activation 9853dd2b: docs contradiction found at the arm; magistrate registration, not a ruling; the 09-16 root was NOT moved (the launch charge forbids moving plan directories this session did not author). Goes to the cold gate or Ed before the next harvest retires or retains a root. 2026-09-18 headless activation f0b608b7 (record 01): the 09-16 harvest archive `~/night-archive/d079-epoch-25g83-derivation-n1-20260916-harvest-20260916/`, found empty by arm record 21, was re-harvested byte-exact from the retained live root (20/20 sums OK against the live root and the copy, `SHA256SUMS` inside the archive, inventories identical); the 09-16 root remains retained under this lane's rule and may now be retired when the lane rules, with a complete archive. The 09-17 plan root was retired 2026-09-18 19:26 (arm record 21, step 0). 2026-09-19 — A third retained, inert night root (the directory holding a completed night's plan and evidence), `d079-epoch-25g83-derivation-n2-20260919`, now remains alongside the 2026-09-16 and `n1-20260919` roots. |
+| A230 | NIGHT-ROOT-RETENTION-DISCOVERY-01 | P2 Next Slice | DONE 2026-09-21 (cold-gate ruling packet 05 Q2 AFFIRMED option (ii): runbook §0.7 restated in the executable form, handback retention sentence unchanged; ruling docs/process_traces/2026-09-21-activation-29ea94df/05-coldgate-packet-a230-retained-root-discovery/10-coldgate-fable-ruling.md) | docs/phase_2/derivation_night_runbook.md section 0.7 says the arm precondition `print -rl -- /Users/edr/night-custody/*/night_plan.json(N)` must print nothing, while docs/process/NIGHT_HANDBACK.md section Next lane rules that the clone and night root of a night that opened a ledger session are RETAINED (only a refused night's plan root is retired). After the 2026-09-16 night, which opened a session, its root /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916 stays discoverable by that glob, so the two texts contradict each other for every retained root. The watchdog fences only active spans (plan_span_active, plan_is_armed in scripts/magistrate_watchdog.py) and the installer reads no sibling, so a completed retained root arms nothing; the 2026-09-17 arm proceeded on that reading and recorded it (arm record 77). | One rule holds in both documents, chosen by the cold gate or Ed (rule 11): either retained roots move out of discovery to a retained-custody location that is not /Users/edr/night-custody/<plan_id> (with the handback's retention wording and the inventory updated), or section 0.7's precondition is restated as 'no plan whose span is active or whose agents are installed', with the executable check that the watchdog already applies; the runbook and the handback then say the same thing and the arm scripts assert the executable form. Evidence: docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-record-n1-20260917.md (section Step 2, discovery bullet); docs/phase_2/derivation_night_runbook.md (section 0.7); docs/process/NIGHT_HANDBACK.md (section Next lane, retention sentence). Authority: [2026-09-17 activation 9853dd2b, arm record 77 (n1-20260917); registration by the magistrate, not a ruling](docs/process_traces/2026-09-16-activation-9853dd2b/77-arm-record-n1-20260917.md). Acceptance: [NIGHT-ROOT-RETENTION-DISCOVERY-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-17 activation 9853dd2b: docs contradiction found at the arm; magistrate registration, not a ruling; the 09-16 root was NOT moved (the launch charge forbids moving plan directories this session did not author). Goes to the cold gate or Ed before the next harvest retires or retains a root. 2026-09-18 headless activation f0b608b7 (record 01): the 09-16 harvest archive `~/night-archive/d079-epoch-25g83-derivation-n1-20260916-harvest-20260916/`, found empty by arm record 21, was re-harvested byte-exact from the retained live root (20/20 sums OK against the live root and the copy, `SHA256SUMS` inside the archive, inventories identical); the 09-16 root remains retained under this lane's rule and may now be retired when the lane rules, with a complete archive. The 09-17 plan root was retired 2026-09-18 19:26 (arm record 21, step 0). 2026-09-19 — A third retained, inert night root (the directory holding a completed night's plan and evidence), `d079-epoch-25g83-derivation-n2-20260919`, now remains alongside the 2026-09-16 and `n1-20260919` roots. |
 | A232 | QUIET-PREDICATE-EVIDENCE-01 | P1 Phase Gate | READY | The busy-core cutoff (busy CPU seconds per elapsed second; 1.0 busy-core equivalent means one fully busy core) in NIGHT-GATE-QUIET-ADMISSION-01, the night gate repair that checks whether an unattended run may start, has no evidence behind it yet; the consult (section 2, "Science blocker") and the standing sensible-gates ruling (every tolerance sized to the instrument) both require the number to be derived from what the instrument reads, not from wattage arithmetic. Establish the cutoff's discrimination in the instrument's units: (1) sample the `cpu_interval_v1` predicate (busy-core equivalents, including the observer: the sampler and its children) on this machine across quiet and contaminated states (clean-state samples require an empty census, the scan for active AI-agent processes), recording alongside it the `powermetrics` macOS power sampler's CPU package power and per-cluster active residency (the fraction of time each CPU cluster is active) for the same intervals; (2) read the accepted clean captures (the r6 acceptance `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json` and its evidence bundles) for their idle CPU power and residency, so the accepted idle level is the reference; (3) express the cutoff as the busy-core level whose excess energy over 60 s stays under the ~5 J floor tolerance relative to that reference, and state the observer's own cost; (4) deliver a short evidence memo the cold gate (independent adjudication) can rule on (proposition 4 of packet 70, currently expected REFUSE pending evidence). | an evidence memo with real sampled numbers (state the sampling dates, machine state, and the exact commands), the derived cutoff with its physical rationale, the observer cost, and a recommendation the cold gate can AFFIRM or REJECT atomically; no threshold is written into any plan or code without that ruling; no `[QUIET-MAC]` exclusive window is consumed (sampling is read-only and may run beside other work, but the clean-state samples must come from a census-clean machine and say so). Evidence: docs/process_traces/2026-09-17-interactive-45a0774c/01-gate-redesign-consult.md (section 2, Science blocker; section 4, proposition 4); docs/process_traces/2026-09-17-activation-8789ee70/01-n1-20260917-harvest-record.md (findings 1–2; section 2.1 load and daemon observations); docs/process_traces/2026-09-09-rehearsal-harvest/121-ed-rulings-2026-09-10-recoverability-steerability.md:54–58 (Ed's gate-sensibility directive, 2026-09-10 ~04:20 PDT; citation supplied by the magistrate's resume ruling). Authority: [2026-09-17 interactive session 5c919872 (registration by the magistrate, not a ruling).](docs/process_traces/2026-09-17-interactive-5c919872/03-brief-lanes-registration-seat.md). Acceptance: [QUIET-PREDICATE-EVIDENCE-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-18 interactive 5c919872: the merged sampler's `--observation` mode is the driver's worker entry (needs `--job-id` and `--result-fd`, writes a framed envelope); sampling for this lane goes through the flagless smoke CLI (`python3 -B -m joulewise.quiet_admission --sample-interval-s 30`, whole-round observer cost 1.15 cpu-s per 30 s round on the desktop) or a harness that supplies the pipe; quote no observer floor from the worker mode (cold-gate ruling 71 Q5). 2026-09-18 headless activation f0b608b7 (record 14 of activation d8ca3a36, decisions 1–7): the campaign is two-stage — stage A is this lane (desk harness plus the observer-only and contaminated states now; census-clean idle and synthetic-load states only from a non-agent context, since a `claude -p` magistrate and every interactive session are themselves in the census), stage B is QUIET-PREDICATE-STAGE-B-CONFIRMATION-01 (240). Corrections to this text: the slot is 480 s, not 60 s; the ≈5 J floor tolerance is a clearance bar for the claim, not a contamination budget — the derivation bounds the incremental false effect; the reference is a fresh 25G83 census-clean idle recorded with the same harness in the same session as the load states (the r6 idle numbers, 0.07–0.70 W CPU rail, median ≈ 0.10 W, are the historical consistency check only); observer cost is the whole-round figure (1.15 cpu-s per 30 s round on the desktop; 1.67–1.80 under three seats), bracketed, never subtracted; E-placed and P-placed loads reported separately, worse bound taken. The sampling harness `scripts/sample_quiet_predicate_evidence.py` (collect / load / summarize, 31 offline tests) is on branch `feat/2026-09-18-quiet-predicate-evidence-harness` at `98336969`, bench-verified live (record 20), UNMERGED. 2026-09-19 — Stage A, the sampling-harness implementation, has pull request #360 open from `feat/2026-09-18-quiet-predicate-evidence-harness` after five fix rounds and two cold gates (independent adjudications); records are under `docs/process_traces/2026-09-19-activation-d0b83820/`. After merge, the Stage A evidence campaign measures joules per 480 s slot under synthetic load on a quiet machine with no agent session. 2026-09-19 afternoon — The sampling harness merged in pull request #360, main `0c529f99`. The unattended evidence executor task (`STAGE-A-EVIDENCE-EXECUTOR-01`) now carries the campaign. Part 1 of its implementation branch adds the operating-system build identifier and per-round AC-power (external power-source) and thermal-probe results to every harness row. |
 | A234 | WATCHDOG-EARLY-REFUSAL-RELEASE-01 | P2 Next Slice | READY | The magistrate watchdog, the scheduler that relaunches the headless lead agent (`scripts/magistrate_watchdog.py:771–790` on `a90ab4e8`), uses a census hold (keeping that agent absent from the scan for active AI-agent processes) and holds the headless magistrate out of the machine for the whole armed span through nominal completion even when the night gate, the pre-measurement admission check, has already refused at t0 (the planned start instant) with zero capture; on 2026-09-17 that hold cost about 2.5 h of idle machine after a 15:30 refusal (harvest at 18:09). The consult (section 2, "Retry reconciliation") names this as the second half of the zero-capture successor route: once the driver has written its terminal refusal and the courier (the process that delivers the night's result) has delivered (`courier.sent`), the hold has nothing left to protect. Release the hold on positive terminal evidence, proof that the night has finished refusing (terminal refusal result + delivery handoff complete + no start claim), never on the mere existence of a refusal file, so that the successor activation can harvest and re-plan within minutes (the refusal fast-retry ruling A212 (REFUSAL-FAST-RETRY-01)'s ~20 min target). | a regression where a refusal result plus `courier.sent` releases the hold before nominal completion, a second where a refusal file WITHOUT `courier.sent` keeps the hold, and a third where a started night keeps the hold through completion; the watchdog's existing armed-span, clock and reboot tests unchanged; lands under the twelve-row gate after NIGHT-GATE-QUIET-ADMISSION-01 (it consumes that lane's successor predicate). Evidence: docs/process_traces/2026-09-17-interactive-45a0774c/01-gate-redesign-consult.md (section 2, Retry reconciliation); scripts/magistrate_watchdog.py:771–790 on a90ab4e8 (plan_completion_epoch and plan_span_active; hold through nominal completion before courier.sent check); docs/process_traces/2026-09-17-activation-8789ee70/01-n1-20260917-harvest-record.md (launch 18:09 after the 15:30 refusal). Authority: [2026-09-17 interactive session 5c919872 (registration by the magistrate, not a ruling).](docs/process_traces/2026-09-17-interactive-5c919872/03-brief-lanes-registration-seat.md). Acceptance: [WATCHDOG-EARLY-REFUSAL-RELEASE-01 acceptance](docs/process/state_kernel.json). |
 | A235 | BIND-REQUEST-PAYLOAD-CAP-01 | P3 Hardening Candidates | READY | The bind loop, the night driver's bounded wait for sustained quiet before permitting an unattended measurement, sends requests to worker processes (child processes that perform individual checks) on the command line: `scripts/run_night.py` `_bind_argv` puts the whole static receipt (the recorded results of checks performed once before binding) into the `--request` argument as JSON. This is the one uncapped payload crossing a process boundary in a design whose result frame (a length-delimited reply sent through a pipe) is capped at 256 KiB. A request over the operating-system kernel's argument-length limit fails closed to `night_probe_error` (the refusal code for a failed probe), which is outside D-182's eligible successor set (the refusal outcomes that permit a fresh replacement night after zero capture), so such a night gets no successor. | Pass the worker request through a capped channel, either the same framed pipe (a pipe carrying length-delimited messages) or a bounded file the worker reads. Refuse before launching a worker when the request exceeds the cap, with a distinct detail identifying that cause. Add a regression with a synthetic oversized static receipt; existing supervision tests (tests of worker deadlines, termination and cleanup) remain unchanged and pass. Evidence: docs/process_traces/2026-09-17-interactive-5c919872/29-opus-counter-review-13d53ce2.md:18–37 (finding S1: uncapped request, argument-length failure and no D-182 successor). Authority: [registration by the magistrate (interactive session 5c919872), not a ruling](docs/process_traces/2026-09-17-interactive-5c919872/31-brief-lanes-post-pr358.md). Acceptance: [BIND-REQUEST-PAYLOAD-CAP-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-18 headless activation f0b608b7: record 19 confirmed the production `--request` argv is the only production payload that can hit the kernel argument limit; the test-fixture argv defect is separate (lane 238) and its fix does not touch this seam. |
@@ -1102,6 +1104,8 @@ NONE — no global work-selection gate is active.
 | A260 | WATCHDOG-COURIER-PATH-HOLD-01 | P3 Tooling | READY | The night driver’s own argv carries --courier-bin /Users/edr/.local/share/claude/versions/…, which the census regex matches from an INDEPENDENT producer: the watchdog’s production_census inside the plan span. At 00:43:45 PDT 2026-09-20, driver pid 79018 caused HOLD_CENSUS (production census non-empty inside plan span). This is never fatal to the night, but produces a false hold/notice every night. Use census-safe courier configuration (a path or indirection that does not contain an agent name), not output filtering. | The authorized driver’s courier configuration no longer triggers a false HOLD_CENSUS or notice from the independent watchdog inside the plan span. Use a census-safe path or indirection without an agent name; preserve raw census output and refusal of real foreign agents. Evidence: docs/process_traces/2026-09-20-activation-21752427/10-refuter-census-execution-astra.md (F2: executed production_census and decide probe; independent producer); docs/process_traces/2026-09-20-activation-21752427/01-qpe01-pilot-n1-20260920-harvest-record.md (§1: HOLD_CENSUS on driver pid 79018 at 00:43:45 PDT). Authority: [Record 10 F2: independent watchdog courier-path false hold; record 01 §1: observed hold](docs/process_traces/2026-09-20-activation-21752427/10-refuter-census-execution-astra.md). Acceptance: [WATCHDOG-COURIER-PATH-HOLD-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-20 activation 21752427 — queued [AGENT], p3_tooling. Registered from refuter 10 F2 and record 01 §1; separate from the concurrent-pgrep cure delivered by PR #371 (980f8d64). Census-safe courier configuration is the cure direction; no output filtering. |
 | A261 | TEST-FIXTURE-HOST-PATHS-01 | P3 Tooling | READY | Move remaining host-file paths in plan fixtures under each test’s temporary root: tests/test_magistrate_watchdog_cli.py:198 chain_path="/bin/true" is latent because the module never reaches the installer’s UTF-8 reader (refuter 06 item 4 substituted a binary and three tests still passed); tests/test_install_night_agent.py:110 chain_sha256_path="/tmp/install-night-agent-test.sha256" is inert today per Opus 07 finding 1’s executed trace. | Every plan fixture path lives under the test’s temporary root, including the watchdog CLI chain path and the installer sidecar path; focused fixture tests pass without depending on host-file existence or contents. Evidence: docs/process_traces/2026-09-20-activation-21752427/02-brief-seat-legacy-fixture-linux.md (delivered legacy fixture fix brief); docs/process_traces/2026-09-20-activation-21752427/06-refuter-legacy-fixture-astra.md (item 4: watchdog CLI binary substitution; three tests pass); docs/process_traces/2026-09-20-activation-21752427/07-opus-counter-review-legacy-fixture.md (finding 1: fixed sidecar path currently inert; executed trace); docs/process_traces/2026-09-20-activation-21752427/08-diff-gate-legacy-fixture.md (legacy fixture closure). Authority: [Records 06 item 4 and 07 finding 1: remaining host-path fixture follow-ups](docs/process_traces/2026-09-20-activation-21752427/06-refuter-legacy-fixture-astra.md). Acceptance: [TEST-FIXTURE-HOST-PATHS-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-20 activation 21752427 — queued [AGENT], p3_tooling. CI-LEGACY-FIXTURE-LINUX-01 retired by removal after PR #370 (merge d8e6761f, 2026-09-20 05:00 PDT); post-merge matrix run 35509175943 SUCCESS, including test (3.11, 3). Closure evidence: records 02/06/07/08 in docs/process_traces/2026-09-20-activation-21752427/. These remaining host-path fixtures are follow-ups, latent/inert today as executed in records 06/07. |
 | A262 | RUNBOOK-TRACKED-COMMANDS-01 | P3 Tooling | READY | Replace the per-night script-set procedure in `docs/phase_2/derivation_night_runbook.md` §0–§1.5 with the tracked-command checklist of NIGHT_HANDBACK §Census (prepare/check/notice/veto/publish-install/verify/uninstall), keeping every process rule verbatim; evidence: records 33 §4, 44 §4, 47. | The runbook §0–§1.5 uses the NIGHT_HANDBACK §Census tracked-command checklist (prepare/check/notice/veto/publish-install/verify/uninstall), with every process rule preserved verbatim. Evidence: docs/process_traces/2026-09-20-activation-21752427/33-diff-gate-evidence-night-lifecycle.md (§4); docs/process_traces/2026-09-20-activation-21752427/44-diff-gate-evidence-night-b2.md (§4); docs/process_traces/2026-09-20-activation-21752427/47-fresh-eyes-final-evidence-night-b2-round2.md. Authority: [Record 44 §4: successor runbook doc lane; records 33 §4 and 47](docs/process_traces/2026-09-20-activation-21752427/44-diff-gate-evidence-night-b2.md). Acceptance: [RUNBOOK-TRACKED-COMMANDS-01 acceptance](docs/process/state_kernel.json). Note: 2026-09-20 activation 21752427, touch 6 — registered after slice B2 merged as PR #375 (`790cce67`); successor doc lane from records 33 §4, 44 §4, 47. Keep every process rule verbatim. |
+| A263 | RETAINED-ROOT-SPAN-ARITHMETIC-01 | P3 Hardening Candidates | DONE 2026-09-21 (same PR: `retained_roots` evaluates `plan_span_active` on each discovered root's own plan; span-active → ACTIVE, unparseable or foreign custody_root → UNKNOWN; test `test_discovery_span_fence_reuses_the_watchdog_rule`) — residual noted by the Opus counter-review: an unparseable plan (e.g. after a future plan-schema bump) on a plainly harvested root reads UNKNOWN with no cure but moving the root, which §0.7 forbids; on any schema bump, extend the classifier to parse the older schema before arming | `evidence_night.retained_roots` classifies a discovered root by night records only; the watchdog's `plan_span_active` (scripts/magistrate_watchdog.py:774-790) also keeps a plan active by time (until t0 + window_max_s + COURIER_DEADLINE_S, then until the dead-man + COURIER_LOCK_FRESH_S unless `courier.sent` exists). A root whose chain died inside its span is `retained` to the check and span-active to the watchdog at the same instant (Opus contract refuter, packet 05, Q1 R4). | Either the check reads t0 and window from each discovered root's plan and refuses inside the watchdog's span, or the contract records that the watchdog fences magistrate launches during active spans so the check cannot run inside one; a test pins the chosen rule. Evidence: docs/process_traces/2026-09-21-activation-29ea94df/05-coldgate-packet-a230-retained-root-discovery/11-opus-contract-refuter.md §Q1 R4. | [2026-09-21 activation 29ea94df, packet 05] |
+| A264 | MAGISTRATE-LAUNCH-WITHOUT-MCP-01 | P3 Tooling | READY | The headless magistrate is launched with the project Codex MCP server, so every activation owns two idle `codex mcp-server` processes that the pre-arm census classifies as foreign (descendants of the session root outside the caller's ancestor chain); the ruled cure is a manual termination step before `check` (NIGHT_HANDBACK §Arm procedure via the tracked commands). | The watchdog launches the headless magistrate without the project MCP server (Claude Code's strict MCP-config flags), the post-launch census shows no descendant of the session root, and the handbook step becomes a no-op check. Needs its own gate packet (cold-gate ruling packet 05 Q3, preferred durable form (c)). Evidence: docs/process_traces/2026-09-21-activation-29ea94df/05-coldgate-packet-a230-retained-root-discovery/10-coldgate-fable-ruling.md §Q3. | [2026-09-21 activation 29ea94df, packet 05 Q3] |
 
 ### Shelved task records
 
diff --git a/docs/contracts/evidence_night_entry.md b/docs/contracts/evidence_night_entry.md
index a5ae1b16..8116f30a 100644
--- a/docs/contracts/evidence_night_entry.md
+++ b/docs/contracts/evidence_night_entry.md
@@ -172,7 +172,7 @@ refusal prints one `REFUSED:` line and exits 2; an unexpected defect prints
 captured return codes and output in the attempt journal. A nonblocking flock
 on `<staging_under>/.locks/<candidate-name>.lock` serializes both preparation
 and lifecycle operations for a candidate (one lock domain).
-No command fast-forwards or repairs a checkout.
+No command repairs a checkout. The one move any command makes is `check`'s fast-forward-only pull of the canonical checkout (item 1 below).
 
 `check` first verifies all sealed digests, render inventory, detached clean H,
 locked environment, interpreter identity and the clone's wrapper/manifest/
@@ -189,6 +189,23 @@ with the clone's code. It then writes verdicts and evidence for:
    The canonical checkout contains **candidate H** and has empty
    `git --no-optional-locks status --porcelain -uno`. Untracked canonical
    files do not fail that check; tracked modifications and observation errors do.
+   **Self fast-forward (D-183, Ed 2026-09-21):** when the canonical checkout is
+   clean but does not contain H, and item 0 passed (no night label loaded, no
+   plist or sidecar present, label discovery known), `check` runs
+   `git -C <canonical> pull --ff-only` itself, bounded to 120 s with
+   `GIT_TERMINAL_PROMPT=0` so an unreachable remote or a credential prompt
+   refuses instead of hanging, and records
+   `fast_forward: {before, after, pull, clean_before}` in the evidence. A dirty
+   tree, a missing or divergent upstream, a timeout, or a pull that still lacks
+   H refuses with `canonical fast-forward failed: …`; the still-lacks-H cause
+   names the before and after shas because the tree did move. With item 0
+   failed the pull is not licensed and the check refuses without moving
+   anything. A checkout that already contains H records `fast_forward: null`.
+   The pull may make the resident supervisor stale under item 2; that refusal
+   names the hand-off (`… commit, push and exit so the watchdog's successor
+   arms`) and `check` re-raises that stale case as its own cause (other supervisor
+   causes stay under the generic `pre-arm checks failed` line) — the session exits and the
+   watchdog's successor arms — never an owner action.
 2. `/Users/edr/night-custody/magistrate/state.json` supplies
    `resident_session.supervisor_pid`. Null, an absent PID, or a reused PID
    whose command no longer names `magistrate_watchdog.py` is clear.
@@ -202,10 +219,23 @@ with the clone's code. It then writes verdicts and evidence for:
    unchanged installer. This checks availability; it never invokes the courier.
 4. Every `<roots_under>/night-custody/*/night_plan.json` is inventoried and
    must be a regular non-symlink file; directories and special files refuse.
-   An existing regular `night/courier.sent` or `night/result.json` classifies
-   its root as retained. Otherwise it is UNKNOWN and refuses. Discovery
-   never removes a root, and has no fixed root count. Retention classification
-   does not certify process liveness or completed delivery.
+   A root whose `night/chain.started` is a regular file without a regular
+   `night/chain.exited` is ACTIVE and refuses. Otherwise an existing regular
+   `night/courier.sent`, `night/result.json`, `night/chain.exited`, or any
+   regular file matched by `run_night._refusal_paths` (`refusal.json`,
+   `refusal-01.json` and later numbers, `calibration-refusal.json`,
+   `calibration-refusal.json.*.json`) classifies its root as retained; the
+   record lists every marker found. Otherwise it is UNKNOWN and refuses.
+   A retained root whose plan span is still active by the watchdog's rule
+   (`scripts/magistrate_watchdog.plan_span_active`, evaluated on that root's
+   own `night_plan.json` at observation time with the entry checkout's timing
+   constants, which may differ from the head that authored an older sibling
+   plan) is ACTIVE and refuses; a root whose plan does not parse, or whose
+   `custody_root` is not its own directory, is UNKNOWN and refuses. Each row
+   records its reason. Discovery never removes a root, and has no fixed root
+   count. Classifying a root `retained` certifies only that a terminal record
+   exists and that the plan's span is over; it does not certify that the
+   courier's delivery succeeded.
 5. The exact raw bracketed `night_gate.AGENT_CENSUS_ARGV` result is retained
    alongside `arm_census.observe_arm_census` and `classify_arm_census` evidence.
    The argv derivation and ancestry classification execute inside the clone's
diff --git a/docs/decision_log.md b/docs/decision_log.md
index 506a0b62..f98a40a1 100644
--- a/docs/decision_log.md
+++ b/docs/decision_log.md
@@ -226,6 +226,7 @@ be re-derived by a future agent gets an entry here.
 | D-180 | ARM RECOVERABILITY AND STEERABILITY — install spans recur within a day; pre-authorized retry class for non-physics arm aborts (idle interactive session, stale notice hash, uncertain tick, transport) without a cold gate; idle interactive sessions not foreign at the arm-time census of stub nights (plan span unchanged); remote control between windows; lanes INSTALL-WINDOWS-MULTI-01 / ARM-RETRY-CLASS-01 / ARM-CENSUS-IDLE-INTERACTIVE-01 / REMOTE-CONTROL-BETWEEN-WINDOWS-01 | ratified by Ed (2026-09-10; decided ≠ done, each clause lands under gates) |
 | D-181 | WINDOWS RUN WHENEVER THE MACHINE IS QUIET — no cadence rule (clean census, day or night, several windows per day when the gates pass; every soundness fence unchanged); Fable 5.1 is the final eyes on every merge (gate rows 7/12 unchanged, final head sha in row 12); the owner's hands step for the first pack night prepared and emailed; lanes INSTALL-WINDOWS-MULTI-01 → ARM-RETRY-CLASS-01 → ARM-CENSUS-IDLE-INTERACTIVE-01 promoted to the head of the agent lane behind the 09-15 harvest event | ratified by Ed (2026-09-14, directive issue #337; recorded verbatim, nothing installed by the entry) |
 | D-182 | ZERO-CAPTURE MACHINE-STATE REFUSAL LICENSES ONE NEW-PLAN SUCCESSOR — a night that refuses on machine state (census, load or CPU quietness, bind-window expiry, screensaver configuration, boot clock) with zero capture licenses ONE new-plan successor once the courier has delivered: new plan id, fresh notice, ≥ 60 s spacing, bounded by the new plan's install close; never a re-arm of the same plan; every observed NO still stops; physics/evidence refusals and every gate at the successor's own t0 unchanged | ratified by Ed (2026-09-16 00:35 PDT for t0 refusals, lane record 06 amendment of activation 08ca8197; re-affirmed and extended to bind-window expiry 2026-09-17, interactive session 5c919872, "affirm of course"; recorded verbatim, nothing installed by the entry) |
+| D-183 | NO ARTIFICIAL OWNER STOPS — the process exists to prevent bad science, not to idle; any precondition an agent can satisfy itself with its own authority (git, gh, launchctl at the documented interfaces) is satisfied by the agent, never queued as an owner action. First instance: the canonical checkout `/Users/edr/code/JouleWise` behind a merged cure stalled the loop 40 h (05:10 09-20 → 21:40 09-21) because the relaunch prompt fenced every git operation there; now a clean canonical tree behind H is fast-forwarded by the evidence-night `check` itself (`git pull --ff-only`, evidence `fast_forward`) whenever no night agent is loaded, the relaunch prompt licenses that one move and requires the session to exit for a fresh supervisor instead of holding, and owner actions remain ONLY hardware, sudo, and the notice NO. Soundness fences unchanged: no move while anything is armed or loaded, no reset/force, dirty trees refuse | ratified by Ed (2026-09-21 21:50 PDT, interactive session: "make sure no more idiotic stops artificially, you have gh auth for a reason"; "the process is meant to prevent bad science not work for 40h") |
 
 ---
 
@@ -12014,3 +12015,59 @@ stay fail-closed (D-161); the successor passes every gate anew at its own t0,
 including the census (D-181); the refusal that ends a span ends it (no waiting
 inside a refused span beyond the bind window the plan itself seals); no
 frequency bound is added (every bound must be scientific, D-181).
+
+## D-183: No artificial owner stops — an agent satisfies any precondition it can satisfy itself (Ed, 2026-09-21)
+
+**Status:** ratified by Ed, 2026-09-21 ~21:50 PDT, in the interactive session
+a87c3444 (verbatim: "make sure no more idiotic stops artificially, you have gh
+auth for a reason"; "obviously idiotic and should not have a 40h stall, def fix
+stuff like that, the process is meant to prevent bad science not work for 40h").
+Recorded by the session that received the ruling; the first implementation lands
+in the same PR (record
+`docs/process_traces/2026-09-21-interactive-a87c3444/01-d183-canonical-self-fast-forward.md`).
+
+**The rule.** Any precondition that an agent can satisfy with authority it
+already holds is satisfied by the agent and recorded, never queued as an action
+for Ed. The authority an agent already holds is: git operations that cannot lose
+work (a fast-forward-only pull of a clean tree), GitHub operations under the
+existing merge gate (D-072), and launchctl at the documented night-agent
+interfaces. Owner actions are only hardware and sudo (the standing rule since
+2026-08-14) and the notice NO.
+
+**Terms, so the rule can be applied without this session's context.** The
+*canonical checkout* is the repository at `/Users/edr/code/JouleWise`, the one
+the watchdog LaunchAgent imports the census code from on every 300-second run.
+A *fast-forward-only pull* (`git pull --ff-only`) moves a branch forward to its
+upstream only when the upstream already contains every local commit; it can
+never discard a commit and fails instead of merging. A *clean tree* has no
+tracked file modified (`git status --porcelain -uno` prints nothing); untracked
+files do not count. *Loaded* means a `com.joulewise.night*` label is present in
+launchd or its plist is on disk, which is the state between arming a night and
+uninstalling it after the night. *Armed* is the plan-level view of the same
+span: a published plan whose agents are installed.
+
+**Why now.** The census self-match cure merged at 05:10 PDT 09-20 (PR #371), but
+the relaunch prompt read "Perform no git operation in the canonical root", so the
+headless magistrate emailed Ed once and held. The canonical checkout stayed 157
+commits behind until Ed ran the pull at 21:40 PDT 09-21: about 40 hours with
+nothing armed, every PR green, and a clean fast-forward as the only missing step.
+The hold bought no soundness. The one email was one of nine sent that night, and
+the session's Gmail authorisation later expired, so no reminder went out.
+
+**What this changes.** (1) The evidence-night `check` command fast-forwards the
+canonical checkout itself when the tree is clean, nothing is loaded (its item 0
+passed) and the checkout does not yet contain candidate H; it records
+`fast_forward: {before, after, pull}` in its evidence, or `null` when no move was
+needed. A dirty tree, a missing or divergent upstream, or a pull that still
+lacks H refuses. (2) The relaunch prompt licenses exactly that move and requires
+the session to commit, push and exit when the move makes its own resident
+supervisor stale, so the watchdog's successor arms; it no longer holds for an
+owner. (3) Every future "waiting for Ed" line must name the soundness the wait
+buys; a wait that buys none is a defect and is logged as one.
+
+**What this does not change.** No git operation in the canonical root other than
+the fast-forward, and none at all while anything is armed or loaded; no reset,
+force or checkout; the supervisor-freshness rule (activation records 19/21)
+still refuses a supervisor that started before the checkout came to contain H;
+physics, evidence and pre-registration refusals stay fail-closed (D-161); the
+notice NO still stops everything.
diff --git a/docs/phase_2/derivation_night_runbook.md b/docs/phase_2/derivation_night_runbook.md
index 449b6e35..618abc62 100644
--- a/docs/phase_2/derivation_night_runbook.md
+++ b/docs/phase_2/derivation_night_runbook.md
@@ -696,10 +696,11 @@ interactive session is the `arm_idle_interactive` retry cause under §1.4a once
 closes; A172 never equates interactive with idle for those classes, and missing evidence
 follows the existing refusal path. A173 alone owns classification and exemption changes.
 
-### 0.7 Nothing else is armed or discoverable
+### 0.7 Nothing else is armed, and every discoverable root is retained
 
 No stand-down, no Ed NO, no unresolved owner-authored `directive` issue, no
-discoverable prior plan root, no active or indeterminate measurement ownership.
+discoverable prior plan root that is ACTIVE or UNKNOWN (a harvested, retained
+root may remain discoverable), no active or indeterminate measurement ownership.
 Remove every `REHEARSAL_STUB` plan root before arming any real plan
 (`docs/process/MAGISTRATE_WATCHDOG.md`, §"Install handoff").
 
@@ -721,12 +722,37 @@ The night's own driver never discovers anything — launchd hands
 `--plan` argument (its `--plan` is `required=True`), so the driver reads the
 file it was installed with and no other.
 
-Check it, and expect no output:
+Check it. Prior roots may be discoverable; what stops an arm is any root whose
+chain is open, whose span is active, whose night agents are installed, or whose
+records show no terminal state. The executable form is
+`python -m joulewise.evidence_night check --candidate STAGING`, whose
+`night_agents` and `retained_roots` items must both pass with every inventoried
+root classified `retained` (contract item 4: `ACTIVE` and `UNKNOWN` refuse).
+For a manual read:
 
 ```zsh
-print -rl -- /Users/edr/night-custody/*/night_plan.json(N)
+for p in /Users/edr/night-custody/*/night_plan.json(N); do
+  n=${p:h}/night; r=${p:h:t}
+  if [[ ! -f $p || -L $p ]]; then print -r -- "$r: REFUSED plan is not a regular file"; continue; fi
+  if [[ -f $n/chain.started && ! -f $n/chain.exited ]]; then print -r -- "$r: ACTIVE"; continue; fi
+  m=($n/courier.sent(N.) $n/result.json(N.) $n/chain.exited(N.) $n/refusal.json(N.) $n/refusal-<0-9>*.json(N.) $n/calibration-refusal.json(N.) $n/calibration-refusal.json.*.json(N.))
+  (( $#m )) && print -r -- "$r: retained ${m[1]:t}" || print -r -- "$r: UNKNOWN"
+done
 ```
 
+Every line must read `retained`; an `ACTIVE` or `UNKNOWN` line, or any
+installed night plist, stops the arm. Do not move or edit a root to change its
+line. This loop reads records only and cannot see the span rule; `check` binds.
+
+Source: cold-gate ruling 2026-09-21 (packet 05 Q2, lane A230). The `(N.)`
+qualifier restricts each glob to regular files, matching contract item 4's
+regular-file rule; it is the one correction to the ruled loop (record 02 of
+activation 29ea94df). The span half of the check above is `retained_roots`'s
+reuse of `scripts/magistrate_watchdog.plan_span_active`; the manual loop reads
+records only, so a root inside its span shows `retained` here and ACTIVE to the
+tracked check, which is the one that binds. `refusal-N.json` names are two-digit
+(`refusal-01.json` and later).
+
 ### 0.8 The clone's tree is clean, and the two desk inputs are written
 
 **Clean tree** means: the measurement clone has no uncommitted change of any
diff --git a/docs/process/MAGISTRATE_RELAUNCH_PROMPT.md b/docs/process/MAGISTRATE_RELAUNCH_PROMPT.md
index 41ca7613..ba819cc4 100644
--- a/docs/process/MAGISTRATE_RELAUNCH_PROMPT.md
+++ b/docs/process/MAGISTRATE_RELAUNCH_PROMPT.md
@@ -7,7 +7,7 @@ After Gmail accepts that launch email, write `@@CUSTODY_ROOT@@/notice.ack` as JS
 Work in linked worktrees; preserve and inspect dirty work, and keep completed work committed and pushed under the normal gates.
 You may spawn Codex children under the bridge contract, but remain the top-level lead and stop every child before stand-down.
 Frozen checkout triples `(plan_id, root, head)` for this activation: @@FENCED_CHECKOUTS@@.
-Perform no git operation in the canonical root above; while any plan is armed, never fast-forward, pull, checkout, or otherwise move any listed measurement root—any post-arm move requires a re-arm with a re-pinned plan.
+While NO plan is armed and no night agent is loaded, you MUST keep the canonical root current yourself: a clean tree behind `origin/main` is moved by the evidence-night `check` command's own fast-forward (D-183), or by hand with `git -C /Users/edr/code/JouleWise pull --ff-only` only after you have confirmed no `com.joulewise.night*` label is loaded and no such plist is on disk — never wait for Ed to do it, and if that move makes the resident supervisor stale, commit, push, and exit so the watchdog's successor arms. Perform no other git operation in the canonical root; while any plan is armed, never fast-forward, pull, checkout, or otherwise move the canonical root or any listed measurement root—any post-arm move requires a re-arm with a re-pinned plan.
 Never arm or re-arm a night except through the documented `NIGHT_HANDBACK` email-then-arm procedure; Ed's NO always overrides.
 Arming a night obligates this session to end its loop and exit by the request deadline; the LaunchAgent is then the wake source.
 The first real window may be armed only under a v2 plan after both night agents are installed from that plan's `measurement_root` at its `measurement_head`.
diff --git a/docs/process/MAGISTRATE_WATCHDOG.md b/docs/process/MAGISTRATE_WATCHDOG.md
index 3df10d91..975829d1 100644
--- a/docs/process/MAGISTRATE_WATCHDOG.md
+++ b/docs/process/MAGISTRATE_WATCHDOG.md
@@ -186,7 +186,7 @@ The program guards every write path against the configured custody root. The mec
 - `launchd.out` and `launchd.err`, written by launchd at paths rendered in the plist.
 - Transient atomic replacements named `.<target>.<pid>.<uuid>.tmp` beside any target written through the atomic writer; each is normally replaced into its target after fsync, while a process crash can leave the temporary file for inspection.
 
-No status branch, checkout, plan, night result, `courier.sent`, or repository file is written by the service. The relaunched magistrate remains separately authorized to work in linked worktrees under repository rules; its prompt adds no service write path. Prompt line 24 adds one external write authority outside the custody root: commenting on and closing owner-authored `directive` issues on GitHub. At each launch, `@@FENCED_CHECKOUTS@@` is rendered as a deterministic JSON list containing the canonical repository and every authored, not-completed v2 plan's canonical measurement root and head. The prompt forbids Git operations in the canonical root and forbids moving every listed measurement root. Overlapping armed spans at different roots, or one canonical measurement root pinned at two heads, hold as `plan_conflict`; non-overlapping spans at different roots compose and all remain fenced. A post-arm move invalidates the pin and requires a re-arm with a re-pinned plan. Arming also obligates the session to end its loop and exit by the request deadline. The relaunched session may not ratify or amend process rules, decision-log entries, or skill doctrine; rule 11 routes those decisions to the cold gate or Ed.
+No status branch, checkout, plan, night result, `courier.sent`, or repository file is written by the service. The relaunched magistrate remains separately authorized to work in linked worktrees under repository rules; its prompt adds no service write path. Prompt line 24 adds one external write authority outside the custody root: commenting on and closing owner-authored `directive` issues on GitHub. At each launch, `@@FENCED_CHECKOUTS@@` is rendered as a deterministic JSON list containing the canonical repository and every authored, not-completed v2 plan's canonical measurement root and head. The prompt licenses exactly one Git operation in the canonical root — a fast-forward-only pull of a clean tree while nothing is armed or loaded (D-183; the evidence-night `check` performs it) — forbids every other, and forbids moving every listed measurement root. Overlapping armed spans at different roots, or one canonical measurement root pinned at two heads, hold as `plan_conflict`; non-overlapping spans at different roots compose and all remain fenced. A post-arm move invalidates the pin and requires a re-arm with a re-pinned plan. Arming also obligates the session to end its loop and exit by the request deadline. The relaunched session may not ratify or amend process rules, decision-log entries, or skill doctrine; rule 11 routes those decisions to the cold gate or Ed.
 
 ## Install handoff
 
diff --git a/docs/process/NIGHT_HANDBACK.md b/docs/process/NIGHT_HANDBACK.md
index 47633cfe..9ed2b3bf 100644
--- a/docs/process/NIGHT_HANDBACK.md
+++ b/docs/process/NIGHT_HANDBACK.md
@@ -295,6 +295,21 @@ after prepare; relay any mailbox NO into `<staging>/lifecycle/NO` before veto;
 `publish-install` repeats the veto observation and the loaded-jobs probe at the publication boundary and requires a fresh `check` record; the lead re-runs `check` after any change.
 Record 17's script set remains the fallback until the first live use succeeds.
 
+Pre-check step, ruled by the cold gate 2026-09-21 (packet 05 Q3): the census
+classifies every process outside the caller's ancestor chain as foreign, and
+the tracked check refuses on any foreign PID, so the session's own MCP helpers
+must be gone first. The ruled text:
+
+Before running `check` on a real plan, this session terminates its own idle
+MCP helpers. List the children of the session root: `pgrep -lP
+<session-root-pid>`. For every child whose command line contains `codex
+mcp-server`, send SIGTERM to that child and its descendants (`pkill -TERM -P
+<child-pid>`; `kill -TERM <child-pid>`), wait until `pgrep -f 'codex
+mcp-server'` lists no descendant of the session root, and record the PIDs
+terminated in the check record. Terminate nothing outside the session root's
+descendants. Then run `check`. If the census still reports any descendant of
+the own session root as foreign, stop; never relabel it "diagnostic".
+
 **Timeline.** The plan's relative boundaries are: install strictly before
 t0 − 600 s (the close is excluded); REQUEST and magistrate exit at
 t0 − 480 s; TERM at t0 − 360 s; KILL at t0 − 300 s. Acquisition,
diff --git a/docs/process_traces/2026-09-21-interactive-a87c3444/01-d183-canonical-self-fast-forward.md b/docs/process_traces/2026-09-21-interactive-a87c3444/01-d183-canonical-self-fast-forward.md
new file mode 100644
index 00000000..bea5ed5b
--- /dev/null
+++ b/docs/process_traces/2026-09-21-interactive-a87c3444/01-d183-canonical-self-fast-forward.md
@@ -0,0 +1,95 @@
+# Record 01 — D-183: no artificial owner stops; `check` fast-forwards the canonical checkout itself
+
+Interactive session `a87c3444` (Fable 5.1, Ed at the machine), 2026-09-21 21:37–23:xx PDT.
+
+## §1 Forcing problem (executed evidence)
+
+At 21:37 PDT Ed asked what was going on ("haven't got an email in a while").
+Bench observation from the canonical checkout and the custody root:
+
+- `git status -sb` in `/Users/edr/code/JouleWise`: `## main...origin/main [behind 157]`, HEAD `0959e613`.
+- `state.json`: activation `21752427` ACTIVE since `Sun Sep 20 03:19:26 2026`, supervisor pid 80188; heartbeat 21:30 09-21.
+- `RUN_STATE.md` on `origin/main` (pointer of 16:40 09-20): "THE ONE OWNER ACTION (unchanged since 05:10): fast-forward `/Users/edr/code/JouleWise`".
+- Gmail sent items to `claude2.glaring610@passmail.net`: last message 05:10 PDT 09-20 (`1a0beb3c25241ce3`); nothing after.
+- The stall: 05:10 09-20 → 21:40 09-21, about 40 h, with nothing armed and every merged PR green. The only precondition was a clean fast-forward the relaunch prompt forbade the headless session from performing ("Perform no git operation in the canonical root").
+
+Ed's ruling (verbatim, 21:50 PDT): "make sure no more idiotic stops artificially, you have gh auth for a reason"; "obviously idiotic and should not have a 40h stall, def fix stuff like that, the process is meant to prevent bad science not work for 40h".
+
+## §2 Actions at the bench
+
+1. 21:40:47 `git -C /Users/edr/code/JouleWise pull --ff-only` → HEAD `7e35d16a`; `git merge-base --is-ancestor 980f8d64 HEAD` → true (cure present).
+2. The holding activation's hold watch saw it, pushed its exit block (`9e0a4995`) and exited; the watchdog logged `clean activation exit` (event 283) then a 300 s `BACKOFF_USAGE` (event 284). Its exit note records that the headless session's Gmail auth had expired, so its exit email never went out (preserved on disk).
+3. Fix branch `fix/2026-09-21-canonical-self-fast-forward` in worktree `JouleWise-wt-selfff` off `9e0a4995`.
+
+## §3 The change
+
+- `joulewise/evidence_night.py`: `canonical_status`, `canonical_fast_forward` (clean tree → `git pull --ff-only` → re-check H; evidence `{before, after, pull}`), `canonical_check(..., may_fast_forward)`; `check` passes `may_fast_forward = <night_agents check passed>`.
+- `tests/test_evidence_night.py`: `test_canonical_fast_forwards_itself_when_nothing_is_loaded` (old → tip; `fast_forward` null and no pull when H present), `test_canonical_fast_forward_refuses_dirty_tree_and_loaded_agents`, and the amended `test_canonical_must_contain_h_and_be_clean` (no upstream → `fast-forward failed`, HEAD unmoved).
+- Docs: `MAGISTRATE_RELAUNCH_PROMPT.md` (one licensed move; exit-for-successor instead of holding), `MAGISTRATE_WATCHDOG.md` line 189, `docs/contracts/evidence_night_entry.md` item 1 (+ the "no command fast-forwards" sentence), `docs/decision_log.md` D-183.
+
+Soundness fences unchanged: nothing moves while a night label is loaded or a plist is present (item 0 failed → pull not licensed); no reset or force; dirty trees refuse; the supervisor-freshness rule (records 19/21) still refuses the session's own stale supervisor, which is now the documented hand-off, not a hold.
+
+## §4 Bench evidence
+
+- Targeted: `pytest -q tests/test_evidence_night.py -k 'canonical or census_fix'` → `4 passed, 90 deselected in 3.09s` (after fixing one assertion slice, `c[-3:]` → `c[-2:]`, in the new test).
+- Full affected modules (`test_evidence_night`, `test_docs_freshness`, `test_identity_pins`, `test_schemas`, `test_magistrate_watchdog`): see §6.
+
+## §5 Reviews
+
+- Opus counter-review (contract lens): see §6.
+- Sol refuter (execution lens, counterfactual repos + mutation probe): see §6.
+
+## §6 Results (filled as they land)
+
+### §6.1 Full affected modules, round 1 (head `98e05bba`)
+
+`pytest -q tests/test_evidence_night.py tests/test_docs_freshness.py tests/test_identity_pins.py tests/test_schemas.py tests/test_magistrate_watchdog.py` → `2 failed, 300 passed, 1 skipped, 1044 subtests passed in 177.16s`. Both failures in `test_docs_freshness` (decision index vs bodies; dangling `D-183` references): the D-183 index row existed but its `## D-183:` body did not. Fixed by appending the body; `tests/test_docs_freshness.py` → `31 passed, 383 subtests passed`.
+
+### §6.2 Opus counter-review (contract lens, on `98e05bba`) — VERDICT FIX-FIRST, no BLOCKER
+
+Findings and dispositions (lead-triaged; nothing silently applied):
+
+| # | Tier | Finding | Disposition |
+| --- | --- | --- | --- |
+| 1 | NIT | Contract parenthetical for item 0 omitted "discovery known" (code is the conservative superset). | FIXED: contract item 1 text now lists all three conditions. |
+| 2 | SHOULD-FIX | Prompt licensed a bare hand-run `pull --ff-only` with a weaker prose precondition than the code's. | FIXED: prompt licenses the move via `check`, or by hand only after confirming no `com.joulewise.night*` label loaded and no plist on disk. |
+| 3 | SHOULD-FIX | Stale-supervisor refusal after an in-check move surfaced only as the generic `pre-arm checks failed`; a headless loop could re-run `check` forever. | FIXED: the refusal text names the hand-off ("commit, push and exit so the watchdog's successor arms (D-183)") and `check` re-raises exactly the stale case as its own cause (other supervisor causes stay generic — two existing tests pin that). |
+| 4 | SHOULD-FIX | No test for the post-pull still-lacks-H branch. | FIXED: `test_canonical_fast_forward_that_still_lacks_h_refuses_and_keeps_evidence` (upstream advances without the fix; HEAD moves old → other; refusal names both shas). |
+| 5 | SHOULD-FIX | No test of the records-19/21 hand-off after an in-check move. | FIXED: `test_fast_forward_makes_the_resident_supervisor_stale_and_says_so` (supervisor started before the move refuses with the named hand-off; one started after passes). |
+| 6 | SHOULD-FIX | Evidence of a pull that moved the tree was discarded when the check then refused. | FIXED: the still-lacks-H refusal carries before/after shas in its cause; `clean_before` observation retained in the evidence. |
+| 7 | SHOULD-FIX | The pull had no timeout and inherited stdin: an unreachable remote or credential prompt would hang the unattended loop — the stall class D-183 removes. | FIXED: `FAST_FORWARD_TIMEOUT_S = 120`, `GIT_TERMINAL_PROMPT=0`, `TimeoutExpired` → refusal; `test_canonical_fast_forward_is_bounded_and_prompt_free` pins both. `probe_command` gained an `env` merge parameter. |
+| 8 | NIT | Clean-before-move observation dropped. | FIXED with 6. |
+| 9 | NIT | Still-lacks-H message differed from the documented cause prefix. | FIXED: prefix `canonical fast-forward failed:` on every refusal of the move. |
+| 10 | NIT | Divergent upstream and plist-present-but-ABSENT branches untested. | ACCEPTED as nits: divergence is a real `--ff-only` rejection routed through the same `returncode` refusal the no-upstream test exercises; plist presence is item 0's existing coverage. |
+| 11 | NIT | TOCTOU between the item-0 sample and the pull for a *different* candidate's install (seconds wide, single-operator machine). | ACCEPTED: the per-candidate lock does not cover it; the pull is fast-forward-only and the other candidate's own `check` re-observes. Recorded, not fixed. |
+| 12 | NIT | Pull stdout/stderr recorded verbatim could carry a remote URL. | ACCEPTED: the remote is a public GitHub URL without credentials; revisit if a credential-bearing remote is ever configured. |
+
+### §6.3 Full affected modules, round 2 (after the Opus fixes)
+
+`pytest -q tests/test_evidence_night.py tests/test_docs_freshness.py tests/test_magistrate_watchdog.py` → `224 passed, 692 subtests passed in 175.07s`, exit 0. Two fix iterations inside the round, both test-side: a wrapped runner that delegated to the real `probe_command` let a real `pgrep` see the live successor magistrate (never delegate past the fixture runner), and the bounded-pull test first expected the canonical reason on the raised line (only night_agents, census and the stale-supervisor case are re-raised verbatim; canonical stays under the generic line).
+
+### §6.4 Sol refuter (execution lens, gpt-5.6-sol high, read-only, on `98e05bba`) — VERDICT BLOCK on that head; delta re-audit on `c84f4db0` clears it
+
+Executed by the refuter against the real functions with counterfactual repositories (its scripts: `/tmp/canonical_counterfactuals.py`, `/tmp/run_canonical_mutation.py`, `/tmp/pull_bound_probe.py`): (a) diverged upstream → refused (`Not possible to fast-forward`), HEAD unmoved; (b) deleted remote → refused, HEAD unmoved; (c) upstream on a branch without H → refused but HEAD moved and the structured evidence was discarded; (d) untracked file → fast-forwarded with evidence; (e) staged change → refused, HEAD unmoved. JSON serialisation of real records OK. Mutations on `98e05bba`: `may_fast_forward=True` killed by the loaded-agents test; the post-pull containment guard replaced by `pass` SURVIVED.
+
+| Tier | Finding (on `98e05bba`) | Disposition |
+| --- | --- | --- |
+| BLOCKER | Wrong upstream moves canonical before refusal while discarding before/after/pull evidence. | Same finding as Opus #6; FIXED in `c84f4db0`: the refusal names `HEAD moved <before> -> <after>`; `clean_before` kept. The move itself is inherent to `pull --ff-only` and stays within the checkout's upstream branch; documented in contract item 1. |
+| BLOCKER | `git pull --ff-only` unbounded and prompt-capable (`pull kwargs: {}`). | Same as Opus #7; FIXED in `c84f4db0`: `timeout=120`, `GIT_TERMINAL_PROMPT=0`, `TimeoutExpired` → refusal. |
+| SHOULD-FIX | Post-pull containment guard not pinned by any test (mutation survived). | FIXED in `c84f4db0`: `test_canonical_fast_forward_that_still_lacks_h_refuses_and_keeps_evidence`. |
+
+**Delta re-audit (lead, bench, `c84f4db0`, the refuter's own scripts re-pinned with `sed 's/98e05bba:/c84f4db0:/'` and the mutation's target text updated to the new refusal):**
+
+- `pull_bound_probe.py` → `pull kwargs: {'timeout': 120, 'env': {'GIT_TERMINAL_PROMPT': '0'}}`; `return keys: ['after', 'before', 'clean_before', 'pull']`.
+- `run_canonical_mutation.py postpull_pass` → `FAILED (failures=1)` over the five canonical tests: KILLED.
+- `run_canonical_mutation.py license_true` → `FAILED (errors=1)`: KILLED.
+
+Same-signature statement: the two blockers and the should-fix are one fix round; their signatures (unbounded subprocess, evidence discarded on refusal, unpinned guard) do not recur in the delta. No round three.
+
+### §6.5 Terminal review (Fable, full session context)
+
+Merge candidate = the records-only head after this section (sha in the PR ledger row 12). Diff read in full at the bench: one function pair plus a flag in `evidence_night.py`, `probe_command` env merge, five tests, four doc edits, D-183 row + body. Fences verified by reading and by the refuter's executed cases: no move while loaded (item 0 gate, mutation killed), no reset/force (only `pull --ff-only`), dirty refuses (case e), bounded and prompt-free (probe). Verdict: MERGE on green hosted checks.
+
+## §7 Second artificial stop found the same night: a refused 09-16 night root blocked `check` (retired at the bench)
+
+Successor activation 29ea94df's first live `check` (21:58 PDT, candidate t0 22:38) refused on two items: `census` (two interactive Claude windows, expected until Ed closes them) and `retained_roots`: `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916` classified UNKNOWN because it has neither `night/courier.sent` nor `night/result.json`. Bench facts: that night ran 09-16 (gate GO 09:45; dead-man refused at 13:20 while the chain was alive; `night/refusal.json` = `night_chain_alive`; chain exited 20:52) and its durable record is on `origin/night-results/d079-epoch-25g83-derivation-n1-20260916` (`6725e481`). The root had sat there since 09-16 because the earlier arm scripts never inventoried retained roots; the new `check` does, and would have refused every arm from now on. Under D-183 and the retirement precedent (`~/night-archive/*-plan-root-retired-<epoch>` for the 09-13 and 09-15 roots) the lead retired it at 22:03 PDT: SHA256SUMS + lstat inventory written first, `mv` to `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260916-plan-root-retired-1790053407`, digests re-verified after the move (0 mismatches). Nothing deleted. Follow-up for the successor: `retained_roots` should classify a root with `night/refusal.json` plus a pushed durable branch as retained, not UNKNOWN (lane to register: RETAINED-ROOT-REFUSAL-CLASS-01).
diff --git a/joulewise/evidence_night.py b/joulewise/evidence_night.py
index 6f6f5cba..65970410 100644
--- a/joulewise/evidence_night.py
+++ b/joulewise/evidence_night.py
@@ -23,10 +23,12 @@ REMOTE = "https://github.com/mpmdw/JouleWise"
 SCHEMA = "joulewise.evidence_prepare.v1"
 STEPS = ("clone", "venv", "plan", "wrapper", "render", "complete")
 # Activation records 19/21: every arm needs a supervisor started after the
-# canonical fast-forward; H must include the bracketed census cure.
+# canonical fast-forward; H must include the bracketed census cure. D-183:
+# `check` performs that fast-forward itself when nothing is loaded.
 CENSUS_FIX = "980f8d6452fb6923644bdac1e243ce0a344c881f"
 CANONICAL = "/Users/edr/code/JouleWise"
 SUPERVISOR_STATE = "/Users/edr/night-custody/magistrate/state.json"
+FAST_FORWARD_TIMEOUT_S = 120
 MAGISTRATE = "/Users/edr/night-custody/magistrate"
 DIRECTIVES_ARGV = ("gh", "issue", "list", "--repo", "mpmdw/JouleWise", "--label",
                    "directive", "--state", "open", "--author", "mpmdw", "--json",
@@ -580,9 +582,10 @@ print(json.dumps(s))
     return json.loads(run([root / ".venv/bin/python", "-B", "-c", code, plan], cwd=root))
 
 
-def probe_command(argv, *, cwd=None, timeout=None):
+def probe_command(argv, *, cwd=None, timeout=None, env=None):
     return subprocess.run(list(map(str, argv)), cwd=cwd, capture_output=True, text=True,
-                          check=False, timeout=timeout, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
+                          check=False, timeout=timeout,
+                          env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", **(env or {})))
 
 
 def observation_record(result):
@@ -596,16 +599,54 @@ def contains_head(canonical, head, commit, runner):
     return result.returncode == 0
 
 
-def canonical_check(state, canonical, runner):
-    if not contains_head(Path(state["measurement_root"]), CENSUS_FIX, state["head"], runner):
-        raise Refused("candidate H does not contain the census fix " + CENSUS_FIX)
-    if not contains_head(canonical, state["head"], "HEAD", runner):
-        raise Refused("canonical checkout does not contain candidate H")
+def canonical_status(canonical, runner):
     result = runner(["git", "-C", canonical, "--no-optional-locks", "status", "--porcelain", "-uno"])
     if result.returncode or result.stdout.strip():
         raise Refused("canonical checkout is dirty or unreadable: " + result.stdout + result.stderr)
+    return result
+
+
+def canonical_fast_forward(state, canonical, runner):
+    # D-183 (Ed, 2026-09-21): a clean canonical checkout behind candidate H is
+    # moved here by a fast-forward-only pull whenever no night agent is loaded;
+    # it is never an owner action. A dirty tree, a divergent or unreachable
+    # remote, or a pull that still lacks H refuses; nothing is reset or forced.
+    clean_before = canonical_status(canonical, runner)
+    before = runner(["git", "-C", canonical, "rev-parse", "HEAD"])
+    if before.returncode:
+        raise Refused("cannot read canonical HEAD: " + before.stderr.strip())
+    # Bounded and prompt-free: an unreachable remote or a credential prompt must
+    # refuse, never hang the unattended loop (the stall class D-183 removes).
+    try:
+        pull = runner(["git", "-C", canonical, "pull", "--ff-only"], timeout=FAST_FORWARD_TIMEOUT_S,
+                      env={"GIT_TERMINAL_PROMPT": "0"})
+    except subprocess.TimeoutExpired as exc:
+        raise Refused(f"canonical fast-forward failed: timed out after {FAST_FORWARD_TIMEOUT_S} s") from exc
+    if pull.returncode:
+        raise Refused("canonical fast-forward failed: " + (pull.stderr.strip() or pull.stdout.strip()))
+    after = runner(["git", "-C", canonical, "rev-parse", "HEAD"])
+    if after.returncode:
+        raise Refused("cannot read canonical HEAD after fast-forward: " + after.stderr.strip())
+    moved = dict(before=before.stdout.strip(), after=after.stdout.strip(), pull=observation_record(pull),
+                 clean_before=observation_record(clean_before))
+    if not contains_head(canonical, state["head"], "HEAD", runner):
+        raise Refused("canonical fast-forward failed: HEAD moved " + moved["before"] + " -> " + moved["after"]
+                      + " but still does not contain candidate H")
+    return moved
+
+
+def canonical_check(state, canonical, runner, may_fast_forward=False):
+    if not contains_head(Path(state["measurement_root"]), CENSUS_FIX, state["head"], runner):
+        raise Refused("candidate H does not contain the census fix " + CENSUS_FIX)
+    fast_forward = None
+    if not contains_head(canonical, state["head"], "HEAD", runner):
+        if not may_fast_forward:
+            raise Refused("canonical checkout does not contain candidate H "
+                          "(fast-forward not licensed while night agents are loaded)")
+        fast_forward = canonical_fast_forward(state, canonical, runner)
+    result = canonical_status(canonical, runner)
     return dict(path=str(canonical), required_head=state["head"], census_fix=CENSUS_FIX,
-                status=observation_record(result))
+                status=observation_record(result), fast_forward=fast_forward)
 
 
 def supervisor_check(state, canonical, state_path, runner):
@@ -649,23 +690,58 @@ def supervisor_check(state, canonical, state_path, runner):
     if arrival is None:
         raise Refused("no reflog entry continuously contains H")
     if started <= arrival:
-        raise Refused(f"stale resident supervisor pid {pid}: started {started}, H arrived {arrival}")
+        raise Refused(f"stale resident supervisor pid {pid}: started {started}, H arrived {arrival}; "
+                      "this session cannot arm — commit, push and exit so the watchdog's successor arms (D-183)")
     return dict(evidence, started_epoch_s=started, head_arrived_epoch_s=arrival,
                 continuous_reflog=walked)
 
 
-def retained_roots(state):
+# Night records that classify a discovered custody root. Several families can
+# coexist (a refusal written mid-chain, then chain.exited); an open chain takes
+# precedence over every marker, and a retained root whose plan span is still
+# active by the watchdog's rule is ACTIVE too. The installer refuses re-admission
+# on the same names (night_agent_install); the refusal names come from the
+# driver's own run_night._refusal_paths, and the span rule from the watchdog's
+# plan_span_active — both entry-checkout modules, evaluated with the entry
+# checkout's constants.
+TERMINAL_NIGHT_RECORDS = ("courier.sent", "result.json", "chain.exited")
+
+
+def retained_roots(state, now_epoch_s=None):
+    from joulewise.night_gate import NightPlan, PlanError
+    from scripts.magistrate_watchdog import Storage, plan_span_active
+    from scripts.run_night import _refusal_paths
+    now = time.time() if now_epoch_s is None else now_epoch_s
     inventory = []
     for plan in sorted((safe_path(state["roots_under"]) / "night-custody").glob("*/night_plan.json")):
         safe_path(plan)
         if not plan.is_file():
             raise Refused("retained plan is not a regular non-symlink file: " + str(plan))
-        markers = [p for p in (plan.parent / "night/courier.sent", plan.parent / "night/result.json")
-                   if safe_path(p).is_file()]
-        inventory.append(dict(plan=str(plan), classification="retained" if markers else "UNKNOWN",
+        night = plan.parent / "night"
+        markers = [night / name for name in TERMINAL_NIGHT_RECORDS if safe_path(night / name).is_file()]
+        markers.extend(p for p in _refusal_paths(night) if safe_path(p).is_file())
+        chain_open = (safe_path(night / "chain.started").is_file()
+                      and not safe_path(night / "chain.exited").is_file())
+        if chain_open:
+            classification, reason = "ACTIVE", "chain.started without chain.exited"
+        elif not markers:
+            classification, reason = "UNKNOWN", "no terminal night record"
+        else:
+            classification, reason = "retained", "terminal record present; plan span over"
+            try:
+                parsed = NightPlan.from_mapping(json.loads(plan.read_text(encoding="utf-8")))
+                if os.path.realpath(parsed.custody_root) != os.path.realpath(plan.parent):
+                    classification = "UNKNOWN"
+                    reason = f"plan custody_root {parsed.custody_root} is not {plan.parent}"
+                elif plan_span_active(parsed, now, Storage(plan.parent)):
+                    classification = "ACTIVE"
+                    reason = "plan span active (scripts/magistrate_watchdog.plan_span_active)"
+            except (PlanError, ValueError, TypeError, OverflowError, OSError) as exc:
+                classification, reason = "UNKNOWN", f"plan unreadable: {type(exc).__name__}: {exc}"
+        inventory.append(dict(plan=str(plan), classification=classification, reason=reason,
                               evidence=[str(p) for p in markers]))
-    return dict(inventory=inventory, verdict="fail" if any(
-        row["classification"] == "UNKNOWN" for row in inventory) else "pass")
+    return dict(inventory=inventory, now_epoch_s=now, verdict="pass" if all(
+        row["classification"] == "retained" for row in inventory) else "fail")
 
 
 def clone_census(state, caller_pid, observation=None, *, argv_only=False):
@@ -829,8 +905,9 @@ def check(*, candidate, canonical=CANONICAL, supervisor_state=SUPERVISOR_STATE,
             return dict(digests=state["digests"], schedule=s)
 
         if inspect("sealed", seal):
-            inspect("night_agents", lambda: require_no_night_agents(night_agents(state, launchctl_bin)))
-            inspect("canonical", lambda: canonical_check(state, safe_path(canonical), runner))
+            nothing_loaded = inspect("night_agents", lambda: require_no_night_agents(night_agents(state, launchctl_bin)))
+            inspect("canonical", lambda: canonical_check(state, safe_path(canonical), runner,
+                                                         may_fast_forward=nothing_loaded))
             inspect("supervisor", lambda: supervisor_check(state, safe_path(canonical), supervisor_state, runner))
             courier = shutil.which("claude")
             checks["courier"] = dict(verdict="pass" if courier else "fail", path=courier,
@@ -850,6 +927,9 @@ def check(*, candidate, canonical=CANONICAL, supervisor_state=SUPERVISOR_STATE,
                 reason = checks.get(name, {}).get("reason")
                 if reason:
                     raise Refused(reason)
+            stale = checks.get("supervisor", {}).get("reason", "")
+            if stale.startswith("stale resident supervisor"):
+                raise Refused(stale)
             raise Refused("pre-arm checks failed: " + ", ".join(k for k, v in checks.items() if v["verdict"] != "pass")
                           + "; see " + str(path))
         return record
diff --git a/tests/test_evidence_night.py b/tests/test_evidence_night.py
index dd38214e..b3b3afd2 100644
--- a/tests/test_evidence_night.py
+++ b/tests/test_evidence_night.py
@@ -635,6 +635,28 @@ class LifecycleTests(unittest.TestCase):
         self.assertNotIn(entry.CANONICAL, list(map(str, argv)))
         return entry.probe_command(argv, **kwargs)
 
+    def sibling_plan(self, root, *, t0=None, custody_root=None):
+        # A parseable v2 plan for a sibling custody root; ten days old by default,
+        # so the watchdog's span rule reads it as long over.
+        t0 = (int(time.time()) // 60 - 60 * 24 * 10) * 60 if t0 is None else t0
+        return dict(schema="joulewise.night_plan.v2", schema_version=2, plan_id=root.name,
+                    receipt_class="DIAGNOSTIC_NO_PACK", t0_epoch_s=float(t0), window_max_s=9000,
+                    authored_epoch_s=float(t0 - 3600), repo_head=self.head, chain_path="chain.zsh",
+                    chain_sha256_path="chain.zsh.sha256",
+                    custody_root=str(root) if custody_root is None else custody_root,
+                    measurement_head=self.head, measurement_root=str(self.root),
+                    registration_path="docs/registration.md")
+
+    def sibling_root(self, name, *markers, t0=None, custody_root=None, plan_text=None):
+        root = self.custody.parent / name
+        (root / "night").mkdir(parents=True)
+        for marker in markers:
+            (root / "night" / marker).write_text("{}")
+        if plan_text is None:
+            plan_text = json.dumps(self.sibling_plan(root, t0=t0, custody_root=custody_root))
+        (root / "night_plan.json").write_text(plan_text)
+        return root
+
     def checked(self, fail=None):
         if fail:
             with self.assertRaisesRegex(entry.Refused, fail):
@@ -666,12 +688,107 @@ class LifecycleTests(unittest.TestCase):
         (self.canonical / "tracked").write_text("dirty")
         self.assertFalse(self.checked("canonical")["armable"])
         subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", self.old], check=True)
-        self.checked("canonical")
+        # Behind H with no upstream: the fast-forward attempt refuses, nothing moves.
+        reason = self.checked("canonical")["checks"]["canonical"]["reason"]
+        self.assertIn("fast-forward failed", reason)
+        self.assertEqual(self.canonical_head(), self.old)
         subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", self.tip], check=True)
         (self.canonical / "untracked").write_text("irrelevant")
         self.assertTrue(self.checked()["rehearsal_ready"])
         self.assertTrue(any(c[-4:] == ["--no-optional-locks", "status", "--porcelain", "-uno"] for c in self.calls))
 
+    def canonical_head(self):
+        return subprocess.check_output(["git", "-C", str(self.canonical), "rev-parse", "HEAD"], text=True).strip()
+
+    def give_canonical_upstream(self):
+        bare = self.base / "upstream.git"
+        subprocess.run(["git", "clone", "-q", "--bare", str(self.canonical), str(bare)], check=True)
+        branch = subprocess.check_output(["git", "-C", str(self.canonical), "rev-parse", "--abbrev-ref", "HEAD"],
+                                         text=True).strip()
+        subprocess.run(["git", "-C", str(self.canonical), "remote", "add", "origin", str(bare)], check=True)
+        subprocess.run(["git", "-C", str(self.canonical), "fetch", "-q", "origin"], check=True)
+        subprocess.run(["git", "-C", str(self.canonical), "branch", "-q", "--set-upstream-to=origin/" + branch],
+                       check=True)
+        return bare
+
+    def test_canonical_fast_forwards_itself_when_nothing_is_loaded(self):
+        # D-183: a clean canonical checkout behind H is moved by check itself.
+        self.give_canonical_upstream()
+        subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", self.old], check=True)
+        record = self.checked()
+        self.assertTrue(record["rehearsal_ready"])
+        moved = record["checks"]["canonical"]["fast_forward"]
+        self.assertEqual((moved["before"], moved["after"]), (self.old, self.tip))
+        self.assertEqual(moved["pull"]["exit_code"], 0)
+        self.assertEqual(self.canonical_head(), self.tip)
+        self.assertTrue(any(c[-2:] == ["pull", "--ff-only"] and str(self.canonical) in c for c in self.calls))
+        # Already containing H: no pull is attempted.
+        self.calls.clear()
+        self.assertIsNone(self.checked()["checks"]["canonical"]["fast_forward"])
+        self.assertFalse(any("pull" in c for c in self.calls))
+
+    def test_canonical_fast_forward_that_still_lacks_h_refuses_and_keeps_evidence(self):
+        bare = self.give_canonical_upstream()
+        # The upstream branch advances WITHOUT the fix: old -> other.
+        subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", self.old], check=True)
+        other = self.commit("other", self.arrival + 200)
+        branch = subprocess.check_output(["git", "-C", str(self.canonical), "rev-parse", "--abbrev-ref", "HEAD"],
+                                         text=True).strip()
+        subprocess.run(["git", "-C", str(self.canonical), "push", "-q", "-f", "origin", f"HEAD:{branch}"], check=True)
+        subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", self.old], check=True)
+        reason = self.checked("canonical")["checks"]["canonical"]["reason"]
+        self.assertIn("canonical fast-forward failed: HEAD moved " + self.old + " -> " + other, reason)
+        self.assertIn("still does not contain candidate H", reason)
+        self.assertEqual(self.canonical_head(), other)
+        self.assertIn(str(bare), subprocess.check_output(["git", "-C", str(self.canonical), "remote", "-v"], text=True))
+
+    def test_canonical_fast_forward_is_bounded_and_prompt_free(self):
+        self.give_canonical_upstream()
+        subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", self.old], check=True)
+        seen = {}
+
+        def runner(argv, **kwargs):
+            if list(map(str, argv))[-2:] == ["pull", "--ff-only"]:
+                seen.update(kwargs)
+                raise subprocess.TimeoutExpired(argv, kwargs.get("timeout"))
+            return self.runner(argv, **kwargs)
+        with patch.dict(self.kw, runner=runner):
+            record = self.checked("canonical")
+        self.assertEqual(seen, dict(timeout=entry.FAST_FORWARD_TIMEOUT_S, env={"GIT_TERMINAL_PROMPT": "0"}))
+        self.assertEqual(self.canonical_head(), self.old)
+        self.assertIn("timed out", record["checks"]["canonical"]["reason"])
+
+    def test_fast_forward_makes_the_resident_supervisor_stale_and_says_so(self):
+        # Records 19/21 after an in-check move: the session's own supervisor predates
+        # the arrival of H and the refusal names the hand-off (D-183).
+        self.give_canonical_upstream()
+        subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", self.old], check=True)
+        self.live_supervisor(self.arrival + 50)
+        record = self.checked("stale resident supervisor pid 42")
+        self.assertEqual(self.canonical_head(), self.tip)
+        self.assertEqual(record["checks"]["canonical"]["verdict"], "pass")
+        reason = record["checks"]["supervisor"]["reason"]
+        self.assertIn("exit so the watchdog's successor arms", reason)
+        self.assertGreaterEqual(record["checks"]["supervisor"].get("head_arrived_epoch_s", 0) or 0, 0)
+        # A supervisor started after the move passes.
+        self.live_supervisor(time.time() + 5)
+        self.assertTrue(self.checked()["rehearsal_ready"])
+
+    def test_canonical_fast_forward_refuses_dirty_tree_and_loaded_agents(self):
+        self.give_canonical_upstream()
+        subprocess.run(["git", "-C", str(self.canonical), "reset", "--hard", "-q", self.old], check=True)
+        (self.canonical / "tracked").write_text("dirty")
+        self.assertIn("dirty", self.checked("canonical")["checks"]["canonical"]["reason"])
+        self.assertEqual(self.canonical_head(), self.old)
+        subprocess.run(["git", "-C", str(self.canonical), "checkout", "-q", "--", "tracked"], check=True)
+        loaded = dict(self.absent_agents, jobs=[dict(label="com.joulewise.night", liveness="LOADED"),
+                                                dict(label="com.joulewise.night.deadman", liveness="ABSENT")])
+        with patch.object(entry, "night_agents", return_value=loaded):
+            record = self.checked("night agents already loaded")
+        self.assertIn("not licensed while night agents are loaded", record["checks"]["canonical"]["reason"])
+        self.assertEqual(self.canonical_head(), self.old)
+        self.assertFalse(any("pull" in c for c in self.calls))
+
     def test_candidate_must_contain_census_fix(self):
         with patch.object(entry, "CENSUS_FIX", self.tip):
             self.assertIn("census fix", self.checked("canonical")["checks"]["canonical"]["reason"])
@@ -717,18 +834,113 @@ class LifecycleTests(unittest.TestCase):
             self.checked("courier")
 
     def test_discovery_retains_every_harvested_root_and_refuses_unknown(self):
-        for i, marker in enumerate(("courier.sent", "result.json", None)):
-            root = self.custody.parent / f"prior-{i}"
-            (root / "night").mkdir(parents=True)
-            (root / "night_plan.json").write_text("{}")
-            if marker:
-                (root / "night" / marker).write_text("{}")
+        markers = ("courier.sent", "result.json", "chain.exited", "refusal.json", "refusal-2.json",
+                   "calibration-refusal.json", "calibration-refusal.json.1789617139.json", None)
+        for i, marker in enumerate(markers):
+            self.sibling_root(f"prior-{i}", *([marker] if marker else []))
         result = self.checked("retained_roots")["checks"]["retained_roots"]
-        self.assertEqual([r["classification"] for r in result["inventory"]], ["retained", "retained", "UNKNOWN"])
+        self.assertEqual([r["classification"] for r in result["inventory"]],
+                         ["retained"] * (len(markers) - 1) + ["UNKNOWN"])
+        self.assertEqual([r["evidence"] for r in result["inventory"]],
+                         [[str(self.custody.parent / f"prior-{i}/night/{m}")] for i, m in enumerate(markers[:-1])] + [[]])
+        self.assertEqual(result["inventory"][-1]["reason"], "no terminal night record")
+        root = self.custody.parent / f"prior-{len(markers) - 1}"
         self.assertTrue((root / "night_plan.json").exists())
         (root / "night/result.json").write_text("{}")
         self.assertTrue(self.checked()["rehearsal_ready"])
 
+    def test_discovery_refuses_an_open_chain_and_ignores_non_marker_records(self):
+        # A refused night whose chain was killed: refusal.json + chain.started + chain.exited
+        # (the 2026-09-16 root's shape) is retained; the same root before chain.exited is ACTIVE.
+        root = self.sibling_root("refused", "refusal.json", "chain.started", "receipt.json", "censuses.jsonl")
+        result = self.checked("retained_roots")["checks"]["retained_roots"]
+        self.assertEqual([(r["classification"], r["reason"]) for r in result["inventory"]],
+                         [("ACTIVE", "chain.started without chain.exited")])
+        (root / "night/chain.exited").write_text('{"exit_code": -15}')
+        result = self.checked()["checks"]["retained_roots"]
+        self.assertEqual([(r["classification"], r["reason"]) for r in result["inventory"]],
+                         [("retained", "terminal record present; plan span over")])
+        self.assertEqual(result["inventory"][0]["evidence"],
+                         [str(root / "night/chain.exited"), str(root / "night/refusal.json")])
+        # An open chain stays ACTIVE even when a courier marker exists.
+        (root / "night/chain.exited").unlink()
+        (root / "night/courier.sent").write_text("{}")
+        self.assertEqual(self.checked("retained_roots")["checks"]["retained_roots"]["inventory"][0]["classification"], "ACTIVE")
+        # Receipt-only and stray-file roots are unknown.
+        for name in ("courier.sent", "chain.started", "refusal.json"):
+            (root / "night" / name).unlink()
+        self.assertEqual(self.checked("retained_roots")["checks"]["retained_roots"]["inventory"][0]["classification"], "UNKNOWN")
+
+    def test_retained_root_classification_ruled_cases(self):
+        # Cold-gate ruling 2026-09-21 (packet 05, Q4): active is tested before retained.
+        cases = [
+            (("refusal.json",), "retained"), (("chain.exited",), "retained"),
+            (("refusal-3.json",), "retained"), (("calibration-refusal.json.2.json",), "retained"),
+            (("chain.started",), "ACTIVE"),
+            (("chain.started", "calibration-refusal.json"), "ACTIVE"),
+            (("chain.started", "chain.exited"), "retained"),
+            ((), "UNKNOWN"),
+        ]
+        state = {"roots_under": str(self.custody.parent.parent)}
+        for i, (names, expected) in enumerate(cases):
+            self.sibling_root(f"case-{i}", *names)
+        # A refusal record that is a directory does not count.
+        root = self.sibling_root("case-dir")
+        (root / "night/refusal.json").mkdir()
+        result = entry.retained_roots(state)
+        by_name = {Path(r["plan"]).parent.name: r for r in result["inventory"]}
+        for i, (names, expected) in enumerate(cases):
+            with self.subTest(names=names):
+                row = by_name[f"case-{i}"]
+                self.assertEqual(row["classification"], expected)
+                self.assertEqual(row["evidence"], [str(self.custody.parent / f"case-{i}/night/{n}")
+                                                   for n in sorted(names) if n != "chain.started"])
+        self.assertEqual((by_name["case-dir"]["classification"], by_name["case-dir"]["evidence"]), ("UNKNOWN", []))
+        self.assertEqual(result["verdict"], "fail")
+        # Through the check: an ACTIVE root alone refuses naming retained_roots.
+        for name in list(by_name):
+            if name != "case-4":
+                shutil.rmtree(self.custody.parent / name)
+        with self.assertRaisesRegex(entry.Refused, "retained_roots"):
+            entry.check(**self.kw)
+        # A refusal-only root alone passes, with the complete evidence path (ruled case 1).
+        shutil.rmtree(self.custody.parent / "case-4")
+        only = self.sibling_root("refusal-only", "refusal.json")
+        record = self.checked()
+        self.assertTrue(record["rehearsal_ready"])
+        self.assertEqual(record["checks"]["retained_roots"]["inventory"],
+                         [dict(plan=str(only / "night_plan.json"), classification="retained",
+                               reason="terminal record present; plan span over",
+                               evidence=[str(only / "night/refusal.json")])])
+
+    def test_discovery_span_fence_reuses_the_watchdog_rule(self):
+        from scripts.magistrate_watchdog import COURIER_DEADLINE_S
+        state = {"roots_under": str(self.custody.parent.parent)}
+        t0 = 1_800_000_000
+        root = self.sibling_root("span", "chain.started", "chain.exited", t0=t0)
+        # Inside t0 + window + courier deadline: ACTIVE even though the chain exited.
+        row = entry.retained_roots(state, now_epoch_s=t0 + 600)["inventory"][0]
+        self.assertEqual((row["classification"], row["reason"]),
+                         ("ACTIVE", "plan span active (scripts/magistrate_watchdog.plan_span_active)"))
+        # Still inside the completion interval with courier.sent: the watchdog keeps the span active.
+        (root / "night/courier.sent").write_text("{}")
+        self.assertEqual(entry.retained_roots(state, now_epoch_s=t0 + 9000 + COURIER_DEADLINE_S - 1)["inventory"][0]["classification"], "ACTIVE")
+        # After the completion interval, courier.sent closes the span.
+        self.assertEqual(entry.retained_roots(state, now_epoch_s=t0 + 9000 + COURIER_DEADLINE_S + 1)["inventory"][0]["classification"], "retained")
+        # Without courier.sent the span runs to the dead-man plus the courier-lock freshness window.
+        (root / "night/courier.sent").unlink()
+        self.assertEqual(entry.retained_roots(state, now_epoch_s=t0 + 9000 + COURIER_DEADLINE_S + 1)["inventory"][0]["classification"], "ACTIVE")
+        self.assertEqual(entry.retained_roots(state, now_epoch_s=t0 + 30 * 86400)["inventory"][0]["classification"], "retained")
+        # A plan whose custody_root is not its own directory, or that cannot be parsed, is UNKNOWN.
+        shutil.rmtree(root)
+        self.sibling_root("moved", "courier.sent", custody_root="/Users/nobody/night-custody/moved")
+        row = entry.retained_roots(state)["inventory"][0]
+        self.assertEqual(row["classification"], "UNKNOWN"); self.assertIn("custody_root", row["reason"])
+        shutil.rmtree(self.custody.parent / "moved")
+        self.sibling_root("bare", "courier.sent", plan_text="{}")
+        row = entry.retained_roots(state)["inventory"][0]
+        self.assertEqual(row["classification"], "UNKNOWN"); self.assertTrue(row["reason"].startswith("plan unreadable: PlanError"))
+
     def test_census_foreign_workload_and_unknown_refuse(self):
         from dataclasses import replace
         from tests.test_arm_census import observation, row
```
