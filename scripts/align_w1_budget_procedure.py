#!/usr/bin/env python3
"""The W1 budget procedure after R1: RL-148 section 2, RL-149 section 1.5, RL-152 section 1.2.

Blind by construction: it reads only R1 timing and count fields (whitelisted
in ``timing_view``; never an energy, U5, beta_T, residual or score) plus the
WP18 X turn count, and computes the decision with the kit's own functions,
so it cannot disagree with ``--check`` on a record whose picks did not change
(``thermometry.D.sensor_pick_changed`` false). On a changed-pick record the
kit's G_turn cap is the R1-pick S7 (``thermometry.D.s7_for_r1_picks.S7``),
which the timing view does not read, and the step goes to the research lead
(RL-159 section 1.4 finding 2).

  decide        print the step and the inputs to set; there is no ruling 1(f)
                receipt to draft or sign (RL-148 section 2; the R10-2(a)
                receipt path is retired, RL-156 section 3.1)
  backfill-x-g  copy X-G's admitted turns, deadman flag and phase seconds from
                r1_result.json into r1_slots.x_g, for an R1 record written
                before the driver recorded them (R10-4)
  derive-contrast
                print inputs.R1.thermal_policy.contrast_g0_cap_s and contrast_fit,
                the kit's own re-derivation from the (backfilled) r1_slots record
  backfill-turn-counts
                copy the lead's explicit per-turn count export (R11/R16) into
                the three gated D deadman_budget rows, binding its sha256; the
                R1 driver does not record per-turn counts

Steps of ``decide`` (RL-148 section 2 withdrew ruling 1(f) for D, with R10-2's
receipt and 4-bit routes; PR #777 row-2 finding 9):
  0. any inconclusive segment not released under RL-122 3(a): R1-RERUN (R7-3,
     the magistrate's call); stop.
  1. B_D is R1's step-d budget (r1_slots.slots.B_D, at least 6,144); missing or
     invalid per-turn count evidence at it: R1-RERUN (or a backfill).
  2. the typical case fits T_dead at the R1 G_turn cap (slots.S7; the kit's
     source only when sensor_pick_changed is false) and the
     three-turn opportunity at B_D passes: TYPICAL-CASE, with the inputs to set.
  3. otherwise RESEARCH-LEAD: the research lead rules; there is no automatic
     route.
Ruling 1(f)'s worst case is printed (``worst_case_print_only``) and decides
nothing. R11 (RUN_STATE 212) binds a separate contrast cap/fit; an unqualified
contrast is a predeclared non-veto INCONCLUSIVE note.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import align_v4_kit as kit  # noqa: E402

# The only fields read (R10-2: timing and count fields, never energies).
# S7 is the R1 G_turn cap the typical-case bar uses when a G1 timed out (PR #777 row-2 finding 9).
SLOT_FIELDS = ('I_D', 'B_D', 'S7')
# phases_s is copied only through _phases, key by key (cold-review LOW-3).
# RL-148 section 2 / RL-149 section 1.5: gate_waits_s (the run's own G1 waits) and g1_timeouts are the
# typical-case bar's inputs (align_v4_kit.typical_case_fit); the view keeps them so a kit check on the view
# reads the same record (PR #777 row-1 review, finding 6).
ROW_FIELDS = ('run', 'g0_outcome', 'decode_tokens', 'admitted_turns', 'x7',
              'turn_decode_counts', 'turn_completed', 'turn_counts_source_sha256', 'gate_waits_s', 'g1_timeouts',
              # RL-152 section 1.2: turn_opportunity reads the own stop from the driver's row (duty_bar.stop).
              'duty_bar')
FIT_FIELDS = ('r_decode_tok_per_s', 'r_decode_step_d_tok_per_s', 'turn_cap_tokens')
X_G_FIELDS = ('status', 'g0_outcome', 'g0_wait_s', 'admitted_turns', 'x7')
DUTY_FIELDS = ('verdict', 'pass')
PHASE_FIELDS = ('G0', 'G1', 'H', 'decode', 'prefill', 'tool', 'tail')
X_G_RESULT_FIELDS = ('g0_outcome', 'g0_wait_s', 'admitted_turns', 'phases_s', 'episode_flags')


def _pick(value, fields):
    return {key: deepcopy(value[key]) for key in fields if isinstance(value, dict) and key in value}


def _phases(value):
    return _pick(value, PHASE_FIELDS) if isinstance(value, dict) else value


def timing_view(r1_slots):
    """The whitelisted R1 timing and count fields; nothing else is copied."""
    rows = r1_slots.get('deadman_budget')
    view = {'schema': r1_slots.get('schema'), 'source': r1_slots.get('source'),
            'slots': _pick(r1_slots.get('slots'), SLOT_FIELDS),
            'max_r1_tail_s': r1_slots.get('max_r1_tail_s'),
            'inconclusive_segments': deepcopy(r1_slots.get('inconclusive_segments')),
            'budget_fit_inputs': _pick(r1_slots.get('budget_fit_inputs'), FIT_FIELDS),
            'duty_bar': _pick(r1_slots.get('duty_bar'), DUTY_FIELDS),
            'deadman_budget': ([{**_pick(row, ROW_FIELDS), 'phases_s': _phases(row.get('phases_s'))}
                                if isinstance(row, dict) else row for row in rows]
                               if isinstance(rows, list) else rows)}
    x_g = r1_slots.get('x_g')
    view['x_g'] = ({**_pick(x_g, X_G_FIELDS), **({'phases_s': _phases(x_g['phases_s'])} if 'phases_s' in x_g else {})}
                   if isinstance(x_g, dict) else x_g)
    return view


def decide(r1_slots, x_max_turns, planning_release=None):
    """The post-R1 budget decision on the timing view. Returns the decision record.

    RL-148 section 2 (ruling 1(f) withdrawn for D; no R10-2 receipt and no 4-bit path), RL-149 section 1.5
    and RL-152 section 1.2 (PR #777 row-2 finding 9): B_D is R1's step-d budget (``r1_slots.slots.B_D``;
    the fit rule no longer lowers it), and W1 needs the typical case to fit (``kit.typical_case_fit`` at the
    R1 G_turn cap ``slots.S7``, which is the kit's cap only when ``sensor_pick_changed`` is false: on a
    changed-pick record the kit binds the R1-pick S7, and the step goes to the research lead; RL-159 section
    1.4 finding 2) and the three-turn opportunity at that B_D (``kit.turn_opportunity``). Steps:
    ``R1-RERUN`` (an INCONCLUSIVE segment, or missing count evidence), ``TYPICAL-CASE`` (both pass; the
    inputs to set), or ``RESEARCH-LEAD`` (either fails: the research lead rules; there is no automatic
    route). Ruling 1(f)'s worst case is printed for the record and decides nothing.

    ``planning_release`` is the lead's RL-122 3(a) record or None: planning-turn
    G0 timeouts it releases do not call for an R1 re-run (kit.check_r1_evidence
    applies the same record)."""
    view = timing_view(r1_slots)
    inconclusive = view.get('inconclusive_segments')
    if not isinstance(inconclusive, dict):
        raise ValueError('r1_slots.inconclusive_segments must be recorded (R6-2)')
    released = kit.planning_released_segments(r1_slots, planning_release)
    deciding_inconclusive = {k: v for k, v in inconclusive.items() if k != 'X_G_contrast' and k not in released}
    if deciding_inconclusive:
        return {'step': 'R1-RERUN',
                'reason': ('inconclusive segment(s) ' + ', '.join(sorted(inconclusive))
                           + ': the remedy is an R1 re-run, the magistrate\'s call (R7-3)')}
    slots = view['slots']
    t_dead = kit.l1_t_dead(slots['I_D'], view['max_r1_tail_s'])
    b_d = slots.get('B_D')
    if type(b_d) is not int or b_d < kit.BUDGET_FLOOR:
        raise ValueError(f'r1_slots.slots.B_D must be the step-d decode budget, an int of at least '
                         f'{kit.BUDGET_FLOOR} (the kit\'s floor), not {b_d!r}; return to the lead')
    g_turn = slots.get('S7')
    contrast = kit.w1_contrast_g0_cap(view, x_max_turns)
    duty = view['duty_bar']
    notes = []
    if not contrast['fits']:
        notes.append('CONTRAST: non-veto ' + contrast['predeclared'])
    if duty.get('pass') is not True:
        notes.append(f'DUTY BAR: verdict {duty.get("verdict")!r}; W1 does not arm on a failed duty bar')
    typical = kit.typical_case_fit(view, t_dead, g_turn)
    opportunity = kit.turn_opportunity(view, b_d)
    worst = kit.ruling_1f_fit(view, b_d, t_dead)
    base = {'T_dead_s': t_dead, 'B_D': b_d, 'notes': notes, 'typical_case': typical, 'turn_opportunity': opportunity,
            'worst_case_print_only': worst,
            'authority': 'RL-148 section 2; RL-149 section 1.5; RL-152 section 1.2'}
    if opportunity['status'] == 'inconclusive':
        return {**base, 'step': 'R1-RERUN',
                'reason': 'R11: missing or invalid per-turn count evidence at B_D: an R1 re-run or a backfill'}
    if not typical['fits'] or opportunity['status'] != 'pass':
        why = []
        if not typical['fits']:
            why.append('the typical case does not fit T_dead (RL-148 section 2)')
        if opportunity['status'] != 'pass':
            why.append(f'the three-turn opportunity at B_D {b_d} is {opportunity["status"]} (RL-152 section 1.2)')
        return {**base, 'step': 'RESEARCH-LEAD',
                'reason': '; '.join(why) + ': no R10-2 receipt and no 4-bit route (RL-148 section 2); '
                          'the research lead rules'}
    return {**base, 'step': 'TYPICAL-CASE', 'contrast_predeclared': contrast['predeclared'],
            'set_inputs': {'R1.B_D': b_d, 'R1.T_dead': t_dead,
                           'R1.thermal_policy.g0_cap_s': kit.w1_g0_cap(view)['value_s'],
                           'R1.thermal_policy.contrast_g0_cap_s': contrast['value_s'],
                           'R1.thermal_policy.contrast_fit': contrast}}


def backfill_x_g(r1_slots, r1_result, r1_result_sha256):
    """r1_slots with X-G's timing and count fields copied from r1_result.json.

    Only the X_G_contrast phase result's whitelisted fields are read; its
    G0 outcome and wait must equal the r1_slots record, and fields already
    recorded are never overwritten. A recorded lead step (lead ruling on R10
    open point (b), like s6_tuning): it records the source file's sha256."""
    if not kit.valid_digest(r1_result_sha256):
        raise ValueError('backfill-x-g must record the r1_result.json sha256 (64 lowercase hex)')
    phases = r1_result.get('phases') if isinstance(r1_result, dict) else None
    matches = [p for p in phases if isinstance(p, dict) and p.get('name') == 'X_G_contrast'] \
        if isinstance(phases, list) else []
    if len(matches) != 1 or not isinstance(matches[0].get('result'), dict):
        raise ValueError('r1_result.json must hold exactly one X_G_contrast phase with a result')
    result = _pick(matches[0]['result'], X_G_RESULT_FIELDS)
    x_g = r1_slots.get('x_g')
    if not isinstance(x_g, dict) or x_g.get('status') == 'not_run':
        raise ValueError('r1_slots.x_g must record a run X-G')
    if any(x_g.get(k) != result.get(k) for k in ('g0_outcome', 'g0_wait_s')):
        raise ValueError('r1_result X_G_contrast disagrees with r1_slots.x_g on g0_outcome or g0_wait_s')
    present = [k for k in kit.X_G_EVIDENCE_FIELDS if x_g.get(k) is not None]
    if present:
        raise ValueError(f'r1_slots.x_g already records {present}; nothing is overwritten')
    from scripts.align_r1_rehearsal import x_g_evidence
    out = deepcopy(r1_slots)
    out['x_g'].update(x_g_evidence(result), backfill={
        'authority': 'LEAD-RULINGS-2 R10-4; R10 builder decisions, lead ruling (b)',
        'lead_step': True, 'source': 'r1_result.json phases[X_G_contrast].result',
        'r1_result_sha256': r1_result_sha256, 'fields': list(kit.X_G_EVIDENCE_FIELDS)})
    return out


def backfill_turn_counts(r1_slots, export, export_sha256):
    """r1_slots with the gated D runs' per-turn counts from a lead-owned export.

    ``export`` maps each gated D run name to ``{'turn_decode_counts': [int, ...],
    'turn_completed': [bool, ...]}`` taken from explicit bundle bytes (R11/R16:
    count-only, never an energy or score). The record keeps the export's sha256 in
    ``turn_counts_source_sha256``. Existing values are never overwritten, and the
    lengths and decode-token sum must agree with the driver's own row, so a
    mismatched export is refused here as well as by ``kit.turn_opportunity``."""
    if not kit.valid_digest(export_sha256):
        raise ValueError('backfill-turn-counts must record the export sha256 (64 lowercase hex)')
    rows = r1_slots.get('deadman_budget')
    if (not isinstance(rows, list) or len(rows) != 3 or not isinstance(export, dict)
            or {r.get('run') for r in rows if isinstance(r, dict)} != set(kit.GATED_D_RUN_NAMES)
            or set(export) != set(kit.GATED_D_RUN_NAMES)):
        raise ValueError('turn-count export must cover exactly the three gated D runs of r1_slots')
    cap = (r1_slots.get('budget_fit_inputs') or {}).get('turn_cap_tokens')
    out = deepcopy(r1_slots)
    for row in out['deadman_budget']:
        entry = export[row['run']]
        counts, completed = (entry.get(k) if isinstance(entry, dict) else None
                             for k in ('turn_decode_counts', 'turn_completed'))
        present = [k for k in ('turn_decode_counts', 'turn_completed', 'turn_counts_source_sha256')
                   if row.get(k) is not None]
        if present:
            raise ValueError(f'{row["run"]} already records {present}; nothing is overwritten')
        if (type(cap) is not int or not isinstance(counts, list) or not counts
                or any(type(n) is not int or not 0 <= n <= cap for n in counts)
                or not isinstance(completed, list) or len(completed) != len(counts)
                or any(type(v) is not bool for v in completed)
                or sum(counts) != row.get('decode_tokens') or row.get('admitted_turns') != len(counts)):
            raise ValueError(f'{row["run"]}: export disagrees with the driver row '
                             '(per-turn counts, completion flags, decode_tokens, admitted_turns)')
        row.update(turn_decode_counts=list(counts), turn_completed=list(completed),
                   turn_counts_source_sha256=export_sha256)
    out['turn_counts_backfill'] = {'authority': 'RUN_STATE 212 R16; lead-owned export',
                                   'lead_step': True, 'export_sha256': export_sha256}
    return out


def _load(path):
    return json.loads(Path(path).read_bytes())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('decide')
    p.add_argument('--r1-slots', type=Path, default=ROOT / kit.R1_SLOTS)
    p.add_argument('--inputs', type=Path, default=ROOT / kit.INPUTS, help='read for WP18.X.max_turns only')
    p.add_argument('--planning-release', type=Path, default=ROOT / kit.R1_PLANNING_RELEASE,
                   help='the lead\'s RL-122 3(a) record; used only if the file exists')
    p = sub.add_parser('backfill-x-g')
    p.add_argument('--r1-slots', type=Path, default=ROOT / kit.R1_SLOTS)
    p.add_argument('--r1-result', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p = sub.add_parser('derive-contrast')
    p.add_argument('--r1-slots', type=Path, default=ROOT / kit.R1_SLOTS)
    p.add_argument('--inputs', type=Path, default=ROOT / kit.INPUTS, help='read for WP18.X.max_turns only')
    p = sub.add_parser('backfill-turn-counts')
    p.add_argument('--r1-slots', type=Path, default=ROOT / kit.R1_SLOTS)
    p.add_argument('--counts-export', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'derive-contrast':
            contrast = kit.w1_contrast_g0_cap(_load(args.r1_slots), _load(args.inputs)['WP18']['X']['max_turns'])
            print(json.dumps({'contrast_g0_cap_s': contrast['value_s'], 'contrast_fit': contrast},
                             indent=2, sort_keys=True))
        elif args.command == 'backfill-turn-counts':
            raw = args.counts_export.read_bytes()
            out = backfill_turn_counts(_load(args.r1_slots), json.loads(raw), hashlib.sha256(raw).hexdigest())
            args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
            print(f'wrote {args.out}')
        elif args.command == 'decide':
            x_max_turns = _load(args.inputs)['WP18']['X']['max_turns']
            release = _load(args.planning_release) if args.planning_release.is_file() else None
            out = decide(_load(args.r1_slots), x_max_turns, planning_release=release)
            print(json.dumps(out, indent=2, sort_keys=True))
        else:
            raw = args.r1_result.read_bytes()
            out = backfill_x_g(_load(args.r1_slots), json.loads(raw), hashlib.sha256(raw).hexdigest())
            args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
            print(f'wrote {args.out}')
    except (OSError, KeyError, TypeError, ValueError) as exc:
        print(f'align_w1_budget_procedure: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
