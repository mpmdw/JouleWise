# R16 condition waits implementation handoff

2026-11-08. Branch: `align/2026-11-08-condition-waits-impl`.
Implementation commit: **`427bb3434`**, `align v4: implement R16 condition waits
and CW-1 qualification kit`. This report is a subsequent local documentation
commit. No push, registration, native arm or characterization was performed.

## Scope and authority

The brief installs R16 from `origin/main:RUN_STATE.md` item 226 and the paired
condition-waits agreement. Read both designs through local Git objects, the
agreement, the main speed toolbox, repository instructions, targeted M0/state/
queue sections and D-050/D-077. No active stop card applies. This is the bounded
AGENT implementation lane requested by Ed, not a quiet-machine lane selected
from the old generated queue. No delegation or external consult was used.

The explicit brief overrides normal bookkeeping and canonical-suite rules:
`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and
`tests/test_gen_state.py` are unchanged. No kernel task was registered. The
requested branch already existed at intake, clean, based on the requested R11
lane plus its existing two commits; those commits were preserved.

Only repository code/config/docs, allowed Git objects and synthetic temporary
files were used. Absolute measurement/model locators encountered in repository
text were not followed. No real restricted directory, sealed outcome, Block-5
analysis, model payload or network was accessed. No measurement job was started,
signalled, inspected for results or otherwise operated.

## Delivered behavior

- Frozen Q/policy validation, two-sided temperature bands, G0 slow-slope rule,
  qualified fans, complete trailing power means, pressure/display/setup/battery
  predicates, overlapping 180 s stability/guard and 300 s display/quiet floors.
- Fixed 1800 s attempt ceiling, including equality; no release at expiry. An
  explicit second attempt needs fresh ambient-check provenance and the prior
  failure digest. Attempt 3 refuses. Retry metadata is forwarded to native GO.
- Native SMC/notify/pmset/ioreg and power adapters with injected seams. The
  native arm shares its existing contention intervals with the evaluator;
  final physical/clock checks and the final agent census still precede GO.
  No post-READY sleep. All new computation and observers end before the chain.
- Create-once admission traces/receipts, deterministic replay, current session/
  boot/policy bindings, triage receipt digests and a newly computed binding at
  actual native GO. Preliminary install evidence is never reused as GO.
- Optional prospective policy embedding in the v4 kit and ALIGN-only driver
  wiring. Missing Q/CW-1 selects cohort-frozen `incumbent_shadow` when the lead
  builds the policy. Shadow failures, missing channels, floors and ceiling do
  not gate incumbent readiness. Absent prospective policy preserves older kits.
- CW-1 plan generator, bounded orchestration API, real D/R0 one-attempt pulse
  command, synthetic finalize/offload stand-in, display transition, both full
  1800 s recoveries, Q/delta candidates, censoring/re-exit checks, total observer
  cost gate and zero-hold replay for all three required idle sources.
- Timing writes are boundary markers only on the canonical chain journal;
  sample-rate records are separate admission evidence. No timing ledger is
  computed on the MBP. No measured episode, idle, G0/G1/H, settle, countdown,
  workload/RNG/cache path or batch size changed.

The implementation/runbook is
[`CONDITION-WAITS-IMPL.md`](../align/v4/CONDITION-WAITS-IMPL.md). The committed
registration receipt is still a pending template; no numeric hardware Q or
passing CW-1 evidence was invented or registered.

## Files touched

New implementation and tooling:

- `joulewise/align/apple/condition_waits.py`
- `joulewise/align/apple/condition_waits_native.py`
- `joulewise/align/apple/condition_waits_cw1.py`
- `scripts/align_v4_condition_waits.py`

Existing integration and bindings:

- `joulewise/align/apple/v4_cadence.py`
- `joulewise/align/apple/v4_registration.py`
- `joulewise/hazards/arm.py`
- `joulewise/hazards/contention.py`
- `joulewise/b5/driver.py`
- `scripts/align_v4_kit.py`
- `scripts/align_v4_session.py`
- `configs/campaigns/align_v4/plan_tree.json` — regenerated generator digest only.
- `configs/campaigns/align_v4/registration/identity_pins.json` — regenerated tree digest only.
- `configs/campaigns/align_v4/registration/registration_receipt.json` — four new pending artifact entries.

Verification and documentation:

- `tests/align/test_condition_waits.py`
- `tests/align/test_condition_waits_arm.py`
- `tests/align/test_v4_kit.py` — expected forwarding of two optional CLI arguments.
- `docs/align/v4/CONDITION-WAITS-IMPL.md`
- This run report.

## Verification

Modules were run **one at a time**, with total test time well below the brief's
20 min bound. The full suite was deliberately not run because Ed expressly
forbids it while the blinded 8-worker analysis is running. All final targeted
results below pass; 240 distinct tests completed, **237 passed / 3 skipped**.

Each command below used `JW_B5_SYNTHETIC_ONLY=1`:

| Command | Final result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_condition_waits` | 35 passed; final complete run 49.533 s |
| `python3.13 -B -m unittest tests.align.test_condition_waits_arm` | 7 passed |
| `python3.13 -B -m unittest tests.align.test_v4_cadence` | 26 passed |
| `python3.13 -B -m unittest tests.hazards.test_arm_dwell_clean_run` | 4 passed |
| `python3.13 -B -m unittest tests.hazards.test_contention` | 48 run; 3 native tests skipped |
| `python3.13 -B -m unittest tests.align.test_v4_executed_closure` | 4 passed |
| `python3.13 -B -m unittest tests.align.test_v4_kit` | 116 passed |

Focused native-source/reference tests were also rerun after their final edits
(5 passed). `python3.13 -B scripts/align_v4_kit.py` regenerated the provisional
kit; it did not arm anything. CLI `--help` passed. All 14 changed Python files
compiled in memory without bytecode output. Staged `git diff --check` passed.
Protected coordination/state paths were checked unchanged before commit.

The disabled contention hooks produce **byte-identical complete measurement
JSON** to `origin/align/2026-11-08-v4-r11` on synthetic quiet, burst and persistent
contention scenarios. Receipt replay bytes and synthetic compressed offload
bytes are also compared exactly. These are synthetic equivalence checks, not
live hardware or whole-window output claims.

Measure-first check: cProfile over 301 synthetic evaluator samples consumed
0.081376 process CPU seconds in that run; a second replay produced identical
receipt bytes. This excludes every native source and does **not** establish
the 0.5%-of-one-core monitor budget or a utilization saving. No cache, batching
or software parallelization optimization was introduced.

Development catches included shadow-ceiling interference with incumbent waits,
overly strict slope coverage, and moving-bin aliasing under tiny native-guard
probe jitter. The final tests cover these cases. An early integration test
reached the instrument fake's sandbox-inaccessible process-group census; the
final integration tests stub instrument collection/judgment at its independent
seam. Real instrument cleanup remains part of the native smoke.

## Remaining gates and uncertainty

1. The lead must approve the exact Q source under final R1 mode/picks, decoder/
   units/channel definitions, setup and contemporaneous fan/power reference.
   This run supplies no hardware values. If Q/CW-1 is missing at registration,
   write the explicit incumbent-shadow policy and keep that policy for the cohort.
2. Native smoke must check PM endpoint/elapsed semantics and freshness, SMC
   decoders and fan lag, IODisplayWrangler against all online displays and the
   screensaver, raw clock behavior, final reads/census and bounded cleanup.
   Native sampler subprocess cost may exceed the 0.005 CPU-s/s budget; only a
   measured total observer-tree cost can settle that. Self CPU alone cannot.
3. In a clean magistrate-owned gap **after R1**, run CW-1 with the existing local
   D weights through the pinned R0 MLX harness, plus pulse 2 and both recoveries.
   Supply/review bounded pulse handles, native preflight/display/final-check
   callbacks and observer-tree CPU accounting before launch. Nothing is launched
   by the parser CLI. No MLX or real D decode ran in this sandbox; no CPU fallback
   or downloaded weights are a substitute.
4. Replay permitted new diagnostic exports for R0 rerun-11 idle, R1 soak and
   CW-1 soak, requiring zero eligible-boundary holds for each. Missing channels
   remain unknown. Review R1's post-D recovery export for load transfer. Only
   then may the lead use the band for a new cohort under registration/review.
5. The magistrate owns cross-session attempt counting and ambient evidence;
   callers must not relabel each failed session as attempt 1. The implementation
   limits each declared sequence but does not write a new coordination ledger.
6. Install's preliminary receipt and the later native arm are separate reads.
   Native admission restarts after its cadence/collector work. Its cost, including
   that preliminary check, must appear in the before/after ledger. A final native
   state disturbance returns NULL with evidence; standalone `run_attempt` can
   re-establish stability within its original deadline. No two PASS files are
   represented as one continuous trace across install.

**Next exact step:** review this implementation, assemble the final-R1 Q/channel
bindings (or explicit incumbent-shadow policy), and prepare the bounded CW-1
host callbacks for a later clean magistrate gap. Do not launch them beside the
current analysis or from an active agent session. Keep **0 minutes** of credited
saving and the existing 30–45 min turnaround estimate until measured evidence
includes all preliminary and native-arm costs.
