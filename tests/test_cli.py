import io
import unittest
from contextlib import redirect_stdout

from joulewise.cli import main


class CliTests(unittest.TestCase):
    def test_validate_config_command(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["validate-config", "configs/examples/mock_local.json"])
        self.assertEqual(exit_code, 0)
        self.assertIn("valid config", stdout.getvalue())
        self.assertIn("runtime=mock", stdout.getvalue())

    def test_print_config_schema_command(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["print-config-schema"])
        self.assertEqual(exit_code, 0)
        self.assertIn("JouleWise BenchmarkConfig", stdout.getvalue())

    def test_print_output_schema_command(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["print-output-schema"])
        self.assertEqual(exit_code, 0)
        self.assertIn("JouleWise SummaryMetrics", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
