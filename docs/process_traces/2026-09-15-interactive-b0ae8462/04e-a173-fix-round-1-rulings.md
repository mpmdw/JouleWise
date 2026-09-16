# 04e — A173 fix-round-1 rulings (magistrate b0ae8462, 2026-09-15 21:40 PDT)

From the Astra contract refuter (04c, AMEND: one blocker) and the Opus execution lens (04d, AMEND: no blocker; live run
classified the interactive session IDLE and the headless magistrate + Codex seats foreign for a stub, exit 0 for real
classes; 200 fuzz inventories, 0 exceptions).

**R1 (04c blocker)** — the OWN activation's root (the caller's interactive or `claude -p` ancestor) is classified like
an idle session: its idle helpers (`codex mcp-server`, `codex-code-mode-host`, shells) are exempt, its WORKLOAD
descendants still make the census busy, and a sibling `codex exec` seat outside the caller's ancestry stays foreign.
Regression pair: own root + idle MCP helpers → clear; own root + sibling `codex exec` outside ancestry → blocked.
**R2 (04d SF1)** — runbook uses `"$PY" -B -m joulewise.arm_census` at both sites; exit 1 documented as "the census did
not run" (preserve transcript; not a busy verdict). **R3 (04d SF2)** — `timeout=30` on the discovery probe;
`TimeoutExpired` → diagnostic (unknown → idle). **R4 (04d SF3)** — three coverage cells: unreadable hit outside an
exempt tree reads IDLE; `endswith("/t3-code/dist/cli.js")` pinned against `/opt/t3-code/dist/helper.js` and
`/x/t3-code-fork/y.js`; pgrep exit 2 stdout is a diagnostic, never hits. **R5 (04d nit)** — collapse repeated
"discovery unknown row" diagnostics to a count (the headless magistrate's prompt argv produced 700 of them) and take
the hit set from a numeric `pgrep` form so a `<digits> <text>` continuation line cannot inject a pid.
