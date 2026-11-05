"""Copy released block-5 results into a reviewable, non-issuing paper candidate.

No analysis, raw-data access, custody issuance, outcome selection, or claim prose.
The independent comparator owns leaf routing and bars; the post-release reader
owns uncovered checks and the Results cold gate. See docs/process/b5_results_renderer.md.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

from joulewise.authentication_io import read_authentication_input_nofollow
from joulewise.b5_analysis.disclosures import render_disclosures, SCHEMA as DISCLOSURE_SCHEMA
from joulewise.b5_analysis.dry_run import STEP_IDS, SCHEMA as RELEASE_SCHEMA, SEAL_KEYS, is_nonstopping_outcome
from joulewise.analysis_engine.artifact import _ATTRIBUTION_FLOOR_KEYS
from scripts import compare_b5_recompute as cmp

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / 'docs/paper/block5/Results.template.md'
REVIEW_SCHEMA = 'joulewise.b5_results_review.v1'
PROVENANCE_SCHEMA = 'joulewise.b5_results_provenance.v1'
ROLE_PATTERNS = {
    'fill': r'outputs/[0-9a-f]{64}-results-fill-input\.json',
    'disclosure': r'disclosures/[0-9a-f]{64}\.json',
    'released_view': r'disclosures/[0-9a-f]{64}\.released\.txt',
    'unreleased_view': r'disclosures/[0-9a-f]{64}\.unreleased\.txt',
    'verdicts': r'outputs/[0-9a-f]{64}-claim-verdicts\.json',
}


class RendererRefusal(ValueError):
    """A rendering defect or pending review; never a scientific outcome."""


def need(condition, code):
    if not condition:
        raise RendererRefusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
                      allow_nan=False).encode('utf-8')


def loads(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate_key')
            result[key] = value
        return result

    def nonfinite(_):
        raise RendererRefusal('nonfinite_number')

    try:
        value = json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)
        canonical(value)  # also catches overflowing JSON exponents
        return value
    except (UnicodeError, ValueError, TypeError, OverflowError, RecursionError) as exc:
        if isinstance(exc, RendererRefusal):
            raise
        raise RendererRefusal('invalid_json') from None


def read_file(path):
    path = Path(path).absolute()
    return read_under(path.parent, path.name)


def read_under(root, name):
    """Only explicitly named, symlink-free files. Never walk a custody tree."""
    root = Path(root).absolute()
    need(isinstance(name, str) and bool(name) and '\\' not in name and '\x00' not in name
         and not Path(name).is_absolute()
         and all(p not in ('', '.', '..') for p in name.split('/')), 'unsafe_path')
    try:
        return read_authentication_input_nofollow(root, name, grammar='raw', label='B5 Results input')
    except (OSError, ValueError, RuntimeError):
        raise RendererRefusal('input_unreadable_or_symlink') from None


def keys(value, expected):
    need(type(value) is dict and set(value) == set(expected), 'missing_or_unexpected_field')


def pointer(at):
    return '/' + '/'.join(str(part).replace('~', '~0').replace('/', '~1') for part in at)


def resolve(value, ptr):
    need(isinstance(ptr, str) and ptr.startswith('/') and ptr != '/', 'invalid_recompute_pointer')
    try:
        for token in ptr[1:].split('/'):
            need(re.search(r'~(?![01])', token) is None, 'invalid_recompute_pointer')
            token = token.replace('~1', '/').replace('~0', '~')
            if isinstance(value, list):
                need(re.fullmatch(r'0|[1-9][0-9]*', token) is not None, 'invalid_recompute_pointer')
                value = value[int(token)]
            else:
                value = value[token]
        return value
    except (KeyError, TypeError, IndexError):
        raise RendererRefusal('invalid_recompute_pointer') from None


def _fill_shape(fill, verdicts, registry):
    """The complete extended step-11 projection, compared to its released parent."""
    keys(fill, cmp.FILL_SHAPE['top'])
    need(fill['schema_version'] == 'joulewise.results_fill_input.v1', 'fill_schema')
    keys(fill['campaigns'], ('alpha', 'beta'))
    for campaign in fill['campaigns'].values():
        keys(campaign, cmp.FILL_SHAPE['campaign'])
    keys(fill['characterization'], cmp.FILL_SHAPE['characterization'])
    gamma = fill['gamma']
    keys(gamma, cmp.FILL_SHAPE['gamma'])
    keys(gamma['floor_artifact'], cmp.FILL_SHAPE['floor_artifact'])
    rows = gamma['contrasts']
    expected = list(registry.tables['contrast'])
    need(type(rows) is list and [r['contrast_id'] for r in rows] == expected, 'contrast_census')
    need([r['contrast_id'] for r in verdicts['contrasts']] == expected, 'verdict_census')
    parent = verdicts['inputs']
    need(gamma['claim_verdicts_id'] == verdicts['claim_verdicts_id']
         and gamma['evidence_class'] == parent['evidence_class']
         and gamma['limitations'] == parent['limitations']
         and gamma['finalized_manifest'] == parent['analysis_manifest']
         and gamma['floor_artifact'] == {k: parent['floor_artifact'][k] for k in cmp.FILL_SHAPE['floor_artifact']},
         'fill_parent_mismatch')
    from joulewise.results_fill_adapter import _contrast_limitations
    for row, source in zip(rows, verdicts['contrasts'], strict=True):
        keys(row, cmp.FILL_SHAPE['contrast'])
        for field, shape in (('metric', 'metric'), ('conditions', 'conditions'),
                             ('multiplicity', 'multiplicity'), ('claim_evaluation', 'evaluation'),
                             ('loo', 'loo')):
            keys(row[field], cmp.ENGINE_KEYS[shape])
        keys(row['sampling'], (*cmp.ENGINE_KEYS['sampling'], *cmp.ENGINE_KEYS['kept_sampling']))
        floor_keys = set(cmp.ENGINE_KEYS['floor']) | set(cmp.ENGINE_KEYS['v3_floor'])
        if set(row['floor']) & _ATTRIBUTION_FLOOR_KEYS:
            floor_keys |= _ATTRIBUTION_FLOOR_KEYS
        keys(row['floor'], floor_keys)
        for field, shape in (('resolutions', 'resolution'), ('arm_gates', 'arm_gate')):
            for item in row['floor'][field]:
                expected_keys = set(cmp.ENGINE_KEYS[shape])
                if shape == 'resolution' and set(item) & _ATTRIBUTION_FLOOR_KEYS:
                    expected_keys |= _ATTRIBUTION_FLOOR_KEYS
                keys(item, expected_keys)
        for item in row['loo']['rows']:
            keys(item, cmp.ENGINE_KEYS['loo_row'])
        for interval in (row['interval'], row['decision_interval']):
            if interval is not None:
                keys(interval, ('lower', 'upper'))
        direct = ('contrast_id', 'metric', 'conditions', 'floor', 'multiplicity', 'claim_evaluation',
                  'plan_id', 'claim_role', 'hypothesized_direction', 'equivalence', 'sampling', 'loo')
        projected = {k: source[k] for k in direct}
        projected.update({k: source['estimator'][k] for k in ('n', 'df', 't_critical_95', 'estimate')})
        included = {b['block_id'] for b in source['bundle_blocks']['blocks'] if b['included'] is True}
        planned = source['bundle_blocks']['planned_block_ids']
        projected.update(
            limitations=_contrast_limitations(verdicts, source),
            floor_source_cell_ids=source['floor']['floor_row_ids'],
            interval=source['estimator']['metrology_aware_CI95'],
            decision_interval=source['deterministic_bounds']['decision_interval'],
            deterministic_widening_total=source['deterministic_bounds']['total'],
            j_per_token=source['estimator']['estimate'] if source['metric']['unit'] == 'J/token' else None,
            kept_block_ids=[b for b in planned if b in included],
            removed_block_ids=[b for b in planned if b not in included])
        need(canonical(row) == canonical(projected), 'fill_parent_mismatch')
    cmp.gate_fill(fill)
    cmp.gate(fill, 'fill', registry)


def _release_outputs(record):
    need(record.get('schema_version') == RELEASE_SCHEMA
         and record.get('mode') == 'release' and record.get('completed_without_tooling_refusal') is True
         and 'release_difference' not in record, 'release_not_complete')
    keys(record['sealed'], SEAL_KEYS)
    need(re.fullmatch(r'[0-9a-f]{40}', record['analysis_commit']) is not None, 'release_identity')
    rows = record['steps']
    order = []
    for row in rows:
        if not order or order[-1] != row['step']:
            order.append(row['step'])
        need(row['status'] == 'ok' or is_nonstopping_outcome(row), 'release_step_not_complete')
        if row['status'] == 'ok':
            need(row['exit_status'] == 0 or (row['step'] == '4' and row['exit_status'] == 1
                 and row['registered_exit'] == 'p42_floor_cells_only'), 'release_step_not_complete')
    need(tuple(order) == STEP_IDS and sum(r['step'] == '9b' for r in rows) == 1, 'release_step_census')
    listed = {}
    for row in rows:
        for entry in row['outputs']:
            keys(entry, ('name', 'sha256'))
            need(entry['name'] not in listed and re.fullmatch(r'[0-9a-f]{64}', entry['sha256']) is not None,
                 'release_output_census')
            listed[entry['name']] = (entry['sha256'], row['step'])
    return listed


@dataclass
class Inputs:
    bindings: dict
    documents: dict
    names: dict
    comparison: dict
    recompute: dict
    registry: object
    nonissuance: bool


class ReleasedCustody:
    """Comparator interface backed solely by listed, digest-checked outputs."""
    def __init__(self, root, listed, registry):
        self.root, self.listed, self.registry = root, listed, registry
        self.nonfinite, self.cache, self.digests = {}, {}, {}

    def names(self, pattern):
        return sorted(name for name in self.listed if re.fullmatch(pattern, name))

    def read(self, name):
        if name not in self.cache:
            need(name in self.listed, 'unlisted_artifact')
            raw = read_under(self.root, name)
            need(sha(raw) == self.listed[name][0], 'release_digest_mismatch')
            label = next((label for label, pattern in cmp.STEP11_SOURCES if re.fullmatch(pattern, name)), None)
            value = (cmp.strict_loads(raw, label, cmp.STEP11_TAILS[label]) if label else loads(raw))
            if label:
                cmp.gate(value, label, self.registry)
                (cmp.gate_fill if label == 'fill' else cmp.gate_lines)(value)
            self.cache[name], self.digests[name] = value, sha(raw)
        return self.cache[name]

    def one(self, pattern):
        names = self.names(pattern)
        need(len(names) <= 1, 'ambiguous_artifact')
        return self.read(names[0]) if names else None


def load_inputs(release_dir, artifacts_dir, comparison_path, recompute_path, window_index=None):
    try:
        return _load_inputs(release_dir, artifacts_dir, comparison_path, recompute_path, window_index)
    except RendererRefusal:
        raise
    except cmp.Refusal:
        raise RendererRefusal('released_artifact_invalid') from None
    except (KeyError, TypeError, ValueError, IndexError, AttributeError):
        raise RendererRefusal('input_shape_invalid') from None


def _load_inputs(release_dir, artifacts_dir, comparison_path, recompute_path, window_index):
    """Read only released artifacts by record digest and the supplied recompute evidence.

    artifacts_dir is explicit: no search for restricted roots or evidence paths.
    Release verification/event ordering remains the designated lead's prerequisite.
    """
    record_raw = read_under(release_dir, 'B5-RELEASE-RECORD.json')
    record = loads(record_raw)
    listed = _release_outputs(record)
    raw, names = {}, {}
    for role, pattern in ROLE_PATTERNS.items():
        found = [name for name in listed if re.fullmatch(pattern, name)]
        need(len(found) == 1, 'missing_or_ambiguous_artifact')
        name = found[0]
        need(listed[name][1] == ('9' if role == 'verdicts' else '11'), 'artifact_wrong_step')
        raw[role] = read_under(artifacts_dir, name)
        need(sha(raw[role]) == listed[name][0], 'release_digest_mismatch')
        names[role] = name
    comparison_raw, recompute_raw = read_file(comparison_path), read_file(recompute_path)
    comparison, recompute = loads(comparison_raw), loads(recompute_raw)
    need(comparison.get('schema') == cmp.SCHEMA and 'refused' not in comparison, 'comparison_schema')
    need(recompute.get('schema') == 'joulewise.independent_recompute_b5.v1'
         and recompute.get('mode') == 'REGISTERED', 'recompute_schema_or_mode')
    bars = cmp.load_bars(cmp.DEFAULT_BARS)
    need(comparison['bar_set'] == bars['bar_set'] and comparison['bars'] == bars['families'], 'wrong_recompute_bars')
    need(not comparison['structure_flags'] and bool(comparison['comparisons'])
         and all(r['verdict'] == 'AGREE' for r in comparison['comparisons'])
         and all(c['fail'] == 0 for c in comparison['counts'].values()), 'recompute_disagreement')
    for field in ('unmapped', 'uncompared', 'unbound', 'absent_sources', 'nonfinite'):
        need(not comparison['coverage'][field], 'recompute_coverage_incomplete')
    program_digest = recompute['program_sha256']
    need(isinstance(program_digest, str) and re.fullmatch(r'[0-9a-f]{64}', program_digest) is not None
         and comparison['recompute_program_sha256'] == program_digest, 'recompute_program_mismatch')
    index_path = cmp.WINDOW_INDEX if window_index is None else Path(window_index)
    index_raw = read_file(index_path)
    need(sha(index_raw) == record['window_index_sha256'], 'window_index_mismatch')
    # This comparator helper parses the index only; it follows none of its paths.
    registry = cmp.indexed(cmp.load_registry(), cmp.load_window_index(index_path, record))
    need(comparison['routing_registry_sha256'] == registry.digests, 'recompute_registry_mismatch')
    custody = ReleasedCustody(artifacts_dir, listed, registry)
    structural = cmp.Comparison(bars)
    table = cmp.compare_expected(structural, custody, recompute)
    need(all(row['verdict'] == 'AGREE' for row in structural.rows), 'released_structure_incomplete')
    need(cmp.table_structure(table) == comparison['expected_checks'], 'comparison_check_census')
    structural.rows = comparison['comparisons']
    cover = cmp.coverage(custody, structural)
    need(cover == comparison['coverage'], 'comparison_coverage_mismatch')
    fill = cmp.strict_loads(raw['fill'], 'fill', b'\n')
    disclosure = cmp.strict_loads(raw['disclosure'], 'disclosure', b'')
    verdicts = loads(raw['verdicts'])
    _fill_shape(fill, verdicts, registry)
    need(fill['gamma']['claim_verdicts_sha256'] == sha(raw['verdicts']), 'verdict_digest_mismatch')
    keys(disclosure, cmp.DISCLOSURE_SHAPE['top'])
    need(disclosure['schema_version'] == DISCLOSURE_SCHEMA, 'disclosure_schema')
    cmp.gate(disclosure, 'disclosure', registry)
    cmp.gate_lines(disclosure)
    for role, released in (('released_view', True), ('unreleased_view', False)):
        need(render_disclosures(disclosure, released=released).encode() == raw[role], 'disclosure_view_mismatch')
    bindings = {role: sha(data) for role, data in raw.items()}
    bindings.update(release_record=sha(record_raw), comparison=sha(comparison_raw), recompute=sha(recompute_raw),
                    window_index=sha(index_raw), structural_sources=custody.digests)
    return Inputs(bindings, {'fill': fill, 'disclosure': disclosure}, names, comparison, recompute, registry,
                  any(is_nonstopping_outcome(r) for r in record['steps']))


def leaf_checks(inputs):
    """Concrete leaf -> exact automatic comparison, manual check, or listed metadata.

    The comparator's coverage paths intentionally collapse list indices. We use
    its owner-derived context to bind each concrete leaf to its own row again.
    """
    report = inputs.comparison
    rows = {}
    for row in report['comparisons']:
        key = (row['family'], row['key'])
        need(key not in rows, 'duplicate_comparison_row')
        rows[key] = row
    result = {}
    for label, document in inputs.documents.items():
        for path, value, context in cmp.leaves(document, label):
            collapsed = label + ':' + path
            concrete = label + ':' + pointer(context['@@at'])
            need(concrete not in result, 'duplicate_leaf')
            number = cmp.numeric(value) or value is None
            rule = match = None
            for candidate in cmp.COVERAGE:
                match = re.fullmatch(candidate[0], collapsed)
                if match and cmp.admits(candidate, value, number, False, cmp.numeric_word(value)):
                    rule = candidate
                    break
            if rule is None and value in ([], {}):
                result[concrete] = {'status': 'LISTED', 'reason': 'empty container; no printed value'}
                continue
            need(rule is not None and collapsed in report['coverage']['leaves'], 'missing_or_unexpected_leaf')
            if len(rule) == 3:
                family = rule[1]
                key, _ = cmp.key_for(rule[2], context, match.groupdict(), inputs.registry)
                row = rows.get((family, key))
                need(row is not None and row['verdict'] == 'AGREE'
                     and cmp.same(row.get('l9_raw', row['l9']), value), 'leaf_comparison_mismatch')
                need(all(rows.get(('routing_id', item), {}).get('verdict') == 'AGREE'
                         for item in row.get('items', [])), 'leaf_route_mismatch')
                result[concrete] = {'status': 'AUTO_AGREE', 'family': family, 'key': key,
                                    'qualification': row.get('reason')}
            else:
                # All text is reviewed: digits embedded in prose are not numerically
                # covered by a neighbouring typed value. Nulls count as printed leaves.
                manual = number or cmp.numeric_word(value) or path.endswith('/text')
                result[concrete] = ({'status': 'PENDING', 'reviewer': None, 'recompute_pointers': [], 'note': None}
                                    if manual else {'status': 'LISTED', 'reason': rule[1]})
    return result


def prepare_review(inputs):
    return {'schema_version': REVIEW_SCHEMA, 'bindings': inputs.bindings,
            'gate': {'release_event': None, 'reader': None, 'first_read_utc': None,
                     'results_cold_gate': None, 'judge': None, 'refuter': None},
            'checks': leaf_checks(inputs)}


def validate_review(inputs, review, *, allow_pending=False):
    expected = prepare_review(inputs)
    keys(review, expected)
    need(review['schema_version'] == REVIEW_SCHEMA and review['bindings'] == inputs.bindings, 'stale_review')
    keys(review['gate'], expected['gate'])
    if not allow_pending:
        need(all(isinstance(v, str) and v.strip() for v in review['gate'].values()), 'results_gate_pending')
        need(review['gate']['judge'] != review['gate']['refuter'], 'results_gate_not_independent')
    keys(review['checks'], expected['checks'])
    for leaf, check in expected['checks'].items():
        actual = review['checks'][leaf]
        if check['status'] != 'PENDING':
            need(actual == check, 'automatic_check_changed')
            continue
        if allow_pending and actual == check:
            continue
        keys(actual, check)
        need(actual['status'] == 'HAND_CHECKED' and isinstance(actual['reviewer'], str)
             and actual['reviewer'].strip() and isinstance(actual['note'], str) and actual['note'].strip()
             and type(actual['recompute_pointers']) is list and bool(actual['recompute_pointers']), 'hand_check_pending')
        for ptr in actual['recompute_pointers']:
            resolve(inputs.recompute, ptr)


def cell(value):
    """Lossless staging display; no new scientific rounding convention."""
    text = 'not available (null)' if value is None else (
        value if isinstance(value, str) else canonical(value).decode())
    return html.escape(text, quote=False).replace('|', '&#124;').replace('`', '&#96;').replace('\n', '<br>')


def contrast_sections(rows):
    """Copy every row without selecting, estimating or deciding claim wording."""
    table = ['| Contrast | Issued outcome | Direction | Ceiling | n | Estimate | Unit | Metrology interval | Decision interval | Operative floor | Paper placement |',
             '|---|---|---|---|---:|---:|---|---|---|---|---|']
    for row in rows:
        verdict = row['claim_evaluation']
        table.append('| ' + ' | '.join(cell(v) for v in (
            row['contrast_id'], verdict['outcome'], verdict['direction'], verdict['claim_level_ceiling'],
            row['n'], row['estimate'], row['metric']['unit'], row['interval'], row['decision_interval'],
            row['floor']['active_floor_j'], 'STOP_FILL / NEEDS-LEAD')) + ' |')
    details = []
    for row in rows:
        details += [f"### {cell(row['contrast_id'])}", '', '| Released field | Value |', '|---|---|']
        for path, value, context in cmp.leaves(row, 'fill'):
            details.append('| ' + cell(pointer(context['@@at'])) + ' | ' + cell(value) + ' |')
        details.append('')
    return '\n'.join(table), '\n'.join(details)


def render(inputs, review, template_raw=None, *, allow_pending=False):
    validate_review(inputs, review, allow_pending=allow_pending)
    template_raw = read_file(TEMPLATE) if template_raw is None else template_raw
    template = template_raw.decode('utf-8')
    table, details = contrast_sections(inputs.documents['fill']['gamma']['contrasts'])
    disclosure = render_disclosures(inputs.documents['disclosure'], released=True)
    # Indented literal block prevents source text from introducing Markdown/HTML.
    disclosure = '\n'.join('    ' + line for line in disclosure.splitlines())
    substitutions = {'REVIEW_STATE': ('PENDING / REVIEW CANDIDATE ONLY' if allow_pending else
                                     'Results checks and cold gate recorded; placements remain STOP_FILL'),
                     'CONTRAST_TABLE': table, 'CONTRAST_DETAILS': details,
                     'DISCLOSURES': disclosure,
                     'CLAIM_CUSTODY': ('claim_side_bound_not_issuable; no VerifiedClaimEvidence; STOP_FILL'
                                      if inputs.nonissuance else 'Issuing grants and placements require lead adoption; STOP_FILL')}
    need(set(re.findall(r'\{\{([A-Z_]+)\}\}', template)) == set(substitutions), 'template_census')
    for token in substitutions:
        need(template.count('{{' + token + '}}') == 1, 'template_census')
    template = re.sub(r'\{\{([A-Z_]+)\}\}', lambda m: substitutions[m[1]], template)
    provenance = []
    for label, document in inputs.documents.items():
        for _, value, context in cmp.leaves(document, label):
            ptr = pointer(context['@@at'])
            leaf = label + ':' + ptr
            provenance.append({'leaf': leaf, 'value': value, 'printed': cell(value),
                               'released_path': inputs.names[label], 'json_pointer': ptr,
                               'sha256': inputs.bindings[label], 'check': review['checks'][leaf]})
    manifest = {'schema_version': PROVENANCE_SCHEMA, 'bindings': inputs.bindings,
                'review_canonical_sha256': sha(canonical(review)), 'template_sha256': sha(template_raw),
                'results_sha256': sha(template.encode()), 'gate': review['gate'], 'leaves': provenance}
    lines = ['| Printed value / text | Released leaf | File SHA-256 | Recompute status |', '|---|---|---|---|']
    lines += ['| ' + ' | '.join((cell(r['value']), cell(r['released_path'] + '#' + r['json_pointer']),
                                r['sha256'], cell(r['check']['status'] +
                                    (' (' + r['check']['qualification'] + ')' if r['check'].get('qualification') else ''))))
              + ' |' for r in provenance]
    return {'Results.md': template.encode(), 'provenance.json': canonical(manifest) + b'\n',
            'provenance.md': ('\n'.join(lines) + '\n').encode()}


def publish(output, files):
    """Publish a complete new directory only; never overwrite a paper or custody."""
    output = Path(output).absolute()
    need(not output.exists() and not output.is_symlink(), 'output_exists')
    need(output.parent.resolve() == output.parent, 'unsafe_output_parent')
    staging = Path(tempfile.mkdtemp(prefix='.b5-results-', dir=output.parent))
    reserved = False
    try:
        for name, raw in files.items():
            with (staging / name).open('xb') as stream:
                stream.write(raw)
        try:
            output.mkdir()  # exclusive reservation; never replace an existing directory
        except FileExistsError:
            raise RendererRefusal('output_exists') from None
        reserved = True
        # Only our empty reservation is replaced. No prose exists until rename.
        os.rename(staging, output)
        reserved = False
    finally:
        if reserved:
            try:
                output.rmdir()
            except OSError:
                pass
        if staging.exists():
            shutil.rmtree(staging)


def validate_rendered(output, expected):
    """Re-derive and compare every byte, including the contrast row census."""
    output = Path(output)
    for name, raw in expected.items():
        need(read_under(output, name) == raw, 'rendered_mismatch')
    # The no-follow reads must succeed before even listing an output directory.
    need(set(p.name for p in output.iterdir()) == set(expected), 'rendered_file_census')
