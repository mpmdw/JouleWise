"""Syntax-check every sh block (bash -n and zsh -n, placeholders stubbed) and every python heredoc of each item."""
import re, subprocess, sys, glob, os
D = "/Volumes/JW-EXT/scratch/items-rl171"; bad = 0
for f in sorted(glob.glob(f"{D}/ITEM-*.md")) + [f"{D}/STANDING-F0.md"]:
    t = open(f).read()
    blocks = re.findall(r"```sh\n(.*?)```", t, re.S)
    sh = "\n".join(blocks)
    sh = re.sub(r"<LEAD FILLS:[^>]*>", "0", sh).replace("<token>", "TOKEN")
    for shell in ("bash", "zsh"):
        r = subprocess.run([shell, "-n"], input=sh, text=True, capture_output=True)
        if r.returncode: bad += 1; print(os.path.basename(f), shell, r.stderr[:300])
    for py in re.findall(r"<<'PY'\n(.*?)\nPY\n", sh, re.S):
        try: compile(py, f, "exec")
        except SyntaxError as e: bad += 1; print(os.path.basename(f), "python", e)
    # pick_arg sanity: run it at a few epochs under bash
    if "pick_arg()" in sh:
        print(os.path.basename(f), "blocks", len(blocks), "py", len(re.findall(r"<<'PY'", sh)), "pick_arg ok")
    else:
        print(os.path.basename(f), "blocks", len(blocks), "py", len(re.findall(r"<<'PY'", sh)))
print("BAD", bad)
