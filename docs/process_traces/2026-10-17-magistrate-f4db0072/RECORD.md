# Magistrate activation f4db0072 (Opus 5.5, headless, 2026-10-17 from 19:08 PDT)

Launch: notice_pending []; no unread mail from Ed; open directive issues are the old 09-24/25 set (#405, #408, #416, #417, #421, #422), nothing new. No standdown request.

## Finding: the loop's pre-check could never pass under ProcessType Background

- Loop state at launch: WAIT_PHYSICS since 18:21 on hazard `instrument`. Contention passed from pre-check 000003 on (mediaanalysisd pid 21331 still `T`, 0.0%), but the instrument probe refused on every tick:

| pre-check | frames of 300 in 55 s | median interval |
|---|---|---|
| 000001 (18:10) | 237 | 218 ms |
| 000002 (18:26) | 178 | 298 ms |
| 000003 (18:42) | 197 | 259 ms |
| 000004 (18:54) | 183 | 290 ms |
| 000005 (19:08) | 180 | 299 ms |

  Bound: 300 frames within 55 s, median <= 150 ms (`joulewise/hazards/instrument.py`). The same probe and argv (`powermetrics -n 300 -i 100`, same samplers) gave 300 frames, 131 ms median in both machine tests today (MT-20261017T1735Z, MT-20261017T2215Z), which ran as Interactive night jobs. Per-frame plist size was the same (about 52 KB), so the capture did the same work, only slower.
- Cause: `configs/launchd/com.joulewise.b6loop.plist.template` sets `ProcessType Background`; the pre-check's powermetrics inherits the throttled launch context. This is the 09-19 slow-cadence defect class (244-250 ms medians under a default-ProcessType job), which is why every night job must be Interactive. The machine test never ran the loop, so it could not catch this.
- Effect on numbers: none. Collection runs in the Interactive night jobs and nothing was collected. The pre-check refused correctly, on a real hazard of its own launch context.

## Action

- Fix on the round lane: `1706257c4` on `lane/2026-10-17-b6-packs-registered` (also `fix/2026-10-17-b6loop-interactive`): template `ProcessType Interactive`, the test's assertion, and the page's description. `tests.test_b6_loop` 54/54 OK. No executed Python changes, so there is no re-pin; the measurement checkout stays at `f31aca19f`.
- 19:22 PDT: `launchctl bootout` of `com.joulewise.b6loop` (killed tick 000006 mid pre-check; no powermetrics or tick process left), re-rendered from the lane template (the only diff to the loaded plist is ProcessType), `launchctl bootstrap` rc 0; `launchctl print` shows `spawn type = interactive (4)`. The Background plist is kept at `/Users/edr/night-b6/loop/com.joulewise.b6loop.plist.background-f4db0072`.
- Any later re-render of the loop plist must use the lane template (or the f31aca19f template with Interactive substituted).
- Live check: pre-check 000007, the first under Interactive (19:22), captured 300 of 300 frames over a 39 s timestamp span (mean 130 ms; plist 15.7 MB), matching the machine tests (300 frames, about 40 s, 131 ms median). Its verdict was not yet written when this activation exited, so the next activation reads it.
- The activation exited right after this commit so the pre-check and collection are not held by a live agent.
