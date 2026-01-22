import numpy as np

from geometrix import show
from geometrix.api import SceneBundle
from geometrix.scene.spec import BufferSpec, ObjectSpec, SceneSpec


def make_face(
    axis: str, value: float, n: int = 25
) -> tuple[np.ndarray, tuple[int, int]]:
    u = np.linspace(-1.0, 1.0, n)
    v = np.linspace(-1.0, 1.0, n)
    uu, vv = np.meshgrid(u, v, indexing="ij")
    if axis == "x":
        positions = np.stack([np.full_like(uu, value), uu, vv], axis=-1)
    elif axis == "y":
        positions = np.stack([uu, np.full_like(uu, value), vv], axis=-1)
    else:
        positions = np.stack([uu, vv, np.full_like(uu, value)], axis=-1)
    return positions.reshape(-1, 3).astype(np.float32), (n, n)


arrays = {}
objects = []
specs = {}

for axis in ("x", "y", "z"):
    for value in (-1.0, 1.0):
        key = f"positions_{axis}_{'neg' if value < 0 else 'pos'}"
        positions, grid_shape = make_face(axis, value)
        arrays[key] = positions
        specs[key] = BufferSpec(dtype=str(positions.dtype), shape=positions.shape)
        objects.append(
            ObjectSpec(
                type="surface_grid",
                name=f"face_{axis}_{value:+.0f}",
                buffers={"positions": key},
                metadata={"grid": {"Nu": grid_shape[0], "Nv": grid_shape[1]}},
            )
        )

scene = SceneSpec(version="1.0", objects=objects, buffers=specs)
show(SceneBundle(scene=scene, arrays=arrays))
