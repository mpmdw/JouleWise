# 04 — Retirement of the harvested 09-15 plan root (2026-09-15 23:25 PDT, activation `08ca8197`)

Requested by the interactive session `b0ae8462` (cross-session message after
record 03's finding): retire
`/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260915` under the
record-48 procedure (runbook §1.4 precondition "after any prior stub or plan
root is retired"; the documented post-completion step). Preconditions held:
the night was REFUSED at t0 and harvested (activation `1acf2aee`, byte-exact
archive `…-harvest-20260915` with 18 `SHA256SUMS` lines), both night agents
uninstalled, `launchctl list` showing only `com.joulewise.magistrate`,
nothing armed.

Executed, in order:

1. The 18 harvest checksums re-checked against the LIVE root: 18 OK, 0 non-OK.
2. `lstat` inventory (size, mtime ns, path; `results-clone/` excluded) taken
   before: 20 entries (`03-stage-evidence/retire-20260915-lstat-before.txt`).
3. `mv` to `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260915-plan-root-retired-1789539949`
   (same filesystem rename; no byte inside the root altered).
4. Inventory re-taken after and `cmp` identical
   (`03-stage-evidence/retire-20260915-lstat-after.txt`).
5. The 18 checksums re-verified in the new location: 18 OK.
6. `SHA256SUMS` file digest (unchanged archive manifest):
   `e8dd3db32c149125885984b5dc1e2cacaff827707a0da710e01a404308d8e8b4`.
7. Discoverable plans under `/Users/edr/night-custody/*/night_plan.json`
   after: 0. Watchdog `state.json` state: ACTIVE throughout.

The staged `rehearsal-20260916` plan (record 03) stays in
`/Users/edr/night-plan-staging/`, undiscoverable, unpublished.
