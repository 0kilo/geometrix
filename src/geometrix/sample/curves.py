"""Curve sampling utilities."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from geometrix.sample.domains import Domain


@dataclass(frozen=True)
class CurveSamples:
    positions: np.ndarray


def sample_curve(
    func: Callable[[np.ndarray], tuple[np.ndarray, np.ndarray, np.ndarray]],
    domain: Domain,
    count: int,
) -> CurveSamples:
    """Sample a parametric curve over a 1D domain."""
    t_vals = domain.linspace(count)
    x_vals, y_vals, z_vals = func(t_vals)
    x_vals = _broadcast_to(x_vals, t_vals.shape)
    y_vals = _broadcast_to(y_vals, t_vals.shape)
    z_vals = _broadcast_to(z_vals, t_vals.shape)
    positions = np.stack([x_vals, y_vals, z_vals], axis=-1)
    return CurveSamples(positions=positions.astype(np.float32))


def _broadcast_to(values: np.ndarray, shape: tuple[int, ...]) -> np.ndarray:
    array = np.asarray(values)
    if array.shape != shape:
        return np.broadcast_to(array, shape)
    return array
