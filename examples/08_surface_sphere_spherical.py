# Example: sphere surface in spherical coordinates.
# Demonstrates coordinate helpers for math users.
import sympy as sp

from geometrix import show, spherical_to_cartesian
from geometrix.api import SceneBundle
from geometrix.sample.domains import Domain
from geometrix.sample.surface import sample_surface_grid
from geometrix.scene.build import build_surface_scene
from geometrix.symbolic.compile import compile_vector

# Spherical coordinates (r, theta, phi).
r, theta, phi = sp.symbols("r theta phi")
# Convert to Cartesian expressions.
x_expr, y_expr, z_expr = spherical_to_cartesian(r, theta, phi)
# Fix radius to 1 for the unit sphere.
x_expr = x_expr.subs(r, 1.0)
y_expr = y_expr.subs(r, 1.0)
z_expr = z_expr.subs(r, 1.0)

# Compile the parametric surface.
compiled = compile_vector([x_expr, y_expr, z_expr], [theta, phi])
# Parameter domains for the angles.
domains = [Domain("theta", 0.0, sp.pi.evalf()), Domain("phi", 0.0, 2 * sp.pi.evalf())]
# Sampling resolution for each parameter.
counts = [50, 80]

# Sample the surface positions on the grid.
surface = sample_surface_grid(compiled, domains, counts)
# Build the scene from sampled positions.
scene = build_surface_scene(surface.positions, surface.grid_shape)
# Render the scene.
show(SceneBundle(scene=scene, arrays={"positions": surface.positions}))
