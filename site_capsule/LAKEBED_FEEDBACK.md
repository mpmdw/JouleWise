# Lakebed Feedback Log (for the Lakebed maintainer)

Lakebed is an alpha demo deployment environment. Standing rule (Ed,
2026-07-09): every issue encountered while interacting with Lakebed —
validator rejections, runtime surprises, CLI friction, docs gaps — is
logged here in verbose detail so the developer maintaining Lakebed gets
actionable field reports. Agents: append a dated entry at every Lakebed
interaction that hits ANY friction; include exact commands, exact error
text, environment (CLI version if discoverable), what was expected, what
happened, the workaround used, and a severity guess.

Entry format:

```
## YYYY-MM-DD — <one-line summary>
- Command / action:
- Expected:
- Observed (verbatim output where possible):
- Workaround:
- Severity for a production user: blocker / major / minor / paper-cut
- Suggestion for the maintainer:
```

---

## 2026-07-08 — Backfill: issues from the initial capsule deploy session

Recorded retroactively from the 2026-07-08 deploy session (full
narrative: `docs/run_reports/2026-07-08-lakebed-deploy.md`). Each was a
real deploy blocker or near-blocker:

1. **Deploy validator scans server source textually, including
   comments.** Tokens `process`, `fetch`, `globalThis`, `self` are
   rejected wherever they appear — even in comments or string literals.
   Workaround: `\u00XX`-escape the tokens in the packer and use a
   Unicode-escaped `fetch` identifier. Severity: major (false positives
   on comments make the rule hard to discover; error should say which
   byte offset/line matched). Suggestion: parse, don't grep; or at
   minimum exempt comments and report match locations.
2. **Unbounded `for(;;)` loops rejected by the same textual scan.**
   Workaround: bounded decode loop. Severity: minor once known;
   paper-cut discoverability. Suggestion: document the full deny-list.
3. **>2 MiB request bodies rejected; ~1 MiB artifact cap.** Embedded
   woff2 fonts exceeded it; `pack_capsule.py` defaults fonts OFF for
   Lakebed. Severity: minor (fair limit, but the limit should be in the
   CLI error message with the observed size).
4. **Production runtime has no global object.** Code that feature-tests
   via a global crashes only in production, not locally. Severity:
   major (local/prod divergence). Suggestion: ship a local emulation
   mode matching the production runtime.
5. **`Response` constructor broken in production runtime**
   (`Buffer.alloc` error). Workaround: manual `DecompressionStream` +
   `TextDecoder` instead of `new Response(stream)`. Severity: major.
6. **Bundler inlines an imported binding's module source at every
   reference site** — N references = N copies, blowing the size cap.
   Workaround: alias the import once into a local. Severity: major
   (silent size multiplication). Suggestion: dedupe module inlining.
7. **`npx lakebed auth login` is browser-interactive only** — no
   headless/token path, so automated agents must hand off to a human.
   Severity: minor for demos, major for CI. Suggestion: device-code or
   token auth.

## 2026-07-09 — No new Lakebed defects this session

`build_site.py`/`pack_capsule.py` regen ran clean (0.29 MiB capsule).
The deploy step itself was deferred to Ed for approval-policy reasons on
the agent side — not a Lakebed issue. No new platform behavior observed.
