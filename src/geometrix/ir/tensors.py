"""Tensor metadata helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass

_TENSOR_BASE_RE = re.compile(r"^[A-Za-z]+")
_TENSOR_INDEX_RE = re.compile(r"([_^])(\{[^}]+\}|\w)")


@dataclass(frozen=True)
class TensorIndex:
    symbol: str
    variance: str


@dataclass(frozen=True)
class TensorMetadata:
    name: str
    indices: tuple[TensorIndex, ...]
    order: int
    dim: int


def parse_tensor_name(name: str, dim: int) -> TensorMetadata:
    raw = name.strip()
    base_match = _TENSOR_BASE_RE.match(raw)
    if not base_match:
        raise ValueError(f"Invalid tensor name: {name}")
    base = base_match.group(0)
    indices: list[TensorIndex] = []
    for variance, token in _TENSOR_INDEX_RE.findall(raw):
        text = token[1:-1] if token.startswith("{") else token
        for symbol in text:
            if not symbol.isalpha():
                continue
            indices.append(
                TensorIndex(symbol=symbol, variance="up" if variance == "^" else "down")
            )
    if not indices:
        raise ValueError(f"Tensor indices missing in {name}")
    return TensorMetadata(
        name=base, indices=tuple(indices), order=len(indices), dim=dim
    )
