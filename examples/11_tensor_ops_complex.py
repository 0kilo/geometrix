# Example: more complex tensor operations (composition, contractions).
# Useful for differential geometry workflows.
import sympy as sp

from geometrix.symbolic.ops import (
    auto_from_embedding,
    christoffel_symbols,
    ricci_tensor,
    riemann_tensor,
    scalar_curvature,
)
from geometrix.transport.latex_viewer import show_latex

# Angular parameters for the sphere.
theta, phi = sp.symbols("theta phi")
# Sphere embedding for metric/tensor calculations.
embedding = [
    sp.sin(theta) * sp.cos(phi),
    sp.sin(theta) * sp.sin(phi),
    sp.cos(theta),
]
# Metric induced by the embedding.
metric = auto_from_embedding(embedding, [theta, phi])
# Connection and curvature tensors.
Gamma = christoffel_symbols(metric, [theta, phi])
Riemann = riemann_tensor(metric, [theta, phi])
Ricci = ricci_tensor(metric, [theta, phi])
R = scalar_curvature(metric, [theta, phi])

# Render selected tensor components in LaTeX.
show_latex(sp.latex(metric), inline=False)
show_latex(sp.latex(Gamma[0, 1, 1]), inline=True)
show_latex(sp.latex(Riemann[0, 1, 0, 1]), inline=True)
show_latex(sp.latex(Ricci[0, 0]), inline=True)
show_latex(sp.latex(sp.simplify(R)), inline=True)
