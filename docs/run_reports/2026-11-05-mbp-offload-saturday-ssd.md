# Measurement-MBP offload: Saturday day-only SSD revision

Task: address the reproduced B1/H1–H7/M1–M9/L1–L12 review, incorporating Ed's
November 5 fact that a borrowed WD_Black SN7100 2 TB in an OWC Express 1M2
will be attached November 7 by day only. Authoring, implementation and final
verification were performed by this session; no subagent/consult was used.

Implementation commit: `e18c89c64`, on the requested
`lane/2026-11-05-mbp-offload-runbook`. The checkout initially was clean and
detached at cached origin/lane's `1a38da9d2`; created the matching local branch
there. New commits only; no history rewriting, push, merge or deployment.

The full per-finding disposition, verification table, remaining gates and
Saturday command sequence live in [answer.md](../../answer.md). The maintained
procedure is [the runbook](../align/mbp_offload_and_gold_setup.md).

The supplied branch already contained multiple fix rounds. This revision
retains the safe KEEP/census/path/flags/ACL/disk-guard/HF-resume mechanisms,
orders actual SSD verification before cloud upload, adds bound native cloud
transition proof and final SSD byte re-verification, closes the public-only
deletion escape, includes pilot10, and changes energy admission to require
eject/physical unplug. The standalone external-volume census is read-only,
requires diskutil AND mount observations, refuses unknowns/tool failure and
even attached-unmounted media, and emits redacted facts. The final deletion
program detects Python-launched writers and rechecks magistrate lock/launchers.
Gold runner cleanup cannot bypass the new deletion policy. The handoff commit
also permits unique reviewed retry-ID suffixes in the persistent operation.

No retention policy was invented: all three pilots remain retained and
deletion refuses. No native upload grammar was invented: the unpinned parser
refuses. The day-only SSD conflicts with an R0 gate that probes external copy
destinations during a measurement; the runbook stops for the R0 lead rather
than allowing an attached-enclosure window or claiming a stale receipt passes.
The supplemental internal budget enforces at least 80 GB plus remaining
journal AND any larger reviewed amendment requirement. Current historical
~66 GB available with no pilot reclaim does not meet that gate.

Final verification: 91 tests across eight focused unittest modules, all pass;
module counts and exact commands are in answer.md. Compilation passed for
joulewise, tests and both changed scripts, using a pycache prefix under
`/private/tmp/jwsol/offload-fix/tmp`. Runbook tests parse every shell fence and
inline Python heredoc without executing any documented operational command.
Native uchg and isolated process-group tests use synthetic temporary files
and processes. No native storage/cloud/MLX or real data validation is claimed.
`git diff --check` passes; protected coordination paths have no diff against
the initial head. The full suite was forbidden and was not run.

Test-scheduling deviation: an initial model-KEEP run returned a running
session after its one-second yield; a short R0-patch module (0.086 s) was
started before polling it to completion (model-KEEP total 2.489 s). This
briefly violated the requested one-module-at-a-time scheduling. Subsequent
verification re-ran those modules serially with ten-second yields (4.222 s
and 0.186 s respectively), and all final runs completed before the next
module. Total targeted execution, including iterations, was far below the
20-minute limit. An initial external-census fixture accidentally overrode
unittest.TestCase.run; renamed its injected tool-response method and all
seven tests pass. These were test-workflow/fixture corrections, not live
hardware failures.

All filesystem fixtures remained under TMPDIR. No path under real
restricted data, night roots or Block-5 roots was inspected; absolute paths
in artifacts/configs stayed text. Repository Git objects through the allowed
shared store supplied code/records only. Cached origin/main
`f193a320f836601014a88bc169aefad5cead4c71` includes items 169–174, including
pilot10's last-v3 instruction and retained pilots. No fetch was attempted:
the explicit no-network rule takes precedence over the requested fetch.
Current server/native measurement-Mac state is unknown.

No RUN_STATE, TASK_QUEUE, state_kernel or test_gen_state edits; no task
registration or advisor-visible hardware-state change. Actual freed bytes:
zero. No analysis pipeline, measurement window, cloud operation, model download,
real-source deletion, network, external messages, push or native MLX execution.

Next exact step: lead reviews local commits, supplies the reviewed native
parser pin/current ref objects/original-format M6 verifiers, adjudicates the
retention and unplugged-R0 conflicts, and hands the reviewed script files to
Ed. Ed copies/verifies all three pilots and M6 archives with sources retained,
then ejects and physically unplugs before each pre-arm census. A fresh SAFE
verdict, real two-copy custody, sufficient df space and a measurement release
are not asserted by this implementation.
