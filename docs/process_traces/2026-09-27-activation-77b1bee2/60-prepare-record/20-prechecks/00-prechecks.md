# Prepare step: value-blind pre-checks (ruling 71 §8, statement item 2, PREDECESSOR-PATH-01 C1–C6)

Run by magistrate 77b1bee2, 16:20–16:25 PDT 09-27. No B value was read.

| Check | Result | Evidence |
|---|---|---|
| §8.1 finding S1 ruled | PREDECESSOR-PATH-01 ruled (b); owner told (C4, Gmail `1a0e52ead28598fe`) | `../11-predecessor-path-ruling.md` |
| §8.2 repair merged; run checkout advanced | PR #436 merged as `e7c8bcc6`. The W2 run checkout was fast-forwarded from `722f7bd1` to `e7c8bcc6`, with `722f7bd1` an ancestor; `configs/calibration` is unchanged in that range. Tool sha256 `21b2eea8…060c` | `run-commit.txt`, `tool-sha256.txt` |
| §8.3 / item 2(d) the four digests | ledger `23f72c37…1c7d`, pin `5dbac530…aad5`, W1 verdict `07bcc13b…35a2`, W2 verdict `51f49618…46ec`: **all equal** | `prechecks-3-6.txt` |
| §8.4 head pin committed | `git status` clean; last commit `722f7bd1` | same |
| §8.5 interpreter | `<run checkout>/.venv/bin/python`, a symlink to python3.13, **Python 3.13.1**; the same interpreter the harvest dry run used | same |
| §8.6 disposition registry | `ba1ba3fc…a63c` equals the pinned `DISPOSITION_REGISTRY_SHA256` | same |
| C3 predecessor file | `9c3a29f6…fe16`; a regular file, not a symlink; clean | same |
| pre-registration | `81b65f08…ddf1` | same |
| §8.7 R8 probe at the merged commit | 24 rows with a locator, 12 valid; **12/12 accepted**; `/Users/edr`, the W1 night directory and `/` each refused 12/12 | `check7-r8-probe.txt` |
| §8.8 custody digest list, before | 20,527 files in the W1 and W2 night directories; list sha256 in `check8-custody-digests-before.sha256`, full list at `~/night-archive/prepare-25g83-77b1bee2/` | the list |
| §8.9 `--out` | `/Users/edr/night-archive/prepare-25g83-77b1bee2/candidate_acceptance_25g83.json`, a new file outside `configs/` and outside `/Users/edr/night-custody` | — |
| §8.10 dry run and owner replies | dry run rc 0: W1 and W2 `battery=pass recorded=pass`, finalized 12/12, valid 6+6, excluded none, prefix pending 0, **admissible yes**. Gmail `from:claude2.glaring610@passmail.net is:unread`: none at 16:25. Directives unchanged; no stand-down request | `check10-dryrun.txt` |
