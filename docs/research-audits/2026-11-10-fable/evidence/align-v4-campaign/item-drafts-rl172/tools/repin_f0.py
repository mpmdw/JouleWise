"""Re-pin STANDING-F0 from the W1-line head c3f4bacd8 to b2e01464d (RL-172b condition 3; RL-172c). Run after rl172.py.
Evidence (Air, 2026-11-15): probe/hashes-b2e01464d.txt, probe/b2e01464d-derived.txt, probe/tests-b2e01464d.log."""
import sys
sys.path.insert(0, "/Volumes/JW-EXT/scratch/items-rl171/tools")
from common import count_sub
D = "/Volumes/JW-EXT/scratch/items-rl171"; p = f"{D}/STANDING-F0.md"; s = open(p).read()
OLD, NEW = "c3f4bacd8013ca98c19cf8d41f830c701930cd41", "b2e01464d6d4fbf2901ff4d4154df9455104a12a"
TREE = "c904864e46879a4adfbdf0b467d4da1ee5928285"
V4OLD, V4NEW = "6815d1b65fee6bc67743a8905a3e61dcc8f5294b62fdd238938ca1e77b16ef57", "28caceeba15c30ca679e25c49a7c85b828096bb3b1ab3e2c676d8d1c8d10db80"
def sub(old, new, n=1):
    global s; s = count_sub(s, old, new, n)
sub("re-drafted under RL-171 by the items-rl171 builder 2026-11-15 PST, ISSUED",
    "re-drafted under RL-171 and RL-172 and re-pinned to the W1-line head `b2e01464d` (RL-172b condition 3; RL-172c) by the items-rl171 builder 2026-11-15 PST, ISSUED")
sub(f"on `{OLD}` (the merge of PR #783, head of `ops/2026-11-11-w1-presign`), in the staged worktree `/Users/edr/code/jw-wt/partc-c3f4`.",
    f"on `{NEW}` (the merge of PR #790, head of `ops/2026-11-11-w1-presign`), in the staged worktree `/Users/edr/code/jw-wt/partc-b2e01464d`.")
sub("rule 6 is now the c3f4bacd8 launch window 02:35:00-22:40:00", "rule 6 is now the b2e01464d launch window 02:35:00-22:40:00")
sub(f"1. **Pin.** The full sha `{OLD}`, the 17-hash table below, the Mac-check line below and the staged worktree `/Users/edr/code/jw-wt/partc-c3f4` (item 325's smoke worktree; created by the script if absent). The lead checked these once, for item 325: the Air tests at `c3f4bacd8` (`/Volumes/JW-EXT/scratch/partc2-c3f4/tests/`, six modules OK) and the 17 hashes, which equal Mythos's independent table (`/Volumes/JW-EXT/scratch/mythos-schedule-review/partc-paths-at-c3f4bacd8.txt`). No new Air check is made for this item.",
    f"1. **Pin.** The full sha `{NEW}` (tree `{TREE}`), the 17-hash table below, the Mac-check line below and the staged worktree `/Users/edr/code/jw-wt/partc-b2e01464d` (created by the script if absent). Pre-qualified on the Air at `b2e01464d` by the items-rl171 builder, 2026-11-15: the six dry-check modules OK (`/Volumes/JW-EXT/scratch/items-rl171/probe/tests-b2e01464d.log`: 1, 31, 15, 58, 24 and 24 tests, one skip), the 17 hashes (`probe/hashes-b2e01464d.txt`: sixteen equal the `c3f4bacd8` table, Mythos's independent one; `v4_registration.py` differs by one line, below), and the bounds re-derived from these bytes (`probe/b2e01464d-derived.txt`). The six modules still run once on the MBP at this sha (Start and check).")
sub("is not `c3f4bacd8`. The lead re-issues it as part of that merge (for example PR #774's: RL-165 §9 lets a pass carry to #774's merge commit, but this item names a sha, so it is re-issued there).",
    "is not `b2e01464d`. The lead re-issues it as part of that merge (for example PR #774's: RL-165 §9 lets a pass carry to #774's merge commit, but this item names a sha, so it is re-issued there). This issue replaces the one at `c3f4bacd8` (RL-172b condition 3: re-issued at the merge commit; the W1-line head moved by #798's merge `e5b4f4f7f` and then #790's merge `b2e01464d`).")
sub("What is left is what the bytes at `c3f4bacd8` do:", "What is left is what the bytes at `b2e01464d` do (re-derived on the Air at this sha, unchanged from `c3f4bacd8`):")
sub("(run on the Air at `c3f4bacd8`: soak start 22:50:40 admitted, 22:50:41 refused, 02:34:59 refused, 02:35:00 admitted; `/Volumes/JW-EXT/scratch/items-rl171/probe/c3f4-soak-child-boundary.txt`)",
    "(run on the Air at `b2e01464d`: `OS_BATCH_WINDOW_LOCAL` 02:00-02:35, soak 1,800 s + Part C cap 9,560 s = 11,360 s; soak start 22:50:40 admitted, 22:50:41 refused, 02:34:59 refused, 02:35:00 admitted; `/Volumes/JW-EXT/scratch/items-rl171/probe/b2e01464d-derived.txt`)")
sub("Item 325's run at this commit is the counted pass that RL-149 §5 item 12 reads if it passes; runs under this item are F0 diagnostics and are compared with it.",
    "Item 325's run at `c3f4bacd8` is the counted pass that RL-149 §5 item 12 reads; it carries to `b2e01464d` (RL-172b §2: to #798's merge; RL-172c: to #790 at `ca02c76e3` and any head with tree `c904864e…`, which `b2e01464d` has), so no new counted Part C is needed. Runs under this item are F0 diagnostics and are compared with it.")
sub(f"- **Smoke commit `{OLD}`** (`origin/ops/2026-11-11-w1-presign`; merge of PR #783 head `0ec600128cb5e5040fe0dad2d30e4a10a38eae67` into `f30a97d00`). Its tree equals #783's head (`git diff 0ec600128 c3f4bacd8` is empty). It contains `f30a97d00` (PR #777's merge), `f006b7aa6` and `a6a09e6d7`. The commit, bytes, launcher CLI, runner spec and plist (`ProcessType Interactive`, `ExitTimeOut 400`) are exactly item 325's.",
    f"- **Smoke commit `{NEW}`** (`origin/ops/2026-11-11-w1-presign`; merge of PR #790, parents `e5b4f4f7f` (#798's merge) and `ca02c76e3` (#790's head)). Its tree is `{TREE}`, equal to `ca02c76e3`'s (RL-172c's tree). It contains `c3f4bacd8`, `0ec600128` (#783's head), `f30a97d00` (PR #777's merge), `f006b7aa6`, `a6a09e6d7`, `e5b4f4f7f` and `ca02c76e3`. Against `c3f4bacd8` it changes 40 files, none of them the launcher, the LaunchAgent wrapper, the smoke runner, the rehearsal driver, the Part C kit or `r1_runtime.json`: the launcher CLI, runner spec and plist (`ProcessType Interactive`, `ExitTimeOut 400`) are item 325's.\n"
    "- **Line 2 for `b2e01464d`.** CI `ci` run 43706817774 on #790's head `ca02c76e3`: completed, success. Its tree is `b2e01464d`'s (`git diff ca02c76e3 b2e01464d` is empty), so the diff over every path, frozen or not, is empty. A push run on `b2e01464d` itself (43712204542) was queued at re-pin: <LEAD FILLS: its conclusion, if finished>. **Frozen-path diff `c3f4bacd8` → `b2e01464d` over the 17 asserted paths:** one file, `joulewise/align/apple/v4_registration.py`, +1 line (`EXECUTED_CLOSURE` gains `joulewise/align/apple/v4_desk_seal.py`, a W1 desk path that Part C never imports, RL-172b). `R1_EXECUTED_SOURCES` (the ten condition-13 paths) is unchanged, and `verify_r1_executed_sources` returns the new full sha.\n"
    "- **Re-derived from the bytes at `b2e01464d` (Air, `probe/b2e01464d-derived.txt`):** the soak child still refuses a soak start in (22:50:40, 02:35:00); the launcher's minimum for `--fresh-soak --parts C` is still 12,180 s (`r1_minimum_seconds('C', True)`; `MAX_DESK_SECONDS` 43,200); so the launch window stays 02:35:00-22:40:00 (rule 6), with the 20-min gap after F0 (rule 9) unchanged.")
sub("- **Condition-13 paths at `c3f4bacd8`**", "- **Condition-13 paths at `b2e01464d`**")
sub("The 17 hashes, as in item 325:", "The 17 hashes at `b2e01464d` (sixteen as in item 325; `v4_registration.py` new):")
sub("| Path | sha256 at `c3f4bacd8` |", "| Path | sha256 at `b2e01464d` |")
sub(V4OLD, V4NEW, 2)
sub("  `verify_r1_executed_sources` at `c3f4bacd8` returns the full sha.", "  `verify_r1_executed_sources` at `b2e01464d` returns the full sha (Air, 2026-11-15).")
sub("skip them if item 325's Start and check recorded all six OK, or if `$CUSTODY/standing-f0/tests-ok-c3f4bacd8` exists;",
    "skip them only if `$CUSTODY/standing-f0/tests-ok-b2e01464d` exists (item 325's run was at `c3f4bacd8` and does not count here);")
sub("WT=/Users/edr/code/jw-wt/partc-c3f4\n", "WT=/Users/edr/code/jw-wt/partc-b2e01464d\n")
sub("cd /Users/edr/code/jw-wt/partc-c3f4\n", "cd /Users/edr/code/jw-wt/partc-b2e01464d\n")
sub('  git -C "$WT" diff --quiet 0ec600128cb5e5040fe0dad2d30e4a10a38eae67 HEAD || { echo "STOP: tree differs from PR #783\'s head"; return 1; }',
    f'  test "$(git -C "$WT" rev-parse \'HEAD^{{tree}}\')" = {TREE} || {{ echo "STOP: tree is not RL-172c\'s {TREE[:9]}"; return 1; }}')
sub('git diff --quiet 0ec600128cb5e5040fe0dad2d30e4a10a38eae67 HEAD || { echo "STOP: tree differs from PR #783\'s head"; exit 1; }',
    f'test "$(git rev-parse \'HEAD^{{tree}}\')" = {TREE} || {{ echo "STOP: tree is not RL-172c\'s {TREE[:9]}"; exit 1; }}\n'
    'git merge-base --is-ancestor C3F4FULLSHA HEAD\n'
    'git merge-base --is-ancestor e5b4f4f7fbc05d3c1ff661356867f95a24e0cf9a HEAD\n'
    'git merge-base --is-ancestor ca02c76e3b06118a6bcb5d612f034c93ceafb003 HEAD')
sub('sys.exit("STOP: outside 02:35:00-22:40:00, the c3f4bacd8 soak child\'s window (rule 6, RL-171)")',
    'sys.exit("STOP: outside 02:35:00-22:40:00, the b2e01464d soak child\'s window (rule 6, RL-171)")')
sub("It is VOID as soon as the W1-line head is not `c3f4bacd8` (the lead re-issues it with that merge)", "It is VOID as soon as the W1-line head is not `b2e01464d` (the lead re-issues it with that merge)")
sub("A launcher refusal at c3f4bacd8 is recorded", "A launcher refusal at b2e01464d is recorded")
n = s.count(OLD)
s = s.replace(OLD, NEW).replace("C3F4FULLSHA", OLD)
open(p, "w").write(s)
left = [l[:140] for l in s.split("\n") if "c3f4" in l]
print(f"STANDING-F0 re-pinned: {n} full-sha replacements; c3f4 lines left (historical):", len(left))
for l in left: print("   ", l)
