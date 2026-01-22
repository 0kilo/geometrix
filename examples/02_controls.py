from dataclasses import replace

import numpy as np

from geometrix.api import SceneBundle, show
from geometrix.scene.build import build_surface_scene

u = np.linspace(0.0, 1.0, 20)
v = np.linspace(0.0, 1.0, 20)
uu, vv = np.meshgrid(u, v, indexing="ij")
positions = (
    np.stack([uu, vv, 0 * uu], axis=-1).reshape(-1, 3).astype(np.float32)
)

scene = build_surface_scene(positions, (20, 20))
scene = replace(
    scene,
    axes={"visible": True},
    grid={"visible": True},
    controls={"lighting": 1.1},
    legend={"visible": True, "items": ["Surface"]},
    gizmo={"visible": True},
)

show(SceneBundle(scene=scene, arrays={"positions": positions}))
