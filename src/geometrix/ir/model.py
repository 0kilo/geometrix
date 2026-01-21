"""Symbolic IR models for DSL parsing."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DefinitionKind(str, Enum):
    SCALAR = "scalar"
    VECTOR = "vector"
    TENSOR = "tensor"


@dataclass(frozen=True)
class Definition:
    name: str
    args: tuple[str, ...]
    expression: str
    kind: DefinitionKind = DefinitionKind.SCALAR


@dataclass(frozen=True)
class RenderRequest:
    kind: str
    target: str
    options: dict[str, Any] = field(default_factory=dict)


@dataclass
class SymbolicIR:
    coords: list[str] = field(default_factory=list)
    params: dict[str, float] = field(default_factory=dict)
    definitions: dict[str, Definition] = field(default_factory=dict)
    render_requests: list[RenderRequest] = field(default_factory=list)
