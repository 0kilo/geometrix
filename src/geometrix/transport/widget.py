"""Minimal ipywidgets transport stub."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from importlib import resources
from typing import TYPE_CHECKING, Any

import numpy as np

from geometrix.scene.spec import SceneSpec
from geometrix.transport.buffers import build_payload

if TYPE_CHECKING:
    from ipywidgets import DOMWidget as _RuntimeDOMWidget
    from traitlets import Dict as _RuntimeDict
    from traitlets import Unicode as _RuntimeUnicode

    _TRAITLETS_AVAILABLE = True
else:
    try:
        from ipywidgets import DOMWidget as _RuntimeDOMWidget
        from traitlets import Dict as _RuntimeDict
        from traitlets import Unicode as _RuntimeUnicode

        _TRAITLETS_AVAILABLE = True
    except ImportError:  # pragma: no cover - optional in minimal envs
        _TRAITLETS_AVAILABLE = False

        class _RuntimeDOMWidget:
            def __init__(self, *_args: Any, **_kwargs: Any) -> None:
                pass

        class _RuntimeDict:
            def __init__(self, *_args: Any, **_kwargs: Any) -> None:
                pass

            def tag(self, **_kwargs: Any) -> Any:
                return self

        class _RuntimeUnicode:
            def __init__(self, *_args: Any, **_kwargs: Any) -> None:
                pass

            def tag(self, **_kwargs: Any) -> Any:
                return self


DOMWidget: Any = _RuntimeDOMWidget
Dict: Any = _RuntimeDict
Unicode: Any = _RuntimeUnicode


@dataclass
class GeomViewer:
    """Lightweight wrapper around a widget model."""

    scene: SceneSpec
    buffers: dict[str, memoryview]


class GeomWidget(DOMWidget):
    """DOMWidget placeholder for future frontend integration."""

    if _TRAITLETS_AVAILABLE:
        _model_name = Unicode("GeomWidgetModel").tag(sync=True)
        _view_name = Unicode("GeomWidgetView").tag(sync=True)
        _model_module = Unicode("geometrix-widget").tag(sync=True)
        _view_module = Unicode("geometrix-widget").tag(sync=True)
        _model_module_version = Unicode("0.1.0").tag(sync=True)
        _view_module_version = Unicode("0.1.0").tag(sync=True)
        scene_spec = Dict({}).tag(sync=True)
        buffers = Dict({}).tag(sync=True)
        height = Unicode("420").tag(sync=True)

    def __init__(
        self, scene: SceneSpec, buffers: dict[str, np.ndarray], height: int = 420
    ) -> None:
        super().__init__()
        if _TRAITLETS_AVAILABLE:
            self.scene_spec = _scene_to_dict(scene)
            self.buffers = _encode_buffers(buffers)
            self.height = str(height)
            _ensure_js_loaded()
        self._buffer_payload = buffers


def build_viewer(scene: SceneSpec, arrays: dict[str, Any]) -> GeomViewer:
    payload = build_payload(arrays)
    return GeomViewer(scene=scene, buffers=payload.buffers)


def build_widget(
    scene: SceneSpec, arrays: dict[str, np.ndarray], height: int = 420
) -> GeomWidget:
    return GeomWidget(scene, arrays, height=height)


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
            key: {"dtype": spec.dtype, "shape": spec.shape}
            for key, spec in scene.buffers.items()
        },
        "camera": scene.camera,
        "lights": scene.lights,
        "axes": scene.axes,
        "grid": scene.grid,
    }


def _encode_buffers(arrays: dict[str, np.ndarray]) -> dict[str, dict[str, Any]]:
    encoded: dict[str, dict[str, Any]] = {}
    for key, array in arrays.items():
        data = base64.b64encode(array.tobytes()).decode("ascii")
        encoded[key] = {
            "dtype": str(array.dtype),
            "shape": list(array.shape),
            "data": data,
        }
    return encoded


def _ensure_js_loaded() -> None:
    try:
        from IPython.display import Javascript, display
    except ImportError:
        return

    try:
        static_dir = resources.files("geometrix") / "static"
    except Exception:
        return
    candidates = [
        static_dir / "index.js",
    ]
    js_path = next((path for path in candidates if path.is_file()), None)
    if not js_path:
        return
    try:
        js_text = js_path.read_text(encoding="utf-8")
    except Exception:
        return
    shim = """
if (window.GeometrixWidget && typeof define === "function" && define.amd) {
  define("geometrix-widget", [], function () {
    return window.GeometrixWidget;
  });
}
"""
    display(Javascript(f"{js_text}\n{shim}"))
