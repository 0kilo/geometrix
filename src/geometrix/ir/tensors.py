"""Tensor metadata helpers (placeholder for v1)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TensorMetadata:
    name: str
    order: int
    dim: int
