import json, collections

KP = "docs/process/state_kernel.json"
k = json.load(open(KP))
T = k["tasks"]

EVIDX = "docs/process_traces/2026-09-03-kernel-batch/02-evidence-index.md"
CODEAUD = "docs/process_traces/2026-09-02-hands-free-week/13-audit-code-tests-opus.md"
WGATE = "docs/process_traces/2026-09-02-hands-free-week/15-watchdog-gate-synthesis.md"

def row(tid, lane, rank, priority, status, goal, auth_path, auth_label,
        acc_summary, acc_evidence, note, deps=None):
    return {
        "acceptance": {
            "evidence": acc_evidence,
            "pointer": {
                "json_pointer": "/tasks/%s/acceptance" % tid,
                "label": "%s acceptance" % tid,
                "path": KP,
            },
            "summary": acc_summary,
        },
        "authority": {"label": auth_label, "path": auth_path},
        "dependencies": deps or [],
        "fallback": None,
        "fences": [],
        "flags": [],
        "goal": goal,
        "id": tid,
        "lane": lane,
        "priority": priority,
        "rank": rank,
        "status": status,
        "status_note": note,
        "stop_card": None,
    }

new = []

new.append(row(
    "LINEAGE-RELOCATABLE-01", "agent", 126, "p3_hardening_candidates", "queued",
    "Design a relocatable launch lineage so an evidence bundle can be authenticated from a clone. Today every hop of the lineage layer resolves by machine-absolute path - the consumption receipt, the launch manifest, the window root and the lifecycle receipts - so re-rooting the pack root alone buys nothing. This is a design lane with its own consult, not a should-fix on any implementation branch.",
    EVIDX,
    "decode-identity file 32, S3 ruled (d): a relocatable lineage is a new ruling and a design lane, and the kernel row goes in the post-merge kernel batch",
    "A ruled design for authenticating a launch lineage from a relocated checkout exists, with the consult that produced it on record.",
    [
     "A consult (three seats per the standing rule) has ruled how each absolute hop is re-rooted or replaced, or has ruled that it is not worth doing",
     "The contract paragraph stating today's limitation at the lineage layer, landed on the decode-identity branch, is cited as the starting statement of the problem",
     "No gate semantics change without its own cold gate: S3 (d) was ruled precisely because nothing is lost mechanically today",
    ],
    "Registered 2026-09-03 in the post-merge kernel batch, as ruling S3 (d) of the decode-identity synthesis directed. The ruling records that clone-reproducibility needs re-rooting across arm_readiness authentication as a whole, and that the gate cannot be reached with a missing pack root in production, so nothing is broken today - the label reached through the direct seam is the honest one. This is one of the four ruled-not-installed rows the 2026-09-02 fresh-Fable docs-vs-truth audit found (its A7).",
))

new.append(row(
    "LINEAGE-RESOLVE-RACE-01", "agent", 127, "p3_hardening_candidates", "queued",
    "Bring the two strict path resolves in the launch-lineage authentication inside the error contract. arm_readiness.py resolves strictly at two sites outside any try block, so a file that vanishes between an earlier strict resolve and these lines raises a raw FileNotFoundError that escapes authenticate_launch_lineage, and the analysis-side reader catches only LaunchLineageError.",
    EVIDX,
    "decode-identity file 46 NIT-1 (cold Fable ruling on packet 45): two strict resolves outside try, raw FileNotFoundError escapes the lineage error type",
    "Every path resolve inside launch-lineage authentication either succeeds or raises the lineage error type, proven by a test that makes the file vanish between the two resolves.",
    [
     "A regression removes the expected file between the first strict resolve and the later one and asserts the lineage error type, not FileNotFoundError",
     "The analysis-side reader refuses with a named reason code on that input rather than propagating an OSError",
     "The counterfactual is recorded: with the wrap removed, the same test fails with the raw exception",
    ],
    "Registered 2026-09-03 from the packet-45 cold gate's residual nits. Cited sites at the time of the ruling: arm_readiness.py:9020 (expected_path.resolve strict) and :10222 (the consumption launch_manifest path resolve), against inputs.py:2778-2782 which catches only LaunchLineageError. Line numbers are as-of the ruling and must be re-derived before work starts. Surfaced by the cold seat's own harness (E2a first attempt, cascade S6 first run); reachable in production only as a race, which is why it was ruled a NIT and not a blocker.",
))

new.append(row(
    "ONE-USE-CONSUMPTION-TEST-01", "agent", 128, "p2_next_slice", "queued",
    "Restore an executable end-to-end test of the one-use consumption write. The only such test is skipped as STRUCTURAL-BLOCKED, so the one-use property that the arm-consumption cure rests on is currently supported by the primitive plus a code-read mapping, not by an executed end-to-end proof.",
    EVIDX,
    "decode-identity file 46 NIT-2 (cold Fable ruling on packet 45): the only end-to-end one-use consumption test is unittest.skip STRUCTURAL-BLOCKED",
    "A running end-to-end test proves that exactly one consumer wins the launch capability and that replay refuses, with the structural blocker either removed or replaced by a test that does not need it.",
    [
     "test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses runs unskipped, or a named successor covers the same two assertions",
     "The reason the original was STRUCTURAL-BLOCKED is stated and shown cured, not worked around by weakening the assertions",
     "The counterfactual is recorded: with the one-use write removed, the test fails",
    ],
    "Registered 2026-09-03 from the packet-45 cold gate's residual nits. Cited site at the time of the ruling: tests/test_arm_readiness_lifecycle.py:751-755; re-derive before work. The nit is explicit that the one-use claim in Cure C(i) rests on the primitive (E1) and a code-read mapping while this test stays skipped, so the row is scoped to restoring the executed proof, not to re-litigating the cure.",
))

new.append(row(
    "RAW-CAPTURE-DIGEST-01", "agent", 129, "p2_next_slice", "queued",
    "Digest the window's raw captures. The bundle writer records a raw_sha256 map in the bundle metadata at close, and the reducer verifies it before parsing, reusing the existing verification block. Migration-safe: verify only when the map is present, so corpora written before the change still reduce.",
    CODEAUD,
    "Code-and-tests audit 2026-09-02, section 5 item 1 (sized 3-4 h): the only primary-evidence class the calibration side guards and the claim side does not",
    "A raw capture that changed on disk after collection cannot be reduced into a result.",
    [
     "RunBundleWriter.close writes a raw_sha256 map into the bundle metadata",
     "The reducer verifies that map before parsing and refuses on mismatch with a named reason code",
     "Defect-shaped regression: flip one byte of a raw powermetrics capture in a fixture bundle and assert the reduction refuses",
     "Bundles without the map still reduce, so existing corpora are not orphaned",
    ],
    "Registered 2026-09-03 from the code-and-tests audit's ranked five. The audit places this first on risk-closed over cost, on the ground that it sits on the exact path the paper's custody argument rests on.",
))

new.append(row(
    "SILENT-REFUSAL-TESTS-01", "agent", 130, "p3_hardening_candidates", "queued",
    "Give the unguarded refusals a counterfactual test each, shaped as remove the refusal and this test fails - never as this string appears in a list. Start with the one refusal the audit's mutation pass proved unguarded, resolve the one row it left unfilled, and decide what to do about the refusals that are guarded only by the most expensive module in the suite.",
    CODEAUD,
    "Code-and-tests audit 2026-09-02, section 5 item 2 and the mutation results in section 2.2 with the counts in section 2.3",
    "Every refusal in the audited sample has a test that fails when the refusal is deleted, and the audit's own count discrepancy is reconciled on the record.",
    [
     "M6 readiness_pack_not_committed gains a counterfactual regression: deleted refusal, red suite",
     "M8 launch_binding_mismatch is re-run to a verdict - the audit left its mutant and verdict cells unfilled",
     "The four refusals covered only by an expensive module (config_hash_mismatch and whole_window_verdict_conflict by the analysis-integration module, the ledger rollback taxonomy by the calibration-exits module, the anchor fallback by the reduce module) either gain a cheap guard or are recorded as an accepted process cost",
     "The section 5 item 2 count of six is reconciled against section 2.2 and section 2.3 in writing before the work is called done",
    ],
    "Registered 2026-09-03. RECORDED DISCREPANCY IN THE SOURCE: section 5 item 2 says six silent refusals in the section 2.2 SILENT rows, but section 2.2 carries ONE row verdicted SILENT (M6), three marked narrow set silent that each flipped to COVERED on a wider module set (M4, M9, M13), and one row never filled in (M8). Section 2.3 states it plainly - nine of the ten sampled refusals have a real counterfactual test, and one sampled refusal is unguarded (M6) - and separately names four refusals that are silent only against the module a developer would reach for first, which is a coverage-cost finding rather than an absence of coverage. This row is scoped to what sections 2.2 and 2.3 support; the six is carried as an open reconciliation, not as a work item count. See docs/process_traces/2026-09-03-kernel-batch/02-evidence-index.md source D.",
))

new.append(row(
    "CANONICAL-JSON-ONE-HOME-01", "agent", 131, "p3_hardening_candidates", "queued",
    "Give canonical_json_bytes one home. Move it to a single module, re-export from the current sites so no caller changes, and assert in a test that the three names resolve to the same object.",
    CODEAUD,
    "Code-and-tests audit 2026-09-02, section 5 item 3 (sized 30 min): a class of digest-mismatch bug that would be very hard to read backwards from its symptom",
    "There is exactly one canonical JSON serializer, and a test fails if the copies ever diverge again.",
    [
     "One module owns the implementation; the other sites re-export it",
     "A test asserts the three names resolve to the same object",
     "No digest value anywhere in the repo changes as a result - the move is byte-neutral and shown to be",
    ],
    "Registered 2026-09-03 from the code-and-tests audit's ranked five (its section 3.3 is the finding, section 5 item 3 the prescription). The audit names joulewise/authentication_io.py as the natural home; that is a suggestion, not a ruling.",
))

new.append(row(
    "INSTRUMENT-PATH-PIN-01", "agent", 132, "p2_next_slice", "queued",
    "Record which instrument binary actually ran, and pin its digest. Replace the hardcoded powermetrics path literal in the fiducial with the resolved sampler binary, add an expected powermetrics digest to the campaign policy, and compare it both at calibration and at window prepare.",
    CODEAUD,
    "Code-and-tests audit 2026-09-02, section 5 item 4 (sized 2-3 h): converts the paper's instrument identity from a declared label into a measured fact",
    "The paper can name the exact instrument binary that produced its numbers, and a substituted or updated binary is caught rather than assumed.",
    [
     "The fiducial records the resolved sampler binary path, not the hardcoded literal",
     "An expected instrument digest lives in the campaign policy and is compared at calibration and at window prepare",
     "The refresh path across OS updates is written down: who re-pins, on what evidence, and what a mismatch does to an in-flight window",
     "Landed together with the model-side identity cure it is the twin of, per the audit",
    ],
    "Registered 2026-09-03 from the code-and-tests audit's ranked five. Cited site at the time of the audit: the /usr/bin/powermetrics literal at powermetrics_fiducial.py:1502; re-derive before work. The audit says most of the cost is deciding where the pin lives and how it is refreshed, not the code - so the design question is the work.",
))

new.append(row(
    "GENERATOR-CORE-01", "agent", 133, "p3_hardening_candidates", "queued",
    "Extract the campaign generators' common core. Roughly 1500 lines are byte-identical across every generation of generator; move them to one shared module (the write-boundary validator first, which exists in nine copies) and leave each generator as its pins plus its genuine diffs.",
    CODEAUD,
    "Code-and-tests audit 2026-09-02, section 5 item 5 (sized 1-2 days): a prerequisite worth paying BEFORE the next floor generators are written, not after",
    "A new campaign generator is written as its pins and its diffs, not as a hand-copy of a few thousand lines.",
    [
     "One shared module holds the byte-identical core, starting with validate_generation_write_boundary",
     "Every existing generator still produces byte-identical output after the extraction - shown, not asserted",
     "The next floor producer is written against the shared core",
    ],
    "Registered 2026-09-03 from the code-and-tests audit's ranked five. The audit's argument for sequence: the unowned floor-producer finding from the companion audit becomes a small task instead of a risky one only if this lands first, because under the current design owning it means hand-copying about 2900 lines twice. Ordered last of the five on cost, but it gates the cheapness of the others.",
))

new.append(row(
    "WATCHDOG-INSTALL-01", "agent", 134, "p1_phase_gate", "partial",
    "Build and install the relaunch watchdog: a user-level launchd supervisor that owns the stand-down deadline and the force path, spawns each magistrate activation as a single-turn headless session, verifies the agent census before a window span, walks the process tree to terminate descendants rather than trusting the process group, honours a remote stop branch and a local stop file, and emails Ed at each launch and stand-down.",
    WGATE,
    "Watchdog cold gate synthesis 2026-09-03 (cold Fable file 14 and Opus refuter file 12, no blockers): eleven adopted rulings with the seat that decided each",
    "The watchdog is installed and Ed has been emailed the install notice, with every one of the eleven adopted rulings realized in the code that was installed.",
    [
     "Timings as ruled: cooperative request at t0 minus 25 min, SIGTERM at t0 minus 16, SIGKILL at t0 minus 15, then a census verification, enforced at 10 s or finer resolution",
     "Census scope as ruled: the exact production agent_census imported from the night gate, empty inside a plan span, with the span extended while the chain has started and not exited",
     "Kill primitive as ruled: walk the process tree from the recorded session pid until stable and terminate every descendant; unowned census hits are reported as holds and never killed",
     "Kill switch as ruled: the remote stop branch checked with a positive control on main so a network failure never reads as cleared, a glob so a typo is not silent, plus the local stop file",
     "The install notice is emailed, then the install proceeds without waiting for a reply, per the delegation",
    ],
    "In progress 2026-09-03 on local branch feat/2026-09-03-magistrate-watchdog (worktree /Users/edr/code/JouleWise-wt-watchdog-build, at 46eaf18c; NOT pushed to origin as of this batch). Design consult files 02-04 and 09-10, cold gate packet 11 with exhibits 11a and 11b, Opus refutation 12, cold Fable ruling 14, synthesis 15, build brief 16, all under docs/process_traces/2026-09-02-hands-free-week/. Authorized by D-171 item 4. The first stand-down after install kills the magistrate's own session tree including the Terminal-hosted interactive twin, which the synthesis records as the only reason the census can never be empty today. Arming nights is explicitly OUTSIDE this row's charter (synthesis row 11).",
))

new.append(row(
    "NIGHT-PLAN-PIN-01", "agent", 135, "p1_phase_gate", "partial",
    "Pin night plans to the measurement checkout and install the night agents from it, so an ordinary daytime pull of the canonical checkout can no longer move HEAD past a pinned repo_head and make the gate refuse a plan as stale.",
    WGATE,
    "Watchdog cold gate synthesis 2026-09-03 row 7 (Fable Q6 split): the plan-pin change MUST land before the first REAL window is armed, may follow the watchdog install for rehearsal stubs, and needs a re-arm after any HEAD move",
    "Night plans are pinned to the measurement checkout and the agents are installed from it, so a canonical-checkout pull cannot stale a pinned plan.",
    [
     "Plans pin the measurement checkout of record, not the canonical checkout",
     "The night agent installer renders its plists from the measurement checkout",
     "A canonical-checkout pull during the day leaves an armed plan armable - shown by re-running the gate's staleness check after a pull",
     "Landed before any REAL window is armed; rehearsal stubs may run before it",
    ],
    "In progress 2026-09-03 on branch feat/2026-09-03-night-plan-pin, PUSHED to origin at 12ec41d2: night plan v2 pins the measurement checkout (measurement_root and measurement_head), the R-6 stale check keys on the measurement HEAD so dev-tree HEAD movement is informational only, the installer checks both pins at install and neither at uninstall, and v1 plans retire fail-closed (Sol xhigh, lead replay 104 OK, two mutation probes kill). Forced by the 2026-09-02 evening re-arm: a fresh audit caught that daytime pulls had moved canonical HEAD past the pinned repo_head, so the gate would have refused night_plan_stale, and the rehearsal-20260903 plan had to be re-pinned and its plists re-rendered at 33290b8b. The run_night.py interlock from the Sol watchdog design was deferred here by the synthesis, because this lane already edits the driver.",
))

new.append(row(
    "R7F-EXIT3-SEMANTICS-01", "agent", 136, "p3_hardening_candidates", "queued",
    "Settle the exit-3 semantics the r7f-unavailable cold gate left as a follow-up, and record the answer where the driver and its readers can both see it.",
    "docs/process_traces/2026-09-02-coldgate-r7f-unavailable/MAGISTRATE-RULING-r7f-unavailable.md",
    "Cold gate r7f-unavailable 2026-09-02: the ruling registers this as a follow-up kernel row",
    "The exit-3 semantics are written down as ruled, and the code and its documentation agree.",
    [
     "The ruled semantics are stated in one place that the driver and its readers share",
     "A regression fails if the exit code and the recorded disposition disagree",
    ],
    "Registered 2026-09-03. This row was promised by the r7f-unavailable ruling (its follow-up paragraph) and by the dx-registry magistrate notes, and never created - the batch that was to carry it never ran after #272 merged. It is one of the four ruled-not-installed instances the 2026-09-02 fresh-Fable docs-vs-truth audit counted (its A7), which is the same failure pattern T26-RULING-INSTALL-01 was created to cure. Scope the exact question from the ruling text before starting; this row records the debt, it does not restate the ruling.",
))

new.append(row(
    "PREWINDOW-V5-PIN-01", "agent", 137, "p1_phase_gate", "queued",
    "Retarget the prewindow check's window pin from the retired campaign family to the live one. The script still pins its runs-root prefix to the _v2 campaign packs, so it is checking the wrong family for every window the live campaign will run.",
    "docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md",
    "Unattended stage-1 ruling R-12: the prewindow check's window pin gets a separate small pull request that retargets it",
    "The prewindow check pins the live campaign family, and a window of that family passes it while a stale-family root is refused.",
    [
     "The runs-root prefix pin names the live family, not _v2",
     "A regression covers both directions: a live-family root passes, a stale-family root refuses",
     "The change is a retarget only - no new admission lane and no gate-semantics change",
    ],
    "Registered 2026-09-03. Ruled by R-12 of the unattended stage-1 ruling and never given an owner; PREWINDOW-REGEX-01 covers only the regex, not the family pin. Verified still true at this head: scripts/prewindow_check.sh:51 reads that the governed family is the _v2 campaign packs. One of the four ruled-not-installed instances in the 2026-09-02 fresh-Fable docs-vs-truth audit (its A7). Registered as a separate row rather than folded into PREWINDOW-REGEX-01 so the two debts stay separately visible.",
))

new.append(row(
    "CHARTER-V3-PACKET-INPUTS-01", "agent", 138, "p3_hardening_candidates", "queued",
    "Own the charter v3 revision that D-170 item 4 deferred: the packet-input-list amendment requiring an execution record or a code-path proof as a listed packet input. It needs a charter digest and Ed's re-ratification, which is why it was deferred rather than dropped.",
    "docs/decision_log.md",
    "D-170 item 4 and its Where recorded and discharged paragraph: the packet-input-list amendment is deferred to charter v3 because it requires a charter digest and Ed re-ratification",
    "Charter v3 carries the packet-input-list amendment, digested and re-ratified by Ed, and the executed-evidence duty has a tracked template home.",
    [
     "The amended packet-input-list clause is drafted against the current charter text",
     "The charter digest is computed and recorded, and Ed has re-ratified the amended charter",
     "The consult-brief Executed requirement gains a tracked home in this repository instead of living only in the magistrate scratchpad template",
    ],
    "Registered 2026-09-03. The deferral is stated in D-170's own body and had no owner row, which is what the 2026-09-02 fresh-Fable docs-vs-truth audit found (its A7, fourth of four). Ed re-ratification puts the closing step in the ed_external lane even though the drafting is agent work; the row stays in the agent lane and the Ed step is called out in acceptance rather than split into a second row.",
))

for r in new:
    assert r["id"] not in T, r["id"]
    T[r["id"]] = r

# rank uniqueness check per lane
seen = collections.defaultdict(set)
for i, v in T.items():
    assert v["rank"] not in seen[v["lane"]], (i, v["lane"], v["rank"])
    seen[v["lane"]].add(v["rank"])

json.dump(k, open(KP, "w"), indent=2, sort_keys=True, ensure_ascii=False)
open(KP, "a").write("\n")
print("added", len(new), "rows; total", len(T))
