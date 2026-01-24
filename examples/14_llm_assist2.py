# Example: LLM-assisted solving (full) with a wave-like surface.
# Shows a step-by-step response and graphs the resulting surface.
import sympy as sp
from google.colab import userdata

from geometrix import latex, llm_solve, show
from geometrix.api import SceneBundle
from geometrix.sample.domains import Domain
from geometrix.sample.surface import sample_surface_grid
from geometrix.scene.build import build_surface_scene
from geometrix.symbolic.compile import compile_vector
from geometrix.symbolic.llm import LLMConfig

# Provider/model configuration for LiteLLM.
config = LLMConfig(
    provider="gemini",
    model="gemini-3-flash-preview",
    api_key=userdata.get("GEMINI_API_KEY"),
)
# LLM-assisted solve with full derivation + validation.
live = llm_solve(
    "z_{xx}+z_{yy}+2z=0",
    config=config,
    response_type="full",
    wants_graph=True,
    graph_dim=3,
)

# Use the graph expression (expects z = f(x,y)).
graph_latex = live.data.graph
lhs, rhs = graph_latex.split("=", 1)
rhs = rhs.strip()

# Parse the explicit surface from LaTeX.
x, y = sp.symbols("x y")
z_expr = latex(rhs)

# Graph domain for a wave surface.
domains = [Domain("x", 0.0, 2 * sp.pi.evalf()), Domain("y", 0.0, 2 * sp.pi.evalf())]
counts = [120, 120]

# Sample and render the surface.
compiled = compile_vector([x, y, z_expr], [x, y])
surface = sample_surface_grid(compiled, domains, counts)
scene = build_surface_scene(surface.positions, surface.grid_shape)
show(SceneBundle(scene=scene, arrays={"positions": surface.positions}))
