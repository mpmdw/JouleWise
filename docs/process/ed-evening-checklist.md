# Ed's hardware evening — ordered checklist (2026-08-17; ~1.5-2h)

Ordered pointers only; every procedure's ONE home is the runbook or the named
script. Check items off in order. Each item names the evidence it produces —
that evidence is what closes the operator-qualification rows the READY
council needs tonight.

1. **Sudoers install + both clock vectors** — install
   `scripts/joulewise-network-time.sudoers` per the D-127 route
   (runbook §5A/D-127 notes; verify the sha matches the reviewed digest
   first), then exercise BOTH vectors once (prior-state read + noninteractive
   off/on). Evidence: the captured probe outputs.
2. **Quiet-state baseline (ED-Q-L9-3) — do this EARLY** while the machine
   settles: the ~10-minute quiet-machine baseline per the qualification
   script. Evidence: the baseline capture. (This also unblocks the census
   work order.)
3. **Dress rehearsal** — the full E-4→E-9 wrapper sequence against SCRATCH
   custody (runbook §5, the `capture_t0_step.py` flow), then
   author→ARM→verify→consume against scratch (never the real packs tonight).
   Evidence: the rehearsal captures + receipts.
4. **Sampler checklist + rail probe + keyboard-backlight rows** — per the
   qualification script items (backlight: level zero, auto-adjust false,
   inactivity never; record `verification=operator_visual`).
5. **a9/a10 desk replay + ED-QUAL-L4-1 decisive replay** — desk items, can
   run while other captures settle.

When you're done, just say so (or push the evidence) — the READY-candidate
council sits overnight on the closed rows, and the morning goes to the
shakedown runs per D-139. Leave the machine in its quiet overnight state if
possible.
