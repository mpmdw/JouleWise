"""Seeded, subject-balanced MATH workload, using the existing importer."""
from pathlib import Path

from joulewise.benchmark_import_math import (
    COMMIT, REPO_URL, PROMPT_TEMPLATE, PROMPT_TEMPLATE_ID, SCORER_ID,
    _expected_rendered_prompt, _keyed, _subject_interleaved,
    eligible_records, select_items, select_pilot,
)


def build_manifest(config, rows):
    eligible, _ = eligible_records(rows)
    excluded, flags = set(), []
    if config.get("exclude_importer_sets", True):
        pilot = select_pilot(eligible)
        excluded.update(row["source_item_id"] for row in pilot)
        excluded.update(row["source_item_id"] for row in select_items(eligible, pilot, 128))
    for filename in config.get("exclude_item_id_files", []):
        try:
            text = Path(filename).expanduser().read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise ValueError(f"cannot read configured exclusion file {filename}: {exc}") from exc
        excluded.update(line.strip() for line in text.splitlines() if line.strip())
    domain = "joulewise.packs.difficulty.selection.v1/" + config["seed"]
    levels = {}
    for level in range(1, 6):
        pool = [row for row in eligible if row["level"] == level
                and row["source_item_id"] not in excluded]
        levels[level] = _subject_interleaved(_keyed(pool, domain), domain)[:config["n_per_level"]]
        if len(levels[level]) < config["n_per_level"]:
            flags.append(f"short_level:{level}:{len(levels[level])}")
    items = []
    for index in range(max(map(len, levels.values()), default=0)):
        for level in range(1, 6):
            if index >= len(levels[level]):
                continue
            row = levels[level][index]
            items.append({"order": len(items), "item_id": row["source_item_id"],
                          "level": level, "subject": row["subject"], "problem": row["problem"],
                          "prompt": PROMPT_TEMPLATE.replace("{problem}", row["problem"]),
                          "expected_answer": row["expected_answer"],
                          "energy_subset": index < config["energy_per_level"]})
    return {"schema_version": "difficulty_manifest.v1", "pack_version": config["version"],
            "seed": config["seed"], "selection_domain": domain,
            "source": {"dataset": "math", "repo_url": REPO_URL, "commit": COMMIT},
            "scorer_id": SCORER_ID, "prompt_template_id": PROMPT_TEMPLATE_ID,
            "n_per_level": config["n_per_level"], "energy_per_level": config["energy_per_level"],
            "level_counts": {str(level): len(pool) for level, pool in levels.items()},
            "excluded_count": sum(row["source_item_id"] in excluded for row in eligible),
            "flags": flags, "items": items}


def rendered_prompt(item, thinking):
    return _expected_rendered_prompt(item["problem"], thinking)
