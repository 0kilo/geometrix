# Example: LLM-assisted solving with JSON LaTeX responses.
# Uses built-in prompts and validation.
import os

import sympy as sp

from geometrix import latex, llm_solve, show
from geometrix.api import SceneBundle
from geometrix.symbolic import LLMConfig
from geometrix.sample.domains import Domain
from geometrix.sample.surface import sample_surface_grid
from geometrix.scene.build import build_surface_scene
from geometrix.symbolic.compile import compile_vector
from google.colab import userdata

# Provider/model configuration for LiteLLM.
config = LLMConfig(provider="gemini", model="gemini-3-flash-preview", api_key=userdata.get('GEMINI_API_KEY'))
# LLM-assisted solve with default prompts + validation.
live = llm_solve(
    "x^2 + y^2 + z^2 = 1",
    config=config,
    response_type="minimal",
    wants_graph=True,
    graph_dim=3,
)
print("live:", live.data.solution)

# Pipe the LLM graph field into the render pipeline.
graph_latex = live.data.graph
lhs, rhs = graph_latex.split("=", 1)
rhs = rhs.strip()

x, y = sp.symbols("x y")
z_expr = latex(rhs)

domains = [Domain("x", -1.0, 1.0), Domain("y", -1.0, 1.0)]
counts = [80, 80]

compiled = compile_vector([x, y, z_expr], [x, y])
surface = sample_surface_grid(compiled, domains, counts)
scene = build_surface_scene(surface.positions, surface.grid_shape)
show(SceneBundle(scene=scene, arrays={"positions": surface.positions}))
