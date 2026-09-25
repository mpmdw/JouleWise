# Spotlight exclusions the measurement machinery depends on

This is untracked machine state that the code relies on. Nothing checks it at runtime. The t0 census sees indexing load only indirectly, through CPU.

**The Spotlight privacy list** (System Settings → Spotlight → Search Privacy) must contain:
- `/Users/edr/code` (added 2026-09-17, computer use, screenshot-verified);
- `/Users/edr/night-custody` (added 2026-09-17), which covers `night-custody/measurement/`, where evidence-night measurement clones have been created since 2026-09-25;
- `/Users/edr/night-archive` (added 2026-09-17).

**Verify** with a probe file (wait ≥ 45 s, then expect `0`), plus a control outside the list (expect `1`):

```zsh
mkdir -p ~/night-custody/measurement/spotlight-probe && echo '{}' > ~/night-custody/measurement/spotlight-probe/p.json
mkdir -p ~/spotlight-ctrl && echo '{}' > ~/spotlight-ctrl/p.json
sleep 45
mdfind -onlyin ~/night-custody 'kMDItemFSName == "p.json"' | wc -l   # expect 0
mdfind -onlyin ~/spotlight-ctrl 'kMDItemFSName == "p.json"' | wc -l  # expect 1
rm -rf ~/night-custody/measurement/spotlight-probe ~/spotlight-ctrl
```

Last verified 2026-09-25 ≈02:30 PDT on 25G83: 0 and 1.

**Known non-remedies:**
- A `.noindex` folder-name suffix does **not** prevent indexing on 25G83 (tested).
- `corespotlightd` indexes content that apps donate (Mail, Messages, Notes and similar); folder exclusions do not cover it.

The record is `docs/process_traces/2026-09-24-interactive-4b/29-spotlight-gap-measurement-clones.md`.
