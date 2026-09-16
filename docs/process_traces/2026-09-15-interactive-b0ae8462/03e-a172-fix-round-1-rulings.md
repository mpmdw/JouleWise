# 03e — A172 fix-round-1 rulings (magistrate b0ae8462, 2026-09-15 21:40 PDT)

From the Astra contract refuter (03c, NOT LANDABLE on two authority conflicts) and the Opus execution lens (03d, LANDABLE
with one docs should-fix; 1000 fuzz cases, every denial traces to a named bound).

**R1 (03c F1) — `veto_clear` must not require reading the notice thread.** Clearance is defined over the channels the
headless magistrate is AUTHORIZED and ABLE to observe: the directive-issue channel (`gh issue list --label directive`),
`standdown.request`/STOP, and any NO relayed into a readable channel. An unreadable Gmail thread is recorded as a
limitation in the attempt directory, never a publication stop — otherwise an initial arm could not proceed headless,
which contradicts Ed's directive. Every observed NO is preserved and stops.

**R2 (03c F2) — the same-or-next-span ceiling is DROPPED from `retry_allowed`.** With the live whole-day
`INSTALL_SPANS` the ceiling can bind BEFORE `install_close_epoch` (demonstrated: attempt 23:49 → denied at 00:00 two
days later while install close is 00:15). Ed's 2026-09-15 directive ("never artificially scarce; every bound
scientific") is the more recent and stronger instruction than D-180's ceiling wording, which was written when the
install span was a 3-hour belt; the ceiling is subsumed by `install_close_epoch` + `PLAN_MAX_AGE_S`. Remove the
`outside_same_or_next_span` denial and the `install_spans` input; keep an informational sentence in the policy block
that D-180's ceiling is subsumed and why. RECORDED FOR ED as an amendment to D-180 cl.2's wording (dated addendum;
Ed may reinstate).

**R3 (03d should-fix 1)** — runbook: `latest_abort_epoch_s` is copied byte-for-byte from `attempts[-1].abort_epoch_s`,
never re-typed. **R4 (03d nit 1)** — check notice well-formedness before `notice_reused`. Dominated-bound nit accepted
as documented redundancy.
