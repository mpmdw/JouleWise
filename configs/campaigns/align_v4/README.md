# ALIGN v4 W1 skeleton — PROVISIONAL, NON-CLAIM

Build: `python3.13 -B scripts/align_v4_kit.py`. Check: add `--check`.
`--check` MUST FAIL while registration/inputs.json contains pending inputs.
No study/model path is followed. All source configs come from pinned Git objects.

18 members per Amendment A1: four exact original anchors, eight 30B contrast
runs and six D runs. Midpoint follows ordinal 9. D uses seed 1 (both pairs and
conditions), development 93 at ordinal 18, and a replay of 5 at 17. Development
91–92 are reserved for R0; held-out starts at 2, excluding development indices.
The window-plan draft's D index 101 is superseded by synthesized WP16/A1.
Checkpointing is explicitly off for D throughout the series, superseding A1.

WP11 must provide D file identities/inventory/verification; WP18 must provide
X=b-e25/index16 and Y=b-e18/index14 historical max_turns and fixture digests.
No configured 12-turn fallback is used for the contrast. R0 must select effort;
R1 must select B_D, I_D, T_dead, sensors, bands, recovery cap and chunk size.
T_dead follows lead ruling L1: min((1750 - I_D), (1800 - I_D - max_r1_tail_s
- 10)) / 1.13544, with max_r1_tail_s from r1_slots; --check asserts that
I_D + 1.13544 T_dead + max_r1_tail_s + 10 <= 1800.
Missing numeric controls are null and invalid as executable EpisodeSpecs.
The existing qwen3_5 endpoint selects XML tools from the model family.
Presence penalty remains the endpoint's fixed zero; sampler is 1/.95/20/0.

WP15 must wire the thermal launcher and custody for R: 5 captures its last
60 s of idle before neutral warmup; all later sidecar members consume it.
The scaffold's campaign commands remain a skeleton pending that wiring.
No synthetic sensor, reference temperature, model digest or turn count is used.

Sizing_preview.json contains A1's planning guesses only. No arm-compatible
sizing_b5.json is supplied. Use fit_roster with R1 measured cost estimates:
drop only 18 first, then decrease B_D by 1024 down to 6144; otherwise return
to lead. Preserve anchors, contrasts and 5/17. Requalify/freeze changed budgets.
The additive align_v4_session.py refuses prepare/install while inputs are pending.
Its desk is the parameterized pilot instrument desk; WP21 owns full U4–U6,
K-session and contrast reporting. This kit grants no arm or hardware approval.

`night_plan.template.json` is the fail-closed Window-1 planning sheet for the
pilot night-plan v5 family; it is not itself a run_night plan (prepare writes
that). Every R1 value, including every member cost, is an explicit
`PENDING_R1` value. Validate a separately filled copy with
`python3 -B scripts/validate_align_v4_w1_plan.py <copy>`; the command refuses
any placeholder or disagreement with registration/inputs.json and recomputes
both the 26,940 s span cap and 44,640 s window maximum. The template is not
custody, an arm receipt, or an installation.
