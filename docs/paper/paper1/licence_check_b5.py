"""Offline wording checks for the released Block 5 paper (RL-52 step 3).

Run: python3.13 -I -B docs/paper/paper1/licence_check_b5.py [--paper COPY]
     python3.13 -I -B docs/paper/paper1/licence_check_b5.py --self-test

Exit 0: no encoded violation; 1: wording violation; 2: unusable input.
This is a wording lint, not publication clearance. See the companion run report
for sentence-by-sentence judgments and matters requiring the research lead.
It reads only the supplied Markdown, the committed-text rederivation ledger,
and AST string literals in the disclosure producer; it executes no producer,
analysis, Git, network, model, or measurement code. No custody paths are followed.

Authority: release-to-paper audit §2 D constraints C1-C10, RL-4, RL-41,
RL-52 and RL-55. Fixed sentences are checked in Appendix C, allowing only
whitespace changes and initial capitalization. Internal labels need bracketed
glosses; paraphrases need an Appendix C label citation. Scope is Part 1:
BYTES text and unfilled replication branches are not result assertions.
The ledger hash pins the released inputs; collection-time eligibility remains
a recorded judgment. Value rounding is the separate fill_check_b5.py's job.
"""
from __future__ import annotations

import argparse
import ast
import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / 'docs/paper/paper1/paper1.md'
LEDGER = ROOT / 'docs/analysis/b5/rederivation.tsv'
PRODUCER = ROOT / 'joulewise/b5_analysis/disclosures.py'
LEDGER_SHA = '41b7e577a7be494245ed42ba38190da9de860430a75f5dc6d0987a15de79060f'
BOUNDARY = 'M3 Max / MLX / powermetrics SoC rails'
D177 = 'phase attribution is reported without a measured instrument phase-accounting check'


def norm(text: str) -> str:
    return ' '.join(text.replace('*', '').replace('`', '').split())


def visible(text: str) -> str:
    # Preserve line numbering, including multiline comments and FILL descriptions.
    def blank(match: re.Match[str]) -> str:
        return re.sub(r'[^\n]', ' ', match.group())
    return re.sub(r'\{\{FILL:.*?\}\}', blank,
                  re.sub(r'<!--.*?-->', blank, text, flags=re.S), flags=re.S)


@dataclass(frozen=True)
class Block:
    line: int
    section: str
    text: str


def blocks(text: str) -> list[Block]:
    """Markdown paragraphs and individual table rows; headings retain section IDs."""
    result = []
    section = 'title'
    pending: list[str] = []
    start = 1

    def flush() -> None:
        if pending:
            result.append(Block(start, section, '\n'.join(pending)))
            pending.clear()

    for line, value in enumerate(visible(text).splitlines(), 1):
        if value.startswith('#'):
            flush()
            section = value.lstrip('# ').strip()
        elif not value.strip():
            flush()
        elif value.startswith('|'):
            flush()
            # Column headers remain units in the inventory; rules are formatting.
            if not re.fullmatch(r'[| :\-]+', value):
                result.append(Block(line, section, value))
        else:
            if re.match(r'^(?:- |\d+\. )', value):
                flush()
            if not pending:
                start = line
            pending.append(value)
    flush()
    return result


def part1(block: Block) -> bool:
    s = block.section
    return not (s.startswith(('2.', '3.3', '7.', '10.', 'References',
                              'Appendix B', 'D.')) or s.startswith('6.8'))


@dataclass(frozen=True, order=True)
class Finding:
    line: int
    code: str
    reason: str


def load_ledger() -> dict[int, dict[str, str]]:
    raw = LEDGER.read_bytes()
    if hashlib.sha256(raw).hexdigest() != LEDGER_SHA:
        raise ValueError('rederivation.tsv differs from the RL-55 print authority')
    reader = csv.DictReader(raw.decode().splitlines(), delimiter='\t', quoting=csv.QUOTE_NONE)
    return dict(enumerate(reader, 2))


def fixed_sentences() -> dict[str, str]:
    """Extract literal definitions without importing the producer or its deps."""
    wanted = {'ATTRIBUTION_SENTENCE', 'GROSS_SENTENCE', 'AGREE_SENTENCE',
              'DIFFER_SENTENCE', 'DECISION_SENTENCE', 'LOO_SENTENCE',
              'MACHINE_BOUNDARY', 'CONDITIONALITY', 'ARM_SENTENCE',
              'MONITOR_SENTENCE', 'MIDPOINT_SENTENCE', 'TEMPERATURE_SENTENCE'}
    result = {}
    for node in ast.parse(PRODUCER.read_text(encoding='utf-8')).body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        if target.id in wanted:
            result[target.id] = ast.literal_eval(node.value)
        elif target.id == 'FIXED_SENTENCES':
            result.update(ast.literal_eval(node.value))
    if len(result) != 21:
        raise ValueError('disclosure fixed-sentence definitions changed; review the lint')
    return result


def outcome(estimate: Decimal, gate: Decimal | None,
            ci: tuple[Decimal, Decimal], di: tuple[Decimal, Decimal],
            rejects: bool, valid: bool = True) -> str:
    """Paper §4.8 precedence, not a replacement for the registered claim engine."""
    if not valid:
        return 'not estimable'
    ci_zero = ci[0] <= 0 <= ci[1]
    di_zero = di[0] <= 0 <= di[1]
    if gate is None or abs(estimate) <= gate or (di_zero and not ci_zero):
        return 'not resolvable'
    if ci_zero or not rejects:
        return 'unresolved'
    return 'direction supported'


def interval(text: str) -> tuple[Decimal, Decimal]:
    values = text.strip('[] ').replace('−', '-').split(',')
    if len(values) != 2:
        raise ValueError('expected two interval ends')
    lo, hi = map(Decimal, values)
    if not lo.is_finite() or not hi.is_finite() or lo > hi:
        raise ValueError('invalid interval')
    return lo, hi


def pvalue(text: str) -> Decimal:
    text = norm(text).translate(str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺', '0123456789-+'))
    return Decimal(re.sub(r'\s*×\s*10', 'e', text))


def has_d177(text: str) -> bool:
    text = norm(text).lower()
    return D177 in text or bool(re.search(
        r'phase attribution (?:was not checked|was not characterized).*?'
        r'(?:independent|instrument)', text))


def check(text: str, ledger: dict[int, dict[str, str]],
          fixed: dict[str, str]) -> list[Finding]:
    found: set[Finding] = set()
    bs = blocks(text)
    scoped = [b for b in bs if part1(b)]

    def fail(block: Block | None, code: str, reason: str) -> None:
        found.add(Finding(block.line if block else 1, code, reason))

    def section(prefix: str) -> list[Block]:
        return [b for b in bs if b.section.startswith(prefix)]

    all_text = norm(visible(text))
    if BOUNDARY not in all_text:
        fail(next(iter(section('3.1')), None), 'C8', 'missing exact SoC boundary label')

    # Assertive phrases only. Conditional method descriptions and negated
    # limitations are reviewed in the report, not silently counted as results.
    forbidden = (
        r'\btiming uncertainty dominates\b',
        r'\btiming attribution dominates (?:the detection floor|these measurements)\b',
        r'\b(?:the|our) measurement(?:s)? (?:is|are) attribution-limited\b',
        r'\benergy scales with (?:parameter count|model size)\b',
        r'\b(?:8B|1\.7B) (?:is|was) (?:more efficient|a cross-boundary winner)\b',
        r'\b(?:this|the) (?:result|study) proves\b',
        r'\b(?:universal|architecture-wide) (?:law|conclusion|result)\b',
        r'\b(?:Block 5|primary block|this contrast|these contrasts) (?:reaches?|supports?|achieves?) (?:level )?L[34]\b',
        r'\b(?:energy|joules) per parameter\b',
        r'\b(?:unresolved|not resolvable|refused) (?:means|shows) (?:equality|zero effect)\b',
        r'\b(?:BETA minus ALPHA|ALPHA minus BETA) (?:shows|supports|demonstrates)\b',
    )
    for b in scoped:
        plain = norm(b.text)
        for pattern in forbidden:
            if b.section.startswith('4.6') and 'Branch A holds when' in plain:
                continue  # prospective definition, not the selected branch
            for match in re.finditer(pattern, plain, re.I):
                if not re.search(r'\b(?:no|not|never)\b[^.;:]*$', plain[max(0, match.start()-45):match.start()], re.I):
                    fail(b, 'C3/C4/C5', 'forbidden assertion: ' + match.group())
        if re.search(r'sensitivity[ _-]clean', plain, re.I) and 'Erratum-3 bracket sensitivity only' not in plain:
            fail(b, 'RL4-vi', 'sensitivity clean lacks Erratum-3 bracket sensitivity only')
        if not plain.startswith('|') and re.search(r'\bp\s*[<≤=]\s*\d', plain, re.I):
            fail(b, 'RL4-ii', 'numerical p-value outside a results table')
        if re.match(r'\*Table (?:S[1-8]|[1-5])\.', b.text) and not has_d177(plain):
            fail(b, 'C7/RL4-x', 'Block 5 table caption lacks the D-177 limitation')

    class_blocks = [b for b in scoped if 'attribution_limited' in b.text]
    if not any(re.search(r'(?:set|determined|governed) by[^.;]*(?:clock.anchor|timing bound)',
                         norm(b.text), re.I) for b in class_blocks):
        fail(next(iter(class_blocks), None), 'RL4-viii',
             'floor class is named but not defined as a published floor set by the clock-anchor timing bound')

    for b in section('6.5'):
        plain = norm(b.text)
        if 'Registered descriptive estimates' in plain and re.search(r'\d\.\d+.*ratio|ratio.*\d\.\d+', plain):
            if not re.search(r'(?:timing|recorded).*?bounds.*?(?:not propagated|not included)|without (?:the )?recorded bounds', plain, re.I):
                fail(b, 'RL4-descriptive', 'energy-ratio paragraph omits that recorded timing bounds are not propagated')
        if plain.startswith(('Leave-one-quad-out.', 'Decision interval against the floor.')) and ' J' in plain and not has_d177(plain):
            fail(b, 'C7/RL4-x', 'phase-energy paragraph lacks the D-177 limitation')
        if 'Load-correlated exclusions not applied' in plain:
            if not ('could not compute' in plain and 'uncompared' in plain):
                fail(b, 'C9/RL4-vi', 'contrast load sensitivity needs registered refusal and uncompared recompute label')

    dom = section('6.4')
    dom_plain = norm(' '.join(b.text for b in dom))
    if 'point diagnostic; no interval' not in dom_plain.lower():
        fail(next(iter(dom), None), 'C5', 'dominance diagnostics need point diagnostic; no interval')
    if ledger[863]['printed_value'] != 'B' or ledger[864]['printed_value'] != 'false':
        raise ValueError('dominance licence changed; review branch-specific rules')
    for b in dom:
        if not b.text.startswith('| Qwen3-'):
            continue
        cells = [norm(x) for x in b.text.strip('|').split('|')]
        if len(cells) != 5:
            fail(b, 'C5', 'cannot parse dominance row')
            continue
        for value in cells[2:4]:
            if not re.search(r'\([\d.]+ ÷ [\d.]+\)', value):
                fail(b, 'C5', 'R lacks numerator and denominator')
        # Failed components may have their terms in the immediately following
        # prose; every component, including a passing one, still needs terms.
        ratio = cells[4].split()[0]
        inline_terms = bool(re.search(r'\([\d.]+ ÷ [\d.]+', cells[4]))
        prose_terms = bool(re.search(r'R_cm = ' + re.escape(ratio) + r' for [^(]+\([\d.]+ ÷ [\d.]+ J, n = \d+\)', dom_plain))
        if not inline_terms and not prose_terms:
            fail(b, 'C5', f'{cells[0]} {cells[1]} R_cm lacks numerator and denominator')
        if not ('n as in Table 3' in dom_plain or 'n =' in b.text):
            fail(b, 'C5', 'dominance row lacks n or an explicit n cross-reference')

    appendix = section('Appendix C.')
    appendix_text = norm(' '.join(b.text for b in appendix))
    for name, sentence in fixed.items():
        sentence = norm(sentence)
        capitalized = sentence[:1].upper() + sentence[1:]
        if sentence not in appendix_text and capitalized not in appendix_text:
            fail(next(iter(appendix), None), 'C6/RL4-xi', f'Appendix C omits/changes fixed sentence {name}')
    for b in appendix:
        if 'open question' in b.text:
            fail(b, 'C6/RL4-xi', 'Appendix C still leaves fixed-wording policy open after RL-4')
        if 'NEG-8' in b.text and not re.search(r'NEG-8[^\n]*\[|\[[^\]]*NEG-8', b.text):
            fail(b, 'C6/RL4-xi', 'internal NEG-8 label needs a bracketed gloss')

    # Named, unambiguous paraphrases; arbitrary paraphrase recognition is human.
    paraphrases = (
        ('3.4', 'The boundary of this', 'Whole-machine boundary'),
        ('6. Results', 'Every number is conditional', 'Conditionality'),
        ('6.2', '*Table 2.', 'Separate windows'),
        ('6.6', 'Across sessions within the primary block', 'cross-window agree/differ'),
    )
    for prefix, marker, label in paraphrases:
        for b in section(prefix):
            if marker in norm(b.text) or marker in b.text:
                if not re.search(r'Appendix C[^.;]*' + re.escape(label), norm(b.text), re.I):
                    fail(b, 'C6/RL4-xi', f'body paraphrase needs Appendix C label citation: {label}')

    contrast_rows = [b for b in section('6.5') if re.match(r'\| (?:decode|prefill \(2,048\)) \|', b.text)]
    if len(contrast_rows) != 2:
        fail(next(iter(section('6.5')), None), 'C4', 'print exactly both primary contrast rows')
    seen = set()
    for b in contrast_rows:
        try:
            cells = [norm(x) for x in b.text.strip('|').split('|')]
            if len(cells) != 9:
                raise ValueError('contrast table needs nine fields')
            phase = 'decode' if cells[0] == 'decode' else 'prefill'
            if phase in seen:
                raise ValueError('duplicate contrast')
            seen.add(phase)
            n, estimate = int(cells[1]), Decimal(cells[2])
            ci, di = interval(cells[3]), interval(cells[4])
            gate, p = Decimal(cells[5]), pvalue(cells[6])
            if not all(v.is_finite() for v in (estimate, gate, p)) or gate < 0 or not 0 <= p <= 1:
                raise ValueError('invalid contrast number')
            calculated = outcome(estimate, gate, ci, di, p <= Decimal('.05'))
            if cells[7] != calculated:
                fail(b, 'C2/precedence', f'printed outcome {cells[7]!r} contradicts §4.8: {calculated}')
            base = 530 if phase == 'decode' else 533
            expected = ledger[base]['printed_value'].replace('_', ' ')
            if cells[7] != expected:
                fail(b, 'C2', 'outcome differs from released registered word')
            if cells[8] == 'L2':
                loo_rows = (63, 64) if phase == 'decode' else (67, 68)
                loo = [Decimal(ledger[r]['printed_value']) for r in loo_rows]
                eligible = (
                    n >= 5 and calculated == 'direction supported' and estimate > 0
                    and ledger[base + 1]['printed_value'] == 'positive'
                    and ledger[base + 2]['printed_value'] == 'L2'
                    and ledger[525]['printed_value'] == 'none'
                    and ledger[526]['printed_value'] == 'none'
                    and all(x > gate for x in loo)
                )
                if not eligible:
                    fail(b, 'C2/L2', 'L2 gate conditions fail (including recorded eligibility inputs)')
            elif cells[8] not in {'L1', 'L0'}:
                fail(b, 'C2/L2', 'Block 5 cannot claim L3/L4 or an unknown level')
        except (ValueError, InvalidOperation) as exc:
            fail(b, 'C2/L2', f'unparseable contrast row: {exc}')

    methods = norm(' '.join(b.text for b in section('4.8')))
    words = ['not estimable', 'not resolvable', 'unresolved', 'direction supported']
    bullets = re.findall(r'^- \*\*([^*]+)\*\*:', '\n'.join(b.text for b in section('4.8')), re.M)
    if bullets != words:
        fail(next(iter(section('4.8')), None), 'C2/precedence', 'outcome precedence list differs from §4.8 rule')
    if not all(s in methods for s in ('registered one', 'not verdict-influential', 'confirmatory', 'L1')):
        fail(next(iter(section('4.8')), None), 'C2/L2', 'methods omit a stated L2 condition or L1 fallback')
    results = norm(' '.join(b.text for b in section('6.5')))
    if not all(s in results for s in ('collection-time records', 'did not re-derive', 'one session',
                                      '6 of 10 planned quads', '5 of 10 planned quads')):
        fail(next(iter(section('6.5')), None), 'RL4-iii/RL41', 'contrast context lacks session/counts/recorded-input qualification')
    return sorted(found)


def self_test() -> bool:
    """Mutations must add the specified finding, not merely retain baseline red."""
    ledger, fixed = load_ledger(), fixed_sentences()
    paper = PAPER.read_text(encoding='utf-8')

    class LicenceTests(unittest.TestCase):
        def test_precedence(self) -> None:
            d = Decimal
            yes = (d('1'), d('3'))
            zero = (d('-1'), d('3'))
            cases = [((None, zero, zero, False, False), 'not estimable'),
                     ((None, zero, zero, False, True), 'not resolvable'),
                     ((d('2'), zero, zero, False, True), 'not resolvable'),
                     ((d('1'), yes, zero, True, True), 'not resolvable'),
                     ((d('1'), zero, zero, True, True), 'unresolved'),
                     ((d('1'), yes, yes, False, True), 'unresolved'),
                     ((d('1'), yes, yes, True, True), 'direction supported')]
            for args, word in cases:
                with self.subTest(word=word, args=args):
                    self.assertEqual(outcome(d('2'), *args), word)

        def test_violating_copies(self) -> None:
            cases = [
                ('dominance', paper.replace('## 11. Conclusion', '## 11. Conclusion\n\nTiming uncertainty dominates.'), 'C3/C4/C5'),
                ('counts', paper.replace('| decode | 6 | 146.63', '| decode | 4 | 146.63'), 'C2/L2'),
                ('outcome', paper.replace('| direction supported | L2 |', '| unresolved | L2 |', 1), 'C2/precedence'),
                ('missing-row', paper.replace(next(b.text for b in blocks(paper) if b.text.startswith('| decode | 6 |')), ''), 'C4'),
                ('sensitivity', paper.replace('## 11. Conclusion', '## 11. Conclusion\n\nSensitivity clean.'), 'RL4-vi'),
                ('cross-floor', paper.replace('## 11. Conclusion', '## 11. Conclusion\n\nBETA minus ALPHA shows a model effect.'), 'C3/C4/C5'),
                ('higher-level', paper.replace('## 11. Conclusion', '## 11. Conclusion\n\nBlock 5 reaches L3.'), 'C3/C4/C5'),
                ('p-prose', paper.replace('## Abstract', '## Abstract\n\np = 0.001.'), 'RL4-ii'),
                ('caption', paper.replace(
                    'Phase attribution is reported without a measured instrument\nphase-accounting check.*', ''), 'C7/RL4-x'),
            ]
            baseline = set(check(paper, ledger, fixed))
            with tempfile.TemporaryDirectory(prefix='jw-b5-licence-') as directory:
                for name, mutant, code in cases:
                    with self.subTest(copy=name):
                        path = Path(directory) / (name + '.md')
                        self.assertNotEqual(mutant, paper)
                        path.write_text(mutant, encoding='utf-8')
                        added = set(check(path.read_text(encoding='utf-8'), ledger, fixed)) - baseline
                        self.assertTrue(any(f.code == code for f in added), added)
                        if name == 'caption':
                            self.assertTrue(any(f.code == code and f.line == 852 for f in added), added)

        def test_comments_and_templates_are_not_results(self) -> None:
            extra = '\n<!-- Timing uncertainty dominates. -->\n{{FILL: pending | p = 0.001}}\n'
            self.assertNotIn('Timing uncertainty dominates', visible(extra))
            self.assertNotIn('p = 0.001', visible(extra))
            # Appending cannot move existing finding locations.
            self.assertEqual(check(paper + extra, ledger, fixed), check(paper, ledger, fixed))

    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(LicenceTests))
    return result.wasSuccessful()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--paper', type=Path, default=PAPER, help='working paper or deliberately violating copy')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    try:
        if args.self_test:
            return 0 if self_test() else 1
        findings = check(args.paper.read_text(encoding='utf-8'), load_ledger(), fixed_sentences())
    except (OSError, ValueError, SyntaxError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps([f.__dict__ for f in findings], indent=2))
    else:
        for f in findings:
            print(f'L{f.line} {f.code}: {f.reason}')
        print(f'{"FAIL" if findings else "PASS"}: {len(findings)} mechanical licence violation(s); judgment review still required')
    return 1 if findings else 0


if __name__ == '__main__':
    raise SystemExit(main())
