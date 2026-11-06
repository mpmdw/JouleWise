# Triage of sol/burn-w1rev (lead-side verification, 2026-11-06)

All code findings are present on the r4 integration head (d9c709ee5). The patch
3-way-applies there. After regenerating the kit (plan_tree/identity_pins hashes),
test_v4_kit + test_v4_prequal: 101 OK. On this branch: 89 OK.

- Sizing provenance: REAL, LOW. prepare runs generate(check=True), which already catches a
  stale sizing_b5.json. Only install's require_w1_ready checked mere existence.
- WP11 hf_pins receipt bytes: REAL, LOW. The shard hashes were already compared, so a
  stale receipt could not change the bound weights.
- WP18 fixture bytes: REAL gap, MEDIUM, but the fix is a DESIGN choice. The fixture paths
  registration/wp18_{x,y}_token_ids.json are new. They become a hard W1 prerequisite, so the
  Mac side must commit the fixtures exactly there. Needs a lead ruling, not a silent merge.
- R0 effort message: cosmetic.
- Disk-gate test using the r0_desk disk_path (/Users/edr): test hygiene only.
