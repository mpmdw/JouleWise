# Exhibit B — controlling contract text at main `9e0a4995`

## B1 `docs/contracts/evidence_night_entry.md` lines 142–158 (slice B1 authority and scope) and 203–208 (check item 4)
```
## Slice B1: checks and the installer façade

```
python -m joulewise.evidence_night check --candidate STAGING
python -m joulewise.evidence_night publish-install --candidate STAGING --notice-accepted MESSAGE_ID
python -m joulewise.evidence_night verify --candidate STAGING
python -m joulewise.evidence_night uninstall --candidate STAGING
```

Authority: consult 18; records 19 §1, **21** (superseding the latest-HEAD-move
predicate), 26 §4, 27 and 28; `NIGHT_HANDBACK` Census and ARM-RETRY-POLICY;
record 17 steps 0, 4, 5 and `evidence-checks.py`. The installer, census,
retry policy and driver remain unchanged. B1 is a mechanical façade for the
lead's bench procedure. `armable` means the implemented checks passed at the
recorded observation time; it is not notice/veto clearance or quiet-machine
validation. The lead must review workloads, stop/directive channels and all
readable NO relays, then leave with every owned helper before REQUEST.
[...]
4. Every `<roots_under>/night-custody/*/night_plan.json` is inventoried and
   must be a regular non-symlink file; directories and special files refuse.
   An existing regular `night/courier.sent` or `night/result.json` classifies
   its root as retained. Otherwise it is UNKNOWN and refuses. Discovery
   never removes a root, and has no fixed root count. Retention classification
   does not certify process liveness or completed delivery.
```

## B2 consult 18, cited by B1 as authority: `docs/process_traces/2026-09-20-activation-21752427/18-consult-evidence-installer-split-astra.md` line 53 (the KEEP-inventory row on discovery). Proposition addressed: what discovery must establish and what it must never do. Included because the contract names this record as its authority and no other primary text states the discovery duty.
```
|---|---|
| Keep | Fenced canonical/other-worktree roots; no overwrite of foreign, retained or invoked candidates; symlink/path collisions; same-filesystem atomic publication. Prevent mistaken writes and lost evidence. |
| Keep | Raw shared bracketed census, ancestry/foreign-workload review, real-night refusal without stub exemption, unknown observations resolved, owned helpers gone before REQUEST. |
| Keep | Discover retained roots and establish harvest/ownership/completion; unknown or active ownership stops. Never delete or hide roots to pass discovery. |
| Keep | Locked environment, pinned checkout, tracked manifest/source equality, ruled registration and chain digest binding, wrapper sidecars and published-plan literal. Keep frozen v2/no-pack protocol and PROVISIONAL status. |
| Keep | Reject unresolved placeholders, invalid kind/schema, stale/future-authored plan, non-minute or ambiguous local t0, existing results, loaded/UNKNOWN jobs, retained prior plists and exclusive install cutoff. Derive timing from `schedule`. |
| Keep | Evidence probe schema, binding/freshness, verify-only/no collect/no load, proven cleanup, consent-repeat requirement and interpreter identity. No probe-success claim of collection. |
```
