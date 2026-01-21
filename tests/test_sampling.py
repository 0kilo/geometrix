import numpy as np
import sympy as sp

from geometrix.sample.curves import sample_curve
from geometrix.sample.domains import Domain
from geometrix.sample.points import sample_points
from geometrix.sample.surface import sample_surface_grid
from geometrix.symbolic.compile import compile_expr, compile_vector


def test_compile_expr_scalar():
    x = sp.Symbol("x")
    expr = sp.sin(x) + 1
    compiled = compile_expr(expr, [x])
    result = compiled(np.array([0.0, np.pi / 2]))
    assert np.allclose(result, np.array([1.0, 2.0]))


def test_compile_vector_and_surface_sampling():
    u, v = sp.symbols("u v")
    vector = [sp.cos(u), sp.sin(u), v]
    compiled = compile_vector(vector, [u, v])

    domain_u = Domain("u", 0.0, np.pi)
    domain_v = Domain("v", 0.0, 1.0)
    surface = sample_surface_grid(compiled, [domain_u, domain_v], [3, 2])
    assert surface.positions.shape == (6, 3)
    assert surface.grid_shape == (3, 2)


def test_curve_sampling():
    t = sp.Symbol("t")
    vector = [t, t * 0, t * 0]
    compiled = compile_vector(vector, [t])

    curve = sample_curve(compiled, Domain("t", 0.0, 1.0), 4)
    assert curve.positions.shape == (4, 3)
    assert np.allclose(curve.positions[:, 0], np.linspace(0.0, 1.0, 4))


def test_point_sampling():
    def func(x, y):
        return x, y, x + y

    coords = [np.array([0.0, 1.0]), np.array([2.0, 3.0])]
    points = sample_points(func, coords)
    assert points.positions.shape == (2, 3)
