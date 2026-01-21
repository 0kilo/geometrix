import * as THREE from "three";

import { getBuffer } from "../buffers";
import type { BufferMap, ObjectSpec, SceneSpec } from "../types";
import { buildColors } from "../utils/colormap";

function buildGridIndices(nu: number, nv: number): Uint32Array {
  const indices = new Uint32Array((nu - 1) * (nv - 1) * 6);
  let idx = 0;
  for (let i = 0; i < nu - 1; i += 1) {
    for (let j = 0; j < nv - 1; j += 1) {
      const a = i * nv + j;
      const b = a + 1;
      const c = a + nv;
      const d = c + 1;
      indices[idx++] = a;
      indices[idx++] = c;
      indices[idx++] = b;
      indices[idx++] = b;
      indices[idx++] = c;
      indices[idx++] = d;
    }
  }
  return indices;
}

function getGridShape(obj: ObjectSpec): [number, number] {
  const meta = obj.metadata ?? {};
  const grid = meta.grid as { Nu?: number; Nv?: number } | undefined;
  if (!grid?.Nu || !grid?.Nv) {
    throw new Error("surface_grid metadata missing grid shape");
  }
  return [grid.Nu, grid.Nv];
}

export function buildSurfaceGrid(
  obj: ObjectSpec,
  scene: SceneSpec,
  buffers: BufferMap,
): THREE.Mesh {
  const positionsKey = obj.buffers.positions;
  if (!positionsKey) {
    throw new Error("Surface object missing positions buffer");
  }
  const positionSpec = scene.buffers[positionsKey];
  const positionData = getBuffer(positionsKey, positionSpec, buffers) as Float32Array;

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positionData, 3));

  const [nu, nv] = getGridShape(obj);
  geometry.setIndex(new THREE.BufferAttribute(buildGridIndices(nu, nv), 1));
  geometry.computeVertexNormals();

  const valuesKey = obj.buffers.values;
  if (valuesKey) {
    const valuesSpec = scene.buffers[valuesKey];
    const values = getBuffer(valuesKey, valuesSpec, buffers) as Float32Array;
    const colors = buildColors(values, obj.style);
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  }

  const material = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    side: THREE.DoubleSide,
    vertexColors: Boolean(valuesKey),
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.userData = { spec: obj };
  return mesh;
}
