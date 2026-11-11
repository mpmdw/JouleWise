Stopped before editing: **Block 5 pins the file’s current bytes.**

- `t0_rehearsal.py` is **not** one of RL-84’s ten condition-13 paths.
- [sealed_inventory.json](/Volumes/JW-EXT/jw-wt/sol-w1-p3-qualification/configs/campaigns/v5_claim_25g83/sealed_inventory.json:509) pins it at commit `c27485347c9629b857df81665b5b1b8d10dcd36a`.
- The sealed pin, historical file, and current file all have SHA-256:
  `833b19ad013ed117ff2f0ab5834ce558a7b35227d0e9ba0332f9a07233b21ef1`
- [registry.json](/Volumes/JW-EXT/jw-wt/sol-w1-p3-qualification/configs/pins/registry.json:39673) binds that inventory entry to historical target 4483. It also records a Block 4 sizing reference at `bda1c180cf156ecedcbe01a6010390dcd724c8cc`.
- The v4 `ARTIFACTS` membership check returned `True`.

Per your **“STOP … edit nothing”** instruction, no files changed, no report was written, no tests ran, and no commit was created. The requested branch remains clean.

Next step: lead disposition of the sealed-file pin before any registry edit.