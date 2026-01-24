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


def test_parse_dsl_tensor_definition():
    text = """
    coords: u v
    g_{ij} = (1, 0, 0, 1)
    Gamma^i_{jk} = 0
    """
    ir = parse_dsl(text)
    assert ir.definitions["g_{ij}"].kind.value == "tensor"
    assert ir.definitions["Gamma^i_{jk}"].kind.value == "tensor"
    metadata = ir.tensor_metadata["g_{ij}"]
    assert metadata.order == 2
    assert metadata.dim == 2


def test_parse_dsl_time_default_and_override():
    ir = parse_dsl("coords: u v")
    assert ir.time_param == "t"
    assert ir.time_value == 0.0

    ir = parse_dsl("coords: u v\nparams: t=2")
    assert ir.time_value == 2.0


def test_parse_dsl_rejects_unknown_statement():
    with pytest.raises(DSLParseError):
        parse_dsl("unknown: value")


def test_parse_latex_rejects_unknown_command():
    with pytest.raises(LatexParseError):
        parse_latex_expr(r"\\badcmd(x)", allowed_symbols=["x"])


def test_parse_latex_rejects_invalid_chars():
    with pytest.raises(LatexParseError):
        parse_latex_expr(r"x; y", allowed_symbols=["x", "y"])


def test_parse_latex_accepts_known_command():
    sympy = pytest.importorskip("sympy")
    expr = parse_latex_expr(r"\sin(x)", allowed_symbols=["x"])
    assert str(expr) == str(sympy.sin(sympy.Symbol("x")))


def test_parse_latex_allows_index_symbols():
    sympy = pytest.importorskip("sympy")
    expr = parse_latex_expr("i", allowed_symbols=[])
    assert str(expr) == str(sympy.Symbol("i"))


def test_parse_dsl_tensor_shape_validation():
    text = """
    coords: u v
    g_{ij} = (1, 0, 1)
    """
    with pytest.raises(DSLParseError):
        parse_dsl(text)
