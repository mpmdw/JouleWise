"""Test-only loading of immutable historical generator source.

Archived generators keep their original import spelling and bytes. Their
synthetic fixture executions bind that spelling to the extracted readers,
then remove the binding. No retired implementation is loaded or installed in
the main checkout.
"""
from functools import wraps
from pathlib import Path



from joulewise.stored_generator import historical_reader_imports


def exec_archived_generator(loader, module):
    if Path(module.__file__).name != "generate_configs.py":
        return loader.exec_module(module)
    with historical_reader_imports():
        return loader.exec_module(module)


def historical_generator_call(function):
    @wraps(function)
    def invoke(*args, **kwargs):
        with historical_reader_imports():
            return function(*args, **kwargs)
    return invoke
