"""Point cloud sampling utilities."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PointSamples:
    positions: np.ndarray


def sample_points(
    func: Callable[..., tuple[np.ndarray, np.ndarray, np.ndarray]],
    coords: list[np.ndarray],
) -> PointSamples:
    x_vals, y_vals, z_vals = func(*coords)
    base_shape = np.asarray(coords[0]).shape
    x_vals = _broadcast_to(x_vals, base_shape)
    y_vals = _broadcast_to(y_vals, base_shape)
    z_vals = _broadcast_to(z_vals, base_shape)
    positions = np.stack([x_vals, y_vals, z_vals], axis=-1).reshape(-1, 3)
    return PointSamples(positions=positions.astype(np.float32))


def _broadcast_to(values: np.ndarray, shape: tuple[int, ...]) -> np.ndarray:
    array = np.asarray(values)
    if array.shape != shape:
        return np.broadcast_to(array, shape)
    return array
