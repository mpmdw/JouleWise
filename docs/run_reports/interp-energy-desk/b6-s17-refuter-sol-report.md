Committed [the report](/Volumes/JW-EXT/jw-wt/sol-b6-s17-refuter/docs/run_reports/2026-11-10-b6-s17-refuter.md) as `729f9e704` on `b6-s17-refuter`.

- Five findings: three medium, two low.
- Quotation audit: 372 exact lines; three signing-statement lines were reflowed without changing words.
- **7b:** the arithmetic is reusable unchanged, but the inspected B6 program does not call it. Release-digest confirmation and the ruling remain with the lead.
- Static checks and `git diff --check` passed. No tests or data readers ran.

Only the report changed. Working tree clean; nothing pushed.