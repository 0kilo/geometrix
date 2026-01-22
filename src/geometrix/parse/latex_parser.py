"""Safe LaTeX parsing helpers."""

from __future__ import annotations

import re
from collections.abc import Iterable


class LatexParseError(ValueError):
    pass


_ALLOWED_COMMANDS = {
    "sin",
    "cos",
    "tan",
    "sinh",
    "cosh",
    "tanh",
    "asin",
    "acos",
    "atan",
    "exp",
    "log",
    "ln",
    "sqrt",
    "frac",
    "left",
    "right",
    "cdot",
    "times",
    "partial",
    "nabla",
    "pi",
    "alpha",
    "beta",
    "gamma",
    "delta",
    "epsilon",
    "varepsilon",
    "zeta",
    "eta",
    "theta",
    "kappa",
    "lambda",
    "mu",
    "nu",
    "xi",
    "rho",
    "sigma",
    "tau",
    "upsilon",
    "phi",
    "chi",
    "psi",
    "omega",
    "Gamma",
    "Delta",
    "Lambda",
    "Omega",
    "Sigma",
    "Theta",
}

_INDEX_SYMBOLS = {"i", "j", "k", "l", "m", "n", "a", "b", "c", "d"}


def parse_latex_expr(latex: str, allowed_symbols: Iterable[str]):
    """Parse a LaTeX string into a SymPy expression."""
    _validate_latex(latex, allowed_symbols)
    try:
        from sympy.parsing.latex import parse_latex
    except Exception as exc:  # pragma: no cover - optional dependency
        raise LatexParseError("sympy is required for LaTeX parsing") from exc
    try:
        return parse_latex(latex)
    except ImportError as exc:
        raise LatexParseError("antlr4 runtime is required for LaTeX parsing") from exc


def _validate_latex(latex: str, allowed_symbols: Iterable[str]) -> None:
    if any(ch in latex for ch in (";", "@", "`", "$")):
        raise LatexParseError("Unsupported characters in LaTeX")
    allowed = set(allowed_symbols) | _INDEX_SYMBOLS
    for command in _extract_commands(latex):
        if command not in _ALLOWED_COMMANDS:
            raise LatexParseError(f"Unsupported LaTeX command: \\{command}")
    for symbol in _extract_symbols(latex):
        if symbol not in allowed:
            raise LatexParseError(f"Unknown symbol: {symbol}")


def _extract_commands(latex: str) -> list[str]:
    return re.findall(r"\\([A-Za-z]+)", latex)


def _extract_symbols(latex: str) -> list[str]:
    tokens = re.findall(r"\b[A-Za-z]+\b", latex)
    return [token for token in tokens if token not in _ALLOWED_COMMANDS]
