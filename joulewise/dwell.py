"""Replay the final continuous clean run in a prewindow --wait transcript."""
import re


def final_clean_dwell(stdout: str, *, minimum_s: int = 600) -> bool:
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", stdout)
    if "TIMED OUT" in text:
        return False
    starts = list(re.finditer(
        rf"continuous clean dwell 0/{minimum_s}s \(check 1\)", text))
    if not starts:
        return False
    suffix = text[starts[-1].start():]
    if re.search(r"BLOCK|not ready", suffix, re.I):
        return False
    samples = re.findall(r"continuous clean dwell ([0-9]+)/([0-9]+)s \(check ([0-9]+)\)", suffix)
    if not samples or any(int(goal) != minimum_s for _, goal, _ in samples):
        return False
    elapsed = [int(seconds) for seconds, _, _ in samples]
    checks = [int(check) for _, _, check in samples]
    return (checks == list(range(1, len(checks) + 1))
            and elapsed == sorted(elapsed) and elapsed[-1] >= minimum_s
            and re.fullmatch(r"READY after [0-9]+ min\.", suffix.strip().splitlines()[-1]) is not None)
