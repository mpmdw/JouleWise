#!/usr/bin/env python3
"""LEAD-RULINGS-2 R10-2: the pre-declared, mechanical W1 budget procedure after R1.

Blind by construction: it reads only R1 timing and count fields (whitelisted
in ``timing_view``; never an energy, U5, beta_T, residual or score) plus the
WP18 X turn count, and computes ruling 1(f)'s branch with the kit's own
functions, so it cannot disagree with ``--check``.

  decide        print the step and, for R10-2 branch (a) or (b), write the
                receipt draft (lead_signature PENDING) for the lead to sign
  sign          set the lead's signature line and write the canonical receipt
                the kit reads (registration/ruling_1f_receipt.json)
  backfill-x-g  copy X-G's admitted turns, deadman flag and phase seconds from
                r1_result.json into r1_slots.x_g, for an R1 record written
                before the driver recorded them (R10-4)

Steps of ``decide`` (R10-2, recorded before any R1 number exists):
  0. any inconclusive segment: R1-RERUN (R7-3, the magistrate's call); stop.
  1. the current rule fits at some B_D >= 6,144: CURRENT-RULE, no receipt.
  2. G0* = T_dead - holds (projected to 10,240 tokens) - prefill/tool
     - 10,240/r. If ceil(1.25 x the longest released gated D G0 wait) <= G0*:
     R10-2(a), D arms G0 at floor(G0*) (below 600 s), B_D = 6,144.
  3. otherwise R10-2(b): 4-bit D next, after its own R1-4bit gated night; the
     lead rules on it with Ed. (c) (window council) follows if (a) also fails
     on the 4-bit night.
The contrast members' cap must fit their deadman in every branch (R10-2(a));
when it cannot be shown, --check refuses W1 and this tool says so.
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
SLOT_FIELDS = ('I_D', 'B_D')
ROW_FIELDS = ('run', 'g0_outcome', 'phases_s', 'decode_tokens', 'admitted_turns', 'x7')
FIT_FIELDS = ('r_decode_tok_per_s', 'r_decode_step_d_tok_per_s', 'turn_cap_tokens')
X_G_FIELDS = ('status', 'g0_outcome', 'g0_wait_s', *kit.X_G_EVIDENCE_FIELDS)
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


def _draft(branch, derived, view):
    d = derived['derivation']
    waits = {run: row['G0_s'] for run, row in derived['inputs']['gated_d'].items()}
    if branch == 'a':
        exposure = (f'A W1 D member whose G0 does not release within G0* = {d["d_g0_cap_s"]} s ends X2 before '
                    f'turn 1 (episode.g0_unreleased), never X7. R1\'s gated D G0 waits were {waits} s '
                    f'(censored: {d["censored_D"]}).')
        deviation = ('Public deviation (R10-2(a)): lowers FINAL-DESIGN\'s and R7-2\'s 600 s G0-cap floor for W1\'s '
                     f'D members only, to {d["d_g0_cap_s"]} s; ruling 1(f)\'s worst-case guarantee is kept with '
                     'that armed cap as its G0 term.')
    else:
        exposure = None
        deviation = ('No deviation applied: R10-2(a) does not fit (ceil(1.25 x longest released gated D G0 wait) = '
                     f'{d["admit_bound_s"]} s against G0* = {d["G0_star_s"]:.1f} s). R10-2(b): 4-bit D next, '
                     'after its own R1-4bit gated night; the lead rules on it with Ed.')
    return {'schema': kit.RULING_1F_RECEIPT_SCHEMA, 'authority': kit.R10_AUTHORITY, 'branch': branch,
            'procedure': {'path': 'scripts/align_w1_budget_procedure.py',
                          'sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
            'r1_record': {'schema': view['schema'], 'source': view['source'], 'I_D': view['slots'].get('I_D'),
                          'max_r1_tail_s': view['max_r1_tail_s']},
            'inputs': derived['inputs'], 'derivation': derived['derivation'], 'contrast': derived['contrast'],
            'rules': {'g0_term_rule': 'G0 term = the armed D cap = floor(G0*) (R10-2(a))',
                      'g0_star_rule': 'G0* = T_dead - holds_proj - max(prefill + tool) - 10,240 / r',
                      'rate_rule': 'r = min(step-d and every gated run\'s decode rate) (R6-3)',
                      'holds_term_rule': ('holds_proj = max over the gated D runs of max(G1 + H, '
                                          '(G1 + H) / decode_tokens x 10,240) (R10-4, the audit\'s corrected D-f)'),
                      'overshoot_rule': 'the last admitted turn keeps its full 4,096-token cap (R6-3)',
                      'admit_rule': ('ceil(1.25 x the longest released gated D G0 wait) <= G0*; a censored '
                                     'D G0 sets no bound and is recorded in censored_D (R10-2(a) text)'),
                      'contrast_rule': derived['contrast']['rule']},
            'x2_exposure': exposure, 'deviation_log': deviation,
            'lead_signature': kit.UNSIGNED + ': the lead replaces this with a signature line '
                              '(name, session, date) via `align_w1_budget_procedure.py sign`'}


def decide(r1_slots, x_max_turns):
    """Run R10-2's steps on the timing view. Returns the decision record."""
    view = timing_view(r1_slots)
    inconclusive = view.get('inconclusive_segments')
    if not isinstance(inconclusive, dict):
        raise ValueError('r1_slots.inconclusive_segments must be recorded (R6-2)')
    if inconclusive:
        return {'step': 'R1-RERUN', 'branch': None, 'receipt_draft': None,
                'reason': ('inconclusive segment(s) ' + ', '.join(sorted(inconclusive))
                           + ': the remedy is an R1 re-run, the magistrate\'s call (R7-3)')}
    slots = view['slots']
    t_dead = kit.l1_t_dead(slots['I_D'], view['max_r1_tail_s'])
    derived = kit.r10_2_derivation(view, t_dead, x_max_turns)
    contrast = derived['contrast']
    duty = view['duty_bar']
    notes = []
    if not contrast['fits']:
        notes.append('CONTRAST: the contrast G0 cap cannot be shown to fit the contrast deadman; --check refuses '
                     'W1 in every branch (R10-2(a)): ' + '; '.join(contrast['reasons']))
    if duty.get('pass') is not True:
        notes.append(f'DUTY BAR: verdict {duty.get("verdict")!r}; --check also needs r1_slots.duty_bar.lead_fallback '
                     '(ruling 1(e) step) before W1 arms')
    largest = kit.max_fitting_b_d(view, t_dead)
    base = {'T_dead_s': t_dead, 'derived': derived, 'notes': notes,
            'current_rule_largest_fitting_B_D': largest}
    if largest is not None:
        return {**base, 'step': 'CURRENT-RULE', 'branch': None, 'receipt_draft': None,
                'set_inputs': {'R1.B_D': largest, 'R1.T_dead': t_dead,
                               'R1.thermal_policy.g0_cap_s': kit.w1_d_g0_cap(view)['value_s'],
                               'R1.thermal_policy.contrast_g0_cap_s': contrast['value_s']}}
    branch = derived['branch']
    if branch == 'current':   # G0* >= 600 s but the current rule misses: not reachable, kept fail closed
        raise ValueError('R10-2: G0* is at least 600 s yet the current rule does not fit; return to the lead')
    out = {**base, 'step': f'R10-2({branch})', 'branch': branch, 'receipt_draft': _draft(branch, derived, view)}
    if branch == 'a':
        out['set_inputs'] = {'R1.B_D': kit.BUDGET_FLOOR, 'R1.T_dead': t_dead,
                             'R1.thermal_policy.g0_cap_s': derived['derivation']['d_g0_cap_s'],
                             'R1.thermal_policy.contrast_g0_cap_s': contrast['value_s'],
                             'R1.thermal_policy.g0_cap_receipt': {
                                 'authority': kit.thermal_gates.R10_G0_CAP_AUTHORITY,
                                 'receipt_sha256': 'the sha256 that `sign` prints'}}
    else:
        out['projection_print_only'] = {
            'r4_tok_per_s_projection': 1.70 * derived['inputs']['r_decode_tok_per_s'],
            'note': 'a projection, never admission evidence: the 4-bit branch needs its own R1-4bit gated night'}
    return out


def sign(draft, signature):
    """The lead's signature on a drafted receipt; returns the receipt."""
    if not isinstance(draft, dict) or draft.get('schema') != kit.RULING_1F_RECEIPT_SCHEMA:
        raise ValueError(f'not a {kit.RULING_1F_RECEIPT_SCHEMA} draft')
    if not isinstance(signature, str) or not signature.strip() or signature.startswith(kit.UNSIGNED):
        raise ValueError('the signature line must be non-empty text')
    return {**draft, 'lead_signature': signature.strip()}


def backfill_x_g(r1_slots, r1_result, r1_result_sha256):
    """r1_slots with X-G's timing and count fields copied from r1_result.json.

    Only the X_G_contrast phase result's whitelisted fields are read; its
    G0 outcome and wait must equal the r1_slots record, and fields already
    recorded are never overwritten."""
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
        'authority': 'LEAD-RULINGS-2 R10-4', 'source': 'r1_result.json phases[X_G_contrast].result',
        'r1_result_sha256': r1_result_sha256, 'fields': list(kit.X_G_EVIDENCE_FIELDS)})
    return out


def _load(path):
    return json.loads(Path(path).read_bytes())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('decide')
    p.add_argument('--r1-slots', type=Path, default=ROOT / kit.R1_SLOTS)
    p.add_argument('--inputs', type=Path, default=ROOT / kit.INPUTS, help='read for WP18.X.max_turns only')
    p.add_argument('--draft-out', type=Path, help='where to write the receipt draft (branch (a) or (b))')
    p = sub.add_parser('sign')
    p.add_argument('draft', type=Path)
    p.add_argument('--signature', required=True)
    p.add_argument('--out', type=Path, default=ROOT / kit.RULING_1F_RECEIPT)
    p = sub.add_parser('backfill-x-g')
    p.add_argument('--r1-slots', type=Path, default=ROOT / kit.R1_SLOTS)
    p.add_argument('--r1-result', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'decide':
            x_max_turns = _load(args.inputs)['WP18']['X']['max_turns']
            out = decide(_load(args.r1_slots), x_max_turns)
            draft = out.pop('receipt_draft')
            if draft is not None:
                if args.draft_out is None:
                    raise ValueError(f'{out["step"]} drafts a receipt: pass --draft-out')
                args.draft_out.write_bytes(kit.receipt_bytes(draft))
                out['receipt_draft_path'] = str(args.draft_out)
            print(json.dumps(out, indent=2, sort_keys=True))
        elif args.command == 'sign':
            receipt = sign(_load(args.draft), args.signature)
            args.out.write_bytes(kit.receipt_bytes(receipt))
            print(json.dumps({'receipt': str(args.out), 'branch': receipt['branch'],
                              'g0_cap_receipt': {'authority': kit.thermal_gates.R10_G0_CAP_AUTHORITY,
                                                 'receipt_sha256': kit.receipt_sha256(receipt)}},
                             indent=2, sort_keys=True))
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
