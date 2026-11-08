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

WP11 (supplied) binds D's six weight shards: the R0 re-run record's governed
model_artifact_identity, checked shard by shard against the HF LFS pins at
815b83c0 (configs/align/v4/qwen38-27b-8bit-hf-pins.json); the folded sha256
recomputes from the pins alone. WP18 (Mac-side) must provide X=b-e25/index16
and Y=b-e18/index14 recorded pilot-7 turn counts and the token-id fixture
digest. No configured 12-turn fallback is used for the contrast.
R0.reasoning_effort stays a placeholder until R0 passes.
R1 must select B_D, I_D, T_dead, sensors, bands, recovery cap and chunk size.
W1's g0_cap_s binds r1_slots.g0_cap_w1.value_s (LEAD-RULINGS-2 R7-2, R7-12):
clamp(ceil(1.25 * max counted gated D and X-G G0 wait), 600 s, R1 g0_timeout_s).
Unreleased G0s count at the full R1 timeout; an inconclusive X-G records
x_g_fallback. Ruling 1(f) uses this cap + max(G1 + H) + max(prefill + tool)
+ (B_D + turn_cap_tokens) / min(step-d and gated decode rates), and refuses
when that misses T_dead. Only a signed lead receipt
(registration/ruling_1f_receipt.json, LEAD-RULINGS-2 R10-2(a), drafted by
scripts/align_w1_budget_procedure.py) changes that, and only when the 600 s
rule fits at no B_D: D then arms G0* = T_dead - holds projected to 10,240
tokens - prefill/tool - 10,240 / r, below 600 s, named in
thermal_policy.g0_cap_receipt; contrast members arm their own
thermal_policy.contrast_g0_cap_s and contrast_fit on EVERY path (R11, RUN_STATE 212).
Failed/incomplete proof predeclares non-veto INCONCLUSIVE. Missing/nonpositive
available cap gives immediate G0 timeout; changed predecessor heat is disclosed.
D sizing/receipt checks remain unchanged. The kit re-derives every number.
T_dead follows lead ruling L1: min((1750 - I_D), (1800 - I_D - max_r1_tail_s
- 10)) / 1.13544, with max_r1_tail_s from r1_slots; --check asserts that
I_D + 1.13544 T_dead + max_r1_tail_s + 10 <= 1800.
Missing numeric controls are null and invalid as executable EpisodeSpecs.
The existing qwen3_5 endpoint selects XML tools from the model family.
Presence penalty remains the endpoint's fixed zero; sampler is 1/.95/20/0.

Window reference R: member 5 captures its last 60 s of idle before neutral
warmup (role capture); all later sidecar members consume it (role consume,
bound to member 5's run_id and config bytes). The plan records this in
runtime_requirements.window_reference and --check refuses any other roles.
W1 members run from their own configs through the plan's stage commands; the
WP15 R1 runtime (runtime_requirements.r1_runtime_entrypoint) runs R1 only.
The scaffold's campaign commands remain a skeleton pending the W1 wiring.
No synthetic sensor, reference temperature, model digest or turn count is used.

Sizing_preview.json contains A1's planning guesses only. sizing_b5.json comes
from R1 (FINAL-DESIGN B8): once registration/w1_plan.json (the R1-filled copy
of night_plan.template.json) is committed and validates, the kit derives
sizing_b5.json from its member_s (span, window, T_stream_max_s) and the
pilot-3 disk law (two copies). Until then --check and prepare refuse with
that reason. Use fit_roster with R1 measured cost estimates:
drop only 18 first, then decrease B_D by 1024 down to 6144; otherwise return
to lead. Preserve anchors, contrasts and 5/17. Requalify/freeze changed budgets.
W1 arm requires --obc-off-attested-by, --battery-log (and --window-battery-journal), --next-arm-triage and --w1-disk-config. By-day
scripts/align_v4_offloads.py verifies configured inventories; the disk config
names daytime_offload_receipt and an explicit lead-signed
daytime_offload_freshness policy (max_age_s, lead_signature); no default duration. Arm checks >=80 decimal GB
free without remounting/re-hashing the SSD. Empty offloads require explicit
offloads_owed: none. Battery arm requires fresh AC, >=99%, not charging and
|InstantAmperage| <=200 mA, retaining raw ioreg and pmset evidence (pmset is evidence only).
Top-up evidence is derived from the logged battery record, never typed: a completed charge within
30 min, or continuous float since one. --battery-log is the between-window sampler log (stopped before
the arm dwell; none runs during a window) and --window-battery-journal the window's own 1 Hz SMC capture. DC residuals print for benign members only.
R12: a window ends at authenticated terminal completion (the 59,520 s maximum is a
ceiling, not a reservation). W1/D arm also requires --next-arm-triage, the frozen
B2 list (joulewise/align/apple/v4_cadence.NEXT_ARM_TRIAGE), every entry gating.
Calibration is a fixed 8 counted windows (v4_cadence.calibration_stop, RUN_STATE 217): no
early stop, 39 eligible benign per pair after 8, else insufficient_calibration.
require_w1_ready also requires registration_receipt.json, bound to current and
committed protocol/kit/desk/estimand/deviation/U3/WP19 bytes, two admitted gate
reports and the lead signature. The committed pending template never admits.
U3 is PENDING frozen predictive derivation/OC sensitivity: explicit replay
summaries install no k or energy bar. Historical k=3 receipts cannot admit W1.
Generate wp19_receipt.json from all-turn X/Y rendering plus complete native X-G.
The numeric B window consequence and qualified full-span mount audit remain
lead-owned pending gates. R0.record_sha256 must bind sensor provenance.
R16 checks actual per-turn opportunity at the chosen B_D, never a capability guarantee.
The additive align_v4_session.py refuses prepare/install while inputs are pending.
Its desk is the parameterized pilot instrument desk; WP21 owns full U4–U6,
K-session and contrast reporting. This kit grants no arm or hardware approval.

RUN_STATE 210 / squeeze: runtime_requirements.km003c explicitly enables the
Block HAZARD_PACK driver's existing reader and supervision, before the first
idle baseline through the final member, in hazards/meter/ with closing hashes.
require_w1_ready refuses a missing/disabled/changed declaration. The v4 desk
prints per-member DC integrals and a separate five-term DC residual, labelled
SECONDARY / not yet registered. Missing coverage or one dropped counter makes
that member's DC channel missing and never changes powermetrics eligibility.
See docs/align/squeeze/KM003C-ALIGN.md for custody and remaining live gates.

`night_plan.template.json` is the fail-closed Window-1 planning sheet for the
pilot night-plan v5 family; it is not itself a run_night plan (prepare writes
that). Every R1 value, including every member cost, is an explicit
`PENDING_R1` value. Validate a separately filled copy with
`python3 -B scripts/validate_align_v4_w1_plan.py <copy>`; the command refuses
any placeholder or disagreement with registration/inputs.json (and with
r1_slots.json max_r1_tail_s), applies lead ruling L1 to T_dead, validates the
template's own heavy/per_turn gate policy, and recomputes both the 26,940 s
span cap and 44,640 s window maximum. After any kit regeneration, rebuild the
template's member bindings with `--regenerate-template`. The template is not
custody, an arm receipt, or an installation.
