import sympy as sp

from geometrix import show, spherical_to_cartesian
from geometrix.api import SceneBundle
from geometrix.sample.domains import Domain
from geometrix.sample.surface import sample_surface_grid
from geometrix.scene.build import build_surface_scene
from geometrix.symbolic.compile import compile_vector

r, theta, phi = sp.symbols("r theta phi")
x_expr, y_expr, z_expr = spherical_to_cartesian(r, theta, phi)
x_expr = x_expr.subs(r, 1.0)
y_expr = y_expr.subs(r, 1.0)
z_expr = z_expr.subs(r, 1.0)

compiled = compile_vector([x_expr, y_expr, z_expr], [theta, phi])
domains = [Domain("theta", 0.0, sp.pi.evalf()), Domain("phi", 0.0, 2 * sp.pi.evalf())]
counts = [50, 80]

surface = sample_surface_grid(compiled, domains, counts)
scene = build_surface_scene(surface.positions, surface.grid_shape)
show(SceneBundle(scene=scene, arrays={"positions": surface.positions}))
