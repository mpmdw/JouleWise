"""Semantic-only receipt collections for calibration test fixtures."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
import copy
from dataclasses import dataclass
from typing import Any, TypeVar


Receipt = Mapping[str, Any]
MutableReceipt = dict[str, Any]
Selector = Callable[[Receipt], bool]
T = TypeVar("T")


def _selector(
    predicate: Selector | None,
    criteria: Mapping[str, Any],
) -> Selector:
    if predicate is not None and criteria:
        raise ValueError("use either a predicate or exact field criteria")
    if predicate is not None:
        return predicate
    return lambda row: all(row.get(key) == value for key, value in criteria.items())


@dataclass(frozen=True)
class ReceiptCorpus:
    """An ordered receipt corpus with no positional-access protocol."""

    _rows: tuple[Receipt, ...]

    def __init__(self, rows: Iterable[Receipt] = ()) -> None:
        object.__setattr__(self, "_rows", tuple(rows))

    def __iter__(self) -> Iterator[Receipt]:
        return iter(self._rows)

    def __len__(self) -> int:
        return len(self._rows)

    def __deepcopy__(self, memo: dict[int, Any]) -> "ReceiptCorpus":
        return ReceiptCorpus(copy.deepcopy(tuple(self._rows), memo))

    def filter(
        self,
        predicate: Selector | None = None,
        **criteria: Any,
    ) -> "ReceiptCorpus":
        select = _selector(predicate, criteria)
        return ReceiptCorpus(row for row in self if select(row))

    def one(
        self,
        predicate: Selector | None = None,
        **criteria: Any,
    ) -> Receipt:
        select = _selector(predicate, criteria)
        matches = [row for row in self if select(row)]
        if len(matches) != 1:
            raise AssertionError(f"semantic receipt selector matched {len(matches)} rows")
        return matches.pop()

    def replace(
        self,
        predicate: Selector,
        replacement: Receipt | Callable[[Receipt], Receipt],
    ) -> "ReceiptCorpus":
        target = self.one(predicate)
        replacement_row = replacement(target) if callable(replacement) else replacement
        return ReceiptCorpus(
            replacement_row if row is target else row for row in self
        )

    def without(self, predicate: Selector) -> "ReceiptCorpus":
        matches = self.filter(predicate)
        if not len(matches):
            raise AssertionError("semantic receipt removal matched no rows")
        return self.filter(lambda row: not predicate(row))

    def before(self, predicate: Selector) -> "ReceiptCorpus":
        self.one(predicate)
        prefix: list[Receipt] = []
        for row in self:
            if predicate(row):
                break
            prefix.append(row)
        return ReceiptCorpus(prefix)

    def replace_group(
        self,
        predicate: Selector,
        replacements: Iterable[Receipt],
    ) -> "ReceiptCorpus":
        matches = self.filter(predicate)
        if not len(matches):
            raise AssertionError("semantic receipt group selector matched no rows")
        emitted = False
        rows: list[Receipt] = []
        for row in self:
            if predicate(row):
                if not emitted:
                    rows.extend(replacements)
                    emitted = True
                continue
            rows.append(row)
        return ReceiptCorpus(rows)

    def insert_after(
        self,
        predicate: Selector,
        additions: Iterable[Receipt],
    ) -> "ReceiptCorpus":
        target = self.one(predicate)
        rows: list[Receipt] = []
        for row in self:
            rows.append(row)
            if row is target:
                rows.extend(additions)
        return ReceiptCorpus(rows)


def receipt_collection(function: T) -> T:
    """Annotate a helper whose return value is a wrapped receipt corpus."""

    setattr(function, "__receipt_collection__", True)
    return function


__all__ = ["ReceiptCorpus", "receipt_collection"]
