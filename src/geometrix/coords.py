"""Coordinate helper utilities."""

from __future__ import annotations

import sympy as sp


def cylindrical_to_cartesian(r: sp.Expr, phi: sp.Expr, z: sp.Expr) -> list[sp.Expr]:
    """Convert cylindrical coordinates to Cartesian (x, y, z)."""

    return [r * sp.cos(phi), r * sp.sin(phi), z]


def spherical_to_cartesian(r: sp.Expr, theta: sp.Expr, phi: sp.Expr) -> list[sp.Expr]:
    """Convert spherical coordinates to Cartesian (x, y, z)."""

    return [
        r * sp.sin(theta) * sp.cos(phi),
        r * sp.sin(theta) * sp.sin(phi),
        r * sp.cos(theta),
    ]


def lorentz_metric(c: sp.Expr | float = 1.0) -> sp.Matrix:
    """Return Minkowski metric with signature (-,+,+,+)."""

    c_sym = sp.sympify(c)
    return sp.diag(-(c_sym**2), 1, 1, 1)
