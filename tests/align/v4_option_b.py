"""Shared witness for the RUN_STATE 252 option-B manifest regeneration (claim contract B5/B6).

Option B moves the sabotage-instructed member of each pair to a seeded ordinal and appends the test reserves
T4-T5, so earlier seed-checked windows are no longer byte-identical. What must survive is everything the
earlier paired seed checks matched: every member's ordinal, pair, model, seed index, episode seed and first
turn seed, and every window field other than the member conditions/pools and the new ``sabotage_ordinals``.
The only permitted change inside a window is which fresh ordinal of each pair is sabotage-instructed.
"""

SEED_FIELDS = ('ordinal', 'pair', 'model_id', 'seed_index', 'episode_seed', 'turn_seed_0')
# The manifest bytes regenerated under option B (seeded sabotage ordinals, test reserves T4-T5).
OPTION_B_MANIFEST_SHA256 = '70009b6a594835643ef0bb2ff324ed700447cbe7a6237975ebdb209ec2c78dd6'


def assert_seed_preserved(case, old, new):
    """``old``: a window from an earlier seed-checked manifest; ``new``: the same window id now."""
    case.assertEqual({k: v for k, v in old.items() if k != 'members'},
                     {k: v for k, v in new.items() if k not in ('members', 'sabotage_ordinals')}, old['id'])
    case.assertEqual([{k: m[k] for k in SEED_FIELDS} for m in old['members']],
                     [{k: m[k] for k in SEED_FIELDS} for m in new['members']], old['id'])
    if old['id'] == 'W1':
        case.assertEqual(old, new)                       # W1 is selection data: wholly unchanged
        return
    for before, after in zip(old['members'], new['members'], strict=True):
        if not 6 <= before['ordinal'] <= 21:
            case.assertEqual(before, after, (old['id'], before['ordinal']))
    for pair in {m['pair'] for m in new['members'] if 6 <= m['ordinal'] <= 21}:
        fresh = [m for m in new['members'] if 6 <= m['ordinal'] <= 21 and m['pair'] == pair]
        sabotage = [m['ordinal'] for m in fresh if m['condition'] == 'sabotage']
        case.assertEqual(sabotage, [new['sabotage_ordinals'][pair]], (old['id'], pair))
        for m in fresh:
            role = new['role']
            case.assertEqual(m['pool'], role if m['condition'] == 'benign' or role == 'test' else 'known_h')
