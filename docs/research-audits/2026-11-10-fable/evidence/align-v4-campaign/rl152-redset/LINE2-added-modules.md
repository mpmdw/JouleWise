# RL-155a §4: the line owed for dev-02 (and as a note beside the pilot's arm record)

Question. RL-152 §2.2's red set has two modules beyond its named eight: `align.test_r1_followup` and `hazards.test_refusal_allowlist`. For each, are the bytes it tests among the 37 frozen paths of `c76344c5`/`d963500b`? If so, are they byte-identical at the base (`fe907d0d3`), the pilot commit (`b4b6aeb19`) and #777's head (`ae340d3da`)?

Method. Each red test was run once at `b4b6aeb19` on the Air, which has no live run.
- An audit hook recorded every repo file the test process opened or imported (`files-*.json`).
- For the sampler test, a profiler recorded every repo file whose code ran during the test method itself (`exec-r1_followup.json`).
- The refusal test was also run at the #775 head `8bd31ae5a` to get CI's failure.
- Blobs are from `git rev-parse <commit>:<path>`.

## 1. `align.test_r1_followup.ProcessSamplerTests.test_main_interpreter_blocked_in_every_phase_does_not_starve_inventory` (1 ERROR on CI)

- **What it tests.** A timing property: a `usleep` that holds the GIL for 2.1 s must not starve the sampler process.
  - Code executed inside the test: `joulewise/align/apple/r1_runtime.py` (`ProcessInventory`), `joulewise/align/apple/thermal.py`, `scripts/align_r1_followup_kit.py` (`phase_coverage`), plus test helpers.
  - It **passes on the Air** at `b4b6aeb19` (11.5 s). The CI error is host and timing related.
- **Frozen paths it executes, both identical at all three commits:**

| Frozen path | fe907d0d3 | b4b6aeb19 | ae340d3da |
|---|---|---|---|
| `joulewise/align/apple/r1_runtime.py` | 261761f1 | 261761f1 | 261761f1 |
| `joulewise/align/apple/thermal.py` | e7cbd680 | e7cbd680 | e7cbd680 |

- **Not frozen:** `scripts/align_r1_followup_kit.py` (d1527499, d1527499, 4d9e2e9a).
- **Only imported.** The test module imports two more frozen paths at load time, and #777 changed both. The test never calls into them.
  - `joulewise/align/apple/v4_registration.py`: 963b6511 at base and pilot, 12a6a98d at #777's head.
  - `scripts/align_r1_rehearsal.py`: 9619cc86 at base and pilot, 2d6b24c1 at #777's head.
  - These are the #777 frozen-path changes RL-152 §2.2 already lists. Their bytes at the base and the pilot commit are identical.
  - Nine other frozen paths are also imported, and all are identical at all three commits (table in `files-r1_followup.json` and below).

## 2. `hazards.test_refusal_allowlist...test_every_refusal_site_is_listed_with_its_exact_count` (FAIL on CI)

- **What fails** (reproduced at `8bd31ae5a`): one unlisted refusal site, `scripts/launch_align_r0.py`, function `launch`, `ValueError|parts c runs`, line 308.
  - That file **is a frozen path**, and it is **byte-identical at all three commits: `d2e8cba0`.**
  - The fix is the census line in `configs/gates/hazard_refusals.json`, which is not frozen. Its blobs:

| Commit | `hazard_refusals.json` blob | Census line present? |
|---|---|---|
| fe907d0d3 (base) | 90828966 | no |
| b4b6aeb19 (pilot) | 567120bb | yes; the test **passes** at the pilot commit |
| 8bd31ae5a (#775 head) | 90828966 | no; reverted to base by `cf63121bc` |
| ae340d3da (#777 head) | c512bb4c | yes |

- **The census also parses nine other frozen paths.** Eight are identical at all three commits.
- **The exception is `scripts/run_align_r1_smoke.py`:** b7a66a5b at base and pilot, 5756cdb1 at #777's head.
  - #777 changes one refusal message, `"idle soak would overlap the 11:45-13:15 ..."` → `f"... {r1.os_batch_window_text()} ..."`.
  - It is scanned by the test, but it is not the failing site.

## The line, as I read it (the lead decides)

- **`align.test_r1_followup`.** The bytes it executes that are frozen are `r1_runtime.py` 261761f1 and `thermal.py` e7cbd680, identical at base, pilot and #777 head. The test passes on the Air, so the CI error is environmental.
- **`hazards.test_refusal_allowlist`.** The failing site is in frozen `scripts/launch_align_r0.py`, d2e8cba0, identical at base, pilot and #777 head. The red comes from the unfrozen census file, which is missing the line at base and at `8bd31ae5a`. It passes at `b4b6aeb19` itself.
- **Strict-reading caveat for the research lead.** Under RL-155a §4's literal text ("the bytes it tests"), two kinds of frozen path differ at #777's head and so trip "comes to me before dev-02 arms":
  - frozen paths that are only imported (`v4_registration.py`, `align_r1_rehearsal.py`);
  - frozen paths that are only scanned (`run_align_r1_smoke.py`).
  - None is executed by the sampler test or is the failing census site.
  - All are identical at base and pilot, and all are #777's known three frozen-path changes.
