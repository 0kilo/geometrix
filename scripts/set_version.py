"""Sync version across pyproject.toml, js/package.json, and widget.py."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"


def update_pyproject(version: str) -> None:
    text = PYPROJECT.read_text(encoding="utf-8")
    lines = text.splitlines()
    out = []
    in_project = False
    for line in lines:
        if line.strip() == "[project]":
            in_project = True
            out.append(line)
            continue
        if in_project and line.startswith("[") and line.strip() != "[project]":
            in_project = False
        if in_project and line.strip().startswith("version ="):
            out.append(f'version = "{version}"')
            continue
        out.append(line)
    PYPROJECT.write_text("\n".join(out) + "\n", encoding="utf-8")





def main() -> None:
    parser = argparse.ArgumentParser(description="Sync version across the repo.")
    parser.add_argument("version", help="Version to set, e.g. 0.1.2")
    args = parser.parse_args()

    update_pyproject(args.version)
    print(f"Set version to {args.version}")


if __name__ == "__main__":
    main()
