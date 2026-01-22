import sympy as sp

from geometrix.symbolic.ops import (
    auto_from_embedding,
    gaussian_curvature,
    laplace_beltrami,
)
from geometrix.transport.latex_viewer import show_latex

u, v = sp.symbols("u v")
X = [sp.sin(u) * sp.cos(v), sp.sin(u) * sp.sin(v), sp.cos(u)]

g = auto_from_embedding(X, [u, v])
K = sp.simplify(gaussian_curvature(g, [u, v]))
show_latex(sp.latex(K))

f = u**2 + v**2
lb = sp.simplify(laplace_beltrami(g, [u, v], f))
print(lb)
