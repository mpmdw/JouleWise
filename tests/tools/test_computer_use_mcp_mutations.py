"""Offline guard-removal regression tests; mutate Python source in memory only.

The original review published mutant descriptions, not its runner. These 22
review mutants reproduce those descriptions on the current implementation.
The pre-input armed mutant removes the now-redundant post-discovery checks
together; leaving any of them in place would still correctly refuse input.
Swift guard source checks in the functional suite are not native execution.
"""

import io
import types
import unittest
from unittest.mock import patch

from tests.tools import test_computer_use_mcp as functional


def replace(source, old, new, *, occurrence=None):
    if old not in source:
        raise AssertionError(f"Stale mutation anchor: {old!r}")
    if occurrence is None:
        return source.replace(old, new)
    parts = source.split(old)
    if len(parts) <= occurrence:
        raise AssertionError(f"Missing mutation occurrence {occurrence}: {old!r}")
    return old.join(parts[:occurrence]) + new + old.join(parts[occurrence:])


# Tuples are (description, old source, replacement, optional 1-based occurrence).
REVIEW_MUTANTS = [
    ("night label refusal removed", 'if fields[2].startswith("com.joulewise.night"):', 'if False:'),
    ("night prefix narrowed to exact", 'fields[2].startswith("com.joulewise.night")',
     'fields[2] == "com.joulewise.night"'),
    ("future epoch check removed", 'if epoch > self.clock():', 'if False:'),
    ("invalid marker fails open",
     'raise ToolError("Cannot verify armed-night state: invalid armed_until epoch") from exc', 'continue'),
    ("unreadable marker fails open",
     'raise ToolError("Cannot verify armed-night state: unreadable armed_until marker") from exc', 'continue'),
    ("malformed domain header fails open",
     'raise ToolError(f"Cannot verify armed-night state: malformed launchctl domain {domain}")', 'pass'),
    ("malformed service row fails open",
     'raise ToolError(f"Cannot verify armed-night state: malformed launchctl row in {domain}")', 'pass'),
    ("first app gate removed", 'frontmost = self.check_app(name, arguments)', 'frontmost = None', 1),
    ("pre-input app recheck removed", 'frontmost = self.check_app(name, arguments)', 'pass', 2),
    ("post-discovery armed rechecks removed", 'self.check_armed()', 'pass'),
    ("pre-capture armed recheck removed", '            before_capture()', '            pass'),
    ("wait and frontmost skip armed gate", 'if name != "permissions_status":',
     'if name not in ("permissions_status", "wait", "frontmost_app"):'),
    ("dry run made live", 'if self.env.get("JW_CU_DRY_RUN") not in (None, "", "0"):', 'if False:'),
    ("before log dropped", 'self.log(call_id, "before", name, arguments, frontmost, "pending")', 'pass'),
    ("execute log dropped", 'self.log(call_id, "execute", name, arguments, frontmost, "pending")', 'pass'),
    ("append replaced by truncate", 'os.O_CREAT | os.O_APPEND', 'os.O_CREAT | os.O_TRUNC'),
    ("rate five becomes six", 'len(self.input_times) >= 5', 'len(self.input_times) >= 6'),
    ("rate limiter removed", 'self.rate_limit()', 'pass'),
    ("Screen Recording gate removed", 'if permissions.get("screen_recording") is not True:', 'if False:'),
    ("Accessibility gate removed", 'if permissions.get("accessibility") is not True:', 'if False:'),
    ("open target gate removed", 'if arguments["name"] not in apps:', 'if False:'),
    ("redaction disabled", 'if name == "type_text" and self.env.get("JW_CU_REDACT") == "1":', 'if False:'),
]

ROUND_TWO_MUTANTS = [
    ("GUI label query replaced with caller list",
     '["/bin/launchctl", "print", domain]', '["/bin/launchctl", "list"]'),
    ("unreadable domain fails open",
     'raise ToolError(f"Cannot verify armed-night state: unreadable launchctl domain {domain}") from exc',
     'continue'),
    ("system domain ignored", '(f"gui/{os.getuid()}", "system")', '(f"gui/{os.getuid()}",)'),
    ("permissions preflight compiles while armed", 'except ArmedError as exc:', 'except ArmedError as exc:\n'
     '                self.backend.helper("permissions_status")'),
    ("ambiguous dry-run values made live", 'self.env.get("JW_CU_DRY_RUN") not in (None, "", "0")',
     'self.env.get("JW_CU_DRY_RUN") == "1"'),
    ("click owner check removed", 'self.check_click_target(arguments, frontmost)', 'pass'),
    ("key combo block removed", 'raise ToolError("App-switching and launcher key combos are blocked")', 'pass'),
    ("catch-all narrowed", 'except Exception as exc:\n            result = text_result',
     'except (ToolError, OSError, ValueError) as exc:\n            result = text_result'),
    ("remote armed opt-out made default", 'if not config.get("respect_remote_armed", True):',
     'if not config.get("respect_remote_armed", False):'),
]


class SafetyMutationTests(unittest.TestCase):
    def test_review_and_round_two_mutants_are_caught(self):
        source = (functional.cu.HERE / "server.py").read_text()
        for spec in REVIEW_MUTANTS + ROUND_TWO_MUTANTS:
            name, old, new, *occurrence = spec
            with self.subTest(mutant=name):
                if name == "post-discovery armed rechecks removed":
                    # Preserve the first operational gate and permissions-status
                    # gate, but remove all later input rechecks as one defect.
                    mutated = source
                    for nth in (5, 4, 2):
                        mutated = replace(mutated, old, new, occurrence=nth)
                else:
                    mutated = replace(source, old, new, occurrence=occurrence[0] if occurrence else None)
                module = types.ModuleType("synthetic_mutant")
                module.__file__ = str(functional.cu.HERE / "server.py")
                exec(compile(mutated, module.__file__, "exec"), module.__dict__)
                with patch.object(functional, "cu", module):
                    suite = unittest.defaultTestLoader.loadTestsFromTestCase(functional.ComputerUseTests)
                    result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
                self.assertFalse(result.wasSuccessful(), f"Safety mutant survived: {name}")
                self.assertEqual(result.testsRun, len(unittest.defaultTestLoader.getTestCaseNames(
                    functional.ComputerUseTests)))


if __name__ == "__main__":
    unittest.main()
