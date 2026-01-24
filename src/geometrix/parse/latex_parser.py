"""Safe LaTeX parsing helpers."""

from __future__ import annotations

import re
from collections.abc import Iterable


class LatexParseError(ValueError):
    pass


_ALLOWED_COMMANDS = {
    "abs",
    "arccos",
    "arcsin",
    "arctan",
    "sin",
    "cos",
    "tan",
    "cot",
    "sec",
    "csc",
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
    "sum",
    "prod",
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
        import sympy as sp
        from sympy.parsing.sympy_parser import (
            implicit_multiplication_application,
            parse_expr,
            standard_transformations,
        )
    except Exception as exc:  # pragma: no cover - optional dependency
        raise LatexParseError("sympy is required for LaTeX parsing") from exc

    expr_text = _latex_to_sympy(latex)
    transformations = standard_transformations + (implicit_multiplication_application,)
    local_dict = _build_locals(allowed_symbols, sp)
    try:
        return parse_expr(expr_text, local_dict=local_dict, transformations=transformations)
    except Exception as exc:
        raise LatexParseError(f"Failed to parse LaTeX: {exc}") from exc


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


def _latex_to_sympy(latex: str) -> str:
    expr = latex
    expr = expr.replace("\\left", "").replace("\\right", "")
    expr = expr.replace("\\cdot", "*").replace("\\times", "*")
    expr = _replace_frac(expr)
    expr = _replace_sqrt(expr)
    expr = _replace_commands(expr)
    expr = _replace_subscripts(expr)
    expr = _replace_powers(expr)
    return expr


def _replace_commands(expr: str) -> str:
    replacements = {
        "\\sin": "sin",
        "\\cos": "cos",
        "\\tan": "tan",
        "\\cot": "cot",
        "\\sec": "sec",
        "\\csc": "csc",
        "\\sinh": "sinh",
        "\\cosh": "cosh",
        "\\tanh": "tanh",
        "\\asin": "asin",
        "\\acos": "acos",
        "\\atan": "atan",
        "\\arcsin": "asin",
        "\\arccos": "acos",
        "\\arctan": "atan",
        "\\exp": "exp",
        "\\log": "log",
        "\\ln": "log",
        "\\pi": "pi",
        "\\alpha": "alpha",
        "\\beta": "beta",
        "\\gamma": "gamma",
        "\\delta": "delta",
        "\\epsilon": "epsilon",
        "\\varepsilon": "varepsilon",
        "\\zeta": "zeta",
        "\\eta": "eta",
        "\\theta": "theta",
        "\\kappa": "kappa",
        "\\lambda": "lambda",
        "\\mu": "mu",
        "\\nu": "nu",
        "\\xi": "xi",
        "\\rho": "rho",
        "\\sigma": "sigma",
        "\\tau": "tau",
        "\\upsilon": "upsilon",
        "\\phi": "phi",
        "\\chi": "chi",
        "\\psi": "psi",
        "\\omega": "omega",
        "\\Gamma": "Gamma",
        "\\Delta": "Delta",
        "\\Lambda": "Lambda",
        "\\Omega": "Omega",
        "\\Sigma": "Sigma",
        "\\Theta": "Theta",
    }
    for key, value in replacements.items():
        expr = expr.replace(key, value)
    return expr


def _replace_powers(expr: str) -> str:
    expr = re.sub(r"\^\{([^}]+)\}", r"**(\1)", expr)
    expr = re.sub(r"\^([A-Za-z0-9]+)", r"**\1", expr)
    return expr


def _replace_subscripts(expr: str) -> str:
    expr = re.sub(r"_\{([^}]+)\}", r"_\1", expr)
    return expr


def _replace_frac(expr: str) -> str:
    while "\\frac" in expr:
        idx = expr.find("\\frac")
        if idx == -1:
            break
        num, num_end = _extract_group(expr, idx + 5)
        den, den_end = _extract_group(expr, num_end)
        if num is None or den is None:
            break
        replacement = f"({num})/({den})"
        expr = expr[:idx] + replacement + expr[den_end:]
    return expr


def _replace_sqrt(expr: str) -> str:
    while "\\sqrt" in expr:
        idx = expr.find("\\sqrt")
        if idx == -1:
            break
        rad, rad_end = _extract_group(expr, idx + 5)
        if rad is None:
            break
        replacement = f"sqrt({rad})"
        expr = expr[:idx] + replacement + expr[rad_end:]
    return expr


def _extract_group(text: str, start: int) -> tuple[str | None, int]:
    start = _skip_whitespace(text, start)
    if start >= len(text) or text[start] != "{":
        return None, start
    depth = 0
    for idx in range(start, len(text)):
        char = text[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : idx], idx + 1
    return None, start


def _skip_whitespace(text: str, start: int) -> int:
    idx = start
    while idx < len(text) and text[idx].isspace():
        idx += 1
    return idx


def _build_locals(allowed_symbols: Iterable[str], sp) -> dict[str, object]:
    local_dict: dict[str, object] = {
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "cot": sp.cot,
        "sec": sp.sec,
        "csc": sp.csc,
        "sinh": sp.sinh,
        "cosh": sp.cosh,
        "tanh": sp.tanh,
        "asin": sp.asin,
        "acos": sp.acos,
        "atan": sp.atan,
        "exp": sp.exp,
        "log": sp.log,
        "sqrt": sp.sqrt,
        "pi": sp.pi,
    }
    for name in allowed_symbols:
        if name in local_dict:
            continue
        local_dict[name] = sp.Symbol(name)
    return local_dict
