# Example: surface defined with LaTeX input.
# The LaTeX is parsed, simplified, then graphed.
import sympy as sp

from geometrix import latex, show
from geometrix.api import SceneBundle
from geometrix.sample.domains import Domain
from geometrix.sample.surface import sample_surface_grid
from geometrix.scene.build import build_surface_scene
from geometrix.symbolic.compile import compile_vector

# Surface parameters.
u, v = sp.symbols("u v")

# Math-first: start with LaTeX strings, then parse to SymPy.
latex_x = "u"  # LaTeX for the x-coordinate.
latex_y = "v"  # LaTeX for the y-coordinate.
latex_z = "\\sin(u)\\cos(v)"  # LaTeX for the z-coordinate.

# Parse LaTeX into SymPy expressions (and show LaTeX output).
x_expr = latex(latex_x, show_latex_expr=True)
y_expr = latex(latex_y, show_latex_expr=True)
z_expr = latex(latex_z, show_latex_expr=True)

# Compile into a numeric sampler.
compiled = compile_vector([x_expr, y_expr, z_expr], [u, v])
# Parameter domains for sampling.
domains = [
    Domain("u", -sp.pi.evalf(), sp.pi.evalf()),
    Domain("v", -sp.pi.evalf(), sp.pi.evalf()),
]
# Grid resolution along each parameter.
counts = [60, 60]

# Sample and render the surface.
surface = sample_surface_grid(compiled, domains, counts)
scene = build_surface_scene(surface.positions, surface.grid_shape)
show(SceneBundle(scene=scene, arrays={"positions": surface.positions}))
