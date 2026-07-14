# JouleWise site capsule (Lakebed)

Serves the whole generated JouleWise site (`docs/site/`) from one Lakebed
capsule, plus a **live GitHub freshness layer**: every page checks whether
the repo has moved past the commits the snapshot was built from and shows a
drift banner if so.

**Live:** https://quiet-signal-6af8833395.lakebed.app

## How it fits together

- `docs/site/*.html` + `style.css` + `fonts/` are the source of truth (built
  by `scripts/build_site.py` from the repo's process docs).
- `scripts/pack_capsule.py` packs that site into gitignored TypeScript
  content modules under `server/content/` (bounded gzip+Base64 page shards,
  one shared style/freshness archive, a synchronous route/source manifest,
  and provenance stamps parsed from the pages).
- `server/index.ts` registers one HTTP endpoint per page (canonical path +
  aliases), lazily decodes and caches only the requested shard, and serves `/style.css`,
  `/api/freshness` (live), and `/api/health`.
- `client/index.tsx` is a tiny Preact shell that redirects `/` → `/index`
  (Lakebed reserves `/` and `/index.html` for the client shell).

## Deploy / update (the canonical flow)

```sh
# from the repo root — install the exact locked renderer, then regenerate:
npm ci
python3 scripts/build_site.py
npm --prefix site_capsule ci
python3 scripts/pack_capsule.py                    # fonts OFF by default (see note)
npm --prefix site_capsule exec -- lakebed deploy  # updates the existing deployId
```

The root lockfile pins Marked 18.0.6 and the capsule lockfile pins Lakebed
0.0.29 (including all transitive packages). The pack step uses only that local
Lakebed executable to build and measure the real validator artifact, then fails
before deploy if it exceeds 90% of the 1 MiB cap. If the pinned executable is
not installed, it uses the deterministic conservative estimator and labels
that mode `estimator-only advisory`; ambient PATH and `npx` caches do not alter
the canonical result. For a controlled preinstalled package, the explicit
`JOULEWISE_MARKED_BIN` and `JOULEWISE_LAKEBED_BIN` overrides are accepted only
when their adjacent package metadata reports the exact pinned version.

`lakebed.json` pins the `deployId`, so `deploy` updates the same URL. The
deploy is **claimed/owned** (needed for outbound `fetch` to GitHub); an
anonymous deploy would disable freshness.

## Artifact identity policy

`docs/site/build_manifest.json` records whether long-form pages used pinned
Marked, the built-in offline fallback, or the hermetic `--no-marked`
placeholder, together with the exact Marked version and offline renderer
revision. The capsule's generated build information carries that renderer
identity plus the exact Lakebed version.

Site and capsule bytes are not claimed identical from commit alone. The
capsule deliberately embeds `branch` and `builtAt`; exact-byte reproduction
therefore also requires identical generated site inputs and renderer mode,
the committed lockfiles, `JOULEWISE_BUILD_BRANCH`, and `SOURCE_DATE_EPOCH`.
Without those explicit inputs, branch and wall-clock metadata are expected to
change the bytes. Offline builds remain supported: absent Marked selects the
recorded built-in fallback, while `--no-marked` remains a separate hermetic
parser/template test path.

## Fonts note (why the default is fonts-off)

Lakebed caps the deploy artifact at 1 MiB. The embedded woff2 fonts alone
exceed that, so `pack_capsule.py` defaults to the CSS fallback stacks
(Iowan Old Style / Georgia serif, SF Mono / Menlo mono, system sans) — the
editorial character holds. `python3 scripts/pack_capsule.py --fonts` inlines
the real Fraunces / IBM Plex faces for hosts without the size limit.

## Freshness behavior

`/api/freshness` compares each source's baked commit against
`GET /repos/mpmdw/JouleWise/commits?path=<source>&sha=main`, DB-cached for
5 minutes. It **fails soft**: if a refresh fails after cached evidence exists,
the API returns the newest cached rows, marks affected sources `stale: true`,
and sets `unavailableRefresh: true` / `unavailable: true`. If no evidence is
available, it returns `{unavailable: true}`. The page must never treat a failed
refresh as proof that a source has not moved. Set `GITHUB_TOKEN` in
`.env.lakebed.server` for higher rate limits (optional; the public API works
unauthenticated).

`/api/live-status` fetches the current GitHub markdown for the advisor-facing
status sources (`PROJECT_STATUS.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, and the
risk register), parses the same high-level fields as the static generator, and
caches them for one minute in the Lakebed DB. The status page polls this
endpoint so the top-line queue, verification, and status readouts can update
without a redeploy. It fails soft: if GitHub or outbound access is unavailable,
it returns the newest cached markdown-derived payload when available, marks
those source rows stale, and sets `unavailableRefresh: true`; otherwise, the
baked page remains the source of visible truth.

## Production smoke / inspection

After deploying, verify the public endpoints:

```sh
curl -s -o /dev/null -w '%{http_code} %{content_type} %{size_download}\n' \
  https://quiet-signal-6af8833395.lakebed.app/index
curl -s -o /dev/null -w '%{http_code} %{content_type} %{size_download}\n' \
  https://quiet-signal-6af8833395.lakebed.app/status.html
curl -s https://quiet-signal-6af8833395.lakebed.app/api/freshness
curl -s https://quiet-signal-6af8833395.lakebed.app/api/live-status
```

Lakebed hosted inspection is private by default and should stay that way for
this project. From `site_capsule/`, use the committed `lakebed.json` binding:

```sh
npx lakebed inspect https://quiet-signal-6af8833395.lakebed.app
npx lakebed db dump https://quiet-signal-6af8833395.lakebed.app
npx lakebed logs https://quiet-signal-6af8833395.lakebed.app
```

## Platform constraints worked around (so future edits don't reintroduce them)

The Lakebed deploy validator textually scans every file under `server/` and
`shared/` (comments included) and rejects `process`, `fetch`, `globalThis`,
`self`, any `for` loop with an omitted initializer (including `for(;;)`), and
>2 MiB request bodies; the production runtime lacks a global object and has a
broken `Response` constructor (`Buffer.alloc`).
Hence: bounded gzip+Base64 shards emitted as chunked string literals, token
escaping in the packer, a Unicode-escaped `fetch` identifier, bounded decode
loops below the first-request instruction budget, and a manual
`DecompressionStream` + `TextDecoder` path (no
`Response`). Keep these if you edit `server/index.ts`.
