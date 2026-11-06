# ALIGN token admission budget and deadman

Authority: council FINAL-DESIGN §2.2 and B3, available with
`git show origin/lane/2026-11-05-align-window-council:docs/align/council-2026-11-05/FINAL-DESIGN.md`.
This implementation is B3,
based on pilot-9 `c9a0a3943`. It does not fill R0/R1 slots or authorize a run.

`EpisodeSpec` carries two fields that must be enabled together or both omitted.
Campaign generation preserves them in `workload_profile.prompt_text`:

```json
{
  "max_tokens": 4096,
  "max_context_tokens": 40960,
  "max_episode_decode_tokens": 8192,
  "deadman_s": 1086
}
```

These are illustrative values, not selected operating parameters. R1 chooses
the model's budget and measures its member intercept `I_m`. The deadman is
`(1750 - I_m) / 1.13544` seconds of episode time; 1086 seconds is the council's
transferred-intercept example. The code requires finite positive values, bounds
`deadman_s` strictly below `1800 / 1.13544` (about 1585.29 s), and caps the decode
admission threshold at the configured context cap, at most 40960. That permissive
bound uses a zero member intercept; the kit/R1 lane must enforce the tighter
model-specific formula above, floors, multiples of 1024 and member sizing.

Before turn k, cumulative emitted decode must be strictly below the episode
budget. Each admitted turn retains its full `max_tokens` cap. Thus a budget
of 8192 and a cap of 4096 can admit a turn at cumulative count 8191; it can
finish at 12287. The next admission records `episode.decode_budget:<k>`.
Reasoning tokens and emitted stop-token IDs are included in native decode
counts. Prefill does not consume the decode admission budget. The existing
context guard reserves the rendered prompt (cached prefix plus fresh prefill)
and the full per-turn decode cap within the effective context limit. New cells
also enforce the 40960 ceiling when the model's native limit is unread. The
design specifies no separate cumulative prefill budget, so none was added.

`deadman_s` is measured from the episode start stamp, excluding prior idle and
warmup. It is checked at admissions and stream token boundaries; an opt-in
stream cap also stops endpoints that ignore the requested per-turn cap.
For `SystemClock`, POSIX `ITIMER_REAL` interrupts a blocked stream read,
prompt render or tool call. The handler and timer are restored on exit. This
requires the main thread and no pre-existing active real timer; incompatible
environments fail the episode rather than run without interrupt coverage.
Fake clocks use boundary checks. An uninterruptible device/OS call can still
defer Python signal handling; the outer runner member cap remains necessary.

The deadman records `episode.deadman:<k>`, retains returned tokens, prevents
further tool dispatch, skips scoring and fails the member with partial custody
through the existing runtime-failure path. Its stop condition remains
`episode.deadman` rather than `endpoint_error`. The failed bundle retains
`align_episode.json`, transcript, turns, runtime events and `align_failure.json`.
The ALIGN desk prints the distinct end state and excludes deadmen from both
registered residual fits and episode-scope alternatives. All-member diagnostic
views may still show them. A decode-budget stop is normal and does not exclude.

For opt-in specs, `hardware.token_budget` in the episode and the matching
`episode_outcome.token_budget`/runtime metadata record decode and prefill counts,
cached context counts, configured limits, indexed stop reason and `incomplete`.
The desk exposes this record and includes the new controls in configuration
grouping. Policy identities include the fixed limits, without realized counts.

The limits are opt-in; the code does not infer model names or fabricate R1
values. The legacy `max_episode_seconds` cannot be combined with either new
field. Unset fields are omitted from serialized specs, identities and member
records. The four Qwen3-30B anchor configs are unchanged and retain their
120-second guard, checked only before the next turn. Contrast turn-count
stopping is unaffected. No pinned controller, monitor, SMC or MLX runtime
code changed, and no rebind is needed.

Verification: `python3.13 -B -m unittest tests.align.test_decode_budget` uses
synthetic endpoints only. It covers exact/overshooting admission, speed
independence, context reservation, partial/zero-token deadmen, stalled streams,
config and identity propagation, desk compatibility and frozen anchor config
hashes plus legacy guard behavior. Real-model and hardware qualification remain
R0/R1 work for the lead.
