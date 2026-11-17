"""Apply the audit's renewal changes to the preserved item 346 source."""

RULE_7 = """7. **Preserve the remaining counted schedule.** F0's launch plus 12,180 s and its 1,200 s close interval must fit before the effective t0 cutoff of every outstanding counted span it could delay. A span's last legal whole second is the earliest of its window end, its exclusive item expiry minus one, and its exclusive queue expiry minus one. When two outstanding spans are dependent, also work back from s02's last legal second by s01's bounded duration (including any allowed soak retry and cleanup reserve) and the campaign close interval of at least 300 s. Compare the F0 handoff to the earlier of this result and s01's own limit. Include a dated dependent s02 whose hand gate prevents issue, using its prospective window/queue bounds until issued. Use the actual item expiry once issued. When s01 has closed, protect s02 on its own. Retain any later proven fence, Check, copy or hand-read timing in the readiness assessment."""

RULE_7_CODE = """def latest(span):
    window_end, item_expiry, queue_expiry = span.split(":")
    bounds = [int(window_end)]
    bounds.extend(int(value) - 1 for value in (item_expiry, queue_expiry) if value != "-")
    if min(bounds) <= 0:
        raise ValueError("nonpositive cutoff")
    return min(bounds)

census = sys.argv[2].split()
try:
    if not census:
        raise ValueError("missing census")
    for entry in ([] if census == ["none"] else census):
        parts = entry.split("/")
        if len(parts) == 1:
            bound = latest(entry)
        elif len(parts) == 3:
            first, second, budget = parts
            first_s, close_s = map(int, budget.split(":"))
            if first_s <= 0 or close_s < 300:
                raise ValueError("invalid dependent-span budget")
            bound = min(latest(first), latest(second) - first_s - close_s)
        else:
            raise ValueError("invalid census row")
        # Eligibility is reported in whole seconds. Keep the exclusive next-second boundary.
        if now + 12180 + 1200 >= bound + 1:
            sys.exit(f"STOP: F0 would cost a counted span its effective t0 (rule 7; latest {bound})")
except ValueError as error:
    sys.exit(f"STOP: invalid counted schedule (rule 7): {error}")
"""

ORDER = """   - **Order (RL-174 B).** A READY v4 session, then counted work, then F0, then F2, hp-02 and DESIGN_QUEUE_LOW. An F2 item whose priority gate fails is not a staged item for trigger (c). Counted work which can launch now takes precedence. Rule 7 protects its remaining dated schedule."""

CENSUS = """#   SESSION_READY  R-A (the lead's READY record, RL-172 (f))
#   COUNTED_SCHEDULE  rule 7. Re-read every outstanding staged counted item and its dated successors,
#     including those that become due during F0's handoff. Use space-separated rows or explicit none
#     after a complete census. A single span row is window_end:item_expiry:queue_expiry (whole epochs).
#     Use "-" for an unissued prospective item expiry or an absent expiry only when the law allows it.
#     A dependent pair row is first/second/first_bound_s:close_s, with both spans in the same format.
#     For a pending qualification pair, record 27260:300 or a longer proven first-to-second bound.
#     Supply actual issue + 86400 and authenticated queue expiry wherever applicable. Missing evidence stops.
"""


def replace_line(text, prefix, replacement):
    lines = text.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if len(matches) != 1:
        raise ValueError(f'expected one item 346 line starting with {prefix!r}')
    lines[matches[0]] = replacement + '\n'
    return ''.join(lines)


def repair_standing(text):
    text = replace_line(text, '7. **It never costs', RULE_7)
    text = replace_line(text, '   - **Order (RL-165', ORDER)
    text = text.replace("From the lead's record that a v4 session is READY,",
                        "From the effective v4 READY record under RL-175 A.2,")
    old_host_rule = next(line for line in text.splitlines() if line.startswith('8. **Host state and the restart'))
    keep_from = old_host_rule.index("The lead's journal-copy marker")
    text = replace_line(text, '8. **Host state and the restart',
                        '8. **Host state (RL-174 C).** ' + old_host_rule[keep_from:].replace(' **Host state.**', ''))
    text = replace_line(text, '  case "${RESTART_PENDING:-}"', '  # RL-174 C closes the restart hold.')
    text = replace_line(text, '#   SESSION_READY, COUNTED_LATEST', CENSUS.rstrip())
    text = replace_line(text, '#                       of every staged counted span', '')
    start = text.index('for e in ([] if sys.argv[2]')
    end = text.index('print(int(now))', start)
    text = text[:start] + RULE_7_CODE + text[end:]
    text = text.replace('COUNTED_LATEST', 'COUNTED_SCHEDULE').replace('RESTART_PENDING, ', '')
    text = text.replace('It EXPIRES 7 days after issue.', 'It expires seven days after the actual issue, even when issued ahead.')
    text = replace_line(text, '# RL-89 Mac check', '# RL-89 Mac check using item 377’s verified restored copy (LQ5).')
    text = replace_line(text, 'R0=', 'R0="$CUSTODY/standing-f0/r0-restore-ade002e9/r0.json"')
    text = text.replace('"$REPO/configs/align/v4/r1_runtime.json" <<\'PY\'',
                        '"$REPO/configs/align/v4/r1_runtime.json" <<\'PY\' || exit 1')
    text = text.replace('"mobileassetd"}', '"mobileassetd","bird","cloudd","fileproviderd"}')
    text = text.replace('Nothing is judged on it.', 'Nothing is judged on it. Earlier queries without the three cloud jobs recorded them as unobserved.')
    return text
