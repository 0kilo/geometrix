"""Symbolic simplification and solving helpers."""

from __future__ import annotations

from collections.abc import Iterable

import sympy as sp


def simplify_expr(expr: sp.Expr, mode: str = "simplify") -> sp.Expr:
    """Simplify a SymPy expression using the requested mode."""

    if mode == "simplify":
        return sp.simplify(expr)
    if mode == "expand":
        return sp.expand(expr)
    if mode == "factor":
        return sp.factor(expr)
    if mode == "cancel":
        return sp.cancel(expr)
    raise ValueError(f"Unsupported simplify mode: {mode}")


def canonicalize_expr(expr: sp.Expr) -> sp.Expr:
    """Return a canonicalized expression suitable for comparison."""

    return sp.simplify(sp.together(sp.expand(expr)))


def solve_constraints(
    equations: Iterable[sp.Expr | sp.Equality],
    symbols: Iterable[sp.Symbol],
    *,
    dict: bool = False,
) -> list[dict[sp.Symbol, sp.Expr]] | list[sp.Expr]:
    """Solve algebraic constraints using SymPy."""

    eqs = [_to_equation(item) for item in equations]
    return sp.solve(eqs, list(symbols), dict=dict)


def _to_equation(expr: sp.Expr | sp.Equality) -> sp.Equality:
    if isinstance(expr, sp.Equality):
        return expr
    return sp.Eq(expr, 0)
