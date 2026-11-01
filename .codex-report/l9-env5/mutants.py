"""L9-ENV-5 mutants: (file, old, new) substitutions applied in a /tmp worktree only.

O-* are L9-ENV-3-OPUS-REV's M01-M17, E-* L9-ENV-4's (FABLE-REV numbering) where
they differ, N-* this seat's O-F1/O-F3/O-F5 mutants.  Patterns re-targeted to
the L9-ENV-5 source are marked (rt).
"""
WW = "joulewise/whole_window.py"
MID = ("                    Window(\n                        start_s=(window.start_s + window.end_s) / 2.0,\n"
       "                        end_s=(window.start_s + window.end_s) / 2.0,\n                    )")
MUTANTS = {
 "O-M01_clamp_to_start": [(WW, MID, MID.replace("(window.start_s + window.end_s) / 2.0", "window.start_s"))],
 "E-M02_clamp_to_end": [(WW, MID, MID.replace("(window.start_s + window.end_s) / 2.0", "window.end_s"))],
 "O-M02_drop_negative_power_guard(rt)": [(WW, "            or any(point.power_w < 0.0 for point in curve)\n", "")],
 "O-M03_eps_off_sign": [(WW, "                        end_s=window.end_s + eps_off_s,\n", "                        end_s=window.end_s - eps_off_s,\n")],
 "O-M04_mirror_drops_items": [(WW, "    for item in reader.item_windows():\n        rows.append(", "    for item in []:\n        rows.append(")],
 "O-M05_restamp_all_member_gates": [(WW, "                and prefix + _json_pointer_token(str(member)) == pointer\n", "")],
 "O-M06_restamp_sets_eligible": [(WW, "        or gate.get(\"eligible\") is not False\n    ):\n        return False\n    merged = set(existing)\n    merged.discard(_ANCHOR_ENVELOPE_UNRECORDED)\n    merged.update(reasons)\n    gate[\"reasons\"] = sorted(merged)",
                                   "    ):\n        return False\n    merged = set(existing)\n    merged.discard(_ANCHOR_ENVELOPE_UNRECORDED)\n    merged.update(reasons)\n    gate[\"reasons\"] = sorted(merged)\n    gate[\"eligible\"] = not merged")],
 "E-M09_restamp_ignores_eligible": [(WW, "        or _ANCHOR_ENVELOPE_UNRECORDED not in existing\n        or gate.get(\"eligible\") is not False\n    ):", "        or _ANCHOR_ENVELOPE_UNRECORDED not in existing\n    ):")],
 "O-M07_skip_reconstruction_proof(rt)": [(WW, "                if _corner_composed_anchor_shift_envelope(\n                    contributions, *bounds\n                ) != recorded:\n                    return summary\n", "")],
 "O-M08_clamp_le": [(WW, "                    if window.end_s < window.start_s\n                    else window", "                    if window.end_s <= window.start_s\n                    else window")],
 "O-M09_v062_anchor_shift_sign": [(WW, "            anchor_curve[0].t - raw_curve[0].t\n", "            raw_curve[0].t - anchor_curve[0].t\n")],
 "O-M10_corner_none_continue": [(WW, "            if corner is None:\n                return None\n            corner_envelopes.append(corner)", "            if corner is None:\n                continue\n            corner_envelopes.append(corner)")],
 "O-M11_restamp_keeps_unrecorded": [(WW, "    merged.discard(_ANCHOR_ENVELOPE_UNRECORDED)\n", "")],
 "O-M12_skip_tail_refusal_return": [(WW, "    if (\n        anchor_ctx.detail == \"post_window_trace_tail_shorter_than_anchor_bound\"\n    ):\n        # Reduce stamps no envelope gate reasons on this resolved refusal.\n        return operative\n", "")],
 "O-M13_flag_on_session_unclamped(rt)": [(WW, "        rederive = (\n            _rederive_operative_summary\n            if self.analysis_clamp", "        rederive = (\n            _rederive_summary_for_authenticated_fiducial_bound\n            if self.analysis_clamp")],
 "O-M14_unknown_pointer_guard_dropped": [(WW, "        # A recorded member envelope the reconstruction does not know.\n        return summary\n", "        pass\n")],
 "O-M15_mirror_drops_levels": [(WW, "    for level_key, intervals in sorted(levels.items()):\n        rows.append(", "    for level_key, intervals in sorted({}.items()):\n        rows.append(")],
 "O-M16_edge_minus_span": [(WW, "    edge_bound_s = fiducial_bound_s + wall_minus_monotonic_span_s\n    corner_envelopes", "    edge_bound_s = fiducial_bound_s - wall_minus_monotonic_span_s\n    corner_envelopes")],
 "O-M17_v052_raw_curve": [(WW, "    curve = anchor_curve if anchor_curve is not None else raw_curve\n", "    curve = raw_curve\n")],
 "E-M06_mirror_drops_blocks": [(WW, "    for block_id, intervals in sorted((reader.block_windows() or {}).items()):\n", "    for block_id, intervals in sorted({}.items()):\n")],
 "E-M12_clamped_appended_last": [(WW, "        if pointer in recorded:\n            ordered[pointer] = recorded[pointer]\n        elif pointer in clamped:\n            ordered[pointer] = clamped[pointer]\n",
                                   "        if pointer in recorded:\n            ordered[pointer] = recorded[pointer]\n    for pointer, _contributions in rows:\n        if pointer in clamped:\n            ordered[pointer] = clamped[pointer]\n")],
 "E-M13_clamp_disabled": [(WW, "    return _clamp_inverted_operative_envelopes(\n        path,\n        summary,", "    return summary\n    return _clamp_inverted_operative_envelopes(\n        path,\n        summary,")],
 "E-M14_always_recompute_body": [(WW, "    if minted is not None:\n        return minted\n", "")],
 "E-M15_restamp_skips_inner_windows": [(WW, "            if isinstance(inner, dict) and not _restamp_clamped_gate(inner, reasons):\n                return False\n", "            pass\n")],
 "E-M16_gate_reasons_without_joint_bound": [(WW, "        pointer: _anchor_envelope_gate_reasons(envelope, joint_bound_j)\n", "        pointer: _anchor_envelope_gate_reasons(envelope, None)\n")],
 "E-M17_v062_summed_curve": [(WW, "                            _shift_curve(\n                                reader.source_curve(source), anchor_shift_s\n                            ),", "                            curve,")],
 "E-MF1_keep_passing_envelope": [(WW, "        if clamped_reasons[pointer]\n", "")],
 "N01_default_flag_true": [(WW, "        analysis_clamp: bool = False,\n", "        analysis_clamp: bool = True,\n")],
 "N02_flag_ignored_always_on": [(WW, "        self.analysis_clamp = analysis_clamp is True\n", "        self.analysis_clamp = True\n")],
 "N03_prepare_always_clamps": [(WW, "            _rederive_operative_summary\n            if self.analysis_clamp\n            else _rederive_summary_for_authenticated_fiducial_bound\n", "            _rederive_operative_summary\n")],
 "N04_member_sessions_drop_flag": [(WW, "                analysis_clamp=self.analysis_clamp,\n", "")],
 "N05_truthy_flag": [(WW, "        self.analysis_clamp = analysis_clamp is True\n", "        self.analysis_clamp = bool(analysis_clamp)\n")],
 "N06_drop_OF3_reproduced_guard": [(WW, "    if not reproduced:\n", "    if False:\n")],
 "N07_drop_OF5_input_inversion_guard": [(WW, "            or any(window.end_s < window.start_s for window in windows)\n", "")],
 "N08_dry_run_flag_off": [("joulewise/b5_analysis/dry_run.py", "archive_context=context,analysis_clamp=True)", "archive_context=context,analysis_clamp=False)")],
 "N09_floor_extraction_flag_dropped": [("joulewise/floor_extraction.py", "        archive_context=archive_context,\n        analysis_clamp=True,\n", "        archive_context=archive_context,\n")],
 "N10_inputs_site3_flag_dropped(rt)": [("joulewise/analysis_engine/inputs.py", "        session_kwargs[\"analysis_clamp\"] = True\n", "        pass\n")],
 "N12_floor_mint_estimator_gate_inverted": [("joulewise/floor_mint_estimator.py", "           if \"analysis_clamp\" in inspect.signature(", "           if \"analysis_clamp\" not in inspect.signature(")],
 "N11_issuer_flag_dropped": [("joulewise/paper_reported_energy_issuer.py", "archive_context=context,\n            analysis_clamp=True)", "archive_context=context)")],
}
