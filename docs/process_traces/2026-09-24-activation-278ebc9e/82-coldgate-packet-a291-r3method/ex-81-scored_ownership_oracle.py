"""Independent, closed INV-11 predicate from A291-ESC2-01 K1.

The roster and registration are data inputs. This module deliberately imports
neither the packer nor the independent roster checker.
"""

from collections import defaultdict
from typing import NamedTuple


class OwnershipViolation(NamedTuple):
    model: str
    item: str
    live: int
    terminal: int
    reason: str


def ownership_violations(registration, roster):
    """Return every registered item that fails the closed ownership rule.

    Every envelope listing counts, including listings of superseded and
    terminal blocks. A live holder may not be superseded or contain *any*
    terminal item, even when that terminal entry names another block.
    """
    blocks = {b['block_id']: b for b in roster['blocks']}
    live = defaultdict(list)
    for envelope in roster['envelopes']:
        for block_id in envelope['blocks']:
            block = blocks[block_id]
            for item in set(block['items']):
                live[block['model'], item].append((block_id, envelope['index']))

    terms = defaultdict(list)
    for entry in roster['terminal_refusals']:
        terms[entry['model'], entry['item_id']].append(entry)

    violations = []
    items = (item for level in range(1, 6)
             for item in registration['item_ids_by_level'][str(level)])
    registered_items = tuple(items)
    for model in registration['role_to_model_id'].values():
        for item in registered_items:
            holders = live[model, item]
            terminal = terms[model, item]
            counts = (len(holders), len(terminal))
            if counts not in ((1, 0), (0, 1)):
                reason = 'counts'
            elif holders:
                holder = blocks[holders[0][0]]
                if holder['superseded']:
                    reason = 'superseded_live'
                elif any(terms[model, held_item] for held_item in holder['items']):
                    reason = 'terminal_item_in_live_holder'
                else:
                    continue
            else:
                continue
            violations.append(OwnershipViolation(model, item, *counts, reason))
    return violations
