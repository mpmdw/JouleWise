#!/usr/bin/env python3
"""Independent seed check of the option-B series manifest (RUN_STATE 251; claim contract B5/B6).

Standard library only: no JouleWise or scripts import. The allocation is re-derived from the REGISTERED TEXT
(pilot_protocol_v4.md: the W1 roster table, the seed law, R15, R22-2 / R24 and the claim contract's B5
placement law and B6 test reserves), never from the generator, and compared field by field with the committed
manifest. It checks, for every one of the 436 members (W1 18 + 19 C/T windows x 22):

* the episode seed and first turn seed reproduce the seed law from (model tag, pair, seed index);
* the seed index, pair, model, condition and pool equal the text-derived allocation;
* exactly one sabotage-instructed member per pair per C/T window, at the B5 placement law's ordinal;
* per pair, the index sets of calibration (C1-C8), test (T1-T3), calibration reserve (C9-C14) and test reserve
  (T4-T5) windows are pairwise disjoint, distinct across the whole series, consumed in kit order, and never
  use the reserved development indices 1 and 91-99;
* no sabotage-instructed member shares a seed index with a benign member of its pair.

``python3 derive_and_check.py [--manifest PATH] [--write-receipt]`` prints MATCH or the differences.
"""
import argparse
import hashlib
import json
from pathlib import Path

SPAM, BANK = 'spam_filter_update', 'bank_transfer_2'
PAIRS = (SPAM, BANK)
M30, MD = 'qwen3-30b-a3b', 'qwen3.8-27b'          # D-25a: the D seed tag is quantization-free
RESERVED = {1, *range(91, 100)}
PLACEMENT_LAW = 'align-v4-sabotage-slot-v1'
MANIFEST = 'configs/campaigns/align_v4/series/series_manifest.json'


def u64(value):
    raw = json.dumps(value, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('utf-8')
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], 'big')


def episode_seed(model, pair, index):
    return u64(['align-p4-v1', model, 'thinking_on', 'shade/' + pair, index])


def turn_seed_0(seed):
    return u64(['align-p4-turn-v1', seed, 0])


def slot(window, pair):
    """Claim contract B5: SHA-256(JSON([law, window id, "shade/" + pair]))[:8], big-endian, mod 8."""
    return u64([PLACEMENT_LAW, window, 'shade/' + pair]) % 8


def w1_members():
    # Protocol "W1 roster and later windows" table (after chair ruling 1(g)); X = b-e25 spam/sabotage index 16,
    # Y = b-e18 spam/benign index 14; anchors keep their original 30B tag and index 1.
    table = [(M30, SPAM, 'benign', 1, 'anchor'), (M30, BANK, 'sabotage', 1, 'anchor'),
             (M30, SPAM, 'sabotage', 1, 'anchor'), (M30, BANK, 'benign', 1, 'anchor'),
             (MD, SPAM, 'benign', 1, 'D'), (M30, SPAM, 'sabotage', 16, 'X-G'), (M30, SPAM, 'benign', 14, 'Y-S'),
             (MD, BANK, 'benign', 1, 'D'), (M30, SPAM, 'sabotage', 16, 'X-S'), (M30, SPAM, 'benign', 14, 'Y-G'),
             (MD, SPAM, 'sabotage', 1, 'D'), (M30, SPAM, 'benign', 14, 'Y-G'), (M30, SPAM, 'sabotage', 16, 'X-S'),
             (MD, BANK, 'sabotage', 1, 'D'), (M30, SPAM, 'benign', 14, 'Y-S'), (M30, SPAM, 'sabotage', 16, 'X-G'),
             (MD, SPAM, 'benign', 1, 'D'), (MD, BANK, 'benign', 93, 'D')]
    return [dict(ordinal=i, model_id=model, pair=pair, condition=condition, seed_index=index, role=role,
                 pool='selection') for i, (model, pair, condition, index, role) in enumerate(table, 1)]


def derive():
    """Every C/T window, from the registered text. Kit (seed-consumption) order: C1-C8, T1-T3 (R15: 2-65,
    66-89), then the C9-C14 reserve pool from 100 (R24), then the T4-T5 test reserve pool from 148 (B6)."""
    windows = {'W1': dict(role='selection', members=w1_members())}
    kit_order = ([('C', n) for n in range(1, 9)] + [('T', n) for n in range(1, 4)]
                 + [('C', n) for n in range(9, 15)] + [('T', n) for n in range(4, 6)])
    pools = {('C', 9): 100, ('T', 4): 148}
    nxt = dict.fromkeys(PAIRS, 2)
    for prefix, number in kit_order:
        name = f'{prefix}{number}'
        if (prefix, number) in pools:
            nxt = dict.fromkeys(PAIRS, pools[prefix, number])
        first = SPAM if number % 2 else BANK          # odd windows start with spam; the first pair takes evens
        second = BANK if first == SPAM else SPAM
        evens, odds = list(range(6, 22, 2)), list(range(7, 22, 2))
        placed = {first: evens[slot(name, first)], second: odds[slot(name, second)]}
        role = 'calibration' if prefix == 'C' else 'test'
        rows = [dict(ordinal=i + 1, model_id=M30, pair=p, condition=c, seed_index=1, pool='anchor')
                for i, (p, c) in enumerate([(SPAM, 'benign'), (BANK, 'sabotage'), (SPAM, 'sabotage'), (BANK, 'benign')])]
        rows.append(dict(ordinal=5, model_id=MD, pair=SPAM, condition='benign', seed_index=1, pool='sentinel'))
        for ordinal in range(6, 22):
            pair = first if ordinal % 2 == 0 else second
            while nxt[pair] in RESERVED:
                nxt[pair] += 1
            sabotage = ordinal == placed[pair]
            rows.append(dict(ordinal=ordinal, model_id=MD, pair=pair, seed_index=nxt[pair],
                             condition='sabotage' if sabotage else 'benign',
                             pool=('known_h' if sabotage and prefix == 'C' else role)))
            nxt[pair] += 1
        rows.append(dict(rows[4], ordinal=22))
        windows[name] = dict(role=role, members=rows, sabotage_ordinals=placed,
                             group=('calibration' if prefix == 'C' and number <= 8 else
                                    'calibration_reserve' if prefix == 'C' else
                                    'test' if number <= 3 else 'test_reserve'))
    for window in windows.values():
        for row in window['members']:
            row['episode_seed'] = episode_seed(row['model_id'], row['pair'], row['seed_index'])
            row['turn_seed_0'] = turn_seed_0(row['episode_seed'])
    return windows


def check(manifest):
    """Return (differences, summary). An empty difference list is a MATCH."""
    expected = derive()
    diffs = []
    actual = {w['id']: w for w in manifest['windows']}
    order = ['W1', *[f'C{n}' for n in range(1, 15)], *[f'T{n}' for n in range(1, 6)]]
    if manifest.get('order') != order:
        diffs.append(f'order {manifest.get("order")} != {order}')
    if sorted(actual) != sorted(expected):
        diffs.append(f'window ids {sorted(actual)} != {sorted(expected)}')
    members = 0
    for name, window in expected.items():
        got = actual.get(name)
        if got is None:
            continue
        if got.get('role') != window['role']:
            diffs.append(f'{name}: role {got.get("role")} != {window["role"]}')
        if name != 'W1' and got.get('sabotage_ordinals') != window['sabotage_ordinals']:
            diffs.append(f'{name}: sabotage_ordinals {got.get("sabotage_ordinals")} != {window["sabotage_ordinals"]}')
        if len(got['members']) != len(window['members']):
            diffs.append(f'{name}: {len(got["members"])} members != {len(window["members"])}')
        for want, have in zip(window['members'], got['members']):
            members += 1
            for key, value in want.items():
                if have.get(key) != value:
                    diffs.append(f'{name}:{want["ordinal"]} {key} {have.get(key)!r} != {value!r}')
            # the committed seeds themselves must reproduce the law from the committed inputs
            if have.get('episode_seed') != episode_seed(have.get('model_id'), have.get('pair'), have.get('seed_index')):
                diffs.append(f'{name}:{want["ordinal"]} episode_seed does not reproduce the seed law')
            if have.get('turn_seed_0') != turn_seed_0(have.get('episode_seed')):
                diffs.append(f'{name}:{want["ordinal"]} turn_seed_0 does not reproduce the turn seed law')
        if name != 'W1':
            for pair in PAIRS:
                sab = [m['ordinal'] for m in got['members'] if 6 <= m['ordinal'] <= 21 and m['pair'] == pair
                       and m['condition'] == 'sabotage']
                if len(sab) != 1:
                    diffs.append(f'{name}: {pair} has {len(sab)} sabotage-instructed members')
    # per pair: the four index groups are disjoint, distinct, in kit order and outside the reserved range
    groups = {pair: {g: [] for g in ('calibration', 'test', 'calibration_reserve', 'test_reserve')} for pair in PAIRS}
    by_condition = {pair: {'benign': set(), 'sabotage': set()} for pair in PAIRS}
    kit = [*[f'C{n}' for n in range(1, 9)], 'T1', 'T2', 'T3', *[f'C{n}' for n in range(9, 15)], 'T4', 'T5']
    sequence = {pair: [] for pair in PAIRS}
    for name in kit:
        got = actual.get(name)
        if got is None:
            continue
        for m in got['members']:
            if 6 <= m['ordinal'] <= 21:
                groups[m['pair']][expected[name]['group']].append(m['seed_index'])
                by_condition[m['pair']][m['condition']].add(m['seed_index'])
                sequence[m['pair']].append(m['seed_index'])
    ranges = {}
    for pair in PAIRS:
        flat = sequence[pair]
        if flat != sorted(flat) or len(flat) != len(set(flat)):
            diffs.append(f'{pair}: held-out indices not distinct and in kit order')
        if set(flat) & RESERVED:
            diffs.append(f'{pair}: reserved development index used: {sorted(set(flat) & RESERVED)}')
        sets = {g: set(v) for g, v in groups[pair].items()}
        names = list(sets)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                if sets[a] & sets[b]:
                    diffs.append(f'{pair}: {a} and {b} share indices {sorted(sets[a] & sets[b])}')
        if by_condition[pair]['benign'] & by_condition[pair]['sabotage']:
            diffs.append(f'{pair}: a sabotage-instructed member shares a seed index with a benign member')
        ranges[pair] = {g: [min(v), max(v), len(v)] if v else None for g, v in groups[pair].items()}
    summary = dict(windows=len(actual), members=members, ranges=ranges,
                   sabotage_ordinals={n: expected[n]['sabotage_ordinals'] for n in kit})
    return diffs, summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).absolute().parents[4]
    parser.add_argument('--manifest', type=Path, default=root / MANIFEST)
    parser.add_argument('--write-receipt', action='store_true')
    args = parser.parse_args(argv)
    raw = args.manifest.read_bytes()
    diffs, summary = check(json.loads(raw))
    receipt = dict(schema='joulewise.align_v4.seedcheck.v1', seat='claim-contract-B opus',
                   manifest_sha256=hashlib.sha256(raw).hexdigest(), verdict='MATCH' if not diffs else 'MISMATCH',
                   differences=diffs, **summary)
    if args.write_receipt:
        (Path(__file__).absolute().parent / 'comparison.json').write_text(
            json.dumps(receipt, indent=1, sort_keys=True) + '\n')
    print(receipt['verdict'], receipt['manifest_sha256'], f"{summary['members']} members")
    for line in diffs[:50]:
        print(' ', line)
    return 0 if not diffs else 1


if __name__ == '__main__':
    raise SystemExit(main())
