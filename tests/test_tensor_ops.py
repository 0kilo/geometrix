import sympy as sp

from geometrix.symbolic.ops import (
    auto_from_embedding,
    christoffel_symbols,
    gaussian_curvature,
    laplace_beltrami,
    scalar_curvature,
)


def test_plane_metric_and_curvature():
    u, v = sp.symbols("u v")
    embedding = [u, v, sp.Integer(0)]
    metric = auto_from_embedding(embedding, [u, v])
    assert metric == sp.eye(2)

    gamma = christoffel_symbols(metric, [u, v])
    assert gamma[0, 0, 0] == 0
    assert gamma[1, 1, 1] == 0

    assert scalar_curvature(metric, [u, v]) == 0
    assert gaussian_curvature(metric, [u, v]) == 0


def test_laplace_beltrami_plane():
    u, v = sp.symbols("u v")
    metric = sp.eye(2)
    f = u**2 + v**2
    result = laplace_beltrami(metric, [u, v], f)
    assert sp.simplify(result - 4) == 0
