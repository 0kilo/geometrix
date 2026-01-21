"""Public API for geometrix."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import sympy as sp

from geometrix.ir.model import DefinitionKind
from geometrix.parse.dsl_parser import parse_dsl
from geometrix.sample.domains import Domain
from geometrix.sample.surface import sample_surface_grid
from geometrix.scene.build import build_surface_scene
from geometrix.symbolic.compile import compile_vector
from geometrix.transport.html import render_html
from geometrix.transport.widget import build_widget


@dataclass
class SceneBundle:
    scene: Any
    arrays: dict[str, Any]


@dataclass
class GeomProgram:
    """Minimal DSL program wrapper."""

    source: str
    ir: Any

    def build_scene(self) -> SceneBundle:
        return _build_scene_from_ir(self.ir)

    def show(self, **kwargs: Any) -> None:
        bundle = self.build_scene()
        show(bundle, **kwargs)


def geom(text: str) -> GeomProgram:
    """Parse DSL text into a GeomProgram."""

    ir = parse_dsl(text)
    return GeomProgram(source=text, ir=ir)


def show(scene_or_program: Any, **kwargs: Any) -> None:
    """Render a scene or program in a notebook using widget or HTML fallback."""

    if isinstance(scene_or_program, GeomProgram):
        bundle = scene_or_program.build_scene()
        return show(bundle, **kwargs)
    if isinstance(scene_or_program, SceneBundle):
        bundle = scene_or_program
    else:
        raise TypeError("Expected GeomProgram or SceneBundle")

    height = kwargs.get("height", 420)
    use_widget = bool(kwargs.get("use_widget", False))
    if use_widget:
        widget = build_widget(bundle.scene, bundle.arrays, height=height)
        try:
            from IPython.display import display
        except ImportError as exc:
            raise RuntimeError("IPython is required to render the scene") from exc
        display(widget)
        return

    html_bundle = render_html(bundle.scene, bundle.arrays, height=height)
    try:
        from IPython.display import HTML, display
    except ImportError as exc:
        raise RuntimeError("IPython is required to render the scene") from exc
    display(HTML(html_bundle.html))


def _build_scene_from_ir(ir) -> SceneBundle:
    if not ir.render_requests:
        raise ValueError("No render requests found")
    request = ir.render_requests[0]
    if request.kind != "surface":
        raise ValueError("Only surface render requests are supported in v1")

    definition = ir.definitions.get(request.target)
    if not definition or definition.kind != DefinitionKind.VECTOR:
        raise ValueError("Surface render expects a vector definition")

    coord_symbols = [sp.Symbol(name) for name in ir.coords]
    param_symbols = {sp.Symbol(name): value for name, value in ir.params.items()}

    exprs = _parse_vector_expr(definition.expression, ir.coords, list(ir.params.keys()))
    exprs = [expr.subs(param_symbols) for expr in exprs]

    compiled = compile_vector(exprs, coord_symbols)
    domains = _parse_domains(request.options, ir)
    counts = _parse_res(request.options)
    surface = sample_surface_grid(compiled, domains, counts)

    scene = build_surface_scene(surface.positions, surface.grid_shape)
    arrays = {"positions": surface.positions}
    return SceneBundle(scene=scene, arrays=arrays)


def _parse_vector_expr(
    expr: str, coords: list[str], params: list[str]
) -> list[sp.Expr]:
    stripped = expr.strip().lstrip("(").rstrip(")")
    parts = [part.strip() for part in stripped.split(",") if part.strip()]
    symbols = {name: sp.Symbol(name) for name in coords + params}
    return [sp.sympify(part, locals=symbols) for part in parts]


def _parse_domains(options: dict[str, str], ir) -> list[Domain]:
    domain_text = options.get("domain")
    if not domain_text:
        return [Domain(name, 0.0, 1.0) for name in ir.coords]
    entries = domain_text.split()
    domains = []
    for entry in entries:
        name, rng = entry.split(":", 1)
        rng = rng.strip().lstrip("[").rstrip("]")
        start_text, stop_text = [part.strip() for part in rng.split(",", 1)]
        start = float(sp.sympify(start_text, locals=ir.params))
        stop = float(sp.sympify(stop_text, locals=ir.params))
        domains.append(Domain(name, start, stop))
    return domains


def _parse_res(options: dict[str, str]) -> list[int]:
    if "res" not in options:
        return [50, 50]
    parts = options["res"].split()
    return [int(parts[0]), int(parts[1])]
