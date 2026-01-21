"""Build JS assets and copy them into the Python package."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS_DIR = ROOT / "js"
DIST_DIR = JS_DIR / "dist"
STATIC_DIR = ROOT / "src" / "geometrix" / "static"


def run_build() -> None:
    subprocess.run(["npm", "--prefix", str(JS_DIR), "install"], check=True)
    subprocess.run(["npm", "--prefix", str(JS_DIR), "run", "build"], check=True)


def copy_assets() -> None:
    if STATIC_DIR.exists():
        shutil.rmtree(STATIC_DIR)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    if not DIST_DIR.exists():
        raise FileNotFoundError("js/dist not found; run build first")
    shutil.copytree(DIST_DIR, STATIC_DIR, dirs_exist_ok=True)


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
    copy_assets()


if __name__ == "__main__":
    main()
