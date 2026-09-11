"""Synthetic mixed-epoch ledger fixtures for the S4 issuer's prepare-candidate.

Nothing here touches production configs or the real ledger: every fixture is
built into a disposable Git repository under a temporary directory, through the
real ledger writer, so the shapes the issuer authenticates are the shapes the
ledger actually produces.
"""
