# Example: basic tensor operations and rendered surface output.
# Focus: how symbolic tensor math feeds the grapher.
import sympy as sp

from geometrix.symbolic.ops import (
    auto_from_embedding,
    gaussian_curvature,
    laplace_beltrami,
)
from geometrix.transport.latex_viewer import show_latex

# Surface parameters.
u, v = sp.symbols("u v")
# Unit sphere embedding in R^3.
X = [sp.sin(u) * sp.cos(v), sp.sin(u) * sp.sin(v), sp.cos(u)]

# Metric induced by the embedding.
g = auto_from_embedding(X, [u, v])
# Gaussian curvature from the metric.
K = sp.simplify(gaussian_curvature(g, [u, v]))
# Render the curvature in LaTeX.
show_latex(sp.latex(K))

# Example scalar field on the surface.
f = u**2 + v**2
# Laplace-Beltrami of the scalar field.
lb = sp.simplify(laplace_beltrami(g, [u, v], f))
print(lb)
