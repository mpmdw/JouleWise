"""Post-hoc attempt scoring; every generation yields one bench row."""
import math
import re
from collections import Counter

from joulewise.benchmark_import_math import score_response

BENCH_COLUMNS = ("model", "mode", "item_id", "level", "attempt", "outcome", "correct",
                 "prompt_tokens", "generated_tokens", "cap_hit", "flags")


def repetition_loop(units, detector):
    """Greedily count disjoint occurrences of each fixed-span tail window."""
    tail_length = math.ceil(len(units) * detector["tail_fraction"])
    tail = units[len(units) - tail_length:]
    span, repeats = detector["min_span"], detector["min_repeats"]
    windows = {}
    for start in range(len(tail) - span + 1):
        window = tuple(tail[start:start + span])
        count, last = windows.get(window, (0, -span))
        if start >= last + span:
            count += 1
            if count >= repeats:
                return True
            windows[window] = count, start
    return False


def _incoming_flags(value):
    flags = set()
    if isinstance(value, str):
        values = value.split(";") if value else []
    elif isinstance(value, list):
        values = value
    else:
        return {"bad_flag"}
    for flag in values:
        if isinstance(flag, str) and re.fullmatch(r"[a-z0-9_.:-]+", flag):
            flags.add(flag)
        else:
            flags.add("bad_flag")
    return flags


def score_generations(manifest, config, generations):
    items = {item["item_id"]: item for item in manifest["items"]}
    configurations = {(entry["model"], entry["mode"]) for entry in config["configurations"]}
    seen, result = Counter(), []
    for generation in generations:
        row = generation if isinstance(generation, dict) else {}
        model, mode, item_id = (str(row.get(key, "")) for key in ("model", "mode", "item_id"))
        item = items.get(item_id)
        flags = _incoming_flags(row.get("flags", []))
        if item is None:
            flags.add("unknown_item")
        if (model, mode) not in configurations:
            flags.add("unknown_config")
        text = row.get("response_text")
        if not isinstance(text, str) or not text:
            flags.add("missing_text")
            text = ""
        finish = row.get("finish_reason")
        status = {"stop": "succeeded", "length": "capped", "error": "runtime_failed"}.get(
            finish if isinstance(finish, str) else "", "runtime_failed")
        if finish not in ("stop", "length", "error"):
            flags.add("unknown_finish_reason")
        if finish == "error":
            flags.add("runtime_failed")
        key = model, mode, item_id
        attempt = row.get("attempt", 1 + seen[key])
        seen[key] += 1
        if type(attempt) is not int or attempt < 1:
            flags.add("bad_number")
            attempt = None
        tokens = [row.get(key) for key in ("prompt_tokens", "generated_tokens")]
        if any(type(value) is not int or value < 0 for value in tokens):
            flags.add("bad_number")
        tokens = [value if type(value) is int and value >= 0 else None for value in tokens]
        ids = row.get("generated_token_ids")
        if not isinstance(ids, list) or any(type(value) is not int or value < 0 for value in ids):
            ids = text.split()
            flags.add("loop_check_words")
        if repetition_loop(ids, config["loop_detector"]):
            flags.add("repetition_loop")
        outcome = score_response(text, item["expected_answer"], runtime_status=status,
                                 enable_thinking=mode == "on")["outcome"] if item else "malformed"
        result.append(dict(zip(BENCH_COLUMNS, (model, mode, item_id,
                      item["level"] if item else None, attempt, outcome, int(outcome == "correct"),
                      *tokens, int(finish == "length"), ";".join(sorted(flags))))))
    return result
