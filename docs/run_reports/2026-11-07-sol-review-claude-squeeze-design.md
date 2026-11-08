# Sol cross-review of Claude's squeeze design — 2026-11-07

**DRAFT desk review; lead adjudication owed. Nothing registered, scheduled, armed, pushed or measured.**

## Assignment and workspace

Review `a832f4993:docs/align/squeeze/squeeze-design.md`, independently judge its claims and actions, write `docs/align/squeeze/sol/review-of-claude-squeeze-design.md`, and commit locally on `align/2026-11-07-sol-review-claude-squeeze-design`.

That branch was already checked out at `a832f4993c4f35f333634884b5905768078b8085` with a clean worktree. I preserved the original product and all code/configuration. The only additions are the requested review and this run report.

M0: read AGENTS/CLAUDE, the generated stop-card and workspace intake, queue/do-not-do sections, playbook M0, orchestration, source-of-truth map and targeted D-139 authority. No active stop card/global gate was found. The explicit user task selects this research desk work. The task's standing prohibitions override repository defaults to register tasks, update coordination state or run the full suite. `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and `tests/test_gen_state.py` are untouched.

No network was used: the no-network rule takes precedence over “git fetch origin first.” All required local refs existed. Git object reads from the allowed shared store were used only through Git. No external user path, real restricted directory, measurement bundle, model cache or sealed outcome was opened. No Block-5 analysis, native measurement, model load/download, MLX import or background-process inspection was performed.

## Result and evidence

Verdict: **DISAGREE with adoption as written; AGREE with the corrected core design direction.** The review individually dispositions all 16 synthesis actions and provides ledgers for synthesis claims, repeated appendix claims, additional seat-specific claims and primary-source verification limits. Its alias table expands every compact citation to a named commit and repository path:line.

Main findings:

1. W1 already attempts to launch KM003C through `align_v4_session → align_pilot_session → bytes_h_session → b5.plan → run_night → b5.driver.production_seams`. A narrow ALIGN-code grep missed this inherited route. Capture still needs confirmation; adding another reader is the wrong default fix.
2. The rank-max/union-bound arithmetic is correct only under the relevant frozen-score exchangeability assumptions. LOTO calibration versus full-fit scoring, shared windows, U4 and interleaving do not establish those assumptions.
3. The composition's exact same-episode algebra has coefficient 1 on the full-to-visible prediction difference, not an additional κ. Off-Mac imputation is a conditional model, not exact measured flags.
4. SQ1's quoted power omits its 90% lower-bound ≥.5 requirement. With six eligible attacks it needs 6/6 catches: power .015625 at p=.5, .117649 at p=.7. With eight it needs ≥7/8: .035156/.255298.
5. SQ2 needs explicit visible and monitor-only comparators, allocation, selected-strategy inference and transport uncertainty. SQ4's nonrejection does not prove equivalence.
6. Physical site/dose mapping, DC fitting and uncertainty, precise token accounting, sham/RNG identity, attack-induced exclusions, metadata blinding, out-of-span work, extensions and inconclusive outcomes need completion.

All empirical pilot numbers are checked only against the explicitly requested public audit text. I did not independently recompute them. External-paper-specific claims are marked UNVERIFIABLE at the primary-source level under the no-network constraint; corroborating repository attribution is identified separately.

The review also inspected later analysis/kit review documents at `64fdc5189` and `96dd7e78c`, after forming its core findings. Their reported tests/fixes are attributed, not claimed as rerun or independently verified by this session.

## Verification

This is Markdown-only work. No unittest, compileall, canonical/quick suite or full suite was run. The required checks were bounded static source tracing, citation checks and synthetic arithmetic; no repository Python runtime was imported. All computations used `python3.13 -I -B -` with standard-library code only, one process at a time.

| Check / command | Result | Number-bearing catch or limit |
|---|---|---|
| `git status --short --branch`, `git branch --show-current`, `git rev-parse HEAD` | Correct assigned branch, clean at intake | Preserved unrelated work; none was present. |
| `git show <pin>:<path>` / scoped `git grep` | Read named protocol, residual API, chair, authority, audits and targeted implementation | Shared W1 meter path contradicts the product's missing-launch claim. No real paths in source were followed. |
| Isolated stdlib citation/source validator | 28 aliases, all referenced spans within their pinned files; all 16 actions represented; code fences balanced | Also passed 8 source assertions for the W1 meter call chain and 2 for the same route at the reviewed integrated base. Structural citation validation does not itself prove semantic support. |
| Isolated exact binomial/interval arithmetic | Values below | Corrected full SQ1 power and qualified yield/precision. No measurement inputs. |
| Final document/citation check and `git diff --check` | Recorded at local close below | Documentation consistency and whitespace only; no hardware or registration admission. |

Recomputed planning values:

| Quantity | Result |
|---|---|
| P(Bin(40,.5)≥27), P(Bin(40,.8)≥27) | .0192386541, .9805926311 |
| SQ1 test-only power at n=6, p=.5/.7, threshold ≥2 | .890625 / .989065 |
| SQ1 full criterion at n=6, threshold 6/6 | .015625 / .117649 |
| SQ1 full criterion at n=8, threshold ≥7/8 | .03515625 / .25529833 |
| One-sided 90% CP lower bound at 5/6 | .4896836934 |
| Iid maximum's realized-tail 90% upper at m=39 | .0573315449 per channel |
| P(≥8 realized) at (n,p)=(21,.5),(37,.3),(57,.2) | .9053764, .9052828, .9066123; does not size monitor-missed attacks |
| P(≥39 of 42) at independent exclusion .05/.07/.10 | .8431074 / .6612685 / .3836460 per pair, before whole-window failures |
| SE(κ), 40 J/(512×3.6), 2.97 J/(256×.619) | .02170139, .01874243; conditional planning assumptions |
| Difference of two independent n=200, p=.1 arms, normal 90% half-width | .04934561, before maxima/transport/clustering |
| Two-sided 90% exact CP at 22/24; upper at 0/24 | [.76019898,.98498822]; .11734616 |
| Six D + three T windows +12.4 h; plus D7/T4 | 161.2 h; 194.2667 h after W1 |

The review includes runnable stdlib code for the decisive SQ1 calculation. Additional numbers use `sum(comb(n,j)*p**j*(1-p)**(n-j) for j in range(k,n+1))`; CP limits are monotone bisections of the corresponding binomial tails. One intermediate verification probe used the wrong complement index for the 22/24 upper endpoint; the check was corrected and rerun before delivery. The committed number above is the corrected one.

## Native checks still owed by the lead

After integrating the reviewed kit with the ALIGN lane, outside this sandbox, run `python3.13 -B -m unittest tests.align.test_squeeze_native` at the integrated equivalent of `96dd7e78c:tests/align/test_squeeze_native.py:20–82`. It contains two tiny synthetic MLX checks, without model downloads. They cover exact-k fresh-cache generation and lazy cache/auxiliary fencing; they are not evidence of physical detection.

Then use the owning live gates for actual cache/RNG identity, meter sample support and clock mapping, battery assist, the new DC endpoint, site/dose execution, gate/deadman containment and physical replay comparisons. This session did not perform or authorize those measurements. The user reports no usable Metal device or MLX CPU fallback in the sandbox; no native execution was attempted.

## Process and handoff

No subagents, external consults, installed skills or new integrations were used. This root review is the requested independent seat, not the lead's final gate. No coordination state was edited and no kernel task was registered. There are no ephemeral evidence dependencies: the numerical method, results, source pins, findings and limitations are committed in the two documents.

The next exact action is for the lead to disposition review F1–F9 and reconcile a defensible addendum, estimator, power plan and physical manifest before implementing or arming it. Open questions are scientific rulings/verification needs in that report, not a request for this reviewer to choose them. In particular, the report does not select a monitor, change the threat model, allocate Mac time or assert that a limits result is publishable.

Local close: both added documents passed the final pinned-citation/action/fence validation and `git diff --check`. The local commit is the commit containing this run report; no push was made. Resolve its exact identifier with `git log -1 --format=%H` on the named review branch.
