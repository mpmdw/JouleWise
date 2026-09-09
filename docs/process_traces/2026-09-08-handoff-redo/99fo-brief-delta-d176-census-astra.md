WRITE_SCOPE: []

# Delta re-audit — D-176 census cure (gpt-6-astra, HIGH, genre review, EXECUTION lens; NO repository writes — /tmp only; assert `git status --short` empty at the end)
Branch int/2026-09-08-d176-seats-2-3, head 07681e95; round = `git diff 93870527 07681e95`; synthesis at
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99ey-coldgate-packet-d176-second-gate/13-magistrate-synthesis.md items 1–6. EXECUTE with TemporaryDirectory fixtures and
the REAL resolver + shipped inventory: (a) measurement_root = the running checkout, un-inventoried → passes the census;
inventoried (plant it in a temp inventory) → refuses rehearsal_roots_not_disjoint: measurement_root; (b) another checkout
named as measurement_root → launcher is not the planned clone, at BOTH gate and consumer; (c) a rehearsal clone whose
basename lacks JouleWise-rehearsal- → refuses (name the code); (d) a temp git repo where a local commit deletes an
inventory entry: the pin against plan.repo_head refuses at ARM and at consumption; (e) a custody_root or ledger_path
from the inventory planted as a rehearsal custody_root → refuses DISJOINT; (f) confirm the G2-a DIAGNOSTIC_NO_PACK class
still parses and launches through the watchdog/driver paths untouched (no census consulted for unprefixed non-pack
plans); (g) the end-to-end pack fixture still passes; (h) byte-diff frozen seams vs main. Report each executed/killed with
the code observed; any NEW defect. ≤ 800 words; verdict keys per genre review; header < 8192 bytes.
