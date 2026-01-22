"""Animation scaffolding."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

import numpy as np

from geometrix.scene.spec import SceneSpec


@dataclass(frozen=True)
class Frame:
    t: float
    arrays: dict[str, np.ndarray]


@dataclass(frozen=True)
class Animation:
    frames: list[Frame]
    fps: int = 30
    loop: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_spec(self) -> dict[str, Any]:
        return {
            "fps": self.fps,
            "loop": self.loop,
            "frame_count": len(self.frames),
            "metadata": self.metadata,
        }


def attach_animation(scene: SceneSpec, animation: Animation) -> SceneSpec:
    return replace(scene, animation=animation.to_spec())
