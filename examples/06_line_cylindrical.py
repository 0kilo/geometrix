import numpy as np

from geometrix import show
from geometrix.api import SceneBundle
from geometrix.sample.curves import sample_curve
from geometrix.sample.domains import Domain
from geometrix.scene.build import build_line_scene


def helix(t_vals: np.ndarray):
    r = 1.0
    phi = t_vals
    z = 0.15 * t_vals
    x_vals = r * np.cos(phi)
    y_vals = r * np.sin(phi)
    return x_vals, y_vals, z


domain = Domain("t", 0.0, 6.0 * np.pi)
samples = sample_curve(helix, domain, 300)

scene = build_line_scene(samples.positions)
show(SceneBundle(scene=scene, arrays={"positions": samples.positions}))
