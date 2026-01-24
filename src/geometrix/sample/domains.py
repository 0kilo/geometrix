"""Domain helpers for sampling."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Domain:
    name: str
    start: float
    stop: float

    def linspace(self, count: int) -> np.ndarray:
        if count <= 1:
            raise ValueError("count must be > 1")
        return np.linspace(self.start, self.stop, count, dtype=np.float64)


def meshgrid(domains: list[Domain], counts: list[int]) -> list[np.ndarray]:
    if len(domains) != len(counts):
        raise ValueError("domains and counts must match")
    axes = [
        domain.linspace(count) for domain, count in zip(domains, counts, strict=True)
    ]
    grids = np.meshgrid(*axes, indexing="ij")
    return [np.asarray(grid) for grid in grids]


def validate_domains(domains: list[Domain]) -> None:
    """Validate domain ordering and numeric bounds."""

    for domain in domains:
        if not np.isfinite(domain.start) or not np.isfinite(domain.stop):
            raise ValueError(f"Domain {domain.name} bounds must be finite")
        if domain.start >= domain.stop:
            raise ValueError(f"Domain {domain.name} start must be < stop")
