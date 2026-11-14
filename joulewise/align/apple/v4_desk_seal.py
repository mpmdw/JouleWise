"""ALIGN v4 per-window desk release guard (desk-leak audit, 2026-11-13).

The common desk (``scripts/align_pilot_session.py:desk``) computes and prints per-member residual
scores, energy on every rail, task scores, tool structure and battery discharge. In a C or T window
that breaks protocol v4 B0 (:1099-1101: the K decision, every S leaf and every C-window
sabotage-instructed leaf are computed only in the release run; incremental runs print
``withheld_until_series_complete``), B2 (:1170-1173), B9 (:1421-1424), the DC seal (:828-829,
MED-4), B7 (:1383: secondaries are computed in the release run) and R27/A25 (thresholds and T
scores withheld until ``calibration_complete``).

This module is the guard. Before release, in a C or T window, the desk prints and records only an
ALLOWLIST: per member the identity, pool role, exclusion and eligibility fields and flag codes;
every other value is replaced by ``{status: withheld_until_series_complete, sha256: <canonical
JSON>}``; the window's analyses become a hash plus window-pooled instrument figures that carry no
member or cell key. The unsealed PILOT is written to ``archive/withheld/PILOT.full.json`` (the
session's withheld archive, beside the harvest's ``archive/withheld/battery-assist.json``) for the
release run. W1 (selection data) has its own scope (:data:`W1_WITHHOLD_SABOTAGE_GPU_AND_OUTCOMES`, ON by
RL-149 section 3(a)) with one exception class, the registered W1 outputs that need a non-benign member's
value (:data:`W1_EXCEPTIONS`): they are computed in memory from the full records and print as their
registered output only. Release for W1's withheld values is the series' release event.

RL-149 section 3 carve-out: codes that say a member was truncated or heat-ended (:data:`CARVE_OUT_CODES`)
print only as a window count over all members, never per member (X2's G1-timeout column likewise); codes
for instrument and identity faults stay per member. RL-149 3(c): no pooled figure is an extreme-value
statistic over a set holding a non-benign member, and no heat-bearing quantity prints per member.

RL-151 section 4: per-member code lists print as codes, never the text after the first ':' (C1(a)); in W1 no
printed figure gives a carved count over the non-benign members alone (pooled carved counts and the R10 count
are over benign members, U1's all-member counts are withheld, the section 1.5 tripwire prints its verdict;
C2, C3); a released desk records and prints that it ran released (C4). Withheld digests are keyed (see
:func:`keyed_digest`).

:func:`released` is True only on a registered release event (a committed ``series_complete``
record plus a lead-signed release receipt); no such record exists today. Pure stdlib; it reads
only the two release files and the series manifest, never energy, transcript or meter bytes.
"""
from __future__ import annotations

import contextlib
import hashlib
import hmac
import json
import secrets
import math
import os
from pathlib import Path
import re

WITHHELD = 'withheld_until_series_complete'
WITHHELD_PILOT = 'archive/withheld/PILOT.full.json'
SERIES_MANIFEST = 'configs/campaigns/align_v4/series/series_manifest.json'
# The release event (protocol B0 :1099-1101, B2 :1173, B7 :1383): "computed only in the release run, after
# the last admitted test window's eligibility is final". The record names that window and its final
# eligibility; the receipt is the lead's signed authorization of the release run over that exact record.
SERIES_COMPLETE = 'configs/campaigns/align_v4/series/series_complete.json'
RELEASE_RECEIPT = 'configs/campaigns/align_v4/series/release_receipt.json'
SERIES_COMPLETE_SCHEMA = 'joulewise.align_v4.series_complete.v1'
RELEASE_RECEIPT_SCHEMA = 'joulewise.align_v4.release_receipt.v1'
GUARD_SCHEMA = 'joulewise.align_v4.desk_release_guard.v1'
GPU = 'powermetrics:gpu_power'

# RESEARCH-LEAD SWITCH, ruled ON (RL-149 section 3(a)): "W1_WITHHOLD_SABOTAGE_GPU_AND_OUTCOMES = True".
# Every non-benign W1 member (ordinals 2, 3, 6, 9, 11, 13, 14, 16 of the frozen roster) gets the C/T member
# allowlist: GPU-rail energy, residual/transfer/tamper scores, task outcomes, tool structure, battery and
# non-GPU rails are withheld, except through W1_EXCEPTIONS. False keeps only the MED-4 minimum
# (battery_discharge and non-GPU rails of non-benign members) and is not the ruled setting.
W1_WITHHOLD_SABOTAGE_GPU_AND_OUTCOMES = True

# RL-149 section 3(a): "the registered W1 outputs that need a non-benign member's value ... are computed in
# memory and print as their registered output only." The builder's trace (protocol v4 line numbers). W1's
# non-benign members: anchors 2, 3; contrast template X (X-G 6, 16; X-S 9, 13), all sabotage-condition;
# D 11, 14. ``handling`` is what the sealed desk prints; ``in_class`` False marks a registered output that
# needs a non-benign value but is NOT in RL-149's named class (left withheld or narrowed; cold review).
W1_EXCEPTIONS = (
    {'output': 'deciding contrast (thermal.deciding_experiment)', 'protocol': ':518-534, ruling 9 :693-694, D-C1',
     'reads': 'turn_owned_j, tokens, start_ns, stage, admission slow temperature and G1 waits of X-template '
              'members 6, 9, 13, 16 (sabotage condition)',
     'in_class': True, 'handling': 'printed whole: verdict, branch, reason, delivery statistics, d_template_j, '
                                   'arm_effect_j, ci90_j, df, same-arm pair statistics, per-turn arm-mean differences'},
    {'output': 'U1 (thermal.model_windows[*].U1)', 'protocol': ':444-451, :461-465',
     'reads': "every gated member's turn OS/PM states, coverage, gate timeouts and X1-X4 exclusions",
     'in_class': True, 'handling': 'verdict printed; its counts over all members (turn admissions, G1/H and G0 '
                                   'timeouts, thermally excluded members) withheld, since with the benign rows printed '
                                   'whole they give the non-benign counts by subtraction (RL-151 section 4 C2)'},
    {'output': 'U2 (thermal.model_windows[*].U2)', 'protocol': ':452, :461-465',
     'reads': 'the G0 slow-temperature range over every gated member (an extreme-value statistic over a set '
              'holding non-benign members) and every G1/H release',
     'in_class': True, 'handling': 'printed as registered (status, g0_slow_range_c); RL-149 names U3-U6, U1/U2 '
                                   'read the same records and are placed in the class here for the cold review'},
    {'output': 'U3 (thermal.model_windows[*].U3 pairs)', 'protocol': ':453, :463-464, ruling 5 :660-684',
     'reads': 'identical-work replay pairs X-S 9/13 and X-G 6/16 (sabotage condition) beside 7/15, 10/12, 5/17',
     'in_class': True, 'handling': 'printed as registered (pair status, token identity, |dE| and its margin)'},
    {'output': 'U4-U6', 'protocol': ':444-447, :454-456, ruling 6 :686-688',
     'reads': 'nothing in W1 (U4-U6 are unevaluable there; U4 later reads W1 ordinals 5 and 17, both benign)',
     'in_class': True, 'handling': 'printed as registered (inconclusive in W1)'},
    {'output': 'B bar (registration_diagnostics.battery_windows)', 'protocol': 'W1-BLOCKERS lead ruling 9; :889',
     'reads': 'B, assist and unobserved codes of every member', 'in_class': False,
     'handling': 'window counts and bar verdict printed (a count over all members); per-member battery rows withheld'},
    {'output': 'R10 D-member X2 count and rate (d_member_x2)', 'protocol': 'LEAD-RULINGS-2 R10; :395, :409-416',
     'reads': 'G0/G1 timeouts of D members incl. 11 and 14', 'in_class': False,
     'handling': 'R10 count and rate printed over the four BENIGN W1 D members only, labelled so (RL-151 section 4 C2); '
                 'non-benign rows keep the G0 outcome only (RL-149 carve-out); the RL-149 section 1.5 tripwire (more '
                 'than 10 % of the D G1 admissions timing out) is judged in memory over all six D members and prints '
                 'its verdict only. In C/T only the G0 count prints'},
    {'output': 'R22-3 balance check by condition', 'protocol': 'RUN_STATE 234 R22-3',
     'reads': 'exposure seconds and event counts of the sabotage-condition members', 'in_class': False,
     'handling': 'withheld with a member count, as in C/T (member time by condition is an outcome, RL-149 3(c))'},
    {'output': 'warm reference: G0/G1 waits against ordinal', 'protocol': 'ruling 18 :724-729',
     'reads': 'gate waits of every ordinal', 'in_class': False,
     'handling': 'rows of non-benign ordinals withheld (heat-bearing per member); R-minus-R1 soak and '
                 'thermal.reference_warm (ordinal 5, benign) printed'},
    {'output': 'rebuild counts and the no-rebuild sensitivity list', 'protocol': 'ruling 18 :727-728',
     'reads': 'cache rebuilds of every member', 'in_class': False,
     'handling': 'non-benign rows and ids withheld'},
    {'output': 'tool_call_flags table (per member)', 'protocol': ':480-489',
     'reads': 'tool-call flags of every member', 'in_class': False,
     'handling': 'non-benign rows withheld; window turn totals printed'},
    {'output': 'refusal/incomplete members by arm', 'protocol': ':493',
     'reads': 'end state of every member', 'in_class': False,
     'handling': "non-benign members' end state withheld with their member line"},
    {'output': 'residual analysis: sabotage full-benign-fit scores, cross-pair transfer, known-H tamper curve',
     'protocol': ':536-559, B4', 'reads': 'GPU-rail energy and residual rows of D/anchor/X sabotage members',
     'in_class': False, 'handling': 'non-benign score rows and the tamper curve withheld (the preview RL-149 '
                                    'withholds); benign LOTO scores print'},
)

# RL-149 section 3 carve-out: truncation / heat-ended codes print only as a window count over all members.
CARVE_OUT_CODES = ('episode.deadman', 'thermal.gate_timeout', 'thermal.hold_timeout', 'episode.decode_budget',
                   'turn_token_budget_reached', 'turn_budget_reached', 'episode.turn_token_budget_reached',
                   'episode.max_turns', 'episode.time_guard', 'reasoning_censored_at_token_limit',
                   'calibration_censored_at_ceiling')

# Per member (PILOT.json ``members`` and the printed member lines): identity and the exclusion record, which
# is the harvest's own (``members_excluded``) and is all any consumer reads; ``light_triage.final_adjudication_error``
# and harvest-off ``final`` read only top-level fields and ``extra_checks.thermal``, and the full-desk gate reads
# the full members in memory. PR #774 row-1 F5: chain_eligible, chain_reasons (it can carry the heat-bearing
# ``thermal_pressure_elevated_in_window``), target_precheck_eligible, window_evidence_precheck, the harvest
# flag codes and readable are read by no consumer, so they are folded into the digest. Per-member instrument
# and identity codes stay visible in ``extra_checks.thermal`` members (``flags``), which the packet builder reads.
# Every other field is folded into one ``withheld`` digest, so not even a withheld key name is printed.
MEMBER_ALLOWLIST = ('run_id', 'ordinal', 'pool_role', 'excluded', 'exclusion_codes', 'disclosed_exclusion_codes')
# PILOT.json top level kept verbatim (light_triage.final_adjudication_error reads plan_id, status,
# members_excluded and members_disclosure_only; the packet builder reads checks and the desk status).
TOP_ALLOWLIST = ('schema_version', 'non_claim', 'session_id', 'plan_id', 'runs_root', 'checks',
                 'registered_eligible_members', 'exclusions_path', 'members_excluded',
                 'members_disclosure_only', 'harvest_flags_status', 'status')
# The v4 extra report (``powermode_desk_check``) kept verbatim.
EXTRA_ALLOWLIST = ('unlisted_flag_codes', 'w1_non_benign_tool_path', 'w1_g1_tripwire',
                   'instrument_ok', 'powermode_mismatches', 'series', 'pool_members', 'calibration_counts_final',
                   'calibration_counts_note', 'registration_error', 'series_desk_row')
# Thermal desk records: what light_triage (id, excluded, calibration_exclusions), the U-check/escalation
# readers and the next-arm packet builder read: X1-X8 fault tabulation (flags, coverage, pm_period_s,
# pm_max_gap_s, model, gated), the D cohort assertion (configuration = the frozen spec slots, cohort_identity
# = model/runtime identity) and the X5/U3 identity reconstruction (identical_work_group, compare_reference_id,
# and ``tokens``, which is replaced by its sha256: equal digests iff equal tokens, None stays None).
# Per-turn observations, energy, tool calls, waits and battery are withheld.
THERMAL_MEMBER_ALLOWLIST = ('id', 'ordinal', 'pool_role', 'role', 'model', 'window', 'stage', 'gated',
                            'excluded', 'calibration_exclusions', 'coverage', 'pm_period_s', 'pm_max_gap_s',
                            'supplemental', 'identical_work_group', 'compare_reference_id', 'replay_of',
                            'configuration', 'cohort_identity')
U3_PAIR_KEEP = ('status', 'exclusion', 'token_identical')
MODEL_WINDOW_KEEP = ('hardware_control', 'monitoring_calibration', 'consequence')
BATTERY_WINDOW_KEEP = ('B_count', 'unobserved_count', 'assist_count', 'assist_outside_request_count',
                       'bar_pass', 'status', 'consequence')
KM003C_KEEP = ('schema', 'label', 'print_only', 'measurement', 'residual', 'fit', 'uncertainty', 'detail')
# RL-149: the G0 outcome stays per member (a G0 timeout ends a member before its first turn and decides
# eligibility); the G1-timeout column (and ``x2``, which ORs it in) is not printed per member. PR #774 row-1 F1:
# in C/T only the G0 count is kept; ``x2_count``/``x2_rate`` minus it would give the G1 count, which belongs to
# the carve-out (window counts over all members). Real C/T rosters hold 18 role-D members (14 pool benign, 2
# sentinels, 2 sabotage); W1 holds 6 (ordinals 5, 8, 11, 14, 17, 18; 11 and 14 non-benign).
X2_ROW_KEEP = ('run_id', 'ordinal', 'g0_outcome', 'g0_timeout_x2')
X2_KEEP = ('print_only', 'authority', 'd_members', 'read', 'unread', 'g0_timeout_x2_count')


def canonical_sha256(value):
    """sha256 of the canonical JSON (sorted keys, no whitespace) of ``value``."""
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


# Withheld digests are keyed. A plain sha256 of a low-entropy value (a turn list, a small count, a boolean)
# is inverted by enumeration, so each desk run draws a random 32-byte key, records it in its withheld archive
# (``archive/withheld/desk_seal_key.json``, beside PILOT.full.json; it opens with it) and digests every
# withheld value as HMAC-SHA256 over its canonical JSON. Outside a :func:`keyed` block (the light triage, a
# direct call) the key is a process-ephemeral one that is never written: the digest cannot be checked later,
# and it cannot be inverted.
DIGEST = 'HMAC-SHA256 over canonical JSON (sort_keys, separators (",", ":"))'
WITHHELD_KEY = 'archive/withheld/desk_seal_key.json'
_KEY = {'current': None, 'ephemeral': secrets.token_bytes(32)}


@contextlib.contextmanager
def keyed(key):
    previous, _KEY['current'] = _KEY['current'], key
    try:
        yield key
    finally:
        _KEY['current'] = previous


def keyed_digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=True, default=str).encode()
    return hmac.new(_KEY['current'] or _KEY['ephemeral'], raw, hashlib.sha256).hexdigest()


def withheld(value):
    return {'status': WITHHELD, 'hmac_sha256': keyed_digest(value)}


def _code(flag):
    """A flag's code: the string up to its first ':' (values after it are withheld)."""
    if isinstance(flag, dict):
        flag = flag.get('code')
    return str(flag).split(':')[0] if flag is not None else None


# PR #774 Sol seat F3: per-member flags print from an explicit ALLOWLIST of instrument and identity codes, each
# with the consumer that reads it after sealing; every other code (completion, unfinished reasoning, cache
# rebuilds, context termination, battery assist, tool behaviour, carved codes, anything unknown) is withheld in
# the member's digest. Eligibility-required exclusions keep their ruled path (``calibration_exclusions``,
# ``exclusion_codes``, ``members_excluded``), not this one.
FLAG_ALLOWLIST = {
    'thermal.start_gate_timeout': 'RL-149 section 3: a G0 timeout ends a member before its first turn and decides '
                                  'eligibility; thermal_desk.thermal_exclusions (X2/G0)',
    'thermal.state_unobserved': 'X4 state-unobserved instrument fault; thermal_desk.state_unobserved, the packet '
                                "builder's X1-X8 fault tabulation (align_v4_next_arm_packet faults)",
    'thermal.custody_invalid': 'instrument custody fault; thermal_desk.calibration_exclusions, the packet '
                               "builder's fault tabulation",
    'member.runtime_failure': 'runtime failure (X6-class instrument fault); calibration_exclusions, fault tabulation',
    'member.artifact_missing': 'missing episode artifact; align_v4_thermal_desk roster row, fault tabulation',
}
IDENTITY_MARKER = 'identity_mismatch'   # X5 identity codes: align_v4_next_arm_packet eligibility ('identity X5')
# Sealed DC rows keep the meter's health codes only (RL-151 section 4 table: "The meter's health fields stay
# visible"; align_v4_next_arm_packet meter_coverage tabulates them); fit flags are withheld.
METER_PREFIX = 'meter.'


def allowed_code(code):
    return code in FLAG_ALLOWLIST or (isinstance(code, str) and IDENTITY_MARKER in code)


def _codes(flags):
    """Per-member flag codes from the allowlist only; unknown and behavioural codes are withheld."""
    return sorted({c for c in (_code(f) for f in flags or ()) if c and allowed_code(c)})


def _session_codes(flags):
    """Session-scoped harvest flags (no member): codes without suffix text, carved codes counted elsewhere."""
    return sorted({c for c in (_code(f) for f in flags or ()) if c and c not in CARVE_OUT_CODES})


def _meter_codes(flags):
    return list(dict.fromkeys(c for c in (_code(f) for f in flags or ()) if c and c.startswith(METER_PREFIX)))


def coverage_verdicts(coverage):
    """PR #774 Sol F2: per coverage span, the verdict and a reason code only. Sample counts, fractions, gaps
    and intervals encode elapsed time on the sampler grid, so they go into the member's withheld digest.
    The rule is ``thermal_desk.acceptance``'s U1 coverage check (>= 99 % of samples, no interval > 2 s)."""
    if not isinstance(coverage, list):
        return coverage
    out = []
    for span in coverage:
        span = span if isinstance(span, dict) else {}
        fraction, interval = span.get('sample_fraction'), span.get('max_interval_ns')
        reasons = ([] if fraction is not None and fraction >= .99 else ['coverage.samples_below_99pct']) + \
                  ([] if interval is not None and interval <= 2 * 10**9 else ['coverage.interval_over_2s'])
        out.append({'verdict': 'fail' if reasons else 'pass', 'reasons': reasons})
    return out


def _strip(codes):
    """RL-151 section 4 C1(a): a per-member code list printed as codes only, never the text after the first ':'.

    Exact-string consumers keep their verbatim fields elsewhere: ``members_excluded`` and
    ``members_disclosure_only`` (top level) are compared string-for-string with the harvest's exclusions by
    ``light_triage.final_adjudication_error`` through ``v4_contention.records_agree_with_harvest``. Every other
    per-member reader uses a prefix or truthiness (``light_triage.apply_harvest_codes``,
    ``v4_contention.split_codes``, the packet builder's ``eligibility``/``faults``), so codes suffice there.
    """
    if not isinstance(codes, (list, tuple)):
        return codes
    return list(dict.fromkeys(c for c in (_code(x) for x in codes) if c))


def carve_out_counts(flag_sets):
    """Window count over all members: carved code -> number of members carrying it (RL-149 section 3)."""
    counts = {}
    flag_sets = list(flag_sets)
    for flags in flag_sets:
        for code in {_code(f) for f in flags or ()} & set(CARVE_OUT_CODES):
            counts[code] = counts.get(code, 0) + 1
    return {'members': len(flag_sets), 'counts': dict(sorted(counts.items())), 'rule': 'RL-149 section 3 carve-out'}


def _benign_counts(flag_sets):
    """W1 (RL-151 section 4 C3): carved counts over the BENIGN members only, labelled so; a count over all
    members would give the non-benign members' count by subtracting the printed benign rows."""
    return {**carve_out_counts(flag_sets), 'over': 'benign members only (RL-151 section 4 C3)'}


def w1_g1_tripwire(records):
    """RL-149 section 1.5: more than 10 % of W1's D G1 admissions timing out goes to the research lead.

    Evaluated in memory over all D members; only the verdict prints (RL-151 section 4 C2)."""
    gates = [i for r in records or () if r.get('role') == 'D'
             for i in r.get('intervals') or () if isinstance(i, dict) and i.get('kind') == 'G1']
    timeouts = sum(i.get('outcome') == 'timeout' for i in gates)
    verdict = 'to the research lead' if gates and timeouts / len(gates) > .10 else 'within'
    return {'verdict': verdict, 'rule': 'RL-149 section 1.5: > 10 % of W1 D G1 admissions timing out',
            'withheld': withheld({'admissions': len(gates), 'timeouts': timeouts})}


def _member_flags(member):
    summary = member.get('summary') or {}
    return [*(summary.get('flags') or ()), *(_code(f) for f in member.get('harvest_flags') or ())]


# --- the release event ---------------------------------------------------------------------------

def _load(path):
    try:
        raw = Path(path).read_bytes()
        return raw, json.loads(raw)
    except (OSError, ValueError):
        return None, None


def release_error(root):
    """``None`` when ``root`` holds a registered release event, else why not (fail closed).

    OPEN ITEM for the research lead's cold pass (PR #774 row-1 F6): the lead signature is format-only
    (``align_v4_kit.valid_lead_signature``, as for the registration receipt), so anyone who can write the
    measurement root could forge a release; the receipt binds the record's bytes, not an identity.

    ``series_complete.json`` (schema :data:`SERIES_COMPLETE_SCHEMA`)::

        {"schema": ..., "event": "series_complete", "last_admitted_test_window": "T<k>",
         "test_windows_final_eligibility": {"T1": "final", ..., "T<k>": "final"},
         "series_manifest_sha256": <sha256 of the frozen series manifest bytes>,
         "record_commit": <40-hex commit that recorded the series' last final eligibility>}

    ``release_receipt.json`` (schema :data:`RELEASE_RECEIPT_SCHEMA`)::

        {"schema": ..., "release_run": true, "series_complete_sha256": <sha256 of series_complete.json>,
         "ruling": "RL-<n>: <the research lead's release ruling>", "lead_signature": "lead: <name/session> <YYYY-MM-DD>"}
    """
    if root is None:
        return 'no measurement root'
    root = Path(root)
    raw, record = _load(root / SERIES_COMPLETE)
    if not isinstance(record, dict):
        return 'no series_complete record'
    if record.get('schema') != SERIES_COMPLETE_SCHEMA or record.get('event') != 'series_complete':
        return 'series_complete record malformed'
    last = record.get('last_admitted_test_window')
    final = record.get('test_windows_final_eligibility')
    if (not isinstance(last, str) or not re.fullmatch(r'T[1-9][0-9]*', last) or not isinstance(final, dict)
            or last not in final or not final or any(v != 'final' for v in final.values())):
        return "series_complete does not record the last admitted test window's final eligibility"
    if not isinstance(record.get('record_commit'), str) or not re.fullmatch(r'[0-9a-f]{40}', record['record_commit']):
        return 'series_complete names no committed record'
    try:
        manifest = (root / SERIES_MANIFEST).read_bytes()
    except OSError:
        return 'series manifest unreadable'
    if record.get('series_manifest_sha256') != hashlib.sha256(manifest).hexdigest():
        return 'series_complete is bound to another series manifest'
    _raw, receipt = _load(root / RELEASE_RECEIPT)
    if not isinstance(receipt, dict) or receipt.get('schema') != RELEASE_RECEIPT_SCHEMA:
        return 'no release receipt'
    if receipt.get('release_run') is not True or receipt.get('series_complete_sha256') != hashlib.sha256(raw).hexdigest():
        return 'release receipt does not authorize this series_complete record'
    ruling = receipt.get('ruling')
    if not isinstance(ruling, str) or not re.match(r'RL-[1-9][0-9]*\b', ruling.strip()):
        # RL-151 section 4.3: the receipt names the research lead's release ruling, so the authorization sits in
        # the decision log where its absence can be seen.
        return 'release receipt names no research-lead release ruling'
    from scripts.align_v4_kit import valid_lead_signature
    if not valid_lead_signature(receipt.get('lead_signature')):
        return 'release receipt is not lead-signed'
    return None


def release_record(state):
    """What a released desk records (RL-151 section 4 C4): both release files' sha256 and the ruling."""
    state = state or {}
    root = Path(state.get('source_measurement_root') or state.get('measurement_root'))
    complete, receipt = (root / SERIES_COMPLETE).read_bytes(), (root / RELEASE_RECEIPT).read_bytes()
    return {'schema': GUARD_SCHEMA, 'status': 'released', 'window_id': window_id(state),
            'series_complete': SERIES_COMPLETE, 'series_complete_sha256': hashlib.sha256(complete).hexdigest(),
            'release_receipt': RELEASE_RECEIPT, 'release_receipt_sha256': hashlib.sha256(receipt).hexdigest(),
            'ruling': json.loads(receipt).get('ruling'), 'authority': 'RL-151 section 4 C4'}


def released(state):
    """True only on a registered release event (see :func:`release_error`). Today: always False."""
    state = state or {}
    root = state.get('source_measurement_root') or state.get('measurement_root')
    return release_error(root) is None


# --- scope ---------------------------------------------------------------------------------------

def window_id(state):
    return ((state or {}).get('v4_series') or {}).get('window_id', 'W1')


def window_scope(state):
    """``'W1'`` (selection), ``'C'`` (calibration) or ``'T'`` (test). Anything else seals as C/T."""
    series = (state or {}).get('v4_series') or {}
    wid, role = series.get('window_id', 'W1'), series.get('role')
    if wid == 'W1' and role in (None, 'selection'):
        return 'W1'
    if role == 'test' or (role is None and str(wid).startswith('T')):
        return 'T'
    return 'C'      # calibration, a D alias, or an unknown role: fail closed to the C/T seal


def _nonbenign(plan_members, pilot_members=()):
    conditions = {m.get('run_id'): m.get('condition') for m in plan_members or ()}
    for m in pilot_members or ():
        conditions.setdefault(m.get('run_id'), m.get('condition'))
    return {rid for rid, c in conditions.items() if c != 'benign'}


# --- members -------------------------------------------------------------------------------------

def seal_member(member, plan_row=None):
    """One PILOT member reduced to :data:`MEMBER_ALLOWLIST` plus one ``withheld`` digest of the rest."""
    plan_row = plan_row or {}
    view = {'run_id': member.get('run_id'), 'ordinal': member.get('ordinal', plan_row.get('ordinal')),
            'pool_role': plan_row.get('pool_role', member.get('pool_role')),
            'excluded': member.get('excluded'), 'exclusion_codes': _strip(member.get('exclusion_codes')),
            'disclosed_exclusion_codes': _strip(member.get('disclosed_exclusion_codes', []))}
    view = {k: view[k] for k in MEMBER_ALLOWLIST if k in view}
    rest = {k: v for k, v in member.items() if k not in view or view[k] != v}
    view['withheld'] = withheld(rest)
    return view


def seal_line(run_id, record):
    """A printed member line (``harvest_flags`` / ``detail`` / ``unreadable``) reduced to the allowlist."""
    out = {'harvest_flags': {'withheld': withheld(record.get('harvest_flags'))}}
    detail = record.get('detail') or {}
    keep = {k: (_strip(detail[k]) if k.endswith('_codes') else detail[k]) for k in MEMBER_ALLOWLIST if k in detail}
    keep['withheld'] = withheld({k: v for k, v in detail.items() if k not in keep})
    out['detail'] = keep
    if 'unreadable' in record:
        out['unreadable'] = str(record['unreadable']).split(':')[0] + ' (message ' + WITHHELD + ')'
    return out


# --- window analyses: hash plus window-pooled instrument figures (no member or cell key) -----------

def _finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def pooled_residuals(analysis):
    scopes = {}
    for configuration in analysis or ():
        for scope, block in (configuration.get('scopes') or {}).items():
            for label, convention in block.items():
                if not isinstance(convention, dict) or 'residuals' not in convention:
                    continue
                row = scopes.setdefault(scope, {}).setdefault(label, {
                    'members_scored': 0, 'members_with_finite_score': 0, 'fit_flags': set(), 's_r_df': 0})
                residuals = convention.get('residuals') or []
                row['members_scored'] += len(residuals)
                row['members_with_finite_score'] += sum(_finite(r.get('score')) for r in residuals)
                row['fit_flags'] |= set(convention.get('flags') or ())
                row['s_r_df'] += convention.get('s_r_df') or 0
    for block in scopes.values():
        for row in block.values():
            row['fit_flags'] = sorted(row['fit_flags'])
    return {'configurations': len(analysis or ()), 'scopes': scopes}


def pooled_i4(i4):
    def tally(rows):
        out = {}
        for r in rows if isinstance(rows, list) else ():
            status = r.get('status') if isinstance(r, dict) else None
            out[str(status)] = out.get(str(status), 0) + 1
        return out
    cells = list((i4 or {}).values())
    replays = [r for c in cells if isinstance(c.get('replay_identity'), list) for r in c['replay_identity']]
    merge = lambda field: {k: sum(tally(c.get(field)).get(k, 0) for c in cells)
                           for k in sorted({k for c in cells for k in tally(c.get(field))})}
    return {'cells': len(cells), 'replay_pairs': len(replays),
            'replay_identical': sum(r.get('status') == 'identical' for r in replays),
            'accounting': merge('accounting'), 'sampler_provenance': merge('sampler_provenance'),
            'independent_seed_observations': sum(len((c.get('independent_seed_distinct') or {}).get('observations') or ())
                                                 for c in cells)}


def pooled_spreads(spreads):
    pairs = {(r.get('original'), r.get('replay')) for rows in (spreads or {}).values() for r in rows or ()}
    return {'replay_pairs': len(pairs),
            'channels': sorted({r.get('channel') for rows in (spreads or {}).values() for r in rows or ()})}


def pooled_raw(raw):
    return {'cells': len(raw or {}), 'channels': sorted({ch for cell in (raw or {}).values() for ch in cell})}


def pooled_identity(identity):
    values = list((identity or {}).values())
    return {'cells': len(values), 'identical': sum(v is True for v in values),
            'not_identical': sum(v is False for v in values), 'not_evaluated': sum(v == 'not_evaluated' for v in values)}


def _sealed_block(value, pooled):
    return {**withheld(value), 'pooled': pooled}


# --- the v4 extra report ---------------------------------------------------------------------------

def _seal_dc_rows(dc, run_ids):
    """km003c rows of ``run_ids`` sealed (status and flags kept); MED-4-sealed rows stay as they are."""
    members = {}
    for rid, row in (dc.get('members') or {}).items():
        if rid in run_ids and isinstance(row, dict) and not row.get('sealed'):
            row = {'label': row.get('label'), 'print_only': True, 'sealed': True, 'sealed_hmac_sha256': keyed_digest(row),
                   'status': row.get('status'), 'flags': _meter_codes(row.get('flags')),
                   'sealed_until': 'series_complete'}
        elif rid in run_ids and isinstance(row, dict):          # MED-4-sealed: meter codes only (RL-151 C1(a), Sol F3)
            row = {**row, 'flags': _meter_codes(row.get('flags'))}
        members[rid] = row
    return {**dc, 'members': members}


def seal_dc(dc, plan_members):
    """C/T: every member's DC row is sealed (energy on every rail, protocol B0); top-level fits withheld."""
    if not isinstance(dc, dict):
        return dc
    sealed = _seal_dc_rows(dc, set(dc.get('members') or {}))
    out = {k: sealed[k] for k in KM003C_KEEP if k in sealed}
    out['members'] = sealed['members']
    rest = {k: v for k, v in dc.items() if k not in out}
    if set(rest) == {'withheld'}:           # already sealed (the desk prints seal first): idempotent
        out['withheld'] = rest['withheld']
    elif rest:
        out['withheld'] = withheld(rest)
    return out


def seal_balance(report):
    """C/T: R22-3's exposure is member time (B7 time baseline); the report is withheld, members counted."""
    if not isinstance(report, dict):
        return report
    return {'status': report.get('status'), 'authority': report.get('authority'),
            **_sealed_block(report, {'members': (report.get('total') or {}).get('members'),
                                     'members_without_exposure_or_condition': len(report.get('members_without_exposure_or_condition') or ())})}


def balance_lines(report):
    return [f"balance (R22-3): {WITHHELD} hmac_sha256={report.get('hmac_sha256')} "
            f"members={(report.get('pooled') or {}).get('members')} (print only)"]


def _seal_thermal_member(record):
    view = {k: record[k] for k in THERMAL_MEMBER_ALLOWLIST if k in record}
    view['flags'] = _codes(record.get('flags'))                # Sol F3: allowlisted codes only
    if 'calibration_exclusions' in view:                     # RL-151 C1(a): codes only, no suffix text
        view['calibration_exclusions'] = _strip(view['calibration_exclusions'])
    if 'coverage' in view:                                   # Sol F2: verdicts only
        view['coverage'] = coverage_verdicts(view['coverage'])
    if 'tokens' in record:
        # Sol F6: a keyed commitment (equal digests iff equal tokens within one desk's key), so a candidate
        # dictionary cannot identify the tokens without the withheld key.
        view['tokens'] = None if record['tokens'] is None else 'hmac:' + keyed_digest(record['tokens'])
    view['withheld'] = withheld({k: v for k, v in record.items()
                                 if k not in view or k in ('flags', 'tokens', 'calibration_exclusions', 'coverage')})
    return view


def _seal_model_window(result):
    view = {f'U{k}': {'status': (result.get(f'U{k}') or {}).get('status')} for k in range(1, 7) if f'U{k}' in result}
    pairs = (result.get('U3') or {}).get('pairs')
    if isinstance(pairs, list) and 'U3' in view:
        view['U3']['pairs'] = [{k: p[k] for k in U3_PAIR_KEEP if k in p} for p in pairs if isinstance(p, dict)]
    view.update({k: result[k] for k in MODEL_WINDOW_KEEP if k in result})
    view['withheld'] = withheld(result)
    return view


def seal_thermal(thermal, run_ids=None):
    """Thermal desk section: U statuses and the allowlisted member fields; ``run_ids`` None = every member."""
    if not isinstance(thermal, dict):
        return thermal
    out = {'schema': thermal.get('schema')}
    if run_ids is None:
        out['model_windows'] = {k: _seal_model_window(v) for k, v in (thermal.get('model_windows') or {}).items()}
    else:
        # W1: the U results print as registered, except U1's counts over all members (turn admissions,
        # G1/H and G0 timeouts, thermally excluded members): with the benign rows printed whole they give the
        # non-benign members' counts by subtraction (RL-151 section 4 C2). U1 prints its verdict.
        out['model_windows'] = {k: ({**v, 'U1': {'status': (v.get('U1') or {}).get('status'),
                                                 'withheld': withheld(v.get('U1'))}} if isinstance(v, dict) and 'U1' in v else v)
                                for k, v in (thermal.get('model_windows') or {}).items()}
    out['members'] = [_seal_thermal_member(r) if (run_ids is None or r.get('id') in run_ids) else r
                      for r in thermal.get('members') or ()]
    out['carve_out_flag_counts'] = (carve_out_counts(r.get('flags') for r in thermal.get('members') or ())
                                    if run_ids is None else _benign_counts(
                                        r.get('flags') for r in thermal.get('members') or () if r.get('id') not in run_ids))
    rest = {k: v for k, v in thermal.items() if k not in ('schema', 'model_windows', 'members')}
    tools = rest.get('tool_call_flags')
    if run_ids is None:
        if isinstance(tools, dict):
            out['tool_call_flags'] = {'turn_totals': tools.get('turn_totals'), 'withheld': withheld(tools)}
        out['withheld'] = withheld(rest)
    else:
        # W1: the deciding contrast is in RL-149's exception class and prints as registered (W1_EXCEPTIONS).
        for key, value in rest.items():
            if key == 'tool_call_flags' and isinstance(value, dict):
                value = seal_w1_tool_table(value, run_ids)
            out[key] = value
    return out


def seal_w1_tool_table(table, run_ids):
    """PR #774 Sol F4 (lead disposition): W1's tool-call table prints the benign rows and turn totals over the
    benign rows only, labelled ``population: benign``. The non-benign rows and their aggregate are one withheld
    digest; no per-row placeholder is left, since a row exists only for a member that carried a flag."""
    rows = list(table.get('members') or ())
    benign = [r for r in rows if r.get('id') not in run_ids]
    keys = sorted({k for r in rows for k in r if k not in ('id', 'model')} | set(table.get('turn_totals') or {}))
    out = {k: v for k, v in table.items() if k not in ('members', 'turn_totals')}
    out.update(members=benign, population='benign',
               turn_totals={k: sum(len(r.get(k) or ()) for r in benign) for k in keys},
               withheld_non_benign=withheld([r for r in rows if r.get('id') in run_ids]))
    return out


def seal_registration_diagnostics(diag):
    if not isinstance(diag, dict):
        return diag
    out = {}
    windows = diag.get('battery_windows')
    if isinstance(windows, dict):
        out['battery_windows'] = {k: {**{f: row[f] for f in BATTERY_WINDOW_KEEP if f in row}, 'withheld': withheld(row)}
                                  for k, row in windows.items()}
    cohort = diag.get('d_cohort')
    if isinstance(cohort, dict):
        out['d_cohort'] = {'instrument_ok': cohort.get('instrument_ok'), 'withheld': withheld(cohort)}
    sentinel = diag.get('sentinel')
    if isinstance(sentinel, dict):
        out['sentinel'] = {'ordinal': sentinel.get('ordinal'),
                           'candidates': {str(k): {'admissible': (v or {}).get('admissible'),
                                                   'requirements': (v or {}).get('requirements')}
                                          for k, v in (sentinel.get('candidates') or {}).items()},
                           'withheld': withheld(sentinel)}
    rest = {k: v for k, v in diag.items() if k not in out}
    if rest:
        out['withheld'] = withheld(rest)
    return out


def _seal_x2(report, run_ids=None):
    """R10 X2 report: counts and rate kept; per row the G0 outcome only (``run_ids`` None = every row)."""
    if not isinstance(report, dict):
        return report
    rows = report.get('members') or ()
    # C/T: X2_KEEP only. W1 (``run_ids`` = its non-benign members): the R10 count and rate are over the BENIGN
    # D members only and labelled so (RL-151 section 4 C2: over all six D members they give the non-benign G1
    # timeouts by subtraction); the RL-149 section 1.5 tripwire is evaluated in memory over all six.
    if run_ids is None:
        out = {k: report[k] for k in X2_KEEP if k in report}
    else:
        benign = [r for r in rows if r.get('run_id') not in run_ids]
        x2_benign = sum(bool(r.get('x2')) for r in benign)
        out = {k: report[k] for k in X2_KEEP if k in report}
        out.update(x2_count=x2_benign, x2_rate=(x2_benign / len(benign)) if benign else None,
                   g0_timeout_x2_count=sum(bool(r.get('g0_timeout_x2')) for r in benign),
                   pool='benign D members only (RL-151 section 4 C2)')
    out['members'] = [{k: r[k] for k in X2_ROW_KEEP if k in r} if run_ids is None or r.get('run_id') in run_ids else r
                      for r in rows]
    out['withheld'] = withheld(report)
    return out


def seal_extra(extra, plan_members, scope, *, w1_withhold=None):
    """The v4 extra report (``powermode_desk_check``) for ``scope``; also the light triage's record source."""
    if not isinstance(extra, dict):
        return extra
    if scope == 'W1':
        return _seal_extra_w1(extra, plan_members, W1_WITHHOLD_SABOTAGE_GPU_AND_OUTCOMES if w1_withhold is None else w1_withhold)
    out = {k: extra[k] for k in EXTRA_ALLOWLIST if k in extra}
    for key, value in extra.items():
        if key in out:
            continue
        if key == 'km003c':
            out[key] = seal_dc(value, plan_members)
        elif key == 'thermal':
            out[key] = seal_thermal(value)
        elif key == 'registration_diagnostics':
            out[key] = seal_registration_diagnostics(value)
        elif key == 'balance_check':
            out[key] = value if isinstance(value, dict) and value.get('status') == WITHHELD else seal_balance(value)
        elif key == 'd_member_x2':
            out[key] = _seal_x2(value)
        else:
            out[key] = withheld(value)
    return out


def _seal_extra_w1(extra, plan_members, withhold):
    nonbenign = _nonbenign(plan_members)
    ordinals = {m.get('ordinal') for m in plan_members or () if m.get('run_id') in nonbenign}
    out = dict(extra)
    if withhold:
        if isinstance(extra.get('balance_check'), dict) and extra['balance_check'].get('status') != WITHHELD:
            out['balance_check'] = seal_balance(extra['balance_check'])
        if isinstance(extra.get('d_member_x2'), dict):
            out['d_member_x2'] = _seal_x2(extra['d_member_x2'], nonbenign)
    if isinstance(extra.get('km003c'), dict):
        # MED-4 already seals non-benign DC rows; re-apply so the guard never depends on the caller.
        out['km003c'] = _seal_dc_rows(extra['km003c'], nonbenign)
    thermal = extra.get('thermal')
    if isinstance(thermal, dict):
        if withhold:
            out['thermal'] = seal_thermal(thermal, nonbenign)
        else:
            out['thermal'] = {**thermal, 'members': [
                {**r, 'battery': withheld(r['battery'])} if r.get('id') in nonbenign and 'battery' in r else r
                for r in thermal.get('members') or ()]}
    diag = extra.get('registration_diagnostics')
    if isinstance(diag, dict):
        diag = dict(diag)
        if isinstance(diag.get('battery_windows'), dict):
            def battery_row(row):
                if withhold:
                    row = benign_assist_counts(row, nonbenign)
                row = {**row, 'members': [withheld(m) if m.get('id') in nonbenign else m for m in row.get('members') or ()]}
                sensitivity = row.get('no_assist_sensitivity')
                if withhold and isinstance(sensitivity, dict):
                    # Sol F5: the no-assist list would name which non-benign members were (not) assisted.
                    row['no_assist_sensitivity'] = {**sensitivity, 'population': 'benign', 'member_ids': [
                        i for i in sensitivity.get('member_ids') or () if i not in nonbenign], 'withheld': withheld(sensitivity)}
                return row
            diag['battery_windows'] = {k: battery_row(row) if isinstance(row, dict) else row
                                       for k, row in diag['battery_windows'].items()}
        if withhold and isinstance(diag.get('rebuilds'), list):
            diag['rebuilds'] = [withheld(r) if r.get('id') in nonbenign else r for r in diag['rebuilds']]
        sensitivity = diag.get('no_rebuild_sensitivity')
        if withhold and isinstance(sensitivity, dict):
            diag['no_rebuild_sensitivity'] = {**sensitivity, 'member_ids': [
                i for i in sensitivity.get('member_ids') or () if i not in nonbenign], 'withheld': withheld(sensitivity)}
        warm = diag.get('warm_reference')
        if withhold and isinstance(warm, dict) and isinstance(warm.get('wait_against_ordinal'), list):
            diag['warm_reference'] = {**warm, 'wait_against_ordinal': [
                withheld(r) if r.get('ordinal') in ordinals else r for r in warm['wait_against_ordinal']]}
        out['registration_diagnostics'] = diag
    return out


# --- PILOT ---------------------------------------------------------------------------------------

def seal_pilot(pilot, plan_members, window_id_, *, scope=None, w1_withhold=None):
    """The PILOT a C/T (or W1) desk may record and print before release (allowlist; fail closed)."""
    scope = scope or ('W1' if window_id_ == 'W1' else 'T' if str(window_id_).startswith('T') else 'C')
    if scope == 'W1':
        return _seal_pilot_w1(pilot, plan_members, W1_WITHHOLD_SABOTAGE_GPU_AND_OUTCOMES if w1_withhold is None else w1_withhold)
    rows = {m.get('run_id'): m for m in plan_members or ()}
    out = {k: pilot[k] for k in TOP_ALLOWLIST if k in pilot}
    pooled = {'residual_analysis': pooled_residuals, 'raw_within_cell_energy_sd': pooled_raw,
              'repeat_energy_spread': pooled_spreads, 'I4_prime': pooled_i4, 'repeat_token_identity': pooled_identity}
    for key, value in pilot.items():
        if key in out:
            continue
        if key == 'members':
            out[key] = [seal_member(m, rows.get(m.get('run_id'))) for m in value]
        elif key in pooled:
            out[key] = _sealed_block(value, pooled[key](value))
        elif key == 'session_harvest_flags':
            out[key] = {'flag_codes': _session_codes(value), 'withheld': withheld(value)}
        elif key == 'extra_checks':
            out[key] = seal_extra(value, plan_members, scope)
        elif key == 'cross_pilot_token_identity' and value is None:
            out[key] = None
        elif key in ('episode_scope_alternative_eligible_members', 'episode_scope_alternative_ineligible_reasons'):
            out[key] = _sealed_block(value, {'members': len(value or ())})
        else:
            out[key] = withheld(value)
    out['carve_out_flag_counts'] = carve_out_counts(_member_flags(m) for m in pilot.get('members') or ())
    return out


def _cells_of(members, run_ids):
    from joulewise.align.apple.pilot_analysis import cell_key
    return {cell_key(m) for m in members if m.get('run_id') in run_ids}


def _in_cells(key, cells):
    return any(key == c or key.startswith(c + '/configuration=') for c in cells)


def _seal_pilot_w1(pilot, plan_members, withhold):
    members = pilot.get('members') or []
    nonbenign = _nonbenign(plan_members, members)
    rows = {m.get('run_id'): m for m in plan_members or ()}
    cells = _cells_of(members, nonbenign)
    out = dict(pilot)

    def minimum(member):
        member = dict(member)
        if 'battery_discharge' in member:
            member['battery_discharge'] = withheld(member['battery_discharge'])
        summary = member.get('summary')
        if isinstance(summary, dict) and isinstance(summary.get('energy'), dict):
            other = {ch: v for ch, v in summary['energy'].items() if ch != GPU}
            energy = {ch: v for ch, v in summary['energy'].items() if ch == GPU}
            if other:
                energy['non_gpu_rails'] = withheld(other)
            member['summary'] = {**summary, 'energy': energy}
        return member
    out['members'] = [(seal_member(m, rows.get(m.get('run_id'))) if withhold else minimum(m))
                      if m.get('run_id') in nonbenign else m for m in members]
    raw = pilot.get('raw_within_cell_energy_sd')
    if isinstance(raw, dict):
        out['raw_within_cell_energy_sd'] = {
            key: ((withheld(cell) if withhold else {ch: (v if ch == GPU else withheld(v)) for ch, v in cell.items()})
                  if _in_cells(key, cells) else cell) for key, cell in raw.items()}
    spreads = pilot.get('repeat_energy_spread')
    if isinstance(spreads, dict):
        out['repeat_energy_spread'] = {
            key: ([r if (not withhold and r.get('channel') == GPU) else withheld(r) for r in entries]
                  if _in_cells(key, cells) else entries) for key, entries in spreads.items()}
    if withhold and isinstance(pilot.get('residual_analysis'), list):
        out['residual_analysis'] = [_seal_residual_rows(c, nonbenign) for c in pilot['residual_analysis']]
    if withhold and isinstance(pilot.get('I4_prime'), dict):
        # Per-turn accounting and sampler rows give a member's turn count (episode length): status only.
        def row(r):
            return ({'run_id': r.get('run_id'), 'status': r.get('status'), 'withheld': withheld(r)}
                    if isinstance(r, dict) and r.get('run_id') in nonbenign else r)
        out['I4_prime'] = {cell: (withheld(value) if _in_cells(cell, cells) else
                                  {**value, **{f: [row(r) for r in value.get(f) or ()]
                                               for f in ('accounting', 'sampler_provenance') if isinstance(value.get(f), list)}})
                           if isinstance(value, dict) else value for cell, value in pilot['I4_prime'].items()}
    identity = pilot.get('repeat_token_identity')
    if withhold and isinstance(identity, dict):
        # RL-152 section 3.2: a cell holding a non-benign member is one pooled figure over it: withheld.
        out['repeat_token_identity'] = {cell: (withheld(v) if _in_cells(cell, cells) else v) for cell, v in identity.items()}
    reasons = pilot.get('episode_scope_alternative_ineligible_reasons')
    if withhold and isinstance(reasons, dict):
        out['episode_scope_alternative_ineligible_reasons'] = {
            rid: (_codes(codes) if rid in nonbenign else codes) for rid, codes in reasons.items()}
    if withhold:
        out['carve_out_flag_counts'] = _benign_counts(_member_flags(m) for m in members if m.get('run_id') not in nonbenign)
    if 'extra_checks' in pilot:
        out['extra_checks'] = _seal_extra_w1(pilot['extra_checks'], plan_members, withhold)
    return out


def _seal_residual_rows(configuration, run_ids):
    scopes = {}
    for scope, block in (configuration.get('scopes') or {}).items():
        block = dict(block)
        for label, convention in list(block.items()):
            if not isinstance(convention, dict) or 'residuals' not in convention:
                continue
            convention = dict(convention)
            convention['residuals'] = [withheld(r) if r.get('run_id') in run_ids else r for r in convention['residuals']]
            convention['cross_pair_transfer'] = [
                {**t, 'scores': [withheld(s) if s.get('run_id') in run_ids else s for s in t.get('scores') or ()]}
                for t in convention.get('cross_pair_transfer') or ()]
            convention['tamper_detection_curve'] = withheld(convention.get('tamper_detection_curve'))
            # RL-152 section 3.2: s_r and the per-cell residual counts pool cells that hold non-benign members,
            # beside printed benign residuals; they are recomputed over the benign residuals and labelled.
            benign = [r for r in convention['residuals'] if isinstance(r, dict) and r.get('run_id') not in run_ids
                      and _finite(r.get('residual_j'))]
            cells = {}
            for r in benign:
                cells.setdefault(r.get('cell'), []).append(r['residual_j'])
            df = sum(len(x) - 1 for x in cells.values())
            ss = math.fsum(sum((v - math.fsum(x) / len(x)) ** 2 for v in x) for x in cells.values())
            convention.update(s_r_j=math.sqrt(ss / df) if df > 0 else None, s_r_df=df,
                              cell_residual_counts={c: len(x) for c, x in cells.items()}, s_r_population='benign')
            block[label] = convention
        scopes[scope] = block
    return {**configuration, 'scopes': scopes}


def seal_w1_line(run_id, record, nonbenign, withhold):
    if run_id not in nonbenign:
        return record
    if withhold:
        return seal_line(run_id, record)
    flags = dict(record.get('harvest_flags') or {})
    if 'battery_discharge' in flags:
        flags['battery_discharge'] = withheld(flags['battery_discharge'])
    return {**record, 'harvest_flags': flags}


# --- the desk hook -------------------------------------------------------------------------------

def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n'
    temporary = path.with_name('.' + path.name + '.tmp')
    temporary.write_text(raw)
    os.replace(temporary, path)
    return hashlib.sha256(raw.encode()).hexdigest()


class DeskSeal:
    """``print_policy`` for ``align_pilot_session.desk``: (pilot, member lines) -> what may be recorded/printed.

    Writes the unsealed PILOT to ``<output>/archive/withheld/PILOT.full.json`` (``output`` is the session
    for a harvested desk, its inspection directory for ``--no-harvest``) and keeps it in ``full`` for the
    caller's in-memory gates (the v4 full-desk gate re-derives exclusion checks from the full members).
    """

    def __init__(self, plan_members, window_id_, scope, *, w1_withhold=None):
        # A list, or a zero-argument callable read when the desk applies the policy (the roster read stays
        # where the common desk reads it).
        self._plan_members = plan_members
        self.window_id = window_id_
        self.scope = scope
        self.w1_withhold = W1_WITHHOLD_SABOTAGE_GPU_AND_OUTCOMES if w1_withhold is None else w1_withhold
        self.full = None
        self.key = secrets.token_bytes(32)          # the caller runs the desk inside ``keyed(self.key)``

    @property
    def plan_members(self):
        members = self._plan_members() if callable(self._plan_members) else self._plan_members
        return list(members or ())

    def __call__(self, pilot, lines, *, output):
        self.full = pilot
        self._plan_members = self.plan_members      # resolve once
        digest = _write_json(Path(output) / WITHHELD_PILOT, pilot)
        _write_json(Path(output) / WITHHELD_KEY, {'schema': GUARD_SCHEMA + '.key', 'algorithm': DIGEST,
                                                  'key_hex': self.key.hex()})
        with keyed(self.key):
            return self._seal(pilot, lines, digest)

    def _seal(self, pilot, lines, digest):
        sealed = seal_pilot(pilot, self.plan_members, self.window_id, scope=self.scope, w1_withhold=self.w1_withhold)
        if self.scope == 'W1':
            nonbenign = _nonbenign(self.plan_members, pilot.get('members'))
            lines = [(rid, seal_w1_line(rid, record, nonbenign, self.w1_withhold)) for rid, record in lines]
        else:
            lines = [(rid, seal_line(rid, record)) for rid, record in lines]
        sealed['release_guard'] = {
            'schema': GUARD_SCHEMA, 'status': WITHHELD, 'window_id': self.window_id, 'scope': self.scope,
            'w1_withhold_sabotage_gpu_and_outcomes': self.w1_withhold if self.scope == 'W1' else None,
            'w1_exceptions': [e['output'] for e in W1_EXCEPTIONS if e['in_class']] if self.scope == 'W1' else None,
            'authority': 'desk-leak audit 2026-11-13; RL-149 section 3',
            'withheld_pilot': WITHHELD_PILOT, 'withheld_pilot_sha256': digest,
            'digest': DIGEST, 'digest_key': WITHHELD_KEY,
            'opens': 'release run (registered series_complete record plus lead-signed release receipt)'}
        return sealed, lines


class ReleasedDesk:
    """``print_policy`` after the registered release event: every field opens, and the desk records and prints
    that it ran released (RL-151 section 4 C4), so a forged or early release cannot pass for an ordinary desk."""

    def __init__(self, state):
        self.record = release_record(state)
        self.full = None

    def __call__(self, pilot, lines, *, output):
        self.full = pilot
        print('release_guard: released ' + json.dumps({k: self.record[k] for k in
              ('window_id', 'ruling', 'series_complete_sha256', 'release_receipt_sha256')}, sort_keys=True))
        return {**pilot, 'release_guard': self.record}, lines


def desk_policy(state, plan_members, *, w1_withhold=None):
    """The v4 desk's ``print_policy`` for ``state``: the seal, or :class:`ReleasedDesk` once released."""
    if released(state):
        return ReleasedDesk(state)
    return DeskSeal(plan_members, window_id(state), window_scope(state), w1_withhold=w1_withhold)


def benign_assist_counts(row, nonbenign):
    """W1 (PR #774 Sol F5, the C2 invariant applied to battery): with the benign battery rows printed whole, a
    window assist count over all members gives the non-benign members' assist count by subtraction, so the
    assist counts are over the benign members only and labelled so. B and unobserved counts decide eligibility
    (exclusion codes, per member already) and the bar verdict is registered, so they stay."""
    if not isinstance(row, dict):
        return row
    benign = [m for m in row.get('members') or () if isinstance(m, dict) and m.get('id') not in nonbenign]
    def count(code):
        return sum(code in (m.get('flags') or ()) for m in benign)
    from joulewise.align.apple.v4_battery import EXCLUDE, MISSING
    def any_of(codes):
        return sum(bool(set(m.get('flags') or ()) & set(codes)) or (m.get('status') not in (None, 'observed') and codes is MISSING)
                   for m in benign)
    # RL-152 section 3.2: every count beside the printed benign rows is over the benign rows; the bar verdict
    # (bar_pass, status, consequence) is computed in memory over all members and prints as a verdict.
    return {**row, 'assist_count': count('battery.assist'),
            'assist_outside_request_count': count('battery.assist_outside_request'),
            'B_count': any_of(EXCLUDE), 'unobserved_count': any_of(MISSING),
            'assist_population': 'benign', 'count_population': 'benign', 'counts_all_members': withheld(
                {k: row.get(k) for k in ('assist_count', 'assist_outside_request_count', 'B_count', 'unobserved_count')})}


def battery_print_row(state, row, plan_members):
    """The row the desk prints for a battery window: W1 under the switch prints benign-only assist counts."""
    if sealed_scope(state) == 'W1' and W1_WITHHOLD_SABOTAGE_GPU_AND_OUTCOMES:
        return benign_assist_counts(row, _nonbenign(plan_members))
    return row


# RL-152 section 3.4, tripwire 2: codes known and deliberately withheld per member (behaviour, outcome, carved,
# battery and contention disclosures). A code that is neither on FLAG_ALLOWLIST nor here is UNLISTED: a new
# instrument fault on a withheld member would otherwise be hidden.
KNOWN_WITHHELD_PREFIXES = (
    'episode.end_task', 'episode.max_turns', 'episode.time_guard', 'episode.deadman', 'episode.decode_budget',
    'episode.context_limit', 'episode.malformed_tool_call', 'episode.unsupported_tool_call_format',
    'episode.turn_token_budget_reached', 'turn_token_budget_reached', 'turn_budget_reached',
    'reasoning_censored_at_token_limit', 'calibration_censored_at_ceiling', 'ended_in_unclosed_reasoning',
    'cache.rebuilt_untrimmable', 'battery.', 'contention.', 'repetition.', 'energy.nonfinite_half_width',
    'thermal.gate_timeout', 'thermal.hold_timeout', 'thermal.os_level_nonzero', 'thermal.powermetrics_non_nominal')
TOOL_PATH_CODES = ('episode.unsupported_tool_call_format', 'episode.malformed_tool_call.json')


def unlisted_codes(flags):
    return sorted({c for c in (_code(f) for f in flags or ()) if c and not allowed_code(c)
                   and not c.startswith(KNOWN_WITHHELD_PREFIXES)})


def _admitted_turns(record):
    turns = record.get('turns')
    return turns if isinstance(turns, int) and turns >= 0 else len(record.get('turn_observation') or ())


def tool_path_fires(record):
    """RL-152 section 3.4 tripwire 1, one member: an unsupported XML or malformed JSON tool call on at least
    half of its admitted turns, and on at least two."""
    turns = {str(f).rsplit(':', 1)[1] for f in record.get('flags') or ()
             if str(f).startswith(tuple(c + ':' for c in TOOL_PATH_CODES))}
    return len(turns) >= 2 and 2 * len(turns) >= _admitted_turns(record)


def tripwires(records, scope, nonbenign):
    """RL-152 section 3.4: the two instrument-health lines, computed in memory; each prints one fact, no count
    of a withheld member. Returns (report, printed lines)."""
    report, lines = {}, []
    if scope == 'W1':
        fires = any(tool_path_fires(r) for r in records if r.get('id') in nonbenign)
        report['w1_non_benign_tool_path'] = {'verdict': 'to the research lead' if fires else 'within',
                                             'rule': 'RL-152 section 3.4 (chair ruling 2(d), :484-489)'}
        lines.append('W1 non-benign tool path (RL-152 section 3.4): ' + report['w1_non_benign_tool_path']['verdict'])
        benign = sum(len(unlisted_codes(r.get('flags'))) for r in records if r.get('id') not in nonbenign)
        withheld_present = any(unlisted_codes(r.get('flags')) for r in records if r.get('id') in nonbenign)
        report['unlisted_flag_codes'] = {'benign_members': benign, 'population': 'benign',
                                         'withheld_members': 'present, to the research lead' if withheld_present else 'none'}
        lines.append(f'W1 unlisted flag codes (RL-152 section 3.4): benign members {benign}; withheld members: '
                     + report['unlisted_flag_codes']['withheld_members'])
    else:
        total = sum(len(unlisted_codes(r.get('flags'))) for r in records)
        report['unlisted_flag_codes'] = {'all_members': total, 'population': 'all'}
        lines.append(f'unlisted flag codes (RL-152 section 3.4): all members {total}')
    return report, lines


def seals_balance(state):
    """Whether the R22-3 balance print is withheld now: C/T, and W1 with the switch on (RL-149 3)."""
    scope = sealed_scope(state)
    return scope in ('C', 'T') or (scope == 'W1' and W1_WITHHOLD_SABOTAGE_GPU_AND_OUTCOMES)


def sealed_scope(state):
    """The scope whose extra report and prints are sealed now, or ``None`` once released."""
    return None if released(state) else window_scope(state)


# --- the shared output boundary (PR #774 Sol seat F1) ---------------------------------------------

def is_v4_session(state):
    """Whether the STORED session/registration identity is ALIGN v4 (never the entry point or its kit argument).

    Any one of: a frozen series window; a v4 session id (``align-v4-`` prefix); a registration or pack path
    under an ``align_v4`` kit; a v4 registration receipt in the session's registration directory.
    """
    state = state or {}
    if state.get('v4_series'):
        return True
    if str(state.get('session_id', '')).startswith('align-v4'):
        return True
    paths = [state.get('registration_dir'), (state.get('inputs') or {}).get('pack_root')]
    for path in paths:
        if path and any(p == 'align_v4' or p.startswith(('align_v4_', 'align-v4')) for p in Path(str(path)).parts):
            return True
    registration = state.get('registration_dir')
    if registration:
        try:
            receipt = json.loads((Path(registration) / 'registration_receipt.json').read_bytes())
        except (OSError, ValueError):
            receipt = None
        if isinstance(receipt, dict) and str(receipt.get('schema', '')).startswith('joulewise.align_v4'):
            return True
    return False


def enforce(state, policy, plan_members):
    """The policy a v4 desk must run under: the given guard, or the guard installed now. An explicit ``None``
    installs it (it never disables protection); any other policy is refused."""
    if isinstance(policy, (DeskSeal, ReleasedDesk)):
        return policy
    if policy is None:
        return desk_policy(state, plan_members)
    raise ValueError('ALIGN v4 session (stored identity): the desk runs only under the release guard '
                     '(joulewise.align.apple.v4_desk_seal); a custom print_policy is refused')


def _thermal_desk_state(registration_dir):
    """The release-event root for the standalone thermal desk: the checkout holding its registration dir."""
    path = Path(registration_dir).resolve()
    parts = path.parts
    if len(parts) >= 4 and parts[-4:-1] == ('configs', 'campaigns', parts[-2]) and parts[-1] == 'registration':
        return {'measurement_root': str(path.parents[3])}
    return {'measurement_root': str(Path(__file__).resolve().parents[3])}


def guard_thermal_desk(result, prints, records, registration_dir, output):
    """``align_v4_thermal_desk`` output boundary (Sol F1): (PILOT, RL145_PRINTS, sealed?) to write.

    Before release the full PILOT and RL-145 prints go to ``<output>/archive/withheld/`` with the desk key; the
    written PILOT carries the C/T or W1 seal (scope from the members' windows; conditions from the records,
    an unknown condition counting as non-benign) and ``release_guard``. After release both open, with the
    released ``release_guard`` record.
    """
    state = _thermal_desk_state(registration_dir)
    if released(state):
        record = release_record(state)
        print('release_guard: released ' + json.dumps({k: record[k] for k in
              ('ruling', 'series_complete_sha256', 'release_receipt_sha256')}, sort_keys=True))
        return {**result, 'release_guard': record}, prints, False
    windows = {str(r.get('window')) for r in records if r.get('window') is not None}
    scope = ('T' if any(re.match(r'T[1-9]', w) for w in windows) else
             'C' if any(re.match(r'[CD][1-9]', w) for w in windows) else 'W1')
    plan = [{'run_id': r.get('id'), 'condition': r.get('condition'), 'ordinal': r.get('ordinal')} for r in records]
    nonbenign = _nonbenign(plan)
    key = secrets.token_bytes(32)
    output = Path(output)
    digest = _write_json(output / WITHHELD_PILOT, result)
    _write_json(output / 'archive/withheld/RL145_PRINTS.full.json', prints)
    _write_json(output / WITHHELD_KEY, {'schema': GUARD_SCHEMA + '.key', 'algorithm': DIGEST, 'key_hex': key.hex()})
    thermal_keys = ('schema', 'model_windows', 'deciding_experiment', 'members', 'tool_call_flags')
    with keyed(key):
        extra = seal_extra({'thermal': {k: result[k] for k in thermal_keys if k in result},
                            'registration_diagnostics': result.get('registration_diagnostics')}, plan, scope)
        sealed = {**extra['thermal'], 'registration_diagnostics': extra['registration_diagnostics'],
                  'u3_bar': result.get('u3_bar'), 'u3_pending': result.get('u3_pending'), 'wp19': result.get('wp19'),
                  'K_session_read': withheld(result.get('K_session_read'))}
        for key_name, value in result.items():
            if key_name not in sealed and key_name not in thermal_keys:
                sealed[key_name] = withheld(value)
        rows = prints.get('members') or [] if isinstance(prints, dict) else []
        sealed_prints = {k: prints[k] for k in ('schema', 'authority', 'print_only') if k in prints}
        if scope == 'W1' and not W1_WITHHOLD_SABOTAGE_GPU_AND_OUTCOMES:
            sealed_prints['members'] = rows
        else:
            visible = [] if scope in ('C', 'T') else [r for r in rows if r.get('id') not in nonbenign]
            sealed_prints.update(members=visible, population='benign' if scope == 'W1' else None,
                                 withheld_members=withheld([r for r in rows if r not in visible]))
        bins = {k: prints.get(k) for k in ('residual_by_decode_bin', 'residual_by_load_bin')}
        sealed_prints['residual_bins'] = withheld(bins)
    trip, lines = tripwires(records, scope, nonbenign)            # RL-152 section 3.4
    sealed.update(trip)
    for line in lines:
        print(line)
    sealed['release_guard'] = {
        'schema': GUARD_SCHEMA, 'status': WITHHELD, 'entry_point': 'scripts/align_v4_thermal_desk.py',
        'scope': scope, 'w1_withhold_sabotage_gpu_and_outcomes': W1_WITHHOLD_SABOTAGE_GPU_AND_OUTCOMES if scope == 'W1' else None,
        'authority': 'desk-leak audit 2026-11-13; RL-149 section 3; RL-151 section 4; PR #774 Sol F1',
        'withheld_pilot': WITHHELD_PILOT, 'withheld_pilot_sha256': digest,
        'withheld_prints': 'archive/withheld/RL145_PRINTS.full.json', 'digest': DIGEST, 'digest_key': WITHHELD_KEY,
        'opens': 'release run (registered series_complete record plus lead-signed release receipt)'}
    return sealed, sealed_prints, True


def sealed_markdown(sealed):
    """THERMAL.md for a sealed thermal desk: the U verdicts, the contrast verdict where it prints (W1), and each
    member's exclusion codes; every value is in PILOT.json's allowlist or withheld."""
    rows = ['# ALIGN v4 thermal desk (release guard: ' + WITHHELD + ')', '',
            '| Model/window | U1 | U2 | U3 | U4 | U5 | U6 |', '|---|---|---|---|---|---|---|']
    for key, result in (sealed.get('model_windows') or {}).items():
        rows.append('| ' + key + ' | ' + ' | '.join(str((result.get(f'U{k}') or {}).get('status')) for k in range(1, 7)) + ' |')
    contrast = sealed.get('deciding_experiment')
    if isinstance(contrast, dict) and 'verdict' in contrast:
        rows.extend(['', 'Deciding contrast: ' + str(contrast.get('verdict')) + ' (printed as registered; RL-149 section 3).'])
    rows.extend(['', '| Member | Excluded | Exclusion codes |', '|---|---|---|'])
    for member in sealed.get('members') or ():
        rows.append('| ' + str(member.get('id')) + ' | ' + str(member.get('excluded')) + ' | ' +
                    ', '.join(_strip(member.get('calibration_exclusions') or [])) + ' |')
    rows.extend(['', 'Member energy, gates, tokens and tool tables are withheld until series_complete '
                     '(archive/withheld/PILOT.full.json).', ''])
    return '\n'.join(rows)
