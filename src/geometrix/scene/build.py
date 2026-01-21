"""Build SceneSpec objects from sampled data."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from geometrix.scene.spec import BufferSpec, ObjectSpec, SceneSpec


@dataclass(frozen=True)
class BufferRegistry:
    specs: dict[str, BufferSpec]
    arrays: dict[str, np.ndarray]


def build_surface_scene(
    positions: np.ndarray, grid_shape: tuple[int, int]
) -> SceneSpec:
    buffers = {
        "positions": positions.astype(np.float32),
    }
    registry = build_buffers(buffers)
    obj = ObjectSpec(
        type="surface_grid",
        name="surface",
        buffers={"positions": "positions"},
        metadata={"grid": {"Nu": grid_shape[0], "Nv": grid_shape[1]}},
    )
    return SceneSpec(version="1.0", objects=[obj], buffers=registry.specs)


def build_buffers(arrays: dict[str, np.ndarray]) -> BufferRegistry:
    specs: dict[str, BufferSpec] = {}
    for key, array in arrays.items():
        specs[key] = BufferSpec(dtype=str(array.dtype), shape=tuple(array.shape))
    return BufferRegistry(specs=specs, arrays=arrays)
