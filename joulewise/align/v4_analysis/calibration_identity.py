"""Runtime identity of the calibration predicate (lead ruling on r23j2-sol P2).

The static port audit (tests.align.test_v4_calibration_port_pin) reads source.
It cannot see what actually runs: an import-time side effect in another module,
an importlib monkeypatch, a star import or a runtime setattr. This module checks
the LIVE objects at the start of every analyze/io.load run, before any
calibration use:

- each pinned function must be a plain function whose `__globals__` is its
  module's namespace. Its code (bytecode, names, constants, recursively),
  defaults and closure must equal the pins;
- the CURRENT value of every reached module global must equal its pin;
- the engine's references must be the very objects held by those modules.

The pins were computed from align/2026-11-08-v4-r11 @ bbfccb70a under the
release interpreter (CPython 3.13); bytecode is interpreter-specific. Nothing is
cached: every call rehashes. Any difference refuses as calibration_identity_drift.
"""
import hashlib
import json
import sys
import types

R11_COMMIT = 'bbfccb70ab993c395f254058694906610547651d'
INTERPRETER = (3, 13)
CADENCE = 'joulewise.align.apple.v4_cadence'
KIT = 'scripts.align_v4_kit'
FUNCTIONS = {CADENCE: ('calibration_stop', '_validated_rulings', 'slot_of', '_is_digest'),
             KIT: ('valid_lead_signature',)}
VALUES = {CADENCE: ('CAL_PAIRS', 'CAL_WINDOWS', 'CAL_TARGET_PER_PAIR', 'BENIGN_PER_PAIR_PER_WINDOW',
                    'WINDOW_MEMBERS', 'CAPTURED_MAX', 'REPLACEMENT_WINDOWS', 'STRUCTURAL_BARS',
                    'ZERO_CAPTURE_BAR', 'RULING_RESETS'),
          KIT: ('UNSIGNED',)}
MODULE_GLOBALS = {CADENCE: {'re': 're'}, KIT: {}}
# Computed from r11 bbfccb70a sources under CPython 3.13 (tests.align.test_v4_calibration_identity).
PINS = {
    'joulewise.align.apple.v4_cadence': {
        'BENIGN_PER_PAIR_PER_WINDOW': '6e55bc0ba6ede370ebf04b3d78e3b4781cc3f3687add79eb884a476013f4f8a5',
        'CAL_PAIRS': '93a4752658760c422b04c5a8c431c296355226200142f4c0acc1c234658e2ae0',
        'CAL_TARGET_PER_PAIR': '84f0304f8f076badb00f06e62cb500c0d62fda74fa5502570067886f75bc2f52',
        'CAL_WINDOWS': 'bbda34ba52144edfc1ff733580053fda0e26f7aca39838f30ddedd077546af5b',
        'CAPTURED_MAX': '24f8494b4fe2a0890be33e15c2e582f1c50ba61b074d74858125ebca81713196',
        'REPLACEMENT_WINDOWS': '05e737d33495ad2cee53aa34d874374c3d90fcc1ddb8e1b020351b1b8c6f232d',
        'RULING_RESETS': 'a6278e1a1e59cf07c6188d1c662a74d4a21f461048969d72d59c42cf2accc617',
        'STRUCTURAL_BARS': '9dcb8ea3565fdcc3aa3b8acb9f881c0d276907bb810048692e89c4a4faf293e6',
        'WINDOW_MEMBERS': '24f8494b4fe2a0890be33e15c2e582f1c50ba61b074d74858125ebca81713196',
        'ZERO_CAPTURE_BAR': 'f43d72301bd696a17380bdffd11d4989322807842f400f772127e0d0dd93f7b6',
        '_is_digest': 'a01767c06c70a267e4069ec0b425005d616a7bbb30905a533fc66f52237e3e4e',
        '_validated_rulings': '8cec4b6d5f607f355d93e32620f28b316989b1ae75b15c1996bfc9b0a0d537b3',
        'calibration_stop': '27d33ed2a7c0d90d64f3c207e1be074b0735ce144bd8b26680d0409ebf697948',
        're': '34eba27d5c2035643b1455fa6f33c92c1222613bd4ff1cb5b1a40ed2a4457a2b',
        'slot_of': 'd678069fd4fa3a3d883f2cfcd9d96cabf0eb28a3560e99cc4e5010ad2272bcee',
    },
    'scripts.align_v4_kit': {
        'UNSIGNED': 'daff8f956ef077f599f2c7b1a2273325788969ce240c516179316c25728a070b',
        'valid_lead_signature': '39ce4f1f5018770f017a10d2fcd986cb0051cf0e915ccc75b3c3ab6e0e6db77c',
    },
}


def _canonical(value):
    if isinstance(value, types.CodeType):
        return ['code', code_digest(value)]
    if isinstance(value, (tuple, list)):
        return [type(value).__name__, [_canonical(v) for v in value]]
    if isinstance(value, (frozenset, set)):
        return [type(value).__name__, sorted((_canonical(v) for v in value), key=json.dumps)]
    if isinstance(value, dict):
        return ['dict', sorted(([_canonical(k), _canonical(v)] for k, v in value.items()), key=json.dumps)]
    if value is None or isinstance(value, (bool, int, float, str, bytes, complex)) or value is Ellipsis:
        return [type(value).__name__, repr(value)]
    raise TypeError(f'uncanonical value of type {type(value).__name__}')


def code_digest(code):
    """Bytecode, names, locals and constants of a code object, recursively; no filename/lines."""
    fields = [code.co_name, code.co_code.hex(), list(code.co_names), list(code.co_varnames),
              list(code.co_freevars), list(code.co_cellvars), code.co_argcount, code.co_posonlyargcount,
              code.co_kwonlyargcount, code.co_flags, [_canonical(c) for c in code.co_consts]]
    return hashlib.sha256(json.dumps(fields, sort_keys=True).encode()).hexdigest()


def function_digest(function):
    return hashlib.sha256(json.dumps([code_digest(function.__code__), _canonical(function.__defaults__),
        _canonical(function.__kwdefaults__), function.__closure__ is None], sort_keys=True).encode()).hexdigest()


def value_digest(value):
    return hashlib.sha256(json.dumps(_canonical(value), sort_keys=True).encode()).hexdigest()


def live_digests(modules):
    """{module: {name: digest}} of the live objects; raises on a non-plain function."""
    out = {}
    for name in FUNCTIONS:
        module = modules[name]
        row = {}
        for fn in FUNCTIONS[name]:
            obj = module.__dict__.get(fn)
            if type(obj) is not types.FunctionType or obj.__globals__ is not module.__dict__:
                raise ValueError(f'calibration_identity_drift: {name}.{fn} is not the plain module function')
            row[fn] = function_digest(obj)
        for value in VALUES[name]:
            if value not in module.__dict__:
                raise ValueError(f'calibration_identity_drift: {name}.{value} missing')
            row[value] = value_digest(module.__dict__[value])
        for alias, target in MODULE_GLOBALS[name].items():
            if module.__dict__.get(alias) is not sys.modules.get(target):
                raise ValueError(f'calibration_identity_drift: {name}.{alias} is not module {target}')
            row[alias] = value_digest(target)
        out[name] = row
    return out


def check():
    """Refuse unless the live calibration predicate is r11's. Never cached."""
    if tuple(sys.version_info[:2]) != INTERPRETER:
        raise ValueError(f'calibration_identity_drift: pins are for CPython {INTERPRETER}, '
                         f'running {tuple(sys.version_info[:2])}')
    import importlib
    from joulewise.align.apple import v4_cadence
    from joulewise.align.v4_analysis import engine
    kit = sys.modules.get(KIT) or importlib.import_module(KIT)
    modules = {CADENCE: sys.modules.get(CADENCE), KIT: sys.modules.get(KIT)}
    if modules[CADENCE] is not v4_cadence or modules[KIT] is not kit:
        raise ValueError('calibration_identity_drift: calibration modules were replaced in sys.modules')
    for name in ('calibration_stop', 'slot_of', 'STRUCTURAL_BARS'):
        if getattr(engine, name) is not getattr(v4_cadence, name):
            raise ValueError(f'calibration_identity_drift: engine.{name} is not v4_cadence.{name}')
    live = live_digests(modules)
    if live != PINS:
        drift = sorted(f'{m}.{n}' for m in PINS for n in PINS[m] if live.get(m, {}).get(n) != PINS[m][n])
        raise ValueError('calibration_identity_drift: ' + ', '.join(drift))
    return live
