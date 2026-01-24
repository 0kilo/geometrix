import pytest
import sympy as sp

from geometrix import canonicalize, latex_equation, simplify, solve
from geometrix.sample.domains import Domain, validate_domains


def test_latex_equation_parses():
    eq = latex_equation("x=1")
    x = sp.Symbol("x")
    assert eq == sp.Eq(x, 1)


def test_simplify_modes():
    x = sp.Symbol("x")
    expr = x**2 - 1
    assert simplify(expr, mode="expand") == sp.expand(expr)
    assert simplify(expr, mode="factor") == sp.factor(expr)


def test_canonicalize_expr():
    x = sp.Symbol("x")
    expr = (x**2 - 1) / (x - 1)
    assert canonicalize(expr) == sp.simplify(sp.together(sp.expand(expr)))


def test_solve_constraints():
    x, y = sp.symbols("x y")
    solutions = solve([x + y - 1, x - y - 1], [x, y], dict=True)
    assert solutions == [{x: 1, y: 0}]


def test_validate_domains():
    domains = [Domain("u", 0.0, 1.0)]
    validate_domains(domains)
    with pytest.raises(ValueError):
        validate_domains([Domain("u", 1.0, 0.0)])
