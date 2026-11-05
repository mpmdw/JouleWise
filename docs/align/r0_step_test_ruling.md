# R0 step-test duration ruling — 2026-11-05

Authority: laptop lead, 2026-11-05, ruling supplied with the PR #661 task.
This supersedes **FINAL-DESIGN-AMENDMENT-1 §A5, R0 item 3** only as to the
60 s SMC step. Amendment source: commit
`6eb1ff5be31bec330ae5af262c2b4c7601e7755e`,
`docs/align/council-2026-11-05/FINAL-DESIGN-AMENDMENT-1.md` (available in local
Git objects; the council tree is not integrated here).

The conflict is with **PR #658's written selection rule**, source commit
`274fec2cb2fcc301798c91140e51c244c2469988`,
`docs/align/smc_temperature.md`, “Written selection rule”, items 3–4:
S_slow requires tau >120 s and tau below the load duration. A 60 s load cannot
resolve that class. That source also limited tau to the recovery duration;
the ruling below replaces that restriction with recovery confirmation.

The ruled profile is **idle 300 s, load 900 s, idle recovery 600 s**: 1,800 s,
about 30 minutes at the desk. Durations are configuration (`smc_step` in
[the R0 config](r0_desk.example.json)), with those defaults.

- **S_slow:** tau strictly in (120 s, 900 s), fitted on the load phase and
  confirmed against the recovery using the fixed load-fit prediction.
- **S_fast:** tau strictly below 30 s, fitted on the first 120 s of load.
- Load duration must be at least the 900 s tau upper bound. Shorter loads
  refuse with `smc_step.load_below_tau_upper_bound` before capture or model work.

Implementation retains #658's amplitude >3 idle SD, R2 >=0.8 and >=90% valid
one-second slots per phase. Recovery confirmation uses the existing R2 >=0.8
bar, without refitting tau. The R0 readability bar remains >99% valid slots
at 1 Hz over at least 600 s. All sensor locations remain PROVISIONAL.

Matching note for **#658**: use the same 300/900/600 default CLI profile and
load-only slow fit / first-120-s fast fit; confirm slow recovery without the
old `tau < recovery duration` filter. #661 passes all three durations explicitly
and independently re-ranks the SHA-256-authenticated #658 journal according to
this ruling. The #658 capture code is not integrated or changed by this commit.
No PR comment was posted (offline lane).

The [runbook](r0_desk_runbook.md) budgets the additional 30 min and a journal
allowance of 16 KiB per 1 Hz slot (29,491,200 bytes by default), in addition to
80 decimal GB free before W1. The row size is a planning estimate, to be checked
on the measurement Mac. Capture timeout is configured phase total plus 600 s.

Synthetic tau 60 s / 400 s traces resolve under this profile and confirm on
recovery. A 60 s sensor cannot satisfy S_fast's <30 s rule, so that pair alone
leaves selection inconclusive. A separate synthetic 20 s / 400 s pair verifies
complete role selection. These are fixture checks, never live qualification.
