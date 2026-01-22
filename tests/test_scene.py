import numpy as np

from geometrix.animation import Animation, Frame, attach_animation
from geometrix.scene.build import build_buffers, build_surface_scene
from geometrix.transport.html import _scene_to_dict, render_html


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


def test_transport_payload_and_render():
    arrays = {"positions": np.zeros((2, 3), dtype=np.float32)}
    scene = build_surface_scene(arrays["positions"], (2, 1))
    bundle = render_html(scene, arrays, height=360)
    assert "geometrix-container" in bundle.html
    scene_dict = _scene_to_dict(scene)
    assert scene_dict["buffers"]["positions"]["shape"] == [2, 3]


def test_attach_animation():
    positions = np.zeros((2, 3), dtype=np.float32)
    scene = build_surface_scene(positions, (1, 2))
    frame = Frame(t=0.0, arrays={"positions": positions})
    anim = Animation(frames=[frame], fps=24)
    updated = attach_animation(scene, anim)
    assert updated.animation["fps"] == 24
    assert updated.animation["frame_count"] == 1
