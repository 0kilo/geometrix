"""Package a zip bundle for Colab testing."""

from __future__ import annotations

import argparse
import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _add_path(zip_handle: zipfile.ZipFile, path: Path, base: Path) -> None:
    if path.is_dir():
        for child in sorted(path.rglob("*")):
            if child.is_file():
                zip_handle.write(child, child.relative_to(base))
        return
    zip_handle.write(path, path.relative_to(base))


def create_zip(output: Path) -> None:
    targets = [
        ROOT / "pyproject.toml",
        ROOT / "README.md",
        ROOT / "src" / "geometrix",
    ]

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zip_handle:
        for path in targets:
            if path.exists():
                _add_path(zip_handle, path, ROOT)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Colab test bundle.")
    parser.add_argument(
        "--output",
        default=ROOT / "dist" / "geometrix_colab.zip",
        type=Path,
    )
    args = parser.parse_args()
    create_zip(args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    os.chdir(ROOT)
    main()
