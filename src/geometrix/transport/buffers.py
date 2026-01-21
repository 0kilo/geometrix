"""Buffer registry helpers for widget transport."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from geometrix.scene.spec import BufferSpec


@dataclass(frozen=True)
class BufferPayload:
    specs: dict[str, BufferSpec]
    buffers: dict[str, memoryview]


def build_payload(arrays: dict[str, np.ndarray]) -> BufferPayload:
    specs: dict[str, BufferSpec] = {}
    buffers: dict[str, memoryview] = {}
    for key, array in arrays.items():
        specs[key] = BufferSpec(dtype=str(array.dtype), shape=tuple(array.shape))
        buffers[key] = memoryview(array.data)
    return BufferPayload(specs=specs, buffers=buffers)
