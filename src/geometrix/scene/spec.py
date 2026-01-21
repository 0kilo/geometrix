"""SceneSpec models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class BufferSpec:
    dtype: str
    shape: tuple[int, ...]


@dataclass(frozen=True)
class ObjectSpec:
    type: str
    buffers: dict[str, str]
    name: str | None = None
    style: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SceneSpec:
    version: str
    objects: list[ObjectSpec]
    buffers: dict[str, BufferSpec]
    camera: dict[str, Any] = field(default_factory=dict)
    lights: list[dict[str, Any]] = field(default_factory=list)
    axes: dict[str, Any] = field(default_factory=dict)
    grid: dict[str, Any] = field(default_factory=dict)
