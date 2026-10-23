# BY-MERGE-REVIEW — BLOCKED, execution not performed

Date: 2026-10-23 UTC. TAG: BY-MERGE-REVIEW.

**This is an incomplete executing review, not a pass or merge recommendation.** The managed environment failed before a shell became available. No production function, synthetic campaign, refusal replay, test, or arithmetic mutant was executed. There are no confirmed arithmetic findings and no measured mutation survivors; those statements do not establish that the code is correct.

## Source and delivery

- Repository: `mpmdw/JouleWise`.
- Requested lane: `lane/2026-10-22-bytes-pass1`.
- Independently read remote lane head: `1c458d71d8a048e24b6c3a6b402fe3c34d9f57c3`, matching the requested integration head.
- Delivery branch: `report/2026-10-22-by-merge-review`, based on that exact commit.
- Only this report is added. No production code, tests, configurations, registration, RUN_STATE, or TASK_QUEUE is changed.
- Delivery uses the connected GitHub branch/file tools because local Git cannot start. This is a remote report commit, not a claim that the requested local fetch/checkout/push commands ran. No PR is opened, no other branch is updated, and no force update is used.

## What I did

Read repository instructions and targeted intake remotely: AGENTS.md, the RUN_STATE generated intake (no active stop card), Mission M0, orchestration, the BYTES registration, and the later H-DISK ruling. The exhaustive write scope overrides repository bookkeeping instructions.

Used three independent workers, as requested, for (1) analysis/battery/twin arithmetic and mutations, (2) C5 disk/b6/loop behavior, and (3) manifest/C4/H-session/Mac-kit/stream preprocessing. They inspected source, focused tests, and governing texts remotely. All returned explicitly blocked handoffs. No worker made repository writes or claimed execution.

Waited for the selected managed environment to start and rechecked shell availability and environment status. Startup eventually failed during container creation. The first recorded clock check was 05:02:04 UTC; after the failure, the status check at 05:12:31 UTC reported `observed_phase=failed`, `connectivity=offline`, `observations_current=true`, and `failure.code=environment_startup_failed`. Waiting began before that first clock check; its total duration is not asserted.

## Commands attempted and exact tails

The following shell requests were rejected before a process could start:

```sh
pwd && test -d /workspace/JouleWise && git -C /workspace/JouleWise status --short --branch && cat /etc/codex/network-policy.json
```

Exact tool tail:

```text
No usable execution environment is available. Wait for an environment to become available before using this tool.
```

Repeated `pwd` shell requests received the same tail. Neither `/etc/codex/network-policy.json` nor the local working tree could be inspected.

The environment wait ended with this exact tail:

```text
Environment `ccarenv_b64_Y2NhcmVudl83MzI5NTJmNDU3ZWM4MTkxYmZjMDBmYzdjZTYwOTBjNw` failed to start: exec-server connection attempt failed: environment unavailable: Environment provisioning failed during container_creation. Cause: snapshot_materialization_failed. Reason: gateway_unavailable.
```

The final environment-status failure payload was:

```json
{"code":"environment_startup_failed","message":"Environment startup failed. Check the configuration, retry, or contact support."}
```

**Not run:** seat_setup, local fetch/checkout, any Python or test process, production-shaped campaigns, CLI stage chain, refusal replays, mutants, local commits, or local pushes. No test process existed to which JW_B5_SYNTHETIC_ONLY or TMPDIR could be applied.

The source-head read was:

```text
github.fetch https://api.github.com/repos/mpmdw/JouleWise/git/ref/heads/lane/2026-10-22-bytes-pass1
object.sha = 1c458d71d8a048e24b6c3a6b402fe3c34d9f57c3
```

The requested report branch did not exist when checked remotely (GitHub 404). It is created only for this report from the source head above.

## Ranked findings

**Not available: execution is blocked.** No code finding is promoted to blocker/high/medium/low without its required reproduction. The environment failure is a task blocker, not a finding about JouleWise.

The user-reported defects-campaign disagreement (387 fields; twin battery term pending PR #574) remains a known baseline supplied in the brief. It was not independently reproduced here and is not presented as a new finding.

## Static observations and candidates to execute

These are handoff leads, not executed findings. Suggested fixes are conditional on reproduction and adjudication.

| Location at source head | Observation or candidate | Execution needed | Smallest conditional fix |
|---|---|---|---|
| `docs/registrations/bytes_pack_v1.md:12` | The cited `docs/process_traces/2026-10-22-forward/BAT-RULING.md` returns 404 at the lane head and at main. The lane directory listing contains only BY-G-MANIFEST-REDERIVATION.md. This is a confirmed remote provenance observation, not an arithmetic result. | Verify local absence and locate the authoritative ruling; do not infer its unpublished contents. | Lead restores the exact adopted ruling or corrects its reference. This report seat has no write scope for either. |
| `scripts/bytes_gates.py:211` and `:222` | Spread calculation appears to call max on an empty set after an early stop with fewer than two successful check/soak observations. | Execute native H export and C5 with that early stop; check unavailable diagnostics and CLI exit. | If reproduced, preserve measured rows and make dependent sizing explicitly unavailable when no spread exists. |
| `scripts/bytes_gates.py:321` | Some missing raw-byte receipts may still allow P to be calculated from the remaining receipts. Existing remote-read test covers all receipts missing. | Remove one eligible receipt's raw_allocated_bytes; run exporter, C5, and the native disk consumer. | If sizing is unsupported, make it unavailable until required observations are complete; retain disclosure rather than invent a rate. |
| `scripts/bytes_twin.py:353`; `tests/test_bytes_agreement.py:186` | The comparer uses an absolute 1e-6 floor as well as relative tolerance. Its comments at 1106–1111 acknowledge resident-rho sensitivities around 1e-7 below that floor. Zeroing that sensitivity is a candidate surviving numeric mutant. | Apply the arithmetic mutant in a scratch copy, rerun the focused comparison, and demonstrate a changed output number and an unchanged test verdict. | Use the governing precision/half-width rule or the brief's 1e-6 relative fallback, with derivation. Do not change a bar merely to kill a mutant. |

Remote provenance reproduction used `github.fetch_file(repository_full_name="mpmdw/JouleWise", ref="1c458d71d8a048e24b6c3a6b402fe3c34d9f57c3", path="docs/process_traces/2026-10-22-forward/BAT-RULING.md")`; its exact result began `GitHub API error 404: {"message":"Not Found"`. A second read with `ref="main"` returned the same error.

No claimed surviving mutant exists in this report: none was applied. The sensitivity row is only a candidate.

## No-silly-numbers dimension

**Execution audit incomplete.** No agreement bar, physics threshold, or numeric output was experimentally validated, and no tolerance was changed.

For recovery, the registration supplies the approximately 1 J per-run attribution scale, the smallest printed energy half-width of 0.013 J, the 1% half-width agreement rule, fixed printed precisions, and exact equality for counts/labels/hashes. The brief's no-half-width fallback is 1e-6 relative. The absolute-floor comparison candidate above needs execution and assessment against those authorities.

H-DISK fixes c=2 physical copies, WAIT from the registered 7,200 s wait, and committed fixed bytes. Those are governing inputs, not tolerances selected by this review. Older 150 GiB reserve prose must not be substituted into the later ruled formula.

## Decisions I made

1. Failed environment provisioning is not scientific evidence. Read-only inspection does not satisfy RUN, refusal replay, mutation testing, or production-shaped end-to-end coverage.
2. Keep known #574 disagreement separate from any new finding; do not infer its exact present result from the brief.
3. Apply the later `docs/process_traces/2026-10-21-magistrate-283e9802/H-DISK-RULING.md` for P: `2*(B+WAIT)+fixed`, without the older reserve. Its addendum supplies the exact native-budget encoding.
4. The embedded registration battery clauses settle the intended same-span cable plus signed battery term, own-idle subtraction, forward edge terms, and delayed decode-assisted scope. The missing linked ruling is a provenance gap; it does not license inventing arithmetic.
5. Preserve report-only scope. Do not repair production files, the missing ruling, or repository bookkeeping.
6. Use the already connected GitHub tools to preserve this blocked report on the authorized branch. No new plugin, PR, or other branch is needed.

No NEEDS_RULING is raised: no unresolved scientific choice was made that changes counted data or a printed number.

## Required recovery and remaining work

A fresh, usable execution environment is required. Resume this task at the pinned integration source, preserve this blocked report, and execute the review before issuing a code verdict.

- Start with `bash tools/cloud/seat_setup.sh` if it exists on the base branch; inspect local AGENTS, status, intake, and applicable rulings.
- Give independent writers isolated scratch trees inside the allowed report scope. Give every test process `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`, and a distinct existing TMPDIR. Restrict test runs to the focused scratch modules touched for the review.
- Run production-shaped full-size synthetic archives through the real reducer, harvest export, blinded stage, key release, committed fit predictions, and held-out stage. Exercise the seven existing agreement campaigns, including unequal pass durations, signed clock latency, defects, minimum counts, edge-locked meter, and missing withheld files/uncollected passes.
- Replay every refusal clause across analysis/twin, manifests/C4, H export/C5/native disk gate, and loop prepare. Verify the prepare hold until sizing rows carry registered P and exact equality between P and its native budget encoding.
- Independently exercise same-span battery energy, charging sign, forward edge terms, maximum SMC poll-gap tau, battery column, delayed publication, and decode-only without-assisted scope.
- Apply arithmetic mutants in scratch copies, run discriminating focused tests, restore, and retain exact kill/survive evidence. Explicitly list every survivor demonstrated to alter a printed number.
- Audit no-silly-numbers separately. Rank only reproduced findings, with source file:line, exact command/tail, governing clause, and smallest fix.
- Replace this incomplete report with the executed results, commit small green steps, and push only `report/2026-10-22-by-merge-review`. Never open a PR or update another branch.

Until that recovery runs, the requested executing review remains **BLOCKED / INCOMPLETE**.
