# `lm-interim-01` input binding, 2026-11-25

The lead assigned this Phase Gate [AGENT] task for the RL-217 A and E.1 packet. Mission M0 found no active stop card. The branch starts at the #971 merge and carries the lead's Air pinning commit `8e0a0ab4b`.

The draft manifest registers `/Volumes/JW-EXT/lm-interim-01-root`. Every span has a record of its close under RL-217 A, with its full inventory digest bound through [RS593](https://github.com/mpmdw/JouleWise/commit/ff17d783e). For `dev-05-s02`, RS437 misprinted the suffix. The close marker carries the matching digest ([RS591](https://github.com/mpmdw/JouleWise/commit/86576174b)). The research lead confirms the binding in the B.2 packet.

`validate --repo . --span-ledger … --roster-out …` resolved 14 spans across five fit dates and wrote `/Volumes/JW-EXT/scratch/inputbind-stage-1125/roster.json`. The local dates use America/Los_Angeles and the staged attempt names, cross-checked against the public close dates. `dev-05-s01` uses a2. The draft `LOOKS.json` row commits the manifest and roster hashes. The CLI's `row` command applies after the look is committed and the verdict file exists.

Draft validation reported `ok lm-interim-01 (draft); open placeholders: 0`. The read-only `pin` check found zero changes. `check-inputs --roster …` bound 2,855 files across all 14 spans and returned pin-list SHA-256 `a3f0e7fce89c229edfa918fa7d0efa4a0de1ed6bc1388e3a85f038876f8b8ee9`. The focused test compared each ordered inventory with the staged sums text and checked the same round trip against the committed digests. The checks used repository files and staged metadata. The lead retained custody-side verification. CI runs the full suite.

The lead places the staged roster at `/Volumes/JW-EXT/lm-interim-01-root/lm-interim-01/roster.json`, registers `execution_host`, and runs the rules-3/4 rehearsal under RL-217 E.1.
