# Dated transfer audit round 1 repair · 2026-11-18

The branch matched remote head `b5dddebd57d1ef152dd09cda14fc609b3b852fbd`
at intake. The HIGH and MED reproductions failed the new regressions on
that head. The LOW entry recorded passing checks.

| Audit finding | Repair and regression | Result |
| --- | --- | --- |
| HIGH · transfer inherits retired stop scopes | The kit generator supplies transfer-specific RL-179 F-6 prose. Watcher loss raises an alarm only. A changed frozen path removes only the affected entry from admission. The regression finds the retired wording in every old kit and tests that an arbitrary replacement in the qualification template cannot leak into a new transfer kit. | PASS |
| MED · a second t0 on date 20 collapses into the same served row | Both date-map entry points validate observed starts before building the set of served days. Regressions cover identical and distinct timestamps on the same day, a duplicate on an earlier day, an off-roster start, and a 21st distinct start. A valid 20-start map still has 20 served rows. | PASS |
| LOW · kit layout, draft halt and look shape | Revalidated all 20 kit, queue and plan sets on the pinned tooling. All 60 checks before, at and after queue expiry halted. The look remains a draft with the closed output shape. The synthetic span completed six legs with zero stops. | PASS |

The generator validates candidate kit and queue bytes in seat-local
scratch before writing the regenerated drafts. It updates all 20 kit,
queue and item bindings, the date-place roster, the look's kit and
roster references and the draft ledger hash. Machine stop fields,
runner pin and seeded leg rosters retain their prior byte values.
The kit has the same scope interpretation as the shared Issue and Check.

- Kit 01 SHA-256 `a018bf05c67e0417cb2a3e5cf0f8a3073a7fac9502670f823b10d868539cefd3`
- Date-place roster SHA-256 `173f75c45475ab2c2cd01402d570d5c8740cbf8c24fa85c5127b76b22dc4e01f`
- Look draft SHA-256 `e63575eeb9614a417e0de07ca087df8eb7608d706b1fb30924be6ee92078c3a8`

This repair is draft data and desk tooling. Verification used the pinned
regeneration, focused regressions, look validation, synthetic runner
and worker tests, and the generated-state check. The fixture census
remained unverified because the environment denied `ps` access.

All 20 spans remain drafts pending effective freeze 2, scientific
registration and dated lead issue. The next step is the independent
delta audit of this repair. The final manifest still needs Fable's
cold pass before the terminal read. All audit round 1 findings have
a disposition and neither RL-183 NEEDS_SPEC item reopens.
