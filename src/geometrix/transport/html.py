"""HTML fallback renderer for notebooks."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from importlib import resources
from typing import Any

import numpy as np

from geometrix.animation import Animation
from geometrix.scene.spec import SceneSpec

DEFAULT_TEMPLATE = """
<div id="geometrix-container" style="width:100%;height:__HEIGHT__px;"></div>
<style>__CSS__</style>
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.module.js"
  }
}
</script>
<script type="module">
__SCRIPT__
</script>
"""


@dataclass(frozen=True)
class HtmlBundle:
    html: str


def render_html(
    scene: SceneSpec,
    arrays: dict[str, np.ndarray],
    height: int = 420,
    animation: Animation | None = None,
) -> HtmlBundle:
    payload = _build_payload(scene, arrays, animation)
    html = _build_html(payload, height)
    return HtmlBundle(html=html)


def _build_payload(
    scene: SceneSpec, arrays: dict[str, np.ndarray], animation: Animation | None
) -> dict[str, Any]:
    buffers: dict[str, Any] = {}
    for key, array in arrays.items():
        data = base64.b64encode(array.tobytes()).decode("ascii")
        buffers[key] = {
            "dtype": str(array.dtype),
            "shape": list(array.shape),
            "data": data,
        }
    payload = {
        "scene": _scene_to_dict(scene),
        "buffers": buffers,
    }
    if animation:
        payload["scene"]["animation"] = animation.to_spec()
        payload["frames"] = _encode_frames(animation)
    return payload


def _build_html(payload: dict[str, Any], height: int) -> str:
    payload_json = json.dumps(payload)
    css = _load_css()
    template = _load_template()
    script = _load_script()
    script = script.replace("__PAYLOAD__", payload_json)
    html = template.replace("__HEIGHT__", str(height))
    html = html.replace("__CSS__", css)
    html = html.replace("__SCRIPT__", script)
    return html


def _load_css() -> str:
    try:
        css_path = resources.files("geometrix.transport") / "html_ui.css"
    except Exception:
        return ""
    try:
        return css_path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _load_template() -> str:
    try:
        template_path = (
            resources.files("geometrix.transport") / "templates" / "index.html"
        )
    except Exception:
        return DEFAULT_TEMPLATE
    try:
        return template_path.read_text(encoding="utf-8")
    except Exception:
        return DEFAULT_TEMPLATE


def _load_script() -> str:
    try:
        scripts_dir = (
            resources.files("geometrix.transport") / "templates" / "scripts"
        )
    except Exception:
        return ""
    try:
        parts = []
        for path in sorted(scripts_dir.glob("*.js")):
            parts.append(path.read_text(encoding="utf-8"))
        return "\n".join(parts)
    except Exception:
        return ""


def _scene_to_dict(scene: SceneSpec) -> dict[str, Any]:
    return {
        "version": scene.version,
        "objects": [
            {
                "type": obj.type,
                "name": obj.name,
                "buffers": obj.buffers,
                "style": obj.style,
                "metadata": obj.metadata,
            }
            for obj in scene.objects
        ],
        "buffers": {
            key: {"dtype": spec.dtype, "shape": list(spec.shape)}
            for key, spec in scene.buffers.items()
        },
        "camera": scene.camera,
        "lights": scene.lights,
        "axes": scene.axes,
        "grid": scene.grid,
        "controls": scene.controls,
        "legend": scene.legend,
        "gizmo": scene.gizmo,
        "animation": scene.animation,
    }


def _encode_frames(animation: Animation) -> list[dict[str, Any]]:
    frames: list[dict[str, Any]] = []
    for frame in animation.frames:
        payload: dict[str, Any] = {}
        for key, array in frame.arrays.items():
            data = base64.b64encode(array.tobytes()).decode("ascii")
            payload[key] = {
                "dtype": str(array.dtype),
                "shape": list(array.shape),
                "data": data,
            }
        frames.append(payload)
    return frames
