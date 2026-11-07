# Block-5 analysis — shard 0

- Date: 2026-11-06
- Data: test/synthetic only
- Python: `python3` (`Python 3.12.13`)
- Command pattern: `timeout 1200 $PY -B -m unittest MODULE 2>&1 | tail -150 > /tmp/jws/MODULE.log`

## Module results

tests.b5_analysis.test_result_equivalence: <Ran 90 tests in 34.951s> <OK (skipped=4)>

tests.b5_analysis.test_release_equality: <Ran 10 tests in 3.898s> <OK (skipped=1)>

tests.b5_analysis.test_speed_plan: <Ran 6 tests in 78.390s> <OK>

tests.b5_analysis.test_pack_parallel: <Ran 6 tests in 89.399s> <OK>

tests.b5_analysis.test_reported_parallel: <Ran 3 tests in 12.850s> <OK>

tests.b5_analysis.test_sensitivity_parallel: <Ran 1 test in 8.530s> <OK>

tests.b5_analysis.test_producer_parallel: <Ran 4 tests in 6.558s> <OK>

tests.b5_analysis.test_speed_quantile_memo: <Ran 4 tests in 8.994s> <OK>

tests.b5_analysis.test_postrelease_step4: <Ran 5 tests in 0.041s> <OK>

tests.b5_analysis.test_postrelease_bracket_copies: <Ran 2 tests in 0.005s> <OK>

tests.b5_analysis.test_postrelease_bracket_snapshot: <Ran 5 tests in 0.197s> <OK>

tests.b5_analysis.test_postrelease_g9: <Ran 2 tests in 0.007s> <OK>

tests.b5_analysis.test_postrelease_step11_codes: <Ran 7 tests in 0.114s> <OK>

## Modules not run

None.

Elapsed runner time: 274 seconds.
