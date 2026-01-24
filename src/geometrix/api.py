"""Public API for geometrix."""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import sympy as sp

from geometrix.ir.model import DefinitionKind
from geometrix.parse.dsl_parser import parse_dsl
from geometrix.parse.latex_parser import LatexParseError, parse_latex_expr
from geometrix.sample.domains import Domain, validate_domains
from geometrix.sample.surface import sample_surface_grid
from geometrix.scene.build import (
    build_line_scene,
    build_mesh_scene,
    build_points_scene,
    build_surface_scene,
)
from geometrix.symbolic.compile import compile_vector
from geometrix.symbolic.llm import LLMConfig, request_llm_json
from geometrix.symbolic.llm_prompts import build_request_prompt, build_system_prompt
from geometrix.symbolic.llm_validate import ValidationResult, validate_llm_response
from geometrix.symbolic.solve import canonicalize_expr, simplify_expr, solve_constraints
from geometrix.transport.html import render_html
from geometrix.transport.latex_viewer import show_latex


@dataclass
class SceneBundle:
    """Container for a SceneSpec plus its backing arrays."""

    scene: Any
    arrays: dict[str, Any]


@dataclass
class GeomProgram:
    """Minimal DSL program wrapper."""

    source: str
    ir: Any

    def build_scene(self) -> SceneBundle:
        """Compile the DSL into a SceneBundle."""

        return _build_scene_from_ir(self.ir)

    def show(self, **kwargs: Any) -> None:
        """Render the program in a notebook."""

        bundle = self.build_scene()
        show(bundle, **kwargs)


def geom(text: str) -> GeomProgram:
    """Parse DSL text into a GeomProgram."""

    ir = parse_dsl(text)
    return GeomProgram(source=text, ir=ir)


def latex(
    expression: str,
    *,
    allowed_symbols: bool | Iterable[str] = True,
    show_latex_expr: bool = False,
    inline: bool = True,
):
    """Parse a LaTeX expression into a SymPy expression.

    Args:
        expression: LaTeX string to parse.
        allowed_symbols: True to infer symbols from the expression, False for
            none, or an explicit list of allowed symbols.
        show_latex_expr: If True, render the LaTeX in the output cell.
        inline: Render the LaTeX inline (default) or in block mode.
    """

    if show_latex_expr:
        show_latex(expression, inline=inline)
    symbols = _resolve_allowed_symbols(expression, allowed_symbols)
    try:
        return parse_latex_expr(expression, allowed_symbols=symbols)
    except LatexParseError as exc:
        raise ValueError(str(exc)) from exc


def latex_equation(
    expression: str,
    *,
    allowed_symbols: bool | Iterable[str] = True,
    show_latex_expr: bool = False,
    inline: bool = True,
) -> sp.Equality:
    """Parse a LaTeX equation into a SymPy Equality."""

    if "=" in expression:
        lhs_text, rhs_text = expression.split("=", 1)
        lhs = latex(
            lhs_text.strip(),
            allowed_symbols=allowed_symbols,
            show_latex_expr=show_latex_expr,
            inline=inline,
        )
        rhs = latex(
            rhs_text.strip(),
            allowed_symbols=allowed_symbols,
            show_latex_expr=show_latex_expr,
            inline=inline,
        )
        return sp.Eq(lhs, rhs)
    return sp.Eq(
        latex(
            expression,
            allowed_symbols=allowed_symbols,
            show_latex_expr=show_latex_expr,
            inline=inline,
        ),
        0,
    )


def simplify(
    expr: sp.Expr,
    *,
    mode: str = "simplify",
) -> sp.Expr:
    """Simplify a SymPy expression using the requested mode."""

    return simplify_expr(expr, mode=mode)


def canonicalize(expr: sp.Expr) -> sp.Expr:
    """Canonicalize a SymPy expression for stable comparison."""

    return canonicalize_expr(expr)


def solve(
    equations: Iterable[sp.Expr | sp.Equality],
    symbols: Iterable[sp.Symbol],
    *,
    dict: bool = False,
) -> list[dict[sp.Symbol, sp.Expr]] | list[sp.Expr]:
    """Solve algebraic constraints using SymPy."""

    return solve_constraints(equations, symbols, dict=dict)


def llm_solve(
    problem_latex: str,
    *,
    config: LLMConfig,
    response_type: str = "minimal",
    wants_graph: bool = False,
    graph_dim: int | None = None,
    system_prompt: str | None = None,
    request_prompt: str | None = None,
    require_domains: bool = False,
    strict_latex: bool = False,
    enforce_json: bool = True,
    max_retries: int = 0,
    extra_params: dict[str, Any] | None = None,
    show_steps: bool | None = None,
) -> ValidationResult:
    """Solve a LaTeX problem using an LLM with default prompts and validation."""

    logger = logging.getLogger("geometrix.llm")
    system_prompt = system_prompt or build_system_prompt()
    request_prompt = request_prompt or build_request_prompt(
        response_type=response_type,
        problem_latex=problem_latex,
        wants_graph=wants_graph,
        graph_dim=graph_dim,
    )
    raw = request_llm_json(
        config,
        system_prompt,
        request_prompt,
        enforce_json=enforce_json,
        max_retries=max_retries,
        extra_params=extra_params,
    )
    try:
        result = validate_llm_response(
            raw,
            wants_graph=wants_graph,
            require_domains=require_domains,
            strict_latex=strict_latex,
        )
    except ValueError as exc:
        print(raw)
        logger.error("Invalid LLM response JSON: %s", raw)
        raise exc
    if show_steps is None:
        show_steps = response_type == "full"
    if show_steps and result.data.response_type == "full":
        if not result.data.steps:
            print("LLM derivation steps are empty.")
        try:
            from geometrix.transport.latex_viewer import show_latex
        except Exception:
            for step in result.data.steps:
                print(step)
            print(result.data.solution)
            return result
        for step in result.data.steps:
            show_latex(step, inline=False)
        show_latex(result.data.solution, inline=False)
    return result


def show(scene_or_program: Any, **kwargs: Any) -> None:
    """Render a scene or program in a notebook using the HTML renderer.

    Args:
        scene_or_program: GeomProgram or SceneBundle instance.
        height: Optional output height in pixels.
        animation: Optional Animation instance for frame updates.
    """

    if isinstance(scene_or_program, GeomProgram):
        bundle = scene_or_program.build_scene()
        return show(bundle, **kwargs)
    if isinstance(scene_or_program, SceneBundle):
        bundle = scene_or_program
    else:
        raise TypeError("Expected GeomProgram or SceneBundle")

    height = kwargs.get("height", 420)
    animation = kwargs.get("animation")
    html_bundle = render_html(
        bundle.scene, bundle.arrays, height=height, animation=animation
    )
    try:
        from IPython.display import HTML, display
    except ImportError as exc:
        raise RuntimeError("IPython is required to render the scene") from exc
    display(HTML(html_bundle.html))


def _resolve_allowed_symbols(
    expression: str, allowed_symbols: bool | Iterable[str]
) -> list[str]:
    if allowed_symbols is True:
        tokens = re.findall(r"\b[A-Za-z]+\b", expression)
        return sorted(set(tokens))
    if allowed_symbols is False or allowed_symbols is None:
        return []
    return list(allowed_symbols)


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
    validate_domains(domains)
    _validate_params(ir.params)
    counts = _parse_res(request.options)
    surface = sample_surface_grid(compiled, domains, counts)

    scene = build_surface_scene(surface.positions, surface.grid_shape)
    arrays = {"positions": surface.positions}
    return SceneBundle(scene=scene, arrays=arrays)


def _parse_vector_expr(
    expr: str, coords: list[str], params: list[str]
) -> list[sp.Expr]:
    stripped = expr.strip()
    if stripped.startswith("(") and stripped.endswith(")"):
        stripped = stripped[1:-1]
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


def _validate_params(params: dict[str, float]) -> None:
    for key, value in params.items():
        if not float("-inf") < float(value) < float("inf"):
            raise ValueError(f"Param {key} must be finite")


def points(positions: Any, values: Any | None = None) -> SceneBundle:
    """Build a point cloud SceneBundle from positions and optional values."""

    scene = build_points_scene(positions, values=values)
    arrays = {"positions": positions}
    if values is not None:
        arrays["values"] = values
    return SceneBundle(scene=scene, arrays=arrays)


def line(positions: Any, values: Any | None = None) -> SceneBundle:
    """Build a line SceneBundle from positions and optional values."""

    scene = build_line_scene(positions, values=values)
    arrays = {"positions": positions}
    if values is not None:
        arrays["values"] = values
    return SceneBundle(scene=scene, arrays=arrays)


def mesh(
    vertices: Any, faces: Any | None = None, values: Any | None = None
) -> SceneBundle:
    """Build a mesh SceneBundle from vertices, faces, and optional values."""

    scene = build_mesh_scene(vertices, faces=faces, values=values)
    arrays = {"vertices": vertices}
    if faces is not None:
        arrays["faces"] = faces
    if values is not None:
        arrays["values"] = values
    return SceneBundle(scene=scene, arrays=arrays)
