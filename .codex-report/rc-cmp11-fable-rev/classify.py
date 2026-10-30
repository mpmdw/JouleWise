"""Classify sweep.out's exit-0 deletions at f9f86869e into the classes RC-CMP-9 declares (SUMMARY A4b, Sweep residue,
coverage rule names) with an UNDECLARED fallback. Each class is a path pattern; a row matching no pattern is a
producer-unconditional deletion the report does not declare."""
import re
import sys

CLASSES = [
    ("text, label, restricted (TEXT / DISCLOSURE_CONTROL rules)", r"/(text|label|restricted)$"),
    ("flag_count line and its keys (NEEDS_RULING 4: the flag catalog is not a registered source)",
     r"disclosures/.*window_lines/[a-z]+/1(/(count|family|code|blinding))?$"),
    ("machine_absent line (NEEDS_RULING 4: conditional on the meter-absent flag)", r"disclosures/.*window_lines/[a-z]+/23$"),
    ("attempt_count causes (NEEDS_RULING 3: the window index is not read)", r"block_lines/\d+/causes/"),
    ("verdict-only engine internals (declared): bundle ids, reason codes, included flag of a block, included_bundle_ids",
     r"claim-verdicts.*bundle_blocks/(blocks/\d+/(bundle_a_id|bundle_b_id|reason_codes|included)|included_bundle_ids)"),
    ("verdict-only engine internals (declared): randomization_check, variance_contributions, repeat_point_CI95",
     r"claim-verdicts.*(randomization_check|variance_contributions|repeat_point_CI95)"),
    ("verdict's own sampling/removed_block_ids members (declared; the fill's copy is bound)", r"claim-verdicts.*sampling/removed_block_ids/"),
    ("estimator internals in the disclosure copy (ESTIMATOR_INTERNALS)", r"disclosures/.*estimator/(variance_contributions|repeat_point_CI95)"),
    ("limitation notes and reason codes (declared)", r"(limitations/|reason_codes/)"),
    ("fill identity pins (IDENTITY rule): finalized_manifest ids", r"results-fill-input.*finalized_manifest/"),
    ("kept-units record identity and harvest fields (declared)", r"kept-units/.*:(attempt|catalog_sha256|harvest_pin|plan_id|roster_sha256|schema_version|sensitivity_label)$"),
    ("kept-units record cell fields (declared: identity, positions, counts the floor's n covers)",
     r"kept-units/.*cells/[^/]+/(dropped|minimum|planned|target|n_r|n_b|kept/\w+/\d+/(positions|stage_ids|stratum|unit_id))"),
    ("recompute unread fields (declared): program_sha256, unselected corpus member, GAMMA claim_usable, direction, assist strata, the recompute's own assist status word",
     r"^recompute:(program_sha256|members/ALPHA/(corpus-r1|run-a/selected)|inputs/GAMMA/claim_usable|contrasts/[^/]+/direction|disclosures/battery_assist/[^/]+/(assist_members_by_stratum|status))"),
]
rows = [line.split("exit 0: ", 1)[1].strip() for line in open(sys.argv[1]) if "exit 0:" in line]
counts, undeclared = {}, []
for row in rows:
    for name, pattern in CLASSES:
        if re.search(pattern, row):
            counts[name] = counts.get(name, 0) + 1
            break
    else:
        undeclared.append(row)
print(f"exit-0 deletions: {len(rows)}")
for name, _ in CLASSES:
    print(f"{counts.get(name, 0):5d}  {name}")
print(f"{len(undeclared):5d}  UNDECLARED")
for row in undeclared:
    print("   ", re.sub(r"[0-9a-f]{64}", "SHA", row))
