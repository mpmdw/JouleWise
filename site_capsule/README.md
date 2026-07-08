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
  content modules under `server/content/` (gzip+base64 page bodies, one
  shared stylesheet, per-source provenance stamps parsed from the pages).
- `server/index.ts` registers one HTTP endpoint per page (canonical path +
  aliases), a `/style.css` endpoint, `/api/freshness` (live), `/api/health`.
- `client/index.tsx` is a tiny Preact shell that redirects `/` → `/index`
  (Lakebed reserves `/` and `/index.html` for the client shell).

## Deploy / update (the canonical flow)

```sh
# from the repo root — regenerate the site first if docs changed:
python3 scripts/build_site.py
python3 scripts/pack_capsule.py          # fonts OFF by default (see note)
cd site_capsule && npx lakebed deploy    # updates the existing deployId
```

`lakebed.json` pins the `deployId`, so `deploy` updates the same URL. The
deploy is **claimed/owned** (needed for outbound `fetch` to GitHub); an
anonymous deploy would disable freshness.

## Fonts note (why the default is fonts-off)

Lakebed caps the deploy artifact at 1 MiB. The embedded woff2 fonts alone
exceed that, so `pack_capsule.py` defaults to the CSS fallback stacks
(Iowan Old Style / Georgia serif, SF Mono / Menlo mono, system sans) — the
editorial character holds. `python3 scripts/pack_capsule.py --fonts` inlines
the real Fraunces / IBM Plex faces for hosts without the size limit.

## Freshness behavior

`/api/freshness` compares each source's baked commit against
`GET /repos/mpmdw/JouleWise/commits?path=<source>&sha=main`, DB-cached for
5 minutes. It **fails soft**: on any fetch/rate-limit error it returns
cached data if present, else `{unavailable: true}` — the page renders the
identical snapshot with no drift banner, and never claims "not moved" when
it could not actually check. Set `GITHUB_TOKEN` in `.env.lakebed.server`
for higher rate limits (optional; the public API works unauthenticated).

## Platform constraints worked around (so future edits don't reintroduce them)

The Lakebed deploy validator textually scans server source (comments
included) and rejects `process`, `fetch`, `globalThis`, `self`, unbounded
`for(;;)` loops, and >2 MiB request bodies; the production runtime lacks a
global object and has a broken `Response` constructor (`Buffer.alloc`).
Hence: gzip+base64 page bodies emitted as chunked string literals, token
escaping in the packer, a Unicode-escaped `fetch` identifier, a bounded
decode loop, and a manual `DecompressionStream` + `TextDecoder` path (no
`Response`). Keep these if you edit `server/index.ts`.
