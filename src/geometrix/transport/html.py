"""HTML fallback renderer for notebooks."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any

import numpy as np

from geometrix.scene.spec import SceneSpec


@dataclass(frozen=True)
class HtmlBundle:
    html: str


def render_html(
    scene: SceneSpec, arrays: dict[str, np.ndarray], height: int = 420
) -> HtmlBundle:
    payload = _build_payload(scene, arrays)
    html = _build_html(payload, height)
    return HtmlBundle(html=html)


def _build_payload(scene: SceneSpec, arrays: dict[str, np.ndarray]) -> dict[str, Any]:
    buffers: dict[str, Any] = {}
    for key, array in arrays.items():
        data = base64.b64encode(array.tobytes()).decode("ascii")
        buffers[key] = {
            "dtype": str(array.dtype),
            "shape": list(array.shape),
            "data": data,
        }
    return {
        "scene": _scene_to_dict(scene),
        "buffers": buffers,
    }


def _build_html(payload: dict[str, Any], height: int) -> str:
    payload_json = json.dumps(payload)
    return f"""
<div id="geometrix-container" style="width:100%;height:{height}px;"></div>
<script type="module">
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.module.js";
import {{ OrbitControls }} from "https://cdn.jsdelivr.net/npm/three@0.163.0/examples/jsm/controls/OrbitControls.js";

const payload = {payload_json};

const dtypeToCtor = {{
  float32: Float32Array,
  float64: Float64Array,
  int32: Int32Array,
  uint32: Uint32Array,
  int16: Int16Array,
  uint16: Uint16Array,
  int8: Int8Array,
  uint8: Uint8Array,
}};

function decode(base64) {{
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {{
    bytes[i] = binary.charCodeAt(i);
  }}
  return bytes.buffer;
}}

function buildColors(values) {{
  let min = values[0] ?? 0;
  let max = values[0] ?? 1;
  for (let i = 1; i < values.length; i += 1) {{
    min = Math.min(min, values[i]);
    max = Math.max(max, values[i]);
  }}
  const range = max - min || 1;
  const colors = new Float32Array(values.length * 3);
  for (let i = 0; i < values.length; i += 1) {{
    const t = (values[i] - min) / range;
    colors[i * 3] = 0.1 + 0.85 * t;
    colors[i * 3 + 1] = 0.2 + 0.7 * (1 - Math.abs(0.5 - t) * 2);
    colors[i * 3 + 2] = 0.9 - 0.7 * t;
  }}
  return colors;
}}

const buffers = {{}};
for (const [key, spec] of Object.entries(payload.buffers)) {{
  const ctor = dtypeToCtor[spec.dtype];
  const raw = decode(spec.data);
  buffers[key] = new ctor(raw);
}}

const scene = new THREE.Scene();
scene.add(new THREE.AmbientLight(0xffffff, 0.7));
const light = new THREE.DirectionalLight(0xffffff, 0.8);
light.position.set(5, 5, 5);
scene.add(light);

for (const obj of payload.scene.objects) {{
  if (obj.type === "points") {{
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.BufferAttribute(buffers[obj.buffers.positions], 3)
    );
    const material = new THREE.PointsMaterial({{ size: 0.05, color: 0xffffff }});
    scene.add(new THREE.Points(geometry, material));
  }} else if (obj.type === "line") {{
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.BufferAttribute(buffers[obj.buffers.positions], 3)
    );
    scene.add(
      new THREE.Line(geometry, new THREE.LineBasicMaterial({{ color: 0xffffff }}))
    );
  }} else if (obj.type === "surface_grid") {{
    const geometry = new THREE.BufferGeometry();
    const positions = buffers[obj.buffers.positions];
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const grid = obj.metadata?.grid;
    if (!grid) throw new Error("Missing grid metadata");
    const nu = grid.Nu;
    const nv = grid.Nv;
    const indices = [];
    for (let i = 0; i < nu - 1; i += 1) {{
      for (let j = 0; j < nv - 1; j += 1) {{
        const a = i * nv + j;
        const b = a + 1;
        const c = a + nv;
        const d = c + 1;
        indices.push(a, c, b, b, c, d);
      }}
    }}
    geometry.setIndex(indices);
    geometry.computeVertexNormals();
    const valuesKey = obj.buffers.values;
    let material = new THREE.MeshStandardMaterial({{
      color: 0xffffff,
      side: THREE.DoubleSide
    }});
    if (valuesKey) {{
      const colors = buildColors(buffers[valuesKey]);
      geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
      material = new THREE.MeshStandardMaterial({{
        vertexColors: true,
        side: THREE.DoubleSide
      }});
    }}
    scene.add(new THREE.Mesh(geometry, material));
  }}
}}

const container = document.getElementById("geometrix-container");
const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.setPixelRatio(window.devicePixelRatio || 1);
renderer.setClearColor(0x0b0f1a);
container.appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera(
  45,
  container.clientWidth / container.clientHeight,
  0.01,
  1000
);
camera.position.set(3, 3, 3);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

function animate() {{
  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}}
animate();
</script>
"""


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
    }
