"""Parse the minimal DSL into a SymbolicIR."""

from __future__ import annotations

import re
from collections.abc import Iterable

from geometrix.ir.model import Definition, DefinitionKind, RenderRequest, SymbolicIR

_DEFINE_RE = re.compile(r"^(?P<lhs>[^=]+)=(?P<rhs>.+)$")
_CALL_RE = re.compile(r"^(?P<name>\w+)\((?P<args>[^)]*)\)$")


class DSLParseError(ValueError):
    pass


def parse_dsl(text: str) -> SymbolicIR:
    ir = SymbolicIR()
    for raw_line in _iter_lines(text):
        line = raw_line.strip()
        if line.startswith("coords:"):
            ir.coords = _parse_coords(line)
            continue
        if line.startswith("params:"):
            ir.params = _parse_params(line)
            continue
        if line.startswith("render:"):
            ir.render_requests.append(_parse_render(line))
            continue
        if "=" in line:
            definition = _parse_definition(line)
            ir.definitions[definition.name] = definition
            continue
        raise DSLParseError(f"Unknown DSL statement: {line}")
    return ir


def _iter_lines(text: str) -> Iterable[str]:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        yield stripped


def _parse_coords(line: str) -> list[str]:
    _, payload = line.split(":", 1)
    coords = [token for token in payload.strip().split() if token]
    if not coords:
        raise DSLParseError("coords must list at least one symbol")
    return coords


def _parse_params(line: str) -> dict[str, float]:
    _, payload = line.split(":", 1)
    params: dict[str, float] = {}
    for token in payload.split():
        if not token:
            continue
        if "=" not in token:
            raise DSLParseError(f"Invalid param assignment: {token}")
        key, value = token.split("=", 1)
        try:
            params[key] = float(value)
        except ValueError as exc:
            raise DSLParseError(f"Invalid param value for {key}: {value}") from exc
    return params


def _parse_definition(line: str) -> Definition:
    match = _DEFINE_RE.match(line)
    if not match:
        raise DSLParseError(f"Invalid definition: {line}")
    lhs = match.group("lhs").strip()
    rhs = match.group("rhs").strip()
    call_match = _CALL_RE.match(lhs)
    if call_match:
        name = call_match.group("name")
        args = tuple(
            arg.strip() for arg in call_match.group("args").split(",") if arg.strip()
        )
    else:
        name = lhs
        args = tuple()
    kind = _infer_kind(rhs)
    return Definition(name=name, args=args, expression=rhs, kind=kind)


def _infer_kind(expression: str) -> DefinitionKind:
    expr = expression.strip()
    if expr.startswith("(") and "," in expr and expr.endswith(")"):
        return DefinitionKind.VECTOR
    return DefinitionKind.SCALAR


def _parse_render(line: str) -> RenderRequest:
    _, payload = line.split(":", 1)
    parts = [token for token in payload.strip().split() if token]
    if len(parts) < 2:
        raise DSLParseError("render requires a kind and target")
    kind, target, *rest = parts
    options = _parse_render_options(rest)
    return RenderRequest(kind=kind, target=target, options=options)


def _parse_render_options(tokens: list[str]) -> dict[str, str]:
    options: dict[str, str] = {}
    idx = 0
    while idx < len(tokens):
        token = tokens[idx]
        if "=" in token:
            key, value = token.split("=", 1)
            options[key] = value
            idx += 1
            continue
        if token == "domain" and idx + 2 < len(tokens):
            options["domain"] = f"{tokens[idx + 1]} {tokens[idx + 2]}"
            idx += 3
            continue
        if token == "res" and idx + 2 < len(tokens):
            options["res"] = f"{tokens[idx + 1]} {tokens[idx + 2]}"
            idx += 3
            continue
        options[f"arg_{idx}"] = token
        idx += 1
    return options
