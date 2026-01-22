"""Tensor and differential geometry operations."""

from __future__ import annotations

import sympy as sp


def auto_from_embedding(embedding: list[sp.Expr], coords: list[sp.Symbol]) -> sp.Matrix:
    """Compute the metric tensor from an embedding X(coords)."""

    if len(embedding) != 3:
        raise ValueError("embedding must be a 3-vector")
    jacobian = sp.Matrix(embedding).jacobian(coords)
    metric = jacobian.T * jacobian
    return sp.Matrix(metric)


def christoffel_symbols(
    metric: sp.Matrix, coords: list[sp.Symbol]
) -> sp.ImmutableDenseNDimArray:
    """Compute Christoffel symbols of the second kind."""

    dim = metric.shape[0]
    if metric.shape[0] != metric.shape[1]:
        raise ValueError("metric must be square")
    g_inv = metric.inv()
    gamma = [
        [[sp.Integer(0) for _ in range(dim)] for _ in range(dim)] for _ in range(dim)
    ]
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                term = sp.Integer(0)
                for ell in range(dim):
                    term += g_inv[i, ell] * (
                        sp.diff(metric[ell, j], coords[k])
                        + sp.diff(metric[ell, k], coords[j])
                        - sp.diff(metric[j, k], coords[ell])
                    )
                gamma[i][j][k] = sp.simplify(sp.Rational(1, 2) * term)
    return sp.ImmutableDenseNDimArray(gamma)


def riemann_tensor(
    metric: sp.Matrix, coords: list[sp.Symbol]
) -> sp.ImmutableDenseNDimArray:
    """Compute Riemann curvature tensor R^i_{jkl}."""

    dim = metric.shape[0]
    gamma = christoffel_symbols(metric, coords)
    riemann = [
        [[[sp.Integer(0) for _ in range(dim)] for _ in range(dim)] for _ in range(dim)]
        for _ in range(dim)
    ]
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                for ell in range(dim):
                    term = sp.diff(gamma[i, j, ell], coords[k]) - sp.diff(
                        gamma[i, j, k], coords[ell]
                    )
                    for m in range(dim):
                        term += (
                            gamma[i, k, m] * gamma[m, j, ell]
                            - gamma[i, ell, m] * gamma[m, j, k]
                        )
                    riemann[i][j][k][ell] = sp.simplify(term)
    return sp.ImmutableDenseNDimArray(riemann)


def ricci_tensor(metric: sp.Matrix, coords: list[sp.Symbol]) -> sp.Matrix:
    """Compute Ricci tensor R_{ij}."""

    dim = metric.shape[0]
    riemann = riemann_tensor(metric, coords)
    ricci = sp.zeros(dim)
    for i in range(dim):
        for j in range(dim):
            term = sp.Integer(0)
            for k in range(dim):
                term += riemann[k, i, k, j]
            ricci[i, j] = sp.simplify(term)
    return sp.Matrix(ricci)


def scalar_curvature(metric: sp.Matrix, coords: list[sp.Symbol]) -> sp.Expr:
    """Compute scalar curvature R."""

    ricci = ricci_tensor(metric, coords)
    g_inv = metric.inv()
    dim = metric.shape[0]
    scalar = sp.Integer(0)
    for i in range(dim):
        for j in range(dim):
            scalar += g_inv[i, j] * ricci[i, j]
    return sp.simplify(scalar)


def gaussian_curvature(metric: sp.Matrix, coords: list[sp.Symbol]) -> sp.Expr:
    """Compute Gaussian curvature for 2D metrics."""

    if metric.shape != (2, 2):
        raise ValueError("Gaussian curvature requires a 2x2 metric")
    scalar = scalar_curvature(metric, coords)
    return sp.simplify(scalar / 2)


def laplace_beltrami(metric: sp.Matrix, coords: list[sp.Symbol], f: sp.Expr) -> sp.Expr:
    """Compute Laplace-Beltrami of a scalar field."""

    if metric.shape[0] != metric.shape[1]:
        raise ValueError("metric must be square")
    dim = metric.shape[0]
    g_inv = metric.inv()
    det_g = sp.simplify(metric.det())
    sqrt_g = sp.sqrt(det_g)
    result = sp.Integer(0)
    for i in range(dim):
        term = sp.Integer(0)
        for j in range(dim):
            term += g_inv[i, j] * sp.diff(f, coords[j])
        result += sp.diff(sqrt_g * term, coords[i])
    return sp.simplify(result / sqrt_g)
