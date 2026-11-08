Committed **`57f224549`** on `align/2026-11-08-ssd-permanent-sol2`. Working tree is clean; nothing pushed.

Added:

- [Permanent SSD study](/Users/edr/code/CapstoneProject/jw-wt/sol-ssd-permanent-sol2/docs/align/v4/SSD-PERMANENT-STUDY.md)
- [Draft amendment](/Users/edr/code/CapstoneProject/jw-wt/sol-ssd-permanent-sol2/docs/align/v4/DRAFT-AMENDMENT-permanent-ssd.md)
- [Run report](/Users/edr/code/CapstoneProject/jw-wt/sol-ssd-permanent-sol2/docs/run_reports/2026-11-08-ssd-permanent-sol2.md)

The drafts rank **B → B-unmount → B-cut**, reject in-window writes, and propose DC budgets of **±0.10 J mean error and ≤0.60 J added SD**, requiring qualification. They cover MBP hours, R1 transfer, automated lifecycle hooks, manifests, configuration-break consequences and 4 TB purchase requirements. Old documents and protected coordination files are unchanged.

Verification:

- `python3.13 -B -m unittest tests.align.test_ssd_qualification` — **26 passed**
- `python3.13 -B -m unittest tests.align.test_external_volume` — **23 passed**
- Arithmetic, local links and staged whitespace checks — **passed**

Open: actual DC precision, power-state stability, hub switching, remount reliability and R1 transfer remain unmeasured. The proposed budgets require lead scientific adoption. Next step is lead comparison of both seats before selecting and qualifying a mode for W1. No hardware capture, full suite, network or sealed-data access occurred.