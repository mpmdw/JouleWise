# S-0 estate 11 — the delta W-10 forces (D-157 R-3)

> **This file is co-owned by two T26 streams and merges by APPEND.** The
> D-139/A2 gamma-families stream (branch `fix/d139-a2-gamma-families`) owns the
> sections describing the `_admit_bound_analysis_manifest` mint-path delta —
> the anchor map, the immutable-audit ranges, the affected runsheet and runbook
> sections. This branch (PR #214, T26 S3 pack authentication) contributes only
> the section below. Neither stream's text is reproduced on the other's branch,
> so whichever lands second appends its own section and never rewrites the
> other's. If you are resolving a conflict here, the resolution is "keep both".

## S-1 manifest builder-digest re-pin (S3 D6)

Contributed by the T26 S3 pack-authentication stream (PR #214); it sits in this
handoff because it is another mechanical delta the estate-11 operator carries,
and for no other reason.

### What is wrong

A **custody tool** is one of the four scripts the S-0 operator executes from the
clone during the transaction. Before the first one runs, §3.6.1 recomputes each
executing file's SHA-256 and refuses if it differs from the digest recorded for
that path — this is how the operator learns that the file about to run is the
file that was reviewed.

Two records claim to hold those digests, and they are not the same kind of
thing:

1. `s0-candidate-manifest.json`, whose `custody_tools` map the runsheet
   **computes from the blobs at the reviewed head** at §1.3
   (`s0-runsheet-r4.md:1185`) and which §3.6.1 reads at `:1882`. This is the
   record on the enforcement path.
2. `docs/process_traces/2026-08-22-t20/s1-candidate/MANIFEST.md` §6 "Tool
   digests" (lines 184–198), a **hand-transcribed** block recomputed once, at
   the fix-round head on 2026-08-23. Nothing recomputes it. It is a review
   record, not an enforcement input.

Record 2 is now false for one of the four tools:

| Tool | S-1 §6 records | Builder bytes + `.sha256` sidecar today | Agrees |
|---|---|---|---|
| `build_family_marker.py` | `e51617f9…` | `e51617f9…` | yes |
| `verify_family_marker.py` | `68be9c6e…` | `68be9c6e…` | yes |
| **`build_v4_histsem_pinset.py`** | **`29335e6f…`** | **`d72c1560…`** | **NO** |
| `verify_receipt_histsem.py` | `394ed199…` | `394ed199…` | yes |

Full values: recorded
`29335e6fcfe8e97a78212f44e44a96e869d3179afb3411cda74f2a8070b978fa`; actual
`d72c156030d9dc477671924677bff70624aaf878868fb0b5ec3ac4035990b23a`.

### How it drifted, exactly

Two commits changed the builder after S-1 §6 was transcribed, and each one moved
the digest:

| Commit | Date | Subject | Builder SHA-256 after it |
|---|---|---|---|
| `f6a4c81d` | 2026-08-23 | Fix the pinset builder's chain composition (lead pre-execution read catch) | `95d55935…` |
| `cd46e165` | 2026-08-24 | Cure the `_v4` pinset builder's unsatisfiable pre-authoring gate (projection custody) | `d72c1560…` |

The tracked sidecar `scripts/build_v4_histsem_pinset.py.sha256` followed both
moves and reads `d72c1560…` today, so the sidecar mechanism worked. Only the
hand-transcribed block went stale — the failure mode S-1 §6 names in its own
preamble ("a hand-transcribed digest block does not update itself, which is
precisely the drift the `.sha256` sidecar regression exists to catch for the
tools"). It caught it for the tools and not for itself.

### Reproduce it

```zsh
cd <clone>
for f in build_family_marker verify_family_marker build_v4_histsem_pinset verify_receipt_histsem; do
  printf '%s  actual=%s  sidecar=%s\n' "$f" \
    "$(shasum -a 256 scripts/$f.py | cut -d' ' -f1)" \
    "$(cut -d' ' -f1 scripts/$f.py.sha256)"
done
sed -n '194,198p' docs/process_traces/2026-08-22-t20/s1-candidate/MANIFEST.md
```

### Consequence, stated precisely

**The transaction is not blocked and no gate is weakened.** §3.6.1 authenticates
against the generated `s0-candidate-manifest.json`, which is cut from the
reviewed head immediately before execution, so the executing builder is checked
against its own reviewed bytes either way. What is wrong is the **review
record**: a reader who audits the transaction by reading S-1 §6 — the natural
thing to do — is told the reviewed builder is `29335e6f…`, sees `d72c1560…` on
disk, and must either conclude the tool was tampered with or spend the time this
section saves. With the mint imminent, that is a live cost.

### What estate 11 does

Estate 11 re-pins the value. When it re-cuts the reviewed head it recomputes all
four tool digests with the command above and records them in its own estate
artifacts, so the estate-11 record is true at its own head.

**Do NOT edit `docs/process_traces/2026-08-22-t20/s1-candidate/MANIFEST.md`.**
That file is the pinned record of what S-1 reviewed on 2026-08-23; rewriting a
digit inside it would destroy the very evidence that shows the drift happened
and would make the estate-11 correction unfalsifiable. The pinned record stays
as written and this section is the correction that supersedes it — the same
"receipts govern over descriptive bytes" shape the freeze packs already use.
