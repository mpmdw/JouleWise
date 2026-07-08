# Run Report — Site Observatory: Data-Driven Status Frontend (2026-07-08)

**Outcome:** the generated half of `docs/site/` is no longer rendered
markdown in a skin. `scripts/build_site.py` was rewritten around
fail-closed parsers over the live process docs, and three new pages
present project state as a designed observation experience: `status.html`
(console strip + five-station "flight recorder" spine: what is true now /
what changed / what happens next / what could invalidate it / where the
evidence lives), `roadmap.html` (queue lane cards, next-two flight plan,
do-not-do interlock), `record.html` (sessions timeline, binding
decisions, council timeline). The library became a grouped Sources layer;
doc pages gained TOC sidebars and scrolling table wrappers. Merged as
PR #13 under the standing merge-with-review authority.

## Honesty mechanics (the load-bearing part)

- Every number and state on a generated page derives from parsing the md
  sources at build time; parsers exit nonzero naming component, source,
  and expected pattern. No hand-typed data survives review (two hardcoded
  narrative strings were caught and derived; an invented `meta` lane
  state and a council-index fallback were caught by counterreview and
  removed — absence of a lane tag now renders as absence).
- P2-017 closed: per-source provenance stamps (`git log -1 -- <source>`
  plus a `+ uncommitted` dirty marker) on every generated page/component.
- The fail-closed parser found real source drift while being built: the
  council-log index table was missing its C-011 row (fixed at source).
- The final-head gate HELD the merge because the site truthfully rendered
  a stale RUN_STATE test count (564 vs the grown 576) — the site cannot
  be more honest than its sources; the source was fixed and re-stamped.

## Process trace (layers and unique catches)

- Dual-prior 5.5 design round (instrument-maximalist vs editorial): both
  converged on extend-don't-replace, status hub, fail-closed parsing;
  lead synthesized console-strip + flight-recorder and cut invented-
  metric components (gauges, radar).
- 5.5 implementation (branch `stream/site-observatory`), then two Codex
  IMAGE critique rounds (7 then 8 screenshots; 16 findings r1, per-item
  verification r2) — Ed directed image-heavy analysis to Codex
  (higher-res, cheap tokens); encoded in the codex-delegation skill,
  with a `codex-run -i` passthrough added (variadic `--image` trap
  documented).
- Lead root-caused the persistent mobile overflow after tool-fighting
  (stale-CSS caching ×3, corrupted preview emulation, headless Chrome's
  ~500px minimum window): a grid item with `margin: 0 auto` disables
  stretch alignment, so max-content sizing won — one-line fix; every
  page now fits 390px (iframe-measured).
- 14-image Codex visual sign-off: SHIP; hand-page regression check
  clean.
- Fresh 5.5 counterreview: 2 blockers (both fail-closed honesty), 3
  should-fixes (derived latest-report, attribute escaping, escaped
  excerpt) — all fixed; 12 parser tests.
- Final-head 5.5 pass: HOLD on the stale-source test count (above) —
  the gate's unique catch; fixed in this bookkeeping.

## Verification

- Suite: `Ran 576 tests, OK (skipped=10)` (564 + 12 parser tests),
  lead-run.
- Real build (`npx marked`) green; `--no-marked` sandbox path green.
- Mobile: all pages scrollWidth ≤ 390 at 390px (iframe-measured);
  desktop layouts visually verified.
- Degree framing corrected reader-facing (undergraduate CS capstone, not
  master's) in the site hero and PROJECT_STATUS.

## Next

Unchanged: P2-015 then P2-006 in one quiet window [QUIET-MAC]. The site
regenerates via `python3 scripts/build_site.py` (commit sources first;
stamps are per-source and dirty-aware).
