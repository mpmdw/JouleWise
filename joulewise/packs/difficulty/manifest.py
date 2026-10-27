"""Seeded uniform MATH selections, reusing the existing importer."""
import hashlib
from collections import Counter
from pathlib import Path

from joulewise.benchmark_import_math import (
    COMMIT, REPO_URL, PROMPT_TEMPLATE, PROMPT_TEMPLATE_ID, SCORER_ID,
    _expected_rendered_prompt, eligible_records, select_items, select_pilot,
)

SELECTION_KEYS = ("schema_version", "pack_version", "seed", "selection_domain", "sizes", "selections")


def selections_only(manifest):
    return {key: manifest[key] for key in SELECTION_KEYS}


def build_manifest(config, rows):
    eligible, _ = eligible_records(rows)
    excluded, flags = set(), []
    if config["exclude_importer_sets"]:
        pilot = select_pilot(eligible)
        excluded.update(row["source_item_id"] for row in pilot)
        excluded.update(row["source_item_id"] for row in select_items(eligible, pilot, 128))
    for filename in config["exclude_item_id_files"]:
        try:
            text = Path(filename).expanduser().read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise ValueError(f"cannot read configured exclusion file {filename}: {exc}") from exc
        excluded.update(line.strip() for line in text.splitlines() if line.strip())
    domain = "joulewise.packs.difficulty.selection.v2/" + config["seed"]

    def ordered(pool, tag):
        return sorted(pool, key=lambda row: (
            hashlib.sha256((domain + "/" + tag + "/" + row["source_item_id"]).encode("utf-8")).hexdigest(),
            row["source_item_id"]))

    levels, selections, counts = {}, {}, {}
    for level in range(1, 6):
        pool = [row for row in eligible if row["level"] == level and row["source_item_id"] not in excluded]
        levels[level] = ordered(pool, "level")[:config["n_per_level"]]
        if len(levels[level]) < config["n_per_level"]:
            flags.append(f"short_level:{level}:{len(levels[level])}")
    for mode in ("off", "on"):
        selections[mode] = {role: {} for role in ("bench", "energy")}
        counts[mode] = {role: {} for role in ("bench", "energy", "holdout")}
        for level in range(1, 6):
            bench = ordered(levels[level], f"bench/{mode}/{level}")[:config["sizes"][mode]["bench"][str(level)]]
            energy = ordered(bench, f"energy/{mode}/{level}")[:config["sizes"][mode]["energy"][str(level)]]
            energy_ids = {row["source_item_id"] for row in energy}
            for role, subset in (("bench", bench), ("energy", energy)):
                selections[mode][role][str(level)] = [row["source_item_id"] for row in subset]
                if len(subset) < config["sizes"][mode][role][str(level)]:
                    flags.append(f"short_selection:{mode}:{role}:{level}:{len(subset)}")
            for role, subset in (("bench", bench), ("energy", energy),
                                 ("holdout", [row for row in bench if row["source_item_id"] not in energy_ids])):
                counts[mode][role][str(level)] = dict(sorted(Counter(row["subject"] for row in subset).items()))
    selected_sets = {(mode, role, level): set(selections[mode][role][str(level)])
                     for mode in selections for role in selections[mode] for level in range(1, 6)}
    items = []
    for index in range(max(map(len, levels.values()), default=0)):
        for level in range(1, 6):
            if index >= len(levels[level]):
                continue
            row = levels[level][index]
            item = {"order": len(items), "item_id": row["source_item_id"], "level": level,
                    "subject": row["subject"], "problem": row["problem"],
                    "prompt": PROMPT_TEMPLATE.replace("{problem}", row["problem"]),
                    "expected_answer": row["expected_answer"]}
            item.update({f"{role}_{mode}": row["source_item_id"] in selected_sets[mode, role, level]
                         for mode in selections for role in selections[mode]})
            items.append(item)
    return {"schema_version": "difficulty_manifest.v2", "pack_version": config["version"],
            "seed": config["seed"], "selection_domain": domain,
            "source": {"dataset": "math", "repo_url": REPO_URL, "commit": COMMIT},
            "scorer_id": SCORER_ID, "prompt_template_id": PROMPT_TEMPLATE_ID,
            "n_per_level": config["n_per_level"], "sizes": config["sizes"],
            "selections": selections, "subject_counts": counts,
            "level_counts": {str(level): len(pool) for level, pool in levels.items()},
            "excluded_count": sum(row["source_item_id"] in excluded for row in eligible),
            "flags": flags, "items": items}


def rendered_prompt(item, thinking):
    return _expected_rendered_prompt(item["problem"], thinking)
