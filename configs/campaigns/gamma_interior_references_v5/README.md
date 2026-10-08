# GAMMA interior drift-diagnostic references (block 5)

GAMMA (`d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5`) runs three interior reference
stages, after science members 20, 40 and 60. `run_campaign.py` skips a run id
whose complete bundle already exists in its runs root, so each stage needs its
own run id (GAMMA-INTERIOR-REFERENCES-01, lane L10).

- After member 40 (the decode/prefill boundary, the window's temporal
  midpoint) GAMMA runs the shared `window_references_v5/midpoint/` reference,
  `neg8-window-midpoint`. It is the window's one NEG-8 midpoint, as in the
  floor packs.
- After members 20 and 60 (the two arm midpoints) GAMMA runs the two
  directories here. Each config is `window_references_v5/midpoint/
  neg8-window-midpoint.json` byte for byte except `run_id`. Each order manifest
  gives the role `window_interior_reference_diagnostic`, which is not a NEG-8
  role, so the whole-window NEG-8 screen (which accepts exactly 3 start + 1
  midpoint + 3 end references) and the drift allowance do not read them. They
  are recorded drift diagnostics.

The GAMMA generator does not write these files. It refuses unless their bytes
are exactly what it derives from the shared midpoint reference.
