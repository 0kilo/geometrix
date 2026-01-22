import numpy as np

from geometrix.animation import Animation, Frame
from geometrix.api import SceneBundle, show
from geometrix.scene.build import build_surface_scene

positions = np.zeros((100, 3), dtype=np.float32)
scene = build_surface_scene(positions, (10, 10))

frames = [
    Frame(t=0.0, arrays={"positions": positions}),
    Frame(t=1.0, arrays={"positions": positions + 0.2}),
]

show(
    SceneBundle(scene=scene, arrays={"positions": positions}),
    animation=Animation(frames, fps=24),
)
