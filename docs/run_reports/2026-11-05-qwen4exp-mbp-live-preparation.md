# Saturday Mac validation preparation — 2026-11-05

Task authority: Ed's Saturday 2026-11-07 brief for GOAL 6/7/8/11. Workspace
started clean, detached at `65763077a` (PR #675 canonical lane). Created
`lane/2026-11-07-qwen4exp-mbp-live`; local commits only, no push.
Implementation commits: `922ba22fa` (reuse PR #671) and `b6d15b6b2`
(Saturday tooling/docs/tests). This report and answer.md are a final docs-only
handoff commit.

Mission M0 intake: read repo AGENTS/CLAUDE conventions, targeted restart
sections (ACTIVE_STOP_CARD NONE), queue/do-not-do-yet, plan map, playbook M0,
orchestration, and relevant decision log. The explicit task selects this
bounded agent lane. Per the brief, RUN_STATE.md, TASK_QUEUE.md, state kernel
and tests/test_gen_state.py were preserved, with no task registration.

No network, real measurement data, real weights, MLX imports/execution or
analysis pipeline. Git reads of branch objects used the authorized shared
object store through Git. No other outside-/Users/edr paths were followed.
The long analysis job was not inspected, stopped or affected intentionally.

Implementation: restored PR #671's nine e2e/tool-template/item/hosted-reference
files from the local origin ref. Added maxfit/maxfit5 provisional screening
labels. Added the Saturday runbook, results/status-log templates, unified
validation/logistics CLI, separately hosted bf16 same-item benchmark client,
report renderer and tiny fixture/native tests. Canonical model and converter
are unchanged; the wrapper calls the existing converter and verified loader.
PR #680 streamed gold remains separate and does not close the Saturday gates.
Full file/command handoff: [answer.md](../../answer.md).

Validation (one targeted unittest module at a time, far below 20 minutes):

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.test_qwen4exp_mbp_live` | 26 tests OK, 3 native skips |
| `python3.13 -B -m unittest tests.test_qwen4exp_e2e_eval` | 37 tests OK, 21 dependency/optional skips |
| `python3.13 -B -m unittest tests.test_qwen4exp_hosted_reference` | 13 tests OK, 8 dependency skips; no socket use |
| `python3.13 -B -m compileall -q joulewise tests scripts/qwen4exp_mbp_live.py scripts/qwen4exp_bf16_benchmark.py scripts/qwen4exp_mbp_report.py scripts/qwen4exp_e2e_eval.py scripts/qwen4exp_hosted_reference.py scripts/qwen4exp_e2e_build_items.py` | PASS |
| `ast.parse(..., feature_version=(3,11))` on four new Python files | PASS; syntax only |
| 15 runbook shell blocks through `zsh -f -n` | exit 0; sandbox nice(5) warning |
| `git diff --check` | PASS |

No full suite: expressly prohibited by the brief's machine-load rule. No
live or quiet-machine validation occurred; all hardware outcomes stay OPEN.
Missing jinja2/transformers/MLX means reused template/model paths are not
validated by the default interpreter here. Native validation venv must use
the exact three pins and resolve the native test skips before real weights.

Independent review evidence (light tooling tier, no contract/science change):
read-only child `/root/review_live_scripts` reviewed the code and delta/docs;
no delegated writes, no final verification or authority ruling. Its initial
review identified four issues: (1) paging disk counters included model load,
(2) external disk identity not bound to the APFS volume, (3) reference report
comparability unchecked, (4) duplicate full artifact hashing. Lead fixed
all four and added fixtures. Its delta confirmed the fixes and identified
one defensive gap (generation settings); lead added full RunConfig matching
and a thinking-mode mismatch fixture. The requested canonical native timing
smoke was added, gated on native dependencies. Parent owns final diff/checks.
The final read-only delta found no remaining concrete defect; the review's
own earlier tiny fixture runs were also green. This small review is recorded
here as the D-050 process trace, with child identity, scope, findings,
dispositions and downstream implementation commit above. No Fable/network consult
was possible under the no-network rule; no merge/review-gate completion claimed.

Known limitations: mmap has no hard OS cache quota, so the run uses measured
residency/abort checks. The 10% comparison is Metal allocation proxy until
lead accounting review. Physical APFS plist/API assumptions require native
exercise. PLE disk bytes are whole-device upper bounds, first cache state
unknown. Hosted bf16 needs independently checked server metadata; no host
is supplied. Quantization screens/P5 targets remain provisional or recipe
specific. Standalone converter has no dry-run/resume; wrapper provides dry
planning and preserves interrupted artifacts. All native/reused reports
are validation evidence, never study/energy data.

Next: lead reviews local commits; operator prepares the Mac venv and starts
[mbp_live.md](../align/qwen4_exp_port/mbp_live.md) step 0 outside any agent or
measurement session. Run native tiny tests before downloading/loading.
