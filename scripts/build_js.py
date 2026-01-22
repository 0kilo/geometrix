"""Build JS assets and copy them into the Python package."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS_DIR = ROOT / "js"
DIST_DIR = JS_DIR / "dist"


def run_build() -> None:
    subprocess.run(["npm", "--prefix", str(JS_DIR), "install"], check=True)
    subprocess.run(["npm", "--prefix", str(JS_DIR), "run", "build"], check=True)
    _ensure_index_js()


def _ensure_index_js() -> None:
    iife_path = DIST_DIR / "index.iife.js"
    index_path = DIST_DIR / "index.js"
    if iife_path.exists():
        index_path.write_text(iife_path.read_text(encoding="utf-8"), encoding="utf-8")


def _clear_legacy_assets() -> None:
    static_dir = ROOT / "src" / "geometrix" / "static"
    if static_dir.exists():
        shutil.rmtree(static_dir)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build JS assets and copy to Python package."
    )
    parser.add_argument(
        "--skip-build", action="store_true", help="Skip npm build step."
    )
    args = parser.parse_args()

    if not args.skip_build:
        run_build()
    _clear_legacy_assets()


if __name__ == "__main__":
    main()
