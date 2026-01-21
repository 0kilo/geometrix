import numpy as np

from geometrix.scene.build import build_buffers, build_surface_scene
from geometrix.transport.buffers import build_payload
from geometrix.transport.widget import _scene_to_dict, build_viewer, build_widget


def test_build_buffers_creates_specs():
    arrays = {"positions": np.zeros((2, 3), dtype=np.float32)}
    registry = build_buffers(arrays)
    assert registry.specs["positions"].shape == (2, 3)
    assert registry.specs["positions"].dtype == "float32"


def test_scene_spec_surface():
    positions = np.zeros((6, 3), dtype=np.float32)
    scene = build_surface_scene(positions, (2, 3))
    assert scene.version == "1.0"
    assert scene.objects[0].type == "surface_grid"
    assert scene.buffers["positions"].shape == (6, 3)


def test_transport_payload_and_viewer():
    arrays = {"positions": np.zeros((2, 3), dtype=np.float32)}
    payload = build_payload(arrays)
    assert "positions" in payload.buffers

    scene = build_surface_scene(arrays["positions"], (2, 1))
    viewer = build_viewer(scene, arrays)
    assert viewer.scene.version == "1.0"
    scene_dict = _scene_to_dict(scene)
    assert scene_dict["buffers"]["positions"]["shape"] == (2, 3)


def test_widget_payload_encoding():
    arrays = {"positions": np.zeros((2, 3), dtype=np.float32)}
    scene = build_surface_scene(arrays["positions"], (2, 1))
    widget = build_widget(scene, arrays, height=360)
    assert widget.height == "360"
    assert "positions" in widget.buffers
