from pathlib import Path
p=Path('/tmp/278ebc9e/r4ref/predicate/joulewise/scored_packer.py')
s=p.read_text(); a=s.index('def _parent_facts('); b=s.index('\n\ndef _lever(',a)
s=s[:a]+'''def _ownership(registration, roster):
    from collections import defaultdict
    blocks = {b['block_id']: b for b in roster['blocks']}
    live = defaultdict(list)
    term = defaultdict(list)
    placement = {(p['block_id'], p['envelope_index']): p for p in roster['placements']}
    for e in roster['envelopes']:
        for bid in e['blocks']:
            b = blocks[bid]
            for item in set(b['items']):
                live[b['model'], item].append((bid,e['index']))
    for t in roster['terminal_refusals']:
        term[t['model'], t['item_id']].append(t)
    return dict(blocks=blocks, live=live, term=term, placement=placement)


def _conserve(registration, view):
    for model in registration.role_to_model_id.values():
        for item in _items(registration):
            holders = view['live'][model,item]
            terminal = view['term'][model,item]
            _need((len(holders), len(terminal)) in ((1,0),(0,1)), 'inv_11', 'item conservation')
            if holders:
                holder = view['blocks'][holders[0][0]]
                _need(not holder['superseded'], 'inv_11', 'item conservation')
                _need(not any(view['term'][model,x] for x in holder['items']), 'inv_11', 'item conservation')


def _parent_facts(registration, roster, captured_window_keys=None):
    view = _ownership(registration, roster)
    facts = []
    for parent in view['blocks'].values():
        if parent['parent_block_id'] is not None:
            continue
        model = parent['model']
        indices = []
        n_terminal = 0
        for item in parent['items']:
            if view['term'][model,item]:
                n_terminal += 1
                continue
            live = view['live'][model,item]
            placement = view['placement'].get(live[0]) if len(live) == 1 else None
            if placement is not None and (captured_window_keys is None or
                    (placement['block_id'], placement['attempt']) in captured_window_keys):
                indices.append(placement['envelope_index'])
        facts.append(dict(parent_id=parent['block_id'], model=model, level=parent['level'],
                          n_items=len(parent['items']), n_terminal=n_terminal, indices=indices))
    return facts
'''+s[b:]
s=s.replace('    _need(all(type(p["attempt"])', '    _conserve(registration, _ownership(registration, roster))\n    _need(all(type(p["attempt"])',1)
a=s.index('    terminal = roster["terminal_refusals"]\n    live_counts = {}');b=s.index('    children = {}',a);s=s[:a]+s[b:]
# R4-2(d) implement complete canonical parent formation after ownership/event/child checks.
pos=s.index('\n\ndef _seal(')
s=s[:pos]+'''
    expected = []
    width = registration.block_size[registration.arm]
    for level in LEVELS:
        ids = registration.item_ids_by_level[str(level)]
        for model in models:
            for k, start in enumerate(range(0,len(ids),width)):
                expected.append((f'{model}:{registration.arm}:{level}:{k}', model, level, ids[start:start+width]))
    parents = [b for b in roster['blocks'] if b['parent_block_id'] is None]
    _need([(b['block_id'],b['model'],b['level'],b['items']) for b in parents] == expected, 'inv_10', 'parent formation')
'''+s[pos:]
p.write_text(s)
