# Interim fit twin final builder pass

The lead's 07:21 ruling governs malformed T05 inputs and contradictory F04 receipts. The tests use synthetic fixtures and the recorded outcomes from audit 4. The twin uses only the registered KM003C decoder and initializer alongside the standard library and NumPy.

Twin manifest path `scripts/cadence_interim_twin.py`. Tested SHA-256 `91ca54ab8747ede3d0fe8826e1b7d06ef721bce94de52969b9508a3eac890aab`.

| Class | Regression | Result |
| --- | --- | --- |
| **F04 required** | A step with `SystemExit: 130` recorded with `rc=0` raises in the bound child. The receipt and step controls also cover other exit codes, deadline and exception paths, and disagreement with the step result. A matching interrupted receipt remains unaccepted. | PASS |
| **T05 required** | The exact duplicate-member injection raises. Nested duplicate keys, NaN, Infinity, float overflow, quoted NaN on a numeric timestamp, unknown phase labels or markers, and missing phase timestamps refuse. Finite writer phases and the ordinary missing-turn-index case still pass. | PASS |
| T07 | An appended journal reading with empty `sensors` uses the empty-map fallback. The nonempty malformed-sensors control still drops only its leg. | PASS |
| T10 | An empty `gpu` field contributes no clock evidence. The remaining paired samples still produce a valid cell. | PASS |
| T13 | Window ends are considered chronologically and weights accumulate in rich-file order. The two reversed fixtures cut at 35 seconds and produce no early cut, respectively. Both chronological controls cut at 18 seconds. | PASS |
| T14 | The exponential diagnostic overflows in the narrow-temperature-spread witness and fails the cell. A forbidden leg ID in the leave-one-out map fails its cell for both ordinary pressure and a valid bound pressure key. The other cell still runs. | PASS |
| T12 and prior controls | The 91-key digest, pressure states, bound IDs, prior audit cases, isolated decoder checks, and outer-stream digit scan pass. | PASS |

The 50 focused tests and `git diff --check` passed. Receipt checks follow the pinned runner's return-code and exception recording. Phase names come from its MLX runtime, Align workload, and thermal gate writers. [Runner step writer](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L477-L498), [runner exit writer](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L647-L654), [MLX phase writer](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/joulewise/adapters/mlx_runtime.py#L775-L847), [Align workload phases](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/joulewise/align/apple/workload.py#L504-L610), [thermal phases](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/joulewise/align/apple/thermal_gates.py#L649-L651)

No twin class is left open from the supplied audit 4 reproductions. Astra's paired acceptance census remains pending. P01 through P03 and the primary Stage 1 refusal checks belong to their existing owners. [RL-184 §3.2](https://github.com/mpmdw/JouleWise/blob/61e8c9c2ccfd023c82e0da048dd89f4ed854a5bc/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L21104-L21119)
