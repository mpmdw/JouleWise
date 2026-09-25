from pathlib import Path
root=Path('/tmp/278ebc9e/r4ref/baseline')
p=root/'tests/scored_ownership_generator.py'
s=p.read_text().replace('TRIPLE_SAMPLE = 128\nTRIPLE_SEED = 291013\n','')
s=s.replace("    r['blocks'].remove(rng.choice(choices))", "    b = rng.choice(choices)\n    bid = b['block_id']\n    r['blocks'].remove(b)\n    r['placements'] = [p for p in r['placements'] if p['block_id'] != bid]\n    for e in r['envelopes']:\n        for key in ('blocks', 'voided_block_ids'):\n            e[key] = [x for x in e[key] if x != bid]")
s=s.replace('OPERATORS = (', '''def drop_terminal_entry(r, rng):
    if not r['terminal_refusals']:
        return False
    r['terminal_refusals'].pop(rng.randrange(len(r['terminal_refusals'])))
    return True


def duplicate_terminal_entry(r, rng):
    if not r['terminal_refusals']:
        return False
    r['terminal_refusals'].append(deepcopy(rng.choice(r['terminal_refusals'])))
    return True


def copy_item_into_live_block(r, rng):
    ids = {bid for e in r['envelopes'] for bid in e['blocks']}
    choices = [(a,b) for a in r['blocks'] for b in r['blocks']
               if a['block_id'] in ids and b['block_id'] in ids
               and a['block_id'] != b['block_id'] and a['model'] == b['model']]
    if not choices:
        return False
    a,b = rng.choice(choices)
    b['items'].append(rng.choice(a['items']))
    return True


OPERATORS = (''').replace('flip_superseded, drop_single)', 'flip_superseded, drop_single, drop_terminal_entry,\n             duplicate_terminal_entry, copy_item_into_live_block)')
s=s.replace('        rng = random.Random(TRIPLE_SEED)\n        all_combos = list(product(OPERATORS, repeat=3))\n        return rng.sample(all_combos, TRIPLE_SAMPLE)','        return list(product(OPERATORS, repeat=3))')
p.write_text(s)
p=root/'tests/scored_roster_checker.py';s=p.read_text();a=s.index('    # INV-11 (02d:');b=s.index("    for i, e in enumerate(r['envelopes']):",a)
s=s[:a]+'''    live = {}
    for e in r['envelopes']:
        for bid in e['blocks']:
            if bid not in bm:
                continue
            b = bm[bid]
            for item in set(b['items']):
                live.setdefault((b['model'], item), []).append(b)
    terminal = {}
    for t in r['terminal_refusals']:
        terminal.setdefault((t['model'], t['item_id']), []).append(t)
    for m in models:
        for item in ids:
            holders = live.get((m,item), [])
            named = terminal.get((m,item), [])
            valid = ((len(holders), len(named)) in ((1,0),(0,1)))
            if valid and holders:
                valid = not holders[0]['superseded'] and not any(terminal.get((m,x)) for x in holders[0]['items'])
            if not valid:
                _bad(out, 'INV-11', f'item ownership {m}:{item}')
'''+s[b:];p.write_text(s)
p=root/'tests/test_scored_ownership_forgery.py';s=p.read_text();s=s.replace('    return g, p, reg, out','''    m = deepcopy(b1)
    e = m['envelopes'][voided['index']]
    singles = {b['block_id'] for b in m['blocks'] if b['parent_block_id'] == parent['block_id']}
    for bid in list(e['blocks']):
        if bid in singles:
            e['blocks'].remove(bid)
            e['voided_block_ids'].append(bid)
    out['B1-singles-voided'] = m
    m = deepcopy(base)
    a, b = next((i,j) for i,x in enumerate(m['blocks']) for j,y in enumerate(m['blocks'])
                if x['parent_block_id'] is None and y['parent_block_id'] is None
                and x['model'] != y['model'] and x['level'] == y['level'])
    m['blocks'][a], m['blocks'][b] = m['blocks'][b], m['blocks'][a]
    out['cross-model-reorder'] = m
    return g, p, reg, out''')
s=s.replace("('AUD-1', 'B1', 'B2', 'probe-D')", "('AUD-1', 'B1', 'B2', 'probe-D', 'B1-singles-voided')")
s=s.replace('g, _, _, witnesses = _named_witnesses()', 'g, p, _, witnesses = _named_witnesses()')
s=s.replace('            self.assertTrue(bad, name)', '''            self.assertTrue(bad, name)
            self.assertIn('INV-11', _checker_rows(g, witnesses[name], p), name)
            if name == 'B1-singles-voided':
                self.assertIn('superseded_live', [v.reason for v in bad])''')
s=s.replace("        print('NAMED legal-contrast oracle=ACCEPT', flush=True)","""        self.assertEqual([], ownership_violations(g, witnesses['cross-model-reorder']))
        for name in ('legal-contrast', 'cross-model-reorder'):
            self.assertNotIn('INV-11', _checker_rows(g, witnesses[name], p))
        print('NAMED legal-contrast oracle=ACCEPT', flush=True)""")
s=s.replace("            self.assertTrue(outcomes[name].startswith('refused:'), (name, outcomes[name]))", "            self.assertEqual('refused:inv_11', outcomes[name], name)\n        self.assertEqual('refused:inv_10', outcomes['cross-model-reorder'])")
s=s.replace('    def _seal_property(self, arity):', '''    def test_legal_corpus_seal(self):
        count = 0
        refusals = []
        for seed in range(291013, 291017):
            for i in range(12):
                case = generate_case(seed, i)
                for k, roster in enumerate(case.rosters):
                    m = deepcopy(roster)
                    refresh_derived(case.g, m)
                    m['sha256'] = None
                    if m['events']:
                        m['events'][-1]['sha256'] = ''
                    try:
                        _seal(case.reg, m, finalize=True)
                    except PackingRefusal as exc:
                        refusals.append((seed,i,k,str(exc)))
                    else:
                        count += 1
        print('LEGAL_SEAL accepted=' + str(count) + ' refused=' + str(len(refusals)) + ' first=' + repr(refusals[:10]), flush=True)
        self.assertEqual(1868, count)

    def _seal_property(self, arity):''')
s=s.replace('        inconclusive = []','        inconclusive = []\n        refusal_codes = Counter()\n        checker_disagreements = []')
s=s.replace("                if outcome != 'ready':", """                if outcome.startswith('refresh_error:'):
                    try:
                        _seal(case.reg, m, finalize=True)
                    except PackingRefusal:
                        pass
                    except Exception as exc:
                        seal_crashes.append((combo, case.seed, case.i, k, type(exc).__name__, str(exc)))
                    else:
                        seal_crashes.append((combo, case.seed, case.i, k, 'accepted-refresh-error'))
                if outcome != 'ready':""")
s=s.replace('                    _checker_rows(case.g, m, case.p)', "                    rows = _checker_rows(case.g, m, case.p)\n                    if 'INV-52' not in rows and 'INV-11' not in rows:\n                        checker_disagreements.append((combo, case.seed, case.i, k, sorted(rows)))")
s=s.replace('                except PackingRefusal:\n                    continue','                except PackingRefusal as exc:\n                    refusal_codes[exc.code] += 1\n                    continue')
s=s.replace('f\'seal_crashes={len(seal_crashes)} runtime_s=', 'f\'seal_crashes={len(seal_crashes)} checker_disagreements={len(checker_disagreements)} refusal_codes={json.dumps(refusal_codes,sort_keys=True)} runtime_s=')
s=s.replace("        self.assertFalse(escapes,", "        self.assertFalse(checker_disagreements, repr(checker_disagreements[:10]))\n        self.assertEqual(0, totals['operator_error'])\n        self.assertEqual(0, totals['refresh_error'])\n        self.assertFalse(escapes,")
p.write_text(s)
