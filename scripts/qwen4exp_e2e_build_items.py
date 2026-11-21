#!/usr/bin/env python3
"""Build the pinned item set for the qwen4_exp end-to-end validation harness.

Writes ``configs/qwen4_exp_port/e2e_items.json``. Every external item records
its source URL (commit-pinned where the host supports it), the sha256 of the
source file as fetched, the selection rule, and the sha256 of the item bytes
that the harness feeds the model. The harness re-verifies the item hashes on
every load, so an edited item cannot silently change a result.

Sources (all fetched 2026-11-05):
  * GSM8K test split, openai/grade-school-math (MIT), commit b0bb162.
  * IFEval input_data.jsonl, google-research/google-research (Apache-2.0),
    commit 26d8ccd.
  * Project Gutenberg plain-text ebooks #1342, #5, #1228, #23839 (public
    domain in the USA). Gutenberg files are not commit-versioned, so the
    file sha256 at fetch time is recorded and the excerpt is located by
    anchor text, not byte offset.
  * PEP 20, python/peps (public domain), commit b990d05.

Authored items (coherence questions, tool-call cases) are original to this
repository.

Offline use: ``--source-dir DIR`` must contain the fetched files under the
names in SOURCES. ``--fetch DIR`` downloads them first (network, data only;
nothing fetched is executed).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = REPO_ROOT / "configs" / "qwen4_exp_port" / "e2e_items.json"
ITEMS_SCHEMA = "qwen4exp-e2e-items/v1"
FETCHED_ON = "2026-11-05"

SOURCES = {
    "gsm8k_test.jsonl": {
        "url": "https://raw.githubusercontent.com/openai/grade-school-math/"
               "b0bb162abedc65e1fdd8e93ed090fd7598ee68bc/grade_school_math/data/test.jsonl",
        "sha256": "3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14",
        "license": "MIT (openai/grade-school-math)",
    },
    "ifeval_input.jsonl": {
        "url": "https://raw.githubusercontent.com/google-research/google-research/"
               "26d8ccdab6fec61b5c83ad6327ea8bda9e580288/instruction_following_eval/data/input_data.jsonl",
        "sha256": "67ffeee0fcb87c317c5b08a2de85557b4a7e96ada6178aa645b4954fe4b53d49",
        "license": "Apache-2.0 (google-research/google-research)",
    },
    "pg1342.txt": {"url": "https://www.gutenberg.org/cache/epub/1342/pg1342.txt",
                   "sha256": None, "license": "Public domain in the USA (Project Gutenberg #1342)"},
    "pg5.txt": {"url": "https://www.gutenberg.org/cache/epub/5/pg5.txt",
                "sha256": None, "license": "Public domain in the USA (Project Gutenberg #5)"},
    "pg1228.txt": {"url": "https://www.gutenberg.org/cache/epub/1228/pg1228.txt",
                   "sha256": None, "license": "Public domain in the USA (Project Gutenberg #1228)"},
    "pg23839.txt": {"url": "https://www.gutenberg.org/cache/epub/23839/pg23839.txt",
                    "sha256": None, "license": "Public domain in the USA (Project Gutenberg #23839)"},
    "pep-0020.rst": {
        "url": "https://raw.githubusercontent.com/python/peps/"
               "b990d0599141b030e68d1a1bb91aac9981d1fd56/peps/pep-0020.rst",
        "sha256": "742999637cc96eef52e8148fdf65a6065a0953daee92bb48b8c739efcf6def07",
        "license": "Public domain (PEP 20 copyright section)",
    },
}

# Excerpts: (id, source file, start anchor, end anchor (inclusive), purpose).
EXCERPTS = (
    ("pp_ch1", "pg1342.txt", "It is a truth universally acknowledged",
     "its solace was visiting and news.", "English literary prose, about 1k tokens"),
    ("pp_ch1_3_long", "pg1342.txt", "It is a truth universally acknowledged",
     "I quite detest the man.”", "long English prose past the 2048-token QSA indexer budget"),
    ("us_constitution", "pg5.txt", "We the people of the United States",
     "he shall be chosen.", "legal English"),
    ("origin_intro", "pg1228.txt", "When on board H.M.S.",
     "some brief\nextracts from my manuscripts.", "scientific prose"),
    ("lunyu_xueer", "pg23839.txt", "1. 子曰：「學而時習之",
     "患不知人也。」", "classical Chinese, multi-byte tokens"),
    ("pep20_zen", "pep-0020.rst", "    Beautiful is better than ugly.",
     "let's do more of those!", "structured technical text"),
)
SHUFFLE_SEED = 20261105

GSM8K_COUNT = 30
IFEVAL_COUNT = 25
# Instruction types the harness verifies exactly as IFEval's strict checker
# does (language detection excepted, see the harness). Types needing nltk
# sentence splitting or langdetect are excluded from selection.
IFEVAL_SUPPORTED = frozenset({
    "punctuation:no_comma", "length_constraints:number_words",
    "keywords:forbidden_words", "detectable_format:number_highlighted_sections",
    "keywords:frequency", "combination:repeat_prompt", "startend:quotation",
    "change_case:english_lowercase", "keywords:existence", "detectable_format:title",
    "keywords:letter_frequency", "detectable_format:number_bullet_lists",
    "detectable_content:number_placeholders", "length_constraints:number_paragraphs",
    "startend:end_checker", "detectable_content:postscript",
    "change_case:english_capital", "combination:two_responses",
    "detectable_format:json_format", "detectable_format:multiple_sections",
    "length_constraints:nth_paragraph_first_word",
    "detectable_format:constrained_response",
})


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for name, spec in SOURCES.items():
        target = directory / name
        if target.exists():
            continue
        request = urllib.request.Request(spec["url"], headers={"User-Agent": "joulewise-items/1"})
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310 - pinned https URLs
            target.write_bytes(response.read())


def load_sources(directory: Path) -> dict[str, dict]:
    loaded = {}
    for name, spec in SOURCES.items():
        data = (directory / name).read_bytes()
        digest = sha256_bytes(data)
        if spec["sha256"] is not None and digest != spec["sha256"]:
            raise SystemExit(f"{name}: sha256 {digest} != pinned {spec['sha256']}")
        loaded[name] = {"bytes": data, "sha256": digest, **{k: v for k, v in spec.items() if k != "sha256"}}
    return loaded


def excerpt(text: str, start: str, end: str) -> str:
    i = text.index(start)
    j = text.index(end, i) + len(end)
    return text[i:j]


def shuffled_words(text: str, seed: int) -> str:
    words = text.split()
    random.Random(seed).shuffle(words)
    lines, line = [], []
    for word in words:
        line.append(word)
        if len(line) == 12:
            lines.append(" ".join(line))
            line = []
    if line:
        lines.append(" ".join(line))
    return "\n".join(lines)


def build_nll(sources: dict) -> list[dict]:
    items = []
    for item_id, name, start, end, purpose in EXCERPTS:
        raw = sources[name]["bytes"].decode("utf-8")
        text = raw.replace("\r\n", "\n")
        body = excerpt(text, start, end)
        items.append({
            "id": item_id, "kind": "natural", "purpose": purpose, "text": body,
            "sha256": sha256_text(body), "chars": len(body),
            "source": {"file": name, "url": sources[name]["url"],
                       "file_sha256_at_fetch": sources[name]["sha256"], "fetched": FETCHED_ON,
                       "license": sources[name]["license"], "normalization": "crlf_to_lf",
                       "start_anchor": start, "end_anchor": end},
        })
    base = next(item for item in items if item["id"] == "pp_ch1")
    control = shuffled_words(base["text"], SHUFFLE_SEED)
    items.append({
        "id": "pp_ch1_shuffled", "kind": "control", "purpose":
        "word-shuffled pp_ch1; same unigrams, no syntax: must score far worse than pp_ch1",
        "text": control, "sha256": sha256_text(control), "chars": len(control),
        "source": {"derived_from": "pp_ch1", "derivation": "str.split, random.Random(seed).shuffle, 12 words per line",
                   "seed": SHUFFLE_SEED},
    })
    return items


def build_gsm8k(sources: dict) -> list[dict]:
    lines = sources["gsm8k_test.jsonl"]["bytes"].decode("utf-8").splitlines()
    items = []
    for index, line in enumerate(lines[:GSM8K_COUNT]):
        row = json.loads(line)
        final = row["answer"].rsplit("####", 1)[1].strip().replace(",", "")
        items.append({
            "id": f"gsm8k_test_{index:04d}", "question": row["question"], "answer": final,
            "solution": row["answer"], "line_index": index, "line_sha256": sha256_text(line),
            "sha256": sha256_text(row["question"] + "\x00" + final),
        })
    return items


def build_ifeval(sources: dict) -> list[dict]:
    lines = sources["ifeval_input.jsonl"]["bytes"].decode("utf-8").splitlines()
    items = []
    for index, line in enumerate(lines):
        row = json.loads(line)
        if not set(row["instruction_id_list"]) <= IFEVAL_SUPPORTED:
            continue
        kwargs = [{k: v for k, v in entry.items() if v is not None} for entry in row["kwargs"]]
        items.append({
            "id": f"ifeval_{row['key']}", "key": row["key"], "prompt": row["prompt"],
            "instruction_id_list": row["instruction_id_list"], "kwargs": kwargs,
            "line_index": index, "line_sha256": sha256_text(line),
            "sha256": sha256_text(json.dumps([row["prompt"], row["instruction_id_list"], kwargs],
                                             sort_keys=True, ensure_ascii=False)),
        })
        if len(items) == IFEVAL_COUNT:
            break
    return items


def _tool(name, description, properties, required):
    return {"type": "function", "function": {
        "name": name, "description": description,
        "parameters": {"type": "object", "properties": properties, "required": required}}}


TOOLS = {
    "get_weather": _tool("get_weather", "Get the current weather for a city.", {
        "city": {"type": "string", "description": "City name, e.g. Paris"},
        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "description": "Temperature unit"},
    }, ["city"]),
    "convert_currency": _tool("convert_currency", "Convert an amount between two currencies.", {
        "amount": {"type": "number", "description": "Amount to convert"},
        "from_currency": {"type": "string", "description": "ISO 4217 code of the source currency"},
        "to_currency": {"type": "string", "description": "ISO 4217 code of the target currency"},
    }, ["amount", "from_currency", "to_currency"]),
    "search_flights": _tool("search_flights", "Search for flights between two places on a date.", {
        "origin": {"type": "string", "description": "Departure city or airport code"},
        "destination": {"type": "string", "description": "Arrival city or airport code"},
        "date": {"type": "string", "description": "Departure date, YYYY-MM-DD"},
        "passengers": {"type": "integer", "description": "Number of passengers (default 1)"},
    }, ["origin", "destination", "date"]),
    "calculate_bmi": _tool("calculate_bmi", "Calculate body-mass index.", {
        "weight_kg": {"type": "number", "description": "Weight in kilograms"},
        "height_m": {"type": "number", "description": "Height in metres"},
    }, ["weight_kg", "height_m"]),
    "send_email": _tool("send_email", "Send an email.", {
        "to": {"type": "string", "description": "Recipient address"},
        "subject": {"type": "string", "description": "Subject line"},
        "body": {"type": "string", "description": "Message body"},
    }, ["to", "subject", "body"]),
    "get_stock_price": _tool("get_stock_price", "Get the latest price for a stock ticker.", {
        "ticker": {"type": "string", "description": "Exchange ticker symbol, e.g. AAPL"},
    }, ["ticker"]),
    "create_calendar_event": _tool("create_calendar_event", "Create a calendar event.", {
        "title": {"type": "string", "description": "Event title"},
        "start_time": {"type": "string", "description": "ISO 8601 start time, e.g. 2026-01-31T09:30"},
        "duration_minutes": {"type": "integer", "description": "Duration in minutes"},
        "attendees": {"type": "array", "items": {"type": "string"}, "description": "Attendee email addresses"},
    }, ["title", "start_time", "duration_minutes"]),
    "set_thermostat": _tool("set_thermostat", "Set the thermostat.", {
        "temperature": {"type": "number", "description": "Target temperature in degrees"},
        "mode": {"type": "string", "enum": ["heat", "cool", "auto"], "description": "Operating mode"},
    }, ["temperature", "mode"]),
}


def _call(name, **args):
    return {"name": name, "args": args}


def build_toolcall() -> list[dict]:
    """BFCL-style categories: simple, multiple, parallel, parallel_multiple,
    irrelevance, and round trips through a tool response. ``args`` maps each
    parameter to its accepted values; OMIT means the parameter may be absent."""
    omit = "<omitted>"
    cases = [
        ("simple_weather", "simple", ["get_weather"], None,
         "What's the weather like in Paris right now? Use Celsius.",
         [_call("get_weather", city=["Paris", "Paris, France"], unit=["celsius"])], None),
        ("simple_bmi", "simple", ["calculate_bmi"], None,
         "Calculate the BMI for someone who weighs 70 kg and is 1.75 m tall.",
         [_call("calculate_bmi", weight_kg=[70], height_m=[1.75])], None),
        ("simple_stock", "simple", ["get_stock_price"], None,
         "What is Apple's current stock price?",
         [_call("get_stock_price", ticker=["AAPL"])], None),
        ("multiple_currency", "multiple",
         ["get_weather", "convert_currency", "search_flights", "get_stock_price"], None,
         "Convert 250 US dollars to euros.",
         [_call("convert_currency", amount=[250], from_currency=["USD"], to_currency=["EUR"])], None),
        ("multiple_flights", "multiple",
         ["get_weather", "convert_currency", "search_flights", "get_stock_price"], None,
         "Find flights from San Francisco to Tokyo on 2026-12-20 for 2 passengers.",
         [_call("search_flights", origin=["San Francisco", "SFO"],
                destination=["Tokyo", "NRT", "HND", "TYO"], date=["2026-12-20"], passengers=[2])], None),
        ("multiple_thermostat", "multiple", ["send_email", "create_calendar_event", "set_thermostat"], None,
         "Set the thermostat to 21 degrees in heat mode.",
         [_call("set_thermostat", temperature=[21], mode=["heat"])], None),
        ("parallel_weather", "parallel", ["get_weather"], None,
         "What's the weather in London and in Berlin? Use celsius for both.",
         [_call("get_weather", city=["London", "London, UK"], unit=["celsius"]),
          _call("get_weather", city=["Berlin", "Berlin, Germany"], unit=["celsius"])], None),
        ("parallel_multiple_finance", "parallel_multiple", ["get_stock_price", "convert_currency"], None,
         "Get the stock prices of NVDA and MSFT, and convert 100 GBP to USD.",
         [_call("get_stock_price", ticker=["NVDA"]), _call("get_stock_price", ticker=["MSFT"]),
          _call("convert_currency", amount=[100], from_currency=["GBP"], to_currency=["USD"])], None),
        ("array_calendar", "simple", ["create_calendar_event"], None,
         "Schedule a 45-minute meeting titled 'Design review' starting 2026-11-12T15:00 "
         "with alice@example.com and bob@example.com.",
         [_call("create_calendar_event", title=["Design review"],
                start_time=["2026-11-12T15:00", "2026-11-12T15:00:00"], duration_minutes=[45],
                attendees=[{"unordered": ["alice@example.com", "bob@example.com"]}])], None),
        ("string_email", "simple", ["send_email"], None,
         "Email carol@example.com with the subject 'Lunch' and the body "
         "'Are you free for lunch tomorrow at noon?'",
         [_call("send_email", to=["carol@example.com"], subject=["Lunch"],
                body=["Are you free for lunch tomorrow at noon?"])], None),
        ("system_weather_fahrenheit", "multiple", ["search_flights", "get_weather"],
         "You are a concise travel assistant.",
         "Is it going to be cold in Oslo? Give me the temperature in fahrenheit.",
         [_call("get_weather", city=["Oslo", "Oslo, Norway"], unit=["fahrenheit"])], None),
        ("float_thermostat", "simple", ["set_thermostat"], None,
         "Make it 68.5 degrees and switch to cooling.",
         [_call("set_thermostat", temperature=[68.5], mode=["cool"])], None),
        ("irrelevance_author", "irrelevance", ["get_weather", "get_stock_price"], None,
         "Who wrote the novel Pride and Prejudice?", [], {"must_contain": ["Austen"]}),
        ("irrelevance_octopus", "irrelevance", ["calculate_bmi"], None,
         "Tell me one fun fact about octopuses in a single sentence.", [], {"must_contain": ["octop"]}),
    ]
    items = []
    for item_id, category, tool_names, system, user, expected, extra in cases:
        messages = ([{"role": "system", "content": system}] if system else []) + [
            {"role": "user", "content": user}]
        item = {"id": item_id, "category": category, "tools": [TOOLS[n] for n in tool_names],
                "messages": messages, "expected_calls": expected, "omit_sentinel": omit}
        if extra:
            item.update(extra)
        items.append(item)
    # Round trips: the call and tool response go back through the template;
    # the final answer must use the result and make no further call.
    trips = [
        ("roundtrip_weather", ["get_weather"], "What's the weather in Paris in celsius?",
         {"name": "get_weather", "arguments": {"city": "Paris", "unit": "celsius"}},
         '{"city": "Paris", "temperature": 18, "unit": "celsius", "condition": "light rain"}',
         ["18", "rain"]),
        ("roundtrip_currency", ["convert_currency"], "Convert 250 USD to EUR.",
         {"name": "convert_currency", "arguments": {"amount": 250, "from_currency": "USD", "to_currency": "EUR"}},
         '{"amount": 250, "from": "USD", "to": "EUR", "result": 231.75}',
         ["231.75"]),
    ]
    for item_id, tool_names, user, call, response, must in trips:
        items.append({
            "id": item_id, "category": "round_trip", "tools": [TOOLS[n] for n in tool_names],
            "messages": [
                {"role": "user", "content": user},
                {"role": "assistant", "content": "", "tool_calls": [{"type": "function", "function": call}]},
                {"role": "tool", "content": response},
            ],
            "expected_calls": [], "must_contain": must, "omit_sentinel": omit,
        })
    for item in items:
        item["sha256"] = sha256_text(json.dumps(
            {k: v for k, v in item.items() if k != "sha256"}, sort_keys=True, ensure_ascii=False))
    return items


def build_coherence() -> list[dict]:
    """Short factual and format checks (original). ``thinking`` items run with
    the template's thinking enabled at reasoning_effort=low."""
    cases = [
        ("capital_fr", False, [{"role": "user", "content": "What is the capital of France? Answer with one word."}],
         {"regex_all": [r"\bParis\b"]}, 64),
        ("arith_mult", False, [{"role": "user", "content": "What is 17 multiplied by 23? Reply with just the number."}],
         {"regex_all": [r"\b391\b"]}, 64),
        ("chem_gold", False, [{"role": "user", "content": "What is the chemical symbol for gold? Reply with just the symbol."}],
         {"regex_all": [r"\bAu\b"]}, 64),
        ("author_pp", False, [{"role": "user", "content": "Who wrote the novel 'Pride and Prejudice'? Reply with just the author's name."}],
         {"regex_all": [r"Austen"]}, 64),
        ("zh_capital", False, [{"role": "user", "content": "中国的首都是哪座城市？请只回答城市名。"}],
         {"regex_all": ["北京"]}, 64),
        ("translate_fr", False, [{"role": "user", "content": "Translate 'thank you very much' into French. Reply with only the translation."}],
         {"regex_all": [r"(?i)merci beaucoup"]}, 64),
        ("code_square", False, [{"role": "user", "content": "Write a Python function named square that returns the square of its argument x. Output only the code."}],
         {"regex_all": [r"def\s+square\s*\(\s*x", r"return\s+(x\s*\*\*\s*2|x\s*\*\s*x)"]}, 160),
        ("multi_turn_name", False, [
            {"role": "user", "content": "My name is Ada."},
            {"role": "assistant", "content": "Nice to meet you, Ada!"},
            {"role": "user", "content": "What is my name? Reply with just the name."}],
         {"regex_all": [r"\bAda\b"]}, 64),
        ("paragraph_water", False, [{"role": "user", "content": "Write one paragraph of about 80 words explaining the water cycle."}],
         {"min_keywords": [2, ["evaporat", "condens", "precipit", "runoff", "transpir"]],
          "words_between": [40, 200], "distinct_trigram_min": 0.7, "max_word_run": 3}, 320),
        ("thinking_sum", True, [{"role": "user", "content": "What is 12 + 30? Answer with just the number."}],
         {"regex_all": [r"\b42\b"], "reasoning_closed": True}, 1536),
        ("thinking_capital_jp", True, [{"role": "user", "content": "What is the capital of Japan? Answer with one word."}],
         {"regex_all": [r"Tokyo"], "reasoning_closed": True}, 1536),
    ]
    items = []
    for item_id, thinking, messages, check, max_tokens in cases:
        item = {"id": item_id, "thinking": thinking, "messages": messages, "check": check,
                "max_tokens": max_tokens}
        item["sha256"] = sha256_text(json.dumps(
            {k: v for k, v in item.items() if k != "sha256"}, sort_keys=True, ensure_ascii=False))
        items.append(item)
    return items


def build(source_dir: Path) -> dict:
    sources = load_sources(source_dir)
    nll = build_nll(sources)
    return {
        "schema": ITEMS_SCHEMA,
        "built_by": "scripts/qwen4exp_e2e_build_items.py",
        "sources": {name: {"url": s["url"], "sha256_at_fetch": s["sha256"], "license": s["license"],
                           "fetched": FETCHED_ON} for name, s in sources.items()},
        "selection": {
            "gsm8k": f"first {GSM8K_COUNT} lines of the test split, file order",
            "ifeval": f"first {IFEVAL_COUNT} rows (file order) whose instruction ids are all verifiable "
                      "without nltk or langdetect",
            "nll": "anchored excerpts, CRLF normalized to LF; plus one seeded word-shuffle control",
        },
        "nll": nll,
        "consistency": [
            {"id": "consistency_short", "messages": [{"role": "user", "content": "List three primary colours, one per line."}],
             "max_tokens": 32},
            {"id": "consistency_code", "messages": [{"role": "user", "content": "Write a Python function that reverses a string."}],
             "max_tokens": 48},
            {"id": "consistency_long_qsa", "context_from": "pp_ch1_3_long",
             "messages": [{"role": "user", "content": "{context}\n\nIn one sentence, what does Mrs. Bennet want her husband to do?"}],
             "max_tokens": 48},
        ],
        "coherence": build_coherence(),
        "math": build_gsm8k(sources),
        "ifeval": build_ifeval(sources),
        "toolcall": build_toolcall(),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--fetch", action="store_true", help="download missing sources into --source-dir first")
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    args = parser.parse_args(argv)
    if args.fetch:
        fetch(args.source_dir)
    items = build(args.source_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(items, indent=1, ensure_ascii=False, sort_keys=False) + "\n"
    args.out.write_text(data, encoding="utf-8")
    print(f"wrote {args.out} sha256={sha256_text(data)} "
          f"nll={len(items['nll'])} math={len(items['math'])} ifeval={len(items['ifeval'])} "
          f"toolcall={len(items['toolcall'])} coherence={len(items['coherence'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
