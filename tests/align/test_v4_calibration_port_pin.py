"""Merge-order guard (docs/analysis/v4/MERGE-ORDER.md): the engine's calibration
predicate must stay a byte-identical port of align/2026-11-08-v4-r11 @ bbfccb70a.

Pinned are the source segments, as written in each file, of calibration_stop, every
helper it calls and every module constant it reads, including the kit's
lead-signature check. If r11 changes any of them, this test fails and forces a
re-port; the rest of v4_cadence.py and the arm stack are r11-owned and r11 wins
on merge.
"""
import ast
import hashlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
R11_COMMIT = 'bbfccb70ab993c395f254058694906610547651d'
PINS = {
    'joulewise/align/apple/v4_cadence.py': {
        'CAL_PAIRS': '0c97e67c00853b7d941e7e8e1795e099ef95a9f13aea61f56f09d6bcd20daec9',
        'CAL_WINDOWS': 'f0353abebb5cf5fb4ffe9c8996604dff44ebae571563e9f5f4a5b85ec026bae7',
        'CAL_TARGET_PER_PAIR': '64fd356e345424750ac8858e2d1af8945d220f37f68c32757a0ba698c115f552',
        'BENIGN_PER_PAIR_PER_WINDOW': 'd18c267529ce4e9fe7a08924c820e79def73a8d09ce12eb0c9f009f0ef9a2a5c',
        'WINDOW_MEMBERS': 'e165539d70a5857f2d7fd6d6d15a5827290a866fa3881c5fb9e48a78bcaed84f',
        'CAPTURED_MAX': '1908ca9329ad12879bf7a03daade294c9b7ddba09d85ef73c8b549a8dbaaa156',
        'REPLACEMENT_WINDOWS': 'c0cbbb4d2f9771a224b6ad56ab56e98f83c09650a33416da9fce367b139ba7e6',
        'STRUCTURAL_BARS': 'b32e4c6dd4055fff3169f21272df2bb9316cfe3985c587b852c5f25c122acd0b',
        'ZERO_CAPTURE_BAR': 'c4a4efc50d3841d55f82c9c0e95b5794eb47168d5d19d110a4c08e67fa283948',
        'RULING_RESETS': 'ef93d90bca6c86326614d516fea88bb4e75bad6b25e5c04a2ae15bd85c12bdc6',
        '_is_digest': 'e6522ce9226cc346255b6c0a6af6e5506e681175fd2dbb09593d9b64fbefb18b',
        'slot_of': '89a2848e2bb1f49afced78f7ad68dc48cbe32ffd6f4e13bf1c2291688cf5821e',
        '_validated_rulings': 'b1511813dd58568e838df9c99890ccd5a5ec74fe77d97d9d28d62b6c8c13928d',
        'calibration_stop': 'b788b2c30cae011cf8f36127a39b90eb487457b3fcb9b3e790b5bb0d93e7b137',
    },
    'scripts/align_v4_kit.py': {
        'UNSIGNED': 'd6ff0fc7a42c0ff1f1ad8555c0d49ea7c76055202b6d466bf0d5a2e0a00886cf',
        'valid_lead_signature': 'a9d71cc7d2c87d03924ab12fd3dbe4800b6a5f91cfa1cccaa2f747ac77b14e64',
    },
}


def top_level_segments(path):
    source = (ROOT/path).read_text()
    segments = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.FunctionDef):
            names = [node.name]
        elif isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        else:
            continue
        for name in names:
            if name in segments:
                raise AssertionError(f'{path}: {name} defined twice at top level')
            segments[name] = ast.get_source_segment(source, node)
    return segments


class CalibrationPortPinTests(unittest.TestCase):
    def test_calibration_stop_and_its_dependencies_equal_r11_bbfccb70a(self):
        for path, pins in PINS.items():
            segments = top_level_segments(path)
            for name, expected in pins.items():
                with self.subTest(path=path, name=name):
                    self.assertIn(name, segments)
                    actual = hashlib.sha256(segments[name].encode()).hexdigest()
                    self.assertEqual(actual, expected, f'{path}:{name} drifted from r11 {R11_COMMIT}; re-port it')

    def test_pin_covers_every_module_name_calibration_stop_reaches(self):
        segments = top_level_segments('joulewise/align/apple/v4_cadence.py')
        pinned = set(PINS['joulewise/align/apple/v4_cadence.py'])
        reached, frontier = set(), ['calibration_stop']
        while frontier:
            name = frontier.pop()
            if name in reached:
                continue
            reached.add(name)
            for node in ast.walk(ast.parse(segments[name])):
                if isinstance(node, ast.Name) and node.id in segments and node.id not in reached:
                    frontier.append(node.id)
        self.assertEqual(reached - pinned, set())

    def test_engine_uses_this_predicate(self):
        from joulewise.align.apple import v4_cadence
        from joulewise.align.v4_analysis import engine
        self.assertIs(engine.calibration_stop, v4_cadence.calibration_stop)
        self.assertIs(engine.slot_of, v4_cadence.slot_of)
        self.assertIs(engine.STRUCTURAL_BARS, v4_cadence.STRUCTURAL_BARS)


if __name__ == '__main__':
    unittest.main()
