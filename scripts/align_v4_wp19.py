#!/usr/bin/env python3
"""WP19 tokenizer-only X/Y all-turn render and R1 X-G identity receipt.

No model load or generation. --tokenizer must be an explicit local directory;
transformers uses local_files_only=True. Task tools are the simulated SHADE
tools specified in the contrast config. Run on the lead's authorized desk.
"""
import argparse
import importlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.align.apple.v4_registration import wp19_identity, digest


def render_fixture(fixture, tokenizer, endpoint, task, *, condition, seed):
    from joulewise.align.interfaces import ChatMessage, ChatResult
    from joulewise.align.apple.endpoint import parse_completion
    task.reset(seed)
    history = [ChatMessage('system', task.system_prompt(condition)), ChatMessage('user', task.user_prompt())]
    tools = task.tool_schemas()
    prompts = []
    for turn in fixture['turns']:
        prompt = endpoint._render_prompt(history, tools)
        prompts.append(list(tokenizer.encode(prompt, add_special_tokens=False)))
        # Render the next turn from the recorded completion, never a new sample.
        output_ids = list(turn['output_token_ids'])
        eos = getattr(tokenizer, 'eos_token_ids', None) or [getattr(tokenizer, 'eos_token_id', None)]
        eos = {eos} if isinstance(eos, int) else set(eos)
        while output_ids and output_ids[-1] in eos:
            output_ids.pop()
        # Only terminal EOS is removed. Think/tool markers are history bytes.
        raw = tokenizer.decode(output_ids, skip_special_tokens=False)
        visible, reasoning, calls, flags = parse_completion(raw, model_family=endpoint.model_family,
            tools=tools, reasoning_open=prompt.rstrip().endswith('<think>'))
        result = ChatResult(visible, reasoning, calls, len(prompts[-1]), 0,
                           len(turn['output_token_ids']), 0, 0, None, 0, raw_usage={'raw_text': raw})
        history.append(endpoint.assistant_history_message(result))
        for call in calls:
            try:
                output = task.call_tool(call.name, call.arguments_json)
                if not isinstance(output, str):
                    output = json.dumps(output, sort_keys=True)
            except Exception as exc:
                output = json.dumps({'error': f'{type(exc).__name__}:{exc}'})
            history.append(ChatMessage('tool', output, name=call.name, tool_call_id=call.call_id))
    return prompts


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=ROOT)
    p.add_argument('--tokenizer', type=Path, required=True)
    p.add_argument('--x-g-turns', type=Path, required=True, help='explicit R1 X-G align_turns.jsonl')
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args(argv)
    if not args.tokenizer.is_dir():
        raise ValueError('--tokenizer must be a local directory (no downloads)')
    from transformers import AutoTokenizer
    from joulewise.schemas import BenchmarkConfig
    from joulewise.align.apple.workload import EpisodeSpec
    from joulewise.align.apple.endpoint import MlxEndpoint
    from joulewise.clock import FakeClock
    from scripts import align_v4_kit as kit
    tokenizer = AutoTokenizer.from_pretrained(str(args.tokenizer), local_files_only=True, trust_remote_code=False)
    plan = json.loads((args.root/kit.KIT/'collection_plan.json').read_bytes())
    fixtures, rendered, sources = {}, {}, {}
    for arm in ('X', 'Y'):
        raw = (args.root/kit.WP18_FIXTURES[arm]).read_bytes()
        fixtures[arm] = json.loads(raw)
        kit.check_wp18_turn_contents(fixtures[arm], arm)
        sources[str(kit.WP18_FIXTURES[arm])] = digest(raw)
        member = next(m for m in plan['members'] if m['role'] == arm+'-G')
        cfg_raw = (args.root/member['config_path']).read_bytes()
        sources[member['config_path']] = digest(cfg_raw)
        cfg = BenchmarkConfig.from_mapping(json.loads(cfg_raw))
        spec = EpisodeSpec.from_text(cfg.workload_profile.prompt_text)
        module, factory = spec.task_factory.split(':')
        task = getattr(importlib.import_module(module), factory)(**spec.task_kwargs)
        endpoint = MlxEndpoint(SimpleNamespace(_tokenizer=tokenizer), cfg, FakeClock(), episode_domain='wp19',
                               enable_thinking=spec.enable_thinking, assistant_history=spec.assistant_history,
                               chat_template_kwargs=spec.chat_template_kwargs)
        rendered[arm] = render_fixture(fixtures[arm], tokenizer, endpoint, task,
                                      condition=spec.condition, seed=spec.seed)
    live = args.x_g_turns.read_bytes()
    rows = [json.loads(line) for line in live.splitlines() if line.strip()]
    from joulewise.align.apple.sampling import turn_seed
    for i, row in enumerate(rows):
        if row.get('turn') != i or row['generation']['sampler']['per_turn_seed'] != turn_seed(7655467588542005630, i):
            raise ValueError('live X-G turn/seed binding failed')
    turns = [{'turn': r['turn'], **{k: r['generation'][k] for k in ('prompt_token_ids', 'output_token_ids')}} for r in rows]
    result = wp19_identity(fixtures, rendered, turns, live_source_sha256=digest(live))
    result['source_sha256'] = sources
    result['tokenizer_files_sha256'] = {name: digest((args.tokenizer/name).read_bytes())
        for name in ('tokenizer.json', 'tokenizer_config.json')}
    with args.output.open('x') as f:
        f.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
