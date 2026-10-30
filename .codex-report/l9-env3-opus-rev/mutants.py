"""Mutants of joulewise/whole_window.py (applied in-process only; the file on disk is untouched)."""
MUTANTS = {
    "M01_clamp_to_start": [(
        "                    Window(\n                        start_s=(window.start_s + window.end_s) / 2.0,\n                        end_s=(window.start_s + window.end_s) / 2.0,\n                    )",
        "                    Window(\n                        start_s=window.start_s,\n                        end_s=window.start_s,\n                    )")],
    "M02_drop_negative_power_guard": [(
        "            or not windows\n            or any(point.power_w < 0.0 for point in curve)\n            for curve, windows in contributions\n        )\n    ):\n        return None\n\n    origin_s",
        "            or not windows\n            for curve, windows in contributions\n        )\n    ):\n        return None\n\n    origin_s")],
    "M03_wrong_edge_sign": [(
        "                        end_s=window.end_s + eps_off_s,\n                    )\n                    for window in windows\n                ]\n                # The one ruled change",
        "                        end_s=window.end_s - eps_off_s,\n                    )\n                    for window in windows\n                ]\n                # The one ruled change")],
    "M04_mirror_drops_items": [(
        "    for item in reader.item_windows():\n        rows.append(",
        "    for item in []:\n        rows.append(")],
    "M05_restamp_all_member_gates": [(
        "                and prefix + _json_pointer_token(str(member)) == pointer\n",
        "")],
    "M06_restamp_ignores_eligibility_and_sets_eligible": [(
        "        or gate.get(\"eligible\") is not False\n    ):\n        return False\n    merged = set(existing)\n    merged.discard(_ANCHOR_ENVELOPE_UNRECORDED)\n    merged.update(reasons)\n    gate[\"reasons\"] = sorted(merged)",
        "    ):\n        return False\n    merged = set(existing)\n    merged.discard(_ANCHOR_ENVELOPE_UNRECORDED)\n    merged.update(reasons)\n    gate[\"reasons\"] = sorted(merged)\n    gate[\"eligible\"] = not merged")],
    "M07_skip_reconstruction_proof": [(
        "                if _corner_composed_anchor_shift_envelope(\n                    contributions, *bounds\n                ) != recorded:\n                    return summary\n",
        "")],
    "M08_clamp_also_zero_length_le": [(
        "                    if window.end_s < window.start_s\n                    else window\n                    for window in shifted_windows",
        "                    if window.end_s <= window.start_s\n                    else window\n                    for window in shifted_windows")],
    "M09_v062_anchor_shift_sign": [(
        "            anchor_curve[0].t - raw_curve[0].t\n",
        "            raw_curve[0].t - anchor_curve[0].t\n")],
    "M10_corner_none_continue": [(
        "            corner = _anchor_shift_envelope(corner_contributions, bundle_bound_s)\n            if corner is None:\n                return None\n            corner_envelopes.append(corner)\n\n    if common_only is None or not corner_envelopes:\n        return None\n    lower_j = min(float(envelope[\"lower_j\"]) for envelope in corner_envelopes)\n    upper_j = max(float(envelope[\"upper_j\"]) for envelope in corner_envelopes)\n    if not (\n        math.isfinite(point_j)\n        and math.isfinite(lower_j)\n        and math.isfinite(upper_j)\n        and lower_j <= point_j <= upper_j\n    ):\n        return None\n    independent_edge_bound_j = max(\n        0.0,\n        float(common_only[\"lower_j\"]) - lower_j,\n        upper_j - float(common_only[\"upper_j\"]),\n    )\n    return {\n        \"method\": ANCHOR_SHIFT_METHOD,",
        "            corner = _anchor_shift_envelope(corner_contributions, bundle_bound_s)\n            if corner is None:\n                continue\n            corner_envelopes.append(corner)\n\n    if common_only is None or not corner_envelopes:\n        return None\n    lower_j = min(float(envelope[\"lower_j\"]) for envelope in corner_envelopes)\n    upper_j = max(float(envelope[\"upper_j\"]) for envelope in corner_envelopes)\n    if not (\n        math.isfinite(point_j)\n        and math.isfinite(lower_j)\n        and math.isfinite(upper_j)\n        and lower_j <= point_j <= upper_j\n    ):\n        return None\n    independent_edge_bound_j = max(\n        0.0,\n        float(common_only[\"lower_j\"]) - lower_j,\n        upper_j - float(common_only[\"upper_j\"]),\n    )\n    return {\n        \"method\": ANCHOR_SHIFT_METHOD,")],
    "M11_restamp_keeps_unrecorded": [(
        "    merged.discard(_ANCHOR_ENVELOPE_UNRECORDED)\n", "")],
    "M12_skip_tail_refusal_early_return": [(
        "    if (\n        anchor_ctx.detail == \"post_window_trace_tail_shorter_than_anchor_bound\"\n    ):\n        # Reduce stamps no envelope gate reasons on this resolved refusal.\n        return operative\n",
        "")],
    "M13_session_calls_unclamped": [(
        "                        _rederive_operative_summary(\n                            path,",
        "                        _rederive_summary_for_authenticated_fiducial_bound(\n                            path,")],
    "M14_clamp_gross_unknown_pointer_guard_dropped": [(
        "        # A recorded member envelope the reconstruction does not know.\n        return summary\n",
        "        pass\n")],
    "M15_mirror_drops_levels": [(
        "    for level_key, intervals in sorted(levels.items()):\n        rows.append(",
        "    for level_key, intervals in sorted({}.items()):\n        rows.append(")],
}

MUTANTS_ROUND2 = {
    "M16_edge_composition_minus_span": [(
        "    common_only = _anchor_shift_envelope(contributions, bundle_bound_s)\n    edge_bound_s = fiducial_bound_s + wall_minus_monotonic_span_s\n",
        "    common_only = _anchor_shift_envelope(contributions, bundle_bound_s)\n    edge_bound_s = fiducial_bound_s - wall_minus_monotonic_span_s\n")],
    "M17_v052_mirror_uses_raw_curve": [(
        "    curve = anchor_curve if anchor_curve is not None else raw_curve\n",
        "    curve = raw_curve\n")],
}
MUTANTS.update(MUTANTS_ROUND2)
