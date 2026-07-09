"""Deterministic jw_mixed_v1 suite content generators.

The text-path budget is the adapter-realized count:
``len(tokenizer.encode(prompt_text, add_special_tokens=True))``.  BOS, when
the tokenizer adds one, is inside the requested prompt budget.  D-046 sentinel
items are the deliberate exception: they are delivered ids-native with
``add_special_tokens=False`` and record that delivery in the annotations
sidecar rather than in schema-forbidden manifest fields.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, TypeAlias

from joulewise.provenance import prompt_token_ids_sha256, sha256_hex
from joulewise.suite import ORDER_POLICY_MANIFEST, SUITE_SCHEMA_VERSION, SuiteManifest

GENERATOR_VERSION = "1.0.0"
DRBG_VERSION = "sha256-ctr-v1"
SYNTHETIC_PROMPT_SEED = "JouleWise synthetic prompt token sequence."


class TokenizerProtocol(Protocol):
    """Minimal tokenizer surface required by jw_mixed_v1."""

    vocab_size: int

    def encode(self, text: str, add_special_tokens: bool) -> list[int]:
        """Return token ids for text."""

    def decode(self, ids: list[int]) -> str:
        """Return decoded text for token ids."""


class ShapeError(ValueError):
    """Raised when a tokenizer cannot realize an exact prompt budget."""


class Drbg:
    """SHA-256 counter-mode DRBG with exact-uniform rejection sampling."""

    def __init__(self, seed_bytes: bytes) -> None:
        self.key = bytes(seed_bytes)
        self.ctr = 0

    def _block(self) -> bytes:
        self.ctr += 1
        return hashlib.sha256(self.key + self.ctr.to_bytes(8, "big")).digest()

    def u64(self) -> int:
        return int.from_bytes(self._block()[:8], "big")

    def below(self, n: int) -> int:
        if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
            raise ValueError("n must be a positive integer")
        lim = (1 << 64) - ((1 << 64) % n)
        while True:
            x = self.u64()
            if x < lim:
                return x % n

    def choice(self, seq: Sequence[Any]) -> Any:
        if not seq:
            raise ValueError("cannot choose from an empty sequence")
        return seq[self.below(len(seq))]


_BANKS: dict[str, Any] = {
    "personas": [
        "a first-year nursing student",
        "a city council member",
        "a visiting exchange student",
        "a new town clerk",
        "a maintenance dispatcher",
        "a library volunteer",
        "a field supervisor",
        "a harbor coordinator",
    ],
    "domains": [
        "harbor pilot crews",
        "greenhouse irrigation schedules",
        "library lending desks",
        "transit repair logs",
        "storm shelter rosters",
        "market stall ledgers",
        "regional survey teams",
        "dock inspection routes",
    ],
    "adjectives": [
        "seasonal",
        "quiet",
        "rotating",
        "local",
        "temporary",
        "shared",
        "careful",
        "daily",
    ],
    "verbs": [
        "tracks",
        "reviews",
        "balances",
        "updates",
        "routes",
        "checks",
        "compares",
        "records",
    ],
    "objects": [
        "crew notes",
        "supply counts",
        "route cards",
        "permit slips",
        "shift totals",
        "repair flags",
        "ledger rows",
        "intake forms",
    ],
    "constraints": [
        "avoid jargon",
        "give two examples",
        "use a numbered list",
        "include one risk to watch",
        "keep the tone practical",
        "name the tradeoffs",
    ],
    "imports": ["collections", "datetime", "itertools", "json", "math", "pathlib"],
    "syllables": [
        "lan",
        "ver",
        "tor",
        "min",
        "sai",
        "kel",
        "dor",
        "wen",
        "pak",
        "luma",
        "nori",
        "tavi",
    ],
    "field_types": ["string", "int", "date", "enum", "bool", "nullable"],
    "profiles": [
        ("en-Latin", "ltr", ["the", "and", "near", "with"], list("lanvermistop")),
        ("ru-Cyrillic", "ltr", ["и", "на", "по", "для"], list("абвгдежзиклмнопрсту")),
        ("zh-CJK", "ltr", ["和", "在", "向", "与"], list("的一是在不了有和人这中大为上个国我以要他")),
        ("hi-Devanagari", "ltr", ["और", "में", "है", "से"], list("कखगचजटनपमयरलवसहािीुेो")),
        ("ar-Arabic", "rtl", ["و", "في", "من", "على"], list("ابتثجحخدذرزسشصضطظعغفقكلمنهوي")),
        ("el-Greek", "ltr", ["και", "σε", "με", "για"], list("αβγδεζηθικλμνξοπρστυφχψω")),
    ],
}


def _bank_hash() -> str:
    payload = json.dumps(_BANKS, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


BANK_HASH = _bank_hash()
_EXPECTED_BANK_HASH = "9bda5d6bef86ce02d1970eb0e246b86ea0029075b98a2b72049e95d991ad06c7"


def _assert_bank_hash() -> None:
    actual = _bank_hash()
    if actual != _EXPECTED_BANK_HASH:
        raise AssertionError(
            "jw_mixed_v1 word bank hash changed; bump generator version and update "
            f"BANK_HASH assertion ({actual})"
        )
    if BANK_HASH != actual:
        raise AssertionError(f"jw_mixed_v1 BANK_HASH constant is stale ({BANK_HASH} != {actual})")


TokenizerManifestRow: TypeAlias = Mapping[str, str] | tuple[str, str]


def _canonical_tokenizer_row(row: TokenizerManifestRow) -> dict[str, str]:
    if isinstance(row, Mapping):
        name = row.get("filename")
        status = row.get("status")
        digest = row.get("sha256")
    else:
        name, digest = row
        status = None
    if not name:
        raise ValueError("tokenizer_manifest rows require filename")
    if status is None:
        status = "present"
    if status == "absent":
        if digest is not None:
            raise ValueError("tokenizer_manifest absent rows must not include sha256")
        return {"filename": name, "status": "absent"}
    if status != "present":
        raise ValueError("tokenizer_manifest status must be present or absent")
    if digest is None:
        raise ValueError("tokenizer_manifest present rows require sha256")
    if len(digest) != 64 or any(ch not in "0123456789abcdefABCDEF" for ch in digest):
        raise ValueError("tokenizer_manifest sha256 values must be 64 hex characters")
    return {"filename": name, "sha256": digest.lower()}


def canonical_tokenizer_manifest(files: Sequence[TokenizerManifestRow]) -> list[dict[str, str]]:
    rows = sorted(
        (_canonical_tokenizer_row(row) for row in files),
        key=lambda row: row["filename"],
    )
    if not rows:
        raise ValueError("tokenizer_manifest must contain at least one file row")
    if not any("sha256" in row for row in rows):
        raise ValueError("tokenizer_manifest must contain at least one present file row")
    return rows


def tokenizer_manifest_sha256(files: Sequence[TokenizerManifestRow]) -> str:
    rows = canonical_tokenizer_manifest(files)
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def tokenizer_id_from_manifest(files: Sequence[TokenizerManifestRow]) -> str:
    """Return the B7 canonical tokenizer id from per-file sha256 entries."""

    return "tokfiles_" + tokenizer_manifest_sha256(files)


FAKE_TOKENIZER_MANIFEST: tuple[tuple[str, str], ...] = (
    ("fake-tokenizer.json", "0" * 64),
    ("fake-merges.txt", "1" * 64),
)
FAKE_TOKENIZER_ID = tokenizer_id_from_manifest(FAKE_TOKENIZER_MANIFEST)


def tokenizer_id_for(
    tokenizer_manifest: Sequence[TokenizerManifestRow] | None = None,
    tokenizer_id: str | None = None,
) -> str:
    if tokenizer_manifest is None:
        raise ValueError("tokenizer_manifest is required for suite builds")
    derived = tokenizer_id_from_manifest(tokenizer_manifest)
    if tokenizer_id is not None and tokenizer_id != derived:
        raise ValueError("tokenizer_id does not match tokenizer_manifest")
    return derived


def item_seed(master_seed: str, category: str, item_index: int) -> int:
    payload = f"jw_mixed_v1.seed\0{master_seed}\0{category}\0{item_index}"
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def item_id_for(
    generator_id: str,
    seed: int,
    prompt_budget: int,
    tokenizer_id: str,
    generator_version: str = GENERATOR_VERSION,
) -> str:
    payload = (
        "jw_mixed_v1.item\0"
        + generator_id
        + "\0"
        + generator_version
        + "\0"
        + str(seed)
        + "\0"
        + str(prompt_budget)
        + "\0"
        + tokenizer_id
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _encode(tokenizer: TokenizerProtocol, text: str, add_special_tokens: bool) -> list[int]:
    return list(tokenizer.encode(text, add_special_tokens=add_special_tokens))


def _special_ids(tokenizer: TokenizerProtocol) -> set[int]:
    result: set[int] = set()
    for attr in ("special_token_ids", "all_special_ids"):
        value = getattr(tokenizer, attr, None)
        if isinstance(value, Iterable) and not isinstance(value, str):
            for item in value:
                if isinstance(item, int) and not isinstance(item, bool):
                    result.add(item)
    for attr in ("bos_token_id", "eos_token_id", "pad_token_id", "unk_token_id"):
        value = getattr(tokenizer, attr, None)
        if isinstance(value, int) and not isinstance(value, bool):
            result.add(value)
    value = getattr(tokenizer, "eos_token_ids", None)
    if isinstance(value, int) and not isinstance(value, bool):
        result.add(value)
    elif isinstance(value, Iterable) and not isinstance(value, str):
        for item in value:
            if isinstance(item, int) and not isinstance(item, bool):
                result.add(item)
    return result


def _topic(drbg: Drbg) -> str:
    return (
        f"the {drbg.choice(_BANKS['adjectives'])} "
        f"{drbg.choice(_BANKS['domains'])}"
    )


def _name(drbg: Drbg) -> str:
    return (drbg.choice(_BANKS["syllables"]) + drbg.choice(_BANKS["syllables"])).title()


def _snake(drbg: Drbg) -> str:
    parts = [drbg.choice(_BANKS["syllables"]) for _ in range(2 + drbg.below(2))]
    return "_".join(parts)


def _prose_sentence(drbg: Drbg, subject: str | None = None, *, numeric: bool = False) -> str:
    actor = subject or drbg.choice(["the team", "the clerk", "the route lead", "the group"])
    detail = (
        f" after {2 + drbg.below(8)} checks"
        if numeric
        else f" while the plan remains easy to audit"
    )
    return (
        f"{actor.capitalize()} {drbg.choice(_BANKS['verbs'])} "
        f"{drbg.choice(_BANKS['objects'])} for {_topic(drbg)}{detail}."
    )


PROSE_ATOMS = [
    " in most cases",
    " over time",
    " for the local team",
    " when records change",
    " with care",
    " clearly",
    " steadily",
    " a",
    " e",
    " i",
    " o",
    " u",
    " x",
    " 0",
]
CODE_ATOMS = [
    " # note: keep the branch simple",
    " # handles empty input",
    " # local check",
    " value",
    " data",
    " x",
    " y",
    " 0",
]


@dataclass(frozen=True)
class ExactPrompt:
    text: str
    token_ids: list[int]
    elastic_fill_tokens: int
    coarse_units: int


def realize_exact_prompt(
    tokenizer: TokenizerProtocol,
    *,
    target_tokens: int,
    prologue: str,
    unit_factory: Any,
    atom_ladder: Sequence[str],
    epilogue: str = "",
    add_special_tokens: bool = True,
    coarse_headroom: int = 24,
    backtracking_depth: int = 8,
    max_units: int = 200,
) -> ExactPrompt:
    """Grow coarse units, then full-re-encode greedy-fill to exact shape."""

    units: list[str] = []
    atoms: list[str] = []

    def assemble() -> str:
        hard_boundary = "\n" if epilogue else ""
        return prologue + "".join(units) + "".join(atoms) + hard_boundary + epilogue

    def count(text: str) -> int:
        return len(_encode(tokenizer, text, add_special_tokens=add_special_tokens))

    base_text = assemble()
    base_count = count(base_text)
    if base_count > target_tokens:
        raise ShapeError(f"fixed prologue/epilogue exceed target: {base_count}>{target_tokens}")

    for _ in range(max_units):
        if count(assemble()) > target_tokens - coarse_headroom:
            break
        unit = unit_factory()
        units.append(unit)
        if count(assemble()) > target_tokens - coarse_headroom:
            units.pop()
            break

    current_text = assemble()
    current_count = count(current_text)
    if current_count > target_tokens:
        raise ShapeError("coarse stage exceeded target")

    accepted_indices: list[int] = []
    next_index_stack = [0]
    consecutive_pops = 0
    attempts = 0
    max_attempts = max(1000, target_tokens * max(32, len(atom_ladder) * 4))
    while current_count != target_tokens:
        attempts += 1
        if attempts > max_attempts:
            raise ShapeError("exact-shape fill exceeded attempt bound")
        progressed = False
        start = next_index_stack[-1]
        for idx in range(start, len(atom_ladder)):
            atom = atom_ladder[idx]
            atoms.append(atom)
            candidate_text = assemble()
            candidate_count = count(candidate_text)
            atoms.pop()
            if current_count < candidate_count <= target_tokens:
                next_index_stack[-1] = idx + 1
                atoms.append(atom)
                accepted_indices.append(idx)
                next_index_stack.append(0)
                current_text = candidate_text
                current_count = candidate_count
                consecutive_pops = 0
                progressed = True
                break
        if progressed:
            continue
        if not atoms or consecutive_pops >= backtracking_depth:
            raise ShapeError(f"cannot realize exact prompt budget {target_tokens}")
        atoms.pop()
        accepted_indices.pop()
        next_index_stack.pop()
        current_text = assemble()
        current_count = count(current_text)
        consecutive_pops += 1

    final_ids = _encode(tokenizer, current_text, add_special_tokens=add_special_tokens)
    if len(final_ids) != target_tokens:
        raise ShapeError("final verification failed")
    filled_ids = len(_encode(tokenizer, "".join(atoms), add_special_tokens=False))
    return ExactPrompt(
        text=current_text,
        token_ids=final_ids,
        elastic_fill_tokens=filled_ids,
        coarse_units=len(units),
    )


@dataclass(frozen=True)
class GeneratedContent:
    generator_id: str
    item_id: str
    seed: int
    prompt_text: str | None
    prompt_token_ids: list[int]
    annotations: dict[str, Any]


def _base_annotations(
    generator_id: str,
    seed: int,
    tokenizer_id: str,
    prompt: ExactPrompt | None,
    *,
    add_special_tokens: bool,
    parameters: dict[str, Any],
) -> dict[str, Any]:
    out = {
        "generator_id": generator_id,
        "generator_version": GENERATOR_VERSION,
        "seed": seed,
        "tokenizer_id": tokenizer_id,
        "drbg": DRBG_VERSION,
        "bank_hash": BANK_HASH,
        "token_accounting": (
            "encode_add_special_true" if add_special_tokens else "encode_add_special_false"
        ),
        "parameters": parameters,
    }
    if prompt is not None:
        out.update(
            {
                "realized_token_count": len(prompt.token_ids),
                "token_ids_sha256": prompt_token_ids_sha256(prompt.token_ids),
                "text_sha256": sha256_hex(prompt.text),
                "elastic_fill_tokens": prompt.elastic_fill_tokens,
                "coarse_units": prompt.coarse_units,
            }
        )
    return out


def generate_chat(
    seed: int,
    tokenizer: TokenizerProtocol,
    *,
    prompt_budget: int = 512,
    tokenizer_id: str,
    add_special_tokens: bool = True,
    body_only: bool = False,
) -> GeneratedContent:
    drbg = Drbg(seed.to_bytes(8, "big"))
    n_constraints = 3 + drbg.below(3)
    persona = drbg.choice(_BANKS["personas"])
    topic = _topic(drbg)
    constraints = [drbg.choice(_BANKS["constraints"]) for _ in range(n_constraints)]
    prologue = "" if body_only else "You are a helpful assistant. Use the context below.\n"
    epilogue = (
        ""
        if body_only
        else (
            "Explain "
            + topic
            + " to "
            + persona
            + ", "
            + ", ".join(constraints)
            + "."
        )
    )

    def unit() -> str:
        return _prose_sentence(drbg) + " "

    prompt = realize_exact_prompt(
        tokenizer,
        target_tokens=prompt_budget,
        prologue=prologue,
        unit_factory=unit,
        atom_ladder=PROSE_ATOMS,
        epilogue=epilogue,
        add_special_tokens=add_special_tokens,
    )
    params = {
        "persona": {"source": "drbg", "range": [0, len(_BANKS["personas"]) - 1], "value": persona},
        "topic": {"source": "drbg", "grammar": "adjective+domain", "value": topic},
        "n_constraints": {"source": "drbg", "range": [3, 5], "value": n_constraints},
        "coarse_headroom": {"source": "pinned", "value": 24},
    }
    ann = _base_annotations(
        "jw.chat", seed, tokenizer_id, prompt, add_special_tokens=add_special_tokens, parameters=params
    )
    return GeneratedContent(
        "jw.chat",
        item_id_for("jw.chat", seed, prompt_budget, tokenizer_id),
        seed,
        prompt.text,
        prompt.token_ids,
        ann,
    )


def generate_code(
    seed: int,
    tokenizer: TokenizerProtocol,
    *,
    prompt_budget: int = 512,
    tokenizer_id: str,
    add_special_tokens: bool = True,
    body_only: bool = False,
) -> GeneratedContent:
    drbg = Drbg(seed.to_bytes(8, "big"))
    n_imports = 2 + drbg.below(2)
    n_complete_functions = 2 + drbg.below(2)
    imports = [drbg.choice(_BANKS["imports"]) for _ in range(n_imports)]
    module = "route_manifest"
    prologue = "" if body_only else "Complete the final function in this module. Return only code.\n"
    header = "".join(f"import {name}\n" for name in imports)
    header += f'"""{module} helpers for synthetic records."""\n\n'
    complete = []
    for _ in range(n_complete_functions):
        fn = _snake(drbg)
        complete.append(
            f"def {fn}(records):\n"
            f"    total = 0\n"
            f"    for row in records:\n"
            f"        total += int(row.get('count', 0))\n"
            f"    return total\n\n"
        )
    stub_name = _snake(drbg)
    epilogue = (
        ""
        if body_only
        else (
            f"def {stub_name}(records, key):\n"
            f"    \"\"\"Merge rows into a dictionary of lists keyed by key.\"\"\"\n"
            f"    # TODO: implement\n"
        )
    )
    prologue += header + "".join(complete)

    def unit() -> str:
        var = _snake(drbg)
        return f"# note: {var} keeps local state before the final stub\n"

    prompt = realize_exact_prompt(
        tokenizer,
        target_tokens=prompt_budget,
        prologue=prologue,
        unit_factory=unit,
        atom_ladder=CODE_ATOMS,
        epilogue=epilogue,
        add_special_tokens=add_special_tokens,
    )
    params = {
        "n_imports": {"source": "drbg", "range": [2, 3], "value": n_imports},
        "n_complete_functions": {
            "source": "drbg",
            "range": [2, 3],
            "value": n_complete_functions,
        },
        "indent": {"source": "pinned", "value": "    "},
        "coarse_headroom": {"source": "pinned", "value": 24},
    }
    ann = _base_annotations(
        "jw.code", seed, tokenizer_id, prompt, add_special_tokens=add_special_tokens, parameters=params
    )
    return GeneratedContent(
        "jw.code",
        item_id_for("jw.code", seed, prompt_budget, tokenizer_id),
        seed,
        prompt.text,
        prompt.token_ids,
        ann,
    )


def generate_summ(
    seed: int,
    tokenizer: TokenizerProtocol,
    *,
    prompt_budget: int = 512,
    tokenizer_id: str,
) -> GeneratedContent:
    drbg = Drbg(seed.to_bytes(8, "big"))
    n_entities = 3 + drbg.below(3)
    facts_per_entity = 6 + drbg.below(5)
    n_needles = 1 + drbg.below(2)
    entities = [_name(drbg) for _ in range(n_entities)]
    needles: list[dict[str, Any]] = []
    prologue = "Read the following report.\n"
    epilogue = "Summarize the report above in about 120 words, covering each named party."
    required_units: list[str] = []
    for needle_index in range(n_needles):
        entity = drbg.choice(entities)
        number = 10 + drbg.below(80)
        needle = f"NEEDLE-{1000 + drbg.below(9000)}"
        sentence = (
            f"{entity} reported {number} route notes during the {drbg.choice(_BANKS['adjectives'])} "
            f"review, and the same party later checked {drbg.choice(_BANKS['objects'])}. "
            f"The unique reference code was {needle}. "
        )
        position = drbg.below(len(required_units) + 1)
        required_units.insert(position, sentence)
        needles.append({"needle": needle, "entity": entity, "position": position})
    for needle in needles:
        needle_text = str(needle["needle"])
        needle["position"] = next(
            index for index, unit_text in enumerate(required_units) if needle_text in unit_text
        )

    def unit() -> str:
        entity = drbg.choice(entities)
        number = 10 + drbg.below(80)
        return (
            f"{entity} reported {number} route notes during the {drbg.choice(_BANKS['adjectives'])} "
            f"review, and the same party later checked {drbg.choice(_BANKS['objects'])}."
        ) + " "

    prompt = realize_exact_prompt(
        tokenizer,
        target_tokens=prompt_budget,
        prologue=prologue + "".join(required_units),
        unit_factory=unit,
        atom_ladder=PROSE_ATOMS,
        epilogue=epilogue,
        add_special_tokens=True,
    )
    realized_needles = sum(1 for needle in needles if needle["needle"] in prompt.text)
    if realized_needles != n_needles:
        raise ShapeError(
            f"needle realization failed: requested {n_needles}, realized {realized_needles}"
        )
    params = {
        "n_entities": {"source": "drbg", "range": [3, 5], "value": n_entities},
        "facts_per_entity_draw": {
            "source": "drbg",
            "range": [6, 10],
            "value": facts_per_entity,
            "semantics": "legacy draw recorded for replay; filler continues until token budget",
        },
        "n_needles": {"source": "drbg", "range": [1, 2], "value": n_needles},
        "coarse_headroom": {"source": "pinned", "value": 24},
    }
    ann = _base_annotations(
        "jw.summ", seed, tokenizer_id, prompt, add_special_tokens=True, parameters=params
    )
    ann["needle_positions"] = needles
    ann["requested_needles"] = n_needles
    ann["realized_needles"] = realized_needles
    return GeneratedContent(
        "jw.summ",
        item_id_for("jw.summ", seed, prompt_budget, tokenizer_id),
        seed,
        prompt.text,
        prompt.token_ids,
        ann,
    )


def _apply_step(value: int, op: str, operand: int) -> int:
    if op == "add":
        return value + operand
    if op == "sub":
        return value - operand
    if op == "mul":
        return value * operand
    if op == "int_div":
        if value % operand != 0:
            raise ValueError("non-divisible int_div")
        return value // operand
    if op == "percent_increase":
        out = value * (100 + operand)
        if out % 100 != 0:
            raise ValueError("non-integer percent")
        return out // 100
    raise ValueError(op)


def _arithmetic_trace(drbg: Drbg, n_steps: int) -> tuple[int, int, list[dict[str, int | str]]]:
    cap = 10000
    current = 10 + drbg.below(71)
    final_answer = current
    reverse_steps: list[dict[str, int | str]] = []
    for _ in range(n_steps):
        add_k = 2 + drbg.below(17)
        div_d = 2 + drbg.below(5)
        mul_m = 2 + drbg.below(5)
        pct = drbg.choice([10, 20, 25, 50])
        candidates: list[tuple[str, int, int]] = []
        if current > add_k + 1:
            candidates.append(("add", add_k, current - add_k))
        if current + add_k <= cap:
            candidates.append(("sub", add_k, current + add_k))
        if current * div_d <= cap:
            candidates.append(("int_div", div_d, current * div_d))
        if current % mul_m == 0 and current // mul_m > 0:
            candidates.append(("mul", mul_m, current // mul_m))
        den = 100 + pct
        if (current * 100) % den == 0:
            prev = (current * 100) // den
            if prev > 0:
                candidates.append(("percent_increase", pct, prev))
        op, operand, prev = drbg.choice(candidates)
        reverse_steps.append({"before": prev, "op": op, "operand": operand, "after": current})
        current = prev
    steps = list(reversed(reverse_steps))
    value = current
    for step in steps:
        value = _apply_step(value, str(step["op"]), int(step["operand"]))
        if value != step["after"] or not isinstance(value, int):
            raise AssertionError("reasoning trace verification failed")
    if value != final_answer:
        raise AssertionError("final answer verification failed")
    return current, final_answer, steps


def _logic_puzzle(drbg: Drbg) -> tuple[str, dict[str, Any]]:
    names: list[str] = []
    while len(names) < 5:
        name = _name(drbg)
        if name not in names:
            names.append(name)
    order = list(names)
    # Deterministic shuffle through DRBG.
    for i in range(len(order) - 1, 0, -1):
        j = drbg.below(i + 1)
        order[i], order[j] = order[j], order[i]
    constraints = []
    for left, right in zip(order, order[1:]):
        constraints.append((left, right))
    constraints.append((order[0], order[2]))
    valid = []
    for perm in itertools.permutations(names):
        if all(perm.index(a) < perm.index(b) for a, b in constraints):
            valid.append(perm)
    if len(valid) != 1:
        raise AssertionError("logic puzzle must have unique solution")
    text = "Five delivery leads arrived in a fixed order. "
    text += " ".join(f"{a} arrived before {b}." for a, b in constraints)
    text += " Who arrived third?"
    return text, {"constraints": constraints, "solution_order": list(valid[0]), "answer": valid[0][2]}


def generate_reason(
    seed: int,
    tokenizer: TokenizerProtocol,
    *,
    prompt_budget: int = 512,
    tokenizer_id: str,
) -> GeneratedContent:
    drbg = Drbg(seed.to_bytes(8, "big"))
    n_steps = 4 + drbg.below(3)
    n_distractors = 1 + drbg.below(3)
    logic_variant = drbg.below(4) == 0
    distractors = [
        f"The side ledger mentioned {20 + drbg.below(70)} labels, but those labels are unrelated."
        for _ in range(n_distractors)
    ]
    if logic_variant:
        puzzle_text, truth = _logic_puzzle(drbg)
        body_units = [puzzle_text + " "] + [d + " " for d in distractors]
        answer = truth["answer"]
        trace: dict[str, Any] = {"reason_type": "logic", **truth}
    else:
        initial, answer, steps = _arithmetic_trace(drbg, n_steps)
        units = [f"The starting count is {initial} crates. "]
        labels = {
            "add": "adds",
            "sub": "removes",
            "mul": "multiplies the count by",
            "int_div": "packs the count evenly into groups of",
            "percent_increase": "raises the count by",
        }
        for step in steps:
            op = str(step["op"])
            operand = int(step["operand"])
            suffix = " percent" if op == "percent_increase" else ""
            units.append(f"Then the clerk {labels[op]} {operand}{suffix}. ")
        body_units = units + [d + " " for d in distractors]
        trace = {
            "reason_type": "arithmetic",
            "initial": initial,
            "answer": answer,
            "steps": steps,
            "integer_intermediates": [step["after"] for step in steps],
            "verified_answer": _evaluate_trace(initial, steps),
        }
    prologue = "Solve the following reasoning task.\n"
    epilogue = "Work through this step by step, then state the final number or name."
    unit_iter = iter(body_units)

    def unit() -> str:
        try:
            return next(unit_iter)
        except StopIteration:
            return _prose_sentence(drbg, "the scene") + " "

    prompt = realize_exact_prompt(
        tokenizer,
        target_tokens=prompt_budget,
        prologue=prologue,
        unit_factory=unit,
        atom_ladder=PROSE_ATOMS,
        epilogue=epilogue,
        add_special_tokens=True,
    )
    params = {
        "n_steps": {"source": "drbg", "range": [4, 6], "value": n_steps},
        "n_distractors": {"source": "drbg", "range": [1, 3], "value": n_distractors},
        "logic_variant": {"source": "drbg", "rate": 0.25, "value": logic_variant},
        "answer_seed_range": {"source": "implementation", "value": [10, 80]},
        "intermediate_cap": {"source": "pinned", "value": 10000},
        "coarse_headroom": {"source": "pinned", "value": 24},
    }
    ann = _base_annotations(
        "jw.reason", seed, tokenizer_id, prompt, add_special_tokens=True, parameters=params
    )
    ann["ground_truth"] = {"answer": answer}
    ann["reasoning_trace"] = trace
    ann["distractors"] = distractors
    return GeneratedContent(
        "jw.reason",
        item_id_for("jw.reason", seed, prompt_budget, tokenizer_id),
        seed,
        prompt.text,
        prompt.token_ids,
        ann,
    )


def _evaluate_trace(initial: int, steps: Sequence[dict[str, Any]]) -> int:
    value = initial
    for step in steps:
        value = _apply_step(value, str(step["op"]), int(step["operand"]))
    return value


def generate_json(
    seed: int,
    tokenizer: TokenizerProtocol,
    *,
    prompt_budget: int = 512,
    tokenizer_id: str,
) -> GeneratedContent:
    drbg = Drbg(seed.to_bytes(8, "big"))
    n_fields = 6 + drbg.below(4)
    n_distractors = 2 + drbg.below(3)
    n_red_herrings = 1 + drbg.below(3)
    fields = [_snake(drbg) for _ in range(n_fields)]
    truth: dict[str, Any] = {}
    schema: dict[str, str] = {}
    for field in fields:
        kind = drbg.choice(_BANKS["field_types"])
        schema[field] = kind
        if kind == "string":
            truth[field] = _name(drbg)
        elif kind == "int":
            truth[field] = 100 + drbg.below(900)
        elif kind == "date":
            truth[field] = f"203{drbg.below(5)}-0{1 + drbg.below(9)}-{10 + drbg.below(18)}"
        elif kind == "enum":
            truth[field] = drbg.choice(["A", "B", "C", "D"])
        elif kind == "bool":
            truth[field] = bool(drbg.below(2))
        else:
            truth[field] = None
    prologue = (
        "Extract the following fields from the record below. Output only JSON matching the schema.\n"
        + json.dumps(schema, sort_keys=True)
        + "\n"
    )
    epilogue = "Output only the JSON object."
    record_lines = []
    for key, value in truth.items():
        record_lines.append(f"[2031-04-12 08:31] {key}={value}; source=synthetic\n")
    for _ in range(n_distractors):
        record_lines.append(f"near_miss={1000 + drbg.below(8000)} should be ignored\n")
    for _ in range(n_red_herrings):
        record_lines.append(f"extra_{_snake(drbg)}: {drbg.choice(_BANKS['objects'])}\n")
    line_iter = iter(record_lines)

    def unit() -> str:
        try:
            return next(line_iter)
        except StopIteration:
            return f"notes: {_prose_sentence(drbg)} "

    prompt = realize_exact_prompt(
        tokenizer,
        target_tokens=prompt_budget,
        prologue=prologue,
        unit_factory=unit,
        atom_ladder=PROSE_ATOMS,
        epilogue=epilogue,
        add_special_tokens=True,
    )
    params = {
        "n_fields": {"source": "drbg", "range": [6, 9], "value": n_fields},
        "n_distractors": {"source": "drbg", "range": [2, 4], "value": n_distractors},
        "n_red_herrings": {"source": "drbg", "range": [1, 3], "value": n_red_herrings},
        "record_styles": {"source": "pinned", "value": ["log", "freetext", "kv"]},
        "coarse_headroom": {"source": "pinned", "value": 24},
    }
    ann = _base_annotations(
        "jw.json", seed, tokenizer_id, prompt, add_special_tokens=True, parameters=params
    )
    ann["ground_truth"] = truth
    ann["schema"] = schema
    return GeneratedContent(
        "jw.json",
        item_id_for("jw.json", seed, prompt_budget, tokenizer_id),
        seed,
        prompt.text,
        prompt.token_ids,
        ann,
    )


def _script_word(drbg: Drbg, chars: Sequence[str]) -> str:
    return "".join(drbg.choice(chars) for _ in range(2 + drbg.below(5)))


def _clone_drbg(drbg: Drbg) -> Drbg:
    clone = Drbg(drbg.key)
    clone.ctr = drbg.ctr
    return clone


def _ascii_tail_candidates(tokenizer: TokenizerProtocol, max_tokens: int) -> list[str]:
    candidates = ["", " 0", " 1", " 2", " 0 0", " 1 1", " 0 0 0", " 1 1 1"]
    out: list[str] = []
    for tail in candidates:
        if tail and len(_encode(tokenizer, tail, add_special_tokens=False)) > max_tokens:
            continue
        out.append(tail)
    return out


def realize_exact_prompt_with_final_ascii_tail(
    tokenizer: TokenizerProtocol,
    *,
    target_tokens: int,
    prologue: str,
    unit_factory_for: Any,
    native_atom_ladder_for: Any,
    drbg_state: Drbg,
    epilogue: str = "",
    add_special_tokens: bool = True,
    ascii_tail_max: int = 3,
) -> tuple[ExactPrompt, int]:
    """Realize exact text with native atoms first and only a final ASCII tail."""

    errors: list[Exception] = []
    for tail in _ascii_tail_candidates(tokenizer, ascii_tail_max):
        for native_target in range(target_tokens, max(0, target_tokens - ascii_tail_max) - 1, -1):
            attempt_drbg = _clone_drbg(drbg_state)
            try:
                native = realize_exact_prompt(
                    tokenizer,
                    target_tokens=native_target,
                    prologue=prologue,
                    unit_factory=unit_factory_for(attempt_drbg),
                    atom_ladder=native_atom_ladder_for(attempt_drbg),
                    epilogue=epilogue,
                    add_special_tokens=add_special_tokens,
                )
            except ShapeError as exc:
                errors.append(exc)
                continue
            if not tail:
                if native_target == target_tokens:
                    return native, 0
                continue
            final_text = native.text + tail
            final_ids = _encode(tokenizer, final_text, add_special_tokens=add_special_tokens)
            tail_tokens = len(final_ids) - len(native.token_ids)
            if len(final_ids) == target_tokens and 0 < tail_tokens <= ascii_tail_max:
                return (
                    ExactPrompt(
                        text=final_text,
                        token_ids=final_ids,
                        elastic_fill_tokens=native.elastic_fill_tokens + tail_tokens,
                        coarse_units=native.coarse_units,
                    ),
                    tail_tokens,
                )
    if errors:
        raise ShapeError(f"cannot realize exact prompt budget {target_tokens} with final ASCII tail")
    raise ShapeError(f"cannot realize exact prompt budget {target_tokens}")


def generate_multiling(
    seed: int,
    tokenizer: TokenizerProtocol,
    *,
    prompt_budget: int = 512,
    tokenizer_id: str,
    profile_index: int | None = None,
    add_special_tokens: bool = True,
    body_only: bool = False,
) -> GeneratedContent:
    drbg = Drbg(seed.to_bytes(8, "big"))
    profiles = _BANKS["profiles"]
    if profile_index is None:
        profile_index = drbg.below(len(profiles))
        profile_source = "drbg"
    else:
        profile_index %= len(profiles)
        profile_source = "pinned"
    language, direction, function_words, chars = profiles[profile_index]
    prologue = "" if body_only else "Continue the following text in the same language:\n"
    epilogue = ""
    punct = "。" if "CJK" in language else ("؟" if "Arabic" in language else ".")

    def sentence_from(local_drbg: Drbg) -> str:
        words = [local_drbg.choice(function_words)]
        words.extend(_script_word(local_drbg, chars) for _ in range(3 + local_drbg.below(8)))
        sep = "" if "CJK" in language else " "
        return sep.join(words) + punct + " "

    def unit_factory_for(local_drbg: Drbg) -> Any:
        return lambda: sentence_from(local_drbg)

    def native_atom_ladder_for(local_drbg: Drbg) -> list[str]:
        return [
            local_drbg.choice(function_words),
            chars[0],
            chars[-1],
            chars[0] * 3,
            chars[-1] * 3,
            punct,
            punct * 3,
            punct + (" " if "CJK" not in language else ""),
            sentence_from(local_drbg),
        ]

    prompt, ascii_tail_tokens = realize_exact_prompt_with_final_ascii_tail(
        tokenizer,
        target_tokens=prompt_budget,
        prologue=prologue,
        unit_factory_for=unit_factory_for,
        native_atom_ladder_for=native_atom_ladder_for,
        drbg_state=drbg,
        epilogue=epilogue,
        add_special_tokens=add_special_tokens,
    )
    params = {
        "language": {"source": profile_source, "range": [0, len(profiles) - 1], "value": language},
        "direction": {"source": "pinned", "value": direction},
        "ascii_tail_max": {"source": "pinned", "value": 3},
        "coarse_headroom": {"source": "pinned", "value": 24},
    }
    ann = _base_annotations(
        "jw.multiling",
        seed,
        tokenizer_id,
        prompt,
        add_special_tokens=add_special_tokens,
        parameters=params,
    )
    ann["script_profile"] = language
    ann["direction"] = direction
    ann["ascii_tail_tokens"] = ascii_tail_tokens
    ann["chars_per_token"] = len(prompt.text) / max(1, len(prompt.token_ids))
    return GeneratedContent(
        "jw.multiling",
        item_id_for("jw.multiling", seed, prompt_budget, tokenizer_id),
        seed,
        prompt.text,
        prompt.token_ids,
        ann,
    )


GENERATOR_FUNCS = {
    "jw.chat": generate_chat,
    "jw.code": generate_code,
    "jw.summ": generate_summ,
    "jw.reason": generate_reason,
    "jw.json": generate_json,
    "jw.multiling": generate_multiling,
}


def repeated_seed_ids(tokenizer: TokenizerProtocol, target_tokens: int) -> list[int]:
    seed = _encode(tokenizer, SYNTHETIC_PROMPT_SEED, add_special_tokens=False)
    if not seed:
        seed = _encode(tokenizer, "JouleWise", add_special_tokens=False)
    if not seed:
        seed = [0]
    repeated: list[int] = []
    while len(repeated) < target_tokens:
        repeated.extend(seed)
    return repeated[:target_tokens]


def random_token_ids(tokenizer: TokenizerProtocol, seed: int, target_tokens: int) -> list[int]:
    vocab_size = getattr(tokenizer, "vocab_size", None)
    if isinstance(vocab_size, bool) or not isinstance(vocab_size, int) or vocab_size <= 0:
        raise ValueError("tokenizer.vocab_size must be a positive integer")
    excluded = _special_ids(tokenizer)
    allowed = []
    for token_id in range(vocab_size):
        if token_id in excluded:
            continue
        if tokenizer.decode([token_id]) == "":
            continue
        allowed.append(token_id)
    if not allowed:
        raise ValueError("random-token sentinel has no allowed token ids")
    drbg = Drbg(seed.to_bytes(8, "big"))
    return [allowed[drbg.below(len(allowed))] for _ in range(target_tokens)]


def sentinel_content(
    condition_id: str,
    seed: int,
    tokenizer: TokenizerProtocol,
    *,
    prompt_budget: int = 512,
    tokenizer_id: str,
) -> GeneratedContent:
    if condition_id == "repeated_seed":
        ids = repeated_seed_ids(tokenizer, prompt_budget)
        generator_id = "jw.sentinel.repeated_seed"
        ann = _sentinel_ann(generator_id, seed, tokenizer_id, ids, condition_id)
        return GeneratedContent(
            generator_id,
            item_id_for(generator_id, seed, prompt_budget, tokenizer_id),
            seed,
            None,
            ids,
            ann,
        )
    if condition_id == "random_token":
        ids = random_token_ids(tokenizer, seed, prompt_budget)
        generator_id = "jw.sentinel.random_token"
        ann = _sentinel_ann(generator_id, seed, tokenizer_id, ids, condition_id)
        ann["excluded_special_ids"] = sorted(_special_ids(tokenizer))
        return GeneratedContent(
            generator_id,
            item_id_for(generator_id, seed, prompt_budget, tokenizer_id),
            seed,
            None,
            ids,
            ann,
        )
    if condition_id == "natural_prose":
        content = generate_chat(
            seed,
            tokenizer,
            prompt_budget=prompt_budget,
            tokenizer_id=tokenizer_id,
            add_special_tokens=False,
            body_only=True,
        )
    elif condition_id == "code_like":
        content = generate_code(
            seed,
            tokenizer,
            prompt_budget=prompt_budget,
            tokenizer_id=tokenizer_id,
            add_special_tokens=False,
            body_only=True,
        )
    elif condition_id == "multilingual":
        content = _mixed_multilingual_sentinel(seed, tokenizer, prompt_budget, tokenizer_id)
    else:
        raise ValueError(f"unknown sentinel condition {condition_id!r}")
    generator_id = f"jw.sentinel.{condition_id}"
    ann = dict(content.annotations)
    ann.update(_sentinel_ann(generator_id, seed, tokenizer_id, content.prompt_token_ids, condition_id))
    return GeneratedContent(
        generator_id,
        item_id_for(generator_id, seed, prompt_budget, tokenizer_id),
        seed,
        None,
        content.prompt_token_ids,
        ann,
    )


def _mixed_multilingual_sentinel(
    seed: int,
    tokenizer: TokenizerProtocol,
    prompt_budget: int,
    tokenizer_id: str,
) -> GeneratedContent:
    drbg = Drbg(seed.to_bytes(8, "big"))
    order = [1, 2, 3, 4]
    per_block = max(1, (prompt_budget - 32) // 4)
    blocks = []
    for index in order[:-1]:
        block_seed = drbg.u64()
        block = generate_multiling(
            block_seed,
            tokenizer,
            prompt_budget=per_block,
            tokenizer_id=tokenizer_id,
            profile_index=index,
            add_special_tokens=False,
            body_only=True,
        )
        blocks.append(block.prompt_text or "")
    prologue = "\n".join(blocks) + "\n"
    prompt = realize_exact_prompt(
        tokenizer,
        target_tokens=prompt_budget,
        prologue=prologue,
        unit_factory=lambda: generate_multiling(
            drbg.u64(),
            tokenizer,
            prompt_budget=32,
            tokenizer_id=tokenizer_id,
            profile_index=order[-1],
            add_special_tokens=False,
            body_only=True,
        ).prompt_text
        or "",
        atom_ladder=[" و", " من", " في", " ا", " 0"],
        add_special_tokens=False,
    )
    ann = _base_annotations(
        "jw.multiling",
        seed,
        tokenizer_id,
        prompt,
        add_special_tokens=False,
        parameters={
            "mixed_profiles": {"source": "pinned", "value": ["ru-Cyrillic", "zh-CJK", "hi-Devanagari", "ar-Arabic"]},
            "coarse_headroom": {"source": "pinned", "value": 24},
        },
    )
    ann["chars_per_token"] = len(prompt.text) / max(1, len(prompt.token_ids))
    return GeneratedContent(
        "jw.multiling",
        item_id_for("jw.multiling", seed, prompt_budget, tokenizer_id),
        seed,
        prompt.text,
        prompt.token_ids,
        ann,
    )


def _sentinel_ann(
    generator_id: str,
    seed: int,
    tokenizer_id: str,
    ids: list[int],
    condition_id: str,
) -> dict[str, Any]:
    return {
        "generator_id": generator_id,
        "generator_version": GENERATOR_VERSION,
        "seed": seed,
        "tokenizer_id": tokenizer_id,
        "drbg": DRBG_VERSION,
        "condition_id": condition_id,
        "bos_present": False,
        "prompt_source": "token_ids",
        "realized_token_count": len(ids),
        "token_ids_sha256": prompt_token_ids_sha256(ids),
        "text_sha256": None,
    }


@dataclass(frozen=True)
class ManifestBuild:
    manifest: dict[str, Any]
    annotations: dict[str, Any]


def _difficulty(category: str) -> dict[str, Any]:
    return {
        "axis": "category",
        "value": 1.0,
        "scale": "nominal",
        "label": category,
        "source": "jw_mixed_v1",
        "quarantine_note": "synthetic generator category; no correctness claim",
    }


def _source(content: GeneratedContent, *, ids_native: bool, prompt_template_id: str) -> dict[str, Any]:
    source = {
        "source_item_id": content.item_id,
        "source_sha256": prompt_token_ids_sha256(content.prompt_token_ids),
        "prompt_template_id": prompt_template_id,
        "license": "internal-synthetic",
        "contamination_note": "license-clean synthetic content generated from closed banks",
    }
    if ids_native:
        source["prompt_token_ids"] = list(content.prompt_token_ids)
    else:
        source["prompt_text"] = content.prompt_text or ""
    return source


def _item(
    content: GeneratedContent,
    *,
    category: str,
    condition_id: str,
    block_id: str,
    level_id: str,
    prompt_budget: int,
    output_budget: int,
    ids_native: bool = False,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "item_id": content.item_id,
        "item_type": "ids_prompt" if ids_native else "text_prompt",
        "category": category,
        "difficulty": _difficulty(category),
        "shape": {
            "planned_prompt_tokens": prompt_budget,
            "planned_output_tokens": output_budget,
            "prompt_level": f"{prompt_budget}_tokens",
            "decode_level": f"{output_budget}_tokens",
        },
        "source": _source(
            content,
            ids_native=ids_native,
            prompt_template_id=content.generator_id + ":" + GENERATOR_VERSION,
        ),
        "grouping": {
            "condition_id": condition_id,
            "block_id": block_id,
            "level_id": level_id,
            "prefix_group_id": None,
        },
        "output_policy": "fixed_budget_exact",
        "status_policy": "none",
        "tags": tags or [],
    }


def _manifest_shell(
    *,
    suite_id: str,
    suite_profile: str,
    master_seed: str,
    tokenizer_id: str,
    tokenizer_manifest_hash: str,
    parameters: dict[str, Any],
    items: list[dict[str, Any]],
    order_policy: str = ORDER_POLICY_MANIFEST,
) -> dict[str, Any]:
    params_hash = hashlib.sha256(
        json.dumps(parameters, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    source_payload = {
        "item_ids": [item["item_id"] for item in items],
        "suite_profile": suite_profile,
        "tokenizer_id": tokenizer_id,
        "tokenizer_manifest_sha256": tokenizer_manifest_hash,
    }
    subset_sha = hashlib.sha256(
        json.dumps(source_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    manifest = {
        "schema_version": SUITE_SCHEMA_VERSION,
        "suite_id": suite_id,
        "suite_profile": suite_profile,
        "suite_revision": "2026-07-08",
        "suite_seed": master_seed,
        "generator": {
            "name": "jw_mixed_v1",
            "version": GENERATOR_VERSION,
            "parameters_hash": params_hash,
        },
        "analysis_contract": {
            "independent_unit": "bundle",
            "primary_window_class": "suite",
            "allowed_aggregation_levels": ["suite", "block", "level"],
        },
        "execution_policy": {
            "order_policy": order_policy,
            "within_bundle_repeats": 1,
            "cooldown_policy": "bundle_only",
            "cache_policy": "cold_between_bundles",
            "warmup_policy": "adapter_default",
            "default_output_policy": "fixed_budget_exact",
        },
        "source_manifest": {
            "source_id": "jw_mixed_v1:" + tokenizer_id,
            "source_kind": "synthetic",
            "revision": GENERATOR_VERSION,
            "subset_id": suite_profile,
            "subset_sha256": subset_sha,
            "license": "internal-synthetic",
            "contamination_note": "closed-bank synthetic prompts; tokenizer id includes B7 file manifest",
        },
        "items": items,
    }
    SuiteManifest.from_mapping(manifest)
    return manifest


def _write_sidecar(path: str | Path, annotations: dict[str, Any]) -> None:
    if path is None:
        raise ValueError("sidecar_path is required for manifest builds")
    sidecar = Path(path)
    sidecar.write_text(json.dumps(annotations, indent=2, sort_keys=True) + "\n")


def _tokenizer_audit(
    tokenizer_manifest: Sequence[TokenizerManifestRow] | None,
    tokenizer_id: str | None,
) -> tuple[str, list[dict[str, str]], str]:
    if tokenizer_manifest is None:
        raise ValueError("tokenizer_manifest is required for suite builds")
    rows = canonical_tokenizer_manifest(tokenizer_manifest)
    manifest_hash = tokenizer_manifest_sha256(tokenizer_manifest)
    derived = "tokfiles_" + manifest_hash
    if tokenizer_id is not None and tokenizer_id != derived:
        raise ValueError("tokenizer_id does not match tokenizer_manifest")
    return derived, rows, manifest_hash


def _build_jw_mixed_suite(
    master_seed: str,
    tokenizer: TokenizerProtocol,
    *,
    items_per_category: int = 6,
    prompt_budget: int = 512,
    output_budget: int = 256,
    tokenizer_manifest: Sequence[TokenizerManifestRow] | None = None,
    tokenizer_id: str | None = None,
    order_policy: str = ORDER_POLICY_MANIFEST,
) -> ManifestBuild:
    tok_id, tokenizer_rows, tokenizer_files_hash = _tokenizer_audit(
        tokenizer_manifest,
        tokenizer_id,
    )
    items: list[dict[str, Any]] = []
    annotations: dict[str, Any] = {
        "suite": "jw_mixed_v1",
        "tokenizer": {
            "tokenizer_id": tok_id,
            "files": tokenizer_rows,
            "files_sha256": tokenizer_files_hash,
        },
        "items": {},
    }
    for category, func in GENERATOR_FUNCS.items():
        for index in range(items_per_category):
            seed = item_seed(master_seed, category, index)
            kwargs: dict[str, Any] = {}
            if category == "jw.multiling":
                kwargs["profile_index"] = index % len(_BANKS["profiles"])
            content = func(
                seed,
                tokenizer,
                prompt_budget=prompt_budget,
                tokenizer_id=tok_id,
                **kwargs,
            )
            items.append(
                _item(
                    content,
                    category=category,
                    condition_id=category,
                    block_id=category,
                    level_id=f"common_{prompt_budget}_{output_budget}",
                    prompt_budget=prompt_budget,
                    output_budget=output_budget,
                )
            )
            annotations["items"][content.item_id] = content.annotations
    parameters = {
        "master_seed": master_seed,
        "prompt_budget": prompt_budget,
        "output_budget": output_budget,
        "items_per_category": items_per_category,
        "tokenizer_id": tok_id,
        "bank_hash": BANK_HASH,
    }
    if order_policy != ORDER_POLICY_MANIFEST:
        parameters["order_policy"] = order_policy
    suite_profile = f"jw_mixed_v1_common_{prompt_budget}_{output_budget}"
    manifest = _manifest_shell(
        suite_id="jw_mixed_v1",
        suite_profile=suite_profile,
        master_seed=master_seed,
        tokenizer_id=tok_id,
        tokenizer_manifest_hash=tokenizer_files_hash,
        parameters=parameters,
        items=items,
        order_policy=order_policy,
    )
    annotations["source_manifest"] = {
        "source_id": manifest["source_manifest"]["source_id"],
        "subset_sha256": manifest["source_manifest"]["subset_sha256"],
        "tokenizer_id": tok_id,
        "tokenizer_files_sha256": tokenizer_files_hash,
    }
    return ManifestBuild(manifest, annotations)


def build_jw_mixed_manifest(
    master_seed: str,
    tokenizer: TokenizerProtocol,
    *,
    sidecar_path: str | Path,
    **kwargs: Any,
) -> dict[str, Any]:
    build = _build_jw_mixed_suite(master_seed, tokenizer, **kwargs)
    _write_sidecar(sidecar_path, build.annotations)
    return build.manifest


SENTINEL_CONDITIONS = [
    "repeated_seed",
    "random_token",
    "natural_prose",
    "code_like",
    "multilingual",
]


def _build_sentinel_suite(
    master_seed: str,
    tokenizer: TokenizerProtocol,
    *,
    prompt_budget: int = 512,
    output_budget: int = 256,
    tokenizer_manifest: Sequence[TokenizerManifestRow] | None = None,
    tokenizer_id: str | None = None,
    order_policy: str = ORDER_POLICY_MANIFEST,
) -> ManifestBuild:
    tok_id, tokenizer_rows, tokenizer_files_hash = _tokenizer_audit(
        tokenizer_manifest,
        tokenizer_id,
    )
    items: list[dict[str, Any]] = []
    annotations: dict[str, Any] = {
        "suite": "jw_mixed_v1_sentinel",
        "tokenizer": {
            "tokenizer_id": tok_id,
            "files": tokenizer_rows,
            "files_sha256": tokenizer_files_hash,
        },
        "items": {},
    }
    for index, condition in enumerate(SENTINEL_CONDITIONS):
        seed = item_seed(master_seed, "jw.sentinel." + condition, index)
        content = sentinel_content(condition, seed, tokenizer, prompt_budget=prompt_budget, tokenizer_id=tok_id)
        items.append(
            _item(
                content,
                category="sentinel",
                condition_id=condition,
                block_id="sentinel",
                level_id=f"common_{prompt_budget}_{output_budget}",
                prompt_budget=prompt_budget,
                output_budget=output_budget,
                ids_native=True,
                tags=["sentinel"],
            )
        )
        annotations["items"][content.item_id] = content.annotations
    parameters = {
        "master_seed": master_seed,
        "prompt_budget": prompt_budget,
        "output_budget": output_budget,
        "conditions": SENTINEL_CONDITIONS,
        "tokenizer_id": tok_id,
        "bank_hash": BANK_HASH,
    }
    if order_policy != ORDER_POLICY_MANIFEST:
        parameters["order_policy"] = order_policy
    suite_profile = f"jw_mixed_v1_sentinel_{prompt_budget}_{output_budget}"
    manifest = _manifest_shell(
        suite_id="jw_mixed_v1_sentinel",
        suite_profile=suite_profile,
        master_seed=master_seed,
        tokenizer_id=tok_id,
        tokenizer_manifest_hash=tokenizer_files_hash,
        parameters=parameters,
        items=items,
        order_policy=order_policy,
    )
    annotations["source_manifest"] = {
        "source_id": manifest["source_manifest"]["source_id"],
        "subset_sha256": manifest["source_manifest"]["subset_sha256"],
        "tokenizer_id": tok_id,
        "tokenizer_files_sha256": tokenizer_files_hash,
    }
    return ManifestBuild(manifest, annotations)


def build_sentinel_manifest(
    master_seed: str,
    tokenizer: TokenizerProtocol,
    *,
    sidecar_path: str | Path,
    **kwargs: Any,
) -> dict[str, Any]:
    build = _build_sentinel_suite(master_seed, tokenizer, **kwargs)
    _write_sidecar(sidecar_path, build.annotations)
    return build.manifest


_assert_bank_hash()
