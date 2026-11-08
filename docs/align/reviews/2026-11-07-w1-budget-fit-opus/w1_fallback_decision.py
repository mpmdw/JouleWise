#!/usr/bin/env python3
"""ALIGN v4 W1: ruling 1(f) budget fit and the ruling 1(e) fallback, mechanically.

Opus audit seat, 2026-11-07, written against lane/2026-11-06-v4-r1-integrated
@ e901eb2a4. It reuses the kit's own arithmetic (scripts/align_v4_kit.py:
l1_t_dead, w1_g0_cap, ruling_1f_fit, max_fitting_b_d), so it cannot disagree
with the kit refusal it explains.

Usage (from a checkout of the lane):
    python3 -B w1_fallback_decision.py --r1-slots configs/campaigns/align_v4/registration/r1_slots.json \
        [--r4 TOK_PER_S --i-d4 S] [--json]
    python3 -B w1_fallback_decision.py --demo     # synthetic R1 outcomes, no data

Blinding: it reads only engineering fields of r1_slots (slots.B_D/I_D/N_chunk,
max_r1_tail_s, budget_fit_inputs, deadman_budget phases/decode_tokens/
g0_outcome/admitted_turns/x7, x_g status/wait, g0_cap_w1, duty_bar verdict,
s6_tuning G1/H median waits, inconclusive_segments, ac_powermode). It never reads u5, planning_temperature,
projected_mde, energies, residuals or scores.

Projection constants are labelled assumptions, not R1 evidence:
  R4_OVER_R8 = 1.70  4-bit/8-bit decode-rate ratio (active bytes 28.6 GB vs 16.1 GB
                     gives 1.78 at equal bandwidth efficiency; 1.70 is the
                     conservative default). Use --r4 once a d-4bit step exists.
  STEP2_IDLE_S = 150 1(e) step 2 (idle 300 -> 450 s, inside the member).
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import sys

R4_OVER_R8 = 1.70
STEP2_IDLE_S = 150.0
FLOOR = 6144
CAP_TOKENS = 4096
D_CAP_LIMIT_S = 3300          # runner envelope with unspent idle-wait (run_campaign.py:11214)
SPAN_FIXED_W1 = 4995 + 3131.27 + 4 * 850 + 4 * 1150   # scaffold + anchors + contrast (A1 planning)
WINDOW_RESERVES = 3300 + 7200 + 7200
DK_FIXED = 4995 + 3131.27


def load_kit(root):
    sys.path.insert(0, str(root))
    os.chdir(root)
    from scripts import align_v4_kit as kit
    cap, timeout = kit.d_turn_cap_tokens(), kit.r1_g0_timeout_s()
    kit.d_turn_cap_tokens = lambda root=kit.ROOT: cap      # cache: one git show, not thousands
    kit.r1_g0_timeout_s = lambda root=kit.ROOT: timeout
    return kit


def window(span_s):
    return 60 * math.ceil((span_s + WINDOW_RESERVES) / 60)


def member_cap_needed(kit, i_d, tail, episode_s):
    """Smallest 60 s multiple C with I_D + 1.13544*episode + tail + 10 <= C (L1 at a cap C)."""
    return 60 * math.ceil((i_d + kit.DEADMAN_FACTOR * episode_s + tail + kit.L1_MARGIN_S) / 60)


def dk_windows(d_member_s, held_out_needed=48):
    n_d = math.floor((59520 - WINDOW_RESERVES - DK_FIXED) / d_member_s)
    held = n_d - 2
    return n_d, held, (math.ceil(held_out_needed / held) if held > 0 else None)


def decide(kit, r1, r4=None, i_d4=None):
    out = {'authority': 'CHAIR 1(e)/1(f); LEAD-RULINGS-1 L1; LEAD-RULINGS-2 R5-4, R6-3, R7-2, R7-12, R8-8',
           'steps': []}
    note = out['steps'].append
    if r1.get('inconclusive_segments'):
        out['branch'] = 'R1-RERUN'
        note('inconclusive_segments present: the remedy is an R1 re-run (magistrate), LEAD-RULINGS-2 R7-3. Stop.')
        return out
    slots = r1.get('slots') or {}
    i_d, tail = slots['I_D'], r1['max_r1_tail_s']
    td = kit.l1_t_dead(i_d, tail)
    fit = kit.ruling_1f_fit(r1, FLOOR, td)
    terms, r = fit['terms_s'], fit['r_decode_tok_per_s']
    g0c, hg, pt = terms['G0_s'], terms['holds_s'], terms['prefill_tool_s']
    rows = r1['deadman_budget']
    rho = max(((p['phases_s']['G1'] + p['phases_s']['H']) / p['decode_tokens'])
              for p in rows if p.get('decode_tokens')) if any(p.get('decode_tokens') for p in rows) else 0.0
    hg_proj = max(hg, rho * (FLOOR + CAP_TOKENS))
    truncated = [p['run'] for p in rows if p.get('x7')]
    bmax = kit.max_fitting_b_d(r1, td)
    out.update(inputs={'r_decode': r, 'I_D': i_d, 'max_r1_tail_s': tail, 'T_dead': td, 'G0_cap_W1': g0c,
                       'g0_censored': fit['g0_cap_w1']['censored'], 'x_g_fallback': fit['g0_cap_w1']['x_g_fallback'],
                       'HG': hg, 'PT': pt, 'hold_s_per_token_max': rho, 'HG_projected_floor': hg_proj,
                       'gated_runs_cut_by_deadman': truncated,
                       'duty_bar': (r1.get('duty_bar') or {}).get('verdict'), 'B_D_top': slots.get('B_D'),
                       'N_chunk': slots.get('N_chunk'), 'ac_powermode': r1.get('ac_powermode')},
               floor_worst_s=fit['worst_s'], floor_slack_s=td - fit['worst_s'], largest_fitting_B_D=bmax)
    note(f'1(f) at B_D 6,144: worst {fit["worst_s"]:.0f} s vs T_dead {td:.0f} s (slack {td - fit["worst_s"]:.0f} s); '
         f'largest fitting B_D {bmax}.')
    if g0c >= td:
        note(f'G0_cap_W1 {g0c} s >= T_dead {td:.0f} s: no decode rate or B_D can fit, and a W1 G0 could never '
             'time out before the deadman (X7 before X2).')
    if bmax is not None:
        out['branch'] = 'A-ADMIT-8BIT'
        note(f'Admit 8-bit at inputs.R1.B_D = {bmax} (then kit.fit_roster for the span). '
             'If the duty bar is not pass, 1(e) still applies to the duty bar itself.')
        return out

    # 1(e) steps 1-2 at their best case (no Mac time spent to show they cannot cure it).
    head_bc = td - kit.thermal_gates.G0_CAP_DEFAULT_S - pt                         # step 1: HG -> 0, G0c -> 600
    g0c_s2 = max(600.0, (g0c - 1.25 * STEP2_IDLE_S)) if not fit['g0_cap_w1']['censored'] else g0c
    head_s2 = (td - STEP2_IDLE_S / kit.DEADMAN_FACTOR) - g0c_s2 - pt                # step 2 alone, HG -> 0
    r_star_bc = (FLOOR + CAP_TOKENS) / head_bc if head_bc > 0 else math.inf
    out['r_star'] = {'measured_terms': (FLOOR + CAP_TOKENS) / (td - g0c - hg - pt) if td - g0c - hg - pt > 0
                     else math.inf, 'best_case_steps_1_2': r_star_bc}
    if r < r_star_bc and r < ((FLOOR + CAP_TOKENS) / head_s2 if head_s2 > 0 else math.inf):
        note(f'1(e) steps 1-2 cannot cure 1(f): even with zero G1/H and G0_cap_W1 at the 600 s floor the floor needs '
             f'r >= {r_star_bc:.1f} tok/s; R1 measured {r:.2f}. Record both as "still failing (arithmetic)" and go to step 3.')
    else:
        note('Steps 1-2 could in principle cure 1(f) (decode term fits). Step 1: tune S6 (0.5 C steps, <= 2.0 C) '
             'by replaying the recorded gate journals; the kit needs measured deadman rows at the tuned band, so the '
             'magistrate re-runs the R1 gated block (D_bank, D_spam a, D_spam b, X-G) at S6. Step 2 only if '
             'G0_cap_W1 > 787.5 s, uncensored, and the <= +55 s gain closes the gap; it costs 132 s of T_dead and '
             'breaks the 30B contrast member fit if applied to contrast members.')
        out['branch'] = 'STEP1-S6-RERUN-GATED-BLOCK'
        return out

    # Step 3: 4-bit at the same rung.
    r4v = r4 if r4 is not None else R4_OVER_R8 * r
    td4 = kit.l1_t_dead(i_d4 if i_d4 is not None else i_d, tail)
    hg4 = hg * r / r4v
    worst4 = g0c + hg4 + pt + (FLOOR + CAP_TOKENS) / r4v
    worst4_bc = 600 + pt + (FLOOR + CAP_TOKENS) / r4v
    out['step3'] = {'r4': r4v, 'r4_source': 'measured d-4bit step' if r4 is not None else f'projection {R4_OVER_R8} x r8',
                    'T_dead4': td4, 'worst_floor_s': worst4, 'slack_s': td4 - worst4,
                    'best_case_with_S6_slack_s': td4 - worst4_bc}
    # S6 effect estimate (step 1 is cumulative with step 3): the FD 2.6 target is a
    # median G1 and hold wait <= 90 s, so scale the measured gate seconds by
    # 90 / (larger recorded median). An estimate, not evidence: the kit needs
    # gated rows measured at the tuned band.
    s6 = r1.get('s6_tuning') or {}
    medians = [s6.get(k) for k in ('G1_median_s', 'H_median_s') if isinstance(s6.get(k), (int, float))]
    s6_scale = min(1.0, 90.0 / max(medians)) if medians and max(medians) > 0 else 0.0
    worst4_s6 = g0c + hg4 * s6_scale + pt + (FLOOR + CAP_TOKENS) / r4v
    out['step3'].update(s6_scale_estimate=s6_scale, worst_floor_with_S6_estimate_s=worst4_s6,
                        slack_with_S6_estimate_s=td4 - worst4_s6)
    if worst4 <= td4:
        out['branch'] = 'STEP3-4BIT'
        note(f'Step 3 fits at 4-bit: worst {worst4:.0f} s <= T_dead4 {td4:.0f} s. Rule 4-bit at the same rung; '
             'before W1 it needs the 4-bit R0 qualification (load/NLL/memory), pins, and an R1-4bit night (step-d '
             '+ gated block) so the kit sees 4-bit r1_slots. Ed: the named paper model changes (CHAIR B Q6).')
        return out
    note(f'Step 3 fails at 4-bit on R1\'s measured gate seconds: worst {worst4:.0f} s vs T_dead4 {td4:.0f} s.')
    if worst4_s6 <= td4:
        out['branch'] = 'STEP1+3-4BIT-S6'
        note(f'Steps 1+3 (cumulative) fit on the S6 estimate (scale {s6_scale:.2f}): worst {worst4_s6:.0f} s. '
             'Rule them provisionally; admission needs an R1-4bit night whose gated block runs at the tuned S6 '
             '(<= 2.0 C), so the kit re-derives 1(f) from measured rows. If that night still refuses, go to step 4.')
        return out
    note(f'Steps 1+3 fail on the S6 estimate too (worst {worst4_s6:.0f} s); idealised best case (zero holds, '
         f'G0 at 600 s) slack {td4 - worst4_bc:.0f} s.')

    # Step 4: screen-only, return to council with the structural options sized.
    out['branch'] = 'STEP4-COUNCIL'
    ep8 = g0c + hg_proj + pt + (FLOOR + CAP_TOKENS) / r
    ep4 = g0c + hg_proj * r / r4v + pt + (FLOOR + CAP_TOKENS) / r4v
    ep8_s6 = g0c + hg_proj * max(s6_scale, 1e-9) + pt + (FLOOR + CAP_TOKENS) / r
    c8, c4 = member_cap_needed(kit, i_d, tail, ep8), member_cap_needed(kit, i_d4 or i_d, tail, ep4)
    c8_s6 = member_cap_needed(kit, i_d, tail, ep8_s6)
    out['council_sizing_note'] = (f'8-bit cap with the S6 estimate applied to projected holds: {c8_s6} s '
                                  '(needs a gated block measured at the tuned band before freezing).')
    sizing = {}
    for label, c in (('8-bit', c8), ('8-bit+S6 (estimate)', c8_s6), ('4-bit', c4)):
        n_d, held, wins = dk_windows(c)
        w18, w17 = window(math.ceil(SPAN_FIXED_W1 + 6 * c)), window(math.ceil(SPAN_FIXED_W1 + 5 * c))
        sizing[label] = {'D_member_cap_s': c, 'W1_window_18': w18, 'W1_window_drop18': w17,
                         'W1_fits_44640': w18 <= 44640 or w17 <= 44640,
                         'W1_fits_59520': w18 <= 59520 or w17 <= 59520,
                         'Dk_D_members': n_d, 'Dk_held_out': held, 'Dk_windows_for_48': wins,
                         'within_runner_envelope': c <= D_CAP_LIMIT_S}
    out['council_sizing'] = sizing
    note('1(e) step 4: D screen-only and return to council (the kit refuses step 4 as a W1 admission, R5-10). '
         f'Council option S1 (8-bit, plan-declared D member cap): C_D = {c8} s; S2 (4-bit + cap): C_D = {c4} s. '
         'Holds are projected to the full floor budget from R1\'s worst hold-seconds per decoded token.')
    return out


# ------------------------------------------------------------------ synthetic demo
def synthetic(kit, *, i_d, r, g0_waits, xg_wait, hg_runs, pt, decode_tokens=(3500, 4200, 4100), x7=(True,) * 3,
              b_top=None, censored=(), s6_medians=(200.0, 180.0)):
    rows = []
    for name, w, hgv, tok, cut in zip(kit.GATED_D_RUN_NAMES, g0_waits, hg_runs, decode_tokens, x7):
        outcome = 'deadman' if name in censored else 'released'
        rows.append({'run': name, 'g0_outcome': outcome, 'decode_tokens': tok, 'x7': cut, 'admitted_turns': 1,
                     'phases_s': {'G0': w, 'G1': hgv * 0.4, 'H': hgv * 0.6, 'decode': tok / r,
                                  'prefill': pt * 0.8, 'tool': pt * 0.2, 'tail': 8.0}})
    top = b_top or min(40960, 1024 * math.floor((((1800 - i_d) / kit.DEADMAN_FACTOR) - 53) * r / 1024))
    return {'slots': {'B_D': top, 'I_D': i_d, 'N_chunk': 1024}, 'max_r1_tail_s': 30.0,
            's6_tuning': {'status': 'TODO', 'G1_median_s': s6_medians[0], 'H_median_s': s6_medians[1]},
            'deadman_budget': rows, 'x_g': {'status': 'measured', 'g0_outcome': 'released', 'g0_wait_s': xg_wait},
            'budget_fit_inputs': {'r_decode_step_d_tok_per_s': r, 'turn_cap_tokens': CAP_TOKENS,
                                  'r_decode_tok_per_s': r},
            'duty_bar': {'verdict': 'fail'}, 'inconclusive_segments': [], 'ac_powermode': 0}


def demo(kit):
    cases = {
        '8-bit, optimistic thermal': dict(i_d=380, r=12.4, g0_waits=(420, 450, 470), xg_wait=400,
                                          hg_runs=(120, 150, 140), pt=50),
        '8-bit, central (R7 physics)': dict(i_d=420, r=11.6, g0_waits=(640, 700, 690), xg_wait=720,
                                            hg_runs=(280, 300, 290), pt=80),
        '8-bit, G0 censored': dict(i_d=450, r=11.2, g0_waits=(1100, 900, 950), xg_wait=800,
                                   hg_runs=(100, 120, 90), pt=90, censored=('D_spam_benign_s1_gated_held_a',)),
        'hypothetical 20 tok/s, G0 at floor, small holds': dict(i_d=380, r=20.0, g0_waits=(400, 450, 470),
                                                                xg_wait=400, hg_runs=(20, 30, 25), pt=40,
                                                                x7=(False,) * 3),
        'hypothetical 25 tok/s, G0 at floor, small holds': dict(i_d=380, r=25.0, g0_waits=(400, 450, 470),
                                                                xg_wait=400, hg_runs=(20, 30, 25), pt=40,
                                                                x7=(False,) * 3),
    }
    expected = ['STEP1+3-4BIT-S6', 'STEP4-COUNCIL', 'STEP4-COUNCIL', 'A-ADMIT-8BIT', 'A-ADMIT-8BIT']
    for (name, kw), want in zip(cases.items(), expected):
        res = decide(kit, synthetic(kit, **kw))
        assert res['branch'] == want, (name, res['branch'], want)
        # The A branch must agree with the kit's own refusal logic.
        td = kit.l1_t_dead(kw['i_d'], 30.0)
        assert (res['branch'] == 'A-ADMIT-8BIT') == (kit.max_fitting_b_d(synthetic(kit, **kw), td) is not None)
        print(f'\n## {name}\nbranch: {res["branch"]}')
        for s in res['steps']:
            print(' -', s)
        if 'council_sizing' in res:
            print('   sizing:', json.dumps(res['council_sizing']))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--root', type=Path, default=Path.cwd())
    p.add_argument('--r1-slots', type=Path)
    p.add_argument('--r4', type=float, help='measured 4-bit decode rate (d-4bit step), tok/s')
    p.add_argument('--i-d4', type=float, help='measured 4-bit member intercept, s')
    p.add_argument('--demo', action='store_true')
    p.add_argument('--json', action='store_true')
    a = p.parse_args(argv)
    r1_path = a.r1_slots.resolve() if a.r1_slots else None
    kit = load_kit(a.root.resolve())
    if a.demo:
        demo(kit)
        return 0
    res = decide(kit, json.loads(r1_path.read_text()), r4=a.r4, i_d4=a.i_d4)
    if a.json:
        print(json.dumps(res, indent=2, default=str))
    else:
        print('branch:', res['branch'])
        for s in res['steps']:
            print(' -', s)
        print(json.dumps({k: v for k, v in res.items() if k not in ('steps', 'branch')}, indent=2, default=str))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
