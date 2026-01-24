# Example: render a line defined in cylindrical coordinates.
# Converts to Cartesian for visualization.
import numpy as np

from geometrix import show
from geometrix.api import SceneBundle
from geometrix.sample.curves import sample_curve
from geometrix.sample.domains import Domain
from geometrix.scene.build import build_line_scene


# Helix in cylindrical coordinates (r, phi, z).
def helix(t_vals: np.ndarray):
    # Fixed radius for the helix.
    r = 1.0
    # Angle parameter for rotation.
    phi = t_vals
    # Height as a linear function of t.
    z = 0.15 * t_vals
    # Convert to Cartesian coordinates.
    x_vals = r * np.cos(phi)
    y_vals = r * np.sin(phi)
    return x_vals, y_vals, z


# Parameter domain for the helix.
domain = Domain("t", 0.0, 6.0 * np.pi)
# Sample the curve into positions.
samples = sample_curve(helix, domain, 300)

# Build and render the line scene.
scene = build_line_scene(samples.positions)
show(SceneBundle(scene=scene, arrays={"positions": samples.positions}))
