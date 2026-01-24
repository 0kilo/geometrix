# Example: show a surface with UI controls (axes, grid, lighting).
# Intended for math users: toggle visual guides and adjust lighting.
from dataclasses import replace

import numpy as np

from geometrix.api import SceneBundle, show
from geometrix.scene.build import build_surface_scene

# Parameter grid for the surface domain.
u = np.linspace(0.0, 1.0, 20)
v = np.linspace(0.0, 1.0, 20)
# Meshgrid of the parameter domain.
uu, vv = np.meshgrid(u, v, indexing="ij")
# Flat plane z=0 sampled on the grid.
positions = (
    np.stack([uu, vv, 0 * uu], axis=-1).reshape(-1, 3).astype(np.float32)
)

# Build the surface scene from sampled positions.
scene = build_surface_scene(positions, (20, 20))
# Update UI overlays and controls.
scene = replace(
    scene,
    axes={"visible": True},
    grid={"visible": True},
    controls={"lighting": 1.1},
    legend={"visible": True, "items": ["Surface"]},
    gizmo={"visible": True},
)

# Render the scene with the sampled positions.
show(SceneBundle(scene=scene, arrays={"positions": positions}))
