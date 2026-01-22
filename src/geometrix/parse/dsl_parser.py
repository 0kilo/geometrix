"""Parse the minimal DSL into a SymbolicIR."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import replace

from geometrix.ir.model import Definition, DefinitionKind, RenderRequest, SymbolicIR
from geometrix.ir.tensors import TensorMetadata, parse_tensor_name

_DEFINE_RE = re.compile(r"^(?P<lhs>[^=]+)=(?P<rhs>.+)$")
_CALL_RE = re.compile(r"^(?P<name>\w+)\((?P<args>[^)]*)\)$")
_TENSOR_RE = re.compile(r"[_^](\{[^}]+\}|\w+)")


class DSLParseError(ValueError):
    pass


def parse_dsl(text: str) -> SymbolicIR:
    """Parse DSL text into a SymbolicIR."""
    ir = SymbolicIR()
    for raw_line in _iter_lines(text):
        line = raw_line.strip()
        if line.startswith("coords:"):
            ir.coords = _parse_coords(line)
            ir.index_sets.setdefault("default", len(ir.coords))
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
            if definition.kind == DefinitionKind.TENSOR:
                _register_tensor_metadata(ir, definition)
            continue
        raise DSLParseError(f"Unknown DSL statement: {line}")
    _apply_time_defaults(ir)
    _finalize_tensor_metadata(ir)
    return ir


def _apply_time_defaults(ir: SymbolicIR) -> None:
    if ir.time_param in ir.params:
        ir.time_value = ir.params[ir.time_param]


def _iter_lines(text: str) -> Iterable[str]:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        yield stripped


def _parse_coords(line: str) -> list[str]:
    """Parse a coords declaration."""
    _, payload = line.split(":", 1)
    coords = [token for token in payload.strip().split() if token]
    if not coords:
        raise DSLParseError("coords must list at least one symbol")
    return coords


def _parse_params(line: str) -> dict[str, float]:
    """Parse a params declaration."""
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
    """Parse a scalar, vector, or tensor definition line."""
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
    kind = _infer_kind(lhs, rhs)
    return Definition(name=name, args=args, expression=rhs, kind=kind)


def _infer_kind(lhs: str, expression: str) -> DefinitionKind:
    if _is_tensor_lhs(lhs):
        return DefinitionKind.TENSOR
    expr = expression.strip()
    if expr.startswith("(") and "," in expr and expr.endswith(")"):
        return DefinitionKind.VECTOR
    return DefinitionKind.SCALAR


def _is_tensor_lhs(lhs: str) -> bool:
    return bool(_TENSOR_RE.search(lhs))


def _register_tensor_metadata(ir: SymbolicIR, definition: Definition) -> None:
    dim = len(ir.coords) if ir.coords else 0
    try:
        metadata = parse_tensor_name(definition.name, dim)
    except ValueError as exc:
        raise DSLParseError(str(exc)) from exc
    ir.tensor_metadata[definition.name] = metadata


def _finalize_tensor_metadata(ir: SymbolicIR) -> None:
    if not ir.tensor_metadata:
        return
    dim = len(ir.coords)
    if dim <= 0:
        raise DSLParseError("Tensor definitions require coords to infer dimensions")
    ir.index_sets.setdefault("default", dim)
    for name, metadata in list(ir.tensor_metadata.items()):
        if metadata.dim != dim:
            metadata = replace(metadata, dim=dim)
            ir.tensor_metadata[name] = metadata
        definition = ir.definitions.get(name)
        if definition:
            _validate_tensor_shape(definition.expression, metadata)


def _count_top_level_items(expr: str) -> int | None:
    text = expr.strip()
    if not (text.startswith("(") and text.endswith(")")):
        return None
    inner = text[1:-1].strip()
    if not inner:
        return 0
    depth = 0
    count = 1
    saw_comma = False
    for ch in inner:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(depth - 1, 0)
        elif ch == "," and depth == 0:
            count += 1
            saw_comma = True
    if not saw_comma:
        return None
    return count


def _validate_tensor_shape(expression: str, metadata: TensorMetadata) -> None:
    flat_count = _count_top_level_items(expression)
    if flat_count is None:
        return
    expected = metadata.dim ** metadata.order
    if flat_count != expected:
        raise DSLParseError(
            f"Tensor {metadata.name} expects {expected} values for dim {metadata.dim}"
        )


def _parse_render(line: str) -> RenderRequest:
    """Parse a render declaration."""
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
        if token == "time" and idx + 1 < len(tokens):
            options["time"] = tokens[idx + 1]
            idx += 2
            continue
        options[f"arg_{idx}"] = token
        idx += 1
    return options
