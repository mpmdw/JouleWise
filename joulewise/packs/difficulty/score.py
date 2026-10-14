"""Post-hoc attempt scoring; every generation yields one bench row."""
from joulewise.benchmark_import_math import score_response

BENCH_COLUMNS = ("model", "mode", "item_id", "level", "outcome", "correct",
                 "prompt_tokens", "generated_tokens", "cap_hit", "flags")


def score_generations(manifest, config, generations):
    items = {item["item_id"]: item for item in manifest["items"]}
    configurations = {(entry["model"], entry["mode"]) for entry in config["configurations"]}
    seen, result = set(), []
    for generation in generations:
        row = generation if isinstance(generation, dict) else {}
        model, mode, item_id = (str(row.get(key, "")) for key in ("model", "mode", "item_id"))
        item = items.get(item_id)
        flags = []
        if item is None:
            flags.append("unknown_item")
        if (model, mode) not in configurations:
            flags.append("unknown_config")
        text = row.get("response_text")
        if not isinstance(text, str) or not text:
            flags.append("missing_text")
            text = ""
        finish = row.get("finish_reason")
        status = {"stop": "succeeded", "length": "capped", "error": "runtime_failed"}.get(
            finish if isinstance(finish, str) else "", "runtime_failed")
        if finish not in ("stop", "length", "error"):
            flags.append("unknown_finish_reason")
        key = (model, mode, item_id)
        if key in seen:
            flags.append("duplicate")
        seen.add(key)
        tokens = [row.get(key) for key in ("prompt_tokens", "generated_tokens")]
        if any(type(value) is not int or value < 0 for value in tokens):
            flags.append("bad_number")
        tokens = [value if type(value) is int and value >= 0 else None for value in tokens]
        outcome = score_response(text, item["expected_answer"], runtime_status=status,
                                 enable_thinking=mode == "on")["outcome"] if item else "malformed"
        result.append(dict(zip(BENCH_COLUMNS, (model, mode, item_id,
                      item["level"] if item else None, outcome, int(outcome == "correct"),
                      *tokens, int(finish == "length"), ";".join(flags)))))
    return result
