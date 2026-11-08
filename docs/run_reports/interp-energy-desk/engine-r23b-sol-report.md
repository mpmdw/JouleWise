Committed all seven fixes on `engine-r23b`:

`a4cb35424e3fd27d54fadd29650450be1d6b3a02`

- Changed eight production modules, three test modules, `ENGINE-sol.md`, and the run report.
- **136 targeted tests passed**, one module per process. Supplied probes, compileall, diff checks, and serial/parallel byte equality passed.
- Compatibility note: selection-only W1 exports now need full `anchor_members` evidence for σ_w; thermal-only snapshots still supply checks/contrast.
- No new native MLX tests are required. Hardware validation remains outside this synthetic qualification.

Working tree is clean; nothing pushed. Exact commands, results, file list, and lead handoff are in the [run report](/Users/edr/code/CapstoneProject/jw-wt/sol-engine-r23b/docs/run_reports/2026-11-08-engine-r23b.md).