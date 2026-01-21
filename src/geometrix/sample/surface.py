"""Surface sampling utilities."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from geometrix.sample.domains import Domain, meshgrid


@dataclass(frozen=True)
class SurfaceGrid:
    positions: np.ndarray
    grid_shape: tuple[int, int]


def sample_surface_grid(
    func: Callable[..., tuple[np.ndarray, np.ndarray, np.ndarray]],
    domains: list[Domain],
    counts: list[int],
) -> SurfaceGrid:
    if len(domains) != 2 or len(counts) != 2:
        raise ValueError("surface sampling expects two domains and counts")
    u_grid, v_grid = meshgrid(domains, counts)
    x_vals, y_vals, z_vals = func(u_grid, v_grid)
    x_vals = _broadcast_to(x_vals, u_grid.shape)
    y_vals = _broadcast_to(y_vals, u_grid.shape)
    z_vals = _broadcast_to(z_vals, u_grid.shape)
    positions = np.stack([x_vals, y_vals, z_vals], axis=-1).reshape(-1, 3)
    return SurfaceGrid(
        positions=positions.astype(np.float32),
        grid_shape=(counts[0], counts[1]),
    )


def _broadcast_to(values: np.ndarray, shape: tuple[int, ...]) -> np.ndarray:
    array = np.asarray(values)
    if array.shape != shape:
        return np.broadcast_to(array, shape)
    return array
