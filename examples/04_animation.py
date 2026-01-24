# Example: animate a surface over time with a simple parameter update.
# Shows how to build frame-by-frame visuals.
import numpy as np

from geometrix.animation import Animation, Frame
from geometrix.api import SceneBundle, show
from geometrix.scene.build import build_surface_scene

# Initial surface positions (10x10 grid flattened).
# Initial surface positions (10x10 grid flattened).
positions = np.zeros((100, 3), dtype=np.float32)
# Scene definition for the surface grid.
scene = build_surface_scene(positions, (10, 10))

# Two frames: base surface and an offset version.
frames = [
    Frame(t=0.0, arrays={"positions": positions}),
    Frame(t=1.0, arrays={"positions": positions + 0.2}),
]

# Render with animation playback.
show(
    SceneBundle(scene=scene, arrays={"positions": positions}),
    animation=Animation(frames, fps=24),
)
