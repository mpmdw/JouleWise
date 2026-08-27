# S11 named residuals at merge (PR #213, head bb68c97c)

Nothing here is a blocker. Each is a limit the stream is knowingly leaving, recorded
so it is carried rather than rediscovered. Lead-reproduced at the bench 2026-08-27.

## R-1 — the ancestor walk stops at depth 6, and the stop is SILENT

`_reachable_analysis_manifest_v3` ascends at most
`MAX_ANALYSIS_MANIFEST_V3_ANCESTOR_DEPTH = 6` real ancestors looking for a marker that
names the stage. Beyond that it returns `None`, which means null provenance and a
collection that proceeds.

Lead reproduction (synthetic packs, stage nested under N group directories):

```
stage 6 levels below pack root : rc=0  id='am-e6ae7e138…'  bundle invoked
stage 7 levels below pack root : rc=0  id=None             bundle invoked
stage 8 levels below pack root : rc=0  id=None             bundle invoked
```

At depth 7 and beyond this is the original S9-01 shape — a silent null on a stage that
does belong to a pack.

**Why it is not cured here.** The unbounded walk was delta-blocker F2: it ascended to
the filesystem root and captured unrelated markers. Bounding it is what closed F2. The
obvious tightening — refuse instead of returning null when the bound is hit — would
refuse every legitimate no-marker calibration or reference collection nested more than
six levels deep, which is the F3 over-reach in a new costume.

**Exposure today: none.** The generator writes stage directories as DIRECT CHILDREN of
the pack root (`configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/01_…` etc., depth
1), and the window runbook passes those paths verbatim
(`docs/phase_2/window_runbook.md:1456,1480`). No committed or generatable pack comes
near depth 7.

**If it is ever to be cured** it needs a design decision, not a patch: an authenticated
pack root supplied by the frozen launch plan, so the collector is TOLD its pack instead
of discovering it. That is the shape the delta auditor recommended and it is the honest
end state.

## R-2 — an unowned pre-existing bundle is adopted, and only the log records it

The existing-bundle ownership check refuses only a bundle owned by a campaign
provenance carrying a DIFFERENT analysis identity. A bundle with NO owning provenance
proceeds.

Lead reproduction: collect 20 bundles, delete every campaign provenance and the
campaign log, re-collect the same stage:

```
rc=0   executions = ['existing'] x20   no bundle re-invoked
unowned bundle ids recorded in the campaign log: yes
```

So bundles whose provenance no longer exists are adopted into the new campaign.

**Why it is deliberate.** Requiring ownership was delta-blocker F4: a run interrupted
after a bundle finalized but before its provenance member was written left that bundle
unowned forever, so the campaign could never resume — unrecoverable loss on a spent
hardware window. The contract sentence
(`docs/specs/c027/analysis_engine_trio.md:465-468`) forbids reusing existing bundles
*under the new ID*; it does not speak to unowned bundles, and refusing them costs more
than it protects.

**This is not a regression.** Before this stream there was no ownership check at all,
so every pre-existing bundle was adopted unconditionally. The stream strictly narrowed
what is adopted and made the adoption visible in the preflight detail.

**The honest cure**, if wanted later: a durable pending→invoked ownership reservation
written before dispatch, so the crash interval has an owner and unowned genuinely means
foreign. That is a collector-lifecycle change, not a check.

## R-3 — the same-filesystem guard is inspected, not executed

The walk breaks when an ancestor's `st_dev` differs from the stage directory's, so it
cannot ascend across a mount boundary. This was read in the code and reasoned about; it
was NOT exercised, because doing so needs a second filesystem mounted under the pack.
Recorded as unverified rather than claimed.

## R-4 — the unreadable-marker branch uses a code the registry does not name

An `OSError` reading a selected marker is reported as
`analysis_prospective_source_hash_mismatch` (`scripts/run_campaign.py:1393-1398`) even
though no source hash was obtained or compared. The delta re-audit was asked to rule
whether the registered code is untruthful for that condition and answered **YES**, on
the registry's own wording (`docs/decision_log.md:9160-9214`).

Per the magistrate's T26 ruling this is a D-078 vocabulary amendment — a decision-log
change made in the registration wave, not here. The proposed code is
`analysis_prospective_input_unreadable`. No implementation work is blocked; the branch
fails closed either way.
