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
Missing numeric controls are null and invalid as executable EpisodeSpecs.
The existing qwen3_5 endpoint selects XML tools from the model family.
Presence penalty remains the endpoint's fixed zero; sampler is 1/.95/20/0.

WP15 must wire the thermal launcher and custody for R: 5 captures its last
60 s of idle before neutral warmup; all later sidecar members consume it.
The scaffold's campaign commands remain a skeleton pending that wiring.
No synthetic sensor, reference temperature, model digest or turn count is used.

Sizing_preview.json contains A1's planning guesses only. No arm-compatible
sizing_b5.json is supplied. Use fit_roster with R1 measured cost estimates:
drop only 17 first, then decrease B_D by 1024 down to 6144; otherwise return
to lead. Preserve anchors, contrasts and 5/17. Requalify/freeze changed budgets.
The additive align_v4_session.py refuses prepare/install while inputs are pending.
Its desk is the parameterized pilot instrument desk; WP21 owns full U4–U6,
K-session and contrast reporting. This kit grants no arm or hardware approval.
