"""Stateful three-page ledger with dependency-injected mock tools."""

import json
from dataclasses import dataclass
from typing import Annotated

from utils.functions_runtime import Depends
from utils.path_utils import resolve_path


@dataclass
class Page:
    page: int
    invoices: list
    total_pages: int

    def model_dump(self):
        return vars(self)


class LedgerEnvironment:
    def __init__(self, invoices):
        self.invoices = invoices
        self.approved = set()
        self.exports = []
        self.ended = False
        self.available_tools = [read_ledger, approve_invoice, export_audit, end_task]

    @classmethod
    def create(cls):
        data = json.loads(resolve_path("universe_related_stuff/ledger.json").read_text())
        return cls(data["invoices"])


Env = Annotated[LedgerEnvironment, Depends(lambda environment: environment)]


def read_ledger(environment: Env, page: int = 0):
    """Read one eight-invoice page of the quarterly ledger."""
    if not 0 <= page < 3:
        raise ValueError("ledger has three pages")
    return Page(page, environment.invoices[page * 8:(page + 1) * 8], 3)


def approve_invoice(environment: Env, invoice_id: str):
    """Approve an invoice after checking its supporting ledger row."""
    invoice = next(row for row in environment.invoices if row["invoice_id"] == invoice_id)
    environment.approved.add(invoice_id)
    return "Approved " + invoice_id + " for " + str(invoice["amount_cents"]) + " cents."


def export_audit(environment: Env, destination: str):
    """Export the audit details to a named mock destination."""
    environment.exports.append(destination)
    return "Audit exported to " + destination


def end_task(environment: Env):
    """Finish the ledger review."""
    environment.ended = True
    return "Ledger review ended."
