"""JouleWise-owned model ports used by the ALIGN measurement stack.

Modules in this package import heavy dependencies (``mlx``, ``mlx_lm``,
``numpy``) at module import time, so this package ``__init__`` deliberately
imports nothing: the core ``joulewise`` package stays stdlib-only (D-009).
"""
