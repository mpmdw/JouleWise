#!/usr/bin/env python3
"""Hand-written fake from field names, not recorded from a real service.

SOL_CLOUD_TEST_SCENARIO selects JSON; SOL_CLOUD_TEST_CALLS records argv JSONL.
Responses are indexed independently per subcommand; the last repeats. Processes
never sleep and always exit on their own immediately.
"""
import json
import os
from pathlib import Path
import sys

scenario_path = Path(os.environ['SOL_CLOUD_TEST_SCENARIO'])
scenario = json.loads(scenario_path.read_text())
calls = Path(os.environ['SOL_CLOUD_TEST_CALLS'])
previous = [json.loads(line) for line in calls.read_text().splitlines()] if calls.exists() else []
argv = sys.argv[1:]
prompt = sys.stdin.read() if argv[-1] == '--prompt-stdin' else None
with calls.open('a') as stream:
    stream.write(json.dumps({'argv': argv, 'prompt': prompt}) + '\n')
command = argv[1]
index = sum(call['argv'][1] == command for call in previous)
responses = scenario[command]
response = responses[min(index, len(responses)-1)]
for key, stream in [('stdout', sys.stdout), ('stderr', sys.stderr)]:
    if key + '_file' in response:
        stream.buffer.write((scenario_path.parent / response[key + '_file']).read_bytes())
    else:
        stream.write(response.get(key, ''))
sys.exit(response.get('rc', 0))
