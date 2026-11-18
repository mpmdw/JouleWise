# RL-183 dated transfer closure · 2026-11-18

Both transfer NEEDS_SPEC items closed at confirmed remote implementation
head `224cb92d3aeb637e0ab276cf8bc1d54de989616b` on
`align/2026-11-18-transfer-block`. At readback, GitHub CI was pending
with zero check runs and zero commit statuses.
[Execution report](2026-11-18-rl183-transfer-execution.md)

| Closed item | Implementation | Regression | Result |
| --- | --- | --- | --- |
| RL-183 §3.1 final-window midnight substitution | `82642f760`, `224cb92d3` | Place 20 retains its ordinal on the verified substitute close date. D+1 can serve it or expire to missed. An existing transfer t0 on D prevents a second block. | PASS |
| RL-183 §3.2 transfer variant and release boundary | `82642f760`, `224cb92d3` | The new dispatcher validates the closed v2 shape and its hash-only finalization. The pinned v1 validator refuses the v2 draft. Synthetic execution verifies the three exact success names, pre-read exit 2, and post-read exit 1 with only the two-line stderr notice, empty stdout and no public JSON. | PASS |

The qualification registration at `0b09bee24` still carries
`PENDING:CODE` in its v2 schema hash slot. The transfer draft also
carries the pending hash. Transfer stays in v2. Its current schema
SHA-256 is `1e12a6a2c7eea9f42ba8e68dc651429f2da8f093f2a2078c33e26eeebdba3210`.

The synthetic release regressions used an alias for the enclosing
fixture directory. They exercised the registered filenames directly.
The fixture census remains unverified because the environment denied
`ps` access. This closure is docs-only. Verification used the focused
draft, dispatch and synthetic worker checks and generated-state check.

All 20 spans remain drafts pending effective freeze 2, scientific
registration and dated lead issue. The separate 120-leg cap and the
existing 132-leg campaign cap still apply. The lead's next step is
scientific registration, followed by scorer integration and final
pins. The final manifest goes to Fable for a cold pass before the
terminal read.
