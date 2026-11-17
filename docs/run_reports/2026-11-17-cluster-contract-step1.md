# Cluster contract, step 1

The lead selected this [AGENT] task directly under RUN_STATE item 399. The active
stop card was clear. CURRENT still points to item 398. The item 398 measurement
path and the generated pointer were outside this task.

- [Cluster contract](../ops/cluster_contract.md) records the adopted L1–L6,
  seam ownership, scenario requirements and merge order.
- The new publication primitive has no existing production callers. Its tests
  cover atomic create and replace, sync order, collisions, unsafe reads,
  ENOSPC, EIO, and recovery from injected and abrupt process exits.
- The shared suite collects 75 scenarios. A-09 passes against the real watcher.
  Expected failures comprise 73 missing-seam scenarios and A-12, which
  reproduces main's acceptance of duplicate numbered pointer headings. A-12
  needs a separate main behavior fix for the final cluster gate.
- Focused verification used `python3.13 -B -m unittest -v tests.test_durable
  tests.contract.test_cluster`. The extra inventory test passes. The local
  generated-state and pointer checks passed. The full sharded suite is the
  hosted PR CI check. Local broad discovery includes tests that access
  prohibited data classes or signal processes, so this session ran the
  focused synthetic checks locally.
- The fixture census attempted `scripts/fixture_orphan_census.py --fail-on-orphans`
  and could not obtain the process inventory because `ps` was denied
  (`Operation not permitted`). No orphan count was established.
- The next step is lead review of the draft and CI evidence, then rebasing
  #804 onto the reviewed step 1. Member-specific fixtures and production
  checkpoint call sites belong in the member PRs. Follow the order in §4.4
  and keep live gates with the lead.
