# Filler launch bands, November 19, 2026

Tier 0 evidence on the Air for RL-171 §3. Resumed after the 12:27 PST host pause. A fresh fetch showed a clean branch at audit base `9a5a9be30027d90a5ec69f1820b3f8a081d664de`, with no previous push, PR, or uncommitted output from the interrupted turn.

- Pin A admits both tested roster sizes with one of the two arguments throughout the day except **10:50:01–13:14:59 PST** (8,699 seconds). The default argument's last evening admit is **23:48:10** for one leg and **23:03:10** for two. Use the alternate starting the next second. The one-leg f2-stab-01 sample agrees with the one-leg f2-inst-02 sample, and both two-leg instrument samples agree.
- Pin B admitted every sampled t0 for f2-stab-15 L003 with the window omitted. Passing `02:00-02:35` refused **00:22:31–02:34:59 PST**. Its two no-window mocks ran 1/1 legs at 11:30 and 01:50, finishing at 12:28:42.560 and 02:48:42.560 respectively. Pin A's alternate-window mock ran 2/2 legs at 01:45, finishing at 03:06:52.860. All three returned rc 0 with zero blackout holds. These are synthetic adapter timings and outcomes.
- The item 406 boundaries reproduced to the second on Nov 17, 20 and 21. The filler sweeps covered both Nov 20 and 21 at minute resolution and bisected the transitions. The native frozen-path validators and explicit-t0 plan probes agreed with the sweep. The picker passed all 112 boundary probes in each of the four Bash/zsh execution and sourcing combinations.
- The local checks exercised the evidence scripts and both pins' native planning and mock entry points. The change is scoped to evidence and this report, so local verification used those focused checks. Both detached worktrees were clean after verification.

[Band tables and decision table](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/filler-clock-bands/README.md) · [Verification record](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/filler-clock-bands/VERIFICATION.json) · [Item body for the lead to post](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/filler-clock-bands/ITEM-BODY.md)

## NEEDS_SPEC

RL-172 §0 says to name a window on every campaign pin. RL-175 §C.4's amendment is scoped to qualification spans. Before posting, the lead should explicitly reconcile RL-172 §0 with the proposed no-window instruction for f2-stab-15 and -16. The observations and the proposed item are ready for that decision.
