#!/usr/bin/env python3.13
"""RL-156 §4.2 hand checks (2) and (3), for the lead, on the AIR's copy of a Part C OUT (never on the MBP).

Re-evaluates a completed Part C run with PR #783's evaluator (branch align/2026-11-14-rl153-followups,
head 561f4dd05) and prints ONLY: the re-evaluation, the run's own recorded evaluation (the same object
the magistrate's Check prints), a line-by-line comparison, and whether X_G's ``episode_flags`` is a list.

It mirrors #783's ``align_r1_followup_kit.smoke_part_c`` after the members ran: the same member result
fields (bundle names, slots' N_chunk, x7, deadman T_dead, episode_flags) and the same bundle readers
(``facts_from_bundle``, ``step_d_facts``, ``rl145_prints.bundle_prints``). Energy/slot fields that sit in
``smoke_part_c.json``'s members block are loaded in-process, as the evaluator loads them, and never printed.

Usage (Air):
  python3.13 -B reeval_partc_783.py /Volumes/JW-EXT/partc-desk/<OUT basename>
    [--tree /Volumes/JW-EXT/jw-wt/pr783-eval]      # a clean worktree detached at 561f4dd05
"""
import argparse, json, os, socket, subprocess, sys
from pathlib import Path

PR783_HEAD = "561f4dd0558284c753eb9c579ab3d8eee2ab140a"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path, help="Air copy of the Part C OUT (holds part-c/smoke_part_c.json)")
    ap.add_argument("--tree", type=Path, default=Path("/Volumes/JW-EXT/jw-wt/pr783-eval"))
    a = ap.parse_args()
    if "mbp" in socket.gethostname().lower() or Path("/Users/Shared/JouleWise/measurement-mode").exists():
        sys.exit("REFUSE: run on the Air's copy, never on the measurement Mac")
    out = a.out.resolve()
    if not str(out).startswith("/Volumes/JW-EXT/"):
        sys.exit(f"REFUSE: {out} is not an Air copy under /Volumes/JW-EXT")
    head = subprocess.check_output(["git", "-C", str(a.tree), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(a.tree), "status", "--porcelain"], text=True).strip()
    if head != PR783_HEAD or dirty:
        sys.exit(f"REFUSE: --tree must be a clean checkout of {PR783_HEAD} (got {head}, dirty={bool(dirty)})")
    os.environ.setdefault("JW_B5_SYNTHETIC_ONLY", "1")
    sys.path.insert(0, str(a.tree))
    from scripts import align_r1_part_c as part_c
    from scripts.align_r1_followup_kit import PART_C_GATED_D, PART_C_X_G
    from joulewise.align.apple import r1_runtime as rt
    from joulewise.align.apple.rl145_prints import bundle_prints

    pc = out / "part-c"
    record = json.loads((pc / "smoke_part_c.json").read_text())
    members = record.get("members") or {}
    recorded = record.get("evaluation")

    step = members.get("step_d") or {}
    slots = step.get("slots")
    n_chunk = (slots or {}).get("N_chunk") if isinstance(slots, dict) else None
    step_dir = pc / rt.STEP_D_SEGMENT
    step_line = (part_c.step_d_facts(step_dir / step["bundle"], step) if step.get("bundle")
                 else {"g0_outcome": step.get("g0_outcome")})
    x_g = members.get("x_g")
    xg_flags_is_list = None if x_g is None else isinstance(x_g.get("episode_flags"), list)
    if not isinstance(slots, dict) or not isinstance(n_chunk, int):
        doc = part_c.evaluate(step_d=step_line, d_bank=None, n_chunk=n_chunk if isinstance(n_chunk, int) else 1)
    else:
        bank = members["d_bank"]
        bank_bundle = pc / PART_C_GATED_D / bank["bundle"]
        bank_facts = part_c.facts_from_bundle(bank_bundle, role="d-bank")
        bank_facts["x7"] = bank.get("x7", bank_facts["x7"])
        bank_facts["t_dead_s"] = (bank.get("deadman") or {}).get("T_dead_s", bank_facts["t_dead_s"])
        if isinstance(bank.get("episode_flags"), list):
            bank_facts["episode_flags"] = list(bank["episode_flags"])
        printed = bundle_prints(bank_bundle, estimate_tokens=True)
        x_g_facts, why = None, None
        if x_g is not None and x_g.get("bundle"):
            x_g_facts = part_c.facts_from_bundle(pc / PART_C_X_G / x_g["bundle"], role="x-g")
            if xg_flags_is_list:      # #783 (PR #777 row-2 finding 7)
                x_g_facts["x7"] = any(str(f).startswith("episode.deadman:") for f in x_g["episode_flags"])
        else:
            why = "X_G not in the run's record"
        doc = part_c.evaluate(step_d=step_line, d_bank=bank_facts, n_chunk=n_chunk, x_g=x_g_facts,
                              x_g_not_run_reason=why, printed=printed)

    def passes(ev):
        lines = (ev or {}).get("lines") or {}
        return {k: (None if v is None else v.get("pass")) for k, v in lines.items()}
    rec_p, new_p = passes(recorded), passes(doc)
    diff = sorted(k for k in set(rec_p) | set(new_p) if rec_p.get(k) != new_p.get(k))
    if (recorded or {}).get("verdict") != doc["verdict"]:
        diff.append("verdict")
    print(json.dumps({"out": str(out), "evaluator": f"PR #783 {PR783_HEAD}",
                      "check2_x_g_episode_flags_is_list": xg_flags_is_list,
                      "recorded_verdict": (recorded or {}).get("verdict"), "pr783_verdict": doc["verdict"],
                      "line_pass": {"recorded": rec_p, "pr783": new_p},
                      "differs": diff,
                      "pr783_evaluation": doc}, indent=1, sort_keys=True, default=str))
    print("CHECK3:", "DIFFERS -> both runs to the research lead (RL-156 §4.2 item 3)" if diff else "same verdict and lines")
    if xg_flags_is_list is False:
        print("CHECK2: X_G episode_flags NOT a list -> tonight's X_G X7 line is not relied on (RL-156 §4.2 item 2)")


if __name__ == "__main__":
    main()
