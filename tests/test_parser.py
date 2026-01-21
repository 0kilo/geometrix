import pytest

from geometrix.parse.dsl_parser import DSLParseError, parse_dsl
from geometrix.parse.latex_parser import LatexParseError, parse_latex_expr


def test_parse_dsl_coords_params_definitions_render():
    text = """
    coords: u v
    params: R=1
    X(u,v) = (R*sin(u), R*cos(v), R)
    K = 1
    render: surface X color=K res 10 20
    """
    ir = parse_dsl(text)
    assert ir.coords == ["u", "v"]
    assert ir.params["R"] == 1.0
    assert ir.definitions["X"].args == ("u", "v")
    assert ir.definitions["X"].kind.value == "vector"
    assert ir.render_requests[0].kind == "surface"
    assert ir.render_requests[0].options["res"] == "10 20"


def test_parse_dsl_rejects_unknown_statement():
    with pytest.raises(DSLParseError):
        parse_dsl("unknown: value")


def test_parse_latex_rejects_unknown_command():
    with pytest.raises(LatexParseError):
        parse_latex_expr(r"\\badcmd(x)", allowed_symbols=["x"])


def test_parse_latex_accepts_known_command():
    sympy = pytest.importorskip("sympy")
    pytest.importorskip("antlr4")
    try:
        expr = parse_latex_expr(r"\sin(x)", allowed_symbols=["x"])
    except LatexParseError as exc:
        if "antlr4" in str(exc):
            pytest.skip("antlr4 runtime not available")
        raise
    assert str(expr) == str(sympy.sin(sympy.Symbol("x")))
