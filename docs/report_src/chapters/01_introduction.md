# Introduction

Running large language models locally turns energy from an operator's line
item into a user-facing decision problem. A person choosing between a 1.5B
model and a 122B mixture-of-experts model on the same laptop is implicitly
choosing a per-request energy cost, a battery budget, and a thermal envelope
— yet the numbers needed to make that choice are rarely measured on the
actual deployed stack. JouleWise exists to make that decision measurable.

The intended consumers, per the capstone scope contract
(`docs/contracts/capstone_scope.md`), are practitioners deploying local LLM
inference on Apple-silicon-class hardware, and course staff assessing whether
the measurement instrument itself is sound. Both need per-request energy on
an exact, named stack — not vendor TDP figures or cloud-scale averages.

Latency and throughput alone are insufficient for this decision: two stacks
can deliver similar tokens per second at very different package power, and
idle draw can dominate short requests. Energy per request, with an explicit
idle-subtracted basis, is the quantity that maps to battery and cost.

Auditability is this project's warrant rather than its empirical
contribution: every reported number traces to an immutable run bundle, a
validation verdict, and a claims-index row, so a reader can independently
verify what was measured before deciding whether to believe it. The
empirical findings themselves are deliberately scoped by the claims ladder
(`docs/contracts/claims_ladder.md`).
