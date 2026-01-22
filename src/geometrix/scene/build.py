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


def build_points_scene(
    positions: np.ndarray, values: np.ndarray | None = None
) -> SceneSpec:
    buffers: dict[str, np.ndarray] = {"positions": positions.astype(np.float32)}
    buffer_map = {"positions": "positions"}
    if values is not None:
        buffers["values"] = values.astype(np.float32)
        buffer_map["values"] = "values"
    registry = build_buffers(buffers)
    obj = ObjectSpec(type="points", name="points", buffers=buffer_map)
    return SceneSpec(version="1.0", objects=[obj], buffers=registry.specs)


def build_line_scene(
    positions: np.ndarray, values: np.ndarray | None = None
) -> SceneSpec:
    buffers: dict[str, np.ndarray] = {"positions": positions.astype(np.float32)}
    buffer_map = {"positions": "positions"}
    if values is not None:
        buffers["values"] = values.astype(np.float32)
        buffer_map["values"] = "values"
    registry = build_buffers(buffers)
    obj = ObjectSpec(type="line", name="line", buffers=buffer_map)
    return SceneSpec(version="1.0", objects=[obj], buffers=registry.specs)


def build_mesh_scene(
    vertices: np.ndarray,
    faces: np.ndarray | None = None,
    values: np.ndarray | None = None,
) -> SceneSpec:
    buffers: dict[str, np.ndarray] = {"vertices": vertices.astype(np.float32)}
    buffer_map = {"vertices": "vertices"}
    if faces is not None:
        buffers["faces"] = faces.astype(np.uint32)
        buffer_map["faces"] = "faces"
    if values is not None:
        buffers["values"] = values.astype(np.float32)
        buffer_map["values"] = "values"
    registry = build_buffers(buffers)
    obj = ObjectSpec(type="mesh", name="mesh", buffers=buffer_map)
    return SceneSpec(version="1.0", objects=[obj], buffers=registry.specs)


def build_buffers(arrays: dict[str, np.ndarray]) -> BufferRegistry:
    specs: dict[str, BufferSpec] = {}
    for key, array in arrays.items():
        specs[key] = BufferSpec(dtype=str(array.dtype), shape=tuple(array.shape))
    return BufferRegistry(specs=specs, arrays=arrays)
