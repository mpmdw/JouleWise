# Cold-gate packet (D-176 second gate): the integrated pack-night launch head — is it fit for the first pack-bound night, and how must the production-root census treat the running deployment?

Assembled mechanically by the interactive magistrate at 2026-09-08 ~16:30 PDT. Trigger: synthesis exhibit C item 6
("a second cold gate on the integrated head and the real plan bytes precedes the first pack-bound night"), and Opus
exhibit A finding 1 (a design contradiction discovered at integration). Checkout = the integrated head
int/2026-09-08-d176-seats-2-3 at 4d72e524 (main + seat 2 producer + seat 3 consumer + integration).

## Q1 — the census self-collision (exhibit A finding 1)
The roots/locators ruling (exhibit B) froze PRODUCTION_CUSTODY_ROOTS as roles with derivations, including `repo_runs`
= CLONE_DERIVED `Path(arm_readiness.__file__).resolve().parents[1]/"runs"` and `deployment_measurement_root` = INVENTORY
(every entry of configs/production_custody_inventory.json), and made the consumer refuse a T0_REHEARSAL whose plan
`measurement_root` lies under any production root. But the consumer runs as
`<measurement_root>/.venv/bin/python <measurement_root>/scripts/launch_window.py` (scripts/run_night.py ~:1256), so
`repo_runs` is `<measurement_root>/runs` and `_contains(measurement_root, repo_runs)` is always true; and if the running
deployment is inventoried, equality also refuses. Bench-verified by Opus. Exhibit B explicitly excluded ARM-context roots
from the census for the same self-collision reason but did not carry the exclusion to `measurement_root`.
Charge: rule the census semantics for the RUNNING deployment. Candidates: (a) exempt `repo_runs` and the running
deployment's own inventory entry from the `measurement_root` DISJOINT check (identify "own" by realpath equality of
`arm_readiness.__file__`'s checkout with the inventory entry); (b) drop `measurement_root` from the DISJOINT set
entirely (custody_root, ledger, backups still checked); (c) require a rehearsal to run from a DEDICATED rehearsal clone
that is itself NOT inventoried (then the census is honest: the rehearsal's measurement_root is disjoint from every
production deployment) and make the consumer refuse if the running checkout IS inventoried; (d) other. For each, state
the failure-mode test: can a rehearsal (or a mis-purposed pack night) ever write into a retained production runs root,
ledger, or backup? Which candidate keeps the property by construction rather than by inventory maintenance?

## Q2 — fitness of the integrated head for the first pack-bound night
Exhibit A §(6) lists what remains unexecuted at this head: real ARM minting, real ARM verify, real T-0 authoring, the
driver→launcher process boundary (Popen/execve) — all stubbed in the end-to-end fixture; seat 4 (rehearsal purpose /
G7) unwritten so the §6 G7 fence stands; the inventory HEAD-pins itself against the RUNNING checkout's git HEAD (so the
measurement clone must hold these exact bytes at its HEAD and be an inventory entry — re-triggering Q1); the shipped
inventory names a v5 clone path that does not yet exist; the Ed-owned privileged-anchor control still NEEDS-ED.
Charge: rule (1) which of these MUST be closed before the first pack-bound night and which may be observational
residue; (2) whether the inventory's HEAD-pin against the running checkout is sound for a measurement clone that is
re-cut at a reviewed head (state the exact check the clone must satisfy at arm time); (3) the minimal live rehearsal
that discharges the stubbed seams (a rehearsal-class pack night on a dedicated rehearsal clone with a real ARM mint and
a real Popen handoff, presenting its rehearsal-class GO to the production launcher to record the G7 class refusal —
or a narrower shape). Read the code at this checkout (scripts/run_night.py, joulewise/night_gate.py,
joulewise/arm_readiness.py around the cited lines, joulewise/t0_rehearsal.py, configs/production_custody_inventory.json,
tests/test_launch_window.py ~:2031) to ground each ruling with file:line.

Write the ruling to ./coldgate-packet/10-coldgate-fable-ruling.md (under 900 words, numbered decisions Q1.x/Q2.x, one-line
verdict last). NOT EXECUTED for anything unverifiable.
