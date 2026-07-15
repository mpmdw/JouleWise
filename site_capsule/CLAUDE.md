# JouleWise Site Capsule Agent Instructions

This directory contains the Lakebed capsule for the generated JouleWise site.
Repository-level `AGENTS.md` remains authoritative.

## D-068 site boundary

- No agent ever regenerates or deploys the site. Deployment is Ed-manual.
- When front-facing state changes, refresh or report against
  `docs/site/DRIFT.md`; automation informs, and Ed decides when to use the
  manual runbook in `site_capsule/README.md`.
- Do not treat the `deploy` script in `package.json` as agent authorization.

## Capsule code boundaries

- Put client code in `client/`, server code in `server/`, and runtime-neutral
  shared code in `shared/`.
- Use `lakebed/server` only from server code and `lakebed/client` only from
  client code.
- Keep `shared/` free of DOM, Node, environment, and Lakebed runtime imports.
- Do not add a separate CSS, PostCSS, or Tailwind build pipeline.
