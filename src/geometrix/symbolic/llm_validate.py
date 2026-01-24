"""Validation helpers for LLM JSON LaTeX responses."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterable, Literal

from pydantic import BaseModel, Field, ValidationError

from geometrix.parse.latex_parser import LatexParseError, parse_latex_expr

GraphType = Literal["curve", "surface", "implicit", "none"]


class _ResponseBase(BaseModel):
    response_type: Literal["minimal", "full"]
    input: str
    solution: str
    graph_type: GraphType
    graph: str
    parameters: str
    domains: str
    not_graphable: str


class MinimalResponse(_ResponseBase):
    response_type: Literal["minimal"]


class FullResponse(_ResponseBase):
    response_type: Literal["full"]
    steps: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class ValidationResult:
    """Validation output for LLM responses."""

    data: MinimalResponse | FullResponse
    warnings: tuple[str, ...]


def validate_llm_response(
    text: str,
    *,
    wants_graph: bool | None = None,
    require_domains: bool = False,
    strict_latex: bool = False,
) -> ValidationResult:
    """Validate JSON, schema, graphability, and optional LaTeX parsing."""

    data = _parse_json(text)
    parsed = _validate_schema(data)
    warnings: list[str] = []

    warnings.extend(
        _validate_graphability(parsed, wants_graph=wants_graph, require_domains=require_domains)
    )
    warnings.extend(_validate_latex(parsed, strict=strict_latex))

    if strict_latex and warnings:
        raise ValueError("LaTeX validation failed: " + "; ".join(warnings))

    return ValidationResult(data=parsed, warnings=tuple(warnings))


def _parse_json(text: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        extracted = _extract_json_object(text)
        if extracted is not None:
            return extracted
        raise ValueError("LLM response is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("LLM response JSON must be an object")
    return payload


def _extract_json_object(text: str) -> dict[str, Any] | None:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    snippet = text[start : end + 1]
    try:
        payload = json.loads(snippet)
    except json.JSONDecodeError:
        try:
            payload = json.loads(_escape_backslashes(snippet))
        except json.JSONDecodeError:
            return None
    if isinstance(payload, dict):
        return payload
    return None


def _escape_backslashes(text: str) -> str:
    return text.replace("\\", "\\\\")


def _validate_schema(data: dict[str, Any]) -> MinimalResponse | FullResponse:
    response_type = data.get("response_type")
    model = FullResponse if response_type == "full" else MinimalResponse
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        raise ValueError("LLM response does not match schema") from exc


def _validate_graphability(
    data: MinimalResponse | FullResponse,
    *,
    wants_graph: bool | None,
    require_domains: bool,
) -> list[str]:
    warnings: list[str] = []
    if wants_graph and data.graph_type == "none":
        raise ValueError("Graph requested but graph_type is none")
    if data.graph_type != "none" and not data.graph:
        raise ValueError("graph_type requires a non-empty graph field")
    if require_domains and data.graph_type != "none" and not data.domains:
        warnings.append("graph_type provided without domains")
    return warnings


def _validate_latex(
    data: MinimalResponse | FullResponse,
    *,
    strict: bool,
) -> list[str]:
    warnings: list[str] = []
    fields = _iter_latex_fields(data)
    for name, value in fields:
        if not value:
            continue
        if "\\text" in value and not strict:
            continue
        try:
            parse_latex_expr(value, allowed_symbols=_infer_symbols(value))
        except LatexParseError as exc:
            warnings.append(f"{name} failed LaTeX parse: {exc}")
    return warnings


def _iter_latex_fields(
    data: MinimalResponse | FullResponse,
) -> Iterable[tuple[str, str]]:
    base_fields = [
        ("input", data.input),
        ("solution", data.solution),
        ("graph", data.graph),
        ("parameters", data.parameters),
        ("domains", data.domains),
        ("not_graphable", data.not_graphable),
    ]
    if isinstance(data, FullResponse):
        for idx, step in enumerate(data.steps):
            base_fields.append((f"steps[{idx}]", step))
    return base_fields


def _infer_symbols(expr: str) -> list[str]:
    symbols: list[str] = []
    token = ""
    for char in expr:
        if char.isalpha():
            token += char
        else:
            if token:
                symbols.append(token)
                token = ""
    if token:
        symbols.append(token)
    return sorted(set(symbols))
