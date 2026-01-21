"""Compile SymPy expressions into numeric evaluators."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import sympy as sp


@dataclass(frozen=True)
class CompiledExpression:
    symbols: tuple[sp.Symbol, ...]
    func: Callable[..., Any]

    def __call__(self, *args: Any) -> Any:
        return self.func(*args)


def compile_expr(expr: sp.Expr, symbols: list[sp.Symbol]) -> CompiledExpression:
    """Compile a SymPy expression to a numpy-backed callable."""

    func = sp.lambdify(symbols, expr, modules=["numpy"])
    return CompiledExpression(symbols=tuple(symbols), func=func)


def compile_vector(
    exprs: list[sp.Expr], symbols: list[sp.Symbol]
) -> CompiledExpression:
    """Compile a vector of SymPy expressions into a callable."""

    func = sp.lambdify(symbols, exprs, modules=["numpy"])
    return CompiledExpression(symbols=tuple(symbols), func=func)
