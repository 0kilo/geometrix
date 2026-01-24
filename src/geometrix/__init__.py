"""Top-level package for geometrix."""

from .api import (
    GeomProgram,
    canonicalize,
    geom,
    latex,
    latex_equation,
    llm_solve,
    line,
    mesh,
    points,
    show,
    simplify,
    solve,
)
from .coords import cylindrical_to_cartesian, lorentz_metric, spherical_to_cartesian

__all__ = [
    "geom",
    "show",
    "latex",
    "latex_equation",
    "simplify",
    "canonicalize",
    "solve",
    "llm_solve",
    "points",
    "line",
    "mesh",
    "GeomProgram",
    "cylindrical_to_cartesian",
    "spherical_to_cartesian",
    "lorentz_metric",
]
