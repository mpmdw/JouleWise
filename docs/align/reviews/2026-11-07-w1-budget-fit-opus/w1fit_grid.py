#!/usr/bin/env python3
"""Ruling 1(f) budget-fit grid for ALIGN v4 W1 (Opus seat, 2026-11-07).

Closed-form arithmetic, cross-checked point by point against the kit's own
ruling_1f_fit / max_fitting_b_d / w1_g0_cap on synthetic r1_slots built for
each grid point (worktree at e901eb2a4).  No model, no hardware, no data.
"""
import itertools
import math
import sys

WT = sys.argv[1] if len(sys.argv) > 1 else '.'
sys.path.insert(0, WT)
import os
os.chdir(WT)
from scripts import align_v4_kit as kit  # noqa: E402

# The two constants the kit re-reads on every call (a git show and a file read).
# Read once from the frozen sources, then cached so the grid runs in seconds.
_CAP_TOKENS = kit.d_turn_cap_tokens()
_G0_TIMEOUT = kit.r1_g0_timeout_s()
assert (_CAP_TOKENS, _G0_TIMEOUT) == (4096, 1200.0), (_CAP_TOKENS, _G0_TIMEOUT)
kit.d_turn_cap_tokens = lambda root=kit.ROOT: _CAP_TOKENS
kit.r1_g0_timeout_s = lambda root=kit.ROOT: _G0_TIMEOUT

F = kit.DEADMAN_FACTOR          # 1.13544
CAP = 4096                      # kit.d_turn_cap_tokens()
FLOOR = kit.BUDGET_FLOOR        # 6144
TAIL = 30.0                     # max_r1_tail_s (<= 40 s: L1 first term governs)


def t_dead(i_d, tail=TAIL, member_cap=1800):
    return min((member_cap - 50 - i_d) / F, (member_cap - i_d - tail - 10) / F)


def b_d_top(i_d, r, prefill_s=53.0, member_cap=1800):
    """Step-d's B_D (r1_runtime.derive_step_d_slots): no gates in it."""
    budget = ((member_cap - i_d) / F - prefill_s) * r
    return min(40960, max(0, 1024 * math.floor(budget / 1024)))


def worst(g0c, hg, pt, r, b_d):
    return g0c + hg + pt + (b_d + CAP) / r


def bd_max(g0c, hg, pt, r, td, top):
    best = None
    for b in range(min(top, 40960) // 1024 * 1024, FLOOR - 1, -1024):
        if worst(g0c, hg, pt, r, b) <= td + 1e-6:
            best = b
            break
    return best


def r_star(g0c, hg, pt, td, b_d=FLOOR):
    head = td - g0c - hg - pt
    return math.inf if head <= 0 else (b_d + CAP) / head


# ---------------------------------------------------------------- kit cross-check
def synthetic_slots(g0c, hg, pt, r, top):
    """r1_slots whose kit re-derivation gives exactly these terms."""
    if g0c == 1200:
        rows_g0 = [(1200.0, 'deadman')] + [(300.0, 'released')] * 2
        xg = {'status': 'measured', 'g0_outcome': 'released', 'g0_wait_s': 300.0}
    else:
        w = 480.0 if g0c == 600 else (g0c - 0.5) / 1.25   # ceil(1.25 w) == g0c
        rows_g0 = [(w, 'released')] * 3
        xg = {'status': 'measured', 'g0_outcome': 'released', 'g0_wait_s': w}
    rows = []
    for name, (g0, outcome) in zip(kit.GATED_D_RUN_NAMES, rows_g0):
        rows.append({'run': name, 'g0_outcome': outcome, 'decode_tokens': 4096,
                     'phases_s': {'G0': g0, 'G1': hg / 2, 'H': hg / 2, 'decode': 4096 / r,
                                  'prefill': pt * 0.75, 'tool': pt * 0.25, 'tail': 5.0}})
    return {'deadman_budget': rows, 'x_g': xg, 'slots': {'B_D': top},
            'budget_fit_inputs': {'r_decode_step_d_tok_per_s': r, 'turn_cap_tokens': CAP,
                                  'r_decode_tok_per_s': r}}


def cross_check():
    n = bad = 0
    for i_d, r, g0c, hg, pt in itertools.product((350, 400, 450, 520), (10, 12, 15, 20, 25, 30, 40),
                                                 (600, 700, 800, 900, 1000, 1200),
                                                 (0, 100, 300), (40, 80, 150)):
        td, top = t_dead(i_d), b_d_top(i_d, r)
        if top < 1024:
            continue
        slots = synthetic_slots(g0c, hg, pt, r, top)
        kit_cap = kit.w1_g0_cap(slots)['value_s']
        kit_max = kit.max_fitting_b_d(slots, td)
        mine = bd_max(g0c, hg, pt, r, td, top)
        n += 1
        if kit_cap != g0c or kit_max != mine:
            bad += 1
            print('MISMATCH', i_d, r, g0c, hg, pt, kit_cap, kit_max, mine)
    print(f'kit cross-check: {n} grid points, {bad} mismatches')


# ---------------------------------------------------------------- tables
def fmt(v):
    if v is None:
        return '—'
    if isinstance(v, float):
        return 'inf' if math.isinf(v) else f'{v:.1f}'
    return str(v)


def table(title, rows, cols, cell):
    print(f'\n### {title}\n')
    print('| ' + ' | '.join([''] + [str(c) for c in cols]) + ' |')
    print('|' + '---|' * (len(cols) + 1))
    for r in rows:
        print('| ' + ' | '.join([str(r)] + [fmt(cell(r, c)) for c in cols]) + ' |')


def main():
    cross_check()
    print('\nT_dead by I_D (tail 30 s):', {i: round(t_dead(i), 1) for i in (350, 400, 450, 520)})
    print('step-d B_D_top by r at I_D 400:', {r: b_d_top(400, r) for r in (11, 12, 15, 20, 25, 30)})

    G0 = (600, 700, 800, 900, 1000, 1100, 1200)
    R = (11, 12, 14, 15, 17.5, 20, 22.5, 25, 27.5, 30)
    for i_d in (350, 400, 520):
        td = t_dead(i_d)
        table(f'Required decode rate r* (tok/s) to fit B_D = 6,144 at I_D = {i_d} s (T_dead = {td:.0f} s); '
              'rows G0_cap_W1, columns HG + PT (s)',
              G0, (40, 100, 200, 300, 450, 600),
              lambda g, x: r_star(g, x, 0, td))

    td = t_dead(400)
    for hgpt in (60, 150, 300, 500):
        table(f'Largest fitting B_D (kit max_fitting_b_d), I_D 400 s (T_dead {td:.0f} s), HG + PT = {hgpt} s; '
              'rows r (tok/s), columns G0_cap_W1 (s)',
              R, G0, lambda r, g: bd_max(g, hgpt, 0, r, td, b_d_top(400, r)))

    table('Slack at the floor, T_dead - worst(B_D = 6,144) (s), I_D 400, HG + PT = 150 s; rows r, cols G0_cap_W1',
          R, G0, lambda r, g: td - worst(g, 150, 0, r, FLOOR))

    # Member cap needed (L1 restated against a cap C) to fit B_D = 6,144 (and B_D_top)
    print('\n### Member cap C needed for B_D = 6,144: C >= I_D + 1.13544*(G0c + HG + PT + 10240/r) + tail + 10\n')
    print('| scenario | I_D | G0c | HG | PT | r | episode worst (s) | C needed (s) |')
    print('|---|---|---|---|---|---|---|---|')
    scen = [
        ('8-bit optimistic', 380, 600, 150, 50, 12.5),
        ('8-bit central', 420, 800, 350, 80, 11.5),
        ('8-bit pessimistic', 520, 1200, 600, 150, 10.5),
        ('4-bit optimistic (proj.)', 370, 600, 80, 45, 21.5),
        ('4-bit central (proj.)', 410, 800, 200, 70, 19.5),
        ('4-bit pessimistic (proj.)', 510, 1200, 350, 140, 17.5),
    ]
    for name, i_d, g0c, hg, pt, r in scen:
        ep = worst(g0c, hg, pt, r, FLOOR)
        need = i_d + F * ep + TAIL + 10
        print(f'| {name} | {i_d} | {g0c} | {hg} | {pt} | {r} | {ep:.0f} | {need:.0f} |')
        print(f'|   (at 1,800 s cap: T_dead {t_dead(i_d):.0f} s, slack {t_dead(i_d) - ep:.0f} s, '
              f'B_D_max {bd_max(g0c, hg, pt, r, t_dead(i_d), b_d_top(i_d, r))}) | | | | | | | |')

    # Window arithmetic for raised D member cost
    print('\n### W1 window vs D member cost (A1 law: span = ceil(4995 + sum member_s); '
          'window = 60*ceil((span + 17700)/60))\n')
    print('| D member_s | 18 members: span / window | drop 18: span / window | fits 44,640? | fits 59,520? |')
    print('|---|---|---|---|---|')
    fixed = 3131.27 + 4 * 850 + 4 * 1150
    for d in (1800, 2100, 2400, 2700, 3000, 3300):
        out = []
        for n_d in (6, 5):
            span = math.ceil(4995 + fixed + n_d * d)
            win = 60 * math.ceil((span + 17700) / 60)
            out.append((span, win))
        ok44 = 'yes' if out[0][0] <= 26940 else ('drop 18' if out[1][0] <= 26940 else 'no')
        ok59 = 'yes' if out[0][1] <= 59520 else ('drop 18' if out[1][1] <= 59520 else 'no')
        print(f'| {d} | {out[0][0]} / {out[0][1]} | {out[1][0]} / {out[1][1]} | {ok44} | {ok59} |')

    print('\n### D_k window capacity at the 59,520 s maximum (span cap 41,820 s; 4 anchors + 2 sentinels fixed)\n')
    print('| D member_s | D members per window | held-out per window | windows for 48 held-out (42 benign + 6 sabotage) |')
    print('|---|---|---|---|')
    for d in (1800, 2100, 2400, 2700, 3000, 3300):
        n_d = math.floor((59520 - 17700 - 4995 - 3131.27) / d)
        held = n_d - 2
        print(f'| {d} | {n_d} | {held} | {math.ceil(48 / held)} |')

    # Contrast members under a long G0 cap
    cd = kit.CONTRAST_DEADMAN_S
    print(f'\nContrast deadman {cd:.1f} s covers G0 + G1 + episode; member bound 516.58 + 1.13544*{cd:.1f} = '
          f'{516.5751274713251 + F * cd:.1f} s.')
    for g0 in (300, 600, 800, 1000):
        print(f'  contrast G0 {g0} s leaves {cd - g0:.0f} s for G1 + the pilot-7-count episode')

    # 1(e) step 2 arithmetic
    print('\n1(e) step 2 (idle +150 s inside the member): T_dead falls by', round(150 / F, 1),
          's for every member that carries it; G0_cap_W1 can fall by at most 1.25 x 150 =', 1.25 * 150,
          's (only if uncensored and above the 600 s floor). Net headroom change in [-132.1, +55.4] s.')
    print('contrast members after D with +150 s idle: member bound', round(516.5751274713251 + 150 + F * cd, 1),
          's > 1,800 unless their deadman drops to', round((1750 - 516.5751274713251 - 150) / F, 1), 's')


if __name__ == '__main__':
    main()
