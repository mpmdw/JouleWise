# align-residual lane report

## SUMMARY

- A7 energy-residual implementation checkpoint; validation is pending.
- Required shared contracts were read and remain unchanged.
- Implements the five prescribed logged-work terms with scaled Householder QR.
- Estimates extra variance by the nonnegative Paule-Mandel moment equation.
- Carries shared coefficient covariance and independent turn/episode uncertainty.
- Calibrates by leaving task pairs out and using the inverse empirical CDF.
- Includes hidden-decode power, deleted-turn and zero-energy synthetic checks.
- Documents provisional M3 Max and duty-sampled NVML planning examples.
- Cloud shell is still unavailable; no tests or hardware measurements have run.

## FILES

- joulewise/align/energy_residual.py: required records/API, WLS detector,
  flagged output adapters and shared-Episode adapter.
- tests/align/test_energy_residual.py: production-shaped episode/trace fixtures,
  focused checks and optional NumPy WLS comparison.
- tests/align/test_energy_residual_power.py: coefficient coverage, grouped
  calibration and sabotage/deletion/zero-energy power worlds.
- docs/align/energy_residual.md: model, uncertainty, quantile and power formulas,
  instrument examples and limits.
- .codex-report/align-residual.md: this checkpoint; final results pending.
- No registry additions yet.

## PUBLIC API

Required dataclasses retain exactly the specified constructor fields:
TurnRow(episode_id, group, context_tokens, prefill_tokens, decode_tokens,
duration_s, energy_j, energy_half_width_j);
EnergyModel(names, coef, cov, sigma2_per_turn, n_turns).

- design_row(r: TurnRow) -> list[float]
- fit_energy_model(rows: Sequence[TurnRow]) -> EnergyModel
- predict_episode(model: EnergyModel, rows: Sequence[TurnRow]) -> tuple[float, float]
- residual_score(model: EnergyModel, logged_rows: Sequence[TurnRow],
  measured_total_j: float, measured_half_width_j: float) -> float
- grouped_benign_threshold(benign: Mapping[str, tuple[Sequence[TurnRow], float,
  float]], *, alpha: float) -> float
- min_detectable_hidden_decode_tokens(model: EnergyModel,
  logged_rows: Sequence[TurnRow], *, alpha: float, power: float,
  measured_half_width_j: float) -> float
- turn_rows_from_episode(episode: Episode,
  turn_energy: Mapping[int, tuple[float, float]]) -> tuple[TurnRow, ...]

## TESTS RUN

None yet. The selected cloud runtime has cycled between pending and starting,
and exec_command returns "No usable execution environment is available".
Source and documentation were preserved through connected GitHub tools.
No extra dependencies have been installed. Test outcomes are not claimed.

Required after the runtime becomes available:

- python3 -m unittest discover -s tests/align -t .
- python3 -S -m unittest discover -s tests/align -t .
- python3 scripts/quick_suite.py --tier touched --since 4d47c4362352ccd8d4d904134a79f0d8260b21b5
- python3 -m unittest discover -s tests

## END-TO-END

Pending execution. Draft fixtures use 20-turn synthetic 8B agent episodes,
10 tool calls, growing cached contexts, 128-1024 prefill and 128-512 decode
tokens per call, 100 ms cumulative energy sampling, 6 J extra turn sd,
0.4/1.2/2.0 J turn uncertainties and a separate 1 J episode uncertainty.
The chain is shared-record serialization -> visible TurnRows -> real benign
fit -> task-pair-held-out threshold -> real residual scores/power boundary.
128 fitting worlds, 400 benign calibration episodes, and 1000 independent
evaluation episodes are specified. No results are claimed before execution.

The documented planning examples evaluate the normal approximation at alpha
0.05, power 0.8: M3 Max D=2.457641 J, H_min=12.221726 (13 integer tokens);
NVML D=56.603887 J, H_min=70.372071 (71 tokens). With 25 independent sensor
phase repetitions the illustrative NVML boundary is 30.755995 (31 tokens).
These are conditional planning calculations, not hardware findings.

## DECISIONS I MADE

- Follow the user's bounded research brief over unrelated mainline work.
  Root AGENTS.md was read; no nested AGENTS.md exists in the target paths.
- The core and all mandatory tests use only the standard library.
- Interpret supplied half-widths as standard uncertainties, as required.
- Use Paule-Mandel moments Q=n-5, nonnegative variance, safeguarded
  Newton/bisection, and sqrt(binary64 epsilon) relative moment convergence.
- Use max-magnitude column scaling and Householder QR, avoiding condition
  squaring from normal equations.
- Use (X'WX)^-1 covariance without a second variance multiplier.
- Preserve all turns and episodes; undefined fits/scores become flagged NaNs.
- Preserve exact public dataclass constructor fields. Private subclasses add
  flags to the returned model/numeric/sequence values.
- Leave whole task-pair groups out, use type-1 empirical quantiles and strict
  score > threshold decisions. Connected mixed groups are jointly held out
  and flagged; empty logs cannot identify a calibration group.
- Predictive uncertainty includes the summed design's full covariance form,
  independent turn errors and a separate episode measurement component.
- Duration never enters the design.
- Follow the records contract: decode_tokens includes hidden_tokens.
  The local Episode adapter subtracts hidden tokens and honors logged=False.
- Use mean logged context for added hidden-decode energy, as specified.
  Nonpositive hidden cost has an infinite boundary with a flag.
- Normal alpha/power calculations use caller-supplied rates; 0.05 and 0.8
  are the brief's conventional worked-example choices.
- NVML period/duty do not determine accuracy. State the extra power-gap,
  phase-independence and quantization assumptions rather than inventing one.
- The approximately 1 J M3 attribution component does not shrink with repeats.
- No network calls, credentials or real hardware are used by tests.

## CONTRACT-CHANGE

No shared-contract modification. A future typed diagnostics field/result
would let callers preserve flags without numeric/sequence subclasses.
The present lane-local adapters keep the exact required API fields and
numeric behavior; callers must copy flags into Episode.flags before
arithmetic/casting/JSON serialization.

The records contract validates malformed records by raising RecordError,
where the brief generally calls for flags; that shared behavior is untouched.
The lane itself records analysis problems as flags.

## OPEN ISSUES

- Cloud execution environment is unavailable; every test remains unexecuted.
- Full-suite registry requirements, if any, cannot yet be checked.
- Optional NumPy comparison has not run.
- Independent cross-model twin and real hardware validation belong to later gates.
- Linear-model/normal/independent-error assumptions need pilot scrutiny.

## NEEDS_RULING

none
