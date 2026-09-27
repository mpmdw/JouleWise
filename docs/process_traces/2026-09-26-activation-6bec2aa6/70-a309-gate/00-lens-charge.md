# A309 BFGD-VERDICT-MERGE-LIVENESS-01 — review lens charge (read-only)
WRITE_SCOPE: []

**Candidate:** commit `87aad39c7c8d543afc252395797a948e3b4373da` on `fix/2026-09-26-bfgd-verdict-merge-liveness`, one commit on top of main `64e39bb9`; your working tree is that commit. Review `git diff 64e39bb9 87aad39c7c8d543afc252395797a948e3b4373da`, which touches `joulewise/battery_float.py` `load_committed_verdict` and `tests/test_battery_float.py`.

**Authority:**
- The dictated closure, which the candidate must implement exactly: `/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-8e43cfa7/10-liveness/ex-01-dictated-closure-M1.md`.
- The seat brief: `.../10-liveness/00-seat-brief.txt`.

**Context.** `load_committed_verdict` authenticates a committed harvest battery-float verdict file before calibration issuance. A forged, rewritten or wrongly-merged verdict that loads as authentic would let a battery-confounded window issue a calibration, which is a false number. An honest verdict that fails to load blocks issuance, which fails closed.

**Your lens** is one of:
- **EXECUTION** (Sol): run the tests yourself. Build adversarial git histories in /tmp that try to make a forged or altered record load: renames, merges that rewrite the path, octopus merges, a merge that deletes and re-adds, a cherry-pick of the adding commit, a record whose adding commit is on a side branch merged with -s ours, submodule and symlink tricks, CRLF/whitespace. Report every history that loads when it should not, or refuses when it is honest.
- **CONTRACT** (Opus): check the diff line by line against the dictated closure, and every caller of `load_committed_verdict` / `authenticate_committed_verdict` for a changed contract. Check the claim in the comment that "a merge that rewrites the record is caught by the adding-blob check", and whether `--no-renames` with `--full-history --no-merges` can hide a touching commit.

Classify each finding BLOCKER, SHOULD-FIX or NIT, with evidence (executed commands) and the exact fix. Do not edit repository files; scratch goes in /tmp.
