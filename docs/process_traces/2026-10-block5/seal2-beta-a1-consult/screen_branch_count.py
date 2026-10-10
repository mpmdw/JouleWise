import json, re, collections
d = json.load(open('/Users/edr/night-archive/harvest-v5-b5-beta-a1-20261010T0742Z/derived/neg8-screen.json'))
COND = {'neg8_drift_bound_underived','neg8_idle_sub_drift_bound_underived','neg8_drift_bound_stale',
        'neg8_bracket_abs_delta_exceeded','neg8_bracket_idle_sub_abs_delta_exceeded',
        'neg8_bracket_missing','neg8_bracket_reference_invalid'}
PROB = {'bracket_absent','conditions_beyond_bound_underived','clean_bound_unavailable','collected_bound_unavailable',
        'evaluation_time_unrecorded','policy_unregistered','evaluation_basis_invalid','source_manifests_unrecorded',
        'source_manifest_path_invalid','source_manifest_unauthenticated','source_manifest_policy_differs',
        'source_manifest_members_invalid','evaluation_basis_projection_failed','not_point_drift',
        'rederivation_invalid','rederivation_differs_from_stored_bracket'}
SUB = {'provenance','bundle_strict_invalid'}
REASON = {'contention.request_overlap','battery.member_span','battery.accumulator_excursion','thermal.os_level_nonzero',
          'thermal.powermetrics_pressure_elevated','clock.step_overlap','contention.unmeasured','battery.unmeasured',
          'env.member_quiet_state_violated','battery.capture_pair_failed','member.timeout','member.admission_aborted',
          'member.strict_validation_failed','member.anchor_not_bounded','member.anchor_recompute_mismatch',
          'member.reduction_mismatch','member.unreadable','member.bytes_missing','member.bytes_ambiguous',
          'model.identity_mismatch','model.identity_underivable','status_not_succeeded','summary_unreadable',
          'strict_invalid','energy_unreadable'}
def w(v, ok): return v if v in ok else ('null' if v is None else 'other')
def prob(p):
    if p in PROB: return p
    head, _, tail = str(p).partition(':')
    if head == 'rederivation_failed': return head + ':' + (tail if tail in SUB else 'other')
    if head == 'rederivation_raised': return head + ':' + (tail if re.fullmatch('[A-Za-z]{1,40}', tail) else 'other')
    return 'other'
r = d.get('rescreen') or {}; s = r.get('survivors') or {}; st = d.get('stored') or {}
print('bound_used', w(d.get('bound_used'), {'corpus_physics_clean','collected_subset','stored_bracket'}))
print('stored.decision', w(st.get('decision'), {'passed','failed','flagged'}))
print('stored.other_conditions', sorted(w(c, COND) for c in st.get('conditions_beyond_bound_underived') or []))
print('rescreen.evaluated', bool(r.get('evaluated')))
print('rescreen.decision', w(r.get('decision'), {'passed','failed','flagged'}))
print('rescreen.conditions', sorted(w(c, COND) for c in r.get('conditions') or []))
print('rescreen.problems', [prob(p) for p in r.get('problems') or []])
print('freshness', w((r.get('freshness') or {}).get('decision'), {'fresh','stale','underived'}),
      len((r.get('freshness') or {}).get('triggers') or []))
print('survivor_screen', w(s.get('survivor_screen') or d.get('survivor_screen'),
      {'evaluated','references_insufficient','more_references_than_planned','invalid'}))
print('endpoint_protocol', w(s.get('endpoint_protocol'), {'replicated_endpoints','replicated_endpoints_with_midpoint',
      'legacy_single_member_endpoints','invalid'}))
rc = s.get('reference_counts') or d.get('reference_counts') or {}
print('reference_counts', {k: rc.get(k) for k in ('start','midpoint','end') if isinstance(rc.get(k), int)})
print('losses_by_position_reason', sorted(collections.Counter(
    (w(i.get('position'), {'start','midpoint','end'}), w(i.get('reason'), REASON))
    for i in s.get('reference_losses') or [] if isinstance(i, dict)).items()))
print('harvest_losses_by_code', sorted(collections.Counter(
    w(v, REASON) for v in (d.get('harvest_reference_losses') or {}).values()).items()))
