Committed **`ec20d5422`** on `align/2026-11-08-ssd-permanent-sol1`. Working tree is clean; nothing pushed.

Added:

- [Permanent SSD study](/Users/edr/code/CapstoneProject/jw-wt/sol-ssd-permanent-sol1/docs/align/v4/SSD-PERMANENT-STUDY.md)
- [Draft amendment](/Users/edr/code/CapstoneProject/jw-wt/sol-ssd-permanent-sol1/docs/align/v4/DRAFT-AMENDMENT-permanent-ssd.md)
- [Run report](/Users/edr/code/CapstoneProject/jw-wt/sol-ssd-permanent-sol1/docs/run_reports/2026-11-08-ssd-permanent-sol1.md)

The drafts rank B → B-unmount → B-cut, reject in-window writes, propose **±0.10 J mean-error / 0.60 J added-SD** DC tolerances, and cover qualification hours, R1 transfer, automation, series breaks and 4 TB purchase requirements. Old documents and coordination files remain unchanged.

Verification passed:

- `python3.13 -B -m unittest tests.align.test_ssd_qualification` — 26 tests.
- `python3.13 -B -m unittest tests.align.test_external_volume` — 23 tests.
- Documentation links, arithmetic and staged diff checks.

**Next:** lead comparison and disposition of the proposed tolerances/protocol. Hardware power states, DC precision, remount reliability and R1 transfer remain unmeasured. Native meter/SMC/powermetrics/MLX qualification must run outside this sandbox in a clean session. The 8.5-hour-per-candidate schedule is a base cost, not a guaranteed decisive result.