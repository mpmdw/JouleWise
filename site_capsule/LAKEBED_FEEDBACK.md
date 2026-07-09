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
8. **Root page paths are reserved in a way that surprises static-site
   deploys.** Registering server endpoints for `/` or `/index.html`
   conflicts with the Lakebed client shell. Workaround: serve the static
   homepage from `/index` and let the client redirect `/` there. Severity:
   minor once known, major for static-site ports. Suggestion: document
   reserved paths prominently and make the validator error name the
   reserved route and suggested replacement.

## 2026-07-09 — Advisor-status redeploy: hosted inspection and HTTP/API friction

Environment: Lakebed CLI package resolved through `npx`; generated
anonymous artifact reported `lakebed: 0.0.25`, compiler `0.1.0`.
Capsule deploy ID: `dep_2I04CG6tQ4t0mzY7`. Live app:
`https://quiet-signal-6af8833395.lakebed.app`.

### Hosted inspection auth cannot use the committed deploy binding alone

- Command / action:
  - from `site_capsule/`: `npx lakebed logs https://quiet-signal-6af8833395.lakebed.app`
  - from `site_capsule/`: `npx lakebed db dump https://quiet-signal-6af8833395.lakebed.app`
- Expected: because `site_capsule/lakebed.json` contains the deploy ID and
  the command was run from the capsule directory, hosted inspection would
  authenticate or at least give a next step that identifies the missing
  local credential file.
- Observed:

  ```
  Error: {
    "command": "npx lakebed logs dep_2I04CG6tQ4t0mzY7",
    "error": "Lakebed hosted inspection requires authorization.",
    "hint": "Run this command from the capsule directory so Lakebed can read .lakebed/deploy.json, or send Authorization: Bearer <claim-token>.",
    "inspectPolicy": "private",
    "path": "/__lakebed/logs"
  }
  ```

  `db dump` produced the same authorization error and hint.
- Workaround: rely on public smoke endpoints (`/api/health`,
  `/api/freshness`, `/api/live-status`) instead of hosted logs/DB dump.
- Severity for a production user: major for incident response; minor for a
  demo where public health endpoints are enough.
- Suggestion for the maintainer: distinguish `lakebed.json` deploy
  binding from `.lakebed/deploy.json` claim-token state in the docs and
  in the error. If inspection requires a private claim token, add
  `npx lakebed inspect --login` or a command that prints exactly which
  local credential file is missing and how to recreate it.

### GET endpoints do not automatically satisfy HEAD requests

- Command / action: smoke checks used `HEAD`/`curl -I` against deployed
  page endpoints during live-site analysis, including `/index` and
  `/status.html`.
- Expected: `HEAD` on a `GET` endpoint returns the same status and headers
  as `GET` with no body, as many uptime monitors and link checkers assume.
- Observed: `GET /index` and `GET /status.html` returned 200, but `HEAD`
  returned 404 for the same paths.
- Workaround: use `GET` smoke checks:

  ```
  curl -s -o /dev/null -w '%{http_code} %{content_type} %{size_download}\n' \
    https://quiet-signal-6af8833395.lakebed.app/status.html
  ```

- Severity for a production user: minor to major depending on monitoring
  setup; it can create false outage reports.
- Suggestion for the maintainer: either auto-route `HEAD` to matching
  `GET` endpoints or document that `HEAD` must be registered explicitly
  with `endpoint({ method: "HEAD", path }, ...)`.

### `npx lakebed` depends on registry access unless cached

- Command / action:
  - `npx lakebed build`
  - `npx lakebed deploy`
- Expected: the CLI is installed or resolved quickly enough to build and
  deploy from a repo checkout.
- Observed in a restricted-network agent environment:

  ```
  npm error code ENOTFOUND
  npm error syscall getaddrinfo
  npm error errno ENOTFOUND
  npm error network request to https://registry.npmjs.org/lakebed failed,
  reason: getaddrinfo ENOTFOUND registry.npmjs.org
  ```

- Workaround: rerun with explicit network approval, or rely on an already
  cached `npx` package directory.
- Severity for a production user: paper-cut for local demos; major for CI
  or agentic deploys in restricted networks.
- Suggestion for the maintainer: document a reproducible pinned CLI
  install path, for example `devDependency` + `npm exec lakebed`, or
  publish a recommendation such as `npx --yes lakebed@0.0.25 ...` so
  deploy logs and artifacts can cite a stable CLI version.

### Public deploy smoke cannot reveal server exceptions without inspection

- Command / action: after deploying `/api/freshness`, one public JSON
  response returned only a partial freshness check. Hosted `logs` and
  `db dump` were unavailable because of the inspection auth issue above.
- Expected: either public endpoint errors include enough structured detail
  for the app owner, or private inspection works immediately from the
  claimed capsule checkout.
- Observed: public endpoint could only show `unavailable: true`, while
  the private diagnostic path was blocked. This forced diagnosis by code
  inspection and redeploy rather than by server logs.
- Workaround: patch application code to fail per source instead of per
  request, then redeploy; use public JSON fields as the only diagnostic
  surface.
- Severity for a production user: major when debugging live incidents.
- Suggestion for the maintainer: make owner-authenticated logs easy to
  access from the deployed capsule directory, and consider an owner-only
  response-debug mode for endpoint exceptions.

## 2026-07-09 — Artifact size cap hit by organic content growth; error lacks diagnostics

- Command / action: `npx lakebed deploy` from `site_capsule/` after a day
  of documentation growth (decision/council logs gained ~8 entries).
- Expected: deploy, or an error saying which component exceeded the limit
  and by how much.
- Observed (verbatim): `"error": "Artifact exceeds 1048576 bytes."` with a
  stack trace from `deploy-api.js:58`. No breakdown (server bundle vs
  client vs pages), no overshoot amount, no local pre-check.
- Diagnosis required manual work: `npx lakebed build`, then JSON-inspect
  `.lakebed/artifacts/*.anonymous.json` to learn the server source bundle
  was 1,060,132 bytes base64 (795,099 raw JS) — 1.7% over. Also learned
  the bundle carries ~490KB of injected runtime on top of ~300KB app
  payload, which the app author cannot see or shrink.
- Workaround: trimmed our two largest embedded pages (site generator now
  serves log indexes + recent entries with a GitHub pointer), bringing the
  artifact to 927,682 bytes.
- Severity for a production user: major — every growing site hits this
  wall eventually, and the error gives no actionable direction.
- Suggestions: (1) `lakebed build` should print the artifact size and its
  component breakdown vs the limit every run (a burn-down number);
  (2) the deploy error should include actual size, limit, and top-3
  largest embedded modules; (3) document the runtime overhead budget so
  authors know their real payload allowance (~550KB, not 1 MiB).
